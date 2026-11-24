"""Revision de la «Lectura» que escribe el LLM: lo unico del texto final que no arma el codigo.

El modelo recibe `destacados` (la zona con mayor ingreso, mayor prob. de apertura, menor competencia...), pero a veces
pega bien las cifras y mal el superlativo («Fuentes de Aragon y Canteros tienen la mayor prob. de apertura» cuando la
mayor es Canteros y Fuentes de Aragon va cuarta), inventa una cifra («NSE medio en el 60 % de la poblacion») o le pone a
un giro la viabilidad de otro. Aqui se revisa cada frase contra los datos de TODAS las herramientas:

  * superlativo + magnitud (mayor, mas alto, lidera(n), destaca, mejor(es), menor...  con prob. de apertura, ingreso,
    gasto potencial, competidores, edad, score u «oportunidad»): las zonas nombradas tienen que ser las primeras de esa
    magnitud en el top. Sin magnitud escrita, se deduce de la cifra que sigue («lidera con un 12.5 %» = edad clave);
  * cifras: cada cifra tiene que salir de una herramienta (y con su tipo: un % solo es un %), y si la frase nombra una
    zona, de ESA zona; si nombra un giro de sugerir_giros, de ESE giro;
  * giros (sugerir_giros): el giro que «lidera» es el 1 de la lista, los giros se nombran en el orden de la herramienta,
    y a un giro no se le atribuyen cifras de zonas que se calcularon para otro giro;
  * con filtro de colonia: «En <colonia pedida>, la colonia Z» solo vale si Z esta dentro de la colonia.

`problemas(frase, Contexto)` es la regla (la usa tambien eval/evaluar.py); `depurar` quita las frases que fallan y, si no
queda nada, arma una lectura corta con `destacados`.
"""
from __future__ import annotations

import re
import unicodedata

from app import herramientas as H

# ---------------------------------------------------------------- numeros (los comparte eval/evaluar.py)
AGEB_RE = re.compile(r"\b\d{9}[0-9A-Z]{4}\b")
FECHA_RE = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b|\b\d{1,2}/\d{4}\b")
NUM_RE = re.compile(r"(?<![\w.,/])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\w])\s*(%|millones|millon|mdp|mil\b|m\b)?",
                    re.I)
_MULT = {"millones": 1e6, "millon": 1e6, "mdp": 1e6, "m": 1e6, "mil": 1e3}


def numeros_de(obj, acc: set | None = None) -> set:
    """Todos los numeros que regreso una herramienta (valores y numeros dentro de textos)."""
    acc = set() if acc is None else acc
    if isinstance(obj, bool) or obj is None:
        return acc
    if isinstance(obj, (int, float)):
        acc.add(float(obj))
    elif isinstance(obj, str):
        s = FECHA_RE.sub(" ", obj)
        for m in NUM_RE.finditer(s):
            acc.add(float(m.group(1).replace(",", "")))
    elif isinstance(obj, dict):
        for v in obj.values():
            numeros_de(v, acc)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            numeros_de(v, acc)
    return acc


def numeros_tipados(obj, acc: dict | None = None, clave: str = "", pct_ctx: bool = False) -> dict:
    """{'todos', 'pct', 'pesos'}: los numeros de las herramientas con su tipo. Un % es un campo `*_pct`, un valor con
    unidad «%», o un numero seguido de «%» dentro de un texto; los pesos, un campo `*_mxn` o un numero con «$»."""
    acc = {"todos": set(), "pct": set(), "pesos": set()} if acc is None else acc
    if isinstance(obj, bool) or obj is None:
        return acc
    k = str(clave).lower()
    if isinstance(obj, (int, float)):
        v = float(obj)
        acc["todos"].add(v)
        if pct_ctx or "pct" in k or "porcentaje" in k:
            acc["pct"].add(v)
        elif "mxn" in k or "pesos" in k:
            acc["pesos"].add(v)
    elif isinstance(obj, str):
        s = FECHA_RE.sub(" ", obj)
        for m in NUM_RE.finditer(s):
            v = float(m.group(1).replace(",", ""))
            u = (m.group(2) or "").lower()
            acc["todos"].add(v)
            if u == "%":
                acc["pct"].add(v)
            elif s[max(0, m.start(1) - 1):m.start(1)] == "$" or u in _MULT:
                acc["pesos"].add(v * _MULT.get(u, 1.0))
    elif isinstance(obj, dict):
        local = "%" in str(obj.get("unidad", ""))
        for kk, v in obj.items():
            numeros_tipados(v, acc, kk, local and kk in ("valor", "variacion_anual_pct"))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            numeros_tipados(v, acc, clave, pct_ctx)
    return acc


