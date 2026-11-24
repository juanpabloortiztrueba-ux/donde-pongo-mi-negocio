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
    ("edad clave", "edad_clave_pct", re.compile(
        r"\bedad\b|\bedades\b|\b\d{1,2}\s+(?:a\s+)?\d{1,2}\s+anos\b|\b(?:0|15|25)\s+(?:a\s+)?(?:14|24|59)\b|\b60\s+(?:o mas|anos o mas|\+)|"
        r"\bmenores de \d+|\bmayores de \d+|\bninos\b|\bninas\b|\bjovenes\b|\badolescentes\b|\badultos\b|\binfantil\b|"
        r"\btercera edad\b|\bporcentaje de [a-z0-9 ]{0,40}\banos\b")),
    ("score", "score", re.compile(r"\bscore\b|\bpuntaje\b")),
)
# grupo de edad del Censo que nombra una frase (texto ligero: «0-14» queda «0 14»); el 60+ va primero («adultos mayores»)
GRUPOS_EDAD = (
    ("60+", re.compile(r"\badultos mayores\b|\b60\s+(?:o mas|anos o mas|\+)|\btercera edad\b|\bmayor(?:es)? de 6[05]\b|\badultos de 60")),
    ("0-14", re.compile(r"\bmenor(?:es)? de 1[45]\b|\bninos\b|\bninas\b|\b0\s+(?:a\s+)?14\b|\binfantil\b|\bpoblacion infantil\b")),
    ("15-24", re.compile(r"\bjovenes\b|\b15\s+(?:a\s+)?24\b|\badolescentes\b")),
    ("25-59", re.compile(r"\badultos\b|\b25\s+(?:a\s+)?59\b")),
)


def grupo_de_edad(trozo: str) -> str | None:
    """Grupo de edad (0-14, 15-24, 25-59, 60+) que nombra el trozo de texto ligero, o None."""
    for grupo, rx in GRUPOS_EDAD:
        if rx.search(trozo):
            return grupo
    return None


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
SALTA_COMA = re.compile(r"(?:destaca|sobresale)(?:n)?\s*,\s*(?:con|por|gracias a|al tener)\b")
GENERICO_OK = re.compile(r"mejor|lider|mayor|mas alt")   # con estas, «la oportunidad / la mejor opcion / el mayor potencial» se compara con el score
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


DICE_EMPATE = re.compile(r"\bempat|\bigual|\btambien\b|\bcompart|\bjunto con\b|\bambas?\b|\bambos\b|\bmismo\b|\bcoincid")


def _empate_sin_decir(asignadas: list[dict], todas: list[dict], campo: str, d: int, fn: str) -> list[str]:
    """Nombres de las zonas que empatan en el extremo de `campo` con las que la frase presenta como las unicas («CENTRO tiene
    la menor competencia con 0.0» cuando Caracoles y otra zona tambien tienen 0.0) y que la frase no nombra ni dice que empatan."""
    vals = [v for v in (_valor(z, campo) for z in todas) if v is not None]
    mias = [_valor(z, campo) for z in asignadas]
    if not vals or any(v is None for v in mias) or DICE_EMPATE.search(fn):
        return []
    ext = max(vals) if d > 0 else min(vals)
    if any(v != ext for v in mias):
        return []                       # esa zona no es el extremo: lo dice la otra regla
    ids = {id(z) for z in asignadas}
    return [z["colonia"] for z in todas if id(z) not in ids and _valor(z, campo) == ext]


