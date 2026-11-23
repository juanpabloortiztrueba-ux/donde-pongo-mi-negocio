"""Etapa Datos B: DENUE (descarga masiva) de la ZMVM, corte actual + corte historico, y catalogo SCIAN.

Produce:
  data/processed/denue_actual.parquet      DENUE mas reciente (solo municipios de la ZMVM)
  data/processed/denue_hist.parquet        DENUE ~2020 (por defecto 11/2020), solo ZMVM
  data/processed/scian.csv                 catalogo SCIAN 2023 (el que usa el DENUE actual): codigo, titulo, nivel
  data/processed/scian_2018.csv            catalogo SCIAN 2018 (algunos codigos del corte historico ya son 2018)
  data/processed/scian_2013.csv            catalogo SCIAN 2013 (el que usa casi todo el corte historico)
  data/processed/scian_hist_a_actual.csv   puente codigo del corte historico -> codigo del corte actual (empirico, con
                                           los ids que estan en ambos cortes). En denue_hist la columna
                                           `codigo_act_actual` ya trae el codigo traducido.
  data/processed/_fuentes_01b.json         url, fecha, tamano y sha256 de cada descarga
  data/FUENTES.md                          se le agregan las filas de esta etapa

Fuente de la descarga: https://www.inegi.org.mx/app/descarga/?ti=6 (DENUE, "Otros | DENUE").
Las URLs se descubren con la misma API que usa esa pagina, asi que si INEGI publica un
corte nuevo, el script toma el mas reciente solo.

Uso (desde la raiz del repo):
  uv run python scripts/01b_denue.py                 # idempotente: no rehace lo que ya existe
  uv run python scripts/01b_denue.py --force         # rehace todo
  uv run python scripts/01b_denue.py --hist 04/2020  # otro corte historico (MM/AAAA)
  uv run python scripts/01b_denue.py --keep-raw      # no borra zips ni CSV al terminar

No usa tokens: la base es la descarga masiva (publica).
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
RAW_DENUE = RAW / "denue"
RAW_SCIAN = RAW / "scian"
PROC = RAIZ / "data" / "processed"
FUENTES_JSON = PROC / "_fuentes_01b.json"
FUENTES_MD = RAIZ / "data" / "FUENTES.md"
MUNICIPIOS_CSV = PROC / "zmvm_municipios.csv"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"}
API = "https://www.inegi.org.mx/app/api/descarga/descarga/descargamasiva/lista"
CONTENIDOS = "https://www.inegi.org.mx/contenidos"
ENTIDADES = ["09", "13", "15"]

URL_SCIAN_2023 = "https://www.inegi.org.mx/contenidos/app/scian/scian_2023_categorias_y_productos.xlsx"
URL_SCIAN_2018 = "https://www.inegi.org.mx/contenidos/app/scian/scian_2018_categorias_y_productos.xlsx"
URL_SCIAN_2013 = "https://www.inegi.org.mx/contenidos/app/clasificadores/scian/SCIAN_2013_estructura_productos.xlsx"

# Columnas del CSV del DENUE que se leen (el resto -- calles, telefonos, correos -- no sirve al modelo)
COLS = ["id", "nom_estab", "raz_social", "codigo_act", "nombre_act", "per_ocu", "tipo_asent", "nomb_asent",
        "cod_postal", "cve_ent", "cve_mun", "cve_loc", "ageb", "manzana", "tipoUniEco", "latitud", "longitud",
        "fecha_alta"]

# Cuadro aproximado de la ZMVM (lat, lon) para descartar coordenadas absurdas
BBOX = (18.8, 20.4, -100.0, -98.2)


# ------------------------------------------------------------------ utilidades
def log(*a):
    print(dt.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def sha256(path, bloque=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(bloque):
            h.update(b)
    return h.hexdigest()


def cargar_fuentes():
    return json.loads(FUENTES_JSON.read_text()) if FUENTES_JSON.exists() else {}


def guardar_fuentes(d):
    FUENTES_JSON.write_text(json.dumps(d, indent=1, ensure_ascii=False))


def descargar(url, destino, fuentes, clave, corte, notas=""):
    """Baja url a destino (idempotente) y registra url/fecha/tamano/sha256 en `fuentes`."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not (destino.exists() and destino.stat().st_size > 0):
        tmp = destino.with_suffix(destino.suffix + ".part")
        log("bajando", url)
        for intento in range(1, 9):  # el servidor de INEGI a veces se cuelga: reintenta y reanuda
            ya = tmp.stat().st_size if tmp.exists() else 0
            try:
                cab = dict(UA, Range=f"bytes={ya}-") if ya else UA
                with requests.get(url, headers=cab, stream=True, timeout=(15, 45)) as r:
                    if r.status_code == 416:  # ya estaba completo
                        break
                    r.raise_for_status()
                    with open(tmp, "ab" if (ya and r.status_code == 206) else "wb") as f:
                        for trozo in r.iter_content(1 << 20):
                            f.write(trozo)
                break
            except requests.RequestException as e:
                log(f"intento {intento} fallo ({type(e).__name__}); reintento")
        else:
            raise SystemExit(f"No se pudo bajar {url}")
        tmp.rename(destino)
    if clave not in fuentes or fuentes[clave].get("sha256") is None:
        fuentes[clave] = {"url": url, "archivo": destino.name, "descargado": dt.date.today().isoformat(),
                          "corte": corte, "tam": destino.stat().st_size, "sha256": sha256(destino), "notas": notas}
        guardar_fuentes(fuentes)
    return destino


