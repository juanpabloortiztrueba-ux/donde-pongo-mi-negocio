"""Router de las vistas Explorar y Comparar giros del tablero.

Dueno: el constructor del grupo «explorar».

    GET /api/variables                  lista curada de variables por AGEB (etiqueta, unidad, fuente, descripcion)
    GET /api/mapa?variable=&municipio=  valores por cvegeo, cuantiles, resumen por municipio e histograma
    GET /api/scores/{giro}?municipio=   score y componentes por cvegeo (motor.score_giro)
    GET /api/comparar?giros=a,b,c       metricas y top 10 por giro (1 a 4 giros; la vista usa de 2 a 4)
    GET /api/denue/{giro}?municipio=&max=5000   puntos de la competencia, muestreados si son muchos
    GET /api/sugerir?municipio=&nse=&ticket_max=   herramientas.sugerir_giros
    GET /api/transporte                 estaciones de transporte masivo

Todo lo pesado (features, DENUE por giro, scores) se carga perezosamente y queda en cache; el arranque no lee datos.
Las cifras salen de data/processed, models/ y de motor/herramientas (validados); aqui no se escribe ninguna a mano.
"""
from __future__ import annotations

import math
import threading
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api import base

RAIZ = Path(__file__).resolve().parents[2]
PROC = RAIZ / "data" / "processed"
MODELS = RAIZ / "models"
router = APIRouter(prefix="/api", tags=["explorar"])
_candado = threading.Lock()

NO = "NO ENCONTRADO"
F_CENSO = "Censo 2020 INEGI"
F_CONAPO = "CONAPO 2020, índice de marginación urbana"
F_DECIL = "modelo propio: decil imputado con ENIGH 2024 y Censo 2020"
F_TRANSP = "datos.cdmx.gob.mx y OpenStreetMap, cálculo propio"
F_METRO = "STC Metro, afluencia 2025 (datos.cdmx.gob.mx)"
F_MODELO = "modelo propio (models/scores_giros.parquet)"


def _error(estado: int, mensaje: str, **extra) -> JSONResponse:
    return JSONResponse(status_code=estado, content={"error": mensaje, **extra})


