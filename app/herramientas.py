"""Herramientas del agente (Python puro, se prueban sin LLM).

Cada funcion regresa un dict listo para json.dumps, con cifras ya redondeadas y un campo `fuentes`.
Lo que no esta en los datos sale como "NO ENCONTRADO". El agente (app/agente.py) solo puede citar
numeros que vengan de aqui.

    perfil_giro(texto)                                  -> giro de config/giros.yaml (o propuestas SCIAN)
    recomendar_zonas(giro, municipio, nse, top, una_por_colonia, colonia, radio_km)
                                                        -> top de colonias (AGEB) con score y razones; con
                                                           `colonia`, solo esa colonia y las AGEB a <= radio_km
    ficha_zona(zona, municipio, giro)                   -> datos de una AGEB o de una colonia
    buscar_carpetas(pregunta, k)                        -> trozos de carpetas/ (RAG)
    contexto_macro(giro)                                -> macro.json resumido (con giro: lo que le importa a ese giro)
    sugerir_giros(municipio, nse, ticket_max, top, colonia, radio_km, inversion)
                                                        -> extra: giros que mejor salen en una zona
    ficha_municipio(municipio)                          -> extra: trozo corto de la ficha del municipio (carpetas/)
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from app import lugares, motor, rag

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
NO = "NO ENCONTRADO"

# fuentes cortas (las URL completas y sha256 estan en data/FUENTES.md)
F_CENSO = "INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana"
F_MARCO = "INEGI, Marco Geoestadístico 2020 (polígonos de AGEB)"
F_DENUE = "INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)"
F_ENIGH = "INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)"
F_CONAPO = "CONAPO, Índice de marginación urbana 2020"
F_MODELO = "Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)"
F_GIROS = "config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)"
F_SCIAN = "INEGI, SCIAN 2023 (data/processed/scian.csv)"
F_ZMVM = "SEDATU-CONAPO-INEGI, delimitación de zonas metropolitanas 2015 (data/processed/zmvm_municipios.csv)"
F_TRANSP = "datos.cdmx.gob.mx (Metro, Metrobus, STE, GTFS) y OpenStreetMap para Mexibus/Mexicable (data/FUENTES.md)"


# ---------------------------------------------------------------- utilidades
def norm(s) -> str:
    """minusculas, sin acentos ni signos."""
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s.lower())).strip()


def _r(x, nd=0):
    """Redondea y regresa None si no es finito (json no acepta NaN)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(v):
        return None
    v = round(v, nd)
    return int(v) if nd <= 0 else v


def _txt(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) or pd.isna(x) else str(x)


def a_json(d: dict) -> str:
    """JSON compacto (lo que se le pasa al LLM)."""
    return json.dumps(d, ensure_ascii=False, separators=(",", ":"))


@lru_cache(maxsize=1)
def municipios() -> pd.DataFrame:
    return pd.read_csv(PROC / "zmvm_municipios.csv", dtype=str)


def resolver_municipio(texto: str | None) -> dict:
    """Nombre o clave -> {ok, cvegeo_mun, nom_mun} | {ok: False, motivo, sugerencias}."""
    if not texto:
        return {"ok": True, "cvegeo_mun": None, "nom_mun": None}
    mun = municipios()
    t = str(texto).strip()
    if re.fullmatch(r"\d{5}", t) and t in set(mun["cvegeo_mun"]):
        return {"ok": True, "cvegeo_mun": t, "nom_mun": mun.set_index("cvegeo_mun").at[t, "nom_mun"]}
    n = norm(t)
    por_nom = {norm(a): (c, a) for c, a in zip(mun["cvegeo_mun"], mun["nom_mun"])}
    if n in por_nom:
        c, a = por_nom[n]
        return {"ok": True, "cvegeo_mun": c, "nom_mun": a}
    hall = rag.municipios_en(t)
    if len(hall) == 1:
        c = mun.loc[mun["nom_mun"] == hall[0], "cvegeo_mun"].iloc[0]
        return {"ok": True, "cvegeo_mun": c, "nom_mun": hall[0]}
    fuera = rag.ciudades_fuera(t)
    if fuera:
        return {"ok": False, "fuera_de_zmvm": True,
                "motivo": f"{t} esta fuera de la Zona Metropolitana del Valle de Mexico; el modelo solo cubre sus 76 municipios"}
    sug = difflib.get_close_matches(n, list(por_nom), n=3, cutoff=0.6)
    return {"ok": False, "motivo": f"{NO}: '{t}' no es un municipio o alcaldia de la ZMVM",
            "sugerencias": [por_nom[s][1] for s in sug]}


def _fuera(texto: str) -> list[str]:
    return rag.ciudades_fuera(texto or "")


# ---------------------------------------------------------------- perfil_giro
@lru_cache(maxsize=1)
def _sinonimos() -> list[tuple[str, str]]:
    """(frase normalizada, clave), las mas largas primero."""
    pares = set()
    for k, g in motor.giros().items():
        for s in list(g.get("nombres", [])) + [k.replace("_", " ")]:
            pares.add((norm(s), k))
    return sorted(pares, key=lambda p: -len(p[0]))


def _singular(n: str) -> str:
    """'heladerias' -> 'heladeria', 'farmacias' -> 'farmacia' (palabra por palabra, conservador)."""
    out = []
    for w in n.split():
        if len(w) > 5 and w.endswith("es") and w[-3] in "rnld":
            w = w[:-2]
        elif len(w) > 4 and w.endswith("s"):
            w = w[:-1]
        out.append(w)
    return " ".join(out)


def _buscar_giro(texto: str) -> tuple[str | None, str | None]:
    """Clave del giro cuyo sinonimo aparece (palabras completas) en el texto; el sinonimo mas largo gana."""
    for q in (f" {norm(texto)} ", f" {_singular(norm(texto))} "):
        for frase, clave in _sinonimos():
            if f" {frase} " in q or f" {_singular(frase)} " in q:
                return clave, frase
    return None, None


@lru_cache(maxsize=1)
def _conteo_scian() -> pd.Series:
    d = pd.read_parquet(PROC / "denue_actual.parquet", columns=["codigo_act"])
    return d["codigo_act"].value_counts()


@lru_cache(maxsize=1)
def _metricas() -> pd.DataFrame:
    p = RAIZ / "models" / "metricas_giro.csv"
    return pd.read_csv(p).set_index("giro") if p.exists() else pd.DataFrame()


def _scian_proponer(texto: str, n: int = 3) -> list[dict]:
    """Clases SCIAN (6 digitos) cuyo titulo comparte palabras con el texto."""
    vacias = {"quiero", "poner", "abrir", "negocio", "tienda", "donde", "para", "una", "unos", "como", "zona",
              "colonia", "mejor", "conviene", "ciudad", "mexico", "local", "venta", "servicio", "servicios",
              "algo", "barato", "nivel", "bajo", "medio", "alto", "cerca", "economico"}
    toks = [t for t in _singular(norm(texto)).split() if len(t) >= 4 and t not in vacias]
    if not toks:
        return []
    sc = pd.read_csv(PROC / "scian.csv", dtype=str)
    sc = sc[sc["codigo"].str.len() == 6].copy()
    tit = sc["titulo"].map(lambda s: _singular(norm(s)))
    sc["p"] = [sum(f" {t} " in f" {tt} " for t in toks) for tt in tit]  # palabras completas
    sc = sc[sc["p"] > 0].sort_values(["p", "codigo"], ascending=[False, True]).head(n)
    cnt = _conteo_scian()
    return [{"scian": c, "titulo": t, "establecimientos_zmvm_2026": int(cnt.get(c, 0))}
            for c, t in zip(sc["codigo"], sc["titulo"])]


def perfil_giro(texto: str) -> dict:
    """Texto libre ('quiero poner una neveria') -> giro del catalogo con sus supuestos."""
    clave, frase = _buscar_giro(texto or "")
    if clave is None:
        props = _scian_proponer(texto or "")
        return {"encontrado": False,
                "motivo": f"{NO}: ningun giro de config/giros.yaml coincide con el texto",
                "propuestas_scian": props,
                "giros_disponibles": sorted(motor.giros()),
                "sugerencia": "usa sugerir_giros(municipio, nse) si la persona no tiene giro definido",
                "fuentes": [F_GIROS] + ([F_SCIAN, F_DENUE] if props else [])}
    g = motor.giros()[clave]
    cnt = _conteo_scian()
    comp_directa = int(sum(cnt.get(c, 0) for c in g.get("scian", [])))
    out = {"encontrado": True, "giro": clave, "coincidencia": frase, "nombres": g.get("nombres", [])[:4],
           "scian_competencia": g.get("scian", []),
           "scian_con_filtro_por_nombre": [f["codigos"] for f in g.get("scian_con_filtro", [])] or None,
           "establecimientos_zmvm_2026_clases_scian": comp_directa if g.get("scian") else None,
           "radio_influencia_m": g["radio_influencia_m"],
           "cliente_objetivo_edades": g.get("cliente_objetivo"), "nse_objetivo": g.get("nse_objetivo"),
           "demanda_base": g.get("demanda_base", "residente"),
           "rubro_enigh": g.get("rubro_enigh") or NO,
           "ticket_promedio_mxn": g.get("ticket_promedio_mxn"), "ticket_fuente": g.get("ticket_fuente"),
           "notas": g.get("notas")}
    if g.get("rubro_enigh_nota"):
        out["aviso_rubro"] = g["rubro_enigh_nota"]
    if aviso_rubro_amplio(clave):
        out["aviso_rubro_amplio"] = aviso_rubro_amplio(clave)
    m = _metricas()
    if clave in m.index:
        r = m.loc[clave]
        out["validacion_modelo"] = {"auc_modelo": _r(r["auc_modelo"], 2), "auc_linea_base_densidad": _r(r["auc_densidad"], 2),
                                    "agebs_con_apertura_2020_2026": _r(r["agebs_con_apertura"])}
        if r["agebs_con_apertura"] < 30:
            out["aviso_modelo"] = "giro raro: muy pocas AGEB con aperturas, el modelo es poco confiable para este giro"
    out["fuentes"] = [F_GIROS, F_DENUE, F_MODELO]
    return out


