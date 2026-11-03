# Agente de Derechos

**Responsabilidad:** Gestionar las solicitudes de derechos de titulares de datos (DSAR: Data Subject Access Requests).

Registra peticiones de acceso, rectificación, supresión u oposición; coordina su trámite dentro de los plazos legales; y hace seguimiento hasta la resolución.

## Skills

- `skills/registrar_solicitudes/` — captura y valida nuevas solicitudes DSAR
- `skills/gestionar_derechos/` — tramita ejercicio de derechos (acceso, supresión, etc.)
- `skills/seguimiento_solicitudes/` — monitorea estado y plazos de cada solicitud

Cada carpeta de skill tiene su `SKILL.md` y enlaza al conocimiento compartido de `knowledge/`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `skills/` | Las 3 skills: `registrar_solicitudes`, `gestionar_derechos`, `seguimiento_solicitudes` |
| `knowledge/` | Conocimiento común: referencias normativas, perfiles, plantilla de respuesta, guía de uso y evaluaciones. `knowledge/SKILL.md` es la skill completa que el código carga como instrucciones del asistente; no la muevas |
| `config/` | Perfiles legales (`PE-LEY29733`, `LAB-30`, `LAB-15-REVIEW`) y política de la organización |
| `rag_store/` | Índice RAG ya generado |
| `src/dsar/` | Motor determinista (`core`), RAG, asistente, servicios, almacenamiento SQLite y servidor MCP |
| `tests/` | Pruebas del motor (`pytest -q tests/core`), solo datos sintéticos |

Principio: **el LLM nunca decide.** Estados, plazos y revisión humana los calcula `dsar.core`; aprobar o rechazar solo lo hace una persona.

## Uso rápido

```bash
pip install -e ".[dev]"
pytest -q tests/core
python -m dsar.mcp.server          # herramientas MCP para la skill maestra
```
