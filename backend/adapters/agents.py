"""One adapter per agent. Each translates platform requests to the agent's NATIVE API and back.
Adapters never reimplement skills and report only capabilities that really exist."""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import httpx

from shared.contracts.agent_contract import (CAIDO, DEGRADADO, FUERA_DE_ALCANCE, OPERATIVO,
                                             AgentAdapter, ExecutionRequest)

GATEWAY = os.getenv("GATEWAY_URL", "http://llm-gateway:8080")
TIMEOUT = float(os.getenv("AGENT_TIMEOUT_SECONDS", "600"))


async def _get(url: str, **kw) -> httpx.Response:
    async with httpx.AsyncClient(timeout=kw.pop("timeout", 5)) as c:
        return await c.get(url, **kw)


async def _post(url: str, **kw) -> httpx.Response:
    async with httpx.AsyncClient(timeout=kw.pop("timeout", TIMEOUT)) as c:
        return await c.post(url, **kw)


def _down(e: Exception) -> dict:
    return {"status": CAIDO, "reason": f"No responde ({type(e).__name__})", "detail": {}}


class _HttpAdapter(AgentAdapter):
    url_env = ""
    default_url = ""
    health_path = "/"

    @property
    def base(self) -> str:
        return os.getenv(self.url_env, self.default_url).rstrip("/")

    async def health_check(self) -> dict:
        try:
            r = await _get(self.base + self.health_path)
            if r.status_code < 400:
                return {"status": OPERATIVO, "reason": None, "detail": {}}
            return {"status": DEGRADADO, "reason": f"HTTP {r.status_code}", "detail": {}}
        except Exception as e:  # noqa: BLE001
            return _down(e)


# ---------------------------------------------------------------- Group 1
class G1(_HttpAdapter):
    id, group, route = "formacion", 1, "/agentes/formacion"
    name = "Formación y concientización"
    responsibility = "Capacitación, evaluaciones e indicadores de concientización"
    url_env, default_url, health_path = "AGENT_G1_URL", "http://agent-g1:8000", "/openapi.json"

    def get_capabilities(self):
        return [{"action": "chat", "description": "Consulta al asistente de formación (SSE nativo /chat)",
                 "input": {"mensaje": "str"}}]

    async def execute(self, req: ExecutionRequest):
        # Native auth: the agent ships a default account; credentials come from env.
        cred = {"email": os.getenv("G1_USER", "admin"), "password": os.getenv("G1_PASSWORD", "admin")}
        tok = (await _post(f"{self.base}/auth/login", json=cred, timeout=30)).json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        conv = (await _post(f"{self.base}/chat/conversaciones", json={"titulo": "Plataforma"}, headers=h,
                            timeout=30)).json()["id"]
        text, events = "", []
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            async with c.stream("POST", f"{self.base}/chat", headers=h,
                                json={"conversacion_id": conv, "mensaje": req["input"]["mensaje"]}) as r:
                ev = ""
                async for line in r.aiter_lines():
                    if line.startswith("event:"):
                        ev = line[6:].strip()
                    elif line.startswith("data:"):
                        d = json.loads(line[5:])
                        events.append(ev)
                        if ev == "token":
                            text += d.get("content", "")
                        elif ev in ("approval_required", "error"):
                            return {"output": {"text": text, "pending_human_approval": d if ev != "error" else None,
                                               "error": d if ev == "error" else None}, "native_status": r.status_code}
        return {"output": {"text": text, "events": sorted(set(events))}, "native_status": r.status_code}


