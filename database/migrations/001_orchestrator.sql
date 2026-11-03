-- Orchestrator state. Idempotent. Lives in its own schema; the professor's script is never touched.
CREATE SCHEMA IF NOT EXISTS orchestrator;

CREATE TABLE IF NOT EXISTS orchestrator.execution (
    id           uuid PRIMARY KEY,
    agent_id     text        NOT NULL,
    action       text        NOT NULL,
    status       text        NOT NULL CHECK (status IN ('queued','running','succeeded','failed')),
    llm_mode     text,
    simulated    boolean     NOT NULL DEFAULT false,
    input_hash   text,
    result       jsonb,
    error        text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    started_at   timestamptz,
    finished_at  timestamptz
);

CREATE TABLE IF NOT EXISTS orchestrator.event (
    id           bigserial PRIMARY KEY,
    execution_id uuid REFERENCES orchestrator.execution(id) ON DELETE CASCADE,
    agent_id     text        NOT NULL,
    kind         text        NOT NULL,   -- submitted | started | finished | failed | health
    message      text,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orchestrator.handoff (
    id           bigserial PRIMARY KEY,
    from_agent   text NOT NULL,
    to_agent     text NOT NULL,
    envelope     jsonb NOT NULL,        -- as produced by the source agent (no personal data values)
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS execution_agent_idx ON orchestrator.execution (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS event_created_idx   ON orchestrator.event (created_at DESC);
