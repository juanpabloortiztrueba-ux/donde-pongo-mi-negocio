"""Pruebas de las carpetas y del buscador (app/rag.py). Las vectoriales necesitan Ollama; si no responde, se saltan."""
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from app import rag  # noqa: E402


def test_hay_76_fichas():
    fichas = [f for f in (RAIZ / "carpetas" / "03_municipios").glob("[0-9]*.md") if not f.name.startswith("00_")]
    claves = set(pd.read_csv(RAIZ / "data" / "processed" / "zmvm_municipios.csv", dtype=str)["cvegeo_mun"])
    assert {f.name[:5] for f in fichas} == claves and len(fichas) == 76


def test_indice_completo():
    e = rag.estado()
    assert e["dim"] == 768 and e["trozos"] > 500 and e["archivos"] >= 80


def test_municipios_en_pregunta():
    assert rag.municipios_en("negocios en Coyoacán") == ["Coyoacán"]
    assert "Naucalpan de Juárez" in rag.municipios_en("algo en naucalpan")
    assert rag.municipios_en("una heladería en Monterrey") == []
    assert rag.ciudades_fuera("una heladería en Monterrey") == ["monterrey"]


def test_sin_tokens_en_carpetas():
    env = (RAIZ / ".env").read_text() if (RAIZ / ".env").exists() else ""
    valores = [v.strip().strip("'\"") for k, v in (l.split("=", 1) for l in env.splitlines() if "=" in l) if len(v.strip()) > 12]
    for f in (RAIZ / "carpetas").rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        assert not any(v in t for v in valores), f


def test_cada_fuente_de_numero_tiene_marca():
    # las fichas deben decir de donde salen y marcar estimaciones
    t = (RAIZ / "carpetas" / "03_municipios" / "09003_coyoacan.md").read_text(encoding="utf-8")
    assert "Fuente" in t and "estimación" in t.lower() and "DENUE" in t


def _ollama():
    try:
        rag.embebe_consulta("prueba")
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _ollama(), reason="Ollama no responde")
def test_busqueda_vectorial():
    r = rag.buscar("como se estima el nivel socioeconomico", k=3)
    assert r and r[0]["modo"] == "vectorial" and "nse_estimado" in r[0]["archivo"]
    r = rag.buscar("colonias con mas negocios en Coyoacan", k=3)
    assert all(x["archivo"].endswith("09003_coyoacan.md") for x in r[:2])
    r = rag.buscar("heladeria en Monterrey", k=1)
    assert r[0]["archivo"] == "00_alcance.md"


def test_respaldo_lexico(monkeypatch):
    monkeypatch.setattr(rag, "embebe_consulta", lambda q: (_ for _ in ()).throw(RuntimeError("sin ollama")))
    r = rag.buscar("marginacion CONAPO indice", k=2)
    assert r and r[0]["modo"] == "lexico"


def test_valle_de_chalco_no_se_confunde_con_chalco():
    from app import rag
    assert rag.municipios_en("negocio en Valle de Chalco") == ["Valle de Chalco Solidaridad"]
    assert rag.municipios_en("heladeria en Chalco") == ["Chalco"]
    assert rag.municipios_en("cuautitlan izcalli") == ["Cuautitlán Izcalli"]