def problemas_de_frase(frase: str, zonas: list[dict], filtros: dict | None = None) -> list[str]:
    """Motivos por los que la frase contradice a los datos de las zonas (lista vacia = la frase vale)."""
    fn = ligera(frase)
    ms = menciones(fn, zonas)
    problemas: list[str] = []
    pares = _pares_superlativo(fn)
    pos_todos = sorted(m.start() for rx, _ in SUPERLATIVOS for m in rx.finditer(fn))
    pos_pares = {q["pos"] for q in pares}
    for par in pares:
        p, d = par["pos"], par["dir"]
        previo = max([x for x in pos_todos if x < p], default=-1)
        # «La colonia X destaca por tener el mayor porcentaje de...»: «destaca» no trae magnitud propia y la zona va antes
        # de el; un superlativo vecino sin magnitud (sin coma de por medio) no corta la busqueda de la zona
        # (con coma tambien: «X destaca, con el mayor porcentaje de...» / «destaca por / gracias a / al tener»)
        while previo >= 0 and previo not in pos_pares and ("," not in fn[previo:p] or SALTA_COMA.match(fn[previo:p])):
            previo = max([x for x in pos_todos if x < previo], default=-1)
        siguiente = min([x for x in pos_todos if x > p], default=len(fn) + 1)
        asignadas = [z for a, b, z in ms if previo < a <= p] or [z for a, b, z in ms if p < a < siguiente]
        asignadas = list({id(z): z for z in asignadas}.values())
        if not asignadas:
            continue
        et = "mayor" if d > 0 else "menor"
        if par["campo"] == "edad_clave_pct":
            # el top solo compara la edad clave del giro: «mayor porcentaje de adultos mayores» en una heladeria no se puede juzgar
            g_frase, g_top = grupo_de_edad(fn[p:p + 90]), asignadas[0].get("edad_clave_grupo")
            if g_frase and g_top and g_frase != g_top:
                problemas.append(f"{et} edad: el top solo compara {asignadas[0].get('edad_clave_etiqueta', g_top)}, no {g_frase}")
                continue
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
            elif (emp := _empate_sin_decir(asignadas, zonas, campo, d, fn)):
                problemas.append(f"{et} {nombre}: empata con {', '.join(emp)} y la frase no lo dice")
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
            validos = _campos_de_tipo(tipo) + (("edad_clave_pct_zmvm", "poblacion_ageb_2020", "hogares_ageb_2020",
                                                "residentes_objetivo_en_radio", "empleos_en_radio") if tipo == "num" else ())
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

    # ---- una magnitud con la cifra de otra
    def mezclas(self, fr: str) -> list[str]:
        """«Anzures muestra una alta captura con 62.9 % de la edad clave»: la frase habla de una magnitud (captura, apertura,
        competencia, ingreso, gasto, score) y la cifra que le pone es de otra («de la edad clave»). Solo cuenta si entre la
        magnitud y la cifra no hay coma, «y», «pero» ni otra cifra: ahi la cifra ya es de otra idea."""
        fl = ligera(fr)
        out = []
        for m in CIFRA_RE.finditer(fl):
            despues = fl[m.end():m.end() + 26]
            dm = re.match(r"\s*(?:%|por ciento)?\s*(?:de|en)\s+(?:la\s+|el\s+)?", despues)
            if not dm:
                continue
            campo_b = next((c for c, rx in KW_CAMPO if rx.match(despues[dm.end():])), None)
            if campo_b is None:
                continue
            antes = fl[:m.start()]
            corte = list(re.finditer(r"[.;,]|\b(?:y|e|pero|mientras|ademas|aunque|tambien)\b", antes))
            seg = antes[corte[-1].end():] if corte else antes
            if CIFRA_RE.search(seg):
                continue
            for campo_a, rx in MAGNITUD_DE_FRASE:
                if campo_a != campo_b and rx.search(seg):
                    out.append(f"{m.group(0).strip()} es {NOMBRE_CAMPO.get(campo_b, campo_b)}, no {NOMBRE_CAMPO.get(campo_a, campo_a)}")
                    break
        return out

    # ---- giros
    def giros_problemas(self, fr: str) -> tuple[list[str], list[str]]:
        """(problemas de superlativo, problemas de cifras) sobre los giros que nombra la frase."""
        fn = ligera(fr)
        gs = giros_en(fn)
        sup, cif = [], []
        zm = menciones(fn, self.zonas_todas)
        # sin sugerir_giros no hay superlativos de giro que juzgar, pero si un giro ajeno al top (abajo)
        pos_todos = sorted(m.start() for rx, _ in SUPERLATIVOS for m in rx.finditer(fn)) if self.giros_claves else []
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
        # p. ej. «heladería» heredada del historial; no cuenta un nombre dentro de una colonia («Gabriel Ramos Millán»)
        ajenos = [c for a, _, c in gs if c not in self.giros_de_zonas and not any(za <= a < zb for za, zb, _ in zm)]
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


