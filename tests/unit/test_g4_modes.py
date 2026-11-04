"""G4 scope filtering and consolidation provenance; no model/network/DB required."""
import importlib.util
from pathlib import Path
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.services import audit_modes as consolidation

path = Path(__file__).resolve().parents[2] / "agents/Agente_evidencia_auditoria-Grupo4/audit_modes.py"
spec = importlib.util.spec_from_file_location("g4_native_modes", path)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
app = FastAPI()
app.include_router(native.router)
client = TestClient(app)

@pytest.mark.parametrize("role,count,excluded", [("responsable",44,"EN-"),("encargado",33,"RT-"),("ambos",52,"NONE")])
def test_plan_uses_catalog_and_filters_by_role(role,count,excluded):
    res = client.post("/api/planificar", json={"rol":role,"alcance":"Matrícula"})
    assert res.status_code == 200
    o = res.json()
    assert o["total"] == count
    assert all(not i["codigo_interno"].startswith(excluded) for i in o["items"])
    assert all(i["evidencia_esperada"] for i in o["items"])
    assert "internos" in o["nota"]

@pytest.mark.parametrize("body", [{"rol":"otro","alcance":"a"},{"rol":"ambos","alcance":"  "}])
def test_invalid_plan_rejected(body):
    assert client.post("/api/planificar",json=body).status_code == 422


def record(**kw):
    return {"id":str(uuid.uuid4()),"agent_id":"auditoria","action":"auditar","status":"succeeded","simulated":False,
            "result":{"output":{"nombre_archivo":"contrato.txt","sha256":"abc","severidad":"NO VERIFICABLE","dictamen_markdown":"Falta evidencia de aprobación"}},**kw}


def test_consolidation_preserves_sources_and_pending_review(monkeypatch):
    rec = record(simulated=True)
    monkeypatch.setattr(consolidation.db,"query",lambda *a:[rec])
    o = consolidation.consolidate([rec["id"],rec["id"]])
    assert o["total_evaluaciones"] == 1
    assert o["filas"][0]["ejecucion_id"] == rec["id"]
    assert o["filas"][0]["simulado"] is True
    assert o["resumen"] == {"NO VERIFICABLE":1}
    assert "Pendiente" in o["filas"][0]["estado_revision"]
    assert "Falta evidencia" in o["informe_markdown"]

@pytest.mark.parametrize("change", [{"agent_id":"terceros"},{"action":"consolidar"},{"status":"failed"}])
def test_m3_rejects_unrelated_or_failed_execution(monkeypatch,change):
    rec = record(**change)
    monkeypatch.setattr(consolidation.db,"query",lambda *a:[rec])
    with pytest.raises(ValueError): consolidation.consolidate([rec["id"]])


def test_m3_rejects_missing_evaluation(monkeypatch):
    monkeypatch.setattr(consolidation.db,"query",lambda *a:[])
    with pytest.raises(ValueError): consolidation.consolidate([str(uuid.uuid4())])
    with pytest.raises(ValueError): consolidation.consolidate([])
