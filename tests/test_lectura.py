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
    por_indicador = {k for k in H.indicadores_del_giro("taqueria") if k in m["indicadores"] and m["indicadores"][k].get("valor") != H.NO}
    assert set(m["como_influye"]) == por_indicador | {"tasa_real", "insumos_del_giro"}
    fijas = [t for k, t in m["como_influye"].items() if k in por_indicador]
    assert all(not any(ch.isdigit() for ch in t) for t in fijas)    # el mecanismo por indicador son frases fijas, sin cifras
    assert H.pide_como_influye("¿cómo influyen la inflación y la tasa de Banxico?") and H.pide_como_influye("¿Cómo afecta la tasa?")
    assert not H.pide_como_influye("¿cómo está la inflación?")
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


# =============================================================== pulido final del nucleo (N1 a N5, N10)
def _usadas_de(r):
    return [{"nombre": "recomendar_zonas", "args": {}, "resultado": r}]


def _zona_falsa(colonia, ageb, **kw):
    z = {"colonia": colonia, "ageb": ageb, "municipio": "Prueba", "prob_apertura_pct": 30, "gasto_potencial_trim_mxn": 50000,
         "competidores_ponderados": 2.0, "score": 80.0, "edad_clave_pct": 15.0, "ingreso_trim_mediano_estimado_mxn": 60000}
    z.update(kw)
    return z


def _top_falso(zonas):
    return {"encontrado": True, "giro": "heladeria", "zonas": zonas, "filtros": None}


def test_n1_la_edad_es_una_magnitud_aunque_la_zona_vaya_antes_del_superlativo():
    # pregunta 27: Pedregal de Santo Domingo (20.2 %) no es el mayor porcentaje de menores de 14 anos; Carmen Serdan (21.6 %) si
    r, u = _usadas("heladeria", municipio="Coyoacán")
    pedregal = next(z for z in r["zonas"] if z["colonia"] == "PEDREGAL DE SANTO DOMINGO")
    carmen = next(z for z in r["zonas"] if z["colonia"] == "CARMEN SERDÁN")
    assert pedregal["edad_clave_pct"] == 20.2 and carmen["edad_clave_pct"] == 21.6
    falsa = ("La colonia PEDREGAL DE SANTO DOMINGO destaca por tener el mayor porcentaje de menores de 14 años (20.2 %) "
             "y un gasto potencial por trimestre de $98,000.")
    assert "mayor edad clave" in " ".join(_con(falsa, u)["superlativos"])
    for variante in ("PEDREGAL DE SANTO DOMINGO tiene el mayor porcentaje de niños (20.2 %).",
                     "PEDREGAL DE SANTO DOMINGO concentra el mayor porcentaje de población de 0 a 14 años.",
                     "En PEDREGAL DE SANTO DOMINGO el porcentaje de menores de 14 años (20.2 %) es el más alto.",
                     "PEDREGAL DE SANTO DOMINGO tiene el mayor porcentaje de personas de 0-14 años."):
        assert _con(variante, u)["superlativos"], variante
    assert not _con("CARMEN SERDÁN tiene el mayor porcentaje de menores de 14 años (21.6 %).", u)["superlativos"]
    # el check del evaluador (lectura_superlativos) usa la misma regla; depurar quita la frase falsa y deja la lectura del codigo
    t, quitadas = L.depurar("**Lectura:** " + falsa, u, "¿qué porcentaje es menor de 14 años?")
    assert quitadas and "destaca por tener el mayor porcentaje" not in (t or "")
    assert t and "tiene el mayor gasto potencial ($98,000 por trimestre)" in t


def test_n1_un_grupo_de_edad_que_el_top_no_compara_no_se_puede_juzgar():
    r, u = _usadas("heladeria", municipio="Coyoacán")
    z = r["zonas"][0]["colonia"]
    mal = _con(f"{z} tiene el mayor porcentaje de adultos mayores.", u)["superlativos"]
    assert mal and "0 a 14 años" in mal[0]
    assert L.grupo_de_edad(L.ligera("60 años o más")) == "60+" and L.grupo_de_edad(L.ligera("jóvenes de 15 a 24 años")) == "15-24"
    assert L.grupo_de_edad(L.ligera("adultos de 25 a 59 años")) == "25-59" and L.grupo_de_edad(L.ligera("menores de 14")) == "0-14"


