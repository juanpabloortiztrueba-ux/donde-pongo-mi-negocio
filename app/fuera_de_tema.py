"""Preguntas fuera de tema y red de seguridad contra nombres de funciones internas. Sin LLM: solo reglas.

    clasificar("¿Cómo me llamo?")            -> ("nombre", "tu_nombre")
    clasificar("hola")                       -> ("saludo", "hola")
    clasificar("¿quién ganó el último mundial?") -> ("ajeno", "ajeno")
    clasificar("hola, quiero poner una heladería en Tlalpan") -> None   (trae señales de negocio)
    texto_fijo("nombre")                     -> «No sé cómo te llamas: solo contesto dónde conviene poner un negocio...»
    sin_funciones_internas("... usa sugerir_giros(municipio='X') ...") -> texto sin esas frases

Criterio: una pregunta es fuera de tema solo si coincide con un patrón ajeno (su nombre, un saludo, deportes, noticias, clima,
chistes, código, preguntas personales, temas generales) Y no trae ninguna señal de negocio: un giro del catálogo o su sinónimo,
un municipio o una colonia reconocidos, o palabras como negocio, poner, abrir, zona, competencia, ingreso, economía, dólar...
Una pregunta sin ningún patrón ajeno nunca es fuera de tema (con historial, un seguimiento corto como «¿y en Polanco?» o
«¿qué me recomiendas?» sigue su camino normal). Los saludos y cortesías solo cuentan si el mensaje no trae nada más.
El historial no se usa para decidir: una señal de negocio en un turno anterior no vuelve de negocio una pregunta que trae un
patrón ajeno y ninguna señal propia.
"""
from __future__ import annotations

import re

from app import herramientas as H
from app import rag

TIPOS = ("saludo", "nombre", "ajeno")

BASE = ("dónde conviene poner un negocio en la Zona Metropolitana del Valle de México, con datos de INEGI, DENUE, ENIGH, CONAPO y Banxico")
PRUEBA = "Prueba con «quiero poner una heladería en Coyoacán» o «¿qué negocio pongo en Tlalpan?»."

# primera frase de cada subtipo; el resto es igual en todos (qué sí contesta y un ejemplo)
_TEXTOS = {
    "tu_nombre": f"No sé cómo te llamas: solo contesto {BASE}. {PRUEBA}",
    "ajeno": f"De eso no sé: solo contesto {BASE}. {PRUEBA}",
    "hola": f"¡Hola! Aquí solo contesto {BASE}. {PRUEBA}",
    "gracias": f"¡Con gusto! Recuerda que solo contesto {BASE}. {PRUEBA}",
    "adios": f"¡Hasta luego! Cuando quieras volver, solo contesto {BASE}. {PRUEBA}",
    "estas": f"Bien, gracias. Aquí solo contesto {BASE}. {PRUEBA}",
    "ok": f"Perfecto. Cuando quieras, solo contesto {BASE}. {PRUEBA}",
    "presenta": f"Mucho gusto. Aquí solo contesto {BASE}. {PRUEBA}",
    "identidad": f"Soy un asistente local que solo contesta {BASE}. {PRUEBA}",
}
SUBTIPO_DE = {"tu_nombre": "nombre", "ajeno": "ajeno"}   # los demás subtipos son «saludo»
TEXTO_AJENO = _TEXTOS["ajeno"]


def texto_fijo(tipo: str, subtipo: str | None = None) -> str:
    """Respuesta fija (sin LLM) para un tipo de fuera de tema; `subtipo` afina la primera frase."""
    if subtipo in _TEXTOS and SUBTIPO_DE.get(subtipo, "saludo") == tipo:
        return _TEXTOS[subtipo]
    return {"nombre": _TEXTOS["tu_nombre"], "saludo": _TEXTOS["hola"]}.get(tipo, TEXTO_AJENO)


# ---------------------------------------------------------------- patrones (sobre el texto normalizado: minusculas, sin acentos ni signos)
def _rx(*partes: str) -> re.Pattern:
    return re.compile("|".join(partes))


