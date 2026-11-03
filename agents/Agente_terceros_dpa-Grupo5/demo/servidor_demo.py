#!/usr/bin/env python3
"""
servidor_demo.py — Servidor local de la demo del Agente 7 (PIMS DPA Auditor).

Hace dos cosas a la vez:

  1. Sirve los archivos estáticos de esta carpeta (index.html, app.js, corpus.js).
  2. Expone POST /api/auditar, que lanza el CLI de Claude Code en modo headless
     (`claude -p`) y reemite su salida al navegador como Server-Sent Events.

Así la demo funciona **sin API Key**: la inferencia la hace el CLI de Claude Code
con la suscripción del usuario. Nada sale de la máquina más allá de lo que el
propio CLI ya hace; este servidor solo habla con `claude` por stdin/stdout.

Uso:
    python servidor_demo.py                 # http://localhost:8000
    python servidor_demo.py --puerto 8080
    python servidor_demo.py --permitir-script   # habilita Bash (ver más abajo)

Requisitos: Python 3.9+ (solo biblioteca estándar) y Claude Code autenticado
(`claude` en el PATH).

----------------------------------------------------------------------------
Nota de seguridad sobre --permitir-script
----------------------------------------------------------------------------
Por defecto el agente corre **sin herramientas que ejecuten o escriban**. El
texto del contrato es contenido no confiable (la propia regla de rigor 7 de la
skill lo dice, y uno de los contratos de prueba contiene un intento de inyección
de instrucciones). Darle Bash al agente con ese texto en contexto convertiría una
inyección en ejecución de código.

El coste de esa decisión es que el Paso 8 de la skill se resuelve con las
fórmulas aplicadas a mano y la trazabilidad queda en `calculo: "manual"`, que es
la vía alterna que SKILL.md contempla expresamente.

`--permitir-script` habilita Bash y Write para que el agente pueda ejecutar
`calcular_resultado.py` y obtener `calculo: "script"`. Úsalo solo con contratos
en los que confíes, nunca con uno pegado por un tercero.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent

# Modelo por defecto si el navegador no indica otro.
MODELO_POR_DEFECTO = "claude-sonnet-4-6"

# Tope del system prompt que acepta el endpoint, como sanidad básica.
MAX_SYSTEM = 400_000
MAX_CONTRATO = 400_000

# Herramientas del agente.
#   Modo seguro (por defecto): puede consultar la skill instalada y leer sus
#   archivos de referencia, pero no ejecuta ni escribe nada.
#   Modo script (--permitir-script): añade Bash y Write para calcular con el
#   script. Ver la nota de seguridad de la cabecera.
HERRAMIENTAS_SEGURAS = "Skill,Read,Glob,Grep"
HERRAMIENTAS_SCRIPT = "Skill,Read,Glob,Grep,Bash,Write"
HERRAMIENTAS_VETADAS_SEGURAS = (
    "Bash,PowerShell,Write,Edit,NotebookEdit,WebFetch,WebSearch,Task"
)
HERRAMIENTAS_VETADAS_SCRIPT = "PowerShell,Edit,NotebookEdit,WebFetch,WebSearch,Task"

# Un solo análisis a la vez: cada uno es un agente de un par de minutos.
_ocupado = threading.Lock()


def ruta_claude() -> str:
    """Localiza el ejecutable del CLI de Claude Code."""
    ruta = shutil.which("claude")
    if not ruta:
        sys.exit(
            "No se encontró el ejecutable 'claude' en el PATH.\n"
            "Instala Claude Code y comprueba que `claude --version` responde."
        )
    return ruta


class Handler(SimpleHTTPRequestHandler):
    """Sirve los archivos de la demo y atiende POST /api/auditar."""

    # Inyectados desde main()
    claude_bin = ""
    permitir_script = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DEMO_DIR), **kwargs)

    # --- Registro más corto y legible -------------------------------------

    def log_message(self, formato, *args):  # noqa: A002
        sys.stderr.write("  %s\n" % (formato % args))

    # --- Cabeceras --------------------------------------------------------

    def end_headers(self):
        # La demo es local: evita que el navegador sirva una versión cacheada
        # de app.js o corpus.js tras regenerarlos. No se añade a las respuestas
        # informativas (100 Continue), donde no tiene sentido.
        if getattr(self, "_codigo_enviado", 200) >= 200:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_response_only(self, code, message=None):
        self._codigo_enviado = int(code)
        super().send_response_only(code, message)

    # --- POST /api/auditar ------------------------------------------------

    def do_POST(self):  # noqa: N802
        if self.path.rstrip("/") != "/api/auditar":
            self.send_error(404, "Ruta no encontrada")
            return

        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            self.send_error(400, "Content-Length inválido")
            return

        if largo <= 0 or largo > (MAX_SYSTEM + MAX_CONTRATO + 10_000):
            self.send_error(413, "Cuerpo de la petición fuera de rango")
            return

        try:
            peticion = json.loads(self.rfile.read(largo).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_error(400, f"JSON inválido: {exc}")
            return

        system = (peticion.get("system") or "").strip()
        contrato = (peticion.get("contrato") or "").strip()
        proveedor = (peticion.get("proveedor") or "").strip()
        modelo = (peticion.get("modelo") or MODELO_POR_DEFECTO).strip()

        if not contrato:
            self.send_error(400, "Falta el texto del contrato")
            return
        if len(system) > MAX_SYSTEM or len(contrato) > MAX_CONTRATO:
            self.send_error(413, "El system prompt o el contrato son demasiado largos")
            return

        if not _ocupado.acquire(blocking=False):
            self.send_response(409)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"error": "Ya hay una auditoría en curso. Espera a que termine."},
                    ensure_ascii=False,
                ).encode("utf-8")
            )
            return

        try:
            self._auditar(system, contrato, proveedor, modelo)
        finally:
            _ocupado.release()

    # --- Lanzamiento del agente y reemisión por SSE -----------------------

    def _sse(self, payload: str) -> bool:
        """Envía un evento SSE. Devuelve False si el navegador cerró."""
        try:
            self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
            self.wfile.flush()
            return True
        except (BrokenPipeError, ConnectionResetError, OSError):
            return False

    def _auditar(self, system: str, contrato: str, proveedor: str, modelo: str):
        mensaje = "Evalúa este DPA para el registro de proveedores del PIMS."
        if proveedor:
            mensaje += f"\n\nProveedor indicado por el usuario: {proveedor}"
        mensaje += f"\n\n[CONTRATO]\n{contrato}\n[/CONTRATO]"

        # El system prompt no puede ir como argumento: en Windows la línea de
        # comandos está limitada a 32 767 caracteres y el corpus de la skill
        # ronda los 43 000. Por eso se entrega en un archivo temporal.
        archivo_system = None
        if system:
            fd, archivo_system = tempfile.mkstemp(
                prefix="pims_system_", suffix=".txt", text=True
            )
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(system)

        permitidas = HERRAMIENTAS_SCRIPT if self.permitir_script else HERRAMIENTAS_SEGURAS
        vetadas = (
            HERRAMIENTAS_VETADAS_SCRIPT
            if self.permitir_script
            else HERRAMIENTAS_VETADAS_SEGURAS
        )

        cmd = [self.claude_bin, "-p"]
        if archivo_system:
            cmd += ["--append-system-prompt-file", archivo_system]
        cmd += [
            "--model", modelo,
            "--allowedTools", permitidas,
            "--disallowedTools", vetadas,
            "--permission-mode", "dontAsk",
            "--output-format", "stream-json",
            "--include-partial-messages",
            "--verbose",
        ]

        print(f"\n  → auditando ({modelo}, herramientas: {permitidas})", flush=True)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        # Desactiva el buffering de cualquier proxy intermedio.
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        proceso = None
        try:
            proceso = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(DEMO_DIR),
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            # El prompt va por stdin: así no le afecta el límite de la línea
            # de comandos y no aparece en la lista de procesos.
            proceso.stdin.write(mensaje)
            proceso.stdin.close()

            errores = []
            hilo_err = threading.Thread(
                target=lambda: errores.extend(proceso.stderr.readlines()), daemon=True
            )
            hilo_err.start()

            vivo = True
            for linea in proceso.stdout:
                linea = linea.strip()
                if not linea:
                    continue
                if not self._sse(linea):
                    vivo = False
                    break

            if vivo:
                codigo = proceso.wait()
            else:
                # El navegador cerró. Hay que matar el proceso ya: si solo
                # esperásemos, el hijo se bloquearía escribiendo en un stdout
                # que nadie lee y wait() no volvería nunca.
                print("  (el navegador cerró la conexión, se cancela el agente)", flush=True)
                proceso.kill()
                try:
                    codigo = proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    codigo = -1

            hilo_err.join(timeout=2)

            if vivo:
                detalle = "".join(errores).strip()[-1500:]
                self._sse(
                    json.dumps(
                        {
                            "type": "shim_fin",
                            "codigo": codigo,
                            "stderr": detalle,
                        },
                        ensure_ascii=False,
                    )
                )
            print(f"  ← terminado (código {codigo})", flush=True)

        except Exception as exc:  # noqa: BLE001
            self._sse(
                json.dumps(
                    {"type": "shim_error", "mensaje": f"{type(exc).__name__}: {exc}"},
                    ensure_ascii=False,
                )
            )
            print(f"  ✗ error del shim: {exc}", file=sys.stderr, flush=True)
        finally:
            if proceso and proceso.poll() is None:
                proceso.kill()
            if archivo_system:
                try:
                    os.unlink(archivo_system)
                except OSError:
                    pass


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--puerto", type=int, default=8000, help="Puerto (por defecto 8000)")
    ap.add_argument(
        "--permitir-script",
        action="store_true",
        help="Habilita Bash y Write para que el agente ejecute calcular_resultado.py "
        "(calculo: \"script\"). Lee la nota de seguridad de la cabecera del archivo.",
    )
    args = ap.parse_args()

    Handler.claude_bin = ruta_claude()
    Handler.permitir_script = args.permitir_script

    # Solo localhost: la demo no se expone a la red.
    servidor = ThreadingHTTPServer(("127.0.0.1", args.puerto), Handler)

    modo = "script (Bash habilitado)" if args.permitir_script else "seguro (sin ejecución)"
    print("")
    print("  PIMS Privacy Guard · Auditor de DPAs — servidor de demo")
    print("  " + "-" * 54)
    print(f"  Abre:        http://localhost:{args.puerto}/")
    print(f"  CLI:         {Handler.claude_bin}")
    print(f"  Modo:        {modo}")
    print("  Inferencia:  Claude Code con tu suscripción (sin API Key)")
    print("  Escuchando:  127.0.0.1 solamente")
    print("  Ctrl+C para detener")
    print("")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n  detenido")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