def cifras_citadas(texto: str, pregunta: str) -> list[dict]:
    """Cifras de la respuesta que hay que verificar (sin AGEB, fechas, enumeraciones ni numeros de la pregunta)."""
    s = AGEB_RE.sub(" ", texto)
    s = FECHA_RE.sub(" ", s)
    s = re.sub(r"/\s*100\b", " ", s)           # 'score 96.5/100'
    s = re.sub(r"(?m)^\s*\d+[.)]\s", " ", s)    # '1. ' de listas
    s = re.sub(r"\b(?:top|primer[oa]s?)\s+\d+\b", " ", s, flags=re.I)
    en_pregunta = {float(m.group(1).replace(",", "")) for m in NUM_RE.finditer(pregunta)}
    out = []
    for m in NUM_RE.finditer(s):
        txt = m.group(1)
        v = float(txt.replace(",", ""))
        dec = len(txt.split(".")[1]) if "." in txt else 0
        if dec == 0 and (v <= 10 or 1990 <= v <= 2030):   # enumeraciones, deciles y anios no se verifican
            continue
        if v in en_pregunta:
            continue
        u = (m.group(2) or "").lower()
        mult = 1e6 if u in ("millones", "millon", "mdp", "m") else 1e3 if u == "mil" else 1.0
        out.append({"texto": m.group(0).strip(), "valor": v * mult, "tol": 0.5 * 10 ** (-dec) * mult,
                    "crudo": v, "tol_crudo": 0.5 * 10 ** (-dec)})
    return out


def coincide(c: dict, nums: set) -> bool:
    """Coincide si la cifra (con su unidad aplicada, o tal cual: «5362 millones de USD» cuando la herramienta
    ya da millones) esta a medio digito de un numero de las herramientas (o de una fraccion escrita como %)."""
    pares = [(c["valor"], c["tol"]), (c.get("crudo", c["valor"]), c.get("tol_crudo", c["tol"]))]
    for n in nums:
        for cand in (n, n * 100):
            if any(abs(v - cand) <= tol + 1e-9 for v, tol in pares):
                return True
    return False


def _coincide_exacto(c: dict, nums: set) -> bool:
    """Como `coincide`, sin la lectura de fracciones como % (para los conjuntos que ya vienen tipados)."""
    pares = [(c["valor"], c["tol"]), (c.get("crudo", c["valor"]), c.get("tol_crudo", c["tol"]))]
    return any(abs(v - n) <= tol + 1e-9 for n in nums for v, tol in pares)


def _tipo_de_cifra(fr: str, pos: int, c: dict) -> str:
    """'pct' si lleva %, 'pesos' si lleva $ o millones/mil, 'num' en otro caso."""
    txt = c["texto"]
    if txt.rstrip().endswith("%") or re.match(r"\s*por ciento", fr[pos + len(txt):pos + len(txt) + 14], re.I):
        return "pct"
    if fr[max(0, pos - 1):pos] == "$" or re.search(r"millon|mdp|\bmil\b", txt, re.I):
        return "pesos"
    return "num"


# ---------------------------------------------------------------- magnitudes, superlativos y campos de la zona
# magnitud -> (campo de la zona, palabras que la nombran en la frase normalizada)
MAGNITUDES = (
    ("prob. de apertura", "prob_apertura_pct", re.compile(r"\bapertura\b|\bprobabilidad\b|\bprob\b")),
    ("gasto potencial", "gasto_potencial_trim_mxn", re.compile(r"\bgasto\b")),
    ("ingreso", "ingreso_trim_mediano_estimado_mxn", re.compile(r"\bingresos?\b")),
    ("competidores", "competidores_ponderados", re.compile(r"\bcompetidores\b|\bcompetencia\b|\bcompetidoras\b")),
    ("edad clave", "edad_clave_pct", re.compile(r"\bedad\b|\bedades\b|\b\d+ a \d+ anos\b|\b60 o mas\b|\bmenores de \d+|\bmayores de \d+|"
                                                r"\bninos\b|\bninas\b|\bjovenes\b|\badultos mayores\b|\bpoblacion infantil\b")),
    ("score", "score", re.compile(r"\bscore\b|\bpuntaje\b")),
)
# palabras que, con «mejor / lidera», hablan del score en general (la oportunidad, la mejor opcion)
GENERICO_FUERTE = re.compile(r"\bopcion(?:es)?\b|\boportunidad(?:es)?\b|(?<!gasto )\bpotencial\b|\blugar(?:es)?\b|\bubicacion(?:es)?\b|\bsitios?\b")
GENERICO_DEBIL = re.compile(r"\bcolonias?\b|\bzonas?\b|\bareas?\b")
CAMPOS_PCT = ("prob_apertura_pct", "edad_clave_pct", "captura_huff_pct", "prob_sigue_abierto_pct")
CAMPOS_PESOS = ("gasto_potencial_trim_mxn", "ingreso_trim_mediano_estimado_mxn")
CAMPOS_NUM = ("competidores_ponderados", "score", "decil_estimado", "dist_a_colonia_km")
# superlativos: (regex, direccion): +1 el mayor valor, -1 el menor. «menores de 14» y «adultos mayores» no son superlativos
_NO_EDAD = r"(?!\s+(?:de\s+)?\d)(?!\s+de\s+edad)"
SUPERLATIVOS = (
    (re.compile(rf"\b(?:menor(?:es)?{_NO_EDAD}|menos|mas baj[oa]s?|minim[oa]s?)\b"), -1),
    (re.compile(rf"(?<!adultos )(?<!personas )(?<!gente )\b(?:mayor(?:es)?{_NO_EDAD}|mas alt[oa]s?|maxim[oa]s?|lidera(?:n)?|liderea(?:n)?|"
                r"destaca(?:n)?|destacad[oa]s?|encabeza(?:n)?|sobresale(?:n)?|mejor(?:es)?)\b"), +1),
)
GENERICO_OK = re.compile(r"mejor|lider")        # con estas, «la oportunidad / la mejor opcion» se compara con el score
GENERICO_DEBIL_OK = re.compile(r"mejor")        # con esta, tambien «las mejores colonias / zonas»
ARTICULOS = {"de", "del", "la", "las", "los", "el", "y", "en"}
ANAFORA = re.compile(r"^\W*(?:por (?:otro|otra) (?:lado|parte)|ambos|ambas|ademas|además|tambien|también|asi|así|sin embargo|"
                     r"mientras|en cambio|esto|esta|estas|estos|esa|esas|esos|ese|dicho|por ello|por eso|por lo tanto)\b", re.I)