NOMBRE = _rx(r"\bcomo me llamo\b", r"\bcual es mi nombre\b", r"\bsabes (?:como me llamo|mi nombre|quien soy)\b", r"\bquien soy\b",
             r"\bcomo me dicen\b")
IDENTIDAD = _rx(r"\bcomo te llamas\b", r"\bcual es tu nombre\b", r"\bquien eres\b", r"\bque eres\b", r"\bque puedes hacer\b",
                r"\bque sabes hacer\b", r"\bque haces\b", r"\bpara que sirves\b", r"\bquien te (?:creo|hizo|programo)\b",
                r"^(?:ayuda|ayudame|necesito ayuda)$")
PRESENTA = re.compile(r"^(?:hola )?(?:me llamo|mi nombre es)(?: \w+){1,3}$")

AJENO = _rx(
    # deportes
    r"\b(?:futbol|soccer|mundial(?:es)?|liga mx|champions|nfl|nba|mlb|formula 1|tenis|boxeo|olimpiadas?|olimpicos|marcador|"
    r"campeonato|playoffs?|seleccion mexicana|chivas|cruz azul|tigres|rayados|real madrid|messi|checo perez|quien gano|"
    r"gano el (?:partido|juego|mundial|campeonato)|partido de (?:futbol|ayer|hoy|anoche)|goles?)\b",
    # noticias y politica
    r"\b(?:noticias?|ultima hora|que paso (?:hoy|ayer)|titulares|presidente|presidenta|sheinbaum|trump|amlo|lopez obrador|"
    r"elecciones|congreso|senado|diputados?|guerra|ucrania|gaza|israel|terremoto|sismo|huracan|temblor)\b",
    # clima
    r"\b(?:clima|va a llover|llover|lluvia|llueve|temperatura|pronostico|hace (?:calor|frio)|que tiempo hace|nublado|soleado)\b",
    # chistes y entretenimiento
    r"\b(?:chistes?|cuentame (?:un|una|algo)|hazme reir|adivinanza|acertijo|poema|poesia|cancion|canciones|pelicula|peliculas|"
    r"netflix|musica|videojuego|horoscopo|signo zodiacal|memes?)\b",
    # codigo
    r"\b(?:python|javascript|typescript|java|html|css|sql|react|codigo(?! postal)|script|programacion|compilar)\b",
    r"\b(?:escribe|escribeme|dame|hazme|genera|crea|programa|programame)\s+(?:un |una |el |la )?(?:codigo|script|programa|funcion|"
    r"clase|pagina|app|aplicacion|bot|algoritmo|query)\b",
    # preguntas personales (al asistente o sobre la persona)
    r"\b(?:cuantos anos tienes|que edad tienes|cuantos anos tengo|eres (?:un |una )?(?:robot|humano|persona|real|hombre|mujer|"
    r"chatgpt|gpt|inteligente|feliz|bueno|tonto)|estas casado|tienes (?:novia|novio|familia|hijos|hermanos|sentimientos|miedo|"
    r"mascota)|te gusta|cual es tu (?:color|comida|cancion|pelicula|equipo|signo|animal)|como te sientes|de donde eres|donde vives|"
    r"cuentame de ti|hablame de ti|te quiero|te amo|quieres ser mi (?:amigo|novio|novia)|que (?:hora|dia|fecha) es(?: hoy)?$|"
    r"fecha de hoy|en que ano estamos|cual es mi (?:color|comida|cancion|pelicula|equipo|signo|animal|edad|apellido|cumpleanos|"
    r"numero|direccion|telefono|correo)|de donde soy|^(?:sabes )?donde vivo$|cuando es mi cumpleanos)\b",
    # temas generales
    r"\b(?:capital de(?! trabajo| arranque| inicial| semilla)|quien (?:fue|descubrio|invento|escribio|pinto|compuso|era)|cuanto es \d|cuanto mide|como se dice|traduce|"
    r"traduceme|receta|recetas|como cocinar|dolor de|ecuacion|derivada|resuelve|sentido de la vida|tarea de|donde comer|"
    r"que comer|que cenar)\b",
)

