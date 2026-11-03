"""Contrato con el generador REAL del Grupo 3; expediente ficticio, sin decisiones reales."""
import importlib.util
from pathlib import Path
import pytest
from inventario.service import InventoryAgent


def test_sobre_producido_por_codigo_grupo3(tmp_path):
    source = Path(__file__).resolve().parents[2] / "Agente_derechos_dsar-Grupo3/src/dsar/storage/handoffs.py"
    if not source.exists():
        pytest.skip("Requiere checkout con el código del Grupo 3 para probar su productor real")
    spec = importlib.util.spec_from_file_location("productor_dsar", source)
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    package = {"case_id": "DSAR-PRUEBA-CONTRATO", "status": "APPROVED", "request_types": ["access"],
               "discovered_records": [], "policy": {"policy_id": "PE-LEY29733"}, "audit_trail": [],
               "human_decision": {"reviewer": "PERSONA FICTICIA"}, "coverage": {"missing_systems": ["Biblioteca"]}}
    envelope = next(h for h in producer.build_handoffs(package, "2026-11-03T17:00:00-05:00") if h["to_agent"] == "inventario")
    agent = InventoryAgent(tmp_path / "inv.sqlite3")
    result, status = agent.recibir_handoff(envelope, "UNSA-DEMO")
    assert status == 200
    assert result["data"]["case_ref"] == package["case_id"]
    assert result["data"]["hash_verificado"]
    assert result["data"]["requiere_validacion"]
    assert result["data"]["sistemas"][0]["estado"] == "sin_activos_en_inventario"
