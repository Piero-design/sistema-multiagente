-- Flows between agents (orchestrator-owned). Idempotent.
ALTER TABLE orchestrator.handoff ADD COLUMN IF NOT EXISTS delivery_status text;     -- entregado | sin_receptor | pendiente_humano
ALTER TABLE orchestrator.handoff ADD COLUMN IF NOT EXISTS delivery_detail jsonb;
ALTER TABLE orchestrator.handoff ADD COLUMN IF NOT EXISTS flow_run_id uuid;

CREATE TABLE IF NOT EXISTS orchestrator.flow_run (
    id          uuid PRIMARY KEY,
    flow        text        NOT NULL,
    status      text        NOT NULL CHECK (status IN ('running','succeeded','failed')),
    steps       jsonb       NOT NULL DEFAULT '[]'::jsonb,   -- real executions chained, in order
    result      jsonb,
    error       text,
    created_at  timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz
);
-- No GRANT here: the orchestrator_rw role is created later by database/roles/00_agent_roles.sql,
-- which grants SELECT/INSERT/UPDATE on ALL tables of the orchestrator schema (including this one).
