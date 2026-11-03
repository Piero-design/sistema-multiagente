#!/usr/bin/env python3
"""
instalar_flujos.py — Prepara e instala los flujos de n8n del PIMS en ESTA máquina.

    python n8n/instalar_flujos.py              # genera flujos y scripts de arranque
    python n8n/instalar_flujos.py --importar   # además los importa y publica en n8n (con n8n DETENIDO)

Qué hace:
  1. Detecta la carpeta del proyecto (RAIZ) y genera n8n/flujos_listos/*.json con esa ruta.
  2. Escribe n8n/iniciar_n8n.bat (Windows) y n8n/iniciar_n8n.sh (Linux/macOS) con las variables
     de entorno que necesita n8n 2.x:
       N8N_RESTRICT_FILE_ACCESS_TO = RAIZ   (n8n solo puede leer/escribir dentro del proyecto)
       NODES_EXCLUDE = []                   (habilita Execute Command: Claude Code y crear carpetas)
       GENERIC_TIMEZONE = America/Lima      (fechas de referencia y renovaciones)
       N8N_LISTEN_ADDRESS = 127.0.0.1       (n8n solo accesible desde este equipo)
  3. Con --importar: ejecuta `n8n import:workflow` y `n8n publish:workflow` para los 13 flujos.

Opciones: --sin-execute-command (no habilita Execute Command: sin Claude Code ni creación de carpetas)
          --zona America/Lima   --puerto 5678
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
IDS = ["PimsLeerArchivos", "PimsGuardarArchi", "PimsModeloIA0000", "PimsClaudeCode00", "PimsCrearCarpeta",
       "PimsBaseDatos000", "PimsAuditar00000", "PimsPerfilar0000", "PimsAprobaciones", "PimsRenovaciones", "PimsConsultas000",
       "PimsAdministrar0", "PimsPaginaWeb000", "PimsChat00000000"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--importar", action="store_true", help="Importar y publicar en n8n (n8n debe estar detenido)")
    ap.add_argument("--sin-execute-command", action="store_true")
    ap.add_argument("--zona", default="America/Lima")
    ap.add_argument("--puerto", type=int, default=5678)
    a = ap.parse_args()

    raiz = str(RAIZ.resolve()).replace("\\", "/")
    print(f"Proyecto (RAIZ): {raiz}\n")
    r = subprocess.run([sys.executable, str(AQUI / "construir_flujos.py"), "--raiz", raiz, "--puerto", str(a.puerto)], text=True)
    if r.returncode:
        sys.exit("No se pudieron construir los flujos.")

    excluir = "" if a.sin_execute_command else "[]"
    bat = [
        "@echo off",
        "REM Generado por n8n/instalar_flujos.py. Arranca n8n con la configuracion del PIMS.",
        "chcp 65001 > nul",
        f'set "N8N_RESTRICT_FILE_ACCESS_TO={raiz}"',
        f'set "GENERIC_TIMEZONE={a.zona}"',
        f'set "N8N_PORT={a.puerto}"',
        'set "N8N_LISTEN_ADDRESS=127.0.0.1"',
        'set "N8N_DIAGNOSTICS_ENABLED=false"',
        'set "N8N_PERSONALIZATION_ENABLED=false"',
        f'set "NODES_EXCLUDE={excluir}"' if excluir else 'REM Execute Command deshabilitado (sin Claude Code ni creacion de carpetas)',
        "echo.",
        f"echo   PIMS Privacy Guard - pagina: http://localhost:{a.puerto}/webhook/pims/app",
        f"echo   n8n (editor de flujos): http://localhost:{a.puerto}/",
        f"echo   Proyecto: {raiz}",
        "echo   Ctrl+C para detener",
        "echo.",
        "n8n start",
    ]
    sh = [
        "#!/bin/sh",
        "# Generado por n8n/instalar_flujos.py. Arranca n8n con la configuración del PIMS.",
        f'export N8N_RESTRICT_FILE_ACCESS_TO="{raiz}"',
        f'export GENERIC_TIMEZONE="{a.zona}" N8N_PORT={a.puerto} N8N_LISTEN_ADDRESS=127.0.0.1',
        "export N8N_DIAGNOSTICS_ENABLED=false N8N_PERSONALIZATION_ENABLED=false",
        f"export NODES_EXCLUDE='{excluir}'" if excluir else "# Execute Command deshabilitado",
        f'echo "PIMS Privacy Guard - página: http://localhost:{a.puerto}/webhook/pims/app"',
        f'echo "n8n (editor de flujos): http://localhost:{a.puerto}/"',
        "exec n8n start",
    ]
    (AQUI / "iniciar_n8n.bat").write_text("\r\n".join(bat) + "\r\n", encoding="utf-8")
    (AQUI / "iniciar_n8n.sh").write_text("\n".join(sh) + "\n", encoding="utf-8")
    try:
        (AQUI / "iniciar_n8n.sh").chmod(0o755)
    except OSError:
        pass
    print("\nScripts de arranque: n8n/iniciar_n8n.bat (Windows) · n8n/iniciar_n8n.sh (Linux/macOS)")

    if not a.importar:
        print("\nSiguiente paso (con n8n detenido):  python n8n/instalar_flujos.py --importar")
        return

    # En Windows, npm instala tres lanzadores: n8n (script sh, no ejecutable), n8n.cmd y n8n.ps1.
    # Algunas versiones de Python (3.12) devuelven el script sh con shutil.which("n8n"): WinError 193.
    if os.name == "nt":
        n8n = shutil.which("n8n.cmd") or shutil.which("n8n.exe")
    else:
        n8n = shutil.which("n8n")
    if not n8n:
        sys.exit("\nNo se encontró el comando 'n8n'. Instálalo con:  npm install -g n8n   (requiere Node.js 24 o superior)")
    print(f"\nImportando con {n8n} …")
    r = subprocess.run([n8n, "import:workflow", "--separate", f"--input={AQUI / 'flujos_listos'}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit(f"Falló la importación:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    fallos = []
    for wid in IDS:
        r = subprocess.run([n8n, "publish:workflow", f"--id={wid}"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        print(f"  publicado {wid}" if r.returncode == 0 else f"  ERROR al publicar {wid}")
        if r.returncode:
            fallos.append((wid, (r.stderr or r.stdout)[-400:]))
    if fallos:
        for wid, err in fallos:
            print(f"\n{wid}: {err}")
        sys.exit("\nAlgunos flujos no se publicaron (ver arriba).")
    print("\nListo. Arranca n8n con n8n\\iniciar_n8n.bat (Windows) o n8n/iniciar_n8n.sh y abre:")
    print(f"  http://localhost:{a.puerto}/webhook/pims/app")


if __name__ == "__main__":
    main()
