"""Loads DEMONSTRATION data (fictitious UNSA) through the platform API so agents have something to work with:
G6 inventory with the systems that Group 8's example incidents talk about.
Usage:  python scripts/seed_demo_data.py [http://localhost:8080]
Only field NAMES are registered (never values), and every asset stays 'pendiente_validacion'."""
import json
import sys
import time
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
ORG = "UNSA-DEMO"

SYSTEMS = [
    ("Registro Académico", "registro-academico", "dni,nombres,apellidos,correo_institucional,codigo_estudiante,promedio_ponderado,situacion_academica",
     "Gestionar la trayectoria académica de estudiantes", "Estudiantes", "Oficina de Registro Académico (ficticia)"),
    ("SISACAD (notas)", "sisacad-notas", "codigo_estudiante,dni,curso,nota_final,docente,fecha_registro,usuario_modificacion",
     "Registrar y consultar calificaciones", "Estudiantes", "Dirección de Estudios (ficticia)"),
    ("Portal de admisión", "portal-admision", "dni,nombres,apellidos,correo,telefono,fecha_nacimiento,colegio_procedencia,puntaje_examen",
     "Gestionar postulaciones e ingreso", "Postulantes; Ingresantes", "Oficina de Admisión (ficticia)"),
    ("Planilla CAS", "planilla-cas", "dni,nombres,apellidos,cargo,remuneracion,cuenta_bancaria,regimen_pensionario",
     "Pago de remuneraciones del personal CAS", "Personal administrativo", "Oficina de Recursos Humanos (ficticia)"),
]


def call(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "User-Agent": "pims-seed-demo/1.0"})   # proxies (e.g. Cloudflare) reject the default Python agent
    return json.load(urllib.request.urlopen(req, timeout=60))


def run(agent, action, inp):
    eid = call(f"/api/agents/{agent}/execute", {"action": action, "input": inp})["execution_id"]
    for _ in range(60):
        e = json.load(urllib.request.urlopen(urllib.request.Request(f"{BASE}/api/executions/{eid}", headers={"User-Agent": "pims-seed-demo/1.0"}), timeout=30))
        if e["status"] in ("succeeded", "failed"):
            return e
        time.sleep(1.5)
    raise TimeoutError(eid)


for nombre, slug, columnas, finalidad, titulares, responsable in SYSTEMS:
    e = run("inventario", "registrar_activos", {"organizacion": ORG, "fuentes": [{
        "id": f"{slug}-fuente-1", "nombre": f"Esquema de {nombre} (ficticio)", "sistema": nombre, "formato": "csv",
        "contenido": columnas.replace(",", ",") + "\n" + ",".join("x" for _ in columnas.split(",")),
        "contexto": {"finalidad": finalidad + " (declaración ficticia)", "titulares": [t.strip() for t in titulares.split(";")],
                     "responsable": responsable}}]})
    d = (e.get("result") or {}).get("output", {}).get("data", {})
    print(f"{nombre:22s} {e['status']:9s} campos={d.get('total_campos')} registro={d.get('registro')}", e.get("error") or "")