# magnitudes que una frase puede nombrar antes de una cifra (para `Contexto.mezclas`) y como se llaman en el aviso
MAGNITUD_DE_FRASE = (("captura_huff_pct", re.compile(r"\bcaptura\b")),
                     ("prob_apertura_pct", re.compile(r"\bapertura\b|\bprobabilidad\b")),
                     ("competidores_ponderados", re.compile(r"\bcompetidores\b|\bcompetencia\b")),
                     ("ingreso_trim_mediano_estimado_mxn", re.compile(r"\bingresos?\b")),
                     ("gasto_potencial_trim_mxn", re.compile(r"\bgasto\b")),
                     ("score", re.compile(r"\bscore\b|\bpuntaje\b")))
NOMBRE_CAMPO = {"captura_huff_pct": "la captura", "prob_apertura_pct": "la probabilidad de apertura", "edad_clave_pct": "la edad clave",
                "competidores_ponderados": "la competencia", "ingreso_trim_mediano_estimado_mxn": "el ingreso",
                "gasto_potencial_trim_mxn": "el gasto potencial", "score": "el score", "decil_estimado": "el decil"}


def _campo_de_cifra(fl: str, pos: int, largo: int) -> str | None:
    """Que magnitud nombra la frase (ligera) junto a una cifra: la palabra que sigue («67.2 % de la edad clave») o la ultima antes."""
    despues = fl[pos + largo:pos + largo + 26]
    habita = re.match(r"\s*(habitantes|hogares)\b", despues)    # «AGEB con 20 habitantes» (aviso de una AGEB casi vacia)
    if habita:
        return "poblacion_ageb_2020" if habita.group(1) == "habitantes" else "hogares_ageb_2020"
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
    return {"cifras": ctx.cifras(fr) + ctx.mezclas(fr) + sg_cif, "superlativos": sup + sg_sup}


def orden_de_giros(texto: str, claves: list[str]) -> bool:
    """Los giros de `claves` (en el orden de sugerir_giros) se nombran en el texto en ese mismo orden (por primera aparicion)."""
    fn = ligera(texto)
    primera = {}
    for a, _, c in giros_en(fn):
        primera.setdefault(c, a)
    pos = [primera[c] for c in claves if c in primera]
    return pos == sorted(pos)


# ---------------------------------------------------------------- lectura armada por el codigo
# acentos de los nombres de colonia (la base del DENUE los trae en mayusculas y sin acento); misma tabla que
# web/src/comun/formato.ts::ACENTOS, para que el chat y las tarjetas escriban igual
ACENTOS = {
    "juarez": "Juárez", "aragon": "Aragón", "seccion": "Sección", "ampliacion": "Ampliación", "jimenez": "Jiménez", "cantu": "Cantú",
    "gonzalez": "González", "hernandez": "Hernández", "martinez": "Martínez", "perez": "Pérez", "rodriguez": "Rodríguez",
    "ramirez": "Ramírez", "sanchez": "Sánchez", "lopez": "López", "garcia": "García", "gutierrez": "Gutiérrez", "fernandez": "Fernández",
    "alvarez": "Álvarez", "alvaro": "Álvaro", "obregon": "Obregón", "tlahuac": "Tláhuac", "coyoacan": "Coyoacán", "atizapan": "Atizapán",
    "cuautitlan": "Cuautitlán", "chimalhuacan": "Chimalhuacán", "nezahualcoyotl": "Nezahualcóyotl", "tecamac": "Tecámac",
    "jardin": "Jardín", "mexico": "México", "maria": "María", "jose": "José", "sebastian": "Sebastián", "andres": "Andrés",
    "periferico": "Periférico", "union": "Unión", "revolucion": "Revolución", "constitucion": "Constitución", "cooperacion": "Cooperación",
    "politecnico": "Politécnico", "lazaro": "Lázaro", "cardenas": "Cárdenas", "pantitlan": "Pantitlán", "vazquez": "Vázquez",
    "gomez": "Gómez", "ramon": "Ramón", "agricola": "Agrícola", "habitacion": "Habitación", "penon": "Peñón", "republica": "República",
    "petroleo": "Petróleo", "mixcoatl": "Mixcóatl", "quetzalcoatl": "Quetzalcóatl", "agustin": "Agustín", "alamos": "Álamos", "rio": "Río",
    "olimpica": "Olímpica", "muzquiz": "Múzquiz", "pavon": "Pavón", "baez": "Báez", "evolucion": "Evolución", "capulin": "Capulín",
    "anahuac": "Anáhuac", "asis": "Asís", "jesus": "Jesús", "simon": "Simón", "barbara": "Bárbara", "martin": "Martín", "dario": "Darío",
    "lucia": "Lucía", "frio": "Frío", "tequisistlan": "Tequisistlán", "hipodromo": "Hipódromo", "ctm": "CTM",
}
_ROMANOS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"}


