"""Herramientas MCP reales (SDK mcp 1.x), con instrucciones de dominio cargadas."""
from __future__ import annotations

import argparse
from typing import Any
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from .service import InventoryAgent, ROOT


def create_server(db_path=None, port: int = 8007) -> FastMCP:
    agent = InventoryAgent(db_path)
    mcp = FastMCP("inventario-agent", instructions=agent.instructions, host="127.0.0.1", port=port)
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)

    @mcp.resource("inventario://contrato")
    def contrato_integracion() -> str:
        """Contrato del Grupo 6, operaciones, errores y conexión DSAR."""
        return (ROOT / "references/contrato-integracion.md").read_text(encoding="utf-8")

    @mcp.resource("inventario://ejemplo")
    def ejemplo_registro() -> str:
        """Entrada ficticia para registrar un activo de matrícula."""
        return (ROOT / "examples/registro_matricula.json").read_text(encoding="utf-8")

    @mcp.tool(annotations=write)
    def inventario_ejecutar(solicitud: dict[str, Any]) -> dict[str, Any]:
        """Despacha una acción del contrato Grupo 6. analizar no escribe; registrar_activos persiste metadatos."""
        return agent.ejecutar(solicitud)[0]

    @mcp.tool(annotations=write)
    def inventario_registrar_activos(organizacion: str, fuentes: list[dict[str, Any]]) -> dict[str, Any]:
        """Registra/actualiza fuentes por organización. Guarda metadatos y revisiones, no valores de filas."""
        return agent.ejecutar({"accion": "registrar_activos", "organizacion": organizacion, "fuentes": fuentes})[0]

    @mcp.tool(annotations=read)
    def inventario_consultar(organizacion: str, sistema: str | None = None) -> dict[str, Any]:
        """Consulta activos de una organización, opcionalmente de un sistema exacto (normalizado)."""
        return agent.ejecutar({"accion": "consultar_inventario", "organizacion": organizacion, "sistema": sistema})[0]

    @mcp.tool(annotations=read)
    def inventario_clasificar_datos(organizacion: str, campos: list[str]) -> dict[str, Any]:
        """Sugiere categorías por nombre. Un campo desconocido conserva es_pii=null y requiere revisión."""
        return agent.ejecutar({"accion": "clasificar_datos", "organizacion": organizacion, "campos": campos})[0]

    @mcp.tool(annotations=read)
    def inventario_mapear_tratamientos(organizacion: str, sistema: str | None = None) -> dict[str, Any]:
        """Prepara borradores y flujos exclusivamente con contexto declarado, sin deducir bases jurídicas."""
        return agent.ejecutar({"accion": "mapear_tratamientos", "organizacion": organizacion, "sistema": sistema})[0]

    @mcp.tool(annotations=read)
    def inventario_confirmar_cobertura(organizacion: str, handoff: dict[str, Any]) -> dict[str, Any]:
        """Recibe el sobre DSAR confirmar_cobertura, verifica hash y consulta activos; no modifica DSAR."""
        return agent.recibir_handoff(handoff, organizacion)[0]

    return mcp


def main(argv=None):
    parser = argparse.ArgumentParser(description="MCP Grupo 6 · Inventario")
    parser.add_argument("--db")
    parser.add_argument("--http", action="store_true", help="Streamable HTTP local; por defecto stdio")
    parser.add_argument("--port", type=int, default=8007)
    args = parser.parse_args(argv)
    create_server(args.db, args.port).run(transport="streamable-http" if args.http else "stdio")


if __name__ == "__main__":
    main()
