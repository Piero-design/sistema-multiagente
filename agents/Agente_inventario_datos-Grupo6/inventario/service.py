"""Punto de entrada único para CLI, HTTP y MCP; sin aprobaciones ni envíos externos."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from . import AGENT_DIRECTORY, AGENT_ID, CONTRACT_VERSION
from .domain import DomainError, analizar_fuentes, clasificar, digest, mapear, normalizar
from .models import Handoff, Solicitud
from .storage import Repository

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("SKILL.md", "skills/registrar_activos/SKILL.md", "skills/clasificar_datos/SKILL.md", "skills/mapear_tratamientos/SKILL.md")


def cargar_skill() -> str:
    return "\n\n".join((ROOT / path).read_text(encoding="utf-8") for path in SKILLS)


def respuesta(accion: str | None, data=None, error=None, request_id=None) -> dict[str, Any]:
    return {"agent_id": AGENT_ID, "agent_directory": AGENT_DIRECTORY, "contract_version": CONTRACT_VERSION,
            "status": "error" if error else "ok", "accion": accion, "request_id": request_id,
            "motor": "reglas_locales", "simulado": False, "data": data, "error": error}


def validation_error(exc: ValidationError) -> dict[str, Any]:
    # No devuelve valores de entrada: una solicitud inválida podría traer datos personales.
    return {"code": "ENTRADA_INVALIDA", "message": "La solicitud no cumple el contrato.", "retryable": False,
            "details": [{"campo": ".".join(map(str, e["loc"])), "tipo": e["type"]} for e in exc.errors()]}


class InventoryAgent:
    def __init__(self, db_path: Path | str | None = None):
        self.repository = Repository(db_path if db_path is not None else os.environ.get("INVENTARIO_DB_PATH", str(ROOT / "data/inventario.sqlite3")))
        self.instructions = cargar_skill()

    def ejecutar(self, payload: Any) -> tuple[dict[str, Any], int]:
        try:
            req = Solicitud.model_validate(payload)
        except ValidationError as exc:
            return respuesta(None, error=validation_error(exc)), 422
        try:
            if req.accion in {"analizar", "registrar_activos"}:
                data = analizar_fuentes(req.organizacion, req.fuentes)
                data["tratamientos"] = mapear(data["activos"])
                data["persistido"] = req.accion == "registrar_activos"
                if data["persistido"]:
                    data["registro"] = self.repository.guardar(data["activos"])
            elif req.accion == "clasificar_datos":
                data = {"campos": [clasificar(name) for name in req.campos], "requiere_validacion": True}
            else:
                assets = self.repository.consultar(req.organizacion, req.sistema)
                if req.accion == "consultar_inventario":
                    data = {"organizacion": req.organizacion, "activos": assets, "total_activos": len(assets)}
                elif req.accion == "mapear_tratamientos":
                    data = {"organizacion": req.organizacion, "tratamientos": mapear(assets), "requiere_validacion": True}
                elif req.accion == "confirmar_cobertura":
                    systems = []
                    for system in dict.fromkeys(req.missing_systems):
                        matching = [a for a in assets if normalizar(a["sistema"]) == normalizar(system)]
                        systems.append({"sistema": system, "estado": "inventariado_pendiente_validacion" if matching else "sin_activos_en_inventario",
                                        "activo_ids": [a["id"] for a in matching],
                                        "categorias": sorted({f["categoria"] for a in matching for f in a["campos"]})})
                    data = {"organizacion": req.organizacion, "sistemas": systems, "found_systems_dsar": req.found_systems,
                            "requiere_validacion": True, "modifica_expediente_dsar": False,
                            "advertencia": "Inventariar un sistema no demuestra que contenga registros de un titular ni resuelve la cobertura DSAR."}
                else:  # exportar_evidencia: adaptador para el contrato HTTP real del Grupo 4.
                    document = {"agent_id": AGENT_ID, "organizacion": req.organizacion, "activos": assets,
                                "tratamientos": mapear(assets), "estado": "borrador_pendiente_validacion", "simulado": False}
                    content = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True)
                    data = {"nombre_archivo": "inventario-grupo6.json", "contenido": content,
                            "sha256": hashlib.sha256(content.encode()).hexdigest(),
                            "destinatario_previsto": "Agente_evidencia_auditoria-Grupo4", "enviado": False}
            return respuesta(req.accion, data=data, request_id=req.request_id), 200
        except DomainError as exc:
            return respuesta(req.accion, error={"code": exc.code, "message": str(exc), "retryable": False}, request_id=req.request_id), exc.status
        except (sqlite3.Error, OSError, json.JSONDecodeError):
            return respuesta(req.accion, error={"code": "ALMACENAMIENTO_NO_DISPONIBLE", "message": "No se pudo consultar o guardar el inventario.", "retryable": True}, request_id=req.request_id), 503

    def recibir_handoff(self, payload: Any, organizacion: str) -> tuple[dict[str, Any], int]:
        try:
            handoff = Handoff.model_validate(payload)
        except ValidationError as exc:
            return respuesta("confirmar_cobertura", error=validation_error(exc)), 422
        # El Grupo 3 calcula exactamente json.dumps(sort_keys=True, ensure_ascii=False), con espacios.
        body = {key: value for key, value in payload.items() if key != "sha256"}
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        if not hmac.compare_digest(expected, handoff.sha256):
            return respuesta("confirmar_cobertura", error={"code": "HASH_HANDOFF_INVALIDO", "message": "El sobre no conserva el SHA-256 del emisor.", "retryable": False}), 422
        result, status = self.ejecutar({"accion": "confirmar_cobertura", "organizacion": organizacion,
                                       "missing_systems": handoff.payload.missing_systems,
                                       "found_systems": handoff.payload.found_systems})
        if status == 200:
            result["data"]["case_ref"] = handoff.case_ref
            result["data"]["handoff_sha256"] = handoff.sha256
            result["data"]["hash_verificado"] = True
            result["data"]["autenticidad_emisor_verificada"] = False
        return result, status

    def estado(self) -> dict[str, Any]:
        return {"agent_id": AGENT_ID, "agent_directory": AGENT_DIRECTORY,
                "contract_version": CONTRACT_VERSION, "motor": "reglas_locales", "simulado": False,
                "skill_cargada": True, "skill_sha256": digest(self.instructions),
                "acciones": list(Solicitud.model_fields["accion"].annotation.__args__),
                "orquestador_central": "no_disponible_en_repositorio_inspeccionado",
                "almacenamiento": "SQLite propia; sin conexión automática a la BD común"}