def test_n2_mayor_potencial_se_compara_con_el_score():
    # pregunta 3: «las zonas con mayor potencial son Del Valle Centro y Ampliacion Napoles» y Napoles es la 4.a
    r, u = _usadas("gimnasio")
    z = r["zonas"]
    assert z[3]["colonia"] == "AMPLIACIÓN NÁPOLES"
    assert _con(f"Las zonas con mayor potencial para un gimnasio son {z[0]['colonia']} y {z[3]['colonia']}.", u)["superlativos"]
    assert _con(f"{z[3]['colonia']} tiene la mayor oportunidad para un gimnasio.", u)["superlativos"]
    assert not _con(f"Las zonas con mayor potencial para un gimnasio son {z[0]['colonia']} y {z[1]['colonia']}.", u)["superlativos"]
    assert _con(f"La zona con más alto potencial es {z[4]['colonia']}.", u)["superlativos"]
    # depurar la quita y arma la lectura con los destacados
    t, quitadas = L.depurar(f"**Lectura:** Las zonas con mayor potencial son {z[0]['colonia']} y {z[3]['colonia']}.", u)
    assert quitadas and "mayor potencial" not in t


def test_n3_empates_se_nombran_todos():
    r = _top_falso([_zona_falsa("POLANCO IV SECCION", "A1", competidores_ponderados=0.0, prob_apertura_pct=23, gasto_potencial_trim_mxn=109000),
                    _zona_falsa("5 DE MAYO", "A2", competidores_ponderados=1.4, prob_apertura_pct=16, gasto_potencial_trim_mxn=95000),
                    _zona_falsa("GRANADA", "A3", competidores_ponderados=0.0, prob_apertura_pct=21, gasto_potencial_trim_mxn=140000),
                    _zona_falsa("POLANCO V SECCION", "A4", competidores_ponderados=1.1, prob_apertura_pct=50, gasto_potencial_trim_mxn=145000),
                    _zona_falsa("POLANCO I SECCION", "A5", competidores_ponderados=0.0, prob_apertura_pct=22, gasto_potencial_trim_mxn=115000)])
    t = L.desde_destacados(r)
    assert "Polanco IV Sección, Granada y Polanco I Sección empatan con la menor competencia (0.0 competidores ponderados)" in t
    assert "Polanco V Sección tiene la mayor probabilidad de apertura (50 %)" in t and "el mayor gasto potencial ($145,000 por trimestre)" in t
    # dos zonas que empatan
    r["zonas"][2]["competidores_ponderados"] = 0.5
    assert "Polanco IV Sección y Polanco I Sección empatan con la menor competencia (0.0 competidores ponderados)" in L.desde_destacados(r)
    # cuatro de cinco empatan: no distingue a nadie y no se dice; todo el top empata: tampoco
    for z in r["zonas"][:4]:
        z["competidores_ponderados"] = 0.0
    assert "competencia" not in L.desde_destacados(r)
    for z in r["zonas"]:
        z["competidores_ponderados"] = 0.0
    assert "competencia" not in L.desde_destacados(r)
    # y lo que dice el codigo lo valida la propia regla de superlativos
    r2 = H.recomendar_zonas("heladeria", colonia="Polanco")
    texto = L.desde_destacados(r2)
    assert "empatan con la menor competencia (0.0 competidores ponderados)" in texto
    u2 = _usadas_de(r2)
    assert all(not any(_con(f, u2).values()) for f in L.frases(texto))
    assert r2["destacados"]["menor_competencia"]["empatan"] == ["POLANCO IV SECCIÓN", "GRANADA", "POLANCO I SECCIÓN"]