# ---------------------------------------------------------------- recomendar_zonas
def _resolver_giro(giro: str) -> str | None:
    if giro in motor.giros():
        return giro
    clave, _ = _buscar_giro(giro or "")
    return clave


# La edad que le importa a cada giro, en UN solo lugar (los demas giros usan 25-59, la poblacion en edad de
# trabajar). Es criterio del proyecto, coherente con cliente_objetivo de config/giros.yaml; no es un dato medido.
EDAD_CLAVE = {
    "heladeria": "0-14", "papeleria": "0-14", "guarderia": "0-14", "pizzeria": "0-14",
    "libreria": "15-24", "cafe_internet": "15-24", "tienda_celulares": "15-24", "bar": "15-24", "escuela_idiomas": "15-24",
    "farmacia": "60+", "optica": "60+", "consultorio_medico": "60+", "laboratorio_clinico": "60+",
}
EDAD_DEFECTO = "25-59"
EDAD_COL = {"0-14": "pob_0_14", "15-24": "pob_15_24", "25-59": "pob_25_59", "60+": "pob_60_mas"}
EDAD_ETIQUETA = {"0-14": "0 a 14 años", "15-24": "15 a 24 años", "25-59": "25 a 59 años", "60+": "60 años o más"}


# Nombre natural (con acentos) de cada giro, para mostrarlo en pantalla; contiene un sinonimo del giro.
NOMBRE_GIRO = {
    "heladeria": "heladería", "cafeteria": "cafetería", "gimnasio": "gimnasio", "farmacia": "farmacia", "papeleria": "papelería",
    "lavanderia": "lavandería", "veterinaria": "veterinaria", "taqueria": "taquería", "abarrotes": "tienda de abarrotes",
    "barberia_estetica": "barbería y estética", "consultorio_dental": "consultorio dental", "guarderia": "guardería",
    "ferreteria": "ferretería", "pasteleria": "pastelería", "libreria": "librería", "renta_bicicletas": "renta de bicicletas",
    "tortilleria": "tortillería", "fonda": "fonda", "pizzeria": "pizzería", "optica": "óptica", "tienda_ropa": "tienda de ropa",
    "zapateria": "zapatería", "cerrajeria": "cerrajería", "taller_mecanico": "taller mecánico",
    "purificadora": "purificadora de agua", "panaderia": "panadería", "tienda_mascotas": "tienda de mascotas",
    "escuela_idiomas": "escuela de idiomas", "spa": "spa", "cafe_internet": "café internet", "floreria": "florería",
    "carniceria": "carnicería", "fruteria": "frutería", "comida_china": "comida china", "sushi": "sushi", "bar": "bar",
    "coworking": "coworking", "consultorio_medico": "consultorio médico", "laboratorio_clinico": "laboratorio clínico",
    "tienda_celulares": "tienda de celulares",
}


def nombre_giro(clave: str) -> str:
    return NOMBRE_GIRO.get(clave, clave.replace("_", " "))


def edad_clave(clave: str) -> str:
    """Grupo de edad del Censo que importa al giro (0-14, 15-24, 25-59 o 60+)."""
    return EDAD_CLAVE.get(clave, EDAD_DEFECTO)


@lru_cache(maxsize=4)
def _pct_edad_zmvm(grupo: str) -> float:
    f = motor.cargar_features()
    return float(100 * f[EDAD_COL[grupo]].sum() / f["pob_total"].sum())


@lru_cache(maxsize=40)
def _score(clave: str) -> pd.DataFrame:
    d = motor.score_giro(clave)
    f = motor.cargar_features()
    extra = f[["cve_ent", "cve_mun", "decil_imputado", "pob_total", "hogares", "ing_trim_mediano_est",
               "pob_0_14", "pob_15_24", "pob_25_59", "pob_60_mas"]]
    d = d.join(extra, on="cvegeo")
    d["cvegeo_mun"] = d["cve_ent"].astype(str) + d["cve_mun"].astype(str)
    d["rank_zmvm"] = np.arange(1, len(d) + 1)
    return d


def _pesos_txt(v) -> str:
    return f"${v:,.0f}" if isinstance(v, (int, float)) else str(v)


def _resumen(z: dict) -> str:
    """Una linea con las cifras de la zona, ya formateadas (el agente la copia tal cual; corta para no alargar la respuesta)."""
    g = z["gasto_potencial_trim_mxn"]
    if isinstance(g, (int, float)):
        gasto = _pesos_txt(g) + " por trimestre" + (f" ({z['gasto_potencial_nota']})" if z.get("gasto_potencial_nota") else "")
    else:
        gasto = str(g)
    ing = _pesos_txt(z["ingreso_trim_mediano_estimado_mxn"]) if isinstance(z["ingreso_trim_mediano_estimado_mxn"], (int, float)) else NO
    edad = f"{z['edad_clave_pct']} %" if isinstance(z["edad_clave_pct"], (int, float)) else f"{NO} (el Censo reserva el dato)"
    return (f"prob. de apertura {z['prob_apertura_pct']} %; gasto potencial {gasto}; "
            f"{z['competidores_ponderados']} competidores ponderados (captura {z['captura_huff_pct']} %); "
            f"NSE estimado {z['nse_estimado']}, decil {z['decil_estimado']}, ingreso trimestral estimado por hogar {ing}; "
            f"{z['edad_clave_etiqueta']}: {edad}")


UMBRAL_HABITANTES_AGEB = 200   # una AGEB del top con menos habitantes o menos hogares que esto lleva aviso
UMBRAL_HOGARES_AGEB = 50


def _aviso_ageb_vacia(pob, hogares) -> str | None:
    """Aviso de una AGEB casi vacia: el score mide el radio de influencia, asi que el gasto no sale de quienes viven en ella."""
    if isinstance(pob, (int, float)) and pob < UMBRAL_HABITANTES_AGEB:
        cuanto = f"{pob:,} habitantes"
    elif isinstance(hogares, (int, float)) and hogares < UMBRAL_HOGARES_AGEB:
        cuanto = f"{hogares:,} hogares"
    else:
        return None
    return f"AGEB con {cuanto}: el gasto viene del radio de influencia, no de quienes viven en la AGEB"


