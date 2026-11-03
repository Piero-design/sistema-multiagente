"""Estados, borrador de respuesta y dependencia exclusiva de la biblioteca estándar."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

import dsar.core
from dsar.core.errors import TransitionError
from dsar.core.render import guided_letter, render_response
from dsar.core.states import ALLOWED_STATES, HUMAN_ONLY_STATES, TRANSITIONS, check_transition

CORE_DIR = Path(dsar.core.__file__).parent


def test_transitions_only_use_allowed_states():
    for source, targets in TRANSITIONS.items():
        assert source in ALLOWED_STATES
        assert targets <= ALLOWED_STATES


def test_human_only_states_are_reached_only_from_decidable_states():
    for source, targets in TRANSITIONS.items():
        if targets & HUMAN_ONLY_STATES:
            assert source in {"REVIEW", "APPROVAL_REQUIRED", "ON_HOLD"}


def test_invalid_transition_raises():
    check_transition("REVIEW", "APPROVED")
    with pytest.raises(TransitionError):
        check_transition("IDENTITY_PENDING", "APPROVED")
    with pytest.raises(TransitionError):
        check_transition("APPROVED", "REJECTED")


def test_render_marks_actions_as_not_executed(build, request_fixture):
    text = render_response(build(request_fixture("erasure")))
    assert "Propuesta (erasure, no ejecutada)" in text
    assert "ejecutad" not in text.replace("no ejecutada", "")


def test_render_pending_identity_has_no_records(build, request_fixture):
    text = render_response(build(request_fixture("identity-pending")))
    assert "verificacion de identidad esta pendiente" in text
    assert "example.test" not in text


def test_render_inserts_letter_without_changing_facts(build, request_fixture):
    package = build(request_fixture("access"))
    text = render_response(package, letter="Estimada persona titular: adjuntamos su informacion.")
    assert "## Carta al titular (borrador, no enviada)" in text
    assert text.replace("## Carta al titular (borrador, no enviada)\n\nEstimada persona titular: "
                        "adjuntamos su informacion.\n\n", "") == render_response(package)


def test_guided_letter_states_facts_without_personal_data(build, request_fixture):
    package = build(request_fixture("access"))
    letter = guided_letter(package)
    assert letter.startswith("Estimado/a titular:")
    assert f"solicitud de acceso, registrada el {package['received_at']}" in letter
    assert package["case_id"] in letter and f"a más tardar el {package['deadline_at']}" in letter
    assert "registros asociados" in letter or "un registro asociado" in letter
    assert "example.test" not in letter
    for record in package["discovered_records"]:
        assert not any(isinstance(value, str) and value in letter for value in record["data"].values())


def test_guided_letter_pending_identity_does_not_search(build, request_fixture):
    letter = guided_letter(build(request_fixture("identity-pending")))
    assert "confirmar su identidad" in letter and "no buscaremos información" in letter
    assert "registro" not in letter


def test_guided_letter_marks_modifications_as_proposals(build, request_fixture):
    letter = guided_letter(build(request_fixture("erasure")))
    assert "solicitud de supresión o cancelación" in letter
    assert "son una propuesta: no se aplicarán sin la aprobación" in letter


def test_guided_letter_lists_each_deadline_when_they_differ(build, peru_request):
    package = build(peru_request(["access", "rectification"]))
    dates = {item["deadline_at"] for item in package["deadlines"].values()}
    letter = guided_letter(package)
    if len(dates) > 1:
        assert "Cada derecho tiene su propio plazo" in letter
        assert all(date in letter for date in dates)


def test_guided_letter_reflects_the_human_decision(build, request_fixture):
    package = build(request_fixture("access"))
    package["human_decision"] = {"decision": "APPROVED", "reviewer": "DPO", "at": "2026-10-02", "note": "Procede"}
    assert "La persona responsable aprobó la propuesta" in guided_letter(package)
    package["human_decision"]["decision"] = "REJECTED"
    assert "no aprobó la propuesta" in guided_letter(package)


def test_template_sections_match_render(build, peru_request):
    template = (Path(__file__).resolve().parents[2] / "knowledge" / "assets" / "response-template.md")
    headings = [line for line in template.read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
    text = render_response(build(peru_request(["access", "rectification"])))
    for heading in headings:
        if heading not in {"## Carta al titular (borrador, no enviada)", "## Fundamento recuperado por el RAG"}:
            assert heading in text


def _imports(path: Path) -> set[str]:
    modules = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            modules.add((node.module or "").split(".")[0])
    return modules


def test_core_only_uses_standard_library():
    files = sorted(CORE_DIR.glob("*.py"))
    assert len(files) >= 10
    for path in files:
        outside = _imports(path) - set(sys.stdlib_module_names) - {"__future__"}
        assert not outside, f"{path.name} importa {sorted(outside)}"