def test_n4_depurar_no_repite_zona_y_magnitud_de_la_base():
    r = _top_falso([_zona_falsa("EX EJIDO DE SAN FRANCISCO", "B1", competidores_ponderados=2.9, prob_apertura_pct=40, gasto_potencial_trim_mxn=90000, score=95.0),
                    _zona_falsa("CENTRO", "B2", competidores_ponderados=5.0, prob_apertura_pct=20, gasto_potencial_trim_mxn=80000, score=90.0),
                    _zona_falsa("ROMA NORTE", "B3", competidores_ponderados=6.0, prob_apertura_pct=15, gasto_potencial_trim_mxn=70000, score=85.0, ingreso_trim_mediano_estimado_mxn=88000)])
    u = _usadas_de(r)
    texto = ("**Lectura:** Roma Norte tiene la mayor probabilidad de apertura (15 %). "                       # falsa: dispara la base
             "Ex Ejido de San Francisco tiene la menor competencia (2.9 competidores ponderados). "           # ya esta en la base
             "ROMA NORTE destaca por su ingreso trimestral estimado por hogar de $88,000.")                   # dato nuevo
    t, quitadas = L.depurar(texto, u)
    assert len(quitadas) == 1 and "Roma Norte tiene la mayor probabilidad" not in t
    assert t.count("menor competencia") == 1                         # la base lo dice una vez y la suelta repetida se quito
    assert "$88,000" in t                                            # lo que no estaba en la base se conserva
    assert "Ex Ejido de San Francisco tiene la mayor probabilidad de apertura (40 %)" in t and "y la menor competencia (2.9 competidores ponderados)" in t


def test_n5_nombres_casi_iguales_se_escriben_con_su_nombre_exacto():
    r, u = _usadas("abarrotes", municipio="Ecatepec de Morelos")
    nombres = [z["colonia"] for z in r["zonas"]]
    assert "JARDINES DE ARAGON" in nombres and "GUADALUPE VICTORIA" in nombres
    n = L.normalizar_nombres
    assert n("jardines de Aragon tiene 9.1 competidores.", r["zonas"]) == "Jardines de Aragón tiene 9.1 competidores."
    assert n("jardines de aragón y guadalupe victoria.", r["zonas"]) == "Jardines de Aragón y Guadalupe Victoria."
    assert n("En Jardines de Aragan hay ruido.", r["zonas"]) == "En Jardines de Aragón hay ruido."        # una letra
    # el nombre exacto del renglon (MAYUSCULAS) tambien se escribe bonito en la prosa
    assert n("JARDINES DE ARAGON y Guadalupe Victoria.", r["zonas"]) == "Jardines de Aragón y Guadalupe Victoria."
    assert n("Jardines de Aragón y Guadalupe Victoria.", r["zonas"]) == "Jardines de Aragón y Guadalupe Victoria."   # el que arma el codigo
    assert n("Guadalupe Victoria Norte es otra colonia.", r["zonas"]) == "Guadalupe Victoria Norte es otra colonia."  # una colonia mas larga no se toca
    assert n("Una colonia cualquiera y la Guadalupana.", r["zonas"]) == "Una colonia cualquiera y la Guadalupana."
    # ejemplos de la evaluacion: «Fuente de Aragon» (es FUENTES DE ARAGON) y «del Valle Norte» con minuscula
    z = [_zona_falsa("FUENTES DE ARAGON", "C1"), _zona_falsa("DEL VALLE NORTE", "C2")]
    assert n("Fuente de Aragon y del Valle Norte destacan.", z) == "Fuentes de Aragón y Del Valle Norte destacan."
    # los acentos bien escritos y la capitalizacion que ya trae la frase no se pierden ni se pasan a mayusculas (N5)
    assert n("Fuentes de Aragón tiene el mayor gasto potencial.", z) == "Fuentes de Aragón tiene el mayor gasto potencial."
    assert n("Fuente de Aragón lidera con ingreso.", z) == "Fuentes de Aragón lidera con ingreso."
    assert n("Fuentes de Aragon tiene el mayor gasto.", z) == "Fuentes de Aragón tiene el mayor gasto."
    zn = [_zona_falsa("MIXCOATL", "C3"), _zona_falsa("AMPLIACION NAPOLES", "C4")]
    assert n("Mixcóatl tiene la menor competencia.", zn) == "Mixcóatl tiene la menor competencia."
    assert n("Ampliación Nápoles destaca y Mixcoatl tambien.", zn) == "Ampliación Nápoles destaca y Mixcóatl tambien."
    assert L._nombre_bonito("BENITO JUAREZ") == "Benito Juárez" and L._nombre_bonito("FUENTES DE ARAGON") == "Fuentes de Aragón"
    assert L._nombre_bonito("LOMAS IX-A") == "Lomas IX-A"
    # y depurar lo aplica a la lectura sin quitar nada
    t, quitadas = L.depurar("**Lectura:** jardines de Aragon tiene un ingreso trimestral estimado por hogar de "
                            f"${r['zonas'][3]['ingreso_trim_mediano_estimado_mxn']:,}.", u)
    assert not quitadas and t.startswith("**Lectura:** Jardines de Aragón tiene")


