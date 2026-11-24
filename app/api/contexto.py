"""Router de las vistas Macro, El modelo y Datos y carpetas del tablero.

Dueno: el constructor del grupo «contexto». Todo se lee de archivos del repo (nada escrito a mano):
  GET /api/macro                 ultimo valor de data/processed/macro.json + series mensuales de macro_series.parquet
  GET /api/modelo                score (pesos y version leidos en vivo de app.motor), validacion, AUC por giro,
                                 importancia, evaluacion del agente, limites y preguntas del profe
  GET /api/modelo/ejemplo        una AGEB real armada termino por termino (la escena que arma la suma)
  GET /api/fuentes               tablas de data/FUENTES.md parseadas, tamanos de data/processed y objetivos del Makefile
  GET /api/carpetas              arbol de carpetas/ con los trozos de cada archivo en data/index/chunks.parquet
  GET /api/carpetas/doc?ruta=    el Markdown de un archivo de carpetas/ (la ruta no puede salirse de carpetas/)
  GET /api/carpetas/buscar?q=    app.rag.buscar; funciona sin Ollama con el modo lexico y dice cual uso
  GET /api/descargas             lista de descargas; GET /api/descargas/<archivo>: agebs.csv (sin geometria),
                                 metricas_giro.csv e importancia.csv
"""
from __future__ import annotations

import json
import math
import re
import threading
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

router = APIRouter(prefix="/api", tags=["contexto"])

RAIZ = Path(__file__).resolve().parents[2]
PROC = RAIZ / "data" / "processed"
MODELS = RAIZ / "models"
REPORTS = RAIZ / "reports"
CARPETAS = RAIZ / "carpetas"
INDEX = RAIZ / "data" / "index" / "chunks.parquet"


# ---------------------------------------------------------------- utilidades
def _error(estado: int, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=estado, content={"error": mensaje})


def _json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _texto(ruta: Path) -> str:
    try:
        return ruta.read_text(encoding="utf-8")
    except Exception:
        return ""


def _num(x, dec: int = 0) -> str:
    """Formato es-MX para los textos que arma el servidor: 1,234.5"""
    try:
        if x is None or (isinstance(x, float) and not math.isfinite(x)):
            return "NO ENCONTRADO"
        return f"{float(x):,.{dec}f}"
    except (TypeError, ValueError):
        return "NO ENCONTRADO"


def _sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn").lower()


def _flt(x):
    """float JSON-seguro (NaN e inf salen como None)."""
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _rel(ruta: Path) -> str:
    try:
        return ruta.relative_to(RAIZ).as_posix()
    except ValueError:
        return ruta.as_posix()


# ---------------------------------------------------------------- Markdown: secciones, parrafos, vinetas
_ENCABEZADO = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def _secciones(md: str) -> list[tuple[int, str, str]]:
    """[(nivel, titulo, cuerpo)] en el orden del archivo (el cuerpo llega hasta el siguiente encabezado)."""
    out: list[tuple[int, str, list[str]]] = []
    en_codigo = False
    for ln in md.splitlines():
        if ln.lstrip().startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else _ENCABEZADO.match(ln)
        if m:
            out.append((len(m.group(1)), m.group(2), []))
        elif out:
            out[-1][2].append(ln)
    return [(n, t, "\n".join(c).strip()) for n, t, c in out]


def _seccion(md: str, titulo: str) -> str:
    """Cuerpo de la primera seccion cuyo titulo contiene `titulo` (sin importar acentos ni mayusculas)."""
    buscado = _sin_acentos(titulo)
    for _, t, cuerpo in _secciones(md):
        if buscado in _sin_acentos(t):
            return cuerpo
    return ""


