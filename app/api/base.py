"""Router Base del tablero: estado, catalogos y geometria.

Dueno: etapa Base del tablero.

    GET /api/estado        Ollama, internet, fechas de corte y KPIs leidos de archivos
    GET /api/giros         giros de config/giros.yaml
    GET /api/municipios    los 76 municipios de la ZMVM
    GET /api/geo/agebs     GeoJSON de AGEB (simplificado ~20 m, 5 decimales), en cache y comprimido
    GET /api/geo/municipios contornos de municipio (disueltos)
    GET /api/inicio/demo   top 5 de la heladeria y puntos de score para la escena de Inicio

Todo se carga perezosamente y se guarda en cache: el servidor arranca sin leer datos.
"""
from __future__ import annotations

import gzip
import json
import re
import socket
import threading
import time
import unicodedata
import urllib.request
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

RAIZ = Path(__file__).resolve().parents[2]
PROC = RAIZ / "data" / "processed"
router = APIRouter(prefix="/api", tags=["base"])

OLLAMA_URL = "http://127.0.0.1:11434"
MODELOS_NECESARIOS = ("qwen3:8b", "nomic-embed-text")


# ---------------------------------------------------------------- Ollama e internet
_cache_red: dict = {}
_candado = threading.Lock()
_candado_geo = threading.Lock()


def _con_cache(clave: str, ttl: float, fn):
    """Guarda el resultado de fn() ttl segundos (los chequeos de red no deben frenar cada pedido)."""
    ahora = time.monotonic()
    with _candado:
        hit = _cache_red.get(clave)
        if hit and ahora - hit[0] < ttl:
            return hit[1]
    valor = fn()
    with _candado:
        _cache_red[clave] = (time.monotonic(), valor)
    return valor


def hay_internet() -> bool:
    """Conecta por TCP a un DNS publico (443/53) con timeout de 1.5 s; en cache 30 s."""
    def probar() -> bool:
        for host, puerto in (("1.1.1.1", 443), ("8.8.8.8", 53)):
            try:
                with socket.create_connection((host, puerto), timeout=1.5):
                    return True
            except OSError:
                continue
        return False
    return _con_cache("internet", 30, probar)


def estado_ollama() -> dict:
    """{prendido, modelos, faltan, cargados}; Ollama local en 127.0.0.1:11434, timeout corto, cache 5 s."""
    def probar() -> dict:
        try:
            with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1.0) as r:
                modelos = [m["name"] for m in json.load(r).get("models", [])]
        except Exception:
            return {"prendido": False, "modelos": [], "faltan": list(MODELOS_NECESARIOS), "cargados": []}
        try:
            with urllib.request.urlopen(f"{OLLAMA_URL}/api/ps", timeout=1.0) as r:
                cargados = [m["name"] for m in json.load(r).get("models", [])]
        except Exception:
            cargados = []
        tiene = lambda n: any(m == n or m.startswith(n + ":") for m in modelos)
        return {"prendido": True, "modelos": modelos, "cargados": cargados,
                "faltan": [n for n in MODELOS_NECESARIOS if not tiene(n)]}
    return _con_cache("ollama", 5, probar)


# ---------------------------------------------------------------- KPIs desde archivos
@lru_cache(maxsize=1)
def _giros_yaml() -> dict:
    """config/giros.yaml como {clave: giro} (sin importar el motor, que carga scipy y pandas)."""
    import yaml

    try:
        y = yaml.safe_load((RAIZ / "config" / "giros.yaml").read_text(encoding="utf-8"))
        return {g["clave"]: g for g in y["giros"]}
    except Exception:
        return {}


def _json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return {}


@lru_cache(maxsize=1)
def kpis() -> dict:
    """Cifras que salen de archivos del repo; lo que falta se queda en None (nada escrito a mano)."""
    import pyarrow.parquet as pq

    def filas(nombre: str):
        try:
            return pq.ParquetFile(PROC / nombre).metadata.num_rows
        except Exception:
            return None

    meta = _json(RAIZ / "models" / "metadata.json")
    ev = _json(RAIZ / "reports" / "evaluacion.json")
    try:
        n_mun = int(sum(1 for _ in (PROC / "zmvm_municipios.csv").open(encoding="utf-8")) - 1)
    except Exception:
        n_mun = None
    n_giros = len(_giros_yaml()) or None
    return {
        "agebs": filas("agebs_base.parquet"),
        "municipios": n_mun,
        "negocios_denue": filas("denue_actual.parquet"),
        "negocios_denue_hist": filas("denue_hist.parquet"),
        "giros": n_giros,
        "auc_global": (meta.get("validacion") or {}).get("auc_oof_global"),
        "evaluacion": {
            "pasan": ev.get("pasan"), "total": ev.get("preguntas"), "aprobado": ev.get("aprobado"),
            "trampa_pasa": ev.get("trampa_pasa"), "fecha": ev.get("fecha"),
            "latencia_mediana_s": ev.get("latencia_mediana_s"),
        },
    }


