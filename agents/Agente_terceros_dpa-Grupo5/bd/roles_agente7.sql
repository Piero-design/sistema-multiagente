-- =============================================================================
-- Usuarios autores y roles de base de datos del Agente 7 (plan §4 y §9.3).
-- Se ejecuta como postgres DESPUÉS de agente7_terceros_dpa.sql. Idempotente.
--
--   psql -U postgres -d gestitel_revision -v clave_agente7=... -v clave_lectura=... -f roles_agente7.sql
--
-- Las contraseñas entran como variables de psql: no se escriben en este archivo.
-- =============================================================================
\set ON_ERROR_STOP on
\if :{?schema}
\else
  \set schema demo
\endif
\if :{?clave_agente7}
\else
  \echo 'Falta -v clave_agente7=...'
  \quit
\endif
\if :{?clave_lectura}
\else
  \echo 'Falta -v clave_lectura=...'
  \quit
\endif

SELECT set_config('search_path', :'schema' || ',public', false);

BEGIN;

-- 4.1 Identidades que firman los registros. password '!' = sin contraseña utilizable:
-- sirven para la trazabilidad, no para entrar a Gestitel.
INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
SELECT '!', false, u.username, u.first_name, u.last_name, u.email, false, true, now()
FROM (VALUES ('agente7', 'Agente 7', 'Terceros/DPA', 'agente7@unsa.edu.pe'),
             ('dpo',     'Nombre',   'DPO',          'dpo@unsa.edu.pe'),
             ('legal',   'Nombre',   'Legal',        'legal@unsa.edu.pe')) AS u(username, first_name, last_name, email)
WHERE NOT EXISTS (SELECT 1 FROM auth_user a WHERE a.username = u.username);

-- 4.2 Rol de n8n: lee todo el PIMS, escribe solo en su módulo y nunca modifica una aprobación.
SELECT format('CREATE ROLE agente7 LOGIN PASSWORD %L', :'clave_agente7')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agente7') \gexec
SELECT format('ALTER ROLE agente7 PASSWORD %L', :'clave_agente7') \gexec

-- 9.3 Rol del chat: solo lectura.
SELECT format('CREATE ROLE agente7_lectura LOGIN PASSWORD %L', :'clave_lectura')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agente7_lectura') \gexec
SELECT format('ALTER ROLE agente7_lectura PASSWORD %L', :'clave_lectura') \gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO agente7, agente7_lectura', current_database()) \gexec
SELECT format('GRANT USAGE ON SCHEMA %I TO agente7, agente7_lectura', :'schema') \gexec
SELECT format('GRANT SELECT ON ALL TABLES IN SCHEMA %I TO agente7, agente7_lectura', :'schema') \gexec

GRANT INSERT, UPDATE ON core_thirdparty, core_dpacontract, core_dpacontract_assets,
                        core_dpaassessment, core_dpacontrolresult TO agente7;
GRANT INSERT ON core_dpaapproval TO agente7;               -- solo inserción: historial inmutable
SELECT format('GRANT USAGE ON ALL SEQUENCES IN SCHEMA %I TO agente7', :'schema') \gexec

-- Las funciones se ejecutan con los permisos de quien llama (SECURITY INVOKER):
-- agente7_lectura puede invocarlas, pero sus INSERT fallan por falta de privilegios.
REVOKE ALL ON FUNCTION agente7_guardar_auditoria(jsonb, text, integer),
                       agente7_registrar_decision(text, text, text, text, text, text, timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION agente7_guardar_auditoria(jsonb, text, integer),
                          agente7_registrar_decision(text, text, text, text, text, text, timestamptz) TO agente7;

COMMIT;

SELECT id, username FROM auth_user WHERE username IN ('agente7', 'dpo', 'legal') ORDER BY id;
\echo 'Roles agente7 y agente7_lectura listos. El id de agente7 es el usuario_autor_id de n8n.'
