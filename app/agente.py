"""Agente local: qwen3:8b (Ollama) con tool calling sobre app/herramientas.py.

    uv run python app/agente.py "quiero poner una heladeria"

Flujo:
0. Fuera de tema («¿cómo me llamo?», «hola», deportes...; app/fuera_de_tema.py): sin herramientas ni LLM, texto fijo.
   Y una red de seguridad: si el modelo nombra funciones internas (perfil_giro, sugerir_giros(...)), esas frases se quitan.
1. Pre-consulta deterministica (sin LLM): con reglas simples se llaman las herramientas obvias
   (perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio, sugerir_giros) y sus resultados entran a la
   conversacion como llamadas ya hechas. Detecta colonias (app/lugares.py) y hereda giro, municipio, colonia y NSE
   de los turnos anteriores en los seguimientos («¿y en Coyoacan?»). Ahorra rondas del modelo (latencia) y lo ancla en datos.
2. Bucle de tool calling: el modelo puede pedir mas herramientas (ficha_zona, buscar_carpetas...)
   hasta MAX_RONDAS; luego redacta. Al modelo le llega una vista compacta de cada resultado (`para_llm`).
3. Respuesta en dos partes. Lo que son datos lo arma el codigo (`bloques`): aviso de colonia, el top de zonas con las
   cifras de CADA zona, los giros en el orden de la herramienta, el contexto macro y la ficha del municipio. El LLM escribe
   solo lo que pide criterio: la lectura (que distingue a las zonas) y los riesgos. Asi las cifras no se mezclan entre
   zonas, el formato es fijo («63 %») y la latencia baja (menos tokens generados). Al final `cerrar` completa la seccion de
   fuentes (nunca cortada), corrige «FIX» y evita renglones a medias.
4. Si Ollama no responde, se arma una respuesta de plantilla con los mismos resultados (modo 'plantilla').
Todo corre en la Mac: no usa internet.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import herramientas as H  # noqa: E402
from app import fuera_de_tema as fuera, lectura as lectura_mod, lugares, rag  # noqa: E402

MODELO = "qwen3:8b"
HOST = "http://localhost:11434"
MAX_RONDAS = 4
OPCIONES = {"temperature": 0.2, "num_ctx": 8192, "num_predict": 700}
HISTORIAL_MAX_CHARS = 500  # lo que se conserva de cada respuesta anterior del asistente (menos prompt, menos latencia)

SYSTEM = """Eres un asesor de ubicación de negocios para la Zona Metropolitana del Valle de México (ZMVM: 16 alcaldías de la CDMX, 59 municipios del Estado de México y Tizayuca, Hidalgo). Respondes en español de México, claro y directo.

Reglas duras:
- Usa SOLO cifras, colonias, municipios y claves AGEB que aparezcan en los resultados de las herramientas. Copia los números tal como vienen. No calcules cifras nuevas, no inventes datos ni colonias.
- Los porcentajes se escriben «63 %» (número y luego el signo), nunca «% 63».
- Si una herramienta dice "NO ENCONTRADO" o encontrado=false, dilo así. Si piden un lugar fuera de la ZMVM (por ejemplo Monterrey), di claramente que está fuera de alcance del modelo y NO des colonias.
- Si recomendar_zonas trae "aviso_colonia", el sistema lo pone al inicio de la respuesta (qué colonia se usó, qué filtro, o si no se encontró, qué se da a cambio). Tu texto debe ser coherente con él: si la colonia no se encontró, no digas que las zonas son de esa colonia.
- El NSE, el decil y el ingreso por colonia son estimaciones del proyecto: di "estimado". El ticket promedio es un supuesto.
- Si falta información, llama otra herramienta (ficha_zona, buscar_carpetas, contexto_macro) antes de responder.
- El score 0-100 es un percentil DENTRO de cada giro: ordena colonias para ese giro, no dice que el giro sea viable y no sirve para comparar giros.
- El tipo de cambio se llama «FIX», nunca «tipo de cambio fijo».

