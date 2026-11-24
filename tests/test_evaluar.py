"""Pruebas de los checks de eval/evaluar.py (sin LLM): que detecten cifras y AGEB inventadas."""
import importlib.util
from pathlib import Path

from app import herramientas as H
from app import motor

_spec = importlib.util.spec_from_file_location("evaluar", Path(__file__).resolve().parents[1] / "eval" / "evaluar.py")
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)


def _respuesta(zonas, extra="", fuentes=None, avisos=()):
    lineas = [f"{i}. **{z['colonia']}**, {z['municipio']} (AGEB {z['ageb']}): score {z['score']}/100 (relativo al giro). {z['resumen_texto']}."
              for i, z in enumerate(zonas, 1)]
    riesgos = ("\n\n**Riesgos:**\n" + "\n".join(f"- {a[0].upper() + a[1:]}" for a in avisos)) if avisos else ""
    return "\n".join(lineas) + extra + riesgos + "\n\n**Fuentes:** " + "; ".join(fuentes or []) + "."


def _caso(texto, res, q=None, extra_tools=()):
    q = q or {"id": 1, "tipo": "giro", "giro": "heladeria", "pregunta": "quiero poner una heladeria"}
    r = {"respuesta": texto, "latencia_s": 10.0,
         "herramientas": [{"nombre": "recomendar_zonas", "args": {}, "resultado": res}, *extra_tools]}
    return ev.calificar(q, r, motor.cargar_features(), [])


def _ok(res, extra="", q=None, extra_tools=()):
    return _caso(_respuesta(res["zonas"], extra, res["fuentes"], res.get("avisos", ())), res, q, extra_tools)


def test_respuesta_fiel_pasa():
    res = H.recomendar_zonas("heladeria")
    c = _ok(res)
    assert c["pasa"], c
    assert c["checks"]["ingreso_y_edad"] and c["checks"]["colonia_de_su_ageb"] and c["checks"]["cifras_por_zona"]


def test_cifra_inventada_falla():
    res = H.recomendar_zonas("heladeria")
    c = _ok(res, "\nAdemas la renta promedio es de $48,750 y el trafico de 12,345 personas, con 37.3 % de margen.")
    assert not c["checks"]["cifras"] and "48,750" in " ".join(c["detalle"]["cifras_no_encontradas"])


def test_ageb_inventada_falla():
    res = H.recomendar_zonas("heladeria")
    zonas = [dict(z) for z in res["zonas"]]
    zonas[0]["ageb"] = "0900200019999"
    assert not _caso(_respuesta(zonas, "", res["fuentes"]), res)["checks"]["top_agebs"]


# --- huecos que dejo el evaluador anterior (revision critica E1)
def test_cifra_de_otra_zona_falla():
    res = H.recomendar_zonas("heladeria")
    zonas = [dict(z) for z in res["zonas"]]
    zonas[0]["resumen_texto"] = zonas[0]["resumen_texto"].replace(f"{zonas[0]['prob_apertura_pct']} %", f"{zonas[1]['prob_apertura_pct']} %", 1)
    zonas[0]["resumen_texto"] = zonas[0]["resumen_texto"].replace(_p(zonas[0]["gasto_potencial_trim_mxn"]), _p(zonas[1]["gasto_potencial_trim_mxn"]))
    c = _caso(_respuesta(zonas, "", res["fuentes"]), res)
    assert not c["checks"]["cifras_por_zona"] and c["detalle"]["cifras_de_otra_zona"]


def _p(v):
    return f"${v:,.0f}"


def test_colonias_intercambiadas_fallan():
    res = H.recomendar_zonas("heladeria")
    zonas = [dict(z) for z in res["zonas"]]
    zonas[0]["colonia"], zonas[1]["colonia"] = zonas[1]["colonia"], zonas[0]["colonia"]
    c = _caso(_respuesta(zonas, "", res["fuentes"]), res)
    assert not c["checks"]["colonia_de_su_ageb"]


def test_colonia_nombrada_sin_origen_falla():
    res = H.recomendar_zonas("heladeria")
    c = _ok(res, "\nTambien podrias mirar POLANCO o la COLONIA INVENTADA XYZ.")
    assert not c["checks"]["colonias_con_origen"] and "polanco" in c["detalle"]["colonias_sin_origen"]
    zonas = [dict(z) for z in res["zonas"]]
    zonas[2]["colonia"] = "COLONIA INVENTADA XYZ"
    assert not _caso(_respuesta(zonas, "", res["fuentes"]), res)["checks"]["colonias_con_origen"]


