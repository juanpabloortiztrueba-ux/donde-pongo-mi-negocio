"""Pruebas del agente sin LLM: reglas de pre-consulta y respaldo cuando Ollama no responde."""
from app import agente


def _nombres(plan):
    return [k for k, _ in plan]


def test_pre_consulta_reglas():
    assert _nombres(agente.pre_consulta("quiero poner una heladeria")) == ["perfil_giro", "recomendar_zonas"]
    p = dict(agente.pre_consulta("una farmacia en Iztapalapa"))
    assert p["recomendar_zonas"] == {"giro": "farmacia", "municipio": "Iztapalapa"}
    assert "contexto_macro" in _nombres(agente.pre_consulta("como esta la inflacion y la tasa de Banxico para abrir un negocio"))
    assert "recomendar_zonas" not in _nombres(agente.pre_consulta("como esta la inflacion para abrir un negocio"))
    p = dict(agente.pre_consulta("algo barato para una zona de nivel bajo"))
    assert p["sugerir_giros"] == {"nse": "bajo", "ticket_max": 100}
    p = dict(agente.pre_consulta("una heladeria en Monterrey"))
    assert p["recomendar_zonas"]["municipio"] == "Monterrey"


def test_respaldo_sin_ollama(monkeypatch):
    monkeypatch.setattr(agente, "HOST", "http://localhost:9")  # puerto cerrado
    out = agente.responder("quiero poner una farmacia en Iztapalapa")
    assert out["modo"] == "plantilla"
    assert "Top 5 para farmacia" in out["respuesta"] and "Fuentes" in out["respuesta"]


def test_reglas_solo_cuando_aplican():
    from app import agente as A
    base = A.system_para([])
    assert "sugerir_giros (la persona" not in base and "aviso_prob_baja" not in base
    u = [{"nombre": "recomendar_zonas", "resultado": {"encontrado": True, "aviso_prob_baja": "x"}}]
    assert "No hables de «viabilidad»" in A.system_para(u)
    u = [{"nombre": "sugerir_giros", "resultado": {"encontrado": True}}]
    assert "Giros que conviene considerar" in A.system_para(u)
