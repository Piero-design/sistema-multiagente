-- Pruebas de las reglas que impone el motor (plan §11, 02_reglas).
-- Requiere la extensión cargada y al menos un expediente migrado.
--   psql -d gestitel_revision -f bd/pruebas/02_reglas.sql
-- Cada prueba imprime OK o FALLA. Todo ocurre dentro de una transacción que se revierte.
\set ON_ERROR_STOP on
SET search_path TO demo, public;
BEGIN;

CREATE TEMP TABLE resultado (n serial, prueba text, ok boolean);

CREATE FUNCTION pg_temp.debe_fallar(p_prueba text, p_sql text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    BEGIN
        EXECUTE p_sql;
        INSERT INTO resultado (prueba, ok) VALUES (p_prueba, false);
    EXCEPTION WHEN OTHERS THEN
        INSERT INTO resultado (prueba, ok) VALUES (p_prueba || ' → ' || left(SQLERRM, 70), true);
    END;
END $$;

-- Expediente de prueba: el primero cargado, con su historial vacío
SELECT assessment_code AS exp FROM core_dpaassessment
 WHERE NOT EXISTS (SELECT 1 FROM core_dpaapproval p WHERE p.assessment_id = core_dpaassessment.id)
 ORDER BY id LIMIT 1 \gset

SELECT pg_temp.debe_fallar('Puntaje 120 rechazado',
       format('UPDATE core_dpaassessment SET score = 120 WHERE assessment_code = %L', :'exp')) \gset
SELECT pg_temp.debe_fallar('Rol de tercero inválido rechazado',
       'UPDATE core_thirdparty SET pims_role = ''X'' WHERE id = (SELECT min(id) FROM core_thirdparty)') \gset
SELECT pg_temp.debe_fallar('Estado de control inválido rechazado',
       'UPDATE core_dpacontrolresult SET result_status = ''Z'' WHERE id = (SELECT min(id) FROM core_dpacontrolresult)') \gset
SELECT pg_temp.debe_fallar('Legal antes que el DPO rechazado',
       format('SELECT agente7_registrar_decision(%L, ''Legal'', ''aprobar'', ''Ana'', ''Asesoría Legal'', ''ok'')', :'exp')) \gset
SELECT pg_temp.debe_fallar('Guardar dos veces la misma auditoría rechazado',
       format('SELECT agente7_guardar_auditoria((SELECT result_json FROM core_dpaassessment WHERE assessment_code = %L), NULL, 1)', :'exp')) \gset

-- Flujo correcto: DPO aprueba → Pendiente Legal; Legal aprueba → Aprobado
INSERT INTO resultado (prueba, ok)
SELECT 'DPO aprueba → estado L', agente7_registrar_decision(:'exp', 'DPO', 'aprobar', 'Luis', 'Oficial de Datos Personales', 'Conforme') = 'L';
SELECT pg_temp.debe_fallar('Segunda decisión del DPO rechazada',
       format('SELECT agente7_registrar_decision(%L, ''DPO'', ''rechazar'', ''Luis'', ''DPO'', ''cambio'')', :'exp')) \gset
INSERT INTO resultado (prueba, ok)
SELECT 'Legal aprueba → estado A', agente7_registrar_decision(:'exp', 'Legal', 'aprobar', 'Ana', 'Asesoría Legal', 'Visto bueno') = 'A';
SELECT pg_temp.debe_fallar('UPDATE de una aprobación rechazado',
       'UPDATE core_dpaapproval SET decision = ''R''') \gset
SELECT pg_temp.debe_fallar('DELETE de una aprobación rechazado',
       'DELETE FROM core_dpaapproval') \gset

SELECT CASE WHEN ok THEN 'OK   ' ELSE 'FALLA' END || ' ' || prueba AS "Pruebas de reglas" FROM resultado ORDER BY n;
SELECT count(*) FILTER (WHERE ok) || '/' || count(*) || ' pruebas correctas' AS total FROM resultado;

ROLLBACK;
