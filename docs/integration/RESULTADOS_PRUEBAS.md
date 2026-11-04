# Resultados de pruebas

Fecha: 2026-11-03/04. Equipo: laptop de desarrollo, Docker Desktop. **Modo LLM: `cloud` (Gemini real).** No se ejecutó el modo `ollama` ni el modo `mock` en la plataforma completa (`mock` solo en pruebas unitarias del gateway).

## Línea base de los agentes (antes de integrar)

| Agente | Prueba | Resultado |
|---|---|---|
| G3 | `pytest tests/core` | 115 pasan |
| G4 | `probar_auditor.py --listar` / `--evaluar E6` (offline) | Salida normal |
| G1, G2, G7, G8 | — | Sin suite automática (G1 tiene `tests/` vacío; G8 solo un registro manual de pruebas). Línea base mínima. |

## Después de integrar (mismo entorno de ejecución, contenedor)

| Prueba | Resultado |
|---|---|
| G3 `pytest tests/core` dentro de su contenedor | 115 pasan (igual que la línea base) |
| G4 `probar_auditor.py --evaluar E6` en contenedor | Salida con nota de gobernanza |
| `tests/unit` (gateway, modo `mock`) | 3 pasan |
| `tests/integration` contra la plataforma (modo `cloud`) | 13 pasan |
| Persistencia | 14 ejecuciones antes y después de reiniciar `postgres` y `backend` |
| Carga del script del profesor | Esquemas `public` y `demo` creados; segunda corrida lo omite |

Ejecuciones reales por el orquestador: G1 chat, G3 plazos (valores deterministas idénticos a la línea base), G4 auditoría y hash, G5 auditoría completa (puntaje 2, "No recomendable sin enmiendas"), G7 SoA, G8 análisis de brecha. El gateway registró llamadas sin errores.

## Cómo se compara

La salida de un LLM no es idéntica byte a byte. Se compararon estructura, campos requeridos y partes deterministas (plazos, hash, puntaje calculado por código).

## Ronda ampliada de pruebas funcionales (modo `cloud`, llamadas reales al modelo)

`tests/integration/test_agents_behavior.py`: **15 pasan** (5 min 12 s) más 2 de G2 que se omiten si el control de alcance del grupo está cerrado.

| Agente | Qué se verificó |
|---|---|
| G1 | El chat devuelve texto. |
| G3 | Un caso sin identidad verificada queda `IDENTITY_PENDING`, exige revisión humana y no genera handoffs; pedir el borrador de un caso no aprobado es rechazado por el agente; plazo de información = 8 días hábiles; la consulta de norma devuelve fragmentos con fuente; las herramientas de decisión humana no son invocables. |
| G4 | Estructura del dictamen, hash SHA-256 correcto, etiqueta del proveedor sustituida; contenido vacío rechazado. |
| G5 | Puntaje calculado por el código; el expediente queda "Pendiente DPO" (nunca se aprueba solo); un contrato con instrucciones inyectadas no alcanza puntaje 100 y sigue pendiente. |
| G7 | Reglas de aplicabilidad por rol (A.1 solo responsable, A.2 solo encargado, A.3 todos); entrada inválida rechazada sin inventar; RAG con embeddings por el gateway. |
| G8 | Análisis de brecha completo (menciona las 48 h); reporte corto rechazado; no se afirma ningún envío. |
| Aislamiento | Con G4 detenido la plataforma sigue viva, G4 aparece `caído` con motivo, los demás siguen operativos y el fallo queda registrado. |
| G2 (control de alcance abierto temporalmente, con tu autorización) | Pregunta sobre la norma: respondió citando la cláusula 6.1.2 (páginas 13–14) recuperada de Qdrant; evaluación de riesgos de un sistema de matrícula: respuesta estructurada; pregunta fuera de tema ("receta de pizza"): rechazada por el agente con `OUT_OF_SCOPE`. Después se restauró el control a cerrado. |

### Defectos encontrados y corregidos al probar

1. **Gemini 3.x exige la `thought_signature` en las llamadas a herramientas** y los clientes tipo OpenAI de n8n la descartan: el segundo turno del agente de G2 recibía HTTP 400. El gateway ahora guarda la firma de cada respuesta y la reinyecta (con la firma de omisión documentada como respaldo). Cubierto por un test unitario.
2. **Búsqueda web automática de G2:** el chat intentaba usar Tavily (falta la clave y además enviaría datos fuera). El adaptador ahora envía `webMode: off`.

