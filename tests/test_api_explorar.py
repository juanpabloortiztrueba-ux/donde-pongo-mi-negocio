"""Pruebas de la API de Explorar y Comparar (sin Ollama ni red): variables, mapa, scores, comparar, denue, sugerir, transporte."""
import math

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.servidor import crear_app


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    web = tmp_path_factory.mktemp("web")
    (web / "index.html").write_text('<!doctype html><div id="root"></div>', encoding="utf-8")
    return TestClient(crear_app(web))


def sin_nan(x):
    """Ningun NaN ni infinito en el JSON (rompe JSON.parse en el navegador)."""
    if isinstance(x, float):
        assert math.isfinite(x)
    elif isinstance(x, dict):
        [sin_nan(v) for v in x.values()]
    elif isinstance(x, list):
        [sin_nan(v) for v in x]


def test_variables(cliente):
    d = cliente.get("/api/variables").json()
    claves = {v["clave"] for v in d["variables"]}
    assert len(claves) >= 14
    assert {"densidad", "pob_total", "decil", "empleo_1km", "comercio_1km", "grado_marginacion", "afluencia_metro"} <= claves
    for v in d["variables"]:
        assert v["etiqueta"] and v["unidad"] and v["fuente"] and v["descripcion"] and v["agregacion_texto"]
    assert next(v for v in d["variables"] if v["clave"] == "empleo_1km")["fuente"].startswith("DENUE corte ")
    assert set(next(v for v in d["variables"] if v["clave"] == "grado_marginacion")["etiquetas_ordinal"].values()) >= {"Muy bajo", "Muy alto"}


