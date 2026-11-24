"""Revision de la Lectura (app/lectura.py) y arreglos del agente tras la evaluacion final. Sin LLM ni red."""
import pandas as pd

from app import agente, herramientas as H, lectura as L, motor


def _usadas(giro="heladeria", **kw):
    r = H.recomendar_zonas(giro, **kw)
    return r, [{"nombre": "recomendar_zonas", "args": {}, "resultado": r}]


def _con(frase, usadas, pregunta=""):
    return L.problemas(frase, L.Contexto(usadas, pregunta))


# --- (a) y (superlativos): lideran / mejor / score / cifra sin magnitud
def test_lideran_y_mejores_se_comparan_con_el_score():
    r, u = _usadas()
    z = r["zonas"]                                  # el top viene ordenado por score
    assert _con(f"{z[1]['colonia']} y {z[3]['colonia']} lideran la oportunidad para una heladería.", u)["superlativos"]
    assert not _con(f"{z[0]['colonia']} y {z[1]['colonia']} lideran la oportunidad para una heladería.", u)["superlativos"]
    assert _con(f"La mejor opción es {z[4]['colonia']}.", u)["superlativos"]
    assert not _con(f"La mejor opción es {z[0]['colonia']}.", u)["superlativos"]
    assert _con(f"Las mejores colonias son {z[3]['colonia']} y {z[1]['colonia']}.", u)["superlativos"]


def test_superlativo_sin_magnitud_se_deduce_de_la_cifra():
    r, u = _usadas("guarderia", municipio="Tlalnepantla de Baz")
    z = sorted(r["zonas"], key=lambda x: -x["edad_clave_pct"])
    ultimo, primero = z[-1], z[0]
    assert ultimo["edad_clave_pct"] < primero["edad_clave_pct"]
    assert _con(f"{ultimo['colonia']} lidera con un {ultimo['edad_clave_pct']} % de este grupo.", u)["superlativos"]
    assert not _con(f"{primero['colonia']} lidera con un {primero['edad_clave_pct']} % de este grupo.", u)["superlativos"]


def test_menores_de_14_no_es_un_superlativo_y_si_es_edad():
    r, u = _usadas("heladeria")
    z = sorted(r["zonas"], key=lambda x: -x["edad_clave_pct"])
    assert not L.SUPERLATIVOS[0][0].search("la poblacion menores de 14 anos") and not L.SUPERLATIVOS[1][0].search("adultos mayores")
    f = f"{z[-1]['colonia']} destaca por tener un {z[-1]['edad_clave_pct']} % de menores de 14 años."
    assert _con(f, u)["superlativos"]


# --- (b) cifras: sin origen, de otro tipo, de otra zona
def test_cifra_inventada_o_de_otro_tipo_se_quita():
    r, u = _usadas()
    z = r["zonas"][0]
    nombre = z["colonia"]
    assert _con(f"{nombre} tiene una probabilidad de apertura de 57.3 %.", u)["cifras"]                 # sin origen
    assert not _con(f"{nombre} tiene una probabilidad de apertura del {z['prob_apertura_pct']} %.", u)["cifras"]
    ing = z["ingreso_trim_mediano_estimado_mxn"]
    assert not _con(f"{nombre} tiene un ingreso trimestral estimado de ${ing:,}.", u)["cifras"]
    # un % no puede ser el ingreso en pesos: el numero existe pero no es de este tipo
    assert _con(f"{nombre} tiene un {z['gasto_potencial_trim_mxn'] // 1000} % de ingreso.", u)["cifras"]
    otra = r["zonas"][1]
    assert _con(f"{nombre} tiene una probabilidad de apertura del {otra['prob_apertura_pct']} %.", u)["cifras"]   # de otra zona


