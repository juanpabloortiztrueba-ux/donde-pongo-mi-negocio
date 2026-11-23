"""Etapa Datos A: Censo 2020 por AGEB urbana + Marco Geoestadistico 2020 + marginacion urbana CONAPO.

Produce:
  data/processed/zmvm_municipios.csv     lista oficial de municipios de la ZMVM
  data/processed/agebs_base.parquet      GeoParquet EPSG:4326, una fila por AGEB urbana de la ZMVM
  data/processed/_fuentes_01a.json       url, fecha, tamano y sha256 de cada descarga (alimenta data/FUENTES.md)

Uso (desde la raiz del repo):
  uv run python scripts/01a_censo_marco.py            # idempotente: si ya hay salidas, no hace nada
  uv run python scripts/01a_censo_marco.py --force    # rehace todo
  uv run python scripts/01a_censo_marco.py --keep-raw # no borra zips ni capas al terminar

No usa tokens: todas las fuentes son descargas publicas.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
PROC = RAIZ / "data" / "processed"
FUENTES_JSON = PROC / "_fuentes_01a.json"
FUENTES_MD = RAIZ / "data" / "FUENTES.md"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"}
ENTIDADES = {"09": "09_ciudaddemexico", "13": "13_hidalgo", "15": "15_mexico"}

# --- URLs (todas verificadas el 2026-11-23) ---
URL_CPV = ("https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/ageb_manzana/"
           "ageb_mza_urbana_{ent}_cpv2020_csv.zip")
URL_MARCO = ("https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/"
             "productos/geografia/marcogeo/889463807469/{nombre}.zip")
URL_IMU = "https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Marginacion/IMU_2020.zip"
URL_ZM2015 = "https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Delimitacion_ZM/ZM_2015.csv"

# Municipios de la ZM de la Ciudad de Mexico en la edicion 2020 de la delimitacion
# (SEDATU-CONAPO-INEGI, "Metropolis de Mexico 2020", cuadro B.09.1.01, pp. 180-183):
# 16 alcaldias + 2 de Hidalgo + 45 del Estado de Mexico = 63. Se usa solo para marcar la
# columna en_delim_2020; la lista base (76) es la edicion 2015, que es la que trae CSV oficial.
ZM2020 = (
    "09002 09003 09004 09005 09006 09007 09008 09009 09010 09011 09012 09013 09014 09015 09016 09017 "
    "13013 13069 15002 15011 15013 15020 15022 15023 15024 15025 15028 15029 15030 15031 15033 15035 "
    "15037 15038 15039 15044 15046 15053 15057 15058 15059 15060 15069 15070 15075 15081 15083 15084 "
    "15089 15091 15092 15093 15095 15099 15100 15103 15104 15108 15109 15120 15121 15122 15125"
).split()

# Variables del Censo (mnemonicos del diccionario de datos del CPV 2020 por AGEB y manzana)
COLS_CPV = ["ENTIDAD", "MUN", "LOC", "AGEB", "MZA", "NOM_LOC", "POBTOT", "POB0_14", "POB15_64", "POB65_MAS",
            "P_60YMAS", "P_15A17", "P_18A24", "TOTHOG", "VIVPAR_HAB", "VIVPARH_CV", "PROM_OCUP",
            "GRAPROES", "VPH_AUTOM", "VPH_INTER", "VPH_PC", "VPH_CEL", "PEA", "POCUPADA"]
NUM_CPV = COLS_CPV[6:]


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def cargar_fuentes() -> dict:
    return json.loads(FUENTES_JSON.read_text()) if FUENTES_JSON.exists() else {}


def descargar(url: str, destino: Path, fuentes: dict, clave: str, es_zip: bool = False) -> Path:
    """Descarga con reanudacion; rechaza respuestas HTML (los bloqueos de INEGI/CONAPO regresan HTML)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        if not es_zip or zipfile.is_zipfile(destino):
            registrar(fuentes, clave, url, destino)
            return destino
    print(f"  bajando {url}", flush=True)
    parcial = destino.with_suffix(destino.suffix + ".part")
    for intento in range(4):
        pos = parcial.stat().st_size if parcial.exists() else 0
        cab = dict(UA, **({"Range": f"bytes={pos}-"} if pos else {}))
        try:
            with requests.get(url, headers=cab, stream=True, timeout=60) as r:
                if r.status_code == 416:  # ya estaba completo
                    break
                r.raise_for_status()
                if "text/html" in r.headers.get("Content-Type", ""):
                    raise RuntimeError(f"{url} regreso HTML (bloqueo o URL rota)")
                modo = "ab" if r.status_code == 206 else "wb"
                with open(parcial, modo) as f:
                    for bloque in r.iter_content(1 << 20):
                        f.write(bloque)
            break
        except (requests.RequestException, OSError) as e:
            print(f"  intento {intento + 1} fallo: {e}", flush=True)
    else:
        raise RuntimeError(f"no se pudo bajar {url}")
    parcial.rename(destino)
    if es_zip and not zipfile.is_zipfile(destino):
        raise RuntimeError(f"{destino} no es un zip valido")
    registrar(fuentes, clave, url, destino)
    return destino


