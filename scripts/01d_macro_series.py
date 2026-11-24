"""Etapa Datos D: series historicas del contexto macro (Banxico SIE + INEGI BIE), de 2015 a hoy.

Uso (desde la raiz del repo):
    uv run python scripts/01d_macro_series.py

Salida: data/processed/macro_series.parquet, en formato largo:
    serie (clave corta), fecha (date), valor, unidad, fuente, id_serie
Las series diarias (tasa objetivo, TIIE, FIX) se guardan diarias; el resto, mensuales (fecha = dia 1 del mes).
La API del tablero (app/api/contexto.py) las agrega a meses.

Reusa de scripts/01c_enigh_macro.py la carga de tokens, el limpiador de secretos y las URL de las API, y de
data/processed/macro.json los id_serie. Los tokens salen de .env y nunca se imprimen ni van a un mensaje de error.
Cada peticion lleva timeout. Idempotente: vuelve a bajar todo y reescribe el parquet (tarda ~1 min).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
DESDE = dt.date(2015, 1, 1)
TIMEOUT = 30  # segundos por peticion
REINTENTOS = 3
INEGI_API = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"  # el mismo de 01c (se verifica abajo)


def _cargar_01c():
    spec = importlib.util.spec_from_file_location("enigh_macro_01c", RAIZ / "scripts" / "01c_enigh_macro.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# (clave, origen, id por defecto, texto que debe contener el titulo, unidad, llave de macro.json con el mismo id o None)
SERIES = [
    ("tasa_objetivo", "banxico", "SF61745", "Tasa objetivo", "% anual", "tasa_objetivo"),
    ("tiie_28", "banxico", "SF43783", "TIIE a 28", "% anual", "tiie_28"),
    ("tipo_cambio_fix", "banxico", "SF43718", "FIX", "MXN por USD", "tipo_cambio_fix"),
    ("remesas", "banxico", "SE27803", "Remesas Familiares Total", "millones de USD (mensual)", "remesas"),
    ("inpc_indice", "inegi", "910392", "", "indice base 2018=100", None),
    ("inpc_general_var_anual", "inegi", "910406", "Índice general", "% variacion anual", "inpc_general_var_anual"),
    ("inpc_mercancias_var_anual", "inegi", "910408", "Mercancías", "% variacion anual", None),
    ("inpc_agropecuarios_var_anual", "inegi", "910411", "Agropecuarios", "% variacion anual", None),
    ("confianza_consumidor", "inegi", "454168", "confianza del consumidor", "puntos (indice)", "confianza_consumidor"),
    ("imcp_indice", "inegi", "740933", "", "indice de volumen 2018=100", None),
    ("consumo_privado_var_anual", "inegi", "740946", "Total", "% variacion anual (cifras originales)", "consumo_privado"),
]


def escribe_fuentes(df: pd.DataFrame, destino: Path, hoy: dt.date) -> None:
    """Reescribe la seccion 01d de data/FUENTES.md (entre marcadores, como 01a); el resto del archivo no se toca."""
    ini, fin = "<!-- 01d:inicio (generado por scripts/01d_macro_series.py; no editar a mano) -->", "<!-- 01d:fin -->"
    sha = hashlib.sha256((PROC / "macro_series.parquet").read_bytes()).hexdigest()
    filas = ["| Archivo y serie | URL | Descarga | Fecha del ultimo dato | Datos | sha256 |", "|---|---|---|---|---|---|"]
    for clave, g in df.groupby("serie", sort=False):
        i = g["id_serie"].iloc[0]
        url = (f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{i}/datos" if g["fuente"].iloc[0].startswith("Banco")
               else f"{INEGI_API}/INDICATOR/{i}/es/00/false/BIE-BISE/2.0/<token>")
        filas.append(f"| macro_series.parquet · serie {clave} (id {i}; {g['unidad'].iloc[0]}) | {url} | {hoy.isoformat()} | "
                     f"{g['fecha'].max().date().isoformat()} | {len(g):,} datos | solo la API (ver abajo) |")
    bloque = "\n".join([
        ini, "## Datos D: series historicas del contexto macro, 2015 a hoy (" + hoy.isoformat() + ")", "",
        "Banxico SIE (token `BANXICO_TOKEN` de `.env`) e INEGI BIE (token `INEGI_TOKEN`). Los tokens no se escriben aqui ni en ningun log.", "",
        *filas, "",
        "Notas:",
        f"- `data/processed/macro_series.parquet`: formato largo (`serie, fecha, valor, unidad, fuente, id_serie`), {len(df):,} filas, sha256 `{sha}`.",
        "- Tasa objetivo, TIIE a 28 dias y FIX son diarias; las demas, mensuales (fecha = dia 1 del mes). El tablero las agrega a meses (promedio; la tasa objetivo, al cierre del mes).",
        "- Los id_serie son los de `data/processed/macro.json` (etapa 01c); los de INEGI se verifican contra su descripcion en el catalogo. `inpc_mercancias` e `inpc_agropecuarios` son los proxies de alimentos de 01c.",
        fin, ""])
    t = destino.read_text(encoding="utf-8") if destino.exists() else "# Fuentes de datos\n"
    if ini in t and fin in t:
        a, b = t.index(ini), t.index(fin) + len(fin)
        t = t[:a] + bloque.rstrip("\n") + t[b:]
    else:
        t = t.rstrip("\n") + "\n\n" + bloque
    destino.write_text(t, encoding="utf-8")


def main() -> None:
    m = _cargar_01c()
    assert m.INEGI_API == INEGI_API
    bx, ig = m._cargar_tokens()
    limpiar = m._Limpio(bx, ig)
    H = {"Bmx-Token": bx, "Accept": "application/json"}
    hoy = dt.date.today()
    try:
        macro = json.loads((PROC / "macro.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        macro = {}

    def get_json(url: str, headers=None):
        err = ""
        for i in range(REINTENTOS):
            try:
                r = requests.get(url, headers=headers, timeout=TIMEOUT)
                if r.status_code == 200:
                    return r.json()
                err = f"HTTP {r.status_code}: {r.text[:120]}"
                if r.status_code in (400, 401, 403, 404):
                    break
            except requests.RequestException as e:
                err = f"{type(e).__name__}: {e}"
            time.sleep(1.5 * (i + 1))
        raise RuntimeError(limpiar(err))

    filas: list[dict] = []

    def agrega(clave, id_serie, unidad, fuente, pares):
        n0 = len(filas)
        for fecha, valor in pares:
            filas.append(dict(serie=clave, fecha=fecha, valor=float(valor), unidad=unidad, fuente=fuente, id_serie=id_serie))
        fs = [f["fecha"] for f in filas[n0:]]
        print(f"{clave:30s} {id_serie:8s} {len(fs):5d} datos  {min(fs)} .. {max(fs)}", flush=True)

    for clave, origen, id_def, esperado, unidad, llave in SERIES:
        id_serie = str(macro.get(llave, {}).get("id_serie") or id_def) if llave else id_def
        if origen == "banxico":
            meta = get_json(f"{m.BANXICO}/series/{id_serie}", H)["bmx"]["series"][0]
            titulo = " ".join(meta["titulo"].split())
            if esperado.lower() not in titulo.lower():
                raise RuntimeError(f"Banxico {id_serie}: el titulo '{titulo}' no contiene '{esperado}'")
            diaria = (meta.get("periodicidad") or "").lower().startswith("diaria")
            tramos = ([(dt.date(y, 1, 1), min(dt.date(y, 12, 31), hoy)) for y in range(DESDE.year, hoy.year + 1)]
                      if diaria else [(DESDE, hoy)])
            pares = []
            for a, b in tramos:
                j = get_json(f"{m.BANXICO}/series/{id_serie}/datos/{a.isoformat()}/{b.isoformat()}", H)
                for d in j["bmx"]["series"][0].get("datos", []):
                    if d["dato"] in ("N/E", "", None):
                        continue
                    pares.append((dt.datetime.strptime(d["fecha"], "%d/%m/%Y").date(), float(d["dato"].replace(",", ""))))
                time.sleep(0.2)
            fuente = f"Banco de Mexico, SIE API (serie {id_serie}); https://www.banxico.org.mx/SieInternet/"
        else:
            if esperado:
                j = get_json(f"{m.INEGI_API}/CL_INDICATOR/{id_serie}/es/BIE-BISE/2.0/{ig}?type=json")
                desc = " ".join(j["CODE"][0]["Description"].split())
                if esperado.lower() not in desc.lower():
                    raise RuntimeError(f"INEGI {id_serie}: la descripcion '{desc}' no contiene '{esperado}'")
            j = get_json(f"{m.INEGI_API}/INDICATOR/{id_serie}/es/00/false/BIE-BISE/2.0/{ig}?type=json")
            pares = []
            for o in j["Series"][0]["OBSERVATIONS"]:
                if o["OBS_VALUE"] in (None, ""):
                    continue
                y, mes = o["TIME_PERIOD"].split("/")[:2]
                pares.append((dt.date(int(y), int(mes), 1), float(o["OBS_VALUE"])))
            fuente = f"INEGI, Banco de Indicadores API (BIE, id {id_serie}); https://www.inegi.org.mx/app/indicadores/"
        pares = sorted({f: v for f, v in pares if f >= DESDE}.items())
        if not pares:
            raise RuntimeError(f"{clave}: sin datos desde {DESDE}")
        agrega(clave, id_serie, unidad, fuente, pares)

    df = pd.DataFrame(filas)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values(["serie", "fecha"]).reset_index(drop=True)
    PROC.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROC / "macro_series.parquet", index=False)
    escribe_fuentes(df, RAIZ / "data" / "FUENTES.md", hoy)
    print(f"macro_series.parquet: {len(df)} filas, {df['serie'].nunique()} series, consultado {hoy}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:  # los mensajes ya van sin tokens
        sys.exit(f"Error: {e}")
