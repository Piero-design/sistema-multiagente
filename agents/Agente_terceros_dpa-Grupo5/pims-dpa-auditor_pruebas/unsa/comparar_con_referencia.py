#!/usr/bin/env python3
"""
comparar_con_referencia.py — Mide qué tan cerca está un modelo de las evaluaciones de referencia.

    python pims-dpa-auditor_pruebas/unsa/comparar_con_referencia.py <registros...> [--salida informe.md]

<registros> son archivos o carpetas con los JSON que produjo el sistema (p. ej. datos/registro/*.json,
exportados desde la página). Cada uno se empareja con su referencia por el nombre del proveedor.

Métricas por contrato y globales:
  - Concordancia exacta por control (26 por contrato) y concordancia aceptando las alternativas
    de los controles "discutibles".
  - Kappa de Cohen sobre los estados (Cumple / Parcial / No cumple / Sin evidencia / No aplica):
    corrige el acuerdo que se daría por azar. Lectura habitual: >0,8 casi perfecto; 0,6-0,8 sustancial.
  - Concordancia en los 9 controles críticos.
  - Diferencia de puntaje, coincidencia de banda y de dictamen.
  - Cobertura de alertas Altas: cuántas alertas Altas de la referencia tienen una alerta Alta en el
    resultado que comparte al menos un control relacionado.
  - Matriz de confusión global (filas: referencia; columnas: modelo).

Sirve para comparar modelos (Claude, Ollama, otros) y ejecuciones repetidas sobre los mismos contratos.
Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ESTADOS = ["Cumple", "Parcial", "No cumple", "Sin evidencia", "No aplica"]
CRITICOS = {"A.2.2.2", "A.2.2.3", "A.2.4.3", "A.2.5.3", "A.2.5.7", "A.2.5.8", "A.2.5.9", "A.3.10", "A.3.12"}


def clave(nombre):
    t = unicodedata.normalize("NFD", str(nombre or "")).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\b(s\.?\s?a\.?\s?c\.?|s\.?\s?a\.?|s\.?\s?r\.?\s?l\.?|inc|ltd|llc)\b\.?", " ", t)
    return " ".join(re.findall(r"[a-z0-9]+", t))


def kappa(pares):
    n = len(pares)
    if not n:
        return None
    po = sum(1 for a, b in pares if a == b) / n
    ca, cb = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def cargar(rutas):
    salida = []
    for r in rutas:
        p = Path(r)
        for f in (sorted(p.glob("*.json")) if p.is_dir() else [p]):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(d, dict) and "controles" in d and "puntaje_proveedor" in d:
                salida.append((f, d))
    return salida


def comparar(ref, res):
    rc = {c["control"]: c for c in ref["controles"]}
    mc = {c["control"]: c for c in res.get("controles", [])}
    pares, exactos, aceptables, crit_ok, filas = [], 0, 0, 0, []
    for cid, c in rc.items():
        m = mc.get(cid, {}).get("estado", "(falta)")
        ok = m == c["estado"]
        acep = ok or m in c.get("_alternativas", [])
        exactos += ok
        aceptables += acep
        if cid in CRITICOS:
            crit_ok += ok
        pares.append((c["estado"], m))
        if not ok:
            filas.append((cid, c["estado"], m, "aceptable" if acep else "distinto", c.get("observacion", "")))
    ra = [a for a in ref["alertas"] if a["prioridad"] == "Alta"]
    ma = [a for a in res.get("alertas", []) if a["prioridad"] == "Alta"]
    cubiertas = sum(1 for a in ra if any(set(a.get("controles_relacionados") or []) & set(b.get("controles_relacionados") or [])
                                          or (a.get("origen") == "script" and b.get("origen") == "script") for b in ma))
    pr, pm = ref["puntaje_proveedor"], res["puntaje_proveedor"]
    return {"n": len(rc), "exactos": exactos, "aceptables": aceptables, "criticos": crit_ok, "pares": pares, "difieren": filas,
            "puntaje_ref": pr["valor"], "puntaje_mod": pm["valor"], "banda_ok": pr["banda"] == pm["banda"],
            "dictamen_ref": ref["dictamen"], "dictamen_mod": res["dictamen"], "riesgo_ref": ref["nivel_riesgo_pii"],
            "riesgo_mod": res.get("nivel_riesgo_pii"), "altas_ref": len(ra), "altas_cubiertas": cubiertas, "kappa": kappa(pares)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registros", nargs="+")
    ap.add_argument("--referencias", default=str(AQUI / "esperado"))
    ap.add_argument("--salida", help="Escribir el informe en Markdown")
    a = ap.parse_args()

    refs = {clave(d["tercero"]["nombre"]): (f, d) for f, d in cargar([a.referencias])}
    resultados = cargar(a.registros)
    emparejados = []
    for f, d in resultados:
        k = clave((d.get("tercero") or {}).get("nombre"))
        ref = refs.get(k) or next((v for kk, v in refs.items() if kk.split()[:2] == k.split()[:2]), None)
        if ref:
            emparejados.append((f, d, ref[1], comparar(ref[1], d)))
    if not emparejados:
        sys.exit("Ningún registro coincide con un proveedor de las referencias.")

    L = ["# Comparación con las evaluaciones de referencia", "",
         f"Referencias: `{a.referencias}` · registros comparados: {len(emparejados)}", "",
         "| Contrato | Modelo | Exactos | Con alternativas | Críticos | Kappa | Puntaje ref → modelo | Dictamen | Alertas altas cubiertas |",
         "|---|---|---|---|---|---|---|---|---|"]
    glob_pares, tot = [], Counter()
    for f, d, ref, m in emparejados:
        modelo = (d.get("_registro") or {}).get("modelo") or (d.get("trazabilidad") or {}).get("evaluador", "—")
        glob_pares += m["pares"]
        tot.update({"n": m["n"], "exactos": m["exactos"], "aceptables": m["aceptables"], "criticos": m["criticos"], "crit_n": 9,
                    "dictamen": m["dictamen_ref"] == m["dictamen_mod"], "banda": m["banda_ok"], "altas_ref": m["altas_ref"],
                    "altas_cub": m["altas_cubiertas"], "abs_dif": abs(m["puntaje_ref"] - m["puntaje_mod"]), "casos": 1})
        L.append(f"| {ref['tercero']['nombre']} | {modelo} | {m['exactos']}/{m['n']} | {m['aceptables']}/{m['n']} | {m['criticos']}/9 | "
                 f"{m['kappa']:.2f} | {m['puntaje_ref']} → {m['puntaje_mod']} | {'✔' if m['dictamen_ref'] == m['dictamen_mod'] else '✘ ' + m['dictamen_mod']} | "
                 f"{m['altas_cubiertas']}/{m['altas_ref']} |")
    k = kappa(glob_pares)
    L += ["", "## Global", "",
          f"- Concordancia exacta: **{tot['exactos']}/{tot['n']} ({100 * tot['exactos'] / tot['n']:.1f} %)**; "
          f"aceptando alternativas: {tot['aceptables']}/{tot['n']} ({100 * tot['aceptables'] / tot['n']:.1f} %)",
          f"- Controles críticos: {tot['criticos']}/{tot['crit_n']} ({100 * tot['criticos'] / tot['crit_n']:.1f} %)",
          f"- Kappa de Cohen global: **{k:.3f}**",
          f"- Dictamen coincidente: {tot['dictamen']}/{tot['casos']} · banda coincidente: {tot['banda']}/{tot['casos']} · "
          f"error medio de puntaje: {tot['abs_dif'] / tot['casos']:.1f} puntos",
          f"- Alertas altas de la referencia cubiertas: {tot['altas_cub']}/{tot['altas_ref']}", "",
          "## Matriz de confusión (filas: referencia · columnas: modelo)", "",
          "| | " + " | ".join(ESTADOS) + " | (falta) |", "|---" * (len(ESTADOS) + 2) + "|"]
    cm = Counter(glob_pares)
    for r in ESTADOS:
        L.append(f"| **{r}** | " + " | ".join(str(cm[(r, c)] or "·") for c in ESTADOS + ["(falta)"]) + " |")
    L += ["", "## Controles en los que difieren", ""]
    for f, d, ref, m in emparejados:
        if m["difieren"]:
            L.append(f"**{ref['tercero']['nombre']}**")
            L += [f"- {cid}: referencia *{r}* · modelo *{mm}* ({tipo})" for cid, r, mm, tipo, _ in m["difieren"]]
            L.append("")
    if all(not m["difieren"] for *_, m in emparejados):
        L.append("Ninguno.")
    texto = "\n".join(L) + "\n"
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    main()