def _palabra_bonita(p: str, i: int) -> str:
    if "-" in p:                       # «IX-A»: cada parte por separado; una letra sola queda en mayuscula
        return "-".join(x.upper() if len(x) == 1 else _palabra_bonita(x, i) for x in p.split("-"))
    bajo = p.lower()
    if bajo in _ROMANOS:
        return p.upper()
    if bajo in ACENTOS:
        return ACENTOS[bajo]
    return bajo if i and bajo in ARTICULOS else p.capitalize()


def _nombre_bonito(colonia: str) -> str:
    """«DEL VALLE NORTE» -> «Del Valle Norte»; «FUENTES DE ARAGON» -> «Fuentes de Aragón»; «POLANCO IV SECCION» -> «Polanco IV Sección»."""
    return " ".join(_palabra_bonita(p, i) for i, p in enumerate(str(colonia).split()))


def _con_acentos_de(bonito: str, escrito: str) -> str:
    """`bonito` conserva los acentos que ya traia `escrito` (misma longitud y mismas letras sin acento) y que la tabla no conoce."""
    if len(bonito) != len(escrito) or ligera(bonito) != ligera(escrito):
        return bonito
    def acentuada(c: str) -> bool:
        return len(unicodedata.normalize("NFD", c)) > 1

    out = []
    for b, w in zip(bonito, escrito):
        out.append((w.upper() if b.isupper() else w.lower()) if acentuada(w) and not acentuada(b) else b)
    return "".join(out)


def _hay_destacado(r: dict, campo: str, minimo: float | None = None) -> bool:
    """El destacado dice algo solo si el top no empata y, en probabilidades, el mayor no es una probabilidad baja."""
    vals = [v for v in (_valor(z, campo) for z in r.get("zonas", [])) if v is not None]
    if len(vals) < 2 or max(vals) == min(vals):
        return False
    return minimo is None or max(vals) >= minimo


MAX_EMPATE = 3     # si mas de 3 zonas empatan en el extremo, el empate no distingue a nadie y no se dice

# (clave de destacados, campo de la zona, el extremo es el mayor, valor minimo del mayor, frase de una zona, frase de un empate)
DESTACADOS_TEXTO = (
    ("mayor_prob_apertura", "prob_apertura_pct", True, 100 * H.PROB_BAJA,
     "tiene la mayor probabilidad de apertura ({v} %)", "empatan con la mayor probabilidad de apertura ({v} %)"),
    ("mayor_gasto_potencial", "gasto_potencial_trim_mxn", True, None,
     "tiene el mayor gasto potencial ({v} por trimestre)", "empatan con el mayor gasto potencial ({v} por trimestre)"),
    ("menor_competencia", "competidores_ponderados", False, None,
     "tiene la menor competencia ({v} competidores ponderados)", "empatan con la menor competencia ({v} competidores ponderados)"),
)


def _zonas_en_el_extremo(r: dict, campo: str, mayor: bool) -> list[dict]:
    """Las zonas del top que tienen el valor extremo de `campo` (varias si empatan, en el orden del top). Vacio si todo el
    top empata, si falta el dato o si empatan mas de MAX_EMPATE zonas."""
    zs = [(z, _valor(z, campo)) for z in r.get("zonas", [])]
    zs = [(z, v) for z, v in zs if v is not None]
    if len(zs) < 2 or max(v for _, v in zs) == min(v for _, v in zs):
        return []
    ext = max(v for _, v in zs) if mayor else min(v for _, v in zs)
    top = [z for z, v in zs if v == ext]
    return top if len(top) <= MAX_EMPATE else []


