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
    assert any("Banco de México" in f for f in r["fuentes"])


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


# ---------------------------------------------------------------- colonias (2026-11-23)
def _km(f, ageb, centro):
    from app import lugares
    return float(lugares.distancias_km(centro)[ageb])


@pytest.mark.parametrize("colonia,mun,patron", [
    ("Polanco", "Miguel Hidalgo", "POLANCO"),
    ("la Condesa", "Cuauhtémoc", "CONDESA"),
    ("Santa Fe", "Álvaro Obregón", "SANTA FE"),
])
def test_recomendar_zonas_por_colonia(colonia, mun, patron):
    from app import lugares
    r = h.recomendar_zonas("heladeria", colonia=colonia)
    assert r["encontrado"] and r["filtros"]["colonia"] == colonia and "Filtro por colonia" in r["aviso_colonia"]
    info = r["colonia_consultada"]
    assert info["encontrada"] and info["agebs_en_colonia"] >= 2 and info["radio_km"] == 2.0
    assert any(z["en_colonia_consultada"] for z in r["zonas"])           # al menos una es de la colonia misma
    assert patron in " ".join(info["colonias_coincidentes"]).upper() and mun in info["municipio"]
    for z in r["zonas"]:                                                  # y todas de la colonia o a <= 2 km del centroide
        assert z["en_colonia_consultada"] or z["dist_a_colonia_km"] <= 2.0 + 1e-6
        assert z["en_colonia_consultada"] or _km(None, z["ageb"], info["centroide"]) <= 2.0 + 0.06
    assert r["avisos"][0].startswith("Filtro por colonia")


def test_colonia_inexistente_avisa_y_da_a_cambio():
    r = h.recomendar_zonas("papeleria", colonia="Villa Esperanza Imaginaria")
    assert r["encontrado"] and len(r["zonas"]) == 5                        # a cambio: top sin filtro de colonia
    assert r["aviso_colonia"].startswith("NO ENCONTRADO") and "SIN filtro" in r["aviso_colonia"]
    assert r["filtros"] == {"colonia_no_encontrada": "Villa Esperanza Imaginaria"}
    assert not r["colonia_consultada"]["encontrada"]
    r2 = h.recomendar_zonas("papeleria", municipio="Coyoacán", colonia="Polanco")  # Polanco no esta en Coyoacan
    assert r2["aviso_colonia"].startswith("NO ENCONTRADO") and "Coyoacán" in r2["aviso_colonia"]
    assert all(z["municipio"] == "Coyoacán" for z in r2["zonas"])


def test_colonia_ambigua_lo_dice():
    r = h.recomendar_zonas("farmacia", colonia="Del Carmen")
    assert r["colonia_consultada"]["ambigua"] and "más colonias con ese nombre" in r["aviso_colonia"]
    assert r["colonia_consultada"]["alternativas"]


def test_zona_trae_ingreso_edad_y_resumen():
    r = h.recomendar_zonas("heladeria", municipio="Coyoacán")
    assert r["edad_clave"]["grupo"] == "0-14" and r["edad_clave"]["pct_zmvm"]
    for z in r["zonas"]:
        assert isinstance(z["ingreso_trim_mediano_estimado_mxn"], int) and z["edad_clave_etiqueta"] == "0 a 14 años"
        assert f"{z['edad_clave_pct']} %" in z["resumen_texto"] and f"${z['ingreso_trim_mediano_estimado_mxn']:,}" in z["resumen_texto"]
    assert h.recomendar_zonas("farmacia", municipio="Coyoacán")["edad_clave"]["grupo"] == "60+"
    json.dumps(r)


def test_edad_clave_cubre_todos_los_giros():
    assert set(h.EDAD_CLAVE) <= set(motor.giros())            # no hay claves huerfanas
    assert all(h.edad_clave(g) in h.EDAD_COL for g in motor.giros())


def test_contexto_macro_por_giro():
    m = h.contexto_macro("heladeria")
    assert m["giro"] == "heladeria" and "tasa_objetivo" in m["indicadores"] and "inpc_alimentos_var_anual" in m["indicadores"]
    assert "Banxico" in m["linea"] and "serie SF61745" in m["linea"] and len(m["linea"]) < 500
    assert "inpc_alimentos_var_anual" not in h.contexto_macro("farmacia")["indicadores"]
    assert "FIX" in h.contexto_macro("optica")["linea"]
    assert "remesas" in h.contexto_macro()["indicadores"]     # sin giro, todo como antes


def test_ficha_municipio_corta():
    f = h.ficha_municipio("Coyoacán")
    assert f["encontrado"] and f["municipio"] == "Coyoacán" and 2 <= len(f["ficha"]) <= 6
    assert sum(len(x) for x in f["ficha"]) <= 520
    assert not h.ficha_municipio("Narnia")["encontrado"]


def test_sugerir_giros_barato_es_poca_inversion():
    r = h.sugerir_giros(nse="bajo", inversion="baja")
    assert r["encontrado"] and "NO ENCONTRADO" in r["criterio_inversion"]
    chicos = h.giros_poca_inversion()
    assert all(g["giro"] in chicos and g["personal_ocupado_medio_estab"] for g in r["giros"])
    v = [g["viabilidad_pct"] for g in r["giros"]]
    assert v == sorted(v, reverse=True)                        # el orden de la herramienta es por viabilidad
    assert h.sugerir_giros(colonia="Polanco")["colonia_consultada"]["encontrada"]


def test_lugares_buscar_y_resolver():
    from app import lugares
    r = lugares.buscar("polan")
    assert r and all("POLANCO" in x["colonia"] for x in r) and r[0]["municipio"] == "Miguel Hidalgo"
    assert lugares.buscar("x") == []
    res = lugares.resolver("Interlomas")                      # asentamiento que solo existe en el DENUE
    assert res["ok"] and res["municipio"] == "Huixquilucan" and res["agebs"]
    assert lugares.resolver("polanko")["criterio"] == "aproximado"
    assert not lugares.resolver("Narnia Central")["ok"]
    det = lugares.detectar("heladeria en la colonia Narnia Central")
    assert det and not det[0]["encontrada"] and det[0]["origen"] == "explicita"
