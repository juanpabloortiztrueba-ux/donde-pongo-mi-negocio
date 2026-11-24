"""Router del panel de desglose del tablero (el panel lateral que se abre al picar una AGEB o una tarjeta de zona).

    GET /api/zona/{cvegeo}/desglose?giro=<clave>
        De una AGEB: el score del giro partido en sus cinco componentes (aporte en puntos, peso y percentil), su lugar
        entre las 5,875 AGEB, la gente (edades, ingreso, decil y NSE) contra su municipio y la ZMVM, los competidores y
        los complementarios (conteos y los más cercanos con nombre y distancia), las estaciones cercanas y el flujo de
        gente. Sin `giro` (o con un giro que no existe) regresa todo lo que no depende del giro y una nota.
        AGEB inexistente: 404 {error} en español.

Todo sale de app/motor.py (score_giro, pesos de models/pesos_score.json) y de data/processed (solo lectura); no se
escribe ningún peso ni cifra a mano. Los resultados por giro (tabla del score, árboles de vecinos) y los agregados por
municipio se guardan en memoria: después de la primera llamada de cada giro responde en pocos milisegundos.
"""
from __future__ import annotations

import unicodedata
from functools import lru_cache
from math import isfinite

import numpy as np
import pandas as pd
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scipy.spatial import cKDTree

from app import motor
from app.api import base
from app.api.preguntar import _limpio, _nombre_colonia

router = APIRouter(prefix="/api", tags=["desglose"])
NO = "NO ENCONTRADO"

F_CENSO = "Censo de Población y Vivienda 2020, INEGI (resultados por AGEB urbana)"
F_ENIGH = "ENIGH 2024, INEGI; el decil y el ingreso de cada AGEB los estima el proyecto (reports/decil_imputado.md)"
F_TRANSP = "datos.cdmx.gob.mx (Metro, Metrobús, STE, GTFS) y OpenStreetMap; afluencia del Metro 2025"
F_SCORE = "modelo propio (score por giro: percentil de la AGEB dentro del giro, DENUE, Censo 2020 y ENIGH 2024)"
RADIO_ESTACIONES_M = 1500
VECINOS = 5

# Qué es cada componente del score (las claves son las de motor.FUENTE_TERMINO; los pesos salen de motor.PESOS_SCORE).
COMPONENTES = {
    "prob_apertura": ("Aperturas esperadas por competidor", "Cuántos negocios del giro se espera que abran en el radio, repartidos entre los que ya compiten allí."),
    "complementarios": ("Negocios complementarios", "Negocios que atraen al cliente del giro (escuelas, plazas, servicios…), ponderados por distancia."),
    "pob_neta": ("Gente que compraría", "Personas del cliente objetivo en el radio, ajustadas al nivel socioeconómico que busca el giro y a la parte del mercado que queda libre."),
    "flujo": ("Flujo de gente", "Empleos y corredor comercial en el radio, estaciones y afluencia del Metro a 1 km."),
    "demanda_neta": ("Gasto potencial", "Lo que gastan las familias del radio en el rubro de la ENIGH del giro, por la parte del mercado que queda libre."),
}
ORDEN = ["prob_apertura", "complementarios", "pob_neta", "flujo", "demanda_neta"]


# ---------------------------------------------------------------- utilidades
def _error(estado: int, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=estado, content={"error": mensaje})


def _r(x, nd=1):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return round(x, nd) if isfinite(x) else None


def _r0(x):
    v = _r(x, 0)
    return int(v) if v is not None else None


