"""Repositorio SQLite (solo biblioteca estándar). Una conexión por operación."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    request_types TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    org_version TEXT,
    deadline_at TEXT NOT NULL,
    approver TEXT,
    package_json TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    reviewer TEXT NOT NULL,
    decision TEXT NOT NULL,
    note TEXT NOT NULL,
    at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS handoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    to_agent TEXT NOT NULL,
    control_ref TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    requires_hitl INTEGER NOT NULL DEFAULT 0,
    sha256 TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pendiente',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS llm_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    task TEXT,
    provider TEXT NOT NULL,
    model TEXT,
    prompt_sha256 TEXT NOT NULL,
    latency_s REAL,
    ok INTEGER NOT NULL,
    error TEXT,
    at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS inbound_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL UNIQUE,
    sender TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    received_at TEXT NOT NULL,
    in_reply_to TEXT,
    attachments_json TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    proposal_json TEXT,
    case_id TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    claimed_at TEXT,
    analysis_s REAL,
    decided_by TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS inbound_status ON inbound_messages (status, received_at, id);
CREATE INDEX IF NOT EXISTS inbound_sender ON inbound_messages (sender, received_at);
CREATE TABLE IF NOT EXISTS outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    kind TEXT NOT NULL,
    to_address TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'borrador',
    in_reply_to TEXT,
    message_id TEXT UNIQUE,
    sha256 TEXT,
    decided_by TEXT,
    reason TEXT,
    sent_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS outbox_case ON outbox (case_id, id);
"""
OUTBOX_FIELDS = frozenset({"subject", "body", "status", "message_id", "sha256", "decided_by", "reason", "sent_at"})
INBOUND_FIELDS = frozenset({"status", "reason", "proposal", "case_id", "attempts", "claimed_at", "analysis_s",
                            "decided_by"})


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _upsert_case(conn: sqlite3.Connection, package: dict[str, Any], payload: dict[str, Any] | None = None) -> None:
    rights = package.get("request_types") or [package["request_type"]]
    org = package.get("organization") or {}
    stamp = _now()
    conn.execute(
        """INSERT INTO cases (case_id, status, request_types, policy_id, org_version, deadline_at,
                              approver, package_json, payload_json, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(case_id) DO UPDATE SET status=excluded.status,
               deadline_at=excluded.deadline_at, approver=excluded.approver,
               package_json=excluded.package_json,
               payload_json=COALESCE(excluded.payload_json, cases.payload_json),
               updated_at=excluded.updated_at""",
        (package["case_id"], package["status"], ",".join(rights), package["policy"]["policy_id"],
         org.get("version") if org.get("applied") else None, package["deadline_at"],
         package["hitl"].get("approver"), _dumps(package), _dumps(payload) if payload else None,
         stamp, stamp),
    )


def _insert_decision(conn: sqlite3.Connection, case_id: str, reviewer: str, decision: str, note: str,
                     at: str) -> None:
    conn.execute("INSERT INTO decisions (case_id, reviewer, decision, note, at) VALUES (?, ?, ?, ?, ?)",
                 (case_id, reviewer, decision, note, at))