def agregar_a_fuentes_md(fuentes):
    """Agrega (sin reescribir) las filas de esta etapa a data/FUENTES.md; no duplica por sha256."""
    previo = FUENTES_MD.read_text() if FUENTES_MD.exists() else ""
    filas = []
    for clave, f in fuentes.items():
        if f["sha256"] in previo:
            continue
        filas.append(f"- `{f['archivo']}` | {f['url']} | descargado {f['descargado']} | corte {f['corte']} "
                     f"| {f['tam']:,} bytes | sha256 `{f['sha256']}` | etapa Datos B (01b_denue.py). {f.get('notas', '')}\n")
    if filas:
        with open(FUENTES_MD, "a") as fh:
            fh.write(("\n" if previo and not previo.endswith("\n") else "") + "".join(filas))


# ------------------------------------------------------------------ lista de municipios
def municipios_zmvm():
    """Claves cve_ent+cve_mun (5 caracteres) de la ZMVM. Usa el CSV de Datos A (76 municipios, delimitacion
    CONAPO-SEDATU-INEGI 2015). Si aun no existe, usa la lista de respaldo de abajo y avisa."""
    if MUNICIPIOS_CSV.exists():
        d = pd.read_csv(MUNICIPIOS_CSV, dtype=str)
        return sorted(d["cvegeo_mun"].tolist())
    log("AVISO: no existe zmvm_municipios.csv; uso la lista de respaldo (delimitacion 2015, 76 municipios)")
    return RESPALDO_76


# Respaldo: 16 alcaldias + 59 municipios del Edomex + Tizayuca (CONAPO ZM_2015.csv)
RESPALDO_76 = sorted(
    ["09%03d" % i for i in range(2, 18, 1)]
    + ["13069"]
    + ("15002 15009 15010 15011 15013 15015 15016 15017 15020 15022 15023 15024 15025 15028 15029 15030 15031 "
       "15033 15034 15035 15036 15037 15038 15039 15044 15046 15050 15053 15057 15058 15059 15060 15061 15065 "
       "15068 15069 15070 15075 15081 15083 15084 15089 15091 15092 15093 15094 15095 15096 15099 15100 15102 "
       "15103 15104 15108 15109 15112 15120 15121 15122 15125").split()
)