def _parrafos(txt: str) -> list[str]:
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", txt) if p.strip() and not p.lstrip().startswith(("|", "```"))]


def _vinetas(txt: str) -> list[str]:
    out: list[str] = []
    for ln in txt.splitlines():
        if re.match(r"^\s*(?:[-*]|\d+\.)\s+", ln):
            out.append(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", ln).strip())
        elif out and ln.startswith("  ") and ln.strip():
            out[-1] += " " + ln.strip()
    return out


def _vineta_con(txt: str, clave: str) -> str:
    c = _sin_acentos(clave)
    return next((v for v in _vinetas(txt) if c in _sin_acentos(v)), "")


def _sin_negritas(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", s)


# ================================================================ MACRO
# clave (la `serie` del parquet) -> nombre visible, unidad, como se agrega a meses, tono de la grafica y tema para quien abre un negocio
SERIES_MACRO = {
    "tasa_objetivo": ("Tasa objetivo de Banxico", "% anual", "cierre", "naranja", "credito"),
    "tiie_28": ("TIIE a 28 días", "% anual", "promedio", "azul", "credito"),
    "tipo_cambio_fix": ("Tipo de cambio FIX", "pesos por dólar", "promedio", "naranja", "insumos"),
    "inpc_general_var_anual": ("Inflación general (INPC)", "% anual", "dato", "naranja", "costos"),
    "inpc_mercancias_var_anual": ("Inflación de mercancías", "% anual", "dato", "azul", "costos"),
    "inpc_agropecuarios_var_anual": ("Inflación de agropecuarios", "% anual", "dato", "gris", "costos"),
    "confianza_consumidor": ("Confianza del consumidor", "puntos", "dato", "naranja", "consumo"),
    "consumo_privado_var_anual": ("Consumo privado", "% anual (volumen)", "dato", "azul", "consumo"),
    "remesas": ("Remesas familiares", "millones de USD al mes", "dato", "naranja", "remesas"),
    "inpc_indice": ("INPC, índice (2018 = 100)", "índice", "dato", "gris", "costos"),
    "imcp_indice": ("Consumo privado, índice de volumen (2018 = 100)", "índice", "dato", "gris", "consumo"),
}


@lru_cache(maxsize=4)
def _series_mensuales(mtime: float) -> list[dict]:
    import pandas as pd

    df = pd.read_parquet(PROC / "macro_series.parquet")
    df["fecha"] = pd.to_datetime(df["fecha"])
    out = []
    for clave, (nombre, unidad, agrega, tono, tema) in SERIES_MACRO.items():
        g = df[df["serie"] == clave].sort_values("fecha")
        if g.empty:
            continue
        mes = g["fecha"].dt.strftime("%Y-%m")
        m = g.groupby(mes)["valor"].mean() if agrega == "promedio" else g.groupby(mes)["valor"].last()
        ult = g.iloc[-1]
        out.append({
            "clave": clave, "nombre": nombre, "unidad": unidad, "agregacion": agrega, "tono": tono, "tema": tema,
            "id_serie": str(ult["id_serie"]), "fuente": str(ult["fuente"]).replace("Banco de Mexico", "Banco de México"), "unidad_origen": str(ult["unidad"]),
            "periodicidad": "diaria (la gráfica muestra un dato por mes)" if len(g) > 1.5 * m.shape[0] else "mensual",
            "ultimo": {"fecha": ult["fecha"].date().isoformat(), "valor": _flt(ult["valor"])},
            "desde": g["fecha"].iloc[0].date().isoformat(), "n_datos": int(len(g)),
            "puntos": [[k, round(float(v), 4)] for k, v in m.items()],
        })
    return out


@router.get("/macro", response_model=None)
def macro():
    """Ultimo valor de cada indicador (macro.json, con su fecha, serie y fuente) y las series mensuales desde 2015."""
    actual = _json(PROC / "macro.json")
    meta = actual.pop("_meta", {})
    series, aviso = [], None
    f = PROC / "macro_series.parquet"
    if f.exists():
        try:
            series = _series_mensuales(f.stat().st_mtime)
        except Exception as e:  # parquet danado: la vista sigue con los KPI
            aviso = f"No pude leer macro_series.parquet ({type(e).__name__})."
    else:
        aviso = "NO ENCONTRADO: falta data/processed/macro_series.parquet. Corre `uv run python scripts/01d_macro_series.py`."
    # si la serie mensual/diaria ya trae un dato más nuevo que macro.json, el KPI usa ese (así KPI y gráfica comparten corte)
    por = {s["clave"]: s for s in series}
    for ind in actual.values():
        if isinstance(ind, dict) and isinstance(ind.get("fuente"), str):
            ind["fuente"] = ind["fuente"].replace("Banco de Mexico", "Banco de México")
    for k, ind in actual.items():
        s = por.get(k)
        if s and isinstance(ind, dict) and str(s["ultimo"]["fecha"]) > str(ind.get("fecha") or "") and s["ultimo"]["valor"] is not None:
            ind["valor"], ind["fecha"] = s["ultimo"]["valor"], s["ultimo"]["fecha"]
    return {"indicadores": actual, "series": series, "meta": meta, "aviso": aviso,
            "fuente": "Banco de México (SIE) e INEGI (BIE); consultado " + str(meta.get("generado") or "NO ENCONTRADO")}


# ================================================================ EL MODELO
TERMINOS = {
    "prob_apertura": ("Aperturas esperadas por competidor", "Cuántos negocios del giro se espera que aparezcan en el radio del sitio, repartidos entre los que ya compiten."),
    "demanda_neta": ("Gasto potencial", "Gasto de los hogares del radio en el rubro del giro (ENIGH 2024), por la parte del mercado que se llevaría un local nuevo."),
    "pob_neta": ("Población objetivo", "Residentes del cliente objetivo en el radio, ajustados al nivel socioeconómico que busca el giro y a la competencia."),
    "flujo": ("Flujo de gente", "Proxy: empleo del DENUE, corredor comercial y Metro en el radio (no hay aforos peatonales abiertos)."),
    "complementarios": ("Negocios complementarios", "Negocios que atraen al mismo cliente (por ejemplo, escuelas para una papelería), con peso por distancia."),
}
SECTORES = {
    "11": "agricultura y pesca", "21": "minería", "22": "energía y agua", "23": "construcción", "31": "industria (alimentos, bebidas, textiles)",
    "32": "industria (madera, papel, químicos)", "33": "industria (metales, maquinaria)", "43": "comercio al por mayor",
    "46": "comercio al por menor", "48": "transportes", "49": "mensajería y almacenamiento", "51": "medios e información",
    "52": "servicios financieros y seguros", "53": "servicios inmobiliarios", "54": "servicios profesionales y técnicos", "55": "corporativos",
    "56": "apoyo a negocios y residuos", "61": "servicios educativos", "62": "salud y asistencia social", "71": "esparcimiento, cultura y deporte",
    "72": "alojamiento y comida", "81": "otros servicios", "93": "gobierno",
}
VARIABLES = {
    "giro_cod": "Tipo de giro (qué negocio es)", "comp_ageb": "Competidores del giro en la misma AGEB (2020)", "comp_1km": "Competidores del giro a 1 km (2020)",
    "comp_huff": "Competencia del giro ponderada por distancia (Huff)", "compl_huff": "Negocios complementarios ponderados por distancia",
    "n_establecimientos": "Negocios de todo tipo en la AGEB", "area_km2": "Superficie de la AGEB (km²)", "pob_total": "Población total",
    "pob_0_14": "Población de 0 a 14 años", "pob_15_24": "Población de 15 a 24 años", "pob_25_59": "Población de 25 a 59 años", "pob_60_mas": "Población de 60 años o más",
    "hogares": "Hogares", "viviendas_habitadas": "Viviendas habitadas", "prom_ocupantes": "Ocupantes por vivienda", "escolaridad_prom": "Escolaridad promedio",
    "pct_viv_auto": "Viviendas con auto (%)", "pct_viv_internet": "Viviendas con internet (%)", "pct_viv_pc": "Viviendas con computadora (%)",
    "pct_viv_celular": "Viviendas con celular (%)", "pea": "Población económicamente activa", "pob_ocupada": "Población ocupada",
    "im_2020": "Índice de marginación urbana 2020", "densidad_hab_km2": "Densidad (hab/km²)", "decil_esperado": "Decil de ingreso esperado (imputado)",
    "ing_trim_mediano_est": "Ingreso trimestral mediano estimado", "p_nse_bajo": "Probabilidad de NSE bajo", "p_nse_medio": "Probabilidad de NSE medio",
    "p_nse_alto": "Probabilidad de NSE alto", "es_cdmx": "Está en la Ciudad de México", "empleo_500m": "Empleos a 500 m", "empleo_1km": "Empleos a 1 km",
    "estab_500m": "Negocios a 500 m", "estab_1km": "Negocios a 1 km", "pob_diurna": "Población diurna (empleo)", "n_escuelas_500m": "Escuelas a 500 m",
    "n_escuelas_1km": "Escuelas a 1 km", "n_hospitales_500m": "Hospitales a 500 m", "n_hospitales_1km": "Hospitales a 1 km", "n_plazas_500m": "Plazas comerciales a 500 m",
    "n_plazas_1km": "Plazas comerciales a 1 km", "dist_estacion_m": "Distancia a la estación de transporte más cercana (m)", "dist_metro_m": "Distancia al Metro (m)",
    "afluencia_metro_cercano": "Afluencia de la estación de Metro más cercana", "n_estaciones_1km": "Estaciones de transporte a 1 km",
    "afluencia_metro_1km": "Afluencia de Metro a 1 km", "giro_total_log": "Tamaño del giro en la ZMVM (logaritmo)", "radio_m": "Radio de influencia del giro (m)",
    "gasto_rubro_ageb": "Gasto potencial del rubro en la AGEB", "gasto_area": "Gasto potencial del rubro en el radio", "pob_obj_ageb": "Población objetivo en la AGEB",
    "pob_obj_area": "Población objetivo en el radio", "pob_diurna_area": "Población diurna en el radio", "nse_fit": "Ajuste al NSE objetivo del giro",
    "comp_por_10mil_obj": "Competencia por cada 10 mil personas objetivo",
}


def _nombre_variable(f: str) -> str:
    if f in VARIABLES:
        return VARIABLES[f]
    m = re.fullmatch(r"sec(\d{2})_(500m|1km)", f)
    if m:
        return f"Negocios de {SECTORES.get(m.group(1), 'sector ' + m.group(1))} a {'500 m' if m.group(2) == '500m' else '1 km'}"
    return f.replace("_", " ")


def _nombres_giros() -> dict[str, str]:
    try:
        from app.api.base import _giros_lista

        return {g["clave"]: g["nombre"] for g in _giros_lista()}
    except Exception:
        return {}


def _motor_vivo() -> dict:
    """Pesos y version del score leidos de app.motor en este momento (no de una copia)."""
    try:
        from app import motor

        return {"pesos": {k: float(v) for k, v in motor.PESOS_SCORE.items()}, "version": str(motor.SCORE_VERSION), "origen": "app/motor.py (PESOS_SCORE y SCORE_VERSION)"}
    except Exception as e:
        pj = _json(MODELS / "pesos_score.json")
        return {"pesos": pj.get("pesos", {}), "version": pj.get("version"), "origen": f"models/pesos_score.json (el motor no cargó: {type(e).__name__})"}


def _lineas_base(filas: list[dict]) -> dict:
    """En cuantos giros con datos el modelo supera a cada linea base, y los promedios (todo de metricas_giro.csv)."""
    ok = [f for f in filas if not f["poco_dato"] and f.get("auc_modelo") is not None]
    claves = {"densidad": "auc_densidad", "competencia": "auc_competencia", "comp_ageb": "auc_comp_ageb", "actividad": "auc_actividad", "score": "auc_score"}
    out: dict = {"giros": len(ok), "modelo_promedio": None, "supera": {}, "promedio": {}}
    if ok:
        out["modelo_promedio"] = sum(f["auc_modelo"] for f in ok) / len(ok)
        for k, col in claves.items():
            vals = [(f["auc_modelo"], f[col]) for f in ok if f.get(col) is not None]
            out["supera"][k] = sum(1 for a, b in vals if a > b)
            out["promedio"][k] = sum(b for _, b in vals) / len(vals) if vals else None
    return out


def _auc_por_giro() -> list[dict]:
    import pandas as pd

    try:
        m = pd.read_csv(MODELS / "metricas_giro.csv")
    except Exception:
        return []
    nombres = _nombres_giros()
    out = []
    for r in m.to_dict("records"):
        g = str(r["giro"])
        n = int(r.get("agebs_con_apertura") or 0)
        out.append({"giro": g, "nombre": nombres.get(g) or g.replace("_", " ").capitalize(), "tasa_base": _flt(r.get("tasa_base")),
                    "agebs_con_apertura": n, "poco_dato": n < 30,
                    **{c: _flt(r.get(c)) for c in ("auc_modelo", "auc_densidad", "auc_competencia", "auc_comp_ageb", "auc_actividad", "auc_score")}})
    return out


def _importancia(n: int = 20) -> list[dict]:
    import pandas as pd

    try:
        d = pd.read_csv(MODELS / "importancia.csv").sort_values("importancia_ap", ascending=False).head(n)
    except Exception:
        return []
    return [{"variable": r["feature"], "nombre": _nombre_variable(str(r["feature"])), "importancia": _flt(r["importancia_ap"]), "sd": _flt(r.get("sd"))}
            for r in d.to_dict("records")]


def _evaluacion() -> dict:
    ev = _json(REPORTS / "evaluacion.json")
    if not ev:
        return {}
    filas = [{"id": int(f.get("id") or 0), "pregunta": f.get("pregunta"), "latencia_s": _flt(f.get("latencia_s")), "pasa": bool(f.get("pasa")),
              "tipo": f.get("tipo"), "modo": f.get("modo")} for f in ev.get("filas", [])]
    return {"fecha": ev.get("fecha"), "modelo": ev.get("modelo"), "preguntas": ev.get("preguntas"), "pasan": ev.get("pasan"), "aprobado": ev.get("aprobado"),
            "trampa_pasa": ev.get("trampa_pasa"), "latencia_mediana_s": ev.get("latencia_mediana_s"), "latencia_p90_s": ev.get("latencia_p90_s"),
            "latencia_max_s": ev.get("latencia_max_s"), "mediana_bajo_objetivo": ev.get("mediana_bajo_objetivo"), "criterios": ev.get("criterios"),
            "swap_mb_max": ev.get("swap_mb_max"), "filas": filas, "fuente": "reports/evaluacion.json (eval/evaluar.py, modelo propio)"}


def _validacion_score() -> dict:
    d = _json(MODELS / "validacion_score_resumen.json")
    if not d:
        return {}
    filas = d.get("resumen", [])
    ingenuas = {"actividad", "comp_ageb", "comp_huff", "densidad", "captura_huff"}
    etiquetas = {"crecimiento_neto": "Crecimiento neto de negocios", "sobrevivencia": "Sobrevivencia de los negocios de 2020",
                 "altas_reales": "Altas fuera de la carga censal", "aperturas_crudas": "Aperturas crudas"}
    out = []
    for obj, etq in etiquetas.items():
        xs = {r["puntuacion"]: r["valor"] for r in filas if r["objetivo"] == obj}
        base = {k: v for k, v in xs.items() if k in ingenuas}
        mejor = max(base, key=base.get) if base else None
        out.append({"objetivo": obj, "etiqueta": etq, "metrica": "AUC" if obj == "aperturas_crudas" else "ρ de Spearman",
                    "vigente": _flt(xs.get("score_nuevo")), "vigente_oos": _flt(xs.get("score_nuevo_oos")), "anterior": _flt(xs.get("score_v21")),
                    "mejor_base": _flt(base.get(mejor)) if mejor else None, "mejor_base_nombre": mejor,
                    "modelo_dedicado": _flt(xs.get("prob_sobrevive")) if obj == "sobrevivencia" else (_flt(xs.get("prob_modelo")) if obj == "aperturas_crudas" else None)})
    return {"version": d.get("version"), "fecha": d.get("fecha"), "filas": out, "nse": d.get("nse"),
            "fuente": "models/validacion_score_resumen.json (scripts/03b_validar_score.py), DENUE 11/2020 y 05/2026, Censo 2020 INEGI"}


def _limites(meta: dict, giros: list[dict], vsc: dict) -> list[dict]:
    """Limites honestos: el texto sale de reports/ y carpetas/05_modelo; las cifras, de los archivos del modelo."""
    nd = "NO ENCONTRADO"
    val = _texto(REPORTS / "validacion.md")
    expl = _texto(CARPETAS / "05_modelo" / "explicacion_modelo.md")
    preg = _texto(CARPETAS / "05_modelo" / "preguntas_de_examen_del_score.md")
    et = meta.get("etiquetas") or {}
    nuevos, a2024 = et.get("nuevos"), (et.get("nuevos_por_anio_alta") or {}).get("2024")
    out = []

    aviso = _sin_negritas(_vineta_con(_seccion(val, "Qué predice"), "Aviso fuerte"))
    out.append({"clave": "aparecio", "titulo": "En el DENUE, «apareció» no es «abrió»", "texto": aviso or nd,
                "fuente": "reports/validacion.md, sección «Qué predice»; DENUE 11/2020 y 05/2026 (INEGI)",
                "cifras": [{"etiqueta": "negocios nuevos con fecha de alta 2024 (carga de los Censos Económicos)", "valor": a2024, "formato": "n"},
                           {"etiqueta": "negocios nuevos en total entre los dos cortes", "valor": nuevos, "formato": "n"}]})

    ficha = _texto(CARPETAS / "03_municipios" / "09003_coyoacan.md")
    frase = next((ln.strip() for ln in ficha.splitlines() if ln.lstrip().startswith("Colonia = el asentamiento")), "")
    try:
        import pyarrow.parquet as pq

        col = pq.read_table(PROC / "agebs_features.parquet", columns=["colonia_fuente"]).column("colonia_fuente").to_pylist()
        n_den, n_tot = sum(1 for x in col if x == "denue"), len(col)
    except Exception:
        n_den = n_tot = None
    frase = re.split(r"\s+Negocios\s*=", frase)[0] if frase else ""
    out.append({"clave": "colonia", "titulo": "La colonia es el asentamiento más frecuente de la AGEB",
                "texto": (frase + " La AGEB es la unidad del Censo y no coincide con los límites oficiales de una colonia: una colonia grande se reparte en varias AGEB.") if frase else nd,
                "fuente": "carpetas/03_municipios (ficha de cada municipio) y data/processed/agebs_features.parquet",
                "cifras": [{"etiqueta": "AGEB cuya colonia sale del DENUE (en el resto, de la localidad del Censo)", "valor": n_den, "formato": "n"},
                           {"etiqueta": "AGEB puntuadas en total", "valor": n_tot, "formato": "n"}]})

    nse = vsc.get("nse") or {}
    par = _parrafos(_seccion(preg, "confiable es el nivel socioeconómico"))
    out.append({"clave": "decil", "titulo": "El decil de ingreso está imputado, no medido", "texto": _sin_negritas(par[0]) if par else nd,
                "fuente": "carpetas/05_modelo/preguntas_de_examen_del_score.md y reports/decil_imputado.md (ENIGH 2024 aplicada al Censo 2020)",
                "cifras": [{"etiqueta": "acierto de la banda de NSE (bajo, medio o alto)", "valor": _flt(nse.get("banda_exacta")), "formato": "pct"},
                           {"etiqueta": "acierto si siempre se dijera «medio»", "valor": _flt(nse.get("mayoritaria")), "formato": "pct"},
                           {"etiqueta": "acierto del decil exacto", "valor": _flt(nse.get("decil_exacto")), "formato": "pct"}]})

    sob = meta.get("sobrevivencia") or {}
    par = _parrafos(_seccion(preg, "predecir si un negocio va a sobrevivir"))
    out.append({"clave": "sobrevivencia", "titulo": "El modelo de sobrevivencia es débil", "texto": _sin_negritas(par[0]) if par else nd,
                "fuente": "carpetas/05_modelo/preguntas_de_examen_del_score.md y models/metadata.json",
                "cifras": [{"etiqueta": "AUC del modelo de sobrevivencia (0.5 = azar)", "valor": _flt(sob.get("auc_oof")), "formato": "auc"},
                           {"etiqueta": "de los negocios de 2020 en los giros modelados siguen abiertos en 2026", "valor": _flt(sob.get("tasa_sobrevive")), "formato": "pct"}]})

    raros = _sin_negritas(_vineta_con(_seccion(expl, "Límites"), "giros raros") or _vineta_con(expl, "giros raros"))
    por = {g["giro"]: g for g in giros}
    cw, bi = por.get("coworking"), por.get("renta_bicicletas")
    out.append({"clave": "raros", "titulo": "Renta de bicicletas y coworking salen flojos", "texto": raros or nd,
                "fuente": "carpetas/05_modelo/explicacion_modelo.md, sección «Límites», y models/metricas_giro.csv",
                "cifras": [{"etiqueta": "AGEB con una apertura de renta de bicicletas", "valor": bi["agebs_con_apertura"] if bi else None, "formato": "n"},
                           {"etiqueta": "AGEB con una apertura de coworking", "valor": cw["agebs_con_apertura"] if cw else None, "formato": "n"}]})

    m = re.search(r"El score es un percentil dentro de cada giro:.*?\)\.", _sin_negritas(expl), re.S)
    out.append({"clave": "relativo", "titulo": "El score es relativo al giro", "texto": " ".join(m.group(0).split()) if m else nd,
                "fuente": "carpetas/05_modelo/explicacion_modelo.md, sección «Cómo se arma score_giro»", "cifras": []})
    flujo = _sin_negritas(_vineta_con(_seccion(expl, "Cómo se arma"), "flujo"))
    out.append({"clave": "flujo", "titulo": "El flujo de gente es un proxy", "texto": flujo or nd,
                "fuente": "carpetas/05_modelo/explicacion_modelo.md, sección «Cómo se arma score_giro»", "cifras": []})
    return out


def _qa(meta: dict, ev: dict, lb: dict) -> list[dict]:
    """«Preguntas que puede hacer el profe»: respuestas cortas, de los reportes del repo y de los numeros vivos."""
    preg = _texto(CARPETAS / "05_modelo" / "preguntas_de_examen_del_score.md")
    val = _texto(REPORTS / "validacion.md")
    fuente_pe = "carpetas/05_modelo/preguntas_de_examen_del_score.md"
    qa: list[dict] = []
    v = meta.get("validacion") or {}
    pl = [p.get("auc") for p in meta.get("pliegues", []) if p.get("auc") is not None]
    par = _parrafos(_seccion(val, "Qué predice"))
    if par:
        qa.append({"pregunta": "¿Qué predice exactamente el modelo?", "respuesta": _sin_negritas(par[0]), "fuente": "reports/validacion.md"})
    if pl and lb.get("giros"):
        qa.append({"pregunta": "¿Cómo se validó y qué tan bien funciona?",
                   "respuesta": (f"Se dejaron fuera municipios enteros (GroupKFold por municipio, {len(pl)} pliegues): el modelo se prueba en lugares que no vio al entrenar. "
                                 f"El AUC fuera de pliegue es {_num(v.get('auc_oof_global'), 3)} en global y va de {_num(min(pl), 3)} a {_num(max(pl), 3)} entre pliegues. "
                                 f"Dentro de cada giro supera a la línea base de densidad en {lb['supera'].get('densidad', 'NO ENCONTRADO')} de {lb['giros']} giros "
                                 f"(AUC medio {_num(lb['modelo_promedio'], 3)} contra {_num((lb['promedio'] or {}).get('densidad'), 3)})."),
                   "fuente": "models/metadata.json y models/metricas_giro.csv"})
    fuga = _vineta_con(_seccion(val, "Sin fuga"), "corte 11/2020")
    if fuga:
        qa.append({"pregunta": "¿Hay fuga de información (usar el futuro para predecir el pasado)?", "respuesta": _sin_negritas(fuga), "fuente": "reports/validacion.md, sección «Sin fuga de información»"})
    for titulo, q in (("por qué el score no predice aperturas crudas", "¿Por qué el score queda debajo de la competencia en AUC?"),
                      ("pesos del score los puso el autor", "¿Los pesos del score los puso usted?"),
                      ("predecir si un negocio va a sobrevivir", "¿Se puede predecir si un negocio va a sobrevivir?"),
                      ("confiable es el nivel socioeconómico", "¿Qué tan confiable es el nivel socioeconómico?"),
                      ("haría distinto con más datos", "¿Qué haría distinto con más datos?")):
        p = _parrafos(_seccion(preg, titulo))
        if p:
            qa.append({"pregunta": q, "respuesta": _sin_negritas(re.sub(r"^\*\*Respuesta corta\.\*\*\s*", "", p[0])), "fuente": fuente_pe})
    if ev:
        obj = (ev.get("criterios") or {}).get("mediana_objetivo_s")
        qa.append({"pregunta": "¿Qué tan bien responde el agente y cuánto tarda?",
                   "respuesta": (f"En la evaluación de {ev.get('preguntas')} preguntas ({ev.get('fecha')}) pasan {ev.get('pasan')}; la pregunta trampa (una ciudad fuera de la ZMVM) "
                                 f"{'pasa' if ev.get('trampa_pasa') else 'no pasa'}. Cada respuesta tarda una mediana de {_num(ev.get('latencia_mediana_s'), 1)} s "
                                 f"(p90 {_num(ev.get('latencia_p90_s'), 1)} s, máximo {_num(ev.get('latencia_max_s'), 1)} s), porque el modelo de lenguaje corre local ({ev.get('modelo')})."
                                 + (f" La mediana no cumple el objetivo de {_num(obj)} s." if ev.get("mediana_bajo_objetivo") is False and obj else "")),
                   "fuente": "reports/evaluacion.json"})
    return qa


def _mtimes() -> tuple:
    rutas = [MODELS / "metadata.json", MODELS / "metricas_giro.csv", MODELS / "importancia.csv", MODELS / "pesos_score.json", MODELS / "validacion_score_resumen.json",
             REPORTS / "evaluacion.json", REPORTS / "validacion.md", CARPETAS / "05_modelo" / "explicacion_modelo.md", CARPETAS / "05_modelo" / "preguntas_de_examen_del_score.md"]
    return tuple(r.stat().st_mtime if r.exists() else 0.0 for r in rutas)


@lru_cache(maxsize=1)
def _modelo_estatico(mtimes: tuple) -> dict:
    meta = _json(MODELS / "metadata.json")
    giros = _auc_por_giro()
    lb = _lineas_base(giros)
    ev = _evaluacion()
    vsc = _validacion_score()
    return {"meta": meta, "giros": giros, "lineas_base": lb, "evaluacion": ev, "validacion_score": vsc, "pesos_info": _json(MODELS / "pesos_score.json"),
            "limites": _limites(meta, giros, vsc), "preguntas": _qa(meta, ev, lb), "importancia": _importancia(20)}


@router.get("/modelo")
def modelo() -> dict:
    est = _modelo_estatico(_mtimes())
    meta, vivo = est["meta"], _motor_vivo()
    pesos = vivo["pesos"]
    total = sum(pesos.values()) or 1.0
    terminos = [{"clave": k, "nombre": TERMINOS.get(k, (k, ""))[0], "descripcion": TERMINOS.get(k, (k, ""))[1], "peso": float(p), "peso_norm": float(p) / total}
                for k, p in pesos.items()]
    pj = est["pesos_info"]
    v = meta.get("validacion") or {}
    return {
        "score": {"version": vivo["version"], "origen": vivo["origen"], "terminos": terminos, "suma_pesos": total,
                  "sin_redondear": pj.get("pesos_sin_redondear"), "por_pliegue": pj.get("pesos_por_pliegue"), "objetivos": pj.get("objetivos_que_aprende"),
                  "fecha": pj.get("fecha"), "origen_pesos": pj.get("origen")},
        "modelo": {"nombre": meta.get("modelo"), "sklearn": meta.get("sklearn"), "id": meta.get("modelo_id"), "fecha": meta.get("fecha"),
                   "n_variables": len(meta.get("features", [])), "n_giros": len(meta.get("giros", [])), "iteraciones": meta.get("n_iter_final"),
                   "filas_entrenamiento": meta.get("filas_entrenamiento"), "cortes": meta.get("cortes"), "segundos": meta.get("segundos")},
        "validacion": {"auc_global": v.get("auc_oof_global"), "ap_global": v.get("ap_oof_global"), "tasa_base": v.get("tasa_base_global"),
                       "pliegues": [{"pliegue": p.get("pliegue"), "auc": p.get("auc"), "n_test": p.get("n_test"), "municipios": p.get("municipios_test")} for p in meta.get("pliegues", [])],
                       "metodo": "GroupKFold por municipio (cada municipio queda entero en entrenamiento o en prueba)",
                       "fuente": "modelo propio (models/metadata.json, scripts/03_entrenar.py), DENUE 11/2020 y 05/2026, Censo 2020 INEGI"},
        "sobrevivencia": {k: (meta.get("sobrevivencia") or {}).get(k) for k in ("auc_oof", "ap_oof", "tasa_sobrevive", "n")},
        "giros": est["giros"], "lineas_base": est["lineas_base"], "importancia": est["importancia"],
        "evaluacion": est["evaluacion"], "validacion_score": est["validacion_score"],
        "limites": est["limites"], "preguntas": est["preguntas"],
        "fuentes": {"giros": "modelo propio (models/metricas_giro.csv): AUC fuera de pliegue por municipio, DENUE 11/2020 y 05/2026, Censo 2020 INEGI",
                    "importancia": "modelo propio (models/importancia.csv): importancia por permutación en un pliegue espacial"},
    }


_cache_ejemplo: dict = {}
_candado_ejemplo = threading.Lock()


@router.get("/modelo/ejemplo", response_model=None)
def modelo_ejemplo(giro: str = Query("heladeria", max_length=60), posicion: int = Query(1, ge=1, le=50)):
    """Una AGEB real del top del giro, con el percentil de cada termino, su peso y lo que aporta al score."""
    clave = (giro, posicion)
    with _candado_ejemplo:
        if clave in _cache_ejemplo:
            return _cache_ejemplo[clave]
    try:
        from app import motor

        if giro not in motor.giros():
            return _error(404, f"NO ENCONTRADO: el giro «{giro}» no está en config/giros.yaml")
        d = motor.score_giro(giro)
        if posicion > len(d):
            return _error(404, "NO ENCONTRADO: esa posición no existe")
        fila = d.iloc[posicion - 1]
        pesos = {k: float(v) for k, v in motor.PESOS_SCORE.items()}
        sin_demanda = bool(d["demanda"].isna().all())  # giro sin rubro ENIGH: el peso de la demanda pasa a la poblacion
        if sin_demanda and "demanda_neta" in pesos:
            pesos["pob_neta"] = pesos.get("pob_neta", 0.0) + pesos.pop("demanda_neta")
        tot = sum(pesos.values()) or 1.0
        terminos, acumulado = [], 0.0
        for k, p in pesos.items():
            pct = _flt(fila.get(f"pct_{k}")) or 0.0
            aporte = 100.0 * p * pct / tot
            acumulado += aporte
            terminos.append({"clave": k, "nombre": TERMINOS.get(k, (k, ""))[0], "peso": p, "peso_norm": p / tot, "percentil": pct, "aporte": aporte, "acumulado": acumulado})
        res = {"giro": giro, "nombre_giro": _nombres_giros().get(giro, giro), "posicion": posicion, "cvegeo": str(fila["cvegeo"]), "colonia": str(fila.get("nom_colonia") or ""),
               "municipio": str(fila.get("nom_mun") or ""), "score": float(fila["score"]), "suma_terminos": acumulado, "terminos": terminos,
               "sin_demanda_enigh": sin_demanda, "score_version": str(motor.SCORE_VERSION),
               "fuente": "modelo propio (app/motor.py, score_giro), Censo 2020 INEGI, DENUE corte 05/2026, ENIGH 2024"}
    except Exception as e:  # el motor no cargo: la vista sigue sin el ejemplo
        return _error(503, f"No pude calcular el ejemplo ({type(e).__name__}).")
    with _candado_ejemplo:
        _cache_ejemplo[clave] = res
    return res


def precalentar() -> None:
    """Carga el motor y calcula el ejemplo de la escena del score (lo puede llamar quien arranca el servidor en un hilo)."""
    try:
        modelo_ejemplo("heladeria", 1)
    except Exception:
        pass


# ================================================================ DATOS: fuentes
_FILA_TABLA = re.compile(r"^\s*\|(.+)\|\s*$")
_SHA = re.compile(r"`?[0-9a-f]{64}`?")


def _limpia(s: str) -> str:
    return s.strip().strip("`").strip()


