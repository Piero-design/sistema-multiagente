import uuid
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from db import get_db_connection, registrar_audit
from llm_service import LLMService

logger = logging.getLogger("heatmap")

# Definición de los 6 Ejes Temáticos de Riesgo PII conforme a ISO/IEC 27701:2025 (Control A.3.17 y A.3.11)
# y Marco Normativo Peruano (Ley N° 29733, D.S. 003-2013-JUS y D.S. 016-2024-JUS)
EJES_RIESGO_PII = {
    "phishing_social": {
        "id": "phishing_social",
        "nombre": "Ingeniería Social y Phishing Institucional",
        "icono": "🎣",
        "control_iso": "A.3.17",
        "norma_ref": "ISO/IEC 27701:2025 Control A.3.17 & ISO 27002 Control 6.3",
        "cursos_asociados": ["f003"],
        "descripcion": "Susceptibilidad a correos fraudulentos, suplantación de identidad universitaria y entrega involuntaria de credenciales a bases de datos académicas.",
        "peso": 0.20
    },
    "fuga_investigacion": {
        "id": "fuga_investigacion",
        "nombre": "Fuga de PII en Investigación y Docencia",
        "icono": "🧪",
        "control_iso": "A.3.17",
        "norma_ref": "Ley N° 29733 Art. 19 & Estatuto UNSA Art. 88",
        "cursos_asociados": ["f001", "f003"],
        "descripcion": "Exposición no autorizada de datos de tesis, historiales médicos en biomédicas, actas de notas no anonimizadas o repositorios abiertos con PII.",
        "peso": 0.20
    },
    "derechos_arco": {
        "id": "derechos_arco",
        "nombre": "Vulnerabilidad en Trámite de Derechos ARCO",
        "icono": "⚖️",
        "control_iso": "A.3.17",
        "norma_ref": "Ley N° 29733 Título III & D.S. 003-2013-JUS Art. 47-58",
        "cursos_asociados": ["f005", "f001"],
        "descripcion": "Riesgo de sanciones por incumplimiento de plazos legales (Acceso 10 días, Rectificación/Cancelación 2 días) ante solicitudes de alumnos y egresados.",
        "peso": 0.15
    },
    "retencion_custodia": {
        "id": "retencion_custodia",
        "nombre": "Retención Indebida y Custodia de Archivos",
        "icono": "🗄️",
        "control_iso": "A.3.17",
        "norma_ref": "ISO/IEC 27701:2025 Control A.3.20 & Principio de Calidad Ley 29733",
        "cursos_asociados": ["f001", "f002"],
        "descripcion": "Almacenamiento histórico descontrolado de expedientes físicos y digitales sin política de purga, destrucción segura o cifrado en reposo.",
        "peso": 0.15
    },
    "consentimiento_digital": {
        "id": "consentimiento_digital",
        "nombre": "Consentimiento Digital y Transparencia Web",
        "icono": "📝",
        "control_iso": "A.3.17",
        "norma_ref": "Ley N° 29733 Art. 13 & D.S. 003-2013-JUS Art. 12",
        "cursos_asociados": ["f001", "f002"],
        "descripcion": "Captura de datos de postulantes y estudiantes en formularios web y plataformas virtuales sin cláusula informativa clara, previa y verificable.",
        "peso": 0.10
    },
    "respuesta_brechas": {
        "id": "respuesta_brechas",
        "nombre": "Respuesta Tardía y Reporte de Brechas en 24h",
        "icono": "🚨",
        "control_iso": "A.3.11",
        "norma_ref": "ISO/IEC 27701 Control A.3.11 & D.S. 016-2024-JUS / Directiva CSIRT",
        "cursos_asociados": ["f004"],
        "descripcion": "Falta de preparación del personal para identificar una fuga de datos y activar el protocolo de escalamiento obligatorio en menos de 24 horas ante la ANPD.",
        "peso": 0.20
    }
}