def test_fuentes_cortadas_y_formato():
    res = H.recomendar_zonas("heladeria")
    c = _caso(_respuesta(res["zonas"], "", res["fuentes"][:2]), res)
    assert not c["checks"]["fuentes_completas"]
    assert not _ok(res, "\nprob. de apertura % 63")["checks"]["formato"]
    assert not _ok(res, "\nel tipo de cambio fijo es 19.02")["checks"]["formato"]


def test_sin_ingreso_ni_edad_falla():
    res = H.recomendar_zonas("heladeria")
    zonas = [dict(z, resumen_texto=f"prob. de apertura {z['prob_apertura_pct']} %") for z in res["zonas"]]
    assert not _caso(_respuesta(zonas, "", res["fuentes"]), res)["checks"]["ingreso_y_edad"]


def test_colonia_respetada_y_colonia_inexistente():
    q = {"id": 21, "tipo": "giro", "giro": "heladeria", "colonia": {"regex": "^polanco", "muns": ["09016"]}, "pregunta": "heladeria en Polanco"}
    res = H.recomendar_zonas("heladeria", colonia="Polanco")
    assert _caso(_respuesta(res["zonas"], "", res["fuentes"]), res, q)["checks"]["colonia_respetada"]
    lejos = H.recomendar_zonas("heladeria")                          # el top de la ZMVM no esta cerca de Polanco
    assert not _caso(_respuesta(lejos["zonas"], "", lejos["fuentes"]), lejos, q)["checks"]["colonia_respetada"]
    qi = {"id": 24, "tipo": "giro", "giro": "papeleria", "colonia_inexistente": "Villa Esperanza Imaginaria", "pregunta": "papeleria en la colonia Villa Esperanza Imaginaria"}
    ri = H.recomendar_zonas("papeleria", colonia="Villa Esperanza Imaginaria")
    texto = "> " + ri["aviso_colonia"] + "\n\n" + _respuesta(ri["zonas"], "", ri["fuentes"])
    assert _caso(texto, ri, qi)["checks"]["colonia_respetada"]
    assert not _caso(_respuesta(ri["zonas"], "", ri["fuentes"]), ri, qi)["checks"]["colonia_respetada"]   # sin avisar


def test_seguimiento_mantiene_giro():
    q = {"id": 25, "tipo": "giro", "giro": "heladeria", "municipio": "09003", "pregunta": "¿Y en Coyoacán?",
         "historial": [{"role": "user", "content": "Quiero poner una heladería"}]}
    res = H.recomendar_zonas("heladeria", municipio="Coyoacán")
    assert _caso(_respuesta(res["zonas"], "", res["fuentes"]) + "\nSigo con heladería.", res, q)["checks"]["seguimiento_mantiene_giro"]
    otro = H.recomendar_zonas("abarrotes", municipio="Coyoacán")
    assert not _caso(_respuesta(otro["zonas"], "", otro["fuentes"]), otro, q)["checks"]["seguimiento_mantiene_giro"]


def test_macro_breve():
    res = H.recomendar_zonas("heladeria")
    mac = H.contexto_macro("heladeria")
    tool = {"nombre": "contexto_macro", "args": {}, "resultado": mac}
    ok = _ok(res, "\n**Contexto económico:** " + mac["linea"], extra_tools=[tool])
    assert ok["checks"]["macro_breve"], ok
    assert not _ok(res, extra_tools=[tool])["checks"]["macro_breve"]          # sin la linea macro
    largo = _ok(res, "\n**Contexto económico:** " + mac["linea"] + " Banxico " + "x " * 400, extra_tools=[tool])
    assert not largo["checks"]["macro_breve"]


def test_millones_y_porcentajes_equivalentes():
    nums = {429000.0, 0.94}
    assert ev.coincide(ev.cifras_citadas("gasto de $0.43 millones", "")[0], nums)
    assert ev.coincide(ev.cifras_citadas("probabilidad de 94 %", "")[0], nums)
    assert not ev.coincide(ev.cifras_citadas("gasto de $0.52 millones", "")[0], nums)


def test_sugerir_con_una_sola_opcion_falla():
    res = H.sugerir_giros(municipio="Coyoacán")
    uno = res["giros"][0]["giro"].replace("_", " ")
    q = {"id": 17, "tipo": "sugerir", "pregunta": "Quiero poner un negocio en Coyoacán"}
    texto = f"Te recomiendo una {uno}. **Fuentes:** INEGI, DENUE."
    r = {"respuesta": texto, "latencia_s": 10.0, "herramientas": [{"nombre": "sugerir_giros", "args": {}, "resultado": res}]}
    c = ev.calificar(q, r, motor.cargar_features(), [])
    assert not c["checks"]["alternativas"] and not c["checks"]["score_relativo"]


