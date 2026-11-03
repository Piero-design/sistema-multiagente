#!/usr/bin/env python3
"""
configurar_bd.py — Conecta n8n con la base del PIMS (fase 5 del plan, bd/PLAN_MIGRACION_BD.md).

    python n8n/configurar_bd.py                     # con n8n DETENIDO
    python n8n/configurar_bd.py --desactivar        # vuelve a trabajar solo con archivos

1. Comprueba con psql que el rol agente7 entra a la base y ve las funciones del Agente 7.
2. Crea (o reemplaza) en n8n la credencial Postgres "PIMS Postgres" con el id fijo que usan los flujos.
   La contraseña se pide por teclado, se pasa a `n8n import:credentials` en un archivo temporal que se
   borra al terminar, y n8n la guarda cifrada.
3. Activa la base en datos/config_bd.json con el id del usuario autor (demo.auth_user, username agente7).

Requisitos: bd/instalar_bd.ps1 ya ejecutado y n8n detenido (como para instalar_flujos.py --importar).
"""
import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
from construir_flujos import CREDENCIAL_BD  # noqa: E402

CONFIG = RAIZ / "datos" / "config_bd.json"


def psql_bin():
    p = shutil.which("psql")
    if p:
        return p
    for v in ("18", "17", "16"):
        c = Path(rf"C:\Program Files\PostgreSQL\{v}\bin\psql.exe")
        if c.exists():
            return str(c)
    sys.exit("No encuentro psql: agrega la carpeta bin de PostgreSQL al PATH.")


def n8n_bin():
    n = (shutil.which("n8n.cmd") or shutil.which("n8n.exe")) if os.name == "nt" else shutil.which("n8n")
    if not n:
        sys.exit("No encuentro el comando 'n8n'.")
    return n


def guardar_config(cambios):
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    cfg.update(cambios)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--servidor", default="localhost")
    ap.add_argument("--puerto", type=int, default=5432)
    ap.add_argument("--base", default="gestitel_revision")
    ap.add_argument("--usuario", default="agente7")
    ap.add_argument("--esquema", default="demo")
    ap.add_argument("--desactivar", action="store_true")
    a = ap.parse_args()

    if a.desactivar:
        guardar_config({"activo": False})
        print("Base desactivada en datos/config_bd.json: el agente vuelve a escribir solo archivos.")
        return

    clave = getpass.getpass(f"Contraseña del rol {a.usuario}: ")
    if not clave:
        sys.exit("Contraseña vacía.")

    # 1. ¿Entra agente7 y ve el módulo?
    env = dict(os.environ, PGPASSWORD=clave, PGCLIENTENCODING="UTF8")
    r = subprocess.run([psql_bin(), "-X", "-At", "-h", a.servidor, "-p", str(a.puerto), "-U", a.usuario, "-d", a.base,
                        "-c", f"SELECT id FROM {a.esquema}.auth_user WHERE username = 'agente7'",
                        "-c", f"SELECT has_function_privilege('{a.esquema}.agente7_guardar_auditoria(jsonb, text, integer)', 'EXECUTE')"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode:
        sys.exit(f"El rol {a.usuario} no pudo conectarse:\n{r.stderr.strip()}")
    lineas = r.stdout.split()
    if len(lineas) < 2 or lineas[1] != "t":
        sys.exit(f"Conecta, pero falta el usuario autor o el permiso sobre las funciones (¿se ejecutó bd/instalar_bd.ps1?). Salida: {r.stdout!r}")
    autor = int(lineas[0])
    print(f"Conexión correcta como {a.usuario}; usuario autor agente7 = {autor}.")

    # 2. Credencial en n8n
    cred = [{"id": CREDENCIAL_BD["id"], "name": CREDENCIAL_BD["name"], "type": "postgres",
             "data": {"host": a.servidor, "database": a.base, "user": a.usuario, "password": clave,
                      "port": a.puerto, "ssl": "disable", "allowUnauthorizedCerts": False, "sshTunnel": False}}]
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(cred, fh)
        r = subprocess.run([n8n_bin(), "import:credentials", f"--input={tmp}"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    if r.returncode:
        sys.exit(f"n8n no importó la credencial (¿n8n está detenido?):\n{(r.stderr or r.stdout)[-1500:]}")
    print(f"Credencial '{CREDENCIAL_BD['name']}' guardada en n8n (id {CREDENCIAL_BD['id']}).")

    # 3. Activar
    guardar_config({"activo": True, "esquema": a.esquema, "usuario_autor_id": autor})
    print("Base activada en datos/config_bd.json. Arranca n8n con n8n\\iniciar_n8n.bat.")


if __name__ == "__main__":
    main()
