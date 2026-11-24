"""Fuera de tema, red de seguridad, registro local de preguntas y detalles menores del agente (2026-11-24). Textos fijos, sin LLM."""
import json
import time

import pytest
from fastapi.testclient import TestClient

from app import agente, historial
from app import fuera_de_tema as F
from app import herramientas as H
from app import lectura as L
from app.api import preguntar
from app.servidor import crear_app

HIST = [{"role": "user", "content": "Quiero poner una heladería"}, {"role": "assistant", "content": "Te muestro las zonas."}]

DE_NEGOCIO = [
    "¿qué negocio pongo en Coyoacán?", "quiero poner algo barato", "¿cuánto ganan ahí?", "¿y en Polanco?", "¿qué me recomiendas?",
    "hola, quiero poner una heladería en Tlalpan", "gracias, ¿y en Iztapalapa?", "¿cómo está la economía?",
    "una tienda para niños en Coyoacán", "Quiero abrir una nevería en Polanco", "¿y en el sur?", "gracias, ¿y en el sur?",
    "¿es buen momento?", "¿y una veterinaria?", "¿cómo me afecta la competencia?", "¿qué es el score?", "hola buenas, ¿dónde pongo una cafetería?",
    "¿cuál es el dólar hoy para abrir un negocio?", "Quiero abrir una taquería, ¿cómo influyen la inflación y la tasa de Banxico?",
    "¿dónde abro una cafetería de especialidad?", "Quiero poner una heladería en Monterrey",
    "¿qué puedes hacer para ayudarme a abrir una cafetería en Coyoacán?", "me llamo Juan quiero cafetería",   # revisor 2026-11-24
    "¿cuánto capital de trabajo necesito?", "¿y una escuela de música?", "¿qué día es mejor para inaugurar?",
]
AJENAS = {
    "nombre": ["¿Cómo me llamo?", "como me llamo", "¿quién soy?", "¿cuál es mi nombre?", "¿sabes cómo me llamo?"],
    "saludo": ["hola", "Hola!", "buenas noches", "buenos días", "gracias", "muchas gracias", "ok gracias", "adiós", "¿cómo estás?",
               "hola, ¿me puedes ayudar?", "¿quién eres?", "¿qué puedes hacer?", "me llamo Juan", "hasta luego"],
    "ajeno": ["¿Quién ganó el último mundial?", "¿quién ganó el partido de ayer?", "cuéntame un chiste", "¿va a llover mañana?",
              "¿qué clima hace hoy?", "escríbeme un código en python", "¿cuántos años tienes?", "¿cuál es la capital de Francia?",
              "dame las noticias de hoy", "¿quién es el presidente?", "¿qué hora es?", "dame una receta de pozole", "¿cuál es mi color favorito?"],
}


@pytest.mark.parametrize("hist", [None, HIST], ids=["sin_historial", "con_historial"])
def test_detector_no_toca_las_preguntas_de_negocio(hist):
    for q in DE_NEGOCIO:
        assert F.tipo_fuera_de_tema(q, hist) is None, q
        assert agente.fuera_de_tema(q, hist) is None, q


@pytest.mark.parametrize("hist", [None, HIST], ids=["sin_historial", "con_historial"])
def test_detector_reconoce_nombre_saludo_y_tema_ajeno(hist):
    for tipo, preguntas in AJENAS.items():
        for q in preguntas:
            assert F.tipo_fuera_de_tema(q, hist) == tipo, (q, F.clasificar(q, hist))


def test_una_senal_de_negocio_gana_al_patron_ajeno():
    for q in ("hola, ¿cómo me llamo? quiero una heladería", "¿quién ganó el mundial? abriré una papelería en Tlalpan",
              "¿cómo está el clima económico para mi negocio?", "no sé cómo me llamo pero quiero un gimnasio"):
        assert F.tipo_fuera_de_tema(q) is None, q
    # y el historial de negocio no vuelve de negocio una pregunta ajena
    assert F.tipo_fuera_de_tema("¿quién ganó el último mundial?", HIST) == "ajeno"


