"""Multi-agent flows. Each step is a REAL execution of an agent through its adapter (persisted like any other).
Only connections that the agents' code or catalogs really support are implemented:

  dsar_handoffs        G3 -> G4 / G6        : G3 produces handoffs after a HUMAN decision; the orchestrator transports them.
                                              G4 evaluates the evidence envelope; G6 receives `confirmar_cobertura` (it verifies the
                                              producer's SHA-256). G3 -> G5: G5 has no receiver, so it is stored as sin_receptor.
  inventario_a_auditoria G6 -> G4           : G6's `exportar_evidencia` prepares a document for Group 4 (documented contract);
                                              the orchestrator hands it to G4's audit.
  terceros_a_controles G5 -> G7             : G7's catalog names the Third-Parties agent as owner of A.1.2.7 etc.; G5's per-control
                                              results become G7's `evidencias` input (Cumple -> implementado, Parcial -> parcial).
  inventario_a_riesgos G6 -> G2             : the inventoried system (field NAMES, categories, declared purpose, data subjects; never values)
                                              becomes the question G2 answers about privacy risk (ISO/IEC 27701 6.1.2).
  incidente_a_formacion G8 -> G1            : G8's lessons learned (references only, no personal data) become the question to G1.
Data transformation happens here, at the boundary; no agent is modified."""
from __future__ import annotations

import asyncio
import json
import os
import re
import uuid

import httpx

from backend.orchestrator import orchestrator as orch
from backend.services import db

_tasks: set = set()


class _Steps(list):
    """Persists the executed steps as they happen, so the UI shows real progress."""

    def __init__(self, rid: str):
        super().__init__()
        self.rid = rid

    def append(self, item):
        super().append(item)
        try:
            db.execute("UPDATE orchestrator.flow_run SET steps=%s::jsonb WHERE id=%s", (json.dumps(list(self)), self.rid))
        except Exception:  # noqa: BLE001
            pass


async def _step(agent: str, action: str, payload: dict, steps: list, wait: int = 600) -> dict:
    eid = orch.submit(agent, action, payload)
    end = asyncio.get_event_loop().time() + wait
    while asyncio.get_event_loop().time() < end:
        st = orch.get_status(eid)
        if st["status"] in ("succeeded", "failed"):
            res = orch.get_result(eid)
            steps.append({"agent": agent, "action": action, "execution_id": eid, "status": st["status"]})
            if st["status"] == "failed":
                raise RuntimeError(f"{agent}.{action} falló: {res.get('error')}")
            return res["result"]["output"]
        await asyncio.sleep(2)
    raise TimeoutError(f"{agent}.{action}")


def start(flow: str, params: dict) -> str:
    if flow not in FLOWS:
        raise KeyError(flow)
    rid = str(uuid.uuid4())
    db.execute("INSERT INTO orchestrator.flow_run (id, flow, status) VALUES (%s,%s,'running')", (rid, flow))
    t = asyncio.create_task(_run(rid, flow, params))
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)
    return rid


async def _run(rid: str, flow: str, params: dict) -> None:
    steps = _Steps(rid)
    try:
        result = await FLOWS[flow](rid, params, steps)
        db.execute("UPDATE orchestrator.flow_run SET status='succeeded', steps=%s::jsonb, result=%s::jsonb, "
                   "finished_at=now() WHERE id=%s", (json.dumps(list(steps)), json.dumps(result, default=str), rid))
    except Exception as e:  # noqa: BLE001
        db.execute("UPDATE orchestrator.flow_run SET status='failed', steps=%s::jsonb, error=%s, finished_at=now() "
                   "WHERE id=%s", (json.dumps(list(steps)), f"{type(e).__name__}: {e}"[:1000], rid))


def get(rid: str) -> dict | None:
    r = db.query("SELECT id::text, flow, status, steps, result, error, created_at, finished_at "
                 "FROM orchestrator.flow_run WHERE id=%s", (rid,))
    return r[0] if r else None