def registrar(fuentes: dict, clave: str, url: str, ruta: Path) -> None:
    if clave in fuentes and fuentes[clave].get("tam") == ruta.stat().st_size:
        return
    fuentes[clave] = {"url": url, "archivo": ruta.name, "descargado": dt.date.today().isoformat(),
                      "tam": ruta.stat().st_size, "sha256": sha256(ruta)}
    FUENTES_JSON.write_text(json.dumps(fuentes, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- 1) municipios
def paso_municipios(fuentes: dict) -> pd.DataFrame:
    print("1) Municipios de la ZMVM", flush=True)
    ruta = descargar(URL_ZM2015, RAW / "conapo" / "ZM_2015.csv", fuentes, "zm2015")
    d = pd.read_csv(ruta, dtype=str, encoding="cp1252")
    d.columns = [c.strip() for c in d.columns]
    d = d[d["NOM_ZM"].str.startswith("Valle de M")].copy()
    d["cvegeo_mun"] = d["CVE_MUN"].str.zfill(5)
    out = pd.DataFrame({
        "cve_ent": d["CVE_ENT"].str.zfill(2),
        "cve_mun": d["cvegeo_mun"].str[2:],
        "cvegeo_mun": d["cvegeo_mun"],
        # CONAPO trae "álvaro Obregón" (a minuscula); se corrige la primera letra
        "nom_mun": d["NOM_MUN"].str.strip().map(lambda n: n[:1].upper() + n[1:]),
        "nom_ent": d["NOM_ENT"].str.strip(),
        "pob_2015": pd.to_numeric(d["POB_2015"].str.replace(",", ""), errors="coerce"),
        "municipio_central": d["MC"].str.strip().eq("1") if "MC" in d else False,
    })
    out["en_delim_2020"] = out["cvegeo_mun"].isin(ZM2020)
    out["fuente"] = "CONAPO-SEDATU-INEGI, Delimitacion de ZM 2015 (ZM_2015.csv); en_delim_2020 segun Metropolis de Mexico 2020"
    out = out.sort_values("cvegeo_mun").reset_index(drop=True)
    assert len(out) == 76, f"se esperaban 76 municipios, hay {len(out)}"
    assert out["cvegeo_mun"].is_unique
    PROC.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROC / "zmvm_municipios.csv", index=False)
    print(f"  {len(out)} municipios ({out['cve_ent'].value_counts().to_dict()}); "
          f"{int(out['en_delim_2020'].sum())} tambien estan en la edicion 2020", flush=True)
    return out