CIFRA_RE = re.compile(r"\$?\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(%|por ciento|millones|millon|mil\b)?")
# magnitudes de zona que no se pueden atribuir a un giro que no se calculo con recomendar_zonas
MAG_DE_ZONA = re.compile(r"\bgasto\b|\bingresos?\b|\bcompetidores\b|\bcompetencia\b|\bcaptura\b|\bedad clave\b|\bscore\b")


def ligera(s: str) -> str:
    """Minusculas sin acentos; todo lo que no es letra, numero, «. , % $» pasa a espacio. Misma longitud que el original
    (las posiciones valen para el texto original)."""
    out = []
    for ch in str(s):
        b = unicodedata.normalize("NFD", ch)[0].lower()
        out.append(b if b.isalnum() or b in ".,%$" else " ")
    return "".join(out)


def _tokens_nombre(colonia: str) -> list[str]:
    return [t for t in H.norm(colonia).split()]


def menciones(frase_norm: str, zonas: list[dict]) -> list[tuple[int, int, dict]]:
    """[(inicio, fin, zona)] de las zonas que nombra la frase (normalizada). Nombre completo, en singular o plural.
    Si un nombre esta dentro de otro mas largo que tambien aparece («Granada» en «Ampliacion Granada»), solo cuenta
    la coincidencia mas larga en ese tramo; el nombre corto cuenta si aparece tambien fuera de el."""
    spans: list[tuple[int, int, dict]] = []
    for z in zonas:
        toks = _tokens_nombre(z["colonia"])
        if not toks:
            continue
        rx = r"\b" + r"\s+".join(re.escape(t.rstrip("s") if len(t) > 3 else t) + ("s?" if len(t) > 3 else "") for t in toks) + r"\b"
        spans += [(m.start(), m.end(), z) for m in re.finditer(rx, frase_norm)]
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    out: list[tuple[int, int, dict]] = []
    for a, b, z in spans:
        if any(a2 <= a and b <= b2 and (a2, b2) != (a, b) and z is not z2 for a2, b2, z2 in spans):
            continue  # contenido en el tramo de otra zona mas larga
        if (a, b) in {(x, y) for x, y, _ in out}:
            continue
        out.append((a, b, z))
    return out


def _valor(z: dict, campo: str):
    v = z.get(campo)
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _cifras_en(trozo: str) -> list[dict]:
    """Cifras del trozo (texto ligero): [{valor, tol, tipo}]. Los rangos de edad («0 a 14 anos») no cuentan."""
    t = re.sub(r"\b\d{1,3}\s+(?:a|-)\s+\d{1,3}\s+anos\b|\b60\s+(?:o mas|\+)(?:\s+anos)?|\bmenores de \d+|\bmayores de \d+", " ", trozo)
    out = []
    for m in CIFRA_RE.finditer(t):
        txt = m.group(1)
        v = float(txt.replace(",", ""))
        dec = len(txt.split(".")[1]) if "." in txt else 0
        u = (m.group(2) or "").lower()
        mult = 1e6 if u in ("millones", "millon") else 1e3 if u == "mil" else 1.0
        tipo = "pct" if u in ("%", "por ciento") else "pesos" if (m.group(0).lstrip().startswith("$") or mult > 1) else "num"
        out.append({"valor": v * mult, "tol": max(0.5 * 10 ** (-dec) * mult, 600 if tipo == "pesos" else 0), "tipo": tipo})
    return out


def _campos_de_tipo(tipo: str) -> tuple[str, ...]:
    return {"pct": CAMPOS_PCT, "pesos": CAMPOS_PESOS}.get(tipo, CAMPOS_NUM + CAMPOS_PCT + CAMPOS_PESOS)


