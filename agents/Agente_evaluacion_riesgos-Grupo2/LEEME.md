# Agente ISO/IEC 27701:2025 — Kit para n8n local

Este kit se preparó a partir de los **tres JSON originales entregados por el equipo**. Es una preparación para la importación; NO implica que el proyecto ya haya sido ejecutado en tu computadora.

## 1. Requisitos

- Docker Engine + Docker Compose v2 (Linux) o Docker Desktop (Windows/macOS).
- Internet para descargar las imágenes de Docker y consultar la API de Gemini.
- Una clave de API propia de Google Gemini (aistudio.google.com/apikey).
- RAM suficiente para ejecutar n8n y Qdrant. No necesita GPU mientras uses Gemini.

Comprueba: `docker --version` y `docker compose version`.

## 2. Inicia los servicios

Abre una terminal dentro de la carpeta que contiene `compose.yaml`:

```bash
cp .env.example .env
openssl rand -hex 32
```

Abre `.env` en tu editor y sustituye `CAMBIA_ESTA_CLAVE_POR_UN_SECRETO_LARGO` por la clave aleatoria del paso anterior. No compartas este archivo ni subas secretos a GitHub.

```bash
docker compose up -d
docker compose ps
```

Abre `http://localhost:5678` en el navegador y completa la creación de tu cuenta local de administrador de n8n.

**Nota:** para Windows PowerShell puedes copiar `.env.example` como `.env` con `Copy-Item .env.example .env`, y generar una clave con un gestor seguro de contraseñas (32+ caracteres).

El panel es accesible solo desde este equipo, por `127.0.0.1:5678`. Qdrant no publica puerto al host, solo se comunica con n8n en la red privada de Docker.

## 3. Importa los tres flujos por la interfaz de n8n

En el editor de n8n usa **... > Import from File** y selecciona, en este orden:

1. `workflows/Skill_Evaluacion_Riesgos_27701.json`
2. `workflows/RAG_ISO27701.json`
3. `workflows/Agente_Evaluacion_Riesgos.json`

Los tres JSON mantienen los nodos y conexiones de origen, pero se han retirado los IDs de credenciales del entorno cloud y la metadata de instancia; los workflows están inicialmente desactivados. El chat público está deshabilitado para pruebas locales.

## 4. Reconecta el Skill

Abre `Agente_Evaluacion_Riesgos`, selecciona `obtener_skill_evaluacion` y vuelve a elegir **el Skill que acabas de importar** en el selector de workflow. El identificador exportado por n8n Cloud NO es una referencia fiable en la nueva instancia. Guarda.

## 5. Crea una credencial nueva de Google Gemini

En n8n, crea una credencial de tipo **Google Gemini(PaLM) API** usando tu propia clave de Google AI Studio. No copies el ID antiguo del JSON.

En `Agente_Evaluacion_Riesgos` asigna esta credencial a:
- `Google Gemini Chat Model`
- `Embeddings Google Gemini`

En `RAG_ISO27701` asigna la misma credencial a:
- `Embeddings Google Gemini`

Comprueba que el modelo seleccionado sea accesible con tu API key (el JSON original indica `models/gemini-3.5-flash-lite`).

## 6. Prueba sin el libro, solo infraestructura

Prueba desde el chat de prueba del editor del workflow Agente:
- `Hola, ¿cuál es tu función?` — confirma que Gemini contesta.
- `¿Puedes ayudarme a evaluar riesgos de un proveedor?` — confirma que el nodo `obtener_skill_evaluacion` ejecuta el Skill y pide contexto.

Sin cargar previamente el PDF **NO** se puede validar recuperación RAG ni referencias exactas a la norma. Es correcto que el agente indique falta de conocimiento documental o que el almacén está vacío.

Las pruebas completas requieren cargar el PDF autorizado de la norma en el flujo RAG y ejecutar su ingesta, mientras sus nodos de almacenamiento sigan siendo `Simple Vector Store`.

## 7. Persistencia y mejoras futuras

El servicio de Qdrant ya estará corriendo, pero **los JSON conservan el `Simple Vector Store` original** por compatibilidad: el almacenamiento vectorial NO es persistente aún. Para activarlo:
1. En `RAG_ISO27701`, sustituye el nodo de inserción `Simple Vector Store` por `Qdrant Vector Store`, modo **Insert Documents**.
2. Configura credencial Qdrant con URL `http://qdrant:6333` y la clave `QDRANT_API_KEY` de `.env`.
3. Usa la colección `iso27701` y conecta el mismo cargador PDF y embeddings (o los elegidos posteriormente).
4. En `Agente_Evaluacion_Riesgos`, sustituye `buscar_iso27701` por `Qdrant Vector Store`, modo **Retrieve Documents (As Tool for AI Agent)**, con la misma colección, credencial y modelo de embeddings utilizado durante la ingesta.
5. Conecta el nuevo nodo al puerto de herramientas del agente y prueba que recupere documentos después de reiniciar los servicios.

IMPORTANTE: conserva la misma dimensión/modelo de embeddings al insertar y consultar una colección.

El PDF completo de ISO no se incluye en los JSON originales ni en este kit.

## 8. Operación básica

```bash
docker compose logs -f n8n      # Ver errores/arranque n8n
docker compose logs -f qdrant   # Ver errores/arranque Qdrant
docker compose stop            # Detener; conserva datos
docker compose start           # Volver a iniciar
docker compose down            # Elimina contenedores, mantiene volúmenes
docker compose ps              # Ver estado
```

No ejecutes `docker compose down -v`: borraría volúmenes y datos de los servicios. Respaldar los volúmenes es necesario antes de actualizar en producción.

## 9. Consideraciones para la siguiente etapa

- Hoy el prompt limita el agente principalmente a la *evaluación de riesgos*, NO a responder todas las preguntas que pudieran surgir de la norma. Habrá que ampliar el enrutamiento cuando definamos el uso académico final.
- El informe original documenta pruebas de activación y aclaración de contexto, no una validación exhaustiva de evaluación de riesgos completa.
- `Simple Memory` es memoria conversacional y NO sustituye al repositorio de documentos.
- El precio de n8n Community es independiente de los costes o cuotas de Gemini API.
- No publiques el chat en Internet hasta configurar autenticación, seguridad de la infraestructura y las condiciones de uso del material ISO.

## 10. Documentación oficial

- n8n Docker Compose: https://docs.n8n.io/deploy/host-n8n/install-options/install-using-docker-compose
- n8n importación: https://docs.n8n.io/build/manage-workflows/export-and-import
- Credencial Gemini: https://docs.n8n.io/integrations/builtin/credentials/googleai
- Vector Store en memoria: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.vectorstoreinmemory
- Qdrant node: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.vectorstoreqdrant
