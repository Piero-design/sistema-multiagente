# Explicación del Grupo 06 · 3 minutos

## Qué decir

«Nuestro agente se encarga del inventario de datos personales. Recibe una fuente identificada y su sistema, reconoce los campos, propone su categoría y genera un mapa de tratamientos. Lo que la fuente o el usuario no documenta queda por determinar. No almacenamos las filas originales de estudiantes o clientes: guardamos metadatos, referencias y hashes.»

«Tenemos tres funciones: registrar activos, clasificar datos y mapear tratamientos. El mismo núcleo Python puede ejecutarse por consola, API HTTP o herramientas MCP. La skill explica al modelo cliente cómo usar esas funciones; el código es el que valida, calcula y guarda los resultados.»

«La implementación actual usa reglas por nombres de campo. No hay un modelo de IA ejecutándose dentro del servidor. Es una limitación explícita: la clasificación requiere revisión y un nombre desconocido no significa que no sea dato personal.»

## Demostración

1. Arranca `python -m uvicorn inventario.api:app --host 127.0.0.1 --port 8006` desde la carpeta del grupo y abre `http://127.0.0.1:8006`.
2. Pulsa **Cargar ejemplo** y **Analizar sin guardar**. Muestra los cuatro campos y la evidencia por columna. Explica que todo el ejemplo es ficticio.
3. Pulsa **Registrar activos**. La primera vez crea un activo. Repítelo: devuelve `sin_cambios: 1`; no duplica la fuente.
4. Abre **Mapa de tratamientos**. Muestra el flujo declarado y los pendientes de retención y base jurídica. Explica que se tomó el contexto declarado, no se inventó desde el nombre Matrícula.
5. Abre **Cobertura de ejemplo**. Matrícula aparece inventariada y Biblioteca sin activos. Tener un sistema en el inventario no garantiza que el agente DSAR haya encontrado todos los registros de una persona.

Si el panel falla por estar abierto como archivo, usa la URL del servidor. Alternativa por consola: `python agent.py --entrada examples/registro_matricula.json`, luego `python agent.py --entrada examples/cobertura.json`.

## Cómo se conecta

«El Grupo 3 ya produce un mensaje para `inventario` con la acción `confirmar_cobertura`. Nuestro receptor acepta ese formato, comprueba su hash y consulta el inventario de la organización indicada. Probamos esa compatibilidad con el generador real del Grupo 3 y un expediente ficticio.»

«Para los demás grupos ofrecemos consultas de activos y tratamientos. Para Auditoría podemos preparar un documento con los campos `nombre_archivo` y `contenido` que recibe su API. Eso todavía no se envía automáticamente.»

«No afirmamos integración completa: el repositorio aún no tiene un coordinador central ejecutable. Sí comprobamos descubrimiento y llamadas usando un cliente MCP real, además de la API y la consola.»

## Respuestas breves a preguntas

- **¿La skill sola hace el trabajo?** No. Son instrucciones de dominio cargadas por el servidor MCP; las operaciones reales están en el núcleo Python.
- **¿Usa IA?** Un modelo cliente puede usar la skill y las herramientas MCP. El motor implementado usa reglas locales y no requiere un LLM. No se verificó razonamiento con un modelo real.
- **¿Qué es simulado?** Los datos de matrícula y el expediente DSAR son ficticios. El registro SQLite, la validación, el hash y las llamadas MCP/HTTP son reales. No hay respuestas prefabricadas del agente.
- **¿Qué falta para integrar todo?** El ejecutor central, las decisiones de base compartida/permisos y las llamadas de los demás consumidores. También faltan revisión humana autenticada y extracción semántica si se desea usar un modelo.
- **¿Puede afirmar cumplimiento?** No. Es un borrador técnico con evidencia y pendientes; no sustituye una validación normativa.
