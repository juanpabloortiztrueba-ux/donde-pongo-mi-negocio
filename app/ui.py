"""Interfaz Streamlit: chat con el agente y mapa del score por AGEB.

    uv run streamlit run app/ui.py      (o `make app`)

El mapa interactivo (folium) necesita internet para el mapa base y Leaflet; sin internet se
dibuja un mapa estatico (matplotlib) con los mismos datos. El agente y los datos son locales.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from app import herramientas as H  # noqa: E402
from app import motor  # noqa: E402

st.set_page_config(page_title="Donde pongo mi negocio", page_icon=":round_pushpin:", layout="wide")


# ---------------------------------------------------------------- datos en cache
@st.cache_resource(show_spinner="Cargando poligonos de AGEB...")
def geometria():
    """Poligonos simplificados (~20 m) de las 5 875 AGEB; se leen una vez por sesion del servidor."""
    import geopandas as gpd
    import shapely

    g = gpd.read_parquet(RAIZ / "data" / "processed" / "agebs_features.parquet",
                         columns=["cvegeo", "nom_colonia", "nom_mun", "geometry"])
    # simplifica (~20 m) y redondea a 5 decimales: el GeoJSON baja de ~13 MB a ~3 MB
    g["geometry"] = shapely.set_precision(g.geometry.simplify(0.0002, preserve_topology=True).values, 1e-5)
    return g


@st.cache_data(show_spinner=False)
def scores(giro: str) -> pd.DataFrame:
    return motor.score_giro(giro)[["cvegeo", "score", "prob_apertura", "competencia", "nse"]]


@st.cache_data(show_spinner=False, ttl=600)
def hay_internet() -> bool:
    import requests
    try:
        requests.head("https://cdn.jsdelivr.net", timeout=1.5)
        return True
    except Exception:
        return False


GIROS = sorted(motor.giros())


# ---------------------------------------------------------------- mapa
def mapa_folium(giro: str, top: list[dict], filtro_mun: str | None):
    import folium
    from branca.colormap import LinearColormap
    from streamlit_folium import st_folium

    g = geometria().merge(scores(giro), on="cvegeo", how="left")
    if filtro_mun:
        g = g[g["nom_mun"] == filtro_mun]
    g = g.assign(score=g["score"].round(0))
    cm = LinearColormap(["#f7fbff", "#9ecae1", "#3182bd", "#08306b"], vmin=0, vmax=100, caption=f"Score {giro} (0-100)")
    if len(g):
        x0, y0, x1, y1 = g.total_bounds
        centro = [(y0 + y1) / 2, (x0 + x1) / 2]
    else:
        centro = [19.43, -99.13]
    m = folium.Map(location=centro, zoom_start=10 if not filtro_mun else 12, tiles="OpenStreetMap", prefer_canvas=True)
    folium.GeoJson(
        g[["cvegeo", "nom_colonia", "nom_mun", "score", "geometry"]].to_json(),
        style_function=lambda f: {"fillColor": cm(f["properties"]["score"] or 0), "color": "#555", "weight": 0.2,
                                  "fillOpacity": 0.65},
        tooltip=folium.GeoJsonTooltip(fields=["nom_colonia", "nom_mun", "cvegeo", "score"],
                                      aliases=["Colonia", "Municipio", "AGEB", "Score"]),
    ).add_to(m)
    cm.add_to(m)
    for i, z in enumerate(top, 1):
        folium.Marker([z["lat"], z["lon"]], tooltip=f"{i}. {z['colonia']} ({z['score']})",
                      icon=folium.DivIcon(html=f'<div style="background:#d7301f;color:#fff;border-radius:50%;'
                                               f'width:24px;height:24px;text-align:center;font:bold 13px/24px sans-serif;'
                                               f'border:2px solid #fff">{i}</div>')).add_to(m)
    st_folium(m, height=560, use_container_width=True, returned_objects=[], key=f"mapa_{giro}_{filtro_mun}")


def mapa_estatico(giro: str, top: list[dict], filtro_mun: str | None):
    import matplotlib.pyplot as plt

    g = geometria().merge(scores(giro), on="cvegeo", how="left")
    if filtro_mun:
        g = g[g["nom_mun"] == filtro_mun]
    fig, ax = plt.subplots(figsize=(7, 7))
    g.plot(column="score", cmap="Blues", vmin=0, vmax=100, linewidth=0, ax=ax, legend=True,
           legend_kwds={"shrink": 0.6, "label": f"Score {giro}"})
    for i, z in enumerate(top, 1):
        ax.scatter(z["lon"], z["lat"], s=160, c="#d7301f", edgecolors="white", zorder=3)
        ax.annotate(str(i), (z["lon"], z["lat"]), ha="center", va="center", color="white", fontsize=8, zorder=4)
    ax.set_axis_off()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def top_de(giro: str, mun: str | None, nse: str | None) -> list[dict]:
    r = H.recomendar_zonas(giro, municipio=mun, nse=nse)
    if not r.get("encontrado"):
        return []
    f = motor.cargar_features()
    return [{**z, "lat": float(f.at[z["ageb"], "lat"]), "lon": float(f.at[z["ageb"], "lon"])} for z in r["zonas"]]


# ---------------------------------------------------------------- estado
ss = st.session_state
ss.setdefault("chat", [])          # [{role, content}]
ss.setdefault("giro", "heladeria")
ss.setdefault("mun", None)
ss.setdefault("nse", None)

with st.sidebar:
    st.header("Donde pongo mi negocio")
    st.caption("ZMVM: 16 alcaldias, 59 municipios del Edomex y Tizayuca. Datos: INEGI (Censo 2020, DENUE 05/2026, "
               "ENIGH 2024), CONAPO, Banxico. Modelo local qwen3:8b.")
    ss.giro = st.selectbox("Giro del mapa", GIROS, index=GIROS.index(ss.giro))
    muns = [None] + sorted(H.municipios()["nom_mun"])
    ss.mun = st.selectbox("Municipio o alcaldia", muns, index=muns.index(ss.mun) if ss.mun in muns else 0,
                          format_func=lambda x: "Toda la ZMVM" if x is None else x)
    ss.nse = st.selectbox("NSE estimado", [None, "bajo", "medio", "alto"],
                          index=[None, "bajo", "medio", "alto"].index(ss.nse), format_func=lambda x: x or "Todos")
    estatico = st.toggle("Mapa estatico (sin internet)", value=not hay_internet())
    if st.button("Borrar conversacion"):
        ss.chat = []
        st.rerun()

col_chat, col_mapa = st.columns([1, 1.1], gap="large")

with col_chat:
    st.subheader("Pregunta")
    for m in ss.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("meta"):
                st.caption(m["meta"])
    pregunta = st.chat_input("Ej.: quiero poner una heladeria en Coyoacan")
    if pregunta:
        with st.chat_message("user"):
            st.markdown(pregunta)
        with st.chat_message("assistant"):
            with st.spinner("Consultando datos y modelo local..."):
                from app import agente
                hist = [{"role": m["role"], "content": m["content"]} for m in ss.chat[-4:]]
                out = agente.responder(pregunta, historial=hist)
            st.markdown(out["respuesta"])
            meta = (f"{out['modo']} · {out['latencia_s']} s · herramientas: "
                    + ", ".join(u["nombre"] for u in out["herramientas"]))
            st.caption(meta)
        ss.chat += [{"role": "user", "content": pregunta}, {"role": "assistant", "content": out["respuesta"], "meta": meta}]
        # el mapa sigue al giro y filtros de la ultima recomendacion
        for u in reversed(out["herramientas"]):
            r = u["resultado"]
            if u["nombre"] == "recomendar_zonas" and r.get("encontrado"):
                ss.giro = r["giro"]
                ss.mun = (r.get("filtros") or {}).get("municipio")
                ss.nse = (r.get("filtros") or {}).get("nse")
                break
        st.rerun()

with col_mapa:
    st.subheader(f"Score de {ss.giro}" + (f" en {ss.mun}" if ss.mun else " en la ZMVM"))
    top = top_de(ss.giro, ss.mun, ss.nse)
    if estatico:
        mapa_estatico(ss.giro, top, ss.mun)
    else:
        mapa_folium(ss.giro, top, ss.mun)
    if top:
        st.dataframe(pd.DataFrame(top)[["colonia", "municipio", "ageb", "score", "prob_apertura_pct",
                                        "competidores_ponderados", "nse_estimado"]],
                     hide_index=True, width="stretch")
    st.caption(H.metodo_score().capitalize() + ". " + H.COMO_LEER.capitalize()
               + ". NSE y decil son estimaciones del proyecto.")
