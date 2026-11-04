"""Prórroga (art. 71), requerimiento (art. 70), subsanación (art. 66.2) y decisión humana."""

from __future__ import annotations

import copy
from datetime import date, datetime, timezone

import pytest

from dsar.core.errors import CaseInputError, TransitionError
from dsar.core.procedures import (
    CANCELLATION_REASON,
    apply_human_decision,
    ensure_exportable,
    extend_deadline,
    extension_preview,
    upgrade_legacy_extensions,
    observe_request,
    propose_cancellation,
    request_additional_information,
    resume_case,
)
from dsar.core.render import render_response
from dsar.core.validator import validate

DECIDED_AT = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)
REVIEWER = "Revisora Demo"


@pytest.fixture
def pe_case(build, request_fixture):
    # rectification vence 2026-10-16 y access 2026-10-30 (días hábiles).
    return build(request_fixture("pe-combined"))


@pytest.fixture
def lab_case(build, request_fixture):
    return build(request_fixture("access"))


# Prórroga (art. 71)

def test_extension_once_by_equal_term(pe_case, profiles):
    extended = extend_deadline(pe_case, profiles, "access", "Volumen de sistemas", REVIEWER, date(2026, 10, 20))
    access = extended["deadlines"]["access"]
    assert access["deadline_at"] == "2026-11-27"
    assert access["extended"] is True
    assert access["extension"]["original_deadline_at"] == "2026-10-30"
    assert access["extension"]["decided_by"] == REVIEWER
    assert extended["deadline_at"] == "2026-10-16"
    assert extended["status"] == pe_case["status"]
    assert validate(extended) == []
    assert "prorrogado 20 dias habiles; vencia 2026-10-30" in render_response(extended)
    assert pe_case["deadlines"]["access"]["deadline_at"] == "2026-10-30"


def test_extension_fails_the_second_time(pe_case, profiles):
    once = extend_deadline(pe_case, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20))
    with pytest.raises(CaseInputError, match="ya fue prorrogado"):
        extend_deadline(once, profiles, "access", "Otra vez", REVIEWER, date(2026, 10, 21))


def test_extension_not_allowed_for_information(build, peru_request, profiles):
    package = build(peru_request(["information", "access"]))
    with pytest.raises(CaseInputError, match="information"):
        extend_deadline(package, profiles, "information", "Motivo", REVIEWER, date(2026, 10, 5))


def test_extension_must_be_decided_within_original_term(pe_case, profiles):
    with pytest.raises(CaseInputError, match="dentro del plazo que se amplia"):
        extend_deadline(pe_case, profiles, "rectification", "Motivo", REVIEWER, date(2026, 10, 19))


def test_extension_cannot_exceed_original_term(pe_case, profiles):
    with pytest.raises(CaseInputError):
        extend_deadline(pe_case, profiles, "rectification", "Motivo", REVIEWER, date(2026, 10, 5), days=11)
    shorter = extend_deadline(pe_case, profiles, "rectification", "Motivo", REVIEWER, date(2026, 10, 5), days=5)
    assert shorter["deadlines"]["rectification"]["deadline_at"] == "2026-10-23"
    assert shorter["deadline_at"] == "2026-10-23"


def test_extension_requires_human_and_profile(pe_case, lab_case, profiles):
    with pytest.raises(CaseInputError):
        extend_deadline(pe_case, profiles, "access", "Motivo", "  ", date(2026, 10, 5))
    with pytest.raises(CaseInputError, match="no admite prorroga"):
        extend_deadline(lab_case, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 5))


def test_extension_legal_deadline_is_the_legal_ceiling_not_legal_plus_granted_days(build, peru_request, org, profiles):
    """Art. 71.1: «por un plazo igual, como máximo». El tope legal es plazo legal + plazo legal (20 + 20), con
    independencia de los días que conceda la organización."""
    package = build(peru_request(["access"]), org)
    assert package["deadlines"]["access"]["days"] == 15 and package["deadlines"]["access"]["legal_days"] == 20
    extended = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20))
    access = extended["deadlines"]["access"]
    assert access["extension"]["days"] == 15 and access["extension"]["max_days"] == 20
    assert (access["deadline_at"], access["legal_deadline_at"]) == ("2026-11-13", "2026-11-27")
    assert access["extension"]["original_legal_deadline_at"] == "2026-10-30"
    assert access["extension"]["legal_ceiling_at"] == access["legal_deadline_at"]
    assert access["deadline_at"] <= access["legal_deadline_at"]
    assert validate(extended) == []


def test_extension_may_reach_the_legal_term_even_when_the_policy_is_stricter(build, peru_request, org, profiles):
    package = build(peru_request(["access"]), org)  # interno 15, legal 20
    longest = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20), days=20)
    assert longest["deadlines"]["access"]["extension"]["days"] == 20
    assert longest["deadlines"]["access"]["deadline_at"] <= longest["deadlines"]["access"]["legal_deadline_at"]
    assert validate(longest) == []
    with pytest.raises(CaseInputError, match="de 1 a 20 dias"):
        extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20), days=21)


