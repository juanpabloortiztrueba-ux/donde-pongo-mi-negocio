"""Colonias y asentamientos de la ZMVM: de un texto libre a las AGEB que cubre.

    resolver("Polanco")            -> {ok, colonias, agebs, centro, municipio, criterio, ambigua, alternativas}
    detectar("una neveria en la Condesa")  -> [{texto, encontrada, resolucion|motivo, origen}]

Fuentes del indice (todo normalizado: minusculas, sin acentos ni signos):
  * `nom_colonia` de agebs_features (el asentamiento mas frecuente del DENUE dentro de cada AGEB);
  * `nom_asent` del DENUE actual, para asentamientos que no son el principal de ninguna AGEB
    (p. ej. Interlomas); se asignan a las AGEB donde tienen >= 3 establecimientos.
Mas una lista corta de alias conocidos (Polanco, la Condesa, la Roma, Santa Fe, Del Valle...) que apunta a
varias secciones o a nombres que el DENUE escribe distinto.

La deteccion en una pregunta pide una pista de lugar («en», «por», «cerca de», «colonia»...) antes del nombre,
para que «una cafeteria moderna» no cuente como la colonia Moderna. Nunca decide en silencio: si la colonia no
existe o es ambigua, el resultado lo dice (lo usa recomendar_zonas para avisar y para decir que dio a cambio).
Un nombre inventado que EMPIEZA con uno real («Villa Esmeralda del Bosque Azul») se resuelve con `criterio='parcial'` y
`parcial=True` (resolver) y la deteccion trae `parcial` y `texto_pedido`: el aviso dice NO ENCONTRADO y cual se uso.
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from app import motor, rag

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"

MIN_ESTAB_DENUE = 3  # establecimientos de un asentamiento del DENUE para asignarlo a una AGEB


def norm(s) -> str:
    """minusculas, sin acentos ni signos."""
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s.lower())).strip()


# alias: frases que dice la gente -> patrones (regex sobre el nombre normalizado) y municipios (cvegeo_mun).
# Los municipios evitan confundir «Santa Fe» o «Satelite» con homonimos de otros lados.
ALIAS = [
    {"frases": ["polanco"], "patrones": [r"^polanco\b"], "muns": ["09016"]},
    {"frases": ["condesa", "la condesa", "hipodromo condesa", "hipodromo"],
     "patrones": [r"^condesa$", r"^hipodromo condesa$", r"^hipodromo$"], "muns": ["09015"]},
    {"frases": ["roma", "la roma", "roma norte", "roma sur"], "patrones": [r"^roma norte$", r"^roma sur$"],
     "muns": ["09015"], "por_frase": {"roma norte": [r"^roma norte$"], "roma sur": [r"^roma sur$"]}},
    {"frases": ["santa fe"], "patrones": [r"^santa fe\b"], "muns": ["09010", "09004"]},
    {"frases": ["del valle", "colonia del valle"], "patrones": [r"^del valle\b"], "muns": ["09014"]},
    {"frases": ["narvarte", "la narvarte"], "patrones": [r"\bnarvarte\b"], "muns": ["09014"]},
    {"frases": ["doctores", "los doctores"], "patrones": [r"^doctores$"], "muns": ["09015"]},
    {"frases": ["juarez", "colonia juarez", "zona rosa"], "patrones": [r"^juarez$", r"^zona rosa$", r"^juarez zona rosa$"],
     "muns": ["09015"]},
    {"frases": ["centro", "centro historico", "el zocalo", "zocalo", "centro de la ciudad"],
     "patrones": [r"^centro$", r"^centro historico$"], "muns": ["09015"], "requiere_pista": True},
    {"frases": ["satelite", "ciudad satelite"], "patrones": [r"satelite"], "muns": ["15057"]},
    {"frases": ["lindavista"], "patrones": [r"^lindavista"], "muns": ["09005"]},
    {"frases": ["tlatelolco"], "patrones": [r"tlatelolco"], "muns": ["09015"]},
    {"frases": ["anzures", "nueva anzures"], "patrones": [r"anzures"], "muns": ["09016"]},
    {"frases": ["lomas de chapultepec", "las lomas"], "patrones": [r"^lomas de chapultepec"], "muns": ["09016"]},
    {"frases": ["pedregal", "jardines del pedregal"], "patrones": [r"^jardines del pedregal"], "muns": ["09010"]},
    {"frases": ["coapa"], "patrones": [r"\bcoapa\b"], "muns": ["09012", "09003"]},
    {"frases": ["interlomas"], "patrones": [r"interlomas"], "muns": ["15037"]},
    {"frases": ["escandon"], "patrones": [r"^escandon"], "muns": ["09016"]},
    {"frases": ["santa maria la ribera", "la ribera"], "patrones": [r"^santa maria la ribera$"], "muns": ["09015"]},
    {"frases": ["san angel"], "patrones": [r"^san angel$"], "muns": ["09010"]},
    {"frases": ["napoles"], "patrones": [r"napoles"], "muns": ["09014"]},
    {"frases": ["portales"], "patrones": [r"^portales"], "muns": ["09014"]},
    {"frases": ["mixcoac"], "patrones": [r"mixcoac"], "muns": ["09014"]},
]

# palabras que pueden ir entre la pista de lugar y el nombre («en LA Condesa», «en la COLONIA Roma»)
RELLENO = {"el", "la", "los", "las", "de", "del", "colonia", "col", "zona", "barrio", "fraccionamiento", "fracc",
           "unidad", "habitacional", "rumbo", "a"}
MARCAS_EXPLICITAS = {"colonia", "col", "fraccionamiento", "fracc", "barrio", "habitacional"}
PISTAS = {"en", "por", "cerca", "rumbo", "alrededor", "junto", "lado", "sobre", "dentro", "hacia", "zona", "colonia",
          "col", "barrio", "fraccionamiento", "fracc", "habitacional", "para", "ubicado", "ubicada"}
PREGUNTA = {"y", "que", "tal", "si", "mejor", "ahora", "entonces", "pero", "tambien", "oye", "hola", "en", "la", "el", "los", "las",
            "colonia", "col", "zona", "de", "del"}
# palabras sueltas demasiado genericas para expandir por prefijo («lomas» -> 400 colonias)
GENERICAS = {"norte", "sur", "oriente", "poniente", "industrial", "residencial", "popular", "nueva", "nuevo", "vieja",
             "central", "jardin", "jardines", "bosques", "bosque", "lomas", "loma", "villa", "villas", "santa", "san",
             "valle", "barrio", "pueblo", "ciudad", "unidad", "colonia", "ampliacion", "fraccionamiento", "centro",
             "moderna", "progreso", "mexico", "zona", "pensil", "isidro"}
NO_ES_COLONIA = {"mexico", "ciudad de mexico", "cdmx", "estado de mexico", "edomex", "zmvm", "valle de mexico",
                 "zona metropolitana", "area metropolitana", "df", "distrito federal", "la ciudad", "la zona"}
PREFIJOS_DENUE = re.compile(r"^(?:colonia|col|fracc|fraccionamiento|u hab|unidad habitacional|barrio|pueblo|pblo)\s+")


# ---------------------------------------------------------------- indice
@lru_cache(maxsize=1)
def _indice() -> dict:
    """nombre normalizado -> {cvegeo_mun: {"display": Counter, "agebs": set}} y datos de ayuda."""
    f = motor.cargar_features()
    ent: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"display": defaultdict(int), "agebs": set()}))
    for cve, nom in zip(f.index, f["nom_colonia"]):
        if not isinstance(nom, str) or not nom.strip():
            continue
        e = ent[norm(nom)][cve[:5]]
        e["display"][nom.strip()] += 1
        e["agebs"].add(cve)
    # asentamientos del DENUE que ninguna AGEB tiene como principal
    d = pd.read_parquet(PROC / "denue_actual.parquet", columns=["nom_asent", "cvegeo_mun", "cvegeo"])
    d = d.dropna()
    d["n"] = d["nom_asent"].map(lambda s: PREFIJOS_DENUE.sub("", norm(s)))
    g = d.groupby(["n", "cvegeo_mun", "cvegeo"]).size()
    g = g[g >= MIN_ESTAB_DENUE]
    idx = set(f.index)
    for (n, mun, cve), _ in g.items():
        if len(n) < 4 or cve not in idx or mun in ent.get(n, {}):
            continue
        e = ent[n][mun]
        e["display"][n.upper()] += 1
        e["agebs"].add(cve)
    prefijos: dict[str, set] = defaultdict(set)
    for n in ent:
        w = n.split()
        for k in range(1, len(w)):
            prefijos[" ".join(w[:k])].add(n)
    return {"ent": ent, "prefijos": prefijos, "claves": sorted(ent)}


@lru_cache(maxsize=1)
def _nom_mun() -> dict[str, str]:
    mun = pd.read_csv(PROC / "zmvm_municipios.csv", dtype=str)
    return dict(zip(mun["cvegeo_mun"], mun["nom_mun"]))


def _union(nombres: list[str], muns: set[str] | None) -> dict[str, dict]:
    """{cvegeo_mun: {"nombres": set(display), "agebs": set}} de los nombres normalizados dados."""
    ix = _indice()["ent"]
    out: dict[str, dict] = {}
    for n in nombres:
        for mun, e in ix.get(n, {}).items():
            if muns is not None and mun not in muns:
                continue
            o = out.setdefault(mun, {"nombres": set(), "agebs": set()})
            o["nombres"] |= set(e["display"])
            o["agebs"] |= e["agebs"]
    return out


def _alias_de(n: str) -> dict | None:
    for a in ALIAS:
        if n in a["frases"]:
            return a
    return None


def _sugerir(n: str, cve_mun: str | None = None, max_n: int = 4) -> list[str]:
    """Nombres parecidos a `n` («Polanquito Norte» -> Polanco): parecido de la frase completa y de cada palabra
    contra los nombres del indice y los alias. Texto listo para mostrar: «Nombre (Municipio)»."""
    ix = _indice()
    cand: list[str] = []
    for s in difflib.get_close_matches(n, ix["claves"], n=max_n, cutoff=0.7):
        cand.append(s)
    vocab = {fr: fr for a in ALIAS for fr in a["frases"]}
    for pal in n.split():
        if len(pal) < 5 or pal in GENERICAS or pal in RELLENO:
            continue
        for s in difflib.get_close_matches(pal, list(vocab), n=2, cutoff=0.68):
            cand.append(vocab[s])
        for s in difflib.get_close_matches(pal, [k for k in ix["claves"] if len(k.split()) == 1], n=2, cutoff=0.78):
            cand.append(s)
    out = []
    for s in dict.fromkeys(cand):
        if s == n:
            continue
        if s in ix["ent"]:
            muns = [m for m in ix["ent"][s] if cve_mun is None or m == cve_mun] or list(ix["ent"][s])
            mejor = max(muns, key=lambda m: len(ix["ent"][s][m]["agebs"]))
            out.append(f"{sorted(ix['ent'][s][mejor]['display'], key=len)[0].title()} ({_nom_mun().get(mejor, mejor)})")
        else:  # alias («polanco»)
            a = _alias_de(s)
            mun = _nom_mun().get(a["muns"][0], "") if a else ""
            out.append(f"{s.title()} ({mun})" if mun else s.title())
    return list(dict.fromkeys(out))[:max_n]


def _limpia_frase(texto: str) -> str:
    """Quita «la colonia», «el», «zona»... del inicio, salvo que el texto completo sea un nombre conocido."""
    n = norm(texto)
    if _alias_de(n):
        return n
    sin = n
    while True:
        m = re.match(r"^(?:la colonia|colonia|col|el|la|los|las|zona|barrio|fraccionamiento|fracc)\s+(.+)$", sin)
        if not m:
            break
        sin = m.group(1)
    ent = _indice()["ent"]
    if n in ent and sin not in ent and not _alias_de(sin):
        return n
    return sin


# ---------------------------------------------------------------- resolver
def resolver(texto: str, cve_mun: str | None = None) -> dict:
    """Texto de colonia -> AGEB y centroide. Nunca inventa: si no hay, dice NO ENCONTRADO y sugiere.

    cve_mun: restringe a un municipio (cvegeo de 5 digitos). Si el nombre existe en varios municipios y no se
    restringe, `ambigua` es True: se elige el de mas poblacion y `alternativas` lista los demas."""
    n = _limpia_frase(texto)
    if not n:
        return {"ok": False, "consulta": texto, "motivo": "NO ENCONTRADO: texto vacio", "sugerencias": []}
    ix = _indice()
    restringe = {cve_mun} if cve_mun else None
    criterio, hallados = None, {}
    alias = _alias_de(n)
    if alias:
        pats = (alias.get("por_frase") or {}).get(n, alias["patrones"])
        nombres = [k for k in ix["claves"] if any(re.search(p, k) for p in pats)]
        muns = set(alias["muns"]) & restringe if restringe else set(alias["muns"])
        hallados, criterio = _union(nombres, muns), "alias"
    if not hallados and n in ix["ent"]:
        hallados, criterio = _union([n], restringe), "exacto"
        # nombre exacto + sus secciones («Del Valle» -> Del Valle Centro/Norte/Sur) solo si no esta ya completo
    if not hallados:
        pref = ix["prefijos"].get(n)
        if pref and (len(n.split()) >= 2 or (n not in GENERICAS and len(n) >= 5)):
            hallados, criterio = _union(sorted(pref), restringe), "prefijo"
    if not hallados:
        # nombre escrito con una palabra extra o con otro orden: todas las palabras del texto estan en el nombre
        pal = [p for p in n.split() if len(p) >= 4 and p not in GENERICAS]
        if pal and len(n.split()) >= 2:
            nombres = [k for k in ix["claves"] if all(re.search(rf"\b{re.escape(p)}\b", k) for p in pal)]
            if 0 < len(nombres) <= 12:
                hallados, criterio = _union(nombres, restringe), "contiene"
    if not hallados and len(n) >= 6:
        cerca = difflib.get_close_matches(n, ix["claves"], n=3, cutoff=0.84)
        if cerca:
            hallados, criterio = _union(cerca[:1], restringe), "aproximado"
    if not hallados:
        # nombre inventado que EMPIEZA con uno que si existe («Villa Esmeralda del Bosque Azul»): nunca se resuelve en
        # silencio; se usa el nombre real mas parecido pero el resultado dice que lo pedido no existe (parcial=True)
        pal = n.split()
        for k in range(len(pal) - 1, 0, -1):
            pref_n = " ".join(pal[:k])
            ok_nombre = (pref_n in ix["ent"] or _alias_de(pref_n) is not None) and (
                k >= 2 or (pref_n not in GENERICAS and len(pref_n) >= 6))
            if ok_nombre:
                r0 = resolver(pref_n, cve_mun)
                if r0["ok"]:
                    return {**r0, "consulta": texto, "criterio": "parcial", "parcial": True, "usada": pref_n,
                            "pedido": re.sub(r"\s+", " ", texto.strip())}
                break
        sug_txt = _sugerir(n, cve_mun)
        donde = f" en {_nom_mun().get(cve_mun, cve_mun)}" if cve_mun else " en la ZMVM"
        return {"ok": False, "consulta": texto,
                "motivo": f"NO ENCONTRADO: '{texto}' no aparece como colonia o asentamiento{donde} (agebs_features ni DENUE 05/2026)",
                "sugerencias": sug_txt}
    f = motor.cargar_features()
    pob = {m: float(f.loc[sorted(v["agebs"]), "pob_total"].sum()) for m, v in hallados.items()}
    orden = sorted(hallados, key=lambda m: -pob[m])
    # alias con varios municipios (Santa Fe: Alvaro Obregon y Cuajimalpa) = una sola zona; lo demas, ambiguo
    unir = criterio == "alias" and len(orden) > 1
    ambigua = len(orden) > 1 and not unir
    elegidos = orden if unir else orden[:1]
    agebs = sorted({a for m in elegidos for a in hallados[m]["agebs"]})
    colonias = sorted({c for m in elegidos for c in hallados[m]["nombres"]})
    sub = f.loc[agebs]
    out = {"ok": True, "consulta": texto, "criterio": criterio, "ambigua": ambigua,
           "cvegeo_mun": elegidos[0] if len(elegidos) == 1 else None,
           "municipio": ", ".join(_nom_mun().get(m, m) for m in elegidos),
           "colonias": colonias[:12], "n_colonias": len(colonias), "agebs": agebs,
           "poblacion_2020": int(sub["pob_total"].sum()),
           "centro": {"lat": round(float(sub["lat"].mean()), 5), "lon": round(float(sub["lon"].mean()), 5)}}
    if ambigua:
        out["alternativas"] = [{"municipio": _nom_mun().get(m, m), "cvegeo_mun": m, "agebs": len(hallados[m]["agebs"]),
                                "poblacion_2020": int(pob[m]),
                                "colonias": sorted(hallados[m]["nombres"])[:4]} for m in orden[1:6]]
    return out


def buscar(texto: str, n: int = 8) -> list[dict]:
    """Colonias cuyo nombre empieza con (o contiene) el texto, para autocompletar: [{colonia, municipio, cvegeo_mun, agebs}],
    las de mas AGEB primero. Solo nombres de agebs_features (los asentamientos extra del DENUE no se listan)."""
    q = norm(texto)
    if len(q) < 2:
        return []
    f = motor.cargar_features()
    nom = f["nom_colonia"].fillna("")
    nn = nom.map(norm)
    m = nn.str.startswith(q) | nn.str.contains(rf"\b{re.escape(q)}", regex=True)
    g = f[m].assign(_n=nn[m], _ini=nn[m].str.startswith(q)).groupby(["nom_colonia", "nom_mun"], sort=False).agg(
        cvegeo_mun=("cve_mun", "first"), cve_ent=("cve_ent", "first"), agebs=("cvegeo", "size"), _ini=("_ini", "max"))
    g = g.reset_index().sort_values(["_ini", "agebs"], ascending=[False, False]).head(n)
    return [{"colonia": r["nom_colonia"], "municipio": r["nom_mun"], "cvegeo_mun": f"{r['cve_ent']}{r['cvegeo_mun']}", "agebs": int(r["agebs"])}
            for _, r in g.iterrows()]


def distancias_km(centro: dict) -> pd.Series:
    """Distancia en km de cada AGEB al punto (lat, lon), en metros EPSG:6372 / 1000. Indice = cvegeo."""
    xy = motor.agebs_xy()
    cx, cy = motor.a_metros([centro["lon"]], [centro["lat"]])
    return pd.Series(np.hypot(xy["x"].to_numpy() - cx[0], xy["y"].to_numpy() - cy[0]) / 1000.0, index=xy.index)


# ---------------------------------------------------------------- deteccion en una pregunta
def _enmascara(tokens: list[str], frases: list[str]) -> list[str]:
    """Reemplaza por '#' las apariciones de cada frase (palabras completas)."""
    t = list(tokens)
    for fr in sorted({x for x in frases if x}, key=lambda x: -len(x.split())):
        w = fr.split()
        for i in range(len(t) - len(w) + 1):
            if t[i:i + len(w)] == w:
                t[i:i + len(w)] = ["#"] * len(w)
    return t


def _cue(tokens: list[str], i: int) -> tuple[bool, bool]:
    """(hay pista de lugar antes de la posicion i, la pista es explicita: colonia/barrio/fraccionamiento)."""
    j, explicita = i - 1, False
    while j >= 0 and tokens[j] in RELLENO:
        explicita = explicita or tokens[j] in MARCAS_EXPLICITAS
        j -= 1
    if j >= 0 and tokens[j] in PISTAS:
        return True, explicita or tokens[j] in MARCAS_EXPLICITAS
    if explicita:
        return True, True
    if j < 0 or all(t in PREGUNTA or t == "#" for t in tokens[:j + 1]):  # «Polanco», «¿y la Condesa?»
        return True, False
    return False, False


MAYUS = re.compile(r"\b(?:en|por|cerca de|cerca del|rumbo a|rumbo de|zona de|colonia|col\.?|fraccionamiento|barrio de|barrio)\s+"
                   r"(?:la |el |los |las )?"
                   r"((?:[A-ZÁÉÍÓÚÑ][\wáéíóúñ.]*)(?:\s+(?:(?:de|del|la|las|los|y)\s+)?[A-ZÁÉÍÓÚÑ0-9][\wáéíóúñ.]*){0,4})")


def detectar(pregunta: str, municipios: list[str] | None = None, giro_frase: str | None = None,
             cve_mun: str | None = None) -> list[dict]:
    """Colonias o asentamientos que nombra la pregunta, en el orden en que aparecen.

    municipios: nombres de municipios ya detectados (se ignoran como colonia); giro_frase: la frase del giro.
    cve_mun: si la pregunta fija un municipio, la colonia se busca solo ahi.
    Cada elemento: {texto, encontrada, origen ('nombre'|'alias'|'explicita'|'mayuscula'), resolucion | motivo}."""
    n = norm(pregunta)
    if not n:
        return []
    tokens = n.split()
    ignorar = [norm(m) for m in (municipios or [])] + [giro_frase or ""] + [c for c in rag.CIUDADES_FUERA if c in n]
    ignorar += [a for a in rag._municipios() if f" {a} " in f" {n} "]  # frases de municipio tal como las escribio la persona
    ignorar += [x for x in NO_ES_COLONIA if f" {x} " in f" {n} "]
    ix = _indice()
    toks = _enmascara(tokens, ignorar)
    out, usados = [], set()
    L = len(toks)
    # colonias cuyo nombre contiene un municipio («Villa Coyoacan»): se buscan antes, con el nombre completo
    for k in range(min(6, L), 1, -1):
        for i in range(0, L - k + 1):
            frase = " ".join(tokens[i:i + k])
            if "#" not in toks[i:i + k] or all(t == "#" for t in toks[i:i + k]) or any(j in usados for j in range(i, i + k)) or frase not in ix["ent"]:
                continue
            if not _cue(toks, i)[0]:
                continue
            res = resolver(frase, cve_mun)
            if res["ok"]:
                out.append({"texto": " ".join(pregunta_palabras(pregunta, tokens, i, k)), "frase": frase, "encontrada": True,
                            "origen": "nombre", "resolucion": res, "pos": i})
                usados.update(range(i, i + k))
    for k in range(min(7, L), 0, -1):
        # con el mismo largo, primero la frase que es un nombre exacto del catalogo («Roma Sur») y despues el alias
        # amplio («la Roma»), para no perder lo que la persona pidio con precision
        for i in sorted(range(0, L - k + 1), key=lambda i: (0 if " ".join(toks[i:i + k]) in ix["ent"] else 1, i)):
            if any(j in usados for j in range(i, i + k)) or "#" in toks[i:i + k]:
                continue
            frase = " ".join(toks[i:i + k])
            if frase in NO_ES_COLONIA or all(t in RELLENO or t in PREGUNTA for t in toks[i:i + k]):
                continue
            alias = _alias_de(frase)
            conocido = frase in ix["ent"] or (alias is not None)
            if not conocido:
                pref = ix["prefijos"].get(frase)
                conocido = bool(pref) and (k >= 2 or (frase not in GENERICAS and len(frase) >= 6))
            if not conocido:
                continue
            hay_pista, explicita = _cue(toks, i)
            if not hay_pista and not (alias and not alias.get("requiere_pista")):
                continue
            res = resolver(frase, cve_mun)
            if not res["ok"]:
                continue
            out.append({"texto": " ".join(pregunta_palabras(pregunta, tokens, i, k)), "frase": frase, "encontrada": True,
                        "origen": "alias" if alias else ("explicita" if explicita else "nombre"), "resolucion": res, "pos": i})
            usados.update(range(i, i + k))
    # nombres explicitos o con mayuscula que NO existen: nunca se ignoran en silencio
    for m in MAYUS.finditer(pregunta):
        cand = m.group(1).strip(" .,")
        nc = norm(cand)
        if not nc or nc in NO_ES_COLONIA or rag.municipios_en(cand) or rag.ciudades_fuera(cand):
            continue
        if giro_frase and giro_frase in nc.split() or any(norm(x) == nc for x in (municipios or [])):
            continue
        if any(o["frase"] == nc or nc in o["frase"] for o in out):
            continue
        # el candidato EMPIEZA con una colonia ya resuelta y trae mas palabras («Villa Esmeralda del Bosque Azul»):
        # se conserva lo que pidio la persona; resolver() lo marca como parcial y el aviso dice que NO se encontro
        corto = next((o for o in out if nc.startswith(o["frase"] + " ")
                      and not nc[len(o["frase"]) + 1:].startswith("y ")
                      and not any(o2 is not o and o2["frase"] in nc[len(o["frase"]):] for o2 in out)), None)
        if corto is not None:
            if nc not in ix["ent"] and not ix["prefijos"].get(nc) and not _alias_de(nc):
                res = resolver(cand, cve_mun)
                nuevo = {"texto": cand, "frase": nc, "origen": corto["origen"], "pos": corto["pos"], "texto_pedido": cand,
                         "parcial": bool(res.get("parcial"))}
                if res["ok"]:
                    nuevo.update(encontrada=True, resolucion=res)
                else:
                    nuevo.update(encontrada=False, motivo=res["motivo"], sugerencias=res.get("sugerencias", []))
                out[out.index(corto)] = nuevo
            continue
        if any(o["frase"] in nc for o in out):
            continue
        if nc in ix["ent"] or ix["prefijos"].get(nc) or _alias_de(nc):
            continue  # existe pero sin pista (ya se resolvio arriba) o se descarto por generica
        explicito = bool(re.search(r"\b(?:colonia|col\.?|fraccionamiento|barrio)\s+(?:la |el |los |las )?" + re.escape(cand), pregunta, re.I))
        res = resolver(cand, cve_mun)
        if res["ok"]:
            out.append({"texto": cand, "frase": nc, "encontrada": True, "origen": "mayuscula", "resolucion": res, "pos": m.start()})
        else:
            out.append({"texto": cand, "frase": nc, "encontrada": False, "origen": "explicita" if explicito else "mayuscula",
                        "motivo": res["motivo"], "sugerencias": res.get("sugerencias", []), "pos": m.start()})
    out.sort(key=lambda o: o["pos"])
    return out


def pregunta_palabras(pregunta: str, tokens: list[str], i: int, k: int) -> list[str]:
    """Palabras originales (con mayusculas y acentos) que corresponden a tokens[i:i+k], si se pueden alinear."""
    crudas = re.findall(r"[\wÁÉÍÓÚÜÑáéíóúüñ]+", pregunta)
    if len(crudas) == len(tokens) and all(norm(c) == t for c, t in zip(crudas, tokens)):
        return crudas[i:i + k]
    return tokens[i:i + k]
