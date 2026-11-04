"""Human-decision bridge for Group 3 (integration tooling, not part of the agent).

G3 deliberately keeps `verify_identity` and `decide` out of its MCP tools so that no model can approve a case.
This small internal HTTP bridge exposes exactly those two functions, ONLY to the platform backend, which calls it
for an authenticated human (the person's name is recorded as the reviewer). It is not reachable by the models:
the orchestrator adapter for G3 never offers these actions."""
import os
from typing import Literal

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

from dsar.core.errors import CaseInputError, TransitionError
from dsar.services import cases, controls, decisions, drafting, export, intake, metrics, org_policy, outbox, system
from dsar.services.context import build_context
from dsar.services.errors import LLMError, MailboxError, NotFoundError

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


# ---------------------------------------------------------------- G3 case work for the signed-in DPO
# The rest of the agent's own panel (expediente, draft, extension, export, mail intake, outbox, indicators,
# policy). Same rule as above: only the platform backend calls it, with the token and the person's name as
# `reviewer`. Nothing here approves a case or runs a right; sending stays off unless DSAR_MAIL_SEND_ENABLED=true.
ERROR_CODES = ((NotFoundError, 404), (TransitionError, 409), (CaseInputError, 422), (ValueError, 422),
               (LLMError, 502), (MailboxError, 502))


def _token(x_bridge_token: str | None = Header(default=None)) -> None:
    _auth(x_bridge_token)


gestion = APIRouter(prefix="/gestion", dependencies=[Depends(_token)])


def _run(call, *args):
    try:
        return call(build_context(), *args)
    except tuple(error for error, _ in ERROR_CODES) as e:
        raise HTTPException(next(code for error, code in ERROR_CODES if isinstance(e, error)), str(e))


class Reviewer(BaseModel):
    reviewer: str


class Extend(Reviewer):
    right: str
    reason: str
    days: int | None = None


class Note(Reviewer):
    note: str


class Draft(BaseModel):
    mode: str = "guided"
    letter: bool = True


class Export(BaseModel):
    draft: str


class Confirm(Reviewer):
    request_types: list[str]
    subject_email: str


class Reason(Reviewer):
    reason: str


class Count(BaseModel):
    count: int = 25


class Limit(BaseModel):
    limit: int = 50


class Prepare(BaseModel):
    case_id: str
    kind: str = "respuesta"
    to_address: str | None = None
    missing: str | None = None


class Edit(Reviewer):
    subject: str
    body: str


class Policy(BaseModel):
    policy: dict
    text: str | None = None


@gestion.get("/casos")
def list_cases(estado: str | None = Query(default=None, max_length=30)):
    return _run(cases.list_cases, estado)


@gestion.get("/casos/{case_id}")
def get_case(case_id: str):
    return _run(cases.get, case_id) | {"controls": _run(controls.for_case, case_id)}


@gestion.post("/casos/{case_id}/borrador")
def draft(case_id: str, body: Draft):
    return _run(drafting.draft, case_id, body.mode, None, body.letter)


@gestion.get("/casos/{case_id}/prorroga")
def extension_options(case_id: str, derecho: str = Query(max_length=20), dias: int | None = Query(default=None, ge=1, le=60)):
    return _run(decisions.extension_options, case_id, derecho, dias)


@gestion.post("/casos/{case_id}/prorroga")
def extend(case_id: str, body: Extend):
    return _run(decisions.extend, case_id, body.right, body.reason, body.reviewer, body.days)


@gestion.post("/casos/{case_id}/reanudar")
def resume(case_id: str, body: Note):
    return _run(decisions.resume, case_id, body.reviewer, body.note)


@gestion.post("/casos/{case_id}/exportar")
def export_case(case_id: str, body: Export):
    # The files stay in the agent volume; the DPO also gets their content to download from the browser.
    out = _run(export.export_case, case_id, body.draft, [])
    return out | {"package": _run(cases.get, case_id), "draft": body.draft}


@gestion.get("/correos")
def list_inbound(estado: str | None = Query(default=None, max_length=20), caso: str | None = Query(default=None, max_length=30)):
    return _run(intake.list_inbound, estado, caso)


@gestion.get("/correos/resumen")
def mail_summary():
    return _run(intake.summary)


@gestion.post("/correos/sincronizar")
def synchronize(body: Limit):
    return _run(intake.synchronize, max(1, min(body.limit, 200)))


@gestion.post("/correos/demo")
def mail_demo(body: Count):
    return _run(intake.load_demo, max(1, min(body.count, 50)), None)


@gestion.get("/correos/{inbound_id}")
def get_inbound(inbound_id: int):
    return _run(intake.get, inbound_id)


@gestion.post("/correos/{inbound_id}/confirmar")
def confirm(inbound_id: int, body: Confirm):
    return _run(intake.confirm, inbound_id, body.reviewer, body.request_types, body.subject_email)


@gestion.post("/correos/{inbound_id}/descartar")
def discard_inbound(inbound_id: int, body: Reason):
    return _run(intake.discard, inbound_id, body.reviewer, body.reason)


@gestion.get("/salida")
def list_outbox(estado: str | None = Query(default=None, max_length=20), caso: str | None = Query(default=None, max_length=30)):
    return _run(outbox.list_outbox, estado, caso)


@gestion.post("/salida")
def prepare(body: Prepare):
    return _run(lambda ctx: outbox.prepare(ctx, body.case_id, body.kind, body.to_address, missing=body.missing))


@gestion.put("/salida/{outbox_id}")
def edit(outbox_id: int, body: Edit):
    return _run(outbox.edit, outbox_id, body.reviewer, body.subject, body.body)


@gestion.post("/salida/{outbox_id}/enviar")
def send(outbox_id: int, body: Reviewer):
    return _run(outbox.send, outbox_id, body.reviewer)


@gestion.post("/salida/{outbox_id}/descartar")
def discard_outbox(outbox_id: int, body: Reason):
    return _run(outbox.discard, outbox_id, body.reviewer, body.reason)


@gestion.get("/indicadores")
def indicators():
    return _run(metrics.indicators)


@gestion.get("/politica")
def get_policy():
    return _run(org_policy.get)


@gestion.put("/politica")
def save_policy(body: Policy):
    return _run(org_policy.save, body.policy, body.text)


@gestion.get("/auditoria")
def audit():
    return {"llm": _run(system.llm_log, 50), "skill": system.skill_fingerprint(), "modelos": _run(system.models)}


app.include_router(gestion)
