-- One PostgreSQL role per agent, same pattern as agents/Agente_terceros_dpa-Grupo5/bd/roles_agente7.sql:
-- read the whole PIMS (schema demo), write only where justified.
-- Today no agent except Group 5 writes to Gestitel (G1/G3/G4/G8 keep private stores),
-- so the others are read-only. Widen a grant only through a reviewed migration.
-- Run as the superuser: psql -v schema=demo -v pw_g1=... -f 00_agent_roles.sql  (passwords come from .env)
\set ON_ERROR_STOP on
\if :{?schema}
\else
  \set schema demo
\endif

DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['agente_g1','agente_g2','agente_g3','agente_g4','agente_g7','agente_g8','orchestrator_rw']
  LOOP
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('CREATE ROLE %I NOLOGIN', r);
    END IF;
  END LOOP;
END $$;

SELECT format('GRANT CONNECT ON DATABASE %I TO agente_g1, agente_g2, agente_g3, agente_g4, agente_g7, agente_g8, orchestrator_rw', current_database()) \gexec
SELECT format('GRANT USAGE ON SCHEMA %I TO agente_g1, agente_g2, agente_g3, agente_g4, agente_g7, agente_g8, orchestrator_rw', :'schema') \gexec
SELECT format('GRANT SELECT ON ALL TABLES IN SCHEMA %I TO agente_g1, agente_g2, agente_g3, agente_g4, agente_g7, agente_g8, orchestrator_rw', :'schema') \gexec

-- No agent role can read credentials tables.
SELECT format('REVOKE ALL ON %I.auth_user FROM agente_g1, agente_g2, agente_g3, agente_g4, agente_g7, agente_g8', :'schema') \gexec

-- Orchestrator: owns its own schema only.
GRANT USAGE ON SCHEMA orchestrator TO orchestrator_rw;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA orchestrator TO orchestrator_rw;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA orchestrator TO orchestrator_rw;

-- Orchestrator writes ONE generic audit row per agent execution into Gestitel's security log
-- (free-text action/module + jsonb detail; never the agent input or any personal data).
SELECT format('GRANT INSERT ON %I.core_securitylog TO orchestrator_rw', :'schema') \gexec