Para preguntas de economía (macro) responde con los indicadores, su fecha y su serie, sin calificarlos («moderada», «alta expectativa»): di su valor y qué mide, no cómo se «refleja» en el gasto. No uses más de 450 palabras."""

# Cuando el sistema ya muestra los datos (zonas, giros, macro, ficha), el modelo solo escribe la lectura y los riesgos.
REGLA_COMPLEMENTO = """
IMPORTANTE: el sistema ya muestra solo, junto a tu texto, el aviso de colonia, el top de zonas con sus cifras, los giros, el contexto económico, la ficha del municipio, los riesgos y las fuentes. NO los repitas ni escribas renglones por zona. Escribe SOLO una sección:
**Lectura:** 2 a 4 frases (máximo 80 palabras) que contesten directamente lo que preguntó la persona (por ejemplo cuánto ganan o qué porcentaje es de cierta edad, usando las cifras de las zonas) y que digan qué distingue a las primeras zonas o giros. Apóyate en `destacados` y copia 2 o 3 cifras exactas de los resultados, cada una junto al nombre de su zona y con su nombre exacto («gasto potencial», «ingreso trimestral estimado por hogar», «prob. de apertura»): no uses la cifra de una zona para otra ni confundas una magnitud con otra. Máximo 2 zonas por frase. Di «mayor», «menor», «lidera», «mejor» o «destaca» SOLO para la zona que `destacados` marca con esa magnitud (si trae `empatan`, nombra todas esas zonas: «A y B empatan con...»), y «la mejor opción» solo para la zona 1 del top (la 2.ª, 3.ª... no es «la mayor»); no digas qué grupo «lidera» con un porcentaje sin compararlo con las demás zonas; si una zona queda a km de la colonia pedida, no digas que está «en» ella. No escribas claves AGEB ni negritas dentro de la lectura. Empieza con «**Lectura:**»."""
REGLA_SUGERIR = """
Esta vez se llamó sugerir_giros (la persona no trae giro): la lectura compara los giros de la lista (el sistema ya los muestra en su orden, por viabilidad) y recuerda que el score de las colonias es relativo dentro de cada giro. Nombra los giros en el orden de la lista; «lidera» o «mayor viabilidad» es solo el giro 1, con SU viabilidad. Las zonas y su gasto potencial son del giro de recomendar_zonas: no se las atribuyas a otro giro de la lista."""
REGLA_PROB_BAJA = """
Esta vez recomendar_zonas trae "aviso_prob_baja": la probabilidad de apertura es baja en todo el top (el sistema ya lo avisa). En tu lectura di que el score alto es relativo al giro, no prueba de que el giro sea viable. No hables de «viabilidad» ni listes otros giros: aquí no se llamó sugerir_giros."""
REGLA_COMO = """
La persona pregunta CÓMO influye o afecta algo (el contexto macro trae `como_influye`): en tu lectura explica el mecanismo con esas frases (los insumos del giro, la tasa real aproximada frente a la inflación, crédito, margen, precio) y no agregues cifras que no estén en los resultados ni recomendaciones que no salgan de ellas. No te limites a repetir los indicadores. La tasa objetivo es la tasa de política de Banxico, no la tasa a la que el negocio pide prestado (esa es la TIIE más un margen): no la presentes como el costo del crédito del negocio. Explica solo lo que aplica al giro de la pregunta. Si la pregunta no pide zonas, no nombres colonias: el sistema ya muestra el top."""
REGLA_INGRESO = """
La persona pregunta por el INGRESO de la gente: el sistema ya muestra el ingreso trimestral mediano estimado por hogar del municipio ({ingreso}). Contesta primero con esa cifra, dilo como estimación del proyecto, y luego compara 1 o 2 zonas con su ingreso trimestral estimado. No uses otra cifra de ingreso del municipio."""
REGLA_AGEB_VACIA = """
Alguna zona trae `aviso` (AGEB con muy pocos habitantes: el gasto viene del radio de influencia, no de quienes viven ahí). Si la nombras como «la mejor opción» o por su score, repite ese aviso en la misma frase."""
REGLA_HERENCIA = """
Esta pregunta continúa la conversación (el sistema ya dice qué se mantiene: {que}). Contesta solo lo nuevo que pide la persona."""


def _usada(usadas: list[dict], nombre: str) -> dict | None:
    for u in usadas:
        r = u["resultado"]
        if u["nombre"] == nombre and isinstance(r, dict) and (r.get("encontrado") or r.get("linea") or r.get("indicadores")):
            return r
    return None


def system_para(usadas: list[dict], herencia: dict | None = None, pregunta: str = "") -> str:
    """Prompt del sistema: reglas y, segun los resultados de las herramientas, lo que el modelo debe (y no debe) escribir."""
    extra = ""
    zonas = _usada(usadas, "recomendar_zonas")
    if _usada(usadas, "sugerir_giros"):
        extra += REGLA_SUGERIR
    elif zonas and zonas.get("aviso_prob_baja"):
        extra += REGLA_PROB_BAJA
    if bloques(usadas, herencia):
        extra += REGLA_COMPLEMENTO
    if pregunta and H.pide_como_influye(pregunta) and (_usada(usadas, "contexto_macro") or {}).get("como_influye"):
        extra += REGLA_COMO
    ing = (_usada(usadas, "ficha_municipio") or {}).get("ingreso_linea")
    if pregunta and ing and H.pide_ingreso(pregunta):
        extra += REGLA_INGRESO.format(ingreso=_ingreso_txt(_usada(usadas, "ficha_municipio")))
    if zonas and any(z.get("aviso_ageb_poco_poblada") for z in zonas.get("zonas", [])):
        extra += REGLA_AGEB_VACIA
    if herencia:
        extra += REGLA_HERENCIA.format(que=", ".join(f"{k} = {v}" for k, v in herencia.items()))
    return SYSTEM + extra


def _ingreso_txt(ficha: dict) -> str:
    """«$110,800 por hogar al trimestre, decil típico 8» del ingreso estimado del municipio (ficha_municipio)."""
    dec = f", decil típico {ficha['decil_tipico']}" if ficha.get("decil_tipico") is not None else ""
    return f"{H._pesos_txt(ficha['ingreso_trim_mediano_est_hogar_mxn'])} por hogar al trimestre{dec}"


def _f(nombre: str, desc: str, props: dict, req: list[str]) -> dict:
    return {"type": "function", "function": {"name": nombre, "description": desc,
                                             "parameters": {"type": "object", "properties": props, "required": req}}}


S = {"type": "string"}
TOOLS = [
    _f("perfil_giro", "Identifica el giro del catalogo a partir del texto del usuario (sinonimos) y da sus supuestos: SCIAN, radio, cliente objetivo, ticket.",
       {"texto": {**S, "description": "texto libre, p. ej. 'quiero poner una neveria'"}}, ["texto"]),
    _f("recomendar_zonas", "Top de colonias (AGEB) de la ZMVM para un giro, con score 0-100, ingreso estimado, edad clave y razones en numeros. Filtros opcionales por municipio/alcaldia, por NSE estimado y por colonia (limita a esa colonia y las AGEB a 2 km).",
       {"giro": {**S, "description": "clave del giro (p. ej. heladeria)"},
        "municipio": {**S, "description": "municipio o alcaldia de la ZMVM (opcional)"},
        "nse": {**S, "enum": ["bajo", "medio", "alto"], "description": "nivel socioeconomico estimado (opcional)"},
        "colonia": {**S, "description": "colonia o asentamiento, p. ej. Polanco, la Condesa, Santa Fe (opcional)"},
        "top": {"type": "integer", "description": "cuantas colonias (1-10, default 5)"}}, ["giro"]),
    _f("ficha_zona", "Datos de una AGEB (clave de 13 caracteres) o de una colonia por nombre: poblacion, edades, NSE estimado, negocios, transporte; con giro, su score ahi.",
       {"zona": {**S, "description": "clave AGEB o nombre de colonia"},
        "municipio": {**S, "description": "municipio para desambiguar (opcional)"},
        "giro": {**S, "description": "clave del giro (opcional)"}}, ["zona"]),
    _f("buscar_carpetas", "Busca en las carpetas de informacion del proyecto: metodologia (Censo, DENUE, ENIGH, NSE), fichas por municipio, teoria de localizacion, explicacion del modelo y alcance.",
       {"pregunta": S, "k": {"type": "integer", "description": "trozos (1-8, default 4)"}}, ["pregunta"]),
    _f("contexto_macro", "Ultimos indicadores macro de Mexico: tasa objetivo de Banxico, TIIE 28, tipo de cambio FIX, remesas, inflacion INPC, confianza del consumidor y consumo privado. Con giro, solo los que le importan a ese giro.",
       {"giro": {**S, "description": "clave del giro (opcional)"}}, []),
    _f("ficha_municipio", "Trozo corto de la ficha del municipio o alcaldia: poblacion, densidad, edades, escolaridad y NSE estimado.",
       {"municipio": S}, ["municipio"]),
    _f("sugerir_giros", "Cuando el usuario no tiene giro: giros del catalogo que mejor salen en un municipio, colonia y/o NSE; con inversion='baja', los de poca inversion (aproximacion).",
       {"municipio": S, "nse": {**S, "enum": ["bajo", "medio", "alto"]}, "colonia": S,
        "inversion": {**S, "enum": ["baja"], "description": "'baja' si pide algo barato / poca inversion"},
        "ticket_max": {"type": "number", "description": "ticket promedio maximo en pesos (solo si lo pide en pesos)"},
        "top": {"type": "integer"}}, []),
]

MACRO = re.compile(r"\b(inflacion|inpc|tasa|tasas|banxico|tipo de cambio|dolar|remesas|economia|macro|tiie|consumo privado|confianza del consumidor|interes)\b")
NSE = re.compile(r"\b(?:nivel|nse|zona|clase|estrato)\s+(?:socioeconomico\s+|economico\s+|de nivel\s+)?(bajo|medio|alto|baja|media|alta)\b")
BARATO = re.compile(r"\b(barato|barata|economico|poca inversion|bajo costo|poco dinero)\b")
MARCA_SEGUIMIENTO = re.compile(r"\b(ahi|misma zona|mismo lugar|esa zona|esa colonia|y si|entonces|ahora|tambien|mejor)\b|^y\b")
NEGOCIO_GENERICO = re.compile(r"\b(negocio|algo|que pongo|que abro|que me recomiendas)\b")


def _extrae(pregunta: str) -> dict:
    """Lo que dice UNA pregunta: giro, municipios, colonia, NSE, si pide algo barato, si es macro o fuera de la ZMVM."""
    n = H.norm(pregunta)
    perfil = H.perfil_giro(pregunta)
    giro, frase = perfil.get("giro"), perfil.get("coincidencia")
    muns = rag.municipios_en(pregunta)
    fuera = rag.ciudades_fuera(pregunta)
    m = NSE.search(n)
    nse = {"baja": "bajo", "media": "medio", "alta": "alto"}.get(m.group(1), m.group(1)) if m else None
    cve = None
    if len(muns) == 1:
        r = H.resolver_municipio(muns[0])
        cve = r.get("cvegeo_mun") if r.get("ok") else None
    cols = [] if fuera else lugares.detectar(pregunta, muns, frase, cve)
    return {"n": n, "giro": giro, "perfil": perfil, "muns": muns, "mun": muns[0] if len(muns) == 1 else None, "fuera": fuera,
            "colonia": cols[0] if cols else None, "nse": nse, "barato": bool(BARATO.search(n)),
            "macro": bool(MACRO.search(n)), "generico": bool(NEGOCIO_GENERICO.search(n)),
            "pide_como": H.pide_como_influye(pregunta)}


def _heredar(cur: dict, historial: list[dict] | None) -> tuple[dict, dict]:
    """Completa lo que la pregunta actual no trae con los turnos anteriores del usuario (seguimientos).

    Regresa (valores efectivos, lo heredado). Reglas:
    - giro: se hereda si la pregunta no trae giro, no es macro ni pide un negocio en general / algo barato;
    - ubicacion (municipio, colonia): se hereda si la pregunta no trae ninguna; si trae giro nuevo, solo con una marca de
      seguimiento («y», «ahi», «misma zona»...); una colonia nueva o un municipio nuevo reemplazan a ambos;
    - NSE: se hereda si no trae uno y no cambia de ubicacion."""
    ef = {"giro": cur["giro"], "mun": cur["mun"], "colonia": cur["colonia"], "nse": cur["nse"], "barato": cur["barato"]}
    her: dict = {}
    users = [m["content"] for m in (historial or []) if m.get("role") == "user" and m.get("content")]
    if not users or cur["fuera"]:
        return ef, her
    prev = {"giro": None, "mun": None, "colonia": None, "nse": None, "barato": False}
    for u in users:
        e = _extrae(u)
        if e["giro"]:
            prev["giro"] = e["giro"]
            prev["barato"] = False
        if e["mun"] or e["colonia"]:
            prev["mun"], prev["colonia"] = e["mun"], e["colonia"]
        if e["nse"]:
            prev["nse"] = e["nse"]
        if e["barato"]:
            prev["barato"] = True
    tiene_ubic = bool(cur["mun"] or cur["colonia"] or cur["muns"])
    sigue = bool(MARCA_SEGUIMIENTO.search(cur["n"]))
    if not cur["giro"] and prev["giro"] and not cur["macro"] and not cur["barato"] and not (cur["generico"] and not sigue):
        ef["giro"] = prev["giro"]
        her["giro"] = prev["giro"]
    if not tiene_ubic and (not cur["giro"] or sigue) and (prev["mun"] or prev["colonia"]):
        ef["mun"], ef["colonia"] = prev["mun"], prev["colonia"]
        if prev["colonia"]:
            her["colonia"] = prev["colonia"]["texto"]
        if prev["mun"]:
            her["municipio"] = prev["mun"]
    if not cur["nse"] and prev["nse"] and not tiene_ubic and not cur["giro"]:
        ef["nse"] = prev["nse"]
        her["nse"] = prev["nse"]
    if not cur["giro"] and prev["barato"] and not ef["giro"] and not cur["macro"]:
        ef["barato"] = True
        her["barato"] = "poca inversion"
    return ef, her


def _planear(pregunta: str, historial: list[dict] | None = None) -> tuple[list[tuple[str, dict]], dict]:
    """(plan, heredado): herramientas obvias segun reglas simples y lo que se heredo de turnos anteriores."""
    cur = _extrae(pregunta)
    ef, her = _heredar(cur, historial)
    n, giro, nse, mun = cur["n"], ef["giro"], ef["nse"], ef["mun"]
    col = ef["colonia"]["texto"] if ef["colonia"] else None
    texto_giro = pregunta if giro == cur["giro"] else giro  # giro heredado: se pregunta por su clave
    plan: list[tuple[str, dict]] = [("perfil_giro", {"texto": texto_giro or pregunta})]
    if cur["fuera"]:
        if giro:
            plan.append(("recomendar_zonas", {"giro": giro, "municipio": cur["fuera"][0].title()}))
        plan.append(("buscar_carpetas", {"pregunta": pregunta, "k": 2}))
        return plan, her
    macro = cur["macro"] or cur["pide_como"]   # «¿cómo está la economía?», «¿es buen momento?», «¿afecta...?» piden el contexto macro
    # municipio para la ficha: el explicito, o el de la colonia si cae en uno solo
    mun_ficha = mun
    if not mun_ficha and ef["colonia"] and ef["colonia"].get("encontrada"):
        mun_ficha = ef["colonia"]["resolucion"].get("municipio") if ef["colonia"]["resolucion"].get("cvegeo_mun") else None
    if giro:
        if macro:
            plan.append(("contexto_macro", {"giro": giro}))
        plan.append(("recomendar_zonas", {"giro": giro, "municipio": mun, "nse": nse, "colonia": col}))
        if not macro:
            plan.append(("contexto_macro", {"giro": giro}))
        if mun_ficha:
            plan.append(("ficha_municipio", {"municipio": mun_ficha}))
    else:
        if macro:
            plan.append(("contexto_macro", {}))
        if mun or col or nse or ef["barato"] or ("negocio" in n and not macro):
            args = {"municipio": mun, "nse": nse, "colonia": col, "inversion": "baja" if ef["barato"] else None}
            plan.append(("sugerir_giros", args))
            sg = H.sugerir_giros(**{k: v for k, v in args.items() if v})
            if sg.get("encontrado"):
                plan.append(("recomendar_zonas", {"giro": sg["giros"][0]["giro"], "municipio": mun, "nse": nse, "colonia": col}))
            if mun_ficha:
                plan.append(("ficha_municipio", {"municipio": mun_ficha}))
    return [(k, {a: b for a, b in v.items() if b not in (None, "")}) for k, v in plan], her


def pre_consulta(pregunta: str, historial: list[dict] | None = None) -> list[tuple[str, dict]]:
    """Herramientas obvias segun reglas simples; regresa [(nombre, argumentos)].

    historial: turnos anteriores [{role, content}] (como los guarda la UI). Si la pregunta no trae giro, municipio,
    colonia o NSE, se heredan de los mensajes del usuario (p. ej. «¿y en Coyoacan?» despues de «heladeria»).
    Una pregunta fuera de tema («¿cómo me llamo?», «hola», deportes) no llama ninguna herramienta: regresa []."""
    if fuera.tipo_fuera_de_tema(pregunta, historial):
        return []
    return _planear(pregunta, historial)[0]


def fuera_de_tema(pregunta: str, historial: list[dict] | None = None) -> dict | None:
    """{tipo: saludo|nombre|ajeno, subtipo, texto} si la pregunta no es de negocios (texto fijo, sin LLM); None si si lo es."""
    return fuera.respuesta(pregunta, historial)


# ---------------------------------------------------------------- vista compacta para el LLM
def para_llm(nombre: str, r, con_mecanismo: bool = False, con_ingreso: bool = False) -> dict:
    """Lo que de verdad necesita el modelo de cada resultado (menos tokens = menos latencia). El resultado
    completo se queda en `herramientas` para la UI, el tablero y el evaluador."""
    if not isinstance(r, dict):
        return r
    if nombre == "perfil_giro" and r.get("encontrado"):
        keep = ("encontrado", "giro", "coincidencia", "cliente_objetivo_edades", "nse_objetivo", "ticket_promedio_mxn",
                "ticket_fuente", "radio_influencia_m", "aviso_rubro", "aviso_rubro_amplio", "aviso_modelo", "validacion_modelo", "fuentes")
        return {k: r[k] for k in keep if k in r}
    if nombre == "recomendar_zonas" and r.get("encontrado"):
        out = {k: r[k] for k in ("giro", "filtros", "aviso_colonia", "aviso_prob_baja", "aviso_rubro_amplio", "edad_clave", "destacados") if r.get(k)}
        zonas = []
        for z in r["zonas"]:
            zz = {"colonia": z["colonia"], "municipio": z["municipio"], "ageb": z["ageb"], "score": z["score"], "datos": z["resumen_texto"]}
            if z.get("aviso_ageb_poco_poblada"):
                zz["aviso"] = z["aviso_ageb_poco_poblada"]
            if "dist_a_colonia_km" in z:
                zz["dist_a_colonia_km"], zz["en_colonia_consultada"] = z["dist_a_colonia_km"], z["en_colonia_consultada"]
            zonas.append(zz)
        out["zonas"] = zonas
        out["como_leer_score"] = r["como_leer_score"]
        out["fuentes"] = r.get("fuentes", [])
        return out
    if nombre == "contexto_macro" and r.get("linea"):
        extra = {"como_influye": r["como_influye"]} if con_mecanismo and r.get("como_influye") else {}
        return {"giro": r["giro"], "linea": r["linea"], **extra, "fuentes": r.get("fuentes", [])}
    if nombre == "ficha_municipio" and r.get("encontrado"):
        extra = {"ingreso_municipio": r["ingreso_linea"], "ingreso_trim_mediano_est_hogar_mxn": r["ingreso_trim_mediano_est_hogar_mxn"]} \
            if con_ingreso and r.get("ingreso_linea") else {}
        return {"municipio": r["municipio"], "ficha": r["ficha"], **extra, "fuentes": r.get("fuentes", [])}
    if nombre == "sugerir_giros" and r.get("encontrado"):
        return {k: v for k, v in r.items() if k not in ("metodo",)}
    return r


def _cliente():
    import ollama
    return ollama.Client(host=HOST, timeout=240)


def _tool_calls(msg) -> list[tuple[str, dict]]:
    out = []
    for tc in (getattr(msg, "tool_calls", None) or []):
        args = tc.function.arguments
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        out.append((tc.function.name, dict(args or {})))
    return out


def _limpia(texto: str) -> str:
    """Quita bloques <think> si el modelo los deja."""
    return re.sub(r"<think>.*?</think>", "", texto or "", flags=re.S).strip()


def _historial_corto(historial: list[dict] | None) -> list[dict]:
    """Turnos anteriores para el prompt: las respuestas largas del asistente se recortan (menos tokens)."""
    out = []
    for m in historial or []:
        c = m.get("content") or ""
        if m.get("role") == "assistant" and len(c) > HISTORIAL_MAX_CHARS:
            c = c[:HISTORIAL_MAX_CHARS].rsplit(" ", 1)[0] + " […]"
        out.append({"role": m.get("role", "user"), "content": c})
    return out


# ---------------------------------------------------------------- bloques de datos (los arma el codigo, no el modelo)
def _renglon_zona(i: int, z: dict, r: dict) -> str:
    cerca = ""
    if "dist_a_colonia_km" in z:
        col = (r.get("filtros") or {}).get("colonia", "la colonia pedida")
        cerca = f" Dentro de {col}." if z["en_colonia_consultada"] else f" A {z['dist_a_colonia_km']} km de {col}."
    aviso = f" **Ojo:** {z['aviso_ageb_poco_poblada']}." if z.get("aviso_ageb_poco_poblada") else ""
    return (f"{i}. **{z['colonia']}**, {z['municipio']} (AGEB {z['ageb']}): score {z['score']}/100. "
            f"{z['resumen_texto']}.{cerca}{aviso}")


_ACENTOS_SINONIMO = {"miscelanea": "miscelánea", "cafe": "café", "ingles": "inglés", "clinica": "clínica", "mecanico": "mecánico",
                     "medico": "médico", "japones": "japonés", "economica": "económica", "fisico": "físico", "garrafon": "garrafón",
                     "lena": "leña", "unas": "uñas", "estetica": "estética", "optica": "óptica", "reparacion": "reparación",
                     "automotriz": "automotriz", "ortodoncia": "ortodoncia", "odontologo": "odontólogo", "ciclovia": "ciclovía"}


def _acentuar(texto: str) -> str:
    """Acentos de un sinónimo del catálogo (vienen sin acentos): «nevería», «tintorería», «café»."""
    t = re.sub(r"(\w)eria\b", r"\1ería", texto)
    return " ".join(_ACENTOS_SINONIMO.get(w, w) for w in t.split())


def sinonimo_usado(usadas: list[dict], clave: str) -> str | None:
    """La palabra de la pregunta que se resolvio al giro `clave` con otro nombre («nevería» → heladería), con acentos; None si
    la persona uso el nombre del giro (o una palabra que es parte de el)."""
    nombre = H.nombre_giro(clave)
    for u in usadas:
        r = u["resultado"]
        if u["nombre"] == "perfil_giro" and isinstance(r, dict) and r.get("giro") == clave and r.get("coincidencia"):
            c = H._singular(H.norm(r["coincidencia"]))
            propios = {H._singular(H.norm(x)) for x in (nombre, clave.replace("_", " "))}
            if c and len(c.split()) <= 3 and not any(c in x or x in c for x in propios):
                return _acentuar(str(r["coincidencia"]))
    return None


def giro_visible(usadas: list[dict], clave: str) -> str:
    """Nombre del giro para encabezados: «heladería (nevería)» si la persona pidió por un sinónimo."""
    nombre = H.nombre_giro(clave)
    sin = sinonimo_usado(usadas, clave)
    return f"{nombre} ({sin})" if sin else nombre


def _nota_sinonimo(usadas: list[dict]) -> str | None:
    """Una linea que dice con que giro del catalogo se quedo la respuesta cuando la pregunta uso otro nombre
    («Tomé «nevería» como heladería, el giro más cercano del catálogo»)."""
    for u in usadas:
        r = u["resultado"]
        if u["nombre"] == "recomendar_zonas" and isinstance(r, dict) and r.get("encontrado") and r.get("giro"):
            sin = sinonimo_usado(usadas, r["giro"])
            if sin:
                return f"Tomé «{sin}» como {H.nombre_giro(r['giro'])}, el giro más cercano del catálogo."
    return None


def _frase_edad(edad: dict) -> str:
    """«en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020)»: la referencia de la edad clave del giro."""
    et = str(edad["etiqueta"])
    tiene = et if et.startswith("60") else f"de {et}"
    return f"Referencia: en la ZMVM, {edad['pct_zmvm']} % de la población tiene {tiene} (Censo 2020)."


def _bloque_zonas(r: dict, giro_txt: str | None = None) -> list[str]:
    """Encabezado (score relativo al giro), la referencia de edad en su propia linea y el top de zonas."""
    edad = r.get("edad_clave")
    out = [f"**Top {len(r['zonas'])} para {giro_txt or H.nombre_giro(r['giro'])}** (score 0-100 relativo al giro)"]
    if edad and edad.get("pct_zmvm") is not None:
        out.append("")
        out.append(_frase_edad(edad))
        out.append("")
    out += [_renglon_zona(i, z, r) for i, z in enumerate(r["zonas"], 1)]
    if r.get("aviso_prob_baja"):
        out += ["", f"**Ojo:** {r['aviso_prob_baja']}."]    # linea en blanco: si no, Markdown lo funde con el ultimo renglon
    return ["\n".join(out)]


def _bloque_giros(r: dict) -> list[str]:
    out = ["**Giros que conviene considerar** (en orden de viabilidad = prob. de apertura × prob. de seguir abierto; "
           "el score de las colonias es relativo dentro de cada giro y no compara giros)"]
    for i, g in enumerate(r["giros"], 1):
        aviso = f" ({g['aviso']})" if g.get("aviso") else ""
        out.append(f"{i}. {H.nombre_giro(g['giro'])}: viabilidad {g['viabilidad_pct']} %, prob. de apertura {g['prob_apertura_pct']} %, "
                   f"prob. de seguir abierto {g['prob_sigue_abierto_pct']} %.{aviso}")
    if r.get("criterio_inversion"):
        out.append(f"**Nota sobre «barato»:** {r['criterio_inversion']}.")
    return ["\n".join(out)]


ORDEN_MACRO = ["tasa_objetivo", "tiie_28", "tipo_cambio_fix", "inpc_general_var_anual", "inpc_alimentos_var_anual",
               "remesas", "confianza_consumidor", "consumo_privado"]


def _bloque_macro(r: dict, con_mecanismo: bool = False) -> list[str]:
    """Contexto macro; con `con_mecanismo` (la pregunta pide «cómo influye») agrega una frase fija por indicador."""
    mec = r.get("como_influye") or {}
    mec_txt = ("**Cómo influye en el negocio:**\n" + "\n".join(f"- {t}" for t in mec.values())) if con_mecanismo and mec else ""
    if r.get("linea"):
        return [f"**Contexto económico:** {r['linea']}"] + ([mec_txt] if mec_txt else [])
    ind = r.get("indicadores", {})
    filas = [f"- {H._txt_indicador(k, ind[k])}" for k in ORDEN_MACRO if k in ind]
    return (["**Indicadores (valores nacionales):**\n" + "\n".join(filas)] + ([mec_txt] if mec_txt else [])) if filas else []


def _prioridad_aviso(a: str, r: dict) -> int:
    """0 = lo que dice que el modelo o el gasto no son confiables (probabilidad baja, giro raro, rubro ENIGH sustituto o
    sin rubro); 1 = que el gasto usa un rubro amplio (ordena zonas, no compara giros); 2 = el resto de los avisos."""
    if a == r.get("aviso_prob_baja") or a.startswith(("giro raro", "sin rubro ENIGH")) or a == r.get("rubro_enigh_nota"):
        return 0
    return 1 if a == r.get("aviso_rubro_amplio") else 2


def riesgos(usadas: list[dict]) -> list[str]:
    """Riesgos de la respuesta, armados con los avisos de las herramientas (sin LLM): hasta 5 viñetas. Los avisos que dicen
    que el modelo o el gasto del giro no son confiables van primero (si no, el corte los dejaba fuera)."""
    out: list[str] = []
    for u in usadas:
        r = u["resultado"]
        if u["nombre"] == "recomendar_zonas" and isinstance(r, dict) and r.get("encontrado"):
            avisos = [a for a in r.get("avisos", []) if not a.startswith(("Filtro por colonia", "NO ENCONTRADO"))]
            rubro = (H.motor.giros().get(r.get("giro"), {}) or {}).get("rubro_enigh_nota")
            if r.get("aviso_prob_baja") and r["aviso_prob_baja"] not in avisos:
                avisos.insert(0, r["aviso_prob_baja"])
            ctx = {"aviso_prob_baja": r.get("aviso_prob_baja"), "rubro_enigh_nota": rubro, "aviso_rubro_amplio": r.get("aviso_rubro_amplio")}
            avisos = sorted(avisos, key=lambda a: _prioridad_aviso(a, ctx))   # estable: conserva el orden dentro de cada grupo
            out += [a[0].upper() + a[1:] for a in avisos]
            break
    for u in usadas:
        r = u["resultado"]
        if u["nombre"] == "sugerir_giros" and isinstance(r, dict) and r.get("encontrado"):
            auc = re.search(r"AUC ([\d.]+)", r.get("metodo", ""))
            out.append("La probabilidad de seguir abierto viene de un modelo débil" + (f" (AUC {auc.group(1)})" if auc else "")
                       + ": mide rotación, no rentabilidad.")
            break
    return list(dict.fromkeys(out))[:5]


def _con_punto(x: str) -> str:
    """Todos los puntos de «Riesgos» terminan con punto final."""
    x = x.rstrip()
    return x if x.endswith((".", "!", "?")) else x + "."


def _bloque_riesgos(usadas: list[dict]) -> list[str]:
    """«Riesgos»: los de `riesgos()`, sin el aviso de probabilidad baja que ya sale como «Ojo» bajo la lista de zonas."""
    ojos = {r["aviso_prob_baja"][0].upper() + r["aviso_prob_baja"][1:] for u in usadas for r in [u["resultado"]]
            if u["nombre"] == "recomendar_zonas" and isinstance(r, dict) and r.get("encontrado") and r.get("zonas")
            and r.get("aviso_prob_baja")}
    rs = [x for x in riesgos(usadas) if x not in ojos]
    return ["**Riesgos:**\n" + "\n".join(f"- {_con_punto(x)}" for x in rs)] if rs else []


def _txt_herencia(her: dict) -> str:
    partes = []
    if her.get("giro"):
        partes.append(H.nombre_giro(her["giro"]))
    if her.get("colonia"):
        partes.append(f"la colonia {her['colonia']}")
    if her.get("municipio"):
        partes.append(f"{her['municipio']}")
    if her.get("nse"):
        partes.append(f"zona de nivel {her['nse']}")
    if her.get("barato"):
        partes.append("poca inversión")
    return "Sigo con " + ", ".join(partes) + " (de tu pregunta anterior)."


PIDE_PORCENTAJE = re.compile(r"\bporcentaje\b|\bproporcion\b|\bque tanto\b|\bcuanta gente\b|\bcuantos\b|\bcuantas\b|\bque parte\b")
EDAD_EN_FICHA = {"0-14": r"0-14 años ([\d.]+) %", "15-24": r"15-24 ([\d.]+) %", "25-59": r"25-59 ([\d.]+) %", "60+": r"60 o más ([\d.]+) %"}
EDAD_TEXTO = {"0-14": "de 0 a 14 años", "15-24": "de 15 a 24 años", "25-59": "de 25 a 59 años", "60+": "de 60 años o más"}


def _edad_del_municipio(ficha: dict, pregunta: str) -> str | None:
    """Si la pregunta pide el porcentaje de un grupo de edad («¿qué porcentaje de la gente es menor de 14 años?»), la frase con
    la cifra del municipio (de la línea «Edad» de ficha_municipio); None si no lo pide o la ficha no trae el dato."""
    q = lectura_mod.ligera(pregunta or "")
    grupo = lectura_mod.grupo_de_edad(q)
    if not grupo or not PIDE_PORCENTAJE.search(q):
        return None
    linea = next((x for x in ficha.get("ficha", []) if x.startswith("Edad:")), "")
    m = re.search(EDAD_EN_FICHA[grupo], linea)
    if not m:
        return None
    return f"En {ficha['municipio']}, {m.group(1)} % de la población tiene {EDAD_TEXTO[grupo]} (Censo 2020)."


def bloques(usadas: list[dict], herencia: dict | None = None, pregunta: str = "") -> list[str]:
    """Secciones de datos de la respuesta, armadas con lo que regresaron las herramientas (sin LLM)."""
    out: list[str] = []
    aviso = _aviso_colonia(usadas)
    if aviso:
        out.append(f"> {aviso}")
    if herencia:
        out.append(_txt_herencia(herencia))
    sin = _nota_sinonimo(usadas)
    if sin:
        out.append(sin)
    ficha_ing = next((u["resultado"] for u in usadas if u["nombre"] == "ficha_municipio" and isinstance(u["resultado"], dict)
                      and u["resultado"].get("ingreso_linea")), None)
    directo = bool(ficha_ing and H.pide_ingreso(pregunta))
    fm = next((u["resultado"] for u in usadas if u["nombre"] == "ficha_municipio" and isinstance(u["resultado"], dict)
               and u["resultado"].get("encontrado") and u["resultado"].get("ficha")), None)
    edad_mun = _edad_del_municipio(fm, pregunta) if fm else None
    if directo:   # «¿cuánto ganan ahí?»: la respuesta directa va antes de las zonas
        out.append(f"**Ingreso en {ficha_ing['municipio']}:** el ingreso trimestral mediano estimado por hogar es de "
                   f"{H._pesos_txt(ficha_ing['ingreso_trim_mediano_est_hogar_mxn'])}"
                   + (f" (decil típico {ficha_ing['decil_tipico']})" if ficha_ing.get("decil_tipico") is not None else "")
                   + f"; {H.F_INGRESO_MUN.split(' (')[0]}." + (f" {edad_mun}" if edad_mun else ""))
    elif edad_mun:   # «¿qué porcentaje de la gente es menor de 14 años?» sin pedir ingreso
        out.append(f"**Edad en {fm['municipio']}:** {edad_mun}")
    vistos = set()
    for nombre, fn in (("sugerir_giros", _bloque_giros), ("recomendar_zonas", _bloque_zonas),
                       ("contexto_macro", _bloque_macro), ("ficha_municipio", None)):
        for u in usadas:
            r = u["resultado"]
            if u["nombre"] != nombre or not isinstance(r, dict):
                continue
            clave = (nombre, json.dumps(u.get("args", {}), sort_keys=True, ensure_ascii=False))
            if clave in vistos:
                continue
            vistos.add(clave)
            if nombre == "ficha_municipio":
                if r.get("encontrado") and r.get("ficha"):
                    ing = f" {r['ingreso_linea']}" if r.get("ingreso_linea") and not directo else ""   # directo: ya salio arriba
                    out.append(f"**Sobre {r['municipio']}:** " + " ".join(r["ficha"][:3]) + ing)
            elif nombre == "recomendar_zonas":
                if r.get("encontrado") and r.get("zonas"):
                    out += fn(r, giro_visible(usadas, r["giro"]))
            elif nombre == "sugerir_giros":
                if r.get("encontrado") and r.get("giros"):
                    out += fn(r)
            elif r.get("linea") or r.get("indicadores"):
                out += fn(r, H.pide_como_influye(pregunta))
    # solo hay "bloques" si hay datos que mostrar (no solo el aviso o la herencia)
    return out if any(b.startswith("**") for b in out) else []


def responder(pregunta: str, historial: list[dict] | None = None, modelo: str = MODELO,
              pre: bool = True, max_rondas: int = MAX_RONDAS) -> dict:
    """Respuesta del agente. Regresa {respuesta, herramientas:[{nombre, args, resultado}], latencia_s, rondas, modo,
    herencia (lo que se mantuvo de turnos anteriores), cortada (el modelo llego al tope de texto),
    metricas (tokens y segundos de Ollama: prompt, generacion y carga del modelo)}."""
    t0 = time.time()
    ft = fuera_de_tema(pregunta, historial)
    if ft:      # sin herramientas y sin LLM: texto fijo
        return {"respuesta": ft["texto"], "herramientas": [], "latencia_s": round(time.time() - t0, 1), "rondas": 0,
                "modo": "fuera_de_tema", "modelo": None, "herencia": None, "cortada": False, "texto_modelo": "", "lectura_quitada": [],
                "fuera_de_tema": True, "tipo_fuera_de_tema": ft["tipo"],
                "metricas": {"tokens_prompt": 0, "tokens_generados": 0, "s_prompt": 0.0, "s_generacion": 0.0, "s_carga": 0.0}}
    msgs = [{"role": "system", "content": SYSTEM}] + _historial_corto(historial) + [{"role": "user", "content": pregunta}]
    usadas: list[dict] = []
    herencia: dict = {}
    pide_como, pide_ing = H.pide_como_influye(pregunta), H.pide_ingreso(pregunta)

    def correr(nombre, args):
        res = H.ejecutar(nombre, args)
        usadas.append({"nombre": nombre, "args": args, "resultado": res})
        return {"role": "tool", "content": H.a_json(para_llm(nombre, res, pide_como, pide_ing)), "tool_name": nombre}

    if pre:
        plan, herencia = _planear(pregunta, historial)
        msgs.append({"role": "assistant", "content": "",
                     "tool_calls": [{"function": {"name": k, "arguments": a}} for k, a in plan]})
        msgs += [correr(k, a) for k, a in plan]
        msgs[0] = {"role": "system", "content": system_para(usadas, herencia, pregunta)}

    rondas, modo, texto, cortada, texto_modelo, lectura_quitada = 0, "llm", "", False, "", []
    metricas = {"tokens_prompt": 0, "tokens_generados": 0, "s_prompt": 0.0, "s_generacion": 0.0, "s_carga": 0.0}
    try:
        cli = _cliente()
        while True:
            rondas += 1
            ultima = rondas >= max_rondas
            r = cli.chat(model=modelo, messages=msgs, tools=None if ultima else TOOLS, think=False,
                         options=OPCIONES, keep_alive="15m")
            for k, v in (("tokens_prompt", r.prompt_eval_count), ("tokens_generados", r.eval_count),
                         ("s_prompt", (r.prompt_eval_duration or 0) / 1e9), ("s_generacion", (r.eval_duration or 0) / 1e9),
                         ("s_carga", (r.load_duration or 0) / 1e9)):
                metricas[k] += v or 0
            llamadas = _tool_calls(r.message)
            if llamadas and not ultima:
                msgs.append({"role": "assistant", "content": r.message.content or "",
                             "tool_calls": [{"function": {"name": k, "arguments": a}} for k, a in llamadas]})
                msgs += [correr(k, a) for k, a in llamadas]
                msgs[0] = {"role": "system", "content": system_para(usadas, herencia, pregunta)}
                continue
            texto = _limpia(r.message.content)
            cortada = getattr(r, "done_reason", None) == "length"
            if texto or ultima:
                break
        texto_modelo = texto
        texto, lectura_quitada = cerrar_con_revision(texto, usadas, cortada, herencia, pregunta)
    except Exception as e:  # Ollama apagado o sin el modelo
        modo = "plantilla"
        texto = (f"_(Ollama no respondio: {type(e).__name__}. Respuesta armada sin LLM; "
                 f"corre `ollama serve` y `ollama pull {modelo}`.)_\n\n") + plantilla(usadas, herencia, pregunta)
    return {"respuesta": texto, "herramientas": usadas, "latencia_s": round(time.time() - t0, 1),
            "rondas": rondas, "modo": modo, "modelo": modelo, "herencia": herencia or None, "cortada": cortada,
            "texto_modelo": texto_modelo, "lectura_quitada": lectura_quitada, "metricas": {k: round(v, 1) for k, v in metricas.items()}}


# ---------------------------------------------------------------- cierre deterministico
PCT_ANTES = re.compile(r"(prob\.?\s+de\s+apertura|prob\.?\s+de\s+seguir\s+abierto|probabilidad\s+de\s+apertura|"
                       r"probabilidad\s+de\s+seguir\s+abierto|captura(?:\s+huff)?|viabilidad)\s*%\s*(\d+(?:\.\d+)?)", re.I)
SECCION_FUENTES = re.compile(r"\n+[*#_ ]*Fuentes?[*#_ ]*:?.*\Z", re.I | re.S)


BIE_ID = re.compile(r"^(.*?) \(BIE, id (\d+)\)$")


def unir_fuentes(fu: list[str]) -> list[str]:
    """Sin repetir y en orden de aparicion. Una fuente que sale una vez sin detalle y otra con el detalle (id de serie) queda una
    sola vez: «INEGI, Banco de Indicadores API» + «... (BIE, id 910406)» + «... (BIE, id 910408)» ->
    «INEGI, Banco de Indicadores API (BIE, ids 910406 y 910408)»."""
    fu = list(dict.fromkeys(f for f in fu if isinstance(f, str)))
    ids: dict[str, list[str]] = {}
    for f in fu:
        m = BIE_ID.match(f)
        if m:
            ids.setdefault(m.group(1), []).append(m.group(2))
    out: list[str] = []
    for f in fu:
        m = BIE_ID.match(f)
        if m:
            if m.group(1) in {x.split(" (BIE", 1)[0] for x in out if "(BIE" in x}:
                continue
            lista = ids[m.group(1)]
            etiqueta = f"id {lista[0]}" if len(lista) == 1 else "ids " + ", ".join(lista[:-1]) + f" y {lista[-1]}"
            out.append(f"{m.group(1)} (BIE, {etiqueta})")
        elif any(g.startswith(f + " (") for g in fu if g != f):
            continue            # la misma fuente ya sale con detalle
        else:
            out.append(f)
    return out


def fuentes_de(usadas: list[dict]) -> list[str]:
    """Fuentes que regresaron las herramientas, sin repetir y en el orden en que aparecieron (ver `unir_fuentes`)."""
    fu: list[str] = []
    for u in usadas:
        r = u["resultado"]
        if isinstance(r, dict):
            fu += [f for f in r.get("fuentes", []) if isinstance(f, str)]
    return unir_fuentes(fu)


def _aviso_colonia(usadas: list[dict]) -> str | None:
    for u in usadas:
        r = u["resultado"]
        if isinstance(r, dict) and r.get("aviso_colonia"):
            return r["aviso_colonia"]
    return None


LECTURA = re.compile(r"\*\*Lectura:?\*\*:?\s*(.*?)(?=\n\s*\*\*(?:Riesgos|Fuentes|Top|Giros|Contexto|Sobre|Indicadores)|\Z)", re.S)


def _lectura(t: str) -> str | None:
    """La seccion «Lectura» que escribio el modelo (o su texto si es corto y no trae encabezados)."""
    m = LECTURA.search(t)
    if m and m.group(1).strip():
        return "**Lectura:** " + m.group(1).strip()
    t = re.sub(r"(?s)\*\*(?:Riesgos|Fuentes).*", "", t).strip()
    return "**Lectura:** " + t if t and len(t) <= 700 and "AGEB" not in t else None


def cerrar(texto: str, usadas: list[dict], cortada: bool = False, herencia: dict | None = None, pregunta: str = "") -> str:
    """Arma la respuesta final (ver `cerrar_con_revision`); solo el texto."""
    return cerrar_con_revision(texto, usadas, cortada, herencia, pregunta)[0]


def _sin_ingreso_repetido(lect: str | None, usadas: list[dict], pregunta: str) -> str | None:
    """Si la respuesta ya abre con «Ingreso en X: $110,800...» (la pregunta pide el ingreso), la lectura no vuelve a decir ese
    ingreso del municipio: se quitan sus frases con esa cifra."""
    ficha = _usada(usadas, "ficha_municipio")
    if not (lect and ficha and ficha.get("ingreso_linea") and H.pide_ingreso(pregunta)):
        return lect
    pesos = H._pesos_txt(ficha["ingreso_trim_mediano_est_hogar_mxn"])
    cuerpo = re.sub(r"^\*\*Lectura:?\*\*:?\s*", "", lect)
    quedan = [f for f in lectura_mod.frases(cuerpo) if pesos not in f]
    return ("**Lectura:** " + " ".join(quedan)) if quedan else None


def _con_edad_de_ninos(lect: str | None, usadas: list[dict], pregunta: str) -> str | None:
    """Pregunta de niños, infantil o familias con hijos y el top compara la edad de 0 a 14 años: la lectura nombra la zona con el
    mayor porcentaje, con su cifra (la arma el codigo desde los renglones, no el modelo). Si la lectura ya la nombra, no se repite."""
    frase = lectura_mod.frase_edad_ninos(usadas, pregunta)
    if not frase:
        return lect
    cuerpo = re.sub(r"^\*\*Lectura:?\*\*:?\s*", "", lect or "")
    if frase.rstrip(".") in cuerpo:
        return lect
    return "**Lectura:** " + (cuerpo + " " if cuerpo else "") + frase


# Palabras que el LLM a veces escribe sin acento («nivel socioeconomico»); sin acento no son correctas en estas respuestas.
# No se tocan las palabras en MAYUSCULAS: suelen ser nombres copiados de los datos.
_ACENTOS_LLM = {
    "socioeconomico": "socioeconómico", "socioeconomica": "socioeconómica",
    "socioeconomicos": "socioeconómicos", "socioeconomicas": "socioeconómicas",
    "economico": "económico", "economica": "económica", "economicos": "económicos", "economicas": "económicas",
    "demografico": "demográfico", "demografica": "demográfica", "demograficos": "demográficos",
    "demograficas": "demográficas", "estadistico": "estadístico", "estadistica": "estadística",
    "poblacion": "población", "informacion": "información", "ubicacion": "ubicación", "inflacion": "inflación",
    "metodologia": "metodología", "analisis": "análisis", "tambien": "también", "ademas": "además",
    "segun": "según", "dificil": "difícil", "facil": "fácil", "trafico": "tráfico", "credito": "crédito",
}
_RE_ACENTOS_LLM = re.compile(r"\b(" + "|".join(sorted(_ACENTOS_LLM, key=len, reverse=True)) + r")\b", re.IGNORECASE)


def acentuar_comunes(texto: str) -> str:
    """Pone el acento a las palabras de `_ACENTOS_LLM` que el modelo escribió sin él; respeta la mayúscula inicial."""
    def cambio(m: re.Match) -> str:
        w = m.group(0)
        if w.isupper():
            return w
        bueno = _ACENTOS_LLM[w.lower()]
        return bueno[0].upper() + bueno[1:] if w[0].isupper() else bueno
    return _RE_ACENTOS_LLM.sub(cambio, texto)


def cerrar_con_revision(texto: str, usadas: list[dict], cortada: bool = False,
                        herencia: dict | None = None, pregunta: str = "") -> tuple[str, list[str]]:
    """Arma la respuesta final: avisos, lectura del modelo, bloques de datos, riesgos y fuentes completas.

    Con datos que mostrar el modelo solo escribe la lectura; todo lo demas lo arma el codigo con lo que regresaron las
    herramientas (cifras de cada zona, orden de los giros, riesgos, fuentes). Retoques: formato de cifras («63 %»),
    «FIX» y el renglon a medias si el modelo se quedo sin texto (num_predict)."""
    t = acentuar_comunes((texto or "").strip())
    interno = fuera.menciona_funciones(t)
    if interno:     # red de seguridad: el modelo no nombra funciones internas ni escribe llamadas tipo f(x=...)
        t = fuera.sin_funciones_internas(t, reemplazo="").strip()
    if cortada and "\n" in t:  # no dejar una frase a medias
        t = t.rsplit("\n", 1)[0].rstrip()
    t = SECCION_FUENTES.sub("", t).rstrip()
    b = bloques(usadas, herencia, pregunta)
    if b:
        avisos = [x for x in b if x.startswith(("> ", "Sigo con", "Tomé «"))]
        datos = [x for x in b if x not in avisos]
        lect, quitadas = lectura_mod.depurar(_lectura(t), usadas, pregunta)
        lect = _sin_ingreso_repetido(lect, usadas, pregunta)
        lect = _con_edad_de_ninos(lect, usadas, pregunta)
        partes = avisos + ([lect] if lect else []) + datos + _bloque_riesgos(usadas)
    else:
        quitadas = []
        if interno and not t:       # no quedo nada util: texto fijo de tema ajeno (sin fuentes de herramientas que no aportaron)
            return fuera.TEXTO_AJENO, []
        aviso = _aviso_colonia(usadas)
        if aviso and ("no encontrado" if aviso.startswith("NO ENCONTRADO") else "filtro por colonia") not in H.norm(t[:500]):
            t = f"> {aviso}\n\n{t}"
        partes = [t]
    out = "\n\n".join(x for x in partes if x)
    out = PCT_ANTES.sub(lambda m: f"{m.group(1)} {m.group(2)} %", out)
    out = re.sub(r"(\d)%", r"\1 %", out)
    out = re.sub(r"tipo de cambio fijo", "tipo de cambio FIX", out, flags=re.I)
    fu = fuentes_de(usadas)
    if fu:
        out += "\n\n**Fuentes:** " + "; ".join(fu) + "."
    return out, quitadas


def plantilla(usadas: list[dict], herencia: dict | None = None, pregunta: str = "", historial: list[dict] | None = None) -> str:
    """Respuesta sin LLM con los resultados de las herramientas (respaldo): los mismos bloques de datos y los riesgos.
    `pregunta` (opcional) activa las frases de «cómo influye» del contexto macro. Sin herramientas y con una pregunta fuera de
    tema («¿cómo me llamo?», «hola»), regresa el texto fijo de fuera de tema."""
    if not usadas and pregunta:
        ft = fuera_de_tema(pregunta, historial)
        if ft:
            return ft["texto"]
    partes = bloques(usadas, herencia, pregunta)
    if not partes:
        aviso = _aviso_colonia(usadas)
        partes = [f"> {aviso}"] if aviso else []
        for u in usadas:
            r = u["resultado"]
            if u["nombre"] == "recomendar_zonas" and isinstance(r, dict) and not r.get("encontrado"):
                partes.append(r.get("motivo", "NO ENCONTRADO"))
    partes += _bloque_riesgos(usadas)
    fu = fuentes_de(usadas)
    return "\n\n".join(partes) + ("\n\n**Fuentes:** " + "; ".join(fu) + "." if fu else "")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "quiero poner una heladeria"
    out = responder(q)
    print(out["respuesta"])
    print(f"\n[{out['modo']}, {out['rondas']} rondas, {out['latencia_s']} s, herramientas: "
          + ", ".join(u["nombre"] for u in out["herramientas"]) + "]")