## Gestitel en uso por G5 (modo `cloud`)

- Al auditar un contrato, G5 guarda en PostgreSQL: 1 evaluación (`core_dpaassessment`), 26 resultados de control, 1 contrato y 1 tercero; sin fila de aprobación (queda pendiente del DPO).
- Un test comprueba que el rol `agente7` no puede borrar en `core_asset` (permission denied).
- **Por qué no lo usan G1, G2, G3, G4, G7 ni G8:** las tablas de negocio de Gestitel guardan códigos de listas (tipo, estado, clasificación) definidos en los modelos Django, no en la base; mapearlos sería inventar valores. G3 además no debe guardar datos del solicitante (`core_arcorequest` exige nombre y documento). G2 y G7 no tienen almacén propio que migrar. Para hacerlo falta el código de los modelos Django del profesor.

- **Adaptación posible sin inventar datos:** cada ejecución de cualquier agente deja una fila de solo metadatos en `demo.core_securitylog` (texto libre y JSON; las tablas de negocio no se tocan). Test: la fila existe y no contiene datos de entrada.
- Se comprobó que el script del profesor no trae comentarios, restricciones CHECK ni catálogos para los códigos de las tablas de negocio (solo las tablas de G5 los tienen), por lo que no se mapearon incidentes, auditorías ni solicitudes.

## Interconexión entre agentes (modo `cloud`, `tests/integration/test_flows.py`: 4 pasan)

Cada paso es una ejecución real de un agente; los flujos corren en el orquestador (`/api/flows`) y se pueden lanzar desde el Panel general.

| Flujo | Qué se comprobó |
|---|---|
| G5 → G7 | El expediente de G5 (26 controles) se transforma en evidencias de G7. Con un contrato bueno (puntaje 54, riesgo medio) la SoA pasó de 0 a **3 controles implementados** (A.2.5.7, A.3.11, A.3.12). Con un contrato malo no cambia nada. El solapamiento entre ambos catálogos es de solo 3 controles. |
| G8 → G1 | El incidente se analiza en G8; sus lecciones aprendidas llegan a G1, que propone capacitaciones. |
| G3 → G4 / G5 / G6 | Tras una decisión humana, G3 genera 3 sobres: `evidencia` se entregó a G4 (severidad propuesta), `terceros` quedó `pendiente_humano` (exige revisión humana) e `inventario` quedó `sin_receptor` (G6 no integrado). Antes de la decisión humana el flujo rechaza (no hay handoffs). Todo se registra en `orchestrator.handoff`. |

| G6 → G2 | Flujo nuevo `inventario_a_riesgos`. Ejecutado a mano en la plataforma **desplegada** (no con pytest en local, porque ahí G2 sigue bloqueado): 51 s, pasos `inventario.consultar_inventario` → `riesgos.chat`; G2 evaluó el «Portal de admisión» (6 campos personales enviados, sin valores) citando la cláusula 6.1.2 e indicando lo no declarado. La prueba automática `test_g6_inventory_feeds_g2_risk_assessment_without_sending_values` está escrita pero **no se ha ejecutado**. G2 usó temporalmente la clave de G8. |

Defecto encontrado y corregido: la herramienta `dsar_handoffs` devuelve un bloque de contenido por sobre y el adaptador los concatenaba; ahora los conserva separados.

Límites: G5 y G6 no tienen receptor de handoffs.

## Acciones humanas con login (`tests/integration/test_human.py`: 5 pasan)

- Las decisiones que los agentes dejan a una persona están en `/revision`, con sesión firmada y roles (DPO, Legal). No son acciones de los agentes: son endpoints propios que llaman al mecanismo nativo de cada uno y registran quién decidió (evento y `demo.core_securitylog`).
- Verificado: sin sesión 401; rol equivocado 403; contraseña incorrecta 401; los modelos siguen sin poder decidir (422).
- **G3:** ciclo completo con decisión humana real: decidir antes de verificar identidad es rechazado por el agente; tras verificar y aprobar se generan los handoffs y viajan a G4/G5 (flujo `dsar_handoffs`).
- **G5:** un contrato «Pendiente DPO» no se puede aprobar con `legal` primero (409, lo exige el agente); DPO y luego Legal sí, y las dos decisiones y el intento fuera de turno quedan registrados.
- **G8:** aprobar o rechazar una acción propuesta está en la web; su prueba automática queda pendiente.
- Para G3 se añadió un puente interno dentro de su contenedor (`g3_human.py`), porque sus funciones de decisión existen solo en Python y no son herramientas de modelo. Solo lo llama el backend con un token compartido.