def partes_destacados(r: dict) -> list[dict]:
    """[{zonas, campo, texto}] de lo que la lectura armada por el codigo dice: una zona con la mayor probabilidad de apertura,
    el mayor gasto o la menor competencia, o varias zonas que empatan en ese extremo (se nombran todas). Omite la magnitud si
    todo el top empata o si el mayor es una probabilidad de apertura baja."""
    partes = []
    for _, campo, mayor, minimo, uno, empate in DESTACADOS_TEXTO:
        if not _hay_destacado(r, campo, minimo):
            continue
        zs = _zonas_en_el_extremo(r, campo, mayor)
        if not zs:
            continue
        v = _valor(zs[0], campo)
        v = int(v) if campo == "prob_apertura_pct" else v
        v = H._pesos_txt(v) if campo == "gasto_potencial_trim_mxn" else v
        partes.append({"zonas": zs, "campo": campo, "texto": (uno if len(zs) == 1 else empate).format(v=v)})
    return partes


def _lista_nombres(nombres: list[str]) -> str:
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def desde_destacados(r: dict) -> str:
    """Lectura corta armada por el codigo con los extremos del top (cuando el modelo no dejo ninguna frase valida). Omite un
    destacado si todo el top empata en esa magnitud o si el mayor es una probabilidad de apertura baja; si 2 o 3 zonas
    empatan en el extremo las nombra todas («A, B y C empatan con la menor competencia (0.0 competidores ponderados)»)."""
    por_grupo: dict[tuple, list[str]] = {}
    for parte in partes_destacados(r):
        nombres = tuple(_nombre_bonito(z["colonia"]) for z in parte["zonas"])
        txt = parte["texto"]
        if por_grupo.get(nombres):       # la misma zona (o el mismo empate) en otra magnitud: «... y la menor competencia»
            txt = txt.replace("tiene ", "", 1) if len(nombres) == 1 else txt.replace("empatan ", "", 1)
        por_grupo.setdefault(nombres, []).append(txt)
    if not por_grupo:
        return ""
    frases_ = [f"{_lista_nombres(list(nombres))} " + " y ".join(txts) for nombres, txts in por_grupo.items()]
    giro = f" de {H.nombre_giro(r['giro'])}" if r.get("giro") else ""
    return f"Entre las zonas del top{giro}, " + "; ".join(frases_) + "."


def desde_giros(g: list[dict]) -> str:
    """Una frase con el giro que encabeza sugerir_giros (la lista ya viene ordenada por viabilidad)."""
    if not g:
        return ""
    return f"Por viabilidad, {H.nombre_giro(g[0]['giro'])} encabeza la lista ({g[0]['viabilidad_pct']} %)."


NEGRITAS = re.compile(r"\*\*(.+?)\*\*")


def _sin_negritas(cuerpo: str) -> tuple[str, bool]:
    """La lectura no lleva negritas (las pone el codigo en los titulos de bloque): se quitan las que el modelo agrega."""
    limpio = NEGRITAS.sub(r"\1", cuerpo)
    return limpio, limpio != cuerpo


INTERPRETA = re.compile(r",?\s*(?:lo que|que)\s+(?:refleja|indica|sugiere|implica|sostiene|muestra|significa|apunta)\b[^.;]*(?=[.;]|$)", re.I)


def _depurar_macro(lectura: str, ctx: Contexto) -> tuple[str | None, list[str]]:
    """Pregunta de economia sin zonas: se quitan las frases con cifras que no salen de contexto_macro y las interpretaciones
    sin respaldo («lo que refleja una moderada expectativa de gasto»): la herramienta da el valor, la fecha y la serie, no el juicio."""
    cuerpo, sin_neg = _sin_negritas(re.sub(r"^\*\*Lectura:?\*\*:?\s*", "", lectura))
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
        return (("**Lectura:** " + " ".join(buenas)) if sin_neg and buenas else lectura), []
    return ("**Lectura:** " + " ".join(buenas)) if buenas else None, quitadas


