"""Servidor MCP del Agente DSAR (SDK `mcp` 2.x).

Uso (desde backend/):
    python -m dsar.mcp.server            # stdio (Claude Code, Claude Desktop)
    python -m dsar.mcp.server --http     # streamable-http en 127.0.0.1:8001/mcp (sin autenticación hasta la fase 5)
"""

from __future__ import annotations

import argparse
from typing import Any

from mcp.server.mcpserver import MCPServer

from dsar.mcp import tools
from dsar.services.context import ServiceContext, build_context, load_env_file

INSTRUCTIONS = (
    "Agente de Derechos DSAR del PIMS (ISO/IEC 27701:2025, Ley 29733). "
    "Puedes crear expedientes, consultar estado, plazos y controles ISO, consultar la norma y leer handoffs. "
    "No puedes aprobar, rechazar ni ejecutar: la decisión humana se registra solo en el panel del agente."
)
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 8001


def create_server(ctx: ServiceContext | None = None) -> MCPServer:
    context = ctx or build_context()
    server = MCPServer(name="dsar-agent", instructions=INSTRUCTIONS)

    @server.tool()
    def dsar_crear_caso(principal_id: str, request_types: list[str], policy_id: str = "PE-LEY29733",
                        received_at: str | None = None, identity_status: str = "pending",
                        identity_reference: str = "", request_text: str = "") -> dict[str, Any]:
        """Registra y tramita una solicitud de derechos (information, access, portability,
        rectification, erasure, objection). Devuelve estado, plazos y motivos de revisión humana."""
        return tools.crear_caso(context, principal_id, request_types, policy_id, received_at, identity_status,
                                identity_reference, request_text)

    @server.tool()
    def dsar_estado(case_id: str) -> dict[str, Any]:
        """Estado de un expediente: motivos HITL, aprobador designado, decisión humana y handoffs."""
        return tools.estado(context, case_id)

    @server.tool()
    def dsar_plazos(case_id: str) -> dict[str, Any]:
        """Plazos por derecho de un expediente guardado."""
        return tools.plazos(context, case_id)

    @server.tool()
    def dsar_controles(case_id: str) -> dict[str, Any]:
        """Controles del Anexo A y cláusulas de ISO/IEC 27701:2025 que evidencia un expediente.
        Tabla fija según el estado del caso; solo lectura."""
        return tools.controles(context, case_id)

    @server.tool()
    def dsar_asistente(pregunta: str, case_id: str | None = None, modo: str = "guided") -> dict[str, Any]:
        """Asistente DSAR: explica un caso o la norma. modo «guided» (sin modelo) o un proveedor configurado
        («gateway» en la plataforma). Solo hechos minimizados; no decide ni redacta borradores con datos."""
        return tools.asistente(context, pregunta, case_id, modo)

    @server.tool()
    def dsar_calcular_plazos(request_types: list[str], received_at: str,
                             policy_id: str = "PE-LEY29733") -> dict[str, Any]:
        """Calcula plazos (días hábiles en PE) sin crear un expediente."""
        return tools.calcular_plazos(context, request_types, received_at, policy_id)

    @server.tool()
    def dsar_listar(status: str | None = None) -> list[dict[str, Any]]:
        """Lista expedientes guardados, opcionalmente filtrados por estado."""
        return tools.listar(context, status)

    @server.tool()
    def dsar_borrador(case_id: str) -> dict[str, Any]:
        """Borrador de respuesta al titular. Solo para expedientes APPROVED por una persona."""
        return tools.borrador(context, case_id)

    @server.tool()
    def dsar_consultar_norma(pregunta: str, top_k: int = 3) -> dict[str, Any]:
        """Fragmentos citables de ISO/IEC 27701, Ley 29733 y la política interna."""
        return tools.consultar_norma(context, pregunta, top_k)

    @server.tool()
    def dsar_handoffs(case_id: str | None = None) -> list[dict[str, Any]]:
        """Entregas del Agente DSAR para los agentes de Evidencia, Terceros e Inventario."""
        return tools.handoffs(context, case_id)

    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Servidor MCP del Agente DSAR")
    parser.add_argument("--http", action="store_true", help="streamable-http en 127.0.0.1 en lugar de stdio")
    parser.add_argument("--port", type=int, default=HTTP_PORT)
    args = parser.parse_args(argv)
    load_env_file()
    server = create_server()
    if args.http:
        server.run(transport="streamable-http", host=HTTP_HOST, port=args.port)
    else:
        server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
