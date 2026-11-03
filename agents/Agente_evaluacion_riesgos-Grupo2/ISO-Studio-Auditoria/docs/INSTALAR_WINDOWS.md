# Instalación completa en Windows para cada compañero

## 0. Preparar programas

Comprueba en PowerShell:

```powershell
wsl --version
docker --version
docker compose version
docker info
node --version
npm --version
git --version
```

`docker info` debe presentar información bajo `Server:`. Si falla, abrir Docker Desktop y esperar **Engine running**. Docker requiere el backend de WSL 2. El proyecto local completo necesita conexión a Internet para Gemini y las descargas iniciales.

## 1. Obtener el código

```powershell
git clone https://github.com/OWNER/REPO.git
cd REPO
```

**Sustituye `OWNER/REPO` por el enlace real del repositorio** cuando se publique. Alternativamente, descargar el ZIP del repositorio, extraerlo y abrir PowerShell en la carpeta raíz.

## 2. Crear el secreto local de Qdrant

```powershell
Copy-Item '.\infra\.env.example' '.\infra\.env'
$clave = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
(Get-Content '.\infra\.env') -replace '^QDRANT_API_KEY=.*$', "QDRANT_API_KEY=$clave" | Set-Content -Encoding ASCII '.\infra\.env'
```

El archivo `infra/.env` queda en la PC y está excluido por Git. **Cada compañero tendrá una clave diferente**. No publiques capturas de ese archivo.

## 3. Iniciar infraestructura

```powershell
docker compose -f '.\infra\compose.yaml' up -d
docker compose -f '.\infra\compose.yaml' ps
```

Esperar servicios `n8n` y `qdrant` en estado `Up`. Visita <http://localhost:5678> y crea una cuenta n8n **local**, distinta de n8n Cloud. Qdrant se accede internamente como `http://qdrant:6333` desde n8n; el puerto 6333 **no** está abierto al navegador por seguridad.

## 4. Importar los cuatro workflows

En `n8n/workflows/` encontrarás:

1. `Skill_Evaluacion_Riesgos_27701.json` → disparador subworkflow + Edit Fields.
2. `Skill_Artefactos_ISO_Studio.json` → procedimiento para Markdown, PDF/DOCX y Mermaid.
3. `RAG_ISO27701.json` → formulario PDF → Data Loader → Embeddings Gemini → Qdrant colección `iso27701_2025`.
4. `Agente_Evaluacion_Riesgos.json` → chat → agente Gemini + Simple Memory + Qdrant + dos Skills.

n8n → Create Workflow → menú `...` → **Import from File**. Importa y guarda en ese orden. **IMPORTANTE:** los workflows son plantillas reproducibles, NO los exports exactos de tu n8n final. Si el equipo exporta los cuatro workflows ya configurados desde la PC principal, prioriza esos exports (tras limpiar secretos).

## 5. Credenciales propias (no incluidas)

En <https://aistudio.google.com/apikey> crear la API Key de Gemini. Introducirla directamente en las credenciales del nodo `Google Gemini Chat Model` y **ambos** nodos `Embeddings Google Gemini` de agente y RAG. No introducirla en los `.env` del repositorio, ni enviarla por chat. Seleccionar un modelo disponible con la cuota de la cuenta; el modelo original es `models/gemini-3.5-flash-lite` si aparece disponible.

En cada nodo Qdrant, crear una credencial **Qdrant API**:

- URL: `http://qdrant:6333`.
- API Key: valor que guardaste en `infra/.env`, después de `QDRANT_API_KEY=`.
- Operación del nodo del RAG: `Insert Documents`.
- Operación del nodo del agente: `Retrieve Documents (As Tool for AI Agent)`.
- Colección **idéntica** en ambos: `iso27701_2025` (modo `By ID`).
- Límite en el agente: `5`; incluir metadatos: sí.
- Modelo de embeddings: el mismo en inserción y búsqueda.

Los flujos importados no copian las API Keys. Si ves un triángulo rojo, abre el nodo y configura sus credenciales/propiedades obligatorias.