def test_cifras_de_macro_ficha_y_perfil_valen_en_cualquier_frase():
    r, u = _usadas("taqueria")
    macro = H.contexto_macro("taqueria")
    perfil = H.perfil_giro("quiero una taqueria")
    u += [{"nombre": "contexto_macro", "args": {}, "resultado": macro}, {"nombre": "perfil_giro", "args": {}, "resultado": perfil}]
    infl = macro["indicadores"]["inpc_general_var_anual"]["valor"]
    assert not _con(f"La inflación general es de {infl} % anual y el ticket de una taquería es de {perfil['ticket_promedio_mxn']} pesos.", u)["cifras"]
    assert _con(f"La inflación general es de {infl + 1.37} % anual.", u)["cifras"]


# --- (c) sugerir_giros: el que lidera es el 1, su cifra es la suya y no se mezclan zonas de otro giro
def _sg():
    sg = H.sugerir_giros(municipio="Coyoacán")
    r = H.recomendar_zonas(sg["giros"][0]["giro"], municipio="Coyoacán")
    return sg, r, [{"nombre": "sugerir_giros", "args": {}, "resultado": sg}, {"nombre": "recomendar_zonas", "args": {}, "resultado": r}]


def test_giro_que_lidera_es_el_1_y_con_su_viabilidad():
    sg, r, u = _sg()
    g1, g3 = sg["giros"][0], sg["giros"][2]
    n1, n3 = H.nombre_giro(g1["giro"]), H.nombre_giro(g3["giro"])
    assert not _con(f"En Coyoacán, {n1} lidera la viabilidad con un {g1['viabilidad_pct']} %.", u)["superlativos"]
    assert _con(f"En Coyoacán, {n3} lidera la viabilidad.", u)["superlativos"]
    mal = _con(f"{n3} lidera con mayor viabilidad ({g1['viabilidad_pct']} %).", u)
    assert mal["cifras"] and mal["superlativos"]


def test_a_un_giro_sin_recomendar_zonas_no_se_le_atribuyen_zonas_ni_gasto():
    sg, r, u = _sg()
    ajeno = sg["giros"][2]["giro"]
    z = r["zonas"][0]["colonia"]
    assert _con(f"{H.nombre_giro(ajeno)} también destaca por su gasto potencial en la misma zona.", u)["cifras"]
    assert _con(f"{H.nombre_giro(ajeno)} sería buena opción en {z}.", u)["cifras"]
    assert not _con(f"{H.nombre_giro(sg['giros'][0]['giro'])} sería buena opción en {z}.", u)["cifras"]


def test_depurar_quita_giros_fuera_de_orden_y_arma_una_frase_con_el_giro_1():
    sg, r, u = _sg()
    g = sg["giros"]
    fuera = f"{H.nombre_giro(g[2]['giro'])} y {H.nombre_giro(g[0]['giro'])} son giros posibles."
    t, quitadas = L.depurar("**Lectura:** " + fuera, u)
    assert quitadas and "Por viabilidad" in t or "Entre las zonas del top" in t
    assert L.orden_de_giros(f"{H.nombre_giro(g[0]['giro'])} y luego {H.nombre_giro(g[2]['giro'])}.", [x["giro"] for x in g])
    assert not L.orden_de_giros(fuera, [x["giro"] for x in g])


# --- el codigo ya no empata ni dice «la mayor (0 %)»
def test_desde_destacados_omite_empates_y_probabilidades_bajas():
    r = H.recomendar_zonas("renta_bicicletas")
    assert r["aviso_prob_baja"] and "0 a 0" not in r["aviso_prob_baja"]
    t = L.desde_destacados(r)
    assert "probabilidad de apertura" not in t and "menor competencia" not in t    # todo el top empata en 0 %, 0.0 competidores
    assert L._nombre_bonito("DEL VALLE NORTE") == "Del Valle Norte" and L._nombre_bonito("POLANCO IV SECCION").startswith("Polanco IV")


# --- herramientas
def test_edad_reservada_por_el_censo_no_imprime_none():
    d = H._score("taqueria")
    fila = d[d["cvegeo"] == "0901600010764"].iloc[0]                  # Polanco III: pob_25_59 = NaN
    z = H._zona(fila, "taqueria")
    assert z["edad_clave_pct"] == H.NO and "None" not in z["resumen_texto"]
    assert "NO ENCONTRADO (el Censo reserva el dato)" in z["resumen_texto"]
    ok = H._zona(d[d["cvegeo"] != "0901600010764"].iloc[0], "taqueria")
    assert isinstance(ok["edad_clave_pct"], float)


