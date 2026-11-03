#!/usr/bin/env python3
"""
equivalencia_perfil.py — Demuestra que n8n/lib/perfil.js valida perfiles igual que
pims-perfilador-organizacion/scripts/validar_perfil.py (mismos errores y advertencias, en el mismo orden).

    python n8n/pruebas/equivalencia_perfil.py [--casos 1500]

Casos: perfil de referencia, perfil contaminado, plantilla vacía y N mutaciones aleatorias
(borrar líneas, cambiar fuentes, estados, valores de DPA, insertar juicios de cumplimiento…).
"""
import argparse
import importlib.util
import json
import random
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("vp", RAIZ / "pims-perfilador-organizacion/scripts/validar_perfil.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)

BASES = [
    RAIZ / "pims-dpa-auditor_pruebas/organizaciones_prueba/altiplano_con_perfil/perfil_organizacion.md",
    RAIZ / "pims-dpa-auditor_pruebas/organizaciones_prueba/perfil_contaminado.md",
    RAIZ / "pims-perfilador-organizacion/assets/plantilla_perfil.md",
]
MUTACIONES = [
    lambda l, r: "",                                                     # borrar línea
    lambda l, r: l.replace("[D1", "[D7"),                                # fuente inexistente
    lambda l, r: l.replace("Desconocido", r.choice(["Sí", "No", "Tal vez", "**Sí**", "Sí, homologado"])),
    lambda l, r: l.replace("Borrador", r.choice(["Aprobado", "Validado por DPO (Ana, 2026-10-13)", "borrador"])),
    lambda l, r: l.rstrip(" |") + " | el proveedor cumple y está exento |" if l.startswith("|") else l,
    lambda l, r: l.replace("## 5.", "## 9.") if l.startswith("## 5.") else l,
    lambda l, r: l.replace("Supuesto", ""),
    lambda l, r: l + "\n| |  |  |  |",
    lambda l, r: l.replace("f0ad22", "zz"),
    lambda l, r: l.replace("## Documentos fuente", "## Fuentes"),
]


def mutar(texto, rnd):
    lineas = texto.split("\n")
    for _ in range(rnd.randint(1, 4)):
        i = rnd.randrange(len(lineas))
        lineas[i] = rnd.choice(MUTACIONES)(lineas[i], rnd)
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", type=int, default=1500)
    a = ap.parse_args()
    rnd = random.Random(16)
    textos = [b.read_text(encoding="utf-8") for b in BASES]
    casos = list(textos) + [mutar(rnd.choice(textos), rnd) for _ in range(a.casos)]

    js = subprocess.run(["node", "-e", """
const P = require(process.argv[1]);
let s=''; process.stdin.on('data', d => s += d).on('end', () => {
  process.stdout.write(JSON.stringify(JSON.parse(s).map(t => P.validar(t))));
});""", str(RAIZ / "n8n/lib/perfil.js")], input=json.dumps(casos), capture_output=True, text=True, encoding="utf-8")
    if js.returncode:
        sys.exit(js.stderr)
    salida_js = json.loads(js.stdout)

    fallas = 0
    validos = 0
    for i, (t, j) in enumerate(zip(casos, salida_js)):
        p = vp.validar(t)
        validos += p["valido"]
        if p != j:
            fallas += 1
            if fallas <= 3:
                print(f"DIFERENCIA en caso {i}:\n  py={json.dumps(p, ensure_ascii=False)[:600]}\n  js={json.dumps(j, ensure_ascii=False)[:600]}")
    print(f"Perfiles comparados: {len(casos)} ({validos} válidos, {len(casos) - validos} inválidos)")
    print("Resultado: IDÉNTICOS" if not fallas else f"Resultado: {fallas} DIFERENCIAS")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
