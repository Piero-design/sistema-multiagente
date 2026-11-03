# Contrato de integración · Grupo 06

## Procedencia y estado del sistema

Inspección realizada sobre `Piero-design/sistema-multiagente`, base `e959dd7`, el 3 de noviembre de 2026. `structure.md` propone `main.py`, `orchestrator.py`, una skill maestra y módulos compartidos, pero esos ejecutables no están en el árbol inspeccionado. `shared/`, `database/` y `tests/` contienen descriptores; no hay un contrato global ejecutable ni un esquema SQLite común implementado allí. No se creó ni simuló un orquestador para aparentar integración.

`Agente_inventario_datos-Grupo6.md` asigna inventario, clasificación y mapa de tratamientos. El informe original, páginas 8 y 12, define campos y regla de no invención. Antes de esta implementación el grupo tenía un descriptor, el informe, el prototipo original y el HTML local añadido; no tenía agente Python, skill de dominio cargable ni receptor interagente.

Contratos existentes consultados:

- Grupo 3: `src/dsar/storage/handoffs.py::build_handoffs()` / `envelope()` y `GUIA_INTEGRACION.md`. Ya produce `to_agent: inventario`, `action: confirmar_cobertura`, con `missing_systems` y `found_systems`. Ese formato se acepta sin renombrar campos.
- Grupo 4: `GUIA_INTEGRACION.md` documenta `POST /api/auditar` con `nombre_archivo`, `contenido`, proveedor/modelo. `exportar_evidencia` prepara los dos campos de contenido; el integrador elige proveedor y modelo. No se realizó una llamada al servicio del Grupo 4.
- Grupos 5 y 8: sus guías describen inventario de activos/metadatos como información útil, pero todavía no hay un cliente que consuma una respuesta específica del Grupo 6. Las consultas entregadas son una interfaz propuesta y ejecutable de este agente, no un protocolo común ya acordado.

## Identificadores y entradas

- Directorio: `Agente_inventario_datos-Grupo6`.
- Alias de agente: `inventario`, tomado del productor DSAR existente.
- Servidor MCP de esta implementación: `inventario-agent`.
- Núcleo: `inventario.service.InventoryAgent.ejecutar(solicitud)` devuelve `(sobre, codigo_http)`.
- CLI: `python agent.py --entrada archivo.json`; también admite stdin. Exit code 0 para éxito y 1 para entrada inválida o fallo de operación. `--estado` inspecciona capacidades.
- HTTP: `POST /api/ejecutar`, `POST /api/handoffs?organizacion=...`, `GET /api/inventario?organizacion=...`, `GET /api/tratamientos?organizacion=...`, `GET /api/status`.

Todas las acciones llevan `accion` y `organizacion`. `request_id` es opcional y se devuelve para correlación; no se usa como autenticación ni como clave de idempotencia.

Acciones admitidas:

- `analizar`: `fuentes` obligatorias; no escribe. Devuelve activos, campos, mapa, evidencia y advertencias.
- `registrar_activos`: las mismas entradas; guarda el lote y devuelve conteos `creados`, `actualizados`, `sin_cambios`.
- `clasificar_datos`: `campos` obligatorios (lista de nombres); no escribe.
- `consultar_inventario`: devuelve activos persistidos; filtro opcional `sistema` por nombre exacto normalizado, sin distinguir acentos o mayúsculas.
- `mapear_tratamientos`: lee activos persistidos y prepara borradores; admite filtro `sistema`.
- `confirmar_cobertura`: `missing_systems` obligatoria, `found_systems` opcional. Solo consulta; no confirma registros de una persona ni modifica DSAR.
- `exportar_evidencia`: lee el inventario y prepara un documento para el Grupo 4; admite `sistema`; `enviado` permanece `false`.

Una fuente requiere `id`, `nombre` y `sistema`. `formato` es opcional y por defecto es `texto`. Formatos:

- `campos`: lista `campos` de nombres; no admite `contenido`.
- `texto`: texto en `contenido`; reconoce alias por cláusula/línea, con negaciones conservadoras.
- `csv`: texto en `contenido`; inspecciona cabeceras y valida cantidad de columnas, sin conservar filas.
- `json`: texto JSON en `contenido`; inspecciona propiedades y rutas con `[*]` para listas de objetos, sin conservar valores. Se rechazan listas de valores escalares; para esquemas simples usa `campos`.

`contexto` es opcional por fuente. Campos escalares: `finalidad`, `base_juridica`, `responsable`, `almacenamiento`, `retencion`. Listas: `titulares`, `accesos`, `transferencias`. Los valores se rotulan `declarado_en_solicitud`; los ausentes/vacíos se devuelven `Por determinar` y `pendiente`, no como ausencia confirmada. `titulares` significa categorías como Estudiantes, nunca identidades personales.