def test_textos_fijos_dicen_que_solo_contestan_de_negocios_en_la_zmvm():
    n = agente.fuera_de_tema("¿Cómo me llamo?")
    assert n["tipo"] == "nombre" and n["texto"] == (
        "No sé cómo te llamas: solo contesto dónde conviene poner un negocio en la Zona Metropolitana del Valle de México, con datos de "
        "INEGI, DENUE, ENIGH, CONAPO y Banxico. Prueba con «quiero poner una heladería en Coyoacán» o «¿qué negocio pongo en Tlalpan?».")
    a = agente.fuera_de_tema("¿Quién ganó el último mundial?")
    assert a["texto"].startswith("De eso no sé: solo contesto dónde conviene poner un negocio en la Zona Metropolitana del Valle de México")
    s = agente.fuera_de_tema("hola")
    assert s["tipo"] == "saludo" and s["texto"].startswith("¡Hola!") and "solo contesto dónde conviene poner un negocio" in s["texto"]
    assert agente.fuera_de_tema("gracias")["texto"].startswith("¡Con gusto!")
    for q in sum(AJENAS.values(), []):
        t = agente.fuera_de_tema(q)["texto"]
        assert "Zona Metropolitana del Valle de México" in t and "«¿qué negocio pongo en Tlalpan?»" in t and not F.menciona_funciones(t), q


def test_pre_consulta_y_plantilla_de_fuera_de_tema_sin_herramientas():
    for q in ("¿Cómo me llamo?", "hola", "¿Quién ganó el último mundial?"):
        assert agente.pre_consulta(q) == [] and agente.pre_consulta(q, HIST) == []
        assert agente.plantilla([], None, q) == agente.fuera_de_tema(q)["texto"]
    assert [k for k, _ in agente.pre_consulta("quiero poner una heladeria")] == ["perfil_giro", "recomendar_zonas", "contexto_macro"]
    # sin herramientas y sin pregunta fuera de tema, la plantilla sigue igual
    assert "Top 5 para farmacia" in agente.plantilla([{"nombre": "recomendar_zonas", "args": {}, "resultado": H.recomendar_zonas("farmacia")}])


def test_responder_fuera_de_tema_no_llama_al_llm(monkeypatch):
    def no(*_, **__):
        raise AssertionError("no debe cargar el cliente de Ollama")
    monkeypatch.setattr(agente, "_cliente", no)
    out = agente.responder("¿Cómo me llamo?")
    assert out["modo"] == "fuera_de_tema" and out["herramientas"] == [] and out["fuera_de_tema"] is True and out["tipo_fuera_de_tema"] == "nombre"
    assert out["respuesta"].startswith("No sé cómo te llamas") and out["metricas"]["tokens_generados"] == 0


# ---------------------------------------------------------------- red de seguridad
FALLA = ('No tienes un giro definido. Para ayudarte, usa la función "sugerir_giros" con los parámetros correspondientes. '
         'Por ejemplo: sugerir_giros(municipio="Tlalnepantla", nse="medio") para ver giros de nivel socioeconomico medio.')


def test_red_de_seguridad_quita_funciones_internas():
    assert F.menciona_funciones(FALLA) and F.menciona_funciones("llama a perfil_giro") and F.menciona_funciones("f(x=1, y=2)")
    assert not F.menciona_funciones("Top 5 para farmacia. El AUC (n=5) es bajo y la tasa (6.5 %) cayó.")
    t = F.sin_funciones_internas("Las zonas de Coyoacán tienen más hogares. Usa recomendar_zonas(giro='farmacia') para verlas. "
                                 "El ingreso estimado es de $110,800 por hogar al trimestre en el municipio.")
    assert "recomendar_zonas" not in t and "(giro=" not in t and "$110,800" in t and t.startswith("Las zonas de Coyoacán")
    lista = F.sin_funciones_internas("Pasos:\n- Llama a ficha_zona para la colonia.\n- El gasto potencial viene del Censo 2020 y del DENUE.")
    assert "ficha_zona" not in lista and "- El gasto potencial viene del Censo 2020 y del DENUE." in lista
    # si no queda nada util, el texto fijo de tema ajeno
    assert F.sin_funciones_internas(FALLA) == F.TEXTO_AJENO
    assert F.sin_funciones_internas(FALLA, reemplazo="") == ""
    assert F.sin_funciones_internas("Texto normal sin nada raro.") == "Texto normal sin nada raro."


