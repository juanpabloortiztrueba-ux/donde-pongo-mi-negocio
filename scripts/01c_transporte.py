"""Etapa Datos C (parte 3): estaciones de transporte masivo de la ZMVM.

Uso: uv run python scripts/01c_transporte.py
Salida: data/processed/transporte.parquet
  sistema, linea, estacion, lat, lon, afluencia_anual, anio_afluencia,
  afluencia_anual_linea, nivel_afluencia, tipo, estado, anio_apertura, alcaldia_municipio, fuente

- afluencia_anual: viajeros del anio indicado en `anio_afluencia`, SOLO donde el dato abierto
  es por estacion (Metro). Para Metrobus, Cablebus y Tren Ligero el dato abierto es por linea o
  por sistema: va en `afluencia_anual_linea` y `afluencia_anual` queda NaN.
- Mexibus y Mexicable (Edomex): ver bitacora; se agregan solo si hay fuente verificable.
Idempotente: no vuelve a bajar lo que ya esta en data/raw/transporte.
"""
from __future__ import annotations

import json
import re
import unicodedata
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw" / "transporte"
PROC = RAIZ / "data" / "processed"
UA = {"User-Agent": "Mozilla/5.0"}
D = "https://datos.cdmx.gob.mx/dataset"
ANIO = 2025  # ultimo anio completo con datos de afluencia

# nombre local -> URL (portal de datos abiertos de la CDMX, descargas directas)
ARCHIVOS = {
    "gtfs_cdmx.zip": f"{D}/75538d96-3ade-4bc5-ae7d-d85595e4522d/resource/32ed1b6b-41cd-49b3-b7f0-b57acb0eb819/download/32ed1b6b-41cd-49b3-b7f0-b57acb0eb819.zip",
    "metro_estaciones_shp.zip": f"{D}/1b014317-ddb1-46c7-ac79-7330c652abe3/resource/288b10dd-4f21-4338-b1ed-239487820512/download/288b10dd-4f21-4338-b1ed-239487820512.zip",
    "metro_afluencia_simple_10_2026.csv": f"{D}/f2046fd5-51b5-4876-b008-bd65d95f9a02/resource/0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb/download/afluenciastc_simple_10_2026.csv",
    "metrobus_estaciones_shp.zip": f"{D}/63a08f93-e959-430f-8dc4-bf07182401e6/resource/66cd5773-d83f-4a80-8c15-8ab34851e046/download/66cd5773-d83f-4a80-8c15-8ab34851e046.zip",
    "metrobus_afluencia_simple_10_2026.csv": f"{D}/f0ff3759-5c5d-41fb-80cc-2a3c8bbab278/resource/f7943c47-835d-4078-93ea-906f64b72f3b/download/afluenciamb_simple_10_2026.csv",
    "ste_shp.zip": f"{D}/6a3bc652-a775-41a0-aeb6-05d31ee40b59/resource/c7a1b906-92ff-4525-9b0c-f166ea731f95/download/c7a1b906-92ff-4525-9b0c-f166ea731f95.zip",
    "tl_afluencia_desglosada_10_2026.csv": f"{D}/ee806dd2-c919-46f2-858f-6a55a05b8ee6/resource/c6f15e48-791d-4ed6-adc3-8d93ed80a055/download/afluencia_desglosada_tl_10_2026.csv",
    "cb_afluencia_desglosada_10_2026.csv": f"{D}/ee806dd2-c919-46f2-858f-6a55a05b8ee6/resource/176c0d20-0111-43bc-903c-d7e807ff37c0/download/afluencia_desglosada_cb_10_2026.csv",
    "interurbano_cobertura.json": f"{D}/ecabde39-52bc-461b-8c5b-6beb88ca1bb7/resource/3f731857-65c1-4399-8deb-f1086f903ab7/download/3f731857-65c1-4399-8deb-f1086f903ab7.json",
}
F_METRO = "Sistema de Transporte Colectivo Metro, datos.cdmx.gob.mx (estaciones SHP y afluencia diaria)"
F_MB = "Metrobus, datos.cdmx.gob.mx (estaciones SHP y afluencia diaria por linea)"
F_STE = "Servicio de Transportes Electricos CDMX, datos.cdmx.gob.mx (SHP y afluencia diaria)"
F_GTFS = "GTFS estatico de la CDMX (datos.cdmx.gob.mx/dataset/gtfs), feed de 2026-02"