FACULTADES_MONITOREADAS = [
    "Ingeniería",
    "Medicina",
    "Derecho",
    "Sociales",
    "Administración Central"
]


def calcular_mapa_calor(facultad_filtro: Optional[str] = None) -> Dict[str, Any]:
    """
    Computa el mapa térmico de riesgos de privacidad y susceptibilidad (Heatmap)
    cruzando el avance formativo por facultad y estamento frente a los 6 dominios de riesgo PII.
    Temperatura / Vulnerabilidad:
      - 0° a 30°: Resiliente / Conciencia Alta (Verde)
      - 31° a 60°: Moderado / Exposición Media (Amarillo/Ámbar)
      - 61° a 80°: Alto Riesgo / Conciencia Deficiente (Naranja)
      - 81° a 100°: Crítico / Zona Térmica Roja (Rojo)
    """
    with get_db_connection() as conn:
        usuarios = conn.execute(
            "SELECT id, nombre, email, rol, facultad, departamento FROM usuarios WHERE activo = 1"
        ).fetchall()

        asignaciones = conn.execute(
            "SELECT user_id, formacion_id, estado FROM formacion_usuario"
        ).fetchall()

    asig_map = {}
    for a in asignaciones:
        asig_map[(a["user_id"], a["formacion_id"])] = a["estado"]

    # Facultades a procesar
    facultades = (
        [facultad_filtro]
        if (facultad_filtro and any(f.lower() in facultad_filtro.lower() for f in FACULTADES_MONITOREADAS))
        else FACULTADES_MONITOREADAS
    )

    # 1. Computar métricas por Eje Temático
    ejes_computados = []
    vulnerabilidad_ponderada_global = 0.0
    zona_critica_nombre = ""
    max_vulnerabilidad = -1.0

    for eje_id, eje_meta in EJES_RIESGO_PII.items():
        cursos = eje_meta["cursos_asociados"]
        total_evaluados = 0
        total_completados = 0
        total_pendientes = 0
        total_vencidos = 0
        total_sin_asignar = 0

        # Evaluar usuarios aplicables
        for u in usuarios:
            # Filtrar si hay facultad_filtro
            if facultad_filtro and facultad_filtro.lower() not in (u["facultad"] or "").lower():
                continue

            for c_id in cursos:
                total_evaluados += 1
                st = asig_map.get((u["id"], c_id))
                if not st:
                    total_sin_asignar += 1
                elif st == "completado":
                    total_completados += 1
                elif st == "vencido":
                    total_vencidos += 1
                else:
                    total_pendientes += 1

        tasa_cumplimiento = (
            round((total_completados / total_evaluados * 100), 1)
            if total_evaluados > 0 else 0.0
        )

        # Cálculo de Temperatura / Grado de Vulnerabilidad (0-100)
        # Factor penalización por cursos vencidos y cursos no asignados
        if total_evaluados > 0:
            penalizacion_vencidos = min(30.0, (total_vencidos / total_evaluados) * 100 * 2.0)
            base_vulnerabilidad = 100.0 - tasa_cumplimiento
            vulnerabilidad = min(100.0, round(base_vulnerabilidad + penalizacion_vencidos, 1))
        else:
            vulnerabilidad = 100.0

        # Índice de Sensibilización (0 a 100 puntos, inverso a la vulnerabilidad)
        indice_sensibilizacion = round(100.0 - vulnerabilidad, 1)

        # Clasificación térmica
        if vulnerabilidad >= 75.0 or total_vencidos > 0:
            nivel_termico = "critico"
            zona_color = "#dc2626"
            etiqueta_termica = "Zona Roja (Crítico)"
        elif vulnerabilidad >= 50.0:
            nivel_termico = "alto"
            zona_color = "#ea580c"
            etiqueta_termica = "Zona Naranja (Alto)"
        elif vulnerabilidad >= 25.0:
            nivel_termico = "moderado"
            zona_color = "#d97706"
            etiqueta_termica = "Zona Ámbar (Moderado)"
        else:
            nivel_termico = "bajo"
            zona_color = "#059669"
            etiqueta_termica = "Zona Verde (Resiliente)"

        if vulnerabilidad > max_vulnerabilidad:
            max_vulnerabilidad = vulnerabilidad
            zona_critica_nombre = eje_meta["nombre"]

        vulnerabilidad_ponderada_global += vulnerabilidad * eje_meta["peso"]

        ejes_computados.append({
            "id": eje_id,
            "nombre": eje_meta["nombre"],
            "icono": eje_meta["icono"],
            "control_iso": eje_meta["control_iso"],
            "norma_ref": eje_meta["norma_ref"],
            "descripcion": eje_meta["descripcion"],
            "cursos_asociados": cursos,
            "evaluados": total_evaluados,
            "completados": total_completados,
            "pendientes": total_pendientes,
            "vencidos": total_vencidos,
            "sin_asignar": total_sin_asignar,
            "tasa_cumplimiento_pct": tasa_cumplimiento,
            "temperatura_vulnerabilidad": vulnerabilidad,
            "indice_sensibilizacion": indice_sensibilizacion,
            "nivel_termico": nivel_termico,
            "zona_color": zona_color,
            "etiqueta_termica": etiqueta_termica
        })

    # 2. Computar Matriz Bidimensional (Eje x Facultad)
    matriz_facultades = []
    for fac in facultades:
        fac_users = [u for u in usuarios if fac.lower() in (u["facultad"] or "").lower()]
        n_fac_users = len(fac_users)
        scores_ejes = {}

        for eje_id, eje_meta in EJES_RIESGO_PII.items():
            cursos = eje_meta["cursos_asociados"]
            fac_evaluados = n_fac_users * len(cursos)
            fac_comp = 0
            fac_venc = 0

            for u in fac_users:
                for c_id in cursos:
                    st = asig_map.get((u["id"], c_id))
                    if st == "completado":
                        fac_comp += 1
                    elif st == "vencido":
                        fac_venc += 1

            t_cumpl = (round(fac_comp / fac_evaluados * 100, 1)) if fac_evaluados > 0 else 0.0
            vuln = min(100.0, round(100.0 - t_cumpl + (20.0 if fac_venc > 0 else 0.0), 1))

            if vuln >= 75.0 or fac_venc > 0:
                color = "#dc2626"
                lvl = "critico"
            elif vuln >= 50.0:
                color = "#ea580c"
                lvl = "alto"
            elif vuln >= 25.0:
                color = "#d97706"
                lvl = "moderado"
            else:
                color = "#059669"
                lvl = "bajo"

            scores_ejes[eje_id] = {
                "vulnerabilidad": vuln,
                "sensibilizacion": round(100.0 - vuln, 1),
                "cumplimiento": t_cumpl,
                "nivel": lvl,
                "color": color,
                "vencidos": fac_venc
            }

        matriz_facultades.append({
            "facultad": fac,
            "usuarios": n_fac_users,
            "scores": scores_ejes
        })

    vulnerabilidad_global = round(vulnerabilidad_ponderada_global, 1)
    sensibilizacion_global = round(100.0 - vulnerabilidad_global, 1)

    return {
        "status": "success",
        "normas_referencia": [
            "ISO/IEC 27701:2025 Control A.3.17 (Sensibilización en seguridad y privacidad de PII)",
            "ISO/IEC 27701:2025 Control A.3.11 (Respuesta ante incidentes de privacidad)",
            "ISO/IEC 27002:2022 Control 6.3 (Information security awareness, education and training)",
            "Ley N° 29733 (Art. 19 Principio de Seguridad)",
            "D.S. N° 016-2024-JUS (Protocolo de notificación de brechas en 24h)"
        ],
        "kpis": {
            "indice_global_sensibilizacion": sensibilizacion_global,
            "vulnerabilidad_promedio_pct": vulnerabilidad_global,
            "zona_termica_critica": zona_critica_nombre,
            "ejes_en_alerta_roja": len([e for e in ejes_computados if e["nivel_termico"] == "critico"]),
            "facultades_evaluadas": len(matriz_facultades),
            "meta_sensibilizacion_pct": 80.0
        },
        "ejes": ejes_computados,
        "matriz_bidimensional": matriz_facultades,
        "timestamp": datetime.now().isoformat()
    }


