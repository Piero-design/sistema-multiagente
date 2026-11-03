import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from db import get_db_connection, registrar_audit
from mcp_client import MCPClient

logger = logging.getLogger("actions")

def is_approval_text(text: str) -> Optional[bool]:
    """
    Detecta si un mensaje de texto libre representa una confirmación o cancelación directa de acción.
    Si el mensaje es una frase larga o da una nueva instrucción (destinatarios, horas, fechas), devuelve None.
    """
    t = text.strip().lower()
    palabras = t.split()
    
    # Si tiene más de 4 palabras, probablemente es una orden con detalles o una pregunta
    if len(palabras) > 4:
        return None

    afirmaciones = {
        "si", "sí", "ok", "dale", "confirmo", "confirmar", "confirmado", "confirmacion", "confirmación",
        "adelante", "procede", "proceder", "afirmativo", "ejecutar", "ejecuta",
        "hazlo", "de acuerdo", "acepto", "correcto", "dale con fe", "mándalo ya", "mandalo ya",
        "mándalo", "mandalo", "de una", "dale de una"
    }
    negaciones = {
        "no", "cancelar", "cancela", "cancelado", "cancelacion", "cancelación", "rechazar", "rechazo",
        "rechazado", "abortar", "detener", "para", "parar", "no enviar", "no quiero", "déjalo", "dejalo",
        "no lo hagas", "espera", "espera no"
    }

    if t in afirmaciones:
        return True
    if t in negaciones:
        return False

    return None

async def check_approval_semantic(text: str, pending_action: Optional[Dict[str, Any]] = None) -> Optional[bool]:
    """
    Evaluación semántica flexible:
    Primero comprueba expresiones directas breves. Si no coincide y existe una acción pendiente,
    utiliza el LLM para discernir si el usuario confirma la acción pendiente, la cancela,
    o está dando una NUEVA orden / instrucción diferente.
    """
    quick = is_approval_text(text)
    if quick is not None:
        return quick

    if not pending_action:
        return None

    try:
        from llm_service import LLMService
        tipo = pending_action.get("tipo", "acción")
        prev = pending_action.get("preview", {})
        resumen_prev = f"Tipo: {tipo}, Destinatarios: {prev.get('destinatarios') or prev.get('total')}, Asunto/Curso: {prev.get('asunto') or prev.get('curso')}"

        prompt = [
            {
                "role": "user",
                "content": (
                    f"El sistema tiene una acción PREPARADA en espera de confirmación:\n"
                    f"[{resumen_prev}]\n\n"
                    f"El usuario acaba de enviar el siguiente mensaje:\n"
                    f"\"{text}\"\n\n"
                    f"Determina cuál es la intención del usuario con respecto a la acción pendiente:\n"
                    f"- 'APROBADO': El usuario autoriza o confirma ejecutar ESTA MISMA acción pendiente (ej: 'sí adelante', 'dale con fe', 'procede de una vez', 'está bien envíalo').\n"
                    f"- 'CANCELADO': El usuario rechaza, cancela o pide no ejecutar esta acción (ej: 'no lo hagas', 'cancela eso', 'espera me equivoqué', 'déjalo ahí').\n"
                    f"- 'OTRO': El usuario está dando una NUEVA orden, especificando otro destinatario, cambiando datos/fechas, o haciendo otra pregunta distinta (ej: 'enviale a nuevo1...', 'avísale a los profes', 'cuál es la norma', 'quiénes son').\n\n"
                    f"Responde estrictamente una sola palabra: APROBADO, CANCELADO u OTRO."
                )
            }
        ]
        res = await LLMService.chat_completion(messages=prompt, temperature=0.0)
        res_clean = res.strip().upper()
        if "APROBADO" in res_clean:
            return True
        elif "CANCELADO" in res_clean:
            return False
        return None
    except Exception as e:
        logger.warning(f"Error en check_approval_semantic: {e}")
        return None

