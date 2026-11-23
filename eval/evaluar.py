"""Evaluacion automatica del agente con las 20 preguntas de eval/preguntas.yaml.

    uv run python eval/evaluar.py              # corre el agente (Ollama) y califica; reanuda si se corto
    uv run python eval/evaluar.py --rehacer    # borra lo parcial y empieza de cero
    uv run python eval/evaluar.py --solo-checks  # vuelve a calificar las respuestas guardadas, sin LLM

Salidas: reports/evaluacion.md, reports/evaluacion.json y reports/evaluacion_parcial.jsonl (una linea por pregunta).
Checks (contrato): AGEB y colonias del top existen en agebs_features; cifras citadas = cifras de las herramientas
(tolerancia de redondeo); hay fuentes; latencia; sin tokens. Pasa si >= 18/20 y la trampa pasa.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import yaml  # noqa: E402

from app import herramientas as H  # noqa: E402

REPORTS = RAIZ / "reports"
PARCIAL = REPORTS / "evaluacion_parcial.jsonl"
LAT_MAX_S = 180          # una respuesta que tarda mas de esto falla el check de latencia
LAT_OBJETIVO_MED_S = 90  # objetivo de la mediana (se reporta)
MIN_CIFRAS_OK = 0.90     # fraccion minima de cifras citadas que deben salir de las herramientas
MAX_CIFRAS_MAL = 1       # y a lo mas 1 cifra sin origen (margen para errores del extractor de numeros)

AGEB_RE = re.compile(r"\b\d{9}[0-9A-Z]{4}\b")
FECHA_RE = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b|\b\d{1,2}/\d{4}\b")
NUM_RE = re.compile(r"(?<![\w.,/])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\w])\s*(%|millones|millon|mdp|mil\b|m\b)?",
                    re.I)
FUENTES_CLAVE = ["inegi", "denue", "censo", "enigh", "conapo", "banxico", "banco de mexico", "carpetas/", "modelo de aperturas"]
RELATIVO_RE = re.compile(r"relativ|no compara|dentro (?:de cada|de este|del|de su) giro|percentil", re.I)
VIABILIDAD_RE = re.compile(r"viabilidad|giros que conviene", re.I)
BAJA_RE = re.compile(r"\bbaj[ao]s?\b", re.I)
FUERA_RE = re.compile(r"fuera (?:de|del)|no (?:cubre|esta|está|incluye|tengo datos)|solo (?:cubre|abarca|trabaja)|únicamente|unicamente|alcance",
                      re.I)


# ---------------------------------------------------------------- utilidades
def memoria() -> dict:
    """Swap usado (MB) y % de memoria libre del sistema (macOS)."""
    out = {}
    try:
        s = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True, timeout=5).stdout
        m = re.search(r"used = ([\d.]+)M", s)
        out["swap_mb"] = float(m.group(1)) if m else None
        p = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=10).stdout
        m = re.search(r"free percentage: (\d+)%", p)
        out["mem_libre_pct"] = int(m.group(1)) if m else None
    except Exception:
        pass
    return out


def tokens_env() -> list[str]:
    """Valores de .env (nunca se imprimen; solo se buscan)."""
    try:
        from dotenv import dotenv_values
        return [v for v in dotenv_values(RAIZ / ".env").values() if v and len(v) >= 8]
    except Exception:
        return []


def numeros_de(obj, acc: set | None = None) -> set:
    """Todos los numeros que regreso una herramienta (valores y numeros dentro de textos)."""
    acc = set() if acc is None else acc
    if isinstance(obj, bool) or obj is None:
        return acc
    if isinstance(obj, (int, float)):
        acc.add(float(obj))
    elif isinstance(obj, str):
        s = FECHA_RE.sub(" ", obj)
        for m in NUM_RE.finditer(s):
            acc.add(float(m.group(1).replace(",", "")))
    elif isinstance(obj, dict):
        for v in obj.values():
            numeros_de(v, acc)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            numeros_de(v, acc)
    return acc


def cifras_citadas(texto: str, pregunta: str) -> list[dict]:
    """Cifras de la respuesta que hay que verificar (sin AGEB, fechas, enumeraciones ni numeros de la pregunta)."""
    s = AGEB_RE.sub(" ", texto)
    s = FECHA_RE.sub(" ", s)
    s = re.sub(r"/\s*100\b", " ", s)           # 'score 96.5/100'
    s = re.sub(r"(?m)^\s*\d+[.)]\s", " ", s)    # '1. ' de listas
    s = re.sub(r"\b(?:top|primer[oa]s?)\s+\d+\b", " ", s, flags=re.I)
    en_pregunta = {float(m.group(1).replace(",", "")) for m in NUM_RE.finditer(pregunta)}
    out = []
    for m in NUM_RE.finditer(s):
        txt = m.group(1)
        v = float(txt.replace(",", ""))
        dec = len(txt.split(".")[1]) if "." in txt else 0
        if dec == 0 and (v <= 10 or 1990 <= v <= 2030):   # enumeraciones, deciles y anios no se verifican
            continue
        if v in en_pregunta:
            continue
        u = (m.group(2) or "").lower()
        mult = 1e6 if u in ("millones", "millon", "mdp", "m") else 1e3 if u == "mil" else 1.0
        out.append({"texto": m.group(0).strip(), "valor": v * mult, "tol": 0.5 * 10 ** (-dec) * mult,
                    "crudo": v, "tol_crudo": 0.5 * 10 ** (-dec)})
    return out


def coincide(c: dict, nums: set) -> bool:
    """Coincide si la cifra (con su unidad aplicada, o tal cual: «5362 millones de USD» cuando la herramienta
    ya da millones) esta a medio digito de un numero de las herramientas (o de una fraccion escrita como %)."""
    pares = [(c["valor"], c["tol"]), (c.get("crudo", c["valor"]), c.get("tol_crudo", c["tol"]))]
    for n in nums:
        for cand in (n, n * 100):
            if any(abs(v - cand) <= tol + 1e-9 for v, tol in pares):
                return True
    return False


# ---------------------------------------------------------------- checks
def _giro_mencionado(clave: str, low: str) -> bool:
    """El giro aparece en la respuesta (normalizada) por su clave o por alguno de sus sinonimos."""
    from app import motor

    nombres = [clave.replace("_", " ")] + list(motor.giros().get(clave, {}).get("nombres", []))
    return any(H._singular(H.norm(n)) in H._singular(low) for n in nombres if n)


def calificar(q: dict, r: dict, feats, toks: list[str]) -> dict:
    texto = r["respuesta"] or ""
    usadas = r["herramientas"]
    tool_txt = json.dumps([u["resultado"] for u in usadas], ensure_ascii=False)
    checks = {}

    # 1) tokens
    checks["sin_tokens"] = not any(t in texto or t in tool_txt for t in toks)

    # 2) fuentes
    low = H.norm(texto)
    checks["fuentes"] = ("fuente" in low) and any(H.norm(k) in low or k in texto.lower() for k in FUENTES_CLAVE)

    # 3) latencia
    checks["latencia"] = r["latencia_s"] <= LAT_MAX_S

    # 4) AGEB y colonias
    agebs = list(dict.fromkeys(AGEB_RE.findall(texto)))
    ageb_tools = set(AGEB_RE.findall(tool_txt))
    det = {"agebs_citadas": agebs}
    existen = all(a in feats.index for a in agebs)
    de_herr = all(a in ageb_tools for a in agebs)
    colonia_ok = all(H.norm(feats.at[a, "nom_colonia"]) in low for a in agebs if a in feats.index)
    det.update(agebs_existen=existen, agebs_de_herramientas=de_herr, colonias_coinciden=colonia_ok)
    tipo = q["tipo"]
    if tipo in ("giro", "sugerir"):
        zonas = [u["resultado"] for u in usadas if u["nombre"] == "recomendar_zonas" and u["resultado"].get("encontrado")]
        esperadas = min(5, max((len(z["zonas"]) for z in zonas), default=5))
        checks["top_agebs"] = existen and de_herr and colonia_ok and len(agebs) >= esperadas
        det["agebs_esperadas"] = esperadas
        if q.get("municipio"):
            checks["municipio"] = bool(agebs) and all(a[:5] == q["municipio"] for a in agebs)
    elif tipo == "trampa":
        checks["trampa_fuera_de_alcance"] = (not agebs) and bool(FUERA_RE.search(texto))
    else:
        checks["agebs_validas"] = existen and de_herr

    # 5) herramienta correcta
    if q.get("giro"):
        checks["giro"] = any(u["nombre"] == "recomendar_zonas" and u["resultado"].get("giro") == q["giro"] for u in usadas)
    if q.get("nse"):
        checks["nse"] = any(u["nombre"] == "recomendar_zonas" and (u["resultado"].get("filtros") or {}).get("nse") == q["nse"]
                            for u in usadas)
    if tipo == "macro":
        macro = [u["resultado"] for u in usadas if u["nombre"] == "contexto_macro"]
        checks["macro_usada"] = bool(macro)
        # que la respuesta si hable de macro: al menos 2 cifras que salen de contexto_macro
        nm = numeros_de(macro)
        det["cifras_macro"] = sum(coincide(c, nm) for c in cifras_citadas(texto, q["pregunta"]))
        checks["macro_cifras"] = det["cifras_macro"] >= 2

    # 5b) honestidad del score: es relativo dentro del giro (no compara giros ni dice viabilidad)
    rz = [u["resultado"] for u in usadas if u["nombre"] == "recomendar_zonas" and u["resultado"].get("encontrado")]
    if any(z.get("aviso_prob_baja") for z in rz):  # prob. de apertura baja en todo el top: debe decirlo
        checks["aviso_prob_baja"] = bool(RELATIVO_RE.search(texto)) and bool(BAJA_RE.search(texto))
    sg = [u["resultado"] for u in usadas if u["nombre"] == "sugerir_giros" and u["resultado"].get("encontrado")]
    if not sg:  # «viabilidad» o una lista de giros sin haber llamado sugerir_giros = cifras inventadas
        checks["sin_giros_inventados"] = not VIABILIDAD_RE.search(texto)
    if tipo == "sugerir":
        checks["sugerir_usada"] = bool(sg)
        if sg:  # que presente las alternativas que regreso la herramienta, no solo la primera
            claves = [g["giro"] for g in sg[0]["giros"]]
            nombrados = [c for c in claves if _giro_mencionado(c, low)]
            det["giros_sugeridos"], det["giros_mencionados"] = claves, nombrados
            checks["alternativas"] = len(nombrados) >= min(3, len(claves))
            checks["score_relativo"] = bool(RELATIVO_RE.search(texto))

    # 6) cifras
    nums = numeros_de([u["resultado"] for u in usadas])
    cit = cifras_citadas(texto, q["pregunta"])
    malas = [c["texto"] for c in cit if not coincide(c, nums)]
    frac = 1.0 if not cit else 1 - len(malas) / len(cit)
    det.update(cifras_citadas=len(cit), cifras_no_encontradas=malas, frac_cifras_ok=round(frac, 3))
    checks["cifras"] = frac >= MIN_CIFRAS_OK and len(malas) <= MAX_CIFRAS_MAL and (tipo == "trampa" or len(cit) > 0)

    return {"checks": checks, "detalle": det, "pasa": all(checks.values())}


# ---------------------------------------------------------------- correr
def cargar_parcial() -> dict:
    if not PARCIAL.exists():
        return {}
    out = {}
    for line in PARCIAL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            out[d["id"]] = d
    return out


def correr(preguntas: list[dict]) -> None:
    from app import agente

    hechas = cargar_parcial()
    for q in preguntas:
        if q["id"] in hechas:
            continue
        m0 = memoria()
        r = agente.responder(q["pregunta"])
        m1 = memoria()
        fila = {"id": q["id"], "pregunta": q["pregunta"], "respuesta": r["respuesta"], "modo": r["modo"],
                "rondas": r["rondas"], "latencia_s": r["latencia_s"],
                "herramientas": [{"nombre": u["nombre"], "args": u["args"], "resultado": u["resultado"]} for u in r["herramientas"]],
                "mem_antes": m0, "mem_despues": m1}
        with PARCIAL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        print(f"[{q['id']:>2}] {r['latencia_s']:>6.1f} s  {r['modo']}  swap {m1.get('swap_mb')} MB  "
              f"libre {m1.get('mem_libre_pct')} %  {q['pregunta'][:50]}", flush=True)


def reporte(preguntas: list[dict]) -> dict:
    from app import motor

    feats = motor.cargar_features()
    toks = tokens_env()
    hechas = cargar_parcial()
    filas = []
    for q in preguntas:
        if q["id"] not in hechas:
            continue
        r = hechas[q["id"]]
        c = calificar(q, r, feats, toks)
        filas.append({**{k: r[k] for k in ("id", "pregunta", "respuesta", "modo", "rondas", "latencia_s", "mem_antes", "mem_despues")},
                      "tipo": q["tipo"], "herramientas": [{"nombre": u["nombre"], "args": u["args"]} for u in r["herramientas"]],
                      **c})
    lat = [f["latencia_s"] for f in filas]
    swaps = [f["mem_despues"].get("swap_mb") for f in filas if f["mem_despues"].get("swap_mb") is not None]
    libres = [f["mem_despues"].get("mem_libre_pct") for f in filas if f["mem_despues"].get("mem_libre_pct") is not None]
    trampa = [f for f in filas if f["tipo"] == "trampa"]
    n_ok = sum(f["pasa"] for f in filas)
    res = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "modelo": "qwen3:8b (Ollama, think=False)", "preguntas": len(filas),
           "pasan": n_ok, "trampa_pasa": bool(trampa) and trampa[0]["pasa"],
           "aprobado": len(filas) == 20 and n_ok >= 18 and bool(trampa) and trampa[0]["pasa"],
           "latencia_mediana_s": round(statistics.median(lat), 1) if lat else None,
           "latencia_p90_s": round(sorted(lat)[int(0.9 * (len(lat) - 1))], 1) if lat else None,
           "latencia_max_s": max(lat) if lat else None,
           "mediana_bajo_objetivo": bool(lat) and statistics.median(lat) <= LAT_OBJETIVO_MED_S,
           "swap_mb_inicio": filas[0]["mem_antes"].get("swap_mb") if filas else None,
           "swap_mb_max": max(swaps) if swaps else None, "swap_mb_fin": swaps[-1] if swaps else None,
           "mem_libre_pct_min": min(libres) if libres else None,
           "criterios": {"latencia_max_s": LAT_MAX_S, "mediana_objetivo_s": LAT_OBJETIVO_MED_S,
                         "frac_cifras_min": MIN_CIFRAS_OK, "max_cifras_sin_origen": MAX_CIFRAS_MAL},
           "filas": filas}
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "evaluacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (REPORTS / "evaluacion.md").write_text(md(res), encoding="utf-8")
    return res


def md(res: dict) -> str:
    L = [f"# Evaluación del agente ({res['fecha']})", "",
         f"Modelo: {res['modelo']}. Preguntas: {res['preguntas']} de 20 (`eval/preguntas.yaml`). Script: `eval/evaluar.py`.", "",
         f"**Resultado: {res['pasan']}/{res['preguntas']} pasan; trampa {'pasa' if res['trampa_pasa'] else 'NO pasa'} → "
         f"{'APROBADO' if res['aprobado'] else 'NO APROBADO'}** (criterio del contrato: ≥ 18/20 y la trampa pasa).", "",
         f"- Latencia: mediana {res['latencia_mediana_s']} s, p90 {res['latencia_p90_s']} s, máxima {res['latencia_max_s']} s "
         f"(objetivo de mediana ≤ {res['criterios']['mediana_objetivo_s']} s: {'sí' if res['mediana_bajo_objetivo'] else 'NO'}; "
         f"una respuesta de más de {res['criterios']['latencia_max_s']} s falla).",
         f"- Memoria (MacBook Air M4, 16 GB): swap {res['swap_mb_inicio']} MB al inicio, máximo {res['swap_mb_max']} MB, "
         f"{res['swap_mb_fin']} MB al final; memoria libre mínima {res['mem_libre_pct_min']} % (`memory_pressure`).", "",
         "## Checks", "",
         "- `sin_tokens`: ningún valor de `.env` aparece en la respuesta ni en lo que regresaron las herramientas.",
         "- `fuentes`: la respuesta tiene sección de fuentes y nombra al menos una fuente real (INEGI, DENUE, ENIGH, CONAPO, Banxico, carpetas...).",
         f"- `latencia`: ≤ {LAT_MAX_S} s.",
         "- `top_agebs`: cada AGEB citada existe en `agebs_features`, salió de una herramienta, su colonia (de `agebs_features`) "
         "aparece en la respuesta y hay al menos 5 (o las que regresó la herramienta).",
         "- `municipio`, `giro`, `nse`, `macro_usada`: se usó la herramienta con el giro/filtro esperado y las AGEB son del municipio pedido.",
         "- `macro_cifras` (pregunta macro): la respuesta cita al menos 2 cifras de `contexto_macro`.",
         f"- `cifras`: a lo más {MAX_CIFRAS_MAL} cifra sin origen y al menos {int(100 * MIN_CIFRAS_OK)} % de las cifras citadas coinciden con un número de las herramientas, con tolerancia "
         "de redondeo según los decimales escritos («0.43 millones» = 430,000; una fracción de la herramienta puede citarse como %). No se verifican enteros ≤ 10 "
         "(enumeraciones, deciles), años ni fechas.",
         "- `trampa_fuera_de_alcance`: dice que está fuera de alcance y no da ninguna AGEB.",
         "- `aviso_prob_baja`: si `recomendar_zonas` avisa que la prob. de apertura es baja en todo el top, la respuesta lo dice y aclara que el score es relativo al giro.",
         "- `sin_giros_inventados`: sin `sugerir_giros`, la respuesta no habla de «viabilidad» ni lista «giros que conviene».",
         "- `sugerir_usada`, `alternativas`, `score_relativo` (preguntas sin giro): se usó `sugerir_giros`, la respuesta nombra al menos 3 de los giros que regresó y dice que el score es relativo dentro de cada giro.", "",
         "## Resultados por pregunta", "",
         "| # | Pregunta | Pasa | Latencia (s) | Herramientas | Cifras ok | Checks que fallan |", "|---|---|---|---|---|---|---|"]
    for f in res["filas"]:
        fallan = [k for k, v in f["checks"].items() if not v]
        L.append(f"| {f['id']} | {f['pregunta']} | {'sí' if f['pasa'] else 'NO'} | {f['latencia_s']} | "
                 f"{', '.join(h['nombre'] for h in f['herramientas'])} | "
                 f"{f['detalle']['cifras_citadas'] - len(f['detalle']['cifras_no_encontradas'])}/{f['detalle']['cifras_citadas']} | "
                 f"{', '.join(fallan) or '-'} |")
    L += ["", "## Respuestas completas", ""]
    for f in res["filas"]:
        L += [f"### {f['id']}. {f['pregunta']}", "",
              f"_{f['modo']}, {f['rondas']} rondas, {f['latencia_s']} s; herramientas: "
              + "; ".join(f"{h['nombre']}({json.dumps(h['args'], ensure_ascii=False)})" for h in f["herramientas"]) + "_", ""]
        if f["detalle"]["cifras_no_encontradas"]:
            L += [f"Cifras que no salen de las herramientas: {', '.join(f['detalle']['cifras_no_encontradas'])}", ""]
        L += ["> " + line for line in f["respuesta"].splitlines()] + [""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-checks", action="store_true", help="califica lo guardado sin llamar al LLM")
    ap.add_argument("--rehacer", action="store_true", help="borra lo parcial y vuelve a correr")
    ap.add_argument("--ids", help="solo estas preguntas, p. ej. 1,20")
    a = ap.parse_args()
    qs = yaml.safe_load((RAIZ / "eval" / "preguntas.yaml").read_text(encoding="utf-8"))["preguntas"]
    if a.ids:
        ids = {int(x) for x in a.ids.split(",")}
        qs_run = [q for q in qs if q["id"] in ids]
    else:
        qs_run = qs
    if a.rehacer and PARCIAL.exists():
        PARCIAL.unlink()
    if not a.solo_checks:
        correr(qs_run)
    res = reporte(qs)
    print(f"{res['pasan']}/{res['preguntas']} pasan; trampa {'ok' if res['trampa_pasa'] else 'FALLA'}; "
          f"mediana {res['latencia_mediana_s']} s; swap max {res['swap_mb_max']} MB; aprobado={res['aprobado']}")