def _zona(r, clave: str) -> dict:
    g = motor.giros()[clave]
    grupo = edad_clave(clave)
    pob = r["pob_total"]
    # el Censo reserva (NaN) el dato de algunos grupos de edad en AGEB chicas: sin dato no hay porcentaje
    edad_pct = _r(100 * r[EDAD_COL[grupo]] / pob, 1) if pob and pd.notna(r[EDAD_COL[grupo]]) else None
    z = {"colonia": _txt(r["nom_colonia"]), "municipio": _txt(r["nom_mun"]), "ageb": r["cvegeo"],
         "score": _r(r["score"], 1), "rank_zmvm": int(r["rank_zmvm"]),
         "prob_apertura_pct": _r(100 * r["prob_apertura"]),
         "aperturas_esperadas_en_radio": _r(r["aperturas_esperadas"], 2),
         "gasto_potencial_trim_mxn": (_r(r["demanda"], -3) if np.isfinite(r["demanda"]) else NO) if g.get("gasto_dimensionable", True)
                                     else GASTO_NO_DIMENSIONABLE,
         "competidores_ponderados": _r(r["competencia"], 1),
         "captura_huff_pct": _r(100 * r["captura_huff"]),
         "residentes_objetivo_en_radio": _r(r["residentes_objetivo"], -1),
         "empleos_en_radio": _r(r["empleo_radio"], -1),
         "demanda_de_personas": BASE_DEMANDA[g.get("demanda_base", "residente")],
         "negocios_corredor_comercial_en_radio": _r(r["corredor_radio"]),
         "complementarios_ponderados": _r(r["complementarios"], 1),
         "prob_sigue_abierto_pct": _r(100 * r["prob_sobrevive"]) if pd.notna(r.get("prob_sobrevive")) else NO,
         "nse_estimado": _txt(r["nse"]) or NO,
         "decil_estimado": _r(r["decil_imputado"]) if pd.notna(r["decil_imputado"]) else NO,
         "ingreso_trim_mediano_estimado_mxn": _r(r["ing_trim_mediano_est"], -2) if pd.notna(r["ing_trim_mediano_est"]) else NO,
         "edad_clave_grupo": grupo, "edad_clave_etiqueta": EDAD_ETIQUETA[grupo],
         "edad_clave_pct": NO if edad_pct is None else edad_pct,
         "edad_clave_pct_zmvm": _r(_pct_edad_zmvm(grupo), 1),
         "poblacion_ageb_2020": _r(pob), "hogares_ageb_2020": _r(r["hogares"]) if pd.notna(r["hogares"]) else None,
         "radio_m": g["radio_influencia_m"]}
    aviso_ageb = _aviso_ageb_vacia(z["poblacion_ageb_2020"], z["hogares_ageb_2020"])
    if aviso_ageb:
        z["aviso_ageb_poco_poblada"] = aviso_ageb
    if "dist_colonia_km" in r.index and pd.notna(r["dist_colonia_km"]):
        z["dist_a_colonia_km"] = _r(r["dist_colonia_km"], 1)
        z["en_colonia_consultada"] = bool(r["en_colonia"])
    if g.get("gasto_proxy") and isinstance(z["gasto_potencial_trim_mxn"], (int, float)):
        z["gasto_potencial_nota"] = f"proxy: {g['gasto_proxy']}"
    z["resumen_texto"] = _resumen(z)
    return z


GASTO_NO_DIMENSIONABLE = "no dimensionable (la ENIGH casi no registra gasto en este rubro)"
BASE_DEMANDA = {"residente": "residentes objetivo", "diurna": "empleos (población que trabaja ahí)",
                "mixta": "mitad residentes objetivo, mitad empleos"}
NOMBRES_PESOS = {"prob_apertura": "aperturas esperadas del giro (modelo)", "demanda_neta": "gasto potencial x captura Huff",
                 "pob_neta": "poblacion objetivo x ajuste a NSE x captura", "flujo": "flujo de gente (empleo, corredor comercial, Metro)",
                 "complementarios": "complementarios"}
COMO_LEER = ("el score 0-100 es un percentil DENTRO de este giro: ordena colonias para este giro en la ZMVM; "
             "no dice que el giro sea rentable ni sirve para comparar giros entre sí (para eso, la prob. de apertura absoluta)")
PROB_BAJA = 0.10  # prob. de apertura por AGEB debajo de esto = pocos negocios del giro abren ahi
RADIO_COLONIA_KM = 2.0  # con `colonia`: AGEB de la colonia y las que estan a esta distancia de su centroide


def metodo_score() -> str:
    return ("score 0-100 = " + " + ".join(f"{100 * w:.0f} % {NOMBRES_PESOS[k]}" for k, w in motor.PESOS_SCORE.items())
            + "; todo medido en el radio de influencia (reparto dasimetrico de cada AGEB en una malla de 100 m) "
              "y cada termino en percentil dentro de la ZMVM para el giro")


def _rango(v: list) -> str:
    """«0» si todos son iguales, «2 a 9» si no."""
    return f"{min(v)}" if min(v) == max(v) else f"{min(v)} a {max(v)}"


def _n_agebs_base(clave: str, m) -> str:
    """«1 de 5,875 AGEB» (si son pocas) o «el 12 % de las AGEB»: en cuantas AGEB aparecio una apertura del giro 2020-2026."""
    n, tasa = int(m.at[clave, "agebs_con_apertura"]), float(m.at[clave, "tasa_base"])
    pct = 100 * tasa
    if pct < 1 and tasa > 0:
        return f"{n:,} de {round(n / tasa):,} AGEB"
    return f"el {_r(pct)} % de las AGEB"


def aviso_rubro_amplio(clave: str) -> str | None:
    """Aviso de los giros cuyo gasto potencial usa un rubro ENIGH amplio o sustituto (config/giros.yaml: rubro_enigh_tipo):
    el gasto ordena zonas dentro del giro, pero no es comparable con el de otro giro (otro rubro, otro tamano)."""
    g = motor.giros().get(clave, {})
    tipo, etiqueta = g.get("rubro_enigh_tipo"), g.get("rubro_enigh_etiqueta")
    if not (tipo and etiqueta and g.get("rubro_enigh")):
        return None
    uso = "completo" if tipo == "amplio" else "como sustituto del giro"
    return (f"el gasto potencial usa el rubro ENIGH {etiqueta} {uso}; sirve para ordenar zonas dentro del giro, "
            "no para comparar entre giros")


def _destacados(zonas: list[dict]) -> dict:
    """Lo que distingue a las zonas del top, ya calculado (el agente lo cita en la lectura sin buscar en cada renglon)."""
    def mejor(clave, mayor=True):
        v = [z for z in zonas if isinstance(z.get(clave), (int, float))]
        return (max if mayor else min)(v, key=lambda z: z[clave]) if v else None

    out = {}
    for nombre, clave, mayor, etiqueta in (
            ("mayor_ingreso_estimado", "ingreso_trim_mediano_estimado_mxn", True, "ingreso trimestral estimado por hogar"),
            ("menor_competencia", "competidores_ponderados", False, "competidores ponderados"),
            ("mayor_prob_apertura", "prob_apertura_pct", True, "prob. de apertura %"),
            ("mayor_gasto_potencial", "gasto_potencial_trim_mxn", True, "gasto potencial por trimestre"),
            ("mayor_edad_clave", "edad_clave_pct", True, "% de la edad clave")):
        z = mejor(clave, mayor)
        if z:
            out[nombre] = {"colonia": z["colonia"], "ageb": z["ageb"], etiqueta: z[clave]}
            empatan = [w["colonia"] for w in zonas if w.get(clave) == z[clave]]
            if 1 < len(empatan) < len(zonas):    # varias zonas con el mismo valor extremo (si son todas, no distingue a nadie)
                out[nombre]["empatan"] = empatan
    ing = [z["ingreso_trim_mediano_estimado_mxn"] for z in zonas if isinstance(z.get("ingreso_trim_mediano_estimado_mxn"), (int, float))]
    pct = [z["edad_clave_pct"] for z in zonas if isinstance(z.get("edad_clave_pct"), (int, float))]
    if ing:
        out["rango_ingreso_trimestral_estimado_mxn"] = [min(ing), max(ing)]
    if pct:
        out["rango_edad_clave_pct"] = [min(pct), max(pct)]
    return out


def _filtro_colonia(colonia: str, cve_mun: str | None, nom_mun: str | None, radio_km: float) -> tuple[set | None, pd.Series | None, dict]:
    """Resuelve la colonia pedida. Regresa (AGEB permitidas | None, distancia km al centroide | None, info).

    Nunca calla: info["aviso"] dice que filtro se uso, que hubo de ambiguo o que NO se encontro y que se da a cambio."""
    r = lugares.resolver(colonia, cve_mun)
    ambito = nom_mun or "toda la ZMVM"
    if not r["ok"]:
        sug = r.get("sugerencias") or []
        aviso = (f"NO ENCONTRADO: «{colonia}» no aparece como colonia o asentamiento ({'en ' + nom_mun if nom_mun else 'en la ZMVM'}). "
                 f"A cambio se muestra el top del giro en {ambito}, SIN filtro de colonia."
                 + (f" ¿Quisiste decir: {'; '.join(sug)}?" if sug else ""))
        return None, None, {"consulta": colonia, "encontrada": False, "motivo": r["motivo"], "sugerencias": sug, "aviso": aviso}
    dist = lugares.distancias_km(r["centro"])
    dentro = set(r["agebs"])
    permitidas = dentro | set(dist.index[dist <= radio_km])
    nombre = r["colonias"][0].title() if r["n_colonias"] == 1 else r["consulta"].strip().title()
    info = {"consulta": colonia, "encontrada": True, "criterio": r["criterio"], "ambigua": r["ambigua"],
            "municipio": r["municipio"], "colonias_coincidentes": r["colonias"], "n_colonias": r["n_colonias"],
            "agebs_en_colonia": len(dentro), "radio_km": radio_km, "agebs_en_radio": len(permitidas),
            "centroide": r["centro"]}
    aviso = (f"Filtro por colonia: «{nombre}» ({r['municipio']}; {len(dentro)} AGEB). El top se limita a las AGEB de esa colonia "
             f"y a las que están a {radio_km:g} km o menos de su centroide; hay al menos 3 zonas de la colonia misma (si las tiene) y cada zona dice si está dentro y a cuántos km queda.")
    if r.get("parcial"):  # lo pedido NO existe y empieza con una colonia que si: se dice, no se resuelve en silencio
        usada = r["colonias"][0].title() if r["n_colonias"] == 1 else r["usada"].title()
        aviso = (f"NO ENCONTRADO: «{r['pedido']}» no aparece como colonia o asentamiento; se usó la colonia más parecida, "
                 f"«{usada}» ({r['municipio']}). " + aviso)
        info.update(parcial=True, pedido=r["pedido"], usada=usada)
    if r["criterio"] == "aproximado":
        aviso += f" Se interpretó «{colonia}» como {', '.join(r['colonias'][:2])}."
    if r["ambigua"]:
        info["alternativas"] = r["alternativas"]
        otras = "; ".join(f"{a['municipio']} ({a['agebs']} AGEB)" for a in r["alternativas"][:3])
        aviso += (f" Hay más colonias con ese nombre ({otras}); se usó la de {r['municipio']}, la más poblada. "
                  "Si buscabas otra, indica el municipio.")
    info["aviso"] = aviso
    return permitidas, dist, info


