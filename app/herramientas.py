"""Herramientas del agente (Python puro, se prueban sin LLM).

Cada funcion regresa un dict listo para json.dumps, con cifras ya redondeadas y un campo `fuentes`.
Lo que no esta en los datos sale como "NO ENCONTRADO". El agente (app/agente.py) solo puede citar
numeros que vengan de aqui.

    perfil_giro(texto)                                  -> giro de config/giros.yaml (o propuestas SCIAN)
    recomendar_zonas(giro, municipio, nse, top)         -> top de colonias (AGEB) con score y razones
    ficha_zona(zona, municipio, giro)                   -> datos de una AGEB o de una colonia
    buscar_carpetas(pregunta, k)                        -> trozos de carpetas/ (RAG)
    contexto_macro()                                    -> macro.json resumido
    sugerir_giros(municipio, nse, ticket_max, top)      -> extra: giros que mejor salen en una zona
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from app import motor, rag

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
NO = "NO ENCONTRADO"

# fuentes cortas (las URL completas y sha256 estan en data/FUENTES.md)
F_CENSO = "INEGI, Censo de Poblacion y Vivienda 2020, resultados por AGEB urbana"
F_MARCO = "INEGI, Marco Geoestadistico 2020 (poligonos de AGEB)"
F_DENUE = "INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)"
F_ENIGH = "INEGI, ENIGH 2024 (gasto trimestral por decil, ambito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)"
F_CONAPO = "CONAPO, Indice de marginacion urbana 2020"
F_MODELO = "Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)"
F_GIROS = "config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)"
F_SCIAN = "INEGI, SCIAN 2023 (data/processed/scian.csv)"
F_ZMVM = "SEDATU-CONAPO-INEGI, delimitacion de zonas metropolitanas 2015 (data/processed/zmvm_municipios.csv)"
F_TRANSP = "datos.cdmx.gob.mx (Metro, Metrobus, STE, GTFS) y OpenStreetMap para Mexibus/Mexicable (data/FUENTES.md)"


# ---------------------------------------------------------------- utilidades
def norm(s) -> str:
    """minusculas, sin acentos ni signos."""
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s.lower())).strip()


def _r(x, nd=0):
    """Redondea y regresa None si no es finito (json no acepta NaN)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(v):
        return None
    v = round(v, nd)
    return int(v) if nd <= 0 else v


def _txt(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) or pd.isna(x) else str(x)


def a_json(d: dict) -> str:
    """JSON compacto (lo que se le pasa al LLM)."""
    return json.dumps(d, ensure_ascii=False, separators=(",", ":"))


@lru_cache(maxsize=1)
def municipios() -> pd.DataFrame:
    return pd.read_csv(PROC / "zmvm_municipios.csv", dtype=str)


def resolver_municipio(texto: str | None) -> dict:
    """Nombre o clave -> {ok, cvegeo_mun, nom_mun} | {ok: False, motivo, sugerencias}."""
    if not texto:
        return {"ok": True, "cvegeo_mun": None, "nom_mun": None}
    mun = municipios()
    t = str(texto).strip()
    if re.fullmatch(r"\d{5}", t) and t in set(mun["cvegeo_mun"]):
        return {"ok": True, "cvegeo_mun": t, "nom_mun": mun.set_index("cvegeo_mun").at[t, "nom_mun"]}
    n = norm(t)
    por_nom = {norm(a): (c, a) for c, a in zip(mun["cvegeo_mun"], mun["nom_mun"])}
    if n in por_nom:
        c, a = por_nom[n]
        return {"ok": True, "cvegeo_mun": c, "nom_mun": a}
    hall = rag.municipios_en(t)
    if len(hall) == 1:
        c = mun.loc[mun["nom_mun"] == hall[0], "cvegeo_mun"].iloc[0]
        return {"ok": True, "cvegeo_mun": c, "nom_mun": hall[0]}
    fuera = rag.ciudades_fuera(t)
    if fuera:
        return {"ok": False, "fuera_de_zmvm": True,
                "motivo": f"{t} esta fuera de la Zona Metropolitana del Valle de Mexico; el modelo solo cubre sus 76 municipios"}
    sug = difflib.get_close_matches(n, list(por_nom), n=3, cutoff=0.6)
    return {"ok": False, "motivo": f"{NO}: '{t}' no es un municipio o alcaldia de la ZMVM",
            "sugerencias": [por_nom[s][1] for s in sug]}