# ---------------------------------------------------------------- 2) censo
def paso_censo(muns: pd.DataFrame, fuentes: dict) -> pd.DataFrame:
    print("2) Censo 2020 por AGEB urbana", flush=True)
    zmvm = set(muns["cvegeo_mun"])
    partes, locs = [], []
    for ent in ENTIDADES:
        z = descargar(URL_CPV.format(ent=ent), RAW / "censo2020" / f"ageb_mza_urbana_{ent}_cpv2020_csv.zip",
                      fuentes, f"cpv{ent}", es_zip=True)
        with zipfile.ZipFile(z) as zf:
            nombre = next(n for n in zf.namelist() if n.endswith(f"conjunto_de_datos_ageb_urbana_{ent}_cpv2020.csv"))
            with zf.open(nombre) as f:
                d = pd.read_csv(f, dtype=str, encoding="utf-8-sig", usecols=COLS_CPV)
            # diccionario de datos: se conserva (es chico) como referencia
            dic = next(n for n in zf.namelist() if "diccionario_datos_ageb_urbana" in n and n.endswith(".csv"))
            destino = RAW / "censo2020" / f"diccionario_datos_ageb_urbana_{ent}_cpv2020.csv"
            if not destino.exists():
                destino.write_bytes(zf.read(dic))
        d["cvegeo_mun"] = d["ENTIDAD"] + d["MUN"]
        d = d[d["cvegeo_mun"].isin(zmvm)]
        # nombre de la localidad: viene en las filas de manzana (en las de AGEB dice 'Total AGEB urbana')
        loc = d[(d["MZA"] != "000")].drop_duplicates(["ENTIDAD", "MUN", "LOC"])[["ENTIDAD", "MUN", "LOC", "NOM_LOC"]]
        locs.append(loc)
        # nivel AGEB: MZA = 000, NOM_LOC = 'Total AGEB urbana' (se excluyen los totales de localidad y municipio)
        ag = d[(d["MZA"] == "000") & (d["NOM_LOC"] == "Total AGEB urbana")].copy()
        partes.append(ag)
        print(f"  {ent}: {len(ag)} AGEB urbanas en la ZMVM", flush=True)
    ag = pd.concat(partes, ignore_index=True)
    locs = pd.concat(locs, ignore_index=True).rename(columns={"NOM_LOC": "nom_loc"})
    ag = ag.drop(columns="NOM_LOC").merge(locs, on=["ENTIDAD", "MUN", "LOC"], how="left")
    ag["cvegeo"] = ag["ENTIDAD"] + ag["MUN"] + ag["LOC"] + ag["AGEB"]
    assert ag["cvegeo"].str.len().eq(13).all() and ag["cvegeo"].is_unique

    # valores protegidos del Censo ('*', 'N/D') -> NaN; se cuentan
    prot = {}
    for c in NUM_CPV:
        raro = set(ag[c].dropna().unique()) - {"*", "N/D"}
        raro = {v for v in raro if not re.fullmatch(r"\d+(\.\d+)?", v)}
        assert not raro, f"{c}: valores no numericos inesperados {sorted(raro)[:5]}"
        prot[c] = int(ag[c].isin(["*", "N/D"]).sum())
        ag[c] = pd.to_numeric(ag[c], errors="coerce")
    pd.Series(prot).to_json(PROC / "_protegidos_01a.json")

    s = pd.DataFrame({"cvegeo": ag["cvegeo"], "cve_ent": ag["ENTIDAD"], "cve_mun": ag["MUN"],
                      "cvegeo_mun": ag["cvegeo_mun"], "cve_loc": ag["LOC"], "nom_loc": ag["nom_loc"]})
    s["pob_total"] = ag["POBTOT"]
    # El Censo por AGEB no trae 25-29 ni 30-59 por separado: se dan los grupos exactos que si se pueden armar
    s["pob_0_14"] = ag["POB0_14"]
    s["pob_15_24"] = ag["P_15A17"] + ag["P_18A24"]
    s["pob_25_59"] = ag["POB15_64"] - s["pob_15_24"] - (ag["P_60YMAS"] - ag["POB65_MAS"])
    s["pob_60_mas"] = ag["P_60YMAS"]
    s["pob_15_64"] = ag["POB15_64"]
    s["pob_65_mas"] = ag["POB65_MAS"]
    s["hogares"] = ag["TOTHOG"]
    s["viviendas_habitadas"] = ag["VIVPAR_HAB"]
    s["prom_ocupantes"] = ag["PROM_OCUP"]
    s["escolaridad_prom"] = ag["GRAPROES"]
    den = ag["VIVPARH_CV"].where(ag["VIVPARH_CV"] > 0)
    for nombre, col in [("auto", "VPH_AUTOM"), ("internet", "VPH_INTER"), ("pc", "VPH_PC"), ("celular", "VPH_CEL")]:
        s[f"pct_viv_{nombre}"] = (100 * ag[col] / den).clip(0, 100)
    s["pea"] = ag["PEA"]
    s["pob_ocupada"] = ag["POCUPADA"]
    neg = (s[["pob_25_59"]] < 0).sum().sum()
    if neg:
        print(f"  aviso: {neg} AGEB con pob_25_59 < 0 (se ponen NaN)")
        s.loc[s["pob_25_59"] < 0, "pob_25_59"] = np.nan
    return s