def test_extension_may_be_communicated_until_the_legal_deadline_not_the_internal_one(build, peru_request, org, profiles):
    package = build(peru_request(["access"]), org)
    access = package["deadlines"]["access"]
    after_internal = date.fromisoformat(access["deadline_at"]).replace(day=int(access["deadline_at"][-2:]) + 1)
    assert after_internal.isoformat() <= access["legal_deadline_at"]
    extended = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, after_internal)
    assert validate(extended) == []
    with pytest.raises(CaseInputError, match="art. 71.2"):
        extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date.fromisoformat(access["legal_deadline_at"]).replace(day=int(access["legal_deadline_at"][-2:]) + 1))


def test_extension_preview_matches_what_extend_would_do(build, peru_request, org, profiles):
    package = build(peru_request(["access"]), org)
    preview = extension_preview(package, profiles, "access", date(2026, 10, 20))
    assert preview["allowed"] is True and preview["max_days"] == 20 and preview["proposed_days"] == 15
    assert preview["legal_ceiling_at"] == "2026-11-27" and preview["communicate_before"] == "2026-10-30"
    extended = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20))
    assert preview["new_deadline_at"] == extended["deadlines"]["access"]["deadline_at"]
    too_long = extension_preview(package, profiles, "access", date(2026, 10, 20), days=21)
    assert too_long["allowed"] is False and "de 1 a 20 dias" in too_long["reason"] and too_long["new_deadline_at"] is None
    assert package["deadlines"]["access"].get("extended") is None, "la vista previa no modifica el expediente"
    info = build(peru_request(["information"]), org)
    assert extension_preview(info, profiles, "information", date(2026, 10, 5))["allowed"] is False


def test_validator_rejects_an_extension_past_the_legal_ceiling(build, peru_request, org, profiles):
    package = build(peru_request(["access"]), org)
    extended = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20), days=20)
    forged = copy.deepcopy(extended)
    forged["deadlines"]["access"]["deadline_at"] = "2026-12-31"
    assert "El plazo prorrogado de access pasa del tope legal" in validate(forged)


def test_validator_detects_forged_extension(pe_case):
    forged = {**pe_case, "deadlines": {**pe_case["deadlines"]}}
    forged["deadlines"]["access"] = {**pe_case["deadlines"]["access"], "extended": True}
    assert "La prorroga de access no registra decision humana" in validate(forged)


# Requerimiento de información adicional (art. 70)

def test_additional_information_suspends_and_shifts_deadlines(pe_case, profiles):
    held = request_additional_information(pe_case, profiles, date(2026, 10, 5), "Falta el correo a corregir", REVIEWER)
    assert held["status"] == "ON_HOLD"
    assert held["suspension"]["suspended_from"] == "2026-10-05"
    assert held["suspension"]["due_at"] == "2026-10-20"
    assert validate(held) == []
    assert "## Tramite suspendido" in render_response(held)

    resumed = resume_case(held, profiles, date(2026, 10, 9), REVIEWER, "El titular respondio")
    assert resumed["status"] == pe_case["status"]
    assert "suspension" not in resumed
    closed = resumed["suspensions"][0]
    assert (closed["suspended_until"], closed["days_suspended"]) == ("2026-10-09", 3)
    assert resumed["deadlines"]["rectification"]["deadline_at"] == "2026-10-21"
    assert resumed["deadlines"]["access"]["deadline_at"] == "2026-11-04"
    assert resumed["deadline_at"] == "2026-10-21"
    assert validate(resumed) == []


def test_suspension_ends_when_principal_term_expires(pe_case, profiles):
    held = request_additional_information(pe_case, profiles, date(2026, 10, 5), "Dato faltante", REVIEWER)
    resumed = resume_case(held, profiles, date(2026, 10, 25), REVIEWER, "Sin respuesta del titular")
    assert resumed["suspensions"][0]["suspended_until"] == "2026-10-20"
    assert resumed["suspensions"][0]["days_suspended"] == 10
    assert resumed["deadlines"]["rectification"]["deadline_at"] == "2026-10-30"


def test_additional_information_window_and_single_use(pe_case, profiles):
    with pytest.raises(CaseInputError, match="entre 2026-10-01 y 2026-10-13"):
        request_additional_information(pe_case, profiles, date(2026, 10, 14), "Tarde", REVIEWER)
    held = request_additional_information(pe_case, profiles, date(2026, 10, 2), "Dato", REVIEWER)
    resumed = resume_case(held, profiles, date(2026, 10, 6), REVIEWER, "Respondio")
    with pytest.raises(CaseInputError, match="una vez"):
        request_additional_information(resumed, profiles, date(2026, 10, 7), "Otro dato", REVIEWER)


