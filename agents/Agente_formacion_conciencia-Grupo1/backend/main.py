import json
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

from config import JWT_EXPIRATION_HOURS
from db import get_db_connection, init_schema, registrar_audit
from auth import verify_password, create_access_token, get_current_user
from agente import pims_agent_graph
from actions import (
    obtener_accion_pendiente,
    eliminar_accion_pendiente,
    ejecutar_accion_preparada,
    is_approval_text,
    check_approval_semantic
)

# Inicialización de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main")

# Inicializar esquema de Base de Datos al arrancar
init_schema()

app = FastAPI(
    title="PIMS UNSA - Agente #8 Formación y Conciencia",
    description="API Gateway y Backend para Sistema de Gestión de Privacidad ISO 27701:2025 y Ley 29733",
    version="1.0.0"
)

# Habilitar CORS para integración con Frontend Vue 3
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# MODELOS PYDANTIC
# ==============================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatMessageRequest(BaseModel):
    conversacion_id: str
    mensaje: str

class NuevaConversacionRequest(BaseModel):
    titulo: Optional[str] = "Nueva consulta"

class ApproveRequest(BaseModel):
    conversacion_id: str
    action_id: str
    approved: bool

# ==============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# ==============================================================================

@app.post("/auth/login")
def login(req: LoginRequest):
    """
    Login de usuario (por defecto: admin / admin).
    Devuelve JWT de acceso con expiración de 8 horas.
    """
    with get_db_connection() as conn:
        # Búsqueda por email o por ID directo
        user = conn.execute(
            "SELECT * FROM usuarios WHERE (email = ? OR id = ?) AND activo = 1",
            (req.email, req.email)
        ).fetchone()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifique su usuario y contraseña."
        )

    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "rol": user["rol"],
        "facultad": user["facultad"],
        "departamento": user["departamento"],
        "nombre": user["nombre"]
    }
    token = create_access_token(token_data)

    registrar_audit(user["id"], "login", {"email": user["email"], "rol": user["rol"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "nombre": user["nombre"],
            "rol": user["rol"],
            "facultad": user["facultad"],
            "departamento": user["departamento"]
        }
    }

@app.get("/auth/me")
def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "nombre": user["nombre"],
        "rol": user["rol"],
        "facultad": user["facultad"],
        "departamento": user["departamento"]
    }

# ==============================================================================
# ENDPOINTS DE CONVERSACIONES Y CHAT
# ==============================================================================

@app.get("/chat/conversaciones")
def listar_conversaciones(user: dict = Depends(get_current_user)):
    """
    Devuelve la lista de conversaciones del usuario autenticado.
    """
    with get_db_connection() as conn:
        convs = conn.execute(
            "SELECT * FROM conversaciones WHERE user_id = ? ORDER BY updated_at DESC",
            (user["id"],)
        ).fetchall()
    return convs

@app.post("/chat/conversaciones")
def crear_conversacion(req: NuevaConversacionRequest, user: dict = Depends(get_current_user)):
    """
    Crea una nueva conversación independiente para el usuario.
    """
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO conversaciones (id, user_id, titulo, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (conv_id, user["id"], req.titulo or "Nueva consulta", now, now)
        )
    return {"id": conv_id, "titulo": req.titulo, "created_at": now, "updated_at": now}

@app.get("/chat/conversaciones/{conversacion_id}")
def obtener_conversacion(conversacion_id: str, user: dict = Depends(get_current_user)):
    """
    Carga todos los mensajes de una conversación histórica.
    """
    with get_db_connection() as conn:
        conv = conn.execute(
            "SELECT * FROM conversaciones WHERE id = ? AND user_id = ?",
            (conversacion_id, user["id"])
        ).fetchone()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        mensajes = conn.execute(
            "SELECT * FROM mensajes WHERE conversacion_id = ? ORDER BY id ASC",
            (conversacion_id,)
        ).fetchall()

    return {"conversacion": conv, "mensajes": mensajes}

# ==============================================================================
# CHAT PRINCIPAL CON STREAMING SSE & LANGGRAPH
# ==============================================================================