def test_mapa_coincide_con_los_datos(cliente):
    d = cliente.get("/api/mapa", params={"variable": "pob_total"}).json()
    sin_nan(d)
    f = pd.read_parquet("data/processed/agebs_features.parquet", columns=["cvegeo", "pob_total", "cve_ent", "cve_mun"])
    assert len(d["valores"]) == len(f) == 5875
    assert d["resumen"]["poblacion"] == int(f["pob_total"].sum())
    assert d["resumen"]["valor"] == pytest.approx(f["pob_total"].sum())  # suma
    assert len(d["municipios"]) == 76 and sum(m["poblacion"] for m in d["municipios"]) == int(f["pob_total"].sum())
    assert [q["p"] for q in d["cuantiles"]] == [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    vals = [q["valor"] for q in d["cuantiles"]]
    assert vals == sorted(vals)
    assert d["dominio"][0] < d["dominio"][1]
    assert sum(c["n"] for c in d["histograma"]["cajas"]) == d["histograma"]["n"] == d["resumen"]["n_con_dato"]
    assert d["fuente"] == "Censo 2020 INEGI"


def test_mapa_municipio_y_razones(cliente):
    d = cliente.get("/api/mapa", params={"variable": "pct_0_14", "municipio": "09003"}).json()  # Coyoacan
    sin_nan(d)
    assert d["resumen"]["ambito"] == "Coyoacán" and d["municipio"] == "09003"
    assert 0 < d["resumen"]["n_agebs"] < 400
    assert 5 < d["resumen"]["valor"] < 30  # % de 0 a 14 anios
    assert len(d["municipios"]) == 76  # la tabla siempre trae todos
    # la densidad agregada es suma de gente / suma de area, no promedio de densidades
    f = pd.read_parquet("data/processed/agebs_features.parquet", columns=["cve_ent", "cve_mun", "pob_total", "area_km2"])
    f = f[(f["cve_ent"] + f["cve_mun"]) == "09003"]
    de = cliente.get("/api/mapa", params={"variable": "densidad", "municipio": "09003"}).json()
    assert de["resumen"]["valor"] == pytest.approx(f["pob_total"].sum() / f["area_km2"].sum(), rel=1e-3)


def test_mapa_todas_las_variables_y_errores(cliente):
    for v in cliente.get("/api/variables").json()["variables"]:
        r = cliente.get("/api/mapa", params={"variable": v["clave"]})
        assert r.status_code == 200, v["clave"]
        sin_nan(r.json())
    ordinal = cliente.get("/api/mapa", params={"variable": "grado_marginacion"}).json()
    assert ordinal["dominio"] == [1.0, 5.0] and [c["etiqueta"] for c in ordinal["histograma"]["cajas"]][0] == "Muy bajo"
    assert cliente.get("/api/mapa", params={"variable": "inventada"}).status_code == 404
    r = cliente.get("/api/mapa", params={"variable": "densidad", "municipio": "99999"})
    assert r.status_code == 422 and "error" in r.json()


def test_scores(cliente):
    d = cliente.get("/api/scores/heladeria").json()
    sin_nan(d)
    assert d["giro"] == "heladeria" and d["nombre"] == "Heladería" and d["n"] == 5875
    assert all(0 <= s <= 100 for s in d["scores"].values())
    assert len(d["cvegeo"]) == 5875 and len(d["componentes"]["prob_apertura"]) == 5875
    assert "viabilidad" in d["componentes"]
    # un municipio recorta
    c = cliente.get("/api/scores/heladeria", params={"municipio": "09003", "componentes": "false"}).json()
    assert 0 < c["n"] < 400 and all(cv.startswith("09003") for cv in c["scores"]) and "componentes" not in c
    assert cliente.get("/api/scores/no_existe").status_code == 404
    assert cliente.get("/api/scores/Heladería").status_code == 200  # con acentos tambien


def test_comparar(cliente):
    r = cliente.get("/api/comparar", params={"giros": "heladeria,cafeteria,papeleria"})
    assert r.status_code == 200
    d = r.json()
    sin_nan(d)
    assert [g["clave"] for g in d["giros"]] == ["heladeria", "cafeteria", "papeleria"]
    m = pd.read_csv("models/metricas_giro.csv").set_index("giro")
    for g in d["giros"]:
        assert g["negocios_denue"] > 100 and g["negocios_denue_hist"] > 100
        assert g["aperturas"] == int(m.at[g["clave"], "aperturas"])
        assert g["auc"] == pytest.approx(m.at[g["clave"], "auc_modelo"], abs=1e-3)
        assert g["tasa_base_pct"] == pytest.approx(100 * m.at[g["clave"], "tasa_base"], abs=0.1)
        assert 0 < g["prob_apertura_media_pct"] < 100 and g["mejor_municipio"]["municipio"]
        assert 0 < g["viabilidad_media_pct"] <= g["prob_apertura_media_pct"]
        assert len(g["top"]) == 10 and g["top"][0]["posicion"] == 1
        colonias = [(z["municipio"], z["colonia"]) for z in g["top"]]
        assert len(set(colonias)) == 10  # una por colonia
        scores = [z["score"] for z in g["top"]]
        assert scores == sorted(scores, reverse=True)
    assert "percentil" in d["notas"]["score"] and "×" in d["notas"]["viabilidad"]
    assert cliente.get("/api/comparar", params={"giros": "a_ver_si_existe"}).status_code == 404
    assert cliente.get("/api/comparar", params={"giros": ""}).status_code == 422
    cinco = "heladeria,cafeteria,papeleria,farmacia,gimnasio"
    assert cliente.get("/api/comparar", params={"giros": cinco}).status_code == 422


def test_denue_muestrea(cliente):
    d = cliente.get("/api/denue/papeleria", params={"max": 300}).json()
    assert d["total"] > 300 and d["mostrados"] == 300 and d["muestreado"] is True
    lon, lat, nombre = d["puntos"][0]
    assert -100.5 < lon < -98 and 18.9 < lat < 20.2
    d2 = cliente.get("/api/denue/papeleria", params={"max": 300}).json()
    assert d2["puntos"] == d["puntos"]  # misma muestra cada vez
    mun = cliente.get("/api/denue/papeleria", params={"municipio": "09003", "max": 20000}).json()
    assert 0 < mun["total"] < d["total"] and mun["muestreado"] is False and mun["mostrados"] == mun["total"]
    # el conteo del DENUE coincide con el de comparar
    comp = cliente.get("/api/comparar", params={"giros": "papeleria"}).json()["giros"][0]
    assert comp["negocios_denue"] == d["total"]
    assert d["fuente"].startswith("DENUE corte ")
    assert cliente.get("/api/denue/no_existe").status_code == 404


def test_sugerir(cliente):
    r = cliente.get("/api/sugerir", params={"municipio": "09003", "top": 5})
    assert r.status_code == 200
    d = r.json()
    sin_nan(d)
    assert d["encontrado"] and 1 <= len(d["giros"]) <= 5
    via = [g["viabilidad_pct"] for g in d["giros"]]
    assert via == sorted(via, reverse=True)
    assert all(g["nombre"] for g in d["giros"]) and "relativo" in d["como_leer"]
    assert d["filtros"]["municipio"] == "Coyoacán"
    otro = cliente.get("/api/sugerir", params={"municipio": "09003", "nse": "alto", "ticket_max": 150}).json()
    assert otro["filtros"]["nse"] == "alto" and all(g["ticket_promedio_mxn"] <= 150 for g in otro["giros"])
    assert cliente.get("/api/sugerir", params={"nse": "rosa"}).status_code == 422
    assert cliente.get("/api/sugerir", params={"municipio": "99999"}).status_code == 422


def test_transporte(cliente):
    d = cliente.get("/api/transporte").json()
    sin_nan(d)
    assert d["n"] == len(d["estaciones"]) > 300
    assert {"Metro", "Metrobus"} <= set(d["sistemas"])
    e = next(x for x in d["estaciones"] if x["sistema"] == "Metro")
    assert {"linea", "estacion", "lat", "lon", "afluencia_anual"} <= set(e)
    todas = cliente.get("/api/transporte", params={"solo_operando": "false"}).json()
    assert todas["n"] >= d["n"]