def _insert_handoff(conn: sqlite3.Connection, handoff: dict[str, Any]) -> None:
    conn.execute(
        """INSERT INTO handoffs (case_id, to_agent, control_ref, action, payload_json, requires_hitl,
                                 sha256, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (handoff["case_ref"], handoff["to_agent"], handoff["control_ref"], handoff["action"],
         _dumps(handoff["payload"]), int(handoff["requires_hitl"]), handoff["sha256"], handoff["created_at"]),
    )


class SqliteRepository:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            conn.executescript(SCHEMA)
            yield conn
            conn.commit()
        finally:
            conn.close()

    def save_case(self, package: dict[str, Any], payload: dict[str, Any] | None = None) -> None:
        with self.connect() as conn:
            _upsert_case(conn, package, payload)

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT package_json FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        return json.loads(row["package_json"]) if row else None

    def get_payload(self, case_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload_json FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        return json.loads(row["payload_json"]) if row and row["payload_json"] else None

    def list_cases(self, status: str | None = None) -> list[dict[str, Any]]:
        query = ("SELECT case_id, status, request_types, policy_id, org_version, deadline_at, approver, "
                 "updated_at FROM cases")
        params: tuple[Any, ...] = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        with self.connect() as conn:
            rows = conn.execute(query + " ORDER BY deadline_at, case_id", params).fetchall()
        return [dict(row) | {"request_types": row["request_types"].split(",")} for row in rows]

    def all_cases(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT package_json FROM cases ORDER BY created_at, case_id").fetchall()
        return [json.loads(row["package_json"]) for row in rows]

    def record_decision(self, case_id: str, reviewer: str, decision: str, note: str, at: str) -> None:
        with self.connect() as conn:
            _insert_decision(conn, case_id, reviewer, decision, note, at)

    def save_handoff(self, handoff: dict[str, Any]) -> None:
        with self.connect() as conn:
            _insert_handoff(conn, handoff)

    def save_decision(self, package: dict[str, Any], decision: dict[str, Any],
                      handoffs: list[dict[str, Any]]) -> None:
        """Expediente, decisión y handoffs en una sola transacción: o se guardan los tres o ninguno."""
        with self.connect() as conn:
            _upsert_case(conn, package)
            _insert_decision(conn, package["case_id"], decision["reviewer"], decision["decision"],
                             decision["note"], decision["at"])
            for handoff in handoffs:
                _insert_handoff(conn, handoff)

    def list_handoffs(self, case_id: str | None = None) -> list[dict[str, Any]]:
        query = ("SELECT case_id, to_agent, control_ref, action, payload_json, requires_hitl, sha256, status, "
                 "created_at FROM handoffs")
        params: tuple[Any, ...] = ()
        if case_id:
            query += " WHERE case_id = ?"
            params = (case_id,)
        with self.connect() as conn:
            rows = conn.execute(query + " ORDER BY id", params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            item["requires_hitl"] = bool(item["requires_hitl"])
            result.append(item)
        return result

    def log_llm_call(self, entry: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO llm_calls (case_id, task, provider, model, prompt_sha256, latency_s, ok, error, at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (entry.get("case_id"), entry.get("task"), entry["provider"], entry.get("model"),
                 entry["prompt_sha256"], entry.get("latency_s"), int(bool(entry.get("ok"))),
                 entry.get("error"), entry.get("at") or _now()),
            )

    def list_llm_calls(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM llm_calls ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) | {"ok": bool(row["ok"])} for row in rows]

    def add_inbound(self, item: dict[str, Any]) -> int | None:
        """Encola un correo; None si ya estaba (mismo Message-ID o mismo contenido)."""
        stamp = _now()
        with self.connect() as conn:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO inbound_messages (message_id, sha256, sender, subject, body, received_at,
                       in_reply_to, attachments_json, status, reason, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item["message_id"], item["sha256"], item["sender"], item["subject"], item["body"],
                 item["received_at"], item.get("in_reply_to"), _dumps(item.get("attachments", [])),
                 item["status"], item.get("reason"), stamp, stamp),
            )
            return cursor.lastrowid if cursor.rowcount else None

    def has_inbound(self, message_id: str, sha256: str) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT 1 FROM inbound_messages WHERE message_id = ? OR sha256 = ?",
                               (message_id, sha256)).fetchone()
        return row is not None

    def count_inbound_from(self, sender: str, since: str) -> int:
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM inbound_messages WHERE sender = ? AND received_at >= ?",
                               (sender, since)).fetchone()
        return int(row[0])

    def get_inbound(self, inbound_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM inbound_messages WHERE id = ?", (inbound_id,)).fetchone()
        return _inbound(row) if row else None

    def list_inbound(self, status: str | None = None, limit: int = 500,
                     case_id: str | None = None) -> list[dict[str, Any]]:
        clauses, params = [], []
        for column, value in (("status", status), ("case_id", case_id)):
            if value:
                clauses.append(f"{column} = ?")
                params.append(value)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM inbound_messages{where} ORDER BY received_at DESC, id DESC LIMIT ?",
                                (*params, limit)).fetchall()
        return [_inbound(row) for row in rows]

    def count_inbound(self) -> dict[str, int]:
        with self.connect() as conn:
            rows = conn.execute("SELECT status, COUNT(*) FROM inbound_messages GROUP BY status").fetchall()
        return {row[0]: int(row[1]) for row in rows}

    def claim_inbound(self, claimed_at: str, stale_before: str) -> dict[str, Any] | None:
        """Toma el correo pendiente más antiguo; recupera los que quedaron a medias antes de `stale_before`."""
        with self.connect() as conn:
            row = conn.execute(
                """UPDATE inbound_messages SET status = 'en_analisis', claimed_at = ?, attempts = attempts + 1,
                       updated_at = ?
                   WHERE id = (SELECT id FROM inbound_messages
                               WHERE status = 'recibido' OR (status = 'en_analisis' AND claimed_at < ?)
                               ORDER BY received_at, id LIMIT 1)
                   RETURNING *""",
                (claimed_at, claimed_at, stale_before),
            ).fetchone()
        return _inbound(row) if row else None

    def update_inbound(self, inbound_id: int, **fields: Any) -> None:
        unknown = set(fields) - INBOUND_FIELDS
        if unknown:
            raise ValueError(f"Campos desconocidos: {sorted(unknown)}")
        if "proposal" in fields:
            fields["proposal_json"] = _dumps(fields.pop("proposal"))
        columns = ", ".join(f"{name} = ?" for name in fields)
        with self.connect() as conn:
            conn.execute(f"UPDATE inbound_messages SET {columns}, updated_at = ? WHERE id = ?",
                         (*fields.values(), _now(), inbound_id))

    def add_outbox(self, item: dict[str, Any]) -> int:
        stamp = _now()
        with self.connect() as conn:
            cursor = conn.execute(
                """INSERT INTO outbox (case_id, kind, to_address, subject, body, in_reply_to, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (item["case_id"], item["kind"], item["to_address"], item["subject"], item["body"],
                 item.get("in_reply_to"), stamp, stamp),
            )
            return int(cursor.lastrowid)

    def get_outbox(self, outbox_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM outbox WHERE id = ?", (outbox_id,)).fetchone()
        return dict(row) if row else None

    def list_outbox(self, status: str | None = None, case_id: str | None = None) -> list[dict[str, Any]]:
        clauses, params = [], []
        for column, value in (("status", status), ("case_id", case_id)):
            if value:
                clauses.append(f"{column} = ?")
                params.append(value)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM outbox{where} ORDER BY id DESC", params).fetchall()
        return [dict(row) for row in rows]

    def update_outbox(self, outbox_id: int, **fields: Any) -> None:
        unknown = set(fields) - OUTBOX_FIELDS
        if unknown:
            raise ValueError(f"Campos desconocidos: {sorted(unknown)}")
        columns = ", ".join(f"{name} = ?" for name in fields)
        with self.connect() as conn:
            conn.execute(f"UPDATE outbox SET {columns}, updated_at = ? WHERE id = ?", (*fields.values(), _now(), outbox_id))

    def outbox_case(self, message_ids: list[str]) -> str | None:
        """Expediente del correo enviado con alguno de esos Message-ID (para asociar las respuestas)."""
        if not message_ids:
            return None
        marks = ", ".join("?" for _ in message_ids)
        with self.connect() as conn:
            row = conn.execute(f"SELECT case_id FROM outbox WHERE message_id IN ({marks}) LIMIT 1",
                               message_ids).fetchone()
        return row["case_id"] if row else None


def _inbound(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["attachments"] = json.loads(item.pop("attachments_json"))
    proposal = item.pop("proposal_json")
    item["proposal"] = json.loads(proposal) if proposal else None
    return item
