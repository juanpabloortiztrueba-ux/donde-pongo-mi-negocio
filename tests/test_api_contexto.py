"""Pruebas de la API del grupo «contexto» (Macro, El modelo, Datos y carpetas). Sin Ollama ni red."""
import os
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import contexto
from app.servidor import crear_app

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    web = tmp_path_factory.mktemp("web")
    (web / "index.html").write_text('<!doctype html><div id="root"></div>', encoding="utf-8")
    return TestClient(crear_app(web))


# ---------------------------------------------------------------- datos nuevos: scripts/01d_macro_series.py
def test_macro_series_parquet():
    import pandas as pd

    d = pd.read_parquet(RAIZ / "data" / "processed" / "macro_series.parquet")
    assert list(d.columns) == ["serie", "fecha", "valor", "unidad", "fuente", "id_serie"]
    assert {"tasa_objetivo", "tiie_28", "tipo_cambio_fix", "remesas", "inpc_general_var_anual", "confianza_consumidor", "consumo_privado_var_anual"} <= set(d["serie"])
    assert d["fecha"].min() >= pd.Timestamp("2015-01-01") and d["fecha"].max() >= pd.Timestamp("2026-01-01")
    assert d["valor"].notna().all() and (d.groupby("serie").size() > 100).all()
    assert d["fuente"].str.contains("Banco de Mexico|INEGI").all() and d["id_serie"].str.len().gt(3).all()


def test_ningun_token_en_los_archivos_nuevos():
    """Los tokens de .env no aparecen en el parquet ni en FUENTES.md (se compara sin imprimirlos)."""
    env = RAIZ / ".env"
    if not env.exists():
        pytest.skip("sin .env")
    valores = [ln.split("=", 1)[1].strip().strip("\"'") for ln in env.read_text(encoding="utf-8").splitlines() if "=" in ln and "TOKEN" in ln.split("=")[0]]
    blob = (RAIZ / "data" / "FUENTES.md").read_text(encoding="utf-8") + (RAIZ / "data" / "processed" / "macro_series.parquet").read_bytes().decode("latin-1")
    blob += (RAIZ / "scripts" / "01d_macro_series.py").read_text(encoding="utf-8")
    fuga = [i for i, v in enumerate(valores) if len(v) > 6 and v in blob]
    assert fuga == []


def test_fuentes_tiene_la_seccion_01d_y_el_makefile_la_corre():
    md = (RAIZ / "data" / "FUENTES.md").read_text(encoding="utf-8")
    assert "<!-- 01d:inicio" in md and "<!-- 01d:fin -->" in md
    assert "scripts/01d_macro_series.py" in (RAIZ / "Makefile").read_text(encoding="utf-8")


# ---------------------------------------------------------------- /api/macro
def test_macro(cliente):
    d = cliente.get("/api/macro").json()
    assert d["aviso"] is None
    ind = d["indicadores"]
    assert ind["tasa_objetivo"]["id_serie"] == "SF61745" and ind["tasa_objetivo"]["fecha"] and ind["tasa_objetivo"]["valor"] > 0
    assert ind["inpc_alimentos_var_anual"]["estado"] == "NO ENCONTRADO"
    assert "_meta" not in ind and d["meta"]["generado"]
    claves = {s["clave"] for s in d["series"]}
    assert {"tasa_objetivo", "tiie_28", "tipo_cambio_fix", "remesas", "inpc_general_var_anual", "confianza_consumidor", "consumo_privado_var_anual"} <= claves
    s = next(s for s in d["series"] if s["clave"] == "tipo_cambio_fix")
    assert len(s["puntos"]) > 130 and re.fullmatch(r"\d{4}-\d{2}", s["puntos"][0][0]) and s["puntos"][0][0] == "2015-01"
    meses = [p[0] for p in s["puntos"]]
    assert meses == sorted(set(meses))  # un dato por mes, en orden
    assert s["id_serie"] == "SF43718" and "Banco de México" in s["fuente"] and s["unidad"]


# ---------------------------------------------------------------- /api/modelo
def test_modelo_lee_el_motor_en_vivo(cliente):
    from app import motor

    d = cliente.get("/api/modelo").json()
    sc = d["score"]
    assert sc["version"] == motor.SCORE_VERSION
    assert {t["clave"]: t["peso"] for t in sc["terminos"]} == pytest.approx(dict(motor.PESOS_SCORE))
    assert sum(t["peso_norm"] for t in sc["terminos"]) == pytest.approx(1.0)
    assert all(t["nombre"] and t["descripcion"] for t in sc["terminos"])