# ------------------------------------------------------------------ descubrir URLs de la descarga masiva
def _b64(s):
    return base64.b64encode(s.encode("utf-8")).decode()


def listar_cortes(ent):
    """Cortes del DENUE de una entidad segun la API de la pagina de descarga masiva.
    Regresa {corte 'MM/AAAA': [url_zip_csv, ...]} (Edomex viene partido en 2 zips)."""
    cuerpo = {"tinfo": "6", "ag": str(int(ent)), "prog": "0", "cc": "0", "subtema": "0", "anio": "0",
              "formato": "0", "datosAbiertos": "3", "titulo": _b64("Otros|DENUE|"), "textoBuscar": "",
              "ingles": "0", "tipoInfo": "OTROS"}
    r = requests.post(f"{API}/obtenerarchivos", json=cuerpo, headers=UA, timeout=60)
    r.raise_for_status()
    cortes = {}
    for x in r.json():
        corte = x["anioInfo"].strip("|").strip()
        if not re.fullmatch(r"\d{2}/\d{4}", corte):
            continue  # cortes viejos solo con anio (2010, 2015) no sirven
        if "_csv.zip" not in x["extensiones"]:
            continue
        cortes.setdefault(corte, []).append(CONTENIDOS + x["pathLogico"] + "_csv.zip")
    return cortes


def clave_corte(c):
    mes, anio = c.split("/")
    return (int(anio), int(mes))


def resolver_urls(hist):
    """{'actual': (corte, {ent: [urls]}), 'hist': (corte, {ent: [urls]})}"""
    por_ent = {e: listar_cortes(e) for e in ENTIDADES}
    comunes = set.intersection(*[set(v) for v in por_ent.values()])
    actual = max(comunes, key=clave_corte)
    if hist not in comunes:
        raise SystemExit(f"El corte historico {hist} no existe en las 3 entidades. Disponibles: "
                         f"{sorted(comunes, key=clave_corte)}")
    return {"actual": (actual, {e: sorted(por_ent[e][actual]) for e in ENTIDADES}),
            "hist": (hist, {e: sorted(por_ent[e][hist]) for e in ENTIDADES})}


# ------------------------------------------------------------------ lectura y limpieza del DENUE
def parse_per_ocu(s):
    """'0 a 5 personas' -> (0, 5); '251 y mas personas' -> (251, NaN)."""
    mn, mx = [], []
    for v in s.fillna(""):
        m = re.match(r"\s*(\d+)\s*a\s*(\d+)", v)
        if m:
            mn.append(int(m.group(1)))
            mx.append(int(m.group(2)))
            continue
        m = re.match(r"\s*(\d+)\s*y\s*m", v)
        mn.append(int(m.group(1)) if m else np.nan)
        mx.append(np.nan)
    return np.array(mn, dtype=float), np.array(mx, dtype=float)


