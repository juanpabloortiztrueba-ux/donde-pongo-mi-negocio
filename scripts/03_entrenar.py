"""Etapa Modelo E: modelo de aperturas por (AGEB, giro) con HistGradientBoosting de sklearn.

Etiqueta: aparecio >=1 establecimiento del giro en el DENUE 05/2026 que no estaba en el de 11/2020
(se empata por `id` y, de respaldo, por nombre normalizado a <= 50 m). Variante: sobrevivio
(el establecimiento del corte 11/2020 sigue en 05/2026).
Features: Censo 2020, decil imputado, DENUE y transporte del corte 11/2020 (sin fuga), y
competencia/complementarios/demanda del giro en ese mismo corte (app/motor.py: matriz_modelo).
Validacion espacial: GroupKFold por municipio (cvegeo_mun), 5 pliegues.

Salidas: models/aperturas.joblib, models/sobrevivencia.joblib, models/metadata.json,
models/importancia.csv, models/metricas_giro.csv, models/etiquetas.parquet,
models/scores_giros.parquet (score_giro de los 40 giros en el corte actual) y reports/validacion.md.

Uso:  OMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03_entrenar.py   (~5-10 min; correr con nohup)
      ... scripts/03_entrenar.py --solo-etiquetas   (solo arma etiquetas)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from app import motor  # noqa: E402

PROC = RAIZ / "data" / "processed"
MODELS = RAIZ / "models"
REPORTE = RAIZ / "reports" / "validacion.md"
R_EMPATE = 50.0       # metros para empatar por nombre cuando cambia el id
N_PLIEGUES = 5
TOP_K = (50, 100)     # precision en las k AGEB mejor puntuadas de cada giro
SEMILLA = 0
PARAMS = dict(learning_rate=0.06, max_iter=800, max_leaf_nodes=31, min_samples_leaf=80, l2_regularization=1.0,
              early_stopping=True, validation_fraction=0.1, n_iter_no_change=25, random_state=SEMILLA)
GENERICOS = {"", "SIN NOMBRE", "NINGUNO", "NA", "N A", "SN", "S N", "NO TIENE", "SIN DATO", "X", "XX"}


def log(msg: str) -> None:
    print(f"[03_entrenar {time.strftime('%H:%M:%S')}] {msg}", flush=True)


# =============================================================== 1. etiquetas
def normaliza(s: pd.Series) -> pd.Series:
    """Mayusculas, sin acentos, solo letras/numeros y un espacio."""
    s = s.fillna("").astype(str).map(lambda t: unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode())
    return s.str.upper().str.replace(r"[^A-Z0-9]+", " ", regex=True).str.strip()


def empatar_por_nombre(a: pd.DataFrame, h: pd.DataFrame) -> tuple[set, set]:
    """Ids (actual, hist) que solo cambiaron de id: mismo nombre normalizado a <= R_EMPATE metros."""
    na, nh = normaliza(a["nombre"]).to_numpy(), normaliza(h["nombre"]).to_numpy()
    arbol = cKDTree(h[["x", "y"]].to_numpy())
    axy = a[["x", "y"]].to_numpy()
    ida, idh = a["id"].to_numpy(), h["id"].to_numpy()
    ea, eh = set(), set()
    for k in range(0, len(a), 40_000):
        m = cKDTree(axy[k:k + 40_000]).sparse_distance_matrix(arbol, R_EMPATE, output_type="ndarray")
        i, j = m["i"] + k, m["j"]
        ok = (na[i] == nh[j]) & ~np.isin(na[i], list(GENERICOS)) & (np.char.str_len(na[i].astype(str)) >= 3)
        ea.update(ida[i[ok]].tolist())
        eh.update(idh[j[ok]].tolist())
    return ea, eh


def etiquetas(con_puntos: bool = False):
    """Etiquetas por (AGEB, giro) y tabla por establecimiento historico (para la variante sobrevivio).
    Con con_puntos=True devuelve ademas (hist con `sobrevive`, nuevos, nuevos fuera de la carga censal) con coordenadas,
    que usa scripts/03b_validar_score.py para medir los objetivos en el mismo circulo del giro."""
    ids_a = set(pd.read_parquet(PROC / "denue_actual.parquet", columns=["id"])["id"].dropna().astype(int))
    ids_h = set(pd.read_parquet(PROC / "denue_hist.parquet", columns=["id"])["id"].dropna().astype(int))
    a, h = motor.denue("actual"), motor.denue("hist")
    a_solo, h_solo = a[~a["id"].isin(ids_h)], h[~h["id"].isin(ids_a)]
    ea, eh = empatar_por_nombre(a_solo, h_solo)
    nuevo = a[~a["id"].isin(ids_h) & ~a["id"].isin(ea)]
    sobrevive = h["id"].isin(ids_a) | h["id"].isin(eh)
    h = h.assign(sobrevive=sobrevive.to_numpy())
    fa = pd.read_parquet(PROC / "denue_actual.parquet", columns=["id", "fecha_alta"]).set_index("id")["fecha_alta"]
    res = {"ids_actual": len(ids_a), "ids_hist": len(ids_h), "ids_en_ambos": len(ids_a & ids_h),
           "actual_solo_con_coord": len(a_solo), "hist_solo_con_coord": len(h_solo),
           "empatados_por_nombre": len(ea), "nuevos": len(nuevo),
           "nuevos_por_anio_alta": nuevo["id"].map(fa).str[:4].value_counts().sort_index().to_dict(),
           "hist_sobreviven_pct": round(100 * float(sobrevive.mean()), 2)}
    agebs = motor.agebs_xy().index
    # altas fuera de la carga de los Censos Economicos 2024 (fecha_alta 2024): son las que mas se parecen a una apertura real
    nuevo_real = nuevo[nuevo["id"].map(fa).str[:4] != "2024"]
    res["nuevos_fuera_carga_censal"] = len(nuevo_real)
    filas, estab = [], []
    for clave, g in motor.giros().items():
        sc, fl = g.get("scian", []), g.get("scian_con_filtro")
        n_new = motor.seleccionar(nuevo, sc, fl).groupby("cvegeo").size()
        n_real = motor.seleccionar(nuevo_real, sc, fl).groupby("cvegeo").size()
        hg = motor.seleccionar(h, sc, fl)
        n_h = hg.groupby("cvegeo").size()
        n_s = hg.groupby("cvegeo")["sobrevive"].sum()
        filas.append(pd.DataFrame({"cvegeo": agebs, "giro": clave,
                                   "n_aperturas": n_new.reindex(agebs).fillna(0).astype(int).to_numpy(),
                                   "n_aperturas_reales": n_real.reindex(agebs).fillna(0).astype(int).to_numpy(),
                                   "n_hist": n_h.reindex(agebs).fillna(0).astype(int).to_numpy(),
                                   "n_sobreviven": n_s.reindex(agebs).fillna(0).astype(int).to_numpy()}))
        estab.append(hg[hg["cvegeo"].isin(agebs)][["id", "cvegeo", "per_ocu_medio", "sobrevive"]].assign(giro=clave))
    et = pd.concat(filas, ignore_index=True)
    et["y_apertura"] = (et["n_aperturas"] > 0).astype(np.int8)
    if con_puntos:
        return et, pd.concat(estab, ignore_index=True), res, (h, nuevo, nuevo_real)
    return et, pd.concat(estab, ignore_index=True), res


# =============================================================== 2. entrenamiento y validacion
def columnas_x(m: pd.DataFrame) -> list[str]:
    return [c for c in m.columns if c not in ("cvegeo", "cvegeo_mun", "giro")]


def modelo() -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(categorical_features=[0], **PARAMS)  # columna 0 = giro_cod


def validar(X: pd.DataFrame, y: np.ndarray, grupos: np.ndarray) -> tuple[np.ndarray, list]:
    """Predicciones fuera de pliegue con GroupKFold por municipio."""
    oof = np.zeros(len(y))
    pliegues = []
    for k, (tr, te) in enumerate(GroupKFold(n_splits=N_PLIEGUES).split(X, y, grupos)):
        t = time.time()
        clf = modelo().fit(X.iloc[tr], y[tr])
        oof[te] = clf.predict_proba(X.iloc[te])[:, 1]
        pliegues.append({"pliegue": k, "n_test": int(len(te)), "municipios_test": int(len(set(grupos[te]))),
                         "auc": float(roc_auc_score(y[te], oof[te])), "iter": int(clf.n_iter_),
                         "segundos": round(time.time() - t, 1)})
        log(f"pliegue {k}: AUC {pliegues[-1]['auc']:.3f}, {clf.n_iter_} iter, {pliegues[-1]['segundos']} s")
    return oof, pliegues


def prec_top(y: np.ndarray, s: np.ndarray, k: int) -> float:
    o = np.argsort(-np.nan_to_num(s, nan=-np.inf), kind="stable")[:k]
    return float(y[o].mean())


def metricas_giro(d: pd.DataFrame, scores: dict[str, str]) -> pd.DataFrame:
    filas = []
    for giro, g in d.groupby("giro", sort=False):
        y = g["y_apertura"].to_numpy()
        f = {"giro": giro, "agebs_con_apertura": int(y.sum()), "tasa_base": float(y.mean()),
             "aperturas": int(g["n_aperturas"].sum())}
        for nom, col in scores.items():
            s = g[col].to_numpy(dtype=float)
            ok = ~np.isnan(s)
            valido = 0 < y[ok].sum() < ok.sum()
            f[f"auc_{nom}"] = float(roc_auc_score(y[ok], s[ok])) if valido else np.nan
            f[f"ap_{nom}"] = float(average_precision_score(y[ok], s[ok])) if valido else np.nan
            for k in TOP_K:
                f[f"p{k}_{nom}"] = prec_top(y, s, k)
        filas.append(f)
    return pd.DataFrame(filas)


def importancia(X: pd.DataFrame, y: np.ndarray, grupos: np.ndarray) -> pd.DataFrame:
    """Importancia por permutacion (caida de average precision) en un pliegue espacial dejado fuera."""
    tr, te = next(GroupKFold(n_splits=N_PLIEGUES).split(X, y, grupos))
    clf = modelo().fit(X.iloc[tr], y[tr])
    rng = np.random.default_rng(SEMILLA)
    te = rng.choice(te, size=min(40_000, len(te)), replace=False)
    r = permutation_importance(clf, X.iloc[te], y[te], scoring="average_precision", n_repeats=3,
                               random_state=SEMILLA, n_jobs=1)
    return (pd.DataFrame({"feature": X.columns, "importancia_ap": r.importances_mean, "sd": r.importances_std})
            .sort_values("importancia_ap", ascending=False).reset_index(drop=True))


def sobrevivencia(estab: pd.DataFrame, mh: pd.DataFrame) -> tuple[HistGradientBoostingClassifier, dict, list[str]]:
    """Variante: P(un establecimiento del corte 11/2020 sigue en 05/2026), por establecimiento."""
    d = estab.merge(mh, on=["cvegeo", "giro"], how="left")
    cols = ["giro_cod", "per_ocu_medio"] + [c for c in columnas_x(mh) if c != "giro_cod"]
    X, y, gr = d[cols], d["sobrevive"].to_numpy().astype(int), d["cvegeo_mun"].to_numpy()
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=N_PLIEGUES).split(X, y, gr):
        oof[te] = modelo().fit(X.iloc[tr], y[tr]).predict_proba(X.iloc[te])[:, 1]
    por_giro = {}
    for giro, idx in d.groupby("giro").indices.items():
        yy = y[idx]
        por_giro[giro] = {"n": int(len(idx)), "tasa": float(yy.mean()),
                          "auc": float(roc_auc_score(yy, oof[idx])) if 0 < yy.sum() < len(yy) else None}
    res = {"n": int(len(y)), "tasa_sobrevive": float(y.mean()), "auc_oof": float(roc_auc_score(y, oof)),
           "ap_oof": float(average_precision_score(y, oof)), "por_giro": por_giro}
    log(f"sobrevivencia: n={len(y):,}, tasa {y.mean():.3f}, AUC oof {res['auc_oof']:.3f}")
    return modelo().fit(X, y), res, cols


# =============================================================== 4. reporte
def _f(v, n=3) -> str:
    return "—" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{n}f}"


def escribir_reporte() -> None:
    meta = json.loads((MODELS / "metadata.json").read_text(encoding="utf-8"))
    met = pd.read_csv(MODELS / "metricas_giro.csv")
    imp = pd.read_csv(MODELS / "importancia.csv")
    et, v, sob = meta["etiquetas"], meta["validacion"], meta["sobrevivencia"]
    w = meta["pesos_score"]
    ok = met[met["agebs_con_apertura"] >= 30]
    gana_d = int((ok["auc_modelo"] > ok["auc_densidad"]).sum())
    gana_c = int((ok["auc_modelo"] > ok["auc_competencia"]).sum())
    gana_a = int((ok["auc_modelo"] > ok["auc_actividad"]).sum())
    gana_ca = int((ok["auc_modelo"] > ok["auc_comp_ageb"]).sum())
    gana_p = int(((ok["p100_modelo"] >= ok["p100_densidad"]) & (ok["p100_modelo"] >= ok["p100_competencia"])).sum())
    L = []
    a = L.append
    a("# Validación del modelo de aperturas (etapa Modelo E)\n")
    a(f"Generado por `scripts/03_entrenar.py` el {meta['fecha']} · modelo `{meta['modelo_id']}` · "
      f"{meta['modelo']} (scikit-learn {meta['sklearn']}).\n")
    a("## Qué predice\n")
    a("Para cada par (AGEB urbana de la ZMVM, giro de `config/giros.yaml`) la probabilidad de que **aparezca al menos "
      "un establecimiento del giro** en el DENUE de 05/2026 que no estaba en el DENUE de 11/2020 (ventana de ~5.5 años). "
      f"Un establecimiento es «nuevo» si su `id` no está en el corte 11/2020 y tampoco hay, a ≤ {meta['r_empate_m']:.0f} m, "
      "un establecimiento del corte 11/2020 que desapareció con el mismo nombre normalizado (cambio de `id`). "
      "El giro se identifica con `codigo_act` (actual) y `codigo_act_actual` (histórico, traducido a SCIAN 2023 por Datos B), "
      "más el filtro por nombre `scian_con_filtro`.\n")
    a(f"- Ids: {et['ids_actual']:,} en 05/2026, {et['ids_hist']:,} en 11/2020, {et['ids_en_ambos']:,} en ambos. "
      f"Empatados por nombre y distancia: {et['empatados_por_nombre']:,}. Nuevos: **{et['nuevos']:,}**. "
      f"Del corte 11/2020 siguen en 05/2026 el {et['hist_sobreviven_pct']} %.")
    na = et["nuevos_por_anio_alta"]
    a(f"- **Aviso fuerte: «apareció en el DENUE» no es lo mismo que «abrió».** De los nuevos, {na.get('2024', 0):,} tienen "
      "`fecha_alta` 2024: es la carga de los Censos Económicos 2024, que además de aperturas reales suma negocios que ya "
      "existían y el DENUE no tenía. Fuente: DENUE 05/2026 y 11/2020 (INEGI, ver `data/FUENTES.md`).")
    a(f"- Filas de entrenamiento: {meta['filas_entrenamiento']:,} (5 875 AGEB × {len(meta['giros'])} giros); "
      f"tasa base global {v['tasa_base_global']:.3f}. Por giro va de {met['tasa_base'].min():.4f} "
      f"({met.loc[met['tasa_base'].idxmin(), 'giro']}) a {met['tasa_base'].max():.2f} ({met.loc[met['tasa_base'].idxmax(), 'giro']}).\n")
    a("## Sin fuga de información\n")
    a("- Todo lo que sale del DENUE se calcula en el **corte 11/2020** (sectores SCIAN a 500 m y 1 km, empleo, población "
      "diurna, escuelas, hospitales, plazas, competencia y complementarios del giro). La etiqueta sale de lo que aparece después.")
    tr = pd.read_parquet(PROC / "transporte.parquet")
    q = tr[tr["anio_apertura"] > motor.ANIO_CORTE_HIST].groupby("sistema")["linea"].agg(lambda x: ", ".join(sorted(set(map(str, x)))))
    a("- Transporte en 11/2020: se quitan las estaciones con `anio_apertura` > 2020 ("
      + "; ".join(f"{k} líneas {v}" for k, v in q.items()) + f", {int((tr['anio_apertura'] > motor.ANIO_CORTE_HIST).sum())} filas) "
      "y el Tren Interurbano (sin año en el archivo; su tramo en la ZMVM no operaba en 2020, supuesto del autor). Mexibús y Mexicable no traen año de apertura en `transporte.parquet` y se dejan (posible fuga menor).")
    a("- Censo 2020 y marginación CONAPO 2020 son anteriores a la ventana. El decil imputado usa variables del Censo 2020; "
      "el gasto potencial usa la ENIGH 2024 (gasto por decil), que no contiene información de establecimientos.")
    a("- No entran nombres de colonia, municipio ni coordenadas. Sí entra `es_cdmx` (entidad).")
    a("- Para recomendar, el modelo entrenado con 11/2020 → 05/2026 se aplica a las mismas variables medidas en **05/2026** "
      "(`score_giro`), suponiendo que la relación se mantiene en la siguiente ventana.\n")
    a("## Modelo y validación espacial\n")
    a(f"Un modelo global con el giro como variable categórica (`giro_cod`) y {len(meta['features'])} variables. Parámetros: "
      f"`{json.dumps(meta['params'])}`; {meta['n_iter_final']} iteraciones en el ajuste final.")
    a(f"Validación **GroupKFold por municipio** (`cvegeo_mun`, {N_PLIEGUES} pliegues): cada municipio queda entero en "
      "entrenamiento o en prueba, así que el modelo se evalúa en alcaldías y municipios que no vio.\n")
    a("| Pliegue | Filas de prueba | Municipios en prueba | AUC | Iteraciones |")
    a("|---|---|---|---|---|")
    for p in meta["pliegues"]:
        a(f"| {p['pliegue']} | {p['n_test']:,} | {p['municipios_test']} | {p['auc']:.3f} | {p['iter']} |")
    a(f"\nFuera de pliegue (todas las filas): AUC global **{v['auc_oof_global']:.3f}**, average precision "
      f"{v['ap_oof_global']:.3f}. El AUC global mezcla giros (parte se explica por la tasa base de cada giro); "
      "lo que importa es el AUC **dentro** de cada giro, abajo.\n")
    a("## Por giro: modelo contra líneas base\n")
    a("Puntuaciones comparadas, todas fuera de pliegue y dentro de cada giro (5 875 AGEB): **modelo** (probabilidad); "
      "**densidad** de población (hab/km², Censo 2020); **competencia** (competidores del giro con peso Huff en su radio, 11/2020); "
      "**comp. AGEB** (competidores del giro dentro de la propia AGEB, 11/2020); "
      "**actividad** (establecimientos de todo tipo a 500 m, 11/2020); y el **score** combinado de `score_giro` (ver abajo). "
      "AP = average precision; P@k = proporción de las k AGEB mejor puntuadas donde sí apareció el giro.\n")
    a(f"Resumen (giros con ≥ 30 AGEB con apertura, {len(ok)} de {len(met)}): el modelo supera en AUC a la densidad en "
      f"**{gana_d}**, a la competencia Huff en **{gana_c}**, a la competencia dentro de la AGEB en **{gana_ca}** y a la "
      f"actividad en **{gana_a}**; en P@100 iguala o supera a densidad y "
      f"competencia a la vez en {gana_p}. AUC medio: modelo {ok['auc_modelo'].mean():.3f}, densidad {ok['auc_densidad'].mean():.3f}, "
      f"competencia {ok['auc_competencia'].mean():.3f}, competencia en la AGEB {ok['auc_comp_ageb'].mean():.3f}, actividad {ok['auc_actividad'].mean():.3f}, "
      f"score vigente {ok['auc_score'].mean():.3f}"
      + (f", score anterior (v2.1) {ok['auc_score_v21'].mean():.3f}" if "auc_score_v21" in ok else "")
      + ". **El score no se diseñó para predecir aperturas crudas y por eso queda debajo**: ver «¿Por qué el score no predice aperturas crudas y está bien?» abajo.\n")
    a("| Giro | AGEB con apertura | Tasa | AUC modelo | AUC dens. | AUC comp. | AUC comp. AGEB | AUC activ. | AUC score vigente | AUC score anterior | AP modelo | AP dens. | AP comp. | P@50 modelo | P@100 modelo | P@100 dens. | P@100 comp. |")
    a("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in met.sort_values("agebs_con_apertura", ascending=False).itertuples():
        nota = " *" if r.agebs_con_apertura < 30 else ""
        a(f"| {r.giro}{nota} | {r.agebs_con_apertura:,} | {r.tasa_base:.3f} | **{_f(r.auc_modelo)}** | {_f(r.auc_densidad)} | "
          f"{_f(r.auc_competencia)} | {_f(r.auc_comp_ageb)} | {_f(r.auc_actividad)} | {_f(r.auc_score)} | {_f(getattr(r, 'auc_score_v21', None))} | **{_f(r.ap_modelo)}** | {_f(r.ap_densidad)} | "
          f"{_f(r.ap_competencia)} | {_f(r.p50_modelo, 2)} | {_f(r.p100_modelo, 2)} | {_f(r.p100_densidad, 2)} | {_f(r.p100_competencia, 2)} |")
    a("\n\\* Menos de 30 AGEB con apertura: métricas inestables, no usar para decidir.\n")
    a("## Variables que más pesan\n")
    a("Importancia por permutación (caída de average precision al barajar la variable) en un pliegue espacial dejado fuera, "
      "40 000 filas, 3 repeticiones. Archivo completo: `models/importancia.csv`.\n")
    a("| # | Variable | Caída de AP | DE |")
    a("|---|---|---|---|")
    for i, r in enumerate(imp.head(20).itertuples(), 1):
        a(f"| {i} | `{r.feature}` | {r.importancia_ap:.4f} | {r.sd:.4f} |")
    a("\n## Variante «sobrevivió»\n")
    a(f"Modelo aparte, por establecimiento del corte 11/2020 de los 40 giros ({sob['n']:,} filas): ¿sigue en 05/2026 (mismo id o "
      f"mismo nombre a ≤ {meta['r_empate_m']:.0f} m)? Tasa {sob['tasa_sobrevive']:.3f}; AUC fuera de pliegue (GroupKFold por municipio) "
      f"**{sob['auc_oof']:.3f}**, AP {sob['ap_oof']:.3f}. Variables: las mismas del corte 11/2020 más el personal ocupado. "
      "En `score_giro` se reporta `prob_sobrevive` para un local nuevo de 0 a 5 personas, como dato de riesgo; **no entra al score**. "
      "Aviso: desaparecer del DENUE puede ser cierre o un cambio de registro que no se pudo empatar.\n")
    a("## Cómo se arma `score_giro`\n")
    a("`app/motor.py: score_giro(giro_clave)` → una fila por AGEB con `cvegeo, prob_apertura, demanda, competencia, "
      "complementarios, score, razones` (más `captura_huff, poblacion_objetivo, demanda_neta, pob_neta, pct_*, prob_sobrevive, "
      "nom_mun, nom_colonia, nse`). Los 40 giros ya calculados en el corte 05/2026 están en `models/scores_giros.parquet`.\n")
    a("Todo se mide en el **mismo círculo** de `radio_influencia_m` alrededor del centroide de la AGEB, con reparto "
      "**dasimétrico**: la población, el gasto y la intensidad de aperturas de cada AGEB se reparten parejo en una malla de "
      f"puntos cada {motor.PASO_MALLA_M} m dentro de su polígono (`motor.malla_agebs`). Así una AGEB enorme no suma toda su "
      "gente en su centroide y el score no crece con el tamaño de la AGEB (ver «Sesgo por tamaño» abajo).")
    a("- `prob_apertura`: probabilidad del modelo con las variables de 05/2026 (por AGEB; crece con el tamaño de la AGEB). "
      "`aperturas_esperadas`: la intensidad -ln(1-p) de cada AGEB repartida en su superficie y sumada en el radio. "
      "El primer término del score (`prob_apertura` en los pesos, por compatibilidad) es el **núcleo**: `aperturas_esperadas × captura_huff`, "
      "o sea aperturas esperadas **por competidor**.")
    a("- `demanda`: gasto potencial trimestral del rubro ENIGH del giro (`rubro_enigh`, pesos de 2024) de los hogares "
      "dentro del radio de influencia, con peso por distancia w(d) = 1/(1+(d/d0)²), d0 = radio/2, 0 fuera del radio.")
    a("- `poblacion_objetivo`: residentes por edad ponderados con `cliente_objetivo` (Censo 2020) dentro del radio; si `demanda_base` es "
      "`diurna`, el empleo del DENUE en el radio; si es `mixta`, el promedio. `pob_neta` lo multiplica por `nse_fit` "
      "(probabilidad de que el hogar sea del NSE objetivo del giro) y por la captura Huff.")
    a("- `competencia`: competidores del giro con peso Huff (`conteos_de_giro`). **Saturación (Huff)**: un local nuevo igual de "
      "atractivo que los existentes se lleva `captura_huff = 1/(1 + competencia)` del mercado. `demanda_neta = demanda × captura_huff`.")
    a("- `flujo`: no hay aforos peatonales abiertos para la ZMVM; se usan proxies: empleo del DENUE en el radio (`empleo_radio`), "
      "negocios de corredor comercial (sectores SCIAN 46, 72 y 81) en el radio (`corredor_radio`) y transporte a 1 km "
      "(afluencia anual del Metro y número de estaciones). `flujo` = promedio de sus percentiles (transporte vale la mitad de un término).")
    a("- `complementarios`: negocios que atraen al cliente (`complementarios` de giros.yaml), con peso Huff.\n")
    a("**Pesos explícitos** (cada término es el percentil 0-1 de la AGEB dentro de la ZMVM para ese giro; score de 0 a 100):\n")
    a("| Término | Peso |")
    a("|---|---|")
    for k, p in w.items():
        a(f"| percentil de `{k}` | {p:.2f} |")
    a("\nSi el giro no tiene rubro ENIGH (`coworking`), el peso de `demanda_neta` pasa a `pob_neta`. "
      "**Los pesos no los puso el autor**: los aprendió `scripts/03b_validar_score.py` contra el crecimiento neto, la sobrevivencia y las altas fuera de la "
      "carga censal, con pesos no negativos que suman 1, ajustados en pliegues por municipio y reportados en el que no vieron, "
      "con la restricción a priori de que la demanda (gasto + población) pese al menos 25 %. Están en `models/pesos_score.json` y la evidencia en "
      "`reports/validacion_score.md`. **El score es un percentil dentro de cada giro: ordena sitios para un giro y no compara "
      "giros entre sí** (una librería con score 90 puede tener 5 % de probabilidad de apertura). Para comparar giros, "
      "`app/herramientas.py: sugerir_giros` usa la probabilidad absoluta de apertura × la de seguir abierto.\n")
    escribir_validacion_score(a)
    escribir_sesgo(a)
    a("## Límites\n")
    a("- La etiqueta es «apareció en el DENUE», sesgada por la cobertura de los Censos Económicos 2024 (ver arriba).")
    a("- Una AGEB con más hogares o más comercio tiene más oportunidades de que aparezca algo: el modelo mide oportunidad de "
      "apertura, no rentabilidad ni ventas.")
    a("- Los giros raros (renta de bicicletas, coworking, comida china, escuela de idiomas, librería, guardería) tienen pocas "
      "aperturas: su probabilidad descansa en el patrón general del modelo global.")
    a("- La validación por municipio es espacial pero no perfecta: AGEB vecinas de municipios distintos se parecen.")
    a("- La variable que más pesa es `comp_ageb` (negocios del giro que ya había en la AGEB): donde ya hay del giro es donde más "
      "aparecen, en parte por rotación (cierra uno y abre otro en el mismo local cuenta como apertura) y en parte por aglomeración.")
    a("- Los radios, el cliente objetivo, el NSE objetivo y los complementarios son supuestos de `config/giros.yaml`.\n")
    sg = MODELS / "scores_giros.parquet"
    if sg.exists():
        e = (pd.read_parquet(sg, filters=[("giro", "==", "heladeria")]).sort_values("score", ascending=False).head(5))
        a("## Ejemplo: heladería, corte 05/2026 (top 5 de `score_giro`)\n")
        a("| AGEB | Municipio | Colonia (DENUE) | NSE | prob_apertura | Gasto potencial helados a 500 m ($/trim) | Competidores Huff | Score |")
        a("|---|---|---|---|---|---|---|---|")
        for r in e.itertuples():
            a(f"| {r.cvegeo} | {r.nom_mun} | {r.nom_colonia} | {r.nse} | {r.prob_apertura:.2f} | {r.demanda:,.0f} | "
              f"{r.competencia:.1f} | {r.score:.1f} |")
        a("\nFuentes: modelo de este reporte; ENIGH 2024 (gasto por decil, ámbito zmvm) y decil imputado (`reports/decil_imputado.md`); "
          "DENUE 05/2026; Censo 2020. El rubro `helados` de la ENIGH tiene pocos hogares con gasto: sirve para ordenar, no para dimensionar.\n")
    a("## Reproducir\n")
    a("```bash\nOMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03_entrenar.py      # etiquetas, validación, modelos, scores, este reporte\n"
      "uv run python scripts/03_entrenar.py --solo-reporte                     # solo reescribe este archivo\n"
      "uv run pytest tests/test_modelo.py -q\n```")
    a(f"\nTiempo de la última corrida completa: {meta['segundos']} s.")
    REPORTE.write_text("\n".join(L) + "\n", encoding="utf-8")
    log(f"reporte: {REPORTE.relative_to(RAIZ)}")


def escribir_validacion_score(a) -> None:
    """Seccion del reporte: resumen de reports/validacion_score.md y la pregunta de examen sobre aperturas crudas."""
    f = MODELS / "validacion_score.csv"
    rj = MODELS / "validacion_score_resumen.json"
    if not (f.exists() and rj.exists()):
        return
    r = pd.read_csv(f)
    info = json.loads(rj.read_text(encoding="utf-8"))
    m = r.groupby(["objetivo", "puntuacion"])["valor"].mean()
    bases = ["densidad", "comp_huff", "comp_ageb", "actividad"]

    def mejor(o):
        c = 0.5 if o == "aperturas_crudas" else 0.0
        return max(abs(m[(o, b)] - c) for b in bases) + c

    a("## ¿Por qué el score no predice aperturas crudas y está bien?\n")
    b = info["diagnostico"]["bins"]
    a("**Respuesta corta, como la diría Juan Pablo:** «El score no está hecho para adivinar dónde aparecen más negocios, sino dónde conviene poner uno. "
      f"Las aperturas se aglomeran donde ya hay competencia: en las AGEB con 3 o más negocios del giro en 2020 aparecieron {10 * b['aper_por_estab']:.0f} nuevos por cada 10 que ya había "
      f"y desaparecieron otros {10 * b['cierres_por_estab']:.0f}, o sea que hay mucha rotación. Un score que castiga la competencia, como debe hacerlo uno de ubicación, "
      "forzosamente queda debajo de la competencia a secas para predecir aperturas crudas. Por eso lo medí contra lo que sí corresponde a la decisión: "
      "crecimiento neto, sobrevivencia y altas fuera de la carga censal. El score nuevo le gana a las líneas base en la tasa de crecimiento neto, "
      "pero esa ventaja viene de la carga de los Censos Económicos 2024 (negocios que ya existían y no estaban en el DENUE 2020): quitando la carga "
      "(crecimiento neto sin carga censal) no le gana al score anterior, en altas fuera de la carga pierde y en sobrevivencia empata (que ninguna "
      "variable predice bien dentro de un giro). Por eso lo conservo como decisión de diseño, no como victoria medida; el detalle y "
      "las limitaciones están en `reports/validacion_score.md`.»\n")
    a("Evidencia, promedio entre giros (ρ de Spearman; AUC en la última fila). La probabilidad de apertura es fuera de muestra por municipio; los "
      "pesos vigentes se ajustaron con todos los datos y la columna «pesos fuera de muestra» los ajusta sin ver el municipio de prueba:\n")
    a("| Objetivo | Score anterior (v2.1) | Score vigente | Score vigente, pesos fuera de muestra | Mejor línea base ingenua |")
    a("|---|---|---|---|---|")
    nom = {"crecimiento_neto": "Crecimiento neto", "sobrevivencia": "Sobrevivencia", "altas_reales": "Altas fuera de la carga censal",
           "neto_sin_carga": "Crecimiento neto sin carga censal", "aperturas_crudas": "Aperturas crudas (AUC)"}
    for o, n in nom.items():
        if (o, "score_nuevo") not in m.index:   # validacion_score.csv de antes del objetivo sin carga censal
            continue
        a(f"| {n} | {m[(o, 'score_v21')]:.3f} | {m[(o, 'score_nuevo')]:.3f} | {m[(o, 'score_nuevo_oos')]:.3f} | {mejor(o):.3f} |")
    n = info["nse"]
    a(f"\nDecil imputado: acierta el decil exacto {100 * n['decil_exacto']:.1f} % y ±1 decil {100 * n['decil_mas_menos_1']:.1f} %; la **banda de NSE** que usa el producto "
      f"(bajo 1-4, medio 5-8, alto 9-10) la acierta {100 * n['banda_exacta']:.1f} % de los hogares (decir siempre «medio» daría {100 * n['mayoritaria']:.0f} %), "
      f"con {100 * n['recall']['bajo']:.0f} % de acierto en bajo, {100 * n['recall']['medio']:.0f} % en medio y {100 * n['recall']['alto']:.0f} % en alto. "
      "Fuente: ENIGH 2024 y modelo propio (`reports/validacion_score.md`, sección 4).\n")


def escribir_sesgo(a) -> None:
    """Seccion del reporte: correlacion del score y de la prob. por AGEB con el tamano de la AGEB."""
    from scipy.stats import spearmanr

    sg = MODELS / "scores_giros.parquet"
    if not sg.exists():
        return
    s = pd.read_parquet(sg, columns=["cvegeo", "giro", "score", "prob_apertura"])
    f = motor.cargar_features()[["pob_total", "area_km2", "densidad_hab_km2"]]
    s = s.join(f, on="cvegeo")
    filas = []
    for g, d in s.groupby("giro"):
        top = d.nlargest(50, "score")
        filas.append({"giro": g, "rho_score_pob": spearmanr(d["score"], d["pob_total"], nan_policy="omit").statistic,
                      "rho_prob_pob": spearmanr(d["prob_apertura"], d["pob_total"], nan_policy="omit").statistic,
                      "rho_score_area": spearmanr(d["score"], d["area_km2"], nan_policy="omit").statistic,
                      "rho_score_dens": spearmanr(d["score"], d["densidad_hab_km2"], nan_policy="omit").statistic,
                      "top50_pob": top["pob_total"].median(), "top50_area": top["area_km2"].median()})
    t = pd.DataFrame(filas)
    a("## Sesgo por tamaño de AGEB\n")
    a("La etiqueta («apareció ≥ 1 negocio del giro en la AGEB») crece con el tamaño de la AGEB: una AGEB con 29 mil habitantes "
      "tiene más oportunidades de que aparezca algo que una de 3 mil. Por eso `prob_apertura` no se usa tal cual en el score: "
      "todo se mide en el círculo del radio con reparto dasimétrico (arriba). Spearman entre 5 875 AGEB, promedio de los "
      f"{len(t)} giros (mínimo y máximo entre giros):\n")
    a("| Medida | Promedio | Mínimo | Máximo |")
    a("|---|---|---|---|")
    for c, n in [("rho_prob_pob", "ρ(prob_apertura por AGEB, población de la AGEB)"), ("rho_score_pob", "ρ(score, población de la AGEB)"),
                 ("rho_score_area", "ρ(score, área de la AGEB)"), ("rho_score_dens", "ρ(score, densidad hab/km²)")]:
        a(f"| {n} | {t[c].mean():.2f} | {t[c].min():.2f} | {t[c].max():.2f} |")
    a(f"\nMediana del top 50 por giro (promedio de los giros): población {t['top50_pob'].mean():,.0f} y área "
      f"{t['top50_area'].mean():.2f} km²; en toda la ZMVM, {f['pob_total'].median():,.0f} y {f['area_km2'].median():.2f} km². "
      "Lo que queda de correlación con la población va de la mano con la densidad (zonas más pobladas por km²), que sí es "
      "una razón económica para poner un negocio. Fuente: `models/scores_giros.parquet` y Censo 2020.\n")


# =============================================================== 3. principal
def sha12(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def entrenar() -> None:
    t0 = time.time()
    MODELS.mkdir(exist_ok=True)
    et, estab, res_et = etiquetas()
    et.to_parquet(MODELS / "etiquetas.parquet", index=False)
    log(f"etiquetas: {len(et):,} filas, {int(et['y_apertura'].sum()):,} positivas; {res_et['nuevos']:,} nuevos "
        f"({res_et['empatados_por_nombre']:,} empatados por nombre) ({time.time() - t0:.0f} s)")

    mh = motor.matriz_modelo("hist")
    m = mh.merge(et, on=["cvegeo", "giro"], how="left", validate="1:1")
    cols = columnas_x(mh)
    assert cols[0] == "giro_cod"
    X, y, gr = m[cols], m["y_apertura"].to_numpy(), m["cvegeo_mun"].to_numpy()
    log(f"matriz hist: {X.shape}, tasa base {y.mean():.3f} ({time.time() - t0:.0f} s)")

    oof, pliegues = validar(X, y, gr)
    d = m[["cvegeo", "giro", "y_apertura", "n_aperturas", "densidad_hab_km2", "comp_huff", "comp_ageb",
           "estab_500m"]].copy()
    d["oof"] = oof
    sc = []
    for giro, idx in m.groupby("giro", sort=False).indices.items():
        sc.append(pd.Series(motor.combinar_score(giro, m.iloc[idx], oof[idx], corte="hist")["score"].to_numpy(),
                            index=m.index[idx]))
    d["score_comb"] = pd.concat(sc).reindex(d.index)
    d.to_parquet(MODELS / "oof.parquet", index=False)
    met = metricas_giro(d, {"modelo": "oof", "densidad": "densidad_hab_km2", "competencia": "comp_huff",
                            "comp_ageb": "comp_ageb", "actividad": "estab_500m", "score": "score_comb"})
    met.to_csv(MODELS / "metricas_giro.csv", index=False)
    glob = {"auc_oof_global": float(roc_auc_score(y, oof)), "ap_oof_global": float(average_precision_score(y, oof)),
            "tasa_base_global": float(y.mean())}
    log(f"validacion: AUC global {glob['auc_oof_global']:.3f}; AUC medio por giro modelo "
        f"{met['auc_modelo'].mean():.3f} vs densidad {met['auc_densidad'].mean():.3f} vs competencia "
        f"{met['auc_competencia'].mean():.3f} ({time.time() - t0:.0f} s)")

    imp = importancia(X, y, gr)
    imp.to_csv(MODELS / "importancia.csv", index=False)
    log(f"importancia lista ({time.time() - t0:.0f} s)")

    clf = modelo().fit(X, y)
    joblib.dump(clf, MODELS / "aperturas.joblib", compress=3)
    sob, res_sob, cols_sob = sobrevivencia(estab, mh)
    joblib.dump(sob, MODELS / "sobrevivencia.joblib", compress=3)
    meta = {"fecha": date.today().isoformat(), "modelo": "sklearn HistGradientBoostingClassifier",
            "sklearn": __import__("sklearn").__version__, "params": PARAMS, "n_iter_final": int(clf.n_iter_),
            "modelo_id": sha12(MODELS / "aperturas.joblib"), "features": cols, "features_sobrevivencia": cols_sob,
            "categoricas": ["giro_cod"], "giros": list(motor.giros()),
            "cortes": {"features": "DENUE 11/2020 + Censo 2020", "etiqueta": "aparece en DENUE 05/2026 y no en 11/2020"},
            "r_empate_m": R_EMPATE, "pliegues": pliegues, "validacion": glob, "etiquetas": res_et,
            "sobrevivencia": res_sob, "pesos_score": motor.PESOS_SCORE, "top_k": list(TOP_K),
            "filas_entrenamiento": int(len(y)), "segundos": round(time.time() - t0)}
    (MODELS / "metadata.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False, default=str), "utf-8")
    log(f"modelos guardados ({time.time() - t0:.0f} s)")
    scores_actuales()
    log(f"listo en {time.time() - t0:.0f} s")


def scores_actuales() -> None:
    """score_giro de los 40 giros en el corte actual -> models/scores_giros.parquet (lo usa la app)."""
    motor.cargar_modelo.cache_clear()
    _, _, meta = motor.cargar_modelo()
    partes = [motor.score_giro(g, usar_cache=False).assign(giro=g) for g in motor.giros()]
    s = pd.concat(partes, ignore_index=True).assign(modelo_id=meta["modelo_id"]).drop(columns="razones")
    s.to_parquet(MODELS / "scores_giros.parquet", index=False)
    log(f"scores_giros: {len(s):,} filas")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-etiquetas", action="store_true")
    ap.add_argument("--solo-reporte", action="store_true")
    ap.add_argument("--solo-scores", action="store_true")
    a = ap.parse_args()
    if a.solo_etiquetas:
        et, estab, res = etiquetas()
        et.to_parquet(MODELS / "etiquetas.parquet", index=False)
        log(json.dumps(res, ensure_ascii=False, default=str))
        log(et.groupby("giro")[["y_apertura", "n_aperturas", "n_hist", "n_sobreviven"]].sum().to_string())
        return
    if a.solo_scores:
        scores_actuales()
    elif not a.solo_reporte:
        entrenar()
        # el score se valida contra los objetivos de decision y sus pesos se reaprenden (03b); luego se regeneran los scores
        (MODELS / "oof_sobrevive.parquet").unlink(missing_ok=True)
        spec = importlib.util.spec_from_file_location("validar_score03b", RAIZ / "scripts" / "03b_validar_score.py")
        m03b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m03b)
        m03b.main([])
        scores_actuales()
    escribir_reporte()


if __name__ == "__main__":
    main()
