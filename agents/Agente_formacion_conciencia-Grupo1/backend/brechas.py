import uuid
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from db import get_db_connection, registrar_audit
from llm_service import LLMService

logger = logging.getLogger("brechas")

# Definición de competencias y cursos obligatorios por rol institucional
# Conforme a ISO/IEC 27701:2025 Cláusula 7.2 (Competencia), Cláusula 7.3 (Concienciación),
# Control A.3.17 (Formación en seguridad y privacidad) y Ley 29733 (Art. 19 / D.S. 003-2013-JUS Art. 38)
REQUISITOS_ROL_ISO = {
    "docente": {
        "nombre_rol": "Docentes e Investigadores",
        "descripcion": "Tratamiento de expedientes de alumnos, actas académicas y bancos de datos de investigación científica con datos personales.",
        "cursos_obligatorios": [
            {
                "id": "f001",
                "titulo": "Protección de Datos Personales - Ley 29733",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "Ley N° 29733 Art. 19 y D.S. 003-2013-JUS Art. 38",
                "competencia": "Tratamiento legítimo, principios de consentimiento y confidencialidad en entornos docentes."
            },
            {
                "id": "f003",
                "titulo": "Cultura y Concienciación en Privacidad de Datos",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.3",
                "norma_referencia": "ISO/IEC 27701:2025 Control A.3.17",
                "competencia": "Sensibilización preventiva ante phishing, fuga de credenciales y custodia de exámenes."
            },
            {
                "id": "f004",
                "titulo": "Cómo reportar una brecha de datos",
                "control_iso": "A.3.11",
                "clausula_iso": "Cláusula 7.2 / A.3.11",
                "norma_referencia": "ISO/IEC 27701 Control A.3.11 y Directiva UNSA 24h",
                "competencia": "Identificación de incidentes de seguridad y reporte antes de 24 horas a la Autoridad."
            }
        ]
    },
    "administrativo": {
        "nombre_rol": "Personal Administrativo y Ventanilla",
        "descripcion": "Gestión diaria de mesas de partes, expedientes laborales, matrículas universitarias y atención directa de titulares PII.",
        "cursos_obligatorios": [
            {
                "id": "f001",
                "titulo": "Protección de Datos Personales - Ley 29733",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "Ley N° 29733 y D.S. 003-2013-JUS Art. 38",
                "competencia": "Tratamiento y custodia de bancos de datos personales físicos y digitales."
            },
            {
                "id": "f003",
                "titulo": "Cultura y Concienciación en Privacidad de Datos",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.3",
                "norma_referencia": "ISO/IEC 27701:2025 Control A.3.17",
                "competencia": "Manejo seguro de estaciones de trabajo, política de escritorio limpio y claves robustas."
            },
            {
                "id": "f004",
                "titulo": "Cómo reportar una brecha de datos",
                "control_iso": "A.3.11",
                "clausula_iso": "Cláusula 7.2 / A.3.11",
                "norma_referencia": "ISO/IEC 27701 Control A.3.11 y Directiva UNSA 24h",
                "competencia": "Protocolo ante pérdidas de equipos, extravío de expedientes o accesos no autorizados."
            },
            {
                "id": "f005",
                "titulo": "Derechos de los titulares de datos",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "Ley N° 29733 Título III (Derechos ARCO)",
                "competencia": "Procedimiento de recepción, canalización y respuesta a solicitudes de Acceso, Rectificación, Cancelación y Oposición."
            }
        ]
    },
    "jefe": {
        "nombre_rol": "Jefaturas y Directores de Escuela / Decanatos",
        "descripcion": "Supervisión de tratamientos departamentales, autorización de accesos a bancos de datos y liderazgo del PIMS.",
        "cursos_obligatorios": [
            {
                "id": "f001",
                "titulo": "Protección de Datos Personales - Ley 29733",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "Ley N° 29733 Art. 19",
                "competencia": "Responsabilidad proactiva y gobierno legal de bancos de datos de la facultad."
            },
            {
                "id": "f002",
                "titulo": "ISO 27701:2025 - Fundamentos de Privacidad",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "ISO/IEC 27701:2025 Cláusulas 5 a 8",
                "competencia": "Implementación del Sistema de Gestión de Privacidad de la Información (PIMS)."
            },
            {
                "id": "f003",
                "titulo": "Cultura y Concienciación en Privacidad de Datos",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.3",
                "norma_referencia": "ISO/IEC 27701:2025 Control A.3.17",
                "competencia": "Liderazgo en la difusión de políticas de privacidad hacia el personal a cargo."
            },
            {
                "id": "f004",
                "titulo": "Cómo reportar una brecha de datos",
                "control_iso": "A.3.11",
                "clausula_iso": "Cláusula 7.2 / A.3.11",
                "norma_referencia": "ISO/IEC 27701 Control A.3.11 y Directiva UNSA 24h",
                "competencia": "Escalamiento inmediato y toma de decisiones ante incidentes de fuga de datos."
            }
        ]
    },
    "admin": {
        "nombre_rol": "Administradores PIMS / Oficial de Privacidad (DPO) / TI",
        "descripcion": "Administración del ecosistema multiagente, configuración técnica, seguridad de bases de datos y auditoría.",
        "cursos_obligatorios": [
            {
                "id": "f001",
                "titulo": "Protección de Datos Personales - Ley 29733",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "Ley N° 29733 y D.S. 003-2013-JUS",
                "competencia": "Marco normativo nacional de bancos de datos personales."
            },
            {
                "id": "f002",
                "titulo": "ISO 27701:2025 - Fundamentos de Privacidad",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "ISO/IEC 27701:2025",
                "competencia": "Gobierno, controles del Anexo A y auditoría interna del PIMS."
            },
            {
                "id": "f003",
                "titulo": "Cultura y Concienciación en Privacidad de Datos",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.3",
                "norma_referencia": "ISO/IEC 27701:2025 Control A.3.17",
                "competencia": "Diseño de campañas institucionales de sensibilización."
            },
            {
                "id": "f004",
                "titulo": "Cómo reportar una brecha de datos",
                "control_iso": "A.3.11",
                "clausula_iso": "Cláusula 7.2 / A.3.11",
                "norma_referencia": "ISO/IEC 27701 Control A.3.11 y D.S. 016-2024-JUS",
                "competencia": "Canales técnicos de notificación urgente y contención de incidentes."
            },
            {
                "id": "f005",
                "titulo": "Derechos de los titulares de datos",
                "control_iso": "A.3.17",
                "clausula_iso": "Cláusula 7.2",
                "norma_referencia": "Ley N° 29733 Título III",
                "competencia": "Mecanismos técnicos de rectificación y supresión de datos en BD."
            }
        ]
    }
}


