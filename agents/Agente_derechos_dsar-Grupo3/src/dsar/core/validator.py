"""Validador de invariantes del expediente. No corrige: solo informa errores."""

from __future__ import annotations

from typing import Any

from .profiles import MUTATING_RIGHTS
from .states import ALLOWED_STATES, ENGINE_FINAL_STATES, HUMAN_ONLY_STATES

REQUIRED_FIELDS = frozenset({
    "case_id", "request_type", "status", "deadline_at", "identity_verification",
    "discovered_records", "hitl", "proposed_action", "audit_trail", "source_hashes", "rag", "disclaimer",
})
SOURCE_HASH_KEYS = frozenset({"request", "data", "policies"})
RAG_METADATA = frozenset({
    "method", "embedding_model", "query", "vector_store", "vector_store_sha256", "vector_dimensions",
})
RAG_CHUNK_FIELDS = frozenset({"rank", "score", "chunk_id", "source", "section", "sha256", "excerpt"})
SUSPENSION_TYPES = frozenset({"additional_information", "request_correction"})


def _actions(package: dict[str, Any]) -> list[str]:
    actions = [package["proposed_action"], *package.get("proposed_actions", [])]
    if any(action.get("executed") is not False for action in actions):
        return ["El prototipo no puede declarar una accion ejecutada"]
    return []


def _rights(package: dict[str, Any]) -> list[str]:
    errors = []
    rights = package.get("request_types") or [package["request_type"]]
    if package["request_type"] != rights[0]:
        errors.append("request_type debe coincidir con el primer derecho de request_types")
    if any(right in MUTATING_RIGHTS for right in rights) and not package["hitl"].get("required"):
        errors.append("Una accion de mutacion o restriccion requiere HITL")
    return errors


def _extension_errors(package: dict[str, Any], right: str, item: dict[str, Any]) -> list[str]:
    profile_extension = (package.get("policy") or {}).get("extension") or {}
    extension = item.get("extension") or {}
    errors = []
    if not profile_extension.get("allowed") or right in profile_extension.get("excluded_rights", []):
        errors.append(f"El perfil no admite prorrogar {right}")
    if not extension.get("decided_by") or not extension.get("original_deadline_at"):
        errors.append(f"La prorroga de {right} no registra decision humana")
    elif not 0 < extension.get("days", 0) <= item.get("legal_days", item["days"]):
        errors.append(f"La prorroga de {right} supera el plazo igual al legal (art. 71.1)")
    elif str(extension.get("decided_at", "")) > extension.get("original_legal_deadline_at", extension["original_deadline_at"]):
        errors.append(f"La prorroga de {right} se decidio fuera del plazo que se amplia (art. 71.2)")
    elif extension.get("legal_ceiling_at") and item["deadline_at"] > extension["legal_ceiling_at"]:
        errors.append(f"El plazo prorrogado de {right} pasa del tope legal")
    return errors


def _deadlines(package: dict[str, Any]) -> list[str]:
    deadlines = package.get("deadlines")
    if deadlines is None:
        return []
    errors = []
    rights = package.get("request_types") or [package["request_type"]]
    if set(deadlines) != set(rights):
        errors.append("Cada derecho solicitado necesita su propio plazo")
    elif package["deadline_at"] != min(item["deadline_at"] for item in deadlines.values()):
        errors.append("deadline_at debe ser el plazo mas cercano de los derechos")
    for right, item in deadlines.items():
        if "legal_days" in item and item["days"] > item["legal_days"]:
            errors.append(f"El plazo de {right} supera el plazo legal")
        if item.get("extended"):
            errors.extend(_extension_errors(package, right, item))
    return errors


def _decision(package: dict[str, Any]) -> list[str]:
    status = package["status"]
    if status not in HUMAN_ONLY_STATES:
        return []
    errors = []
    decision = package.get("human_decision") or {}
    if decision.get("decision") != status or not decision.get("reviewer") or not decision.get("note"):
        errors.append(f"Un estado {status} exige una decision humana registrada")
    if status in {"APPROVED", "REJECTED"} and package["identity_verification"].get("status") != "verified":
        errors.append("No se puede decidir un caso sin identidad verificada")
    return errors


def _suspension(package: dict[str, Any]) -> list[str]:
    suspension = package.get("suspension")
    if package["status"] != "ON_HOLD":
        return ["Hay una suspension activa fuera de ON_HOLD"] if suspension else []
    if not isinstance(suspension, dict):
        return ["Un caso ON_HOLD necesita una suspension activa"]
    errors = []
    if suspension.get("type") not in SUSPENSION_TYPES:
        errors.append("Tipo de suspension no admitido")
    if suspension.get("previous_status") not in ENGINE_FINAL_STATES:
        errors.append("La suspension no registra un estado previo valido")
    if not suspension.get("decided_by"):
        errors.append("La suspension no registra decision humana")
    if suspension.get("cancellation_proposed") and suspension.get("type") != "request_correction":
        errors.append("Solo una solicitud observada puede proponerse como cancelada")
    return errors


def _audit(package: dict[str, Any]) -> list[str]:
    trail = package["audit_trail"]
    errors = []
    if [item.get("sequence") for item in trail] != list(range(1, len(trail) + 1)):
        errors.append("La secuencia de auditoria no es continua")
    if any(item.get("state") not in ALLOWED_STATES for item in trail):
        errors.append("La auditoria contiene estados no admitidos")
    if trail and trail[-1].get("state") != package["status"]:
        errors.append("El ultimo evento de auditoria no coincide con el estado")
    return errors


def _records(package: dict[str, Any]) -> list[str]:
    errors = []
    if package["identity_verification"].get("status") != "verified" and package["discovered_records"]:
        errors.append("Se descubrieron datos sin identidad verificada")
    for record in package["discovered_records"]:
        if not record.get("record_id") or not record.get("source_system"):
            errors.append("Registro sin procedencia completa")
        for field in record.get("redacted_fields", []):
            if field in record.get("data", {}):
                errors.append(f"Campo de tercero no redactado: {field}")
    return errors


def _rag(package: dict[str, Any]) -> list[str]:
    rag = package.get("rag", {})
    if not rag.get("enabled"):
        return []
    errors = []
    if RAG_METADATA - rag.keys():
        errors.append("Metadatos RAG incompletos")
    if rag.get("vector_dimensions", 0) <= 0:
        errors.append("Dimension vectorial RAG invalida")
    if len(str(rag.get("vector_store_sha256", ""))) != 64:
        errors.append("Almacen vectorial sin huella SHA-256 valida")
    for item in rag.get("retrieved_chunks", []):
        if RAG_CHUNK_FIELDS - item.keys():
            errors.append("Fragmento RAG sin procedencia completa")
        if len(str(item.get("sha256", ""))) != 64:
            errors.append("Fragmento RAG sin huella SHA-256 valida")
    return errors


def validate(package: dict[str, Any]) -> list[str]:
    missing = REQUIRED_FIELDS - package.keys()
    if missing:
        return [f"Campos faltantes: {sorted(missing)}"]
    errors: list[str] = []
    if package["status"] not in ALLOWED_STATES:
        errors.append("Estado no admitido")
    for check in (_actions, _rights, _deadlines, _decision, _suspension, _audit, _records):
        errors.extend(check(package))
    if set(package["source_hashes"]) != SOURCE_HASH_KEYS:
        errors.append("Faltan hashes de las entradas")
    errors.extend(_rag(package))
    return errors
