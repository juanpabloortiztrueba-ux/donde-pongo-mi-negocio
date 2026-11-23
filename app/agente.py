"""Agente local: qwen3:8b (Ollama) con tool calling sobre app/herramientas.py.

    uv run python app/agente.py "quiero poner una heladeria"

Flujo:
1. Pre-consulta deterministica (sin LLM): con reglas simples se llaman las herramientas obvias
   (perfil_giro, recomendar_zonas, contexto_macro, sugerir_giros) y sus resultados entran a la
   conversacion como llamadas ya hechas. Ahorra rondas del modelo (latencia) y lo ancla en datos.
2. Bucle de tool calling: el modelo puede pedir mas herramientas (ficha_zona, buscar_carpetas...)
   hasta MAX_RONDAS; luego redacta.
3. Si Ollama no responde, se arma una respuesta de plantilla con los mismos resultados (modo 'plantilla').
Todo corre en la Mac: no usa internet.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import herramientas as H  # noqa: E402
from app import rag  # noqa: E402

MODELO = "qwen3:8b"
HOST = "http://localhost:11434"
MAX_RONDAS = 4
OPCIONES = {"temperature": 0.2, "num_ctx": 8192, "num_predict": 1100}

SYSTEM = """Eres un asesor de ubicación de negocios para la Zona Metropolitana del Valle de México (ZMVM: 16 alcaldías de la CDMX, 59 municipios del Estado de México y Tizayuca, Hidalgo). Respondes en español de México, claro y directo.

Reglas duras:
- Usa SOLO cifras, colonias, municipios y claves AGEB que aparezcan en los resultados de las herramientas. Copia los números tal como vienen (puedes poner comas de miles o el signo de pesos). No calcules cifras nuevas, no inventes datos ni colonias.
- Si una herramienta dice "NO ENCONTRADO" o encontrado=false, dilo así. Si piden un lugar fuera de la ZMVM (por ejemplo Monterrey), di claramente que está fuera de alcance del modelo y NO des colonias.
- El NSE, el decil y el ingreso por colonia son estimaciones del proyecto: di "estimado". El ticket promedio es un supuesto.
- Si falta información, llama otra herramienta (ficha_zona, buscar_carpetas, contexto_macro) antes de responder.
- El score 0-100 es un percentil DENTRO de cada giro: ordena colonias para ese giro, no dice que el giro sea viable y no sirve para comparar giros.

Formato cuando hay recomendación de zonas:
**Top 5 para <giro>**
1. **<colonia>**, <municipio> (AGEB <clave>): score <score>/100 (relativo al giro). Por qué: <2 o 3 cifras de la herramienta: prob. de apertura %, gasto potencial por trimestre, competidores ponderados y captura %, residentes objetivo en el radio, empleos en el radio, NSE estimado>.
(repite para las 5)
**Riesgos:** 2 a 4 viñetas (competencia, confiabilidad del modelo, supuestos, que "apareció en el DENUE" no es lo mismo que "abrió").
**Fuentes:** lista las fuentes que regresaron las herramientas (INEGI Censo 2020, DENUE, ENIGH 2024, CONAPO, modelo del proyecto, Banxico...).