# ---------------------------------------------------------------- Group 2
class G2(_HttpAdapter):
    id, group, route = "riesgos", 2, "/agentes/riesgos"
    name = "Evaluación de riesgos"
    responsibility = "Identificación de riesgos, impacto y mitigación (ISO/IEC 27701)"
    url_env, default_url, health_path = "AGENT_G2_URL", "http://agent-g2:4318", "/api/status"

    def get_capabilities(self):
        return [{"action": "chat", "description": "Consulta al agente de riesgos vía Express → n8n Chat Trigger",
                 "input": {"message": "str", "sessionId": "str (8-100 chars)"}}]

    async def health_check(self):
        try:
            r = await _get(self.base + self.health_path)
            s = r.json()
            reasons = []
            scope = s.get("scope") or {}
            if scope and not scope.get("enabled", True):
                reasons.append(f"alcance bloqueado por el propio agente ({scope.get('state')}): SCOPE_N8N_REVIEWED=false")
            if not s.get("configured"):
                reasons.append("N8N_CHAT_URL no configurada / Chat Trigger no publicado")
            if not await self._qdrant_points():
                reasons.append("norma ISO/IEC 27701:2025 no ingestada en Qdrant (RAG vacío)")
            return {"status": DEGRADADO if reasons else OPERATIVO, "reason": "; ".join(reasons) or None,
                    "detail": {"native": {k: s.get(k) for k in ("configured", "service")}}}
        except Exception as e:  # noqa: BLE001
            return _down(e)

    async def _qdrant_points(self) -> int:
        try:
            r = await _get("http://qdrant:6333/collections/iso27701_2025",
                           headers={"api-key": os.getenv("QDRANT_API_KEY", "")})
            return r.json()["result"]["points_count"] if r.status_code == 200 else 0
        except Exception:  # noqa: BLE001
            return 0

    async def execute(self, req: ExecutionRequest):
        i = req["input"]
        r = await _post(f"{self.base}/api/chat", json={"message": i["message"], "webMode": "off",
                                                      "sessionId": i.get("sessionId", "plataforma-0001")})
        if r.status_code >= 400:
            raise RuntimeError(f"G2 HTTP {r.status_code}: {r.text[:300]}")
        return {"output": r.json(), "native_status": r.status_code}


# ---------------------------------------------------------------- Group 3 (MCP over HTTP)
class G3(AgentAdapter):
    id, group, route = "dsar", 3, "/agentes/dsar"
    name = "Derechos de titulares (DSAR)"
    responsibility = "Registro, plazos y borradores de respuesta a solicitudes de derechos"
    # Model-callable tools only. verify_identity / decide are NOT here by design (human-only).
    TOOLS = {"dsar_crear_caso", "dsar_estado", "dsar_plazos", "dsar_calcular_plazos", "dsar_listar",
             "dsar_borrador", "dsar_consultar_norma", "dsar_handoffs"}

    @property
    def url(self):
        return os.getenv("AGENT_G3_URL", "http://agent-g3:8001/mcp")

    def get_capabilities(self):
        return [{"action": t, "description": "Herramienta MCP nativa", "input": "ver GUIA_INTEGRACION"}
                for t in sorted(self.TOOLS)]

    async def _call(self, tool: str | None, args: dict | None = None):
        try:
            return await self._call_raw(tool, args)
        except BaseExceptionGroup as eg:  # surface the real cause, not the TaskGroup wrapper
            raise eg.exceptions[0]

    async def _call_raw(self, tool: str | None, args: dict | None = None):
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
        async with streamablehttp_client(self.url) as (rd, wr, _):
            async with ClientSession(rd, wr) as s:
                await s.initialize()
                if tool is None:
                    return [t.name for t in (await s.list_tools()).tools]
                res = await s.call_tool(tool, args or {})
                blocks = [getattr(c, "text", "") for c in res.content]
                if getattr(res, "isError", False):
                    raise RuntimeError(f"G3 tool error: {''.join(blocks)[:300]}")

                def parse(t):
                    try:
                        return json.loads(t)
                    except ValueError:
                        return t
                # One content block per item (e.g. one envelope per handoff): keep them separate
                return parse(blocks[0]) if len(blocks) == 1 else [parse(b) for b in blocks]

    async def health_check(self):
        try:
            names = await asyncio.wait_for(self._call(None), 8)
            missing = self.TOOLS - set(names)
            exposed = {n for n in names if n in ("verify_identity", "decide", "dsar_aprobar", "dsar_decidir")}
            if exposed:
                return {"status": DEGRADADO, "reason": f"herramientas de decisión humana expuestas a modelos: {sorted(exposed)}",
                        "detail": {}}
            return {"status": DEGRADADO if missing else OPERATIVO,
                    "reason": f"faltan herramientas: {sorted(missing)}" if missing else None,
                    "detail": {"tools": len(names)}}
        except Exception as e:  # noqa: BLE001
            return _down(e)

    async def execute(self, req: ExecutionRequest):
        tool = req["action"]
        if tool not in self.TOOLS:
            raise PermissionError(f"Acción no permitida para G3: {tool}")
        return {"output": await self._call(tool, req.get("input")), "native_status": None}