def test_additional_information_not_in_lab_profiles(lab_case, profiles):
    with pytest.raises(CaseInputError, match="no admite"):
        request_additional_information(lab_case, profiles, date(2026, 10, 2), "Dato", REVIEWER)


def test_cannot_decide_while_on_hold(pe_case, profiles):
    held = request_additional_information(pe_case, profiles, date(2026, 10, 5), "Dato", REVIEWER)
    with pytest.raises(TransitionError):
        apply_human_decision(held, REVIEWER, "APPROVED", "Aprobado", DECIDED_AT)


def test_validator_detects_on_hold_without_suspension(pe_case):
    forged = {**pe_case, "status": "ON_HOLD",
              "audit_trail": [*pe_case["audit_trail"][:-1], {**pe_case["audit_trail"][-1], "state": "ON_HOLD"}]}
    assert "Un caso ON_HOLD necesita una suspension activa" in validate(forged)


# Subsanación (art. 66.2)

def test_unremedied_request_is_proposed_cancelled_and_needs_human(build, request_fixture, profiles):
    pending = build(request_fixture("identity-pending", policy_id="PE-LEY29733"))
    observed = observe_request(pending, profiles, date(2026, 10, 2), "Falta documento de representacion", REVIEWER)
    assert observed["suspension"]["due_at"] == "2026-10-12"
    with pytest.raises(CaseInputError, match="vence el 2026-10-12"):
        propose_cancellation(observed, date(2026, 10, 12))
    proposed = propose_cancellation(observed, date(2026, 10, 13))
    assert proposed["status"] == "ON_HOLD"
    assert CANCELLATION_REASON in proposed["hitl"]["reasons"]
    assert validate(proposed) == []
    with pytest.raises(CaseInputError, match="vencio"):
        resume_case(proposed, profiles, date(2026, 10, 13), REVIEWER, "Tarde")

    cancelled = apply_human_decision(proposed, REVIEWER, "CANCELLED", "No subsano en plazo", DECIDED_AT)
    assert cancelled["status"] == "CANCELLED"
    assert cancelled["human_decision"]["decision"] == "CANCELLED"
    assert "suspension" not in cancelled
    assert validate(cancelled) == []


def test_cured_request_resumes(build, request_fixture, profiles):
    package = build(request_fixture("pe-combined"))
    observed = observe_request(package, profiles, date(2026, 10, 9), "Falta indicar el dato a corregir", REVIEWER)
    resumed = resume_case(observed, profiles, date(2026, 10, 12), REVIEWER, "Subsanada")
    assert resumed["status"] == package["status"]
    assert resumed["suspensions"][0]["days_suspended"] == 1


def test_observation_window(pe_case, profiles):
    with pytest.raises(CaseInputError, match="entre 2026-10-01 y 2026-10-09"):
        observe_request(pe_case, profiles, date(2026, 10, 12), "Tarde", REVIEWER)


def test_cancellation_requires_proposal(pe_case, profiles):
    observed = observe_request(pe_case, profiles, date(2026, 10, 2), "Dato", REVIEWER)
    with pytest.raises(TransitionError):
        apply_human_decision(observed, REVIEWER, "CANCELLED", "Sin proponer", DECIDED_AT)
    with pytest.raises(TransitionError):
        apply_human_decision(pe_case, REVIEWER, "CANCELLED", "Sin suspension", DECIDED_AT)


# Decisión humana

@pytest.mark.parametrize("decision", ["APPROVED", "REJECTED"])
def test_human_decision_is_the_only_way_to_final_states(pe_case, decision):
    decided = apply_human_decision(pe_case, REVIEWER, decision, "Revisado con evidencia", DECIDED_AT)
    assert decided["status"] == decision
    assert decided["human_decision"]["reviewer"] == REVIEWER
    assert decided["human_decision"]["at"] == "2026-10-20T15:00:00+00:00"
    assert decided["audit_trail"][-1]["state"] == decision
    assert all(action["executed"] is False for action in decided["proposed_actions"])
    assert validate(decided) == []
    assert pe_case["status"] == "APPROVAL_REQUIRED"


def test_decision_requires_reviewer_and_note(pe_case):
    with pytest.raises(CaseInputError):
        apply_human_decision(pe_case, "", "APPROVED", "Nota", DECIDED_AT)
    with pytest.raises(CaseInputError):
        apply_human_decision(pe_case, REVIEWER, "APPROVED", " ", DECIDED_AT)
    with pytest.raises(CaseInputError):
        apply_human_decision(pe_case, REVIEWER, "FULFILLED", "Nota", DECIDED_AT)


