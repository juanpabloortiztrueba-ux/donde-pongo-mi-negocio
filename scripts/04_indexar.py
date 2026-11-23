"""Etapa RAG F: parte las carpetas en trozos y los indexa con embeddings de Ollama.

Pasos:
  1. (salvo --no-generar) corre scripts/04a_carpetas.py para regenerar lo generado con codigo.
  2. Lee todos los .md de carpetas/, los parte por seccion (<= ~1500 caracteres, tablas con su encabezado).
  3. Embeddings con `nomic-embed-text` via Ollama (/api/embed, en lotes). Reusa los de trozos que no cambiaron.
  4. Guarda data/index/chunks.parquet (chunk_id, archivo, seccion, texto, embedding + municipio, texto_sha1)
     y data/index/meta.json.

Uso: uv run python scripts/04_indexar.py [--no-generar] [--rehacer] [--lote 16]
Necesita el servidor de Ollama corriendo (`ollama serve`) y `ollama pull nomic-embed-text`.
Para correrlo largo: nohup uv run python scripts/04_indexar.py > /tmp/indexar.log 2>&1 &
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
CARP = RAIZ / "carpetas"
INDEX = RAIZ / "data" / "index"
MODELO = "nomic-embed-text"
OLLAMA = "http://localhost:11434"
PREFIJO_DOC = "search_document: "  # nomic-embed-text pide prefijos distintos para documento y consulta
MAX_CHARS = 1500
MIN_CHARS = 450  # trozos mas chicos se unen con el siguiente de la misma seccion mayor


# ---------- partir en trozos ----------
def unidades(texto: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Devuelve (titulo del documento, [(h2, etiqueta de seccion, cuerpo)]) cortando en ##, ### (no dentro de ```)."""
    titulo, h2, h3 = "", "", ""
    cur: list[str] = []
    out: list[tuple[str, str, str]] = []
    en_codigo = False

    def cierra():
        cuerpo = "\n".join(cur).strip()
        if cuerpo:
            et = h2 if not h3 else f"{h2} > {h3}"
            out.append((h2, et or "(inicio)", cuerpo))
        cur.clear()

    for ln in texto.splitlines():
        if ln.strip().startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else re.match(r"^(#{1,3}) (.+)$", ln)
        if m:
            n, t = len(m.group(1)), m.group(2).strip()
            if n == 1 and not titulo:
                titulo = t
                continue
            cierra()
            if n <= 2:
                h2, h3 = t, ""
            else:
                h3 = t
            continue
        cur.append(ln)
    cierra()
    return titulo, out


def parte_largo(cuerpo: str, max_chars: int) -> list[str]:
    """Parte un cuerpo largo por lineas; si es tabla, repite el encabezado de la tabla en cada trozo."""
    lineas = cuerpo.splitlines()
    cab: list[str] = []
    for i, ln in enumerate(lineas[:-1]):  # encabezado de tabla: linea con | seguida de |---|
        if ln.startswith("|") and re.match(r"^\|[\s:|-]+\|$", lineas[i + 1]):
            cab = [ln, lineas[i + 1]]
            break
    trozos, act = [], []
    n = 0
    for ln in lineas:
        if n + len(ln) + 1 > max_chars and act:
            trozos.append("\n".join(act))
            act = list(cab) if cab and ln.startswith("|") and ln not in cab else []
            n = sum(len(x) + 1 for x in act)
        act.append(ln)
        n += len(ln) + 1
    if act:
        trozos.append("\n".join(act))
    return [t for t in trozos if t.strip() and t.strip() not in ("|", "")]


def trocea(ruta: Path) -> list[dict]:
    texto = ruta.read_text(encoding="utf-8")
    titulo, uni = unidades(texto)
    titulo = titulo or ruta.stem
    # une unidades chicas consecutivas de la misma seccion mayor (h2)
    piezas: list[list] = []  # [h2, [etiquetas], cuerpo]
    for h2, et, cuerpo in uni:
        if piezas and piezas[-1][0] == h2 and len(piezas[-1][2]) < MIN_CHARS and len(piezas[-1][2]) + len(cuerpo) + 2 <= MAX_CHARS:
            piezas[-1][1].append(et)
            piezas[-1][2] += f"\n\n{'#' * 3} {et.split(' > ')[-1]}\n\n{cuerpo}"
        else:
            piezas.append([h2, [et], cuerpo])
    res = []
    for h2, ets, cuerpo in piezas:
        seccion = ets[0]
        for sub in (parte_largo(cuerpo, MAX_CHARS) if len(cuerpo) > MAX_CHARS else [cuerpo]):
            res.append({"seccion": seccion, "texto": f"{titulo}\n[{seccion}]\n\n{sub.strip()}"})
    return res


