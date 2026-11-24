"""Router de las vistas Preguntar y Ficha de zona del tablero.

Dueno: el constructor del grupo «preguntar».

    POST   /api/preguntas          {pregunta, historial?, rapido?} -> {id, estado, datos, herramientas, ...}
                                   Al instante (~3 s): corre agente.pre_consulta() y herramientas.ejecutar() de cada
                                   paso y regresa sus resultados ya armados para pintar (zonas, perfil, fuera de alcance).
                                   Despues, en un hilo de UNA sola cola (un LLM a la vez), agente.responder().
                                   rapido=true, o Ollama apagado: el texto sale de agente.plantilla(), sin LLM.
                                   Fuera de tema («¿cómo me llamo?», «hola», deportes): sin herramientas ni LLM, texto fijo
                                   (app/fuera_de_tema.py); regresa fuera_de_tema: true y tipo_fuera_de_tema: saludo|nombre|ajeno
                                   (arriba y dentro de `datos`), datos.zonas = [] y sin mapa. Cada pregunta se anota en
                                   data/historial/preguntas.jsonl (app/historial.py; `make historial` lo muestra).
    GET    /api/preguntas/{id}[?completo=1]  (completo=1 agrega `datos`, para reabrir el hilo guardado en el navegador)
                                   {estado: en_cola|pensando|listo|error|cancelada, posicion_en_cola, segundos, respuesta,
                                    herramientas:[{nombre,args,resultado}], latencia_s, modo, modelo, ...}
    DELETE /api/preguntas/{id}     cancela una pregunta que sigue en cola (la que ya esta pensando no se interrumpe)
    GET    /api/zona/{cvegeo}?giro=  ficha de una AGEB: herramientas.ficha_zona + piramide, vivienda, escolaridad,
                                   marginacion, decil, empleo por sector a 500 m y 1 km, transporte y vecinas para el mapa
    GET    /api/buscar_zona?q=&municipio=   colonias o AGEB que coinciden (para el buscador de la Ficha)

Todo lo calcula app/herramientas.py y app/motor.py (validados); aqui solo se ordena y se sanea para JSON.
Los numeros de cada bloque llevan su `fuente` en el mismo objeto: nada se escribe a mano en el frontend.
"""
from __future__ import annotations

import difflib
import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache
from math import isfinite

import numpy as np
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import agente, historial as registro
from app import fuera_de_tema as fuera
from app import herramientas as H
from app import motor
from app.api import base

router = APIRouter(prefix="/api", tags=["preguntar"])
NO = "NO ENCONTRADO"


