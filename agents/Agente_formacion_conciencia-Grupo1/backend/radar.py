import uuid
import json
import logging
import math
from datetime import datetime
from typing import Optional, Dict, Any, List

from db import get_db_connection, registrar_audit
from llm_service import LLMService

logger = logging.getLogger("radar")

# Estamentos universitarios conforme a la estructura de la UNSA y requisitos formativos
# ISO/IEC 27701:2025 Cláusula 7.2 (Competencia), 7.3 (Toma de Conciencia) y Control A.3.17
ESTAMENTOS_UNSA = {
    "docente": {
        "codigo": "docente",
        "nombre": "Docencia e Investigación",
        "descripcion": "Catedráticos ordinarios, contratados e investigadores que custodian actas, notas y bancos de datos científicos con PII.",
        "cursos_clave": ["f001", "f003", "f004"],
        "peso_ponderado": 0.35,
        "icono": "👨‍🏫"
    },
    "administrativo": {
        "codigo": "administrativo",
        "nombre": "Personal Administrativo y Ventanilla",
        "descripcion": "Personal de mesa de partes, recursos humanos, matrícula, bienestar y biblioteca que opera registros masivos de personas.",
        "cursos_clave": ["f001", "f003", "f005"],
        "peso_ponderado": 0.30,
        "icono": "🏛️"
    },
    "jefe": {
        "codigo": "jefe",
        "nombre": "Jefaturas y Direcciones de Unidad",
        "descripcion": "Directores de escuela, jefes de departamento y decanaturas responsables del gobierno y aprobación del tratamiento de datos.",
        "cursos_clave": ["f001", "f002", "f003", "f004"],
        "peso_ponderado": 0.15,
        "icono": "👔"
    },
    "admin": {
        "codigo": "admin",
        "nombre": "Órganos de Gobierno y Gestión TI",
        "descripcion": "Administradores de red, desarrolladores y comités directivos de la UNSA con acceso privilegiado a la infraestructura PIMS.",
        "cursos_clave": ["f001", "f002", "f003", "f004", "f005"],
        "peso_ponderado": 0.15,
        "icono": "💻"
    },
    "auditor": {
        "codigo": "auditor",
        "nombre": "Control Interno y Auditoría PIMS",
        "descripcion": "Auditores de control posterior y oficiales de cumplimiento encargados de verificar la efectividad de las medidas de seguridad.",
        "cursos_clave": ["f001", "f002", "f004"],
        "peso_ponderado": 0.05,
        "icono": "🛡️"
    }
}

META_COBERTURA_INSTITUCIONAL = 90.0  # Meta del PIMS UNSA (> 90% para certificación)


