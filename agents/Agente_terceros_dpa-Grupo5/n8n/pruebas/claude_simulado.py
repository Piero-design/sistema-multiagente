#!/usr/bin/env python3
"""
claude_simulado.py — Imita `claude -p ... --append-system-prompt-file F --output-format json < mensaje`
para probar el flujo "PIMS · Claude Code" sin el CLI real. Reenvía la petición a modelo_simulado.py.

En pruebas se instala como un ejecutable llamado `claude` al principio del PATH de n8n
(o se configura su ruta en datos/config_modelo.json → claude_bin).
Variable opcional: MODELO_SIMULADO_URL (por defecto http://127.0.0.1:11435).
"""
import json
import os
import sys
import urllib.request

args = sys.argv[1:]
system = ""
if "--append-system-prompt-file" in args:
    with open(args[args.index("--append-system-prompt-file") + 1], encoding="utf-8") as fh:
        system = fh.read()
modelo = args[args.index("--model") + 1] if "--model" in args else None
prohibidas = args[args.index("--disallowedTools") + 1] if "--disallowedTools" in args else ""
if "-p" not in args or "Bash" not in prohibidas:
    print(json.dumps({"type": "result", "subtype": "error_args", "is_error": True, "result": f"argumentos inesperados: {args}"}))
    sys.exit(1)
mensaje = sys.stdin.buffer.read().decode("utf-8")
url = os.environ.get("MODELO_SIMULADO_URL", "http://127.0.0.1:11435") + "/claude"
peticion = urllib.request.Request(url, data=json.dumps({"system": system, "mensaje": mensaje, "modelo": modelo}).encode("utf-8"),
                                  headers={"Content-Type": "application/json"})
with urllib.request.urlopen(peticion, timeout=120) as r:
    sys.stdout.write(r.read().decode("utf-8"))
