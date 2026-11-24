"""Pruebas del agente sin LLM: reglas de pre-consulta y respaldo cuando Ollama no responde."""
from app import agente


def _nombres(plan):
    return [k for k, _ in plan]


def test_pre_consulta_reglas():
    assert _nombres(agente.pre_consulta("quiero poner una heladeria")) == ["perfil_giro", "recomendar_zonas", "contexto_macro"]
    p = dict(agente.pre_consulta("una farmacia en Iztapalapa"))
    assert p["recomendar_zonas"] == {"giro": "farmacia", "municipio": "Iztapalapa"}
    assert p["ficha_municipio"] == {"municipio": "Iztapalapa"}
    assert "contexto_macro" in _nombres(agente.pre_consulta("como esta la inflacion y la tasa de Banxico para abrir un negocio"))
    assert "recomendar_zonas" not in _nombres(agente.pre_consulta("como esta la inflacion para abrir un negocio"))
    p = dict(agente.pre_consulta("algo barato para una zona de nivel bajo"))
    assert p["sugerir_giros"] == {"nse": "bajo", "inversion": "baja"}
    p = dict(agente.pre_consulta("una heladeria en Monterrey"))
    assert p["recomendar_zonas"]["municipio"] == "Monterrey"


def test_respaldo_sin_ollama(monkeypatch):
    monkeypatch.setattr(agente, "HOST", "http://localhost:9")  # puerto cerrado
    out = agente.responder("quiero poner una farmacia en Iztapalapa")
    assert out["modo"] == "plantilla"
    assert "Top 5 para farmacia" in out["respuesta"] and "Fuentes" in out["respuesta"]


def test_reglas_solo_cuando_aplican():
    from app import agente as A
    from app import herramientas as H
    base = A.system_para([])
    assert "sugerir_giros (la persona" not in base and "aviso_prob_baja" not in base
    u = [{"nombre": "recomendar_zonas", "resultado": {"encontrado": True, "aviso_prob_baja": "x"}}]
    assert "No hables de «viabilidad»" in A.system_para(u)
    u = [{"nombre": "sugerir_giros", "resultado": {"encontrado": True}}]
    assert "la persona no trae giro" in A.system_para(u)
    # la regla de «solo lectura y riesgos» aparece solo si el sistema muestra bloques de datos
    assert "Escribe SOLO una sección" not in base
    z = [{"nombre": "recomendar_zonas", "args": {}, "resultado": H.recomendar_zonas("heladeria", municipio="Coyoacán")}]
    assert "Escribe SOLO una sección" in A.system_para(z)


# ---------------------------------------------------------------- colonias y seguimientos (2026-11-23)
def test_pre_consulta_detecta_colonia():
    p = dict(agente.pre_consulta("Quiero abrir una nevería en Polanco"))
    assert p["recomendar_zonas"] == {"giro": "heladeria", "colonia": "Polanco"}
    assert p["ficha_municipio"] == {"municipio": "Miguel Hidalgo"} and p["contexto_macro"] == {"giro": "heladeria"}
    assert dict(agente.pre_consulta("¿Dónde pongo una cafetería en la Condesa?"))["recomendar_zonas"]["colonia"] == "la Condesa"
    # una palabra comun que es nombre de colonia no cuenta sin pista de lugar
    assert "colonia" not in dict(agente.pre_consulta("quiero una cafeteria moderna"))["recomendar_zonas"]
    # colonia que no existe: igual se manda, para que la herramienta avise
    p = dict(agente.pre_consulta("Quiero abrir una papelería en la colonia Villa Esperanza Imaginaria"))
    assert p["recomendar_zonas"]["colonia"] == "Villa Esperanza Imaginaria"
    # municipio con nombre de colonia no se confunde
    assert "colonia" not in dict(agente.pre_consulta("farmacia en Benito Juárez"))["recomendar_zonas"]


def test_seguimiento_hereda_giro_y_ubicacion():
    h1 = [{"role": "user", "content": "Quiero poner una heladería, ¿en qué colonias me conviene?"},
          {"role": "assistant", "content": "Te muestro las zonas."}]
    p = dict(agente.pre_consulta("¿Y en Coyoacán?", h1))
    assert p["recomendar_zonas"] == {"giro": "heladeria", "municipio": "Coyoacán"}
    assert "sugerir_giros" not in p and p["perfil_giro"] == {"texto": "heladeria"}
    # sin historial la firma vieja sigue igual
    assert "sugerir_giros" in dict(agente.pre_consulta("¿y en Coyoacán?")) or "recomendar_zonas" not in dict(agente.pre_consulta("¿y en Coyoacán?"))
    # giro nuevo + marca de seguimiento: conserva la ubicacion
    h2 = [{"role": "user", "content": "Quiero abrir una farmacia en Benito Juárez"}]
    p = dict(agente.pre_consulta("¿Y una veterinaria?", h2))
    assert p["recomendar_zonas"] == {"giro": "veterinaria", "municipio": "Benito Juárez"}
    # un giro nuevo sin marca de seguimiento NO hereda la colonia anterior
    h3 = [{"role": "user", "content": "heladería en Polanco"}]
    assert "colonia" not in dict(agente.pre_consulta("quiero abrir una farmacia", h3))["recomendar_zonas"]
    # «un negocio en general» no hereda el giro
    assert "sugerir_giros" in dict(agente.pre_consulta("Quiero poner un negocio en Coyoacán", h1))
    # colonia heredada
    h4 = [{"role": "user", "content": "heladería en la Condesa"}]
    assert dict(agente.pre_consulta("¿y una papelería?", h4))["recomendar_zonas"]["colonia"] == "la Condesa"


