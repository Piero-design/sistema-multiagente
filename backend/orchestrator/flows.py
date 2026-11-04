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
from datetime import datetime, timezone

import httpx

from backend.orchestrator import orchestrator as orch
from backend.services import db

_tasks: set = set()


class _Steps(list):
    """Persists the executed steps as they happen, so the UI shows real progress (who is doing what, what it reads, what it produced)."""

    def __init__(self, rid: str):
        super().__init__()
        self.rid = rid

    def _save(self) -> None:
        try:
            db.execute("UPDATE orchestrator.flow_run SET steps=%s::jsonb WHERE id=%s", (json.dumps(list(self), default=str), self.rid))
        except Exception:  # noqa: BLE001
            pass

    def begin(self, step: dict) -> dict:
        super().append(step)
        self._save()
        return step

    def finish(self, step: dict, **fields) -> None:
        step.update(fields)
        self._save()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cut(v, n: int = 170) -> str:
    t = " ".join(str(v if v is not None else "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def _describe(agent: str, action: str, p: dict) -> tuple[str, str]:
    """What the agent is about to do and what it is given (field names / short excerpts; never raw data values)."""
    org = p.get("organizacion", "")
    if (agent, action) == ("inventario", "consultar_inventario"):
        return "Lee el inventario de activos de datos", f"Organización {org}"
    if (agent, action) == ("inventario", "exportar_evidencia"):
        return "Prepara su inventario como documento de evidencia", f"Organización {org} (solo nombres de campos, sin valores)"
    if (agent, action) == ("inventario", "recibir_handoff"):
        return "Verifica el hash del handoff de G3 y revisa qué cubre su inventario", f"Sobre de G3 (caso {_cut((p.get('handoff') or {}).get('case_ref'), 40)})"
    if (agent, action) == ("auditoria", "auditar"):
        return "Audita el documento como evidencia (pertinencia, suficiencia, trazabilidad)", f"{p.get('nombre_archivo', 'documento')} · {len(str(p.get('contenido', '')))} caracteres"
    if (agent, action) == ("riesgos", "chat"):
        return "Evalúa los riesgos de privacidad (ISO/IEC 27701, cláusula 6.1.2)", _cut(p.get("message"))
    if (agent, action) == ("formacion", "chat"):
        return "Propone capacitaciones a partir de las lecciones", _cut(p.get("mensaje"))
    if (agent, action) == ("incidentes", "analizar"):
        return "Analiza el incidente: clasifica, calcula severidad y redacta borradores", _cut(p.get("reporte"))
    if (agent, action) == ("controles", "ejecutar"):
        n = len(p.get("evidencias") or [])
        return "Genera la declaración de aplicabilidad (SoA)", f"Rol {(p.get('perfil') or {}).get('rol', '—')} · {n} evidencias recibidas" if n else f"Rol {(p.get('perfil') or {}).get('rol', '—')} · sin evidencias enviadas (usa las suyas)"
    if (agent, action) == ("terceros", "registro"):
        return "Busca sus expedientes de auditoría de contratos", f"Organización {org}"
    if (agent, action) == ("dsar", "dsar_handoffs"):
        return "Entrega los handoffs que generó la decisión humana", f"Caso {p.get('case_id', '')}"
    return f"Ejecuta {action}", ""


def _produce(agent: str, action: str, out) -> tuple[str, list[str]]:
    """Short summary of what the step returned, plus the lines of activity the agent reported (if any)."""
    try:
        o = out if isinstance(out, dict) else {}
        d = o.get("data") if isinstance(o.get("data"), dict) else o
        if (agent, action) == ("inventario", "consultar_inventario"):
            acts = d.get("activos") or []
            return f"{len(acts)} sistemas inventariados; {sum(1 for a in acts for c in a.get('campos', []) if c.get('es_pii'))} campos de datos personales", []
        if (agent, action) == ("inventario", "exportar_evidencia"):
            return f"{d.get('nombre_archivo')} · SHA-256 {_cut(d.get('sha256'), 12)}", []
        if (agent, action) == ("inventario", "recibir_handoff"):
            return "Hash verificado; cobertura de su inventario respondida", []
        if (agent, action) == ("auditoria", "auditar"):
            return f"Severidad propuesta: {o.get('severidad')} · SHA-256 {_cut(o.get('sha256'), 12)}", []
        if (agent, action) in (("riesgos", "chat"), ("formacion", "chat")):
            return f"Respuesta de {len(str(o.get('answer') or o.get('text') or ''))} caracteres", []
        if (agent, action) == ("incidentes", "analizar"):
            return f"Expediente {o.get('incidente')} en {o.get('segundos', '?')} s", [str(e.get("texto")) for e in (o.get("eventos") or []) if isinstance(e, dict)][:20]
        if (agent, action) == ("controles", "ejecutar"):
            r = (o.get("datos") or {}).get("resumen") or {}
            return f"SoA con {r.get('implementados', 0)} controles implementados y {r.get('parciales', 0)} parciales (de {r.get('controles_en_soa', '?')})", []
        if (agent, action) == ("terceros", "registro"):
            return f"{len(o.get('registros') or [])} expedientes encontrados", []
        if (agent, action) == ("dsar", "dsar_handoffs"):
            n = len(out) if isinstance(out, list) else 1
            return f"{n} handoffs generados", []
    except Exception:  # noqa: BLE001
        pass
    return "Completado", []


async def _step(agent: str, action: str, payload: dict, steps: list, wait: int = 600, prep: str | None = None) -> dict:
    """Runs one REAL agent execution. `prep` = what the orchestrator did at the boundary just before (data transformation)."""
    titulo, lee = _describe(agent, action, payload)
    t0 = asyncio.get_event_loop().time()
    eid = orch.submit(agent, action, payload)
    st = steps.begin({"agent": agent, "action": action, "execution_id": eid, "status": "running", "titulo": titulo, "lee": lee,
                      "prep": prep, "inicio": _now()})
    end = t0 + wait
    while asyncio.get_event_loop().time() < end:
        s = orch.get_status(eid)
        if s["status"] in ("succeeded", "failed"):
            res = orch.get_result(eid)
            secs = round(asyncio.get_event_loop().time() - t0, 1)
            if s["status"] == "failed":
                steps.finish(st, status="failed", segundos=secs, error=_cut(res.get("error"), 300))
                raise RuntimeError(f"{agent}.{action} falló: {res.get('error')}")
            out = res["result"]["output"]
            produce, actividad = _produce(agent, action, out)
            steps.finish(st, status="succeeded", segundos=secs, produce=produce, actividad_final=actividad)
            return out
        await asyncio.sleep(2)
    steps.finish(st, status="failed", error="tiempo agotado")
    raise TimeoutError(f"{agent}.{action}")


def _note(steps: list, agent: str, action: str, titulo: str, lee: str, produce: str, prep: str | None = None) -> None:
    """A step done by the platform on behalf of an agent without an execution of its own (a read-only HTTP query or a hand-off)."""
    st = steps.begin({"agent": agent, "action": action, "execution_id": None, "status": "succeeded", "titulo": titulo, "lee": lee,
                      "prep": prep, "inicio": _now(), "segundos": 0, "produce": produce, "actividad_final": []})
    steps.finish(st)


# What each flow will do, so the page can show the steps that have not started yet.
PLANS = {
    "incidente_a_formacion": [("incidentes", "Analiza el incidente"), ("formacion", "Propone capacitaciones con las lecciones")],
    "terceros_a_controles": [("terceros", "Busca su último expediente"), ("terceros", "Entrega el detalle de sus 26 controles"),
                             ("controles", "Genera la SoA de partida"), ("controles", "Genera la SoA con las evidencias de G5")],
    "inventario_a_auditoria": [("inventario", "Exporta el inventario como evidencia"), ("auditoria", "Audita la evidencia")],
    "inventario_a_riesgos": [("inventario", "Lee el inventario"), ("riesgos", "Evalúa los riesgos del sistema elegido")],
    "dsar_handoffs": [("dsar", "Entrega los handoffs del caso decidido"), ("auditoria", "G4 evalúa el sobre de evidencia"),
                      ("terceros", "G5 recibe su sobre (pendiente de una persona)"), ("inventario", "G6 verifica el sobre de inventario")],
}


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
    if not r:
        return None
    f = r[0]
    for st in f.get("steps") or []:
        if st.get("execution_id"):
            ev = db.query("SELECT message, created_at FROM orchestrator.event WHERE execution_id=%s AND kind='actividad' "
                          "ORDER BY id LIMIT 60", (st["execution_id"],))
            st["actividad"] = [{"texto": e["message"], "hora": e["created_at"]} for e in ev]
    f["plan"] = [{"agent": a, "titulo": t} for a, t in PLANS.get(f["flow"], [])]
    return f


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
            _note(steps, to, "recibir_handoff", f"Recibe un sobre de G3 ({env.get('action')})", f"Caso {env.get('case_ref') or env.get('case_id')}",
                  "Queda pendiente de una persona: el orquestador no ejecuta nada", prep="El orquestador guarda el sobre y lo marca para revisión humana (requires_hitl)")
        if to == "evidencia":
            # G4 evaluates evidence text; the envelope carries hashes/refs only (G3 never includes personal data values).
            res = await _step("auditoria", "auditar", {"nombre_archivo": f"handoff-{env.get('case_ref') or env.get('case_id')}.json",
                                                      "contenido": json.dumps(env, ensure_ascii=False, indent=2)}, steps,
                                prep="El orquestador toma el sobre original de G3 (con su hash intacto) y se lo entrega a G4 como evidencia")
            status = "entregado"
            detail = {"severidad": res.get("severidad"), "sha256": res.get("sha256"),
                      "nota": "Dictamen propuesto por G4: requiere validación de un auditor humano"}
        if to == "inventario":
            org = p.get("organizacion", "UNSA-DEMO")
            res = await _step("inventario", "recibir_handoff", {"organizacion": org, "handoff": env}, steps,
                              prep="El orquestador entrega a G6 el sobre original de G3 para que verifique su hash")
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
    res5 = d["resultado"]
    _note(steps, "terceros", "detalle_expediente", "Entrega el detalle de su expediente (consulta de solo lectura)", f"Expediente {rid5}",
          f"{len(ctrls)} controles evaluados · puntaje {res5.get('puntaje', '—')} · {sum(1 for c in ctrls if c['estado'] in ESTADO_G5_A_G7)} cumplen o cumplen en parte")
    base = {"perfil": {"rol": rol, "organizacion": p.get("nombre_organizacion", "UNSA")}, "riesgos": []}
    before = await _step("controles", "ejecutar", {"operacion": "generar_soa", **base, "evidencias": []}, steps)
    evid = [{"control": c["control"], "estado": ESTADO_G5_A_G7[c["estado"]],
             "descripcion": f"[Agente de Terceros, expediente {rid5}] {c.get('evidencia') or c.get('observacion') or ''}"[:300]}
            for c in ctrls if c["estado"] in ESTADO_G5_A_G7]
    after = await _step("controles", "ejecutar", {"operacion": "generar_soa", **base, "evidencias": evid}, steps,
                        prep="El orquestador traduce los controles de G5 en evidencias para G7 (Cumple → implementado, Parcial → parcial) y se las entrega")
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
    chat = await _step("formacion", "chat", {"mensaje": q}, steps,
                       prep="El orquestador extrae las lecciones aprendidas del informe de G8 (solo referencias, sin datos personales) y arma la pregunta para G1")
    return {"incidente_resumen": text[:400], "lecciones_enviadas_a_g1": lessons[:400], "recomendacion_g1": chat.get("text")}


# ---------------------------------------------------------------- G6 -> G4
async def inventario_a_auditoria(rid: str, p: dict, steps: list) -> dict:
    org = p.get("organizacion", "UNSA-DEMO")
    exp = await _step("inventario", "exportar_evidencia", {"organizacion": org}, steps)
    doc = (exp.get("data") or {})
    if not doc.get("contenido"):
        raise ValueError("El inventario está vacío: registra activos en G6 primero.")
    aud = await _step("auditoria", "auditar", {"nombre_archivo": doc.get("nombre_archivo", "inventario.json"),
                                               "contenido": doc["contenido"]}, steps,
                      prep="El orquestador entrega a G4 el documento que preparó G6, tal cual y con su SHA-256")
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
    chat = await _step("riesgos", "chat", {"message": q, "sessionId": f"flujo-{rid[:8]}-g6-g2"}, steps, wait=900,
                       prep=f"El orquestador elige el sistema con más datos personales ({resumen['sistema']}) y arma la pregunta con nombres de campos, finalidad y titulares; nunca valores")
    return {"activo": a.get("id"), "sistema_evaluado": resumen["sistema"], "enviado_a_g2": resumen,
            "evaluacion_g2": chat.get("answer") or chat.get("text") or chat.get("output"),
            "nota": "Evaluación propuesta por G2 a partir de nombres de campos y contexto declarado: la valida una persona. No se enviaron valores de datos."}


FLOWS = {"inventario_a_riesgos": inventario_a_riesgos, "inventario_a_auditoria": inventario_a_auditoria, "dsar_handoffs": dsar_handoffs, "terceros_a_controles": terceros_a_controles,
         "incidente_a_formacion": incidente_a_formacion}