def bajar() -> None:
    """Baja lo que falte, extrae los zip y los borra."""
    RAW.mkdir(parents=True, exist_ok=True)
    for nombre, url in ARCHIVOS.items():
        dest = RAW / nombre
        if nombre.endswith(".zip"):
            carpeta = RAW / nombre[:-4]
            if carpeta.exists():
                continue
            r = requests.get(url, headers=UA, timeout=180)
            r.raise_for_status()
            dest.write_bytes(r.content)
            with zipfile.ZipFile(dest) as z:
                z.extractall(carpeta)
            dest.unlink()  # se borra el zip
        elif not dest.exists() or dest.stat().st_size < 1000:
            r = requests.get(url, headers=UA, timeout=180)
            r.raise_for_status()
            dest.write_bytes(r.content)
    # el zip del STE trae tres zip adentro
    for z in list((RAW / "ste_shp").rglob("*.zip")):
        out = z.with_suffix("")
        if not out.exists():
            with zipfile.ZipFile(z) as zz:
                zz.extractall(out)
        z.unlink()


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def arreglar_texto(s: str) -> str:
    """Algunos CSV del portal vienen con mojibake (UTF-8 leido como latin-1)."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def clave_linea(txt: str) -> str:
    """'Linea 1', 'Línea A', 'LÃ­nea 12' -> '1', 'A', '12'."""
    t = arreglar_texto(str(txt))
    m = re.search(r"n[eé]a\s*([0-9A-Za-z]+)\s*$", t, re.I)
    return (m.group(1) if m else t).upper().lstrip("0") or "0"


def puntos(g: gpd.GeoDataFrame) -> pd.DataFrame:
    g = g.to_crs(4326)
    return pd.DataFrame({"lat": g.geometry.y.values, "lon": g.geometry.x.values}, index=g.index)


# ---------------------------------------------------------------- sistemas
def metro() -> pd.DataFrame:
    g = gpd.read_file(next((RAW / "metro_estaciones_shp").rglob("STC_Metro_estaciones*.shp")))
    df = pd.concat([g[["NOMBRE", "LINEA", "TIPO", "ALCALDIAS", "AÑO"]], puntos(g)], axis=1)
    df["linea"] = df.LINEA.str.lstrip("0").str.upper()
    a = pd.read_csv(RAW / "metro_afluencia_simple_10_2026.csv", encoding="utf-8")
    a["lin"] = a.linea.map(clave_linea)
    a["k"] = a.lin + "|" + a.estacion.map(arreglar_texto).map(norm)
    af = a[a.anio == ANIO].groupby("k").afluencia.sum()
    # el SHP y el CSV no escriben igual dos estaciones
    alias = {"ninosheroespoderjudicialcdmx": "ninosheroes", "mixhiuca": "mixiuhca"}
    df["k"] = df.linea + "|" + df.NOMBRE.map(norm).replace(alias)
    df["afluencia_anual"] = df.k.map(af)
    sin = set(af.index) - set(df.k)
    if sin:
        print("  Metro: afluencia sin estacion en el SHP:", sorted(sin)[:10])
    print(f"  Metro: {len(df)} estaciones, {df.afluencia_anual.notna().sum()} con afluencia {ANIO}")
    return pd.DataFrame(dict(
        sistema="Metro", linea=df.linea, estacion=df.NOMBRE, lat=df.lat, lon=df.lon,
        afluencia_anual=df.afluencia_anual, anio_afluencia=ANIO, afluencia_anual_linea=np.nan,
        nivel_afluencia="estacion", tipo=df.TIPO, estado="operando",
        anio_apertura=df["AÑO"], alcaldia_municipio=df.ALCALDIAS, fuente=F_METRO))


def metrobus() -> pd.DataFrame:
    g = gpd.read_file(next((RAW / "metrobus_estaciones_shp").rglob("Metrobus_estaciones.shp")))
    df = pd.concat([g[["NOMBRE", "LINEA", "TIPO", "ALCALDIAS", "AÑO"]], puntos(g)], axis=1)
    df["linea"] = df.LINEA.str.lstrip("0")
    a = pd.read_csv(RAW / "metrobus_afluencia_simple_10_2026.csv")
    a["lin"] = a.linea.map(clave_linea)
    por_linea = a[a.anio == ANIO].groupby("lin").afluencia.sum()
    df["afl_linea"] = df.linea.map(por_linea)
    temporal = df.TIPO.eq("Servicio temporal")
    print(f"  Metrobus: {len(df)} estaciones ({temporal.sum()} de servicio temporal), lineas con afluencia: {sorted(por_linea.index)}")
    return pd.DataFrame(dict(
        sistema="Metrobus", linea=df.linea, estacion=df.NOMBRE, lat=df.lat, lon=df.lon,
        afluencia_anual=np.nan, anio_afluencia=ANIO, afluencia_anual_linea=df.afl_linea,
        nivel_afluencia="linea", tipo=df.TIPO, estado=np.where(temporal, "servicio temporal", "operando"),
        anio_apertura=df["AÑO"], alcaldia_municipio=df.ALCALDIAS, fuente=F_MB))


def tren_ligero() -> pd.DataFrame:
    g = gpd.read_file(next((RAW / "ste_shp").rglob("STE_TrenLigero_estaciones*.shp")))
    df = pd.concat([g[["NOMBRE", "LINEA", "TIPO", "ALCALDIAS", "AÑO"]], puntos(g)], axis=1)
    t = pd.read_csv(RAW / "tl_afluencia_desglosada_10_2026.csv")
    tot = float(t[t.anio == ANIO].afluencia.sum())  # el dato abierto es del sistema completo
    print(f"  Tren Ligero: {len(df)} estaciones; afluencia {ANIO} del sistema: {tot:,.0f}")
    return pd.DataFrame(dict(
        sistema="Tren Ligero", linea=df.LINEA.str.lstrip("0"), estacion=df.NOMBRE, lat=df.lat, lon=df.lon,
        afluencia_anual=np.nan, anio_afluencia=ANIO, afluencia_anual_linea=tot,
        nivel_afluencia="sistema", tipo=df.TIPO, estado="operando",
        anio_apertura=df["AÑO"], alcaldia_municipio=df.ALCALDIAS, fuente=F_STE))


def cablebus() -> pd.DataFrame:
    g = gpd.read_file(next((RAW / "ste_shp").rglob("STE_Cablebus_estaciones*.shp")))
    df = pd.concat([g[["NOMBRE", "LINEA", "TIPO", "ALCALDIAS", "AÑO"]], puntos(g)], axis=1)
    c = pd.read_csv(RAW / "cb_afluencia_desglosada_10_2026.csv")
    c["lin"] = c.linea.map(clave_linea)
    por_linea = c[c.anio == ANIO].groupby("lin").afluencia.sum()
    df["linea"] = df.LINEA.str.lstrip("0")
    print(f"  Cablebus: {len(df)} estaciones; afluencia {ANIO} por linea: {por_linea.round(0).to_dict()}")
    return pd.DataFrame(dict(
        sistema="Cablebus", linea=df.linea, estacion=df.NOMBRE, lat=df.lat, lon=df.lon,
        afluencia_anual=np.nan, anio_afluencia=ANIO, afluencia_anual_linea=df.linea.map(por_linea),
        nivel_afluencia="linea", tipo=df.TIPO, estado="operando",
        anio_apertura=df["AÑO"], alcaldia_municipio=df.ALCALDIAS, fuente=F_STE))


def gtfs_paradas(agencia: str) -> pd.DataFrame:
    G = RAW / "gtfs_cdmx"
    st = pd.read_csv(G / "stops.txt", dtype=str)
    tr = pd.read_csv(G / "trips.txt", dtype=str)
    rt = pd.read_csv(G / "routes.txt", dtype=str)
    stt = pd.read_csv(G / "stop_times.txt", dtype=str, usecols=["trip_id", "stop_id"])
    m = stt.merge(tr[["trip_id", "route_id"]], on="trip_id").merge(
        rt[["route_id", "agency_id", "route_short_name"]], on="route_id")
    m = m[m.agency_id == agencia].drop_duplicates(["stop_id", "route_id"]).merge(st, on="stop_id")
    m["lat"] = m.stop_lat.astype(float)
    m["lon"] = m.stop_lon.astype(float)
    return m[["route_short_name", "stop_name", "lat", "lon"]].rename(
        columns={"route_short_name": "linea", "stop_name": "estacion"})


def suburbano() -> pd.DataFrame:
    df = gtfs_paradas("SUB")
    print(f"  Tren Suburbano: {len(df)} estaciones (GTFS)")
    return pd.DataFrame(dict(
        sistema="Tren Suburbano", linea=df.linea, estacion=df.estacion, lat=df.lat, lon=df.lon,
        afluencia_anual=np.nan, anio_afluencia=np.nan, afluencia_anual_linea=np.nan,
        nivel_afluencia=None, tipo=None, estado="operando (GTFS 2026-02)",
        anio_apertura=np.nan, alcaldia_municipio=None, fuente=F_GTFS + "; sin dato abierto de afluencia"))


def interurbano() -> pd.DataFrame:
    """Tren Interurbano Mexico-Toluca (El Insurgente). Solo Santa Fe y Observatorio caen en la ZMVM."""
    df = gtfs_paradas("INTERURBANO")
    j = json.load(open(RAW / "interurbano_cobertura.json"))
    cent = {}
    for f in j["features"]:
        pol = gpd.GeoDataFrame.from_features([f], crs=4326).to_crs(32614).geometry
        c = pol.centroid.to_crs(4326).iloc[0]
        cent[norm(f["properties"]["Name"])] = (c.y, c.x)
    filas = []
    for _, r in df.iterrows():
        lat, lon = r.lat, r.lon
        if "santafe" in norm(r.estacion) and any("santafe" in k for k in cent):
            lat, lon = next(v for k, v in cent.items() if "santafe" in k)
        filas.append((r.linea, r.estacion, lat, lon, "operando (GTFS 2026-02)"))
    for k, (la, lo) in cent.items():
        if "observatorio" in k:
            filas.append(("1", "Observatorio", la, lo, "apertura no confirmada en el GTFS 2026-02"))
    d = pd.DataFrame(filas, columns=["linea", "estacion", "lat", "lon", "estado"])
    print(f"  Tren Interurbano: {len(d)} estaciones")
    return pd.DataFrame(dict(
        sistema="Tren Interurbano", linea=d.linea, estacion=d.estacion, lat=d.lat, lon=d.lon,
        afluencia_anual=np.nan, anio_afluencia=np.nan, afluencia_anual_linea=np.nan,
        nivel_afluencia=None, tipo=None, estado=d.estado, anio_apertura=np.nan, alcaldia_municipio=None,
        fuente=F_GTFS + " y cobertura de 1,200 m (datos.cdmx.gob.mx); sin dato abierto de afluencia"))


# ------------------------------------------- Edomex: Mexibus y Mexicable (OpenStreetMap)
OVERPASS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter")
F_OSM = "OpenStreetMap (ODbL) via Overpass API; no hay dato abierto oficial; completitud no verificada"
BBOX = "(19.3,-99.3,19.85,-98.8)"


def overpass(consulta: str, cache: Path) -> list[dict]:
    if cache.exists():
        return json.loads(cache.read_text())
    for url in OVERPASS:
        try:
            r = requests.post(url, data={"data": consulta}, timeout=70,
                              headers={"User-Agent": "donde-pongo-mi-negocio-escolar/1.0"})
            if r.status_code == 200:
                els = r.json()["elements"]
                cache.write_text(json.dumps(els))
                return els
        except requests.RequestException:
            continue
    return []


def osm_edomex() -> pd.DataFrame:
    """Mexibus (rutas tipo bus con 'Mexib' en el nombre) y Mexicable (estaciones aerialway)."""
    q_mb = f'[out:json][timeout:45];relation["route"="bus"]["name"~"Mexib",i]{BBOX}->.r;(.r;node(r.r););out body;'
    q_mc = f'[out:json][timeout:45];node["aerialway"="station"]["network"~"Mexicable",i]{BBOX};out body;'
    filas = []
    els = overpass(q_mb, RAW / "osm_mexibus.json")
    nodos = {e["id"]: e for e in els if e["type"] == "node"}
    for rel in (e for e in els if e["type"] == "relation"):
        m = re.search(r"L(?:[ií]nea)?\s*(\d+A?)", rel["tags"].get("name", ""), re.I)
        if not m:
            continue
        for mem in rel["members"]:
            n = nodos.get(mem["ref"]) if mem["type"] == "node" else None
            if n and n.get("tags", {}).get("name") and mem["role"] in ("stop", "platform", "stop_entry_only", "stop_exit_only", ""):
                filas.append(("Mexibus", m.group(1).upper(), n["tags"]["name"], n["lat"], n["lon"], "operando segun OSM"))
    for n in overpass(q_mc, RAW / "osm_mexicable.json"):
        t = n.get("tags", {})
        lin = re.search(r"L[ií]nea\s*(\d+)", t.get("network", ""), re.I)
        if t.get("name") and lin:
            filas.append(("Mexicable", lin.group(1), t["name"], n["lat"], n["lon"],
                          "operando segun OSM" if lin.group(1) == "1" else "segun OSM; apertura no verificada con fuente oficial"))
    if not filas:
        print("  Mexibus/Mexicable: NO ENCONTRADO (Overpass no respondio)")
        return pd.DataFrame()
    d = pd.DataFrame(filas, columns=["sistema", "linea", "estacion", "lat", "lon", "estado"])
    # dos sentidos por estacion: se promedia por (sistema, linea, estacion)
    d = d.groupby(["sistema", "linea", "estacion"], as_index=False).agg(lat=("lat", "mean"), lon=("lon", "mean"),
                                                                       estado=("estado", "first"))
    for s, g in d.groupby("sistema"):
        print(f"  {s}: {len(g)} estaciones (lineas {sorted(g.linea.unique())})")
    return pd.DataFrame(dict(
        sistema=d.sistema, linea=d.linea, estacion=d.estacion, lat=d.lat, lon=d.lon,
        afluencia_anual=np.nan, anio_afluencia=np.nan, afluencia_anual_linea=np.nan,
        nivel_afluencia=None, tipo=None, estado=d.estado, anio_apertura=np.nan,
        alcaldia_municipio=None, fuente=F_OSM))


def construir() -> None:
    bajar()
    partes = [metro(), metrobus(), tren_ligero(), cablebus(), suburbano(), interurbano()]
    partes.append(osm_edomex())
    df = pd.concat(partes, ignore_index=True)
    df["lat"] = df.lat.astype(float)
    df["lon"] = df.lon.astype(float)
    # solo ZMVM: cuadro generoso del valle; se quitan estaciones de Toluca y alrededores
    en_valle = df.lon.between(-99.45, -98.6) & df.lat.between(19.0, 20.0)
    fuera = df[~en_valle]
    if len(fuera):
        print("  fuera de la ZMVM (se descartan):", fuera[["sistema", "estacion"]].values.tolist())
    df = df[en_valle].reset_index(drop=True)
    for c in ("afluencia_anual", "anio_afluencia", "afluencia_anual_linea", "anio_apertura"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    PROC.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROC / "transporte.parquet", index=False)
    print("transporte.parquet:", df.shape)
    print(df.groupby("sistema").size().to_dict())


if __name__ == "__main__":
    construir()
