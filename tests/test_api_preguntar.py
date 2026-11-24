"""Pruebas de la API de Preguntar y Ficha de zona (app/api/preguntar.py).

El LLM va simulado (monkeypatch de agente.responder): estas pruebas no cargan Ollama ni usan red. La prueba con
rapido=true corre las herramientas reales (motor y herramientas validados), sin LLM.
"""
import time

import pytest
from fastapi.testclient import TestClient

from app import agente
from app.api import preguntar
from app.servidor import crear_app


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    web = tmp_path_factory.mktemp("web")
    (web / "index.html").write_text('<!doctype html><div id="root"></div>', encoding="utf-8")
    return TestClient(crear_app(web))


def _esperar(cliente, pid, estados=("listo", "error", "cancelada"), tope=15):
    t0 = time.time()
    while time.time() - t0 < tope:
        v = cliente.get(f"/api/preguntas/{pid}").json()
        if v["estado"] in estados:
            return v
        time.sleep(0.05)
    raise AssertionError(f"la pregunta {pid} no termino: {v}")


# ---------------------------------------------------------------- rapido (herramientas reales, sin LLM)
def test_pregunta_rapida_real(cliente):
    r = cliente.post("/api/preguntas", json={"pregunta": "Quiero poner una heladería", "rapido": True})
    assert r.status_code == 200
    j = r.json()
    assert j["estado"] == "listo" and j["modo"] == "rapido" and j["posicion_en_cola"] == 0
    d = j["datos"]
    assert d["giro"] == {"clave": "heladeria", "nombre": "Heladería"}
    assert len(d["zonas"]) == 5
    z = d["zonas"][0]
    assert len(z["ageb"]) == 13 and 0 <= z["score"] <= 100 and z["colonia"]
    assert [x["score"] for x in d["zonas"]] == sorted((x["score"] for x in d["zonas"]), reverse=True)
    assert len(d["mapa"]["valores"]) == 5875 and set(z["ageb"] for z in d["zonas"]) <= set(d["mapa"]["valores"])
    assert d["corte_denue"] == "05/2026" and d["fuentes"]
    assert "**Fuentes:**" in j["respuesta"] and "Top 5" in j["respuesta"]
    assert [h["nombre"] for h in j["herramientas"]][:2] == ["perfil_giro", "recomendar_zonas"]
    # GET trae lo mismo, y con completo=1 tambien los datos
    g = cliente.get(f"/api/preguntas/{j['id']}").json()
    assert g["estado"] == "listo" and g["respuesta"] == j["respuesta"] and "datos" not in g and g["fuentes"]
    assert cliente.get(f"/api/preguntas/{j['id']}?completo=1").json()["datos"]["giro"]["clave"] == "heladeria"


def test_fuera_de_alcance(cliente):
    j = cliente.post("/api/preguntas", json={"pregunta": "Quiero abrir una taquería en Monterrey", "rapido": True}).json()
    d = j["datos"]
    assert d["zonas"] == [] and d["fuera_de_alcance"]["fuera_de_zmvm"] is True
    assert "Monterrey" in d["fuera_de_alcance"]["motivo"] and d.get("mapa") is None
    assert "NO ENCONTRADO" not in j["respuesta"] or "fuera" in j["respuesta"].lower()


def test_sin_giro_sugiere_giros(cliente):
    d = cliente.post("/api/preguntas", json={"pregunta": "¿Qué negocio pongo en Coyoacán?", "rapido": True}).json()["datos"]
    assert d["sugerencias"] and d["sugerencias"][0]["nombre"] and 0 <= d["sugerencias"][0]["viabilidad_pct"] <= 100
    assert d["zonas"] and all(z["municipio"] == "Coyoacán" for z in d["zonas"]) and d["mapa"]["municipio"] == "09003"


def test_historial_hereda_el_giro(cliente):
    h = [{"role": "user", "content": "Quiero poner una heladería"}, {"role": "assistant", "content": "Respuesta anterior"}]
    d = cliente.post("/api/preguntas", json={"pregunta": "¿y en Coyoacán?", "historial": h, "rapido": True}).json()["datos"]
    assert d["giro"]["clave"] == "heladeria" and d["zonas"] and d["zonas"][0]["municipio"] == "Coyoacán"


def test_validacion_de_la_pregunta(cliente):
    assert cliente.post("/api/preguntas", json={"pregunta": " "}).status_code == 422
    assert cliente.post("/api/preguntas", json={"pregunta": "x" * 601}).status_code == 422
    assert cliente.post("/api/preguntas", json={}).status_code == 422
    r = cliente.get("/api/preguntas/noexiste")
    assert r.status_code == 404 and "error" in r.json()