@app.post("/chat")
async def chat_endpoint(req: ChatMessageRequest, user: dict = Depends(get_current_user)):
    """
    Canal de chat con SSE Streaming.
    Orquesta LangGraph, valida entradas, clasifica intenciones y emite approval_required si aplica.
    """
    conversacion_id = req.conversacion_id
    user_msg_text = req.mensaje.strip()
    now = datetime.now().isoformat()

    # Guardar mensaje del usuario en SQLite
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO mensajes (conversacion_id, rol, contenido, created_at) VALUES (?, ?, ?, ?)",
            (conversacion_id, "user", user_msg_text, now)
        )
        conn.execute(
            "UPDATE conversaciones SET updated_at = ? WHERE id = ?",
            (now, conversacion_id)
        )

    async def event_generator():
        try:
            pending = obtener_accion_pendiente(conversacion_id)
            approval_choice = await check_approval_semantic(user_msg_text, pending_action=pending) if pending else None

            # 1. Caso: El usuario respondió con texto libre de confirmación ("sí", "ok", "confirmo", etc.)
            if pending and approval_choice is not None:
                if approval_choice is True:
                    yield f"event: token\ndata: {json.dumps({'content': '✅ Confirmación recibida. Ejecutando acción en el sistema...\\n\\n'})}\n\n"
                    resultado = await ejecutar_accion_preparada(pending, user_id=user["id"])
                    eliminar_accion_pendiente(conversacion_id)

                    respuesta_final = (
                        f"{resultado.get('mensaje', 'Acción completada.')}\n\n"
                        f"Operación registrada bajo la supervisión del control **A.3.17 de ISO/IEC 27701 (Formación y Conciencia)**."
                    )
                else:
                    eliminar_accion_pendiente(conversacion_id)
                    respuesta_final = "❌ Operación cancelada a solicitud del usuario. No se aplicó ningún cambio."

                yield f"event: token\ndata: {json.dumps({'content': respuesta_final})}\n\n"

                # Persistir respuesta del asistente en SQLite
                with get_db_connection() as conn:
                    conn.execute(
                        "INSERT INTO mensajes (conversacion_id, rol, contenido, created_at) VALUES (?, ?, ?, ?)",
                        (conversacion_id, "assistant", respuesta_final, datetime.now().isoformat())
                    )
                yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"
                return

            # Si había una acción pendiente pero el usuario NO respondió con confirmación
            # (hizo una nueva pregunta), se descarta la acción pendiente anterior.
            if pending and approval_choice is None:
                eliminar_accion_pendiente(conversacion_id)
                pending = None

            # 2. Caso normal: Ejecutar el grafo de LangGraph
            initial_state = {
                "messages": [HumanMessage(content=user_msg_text)],
                "user_id": user["id"],
                "user_rol": user["rol"],
                "user_facultad": user.get("facultad"),
                "conversacion_id": conversacion_id,
                "intent": "consulta_estado",
                "rag_context": [],
                "tool_name": None,
                "tool_args": None,
                "tool_result": None,
                "pending_action": None,
                "requires_approval": False,
                "approved": None
            }

            config = {"configurable": {"thread_id": conversacion_id}}

            # Ejecutar grafo
            final_output = await pims_agent_graph.ainvoke(initial_state, config=config)

            # Comprobar si quedó una acción pendiente que requiera aprobación humana de este turno
            if final_output.get("requires_approval") is True:
                action_pending = final_output.get("pending_action") or obtener_accion_pendiente(conversacion_id)
                if action_pending:
                    approval_payload = {
                        "action_id": action_pending.get("action_id"),
                        "tipo": action_pending.get("tipo"),
                        "preview": action_pending.get("preview", {})
                    }
                    yield f"event: approval_required\ndata: {json.dumps(approval_payload, ensure_ascii=False)}\n\n"
            else:
                eliminar_accion_pendiente(conversacion_id)

            # Transmitir mensaje final
            assistant_messages = [m for m in final_output.get("messages", []) if isinstance(m, AIMessage)]
            final_text = assistant_messages[-1].content if assistant_messages else "Consulta procesada con éxito."

            # Streaming de tokens al frontend
            for chunk in final_text.split(" "):
                yield f"event: token\ndata: {json.dumps({'content': chunk + ' '})}\n\n"

            # Persistir en SQLite
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO mensajes (conversacion_id, rol, contenido, created_at) VALUES (?, ?, ?, ?)",
                    (conversacion_id, "assistant", final_text, datetime.now().isoformat())
                )

            yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"

        except Exception as e:
            logger.error(f"Error procesando SSE Chat: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ==============================================================================
# ENDPOINT DE APROBACIÓN HUMANA (POST /chat/approve)
# ==============================================================================

@app.post("/chat/approve")
async def approve_endpoint(req: ApproveRequest, user: dict = Depends(get_current_user)):
    """
    Endpoint para reanudar el grafo tras confirmación por botón en la UI:
    {conversacion_id, action_id, approved: bool}
    Reanuda el grafo con Command(resume={'approved': req.approved}) o ejecuta directamente la acción.
    """
    conversacion_id = req.conversacion_id
    action_id = req.action_id
    approved = req.approved

    pending = obtener_accion_pendiente(conversacion_id)
    if not pending or pending.get("action_id") != action_id:
        # Intentar ejecutar con la que esté registrada si coincide
        if not pending:
            raise HTTPException(status_code=400, detail="No existe ninguna acción pendiente para esta conversación.")

    config = {"configurable": {"thread_id": conversacion_id}}

    try:
        if approved:
            resultado = await ejecutar_accion_preparada(pending, user_id=user["id"])
            response_text = resultado.get("mensaje", "Acción ejecutada con éxito.")
        else:
            response_text = "❌ Acción cancelada por el usuario. No se realizaron cambios."

        eliminar_accion_pendiente(conversacion_id)

        # Guardar en historial de chat
        now = datetime.now().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO mensajes (conversacion_id, rol, contenido, created_at) VALUES (?, ?, ?, ?)",
                (conversacion_id, "user", "Confirmar" if approved else "Cancelar", now)
            )
            conn.execute(
                "INSERT INTO mensajes (conversacion_id, rol, contenido, created_at) VALUES (?, ?, ?, ?)",
                (conversacion_id, "assistant", response_text, now)
            )

        return {
            "status": "success",
            "approved": approved,
            "response": response_text
        }

    except Exception as e:
        logger.error(f"Error procesando aprobación: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# ENDPOINTS DE ESTADO Y PANEL LATERAL
# ==============================================================================

@app.get("/dashboard/estado")
def obtener_estado_dashboard(user: dict = Depends(get_current_user)):
    """
    Datos de cumplimiento formativo del usuario y métricas institucionales (Control A.3.17).
    """
    user_id = user["id"]
    with get_db_connection() as conn:
        cursos = conn.execute(
            """
            SELECT fu.*, f.titulo, f.control_iso
            FROM formacion_usuario fu
            JOIN formaciones f ON fu.formacion_id = f.id
            WHERE fu.user_id = ?
            """,
            (user_id,)
        ).fetchall()

        total_f = len(cursos)
        completadas = [c for c in cursos if c["estado"] == "completado"]
        pendientes_f = [c for c in cursos if c["estado"] in ("pendiente", "en_curso")]
        vencidas_f = [c for c in cursos if c["estado"] == "vencido"]
        certificados = [c for c in cursos if c.get("certificado_url")]

        cumplimiento_pct = int((len(completadas) / total_f * 100)) if total_f > 0 else 100

        # Métricas adicionales si el usuario es Admin
        admin_metrics = {}
        if user["rol"] == "admin":
            total_usuarios = conn.execute("SELECT count(*) as count FROM usuarios WHERE activo = 1").fetchone()["count"]
            hoy = datetime.now().strftime("%Y-%m-%d")
            correos_hoy = conn.execute(
                "SELECT count(*) as count FROM correos_enviados WHERE enviado_at LIKE ?",
                (f"{hoy}%",)
            ).fetchone()["count"]
            formaciones_activas = conn.execute("SELECT count(*) as count FROM formaciones").fetchone()["count"]

            admin_metrics = {
                "total_usuarios": total_usuarios,
                "correos_enviados_hoy": correos_hoy,
                "formaciones_activas": formaciones_activas
            }

    return {
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "rol": user["rol"]
        },
        "cumplimiento_pct": cumplimiento_pct,
        "formaciones_pendientes": len(pendientes_f),
        "formaciones_vencidas": len(vencidas_f),
        "certificados_vigentes": len(certificados),
        "detalle_formaciones": cursos,
        "admin_metrics": admin_metrics
    }

