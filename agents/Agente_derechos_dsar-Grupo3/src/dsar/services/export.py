"""Exportación del expediente validado a `DSAR_EXPORT_DIR/<id>/`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsar.assistant.guard import executed_claims
from dsar.core.errors import CaseInputError
from dsar.core.procedures import ensure_exportable
from dsar.core.validator import validate
from dsar.services import cases
from dsar.services.context import ServiceContext
from dsar.services.errors import check_case_id

MAX_DRAFT = 200_000


def _folder(export_dir: Path, case_id: str) -> Path:
    """Carpeta del caso, garantizando que queda dentro del directorio de exportación."""
    base = export_dir.resolve()
    folder = (base / check_case_id(case_id).lower()).resolve()
    if folder.parent != base:
        raise CaseInputError("Ruta de exportacion invalida.")
    return folder


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def export_case(ctx: ServiceContext, case_id: str, draft: str, conversation: list[dict[str, Any]]) -> dict[str, Any]:
    folder = _folder(ctx.settings.export_dir, case_id)
    package = cases.get(ctx, case_id)
    ensure_exportable(package)
    errors = validate(package)
    if errors:
        raise CaseInputError("No se puede exportar un expediente invalido: " + "; ".join(errors))
    if not isinstance(draft, str) or len(draft) > MAX_DRAFT:
        raise CaseInputError("Borrador invalido.")
    folder.mkdir(parents=True, exist_ok=True)
    _write_json(folder / "case-package.json", package)
    _write_json(folder / "request.json", cases.payload(ctx, case_id))
    _write_json(folder / "conversation.json", conversation)
    (folder / "response-draft.md").write_text(draft, encoding="utf-8", newline="\n")
    return {"case_id": case_id, "folder": folder.name,
            "files": ["case-package.json", "request.json", "conversation.json", "response-draft.md"],
            "warnings": executed_claims(draft)}
