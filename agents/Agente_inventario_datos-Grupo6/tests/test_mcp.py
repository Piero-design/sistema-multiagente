"""Cliente MCP real por stdio: descubrimiento y llamada, sin un orquestador simulado."""
import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


def test_mcp_stdio(tmp_path):
    async def run():
        params = StdioServerParameters(command=sys.executable, args=["-m", "inventario.mcp_server", "--db", str(tmp_path / "mcp.sqlite3")], cwd=str(ROOT))
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                assert init.serverInfo.name == "inventario-agent"
                assert "declarado_en_solicitud" in init.instructions
                contract = await session.read_resource("inventario://contrato")
                assert "confirmar_cobertura" in contract.contents[0].text
                tools = (await session.list_tools()).tools
                assert {t.name for t in tools} == {"inventario_ejecutar", "inventario_registrar_activos", "inventario_consultar", "inventario_clasificar_datos", "inventario_mapear_tratamientos", "inventario_confirmar_cobertura"}
                source = {"id": "demo", "nombre": "MCP ficticio", "sistema": "Matrícula", "formato": "campos", "campos": ["dni", "email"]}
                result = await session.call_tool("inventario_registrar_activos", {"organizacion": "DEMO-MCP", "fuentes": [source]})
                assert not result.isError
                body = result.structuredContent
                assert body["status"] == "ok" and body["data"]["total_campos"] == 2
                query = await session.call_tool("inventario_consultar", {"organizacion": "DEMO-MCP"})
                assert query.structuredContent["data"]["total_activos"] == 1
                invalid = await session.call_tool("inventario_ejecutar", {"solicitud": {"accion": "analizar", "organizacion": "DEMO-MCP"}})
                assert invalid.structuredContent["status"] == "error"
                assert invalid.structuredContent["error"]["code"] == "ENTRADA_INVALIDA"
    asyncio.run(asyncio.wait_for(run(), timeout=20))
