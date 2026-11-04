"""Central orchestrator: registry, routing, async execution lifecycle persisted in PostgreSQL.
It calls agents only through adapters and never replaces their processing."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import uuid

import httpx
from typing import Any

from backend.adapters.agents import ADAPTERS
from backend.services import db
from shared.contracts.agent_contract import ExecutionRequest

_tasks: set[asyncio.Task] = set()


def _event(execution_id, agent_id: str, kind: str, message: str = "") -> None:
    try:
        db.execute("INSERT INTO orchestrator.event (execution_id, agent_id, kind, message) VALUES (%s,%s,%s,%s)",
                   (execution_id, agent_id, kind, message[:500]))
    except Exception:  # noqa: BLE001  logging must never break an execution
        pass


def _gestitel_log(eid: str, agent_id: str, action: str, status: str, seconds: float | None, simulated: bool) -> None:
    """Shared operational trail in Gestitel (demo.core_securitylog). Metadata only: no input, no output."""
    try:
        db.execute(
            "INSERT INTO demo.core_securitylog (username, action, module, object_type, detail, created_at) "
            "VALUES ('orquestador', 'agent_execute', %s, 'execution', %s::jsonb, now())",
            (agent_id, json.dumps({"execution_id": eid, "agent_action": action, "status": status,
                                   "llm_mode": os.getenv("LLM_MODE", "cloud"), "simulated": simulated,
                                   "seconds": seconds, "source": "plataforma-multiagente"})))
    except Exception:  # noqa: BLE001  the platform never fails because of the trail
        pass


def list_agents() -> list[dict]:
    return [a.get_info() for a in sorted(ADAPTERS.values(), key=lambda a: a.group)]


def get_adapter(agent_id: str):
    if agent_id not in ADAPTERS:
        raise KeyError(agent_id)
    return ADAPTERS[agent_id]


async def _teams() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            return (await c.get(f"{os.getenv('GATEWAY_URL', 'http://llm-gateway:8080')}/teams")).json()["teams"]
    except Exception:  # noqa: BLE001
        return {}


async def health_all() -> list[dict]:
    teams = await _teams()

    async def one(a):
        try:
            h = await asyncio.wait_for(a.health_check(), 12)
        except Exception as e:  # noqa: BLE001   per-agent isolation
            h = {"status": "caido", "reason": type(e).__name__, "detail": {}}
        t = teams.get(a.llm_team) if a.llm_team else None
        if t is not None and not t["usable"] and h.get("status") == "operativo":
            h = {**h, "status": "degradado", "reason": f"Falta la clave de Gemini del equipo {a.llm_team.upper()} "
                                                       f"(LLM_API_KEY_{a.llm_team.upper()} en el .env)"}
        return {**a.get_info(), **h, "capabilities": len(a.get_capabilities()),
                "llm_team": a.llm_team or None, "team_key": None if t is None else t["own_key"]}
    return await asyncio.gather(*(one(a) for a in sorted(ADAPTERS.values(), key=lambda a: a.group)))


def submit(agent_id: str, action: str, payload: dict) -> str:
    adapter = get_adapter(agent_id)
    allowed = {c["action"] for c in adapter.get_capabilities()}
    if action not in allowed:
        raise ValueError(f"Acción '{action}' no existe en {agent_id}. Disponibles: {sorted(allowed)}")
    eid = str(uuid.uuid4())
    h = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]
    db.execute("INSERT INTO orchestrator.execution (id, agent_id, action, status, llm_mode, input_hash) "
               "VALUES (%s,%s,%s,'queued',%s,%s)", (eid, agent_id, action, os.getenv("LLM_MODE", "cloud"), h))
    _event(eid, agent_id, "submitted", action)
    t = asyncio.create_task(_run(eid, adapter, action, payload))
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)
    return eid


async def _run(eid: str, adapter, action: str, payload: dict) -> None:
    db.execute("UPDATE orchestrator.execution SET status='running', started_at=now() WHERE id=%s", (eid,))
    _event(eid, adapter.id, "started", action)
    try:
        res: dict[str, Any] = await adapter.execute(ExecutionRequest(action=action, input=payload))
        db.execute("UPDATE orchestrator.execution SET status='succeeded', finished_at=now(), result=%s::jsonb, "
                   "simulated=%s WHERE id=%s",
                   (json.dumps(res, default=str), bool(res.get("simulated")) or os.getenv("LLM_MODE") == "mock", eid))
        _event(eid, adapter.id, "finished", action)
        _gestitel_log(eid, adapter.id, action, "succeeded", None, bool(res.get("simulated")) or os.getenv("LLM_MODE") == "mock")
    except Exception as e:  # noqa: BLE001  one agent failing never crashes the platform
        db.execute("UPDATE orchestrator.execution SET status='failed', finished_at=now(), error=%s WHERE id=%s",
                   (f"{type(e).__name__}: {e}"[:1000], eid))
        _event(eid, adapter.id, "failed", f"{type(e).__name__}")
        _gestitel_log(eid, adapter.id, action, "failed", None, os.getenv("LLM_MODE") == "mock")


def get_status(eid: str) -> dict | None:
    r = db.query("SELECT id::text, agent_id, action, status, llm_mode, simulated, error, created_at, started_at, "
                 "finished_at, EXTRACT(EPOCH FROM (COALESCE(finished_at, now()) - started_at)) AS seconds "
                 "FROM orchestrator.execution WHERE id=%s", (eid,))
    return r[0] if r else None


def get_result(eid: str) -> dict | None:
    r = db.query("SELECT result, error, status FROM orchestrator.execution WHERE id=%s", (eid,))
    return r[0] if r else None


def get_history(agent_id: str | None = None, limit: int = 50) -> list[dict]:
    sql = ("SELECT id::text, agent_id, action, status, llm_mode, simulated, error, created_at, finished_at "
           "FROM orchestrator.execution ")
    if agent_id:
        return db.query(sql + "WHERE agent_id=%s ORDER BY created_at DESC LIMIT %s", (agent_id, limit))
    return db.query(sql + "ORDER BY created_at DESC LIMIT %s", (limit,))


def activity(limit: int = 100) -> list[dict]:
    return db.query("SELECT id, execution_id::text, agent_id, kind, message, created_at "
                    "FROM orchestrator.event ORDER BY id DESC LIMIT %s", (limit,))


def stats() -> dict:
    rows = db.query("SELECT agent_id, status, count(*) AS n FROM orchestrator.execution GROUP BY 1,2")
    return {"by_agent": rows}