@lru_cache(maxsize=1)
def cortes() -> dict:
    """Fechas de corte de cada fuente, leidas de los registros de descarga y del modelo."""
    f01b = _json(PROC / "_fuentes_01b.json")
    def corte(prefijo: str):
        v = sorted({d.get("corte") for k, d in f01b.items() if k.startswith(prefijo) and isinstance(d, dict) and d.get("corte")})
        return v[-1] if v else None
    macro = _json(PROC / "macro.json")
    meta = _json(RAIZ / "models" / "metadata.json")
    return {
        "denue_actual": corte("denue_actual"),
        "denue_hist": corte("denue_hist"),
        "censo": "2020",
        "enigh": "2024",
        "conapo": "2020",
        "macro_consultado": (macro.get("_meta") or {}).get("generado"),
        "modelo": meta.get("fecha"),
    }


@router.get("/estado")
def estado() -> dict:
    return {"ollama": estado_ollama(), "internet": hay_internet(), "cortes": cortes(), "kpis": kpis(),
            "fuentes": {"agebs": "Censo 2020 INEGI", "negocios_denue": f"DENUE corte {cortes()['denue_actual'] or 'NO ENCONTRADO'}",
                        "municipios": "SEDATU-CONAPO-INEGI, delimitacion de zonas metropolitanas 2015",
                        "auc_global": "modelo propio (validacion por municipio)", "giros": "config/giros.yaml (supuestos del proyecto)"}}


# ---------------------------------------------------------------- catalogos
# config/giros.yaml guarda los nombres sin acentos (los usa el buscador); el tablero muestra estos, con acentos de MX.
NOMBRES_VISIBLES = {
    "barberia_estetica": "Barbería y estética", "cafe_internet": "Café internet", "cafeteria": "Cafetería", "carniceria": "Carnicería",
    "cerrajeria": "Cerrajería", "consultorio_medico": "Consultorio médico", "escuela_idiomas": "Escuela de idiomas", "ferreteria": "Ferretería",
    "floreria": "Florería", "fruteria": "Frutería", "guarderia": "Guardería", "heladeria": "Heladería", "laboratorio_clinico": "Laboratorio clínico",
    "lavanderia": "Lavandería", "libreria": "Librería", "optica": "Óptica", "panaderia": "Panadería", "papeleria": "Papelería",
    "pasteleria": "Pastelería", "pizzeria": "Pizzería", "renta_bicicletas": "Renta de bicicletas", "taller_mecanico": "Taller mecánico",
    "taqueria": "Taquería", "tienda_celulares": "Tienda de celulares", "tienda_mascotas": "Tienda de mascotas", "tienda_ropa": "Tienda de ropa",
    "tortilleria": "Tortillería", "zapateria": "Zapatería",
}


@lru_cache(maxsize=1)
def _giros_lista() -> list[dict]:
    out = []
    for clave, g in _giros_yaml().items():
        nombres = g.get("nombres") or [clave.replace("_", " ")]
        out.append({"clave": clave, "nombre": NOMBRES_VISIBLES.get(clave) or str(nombres[0]).capitalize(), "nombres": [str(n) for n in nombres],
                    "ticket_promedio_mxn": g.get("ticket_promedio_mxn"), "radio_influencia_m": g.get("radio_influencia_m"),
                    "rubro_enigh": g.get("rubro_enigh"), "demanda_base": g.get("demanda_base", "residente")})
    return sorted(out, key=lambda x: unicodedata.normalize("NFKD", x["nombre"]).encode("ascii", "ignore").decode().lower())


@router.get("/giros")
def giros() -> dict:
    return {"giros": _giros_lista(), "fuente": "config/giros.yaml (supuestos del proyecto)"}


@lru_cache(maxsize=1)
def _municipios_lista() -> list[dict]:
    import pandas as pd

    m = pd.read_csv(PROC / "zmvm_municipios.csv", dtype=str)
    ent = {"09": "Ciudad de México", "13": "Hidalgo", "15": "Estado de México"}
    return sorted(({"cvegeo_mun": r.cvegeo_mun, "nombre": r.nom_mun, "cve_ent": r.cve_ent, "entidad": ent.get(r.cve_ent, r.cve_ent)}
                   for r in m.itertuples()), key=lambda x: (x["entidad"] != "Ciudad de México", x["nombre"]))


@router.get("/municipios")
def municipios() -> dict:
    return {"municipios": _municipios_lista(),
            "fuente": "SEDATU-CONAPO-INEGI, delimitación de zonas metropolitanas 2015 (76 municipios)"}


# ---------------------------------------------------------------- geometria
_RE_COORD = re.compile(r"(\d\.\d{5})\d+")
_geo: dict = {}


def _geojson_bytes(feats: list[dict]) -> bytes:
    s = json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, separators=(",", ":"))
    s = re.sub(r"(-?\d+\.\d{5})\d+", r"\1", s)
    return s.encode("utf-8")


