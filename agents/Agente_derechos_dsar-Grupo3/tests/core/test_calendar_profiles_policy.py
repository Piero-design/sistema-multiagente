"""Calendario, perfiles de jurisdicción y política de la organización."""

from __future__ import annotations

import json
from datetime import date

import pytest

from dsar.core.calendar import CalendarError, add_days, count_days, is_counted_day
from dsar.core.errors import CaseInputError
from dsar.core.policy import load_org_policy, validate_org_policy
from dsar.core.profiles import holidays, load_profiles, validate_profiles

RECEIVED = date(2026, 10, 1)


def test_counting_starts_the_day_after_reception(profiles):
    pe = holidays(profiles["PE-LEY29733"])
    assert add_days(RECEIVED, 1, "calendar") == date(2026, 10, 2)
    assert add_days(RECEIVED, 1, "business", pe) == date(2026, 10, 2)
    # Viernes 2026-10-02 + 1 día hábil salta el fin de semana.
    assert add_days(date(2026, 10, 2), 1, "business", pe) == date(2026, 10, 5)


def test_business_days_skip_holidays(profiles):
    pe = holidays(profiles["PE-LEY29733"])
    assert not is_counted_day(date(2026, 10, 8), "business", pe)
    assert add_days(RECEIVED, 5, "business", pe) == date(2026, 10, 9)


def test_count_days_is_inverse_of_add_days(profiles):
    pe = holidays(profiles["PE-LEY29733"])
    for days in range(0, 25):
        end = add_days(RECEIVED, days, "business", pe)
        assert count_days(RECEIVED, end, "business", pe) == days
    assert count_days(RECEIVED, date(2026, 10, 31), "calendar") == 30
    assert count_days(RECEIVED, RECEIVED, "business", pe) == 0


def test_year_without_holidays_fails(profiles):
    pe = holidays(profiles["PE-LEY29733"])
    with pytest.raises(CalendarError, match="2028"):
        add_days(date(2027, 12, 20), 20, "business", pe)


def test_peru_2027_holidays_are_skipped(profiles):
    pe = holidays(profiles["PE-LEY29733"])
    # 2026-12-31 (jueves) + 1 día hábil: el 1 de enero es feriado, el siguiente hábil es el lunes 4.
    assert add_days(date(2026, 12, 31), 1, "business", pe) == date(2027, 1, 4)
    # Jueves y Viernes Santo de 2027 (25 y 26 de marzo).
    assert add_days(date(2027, 3, 24), 1, "business", pe) == date(2027, 3, 29)


def test_case_crossing_into_year_without_holidays_fails(build, peru_request):
    request = peru_request(["access"])
    request["received_at"] = "2027-12-20"
    with pytest.raises(CaseInputError, match="2028"):
        build(request)


def test_unknown_day_type_fails():
    with pytest.raises(CaseInputError):
        add_days(RECEIVED, 1, "lunar")


def test_profiles_file_is_valid(profiles):
    assert validate_profiles(profiles) == []
    assert set(profiles) == {"LAB-30", "LAB-15-REVIEW", "PE-LEY29733"}


@pytest.mark.parametrize("profile, message", [
    ({"day_type": "business", "response_days": 10}, "necesita feriados"),
    ({"day_type": "calendar", "response_days": 0}, "sin plazo valido"),
    ({"response_days": 10, "supported_rights": ["access", "magic"]}, "desconocidos"),
    ({"response_days": 10, "holidays": {"2026": ["2027-01-01"]}}, "feriado invalido"),
    ({"response_days": 10, "extension": {"allowed": True}}, "max_times"),
    ({"response_days": 10, "additional_information": {"request_within_days": 7}}, "principal_response_days"),
])
def test_invalid_profiles_are_reported(profile, message):
    errors = validate_profiles({"X": profile})
    assert any(message in error for error in errors), errors


def test_load_profiles_rejects_invalid_file(tmp_path):
    path = tmp_path / "perfiles.json"
    path.write_text(json.dumps({"X": {"day_type": "business", "response_days": 5}}), encoding="utf-8")
    with pytest.raises(CaseInputError):
        load_profiles(path)


def test_org_policy_file_is_valid(profiles, org):
    assert validate_org_policy(org, profiles) == []


def test_org_policy_longer_than_legal_fails_to_load(tmp_path, profiles, org):
    org["internal_response_days_by_right"]["rectification"] = 11
    path = tmp_path / "politica.json"
    path.write_text(json.dumps(org, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(CaseInputError, match="supera el legal"):
        load_org_policy(path, profiles)


def test_org_policy_for_unknown_profile_fails(profiles, org):
    org["legal_profile"] = "XX-NADA"
    assert any("desconocido" in error for error in validate_org_policy(org, profiles))


def test_org_policy_shape_errors():
    errors = validate_org_policy({"org_id": "x", "approvers": {"erasure": "DPO"}})
    assert any("Falta el campo name" in error for error in errors)
    assert any("default" in error for error in errors)