# ---------------------------------------------------------------- Group 4
class G4(_HttpAdapter):
    id, group, route = "auditoria", 4, "/agentes/auditoria"
    name = "Evidencia y auditoría"
    responsibility = "Evaluación de evidencias, verificación de cumplimiento y dictamen propuesto"
    url_env, default_url, health_path = "AGENT_G4_URL", "http://agent-g4:8004", "/api/status"

    def get_capabilities(self):
        return [{"action": "planificar", "description": "M1: checklist de evidencias según rol y alcance", "input": {"rol": "str", "alcance": "str"}},
                {"action": "consolidar", "description": "M3: consolidar evaluaciones M2 persistidas", "input": {"execution_ids": "list[str]"}},
                {"action": "auditar", "description": "POST /api/auditar (M2: evaluar evidencia)",
                 "input": {"nombre_archivo": "str", "contenido": "str"}},
                {"action": "hash", "description": "SHA-256 del texto", "input": {"contenido": "str"}}]

    async def execute(self, req: ExecutionRequest):
        i = req["input"]
        if req["action"] == "consolidar":
            from backend.services.audit_modes import consolidate
            out = consolidate(i.get("execution_ids"))
            return {"output": out, "simulated": any(x["simulado"] for x in out["filas"])}
        if req["action"] == "planificar":
            r = await _post(f"{self.base}/api/planificar", json=i)
            r.raise_for_status()
            return {"output": r.json(), "native_status": r.status_code}
        if req["action"] == "hash":
            r = await _post(f"{self.base}/api/hash", data={"contenido": i["contenido"],
                            "nombre_archivo": i.get("nombre_archivo", "evidencia.txt")}, timeout=30)
            return {"output": r.json(), "native_status": r.status_code}
        # The agent selects its provider per request: point its 'ollama' branch at the shared gateway.
        body = {"nombre_archivo": i.get("nombre_archivo", "evidencia.txt"), "contenido": i["contenido"],
                "proveedor": "ollama", "modelo": os.getenv("LLM_MODEL", "gateway"),
                "url_base": f"{GATEWAY}/v1"}
        r = await _post(f"{self.base}/api/auditar", json=body)
        if r.status_code >= 400:
            raise RuntimeError(f"G4 HTTP {r.status_code}: {r.text[:300]}")
        out = r.json()
        out["nombre_archivo"] = body["nombre_archivo"]
        out["estado_revision"] = "Pendiente de validación humana"
        # The label "Ollama Local GPU" is fixed text in the agent; do not present it as the real provider.
        fallback = "Contingencia" in out.get("proveedor_usado", "")
        out["proveedor_usado"] = "Motor de contingencia (sin LLM)" if fallback else f"Gateway LLM compartido ({os.getenv('LLM_MODE', 'cloud')})"
        out["motor_contingencia"] = fallback
        return {"output": out, "native_status": r.status_code,
                "simulated": os.getenv("LLM_MODE") == "mock"}


