"""Pruebas de app/herramientas.py (sin LLM). uv run pytest tests/test_herramientas.py -q"""
import json

import pytest

from app import herramientas as h
from app import motor


@pytest.mark.parametrize("texto,clave", [
    ("quiero poner una heladería", "heladeria"),
    ("una nevería en Coyoacán", "heladeria"),
    ("Cafetería de especialidad", "cafeteria"),
    ("quiero un café internet", "cafe_internet"),       # el sinonimo mas largo gana sobre 'cafe'
    ("consultorio dental en Tlalpan", "consultorio_dental"),
    ("renta de bicicletas", "renta_bicicletas"),
    ("librerías", "libreria"),
    ("tienda de abarrotes", "abarrotes"),
])
def test_perfil_giro_sinonimos(texto, clave):
    r = h.perfil_giro(texto)
    assert r["encontrado"] and r["giro"] == clave
    assert r["fuentes"]


def test_perfil_giro_no_encontrado_propone_scian():
    r = h.perfil_giro("venta de motocicletas")
    assert not r["encontrado"] and "NO ENCONTRADO" in r["motivo"]
    assert any(p["scian"] == "468311" for p in r["propuestas_scian"])
    assert not h.perfil_giro("algo barato para zona de nivel bajo")["encontrado"]
    assert not h.perfil_giro("un negocio en Coyoacán")["encontrado"]


def test_recomendar_zonas_existen_y_coinciden_con_motor():
    r = h.recomendar_zonas("heladeria")
    assert r["encontrado"] and len(r["zonas"]) == 5
    f = motor.cargar_features()
    s = motor.score_giro("heladeria").set_index("cvegeo")
    for z in r["zonas"]:
        assert z["ageb"] in f.index
        assert f.at[z["ageb"], "nom_colonia"] == z["colonia"]
        assert abs(z["score"] - s.at[z["ageb"], "score"]) <= 0.05
    # una colonia por fila
    assert len({(z["municipio"], z["colonia"]) for z in r["zonas"]}) == 5
    json.dumps(r)  # serializable (sin NaN de numpy)


def test_recomendar_zonas_filtros():
    r = h.recomendar_zonas("cafeteria", municipio="coyoacan", nse="alto", top=3)
    assert r["encontrado"] and len(r["zonas"]) == 3
    assert all(z["municipio"] == "Coyoacán" and z["nse_estimado"] == "alto" for z in r["zonas"])


def test_fuera_de_zmvm_y_giro_inexistente():
    r = h.recomendar_zonas("heladeria", municipio="Monterrey")
    assert not r["encontrado"] and r.get("fuera_de_zmvm")
    assert not h.recomendar_zonas("venta de cohetes")["encontrado"]
    assert not h.recomendar_zonas("heladeria", municipio="Narnia")["encontrado"]


def test_ficha_zona_ageb_y_colonia():
    cve = h.recomendar_zonas("heladeria")["zonas"][0]["ageb"]
    r = h.ficha_zona(cve, giro="heladeria")
    assert r["encontrado"] and r["ageb"] == cve and r["giro"]["rank_zmvm"] == 1
    c = h.ficha_zona("del valle centro", municipio="Benito Juárez")
    assert c["encontrado"] and c["colonias"][0]["municipio"] == "Benito Juárez"
    assert not h.ficha_zona("9999999999999")["encontrado"]


def test_contexto_macro():
    r = h.contexto_macro()
    ind = r["indicadores"]
    assert ind["tasa_objetivo"]["valor"] > 0 and ind["tasa_objetivo"]["id_serie"]
    assert ind["inpc_alimentos_var_anual"]["valor"] == "NO ENCONTRADO"
    assert any("Banco de Mexico" in f for f in r["fuentes"])


def test_sugerir_giros():
    r = h.sugerir_giros(nse="bajo", ticket_max=100)
    assert r["encontrado"] and all(g["ticket_promedio_mxn"] <= 100 for g in r["giros"])
    assert h.sugerir_giros(municipio="Coyoacán")["encontrado"]


def test_sugerir_giros_ordena_por_probabilidad_absoluta():
    # el score es relativo dentro de cada giro: sugerir_giros no debe ordenar por el, sino por viabilidad absoluta
    r = h.sugerir_giros(municipio="Coyoacán")
    v = [g["viabilidad_pct"] for g in r["giros"]]
    assert v == sorted(v, reverse=True) and len(r["giros"]) >= 3
    assert "relativo" in r["como_leer"]
    assert all("aviso" in g for g in r["giros"] if g["prob_apertura_pct"] < 10)


def test_score_sin_sesgo_por_tamano():
    # el score no debe crecer con el tamano de la AGEB (antes Spearman 0.84 con la poblacion en heladeria)
    from scipy.stats import spearmanr
    from app import motor
    f = motor.cargar_features()[["pob_total", "area_km2"]]
    d = motor.score_giro("heladeria").join(f, on="cvegeo")
    assert spearmanr(d["score"], d["pob_total"], nan_policy="omit").statistic < 0.6
    assert d.head(50)["area_km2"].median() < 2 * f["area_km2"].median()


def test_aviso_prob_baja_en_libreria():
    r = h.recomendar_zonas("libreria")
    if max(z["prob_apertura_pct"] for z in r["zonas"]) < 10:
        assert "aviso_prob_baja" in r and "DENTRO de este giro" in r["como_leer_score"]


def test_buscar_carpetas():
    r = h.buscar_carpetas("como se estima el nivel socioeconomico", k=3)
    assert r["encontrado"] and len(r["trozos"]) == 3
    assert all(t["archivo"].startswith("carpetas/") for t in r["trozos"])


def test_ejecutar_errores_controlados():
    assert "error" in h.ejecutar("no_existe", {})
    assert "error" in h.ejecutar("recomendar_zonas", {"zzz": 1})