## 6. Vincular Skills a la nueva instalación

En `Agente_Evaluacion_Riesgos`, abre los nodos `obtener_skill_evaluacion` y `obtener_skill_artefactos`: `Source=Database`, `Workflow=From list` y selecciona los workflows importados por nombre. Esto es fundamental porque los IDs del n8n original cambian al importar.

Comprobar que la descripción del segundo indique invocación al solicitar PDF, Word, informes y Mermaid. Publicar Skills si tu versión lo requiere. En el modelo de IA, verificar que la instrucción de sistema conserva el bloque ISO Studio sobre generación de Markdown y ` ```mermaid `.

## 7. Activar chat para React

En el nodo `When chat message received` de `Agente_Evaluacion_Riesgos`:

1. `Make Chat Publicly Available`: habilitado para uso **solo local**.
2. `Mode`: `Embedded Chat`.
3. `Response Mode`: `When Last Node Finishes`.
4. Guarda y **Publish**.
5. Copia la URL de producción exacta (`.../webhook/<id>/chat`). No uses `/webhook-test/...` ni el host de n8n Cloud.

Se permite un webhook público únicamente porque el puerto 5678 está vinculado a 127.0.0.1. **No publiques ese puerto en Internet** sin un sistema de autenticación y control de acceso.

## 8. Iniciar frontend

Abre otra ventana de PowerShell:

```powershell
cd frontend
npm install
Copy-Item '.env.example' '.env'
notepad '.env'
```

Establece como mínimo:

```
N8N_CHAT_URL=http://127.0.0.1:5678/webhook/ID_REAL_DE_CHAT/chat
PORT=4317
```

Reemplaza `ID_REAL_DE_CHAT` por el ID que se ve en tu n8n. **No utilices un ID antiguo del proyecto de otra persona.**

```powershell
npm run dev
```

Visita <http://127.0.0.1:5173>. El servidor Express escucha `127.0.0.1:4317`. Verifica la configuración: <http://127.0.0.1:4317/api/status> debería responder con JSON y `configured: true` (esto no certifica conexión; el chat real sí).

## 9. Cargar corpus de demostración (sin usar texto ISO)

Para pruebas puedes usar `examples/Documento_Prueba_FARO.pdf` mediante `RAG_ISO27701`. **Antes de cargarlo, cambia temporalmente** la colección del nodo RAG a `prueba_rag_faro`, ejecuta el formulario y carga el PDF. Después cambia la colección del Qdrant Tool del agente a `prueba_rag_faro` y pregunta por FARO-7429 y la revisión del martes 18:00. Finalmente vuelve a establecer `iso27701_2025` en ambos flujos. No mezcles documentos ficticios con la norma.

La norma ISO no se distribuye en este repositorio. Si el equipo tiene una copia autorizada, debe cargarla localmente y validar que las citas contienen cláusulas precisas. Qdrant crea la colección en la primera inserción; tener el nodo configurado no significa que exista ya información.

## 10. Comandos útiles

```powershell
# Detener solamente frontend: Ctrl+C en su terminal
# Detener contenedores sin eliminar datos:
docker compose -f '.\infra\compose.yaml' stop
# Iniciarlos nuevamente:
docker compose -f '.\infra\compose.yaml' start
# Reiniciarlos sin pérdida de datos:
docker compose -f '.\infra\compose.yaml' restart n8n qdrant
# Consultar logs:
docker compose -f '.\infra\compose.yaml' logs --tail=60 n8n
```

**Nunca uses `docker compose down -v`**: elimina los volúmenes de base de datos y perderías usuarios, workflows y vectores.

## 11. Limitaciones

- Es local, no una plataforma en la nube o multiusuario.
- Gemini API depende de Internet y su cuota.
- Las plantillas JSON requieren recrear credenciales y vincular Skills tras importar.
- No permite subir o editar archivos arbitrarios del usuario desde React.
- El documento normativo y el historial de ejecución no están en Git.