# saludos y cortesias: solo cuentan si el mensaje no trae nada mas que estas palabras
_FILLER = set("""hola holi holis holaa holaaa buenas buenos buen dias dia tardes tarde noches noche hey hello hi ey saludos que tal onda
hubo quiubo quihubo como estas esta estan te tu usted ustedes todo bien muy gracias mil muchas mucho por favor adios bye chao chau
hasta luego pronto manana nos vemos ok okay vale perfecto excelente genial entendido de acuerdo listo amigo amiga asistente bot
me puedes podrias puede podria ayudar ayudas ayudarme ayuda un una poco momento oye disculpa perdon y quiero preguntar algo saber
si claro sale nada con gusto igualmente tambien va""".split())
_GRACIAS = re.compile(r"\bgracias\b|\bte agradezco\b")
_ADIOS = re.compile(r"\badios\b|\bbye\b|\bchao\b|\bchau\b|\bhasta luego\b|\bhasta pronto\b|\bnos vemos\b")
_ESTAS = re.compile(r"\bcomo estas\b|\bcomo te va\b|\bcomo esta usted\b|\bque tal\b")
_OK = re.compile(r"\b(?:ok|okay|vale|perfecto|excelente|genial|entendido|de acuerdo|listo)\b")
_HOLA = re.compile(r"\b(?:hola\w*|holi\w*|buenas|buenos dias|buen dia|buenas tardes|buenas noches|hey|hello|hi|ey|saludos|"
                   r"que onda|que hubo|quiubo|quihubo)\b")


# ---------------------------------------------------------------- señales de negocio
SENALES = re.compile(
    r"\b(?:negocios?|poner|pongo|ponga|pondria|abrir|abro|abra|abriendo|apertura|aperturas|locales?|vender|vendo|ventas?|zonas?|"
    r"colonias?|ageb|agebs|competenc\w+|competidor\w*|clientes?|renta|rentas|rentar|ingresos?|ganan|ganancias?|utilidad|"
    r"economi\w+|inflacion|tasas?|banxico|dolar|dolares|tipo de cambio|tiie|inpc|remesas|consumo|inversion|barato|barata|ticket|"
    r"giros?|emprend\w+|empresas?|tiendas?|comercios?|sucursal|franquicia|ubicacion|municipios?|alcaldias?|zmvm|nse|decil|scian|"
    r"denue|inegi|enigh|conapo|censo|score|metodologia|fuentes?|datos|mapa|socioeconom\w+|gasto|gastos|rentab\w+|mercado|demanda|"
    r"oferta|precios?|costos?|credito|prestamo|poblacion|habitantes|banco de mexico|inaugur\w+|escuelas?|academias?)\b")


def _senal_de_negocio(pregunta: str, n: str) -> bool:
    """Giro del catalogo (o sinonimo), municipio o colonia reconocidos, o una palabra de negocio."""
    if SENALES.search(n):
        return True
    clave, frase = H._buscar_giro(pregunta)
    if clave:
        return True
    muns = rag.municipios_en(pregunta)
    if muns:
        return True
    try:
        from app import lugares
        cols = lugares.detectar(pregunta, muns, frase, None)
        return any(c.get("encontrada") for c in cols)
    except Exception:       # sin el indice de colonias solo se pierde esta señal
        return False


def _saludo(n: str) -> str | None:
    """Subtipo de saludo o cortesia si el mensaje no trae nada mas que eso; None si trae otra cosa."""
    if not n or any(t not in _FILLER for t in n.split()):
        return None
    for rx, sub in ((_GRACIAS, "gracias"), (_ADIOS, "adios"), (_ESTAS, "estas"), (_HOLA, "hola"), (_OK, "ok")):
        if rx.search(n):
            return sub
    return None