def test_n10_la_mejor_opcion_no_va_sin_el_aviso_de_una_ageb_casi_vacia():
    r = H.recomendar_zonas("ferreteria")
    vacia = next(z for z in r["zonas"] if z.get("aviso_ageb_poco_poblada"))
    assert vacia["aviso_ageb_poco_poblada"] == ("AGEB con 20 habitantes: el gasto viene del radio de influencia, "
                                                "no de quienes viven en la AGEB")
    f = f"La mejor opción es {vacia['colonia']}."
    assert L.con_aviso_de_ageb_vacia(f, r["zonas"]) == f"La mejor opción es {vacia['colonia']} ({vacia['aviso_ageb_poco_poblada']})."
    ya = f"La mejor opción es {vacia['colonia']}, pero solo tiene 20 habitantes."
    assert L.con_aviso_de_ageb_vacia(ya, r["zonas"]) == ya                                   # ya lo dice
    normal = r["zonas"][0]["colonia"]
    assert L.con_aviso_de_ageb_vacia(f"La mejor opción es {normal}.", r["zonas"]) == f"La mejor opción es {normal}."
    assert L.con_aviso_de_ageb_vacia(f"{vacia['colonia']} tiene la menor competencia.", r["zonas"]) == f"{vacia['colonia']} tiene la menor competencia."
    # dentro de depurar (la zona va de primera en el score): la frase se queda, con su aviso, y la cifra del aviso es valida
    r2 = {**r, "zonas": [dict(vacia, score=99.9)] + [z for z in r["zonas"] if z is not vacia]}
    u = _usadas_de(r2)
    t, quitadas = L.depurar(f"**Lectura:** La mejor opción es {vacia['colonia']}.", u)
    assert not quitadas and "AGEB con 20 habitantes: el gasto viene del radio de influencia" in t
    assert not any(any(_con(fr, u).values()) for fr in L.frases(t.replace("**Lectura:** ", "")))


def test_destaca_con_coma_tambien_se_juzga():
    # «X destaca, con el mayor porcentaje de...»: la coma no corta la busqueda de la zona; el top solo compara menores de 14 anos
    r, u = _usadas("heladeria", municipio="Coyoacán")
    z = r["zonas"][0]["colonia"]
    falsa = f"{z} destaca, con el mayor porcentaje de jóvenes de 15 a 24 años."
    assert _con(falsa, u)["superlativos"]
    t, quitadas = L.depurar("**Lectura:** " + falsa, u)
    assert quitadas and "jóvenes de 15 a 24" not in (t or "")
    # sin coma ya se quitaba (misma regla)
    assert _con(f"{z} destaca con el mayor porcentaje de jóvenes de 15 a 24 años.", u)["superlativos"]


def test_depurar_quita_las_negritas_de_la_lectura():
    r, u = _usadas("heladeria", municipio="Coyoacán")
    z = r["zonas"][0]
    t, quitadas = L.depurar(f"**Lectura:** La colonia **{_nombre(z)}** tiene {z['competidores_ponderados']} competidores ponderados.", u)
    assert not quitadas and "**" not in t.removeprefix("**Lectura:**") and t.startswith("**Lectura:** La colonia ")
    # una lectura sin negritas ni cambios se devuelve intacta
    ok = f"**Lectura:** {L._nombre_bonito(z['colonia'])} tiene {z['competidores_ponderados']} competidores ponderados."
    assert L.depurar(ok, u)[0] == ok


