"""Evaluacion automatica del agente con las preguntas de eval/preguntas.yaml (20 originales + las de colonia,
seguimiento, ingreso/edades y macro agregadas el 2026-11-23).

    uv run python eval/evaluar.py              # corre el agente (Ollama) y califica; reanuda si se corto
    uv run python eval/evaluar.py --rehacer    # borra lo parcial y empieza de cero
    uv run python eval/evaluar.py --solo-checks  # vuelve a calificar las respuestas guardadas, sin LLM

Salidas: reports/evaluacion.md, reports/evaluacion.json y reports/evaluacion_parcial.jsonl (una linea por pregunta).
Checks (contrato): AGEB y colonias del top existen en agebs_features; cada renglon de zona trae la colonia de SU AGEB
y cifras de ESA zona; ninguna colonia nombrada sin origen en las herramientas; fuentes completas; latencia; sin tokens;
y los de lo nuevo (colonia_respetada, seguimiento_mantiene_giro, ingreso_y_edad, macro_breve, formato).
Aprobado: >= 90 % de las preguntas, la trampa, las tres fuera de tema y todas las de colonia y de seguimiento.
Todas llevan el check `sin_funciones_internas` (ninguna respuesta nombra perfil_giro, recomendar_zonas... ni escribe f(x=...));
las de tipo `fuera_de_tema` (nombre, saludo, tema ajeno) llevan `fuera_de_tema`: el texto fijo que dice que solo contesta sobre
negocios en la ZMVM, sin AGEB ni funciones internas. Esas no usan el LLM.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import yaml  # noqa: E402

from app import fuera_de_tema as fuera  # noqa: E402
from app import herramientas as H  # noqa: E402
from app import historial  # noqa: E402
from app import lectura as lectura_mod  # noqa: E402
from app import motor  # noqa: E402

REPORTS = RAIZ / "reports"
PARCIAL = REPORTS / "evaluacion_parcial.jsonl"
LAT_MAX_S = 165          # una respuesta que tarda mas de esto falla el check de latencia (meta: maxima <= 165 s)
LAT_OBJETIVO_MED_S = 120  # meta de la mediana (se reporta; la maxima debe ser <= 165 s)
MIN_CIFRAS_OK = 0.95     # fraccion minima de cifras citadas que deben salir de las herramientas
MAX_CIFRAS_MAL = 0       # ninguna cifra sin origen (antes se toleraba 1; un entero de 2 digitos inventado coincide por azar)
MIN_APROBADO = 0.90      # fraccion de preguntas que deben pasar
RADIO_COLONIA_KM = 2.0   # AGEB citada a <= esto del centroide de la colonia pedida
MIN_ZONAS_INGRESO_EDAD = 0.6  # fraccion de las zonas citadas que traen ingreso en pesos y % de la edad clave
MACRO_BREVE_MAX_CHARS = 600   # el parrafo de macro no pasa de esto

AGEB_RE, FECHA_RE, NUM_RE = lectura_mod.AGEB_RE, lectura_mod.FECHA_RE, lectura_mod.NUM_RE  # las comparte con app/lectura.py
FUENTES_CLAVE = ["inegi", "denue", "censo", "enigh", "conapo", "banxico", "banco de mexico", "carpetas/", "modelo de aperturas"]
RELATIVO_RE = re.compile(r"relativ|no compara|dentro (?:de cada|de este|del|de su) giro|percentil", re.I)
VIABILIDAD_RE = re.compile(r"viabilidad\W{0,12}\d|giros que conviene considerar", re.I)  # una cifra de viabilidad o una lista inventada
BAJA_RE = re.compile(r"\bbaj[ao]s?\b", re.I)
NO_ENCONTRADO_RE = re.compile(r"no (?:se )?(?:encontr|existe|aparece|hall)", re.I)
A_CAMBIO_RE = re.compile(r"a cambio|sin filtro|en su lugar|toda la zmvm|en la zmvm|en lugar de|m[aá]s parecida", re.I)
PCT_MAL_RE = re.compile(r"(?:prob\.?\s+de\s+apertura|prob\.?\s+de\s+seguir\s+abierto|captura|viabilidad)\s*%\s*\d", re.I)
FIJO_RE = re.compile(r"tipo de cambio fijo", re.I)
NONE_RE = re.compile(r"\bNone\b|\bnan\b|\bNaN\b")   # un dato vacio que se imprimio tal cual («25 a 59 años: None %»)
MECANISMO_RE = re.compile(r"\bcostos?\b|insumos?|cr[eé]dito|financi|margen|\bprecios?\b", re.I)   # «cómo influye»: el mecanismo
PIDE_COMO_RE = re.compile(r"c[oó]mo\s+(?:me\s+)?(?:influy|afect|impact|cambi|repercut)|efecto|impacto", re.I)
GENERICOS_COLONIA = {"centro", "ciudad", "industrial", "residencial", "popular", "central", "nacional", "moderna", "jardines",
                     "lomas", "bosques", "america", "progreso", "libertad", "esperanza", "constitucion", "revolucion",
                     "independencia", "reforma", "hidalgo", "morelos", "juarez", "zaragoza"}
PALABRAS_VACIAS = {"el", "la", "los", "las", "de", "del", "y", "en", "colonia", "colonias", "zona", "zonas", "unidad", "habitacional",
                   "barrio", "barrios", "pueblo", "ampliacion", "fraccionamiento", "norte", "sur", "oriente", "poniente"}
SOLO_NEGOCIOS_RE = re.compile(r"solo contest\w+.{0,200}(?:Zona Metropolitana del Valle de M[eé]xico|ZMVM)", re.I | re.S)
FUERA_RE = re.compile(r"fuera (?:de|del)|no (?:cubre|esta|está|incluye|tengo datos)|solo (?:cubre|abarca|trabaja)|únicamente|unicamente|alcance",
                      re.I)


# ---------------------------------------------------------------- utilidades
def memoria() -> dict:
    """Swap usado (MB) y % de memoria libre del sistema (macOS)."""
    out = {}
    try:
        s = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True, timeout=5).stdout
        m = re.search(r"used = ([\d.]+)M", s)
        out["swap_mb"] = float(m.group(1)) if m else None
        p = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=10).stdout
        m = re.search(r"free percentage: (\d+)%", p)
        out["mem_libre_pct"] = int(m.group(1)) if m else None
    except Exception:
        pass
    return out


def tokens_env() -> list[str]:
    """Valores de .env (nunca se imprimen; solo se buscan). Es el mismo filtro que usa el registro de preguntas del tablero."""
    return historial.tokens_env()


numeros_de, cifras_citadas, coincide = lectura_mod.numeros_de, lectura_mod.cifras_citadas, lectura_mod.coincide


# ---------------------------------------------------------------- checks
def _giro_mencionado(clave: str, low: str) -> bool:
    """El giro aparece en la respuesta (normalizada) por su clave o por alguno de sus sinonimos."""
    from app import motor

    nombres = [clave.replace("_", " ")] + list(motor.giros().get(clave, {}).get("nombres", []))
    return any(H._singular(H.norm(n)) in H._singular(low) for n in nombres if n)


def bloques_de_zona(texto: str, agebs_validas: set) -> dict:
    """{ageb: texto del renglon de esa zona}. El renglon empieza en la linea que trae la clave AGEB y sigue hasta la
    siguiente linea con otra AGEB o con un encabezado en negritas («**Riesgos:**»)."""
    lineas = texto.splitlines()
    bloques: dict[str, list[str]] = {}
    actual = None
    for ln in lineas:
        if ln.lstrip().startswith(("**Lectura", ">")):  # la lectura del modelo y el aviso no son renglones de zona
            actual = None
            continue
        ids = [a for a in AGEB_RE.findall(ln)]
        if ids:
            actual = ids[0]
            bloques.setdefault(actual, []).append(ln)
        elif actual and not re.match(r"^\s*(?:\*\*|#|>)", ln) and ln.strip():
            bloques[actual].append(ln)
        else:
            actual = None
    return {a: "\n".join(v) for a, v in bloques.items() if a in agebs_validas}


ARTICULOS = {"de", "del", "la", "las", "los", "el", "y", "en"}


def zona_mencionada(colonia: str, frase_norm: str) -> bool:
    """La frase (normalizada) nombra la colonia: nombre completo, o todas sus palabras con contenido (en singular o plural:
    «Fuente de Aragon» = «FUENTES DE ARAGON»)."""
    n = H.norm(colonia)
    if f" {n} " in f" {frase_norm} ":
        return True
    toks = [t.rstrip("s") for t in n.split() if t not in ARTICULOS and len(t) > 1]
    pal = {t.rstrip("s") for t in frase_norm.split()}
    return len(toks) >= 2 and all(t in pal for t in toks)


def _zonas_de_herramientas(usadas: list[dict]) -> dict:
    """{ageb: (zona, resultado de la herramienta que la dio)} de todas las llamadas a recomendar_zonas."""
    out = {}
    for u in usadas:
        r = u["resultado"]
        if u["nombre"] == "recomendar_zonas" and isinstance(r, dict) and r.get("encontrado"):
            for z in r["zonas"]:
                out.setdefault(z["ageb"], (z, r))
    return out


def _dist_km(lat1, lon1, lat2, lon2) -> float:
    import math
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 12742 * math.asin(math.sqrt(a))


def colonia_de_referencia(q: dict, feats) -> dict | None:
    """Centro de la colonia pedida, calculado aqui desde agebs_features (independiente de lugares.py):
    AGEB cuyo nom_colonia cumple la regex (y es del municipio dado). Regresa {agebs, lat, lon} o None."""
    c = q.get("colonia")
    if not c:
        return None
    rx = re.compile(c["regex"])
    sel = feats[feats["nom_colonia"].map(lambda x: bool(rx.search(H.norm(x))))]
    if c.get("muns"):
        sel = sel[sel.index.str[:5].isin(c["muns"])]
    if sel.empty:
        return None
    return {"agebs": set(sel.index), "lat": float(sel["lat"].mean()), "lon": float(sel["lon"].mean())}


COLA_SECCION = {"seccion", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "primera", "segunda", "tercera",
                "cuarta", "quinta", "sexta", "septima", "octava", "1", "2", "3", "4", "5", "6", "norte", "sur", "oriente", "poniente"}


def nombres_colonia_conocidos(feats) -> set:
    """Nombres normalizados de colonia (agebs_features) lo bastante especificos para buscarlos en el texto, y su raiz
    sin «seccion»/numero romano/orientacion («polanco iii seccion» -> «polanco»)."""
    out = set()
    for n in {H.norm(x) for x in feats["nom_colonia"].dropna()}:
        w = n.split()
        while len(w) > 1 and w[-1] in COLA_SECCION:
            w.pop()
        for nombre in {n, " ".join(w)}:
            ws = nombre.split()
            if nombre in GENERICOS_COLONIA or len(nombre) < 6 or all(t in GENERICOS_COLONIA or t in PALABRAS_VACIAS for t in ws):
                continue
            out.add(nombre)
    return out


COLONIA_EXPLICITA = re.compile(r"\b(?:colonia|col\.|fraccionamiento|barrio)\s+(?:de\s+|del\s+)?(?:la\s+|el\s+|los\s+|las\s+)?"
                               r"((?:[A-ZÁÉÍÓÚÑ][\wáéíóúñ]*)(?:\s+(?:(?:de|del|la|las|los|y)\s+)?[A-ZÁÉÍÓÚÑ0-9][\wáéíóúñ]*){0,4})")
CAMPOS_RENGLON = ("score", "prob_apertura_pct", "gasto_potencial_trim_mxn", "competidores_ponderados", "captura_huff_pct",
                  "ingreso_trim_mediano_estimado_mxn", "edad_clave_pct", "decil_estimado", "dist_a_colonia_km")


def _escrita_como_nombre(nombre: str, texto: str) -> bool:
    """Alguna aparicion de `nombre` (normalizado, una palabra) en el texto empieza con mayuscula o esta toda en mayusculas."""
    fl = lectura_mod.ligera(texto)
    return any(texto[m.start()].isupper() for m in re.finditer(rf"\b{re.escape(nombre)}\b", fl))


def calificar(q: dict, r: dict, feats, toks: list[str]) -> dict:
    texto = r["respuesta"] or ""
    usadas = r["herramientas"]
    tool_txt = json.dumps([u["resultado"] for u in usadas], ensure_ascii=False)
    checks = {}

    # 1) tokens
    checks["sin_tokens"] = not any(t in texto or t in tool_txt for t in toks)

    # 2) fuentes: seccion de fuentes, una fuente real y TODAS las que regresaron las herramientas (completa, no cortada)
    low = H.norm(texto)
    fuera_tema = q["tipo"] == "fuera_de_tema"      # texto fijo sin herramientas: no lleva fuentes ni cifras
    fu = []
    for u in usadas:
        if isinstance(u["resultado"], dict):
            fu += [f for f in u["resultado"].get("fuentes", []) if isinstance(f, str)]
    if not fuera_tema:
        checks["fuentes"] = ("fuente" in low) and any(H.norm(k) in low or k in texto.lower() for k in FUENTES_CLAVE)
        # las fuentes de una misma serie salen en una sola entrada con sus ids (agente.unir_fuentes); vale tambien el formato viejo
        from app import agente
        checks["fuentes_completas"] = (all(f in texto for f in dict.fromkeys(fu))
                                       or all(f in texto for f in agente.unir_fuentes(fu)))

    # 2b) nada de funciones internas (perfil_giro, recomendar_zonas, sugerir_giros(...)) en lo que ve la persona
    checks["sin_funciones_internas"] = not fuera.menciona_funciones(texto)

    # 3) latencia
    checks["latencia"] = r["latencia_s"] <= LAT_MAX_S

    # 3b) formato: «prob. de apertura % 63», «tipo de cambio fijo» y respuestas cortadas por num_predict
    checks["formato"] = (not PCT_MAL_RE.search(texto) and not FIJO_RE.search(texto) and not NONE_RE.search(texto)
                         and not r.get("cortada")
                         and texto.rstrip().endswith((".", ")", "*")))

    # 4) AGEB y colonias
    agebs = list(dict.fromkeys(AGEB_RE.findall(texto)))
    ageb_tools = set(AGEB_RE.findall(tool_txt))
    det = {"agebs_citadas": agebs}
    existen = all(a in feats.index for a in agebs)
    de_herr = all(a in ageb_tools for a in agebs)
    colonia_ok = all(H.norm(feats.at[a, "nom_colonia"]) in low for a in agebs if a in feats.index)
    det.update(agebs_existen=existen, agebs_de_herramientas=de_herr, colonias_coinciden=colonia_ok)
    tipo = q["tipo"]
    if tipo in ("giro", "sugerir"):
        zonas = [u["resultado"] for u in usadas if u["nombre"] == "recomendar_zonas" and u["resultado"].get("encontrado")]
        esperadas = min(5, max((len(z["zonas"]) for z in zonas), default=5))
        checks["top_agebs"] = existen and de_herr and colonia_ok and len(agebs) >= esperadas
        det["agebs_esperadas"] = esperadas
        if q.get("municipio"):
            checks["municipio"] = bool(agebs) and all(a[:5] == q["municipio"] for a in agebs)
    elif tipo == "trampa":
        checks["trampa_fuera_de_alcance"] = (not agebs) and bool(FUERA_RE.search(texto))
    elif tipo == "fuera_de_tema":
        checks["fuera_de_tema"] = (bool(SOLO_NEGOCIOS_RE.search(texto)) and not agebs and not usadas
                                   and not fuera.menciona_funciones(texto))
    else:
        checks["agebs_validas"] = existen and de_herr

    # 4b) cada renglon de zona: la colonia de SU AGEB (y no la de otra zona citada) y solo cifras de ESA zona
    zt = _zonas_de_herramientas(usadas)
    bloques = bloques_de_zona(texto, set(zt))
    if bloques:
        mal_colonia, mal_cifras = [], []
        for a, bl in bloques.items():
            z, res = zt[a]
            propia = H.norm(z["colonia"])
            lowb = " " + H.norm(bl) + " "
            if f" {propia} " not in lowb:
                mal_colonia.append(a)
            pedida = H.norm((res.get("filtros") or {}).get("colonia", ""))   # «a 1 km de la Condesa» no cuenta como otra colonia
            for a2, (z2, _) in zt.items():
                otra = H.norm(z2["colonia"])
                if a2 != a and a2 in bloques and otra != propia and f" {otra} " in lowb and otra not in propia and propia not in otra \
                        and otra not in pedida:
                    mal_colonia.append(a)
            nz = numeros_de([z, res.get("edad_clave"), res.get("filtros")])
            for c in cifras_citadas(bl, q["pregunta"]):
                if not coincide(c, nz):
                    mal_cifras.append(f"{a[-6:]}: {c['texto']}")
        det.update(renglones_con_otra_colonia=sorted(set(mal_colonia)), cifras_de_otra_zona=mal_cifras)
        checks["colonia_de_su_ageb"] = not mal_colonia
        checks["cifras_por_zona"] = not mal_cifras

    # 4b2) la lectura del modelo: cada frase que nombra una zona solo usa cifras de ESA zona (y de la magnitud que
    # nombra), y sus superlativos («mayor», «lidera», «menor»...) coinciden con el orden real del top
    m = re.search(r"\*\*Lectura:\*\*\s*(.*?)(?:\n\n|\Z)", texto, re.S)
    lectura_txt = m.group(1) if m else ""
    ctx = lectura_mod.Contexto(usadas, q["pregunta"])
    if m and (zt or ctx.giros):
        mal, super_mal = [], []
        for fr in lectura_mod.frases(lectura_txt):
            pr = lectura_mod.problemas(fr, ctx)
            mal += [f"{x} ({fr[:40]}…)" for x in pr["cifras"]]
            if pr["superlativos"]:
                super_mal.append(f"{fr[:60]}… ({'; '.join(pr['superlativos'])})")
        det["lectura_cifras_mal_atribuidas"] = mal
        det["lectura_superlativos_falsos"] = super_mal
        checks["lectura_cifras_de_su_zona"] = not mal
        checks["lectura_superlativos"] = not super_mal

    # 4c) colonias nombradas sin origen: nombres en negritas de un renglon de lista y nombres de colonia del catalogo
    origen = {H.norm(z["colonia"]) for z, _ in zt.values()}
    for u in usadas:
        rr = u["resultado"]
        if u["nombre"] == "ficha_zona" and isinstance(rr, dict):
            origen |= {H.norm(c["colonia"]) for c in rr.get("colonias", [])}
            if rr.get("ficha_ageb_mas_poblada"):
                origen.add(H.norm(rr["ficha_ageb_mas_poblada"]["colonia"]))
        ci = rr.get("colonia_consultada") if isinstance(rr, dict) else None
        if ci:
            origen |= {H.norm(c) for c in ci.get("colonias_coincidentes", [])}
    tool_low = " " + H.norm(tool_txt) + " " + " " + H.norm(q["pregunta"]) + " " + " ".join(H.norm(m.get("content", "")) for m in q.get("historial", []))
    sospechosas = []
    for nombre in nombres_colonia_conocidos(feats):
        sin_art = re.sub(r"^(?:el|la|los|las)\s+", "", nombre)
        if f" {nombre} " in " " + low + " " and f" {nombre} " not in tool_low and f" {sin_art} " not in tool_low:
            # una colonia de una sola palabra («Mercado») escrita en minuscula es el sustantivo comun («la captura del mercado»)
            if len(nombre.split()) == 1 and not _escrita_como_nombre(nombre, texto):
                continue
            sospechosas.append(nombre)
    for m in re.finditer(r"(?m)^\s*\d+[.)]\s+\*\*([^*]+)\*\*", texto):
        nm = H.norm(m.group(1))
        if nm and nm not in origen and not _es_giro_o_mun(nm):
            sospechosas.append(nm)
    # una colonia inventada o sin origen nombrada con «colonia X» / «fraccionamiento X» en cualquier parte del texto
    for mm in COLONIA_EXPLICITA.finditer(texto):
        nc = H.norm(mm.group(1))
        if nc and not _es_giro_o_mun(nc) and f" {nc} " not in tool_low and not any(f" {nc} " in f" {o} " or f" {o} " in f" {nc} " for o in origen):
            sospechosas.append(nc)
    det["colonias_sin_origen"] = sorted(set(sospechosas))
    if tipo in ("giro", "sugerir", "trampa"):
        checks["colonias_con_origen"] = not sospechosas

    # 5) herramienta correcta
    if q.get("giro"):
        checks["giro"] = any(u["nombre"] == "recomendar_zonas" and u["resultado"].get("giro") == q["giro"] for u in usadas)
    if q.get("nse"):
        checks["nse"] = any(u["nombre"] == "recomendar_zonas" and (u["resultado"].get("filtros") or {}).get("nse") == q["nse"]
                            for u in usadas)
    if tipo == "macro":
        macro = [u["resultado"] for u in usadas if u["nombre"] == "contexto_macro"]
        checks["macro_usada"] = bool(macro)
        # que la respuesta si hable de macro: al menos 2 cifras que salen de contexto_macro
        nm = numeros_de(macro)
        det["cifras_macro"] = sum(coincide(c, nm) for c in cifras_citadas(texto, q["pregunta"]))
        checks["macro_cifras"] = det["cifras_macro"] >= 2

    # 5a) colonia pedida: AGEB a <= 2 km de la colonia, o aviso explicito (no encontrada / sin filtro)
    ref = colonia_de_referencia(q, feats)
    if q.get("colonia"):
        distancias = {a: round(_dist_km(feats.at[a, "lat"], feats.at[a, "lon"], ref["lat"], ref["lon"]), 2)
                      for a in agebs if a in feats.index} if ref else {}
        cerca = bool(agebs) and ref is not None and all(d <= RADIO_COLONIA_KM + 0.05 or a in ref["agebs"]
                                                        for a, d in distancias.items())
        filtro = any(u["nombre"] == "recomendar_zonas" and (u["resultado"].get("filtros") or {}).get("colonia") for u in usadas)
        dentro = any(a in ref["agebs"] for a in agebs) if ref else False
        det.update(distancias_a_colonia_km=distancias, alguna_dentro_de_la_colonia=dentro)
        checks["colonia_respetada"] = cerca and filtro and dentro
    if q.get("colonia_inexistente"):
        nombre = H.norm(q["colonia_inexistente"])
        aviso = bool(NO_ENCONTRADO_RE.search(texto)) and nombre in low and bool(A_CAMBIO_RE.search(texto))
        # sin filtro, o con el de la colonia MAS PARECIDA si el aviso lo dice (la pedida queda en colonia_no_encontrada)
        no_filtro = not any((u["resultado"].get("filtros") or {}).get("colonia")
                            and not (u["resultado"].get("filtros") or {}).get("colonia_no_encontrada")
                            for u in usadas if u["nombre"] == "recomendar_zonas" and isinstance(u["resultado"], dict))
        checks["colonia_respetada"] = aviso and no_filtro

    # 5b) honestidad del score: es relativo dentro del giro (no compara giros ni dice viabilidad)
    rz = [u["resultado"] for u in usadas if u["nombre"] == "recomendar_zonas" and u["resultado"].get("encontrado")]
    if any(z.get("aviso_prob_baja") for z in rz):  # prob. de apertura baja en todo el top: debe decirlo
        checks["aviso_prob_baja"] = bool(RELATIVO_RE.search(texto)) and bool(BAJA_RE.search(texto))
    if rz and tipo in ("giro", "sugerir"):
        checks["score_relativo_dicho"] = bool(RELATIVO_RE.search(texto))
    sg = [u["resultado"] for u in usadas if u["nombre"] == "sugerir_giros" and u["resultado"].get("encontrado")]
    if not sg:  # «viabilidad» o una lista de giros sin haber llamado sugerir_giros = cifras inventadas
        checks["sin_giros_inventados"] = not VIABILIDAD_RE.search(texto)
    if tipo == "sugerir":
        checks["sugerir_usada"] = bool(sg)
        if sg:  # que presente las alternativas que regreso la herramienta, no solo la primera, EN SU ORDEN
            claves = [g["giro"] for g in sg[0]["giros"]]
            nombrados = [c for c in claves if _giro_mencionado(c, low)]
            det["giros_sugeridos"], det["giros_mencionados"] = claves, nombrados
            checks["alternativas"] = len(nombrados) >= min(3, len(claves))
            checks["score_relativo"] = bool(RELATIVO_RE.search(texto))
            checks["orden_sugerir"] = lectura_mod.orden_de_giros(lectura_txt, claves) if lectura_txt else True
            if sg[0].get("criterio_inversion"):
                checks["inversion_explicada"] = bool(re.search(r"inversi[oó]n|barato|costo", texto, re.I))

    # 5b2) los avisos que dicen que el modelo o el gasto del giro no son confiables (giro raro, rubro ENIGH sustituto) se muestran
    clave_av = []
    for u in usadas:
        rr = u["resultado"]
        if u["nombre"] == "recomendar_zonas" and isinstance(rr, dict) and rr.get("encontrado"):
            rubro = motor.giros().get(rr["giro"], {}).get("rubro_enigh_nota")
            clave_av += [a for a in rr.get("avisos", []) if a.startswith("giro raro") or (rubro and a == rubro)
                         or a == rr.get("aviso_rubro_amplio")]
    if clave_av:
        clave_av = list(dict.fromkeys(clave_av))
        det["avisos_del_giro"] = clave_av
        checks["avisos_del_giro"] = all(a in texto or (a[0].upper() + a[1:]) in texto for a in clave_av)

    # 5c) seguimiento: mantiene el giro de los turnos anteriores
    if q.get("historial") and q.get("giro"):
        checks["seguimiento_mantiene_giro"] = (
            any(u["nombre"] == "recomendar_zonas" and u["resultado"].get("giro") == q["giro"] for u in usadas)
            and _giro_mencionado(q["giro"], low))

    # 5d) ingreso (en pesos) y edad clave de cada zona citada
    if rz and tipo in ("giro", "sugerir") and bloques:
        ok_ie = 0
        for a, bl in bloques.items():
            z, _ = zt[a]
            nb = {c["valor"] for c in cifras_citadas(bl, "")}
            ing = z.get("ingreso_trim_mediano_estimado_mxn")
            pct = z.get("edad_clave_pct")
            tiene_ing = isinstance(ing, (int, float)) and any(abs(v - ing) <= 50 for v in nb) and bool(re.search(r"\$", bl))
            tiene_edad = (isinstance(pct, (int, float)) and any(abs(v - pct) <= 0.051 for v in nb)) \
                or (not isinstance(pct, (int, float)) and "NO ENCONTRADO" in bl and not NONE_RE.search(bl))
            ok_ie += tiene_ing and tiene_edad
        det["zonas_con_ingreso_y_edad"] = f"{ok_ie}/{len(bloques)}"
        checks["ingreso_y_edad"] = ok_ie >= max(1, MIN_ZONAS_INGRESO_EDAD * len(bloques))

    # 5d2) pulido final: la referencia de edad va en su linea (no mezclada con el encabezado), el sinonimo del giro se dice,
    # una AGEB casi vacia lleva su aviso en el renglon y la pregunta de ingreso se contesta con la cifra del municipio
    if rz and tipo in ("giro", "sugerir"):
        from app import agente
        if any(r_.get("edad_clave") for r_ in rz):
            checks["referencia_edad"] = bool(re.search(r"(?m)^Referencia: en la ZMVM, [\d.,]+ % de la población tiene", texto)) \
                and not re.search(r"relativo al giro;", texto)
        sinonimos = [agente.sinonimo_usado(usadas, r_["giro"]) for r_ in rz]
        if any(sinonimos):
            checks["sinonimo_dicho"] = "Tomé «" in texto
        vacias = {a: zt[a][0]["aviso_ageb_poco_poblada"] for a in bloques if zt[a][0].get("aviso_ageb_poco_poblada")}
        if vacias:
            det["agebs_casi_vacias"] = sorted(vacias)
            checks["aviso_ageb_vacia"] = all(av in bloques[a] for a, av in vacias.items())
    fm = [u["resultado"] for u in usadas if u["nombre"] == "ficha_municipio" and isinstance(u["resultado"], dict)
          and u["resultado"].get("ingreso_linea")]
    if fm and H.pide_ingreso(q["pregunta"]):
        checks["ingreso_municipio"] = H._pesos_txt(fm[0]["ingreso_trim_mediano_est_hogar_mxn"]) in texto

    # 5e) macro breve: una linea de Banxico/INEGI con cifras reales de contexto_macro, sin extenderse
    mg = [u["resultado"] for u in usadas if u["nombre"] == "contexto_macro" and isinstance(u["resultado"], dict) and u["resultado"].get("linea")]
    if mg and tipo in ("giro", "sugerir"):
        nm = numeros_de(mg)
        cit = [c for c in cifras_citadas(texto, q["pregunta"]) if coincide(c, nm)]
        parrafos = [p for p in texto.split("\n") if not p.startswith(("**Fuentes", ">")) and re.search(r"banxico|inegi|inpc|inflaci|tasa objetivo|macro|econ[oó]mic", p, re.I)]
        mayor = max((len(p) for p in parrafos), default=0)
        det["macro_cifras_citadas"], det["macro_parrafo_chars"] = len(cit), mayor
        checks["macro_breve"] = len(cit) >= 2 and mayor <= MACRO_BREVE_MAX_CHARS and bool(re.search(r"banxico|inegi", texto, re.I))
        if PIDE_COMO_RE.search(q["pregunta"]) or H.pide_como_influye(q["pregunta"]):   # «¿cómo influye...?» pide el mecanismo, no solo dos cifras
            checks["macro_mecanismo"] = len(MECANISMO_RE.findall(re.sub(r"\*\*Fuentes.*", "", texto, flags=re.S))) >= 2

    # 6) cifras
    nums = numeros_de([u["resultado"] for u in usadas])
    cit = cifras_citadas(texto, q["pregunta"])
    malas = [c["texto"] for c in cit if not coincide(c, nums)]
    frac = 1.0 if not cit else 1 - len(malas) / len(cit)
    det.update(cifras_citadas=len(cit), cifras_no_encontradas=malas, frac_cifras_ok=round(frac, 3))
    checks["cifras"] = frac >= MIN_CIFRAS_OK and len(malas) <= MAX_CIFRAS_MAL and (tipo in ("trampa", "fuera_de_tema") or len(cit) > 0)

    return {"checks": checks, "detalle": det, "pasa": all(checks.values())}


def _es_giro_o_mun(nm: str) -> bool:
    """Nombre en negritas que es un giro o un municipio (no una colonia)."""
    from app import motor

    if any(nm in H.norm(g.replace("_", " ")) or nm in {H.norm(x) for x in v.get("nombres", [])}
           for g, v in motor.giros().items()):
        return True
    return nm in {H.norm(m) for m in H.municipios()["nom_mun"]}


# ---------------------------------------------------------------- correr
def cargar_parcial() -> dict:
    if not PARCIAL.exists():
        return {}
    out = {}
    for line in PARCIAL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            out[d["id"]] = d
    return out


def correr(preguntas: list[dict]) -> None:
    from app import agente

    hechas = cargar_parcial()
    for q in preguntas:
        if q["id"] in hechas:
            continue
        m0 = memoria()
        r = agente.responder(q["pregunta"], historial=q.get("historial"))
        m1 = memoria()
        fila = {"id": q["id"], "pregunta": q["pregunta"], "respuesta": r["respuesta"], "modo": r["modo"],
                "rondas": r["rondas"], "latencia_s": r["latencia_s"], "cortada": r.get("cortada"), "herencia": r.get("herencia"), "metricas": r.get("metricas"),
                "herramientas": [{"nombre": u["nombre"], "args": u["args"], "resultado": u["resultado"]} for u in r["herramientas"]],
                "mem_antes": m0, "mem_despues": m1}
        with PARCIAL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        print(f"[{q['id']:>2}] {r['latencia_s']:>6.1f} s  {r['modo']}  {r.get('metricas')}  swap {m1.get('swap_mb')} MB  "
              f"libre {m1.get('mem_libre_pct')} %  {q['pregunta'][:50]}", flush=True)


def reporte(preguntas: list[dict]) -> dict:
    from app import motor

    feats = motor.cargar_features()
    toks = tokens_env()
    hechas = cargar_parcial()
    filas = []
    for q in preguntas:
        if q["id"] not in hechas:
            continue
        r = hechas[q["id"]]
        c = calificar(q, r, feats, toks)
        filas.append({**{k: r[k] for k in ("id", "pregunta", "respuesta", "modo", "rondas", "latencia_s", "mem_antes", "mem_despues")},
                      "tipo": q["tipo"], "grupo": q.get("grupo", "original"), "historial": q.get("historial"), "herramientas": [{"nombre": u["nombre"], "args": u["args"]} for u in r["herramientas"]],
                      **c})
    lat = [f["latencia_s"] for f in filas]
    swaps = [f["mem_despues"].get("swap_mb") for f in filas if f["mem_despues"].get("swap_mb") is not None]
    libres = [f["mem_despues"].get("mem_libre_pct") for f in filas if f["mem_despues"].get("mem_libre_pct") is not None]
    trampa = [f for f in filas if f["tipo"] == "trampa"]
    fuera_f = [f for f in filas if f["tipo"] == "fuera_de_tema"]
    n_ok = sum(f["pasa"] for f in filas)
    obligatorias = [f for f in filas if f["grupo"] in ("colonia", "seguimiento")]
    obligatorias_ok = all(f["pasa"] for f in obligatorias)
    res = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "modelo": "qwen3:8b (Ollama, think=False)", "preguntas": len(filas),
           "total_en_yaml": len(preguntas),
           "pasan": n_ok, "trampa_pasa": bool(trampa) and trampa[0]["pasa"],
           "colonia_y_seguimiento_pasan": f"{sum(f['pasa'] for f in obligatorias)}/{len(obligatorias)}",
           "fuera_de_tema_pasan": f"{sum(f['pasa'] for f in fuera_f)}/{len(fuera_f)}",
           "aprobado": (len(filas) == len(preguntas) and n_ok >= MIN_APROBADO * len(preguntas) and bool(trampa)
                        and trampa[0]["pasa"] and obligatorias_ok and bool(fuera_f) and all(f["pasa"] for f in fuera_f)),
           "latencia_mediana_s": round(statistics.median(lat), 1) if lat else None,
           "latencia_p90_s": round(sorted(lat)[int(0.9 * (len(lat) - 1))], 1) if lat else None,
           "latencia_max_s": max(lat) if lat else None,
           "mediana_bajo_objetivo": bool(lat) and statistics.median(lat) <= LAT_OBJETIVO_MED_S,
           "latencia_meta_ok": bool(lat) and statistics.median(lat) <= 120 and max(lat) <= 165,
           "swap_mb_inicio": filas[0]["mem_antes"].get("swap_mb") if filas else None,
           "swap_mb_max": max(swaps) if swaps else None, "swap_mb_fin": swaps[-1] if swaps else None,
           "mem_libre_pct_min": min(libres) if libres else None,
           "criterios": {"latencia_max_s": LAT_MAX_S, "mediana_objetivo_s": LAT_OBJETIVO_MED_S,
                         "frac_cifras_min": MIN_CIFRAS_OK, "max_cifras_sin_origen": MAX_CIFRAS_MAL},
           "filas": filas}
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "evaluacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (REPORTS / "evaluacion.md").write_text(md(res), encoding="utf-8")
    return res


def md(res: dict) -> str:
    n = res["total_en_yaml"]
    L = [f"# Evaluación del agente ({res['fecha']})", "",
         f"Modelo: {res['modelo']}. Preguntas: {res['preguntas']} de {n} (`eval/preguntas.yaml`). Script: `eval/evaluar.py`.", "",
         f"**Resultado: {res['pasan']}/{res['preguntas']} pasan; trampa {'pasa' if res['trampa_pasa'] else 'NO pasa'}; "
         f"fuera de tema {res['fuera_de_tema_pasan']}; colonia y seguimiento {res['colonia_y_seguimiento_pasan']} → "
         f"{'APROBADO' if res['aprobado'] else 'NO APROBADO'}** (criterio: ≥ {int(100 * MIN_APROBADO)} % de las preguntas, la trampa, "
         "las tres fuera de tema y todas las de colonia y de seguimiento).", "",
         f"- Latencia: mediana {res['latencia_mediana_s']} s, p90 {res['latencia_p90_s']} s, máxima {res['latencia_max_s']} s "
         f"(meta: mediana ≤ {res['criterios']['mediana_objetivo_s']} s y máxima ≤ {res['criterios']['latencia_max_s']} s: "
         f"{'cumplida' if res['latencia_meta_ok'] else 'NO cumplida'}; una respuesta de más de {res['criterios']['latencia_max_s']} s falla).",
         f"- Memoria (MacBook Air M4, 16 GB): swap {res['swap_mb_inicio']} MB al inicio, máximo {res['swap_mb_max']} MB, "
         f"{res['swap_mb_fin']} MB al final; memoria libre mínima {res['mem_libre_pct_min']} % (`memory_pressure`).", "",
         "## Checks", "",
         "- `sin_tokens`: ningún valor de `.env` aparece en la respuesta ni en lo que regresaron las herramientas.",
         "- `fuentes`: la respuesta tiene sección de fuentes y nombra al menos una fuente real (INEGI, DENUE, ENIGH, CONAPO, Banxico, carpetas...).",
         "- `fuentes_completas`: todas las fuentes que regresaron las herramientas están en la respuesta (no se corta la lista).",
         f"- `latencia`: ≤ {LAT_MAX_S} s.",
         "- `formato`: sin «prob. de apertura % 63» (debe ser «63 %»), sin «tipo de cambio fijo» (es FIX), sin «None» ni «nan» impresos (un dato vacío se dice «NO ENCONTRADO») y sin respuesta cortada por `num_predict`.",
         "- `top_agebs`: cada AGEB citada existe en `agebs_features`, salió de una herramienta, su colonia (de `agebs_features`) "
         "aparece en la respuesta y hay al menos 5 (o las que regresó la herramienta).",
         "- `colonia_de_su_ageb`: cada renglón de zona (desde la línea con la clave AGEB hasta la siguiente) trae la colonia de SU AGEB y no la de otra zona citada.",
         "- `cifras_por_zona`: las cifras de cada renglón coinciden con las de la zona a la que se atribuyen (no con las de otra).",
         "- `lectura_cifras_de_su_zona`: en la «Lectura» del modelo, cada frase que nombra una zona solo usa cifras de esa zona (si un nombre está dentro de otro más largo, «Granada» en «Ampliación Granada», manda la coincidencia más larga) y cada cifra se compara solo con el campo que nombra («prob. de apertura», «gasto potencial», «ingreso», «competidores», «edad clave») o, sin magnitud, con los campos del renglón de la zona; no con cualquier número del resultado.",
         "- `lectura_cifras_de_su_zona` (a partir de la evaluación final): además, cada cifra tiene que salir de alguna herramienta y ser de su tipo (un % solo se compara con campos en %, los pesos con pesos); las de `perfil_giro`, `contexto_macro` y `ficha_municipio` valen en cualquier frase; la viabilidad de un giro de `sugerir_giros` solo vale con ese giro; y a un giro sin `recomendar_zonas` no se le atribuyen zonas ni gasto potencial.",
         "- `lectura_superlativos`: «mayor», «menor», «lidera(n)», «destaca», «mejor(es)»... junto con una magnitud (prob. de apertura, gasto, ingreso, competidores, edad, score u «oportunidad / mejor opción») solo valen si la zona nombrada es de las primeras del top en esa magnitud (`app/lectura.py`); sin magnitud escrita se deduce de la cifra que sigue («lidera con un 12.5 %»); el giro que «lidera» es el 1 de `sugerir_giros`; y «En <colonia pedida>, la colonia Z» solo si Z está dentro de la colonia; un adjetivo de nivel sin cifra («alto porcentaje de niños de 0 a 14 años») solo vale si la zona está por encima de la referencia de la ZMVM que trae la respuesta («bajo», por debajo), y con «ambas» valen todas las zonas ya nombradas.",
         "- `avisos_del_giro`: los avisos «giro raro», el del rubro ENIGH sustituto y el del rubro ENIGH amplio («el gasto potencial usa el rubro ENIGH ... completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros») de `recomendar_zonas` aparecen en la respuesta (en los riesgos).",
         "- `referencia_edad`: la edad clave del giro en la ZMVM va en su propia línea («Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).»), no dentro del encabezado del top.",
         "- `sinonimo_dicho`: si la pregunta usó otro nombre del giro («nevería»), una línea dice con qué giro del catálogo se quedó («Tomé «nevería» como heladería...»).",
         "- `aviso_ageb_vacia`: una zona del top con menos de 200 habitantes o menos de 50 hogares lleva en su renglón el aviso de que el gasto viene del radio de influencia.",
         "- `ingreso_municipio`: si la pregunta pide el ingreso («¿cuánto ganan?») y hay ficha del municipio, la respuesta trae el ingreso trimestral mediano estimado por hogar del municipio.",
         "- `macro_mecanismo` (pregunta «¿cómo influye...?»): la respuesta explica el mecanismo (costo, insumos, crédito, financiamiento, margen, precio).",
         "- `colonias_con_origen`: ninguna colonia del catálogo de `agebs_features`, renglón de lista en negritas ni nombre escrito como «colonia X» / «fraccionamiento X» aparece sin salir de las herramientas, de la pregunta o del historial.",
         "- `municipio`, `giro`, `nse`, `macro_usada`: se usó la herramienta con el giro/filtro esperado y las AGEB son del municipio pedido.",
         "- `macro_cifras` (pregunta macro): la respuesta cita al menos 2 cifras de `contexto_macro`.",
         f"- `macro_breve` (giro con `contexto_macro`): al menos 2 cifras de la línea macro y el párrafo no pasa de {MACRO_BREVE_MAX_CHARS} caracteres.",
         f"- `ingreso_y_edad`: al menos el {int(100 * MIN_ZONAS_INGRESO_EDAD)} % de las zonas citadas traen su ingreso trimestral estimado en pesos y el % de la edad clave del giro.",
         f"- `colonia_respetada` (preguntas con colonia): toda AGEB citada es de la colonia o está a ≤ {RADIO_COLONIA_KM:g} km de su centroide (calculado aquí desde `agebs_features`), al menos una es de la colonia misma y la herramienta recibió el filtro; "
         "con una colonia inexistente: la respuesta dice «no se encontró», nombra la colonia y explica qué da a cambio, y no aplicó filtro.",
         "- `seguimiento_mantiene_giro` (preguntas con historial): el giro de los turnos anteriores se conserva en la herramienta y en la respuesta.",
         f"- `cifras`: a lo más {MAX_CIFRAS_MAL} cifras sin origen y al menos {int(100 * MIN_CIFRAS_OK)} % de las cifras citadas coinciden con un número de las herramientas, con tolerancia "
         "de redondeo según los decimales escritos («0.43 millones» = 430,000; una fracción de la herramienta puede citarse como %). No se verifican enteros ≤ 10 "
         "(enumeraciones, deciles), años ni fechas.",
         "- `trampa_fuera_de_alcance`: dice que está fuera de alcance y no da ninguna AGEB.",
         "- `fuera_de_tema` (preguntas de nombre, saludo o tema ajeno: «¿Cómo me llamo?», «hola», «¿Quién ganó el último mundial?»): el texto fijo dice que solo contesta sobre negocios en la Zona Metropolitana del Valle de México, no da ninguna AGEB, no llama herramientas (no usa el LLM) y no menciona funciones internas. Estas preguntas no llevan `fuentes` ni `cifras`.",
         "- `sin_funciones_internas` (todas las preguntas): la respuesta no nombra `perfil_giro`, `recomendar_zonas`, `ficha_zona`, `sugerir_giros`, `buscar_carpetas`, `contexto_macro` ni `ficha_municipio` y no escribe llamadas tipo `f(x=...)`.",
         "- `aviso_prob_baja`: si `recomendar_zonas` avisa que la prob. de apertura es baja en todo el top, la respuesta lo dice y aclara que el score es relativo al giro.",
         "- `score_relativo_dicho`: con zonas recomendadas, la respuesta dice que el score es relativo dentro del giro.",
         "- `sin_giros_inventados`: sin `sugerir_giros`, la respuesta no habla de «viabilidad» ni lista «giros que conviene».",
         "- `sugerir_usada`, `alternativas`, `score_relativo`, `orden_sugerir`, `inversion_explicada` (preguntas sin giro): se usó `sugerir_giros`, la respuesta nombra al menos 3 de los giros que regresó, y la Lectura los nombra en el orden de la herramienta, dice que el score es relativo dentro de cada giro y, si pidió algo barato, explica que se entendió como poca inversión.", "",
         "## Resultados por pregunta", "",
         "| # | Pregunta | Pasa | Latencia (s) | Herramientas | Cifras ok | Checks que fallan |", "|---|---|---|---|---|---|---|"]
    for f in res["filas"]:
        fallan = [k for k, v in f["checks"].items() if not v]
        L.append(f"| {f['id']} | {f['pregunta']} | {'sí' if f['pasa'] else 'NO'} | {f['latencia_s']} | "
                 f"{', '.join(h['nombre'] for h in f['herramientas'])} | "
                 f"{f['detalle']['cifras_citadas'] - len(f['detalle']['cifras_no_encontradas'])}/{f['detalle']['cifras_citadas']} | "
                 f"{', '.join(fallan) or '-'} |")
    L += ["", "## Respuestas completas", ""]
    for f in res["filas"]:
        L += [f"### {f['id']}. {f['pregunta']}", "",
              f"_{f['modo']}, {f['rondas']} rondas, {f['latencia_s']} s; herramientas: "
              + "; ".join(f"{h['nombre']}({json.dumps(h['args'], ensure_ascii=False)})" for h in f["herramientas"]) + "_", ""]
        if f["detalle"]["cifras_no_encontradas"]:
            L += [f"Cifras que no salen de las herramientas: {', '.join(f['detalle']['cifras_no_encontradas'])}", ""]
        L += ["> " + line for line in f["respuesta"].splitlines()] + [""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-checks", action="store_true", help="califica lo guardado sin llamar al LLM")
    ap.add_argument("--rehacer", action="store_true", help="borra lo parcial y vuelve a correr")
    ap.add_argument("--ids", help="solo estas preguntas, p. ej. 1,20")
    ap.add_argument("--salida", help="carpeta para evaluacion.md/json y el parcial (pruebas parciales sin pisar reports/)")
    a = ap.parse_args()
    if a.salida:
        REPORTS = Path(a.salida)
        REPORTS.mkdir(parents=True, exist_ok=True)
        PARCIAL = REPORTS / "evaluacion_parcial.jsonl"
    qs = yaml.safe_load((RAIZ / "eval" / "preguntas.yaml").read_text(encoding="utf-8"))["preguntas"]
    if a.ids:
        ids = {int(x) for x in a.ids.split(",")}
        qs_run = [q for q in qs if q["id"] in ids]
    else:
        qs_run = qs
    if a.rehacer and PARCIAL.exists():
        PARCIAL.unlink()
    if not a.solo_checks:
        correr(qs_run)
    res = reporte(qs)
    print(f"{res['pasan']}/{res['preguntas']} pasan; trampa {'ok' if res['trampa_pasa'] else 'FALLA'}; "
          f"mediana {res['latencia_mediana_s']} s; swap max {res['swap_mb_max']} MB; aprobado={res['aprobado']}")
