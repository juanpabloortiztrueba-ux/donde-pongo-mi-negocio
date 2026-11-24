"""Pruebas de la etapa Modelo E (~20 s, sin Ollama ni red).
Requieren haber corrido antes: uv run python scripts/03_entrenar.py
Uso: uv run pytest tests/test_modelo.py -q
"""
import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from app import motor

M = motor.MODELS


@pytest.fixture(scope="module")
def feat():
    return motor.cargar_features()


@pytest.fixture(scope="module")
def meta():
    return json.loads((M / "metadata.json").read_text(encoding="utf-8"))


def test_features_actual_igual_a_features_d(feat):
    # la misma definicion que 02_features: en el corte actual da exactamente agebs_features
    d = motor.features_denue_corte("actual")
    assert np.allclose(d.to_numpy(), feat.loc[d.index, motor.FEATS_DENUE].astype(float).to_numpy())
    t = motor.features_transporte_corte("actual")
    assert np.allclose(t.to_numpy(), feat.loc[t.index, motor.FEATS_TRANSP].astype(float).to_numpy(), equal_nan=True)


def test_corte_hist_sin_futuro():
    # en 11/2020 no hay estaciones que abrieron despues; el DENUE historico es otro
    th, ta = motor.features_transporte_corte("hist"), motor.features_transporte_corte("actual")
    assert (th["n_estaciones_1km"] <= ta["n_estaciones_1km"]).all()
    assert (th["dist_estacion_m"] >= ta["dist_estacion_m"] - 1e-6).all()
    dh, da = motor.features_denue_corte("hist"), motor.features_denue_corte("actual")
    assert not np.allclose(dh["estab_1km"], da["estab_1km"])
    fg = motor.features_giro("heladeria", "hist")
    assert np.allclose(fg["comp_huff"], motor.conteos_de_giro("heladeria", corte="hist").loc[fg.index])


def test_conteos_giro_sigue_igual():
    s = motor.conteos_de_giro("heladeria")
    assert len(s) == 5875 and s.notna().all()
    assert abs(s.mean() - 1.07) < 0.05      # valor de la bitacora de Features D
    fg = motor.features_giro("heladeria", "actual")
    assert np.allclose(fg["comp_huff"], s.loc[fg.index])


def test_matriz_y_metadata(meta):
    m = motor.matriz_modelo("hist", ["heladeria", "farmacia"])
    assert len(m) == 2 * 5875
    assert all(c in m.columns for c in meta["features"])
    assert meta["features"][0] == "giro_cod"
    assert not any(c in meta["features"] for c in ["cvegeo", "cvegeo_mun", "nom_colonia", "lat", "lon"])
    h = hashlib.sha256((M / "aperturas.joblib").read_bytes()).hexdigest()[:12]
    assert meta["modelo_id"] == h


def test_metricas_contra_lineas_base():
    met = pd.read_csv(M / "metricas_giro.csv")
    assert len(met) == 40
    mejor = (met["auc_modelo"] > met["auc_densidad"]) & (met["auc_modelo"] > met["auc_competencia"])
    assert mejor.sum() >= 10


def test_score_giro_forma(feat):
    s = motor.score_giro("heladeria")
    for c in ["cvegeo", "prob_apertura", "demanda", "competencia", "complementarios", "score", "razones"]:
        assert c in s.columns, c
    assert len(s) == 5875 and s["cvegeo"].is_unique and set(s["cvegeo"]) == set(feat.index)
    assert s["prob_apertura"].between(0, 1).all() and s["score"].between(0, 100).all()
    assert s["score"].is_monotonic_decreasing
    assert s["razones"].str.len().gt(20).all()
    np.testing.assert_allclose(s["captura_huff"], 1 / (1 + s["competencia"]))


def test_cache_igual_a_calculo_vivo():
    a = motor.score_giro("farmacia").set_index("cvegeo")
    b = motor.score_giro("farmacia", usar_cache=False).set_index("cvegeo").loc[a.index]
    np.testing.assert_allclose(a["score"], b["score"], rtol=1e-6)
    np.testing.assert_allclose(a["prob_apertura"], b["prob_apertura"], rtol=1e-6)


