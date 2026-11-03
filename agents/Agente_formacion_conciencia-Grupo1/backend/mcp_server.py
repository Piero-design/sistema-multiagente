import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from db import get_db_connection, registrar_audit
from mcp_externos.lms_mock import matricular as lms_matricular
from mcp_externos.correo_mock import enviar_correo as correo_enviar
from mcp_externos.evidencias_mock import guardar_evidencia as evidencia_guardar

logger = logging.getLogger("mcp_server")

# Inicialización condicional de FastMCP si la librería está disponible
try:
    from fastmcp import FastMCP
    mcp = FastMCP("PIMS-UNSA-Formacion-Conciencia")
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("PIMS-UNSA-Formacion-Conciencia")
    except ImportError:
        class FastMCPStub:
            def tool(self):
                def decorator(fn):
                    return fn
                return decorator
            def run(self, **kwargs):
                print("FastMCP corriendo en modo embebido")
        mcp = FastMCPStub()

# ==============================================================================
# HERRAMIENTA 1: gestionar_alta_formacion
# ==============================================================================
@mcp.tool()
def gestionar_alta_formacion(user_id: str, formacion_id: str) -> dict:
    """
    Inscribe al usuario en una formación.
    Internamente orquesta con el MCP LMS (mock) para matricularlo en Moodle UNSA.
    """
    now = datetime.now()
    fecha_asignacion = now.strftime("%Y-%m-%d")
    fecha_vencimiento = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    with get_db_connection() as conn:
        user = conn.execute("SELECT id, nombre, email FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return {"status": "error", "message": f"Usuario no encontrado: {user_id}"}

        curso = conn.execute("SELECT id, titulo, control_iso FROM formaciones WHERE id = ?", (formacion_id,)).fetchone()
        if not curso:
            return {"status": "error", "message": f"Formación no encontrada: {formacion_id}"}

        # Comprobar si ya existe la asignación
        asignacion = conn.execute(
            "SELECT id, estado FROM formacion_usuario WHERE user_id = ? AND formacion_id = ?",
            (user_id, formacion_id)
        ).fetchone()

        if asignacion:
            asignacion_id = asignacion["id"]
            conn.execute(
                """
                UPDATE formacion_usuario
                SET estado = 'en_curso', fecha_asignacion = ?, fecha_vencimiento = ?
                WHERE id = ?
                """,
                (fecha_asignacion, fecha_vencimiento, asignacion_id)
            )
        else:
            asignacion_id = f"fu_{uuid.uuid4().hex[:8]}"
            conn.execute(
                """
                INSERT INTO formacion_usuario (
                    id, user_id, formacion_id, estado, fecha_asignacion, fecha_vencimiento
                ) VALUES (?, ?, ?, 'en_curso', ?, ?)
                """,
                (asignacion_id, user_id, formacion_id, fecha_asignacion, fecha_vencimiento)
            )

    # Orquestación con el MCP LMS externo
    lms_res = lms_matricular(user_id=user_id, curso_id=formacion_id)

    registrar_audit(
        user_id=user_id,
        accion="gestionar_alta_formacion",
        detalle={"formacion_id": formacion_id, "lms_status": lms_res.get("status")}
    )

    return {
        "status": "success",
        "asignacion_id": asignacion_id,
        "usuario": user["nombre"],
        "curso": curso["titulo"],
        "control_iso": curso["control_iso"],
        "estado": "en_curso",
        "fecha_vencimiento": fecha_vencimiento,
        "lms_integracion": lms_res
    }

# ==============================================================================
# HERRAMIENTA 2: consultar_estado_formacion
# ==============================================================================
@mcp.tool()
def consultar_estado_formacion(user_id: str) -> dict:
    """
    Retorna lista de formaciones asignadas, su estado y avance en concientización ISO 27701 (A.3.17).
    """
    with get_db_connection() as conn:
        user = conn.execute("SELECT id, nombre, rol, facultad, email FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return {"status": "error", "message": f"Usuario no encontrado: {user_id}"}

        cursos = conn.execute(
            """
            SELECT fu.id as asignacion_id, f.id as formacion_id, f.titulo, f.control_iso,
                   fu.estado, fu.fecha_asignacion, fu.fecha_vencimiento, fu.certificado_url
            FROM formacion_usuario fu
            JOIN formaciones f ON fu.formacion_id = f.id
            WHERE fu.user_id = ?
            ORDER BY fu.fecha_vencimiento ASC
            """,
            (user_id,)
        ).fetchall()

    completados = [c for c in cursos if c["estado"] == "completado"]
    pendientes = [c for c in cursos if c["estado"] in ("pendiente", "en_curso")]
    vencidos = [c for c in cursos if c["estado"] == "vencido"]

    porcentaje_cumplimiento = int((len(completados) / len(cursos) * 100)) if cursos else 100

    return {
        "status": "success",
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "rol": user["rol"],
            "facultad": user["facultad"],
            "email": user["email"]
        },
        "resumen": {
            "total_formaciones": len(cursos),
            "completadas": len(completados),
            "pendientes": len(pendientes),
            "vencidas": len(vencidos),
            "porcentaje_cumplimiento": porcentaje_cumplimiento
        },
        "formaciones": cursos
    }

# ==============================================================================
# HERRAMIENTA 3: generar_reporte_conciencia
# ==============================================================================
@mcp.tool()
def generar_reporte_conciencia(facultad: Optional[str] = None) -> dict:
    """
    Genera reporte agregado de cumplimiento de formación y concienciación en privacidad
    (Control ISO 27701 A.3.17 y Ley 29733) para una facultad específica o a nivel global UNSA.
    """
    with get_db_connection() as conn:
        if facultad and facultad.lower() not in ("todas", "global", "unsa"):
            usuarios = conn.execute(
                "SELECT id, nombre, rol, facultad FROM usuarios WHERE facultad LIKE ? AND activo = 1",
                (f"%{facultad}%",)
            ).fetchall()
            alcance = f"Facultad: {facultad}"
        else:
            usuarios = conn.execute("SELECT id, nombre, rol, facultad FROM usuarios WHERE activo = 1").fetchall()
            alcance = "Toda la UNSA"

        user_ids = [u["id"] for u in usuarios]
        if not user_ids:
            return {
                "status": "success",
                "alcance": alcance,
                "total_usuarios": 0,
                "mensaje": "No se encontraron usuarios en la facultad indicada"
            }

        placeholders = ",".join(["?"] * len(user_ids))

        # Métricas formaciones
        cursos_asignados = conn.execute(
            f"SELECT estado, count(*) as count FROM formacion_usuario WHERE user_id IN ({placeholders}) GROUP BY estado",
            user_ids
        ).fetchall()

    resumen_formacion = {r["estado"]: r["count"] for r in cursos_asignados}

    total_f = sum(resumen_formacion.values())
    completadas = resumen_formacion.get("completado", 0)
    tasa_formacion = round((completadas / total_f * 100), 1) if total_f > 0 else 0.0

    return {
        "status": "success",
        "alcance": alcance,
        "total_usuarios": len(usuarios),
        "tasa_cumplimiento_formacion_pct": tasa_formacion,
        "formaciones": {
            "total": total_f,
            "completadas": completadas,
            "pendientes": resumen_formacion.get("pendiente", 0) + resumen_formacion.get("en_curso", 0),
            "vencidas": resumen_formacion.get("vencido", 0)
        },
        "timestamp": datetime.now().isoformat()
    }

# ==============================================================================
# HERRAMIENTA 4: evaluar_matriz_brechas
# ==============================================================================
@mcp.tool()
def evaluar_matriz_brechas(rol: Optional[str] = None) -> dict:
    """
    Evalúa la Matriz de Brechas de Competencia por Rol (Skill Gap Analysis)
    conforme a ISO/IEC 27701:2025 Cláusula 7.2 (Competencia), Cláusula 7.3 (Concienciación),
    Control A.3.17 y Ley N° 29733 (Art. 19 / D.S. 003-2013-JUS Art. 38).
    Retorna KPIs consolidados, gaps por estamento universitario y personal con cursos pendientes/vencidos.
    """
    from brechas import calcular_matriz_brechas
    return calcular_matriz_brechas(rol_filtro=rol)

# ==============================================================================
# HERRAMIENTA 5: evaluar_mapa_calor
# ==============================================================================
@mcp.tool()
def evaluar_mapa_calor(facultad: Optional[str] = None) -> dict:
    """
    Evalúa el Mapa de Calor (Heatmap) de Vulnerabilidad y Sensibilización sobre Riesgos PII
    conforme a ISO/IEC 27701:2025 Control A.3.17 (Sensibilización), Control A.3.11 y Ley N° 29733.
    Retorna métricas térmicas en 6 ejes de riesgo (phishing, fuga en investigación, ARCO, retención, consentimiento y brechas en 24h)
    y matriz bidimensional por facultad.
    """
    from heatmap import calcular_mapa_calor
    return calcular_mapa_calor(facultad_filtro=facultad)

# ==============================================================================
# HERRAMIENTA 6: evaluar_radar_cobertura
# ==============================================================================
@mcp.tool()
def evaluar_radar_cobertura(estamento: Optional[str] = None, facultad: Optional[str] = None) -> dict:
    """
    Evalúa la cobertura de capacitación por estamento universitario (Control A.3.17 y Cláusula 7.2 ISO/IEC 27701:2025).
    Genera el polígono multiaxial del radar, comparativa por facultad y métricas de eficacia formativa.
    """
    from radar import calcular_radar_cobertura
    return calcular_radar_cobertura(estamento_filtro=estamento, facultad_filtro=facultad)

# ==============================================================================
# HERRAMIENTA 7: crear_formulario_capacitacion
# ==============================================================================
@mcp.tool()
def crear_formulario_capacitacion(
    titulo: str,
    descripcion: str,
    curso_id: Optional[str] = None,
    preguntas: Optional[List[Dict[str, Any]]] = None,
    destinatarios: Optional[List[str]] = None,
    solicitante_id: str = "admin"
) -> dict:
    """
    Crea un formulario de evaluación o diagnóstico formativo (estilo Google Forms / Microsoft Forms)
    para medir el nivel de conciencia y cumplimiento de la Ley 29733 e ISO/IEC 27701.
    Almacena el formulario en BD con enlace de acceso y lista de destinatarios institucionales.
    """
    form_id = f"gform_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()

    preguntas_default = [
        {
            "id": "p1",
            "tipo": "opcion_multiple",
            "pregunta": "¿Cuál es el plazo máximo según el D.S. 016-2024-JUS para notificar una brecha de seguridad a la Autoridad Nacional de Protección de Datos Personales?",
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
            "pregunta": "¿Qué tan preparado se considera para detectar ataques de phishing y correos fraudulentos dirigidos a su cuenta institucional @unsa.edu.pe?",
            "escala_min": 1,
            "escala_max": 5,
            "etiqueta_min": "Muy vulnerable",
            "etiqueta_max": "Totalmente preparado",
            "control_iso": "A.3.17"
        }
    ]
    preguntas_finales = preguntas if preguntas and len(preguntas) > 0 else preguntas_default
    destinatarios_finales = destinatarios or []

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO formularios_capacitacion (
                id, titulo, descripcion, curso_id, preguntas_json, destinatarios_json, estado, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'activo', ?)
            """,
            (
                form_id,
                titulo,
                descripcion,
                curso_id or "f003",
                json.dumps(preguntas_finales, ensure_ascii=False),
                json.dumps(destinatarios_finales, ensure_ascii=False),
                now
            )
        )

    enlace_form = f"https://forms.pims.unsa.edu.pe/eval/{form_id}"

    registrar_audit(
        user_id=solicitante_id,
        accion="crear_formulario_capacitacion",
        detalle={"form_id": form_id, "titulo": titulo, "destinatarios_count": len(destinatarios_finales)}
    )

    return {
        "status": "success",
        "form_id": form_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "curso_id": curso_id or "f003",
        "enlace_formulario": enlace_form,
        "total_preguntas": len(preguntas_finales),
        "preguntas": preguntas_finales,
        "destinatarios": destinatarios_finales,
        "mensaje": f"Formulario '{titulo}' creado exitosamente con {len(preguntas_finales)} preguntas."
    }

# ==============================================================================
# HERRAMIENTA 8: programar_evento_calendario
# ==============================================================================
@mcp.tool()
def programar_evento_calendario(
    titulo: str,
    fecha_inicio: str,
    duracion_minutos: int = 60,
    descripcion: str = "",
    asistentes: Optional[List[str]] = None,
    ubicacion: str = "Google Meet UNSA (Virtual)",
    enlace_reunion: Optional[str] = None,
    solicitante_id: str = "admin"
) -> dict:
    """
    Programa un evento o recordatorio en el calendario institucional (Google Calendar / Outlook mock)
    con sincronización de invitaciones para talleres, seminarios o vencimiento de capacitaciones ISO 27701.
    """
    evento_id = f"cal_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    asistentes_finales = asistentes or []
    link = enlace_reunion or f"https://meet.google.com/unsa-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO eventos_calendario (
                id, titulo, fecha_inicio, duracion_minutos, descripcion, asistentes_json, ubicacion, enlace_reunion, estado, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'programado', ?)
            """,
            (
                evento_id,
                titulo,
                fecha_inicio,
                duracion_minutos,
                descripcion,
                json.dumps(asistentes_finales, ensure_ascii=False),
                ubicacion,
                link,
                now
            )
        )

    registrar_audit(
        user_id=solicitante_id,
        accion="programar_evento_calendario",
        detalle={"evento_id": evento_id, "titulo": titulo, "fecha_inicio": fecha_inicio, "asistentes": len(asistentes_finales)}
    )

    return {
        "status": "success",
        "evento_id": evento_id,
        "titulo": titulo,
        "fecha_inicio": fecha_inicio,
        "duracion_minutos": duracion_minutos,
        "ubicacion": ubicacion,
        "enlace_reunion": link,
        "total_asistentes": len(asistentes_finales),
        "asistentes": asistentes_finales,
        "recordatorio": "15 minutos antes por notificación push y correo",
        "mensaje": f"Evento '{titulo}' agendado en el calendario para {fecha_inicio}."
    }