def test_sin_ollama_cae_a_plantilla(cliente, monkeypatch):
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: False)
    j = cliente.post("/api/preguntas", json={"pregunta": "farmacia en Iztapalapa"}).json()
    assert j["estado"] == "listo" and j["modo"] == "plantilla" and "Ollama" in j["aviso"] and j["respuesta"]


# ---------------------------------------------------------------- LLM simulado: cola, estados y errores
def test_llm_simulado_estados_y_cola(cliente, monkeypatch):
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: True)
    activos, maximo, orden = [0], [0], []

    def falso(pregunta, historial=None, **_):
        activos[0] += 1
        maximo[0] = max(maximo[0], activos[0])
        orden.append(pregunta)
        time.sleep(0.5)
        activos[0] -= 1
        return {"respuesta": f"Respuesta de {pregunta}\n\n**Fuentes:** x.", "herramientas": [{"nombre": "perfil_giro", "args": {}, "resultado": {"encontrado": True}}],
                "latencia_s": 0.5, "modo": "llm", "modelo": "qwen3:8b", "rondas": 1, "herencia": None, "cortada": False, "metricas": {}}

    monkeypatch.setattr(agente, "responder", falso)
    a = cliente.post("/api/preguntas", json={"pregunta": "quiero poner una papeleria"}).json()
    b = cliente.post("/api/preguntas", json={"pregunta": "quiero poner una panaderia"}).json()
    assert a["datos"]["zonas"] and a["estado"] in ("en_cola", "pensando") and a["ollama"] is True
    assert b["estado"] == "en_cola" and b["posicion_en_cola"] >= 1  # la segunda espera: un LLM a la vez
    va = _esperar(cliente, a["id"])
    assert va["estado"] == "listo" and va["modo"] == "llm" and va["modelo"] == "qwen3:8b" and va["respuesta"].startswith("Respuesta de quiero poner una papeleria")
    vb = _esperar(cliente, b["id"])
    assert vb["estado"] == "listo" and vb["segundos"] >= 0
    assert maximo[0] == 1 and orden == ["quiero poner una papeleria", "quiero poner una panaderia"]


def test_cancelar_en_cola(cliente, monkeypatch):
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: True)
    monkeypatch.setattr(agente, "responder", lambda p, h=None, **_: (time.sleep(0.6), {"respuesta": "ok", "herramientas": [], "latencia_s": 0.6, "modo": "llm", "modelo": "qwen3:8b"})[1])
    a = cliente.post("/api/preguntas", json={"pregunta": "quiero poner una tortilleria"}).json()
    b = cliente.post("/api/preguntas", json={"pregunta": "quiero poner una libreria"}).json()
    assert cliente.delete(f"/api/preguntas/{b['id']}").json()["estado"] == "cancelada"
    assert _esperar(cliente, a["id"])["estado"] == "listo"
    time.sleep(0.8)
    assert cliente.get(f"/api/preguntas/{b['id']}").json()["estado"] == "cancelada"  # el hilo no la contesto


def test_error_del_llm(cliente, monkeypatch):
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: True)

    def roto(*a, **k):
        raise RuntimeError("se cayo")

    monkeypatch.setattr(agente, "responder", roto)
    j = cliente.post("/api/preguntas", json={"pregunta": "quiero poner una zapateria"}).json()
    v = _esperar(cliente, j["id"])
    assert v["estado"] == "error" and "se cayo" in v["error"]


def test_llm_que_cae_a_plantilla(cliente, monkeypatch):
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: True)
    monkeypatch.setattr(agente, "responder", lambda p, h=None, **_: {"respuesta": "armada sin LLM", "herramientas": [], "latencia_s": 1, "modo": "plantilla", "modelo": "qwen3:8b"})
    j = cliente.post("/api/preguntas", json={"pregunta": "quiero poner una floreria"}).json()
    v = _esperar(cliente, j["id"])
    assert v["estado"] == "listo" and v["modo"] == "plantilla" and v["aviso"]


# ---------------------------------------------------------------- ficha de zona
AGEB = "0900700010017"  # Juan Escutia, Iztapalapa


