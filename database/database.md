# database

Base operacional compartida: **PostgreSQL** (Gestitel), cargada desde `gestitel_base_de_datos.sql`, el script del profesor. **Nunca se edita.**

- Se carga con `psql -f` desde el contenedor `db-init` (el volcado usa `\set` y `\restrict`), una sola vez: si el esquema `demo` existe se omite.
- Esquemas: `public` (plataforma) y `demo` (empresa de demostración con ISO/IEC 27001 + 27701 y tablas por dominio: `core_trainingassignment`, `core_riskevaluation`, `core_arcorequest`, `core_audit`, `core_asset`, `core_annexacontrol`, `core_incident`, entre otras).
- `migrations/001_orchestrator.sql`: esquema `orchestrator` (ejecuciones, eventos, handoffs). Idempotente.
- `roles/00_agent_roles.sql`: un rol por agente (patrón del Grupo 5): lectura del PIMS sin acceso a `auth_user`; escritura solo donde se justifique. Hoy ningún agente escribe en Gestitel salvo, de forma opcional, el Grupo 5 con sus propios scripts (`agents/Agente_terceros_dpa-Grupo5/bd/`, no activados).
- `extensions/` y `seed_demo.sql`: vacíos; no se inventan datos. Si se añade una semilla, debe marcarse como "datos de demostración".
- Los agentes 1, 3, 4 y 8 conservan sus almacenes privados (SQLite o archivos).
- Los dos scripts de Gestitel (este y el de `Agente_terceros_dpa-Grupo5/bd/`) son idénticos salvo por los saltos de línea.