Para preguntas de economía (macro) responde con los indicadores, su fecha y su serie, y la sección **Fuentes**. No uses más de 350 palabras."""


# Reglas que solo se agregan cuando aplican (si van siempre, el modelo las aplica donde no toca e inventa cifras)
REGLA_SUGERIR = """
Esta vez se llamó sugerir_giros (la persona no trae giro). Empieza con **Giros que conviene considerar**: lista TODOS los giros que regresó sugerir_giros, en su orden, con su viabilidad %, prob. de apertura % y prob. de seguir abierto % tal como vienen. Di que se ordenan por esas probabilidades absolutas y que el score de colonias es relativo dentro de cada giro (no compara giros). Después da el top de colonias del primero."""
REGLA_PROB_BAJA = """
Esta vez recomendar_zonas trae "aviso_prob_baja": la probabilidad de apertura es baja en todo el top. Ponlo como PRIMER riesgo con sus cifras y di que el score alto es relativo al giro, no prueba de que el giro sea viable. No hables de «viabilidad» ni listes otros giros: aquí no se llamó sugerir_giros."""


def system_para(usadas: list[dict]) -> str:
    """Prompt del sistema mas las reglas que aplican a los resultados ya obtenidos."""
    extra = ""
    if any(u["nombre"] == "sugerir_giros" and isinstance(u["resultado"], dict) and u["resultado"].get("encontrado")
           for u in usadas):
        extra += REGLA_SUGERIR
    elif any(u["nombre"] == "recomendar_zonas" and isinstance(u["resultado"], dict) and u["resultado"].get("aviso_prob_baja")
             for u in usadas):
        extra += REGLA_PROB_BAJA
    return SYSTEM + extra


def _f(nombre: str, desc: str, props: dict, req: list[str]) -> dict:
    return {"type": "function", "function": {"name": nombre, "description": desc,
                                             "parameters": {"type": "object", "properties": props, "required": req}}}


S = {"type": "string"}
TOOLS = [
    _f("perfil_giro", "Identifica el giro del catalogo a partir del texto del usuario (sinonimos) y da sus supuestos: SCIAN, radio, cliente objetivo, ticket.",
       {"texto": {**S, "description": "texto libre, p. ej. 'quiero poner una neveria'"}}, ["texto"]),
    _f("recomendar_zonas", "Top de colonias (AGEB) de la ZMVM para un giro, con score 0-100 y sus razones en numeros. Filtros opcionales por municipio/alcaldia y por NSE estimado.",
       {"giro": {**S, "description": "clave del giro (p. ej. heladeria)"},
        "municipio": {**S, "description": "municipio o alcaldia de la ZMVM (opcional)"},
        "nse": {**S, "enum": ["bajo", "medio", "alto"], "description": "nivel socioeconomico estimado (opcional)"},
        "top": {"type": "integer", "description": "cuantas colonias (1-10, default 5)"}}, ["giro"]),
    _f("ficha_zona", "Datos de una AGEB (clave de 13 caracteres) o de una colonia por nombre: poblacion, edades, NSE estimado, negocios, transporte; con giro, su score ahi.",
       {"zona": {**S, "description": "clave AGEB o nombre de colonia"},
        "municipio": {**S, "description": "municipio para desambiguar (opcional)"},
        "giro": {**S, "description": "clave del giro (opcional)"}}, ["zona"]),
    _f("buscar_carpetas", "Busca en las carpetas de informacion del proyecto: metodologia (Censo, DENUE, ENIGH, NSE), fichas por municipio, teoria de localizacion, explicacion del modelo y alcance.",
       {"pregunta": S, "k": {"type": "integer", "description": "trozos (1-8, default 4)"}}, ["pregunta"]),
    _f("contexto_macro", "Ultimos indicadores macro de Mexico: tasa objetivo de Banxico, TIIE 28, tipo de cambio FIX, remesas, inflacion INPC, confianza del consumidor y consumo privado.", {}, []),
    _f("sugerir_giros", "Cuando el usuario no tiene giro: giros del catalogo que mejor salen en un municipio y/o NSE, opcionalmente con ticket maximo (negocio barato).",
       {"municipio": S, "nse": {**S, "enum": ["bajo", "medio", "alto"]},
        "ticket_max": {"type": "number", "description": "ticket promedio maximo en pesos"},
        "top": {"type": "integer"}}, []),
]

MACRO = re.compile(r"\b(inflacion|inpc|tasa|tasas|banxico|tipo de cambio|dolar|remesas|economia|macro|tiie|consumo privado|confianza del consumidor|interes)\b")
NSE = re.compile(r"\b(?:nivel|nse|zona|clase|estrato)\s+(?:socioeconomico\s+|economico\s+|de nivel\s+)?(bajo|medio|alto|baja|media|alta)\b")
BARATO = re.compile(r"\b(barato|barata|economico|poca inversion|bajo costo|poco dinero)\b")


def pre_consulta(pregunta: str) -> list[tuple[str, dict]]:
    """Herramientas obvias segun reglas simples; regresa [(nombre, argumentos)]."""
    n = H.norm(pregunta)
    plan: list[tuple[str, dict]] = [("perfil_giro", {"texto": pregunta})]
    perfil = H.perfil_giro(pregunta)
    giro = perfil.get("giro")
    fuera = rag.ciudades_fuera(pregunta)
    muns = rag.municipios_en(pregunta)
    m = NSE.search(n)
    nse = {"baja": "bajo", "media": "medio", "alta": "alto"}.get(m.group(1), m.group(1)) if m else None
    if fuera:
        if giro:
            plan.append(("recomendar_zonas", {"giro": giro, "municipio": fuera[0].title()}))
        plan.append(("buscar_carpetas", {"pregunta": pregunta, "k": 2}))
        return plan
    if MACRO.search(n):
        plan.append(("contexto_macro", {}))
    mun = muns[0] if len(muns) == 1 else None
    if giro:
        plan.append(("recomendar_zonas", {"giro": giro, "municipio": mun, "nse": nse}))
    elif mun or nse or BARATO.search(n) or ("negocio" in n and not MACRO.search(n)):
        args = {"municipio": mun, "nse": nse, "ticket_max": 100 if BARATO.search(n) else None}
        plan.append(("sugerir_giros", args))
        sg = H.sugerir_giros(**{k: v for k, v in args.items() if v})
        if sg.get("encontrado"):
            plan.append(("recomendar_zonas", {"giro": sg["giros"][0]["giro"], "municipio": mun, "nse": nse}))
    return [(k, {a: b for a, b in v.items() if b not in (None, "")}) for k, v in plan]


def _cliente():
    import ollama
    return ollama.Client(host=HOST, timeout=240)


def _tool_calls(msg) -> list[tuple[str, dict]]:
    out = []
    for tc in (getattr(msg, "tool_calls", None) or []):
        args = tc.function.arguments
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        out.append((tc.function.name, dict(args or {})))
    return out


def _limpia(texto: str) -> str:
    """Quita bloques <think> si el modelo los deja."""
    return re.sub(r"<think>.*?</think>", "", texto or "", flags=re.S).strip()


def responder(pregunta: str, historial: list[dict] | None = None, modelo: str = MODELO,
              pre: bool = True, max_rondas: int = MAX_RONDAS) -> dict:
    """Respuesta del agente. Regresa {respuesta, herramientas:[{nombre, args, resultado}], latencia_s, rondas, modo}."""
    t0 = time.time()
    msgs = [{"role": "system", "content": SYSTEM}] + list(historial or []) + [{"role": "user", "content": pregunta}]
    usadas: list[dict] = []

    def correr(nombre, args):
        res = H.ejecutar(nombre, args)
        usadas.append({"nombre": nombre, "args": args, "resultado": res})
        return {"role": "tool", "content": H.a_json(res), "tool_name": nombre}

    if pre:
        plan = pre_consulta(pregunta)
        msgs.append({"role": "assistant", "content": "",
                     "tool_calls": [{"function": {"name": k, "arguments": a}} for k, a in plan]})
        msgs += [correr(k, a) for k, a in plan]
        msgs[0] = {"role": "system", "content": system_para(usadas)}

    rondas, modo, texto = 0, "llm", ""
    try:
        cli = _cliente()
        while True:
            rondas += 1
            ultima = rondas >= max_rondas
            r = cli.chat(model=modelo, messages=msgs, tools=None if ultima else TOOLS, think=False,
                         options=OPCIONES, keep_alive="15m")
            llamadas = _tool_calls(r.message)
            if llamadas and not ultima:
                msgs.append({"role": "assistant", "content": r.message.content or "",
                             "tool_calls": [{"function": {"name": k, "arguments": a}} for k, a in llamadas]})
                msgs += [correr(k, a) for k, a in llamadas]
                msgs[0] = {"role": "system", "content": system_para(usadas)}
                continue
            texto = _limpia(r.message.content)
            if texto or ultima:
                break
    except Exception as e:  # Ollama apagado o sin el modelo
        modo = "plantilla"
        texto = (f"_(Ollama no respondio: {type(e).__name__}. Respuesta armada sin LLM; "
                 f"corre `ollama serve` y `ollama pull {modelo}`.)_\n\n") + plantilla(usadas)
    return {"respuesta": texto, "herramientas": usadas, "latencia_s": round(time.time() - t0, 1),
            "rondas": rondas, "modo": modo, "modelo": modelo}


def _pesos(v) -> str:
    return f"${v:,.0f}" if isinstance(v, (int, float)) else str(v)


def plantilla(usadas: list[dict]) -> str:
    """Respuesta sin LLM con los resultados de las herramientas (respaldo)."""
    partes, fuentes = [], []
    for u in usadas:
        r = u["resultado"]
        fuentes += r.get("fuentes", []) if isinstance(r, dict) else []
        if u["nombre"] == "recomendar_zonas":
            if not r.get("encontrado"):
                partes.append(r.get("motivo", "NO ENCONTRADO"))
                continue
            partes.append(f"**Top {len(r['zonas'])} para {r['giro']}**")
            for i, z in enumerate(r["zonas"], 1):
                partes.append(f"{i}. **{z['colonia']}**, {z['municipio']} (AGEB {z['ageb']}): score {z['score']}/100. "
                              f"Prob. de apertura {z['prob_apertura_pct']} %, gasto potencial {_pesos(z['gasto_potencial_trim_mxn'])} por trimestre, "
                              f"{z['competidores_ponderados']} competidores ponderados (captura {z['captura_huff_pct']} %), NSE estimado {z['nse_estimado']}.")
            partes.append("**Riesgos:** " + "; ".join(r.get("avisos", []) + [r.get("como_leer_score", "")]))
        elif u["nombre"] == "contexto_macro":
            for k, v in r["indicadores"].items():
                partes.append(f"- {k}: {v['valor']} {v.get('unidad') or ''} ({v.get('fecha') or ''}, serie {v.get('id_serie') or '-'})")
        elif u["nombre"] == "sugerir_giros" and r.get("encontrado"):
            partes.append("**Giros que conviene considerar** (" + r.get("como_leer", "") + "):")
            partes += [f"- {g['giro']}: viabilidad {g['viabilidad_pct']} %, prob. de apertura {g['prob_apertura_pct']} %, "
                       f"prob. de seguir abierto {g['prob_sigue_abierto_pct']} %" for g in r["giros"]]
    fu = list(dict.fromkeys(fuentes))
    return "\n".join(partes) + ("\n\n**Fuentes:** " + "; ".join(fu) if fu else "")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "quiero poner una heladeria"
    out = responder(q)
    print(out["respuesta"])
    print(f"\n[{out['modo']}, {out['rondas']} rondas, {out['latencia_s']} s, herramientas: "
          + ", ".join(u["nombre"] for u in out["herramientas"]) + "]")