def recomendar_zonas(giro: str, municipio: str | None = None, nse: str | None = None, top: int = 5,
                     una_por_colonia: bool = True, colonia: str | None = None,
                     radio_km: float = RADIO_COLONIA_KM) -> dict:
    """Top de AGEB (colonias) para un giro, opcionalmente dentro de un municipio, un NSE y/o cerca de una colonia.

    colonia: nombre de colonia o asentamiento («Polanco», «la Condesa», «Santa Fe»). Limita el top a las AGEB de esa
    colonia y a las que estan a `radio_km` o menos de su centroide; `filtros`, `colonia_consultada` y `aviso_colonia`
    dicen el filtro. Si la colonia no existe o es ambigua lo dice y explica que se da a cambio."""
    clave = _resolver_giro(giro)
    if clave is None:
        return {"encontrado": False, "motivo": f"{NO}: giro '{giro}' no esta en config/giros.yaml",
                "giros_disponibles": sorted(motor.giros()), "fuentes": [F_GIROS]}
    mres = resolver_municipio(municipio)
    if not mres["ok"]:
        return {"encontrado": False, "giro": clave, **{k: v for k, v in mres.items() if k != "ok"},
                "fuentes": [F_ZMVM]}
    d = _score(clave)
    filtros = {}
    info_col = None
    if colonia and str(colonia).strip():
        permitidas, dist, info_col = _filtro_colonia(str(colonia), mres["cvegeo_mun"], mres["nom_mun"], float(radio_km))
        if permitidas is not None:
            d = d[d["cvegeo"].isin(permitidas)].copy()
            d["dist_colonia_km"] = dist.reindex(d["cvegeo"]).to_numpy()
            d["en_colonia"] = d["cvegeo"].isin(set(lugares.resolver(str(colonia), mres["cvegeo_mun"])["agebs"])).to_numpy()
            filtros["colonia"] = info_col["usada"] if info_col.get("parcial") else str(colonia).strip()
            if info_col.get("parcial"):
                filtros["colonia_no_encontrada"] = info_col["pedido"]
            filtros["radio_km_colonia"] = float(radio_km)
        else:
            filtros["colonia_no_encontrada"] = str(colonia).strip()
    if mres["cvegeo_mun"]:
        d = d[d["cvegeo_mun"] == mres["cvegeo_mun"]]
        filtros["municipio"] = mres["nom_mun"]
    if nse:
        n = norm(nse)
        if n not in ("bajo", "medio", "alto"):
            return {"encontrado": False, "motivo": "nse debe ser bajo, medio o alto", "fuentes": []}
        d = d[d["nse"] == n]
        filtros["nse"] = n
    if d.empty:
        return {"encontrado": False, "giro": clave, "filtros": filtros,
                **({"colonia_consultada": info_col, "aviso_colonia": info_col["aviso"]} if info_col else {}),
                "motivo": f"{NO}: no hay AGEB urbanas con esos filtros", "fuentes": [F_CENSO]}
    n_eval = int(len(d))
    if una_por_colonia:  # la mejor AGEB de cada colonia, para no repetir la misma colonia 5 veces
        d = d.drop_duplicates(subset=["nom_mun", "nom_colonia"], keep="first")
    top = max(1, min(int(top or 5), 10))
    if "en_colonia" in d.columns:  # con colonia: al menos 3 de las del top son de la colonia misma (si hay), el resto por score
        dentro = d[d["en_colonia"]].head(min(3, top))
        sel = pd.concat([dentro, d.drop(index=dentro.index).head(top - len(dentro))]).sort_values("score", ascending=False)
    else:
        sel = d.head(top)
    zonas = [_zona(r, clave) for _, r in sel.iterrows()]
    g = motor.giros()[clave]
    avisos = ["«apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos",
              "el NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)",
              f"el ticket promedio de {g.get('ticket_promedio_mxn')} pesos es un supuesto ({g.get('ticket_fuente')})"]
    if g.get("rubro_enigh_nota"):
        avisos.append(g["rubro_enigh_nota"])
    aviso_rubro = aviso_rubro_amplio(clave)
    if aviso_rubro:
        avisos.append(aviso_rubro)
    if not g.get("rubro_enigh"):
        avisos.append("sin rubro ENIGH para este giro: gasto potencial NO ENCONTRADO, el score usa población objetivo")
    m = _metricas()
    if clave in m.index and m.at[clave, "agebs_con_apertura"] < 30:
        avisos.append(f"giro raro: solo {int(m.at[clave, 'agebs_con_apertura'])} AGEB con aperturas 2020-2026; el modelo es poco confiable")
    out = {"encontrado": True, "giro": clave, "filtros": filtros or None, "agebs_evaluadas": n_eval,
           "metodo": metodo_score(), "como_leer_score": COMO_LEER, "destacados": _destacados(zonas),
           "edad_clave": {"grupo": edad_clave(clave), "etiqueta": EDAD_ETIQUETA[edad_clave(clave)],
                          "pct_zmvm": _r(_pct_edad_zmvm(edad_clave(clave)), 1),
                          "peso_en_cliente_objetivo": g.get("cliente_objetivo", {}).get(edad_clave(clave))}}
    if aviso_rubro:
        out["aviso_rubro_amplio"] = aviso_rubro
    if info_col:
        out["colonia_consultada"] = info_col
        out["aviso_colonia"] = info_col["aviso"]
    probs = [z["prob_apertura_pct"] for z in zonas]
    if max(probs) < 100 * PROB_BAJA:
        tb = f"; en la ZMVM apareció en {_n_agebs_base(clave, m)}" if clave in m.index else ""
        out["aviso_prob_baja"] = (f"probabilidad de apertura baja en todo el top ({_rango(probs)} %){tb}: "
                                  "el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable")
        avisos.insert(0, out["aviso_prob_baja"])
    if info_col:
        avisos.insert(0, info_col["aviso"])
    return {**out, "rubro_enigh": g.get("rubro_enigh") or NO,
            "zonas": zonas, "avisos": avisos,
            "fuentes": [F_MODELO, F_DENUE, F_CENSO, F_ENIGH, F_GIROS]}


# ---------------------------------------------------------------- ficha_zona
def _ficha(f: pd.Series, clave: str | None) -> dict:
    out = {"ageb": f["cvegeo"], "colonia": _txt(f["nom_colonia"]), "municipio": _txt(f["nom_mun"]),
           "colonia_fuente": _txt(f.get("colonia_fuente")),
           "poblacion_2020": _r(f["pob_total"]), "hogares_2020": _r(f["hogares"]),
           "densidad_hab_km2": _r(f["densidad_hab_km2"], -1), "area_km2": _r(f["area_km2"], 3),
           "edades_2020": {"0-14": _r(f["pob_0_14"]), "15-24": _r(f["pob_15_24"]), "25-59": _r(f["pob_25_59"]),
                           "60+": _r(f["pob_60_mas"])},
           "escolaridad_prom_anios": _r(f["escolaridad_prom"], 1),
           "pct_viviendas_auto": _r(f["pct_viv_auto"]), "pct_viviendas_internet": _r(f["pct_viv_internet"]),
           "nse_estimado": _txt(f["nse"]) or NO,
           "decil_estimado": _r(f["decil_imputado"]) if pd.notna(f["decil_imputado"]) else NO,
           "ingreso_trim_mediano_estimado_mxn": _r(f["ing_trim_mediano_est"], -2) if pd.notna(f["ing_trim_mediano_est"]) else NO,
           "grado_marginacion_conapo_2020": _txt(f["gm_2020"]) or NO,
           "establecimientos_denue_en_ageb": _r(f["n_establecimientos"]),
           "empleados_denue_en_ageb": _r(f["pob_diurna"]),
           "escuelas_1km": _r(f["n_escuelas_1km"]), "hospitales_1km": _r(f["n_hospitales_1km"]),
           "plazas_o_super_1km": _r(f["n_plazas_1km"]),
           "estacion_cercana": _txt(f["estacion_cercana"]), "sistema_estacion": _txt(f["sistema_estacion"]),
           "dist_estacion_m": _r(f["dist_estacion_m"], -1),
           "fuentes": [F_CENSO, F_DENUE, F_CONAPO, F_ENIGH, F_TRANSP]}
    if clave:
        d = _score(clave)
        fila = d[d["cvegeo"] == f["cvegeo"]]
        if len(fila):
            z = _zona(fila.iloc[0], clave)
            out["giro"] = {"clave": clave, **{k: v for k, v in z.items() if k not in ("colonia", "municipio", "ageb")},
                           "de_agebs": int(len(d))}
            out["fuentes"].append(F_MODELO)
    return out