def _bytes(s: str) -> int | None:
    m = re.fullmatch(r"([\d,]+)(?: bytes)?", s.strip())
    return int(m.group(1).replace(",", "")) if m else None


def _bullet_fuente(txt: str, ultima_url: str) -> dict:
    """Una vineta de FUENTES.md: `archivo` | url | descargado ... | corte | N bytes | sha256 `...` | notas."""
    campos = [c.strip() for c in txt.split(" | ")]
    fila = {"archivo": _limpia(re.sub(r"`", "", campos[0])), "url": "", "descarga": "", "corte": "", "tamano": "", "sha256": "", "nota": ""}
    resto = campos[1:]
    if resto and (resto[0].startswith(("http", ".../", "mismo")) or "/" in resto[0][:12]):
        fila["url"] = resto.pop(0)
    if fila["url"].startswith(".../") and ultima_url:
        seg = fila["url"][4:].split("/")[0]
        i = ultima_url.find("/" + seg + "/")
        if i > 0:
            fila["url"] = ultima_url[:i] + fila["url"][3:]
    notas = []
    for c in resto:
        m = re.search(r"sha256[^`]*`([0-9a-f]{64})`", c)
        if m and not fila["sha256"]:
            fila["sha256"] = m.group(1)
            extra = re.sub(r"sha256[^`]*`[0-9a-f]{64}`\s*", "", c).strip(" .;")
            if extra:
                notas.append(extra)
        elif re.fullmatch(r"[\d,]+ bytes", c) and not fila["tamano"]:
            fila["tamano"] = c
        elif re.match(r"(descargado|consultado)\b", c) and not fila["descarga"]:
            fila["descarga"] = re.sub(r"^(descargado|consultado)\s*", "", c)
        elif not fila["corte"] and not notas:
            fila["corte"] = c
        else:
            notas.append(c)
    fila["nota"] = "; ".join(notas)
    return fila


