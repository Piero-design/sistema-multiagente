# Ejecutar con Ollama en otra computadora (pendiente de verificar)

> **Estado:** preparado, **no ejecutado**. En la laptop de desarrollo solo se validó `docker compose --profile ollama config`. Nada de esta lista cuenta como verificado hasta que se ejecute y se traigan los resultados.

## 1. Preparar

```bash
git clone <repo> && cd sistema-multiagente
cp .env.ollama.example .env          # LLM_MODE=ollama, LLM_MODEL=qwen2.5:7b, LLM_EMBED_MODEL=nomic-embed-text
# Poner contraseñas propias en POSTGRES_PASSWORD y ORCHESTRATOR_DB_PASSWORD
docker compose --profile ollama up --build -d
```

Requisitos orientativos: 16 GB de RAM para un modelo de 7B (más si se usa uno mayor); GPU opcional (bloque comentado `deploy` en `docker-compose.yml`). La primera ejecución descarga los modelos (`ollama-init`).

## 2. Comprobaciones

| # | Comando / acción | Esperado |
|---|---|---|
| 1 | `docker compose ps` | `ollama` healthy, `ollama-init` terminó (exit 0), resto arriba |
| 2 | `docker compose exec llm-gateway python -c "import urllib.request;print(urllib.request.urlopen('http://localhost:8080/api/tags').read())"` | Lista con el modelo de chat y el de embeddings |
| 3 | `docker compose exec ollama ollama list` | Ambos modelos descargados |
| 4 | `http://localhost:8080/configuracion` → "Probar conexión" | Respuesta real; modo `ollama`; sin aviso de datos fuera de la máquina |
| 5 | `pytest tests/integration -q` | Todos pasan (anotar el modo) |

## 3. Humo por agente (modo `ollama`)

- **G1** chat; **G4** auditar (comparar estructura, no texto); **G5** auditar contrato (2-5 min con modelo real); **G7** generar SoA (usa `/api/embed` y `/api/generate` a través del gateway); **G8** analizar reporte.
- **G2:** requiere un modelo con **tool-calling** y **re-ingestar la norma**, porque el tamaño de los vectores cambia (3072 con Gemini; el de `nomic-embed-text` es otro). Borrar la colección `iso27701_2025` en Qdrant y repetir la ingesta (ver `docs/installation/INSTALACION.md`).
- **G3:** su servidor MCP no usa LLM; no cambia entre modos.
- Registrar si el modelo elegido soporta tool-calling (G2, G8) y su calidad en español.

## 4. Qué traer de vuelta

Salida de los comandos 1–5, capturas del panel, y cualquier agente que quede `degradado`. Con eso se validan juntos.