def _fuera(texto: str) -> list[str]:
    return rag.ciudades_fuera(texto or "")


# ---------------------------------------------------------------- perfil_giro
@lru_cache(maxsize=1)
def _sinonimos() -> list[tuple[str, str]]:
    """(frase normalizada, clave), las mas largas primero."""
    pares = set()
    for k, g in motor.giros().items():
        for s in list(g.get("nombres", [])) + [k.replace("_", " ")]:
            pares.add((norm(s), k))
    return sorted(pares, key=lambda p: -len(p[0]))


def _singular(n: str) -> str:
    """'heladerias' -> 'heladeria', 'farmacias' -> 'farmacia' (palabra por palabra, conservador)."""
    out = []
    for w in n.split():
        if len(w) > 5 and w.endswith("es") and w[-3] in "rnld":
            w = w[:-2]
        elif len(w) > 4 and w.endswith("s"):
            w = w[:-1]
        out.append(w)
    return " ".join(out)


def _buscar_giro(texto: str) -> tuple[str | None, str | None]:
    """Clave del giro cuyo sinonimo aparece (palabras completas) en el texto; el sinonimo mas largo gana."""
    for q in (f" {norm(texto)} ", f" {_singular(norm(texto))} "):
        for frase, clave in _sinonimos():
            if f" {frase} " in q or f" {_singular(frase)} " in q:
                return clave, frase
    return None, None


@lru_cache(maxsize=1)
def _conteo_scian() -> pd.Series:
    d = pd.read_parquet(PROC / "denue_actual.parquet", columns=["codigo_act"])
    return d["codigo_act"].value_counts()


@lru_cache(maxsize=1)
def _metricas() -> pd.DataFrame:
    p = RAIZ / "models" / "metricas_giro.csv"
    return pd.read_csv(p).set_index("giro") if p.exists() else pd.DataFrame()


def _scian_proponer(texto: str, n: int = 3) -> list[dict]:
    """Clases SCIAN (6 digitos) cuyo titulo comparte palabras con el texto."""
    vacias = {"quiero", "poner", "abrir", "negocio", "tienda", "donde", "para", "una", "unos", "como", "zona",
              "colonia", "mejor", "conviene", "ciudad", "mexico", "local", "venta", "servicio", "servicios",
              "algo", "barato", "nivel", "bajo", "medio", "alto", "cerca", "economico"}
    toks = [t for t in _singular(norm(texto)).split() if len(t) >= 4 and t not in vacias]
    if not toks:
        return []
    sc = pd.read_csv(PROC / "scian.csv", dtype=str)
    sc = sc[sc["codigo"].str.len() == 6].copy()
    tit = sc["titulo"].map(lambda s: _singular(norm(s)))
    sc["p"] = [sum(f" {t} " in f" {tt} " for t in toks) for tt in tit]  # palabras completas
    sc = sc[sc["p"] > 0].sort_values(["p", "codigo"], ascending=[False, True]).head(n)
    cnt = _conteo_scian()
    return [{"scian": c, "titulo": t, "establecimientos_zmvm_2026": int(cnt.get(c, 0))}
            for c, t in zip(sc["codigo"], sc["titulo"])]


