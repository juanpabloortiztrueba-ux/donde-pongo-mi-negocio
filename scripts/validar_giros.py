"""Valida config/giros.yaml contra los datos reales del proyecto.

Uso:  uv run python scripts/validar_giros.py [--md reports/validacion_giros.md]

Revisa: estructura y tipos, que cada SCIAN exista como clase en data/processed/scian.csv,
cuantos establecimientos tiene cada giro en el DENUE actual y en el historico, que cada
rubro_enigh exista en enigh_gasto.parquet (ambito zmvm, los 10 deciles), que los pesos
sumen 1, que los regex compilen y peguen, y que no haya dos giros con la misma competencia.
Sale con codigo 1 si hay errores; las advertencias no cambian el codigo.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = RAIZ / "config" / "giros.yaml"
PROC = RAIZ / "data" / "processed"

RANGOS_EDAD = {"0-14", "15-24", "25-59", "60+"}
NSE = {"bajo", "medio", "alto"}
CAMPOS = ["clave", "nombres", "scian", "complementarios", "cliente_objetivo", "nse_objetivo",
          "rubro_enigh", "ticket_promedio_mxn", "ticket_fuente", "radio_influencia_m", "notas"]
DEMANDA = {"residente", "diurna", "mixta"}
MIN_RARO = 100  # menos de esto en el DENUE actual: giro raro, se avisa


class Reporte:
    def __init__(self) -> None:
        self.errores: list[str] = []
        self.avisos: list[str] = []

    def error(self, clave: str, msg: str) -> None:
        self.errores.append(f"[{clave}] {msg}")

    def aviso(self, clave: str, msg: str) -> None:
        self.avisos.append(f"[{clave}] {msg}")


def es_clase(c: object) -> bool:
    return isinstance(c, str) and bool(re.fullmatch(r"\d{6}", c))


def pesos_ok(d: object, llaves: set[str]) -> str | None:
    if not isinstance(d, dict):
        return "no es un diccionario"
    if set(d) != llaves:
        return f"llaves {sorted(map(str, d))} distintas de {sorted(llaves)}"
    try:
        v = [float(x) for x in d.values()]
    except (TypeError, ValueError):
        return "pesos no numericos"
    if min(v) < 0:
        return "peso negativo"
    if abs(sum(v) - 1) > 0.011:
        return f"suman {sum(v):.3f}, no 1"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", help="ruta donde escribir el reporte en Markdown")
    args = ap.parse_args()
    rep = Reporte()

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    giros = cfg.get("giros", [])
    if not 35 <= len(giros) <= 45:
        rep.error("global", f"hay {len(giros)} giros; se esperan ~40")

    scian = pd.read_csv(PROC / "scian.csv", dtype=str)
    clases = dict(zip(scian.loc[scian.nivel == "clase", "codigo"], scian.loc[scian.nivel == "clase", "titulo"]))

    act = pd.read_parquet(PROC / "denue_actual.parquet", columns=["codigo_act", "nombre"])
    act["nombre"] = act["nombre"].fillna("")
    his = pd.read_parquet(PROC / "denue_hist.parquet", columns=["codigo_act_actual", "nombre"])
    his["nombre"] = his["nombre"].fillna("")
    cnt_act = act["codigo_act"].value_counts()
    cnt_his = his["codigo_act_actual"].value_counts()

    g = pd.read_parquet(PROC / "enigh_gasto.parquet")
    gz = g[g["ambito"] == "zmvm"]
    rubros_ok = {k for k, s in gz.groupby("rubro_clave") if s["decil"].nunique() == 10}
    rubros_pct = gz.groupby("rubro_clave")["pct_hogares_con_gasto"].mean()

    claves_vistas: set[str] = set()
    firmas: dict[tuple, str] = {}
    filas: list[dict] = []

    for gi in giros:
        k = str(gi.get("clave", "?"))
        if not re.fullmatch(r"[a-z0-9_]+", k):
            rep.error(k, "clave no es slug ascii (a-z, 0-9, _)")
        if k in claves_vistas:
            rep.error(k, "clave repetida")
        claves_vistas.add(k)
        for c in CAMPOS:
            if c not in gi:
                rep.error(k, f"falta el campo {c}")
        if not isinstance(gi.get("nombres"), list) or not gi.get("nombres"):
            rep.error(k, "nombres debe ser una lista no vacia")
        elif not all(isinstance(n, str) and n.isascii() for n in gi["nombres"]):
            rep.error(k, "nombres con caracteres no ascii o no texto")
        if k not in [str(n) for n in gi.get("nombres", [])] and k.replace("_", " ") not in gi.get("nombres", []):
            rep.aviso(k, "ningun sinonimo coincide con la clave; el agente podria no encontrarlo por nombre")

        # --- SCIAN y competencia efectiva
        directos = gi.get("scian") or []
        filtros = gi.get("scian_con_filtro") or []
        if not directos and not filtros:
            rep.error(k, "sin scian ni scian_con_filtro: el giro no tiene competencia medible")
        for c in directos:
            if not es_clase(c):
                rep.error(k, f"scian {c!r} no es texto de 6 digitos (poner entre comillas)")
            elif c not in clases:
                rep.error(k, f"scian {c} no existe como clase en scian.csv")
        mask_act = act["codigo_act"].isin([c for c in directos if es_clase(c)])
        mask_his = his["codigo_act_actual"].isin([c for c in directos if es_clase(c)])
        sig_f = []
        for f in filtros:
            cods = f.get("codigos") or []
            rx = f.get("nombre_regex")
            for c in cods:
                if not es_clase(c) or c not in clases:
                    rep.error(k, f"scian_con_filtro: {c!r} no es una clase valida de scian.csv")
            try:
                pat = re.compile(rx, re.I)
            except (re.error, TypeError) as e:
                rep.error(k, f"nombre_regex invalido ({e})")
                continue
            sig_f.append((tuple(sorted(cods)), rx))
            mask_act |= act["codigo_act"].isin(cods) & act["nombre"].str.contains(pat)
            mask_his |= his["codigo_act_actual"].isin(cods) & his["nombre"].str.contains(pat)
        n_act, n_his = int(mask_act.sum()), int(mask_his.sum())
        if n_act == 0:
            rep.error(k, "la competencia no pega con ningun establecimiento del DENUE actual")
        elif n_act < MIN_RARO:
            rep.aviso(k, f"giro raro: solo {n_act} establecimientos en el DENUE actual")
        if n_his == 0:
            rep.error(k, "la competencia no pega con ningun establecimiento del DENUE historico (11/2020): el modelo de aperturas no tendria etiquetas")
        elif n_his < 30:
            rep.aviso(k, f"solo {n_his} establecimientos en el historico (11/2020)")
        firma = (tuple(sorted(directos)), tuple(sorted(sig_f)))
        if firma in firmas:
            rep.error(k, f"misma competencia exacta que {firmas[firma]}")
        firmas[firma] = k
        for c in directos:
            if c in clases and cnt_act.get(c, 0) == 0:
                rep.aviso(k, f"scian {c} no tiene establecimientos en la ZMVM (se mantiene por completitud)")

        # --- complementarios
        comp = gi.get("complementarios") or []
        if not comp:
            rep.error(k, "complementarios vacio")
        n_comp = 0
        for c in comp:
            if not es_clase(c):
                rep.error(k, f"complementario {c!r} no es texto de 6 digitos")
            elif c not in clases:
                rep.error(k, f"complementario {c} no existe como clase en scian.csv")
            else:
                n_comp += int(cnt_act.get(c, 0))
                if cnt_act.get(c, 0) == 0:
                    rep.aviso(k, f"complementario {c} no tiene establecimientos en la ZMVM")
                if c in directos:
                    rep.error(k, f"complementario {c} tambien esta en scian (competencia)")
        if len(set(comp)) != len(comp):
            rep.error(k, "complementarios con codigos repetidos")

        # --- pesos
        for campo, llaves in (("cliente_objetivo", RANGOS_EDAD), ("nse_objetivo", NSE)):
            msg = pesos_ok(gi.get(campo), llaves)
            if msg:
                rep.error(k, f"{campo}: {msg}")

        # --- ENIGH
        r = gi.get("rubro_enigh")
        nota_r = str(gi.get("rubro_enigh_nota", ""))
        if r is None:
            if "NO ENCONTRADO" not in nota_r:
                rep.error(k, "rubro_enigh nulo sin la nota 'NO ENCONTRADO' en rubro_enigh_nota")
            pct = None
        elif r not in rubros_ok:
            rep.error(k, f"rubro_enigh {r!r} no existe en enigh_gasto (zmvm, 10 deciles)")
            pct = None
        else:
            pct = float(rubros_pct[r])
            if pct < 5 and not nota_r:
                rep.aviso(k, f"rubro_enigh {r} lo reporta solo {pct:.1f} % de hogares y no hay rubro_enigh_nota")
        for a in gi.get("rubro_enigh_alt") or []:
            if a not in rubros_ok:
                rep.error(k, f"rubro_enigh_alt {a!r} no existe en enigh_gasto")

        # --- ticket, radio, demanda
        t = gi.get("ticket_promedio_mxn")
        if not isinstance(t, (int, float)) or isinstance(t, bool) or t <= 0:
            rep.error(k, f"ticket_promedio_mxn {t!r} debe ser un numero positivo")
        tf = str(gi.get("ticket_fuente", "")).strip()
        if not tf:
            rep.error(k, "ticket_fuente vacio: debe llevar fuente o empezar con 'supuesto'")
        elif not (tf.lower().startswith("supuesto") or re.search(r"https?://|INEGI|Profeco|Banxico", tf)):
            rep.error(k, "ticket_fuente debe empezar con 'supuesto' o citar una fuente")
        rd = gi.get("radio_influencia_m")
        if not isinstance(rd, (int, float)) or not 100 <= rd <= 5000:
            rep.error(k, f"radio_influencia_m {rd!r} fuera de 100-5000")
        if gi.get("demanda_base", "residente") not in DEMANDA:
            rep.error(k, f"demanda_base {gi.get('demanda_base')!r} no es {sorted(DEMANDA)}")
        if not str(gi.get("notas", "")).strip():
            rep.error(k, "notas vacio")

        filas.append({"clave": k, "denue_actual": n_act, "denue_hist_2020": n_his,
                      "compl_estab": n_comp, "rubro_enigh": r or "NO ENCONTRADO",
                      "hogares_con_gasto_pct": None if pct is None else round(pct, 1),
                      "ticket": t, "radio_m": rd, "ticket_supuesto": tf.lower().startswith("supuesto")})

    # --- ningun token en el archivo
    texto = CONFIG.read_text(encoding="utf-8")
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text().splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                nombre, _, valor = linea.partition("=")
                valor = valor.strip().strip("'\"")
                if len(valor) >= 8 and valor in texto:
                    rep.error("global", f"el valor de {nombre.strip()} aparece en giros.yaml")

    df = pd.DataFrame(filas)
    pd.set_option("display.width", 200)
    print(df.to_string(index=False))
    print(f"\n{len(giros)} giros | {len(rep.errores)} errores | {len(rep.avisos)} avisos")
    for m in rep.errores:
        print("ERROR ", m)
    for m in rep.avisos:
        print("AVISO ", m)

    if args.md:
        ruta = RAIZ / args.md
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", encoding="utf-8") as f:
            f.write("# Validacion de config/giros.yaml\n\n")
            f.write("Generado por `scripts/validar_giros.py`. Fuentes: `data/processed/scian.csv`, "
                    "`denue_actual.parquet` (05/2026), `denue_hist.parquet` (11/2020), `enigh_gasto.parquet`.\n\n")
            f.write(f"{len(giros)} giros, {len(rep.errores)} errores, {len(rep.avisos)} avisos.\n\n")
            f.write(df.to_markdown(index=False) + "\n\n" if _tiene_tabulate() else "```\n" + df.to_string(index=False) + "\n```\n\n")
            if rep.errores:
                f.write("## Errores\n\n" + "\n".join(f"- {m}" for m in rep.errores) + "\n\n")
            if rep.avisos:
                f.write("## Avisos\n\n" + "\n".join(f"- {m}" for m in rep.avisos) + "\n")
    return 1 if rep.errores else 0


def _tiene_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    sys.exit(main())
