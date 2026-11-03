"""Persistencia aislada del Grupo 6; no crea ni presupone tablas comunes."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .domain import normalizar

SCHEMA = """
CREATE TABLE IF NOT EXISTS inv6_assets (
    id TEXT PRIMARY KEY, organizacion TEXT NOT NULL, sistema_normalizado TEXT NOT NULL,
    revision_sha256 TEXT NOT NULL, documento TEXT NOT NULL, actualizado_en TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS inv6_org ON inv6_assets(organizacion, sistema_normalizado);
CREATE TABLE IF NOT EXISTS inv6_revisions (
    activo_id TEXT NOT NULL, revision_sha256 TEXT NOT NULL, documento TEXT NOT NULL,
    creado_en TEXT NOT NULL, PRIMARY KEY(activo_id, revision_sha256)
);
"""


class Repository:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def guardar(self, assets: list[dict[str, Any]]) -> dict[str, int]:
        if not assets:
            return {"creados": 0, "actualizados": 0, "sin_cambios": 0}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stats = {"creados": 0, "actualizados": 0, "sin_cambios": 0}
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            connection.executescript(SCHEMA)
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                for asset in assets:
                    old = connection.execute("SELECT revision_sha256 FROM inv6_assets WHERE id = ?", (asset["id"],)).fetchone()
                    if old and old[0] == asset["revision_sha256"]:
                        stats["sin_cambios"] += 1
                        continue
                    now = datetime.now(timezone.utc).isoformat()
                    document = json.dumps(asset, ensure_ascii=False, sort_keys=True)
                    connection.execute("""INSERT INTO inv6_assets VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET sistema_normalizado=excluded.sistema_normalizado,
                        revision_sha256=excluded.revision_sha256, documento=excluded.documento,
                        actualizado_en=excluded.actualizado_en""",
                        (asset["id"], asset["organizacion"], normalizar(asset["sistema"]), asset["revision_sha256"], document, now))
                    connection.execute("INSERT OR IGNORE INTO inv6_revisions VALUES (?, ?, ?, ?)",
                                       (asset["id"], asset["revision_sha256"], document, now))
                    stats["actualizados" if old else "creados"] += 1
            return stats
        finally:
            connection.close()

    def consultar(self, organizacion: str, sistema: str | None = None) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        # read-only: una consulta no crea tablas ni modifica una base de terceros.
        connection = sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
        try:
            query, params = "SELECT documento FROM inv6_assets WHERE organizacion = ?", [organizacion]
            if sistema:
                query += " AND sistema_normalizado = ?"
                params.append(normalizar(sistema))
            rows = connection.execute(query + " ORDER BY id", params).fetchall()
            return [json.loads(row[0]) for row in rows]
        finally:
            connection.close()