@app.get("/admin/correos")
def listar_correos_admin(user: dict = Depends(get_current_user)):
    """
    Permite consultar los correos enviados en SQLite (para auditar flujos de correo masivo).
    """
    if user["rol"] not in ("admin", "jefe", "auditor"):
        raise HTTPException(status_code=403, detail="Acceso denegado")

    with get_db_connection() as conn:
        correos = conn.execute(
            "SELECT * FROM correos_enviados ORDER BY enviado_at DESC LIMIT 50"
        ).fetchall()
    return correos

# ==============================================================================
# ENDPOINTS DE MATRIZ DE BRECHAS (SKILL GAP ANALYSIS ISO 27701)
# ==============================================================================

@app.get("/dashboard/brechas")
async def obtener_matriz_brechas_endpoint(rol: Optional[str] = None, user: dict = Depends(get_current_user)):
    """
    Devuelve la Matriz de Brechas de Competencia por Rol (Skill Gap Analysis)
    conforme a ISO/IEC 27701:2025 Cláusula 7.2, 7.3, Control A.3.17 y Ley 29733.
    Incluye datos cuantitativos reales y el dictamen oficial del Agente Copiloto IA.
    """
    from brechas import obtener_o_generar_diagnostico_ia, calcular_matriz_brechas
    try:
        # Si se pide filtrar por un rol específico, se calcula filtrado
        if rol:
            return calcular_matriz_brechas(rol_filtro=rol)
        # Por defecto, devuelve la matriz global institucional con el dictamen de la IA
        data = await obtener_o_generar_diagnostico_ia(force_refresh=False, solicitante_id=user["id"])
        return data
    except Exception as e:
        logger.error(f"Error obteniendo matriz de brechas: {e}", exc_info=True)
        # Fallback seguro con cálculo matemático directo
        return calcular_matriz_brechas(rol_filtro=rol)