@lru_cache(maxsize=2)
def _fuentes_md(mtime: float) -> dict:
    md = _texto(RAIZ / "data" / "FUENTES.md")
    grupos: list[dict] = [{"titulo": "Fuentes de datos", "texto": [], "filas": []}]
    ultima_url = ""
    for ln in md.splitlines():
        if ln.startswith("<!--"):
            if ":fin" in ln:  # termina el bloque generado de una etapa: lo que sigue sin encabezado es de otra
                grupos.append({"titulo": "Otras descargas", "texto": [], "filas": []})
            continue
        m = re.match(r"^##\s+(.*)", ln)
        if m:
            grupos.append({"titulo": m.group(1).strip(), "texto": [], "filas": []})
            continue
        g = grupos[-1]
        t = _FILA_TABLA.match(ln)
        if t:
            celdas = [c.strip() for c in t.group(1).split("|")]
            if set("".join(celdas)) <= set("-: ") or _sin_acentos(celdas[0]).startswith("archivo"):
                continue  # separador o encabezado de la tabla
            celdas += [""] * (6 - len(celdas))
            es_sha = bool(_SHA.fullmatch(_limpia(celdas[5])))
            f = {"archivo": _limpia(celdas[0]), "url": celdas[1], "descarga": celdas[2], "corte": celdas[3], "tamano": celdas[4],
                 "sha256": _limpia(celdas[5]) if es_sha else "", "nota": "" if es_sha else celdas[5]}
        elif ln.startswith("- "):
            texto = ln[2:].strip()
            if " | " not in texto:
                g["texto"].append(texto)
                continue
            f = _bullet_fuente(texto, ultima_url)
        else:
            if ln.strip():
                g["texto"].append(ln.strip())
            continue
        f["bytes"] = _bytes(f["tamano"])
        if f["url"].startswith("http"):
            ultima_url = f["url"]
        g["filas"].append(f)
    for g in grupos:  # filas sueltas despues del bloque generado de una etapa: se nombran por la etapa que dicen sus notas
        if g["titulo"] == "Otras descargas":
            e = next((m.group(1) for f in g["filas"] for m in [re.search(r"etapa (Datos [A-Z])", f["nota"])] if m), "")
            g["titulo"] = f"Otras descargas ({e})" if e else "Otras descargas"
    grupos = [g for g in grupos if g["filas"] or g["texto"]]
    return {"secciones": grupos, "n_fuentes": sum(len(g["filas"]) for g in grupos)}