def _nombre(z):
    return z["colonia"]


# --- ronda de la evaluación del 2026-11-24 (arreglador)
def test_captura_con_la_cifra_de_la_edad_clave_se_quita():
    # «Anzures muestra una alta captura del mercado con 62.9 % de la edad clave»: 62.9 % es la edad clave; la captura es otra
    r, u = _usadas("cafeteria")
    z = next(x for x in r["zonas"] if x["edad_clave_pct"] != x["captura_huff_pct"])
    nombre = L._nombre_bonito(z["colonia"])
    mala = f"{nombre} muestra una alta captura del mercado con {z['edad_clave_pct']} % de la edad clave."
    assert any("edad clave, no la captura" in x for x in _con(mala, u)["cifras"])
    t, quitadas = L.depurar("**Lectura:** " + mala, u)
    assert quitadas and mala not in (t or "")
    # lo bien dicho no se toca: cada magnitud con su cifra, o separadas por coma o «y»
    assert not _con(f"{nombre} tiene una captura de {z['captura_huff_pct']} %, con {z['edad_clave_pct']} % de la edad clave.", u)["cifras"]
    assert not _con(f"{nombre} tiene buena captura y {z['edad_clave_pct']} % de la edad clave.", u)["cifras"]
    assert not _con(f"{nombre} tiene {z['edad_clave_pct']} % de la edad clave.", u)["cifras"]


def test_empate_en_el_extremo_sin_decirlo_se_quita_y_se_dice_en_la_base():
    r, u = _usadas("guarderia", municipio="Tlalnepantla de Baz")
    cero = [z for z in r["zonas"] if z["competidores_ponderados"] == min(x["competidores_ponderados"] for x in r["zonas"])]
    assert len(cero) >= 2
    uno = L._nombre_bonito(cero[0]["colonia"])
    mala = f"{uno} tiene la menor competencia ({cero[0]['competidores_ponderados']} competidores ponderados)."
    assert any("empata con" in x for x in _con(mala, u)["superlativos"])
    nombres = " y ".join(L._nombre_bonito(z["colonia"]) for z in cero)
    assert not _con(f"{nombres} empatan con la menor competencia ({cero[0]['competidores_ponderados']} competidores ponderados).", u)["superlativos"]
    assert not _con(f"{uno}, igual que {L._nombre_bonito(cero[1]['colonia'])}, tiene la menor competencia ({cero[0]['competidores_ponderados']} competidores ponderados).", u)["superlativos"]
    t, quitadas = L.depurar("**Lectura:** " + mala, u)
    assert quitadas and "empatan con la menor competencia" in t        # la lectura armada por el codigo si dice el empate


def test_concordancia_del_menor_competencia():
    assert L.corregir_concordancia("Centro tiene el menor competencia con 0.0 competidores.") == "Centro tiene la menor competencia con 0.0 competidores."
    assert L.corregir_concordancia("El mayor probabilidad es de Polanco.") == "La mayor probabilidad es de Polanco."
    assert L.corregir_concordancia("Tiene el mayor gasto potencial.") == "Tiene el mayor gasto potencial."


def test_clausula_mientras_que_se_parte_y_se_salva_la_buena():
    r, u = _usadas("guarderia", municipio="Tlalnepantla de Baz")
    ing = max(r["zonas"], key=lambda z: z["ingreso_trim_mediano_estimado_mxn"])
    cero = [z for z in r["zonas"] if z["competidores_ponderados"] == 0]
    assert len(cero) >= 2
    f = (f"{ing['colonia']} lidera con un ingreso trimestral estimado por hogar de ${ing['ingreso_trim_mediano_estimado_mxn']:,}, "
         f"mientras que {cero[0]['colonia']} tiene el menor competencia con 0.0 competidores ponderados.")
    t, quitadas = L.depurar("**Lectura:** " + f, u)
    assert len(quitadas) == 1 and "empata con" in quitadas[0]
    assert f"${ing['ingreso_trim_mediano_estimado_mxn']:,}" in t       # la clausula buena se conserva
    assert "el menor competencia" not in t