def history(limit: int = 20) -> list[dict]:
    return db.query("SELECT id::text, flow, status, created_at, finished_at, error FROM orchestrator.flow_run "
                    "ORDER BY created_at DESC LIMIT %s", (limit,))


def handoffs(limit: int = 50) -> list[dict]:
    return db.query("SELECT id, from_agent, to_agent, delivery_status, delivery_detail, envelope->>'action' AS action, "
                    "COALESCE(envelope->>'case_ref', envelope->>'case_id') AS case_ref, created_at FROM orchestrator.handoff ORDER BY id DESC LIMIT %s",
                    (limit,))


# ---------------------------------------------------------------- G3 -> G4 / G5 / G6
async def dsar_handoffs(rid: str, p: dict, steps: list) -> dict:
    case_id = p["case_id"]
    out = await _step("dsar", "dsar_handoffs", {"case_id": case_id}, steps)
    listed = out if isinstance(out, list) else ([out] if isinstance(out, dict) and out.get("to_agent") else [])
    if not listed:
        raise ValueError("El expediente no tiene handoffs: una persona debe verificar la identidad y decidir primero.")
    # The MCP tool returns a summary; receivers that verify the hash need the producer's original envelope.
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{os.getenv('AGENT_G3_BRIDGE_URL', 'http://agent-g3:8002')}/handoffs/{case_id}",
                        headers={"X-Bridge-Token": os.getenv("HUMAN_BRIDGE_TOKEN", "")})
    envs = r.json() if r.status_code == 200 else listed
    report = []
    for env in envs:
        to = env.get("to_agent")
        status, detail = "sin_receptor", {"motivo": "El agente destino no tiene receptor de handoffs en esta entrega"}
        if env.get("requires_hitl"):
            status, detail = "pendiente_humano", {"motivo": "El sobre exige revisión humana antes de actuar (requires_hitl)"}
        if to == "evidencia":
            # G4 evaluates evidence text; the envelope carries hashes/refs only (G3 never includes personal data values).
            res = await _step("auditoria", "auditar", {"nombre_archivo": f"handoff-{env.get('case_ref') or env.get('case_id')}.json",
                                                      "contenido": json.dumps(env, ensure_ascii=False, indent=2)}, steps)
            status = "entregado"
            detail = {"severidad": res.get("severidad"), "sha256": res.get("sha256"),
                      "nota": "Dictamen propuesto por G4: requiere validación de un auditor humano"}
        if to == "inventario":
            org = p.get("organizacion", "UNSA-DEMO")
            res = await _step("inventario", "recibir_handoff", {"organizacion": org, "handoff": env}, steps)
            d = res.get("data") or {}
            status = "entregado"
            detail = {"hash_verificado": True, "cobertura": d,
                      "nota": "G6 solo consulta su inventario; no busca personas ni modifica el expediente de G3"}
        db.execute("INSERT INTO orchestrator.handoff (from_agent, to_agent, envelope, delivery_status, delivery_detail, "
                   "flow_run_id) VALUES (%s,%s,%s::jsonb,%s,%s::jsonb,%s)",
                   ("dsar", to, json.dumps(env, ensure_ascii=False), status, json.dumps(detail, ensure_ascii=False), rid))
        report.append({"to": to, "action": env.get("action"), "delivery": status, **detail})
    return {"case_id": case_id, "handoffs": report}


# ---------------------------------------------------------------- G5 -> G7
ESTADO_G5_A_G7 = {"Cumple": "implementado", "Parcial": "parcial"}


