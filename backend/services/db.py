"""PostgreSQL access: pooled, parameterized, transactional. Credentials come from the environment."""
from __future__ import annotations

import os
from contextlib import contextmanager

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

_pool: ConnectionPool | None = None


def _dsn() -> str:
    return (f"host={os.getenv('DB_HOST', 'postgres')} port={os.getenv('DB_PORT', '5432')} "
            f"dbname={os.getenv('DB_NAME', 'gestitel')} user={os.getenv('DB_USER', 'orchestrator_rw')} "
            f"password={os.getenv('DB_PASSWORD', '')}")


def pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(_dsn(), min_size=1, max_size=5, kwargs={"row_factory": dict_row}, open=True)
    return _pool


@contextmanager
def tx():
    """Transaction scope: commit on success, rollback on error."""
    with pool().connection() as conn:
        yield conn


def query(sql: str, params: tuple | dict = ()) -> list[dict]:
    with tx() as conn:
        return conn.execute(sql, params).fetchall()


def execute(sql: str, params: tuple | dict = ()) -> None:
    with tx() as conn:
        conn.execute(sql, params)


def ping() -> dict:
    try:
        row = query("SELECT current_database() AS db, "
                    "(SELECT count(*) FROM information_schema.tables WHERE table_schema='demo') AS demo_tables")[0]
        return {"ok": True, **row}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": type(e).__name__}
