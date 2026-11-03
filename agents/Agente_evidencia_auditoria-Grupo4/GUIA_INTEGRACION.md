# Guía de integración — Grupo 4 / AuditPIMS

## Leer primero

**Esta guía es descriptiva y orientativa; no impone una arquitectura al sistema común.** Documenta el avance del Grupo 4 para facilitar su comprensión y reutilización. La IA y el equipo integrador pueden refactorizarlo, reorganizar archivos, unificar dependencias, reemplazar la API por llamadas internas, compartir el cliente de IA o adaptar las entradas y salidas según lo que beneficie a los ocho agentes.

No es obligatorio conservar nuestro dashboard, API HTTP, nombres de funciones, estructura de ejecución, proveedor ni modelo. Se priorizan los objetivos de auditoría, el conocimiento útil y la compatibilidad con el conjunto. El código entregado queda como referencia versionada; adaptar su implementación no implica descartar el avance previo. Las alternativas de esta guía son ejemplos y pueden combinarse o sustituirse por otra solución común.

Esta entrega conserva el avance previo del Grupo 4: skill, conocimientos, plantillas, dashboard, API, CLI, casos de demostración y material académico de apoyo. La lógica de los tres programas principales se conserva sin cambios respecto al proyecto de origen [AuditPIMS](https://github.com/Piero-design/AuditPIMS), commit `8249c53`.

El objetivo de la integración es reutilizar ese avance dentro del sistema de ocho agentes. La conexión con la skill maestra, la base SQLite compartida y el entorno Docker general todavía no está implementada en esta entrega. La elección de modelo, proveedor y forma de ejecución queda a cargo del equipo integrador.

Este documento describe el comportamiento actual del código. Para conocer las capacidades y límites reales, úsalo junto con el esquema de `/openapi.json`. El README previo se conserva como documentación del desarrollo y la exposición; sus porcentajes y ejemplos de resultados no son mediciones de datos compartidos del sistema integrado.

## Qué aporta cada archivo

- `auditoria-evidencias-pims/SKILL.md`: instrucciones y modos M1 (planificar), M2 (evaluar evidencias) y M3 (consolidar). Su existencia no crea por sí sola un proceso ejecutable.
- `auditoria-evidencias-pims/references/`: catálogo de controles, criterios de evaluación y resumen normativo que los programas cargan en el contexto del modelo.
- `auditoria-evidencias-pims/assets/`: plantillas de matriz e informe.
- `app_dashboard.py`: aplicación FastAPI, dashboard y endpoints. La ruta de auditoría con modelo solicita una evaluación M2.
- `auditor_con_ia.py`: CLI para evaluar texto y archivos usando proveedores de IA. La configuración de esta CLI y la de la API no son idénticas; para Ollama usar el contrato de la API descrito abajo.
- `probar_auditor.py`: ocho casos offline con dictámenes predefinidos y consolidación de demostración; no es un evaluador automático de documentos arbitrarios ni una suite de aserciones.
- `documento_prueba_*.txt`: evidencias de ejemplo para demostraciones.
- `GUION_EXPOSICION_*`: material de presentación del avance del equipo.
- `material_apoyo/`: análisis previos ISO 27701 en Markdown/PDF, scripts originales que generaron PDFs y comparación visual de hitos. Los generadores se conservan como fuente histórica: contienen rutas de salida locales y dependencias de fuentes de macOS que deben adaptarse antes de ejecutarlos en otra máquina. No son necesarios para iniciar el agente.

## Ejecutar la implementación existente

Desde la raíz del repositorio:

```bash
cd agents/Agente_evidencia_auditoria-Grupo4
python3 -m venv .venv
```

Activar el entorno según el sistema operativo e instalar:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app_dashboard:app --host 0.0.0.0 --port 8004
```

El puerto 8004 es una propuesta para ejecutar este agente de forma independiente y evitar conflictos con los demás grupos. No es un puerto obligatorio del sistema.

- Dashboard: `http://localhost:8004/`
- Swagger: `http://localhost:8004/docs`
- Contrato OpenAPI: `http://localhost:8004/openapi.json`
- Estado y detección de la skill: `GET /api/status`

También se conserva `python app_dashboard.py`, que usa el puerto 8000 por defecto y admite la variable `PORT`. Ese arranque activa recarga de desarrollo; para el contenedor usar el comando de Uvicorn anterior sin recarga.

## Alternativas orientativas para la integración

### A. Conservar el agente como servicio HTTP

El coordinador envía la evidencia a `POST /api/auditar`. El dashboard no necesita abrirse para usar la API. Este enfoque conserva la implementación de cada grupo y permite que el coordinador utilice una interfaz definida.

### B. Integrarlo como módulo dentro de un único proceso

También se pueden reutilizar `cargar_skill_prompt()`, `AuditoriaRequest` y `auditar_evidencia(req)` de `app_dashboard.py`. Esta última función devuelve el resultado o lanza una `HTTPException`; la integración deberá adaptar ese manejo si no usa FastAPI. Importar el módulo también requiere las dependencias del dashboard.

Las carpetas actuales contienen guiones, por lo que no son nombres normales para imports de paquetes Python. Si se elige esta opción, el integrador puede crear un adaptador o cargar el archivo por su ruta manteniendo su ubicación. El código actual resuelve sus conocimientos mediante `Path(__file__).resolve().parent`: si se mantiene sin adaptar, espera la carpeta `auditoria-evidencias-pims/` junto al módulo. Si se reorganiza, se pueden actualizar esas rutas o centralizar la carga de conocimientos.

### C. Reutilizar skill y conocimientos con el ejecutor común

Si el sistema final ejecuta todas las skills con un cliente de IA central, cargar la skill, las referencias necesarias y las plantillas desde esta carpeta. Eso requiere implementar y validar el ejecutor; los `.md` no ejecutan funciones ni consultan SQLite por sí solos. El historial de Git permite consultar la implementación anterior y comparar resultados cuando se adapte su ejecución.

## Contrato HTTP actual

### Solicitud de auditoría

`POST /api/auditar` recibe JSON:

```json
{
  "nombre_archivo": "evidencia_grupo2.txt",
  "contenido": "Texto completo de la evidencia a evaluar",
  "proveedor": "ollama",
  "modelo": "MODELO_ACORDADO",
  "url_base": "http://localhost:11434/v1"
}
```

Reemplazar `MODELO_ACORDADO` por el nombre exacto del modelo descargado. Enviar explícitamente `proveedor`, `modelo` y `url_base` desde el coordinador. El valor predeterminado de `proveedor` es `gemini`, no Ollama. El modelo predeterminado para la rama Ollama del código conservado es `llama3.1`, pero eso no significa que el grupo integrador lo haya elegido o instalado.

`nombre_archivo` es una etiqueta: no hace que el servidor abra una ruta del disco. `contenido` es el texto que realmente se evalúa. La rama Ollama utiliza el cliente Python `openai` con el valor de clave convencional `ollama`; no requiere una clave de OpenAI para consultar el servidor local de Ollama.

Con Docker Compose, si el servicio compartido se llama `ollama`, enviar `http://ollama:11434/v1`. Dentro de un contenedor, `localhost` identifica ese mismo contenedor. La URL debe ser accesible desde el proceso del Grupo 4, y el modelo debe estar descargado antes de probarlo. Ver [compatibilidad de Ollama](https://docs.ollama.com/api/openai-compatibility) y [red de Compose](https://docs.docker.com/compose/how-tos/networking/).

Los proveedores admitidos explícitamente por la API son `gemini`, `groq`, `openai`, `ollama` y `simulador`. Para los tres servicios externos se admiten `api_key` en la solicitud o las variables `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY` según corresponda. No guardar claves reales en archivos versionados.

### Respuesta de éxito

Campos actuales, con valores ilustrativos:

```json
{
  "exito": true,
  "proveedor_usado": "Ollama Local GPU (MODELO_ACORDADO)",
  "modelo_usado": "MODELO_ACORDADO",
  "tiempo_segundos": 2.15,
  "sha256": "HASH_SHA256_DEL_TEXTO_UTF8",
  "severidad": "NO CONFORMIDAD MAYOR",
  "dictamen_markdown": "Texto del dictamen propuesto para revisión humana"
}
```

`Ollama Local GPU` es una etiqueta fija del código: no verifica el uso real de GPU. Los campos de proveedor y modelo permiten reconocer el simulador o una contingencia; `exito: true` por sí solo no acredita que respondió un LLM.

La severidad se obtiene buscando frases en la respuesta del modelo. No existe todavía un esquema JSON validado del dictamen, puntuaciones calculadas ni almacenamiento de resultados. La propuesta técnica requiere validación del auditor humano.

### Otros endpoints

- `GET /api/casos`: casos de ejemplo precargados.
- `GET /api/controles`: listado parcial de líneas extraídas de la referencia; no usarlo como catálogo normalizado ni como conteo normativo validado.
- `POST /api/hash`: formulario con `contenido` y `nombre_archivo`; calcula SHA-256 del texto codificado en UTF-8.
- `POST /api/auditar-archivo`: formulario multipart con `file`, `proveedor` y `api_key` opcional. No admite `modelo` ni `url_base` en su contrato actual. Para configurar Ollama de forma explícita, usar `/api/auditar` con JSON.

Errores principales: 400 para contenido vacío o credencial requerida ausente; 422 para solicitudes que no cumplen el esquema; 502 cuando falla el proveedor y no se activa contingencia. Configurar en el coordinador un tiempo de espera adecuado para inferencia local: el código puede intentar la llamada al modelo hasta tres veces.

## Decisiones para la integración común

1. Elegir cuándo se delega una tarea al Grupo 4 y el mecanismo común de ejecución. No existe obligación de usar nuestra API HTTP.
2. Acordar el acceso a modelos y la configuración que convenga al conjunto. Las instrucciones y conocimientos especializados pueden reutilizarse con un cliente común; los proveedores actuales del Grupo 4 no condicionan la elección.
3. Definir el esquema SQLite y la responsabilidad de lectura/escritura. Actualmente AuditPIMS recibe texto y devuelve un resultado en memoria: no consulta ni crea tablas.
4. Asociar un identificador de evidencia y de auditoría en el coordinador, guardar el resultado y la revisión humana. El SHA-256 identifica el contenido textual, no sustituye esos identificadores ni demuestra por sí mismo una cadena de custodia.
5. Definir con el Grupo 7 la propiedad de la SoA compartida. La consolidación M3 existente sirve como avance del Grupo 4 y demostración; no es sincronización con la SoA del Grupo 7.
6. Crear el Docker/Compose general, montar los conocimientos y la base persistente, configurar nombres de servicios y comprobar un flujo real con el modelo acordado. No hay Dockerfile ni base SQLite implementados por esta entrega.

## Comportamiento actual y puntos por revisar

- `simulador` devuelve una plantilla de contrato con severidad fija. Sirve para comprobar transporte, interfaz y hash; no mide calidad de auditoría y no necesita IA.
- El motor de contingencia se activa ante determinados errores de cuota/disponibilidad y aplica reglas limitadas. Sus textos son plantillas, no resultados de un LLM ni sustituto de una evaluación validada.
- La subida de archivos decodifica bytes como texto. No extrae texto de un PDF real ni aplica OCR. Convertir documentos a texto antes de usar el endpoint JSON; conservar el original por separado si se necesita integridad del archivo binario.
- El dashboard utiliza recursos web externos; una inferencia local no garantiza que toda la interfaz funcione desconectada de internet.
- La API actual no implementa autenticación y admite CORS amplio. La capa de acceso y el despliegue del sistema final deben definirse en la integración.
- Las referencias y reglas normativas son material del proyecto y requieren revisión del equipo; copiarlas al repositorio no acredita una validación normativa independiente.

## Verificación realizada al preparar esta entrega

Se verificó la sintaxis de los programas, la carga de la skill, el dashboard, Swagger y los endpoints de estado/casos/hash. Se comprobó una auditoría simulada por JSON y por carga de TXT, y el rechazo de contenido vacío. Se ejecutaron los comandos offline `--listar`, `--evaluar E6`, `--evaluar E8` y `--consolidar`.

No se ha verificado inferencia real con el futuro modelo común, integración SQLite, ejecución del coordinador ni despliegue Docker. Los generadores históricos de PDFs se incluyen como material fuente y no se ejecutaron durante esta carga.