def _makefile() -> list[dict]:
    out = []
    for ln in _texto(RAIZ / "Makefile").splitlines():
        m = re.match(r"^([a-z][\w-]*):[^#\n]*##\s*(.*)$", ln)
        if m:
            out.append({"objetivo": m.group(1), "descripcion": m.group(2).strip()})
    return out


def _tamanos_procesados() -> list[dict]:
    out = []
    for d in (PROC, MODELS, RAIZ / "data" / "index"):
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    out.append({"archivo": _rel(f), "bytes": f.stat().st_size})
    return out


@router.get("/fuentes")
def fuentes() -> dict:
    f = RAIZ / "data" / "FUENTES.md"
    md = _fuentes_md(f.stat().st_mtime if f.exists() else 0.0)
    cortes = {}
    try:
        from app.api.base import cortes as _cortes

        cortes = _cortes()
    except Exception:
        pass
    tam = _tamanos_procesados()
    mk = _makefile()
    pasos = ["datos", "features", "entrenar", "indexar"]
    return {"secciones": md["secciones"], "n_fuentes": md["n_fuentes"], "cortes": cortes, "procesados": tam,
            "bytes_procesados": sum(t["bytes"] for t in tam if t["archivo"].startswith("data/processed/")),
            "reconstruir": {"comando": "make " + " ".join(pasos), "pasos": [x for p in pasos for x in mk if x["objetivo"] == p],
                            "setup": next((x for x in mk if x["objetivo"] == "setup"), None)},
            "fuente": "data/FUENTES.md (una fila por archivo descargado, con corte y sha256) y Makefile"}


