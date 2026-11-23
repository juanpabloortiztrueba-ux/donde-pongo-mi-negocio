"""Etapa Features D: una fila por AGEB con todo lo que usan el modelo y el agente.

Entradas (data/processed): agebs_base, denue_actual, enigh_hogares, enigh_gasto, transporte,
config/giros.yaml. Salidas: data/processed/agebs_features.parquet y reports/decil_imputado.md.

Uso:  uv run python scripts/02_features.py        (~1 min; es idempotente, siempre rehace)
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm, spearmanr

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from app import motor  # noqa: E402

PROC = RAIZ / "data" / "processed"
SALIDA = PROC / "agebs_features.parquet"
REPORTE = RAIZ / "reports" / "decil_imputado.md"

COVARIABLES = ["esc_jefe_anios", "tiene_auto", "tiene_internet", "tiene_pc", "tot_integ"]
# nombre de cada covariable en el Censo (agebs_base) y como pasarla a la escala de ENIGH
CENSO = {"esc_jefe_anios": "escolaridad_prom", "tiene_auto": "pct_viv_auto",
         "tiene_internet": "pct_viv_internet", "tiene_pc": "pct_viv_pc", "tot_integ": "prom_ocupantes"}
AMBITO = "zmvm"  # ambito de la ENIGH con el que se definen los deciles y se toma el gasto
NSE_CORTES = {"bajo": range(1, 5), "medio": range(5, 9), "alto": range(9, 11)}  # deciles 1-4, 5-8, 9-10


def t0() -> float:
    return time.time()


def log(msg: str) -> None:
    print(f"[02_features] {msg}", flush=True)


# =============================================================== 1. nombre de colonia
def nombre_colonia(base: pd.DataFrame, den: pd.DataFrame) -> pd.DataFrame:
    """Asentamiento (colonia) mas frecuente del DENUE actual dentro de cada AGEB; si no hay, nom_loc."""
    d = den.dropna(subset=["cvegeo", "nom_asent"])
    d = d[d["nom_asent"].str.strip() != ""]
    c = d.groupby(["cvegeo", "nom_asent"]).size().rename("n").reset_index()
    c = c.sort_values(["cvegeo", "n", "nom_asent"], ascending=[True, False, True]).drop_duplicates("cvegeo")
    tipo = (d.groupby(["cvegeo", "nom_asent", "tipo_asent"]).size().rename("m").reset_index()
            .sort_values(["cvegeo", "nom_asent", "m"], ascending=[True, True, False])
            .drop_duplicates(["cvegeo", "nom_asent"]))
    c = c.merge(tipo[["cvegeo", "nom_asent", "tipo_asent"]], on=["cvegeo", "nom_asent"], how="left")
    cp = (d.groupby(["cvegeo", "cod_postal"]).size().rename("k").reset_index()
          .sort_values(["cvegeo", "k", "cod_postal"], ascending=[True, False, True]).drop_duplicates("cvegeo"))
    out = base[["cvegeo", "nom_loc"]].merge(c[["cvegeo", "nom_asent", "tipo_asent"]], on="cvegeo", how="left")
    out = out.merge(cp[["cvegeo", "cod_postal"]], on="cvegeo", how="left")
    out["colonia_fuente"] = np.where(out["nom_asent"].notna(), "denue", "nom_loc")
    out["nom_colonia"] = out["nom_asent"].fillna(out["nom_loc"]).str.strip()
    return out.rename(columns={"tipo_asent": "tipo_asentamiento", "cod_postal": "cp_modal"})[
        ["cvegeo", "nom_colonia", "tipo_asentamiento", "cp_modal", "colonia_fuente"]]


# =============================================================== 2. DENUE alrededor de la AGEB
def contar_a_radios(pts: pd.DataFrame, cen: pd.DataFrame, radios=(500, 1000), valor=None) -> dict[int, np.ndarray]:
    """Conteo (o suma de `valor`) de puntos a <= r metros del centroide, sin decaimiento."""
    out = {}
    for r in radios:
        out[r] = motor.suma_radial(pts["x"].to_numpy(), pts["y"].to_numpy(),
                                   None if valor is None else pts[valor].to_numpy(), r,
                                   decaimiento=False, centros=cen).to_numpy()
    return out


def etiqueta_r(r: int) -> str:
    return "500m" if r == 500 else "1km"


def features_denue(base: pd.DataFrame, den: pd.DataFrame) -> pd.DataFrame:
    cen = motor.agebs_xy().loc[base["cvegeo"]]
    f = pd.DataFrame(index=base["cvegeo"])
    # por sector SCIAN de 2 digitos
    den = den.assign(sector=den["codigo"].str[:2])
    for sec, pts in den.groupby("sector"):
        for r, v in contar_a_radios(pts, cen).items():
            f[f"sec{sec}_{etiqueta_r(r)}"] = v.astype("int32")
    # empleo (punto medio del estrato) y establecimientos
    for r, v in contar_a_radios(den, cen, valor="per_ocu_medio").items():
        f[f"empleo_{etiqueta_r(r)}"] = v
    for r, v in contar_a_radios(den, cen).items():
        f[f"estab_{etiqueta_r(r)}"] = v.astype("int32")
    # poblacion diurna: empleados del DENUE dentro de la propia AGEB
    dd = den.dropna(subset=["cvegeo"]).groupby("cvegeo").agg(pob_diurna=("per_ocu_medio", "sum"),
                                                              n_establecimientos=("id", "size"))
    f = f.join(dd).fillna({"pob_diurna": 0.0, "n_establecimientos": 0})
    f["n_establecimientos"] = f["n_establecimientos"].astype("int32")
    # escuelas, hospitales y plazas comerciales cercanas
    cod = den["codigo"]
    nom = den["nombre"].fillna("")
    escuelas = den[cod.str.startswith("611")]
    hospitales = den[cod.str.startswith("622")]
    # DENUE no tiene clave de "plaza comercial": proxy = supermercados, tiendas departamentales
    # (sin las "Tiendas 3B") y alquiler de locales/oficinas cuyo nombre dice plaza o centro comercial
    ancla = cod.isin(["462111", "462210"]) & ~nom.str.contains(r"\b(?:3B|TRES B)\b", regex=True)
    plaza_nom = cod.str.startswith("5311") & nom.str.contains(
        r"CENTRO COMERCIAL|PLAZA COMERCIAL|MULTIPLAZA|\bMALL\b|GALERIAS", regex=True)
    plazas = den[ancla | plaza_nom]
    for nombre, pts in [("escuelas", escuelas), ("hospitales", hospitales), ("plazas", plazas)]:
        for r, v in contar_a_radios(pts, cen).items():
            f[f"n_{nombre}_{etiqueta_r(r)}"] = v.astype("int32")
    return f.reset_index()


# =============================================================== 3. transporte
def features_transporte(base: pd.DataFrame) -> pd.DataFrame:
    t = pd.read_parquet(PROC / "transporte.parquet")
    est = t["estado"].fillna("")
    t = t[~est.str.contains("no confirmada|no verificada") & (t["tipo"].fillna("") != "Servicio temporal")]
    # Metro: una estacion por nombre (suma las lineas); el resto, una fila por parada
    m = t[t["sistema"] == "Metro"].groupby("estacion").agg(
        lat=("lat", "mean"), lon=("lon", "mean"),
        afluencia_anual=("afluencia_anual", lambda s: s.sum(min_count=1)),
        linea=("linea", lambda s: ",".join(sorted(map(str, s))))).reset_index()
    m["sistema"] = "Metro"
    o = t[t["sistema"] != "Metro"][["sistema", "linea", "estacion", "lat", "lon", "afluencia_anual"]]
    est = pd.concat([m, o], ignore_index=True)
    est["x"], est["y"] = motor.a_metros(est["lon"], est["lat"])
    cen = motor.agebs_xy().loc[base["cvegeo"]]
    cxy = cen[["x", "y"]].to_numpy()
    f = pd.DataFrame(index=base["cvegeo"])
    d, i = cKDTree(est[["x", "y"]].to_numpy()).query(cxy)
    f["dist_estacion_m"] = d
    f["estacion_cercana"] = est["estacion"].to_numpy()[i]
    f["sistema_estacion"] = est["sistema"].to_numpy()[i]
    f["afluencia_estacion"] = est["afluencia_anual"].to_numpy()[i]  # solo hay dato para el Metro
    mt = est[est["sistema"] == "Metro"].reset_index(drop=True)
    d, i = cKDTree(mt[["x", "y"]].to_numpy()).query(cxy)
    f["dist_metro_m"] = d
    f["metro_cercano"] = mt["estacion"].to_numpy()[i]
    f["afluencia_metro_cercano"] = mt["afluencia_anual"].to_numpy()[i]
    f["n_estaciones_1km"] = motor.suma_radial(est["x"].to_numpy(), est["y"].to_numpy(), None, 1000,
                                              decaimiento=False, centros=cen).to_numpy().astype("int32")
    f["afluencia_metro_1km"] = motor.suma_radial(
        mt["x"].to_numpy(), mt["y"].to_numpy(), mt["afluencia_anual"].fillna(0).to_numpy(), 1000,
        decaimiento=False, centros=cen).to_numpy()
    return f.reset_index()


# =============================================================== 4. decil imputado
def deciles_cortes(h: pd.DataFrame) -> np.ndarray:
    """Cortes de ingreso (9) entre deciles, a partir del `decil` ya calculado por Datos C."""
    g = h.groupby("decil")["ing_cor"].agg(["min", "max"])
    return np.array([(g.loc[k, "max"] + g.loc[k + 1, "min"]) / 2 for k in range(1, 10)])


def wls(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> np.ndarray:
    XtW = X.T * w
    return np.linalg.solve(XtW @ X, XtW @ y)


def wls_se_cluster(X, y, w, b, grupos) -> np.ndarray:
    """Errores estandar robustos por conglomerado (UPM) con el diseno muestral simplificado."""
    e = y - X @ b
    A = np.linalg.inv((X.T * w) @ X)
    s = pd.DataFrame(X * (w * e)[:, None]).groupby(np.asarray(grupos)).sum().to_numpy()
    G, n, k = len(s), len(y), X.shape[1]
    V = A @ (s.T @ s) @ A * (G / (G - 1)) * ((n - 1) / (n - k))
    return np.sqrt(np.diag(V))


def r2_pond(y, p, w) -> float:
    m = np.average(y, weights=w)
    return 1 - np.sum(w * (y - p) ** 2) / np.sum(w * (y - m) ** 2)


def decil_de(valor_ing: np.ndarray, cortes: np.ndarray) -> np.ndarray:
    return np.searchsorted(cortes, valor_ing) + 1  # 1..10


def probs_decil(mu: np.ndarray, sigma: float, cortes: np.ndarray) -> np.ndarray:
    """P(decil k | AGEB) con ingreso lognormal(mu, sigma): matriz n x 10."""
    z = (np.log(cortes)[None, :] - mu[:, None]) / sigma
    cdf = np.hstack([np.zeros((len(mu), 1)), norm.cdf(z), np.ones((len(mu), 1))])
    return np.diff(cdf, axis=1)


def ajustar_modelo(h: pd.DataFrame) -> dict:
    """Ajusta log(ing_cor) ~ covariables comunes con el Censo, con validacion cruzada por UPM."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import GroupKFold

    y = np.log(h["ing_cor"].to_numpy())
    w = h["factor"].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(h))] + [h[c].astype(float).to_numpy() for c in COVARIABLES])
    b = wls(X, y, w)
    se = wls_se_cluster(X, y, w, b, h["upm"])
    cortes = deciles_cortes(h)
    dec = h["decil"].to_numpy()
    res = y - X @ b
    sigma_res = float(np.sqrt(np.average(res ** 2, weights=w)))
    # validacion cruzada (5 pliegues, sin partir una UPM)
    pred_ols, pred_gb = np.zeros(len(h)), np.zeros(len(h))
    for tr, te in GroupKFold(n_splits=5).split(X, y, groups=h["upm"]):
        bb = wls(X[tr], y[tr], w[tr])
        pred_ols[te] = X[te] @ bb
        gb = HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=200, random_state=0)
        gb.fit(X[tr, 1:], y[tr], sample_weight=w[tr])
        pred_gb[te] = gb.predict(X[te, 1:])

    def metricas(p):
        d = decil_de(np.exp(p), cortes)
        pr = probs_decil(p, sigma_res, cortes)
        return {
            "r2": r2_pond(y, p, w),
            "rmse": float(np.sqrt(np.average((y - p) ** 2, weights=w))),
            "spearman": float(spearmanr(p, y).statistic),
            "exacto": float(np.average(d == dec, weights=w)),
            "mas_menos_1": float(np.average(np.abs(d - dec) <= 1, weights=w)),
            "prob_decil_real": float(np.average(pr[np.arange(len(h)), dec - 1], weights=w)),
        }

    return {"b": b, "se": se, "cortes": cortes, "sigma_res": sigma_res,
            "r2_dentro": r2_pond(y, X @ b, w), "n": len(h), "w_total": float(w.sum()),
            "media_log": float(np.average(y, weights=w)), "var_log": float(np.average((y - np.average(y, weights=w)) ** 2, weights=w)),
            "cv_ols": metricas(pred_ols), "cv_hgb": metricas(pred_gb),
            "acuerdo_decil_cortes": float(np.average(decil_de(h["ing_cor"].to_numpy(), cortes) == dec, weights=w)),
            "upm": int(h["upm"].nunique())}