# ---------------------------------------------------------------- saneo para JSON
def _limpio(o):
    """NaN, inf y tipos de numpy a algo que json acepta (starlette no admite NaN)."""
    if isinstance(o, dict):
        return {str(k): _limpio(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [_limpio(v) for v in o]
    if isinstance(o, np.generic):
        o = o.item()
    if isinstance(o, float):
        return o if isfinite(o) else None
    return o


def _error(estado: int, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=estado, content={"error": mensaje})


def _giro_visible(clave: str | None) -> dict | None:
    if not clave:
        return None
    for g in base._giros_lista():
        if g["clave"] == clave:
            return {"clave": clave, "nombre": g["nombre"]}
    return {"clave": clave, "nombre": clave.replace("_", " ").capitalize()}


def _fuente_denue() -> str:
    return f"DENUE corte {base.cortes().get('denue_actual') or NO}"


# ---------------------------------------------------------------- datos que se pintan al instante
def _primero(usadas: list[dict], nombre: str, ok=lambda r: r.get("encontrado")) -> dict | None:
    for u in usadas:
        r = u.get("resultado")
        if u.get("nombre") == nombre and isinstance(r, dict) and ok(r):
            return r
    return None


def _zona_corta(z: dict) -> dict:
    """Lo que necesita una tarjeta de zona, de lo que ya calculo herramientas._zona."""
    claves = ("colonia", "municipio", "ageb", "score", "rank_zmvm", "prob_apertura_pct", "prob_sigue_abierto_pct",
              "gasto_potencial_trim_mxn", "competidores_ponderados", "captura_huff_pct", "complementarios_ponderados",
              "nse_estimado", "decil_estimado", "ingreso_trim_mediano_estimado_mxn", "edad_clave_etiqueta",
              "edad_clave_pct", "edad_clave_pct_zmvm", "poblacion_ageb_2020", "radio_m", "resumen_texto",
              "dist_a_colonia_km", "en_colonia_consultada")
    out = {k: z[k] for k in claves if k in z}
    out["colonia"] = _nombre_colonia(out.get("colonia")) or NO
    return out


def _mapa_de(clave: str, filtros: dict | None) -> dict:
    """Score de cada AGEB para el giro (el mapa de la respuesta) y, si hay filtro de municipio, su clave de 5 digitos."""
    s = motor.score_giro(clave)[["cvegeo", "score"]]
    valores = {cv: round(float(v)) for cv, v in zip(s["cvegeo"], s["score"]) if isfinite(float(v))}
    mun = None
    if filtros and filtros.get("municipio"):
        r = H.resolver_municipio(filtros["municipio"])
        mun = r.get("cvegeo_mun") if r.get("ok") else None
    return {"valores": valores, "municipio": mun}


def armar_datos(usadas: list[dict]) -> dict:
    """Resultados de las herramientas -> el objeto que pinta la vista Preguntar antes de que el LLM termine."""
    rz = _primero(usadas, "recomendar_zonas")
    perfil = _primero(usadas, "perfil_giro")
    sg = _primero(usadas, "sugerir_giros")
    macro = _primero(usadas, "contexto_macro", ok=lambda r: r.get("linea"))
    mun = _primero(usadas, "ficha_municipio")
    clave = (rz or perfil or {}).get("giro")
    datos: dict = {"giro": _giro_visible(clave), "zonas": [], "fuentes": agente.fuentes_de(usadas),
                   "corte_denue": base.cortes().get("denue_actual")}

    if perfil:
        datos["perfil"] = {k: perfil.get(k) for k in ("coincidencia", "ticket_promedio_mxn", "ticket_fuente", "radio_influencia_m",
                                                       "nse_objetivo", "cliente_objetivo_edades", "demanda_base", "notas", "aviso_rubro")}
    else:
        r = next((u["resultado"] for u in usadas if u["nombre"] == "perfil_giro" and isinstance(u["resultado"], dict)), None)
        if r and not r.get("encontrado"):
            datos["perfil_no_encontrado"] = {"motivo": r.get("motivo"), "propuestas_scian": (r.get("propuestas_scian") or [])[:3]}

    if rz:
        datos.update({
            "zonas": [_zona_corta(z) for z in rz.get("zonas", [])],
            "filtros": rz.get("filtros"), "agebs_evaluadas": rz.get("agebs_evaluadas"), "metodo": rz.get("metodo"),
            "como_leer_score": rz.get("como_leer_score"), "edad_clave": rz.get("edad_clave"),
            "aviso_prob_baja": rz.get("aviso_prob_baja"), "aviso_colonia": rz.get("aviso_colonia"),
            "avisos": [a for a in rz.get("avisos", []) if a != rz.get("aviso_prob_baja") and a != rz.get("aviso_colonia")],
            "fuentes_zonas": rz.get("fuentes", []),
        })
        try:
            datos["mapa"] = _mapa_de(rz["giro"], rz.get("filtros"))
        except Exception as e:  # sin mapa no se cae la respuesta
            datos["mapa"] = None
            datos["mapa_error"] = f"{type(e).__name__}: {e}"
    else:
        # fuera de alcance: la herramienta lo dice con fuera_de_zmvm, o el municipio no existe
        for u in usadas:
            r = u.get("resultado")
            if u["nombre"] == "recomendar_zonas" and isinstance(r, dict) and not r.get("encontrado"):
                datos["fuera_de_alcance"] = {"fuera_de_zmvm": bool(r.get("fuera_de_zmvm")), "motivo": r.get("motivo") or NO,
                                             "sugerencias": r.get("sugerencias") or []}
                break
        else:
            r0 = next((u["resultado"] for u in usadas if isinstance(u.get("resultado"), dict) and u["resultado"].get("fuera_de_zmvm")), None)
            if r0:
                datos["fuera_de_alcance"] = {"fuera_de_zmvm": True, "motivo": r0.get("motivo") or NO, "sugerencias": []}

    if sg:
        datos["sugerencias"] = [{**g, "nombre": (_giro_visible(g["giro"]) or {}).get("nombre")} for g in sg.get("giros", [])]
        datos["sugerencias_como_leer"] = sg.get("como_leer")
        datos["sugerencias_filtros"] = sg.get("filtros")
    if macro:
        datos["macro"] = {"linea": macro["linea"], "fuentes": agente.unir_fuentes(macro.get("fuentes", []))}
    if mun:
        datos["municipio"] = {"nombre": mun.get("municipio"), "ficha": mun.get("ficha", [])[:3], "fuentes": mun.get("fuentes", [])}
    # los textos que la vista pinta tal cual pasan por el mismo pulido es-MX que la respuesta de plantilla
    for k in ("avisos",):
        if datos.get(k):
            datos[k] = [_pulir_texto(a) if isinstance(a, str) else a for a in datos[k]]
    for d, k in ((datos.get("macro"), "linea"), (datos.get("fuera_de_alcance"), "motivo"), (datos.get("perfil"), "aviso_rubro"),
                 (datos, "sugerencias_como_leer")):
        if d and isinstance(d.get(k), str):
            d[k] = _pulir_texto(d[k])
    if datos.get("municipio"):
        datos["municipio"]["ficha"] = [_pulir_texto(x) if isinstance(x, str) else x for x in datos["municipio"]["ficha"]]
    return datos


# ---------------------------------------------------------------- trabajos (pregunta -> respuesta del LLM)
@dataclass
class Trabajo:
    id: str
    pregunta: str
    historial: list[dict]
    rapido: bool
    usadas: list[dict]
    datos: dict
    estado: str = "en_cola"          # en_cola | pensando | listo | error | cancelada
    t_creado: float = field(default_factory=time.time)
    t_inicio: float | None = None
    t_fin: float | None = None
    respuesta: str | None = None
    herramientas: list[dict] | None = None
    latencia_s: float | None = None
    modo: str | None = None          # llm | rapido | plantilla
    modelo: str | None = None
    aviso: str | None = None
    error: str | None = None
    detalle: dict | None = None
    fuera_de_tema: bool = False
    tipo_fuera_de_tema: str | None = None   # saludo | nombre | ajeno


_trabajos: dict[str, Trabajo] = {}
_cola: list[str] = []                 # ids que esperan o estan pensando, en orden de llegada (el primero es el que corre)
_candado = threading.RLock()          # protege _trabajos y _cola
_candado_pre = threading.Lock()       # la pre-consulta carga el motor: una a la vez (la Mac tiene poca RAM)
_hilo: ThreadPoolExecutor | None = None
MAX_TRABAJOS = 120


def _ejecutor() -> ThreadPoolExecutor:
    global _hilo
    with _candado:
        if _hilo is None:
            _hilo = ThreadPoolExecutor(max_workers=1, thread_name_prefix="llm")  # un LLM a la vez
        return _hilo


def _datos_fuera_de_tema(tipo: str) -> dict:
    """`datos` de una pregunta fuera de tema: sin giro, sin zonas (lista vacia), sin mapa ni resaltado."""
    return {**armar_datos([]), "fuera_de_tema": True, "tipo_fuera_de_tema": tipo}


def _registrar(t: Trabajo) -> None:
    """Anota la pregunta en data/historial/preguntas.jsonl (si falla, la respuesta no se rompe)."""
    try:
        registro.registrar(t.pregunta, t.historial, t.modo or ("rapido" if t.rapido else "llm"), t.fuera_de_tema,
                           t.herramientas if t.herramientas is not None else t.usadas, t.respuesta, t.latencia_s,
                           t.tipo_fuera_de_tema, fecha=t.t_creado)
    except Exception:
        pass


def _hay_modelo() -> bool:
    """Ollama prendido y con el modelo del agente descargado."""
    est = base.estado_ollama()
    if not est.get("prendido"):
        return False
    return any(m == agente.MODELO or m.startswith(agente.MODELO + ":") for m in est.get("modelos", []))


def _pulir_texto(texto: str) -> str:
    """Retoques es-MX al texto de agente.plantilla() sin tocar el agente: millares con coma, acentos que faltan, «48%» sin espacio
    (como las tarjetas) e identificadores internos con su nombre en español."""
    texto = fuera.sin_funciones_internas(texto)   # red de seguridad: nada de perfil_giro, sugerir_giros(...) en lo que ve la persona
    texto = re.sub(r"(?<![\d.,])(\d{4,})(?= millones de dólares)", lambda m: f"{int(m.group(1)):,}", texto)
    for a, b in (("esta fuera de la Zona Metropolitana del Valle de Mexico", "está fuera de la Zona Metropolitana del Valle de México"),
                 ("Cafe_bebidas de la ENIGH", "El rubro «café y bebidas» de la ENIGH"),
                 ("cafe_bebidas de la ENIGH", "el rubro «café y bebidas» de la ENIGH"), ("ali_fuera_total", "«alimentos fuera del hogar»")):
        texto = texto.replace(a, b)
    return re.sub(r"(\d) %", r"\1%", texto)


def _texto_plantilla(usadas: list[dict], pregunta: str = "", herencia: dict | None = None) -> str:
    """Respuesta sin LLM. Con la pregunta trae lo mismo que fuera del tablero («Ingreso en X», «Cómo influye»)."""
    texto = _pulir_texto(agente.plantilla(usadas, herencia, pregunta))
    fu = agente.fuentes_de(usadas)
    if fu and "**Fuentes:**" not in texto:
        texto += "\n\n**Fuentes:** " + "; ".join(fu) + "."
    return texto


def _correr(t: Trabajo) -> None:
    """Hilo de la cola: una pregunta a la vez contra Ollama."""
    with _candado:
        if t.estado == "cancelada":
            return
        t.estado, t.t_inicio = "pensando", time.time()
    try:
        out = agente.responder(t.pregunta, t.historial)
        with _candado:
            t.respuesta = fuera.sin_funciones_internas(out.get("respuesta") or "")
            t.herramientas = out.get("herramientas") or t.usadas
            t.latencia_s = out.get("latencia_s")
            t.modo = "plantilla" if out.get("modo") == "plantilla" else "llm"
            t.modelo = out.get("modelo")
            t.detalle = {k: out.get(k) for k in ("rondas", "herencia", "cortada", "metricas")}
            if t.modo == "plantilla":
                t.aviso = "Ollama no respondió: la respuesta se armó sin el modelo de lenguaje, con los mismos datos."
            t.estado = "listo"
    except Exception as e:
        with _candado:
            t.estado, t.error = "error", f"{type(e).__name__}: {e}"
    finally:
        with _candado:
            t.t_fin = time.time()
            if t.id in _cola:
                _cola.remove(t.id)
        _registrar(t)


def _podar() -> None:
    """Deja solo los ultimos trabajos terminados (memoria acotada). Llamar con el candado tomado."""
    if len(_trabajos) <= MAX_TRABAJOS:
        return
    hechos = sorted((t for t in _trabajos.values() if t.estado in ("listo", "error", "cancelada")), key=lambda t: t.t_creado)
    for t in hechos[: len(_trabajos) - MAX_TRABAJOS]:
        _trabajos.pop(t.id, None)


def _historial_limpio(h) -> list[dict]:
    out = []
    for m in (h or [])[-8:]:
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str) and m["content"].strip():
            out.append({"role": m["role"], "content": m["content"][:4000]})
    return out


class Pregunta(BaseModel):
    pregunta: str
    historial: list[dict] | None = None
    rapido: bool = False


def _vista(t: Trabajo) -> dict:
    """Estado publico de un trabajo. posicion_en_cola = cuantas preguntas van antes (0 = esta es la que el modelo contesta)."""
    ahora = time.time()
    with _candado:
        if t.estado == "en_cola":
            pos = _cola.index(t.id) if t.id in _cola else 0
            seg = ahora - t.t_creado
        elif t.estado == "pensando":
            pos, seg = 0, ahora - (t.t_inicio or ahora)
        else:
            pos, seg = 0, (t.t_fin or ahora) - (t.t_inicio or t.t_creado)
        out = {"id": t.id, "estado": t.estado, "posicion_en_cola": pos, "segundos": round(seg, 1), "pregunta": t.pregunta,
               "respuesta": t.respuesta, "latencia_s": t.latencia_s, "modo": t.modo, "modelo": t.modelo, "aviso": t.aviso, "error": t.error,
               "herramientas": t.herramientas if t.herramientas is not None else t.usadas, "detalle": t.detalle,
               "fuera_de_tema": t.fuera_de_tema, "tipo_fuera_de_tema": t.tipo_fuera_de_tema}
        out["fuentes"] = agente.fuentes_de(out["herramientas"])
    return _limpio(out)


@router.post("/preguntas")
def crear_pregunta(cuerpo: Pregunta):
    pregunta = (cuerpo.pregunta or "").strip()
    if len(pregunta) < 2:
        return _error(422, "Escribe tu pregunta (por ejemplo: «quiero poner una heladería»).")
    if len(pregunta) > 600:
        return _error(422, "La pregunta es muy larga (máximo 600 caracteres).")
    historial = _historial_limpio(cuerpo.historial)
    t0 = time.time()
    ft = agente.fuera_de_tema(pregunta, historial or None)
    if ft:      # sin herramientas ni LLM: texto fijo, sin zonas ni mapa
        datos = _datos_fuera_de_tema(ft["tipo"])
        t = Trabajo(id=uuid.uuid4().hex[:12], pregunta=pregunta, historial=historial, rapido=bool(cuerpo.rapido), usadas=[], datos=datos,
                    fuera_de_tema=True, tipo_fuera_de_tema=ft["tipo"])
        t.respuesta, t.herramientas = ft["texto"], []
        t.modo = "rapido" if t.rapido else "plantilla"
        t.latencia_s = round(time.time() - t0, 1)
        t.estado, t.t_inicio, t.t_fin = "listo", t0, time.time()
        with _candado:
            _trabajos[t.id] = t
            _podar()
        _registrar(t)
        return _limpio({**_vista(t), "datos": datos, "segundos_consulta": round(time.time() - t0, 1), "ollama": _hay_modelo()})
    try:
        with _candado_pre:
            plan = agente.pre_consulta(pregunta, historial or None)
            usadas = [{"nombre": n, "args": a, "resultado": H.ejecutar(n, a)} for n, a in plan]
            datos = armar_datos(usadas)
    except Exception as e:
        return _error(500, f"No pude consultar las herramientas: {type(e).__name__}: {e}")
    t = Trabajo(id=uuid.uuid4().hex[:12], pregunta=pregunta, historial=historial, rapido=bool(cuerpo.rapido), usadas=usadas, datos=datos)
    ollama = _hay_modelo()
    if t.rapido or not ollama:
        t.respuesta = _texto_plantilla(usadas, t.pregunta)
        t.herramientas = usadas
        t.modo = "rapido" if t.rapido else "plantilla"
        t.latencia_s = round(time.time() - t0, 1)
        if not t.rapido:
            t.aviso = "Ollama está apagado o le falta el modelo: la respuesta se armó sin el modelo de lenguaje, con los mismos datos."
        t.estado, t.t_inicio, t.t_fin = "listo", t0, time.time()
        with _candado:
            _trabajos[t.id] = t
            _podar()
        _registrar(t)
    else:
        with _candado:
            _trabajos[t.id] = t
            _cola.append(t.id)
            _podar()
        _ejecutor().submit(_correr, t)
    return _limpio({**_vista(t), "datos": datos, "segundos_consulta": round(time.time() - t0, 1), "ollama": ollama})


@router.get("/preguntas/{pid}")
def leer_pregunta(pid: str, completo: bool = False):
    """Estado del trabajo. Con completo=1 trae ademas `datos` (zonas, mapa...), para reabrir una pregunta guardada en el navegador."""
    t = _trabajos.get(pid)
    if not t:
        return _error(404, "Esa pregunta ya no está en el servidor (se reinició o se borró). Vuelve a enviarla.")
    v = _vista(t)
    return _limpio({**v, "datos": t.datos}) if completo else v


@router.delete("/preguntas/{pid}")
def cancelar_pregunta(pid: str):
    t = _trabajos.get(pid)
    if not t:
        return _error(404, "Esa pregunta ya no está en el servidor.")
    cancelada = False
    with _candado:
        if t.estado == "en_cola":
            t.estado, t.t_fin = "cancelada", time.time()
            cancelada = True
            if t.id in _cola:
                _cola.remove(t.id)
    if cancelada:
        _registrar(t)
    return _vista(t)


# ---------------------------------------------------------------- ficha de zona
SECTORES = {  # SCIAN 2023, sector de 2 digitos (31-33 manufacturas va junto)
    "11": "Agricultura y pesca", "21": "Minería", "22": "Energía y agua", "23": "Construcción", "31": "Industria manufacturera",
    "43": "Comercio al por mayor", "46": "Comercio al por menor", "48": "Transportes y almacenamiento", "51": "Medios e información",
    "52": "Finanzas y seguros", "53": "Inmobiliarios y alquiler", "54": "Servicios profesionales y técnicos", "55": "Corporativos",
    "56": "Apoyo a negocios y residuos", "61": "Servicios educativos", "62": "Salud y asistencia social",
    "71": "Cultura, deporte y esparcimiento", "72": "Restaurantes y hoteles", "81": "Otros servicios", "93": "Gobierno y justicia",
}
F_CENSO = "Censo 2020 INEGI, resultados por AGEB urbana"
F_CONAPO = "CONAPO, índice de marginación urbana 2020"
F_ENIGH = "ENIGH 2024 INEGI; decil por AGEB estimado por el proyecto (modelo propio)"
F_TRANSP = "datos.cdmx.gob.mx (Metro, Metrobús, STE, GTFS) y OpenStreetMap; afluencia del Metro 2025"
GRADOS = ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"]


@lru_cache(maxsize=1)
def _promedios_zmvm() -> dict:
    """Promedios de la ZMVM (ponderados por poblacion o viviendas), para comparar cada AGEB."""
    f = motor.cargar_features()
    pob = f["pob_total"].sum()
    p15 = (f["pob_15_64"] + f["pob_65_mas"]).fillna(0)

    def ponderado(col, w):
        m = f[col].notna()
        return float((f.loc[m, col] * w[m]).sum() / w[m].sum())

    deciles = [float((f[f"p_decil_{i:02d}"] * f["hogares"]).sum() / f["hogares"].sum()) for i in range(1, 11)]
    grados = f["gm_2020"].value_counts()
    return {
        "edades": {"0-14": float(100 * f["pob_0_14"].sum() / pob), "15-24": float(100 * f["pob_15_24"].sum() / pob),
                   "25-59": float(100 * f["pob_25_59"].sum() / pob), "60+": float(100 * f["pob_60_mas"].sum() / pob)},
        "vivienda": {c: ponderado(c, f["viviendas_habitadas"]) for c in ("pct_viv_auto", "pct_viv_internet", "pct_viv_pc", "pct_viv_celular")},
        "escolaridad": ponderado("escolaridad_prom", p15),
        "deciles": deciles,
        "grados": {g: int(grados.get(g, 0)) for g in GRADOS}, "n_agebs": int(len(f)), "n_con_grado": int(grados.sum()),
    }


def _r(x, nd=1):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return round(x, nd) if isfinite(x) else None


def _r0(x):
    v = _r(x, 0)
    return int(v) if v is not None else None


def _vecinas(f, row, clave: str | None, km: float = 2.5) -> dict:
    """AGEB a <= km de la elegida con su valor (score del giro o decil): el mapa chico de la ficha las pinta."""
    lat0, lon0 = float(row["lat"]), float(row["lon"])
    dy = (f["lat"] - lat0) * 111.32
    dx = (f["lon"] - lon0) * 111.32 * np.cos(np.radians(lat0))
    cerca = f[(dx ** 2 + dy ** 2) <= km ** 2]
    if clave:
        s = motor.score_giro(clave).set_index("cvegeo")["score"]
        v = s.reindex(cerca.index)
        return {"valores": {cv: round(float(x)) for cv, x in v.items() if isfinite(float(x))}, "dominio": [0, 100],
                "etiqueta": f"Score de {(_giro_visible(clave) or {}).get('nombre', clave).lower()} (0–100)", "radio_km": km,
                "fuente": "modelo propio (score por giro, DENUE, Censo 2020 INEGI)"}
    v = cerca["decil_imputado"].astype("float64")  # Int64 con NA -> float con NaN
    return {"valores": {cv: int(x) for cv, x in v.items() if isfinite(x)}, "dominio": [1, 10],
            "etiqueta": "Decil de ingreso estimado (1–10)", "radio_km": km, "fuente": F_ENIGH}


@router.get("/zona/{cvegeo}")
def ficha(cvegeo: str, giro: str | None = None):
    z = (cvegeo or "").strip().upper()
    f = motor.cargar_features()
    if z not in f.index:
        return _error(404, f"{NO}: la AGEB {z} no está en el modelo (solo las 5,875 AGEB urbanas de la ZMVM).")
    clave = H._resolver_giro(giro) if giro else None
    base_ficha = H.ficha_zona(z, giro=clave)
    if not base_ficha.get("encontrado"):
        return _error(404, base_ficha.get("motivo") or NO)
    row = f.loc[z]
    prom = _promedios_zmvm()
    pob = float(row["pob_total"]) if isfinite(float(row["pob_total"])) else 0.0

    etiquetas = {"0-14": "0 a 14 años", "15-24": "15 a 24 años", "25-59": "25 a 59 años", "60+": "60 años o más"}
    col = {"0-14": "pob_0_14", "15-24": "pob_15_24", "25-59": "pob_25_59", "60+": "pob_60_mas"}
    edades = [{"grupo": k, "etiqueta": etiquetas[k], "personas": _r0(row[col[k]]),
               "pct": _r(100 * row[col[k]] / pob, 1) if pob else None, "pct_zmvm": _r(prom["edades"][k], 1)} for k in etiquetas]

    nombres_viv = {"pct_viv_auto": "Con automóvil", "pct_viv_internet": "Con internet", "pct_viv_pc": "Con computadora", "pct_viv_celular": "Con celular"}
    vivienda = [{"clave": c, "etiqueta": n, "pct": _r(row[c], 1), "pct_zmvm": _r(prom["vivienda"][c], 1)} for c, n in nombres_viv.items()]

    p_dec = [_r(100 * row[f"p_decil_{i:02d}"], 1) for i in range(1, 11)]
    marg = {"grado": base_ficha.get("grado_marginacion_conapo_2020"), "indice": _r(row["im_2020"], 1), "indice_normalizado": _r(row["imn_2020"], 3),
            "grados_zmvm": [{"grado": g, "agebs": prom["grados"][g]} for g in GRADOS], "n_agebs": prom["n_con_grado"],
            "sin_grado": prom["n_agebs"] - prom["n_con_grado"]}

    sectores = {}
    for cod, nombre in SECTORES.items():
        cods = ["31", "32", "33"] if cod == "31" else [cod]
        n5 = sum(float(row.get(f"sec{c}_500m", 0) or 0) for c in cods)
        n1 = sum(float(row.get(f"sec{c}_1km", 0) or 0) for c in cods)
        if n5 or n1:
            sectores[cod] = {"clave": cod, "nombre": nombre, "n_500m": _r0(n5), "n_1km": _r0(n1)}
    empleo = {"sectores": sorted(sectores.values(), key=lambda s: -(s["n_1km"] or 0)),
              "negocios_500m": _r0(row["estab_500m"]), "negocios_1km": _r0(row["estab_1km"]),
              "empleos_500m": _r0(row["empleo_500m"]), "empleos_1km": _r0(row["empleo_1km"]),
              "negocios_en_ageb": _r0(row["n_establecimientos"]), "empleos_en_ageb": _r0(row["pob_diurna"]),
              "escuelas_1km": _r0(row["n_escuelas_1km"]), "hospitales_1km": _r0(row["n_hospitales_1km"]), "plazas_1km": _r0(row["n_plazas_1km"]),
              "fuente": f"{_fuente_denue()} (negocios por sector SCIAN; empleo = personal ocupado, punto medio del estrato)"}

    def txt(c):
        v = row.get(c)
        return v if isinstance(v, str) and v else None

    transporte = {"estacion": txt("estacion_cercana"), "sistema": txt("sistema_estacion"), "distancia_m": _r0(row["dist_estacion_m"]),
                  "metro": txt("metro_cercano"), "distancia_metro_m": _r0(row["dist_metro_m"]),
                  "afluencia_metro_anual": _r0(row["afluencia_metro_cercano"]), "estaciones_1km": _r0(row["n_estaciones_1km"]),
                  "fuente": F_TRANSP}

    dec = base_ficha.get("decil_estimado")
    out = {
        "encontrado": True, "ageb": z, "colonia": _nombre_colonia(base_ficha.get("colonia")), "municipio": base_ficha.get("municipio"), "cvegeo_mun": z[:5],
        "tipo_asentamiento": txt("tipo_asentamiento"), "cp": txt("cp_modal"), "colonia_fuente": base_ficha.get("colonia_fuente"),
        "lat": _r(row["lat"], 5), "lon": _r(row["lon"], 5),
        "poblacion": {"habitantes": _r0(row["pob_total"]), "hogares": _r0(row["hogares"]), "viviendas": _r0(row["viviendas_habitadas"]),
                      "ocupantes_por_vivienda": _r(row["prom_ocupantes"], 2), "densidad_hab_km2": _r0(row["densidad_hab_km2"]),
                      "area_km2": _r(row["area_km2"], 3), "fuente": F_CENSO},
        "edades": {"grupos": edades, "fuente": F_CENSO + "; promedio de la ZMVM = las 5,875 AGEB"},
        "vivienda": {"bienes": vivienda, "fuente": F_CENSO + "; promedio de la ZMVM ponderado por viviendas habitadas"},
        "escolaridad": {"anios": _r(row["escolaridad_prom"], 1), "anios_zmvm": _r(prom["escolaridad"], 1),
                        "fuente": F_CENSO + "; promedio de la ZMVM ponderado por población de 15 años o más"},
        "marginacion": {**marg, "fuente": F_CONAPO},
        "ingreso": {"decil": dec if isinstance(dec, (int, float)) else None, "nse": txt("nse"), "ingreso_trim_mediano": _r(row["ing_trim_mediano_est"], -2),
                    "prob_deciles_pct": p_dec, "prob_deciles_zmvm_pct": [_r(100 * x, 1) for x in prom["deciles"]],
                    "prob_nse_pct": {k: _r(100 * row[f"p_nse_{k}"], 1) for k in ("bajo", "medio", "alto")},
                    "fuente": F_ENIGH},
        "empleo": empleo,
        "transporte": transporte,
        "fuentes": base_ficha.get("fuentes", []),
    }
    g = base_ficha.get("giro")
    if g:
        n = int(g.get("de_agebs") or len(f))
        rank = int(g["rank_zmvm"])
        out["giro"] = {**g, "nombre": (_giro_visible(clave) or {}).get("nombre"), "percentil": _r(100 * (n - rank) / max(n - 1, 1), 1),
                       "en_top_5": rank <= 5,
                       "fuente": "modelo propio (score por giro); Censo 2020 INEGI; " + _fuente_denue() + "; ENIGH 2024"}
    elif giro:
        out["giro_no_encontrado"] = giro
    try:
        out["vecinas"] = _vecinas(f, row, clave if g else None)
    except Exception as e:
        out["vecinas"] = None
        out["vecinas_error"] = f"{type(e).__name__}: {e}"
    return _limpio(out)


# ---------------------------------------------------------------- buscador de colonias
@lru_cache(maxsize=1)
def _indice_colonias():
    f = motor.cargar_features()
    d = f[["nom_colonia", "nom_mun", "pob_total", "cve_ent", "cve_mun"]].copy()
    d["nom_colonia"] = d["nom_colonia"].fillna("").astype(str)
    d["norm"] = d["nom_colonia"].map(H.norm)
    d["cvegeo_mun"] = d["cve_ent"].astype(str) + d["cve_mun"].astype(str)
    d["cvegeo"] = d.index
    return d


def precalentar() -> None:
    """Calienta lo que la Ficha pide primero (features, promedios de la ZMVM e indice del buscador)."""
    try:
        _promedios_zmvm()
        _indice_colonias()
    except Exception:
        pass


_MENORES = {"de", "del", "la", "las", "el", "los", "y", "e", "en", "a", "al", "con", "por"}
_ROMANOS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv"}
_SIGLAS = {"ctm", "imss", "issste", "sct", "unam", "uam", "fovissste", "infonavit", "cdmx", "pemex"}


def _nombre_colonia(c) -> str | None:
    """«POLANCO III SECCIÓN» -> «Polanco III Sección» (el DENUE y el Censo escriben los nombres en mayúsculas)."""
    if not isinstance(c, str) or not c:
        return None
    if not c.isupper():
        return c
    out = []
    for i, p in enumerate(c.lower().split(" ")):
        if p in _ROMANOS or p in _SIGLAS:
            out.append(p.upper())
        elif "-" in p and p.split("-")[0] in _ROMANOS:  # «ix-a» -> «IX-A»
            out.append(p.upper())
        else:
            out.append(p if i > 0 and p in _MENORES else p[:1].upper() + p[1:])
    return " ".join(out)


@router.get("/buscar_zona")
def buscar_zona(q: str = Query("", max_length=80), municipio: str | None = None, limite: int = Query(15, ge=1, le=40)):
    d = _indice_colonias()
    fuente = "Censo 2020 INEGI y DENUE (nombre de colonia por AGEB); modelo propio"
    cvmun = None
    if municipio:
        if re.fullmatch(r"\d{5}", municipio.strip()):
            cvmun = municipio.strip()
        else:
            r = H.resolver_municipio(municipio)
            if not r.get("ok") or not r.get("cvegeo_mun"):
                return {"q": q, "municipio": municipio, "resultados": [], "sugerencias": r.get("sugerencias", []), "fuente": fuente,
                        "motivo": f"{NO}: no encontré el municipio «{municipio}» en la ZMVM."}
            cvmun = r["cvegeo_mun"]
    if cvmun:
        d = d[d["cvegeo_mun"] == cvmun]
    texto = (q or "").strip()
    if len(texto) < 2 and not cvmun:
        return {"q": q, "municipio": municipio, "resultados": [], "sugerencias": [], "fuente": fuente,
                "motivo": "Escribe al menos 2 letras o elige un municipio."}
    por_clave = bool(re.fullmatch(r"\d{5,13}[0-9A-Za-z]*", texto))
    if por_clave:
        hit = d[d["cvegeo"].str.startswith(texto.upper())].assign(r=0)
    elif len(texto) >= 2:
        n = H.norm(texto)
        toks = n.split()
        hit = d[d["norm"].map(lambda s: all(t in s for t in toks))].copy() if toks else d.iloc[0:0].copy()
        hit = hit[hit["nom_colonia"] != ""]
        hit["r"] = np.where(hit["norm"] == n, 0, np.where(hit["norm"].str.startswith(n), 1, 2))
    else:  # solo municipio: las colonias mas pobladas
        hit = d[d["nom_colonia"] != ""].assign(r=0)
    resultados = []
    if len(hit):
        orden = sorted(hit.groupby(["nom_colonia", "nom_mun", "cvegeo_mun"], sort=False),
                       key=lambda kv: (int(kv[1]["r"].min()), -float(kv[1]["pob_total"].sum())))
        for (c, m, cm), g in orden[:limite]:
            g = g.sort_values("pob_total", ascending=False)
            resultados.append({"colonia": _nombre_colonia(c) or "Sin nombre", "municipio": m, "cvegeo_mun": cm, "n_agebs": int(len(g)),
                               "habitantes": _r0(g["pob_total"].sum()),
                               "agebs": [{"cvegeo": cv, "habitantes": _r0(p)} for cv, p in zip(g["cvegeo"].head(8), g["pob_total"].head(8))]})
    sug = []
    if not resultados and len(texto) >= 3 and not por_clave:
        nombres = sorted(set(_indice_colonias()["norm"]) - {""})
        sug = [s.title() for s in difflib.get_close_matches(H.norm(texto), nombres, n=4, cutoff=0.7)]
    return _limpio({"q": q, "municipio": municipio, "resultados": resultados, "sugerencias": sug, "fuente": fuente,
                    "motivo": None if resultados else f"{NO}: ninguna colonia o AGEB coincide con «{texto}»" + (" en ese municipio." if cvmun else ".")})
