"""Pruebas de los checks de eval/evaluar.py (sin LLM): que detecten cifras y AGEB inventadas."""
import importlib.util
from pathlib import Path

from app import herramientas as H
from app import motor

_spec = importlib.util.spec_from_file_location("evaluar", Path(__file__).resolve().parents[1] / "eval" / "evaluar.py")
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)


def _respuesta(zonas, extra=""):
    lineas = [f"{i}. **{z['colonia']}**, {z['municipio']} (AGEB {z['ageb']}): score {z['score']}/100. "
              f"Prob. de apertura {z['prob_apertura_pct']} %, gasto potencial ${z['gasto_potencial_trim_mxn']:,} por trimestre, "
              f"{z['competidores_ponderados']} competidores (captura {z['captura_huff_pct']} %)." for i, z in enumerate(zonas, 1)]
    return "\n".join(lineas) + extra + "\n**Fuentes:** INEGI, DENUE 05/2026; Censo 2020."


def _caso(texto, res):
    q = {"id": 1, "tipo": "giro", "giro": "heladeria", "pregunta": "quiero poner una heladeria"}
    r = {"respuesta": texto, "latencia_s": 10.0, "herramientas": [{"nombre": "recomendar_zonas", "args": {}, "resultado": res}]}
    return ev.calificar(q, r, motor.cargar_features(), [])


def test_respuesta_fiel_pasa():
    res = H.recomendar_zonas("heladeria")
    c = _caso(_respuesta(res["zonas"]), res)
    assert c["pasa"], c


def test_cifra_inventada_falla():
    res = H.recomendar_zonas("heladeria")
    texto = _respuesta(res["zonas"], "\nAdemas la renta promedio es de $48,750 y el trafico de 12,345 personas, con 37.3 % de margen.")
    c = _caso(texto, res)
    assert not c["checks"]["cifras"] and "48,750" in " ".join(c["detalle"]["cifras_no_encontradas"])


def test_ageb_inventada_falla():
    res = H.recomendar_zonas("heladeria")
    zonas = [dict(z) for z in res["zonas"]]
    zonas[0]["ageb"] = "0900200019999"
    assert not _caso(_respuesta(zonas), res)["checks"]["top_agebs"]


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
    texto = _respuesta(res["zonas"], "\n**Giros que conviene considerar**: libreria (viabilidad 83 %).")
    assert not _caso(texto, res)["checks"]["sin_giros_inventados"]
