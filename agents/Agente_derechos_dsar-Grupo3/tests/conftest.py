from __future__ import annotations

import copy
from typing import Any

import pytest

from dsar.core.engine import build_case
from dsar.core.profiles import load_profiles
from support import CONFIG, FIXTURES, GENERATED_AT, HASHES, read_json


@pytest.fixture(scope="session")
def dense_ready() -> None:
    """Omite la prueba si el modelo denso no está en la caché local (nunca se descarga)."""
    from dsar.rag import dense

    reason = dense.available()
    if reason:
        pytest.skip(f"RAG denso no disponible: {reason}")


@pytest.fixture(scope="session")
def profiles() -> dict[str, Any]:
    return load_profiles(CONFIG / "perfiles-jurisdiccion.json")


@pytest.fixture(scope="session")
def records() -> list[dict[str, Any]]:
    return read_json(FIXTURES / "subject-data.json")


@pytest.fixture
def org() -> dict[str, Any]:
    return read_json(CONFIG / "politica-organizacion.json")


@pytest.fixture
def request_fixture():
    def load(name: str, **changes: Any) -> dict[str, Any]:
        request = read_json(FIXTURES / f"request-{name}.json")
        request.update(changes)
        return request
    return load


@pytest.fixture
def peru_request(request_fixture):
    def make(rights: list[str]) -> dict[str, Any]:
        request = request_fixture("access", policy_id="PE-LEY29733", request_types=rights)
        request.pop("request_type")
        return request
    return make


@pytest.fixture
def build(profiles, records):
    def run(request: dict[str, Any], organization: dict[str, Any] | None = None) -> dict[str, Any]:
        return build_case(copy.deepcopy(request), records, profiles, generated_at=GENERATED_AT,
                          source_hashes=HASHES, organization=organization)
    return run


@pytest.fixture
def service_ctx(tmp_path):
    """Contexto con BD, handoffs, exportaciones y política en directorios temporales; LLM simulados."""
    import shutil
    from datetime import datetime, timezone

    from dsar.services.context import ServiceContext, Settings
    from dsar.storage.sqlite import SqliteRepository
    from support import FakeProvider

    config = tmp_path / "config"
    config.mkdir()
    shutil.copyfile(CONFIG / "politica-organizacion.json", config / "politica-organizacion.json")
    shutil.copyfile(CONFIG.parent / "knowledge" / "references" / "organizacion-politica-interna.md",
                    config / "organizacion-politica-interna.md")
    settings = Settings(
        db_path=tmp_path / "data" / "dsar.sqlite3", handoff_dir=tmp_path / "handoffs", export_dir=tmp_path / "exports",
        org_policy_path=config / "politica-organizacion.json", org_text_path=config / "organizacion-politica-interna.md",
        org_history_dir=config / "historial", warmup=False,
    )
    providers = {"ollama": FakeProvider("ollama"), "gemini": FakeProvider("gemini", cloud=True)}
    return ServiceContext(settings=settings, repository=SqliteRepository(settings.db_path), providers=providers,
                          clock=lambda: datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc),
                          rag_method="bm25-stem-syn-title", semantic=False)


@pytest.fixture
def client(service_ctx):
    from fastapi.testclient import TestClient

    from dsar.api.main import create_app

    with TestClient(create_app(service_ctx)) as test_client:
        yield test_client