@app.post("/dashboard/brechas/diagnosticar")
async def forzar_diagnostico_brechas_ia(user: dict = Depends(get_current_user)):
    """
    Fuerza la ejecución en vivo del diagnóstico por parte del Agente #8 Copiloto IA
    y persiste la evaluación como evidencia documental exigida por ISO 27701 Cláusula 7.2.
    """
    from brechas import obtener_o_generar_diagnostico_ia
    try:
        data = await obtener_o_generar_diagnostico_ia(force_refresh=True, solicitante_id=user["id"])
        return data
    except Exception as e:
        logger.error(f"Error forzando diagnóstico IA de brechas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico IA: {str(e)}")

# ==============================================================================
# ENDPOINTS DE MAPA DE CALOR DE RIESGOS PII (HEATMAP ISO 27701)
# ==============================================================================

@app.get("/dashboard/heatmap")
async def obtener_mapa_calor_endpoint(facultad: Optional[str] = None, user: dict = Depends(get_current_user)):
    """
    Devuelve el Mapa de Calor (Heatmap) de Vulnerabilidad y Sensibilización sobre Riesgos PII
    conforme a ISO/IEC 27701:2025 Control A.3.17, Control A.3.11 y Ley 29733.
    """
    from heatmap import obtener_o_generar_diagnostico_ia_heatmap, calcular_mapa_calor
    try:
        if facultad:
            return calcular_mapa_calor(facultad_filtro=facultad)
        data = await obtener_o_generar_diagnostico_ia_heatmap(force_refresh=False, solicitante_id=user["id"])
        return data
    except Exception as e:
        logger.error(f"Error obteniendo mapa de calor: {e}", exc_info=True)
        return calcular_mapa_calor(facultad_filtro=facultad)

