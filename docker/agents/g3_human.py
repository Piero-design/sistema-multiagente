"""Human-decision bridge for Group 3 (integration tooling, not part of the agent).

G3 deliberately keeps `verify_identity` and `decide` out of its MCP tools so that no model can approve a case.
This small internal HTTP bridge exposes exactly those two functions, ONLY to the platform backend, which calls it
for an authenticated human (the person's name is recorded as the reviewer). It is not reachable by the models:
the orchestrator adapter for G3 never offers these actions."""
import json
import os
import re
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from dsar.core.errors import CaseInputError, TransitionError
from dsar.services import cases, decisions
from dsar.services.context import build_context

TOKEN = os.environ.get("HUMAN_BRIDGE_TOKEN", "")
app = FastAPI(title="G3 human bridge")


def _auth(token: str | None) -> None:
    if not TOKEN or token != TOKEN:
        raise HTTPException(401, "bridge token required")


class Verify(BaseModel):
    case_id: str
    verified_by: str
    method: str
    reference: str = ""


class Decide(BaseModel):
    case_id: str
    reviewer: str
    decision: Literal["APPROVED", "REJECTED", "CANCELLED"]
    note: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/verify")
def verify(body: Verify, x_bridge_token: str | None = Header(default=None)):
    _auth(x_bridge_token)
    try:
        out = cases.verify_identity(build_context(), body.case_id, body.verified_by, body.method, body.reference)
    except (CaseInputError, TransitionError) as e:
        raise HTTPException(422, str(e))
    return {"status": out["case"]["status"], "case_id": body.case_id}


@app.post("/decide")
def decide(body: Decide, x_bridge_token: str | None = Header(default=None)):
    _auth(x_bridge_token)
    try:
        out = decisions.decide(build_context(), body.case_id, body.reviewer, body.decision, body.note)
    except (CaseInputError, TransitionError) as e:
        raise HTTPException(422, str(e))
    return {"status": out["case"]["status"], "case_id": body.case_id,
            "handoffs": [{"to": h["to_agent"], "action": h["action"]} for h in out["handoffs"]]}


@app.get("/handoffs/{case_id}")
def original_handoffs(case_id: str, x_bridge_token: str | None = Header(default=None)):
    """Read-only: the envelopes exactly as G3 wrote them (needed by receivers that verify the SHA-256).
    They carry references and hashes only; G3 never puts personal data values in a handoff."""
    _auth(x_bridge_token)
    if not re.fullmatch(r"[A-Za-z0-9-]{6,60}", case_id):
        raise HTTPException(400, "invalid case id")
    folder = build_context().settings.handoff_dir / case_id.lower()
    if not folder.is_dir():
        raise HTTPException(404, "no handoffs for this case")
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(folder.glob("*.json"))]