def perfil_giro(texto: str) -> dict:
    """Texto libre ('quiero poner una neveria') -> giro del catalogo con sus supuestos."""
    clave, frase = _buscar_giro(texto or "")
    if clave is None:
        props = _scian_proponer(texto or "")
        return {"encontrado": False,
                "motivo": f"{NO}: ningun giro de config/giros.yaml coincide con el texto",
                "propuestas_scian": props,
                "giros_disponibles": sorted(motor.giros()),
                "sugerencia": "usa sugerir_giros(municipio, nse) si la persona no tiene giro definido",
                "fuentes": [F_GIROS] + ([F_SCIAN, F_DENUE] if props else [])}
    g = motor.giros()[clave]
    cnt = _conteo_scian()
    comp_directa = int(sum(cnt.get(c, 0) for c in g.get("scian", [])))
    out = {"encontrado": True, "giro": clave, "coincidencia": frase, "nombres": g.get("nombres", [])[:4],
           "scian_competencia": g.get("scian", []),
           "scian_con_filtro_por_nombre": [f["codigos"] for f in g.get("scian_con_filtro", [])] or None,
           "establecimientos_zmvm_2026_clases_scian": comp_directa if g.get("scian") else None,
           "radio_influencia_m": g["radio_influencia_m"],
           "cliente_objetivo_edades": g.get("cliente_objetivo"), "nse_objetivo": g.get("nse_objetivo"),
           "demanda_base": g.get("demanda_base", "residente"),
           "rubro_enigh": g.get("rubro_enigh") or NO,
           "ticket_promedio_mxn": g.get("ticket_promedio_mxn"), "ticket_fuente": g.get("ticket_fuente"),
           "notas": g.get("notas")}
    if g.get("rubro_enigh_nota"):
        out["aviso_rubro"] = g["rubro_enigh_nota"]
    m = _metricas()
    if clave in m.index:
        r = m.loc[clave]
        out["validacion_modelo"] = {"auc_modelo": _r(r["auc_modelo"], 2), "auc_linea_base_densidad": _r(r["auc_densidad"], 2),
                                    "agebs_con_apertura_2020_2026": _r(r["agebs_con_apertura"])}
        if r["agebs_con_apertura"] < 30:
            out["aviso_modelo"] = "giro raro: muy pocas AGEB con aperturas, el modelo es poco confiable para este giro"
    out["fuentes"] = [F_GIROS, F_DENUE, F_MODELO]
    return out


# ---------------------------------------------------------------- recomendar_zonas
def _resolver_giro(giro: str) -> str | None:
    if giro in motor.giros():
        return giro
    clave, _ = _buscar_giro(giro or "")
    return clave


@lru_cache(maxsize=40)
def _score(clave: str) -> pd.DataFrame:
    d = motor.score_giro(clave)
    f = motor.cargar_features()
    extra = f[["cve_ent", "cve_mun", "decil_imputado", "pob_total", "hogares", "ing_trim_mediano_est"]]
    d = d.join(extra, on="cvegeo")
    d["cvegeo_mun"] = d["cve_ent"].astype(str) + d["cve_mun"].astype(str)
    d["rank_zmvm"] = np.arange(1, len(d) + 1)
    return d


def _zona(r, clave: str) -> dict:
    g = motor.giros()[clave]
    return {"colonia": _txt(r["nom_colonia"]), "municipio": _txt(r["nom_mun"]), "ageb": r["cvegeo"],
            "score": _r(r["score"], 1), "rank_zmvm": int(r["rank_zmvm"]),
            "prob_apertura_pct": _r(100 * r["prob_apertura"]),
            "aperturas_esperadas_en_radio": _r(r["aperturas_esperadas"], 2),
            "gasto_potencial_trim_mxn": _r(r["demanda"], -3) if np.isfinite(r["demanda"]) else NO,
            "competidores_ponderados": _r(r["competencia"], 1),
            "captura_huff_pct": _r(100 * r["captura_huff"]),
            "residentes_objetivo_en_radio": _r(r["residentes_objetivo"], -1),
            "empleos_en_radio": _r(r["empleo_radio"], -1),
            "demanda_de_personas": BASE_DEMANDA[g.get("demanda_base", "residente")],
            "negocios_corredor_comercial_en_radio": _r(r["corredor_radio"]),
            "complementarios_ponderados": _r(r["complementarios"], 1),
            "prob_sigue_abierto_pct": _r(100 * r["prob_sobrevive"]) if pd.notna(r.get("prob_sobrevive")) else NO,
            "nse_estimado": _txt(r["nse"]) or NO,
            "decil_estimado": _r(r["decil_imputado"]) if pd.notna(r["decil_imputado"]) else NO,
            "poblacion_ageb_2020": _r(r["pob_total"]),
            "radio_m": g["radio_influencia_m"]}