# ---------------------------------------------------------------- 3) marco geoestadistico
def paso_marco(muns: pd.DataFrame, fuentes: dict) -> gpd.GeoDataFrame:
    print("3) Marco Geoestadistico 2020 (AGEB urbanas)", flush=True)
    zmvm = set(muns["cvegeo_mun"])
    capas = []
    for ent, nombre in ENTIDADES.items():
        z = descargar(URL_MARCO.format(nombre=nombre), RAW / "marco2020" / f"{nombre}.zip", fuentes,
                      f"marco{ent}", es_zip=True)
        # solo la capa de AGEB urbana ('<ent>a'); se lee directo del zip, sin extraer el resto
        g = gpd.read_file(f"zip://{z}!conjunto_de_datos/{ent}a.shp")
        g = g[(g["CVE_ENT"] + g["CVE_MUN"]).isin(zmvm)]
        capas.append(g)
        print(f"  {ent}: {len(g)} poligonos de AGEB urbana en la ZMVM", flush=True)
    g = pd.concat(capas, ignore_index=True)
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=capas[0].crs)
    assert g["CVEGEO"].is_unique
    # area y centroide en proyeccion metrica (EPSG:6372, ITRF2008 / LCC Mexico, la oficial de INEGI)
    m = g.to_crs(6372)
    g["area_km2"] = m.geometry.area / 1e6
    cen = gpd.GeoSeries(m.geometry.centroid, crs=6372).to_crs(4326)
    g["lon"], g["lat"] = cen.x, cen.y
    g = g.to_crs(4326)
    return g.rename(columns={"CVEGEO": "cvegeo"})[["cvegeo", "geometry", "lat", "lon", "area_km2"]]


# ---------------------------------------------------------------- 4) marginacion
def paso_marginacion(fuentes: dict) -> pd.DataFrame:
    print("4) Indice de marginacion urbana 2020 (CONAPO)", flush=True)
    z = descargar(URL_IMU, RAW / "conapo" / "IMU_2020.zip", fuentes, "imu2020", es_zip=True)
    with zipfile.ZipFile(z) as zf:
        n = next(n for n in zf.namelist() if n.lower().endswith(".xls"))
        datos = zf.read(n)
    # la hoja con los datos es 'IMU_2020' (la primera hoja trae los mismos datos con encabezados largos)
    d = pd.read_excel(io.BytesIO(datos), sheet_name="IMU_2020", dtype={"CVE_AGEB": str}, engine="xlrd")
    d = d.rename(columns={"CVE_AGEB": "cvegeo", "IM_2020": "im_2020", "GM_2020": "gm_2020", "IMN_2020": "imn_2020"})
    d["cvegeo"] = d["cvegeo"].str.strip()
    d = d[d["cvegeo"].str[:2].isin(ENTIDADES)]
    assert d["cvegeo"].str.len().eq(13).all() and d["cvegeo"].is_unique
    return d[["cvegeo", "im_2020", "gm_2020", "imn_2020"]]


