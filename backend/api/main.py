"""Backend API for the unified frontend."""
from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.adapters.agents import ADAPTERS
from backend.orchestrator import orchestrator as orch
from backend.services import db

app = FastAPI(title="Plataforma multiagente PIMS")
GATEWAY = os.getenv("GATEWAY_URL", "http://llm-gateway:8080")


class ExecuteBody(BaseModel):
    action: str
    input: dict = {}


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/agents")
async def agents():
    return await orch.health_all()


@app.get("/api/agents/{agent_id}")
async def agent(agent_id: str):
    try:
        a = orch.get_adapter(agent_id)
    except KeyError:
        raise HTTPException(404, "Agente desconocido")
    return {**a.get_info(), **await a.health_check(), "capabilities": a.get_capabilities()}


@app.post("/api/agents/{agent_id}/execute", status_code=202)
async def execute(agent_id: str, body: ExecuteBody):
    try:
        return {"execution_id": orch.submit(agent_id, body.action, body.input)}
    except KeyError:
        raise HTTPException(404, "Agente desconocido")
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/api/executions")
async def executions(agent_id: str | None = None, limit: int = 50):
    return orch.get_history(agent_id, min(limit, 200))


@app.get("/api/executions/{eid}")
async def execution(eid: str):
    s = orch.get_status(eid)
    if not s:
        raise HTTPException(404, "No existe")
    return {**s, **{k: v for k, v in (orch.get_result(eid) or {}).items() if k == "result"}}


@app.get("/api/activity")
async def activity(limit: int = 100):
    return {"events": orch.activity(min(limit, 500)), **orch.stats()}


@app.get("/api/system")
async def system():
    llm: dict = {"ok": False}
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            h = (await c.get(f"{GATEWAY}/health")).json()
            m = (await c.get(f"{GATEWAY}/metrics")).json()
        llm = {"ok": True, **h, "last_latency_ms": m.get("last_latency_ms"), "requests": m["requests"],
               "errors": m["errors"], "avg_latency_ms": m["avg_latency_ms"],
               "prompt_tokens": m["prompt_tokens"], "completion_tokens": m["completion_tokens"]}
    except Exception as e:  # noqa: BLE001
        llm = {"ok": False, "error": type(e).__name__}
    return {"llm": llm, "database": db.ping()}


@app.post("/api/system/llm/probe")
async def probe():
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.get(f"{GATEWAY}/probe")
    return r.json()
