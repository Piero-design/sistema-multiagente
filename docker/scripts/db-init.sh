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

if [ -f /database/seed_demo.sql ]; then
  echo "[db-init] labeled demo seed"
  psql -v ON_ERROR_STOP=1 -q -f /database/seed_demo.sql
fi
echo "[db-init] done"