async def terceros_a_controles(rid: str, p: dict, steps: list) -> dict:
    org = p.get("organizacion", "unsa")
    rol = p.get("rol", "ambos")
    if "id_registro" in p:
        rid5 = p["id_registro"]
    else:
        reg = await _step("terceros", "registro", {"organizacion": org}, steps)
        if not reg.get("registros"):
            raise ValueError("No hay expedientes de G5: audita un contrato primero.")
        rid5 = reg["registros"][0]["id_registro"]
    async with httpx.AsyncClient(timeout=30) as c:
        d = (await c.get(f"{os.getenv('AGENT_G5_URL', 'http://agent-g5:5678')}/webhook/pims/registro/detalle",
                         params={"id": rid5})).json()
    ctrls = d["resultado"]["controles"]
    base = {"perfil": {"rol": rol, "organizacion": p.get("nombre_organizacion", "UNSA")}, "riesgos": []}
    before = await _step("controles", "ejecutar", {"operacion": "generar_soa", **base, "evidencias": []}, steps)
    evid = [{"control": c["control"], "estado": ESTADO_G5_A_G7[c["estado"]],
             "descripcion": f"[Agente de Terceros, expediente {rid5}] {c.get('evidencia') or c.get('observacion') or ''}"[:300]}
            for c in ctrls if c["estado"] in ESTADO_G5_A_G7]
    after = await _step("controles", "ejecutar", {"operacion": "generar_soa", **base, "evidencias": evid}, steps)
    rows = lambda o: {f["control"]: f for f in o["datos"]["soa"]}  # noqa: E731
    b, a = rows(before), rows(after)
    changed = [{"control": k, "antes": b[k]["estado"], "despues": a[k]["estado"]} for k in a if k in {e["control"] for e in evid} and a[k]["estado"] != b[k]["estado"]]
    in_catalog = [c["control"] for c in ctrls if c["control"] in a]
    # G7 reads its own evidence when none is sent, so "before" is not an empty baseline: what is checked is that each state
    # sent from G5 is the one G7 reports for that control
    reflejo = [{"control": e["control"], "enviado": e["estado"], "en_soa": a[e["control"]]["estado"]} for e in evid if e["control"] in a]
    return {"expediente_g5": rid5, "controles_g5": len(ctrls), "controles_g5_en_catalogo_g7": len(in_catalog),
            "evidencias_enviadas_a_g7": len(evid), "controles_que_cambiaron_en_soa": changed,
            "estado_en_soa_de_lo_enviado": reflejo, "resumen_antes": before["datos"]["resumen"], "resumen_despues": after["datos"]["resumen"]}


# ---------------------------------------------------------------- G8 -> G1
async def incidente_a_formacion(rid: str, p: dict, steps: list) -> dict:
    inc = await _step("incidentes", "analizar", {"reporte": p["reporte"], "contexto": p.get("contexto", "demo/unsa-base")}, steps, wait=900)
    text = str(inc.get("resultado") or "")
    m = re.search(r"(?is)(lecciones aprendidas.*?)(?=\n#{1,3} |\Z)", text)
    lessons = (m.group(1) if m else text)[:1800]
    q = ("Un incidente reciente dejó estas lecciones aprendidas (solo referencias, sin datos personales):\n"
         f"{lessons}\n\nPropón 3 capacitaciones concretas de concientización para el personal, indicando a quién va dirigida cada una.")
    chat = await _step("formacion", "chat", {"mensaje": q}, steps)
    return {"incidente_resumen": text[:400], "lecciones_enviadas_a_g1": lessons[:400], "recomendacion_g1": chat.get("text")}


# ---------------------------------------------------------------- G6 -> G4
async def inventario_a_auditoria(rid: str, p: dict, steps: list) -> dict:
    org = p.get("organizacion", "UNSA-DEMO")
    exp = await _step("inventario", "exportar_evidencia", {"organizacion": org}, steps)
    doc = (exp.get("data") or {})
    if not doc.get("contenido"):
        raise ValueError("El inventario está vacío: registra activos en G6 primero.")
    aud = await _step("auditoria", "auditar", {"nombre_archivo": doc.get("nombre_archivo", "inventario.json"),
                                               "contenido": doc["contenido"]}, steps)
    return {"documento": doc.get("nombre_archivo"), "sha256_g6": doc.get("sha256"), "enviado_por_g6": doc.get("enviado"),
            "severidad_propuesta_g4": aud.get("severidad"), "sha256_g4": aud.get("sha256"),
            "nota": "Dictamen propuesto por G4: requiere validación de un auditor humano"}


