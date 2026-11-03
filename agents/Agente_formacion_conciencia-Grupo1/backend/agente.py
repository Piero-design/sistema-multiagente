import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command

from config import DB_PATH
from state import PIMSState
from prompts import SYSTEM_PROMPT, INTENT_CLASSIFICATION_PROMPT
from rag import buscar_normativa_iso, buscar_politica_negocio
from mcp_client import MCPClient
from db import get_db_connection
from actions import registrar_accion_pendiente, ejecutar_accion_preparada, is_approval_text, check_approval_semantic
from llm_service import LLMService
from skill_loader import cargar_skill_definicion

logger = logging.getLogger("agente")

# Checkpointer en memoria para persistencia de estado de LangGraph
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
logger.info("Checkpointer MemorySaver configurado para LangGraph.")
# ==============================================================================
# NODOS DEL GRAFO LANGGRAPH (9 Nodos)
# ==============================================================================

# 1. Nodo: entry
async def node_entry(state: PIMSState) -> Dict[str, Any]:
    """
    Recibe el input, asegura estado inicializado y carga activamente el archivo SKILL.md.
    """
    skill_text = cargar_skill_definicion()
    logger.info(f"[LangGraph Flow: node_entry] SKILL.md cargado en el estado ({len(skill_text)} bytes) para usuario: {state.get('user_id')}")
    return {
        "rag_context": state.get("rag_context", []),
        "requires_approval": False,
        "tool_result": None,
        "skill_content": skill_text
    }

# 2. Nodo: classify_intent
async def node_classify_intent(state: PIMSState) -> Dict[str, Any]:
    """
    Clasifica la intención del usuario usando LLM con extracción semántica flexible.
    """
    messages = state.get("messages", [])
    last_text = messages[-1].content if messages else ""
    user_rol = state.get("user_rol", "docente")

    # Detección instantánea de saludos de cortesía (0ms)
    t_clean = last_text.strip().lower().rstrip("!.,;¿?")
    saludos_comunes = {
        "hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches",
        "saludos", "hey", "hola buenas", "hola qué tal", "hola que tal", "qué tal", "que tal"
    }
    if t_clean in saludos_comunes:
        logger.info(f"Saludo rápido detectado: '{last_text}'")
        return {
            "intent": "saludo",
            "tool_args": {}
        }

    # Detección semántica de aprobación previa si el usuario escribe texto libre afirmativo/negativo
    if state.get("pending_action"):
        approval_check = await check_approval_semantic(last_text, pending_action=state.get("pending_action"))
        if approval_check is not None:
            return {
                "intent": "confirmacion_flujo",
                "approved": approval_check
            }

    prompt_clasificacion = [
        {"role": "user", "content": f"Rol del usuario: {user_rol}\nMensaje a clasificar: {last_text}"}
    ]

    try:
        raw_res = await LLMService.chat_completion(
            messages=prompt_clasificacion,
            system_prompt=INTENT_CLASSIFICATION_PROMPT,
            json_mode=True
        )
        parsed = json.loads(raw_res)
        intent = parsed.get("intent", "consulta_estado")
        entidades = parsed.get("entidades", {})
    except Exception as e:
        logger.warning(f"Error clasificando con LLM, usando fallback heurístico: {e}")
        t = last_text.lower()
        if any(w in t for w in ["formulario", "google form", "forms", "encuesta", "cuestionario"]):
            intent = "formulario_capacitacion"
        elif any(w in t for w in ["calendario", "recordatorio", "calendar", "agendar", "agenda", "evento", "meet"]):
            intent = "agendar_calendario"
        elif any(w in t for w in ["correo", "enviar", "masiv", "inscribe", "matricular"]):
            intent = "accion_masiva"
        elif any(w in t for w in ["usuarios", "quiénes", "quienes", "nuevos", "lista"]):
            intent = "consulta_usuarios"
        elif any(w in t for w in ["brecha", "gap", "skill", "competencia"]):
            intent = "analisis_brechas"
        elif any(w in t for w in ["mapa de calor", "heatmap", "sensibilizaci", "calor", "riesgo de pii", "riesgos pii"]):
            intent = "mapa_calor_riesgos"
        elif any(w in t for w in ["radar", "cobertura", "estamento"]):
            intent = "radar_cobertura"
        elif any(w in t for w in ["iso", "ley", "29733", "27701", "a.3.17", "norma", "articulo"]):
            intent = "consulta_normativa"
        elif any(w in t for w in ["inscrib", "firmar", "certificado"]):
            intent = "accion_individual"
        elif any(w in t for w in ["comedor", "partido", "matricula carrera", "nota", "clima"]):
            intent = "fuera_de_alcance"
        else:
            intent = "consulta_estado"
        entidades = {}

    logger.info(f"Intención clasificada flexiblemente: {intent} | Entidades: {entidades}")
    return {
        "intent": intent,
        "tool_args": entidades
    }