# ================================================================ DATOS: carpetas
def _trozos() -> dict[str, int]:
    """Cuantos trozos tiene cada archivo en el indice (se lee solo la columna `archivo`, no los embeddings)."""
    try:
        return _trozos_cache(INDEX.stat().st_mtime)
    except Exception:
        return {}


@lru_cache(maxsize=2)
def _trozos_cache(mtime: float) -> dict[str, int]:
    import pyarrow.parquet as pq

    return dict(Counter(pq.read_table(INDEX, columns=["archivo"]).column("archivo").to_pylist()))


@lru_cache(maxsize=512)
def _titulo_md(ruta: str, mtime: float) -> str:
    for ln in _texto(Path(ruta)).splitlines()[:12]:
        m = re.match(r"^#\s+(.*)", ln)
        if m:
            return m.group(1).strip()
    return ""


def _arbol(d: Path, trozos: dict[str, int]) -> list[dict]:
    nodos = []
    for p in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name)):
        if p.name.startswith("."):
            continue
        rel = p.relative_to(CARPETAS).as_posix()
        if p.is_dir():
            hijos = _arbol(p, trozos)
            nodos.append({"nombre": p.name, "ruta": rel, "tipo": "carpeta", "hijos": hijos, "archivos": sum(h["archivos"] if h["tipo"] == "carpeta" else 1 for h in hijos),
                          "trozos": sum(h["trozos"] for h in hijos)})
        elif p.suffix.lower() == ".md":
            nodos.append({"nombre": p.name, "ruta": rel, "tipo": "archivo", "titulo": _titulo_md(str(p), p.stat().st_mtime), "bytes": p.stat().st_size, "trozos": trozos.get(rel, 0)})
    return nodos


