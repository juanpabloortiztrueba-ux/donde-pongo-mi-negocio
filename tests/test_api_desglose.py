"""Pruebas del panel de desglose (app/api/desglose.py): GET /api/zona/{cvegeo}/desglose?giro=.

Usan el motor y los datos reales (sin LLM, sin Ollama, sin red).
"""
import time

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import motor
from app.servidor import crear_app

GIRO = "heladeria"


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    web = tmp_path_factory.mktemp("web")
    (web / "index.html").write_text('<!doctype html><div id="root"></div>', encoding="utf-8")
    return TestClient(crear_app(web))


@pytest.fixture(scope="module")
def parquet():
    """Los scores del giro, tal cual los guardó el entrenamiento (la verdad contra la que se compara la API)."""
    return pd.read_parquet(motor.MODELS / "scores_giros.parquet", filters=[("giro", "==", GIRO)]).reset_index(drop=True)


def _cv(parquet, lugar: int) -> str:
    return parquet.sort_values("score", ascending=False).cvegeo.iloc[lugar - 1]


def test_suma_de_aportes_casa_con_el_score(cliente, parquet):
    for lugar in (1, 37, 2500, 5875):
        cv = _cv(parquet, lugar)
        j = cliente.get(f"/api/zona/{cv}/desglose?giro={GIRO}").json()
        sc = j["score"]
        esperado = float(parquet.set_index("cvegeo").loc[cv, "score"])
        assert sc["valor"] == pytest.approx(esperado, abs=0.006)
        assert sc["suma_aportes"] == pytest.approx(esperado, abs=0.006)
        assert sum(c["aporte"] for c in sc["componentes"]) == pytest.approx(esperado, abs=0.03)  # cada aporte va redondeado a 2 decimales
        assert sum(c["peso"] for c in sc["componentes"]) == pytest.approx(1.0, abs=1e-3)
        for c in sc["componentes"]:  # aporte = 100 · peso · percentil
            assert c["aporte"] == pytest.approx(c["peso"] * c["percentil"], abs=0.05)
            assert c["fuente"] and c["etiqueta"] and c["descripcion"]


def test_los_pesos_son_los_del_motor_no_los_de_la_vista(cliente, parquet):
    j = cliente.get(f"/api/zona/{_cv(parquet, 10)}/desglose?giro={GIRO}").json()
    por = {c["clave"]: c for c in j["score"]["componentes"]}
    assert set(por) == set(motor.PESOS_SCORE)
    for k, w in motor.PESOS_SCORE.items():
        assert por[k]["peso"] == pytest.approx(w / sum(motor.PESOS_SCORE.values()), abs=1e-3)
    assert j["score"]["version"] == motor.SCORE_VERSION and "pesos_score.json" in j["score"]["pesos_fuente"]


def test_giro_sin_rubro_enigh_pasa_el_peso_a_poblacion(cliente):
    sin = [k for k, g in motor.giros().items() if not g.get("rubro_enigh")]
    if not sin:
        pytest.skip("todos los giros tienen rubro ENIGH")
    cv = motor.score_giro(sin[0]).cvegeo.iloc[0]
    sc = cliente.get(f"/api/zona/{cv}/desglose?giro={sin[0]}").json()["score"]
    por = {c["clave"]: c for c in sc["componentes"]}
    assert por["demanda_neta"]["aplica"] is False and por["demanda_neta"]["peso"] == 0 and por["demanda_neta"]["nota"]
    assert sc["suma_aportes"] == pytest.approx(sc["valor"], abs=0.006)