def ficha_zona(zona: str, municipio: str | None = None, giro: str | None = None) -> dict:
    """Ficha de una AGEB (clave de 13 caracteres) o de una colonia (nombre; puede haber varias AGEB)."""
    f = motor.cargar_features()
    clave = _resolver_giro(giro) if giro else None
    z = str(zona or "").strip().upper()
    if re.fullmatch(r"\d{9}[0-9A-Z]{4}", z):
        if z not in f.index:
            return {"encontrado": False, "motivo": f"{NO}: AGEB {z} no esta en agebs_features (ZMVM urbana)",
                    "fuentes": [F_CENSO]}
        return {"encontrado": True, **_ficha(f.loc[z], clave)}
    if _fuera(zona):
        return {"encontrado": False, "fuera_de_zmvm": True, "motivo": f"{zona} esta fuera de la ZMVM", "fuentes": [F_ZMVM]}
    cand = f
    if municipio:
        mres = resolver_municipio(municipio)
        if not mres["ok"]:
            return {"encontrado": False, **{k: v for k, v in mres.items() if k != "ok"}, "fuentes": [F_ZMVM]}
        cand = f[f["nom_mun"] == mres["nom_mun"]]
    n = norm(zona)
    col = cand["nom_colonia"].map(norm)
    hit = cand[col == n]
    if hit.empty:
        hit = cand[col.str.contains(rf"\b{re.escape(n)}\b", regex=True)] if n else hit
    if hit.empty:
        mres = resolver_municipio(zona)
        if mres["ok"] and mres["nom_mun"]:
            return {"encontrado": False, "motivo": f"'{zona}' es un municipio, no una colonia: usa recomendar_zonas(giro, municipio)",
                    "fuentes": [F_ZMVM]}
        sug = difflib.get_close_matches(n, sorted(set(col)), n=3, cutoff=0.75)
        return {"encontrado": False, "motivo": f"{NO}: colonia '{zona}' no esta en agebs_features",
                "sugerencias": sug, "fuentes": [F_DENUE]}
    # primero las que empiezan con el texto (p. ej. «del valle» -> DEL VALLE CENTRO antes que FUENTES DEL VALLE)
    hit = hit.assign(_ini=~hit["nom_colonia"].map(norm).str.startswith(n)).sort_values(
        ["_ini", "pob_total"], ascending=[True, False]).drop(columns="_ini")
    grupos = hit.groupby(["nom_colonia", "nom_mun"], sort=False)
    out = {"encontrado": True, "agebs_que_coinciden": int(len(hit)), "colonias": []}
    for (c, m), h in list(grupos)[:3]:
        out["colonias"].append({"colonia": c, "municipio": m, "agebs": h["cvegeo"].head(8).tolist(),
                                "poblacion_2020_suma": _r(h["pob_total"].sum())})
    out["ficha_ageb_mas_poblada"] = _ficha(hit.iloc[0], clave)
    out["fuentes"] = out["ficha_ageb_mas_poblada"]["fuentes"]
    return out


# ---------------------------------------------------------------- buscar_carpetas
def buscar_carpetas(pregunta: str, k: int = 4, max_chars: int = 700) -> dict:
    """Trozos de carpetas/ (metodologia, municipios, teoria, modelo) mas parecidos a la pregunta."""
    res = rag.buscar(pregunta, k=max(1, min(int(k or 4), 8)))
    trozos = [{"archivo": f"carpetas/{r['archivo']}", "seccion": r["seccion"], "score": _r(r["score"], 3),
               "texto": r["texto"][:max_chars]} for r in res]
    return {"encontrado": bool(trozos), "modo": res[0]["modo"] if res else None, "trozos": trozos,
            "fuentes": sorted({t["archivo"] for t in trozos})}


# ---------------------------------------------------------------- contexto_macro
# Giros de alimentos y bebidas (les importa la inflacion de alimentos) y giros con insumos importados (tipo de cambio).
GIROS_ALIMENTOS = {"heladeria", "cafeteria", "taqueria", "abarrotes", "pasteleria", "tortilleria", "fonda", "pizzeria",
                   "panaderia", "carniceria", "fruteria", "comida_china", "sushi", "bar", "purificadora"}
GIROS_IMPORTADOS = {"tienda_celulares", "optica", "taller_mecanico", "tienda_mascotas", "tienda_ropa", "zapateria"}
ETIQUETA_MACRO = {"tasa_objetivo": "tasa objetivo de Banxico", "tiie_28": "TIIE a 28 días",
                  "tipo_cambio_fix": "tipo de cambio FIX", "inpc_general_var_anual": "inflación general (INPC)",
                  "inpc_alimentos_var_anual": "inflación de alimentos, bebidas y tabaco (INPC)",
                  "consumo_privado": "consumo privado (IMCP)", "confianza_consumidor": "confianza del consumidor"}


def indicadores_del_giro(giro: str | None) -> list[str]:
    """Claves de macro.json que le importan al giro: tasa y inflacion siempre; alimentos o FIX segun el giro."""
    claves = ["tasa_objetivo", "inpc_general_var_anual"]
    if giro in GIROS_ALIMENTOS:
        claves.append("inpc_alimentos_var_anual")
    if giro in GIROS_IMPORTADOS:
        claves.append("tipo_cambio_fix")
    return claves


def _fmt_valor(v) -> str:
    """Cifra es-MX: separador de miles desde 1,000 («5,362»); los valores chicos van tal cual («6.25»)."""
    if isinstance(v, (int, float)) and abs(v) >= 1000:
        return f"{v:,.0f}"
    return f"{v}"


# indicador de macro.json -> serie de macro_series.parquet (la misma serie, con datos mas nuevos si ya se bajaron)
SERIE_DE = {"tasa_objetivo": "tasa_objetivo", "tiie_28": "tiie_28", "tipo_cambio_fix": "tipo_cambio_fix", "remesas": "remesas",
            "inpc_general_var_anual": "inpc_general_var_anual", "confianza_consumidor": "confianza_consumidor",
            "consumo_privado": "consumo_privado_var_anual"}
MENSUALES = {"remesas", "inpc_general_var_anual", "inpc_alimentos_var_anual", "confianza_consumidor", "consumo_privado"}


def _fecha_txt(fecha, mensual: bool) -> str | None:
    """Fecha del dato: «2026-10» en las series mensuales (nunca «2026-09-01»), «2026-11-23» en las diarias."""
    if fecha is None:
        return None
    t = str(fecha)[:10]
    return t[:7] if mensual else t


def _macro_json() -> dict:
    """data/processed/macro.json; si macro_series.parquet trae un dato mas nuevo de la MISMA serie (mismo id_serie), usa ese
    valor y su fecha («FIX 19.16 del 2026-11-23» en vez de «19.02 del 2026-11-20»)."""
    m = json.loads((PROC / "macro.json").read_text(encoding="utf-8"))
    p = PROC / "macro_series.parquet"
    if not p.exists():
        return m
    try:
        ser = pd.read_parquet(p)
        ser["fecha"] = pd.to_datetime(ser["fecha"])
    except Exception:
        return m
    for k, nombre in SERIE_DE.items():
        v = m.get(k)
        if not isinstance(v, dict) or "valor" not in v or v.get("estado") == NO:
            continue
        g = ser[ser["serie"] == nombre].sort_values("fecha")
        if g.empty or str(g["id_serie"].iloc[-1]) != str(v.get("id_serie")):
            continue
        try:
            actual = pd.to_datetime(str(v.get("fecha")))
        except (ValueError, TypeError):
            continue
        ult = g.iloc[-1]
        if ult["fecha"] > actual and np.isfinite(ult["valor"]):
            v = {x: y for x, y in v.items() if x not in ("variacion_anual_pct", "acumulado_12_meses_millones_usd")}
            v["valor"], v["fecha"] = float(ult["valor"]), ult["fecha"].strftime("%Y-%m-%d")
            m[k] = v
    return m