# ---------------------------------------------------------------- G6 -> G2
def _declared(ctx: dict, key: str) -> str:
    v = (ctx.get(key) or {}).get("valor")
    v = ", ".join(v) if isinstance(v, list) else v
    return v if v and v != "Por determinar" else "no declarado"


async def inventario_a_riesgos(rid: str, p: dict, steps: list) -> dict:
    org = p.get("organizacion", "UNSA-DEMO")
    inv = (await _step("inventario", "consultar_inventario", {"organizacion": org}, steps)).get("data") or {}
    activos = inv.get("activos") or []
    if not activos:
        raise ValueError("El inventario está vacío: registra activos en G6 primero.")
    want = (p.get("sistema") or "").strip().lower()
    pool = [a for a in activos if want in str(a.get("sistema", "")).lower()] if want else activos
    if not pool:
        raise ValueError(f"Ningún activo del inventario coincide con «{p['sistema']}».")
    pii = lambda a: [c for c in a.get("campos", []) if c.get("es_pii")]  # noqa: E731
    a = max(pool, key=lambda x: len(pii(x)))                     # the system exposing the most personal-data fields
    ctx = a.get("contexto") or {}
    campos = [f"{c['nombre']} ({c.get('categoria')})" for c in pii(a)] or ["ningún campo clasificado como dato personal todavía"]
    resumen = {"sistema": a.get("sistema"), "campos_personales": campos, "total_campos": len(a.get("campos", [])),
               "finalidad": _declared(ctx, "finalidad"), "titulares": _declared(ctx, "titulares"), "responsable": _declared(ctx, "responsable"),
               "base_juridica": _declared(ctx, "base_juridica"), "retencion": _declared(ctx, "retencion"),
               "almacenamiento": _declared(ctx, "almacenamiento"), "transferencias": _declared(ctx, "transferencias"),
               "validado_por_persona": not a.get("requiere_validacion", True)}
    q = ("Necesito una evaluación de riesgos de privacidad (ISO/IEC 27701:2025, cláusula 6.1.2) de este sistema de información "
         "de una universidad. Solo conozco los NOMBRES de los campos, no sus valores.\n"
         f"- Sistema: {resumen['sistema']}\n- Campos de datos personales: {', '.join(campos)} (de {resumen['total_campos']} campos)\n"
         f"- Finalidad: {resumen['finalidad']}\n- Titulares: {resumen['titulares']}\n- Responsable: {resumen['responsable']}\n"
         f"- Base jurídica: {resumen['base_juridica']}; retención: {resumen['retencion']}; almacenamiento: {resumen['almacenamiento']}; "
         f"transferencias: {resumen['transferencias']}\n"
         "Lo que figura como «no declarado» es información que falta. Identifica los 5 riesgos de privacidad más relevantes, con "
         "probabilidad, impacto y nivel de cada uno, y propón un tratamiento. Indica qué información faltante cambiaría la evaluación.")
    chat = await _step("riesgos", "chat", {"message": q, "sessionId": f"flujo-{rid[:8]}-g6-g2"}, steps, wait=900)
    return {"activo": a.get("id"), "sistema_evaluado": resumen["sistema"], "enviado_a_g2": resumen,
            "evaluacion_g2": chat.get("answer") or chat.get("text") or chat.get("output"),
            "nota": "Evaluación propuesta por G2 a partir de nombres de campos y contexto declarado: la valida una persona. No se enviaron valores de datos."}


FLOWS = {"inventario_a_riesgos": inventario_a_riesgos, "inventario_a_auditoria": inventario_a_auditoria, "dsar_handoffs": dsar_handoffs, "terceros_a_controles": terceros_a_controles,
         "incidente_a_formacion": incidente_a_formacion}