def _tipo_de_campo(campo: str) -> str:
    return "pct" if campo in CAMPOS_PCT else "pesos" if campo in CAMPOS_PESOS else "num"


def _pares_superlativo(fn: str) -> list[dict]:
    """Cada superlativo con la magnitud que nombra a continuacion (hasta 90 caracteres o hasta el siguiente superlativo):
    {pos, dir, palabra, nombre, campo, cifra}. `campo` es None si no hay magnitud escrita (se deduce de la cifra)."""
    pos = sorted((m.start(), d, m.group(0)) for rx, d in SUPERLATIVOS for m in rx.finditer(fn))
    out = []
    for i, (p, d, palabra) in enumerate(pos):
        fin = pos[i + 1][0] if i + 1 < len(pos) else len(fn)
        trozo = fn[p:min(fin, p + 90)]
        hall = [(m.start(), nombre, campo) for nombre, campo, rx in MAGNITUDES for m in [rx.search(trozo)] if m]
        if GENERICO_OK.match(palabra):
            hall += [(m.start(), "score", "score") for m in [GENERICO_FUERTE.search(trozo)] if m]
        cifras = _cifras_en(trozo)
        cifra = cifras[0] if cifras else None
        nombre = campo = None
        if hall:
            _, nombre, campo = min(hall)
        elif cifra is None:
            antes = fn[max(0, p - 50):p]
            previas = [(len(antes) - ms[-1].end(), nombre, campo) for nombre, campo, rx in MAGNITUDES
                       for ms in [list(rx.finditer(antes))] if ms]
            if previas:
                _, nombre, campo = min(previas)
            elif GENERICO_DEBIL_OK.match(palabra) and GENERICO_DEBIL.search(trozo):
                nombre, campo = "score", "score"
        if campo is None and cifra is None:
            continue
        out.append({"pos": p, "dir": d, "palabra": palabra, "nombre": nombre, "campo": campo, "cifra": cifra, "cifras": cifras})
    return out


def _viola(zs: list[dict], todas: list[dict], campo: str, d: int) -> list[str] | None:
    """Nombres de las zonas de `zs` que no estan entre las primeras de `todas` en `campo` (None si no se puede juzgar)."""
    vals = sorted((v for v in (_valor(z, campo) for z in todas) if v is not None), reverse=d > 0)
    mias = [_valor(z, campo) for z in zs]
    if not vals or any(v is None for v in mias) or len(zs) > len(vals):
        return None
    corte = vals[len(zs) - 1]
    return [z["colonia"] for z, v in zip(zs, mias) if ((v < corte) if d > 0 else (v > corte))]


def problemas_de_frase(frase: str, zonas: list[dict], filtros: dict | None = None) -> list[str]:
    """Motivos por los que la frase contradice a los datos de las zonas (lista vacia = la frase vale)."""
    fn = ligera(frase)
    ms = menciones(fn, zonas)
    problemas: list[str] = []
    pares = _pares_superlativo(fn)
    pos_todos = sorted(m.start() for rx, _ in SUPERLATIVOS for m in rx.finditer(fn))
    for par in pares:
        p, d = par["pos"], par["dir"]
        previo = max([x for x in pos_todos if x < p], default=-1)
        siguiente = min([x for x in pos_todos if x > p], default=len(fn) + 1)
        asignadas = [z for a, b, z in ms if previo < a <= p] or [z for a, b, z in ms if p < a < siguiente]
        asignadas = list({id(z): z for z in asignadas}.values())
        if not asignadas:
            continue
        et = "mayor" if d > 0 else "menor"
        if par["campo"]:
            campos = [(par["campo"], par["nombre"], None)]
            # la magnitud escrita es de otro tipo que una cifra («lidera con ingreso y 16.5 % de menores»): tambien se juzga esa cifra
            otras = [c for c in par["cifras"] if c["tipo"] != "num" and c["tipo"] != _tipo_de_campo(par["campo"])]
            campos += [(None, None, otras[0])] if otras else []
        else:
            campos = [(None, None, par["cifra"])]
        for campo, nombre, c in campos:
            if campo is None:                       # magnitud deducida de la cifra que sigue
                cands = [cp for cp in _campos_de_tipo(c["tipo"])
                         if all((v := _valor(z, cp)) is not None and abs(v - c["valor"]) <= c["tol"] + 1e-9 for z in asignadas[:1])]
                malos = [(cp, _viola(asignadas, zonas, cp, d)) for cp in cands]
                if malos and all(m for _, m in malos):
                    cp, m = malos[0]
                    problemas.append(f"{et} {cp}: {', '.join(m)} no está entre las primeras del top")
                continue
            mal = _viola(asignadas, zonas, campo, d)
            if mal:
                problemas.append(f"{et} {nombre}: {', '.join(mal)} no está entre las primeras del top")
    pedida = H.norm((filtros or {}).get("colonia", ""))
    if pedida:
        for m in re.finditer(rf"\ben\s+(?:la\s+|el\s+)?{re.escape(pedida)}\b", fn):
            for a, b, z in ms:
                if a > m.end() and a - m.end() <= 45 and z.get("en_colonia_consultada") is False \
                        and not re.search(r"\bkm\b|\bcerca\b|\bfuera\b|\bvecin|\bal lado\b", fn[m.end():a]):
                    problemas.append(f"{z['colonia']} no está dentro de {(filtros or {})['colonia']} (queda a {z.get('dist_a_colonia_km')} km)")
    return list(dict.fromkeys(problemas))