def calcular_radar_cobertura(estamento_filtro: Optional[str] = None, facultad_filtro: Optional[str] = None) -> Dict[str, Any]:
    """
    Calcula matemáticamente las dimensiones del Gráfico de Radar de Cobertura
    por Estamento Universitario, cruzando el padrón activo en SQLite con las
    asignaciones y completitudes de cursos formativos de privacidad.
    """
    with get_db_connection() as conn:
        # 1. Padrón de usuarios
        query_users = "SELECT id, nombre, email, rol, facultad, departamento, created_at FROM usuarios WHERE activo = 1"
        params_u = []
        if facultad_filtro and facultad_filtro != "todas":
            query_users += " AND facultad = ?"
            params_u.append(facultad_filtro)
        usuarios_todos = conn.execute(query_users, params_u).fetchall()

        # 2. Asignaciones de formación
        asignaciones_raw = conn.execute(
            """
            SELECT fu.id, fu.user_id, fu.formacion_id, fu.estado, fu.fecha_asignacion, fu.fecha_completado,
                   f.titulo, f.control_iso
            FROM formacion_usuario fu
            JOIN formaciones f ON fu.formacion_id = f.id
            """
        ).fetchall()

    # Mapeo de asignaciones por usuario
    asignaciones_por_usuario: Dict[str, List[Dict[str, Any]]] = {}
    for asig in asignaciones_raw:
        u_id = asig["user_id"]
        asignaciones_por_usuario.setdefault(u_id, []).append(asig)

    # Agrupar usuarios por rol / estamento
    usuarios_por_rol: Dict[str, List[Dict[str, Any]]] = {}
    for u in usuarios_todos:
        r = u["rol"]
        usuarios_por_rol.setdefault(r, []).append(u)

    estamentos_metricas: List[Dict[str, Any]] = []
    total_usuarios_institucionales = len(usuarios_todos)

    suma_cobertura_ponderada = 0.0
    suma_eficacia_ponderada = 0.0
    peso_acumulado = 0.0

    for codigo_rol, estamento_meta in ESTAMENTOS_UNSA.items():
        if estamento_filtro and estamento_filtro != "todos" and codigo_rol != estamento_filtro:
            continue

        usuarios_estamento = usuarios_por_rol.get(codigo_rol, [])
        padron_total = len(usuarios_estamento)

        if padron_total == 0:
            estamentos_metricas.append({
                "codigo": codigo_rol,
                "nombre": estamento_meta["nombre"],
                "descripcion": estamento_meta["descripcion"],
                "icono": estamento_meta["icono"],
                "padron_total": 0,
                "inscritos": 0,
                "completados": 0,
                "pendientes": 0,
                "vencidos": 0,
                "sin_asignar": 0,
                "cobertura_pct": 0.0,
                "eficacia_pct": 0.0,
                "cobertura_ley29733_pct": 0.0,
                "cobertura_iso27701_pct": 0.0,
                "meta_pct": META_COBERTURA_INSTITUCIONAL,
                "gap_pct": META_COBERTURA_INSTITUCIONAL,
                "severidad": "optimo",
                "estado_radar": "sin_personal",
                "usuarios": []
            })
            continue

        # Conteo de personal alcanzado
        usuarios_con_asignacion = 0
        usuarios_con_completados = 0
        usuarios_con_pendientes = 0
        usuarios_con_vencidos = 0
        usuarios_sin_asignacion = 0

        usuarios_con_ley29733 = 0
        usuarios_con_iso27701 = 0

        for u in usuarios_estamento:
            u_asigs = asignaciones_por_usuario.get(u["id"], [])
            if not u_asigs:
                usuarios_sin_asignacion += 1
                continue

            usuarios_con_asignacion += 1
            has_completado = any(a["estado"] == "completado" for a in u_asigs)
            has_pendiente = any(a["estado"] == "pendiente" for a in u_asigs)
            has_vencido = any(a["estado"] == "vencido" for a in u_asigs)

            if has_completado:
                usuarios_con_completados += 1
            if has_pendiente:
                usuarios_con_pendientes += 1
            if has_vencido:
                usuarios_con_vencidos += 1

            if any(a["formacion_id"] == "f001" and a["estado"] == "completado" for a in u_asigs):
                usuarios_con_ley29733 += 1
            if any(a["formacion_id"] in ("f002", "f003") and a["estado"] == "completado" for a in u_asigs):
                usuarios_con_iso27701 += 1

        cobertura_pct = round((usuarios_con_asignacion / padron_total) * 100, 1)
        eficacia_pct = round((usuarios_con_completados / padron_total) * 100, 1)

        cob_ley = round((usuarios_con_ley29733 / padron_total) * 100, 1)
        cob_iso = round((usuarios_con_iso27701 / padron_total) * 100, 1)

        gap_pct = max(0.0, round(META_COBERTURA_INSTITUCIONAL - cobertura_pct, 1))

        if cobertura_pct >= 90.0:
            severidad = "optimo"
            estado_radar = "Excelente"
        elif cobertura_pct >= 65.0:
            severidad = "moderado"
            estado_radar = "Aceptable"
        elif cobertura_pct >= 40.0:
            severidad = "alerta"
            estado_radar = "En Alerta"
        else:
            severidad = "critico"
            estado_radar = "Crítico / Rezagado"

        peso = estamento_meta["peso_ponderado"]
        suma_cobertura_ponderada += (cobertura_pct * peso)
        suma_eficacia_ponderada += (eficacia_pct * peso)
        peso_acumulado += peso

        estamentos_metricas.append({
            "codigo": codigo_rol,
            "nombre": estamento_meta["nombre"],
            "descripcion": estamento_meta["descripcion"],
            "icono": estamento_meta["icono"],
            "padron_total": padron_total,
            "inscritos": usuarios_con_asignacion,
            "completados": usuarios_con_completados,
            "pendientes": usuarios_con_pendientes,
            "vencidos": usuarios_con_vencidos,
            "sin_asignar": usuarios_sin_asignacion,
            "cobertura_pct": cobertura_pct,
            "eficacia_pct": eficacia_pct,
            "cobertura_ley29733_pct": cob_ley,
            "cobertura_iso27701_pct": cob_iso,
            "meta_pct": META_COBERTURA_INSTITUCIONAL,
            "gap_pct": gap_pct,
            "severidad": severidad,
            "estado_radar": estado_radar,
            "usuarios": [
                {
                    "user_id": u["id"],
                    "nombre": u["nombre"],
                    "facultad": u["facultad"] or "General",
                    "tiene_asignacion": u["id"] in asignaciones_por_usuario,
                    "cursos": [
                        {"curso_id": a["formacion_id"], "titulo": a["titulo"], "estado": a["estado"]}
                        for a in asignaciones_por_usuario.get(u["id"], [])
                    ]
                }
                for u in usuarios_estamento
            ]
        })

    cobertura_global_pct = round(suma_cobertura_ponderada / peso_acumulado, 1) if peso_acumulado > 0 else 0.0
    eficacia_global_pct = round(suma_eficacia_ponderada / peso_acumulado, 1) if peso_acumulado > 0 else 0.0

    estamentos_con_gente = [e for e in estamentos_metricas if e["padron_total"] > 0]
    if estamentos_con_gente:
        estamento_lider_obj = max(estamentos_con_gente, key=lambda x: x["cobertura_pct"])
        estamento_rezagado_obj = min(estamentos_con_gente, key=lambda x: x["cobertura_pct"])
        estamento_lider = f"{estamento_lider_obj['nombre']} ({estamento_lider_obj['cobertura_pct']}%)"
        estamento_rezagado = f"{estamento_rezagado_obj['nombre']} ({estamento_rezagado_obj['cobertura_pct']}%)"
    else:
        estamento_lider = "No determinado"
        estamento_rezagado = "No determinado"

    # Cruce por Facultades
    facultades_nombres = ["Ingeniería", "Medicina", "Derecho", "Sociales", "Administración Central"]
    radar_facultades: List[Dict[str, Any]] = []

    for fac in facultades_nombres:
        u_fac = [u for u in usuarios_todos if u["facultad"] == fac]
        p_total = len(u_fac)
        if p_total > 0:
            insc = sum(1 for u in u_fac if u["id"] in asignaciones_por_usuario)
            comp = sum(1 for u in u_fac if any(a["estado"] == "completado" for a in asignaciones_por_usuario.get(u["id"], [])))
            c_pct = round((insc / p_total) * 100, 1)
            e_pct = round((comp / p_total) * 100, 1)
        else:
            insc = 0
            comp = 0
            c_pct = 0.0
            e_pct = 0.0

        radar_facultades.append({
            "facultad": fac,
            "padron_total": p_total,
            "inscritos": insc,
            "completados": comp,
            "cobertura_pct": c_pct,
            "eficacia_pct": e_pct,
            "meta_pct": META_COBERTURA_INSTITUCIONAL
        })

    # Coordenadas para el SVG Radar Chart
    vertices_radar: List[Dict[str, Any]] = []
    total_vertices = len(estamentos_metricas)

    for idx, em in enumerate(estamentos_metricas):
        angulo = (-math.pi / 2) + (2 * math.pi * idx / max(1, total_vertices))
        radio_real = (em["cobertura_pct"] / 100.0) * 110.0
        x_real = round(150 + radio_real * math.cos(angulo), 2)
        y_real = round(150 + radio_real * math.sin(angulo), 2)

        radio_meta = (META_COBERTURA_INSTITUCIONAL / 100.0) * 110.0
        x_meta = round(150 + radio_meta * math.cos(angulo), 2)
        y_meta = round(150 + radio_meta * math.sin(angulo), 2)

        radio_label = 135.0
        x_label = round(150 + radio_label * math.cos(angulo), 2)
        y_label = round(150 + radio_label * math.sin(angulo), 2)

        vertices_radar.append({
            "estamento": em["nombre"],
            "codigo": em["codigo"],
            "icono": em["icono"],
            "valor": em["cobertura_pct"],
            "meta": META_COBERTURA_INSTITUCIONAL,
            "x_real": x_real,
            "y_real": y_real,
            "x_meta": x_meta,
            "y_meta": y_meta,
            "x_label": x_label,
            "y_label": y_label,
            "angulo_deg": round(math.degrees(angulo), 1)
        })

    return {
        "kpis": {
            "cobertura_global_pct": cobertura_global_pct,
            "eficacia_global_pct": eficacia_global_pct,
            "meta_institucional_pct": META_COBERTURA_INSTITUCIONAL,
            "brecha_global_pct": max(0.0, round(META_COBERTURA_INSTITUCIONAL - cobertura_global_pct, 1)),
            "estamento_lider": estamento_lider,
            "estamento_rezagado": estamento_rezagado,
            "total_personal_auditado": total_usuarios_institucionales,
            "total_estamentos_evaluados": len(estamentos_metricas)
        },
        "estamentos": estamentos_metricas,
        "facultades": radar_facultades,
        "radar_chart": {
            "vertices": vertices_radar,
            "centro": {"x": 150, "y": 150},
            "radio_max": 110,
            "anillos": [20, 40, 60, 80, 100]
        },
        "meta_normativa": {
            "control_iso": "Control A.3.17",
            "clausula_iso": "Cláusula 7.2 & 7.3 ISO/IEC 27701:2025",
            "ley_peruana": "Ley N° 29733 Art. 19 y D.S. 003-2013-JUS Art. 38"
        }
    }


