"""Etapa Score: valida el score de `score_giro` contra objetivos que SI corresponden a una decision de ubicacion,
aprende sus pesos fuera de muestra y escribe reports/validacion_score.md.

Por que: el score se media contra «aparecio un negocio del giro en la AGEB» y salia peor que lineas base ingenuas
(AUC 0.58 contra 0.71 de la competencia en la AGEB). Pero un score que castiga la competencia no puede predecir
aperturas crudas, que se aglomeran donde ya hay competidores. Aqui se mide lo que importa a quien abre un negocio.

Objetivos, por (AGEB, giro), con los cortes DENUE 11/2020 y 05/2026, medidos en el MISMO circulo (radio_influencia_m,
peso Huff) que usa el score, con al menos H_MIN establecimientos ponderados del giro en 2020:
  - sobrevivencia      : de los establecimientos del giro de 2020 en el circulo, cuantos siguen en 2026 (mismo id o mismo
                         nombre a <= 50 m, igual que 03_entrenar.py);
  - crecimiento neto   : (aperturas - cierres) / establecimientos de 2020;
  - altas reales       : aperturas con fecha_alta distinta de 2024 (fuera de la carga de los Censos Economicos 2024) / estab. 2020;
  - aperturas crudas   : referencia (lo que se usaba), AUC de «aparecio >= 1 en la AGEB».
«Aparecio» no es «abrio» y «desaparecio» no es «cerro»: ver reports/validacion.md.

Validacion espacial: GroupKFold por municipio (los mismos 5 pliegues del modelo de aperturas). Los pesos se ajustan
en 4 pliegues y se reportan en el que no vieron. Los pesos entregados se ajustan con todo y se redondean a 0.05.

Entradas: models/oof.parquet, models/etiquetas.parquet (corre antes 03_entrenar.py), data/processed.
Salidas: models/pesos_score.json, models/validacion_score.csv, models/oof_sobrevive.parquet (cache),
reports/validacion_score.md; actualiza models/metadata.json, models/metricas_giro.csv y models/oof.parquet
(columna score_comb) para que describan el score vigente.

Uso:  OMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03b_validar_score.py   (~5 min; con nohup)
      ... --solo-reporte   (no reaprende pesos: usa models/pesos_score.json)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from app import motor  # noqa: E402

PROC = RAIZ / "data" / "processed"
MODELS = RAIZ / "models"
REPORTE = RAIZ / "reports" / "validacion_score.md"
H_MIN = 3.0            # establecimientos ponderados (Huff) del giro en 2020 dentro del circulo para medir tasas
MIN_AGEB = 200         # AGEB elegibles minimas para que un giro cuente en un objetivo
MIN_POS = 30           # positivos minimos para un AUC
N_PLIEGUES = 5
PISO_DEMANDA = 0.25    # demanda_neta + pob_neta pesan al menos esto (a priori de teoria, ver reporte)
PASO_REDONDEO = 0.05
SEMILLA = 0
TERMINOS = ["prob_apertura", "demanda_neta", "pob_neta", "flujo", "complementarios"]
PESOS_V21 = {"prob_apertura": 0.30, "demanda_neta": 0.25, "pob_neta": 0.15, "flujo": 0.20, "complementarios": 0.10}
OBJ_APRENDER = ["crecimiento_neto", "sobrevivencia", "altas_reales"]   # pesan igual al aprender
# Sensibilidad (no se entrega): sin el objetivo contaminado por la carga de los Censos Economicos 2024. Ver el reporte, seccion 3.
OBJ_LIMPIOS = ["sobrevivencia", "altas_reales", "neto_sin_carga"]
NOMBRE_OBJ = {"crecimiento_neto": "Crecimiento neto", "sobrevivencia": "Sobrevivencia", "altas_reales": "Altas fuera de la carga censal",
              "neto_sin_carga": "Crecimiento neto sin carga censal", "aperturas_crudas": "Aperturas crudas (referencia)"}
NOMBRE_PUNT = {"score_v21": "Score anterior (v2.1, pesos del autor)", "score_nuevo": "Score nuevo, pesos entregados (dentro de muestra)",
               "score_nuevo_oos": "Score nuevo, pesos fuera de muestra (cifra principal)", "nucleo": "Núcleo: aperturas por competidor",
               "aperturas_esperadas": "Aperturas esperadas (modelo)", "captura_huff": "Captura Huff (1/(1+competidores))",
               "demanda_neta": "Gasto potencial × captura", "pob_neta": "Población objetivo × NSE × captura",
               "flujo": "Flujo de gente (proxy)", "complementarios": "Complementarios", "prob_modelo": "Prob. de apertura de la AGEB (modelo)",
               "prob_sobrevive": "Prob. de seguir abierto (modelo dedicado)", "densidad": "Densidad de población",
               "comp_huff": "Competencia Huff", "comp_ageb": "Competencia en la AGEB", "actividad": "Actividad (negocios a 500 m)",
               "score_limpio_oos": "Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra)"}
BASES = ["densidad", "comp_huff", "comp_ageb", "actividad"]   # lineas base ingenuas


def log(msg: str) -> None:
    print(f"[03b_validar_score {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def cargar_entrenar():
    """03_entrenar.py empieza con un digito: se importa por ruta."""
    spec = importlib.util.spec_from_file_location("entrenar03", RAIZ / "scripts" / "03_entrenar.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# =============================================================== 1. base: componentes y objetivos por (AGEB, giro)
def base_hist(ent) -> tuple[pd.DataFrame, dict]:
    """Una fila por (AGEB, giro) con los componentes del score en el corte 11/2020 (probabilidad fuera de pliegue)
    y los objetivos medidos en el circulo del giro. Devuelve tambien las pruebas del cruce de etiquetas."""
    oof = pd.read_parquet(MODELS / "oof.parquet")
    et, _, res, (h, nuevo, nreal) = ent.etiquetas(con_puntos=True)
    partes = []
    pob_total, pob_radio = motor.cargar_features()["pob_total"], {}
    for g, cfg in motor.giros().items():
        fg = motor.features_giro(g, "hist")
        o = oof[oof["giro"] == g].set_index("cvegeo")
        p = o["oof"].reindex(fg.index).to_numpy()
        c = motor.combinar_score(g, fg, p, corte="hist")
        c.index = fg.index
        c["comp_huff"] = fg["comp_huff"].to_numpy()
        c["comp_ageb"] = fg["comp_ageb"].to_numpy()
        for col in ("densidad_hab_km2", "estab_500m"):
            c[col] = o[col].reindex(fg.index).to_numpy()
        r = float(cfg["radio_influencia_m"])
        sc, fl = cfg.get("scian", []), cfg.get("scian_con_filtro")
        hg, ng, rg = (motor.seleccionar(x, sc, fl) for x in (h, nuevo, nreal))
        c["H"] = motor.suma_radial(hg.x.to_numpy(), hg.y.to_numpy(), None, r).to_numpy()
        c["Sv"] = motor.suma_radial(hg.x.to_numpy(), hg.y.to_numpy(), hg["sobrevive"].to_numpy(float), r).to_numpy()
        c["A"] = motor.suma_radial(ng.x.to_numpy(), ng.y.to_numpy(), None, r).to_numpy()
        c["Ar"] = motor.suma_radial(rg.x.to_numpy(), rg.y.to_numpy(), None, r).to_numpy()
        if r not in pob_radio:
            pob_radio[r] = motor.suma_dasimetrica(pob_total, r)
        c["pob_radio"] = pob_radio[r].reindex(fg.index).to_numpy()
        assert np.allclose(c["H"], c["comp_huff"], rtol=1e-6), g   # H es la misma competencia Huff del score
        c["giro"] = g
        partes.append(c.rename_axis("cvegeo").reset_index())
    d = pd.concat(partes, ignore_index=True)
    d = d.merge(et, on=["cvegeo", "giro"], how="left", validate="1:1")
    d["cvegeo_mun"] = d["cvegeo"].str[:5]
    d["oof"] = oof.set_index(["cvegeo", "giro"])["oof"].reindex(pd.MultiIndex.from_frame(d[["cvegeo", "giro"]])).to_numpy()
    return d, res


def terminos_v21(d: pd.DataFrame) -> pd.Series:
    """Score v2.1: mismos terminos, pero el primero es el percentil de las aperturas esperadas a secas."""
    pct = {"prob_apertura": d["pct_aperturas_esperadas"], "demanda_neta": d["pct_demanda_neta"], "pob_neta": d["pct_pob_neta"],
           "flujo": d["pct_flujo"], "complementarios": d["pct_complementarios"]}
    w = dict(PESOS_V21)
    sin_enigh = d["demanda"].isna().groupby(d["giro"]).transform("all")     # coworking: su peso pasa a pob_neta
    s = sum(w[k] * pct[k] for k in TERMINOS)
    s = np.where(sin_enigh, s - w["demanda_neta"] * pct["demanda_neta"] + w["demanda_neta"] * pct["pob_neta"], s)
    return pd.Series(100.0 * s, index=d.index)


def asignar_pliegues(d: pd.DataFrame) -> pd.Series:
    """Los mismos pliegues del modelo de aperturas: GroupKFold por municipio sobre la tabla (giro, AGEB) en su orden."""
    o = pd.read_parquet(MODELS / "oof.parquet", columns=["cvegeo", "giro"])
    gr = o["cvegeo"].str[:5].to_numpy()
    fold = np.zeros(len(o), int)
    for k, (_, te) in enumerate(GroupKFold(n_splits=N_PLIEGUES).split(np.zeros(len(o)), groups=gr)):
        fold[te] = k
    mf = pd.Series(fold, index=gr).groupby(level=0).first()
    return d["cvegeo_mun"].map(mf).astype(int)


def objetivos(d: pd.DataFrame) -> pd.DataFrame:
    """Columnas objetivo en el circulo del giro; NaN donde hay menos de H_MIN establecimientos de 2020."""
    ok = d["H"] >= H_MIN
    H = d["H"].where(ok)
    d = d.copy()
    d["cierres"] = d["H"] - d["Sv"]
    d["sobrevivencia"] = d["Sv"] / H
    d["crecimiento_neto"] = (d["A"] - d["cierres"]) / H
    d["altas_reales"] = d["Ar"] / H
    d["neto_sin_carga"] = (d["Ar"] - d["cierres"]) / H    # crecimiento neto SIN la carga de los Censos Economicos 2024 (solo altas reales)
    d["neto_absoluto"] = d["A"] - d["cierres"]                                    # robustez: sin normalizar
    d["neto_por_10mil_hab"] = 1e4 * d["neto_absoluto"] / d["pob_radio"].clip(lower=1000)   # robustez: por habitante
    return d


def sobrevivencia_oof(ent, d: pd.DataFrame) -> pd.Series:
    """P(seguir abierto) de un local nuevo (0-5 personas) en cada (AGEB, giro), fuera de pliegue por municipio.
    Es el modelo de sobrevivencia de 03_entrenar.py ajustado en 4 pliegues. Se guarda en models/oof_sobrevive.parquet."""
    f = MODELS / "oof_sobrevive.parquet"
    if f.exists():
        c = pd.read_parquet(f)
        if len(c) == len(d):
            return c.set_index(["cvegeo", "giro"])["prob_sobrevive_oof"].reindex(pd.MultiIndex.from_frame(d[["cvegeo", "giro"]])).to_numpy()
    log("modelo de sobrevivencia fuera de pliegue (~2 min)")
    _, estab, _ = ent.etiquetas()
    mh = motor.matriz_modelo("hist")
    cols = json.loads((MODELS / "metadata.json").read_text(encoding="utf-8"))["features_sobrevivencia"]
    de = estab.merge(mh, on=["cvegeo", "giro"], how="left")
    X, y = de[cols], de["sobrevive"].to_numpy().astype(int)
    fe = de["cvegeo_mun"].map(d.drop_duplicates("cvegeo_mun").set_index("cvegeo_mun")["pliegue"]).to_numpy()
    mh = mh.assign(per_ocu_medio=np.float32(2.5))
    fm = mh["cvegeo_mun"].map(d.drop_duplicates("cvegeo_mun").set_index("cvegeo_mun")["pliegue"]).to_numpy()
    p = np.zeros(len(mh))
    for k in range(N_PLIEGUES):
        clf = ent.modelo().fit(X[fe != k], y[fe != k])
        p[fm == k] = clf.predict_proba(mh.loc[fm == k, cols])[:, 1]
        log(f"  sobrevivencia pliegue {k}")
    out = pd.DataFrame({"cvegeo": mh["cvegeo"].to_numpy(), "giro": mh["giro"].to_numpy(), "prob_sobrevive_oof": p})
    out.to_parquet(f, index=False)
    return out.set_index(["cvegeo", "giro"])["prob_sobrevive_oof"].reindex(pd.MultiIndex.from_frame(d[["cvegeo", "giro"]])).to_numpy()


# =============================================================== 2. aprender pesos fuera de muestra
def preparar_aprendizaje(d: pd.DataFrame, objs: list[str] | None = None) -> dict:
    """Por giro con datos suficientes: percentiles de los terminos (n x 5), rangos z de los 3 objetivos (n x 3), pliegue."""
    G = {}
    for g, x in d[(d["H"] >= H_MIN) & (d["giro"] != "coworking")].groupby("giro"):
        if len(x) < MIN_AGEB:
            continue
        R = np.column_stack([x[o].rank(pct=True).to_numpy() for o in (objs or OBJ_APRENDER)])
        R = (R - R.mean(0)) / (R.std(0) + 1e-12)
        G[g] = (x[[f"pct_{k}" for k in TERMINOS]].to_numpy(), R, x["pliegue"].to_numpy())
    return G


def _perdida(w, G, excluir):
    """- media (giros, objetivos) de la correlacion entre el score y el rango de cada objetivo, sin el pliegue `excluir`."""
    tot, n = 0.0, 0
    for A, R, f in G.values():
        m = (f != excluir) if excluir is not None else np.ones(len(f), bool)
        s = A[m] @ w
        s = (s - s.mean()) / (s.std() + 1e-12)
        tot += float((s @ R[m]).mean() / m.sum())
        n += 1
    return -tot / max(n, 1)


def ajustar_pesos(G: dict, excluir: int | None, piso: float = PISO_DEMANDA) -> np.ndarray:
    i_dem, i_pob = TERMINOS.index("demanda_neta"), TERMINOS.index("pob_neta")
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}, {"type": "ineq", "fun": lambda w: w[i_dem] + w[i_pob] - piso}]
    mejor = None
    for w0 in (np.full(len(TERMINOS), 1 / len(TERMINOS)), np.array([0.5, 0.1, 0.1, 0.1, 0.2])):
        r = minimize(_perdida, w0, args=(G, excluir), bounds=[(0, 1)] * len(TERMINOS), constraints=cons,
                     method="SLSQP", options={"maxiter": 80})
        if mejor is None or r.fun < mejor.fun:
            mejor = r
    w = np.clip(mejor.x, 0, None)
    return w / w.sum()


def redondear(w: np.ndarray, paso: float = PASO_REDONDEO, piso: float = PISO_DEMANDA) -> np.ndarray:
    """Redondea a multiplos de `paso` repartiendo el resto por mayor residuo; respeta suma 1 y el piso de demanda."""
    u = w / paso
    r = np.floor(u).astype(int)
    faltan = int(round(1 / paso)) - r.sum()
    for i in np.argsort(-(u - r))[:max(faltan, 0)]:
        r[i] += 1
    out = r * paso
    i_dem, i_pob = TERMINOS.index("demanda_neta"), TERMINOS.index("pob_neta")
    while out[i_dem] + out[i_pob] < piso - 1e-9:        # sube demanda/poblacion quitando al termino mas grande de los otros
        otros = [j for j in range(len(out)) if j not in (i_dem, i_pob)]
        j = max(otros, key=lambda t: out[t])
        out[j] -= paso
        out[i_pob] += paso
    return np.round(out, 4)


def sensibilidad_limpia(d: pd.DataFrame) -> dict:
    """Sensibilidad: pesos aprendidos SOLO con objetivos sin carga censal (sobrevivencia, altas reales y crecimiento neto sin
    carga). No se entrega: sirve para ver que pasa si se le quita al aprendizaje el objetivo contaminado."""
    G = preparar_aprendizaje(d, OBJ_LIMPIOS)
    por_pliegue = np.array([ajustar_pesos(G, k) for k in range(N_PLIEGUES)])
    final = ajustar_pesos(G, None)
    red = redondear(final)
    oos = np.zeros(len(d))
    for k in range(N_PLIEGUES):
        m = (d["pliegue"] == k).to_numpy()
        oos[m] = aplicar_pesos(d[m], dict(zip(TERMINOS, por_pliegue[k]))).to_numpy()
    log("  sensibilidad (objetivos limpios): " + ", ".join(f"{t}={w:.2f}" for t, w in zip(TERMINOS, red)))
    return {"pesos": dict(zip(TERMINOS, red.tolist())), "oos": oos}


def aprender(d: pd.DataFrame) -> dict:
    G = preparar_aprendizaje(d)
    log(f"aprendizaje: {len(G)} giros, piso de demanda {PISO_DEMANDA}")
    por_pliegue = []
    for k in range(N_PLIEGUES):
        por_pliegue.append(ajustar_pesos(G, k))
        log(f"  pliegue {k}: " + ", ".join(f"{t}={w:.2f}" for t, w in zip(TERMINOS, por_pliegue[-1])))
    sin_piso = [ajustar_pesos(G, k, piso=0.0) for k in range(N_PLIEGUES)]
    final = ajustar_pesos(G, None)
    red = redondear(final)
    log("  final: " + ", ".join(f"{t}={w:.3f}" for t, w in zip(TERMINOS, final)) + " -> redondeado " + str(dict(zip(TERMINOS, red))))
    return {"por_pliegue": np.array(por_pliegue), "sin_piso": np.array(sin_piso), "final": final, "redondeado": red, "giros": sorted(G)}


def aplicar_pesos(d: pd.DataFrame, w: dict) -> pd.Series:
    """score 0-100 con pesos `w` sobre los percentiles pct_* (coworking: el peso de demanda_neta pasa a pob_neta)."""
    s = sum(w[k] * d[f"pct_{k}"] for k in TERMINOS)
    sin_enigh = d["demanda"].isna().groupby(d["giro"]).transform("all")
    s = np.where(sin_enigh, s - w["demanda_neta"] * d["pct_demanda_neta"] + w["demanda_neta"] * d["pct_pob_neta"], s)
    return pd.Series(100.0 * s / sum(w.values()), index=d.index)


# =============================================================== 3. evaluacion
def rho(y, s) -> float:
    ok = np.isfinite(y) & np.isfinite(s)
    if ok.sum() < 30 or np.ptp(s[ok]) == 0 or np.ptp(y[ok]) == 0:
        return np.nan
    return float(spearmanr(s[ok], y[ok]).statistic)


def auc(y, s) -> float:
    ok = np.isfinite(y) & np.isfinite(s)
    if ok.sum() < 30 or not (MIN_POS <= y[ok].sum() <= ok.sum() - MIN_POS):
        return np.nan
    return float(roc_auc_score(y[ok], s[ok]))


def cima(num, den, s, q):
    """(lift, diferencia en puntos) de la tasa en el q superior segun s contra la tasa base del giro."""
    k = max(1, int(round(len(s) * q)))
    top = np.argsort(-s, kind="stable")[:k]
    t, b = num[top].sum() / max(den[top].sum(), 1e-12), num.sum() / max(den.sum(), 1e-12)
    return (t / b if b > 0 else np.nan), float(t - b)


def evaluar(d: pd.DataFrame, puntuaciones: dict[str, str]) -> pd.DataFrame:
    """Una fila por (objetivo, giro, puntuacion): rho o AUC y cima del 5 y 10 %."""
    filas = []
    num = {"crecimiento_neto": d["A"] - d["cierres"], "sobrevivencia": d["Sv"], "altas_reales": d["Ar"],
           "neto_sin_carga": d["Ar"] - d["cierres"]}
    for obj in ("crecimiento_neto", "sobrevivencia", "altas_reales", "neto_sin_carga", "aperturas_crudas", "neto_absoluto", "neto_por_10mil_hab"):
        for g, x in d.groupby("giro"):
            if obj == "aperturas_crudas":
                idx = x.index
                y = x["y_apertura"].to_numpy(float)
                nu, de = y, np.ones(len(x))
            elif obj in ("neto_absoluto", "neto_por_10mil_hab"):   # robustez: todas las AGEB, sin lift
                idx = x.index
                y = x[obj].to_numpy(float)
                nu, de = None, None
            else:
                x = x[x["H"] >= H_MIN]
                if len(x) < MIN_AGEB:
                    continue
                idx = x.index
                y = x[obj].to_numpy(float)
                nu, de = num[obj].loc[idx].to_numpy(float), x["H"].to_numpy(float)
            if obj == "aperturas_crudas" and not (MIN_POS <= y.sum() <= len(y) - MIN_POS):
                continue
            for nom, col in puntuaciones.items():
                s = x[col].to_numpy(float)
                ok = np.isfinite(s)
                if ok.sum() < 30:
                    continue
                v = auc(y, s) if obj == "aperturas_crudas" else rho(y, s)
                f = {"objetivo": obj, "giro": g, "puntuacion": nom, "metrica": "auc" if obj == "aperturas_crudas" else "rho",
                     "valor": v, "n": int(len(x))}
                s0 = np.where(ok, s, -np.inf)
                for q in (0.05, 0.10):
                    f[f"lift{int(q * 100)}"], f[f"dpp{int(q * 100)}"] = cima(nu, de, s0, q) if nu is not None else (np.nan, np.nan)
                    if obj in ("crecimiento_neto", "neto_sin_carga"):    # la tasa base es ~0 o negativa: el cociente no significa nada, solo la diferencia
                        f[f"lift{int(q * 100)}"] = np.nan
                filas.append(f)
    return pd.DataFrame(filas)


def resumen(r: pd.DataFrame) -> pd.DataFrame:
    """Promedio entre giros por (objetivo, puntuacion): valor, error estandar entre giros, lifts y diferencia en puntos."""
    def agg(x):
        v = x["valor"].dropna()
        return pd.Series({"giros": len(v), "valor": v.mean(), "ee": v.std() / np.sqrt(max(len(v), 1)),
                          "lift5": x["lift5"].replace([np.inf, -np.inf], np.nan).mean(), "lift10": x["lift10"].replace([np.inf, -np.inf], np.nan).mean(),
                          "dpp5": x["dpp5"].mean(), "dpp10": x["dpp10"].mean()})
    return r.groupby(["objetivo", "puntuacion"]).apply(agg, include_groups=False).reset_index()


def minus(t: str) -> str:
    return t[0].lower() + t[1:]


def mejor_base(res: pd.DataFrame, obj: str) -> tuple[str, float]:
    """Linea base ingenua con mayor valor absoluto medio (se le da su mejor direccion: a favor o en contra)."""
    r = res[(res["objetivo"] == obj) & res["puntuacion"].isin(BASES)]
    centro = 0.5 if obj == "aperturas_crudas" else 0.0
    i = (r["valor"] - centro).abs().idxmax()
    return r.loc[i, "puntuacion"], float(abs(r.loc[i, "valor"] - centro) + centro)


# =============================================================== 4. diagnostico de la hipotesis
def diagnostico(d: pd.DataFrame) -> dict:
    out = {}
    # (a) aperturas segun competidores previos en la AGEB (nivel AGEB, como el modelo)
    filas = []
    for g, x in d.groupby("giro"):
        b = pd.cut(x["n_hist"], [-1, 0, 2, 10**6], labels=["0", "1-2", "3+"])
        t = x.groupby(b, observed=True)["y_apertura"].agg(["mean", "size"])
        if len(t) == 3 and (t["size"] >= 30).all():
            r3 = x[x["n_hist"] >= 3]
            filas.append({"giro": g, "p0": t.loc["0", "mean"], "p12": t.loc["1-2", "mean"], "p3": t.loc["3+", "mean"],
                          "aper_por_estab": r3["n_aperturas"].sum() / max(r3["n_hist"].sum(), 1),
                          "cierres_por_estab": (r3["n_hist"] - r3["n_sobreviven"]).sum() / max(r3["n_hist"].sum(), 1)})
    t = pd.DataFrame(filas)
    out["bins"] = {c: float(t[c].mean()) for c in ("p0", "p12", "p3", "aper_por_estab", "cierres_por_estab")}
    out["bins_giros"] = len(t)
    # (b) rotacion: correlacion entre aperturas y cierres por AGEB
    rot = [spearmanr(x["n_aperturas"], x["n_hist"] - x["n_sobreviven"]).statistic for _, x in d[d["n_hist"] >= 3].groupby("giro") if len(x) >= MIN_AGEB]
    out["rho_aper_cierres"] = float(np.nanmean(rot))
    out["rho_aper_cierres_giros"] = len(rot)
    out["pct_carga_censal"] = float(1 - d["n_aperturas_reales"].sum() / d["n_aperturas"].sum())
    el = d[d["H"] >= H_MIN]    # entre las AGEB elegibles (las que miden los objetivos), en los circulos ponderados del giro
    out["pct_carga_elegibles"] = float(1 - el["Ar"].sum() / el["A"].sum())
    q = pd.qcut(el["H"].rank(method="first"), 4, labels=False)
    out["carga_por_cuartil_H"] = [float(1 - g["Ar"].sum() / g["A"].sum()) for _, g in el.groupby(q)]
    out["a_sobre_h_mediana_por_cuartil_H"] = [float((g["A"] / g["H"]).median()) for _, g in el.groupby(q)]
    # (c) elasticidad: log(1+aperturas) ~ log(1+estab. 2020) + log(poblacion) + efectos fijos de giro, error por municipio
    f = motor.cargar_features()["pob_total"]
    x = d[["cvegeo", "giro", "cvegeo_mun", "n_aperturas", "n_hist"]].copy()
    x["lpob"] = np.log(x["cvegeo"].map(f).clip(lower=100))
    x["ly"], x["lh"] = np.log1p(x["n_aperturas"]), np.log1p(x["n_hist"])
    for c in ("ly", "lh", "lpob"):
        x[c] = x[c] - x.groupby("giro")[c].transform("mean")
    X, y = x[["lh", "lpob"]].to_numpy(), x["ly"].to_numpy()
    b = np.linalg.solve(X.T @ X, X.T @ y)
    e = y - X @ b
    A = np.linalg.inv(X.T @ X)
    S = pd.DataFrame(X * e[:, None]).groupby(x["cvegeo_mun"].to_numpy()).sum().to_numpy()
    se = np.sqrt(np.diag(A @ (S.T @ S) @ A))
    out["elasticidad"] = {"b_comp": float(b[0]), "se_comp": float(se[0]), "b_pob": float(b[1]), "se_pob": float(se[1]),
                          "r2": float(1 - (e ** 2).sum() / (y ** 2).sum())}
    return out


# =============================================================== 5. decil imputado por bandas de NSE
def exactitud_nse() -> dict:
    """Repite la validacion cruzada del decil imputado (scripts/02_features.py: regresion lineal ponderada, 5 pliegues por
    UPM) y mide la exactitud por banda de NSE (bajo 1-4, medio 5-8, alto 9-10), que es lo que usa el producto."""
    spec = importlib.util.spec_from_file_location("feat02", RAIZ / "scripts" / "02_features.py")
    f2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f2)
    en = pd.read_parquet(PROC / "enigh_hogares.parquet")
    h = en[(en["ambito"] == f2.AMBITO) & (en["ing_cor"] > 0)].reset_index(drop=True)
    y, w = np.log(h["ing_cor"].to_numpy()), h["factor"].to_numpy(float)
    X = np.column_stack([np.ones(len(h))] + [h[c].astype(float).to_numpy() for c in f2.COVARIABLES])
    cortes, dec = f2.deciles_cortes(h), h["decil"].to_numpy()
    pred = np.zeros(len(h))
    res_sd = 0.0
    for tr, te in GroupKFold(n_splits=5).split(X, y, groups=h["upm"]):
        pred[te] = X[te] @ f2.wls(X[tr], y[tr], w[tr])
    b = f2.wls(X, y, w)
    sigma = float(np.sqrt(np.average((y - X @ b) ** 2, weights=w)))
    dp = f2.decil_de(np.exp(pred), cortes)
    banda = lambda z: np.where(z <= 4, 0, np.where(z <= 8, 1, 2))  # noqa: E731
    br, bp = banda(dec), banda(dp)
    nombres = ["bajo", "medio", "alto"]
    P = f2.probs_decil(pred, sigma, cortes)
    pb = np.column_stack([P[:, :4].sum(1), P[:, 4:8].sum(1), P[:, 8:].sum(1)])
    conf = np.array([[np.sum(w[(br == i) & (bp == j)]) for j in range(3)] for i in range(3)])
    conf = conf / conf.sum(1, keepdims=True)
    comp = np.array([np.average(br == i, weights=w) for i in range(3)])
    return {"n": int(len(h)), "upm": int(h["upm"].nunique()),
            "decil_exacto": float(np.average(dp == dec, weights=w)), "decil_mas_menos_1": float(np.average(np.abs(dp - dec) <= 1, weights=w)),
            "banda_exacta": float(np.average(bp == br, weights=w)),
            "recall": {n: float(conf[i, i]) for i, n in enumerate(nombres)},
            "confusion": conf.round(4).tolist(), "composicion": dict(zip(nombres, comp.round(4).tolist())),
            "grave": float(np.average(np.abs(bp - br) == 2, weights=w)),
            "prob_media_banda_real": float(np.average(pb[np.arange(len(h)), br], weights=w)),
            "prob_azar": float(np.sum(comp ** 2)),
            "mayoritaria": float(comp.max())}


# =============================================================== 6. sincronizar archivos que describen el score vigente
def sincronizar(ent, d: pd.DataFrame, w: dict, apren: dict | None) -> None:
    """models/pesos_score.json, models/metadata.json, models/metricas_giro.csv y la columna score_comb de oof.parquet."""
    if apren is not None:
        (MODELS / "pesos_score.json").write_text(json.dumps(
            {"version": motor.SCORE_VERSION, "fecha": date.today().isoformat(), "pesos": w,
             "pesos_sin_redondear": dict(zip(TERMINOS, apren["final"].round(4).tolist())),
             "pesos_por_pliegue": [dict(zip(TERMINOS, p.round(4).tolist())) for p in apren["por_pliegue"]],
             "pesos_por_pliegue_sin_piso": [dict(zip(TERMINOS, p.round(4).tolist())) for p in apren["sin_piso"]],
             "piso_demanda": PISO_DEMANDA, "objetivos_que_aprende": OBJ_APRENDER, "h_min": H_MIN,
             "giros_en_el_aprendizaje": apren["giros"], "origen": "scripts/03b_validar_score.py"},
            indent=1, ensure_ascii=False), encoding="utf-8")
        motor.PESOS_SCORE.clear()
        motor.PESOS_SCORE.update(w)
    mp = MODELS / "metadata.json"
    meta = json.loads(mp.read_text(encoding="utf-8"))
    meta["pesos_score"] = w
    meta["score_version"] = motor.SCORE_VERSION
    meta["validacion_score"] = "reports/validacion_score.md"
    mp.write_text(json.dumps(meta, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    o = pd.read_parquet(MODELS / "oof.parquet")
    k = pd.MultiIndex.from_frame(o[["cvegeo", "giro"]])
    o["score_comb"] = d.set_index(["cvegeo", "giro"])["score_nuevo"].reindex(k).to_numpy()
    o["score_v21"] = d.set_index(["cvegeo", "giro"])["score_v21"].reindex(k).to_numpy()
    o.to_parquet(MODELS / "oof.parquet", index=False)
    mg = pd.read_csv(MODELS / "metricas_giro.csv")
    nuevo = ent.metricas_giro(o.assign(n_aperturas=o["n_aperturas"]), {"score": "score_comb", "score_v21": "score_v21"})
    cols = [c for c in nuevo.columns if c.endswith("_score") or c.endswith("_score_v21")]
    mg = mg.drop(columns=[c for c in mg.columns if c in cols]).merge(nuevo[["giro"] + cols], on="giro", how="left")
    mg.to_csv(MODELS / "metricas_giro.csv", index=False)
    log("sincronizados: metadata.json, metricas_giro.csv, oof.parquet")


# =============================================================== 7. reporte
def fz(v, n=3, signo=False) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    return f"{v:+.{n}f}" if signo else f"{v:.{n}f}"


def escribir_reporte(d, res, resu, diag, nse, apren, w, sens) -> None:
    L = []
    a = L.append
    nombres_w = {"prob_apertura": "núcleo: aperturas esperadas por competidor", "demanda_neta": "gasto potencial × captura Huff",
                 "pob_neta": "población objetivo × NSE × captura", "flujo": "flujo de gente (proxy)", "complementarios": "complementarios"}
    wv = {k: PESOS_V21[k] for k in TERMINOS}
    n_giros = {o: int(resu[(resu["objetivo"] == o) & (resu["puntuacion"] == "score_nuevo")]["giros"].iloc[0]) for o in NOMBRE_OBJ}
    n_giros["aperturas_crudas"] = int(resu[(resu["objetivo"] == "aperturas_crudas") & (resu["puntuacion"] == "score_nuevo")]["giros"].iloc[0])

    def v(obj, p, col="valor"):
        r = resu[(resu["objetivo"] == obj) & (resu["puntuacion"] == p)]
        return float(r[col].iloc[0]) if len(r) else np.nan

    a("# Validación del score: ¿predice algo que le importe a quien abre un negocio?\n")
    a(f"Generado por `scripts/03b_validar_score.py` el {date.today().isoformat()} · score `{motor.SCORE_VERSION}` · "
      "datos: DENUE 11/2020 y 05/2026 (INEGI), Censo 2020 (INEGI), ENIGH 2024 (INEGI), CONAPO 2020, modelo propio de aperturas "
      "(`reports/validacion.md`).\n")
    a("## En corto\n")
    bn, bv = mejor_base(resu, "crecimiento_neto")
    a(f"- El score anterior (v2.1, pesos del autor 30/25/15/20/10) tenía un AUC medio de {v('aperturas_crudas', 'score_v21'):.3f} para predecir "
      f"aperturas crudas, debajo de la competencia en la AGEB ({v('aperturas_crudas', 'comp_ageb'):.3f}). **Eso es lo esperado, no un error**: "
      "las aperturas se aglomeran donde ya hay competidores, y un score que castiga la competencia por diseño tiene que quedar por debajo de "
      "quien la premia (sección 1).")
    a(f"- Contra crecimiento neto (aperturas − desapariciones), el score anterior casi no le ganaba a nada: ρ = "
      f"{fz(v('crecimiento_neto', 'score_v21'))} (la mejor línea base ingenua, {minus(NOMBRE_PUNT[bn])}, {fz(bv)}). El score nuevo (3.0: núcleo sin parámetros "
      f"y pesos aprendidos fuera de muestra, sección 3) llega a ρ = **{fz(v('crecimiento_neto', 'score_nuevo_oos'))} fuera de muestra** "
      f"({fz(v('crecimiento_neto', 'score_nuevo'))} con los pesos entregados, ajustados con todos los datos, que son los que ya vieron el municipio de prueba).")
    a(f"- **Pero esa mejora viene casi entera de la carga de los Censos Económicos 2024, no de aperturas.** {100 * diag['pct_carga_elegibles']:.1f} % de los «nuevos» "
      "entre las AGEB elegibles tienen `fecha_alta` 2024: negocios que ya existían y no estaban en el DENUE 2020. Donde 2020 subregistró queda un stock "
      "de 2020 bajo con muchos «nuevos», y el núcleo λ/(1 + competidores) premia justo eso. Al usar el score, el DENUE 2026 ya trae la carga, así que esa "
      f"ventaja no se traslada. Con el objetivo limpio (crecimiento neto sin carga censal = (altas reales − desapariciones) / establecimientos de 2020) el "
      f"score nuevo saca ρ = {fz(v('neto_sin_carga', 'score_nuevo_oos'))} fuera de muestra ({fz(v('neto_sin_carga', 'score_nuevo'))} con los pesos entregados) contra "
      f"{fz(v('neto_sin_carga', 'score_v21'))} del anterior. **En los dos objetivos limpios que ya había el nuevo empata o pierde:** altas fuera de la carga censal "
      f"{fz(v('altas_reales', 'score_nuevo_oos'))} contra {fz(v('altas_reales', 'score_v21'))}; sobrevivencia {fz(v('sobrevivencia', 'score_nuevo_oos'))} contra "
      f"{fz(v('sobrevivencia', 'score_v21'))}. Ojo: como las altas reales son pocas frente a los cierres, el crecimiento neto sin carga se parece mucho a la "
      "sobrevivencia (casi es menos cierres), así que no cuenta como una evidencia independiente.")
    tope = max(abs(v(o, p)) for o in ("sobrevivencia", "altas_reales", "neto_sin_carga") for p in ("score_v21", "score_nuevo", "score_nuevo_oos"))
    a(f"- Por eso **la elección del score 3.0 sobre el 2.1 no es una victoria empírica**: con estos datos (dos cortes del DENUE, sin ventas ni rentas) ninguno "
      f"de los dos predice bien lo limpio (el mayor ρ de cualquiera de los dos en un objetivo limpio es {tope:.3f}). Se conserva el 3.0 como decisión de diseño, explicada en la sección 3, y se "
      "dice que la validación solo descarta, no confirma.")
    a(f"- **La sobrevivencia no se puede predecir con estos datos**: ninguna puntuación pasa de ρ ≈ {fz(max(abs(v('sobrevivencia', p)) for p in ['prob_sobrevive', 'flujo', 'complementarios', 'densidad', 'actividad', 'score_nuevo', 'score_v21']))} "
      "dentro de un giro. Se reporta `prob_sobrevive` como dato de riesgo, no como criterio de orden.")
    a(f"- El decil imputado acierta el decil exacto {100 * nse['decil_exacto']:.1f} % de las veces, pero **la banda de NSE que usa el producto "
      f"(bajo, medio, alto) la acierta {100 * nse['banda_exacta']:.1f} %** (azar: {100 * nse['prob_azar']:.0f} %; siempre decir «medio»: {100 * nse['mayoritaria']:.0f} %). "
      "Es una pista, no una medición (sección 4).\n")

    a("## 1. Diagnóstico: por qué el score no predice aperturas crudas\n")
    a("Hipótesis: las aperturas se aglomeran donde ya hay competencia (economías de aglomeración, tráfico de clientes, locales que cambian de "
      "dueño) y una parte grande de lo que «apareció» en 2026 es la carga de los Censos Económicos 2024, no aperturas. Un score que baja el "
      "puntaje por competencia queda por debajo de las líneas base que la premian. Se comprueba con cuatro números:\n")
    b = diag["bins"]
    a(f"1. **Más competidores, más aperturas.** Promedio de {diag['bins_giros']} giros: probabilidad de que aparezca ≥ 1 negocio del giro en la AGEB "
      f"de {100 * b['p0']:.0f} % si en 2020 no había ninguno, {100 * b['p12']:.0f} % si había 1 o 2 y {100 * b['p3']:.0f} % si había 3 o más. "
      f"Donde había 3 o más aparecieron {b['aper_por_estab']:.2f} negocios nuevos por cada establecimiento de 2020 y desaparecieron "
      f"{b['cierres_por_estab']:.2f}: las aperturas crecen casi proporcionales al stock.")
    el = diag["elasticidad"]
    a(f"2. **Elasticidad.** Regresión de log(1 + aperturas) sobre log(1 + establecimientos de 2020) y log(población), con efectos fijos de giro y "
      f"errores por municipio: el coeficiente de la competencia previa es {el['b_comp']:.2f} (EE {el['se_comp']:.2f}); el de la población, "
      f"{el['b_pob']:.2f} (EE {el['se_pob']:.2f}). Un 10 % más de competidores previos se asocia con ~{10 * el['b_comp']:.1f} % más aperturas. Es asociación, no causalidad.")
    a(f"3. **Rotación y carga censal.** Entre AGEB con ≥ 3 establecimientos del giro en 2020, la correlación de Spearman entre aperturas y cierres "
      f"es {diag['rho_aper_cierres']:.2f} (promedio de {diag['rho_aper_cierres_giros']} giros): donde más abren, más desaparecen; una apertura bruta mezcla "
      f"expansión con rotación. Además, {100 * diag['pct_carga_censal']:.0f} % de los «nuevos» de los 40 giros tienen `fecha_alta` 2024 (carga de los Censos Económicos), "
      "así que «apareció» no es «abrió».")
    a("4. **Qué le hace el score a esa señal.** AUC medio contra aperturas crudas, por giro:\n")
    a("| Puntuación | AUC |")
    a("|---|---|")
    for p in ["prob_modelo", "comp_ageb", "comp_huff", "aperturas_esperadas", "score_v21_sin_castigo", "score_v21", "demanda_neta", "pob_neta", "captura_huff"]:
        nom = NOMBRE_PUNT.get(p, "Score anterior **sin** el castigo por competencia (contrafactual)")
        a(f"| {nom} | {fz(v('aperturas_crudas', p))} |")
    a("\nLa captura Huff (el castigo por competencia) tiene AUC por debajo de 0.5 contra aperturas: ordena al revés. Los términos de demanda y "
      "población la multiplican y pesaban 40 % del score anterior. Quitarle el castigo (mismo score, sin multiplicar por la captura) sube su AUC, "
      "lo que confirma que la causa es la competencia y no un error de cálculo. **La respuesta corta: el score no predice aperturas crudas "
      "porque no intenta hacerlo; premia lugares con aperturas esperadas y pocos competidores, y las aperturas crudas se dan donde ya hay muchos.**\n")

    a("## 2. Qué se midió y contra qué\n")
    a(f"Por (AGEB, giro), con los cortes DENUE 11/2020 y 05/2026. Todo se mide en el mismo círculo (`radio_influencia_m` del giro, peso Huff) que usa el "
      f"score, con al menos {H_MIN:.0f} establecimientos ponderados del giro en 2020 (tasas con denominadores chicos son puro ruido). "
      "Las etiquetas se empatan como en `03_entrenar.py`: por `id` y, de respaldo, por nombre normalizado a ≤ 50 m; el giro, por SCIAN con el cruce "
      "histórico→actual de `data/processed/scian_hist_a_actual.csv`.\n")
    a("| Objetivo | Definición | Métrica | Giros |")
    a("|---|---|---|---|")
    a(f"| Sobrevivencia | establecimientos de 2020 que siguen en 2026 / establecimientos de 2020 | ρ de Spearman | {n_giros['sobrevivencia']} |")
    a(f"| Crecimiento neto | (aperturas − desapariciones) / establecimientos de 2020 | ρ de Spearman | {n_giros['crecimiento_neto']} |")
    a(f"| Altas fuera de la carga censal | aperturas con `fecha_alta` ≠ 2024 / establecimientos de 2020 (las únicas que se parecen a aperturas reales y siguen abiertas en 2026) | ρ de Spearman | {n_giros['altas_reales']} |")
    a(f"| Crecimiento neto sin carga censal | (altas fuera de la carga − desapariciones) / establecimientos de 2020: el crecimiento neto sin los negocios que ya existían y solo aparecieron por la carga de 2024 | ρ de Spearman | {n_giros['neto_sin_carga']} |")
    a(f"| Aperturas crudas (referencia) | apareció ≥ 1 negocio del giro en la AGEB | AUC | {n_giros['aperturas_crudas']} |")
    a("\nLímites de los objetivos: «desapareció del DENUE» puede ser un cierre o un cambio de registro que no se pudo empatar; la tasa de aperturas "
      "netas se normaliza por el stock de 2020, así que comparte denominador con la competencia (por eso se repite sin normalizar y por habitante, abajo); la sobrevivencia **de las aperturas** (negocios abiertos después de 2020 que ya cerraron) no se "
      "puede medir con dos cortes: solo se ven las que siguen abiertas, por eso el objetivo de sobrevivencia usa los establecimientos de 2020.\n")
    a("Validación espacial: los mismos 5 pliegues por municipio (`GroupKFold`) del modelo de aperturas. Valor = promedio entre giros "
      "(± error estándar entre giros). Lift = tasa en el 5 % o 10 % mejor puntuado de las AGEB elegibles entre la tasa base del giro (promedio de giros; "
      "en crecimiento neto la tasa base es casi cero y a veces negativa, así que no se da el cociente y solo la diferencia en puntos porcentuales, Δ pts, entre la tasa del 10 % mejor puntuado y la del giro).\n")
    for obj in ("crecimiento_neto", "sobrevivencia", "altas_reales", "neto_sin_carga", "aperturas_crudas"):
        a(f"### {NOMBRE_OBJ[obj]}{' — AUC' if obj == 'aperturas_crudas' else ' — ρ de Spearman'}\n")
        a("| Puntuación | Valor | Lift 5 % | Lift 10 % | Δ pts 10 % |")
        a("|---|---|---|---|---|")
        orden = ["score_v21", "score_nuevo_oos", "score_nuevo", "score_limpio_oos", "nucleo", "aperturas_esperadas", "captura_huff", "demanda_neta", "pob_neta", "flujo",
                 "complementarios", "prob_modelo", "prob_sobrevive"] + BASES
        for p in orden:
            r = resu[(resu["objetivo"] == obj) & (resu["puntuacion"] == p)]
            if not len(r):
                continue
            r = r.iloc[0]
            neg = "**" if p in ("score_nuevo_oos",) else ""
            a(f"| {neg}{NOMBRE_PUNT[p]}{neg} | {neg}{fz(r['valor'])} ± {fz(r['ee'])}{neg} | {fz(r['lift5'], 2)} | {fz(r['lift10'], 2)} | "
              f"{fz(100 * r['dpp10'], 1, True)} |")
        bn, bv = mejor_base(resu, obj)
        a(f"\nMejor línea base ingenua (con su mejor dirección): {minus(NOMBRE_PUNT[bn])}, {fz(bv)}.\n")
        if obj == "crecimiento_neto":
            a("Este objetivo mezcla aperturas reales con la carga de los Censos Económicos 2024; el siguiente objetivo limpio (neto sin carga censal) y la tabla de "
              "robustez muestran cuánto de esta ventaja queda sin la carga.\n")
    # por giro: crecimiento neto
    a("#### Por giro: crecimiento neto, con y sin carga censal\n")
    pg = res[(res["objetivo"] == "crecimiento_neto") & res["puntuacion"].isin(["score_v21", "score_nuevo_oos"] + BASES)].pivot(index="giro", columns="puntuacion", values="valor")
    pg["mejor_base"] = pg[BASES].abs().max(axis=1)
    lf = 100 * res[(res["objetivo"] == "crecimiento_neto") & (res["puntuacion"] == "score_nuevo_oos")].set_index("giro")["dpp10"]
    pl = res[(res["objetivo"] == "neto_sin_carga") & res["puntuacion"].isin(["score_v21", "score_nuevo_oos"])].pivot(index="giro", columns="puntuacion", values="valor")
    a("| Giro | ρ score anterior | ρ score nuevo (fuera de muestra) | ρ mejor línea base (abs.) | Δ pts 10 % nuevo | ρ neto sin carga: anterior | nuevo |")
    a("|---|---|---|---|---|---|---|")
    for g, r in pg.sort_values("score_nuevo_oos", ascending=False).iterrows():
        a(f"| {g} | {fz(r['score_v21'])} | {fz(r['score_nuevo_oos'])} | {fz(r['mejor_base'])} | {fz(lf.get(g, np.nan), 1, True)} | "
          f"{fz(pl['score_v21'].get(g, np.nan))} | {fz(pl['score_nuevo_oos'].get(g, np.nan))} |")
    gana = int((pg["score_nuevo_oos"] > pg["mejor_base"]).sum())
    gana_v = int((pg["score_v21"] > pg["mejor_base"]).sum())
    pl2 = pl.dropna()
    gana_l = int((pl2["score_nuevo_oos"] > pl2["score_v21"]).sum())
    a(f"\nEn crecimiento neto, el score nuevo (pesos fuera de muestra) supera a la mejor línea base en {gana} de {len(pg)} giros; el anterior, en {gana_v}. "
      f"Sin la carga censal, el nuevo supera al anterior en {gana_l} de {len(pl2)} giros. Tabla completa (todos los objetivos, giro por giro): `models/validacion_score.csv`.\n")

    costo_piso = "no se midió en esta corrida."
    if (resu["puntuacion"] == "score_sin_piso_oos").any():
        m1 = np.mean([v(o, "score_nuevo_oos") for o in OBJ_APRENDER])
        m0 = np.mean([v(o, "score_sin_piso_oos") for o in OBJ_APRENDER])
        costo_piso = f"ρ medio de los tres objetivos, fuera de muestra, {m1:.3f} con el piso y {m0:.3f} sin él."
    a("### Robustez del crecimiento neto: sin normalizar, por habitante y sin la carga censal\n")
    a("Como la tasa de crecimiento neto comparte denominador con la competencia, se repite sin normalizar (aperturas − desapariciones en el círculo) y "
      "por 10 mil habitantes, con todas las AGEB. La última columna quita la carga de los Censos Económicos 2024: (altas fuera de la carga − desapariciones) / "
      "establecimientos de 2020, con las mismas AGEB elegibles que la tasa. Valor = ρ de Spearman promedio entre giros.\n")
    a("| Puntuación | Neto sin normalizar | Neto por 10 mil hab. | Neto sin carga censal |")
    a("|---|---|---|---|")
    for p in ["score_v21", "score_nuevo_oos", "score_nuevo", "score_limpio_oos", "nucleo", "captura_huff", "pob_neta", "flujo", "prob_modelo"] + BASES:
        a(f"| {NOMBRE_PUNT[p]} | {fz(v('neto_absoluto', p))} | {fz(v('neto_por_10mil_hab', p))} | {fz(v('neto_sin_carga', p))} |")
    rob = []
    for o, nom in [("neto_absoluto", "sin normalizar"), ("neto_por_10mil_hab", "por 10 mil habitantes")]:
        bn_, bv_ = mejor_base(resu, o)
        sn = v(o, "score_nuevo_oos")
        rob.append(f"{nom}: el score nuevo (fuera de muestra) saca {sn:.3f} contra {bv_:.3f} de {minus(NOMBRE_PUNT[bn_])} ({'le gana' if sn > bv_ else 'NO le gana'}; "
                   f"el núcleo solo saca {v(o, 'nucleo'):.3f})")
    a("\nLectura: " + "; ".join(rob) + ". La conclusión se sostiene en la tasa y en el conteo; por habitante, el signo de la competencia domina. "
      f"**Sin la carga censal la ventaja desaparece**: el núcleo cae a {fz(v('neto_sin_carga', 'nucleo'))} y la captura Huff a {fz(v('neto_sin_carga', 'captura_huff'))}, "
      f"el score nuevo queda en {fz(v('neto_sin_carga', 'score_nuevo'))} ({fz(v('neto_sin_carga', 'score_nuevo_oos'))} fuera de muestra) y el anterior en {fz(v('neto_sin_carga', 'score_v21'))}; "
      f"el mejor de la tabla es el flujo de gente ({fz(v('neto_sin_carga', 'flujo'))}). Por qué: la carga registra negocios que ya existían; donde el DENUE 2020 "
      "los dejó fuera, el stock de 2020 sale bajo y los «nuevos» altos, y λ/(1 + competidores) lo lee como mercado en crecimiento sin saturar. "
      f"En los cuartiles del stock de 2020 la parte de «nuevos» que es carga va de {100 * min(diag['carga_por_cuartil_H']):.0f} % a {100 * max(diag['carga_por_cuartil_H']):.0f} %, "
      f"y la mediana de nuevos por establecimiento de 2020 (A/H) de {min(diag['a_sobre_h_mediana_por_cuartil_H']):.2f} a {max(diag['a_sobre_h_mediana_por_cuartil_H']):.2f}: "
      "la contaminación es pareja y no se corrige con un filtro simple.\n")
    a("## 3. Qué se decidió y por qué\n")
    a("**Se cambió el score a la versión 3.0; hay que decir con claridad qué prueba ese cambio y qué no.** El anterior no le ganaba a las líneas base en "
      "crecimiento neto y el nuevo sí, pero esa ventaja viene de la carga de los Censos Económicos 2024 (sección 2, robustez): sin la carga el nuevo no le gana al "
      "anterior. El cambio tiene dos partes:\n")
    a("1. **Núcleo sin parámetros.** El término de aperturas pasó de «aperturas esperadas» a «**aperturas esperadas por competidor**» = "
      "aperturas esperadas × captura Huff = λ / (1 + competidores ponderados). Es presión de entrada sobre el stock que ya hay: donde se esperan "
      "muchas entradas y casi no hay competidores, el mercado está creciendo sin estar saturado. Se probó también multiplicar por la probabilidad "
      "de seguir abierto (la definición «apertura × sobrevivir × captura»): no mejora ningún objetivo, porque dentro de un giro esa probabilidad casi "
      "no varía entre lugares.")
    a("2. **Pesos aprendidos, no puestos.** Pesos no negativos que suman 1, ajustados en 4 de 5 pliegues de municipios y reportados en el que no vieron (el entregado se reajusta con todos los datos y se redondea a 0.05); el "
      "criterio es la correlación de los percentiles del score con los de los tres objetivos, con el mismo peso para crecimiento neto, sobrevivencia "
      f"y altas fuera de la carga censal. Restricción a priori: la demanda (gasto potencial + población objetivo) pesa al menos {int(100 * PISO_DEMANDA)} %, "
      "porque la teoría de localización dice que la demanda atrae entrada y los objetivos, que son de oferta, la ven poco. Costo de la restricción: "
      + costo_piso + " Resultado:\n")
    a("| Término del score | Peso anterior | Pliegue 0 | 1 | 2 | 3 | 4 | Ajuste final | **Entregado (a 0.05)** |")
    a("|---|---|---|---|---|---|---|---|---|")
    for i, k in enumerate(TERMINOS):
        a(f"| {nombres_w[k]} | {wv[k]:.2f} | " + " | ".join(f"{apren['por_pliegue'][j][i]:.2f}" for j in range(N_PLIEGUES))
          + f" | {apren['final'][i]:.2f} | **{w[k]:.2f}** |")
    rg = {k: (apren["por_pliegue"][:, i].min(), apren["por_pliegue"][:, i].max()) for i, k in enumerate(TERMINOS)}
    a("\nEntre pliegues, el núcleo ({:.2f}–{:.2f}), la población ({:.2f}–{:.2f}) y los complementarios ({:.2f}–{:.2f}) son estables; el gasto potencial ({:.2f}–{:.2f}) y el flujo "
      "({:.2f}–{:.2f}) no, y por eso los pesos chicos se redondean a 0.05 y no hay que leer de más. La restricción de demanda quedó activa (gasto + población = "
      "{:.2f}). Ojo con el criterio: los tres objetivos pesan igual y se contraponen (el crecimiento neto castiga la competencia, las altas "
      "reales la premian y la sobrevivencia es indiferente); con solo crecimiento neto el núcleo llega a ρ = {:.3f}, el score con los pesos entregados a {:.3f} y fuera de muestra a {:.3f}. Esa mezcla es un juicio, y por eso se publica "
      "el detalle. ".format(*rg["prob_apertura"], *rg["pob_neta"], *rg["complementarios"], *rg["demanda_neta"], *rg["flujo"],
                            w["demanda_neta"] + w["pob_neta"], v("crecimiento_neto", "nucleo"), v("crecimiento_neto", "score_nuevo"),
                            v("crecimiento_neto", "score_nuevo_oos"))
      + "El score sigue siendo un percentil por giro de 0 a 100, interpretable y cabe en una lámina: "
      f"**score = 100 × [{w['prob_apertura']:.2f}·P(aperturas por competidor) + {w['demanda_neta']:.2f}·P(gasto × captura) + {w['pob_neta']:.2f}·P(población objetivo × NSE × captura) "
      f"+ {w['flujo']:.2f}·P(flujo) + {w['complementarios']:.2f}·P(complementarios)]**, donde P es el percentil dentro del giro. "
      "`prob_sobrevive` queda fuera del score y se reporta como dato de riesgo.\n")
    sw = sens["pesos"]
    a("**Qué sostiene la elección del 3.0 y qué no.** Entre los objetivos que no dependen de la carga censal "
      f"(sobrevivencia, altas fuera de la carga y crecimiento neto sin carga), el 3.0 saca ρ = {fz(v('sobrevivencia', 'score_nuevo_oos'))}, {fz(v('altas_reales', 'score_nuevo_oos'))} y "
      f"{fz(v('neto_sin_carga', 'score_nuevo_oos'))} fuera de muestra, y el 2.1 {fz(v('sobrevivencia', 'score_v21'))}, {fz(v('altas_reales', 'score_v21'))} y "
      f"{fz(v('neto_sin_carga', 'score_v21'))}: empata en sobrevivencia y **pierde en los otros dos**. No hay evidencia limpia de que sea mejor. Se conserva por una razón de "
      "diseño y no por una victoria medida: el núcleo «aperturas esperadas por competidor» pone la saturación en el centro del orden (la pregunta de quien abre un negocio "
      "es dónde hay espacio, no dónde ya hay muchos), y los pesos quedan aprendidos con un criterio explícito y publicado en lugar de puestos a mano. "
      f"Su costo está a la vista en las tablas: ni este score ni el anterior pasan de ρ = {tope:.3f} en un objetivo limpio; con dos cortes del DENUE "
      "y sin ventas ni rentas la validación sirve para descartar, no para confirmar.\n")
    a("**Sensibilidad: qué pasa si el aprendizaje usa solo objetivos limpios.** Se repitió el aprendizaje con sobrevivencia, altas fuera de la carga y crecimiento neto sin carga "
      "(mismos pliegues y mismo piso de demanda); **no se entrega**, es para ver el trade-off. Pesos: "
      + ", ".join(f"{nombres_w[k]} {sw[k]:.2f}" for k in TERMINOS)
      + f". Fuera de muestra saca ρ = {fz(v('neto_sin_carga', 'score_limpio_oos'))} en neto sin carga, {fz(v('altas_reales', 'score_limpio_oos'))} en altas fuera de la carga y "
      f"{fz(v('sobrevivencia', 'score_limpio_oos'))} en sobrevivencia (mejora a ambos scores en lo limpio), pero {fz(v('crecimiento_neto', 'score_limpio_oos'))} en crecimiento neto y "
      f"AUC {fz(v('aperturas_crudas', 'score_limpio_oos'))} en aperturas crudas. Le quita todo el peso al núcleo anti-saturación y ordena hacia donde ya hay negocios "
      "(flujo y complementarios): predice dónde hay actividad, no dónde hay hueco. Por eso no se adopta; pero muestra que, si el criterio fuera solo lo limpio, el score "
      "sería otro, y que la decisión de diseño es de quien lo usa.\n")
    a("**Lo que el score nuevo no hace.** (1) No predice mejor aperturas crudas: baja a un AUC de "
      f"{v('aperturas_crudas', 'score_nuevo_oos'):.3f} fuera de muestra (era {v('aperturas_crudas', 'score_v21'):.3f}), y está bien por la sección 1. (2) No predice sobrevivencia. "
      f"(3) En altas fuera de la carga censal (ρ = {fz(v('altas_reales', 'score_nuevo_oos'))} fuera de muestra, antes {fz(v('altas_reales', 'score_v21'))}) no gana: esa señal "
      "premia flujo y competencia, que son justo lo que el nuevo score baja o pesa menos. Son pocas altas (el DENUE las registra sobre todo en negocios visibles) y se reportan "
      "tal cual. (4) Es evidencia observacional de un solo par de cortes: el modelo de aperturas se entrenó con 2020→2026 y se aplica a 2026 suponiendo que la relación se mantiene. "
      "(5) No es mejor que el anterior en lo que no depende de la carga censal: su ventaja en crecimiento neto viene de ella (sección 2).\n")

    a("## 4. Decil imputado: exactitud por banda de NSE\n")
    a(f"Se repite la validación cruzada de `scripts/02_features.py` ({nse['n']:,} hogares de la ENIGH 2024, ámbito ZMVM, {nse['upm']} UPM; regresión lineal ponderada "
      "de log ingreso sobre escolaridad del jefe, auto, internet, PC y tamaño del hogar; 5 pliegues por UPM) y se mide por banda de NSE (bajo = deciles 1-4, "
      "medio = 5-8, alto = 9-10, convención del proyecto). Fuente: ENIGH 2024 (INEGI) y modelo propio.\n")
    a(f"- Decil exacto: **{100 * nse['decil_exacto']:.1f} %**; ±1 decil: {100 * nse['decil_mas_menos_1']:.1f} % (el azar da 10 % y ~28 %).")
    a(f"- **Banda exacta: {100 * nse['banda_exacta']:.1f} %.** Referencias: azar con las proporciones de cada banda, {100 * nse['prob_azar']:.0f} %; decir siempre «medio», {100 * nse['mayoritaria']:.0f} %. "
      f"Error grave (bajo ↔ alto): {100 * nse['grave']:.1f} % de los hogares. Probabilidad media que el modelo da a la banda correcta: {nse['prob_media_banda_real']:.2f}.\n")
    a("| Banda real | Hogares (ponderado) | Acierto (la clasificó en su banda) | Cayó en bajo | medio | alto |")
    a("|---|---|---|---|---|---|")
    for i, n in enumerate(["bajo", "medio", "alto"]):
        c = nse["confusion"][i]
        a(f"| {n} | {100 * nse['composicion'][n]:.0f} % | **{100 * nse['recall'][n]:.0f} %** | {100 * c[0]:.0f} % | {100 * c[1]:.0f} % | {100 * c[2]:.0f} % |")
    a("\n**Lectura honesta.** A nivel de hogar el decil es una estimación débil (el Censo no trae ingreso); la banda sirve para distinguir lo bajo de lo "
      "alto (solo " + f"{100 * nse['grave']:.1f}" + " % de los hogares cae a dos bandas de distancia), pero se confunde con la banda vecina y subdetecta lo alto: "
      "la regresión es conservadora y manda a «medio» a " + f"{100 * nse['confusion'][2][1]:.0f}" + " % de los hogares de nivel alto. El producto no clasifica hogares: asigna el hogar típico de una AGEB y guarda probabilidades "
      "(`p_nse_*`). A nivel AGEB y municipio el estimado se contrasta con la marginación de CONAPO 2020 (ρ = 0.88) y con el ingreso promedio municipal de la "
      "ENIGH en 35 municipios (ρ = 0.90, `reports/decil_imputado.md`); a nivel AGEB no hay ingreso observado contra el cual medir la banda. "
      "Esta validación es por hogar y sin el estiramiento ecológico que se aplica a las AGEB, así que no es exactamente la del producto. Conviene decir «NSE estimado» y no «NSE de la colonia».\n")

    a("## Reproducir\n")
    a("```bash\nOMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03b_validar_score.py        # reaprende pesos, evalúa, reescribe este reporte\n"
      "uv run python scripts/03_entrenar.py --solo-scores                                       # regenera models/scores_giros.parquet con esos pesos\n"
      "uv run pytest tests/test_modelo.py -q\n```")
    REPORTE.write_text("\n".join(L) + "\n", encoding="utf-8")
    log(f"reporte: {REPORTE.relative_to(RAIZ)}")


# =============================================================== 8. carpetas/05_modelo (lo que consulta el RAG)
def escribir_carpetas(resu, diag, nse, w, sens) -> None:
    """Preguntas de examen sobre el score (con cifras salidas de esta corrida) y copia del reporte, para el RAG."""
    def v(o, p):
        r = resu[(resu["objetivo"] == o) & (resu["puntuacion"] == p)]
        return float(r["valor"].iloc[0]) if len(r) else float("nan")

    b = diag["bins"]
    bn = {o: mejor_base(resu, o) for o in ("crecimiento_neto", "sobrevivencia", "altas_reales", "aperturas_crudas")}
    hoy = date.today().isoformat()
    L = ["# Preguntas de examen sobre el score y respuestas cortas\n",
         f"Generado por `scripts/03b_validar_score.py` el {hoy}; las cifras salen de `reports/validacion_score.md` (DENUE 11/2020 y 05/2026, Censo 2020, "
         "ENIGH 2024 de INEGI; CONAPO 2020; modelo propio). Si algo cambia, vuelve a correr el script: no se editan a mano.\n",
         "## ¿Por qué el score no predice aperturas crudas y está bien?\n",
         "**Respuesta corta.** El score no está hecho para adivinar dónde aparecen más negocios, sino dónde conviene poner uno. Las aperturas se "
         f"aglomeran donde ya hay competencia: en las AGEB con 3 o más negocios del giro en 2020 aparecieron {10 * b['aper_por_estab']:.0f} nuevos por cada 10 que ya había "
         f"y desaparecieron otros {10 * b['cierres_por_estab']:.0f} (rotación). Un score que castiga la competencia, como debe hacerlo uno de ubicación, queda "
         f"debajo de la competencia a secas para predecir aperturas crudas: AUC {v('aperturas_crudas', 'score_nuevo_oos'):.3f} contra {v('aperturas_crudas', 'comp_ageb'):.3f} "
         f"de la competencia en la AGEB y {v('aperturas_crudas', 'prob_modelo'):.3f} del modelo de aperturas. La captura Huff, que es el castigo, tiene AUC "
         f"{v('aperturas_crudas', 'captura_huff'):.3f}: ordena al revés. Además, {100 * diag['pct_carga_censal']:.0f} % de lo que «apareció» en 2026 viene de la carga de los Censos "
         "Económicos 2024, así que «apareció» no es «abrió».\n",
         "**Qué se hizo.** Se midió contra lo que corresponde a la decisión, por (AGEB, giro): crecimiento neto (aperturas menos desapariciones sobre los "
         "establecimientos de 2020), sobrevivencia de los establecimientos de 2020 y altas fuera de la carga censal.\n",
         "## ¿Los pesos del score los puso el autor?\n",
         "No. Los aprendió `scripts/03b_validar_score.py`: pesos no negativos que suman 1, ajustados en 4 de 5 pliegues de municipios y probados en el que no vieron (el entregado se reajusta con todo), "
         "redondeados a 0.05, con una restricción de que gasto potencial y población objetivo pesen al menos 25 %. "
         f"Resultado: {w['prob_apertura']:.2f} aperturas esperadas por competidor, {w['demanda_neta']:.2f} gasto potencial × captura, {w['pob_neta']:.2f} población objetivo × NSE × captura, "
         f"{w['flujo']:.2f} flujo de gente (proxy) y {w['complementarios']:.2f} complementarios. Antes eran 0.30, 0.25, 0.15, 0.20 y 0.10, puestos por el autor. "
         f"En crecimiento neto, el score nuevo saca ρ = {v('crecimiento_neto', 'score_nuevo_oos'):.3f} fuera de muestra ({v('crecimiento_neto', 'score_nuevo'):.3f} con los pesos entregados, que ya vieron todos los municipios) "
         f"contra {v('crecimiento_neto', 'score_v21'):.3f} del anterior y {bn['crecimiento_neto'][1]:.3f} de la mejor línea base ingenua. "
         f"En altas fuera de la carga censal el nuevo saca {v('altas_reales', 'score_nuevo_oos'):.3f} y el anterior {v('altas_reales', 'score_v21'):.3f}: ahí pierde, y se dice.\n",
         "## ¿El score nuevo es mejor que el anterior?\n",
         f"No se puede afirmar. Su ventaja en crecimiento neto viene de la carga de los Censos Económicos 2024: {100 * diag['pct_carga_elegibles']:.1f} % de los «nuevos» entre las AGEB elegibles tienen `fecha_alta` 2024, "
         "negocios que ya existían y no estaban en el DENUE 2020; donde 2020 subregistró queda un stock bajo con muchos «nuevos», y el núcleo λ/(1 + competidores) premia justo eso. "
         "Al usar el score, el DENUE 2026 ya trae la carga, así que esa ventaja no se traslada. Con el objetivo sin carga censal (altas reales menos desapariciones, sobre el stock de 2020) el nuevo saca "
         f"ρ = {v('neto_sin_carga', 'score_nuevo_oos'):.3f} fuera de muestra contra {v('neto_sin_carga', 'score_v21'):.3f} del anterior; en altas fuera de la carga {v('altas_reales', 'score_nuevo_oos'):.3f} contra "
         f"{v('altas_reales', 'score_v21'):.3f}, y en sobrevivencia {v('sobrevivencia', 'score_nuevo_oos'):.3f} contra {v('sobrevivencia', 'score_v21'):.3f}: empata o pierde. Como las altas reales son pocas frente a los cierres, "
         "el neto sin carga se parece mucho a la sobrevivencia, así que no es una evidencia independiente. Se conserva el 3.0 como decisión de diseño (pone la saturación en el centro del orden y los pesos son "
         "aprendidos con un criterio publicado), no como victoria medida; con dos cortes del DENUE y sin ventas ni rentas, la validación descarta pero no confirma. "
         f"Sensibilidad: aprendiendo los pesos solo con objetivos limpios, el núcleo anti-saturación se queda en {sens['pesos']['prob_apertura']:.2f} y el score ordena hacia donde ya hay negocios "
         f"(crecimiento neto ρ = {v('crecimiento_neto', 'score_limpio_oos'):.3f}), por eso no se adopta.\n",
         "## ¿Se puede predecir si un negocio va a sobrevivir?\n",
         f"Con estos datos casi no. Dentro de un giro, la mejor puntuación que se probó (el modelo dedicado de sobrevivencia) saca ρ = {v('sobrevivencia', 'prob_sobrevive'):.3f} contra la "
         f"tasa de sobrevivencia de los establecimientos de 2020 en el círculo del giro, y el score {v('sobrevivencia', 'score_nuevo_oos'):.3f}. Por eso `prob_sobrevive` se reporta como dato de riesgo "
         "y no se usa para ordenar. Aviso: «desapareció del DENUE» puede ser un cierre o un cambio de registro que no se pudo empatar.\n",
         "## ¿Qué tan confiable es el nivel socioeconómico estimado?\n",
         f"El decil exacto de un hogar se acierta {100 * nse['decil_exacto']:.1f} % de las veces y a ±1 decil {100 * nse['decil_mas_menos_1']:.1f} %. La banda (bajo = deciles 1-4, medio = 5-8, alto = 9-10), que es "
         f"lo que usa el producto, se acierta {100 * nse['banda_exacta']:.1f} % (decir siempre «medio» daría {100 * nse['mayoritaria']:.0f} %): {100 * nse['recall']['bajo']:.0f} % en bajo, "
         f"{100 * nse['recall']['medio']:.0f} % en medio y {100 * nse['recall']['alto']:.0f} % en alto, donde se subdetecta. Casi nunca confunde bajo con alto ({100 * nse['grave']:.1f} % de los hogares). "
         "Es un estimado a partir del Censo, no un dato medido: se dice «NSE estimado». Fuente: ENIGH 2024 (INEGI), validación cruzada por UPM.\n",
         "## ¿Qué haría distinto con más datos?\n",
         "Ventas y rentas por local, flujo peatonal real y cortes anuales del DENUE para separar aperturas de cargas censales. Con eso se podría medir rentabilidad y "
         "sobrevivencia de las aperturas, que hoy no se pueden observar con solo dos cortes.\n"]
    (RAIZ / "carpetas" / "05_modelo" / "preguntas_de_examen_del_score.md").write_text("\n".join(L), encoding="utf-8")
    cuerpo = REPORTE.read_text(encoding="utf-8")
    (RAIZ / "carpetas" / "05_modelo" / "validacion_score.md").write_text(
        f"> Copia de `reports/validacion_score.md` hecha por `scripts/03b_validar_score.py` el {hoy}. La fuente es ese reporte.\n\n" + cuerpo, encoding="utf-8")
    log("carpetas/05_modelo: preguntas_de_examen_del_score.md y validacion_score.md")


# =============================================================== principal
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-reporte", action="store_true", help="no reaprende pesos: usa models/pesos_score.json")
    args = ap.parse_args(argv)
    t0 = time.time()
    ent = cargar_entrenar()
    d, res_et = base_hist(ent)
    log(f"base: {len(d):,} filas ({time.time() - t0:.0f} s)")
    d["pliegue"] = asignar_pliegues(d)
    d["score_v21"] = terminos_v21(d)
    ok = d.set_index(["cvegeo", "giro"])["score_v21"]
    # control: el score guardado en oof.parquet es el de los pesos vigentes (o, la primera vez, el v2.1 de antes)
    ref = pd.read_parquet(MODELS / "oof.parquet").set_index(["cvegeo", "giro"])["score_comb"].reindex(ok.index)
    err = min(float((ok - ref).abs().max()), float((aplicar_pesos(d, motor.PESOS_SCORE) - ref.set_axis(d.index)).abs().max()))
    log(f"control: el score reconstruido coincide con el guardado (error maximo {err:.2e})")
    assert err < 0.05   # el guardado se calculo con features en float32: difiere en ~1e-3 de 100
    d = objetivos(d)
    d["prob_sobrevive"] = sobrevivencia_oof(ent, d)
    # contrafactual: el score anterior sin multiplicar demanda y poblacion por la captura Huff
    dd = d.assign(pct_demanda_neta=d.groupby("giro")["demanda"].rank(pct=True).fillna(0.0),
                  pct_pob_neta=d.assign(x=d["poblacion_objetivo"] * d["nse_fit"]).groupby("giro")["x"].rank(pct=True).fillna(0.0))
    d["score_v21_sin_castigo"] = terminos_v21(dd)
    log(f"objetivos y componentes listos ({time.time() - t0:.0f} s)")

    if args.solo_reporte and (MODELS / "pesos_score.json").exists():
        pj = json.loads((MODELS / "pesos_score.json").read_text(encoding="utf-8"))
        w = {k: float(pj["pesos"][k]) for k in TERMINOS}
        apren = {"por_pliegue": np.array([[p[k] for k in TERMINOS] for p in pj["pesos_por_pliegue"]]),
                 "sin_piso": np.array([[p[k] for k in TERMINOS] for p in pj.get("pesos_por_pliegue_sin_piso", [])]),
                 "final": np.array([pj["pesos_sin_redondear"][k] for k in TERMINOS]), "redondeado": np.array([w[k] for k in TERMINOS]),
                 "giros": pj["giros_en_el_aprendizaje"]}
        guardar = None
    else:
        apren = aprender(d)
        w = dict(zip(TERMINOS, apren["redondeado"].tolist()))
        guardar = apren
    # score nuevo: entregado (pesos redondeados con todo) y fuera de muestra (pesos de cada pliegue en su pliegue)
    d["score_nuevo"] = aplicar_pesos(d, w)
    oos = np.zeros(len(d))
    for k in range(N_PLIEGUES):
        m = (d["pliegue"] == k).to_numpy()
        oos[m] = aplicar_pesos(d[m], dict(zip(TERMINOS, apren["por_pliegue"][k]))).to_numpy()
    d["score_nuevo_oos"] = oos
    if len(apren.get("sin_piso", [])):
        sp = np.zeros(len(d))
        for k in range(N_PLIEGUES):
            m = (d["pliegue"] == k).to_numpy()
            sp[m] = aplicar_pesos(d[m], dict(zip(TERMINOS, apren["sin_piso"][k]))).to_numpy()
        d["score_sin_piso_oos"] = sp
    sens = sensibilidad_limpia(d)
    d["score_limpio_oos"] = sens["oos"]
    punt = {"score_v21": "score_v21", "score_nuevo": "score_nuevo", "score_limpio_oos": "score_limpio_oos", "score_nuevo_oos": "score_nuevo_oos", "score_v21_sin_castigo": "score_v21_sin_castigo",
            "nucleo": "nucleo", "aperturas_esperadas": "aperturas_esperadas", "captura_huff": "captura_huff", "demanda_neta": "demanda_neta",
            "pob_neta": "pob_neta", "flujo": "flujo", "complementarios": "complementarios", "prob_modelo": "oof",
            "prob_sobrevive": "prob_sobrevive", "densidad": "densidad_hab_km2", "comp_huff": "comp_huff", "comp_ageb": "comp_ageb",
            "actividad": "estab_500m"}
    if "score_sin_piso_oos" in d:
        punt["score_sin_piso_oos"] = "score_sin_piso_oos"
    res = evaluar(d, punt)
    res.to_csv(MODELS / "validacion_score.csv", index=False)
    resu = resumen(res)
    log(f"evaluacion lista ({time.time() - t0:.0f} s)")
    diag = diagnostico(d)
    nse = exactitud_nse()
    log(f"decil: exacto {nse['decil_exacto']:.3f}, banda {nse['banda_exacta']:.3f}")
    sincronizar(ent, d, w, guardar)
    escribir_reporte(d, res, resu, diag, nse, apren, w, sens)
    escribir_carpetas(resu, diag, nse, w, sens)
    (MODELS / "validacion_score_resumen.json").write_text(json.dumps(
        {"fecha": date.today().isoformat(), "version": motor.SCORE_VERSION, "pesos": w, "diagnostico": diag, "nse": nse,
         "resumen": resu.round(4).to_dict(orient="records")}, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    log(f"listo en {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