Límites: 20 fuentes, 200 000 caracteres por contenido, 1 000 000 en el conjunto, 200 campos explícitos/cabeceras, 500 campos distintos por fuente y 12 niveles JSON. El CLI limita además el archivo JSON completo a 1 000 000 caracteres. Los datos desconocidos o propiedades de contrato no admitidas se rechazan; no se ignoran silenciosamente.

## Salida

Sobre propio del Grupo 6, versión `1.0`:

```json
{
  "agent_id": "inventario",
  "agent_directory": "Agente_inventario_datos-Grupo6",
  "contract_version": "1.0",
  "status": "ok",
  "accion": "registrar_activos",
  "request_id": "demo-grupo06-001",
  "motor": "reglas_locales",
  "simulado": false,
  "data": {"activos": [], "total_activos": 0},
  "error": null
}
```

Este fragmento ilustra la envoltura. Las salidas completas de ejecuciones están en `../examples/salida_registro.json`, `salida_cobertura.json` y `salida_handoff.json`.

Cada activo tiene ID estable, sistema, fuente y SHA-256, lista de campos con evidencia, contexto con procedencia y `revision_sha256`. La clasificación por nombre es inferida; los campos desconocidos conservan `es_pii: null`. El estado siempre es `pendiente_validacion`. Cada tratamiento referencia su activo y crea flujos únicamente a los destinatarios declarados. No se publican valores originales de personas.

## Errores y reintentos

- 422 / `ENTRADA_INVALIDA`: falta un campo, tipo incorrecto, acción no admitida o argumentos incompatibles. No reintentar sin corregir. Los detalles contienen rutas/tipos, no valores de entrada.
- 422 / `FUENTE_INVALIDA`: CSV/JSON inconsistente, límites o estructura no admitida. Todo el lote se rechaza antes de escribir.
- 422 / `HASH_HANDOFF_INVALIDO`: el sobre no coincide con el SHA-256 emitido. No procesar ni alterar para forzar aceptación.
- 503 / `ALMACENAMIENTO_NO_DISPONIBLE`: no se pudo abrir/leer/escribir SQLite. `retryable: true`; el consumidor decide la espera y el número de intentos.

En un error `status: error`, `data` es `null` y `error` incluye `code`, `message` y `retryable`. La validación puede devolver `accion: null` porque no se aceptó la solicitud. HTTP usa el mismo código; CLI usa exit code 1. En MCP los errores de negocio están dentro de este sobre, por lo que el cliente debe revisar `status`, aunque el transporte MCP haya sido exitoso. El SDK MCP maneja por separado llamadas con argumentos que no cumplen la firma de una herramienta.

La API/MCP no reintenta ni envía solicitudes a terceros. Registro idéntico es idempotente por ID de activo y hash de revisión, no por `request_id`. Actualizaciones conservan versiones anteriores. Una consulta de inventario vacío es éxito con `activos: []`, no prueba ausencia de datos personales.

## Recibir el handoff real de DSAR

El emisor incluye `from_agent`, `to_agent`, `case_ref`, `control_ref`, `action`, `payload`, `requires_hitl`, `created_at` y `sha256`. El receptor exige `from_agent: dsar`, `to_agent: inventario` y acción `confirmar_cobertura`. El hash se verifica usando exactamente el JSON canónico del productor (claves ordenadas, Unicode y separadores por defecto de `json.dumps`). Verifica integridad, no autenticidad del remitente.

El sobre no incluye organización: el cliente integrador debe proporcionarla explícitamente; no se deduce del expediente.

```bash
curl -X POST 'http://127.0.0.1:8006/api/handoffs?organizacion=UNSA-DEMO' \
  -H 'Content-Type: application/json' \
  --data-binary @examples/handoff_dsar.json
```

En MCP: `inventario_confirmar_cobertura(organizacion, handoff)`. Se devuelve referencia del caso, hash verificado, sistemas inventariados o pendientes y `requiere_validacion: true`. Incluso si el emisor puso `requires_hitl: false`, la revisión del alcance DSAR sigue pendiente: el inventario no inspecciona registros de titulares.

El integrador debe leer ese resultado; no existe un cliente central que actualice el expediente DSAR automáticamente. Reenviar el mismo sobre solo repite una consulta y no crea activos ni acciones sobre personas.

## Conexiones pendientes

SQLite es propia y opcional para análisis/clasificación, necesaria para conservar/consultar activos. No hay conexión a `database/sistema.db` ni a Gestitel. No se presupone su esquema ni se crean tablas allí. Las funciones/API son adaptables cuando el equipo defina ese contrato.

El servicio local no autentica usuarios, no aprueba revisiones y no controla acceso multiusuario. Una organización es un alcance lógico, no una credencial. Antes de exponer el servicio en red, el equipo debe acordar la capa de acceso. No se desplegó ni publicó un servidor remoto.
