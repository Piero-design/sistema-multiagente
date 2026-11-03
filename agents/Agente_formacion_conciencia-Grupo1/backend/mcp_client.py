import logging
from typing import Dict, Any, Optional

import mcp_server
from mcp_externos.postgres_mock import consultar_pii
from mcp_externos.evidencias_mock import guardar_evidencia

logger = logging.getLogger("mcp_client")

class MCPClient:
    """
    Cliente MCP que despacha llamadas de herramientas tanto al servidor Local FastMCP
    como a servidores externos (PostgreSQL PII, Evidencias).
    """

    @staticmethod
    async def call_tool(tool_name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args = args or {}
        logger.info(f"Invocando herramienta MCP: {tool_name} con argumentos: {args}")

        try:
            # Herramientas del Servidor MCP Propio (FastMCP)
            if tool_name == "gestionar_alta_formacion":
                return mcp_server.gestionar_alta_formacion(
                    user_id=args.get("user_id"),
                    formacion_id=args.get("formacion_id")
                )


            elif tool_name == "consultar_estado_formacion":
                return mcp_server.consultar_estado_formacion(
                    user_id=args.get("user_id")
                )

            elif tool_name == "generar_reporte_conciencia":
                return mcp_server.generar_reporte_conciencia(
                    facultad=args.get("facultad")
                )

            elif tool_name == "evaluar_matriz_brechas":
                return mcp_server.evaluar_matriz_brechas(
                    rol=args.get("rol")
                )

            elif tool_name == "evaluar_mapa_calor":
                return mcp_server.evaluar_mapa_calor(
                    facultad=args.get("facultad")
                )

            elif tool_name == "evaluar_radar_cobertura":
                return mcp_server.evaluar_radar_cobertura(
                    estamento=args.get("estamento"),
                    facultad=args.get("facultad")
                )

            elif tool_name == "crear_formulario_capacitacion":
                return mcp_server.crear_formulario_capacitacion(
                    titulo=args.get("titulo", "Evaluación de Privacidad UNSA"),
                    descripcion=args.get("descripcion", "Cuestionario de Diagnóstico y Toma de Conciencia ISO 27701"),
                    curso_id=args.get("curso_id"),
                    preguntas=args.get("preguntas"),
                    destinatarios=args.get("destinatarios"),
                    solicitante_id=args.get("solicitante_id", "admin")
                )

            elif tool_name == "programar_evento_calendario":
                return mcp_server.programar_evento_calendario(
                    titulo=args.get("titulo", "Taller de Concienciación ISO 27701"),
                    fecha_inicio=args.get("fecha_inicio", "2026-10-26T10:00:00"),
                    duracion_minutos=args.get("duracion_minutos", 60),
                    descripcion=args.get("descripcion", "Sesión formativa obligatoria sobre protección de datos personales"),
                    asistentes=args.get("asistentes"),
                    ubicacion=args.get("ubicacion", "Google Meet UNSA (Virtual)"),
                    enlace_reunion=args.get("enlace_reunion"),
                    solicitante_id=args.get("solicitante_id", "admin")
                )

            elif tool_name == "listar_usuarios":
                return mcp_server.listar_usuarios(
                    filtros=args.get("filtros"),
                    solicitante_rol=args.get("solicitante_rol", "admin"),
                    solicitante_facultad=args.get("solicitante_facultad"),
                    solicitante_id=args.get("solicitante_id")
                )

            elif tool_name == "enviar_correo_masivo":
                return mcp_server.enviar_correo_masivo(
                    user_ids=args.get("user_ids", []),
                    asunto=args.get("asunto", "Aviso de Privacidad UNSA"),
                    cuerpo=args.get("cuerpo", ""),
                    remitente_id=args.get("remitente_id", "admin")
                )

            elif tool_name == "generar_certificado":
                return mcp_server.generar_certificado(
                    user_id=args.get("user_id"),
                    formacion_id=args.get("formacion_id")
                )

            # Herramientas de MCPs Externos directas
            elif tool_name == "consultar_pii":
                return consultar_pii(query=args.get("query", ""))

            elif tool_name == "guardar_evidencia":
                return guardar_evidencia(
                    user_id=args.get("user_id"),
                    archivo=args.get("archivo", "documento.pdf"),
                    control_iso=args.get("control_iso", "A.3.17"),
                    contenido=args.get("contenido")
                )

            else:
                return {
                    "status": "error",
                    "message": f"Herramienta MCP no reconocida: {tool_name}"
                }

        except Exception as e:
            logger.error(f"Fallo en ejecución de tool MCP {tool_name}: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error ejecutando {tool_name}: {str(e)}"
            }
