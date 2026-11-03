# ISO Studio 7.2 — Parche de Gestión de Riesgos

Este es el paquete integrado con React + Express (no una propuesta documental). Seis núcleos GR-01...GR-06 aprobados. Por seguridad inicia bloqueado mientras se revisan los workflows n8n y Qdrant. Sigue `INSTALAR_PATCH_7_2_WINDOWS.md` para instalar, aplicar el guard de Code a n8n y revisar la biblioteca de fuentes.

**Verificación local:** `npm run test:scope`; `npm run build` (si ya ejecutaste `npm install`).

**No se incluyen PDFs completos:** los documentos académicos se utilizarán desde tu instalación local, sin redistribuir copias.

**Límites:** el motor es una barrera determinista de alcance, con revisión de respuesta limitada. No sustituye un clasificador semántico robusto ni restringe automáticamente un webhook n8n accesible de forma independiente.
