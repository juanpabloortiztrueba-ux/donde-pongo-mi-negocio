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


# =============================================================== pulido final del nucleo (N8 a N12)
def test_n8_ficha_del_municipio_trae_el_ingreso_estimado_con_su_fuente():
    f = motor.cargar_features()
    d = f[(f["cve_ent"].astype(str) + f["cve_mun"].astype(str)) == "09003"].sort_values("ing_trim_mediano_est")
    acum = d["hogares"].cumsum()
    esperado = float(d["ing_trim_mediano_est"][acum >= d["hogares"].sum() / 2].iloc[0])       # mediana ponderada por hogares
    r = h.ficha_municipio("Coyoacán")
    assert r["ingreso_trim_mediano_est_hogar_mxn"] == round(esperado, -2) and 40_000 < esperado < 200_000
    assert r["decil_tipico"] == 8
    assert r["ingreso_linea"] == (f"Ingreso trimestral mediano estimado por hogar en Coyoacán: ${round(esperado, -2):,.0f} "
                                  "(decil típico 8; estimación del proyecto con ENIGH 2024 y Censo 2020).")
    assert "ponderada por hogares" in r["metodo_ingreso"] and any("ENIGH 2024" in x for x in r["fuentes"])
    assert h.ficha_municipio("Iztapalapa")["ingreso_trim_mediano_est_hogar_mxn"] < r["ingreso_trim_mediano_est_hogar_mxn"]


def test_n8_la_pregunta_de_ingreso_se_reconoce():
    for q in ("¿cuánto ganan ahí?", "¿Qué tan ricos son en Polanco?", "¿cuál es el nivel socioeconómico?", "Quiero saber el ingreso de la gente"):
        assert h.pide_ingreso(q), q
    for q in ("quiero poner una heladería", "¿qué porcentaje es menor de 14 años?", "¿dónde abro una cafetería?",
              "¿cuánto pagar de sueldo a un empleado?", "¿qué salario le doy a mi cajero?"):
        assert not h.pide_ingreso(q), q
    assert h.pide_ingreso("¿qué sueldo tiene la gente de Coyoacán?")
    # «ingreso» del negocio no es el ingreso de la gente
    for q in ("¿Cuánto ingreso necesito para abrir?", "¿qué ingresos tendría mi negocio?"):
        assert not h.pide_ingreso(q), q
    for q in ("¿qué ingresos tiene la gente donde pondría mi negocio?", "¿cuál es el ingreso de los hogares en Coyoacán?",
              "¿qué nivel de ingresos hay para mi negocio?"):
        assert h.pide_ingreso(q), q


def test_n9_giros_de_rubro_amplio_o_sustituto_lo_dicen():
    g = motor.giros()
    marcados = {k for k, v in g.items() if v.get("rubro_enigh_tipo")}
    assert {"cafeteria", "abarrotes", "fonda", "bar", "guarderia", "renta_bicicletas", "heladeria"} <= marcados
    assert all(g[k].get("rubro_enigh_etiqueta") for k in marcados) and not (marcados & {"farmacia", "papeleria", "optica"})
    a = h.aviso_rubro_amplio("cafeteria")
    assert a == ("el gasto potencial usa el rubro ENIGH alimentos y bebidas consumidos fuera del hogar completo; "
                 "sirve para ordenar zonas dentro del giro, no para comparar entre giros")
    assert "como sustituto del giro" in h.aviso_rubro_amplio("guarderia") and h.aviso_rubro_amplio("farmacia") is None
    r = h.recomendar_zonas("cafeteria")
    assert r["aviso_rubro_amplio"] == a and a in r["avisos"]
    assert "aviso_rubro_amplio" not in h.recomendar_zonas("farmacia") and h.perfil_giro("quiero una cafetería")["aviso_rubro_amplio"] == a