BASE_DEMANDA = {"residente": "residentes objetivo", "diurna": "empleos (poblacion que trabaja ahi)",
                "mixta": "mitad residentes objetivo, mitad empleos"}
NOMBRES_PESOS = {"prob_apertura": "aperturas esperadas del giro (modelo)", "demanda_neta": "gasto potencial x captura Huff",
                 "pob_neta": "poblacion objetivo x ajuste a NSE x captura", "flujo": "flujo de gente (empleo, corredor comercial, Metro)",
                 "complementarios": "complementarios"}
COMO_LEER = ("el score 0-100 es un percentil DENTRO de este giro: ordena colonias para este giro en la ZMVM; "
             "no dice que el giro sea rentable ni sirve para comparar giros entre si (para eso, prob. de apertura absoluta)")
PROB_BAJA = 0.10  # prob. de apertura por AGEB debajo de esto = pocos negocios del giro abren ahi


def metodo_score() -> str:
    return ("score 0-100 = " + " + ".join(f"{100 * w:.0f} % {NOMBRES_PESOS[k]}" for k, w in motor.PESOS_SCORE.items())
            + "; todo medido en el radio de influencia (reparto dasimetrico de cada AGEB en una malla de 100 m) "
              "y cada termino en percentil dentro de la ZMVM para el giro")