def test_pesos_del_score():
    # no negativos, suman 1, son los aprendidos (models/pesos_score.json) y los del respaldo de motor.py
    pj = json.loads((M / "pesos_score.json").read_text(encoding="utf-8"))
    w = motor.PESOS_SCORE
    assert set(w) == {"prob_apertura", "demanda_neta", "pob_neta", "flujo", "complementarios"}
    assert all(v >= 0 for v in w.values()) and abs(sum(w.values()) - 1) < 1e-9
    assert w == pj["pesos"] == motor._PESOS_ENTREGADOS
    assert w["demanda_neta"] + w["pob_neta"] >= pj["piso_demanda"] - 1e-9
    assert pj["version"] == motor.SCORE_VERSION == json.loads((M / "metadata.json").read_text(encoding="utf-8"))["score_version"]


def test_score_es_la_suma_de_percentiles_ponderados():
    s = motor.score_giro("farmacia")
    np.testing.assert_allclose(s["nucleo"], s["aperturas_esperadas"] * s["captura_huff"], rtol=1e-9)
    esperado = 100 * sum(w * s[f"pct_{k}"] for k, w in motor.PESOS_SCORE.items())
    np.testing.assert_allclose(s["score"], esperado, atol=1e-6)


def test_validacion_del_score():
    # el score vigente le gana a la mejor linea base ingenua en el crecimiento neto (el objetivo que importa) y mejora al anterior
    r = pd.read_csv(M / "validacion_score.csv")
    m = r.groupby(["objetivo", "puntuacion"])["valor"].mean()
    base = max(abs(m[("crecimiento_neto", b)]) for b in ["densidad", "comp_huff", "comp_ageb", "actividad"])
    assert m[("crecimiento_neto", "score_nuevo")] > base
    assert m[("crecimiento_neto", "score_nuevo")] > m[("crecimiento_neto", "score_v21")]
    assert m[("crecimiento_neto", "score_nuevo_oos")] > 0          # con pesos ajustados sin ver el municipio de prueba
    # esa ventaja viene de la carga censal 2024: sin ella (objetivo limpio) el score nuevo NO le gana al anterior, y el reporte lo dice
    assert m[("neto_sin_carga", "score_nuevo")] < m[("neto_sin_carga", "score_v21")] + 0.05
    assert m[("neto_sin_carga", "score_nuevo")] < m[("crecimiento_neto", "score_nuevo")]
    # la captura Huff (el castigo por competencia) ordena al reves de las aperturas crudas: por eso el AUC del score es bajo
    assert m[("aperturas_crudas", "captura_huff")] < 0.5
    txt = (motor.RAIZ / "reports" / "validacion_score.md").read_text(encoding="utf-8")
    for t in ["Diagnóstico", "Qué se decidió", "banda", "Crecimiento neto", "Sobrevivencia", "carga de los Censos Económicos",
              "Crecimiento neto sin carga censal", "no es una victoria empírica"]:
        assert t in txt


def test_giro_inexistente():
    with pytest.raises(KeyError):
        motor.score_giro("heladeria_en_monterrey")


def test_sin_tokens_en_salidas():
    env = motor.RAIZ / ".env"
    if not env.exists():
        pytest.skip("sin .env")
    vals = [ln.split("=", 1)[1].strip().strip("'\"") for ln in env.read_text().splitlines()
            if "=" in ln and not ln.lstrip().startswith("#")]
    vals = [v for v in vals if len(v) >= 8]
    for p in [M / "metadata.json", M / "entrenar.log", motor.RAIZ / "reports" / "validacion.md",
              motor.RAIZ / "reports" / "validacion_score.md", motor.RAIZ / "scripts" / "03b_validar_score.py",
              motor.RAIZ / "scripts" / "03_entrenar.py", motor.RAIZ / "app" / "motor.py"]:
        if p.exists():
            txt = p.read_text(encoding="utf-8")
            assert not any(v in txt for v in vals), p.name
