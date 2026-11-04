# database

Base operacional compartida: **PostgreSQL** (Gestitel), cargada desde `gestitel_base_de_datos.sql`, el script del profesor. **Nunca se edita.**

- Se carga con `psql -f` desde el contenedor `db-init` (el volcado usa `\set` y `\restrict`), una sola vez: si el esquema `demo` existe se omite.
- Esquemas: `public` (plataforma) y `demo` (empresa de demostración con ISO/IEC 27001 + 27701 y tablas por dominio: `core_trainingassignment`, `core_riskevaluation`, `core_arcorequest`, `core_audit`, `core_asset`, `core_annexacontrol`, `core_incident`, entre otras).
- `migrations/001_orchestrator.sql`: esquema `orchestrator` (ejecuciones, eventos, handoffs). Idempotente.
- **Grupo 5 no modifica la base del docente** (por defecto). Guarda sus auditorías en archivos del agente (`datos/registro/*.json` y `*.md`, descargables desde su página) y solo **lee** Gestitel para usarlo como contexto de la organización (opción `contexto: bd | ambos` al auditar). `db-init` crea únicamente el rol de solo lectura `agente_g5_lectura` (`default_transaction_read_only = on`, sin acceso a `auth_user`); no crea tablas ni filas. La consulta toca solo tablas del script del docente: `core_process`, `core_asset`, `core_personaldataoperation`, `core_personaldataimpactassessment`, `core_riskevaluation`, `core_gapannexaassessment` + `core_annexacontrol`, `core_document` y `core_systemsettings`.
- La **extensión propia del Grupo 5** (`agents/Agente_terceros_dpa-Grupo5/bd/agente7_terceros_dpa.sql`: 6 tablas, 5 vistas, 2 funciones, y `roles_agente7.sql`, que además inserta 3 usuarios en `auth_user`) queda **desactivada**. Se activa solo con `G5_BD_EXTENSION=true` en `.env` (con `G5_DB_USER=agente7` y `G5_DB_PASSWORD`), sobre una base nueva.
- `roles/00_agent_roles.sql`: un rol por agente (patrón del Grupo 5): lectura del PIMS sin acceso a `auth_user`; escritura solo donde se justifique. 
- `extensions/` y `seed_demo.sql`: vacíos; no se inventan datos. Si se añade una semilla, debe marcarse como "datos de demostración".
- Los agentes 1, 3, 4 y 8 conservan sus almacenes privados (SQLite o archivos).
- Los dos scripts de Gestitel (este y el de `Agente_terceros_dpa-Grupo5/bd/`) son idénticos salvo por los saltos de línea.
- **Los demás agentes siguen sin escribir en Gestitel.** No se hizo porque (1) los códigos de las listas de valores de las tablas de negocio (`incident_type`, `status`, `classification`…) están en los modelos Django y no en la base, y (2) G3 no debe guardar datos del solicitante. Ver `docs/integration/RESULTADOS_PRUEBAS.md`.
- **Bitácora común para todos los agentes:** el orquestador inserta una fila por ejecución en `demo.core_securitylog` (`username='orquestador'`, `action='agent_execute'`, `module`=agente, `detail` con id de ejecución, acción, estado, modo LLM y duración). Solo metadatos: nunca la entrada ni la salida del agente. Es el único uso de Gestitel para G1, G2, G3, G4, G7 y G8. Si el Gestitel del profesor valida valores de `action`, hay que ajustarlo.
