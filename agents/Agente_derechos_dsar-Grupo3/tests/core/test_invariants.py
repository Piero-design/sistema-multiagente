"""Una prueba por invariante (docs/contexto-agente-derechos.md, sección 6).

Cada invariante se comprueba dos veces: el motor no la rompe y el validador la detecta si se fuerza.
"""

from __future__ import annotations

import copy
from datetime import date

import pytest

from dsar.core.calendar import add_days
from dsar.core.profiles import holidays
from dsar.core.validator import validate

SCENARIOS = [
    ("access", {}), ("identity-pending", {}), ("erasure", {}), ("pe-combined", {}),
    ("access", {"principal_id": "person-002", "request_type": "rectification"}),
    ("access", {"principal_id": "person-999"}),
    ("access", {"request_type": "objection", "policy_id": "LAB-15-REVIEW"}),
    ("access", {"request_type": "portability"}),
]


@pytest.fixture
def all_packages(build, request_fixture, org):
    packages = []
    for name, changes in SCENARIOS:
        for organization in (None, org):
            packages.append(build(request_fixture(name, **changes), organization))
    return packages


@pytest.fixture
def access_package(build, request_fixture):
    return build(request_fixture("access"))


def _forced(package, change):
    broken = copy.deepcopy(package)
    change(broken)
    return validate(broken)


# 1. Identidad no verificada => cero registros e IDENTITY_PENDING.
def test_inv1_engine_unverified_identity_yields_no_records(build, request_fixture):
    for status in ("pending", "failed", "VERIFIED-ish"):
        request = request_fixture("access")
        request["identity_verification"]["status"] = status
        package = build(request)
        assert package["discovered_records"] == []
        assert package["status"] == "IDENTITY_PENDING"


def test_inv1_validator_detects_records_without_identity(build, request_fixture, access_package):
    pending = build(request_fixture("identity-pending"))
    errors = _forced(pending, lambda p: p.update(discovered_records=access_package["discovered_records"]))
    assert "Se descubrieron datos sin identidad verificada" in errors


# 2. executed siempre false.
def test_inv2_engine_never_executes(all_packages):
    for package in all_packages:
        actions = [package["proposed_action"], *package["proposed_actions"]]
        assert all(action["executed"] is False for action in actions)


def test_inv2_validator_detects_executed_action(access_package):
    errors = _forced(access_package, lambda p: p["proposed_actions"][0].update(executed=True))
    assert "El prototipo no puede declarar una accion ejecutada" in errors


# 3. Rectificación, supresión u oposición => HITL.
def test_inv3_engine_requires_hitl_for_mutating_rights(all_packages):
    for package in all_packages:
        if set(package["request_types"]) & {"rectification", "erasure", "objection"}:
            assert package["hitl"]["required"] is True


def test_inv3_validator_detects_missing_hitl(build, request_fixture):
    erasure = build(request_fixture("erasure"))
    errors = _forced(erasure, lambda p: p["hitl"].update(required=False))
    assert "Una accion de mutacion o restriccion requiere HITL" in errors


# 4. Plazos solo del perfil, desde el día siguiente a la recepción.
def test_inv4_engine_takes_deadlines_from_profile(all_packages, profiles):
    for package in all_packages:
        profile = profiles[package["policy"]["policy_id"]]
        received = date.fromisoformat(package["received_at"])
        for right, item in package["deadlines"].items():
            legal = item.get("legal_days", item["days"])
            expected_legal = add_days(received, legal, item["day_type"], holidays(profile)).isoformat()
            assert item.get("legal_deadline_at", item["deadline_at"]) == expected_legal
            expected = add_days(received, item["days"], item["day_type"], holidays(profile)).isoformat()
            assert item["deadline_at"] == expected


def test_inv4_validator_detects_wrong_global_deadline(access_package):
    errors = _forced(access_package, lambda p: p.update(deadline_at="2027-01-01"))
    assert "deadline_at debe ser el plazo mas cercano de los derechos" in errors


# 5. Procedencia en cada registro entregable.
def test_inv5_engine_keeps_provenance(all_packages):
    for package in all_packages:
        for record in package["discovered_records"]:
            assert record["source_system"] and record["record_id"]


def test_inv5_validator_detects_missing_provenance(access_package):
    errors = _forced(access_package, lambda p: p["discovered_records"][0].pop("source_system"))
    assert "Registro sin procedencia completa" in errors


# 6. Campos de terceros retirados y anotados.
def test_inv6_engine_redacts_third_parties(all_packages, records):
    third_party = {(r["record_id"], f) for r in records for f in r.get("third_party_fields", [])}
    for package in all_packages:
        for record in package["discovered_records"]:
            for record_id, field in third_party:
                if record["record_id"] == record_id:
                    assert field not in record["data"]
                    assert field in record["redacted_fields"]


def test_inv6_validator_detects_unredacted_field(access_package):
    def leak(package):
        crm = next(r for r in package["discovered_records"] if r["record_id"] == "crm-001")
        crm["data"]["manager_email"] = "tercero@example.test"
    assert "Campo de tercero no redactado: manager_email" in _forced(access_package, leak)


# 7. audit_trail continuo desde 1.
def test_inv7_engine_audit_trail_is_continuous(all_packages):
    for package in all_packages:
        sequences = [item["sequence"] for item in package["audit_trail"]]
        assert sequences == list(range(1, len(sequences) + 1))


def test_inv7_validator_detects_gap(access_package):
    errors = _forced(access_package, lambda p: p["audit_trail"].pop(1))
    assert "La secuencia de auditoria no es continua" in errors


# 8. Todo expediente pasa el validador sin errores.
def test_inv8_every_engine_package_is_valid(all_packages):
    for package in all_packages:
        assert validate(package) == [], package["case_id"]


def test_inv8_validator_detects_missing_fields(access_package):
    errors = _forced(access_package, lambda p: p.pop("hitl"))
    assert errors and errors[0].startswith("Campos faltantes")


# 9. Solo estados admitidos; APPROVED/REJECTED solo por decisión humana.
def test_inv9_engine_never_decides(all_packages):
    for package in all_packages:
        assert package["status"] in {"IDENTITY_PENDING", "REVIEW", "APPROVAL_REQUIRED"}
        assert "human_decision" not in package


@pytest.mark.parametrize("status", ["APPROVED", "REJECTED", "CANCELLED"])
def test_inv9_validator_detects_decision_without_human(access_package, status):
    def decide(package):
        package["status"] = status
        package["audit_trail"][-1]["state"] = status
    assert f"Un estado {status} exige una decision humana registrada" in _forced(access_package, decide)


def test_inv9_validator_detects_unknown_state(access_package):
    assert "Estado no admitido" in _forced(access_package, lambda p: p.update(status="DONE"))


# 10. La política nunca alarga un plazo legal.
def test_inv10_engine_refuses_longer_org_deadline(build, peru_request, org):
    org["internal_response_days_by_right"]["erasure"] = 30
    with pytest.raises(ValueError, match="supera el legal"):
        build(peru_request(["erasure"]), org)


def test_inv10_validator_detects_longer_deadline(build, peru_request, org):
    package = build(peru_request(["access"]), org)
    errors = _forced(package, lambda p: p["deadlines"]["access"].update(days=25))
    assert "El plazo de access supera el plazo legal" in errors