def test_n10_ageb_casi_vacia_lleva_aviso():
    assert h._aviso_ageb_vacia(20, 4) == "AGEB con 20 habitantes: el gasto viene del radio de influencia, no de quienes viven en la AGEB"
    assert h._aviso_ageb_vacia(199, 100).startswith("AGEB con 199 habitantes")
    assert h._aviso_ageb_vacia(900, 45) == "AGEB con 45 hogares: el gasto viene del radio de influencia, no de quienes viven en la AGEB"
    assert h._aviso_ageb_vacia(200, 50) is None and h._aviso_ageb_vacia(349, 183) is None and h._aviso_ageb_vacia(None, None) is None
    # ferreteria: el 4 del top es una AGEB con 20 habitantes y 4 hogares (el orden del score no se toca)
    zs = h.recomendar_zonas("ferreteria")["zonas"]
    vacia = [z for z in zs if z["poblacion_ageb_2020"] == 20]
    assert len(vacia) == 1 and vacia[0]["hogares_ageb_2020"] == 4
    assert vacia[0]["aviso_ageb_poco_poblada"].startswith("AGEB con 20 habitantes")
    assert all("aviso_ageb_poco_poblada" not in z for z in zs if z["poblacion_ageb_2020"] >= 200)


def test_n11_formato_es_mx_y_fechas_de_series_mensuales():
    m = h.contexto_macro()
    assert h._txt_indicador("remesas", m["indicadores"]["remesas"]) == f"remesas {m['indicadores']['remesas']['valor']:,} millones de dólares al mes (2026-09, serie SE27803)"
    assert "5,362" in h._txt_indicador("remesas", m["indicadores"]["remesas"])
    assert m["indicadores"]["remesas"]["fecha"] == "2026-09" and m["indicadores"]["inpc_general_var_anual"]["fecha"] == "2026-10"
    assert h._fmt_valor(5362) == "5,362" and h._fmt_valor(6.25) == "6.25" and h._fmt_valor(1234567) == "1,234,567"
    assert h._fecha_txt("2026-09-01", True) == "2026-09" and h._fecha_txt("2026-11-23", False) == "2026-11-23"
    texto = " ".join(h._txt_indicador(k, v) for k, v in m["indicadores"].items())
    assert "-01," not in texto and "2026-09-01" not in texto


def test_n11_usa_el_dato_mas_nuevo_de_macro_series(tmp_path, monkeypatch):
    import pandas as pd
    macro = {"_meta": {"generado": "2026-11-23"},
             "tipo_cambio_fix": {"valor": 19.0228, "unidad": "MXN por USD", "fecha": "2026-11-20", "id_serie": "SF43718", "fuente": "Banco de Mexico"},
             "tasa_objetivo": {"valor": 6.25, "unidad": "% anual", "fecha": "2026-11-23", "id_serie": "SF61745", "fuente": "Banco de Mexico"},
             "remesas": {"valor": 5362.19, "unidad": "millones de USD (mensual)", "fecha": "2026-09-01", "id_serie": "SE27803",
                         "fuente": "Banco de Mexico", "variacion_anual_pct": 1.55}}
    (tmp_path / "macro.json").write_text(json.dumps(macro), encoding="utf-8")
    ser = pd.DataFrame([
        {"serie": "tipo_cambio_fix", "fecha": pd.Timestamp("2026-11-20"), "valor": 19.0228, "unidad": "MXN por USD", "fuente": "x", "id_serie": "SF43718"},
        {"serie": "tipo_cambio_fix", "fecha": pd.Timestamp("2026-11-23"), "valor": 19.1648, "unidad": "MXN por USD", "fuente": "x", "id_serie": "SF43718"},
        {"serie": "tasa_objetivo", "fecha": pd.Timestamp("2026-11-23"), "valor": 6.25, "unidad": "% anual", "fuente": "x", "id_serie": "SF61745"},
        {"serie": "remesas", "fecha": pd.Timestamp("2026-10-01"), "valor": 5100.0, "unidad": "millones de USD (mensual)", "fuente": "x", "id_serie": "OTRA"},
    ])
    ser.to_parquet(tmp_path / "macro_series.parquet")
    monkeypatch.setattr(h, "PROC", tmp_path)
    ind = h.contexto_macro()["indicadores"]
    assert ind["tipo_cambio_fix"]["valor"] == 19.16 and ind["tipo_cambio_fix"]["fecha"] == "2026-11-23"     # el mas nuevo de la misma serie
    assert ind["tasa_objetivo"]["valor"] == 6.25 and ind["tasa_objetivo"]["fecha"] == "2026-11-23"
    assert ind["remesas"]["valor"] == 5362 and ind["remesas"]["fecha"] == "2026-09"                         # otra serie (otro id): se queda macro.json
    assert "19.16 pesos por dólar (2026-11-23" in h._txt_indicador("tipo_cambio_fix", ind["tipo_cambio_fix"])
    (tmp_path / "macro_series.parquet").unlink()                                                            # sin parquet: como antes
    assert h.contexto_macro()["indicadores"]["tipo_cambio_fix"]["valor"] == 19.02