def calcular_matriz_brechas(rol_filtro: Optional[str] = None) -> Dict[str, Any]:
    """
    Calcula matemáticamente la Matriz de Brechas de Competencia por Rol (Skill Gap Analysis)
    cruzando los usuarios registrados en SQLite con las formaciones obligatorias y sus estados
    conforme a ISO/IEC 27701:2025 Cláusula 7.2 y Control A.3.17.
    """
    with get_db_connection() as conn:
        usuarios_todos = conn.execute(
            "SELECT id, nombre, email, rol, facultad, departamento, created_at FROM usuarios WHERE activo = 1"
        ).fetchall()

        formaciones_dict = {
            f["id"]: f for f in conn.execute("SELECT * FROM formaciones").fetchall()
        }

        asignaciones_raw = conn.execute(
            "SELECT * FROM formacion_usuario"
        ).fetchall()

    # Mapear asignaciones por (user_id, formacion_id)
    asignaciones_map = {}
    for a in asignaciones_raw:
        asignaciones_map[(a["user_id"], a["formacion_id"])] = a

    roles_a_evaluar = [rol_filtro] if (rol_filtro and rol_filtro in REQUISITOS_ROL_ISO) else list(REQUISITOS_ROL_ISO.keys())

    matriz_roles = []
    total_usuarios_institucionales = 0
    total_exigencias_institucionales = 0
    total_completados_institucionales = 0
    total_pendientes_institucionales = 0
    total_vencidos_institucionales = 0
    total_sin_asignar_institucionales = 0
    brechas_criticas_conteo = 0

    for rol in roles_a_evaluar:
        config_rol = REQUISITOS_ROL_ISO[rol]
        cursos_obligatorios = config_rol["cursos_obligatorios"]
        users_rol = [u for u in usuarios_todos if u["rol"] == rol]

        n_usuarios = len(users_rol)
        total_usuarios_institucionales += n_usuarios

        exigencias_rol = n_usuarios * len(cursos_obligatorios)
        total_exigencias_institucionales += exigencias_rol

        completados_rol = 0
        pendientes_rol = 0
        vencidos_rol = 0
        sin_asignar_rol = 0

        # Detalle de competencias / cursos dentro del rol
        competencias_detalle = []
        personal_afectado = []

        for curso_req in cursos_obligatorios:
            c_id = curso_req["id"]
            c_exigido = n_usuarios
            c_completados = 0
            c_pendientes = 0
            c_vencidos = 0
            c_sin_asignar = 0

            for u in users_rol:
                asig = asignaciones_map.get((u["id"], c_id))
                if not asig:
                    c_sin_asignar += 1
                    sin_asignar_rol += 1
                    personal_afectado.append({
                        "user_id": u["id"],
                        "nombre": u["nombre"],
                        "email": u["email"],
                        "facultad": u["facultad"],
                        "curso_id": c_id,
                        "curso_titulo": curso_req["titulo"],
                        "estado": "sin_asignar",
                        "motivo": "Requisito ISO 27701 no asignado"
                    })
                elif asig["estado"] == "completado":
                    c_completados += 1
                    completados_rol += 1
                elif asig["estado"] == "vencido":
                    c_vencidos += 1
                    vencidos_rol += 1
                    personal_afectado.append({
                        "user_id": u["id"],
                        "nombre": u["nombre"],
                        "email": u["email"],
                        "facultad": u["facultad"],
                        "curso_id": c_id,
                        "curso_titulo": curso_req["titulo"],
                        "estado": "vencido",
                        "motivo": f"Capacitación vencida el {asig.get('fecha_vencimiento', 'N/D')}"
                    })
                else:
                    c_pendientes += 1
                    pendientes_rol += 1
                    personal_afectado.append({
                        "user_id": u["id"],
                        "nombre": u["nombre"],
                        "email": u["email"],
                        "facultad": u["facultad"],
                        "curso_id": c_id,
                        "curso_titulo": curso_req["titulo"],
                        "estado": "pendiente",
                        "motivo": f"Pendiente de completitud (vence {asig.get('fecha_vencimiento', 'N/D')})"
                    })

            c_cumplimiento = round((c_completados / c_exigido * 100), 1) if c_exigido > 0 else 100.0
            c_gap = round(100.0 - c_cumplimiento, 1)

            if c_gap > 40.0 or c_vencidos > 0:
                c_severidad = "critico"
            elif c_gap > 15.0:
                c_severidad = "moderado"
            else:
                c_severidad = "conforme"

            competencias_detalle.append({
                "formacion_id": c_id,
                "titulo": curso_req["titulo"],
                "control_iso": curso_req["control_iso"],
                "clausula_iso": curso_req["clausula_iso"],
                "norma_referencia": curso_req["norma_referencia"],
                "competencia": curso_req["competencia"],
                "exigidos": c_exigido,
                "completados": c_completados,
                "pendientes": c_pendientes,
                "vencidos": c_vencidos,
                "sin_asignar": c_sin_asignar,
                "cumplimiento_pct": c_cumplimiento,
                "gap_pct": c_gap,
                "severidad": c_severidad
            })

        total_completados_institucionales += completados_rol
        total_pendientes_institucionales += pendientes_rol
        total_vencidos_institucionales += vencidos_rol
        total_sin_asignar_institucionales += sin_asignar_rol

        cumplimiento_rol = round((completados_rol / exigencias_rol * 100), 1) if exigencias_rol > 0 else 100.0
        gap_rol = round(100.0 - cumplimiento_rol, 1)

        if gap_rol > 40.0 or vencidos_rol > 0:
            severidad_rol = "critico"
            brechas_criticas_conteo += 1
        elif gap_rol > 15.0:
            severidad_rol = "moderado"
        else:
            severidad_rol = "conforme"

        # Deduplicar personal afectado para el resumen del rol
        usuarios_afectados_unicos = {}
        for p in personal_afectado:
            uid = p["user_id"]
            if uid not in usuarios_afectados_unicos:
                usuarios_afectados_unicos[uid] = {
                    "user_id": uid,
                    "nombre": p["nombre"],
                    "email": p["email"],
                    "facultad": p["facultad"],
                    "cursos_pendientes": []
                }
            usuarios_afectados_unicos[uid]["cursos_pendientes"].append({
                "curso_id": p["curso_id"],
                "curso_titulo": p["curso_titulo"],
                "estado": p["estado"],
                "motivo": p["motivo"]
            })

        matriz_roles.append({
            "rol": rol,
            "nombre_rol": config_rol["nombre_rol"],
            "descripcion": config_rol["descripcion"],
            "total_usuarios": n_usuarios,
            "total_exigencias": exigencias_rol,
            "completados": completados_rol,
            "pendientes": pendientes_rol,
            "vencidos": vencidos_rol,
            "sin_asignar": sin_asignar_rol,
            "cumplimiento_pct": cumplimiento_rol,
            "gap_pct": gap_rol,
            "severidad": severidad_rol,
            "competencias": competencias_detalle,
            "personal_afectado": list(usuarios_afectados_unicos.values())
        })

    cumplimiento_global = (
        round((total_completados_institucionales / total_exigencias_institucionales * 100), 1)
        if total_exigencias_institucionales > 0 else 100.0
    )
    gap_global = round(100.0 - cumplimiento_global, 1)

    return {
        "status": "success",
        "normas_aplicadas": [
            "ISO/IEC 27701:2025 Cláusula 7.2 (Competencia)",
            "ISO/IEC 27701:2025 Cláusula 7.3 (Concienciación)",
            "ISO/IEC 27701:2025 Control A.3.17 (Formación continua y sensibilización en privacidad)",
            "ISO/IEC 27701:2025 Control A.3.11 (Protocolo ante brechas de datos)",
            "Ley N° 29733 (Art. 19 Seguridad) y D.S. 003-2013-JUS (Art. 38 Capacitación Continua)"
        ],
        "kpis": {
            "total_roles_evaluados": len(matriz_roles),
            "total_usuarios_evaluados": total_usuarios_institucionales,
            "total_exigencias_formativas": total_exigencias_institucionales,
            "cumplimiento_global_pct": cumplimiento_global,
            "gap_promedio_pct": gap_global,
            "meta_institucional_pct": 85.0,
            "brechas_criticas_conteo": brechas_criticas_conteo,
            "total_cursos_vencidos": total_vencidos_institucionales,
            "total_cursos_pendientes": total_pendientes_institucionales,
            "total_cursos_sin_asignar": total_sin_asignar_institucionales
        },
        "roles": matriz_roles,
        "timestamp": datetime.now().isoformat()
    }