def test_viabilidad_sin_sugerir_falla():
    res = H.recomendar_zonas("libreria")
    assert not _ok(res, "\n**Giros que conviene considerar**: libreria (viabilidad 83 %).")["checks"]["sin_giros_inventados"]


def test_lectura_con_cifra_de_otra_zona_o_magnitud_confundida_falla():
    res = H.recomendar_zonas("heladeria", colonia="Polanco")
    z0, z1 = res["zonas"][0], res["zonas"][1]
    base = _respuesta(res["zonas"], "", res["fuentes"])
    bien = (f"**Lectura:** {z0['colonia']} tiene un ingreso trimestral estimado de ${z0['ingreso_trim_mediano_estimado_mxn']:,} "
            f"y {z1['colonia']} un gasto potencial de ${z1['gasto_potencial_trim_mxn']:,} por trimestre.\n\n")
    assert _caso(bien + base, res)["checks"]["lectura_cifras_de_su_zona"]
    # el ingreso presentado como gasto potencial
    mal = f"**Lectura:** {z0['colonia']} tiene un gasto potencial de ${z0['ingreso_trim_mediano_estimado_mxn']:,}.\n\n"
    assert not _caso(mal + base, res)["checks"]["lectura_cifras_de_su_zona"]
    # la prob. de apertura de una zona atribuida a otra
    otra = z1["prob_apertura_pct"] if z1["prob_apertura_pct"] != z0["prob_apertura_pct"] else z1["prob_apertura_pct"] + 3
    mal2 = f"**Lectura:** {z0['colonia']} tiene una prob. de apertura de {otra} %.\n\n"
    assert not _caso(mal2 + base, res)["checks"]["lectura_cifras_de_su_zona"] or otra in (z0["prob_apertura_pct"],)


def test_destacados_de_zonas():
    r = H.recomendar_zonas("heladeria", municipio="Coyoacán")
    d = r["destacados"]
    assert d["rango_ingreso_trimestral_estimado_mxn"][0] <= d["rango_ingreso_trimestral_estimado_mxn"][1]
    mejor = max(r["zonas"], key=lambda z: z["ingreso_trim_mediano_estimado_mxn"])
    assert d["mayor_ingreso_estimado"]["colonia"] == mejor["colonia"]
    assert d["menor_competencia"]["competidores ponderados"] == min(z["competidores_ponderados"] for z in r["zonas"])


# --- mutaciones de la lectura (revision critica del nucleo): cifra de otra zona, superlativo falso, colonia inventada
Q_POLANCO = {"id": 901, "tipo": "giro", "grupo": "colonia", "giro": "cafeteria", "colonia": {"regex": "^polanco", "muns": ["09016"]},
             "pregunta": "Quiero poner una cafetería en Polanco, ¿dónde me conviene?"}
LECTURA_BASE = ("**Lectura:** Polanco II Sección tiene la mayor probabilidad de apertura (98 %). Granada tiene el mayor gasto potencial "
                "($17,792,000 por trimestre) y el 67.2 % de la edad clave (25 a 59 años). Ampliación Granada tiene la menor competencia "
                "(1.4 competidores ponderados) y un ingreso trimestral estimado por hogar de $111,400.\n\n")


def _polanco(cambio=None, extra=""):
    res = H.recomendar_zonas("cafeteria", colonia="Polanco")
    lectura = LECTURA_BASE if cambio is None else LECTURA_BASE.replace(*cambio)
    assert cambio is None or lectura != LECTURA_BASE
    return _caso(lectura + extra + _respuesta(res["zonas"], "", res["fuentes"]), res, Q_POLANCO)["checks"]


def test_lectura_fiel_pasa_las_revisiones():
    c = _polanco()
    assert c["lectura_cifras_de_su_zona"] and c["lectura_superlativos"] and c["colonias_con_origen"], c


def test_lectura_cifra_de_la_zona_vecina_falla():
    # M2a: el ingreso de Granada atribuido a Ampliación Granada (la coincidencia mas larga manda)
    assert not _polanco(("$111,400", "$169,400"))["lectura_cifras_de_su_zona"]
    # M2d: el % de la edad clave de Ampliación Granada atribuido a Granada
    assert not _polanco(("el 67.2 % de la edad clave", "el 59.0 % de la edad clave"))["lectura_cifras_de_su_zona"]
    # M2e: los competidores de Granada atribuidos a Ampliación Granada
    assert not _polanco(("(1.4 competidores", "(2.5 competidores"))["lectura_cifras_de_su_zona"]
    # M2b: cifra inventada
    assert not _polanco(("$111,400", "$123,456"))["lectura_cifras_de_su_zona"]