def frases(texto: str) -> list[str]:
    return [f for f in re.split(r"(?<=[.;])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«\"(])", texto.strip()) if f.strip()]


# ---------------------------------------------------------------- contexto: lo que dijeron TODAS las herramientas
_NOMBRES_GIRO: dict | None = None


def _regex_giros() -> dict[str, re.Pattern]:
    """{clave de giro: regex de sus nombres (singular o plural) sobre texto ligero}."""
    global _NOMBRES_GIRO
    if _NOMBRES_GIRO is None:
        from app import motor
        out = {}
        for clave, g in motor.giros().items():
            nombres = {H.norm(clave.replace("_", " ")), H.norm(H.nombre_giro(clave)), *[H.norm(n) for n in g.get("nombres", [])]}
            nombres = sorted((n for n in nombres if len(n) > 2), key=len, reverse=True)
            alt = "|".join(re.escape(n.rstrip("s") if len(n) > 3 else n) + ("s?" if len(n) > 3 else "") for n in nombres)
            out[clave] = re.compile(rf"\b(?:{alt})\b")
        _NOMBRES_GIRO = out
    return _NOMBRES_GIRO


def giros_en(fn: str) -> list[tuple[int, int, str]]:
    """[(inicio, fin, clave)] de los giros del catalogo que nombra la frase (texto ligero), por posicion."""
    spans = [(m.start(), m.end(), c) for c, rx in _regex_giros().items() for m in rx.finditer(fn)]
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    out: list[tuple[int, int, str]] = []
    for a, b, c in spans:  # un nombre dentro de otro mas largo («tienda» en «tienda de abarrotes») no cuenta aparte
        if any(a2 <= a and b <= b2 and (a2, b2) != (a, b) for a2, b2, _ in out):
            continue
        out.append((a, b, c))
    return out