def test_modelo_validacion_y_giros(cliente):
    import json

    meta = json.loads((RAIZ / "models" / "metadata.json").read_text(encoding="utf-8"))
    d = cliente.get("/api/modelo").json()
    v = d["validacion"]
    assert v["auc_global"] == meta["validacion"]["auc_oof_global"]
    assert [p["auc"] for p in v["pliegues"]] == [p["auc"] for p in meta["pliegues"]] and len(v["pliegues"]) == 5
    assert len(d["giros"]) == 40
    h = next(g for g in d["giros"] if g["giro"] == "heladeria")
    assert h["nombre"] == "Heladería" and 0.5 < h["auc_modelo"] < 1 and h["auc_densidad"] is not None
    assert next(g for g in d["giros"] if g["giro"] == "renta_bicicletas")["poco_dato"] is True
    lb = d["lineas_base"]
    assert lb["giros"] == sum(1 for g in d["giros"] if not g["poco_dato"]) and lb["supera"]["densidad"] <= lb["giros"]
    assert d["sobrevivencia"]["auc_oof"] == meta["sobrevivencia"]["auc_oof"]


def test_modelo_importancia_en_espanol(cliente):
    imp = cliente.get("/api/modelo").json()["importancia"]
    assert len(imp) == 20
    assert [i["importancia"] for i in imp] == sorted((i["importancia"] for i in imp), reverse=True)
    assert all(i["nombre"] and not re.fullmatch(r"sec\d+_\w+", i["nombre"]) for i in imp)
    assert contexto._nombre_variable("sec46_1km") == "Negocios de comercio al por menor a 1 km"
    assert contexto._nombre_variable("variable_nueva_x") == "variable nueva x"


def test_modelo_evaluacion_limites_y_preguntas(cliente):
    d = cliente.get("/api/modelo").json()
    ev = d["evaluacion"]
    assert ev["preguntas"] >= 28 and len(ev["filas"]) == ev["preguntas"] and all(f["latencia_s"] > 0 for f in ev["filas"])
    claves = {x["clave"] for x in d["limites"]}
    assert {"aparecio", "colonia", "decil", "sobrevivencia", "raros"} <= claves
    for x in d["limites"]:
        assert x["fuente"] and x["texto"] and "NO ENCONTRADO" not in x["texto"], x["clave"]
    assert any("abrió" in x["texto"] for x in d["limites"] if x["clave"] == "aparecio")
    assert len(d["preguntas"]) >= 6 and all(q["pregunta"].startswith("¿") and q["respuesta"] and q["fuente"] for q in d["preguntas"])
    assert d["validacion_score"]["filas"]


def test_modelo_ejemplo_suma_el_score(cliente):
    r = cliente.get("/api/modelo/ejemplo?giro=heladeria&posicion=1")
    assert r.status_code == 200
    d = r.json()
    assert d["suma_terminos"] == pytest.approx(d["score"], abs=0.01)
    assert [t["acumulado"] for t in d["terminos"]] == sorted(t["acumulado"] for t in d["terminos"])
    assert all(0 <= t["percentil"] <= 1 for t in d["terminos"]) and d["colonia"] and d["municipio"]
    assert cliente.get("/api/modelo/ejemplo?giro=no_existe").status_code == 404


# ---------------------------------------------------------------- /api/fuentes
def test_fuentes(cliente):
    d = cliente.get("/api/fuentes").json()
    assert d["n_fuentes"] > 30
    filas = [f for s in d["secciones"] for f in s["filas"]]
    assert all(f["archivo"] for f in filas)
    assert any(f["url"].startswith("https://www.inegi.org.mx") and f["corte"] and f["sha256"] for f in filas)
    enigh = next(f for f in filas if f["archivo"].startswith("enigh2024_ns_gastoshogar"))
    assert enigh["url"].startswith("https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/microdatos/")  # la liga abreviada «...» se completa
    assert any("macro_series" in f["archivo"] for f in filas)
    assert d["reconstruir"]["comando"] == "make datos features entrenar indexar" and len(d["reconstruir"]["pasos"]) == 4
    assert d["bytes_procesados"] > 10_000_000 and any(p["archivo"] == "data/processed/macro_series.parquet" for p in d["procesados"])


def test_parser_de_viñetas_de_fuentes():
    f = contexto._bullet_fuente("`x.zip` | .../microdatos/x.zip | descargado 2026-01-02 | ENIGH 2024 | 1,234 bytes | sha256 `" + "a" * 64 + "` | borrado",
                                "https://sitio.mx/a/b/microdatos/otro.zip")
    assert f["url"] == "https://sitio.mx/a/b/microdatos/x.zip" and f["descarga"] == "2026-01-02" and f["corte"] == "ENIGH 2024"
    assert f["tamano"] == "1,234 bytes" and f["sha256"] == "a" * 64 and f["nota"] == "borrado"
    assert contexto._bytes("1,234 bytes") == 1234 and contexto._bytes("47751") == 47751 and contexto._bytes("142 datos") is None