# ==============================================================================
# HERRAMIENTA 6: listar_usuarios
# ==============================================================================
@mcp.tool()
def listar_usuarios(
    filtros: Optional[Dict[str, Any]] = None,
    solicitante_rol: str = "admin",
    solicitante_facultad: Optional[str] = None,
    solicitante_id: Optional[str] = None
) -> dict:
    """
    Devuelve lista de usuarios según filtros:
    filtros: {'rol': str, 'facultad': str, 'departamento': str, 'antiguedad_dias': int, 'estado_formacion': str}
    Respeta el alcance del rol:
      - docente/administrativo/estudiante: solo a sí mismo
      - jefe: solo su equipo o facultad
      - admin: toda la UNSA
      - auditor: toda la UNSA (solo lectura)
    """
    filtros = filtros or {}
    query = "SELECT id, email, nombre, rol, facultad, departamento, created_at FROM usuarios WHERE activo = 1"
    params = []

    # Control de acceso basado en rol (RBAC / Context Guardrail)
    if solicitante_rol in ("docente", "administrativo", "estudiante"):
        query += " AND id = ?"
        params.append(solicitante_id)
    elif solicitante_rol == "jefe":
        if solicitante_facultad:
            query += " AND facultad = ?"
            params.append(solicitante_facultad)

    # Filtros opcionales
    if "rol" in filtros and filtros["rol"]:
        query += " AND rol = ?"
        params.append(filtros["rol"])

    if "facultad" in filtros and filtros["facultad"]:
        query += " AND facultad LIKE ?"
        params.append(f"%{filtros['facultad']}%")

    if "departamento" in filtros and filtros["departamento"]:
        query += " AND departamento LIKE ?"
        params.append(f"%{filtros['departamento']}%")

    if "antiguedad_dias" in filtros and filtros["antiguedad_dias"] is not None:
        limite_dias = int(filtros["antiguedad_dias"])
        fecha_corte = (datetime.now() - timedelta(days=limite_dias)).strftime("%Y-%m-%d")
        query += " AND created_at >= ?"
        params.append(fecha_corte)

    with get_db_connection() as conn:
        usuarios = conn.execute(query, params).fetchall()

        # Filtro adicional si se pide por estado de formación
        if "estado_formacion" in filtros and filtros["estado_formacion"]:
            estado_req = filtros["estado_formacion"]
            filtrados = []
            for u in usuarios:
                check = conn.execute(
                    "SELECT 1 FROM formacion_usuario WHERE user_id = ? AND estado = ? LIMIT 1",
                    (u["id"], estado_req)
                ).fetchone()
                if check:
                    filtrados.append(u)
            usuarios = filtrados

    return {
        "status": "success",
        "total": len(usuarios),
        "usuarios": usuarios
    }

