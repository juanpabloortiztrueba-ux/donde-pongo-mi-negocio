"""Motor de conteos y demanda por AGEB (sin LLM, solo datos).

Funciones publicas:
- conteos_giro(scian_list, radio_m, ...) -> Series por cvegeo, con decaimiento (Huff simple).
- conteos_de_giro(clave, ...)            -> lo mismo, leyendo config/giros.yaml (con filtros por nombre).
- gasto_potencial(rubro)                 -> Series por cvegeo: pesos por trimestre.
- cargar_features()                      -> agebs_features.parquet.

Las distancias salen del centroide de cada AGEB (lat/lon de agebs_base) en metros
(EPSG:6372, proyeccion LCC de INEGI).
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
CRS_METROS = "EPSG:6372"

# Parametros del decaimiento tipo Huff: w(d) = 1 / (1 + (d/d0)^BETA), d0 = D0_FRAC * radio, w=0 si d > radio
BETA = 2.0
D0_FRAC = 0.5


# ---------------------------------------------------------------- geometria
def a_metros(lon, lat) -> tuple[np.ndarray, np.ndarray]:
    """lon/lat (EPSG:4326) -> x, y en metros (EPSG:6372)."""
    from pyproj import Transformer

    tr = Transformer.from_crs("EPSG:4326", CRS_METROS, always_xy=True)
    x, y = tr.transform(np.asarray(lon, dtype=float), np.asarray(lat, dtype=float))
    return np.asarray(x), np.asarray(y)


@lru_cache(maxsize=1)
def agebs_xy() -> pd.DataFrame:
    """Centroides de las AGEB en metros. Indice = cvegeo."""
    df = pd.read_parquet(PROC / "agebs_base.parquet", columns=["cvegeo", "lat", "lon"])
    df["x"], df["y"] = a_metros(df["lon"], df["lat"])
    return df.set_index("cvegeo")[["x", "y"]]


@lru_cache(maxsize=2)
def denue(corte: str = "actual") -> pd.DataFrame:
    """DENUE de la ZMVM con coordenadas en metros.

    corte='actual' usa `codigo_act` (SCIAN 2023); corte='hist' usa `codigo_act_actual`
    (el codigo del historico traducido al catalogo vigente, ver BITACORA de Datos B).
    Columnas: id, nombre, codigo, per_ocu_medio, cvegeo, x, y.
    """
    if corte not in ("actual", "hist"):
        raise ValueError("corte debe ser 'actual' o 'hist'")
    cod = "codigo_act" if corte == "actual" else "codigo_act_actual"
    cols = ["id", "nombre", cod, "per_ocu_medio", "cvegeo", "lat", "lon"]
    df = pd.read_parquet(PROC / f"denue_{corte}.parquet", columns=cols)
    df = df.rename(columns={cod: "codigo"})
    df = df[df["lat"].notna() & df["lon"].notna() & df["codigo"].notna()].copy()
    df["x"], df["y"] = a_metros(df["lon"], df["lat"])
    return df.drop(columns=["lat", "lon"]).reset_index(drop=True)


# ---------------------------------------------------------------- nucleo radial
def peso_huff(d: np.ndarray, radio_m: float, beta: float = BETA, d0_frac: float = D0_FRAC) -> np.ndarray:
    """Peso por distancia: 1 en d=0, 0.5 en d=d0, y 0 pasando el radio."""
    d0 = d0_frac * radio_m
    w = 1.0 / (1.0 + (d / d0) ** beta)
    return np.where(d <= radio_m, w, 0.0)


def suma_radial(
    x: np.ndarray, y: np.ndarray, valores: np.ndarray | None, radio_m: float,
    decaimiento: bool = True, beta: float = BETA, d0_frac: float = D0_FRAC,
    centros: pd.DataFrame | None = None, trozo: int = 400,
) -> pd.Series:
    """Para cada AGEB suma (valor * peso(d)) de los puntos a <= radio_m de su centroide.

    Sin decaimiento (decaimiento=False) el peso es 1 dentro del radio (conteo plano).
    Se procesa por trozos de AGEB para no armar matrices gigantes (nada de productos cartesianos).
    """
    cen = agebs_xy() if centros is None else centros
    out = np.zeros(len(cen))
    if len(x) == 0:
        return pd.Series(out, index=cen.index)
    v = np.ones(len(x)) if valores is None else np.asarray(valores, dtype=float)
    arbol = cKDTree(np.column_stack([x, y]))
    cxy = cen[["x", "y"]].to_numpy()
    if not decaimiento and valores is None:  # conteo plano: basta return_length
        out = arbol.query_ball_point(cxy, r=radio_m, return_length=True, workers=4).astype(float)
        return pd.Series(out, index=cen.index)
    for a in range(0, len(cxy), trozo):
        sub = cxy[a:a + trozo]
        m = cKDTree(sub).sparse_distance_matrix(arbol, radio_m, output_type="ndarray")
        i, j, d = m["i"], m["j"], m["v"]
        w = peso_huff(d, radio_m, beta, d0_frac) if decaimiento else np.ones_like(d)
        out[a:a + len(sub)] = np.bincount(i, weights=w * v[j], minlength=len(sub))
    return pd.Series(out, index=cen.index)


# ---------------------------------------------------------------- seleccion de giro
def _mascara_scian(codigos: pd.Series, scian_list) -> np.ndarray:
    """True donde el codigo SCIAN coincide con alguno de la lista (exacto de 6, o prefijo si es mas corto)."""
    lista = [str(c) for c in scian_list]
    exactos = {c for c in lista if len(c) == 6}
    prefijos = tuple(c for c in lista if len(c) < 6)
    m = np.array(codigos.isin(exactos).to_numpy(), dtype=bool)
    if prefijos:
        m = m | np.asarray(codigos.str.startswith(prefijos), dtype=bool)
    return m


def seleccionar(df: pd.DataFrame, scian_list, filtros: list[dict] | None = None) -> pd.DataFrame:
    """Establecimientos del giro: codigo en scian_list, mas los de `filtros`
    ({codigos: [...], nombre_regex: '...'}) cuyo nombre cumple el regex (re.I)."""
    m = (_mascara_scian(df["codigo"], scian_list) if scian_list else np.zeros(len(df), bool)).copy()
    for f in filtros or []:
        mc = _mascara_scian(df["codigo"], f["codigos"])
        rx = re.compile(f["nombre_regex"], re.I)
        mn = df["nombre"].fillna("").str.contains(rx).to_numpy()
        m = m | (mc & mn)
    return df[m]


# ---------------------------------------------------------------- API publica
def conteos_giro(
    scian_list, radio_m: float, corte: str = "actual", filtros: list[dict] | None = None,
    decaimiento: bool = True, empleo: bool = False, beta: float = BETA, d0_frac: float = D0_FRAC,
) -> pd.Series:
    """Establecimientos del giro cerca de cada AGEB, con decaimiento tipo Huff.

    - scian_list: codigos SCIAN de 6 digitos (o prefijos mas cortos) que cuentan como el giro.
    - radio_m: radio de influencia en metros, medido desde el centroide de la AGEB.
    - corte: 'actual' (05/2026) o 'hist' (11/2020, con codigo_act_actual).
    - filtros: lista de {codigos, nombre_regex} (el `scian_con_filtro` de giros.yaml).
    - decaimiento: True -> cada establecimiento pesa 1/(1+(d/d0)^2) con d0 = radio/2 (Huff simple);
      False -> conteo plano dentro del radio.
    - empleo: True suma el punto medio del estrato de personal ocupado en vez de contar establecimientos.

    Devuelve una Series con indice cvegeo (las 5 875 AGEB), float, sin NaN.
    """
    pts = seleccionar(denue(corte), scian_list, filtros)
    vals = pts["per_ocu_medio"].to_numpy() if empleo else None
    s = suma_radial(pts["x"].to_numpy(), pts["y"].to_numpy(), vals, radio_m,
                    decaimiento=decaimiento, beta=beta, d0_frac=d0_frac)
    s.name = "conteo_giro"
    return s


@lru_cache(maxsize=1)
def giros() -> dict[str, dict]:
    """config/giros.yaml como dict {clave: giro}."""
    import yaml

    y = yaml.safe_load((RAIZ / "config" / "giros.yaml").read_text(encoding="utf-8"))
    return {g["clave"]: g for g in y["giros"]}


def conteos_de_giro(clave: str, radio_m: float | None = None, corte: str = "actual",
                    complementarios: bool = False, **kw) -> pd.Series:
    """conteos_giro para un giro de giros.yaml (aplica scian_con_filtro y su radio por defecto).
    complementarios=True cuenta los SCIAN complementarios (que atraen a su cliente) en vez de la competencia."""
    g = giros()[clave]
    r = radio_m or g["radio_influencia_m"]
    if complementarios:
        return conteos_giro(g.get("complementarios", []), r, corte=corte, **kw)
    return conteos_giro(g.get("scian", []), r, corte=corte, filtros=g.get("scian_con_filtro"), **kw)


@lru_cache(maxsize=1)
def cargar_features() -> pd.DataFrame:
    """agebs_features.parquet (sin geometria), indexado por cvegeo."""
    df = pd.read_parquet(PROC / "agebs_features.parquet")
    if "geometry" in df.columns:
        df = df.drop(columns="geometry")
    return df.set_index("cvegeo", drop=False)


def gasto_potencial(rubro: str, ambito: str = "zmvm") -> pd.Series:
    """Gasto trimestral potencial (pesos) de las familias de cada AGEB en un rubro ENIGH:
    hogares * sum_k P(decil k | AGEB) * gasto trimestral promedio del hogar en el decil k.
    El decil se definio dentro de la ENIGH del ambito 'zmvm' (ver reports/decil_imputado.md);
    con otro ambito se usan sus gastos con las mismas probabilidades (solo para comparar)."""
    f = cargar_features()
    g = pd.read_parquet(PROC / "enigh_gasto.parquet")
    g = g[(g["ambito"] == ambito) & (g["rubro_clave"] == rubro)].set_index("decil")["gasto_trim_prom_hogar"]
    if g.empty:
        raise KeyError(f"NO ENCONTRADO: rubro '{rubro}' en ambito '{ambito}' de enigh_gasto")
    g = g.reindex(range(1, 11)).fillna(0.0).to_numpy()
    p = f[[f"p_decil_{k:02d}" for k in range(1, 11)]].to_numpy()
    s = pd.Series(f["hogares"].to_numpy() * (p @ g), index=f.index, name=f"gasto_pot_{rubro}")
    return s


# ================================================================ Modelo E: features por corte
# Para entrenar, todo lo que sale del DENUE o del transporte se calcula en el corte historico
# (11/2020): asi el modelo no ve las aperturas que quiere predecir. Para recomendar se usan las
# mismas columnas en el corte actual (05/2026). Censo, CONAPO y decil imputado son de 2020.
SECTORES = ["11", "21", "22", "23", "31", "32", "33", "43", "46", "48", "49", "51", "52", "53", "54", "55",
            "56", "61", "62", "71", "72", "81", "93"]
FEATS_CENSO = ["area_km2", "pob_total", "pob_0_14", "pob_15_24", "pob_25_59", "pob_60_mas", "hogares",
               "viviendas_habitadas", "prom_ocupantes", "escolaridad_prom", "pct_viv_auto", "pct_viv_internet",
               "pct_viv_pc", "pct_viv_celular", "pea", "pob_ocupada", "im_2020", "densidad_hab_km2",
               "decil_esperado", "ing_trim_mediano_est", "p_nse_bajo", "p_nse_medio", "p_nse_alto"]
FEATS_DENUE = ([f"sec{s}_{r}" for s in SECTORES for r in ("500m", "1km")]
               + ["empleo_500m", "empleo_1km", "estab_500m", "estab_1km", "pob_diurna", "n_establecimientos",
                  "n_escuelas_500m", "n_escuelas_1km", "n_hospitales_500m", "n_hospitales_1km",
                  "n_plazas_500m", "n_plazas_1km"])
FEATS_TRANSP = ["dist_estacion_m", "dist_metro_m", "afluencia_metro_cercano", "n_estaciones_1km",
                "afluencia_metro_1km"]
ANIO_CORTE_HIST = 2020  # estaciones abiertas despues de 2020 no existen en el corte historico


def _r(r: int) -> str:
    return "500m" if r == 500 else "1km"


@lru_cache(maxsize=2)
def features_denue_corte(corte: str) -> pd.DataFrame:
    """Columnas FEATS_DENUE con la misma definicion de scripts/02_features.py, en el corte pedido.
    Indice = cvegeo (las 5 875 AGEB)."""
    den = denue(corte)
    cen = agebs_xy()
    f = pd.DataFrame(index=cen.index)
    sec = den["codigo"].str[:2]
    for s in SECTORES:
        p = den[sec == s]
        for r in (500, 1000):
            f[f"sec{s}_{_r(r)}"] = suma_radial(p["x"].to_numpy(), p["y"].to_numpy(), None, r,
                                               decaimiento=False).to_numpy()
    for r in (500, 1000):
        f[f"empleo_{_r(r)}"] = suma_radial(den["x"].to_numpy(), den["y"].to_numpy(),
                                           den["per_ocu_medio"].to_numpy(), r, decaimiento=False).to_numpy()
        f[f"estab_{_r(r)}"] = suma_radial(den["x"].to_numpy(), den["y"].to_numpy(), None, r,
                                          decaimiento=False).to_numpy()
    dd = den.dropna(subset=["cvegeo"]).groupby("cvegeo").agg(pob_diurna=("per_ocu_medio", "sum"),
                                                              n_establecimientos=("id", "size"))
    f = f.join(dd).fillna({"pob_diurna": 0.0, "n_establecimientos": 0})
    cod, nom = den["codigo"], den["nombre"].fillna("")
    ancla = cod.isin(["462111", "462210"]) & ~nom.str.contains(r"\b(?:3B|TRES B)\b", regex=True)
    plaza_nom = cod.str.startswith("5311") & nom.str.contains(
        r"CENTRO COMERCIAL|PLAZA COMERCIAL|MULTIPLAZA|\bMALL\b|GALERIAS", regex=True)
    for nombre, p in [("escuelas", den[cod.str.startswith("611")]), ("hospitales", den[cod.str.startswith("622")]),
                      ("plazas", den[ancla | plaza_nom])]:
        for r in (500, 1000):
            f[f"n_{nombre}_{_r(r)}"] = suma_radial(p["x"].to_numpy(), p["y"].to_numpy(), None, r,
                                                   decaimiento=False).to_numpy()
    return f[FEATS_DENUE].astype(float)


@lru_cache(maxsize=2)
def features_transporte_corte(corte: str) -> pd.DataFrame:
    """FEATS_TRANSP como en 02_features; en 'hist' se quitan las estaciones con anio_apertura > 2020
    y el Tren Interurbano (sin anio en transporte.parquet; su tramo en la ZMVM no existia en 2020)."""
    t = pd.read_parquet(PROC / "transporte.parquet")
    est = t["estado"].fillna("")
    t = t[~est.str.contains("no confirmada|no verificada") & (t["tipo"].fillna("") != "Servicio temporal")]
    if corte == "hist":
        t = t[~(t["anio_apertura"] > ANIO_CORTE_HIST) & (t["sistema"] != "Tren Interurbano")]
    m = t[t["sistema"] == "Metro"].groupby("estacion").agg(
        lat=("lat", "mean"), lon=("lon", "mean"),
        afluencia_anual=("afluencia_anual", lambda s: s.sum(min_count=1))).reset_index()
    m["sistema"] = "Metro"
    o = t[t["sistema"] != "Metro"][["sistema", "estacion", "lat", "lon", "afluencia_anual"]]
    e = pd.concat([m, o], ignore_index=True)
    e["x"], e["y"] = a_metros(e["lon"], e["lat"])
    cen = agebs_xy()
    cxy = cen[["x", "y"]].to_numpy()
    f = pd.DataFrame(index=cen.index)
    f["dist_estacion_m"], _ = cKDTree(e[["x", "y"]].to_numpy()).query(cxy)
    mt = e[e["sistema"] == "Metro"].reset_index(drop=True)
    d, i = cKDTree(mt[["x", "y"]].to_numpy()).query(cxy)
    f["dist_metro_m"] = d
    f["afluencia_metro_cercano"] = mt["afluencia_anual"].to_numpy()[i]
    f["n_estaciones_1km"] = suma_radial(e["x"].to_numpy(), e["y"].to_numpy(), None, 1000,
                                        decaimiento=False).to_numpy()
    f["afluencia_metro_1km"] = suma_radial(mt["x"].to_numpy(), mt["y"].to_numpy(),
                                           mt["afluencia_anual"].fillna(0).to_numpy(), 1000,
                                           decaimiento=False).to_numpy()
    return f[FEATS_TRANSP].astype(float)


def matriz_base(corte: str) -> pd.DataFrame:
    """Features por AGEB (sin giro): Censo/decil + DENUE y transporte del corte. Indice = cvegeo."""
    f = cargar_features()
    base = f[FEATS_CENSO].astype(float).copy()
    base["es_cdmx"] = (f["cve_ent"] == "09").astype(float)
    return base.join(features_denue_corte(corte)).join(features_transporte_corte(corte))


# ================================================================ Modelo E: features del giro
EDADES = {"0-14": "pob_0_14", "15-24": "pob_15_24", "25-59": "pob_25_59", "60+": "pob_60_mas"}
FEATS_GIRO = ["comp_huff", "comp_1km", "comp_ageb", "compl_huff", "giro_total_log", "radio_m",
              "gasto_rubro_ageb", "gasto_area", "pob_obj_ageb", "pob_obj_area", "pob_diurna_area", "nse_fit",
              "comp_por_10mil_obj"]


def pob_objetivo(clave: str) -> pd.Series:
    """Residentes del cliente objetivo: sum_g peso_g * poblacion del grupo de edad g (Censo 2020)."""
    f = cargar_features()
    w = giros()[clave]["cliente_objetivo"]
    return sum(float(p) * f[EDADES[g]].fillna(0.0) for g, p in w.items()).rename("pob_obj")


def _area(valores: pd.Series, radio_m: float) -> pd.Series:
    """Suma Huff (mismo peso que conteos_giro) de un valor por AGEB sobre las AGEB vecinas."""
    c = agebs_xy()
    v = valores.reindex(c.index).fillna(0.0).to_numpy()
    return suma_radial(c["x"].to_numpy(), c["y"].to_numpy(), v, radio_m)


# ---------------------------------------------------------------- reparto dasimetrico (para el score)
# La poblacion, el gasto y la intensidad de aperturas de cada AGEB se reparten parejo en una malla de
# puntos cada PASO_MALLA_M metros dentro de su poligono. Asi lo que cae «a 500 m» de un sitio es lo que de
# verdad esta a 500 m, y una AGEB enorme (p. ej. 29 mil hab. en 2 km2) no suma toda su gente en su
# centroide. Sin esto el score crecia con el tamano de la AGEB, no con la calidad del sitio.
PASO_MALLA_M = 100


@lru_cache(maxsize=1)
def malla_agebs(paso_m: int = PASO_MALLA_M) -> pd.DataFrame:
    """Puntos de la malla dentro de cada AGEB: cvegeo, x, y, frac (= 1 / puntos de su AGEB).
    Las AGEB mas chicas que una celda quedan con un solo punto en su centroide."""
    import geopandas as gpd

    g = gpd.read_parquet(PROC / "agebs_base.parquet", columns=["cvegeo", "geometry"]).to_crs(CRS_METROS)
    x0, y0, x1, y1 = g.total_bounds
    X, Y = np.meshgrid(np.arange(x0 + paso_m / 2, x1, paso_m), np.arange(y0 + paso_m / 2, y1, paso_m))
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(X.ravel(), Y.ravel()), crs=g.crs)
    j = gpd.sjoin(pts, g, predicate="within", how="inner")
    m = pd.DataFrame({"cvegeo": j["cvegeo"].to_numpy(), "x": j.geometry.x.to_numpy(), "y": j.geometry.y.to_numpy()})
    c = agebs_xy()
    faltan = c.loc[c.index.difference(pd.Index(m["cvegeo"].unique()))].rename_axis("cvegeo").reset_index()
    m = pd.concat([m, faltan[["cvegeo", "x", "y"]]], ignore_index=True)
    m["frac"] = 1.0 / m.groupby("cvegeo")["cvegeo"].transform("size")
    return m


def suma_dasimetrica(valores: pd.Series, radio_m: float, decaimiento: bool = True) -> pd.Series:
    """Como _area, pero repartiendo el valor de cada AGEB en su malla: suma (con peso Huff) de lo que
    hay a <= radio_m del centroide de cada AGEB. Indice = cvegeo."""
    m = malla_agebs()
    v = valores.reindex(m["cvegeo"]).fillna(0.0).to_numpy() * m["frac"].to_numpy()
    return suma_radial(m["x"].to_numpy(), m["y"].to_numpy(), v, radio_m, decaimiento=decaimiento)


# Corredor comercial = comercio al por menor (46), comida y bebida (72) y otros servicios (81) del DENUE.
SECTORES_CORREDOR = ("46", "72", "81")


@lru_cache(maxsize=16)
def flujo_corte(corte: str, radio_m: float) -> pd.DataFrame:
    """Proxies de flujo de gente alrededor de cada AGEB (no hay aforos peatonales abiertos para la ZMVM):
    empleo_radio (personal ocupado DENUE, punto medio del estrato, peso Huff), corredor_radio (negocios de
    los sectores 46, 72 y 81, peso Huff) y transporte (afluencia anual del Metro y estaciones a 1 km)."""
    den = denue(corte)
    x, y = den["x"].to_numpy(), den["y"].to_numpy()
    out = pd.DataFrame(index=agebs_xy().index)
    out["empleo_radio"] = suma_radial(x, y, den["per_ocu_medio"].fillna(0).to_numpy(), radio_m).to_numpy()
    cor = den["codigo"].str[:2].isin(SECTORES_CORREDOR).to_numpy()
    out["corredor_radio"] = suma_radial(x[cor], y[cor], None, radio_m).to_numpy()
    t = features_transporte_corte(corte)
    out["afluencia_metro_1km"] = t["afluencia_metro_1km"].to_numpy()
    out["n_estaciones_1km"] = t["n_estaciones_1km"].to_numpy()
    return out


def gasto_rubro(clave: str) -> pd.Series:
    """Gasto potencial trimestral del rubro ENIGH del giro en cada AGEB (NaN si el giro no tiene rubro)."""
    f = cargar_features()
    rub = giros()[clave].get("rubro_enigh")
    if not rub:
        return pd.Series(np.nan, index=f.index)
    col = f"gasto_pot_{rub}_trim"
    return f[col].astype(float) if col in f.columns else gasto_potencial(rub)


def features_giro(clave: str, corte: str) -> pd.DataFrame:
    """Competencia, complementarios y demanda del giro alrededor de cada AGEB, en el corte pedido."""
    g = giros()[clave]
    r = float(g["radio_influencia_m"])
    f = cargar_features()
    pts = seleccionar(denue(corte), g.get("scian", []), g.get("scian_con_filtro"))
    out = pd.DataFrame(index=agebs_xy().index)
    out["comp_huff"] = suma_radial(pts["x"].to_numpy(), pts["y"].to_numpy(), None, r)
    out["comp_1km"] = suma_radial(pts["x"].to_numpy(), pts["y"].to_numpy(), None, 1000, decaimiento=False)
    out["comp_ageb"] = pts.groupby("cvegeo").size().reindex(out.index).fillna(0.0)
    out["compl_huff"] = conteos_giro(g.get("complementarios", []), r, corte=corte)
    out["giro_total_log"] = np.log1p(len(pts))
    out["radio_m"] = r
    gr = gasto_rubro(clave)
    out["gasto_rubro_ageb"] = gr
    out["gasto_area"] = _area(gr, r) if gr.notna().any() else np.nan
    po = pob_objetivo(clave)
    out["pob_obj_ageb"] = po
    out["pob_obj_area"] = _area(po, r)
    out["pob_diurna_area"] = _area(features_denue_corte(corte)["pob_diurna"], r)
    nse = g["nse_objetivo"]
    out["nse_fit"] = sum(float(p) * f[f"p_nse_{k}"].astype(float) for k, p in nse.items())
    out["comp_por_10mil_obj"] = 1e4 * out["comp_huff"] / (out["pob_obj_area"] + 1.0)
    return out[FEATS_GIRO]


def matriz_modelo(corte: str, claves: list[str] | None = None) -> pd.DataFrame:
    """Tabla larga (AGEB x giro) con todas las features del modelo de aperturas.
    Columnas: cvegeo, cvegeo_mun, giro, giro_cod, FEATS_CENSO + es_cdmx + FEATS_DENUE + FEATS_TRANSP + FEATS_GIRO."""
    todos = list(giros())
    claves = claves or todos
    base = matriz_base(corte)
    partes = []
    for c in claves:
        x = base.join(features_giro(c, corte)).astype("float32")
        cab = pd.DataFrame({"cvegeo_mun": x.index.str[:5], "giro": c, "giro_cod": np.float32(todos.index(c))},
                           index=x.index)
        partes.append(pd.concat([cab, x], axis=1))
    return pd.concat(partes).rename_axis("cvegeo").reset_index()


# ================================================================ Modelo E: score_giro
MODELS = RAIZ / "models"
# Score (0-100). Cada termino es el percentil (0-1) de la AGEB dentro de la ZMVM PARA ESE GIRO (el score
# ordena sitios de un giro; no compara giros entre si). Todo se mide en el MISMO circulo de radio_influencia_m
# alrededor del sitio (reparto dasimetrico), no por AGEB, para no premiar AGEB grandes:
#   prob_apertura   : NUCLEO = aperturas esperadas del giro en el radio (intensidad -ln(1-p) del modelo, repartida
#                     en la superficie de cada AGEB) x captura Huff = aperturas esperadas POR COMPETIDOR.
#                     (el nombre del termino se conserva por compatibilidad; ya no es solo la probabilidad)
#   demanda_neta    : gasto potencial del rubro ENIGH en el radio x captura Huff
#   pob_neta        : poblacion objetivo en el radio (residente, diurna o mixta) x ajuste al NSE objetivo x captura
#   flujo           : flujo de gente (empleo DENUE en el radio, corredor comercial 46/72/81, Metro y estaciones a 1 km)
#   complementarios : negocios que atraen al cliente del giro (Huff)
# captura Huff = 1 / (1 + competidores ponderados por distancia): la parte del mercado que se lleva un
# local nuevo igual de atractivo que los que ya estan. Si el giro no tiene rubro ENIGH (coworking),
# el peso de demanda_neta pasa a pob_neta.
# Los PESOS NO los puso el autor: los aprendio scripts/03b_validar_score.py contra el crecimiento neto, la
# sobrevivencia y las altas fuera de la carga censal (ajustados en pliegues por municipio y probados en el
# pliegue que no vieron, no negativos, suman 1, redondeados a 0.05) y quedan en models/pesos_score.json.
# El nucleo (aperturas por competidor) no tiene parametros. Ver reports/validacion_score.md.
SCORE_VERSION = "3.0-nucleo-aprendido"  # cambia si cambia la formula: invalida models/scores_giros.parquet
# Valores de respaldo = los entregados (los mismos de models/pesos_score.json); un test comprueba que coinciden.
_PESOS_ENTREGADOS = {"prob_apertura": 0.35, "demanda_neta": 0.05, "pob_neta": 0.20, "flujo": 0.10,
                     "complementarios": 0.30}
# De donde sale el percentil de cada termino (el termino prob_apertura usa el nucleo, no la probabilidad sola)
FUENTE_TERMINO = {"prob_apertura": "nucleo", "demanda_neta": "demanda_neta", "pob_neta": "pob_neta",
                  "flujo": "flujo", "complementarios": "complementarios"}


def _cargar_pesos() -> dict:
    import json

    f = RAIZ / "models" / "pesos_score.json"
    try:
        w = json.loads(f.read_text(encoding="utf-8"))["pesos"]
        if set(w) == set(FUENTE_TERMINO):
            return {k: float(w[k]) for k in FUENTE_TERMINO}
    except (OSError, ValueError, KeyError):
        pass
    return dict(_PESOS_ENTREGADOS)


PESOS_SCORE = _cargar_pesos()


def poblacion_demanda(clave: str, pob_radio: pd.Series, empleo_radio: pd.Series) -> pd.Series:
    """Poblacion que demanda el giro en su radio: residentes objetivo, poblacion diurna (empleo) o promedio (mixta)."""
    base = giros()[clave].get("demanda_base", "residente")
    if base == "diurna":
        return empleo_radio
    if base == "mixta":
        return 0.5 * (pob_radio + empleo_radio)
    return pob_radio


def combinar_score(clave: str, fg: pd.DataFrame, prob: np.ndarray, pesos: dict | None = None,
                   corte: str = "actual") -> pd.DataFrame:
    """Junta aperturas, demanda, competencia y flujo (fg = features_giro o el giro en matriz_modelo; una fila
    por AGEB, con el cvegeo en el indice o en la columna `cvegeo`)."""
    w = dict(pesos or PESOS_SCORE)
    r = float(giros()[clave]["radio_influencia_m"])
    cv = pd.Index(fg["cvegeo"] if "cvegeo" in fg.columns else fg.index)
    out = pd.DataFrame(index=fg.index)
    out["prob_apertura"] = np.asarray(prob, dtype=float)
    lam = pd.Series(-np.log1p(-np.clip(out["prob_apertura"].to_numpy(), 0.0, 0.999)), index=cv)
    out["aperturas_esperadas"] = suma_dasimetrica(lam, r).reindex(cv).to_numpy()
    out["competencia"] = fg["comp_huff"].astype(float).to_numpy()
    out["captura_huff"] = 1.0 / (1.0 + out["competencia"])
    gr = gasto_rubro(clave)
    dem = suma_dasimetrica(gr, r) if gr.notna().any() else pd.Series(np.nan, index=agebs_xy().index)
    out["demanda"] = dem.reindex(cv).to_numpy()                # pesos por trimestre en el radio de influencia
    fl = flujo_corte(corte, r).reindex(cv)
    pob = suma_dasimetrica(pob_objetivo(clave), r).reindex(cv)
    out["residentes_objetivo"] = pob.to_numpy()               # residentes del cliente objetivo en el radio
    out["poblacion_objetivo"] = poblacion_demanda(clave, pob, fl["empleo_radio"]).to_numpy()  # la que demanda
    out["nse_fit"] = fg["nse_fit"].astype(float).to_numpy()
    out["complementarios"] = fg["compl_huff"].astype(float).to_numpy()
    out["empleo_radio"] = fl["empleo_radio"].to_numpy()
    out["corredor_radio"] = fl["corredor_radio"].to_numpy()
    out["afluencia_metro_1km"] = fl["afluencia_metro_1km"].to_numpy()
    out["n_estaciones_1km"] = fl["n_estaciones_1km"].to_numpy()
    out["nucleo"] = out["aperturas_esperadas"] * out["captura_huff"]   # aperturas esperadas por competidor
    out["demanda_neta"] = out["demanda"] * out["captura_huff"]
    out["pob_neta"] = out["poblacion_objetivo"] * out["nse_fit"] * out["captura_huff"]
    out["flujo"] = (out["empleo_radio"].rank(pct=True) + out["corredor_radio"].rank(pct=True)
                    + 0.5 * (out["afluencia_metro_1km"].rank(pct=True) + out["n_estaciones_1km"].rank(pct=True))) / 3
    if out["demanda"].isna().all():                           # giro sin rubro ENIGH
        w["pob_neta"] += w.pop("demanda_neta")
    out["pct_aperturas_esperadas"] = out["aperturas_esperadas"].rank(pct=True)   # solo informativo
    for k, src in FUENTE_TERMINO.items():
        out[f"pct_{k}"] = out[src].rank(pct=True).fillna(0.0)
    score = np.zeros(len(out))
    for k, pk in w.items():
        score += pk * out[f"pct_{k}"].to_numpy()
    out["score"] = 100.0 * score / sum(w.values())
    return out


@lru_cache(maxsize=1)
def cargar_modelo():
    """(modelo de aperturas, modelo de sobrevivencia o None, metadata) desde models/."""
    import joblib
    import json

    meta = json.loads((MODELS / "metadata.json").read_text(encoding="utf-8"))
    clf = joblib.load(MODELS / "aperturas.joblib")
    sob = joblib.load(MODELS / "sobrevivencia.joblib") if (MODELS / "sobrevivencia.joblib").exists() else None
    return clf, sob, meta


def _fmt_pesos(v: float) -> str:
    if not np.isfinite(v):
        return "NO ENCONTRADO"
    return f"${v / 1e6:,.2f} M" if v >= 1e6 else f"${v:,.0f}"


def _razones(clave: str, d: pd.DataFrame) -> pd.Series:
    """Texto corto con los numeros que explican el score de cada AGEB (todo medido en el radio del giro)."""
    r = giros()[clave]["radio_influencia_m"]
    rub = giros()[clave].get("rubro_enigh") or "sin rubro ENIGH"
    nan = pd.Series(np.nan, index=d.index)
    txt = []
    for p, ae, pp, dem, comp, cap, pob, emp, cor, comple, ps in zip(
            d["prob_apertura"], d["aperturas_esperadas"], d["pct_prob_apertura"], d["demanda"], d["competencia"],
            d["captura_huff"], d["residentes_objetivo"], d["empleo_radio"], d["corredor_radio"], d["complementarios"],
            d.get("prob_sobrevive", nan)):
        t = (f"prob. de apertura en la AGEB {p:.2f}; aperturas esperadas a {r} m {ae:.2f}, o {ae * cap:.2f} por competidor "
             f"(percentil {100 * pp:.0f} en aperturas por competidor); "
             f"gasto potencial {rub} {_fmt_pesos(dem)}/trim a {r} m; {comp:.1f} competidores ponderados "
             f"(captura Huff {100 * cap:.0f} %); residentes objetivo a {r} m {pob:,.0f}; empleos a {r} m {emp:,.0f}; "
             f"{cor:,.0f} negocios de corredor comercial; {comple:.1f} complementarios")
        if np.isfinite(ps):
            t += f"; prob. de seguir abierto 5 anios {ps:.2f}"
        txt.append(t)
    return pd.Series(txt, index=d.index)


def score_giro(giro_clave: str, corte: str = "actual", usar_cache: bool = True) -> pd.DataFrame:
    """Score por AGEB para un giro de giros.yaml, ordenado de mayor a menor.

    Columnas: cvegeo, prob_apertura, demanda (gasto potencial del rubro, pesos/trim en el area),
    competencia (competidores Huff), complementarios, score (0-100), razones, y extras
    (captura_huff, poblacion_objetivo, demanda_neta, pob_neta, pct_*, prob_sobrevive, nom_mun, nom_colonia, nse).
    En corte 'actual' (default) el modelo entrenado con 11/2020 -> 05/2026 se aplica al DENUE 05/2026:
    prob_apertura es la probabilidad de que aparezca >=1 negocio del giro en una ventana de ~5.5 anios.
    """
    if giro_clave not in giros():
        raise KeyError(f"NO ENCONTRADO: giro '{giro_clave}' no esta en config/giros.yaml")
    clf, sob, meta = cargar_modelo()
    cache = MODELS / "scores_giros.parquet"
    if usar_cache and corte == "actual" and cache.exists():
        c = pd.read_parquet(cache, filters=[("giro", "==", giro_clave)])
        if (len(c) and (c["modelo_id"] == meta["modelo_id"]).all() and "score_version" in c.columns
                and (c["score_version"] == SCORE_VERSION).all()):
            c = c.drop(columns=["giro", "modelo_id", "score_version"]).sort_values("score", ascending=False).reset_index(drop=True)
            c.insert(c.columns.get_loc("score") + 1, "razones", _razones(giro_clave, c))
            return c
    m = matriz_modelo(corte, [giro_clave]).set_index("cvegeo")
    prob = clf.predict_proba(m[meta["features"]])[:, 1]
    d = combinar_score(giro_clave, m, prob, corte=corte)
    if sob is not None:
        xs = m.assign(per_ocu_medio=np.float32(2.5))[meta["features_sobrevivencia"]]  # local nuevo de 0-5 personas
        d["prob_sobrevive"] = sob.predict_proba(xs)[:, 1]
    d["razones"] = _razones(giro_clave, d)
    f = cargar_features()
    d = d.join(f[["nom_mun", "nom_colonia", "nse"]])
    d = d.rename_axis("cvegeo").reset_index()
    prim = ["cvegeo", "prob_apertura", "demanda", "competencia", "complementarios", "score", "razones"]
    d = d[prim + [c for c in d.columns if c not in prim]]
    d["score_version"] = SCORE_VERSION
    return d.sort_values("score", ascending=False).reset_index(drop=True)
