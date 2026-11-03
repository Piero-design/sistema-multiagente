# Guía de integración — Grupo 3 / Agente de Derechos DSAR

Describe cómo usar este agente dentro del sistema de ocho agentes. Es orientativa: el equipo integrador puede adaptar la forma de ejecución, siempre que se respeten las reglas de la sección 5.

## 1. Qué hace y qué no

- **Hace:** registra solicitudes de derechos (información, acceso, portabilidad, rectificación, supresión, oposición), calcula plazos legales (Ley 29733, días hábiles), busca solo los registros del titular, retira datos de terceros, marca qué necesita revisión humana, consulta la norma con citas y prepara el borrador de respuesta.
- **No hace:** aprobar, rechazar, ejecutar cambios ni enviar comunicaciones. Lo decide una persona.

## 2. Instalación

Desde esta carpeta (`agents/Agente_derechos_dsar-Grupo3/`), con Python 3.12 o superior:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q tests/core
```

El RAG funciona con BM25 sin más dependencias. Los embeddings densos son opcionales (`pip install -e ".[dense]"`, ver `pyproject.toml`).

## 3. Cómo se usa: servidor MCP

```bash
python -m dsar.mcp.server            # stdio (Claude Code, Claude Desktop, orquestador)
python -m dsar.mcp.server --http     # streamable-http en http://127.0.0.1:8001/mcp
```

El puerto 8001 se puede cambiar con `--port`. El modo HTTP no tiene autenticación: úsalo solo en local.

| Herramienta | Parámetros | Devuelve |
|---|---|---|
| `dsar_crear_caso` | `principal_id`, `request_types`, `policy_id` (`PE-LEY29733`), `received_at`, `identity_status` (`pending`), `identity_reference`, `request_text` | Expediente: estado, plazos, motivos de revisión humana |
| `dsar_estado` | `case_id` | Estado, motivos HITL, aprobador, decisión humana y handoffs |
| `dsar_plazos` | `case_id` | Plazos por derecho |
| `dsar_calcular_plazos` | `request_types`, `received_at`, `policy_id` | Plazos sin crear expediente |
| `dsar_listar` | `status` (opcional) | Expedientes guardados |
| `dsar_borrador` | `case_id` | Borrador al titular (solo expedientes `APPROVED`) |
| `dsar_consultar_norma` | `pregunta`, `top_k` | Fragmentos citables de ISO/IEC 27701, Ley 29733 y política interna |
| `dsar_handoffs` | `case_id` (opcional) | Entregas para otros agentes |

Valores de `request_types`: `information`, `access`, `portability`, `rectification`, `erasure`, `objection`.

## 4. Handoffs: lo que este agente entrega a otros

Cuando una persona decide un expediente, el agente genera un sobre JSON por destinatario. Se leen con `dsar_handoffs` y se guardan como archivos en `handoffs/` (configurable con `DSAR_HANDOFF_DIR`). **Nunca llevan valores de datos personales**: solo referencias, sistemas, nombres de campos y hashes.

```json
{
  "from_agent": "dsar",
  "to_agent": "evidencia",
  "case_ref": "DSAR-...",
  "control_ref": "A.3.14",
  "action": "archivar_expediente",
  "payload": { "...": "..." },
  "requires_hitl": false,
  "created_at": "2026-11-03T10:00:00Z",
  "sha256": "..."
}
```

| `to_agent` | Agente del repositorio | Cuándo | Acción | Control |
|---|---|---|---|---|
| `evidencia` | Agente_evidencia_auditoria-Grupo4 | Siempre que hay decisión humana | `archivar_expediente` (hash del expediente, controles, quién decidió) | A.3.14 |
| `terceros` | Agente_terceros_dpa-Grupo5 | Rectificación, supresión u oposición aprobadas | `notificar_destinatarios` (sistemas y campos afectados) | A.1.3.8 |
| `inventario` | Agente_inventario_datos-Grupo6 | Sistemas declarados sin registros del titular | `confirmar_cobertura` (sistemas faltantes) | A.1.2.9 |

Las skills mencionan también al Agente de Incidentes (Grupo 8) y al DPO, pero **el código todavía no genera esos handoffs**.

**Por acordar con los demás grupos:** los nombres de `to_agent` y si los handoffs se leen como archivos, por MCP o desde la base compartida `database/sistema.db`.

## 5. Reglas que la integración no debe romper

1. Sin identidad verificada, cero registros buscados (`IDENTITY_PENDING`).
2. Toda acción queda como propuesta: `executed: false`.
3. Rectificación, supresión y oposición siempre requieren aprobación humana.
4. Los plazos salen del perfil legal; la política de la organización puede acortarlos, nunca alargarlos.
5. `APPROVED` y `REJECTED` solo por decisión de una persona. Ningún modelo ni cliente MCP puede registrarlos.
6. Un modelo en la nube solo recibe hechos minimizados, nunca registros ni el texto del solicitante.

## 6. Limitación actual: falta la interfaz de decisión humana

Esta entrega no incluye la API ni el frontend del proyecto original. Por eso **no hay una pantalla para que una persona verifique la identidad o apruebe un expediente**. Sin esa decisión los casos se quedan en `IDENTITY_PENDING`, `APPROVAL_REQUIRED` o `REVIEW`, y no se generan borradores ni handoffs.

Hoy esas acciones existen solo como funciones Python, para que las use una interfaz humana del sistema común:

- `dsar.services.cases.verify_identity(ctx, case_id, verified_by, method, ...)`
- `dsar.services.decisions.decide(ctx, case_id, reviewer, decision, note)`

Opciones: exponerlas en el panel común del sistema multiagente o reincorporar la interfaz del proyecto original del Grupo 3. **No deben exponerse como herramientas MCP**, porque un modelo podría aprobar casos.

## 7. Configuración (variables de entorno, opcionales)

| Variable | Por defecto | Uso |
|---|---|---|
| `DSAR_DB_PATH` | `data/dsar.sqlite3` | Base SQLite de expedientes |
| `DSAR_HANDOFF_DIR` | `handoffs/` | Carpeta de handoffs |
| `DSAR_EXPORT_DIR` | `exports/` | Exportaciones |
| `DSAR_UTC_OFFSET_HOURS` | `-5` | Zona horaria (Perú) |
| `DSAR_MAIL_*` | — | Entrada por correo (`python -m dsar.worker`); opcional |

Las rutas son relativas a esta carpeta. No guardes claves ni datos reales en el repositorio.