def _descripciones() -> dict[str, str]:
    """Que contiene cada carpeta: la tabla de carpetas/README.md."""
    out = {}
    for ln in _texto(CARPETAS / "README.md").splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", ln)
        if m:
            out[m.group(1).rstrip("/")] = m.group(2)
    return out


@router.get("/carpetas", response_model=None)
def carpetas():
    if not CARPETAS.is_dir():
        return _error(404, "NO ENCONTRADO: no existe la carpeta carpetas/")
    trozos = _trozos()
    nodos = _arbol(CARPETAS, trozos)
    desc = _descripciones()
    for n in nodos:
        n["descripcion"] = desc.get(n["nombre"].rstrip("/"), "")
    n_arch = sum(n["archivos"] if n["tipo"] == "carpeta" else 1 for n in nodos)
    meta = _json(RAIZ / "data" / "index" / "meta.json")
    return {"nodos": nodos, "archivos": n_arch, "trozos": sum(trozos.values()),
            "indice": {"modelo_embeddings": meta.get("modelo_embeddings"), "dim": meta.get("dim"), "creado": meta.get("creado"), "max_chars": meta.get("max_chars")},
            "fuente": "carpetas/ y data/index/chunks.parquet (scripts/04_indexar.py)"}


def _ruta_segura(ruta: str) -> Path | None:
    """La ruta pedida, resuelta, solo si queda dentro de carpetas/ (sin `..`, rutas absolutas ni symlinks que se escapen)."""
    if not ruta or "\x00" in ruta or len(ruta) > 300:
        return None
    ruta = ruta.replace("\\", "/")
    if ruta.startswith("carpetas/"):
        ruta = ruta[len("carpetas/"):]
    base = CARPETAS.resolve()
    try:
        destino = (base / ruta).resolve()
    except (OSError, ValueError, RuntimeError):
        return None
    if destino == base or not destino.is_relative_to(base):
        return None
    return destino