def _quita_acentos(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


# ---------------------------------------------------------------- variables curadas
# agregacion: suma | razon (num/den * factor) | media_pond (peso) | media. `col` es la columna de agebs_features.parquet.
VARIABLES: list[dict] = [
    {"clave": "pob_total", "etiqueta": "Población", "unidad": "habitantes", "grupo": "Gente", "col": "pob_total", "formato": "num", "dec": 0,
     "agregacion": "suma", "fuente": F_CENSO, "descripcion": "Habitantes que el Censo 2020 contó en la AGEB."},
    {"clave": "densidad", "etiqueta": "Densidad de población", "unidad": "hab/km²", "grupo": "Gente", "col": "densidad_hab_km2", "formato": "num", "dec": 0,
     "agregacion": "razon", "num": "pob_total", "den": "area_km2", "factor": 1.0, "fuente": F_CENSO,
     "descripcion": "Habitantes por kilómetro cuadrado de la AGEB. Donde hay más gente por metro cuadrado, hay más clientes cerca."},
    {"clave": "pct_0_14", "etiqueta": "Niñas y niños (0 a 14 años)", "unidad": "% de la población", "grupo": "Gente", "formato": "pct", "dec": 1,
     "agregacion": "razon", "num": "pob_0_14", "den": "pob_total", "factor": 100.0, "fuente": F_CENSO,
     "descripcion": "Porcentaje de la población que tiene de 0 a 14 años. Pesa en giros como heladerías, papelerías o guarderías."},
    {"clave": "pct_60_mas", "etiqueta": "Personas de 60 años o más", "unidad": "% de la población", "grupo": "Gente", "formato": "pct", "dec": 1,
     "agregacion": "razon", "num": "pob_60_mas", "den": "pob_total", "factor": 100.0, "fuente": F_CENSO,
     "descripcion": "Porcentaje de la población de 60 años o más. Pesa en farmacias, consultorios y servicios de salud."},
    {"clave": "escolaridad", "etiqueta": "Escolaridad promedio", "unidad": "años de estudio", "grupo": "Gente", "col": "escolaridad_prom", "formato": "num", "dec": 1,
     "agregacion": "media_pond", "peso": "pob_total", "fuente": F_CENSO,
     "descripcion": "Años promedio de estudio de las personas de 15 años o más. Se promedia con peso en habitantes."},
    {"clave": "pct_viv_auto", "etiqueta": "Viviendas con automóvil", "unidad": "% de viviendas", "grupo": "Hogares", "col": "pct_viv_auto", "formato": "pct", "dec": 1,
     "agregacion": "media_pond", "peso": "viviendas_habitadas", "fuente": F_CENSO,
     "descripcion": "Porcentaje de viviendas particulares habitadas con al menos un automóvil. Indica si el cliente llega manejando o caminando."},
    {"clave": "pct_viv_internet", "etiqueta": "Viviendas con internet", "unidad": "% de viviendas", "grupo": "Hogares", "col": "pct_viv_internet", "formato": "pct", "dec": 1,
     "agregacion": "media_pond", "peso": "viviendas_habitadas", "fuente": F_CENSO,
     "descripcion": "Porcentaje de viviendas particulares habitadas con internet."},
    {"clave": "pct_viv_pc", "etiqueta": "Viviendas con computadora", "unidad": "% de viviendas", "grupo": "Hogares", "col": "pct_viv_pc", "formato": "pct", "dec": 1,
     "agregacion": "media_pond", "peso": "viviendas_habitadas", "fuente": F_CENSO,
     "descripcion": "Porcentaje de viviendas con computadora, laptop o tablet."},
    {"clave": "grado_marginacion", "etiqueta": "Grado de marginación", "unidad": "1 = muy bajo, 5 = muy alto", "grupo": "Bienestar", "col": "gm_2020", "formato": "ordinal", "dec": 1,
     "agregacion": "media_pond", "peso": "pob_total", "fuente": F_CONAPO, "ordinal": ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"],
     "descripcion": "Grado de marginación urbana de CONAPO, de muy bajo (1) a muy alto (5). En municipios y alcaldías se promedia con peso en habitantes."},
    {"clave": "indice_marginacion", "etiqueta": "Índice de marginación", "unidad": "puntos del índice", "grupo": "Bienestar", "col": "im_2020", "formato": "num", "dec": 1,
     "agregacion": "media_pond", "peso": "pob_total", "fuente": F_CONAPO,
     "descripcion": "Índice de marginación urbana de CONAPO. En estos datos un valor más alto va con menor marginación (los grados «muy bajo» tienen el índice más alto)."},
    {"clave": "decil", "etiqueta": "Decil de ingreso estimado", "unidad": "decil (1 = más pobre, 10 = más rico)", "grupo": "Bienestar", "col": "decil_imputado", "formato": "decil", "dec": 1,
     "agregacion": "media_pond", "peso": "hogares", "fuente": F_DECIL,
     "descripcion": "Decil de ingreso del hogar típico de la AGEB, dentro de la ZMVM. Es una estimación del proyecto (el Censo no trae ingreso), no un dato medido."},
    {"clave": "ingreso_trim", "etiqueta": "Ingreso trimestral estimado del hogar", "unidad": "pesos por trimestre", "grupo": "Bienestar", "col": "ing_trim_mediano_est", "formato": "pesos", "dec": 0,
     "agregacion": "media_pond", "peso": "hogares", "fuente": F_DECIL,
     "descripcion": "Ingreso corriente trimestral mediano estimado por hogar, en pesos de 2024. Es una estimación del proyecto."},
    {"clave": "empleo_1km", "etiqueta": "Empleo a 1 km", "unidad": "personas ocupadas", "grupo": "Economía", "col": "empleo_1km", "formato": "num", "dec": 0,
     "agregacion": "media_pond", "peso": "pob_total", "fuente": "DENUE", "fuente_corte": True,
     "descripcion": "Personas que trabajan en los negocios del DENUE a 1 km del centro de la AGEB (punto medio del estrato de personal ocupado). Mide el movimiento diurno."},
    {"clave": "comercio_1km", "etiqueta": "Comercio al por menor a 1 km", "unidad": "negocios", "grupo": "Economía", "col": "sec46_1km", "formato": "num", "dec": 0,
     "agregacion": "media_pond", "peso": "pob_total", "fuente": "DENUE", "fuente_corte": True,
     "descripcion": "Negocios de comercio al por menor (sector SCIAN 46) a 1 km del centro de la AGEB. Mide qué tan comercial es la zona."},
    {"clave": "dist_estacion", "etiqueta": "Distancia a una estación de transporte masivo", "unidad": "metros", "grupo": "Transporte", "col": "dist_estacion_m", "formato": "num", "dec": 0,
     "agregacion": "media_pond", "peso": "pob_total", "fuente": F_TRANSP,
     "descripcion": "Metros en línea recta del centro de la AGEB a la estación más cercana de Metro, Metrobús, Tren Ligero, Mexibús, Cablebús u otro sistema."},
    {"clave": "afluencia_metro", "etiqueta": "Afluencia del Metro cercano", "unidad": "entradas al año", "grupo": "Transporte", "col": "afluencia_metro_cercano", "formato": "compacto", "dec": 0,
     "agregacion": "media", "fuente": F_METRO,
     "descripcion": "Entradas de 2025 a la estación de Metro más cercana. Es un proxy de flujo peatonal, porque no hay aforos peatonales abiertos para la ZMVM."},
]
POR_CLAVE = {v["clave"]: v for v in VARIABLES}
AGREGACION_TEXTO = {
    "suma": "suma de las AGEB", "razon": "cociente entre los totales de las AGEB", "media_pond": "promedio ponderado",
    "media": "promedio simple de las AGEB",
}
PESO_TEXTO = {"pob_total": "habitantes", "viviendas_habitadas": "viviendas", "hogares": "hogares"}
GM_ORDEN = {"Muy bajo": 1, "Bajo": 2, "Medio": 3, "Alto": 4, "Muy alto": 5}


@lru_cache(maxsize=1)
def _features() -> pd.DataFrame:
    """Columnas de agebs_features que usan las variables (sin la geometria), indexadas por cvegeo."""
    import pyarrow.parquet as pq

    cols = {"cvegeo", "nom_mun", "nom_colonia", "cve_ent", "cve_mun", "area_km2", "pob_total", "viviendas_habitadas", "hogares"}
    for v in VARIABLES:
        for k in ("col", "num", "den", "peso"):
            if v.get(k):
                cols.add(v[k])
    ya = set(pq.read_schema(PROC / "agebs_features.parquet").names)
    f = pd.read_parquet(PROC / "agebs_features.parquet", columns=sorted(cols & ya))
    f["cvegeo_mun"] = f["cve_ent"].astype(str) + f["cve_mun"].astype(str)
    return f.set_index("cvegeo")


def _fuente(v: dict) -> str:
    if v.get("fuente_corte"):
        return f"DENUE corte {base.cortes().get('denue_actual') or NO}"
    return v["fuente"]


def _meta(v: dict) -> dict:
    out = {k: v[k] for k in ("clave", "etiqueta", "unidad", "grupo", "formato", "descripcion")}
    out["decimales"] = v["dec"]
    out["fuente"] = _fuente(v)
    ag = AGREGACION_TEXTO[v["agregacion"]]
    if v["agregacion"] == "media_pond":
        ag += f" por {PESO_TEXTO.get(v['peso'], v['peso'])}"
    out["agregacion"] = v["agregacion"]
    out["agregacion_texto"] = ag
    if v.get("ordinal"):
        out["etiquetas_ordinal"] = {str(i + 1): n for i, n in enumerate(v["ordinal"])}
    return out


def _disponible(v: dict, f: pd.DataFrame) -> bool:
    if v.get("col"):
        return v["col"] in f.columns
    return v.get("num") in f.columns and v.get("den") in f.columns


@router.get("/variables")
def variables() -> dict:
    """Variables curadas con su etiqueta, unidad, fuente y descripcion. Solo las que existen en agebs_features."""
    f = _features()
    ok = [v for v in VARIABLES if _disponible(v, f)]
    return {"variables": [_meta(v) for v in ok], "grupos": list(dict.fromkeys(v["grupo"] for v in ok)),
            "fuente": "data/processed/agebs_features.parquet (Censo 2020 INEGI, CONAPO 2020, DENUE, modelo propio)"}


def _serie(v: dict) -> pd.Series:
    """Valor de la variable por AGEB (NaN donde no hay dato)."""
    f = _features()
    if not v.get("col"):  # cociente de dos columnas
        den = f[v["den"]].where(f[v["den"]] > 0)
        s = f[v["num"]] / den * v["factor"]
    elif v["clave"] == "grado_marginacion":
        s = f["gm_2020"].map(GM_ORDEN).astype(float)
    else:
        s = f[v["col"]].astype(float)
    if v["clave"] == "escolaridad":
        s = s.where(s > 0)
    if v["clave"] in ("pct_viv_auto", "pct_viv_internet", "pct_viv_pc"):
        s = s.where(f["viviendas_habitadas"] > 0)
    if v["clave"] == "densidad":
        s = s.where(f["pob_total"] > 0)
    return s.replace([np.inf, -np.inf], np.nan)


def _r(x, nd: int = 4):
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return round(x, nd) if math.isfinite(x) else None


def _agregar(v: dict, idx: pd.Index) -> float | None:
    """Valor de la variable para un conjunto de AGEB (un municipio o toda la ZMVM), segun su regla de agregacion."""
    f = _features().loc[idx]
    s = _serie(v).loc[idx]
    ag = v["agregacion"]
    if ag == "suma":
        r = s.sum(min_count=1)
    elif ag == "razon":
        num, den = f[v["num"]], f[v["den"]]
        ok = num.notna() & den.notna()
        d = den[ok].sum()
        r = num[ok].sum() / d * v["factor"] if d > 0 else np.nan
    elif ag == "media_pond":
        w = f[v["peso"]].fillna(0)
        ok = s.notna() & (w > 0)
        r = (s[ok] * w[ok]).sum() / w[ok].sum() if ok.any() else np.nan
    else:
        r = s.mean()
    return _r(r, v["dec"] + 2)


def _municipio_valido(municipio: str | None) -> tuple[str | None, JSONResponse | None]:
    if not municipio:
        return None, None
    m = str(municipio).strip()
    if m not in {x["cvegeo_mun"] for x in base._municipios_lista()}:
        return None, _error(422, f"municipio «{m}» no es una clave de 5 dígitos de la ZMVM (usa /api/municipios)")
    return m, None


@router.get("/mapa")
def mapa(variable: str = "densidad", municipio: str | None = None):
    v = POR_CLAVE.get(variable)
    if v is None:
        return _error(404, f"variable «{variable}» no existe", variables=[x["clave"] for x in VARIABLES])
    mun, err = _municipio_valido(municipio)
    if err:
        return err
    f = _features()
    if not _disponible(v, f):
        return _error(404, f"{NO}: la columna de «{variable}» no está en agebs_features.parquet")
    s = _serie(v)
    en = f.index if mun is None else f.index[f["cvegeo_mun"] == mun]
    sf = s.loc[en].dropna()
    if sf.empty:
        return _error(404, f"{NO}: la variable no tiene datos en ese filtro")
    dec = v["dec"] + (1 if v["formato"] in ("pct", "num") and v["dec"] < 2 else 0)
    valores = {cv: round(float(x), dec) for cv, x in s.dropna().items()}
    ordinal = v["formato"] in ("ordinal", "decil")
    if v["clave"] == "grado_marginacion":
        dominio = [1.0, 5.0]
    elif v["clave"] == "decil":
        dominio = [1.0, 10.0]
    else:
        lo, hi = float(np.percentile(sf, 2)), float(np.percentile(sf, 98))
        if not hi > lo:
            lo, hi = float(sf.min()), float(sf.max())
        if not hi > lo:
            lo, hi = lo - 1, hi + 1
        dominio = [round(lo, 4), round(hi, 4)]
    cuantiles = [{"p": q, "valor": _r(np.quantile(sf, q), v["dec"] + 2)} for q in (0, 0.2, 0.4, 0.6, 0.8, 1.0)]

    # histograma: 24 cajas entre los percentiles 2 y 98 (los extremos se juntan en las cajas de las orillas); ordinales, una por valor
    if ordinal:
        k = 5 if v["clave"] == "grado_marginacion" else 10
        cuenta = np.bincount(np.clip(np.round(sf.to_numpy()).astype(int), 1, k), minlength=k + 1)[1:]
        cajas = [{"x0": i + 0.5, "x1": i + 1.5, "n": int(cuenta[i]), "etiqueta": (v["ordinal"][i] if v.get("ordinal") else str(i + 1))}
                 for i in range(k)]
        extremos = 0
    else:
        edges = np.linspace(dominio[0], dominio[1], 25)
        cuenta, _ = np.histogram(np.clip(sf.to_numpy(), dominio[0], dominio[1]), bins=edges)
        cajas = [{"x0": _r(edges[i], v["dec"] + 3), "x1": _r(edges[i + 1], v["dec"] + 3), "n": int(cuenta[i])} for i in range(24)]
        extremos = int(((sf < dominio[0]) | (sf > dominio[1])).sum())

    # resumen por municipio (siempre los 76, para poder comparar y elegir)
    nombres = {m["cvegeo_mun"]: m["nombre"] for m in base._municipios_lista()}
    filas = []
    for cvm, idx in f.groupby("cvegeo_mun").groups.items():
        ss = s.loc[idx].dropna()
        filas.append({"cvegeo_mun": cvm, "municipio": nombres.get(cvm, cvm), "n_agebs": int(len(idx)), "n_con_dato": int(len(ss)),
                      "poblacion": int(f.loc[idx, "pob_total"].sum()), "valor": _agregar(v, idx),
                      "mediana": _r(ss.median(), v["dec"] + 2) if len(ss) else None})
    filas.sort(key=lambda r: (r["valor"] is None, -(r["valor"] or 0)))

    def donde(i):
        col = f.at[i, "nom_colonia"]
        return {"cvegeo": i, "colonia": col if isinstance(col, str) else None, "municipio": f.at[i, "nom_mun"], "valor": _r(s.at[i], v["dec"] + 2)}

    resumen = {"n_agebs": int(len(en)), "n_con_dato": int(len(sf)), "poblacion": int(f.loc[en, "pob_total"].sum()),
               "valor": _agregar(v, en), "mediana": _r(sf.median(), v["dec"] + 2), "minimo": donde(sf.idxmin()), "maximo": donde(sf.idxmax()),
               "ambito": nombres.get(mun) if mun else "Toda la ZMVM"}
    return {"variable": _meta(v), "municipio": mun, "valores": valores, "dominio": dominio, "cuantiles": cuantiles,
            "resumen": resumen, "municipios": filas,
            "histograma": {"cajas": cajas, "dominio": dominio, "valores_en_extremos": extremos, "n": int(len(sf))},
            "fuente": _fuente(v)}


# ---------------------------------------------------------------- scores por giro
def _clave_giro(giro: str) -> str | None:
    from app import motor

    g = (giro or "").strip().lower()
    claves = motor.giros()
    if g in claves:
        return g
    g = _quita_acentos(g).replace(" ", "_")
    return g if g in claves else None


@lru_cache(maxsize=12)
def _score(clave: str) -> pd.DataFrame:
    from app import motor

    d = motor.score_giro(clave).copy()
    d["cvegeo_mun"] = d["cvegeo"].str[:5]
    if "prob_sobrevive" in d.columns:
        d["viabilidad"] = d["prob_apertura"] * d["prob_sobrevive"]
    return d


COMPONENTES = ["prob_apertura", "prob_sobrevive", "viabilidad", "aperturas_esperadas", "demanda", "competencia", "captura_huff",
               "complementarios", "flujo", "pob_neta", "demanda_neta", "residentes_objetivo", "empleo_radio"]


@router.get("/scores/{giro}")
def scores(giro: str, municipio: str | None = None, componentes: bool = True):
    clave = _clave_giro(giro)
    if clave is None:
        return _error(404, f"{NO}: el giro «{giro}» no está en config/giros.yaml")
    mun, err = _municipio_valido(municipio)
    if err:
        return err
    d = _score(clave)
    if mun:
        d = d[d["cvegeo_mun"] == mun]
    d = d.sort_values("score", ascending=False)
    nombre = next((g["nombre"] for g in base._giros_lista() if g["clave"] == clave), clave)
    out = {"giro": clave, "nombre": nombre, "municipio": mun, "n": int(len(d)),
           "scores": {cv: round(float(x), 2) for cv, x in zip(d["cvegeo"], d["score"])},
           "como_leer": ("el score 0–100 es un percentil dentro de este giro: ordena las AGEB para este giro, "
                         "no dice si el giro es viable ni sirve para comparar giros"),
           "fuente": F_MODELO}
    if "score_version" in d.columns and len(d):
        out["score_version"] = str(d["score_version"].iloc[0])
    if componentes:
        cols = [c for c in COMPONENTES if c in d.columns]
        out["cvegeo"] = d["cvegeo"].tolist()
        out["componentes"] = {c: [_r(x, 4) for x in d[c]] for c in cols}
    return out


# ---------------------------------------------------------------- DENUE por giro
@lru_cache(maxsize=48)
def _denue_giro(clave: str, corte: str = "actual") -> pd.DataFrame:
    """Establecimientos del giro (misma regla que motor.seleccionar), sin cargar los 1.08 millones de filas completas."""
    from app import motor

    g = motor.giros()[clave]
    scian = [str(c) for c in g.get("scian", [])]
    filtros = g.get("scian_con_filtro")
    codigos = sorted(set(scian) | {str(c) for f in (filtros or []) for c in f["codigos"]})
    col = "codigo_act" if corte == "actual" else "codigo_act_actual"
    cols = ["id", "nombre", col, "cvegeo_mun", "cvegeo", "lat", "lon"]
    archivo = PROC / f"denue_{corte}.parquet"
    if all(len(c) == 6 for c in codigos):
        df = pd.read_parquet(archivo, columns=cols, filters=[(col, "in", codigos)])
    else:  # algun codigo corto (prefijo): se lee todo y motor.seleccionar filtra
        df = pd.read_parquet(archivo, columns=cols)
    df = df.rename(columns={col: "codigo"})
    df = df[df["lat"].notna() & df["lon"].notna() & df["codigo"].notna()]
    return motor.seleccionar(df, scian, filtros).reset_index(drop=True)


@router.get("/denue/{giro}")
def denue(giro: str, municipio: str | None = None, max: int = 5000):
    clave = _clave_giro(giro)
    if clave is None:
        return _error(404, f"{NO}: el giro «{giro}» no está en config/giros.yaml")
    mun, err = _municipio_valido(municipio)
    if err:
        return err
    tope = min(max if max and max > 0 else 5000, 20000)
    d = _denue_giro(clave)
    if mun:
        d = d[d["cvegeo_mun"] == mun]
    total = int(len(d))
    muestreado = total > tope
    if muestreado:  # muestra fija (misma semilla): el mapa no cambia entre visitas
        d = d.iloc[np.sort(np.random.default_rng(7).choice(total, size=tope, replace=False))]
    puntos = [[round(float(lo), 5), round(float(la), 5), n if isinstance(n, str) else ""]
              for lo, la, n in zip(d["lon"], d["lat"], d["nombre"])]
    return {"giro": clave, "municipio": mun, "total": total, "mostrados": int(len(puntos)), "muestreado": muestreado,
            "columnas": ["lon", "lat", "nombre"], "puntos": puntos,
            "fuente": f"DENUE corte {base.cortes().get('denue_actual') or NO}"}


# ---------------------------------------------------------------- comparar giros
@lru_cache(maxsize=1)
def _metricas_giro() -> pd.DataFrame:
    return pd.read_csv(MODELS / "metricas_giro.csv").set_index("giro")


def _top_zonas(clave: str, n: int = 10) -> tuple[list[dict], dict]:
    from app import herramientas

    r = herramientas.recomendar_zonas(clave, top=n, una_por_colonia=True)
    if not r.get("encontrado"):
        return [], {}
    zonas = [{"posicion": i + 1, "ageb": z["ageb"], "colonia": z["colonia"], "municipio": z["municipio"], "score": z["score"],
              "prob_apertura_pct": z["prob_apertura_pct"], "prob_sigue_abierto_pct": z.get("prob_sigue_abierto_pct"),
              "competidores_ponderados": z.get("competidores_ponderados"), "nse_estimado": z.get("nse_estimado"),
              "residentes_objetivo_en_radio": z.get("residentes_objetivo_en_radio")} for i, z in enumerate(r["zonas"])]
    avisos = {k: r[k] for k in ("como_leer_score", "aviso_prob_baja") if r.get(k)}
    return zonas, avisos


@lru_cache(maxsize=48)
def _giro_comparado(clave: str) -> dict:
    from app import motor

    g = motor.giros()[clave]
    d = _score(clave)
    m = _metricas_giro()
    fila = m.loc[clave] if clave in m.index else None
    nombres = {x["cvegeo_mun"]: x["nombre"] for x in base._municipios_lista()}
    # mejor municipio: mayor score medio entre los que tienen >= 10 AGEB (el score es relativo al giro, y esto tambien)
    por = d.groupby("cvegeo_mun").agg(n=("score", "size"), score=("score", "mean"), prob=("prob_apertura", "mean"))
    por = por[por["n"] >= 10]
    mejor = None
    if len(por):
        c = por["score"].idxmax()
        mejor = {"cvegeo_mun": c, "municipio": nombres.get(c, c), "score_medio": _r(por.at[c, "score"], 1),
                 "prob_apertura_media_pct": _r(100 * por.at[c, "prob"], 1), "n_agebs": int(por.at[c, "n"]),
                 "criterio": "mayor score medio de sus AGEB, entre municipios con al menos 10 AGEB"}
    top, avisos = _top_zonas(clave, 10)
    pa = float(d["prob_apertura"].mean())
    ps = float(d["prob_sobrevive"].mean()) if "prob_sobrevive" in d.columns else None
    via = float(d["viabilidad"].mean()) if "viabilidad" in d.columns else None
    nombre = next((x["nombre"] for x in base._giros_lista() if x["clave"] == clave), clave)
    return {
        "clave": clave, "nombre": nombre,
        "negocios_denue": int(len(_denue_giro(clave, "actual"))),
        "negocios_denue_hist": int(len(_denue_giro(clave, "hist"))),
        "aperturas": int(fila["aperturas"]) if fila is not None and pd.notna(fila["aperturas"]) else None,
        "agebs_con_apertura": int(fila["agebs_con_apertura"]) if fila is not None else None,
        "auc": _r(fila["auc_modelo"], 3) if fila is not None else None,
        "tasa_base_pct": _r(100 * fila["tasa_base"], 1) if fila is not None else None,
        "prob_apertura_media_pct": _r(100 * pa, 1),
        "prob_sigue_abierto_media_pct": _r(100 * ps, 1) if ps is not None else None,
        "viabilidad_media_pct": _r(100 * via, 1) if via is not None else None,
        "mejor_municipio": mejor,
        "ticket_promedio_mxn": g.get("ticket_promedio_mxn"), "radio_influencia_m": g.get("radio_influencia_m"),
        "top": top, "avisos": avisos,
    }


@router.get("/comparar")
def comparar(giros: str = ""):
    claves, malos = [], []
    for g in [x for x in giros.split(",") if x.strip()]:
        c = _clave_giro(g)
        if c:
            claves.append(c)
        else:
            malos.append(g.strip())
    claves = list(dict.fromkeys(claves))
    if malos:
        return _error(404, f"{NO}: giros que no están en config/giros.yaml: {', '.join(malos)}")
    if not claves or len(claves) > 4:
        return _error(422, "elige de 1 a 4 giros (a,b,c,d) para comparar")
    cortes = base.cortes()
    return {"giros": [_giro_comparado(c) for c in claves],
            "notas": {
                "score": "el score 0–100 es un percentil dentro de cada giro: no sirve para comparar giros entre sí",
                "viabilidad": "viabilidad = prob. de apertura × prob. de seguir abierto (absolutas, misma ventana y misma unidad: la AGEB)",
                "prob_sigue_abierto": "viene de un modelo débil (ver «El modelo»): úsala para ordenar, no como cifra exacta",
                "aperturas": "«aparecieron en el DENUE» entre 11/2020 y 05/2026; parte puede ser cobertura de los Censos Económicos"},
            "fuentes": {"negocios_denue": f"DENUE corte {cortes.get('denue_actual') or NO}",
                        "negocios_denue_hist": f"DENUE corte {cortes.get('denue_hist') or NO}",
                        "modelo": "modelo propio (models/metricas_giro.csv y models/scores_giros.parquet)",
                        "ticket_y_radio": "config/giros.yaml (supuestos del proyecto)"}}


# ---------------------------------------------------------------- sugerir y transporte
@router.get("/sugerir")
def sugerir(municipio: str | None = None, nse: str | None = None, ticket_max: float | None = None, top: int = 10,
            inversion: str | None = None):
    from app import herramientas

    mun = municipio.strip() if municipio and municipio.strip() else None
    if mun and mun.isdigit():
        mun, err = _municipio_valido(mun)
        if err:
            return err
    if nse and _quita_acentos(nse).lower() not in ("bajo", "medio", "alto"):
        return _error(422, "nse debe ser bajo, medio o alto")
    args = {"municipio": mun, "nse": _quita_acentos(nse).lower() if nse else None, "ticket_max": ticket_max or None,
            "top": max(1, min(int(top), 10)), "inversion": inversion or None}
    with _candado:  # la herramienta carga el parquet completo de scores la primera vez
        r = herramientas.ejecutar("sugerir_giros", args)
    if r.get("error"):
        return _error(500, r["error"])
    nombres = {g["clave"]: g["nombre"] for g in base._giros_lista()}
    for fila in r.get("giros") or []:
        fila["nombre"] = nombres.get(fila["giro"], fila["giro"])
    # «Cómo se calcula» se muestra tal cual: es-MX y sin identificadores internos (la herramienta no se toca)
    for k in ("metodo", "como_leer"):
        if isinstance(r.get(k), str):
            for a, b in ((">= 1 negocio", "al menos 1 negocio"), ("con nse se exige peso >= 0.3 en nse_objetivo", "con NSE se exige un peso de al menos 0.3 en el NSE objetivo del giro"),
                         ("ticket es supuesto", "el ticket es un supuesto"), ("modelo debil", "modelo débil"), (" x prob.", " × prob.")):
                r[k] = r[k].replace(a, b)
    return r


@router.get("/transporte")
def transporte(solo_operando: bool = True):
    t = pd.read_parquet(PROC / "transporte.parquet")
    t["operando"] = t["estado"].fillna("").astype(str).str.startswith(("operando", "servicio temporal"))
    if solo_operando:
        t = t[t["operando"]]
    out = []
    for r in t.itertuples():
        if not (math.isfinite(r.lat) and math.isfinite(r.lon)):
            continue
        out.append({"sistema": r.sistema, "linea": None if pd.isna(r.linea) else str(r.linea), "estacion": r.estacion,
                    "lat": round(float(r.lat), 5), "lon": round(float(r.lon), 5),
                    "afluencia_anual": None if pd.isna(r.afluencia_anual) else int(r.afluencia_anual),
                    "anio_afluencia": None if pd.isna(r.anio_afluencia) else int(r.anio_afluencia),
                    "estado": r.estado})
    return {"estaciones": out, "n": len(out), "sistemas": sorted({e["sistema"] for e in out}),
            "fuente": "datos.cdmx.gob.mx (Metro, Metrobús, STE, GTFS) y OpenStreetMap para Mexibús y Mexicable (data/FUENTES.md)"}