def clasificar(pregunta: str, historial: list[dict] | None = None) -> tuple[str, str] | None:
    """(tipo, subtipo) si la pregunta es fuera de tema; None si es de negocio (o no se sabe: sigue el camino normal)."""
    n = H.norm(pregunta or "")
    if not n:
        return None
    if (PRESENTA.search(n) or IDENTIDAD.search(n)) and not _senal_de_negocio(pregunta, n):   # revisor 2026-11-24: la señal gana
        return "saludo", "presenta" if PRESENTA.search(n) else "identidad"
    if n.startswith("y ") and any(_senal_de_negocio(m.get("content", ""), H.norm(m.get("content", ""))) for m in (historial or [])
                                  if isinstance(m, dict) and m.get("role") == "user"):
        return None     # «¿y para el mundial?» tras una pregunta de negocio es un seguimiento, no un tema ajeno
    if NOMBRE.search(n):
        return ("nombre", "tu_nombre") if not _senal_de_negocio(pregunta, n) else None
    if AJENO.search(n):
        return ("ajeno", "ajeno") if not _senal_de_negocio(pregunta, n) else None
    sub = _saludo(n)
    return ("saludo", sub) if sub else None


def tipo_fuera_de_tema(pregunta: str, historial: list[dict] | None = None) -> str | None:
    """«saludo», «nombre» o «ajeno» si la pregunta es fuera de tema; None si no."""
    c = clasificar(pregunta, historial)
    return c[0] if c else None


def respuesta(pregunta: str, historial: list[dict] | None = None) -> dict | None:
    """{tipo, subtipo, texto} con el texto fijo si la pregunta es fuera de tema; None si no."""
    c = clasificar(pregunta, historial)
    return {"tipo": c[0], "subtipo": c[1], "texto": texto_fijo(*c)} if c else None


# ---------------------------------------------------------------- red de seguridad: nada de funciones internas en el texto
FUNCIONES = ("perfil_giro", "recomendar_zonas", "ficha_zona", "sugerir_giros", "buscar_carpetas", "contexto_macro", "ficha_municipio")
INTERNO = re.compile(r"\b(?:" + "|".join(FUNCIONES) + r")\b|\b[a-zA-Z_][a-zA-Z0-9_]*\((?:[^()]*?\b[a-zA-Z_][a-zA-Z0-9_]*\s*=[^()]*)\)")
_FRASES = re.compile(r"(?<=[.!?;:…])\s+")
MIN_UTIL = 40     # letras que tiene que quedar para que el texto limpio sirva


def menciona_funciones(texto: str) -> bool:
    """El texto nombra una función interna del agente o escribe una llamada tipo f(x=...)."""
    return bool(INTERNO.search(texto or ""))


def sin_funciones_internas(texto: str, reemplazo: str | None = None) -> str:
    """Quita las frases que nombran funciones internas (perfil_giro, recomendar_zonas...) o escriben una llamada tipo f(x=...).
    Si no queda nada útil (menos de MIN_UTIL letras), regresa `reemplazo` (por omisión, el texto fijo de tema ajeno)."""
    if not texto or not INTERNO.search(texto):
        return texto
    lineas = []
    for ln in texto.split("\n"):
        if not INTERNO.search(ln):
            lineas.append(ln)
            continue
        buenas = [f for f in _FRASES.split(ln) if f.strip() and not INTERNO.search(f)]
        if buenas and not re.match(r"^\s*(?:[-*]|\d+[.)])\s*$", " ".join(buenas)):
            pref = re.match(r"^\s*(?:[-*]\s+|\d+[.)]\s+)", ln)
            lineas.append((pref.group(0) if pref else "") + " ".join(b.strip() for b in buenas))
    limpio = re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()
    util = len(re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", re.sub(r"\*\*[^*]*\*\*:?", "", limpio)))
    return limpio if util >= MIN_UTIL else (reemplazo if reemplazo is not None else TEXTO_AJENO)