def test_cerrar_con_revision_no_deja_pasar_la_falla_real_del_2026_11_24():
    usadas = [{"nombre": "perfil_giro", "args": {"texto": "¿Cómo me llamo?"}, "resultado": H.perfil_giro("¿Cómo me llamo?")}]
    out = agente.cerrar(FALLA, usadas, pregunta="¿Cómo me llamo?")
    assert out == F.TEXTO_AJENO and "sugerir_giros" not in out and "Tlalnepantla" not in out
    # con datos que mostrar, solo se quitan las frases con funciones: la lectura buena se conserva
    z = [{"nombre": "recomendar_zonas", "args": {}, "resultado": H.recomendar_zonas("heladeria", municipio="Coyoacán")}]
    r = z[0]["resultado"]["zonas"][0]
    texto = (f"**Lectura:** {L._nombre_bonito(r['colonia'])} tiene un ingreso trimestral estimado por hogar de "
             f"${r['ingreso_trim_mediano_estimado_mxn']:,}. Para más zonas usa recomendar_zonas(giro='heladeria', top=10).")
    out = agente.cerrar(texto, z, pregunta="heladería en Coyoacán")
    assert "recomendar_zonas" not in out and "top=10" not in out and "**Lectura:**" in out and f"${r['ingreso_trim_mediano_estimado_mxn']:,}" in out


def test_pulir_texto_del_tablero_tambien_la_aplica():
    assert preguntar._pulir_texto(FALLA) == F.TEXTO_AJENO
    assert "contexto_macro" not in preguntar._pulir_texto("La tasa de Banxico es 6.5 %. Revisa contexto_macro(giro='x') para el detalle de la serie.")
    assert preguntar._pulir_texto("La tasa es 6.5 %") == "La tasa es 6.5%"      # el retoque de siempre sigue igual


# ---------------------------------------------------------------- registro local de preguntas
def test_registro_escribe_una_linea_legible(tmp_path):
    ok = historial.registrar("¿Cómo me llamo?", HIST, "rapido", True, [{"nombre": "perfil_giro", "args": {"texto": "x"}, "resultado": {"gran": "resultado"}}],
                             "No sé cómo te llamas...", 0.4, tipo_fuera_de_tema="nombre", carpeta=tmp_path, tokens=[])
    assert ok
    (fila,) = historial.leer(tmp_path)
    assert fila["pregunta"] == "¿Cómo me llamo?" and fila["historial"] == HIST and fila["modo"] == "rapido"
    assert fila["fuera_de_tema"] is True and fila["tipo_fuera_de_tema"] == "nombre" and fila["latencia_s"] == 0.4
    assert fila["herramientas"] == [{"nombre": "perfil_giro", "args": {"texto": "x"}}]      # solo nombre y argumentos
    assert fila["fecha"][:4].isdigit() and "T" in fila["fecha"] and fila["respuesta"].startswith("No sé")
    historial.registrar("otra", None, "llm", False, None, "r", 1.0, carpeta=tmp_path, tokens=[])
    assert [f["pregunta"] for f in historial.leer(tmp_path)] == ["¿Cómo me llamo?", "otra"]