def recomendar_zonas(giro: str, municipio: str | None = None, nse: str | None = None, top: int = 5,
                     una_por_colonia: bool = True) -> dict:
    """Top de AGEB (colonias) para un giro, opcionalmente dentro de un municipio y/o NSE."""
    clave = _resolver_giro(giro)
    if clave is None:
        return {"encontrado": False, "motivo": f"{NO}: giro '{giro}' no esta en config/giros.yaml",
                "giros_disponibles": sorted(motor.giros()), "fuentes": [F_GIROS]}
    mres = resolver_municipio(municipio)
    if not mres["ok"]:
        return {"encontrado": False, "giro": clave, **{k: v for k, v in mres.items() if k != "ok"},
                "fuentes": [F_ZMVM]}
    d = _score(clave)
    filtros = {}
    if mres["cvegeo_mun"]:
        d = d[d["cvegeo_mun"] == mres["cvegeo_mun"]]
        filtros["municipio"] = mres["nom_mun"]
    if nse:
        n = norm(nse)
        if n not in ("bajo", "medio", "alto"):
            return {"encontrado": False, "motivo": "nse debe ser bajo, medio o alto", "fuentes": []}
        d = d[d["nse"] == n]
        filtros["nse"] = n
    if d.empty:
        return {"encontrado": False, "giro": clave, "filtros": filtros,
                "motivo": f"{NO}: no hay AGEB urbanas con esos filtros", "fuentes": [F_CENSO]}
    n_eval = int(len(d))
    if una_por_colonia:  # la mejor AGEB de cada colonia, para no repetir la misma colonia 5 veces
        d = d.drop_duplicates(subset=["nom_mun", "nom_colonia"], keep="first")
    top = max(1, min(int(top or 5), 10))
    zonas = [_zona(r, clave) for _, r in d.head(top).iterrows()]
    g = motor.giros()[clave]
    avisos = ["«aparecio en el DENUE» no es lo mismo que «abrio»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Economicos",
              "el NSE y el decil por AGEB son estimaciones del proyecto (ENIGH no representa colonias)",
              f"ticket promedio {g.get('ticket_promedio_mxn')} MXN es supuesto ({g.get('ticket_fuente')})"]
    if g.get("rubro_enigh_nota"):
        avisos.append(g["rubro_enigh_nota"])
    if not g.get("rubro_enigh"):
        avisos.append("sin rubro ENIGH para este giro: gasto potencial NO ENCONTRADO, el score usa poblacion objetivo")
    m = _metricas()
    if clave in m.index and m.at[clave, "agebs_con_apertura"] < 30:
        avisos.append(f"giro raro: solo {int(m.at[clave, 'agebs_con_apertura'])} AGEB con aperturas 2020-2026; el modelo es poco confiable")
    out = {"encontrado": True, "giro": clave, "filtros": filtros or None, "agebs_evaluadas": n_eval,
           "metodo": metodo_score(), "como_leer_score": COMO_LEER}
    probs = [z["prob_apertura_pct"] for z in zonas]
    if max(probs) < 100 * PROB_BAJA:
        tb = f"; en la ZMVM aparecio en el {_r(100 * m.at[clave, 'tasa_base'])} % de las AGEB" if clave in m.index else ""
        out["aviso_prob_baja"] = (f"probabilidad de apertura baja en todo el top ({min(probs)} a {max(probs)} %){tb}: "
                                  "el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable")
        avisos.insert(0, out["aviso_prob_baja"])
    return {**out, "rubro_enigh": g.get("rubro_enigh") or NO,
            "zonas": zonas, "avisos": avisos,
            "fuentes": [F_MODELO, F_DENUE, F_CENSO, F_ENIGH, F_GIROS]}


# ---------------------------------------------------------------- ficha_zona
def _ficha(f: pd.Series, clave: str | None) -> dict:
    out = {"ageb": f["cvegeo"], "colonia": _txt(f["nom_colonia"]), "municipio": _txt(f["nom_mun"]),
           "colonia_fuente": _txt(f.get("colonia_fuente")),
           "poblacion_2020": _r(f["pob_total"]), "hogares_2020": _r(f["hogares"]),
           "densidad_hab_km2": _r(f["densidad_hab_km2"], -1), "area_km2": _r(f["area_km2"], 3),
           "edades_2020": {"0-14": _r(f["pob_0_14"]), "15-24": _r(f["pob_15_24"]), "25-59": _r(f["pob_25_59"]),
                           "60+": _r(f["pob_60_mas"])},
           "escolaridad_prom_anios": _r(f["escolaridad_prom"], 1),
           "pct_viviendas_auto": _r(f["pct_viv_auto"]), "pct_viviendas_internet": _r(f["pct_viv_internet"]),
           "nse_estimado": _txt(f["nse"]) or NO,
           "decil_estimado": _r(f["decil_imputado"]) if pd.notna(f["decil_imputado"]) else NO,
           "ingreso_trim_mediano_estimado_mxn": _r(f["ing_trim_mediano_est"], -2) if pd.notna(f["ing_trim_mediano_est"]) else NO,
           "grado_marginacion_conapo_2020": _txt(f["gm_2020"]) or NO,
           "establecimientos_denue_en_ageb": _r(f["n_establecimientos"]),
           "empleados_denue_en_ageb": _r(f["pob_diurna"]),
           "escuelas_1km": _r(f["n_escuelas_1km"]), "hospitales_1km": _r(f["n_hospitales_1km"]),
           "plazas_o_super_1km": _r(f["n_plazas_1km"]),
           "estacion_cercana": _txt(f["estacion_cercana"]), "sistema_estacion": _txt(f["sistema_estacion"]),
           "dist_estacion_m": _r(f["dist_estacion_m"], -1),
           "fuentes": [F_CENSO, F_DENUE, F_CONAPO, F_ENIGH, F_TRANSP]}
    if clave:
        d = _score(clave)
        fila = d[d["cvegeo"] == f["cvegeo"]]
        if len(fila):
            z = _zona(fila.iloc[0], clave)
            out["giro"] = {"clave": clave, **{k: v for k, v in z.items() if k not in ("colonia", "municipio", "ageb")},
                           "de_agebs": int(len(d))}
            out["fuentes"].append(F_MODELO)
    return out