@router.get("/carpetas/doc", response_model=None)
def carpetas_doc(ruta: str = Query("", max_length=300)):
    destino = _ruta_segura(ruta)
    if destino is None:
        return _error(400, "Ruta inválida: solo se pueden leer archivos dentro de carpetas/.")
    if destino.suffix.lower() != ".md":
        return _error(400, "Solo se pueden leer archivos Markdown (.md) de carpetas/.")
    if not destino.is_file():
        return _error(404, "NO ENCONTRADO: ese archivo no existe en carpetas/.")
    if destino.stat().st_size > 2_000_000:
        return _error(413, "El archivo pesa más de 2 MB.")
    rel = destino.relative_to(CARPETAS.resolve()).as_posix()
    md = destino.read_text(encoding="utf-8", errors="replace")
    return {"ruta": rel, "titulo": _titulo_md(str(destino), destino.stat().st_mtime) or destino.name, "markdown": md, "bytes": destino.stat().st_size,
            "trozos": _trozos().get(rel, 0), "fuente": f"carpetas/{rel}"}


@router.get("/carpetas/buscar", response_model=None)
def carpetas_buscar(q: str = Query("", max_length=300), k: int = Query(5, ge=1, le=10), archivo: str | None = Query(None, max_length=120)):
    q = q.strip()
    if not q:
        return _error(400, "Escribe qué quieres buscar.")
    try:
        from app import rag

        res = rag.buscar(q, k=k, archivo=archivo or None)
    except FileNotFoundError:
        return _error(503, "NO ENCONTRADO: falta el índice (data/index/chunks.parquet). Corre `make indexar`.")
    except Exception as e:
        return _error(503, f"No pude buscar ({type(e).__name__}).")
    modo = res[0]["modo"] if res else None
    return {"q": q, "modo": modo, "k": k,
            "aviso": ("Ollama no respondió: se buscó por palabras (modo léxico), no por significado." if modo == "lexico" else None),
            "resultados": [{"archivo": r["archivo"], "seccion": r["seccion"], "texto": r["texto"], "score": _flt(r["score"]), "municipio": r.get("municipio") or ""} for r in res],
            "fuente": "carpetas/ indexadas con nomic-embed-text (data/index/chunks.parquet)"}


# ================================================================ DATOS: descargas
@lru_cache(maxsize=2)
def _agebs_csv(mtime: float) -> bytes:
    import pandas as pd

    d = pd.read_parquet(PROC / "agebs_features.parquet")
    d = d.drop(columns=[c for c in ("geometry", "geom", "geometria") if c in d.columns])
    return d.to_csv(index=False).encode("utf-8-sig")  # con BOM: Excel abre bien los acentos


DESCARGAS = {
    "agebs.csv": ("Una fila por AGEB (Censo 2020, DENUE, ENIGH, CONAPO), todas las variables, sin geometría", PROC / "agebs_features.parquet"),
    "metricas_giro.csv": ("AUC y precisión por giro: modelo, líneas base y score", MODELS / "metricas_giro.csv"),
    "importancia.csv": ("Importancia de variables por permutación", MODELS / "importancia.csv"),
}


@router.get("/descargas")
def descargas() -> dict:
    out = []
    for nombre, (desc, f) in DESCARGAS.items():
        out.append({"archivo": nombre, "descripcion": desc, "ruta": f"/api/descargas/{nombre}", "origen": _rel(f), "disponible": f.exists()})
    return {"descargas": out}


@router.get("/descargas/{nombre}", response_model=None)
def descarga(nombre: str):
    if nombre not in DESCARGAS:
        return _error(404, "NO ENCONTRADO: esa descarga no existe.")
    f = DESCARGAS[nombre][1]
    if not f.exists():
        return _error(404, f"NO ENCONTRADO: falta {_rel(f)}.")
    cuerpo = _agebs_csv(f.stat().st_mtime) if nombre == "agebs.csv" else f.read_bytes()
    return Response(cuerpo, media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{nombre}"', "Cache-Control": "no-cache"})
