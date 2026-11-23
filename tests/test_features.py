"""Pruebas rapidas de la etapa Features D (corren en ~20 s, sin Ollama ni red).
Requieren haber corrido antes: uv run python scripts/02_features.py
Uso: uv run pytest tests/test_features.py -q
"""
import numpy as np
import pandas as pd
import pytest
from scipy.spatial import cKDTree

from app import motor

PROC = motor.PROC


@pytest.fixture(scope="module")
def feat():
    return pd.read_parquet(PROC / "agebs_features.parquet").drop(columns="geometry")


def test_forma_y_claves(feat):
    base = pd.read_parquet(PROC / "agebs_base.parquet", columns=["cvegeo", "pob_total"])
    assert len(feat) == len(base) == 5875
    assert feat["cvegeo"].is_unique and feat["cvegeo"].str.len().eq(13).all()
    assert set(feat["cvegeo"]) == set(base["cvegeo"])
    assert feat["pob_total"].sum() == 21_110_690          # igual que Datos A
    assert feat["nom_mun"].nunique() == 76


def test_colonia_y_columnas_del_contrato(feat):
    for c in ["nom_colonia", "decil_imputado", "nse", "densidad_hab_km2", "pob_diurna", "sec46_500m", "sec46_1km",
              "dist_estacion_m", "afluencia_estacion", "n_escuelas_500m", "n_hospitales_1km", "n_plazas_1km"]:
        assert c in feat.columns, c
    assert feat["nom_colonia"].notna().all() and (feat["nom_colonia"].str.strip() != "").all()


def test_sectores_suman_el_total(feat):
    # en 1 km los sectores suman los establecimientos totales (los 23 sectores del DENUE)
    sec = [c for c in feat.columns if c.startswith("sec") and c.endswith("_1km")]
    assert len(sec) == 23
    assert (feat[sec].sum(axis=1) == feat["estab_1km"]).all()
    assert (feat["estab_500m"] <= feat["estab_1km"]).all()


def test_decil_y_probabilidades(feat):
    ok = feat["decil_imputado"].notna()
    assert ok.sum() > 5700
    p = feat.loc[ok, [f"p_decil_{k:02d}" for k in range(1, 11)]]
    assert np.allclose(p.sum(axis=1), 1.0, atol=1e-9)
    assert feat.loc[ok, "decil_imputado"].between(1, 10).all()
    assert set(feat.loc[ok, "nse"].unique()) == {"bajo", "medio", "alto"}
    nse = feat.loc[ok, ["p_nse_bajo", "p_nse_medio", "p_nse_alto"]].sum(axis=1)
    assert np.allclose(nse, 1.0)
    # el reparto de hogares por decil no se aleja de ~10 % (cota holgada)
    rep = (p.mul(feat.loc[ok, "hogares"], axis=0)).sum() / feat.loc[ok, "hogares"].sum()
    assert rep.between(0.06, 0.15).all()


def test_decil_tiene_sentido_economico(feat):
    d = feat.assign(dec=feat["decil_imputado"].astype(float)).groupby("nom_mun")["dec"].median()
    assert d["Benito Juárez"] >= 8 and d["Coyoacán"] >= 7
    assert d["Iztapalapa"] <= 5 and d["Milpa Alta"] <= 4
    assert d["Benito Juárez"] > d["Iztapalapa"] + 3
    # contra CONAPO: a menor marginacion, mayor decil
    ok = feat["decil_imputado"].notna() & feat["im_2020"].notna()
    assert feat.loc[ok, "ing_trim_mediano_est"].corr(feat.loc[ok, "im_2020"], method="spearman") > 0.8


def test_gasto_potencial_coincide_con_la_formula(feat):
    ok = feat["decil_imputado"].notna()
    g = pd.read_parquet(PROC / "enigh_gasto.parquet")
    g = g[(g["ambito"] == "zmvm") & (g["rubro_clave"] == "ali_fuera_total")].set_index("decil")["gasto_trim_prom_hogar"]
    P = feat.loc[ok, [f"p_decil_{k:02d}" for k in range(1, 11)]].to_numpy()
    esperado = feat.loc[ok, "hogares"].to_numpy() * (P @ g.reindex(range(1, 11)).to_numpy())
    assert np.allclose(feat.loc[ok, "gasto_pot_ali_fuera_total_trim"], esperado)
    # y la funcion de motor da lo mismo
    assert np.allclose(motor.gasto_potencial("ali_fuera_total").loc[feat.loc[ok, "cvegeo"]], esperado)
    # el gasto total de la ZMVM es de un orden razonable (hogares x gasto medio del hogar zmvm)
    medio = (g * pd.Series(1 / 10, index=g.index)).sum()
    assert 0.5 < feat["gasto_pot_ali_fuera_total_trim"].sum() / (feat.loc[ok, "hogares"].sum() * medio) < 1.5


def test_transporte(feat):
    assert (feat["dist_estacion_m"] >= 0).all() and feat["dist_estacion_m"].notna().all()
    assert (feat["dist_metro_m"] >= feat["dist_estacion_m"] - 1e-6).all()   # el Metro es un subconjunto
    zocalo = feat[feat["nom_colonia"].str.contains("CENTRO", na=False) & (feat["nom_mun"] == "Cuauhtémoc")]
    assert zocalo["dist_metro_m"].min() < 600


def test_conteos_giro_contra_fuerza_bruta():
    s = motor.conteos_giro(["461170"], 500, decaimiento=False)           # heladerias, conteo plano
    assert len(s) == 5875 and s.notna().all() and (s >= 0).all()
    d = motor.denue("actual")
    pts = d[d["codigo"] == "461170"]
    cen = motor.agebs_xy()
    for cv in s.sort_values().index[[10, 3000, 5800]]:               # 3 AGEB de distinta densidad
        dist = np.hypot(pts["x"] - cen.loc[cv, "x"], pts["y"] - cen.loc[cv, "y"])
        assert s[cv] == (dist <= 500).sum()
        w = motor.peso_huff(dist.to_numpy(), 500)
        assert motor.conteos_giro(["461170"], 500)[cv] == pytest.approx(w.sum())


def test_decaimiento_y_radios():
    plano = motor.conteos_giro(["461170"], 500, decaimiento=False)
    huff = motor.conteos_giro(["461170"], 500)
    assert (huff <= plano + 1e-9).all()                             # el peso nunca pasa de 1
    assert motor.conteos_giro(["461170"], 1000, decaimiento=False).ge(plano).all()
    assert motor.peso_huff(np.array([0.0, 250.0, 500.0, 501.0]), 500).round(3).tolist() == [1.0, 0.5, 0.2, 0.0]


def test_giro_con_filtro_de_nombre():
    # pasteleria no tiene SCIAN propio: sale del filtro por nombre sobre panaderias (311812)
    past = motor.conteos_de_giro("pasteleria", radio_m=1000, decaimiento=False)
    pan = motor.conteos_giro(["311812"], 1000, decaimiento=False)
    assert 0 < past.sum() < pan.sum()


def test_corte_historico():
    h = motor.conteos_giro(["461170"], 500, corte="hist", decaimiento=False)
    assert len(h) == 5875 and h.sum() > 0
    assert h.index.equals(motor.conteos_giro(["461170"], 500).index)