def ficha_zona(zona: str, municipio: str | None = None, giro: str | None = None) -> dict:
    """Ficha de una AGEB (clave de 13 caracteres) o de una colonia (nombre; puede haber varias AGEB)."""
    f = motor.cargar_features()
    clave = _resolver_giro(giro) if giro else None
    z = str(zona or "").strip().upper()
    if re.fullmatch(r"\d{9}[0-9A-Z]{4}", z):
        if z not in f.index:
            return {"encontrado": False, "motivo": f"{NO}: AGEB {z} no esta en agebs_features (ZMVM urbana)",
                    "fuentes": [F_CENSO]}
        return {"encontrado": True, **_ficha(f.loc[z], clave)}
    if _fuera(zona):
        return {"encontrado": False, "fuera_de_zmvm": True, "motivo": f"{zona} esta fuera de la ZMVM", "fuentes": [F_ZMVM]}
    cand = f
    if municipio:
        mres = resolver_municipio(municipio)
        if not mres["ok"]:
            return {"encontrado": False, **{k: v for k, v in mres.items() if k != "ok"}, "fuentes": [F_ZMVM]}
        cand = f[f["nom_mun"] == mres["nom_mun"]]
    n = norm(zona)
    col = cand["nom_colonia"].map(norm)
    hit = cand[col == n]
    if hit.empty:
        hit = cand[col.str.contains(rf"\b{re.escape(n)}\b", regex=True)] if n else hit
    if hit.empty:
        mres = resolver_municipio(zona)
        if mres["ok"] and mres["nom_mun"]:
            return {"encontrado": False, "motivo": f"'{zona}' es un municipio, no una colonia: usa recomendar_zonas(giro, municipio)",
                    "fuentes": [F_ZMVM]}
        sug = difflib.get_close_matches(n, sorted(set(col)), n=3, cutoff=0.75)
        return {"encontrado": False, "motivo": f"{NO}: colonia '{zona}' no esta en agebs_features",
                "sugerencias": sug, "fuentes": [F_DENUE]}
    # primero las que empiezan con el texto (p. ej. «del valle» -> DEL VALLE CENTRO antes que FUENTES DEL VALLE)
    hit = hit.assign(_ini=~hit["nom_colonia"].map(norm).str.startswith(n)).sort_values(
        ["_ini", "pob_total"], ascending=[True, False]).drop(columns="_ini")
    grupos = hit.groupby(["nom_colonia", "nom_mun"], sort=False)
    out = {"encontrado": True, "agebs_que_coinciden": int(len(hit)), "colonias": []}
    for (c, m), h in list(grupos)[:3]:
        out["colonias"].append({"colonia": c, "municipio": m, "agebs": h["cvegeo"].head(8).tolist(),
                                "poblacion_2020_suma": _r(h["pob_total"].sum())})
    out["ficha_ageb_mas_poblada"] = _ficha(hit.iloc[0], clave)
    out["fuentes"] = out["ficha_ageb_mas_poblada"]["fuentes"]
    return out