def test_n12_todos_los_giros_traen_insumos_y_como_influye_los_nombra():
    g = motor.giros()
    assert len(g) == 40 and all(isinstance(v.get("insumos"), list) and 2 <= len(v["insumos"]) <= 4 for v in g.values())
    assert g["taqueria"]["insumos"] == ["carne", "tortilla", "gas"] and g["cafeteria"]["insumos"][:2] == ["café", "leche"]
    m = h.contexto_macro("taqueria")
    ins = m["como_influye"]["insumos_del_giro"]
    assert "carne, tortilla y gas" in ins and "taquería" in ins
    t, i = m["indicadores"]["tasa_objetivo"]["valor"], m["indicadores"]["inpc_general_var_anual"]["valor"]
    assert m["tasa_real_aproximada"]["valor"] == round(t - i, 2) and m["tasa_real_aproximada"]["unidad"] == "puntos porcentuales"
    tr = m["como_influye"]["tasa_real"]
    assert f"{t:g} %" in tr and f"{i:g} %" in tr and f"{round(t - i, 2):g} puntos porcentuales" in tr and "tasa objetivo menos inflación anual" in tr
    assert "por encima de la inflación" in tr
    # un giro de comida cita la aproximacion agropecuaria de contexto_macro; uno que no es de comida no
    assert "agropecuarios del INPC" in ins and "agropecuarios" not in h.contexto_macro("optica")["como_influye"]["insumos_del_giro"]
    assert "armazones" in h.contexto_macro("optica")["como_influye"]["insumos_del_giro"]
    assert "tasa_real" in h.contexto_macro()["como_influye"] and "insumos_del_giro" not in h.contexto_macro()["como_influye"]


def test_n12_mas_preguntas_piden_el_mecanismo_sin_cifras_inventadas():
    for q in ("¿Cómo está la economía para abrir un negocio?", "¿Es buen momento para abrir una taquería?", "¿Me afecta la inflación?",
              "¿afectan las tasas?", "¿Cómo influye el dólar?"):
        assert h.pide_como_influye(q), q
    for q in ("quiero poner una heladería", "¿cómo está la inflación?", "¿dónde abro una cafetería?",
              "¿Me afecta la competencia en Coyoacán?", "¿afecta el tráfico a mi local?",
              "¿Cómo me afecta la competencia en Coyoacán?", "¿Qué impacto de la competencia hay?"):
        assert not h.pide_como_influye(q), q
    # las cifras de como_influye salen de los indicadores (sirven para el chequeo de cifras)
    from app import lectura
    m = h.contexto_macro("taqueria")
    nums = lectura.numeros_de(m)
    assert all(lectura.coincide(c, nums) for c in lectura.cifras_citadas(m["como_influye"]["tasa_real"], ""))