def test_barato_es_poca_inversion_no_ticket():
    p = dict(agente.pre_consulta("algo barato para una zona de nivel bajo"))
    assert p["sugerir_giros"] == {"nse": "bajo", "inversion": "baja"} and "ticket_max" not in p["sugerir_giros"]


def test_cerrar_formato_aviso_y_fuentes():
    usadas = [{"nombre": "recomendar_zonas", "args": {}, "resultado": {
        "encontrado": False, "aviso_colonia": "NO ENCONTRADO: «Xyz» no aparece como colonia. A cambio se muestra el top, SIN filtro de colonia.",
        "fuentes": ["INEGI, DENUE", "Banco de Mexico, SIE"]}}]
    t = agente.cerrar("1. **A**: prob. de apertura % 63 y captura % 100; 63%; tipo de cambio fijo 19.02\n**Fuentes:** solo INEGI, DENUE; Banco de M",
                      usadas)
    assert "prob. de apertura 63 %" in t and "captura 100 %" in t and "63 %;" in t and "tipo de cambio FIX" in t
    assert t.startswith("> NO ENCONTRADO")                                  # el aviso no depende del modelo
    assert t.rstrip().endswith("INEGI, DENUE; Banco de Mexico, SIE.") and t.count("Fuentes") == 1
    # respuesta cortada por num_predict: se quita el renglon a medias y las fuentes quedan completas
    t = agente.cerrar("**Lectura:** bien\n**Riesgos:**\n- uno\n- dos a medi", usadas, cortada=True)
    assert "dos a medi" not in t and "Banco de Mexico, SIE." in t


def test_bloques_arma_zonas_giros_y_orden_sin_llm():
    from app import herramientas as H
    z = H.recomendar_zonas("heladeria", colonia="Polanco")
    sg = H.sugerir_giros(municipio="Coyoacán")
    usadas = [{"nombre": "sugerir_giros", "args": {}, "resultado": sg}, {"nombre": "recomendar_zonas", "args": {}, "resultado": z},
              {"nombre": "contexto_macro", "args": {}, "resultado": H.contexto_macro("heladeria")},
              {"nombre": "ficha_municipio", "args": {}, "resultado": H.ficha_municipio("Miguel Hidalgo")}]
    t = "\n\n".join(agente.bloques(usadas, {"giro": "heladeria"}))
    assert t.startswith("> Filtro por colonia") or "> Filtro por colonia" in t
    assert "Sigo con heladería" in t
    # los giros salen en el orden de la herramienta
    pos = [t.index(H.nombre_giro(g["giro"])) for g in sg["giros"]]
    assert pos == sorted(pos)
    # cada renglon de zona trae su colonia, su AGEB y sus cifras (ingreso y edad)
    for i, zz in enumerate(z["zonas"], 1):
        assert f"{i}. **{zz['colonia']}**, {zz['municipio']} (AGEB {zz['ageb']}): score {zz['score']}/100. {zz['resumen_texto']}." in t
    assert "**Contexto económico:**" in t and "**Sobre Miguel Hidalgo:**" in t
    assert agente.bloques([], None) == []


def test_respaldo_sin_ollama_trae_bloques_y_fuentes(monkeypatch):
    monkeypatch.setattr(agente, "HOST", "http://localhost:9")
    out = agente.responder("quiero abrir una nevería en Polanco")
    t = out["respuesta"]
    assert out["modo"] == "plantilla" and "> Filtro por colonia" in t and "**Contexto económico:**" in t
    assert "ingreso trimestral estimado" in t and "0 a 14 años" in t and "**Riesgos:**" in t and "**Fuentes:**" in t


def test_para_llm_es_compacto_y_conserva_lo_citable():
    from app import herramientas as H
    r = H.recomendar_zonas("heladeria", colonia="Polanco")
    c = agente.para_llm("recomendar_zonas", r)
    assert len(H.a_json(c)) < 0.6 * len(H.a_json(r))
    assert c["aviso_colonia"] == r["aviso_colonia"] and c["zonas"][0]["datos"] == r["zonas"][0]["resumen_texto"]
    assert "en_colonia_consultada" in c["zonas"][0]