@app.post("/dashboard/heatmap/diagnosticar")
async def forzar_diagnostico_heatmap_ia(user: dict = Depends(get_current_user)):
    """
    Fuerza el diagnóstico termográfico en vivo con el Copiloto IA y guarda la evaluación
    en evaluaciones_control para trazabilidad y auditoría.
    """
    from heatmap import obtener_o_generar_diagnostico_ia_heatmap
    try:
        data = await obtener_o_generar_diagnostico_ia_heatmap(force_refresh=True, solicitante_id=user["id"])
        return data
    except Exception as e:
        logger.error(f"Error forzando diagnóstico IA de heatmap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico IA de heatmap: {str(e)}")

# ==============================================================================
# ENDPOINTS DE RADAR DE COBERTURA FORMATIVA (CONTROL A.3.17 & CLÁUSULA 7.2 ISO 27701)
# ==============================================================================

@app.get("/dashboard/radar")
async def obtener_radar_cobertura_endpoint(
    estamento: Optional[str] = None,
    facultad: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """
    Devuelve las métricas multiaxiales del Radar de Cobertura por Estamento Universitario
    (Control A.3.17 y Cláusula 7.2 ISO/IEC 27701:2025).
    """
    from radar import obtener_o_generar_diagnostico_ia_radar, calcular_radar_cobertura
    try:
        if estamento or facultad:
            return calcular_radar_cobertura(estamento_filtro=estamento, facultad_filtro=facultad)
        data = await obtener_o_generar_diagnostico_ia_radar(force_refresh=False, solicitante_id=user["id"])
        return data
    except Exception as e:
        logger.error(f"Error obteniendo radar de cobertura: {e}", exc_info=True)
        return calcular_radar_cobertura(estamento_filtro=estamento, facultad_filtro=facultad)

@app.post("/dashboard/radar/diagnosticar")
async def forzar_diagnostico_radar_ia(user: dict = Depends(get_current_user)):
    """
    Fuerza el diagnóstico multiaxial en vivo con el Copiloto IA y guarda la evaluación
    en evaluaciones_control para trazabilidad y auditoría PIMS.
    """
    from radar import obtener_o_generar_diagnostico_ia_radar
    try:
        data = await obtener_o_generar_diagnostico_ia_radar(force_refresh=True, solicitante_id=user["id"])
        return data
    except Exception as e:
        logger.error(f"Error forzando diagnóstico IA de radar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico IA de radar: {str(e)}")

# ==============================================================================
# ENDPOINTS DE FORMULARIOS GOOGLE FORMS Y CALENDARIO MOCK
# ==============================================================================

@app.get("/formularios")
async def listar_formularios_capacitacion(user: dict = Depends(get_current_user)):
    """
    Lista todos los formularios de evaluación interactiva creados.
    """
    with get_db_connection() as conn:
        forms = conn.execute("SELECT * FROM formularios_capacitacion ORDER BY created_at DESC").fetchall()
        for f in forms:
            f["preguntas"] = json.loads(f["preguntas_json"]) if f.get("preguntas_json") else []
            f["destinatarios"] = json.loads(f["destinatarios_json"]) if f.get("destinatarios_json") else []
    return {"status": "success", "total": len(forms), "formularios": forms}

@app.get("/eventos/calendario")
async def listar_eventos_calendario(user: dict = Depends(get_current_user)):
    """
    Lista los eventos y recordatorios de capacitación agendados en el calendario institucional.
    """
    with get_db_connection() as conn:
        eventos = conn.execute("SELECT * FROM eventos_calendario ORDER BY fecha_inicio ASC").fetchall()
        for ev in eventos:
            ev["asistentes"] = json.loads(ev["asistentes_json"]) if ev.get("asistentes_json") else []
    return {"status": "success", "total": len(eventos), "eventos": eventos}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