def _txt_indicador(k: str, v: dict) -> str:
    if v.get("valor") == NO:
        prox = v.get("proxies") or {}
        p = prox.get("no_subyacente_agropecuarios")
        if p:
            return (f"inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios "
                    f"{_fmt_valor(p['valor'])} % anual ({_fecha_txt(p['fecha'], True)}, serie {p['id_serie']})")
        return f"{ETIQUETA_MACRO.get(k, k)}: NO ENCONTRADO"
    unidad = {"% anual": "% anual", "% variacion anual": "% anual", "MXN por USD": "pesos por dólar",
              "puntos (indice)": "puntos del índice", "% variacion anual (cifras originales)": "% anual (cifras originales)",
              "millones de USD (mensual)": "millones de dólares al mes"}.get(v.get("unidad"), v.get("unidad") or "")
    return f"{ETIQUETA_MACRO.get(k, k)} {_fmt_valor(v['valor'])} {unidad} ({_fecha_txt(v.get('fecha'), k in MENSUALES)}, serie {v.get('id_serie')})"


_ACENTOS_FUENTE = (("Banco de Mexico", "Banco de México"), ("busqueda por ids", "búsqueda por ids"),
                   ("Poblacion", "Población"), ("ambito", "ámbito"))


def _fuente_acentuada(f: str) -> str:
    """Las fuentes que bajaron los scripts de datos vienen sin acentos; el texto visible va con acentos."""
    for a, b in _ACENTOS_FUENTE:
        f = f.replace(a, b)
    return f


# Mecanismo por indicador (texto fijo, sin cifras): lo muestra el agente cuando la pregunta pide «cómo influye / afecta».
ORDEN_COMO = ("tasa_objetivo", "tiie_28", "inpc_general_var_anual", "inpc_alimentos_var_anual", "tipo_cambio_fix",
              "remesas", "confianza_consumidor", "consumo_privado")
COMO_INFLUYE = {
    "tasa_objetivo": "La tasa objetivo de Banxico es la tasa de política, no la que paga el negocio: los bancos prestan a la TIIE, que la sigue "
                     "de cerca, más un margen (que no está en los datos). Con tasa alta cuesta más financiar el equipo, el local y el inventario.",
    "tiie_28": "La TIIE a 28 días es la referencia de los créditos empresariales: si sube, el financiamiento del negocio sale más caro.",
    "tipo_cambio_fix": "Un dólar más caro encarece los insumos y el equipo importados y aprieta el margen si no se puede subir el precio.",
    "inpc_general_var_anual": "La inflación general sube el costo de la renta, los servicios y los insumos, y le quita poder de compra al cliente: "
                              "el negocio absorbe el aumento en su margen o lo traslada al precio y vende menos.",
    "inpc_alimentos_var_anual": "La inflación de alimentos sube el costo de los insumos de un negocio de comida y aprieta el margen, "
                                "además de reducir lo que el hogar gasta fuera de casa.",
    "remesas": "Las remesas sostienen el ingreso de los hogares que las reciben y con ello su gasto en el comercio local.",
    "confianza_consumidor": "Cuando baja la confianza del consumidor, los hogares posponen gastos que no son indispensables.",
    "consumo_privado": "El consumo privado es la demanda total de los hogares: si crece, hay más ventas para el comercio y los servicios.",
}
PIDE_COMO = re.compile(r"\bcomo\s+(?:me\s+|nos\s+|le\s+|les\s+)?(?:influy\w*|afect\w*|impact\w*|cambi\w*|repercut\w*)\b|"
                       r"\b(?:efecto|influencia|impacto)\s+(?:de|del|en)\b|"
                       r"\bcomo\s+(?:esta|anda|va|ve)\s+(?:la\s+)?(?:economia|situacion economica)\b|"
                       r"\b(?:buen|mal|mejor|peor)\s+momento\b|\bmomento\s+(?:para|de)\s+(?:abrir|invertir|poner|emprender)\b")


# «¿me afecta...?» solo cuenta con un termino macro en la misma pregunta («¿me afecta la competencia?» no es de economia)
AFECTA = re.compile(r"\bafect\w*")
TERMINO_MACRO = re.compile(r"\binflacion\b|\btasas?\b|\bdolar(?:es)?\b|\btipo de cambio\b|\beconomi\w*|\bcreditos?\b|\bremesas?\b|"
                           r"\bbanxico\b|\bbanco de mexico\b|\binpc\b|\binteres(?:es)?\b|\bprecios\b|\bconsumo\b|\bconfianza\b")
# «¿es buen momento para abrir?» pide el mecanismo aunque no nombre un indicador
MOMENTO = re.compile(r"\b(?:buen|mal|mejor|peor)\s+momento\b|\bmomento\s+(?:para|de)\s+(?:abrir|invertir|poner|emprender)\b")


def pide_como_influye(pregunta: str | None) -> bool:
    """La pregunta pide el mecanismo («cómo influye la inflación...», «cómo está la economía», «¿es buen momento?»,
    «¿afecta la inflación?»), no solo las cifras. «¿Cómo me afecta la competencia?» no es de economía: el verbo
    (influir, afectar, impacto...) solo cuenta con un término macro en la misma pregunta."""
    q = norm(pregunta or "")
    return bool(MOMENTO.search(q) or ((PIDE_COMO.search(q) or AFECTA.search(q)) and TERMINO_MACRO.search(q)))


def _g(x) -> str:
    """Numero sin ceros de sobra («2.5», «6.25»)."""
    return f"{round(float(x), 2):g}"


def tasa_real(ind: dict) -> dict | None:
    """Tasa real aproximada = tasa objetivo de Banxico menos inflacion general anual (puntos porcentuales), con las cifras
    de `ind` (indicadores de contexto_macro). Es una aproximacion, no una tasa real ex ante."""
    t, i = ind.get("tasa_objetivo"), ind.get("inpc_general_var_anual")
    if not all(isinstance(x, dict) and isinstance(x.get("valor"), (int, float)) for x in (t, i)):
        return None
    return {"valor": round(t["valor"] - i["valor"], 2), "unidad": "puntos porcentuales",
            "formula": "tasa objetivo de Banxico menos inflación general anual",
            "tasa_objetivo": t["valor"], "inflacion_general": i["valor"]}


def _texto_tasa_real(tr: dict) -> str:
    v = tr["valor"]
    lec = ("la tasa de política va por encima de la inflación, así que el dinero tiene un costo real positivo, y el crédito del negocio, "
           "que se paga a la TIIE más un margen, sale todavía más caro" if v > 0 else
           "la tasa de política va por debajo de la inflación, así que el dinero cuesta menos de lo que suben los precios, aunque el crédito "
           "del negocio se paga a la TIIE más un margen" if v < 0 else
           "la tasa de política iguala a la inflación")
    return (f"Con la tasa objetivo en {_g(tr['tasa_objetivo'])} % anual y la inflación general en {_g(tr['inflacion_general'])} % anual, "
            f"la tasa real aproximada es de {_g(v)} puntos porcentuales (tasa objetivo menos inflación anual); {lec}.")


def _texto_insumos(clave: str, ind: dict) -> str | None:
    """Los insumos del giro (config/giros.yaml: insumos) y como los toca la inflacion; para giros de comida, con la
    aproximacion de precios agropecuarios si la inflacion de alimentos no esta."""
    insumos = (motor.giros().get(clave) or {}).get("insumos")
    if not insumos:
        return None
    lista = ", ".join(insumos[:-1]) + (" y " if len(insumos) > 1 else "") + insumos[-1]
    t = (f"Los insumos que más pesan en este giro ({nombre_giro(clave)}) son {lista} (supuesto del proyecto): cuando su precio sube más que el "
         "precio que cobra el negocio, el margen se aprieta.")
    if clave in GIROS_ALIMENTOS:
        al = ind.get("inpc_alimentos_var_anual") or {}
        p = (al.get("proxies") or {}).get("no_subyacente_agropecuarios")
        if p and isinstance(p.get("valor"), (int, float)):
            t += (f" Como aproximación del precio de los alimentos, los precios agropecuarios del INPC variaron "
                  f"{_g(p['valor'])} % anual ({_fecha_txt(p.get('fecha'), True)}).")
    return t


def _como_influye(ks: list[str], out: dict, clave: str | None) -> dict:
    """Mecanismo por indicador, mas la tasa real aproximada y, con giro, los insumos del giro (en ese orden de lectura)."""
    res: dict[str, str] = {}
    tr = tasa_real(out)
    for k in ORDEN_COMO:
        if k in ks and k in COMO_INFLUYE and out[k].get("valor") != NO:
            res[k] = COMO_INFLUYE[k]
        if k == "inpc_general_var_anual":
            if tr and "tasa_objetivo" in out and k in out:
                res["tasa_real"] = _texto_tasa_real(tr)
            ins = _texto_insumos(clave, out) if clave else None
            if ins:
                res["insumos_del_giro"] = ins
    return res


