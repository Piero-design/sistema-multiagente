"""Live progress of an execution: what an agent is reading or doing right now.
The orchestrator sets the current execution id when it starts a run; an adapter that can see its agent's progress calls
`report()` and the line is stored as an `actividad` event, which the flows page shows step by step."""
from __future__ import annotations

import contextvars

from backend.services import db

current_execution: contextvars.ContextVar = contextvars.ContextVar("current_execution", default=None)


def report(agent_id: str, text: str) -> None:
    eid = current_execution.get()
    if not eid or not text:
        return
    try:
        db.execute("INSERT INTO orchestrator.event (execution_id, agent_id, kind, message) VALUES (%s,%s,'actividad',%s)",
                   (eid, agent_id, str(text)[:300]))
    except Exception:  # noqa: BLE001  progress must never break an execution
        pass
