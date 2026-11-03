#!/usr/bin/env python3
"""
migrar_registros.py — Carga en PostgreSQL los expedientes que el agente ya calculó, sin volver a
llamar al modelo (fase 7 del plan, bd/PLAN_MIGRACION_BD.md).

    python bd/migrar_registros.py                      # fuentes por defecto
    python bd/migrar_registros.py datos/registro/X.json # archivos concretos
    python bd/migrar_registros.py --solo-registro      # solo datos/registro/

Fuentes por defecto:
  - datos/registro/*.json                            expedientes reales de n8n (con su informe .md e historial)
  - pims-dpa-auditor_pruebas/resultados/*.json       NubeAndina, AndesCloud, DigiServ
  - pims-dpa-auditor_pruebas/unsa/esperado/*.json    los 5 contratos de la UNSA

Cada registro pasa por demo.agente7_guardar_auditoria(), la MISMA función que llama n8n, así que la
traducción a la base es idéntica. El historial de aprobaciones se reproduce en orden con
demo.agente7_registrar_decision(). Los que ya estén en la base se omiten.

Conexión: variables estándar de PostgreSQL (PGHOST, PGPORT, PGUSER, PGDATABASE, PGPASSWORD o
pgpass.conf). Usa psql, sin dependencias de Python. Por defecto PGDATABASE=gestitel_revision.
"""
import argparse
import glob
import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTES = ["datos/registro/*.json",
           "pims-dpa-auditor_pruebas/resultados/*.json",
           "pims-dpa-auditor_pruebas/unsa/esperado/*.json"]


def buscar_psql():
    p = shutil.which("psql")
    if p:
        return p
    for v in ("18", "17", "16", "15", "14", "13"):
        c = Path(rf"C:\Program Files\PostgreSQL\{v}\bin\psql.exe")
        if c.exists():
            return str(c)
    sys.exit("No encuentro psql. Agrega la carpeta bin de PostgreSQL al PATH.")


def literal(texto):
    """Literal SQL con dollar-quoting y una etiqueta que no aparece en el texto (sin escapar nada)."""
    if texto is None:
        return "NULL"
    while True:
        tag = "$m" + secrets.token_hex(4) + "$"
        if tag not in texto:
            return f"{tag}{texto}{tag}"


def psql(sql, esquema):
    env = dict(os.environ, PGCLIENTENCODING="UTF8")
    env.setdefault("PGDATABASE", "gestitel_revision")
    r = subprocess.run([buscar_psql(), "-X", "-q", "-At", "-v", "ON_ERROR_STOP=1",
                        "-c", f"SET search_path TO {esquema}, public", "-f", "-"],
                       input=sql, capture_output=True, text=True, encoding="utf-8", env=env)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def preparar(ruta):
    reg = json.loads(Path(ruta).read_text(encoding="utf-8"))
    meta = reg.setdefault("_registro", {})
    meta.setdefault("id_registro", reg.get("id_evaluacion"))
    # Resultados de referencia (no los produjo un modelo en n8n)
    meta.setdefault("proveedor", "referencia")
    meta.setdefault("modelo", "referencia")
    md = Path(ruta).with_suffix(".md")
    return reg, (md.read_text(encoding="utf-8") if md.exists() else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--esquema", default="demo")
    ap.add_argument("--autor", default="agente7", help="username de demo.auth_user que firma los registros")
    ap.add_argument("--solo-registro", action="store_true")
    a = ap.parse_args()

    archivos = a.archivos or sorted(f for patron in (FUENTES[:1] if a.solo_registro else FUENTES)
                                    for f in glob.glob(str(RAIZ / patron)))
    autor = psql(f"SELECT id FROM auth_user WHERE username = {literal(a.autor)}", a.esquema)
    if not autor:
        sys.exit(f"No existe el usuario '{a.autor}' en {a.esquema}.auth_user (paso 4.1 del plan).")

    cargados = omitidos = errores = 0
    for ruta in archivos:
        reg, md = preparar(ruta)
        codigo = reg["_registro"]["id_registro"]
        nombre = Path(ruta).name
        if psql(f"SELECT 1 FROM core_dpaassessment WHERE assessment_code = {literal(codigo)}", a.esquema):
            print(f"  ya está   {codigo:32} {nombre}")
            omitidos += 1
            continue
        sql = [f"BEGIN;",
               f"SELECT agente7_guardar_auditoria({literal(json.dumps(reg, ensure_ascii=False))}::jsonb, "
               f"{literal(md)}, {autor});"]
        for ev in (reg.get("aprobacion") or {}).get("historial") or []:
            sql.append("SELECT agente7_registrar_decision("
                       + ", ".join(literal(str(x)) if x is not None else "NULL" for x in (
                           codigo, ev.get("rol"), ev.get("decision"), ev.get("usuario"),
                           ev.get("cargo"), ev.get("comentario")))
                       + f", {literal(ev.get('fecha'))}::timestamptz);")
        sql.append("COMMIT;")
        try:
            psql("\n".join(sql), a.esquema)
        except RuntimeError as e:
            print(f"  ERROR     {codigo:32} {nombre}\n            {e}")
            errores += 1
            continue
        fila = psql(f"SELECT score::int, verdict, approval_status, "
                    f"(SELECT count(*) FROM core_dpacontrolresult WHERE assessment_id = a.id) "
                    f"FROM core_dpaassessment a WHERE assessment_code = {literal(codigo)}", a.esquema)
        puntaje, dictamen, estado, ncontroles = fila.split("|")
        igual = int(puntaje) == reg["puntaje_proveedor"]["valor"]
        print(f"  {'cargado ' if igual else 'DISTINTO'}  {codigo:32} {puntaje:>3} {dictamen} {estado} "
              f"{ncontroles} controles  {nombre}")
        cargados += 1
        errores += 0 if igual else 1

    print()
    print(psql("SELECT 'core_thirdparty ' || count(*) FROM core_thirdparty "
               "UNION ALL SELECT 'core_dpacontract ' || count(*) FROM core_dpacontract "
               "UNION ALL SELECT 'core_dpaassessment ' || count(*) FROM core_dpaassessment "
               "UNION ALL SELECT 'core_dpacontrolresult ' || count(*) FROM core_dpacontrolresult "
               "UNION ALL SELECT 'core_dpaapproval ' || count(*) FROM core_dpaapproval", a.esquema))
    print(f"\n{cargados} cargados · {omitidos} ya estaban · {errores} con error")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