def registrar_accion_pendiente(conversacion_id: str, tipo_accion: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarda una acción preparada en la tabla `acciones_pendientes` para requerir aprobación humana.
    Asegura integridad referencial comprobando que conversacion_id exista en la BD.
    """
    action_id = f"act_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    payload_json = json.dumps(payload, ensure_ascii=False)

    with get_db_connection() as conn:
        # Verificar que la conversación exista para cumplir con la clave foránea
        chk = conn.execute("SELECT id FROM conversaciones WHERE id = ?", (conversacion_id,)).fetchone()
        if not chk:
            # Buscar la conversación más reciente o registrarla si no existiese
            latest = conn.execute("SELECT id FROM conversaciones ORDER BY updated_at DESC LIMIT 1").fetchone()
            if latest:
                conversacion_id = latest["id"]
            else:
                conn.execute(
                    "INSERT INTO conversaciones (id, user_id, titulo, created_at, updated_at) VALUES (?, 'admin', 'Consulta PIMS', ?, ?)",
                    (conversacion_id, now, now)
                )

        # Limpiar cualquier acción previa pendiente de la misma conversación
        conn.execute("DELETE FROM acciones_pendientes WHERE conversacion_id = ?", (conversacion_id,))
        conn.execute(
            """
            INSERT INTO acciones_pendientes (id, conversacion_id, tipo_accion, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (action_id, conversacion_id, tipo_accion, payload_json, now)
        )

    action_record = {
        "action_id": action_id,
        "tipo": tipo_accion,
        "conversacion_id": conversacion_id,
        "preview": payload.get("preview", {}),
        "payload": payload
    }
    return action_record

def obtener_accion_pendiente(conversacion_id: str) -> Optional[Dict[str, Any]]:
    """
    Recupera la acción pendiente EXCLUSIVAMENTE para la conversación indicada.
    Bajo ningún concepto debe recuperar acciones pendientes de otras conversaciones.
    """
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM acciones_pendientes WHERE conversacion_id = ? ORDER BY created_at DESC LIMIT 1",
            (conversacion_id,)
        ).fetchone()

        if row:
            payload = json.loads(row["payload_json"])
            return {
                "action_id": row["id"],
                "tipo": row["tipo_accion"],
                "conversacion_id": row["conversacion_id"],
                "preview": payload.get("preview", {}),
                "payload": payload
            }
    return None

def eliminar_accion_pendiente(conversacion_id: str):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM acciones_pendientes WHERE conversacion_id = ?", (conversacion_id,))

