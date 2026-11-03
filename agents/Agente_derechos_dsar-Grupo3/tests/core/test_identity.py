from __future__ import annotations

import copy

import pytest

from dsar.core.engine import verify_identity
from dsar.core.errors import CaseInputError, TransitionError
from dsar.core.validator import validate
from support import GENERATED_AT

VERIFIED_AT = GENERATED_AT.replace(hour=15)


def verify(package, records, profiles, organization=None, **changes):
    options = {"verified_by": "Revisora Demo", "method": "documento cotejado", "reference": "ref-001",
               "verified_at": VERIFIED_AT, "organization": organization} | changes
    return verify_identity(package, records, profiles, **options)


def test_verification_continues_the_case_from_identity_pending(build, request_fixture, records, profiles):
    pending = build(request_fixture("identity-pending"))
    original = copy.deepcopy(pending)
    verified = verify(pending, records, profiles)

    assert pending == original
    assert verified["status"] == "APPROVAL_REQUIRED"
    assert {item["record_id"] for item in verified["discovered_records"]}
    assert verified["identity_verification"]["status"] == "verified"
    assert verified["identity_verification"]["verified_by"] == "Revisora Demo"
    assert verified["deadlines"] == pending["deadlines"]
    trail = verified["audit_trail"]
    assert trail[:len(pending["audit_trail"])] == pending["audit_trail"]
    assert [item["state"] for item in trail[len(pending["audit_trail"]):]] == ["VERIFIED", "DISCOVERY", "APPROVAL_REQUIRED"]
    assert "La identidad no ha sido verificada" not in " ".join(verified["hitl"]["reasons"])
    assert validate(verified) == []


def test_without_records_the_case_still_needs_review(build, request_fixture, records, profiles):
    verified = verify(build(request_fixture("identity-pending", principal_id="mail-000000000000")), records, profiles)
    assert verified["discovered_records"] == []
    assert verified["status"] in {"REVIEW", "APPROVAL_REQUIRED"}
    assert validate(verified) == []


def test_only_identity_pending_cases_can_be_verified(build, request_fixture, records, profiles):
    with pytest.raises(TransitionError):
        verify(build(request_fixture("access")), records, profiles)


def test_the_reviewer_and_method_are_required(build, request_fixture, records, profiles):
    pending = build(request_fixture("identity-pending"))
    with pytest.raises(CaseInputError):
        verify(pending, records, profiles, verified_by="  ")
    with pytest.raises(CaseInputError):
        verify(pending, records, profiles, method="")


def test_the_policy_must_be_the_one_applied_at_registration(build, peru_request, records, profiles, org):
    request = peru_request(["access"])
    request["identity_verification"]["status"] = "pending"
    pending = build(request, org)
    assert pending["organization"]["applied"] is True
    assert verify(pending, records, profiles, organization=org)["status"] in {"REVIEW", "APPROVAL_REQUIRED"}

    changed = copy.deepcopy(org) | {"version": "otra"}
    with pytest.raises(CaseInputError, match="cambio"):
        verify(pending, records, profiles, organization=changed)
    with pytest.raises(CaseInputError):
        verify(pending, records, profiles, organization=None)
