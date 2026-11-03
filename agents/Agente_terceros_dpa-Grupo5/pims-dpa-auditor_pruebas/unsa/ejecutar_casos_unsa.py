#!/usr/bin/env python3
"""
ejecutar_casos_unsa.py — Audita los 5 contratos supuestos de la UNSA a través de n8n con el modelo
configurado, guarda los registros y los compara con las evaluaciones de referencia.

    python pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py [--n8n http://localhost:5678]
           [--organizacion unsa] [--fecha-ref 2026-10-13] [--repeticiones 1] [--casos 01,03]

Resultado en pims-dpa-auditor_pruebas/unsa/corridas/<fecha-hora>_<modelo>/:
  - un .json y un .md por contrato (y por repetición),
  - comparacion.md con la concordancia por control, kappa, puntajes, dictámenes y alertas.

Úsalo para medir un modelo (o comparar varios: cambia el modelo en Configuración y vuelve a correrlo).
Con --repeticiones N mide además la estabilidad del mismo modelo entre ejecuciones.
La fecha de referencia por defecto (2026-10-13) es la de las referencias: cámbiala y las alertas de
renovación dejarán de coincidir.
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def http(base, metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(f"{base}/webhook/{ruta}", data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"} if datos else {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode("utf-8") or "{}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n8n", default="http://localhost:5678")
    ap.add_argument("--organizacion", default="unsa")
    ap.add_argument("--fecha-ref", default="2026-10-13")
    ap.add_argument("--repeticiones", type=int, default=1)
    ap.add_argument("--casos", help="Prefijos a ejecutar, p. ej. 01,03 (por defecto todos)")
    ap.add_argument("--limite-min", type=int, default=60, help="Minutos máximos de espera por auditoría (n8n permite hasta 30 min por llamada al modelo y hay hasta 2 llamadas)")
    a = ap.parse_args()

    try:
        est = http(a.n8n, "GET", "pims/estado")
    except urllib.error.URLError:
        sys.exit(f"No hay respuesta de n8n en {a.n8n}. Arráncalo con n8n\\iniciar_n8n.bat.")
    modelo = f"{est['modelo'].get('proveedor')}-{est['modelo'].get('modelo')}"
    contratos = sorted((AQUI / "contratos").glob("unsa_*.md"))
    if a.casos:
        pref = tuple(f"unsa_{p.strip()}" for p in a.casos.split(","))
        contratos = [c for c in contratos if c.name.startswith(pref)]
    salida = AQUI / "corridas" / f"{datetime.now():%Y%m%d_%H%M}_{re.sub(r'[^A-Za-z0-9.-]+', '_', modelo)}"
    salida.mkdir(parents=True, exist_ok=True)
    print(f"Modelo: {modelo} · organización: {a.organizacion} · {len(contratos)} contrato(s) × {a.repeticiones}\nResultados: {salida}\n")

    fallidos = []
    for rep in range(1, a.repeticiones + 1):
        for c in contratos:
            t0 = time.time()
            r = http(a.n8n, "POST", "pims/auditar", {"organizacion": a.organizacion, "contrato_texto": c.read_text(encoding="utf-8"),
                                                       "fecha_ref": a.fecha_ref})
            if not r.get("trabajo"):
                print(f"  {c.stem}: no se aceptó ({r.get('error')})")
                continue
            while True:
                time.sleep(3)
                t = http(a.n8n, "GET", f"pims/trabajo?id={r['trabajo']}")
                if t.get("estado") in ("terminado", "error") or time.time() - t0 > a.limite_min * 60:
                    break
            seg = time.time() - t0
            if t.get("estado") != "terminado":
                print(f"  {c.stem} (rep. {rep}): {t.get('estado', 'sin respuesta')} — {t.get('mensaje', '')[:160]}")
                for e in (t.get("errores") or [])[:8]:
                    print(f"      · {e}")
                if t.get("errores") and len(t["errores"]) > 8:
                    print(f"      · … y {len(t['errores']) - 8} más")
                if t.get("estado") == "error" and t.get("trabajo"):
                    print(f"      Respuesta completa del modelo: datos\\fallidos\\{t['trabajo']}.md")
                elif t.get("estado") in ("en_cola", "evaluando"):
                    print(f"      Superó el límite de {a.limite_min} min de este script, pero n8n sigue trabajando.")
                    print("      Cuando termine aparecerá en la página (Expedientes). Para compararlo entonces:")
                    print("      python pims-dpa-auditor_pruebas\\unsa\\comparar_con_referencia.py datos\\registro")
                fallidos.append(c.stem)
                continue
            d = http(a.n8n, "GET", f"pims/registro/detalle?id={t['id_registro']}")
            sufijo = f"_r{rep}" if a.repeticiones > 1 else ""
            (salida / f"{c.stem}{sufijo}.json").write_text(json.dumps(d["resultado"], ensure_ascii=False, indent=2), encoding="utf-8")
            (salida / f"{c.stem}{sufijo}.md").write_text(d["informe"] or "", encoding="utf-8")
            print(f"  {c.stem} (rep. {rep}): {t['puntaje']}/100 · {t['dictamen']} · {seg:.0f} s")

    if fallidos:
        print(f"\nNo terminaron {len(fallidos)} auditoría(s): revisa los mensajes de arriba.")
    if not list(salida.glob("*.json")):
        sys.exit("\nNinguna auditoría terminó: no hay nada que comparar.")
    print()
    subprocess.run([sys.executable, str(AQUI / "comparar_con_referencia.py"), str(salida), "--salida", str(salida / "comparacion.md")])


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    main()
