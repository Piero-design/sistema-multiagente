#!/bin/sh
# One-shot, idempotent database init. Uses psql (the professor's dump has \set / \restrict meta-commands).
set -eu
export PGHOST="${PGHOST:-postgres}" PGUSER="${POSTGRES_USER}" PGPASSWORD="${POSTGRES_PASSWORD}" PGDATABASE="${POSTGRES_DB}"

until pg_isready -q; do sleep 1; done

HAS_DEMO=$(psql -tAc "SELECT 1 FROM information_schema.schemata WHERE schema_name='demo'")
if [ "$HAS_DEMO" = "1" ]; then
  echo "[db-init] schema demo already present: skipping professor's script"
else
  echo "[db-init] loading gestitel_base_de_datos.sql"
  psql -v ON_ERROR_STOP=1 -q -f /database/gestitel_base_de_datos.sql
fi

for f in /database/migrations/*.sql; do
  echo "[db-init] migration $f"
  psql -v ON_ERROR_STOP=1 -q -f "$f"
done

for f in /database/extensions/*.sql; do
  [ -e "$f" ] || continue
  echo "[db-init] extension $f"
  psql -v ON_ERROR_STOP=1 -q -v schema=demo -f "$f"
done

echo "[db-init] roles"
psql -v ON_ERROR_STOP=1 -q -v schema=demo -f /database/roles/00_agent_roles.sql
psql -v ON_ERROR_STOP=1 -q -v pw="$ORCHESTRATOR_DB_PASSWORD" <<'SQL'
SELECT format('ALTER ROLE orchestrator_rw LOGIN PASSWORD %L', :'pw') \gexec
SQL

# Group 5 (Agente 7). By default it does NOT change the professor's database: its audits are stored in files
# (datos/registro/) and it only READS Gestitel to build the organization context, with a read-only login role.
# The group's own extension (6 tables, 5 views, 2 functions, plus 3 rows in auth_user) is opt-in: G5_BD_EXTENSION=true.
if [ "${G5_BD_EXTENSION:-false}" = "true" ] && [ -f /g5bd/agente7_terceros_dpa.sql ]; then
  echo "[db-init] Group 5 extension + roles (agents/Agente_terceros_dpa-Grupo5/bd) — G5_BD_EXTENSION=true"
  psql -v ON_ERROR_STOP=1 -q -v schema=demo -f /g5bd/agente7_terceros_dpa.sql
  psql -v ON_ERROR_STOP=1 -q -v schema=demo -v clave_agente7="$AGENTE7_DB_PASSWORD" -v clave_lectura="$AGENTE7_RO_PASSWORD" -f /g5bd/roles_agente7.sql
else
  echo "[db-init] Group 5: read-only role agente_g5_lectura (no tables are created)"
  psql -v ON_ERROR_STOP=1 -q -v schema=demo -v pw="${AGENTE_G5_RO_PASSWORD:-agente_g5_ro_dev_pw}" <<'SQL'
SELECT format('CREATE ROLE agente_g5_lectura LOGIN PASSWORD %L', :'pw')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agente_g5_lectura') \gexec
SELECT format('ALTER ROLE agente_g5_lectura LOGIN PASSWORD %L', :'pw') \gexec
-- Every session of this role is read-only, even if a query tried to write.
ALTER ROLE agente_g5_lectura SET default_transaction_read_only = on;
SELECT format('GRANT CONNECT ON DATABASE %I TO agente_g5_lectura', current_database()) \gexec
SELECT format('GRANT USAGE ON SCHEMA %I TO agente_g5_lectura', :'schema') \gexec
SELECT format('GRANT SELECT ON ALL TABLES IN SCHEMA %I TO agente_g5_lectura', :'schema') \gexec
SELECT format('REVOKE ALL ON %I.auth_user FROM agente_g5_lectura', :'schema') \gexec
SQL
fi

if [ -f /database/seed_demo.sql ]; then
  echo "[db-init] labeled demo seed"
  psql -v ON_ERROR_STOP=1 -q -f /database/seed_demo.sql
fi
echo "[db-init] done"
