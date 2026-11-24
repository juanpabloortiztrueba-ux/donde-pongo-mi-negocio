"""Servidor del tablero: FastAPI + el build de web/dist.

    uv run python -m app.servidor [--puerto 8501] [--red] [--web <dir>] [--sin-navegador]

Por defecto escucha solo en 127.0.0.1 y sirve web/dist. Con --red escucha en 0.0.0.0 (cualquiera en tu
misma red puede abrirlo). Con --web sirve otro build (lo usan los revisores). Los endpoints viven en
app/api/*.py (un router por grupo; ver docs/CONTRATO.md, seccion Tablero).
"""
from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api import base, contexto, explorar, preguntar

RAIZ = Path(__file__).resolve().parents[1]
WEB_POR_DEFECTO = RAIZ / "web" / "dist"


def crear_app(web: Path | str | None = None) -> FastAPI:
    """App con los cuatro routers y el build web (con fallback a index.html para el ruteo del cliente)."""
    app = FastAPI(title="Donde pongo mi negocio", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.add_middleware(GZipMiddleware, minimum_size=1024)  # lo ya comprimido (geo) lleva Content-Encoding y no se repite
    for modulo in (base, preguntar, explorar, contexto):
        app.include_router(modulo.router)

    raiz_web = Path(web).resolve() if web else WEB_POR_DEFECTO

    @app.get("/api/{resto:path}", include_in_schema=False)
    def api_no_existe(resto: str):
        return JSONResponse(status_code=404, content={"error": f"/api/{resto} no existe"})

    @app.get("/{ruta:path}", include_in_schema=False)
    def servir_web(ruta: str):
        index = raiz_web / "index.html"
        if not index.exists():
            return JSONResponse(status_code=503, content={
                "error": f"no hay build web en {raiz_web}. Corre `make web` (necesita Node) o usa el build versionado en web/dist."})
        destino = (raiz_web / ruta).resolve() if ruta else index
        if ruta and destino.is_file() and raiz_web in destino.parents:
            cab = {"Cache-Control": "public, max-age=31536000, immutable"} if "/assets/" in f"/{ruta}" else {"Cache-Control": "no-cache"}
            return FileResponse(destino, headers=cab)
        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app


def ip_red_local() -> str | None:
    """IP de la red local: ipconfig en Mac, y en Windows/Linux un socket UDP (no manda nada)."""
    if sys.platform == "darwin":
        for iface in ("en0", "en1"):
            try:
                ip = subprocess.run(["ipconfig", "getifaddr", iface], capture_output=True, text=True, timeout=2).stdout.strip()
                if ip:
                    return ip
            except Exception:
                pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return None


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m app.servidor", description="Tablero de «Dónde pongo mi negocio»")
    ap.add_argument("--puerto", type=int, default=8501)
    ap.add_argument("--red", action="store_true", help="escucha en la red local (0.0.0.0)")
    ap.add_argument("--web", default=None, help="carpeta con otro build web (por defecto web/dist)")
    ap.add_argument("--sin-navegador", action="store_true", help="no abre el navegador")
    a = ap.parse_args(argv)

    import uvicorn

    host = "0.0.0.0" if a.red else "127.0.0.1"
    print(f"Tablero en http://127.0.0.1:{a.puerto}", flush=True)
    if a.red:
        ip = ip_red_local()
        print(f"En tu red local: http://{ip}:{a.puerto}" if ip else "En tu red local: no pude detectar tu IP (revisa tu Wi-Fi).", flush=True)
        print("AVISO: cualquiera conectado a la misma red puede abrir el tablero y usar el modelo local.", flush=True)
    if not a.sin_navegador:
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{a.puerto}")).start()
    def _calentar() -> None:  # en un hilo: el primer pedido de cada vista ya no paga la carga del motor
        for modulo in (base, preguntar, contexto):
            try:
                modulo.precalentar()
            except Exception:
                pass

    threading.Thread(target=_calentar, daemon=True, name="precalentar").start()
    uvicorn.run(crear_app(a.web), host=host, port=a.puerto, log_level="warning")


app = crear_app()

if __name__ == "__main__":
    main()
