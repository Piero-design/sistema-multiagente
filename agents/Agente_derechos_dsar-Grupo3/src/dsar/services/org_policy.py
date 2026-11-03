"""Política de la organización: lectura, validación y versiones en `config/historial/`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsar.core.errors import CaseInputError
from dsar.core.policy import ensure_valid_org_policy, org_policy_hash
from dsar.services.context import ServiceContext

MAX_TEXT = 50_000


def _history(ctx: ServiceContext) -> list[str]:
    folder = ctx.settings.org_history_dir
    return sorted((path.name for path in folder.glob("*") if path.is_file()), reverse=True) if folder.is_dir() else []


def get(ctx: ServiceContext) -> dict[str, Any]:
    policy = ctx.organization()
    text_path = ctx.settings.org_text_path
    return {
        "policy": policy,
        "text": text_path.read_text(encoding="utf-8") if text_path.is_file() else None,
        "sha256": org_policy_hash(policy) if policy else None,
        "history": _history(ctx),
    }


def _archive(ctx: ServiceContext, paths: tuple[Path, ...]) -> None:
    stamp = ctx.now().strftime("%Y%m%dT%H%M%SZ")
    history = ctx.settings.org_history_dir
    history.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if path.is_file():
            (history / f"{stamp}-{path.name}").write_bytes(path.read_bytes())


def save(ctx: ServiceContext, policy: dict[str, Any], text: str | None = None) -> dict[str, Any]:
    """Valida contra los perfiles (nunca alarga un plazo legal), archiva la versión anterior y guarda.

    Si cambia el texto, el RAG detecta el cambio del corpus y regenera su índice en la siguiente consulta.
    """
    ensure_valid_org_policy(policy, ctx.profiles)
    if text is not None and (not text.strip().startswith("#") or len(text) > MAX_TEXT):
        raise CaseInputError("El procedimiento interno debe ser Markdown y empezar con un titulo (#).")
    settings = ctx.settings
    _archive(ctx, (settings.org_policy_path, settings.org_text_path))
    settings.org_policy_path.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8", newline="\n")
    if text is not None:
        settings.org_text_path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
    return get(ctx)
