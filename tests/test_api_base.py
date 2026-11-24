"""Pruebas de la API Base del tablero (sin Ollama ni red): estado, giros, municipios, geo y la app web."""
import pytest
from fastapi.testclient import TestClient

from app.servidor import crear_app


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    web = tmp_path_factory.mktemp("web")
    (web / "index.html").write_text('<!doctype html><div id="root"></div>', encoding="utf-8")
    (web / "assets").mkdir()
    (web / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    return TestClient(crear_app(web))


def test_estado(cliente, monkeypatch):
    r = cliente.get("/api/estado")
    assert r.status_code == 200
    d = r.json()
    assert set(d) >= {"ollama", "internet", "cortes", "kpis", "fuentes"}
    assert isinstance(d["ollama"]["prendido"], bool) and isinstance(d["internet"], bool)
    k = d["kpis"]
    assert k["agebs"] == 5875 and k["municipios"] == 76 and k["giros"] == 40
    assert k["negocios_denue"] > 1_000_000
    assert 0.5 < k["auc_global"] < 1
    # AUC medio dentro de cada giro: sale de models/metricas_giro.csv, sin los giros con menos de 30 AGEB con apertura
    import csv, pathlib
    filas = list(csv.DictReader((pathlib.Path(__file__).resolve().parents[1] / "models" / "metricas_giro.csv").open(encoding="utf-8")))
    esperados = [float(r["auc_modelo"]) for r in filas if int(float(r["agebs_con_apertura"])) >= 30]
    assert k["auc_medio_giro_n"] == len(esperados)
    assert k["auc_medio_giro"] == pytest.approx(sum(esperados) / len(esperados))
    assert k["auc_medio_giro"] < k["auc_global"]  # el global mezcla giros y es la cifra más favorable
    assert "metricas_giro.csv" in d["fuentes"]["auc_medio_giro"]
    assert d["cortes"]["denue_actual"] == "05/2026" and d["cortes"]["denue_hist"] == "11/2020"
    import json, pathlib
    ev = json.loads((pathlib.Path(__file__).resolve().parents[1] / "reports" / "evaluacion.json").read_text())
    assert k["evaluacion"]["total"] == ev["preguntas"] >= 28


def test_estado_sin_ollama(cliente, monkeypatch):
    from app.api import base

    monkeypatch.setattr(base, "OLLAMA_URL", "http://127.0.0.1:9")  # nadie escucha
    base._cache_red.pop("ollama", None)
    d = cliente.get("/api/estado").json()
    assert d["ollama"] == {"prendido": False, "modelos": [], "faltan": ["qwen3:8b", "nomic-embed-text"], "cargados": []}
    base._cache_red.pop("ollama", None)


def test_giros(cliente):
    d = cliente.get("/api/giros").json()
    claves = {g["clave"] for g in d["giros"]}
    assert len(claves) == 40 and "heladeria" in claves
    h = next(g for g in d["giros"] if g["clave"] == "heladeria")
    assert h["nombre"] == "Heladería"  # nombre visible con acento (config/giros.yaml va sin acentos)
    assert next(g for g in d["giros"] if g["clave"] == "optica")["nombre"] == "Óptica"
    nombres = [g["nombre"] for g in d["giros"]]
    assert nombres.index("Óptica") < nombres.index("Panadería")  # el orden ignora los acentos
    assert d["fuente"]


def test_municipios(cliente):
    d = cliente.get("/api/municipios").json()
    m = d["municipios"]
    assert len(m) == 76
    assert {x["cve_ent"] for x in m} == {"09", "13", "15"}
    assert sum(x["cve_ent"] == "09" for x in m) == 16
    assert all(len(x["cvegeo_mun"]) == 5 for x in m)


def test_geo_agebs(cliente):
    r = cliente.get("/api/geo/agebs", headers={"Accept-Encoding": "gzip"})
    assert r.status_code == 200 and r.headers["content-encoding"] == "gzip"
    assert int(r.headers["x-geo-bytes-gzip"]) < 800_000 < int(r.headers["x-geo-bytes"])  # comprimido vs crudo (~2.5 MB)
    g = r.json()  # el cliente descomprime
    assert g["type"] == "FeatureCollection" and len(g["features"]) == 5875
    p = g["features"][0]["properties"]
    assert set(p) == {"cvegeo", "colonia", "municipio"} and len(p["cvegeo"]) == 13
    # a 5 decimales como maximo
    x = g["features"][0]["geometry"]["coordinates"]
    while isinstance(x[0], list):
        x = x[0]
    assert len(str(x[0]).split(".")[1]) <= 5


def test_geo_agebs_sin_gzip(cliente):
    r = cliente.get("/api/geo/agebs", headers={"Accept-Encoding": "identity"})
    assert r.status_code == 200 and "content-encoding" not in r.headers
    assert len(r.json()["features"]) == 5875


def test_geo_municipios(cliente):
    g = cliente.get("/api/geo/municipios").json()
    assert len(g["features"]) == 76
    assert set(g["features"][0]["properties"]) == {"cvegeo_mun", "municipio"}


def test_inicio_demo(cliente):
    d = cliente.get("/api/inicio/demo").json()
    assert d["giro"] == "heladeria" and len(d["zonas"]) == 5
    assert len(d["puntos"]) > 5000 and len(d["puntos"][0]) == 4 and len(d["puntos"][0][3]) == 13


def test_index_y_fallback(cliente):
    r = cliente.get("/")
    assert r.status_code == 200 and 'id="root"' in r.text
    assert 'id="root"' in cliente.get("/zona/09002").text  # ruta desconocida del cliente -> index.html
    a = cliente.get("/assets/app.js")
    assert a.status_code == 200 and "immutable" in a.headers["cache-control"]


def test_api_inexistente_es_404_json(cliente):
    r = cliente.get("/api/no-existe")
    assert r.status_code == 404 and "error" in r.json()


def test_no_sale_de_la_carpeta_web(cliente):
    r = cliente.get("/..%2f..%2fpyproject.toml")
    assert "tool.uv" not in r.text


def test_sin_build_web(tmp_path):
    c = TestClient(crear_app(tmp_path / "no_hay"))
    r = c.get("/")
    assert r.status_code == 503 and "make web" in r.json()["error"]
    assert c.get("/api/giros").status_code == 200  # la API vive aunque falte el build


def test_precalentar_existe_y_no_corre_en_crear_app():
    """El servidor precalienta geometria y motor en un hilo desde main(); crear_app() no debe cargar nada."""
    from app.api import base
    from app.servidor import crear_app

    assert callable(base.precalentar)
    antes = dict(base._geo)
    crear_app()
    assert dict(base._geo) == antes
