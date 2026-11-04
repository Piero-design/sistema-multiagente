"""Herramienta MCP dsar_controles: controles y cláusulas ISO de un expediente, solo lectura."""

from __future__ import annotations

import asyncio

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from dsar.mcp import tools
from dsar.mcp.server import create_server


def codes(result: dict) -> list[str]:
    return [item["control"] for item in result["controls"]]


def test_pending_identity_cites_risk_treatment_and_core_controls(service_ctx):
    case = tools.crear_caso(service_ctx, "person-001", ["erasure"], received_at="2026-10-20")
    result = tools.controles(service_ctx, case["case_id"])
    assert result["status"] == "IDENTITY_PENDING"
    assert codes(result)[:2] == ["A.1.3.7", "A.1.3.10"]
    assert "Cláusula 8.3" in codes(result) and "Cláusula 5.3" in codes(result)
    assert all(item["title"] and item["reason"] for item in result["controls"])


def test_verified_rectification_cites_accuracy_without_risk_clause(service_ctx):
    case = tools.crear_caso(service_ctx, "person-001", ["rectification"], received_at="2026-10-20",
                            identity_status="verified", identity_reference="REF-1")
    found = codes(tools.controles(service_ctx, case["case_id"]))
    assert "A.1.4.4" in found and "Cláusula 8.3" not in found
    assert [code for code in found if code.startswith("Cláusula")] == \
        ["Cláusula 8.1", "Cláusula 5.3", "Cláusula 7.4", "Cláusula 9.1", "Cláusula 9.2"]


def test_reading_controls_does_not_change_the_case(service_ctx):
    case = tools.crear_caso(service_ctx, "person-001", ["access"], received_at="2026-10-20")
    before = tools.estado(service_ctx, case["case_id"])
    tools.controles(service_ctx, case["case_id"])
    assert tools.estado(service_ctx, case["case_id"]) == before


def test_unknown_case_is_a_tool_error(service_ctx):
    with pytest.raises(ToolError):
        tools.controles(service_ctx, "DSAR-NO-EXISTE")


def test_server_offers_controls_and_still_no_decision_tools(service_ctx):
    names = {tool.name for tool in asyncio.run(create_server(service_ctx).list_tools())}
    assert {"dsar_controles", "dsar_asistente"} <= names and len(names) == 10
    assert not {name for name in names if any(word in name for word in ("aprobar", "decid", "verific", "ejecut"))}
