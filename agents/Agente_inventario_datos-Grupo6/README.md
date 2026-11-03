# Grupo 06 · Agente de Inventario de Datos Personales

Implementación ejecutable de **Agente_inventario_datos-Grupo6** para `Piero-design/sistema-multiagente`. Registra activos, clasifica campos y prepara el mapa de tratamientos. Incluye skill de dominio, CLI, API FastAPI, herramientas MCP, SQLite propia y panel de demostración.

**Motor actual: reglas locales, sin LLM.** Calcula resultados a partir de la entrada; no usa respuestas prefabricadas. Las fuentes del ejemplo y el expediente DSAR de prueba son ficticios. La integración con el orquestador central sigue pendiente porque ese ejecutor no existe en el repositorio inspeccionado.

## Instalación

Desde la raíz del repositorio, con Python 3.11 o superior:

```bash
cd agents/Agente_inventario_datos-Grupo6
python -m venv .venv
```

Activa el entorno: Windows `.venv\Scripts\activate`; macOS/Linux `source .venv/bin/activate`. Después:

```bash
python -m pip install -r requirements.txt
```

No requiere claves, Ollama ni una base compartida. Se comprobó con Python 3.13.5, FastAPI 0.136.3, Pydantic 2.13.4 y MCP 1.27.2. Usa un entorno propio: el Grupo 3 declara otra versión mayor del SDK MCP y ambos servicios pueden comunicarse sin mezclar sus dependencias.

## Ejecutar y exponer en clase

```bash
python -m uvicorn inventario.api:app --host 127.0.0.1 --port 8006
```