class Contexto:
    """Lo que regresaron las herramientas de UNA respuesta, listo para revisar las frases de la lectura."""

    def __init__(self, usadas: list[dict], pregunta: str = ""):
        res = [u["resultado"] for u in usadas if isinstance(u.get("resultado"), dict)]
        self.pregunta = pregunta or ""
        self.rzs = [r for u in usadas if u["nombre"] == "recomendar_zonas" for r in [u["resultado"]]
                    if isinstance(r, dict) and r.get("encontrado") and r.get("zonas")]
        self.zt: dict = {}
        for r in self.rzs:
            for z in r["zonas"]:
                self.zt.setdefault(z["ageb"], (z, r))
        self.zonas_todas = [z for z, _ in self.zt.values()]
        sg = [r for u in usadas if u["nombre"] == "sugerir_giros" for r in [u["resultado"]]
              if isinstance(r, dict) and r.get("encontrado") and r.get("giros")]
        self.giros = sg[0]["giros"] if sg else []
        self.giros_claves = [g["giro"] for g in self.giros]
        self.giros_de_zonas = {r["giro"] for r in self.rzs if r.get("giro")}
        # numeros que valen para cualquier frase: lo que no es de una zona ni de un giro en particular
        generales = [r for u in usadas if u["nombre"] in ("perfil_giro", "contexto_macro", "ficha_municipio", "buscar_carpetas")
                     for r in [u["resultado"]] if isinstance(r, dict)]
        filtros = [[r.get("filtros"), (r.get("edad_clave") or {}), r.get("colonia_consultada")] for r in self.rzs + sg]
        self.general = numeros_tipados([generales, filtros])
        self.por_giro = {g["giro"]: numeros_tipados({k: v for k, v in g.items() if k != "giro"}) for g in self.giros}
        self.todos = numeros_tipados([u["resultado"] for u in usadas])

    # ---- cifras
    def _en(self, c: dict, tipo: str, conjunto: dict) -> bool:
        base = conjunto["todos"] if tipo == "num" else conjunto[tipo]
        return _coincide_exacto(c, base) or (tipo == "pct" and coincide(c, {n for n in base if 0 < n <= 1}))

    def cifras(self, fr: str) -> list[str]:
        """Cifras de la frase sin origen, de otra zona, de otro giro o de otro tipo (un % que no es %)."""
        fn = ligera(fr)
        zs = {id(z): z for _, _, z in menciones(fn, self.zonas_todas)}
        pool = list(zs.values()) or self.zonas_todas
        giros_f = [c for _, _, c in giros_en(fn)]
        fr = re.sub(r"\b\d{1,3}\s*(?:a|-|–)\s*\d{1,3}\s+a[ñn]os\b|\b60\s+(?:o m[aá]s|\+)\s*(?:a[ñn]os)?", " ", fr)  # rangos de edad
        out, cursor = [], 0
        for c in cifras_citadas(fr, self.pregunta):
            pos = fr.find(c["texto"], cursor)
            pos = fr.find(c["texto"]) if pos < 0 else pos
            cursor = max(cursor, pos + len(c["texto"]))
            tipo = _tipo_de_cifra(fr, pos, c) if pos >= 0 else "num"
            if self._en(c, tipo, self.general):
                continue
            # de un giro de sugerir_giros: del que nombra la frase (o de alguno, si no nombra ninguno)
            if self.por_giro:
                propios = [g for g in giros_f if g in self.por_giro]
                if any(self._en(c, tipo, self.por_giro[g]) for g in (propios or list(self.por_giro))):
                    continue
                if propios and any(self._en(c, tipo, self.por_giro[g]) for g in self.por_giro if g not in propios):
                    otro = next(g for g in self.por_giro if g not in propios and self._en(c, tipo, self.por_giro[g]))
                    out.append(f"{c['texto']} es de {H.nombre_giro(otro)}, no de {H.nombre_giro(propios[0])}")
                    continue
            campo = _campo_de_cifra(ligera(fr), pos, len(c["texto"])) if pos >= 0 else None
            validos = _campos_de_tipo(tipo) + (("edad_clave_pct_zmvm", "poblacion_ageb_2020", "residentes_objetivo_en_radio",
                                                "empleos_en_radio") if tipo == "num" else ())
            campos = (campo,) if campo and campo in validos else validos
            ok = False
            for z in pool:
                for cp in campos:
                    v = _valor(z, cp)
                    if v is None:
                        continue
                    if cp in CAMPOS_PCT:
                        ok = ok or coincide(c, {v})
                    else:
                        ok = ok or _coincide_exacto(c, {v}) or (cp in CAMPOS_PESOS and abs(c["valor"] - v) <= 600)
            if ok:
                continue
            if not self._en(c, tipo, self.todos) and not any(coincide(c, {n}) for n in self.todos["todos"]):
                out.append(f"{c['texto']} no sale de ninguna herramienta")
            else:
                zn = ", ".join(sorted({z["colonia"] for z in pool}))[:60]
                out.append(f"{c['texto']} no es {campo or 'del renglón'} de {zn}")
        return out

    # ---- giros
    def giros_problemas(self, fr: str) -> tuple[list[str], list[str]]:
        """(problemas de superlativo, problemas de cifras) sobre los giros que nombra la frase."""
        if not self.giros_claves:
            return [], []
        fn = ligera(fr)
        gs = giros_en(fn)
        sup, cif = [], []
        zm = menciones(fn, self.zonas_todas)
        pos_todos = sorted(m.start() for rx, _ in SUPERLATIVOS for m in rx.finditer(fn))
        for p in pos_todos:
            d = +1 if any(rx.match(fn, p) for rx, dd in SUPERLATIVOS if dd > 0) else -1
            previo = max([x for x in pos_todos if x < p], default=-1)
            siguiente = min([x for x in pos_todos if x > p], default=len(fn) + 1)
            asig = [c for a, b, c in gs if previo < a <= p and c in self.giros_claves] \
                or [c for a, b, c in gs if p < a < siguiente and c in self.giros_claves]
            if not asig or d < 0:
                continue
            if [z for a, b, z in zm if previo < a <= p] or [z for a, b, z in zm if p < a < siguiente]:
                continue  # el superlativo habla de una zona («las zonas del top de abarrotes, X tiene la mayor...»): lo juzga la regla de zonas
            trozo = fn[p:p + 90]
            campo = "prob_sigue_abierto_pct" if re.search(r"seguir abierto|sobrevive|supervivencia", trozo) else \
                "prob_apertura_pct" if re.search(r"\bapertura\b|\bprobabilidad\b", trozo) and not re.search(r"viabilidad", trozo) else "viabilidad_pct"
            if MAG_DE_ZONA.search(trozo[:60]):
                continue  # «destaca por su gasto potencial» es de zona: lo juzga la otra regla
            vals = sorted((g.get(campo) for g in self.giros if isinstance(g.get(campo), (int, float))), reverse=True)
            mios = [next((g.get(campo) for g in self.giros if g["giro"] == c), None) for c in dict.fromkeys(asig)]
            if vals and all(isinstance(v, (int, float)) for v in mios) and len(mios) <= len(vals):
                corte = vals[len(mios) - 1]
                mal = [H.nombre_giro(c) for c, v in zip(dict.fromkeys(asig), mios) if v < corte]
                if mal:
                    sup.append(f"mayor {campo}: {', '.join(mal)} no es de los primeros de la lista de sugerir_giros")
        # un giro que no tiene recomendar_zonas no puede llevar zonas ni magnitudes de zona
        ajenos = [c for _, _, c in gs if c not in self.giros_de_zonas and c in self.giros_claves]
        if ajenos and (menciones(fn, self.zonas_todas) or MAG_DE_ZONA.search(fn)):
            cif.append(f"{H.nombre_giro(ajenos[0])} no tiene zonas calculadas en esta respuesta (el top es de "
                       f"{', '.join(H.nombre_giro(g) for g in sorted(self.giros_de_zonas)) or 'ningún giro'})")
        return sup, cif