def test_el_lugar_casa_con_el_parquet(cliente, parquet):
    ord_ = parquet.sort_values("score", ascending=False).reset_index(drop=True)
    for lugar in (1, 5, 37, 3000, 5875):
        cv = ord_.cvegeo.iloc[lugar - 1]
        lg = cliente.get(f"/api/zona/{cv}/desglose?giro={GIRO}").json()["score"]["lugar"]
        assert lg["de"] == len(parquet) == 5875
        assert lg["posicion"] == lugar
        assert lg["en_top_5"] is (lugar <= 5)
        assert lg["mejor_que_pct"] == pytest.approx(100 * (5875 - lugar) / 5874, abs=0.06)
        # lugar dentro del municipio: cuántas AGEB del mismo municipio tienen mejor score
        mun = ord_[ord_.cvegeo.str[:5] == cv[:5]]
        assert lg["municipio"]["de"] == len(mun) and lg["municipio"]["posicion"] == 1 + list(mun.cvegeo).index(cv)
        assert lg["fuente"]


def test_aperturas_y_probabilidades_son_las_del_parquet(cliente, parquet):
    cv = _cv(parquet, 37)
    sc = cliente.get(f"/api/zona/{cv}/desglose?giro={GIRO}").json()["score"]
    f = parquet.set_index("cvegeo").loc[cv]
    assert sc["prob_apertura_pct"] == pytest.approx(100 * f["prob_apertura"], abs=0.06)
    assert sc["competidores_ponderados"] == pytest.approx(f["competencia"], abs=0.006)


def test_sin_giro_trae_todo_menos_el_score(cliente, parquet):
    cv = _cv(parquet, 37)
    for url in (f"/api/zona/{cv}/desglose", f"/api/zona/{cv}/desglose?giro="):
        j = cliente.get(url).json()
        assert j["score"] is None and j["competencia"] is None and j["giro"] is None
        assert "Elige un giro" in j["nota_giro"]
        assert j["poblacion"]["habitantes"] and j["ingreso"]["decil"]["ageb"] and j["transporte"]["estaciones"] and j["flujo"]["poblacion_diurna"] is not None
    j = cliente.get(f"/api/zona/{cv}/desglose?giro=no_existe").json()  # un giro que no existe no tumba el panel
    assert j["score"] is None and "NO ENCONTRADO" in j["nota_giro"] and j["giro_pedido"] == "no_existe"


def test_el_giro_acepta_el_nombre_visible(cliente, parquet):
    cv = _cv(parquet, 37)
    j = cliente.get(f"/api/zona/{cv}/desglose", params={"giro": "Heladería"}).json()
    assert j["giro"] == {"clave": GIRO, "nombre": "Heladería"} and j["score"]["valor"]


def test_ageb_inexistente_es_404_en_espanol(cliente):
    for cv in ("0000000000000", "XYZ", "9" * 13):
        r = cliente.get(f"/api/zona/{cv}/desglose?giro={GIRO}")
        assert r.status_code == 404
        assert "NO ENCONTRADO" in r.json()["error"] and "AGEB" in r.json()["error"]


def test_fuentes_presentes_en_cada_bloque(cliente, parquet):
    j = cliente.get(f"/api/zona/{_cv(parquet, 37)}/desglose?giro={GIRO}").json()
    for bloque in ("poblacion", "ingreso", "flujo", "transporte"):
        assert j[bloque]["fuente"], bloque
    assert j["score"]["fuente"] and j["score"]["lugar"]["fuente"]
    assert j["competencia"]["competidores"]["fuente"] and j["competencia"]["complementarios"]["fuente"]
    assert len(j["fuentes"]) >= 4 and all(isinstance(s, str) and s for s in j["fuentes"])
    assert "DENUE" in j["competencia"]["competidores"]["fuente"]


def test_comparacion_con_municipio_y_zmvm(cliente, parquet):
    j = cliente.get(f"/api/zona/{_cv(parquet, 37)}/desglose?giro={GIRO}").json()
    g = j["poblacion"]["grupos_edad"]
    assert [x["grupo"] for x in g] == ["0-14", "15-24", "25-59", "60+"]
    for x in g:
        assert x["pct_ageb"] is not None and x["pct_municipio"] is not None and x["pct_zmvm"] is not None
    assert sum(x["pct_zmvm"] for x in g) == pytest.approx(100, abs=0.5)
    ing = j["ingreso"]
    assert {"ageb", "municipio", "zmvm"} == set(ing["decil"]) == set(ing["ingreso_trim_mediano_mxn"])
    assert ing["ingreso_trim_mediano_mxn"]["zmvm"] > 0 and ing["nse"] in ("bajo", "medio", "alto")
    assert {"bajo", "medio", "alto"} == set(ing["prob_nse_pct"])