def _n(x, nd=0) -> str:
    """Número para un texto es-MX: miles con coma y decimales con punto; NO ENCONTRADO si no hay dato."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        return NO
    return f"{x:,.{nd}f}" if isfinite(x) else NO


def _sin_acentos(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def _fuente_denue() -> str:
    return f"DENUE corte {base.cortes().get('denue_actual') or NO}, INEGI"


def _giro_visible(clave: str) -> dict:
    for g in base._giros_lista():
        if g["clave"] == clave:
            return {"clave": clave, "nombre": g["nombre"]}
    return {"clave": clave, "nombre": clave.replace("_", " ").capitalize()}


def _resolver_giro(giro: str | None) -> str | None:
    """Clave del catálogo a partir de la clave o del nombre visible; None si no existe."""
    if not giro:
        return None
    g = _sin_acentos(giro).replace(" ", "_")
    cat = motor.giros()
    if g in cat:
        return g
    for k, v in cat.items():
        if g in {_sin_acentos(n).replace(" ", "_") for n in v.get("nombres", [])}:
            return k
    return None


def _mediana_ponderada(valores: pd.Series, pesos: pd.Series) -> float | None:
    d = pd.DataFrame({"v": valores, "w": pesos}).dropna()
    d = d[d["w"] > 0].sort_values("v")
    if d.empty:
        return None
    acum = d["w"].cumsum()
    return float(d["v"][acum >= d["w"].sum() / 2].iloc[0])


# ---------------------------------------------------------------- agregados por municipio y ZMVM (una vez)
EDADES = {"0-14": ("0 a 14 años", "pob_0_14"), "15-24": ("15 a 24 años", "pob_15_24"),
          "25-59": ("25 a 59 años", "pob_25_59"), "60+": ("60 años o más", "pob_60_mas")}


def _resumen_grupo(d: pd.DataFrame) -> dict:
    pob = float(d["pob_total"].sum())
    ped = np.array([[float(d[c].sum()) for _, c in EDADES.values()]]) / pob * 100 if pob else np.full((1, 4), np.nan)
    w = d["hogares"].fillna(0)
    nse = {k: (float((d[f"p_nse_{k}"] * w).sum() / w[d[f"p_nse_{k}"].notna()].sum()) * 100 if w[d[f"p_nse_{k}"].notna()].sum() else np.nan)
           for k in ("bajo", "medio", "alto")}
    return {"edades": dict(zip(EDADES, ped[0])), "n_agebs": int(len(d)), "habitantes": pob,
            "decil": _mediana_ponderada(d["decil_imputado"], d["hogares"]),
            "ingreso": _mediana_ponderada(d["ing_trim_mediano_est"], d["hogares"]), "nse": nse,
            "empleo_ageb_medio": float(d["pob_diurna"].mean())}


@lru_cache(maxsize=1)
def _agregados() -> dict:
    f = motor.cargar_features()
    mun = f["cve_ent"].astype(str) + f["cve_mun"].astype(str)
    return {"zmvm": _resumen_grupo(f), "mun": {m: _resumen_grupo(g) for m, g in f.groupby(mun)}}


# ---------------------------------------------------------------- score del giro (una vez por giro)
@lru_cache(maxsize=48)
def _tabla(clave: str) -> pd.DataFrame:
    """score_giro del motor, sin el texto largo de `razones`, con el lugar en la ZMVM y en el municipio (por cvegeo)."""
    d = motor.score_giro(clave).drop(columns=["razones"], errors="ignore").reset_index(drop=True)
    d["lugar"] = np.arange(1, len(d) + 1)               # ya viene ordenado de mayor a menor (igual que herramientas)
    d["cvegeo_mun"] = d["cvegeo"].str[:5]
    d["lugar_mun"] = d.groupby("cvegeo_mun").cumcount() + 1
    d["de_mun"] = d.groupby("cvegeo_mun")["cvegeo"].transform("size")
    return d.set_index("cvegeo", drop=False)


def pesos_efectivos(clave: str) -> dict[str, float]:
    """Pesos del score para el giro, como los usa motor.combinar_score (sin rubro ENIGH, el del gasto pasa a la población)."""
    w = dict(motor.PESOS_SCORE)
    if _tabla(clave)["demanda"].isna().all():
        w["pob_neta"] += w.pop("demanda_neta")
    return w


def _score(clave: str, cv: str) -> dict:
    d = _tabla(clave)
    r = d.loc[cv]
    w = pesos_efectivos(clave)
    tot = sum(w.values())
    g = motor.giros()[clave]
    radio = int(g["radio_influencia_m"])
    den = _fuente_denue()
    valor = {
        "prob_apertura": (r["nucleo"], "aperturas esperadas por competidor",
                          f"{_n(r['aperturas_esperadas'], 2)} aperturas esperadas a {radio} m, con una captura de mercado de {_n(100 * r['captura_huff'])} %"),
        "complementarios": (r["complementarios"], "negocios complementarios ponderados", f"a {radio} m, ponderados por distancia"),
        "pob_neta": (r["pob_neta"], "personas objetivo, ajustadas",
                     f"{_n(r['poblacion_objetivo'])} personas objetivo a {radio} m × ajuste al NSE {_n(r['nse_fit'], 2)} × captura de mercado"),
        "flujo": (r["flujo"], "índice 0 a 1",
                  f"{_n(r['empleo_radio'])} empleos y {_n(r['corredor_radio'])} negocios de corredor a {radio} m; {_n(r['n_estaciones_1km'])} estaciones a 1 km"),
        "demanda_neta": (r["demanda_neta"], "pesos por trimestre",
                         f"gasto del rubro «{g.get('rubro_enigh_etiqueta') or g.get('rubro_enigh') or NO}» en {radio} m × captura de mercado"),
    }
    fuente = {
        "prob_apertura": f"modelo propio de aperturas (DENUE 11/2020 contra 05/2026) × captura Huff; {den}",
        "complementarios": f"{den}; SCIAN complementarios de config/giros.yaml",
        "pob_neta": f"{F_CENSO}; NSE estimado del proyecto ({F_ENIGH.split(';')[0]})",
        "flujo": f"{den}; {F_TRANSP}",
        "demanda_neta": F_ENIGH,
    }
    comps, suma = [], 0.0
    for k in ORDEN:
        pk = float(w.get(k, 0.0))
        pct = float(r[f"pct_{k}"])
        v, unidad, detalle = valor[k]
        aplica = k in w
        suma += 100 * pk * pct / tot if aplica else 0.0
        comps.append({
            "clave": k, "etiqueta": COMPONENTES[k][0], "descripcion": COMPONENTES[k][1], "aplica": aplica,
            "peso": round(pk / tot, 4) if aplica else 0.0,
            "percentil": _r(100 * pct, 1) if aplica else None,
            "aporte": _r(100 * pk * pct / tot, 2) if aplica else 0.0,
            "valor": _r(v, 3) if aplica and isfinite(float(v)) else None, "unidad": unidad, "detalle": detalle if aplica else None,
            "fuente": fuente[k],
            **({} if aplica else {"nota": f"Este giro no tiene rubro de gasto en la ENIGH: su peso pasó a «{COMPONENTES['pob_neta'][0]}»."}),
        })
    lugar = int(r["lugar"])
    n = int(len(d))
    return {
        "valor": _r(r["score"], 2), "de": 100, "version": motor.SCORE_VERSION,
        "componentes": comps, "suma_aportes": round(suma, 2),
        "pesos_fuente": f"models/pesos_score.json (versión {motor.SCORE_VERSION}), aprendidos fuera de muestra por municipio",
        "como_leer": "El score es el percentil de la AGEB dentro del giro, sumado con estos pesos: ordena zonas para este giro, no compara giros.",
        "lugar": {"posicion": lugar, "de": n, "mejor_que_pct": _r(100 * (n - lugar) / max(n - 1, 1), 1), "en_top_5": lugar <= 5,
                  "municipio": {"posicion": int(r["lugar_mun"]), "de": int(r["de_mun"])},
                  "fuente": f"modelo propio: score de las {n:,} AGEB para este giro (models/scores_giros.parquet)"},
        "prob_apertura_pct": _r(100 * r["prob_apertura"], 1),
        "prob_sigue_abierto_pct": _r(100 * r["prob_sobrevive"], 1) if "prob_sobrevive" in r and pd.notna(r["prob_sobrevive"]) else None,
        "competidores_ponderados": _r(r["competencia"], 2), "complementarios_ponderados": _r(r["complementarios"], 2),
        "radio_m": radio, "fuente": F_SCORE,
    }


# ---------------------------------------------------------------- negocios cercanos (DENUE)
@lru_cache(maxsize=1)
def _titulos_scian() -> dict[str, str]:
    d = pd.read_csv(motor.PROC / "scian.csv", dtype=str)
    return dict(zip(d["codigo"], d["titulo"]))


@lru_cache(maxsize=48)
def _negocios(clave: str, tipo: str) -> tuple[pd.DataFrame, cKDTree | None]:
    """Establecimientos del giro (tipo 'comp') o de sus SCIAN complementarios ('compl') y su árbol de vecinos."""
    g = motor.giros()[clave]
    den = motor.denue("actual")
    pts = (motor.seleccionar(den, g.get("scian", []), g.get("scian_con_filtro")) if tipo == "comp"
           else motor.seleccionar(den, g.get("complementarios", [])))
    pts = pts.reset_index(drop=True)
    return pts, (cKDTree(pts[["x", "y"]].to_numpy()) if len(pts) else None)


def _cercanos(clave: str, tipo: str, cv: str, radio: float) -> dict:
    try:
        pts, arbol = _negocios(clave, tipo)
    except (OSError, KeyError, ValueError):   # no hay DENUE con coordenadas en data/processed: quedan los conteos del modelo
        return {"total_zmvm": None, "en_radio": None, "en_ageb": None, "cercanos": [], "sin_puntos": True,
                "motivo": f"{NO}: no hay puntos del DENUE con coordenadas en data/processed para listar los negocios"}
    xy = motor.agebs_xy().loc[cv]
    c = np.array([xy["x"], xy["y"]])
    if arbol is None:
        return {"total_zmvm": 0, "en_radio": 0, "en_ageb": 0, "cercanos": []}
    en_radio = int(arbol.query_ball_point(c, radio, return_length=True))
    k = min(VECINOS, len(pts))
    dist, idx = arbol.query(c, k=k)
    dist, idx = np.atleast_1d(dist), np.atleast_1d(idx)
    tit = _titulos_scian()
    lista = []
    for dd, i in zip(dist, idx):
        p = pts.iloc[int(i)]
        lista.append({"nombre": str(p["nombre"]) if pd.notna(p["nombre"]) and str(p["nombre"]).strip() else None,
                      "actividad": tit.get(str(p["codigo"])), "scian": str(p["codigo"]), "distancia_m": _r0(dd),
                      "en_radio": bool(dd <= radio), "cvegeo": str(p["cvegeo"]), "en_la_ageb": str(p["cvegeo"]) == cv})
    return {"total_zmvm": int(len(pts)), "en_radio": en_radio, "en_ageb": int((pts["cvegeo"] == cv).sum()), "cercanos": lista}


def _competencia(clave: str, cv: str, sc: dict) -> dict:
    radio = float(sc["radio_m"])
    comp, compl = _cercanos(clave, "comp", cv, radio), _cercanos(clave, "compl", cv, radio)
    g = motor.giros()[clave]
    return {
        "radio_m": int(radio),
        "competidores": {**comp, "ponderados": sc["competidores_ponderados"], "etiqueta": "Competidores: negocios del mismo giro",
                         "fuente": f"{_fuente_denue()} (SCIAN del giro en config/giros.yaml); distancias desde el centro de la AGEB"},
        "complementarios": {**compl, "ponderados": sc["complementarios_ponderados"], "etiqueta": "Complementarios: negocios que atraen a su cliente",
                            "scian": [str(c) for c in g.get("complementarios", [])],
                            "fuente": f"{_fuente_denue()} (SCIAN complementarios en config/giros.yaml, criterio del proyecto)"},
    }


# ---------------------------------------------------------------- transporte (data/processed/transporte.parquet)
@lru_cache(maxsize=1)
def _estaciones() -> tuple[pd.DataFrame, cKDTree]:
    t = pd.read_parquet(motor.PROC / "transporte.parquet").dropna(subset=["lat", "lon"]).reset_index(drop=True)
    t["x"], t["y"] = motor.a_metros(t["lon"], t["lat"])
    return t, cKDTree(t[["x", "y"]].to_numpy())


def _transporte(cv: str) -> dict:
    t, arbol = _estaciones()
    xy = motor.agebs_xy().loc[cv]
    c = np.array([xy["x"], xy["y"]])
    dist, idx = arbol.query(c, k=min(VECINOS * 3, len(t)))
    lista, vistos = [], set()
    for dd, i in zip(dist, idx):
        p = t.iloc[int(i)]
        llave = (p["sistema"], str(p["linea"]), p["estacion"])
        if llave in vistos:
            continue
        vistos.add(llave)
        lista.append({"sistema": p["sistema"], "linea": None if pd.isna(p["linea"]) else str(p["linea"]), "estacion": p["estacion"],
                      "distancia_m": _r0(dd), "afluencia_anual": _r0(p["afluencia_anual"]),
                      "anio_afluencia": _r0(p["anio_afluencia"]), "estado": p["estado"] if isinstance(p["estado"], str) else None})
        if len(lista) == VECINOS:
            break
    return {"radio_busqueda_m": RADIO_ESTACIONES_M, "estaciones": lista,
            "a_1km": int(arbol.query_ball_point(c, 1000, return_length=True)),
            "cercanas_en_radio": [e for e in lista if e["distancia_m"] is not None and e["distancia_m"] <= RADIO_ESTACIONES_M],
            "fuente": F_TRANSP}


# ---------------------------------------------------------------- gente y flujo
def _contra(a, mun, zmvm, nd=1) -> dict:
    return {"ageb": _r(a, nd), "municipio": _r(mun, nd), "zmvm": _r(zmvm, nd)}


def _poblacion(row: pd.Series, mun: dict, zm: dict) -> dict:
    pob = float(row["pob_total"]) if pd.notna(row["pob_total"]) else 0.0
    grupos = []
    for k, (etq, col) in EDADES.items():
        n = row[col]
        grupos.append({"grupo": k, "etiqueta": etq, "personas": _r0(n), **{f"pct_{a}": b for a, b in
                       _contra(100 * n / pob if pob else None, mun["edades"][k], zm["edades"][k]).items()}})
    return {"habitantes": _r0(row["pob_total"]), "hogares": _r0(row["hogares"]), "densidad_hab_km2": _r0(row["densidad_hab_km2"]),
            "grupos_edad": grupos,
            "habitantes_municipio": _r0(mun["habitantes"]), "agebs_municipio": mun["n_agebs"],
            "fuente": f"{F_CENSO}; municipio y ZMVM = suma de sus AGEB urbanas"}


def _ingreso(row: pd.Series, mun: dict, zm: dict) -> dict:
    nse = {k: _contra(100 * row[f"p_nse_{k}"] if pd.notna(row[f"p_nse_{k}"]) else None, mun["nse"][k], zm["nse"][k]) for k in ("bajo", "medio", "alto")}
    return {"decil": _contra(row["decil_imputado"], mun["decil"], zm["decil"], 0),
            "ingreso_trim_mediano_mxn": _contra(row["ing_trim_mediano_est"], mun["ingreso"], zm["ingreso"], -2),
            "nse": row["nse"] if isinstance(row["nse"], str) else None, "prob_nse_pct": nse,
            "como_leer": "Decil y NSE son estimaciones del proyecto: la ENIGH no representa colonias. Municipio y ZMVM: mediana ponderada por hogares.",
            "fuente": F_ENIGH}


def _flujo(row: pd.Series, mun: dict, zm: dict) -> dict:
    return {"poblacion_diurna": _r0(row["pob_diurna"]), "poblacion_diurna_ageb_media_municipio": _r0(mun["empleo_ageb_medio"]),
            "poblacion_diurna_ageb_media_zmvm": _r0(zm["empleo_ageb_medio"]),
            "empleos_500m": _r0(row["empleo_500m"]), "empleos_1km": _r0(row["empleo_1km"]),
            "negocios_en_ageb": _r0(row["n_establecimientos"]), "negocios_500m": _r0(row["estab_500m"]), "negocios_1km": _r0(row["estab_1km"]),
            "escuelas_1km": _r0(row["n_escuelas_1km"]), "hospitales_1km": _r0(row["n_hospitales_1km"]),
            "fuente": f"{_fuente_denue()}: población diurna = personal ocupado de los negocios de la AGEB (punto medio del estrato)"}


# ---------------------------------------------------------------- endpoint
@router.get("/zona/{cvegeo}/desglose")
def desglose(cvegeo: str, giro: str | None = None):
    cv = (cvegeo or "").strip().upper()
    f = motor.cargar_features()
    if cv not in f.index:
        return _error(404, f"{NO}: la AGEB {cv} no está en el modelo (solo las {len(f):,} AGEB urbanas de la ZMVM).")
    row = f.loc[cv]
    ag = _agregados()
    mun_id = cv[:5]
    mun, zm = ag["mun"].get(mun_id) or ag["zmvm"], ag["zmvm"]
    clave = _resolver_giro(giro)

    out: dict = {
        "encontrado": True, "ageb": cv, "agebs_zmvm": int(len(f)), "colonia": _nombre_colonia(row["nom_colonia"]), "municipio": row["nom_mun"], "cvegeo_mun": mun_id,
        "giro": _giro_visible(clave) if clave else None, "giro_pedido": giro or None,
        "poblacion": _poblacion(row, mun, zm), "ingreso": _ingreso(row, mun, zm),
        "flujo": _flujo(row, mun, zm), "transporte": _transporte(cv),
        "fuentes": [F_CENSO, F_ENIGH, _fuente_denue(), F_TRANSP],
    }
    if clave:
        sc = _score(clave, cv)
        out["score"] = sc
        out["competencia"] = _competencia(clave, cv, sc)
        out["fuentes"].append(F_SCORE)
        # el flujo del giro se mide en el radio del giro (lo mismo que entra al score)
        r = _tabla(clave).loc[cv]
        out["flujo"]["en_radio_del_giro"] = {"radio_m": sc["radio_m"], "empleos": _r0(r["empleo_radio"]), "negocios_de_corredor": _r0(r["corredor_radio"]),
                                             "estaciones_1km": _r0(r["n_estaciones_1km"]), "afluencia_metro_1km": _r0(r["afluencia_metro_1km"])}
    else:
        out["score"] = None
        out["competencia"] = None
        out["nota_giro"] = ("Elige un giro para ver el score." if not giro
                            else f"{NO}: «{giro}» no es un giro del catálogo. Elige uno para ver el score.")
    return _limpio(out)


def precalentar() -> None:
    """Calienta lo que el panel pide primero: agregados por municipio, estaciones y el DENUE del motor (en un hilo, al arrancar)."""
    try:
        _agregados()
        _estaciones()
        motor.denue("actual")
        motor.agebs_xy()
    except Exception:
        pass