# ---------------------------------------------------------------- /api/carpetas
def test_carpetas_arbol_y_trozos(cliente):
    import json

    d = cliente.get("/api/carpetas").json()
    nombres = {n["nombre"] for n in d["nodos"]}
    assert {"01_metodologia", "02_macro", "03_municipios", "05_modelo", "00_alcance.md"} <= nombres
    n_md = len(list((RAIZ / "carpetas").rglob("*.md")))
    assert d["archivos"] == n_md
    meta = json.loads((RAIZ / "data" / "index" / "meta.json").read_text(encoding="utf-8"))
    assert d["trozos"] == meta["n_trozos"]
    mod = next(n for n in d["nodos"] if n["nombre"] == "05_modelo")
    assert mod["descripcion"] and all(h["trozos"] > 0 and h["titulo"] for h in mod["hijos"])


def test_carpetas_doc_lee_un_archivo(cliente):
    r = cliente.get("/api/carpetas/doc", params={"ruta": "05_modelo/explicacion_modelo.md"})
    assert r.status_code == 200
    d = r.json()
    assert d["titulo"] == "Qué hace el modelo y qué no puede decir" and d["markdown"].startswith("# ") and d["trozos"] > 0
    assert cliente.get("/api/carpetas/doc", params={"ruta": "carpetas/00_alcance.md"}).status_code == 200  # con el prefijo también


@pytest.mark.parametrize("ruta", ["../.env", "../README.md", "/etc/passwd", "carpetas/../.env", "05_modelo/../../README.md", "..\\.env",
                                  "%2e%2e/.env", "....//....//etc/passwd", "", ".", "05_modelo", "/", "05_modelo/../../../../../etc/hosts"])
def test_carpetas_doc_rechaza_rutas_fuera_de_carpetas(cliente, ruta):
    r = cliente.get("/api/carpetas/doc", params={"ruta": ruta})
    assert r.status_code in (400, 404)
    assert "markdown" not in r.json()


def test_carpetas_doc_rechaza_symlink_y_otros_tipos(cliente, tmp_path, monkeypatch):
    raiz = tmp_path / "carpetas"
    raiz.mkdir()
    (tmp_path / "secreto.md").write_text("# secreto", encoding="utf-8")
    (raiz / "ok.md").write_text("# Hola\n\ntexto", encoding="utf-8")
    (raiz / "dato.csv").write_text("a,b", encoding="utf-8")
    (raiz / "enlace.md").symlink_to(tmp_path / "secreto.md")
    monkeypatch.setattr(contexto, "CARPETAS", raiz)
    assert cliente.get("/api/carpetas/doc", params={"ruta": "ok.md"}).json()["markdown"].startswith("# Hola")
    assert cliente.get("/api/carpetas/doc", params={"ruta": "enlace.md"}).status_code == 400  # el enlace sale de carpetas/
    assert cliente.get("/api/carpetas/doc", params={"ruta": "dato.csv"}).status_code == 400  # solo .md
    assert cliente.get("/api/carpetas/doc", params={"ruta": "no_existe.md"}).status_code == 404


def test_carpetas_buscar_sin_ollama_usa_el_modo_lexico(cliente, monkeypatch):
    from app import rag

    def sin_ollama(_):
        raise ConnectionError("Ollama apagado")

    monkeypatch.setattr(rag, "embebe_consulta", sin_ollama)
    r = cliente.get("/api/carpetas/buscar", params={"q": "nivel socioeconomico estimado", "k": 3})
    assert r.status_code == 200
    d = r.json()
    assert d["modo"] == "lexico" and d["aviso"] and 1 <= len(d["resultados"]) <= 3
    assert all(x["archivo"].endswith(".md") and x["texto"] for x in d["resultados"])


def test_carpetas_buscar_valida_la_pregunta(cliente):
    assert cliente.get("/api/carpetas/buscar", params={"q": "  "}).status_code == 400
    assert cliente.get("/api/carpetas/buscar", params={"q": "algo", "k": 99}).status_code == 422


# ---------------------------------------------------------------- /api/descargas
def test_descarga_agebs_sin_geometria(cliente):
    r = cliente.get("/api/descargas/agebs.csv")
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"] and r.headers["content-type"].startswith("text/csv")
    lineas = r.content.decode("utf-8-sig").splitlines()
    cab = lineas[0].split(",")
    assert cab[0] == "cvegeo" and "geometry" not in cab and "nom_colonia" in cab
    assert len(lineas) - 1 >= 5875  # una fila por AGEB (los saltos de linea dentro de un campo, si hubiera, solo suman)


def test_descargas_lista_y_solo_las_permitidas(cliente):
    d = cliente.get("/api/descargas").json()["descargas"]
    assert {x["archivo"] for x in d} == {"agebs.csv", "metricas_giro.csv", "importancia.csv"} and all(x["disponible"] for x in d)
    assert cliente.get("/api/descargas/metricas_giro.csv").text.startswith("giro,")
    assert cliente.get("/api/descargas/.env").status_code == 404
    assert cliente.get("/api/descargas/agebs_features.parquet").status_code == 404