def contexto_macro(giro: str | None = None) -> dict:
    """Ultimos indicadores macro (Banxico e INEGI) con fecha y serie.

    giro: si se da, solo los indicadores que le importan a ese giro (tasa, inflacion; alimentos o tipo de cambio segun
    el giro) y `linea`, una frase lista para citar."""
    m = _macro_json()
    out, fuentes = {}, set()
    for k, v in m.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        if v.get("estado") == NO or "valor" not in v:
            item = {"valor": NO, "detalle": v.get("detalle", "")[:300]}
            if v.get("evidencia") and not giro:
                item["evidencia"] = v["evidencia"][:700]
            prox = {}
            for pk, pv in (v.get("proxies") or {}).items():
                prox[pk] = {"valor": _r(pv["valor"], 2), "unidad": pv.get("unidad"), "fecha": _fecha_txt(pv.get("fecha"), True),
                            "id_serie": pv.get("id_serie")}
                fuentes.add(pv.get("fuente", "").split(";")[0])
            if prox:
                item["proxies"] = prox
            out[k] = item
            continue
        item = {"nombre": ETIQUETA_MACRO.get(k, k), "valor": _r(v["valor"], 2), "unidad": v.get("unidad"),
                "fecha": _fecha_txt(v.get("fecha"), k in MENSUALES),
                "id_serie": v.get("id_serie")}
        for extra in ("variacion_anual_pct", "acumulado_12_meses_millones_usd"):
            if extra in v:
                item[extra] = _r(v[extra], 2 if "pct" in extra else 0)
        out[k] = item
        fuentes.add(v.get("fuente", "").split(";")[0])
    if "remesas" in out:
        out["remesas"]["valor"] = _r(m["remesas"]["valor"], 0)
    alim = out.get("inpc_alimentos_var_anual", {})
    nota = ("valores nacionales, no por colonia; INPC de alimentos "
            + ("NO ENCONTRADO (solo proxies)" if alim.get("valor") == NO else "es el subindice «Alimentos, bebidas y tabaco»"))
    res = {"indicadores": out, "consultado": m.get("_meta", {}).get("generado"), "nota": nota,
           "fuentes": sorted(_fuente_acentuada(f) for f in fuentes if f)}
    res["como_influye"] = _como_influye([k for k in ORDEN_COMO if k in out], out, None)
    tr = tasa_real(out)
    if tr:
        res["tasa_real_aproximada"] = tr
    if giro:
        clave = _resolver_giro(giro)
        if clave:
            ks = [k for k in indicadores_del_giro(clave) if k in out]
            fu = {m[k].get("fuente", "").split(";")[0] for k in ks if isinstance(m.get(k), dict)}
            for k in ks:
                fu |= {pv.get("fuente", "").split(";")[0] for pv in (m[k].get("proxies") or {}).values()}
            res = {"giro": clave, "indicadores": {k: out[k] for k in ks}, "consultado": res["consultado"], "nota": nota,
                   "linea": "valores nacionales: " + "; ".join(_txt_indicador(k, out[k]) for k in ks) + ".",
                   "como_influye": _como_influye(ks, out, clave),
                   "fuentes": sorted(_fuente_acentuada(f) for f in fu if f)}
            if tr:
                res["tasa_real_aproximada"] = tr
    return res


# ---------------------------------------------------------------- ficha_municipio (extra)
FICHA_LINEAS = ("Población en AGEB", "Densidad", "Edad", "Escolaridad promedio", "Población por NSE estimado", "Decil estimado típico")


F_INGRESO_MUN = "estimación del proyecto con ENIGH 2024 y Censo 2020 (reports/decil_imputado.md)"
PIDE_INGRESO = re.compile(r"\bcuanto\s+(?:ganan|gana|gano|ganamos|cobran|cobra|sacan)\b|\bingresos?\b|\bque tan (?:rico|rica|ricos|ricas|pobre|pobres)\b|"
                          r"\bnivel\s+(?:socio\s*economico|economico|de ingresos?)\b|\bsocioeconomic\w*|\bpoder adquisitivo\b")
# «sueldo» o «salario» solo piden el ingreso de la gente si hablan de ella («el sueldo de un empleado» es un costo del negocio)
SUELDO_DE_LA_GENTE = re.compile(r"\b(?:sueldos?|salarios?)\b.*\b(?:ganan|gente|hogares|vecinos|habitantes|familias)\b|"
                                r"\b(?:ganan|gente|hogares|vecinos|habitantes|familias)\b.*\b(?:sueldos?|salarios?)\b")


# «ingreso» suelto que habla del negocio («¿cuánto ingreso necesito para abrir?», «qué ingresos tendría mi negocio»)
INGRESO_DEL_NEGOCIO = re.compile(r"\bingresos?\b.*\b(?:necesit\w*|tendri\w*|tendre|generari\w*|dejari\w*|invert\w*|abrir|mi negocio|del negocio)\b|"
                                 r"\b(?:mi negocio|del negocio)\b.*\bingresos?\b")
DE_LA_GENTE = re.compile(r"\b(?:gente|hogares?|vecinos|habitantes|familias|personas|poblacion|zona|colonia|ahi)\b")


def pide_ingreso(pregunta: str | None) -> bool:
    """La pregunta pide el ingreso de la gente («¿cuánto ganan ahí?», «qué tan ricos», «nivel socioeconómico»)."""
    q = norm(pregunta or "")
    if INGRESO_DEL_NEGOCIO.search(q) and not DE_LA_GENTE.search(q):
        q = re.sub(r"(?<!de )\bingresos?\b", " ", q)    # ese «ingreso» es del negocio; «nivel de ingresos» sigue contando
    return bool(PIDE_INGRESO.search(q) or SUELDO_DE_LA_GENTE.search(q))


def _mediana_ponderada(valores: pd.Series, pesos: pd.Series) -> float | None:
    """Mediana de `valores` donde cada fila pesa `pesos` (el primer valor cuyo peso acumulado llega a la mitad)."""
    d = pd.DataFrame({"v": valores, "w": pesos}).dropna()
    d = d[d["w"] > 0].sort_values("v")
    if d.empty:
        return None
    acum = d["w"].cumsum()
    return float(d["v"][acum >= d["w"].sum() / 2].iloc[0])


def ingreso_municipio(cvegeo_mun: str) -> dict | None:
    """Ingreso trimestral mediano estimado por hogar de un municipio: mediana, ponderada por hogares, del ingreso
    trimestral mediano estimado de sus AGEB (`ing_trim_mediano_est`), y su decil tipico (mediana ponderada por hogares).
    Es una estimacion del proyecto, no un dato del INEGI por municipio."""
    f = motor.cargar_features()
    d = f[(f["cve_ent"].astype(str) + f["cve_mun"].astype(str)) == str(cvegeo_mun)]
    ing = _mediana_ponderada(d["ing_trim_mediano_est"], d["hogares"])
    if ing is None:
        return None
    decil = _mediana_ponderada(d["decil_imputado"], d["hogares"])
    out = {"ingreso_trim_mediano_est_hogar_mxn": _r(ing, -2), "agebs_con_ingreso": int(d["ing_trim_mediano_est"].notna().sum()),
           "metodo_ingreso": "mediana, ponderada por hogares, del ingreso trimestral mediano estimado de las AGEB del municipio",
           "fuente_ingreso": F_INGRESO_MUN}
    if decil is not None:
        out["decil_tipico"] = _r(decil)
    return out


def _linea_ingreso(nombre: str, ing: dict) -> str:
    deciles = f"decil típico {ing['decil_tipico']}; " if ing.get("decil_tipico") is not None else ""
    return (f"Ingreso trimestral mediano estimado por hogar en {nombre}: {_pesos_txt(ing['ingreso_trim_mediano_est_hogar_mxn'])} "
            f"({deciles}{ing['fuente_ingreso'].split(' (')[0]}).")


def ficha_municipio(municipio: str, max_chars: int = 520) -> dict:
    """Trozo corto de la ficha del municipio en carpetas/03_municipios (poblacion, densidad, edades, NSE).

    Lectura directa del indice del RAG: no usa embeddings ni Ollama."""
    mres = resolver_municipio(municipio)
    if not mres["ok"] or not mres["nom_mun"]:
        return {"encontrado": False, **{k: v for k, v in mres.items() if k != "ok"}, "fuentes": [F_ZMVM]}
    try:
        lineas = rag.lineas_ficha(mres["nom_mun"])
    except FileNotFoundError:
        lineas = []
    sel, n = [], 0
    for pref in FICHA_LINEAS:
        for ln in lineas:
            if ln.startswith(pref):
                ln = re.sub(r"\s*Fuente:.*$", "", ln).strip()
                if n + len(ln) <= max_chars:
                    sel.append(ln)
                    n += len(ln)
                break
    if not sel:
        return {"encontrado": False, "municipio": mres["nom_mun"], "motivo": f"{NO}: sin ficha en carpetas/03_municipios",
                "fuentes": ["carpetas/03_municipios"]}
    out = {"encontrado": True, "municipio": mres["nom_mun"], "cvegeo_mun": mres["cvegeo_mun"], "ficha": sel,
           "fuentes": [F_CENSO, F_DENUE, "carpetas/03_municipios (fichas generadas desde agebs_features)"]}
    ing = ingreso_municipio(mres["cvegeo_mun"])
    if ing:
        out.update(ing)
        out["ingreso_linea"] = _linea_ingreso(mres["nom_mun"], ing)
        out["fuentes"].append(F_ENIGH)
    return out