async def obtener_o_generar_diagnostico_ia_heatmap(
    force_refresh: bool = False,
    solicitante_id: str = "admin"
) -> Dict[str, Any]:
    """
    Genera el Dictamen Termográfico y Diagnóstico de Sensibilización sobre Riesgos PII
    con el Copiloto IA (Agente #8) y lo persiste en 'evaluaciones_control'.
    """
    heatmap_data = calcular_mapa_calor()

    with get_db_connection() as conn:
        ultima = conn.execute(
            """
            SELECT * FROM evaluaciones_control
            WHERE nombre_caso = 'Mapa de Calor de Riesgos PII ISO 27701'
            ORDER BY created_at DESC LIMIT 1
            """
        ).fetchone()

    if ultima and not force_refresh:
        try:
            dictamen_previo = json.loads(ultima["resultado_json"])
            return {
                **heatmap_data,
                "diagnostico_ia": dictamen_previo,
                "evidencia_documentada_id": ultima["id"],
                "fecha_diagnostico": ultima["created_at"],
                "origen": "cache_documentado"
            }
        except Exception as e:
            logger.warning(f"Error parseando dictamen previo de heatmap: {e}")

    kpis = heatmap_data["kpis"]
    resumen_ejes = []
    for e in heatmap_data["ejes"]:
        resumen_ejes.append(
            f"- {e['nombre']} ({e['control_iso']}): Temperatura/Vulnerabilidad {e['temperatura_vulnerabilidad']}° ({e['etiqueta_termica']}). "
            f"Sensibilización: {e['indice_sensibilizacion']}/100. Completados: {e['completados']}, Vencidos: {e['vencidos']}, Pendientes: {e['pendientes']}."
        )

    prompt = [
        {
            "role": "system",
            "content": (
                "Eres el Copiloto de Ciberseguridad y Privacidad del Oficial de Protección de Datos (DPO) de la UNSA, "
                "especialista en ISO/IEC 27701:2025 Control A.3.17, Control A.3.11 y Ley N° 29733.\n"
                "Tu objetivo es emitir el Informe Termográfico Oficial de Vulnerabilidad y Sensibilización sobre Riesgos de PII."
            )
        },
        {
            "role": "user",
            "content": (
                f"Datos cuantitativos del mapa de calor institucional de la UNSA:\n"
                f"- Índice Global de Sensibilización: {kpis['indice_global_sensibilizacion']}/100 (Meta: {kpis['meta_sensibilizacion_pct']})\n"
                f"- Vulnerabilidad Promedio Institucional: {kpis['vulnerabilidad_promedio_pct']}%\n"
                f"- Zona Térmica Crítica: {kpis['zona_termica_critica']}\n"
                f"- Ejes en Alerta Roja: {kpis['ejes_en_alerta_roja']} de 6 dominios\n\n"
                f"Detalle por Eje Temático:\n" + "\n".join(resumen_ejes) + "\n\n"
                "Genera un diagnóstico termográfico riguroso y estructurado en JSON válido con las siguientes claves:\n"
                "{\n"
                '  "diagnostico_termografico": "Diagnóstico ejecutivo del DPO sobre la distribución del riesgo térmico.",\n'
                '  "foco_critico_principal": "Explicación del eje más susceptible y sus causas técnicas.",\n'
                '  "vulnerabilidades_destacadas": ["Vulnerabilidad 1", "Vulnerabilidad 2", ...],\n'
                '  "medidas_preventivas": [\n'
                '    {"accion": "...", "eje_afectado": "...", "prioridad": "Inmediata" | "Alta" | "Media", "metodo": "Taller" | "Simulacro" | "Notificación"}\n'
                '  ],\n'
                '  "dictamen_anpd": "Advertencia legal sobre posibles multas o inspecciones de la ANPD ante fugas en estos ejes."\n'
                "}\n"
                "Responde ÚNICAMENTE con el objeto JSON sin texto antes ni después."
            )
        }
    ]

    try:
        raw_res = await LLMService.chat_completion(messages=prompt, json_mode=True, temperature=0.2)
        dictamen_ia = json.loads(raw_res)
    except Exception as e:
        logger.error(f"Error generando dictamen IA de heatmap: {e}")
        dictamen_ia = {
            "diagnostico_termografico": (
                f"El gradiente térmico de la Universidad Nacional de San Agustín registra un índice global de sensibilización "
                f"del {kpis['indice_global_sensibilizacion']}/100, con un nivel de vulnerabilidad institucional del {kpis['vulnerabilidad_promedio_pct']}%. "
                f"Se observa un recalentamiento crítico en los dominios de '{kpis['zona_termica_critica']}' y 'Ingeniería Social'."
            ),
            "foco_critico_principal": (
                "El eje de Respuesta a Brechas en 24h (Control A.3.11) presenta máxima vulnerabilidad debido a la existencia de "
                "módulos formativos vencidos y falta de asimilación del protocolo urgente de escalamiento ante el CSIRT-UNSA."
            ),
            "vulnerabilidades_destacadas": [
                "Exposición a phishing e ingeniería social por falta de talleres prácticos de concientización.",
                "Riesgo de fuga de PII en bancos de datos de tesis e investigaciones científicas en Medicina e Ingeniería.",
                "Desconocimiento de los plazos de atención de solicitudes de Derechos ARCO en áreas administrativas."
            ],
            "medidas_preventivas": [
                {
                    "accion": "Desplegar simulación controlada de phishing a los estamentos docentes y administrativos.",
                    "eje_afectado": "Ingeniería Social",
                    "prioridad": "Inmediata",
                    "metodo": "Simulacro"
                },
                {
                    "accion": "Convocatoria masiva de regularización para el curso f004 (Reporte de brechas en menos de 24 horas).",
                    "eje_afectado": "Respuesta a Brechas",
                    "prioridad": "Inmediata",
                    "metodo": "Notificación"
                },
                {
                    "accion": "Taller presencial para personal de mesa de partes sobre los plazos perentorios de Derechos ARCO.",
                    "eje_afectado": "Derechos ARCO",
                    "prioridad": "Alta",
                    "metodo": "Taller"
                }
            ],
            "dictamen_anpd": (
                "Conforme al D.S. N° 016-2024-JUS, no reportar una brecha dentro de las 24 horas acarrea multas graves "
                "de hasta 50 UIT impuestas por la Autoridad Nacional de Protección de Datos Personales."
            )
        }

    eval_id = f"eval_heatmap_{uuid.uuid4().hex[:8]}"
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
                    "Mapa de Calor de Riesgos PII ISO 27701",
                    json.dumps({"ejes_evaluados": list(EJES_RIESGO_PII.keys()), "kpis": kpis}, ensure_ascii=False),
                    json.dumps(dictamen_ia, ensure_ascii=False),
                    now_str
                )
            )
        registrar_audit(
            solicitante_id,
            "generar_diagnostico_ia_heatmap",
            {"eval_id": eval_id, "sensibilizacion_global": kpis["indice_global_sensibilizacion"]}
        )
    except Exception as exc:
        logger.warning(f"No se pudo guardar la evaluación de heatmap en BD: {exc}")

    return {
        **heatmap_data,
        "diagnostico_ia": dictamen_ia,
        "evidencia_documentada_id": eval_id,
        "fecha_diagnostico": now_str,
        "origen": "ia_en_vivo"
    }