KW_CAMPO = (("prob_apertura_pct", re.compile(r"apertura|probabilidad")),
            ("captura_huff_pct", re.compile(r"captura")),
            ("edad_clave_pct", re.compile(r"edad|anos|menores|ninos|jovenes")),
            ("gasto_potencial_trim_mxn", re.compile(r"gasto")),
            ("ingreso_trim_mediano_estimado_mxn", re.compile(r"ingreso")),
            ("competidores_ponderados", re.compile(r"competidor|competencia")),
            ("score", re.compile(r"\bscore\b")),
            ("decil_estimado", re.compile(r"\bdecil\b")))


def _campo_de_cifra(fl: str, pos: int, largo: int) -> str | None:
    """Que magnitud nombra la frase (ligera) junto a una cifra: la palabra que sigue («67.2 % de la edad clave») o la ultima antes."""
    despues = fl[pos + largo:pos + largo + 26]
    for campo, rx in KW_CAMPO:
        if campo in ("edad_clave_pct", "prob_apertura_pct", "captura_huff_pct") \
                and re.match(r"\s*(?:%|por ciento)?\s*(?:de|en)\s+(?:la\s+|el\s+)?", despues) and rx.search(despues):
            return campo
    antes = fl[max(0, pos - 90):pos]
    mejor = None
    for campo, rx in KW_CAMPO:
        for k in rx.finditer(antes):
            if mejor is None or k.start() > mejor[0]:
                mejor = (k.start(), campo)
    return mejor[1] if mejor else None


def problemas(fr: str, ctx: Contexto) -> dict[str, list[str]]:
    """{'cifras': [...], 'superlativos': [...]}: por que la frase contradice a las herramientas (listas vacias = vale).
    Los superlativos de zona valen si vale contra alguna de las llamadas a recomendar_zonas."""
    sup = []
    if ctx.rzs:
        probs = [problemas_de_frase(fr, r["zonas"], r.get("filtros")) for r in ctx.rzs]
        if all(probs):
            sup += probs[0]
    sg_sup, sg_cif = ctx.giros_problemas(fr)
    return {"cifras": ctx.cifras(fr) + sg_cif, "superlativos": sup + sg_sup}


def orden_de_giros(texto: str, claves: list[str]) -> bool:
    """Los giros de `claves` (en el orden de sugerir_giros) se nombran en el texto en ese mismo orden (por primera aparicion)."""
    fn = ligera(texto)
    primera = {}
    for a, _, c in giros_en(fn):
        primera.setdefault(c, a)
    pos = [primera[c] for c in claves if c in primera]
    return pos == sorted(pos)


# ---------------------------------------------------------------- lectura armada por el codigo
def _nombre_bonito(colonia: str) -> str:
    romanos = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"}
    pal = str(colonia).split()
    return " ".join(p.capitalize() if i == 0 and p.lower() not in romanos else
                    p.lower() if p.lower() in ARTICULOS and i else p.upper() if p.lower() in romanos else p.capitalize()
                    for i, p in enumerate(pal))


def _hay_destacado(r: dict, campo: str, minimo: float | None = None) -> bool:
    """El destacado dice algo solo si el top no empata y, en probabilidades, el mayor no es una probabilidad baja."""
    vals = [v for v in (_valor(z, campo) for z in r.get("zonas", [])) if v is not None]
    if len(vals) < 2 or max(vals) == min(vals):
        return False
    return minimo is None or max(vals) >= minimo


def desde_destacados(r: dict) -> str:
    """Lectura corta armada por el codigo con `destacados` (cuando el modelo no dejo ninguna frase valida). Omite un
    destacado si todo el top empata en esa magnitud o si el mayor es una probabilidad de apertura baja."""
    d = r.get("destacados") or {}
    partes = []
    for clave, plantilla, campo, minimo in (
            ("mayor_prob_apertura", "tiene la mayor probabilidad de apertura ({v} %)", "prob_apertura_pct", 100 * H.PROB_BAJA),
            ("mayor_gasto_potencial", "tiene el mayor gasto potencial ({v} por trimestre)", "gasto_potencial_trim_mxn", None),
            ("menor_competencia", "tiene la menor competencia ({v} competidores ponderados)", "competidores_ponderados", None)):
        x = d.get(clave)
        if not x or not _hay_destacado(r, campo, minimo):
            continue
        v = [val for k, val in x.items() if k not in ("colonia", "ageb")][0]
        v = H._pesos_txt(v) if clave == "mayor_gasto_potencial" else v
        partes.append((_nombre_bonito(x["colonia"]), plantilla.format(v=v)))
    if not partes:
        return ""
    por_zona: dict[str, list[str]] = {}
    for zona, txt in partes:
        por_zona.setdefault(zona, []).append(txt.replace("tiene ", "", 1) if por_zona.get(zona) else txt)
    frases_ = [f"{zona} " + " y ".join(txts) for zona, txts in por_zona.items()]
    giro = f" de {H.nombre_giro(r['giro'])}" if r.get("giro") else ""
    return f"Entre las zonas del top{giro}, " + "; ".join(frases_) + "."