def test_ficha_con_giro(cliente):
    r = cliente.get(f"/api/zona/{AGEB}?giro=farmacia")
    assert r.status_code == 200
    f = r.json()
    assert f["ageb"] == AGEB and f["municipio"] == "Iztapalapa" and f["colonia"] == "Juan Escutia"
    assert f["poblacion"]["habitantes"] > 0 and f["poblacion"]["fuente"]
    ed = f["edades"]["grupos"]
    assert [e["grupo"] for e in ed] == ["0-14", "15-24", "25-59", "60+"]
    assert abs(sum(e["pct"] for e in ed) - 100) < 1 and abs(sum(e["pct_zmvm"] for e in ed) - 100) < 1
    assert {b["clave"] for b in f["vivienda"]["bienes"]} == {"pct_viv_auto", "pct_viv_internet", "pct_viv_pc", "pct_viv_celular"}
    assert f["escolaridad"]["anios"] and f["escolaridad"]["anios_zmvm"]
    assert f["marginacion"]["grado"] in ("Muy bajo", "Bajo", "Medio", "Alto", "Muy alto") and sum(x["agebs"] for x in f["marginacion"]["grados_zmvm"]) == f["marginacion"]["n_agebs"] and f["marginacion"]["n_agebs"] + f["marginacion"]["sin_grado"] == 5875
    assert 1 <= f["ingreso"]["decil"] <= 10 and len(f["ingreso"]["prob_deciles_pct"]) == 10 and abs(sum(f["ingreso"]["prob_deciles_pct"]) - 100) < 1
    e = f["empleo"]
    assert e["negocios_1km"] >= e["negocios_500m"] and e["sectores"] and e["sectores"][0]["n_1km"] >= e["sectores"][-1]["n_1km"] and "DENUE corte" in e["fuente"]
    assert f["transporte"]["estacion"] and f["transporte"]["distancia_m"] >= 0
    g = f["giro"]
    assert g["clave"] == "farmacia" and g["nombre"] == "Farmacia" and 0 <= g["score"] <= 100 and 0 <= g["percentil"] <= 100
    assert g["rank_zmvm"] <= g["de_agebs"] == 5875 and g["fuente"]
    v = f["vecinas"]
    assert AGEB in v["valores"] and v["dominio"] == [0, 100] and 20 < len(v["valores"]) < 600


def test_ficha_sin_giro_y_errores(cliente):
    f = cliente.get(f"/api/zona/{AGEB}").json()
    assert "giro" not in f and f["vecinas"]["dominio"] == [1, 10] and AGEB in f["vecinas"]["valores"]
    f = cliente.get(f"/api/zona/{AGEB}?giro=nogiro").json()
    assert "giro" not in f and f["giro_no_encontrado"] == "nogiro"
    r = cliente.get("/api/zona/0000000000000")
    assert r.status_code == 404 and "NO ENCONTRADO" in r.json()["error"]
    # nada de NaN: la respuesta es JSON valido y los datos que faltan salen como null
    assert cliente.get(f"/api/zona/{AGEB}").text.count("NaN") == 0


# ---------------------------------------------------------------- buscador
def test_buscar_zona(cliente):
    j = cliente.get("/api/buscar_zona", params={"q": "del valle"}).json()
    nombres = [r["colonia"] for r in j["resultados"]]
    assert "Del Valle Centro" in nombres and j["fuente"]
    r0 = next(r for r in j["resultados"] if r["colonia"] == "Del Valle Centro")
    assert r0["municipio"] == "Benito Juárez" and r0["agebs"][0]["cvegeo"].startswith("09014") and r0["n_agebs"] == len(r0["agebs"])
    # por municipio (clave de 5 digitos o nombre)
    m = cliente.get("/api/buscar_zona", params={"q": "", "municipio": "09003"}).json()["resultados"]
    assert m and all(r["cvegeo_mun"] == "09003" for r in m) and m[0]["habitantes"] >= m[-1]["habitantes"]
    assert cliente.get("/api/buscar_zona", params={"q": "polanco", "municipio": "Miguel Hidalgo"}).json()["resultados"]
    # por clave AGEB
    k = cliente.get("/api/buscar_zona", params={"q": AGEB[:10]}).json()["resultados"]
    assert k and all(a["cvegeo"].startswith(AGEB[:10]) for r in k for a in r["agebs"])


def test_buscar_zona_sin_resultados(cliente):
    j = cliente.get("/api/buscar_zona", params={"q": "xyzqw"}).json()
    assert j["resultados"] == [] and "NO ENCONTRADO" in j["motivo"]
    assert "2 letras" in cliente.get("/api/buscar_zona", params={"q": "a"}).json()["motivo"]
    assert cliente.get("/api/buscar_zona", params={"q": "del valle", "municipio": "Narnia"}).json()["resultados"] == []


def test_nombres_de_colonia():
    assert preguntar._nombre_colonia("POLANCO III SECCIÓN") == "Polanco III Sección"
    assert preguntar._nombre_colonia("PEDREGAL DE SANTO DOMINGO") == "Pedregal de Santo Domingo"
    assert preguntar._nombre_colonia("Ya Normal") == "Ya Normal" and preguntar._nombre_colonia(None) is None
