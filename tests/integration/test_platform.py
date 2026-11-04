"""Integration + rule-regression tests against the RUNNING stack (docker compose up -d).
Run: pytest tests/integration -q      Env: PLATFORM_URL (default http://localhost:8080)
Reports the LLM mode in use; nothing here is marked passed without executing against the live services."""
import os
import time

import httpx
import pytest

BASE = os.getenv("PLATFORM_URL", "http://localhost:8080")


def get(path, **kw):
    return httpx.get(BASE + path, timeout=kw.pop("timeout", 30), **kw)


def run(agent, action, payload, wait=240):
    r = httpx.post(f"{BASE}/api/agents/{agent}/execute", json={"action": action, "input": payload}, timeout=30)
    assert r.status_code == 202, r.text
    eid = r.json()["execution_id"]
    end = time.time() + wait
    while time.time() < end:
        e = get(f"/api/executions/{eid}").json()
        if e["status"] in ("succeeded", "failed"):
            return e
        time.sleep(2)
    raise TimeoutError(eid)


@pytest.fixture(scope="session")
def system():
    return get("/api/system").json()


def test_llm_mode_is_reported(system):
    print("LLM_MODE:", system["llm"]["mode"])
    assert system["llm"]["ok"] and system["llm"]["mode"] in ("cloud", "ollama", "mock")
    assert system["llm"]["simulated"] == (system["llm"]["mode"] == "mock")


def test_postgres_loaded_from_professor_script(system):
    assert system["database"]["ok"] and system["database"]["demo_tables"] >= 50


def test_all_eight_agents_listed_with_real_status():
    agents = {a["group"]: a for a in get("/api/agents", timeout=60).json()}
    assert sorted(agents) == list(range(1, 9))
    for g, a in agents.items():
        assert a["status"] in ("operativo", "degradado", "caido", "parcial"), a      # G6 is integrated now
        if a["status"] != "operativo":
            assert a["reason"]


def test_g6_runs_a_real_action():
    e = run("inventario", "consultar_inventario", {"organizacion": "UNSA-DEMO"})
    assert e["status"] == "succeeded" and e["result"]["output"]["status"] == "ok"


def test_unknown_action_rejected():
    r = httpx.post(f"{BASE}/api/agents/dsar/execute", json={"action": "dsar_decidir", "input": {}}, timeout=30)
    assert r.status_code == 422


# ---- human-in-the-loop rules (G3, G5, G8): no model-callable approve/decide capability is exposed ----
FORBIDDEN = ("aprobar", "approve", "decid", "decide", "verify_identity", "rechazar", "notificar", "enviar")


@pytest.mark.parametrize("agent", ["dsar", "terceros", "incidentes", "auditoria"])
def test_no_approval_capability_exposed(agent):
    caps = get(f"/api/agents/{agent}", timeout=60).json()["capabilities"]
    for c in caps:
        assert not any(w in c["action"].lower() for w in FORBIDDEN), c


def test_g3_deadlines_deterministic():
    e = run("dsar", "dsar_calcular_plazos",
            {"request_types": ["erasure"], "received_at": "2026-11-03", "policy_id": "PE-LEY29733"})
    assert e["status"] == "succeeded"
    d = e["result"]["output"]["deadlines"]["erasure"]
    assert d["days"] == 10 and d["deadline_at"] == "2026-11-17"   # same value as before integration


def test_g4_hash_deterministic():
    e = run("auditoria", "hash", {"contenido": "abc"})
    assert e["result"]["output"]["sha256"] == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_execution_is_persisted_and_listed():
    e = run("dsar", "dsar_listar", {})
    assert any(x["id"] == e["id"] for x in get("/api/executions?agent_id=dsar").json())
    assert get("/api/activity").json()["events"]


def test_g2_reports_real_state_with_reason():
    g2 = next(a for a in get("/api/agents", timeout=60).json() if a["group"] == 2)
    if g2["status"] != "operativo":
        assert g2["reason"]       # degraded/down must always say why