def limpiar(df, scian_version, corte):
    """Pasa el trozo crudo del DENUE (todo texto) a las columnas del contrato."""
    for c in df.columns:
        df[c] = df[c].str.strip()
    # el corte historico de CDMX trae las claves sin ceros a la izquierda ("9", "14", "717"): se rellenan
    for c, n in (("cve_ent", 2), ("cve_mun", 3), ("cve_loc", 4), ("ageb", 4), ("manzana", 3), ("cod_postal", 5)):
        df[c] = df[c].str.zfill(n)
    out = pd.DataFrame()
    out["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    out["nombre"] = df["nom_estab"]
    out["razon_social"] = df["raz_social"]
    out["codigo_act"] = df["codigo_act"].str.zfill(6)
    out["nombre_act"] = df["nombre_act"]
    out["per_ocu"] = df["per_ocu"]
    mn, mx = parse_per_ocu(df["per_ocu"])
    out["per_ocu_min"] = mn
    out["per_ocu_max"] = mx
    # punto medio del estrato; el estrato abierto "251 y mas" se toma como 251 (cota inferior)
    out["per_ocu_medio"] = np.where(np.isnan(mx), mn, (mn + mx) / 2)
    out["tipo_asent"] = df["tipo_asent"]
    out["nom_asent"] = df["nomb_asent"]
    out["cod_postal"] = df["cod_postal"]
    out["cve_ent"] = df["cve_ent"]
    out["cvegeo_mun"] = df["cve_ent"] + df["cve_mun"]
    out["cve_loc"] = df["cve_loc"]
    out["ageb"] = df["ageb"]
    out["manzana"] = df["manzana"]
    # cvegeo de AGEB (13 car.): ent2 + mun3 + loc4 + ageb4; vacio si el establecimiento no trae AGEB
    ok = df["cve_loc"].str.len().eq(4) & df["ageb"].str.len().eq(4)
    out["cvegeo"] = (df["cve_ent"] + df["cve_mun"] + df["cve_loc"] + df["ageb"]).where(ok)
    out["tipo_uni"] = df["tipoUniEco"]
    lat = pd.to_numeric(df["latitud"], errors="coerce")
    lon = pd.to_numeric(df["longitud"], errors="coerce")
    malo = ~(lat.between(BBOX[0], BBOX[1]) & lon.between(BBOX[2], BBOX[3]))
    out["lat"] = lat.where(~malo)
    out["lon"] = lon.where(~malo)
    out["fecha_alta"] = df["fecha_alta"]
    out["scian_version"] = scian_version
    out["corte"] = corte
    return out


def leer_zip(zpath, claves_mun, scian_version, corte):
    """Lee el CSV dentro del zip por trozos, se queda solo con los municipios de la ZMVM."""
    piezas = []
    with zipfile.ZipFile(zpath) as z:
        miembro = [n for n in z.namelist() if "conjunto_de_datos/" in n and n.lower().endswith(".csv")]
        assert len(miembro) == 1, (zpath, z.namelist())
        with z.open(miembro[0]) as f:
            usecols = lambda c: c in COLS  # noqa: E731  (hist no trae 'clee'; tampoco la leemos)
            for trozo in pd.read_csv(f, dtype=str, encoding="latin-1", usecols=usecols, chunksize=250_000):
                clave = trozo["cve_ent"].str.strip().str.zfill(2) + trozo["cve_mun"].str.strip().str.zfill(3)
                trozo = trozo[clave.isin(claves_mun)]
                if len(trozo):
                    piezas.append(limpiar(trozo.copy(), scian_version, corte))
    return pd.concat(piezas, ignore_index=True) if piezas else pd.DataFrame()


def construir_corte(nombre, corte, urls_por_ent, claves_mun, scian_version, fuentes, keep_raw):
    """Baja los zips de un corte, filtra a la ZMVM y regresa el DataFrame."""
    zips, trozos = [], []
    for ent, urls in urls_por_ent.items():
        for i, url in enumerate(urls):
            dest = RAW_DENUE / "_zip" / Path(url).name
            descargar(url, dest, fuentes, f"denue_{nombre}_{ent}_{i}", corte,
                      f"DENUE {corte}, entidad {ent}, parte {i + 1} de {len(urls)}")
            zips.append(dest)
            log("leyendo", dest.name)
            trozos.append(leer_zip(dest, set(claves_mun), scian_version, corte))
    df = pd.concat(trozos, ignore_index=True)
    antes = len(df)
    df = df.drop_duplicates("id").reset_index(drop=True)
    log(f"{nombre}: {len(df):,} establecimientos en la ZMVM ({antes - len(df)} ids repetidos descartados)")
    if not keep_raw:
        for z in zips:
            z.unlink(missing_ok=True)
    return df


# ------------------------------------------------------------------ catalogos SCIAN
NIVELES = {2: "sector", 3: "subsector", 4: "rama", 5: "subrama", 6: "clase"}


def catalogo_scian(xlsx):
    """Lee el xlsx de INEGI y regresa DataFrame(codigo, titulo, nivel). Rangos como '31-33' quedan como sector."""
    d = pd.read_excel(xlsx, header=1, dtype=str, usecols=[0, 1])
    d.columns = ["codigo", "titulo"]
    d = d.dropna(subset=["codigo"]).copy()
    d["codigo"] = d["codigo"].str.strip()
    d = d[d["codigo"].str.fullmatch(r"\d{2,6}|\d{2}-\d{2}")]
    d["titulo"] = d["titulo"].str.strip()
    # el xlsx marca con una 'T' pegada los titulos de niveles que tienen hijos (2 a 5 digitos)
    corto = d["codigo"].str.len() < 6
    d.loc[corto, "titulo"] = d.loc[corto, "titulo"].str.replace(r"(?<=[a-záéíóúñ\)\.])T$", "", regex=True)
    d["titulo"] = d["titulo"].str.strip()
    d["nivel"] = d["codigo"].map(lambda c: "sector" if "-" in c else NIVELES[len(c)])
    return d.drop_duplicates("codigo").reset_index(drop=True)


def hacer_scian(fuentes):
    """Descarga y convierte los 3 catalogos. scian.csv es el vigente (2023), el que usa el DENUE actual."""
    sal = {}
    lista = (("scian", "SCIAN 2023", URL_SCIAN_2023, "scian_2023_categorias_y_productos.xlsx"),
             ("scian_2018", "SCIAN 2018", URL_SCIAN_2018, "scian_2018_categorias_y_productos.xlsx"),
             ("scian_2013", "SCIAN 2013", URL_SCIAN_2013, "SCIAN_2013_estructura_productos.xlsx"))
    for nombre, etiqueta, url, xlsx in lista:
        ruta = descargar(url, RAW_SCIAN / xlsx, fuentes, nombre, etiqueta, "catalogo oficial INEGI (estructura y productos)")
        cat = catalogo_scian(ruta)
        cat.to_csv(PROC / f"{nombre}.csv", index=False)
        log(f"{nombre}.csv ({etiqueta}): {len(cat)} filas", cat["nivel"].value_counts().to_dict())
        sal[nombre] = cat
    return sal


def puente_hist_actual(hist, actual, cat_act, cats_hist):
    """Puente de codigos del corte historico al catalogo vigente. Con los ids que estan en los dos cortes
    (INEGI reclasifico a cada establecimiento) toma, para cada codigo historico, el codigo actual mas frecuente.
    Con menos de 3 casos usa identidad si el codigo existe en el catalogo vigente; si no, queda sin mapeo."""
    m = hist[["id", "codigo_act"]].merge(actual[["id", "codigo_act"]], on="id", suffixes=("_h", "_a"))
    g = m.groupby(["codigo_act_h", "codigo_act_a"]).size().rename("n").reset_index()
    tot = g.groupby("codigo_act_h")["n"].sum().rename("n_total")
    g = g.sort_values(["codigo_act_h", "n"], ascending=[True, False]).drop_duplicates("codigo_act_h")
    g = g.merge(tot, on="codigo_act_h")
    g["share"] = (g["n"] / g["n_total"]).round(3)
    g["metodo"] = np.where(g["n_total"] >= 3, "empirico", "pocos_casos")
    vigentes = set(cat_act["codigo"])
    g = g.rename(columns={"codigo_act_h": "codigo_hist", "codigo_act_a": "codigo_actual"})
    pocos = (g["metodo"] == "pocos_casos") & g["codigo_hist"].isin(vigentes)
    g.loc[pocos, "codigo_actual"] = g.loc[pocos, "codigo_hist"]
    g.loc[pocos, "metodo"] = "identidad"
    # codigos historicos que no aparecen en ningun id compartido
    resto = sorted(set(hist["codigo_act"].dropna()) - set(g["codigo_hist"]))
    extra = pd.DataFrame({"codigo_hist": resto})
    extra["codigo_actual"] = extra["codigo_hist"].where(extra["codigo_hist"].isin(vigentes))
    extra["metodo"] = np.where(extra["codigo_actual"].notna(), "identidad", "sin_mapeo")
    extra["n"] = 0
    extra["n_total"] = 0
    extra["share"] = np.nan
    pte = pd.concat([g, extra], ignore_index=True)
    pte.loc[pte["metodo"] == "pocos_casos", "metodo"] = "sin_mapeo"
    pte.loc[pte["metodo"] == "sin_mapeo", "codigo_actual"] = np.nan
    # titulo del codigo historico: SCIAN 2013 si existe ahi, si no 2018
    t_h = {}
    for cat in cats_hist:
        for c, t in zip(cat["codigo"], cat["titulo"]):
            t_h.setdefault(c, t)
    pte["titulo_hist"] = pte["codigo_hist"].map(t_h)
    pte["titulo_actual"] = pte["codigo_actual"].map(cat_act.set_index("codigo")["titulo"])
    pte["cambio_codigo"] = pte["codigo_hist"] != pte["codigo_actual"]
    return pte[["codigo_hist", "titulo_hist", "codigo_actual", "titulo_actual", "n", "n_total", "share", "metodo",
                "cambio_codigo"]].sort_values("codigo_hist").reset_index(drop=True)


# ------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="rehace todo aunque existan las salidas")
    ap.add_argument("--hist", default="11/2020", help="corte historico MM/AAAA (por defecto 11/2020)")
    ap.add_argument("--keep-raw", action="store_true", help="no borra los zips")
    args = ap.parse_args()

    PROC.mkdir(parents=True, exist_ok=True)
    RAW_DENUE.mkdir(parents=True, exist_ok=True)
    fuentes = cargar_fuentes()
    f_act, f_hist = PROC / "denue_actual.parquet", PROC / "denue_hist.parquet"
    f_pte = PROC / "scian_hist_a_actual.csv"

    cats = hacer_scian(fuentes)

    if args.force or not (f_act.exists() and f_hist.exists()):
        claves = municipios_zmvm()
        log(f"municipios ZMVM: {len(claves)}")
        urls = resolver_urls(args.hist)
        for nombre, f, version in (("actual", f_act, "2023 (con codigos 2018)"), ("hist", f_hist, "2013 (algunos codigos 2018)")):
            if f.exists() and not args.force:
                continue
            corte, por_ent = urls[nombre]
            log(f"== corte {nombre}: {corte}")
            df = construir_corte(nombre, corte, por_ent, claves, version, fuentes, args.keep_raw)
            df.to_parquet(f, index=False, compression="zstd")
            log("guardado", f.name, f"{f.stat().st_size / 1e6:.1f} MB")
    else:
        log("denue_actual y denue_hist ya existen (usa --force para rehacerlos)")

    act, hist = pd.read_parquet(f_act), pd.read_parquet(f_hist)
    if args.force or not f_pte.exists() or "codigo_act_actual" not in hist.columns:
        pte = puente_hist_actual(hist, act, cats["scian"], [cats["scian_2013"], cats["scian_2018"]])
        pte.to_csv(f_pte, index=False)
        hist["codigo_act_actual"] = hist["codigo_act"].map(pte.set_index("codigo_hist")["codigo_actual"])
        hist.to_parquet(f_hist, index=False, compression="zstd")
        log("puente hist -> actual:", pte["metodo"].value_counts().to_dict(),
            "| filas hist sin codigo actual:", int(hist["codigo_act_actual"].isna().sum()))
    # en el corte actual el codigo ya es el vigente
    if "codigo_act_actual" not in act.columns:
        act["codigo_act_actual"] = act["codigo_act"]
        act.to_parquet(f_act, index=False, compression="zstd")

    agregar_a_fuentes_md(fuentes)
    log("listo")


if __name__ == "__main__":
    sys.exit(main())