# ---------- embeddings ----------
def ollama_vivo() -> bool:
    try:
        r = requests.get(f"{OLLAMA}/api/tags", timeout=5)
        return any(m["name"].split(":")[0] == MODELO for m in r.json().get("models", []))
    except Exception:
        return False


def embebe(textos: list[str], keep_alive: str = "5m") -> list[list[float]]:
    for intento in range(4):
        try:
            r = requests.post(f"{OLLAMA}/api/embed", json={"model": MODELO, "input": textos, "keep_alive": keep_alive}, timeout=180)
            r.raise_for_status()
            return r.json()["embeddings"]
        except Exception as e:
            if intento == 3:
                raise
            print(f"  reintento {intento + 1} ({e.__class__.__name__})", flush=True)
            time.sleep(3 * (intento + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-generar", action="store_true", help="no correr 04a_carpetas.py antes")
    ap.add_argument("--rehacer", action="store_true", help="ignorar embeddings previos")
    ap.add_argument("--lote", type=int, default=16)
    a = ap.parse_args()

    if not a.no_generar:
        print("generando carpetas...", flush=True)
        subprocess.run([sys.executable, str(RAIZ / "scripts" / "04a_carpetas.py")], check=True, cwd=RAIZ)

    if not ollama_vivo():
        sys.exit(f"Ollama no responde en {OLLAMA} o falta el modelo. Corre `ollama serve` y `ollama pull {MODELO}`.")

    mun = pd.read_csv(RAIZ / "data" / "processed" / "zmvm_municipios.csv", dtype=str).set_index("cvegeo_mun")["nom_mun"].to_dict()
    filas = []
    for ruta in sorted(CARP.rglob("*.md")):
        rel = ruta.relative_to(CARP).as_posix()
        m = re.match(r"^(\d{5})_", ruta.name)
        for t in trocea(ruta):
            filas.append({"archivo": rel, "seccion": t["seccion"], "texto": t["texto"],
                          "municipio": mun.get(m.group(1), "") if m and "03_municipios" in rel else ""})
    df = pd.DataFrame(filas)
    df["texto_sha1"] = [hashlib.sha1(t.encode()).hexdigest() for t in df["texto"]]
    df["chunk_id"] = [f"{i:05d}" for i in range(len(df))]
    print(f"{len(df)} trozos en {df['archivo'].nunique()} archivos; largo medio {df['texto'].str.len().mean():.0f} caracteres, maximo {df['texto'].str.len().max()}", flush=True)

    # reutiliza embeddings de trozos iguales
    previo = {}
    ruta_idx = INDEX / "chunks.parquet"
    if ruta_idx.exists() and not a.rehacer:
        p = pd.read_parquet(ruta_idx)
        if "texto_sha1" in p.columns:
            previo = dict(zip(p["texto_sha1"], p["embedding"]))
    emb: list = [previo.get(h) for h in df["texto_sha1"]]
    pend = [i for i, e in enumerate(emb) if e is None]
    print(f"{len(df) - len(pend)} reutilizados, {len(pend)} por embeber", flush=True)

    t0 = time.time()
    for j in range(0, len(pend), a.lote):
        idx = pend[j:j + a.lote]
        ultimo = j + a.lote >= len(pend)
        vecs = embebe([PREFIJO_DOC + df.at[i, "texto"] for i in idx], keep_alive="0" if ultimo else "5m")  # al final descarga el modelo
        for i, v in zip(idx, vecs):
            emb[i] = np.asarray(v, dtype=np.float32)
        print(f"  {min(j + a.lote, len(pend))}/{len(pend)}  ({time.time() - t0:.0f} s)", flush=True)
    df["embedding"] = emb

    INDEX.mkdir(parents=True, exist_ok=True)
    df = df[["chunk_id", "archivo", "seccion", "texto", "embedding", "municipio", "texto_sha1"]]
    df["embedding"] = df["embedding"].map(lambda v: np.asarray(v, dtype=np.float32).tolist())
    df.to_parquet(ruta_idx, index=False)
    dim = len(df["embedding"].iloc[0])
    json.dump({"modelo_embeddings": MODELO, "prefijo_doc": PREFIJO_DOC, "prefijo_consulta": "search_query: ", "dim": dim,
               "n_trozos": len(df), "n_archivos": int(df["archivo"].nunique()), "max_chars": MAX_CHARS,
               "creado": datetime.now().isoformat(timespec="seconds")},
              open(INDEX / "meta.json", "w", encoding="utf-8"), indent=1)
    print(f"listo: {ruta_idx} ({ruta_idx.stat().st_size / 1e6:.1f} MB, dim {dim})")


if __name__ == "__main__":
    main()
