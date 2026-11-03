"""Rutas del backend (configuración, conocimiento, almacén RAG y fixtures)."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = BACKEND_ROOT / "config"
KNOWLEDGE_DIR = BACKEND_ROOT / "knowledge"
REFERENCES_DIR = KNOWLEDGE_DIR / "references"
SKILL_PATH = KNOWLEDGE_DIR / "SKILL.md"
RAG_STORE_DIR = BACKEND_ROOT / "rag_store"
# Guía de uso: corpus aparte (no entra en el RAG normativo ni en el control de alcance; solo se consulta en preguntas de «cómo se hace»).
GUIDE_DIR = KNOWLEDGE_DIR / "guide"
GUIDE_STORE_DIR = RAG_STORE_DIR / "guide"
FIXTURES_DIR = BACKEND_ROOT / "tests" / "fixtures"
PROFILES_PATH = CONFIG_DIR / "perfiles-jurisdiccion.json"
ORGANIZATION_PATH = CONFIG_DIR / "politica-organizacion.json"


def display_path(path: Path) -> str:
    """Ruta relativa al backend si está dentro; si no, absoluta."""
    resolved = path.resolve()
    return resolved.relative_to(BACKEND_ROOT).as_posix() if resolved.is_relative_to(BACKEND_ROOT) else str(resolved)
