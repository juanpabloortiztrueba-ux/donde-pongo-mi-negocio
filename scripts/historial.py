"""Muestra las ultimas preguntas que llegaron al tablero (data/historial/preguntas.jsonl).

    uv run python scripts/historial.py            # las ultimas 20
    uv run python scripts/historial.py -n 50      # las ultimas 50
    uv run python scripts/historial.py --todas    # todas
    make historial                                # igual que la primera; make historial ARGS="--todas"

Cada pregunta sale con fecha, modo (rapido, llm o plantilla), latencia, la pregunta y las primeras lineas de la respuesta.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import historial  # noqa: E402


def primeras_lineas(texto: str | None, n: int = 3, ancho: int = 110) -> list[str]:
    """Hasta `n` lineas con texto de la respuesta, cada una recortada a `ancho` caracteres."""
    out = []
    for ln in (texto or "").splitlines():
        ln = ln.strip()
        if ln:
            out.append(ln if len(ln) <= ancho else ln[: ancho - 1].rstrip() + "…")
        if len(out) >= n:
            break
    return out


def formatear(fila: dict) -> str:
    """Un bloque legible por pregunta."""
    fecha = str(fila.get("fecha") or "?")[:19].replace("T", " ")
    lat = fila.get("latencia_s")
    etiquetas = [fila.get("modo") or "?", f"{lat} s" if lat is not None else "sin latencia"]
    if fila.get("fuera_de_tema"):
        etiquetas.append(f"fuera de tema ({fila.get('tipo_fuera_de_tema')})")
    if fila.get("historial"):
        etiquetas.append(f"{len(fila['historial'])} mensajes de historial")
    lineas = [f"{fecha} · " + " · ".join(etiquetas), f"  Pregunta: {fila.get('pregunta')}"]
    resp = primeras_lineas(fila.get("respuesta"))
    lineas += [f"  | {x}" for x in resp] if resp else ["  | (sin respuesta)"]
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-n", type=int, default=20, help="cuantas preguntas mostrar (las ultimas; por omision 20)")
    ap.add_argument("--todas", action="store_true", help="mostrar todas")
    ap.add_argument("--carpeta", help="carpeta del registro (por omision data/historial)")
    a = ap.parse_args(argv)
    filas = historial.leer(a.carpeta)
    if not filas:
        print("Todavía no hay preguntas registradas (data/historial/preguntas.jsonl).")
        return 0
    mostrar = filas if a.todas else filas[-max(a.n, 1):]
    print(f"{len(mostrar)} de {len(filas)} preguntas (de la más vieja a la más nueva):\n")
    print("\n\n".join(formatear(f) for f in mostrar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