# ==============================================================================
# HERRAMIENTA 6: enviar_correo_masivo
# ==============================================================================
@mcp.tool()
def enviar_correo_masivo(user_ids: List[str], asunto: str, cuerpo: str, remitente_id: str = "admin") -> dict:
    """
    Envía correo a una lista de usuarios. Por cada usuario, invoca al MCP Correo (mock persistente).
    Devuelve {total, enviados, fallidos, lote_id}.
    """
    if not user_ids:
        return {"status": "error", "message": "Lista de destinatarios vacía"}

    with get_db_connection() as conn:
        placeholders = ",".join(["?"] * len(user_ids))
        encontrados = conn.execute(
            f"SELECT id, email, nombre FROM usuarios WHERE id IN ({placeholders}) OR email IN ({placeholders})",
            user_ids + user_ids
        ).fetchall()

    usuarios = list(encontrados)
    ids_o_emails_encontrados = {u["id"] for u in usuarios} | {u["email"] for u in usuarios if u["email"]}

    # Aceptar destinatarios con formato de correo directo (@) aunque no existan en la tabla usuarios
    for item in user_ids:
        if item not in ids_o_emails_encontrados and "@" in str(item):
            usuarios.append({
                "id": str(item),
                "email": str(item),
                "nombre": str(item).split("@")[0]
            })

    if not usuarios:
        return {"status": "error", "message": "Ninguno de los usuarios o correos especificados fue encontrado"}

    lote_id = f"lote_{uuid.uuid4().hex[:8]}"

    # Orquestación con el MCP Correo
    resultado_correo = correo_enviar(
        destinatarios=usuarios,
        asunto=asunto,
        cuerpo=cuerpo,
        remitente_id=remitente_id,
        lote_id=lote_id
    )

    return {
        "status": "success",
        "lote_id": lote_id,
        "total": len(usuarios),
        "enviados": resultado_correo.get("enviados", 0),
        "fallidos": resultado_correo.get("fallidos", 0),
        "asunto": asunto,
        "destinatarios_nombres": [u["nombre"] for u in usuarios]
    }