def test_registro_no_guarda_tokens(tmp_path, monkeypatch):
    token = "tok_secreto_de_prueba_123456"
    monkeypatch.setattr(historial, "tokens_env", lambda: [token])
    historial.registrar(f"mi token es {token}", [{"role": "user", "content": token}], "llm", False,
                        [{"nombre": "x", "args": {"t": token}}], f"respuesta con {token}", 1.0, carpeta=tmp_path)
    crudo = (tmp_path / historial.ARCHIVO).read_text(encoding="utf-8")
    assert token not in crudo and historial.OCULTO in crudo
    # el filtro es el mismo del evaluador (valores de .env de 8 o mas caracteres)
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("evaluar", Path(__file__).resolve().parents[1] / "eval" / "evaluar.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    assert ev.tokens_env() == [token]


def test_registro_no_rompe_si_falla(tmp_path, monkeypatch):
    archivo = tmp_path / "es_un_archivo"
    archivo.write_text("x")
    assert historial.registrar("p", None, "llm", False, None, "r", 1.0, carpeta=archivo / "adentro", tokens=[]) is False   # no se puede crear la carpeta
    assert historial.registrar("p", None, "llm", False, [object()], "r", 1.0, carpeta=tmp_path, tokens=[]) is True         # lo que no es dict se salta
    assert historial.registrar("p", {"raro": {1, 2}}, "llm", False, None, "r", 1.0, carpeta=tmp_path, tokens=[]) is True        # un set se guarda como lista
    monkeypatch.setattr(historial, "limpiar", lambda *_: (_ for _ in ()).throw(RuntimeError("falla")))
    assert historial.registrar("p", None, "llm", False, None, "r", 1.0, carpeta=tmp_path, tokens=[]) is False              # cualquier error: False


def test_registro_apagado_por_el_entorno(tmp_path, monkeypatch):
    monkeypatch.setattr(historial, "CARPETA", tmp_path / "h")
    monkeypatch.setenv("DONDE_SIN_HISTORIAL", "1")
    assert historial.registrar("p", None, "llm", False, None, "r", 1.0, tokens=[]) is False and not (tmp_path / "h").exists()
    monkeypatch.delenv("DONDE_SIN_HISTORIAL")
    assert historial.registrar("p", None, "llm", False, None, "r", 1.0, tokens=[]) is True and (tmp_path / "h" / historial.ARCHIVO).exists()


@pytest.fixture()
def cliente_con_registro(tmp_path, monkeypatch):
    monkeypatch.setattr(historial, "CARPETA", tmp_path / "historial")
    monkeypatch.delenv("DONDE_SIN_HISTORIAL")
    web = tmp_path / "web"
    web.mkdir()
    (web / "index.html").write_text('<!doctype html><div id="root"></div>', encoding="utf-8")
    return TestClient(crear_app(web)), tmp_path / "historial"


def _esperar(cliente, pid, tope=15):
    t0 = time.time()
    while time.time() - t0 < tope:
        v = cliente.get(f"/api/preguntas/{pid}").json()
        if v["estado"] in ("listo", "error", "cancelada"):
            return v
        time.sleep(0.05)
    raise AssertionError(v)


@pytest.mark.parametrize("rapido", [True, False], ids=["rapido", "con_llm"])
def test_api_fuera_de_tema_cumple_el_contrato(cliente_con_registro, monkeypatch, rapido):
    cliente, carpeta = cliente_con_registro
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: True)

    def no_debe_correr(*_, **__):
        raise AssertionError("fuera de tema no usa el LLM")
    monkeypatch.setattr(agente, "responder", no_debe_correr)
    for q, tipo in (("¿Cómo me llamo?", "nombre"), ("hola", "saludo"), ("¿Quién ganó el último mundial?", "ajeno")):
        j = cliente.post("/api/preguntas", json={"pregunta": q, "rapido": rapido}).json()
        assert j["estado"] == "listo" and j["fuera_de_tema"] is True and j["tipo_fuera_de_tema"] == tipo
        g = cliente.get(f"/api/preguntas/{j['id']}?completo=1").json()
        assert g["fuera_de_tema"] is True and g["tipo_fuera_de_tema"] == tipo and g["herramientas"] == []
        assert g["respuesta"] == agente.fuera_de_tema(q)["texto"] and "Zona Metropolitana del Valle de México" in g["respuesta"]
        d = g["datos"]
        assert d["zonas"] == [] and "mapa" not in d and d["giro"] is None and d["fuera_de_tema"] is True and d["tipo_fuera_de_tema"] == tipo
        assert "fuera_de_alcance" not in d and g["modo"] == ("rapido" if rapido else "plantilla")
    filas = historial.leer(carpeta)
    assert [f["pregunta"] for f in filas] == ["¿Cómo me llamo?", "hola", "¿Quién ganó el último mundial?"]
    assert all(f["fuera_de_tema"] and f["herramientas"] == [] for f in filas) and filas[0]["tipo_fuera_de_tema"] == "nombre"


def test_api_normal_trae_fuera_de_tema_falso_y_se_registra(cliente_con_registro):
    cliente, carpeta = cliente_con_registro
    h = HIST
    j = cliente.post("/api/preguntas", json={"pregunta": "¿y en Coyoacán?", "historial": h, "rapido": True}).json()
    assert j["fuera_de_tema"] is False and j["tipo_fuera_de_tema"] is None and j["datos"]["zonas"]
    (fila,) = historial.leer(carpeta)
    assert fila["pregunta"] == "¿y en Coyoacán?" and fila["historial"] == h and fila["modo"] == "rapido" and fila["fuera_de_tema"] is False
    assert [x["nombre"] for x in fila["herramientas"]][:2] == ["perfil_giro", "recomendar_zonas"] and set(fila["herramientas"][0]) == {"nombre", "args"}
    assert "Top 5" in fila["respuesta"] and fila["latencia_s"] is not None