async def ejecutar_accion_preparada(action_record: Dict[str, Any], user_id: str = "admin") -> Dict[str, Any]:
    """
    Ejecuta físicamente la acción tras la aprobación humana.
    """
    tipo = action_record.get("tipo")
    payload = action_record.get("payload", {})
    action_id = action_record.get("action_id")

    logger.info(f"Ejecutando acción aprobada: {action_id} de tipo {tipo}")

    if tipo == "correo_masivo":
        user_ids = payload.get("user_ids", [])
        asunto = payload.get("asunto", "Aviso Institucional UNSA")
        cuerpo = payload.get("cuerpo", "")
        res = await MCPClient.call_tool("enviar_correo_masivo", {
            "user_ids": user_ids,
            "asunto": asunto,
            "cuerpo": cuerpo,
            "remitente_id": user_id
        })
        if res.get("status") == "error":
            return {
                "tipo": tipo,
                "status": "error",
                "detalles": res,
                "mensaje": f"⚠️ Error al enviar correo: {res.get('message', 'No se pudo completar el envío')}."
            }
        enviados = res.get("enviados", 0)
        return {
            "tipo": tipo,
            "status": "completado" if enviados > 0 else "fallido",
            "detalles": res,
            "mensaje": f"✅ Correo enviado exitosamente a {enviados} destinatarios. ID de lote: {res.get('lote_id', 'N/A')}."
        }

    elif tipo == "inscripcion_masiva":
        user_ids = payload.get("user_ids", [])
        formacion_id = payload.get("formacion_id", "f001")
        exitos = 0
        fallos = 0
        for uid in user_ids:
            r = await MCPClient.call_tool("gestionar_alta_formacion", {
                "user_id": uid,
                "formacion_id": formacion_id
            })
            if r.get("status") == "success":
                exitos += 1
            else:
                fallos += 1

        return {
            "tipo": tipo,
            "status": "completado",
            "total": len(user_ids),
            "exitos": exitos,
            "fallos": fallos,
            "mensaje": f"✅ Inscripción masiva completada: {exitos} usuarios matriculados en formación '{formacion_id}'."
        }

    elif tipo == "inscribir_individual":
        uid = payload.get("user_id")
        fid = payload.get("formacion_id")
        res = await MCPClient.call_tool("gestionar_alta_formacion", {"user_id": uid, "formacion_id": fid})
        return {
            "tipo": tipo,
            "status": "completado",
            "detalles": res,
            "mensaje": f"✅ Matriculado en {res.get('curso')} ({fid}). Vence el {res.get('fecha_vencimiento')}."
        }

    elif tipo == "generar_certificado":
        uid = payload.get("user_id")
        fid = payload.get("formacion_id")
        res = await MCPClient.call_tool("generar_certificado", {"user_id": uid, "formacion_id": fid})
        return {
            "tipo": tipo,
            "status": "completado",
            "detalles": res,
            "mensaje": f"✅ Certificado generado y evidencia guardada en MCP Evidencias: {res.get('certificado_url')}."
        }

    elif tipo == "formulario_capacitacion":
        titulo = payload.get("titulo", "Formulario de Evaluación de Conciencia ISO 27701")
        descripcion = payload.get("descripcion", "Cuestionario de Diagnóstico y Toma de Conciencia de Privacidad")
        curso_id = payload.get("curso_id", "f003")
        preguntas = payload.get("preguntas", [])
        destinatarios = payload.get("destinatarios", [])
        
        res_form = await MCPClient.call_tool("crear_formulario_capacitacion", {
            "titulo": titulo,
            "descripcion": descripcion,
            "curso_id": curso_id,
            "preguntas": preguntas,
            "destinatarios": destinatarios,
            "solicitante_id": user_id
        })

        # Despachar notificación masiva por correo si hay destinatarios
        enviados = 0
        if destinatarios and len(destinatarios) > 0:
            link = res_form.get("enlace_formulario", "https://forms.pims.unsa.edu.pe")
            cuerpo_correo = (
                f"Estimado miembro de la comunidad UNSA,\n\n"
                f"Se le ha convocado a responder el siguiente formulario formativo de toma de conciencia en privacidad:\n"
                f"📌 {titulo}\n\n"
                f"Acceda y complete el formulario en el siguiente enlace institucional:\n"
                f"{link}\n\n"
                f"Oficina de Protección de Datos Personales (PIMS UNSA) - ISO/IEC 27701:2025"
            )
            res_correo = await MCPClient.call_tool("enviar_correo_masivo", {
                "user_ids": destinatarios,
                "asunto": f"📋 Convocatoria: {titulo}",
                "cuerpo": cuerpo_correo,
                "remitente_id": user_id
            })
            enviados = res_correo.get("enviados", 0)

        return {
            "tipo": tipo,
            "status": "completado",
            "detalles": res_form,
            "enviados": enviados,
            "mensaje": f"✅ Formulario '{titulo}' creado y despachado por correo a {len(destinatarios)} destinatarios ({res_form.get('enlace_formulario')})."
        }

    elif tipo == "agendar_calendario":
        titulo = payload.get("titulo", "Capacitación en Privacidad ISO 27701")
        fecha_inicio = payload.get("fecha_inicio", "2026-10-26T10:00:00")
        duracion_minutos = payload.get("duracion_minutos", 60)
        descripcion = payload.get("descripcion", "Sesión de sensibilización obligatoria sobre protección de datos")
        asistentes = payload.get("asistentes", [])
        ubicacion = payload.get("ubicacion", "Google Meet UNSA (Virtual)")
        enlace_reunion = payload.get("enlace_reunion")

        res_cal = await MCPClient.call_tool("programar_evento_calendario", {
            "titulo": titulo,
            "fecha_inicio": fecha_inicio,
            "duracion_minutos": duracion_minutos,
            "descripcion": descripcion,
            "asistentes": asistentes,
            "ubicacion": ubicacion,
            "enlace_reunion": enlace_reunion,
            "solicitante_id": user_id
        })

        return {
            "tipo": tipo,
            "status": "completado",
            "detalles": res_cal,
            "mensaje": f"📅 Evento '{titulo}' agendado en el calendario para {fecha_inicio}. Enlace: {res_cal.get('enlace_reunion')} ({len(asistentes)} invitados)."
        }
        return {
            "tipo": tipo,
            "status": "error",
            "mensaje": f"Tipo de acción desconocido: {tipo}"
        }