# ---------------------------------------------------------------- buscar_carpetas
def buscar_carpetas(pregunta: str, k: int = 4, max_chars: int = 700) -> dict:
    """Trozos de carpetas/ (metodologia, municipios, teoria, modelo) mas parecidos a la pregunta."""
    res = rag.buscar(pregunta, k=max(1, min(int(k or 4), 8)))
    trozos = [{"archivo": f"carpetas/{r['archivo']}", "seccion": r["seccion"], "score": _r(r["score"], 3),
               "texto": r["texto"][:max_chars]} for r in res]
    return {"encontrado": bool(trozos), "modo": res[0]["modo"] if res else None, "trozos": trozos,
            "fuentes": sorted({t["archivo"] for t in trozos})}


# ---------------------------------------------------------------- contexto_macro
def contexto_macro() -> dict:
    """Ultimos indicadores macro (Banxico e INEGI) con fecha y serie."""
    m = json.loads((PROC / "macro.json").read_text(encoding="utf-8"))
    out, fuentes = {}, set()
    for k, v in m.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        if v.get("estado") == NO or "valor" not in v:
            item = {"valor": NO, "detalle": v.get("detalle", "")[:200]}
            prox = {}
            for pk, pv in (v.get("proxies") or {}).items():
                prox[pk] = {"valor": _r(pv["valor"], 2), "unidad": pv.get("unidad"), "fecha": pv.get("fecha"),
                            "id_serie": pv.get("id_serie")}
                fuentes.add(pv.get("fuente", "").split(";")[0])
            if prox:
                item["proxies"] = prox
            out[k] = item
            continue
        item = {"valor": _r(v["valor"], 2), "unidad": v.get("unidad"), "fecha": v.get("fecha"), "id_serie": v.get("id_serie")}
        for extra in ("variacion_anual_pct", "acumulado_12_meses_millones_usd"):
            if extra in v:
                item[extra] = _r(v[extra], 2 if "pct" in extra else 0)
        out[k] = item
        fuentes.add(v.get("fuente", "").split(";")[0])
    if "remesas" in out:
        out["remesas"]["valor"] = _r(m["remesas"]["valor"], 0)
    return {"indicadores": out, "consultado": m.get("_meta", {}).get("generado"),
            "nota": "valores nacionales, no por colonia; INPC de alimentos NO ENCONTRADO (solo proxies)",
            "fuentes": sorted(f for f in fuentes if f)}


# ---------------------------------------------------------------- sugerir_giros (extra)
@lru_cache(maxsize=1)
def _scores_todos() -> pd.DataFrame:
    p = RAIZ / "models" / "scores_giros.parquet"
    d = pd.read_parquet(p, columns=["cvegeo", "giro", "score", "nse", "prob_apertura", "prob_sobrevive"])
    d["cvegeo_mun"] = d["cvegeo"].str[:5]
    return d


def _auc_sobrevive():
    try:
        return _r(motor.cargar_modelo()[2]["sobrevivencia"]["auc_oof"], 2)
    except Exception:  # sin metadata
        return NO


