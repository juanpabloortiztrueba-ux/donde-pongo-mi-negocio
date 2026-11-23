"""Etapa RAG F: genera las carpetas de informacion que se escriben con codigo.

Genera (los textos a mano de carpetas/ no se tocan):
  carpetas/03_municipios/    una ficha por municipio (76) + resumen comparativo
  carpetas/02_macro/         contexto macro desde data/processed/macro.json
  carpetas/01_metodologia/enigh_zmvm_deciles.md
  carpetas/06_giros/         catalogo de giros desde config/giros.yaml
  carpetas/05_modelo/        explicacion del modelo (lee reports/validacion.md si existe)

Uso: uv run python scripts/04a_carpetas.py [--solo municipios|macro|enigh|giros|modelo]
Idempotente: reescribe siempre. Tarda unos 20 s. No usa Ollama ni tokens.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
CARP = RAIZ / "carpetas"
HOY = date.today().isoformat()

FUENTE_CENSO = "INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana)"
FUENTE_DENUE = "INEGI, DENUE (corte 05/2026; historico 11/2020)"


# ---------- utilidades ----------
def sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def slug(s: str) -> str:
    s = sin_acentos(s).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def n0(x) -> str:
    """Entero con separador de miles (coma)."""
    return "NO ENCONTRADO" if x is None or pd.isna(x) else f"{x:,.0f}"


def n1(x) -> str:
    return "NO ENCONTRADO" if x is None or pd.isna(x) else f"{x:,.1f}"


def pct(x) -> str:
    return "NO ENCONTRADO" if x is None or pd.isna(x) else f"{x:.1f} %"


def escribe(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto.rstrip() + "\n", encoding="utf-8")


def pmedia(valores: pd.Series, pesos: pd.Series):
    """Media ponderada ignorando NaN; NaN si no hay datos."""
    m = valores.notna() & pesos.notna() & (pesos > 0)
    if not m.any():
        return np.nan
    return float(np.average(valores[m], weights=pesos[m]))


def mediana_pond(valores: pd.Series, pesos: pd.Series):
    m = valores.notna() & pesos.notna() & (pesos > 0)
    if not m.any():
        return np.nan
    v, w = valores[m].to_numpy(float), pesos[m].to_numpy(float)
    o = np.argsort(v)
    c = np.cumsum(w[o])
    return float(v[o][np.searchsorted(c, c[-1] / 2)])


def tabla_md(cab: list[str], filas: list[list]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(out)


# ---------- catalogos ----------
def cargar_scian() -> tuple[dict, dict]:
    """(titulo por codigo, titulo de sector por prefijo de 2 digitos)."""
    sc = pd.read_csv(PROC / "scian.csv", dtype=str)
    titulo = dict(zip(sc["codigo"], sc["titulo"]))
    sector = {}
    for cod, t in titulo.items():
        if "-" in cod:  # '31-33', '48-49'
            a, b = cod.split("-")
            for k in range(int(a), int(b) + 1):
                sector[str(k)] = t
        elif len(cod) == 2:
            sector[cod] = t
    return titulo, sector


def cargar_giros() -> list[dict]:
    return yaml.safe_load(open(RAIZ / "config" / "giros.yaml", encoding="utf-8"))["giros"]


def mascara_giro(den: pd.DataFrame, g: dict) -> np.ndarray:
    """Establecimientos del giro: clases `scian` + clases con filtro por nombre (ver BITACORA, Giros G)."""
    m = den["codigo_act"].isin(g.get("scian") or []).to_numpy().copy()
    for f in g.get("scian_con_filtro") or []:
        en = den["codigo_act"].isin(f["codigos"]).to_numpy()
        if en.any():
            nom = den["nombre"].fillna("").to_numpy()
            rx = re.compile(f["nombre_regex"], re.I)
            cand = np.flatnonzero(en)
            hit = np.fromiter((bool(rx.search(nom[i])) for i in cand), bool, len(cand))
            m[cand[hit]] = True
    return m


# ---------- municipios ----------
def generar_municipios() -> None:
    feat = pd.read_parquet(PROC / "agebs_features.parquet").drop(columns="geometry")
    mun = pd.read_csv(PROC / "zmvm_municipios.csv", dtype={"cve_ent": str, "cve_mun": str, "cvegeo_mun": str})
    feat["cvegeo_mun"] = feat["cve_ent"] + feat["cve_mun"]
    den = pd.read_parquet(PROC / "denue_actual.parquet", columns=["codigo_act", "nombre", "cvegeo_mun"])
    hist = pd.read_parquet(PROC / "denue_hist.parquet", columns=["cvegeo_mun"])
    titulo, sector = cargar_scian()
    giros = cargar_giros()

    # conteos por giro y municipio (40 giros)
    cuentas = {}
    for g in giros:
        m = mascara_giro(den, g)
        cuentas[g["clave"]] = den.loc[m, "cvegeo_mun"].value_counts()
    giro_mun = pd.DataFrame(cuentas).reindex(mun["cvegeo_mun"]).fillna(0).astype(int)

    n_den = den["cvegeo_mun"].value_counts()
    n_hist = hist["cvegeo_mun"].value_counts()
    den["sector"] = den["codigo_act"].str[:2]
    top_clase = den.groupby(["cvegeo_mun", "codigo_act"]).size().rename("n").reset_index()
    top_sector = den.groupby(["cvegeo_mun", "sector"]).size().rename("n").reset_index()

    # indicadores por municipio
    filas = []
    for _, r in mun.iterrows():
        k = r["cvegeo_mun"]
        d = feat[feat["cvegeo_mun"] == k]
        pob = d["pob_total"].sum()
        area = d["area_km2"].sum()
        nse_pob = d.groupby("nse", observed=True)["pob_total"].sum()
        sin_nse = d.loc[d["nse"].isna(), "pob_total"].sum()
        ge = d["gasto_pot_ali_fuera_total_trim"].sum(min_count=1)
        hog_ge = d.loc[d["gasto_pot_ali_fuera_total_trim"].notna(), "hogares"].sum()
        filas.append(dict(
            cvegeo_mun=k, nom_mun=r["nom_mun"], nom_ent=r["nom_ent"], n_ageb=len(d), pob=pob,
            hogares=d["hogares"].sum(), area=area, dens=pob / area if area else np.nan,
            esc=pmedia(d["escolaridad_prom"], d["pob_total"]),
            auto=pmedia(d["pct_viv_auto"], d["viviendas_habitadas"]),
            internet=pmedia(d["pct_viv_internet"], d["viviendas_habitadas"]),
            p014=d["pob_0_14"].sum() / pob * 100, p1524=d["pob_15_24"].sum() / pob * 100,
            p2559=d["pob_25_59"].sum() / pob * 100, p60=d["pob_60_mas"].sum() / pob * 100,
            nse_bajo=nse_pob.get("bajo", 0) / pob * 100, nse_medio=nse_pob.get("medio", 0) / pob * 100,
            nse_alto=nse_pob.get("alto", 0) / pob * 100, nse_sin=sin_nse / pob * 100,
            decil_med=mediana_pond(d["decil_imputado"].astype(float), d["pob_total"]),
            n_den=int(n_den.get(k, 0)), n_hist=int(n_hist.get(k, 0)),
            den_1000=n_den.get(k, 0) / pob * 1000,
            diurna=d["pob_diurna"].sum(),
            gasto_fuera=ge, gasto_fuera_hog=(ge / hog_ge if hog_ge else np.nan),
            pob_1km_est=d.loc[d["dist_estacion_m"] <= 1000, "pob_total"].sum() / pob * 100,
        ))
    ind = pd.DataFrame(filas).set_index("cvegeo_mun")
    for c in ["pob", "dens", "den_1000", "gasto_fuera_hog", "esc"]:
        ind["rk_" + c] = ind[c].rank(ascending=False, method="min")

    out_dir = CARP / "03_municipios"
    for f in out_dir.glob("[0-9]*.md"):  # solo las fichas; no toca otros archivos
        f.unlink()

    for k, r in ind.iterrows():
        d = feat[feat["cvegeo_mun"] == k].copy()
        ent = {"09": "Ciudad de México", "15": "Estado de México", "13": "Hidalgo"}[k[:2]]
        tipo = "alcaldía" if k.startswith("09") else "municipio"
        mm = mun[mun["cvegeo_mun"] == k].iloc[0]
        n_mun = len(ind)
        L = [f"# Ficha de {tipo}: {r['nom_mun']} ({ent}), clave {k}", ""]
        L += [f"Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). "
              f"{'Es municipio central de la zona metropolitana. ' if str(mm.get('municipio_central')).lower() in ('true', '1', 'si', 'sí') else ''}"
              f"{'Está en la delimitación 2020. ' if str(mm.get('en_delim_2020')).lower() in ('true', '1') else 'No está en la delimitación 2020 (Metrópolis de México 2020). '}"
              f"Cifras generadas con código el {HOY} desde `data/processed/agebs_features.parquet` y el DENUE; "
              f"cubren solo AGEB urbanas.", ""]

        L += ["## Población y hogares", "",
              f"- Población en AGEB urbanas: {n0(r['pob'])} habitantes (lugar {int(r['rk_pob'])} de {n_mun} en la ZMVM). Fuente: {FUENTE_CENSO}.",
              f"- Hogares: {n0(r['hogares'])}. AGEB urbanas: {r['n_ageb']}. Superficie urbana de esas AGEB: {n1(r['area'])} km².",
              f"- Densidad: {n0(r['dens'])} hab/km² (lugar {int(r['rk_dens'])} de {n_mun}).",
              f"- Edad: 0-14 años {pct(r['p014'])}; 15-24 {pct(r['p1524'])}; 25-59 {pct(r['p2559'])}; 60 o más {pct(r['p60'])}.",
              f"- Escolaridad promedio de la población de 15 y más: {n1(r['esc'])} años (lugar {int(r['rk_esc'])} de {n_mun}); promedio de las AGEB ponderado por población.",
              f"- Viviendas con automóvil: {pct(r['auto'])}; con internet: {pct(r['internet'])} (ponderado por viviendas habitadas).",
              f"- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): {pct(r['pob_1km_est'])}."]
        L += [""]

        L += ["## Nivel socioeconómico estimado", "",
              "Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. "
              "Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.", "",
              f"- Población por NSE estimado: bajo {pct(r['nse_bajo'])}, medio {pct(r['nse_medio'])}, alto {pct(r['nse_alto'])}"
              + (f", sin estimación {pct(r['nse_sin'])}." if r['nse_sin'] > 0 else "."),
              f"- Decil estimado típico (mediana ponderada por población): {n0(r['decil_med'])}."]
        gm = d.dropna(subset=["gm_2020"]).groupby("gm_2020")["pob_total"].sum()
        if len(gm):
            tot = gm.sum()
            orden = [x for x in ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"] if x in gm.index]
            L += ["- Grado de marginación urbana (CONAPO 2020), % de la población con índice: "
                  + "; ".join(f"{x} {gm[x] / tot * 100:.1f} %" for x in orden)
                  + ". Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación."]
        else:
            L += ["- Grado de marginación urbana (CONAPO 2020): NO ENCONTRADO."]
        L += [""]

        L += ["## Actividad económica (DENUE)", "",
              f"- Establecimientos en el DENUE 05/2026: {n0(r['n_den'])} ({n1(r['den_1000'])} por cada 1 000 habitantes, lugar {int(r['rk_den_1000'])} de {n_mun}). Fuente: {FUENTE_DENUE}.",
              f"- Establecimientos en el DENUE 11/2020: {n0(r['n_hist'])}. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.",
              f"- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): {n0(r['diurna'])}.",
              ""]
        ts = top_sector[top_sector["cvegeo_mun"] == k].sort_values("n", ascending=False).head(6)
        L += ["### Sectores con más establecimientos", ""]
        L += [tabla_md(["Sector SCIAN", "Establecimientos", "% del municipio"],
                       [[f"{x.sector} {sector.get(x.sector, '')}".strip(), n0(x.n), f"{x.n / r['n_den'] * 100:.1f} %"] for x in ts.itertuples()]), ""]
        tc = top_clase[top_clase["cvegeo_mun"] == k].sort_values("n", ascending=False).head(10)
        L += ["### Giros dominantes (clases SCIAN con más establecimientos)", ""]
        L += [tabla_md(["Clase SCIAN", "Actividad", "Establecimientos"],
                       [[x.codigo_act, titulo.get(x.codigo_act, "NO ENCONTRADO"), n0(x.n)] for x in tc.itertuples()]), ""]

        L += ["## Negocios de giros del catálogo en este municipio", "",
              "Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.", ""]
        gm_ = giro_mun.loc[k].sort_values(ascending=False)
        L += [tabla_md(["Giro", "Establecimientos", "Por 10 000 hab."],
                       [[g, n0(v), n1(v / r["pob"] * 10000)] for g, v in gm_.items()]), ""]

        # colonias
        c = d.groupby("nom_colonia", dropna=False).agg(
            negocios=("n_establecimientos", "sum"), agebs=("cvegeo", "count"), pob=("pob_total", "sum"),
            decil=("decil_esperado", lambda s: np.nan)).reset_index()
        # decil esperado ponderado por poblacion y NSE dominante por poblacion
        dd = d.dropna(subset=["decil_esperado"])
        pesos = dd.groupby("nom_colonia").apply(lambda g: pmedia(g["decil_esperado"], g["pob_total"]), include_groups=False)
        c["decil"] = c["nom_colonia"].map(pesos)
        nse_dom = d.dropna(subset=["nse"]).groupby(["nom_colonia", "nse"], observed=True)["pob_total"].sum().reset_index() \
            .sort_values("pob_total", ascending=False).drop_duplicates("nom_colonia").set_index("nom_colonia")["nse"]
        c["nse"] = c["nom_colonia"].map(nse_dom).fillna("NO ENCONTRADO")
        c = c.sort_values("negocios", ascending=False)
        L += ["## Colonias con más negocios", "",
              "Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. "
              "Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.", ""]
        L += [tabla_md(["Colonia", "AGEB", "Habitantes", "Negocios", "NSE estimado"],
                       [[x.nom_colonia, x.agebs, n0(x.pob), n0(x.negocios), x.nse] for x in c.head(10).itertuples()]), ""]

        cc = c[(c["pob"] >= 3000) & c["decil"].notna()]
        if len(cc) >= 6:
            alto = cc.sort_values("decil", ascending=False).head(5)
            bajo = cc.sort_values("decil").head(5)
            L += ["## Colonias de mayor y menor nivel socioeconómico estimado", "",
                  "Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.", ""]
            L += ["Mayor nivel estimado:", "", tabla_md(["Colonia", "Habitantes", "Decil esperado"],
                  [[x.nom_colonia, n0(x.pob), n1(x.decil)] for x in alto.itertuples()]), "",
                  "Menor nivel estimado:", "", tabla_md(["Colonia", "Habitantes", "Decil esperado"],
                  [[x.nom_colonia, n0(x.pob), n1(x.decil)] for x in bajo.itertuples()]), ""]

        L += ["## Gasto potencial en comida fuera del hogar", "",
              "Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. "
              "Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.", "",
              f"- Gasto potencial total: {n1(r['gasto_fuera'] / 1e6) if pd.notna(r['gasto_fuera']) else 'NO ENCONTRADO'} millones de pesos por trimestre.",
              f"- Por hogar: {n0(r['gasto_fuera_hog'])} pesos por trimestre (lugar {int(r['rk_gasto_fuera_hog'])} de {n_mun}).", ""]
        L += ["## Fuentes de esta ficha",
              f"Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el {HOY} por `scripts/04a_carpetas.py`."]
        escribe(out_dir / f"{k}_{slug(r['nom_mun'])}.md", "\n".join(L))

    # resumen comparativo
    ind_s = ind.sort_values("pob", ascending=False)
    L = ["# Resumen comparativo de los 76 municipios de la ZMVM", "",
         f"Generado el {HOY} desde `agebs_features.parquet` y el DENUE. Solo AGEB urbanas. NSE estimado (ver `01_metodologia/nse_estimado.md`); "
         f"gasto = gasto potencial estimado en comida fuera del hogar por hogar y trimestre, pesos de 2024. "
         f"Total: {n0(ind['pob'].sum())} habitantes y {n0(ind['n_den'].sum())} establecimientos (DENUE 05/2026).", ""]
    L += ["## Los 10 primeros lugares por indicador", "",
          "Listas ordenadas de mayor a menor, calculadas con las mismas cifras de las fichas.", ""]
    for col, nombre, fmt in [("pob", "Municipios con más habitantes (en AGEB urbanas)", n0),
                             ("dens", "Municipios con más densidad (hab/km²)", n0),
                             ("den_1000", "Municipios con más negocios por cada 1 000 habitantes (DENUE 05/2026)", n1),
                             ("n_den", "Municipios con más establecimientos en total (DENUE 05/2026)", n0),
                             ("nse_alto", "Municipios con mayor porcentaje de población en AGEB de NSE alto estimado", n1),
                             ("nse_bajo", "Municipios con mayor porcentaje de población en AGEB de NSE bajo estimado", n1),
                             ("gasto_fuera_hog", "Municipios con mayor gasto potencial en comida fuera del hogar por hogar (pesos por trimestre)", n0),
                             ("esc", "Municipios con mayor escolaridad promedio (años)", n1)]:
        top = ind.sort_values(col, ascending=False).head(10)
        L += [f"### {nombre}", "", "; ".join(f"{i + 1}. {x.nom_mun} ({fmt(getattr(x, col))})" for i, x in enumerate(top.itertuples())) + "."
              + (" Ojo: la tasa sube en municipios con poca población urbana o con comercio que atiende a otras zonas; no equivale a buen mercado local." if col == "den_1000" else ""), ""]
    L += ["## Población, densidad y negocios", ""]
    L += [tabla_md(["Clave", "Municipio", "Habitantes", "Hab/km²", "Negocios", "Negocios por 1 000 hab."],
                   [[k, x.nom_mun, n0(x.pob), n0(x.dens), n0(x.n_den), n1(x.den_1000)] for k, x in ind_s.iterrows()]), ""]
    L += ["## Nivel socioeconómico estimado y gasto", ""]
    L += [tabla_md(["Municipio", "% NSE bajo", "% NSE medio", "% NSE alto", "Decil típico", "Gasto fuera del hogar por hogar (pesos/trim.)"],
                   [[x.nom_mun, f"{x.nse_bajo:.0f}", f"{x.nse_medio:.0f}", f"{x.nse_alto:.0f}", n0(x.decil_med), n0(x.gasto_fuera_hog)] for _, x in ind_s.iterrows()]), ""]
    escribe(out_dir / "00_resumen_zmvm.md", "\n".join(L))
    print(f"municipios: {len(ind)} fichas + resumen; pob total {ind['pob'].sum():,.0f}")


# ---------- macro ----------
def generar_macro() -> None:
    m = json.load(open(PROC / "macro.json", encoding="utf-8"))

    def linea(nombre, d, extra=""):
        return (f"- **{nombre}**: {d['valor']:,.4g} {d['unidad']} (dato de {d['fecha']}, serie {d['id_serie']}). "
                f"Fuente: {d['fuente']}. Consultado el {d['consultado']}.{extra}")

    inf = m["inpc_general_var_anual"]
    tasa = m["tasa_objetivo"]
    real = tasa["valor"] - inf["valor"]
    L = ["# Contexto macroeconómico de México", "",
         f"Generado por `scripts/04a_carpetas.py` desde `data/processed/macro.json` (última lectura de las series: {m['_meta']['generado']}). "
         "Cada cifra trae fecha, número de serie y fuente. Las lecturas en «Qué significa» son interpretación del proyecto, no dato oficial.", "",
         "## Precios y tasas", "",
         linea("Inflación general anual (INPC)", inf, f" Índice base 2018 = {inf['indice_base_2018']}."),
         linea("Tasa objetivo de Banxico", tasa),
         linea("TIIE a 28 días", m["tiie_28"]),
         f"- Tasa real aproximada (tasa objetivo menos inflación anual de {inf['fecha']}): {real:.2f} puntos porcentuales. Cálculo del proyecto.", ""]
    ali = m["inpc_alimentos_var_anual"]
    L += ["## Inflación de alimentos", ""]
    if "valor" in ali:
        L += [linea("Inflación de alimentos", ali)]
    else:
        L += [f"**NO ENCONTRADO**: {ali['detalle']}", "", "Aproximaciones oficiales que sí existen (son proxies, no la inflación de alimentos):", ""]
        for k, p in ali.get("proxies", {}).items():
            L += [linea(p["descripcion_serie"] + " (proxy)", p)]
    L += ["", "## Tipo de cambio, remesas y consumo", "",
          linea("Tipo de cambio FIX", m["tipo_cambio_fix"]),
          linea("Remesas familiares (mensual)", m["remesas"],
                f" Variación anual: {m['remesas']['variacion_anual_pct']} %. Acumulado de 12 meses: {m['remesas']['acumulado_12_meses_millones_usd']:,.0f} millones de USD."),
          linea("Confianza del consumidor", m["confianza_consumidor"], f" {m['confianza_consumidor'].get('nota', '')}"),
          linea("Consumo privado (IMCP, variación anual)", m["consumo_privado"],
                f" Índice de volumen base 2018 = {m['consumo_privado']['indice_volumen_2018']}. {m['consumo_privado'].get('verificacion', '')}"), "",
          "## Qué significa para quien abre un negocio",
          "Interpretación del proyecto, a partir de las cifras anteriores:", "",
          f"- Con tasa objetivo de {tasa['valor']} % e inflación de {inf['valor']} %, el crédito sigue caro en términos reales ({real:.1f} puntos): "
          "financiar la apertura con deuda pesa más que con ahorro propio.",
          f"- Con inflación de {inf['valor']} %, los costos de insumos y rentas suben a ese ritmo en promedio; el ticket tiene que ajustarse en lo mismo para mantener el margen.",
          f"- El consumo privado crece {m['consumo_privado']['valor']:.2f} % anual ({m['consumo_privado']['fecha']}) y la confianza del consumidor está en {m['confianza_consumidor']['valor']:.1f} puntos ({m['confianza_consumidor']['fecha']}): la demanda crece poco.",
          "- Las remesas son un dato nacional; este proyecto no las tiene desagregadas por municipio ni por colonia (NO ENCONTRADO).", "",
          "## Límites",
          "Son cifras nacionales. No se encontró en esta fuente un indicador macro específico de la ZMVM; el nivel de ingreso local viene de la ENIGH y está en `01_metodologia/`."]
    escribe(CARP / "02_macro" / "contexto_macro.md", "\n".join(L))
    print("macro ok")


# ---------- ENIGH por decil ----------
def generar_enigh() -> None:
    c = pd.read_parquet(PROC / "enigh_decil_cortes.parquet")
    c = c[c["ambito"] == "zmvm"].sort_values("decil")
    g = pd.read_parquet(PROC / "enigh_gasto.parquet")
    g = g[g["ambito"] == "zmvm"]
    L = ["# ENIGH 2024: hogares de la ZMVM por decil de ingreso", "",
         f"Generado por `scripts/04a_carpetas.py` el {HOY} desde `data/processed/enigh_decil_cortes.parquet` y `enigh_gasto.parquet`. "
         "Fuente: INEGI, ENIGH 2024 Nueva Serie, microdatos (https://www.inegi.org.mx/programas/enigh/nc/2024/). "
         "Ámbito `zmvm`: submuestra de 3 767 hogares urbanos de 48 municipios; no es representativa por municipio. Pesos corrientes de 2024. "
         "Los deciles son de la ZMVM (decil 1 = 10 % más pobre de la ZMVM).", "",
         "## Ingreso y rasgos del hogar por decil", ""]
    L += [tabla_md(["Decil", "Ingreso corriente mensual prom. (pesos)", "Ingreso trim. máx. del decil", "Escolaridad del jefe (años)", "% con auto", "% con internet", "% con PC/tablet", "Integrantes"],
                   [[int(x.decil), n0(x.ing_cor_mensual_prom), n0(x.ing_cor_trim_max), n1(x.esc_jefe_anios_prom), n1(x.pct_auto), n1(x.pct_internet), n1(x.pct_pc), n1(x.tot_integ_prom)] for x in c.itertuples()]), ""]
    rubros = [("ali_fuera_total", "Comida fuera del hogar"), ("restaurante_comidas", "Restaurantes"), ("comida_rapida", "Comida rápida"),
              ("antojitos_tacos", "Antojitos y tacos"), ("cafe_bebidas", "Café y bebidas"), ("helados", "Helados (compra)"),
              ("pan_pasteles", "Pan y pasteles"), ("ali_dentro", "Alimentos dentro del hogar"), ("medic_prod", "Medicamentos"),
              ("educacion", "Educación"), ("esparci", "Esparcimiento"), ("cuida_pers", "Cuidado personal"),
              ("vesti_calz", "Vestido y calzado"), ("gimnasio_deporte", "Gimnasio y deporte")]
    L += ["## Gasto trimestral promedio del hogar por rubro y decil (pesos de 2024)", "",
          "Promedio contando como cero a los hogares que no gastaron. Rubros con pocos hogares que gastan (helados, gimnasio) dan promedios ruidosos.", ""]
    for i in range(0, len(rubros), 5):
        grupo = [(k, n) for k, n in rubros[i:i + 5] if (g["rubro_clave"] == k).any()]
        if not grupo:
            continue
        filas = []
        for d in range(1, 11):
            fila = [d]
            for k, _ in grupo:
                v = g[(g["rubro_clave"] == k) & (g["decil"] == d)]
                fila.append(n0(v["gasto_trim_prom_hogar"].iloc[0]) if len(v) else "NO ENCONTRADO")
            filas.append(fila)
        L += [tabla_md(["Decil"] + [n for _, n in grupo], filas), ""]
    L += ["## Porcentaje de hogares que reportó gasto en el rubro", ""]
    grupo = [(k, n) for k, n in rubros if (g["rubro_clave"] == k).any()][:7]
    filas = []
    for d in range(1, 11):
        fila = [d]
        for k, _ in grupo:
            v = g[(g["rubro_clave"] == k) & (g["decil"] == d)]
            fila.append(n1(v["pct_hogares_con_gasto"].iloc[0]) if len(v) else "NO ENCONTRADO")
        filas.append(fila)
    L += [tabla_md(["Decil"] + [n for _, n in grupo], filas), ""]
    escribe(CARP / "01_metodologia" / "enigh_zmvm_deciles.md", "\n".join(L))
    print("enigh ok")


# ---------- giros ----------
def generar_giros() -> None:
    giros = cargar_giros()
    titulo, _ = cargar_scian()
    cab = yaml.safe_load(open(RAIZ / "config" / "giros.yaml", encoding="utf-8"))
    L = ["# Catálogo de giros del modelo", "",
         f"Generado por `scripts/04a_carpetas.py` el {HOY} desde `config/giros.yaml` (versión {cab.get('version')}, SCIAN {cab.get('scian_version')}). "
         f"{len(giros)} giros. Los tickets, radios, cliente objetivo y NSE objetivo son **supuestos del autor** salvo donde diga lo contrario: no son dato medido. "
         "Los códigos SCIAN son de 6 dígitos (INEGI, https://www.inegi.org.mx/app/scian/). El DENUE clasifica por actividad, no por producto: donde la clase se comparte con otros giros se filtra por el nombre del negocio.", "",
         "## Lista", "",
         ", ".join(f"{g['clave']}" for g in giros)]
    escribe(CARP / "06_giros" / "00_indice_giros.md", "\n".join(L))

    L = ["# Fichas de giros", "", f"Generado el {HOY} desde `config/giros.yaml`.", ""]
    for g in giros:
        sc = ", ".join(f"{c} ({titulo.get(c, 'NO ENCONTRADO')})" for c in g.get("scian") or []) or "ninguna clase propia; solo por nombre"
        filt = "; ".join(f"clases {', '.join(f['codigos'])} con nombre que cumple /{f['nombre_regex']}/" for f in g.get("scian_con_filtro") or [])
        comp = ", ".join(f"{c} ({titulo.get(c, '?')})" for c in g.get("complementarios") or []) or "ninguno"
        cli = ", ".join(f"{k} años {v * 100:.0f} %" for k, v in (g.get("cliente_objetivo") or {}).items())
        nse = ", ".join(f"{k} {v * 100:.0f} %" for k, v in (g.get("nse_objetivo") or {}).items())
        rub = g.get("rubro_enigh") or "NO ENCONTRADO (la ENIGH no mide este gasto)"
        L += [f"## {g['clave']}", "",
              f"- También se le llama: {', '.join(g.get('nombres') or [])}.",
              f"- Competencia (SCIAN 2023): {sc}." + (f" Además: {filt}." if filt else ""),
              f"- Complementarios (atraen a su cliente; criterio del autor): {comp}.",
              f"- Cliente objetivo por edad (supuesto): {cli}. NSE objetivo (supuesto): {nse}.",
              f"- Rubro de gasto en la ENIGH: {rub}." + (f" {g['rubro_enigh_nota']}" if g.get("rubro_enigh_nota") else ""),
              f"- Ticket promedio de referencia: {g.get('ticket_promedio_mxn')} pesos ({g.get('ticket_fuente')}).",
              f"- Radio de influencia: {g.get('radio_influencia_m')} m (supuesto). Demanda base: {g.get('demanda_base', 'residente')}.",
              f"- Notas: {g.get('notas', '')}", ""]
    escribe(CARP / "06_giros" / "fichas_giros.md", "\n".join(L))
    print(f"giros ok ({len(giros)})")


# ---------- modelo ----------
PLACEHOLDER = """> **[PLACEHOLDER: validación pendiente]** `reports/validacion.md` todavía no existe (la etapa del modelo no ha terminado
> o no se ha corrido `make entrenar`). Esta sección se llena sola al volver a correr `uv run python scripts/04a_carpetas.py`
> (o `make indexar`). Hasta entonces el modelo **no debe citar** AUC, precisión ni importancia de variables: decir «NO ENCONTRADO»."""


def generar_modelo() -> None:
    val = RAIZ / "reports" / "validacion.md"
    meta = RAIZ / "models" / "metadata.json"
    L = ["# Qué hace el modelo y qué no puede decir", "",
         f"Generado por `scripts/04a_carpetas.py` el {HOY}. El diseño viene de `docs/CONTRATO.md`; los resultados, de `reports/validacion.md` y `models/metadata.json` cuando existen.", "",
         "## Qué es", "",
         "El modelo de **aperturas** aprende en qué AGEB aparecen establecimientos de un giro. Para cada pareja (AGEB, giro), la etiqueta es 1 si en el DENUE de mayo de 2026 hay al menos un establecimiento del giro que no estaba en el DENUE de noviembre de 2020 (se empata por identificador y, como respaldo, por nombre y coordenadas). "
         "También hay una variante «sobrevivió»: el establecimiento está en ambos cortes. "
         "Las variables son las de `agebs_features` (población, densidad, NSE estimado, gasto potencial, transporte, escuelas, hospitales, plazas, negocios por sector alrededor) más competencia y complementarios del giro **en el corte de 2020**, para no filtrar información del futuro. "
         "El algoritmo es `HistGradientBoostingClassifier` de scikit-learn (no LightGBM, porque en esta Mac falta libomp y rompería la replicabilidad).", "",
         "## Cómo se califica una zona", "",
         "La función `app/motor.py: score_giro(giro_clave)` regresa, por AGEB: probabilidad de apertura, demanda, competencia, complementarios, score y razones. "
         "La forma exacta en que se combinan esos componentes está en `app/motor.py` y se describe en la validación de abajo; esta explicación no la repite para no contradecir al código. "
         "Las razones son los números que explican el score, para que la respuesta cite cifras.", "",
         "## Cómo se valida", "",
         "Validación espacial: se deja fuera cada vez un grupo de alcaldías o municipios (GroupKFold por `cvegeo_mun`), de modo que el modelo se prueba en municipios que no vio. "
         "Se reportan AUC, precisión en el top-k y la comparación con una línea base ingenua (ordenar solo por densidad de población). Si el modelo no le gana a la línea base, hay que decirlo.", "",
         "## Resultados de la validación", ""]
    if val.exists():
        txt = val.read_text(encoding="utf-8")
        L += [f"Copiados de `reports/validacion.md` (modificado el {date.fromtimestamp(val.stat().st_mtime).isoformat()}). Esa es la fuente; si cambia, volver a generar.", ""]
        # baja un nivel los encabezados para que queden dentro de esta seccion
        txt = re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", txt, flags=re.M)
        L += [txt.strip(), ""]
    else:
        L += [PLACEHOLDER, ""]
    if meta.exists():
        try:
            md = json.load(open(meta, encoding="utf-8"))
            L += ["## Metadatos del modelo entrenado", "", "De `models/metadata.json`:", "", "```json",
                  json.dumps(md, ensure_ascii=False, indent=1)[:3500], "```", ""]
        except Exception as e:  # el archivo puede estar a medias si el entrenamiento sigue corriendo
            L += [f"`models/metadata.json` existe pero no se pudo leer ({e.__class__.__name__}).", ""]
    else:
        L += ["## Metadatos del modelo entrenado", "", "**[PLACEHOLDER]** `models/metadata.json` todavía no existe.", ""]
    L += ["## Límites que hay que decir siempre", "",
          "1. **Aparecer en el DENUE no es abrir ni tener éxito.** Entre los cortes de 2020 y 2026 hay cargas masivas de los Censos Económicos y rotación de identificadores. El modelo describe dónde entraron negocios al directorio, no dónde ganaron dinero.",
          "2. **No hay datos de ventas, rentas ni flujo peatonal por calle.** La unidad más fina es la AGEB (en promedio unas cuantas manzanas). Dentro de una AGEB la esquina importa y el modelo no la ve.",
          "3. **El nivel socioeconómico es una estimación** (ENIGH aplicada al Censo), no un dato medido. La ENIGH no representa municipios. Ver `01_metodologia/nse_estimado.md`.",
          "4. **Los datos son de 2020 (Censo), 2024 (ENIGH) y 2026 (DENUE).** Un barrio que cambió mucho desde 2020 puede estar mal descrito.",
          "5. **Complementarios, radios de influencia, clientes objetivo y tickets son supuestos razonados**, no evidencia. Los tickets en particular son «supuesto» en los 40 giros y deben contrastarse con precios reales.",
          "6. **Giros raros** (renta de bicicletas, coworking) tienen pocas observaciones en el DENUE; el modelo no tiene muestra para ellos y el resultado es poco confiable.",
          "7. **83 AGEB** no tienen NSE ni gasto estimado; para ellas el dato es NO ENCONTRADO.",
          "8. Zona de estudio: solo los 76 municipios de la ZMVM. Fuera de ahí (por ejemplo Monterrey) el modelo no tiene datos y debe decirlo.", ""]
    escribe(CARP / "05_modelo" / "explicacion_modelo.md", "\n".join(L))
    print("modelo ok", "(con validacion.md)" if val.exists() else "(PLACEHOLDER: no hay validacion.md)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["municipios", "macro", "enigh", "giros", "modelo"])
    a = ap.parse_args()
    pasos = {"municipios": generar_municipios, "macro": generar_macro, "enigh": generar_enigh,
             "giros": generar_giros, "modelo": generar_modelo}
    for nom, f in pasos.items():
        if a.solo in (None, nom):
            f()


if __name__ == "__main__":
    main()
