"""Interconnected flows between agents, against the RUNNING stack (cloud mode, real model calls).
Each flow step is a real execution; these tests check the chain, not the wording of the model."""
import time

import httpx
import pytest

from test_platform import BASE, get, run


def flow(name, params, wait=900):
    r = httpx.post(f"{BASE}/api/flows/{name}", json={"params": params}, timeout=30)
    assert r.status_code == 202, r.text
    rid = r.json()["flow_run_id"]
    end = time.time() + wait
    while time.time() < end:
        f = get(f"/api/flows/{rid}").json()
        if f["status"] != "running":
            return f
        time.sleep(3)
    raise TimeoutError(rid)


def test_unknown_flow_is_rejected():
    assert httpx.post(f"{BASE}/api/flows/no_existe", json={"params": {}}, timeout=30).status_code == 404


def test_g5_results_feed_g7_soa():
    # make sure there is at least one G5 expediente
    reg = run("terceros", "registro", {"organizacion": "unsa"})["result"]["output"]
    if not reg.get("registros"):
        run("terceros", "auditar", {"organizacion": "unsa", "contrato_texto":
            "CONTRATO DE ENCARGO. El encargado tratara datos segun instrucciones del responsable."}, wait=420)
    f = flow("terceros_a_controles", {"organizacion": "unsa", "rol": "ambos"})
    assert f["status"] == "succeeded", f["error"]
    r = f["result"]
    assert [s["agent"] for s in f["steps"]].count("controles") == 2        # SoA before and after
    assert r["controles_g5"] == 26
    # whatever G5 marked Cumple/Parcial and G7 knows must show up in G7's SoA with the matching state
    assert r["resumen_despues"]["implementados"] + r["resumen_despues"]["parciales"] >= \
        r["resumen_antes"]["implementados"] + r["resumen_antes"]["parciales"]
    assert r["evidencias_enviadas_a_g7"] >= len(r["controles_que_cambiaron_en_soa"])


def test_g8_incident_lessons_reach_g1():
    f = flow("incidente_a_formacion", {"reporte": (
        "Un funcionario envio por error una hoja de calculo con DNI y notas de 300 estudiantes "
        "a una lista externa de correo de la universidad.")})
    assert f["status"] == "succeeded", f["error"]
    assert [s["agent"] for s in f["steps"]] == ["incidentes", "formacion"]
    assert len(f["result"]["recomendacion_g1"]) > 50


def _human_decides(case_id):
    """A signed-in DPO verifies identity and decides, through the platform's human endpoints (no model involved)."""
    r = httpx.post(f"{BASE}/api/auth/login", json={"user": "dpo", "password": "demo-dpo"}, timeout=30)
    h = {"Authorization": "Bearer " + r.json()["token"]}
    v = httpx.post(f"{BASE}/api/human/dsar/verificar", json={"case_id": case_id, "method": "DNI presencial", "reference": "REF-1"}, headers=h, timeout=60)
    assert v.status_code == 200, v.text
    d = httpx.post(f"{BASE}/api/human/dsar/decidir", json={"case_id": case_id, "decision": "APPROVED", "note": "Aprobado en prueba"}, headers=h, timeout=60)
    assert d.status_code == 200, d.text


def test_g3_handoffs_are_transported_after_human_decision():
    e = run("dsar", "dsar_crear_caso", {"principal_id": "person-001", "request_types": ["erasure"],
            "policy_id": "PE-LEY29733", "received_at": "2026-11-03", "identity_status": "pending",
            "identity_reference": "", "request_text": "quiero que borren mis datos"})
    case_id = e["result"]["output"]["case_id"]
    # before any human decision there is nothing to transport
    f0 = flow("dsar_handoffs", {"case_id": case_id}, wait=120)
    assert f0["status"] == "failed" and "humana" in f0["error"].lower() or "handoffs" in (f0["error"] or "").lower()
    _human_decides(case_id)
    f = flow("dsar_handoffs", {"case_id": case_id})
    assert f["status"] == "succeeded", f["error"]
    by = {h["to"]: h for h in f["result"]["handoffs"]}
    assert by["evidencia"]["delivery"] == "entregado" and by["evidencia"]["severidad"]      # G4 evaluated it
    if "inventario" in by:                                                                   # G6 verified the producer's SHA-256
        assert by["inventario"]["delivery"] == "entregado" and by["inventario"]["cobertura"]["case_ref"] == case_id
    assert by["terceros"]["delivery"] == "pendiente_humano"                                  # requires_hitl respected
    stored = get("/api/flows").json()["handoffs"]
    assert any(h["case_ref"] == case_id for h in stored)


def test_g6_inventory_exported_as_evidence_to_g4():
    run("inventario", "registrar_activos", {"organizacion": "UNSA-DEMO", "fuentes": [{
        "id": "matricula-fuente-1", "nombre": "Fuente de Matricula", "sistema": "Matricula", "formato": "csv",
        "contenido": "nombre_completo,dni,correo_institucional,fecha_nacimiento\nPersona de prueba,00000000,ejemplo@example.invalid,2000-01-01",
        "contexto": {"finalidad": "Gestionar la matricula (ficticia)", "titulares": ["Estudiantes"], "responsable": "Secretaria academica (ficticia)"}}]})
    f = flow("inventario_a_auditoria", {"organizacion": "UNSA-DEMO"})
    assert f["status"] == "succeeded", f["error"]
    assert [s["agent"] for s in f["steps"]] == ["inventario", "auditoria"]
    assert f["result"]["enviado_por_g6"] is False and f["result"]["severidad_propuesta_g4"]