# ---------------------------------------------------------------- limpieza
def limpiar() -> None:
    """Borra zips y capas: todo se puede volver a bajar con este mismo script."""
    for sub in ("censo2020", "marco2020"):
        for z in (RAW / sub).glob("*.zip"):
            z.unlink()
    (RAW / "conapo" / "IMU_2020.zip").unlink(missing_ok=True)
    for carpeta in (RAW / "censo2020", RAW / "marco2020"):
        for p in carpeta.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
    if (RAW / "marco2020").exists() and not any((RAW / "marco2020").iterdir()):
        (RAW / "marco2020").rmdir()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--keep-raw", action="store_true")
    a = ap.parse_args()
    salidas = [PROC / "zmvm_municipios.csv", PROC / "agebs_base.parquet"]
    if all(p.exists() for p in salidas) and not a.force:
        print("Ya existen las salidas; usa --force para rehacer.")
        return 0
    fuentes = cargar_fuentes()
    muns = paso_municipios(fuentes)
    cen = paso_censo(muns, fuentes)
    geo = paso_marco(muns, fuentes)
    imu = paso_marginacion(fuentes)

    print("5) Union por cvegeo", flush=True)
    sin_poligono = set(cen["cvegeo"]) - set(geo["cvegeo"])
    sin_censo = set(geo["cvegeo"]) - set(cen["cvegeo"])
    print(f"  AGEB del Censo sin poligono: {len(sin_poligono)}; poligonos sin fila de Censo: {len(sin_censo)}")
    # base = AGEB del Censo con poligono (el modelo necesita geometria)
    base = cen.merge(geo, on="cvegeo", how="inner")
    base = base.merge(imu, on="cvegeo", how="left")
    base = base.merge(muns[["cvegeo_mun", "nom_mun"]], on="cvegeo_mun", how="left").drop(columns="cvegeo_mun")
    cols = ["cvegeo", "cve_ent", "cve_mun", "nom_mun", "cve_loc", "nom_loc", "geometry", "lat", "lon", "area_km2"]
    base = base[cols + [c for c in base.columns if c not in cols]]
    base = gpd.GeoDataFrame(base, geometry="geometry", crs=4326).sort_values("cvegeo").reset_index(drop=True)
    base.to_parquet(PROC / "agebs_base.parquet")

    resumen = {
        "agebs_censo_sin_poligono": sorted(sin_poligono), "poligonos_sin_censo": sorted(sin_censo),
        "filas": len(base), "pob_total": float(base["pob_total"].sum()),
        "sin_marginacion": int(base["im_2020"].isna().sum()),
    }
    (PROC / "_resumen_01a.json").write_text(json.dumps(resumen, indent=1))
    print(json.dumps({k: v for k, v in resumen.items() if not isinstance(v, list)}, indent=1))

    escribir_fuentes_md()
    if not a.keep_raw:
        limpiar()
        print("zips y capas borrados de data/raw")
    return 0


def escribir_fuentes_md() -> None:
    """Regenera el bloque de 01a en data/FUENTES.md a partir de _fuentes_01a.json."""
    f = cargar_fuentes()
    nota = {
        "zm2015": "Delimitacion de zonas metropolitanas 2015 (SEDATU-CONAPO-INEGI), indicadores por municipio. Lista base de la ZMVM (76 municipios).",
        "imu2020": "Indice de marginacion urbana 2020 por AGEB (CONAPO), hoja IMU_2020. Fecha de corte: Censo 2020; archivo publicado 2021-09-24.",
    }
    lin = ["<!-- 01a:inicio (generado por scripts/01a_censo_marco.py; no editar a mano) -->",
           "## Etapa Datos A: Censo 2020, Marco Geoestadistico, marginacion, municipios",
           "",
           "| Archivo | URL | Descarga | Fecha de corte o levantamiento | Tamano (bytes) | sha256 |",
           "|---|---|---|---|---|---|"]
    corte = {"cpv": "Censo de Poblacion y Vivienda 2020, levantamiento 2020-03-02 a 2020-03-27 (archivo AGEB y manzana, reemplazado por INEGI el 2021-07-26)",
             "marco": "Marco Geoestadistico, Censo de Poblacion y Vivienda 2020 (INEGI, publicado 2021-01-25)"}
    for k, v in f.items():
        c = nota.get(k) or next((t for p, t in corte.items() if k.startswith(p)), "")
        lin.append(f"| {v['archivo']} | {v['url']} | {v['descargado']} | {c} | {v['tam']} | `{v['sha256']}` |")
    lin += ["",
            "Notas:",
            "- Diccionario de datos del Censo: `data/raw/censo2020/diccionario_datos_ageb_urbana_<ent>_cpv2020.csv` (se conserva).",
            "- Lista de municipios 2020 (63 de la ZM de la Ciudad de Mexico): SEDATU-CONAPO-INEGI, *Metropolis de Mexico 2020*, "
            "cuadro B.09.1.01, https://www.gob.mx/cms/uploads/sedatu/MM2020_06022024.pdf (PDF, 188 pp., sha256 no registrado: solo se consulto).",
            "- Los zip y las capas del Marco que no se usan (manzanas, localidades, ejes, etc.) se borran al terminar; el script los vuelve a bajar.",
            "<!-- 01a:fin -->", ""]
    bloque = "\n".join(lin)
    txt = FUENTES_MD.read_text() if FUENTES_MD.exists() else "# Fuentes de datos\n\n"
    pat = re.compile(r"<!-- 01a:inicio.*?<!-- 01a:fin -->\n?", re.S)
    txt = pat.sub(lambda m: bloque, txt) if pat.search(txt) else txt.rstrip("\n") + "\n\n" + bloque
    FUENTES_MD.write_text(txt)


if __name__ == "__main__":
    sys.exit(main())