def desde_giros(g: list[dict]) -> str:
    """Una frase con el giro que encabeza sugerir_giros (la lista ya viene ordenada por viabilidad)."""
    if not g:
        return ""
    return f"Por viabilidad, {H.nombre_giro(g[0]['giro'])} encabeza la lista ({g[0]['viabilidad_pct']} %)."


INTERPRETA = re.compile(r",?\s*(?:lo que|que)\s+(?:refleja|indica|sugiere|implica|sostiene|muestra|significa|apunta)\b[^.;]*(?=[.;]|$)", re.I)


def _depurar_macro(lectura: str, ctx: Contexto) -> tuple[str | None, list[str]]:
    """Pregunta de economia sin zonas: se quitan las frases con cifras que no salen de contexto_macro y las interpretaciones
    sin respaldo («lo que refleja una moderada expectativa de gasto»): la herramienta da el valor, la fecha y la serie, no el juicio."""
    cuerpo = re.sub(r"^\*\*Lectura:?\*\*:?\s*", "", lectura)
    buenas, quitadas = [], []
    for fr in frases(cuerpo):
        mal = ctx.cifras(fr)
        if mal:
            quitadas.append(f"{fr[:70]}… ({'; '.join(mal[:2])})")
            continue
        limpia = INTERPRETA.sub("", fr).rstrip(" ,")
        if limpia != fr.rstrip():
            quitadas.append(f"{fr[:70]}… (interpretación sin respaldo en contexto_macro)")
            limpia = limpia if limpia.endswith((".", ";")) else limpia + "."
        buenas.append(limpia)
    if not quitadas:
        return lectura, []
    return ("**Lectura:** " + " ".join(buenas)) if buenas else None, quitadas


def depurar(lectura: str | None, usadas: list[dict], pregunta: str = "") -> tuple[str | None, list[str]]:
    """(lectura revisada, frases quitadas). `lectura` empieza con «**Lectura:**»; con varias llamadas a recomendar_zonas
    cada frase se revisa contra las zonas de todas (basta con que valga contra una). Ademas de los superlativos se
    revisan las cifras (de ninguna herramienta, de otra zona, de otro giro) y los giros de sugerir_giros (el que lidera es
    el 1, se nombran en el orden de la herramienta)."""
    ctx = Contexto(usadas, pregunta)
    if lectura and not (ctx.rzs or ctx.giros) and any(u["nombre"] == "contexto_macro" for u in usadas):
        return _depurar_macro(lectura, ctx)
    if not lectura or not (ctx.rzs or ctx.giros):
        return lectura, []
    cuerpo = re.sub(r"^\*\*Lectura:?\*\*:?\s*", "", lectura)
    buenas, quitadas = [], []
    vistos: list[str] = []      # giros ya nombrados en la lectura, en el orden de la herramienta
    for fr in frases(cuerpo):
        malos = problemas(fr, ctx)
        motivo = malos["cifras"] + malos["superlativos"]
        if not motivo and ctx.giros_claves:   # un giro nuevo no puede ir antes de uno de mejor lugar ya nombrado
            nuevos = [c for c in dict.fromkeys(c for _, _, c in giros_en(ligera(fr))) if c in ctx.giros_claves and c not in vistos]
            rangos = [ctx.giros_claves.index(c) for c in nuevos]
            previos = [ctx.giros_claves.index(c) for c in vistos]
            if rangos != sorted(rangos) or (previos and rangos and min(rangos) < max(previos)):
                motivo = ["los giros se nombran fuera del orden de sugerir_giros"]
            else:
                vistos += nuevos
        if motivo:
            quitadas.append(f"{fr[:70]}… ({'; '.join(motivo[:2])})")
        else:
            buenas.append(fr)
    if not quitadas:
        return lectura, []
    # lo que queda no puede depender de lo que se quito («Ambas son opciones...», «Por otro lado...»)
    sueltas = [f for f in buenas if not ANAFORA.match(f)][:2]
    base = desde_destacados(ctx.rzs[0]) if ctx.rzs else ""
    if not base and not sueltas and ctx.giros:
        base = desde_giros(ctx.giros)
    nuevo = " ".join(([base] if base else []) + sueltas).strip()
    return ("**Lectura:** " + nuevo) if nuevo else None, quitadas