def test_cerrar_con_datos_ordena_lectura_bloques_riesgos_y_fuentes():
    from app import herramientas as H
    z = H.recomendar_zonas("heladeria", colonia="Polanco")
    usadas = [{"nombre": "recomendar_zonas", "args": {}, "resultado": z}]
    crudo = "**Lectura:** Polanco IV tiene ingreso alto %\n**Riesgos:**\n- inventado por el modelo\n**Fuentes:** inventadas"
    t = agente.cerrar(crudo, usadas)
    i = [t.index(x) for x in ("> Filtro por colonia", "**Lectura:**", "**Top 5 para heladería**", "**Riesgos:**", "**Fuentes:**")]
    assert i == sorted(i)
    assert "inventado por el modelo" not in t and "inventadas" not in t          # riesgos y fuentes los arma el codigo
    assert t.count("**Riesgos:**") == 1 and "ENIGH no representa colonias" in t
    # sin lectura util del modelo igual sale la respuesta completa
    assert "**Lectura:**" not in agente.cerrar("", usadas) and "**Top 5" in agente.cerrar("", usadas)


# --- correcciones de la revision critica del nucleo
def test_colonia_inexistente_que_empieza_con_una_real_no_se_resuelve_en_silencio():
    from app import herramientas as H
    from app import lugares
    q = "Quiero poner una farmacia en la colonia Villa Esmeralda del Bosque Azul"
    d = lugares.detectar(q)
    assert len(d) == 1 and d[0]["parcial"] and d[0]["texto_pedido"] == "Villa Esmeralda del Bosque Azul"
    assert d[0]["resolucion"]["criterio"] == "parcial" and d[0]["resolucion"]["usada"] == "villa esmeralda"
    # el plan manda lo que pidio la persona, no el nombre corto
    assert dict(agente.pre_consulta(q))["recomendar_zonas"]["colonia"] == "Villa Esmeralda del Bosque Azul"
    r = H.recomendar_zonas("farmacia", colonia="Villa Esmeralda del Bosque Azul")
    av = r["aviso_colonia"]
    assert av.startswith("NO ENCONTRADO: «Villa Esmeralda del Bosque Azul»") and "más parecida, «Villa Esmeralda» (Tultitlán)" in av
    assert r["filtros"]["colonia"] == "Villa Esmeralda" and r["filtros"]["colonia_no_encontrada"] == "Villa Esmeralda del Bosque Azul"
    assert r["colonia_consultada"]["parcial"]
    # la colonia real sigue sin aviso de NO ENCONTRADO
    assert not H.recomendar_zonas("farmacia", colonia="Villa Esmeralda")["aviso_colonia"].startswith("NO ENCONTRADO")
    # y «Polanco y Condesa» siguen siendo dos colonias, no un nombre inventado
    assert [x["frase"] for x in lugares.detectar("farmacia en Polanco y Condesa")] == ["polanco", "condesa"]


def test_nombre_exacto_gana_al_alias_y_no_encontrado_sugiere():
    from app import lugares
    assert dict(agente.pre_consulta("una cafetería en la Roma Sur"))["recomendar_zonas"]["colonia"] == "Roma Sur"
    assert dict(agente.pre_consulta("una cafetería en la Roma"))["recomendar_zonas"]["colonia"] == "la Roma"
    d = lugares.detectar("farmacia en Polanquito Norte")[0]
    assert not d["encontrada"] and any("Polanco" in s for s in d["sugerencias"])
    from app import herramientas as H
    assert "Polanco" in H.recomendar_zonas("farmacia", colonia="Polanquito Norte")["aviso_colonia"]


def test_lectura_se_revisa_contra_destacados():
    from app import herramientas as H
    r = H.recomendar_zonas("cafeteria", colonia="Polanco")
    usadas = [{"nombre": "recomendar_zonas", "args": {}, "resultado": r}]
    d = r["destacados"]
    assert d["mayor_prob_apertura"]["colonia"] == "POLANCO II SECCIÓN"   # Granada (88 %) es la cuarta en prob. de apertura
    falsa = "**Lectura:** En Polanco, la colonia Granada tiene la mayor probabilidad de apertura (88 %). Ambas son opciones viables."
    t, quitadas = agente.cerrar_con_revision(falsa, usadas)
    assert quitadas and "Granada tiene la mayor probabilidad" not in t and "Ambas son opciones" not in t
    assert "Polanco II Sección tiene la mayor probabilidad de apertura (98 %)" in t        # la arma el codigo con destacados
    buena = "**Lectura:** Polanco II Sección tiene la mayor probabilidad de apertura (98 %)."
    t2, q2 = agente.cerrar_con_revision(buena, usadas)
    assert not q2 and buena in t2
    # el filtro de colonia: «en Polanco, la colonia Granada» miente aunque la cifra sea correcta
    assert agente.lectura_mod.problemas_de_frase("En Polanco, la colonia Granada tiene un ingreso de $169,400.", r["zonas"], r["filtros"])
    assert not agente.lectura_mod.problemas_de_frase("Granada, a 1.0 km de Polanco, tiene el mayor gasto potencial.", r["zonas"], r["filtros"])
