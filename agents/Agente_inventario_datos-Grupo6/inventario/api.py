"""API local FastAPI: mismo núcleo que CLI y herramientas MCP."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any
from fastapi import Body, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from .models import Solicitud
from .service import InventoryAgent, ROOT, respuesta


def create_app(db_path: Path | str | None = None) -> FastAPI:
    agent = InventoryAgent(db_path)
    app = FastAPI(title="Grupo 6 · Agente de Inventario", version="1.0.0")
    app.state.agent = agent

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content=respuesta(None, error={"code": "ENTRADA_INVALIDA", "message": "La solicitud no cumple el contrato.", "retryable": False,
            "details": [{"campo": ".".join(map(str, e["loc"])), "tipo": e["type"]} for e in exc.errors()]}))

    @app.get("/api/status")
    def status():
        return agent.estado()

    @app.post("/api/ejecutar")
    def ejecutar(req: Solicitud):
        body, code = agent.ejecutar(req.model_dump())
        return JSONResponse(status_code=code, content=body)

    @app.post("/api/handoffs")
    def handoff(req: Annotated[dict[str, Any], Body()], organizacion: Annotated[str, Query(min_length=1, max_length=120)]):
        # Se usa el objeto recibido sin reserializar Pydantic para verificar el hash exacto del emisor.
        body, code = agent.recibir_handoff(req, organizacion)
        return JSONResponse(status_code=code, content=body)

    @app.get("/api/inventario")
    def consultar(organizacion: Annotated[str, Query(min_length=1, max_length=120)], sistema: str | None = None):
        body, code = agent.ejecutar({"accion": "consultar_inventario", "organizacion": organizacion, "sistema": sistema})
        return JSONResponse(status_code=code, content=body)

    @app.get("/api/tratamientos")
    def tratamientos(organizacion: Annotated[str, Query(min_length=1, max_length=120)], sistema: str | None = None):
        body, code = agent.ejecutar({"accion": "mapear_tratamientos", "organizacion": organizacion, "sistema": sistema})
        return JSONResponse(status_code=code, content=body)

    @app.get("/")
    def home():
        return FileResponse(ROOT / "agente.html")

    @app.get("/index.html")
    def local_demo():
        return FileResponse(ROOT / "index.html")

    @app.get("/agente.html")
    def panel():
        return FileResponse(ROOT / "agente.html")

    @app.get("/api/ejemplo")
    def example():
        import json
        return json.loads((ROOT / "examples/registro_matricula.json").read_text(encoding="utf-8"))

    return app


app = create_app()