# ==============================================================================
# HERRAMIENTA AUXILIAR: generar_certificado
# ==============================================================================
@mcp.tool()
def generar_certificado(user_id: str, formacion_id: str) -> dict:
    """
    Genera PDF del certificado y guarda evidencia en MCP Evidencias (mock persistente con SHA256).
    """
    with get_db_connection() as conn:
        user = conn.execute("SELECT id, nombre, email FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        curso = conn.execute("SELECT id, titulo, control_iso FROM formaciones WHERE id = ?", (formacion_id,)).fetchone()

        if not user or not curso:
            return {"status": "error", "message": "Usuario o formación no válidos"}

        now = datetime.now().strftime("%Y-%m-%d")
        cert_name = f"Certificado_{curso['id']}_{user_id}.pdf"
        cert_url = f"https://pims.unsa.edu.pe/certificados/{cert_name}"

        # Actualizar en formación usuario
        conn.execute(
            """
            UPDATE formacion_usuario
            SET estado = 'completado', fecha_completado = ?, certificado_url = ?
            WHERE user_id = ? AND formacion_id = ?
            """,
            (now, cert_url, user_id, formacion_id)
        )

    # Orquestación con MCP Evidencias
    evidencia_res = evidencia_guardar(
        user_id=user_id,
        archivo=cert_name,
        control_iso=curso["control_iso"],
        contenido=f"CERTIFICADO UNSA PIMS\nOtorgado a: {user['nombre']}\nPor completar: {curso['titulo']}\nFecha: {now}"
    )

    return {
        "status": "success",
        "certificado_url": cert_url,
        "usuario": user["nombre"],
        "curso": curso["titulo"],
        "control_iso": curso["control_iso"],
        "evidencia": evidencia_res
    }

if __name__ == "__main__":
    print("Iniciando servidor FastMCP PIMS-UNSA...")
    if hasattr(mcp, "run"):
        mcp.run()