## Agente 8 completo: solo y usado por los otros agentes (modo `cloud`, `tests/integration/test_g8_full.py`)

**Comparación con el repo propio del agente (`tif`):** el código de la carpeta del agente 8 es idéntico a esa copia de trabajo; la integración no modificó ningún archivo suyo.

**Solo (su aplicación original, con datos de ejemplo; accesible con `docker compose --profile standalone up -d standalone-g8` en `127.0.0.1:3100`):**
- Superficie intacta: 4 skills, 10 reportes y 3 archivos de contexto de ejemplo, modo autónomo leyendo su configuración de conectores.
- **Distingue los casos:** correo masivo con DNI y notas → brecha de datos personales, severidad Alta (SE = 3,75), hora límite de 48 h y los **3 borradores** (ANPD, titulares, CNSD) más plan y cierre; ataque DoS sin datos → incidente **sin brecha de datos personales**, severidad N/A y **sin notificaciones**.
- Contexto subido por el usuario: el agente lo abre, consulta los sistemas declarados y cita el contenido.
- Buzón por webhook: sin token o con token malo → 401; con token → 202. La queja se clasifica sola («seguridad», con señales como DNI y SISACAD) y su análisis produce el expediente completo.
- **Acciones propuestas:** el agente propuso acciones pendientes; una persona (DPO) aprobó una en la página de revisión, el agente solo registró la decisión (nada se ejecuta), otra quedó pendiente y la bitácora de Gestitel guardó quién decidió.

**Usado por los otros agentes:**
- **G8 lee a G6, G7 y G5** por conectores HTTP de solo lectura (`docker/agents/g8_conectores.json`): inventario de activos (G6), catálogo de 10 controles (G7) y expedientes de contratos (G5). Rutas que cambian estado (`/webhook/pims/aprobar`, `/api/ejecutar`) están bloqueadas: G8 no puede aprobar nada de otros agentes. Probado dentro de su contenedor con datos de ejemplo cargados por `scripts/seed_demo_data.py`.
- En el análisis del buzón G8 **consultó por sí mismo a G6** (inventario de la UNSA). En análisis manuales con texto simple no llama a otros agentes por iniciativa propia: es decisión de su prompt, que no se modificó.
- **La plataforma usa G8** con 9 acciones: analizar (con contexto opcional), ver expediente, expedientes existentes, depositar queja, leer el buzón, analizar queja, ejemplos y estado del modo autónomo; y el flujo G8 → G1.
- **Otros sistemas o agentes pueden depositar quejas** en su buzón por webhook con token (`G8_BUZON_TOKEN`).

**Defecto encontrado y corregido:** con 4 análisis en paralelo, 39 de 57 llamadas a Gemini devolvieron 429 y el gateway respondía 502. Ahora espera el límite de la clave del equipo (respeta `Retry-After`, hasta 6 reintentos con tope de 60 s) y limita a 2 llamadas simultáneas por equipo. Con eso dos análisis en paralelo terminaron en 85–95 s sin errores.

**Sigue solo en la interfaz original de G8:** activar el modo autónomo, subir contextos desde pantalla y cancelar un análisis.

## Pendiente o no verificado

- **Modo `ollama`**: solo `docker compose --profile ollama config`. Ver `docs/installation/OLLAMA_OTRA_PC.md`.
- **G2** queda bloqueado por defecto (control de alcance del grupo). El chat se probó con el control abierto de forma temporal; para dejarlo operativo: `G2_SCOPE_N8N_REVIEWED=true` en `.env`.
- Las reglas de aprobación humana de G3, G5 y G8 se verifican a nivel de **capacidades expuestas** (ninguna acción de aprobar/decidir/enviar); no se probó contra los endpoints nativos de decisión.
- No hay test de la regla de G3 "la nube solo recibe hechos minimizados": su servidor MCP no usa LLM.
- Handoffs de G3 a otros agentes: no se transportan todavía; la tabla `orchestrator.handoff` existe pero está sin uso.
- Las cuentas de la página de revisión son de demostración (`HUMAN_USERS`); no es un sistema de identidad completo.