def test_api_con_llm_registra_al_terminar_y_si_falla_el_registro_responde(cliente_con_registro, monkeypatch):
    cliente, carpeta = cliente_con_registro
    monkeypatch.setattr(preguntar, "_hay_modelo", lambda: True)
    monkeypatch.setattr(agente, "responder", lambda p, h=None, **_: {
        "respuesta": f"Respuesta de {p}\n\n**Fuentes:** x.", "herramientas": [{"nombre": "perfil_giro", "args": {"texto": p}, "resultado": {}}],
        "latencia_s": 0.1, "modo": "llm", "modelo": "qwen3:8b", "rondas": 1, "herencia": None, "cortada": False, "metricas": {}})
    j = cliente.post("/api/preguntas", json={"pregunta": "una farmacia en Iztapalapa"}).json()
    v = _esperar(cliente, j["id"])
    assert v["estado"] == "listo" and v["fuera_de_tema"] is False
    time.sleep(0.2)
    (fila,) = historial.leer(carpeta)
    assert fila["modo"] == "llm" and fila["respuesta"].startswith("Respuesta de una farmacia") and fila["latencia_s"] == 0.1
    # si escribir falla, la respuesta no se rompe
    monkeypatch.setattr(historial, "CARPETA", carpeta / "no" / "se" / "puede")
    monkeypatch.setattr(historial, "tokens_env", lambda: (_ for _ in ()).throw(RuntimeError("falla")))
    j2 = cliente.post("/api/preguntas", json={"pregunta": "una papelería en Tlalpan", "rapido": True})
    assert j2.status_code == 200 and j2.json()["estado"] == "listo" and j2.json()["respuesta"]


def test_script_historial_imprime_legible(tmp_path, capsys):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("script_historial", Path(__file__).resolve().parents[1] / "scripts" / "historial.py")
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    assert s.main(["--carpeta", str(tmp_path)]) == 0 and "Todavía no hay preguntas" in capsys.readouterr().out
    for i in range(25):
        historial.registrar(f"pregunta {i}", None, "rapido" if i % 2 else "llm", False, None, f"Línea uno {i}\n\nLínea dos\nl3\nl4", 1.5,
                            carpeta=tmp_path, tokens=[])
    assert s.main(["--carpeta", str(tmp_path)]) == 0
    o = capsys.readouterr().out
    assert "20 de 25 preguntas" in o and "pregunta 24" in o and "pregunta 4\n" not in o and "Línea uno 24" in o and "l4" not in o and "1.5 s" in o
    assert s.main(["--carpeta", str(tmp_path), "--todas"]) == 0
    assert "25 de 25 preguntas" in capsys.readouterr().out
    assert s.primeras_lineas("a\n\nb\nc\nd", 3) == ["a", "b", "c"] and len(s.primeras_lineas("x" * 300)[0]) == 110


# ---------------------------------------------------------------- detalles menores (5a-5d)
def test_5a_nombre_exacto_en_mayusculas_se_escribe_bonito_aunque_siga_otra_palabra():
    z = [{"colonia": "POLANCO I SECCIÓN", "ageb": "A"}, {"colonia": "GUADALUPE VICTORIA", "ageb": "B"}]
    n = L.normalizar_nombres
    assert n("POLANCO I SECCIÓN lidera.", z) == "Polanco I Sección lidera."
    assert n("En POLANCO I SECCIÓN Miguel Hidalgo hay poco.", z) == "En Polanco I Sección Miguel Hidalgo hay poco."
    assert n("Guadalupe Victoria Norte es otra colonia.", z) == "Guadalupe Victoria Norte es otra colonia."
    assert n("GUADALUPE VICTORIA NORTE es otra.", z) == "GUADALUPE VICTORIA NORTE es otra."      # en mayusculas y mas larga: no se toca


def test_5b_fuentes_duplicadas_salen_una_vez_con_los_ids():
    r = H.contexto_macro("taqueria")
    assert "INEGI, Banco de Indicadores API" in r["fuentes"]          # la herramienta las trae repetidas
    fu = agente.fuentes_de([{"nombre": "contexto_macro", "args": {}, "resultado": r}])
    bie = [f for f in fu if f.startswith("INEGI, Banco de Indicadores API")]
    assert bie == ["INEGI, Banco de Indicadores API (BIE, ids 910406, 910408 y 910411)"]
    assert agente.unir_fuentes(["A", "B (id 1)", "A", "C"]) == ["A", "B (id 1)", "C"]
    assert agente.unir_fuentes(["B", "A", "B (id 1)"]) == ["A", "B (id 1)"]
    assert agente.unir_fuentes(["X (BIE, id 1)", "X (BIE, id 2)"]) == ["X (BIE, ids 1 y 2)"]
    assert agente.unir_fuentes(["X", "X (BIE, id 7)"]) == ["X (BIE, id 7)"]
    assert agente.unir_fuentes(["Y", "Y"]) == ["Y"]
    texto = agente.plantilla([{"nombre": "contexto_macro", "args": {}, "resultado": r}], None, "¿cómo está la economía?")
    assert texto.count("Banco de Indicadores API") == 1