Abre [el panel local](http://127.0.0.1:8006), pulsa **Cargar ejemplo**, **Analizar sin guardar** y después **Registrar activos**. Consulta **Inventario guardado**, **Mapa de tratamientos** y **Cobertura de ejemplo**. El contrato navegable está en [Swagger](http://127.0.0.1:8006/docs).

El ejemplo reconoce un activo de Matrícula con cuatro campos: nombre, DNI, correo y fecha de nacimiento. El contexto ficticio declara una finalidad, responsable y transferencia. La retención y base jurídica permanecen `Por determinar`. La cobertura distingue Matrícula inventariada de Biblioteca sin activos y siempre solicita validación; no busca personas.

Por consola, desde esta misma carpeta:

```bash
python agent.py --estado
python agent.py --entrada examples/registro_matricula.json
python agent.py --entrada examples/consulta.json
python agent.py --entrada examples/cobertura.json
python agent.py --entrada examples/handoff_dsar.json --handoff --organizacion UNSA-DEMO
```

Los comandos usan la misma SQLite que la API: `data/inventario.sqlite3`, relativa a esta carpeta, no al directorio desde el que arrancó el proceso. Para aislar una demostración, usa `--db data/demo.sqlite3`; en API/MCP puedes configurar `INVENTARIO_DB_PATH`. CLI y MCP también aceptan `--db`.

## Herramientas MCP para el integrador

```bash
python mcp_server.py
# Alternativa HTTP local independiente de FastAPI:
python mcp_server.py --http --port 8007
```

El servidor real se llama `inventario-agent`; el alias de destinatario que usa DSAR es `inventario`. Expone seis herramientas: `inventario_ejecutar`, `inventario_registrar_activos`, `inventario_consultar`, `inventario_clasificar_datos`, `inventario_mapear_tratamientos` e `inventario_confirmar_cobertura`. Carga [SKILL.md](SKILL.md) y las tres skills de dominio como instrucciones para el modelo cliente. No hay un LLM incorporado al servidor.

El cliente puede leer los recursos MCP `inventario://contrato` e `inventario://ejemplo` para consultar el contrato y una entrada ficticia sin acceder al disco del servidor.

Ejemplo de configuración **para un cliente MCP**, sustituyendo ambas rutas por rutas absolutas de la máquina donde se ejecute:

```json
{
  "mcpServers": {
    "inventario": {
      "command": "/RUTA/AL/GRUPO6/.venv/bin/python",
      "args": ["/RUTA/AL/GRUPO6/mcp_server.py"]
    }
  }
}
```

En Windows, el ejecutable está en `.venv/Scripts/python.exe`. Este bloque no registra mágicamente el agente en un orquestador: hay que incorporarlo en el cliente que use el equipo.

## Qué entrega

- `inventario/`: núcleo de dominio, validación, persistencia, HTTP y MCP. Todos usan `InventoryAgent.ejecutar()`; no hay motores distintos según el transporte.
- `agent.py` y `mcp_server.py`: entradas ejecutables por ruta.
- [SKILL.md](SKILL.md) y `skills/`: función de inventario y procedimientos de registrar, clasificar y mapear.
- [Contrato y errores](references/contrato-integracion.md): entrada, salida, nombres, persistencia y consumidores reales.
- [Guion de exposición](GUIA_EXPOSICION.md): explicación y demostración breve para cualquier integrante.
- [Entrada representativa](examples/registro_matricula.json), [salida del registro](examples/salida_registro.json), [salida de cobertura](examples/salida_cobertura.json) y [sobre DSAR](examples/handoff_dsar.json). Las salidas se generaron ejecutando el programa sobre una base temporal nueva; no son plantillas del motor.
- `tests/`: pruebas de dominio, persistencia, HTTP, MCP real y contrato con el productor DSAR.
- `agente.html`: panel conectado a la API/SQLite. [index.html](index.html) conserva la demostración autónoma anterior, con reglas y localStorage separados. No se sincroniza automáticamente con el backend.
- `originales/`: PDF y HTML recibidos, sin alteraciones. El descriptor [Agente_inventario_datos-Grupo6.md](Agente_inventario_datos-Grupo6.md) conserva la asignación original.

## Persistencia y revisión

Un activo se identifica por organización, sistema normalizado e ID de fuente. Repetir una revisión devuelve `sin_cambios`; actualizarla cambia la vista actual y conserva su historial. El lote de fuentes se analiza completo antes de una transacción de registro. SQLite usa tablas `inv6_assets` e `inv6_revisions` y no modifica otros agentes.

El agente conserva nombres de campos, sus ubicaciones, hashes y contexto declarado; descarta los valores originales de CSV/JSON y el contenido completo de las fuentes. Los nombres de fuente, claves JSON y contexto también pueden ser confidenciales: usa esquemas con nombres de campo y ejemplos ficticios. No suministres documentos JSON indexados por nombres o identificadores de personas como si fueran esquemas.

Todos los activos y tratamientos quedan pendientes de validación. El servicio no autentica revisores ni emite aprobación legal. La separación por `organizacion` es un filtro lógico, no un control de acceso; estos servidores se arrancan en loopback para uso local.

## Verificación y pendientes

Para ejecutar las pruebas:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Se comprobaron 16 pruebas: clasificación, desconocidos, potencial sensibilidad, no conservación de valores, CSV/JSON, negaciones, entrada hostil como datos, registro idempotente, historial, aislamiento lógico por organización, atomicidad ante fuente inválida, fallos de almacenamiento, cobertura, exportación para auditoría, HTTP y cliente MCP real por stdio. También se llamó a la CLI con registro y recepción de handoff. El test del productor DSAR necesita un checkout que incluya `agents/Agente_derechos_dsar-Grupo3/src/dsar/storage/handoffs.py`; si solo se descarga esta carpeta, esa prueba se omite explícitamente.

La prueba de interoperabilidad DSAR usa el generador real del Grupo 3 sobre un expediente ficticio. No ejecuta una aprobación real ni el ciclo completo de DSAR. No se ejecutó un coordinador central, un modelo ni una conexión Gestitel/SQLite compartida. Los transportes y las operaciones de inventario comprobados son reales.

El panel se probó contra un servidor Uvicorn real en Chromium: análisis sin guardar, registro, consulta de SQLite, mapa, cobertura y descarga JSON. Se revisó en escritorio y móvil, sin desborde horizontal ni errores JavaScript.

Queda pendiente: elegir y configurar el ejecutor central; acordar permisos y modelo de datos compartido; revisión humana autenticada; conectar consumidores de riesgos/incidentes/terceros a las consultas; probar el flujo completo en el entorno del equipo. Un LLM, PDF/Word/OCR y una extracción semántica de contexto no están implementados. Las reglas de texto pueden omitir cláusulas mixtas por su tratamiento conservador de negaciones. CSV/JSON tienen parsers estructurales; SQL solo puede inspeccionarse como texto de forma limitada.

Las referencias normativas del informe se conservan como contexto académico; esta entrega no realizó un dictamen jurídico. El grupo debe revisar esas fuentes antes de presentar conclusiones legales.