def test_identity_pending_cannot_be_decided(build, request_fixture):
    pending = build(request_fixture("identity-pending"))
    with pytest.raises(TransitionError):
        apply_human_decision(pending, REVIEWER, "APPROVED", "Nota", DECIDED_AT)


def test_decided_case_is_closed_to_new_procedures(pe_case, profiles):
    decided = apply_human_decision(pe_case, REVIEWER, "APPROVED", "Nota", DECIDED_AT)
    with pytest.raises(TransitionError):
        apply_human_decision(decided, REVIEWER, "REJECTED", "Cambio", DECIDED_AT)
    with pytest.raises(TransitionError):
        extend_deadline(decided, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20))
    with pytest.raises(TransitionError):
        request_additional_information(decided, profiles, date(2026, 10, 5), "Dato", REVIEWER)


def test_unverified_identity_cannot_be_exported(build, request_fixture, pe_case):
    ensure_exportable(pe_case)  # identidad verificada: se puede exportar
    pending = build(request_fixture("identity-pending"))
    assert pending["identity_verification"]["status"] != "verified"
    with pytest.raises(TransitionError):
        ensure_exportable(pending)


def test_legacy_extension_gets_the_legal_ceiling_without_changing_the_granted_deadline(build, peru_request, org, profiles):
    """Prórroga registrada con la regla anterior: el plazo legal se había movido 15 días (legal + concedidos)."""
    package = build(peru_request(["access"]), org)
    modern = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20))
    legacy = copy.deepcopy(modern)
    item = legacy["deadlines"]["access"]
    for key in ("max_days", "original_legal_deadline_at", "legal_ceiling_at"):
        del item["extension"][key]
    item["legal_deadline_at"] = "2026-11-20"  # lo que dejaba la regla anterior (30/10 + 15 días hábiles)
    fixed = upgrade_legacy_extensions(legacy, profiles)
    assert fixed["deadlines"]["access"] == modern["deadlines"]["access"]
    assert fixed["deadlines"]["access"]["deadline_at"] == legacy["deadlines"]["access"]["deadline_at"]
    assert legacy["deadlines"]["access"]["legal_deadline_at"] == "2026-11-20", "no modifica el expediente recibido"
    assert upgrade_legacy_extensions(modern, profiles) is modern, "lo ya correcto no se toca"
    assert validate(fixed) == []


def test_preview_of_an_already_extended_right_says_so_instead_of_recomputing_the_ceiling(build, peru_request, org, profiles):
    """Regresión: recalcular legal + plazo igual sobre el tope ya guardado salía del calendario (2027) y daba error."""
    package = build(peru_request(["access"]), org)
    extended = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 20), days=20)
    preview = extension_preview(extended, profiles, "access", date(2026, 10, 21))
    assert preview["allowed"] is False and "ya fue prorrogado" in preview["reason"]
    assert preview["legal_ceiling_at"] == extended["deadlines"]["access"]["extension"]["legal_ceiling_at"]


def test_preview_explains_when_the_calendar_cannot_count_the_ceiling(build, peru_request, profiles):
    package = build(peru_request(["access"]) | {"received_at": "2027-11-20"})
    preview = extension_preview(package, profiles, "access", date(2027, 11, 22))
    assert preview["allowed"] is False and "2028" in preview["reason"] and preview["legal_ceiling_at"] is None


def test_a_suspension_after_an_extension_moves_the_legal_ceiling_too(build, peru_request, org, profiles):
    """Regresión de la revisión: reanudar tras una prórroga dejaba el tope legal fijo y el validador rechazaba el caso."""
    package = build(peru_request(["access"]), org)
    extended = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 5), days=20)
    ceiling = extended["deadlines"]["access"]["extension"]["legal_ceiling_at"]
    held = request_additional_information(extended, profiles, date(2026, 10, 5), "Falta el documento", REVIEWER)
    resumed = resume_case(held, profiles, date(2026, 10, 9), REVIEWER, "Respondió")
    item = resumed["deadlines"]["access"]
    assert item["extension"]["legal_ceiling_at"] > ceiling and item["legal_deadline_at"] == item["extension"]["legal_ceiling_at"]
    assert item["deadline_at"] <= item["extension"]["legal_ceiling_at"]
    assert validate(resumed) == []


def test_legacy_extension_with_suspensions_is_left_alone_instead_of_inventing_a_ceiling(build, peru_request, org, profiles):
    package = build(peru_request(["access"]), org)
    modern = extend_deadline(package, profiles, "access", "Motivo", REVIEWER, date(2026, 10, 5))
    legacy = copy.deepcopy(modern)
    for key in ("max_days", "original_legal_deadline_at", "legal_ceiling_at"):
        del legacy["deadlines"]["access"]["extension"][key]
    legacy["deadlines"]["access"]["suspended_days"] = 3
    assert upgrade_legacy_extensions(legacy, profiles) is legacy
