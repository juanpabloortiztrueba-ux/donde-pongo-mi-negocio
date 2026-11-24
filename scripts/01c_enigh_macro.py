"""Etapa Datos C (parte 1 y 2): ENIGH 2024 NS y macro (Banxico + INEGI).

Uso (desde la raiz del repo):
    uv run python scripts/01c_enigh_macro.py            # enigh + macro
    uv run python scripts/01c_enigh_macro.py enigh      # solo ENIGH
    uv run python scripts/01c_enigh_macro.py macro      # solo macro

Salidas en data/processed/:
    enigh_gasto.parquet, enigh_decil_cortes.parquet, enigh_hogares.parquet,
    enigh_rubros.csv, enigh_claves.csv, macro.json
Idempotente: si los CSV o los parquet ya existen, no se vuelve a bajar.
Los tokens salen de .env y nunca se imprimen.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import warnings
import zipfile
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import requests

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw" / "enigh2024"
PROC = RAIZ / "data" / "processed"
UA = {"User-Agent": "Mozilla/5.0"}  # el sitio del INEGI devuelve HTML sin user-agent
BASE = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024"
ZIPS = {
    "concentradohogar": f"{BASE}/microdatos/enigh2024_ns_concentradohogar_csv.zip",
    "gastoshogar": f"{BASE}/microdatos/enigh2024_ns_gastoshogar_csv.zip",
    "gastospersona": f"{BASE}/microdatos/enigh2024_ns_gastospersona_csv.zip",
    "hogares": f"{BASE}/microdatos/enigh2024_ns_hogares_csv.zip",
    "poblacion": f"{BASE}/microdatos/enigh2024_ns_poblacion_csv.zip",
}
PDFS = {
    "catalogo_gastos.pdf": f"{BASE}/doc/enigh2024_ns_catalogo_gastos.pdf",
    "descripcion_bd.pdf": f"{BASE}/microdatos/889463924494.pdf",
}
FUENTE_ENIGH = ("INEGI, ENIGH 2024 Nueva Serie, microdatos CSV "
                "(concentradohogar, gastoshogar, gastospersona); "
                "https://www.inegi.org.mx/programas/enigh/nc/2024/")


# ---------------------------------------------------------------- utilidades
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def bajar(url: str, destino: Path, minimo: int = 100_000) -> bool:
    """Descarga si no existe. Devuelve True si bajo algo."""
    if destino.exists() and destino.stat().st_size > minimo:
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    if r.headers.get("Content-Type", "").startswith("text/html"):
        raise RuntimeError(f"El INEGI devolvio HTML en vez de archivo: {url}")
    destino.write_bytes(r.content)
    return True


# ------------------------------------------------------------- 1. descargas
def preparar_crudos() -> None:
    """Baja zips, extrae CSV y borra los zip. Baja los PDF de catalogos."""
    RAW.mkdir(parents=True, exist_ok=True)
    for nombre, url in PDFS.items():
        bajar(url, RAW / nombre)
    for nombre, url in ZIPS.items():
        csv = RAW / nombre / f"{nombre}.csv"
        if csv.exists():
            continue
        # si ya se genero el parquet delgado, los CSV de gasto no hacen falta
        if nombre.startswith("gastos") and (RAW / "gastos_delgado.parquet").exists():
            continue
        z = RAW / f"{nombre}.zip"
        bajar(url, z)
        with zipfile.ZipFile(z) as zf:
            zf.extractall(RAW / nombre)
        print(f"  {nombre}: sha256 zip {sha256(z)}")
        z.unlink()  # se borra el zip tras extraer


def gastos_delgados() -> Path:
    """gastoshogar + gastospersona -> parquet con (hogar, clave, gasto_tri)."""
    out = RAW / "gastos_delgado.parquet"
    if out.exists():
        return out
    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    def sel(n: str) -> str:
        # todo como texto y se convierte despues: hay celdas con un espacio en blanco
        return (f"SELECT folioviv, foliohog, clave, TRY_CAST(NULLIF(TRIM(gasto_tri), '') AS DOUBLE) AS gasto_tri "
                f"FROM read_csv('{RAW}/{n}/{n}.csv', header=true, all_varchar=true, sample_size=-1, "
                f"types={{'gasto_tri': 'VARCHAR'}})")
    con.execute(f"COPY ({sel('gastoshogar')} UNION ALL {sel('gastospersona')}) "
                f"TO '{out}' (FORMAT parquet, COMPRESSION zstd)")
    # los CSV de gasto pesan ~600 MB: ya no hacen falta
    for n in ("gastoshogar", "gastospersona"):
        shutil_rm(RAW / n)
    return out


def shutil_rm(p: Path) -> None:
    import shutil
    shutil.rmtree(p, ignore_errors=True)


# ------------------------------------------------- 2. catalogos desde los PDF
def _texto_pdf(ruta: Path, layout: bool = False, paginas=None) -> list[str]:
    import pypdf
    r = pypdf.PdfReader(str(ruta))
    rango = paginas if paginas is not None else range(len(r.pages))
    kw = {"extraction_mode": "layout"} if layout else {}
    return [r.pages[i].extract_text(**kw) for i in rango]


def rubros_inegi() -> dict[str, list[str]]:
    """Catalogo oficial rubro -> claves (seccion 2.4.12 de la descripcion de la BD).

    Se verifica despues contra las columnas de concentradohogar (coinciden)."""
    import pypdf
    n = len(pypdf.PdfReader(str(RAW / "descripcion_bd.pdf")).pages)
    # el catalogo de rubros esta en las ultimas paginas
    lineas = []
    for t in _texto_pdf(RAW / "descripcion_bd.pdf", layout=True, paginas=range(n - 3, n)):
        lineas += t.splitlines()
    rub: dict[str, list[str]] = {}
    blk: list[tuple[str | None, list[str]]] = []

    def cerrar():
        nonlocal blk
        nombre = None
        cl: list[str] = []
        for nm, c in blk:
            nombre = nm or nombre
            cl += c
        if nombre:
            rub[nombre] = cl
        blk = []

    en_tabla = False
    for ln in lineas:
        s = ln.strip()
        if s.startswith("2.4.12"):
            en_tabla = True
        if not en_tabla or not s or s.startswith(("Rubros", "(Contin", "2.4.12", "INEGI")):
            continue
        if re.fullmatch(r"\d{1,3}", s):  # numero de pagina
            continue
        m = re.match(r"^([a-z_]+)(?:\s+(.*))?$", s)
        nm, resto = (m.group(1), m.group(2) or "") if m else (None, s)
        if nm and any(n_ for n_, _ in blk):
            cerrar()
        blk.append((nm, re.findall(r"\b[0-9T][0-9A-Z]{3,5}\b", resto)))
        if not resto.endswith(","):  # un bloque termina en linea sin coma final
            cerrar()
    cerrar()
    return rub


def catalogo_claves() -> tuple[pd.DataFrame, dict[str, str]]:
    """Del PDF 'Catalogo para gastos del hogar': claves de 6 caracteres con su
    nombre, y titulos de division, grupo, clase y subclase (COICOP 2018)."""
    textos = _texto_pdf(RAW / "catalogo_gastos.pdf")
    # paginas de cuerpo: las que traen 'CLAVE CONCEPTO'
    lineas: list[str] = []
    for t in textos:
        if "CLAVE CONCEPTO" in t:
            lineas += t.splitlines()
    lineas = [re.sub(r"[\t ]+", " ", ln).strip() for ln in lineas]
    lineas = [ln for ln in lineas if ln and not ln.startswith(("INEGI.", "CLAVE CONCEPTO"))]
    conectores = {"y", "de", "del", "para", "con", "o", "e", "la", "el", "los", "las",
                  "en", "a", "al", "por", "sin", "no", "otros", "otras", "u", "(", "su", "sus"}
    titulos: dict[str, str] = {}
    claves: dict[str, str] = {}
    pat_clave = re.compile(r"^([0-9][0-9]{4}[0-9A-Z]) (\S.*)$")
    pat_tit = re.compile(r"^(\d\d(?:\.\d){0,3}) (\S.*)$")
    for i, ln in enumerate(lineas):
        m = pat_clave.match(ln)
        if m:
            nom = m.group(2)
            sig = lineas[i + 1] if i + 1 < len(lineas) else ""
            if nom.split()[-1].lower() in conectores and not pat_clave.match(sig) and not sig.startswith(("Incluye", "Excluye")):
                nom += " " + sig
            claves.setdefault(m.group(1), nom.split(":")[0].strip())
            continue
        m = pat_tit.match(ln)
        if m:
            cod = m.group(1).replace(".", "")
            nom = m.group(2).strip()
            sig = lineas[i + 1] if i + 1 < len(lineas) else ""
            if nom.split()[-1].lower() in conectores and not pat_tit.match(sig) and not pat_clave.match(sig):
                nom += " " + sig
            if nom.isupper():
                nom = nom.capitalize()
            titulos.setdefault(cod, re.sub(r"\s+", " ", nom))
    # el PDF parte algunas palabras ("Frut as", "t abaco"): se unen si la palabra junta aparece en el texto
    from collections import Counter
    cnt = Counter(w.lower() for ln in lineas for w in re.findall(r"[^\W\d_]+", ln))

    def reparar(txt: str) -> str:
        pal = txt.split(" ")
        out: list[str] = []
        for w in pal:
            if out:
                a, b = re.sub(r"\W", "", out[-1]).lower(), re.sub(r"\W", "", w).lower()
                if a and b and out[-1][-1].isalpha() and cnt.get(a + b, 0) >= 2 and min(cnt.get(a, 0), cnt.get(b, 0)) <= 2:
                    out[-1] += w
                    continue
            out.append(w)
        return " ".join(out)

    claves = {k: reparar(v) for k, v in claves.items()}
    titulos = {k: reparar(v) for k, v in titulos.items()}
    df = pd.DataFrame({"clave": list(claves), "nombre": list(claves.values())})
    for nivel, k in (("division", 2), ("grupo", 3), ("clase", 4), ("subclase", 5)):
        df[nivel] = df.clave.str[:k].map(titulos)
    return df, titulos


# Subrubros curados: slug -> (nombre, claves). Las claves son de la ENIGH 2024 NS (COICOP 2018).
CURADOS: dict[str, tuple[str, list[str]]] = {
    "ali_fuera_total": ("Alimentos y bebidas consumidos fuera del hogar (restaurantes y comida preparada)",
                        ["111111", "111112", "111113", "111114", "111115", "111116",
                         "111121", "111122", "111123", "111124", "111125", "111126"]),
    "restaurante_comidas": ("Desayunos, comidas, cenas y entrecomidas fuera del hogar", ["111111", "111112", "111113", "111114"]),
    "comida_rapida": ("Comida rapida: hamburguesas y hot dogs, pizzas, pollos rostizados", ["111123", "111125", "111126"]),
    "antojitos_tacos": ("Barbacoa/birria, carnitas y otros alimentos cocinados (tacos, tamales, sopes)", ["111121", "111122", "111124"]),
    "helados": ("Helados, nieves y paletas de hielo (consumo en casa)", ["011861"]),
    "cafe_bebidas": ("Cafe soluble, en grano o molido y preparaciones a base de cafe", ["012201", "012202", "012203"]),
    "chocolate_cacao": ("Chocolate y cacao", ["011851", "011852", "011853", "181155"]),
    "pan_pasteles": ("Pan, pan dulce a granel y pasteles frescos (panaderia y pasteleria)", ["011133", "011137", "011139"]),
    "dulces_golosinas": ("Dulces y golosinas", ["011891"]),
    "consulta_medica": ("Consultas medicas, homeopaticas y de medicina tradicional",
                        ["062191", "062192", "062193", "062194", "062195", "062196", "062197", "062198"]),
    "dental": ("Servicios dentales (consultas, ortodoncia, protesis)", ["062210", "062291", "062292"]),
    "peluqueria_estetica": ("Corte de cabello, permanentes, tintes, pedicura y manicura", ["131311", "131312", "131313"]),
    "gimnasio_deporte": ("Cursos y espacios deportivos, clubes y cuotas deportivas",
                         ["094621", "094622", "094623", "094624", "094625"]),
    "veterinaria_mascotas": ("Veterinaria y otros servicios para mascotas", ["094501", "094502"]),
    "papeleria": ("Papeleria, cuadernos, utiles escolares y material impreso",
                  ["097401", "097402", "097403", "097404", "097405", "097406", "097407", "097408", "097301", "097302"]),
    "libros_revistas": ("Libros, periodicos y revistas",
                        ["097111", "097112", "097113", "097191", "097192", "097193", "097194", "097210", "097220"]),
    "lavanderia_ropa": ("Limpieza, reparacion, confeccion y alquiler de ropa", ["031420"]),
    "cursos_recreativos": ("Cursos de formacion recreativa (pintura, musica, baile)", ["094611"]),
    "eventos_espectaculos": ("Cines, teatros, conciertos y espectaculos", ["096101", "096102", "096103", "096104", "096105",
                                                                        "096201", "096202", "094630"]),
}


# ------------------------------------------------------- 3. hogares y deciles
def _anios_esc(nivel: pd.Series, grado: pd.Series, antec: pd.Series) -> pd.Series:
    """Anios de escolaridad aprox. (convencion SEP/INEGI) con nivelaprob, gradoaprob y antec_esc."""
    n = pd.to_numeric(nivel, errors="coerce")
    g = pd.to_numeric(grado, errors="coerce").fillna(0)
    a = pd.to_numeric(antec, errors="coerce")
    base_antec = a.map({1: 6, 2: 9, 3: 12, 4: 16, 5: 18}).fillna(9)
    y = pd.Series(np.nan, index=nivel.index)
    y[n == 0] = 0
    y[n == 1] = 0
    y[n == 2] = g[n == 2].clip(upper=6)
    y[n == 3] = 6 + g[n == 3].clip(upper=3)
    y[n == 4] = 9 + g[n == 4].clip(upper=3)
    m = n.isin([5, 6])
    y[m] = base_antec[m] + g[m].clip(upper=4)
    y[n == 7] = 12 + g[n == 7].clip(upper=6)
    y[n == 8] = 17 + g[n == 8].clip(upper=3)
    y[n == 9] = 17 + g[n == 9].clip(upper=3)
    y[n == 10] = 19 + g[n == 10].clip(upper=4)
    return y.clip(upper=24)


def decil_ponderado(ing: pd.Series, w: pd.Series) -> pd.Series:
    """Deciles de hogares por ingreso corriente: se ordena por ingreso y se corta
    el factor de expansion acumulado en 10 partes iguales (metodo del INEGI)."""
    orden = ing.sort_values(kind="mergesort").index
    acum = w.loc[orden].cumsum()
    d = np.ceil(acum / w.sum() * 10 - 1e-9).clip(1, 10).astype(int)
    return d.reindex(ing.index)


def zmvm_cvegeo() -> set[str] | None:
    p = PROC / "zmvm_municipios.csv"
    if not p.exists():
        return None
    z = pd.read_csv(p, dtype=str)
    return set(z["cvegeo_mun"])


def cargar_hogares() -> pd.DataFrame:
    """Una fila por hogar con ingreso, factor y rasgos del hogar."""
    c = pd.read_csv(RAW / "concentradohogar" / "concentradohogar.csv",
                    dtype={"folioviv": str, "foliohog": str, "ubica_geo": str, "est_dis": str,
                           "upm": str, "educa_jefe": str})
    h = pd.read_csv(RAW / "hogares" / "hogares.csv", dtype=str,
                    usecols=["folioviv", "foliohog", "celular", "conex_inte", "num_auto", "num_van",
                             "num_pick", "num_compu", "num_lap", "num_table"])
    p = pd.read_csv(RAW / "poblacion" / "poblacion.csv", dtype=str,
                    usecols=["folioviv", "foliohog", "parentesco", "nivelaprob", "gradoaprob", "antec_esc"])
    jefe = p[p.parentesco == "101"].drop_duplicates(["folioviv", "foliohog"]).copy()
    jefe["esc_jefe_anios"] = _anios_esc(jefe.nivelaprob, jefe.gradoaprob, jefe.antec_esc)
    llave = ["folioviv", "foliohog"]
    c = c.merge(h, on=llave, how="left").merge(jefe[llave + ["esc_jefe_anios"]], on=llave, how="left")
    num = lambda s: pd.to_numeric(s, errors="coerce").fillna(0)  # noqa: E731
    c["tiene_auto"] = (num(c.num_auto) + num(c.num_van) + num(c.num_pick)) > 0
    c["tiene_internet"] = c.conex_inte == "1"
    c["tiene_pc"] = (num(c.num_compu) + num(c.num_lap) + num(c.num_table)) > 0
    c["tiene_celular"] = c.celular == "1"
    c["entidad"] = c.ubica_geo.str[:2]
    c["cve_mun"] = c.ubica_geo
    c["urbano"] = c.tam_loc <= 3  # localidades de 2,500 habitantes o mas
    return c.copy()  # desfragmenta el DataFrame


def ambitos(c: pd.DataFrame) -> dict[str, pd.Series]:
    """Mascaras booleanas por ambito. Todos son urbanos (tam_loc 1 a 3)."""
    u = c.urbano
    out = {
        "nacional_urbano": u,
        "cdmx": u & (c.entidad == "09"),
        "edomex": u & (c.entidad == "15"),
    }
    z = zmvm_cvegeo()
    if z:
        out["zmvm"] = u & c.cve_mun.isin(z)
    return out


# ------------------------------------------------------------ 4. calculo
def media_pond(x: np.ndarray, w: np.ndarray, g: np.ndarray, k: int = 10) -> np.ndarray:
    """Media ponderada por grupo g (1..k). Incluye los ceros."""
    sw = np.bincount(g, weights=w, minlength=k + 1)[1:]
    sx = np.bincount(g, weights=w * x, minlength=k + 1)[1:]
    return np.divide(sx, sw, out=np.full(k, np.nan), where=sw > 0)


def construir_enigh() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    preparar_crudos()
    gpath = gastos_delgados()
    c = cargar_hogares()
    rub_pdf = rubros_inegi()
    claves_df, titulos = catalogo_claves()

    # deciles por ambito
    amb = ambitos(c)
    c["decil_nac_urbano"] = np.nan
    mu = amb["nacional_urbano"]
    c.loc[mu, "decil_nac_urbano"] = decil_ponderado(c.loc[mu, "ing_cor"], c.loc[mu, "factor"])
    c = c.reset_index(drop=True)
    idx = {k: np.where(v.values)[0] for k, v in amb.items()}
    decil_amb = {}
    for k, ii in idx.items():
        s = c.iloc[ii]
        decil_amb[k] = decil_ponderado(s.ing_cor.reset_index(drop=True), s.factor.reset_index(drop=True)).values

    # --- enigh_hogares
    cols_h = ["folioviv", "foliohog", "entidad", "cve_mun", "tam_loc", "factor", "ing_cor", "esc_jefe_anios",
              "tiene_auto", "tiene_internet", "tiene_pc", "tiene_celular", "tot_integ", "edad_jefe", "sexo_jefe",
              "est_dis", "upm", "decil_nac_urbano"]
    partes = []
    for k, ii in idx.items():
        s = c.iloc[ii][cols_h].copy()
        s.insert(3, "ambito", k)
        s.insert(6, "decil", decil_amb[k])
        partes.append(s)
    hog = pd.concat(partes, ignore_index=True)
    hog["decil"] = hog["decil"].astype("int8")
    hog["decil_nac_urbano"] = hog["decil_nac_urbano"].astype("int8")
    hog = hog.rename(columns={"cve_mun": "cvegeo_mun"})
    hog.to_parquet(PROC / "enigh_hogares.parquet", index=False)
    print("enigh_hogares:", hog.shape, hog.groupby("ambito").size().to_dict())

    # --- enigh_decil_cortes
    filas = []
    for k, ii in idx.items():
        s = c.iloc[ii].reset_index(drop=True)
        s["decil"] = decil_amb[k]
        for d, g in s.groupby("decil"):
            w = g.factor.to_numpy()
            wm = lambda col: float(np.average(g[col].astype(float), weights=w))  # noqa: E731
            filas.append(dict(
                ambito=k, decil=int(d), hogares_muestra=len(g), hogares_expandidos=float(w.sum()),
                ing_cor_trim_prom=wm("ing_cor"), ing_cor_mensual_prom=wm("ing_cor") / 3,
                ing_cor_trim_min=float(g.ing_cor.min()), ing_cor_trim_max=float(g.ing_cor.max()),
                esc_jefe_anios_prom=float(np.average(g.esc_jefe_anios.fillna(g.esc_jefe_anios.mean()), weights=w)),
                pct_auto=100 * wm("tiene_auto"), pct_internet=100 * wm("tiene_internet"),
                pct_pc=100 * wm("tiene_pc"), pct_celular=100 * wm("tiene_celular"),
                tot_integ_prom=wm("tot_integ"), fuente=FUENTE_ENIGH))
    cortes = pd.DataFrame(filas)
    cortes.to_parquet(PROC / "enigh_decil_cortes.parquet", index=False)
    print("enigh_decil_cortes:", cortes.shape)

    # --- gasto por hogar: rubros oficiales + curados + niveles COICOP
    g = pd.read_parquet(gpath).dropna(subset=["gasto_tri"])
    g = g[g.gasto_tri > 0]
    pos = pd.Series(np.arange(len(c)), index=pd.MultiIndex.from_frame(c[["folioviv", "foliohog"]]))
    g["i"] = pos.reindex(pd.MultiIndex.from_frame(g[["folioviv", "foliohog"]])).values
    g = g.dropna(subset=["i"])
    g["i"] = g["i"].astype(int)
    N = len(c)

    def vec_por_claves(claves) -> np.ndarray:
        s = g[g.clave.isin(claves)].groupby("i").gasto_tri.sum()
        v = np.zeros(N)
        v[s.index.values] = s.values
        return v

    catalogo: list[dict] = []   # rubros: clave, nombre, nivel, definicion
    vectores: dict[str, np.ndarray] = {}

    # a) rubros oficiales del INEGI (columnas de concentradohogar) y sus agregados
    etiquetas = {
        "gasto_mon": "Gasto corriente monetario", "alimentos": "Alimentos, bebidas y tabaco",
        "ali_dentro": "Alimentos dentro del hogar", "ali_fuera": "Alimentos fuera del hogar (INEGI: desayunos, comidas, cenas, entrecomidas y eventos)",
        "bebidas": "Bebidas alcoholicas y no alcoholicas", "tabaco": "Tabaco",
        "cereales": "Cereales", "carnes": "Carnes", "pescado": "Pescados y mariscos", "leche": "Leche y derivados",
        "huevo": "Huevo", "aceites": "Aceites y grasas", "tuberculo": "Tuberculos", "verduras": "Verduras, legumbres y semillas",
        "frutas": "Frutas", "azucar": "Azucar y mieles", "cafe": "Cafe, te y chocolate (consumo en casa)",
        "especias": "Especias y aderezos", "otros_alim": "Otros alimentos diversos (incluye comida preparada y helados)",
        "vesti_calz": "Vestido y calzado", "vestido": "Vestido", "calzado": "Calzado",
        "vivienda": "Vivienda y servicios de conservacion", "alquiler": "Alquiler de vivienda", "pred_cons": "Predial y servicios de conservacion",
        "agua": "Agua", "energia": "Energia electrica y combustibles de la vivienda",
        "limpieza": "Limpieza y cuidados de la casa", "cuidados": "Cuidados de la casa (limpieza)",
        "utensilios": "Utensilios domesticos", "enseres": "Enseres domesticos y mantenimiento",
        "salud": "Salud", "ambul_serv": "Servicios medicos ambulatorios", "aten_hosp": "Atencion hospitalaria",
        "medic_prod": "Medicamentos y productos medicos (farmacia)",
        "transporte": "Transporte", "publico": "Transporte publico", "foraneo": "Transporte foraneo",
        "adqui_vehi": "Compra de vehiculos", "mantenim": "Mantenimiento de vehiculos", "refaccion": "Refacciones y accesorios de vehiculos",
        "combus": "Combustibles", "comunica": "Comunicaciones",
        "educa_espa": "Educacion y esparcimiento", "educacion": "Educacion", "esparci": "Esparcimiento",
        "paq_turist": "Paquetes turisticos y hospedaje", "personales": "Cuidados y accesorios personales",
        "cuida_pers": "Cuidados personales", "acces_pers": "Accesorios y efectos personales",
        "otros_gas": "Otros gastos diversos", "transf_gas": "Transferencias de gasto",
    }
    for col, nom in etiquetas.items():
        if col in c.columns:
            vectores[col] = c[col].fillna(0).to_numpy(float)
            catalogo.append(dict(rubro_clave=col, rubro_nombre=nom, nivel="rubro_inegi",
                                 definicion="Columna de concentradohogar ENIGH 2024 NS"))
    # control: los rubros reconstruidos desde las claves deben dar lo mismo que concentradohogar
    ctrl = []
    for r, cl in rub_pdf.items():
        if r in c.columns and r in ("ali_fuera", "cafe", "medic_prod", "educacion", "esparci", "cuida_pers", "vesti_calz"):
            v = vec_por_claves(cl)
            ctrl.append((r, float(np.abs(v - c[r].fillna(0).to_numpy()).max())))
    if "vesti_calz" in rub_pdf or True:
        v = vec_por_claves(rub_pdf["vestido"] + rub_pdf["calzado"])
        ctrl.append(("vesti_calz", float(np.abs(v - c["vesti_calz"].to_numpy()).max())))
    print("control claves vs concentrado (max diferencia por hogar, pesos):", ctrl)

    # b) subrubros curados
    for slug, (nom, cl) in CURADOS.items():
        vectores[slug] = vec_por_claves(cl)
        catalogo.append(dict(rubro_clave=slug, rubro_nombre=nom, nivel="curado",
                             definicion="Claves ENIGH: " + ", ".join(cl)))
    # c) niveles COICOP: clase (4), subclase (5) y clave (6) solo de la division 11 (restaurantes)
    for k, nivel in ((4, "coicop_clase"), (5, "coicop_subclase"), (6, "coicop_clave")):
        gp = g.assign(p=g.clave.str[:k])
        if k == 6:
            gp = gp[gp.clave.str.startswith("11")]
        for p, sub in gp.groupby("p"):
            if len(p) < k:
                continue
            s = sub.groupby("i").gasto_tri.sum()
            if len(s) < 30:  # casi nadie lo reporta: no es util
                continue
            v = np.zeros(N)
            v[s.index.values] = s.values
            clave = f"coicop_{p}"
            nom = titulos.get(p) if k < 6 else dict(zip(claves_df.clave, claves_df.nombre)).get(p)
            vectores[clave] = v
            catalogo.append(dict(rubro_clave=clave, rubro_nombre=nom or f"Clave {p} (sin nombre en el catalogo del INEGI)", nivel=nivel,
                                 definicion=f"Suma de claves que empiezan con {p}"))

    # d) promedios ponderados por ambito y decil
    w_all = c.factor.to_numpy(float)
    filas = []
    nombres = {d["rubro_clave"]: d["rubro_nombre"] for d in catalogo}
    for k, ii in idx.items():
        gdec = decil_amb[k]
        w = w_all[ii]
        hog_exp = np.bincount(gdec, weights=w, minlength=11)[1:]
        n_m = np.bincount(gdec, minlength=11)[1:]
        for rc, v in vectores.items():
            x = v[ii]
            m = media_pond(x, w, gdec)
            pc = 100 * media_pond((x > 0).astype(float), w, gdec)
            for d in range(10):
                filas.append((k, d + 1, rc, nombres[rc], m[d], hog_exp[d], int(n_m[d]), pc[d], FUENTE_ENIGH))
    gasto = pd.DataFrame(filas, columns=["ambito", "decil", "rubro_clave", "rubro_nombre", "gasto_trim_prom_hogar",
                                         "hogares_expandidos", "hogares_muestra", "pct_hogares_con_gasto", "fuente"])
    gasto["decil"] = gasto["decil"].astype("int8")
    gasto.to_parquet(PROC / "enigh_gasto.parquet", index=False)
    pd.DataFrame(catalogo).to_csv(PROC / "enigh_rubros.csv", index=False)
    claves_df.to_csv(PROC / "enigh_claves.csv", index=False)
    print("enigh_gasto:", gasto.shape, "rubros:", len(vectores))


# ------------------------------------------------------------------ macro
BANXICO = "https://www.banxico.org.mx/SieAPIRest/service/v1"
INEGI_API = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"


def _cargar_tokens() -> tuple[str, str]:
    from dotenv import load_dotenv
    load_dotenv(RAIZ / ".env")
    bx, ig = os.environ.get("BANXICO_TOKEN"), os.environ.get("INEGI_TOKEN")
    if not bx or not ig:
        sys.exit("Faltan BANXICO_TOKEN o INEGI_TOKEN en .env")
    return bx, ig


class _Limpio:
    """Evita que un token se cuele en mensajes de error."""
    def __init__(self, *secretos: str):
        self.sec = [s for s in secretos if s]

    def __call__(self, txt: str) -> str:
        for s in self.sec:
            txt = txt.replace(s, "***")
        return txt


def _fecha_bx(s: str) -> str:
    return dt.datetime.strptime(s, "%d/%m/%Y").date().isoformat()


def _periodo_inegi(p: str) -> str:
    return p.replace("/", "-")


def construir_macro() -> None:
    bx, ig = _cargar_tokens()
    limpiar = _Limpio(bx, ig)
    hoy = dt.date.today()
    H = {"Bmx-Token": bx, "Accept": "application/json"}

    def get_json(url: str, headers=None):
        try:
            r = requests.get(url, headers=headers, timeout=60)
        except requests.RequestException as e:
            raise RuntimeError(limpiar(f"{type(e).__name__}: {e}")) from None
        if r.status_code != 200:
            raise RuntimeError(limpiar(f"HTTP {r.status_code}: {r.text[:150]}"))
        return r.json()

    # ---------- Banxico SIE: se consulta el titulo y luego el dato mas reciente
    def banxico(serie: str, esperado: str, clave_unidad: str) -> dict:
        meta = get_json(f"{BANXICO}/series/{serie}", H)["bmx"]["series"][0]
        titulo = " ".join(meta["titulo"].split())
        if esperado.lower() not in titulo.lower():
            raise RuntimeError(f"Banxico {serie}: el titulo '{titulo}' no contiene '{esperado}'")
        d = get_json(f"{BANXICO}/series/{serie}/datos/oportuno", H)["bmx"]["series"][0]["datos"][0]
        return dict(valor=float(d["dato"].replace(",", "")), unidad=clave_unidad, fecha=_fecha_bx(d["fecha"]),
                    id_serie=serie, titulo_serie=titulo, periodicidad=meta.get("periodicidad"),
                    fuente=f"Banco de Mexico, SIE API (serie {serie}); https://www.banxico.org.mx/SieInternet/",
                    consultado=hoy.isoformat())

    macro: dict = {}
    macro["tasa_objetivo"] = banxico("SF61745", "Tasa objetivo", "% anual")
    macro["tiie_28"] = banxico("SF43783", "TIIE a 28", "% anual")
    macro["tipo_cambio_fix"] = banxico("SF43718", "FIX", "MXN por USD")
    rem = banxico("SE27803", "Remesas Familiares Total", "millones de USD (mensual)")
    # variacion anual y suma de 12 meses con los ultimos 26 meses
    f0 = (dt.date.fromisoformat(rem["fecha"]) - dt.timedelta(days=800)).isoformat()
    ds = get_json(f"{BANXICO}/series/SE27803/datos/{f0}/{rem['fecha']}", H)["bmx"]["series"][0]["datos"]
    ser = {_fecha_bx(x["fecha"])[:7]: float(x["dato"].replace(",", "")) for x in ds if x["dato"] not in ("N/E", "")}
    per = rem["fecha"][:7]
    ant = f"{int(per[:4]) - 1}{per[4:]}"
    if ant in ser:
        rem["variacion_anual_pct"] = round((ser[per] / ser[ant] - 1) * 100, 2)
    meses = sorted(ser)[-12:]
    if len(meses) == 12:
        rem["acumulado_12_meses_millones_usd"] = round(sum(ser[m] for m in meses), 1)
    macro["remesas"] = rem

    # ---------- INEGI: API de indicadores (BIE-BISE). Se valida la descripcion de cada id.
    def inegi_catalogo(i: str) -> str:
        j = get_json(f"{INEGI_API}/CL_INDICATOR/{i}/es/BIE-BISE/2.0/{ig}?type=json")
        return " ".join(j["CODE"][0]["Description"].split())

    def inegi_serie(i: str, esperado: str, completa: bool = False):
        desc = inegi_catalogo(i)
        if esperado.lower() not in desc.lower():
            raise RuntimeError(f"INEGI {i}: la descripcion '{desc}' no contiene '{esperado}'")
        j = get_json(f"{INEGI_API}/INDICATOR/{i}/es/00/{'false' if completa else 'true'}/BIE-BISE/2.0/{ig}?type=json")
        s = j["Series"][0]
        obs = [o for o in s["OBSERVATIONS"] if o["OBS_VALUE"] not in (None, "")]
        return desc, s, obs

    def inegi_ultimo(i: str, esperado: str, unidad: str, extra: dict | None = None) -> dict:
        desc, s, obs = inegi_serie(i, esperado)
        o = obs[0]
        d = dict(valor=round(float(o["OBS_VALUE"]), 4), unidad=unidad, fecha=_periodo_inegi(o["TIME_PERIOD"]),
                 id_serie=i, descripcion_serie=desc,
                 fuente=f"INEGI, Banco de Indicadores API (BIE, id {i}); https://www.inegi.org.mx/app/indicadores/",
                 consultado=hoy.isoformat())
        d.update(extra or {})
        return d

    def inegi_hist(i: str) -> dict[str, float]:
        _, _, obs = inegi_serie(i, "", completa=True)
        return {o["TIME_PERIOD"]: float(o["OBS_VALUE"]) for o in obs}

    # INPC general: indice base 2018=100 y su variacion anual (se verifica contra el calculo propio)
    idx = inegi_hist("910392")
    ult = max(idx)
    y, m = ult.split("/")
    var_calc = round((idx[ult] / idx[f"{int(y) - 1}/{m}"] - 1) * 100, 2)
    inpc = inegi_ultimo("910406", "Índice general", "% variacion anual",
                        dict(id_indice="910392", indice_base_2018=round(idx[ult], 3),
                             verificacion=f"variacion anual recalculada desde el indice 910392: {var_calc}%"))
    if abs(inpc["valor"] - var_calc) > 0.02:
        raise RuntimeError("INPC: la variacion anual publicada no coincide con el indice")
    macro["inpc_general_var_anual"] = inpc

    # INPC alimentos: el subindice 'Alimentos, bebidas y tabaco' NO se encontro en la API (busqueda del 2026-11-23,
    # ver `evidencia` abajo). Se entregan proxies oficiales, claramente marcados.
    prox = {}
    for nombre, idx_id, var_id, esperado in (
            ("no_subyacente_agropecuarios", "910397", "910411", "Agropecuarios"),
            ("subyacente_mercancias", "910394", "910408", "Mercancías")):
        h = inegi_hist(idx_id)
        u = max(h)
        yy, mm = u.split("/")
        calc = round((h[u] / h[f"{int(yy) - 1}/{mm}"] - 1) * 100, 2)
        v = inegi_ultimo(var_id, esperado, "% variacion anual", dict(id_indice=idx_id))
        if abs(v["valor"] - calc) > 0.02:
            raise RuntimeError(f"INPC {nombre}: no coincide con el indice")
        prox[nombre] = v
    macro["inpc_alimentos_var_anual"] = dict(
        estado="NO ENCONTRADO",
        detalle=("El subindice de INPC 'Alimentos, bebidas y tabaco' (por objeto del gasto) no se encontro en la API de "
                 "indicadores del INEGI ni en el SIE de Banxico. Ver evidencia y proxies."),
        evidencia=("Busqueda del 2026-11-23 (la API no tiene buscador por texto: se consulto la descripcion de cada id). "
                   "INEGI BIE-BISE: ids 910000-911200 y 628100-628300 son solo el INPC por componente (general, subyacente, "
                   "mercancias, servicios, no subyacente, agropecuarios, energeticos) y otras series ajenas; no hay "
                   "descomposicion de alimentos. Banxico SIE: SP1 es solo el indice general por objeto del gasto; "
                   "SP30000-SP31500 son genericos y subgrupos de ciudades/regiones (p. ej. 1.1 Alimentos > Carnes > Chuleta), sin el "
                   "total «Alimentos, bebidas y tabaco»; SP74400-SP74900 solo trae subyacente/no subyacente "
                   "(SP74625-SP74640: mercancias, mercancias no alimenticias, servicios, energeticos) sin su contraparte alimenticia."),
        proxies=prox, consultado=hoy.isoformat(),
        fuente="INEGI, Banco de Indicadores API; Banco de Mexico, SIE API (busqueda por ids)")

    # Confianza del consumidor (ENCO, INEGI-Banxico)
    macro["confianza_consumidor"] = inegi_ultimo(
        "454168", "confianza del consumidor", "puntos (indice)",
        dict(nota="Serie 454168 del BIE tal cual; no se verifico si es desestacionalizada."))

    # Consumo privado: IMCP total (indice de volumen 2018=100, cifras originales) y su variacion anual
    imcp = inegi_hist("740933")
    ui = max(imcp)
    yy, mm = ui.split("/")
    calc = round((imcp[ui] / imcp[f"{int(yy) - 1}/{mm}"] - 1) * 100, 2)
    cp = inegi_ultimo("740946", "Total", "% variacion anual (cifras originales)",
                      dict(id_indice="740933", indice_volumen_2018=round(imcp[ui], 2),
                           verificacion=(f"variacion anual recalculada desde el indice 740933: {calc}%; "
                                         "ids confirmados contra el boletin IMCP de INEGI (imcpmi2026_08.pdf)")))
    if abs(cp["valor"] - calc) > 0.02:
        raise RuntimeError("IMCP: la variacion anual publicada no coincide con el indice")
    macro["consumo_privado"] = cp

    macro["_meta"] = dict(generado=hoy.isoformat(), script="scripts/01c_enigh_macro.py macro",
                          nota="Cada indicador trae id_serie, fuente y fecha del dato. Los valores son los ultimos disponibles.")
    PROC.mkdir(parents=True, exist_ok=True)
    (PROC / "macro.json").write_text(json.dumps(macro, ensure_ascii=False, indent=2), encoding="utf-8")
    print("macro.json:", {k: (v.get("valor"), v.get("fecha")) for k, v in macro.items() if k != "_meta"})


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if cmd in ("todo", "enigh"):
        construir_enigh()
    if cmd in ("todo", "macro"):
        construir_macro()


if __name__ == "__main__":
    main()