def _construir_geo() -> dict:
    """Lee los poligonos una vez; AGEB a ~20 m y 5 decimales, y municipios disueltos."""
    import geopandas as gpd
    import shapely
    from shapely.geometry import mapping

    t0 = time.perf_counter()
    g = gpd.read_parquet(PROC / "agebs_features.parquet",
                         columns=["cvegeo", "nom_colonia", "nom_mun", "cve_ent", "cve_mun", "geometry"])
    simple = shapely.set_precision(g.geometry.simplify(0.0002, preserve_topology=True).values, 1e-5)
    feats = [{"type": "Feature", "properties": {"cvegeo": cv, "colonia": col if isinstance(col, str) else None, "municipio": mun},
              "geometry": mapping(geom)}
             for cv, col, mun, geom in zip(g["cvegeo"], g["nom_colonia"], g["nom_mun"], simple)]
    ageb = _geojson_bytes(feats)

    g["cvegeo_mun"] = g["cve_ent"].astype(str) + g["cve_mun"].astype(str)
    d = g.assign(geometry=simple).dissolve(by="cvegeo_mun", aggfunc={"nom_mun": "first"})
    d["geometry"] = shapely.set_precision(d.geometry.simplify(0.0004, preserve_topology=True).values, 1e-5)
    mfeats = [{"type": "Feature", "properties": {"cvegeo_mun": cv, "municipio": r["nom_mun"]}, "geometry": mapping(r["geometry"])}
              for cv, r in d.iterrows()]
    mun = _geojson_bytes(mfeats)
    gz = lambda b: gzip.compress(b, compresslevel=6)
    seg = time.perf_counter() - t0
    return {"agebs": (ageb, gz(ageb)), "municipios": (mun, gz(mun)), "segundos": round(seg, 2)}


def _geo_cache() -> dict:
    with _candado_geo:
        if not _geo:
            _geo.update(_construir_geo())
        return _geo


def _responder_geo(nombre: str, request: Request) -> Response:
    crudo, comprimido = _geo_cache()[nombre]
    cab = {"Cache-Control": "public, max-age=3600", "Vary": "Accept-Encoding", "X-Geo-Bytes": str(len(crudo)),
           "X-Geo-Bytes-Gzip": str(len(comprimido)), "X-Geo-Segundos-Primera-Carga": str(_geo["segundos"])}
    if "gzip" in request.headers.get("accept-encoding", ""):
        return Response(comprimido, media_type="application/geo+json", headers={**cab, "Content-Encoding": "gzip"})
    return Response(crudo, media_type="application/geo+json", headers=cab)


@router.get("/geo/agebs")
def geo_agebs(request: Request) -> Response:
    return _responder_geo("agebs", request)


@router.get("/geo/municipios")
def geo_municipios(request: Request) -> Response:
    return _responder_geo("municipios", request)


# ---------------------------------------------------------------- Inicio: escena con datos reales
_candado_demo = threading.Lock()


def _demo() -> dict:
    """Con candado: si Inicio y otra vista la piden a la vez, el motor se carga una sola vez (la Mac tiene poca RAM)."""
    with _candado_demo:
        return _demo_calculada()


@lru_cache(maxsize=1)
def _demo_calculada() -> dict:
    """Top 5 de heladeria (recomendar_zonas) y un punto por AGEB con su score, para dibujar el mapa de la escena."""
    from app import herramientas as H
    from app import motor

    r = H.recomendar_zonas("heladeria", top=5)
    f = motor.cargar_features()
    s = motor.score_giro("heladeria")[["cvegeo", "score"]]
    s = s.join(f[["lat", "lon"]], on="cvegeo").dropna()
    zonas = [{"colonia": z["colonia"], "municipio": z["municipio"], "ageb": z["ageb"], "score": z["score"],
              "prob_apertura_pct": z["prob_apertura_pct"], "lat": float(f.at[z["ageb"], "lat"]), "lon": float(f.at[z["ageb"], "lon"])}
             for z in r.get("zonas", [])]
    return {"giro": "heladeria", "pregunta": "Quiero poner una heladería", "zonas": zonas,
            "puntos": [[round(float(a), 4), round(float(b), 4), round(float(c)), cv] for a, b, c, cv in zip(s["lon"], s["lat"], s["score"], s["cvegeo"])],
            "fuentes": r.get("fuentes", []), "metodo": r.get("metodo")}


@router.get("/inicio/demo")
def inicio_demo() -> dict:
    try:
        return _demo()
    except Exception as e:  # la escena cae a su estado vacio, no tumba el tablero
        return JSONResponse(status_code=503, content={"error": f"{type(e).__name__}: {e}"})


def precalentar() -> None:
    """Calienta en segundo plano lo que Inicio pide primero (geometria y demo del motor), para que la primera pantalla
    no espere ~10 s. Lo lanza app.servidor.main() en un hilo; crear_app() no lo llama, asi las pruebas no cargan el motor."""
    try:
        _geo_cache()
        _demo()
    except Exception:  # si falla, cada endpoint lo reintenta y reporta su propio error
        pass
