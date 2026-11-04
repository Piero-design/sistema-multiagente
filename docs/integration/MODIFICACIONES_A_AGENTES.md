# Modificaciones a los agentes

## Integración original: agentes conservados; ampliación G4 en rama `agente4`

La integración original conservó los archivos de los agentes. En la rama `agente4`, G4 añade `audit_modes.py` y registra su router en `app_dashboard.py` para ofrecer M1. La skill, referencias y evaluación M2 se conservan. M3 consolida en el backend los resultados persistidos. El frontend común incorpora los tres modos, casos y carga de texto. Ver `GRUPO4_M1_M3.md`.

## Adaptaciones de despliegue (por agente)

| Grupo | Adaptación | Dónde | Por qué |
|---|---|---|---|
| 1 | `LLM_PROVIDER=ollama`, `OLLAMA_HOST` y `OLLAMA_MODEL` apuntan al gateway; rutas de SQLite/Chroma a un volumen | `docker-compose.yml` | Rama `ollama` del propio agente. |
| 1 | `pywin32` filtrado al instalar dependencias | `docker/agents/g1.Dockerfile` | Paquete solo de Windows; el `requirements.txt` original no se toca. |
| 1 | `init_db.py` (paso de instalación del grupo) se ejecuta solo si la tabla `usuarios` está vacía | `docker-compose.yml` | Sin esto no existen cuentas. |
| 3 | Wrapper que fija `HTTP_HOST="0.0.0.0"` antes de llamar a `server.main()` | `docker/agents/g3_run.py` | El servidor MCP escucha solo en 127.0.0.1 por constante del módulo. |
| 3 | Puente interno de decisión humana (`g3_human.py`, puerto 8002) junto al servidor MCP, que sigue igual | `docker/agents/g3_human.py`, `g3_start.sh` | `verify_identity` y `decide` existen solo como funciones; la interfaz de decisión no se entregó. El puente no es una herramienta de modelo: solo lo llama el backend para una persona autenticada. |
| 4 | M1 nativo añadido en `audit_modes.py`; M3 en `backend/services/audit_modes.py`. El adaptador envía `proveedor=ollama` y `url_base` del gateway en cada petición | `backend/adapters/agents.py` | El agente elige proveedor por petición. |
| 5 | `datos/config_modelo.json` se parchea al iniciar (`proveedor=openai`, `url_openai`=gateway); los flujos se regeneran con `instalar_flujos.py --importar` dentro del contenedor | `docker/agents/g5_entrypoint.sh` | Rutas absolutas dentro de los flujos. |
| 5 | Modo Gestitel nativo del grupo: `db-init` aplica su extensión y roles (sin modificarlos) y el contenedor crea la credencial «PIMS Postgres» y activa `config_bd.json` | `docker/scripts/db-init.sh`, `docker/agents/g5_entrypoint.sh` | Es lo que hace a mano su `configurar_bd.py`, de forma no interactiva. |
| 7 | `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`, `OLLAMA_TIMEOUT` apuntan al gateway; se instala `python-docx` | compose y `g7.Dockerfile` | El agente importa `docx` pero no lo declara en su `requirements.txt`. |
| 8 | `GROQ_API_KEY=gateway-managed`, `GROQ_BASE_URL`=gateway; no se define clave de Gemini ni Anthropic | `docker-compose.yml` | `groq-sdk` lee `GROQ_BASE_URL`; así el agente solo puede elegir el proveedor ligado al gateway. Se usa el `Dockerfile` original del grupo. |
| 2 | Copias adaptadas de los workflows (ver abajo) | `docker/agents/g2_adapt_workflows.py` | Los originales están atados a Gemini. |
| 2 | Reenvío TCP 4318 → 127.0.0.1:4317 | `g2_entrypoint.sh` | Express escucha solo en loopback por código. |

| Todos (gateway) | El gateway conserva y reinyecta la `thought_signature` de Gemini en las llamadas a herramientas | `llm-gateway/gateway.py` | Los clientes OpenAI de n8n la descartan y Gemini 3 responde 400. |
| 2 | El adaptador envía `webMode: off` | `backend/adapters/agents.py` | Evita la búsqueda web (Tavily) y que los datos salgan de la plataforma. |

## Grupo 2: cambios en las copias de los workflows (los JSON originales quedan intactos)

1. Nodo de chat `lmChatGoogleGemini` → `lmChatOpenAi`, con `baseURL` del gateway y `LLM_MODEL`.
2. Dos nodos `embeddingsGoogleGemini` (ingesta y recuperación) → `embeddingsOpenAi` con `LLM_EMBED_MODEL`.
3. Los nombres de nodo (incluido "Google Gemini Chat Model"), conexiones, prompts, herramientas y memoria no cambian.
4. Credenciales de Qdrant y del gateway se crean al iniciar (`n8n import:credentials`).
5. Defectos de las plantillas reconstruidas, corregidos solo en la copia: nodo `If` v2.4 → v2.3 (no existe en n8n 2.35); ids estables para los subflujos y re-enlace de los `toolWorkflow`; `webhookId` para el formulario de ingesta.
6. `embeddingBatchSize` de la ingesta 200 → 50.
7. Se mantiene `GEMINI_VISION_API_KEY` vacío: la visión de Gemini evita el gateway y queda desactivada.
8. `SCOPE_N8N_REVIEWED` **no** se activa por defecto (control humano del grupo). Se activa con `G2_SCOPE_N8N_REVIEWED=true` en `.env`.

## Hallazgos que no son modificaciones

- El servidor MCP de G3 es determinista y no llama a ningún LLM; la regla "la nube solo recibe hechos minimizados" afecta a su capa `assistant/llm`, que ese servidor no usa.
- Se desconoce si las plantillas de G2 se corresponden con el export real del grupo.
