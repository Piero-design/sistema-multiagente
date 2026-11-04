# Matriz de compatibilidad

| G | Tecnología | Ejecución | Skills / capacidades | Conocimiento | Conexión al LLM → gateway | Base de datos | UI original | Enfoque de integración | Riesgos |
|---|---|---|---|---|---|---|---|---|---|
| 1 | FastAPI, LangGraph, Chroma | Contenedor Python | Chat SSE, dashboards | `knowledge_base/`, Chroma | `LLM_PROVIDER=ollama` + `OLLAMA_HOST` | SQLite privada | `frontend/` | HTTP (login + SSE) | Sin tests; `pywin32` |
| 2 | React + Express, n8n, Qdrant | Contenedor Node (n8n+Express) + Qdrant | Skills en prompts de workflows | Qdrant (norma por OCR) | Copias de workflows con nodos OpenAI-compat | Qdrant | React original | HTTP a Express; reenvío TCP | Plantillas reconstruidas; bloqueo de alcance; PDF escaneado; tool-calling en Ollama |
| 3 | Python, MCP, BM25 | Contenedor Python | 8 herramientas MCP | `knowledge/`, `rag_store/` | No usa LLM por MCP | SQLite privada | Sin UI de decisión | MCP streamable-http (wrapper de host) | Acciones humanas aún no expuestas; loopback de Ollama no aplicable |
| 4 | FastAPI | Contenedor Python | M1/M2/M3 (API usa M2) | `references/` | `proveedor=ollama` + `url_base` por petición | Ninguna | Dashboard FastAPI | HTTP | Severidad por frases; CDN externos |
| 5 | n8n + Node + Python | Contenedor n8n | Auditar, perfilar, aprobar | Skills + `datos/` | `config_modelo.json` (proveedor openai) | Archivos; extensión PG opcional | Página n8n | Webhooks | Rutas absolutas; Execute Command |
| 6 | HTML estático | — | — | — | Ninguna | — | `index.html` | Stub `fuera_de_alcance` | No integrado |
| 7 | Flask + FAISS | Contenedor Python | Generar SoA, verificar | `knowledge/` | `OLLAMA_URL` + `OLLAMA_EMBED_MODEL` | Ninguna | `static/` | HTTP | Dependencia no declarada; embeddings en Ollama |
| 8 | Node + React | Contenedor (su Dockerfile) | 4 skills `brecha-*` | `knowledge/` | `GROQ_BASE_URL` | Archivos `salidas/` | `web/` | HTTP (job) | SDK sin URL en código; label de proveedor |