# ---------------------------------------------------------------- Group 5 (n8n)
class G5(_HttpAdapter):
    id, group, route = "terceros", 5, "/agentes/terceros"
    name = "Terceros y DPA"
    responsibility = "Auditoría de contratos de encargo de tratamiento contra ISO/IEC 27701 y Ley 29733"
    url_env, default_url, health_path = "AGENT_G5_URL", "http://agent-g5:5678", "/webhook/pims/estado"

    def get_capabilities(self):
        return [{"action": "auditar", "description": "POST pims/auditar (asíncrono, 2-5 min)",
                 "input": {"organizacion": "str", "contrato_texto": "str"}},
                {"action": "trabajo", "description": "GET pims/trabajo?id=", "input": {"id": "str"}},
                {"action": "registro", "description": "GET pims/registro?organizacion=", "input": {"organizacion": "str"}},
                {"action": "organizaciones", "description": "GET pims/organizaciones", "input": {}}]
    # pims/aprobar (DPO/Legal) is a human action: exposed by the backend with human auth, never as model tool.

    async def execute(self, req: ExecutionRequest):
        a, i = req["action"], req.get("input") or {}
        w = f"{self.base}/webhook/pims"
        if a == "auditar":
            r = await _post(f"{w}/auditar", json=i, timeout=60)
            job = r.json()
            jid = job.get("trabajo") or job.get("id")
            for _ in range(int(TIMEOUT // 5)):          # real polling; no fabricated progress
                await asyncio.sleep(5)
                st = (await _get(f"{w}/trabajo", params={"id": jid if isinstance(jid, str) else jid.get("id")},
                                 timeout=15)).json()
                if st.get("estado") in ("terminado", "listo", "error", "fallido") or st.get("dictamen"):
                    return {"output": st, "native_status": 200}
            raise TimeoutError("G5: el trabajo no terminó a tiempo")
        if a in ("trabajo", "registro", "organizaciones"):
            r = await _get(f"{w}/{a}", params=i, timeout=30)
            return {"output": r.json(), "native_status": r.status_code}
        raise PermissionError(f"Acción no soportada para G5: {a}")


# ---------------------------------------------------------------- Group 6 (out of scope)
class G6(AgentAdapter):
    id, group, route = "inventario", 6, "/agentes/inventario"
    name = "Inventario de datos"
    responsibility = "Activos de datos, clasificación y registro de tratamientos"

    def get_capabilities(self):
        return []

    async def health_check(self):
        return {"status": FUERA_DE_ALCANCE, "detail": {},
                "reason": "Fuera del alcance de esta entrega: herramienta HTML del lado del cliente, "
                          "basada en reglas, sin backend ni modelo."}

    async def execute(self, req):
        raise NotImplementedError("Grupo 6 fuera de alcance en esta entrega")


# ---------------------------------------------------------------- Group 7
class G7(_HttpAdapter):
    id, group, route = "controles", 7, "/agentes/controles"
    name = "Controles y SoA"
    responsibility = "Controles de seguridad, aplicabilidad e implementación (SoA)"
    url_env, default_url, health_path = "AGENT_G7_URL", "http://agent-g7:5007", "/api/controles/catalogo"

    def get_capabilities(self):
        return [{"action": "catalogo", "description": "GET /api/controles/catalogo", "input": {}},
                {"action": "ejecutar", "description": "POST /api/controles/ejecutar (skills generar-soa / verificar-controles)",
                 "input": "payload nativo del agente"}]

    async def execute(self, req: ExecutionRequest):
        if req["action"] == "catalogo":
            r = await _get(f"{self.base}{self.health_path}", timeout=30)
        else:
            r = await _post(f"{self.base}/api/controles/ejecutar", json=req.get("input") or {})
        if r.status_code >= 400:
            raise RuntimeError(f"G7 HTTP {r.status_code}: {r.text[:300]}")
        return {"output": r.json(), "native_status": r.status_code}


# ---------------------------------------------------------------- Group 8
class G8(_HttpAdapter):
    id, group, route = "incidentes", 8, "/agentes/incidentes"
    name = "Incidentes y brechas"
    responsibility = "Clasificación, severidad, plazo de 48 h y borradores de notificación"
    url_env, default_url, health_path = "AGENT_G8_URL", "http://agent-g8:3100", "/api/estado"

    def get_capabilities(self):
        return [{"action": "analizar", "description": "POST /api/analizar → job → expediente (solo borradores)",
                 "input": {"reporte": "str (>=20 chars)", "contexto": "str?"}}]
    # Approving/rejecting proposed actions (POST /api/acciones/...) is a human decision, not a model tool.

    async def execute(self, req: ExecutionRequest):
        r = await _post(f"{self.base}/api/analizar", json=req["input"], timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"G8 HTTP {r.status_code}: {r.text[:300]}")
        job = r.json()["job"]
        for _ in range(int(TIMEOUT // 3)):
            st = (await _get(f"{self.base}/api/job/{job}", timeout=15)).json()
            if st.get("status") not in ("running", "queued", None):   # native job fields: status/eventos/resultado/error
                return {"output": st, "native_status": 200}
            await asyncio.sleep(3)
        raise TimeoutError("G8: el análisis no terminó a tiempo")


ADAPTERS: dict[str, AgentAdapter] = {a.id: a for a in (G1(), G2(), G3(), G4(), G5(), G6(), G7(), G8())}
