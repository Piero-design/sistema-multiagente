# ISO Studio 7.2 — Gestión de Riesgos (paquete completo)

Agente académico delimitado por seis temas autorizados, basado en el extracto ISO/IEC 27701:2025 y en secciones seleccionadas del manual CISA 2024.

**Inicio:** abre `INSTALAR_PATCH_7_2_WINDOWS.md`. No requiere cambiar puertos, Docker ni instalar n8n nuevamente. Copia el `.env` de tu versión 7 para conservar Gemini, Tavily y los webhooks; descomprime siempre en carpeta nueva.

**Activación:** por defecto todas las operaciones de la aplicación están bloqueadas hasta adaptar manualmente los workflows n8n y crear una colección Qdrant aislada `iso_gr_2026`; después, establecer `SCOPE_N8N_REVIEWED=true`.

**Pruebas incluidas:** `npm run test:scope` (28 pruebas). Para comprobación completa en Windows: `npm install`, `npm run build`, `npm run test:parsers`, `npm run dev`.

**Contenido:** `scope-policy.json`, `server/lib/scope.js`, sistema de permisos para chat, web, visual y exportación, prompt `n8n/SYSTEM_MESSAGE_GR_7_2.md`, Code Node de guard y guía de filtrado RAG.

**Límites de seguridad:** la clasificación local es un filtro determinista, no una evaluación semántica infalible; tampoco altera directamente la instalación de n8n, las credenciales o el contenido ya almacenado en Qdrant. Para uso público no supervisado se necesita protección adicional, especialmente de los webhooks independientes.