def _distancia_una_letra(a: str, b: str) -> bool:
    """a y b difieren exactamente en una letra (cambiada, sobrante o faltante)."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    corto, largo = sorted((a, b), key=len)
    return any(largo[:i] + largo[i + 1:] == corto for i in range(len(largo)))


def normalizar_nombres(frase: str, zonas: list[dict]) -> str:
    """Escribe cada zona del top con su nombre bonito y acentuado («Fuentes de Aragón», «Del Valle Norte») cuando la frase lo
    escribe distinto: otra mayuscula o minuscula («del Valle Norte»), en singular («Fuente de Aragon») o con una letra de
    diferencia. Si la frase solo cambia mayusculas o acentos, conserva los acentos que ya traia («Ampliación Nápoles»). El
    nombre exacto del renglon, que viene en MAYUSCULAS («FUENTES DE ARAGON», «POLANCO I SECCIÓN»), tambien se escribe bonito:
    en la prosa no se mezclan nombres en mayusculas con nombres acentuados. No toca un nombre seguido de una palabra con
    mayuscula (podria ser otra colonia mas larga)."""
    fn = ligera(frase)
    cambios: list[tuple[int, int, str]] = []
    cubiertos: list[tuple[int, int]] = []
    for a, b, z in menciones(fn, zonas):
        cubiertos.append((a, b))
        generica = len(_tokens_nombre(z["colonia"])) == 1 and frase[a].islower()    # «el centro de la ciudad» no es la colonia CENTRO
        escrito = frase[a:b]
        # solo cambian mayusculas o acentos: se escribe bonito y con los acentos que ya traia («Nápoles» no pierde su acento)
        destino = _con_acentos_de(_nombre_bonito(z["colonia"]), escrito) if ligera(escrito) == ligera(z["colonia"]) \
            else _nombre_bonito(z["colonia"])
        if escrito != destino and not generica and not re.match(r"\s+[A-ZÁÉÍÓÚÑ]\w", frase[b:]):
            cambios.append((a, b, destino))
    nombres = {H.norm(z["colonia"]) for z in zonas}
    toks = [(m.start(), m.end(), m.group()) for m in re.finditer(r"[a-z0-9]+", fn)]
    for z in zonas:                       # una letra de diferencia («Pedregal de Santo Domingu»)
        nom = H.norm(z["colonia"])
        n = len(nom.split())
        if n < 1 or (n < 2 and len(nom) < 8) or len(nom) < 6:
            continue
        for i in range(len(toks) - n + 1):
            ventana = toks[i:i + n]
            if any(fn[ventana[k][1]:ventana[k + 1][0]].strip() for k in range(n - 1)):
                continue                   # una coma o un punto de por medio: no es un solo nombre
            cand = " ".join(t for _, _, t in ventana)
            a, b = ventana[0][0], ventana[-1][1]
            if cand in nombres or not _distancia_una_letra(cand, nom) or any(a < y and x < b for x, y in cubiertos):
                continue
            if not re.match(r"\s+[A-ZÁÉÍÓÚÑ]\w", frase[b:]):
                cambios.append((a, b, _nombre_bonito(z["colonia"])))
                cubiertos.append((a, b))
    for a, b, exacto in sorted(cambios, reverse=True):
        frase = frase[:a] + exacto + frase[b:]
    return frase


MEJOR_OPCION = re.compile(r"\bla mejor\b|\bmejor(?:es)?\s+(?:opcion(?:es)?|zonas?|colonias?|ubicacion(?:es)?|lugar(?:es)?|sitios?|alternativas?)\b|"
                          r"\b(?:opcion|lugar|zona|colonia) ideal\b")
AVISO_YA_DICHO = re.compile(r"\bhabitantes\b|\bhogares\b|\bradio de influencia\b")


def con_aviso_de_ageb_vacia(frase: str, zonas: list[dict]) -> str:
    """Si la frase llama «la mejor opcion» a una zona con aviso (AGEB con menos de 200 habitantes o 50 hogares) y no lo dice,
    le agrega el aviso: la zona sigue en la lectura, pero nunca sin el dato de que casi nadie vive ahi."""
    fn = ligera(frase)
    if not MEJOR_OPCION.search(fn) or AVISO_YA_DICHO.search(fn):
        return frase
    for _, _, z in menciones(fn, zonas):
        if z.get("aviso_ageb_poco_poblada"):
            return frase.rstrip().rstrip(".;") + f" ({z['aviso_ageb_poco_poblada']})."
    return frase


def _repite_la_base(frase: str, zonas: list[dict], cubiertos: set) -> bool:
    """La frase solo dice (zona, magnitud) que la lectura armada por el codigo ya dijo: no se repite."""
    fn = ligera(frase)
    zs = {z["ageb"] for _, _, z in menciones(fn, zonas)}
    campos = {campo for _, campo, rx in MAGNITUDES if rx.search(fn)}
    return bool(zs and campos) and all((a, c) in cubiertos for a in zs for c in campos)


CONCORDANCIA = re.compile(r"\b([Ee])l (mayor|menor) (competencia|probabilidad|captura|viabilidad|poblaci[oó]n|densidad|escolaridad)\b")
SEPARA_CLAUSULAS = re.compile(r",\s*(?:mientras que|en cambio|a diferencia de)\s+", re.I)
PIDE_ZONAS = re.compile(r"\bdonde\b|\bzonas?\b|\bcolonias?\b|\bubicacion\b|\blugar(?:es)?\b|\bmunicipio\b|\balcaldia\b|\bagebs?\b")


def corregir_concordancia(frase: str) -> str:
    """«el menor competencia» -> «la menor competencia» (el modelo falla el genero con los sustantivos femeninos)."""
    return CONCORDANCIA.sub(lambda m: ("L" if m.group(1) == "E" else "l") + f"a {m.group(2)} {m.group(3)}", frase)


def clausulas(frase: str) -> list[str]:
    """La frase partida en «..., mientras que ...»: cada trozo como frase suelta (mayuscula inicial y punto final)."""
    partes = SEPARA_CLAUSULAS.split(frase.strip())
    if len(partes) < 2:
        return [frase]
    out = []
    for t in partes:
        t = t.strip().rstrip(".;").strip()
        if t:
            out.append(t[0].upper() + t[1:] + ".")
    return out


def sin_repetir(frases_: list[str], zonas: list[dict]) -> list[str]:
    """Quita la frase (o la cláusula «..., mientras que ...») que solo repite lo que otra ya dijo de la misma zona y las mismas
    magnitudes («Ampliación Nápoles tiene la mayor probabilidad y el mayor gasto» y, dos frases despues, «Ampliación Nápoles
    destaca por su gasto y su probabilidad»). Solo juzga trozos que nombran una sola zona y al menos una magnitud."""
    dichos: set[tuple[str, str]] = set()
    out: list[str] = []
    for fr in frases_:
        trozos = SEPARA_CLAUSULAS.split(fr.strip())
        quedan = []
        for t in trozos:
            fn = ligera(t)
            zs = {z["ageb"] for _, _, z in menciones(fn, zonas)}
            campos = {campo for _, campo, rx in MAGNITUDES if rx.search(fn)}
            pares = {(a, c) for a in zs for c in campos} if len(zs) == 1 else set()
            if pares and pares <= dichos:
                continue
            dichos |= pares
            quedan.append(t.strip())
        if len(quedan) == len(trozos):
            out.append(fr)
        elif quedan:
            texto = ", mientras que ".join(q.rstrip(".;").strip() for q in quedan)
            out.append(texto[0].upper() + texto[1:] + ".")
    return out


def depurar(lectura: str | None, usadas: list[dict], pregunta: str = "") -> tuple[str | None, list[str]]:
    """(lectura revisada, frases quitadas). `lectura` empieza con «**Lectura:**»; con varias llamadas a recomendar_zonas
    cada frase se revisa contra las zonas de todas (basta con que valga contra una). Ademas de los superlativos se
    revisan las cifras (de ninguna herramienta, de otra zona, de otro giro) y los giros de sugerir_giros (el que lidera es
    el 1, se nombran en el orden de la herramienta). Una frase con «..., mientras que ...» que falla se parte: se
    conservan las cláusulas que valen. En una pregunta de «cómo influye la inflación...» que no pide zonas, la lectura no
    habla de zonas. Tambien se quita lo que repite lo que ya se dijo de la misma zona."""
    ctx = Contexto(usadas, pregunta)
    if lectura and not (ctx.rzs or ctx.giros) and any(u["nombre"] == "contexto_macro" for u in usadas):
        return _depurar_macro(lectura, ctx)
    if not lectura or not (ctx.rzs or ctx.giros):
        return lectura, []
    cuerpo, retocada = _sin_negritas(re.sub(r"^\*\*Lectura:?\*\*:?\s*", "", lectura))
    q_norm = H.norm(pregunta or "")
    macro_puro = bool(pregunta and H.pide_como_influye(pregunta) and not PIDE_ZONAS.search(q_norm)
                      and any(u["nombre"] == "contexto_macro" and isinstance(u["resultado"], dict) and u["resultado"].get("como_influye")
                              for u in usadas))
    buenas, quitadas = [], []
    vistos: list[str] = []      # giros ya nombrados en la lectura, en el orden de la herramienta
    # (retocada: negritas quitadas, nombres de zona reescritos o aviso de AGEB casi vacia agregado)

    def revisar(fr0: str) -> tuple[str | None, list[str]]:
        fr = corregir_concordancia(normalizar_nombres(fr0, ctx.zonas_todas))
        malos = problemas(fr, ctx)
        motivo = malos["cifras"] + malos["superlativos"]
        if macro_puro and menciones(ligera(fr), ctx.zonas_todas):
            motivo = motivo + ["la pregunta es de economía y la frase habla de zonas"]
        nuevos: list[str] = []
        if not motivo and ctx.giros_claves:   # un giro nuevo no puede ir antes de uno de mejor lugar ya nombrado
            nuevos = [c for c in dict.fromkeys(c for _, _, c in giros_en(ligera(fr))) if c in ctx.giros_claves and c not in vistos]
            rangos = [ctx.giros_claves.index(c) for c in nuevos]
            previos = [ctx.giros_claves.index(c) for c in vistos]
            if rangos != sorted(rangos) or (previos and rangos and min(rangos) < max(previos)):
                motivo = ["los giros se nombran fuera del orden de sugerir_giros"]
        if motivo:
            return None, motivo
        vistos.extend(nuevos)
        return con_aviso_de_ageb_vacia(fr, ctx.zonas_todas), []

    for fr0 in frases(cuerpo):
        fr, motivo = revisar(fr0)
        if fr is None and len(clausulas(fr0)) > 1:      # se salva lo que valga de cada clausula
            for cl in clausulas(fr0):
                fr_c, motivo_c = revisar(cl)
                if fr_c is None:
                    quitadas.append(f"{cl[:70]}… ({'; '.join(motivo_c[:2])})")
                else:
                    buenas.append(fr_c)
                    retocada = True
            continue
        if fr is None:
            quitadas.append(f"{fr0[:70]}… ({'; '.join(motivo[:2])})")
        else:
            retocada = retocada or fr != fr0
            buenas.append(fr)
    antes = list(buenas)
    buenas = sin_repetir(buenas, ctx.zonas_todas)
    retocada = retocada or buenas != antes
    if not quitadas:
        return (("**Lectura:** " + " ".join(buenas)) if retocada and buenas else lectura), []
    if macro_puro:      # la lectura es del mecanismo: no se le agregan zonas armadas por el codigo
        return (("**Lectura:** " + " ".join(buenas)) if buenas else None), quitadas
    # lo que queda no puede depender de lo que se quito («Ambas son opciones...», «Por otro lado...»)
    base = desde_destacados(ctx.rzs[0]) if ctx.rzs else ""
    cubiertos = {(z["ageb"], p["campo"]) for p in (partes_destacados(ctx.rzs[0]) if ctx.rzs else []) for z in p["zonas"]}
    sueltas = [f for f in buenas if not ANAFORA.match(f) and not _repite_la_base(f, ctx.zonas_todas, cubiertos)][:2]
    if not base and not sueltas and ctx.giros:
        base = desde_giros(ctx.giros)
    nuevo = " ".join(([base] if base else []) + sueltas).strip()
    return ("**Lectura:** " + nuevo) if nuevo else None, quitadas