# ---------------------------------------------------------------- sugerir_giros (extra)
@lru_cache(maxsize=1)
def _scores_todos() -> pd.DataFrame:
    p = RAIZ / "models" / "scores_giros.parquet"
    d = pd.read_parquet(p, columns=["cvegeo", "giro", "score", "nse", "prob_apertura", "prob_sobrevive"])
    d["cvegeo_mun"] = d["cvegeo"].str[:5]
    return d


def _auc_sobrevive():
    try:
        return _r(motor.cargar_modelo()[2]["sobrevivencia"]["auc_oof"], 2)
    except Exception:  # sin metadata
        return NO


@lru_cache(maxsize=1)
def _personal_por_giro() -> dict[str, float]:
    """Personal ocupado medio por establecimiento del giro (DENUE 05/2026, punto medio del estrato)."""
    den = motor.denue("actual")
    out = {}
    for clave, g in motor.giros().items():
        sel = motor.seleccionar(den, g.get("scian", []), g.get("scian_con_filtro"))
        if len(sel):
            out[clave] = float(sel["per_ocu_medio"].mean())
    return out


def giros_poca_inversion() -> dict[str, float]:
    """Giros de «poca inversion»: el tercio de giros con el establecimiento tipico mas chico del DENUE.

    El proyecto NO tiene datos de inversion inicial por giro (giros.yaml solo trae ticket por venta). Se usa una
    aproximacion declarada: el personal ocupado medio por establecimiento, porque un negocio de 1 a 3 personas
    necesita menos local, equipo e inventario que uno de 10. Regresa {giro: personal medio}."""
    p = _personal_por_giro()
    orden = sorted(p, key=p.get)
    return {k: round(p[k], 1) for k in orden[:max(3, len(orden) // 3)]}


def sugerir_giros(municipio: str | None = None, nse: str | None = None, ticket_max: float | None = None,
                  top: int = 5, colonia: str | None = None, radio_km: float = RADIO_COLONIA_KM,
                  inversion: str | None = None) -> dict:
    """Giros del catalogo que conviene considerar en una zona (sin giro definido).

    El score de cada giro es percentil DENTRO del giro, asi que no sirve para compararlos (una libreria puede
    tener score 90 con 5 % de probabilidad de apertura). Aqui los giros se ordenan por una medida absoluta y
    comparable: en las 10 mejores AGEB del giro dentro del filtro, prob. de apertura x prob. de seguir abierto
    (las dos del modelo, misma ventana 2020-2026 y misma unidad, la AGEB).

    colonia / radio_km: limita a la colonia y las AGEB a <= radio_km de su centroide (igual que recomendar_zonas).
    inversion='baja': solo giros de poca inversion (aproximacion declarada, ver giros_poca_inversion)."""
    mres = resolver_municipio(municipio)
    if not mres["ok"]:
        return {"encontrado": False, **{k: v for k, v in mres.items() if k != "ok"}, "fuentes": [F_ZMVM]}
    d = _scores_todos()
    filtros = {}
    info_col = None
    if colonia and str(colonia).strip():
        permitidas, _, info_col = _filtro_colonia(str(colonia), mres["cvegeo_mun"], mres["nom_mun"], float(radio_km))
        if permitidas is not None:
            d = d[d["cvegeo"].isin(permitidas)]
            filtros["colonia"] = info_col["usada"] if info_col.get("parcial") else str(colonia).strip()
            if info_col.get("parcial"):
                filtros["colonia_no_encontrada"] = info_col["pedido"]
            filtros["radio_km_colonia"] = float(radio_km)
        else:
            filtros["colonia_no_encontrada"] = str(colonia).strip()
    if mres["cvegeo_mun"]:
        d = d[d["cvegeo_mun"] == mres["cvegeo_mun"]]
        filtros["municipio"] = mres["nom_mun"]
    n = norm(nse) if nse else None
    if n:
        if n not in ("bajo", "medio", "alto"):
            return {"encontrado": False, "motivo": "nse debe ser bajo, medio o alto", "fuentes": []}
        d = d[d["nse"] == n]
        filtros["nse"] = n
    if ticket_max:
        filtros["ticket_max_mxn"] = _r(ticket_max)
    chicos = None
    if inversion:
        if norm(inversion) not in ("baja", "poca", "bajo"):
            return {"encontrado": False, "motivo": "inversion solo acepta 'baja'", "fuentes": []}
        chicos = giros_poca_inversion()
        filtros["inversion"] = "baja (aproximacion: establecimiento tipico chico)"
    m = _metricas()
    filas = []
    for clave, g in motor.giros().items():
        t = g.get("ticket_promedio_mxn")
        if ticket_max and (t is None or t > ticket_max):
            continue
        if chicos is not None and clave not in chicos:
            continue
        if n and g.get("nse_objetivo", {}).get(n, 0) < 0.3:
            continue
        if clave in m.index and m.at[clave, "agebs_con_apertura"] < 30:  # giros raros: el modelo no es confiable
            continue
        s = d[d["giro"] == clave].nlargest(10, "score")
        if not len(s):
            continue
        pa, ps = float(s["prob_apertura"].mean()), float(s["prob_sobrevive"].mean())
        fila = {"giro": clave, "viabilidad_pct": _r(100 * pa * ps), "prob_apertura_pct": _r(100 * pa),
                "prob_sigue_abierto_pct": _r(100 * ps), "score_relativo_medio_top10": _r(s["score"].mean(), 1),
                "ticket_promedio_mxn": t, "peso_nse_objetivo": g.get("nse_objetivo", {}).get(n) if n else None}
        if chicos is not None:
            fila["personal_ocupado_medio_estab"] = chicos[clave]
        if pa < PROB_BAJA:
            fila["aviso"] = "probabilidad de apertura baja: pocos negocios de este giro abren aquí"
        filas.append(fila)
    # el orden es el de viabilidad (el agente lo respeta tal cual)
    filas = sorted(filas, key=lambda r: -r["viabilidad_pct"])[:max(1, min(int(top or 5), 10))]
    extra = {}
    if info_col:
        extra = {"colonia_consultada": info_col, "aviso_colonia": info_col["aviso"]}
    if not filas:
        return {"encontrado": False, "filtros": filtros, **extra, "motivo": f"{NO}: ningun giro cumple los filtros", "fuentes": [F_GIROS]}
    out = {"encontrado": True, "filtros": filtros or None, **extra, "giros": filas,
           "como_leer": ("los giros se ordenan por viabilidad = prob. de apertura x prob. de seguir abierto (absolutas, "
                         "comparables entre giros). El score 0-100 es relativo dentro de cada giro: NO compara giros"),
           "metodo": ("en las 10 AGEB con mejor score de cada giro dentro del filtro: media de la prob. de apertura "
                      "(aparece >= 1 negocio del giro 2020-2026) y de la prob. de que un local nuevo siga abierto; "
                      "con nse se exige peso >= 0.3 en nse_objetivo; se excluyen giros con menos de 30 AGEB con "
                      "aperturas (coworking, renta de bicicletas); ticket es supuesto; la prob. de seguir abierto "
                      f"viene de un modelo debil (AUC {_auc_sobrevive()})"),
           "fuentes": [F_MODELO, F_GIROS, F_DENUE]}
    if chicos is not None:
        out["criterio_inversion"] = ("«barato» se entendió como poca inversión inicial. El proyecto NO tiene la inversión por giro "
                                     "(NO ENCONTRADO; el catálogo solo trae el ticket por venta, que no mide el costo de abrir). "
                                     "Aproximación: giros cuyo establecimiento típico es de los más chicos del DENUE (personal ocupado "
                                     "medio por establecimiento, tercio inferior de los giros del catálogo)")
    return out


# ---------------------------------------------------------------- registro para el agente
HERRAMIENTAS = {"perfil_giro": perfil_giro, "recomendar_zonas": recomendar_zonas, "ficha_zona": ficha_zona,
                "buscar_carpetas": buscar_carpetas, "contexto_macro": contexto_macro, "sugerir_giros": sugerir_giros,
                "ficha_municipio": ficha_municipio}


def ejecutar(nombre: str, argumentos: dict | None) -> dict:
    """Llama una herramienta por nombre; los errores regresan como dict (el LLM los lee)."""
    fn = HERRAMIENTAS.get(nombre)
    if fn is None:
        return {"error": f"herramienta '{nombre}' no existe", "disponibles": list(HERRAMIENTAS)}
    args = {k: v for k, v in (argumentos or {}).items() if v not in (None, "", "null")}
    try:
        return fn(**args)
    except TypeError as e:
        return {"error": f"argumentos invalidos para {nombre}: {e}"}
    except Exception as e:  # que el agente siga y lo diga
        return {"error": f"{type(e).__name__}: {e}"}