def test_lavanderia_no_dimensionable_y_proxy_de_bicicletas():
    z = H.recomendar_zonas("lavanderia")["zonas"][0]
    assert z["gasto_potencial_trim_mxn"].startswith("no dimensionable") and "no dimensionable" in z["resumen_texto"]
    b = H.recomendar_zonas("renta_bicicletas")
    assert all("esparcimiento" in x["gasto_potencial_nota"] and "esparcimiento" in x["resumen_texto"] for x in b["zonas"])
    assert "apareció en 1 de" in b["aviso_prob_baja"] and "AGEB" in b["aviso_prob_baja"]


def test_contexto_macro_trae_como_influye_y_la_pregunta_lo_pide():
    m = H.contexto_macro("taqueria")
    assert set(m["como_influye"]) == {k for k in H.indicadores_del_giro("taqueria") if k in m["indicadores"]
                                       and m["indicadores"][k].get("valor") != H.NO}
    assert all(not any(ch.isdigit() for ch in t) for t in m["como_influye"].values())    # frases fijas, sin cifras
    assert H.pide_como_influye("¿cómo influyen la inflación y la tasa de Banxico?") and H.pide_como_influye("¿Cómo afecta la tasa?")
    assert not H.pide_como_influye("¿cómo está la economía?")
    u = [{"nombre": "contexto_macro", "args": {}, "resultado": m}]
    con = "\n".join(agente.bloques(u, None, "¿cómo influye la inflación?"))
    sin = "\n".join(agente.bloques(u, None, "¿cómo está la inflación?"))
    assert "Cómo influye en el negocio" in con and "margen" in con and "Cómo influye" not in sin
    assert "como_influye" in agente.para_llm("contexto_macro", m, True) and "como_influye" not in agente.para_llm("contexto_macro", m)


def test_riesgos_ponen_primero_giro_raro_y_rubro_sustituto():
    r = H.recomendar_zonas("renta_bicicletas")
    rs = agente.riesgos([{"nombre": "recomendar_zonas", "args": {}, "resultado": r}])
    assert any(x.startswith("Giro raro") for x in rs[:3]) and any("esparcimiento como proxy" in x for x in rs[:3])


def test_encabezado_con_el_sinonimo_que_uso_la_persona():
    usadas = [{"nombre": "perfil_giro", "args": {}, "resultado": H.perfil_giro("Quiero abrir una nevería en Polanco")},
              {"nombre": "recomendar_zonas", "args": {}, "resultado": H.recomendar_zonas("heladeria")}]
    assert agente.giro_visible(usadas, "heladeria") == "heladería (nevería)"
    usadas[0]["resultado"] = H.perfil_giro("una lavandería de autoservicio")
    assert agente.giro_visible(usadas, "lavanderia") == "lavandería"
    usadas[0]["resultado"] = H.perfil_giro("quiero una heladeria")
    assert agente.giro_visible(usadas, "heladeria") == "heladería"


def test_macro_sin_zonas_quita_la_interpretacion_sin_respaldo():
    m = H.contexto_macro()
    u = [{"nombre": "contexto_macro", "args": {}, "resultado": m}]
    infl = m["indicadores"]["inpc_general_var_anual"]["valor"]
    t, q = L.depurar(f"**Lectura:** La inflación general es de {infl} % anual, lo que refleja una moderada expectativa de gasto.", u)
    assert q and "refleja" not in t and f"{infl} %" in t
    t2, q2 = L.depurar(f"**Lectura:** La inflación general es de {infl + 1.37} % anual.", u)
    assert q2 and t2 is None
    ok = f"**Lectura:** La inflación general es de {infl} % anual."
    assert L.depurar(ok, u) == (ok, [])