def covariables_agebs(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Covariables del Censo en la escala de ENIGH. Rellena huecos con el promedio del municipio
    (ponderado por hogares) y marca cuantas se rellenaron. Devuelve (X, n_rellenadas)."""
    X = pd.DataFrame(index=base.index)
    for k, c in CENSO.items():
        X[k] = base[c] / (100.0 if c.startswith("pct_") else 1.0)
    hog = base["hogares"].fillna(0)
    n_faltan = X.isna().sum(axis=1)
    for k in COVARIABLES:
        mun = (X[k] * hog).groupby(base["cvegeo"].str[:5]).transform("sum") / hog.where(X[k].notna(), 0).groupby(base["cvegeo"].str[:5]).transform("sum")
        X[k] = X[k].fillna(mun).fillna(np.average(X[k].dropna(), weights=hog[X[k].notna()] + 1e-9))
    X["esc_jefe_anios"] = X["esc_jefe_anios"].clip(0, 20)
    for k in ("tiene_auto", "tiene_internet", "tiene_pc"):
        X[k] = X[k].clip(0, 1)
    return X, n_faltan


def ecologico_municipal(base: pd.DataFrame, h: pd.DataFrame, mu: np.ndarray, valido: np.ndarray) -> pd.DataFrame:
    """Por municipio con >= 30 hogares muestrales: log ingreso medio de la ENIGH (n, ly) y el estimado del Censo (mu_censo)."""
    g = h.assign(ly=np.log(h["ing_cor"])).groupby("cvegeo_mun").apply(
        lambda d: pd.Series({"n": len(d), "ly": np.average(d["ly"], weights=d["factor"])}), include_groups=False)
    g = g[g["n"] >= 30]
    e = pd.DataFrame({"mun": base["cvegeo"].str[:5].to_numpy()[valido], "mu": mu[valido],
                      "hog": base["hogares"].to_numpy()[valido]})
    e = e.groupby("mun").apply(lambda d: np.average(d["mu"], weights=d["hog"]), include_groups=False)
    return g.join(e.rename("mu_censo"), how="inner")


def pendiente_municipal(j: pd.DataFrame) -> tuple[float, float]:
    """Pendiente (y error est. aprox.) de ly sobre mu_censo, ponderada por hogares muestrales del municipio."""
    n, x, y = j["n"].to_numpy(), j["mu_censo"].to_numpy(), j["ly"].to_numpy()
    X = np.column_stack([np.ones(len(x)), x])
    b = wls(X, y, n)
    e = y - X @ b
    se = np.sqrt(np.linalg.inv((X.T * n) @ X)[1, 1] * np.sum(n * e ** 2) / (len(x) - 2))
    return float(b[1]), float(se)


def imputar_decil(base: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    enigh = pd.read_parquet(PROC / "enigh_hogares.parquet")
    h = enigh[(enigh["ambito"] == AMBITO) & (enigh["ing_cor"] > 0)].reset_index(drop=True)
    n_cero = int(((enigh["ambito"] == AMBITO) & (enigh["ing_cor"] <= 0)).sum())
    m = ajustar_modelo(h)
    X, n_faltan = covariables_agebs(base)
    hog = base["hogares"]
    valido = hog.notna() & (hog > 0) & (n_faltan <= 2)
    Xm = np.column_stack([np.ones(len(X))] + [X[c].to_numpy() for c in COVARIABLES])
    mu_raw = Xm @ m["b"]
    wv = hog.where(valido, 0).to_numpy()
    delta = m["media_log"] - float(np.average(mu_raw[valido], weights=wv[valido]))
    mu1 = mu_raw + delta
    centro = float(np.average(mu1[valido], weights=wv[valido]))
    var_entre1 = float(np.average((mu1[valido] - centro) ** 2, weights=wv[valido]))
    # Calibracion ecologica: entre municipios, la ENIGH sube mas rapido que el modelo de hogares (el
    # Censo promedia el ruido de cada hogar y deja ver el contexto del barrio). Se estima la pendiente
    # municipal lam y se estira mu alrededor de su promedio; tope: que la varianza entre AGEB no pase la
    # varianza total menos la de los residuos.
    vm = valido.to_numpy()
    j1 = ecologico_municipal(base, h, mu1, vm)
    lam_raw, lam_se = pendiente_municipal(j1)
    jack = [pendiente_municipal(j1.drop(index=i))[0] for i in j1.index]
    lam_max = float(np.sqrt(max(m["var_log"] - m["sigma_res"] ** 2, 0) / var_entre1))
    lam = float(min(max(lam_raw, 1.0), lam_max))
    mu = centro + lam * (mu1 - centro)
    var_entre = float(np.average((mu[valido] - centro) ** 2, weights=wv[valido]))
    sigma2 = max(m["var_log"] - var_entre, m["sigma_res"] ** 2)
    sigma = float(np.sqrt(sigma2))
    P = probs_decil(mu, sigma, m["cortes"])
    P[~valido.to_numpy()] = np.nan

    f = pd.DataFrame({"cvegeo": base["cvegeo"].to_numpy()})
    f["decil_imputado"] = pd.array(np.where(valido, decil_de(np.exp(mu), m["cortes"]), 0), dtype="Int8")
    f.loc[~valido.to_numpy(), "decil_imputado"] = pd.NA
    f["decil_esperado"] = P @ np.arange(1, 11)
    f["ing_trim_mediano_est"] = np.where(valido, np.exp(mu), np.nan)
    f["decil_cov_rellenadas"] = n_faltan.to_numpy().astype("int8")
    for k in range(10):
        f[f"p_decil_{k + 1:02d}"] = P[:, k]
    for nse, ks in NSE_CORTES.items():
        f[f"p_nse_{nse}"] = P[:, [k - 1 for k in ks]].sum(axis=1)
    di = f["decil_imputado"].astype("float").to_numpy()
    f["nse"] = np.select([di <= 4, di <= 8, di >= 9], ["bajo", "medio", "alto"], default="")
    f["nse"] = f["nse"].replace("", None).astype(object)
    f.loc[~valido.to_numpy(), "nse"] = None

    m.update({"lam": lam, "lam_raw": lam_raw, "lam_se": lam_se, "lam_max": lam_max, "lam_jack": (min(jack), max(jack)),
              "n_mun_cal": len(j1), "mu1": mu1, "var_entre1": var_entre1, "h": h, "delta": float(delta), "var_entre": var_entre, "sigma": sigma, "sigma2": sigma2,
              "n_cero": n_cero, "valido": valido.to_numpy(), "mu": mu, "P": P, "X": X, "n_faltan": n_faltan,
              "enigh_todo": enigh})
    return f, m


def validar_decil(base: pd.DataFrame, f: pd.DataFrame, m: dict) -> dict:
    """Comprobaciones fuera del ajuste: municipios, marginacion CONAPO y reparto de hogares."""
    out = {}
    v = m["valido"]
    hog = base["hogares"].to_numpy()
    # 1) reparto agregado: hogares por decil imputado (esperado) vs 10 % que impone la ENIGH
    P = m["P"][v]
    reparto = (P * hog[v][:, None]).sum(axis=0) / hog[v].sum()
    out["reparto_prob"] = reparto
    dec = f.loc[v, "decil_imputado"].astype(int).to_numpy()
    out["reparto_modal"] = np.bincount(dec, weights=hog[v], minlength=11)[1:] / hog[v].sum()
    # 2) municipios (ENIGH no es representativa por municipio: solo los de >= 30 hogares muestrales)
    j = ecologico_municipal(base, m["h"], m["mu"], v)
    j0 = ecologico_municipal(base, m["h"], m["mu1"], v)
    out["mun_dif_antes"] = float((j0["ly"] - j0["mu_censo"]).abs().mean())
    out["n_mun"] = len(j)
    out["mun_pearson"] = float(np.corrcoef(j["ly"], j["mu_censo"])[0, 1])
    out["mun_spearman"] = float(spearmanr(j["ly"], j["mu_censo"]).statistic)
    out["mun_dif_media_abs"] = float((j["ly"] - j["mu_censo"]).abs().mean())
    out["mun_tabla"] = j
    # 3) marginacion CONAPO (im_2020 alto = menos marginacion)
    ok = v & base["im_2020"].notna().to_numpy()
    out["n_im"] = int(ok.sum())
    out["im_spearman"] = float(spearmanr(m["mu"][ok], base["im_2020"].to_numpy()[ok]).statistic)
    gm = pd.DataFrame({"gm": base["gm_2020"].to_numpy()[ok], "dec": f["decil_imputado"].astype(float).to_numpy()[ok]})
    out["gm_tabla"] = gm.groupby("gm")["dec"].agg(["count", "mean", "median"])
    return out


# =============================================================== 5. gasto potencial
def rubros_de_giros() -> list[str]:
    ys = list(motor.giros().values())
    r = {g.get("rubro_enigh") for g in ys} | {x for g in ys for x in (g.get("rubro_enigh_alt") or [])}
    return sorted(x for x in r if x)


def gasto_por_rubro(base: pd.DataFrame, f: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    gas = pd.read_parquet(PROC / "enigh_gasto.parquet")
    gas = gas[gas["ambito"] == AMBITO]
    P = f[[f"p_decil_{k:02d}" for k in range(1, 11)]].to_numpy()
    hog = base["hogares"].to_numpy()
    out, faltan = {}, {}
    for r in rubros_de_giros():
        s = gas[gas["rubro_clave"] == r].set_index("decil")["gasto_trim_prom_hogar"].reindex(range(1, 11))
        if s.isna().all():
            faltan[r] = "NO ENCONTRADO en enigh_gasto (ambito zmvm)"
            continue
        out[f"gasto_pot_{r}_trim"] = hog * (P @ s.fillna(0.0).to_numpy())
    return pd.DataFrame(out, index=base.index), faltan


# =============================================================== 6. reporte
def tabla(df: pd.DataFrame) -> str:
    cab = "| " + " | ".join(map(str, df.columns)) + " |\n|" + "|".join(["---"] * len(df.columns)) + "|\n"
    return cab + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.to_numpy())


def escribir_reporte(base: pd.DataFrame, f: pd.DataFrame, m: dict, v: dict, faltan: dict) -> None:
    nombres = ["Intercepto", "Escolaridad del jefe (anios)", "Tiene auto (0-1)", "Tiene internet (0-1)",
               "Tiene PC/laptop/tablet (0-1)", "Integrantes del hogar"]
    coef = pd.DataFrame({"Variable": nombres, "Coeficiente (log ingreso)": np.round(m["b"], 4),
                         "Error est. (por UPM)": np.round(m["se"], 4),
                         "t": np.round(m["b"] / m["se"], 1)})
    cv = pd.DataFrame({"Modelo": ["Regresion lineal ponderada (el que se usa)", "Gradient boosting (solo comparacion)"],
                       "R2": [round(m["cv_ols"]["r2"], 3), round(m["cv_hgb"]["r2"], 3)],
                       "RMSE log": [round(m["cv_ols"]["rmse"], 3), round(m["cv_hgb"]["rmse"], 3)],
                       "Spearman": [round(m["cv_ols"]["spearman"], 3), round(m["cv_hgb"]["spearman"], 3)],
                       "Decil exacto": [f"{m['cv_ols']['exacto']:.1%}", f"{m['cv_hgb']['exacto']:.1%}"],
                       "Decil +-1": [f"{m['cv_ols']['mas_menos_1']:.1%}", f"{m['cv_hgb']['mas_menos_1']:.1%}"],
                       "Prob. media al decil real": [round(m["cv_ols"]["prob_decil_real"], 3), round(m["cv_hgb"]["prob_decil_real"], 3)]})
    n_ok = int(m["valido"].sum())
    hog = base["hogares"].to_numpy()
    rep = pd.DataFrame({"Decil": range(1, 11),
                        "Hogares esperados (P)": [f"{x:.1%}" for x in v["reparto_prob"]],
                        "Hogares en AGEB con decil modal": [f"{x:.1%}" for x in v["reparto_modal"]]})
    gm = v["gm_tabla"].reset_index().rename(columns={"gm": "Grado de marginacion CONAPO 2020", "count": "AGEB",
                                                     "mean": "Decil imputado medio", "median": "Mediana"})
    gm["Decil imputado medio"] = gm["Decil imputado medio"].round(2)
    orden = {"Muy bajo": 0, "Bajo": 1, "Medio": 2, "Alto": 3, "Muy alto": 4}
    gm = gm.sort_values("Grado de marginacion CONAPO 2020", key=lambda s: s.map(orden))
    nse_n = f["nse"].value_counts()
    nse_h = pd.Series(hog, index=f.index).groupby(f["nse"]).sum()
    ns = pd.DataFrame({"NSE": ["bajo (deciles 1-4)", "medio (5-8)", "alto (9-10)"],
                       "AGEB": [int(nse_n.get(k, 0)) for k in ("bajo", "medio", "alto")],
                       "Hogares": [f"{nse_h.get(k, 0):,.0f}" for k in ("bajo", "medio", "alto")]})
    muni = v["mun_tabla"].reset_index().rename(columns={"cvegeo_mun": "Municipio", "n": "Hogares muestra",
                                                        "ly": "log ingreso ENIGH", "mu_censo": "log ingreso estimado"}).round(3)
    txt = f"""# Decil de ingreso imputado por AGEB

Generado por `scripts/02_features.py` el {date.today().isoformat()}. Es **estimacion en areas pequenas**: el Censo 2020 no
trae ingreso, asi que se aprende en la ENIGH 2024 como se relaciona el ingreso del hogar con rasgos que *tambien* publica
el Censo por AGEB, y se aplica ese modelo a cada AGEB. Es una estimacion, no un dato medido.

## Datos
- ENIGH 2024 (INEGI), `data/processed/enigh_hogares.parquet`, ambito `zmvm` (hogares urbanos de los municipios de la ZMVM,
  de las entidades 09, 13 y 15): **{m['n']:,} hogares muestrales** en {m['upm']} UPM, {m['w_total']/1e6:.2f} millones de hogares expandidos.
  Se excluyeron {m['n_cero']} hogares con ingreso corriente <= 0 (no entran al logaritmo).
- Censo 2020 (INEGI) por AGEB, `data/processed/agebs_base.parquet`: escolaridad promedio, % de viviendas con auto, internet
  y PC, y promedio de ocupantes.
- Los deciles son los de la ENIGH **dentro del ambito `zmvm`** (hogares ordenados por ingreso corriente trimestral y
  cortados en 10 partes iguales con el factor de expansion). Un decil 1 aqui es el 10 % mas pobre **de la ZMVM**, no del pais.
  Los cortes (ingreso trimestral, pesos 2024) son: {', '.join(f'{c:,.0f}' for c in m['cortes'])}.
  Reconstruidos desde esos cortes, coinciden con la columna `decil` de Datos C en {m['acuerdo_decil_cortes']:.1%} de los hogares (ponderado).

## Modelo
`log(ingreso corriente trimestral del hogar) = b0 + b1*escolaridad_jefe + b2*auto + b3*internet + b4*pc + b5*integrantes + e`,
minimos cuadrados ponderados con el factor de expansion; errores estandar robustos por UPM.

{tabla(coef)}

Ajuste dentro de la muestra: R2 ponderado = {m['r2_dentro']:.3f}; desviacion de los residuos (sigma_res) = {m['sigma_res']:.3f} en log.

### Validacion cruzada (5 pliegues por UPM)
{tabla(cv)}

"Prob. media al decil real" es la probabilidad que el modelo asigna al decil verdadero del hogar (azar = 0.100).
El gradient boosting solo se calcula para ver si una forma no lineal ganaria mucho; **se usa la lineal** porque debe poder
aplicarse a promedios de AGEB (una regresion lineal en logs aplicada al promedio de las covariables da el promedio de las
predicciones, un arbol no) y porque se interpreta.

## De AGEB a decil
1. Cada AGEB recibe sus covariables del Censo en la escala de la ENIGH: porcentajes de 0 a 1 para auto, internet y PC;
   `escolaridad_prom` y `prom_ocupantes` tal cual. Los huecos protegidos por el INEGI (`*`) se rellenan con el promedio
   del municipio ponderado por hogares (hasta 2 covariables faltantes; con mas, o sin hogares, la AGEB queda sin decil).
2. Prediccion mu = log del ingreso trimestral tipico del hogar de la AGEB.
3. **Calibracion de nivel**: el Censo mide cosas parecidas pero no iguales (escolaridad de *toda la poblacion de 15+*, no del jefe;
   ocupantes por *vivienda*, no por hogar). Se suma una constante delta = {m['delta']:+.3f} (en log) para que el promedio de mu,
   ponderado por hogares, sea igual al promedio de log(ingreso) de la ENIGH `zmvm`.
4. **Calibracion ecologica (estiramiento)**: entre municipios, el ingreso de la ENIGH sube mucho mas rapido que el modelo de hogares
   (el modelo de hogares esta "aplanado" porque auto o internet de *un* hogar es una medida ruidosa del ingreso; el
   porcentaje de una AGEB promedia ese ruido y ademas refleja el barrio). Regresando el log del ingreso ENIGH sobre mu en los
   {m['n_mun_cal']} municipios con >= 30 hogares muestrales (ponderado por hogares muestrales) sale una pendiente de {m['lam_raw']:.2f}
   (error est. aprox. {m['lam_se']:.2f}; quitando un municipio a la vez: {m['lam_jack'][0]:.2f} a {m['lam_jack'][1]:.2f}). Se estira mu
   alrededor de su promedio con lambda = {m['lam']:.2f} (tope {m['lam_max']:.2f}: con mas, la varianza entre AGEB pasaria la varianza total
   menos la de los residuos). Sin este paso casi ninguna AGEB llegaba al decil 9-10 y Benito Juarez o Miguel Hidalgo quedaban
   claramente por debajo de lo que mide la ENIGH (diferencia media absoluta por municipio {v['mun_dif_antes']:.3f} sin estirar y {v['mun_dif_media_abs']:.3f} con lambda).
   **Es un supuesto fuerte**: la relacion entre municipios se traslada a AGEB; solo la ENIGH por municipio (no por AGEB) permite verificarlo.
5. **Dispersion dentro de la AGEB**: no todos los hogares de una AGEB son iguales. Se toma sigma^2 = Var(log ingreso ENIGH zmvm) -
   Var entre AGEB de mu = {m['var_log']:.3f} - {m['var_entre']:.3f} = {m['sigma2']:.3f}  (sigma = {m['sigma']:.3f};
   la desviacion de los residuos del modelo, {m['sigma_res']:.3f}, es el piso). Incluye lo que el modelo no explica, aunque
   parte sea diferencia entre AGEB: es la eleccion prudente (no sobreestima la certeza).
6. Con ingreso lognormal(mu, sigma) y los cortes de decil de la ENIGH se calcula **P(decil k | AGEB)** para k=1..10
   (columnas `p_decil_01` a `p_decil_10`).
7. `decil_imputado` = decil donde cae el hogar tipico (exp(mu)); `decil_esperado` = sum k*P(k). `nse`: bajo = deciles 1-4,
   medio = 5-8, alto = 9-10 (convencion de este proyecto, no una clasificacion oficial; AMAI usa otra). `p_nse_*` suma las
   probabilidades de cada grupo.

AGEB con decil: {n_ok:,} de {len(base):,}; sin decil: {len(base) - n_ok} (sin hogares, o con mas de 2 covariables protegidas).

## Resultados
Hogares por decil imputado, sumando las AGEB de la ZMVM (si el metodo fuera perfecto, 10 % cada uno):

{tabla(rep)}

NSE por AGEB (decil del hogar tipico):

{tabla(ns)}

### Comprobaciones fuera del ajuste
- **Marginacion CONAPO 2020**: correlacion de Spearman entre mu y el indice de marginacion `im_2020` (alto = menos marginacion)
  en {v['n_im']:,} AGEB = **{v['im_spearman']:.3f}**. Decil imputado medio por grado de marginacion:

{tabla(gm)}

- **Municipios**: se compara el log del ingreso promedio de la ENIGH (municipios con >= 30 hogares muestrales, {v['n_mun']} municipios;
  la ENIGH **no** es representativa por municipio, asi que es una referencia ruidosa) contra el estimado desde el Censo:
  Pearson = {v['mun_pearson']:.3f}, Spearman = {v['mun_spearman']:.3f}, diferencia media absoluta = {v['mun_dif_media_abs']:.3f} en log (esto ya usa lambda, asi que es un ajuste, no una prueba independiente).

{tabla(muni)}

## Gasto potencial por rubro
`gasto_pot_<rubro>_trim` = hogares de la AGEB x sum_k P(decil k) x gasto trimestral promedio del hogar en el decil k
(`enigh_gasto.parquet`, ambito `zmvm`, el mismo en que se definieron los deciles; pesos corrientes de 2024, el promedio cuenta
los ceros). Rubros calculados: los `rubro_enigh` y `rubro_enigh_alt` de `config/giros.yaml` ({len([c for c in f.columns if c.startswith('gasto_pot_')])} columnas).
{('Sin dato: ' + '; '.join(f'{k} ({x})' for k, x in faltan.items())) if faltan else 'Todos los rubros tienen dato.'}
Avisos: en rubros con pocos hogares que gastan (helados 2-7 %, lavanderia, idiomas) el promedio por decil es ruidoso y no
siempre sube con el decil; sirve para ordenar zonas, no para dimensionar ventas.

## Limites (leer antes de usar el decil)
- El decil es de un **hogar tipico** de la AGEB. Una AGEB con decil 6 puede tener hogares de todos los deciles; por eso se
  guardan las probabilidades, y el gasto potencial las usa en vez del decil solo.
- La ENIGH 2024 es de 2024 y el Censo de 2020; entre ambos hubo inflacion y cambios en internet y escolaridad. Los cortes en pesos
  son de 2024. Con Censo mas viejo que ENIGH, el nivel se calibra con delta, pero el *orden* entre AGEB no se corrige.
- Modelo con 5 covariables: explica una parte del ingreso (R2 arriba). Zonas con ingreso alto sin auto ni internet
  distintos (p. ej. departamentos de lujo con poco auto) se subestiman, y los barrios con muchos hogares de renta o remesas, tambien.
- La pendiente municipal (lambda) sale de 35 puntos ruidosos (la ENIGH no representa municipios); el *orden* de las AGEB no depende
  de ella (esta confirmado por CONAPO), pero cuantas AGEB caen en deciles extremos si.
- Escolaridad: la ENIGH aqui es del jefe del hogar (aproximacion por niveles; ver BITACORA de Datos C); el Censo es de toda
  la poblacion de 15+. La constante delta absorbe la diferencia promedio, no la que cambie de una AGEB a otra.
"""
    REPORTE.parent.mkdir(exist_ok=True)
    REPORTE.write_text(txt, encoding="utf-8")


# =============================================================== principal
def main() -> None:
    t = t0()
    base = gpd.read_parquet(PROC / "agebs_base.parquet")
    log(f"base: {len(base)} AGEB")
    den = motor.denue("actual").merge(
        pd.read_parquet(PROC / "denue_actual.parquet", columns=["id", "nom_asent", "tipo_asent", "cod_postal"]),
        on="id", how="left")
    log(f"DENUE actual: {len(den):,} establecimientos con coordenadas ({time.time() - t:.0f} s)")

    out = base.copy()
    out["densidad_hab_km2"] = out["pob_total"] / out["area_km2"]
    for df in (nombre_colonia(base, den), features_denue(base, den), features_transporte(base)):
        out = out.merge(df, on="cvegeo", how="left", validate="1:1")
    log(f"DENUE y transporte listos ({time.time() - t:.0f} s)")

    f, m = imputar_decil(base)
    out = out.merge(f, on="cvegeo", how="left", validate="1:1")
    v = validar_decil(base, f, m)
    gas, faltan = gasto_por_rubro(base, f)
    out = pd.concat([out.reset_index(drop=True), gas.reset_index(drop=True)], axis=1)
    log(f"decil y gasto listos ({time.time() - t:.0f} s); R2 cv={m['cv_ols']['r2']:.3f}, Spearman vs CONAPO={v['im_spearman']:.3f}")

    gpd.GeoDataFrame(out, geometry="geometry", crs=base.crs).to_parquet(SALIDA, index=False)
    escribir_reporte(base, f, m, v, faltan)
    res = {"filas": len(out), "columnas": out.shape[1], "con_decil": int(m["valido"].sum()),
           "r2_cv": m["cv_ols"]["r2"], "delta": m["delta"], "sigma": m["sigma"], "im_spearman": v["im_spearman"],
           "rubros_sin_dato": faltan, "segundos": round(time.time() - t)}
    (PROC / "_resumen_02.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"listo: {SALIDA.name} {out.shape} en {time.time() - t:.0f} s")


if __name__ == "__main__":
    main()
