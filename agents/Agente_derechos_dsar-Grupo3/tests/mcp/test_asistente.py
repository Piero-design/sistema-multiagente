"""Herramienta MCP dsar_asistente y proveedor del gateway de la plataforma."""

from __future__ import annotations

import json

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from dsar.assistant.llm import default_providers
from dsar.assistant.llm import gateway
from dsar.assistant.llm.base import LLMError
from dsar.mcp import tools


def test_guided_norm_question_answers_with_sources(service_ctx):
    out = tools.asistente(service_ctx, "¿Qué plazo hay para atender un derecho de acceso?")
    assert out["scope"] == "dsar" and out["answer"]
    assert all(set(item) == {"chunk_id", "source", "section"} for item in out["sources"])


def test_case_draft_never_leaves_through_mcp(service_ctx):
    case = tools.crear_caso(service_ctx, "person-001", ["access"], received_at="2026-10-20",
                            identity_status="verified", identity_reference="REF-1")
    out = tools.asistente(service_ctx, "Redacta un borrador de respuesta para este caso.", case["case_id"])
    assert out["answer"] == tools.DRAFT_ELSEWHERE and "draft" not in out


def test_out_of_scope_and_unknown_mode(service_ctx):
    assert tools.asistente(service_ctx, "¿Cuál es la capital de Francia?")["scope"] == "out_of_scope"
    with pytest.raises(ToolError):
        tools.asistente(service_ctx, "¿Qué plazo hay para el acceso?", modo="otro")


def test_cloud_mode_uses_minimized_facts(service_ctx):
    provider = service_ctx.providers["gemini"]
    case = tools.crear_caso(service_ctx, "person-001", ["access"], received_at="2026-10-20",
                            identity_status="verified", identity_reference="REF-1")
    out = tools.asistente(service_ctx, "Explica este caso.", case["case_id"], "gemini")
    assert out["answer"] == provider.reply and provider.calls[-1]["history"] is None


def test_gateway_provider_only_when_configured(monkeypatch):
    monkeypatch.delenv("DSAR_GATEWAY_URL", raising=False)
    assert "gateway" not in default_providers()
    monkeypatch.setenv("DSAR_GATEWAY_URL", "http://llm-gateway:8080/v1")
    providers = default_providers()
    assert providers["gateway"].cloud is True and "ollama" in providers


def test_gateway_provider_calls_openai_endpoint(monkeypatch):
    sent = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"model": "gemini-x", "choices": [{"finish_reason": "stop",
                                                                 "message": {"content": "Hola"}}]}).encode()

    def urlopen(req, timeout):
        sent.update(url=req.full_url, body=json.loads(req.data))
        return Response()

    monkeypatch.setenv("DSAR_GATEWAY_URL", "http://llm-gateway:8080/v1/")
    monkeypatch.setattr(gateway.request, "urlopen", urlopen)
    result = gateway.GatewayProvider().complete("sistema", "usuario", history=[{"role": "user", "content": "x"}])
    assert result.text == "Hola" and result.model == "gemini-x"
    assert sent["url"] == "http://llm-gateway:8080/v1/chat/completions"
    assert [m["role"] for m in sent["body"]["messages"]] == ["system", "user"]   # sin historial


def test_gateway_errors_are_llm_errors(monkeypatch):
    monkeypatch.delenv("DSAR_GATEWAY_URL", raising=False)
    with pytest.raises(LLMError):
        gateway.GatewayProvider().complete("s", "u")
    with pytest.raises(LLMError):
        gateway.parse_response({"choices": [{"finish_reason": "length", "message": {"content": "a"}}]})