def test_nombres_exactos_en_mayusculas_se_escriben_bonitos_en_la_lectura():
    r, u = _usadas("gimnasio")
    z = r["zonas"][0]
    t, quitadas = L.depurar(f"**Lectura:** {z['colonia']} lidera con un ingreso trimestral estimado por hogar de ${z['ingreso_trim_mediano_estimado_mxn']:,}.", u)
    assert not quitadas and t.startswith("**Lectura:** " + L._nombre_bonito(z["colonia"]))
    assert L._nombre_bonito("POLANCO I SECCIÓN") == "Polanco I Sección" and L._nombre_bonito("DR JORGE JIMENEZ CANTU") == "Dr Jorge Jiménez Cantú"


def test_se_quita_lo_que_repite_la_misma_zona_y_magnitudes():
    r, u = _usadas("gimnasio")
    z = r["zonas"][0]
    nom = L._nombre_bonito(z["colonia"])
    f1 = f"{nom} tiene la mayor probabilidad de apertura ({z['prob_apertura_pct']} %)."
    f2 = f"{nom} destaca por su probabilidad de apertura del {z['prob_apertura_pct']} %."
    assert L.sin_repetir([f1, f2], r["zonas"]) == [f1]
    otra = L._nombre_bonito(r["zonas"][1]["colonia"])
    f3 = f"{otra} tiene un ingreso trimestral estimado por hogar de ${r['zonas'][1]['ingreso_trim_mediano_estimado_mxn']:,}, mientras que {nom} destaca por su probabilidad de apertura del {z['prob_apertura_pct']} %."
    assert L.sin_repetir([f1, f3], r["zonas"]) == [f1, f3.split(", mientras que")[0] + "."]
    assert L.sin_repetir([f3], r["zonas"]) == [f3]            # sin nada dicho antes no se quita nada


def test_pregunta_de_economia_sin_zonas_no_lleva_zonas_en_la_lectura():
    r = H.recomendar_zonas("taqueria")
    m = H.contexto_macro("taqueria")
    u = [{"nombre": "recomendar_zonas", "args": {}, "resultado": r}, {"nombre": "contexto_macro", "args": {}, "resultado": m}]
    z = r["zonas"][3]
    mecanismo = "La inflación general sube el costo de la renta, los servicios y los insumos."
    lect = f"**Lectura:** {mecanismo} {L._nombre_bonito(z['colonia'])} destaca por tener el {z['edad_clave_pct']} % de la edad clave."
    pregunta = "Quiero abrir una taquería, ¿cómo influyen la inflación y la tasa de Banxico?"
    t, quitadas = L.depurar(lect, u, pregunta)
    assert t == f"**Lectura:** {mecanismo}" and len(quitadas) == 1 and "habla de zonas" in quitadas[0]
    # si ademas pide zonas, se quedan
    t2, q2 = L.depurar(lect, u, "¿Dónde abro una taquería y cómo me afecta la inflación?")
    assert not q2 and L._nombre_bonito(z["colonia"]) in t2


def test_depurar_devuelve_la_lectura_sin_la_clausula_repetida():
    r, u = _usadas("gimnasio")
    z = max(r["zonas"], key=lambda x: x["prob_apertura_pct"])
    nom = L._nombre_bonito(z["colonia"])
    otra = next(x for x in r["zonas"] if x is not z)
    f1 = f"{nom} tiene la mayor probabilidad de apertura ({z['prob_apertura_pct']} %)."
    f2 = (f"{nom} destaca por su probabilidad de apertura del {z['prob_apertura_pct']} %, mientras que {L._nombre_bonito(otra['colonia'])} "
          f"tiene un ingreso trimestral estimado por hogar de ${otra['ingreso_trim_mediano_estimado_mxn']:,}.")
    t, quitadas = L.depurar(f"**Lectura:** {f1} {f2}", u)
    assert not quitadas and nom + " destaca" not in t and "mientras que" not in t
    assert t == f"**Lectura:** {f1} {L._nombre_bonito(otra['colonia'])} tiene un ingreso trimestral estimado por hogar de ${otra['ingreso_trim_mediano_estimado_mxn']:,}."
