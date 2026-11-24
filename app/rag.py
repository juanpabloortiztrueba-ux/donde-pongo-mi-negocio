"""Busqueda en las carpetas de informacion (RAG sin base de datos).

    from app.rag import buscar
    buscar("como se estima el nivel socioeconomico", k=5)
    -> [{archivo, seccion, texto, score, ...}, ...]

Indice: data/index/chunks.parquet (scripts/04_indexar.py). La similitud es coseno en numpy sobre embeddings
de `nomic-embed-text` (Ollama). Dos ayudas:
  * si la pregunta nombra un municipio de la ZMVM, sus fichas reciben un bono (los embeddings flojean con nombres propios);
  * si Ollama no responde, cae a una busqueda por palabras (modo 'lexico') y lo avisa en el resultado.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
INDEX = RAIZ / "data" / "index" / "chunks.parquet"
MODELO = "nomic-embed-text"
OLLAMA = "http://localhost:11434"
PREFIJO_CONSULTA = "search_query: "
PENALIZA_FICHAS = 0.04  # sin municipio mencionado, las fichas compiten con una pequena desventaja
BONO_MUNICIPIO = 0.12  # se suma al coseno de los trozos de la ficha del municipio mencionado

# alias comunes que no salen del nombre oficial
ALIAS = {"gam": "09005", "neza": "15058", "valle de chalco": "15122", "chalco de diaz covarrubias": "15025",
         "ciudad nezahualcoyotl": "15058", "cuajimalpa": "09004", "tlalnepantla": "15104", "ecatepec": "15033"}


def _norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


@lru_cache(maxsize=1)
def _cargar():
    if not INDEX.exists():
        raise FileNotFoundError(f"No existe {INDEX}. Corre `uv run python scripts/04_indexar.py` (o `make indexar`).")
    df = pd.read_parquet(INDEX).reset_index(drop=True)
    m = np.vstack(df["embedding"].to_numpy()).astype(np.float32)
    m /= np.linalg.norm(m, axis=1, keepdims=True) + 1e-12
    texto_norm = [_norm(t) for t in df["texto"]]
    return df.drop(columns=["embedding"]), m, texto_norm


@lru_cache(maxsize=1)
def _municipios() -> dict[str, str]:
    """frase normalizada -> nombre oficial del municipio, desde zmvm_municipios.csv."""
    mun = pd.read_csv(RAIZ / "data" / "processed" / "zmvm_municipios.csv", dtype=str)
    frases: dict[str, set] = {}
    for cve, nom in zip(mun["cvegeo_mun"], mun["nom_mun"]):
        n = _norm(nom)
        frases.setdefault(n, set()).add(nom)
        if " de " in n:
            primera = n.split(" de ")[0]
            if len(primera) >= 7:  # 'Naucalpan de Juarez' -> 'naucalpan'; evita 'san', 'villa'...
                frases.setdefault(primera, set()).add(nom)
    # frases que apuntan a un solo municipio
    out = {f: next(iter(v)) for f, v in frases.items() if len(v) == 1}
    por_cve = dict(zip(mun["cvegeo_mun"], mun["nom_mun"]))
    for a, cve in ALIAS.items():
        if cve and cve in por_cve:
            out[a] = por_cve[cve]
    return out


def municipios_en(pregunta: str) -> list[str]:
    """Nombres oficiales de los municipios que menciona la pregunta (palabras completas)."""
    q = f" {_norm(pregunta)} "
    hallados = []
    # las frases mas largas primero; al encontrar una se "consume" su texto para que
    # 'Valle de Chalco' no cuente tambien como 'Chalco' ni 'Cuautitlan Izcalli' como 'Cuautitlan'
    for f in sorted(_municipios(), key=len, reverse=True):
        if f" {f} " in q:
            nom = _municipios()[f]
            if nom not in hallados:
                hallados.append(nom)
            q = q.replace(f" {f} ", " " * (len(f) + 2))
    return hallados


CIUDADES_FUERA = ["monterrey", "guadalajara", "puebla", "toluca", "queretaro", "cuernavaca", "pachuca", "tijuana", "cancun",
                  "merida", "san luis potosi", "oaxaca", "veracruz", "chihuahua", "ciudad juarez", "saltillo", "aguascalientes",
                  "morelia", "tlaxcala", "acapulco", "culiacan", "hermosillo", "mexicali", "villahermosa", "tampico", "torreon",
                  "durango", "zacatecas", "colima", "leon guanajuato", "estados unidos", "madrid", "bogota", "buenos aires"]


def ciudades_fuera(pregunta: str) -> list[str]:
    """Ciudades conocidas que NO estan en la ZMVM y que menciona la pregunta (para decir «fuera de alcance»)."""
    q = f" {_norm(pregunta)} "
    return [c for c in CIUDADES_FUERA if f" {c} " in q]


def embebe_consulta(pregunta: str) -> np.ndarray:
    r = requests.post(f"{OLLAMA}/api/embed", json={"model": MODELO, "input": [PREFIJO_CONSULTA + pregunta], "keep_alive": "5m"}, timeout=60)
    r.raise_for_status()
    v = np.asarray(r.json()["embeddings"][0], dtype=np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def _lexico(pregunta: str, texto_norm: list[str]) -> np.ndarray:
    """Puntaje 0-1 por traslape de palabras (respaldo cuando Ollama no responde)."""
    toks = {t for t in _norm(pregunta).split() if len(t) >= 4}
    if not toks:
        return np.zeros(len(texto_norm), dtype=np.float32)
    return np.array([sum(t in tx for t in toks) / len(toks) for tx in texto_norm], dtype=np.float32)


def buscar(pregunta: str, k: int = 5, archivo: str | None = None) -> list[dict]:
    """Los k trozos mas parecidos a la pregunta.

    archivo: prefijo de ruta para limitar la busqueda (p. ej. '03_municipios/' o '01_metodologia/').
    Cada resultado: archivo, seccion, texto, score (coseno + bono), score_coseno, municipio, modo ('vectorial' o 'lexico').
    """
    df, m, texto_norm = _cargar()
    modo = "vectorial"
    try:
        cos = m @ embebe_consulta(pregunta)
    except Exception:
        cos = _lexico(pregunta, texto_norm)
        modo = "lexico"
    score = cos.copy()
    muns = municipios_en(pregunta)
    if muns:
        score += np.where(df["municipio"].isin(muns).to_numpy(), BONO_MUNICIPIO, 0.0)
    if ciudades_fuera(pregunta):  # trae el documento de alcance al frente
        score += np.where(df["archivo"].eq("00_alcance.md").to_numpy(), BONO_MUNICIPIO, 0.0)
    if archivo:
        score = np.where(df["archivo"].str.startswith(archivo).to_numpy(), score, -np.inf)
    limita = not muns and not archivo
    if limita:
        # sin municipio en la pregunta las 76 fichas se parecen entre si y tapan lo demas:
        # pequena penalizacion y a lo mas 2 trozos de fichas en el resultado
        score = score - np.where(df["municipio"].ne("").to_numpy(), PENALIZA_FICHAS, 0.0)
    orden = np.argsort(-score)
    top, n_fichas = [], 0
    for i in orden:
        if not np.isfinite(score[i]) or len(top) >= k:
            break
        if limita and df.at[i, "municipio"]:
            if n_fichas >= 2:
                continue
            n_fichas += 1
        top.append(i)
    return [dict(archivo=df.at[i, "archivo"], seccion=df.at[i, "seccion"], texto=df.at[i, "texto"],
                 score=float(score[i]), score_coseno=float(cos[i]), municipio=df.at[i, "municipio"], modo=modo)
            for i in top]


def lineas_ficha(municipio: str) -> list[str]:
    """Lineas (viñetas) de la ficha del municipio, sin embeddings ni Ollama (lectura directa del indice).
    Cada linea es una viñeta de la ficha, sin el guion inicial."""
    df, _, _ = _cargar()
    x = df[(df["municipio"] == municipio) & df["archivo"].str.startswith("03_municipios/")]
    out = []
    for t in x["texto"]:
        out += [ln.lstrip("- ").strip() for ln in t.splitlines() if ln.startswith("- ")]
    return out


def estado() -> dict:
    """Resumen del indice (para diagnosticar desde la UI o el agente)."""
    df, m, _ = _cargar()
    return {"trozos": len(df), "archivos": int(df["archivo"].nunique()), "dim": int(m.shape[1])}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "como se estima el nivel socioeconomico"
    for r in buscar(q):
        print(f"[{r['score']:.3f}] {r['archivo']} > {r['seccion']} ({r['modo']})\n{r['texto'][:300]}\n")