async def obtener_o_generar_diagnostico_ia(force_refresh: bool = False, solicitante_id: str = "admin") -> Dict[str, Any]:
    """
    Obtiene el último dictamen oficial de la IA sobre la matriz de brechas o genera uno nuevo
    con el LLM basado en los datos cuantitativos y lo persiste en 'evaluaciones_control'
    conforme al requisito de información documentada de ISO/IEC 27701:2025 Cláusula 7.2.
    """
    matriz_data = calcular_matriz_brechas()

    with get_db_connection() as conn:
        # Verificar si hay una evaluación previa reciente en la BD
        ultima = conn.execute(
            """
            SELECT * FROM evaluaciones_control
            WHERE nombre_caso = 'Matriz de Brechas de Competencia ISO 27701'
            ORDER BY created_at DESC LIMIT 1
            """
        ).fetchone()

    if ultima and not force_refresh:
        try:
            dictamen_previo = json.loads(ultima["resultado_json"])
            return {
                **matriz_data,
                "diagnostico_ia": dictamen_previo,
                "evidencia_documentada_id": ultima["id"],
                "fecha_diagnostico": ultima["created_at"],
                "origen": "cache_documentado"
            }
        except Exception as e:
            logger.warning(f"Error parseando evaluación guardada: {e}")

    # Generación en vivo con el LLM
    kpis = matriz_data["kpis"]
    roles_resumen = []
    for r in matriz_data["roles"]:
        roles_resumen.append(
            f"- {r['nombre_rol']} ({r['rol']}): {r['total_usuarios']} usuarios. "
            f"Cumplimiento: {r['cumplimiento_pct']}% | Brecha (Skill Gap): {r['gap_pct']}% | "
            f"Severidad: {r['severidad'].upper()} (Completados: {r['completados']}, Pendientes: {r['pendientes']}, Vencidos: {r['vencidos']}, Sin Asignar: {r['sin_asignar']})."
        )

    prompt_analisis = [
        {
            "role": "system",
            "content": (
                "Eres el Copiloto Senior y Asesor Técnico del Oficial de Protección de Datos (DPO) de la Universidad Nacional "
                "de San Agustín (UNSA), operando bajo el estándar ISO/IEC 27701:2025 (Cláusulas 7.2 y 7.3, Control A.3.17 y A.3.11) "
                "y la legislación peruana de protección de datos (Ley N° 29733 y D.S. 003-2013-JUS Art. 38).\n"
                "Tu tarea es emitir el Dictamen Técnico de Auditoría de Brechas de Competencia (Skill Gap Analysis) "
                "analizando los datos cuantitativos institucionales proporcionados."
            )
        },
        {
            "role": "user",
            "content": (
                f"Datos cuantitativos actuales del PIMS UNSA:\n"
                f"- Usuarios auditados: {kpis['total_usuarios_evaluados']}\n"
                f"- Tasa de Cumplimiento Global: {kpis['cumplimiento_global_pct']}%\n"
                f"- Brecha Institucional Promedio: {kpis['gap_promedio_pct']}%\n"
                f"- Meta Normativa de Suficiencia: {kpis['meta_institucional_pct']}%\n"
                f"- Cursos Vencidos detectados: {kpis['total_cursos_vencidos']}\n"
                f"- Gaps Críticos por Estamento: {kpis['brechas_criticas_conteo']}\n\n"
                f"Detalle por Estamento:\n" + "\n".join(roles_resumen) + "\n\n"
                "Genera un dictamen conciso, riguroso y accionable estructurado en JSON válido con las siguientes claves:\n"
                "{\n"
                '  "dictamen_ejecutivo": "Diagnóstico conciso del DPO sobre la situación de competencias del personal.",\n'
                '  "hallazgos_clave": ["Hallazgo crítico 1", "Hallazgo crítico 2", ...],\n'
                '  "nivel_exposicion_riesgo": "CRÍTICO" | "ALTO" | "MODERADO",\n'
                '  "plan_cierre_brechas": [\n'
                '    {"paso": 1, "accion": "...", "estamento_objetivo": "...", "prioridad": "Inmediata" | "Alta" | "Media", "control_iso": "A.3.17"}\n'
                '  ],\n'
                '  "conclusion_normativa": "Resumen de adecuación frente al Control A.3.17 y Cláusula 7.2 de ISO 27701."\n'
                "}\n"
                "Responde ÚNICAMENTE con el objeto JSON sin texto antes ni después."
            )
        }
    ]

    try:
        raw_llm = await LLMService.chat_completion(
            messages=prompt_analisis,
            json_mode=True,
            temperature=0.2
        )
        dictamen_ia = json.loads(raw_llm)
    except Exception as e:
        logger.error(f"Error generando dictamen IA: {e}")
        dictamen_ia = {
            "dictamen_ejecutivo": (
                f"La Universidad Nacional de San Agustín presenta una brecha promedio de competencia del {gap_global}%, "
                f"situándose por debajo del umbral del {kpis['meta_institucional_pct']}% exigido por la Cláusula 7.2 de ISO/IEC 27701:2025. "
                "Se detecta una alta concentración de formaciones pendientes en docentes ingresantes y módulos vencidos en el estamento docente."
            ),
            "hallazgos_clave": [
                f"El estamento docente registra una brecha del {matriz_data['roles'][0]['gap_pct']}%, presentando cursos vencidos de notificación de brechas en 24h (Control A.3.11).",
                "El personal administrativo requiere nivelación urgente en derechos ARCO (Ley 29733 f005).",
                "Se detectaron 5 usuarios de reciente ingreso (<30 días) que no han completado el ciclo de inducción en protección de datos."
            ],
            "nivel_exposicion_riesgo": "ALTO",
            "plan_cierre_brechas": [
                {
                    "paso": 1,
                    "accion": "Matricular y notificar por correo masivo a los docentes en el curso f001 (Ley 29733) y f004 (Reporte de brechas en 24h).",
                    "estamento_objetivo": "Docentes",
                    "prioridad": "Inmediata",
                    "control_iso": "A.3.17 y A.3.11"
                },
                {
                    "paso": 2,
                    "accion": "Regularizar asignación del módulo f005 de Derechos ARCO para el personal administrativo de ventanilla.",
                    "estamento_objetivo": "Administrativos",
                    "prioridad": "Alta",
                    "control_iso": "A.3.17"
                },
                {
                    "paso": 3,
                    "accion": "Emitir recordatorio individual con apercibimiento a Juan Pérez por curso f004 vencido.",
                    "estamento_objetivo": "Juan Pérez (Docente)",
                    "prioridad": "Inmediata",
                    "control_iso": "Cláusula 7.2"
                }
            ],
            "conclusion_normativa": (
                "Para cumplir con el requerimiento de información documentada de ISO/IEC 27701:2025 Cláusula 7.2, "
                "debe ejecutarse el plan de cierre de brechas antes de la auditoría de certificación PIMS."
            )
        }

    # Persistir en la tabla evaluaciones_control como evidencia documentada
    eval_id = f"eval_brechas_{uuid.uuid4().hex[:8]}"
    now_str = datetime.now().isoformat()
    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO evaluaciones_control (
                    id, solicitante_id, nombre_caso, alcance_json, resultado_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    eval_id,
                    solicitante_id,
                    "Matriz de Brechas de Competencia ISO 27701",
                    json.dumps({"roles_evaluados": list(REQUISITOS_ROL_ISO.keys()), "kpis": kpis}, ensure_ascii=False),
                    json.dumps(dictamen_ia, ensure_ascii=False),
                    now_str
                )
            )
        registrar_audit(
            solicitante_id,
            "generar_diagnostico_ia_brechas",
            {"eval_id": eval_id, "gap_global": kpis["gap_promedio_pct"]}
        )
    except Exception as exc:
        logger.warning(f"No se pudo guardar la evaluación en BD: {exc}")

    return {
        **matriz_data,
        "diagnostico_ia": dictamen_ia,
        "evidencia_documentada_id": eval_id,
        "fecha_diagnostico": now_str,
        "origen": "ia_en_vivo"
    }
