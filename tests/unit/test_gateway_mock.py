"""Gateway unit tests. LLM_MODE=mock (no network, simulated output)."""
import importlib
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "llm-gateway"))


def _client():
    os.environ["LLM_MODE"] = "mock"
    import gateway
    importlib.reload(gateway)
    return TestClient(gateway.app)


def test_health_flags_simulated():
    j = _client().get("/health").json()
    assert j["mode"] == "mock" and j["simulated"] is True and j["data_leaves_machine"] is False


def test_openai_and_ollama_surfaces_label_mock():
    c = _client()
    r = c.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "hola"}]}).json()
    assert "SIMULADA" in r["choices"][0]["message"]["content"]
    g = c.post("/api/generate", json={"prompt": "hola", "model": "x"}).json()
    assert g["done"] and "SIMULADA" in g["response"]
    e = c.post("/api/embed", json={"input": ["a", "b"]}).json()
    assert len(e["embeddings"]) == 2 and len(e["embeddings"][0]) == 64
    assert c.get("/api/tags").json()["models"]


def test_metrics_count_calls():
    c = _client()
    c.post("/api/chat", json={"messages": [{"role": "user", "content": "x"}]})
    assert c.get("/metrics").json()["requests"] >= 1


def test_gemini_thought_signature_is_reattached():
    import gateway
    gateway._sigs.clear()
    out = {"choices": [{"message": {"tool_calls": [{"id": "c1", "extra_content": {"google": {"thought_signature": "SIG"}}}]}}]}
    gateway._remember_signatures(out)
    msgs = [{"role": "assistant", "tool_calls": [{"id": "c1"}, {"id": "other"}]}]
    res = gateway._restore_signatures(msgs)
    assert res[0]["tool_calls"][0]["extra_content"]["google"]["thought_signature"] == "SIG"
    assert res[0]["tool_calls"][1]["extra_content"]["google"]["thought_signature"] == "skip_thought_signature_validator"