def test_5c_todos_los_riesgos_terminan_con_punto():
    r = dict(H.recomendar_zonas("ferreteria"))
    r["avisos"] = ["primer aviso sin punto", "segundo aviso con punto.", "tercero entre paréntesis (AUC 0.5)"]
    bloque = agente._bloque_riesgos([{"nombre": "recomendar_zonas", "args": {}, "resultado": r}])[0]
    lineas = [x for x in bloque.splitlines() if x.startswith("- ")]
    assert len(lineas) >= 3 and all(x.endswith(".") and not x.endswith("..") for x in lineas), lineas


def test_5d_ninos_la_lectura_nombra_la_zona_con_mayor_0_a_14():
    pregunta = "Quiero una heladería en Coyoacán para niños, ¿cuánto ganan ahí?"
    r = H.recomendar_zonas("heladeria", municipio="Coyoacán")
    u = [{"nombre": "recomendar_zonas", "args": {}, "resultado": r}]
    mayor = max(r["zonas"], key=lambda z: z["edad_clave_pct"])
    frase = L.frase_edad_ninos(u, pregunta)
    assert frase == f"{L._nombre_bonito(mayor['colonia'])} tiene el mayor porcentaje de población de 0 a 14 años del top ({mayor['edad_clave_pct']} %)."
    ctx = L.Contexto(u, pregunta)
    assert L.problemas(frase, ctx) == {"cifras": [], "superlativos": []}          # pasa los mismos checks de la lectura
    assert L.frase_edad_ninos(u, "heladería en Coyoacán") is None                  # solo si la pregunta habla de niños
    gim = [{"nombre": "recomendar_zonas", "args": {}, "resultado": H.recomendar_zonas("gimnasio")}]
    assert L.frase_edad_ninos(gim, "gimnasio para niños") is None                   # el top no compara la edad de 0 a 14 años
    # en la respuesta: se agrega a la lectura del modelo, una sola vez
    lectura = f"**Lectura:** {L._nombre_bonito(r['zonas'][0]['colonia'])} tiene el mayor gasto potencial."
    out = agente.cerrar(lectura, u, pregunta=pregunta)
    assert out.count(frase) == 1 and "**Lectura:**" in out
    assert agente.cerrar(f"**Lectura:** {frase}", u, pregunta=pregunta).count(frase) == 1
    sin_lectura = agente.cerrar("", u, pregunta=pregunta)
    assert frase in sin_lectura
    assert frase not in agente.cerrar(lectura, u, pregunta="heladería en Coyoacán")


# ---------------------------------------------------------------- el evaluador
def test_evaluador_califica_fuera_de_tema_y_funciones_internas():
    import importlib.util
    from pathlib import Path
    from app import motor
    spec = importlib.util.spec_from_file_location("evaluar", Path(__file__).resolve().parents[1] / "eval" / "evaluar.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    q = {"id": 29, "tipo": "fuera_de_tema", "pregunta": "¿Cómo me llamo?"}
    ok = ev.calificar(q, {"respuesta": F.texto_fijo("nombre"), "latencia_s": 0.1, "herramientas": []}, motor.cargar_features(), [])
    assert ok["pasa"] and ok["checks"]["fuera_de_tema"] and ok["checks"]["sin_funciones_internas"] and "fuentes" not in ok["checks"]
    malo = ev.calificar(q, {"respuesta": FALLA, "latencia_s": 0.1, "herramientas": []}, motor.cargar_features(), [])
    assert not malo["checks"]["fuera_de_tema"] and not malo["checks"]["sin_funciones_internas"] and not malo["pasa"]
    con_zonas = ev.calificar(q, {"respuesta": F.texto_fijo("nombre") + " AGEB 0900300011389.", "latencia_s": 0.1, "herramientas": []},
                             motor.cargar_features(), [])
    assert not con_zonas["checks"]["fuera_de_tema"]
