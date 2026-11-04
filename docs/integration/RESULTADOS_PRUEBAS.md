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

## Pendiente o no verificado

- **Modo `ollama`**: solo `docker compose --profile ollama config`. Ver `docs/installation/OLLAMA_OTRA_PC.md`.
- **G2** queda bloqueado por defecto (control de alcance del grupo). El chat se probó con el control abierto de forma temporal; para dejarlo operativo: `G2_SCOPE_N8N_REVIEWED=true` en `.env`.
- Las reglas de aprobación humana de G3, G5 y G8 se verifican a nivel de **capacidades expuestas** (ninguna acción de aprobar/decidir/enviar); no se probó contra los endpoints nativos de decisión.
- No hay test de la regla de G3 "la nube solo recibe hechos minimizados": su servidor MCP no usa LLM.
- Handoffs de G3 a otros agentes: no se transportan todavía; la tabla `orchestrator.handoff` existe pero está sin uso.
- Las acciones humanas (verificar identidad y decidir en G3; DPO/Legal en G5; aprobar acciones en G8) no están en la interfaz unificada.
