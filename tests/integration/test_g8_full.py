"""Agent 8 (incidents and breaches): complete functional checks, alone and used by the other agents.
Cloud mode, real model calls; assertions are structural (the model's wording varies) or exact for rules.
Run: pytest tests/integration/test_g8_full.py -q -s"""
import json
import subprocess

import httpx
import pytest

from test_platform import BASE, get, run
from test_human import login, post, psql


def g8_node(code: str) -> str:
    """Runs JavaScript inside G8's own container (same view as the agent's internal tools)."""
    p = subprocess.run(["docker", "compose", "exec", "-T", "agent-g8", "node", "-e", code], capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stderr[-400:]
    return p.stdout.strip()


def out(e):
    assert e["status"] == "succeeded", e.get("error")
    return e["result"]["output"]


MAIL = ("Un funcionario envio por error una hoja de calculo con DNI y notas de 300 estudiantes "
        "a una lista externa de correo de la universidad.")
DDOS = ("El portal de matricula estuvo caido 3 horas por un ataque de denegacion de servicio. "
        "No hay evidencia de acceso ni exfiltracion de datos; los datos de los estudiantes no fueron expuestos.")


# ---------------------------------------------------------------- skills: it must tell the cases apart
def test_g8_breach_generates_the_three_drafts_and_the_48h_clock():
    o = out(run("incidentes", "analizar", {"reporte": MAIL}, wait=480))
    x = out(run("incidentes", "expediente", {"id": o["incidente"]}))
    names = " ".join(x["files"])
    assert "notificacion-anpd" in names and "comunicacion-titulares" in names and "aviso-cnsd" in names
    assert x["limite"] and "ficha" in names and "severidad" in names and "cierre" in names
    assert "brecha" in x["docs"]["00-informe.md"].lower()


def test_g8_non_breach_does_not_generate_notifications():
    o = out(run("incidentes", "analizar", {"reporte": DDOS}, wait=480))
    x = out(run("incidentes", "expediente", {"id": o["incidente"]}))
    names = " ".join(x["files"])
    assert "notificacion-anpd" not in names and "comunicacion-titulares" not in names     # nothing to notify
    informe = x["docs"]["00-informe.md"].lower()
    assert "sin brecha" in informe or "no constituye" in informe or "no hay brecha" in informe


def test_g8_uses_a_user_supplied_context():
    ctx_files = [{"ruta": "politica-demo.md", "texto": "# Politica (ficticia)\nEl responsable de seguridad del Posgrado es la Dra. Prueba. Contacto: seguridad-posgrado@example.invalid"}]
    r = g8_node("fetch('http://localhost:3100/api/contexto',{method:'POST',headers:{'content-type':'application/json'},"
                f"body:JSON.stringify({{nombre:'prueba-g8',archivos:{json.dumps(ctx_files)}}})}}).then(r=>r.json()).then(j=>console.log(JSON.stringify(j)))")
    assert "contextos/prueba-g8" in r
    try:
        o = out(run("incidentes", "analizar", {"reporte": "Un docente del Posgrado reporta accesos extranos a la plataforma de tesis desde una IP desconocida. " * 2,
                                              "contexto": "contextos/prueba-g8"}, wait=480))
        events = " ".join(e["texto"] for e in o.get("eventos", []))
        assert "prueba-g8" in events                                   # the agent opened the uploaded context
    finally:
        g8_node("fetch('http://localhost:3100/api/contexto?c=contextos/prueba-g8',{method:'DELETE'}).then(()=>console.log('ok'))")


# ---------------------------------------------------------------- the agent's own app surface
def test_g8_original_app_surface_is_intact():
    r = g8_node("Promise.all(['/api/estado','/api/config','/api/archivos-demo','/api/autonomia'].map(p=>fetch('http://localhost:3100'+p).then(r=>r.json())))"
                ".then(([e,c,d,a])=>console.log(JSON.stringify({skills:e.skills,agente:e.agente,ejemplos:c.ejemplos.length,"
                "reportes:d.reportes.length,contexto:d.contexto.length,config:a.config,error:a.error_config})))")
    j = json.loads(r)
    assert j["skills"] == 4 and j["agente"] is True
    assert j["ejemplos"] >= 9 and j["reportes"] == 10 and j["contexto"] == 3
    assert j["error"] is None and j["config"] == "config/conectores.json"


def test_g8_complaints_webhook_needs_the_token():
    js = ("const t=process.env.BUZON_WEBHOOK_TOKEN;const body=JSON.stringify({asunto:'prueba',remitente:'x@example.invalid',texto:'Texto de prueba suficientemente largo.'});"
          "const f=(h)=>fetch('http://localhost:3100/api/buzon/webhook/quejas-web',{method:'POST',headers:{'content-type':'application/json',...h},body}).then(r=>r.status);"
          "Promise.all([f({}),f({'x-webhook-token':'malo'}),f({'x-webhook-token':t})]).then(s=>console.log(JSON.stringify(s)))")
    assert json.loads(g8_node(js)) == [401, 401, 202]


# ---------------------------------------------------------------- used BY the platform and the other agents
def test_g8_reads_the_other_agents_through_its_connectors_read_only():
    # seed G6 so there is something to find
    run("inventario", "registrar_activos", {"organizacion": "UNSA-DEMO", "fuentes": [{
        "id": "registro-academico-fuente-1", "nombre": "Esquema de Registro Academico (ficticio)", "sistema": "Registro Academico", "formato": "csv",
        "contenido": "dni,nombres,correo_institucional,promedio_ponderado\nx,x,x,x",
        "contexto": {"finalidad": "Gestionar la trayectoria academica (ficticia)", "titulares": ["Estudiantes"], "responsable": "Registro Academico (ficticio)"}}]})
    run("terceros", "registro", {"organizacion": "unsa"})
    code = ("const c=require('./web/autonomia/conectores');(async()=>{const r={};"
            "r.sistemas=((await c.ejecutar('ListarSistemas',{})).sistemas||[]).map(s=>s.id);"
            "const inv=await c.ejecutar('ConsultarSistema',{sistema:'inventario-g6',ruta:'/api/inventario',consulta:'organizacion=UNSA-DEMO'});"
            "r.g6=(JSON.parse(inv.respuesta||'{}').data||{}).total_activos;"
            "const k=await c.ejecutar('ConsultarSistema',{sistema:'controles-g7',ruta:'/api/controles/catalogo'});r.g7=JSON.parse(k.respuesta).length;"
            "const t=await c.ejecutar('ConsultarSistema',{sistema:'terceros-g5',ruta:'/webhook/pims/registro',consulta:'organizacion=unsa'});r.g5=JSON.parse(t.respuesta).total;"
            "r.bloqueos=[(await c.ejecutar('ConsultarSistema',{sistema:'terceros-g5',ruta:'/webhook/pims/aprobar'})).error,"
            "(await c.ejecutar('ConsultarSistema',{sistema:'inventario-g6',ruta:'/api/ejecutar'})).error];"
            "console.log(JSON.stringify(r))})()")
    r = json.loads(g8_node(code))
    assert {"inventario-g6", "controles-g7", "terceros-g5"} <= set(r["sistemas"])
    assert r["g6"] >= 1 and r["g7"] == 10 and r["g5"] >= 1
    assert all("no permitida" in b for b in r["bloqueos"])          # state-changing routes are blocked: G8 cannot approve anything


def test_g8_mailbox_cycle_through_the_platform_and_human_decision_of_its_proposals():
    asunto = "Veo notas de otra persona (prueba)"
    out(run("incidentes", "depositar_queja", {"buzon": "quejas-web", "asunto": asunto, "remitente": "alumno.ficticio@example.invalid",
                                              "texto": "Al entrar al SISACAD me aparecieron el DNI y las notas de otro estudiante. Creo que hay un error de seguridad grave."}))
    box = out(run("incidentes", "sondear_buzon", {}))
    q = next(x for x in box["quejas"] if x["asunto"] == asunto and x["estado"] in ("nueva", "pendiente"))
    assert q["clasificacion"] == "seguridad"                                  # the mailbox filter classified it
    o = out(run("incidentes", "analizar_queja", {"id": q["id"]}, wait=600))
    exp = out(run("incidentes", "expediente", {"id": o["incidente"]}))
    assert "notificacion-anpd" in " ".join(exp["files"])
    # a person decides the agent's PROPOSED actions (it never executes them). If this run proposed none, use any
    # pending proposal already visible in the human review page (e.g. created by the mailbox or the autonomous mode).
    dpo = login("dpo")
    seen = httpx.get(f"{BASE}/api/human/pendientes", headers=dpo, timeout=60).json()["incidentes"]
    if not seen:
        pytest.skip("no expediente has pending proposed actions right now")
    target, action = seen[0]["expediente"], seen[0]["acciones"][0]["id"]
    r = post("/api/human/incidentes/decidir", {"expediente": target, "accion": action, "decision": "aprobada", "nota": "ok"}, dpo)
    assert r.status_code == 200 and "ninguna acción se ejecuta" in r.json()["nota"]
    after = out(run("incidentes", "expediente", {"id": target}))["acciones"]
    done = next(a for a in after if a["id"] == action)
    assert done["estado"] == "aprobada" and done["nota"].startswith("dpo:")          # attributed to the person
    assert psql(f"select count(*) from demo.core_securitylog where username='dpo' and module='incidentes' "
                f"and detail->>'target'='{target}/{action}'") != "0"