# 3. Nodo: rag_search
async def node_rag_search(state: PIMSState) -> Dict[str, Any]:
    """
    Consulta las colecciones ChromaDB (normas_iso y politicas_negocio).
    """
    last_msg = state["messages"][-1].content
    iso_docs = buscar_normativa_iso(last_msg, n_results=3)
    pol_docs = buscar_politica_negocio(last_msg, n_results=2)
    
    context_snippets = []
    for d in iso_docs:
        context_snippets.append(f"[Normativa ISO / Ley 29733 - {d.get('fuente')}] {d.get('texto')}")
    for d in pol_docs:
        context_snippets.append(f"[Política UNSA - {d.get('fuente')}] {d.get('texto')}")

    return {"rag_context": context_snippets}

# 4. Nodo: tool_call
async def node_tool_call(state: PIMSState) -> Dict[str, Any]:
    """
    Ejecuta herramientas de lectura o no críticas vía MCP Client.
    Utiliza las entidades semánticas extraídas por el LLM.
    """
    intent = state.get("intent")
    user_id = state.get("user_id")
    user_rol = state.get("user_rol", "docente")
    user_facultad = state.get("user_facultad")
    entidades = state.get("tool_args") or {}
    last_text = state["messages"][-1].content.lower()

    if intent == "consulta_estado":
        res = await MCPClient.call_tool("consultar_estado_formacion", {"user_id": user_id})
        return {"tool_name": "consultar_estado_formacion", "tool_result": res}

    elif intent == "consulta_usuarios":
        filtros = {}
        if entidades.get("antiguedad_dias"):
            filtros["antiguedad_dias"] = int(entidades["antiguedad_dias"])
        elif "nuevo" in last_text or "reciente" in last_text or "ingresante" in last_text:
            filtros["antiguedad_dias"] = 30

        if entidades.get("rol"):
            filtros["rol"] = entidades["rol"]
        elif "docente" in last_text or "profe" in last_text:
            filtros["rol"] = "docente"
        elif "administrativo" in last_text:
            filtros["rol"] = "administrativo"

        if entidades.get("facultad"):
            filtros["facultad"] = entidades["facultad"]
        elif "ingenier" in last_text:
            filtros["facultad"] = "Ingeniería"
        elif "medicina" in last_text:
            filtros["facultad"] = "Medicina"
        elif "derecho" in last_text:
            filtros["facultad"] = "Derecho"

        res = await MCPClient.call_tool("listar_usuarios", {
            "filtros": filtros,
            "solicitante_rol": user_rol,
            "solicitante_facultad": user_facultad,
            "solicitante_id": user_id
        })
        return {"tool_name": "listar_usuarios", "tool_result": res}

    return {"tool_result": None}

