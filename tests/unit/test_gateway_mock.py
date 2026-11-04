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


def test_each_team_uses_its_own_key_and_is_blocked_without_one(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "cloud")
    monkeypatch.setenv("LLM_BASE_URL", "http://upstream.invalid/v1")
    monkeypatch.setenv("LLM_API_KEY", "SHARED")
    monkeypatch.setenv("LLM_ALLOW_SHARED_FALLBACK", "false")
    monkeypatch.setenv("LLM_API_KEY_G8", "KEY-G8")
    monkeypatch.delenv("LLM_API_KEY_G1", raising=False)
    import gateway
    importlib.reload(gateway)
    assert gateway.team_key("g8") == "KEY-G8"
    assert gateway.team_key("g1") == ""                      # no silent use of another team's / the shared key
    c = TestClient(gateway.app)
    r = c.post("/g1/v1/chat/completions", json={"messages": [{"role": "user", "content": "hola"}]})
    assert r.status_code == 401 and r.json()["error"]["code"] == "missing_team_key"
    t = c.get("/teams").json()["teams"]
    assert t["g8"]["own_key"] is True and t["g1"]["own_key"] is False and t["g1"]["usable"] is False
    assert "KEY-G8" not in c.get("/teams").text              # keys are never returned
    assert c.post("/g99/v1/chat/completions", json={"messages": []}).status_code == 404
    monkeypatch.setenv("LLM_ALLOW_SHARED_FALLBACK", "true")
    importlib.reload(gateway)
    assert gateway.team_key("g1") == "SHARED"                # development switch


def test_team_prefixes_work_in_mock_mode():
    c = _client()
    for p in ("/g1/api/generate", "/g7/api/generate"):
        assert c.post(p, json={"prompt": "hola"}).json()["done"]
    assert c.post("/g8/openai/v1/chat/completions", json={"messages": [{"role": "user", "content": "x"}]}).status_code == 200
    assert c.post("/openai/v1/chat/completions", json={"messages": [{"role": "user", "content": "x"}]}).status_code == 200
    assert c.get("/g2/api/tags").json()["models"]