def test_lectura_superlativo_falso_falla():
    # M2f: «la mayor probabilidad de apertura» es de Polanco II Sección (98 %), no de Granada (88 %, cuarta)
    assert not _polanco(("Polanco II Sección tiene la mayor", "Granada tiene la mayor"))["lectura_superlativos"]
    # la menor competencia es de Ampliación Granada (1.4); Polanco IV Sección (3.4) no
    assert not _polanco(("Ampliación Granada tiene la menor competencia", "Polanco IV Sección tiene la menor competencia"))["lectura_superlativos"]


def test_lectura_en_la_colonia_pedida_con_zona_de_fuera_falla():
    res = H.recomendar_zonas("cafeteria", colonia="Polanco")
    lectura = "**Lectura:** En Polanco, la colonia Granada destaca por el mayor gasto potencial ($17,792,000 por trimestre).\n\n"
    c = _caso(lectura + _respuesta(res["zonas"], "", res["fuentes"]), res, Q_POLANCO)["checks"]
    assert not c["lectura_superlativos"]
    ok = "**Lectura:** Granada, a 1.0 km de Polanco, tiene el mayor gasto potencial ($17,792,000 por trimestre).\n\n"
    assert _caso(ok + _respuesta(res["zonas"], "", res["fuentes"]), res, Q_POLANCO)["checks"]["lectura_superlativos"]


def test_lectura_colonia_inventada_falla():
    # M3a: «la colonia Lomas de Zorbalandia» no sale de ninguna herramienta
    c = _polanco(("Ampliación Granada tiene la menor", "También conviene la colonia Lomas de Zorbalandia. Ampliación Granada tiene la menor"))
    assert not c["colonias_con_origen"]
    # una colonia que si sale de las herramientas no se marca
    assert _polanco(("Ampliación Granada tiene la menor", "También sirve la colonia Granada. Ampliación Granada tiene la menor"))["colonias_con_origen"]


def test_colonia_parcial_con_aviso_cuenta_como_respetada():
    qi = {"id": 902, "tipo": "giro", "giro": "farmacia", "colonia_inexistente": "Villa Esmeralda del Bosque Azul",
          "pregunta": "Quiero poner una farmacia en la colonia Villa Esmeralda del Bosque Azul"}
    ri = H.recomendar_zonas("farmacia", colonia="Villa Esmeralda del Bosque Azul")
    texto = "> " + ri["aviso_colonia"] + "\n\n" + _respuesta(ri["zonas"], "", ri["fuentes"])
    assert _caso(texto, ri, qi)["checks"]["colonia_respetada"]
    assert not _caso(_respuesta(ri["zonas"], "", ri["fuentes"]), ri, qi)["checks"]["colonia_respetada"]   # sin avisar


# --- huecos que dejo la evaluacion final: None impreso, avisos del giro, mecanismo macro
def test_none_impreso_falla_el_formato():
    res = H.recomendar_zonas("heladeria")
    assert _ok(res)["checks"]["formato"]
    malo = _ok(res, "\nOjo: 25 a 59 años: None %.")
    assert not malo["checks"]["formato"]


def test_avisos_de_giro_raro_y_rubro_sustituto_deben_mostrarse():
    res = H.recomendar_zonas("renta_bicicletas")
    q = {"id": 16, "tipo": "giro", "giro": "renta_bicicletas", "pregunta": "negocio de renta de bicicletas"}
    sin = _caso(_respuesta(res["zonas"], "", res["fuentes"]), res, q)
    assert not sin["checks"]["avisos_del_giro"]
    con = _caso(_respuesta(res["zonas"], "", res["fuentes"], res["avisos"]), res, q)
    assert con["checks"]["avisos_del_giro"]


def test_orden_de_sugerir_se_revisa_en_la_lectura():
    sg = H.sugerir_giros(municipio="Coyoacán")
    r = H.recomendar_zonas(sg["giros"][0]["giro"], municipio="Coyoacán")
    g = sg["giros"]
    n = [H.nombre_giro(x["giro"]) for x in g]
    q = {"id": 17, "tipo": "sugerir", "pregunta": "Quiero poner un negocio en Coyoacán"}
    tools = [{"nombre": "sugerir_giros", "args": {}, "resultado": sg}]
    base = _respuesta(r["zonas"], "", r["fuentes"] + sg["fuentes"])

    def cal(lectura):
        return _caso(f"**Lectura:** {lectura}\n\n" + base, r, q, tools)["checks"]

    assert cal(f"{n[0]} es el primero y {n[2]} el tercero.")["orden_sugerir"]
    assert not cal(f"{n[2]} va antes que {n[0]}.")["orden_sugerir"]
    c = cal(f"{n[2]} lidera con mayor viabilidad ({g[0]['viabilidad_pct']} %).")
    assert not c["lectura_superlativos"] and not c["lectura_cifras_de_su_zona"]
