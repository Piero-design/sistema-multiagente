"""Human-in-the-loop actions through the platform (signed-in humans with roles). Cloud mode.
These replace the old test shortcut that called G3's Python functions inside its container."""
import subprocess

import httpx
import pytest

from test_platform import BASE, get, run
from test_flows import flow

PW = {"dpo": "demo-dpo", "legal": "demo-legal"}


def login(user):
    r = httpx.post(f"{BASE}/api/auth/login", json={"user": user, "password": PW[user]}, timeout=30)
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


def post(path, body, headers):
    return httpx.post(f"{BASE}{path}", json=body, headers=headers, timeout=120)


def psql(sql):
    r = subprocess.run(["docker", "compose", "exec", "-T", "postgres", "psql", "-U", "gestitel", "-d", "gestitel", "-tAc", sql],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def test_decision_endpoints_require_a_signed_in_human():
    for path, body in (("/api/human/dsar/decidir", {"case_id": "x", "decision": "APPROVED", "note": "n"}),
                       ("/api/human/terceros/aprobar", {"id_registro": "x", "decision": "aprobar"}),
                       ("/api/human/incidentes/decidir", {"expediente": "x", "accion": "A1", "decision": "aprobada"})):
        assert httpx.post(f"{BASE}{path}", json=body, timeout=30).status_code == 401
    bad = httpx.post(f"{BASE}/api/auth/login", json={"user": "dpo", "password": "incorrecta"}, timeout=30)
    assert bad.status_code == 401


def test_roles_are_enforced():
    legal = login("legal")
    # Legal cannot decide a DSAR case (DPO only)
    r = post("/api/human/dsar/decidir", {"case_id": "x", "decision": "APPROVED", "note": "n"}, legal)
    assert r.status_code == 403


def test_models_still_cannot_decide():
    for tool in ("dsar_decidir", "verify_identity", "decide"):
        assert httpx.post(f"{BASE}/api/agents/dsar/execute", json={"action": tool, "input": {}}, timeout=30).status_code == 422


def test_dsar_full_cycle_with_real_human_decision_then_handoffs():
    dpo = login("dpo")
    e = run("dsar", "dsar_crear_caso", {"principal_id": "person-001", "request_types": ["erasure"],
            "policy_id": "PE-LEY29733", "received_at": "2026-11-03", "identity_status": "pending",
            "identity_reference": "", "request_text": "quiero que borren mis datos"})
    case_id = e["result"]["output"]["case_id"]
    assert e["result"]["output"]["status"] == "IDENTITY_PENDING"
    # deciding before verifying identity must be refused by the agent's own rules
    early = post("/api/human/dsar/decidir", {"case_id": case_id, "decision": "APPROVED", "note": "sin verificar"}, dpo)
    assert early.status_code == 422
    v = post("/api/human/dsar/verificar", {"case_id": case_id, "method": "DNI presencial", "reference": "REF-1"}, dpo)
    assert v.status_code == 200, v.text
    d = post("/api/human/dsar/decidir", {"case_id": case_id, "decision": "APPROVED", "note": "Aprobado por el DPO"}, dpo)
    assert d.status_code == 200, d.text
    assert d.json()["status"] == "APPROVED" and {h["to"] for h in d.json()["handoffs"]} >= {"evidencia", "terceros"}
    # the decision is attributed to the person who made it
    assert psql(f"select count(*) from demo.core_securitylog where username='dpo' and action='human_decision' and detail->>'target'='{case_id}'") != "0"
    # and the produced handoffs travel to the other agents
    f = flow("dsar_handoffs", {"case_id": case_id})
    assert f["status"] == "succeeded", f["error"]
    by = {h["to"]: h for h in f["result"]["handoffs"]}
    assert by["evidencia"]["delivery"] == "entregado" and by["terceros"]["delivery"] == "pendiente_humano"


def test_g5_two_gate_approval_order_is_enforced_by_the_agent():
    dpo, legal = login("dpo"), login("legal")
    pend = httpx.get(f"{BASE}/api/human/pendientes", headers=dpo, timeout=60).json()["terceros"]
    target = next((x["id_registro"] for x in pend if x["estado"] == "Pendiente DPO"), None)
    assert target, "no hay expedientes Pendiente DPO"
    out_of_turn = post("/api/human/terceros/aprobar", {"id_registro": target, "decision": "aprobar"}, legal)
    assert out_of_turn.status_code == 409                       # Legal before the DPO
    ok = post("/api/human/terceros/aprobar", {"id_registro": target, "decision": "aprobar", "comentario": "ok"}, dpo)
    assert ok.status_code == 200, ok.text
    ok2 = post("/api/human/terceros/aprobar", {"id_registro": target, "decision": "aprobar", "comentario": "ok legal"}, legal)
    assert ok2.status_code == 200, ok2.text
    # accepted decisions are attributed to each person; the out-of-turn attempt is logged too, as a refused attempt
    assert psql("select count(*) from demo.core_securitylog where action='human_decision' and module='terceros' "
                f"and detail->>'target'='{target}' and detail->>'outcome' like '%HTTP 200%'") == "2"
    assert psql("select count(*) from demo.core_securitylog where action='human_decision' and module='terceros' "
                f"and detail->>'target'='{target}' and detail->>'outcome' like '%HTTP 409%'") == "1"


# ---------------- G3 · Gestión DSAR (rest of the agent's panel, DPO only) ----------------
G = "/api/human/dsar/gestion/"


def test_g3_gestion_requires_a_dpo_and_known_paths():
    assert httpx.get(f"{BASE}{G}casos", timeout=30).status_code == 401
    assert httpx.get(f"{BASE}{G}casos", headers=login("legal"), timeout=30).status_code == 403
    assert httpx.get(f"{BASE}{G}../verify", headers=login("dpo"), timeout=30).status_code == 404


def test_g3_gestion_case_work_is_attributed_and_never_decides():
    dpo = login("dpo")
    case_id = run("dsar", "dsar_crear_caso", {"principal_id": "person-001", "request_types": ["access"],
                  "policy_id": "PE-LEY29733", "received_at": "2026-11-03", "identity_status": "pending",
                  "identity_reference": ""})["result"]["output"]["case_id"]
    full = httpx.get(f"{BASE}{G}casos/{case_id}", headers=dpo, timeout=60).json()
    assert full["status"] == "IDENTITY_PENDING" and full["discovered_records"] == []
    assert "Cláusula 8.3" in {c["control"] for c in full["controls"]}
    draft = post(f"{G}casos/{case_id}/borrador", {"mode": "guided"}, dpo)
    assert draft.status_code == 200 and draft.json()["draft"].startswith("# Borrador")
    # a client cannot pretend to be someone else: the backend sets the reviewer to the signed-in person
    post("/api/human/dsar/verificar", {"case_id": case_id, "method": "DNI presencial"}, dpo)
    ext = post(f"{G}casos/{case_id}/prorroga", {"right": "access", "reason": "Volumen", "reviewer": "otra-persona"}, dpo)
    assert ext.status_code == 200, ext.text
    assert ext.json()["deadlines"]["access"]["extension"]["decided_by"] == "dpo"
    assert httpx.get(f"{BASE}{G}casos/{case_id}", headers=dpo, timeout=60).json()["status"] not in ("APPROVED", "REJECTED")
    assert psql(f"select count(*) from demo.core_securitylog where username='dpo' and module='dsar' "
                f"and detail->>'target'='casos/{case_id}/prorroga'") != "0"


def test_g3_gestion_mail_goes_to_human_triage_and_outbox_does_not_send_by_default():
    dpo = login("dpo")
    assert post(f"{G}correos/demo", {"count": 2}, dpo).status_code == 200
    assert post(f"{G}correos/sincronizar", {"limit": 10}, dpo).status_code == 200
    mails = httpx.get(f"{BASE}{G}correos", headers=dpo, timeout=60).json()
    triage = [m for m in mails if m["status"] == "triaje"]
    assert triage, "sin modelo local, los correos quedan para revisión humana"
    ok = post(f"{G}correos/{triage[0]['id']}/confirmar", {"request_types": ["access"], "subject_email": "persona@example.test"}, dpo)
    assert ok.status_code == 200 and ok.json()["case_id"].startswith("DSAR-EMAIL-")
    out = post(f"{G}salida", {"case_id": ok.json()["case_id"], "kind": "identidad"}, dpo)
    assert out.status_code == 200, out.text
    sent = post(f"{G}salida/{out.json()['id']}/enviar", {}, dpo)
    assert sent.status_code in (409, 422)                       # DSAR_MAIL_SEND_ENABLED is false by default

def test_g5_deletion_is_a_dpo_only_human_action_and_rejects_paths():
    body = {"tipo": "expediente", "id": "DPA-NO-EXISTE_000000"}
    assert httpx.post(f"{BASE}/api/human/terceros/eliminar", json=body, timeout=30).status_code == 401
    assert post("/api/human/terceros/eliminar", body, login("legal")).status_code == 403
    dpo = login("dpo")
    for bad in ({"tipo": "expediente", "id": "../../datos/config_modelo"}, {"tipo": "perfil", "id": "../unsa"},
                {"tipo": "otro", "id": "x"}, {"tipo": "documento", "id": "unsa", "nombre": "../config_organizacion.json"},
                {"tipo": "documento", "id": "unsa", "nombre": "ROF.exe"}):
        assert post("/api/human/terceros/eliminar", bad, dpo).status_code == 400, bad
    assert post("/api/human/terceros/eliminar", body, dpo).status_code == 404       # nothing to delete
