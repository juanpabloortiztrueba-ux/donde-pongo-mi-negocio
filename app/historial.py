"""Registro local de las preguntas que llegan por la API del tablero: `data/historial/preguntas.jsonl` (una linea por pregunta).

Cada linea: fecha (ISO, con zona horaria), pregunta, historial (lo que llego), modo (rapido | llm | plantilla), fuera_de_tema,
tipo_fuera_de_tema, herramientas ([{nombre, args}]: sin resultados), respuesta (texto) y latencia_s.

Nunca guarda tokens: todo pasa por el mismo filtro que el check `sin_tokens` del evaluador (los valores de `.env` de 8 o mas
caracteres se reemplazan por «[oculto]» antes de escribir). Si escribir falla, regresa False y no rompe la respuesta.
No registra las preguntas del evaluador (llama al agente directo) ni las de pytest: `tests/conftest.py` apaga el registro con
`DONDE_SIN_HISTORIAL=1`. La carpeta esta en `.gitignore`. Para verlo: `make historial` (scripts/historial.py).
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "data" / "historial"
ARCHIVO = "preguntas.jsonl"
OCULTO = "[oculto]"
_candado = threading.Lock()


def activo() -> bool:
    """El registro esta encendido salvo que el entorno diga lo contrario (pytest, o `DONDE_SIN_HISTORIAL=1`)."""
    return os.environ.get("DONDE_SIN_HISTORIAL", "").strip().lower() not in ("1", "true", "si", "yes")


def tokens_env() -> list[str]:
    """Valores de .env (nunca se imprimen; solo se buscan). Es el mismo filtro del check `sin_tokens` del evaluador."""
    try:
        from dotenv import dotenv_values
        return [v for v in dotenv_values(RAIZ / ".env").values() if v and len(v) >= 8]
    except Exception:
        return []


def limpiar(obj, tokens: list[str]):
    """Copia de `obj` (texto, listas, diccionarios) con cada token reemplazado por «[oculto]»."""
    if isinstance(obj, str):
        for t in tokens:
            if t in obj:
                obj = obj.replace(t, OCULTO)
        return obj
    if isinstance(obj, dict):
        return {limpiar(str(k), tokens): limpiar(v, tokens) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [limpiar(v, tokens) for v in obj]
    return obj


def registrar(pregunta: str, historial: list[dict] | None, modo: str | None, fuera_de_tema: bool, herramientas: list[dict] | None,
              respuesta: str | None, latencia_s: float | None, tipo_fuera_de_tema: str | None = None, fecha: float | None = None,
              carpeta: Path | str | None = None, tokens: list[str] | None = None) -> bool:
    """Agrega una linea al registro. True si escribio; False si el registro esta apagado o fallo (nunca lanza)."""
    try:
        if carpeta is None and not activo():
            return False
        dest = Path(carpeta) if carpeta is not None else CARPETA
        t = time.time() if fecha is None else fecha
        fila = {
            "fecha": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(t)),
            "pregunta": pregunta, "historial": historial or [], "modo": modo,
            "fuera_de_tema": bool(fuera_de_tema), "tipo_fuera_de_tema": tipo_fuera_de_tema,
            "herramientas": [{"nombre": h.get("nombre"), "args": h.get("args") or {}} for h in (herramientas or []) if isinstance(h, dict)],
            "respuesta": respuesta, "latencia_s": latencia_s,
        }
        fila = limpiar(fila, tokens_env() if tokens is None else tokens)
        linea = json.dumps(fila, ensure_ascii=False, default=str)
        with _candado:
            dest.mkdir(parents=True, exist_ok=True)
            with (dest / ARCHIVO).open("a", encoding="utf-8") as f:
                f.write(linea + "\n")
        return True
    except Exception:
        return False


def leer(carpeta: Path | str | None = None) -> list[dict]:
    """Todas las filas del registro, de la mas vieja a la mas nueva (las lineas dañadas se saltan)."""
    ruta = Path(carpeta or CARPETA) / ARCHIVO
    if not ruta.exists():
        return []
    filas = []
    for ln in ruta.read_text(encoding="utf-8").splitlines():
        try:
            filas.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return filas