def test_competidores_con_nombre_y_distancia_ordenados(cliente, parquet):
    c = cliente.get(f"/api/zona/{_cv(parquet, 37)}/desglose?giro={GIRO}").json()["competencia"]
    assert c["radio_m"] == motor.giros()[GIRO]["radio_influencia_m"]
    for bloque in ("competidores", "complementarios"):
        b = c[bloque]
        assert b["en_radio"] >= 0 and b["total_zmvm"] > 0 and 1 <= len(b["cercanos"]) <= 5
        d = [x["distancia_m"] for x in b["cercanos"]]
        assert d == sorted(d) and all(x["nombre"] for x in b["cercanos"])
        assert b["en_radio"] >= sum(1 for x in b["cercanos"] if x["en_radio"])
    # el más cercano es de verdad un establecimiento del DENUE del giro: su SCIAN está en el catálogo
    g = motor.giros()[GIRO]
    scian = {str(s) for s in g["scian"]} | {str(f["codigos"][0]) for f in g.get("scian_con_filtro", [])}
    assert c["competidores"]["cercanos"][0]["scian"] in scian


def test_transporte_y_flujo(cliente, parquet):
    cv = _cv(parquet, 1)
    j = cliente.get(f"/api/zona/{cv}/desglose?giro={GIRO}").json()
    e = j["transporte"]["estaciones"]
    assert 1 <= len(e) <= 5 and [x["distancia_m"] for x in e] == sorted(x["distancia_m"] for x in e) and e[0]["estacion"]
    f = j["flujo"]
    assert f["poblacion_diurna"] >= 0 and f["empleos_500m"] >= 0 and f["empleos_1km"] >= f["empleos_500m"]
    assert f["en_radio_del_giro"]["radio_m"] == motor.giros()[GIRO]["radio_influencia_m"]


def test_rapido_tras_la_primera_llamada_y_con_cache(cliente, parquet):
    cv = _cv(parquet, 37)
    cliente.get(f"/api/zona/{cv}/desglose?giro={GIRO}")  # la primera paga la carga del motor
    for lugar in (2, 100, 4000):
        t0 = time.perf_counter()
        r = cliente.get(f"/api/zona/{_cv(parquet, lugar)}/desglose?giro={GIRO}")
        dt = time.perf_counter() - t0
        assert r.status_code == 200 and dt < 0.3, f"{dt:.3f} s"
    t0 = time.perf_counter()
    cliente.get(f"/api/zona/{cv}/desglose")
    assert time.perf_counter() - t0 < 0.3


def test_json_sin_nan(cliente, parquet):
    r = cliente.get(f"/api/zona/{_cv(parquet, 5000)}/desglose?giro={GIRO}")
    assert r.status_code == 200 and "NaN" not in r.text and "Infinity" not in r.text


def test_sin_denue_con_coordenadas_quedan_los_conteos_del_modelo(cliente, parquet, monkeypatch):
    from app.api import desglose

    def sin_puntos(clave, tipo):
        raise FileNotFoundError("data/processed/denue_actual.parquet")

    monkeypatch.setattr(desglose, "_negocios", sin_puntos)
    j = cliente.get(f"/api/zona/{_cv(parquet, 37)}/desglose?giro={GIRO}").json()
    for b in ("competidores", "complementarios"):
        c = j["competencia"][b]
        assert c["cercanos"] == [] and c["sin_puntos"] is True and "NO ENCONTRADO" in c["motivo"]
        assert c["en_radio"] is None and c["ponderados"] is not None   # sigue el conteo ponderado del modelo
