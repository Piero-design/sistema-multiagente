# Agente_derechos_dsar — Grupo 3

**Responsabilidad:** Gestionar las solicitudes de derechos de titulares de datos (DSAR: Data Subject Access Requests).

Registra peticiones de acceso, rectificación, supresión u oposición; coordina su trámite dentro de los plazos legales; y hace seguimiento hasta la resolución.

## Skills
- `registrar_solicitudes/` — captura y valida nuevas solicitudes DSAR
- `gestionar_derechos/` — tramita ejercicio de derechos (acceso, supresión, etc.)
- `seguimiento_solicitudes/` — monitorea estado y plazos de cada solicitud

## Implementación

La implementación del Grupo 3 está en esta carpeta:

- [SKILL.md](SKILL.md): skill principal, elige entre las 3 skills de [skills/](skills/).
- [GUIA_INTEGRACION.md](GUIA_INTEGRACION.md): instalación, servidor MCP (10 herramientas, entre ellas `dsar_controles` con los controles y cláusulas ISO/IEC 27701 de cada caso y `dsar_asistente`), pestaña «Gestión (DPO)» en la plataforma, handoffs a los agentes de Evidencia (Grupo 4), Terceros (Grupo 5) e Inventario (Grupo 6), y limitaciones actuales.
- [README.md](README.md): estructura y uso rápido.
- `src/dsar/`: motor determinista, RAG, servicios, SQLite y servidor MCP. `knowledge/`, `config/` y `rag_store/`: conocimiento normativo (ISO/IEC 27701:2025, Ley 29733), perfiles legales e índice RAG.

Principio: **el LLM nunca decide**; aprobar o rechazar solo lo hace una persona.
