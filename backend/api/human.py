"""Human-in-the-loop actions. These are the decisions the agents deliberately leave to a person.
They are NOT agent capabilities: they are separate endpoints that need a signed-in human with the right role,
call the agent's own native decision mechanism, and record who decided (events + Gestitel security log)."""
from __future__ import annotations

import json
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.orchestrator import orchestrator as orch
from backend.services import auth, db

router = APIRouter(prefix="/api")
G5 = os.getenv("AGENT_G5_URL", "http://agent-g5:5678").rstrip("/")
G8 = os.getenv("AGENT_G8_URL", "http://agent-g8:3100").rstrip("/")
G3_BRIDGE = os.getenv("AGENT_G3_BRIDGE_URL", "http://agent-g3:8002").rstrip("/")
BRIDGE_HEADERS = {"X-Bridge-Token": os.getenv("HUMAN_BRIDGE_TOKEN", "")}


def _audit(who: dict, system: str, action: str, target: str, outcome: str) -> None:
    """Who decided what. Metadata only (ids, decision), never the case content."""
    orch._event(None, system, "human_decision", f"{who['user']} ({who['role']}) {action} {target}: {outcome}")
    try:
        db.execute("INSERT INTO demo.core_securitylog (username, action, module, object_type, detail, created_at) "
                   "VALUES (%s, 'human_decision', %s, %s, %s::jsonb, now())",
                   (who["user"], system, action, json.dumps({"role": who["role"], "target": target, "outcome": outcome,
                                                              "source": "plataforma-multiagente"})))
    except Exception:  # noqa: BLE001
        pass


async def _call(method: str, url: str, **kw) -> httpx.Response:
    async with httpx.AsyncClient(timeout=60) as c:
        return await c.request(method, url, **kw)


class LoginBody(BaseModel):
    user: str
    password: str


@router.post("/auth/login")
async def login(b: LoginBody):
    return auth.login(b.user, b.password)


@router.get("/auth/me")
async def me(who: dict = Depends(auth.current)):
    return who


# ---------------------------------------------------------------- pending work for a human
@router.get("/human/pendientes")
async def pendientes(who: dict = Depends(auth.current)):
    out: dict = {"user": who, "terceros": [], "dsar": [], "incidentes": []}
    try:  # G5: expedientes waiting for DPO or Legal
        r = (await _call("GET", f"{G5}/webhook/pims/registro", params={"organizacion": "unsa"})).json()
        out["terceros"] = [{"id_registro": x["id_registro"], "proveedor": x.get("proveedor"), "estado": x["estado"],
                            "puntaje": x.get("puntaje"), "banda": x.get("banda")}
                           for x in r.get("registros", []) if str(x.get("estado", "")).startswith("Pendiente")]
    except Exception as e:  # noqa: BLE001
        out["terceros_error"] = type(e).__name__
    try:  # G3: cases not yet decided
        from backend.adapters.agents import ADAPTERS
        lst = await ADAPTERS["dsar"]._call("dsar_listar", {})
        items = lst if isinstance(lst, list) else (lst.get("cases") or lst.get("items") or []) if isinstance(lst, dict) else []
        out["dsar"] = [{"case_id": c.get("case_id") or c.get("id"), "status": c.get("status")} for c in items
                       if isinstance(c, dict) and c.get("status") not in ("APPROVED", "REJECTED", "CANCELLED")]
    except Exception as e:  # noqa: BLE001
        out["dsar_error"] = type(e).__name__
    try:  # G8: expedientes created through the platform, with their proposed actions
        rows = db.query("SELECT result->'output'->>'incidente' AS inc FROM orchestrator.execution "
                        "WHERE agent_id='incidentes' AND status='succeeded' AND result->'output'->>'incidente' IS NOT NULL "
                        "ORDER BY created_at DESC LIMIT 10")
        for row in rows:
            acc = (await _call("GET", f"{G8}/api/acciones/{row['inc']}")).json().get("acciones", [])
            pend = [a for a in acc if a.get("estado") == "pendiente"]
            if pend:
                out["incidentes"].append({"expediente": row["inc"], "acciones": pend})
    except Exception as e:  # noqa: BLE001
        out["incidentes_error"] = type(e).__name__
    return out


# ---------------------------------------------------------------- G5: DPO then Legal (the agent enforces the order)
class Aprobar(BaseModel):
    id_registro: str
    decision: str            # aprobar | rechazar
    comentario: str = ""


@router.post("/human/terceros/aprobar")
async def terceros_aprobar(b: Aprobar, who: dict = Depends(auth.require("DPO", "Legal"))):
    r = await _call("POST", f"{G5}/webhook/pims/aprobar", json={
        "id_registro": b.id_registro, "rol": who["role"], "decision": b.decision, "usuario": who["user"],
        "comentario": b.comentario})
    _audit(who, "terceros", f"aprobacion_{who['role']}", b.id_registro, f"{b.decision} (HTTP {r.status_code})")
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text[:300])
    return r.json()


# ---------------------------------------------------------------- G3: identity check and decision
class VerifyBody(BaseModel):
    case_id: str
    method: str
    reference: str = ""


class DecideBody(BaseModel):
    case_id: str
    decision: str            # APPROVED | REJECTED | CANCELLED
    note: str


@router.post("/human/dsar/verificar")
async def dsar_verificar(b: VerifyBody, who: dict = Depends(auth.require("DPO"))):
    r = await _call("POST", f"{G3_BRIDGE}/verify", headers=BRIDGE_HEADERS,
                    json={"case_id": b.case_id, "verified_by": who["user"], "method": b.method, "reference": b.reference})
    _audit(who, "dsar", "verificar_identidad", b.case_id, f"HTTP {r.status_code}")
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.json().get("detail", r.text[:300]))
    return r.json()


@router.post("/human/dsar/decidir")
async def dsar_decidir(b: DecideBody, who: dict = Depends(auth.require("DPO"))):
    r = await _call("POST", f"{G3_BRIDGE}/decide", headers=BRIDGE_HEADERS,
                    json={"case_id": b.case_id, "reviewer": who["user"], "decision": b.decision, "note": b.note})
    _audit(who, "dsar", "decision_caso", b.case_id, f"{b.decision} (HTTP {r.status_code})")
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.json().get("detail", r.text[:300]))
    return r.json()


# ---------------------------------------------------------------- G8: approve or reject a PROPOSED action (nothing is executed)
class AccionBody(BaseModel):
    expediente: str
    accion: str              # A1, A2...
    decision: str            # aprobada | rechazada
    nota: str = ""


@router.post("/human/incidentes/decidir")
async def incidentes_decidir(b: AccionBody, who: dict = Depends(auth.require("DPO"))):
    r = await _call("POST", f"{G8}/api/acciones/{b.expediente}/{b.accion}",
                    json={"decision": b.decision, "nota": f"{who['user']}: {b.nota}"[:300]})
    _audit(who, "incidentes", "accion_propuesta", f"{b.expediente}/{b.accion}", f"{b.decision} (HTTP {r.status_code})")
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text[:300])
    return {"ok": True, "nota": "El agente solo registra la decisión; ninguna acción se ejecuta."}
