# Problemas habituales

| Síntoma | Causa probable / acción |
|---|---|
| `failed to connect to docker API ...dockerDesktopLinuxEngine` | Iniciar Docker Desktop y esperar «Engine running». `wsl --shutdown` si WSL se bloquea; reiniciar Docker. |
| `docker compose ps` muestra Qdrant/n8n detenidos | `docker compose -f .\infra\compose.yaml up -d`; inspeccionar `logs`. |
| n8n abre pero no hay workflows | Instalación nueva: importar los 4 JSON; no se migran volúmenes desde otra PC. |
| Triángulo rojo en Gemini | Crear credencial Gemini y seleccionar modelo soportado. |
| Triángulo rojo en Qdrant | Definir credencial, modo, colección `iso27701_2025`, embeddings conectados. |
| Tool workflow no devuelve Skill | En cada `obtener_skill_*`, volver a seleccionar el subworkflow local. |
| React muestra «Vista previa» | Completar `frontend/.env`, publicar Chat Trigger y reiniciar `npm run dev`. |
| `Cannot GET /api/status**` | URL incorrecta: usar `http://127.0.0.1:4317/api/status` sin asteriscos. |
| Chat da 404 desde React | Usar URL de PRODUCCIÓN de n8n (`/webhook/`, no `/webhook-test/`) y publicar agente. |
| Qdrant busca pero no halla ISO | Primero cargar PDF autorizado a `iso27701_2025`; confirmar embeddings iguales. |
| Mermaid aparece como texto | Modelo debe devolver ` ```mermaid ... ``` ` válido; comprobar renderer React. |
| PDF/Word no descarga | Verificar API Express :4317 y `npm install`, revisar errores en terminal. |
| Puerto 5678 ocupado | Hay otro n8n. Detener/coordinar puertos; NO borrar contenedores ajenos. |

### Diagnóstico rápido

```powershell
docker compose -f '.\infra\compose.yaml' ps
docker compose -f '.\infra\compose.yaml' logs --tail=40 n8n
Invoke-RestMethod http://127.0.0.1:4317/api/status
```