# 5. Nodo: prepare_action
async def node_prepare_action(state: PIMSState) -> Dict[str, Any]:
    """
    Prepara el borrador de una acción de escritura (ej. correo o inscripción)
    extrayendo semánticamente destinatarios y redactando dinámicamente el mensaje.
    """
    last_text = state["messages"][-1].content
    user_id = state.get("user_id")
    user_rol = state.get("user_rol", "admin")
    conversacion_id = state.get("conversacion_id") or "conv_current"
    entidades = state.get("tool_args") or {}
    intent = state.get("intent")

    # Caso Formulario Google Forms
    if intent == "formulario_capacitacion" or any(w in last_text.lower() for w in ["formulario", "google form", "forms", "encuesta", "cuestionario"]):
        titulo = entidades.get("titulo_evento_o_form") or "Diagnóstico y Evaluación Formativa de Conciencia en Privacidad"
        descripcion = "Formulario interactivo tipo Google Forms para evaluar competencias en la Ley 29733 e ISO/IEC 27701 (Control A.3.17)."
        curso_id = entidades.get("formacion_id") or "f003"

        destinatarios = []
        nombres = []
        with get_db_connection() as conn:
            if entidades.get("rol"):
                u_rows = conn.execute("SELECT id, email, nombre FROM usuarios WHERE rol = ?", (entidades["rol"],)).fetchall()
            elif "docente" in last_text.lower():
                u_rows = conn.execute("SELECT id, email, nombre FROM usuarios WHERE rol = 'docente'").fetchall()
            elif "administrativo" in last_text.lower():
                u_rows = conn.execute("SELECT id, email, nombre FROM usuarios WHERE rol = 'administrativo'").fetchall()
            else:
                u_rows = conn.execute("SELECT id, email, nombre FROM usuarios WHERE activo = 1 LIMIT 8").fetchall()

            destinatarios = [u["id"] for u in u_rows]
            nombres = [f"{u['nombre']} ({u['email']})" for u in u_rows]

        preguntas = [
            {
                "id": "p1",
                "tipo": "opcion_multiple",
                "pregunta": "¿Cuál es el plazo máximo según el D.S. 016-2024-JUS para reportar una brecha de seguridad a la Autoridad Nacional de Datos Personales?",
                "opciones": ["24 horas", "48 horas", "72 horas", "5 días hábiles"],
                "respuesta_correcta": "24 horas",
                "control_iso": "A.3.11"
            },
            {
                "id": "p2",
                "tipo": "opcion_multiple",
                "pregunta": "Bajo la norma ISO/IEC 27701:2025 y la Ley N° 29733, ¿qué derechos comprende la sigla ARCO?",
                "opciones": [
                    "Acceso, Rectificación, Cancelación y Oposición",
                    "Autorización, Registro, Control y Operación",
                    "Almacenamiento, Respaldo, Cifrado y Organización"
                ],
                "respuesta_correcta": "Acceso, Rectificación, Cancelación y Oposición",
                "control_iso": "A.3.17"
            },
            {
                "id": "p3",
                "tipo": "escala",
                "pregunta": "¿Qué tan preparado se considera para identificar intentos de phishing dirigidos a su correo institucional?",
                "escala_min": 1,
                "escala_max": 5,
                "etiqueta_min": "Muy vulnerable",
                "etiqueta_max": "Totalmente preparado",
                "control_iso": "A.3.17"
            }
        ]

        payload = {
            "titulo": titulo,
            "descripcion": descripcion,
            "curso_id": curso_id,
            "preguntas": preguntas,
            "destinatarios": destinatarios,
            "preview": {
                "tipo": "formulario_google_forms",
                "titulo": titulo,
                "descripcion": descripcion,
                "preguntas_count": len(preguntas),
                "preguntas": preguntas,
                "destinatarios": nombres,
                "total": len(nombres),
                "modal_google_form": True
            }
        }
        accion_rec = registrar_accion_pendiente(conversacion_id, "formulario_capacitacion", payload)
        return {
            "pending_action": accion_rec,
            "requires_approval": True
        }

    # Caso Calendario / Recordatorio
    elif intent == "agendar_calendario" or any(w in last_text.lower() for w in ["calendario", "recordatorio", "calendar", "agendar", "agenda", "evento"]):
        titulo = entidades.get("titulo_evento_o_form") or "Taller Obligatorio: Privacidad de Datos y Control A.3.17"
        fecha_inicio = entidades.get("fecha_evento") or (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT10:00:00")
        duracion = 60
        asistentes = []
        with get_db_connection() as conn:
            u_sample = conn.execute("SELECT id, email, nombre FROM usuarios WHERE activo = 1 LIMIT 6").fetchall()
            asistentes = [f"{u['nombre']} ({u['email']})" for u in u_sample]
            asistentes_emails = [u["email"] for u in u_sample]

        meet_link = f"https://meet.google.com/unsa-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
        payload = {
            "titulo": titulo,
            "fecha_inicio": fecha_inicio,
            "duracion_minutos": duracion,
            "descripcion": "Sesión práctica sobre gestión de incidentes y principio de seguridad de la Ley 29733.",
            "asistentes": asistentes_emails,
            "ubicacion": "Google Meet UNSA (Virtual)",
            "enlace_reunion": meet_link,
            "preview": {
                "tipo": "evento_calendario",
                "titulo": titulo,
                "fecha_inicio": fecha_inicio,
                "duracion": f"{duracion} minutos",
                "asistentes": asistentes,
                "total": len(asistentes),
                "ubicacion": "Google Meet UNSA (Virtual)",
                "enlace_reunion": meet_link,
                "recordatorio": "15 minutos antes por notificación push y correo"
            }
        }
        accion_rec = registrar_accion_pendiente(conversacion_id, "agendar_calendario", payload)
        return {
            "pending_action": accion_rec,
            "requires_approval": True
        }

    tipo_accion = entidades.get("tipo_accion")
    es_correo = (tipo_accion == "correo") or any(w in last_text.lower() for w in ["correo", "mail", "envi", "notifica", "avisa", "escribe"])

    # Caso 1: Envío de correo
    if es_correo:
        import re
        email_mencionado = entidades.get("email_destinatario")
        email_regex = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', last_text)
        target_emails = [email_mencionado] if email_mencionado else email_regex

        user_ids = []
        nombres = []

        with get_db_connection() as conn:
            todos_users = conn.execute("SELECT id, nombre, email FROM usuarios").fetchall()

        # Extraer tokens del mensaje para coincidencia exacta con IDs de usuario (ej. "nuevo1", "admin", "juan.perez")
        tokens_texto = set(re.findall(r'[\w\.-]+', last_text.lower()))
        nombre_entidad = (entidades.get("nombre_destinatario") or "").strip().lower()
        email_entidad = (entidades.get("email_destinatario") or "").strip().lower()

        # 1.1 Coincidencia de usuarios individuales específicos (ID, Email o Nombre)
        for u in todos_users:
            u_id = u["id"].lower()
            u_nom = u["nombre"].lower()
            u_em = u["email"].lower()

            id_coincide = (u_id in tokens_texto) or (nombre_entidad and u_id == nombre_entidad)
            email_coincide = any(em in u_em for em in target_emails) or (email_entidad and email_entidad in u_em)
            # Para nombre solo coincide si no es palabra genérica como "nuevo"
            nom_coincide = (nombre_entidad and len(nombre_entidad) >= 4 and nombre_entidad not in ["nuevo", "nuevos", "usuario", "docente", "profesor"] and nombre_entidad in u_nom)

            if id_coincide or email_coincide or nom_coincide:
                if u["id"] not in user_ids:
                    user_ids.append(u["id"])
                    nombres.append(f"{u['nombre']} ({u['email']})")

        # 1.2 Si se especificó un email que no está en la base de datos
        if not user_ids and target_emails:
            for em in target_emails:
                user_ids.append(em)
                nombres.append(em)

        # 1.3 Solo si no se especificó un usuario individual, buscar grupos por filtros
        if not user_ids:
            filtros = {}
            if entidades.get("antiguedad_dias"):
                filtros["antiguedad_dias"] = int(entidades["antiguedad_dias"])
            elif any(w in last_text.lower() for w in ["nuevos", "ingresantes", "recientes"]):
                filtros["antiguedad_dias"] = 30

            if entidades.get("rol"):
                filtros["rol"] = entidades["rol"]
            elif "docente" in last_text.lower() or "profe" in last_text.lower():
                filtros["rol"] = "docente"
            elif "administrativo" in last_text.lower():
                filtros["rol"] = "administrativo"

            if entidades.get("facultad"):
                filtros["facultad"] = entidades["facultad"]
            elif "ingenier" in last_text.lower():
                filtros["facultad"] = "Ingeniería"
            elif "medicina" in last_text.lower():
                filtros["facultad"] = "Medicina"
            elif "derecho" in last_text.lower():
                filtros["facultad"] = "Derecho"

            lista_users = await MCPClient.call_tool("listar_usuarios", {
                "filtros": filtros,
                "solicitante_rol": user_rol,
                "solicitante_id": user_id
            })
            destinatarios = lista_users.get("usuarios", [])
            user_ids = [u["id"] for u in destinatarios]
            nombres = [f"{u['nombre']} ({u['email']})" for u in destinatarios]

        # Extraer detalles específicos del mensaje (fechas, horas, instrucciones)
        detalles = entidades.get("detalles_mensaje")
        if not detalles:
            m = re.search(r'(?:el\s+)?(?:lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo|mañana|hoy)[^\.\n]*', last_text, re.IGNORECASE)
            if m:
                detalles = m.group(0).strip()
            elif " que " in last_text.lower():
                partes = last_text.split(" que ", 1)
                if len(partes) > 1 and len(partes[1].strip()) > 5:
                    detalles = partes[1].strip()

        asunto = entidades.get("asunto_sugerido") or "Convocatoria: Capacitación en Privacidad de Datos UNSA (Ley 29733 / ISO 27701)"

        if detalles:
            cuerpo = (
                f"Estimado(a) miembro de la comunidad UNSA,\n\n"
                f"Por medio del presente recordatorio institucional, se le convoca a la actividad formativa "
                f"en Protección de Datos Personales (Ley N° 29733 y control ISO/IEC 27701:2025 A.3.17).\n\n"
                f"Indicaciones: {detalles}\n\n"
                f"Plataforma: Moodle / Teams UNSA.\n\n"
                f"Atentamente,\nOficina PIMS - Privacidad y Formación UNSA"
            )
        else:
            cuerpo = (
                "Estimado(a) miembro de la comunidad UNSA,\n\n"
                "Por medio del presente recordatorio institucional, se le convoca a participar en la sesión "
                "obligatoria de capacitación en Protección de Datos Personales bajo el marco de la Ley N° 29733 "
                "y el control A.3.17 de la norma ISO/IEC 27701:2025.\n\n"
                "Atentamente,\nOficina PIMS - Privacidad y Formación UNSA"
            )

        payload = {
            "user_ids": user_ids,
            "asunto": asunto,
            "cuerpo": cuerpo,
            "preview": {
                "destinatarios": nombres,
                "total": len(nombres),
                "asunto": asunto,
                "cuerpo": cuerpo
            }
        }
        accion_rec = registrar_accion_pendiente(conversacion_id, "correo_masivo", payload)
        return {
            "pending_action": accion_rec,
            "requires_approval": True
        }

    # Caso 2: Inscripción masiva o grupal a cursos
    else:
        formacion_id = entidades.get("formacion_id") or "f001"
        filtros = {}
        if entidades.get("rol"):
            filtros["rol"] = entidades["rol"]
        elif "docente" in last_text.lower():
            filtros["rol"] = "docente"
        if entidades.get("facultad"):
            filtros["facultad"] = entidades["facultad"]
        elif "ingenier" in last_text.lower():
            filtros["facultad"] = "Ingeniería"

        lista_users = await MCPClient.call_tool("listar_usuarios", {
            "filtros": filtros,
            "solicitante_rol": user_rol,
            "solicitante_id": user_id
        })
        destinatarios = lista_users.get("usuarios", [])
        user_ids = [u["id"] for u in destinatarios]
        nombres = [f"{u['nombre']} ({u['email']})" for u in destinatarios]

        payload = {
            "user_ids": user_ids,
            "formacion_id": formacion_id,
            "preview": {
                "destinatarios": nombres,
                "total": len(nombres),
                "curso": "Protección de Datos Personales - Ley 29733 (f001)",
                "accion": "Matrícula masiva en LMS Moodle UNSA"
            }
        }
        accion_rec = registrar_accion_pendiente(conversacion_id, "inscripcion_masiva", payload)
        return {
            "pending_action": accion_rec,
            "requires_approval": True
        }

# 6. Nodo: human_approval
async def node_human_approval(state: PIMSState) -> Dict[str, Any]:
    """
    Punto de control de aprobación humana (Human-in-the-Loop).
    Evalúa si la acción fue aprobada previamente (True/False) o requiere confirmación en generate_response.
    """
    approved = state.get("approved")
    return {"approved": approved}

# 7. Nodo: execute_action
async def node_execute_action(state: PIMSState) -> Dict[str, Any]:
    """
    Ejecuta físicamente la acción tras la aprobación humana.
    """
    pending = state.get("pending_action")
    if not pending:
        return {"tool_result": {"status": "error", "message": "No hay acción pendiente para ejecutar."}}

    user_id = state.get("user_id", "admin")
    resultado = await ejecutar_accion_preparada(pending, user_id=user_id)
    return {
        "tool_result": resultado,
        "pending_action": None,
        "requires_approval": False
    }

# 8. Nodo: generate_response
async def node_generate_response(state: PIMSState) -> Dict[str, Any]:
    """
    Genera la respuesta final estructurada en Markdown con citas ISO/Ley 29733.
    """
    messages = state.get("messages", [])
    user_id = state.get("user_id")
    user_rol = state.get("user_rol")
    intent = state.get("intent")
    rag = state.get("rag_context", [])
    tool_res = state.get("tool_result")
    pending = state.get("pending_action")
    approved = state.get("approved")

    # Si hay una acción que requiere aprobación y está esperando, informar al usuario
    if state.get("requires_approval") and pending:
        preview = pending.get("preview", {})
        texto_aprobacion = (
            f"He preparado la siguiente acción que requiere tu confirmación antes de ejecutarse:\n\n"
            f"> **📋 Vista Previa de la Acción ({pending.get('tipo')})**\n"
            f"> - **Destinatarios ({preview.get('total', 0)}):** {', '.join(preview.get('destinatarios', []))}\n"
        )
        if "asunto" in preview:
            texto_aprobacion += f"> - **Asunto:** {preview.get('asunto')}\n"
        if "cuerpo" in preview:
            texto_aprobacion += f"> - **Cuerpo:**\n> {preview.get('cuerpo')}\n"
        if "curso" in preview:
            texto_aprobacion += f"> - **Curso a matricular:** {preview.get('curso')}\n"

        texto_aprobacion += "\n¿Confirmas la ejecución de esta acción? Puedes presionar **Confirmar** o responder 'Sí'."
        return {"messages": messages + [AIMessage(content=texto_aprobacion)]}

    # Si fue rechazada
    if approved is False:
        texto_rechazo = "Acción cancelada. No se ha realizado ninguna modificación ni envío en el sistema."
        return {"messages": messages + [AIMessage(content=texto_rechazo)]}

    # Construir prompt enriquecido con contexto
    prompt_context = f"Usuario ID: {user_id} | Rol: {user_rol}\n"
    prompt_context += f"Intención detectada: {intent}\n"
    if intent == "saludo":
        prompt_context += (
            "\nInstrucción: El usuario te ha saludado. Respóndele cordialmente de acuerdo a su rol institucional, "
            "dale la bienvenida y preséntate brevemente como el Agente #8 de Formación y Conciencia UNSA "
            "(PIMS ISO/IEC 27701:2025 Control A.3.17 y Ley N° 29733). Explícale de forma amigable y clara qué consultas "
            "o acciones puede realizar contigo (verificar cumplimiento de capacitaciones, consultar normativas de privacidad, "
            "explorar brechas competenciales, mapas de calor o coordinar convocatorias).\n"
        )
    elif intent == "analisis_brechas":
        try:
            from brechas import calcular_matriz_brechas
            mb = calcular_matriz_brechas()
            prompt_context += (
                f"\nInstrucción Prioritaria: El usuario solicita la Matriz de Brechas de Competencia por Rol (Skill Gap Analysis) "
                f"según el Control A.3.17 y Cláusula 7.2 de ISO/IEC 27701:2025 y Ley 29733 (Art. 19 / D.S. 003-2013-JUS Art. 38).\n"
                f"DATOS CUANTITATIVOS REALES DEL SISTEMA:\n"
                f"- Tasa de Cumplimiento Institucional: {mb['kpis']['cumplimiento_global_pct']}%\n"
                f"- Brecha Institucional Promedio (Skill Gap): {mb['kpis']['gap_promedio_pct']}%\n"
                f"- Meta Normativa: {mb['kpis']['meta_institucional_pct']}%\n"
                f"- Gaps Críticos: {mb['kpis']['brechas_criticas_conteo']}\n"
                f"- Cursos Vencidos: {mb['kpis']['total_cursos_vencidos']}\n"
                f"- Resumen por Estamento:\n"
            )
            for r in mb["roles"]:
                prompt_context += f"  * {r['nombre_rol']}: Cumplimiento {r['cumplimiento_pct']}% | Gap: {r['gap_pct']}% | Severidad: {r['severidad'].upper()} (Completados: {r['completados']}, Pendientes: {r['pendientes']}, Vencidos: {r['vencidos']}, Sin Asignar: {r['sin_asignar']})\n"
        except Exception as e:
            logger.warning(f"Error cargando matriz cuantitativa: {e}")

        prompt_context += (
            "\nPresenta en tu respuesta una tabla Markdown comparativa por rol con: Estamento, Cursos Clave, % Cumplimiento, % Brecha (Skill Gap), Severidad y Acción Inmediata. "
            "Cita expresamente la Cláusula 7.2 (Competencia) y el Control A.3.17 de ISO/IEC 27701:2025, así como el Art. 38 del D.S. 003-2013-JUS. "
            "Explica que los datos se han sincronizado con la Matriz de Brechas institucional e "
            "INCLUYE OBLIGATORIAMENTE al final de tu respuesta el enlace interactivo markdown para abrir la pestaña: "
            "[📊 Abrir Matriz de Brechas de Competencia (Skill Gap)](#tab=brechas)\n"
        )
    elif intent == "mapa_calor_riesgos":
        try:
            from heatmap import calcular_mapa_calor
            hm = calcular_mapa_calor()
            prompt_context += (
                f"\nInstrucción Prioritaria: El usuario solicita el Mapa de Calor (Heatmap): Índice de Sensibilización sobre Riesgos de PII por Tema "
                f"conforme a ISO/IEC 27701:2025 Control A.3.17 (Sensibilización), Control A.3.11 y Ley N° 29733 (Principio de Seguridad Art. 19).\n"
                f"DATOS TERMOGRÁFICOS REALES DEL SISTEMA:\n"
                f"- Índice Global de Sensibilización: {hm['kpis']['indice_global_sensibilizacion']}/100\n"
                f"- Grado de Vulnerabilidad Institucional: {hm['kpis']['vulnerabilidad_promedio_pct']}%\n"
                f"- Zona Térmica Crítica (Máxima alerta): {hm['kpis']['zona_critica'] if 'zona_critica' in hm['kpis'] else hm['kpis']['zona_termica_critica']}\n"
                f"- Ejes en Alerta Roja: {hm['kpis']['ejes_en_alerta_roja']} de 6 dominios\n"
                f"- Desglose por Eje Temático:\n"
            )
            for e in hm["ejes"]:
                prompt_context += f"  * {e['nombre']} ({e['control_iso']}): Temperatura {e['temperatura_vulnerabilidad']}° ({e['etiqueta_termica']}) | Sensibilización {e['indice_sensibilizacion']}/100\n"
        except Exception as e:
            logger.warning(f"Error cargando datos de heatmap en agente: {e}")

        prompt_context += (
            "\nPresenta en tu respuesta una tabla Markdown termográfica con: Eje Temático, Control ISO, Nivel de Vulnerabilidad (°), Nivel Térmico y Medida Preventiva Sugerida. "
            "Cita el Control A.3.17 y el Control A.3.11 de ISO/IEC 27701:2025, así como el D.S. N° 016-2024-JUS (Reporte de brechas en 24h). "
            "Explica que los datos térmicos se han sincronizado con el Mapa de Calor institucional e "
            "INCLUYE OBLIGATORIAMENTE al final de tu respuesta el enlace interactivo markdown para abrir la pestaña: "
            "[🔥 Ver Mapa de Calor de Riesgos PII](#tab=heatmap)\n"
        )
    elif intent == "radar_cobertura":
        try:
            from radar import calcular_radar_cobertura
            r_info = calcular_radar_cobertura()
            rk = r_info["kpis"]
            tabla_estamentos = "| Estamento | Padrón | Inscritos | Aprobados | % Cobertura | Estado Radar |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for em in r_info["estamentos"]:
                tabla_estamentos += f"| {em['icono']} {em['nombre']} | {em['padron_total']} | {em['inscritos']} | {em['completados']} | **{em['cobertura_pct']}%** | {em['estado_radar']} |\n"

            prompt_context += (
                f"\nDatos cuantitativos del Radar de Cobertura por Estamento (Control A.3.17 ISO 27701 y Cláusula 7.2):\n"
                f"- Cobertura Institucional Ponderada: {rk['cobertura_global_pct']}%\n"
                f"- Eficacia Formativa Global: {rk['eficacia_global_pct']}%\n"
                f"- Meta Institucional de Cobertura: {rk['meta_institucional_pct']}%\n"
                f"- Brecha Global: {rk['brecha_global_pct']}%\n"
                f"- Estamento Líder: {rk['estamento_lider']}\n"
                f"- Estamento Rezagado: {rk['estamento_rezagado']}\n\n"
                f"Tabla de Cobertura Multiaxial por Estamento Universitario:\n{tabla_estamentos}\n"
                "INCLUYE OBLIGATORIAMENTE en tu respuesta la tabla de cobertura estamental Markdown, analiza la simetría del polígono "
                "e INCLUYE al final el enlace interactivo markdown para abrir la pestaña: "
                "[🕸️ Explorar Gráfico de Radar de Cobertura](#tab=radar)\n"
            )
        except Exception as e:
            logger.warning(f"Error cargando radar en agente: {e}")
            prompt_context += (
                "\nInstrucción Prioritaria: El usuario solicita el Gráfico de Radar de Cobertura de Capacitación por Estamento Universitario "
                "(Control A.3.17 de ISO/IEC 27701:2025). Explica cómo se audita el alcance formativo transversal entre Pregrado, Posgrado, "
                "Docentes y Personal Administrativo para garantizar una cobertura superior a la meta institucional. "
                "INCLUYE OBLIGATORIAMENTE al final de tu respuesta el enlace interactivo markdown para abrir la pestaña: "
                "[🕸️ Explorar Gráfico de Radar de Cobertura](#tab=radar)\n"
            )
    elif intent == "formulario_capacitacion":
        prompt_context += (
            "\nInstrucción Prioritaria: Se ha preparado un Formulario de Evaluación y Diagnóstico interactivo estilo Google Forms "
            "con preguntas clave sobre la Ley N° 29733 (Derechos ARCO, Principio de Seguridad) y la norma ISO/IEC 27701:2025 "
            "(Control A.3.11 plazo de 24h para reporte de incidentes y Control A.3.17 toma de conciencia). "
            "Explica al usuario que puede previsualizar el formulario interactivo en pantalla y confirmar el envío a los correos institucionales de los destinatarios.\n"
        )
    elif intent == "agendar_calendario":
        prompt_context += (
            "\nInstrucción Prioritaria: Se ha preparado una convocatoria formal de evento en los calendarios institucionales "
            "(Google Calendar / Outlook mock) con enlace Google Meet y recordatorio automático para la capacitación en privacidad. "
            "Indica al usuario que revise los detalles del evento y confirme para agendar y despachar las invitaciones.\n"
        )
    if rag:
        prompt_context += "\nEvidencias y Normativas Recuperadas (RAG):\n" + "\n".join(rag) + "\n"
    if tool_res:
        prompt_context += f"\nResultados de Herramientas del Sistema:\n{json.dumps(tool_res, ensure_ascii=False, indent=2)}\n"

    last_query = messages[-1].content if messages else "¿En qué me puedes asistir?"

    mensajes_llm = [
        {"role": "user", "content": f"Contexto interno del sistema:\n{prompt_context}\n\nPregunta o instrucción del usuario: {last_query}"}
    ]

    respuesta_llm = await LLMService.chat_completion(
        messages=mensajes_llm,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2
    )

    return {"messages": messages + [AIMessage(content=respuesta_llm)]}

# 9. Nodo: derive_response
async def node_derive_response(state: PIMSState) -> Dict[str, Any]:
    """
    Responde de forma natural, inteligente y flexible a consultas fuera de alcance o generales,
    orientando amablemente al usuario hacia el propósito del agente (PIMS / Privacidad UNSA).
    """
    messages = state.get("messages", [])
    last_query = messages[-1].content if messages else "¿En qué puedo ayudarte?"
    user_rol = state.get("user_rol", "miembro de la comunidad")

    prompt = [
        {
            "role": "user",
            "content": (
                f"Eres el Agente #8 de Formación y Conciencia en Privacidad de la UNSA (PIMS ISO 27701:2025 / Ley 29733).\n"
                f"El usuario ({user_rol}) ha consultado algo que no corresponde directamente a tu función principal:\n"
                f"\"{last_query}\"\n\n"
                f"Instrucciones para responder:\n"
                f"1. Sé natural, empático, inteligente y conversacional. NUNCA respondas con una plantilla robótica ni digas que vaya a secretaría para cosas que no son trámites.\n"
                f"2. Si la pregunta es sobre la UNSA en general (por ejemplo: historia, fundación en 1828, lema, facultades o cultura agustina), responde con un dato breve, certero y respetuoso (1 o 2 frases interesantes).\n"
                f"3. Si es sobre un trámite ajeno (matrículas de carrera profesional, pagos, comedor, etc.), indícale con cortesía a qué oficina o canal universitario acudir.\n"
                f"4. Luego, recuerda amablemente que tu especialidad en este sistema es la gestión de capacitaciones en Privacidad de Datos (Ley N° 29733) y acuerdos de confidencialidad (ISO/IEC 27701:2025 A.3.17/A.3.18), e invítalo a consultarte sobre ello si lo necesita."
            )
        }
    ]

    try:
        respuesta = await LLMService.chat_completion(
            messages=prompt,
            temperature=0.3
        )
    except Exception as e:
        logger.warning(f"Error generando derivación con LLM: {e}")
        respuesta = (
            "Comprendo tu consulta, pero como **Agente de Formación y Conciencia de la UNSA**, mi ámbito de competencia "
            "se enfoca en la capacitación sobre **Protección de Datos Personales (Ley N° 29733)** y la norma **ISO/IEC 27701:2025**. "
            "Para ese tema en específico te sugiero consultar en los canales generales de la universidad."
        )

    return {"messages": messages + [AIMessage(content=respuesta)]}


# ==============================================================================
# CONDICIONALES DE ENCAMINAMIENTO
# ==============================================================================

def route_from_classify(state: PIMSState) -> str:
    intent = state.get("intent")
    if intent == "confirmacion_flujo":
        return "human_approval"
    elif intent == "fuera_de_alcance":
        return "derive_response"
    elif intent in ("accion_masiva", "formulario_capacitacion", "agendar_calendario"):
        return "prepare_action"
    elif intent in ("consulta_normativa", "analisis_brechas", "mapa_calor_riesgos", "radar_cobertura"):
        return "rag_search"
    elif intent in ("consulta_estado", "consulta_usuarios"):
        return "tool_call"
    else:
        return "generate_response"

def route_from_approval(state: PIMSState) -> str:
    if state.get("approved") is True:
        return "execute_action"
    return "generate_response"


# ==============================================================================
# CONSTRUCCIÓN DEL GRAFO LANGGRAPH
# ==============================================================================

builder = StateGraph(PIMSState)

# Adición de los 9 nodos
builder.add_node("entry", node_entry)
builder.add_node("classify_intent", node_classify_intent)
builder.add_node("rag_search", node_rag_search)
builder.add_node("tool_call", node_tool_call)
builder.add_node("prepare_action", node_prepare_action)
builder.add_node("human_approval", node_human_approval)
builder.add_node("execute_action", node_execute_action)
builder.add_node("generate_response", node_generate_response)
builder.add_node("derive_response", node_derive_response)

# Definición de Aristas
builder.set_entry_point("entry")
builder.add_edge("entry", "classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_from_classify,
    {
        "rag_search": "rag_search",
        "tool_call": "tool_call",
        "prepare_action": "prepare_action",
        "derive_response": "derive_response",
        "generate_response": "generate_response",
        "human_approval": "human_approval"
    }
)

builder.add_edge("rag_search", "generate_response")
builder.add_edge("tool_call", "generate_response")
builder.add_edge("prepare_action", "human_approval")

builder.add_conditional_edges(
    "human_approval",
    route_from_approval,
    {
        "execute_action": "execute_action",
        "generate_response": "generate_response"
    }
)

builder.add_edge("execute_action", "generate_response")
builder.add_edge("generate_response", END)
builder.add_edge("derive_response", END)

# Compilación del grafo ejecutable
pims_agent_graph = builder.compile(checkpointer=checkpointer)