async def obtener_o_generar_diagnostico_ia_radar(
    estamento_filtro: Optional[str] = None,
    facultad_filtro: Optional[str] = None,
    force_refresh: bool = False,
    solicitante_id: str = "admin"
) -> Dict[str, Any]:
    """
    Obtiene el diagnóstico de cobertura formativa multiaxial generado
    con el Copiloto IA (Agente #8) y lo persiste en 'evaluaciones_control'.
    """
    radar_data = calcular_radar_cobertura(estamento_filtro, facultad_filtro)

    with get_db_connection() as conn:
        ultima = conn.execute(
            """
            SELECT * FROM evaluaciones_control
            WHERE nombre_caso = 'Radar de Cobertura Formativa ISO 27701'
            ORDER BY created_at DESC LIMIT 1
            """
        ).fetchone()

    if ultima and not force_refresh:
        try:
            dictamen_previo = json.loads(ultima["resultado_json"])
            return {
                **radar_data,
                "diagnostico_ia": dictamen_previo,
                "evidencia_documentada_id": ultima["id"],
                "fecha_diagnostico": ultima["created_at"],
                "origen": "cache_documentado"
            }
        except Exception as e:
            logger.warning(f"Error parseando dictamen de radar guardado: {e}")

    kpis = radar_data["kpis"]
    estamentos_txt = []
    for em in radar_data["estamentos"]:
        estamentos_txt.append(
            f"- {em['nombre']} ({em['codigo']}): {em['padron_total']} personas en padrón. "
            f"Cobertura: {em['cobertura_pct']}% | Eficacia Formativa: {em['eficacia_pct']}% | "
            f"Gap vs Meta: {em['gap_pct']}% | Estado: {em['estado_radar']} "
            f"(Inscritos: {em['inscritos']}, Completados: {em['completados']}, Sin Asignar: {em['sin_asignar']})"
        )

    prompt_analisis = [
        {
            "role": "system",
            "content": (
                "Eres el Copiloto Senior de Protección de Datos Personales y Auditor Líder PIMS de la Universidad Nacional "
                "de San Agustín (UNSA), rigiéndote por la norma internacional ISO/IEC 27701:2025 (Cláusula 7.2 Competencia, "
                "Cláusula 7.3 Toma de Conciencia, Control A.3.17 Formación en Privacidad) y la Ley Peruana de Protección de Datos Personales (Ley N° 29733).\n"
                "Tu objetivo es emitir el Dictamen Multiaxial de Cobertura de Capacitación (Gráfico de Radar) "
                "evaluando el alcance en la masa crítica universitaria de forma rigurosa, cuantitativa y accionable."
            )
        },
        {
            "role": "user",
            "content": (
                f"Datos cuantitativos del Radar de Cobertura PIMS UNSA:\n"
                f"- Cobertura Institucional Ponderada: {kpis['cobertura_global_pct']}%\n"
                f"- Eficacia Formativa Global: {kpis['eficacia_global_pct']}%\n"
                f"- Meta Institucional de Cobertura: {kpis['meta_institucional_pct']}%\n"
                f"- Brecha Global: {kpis['brecha_global_pct']}%\n"
                f"- Estamento Líder: {kpis['estamento_lider']}\n"
                f"- Estamento Rezagado: {kpis['estamento_rezagado']}\n"
                f"- Total de Personal Auditado: {kpis['total_personal_auditado']}\n\n"
                f"Detalle por Estamento Universitario:\n"
                + "\n".join(estamentos_txt) +
                "\n\nInstrucción de Respuesta:\n"
                "Debes devolver EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura:\n"
                "{\n"
                '  "diagnostico_cobertura": "Texto formal de 2 o 3 párrafos evaluando la simetría del polígono de cobertura en el radar, los estamentos con desbalance crítico y el impacto respecto a la meta institucional del 90%.",\n'
                '  "estamento_critico_prioritario": "Nombre del estamento más vulnerable con explicación del riesgo operativo",\n'
                '  "plan_nivelacion_estamental": [\n'
                "    {\n"
                '      "estamento": "Nombre del estamento",\n'
                '      "accion": "Acción formativa correctiva concreta y medible",\n'
                '      "plazo_dias": 15,\n'
                '      "prioridad": "Inmediata" | "Alta" | "Media",\n'
                '      "canal": "LMS UNSA" | "Webinar Presencial" | "Google Forms / Micro-learning"\n'
                "    }\n"
                "  ],\n"
                '  "conclusiones_auditoria": ["Conclusión 1 sobre ISO 27701", "Conclusión 2 sobre Ley 29733"]\n'
                "}"
            )
        }
    ]

    try:
        raw_res = await LLMService.chat_completion(
            messages=prompt_analisis,
            temperature=0.1
        )
        cleaned_json = raw_res.strip()
        if cleaned_json.startswith("```json"):
            cleaned_json = cleaned_json[7:]
        if cleaned_json.startswith("```"):
            cleaned_json = cleaned_json[3:]
        if cleaned_json.endswith("```"):
            cleaned_json = cleaned_json[:-3]
        dictamen_ia = json.loads(cleaned_json.strip())
    except Exception as e:
        logger.error(f"Error generando dictamen IA de radar: {e}")
        dictamen_ia = {
            "diagnostico_cobertura": (
                f"El polígono del Radar de Cobertura refleja una tasa ponderada institucional del {kpis['cobertura_global_pct']}%, "
                f"situándose por debajo de la meta de suficiencia del {kpis['meta_institucional_pct']}%. "
                f"Se detecta una asimetría notable con rezago severo en '{kpis['estamento_rezagado']}', lo cual incumple "
                f"el requisito de masa crítica exigido por el Control A.3.17 y la Cláusula 7.2 de la norma ISO/IEC 27701:2025."
            ),
            "estamento_critico_prioritario": kpis['estamento_rezagado'],
            "plan_nivelacion_estamental": [
                {
                    "estamento": "Docencia e Investigación",
                    "accion": "Convocatoria masiva obligatoria y micro-evaluaciones en línea para regularizar docentes pendientes.",
                    "plazo_dias": 15,
                    "prioridad": "Inmediata",
                    "canal": "Google Forms / Micro-learning"
                },
                {
                    "estamento": "Personal Administrativo y Ventanilla",
                    "accion": "Taller práctico sobre atención de solicitudes de derechos ARCO y principio de seguridad de la Ley 29733.",
                    "plazo_dias": 20,
                    "prioridad": "Alta",
                    "canal": "Webinar Presencial"
                }
            ],
            "conclusiones_auditoria": [
                "Existe riesgo de no conformidad mayor en auditoría de certificación ISO 27701 si el polígono de cobertura no alcanza el 90%.",
                "El cumplimiento de la Ley 29733 demanda evidenciar que el personal que accede a bancos de datos cuente con inducción comprobada."
            ]
        }

    eval_id = f"eval_radar_{uuid.uuid4().hex[:8]}"
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
                    "Radar de Cobertura Formativa ISO 27701",
                    json.dumps({"kpis": kpis, "estamentos": [e["codigo"] for e in radar_data["estamentos"]]}, ensure_ascii=False),
                    json.dumps(dictamen_ia, ensure_ascii=False),
                    now_str
                )
            )
        registrar_audit(
            solicitante_id,
            "generar_diagnostico_ia_radar",
            {"eval_id": eval_id, "cobertura_global": kpis["cobertura_global_pct"]}
        )
    except Exception as exc:
        logger.warning(f"No se pudo guardar la evaluación de radar en BD: {exc}")

    return {
        **radar_data,
        "diagnostico_ia": dictamen_ia,
        "evidencia_documentada_id": eval_id,
        "fecha_diagnostico": now_str,
        "origen": "llm_en_vivo"
    }