def sugerir_giros(municipio: str | None = None, nse: str | None = None, ticket_max: float | None = None,
                  top: int = 5) -> dict:
    """Giros del catalogo que conviene considerar en una zona (sin giro definido).

    El score de cada giro es percentil DENTRO del giro, asi que no sirve para compararlos (una libreria puede
    tener score 90 con 5 % de probabilidad de apertura). Aqui los giros se ordenan por una medida absoluta y
    comparable: en las 10 mejores AGEB del giro dentro del filtro, prob. de apertura x prob. de seguir abierto
    (las dos del modelo, misma ventana 2020-2026 y misma unidad, la AGEB)."""
    mres = resolver_municipio(municipio)
    if not mres["ok"]:
        return {"encontrado": False, **{k: v for k, v in mres.items() if k != "ok"}, "fuentes": [F_ZMVM]}
    d = _scores_todos()
    filtros = {}
    if mres["cvegeo_mun"]:
        d = d[d["cvegeo_mun"] == mres["cvegeo_mun"]]
        filtros["municipio"] = mres["nom_mun"]
    n = norm(nse) if nse else None
    if n:
        if n not in ("bajo", "medio", "alto"):
            return {"encontrado": False, "motivo": "nse debe ser bajo, medio o alto", "fuentes": []}
        d = d[d["nse"] == n]
        filtros["nse"] = n
    if ticket_max:
        filtros["ticket_max_mxn"] = _r(ticket_max)
    m = _metricas()
    filas = []
    for clave, g in motor.giros().items():
        t = g.get("ticket_promedio_mxn")
        if ticket_max and (t is None or t > ticket_max):
            continue
        if n and g.get("nse_objetivo", {}).get(n, 0) < 0.3:
            continue
        if clave in m.index and m.at[clave, "agebs_con_apertura"] < 30:  # giros raros: el modelo no es confiable
            continue
        s = d[d["giro"] == clave].nlargest(10, "score")
        if not len(s):
            continue
        pa, ps = float(s["prob_apertura"].mean()), float(s["prob_sobrevive"].mean())
        fila = {"giro": clave, "viabilidad_pct": _r(100 * pa * ps), "prob_apertura_pct": _r(100 * pa),
                "prob_sigue_abierto_pct": _r(100 * ps), "score_relativo_medio_top10": _r(s["score"].mean(), 1),
                "ticket_promedio_mxn": t, "peso_nse_objetivo": g.get("nse_objetivo", {}).get(n) if n else None}
        if pa < PROB_BAJA:
            fila["aviso"] = "probabilidad de apertura baja: pocos negocios de este giro abren aqui"
        filas.append(fila)
    filas = sorted(filas, key=lambda r: -r["viabilidad_pct"])[:max(1, min(int(top or 5), 10))]
    if not filas:
        return {"encontrado": False, "filtros": filtros, "motivo": f"{NO}: ningun giro cumple los filtros", "fuentes": [F_GIROS]}
    return {"encontrado": True, "filtros": filtros or None, "giros": filas,
            "como_leer": ("los giros se ordenan por viabilidad = prob. de apertura x prob. de seguir abierto (absolutas, "
                          "comparables entre giros). El score 0-100 es relativo dentro de cada giro: NO compara giros"),
            "metodo": ("en las 10 AGEB con mejor score de cada giro dentro del filtro: media de la prob. de apertura "
                       "(aparece >= 1 negocio del giro 2020-2026) y de la prob. de que un local nuevo siga abierto; "
                       "con nse se exige peso >= 0.3 en nse_objetivo; se excluyen giros con menos de 30 AGEB con "
                       "aperturas (coworking, renta de bicicletas); ticket es supuesto; la prob. de seguir abierto "
                       f"viene de un modelo debil (AUC {_auc_sobrevive()})"),
            "fuentes": [F_MODELO, F_GIROS, F_DENUE]}


# ---------------------------------------------------------------- registro para el agente
HERRAMIENTAS = {"perfil_giro": perfil_giro, "recomendar_zonas": recomendar_zonas, "ficha_zona": ficha_zona,
                "buscar_carpetas": buscar_carpetas, "contexto_macro": contexto_macro, "sugerir_giros": sugerir_giros}


def ejecutar(nombre: str, argumentos: dict | None) -> dict:
    """Llama una herramienta por nombre; los errores regresan como dict (el LLM los lee)."""
    fn = HERRAMIENTAS.get(nombre)
    if fn is None:
        return {"error": f"herramienta '{nombre}' no existe", "disponibles": list(HERRAMIENTAS)}
    args = {k: v for k, v in (argumentos or {}).items() if v not in (None, "", "null")}
    try:
        return fn(**args)
    except TypeError as e:
        return {"error": f"argumentos invalidos para {nombre}: {e}"}
    except Exception as e:  # que el agente siga y lo diga
        return {"error": f"{type(e).__name__}: {e}"}
