# Guía general de exposición — Plataforma PIMS multiagente

Duración sugerida de esta parte: **10–12 min** (ajustable). Cada grupo expone después su propio agente (6–8 min) con su guía en `grupos/`. Aquí se explica **una sola vez** lo compartido (gateway, base de datos, Docker) para no repetirlo ocho veces.

## 1. Problema y propósito
Una organización que implanta un PIMS (ISO/IEC 27701:2025, Ley 29733 y su reglamento D.S. 016-2024-JUS) necesita muchas tareas distintas: formar al personal, evaluar riesgos, atender derechos de titulares, auditar evidencias, controlar a terceros, inventariar datos, declarar controles y gestionar brechas. Ocho grupos construyeron un agente para cada una, con tecnologías distintas. El reto de esta entrega fue **hacerlos funcionar juntos sin reescribir ninguno**.

## 2. Por qué una arquitectura multiagente
Cada agente conserva su conocimiento, sus skills y sus reglas (especialización). Se integran por **adaptadores** en el borde: si cambia un agente, solo cambia su adaptador. Un agente que falla no tumba a los demás.

## 3. Los ocho agentes
| G | Agente | Responsabilidad | Tecnología original |
|---|---|---|---|
| 1 | Formación y concientización | Capacitación, evaluaciones, indicadores | FastAPI, LangGraph, ChromaDB, SQLite |
| 2 | Evaluación de riesgos | Riesgos, impacto, mitigación | React + Express + n8n + Qdrant |
| 3 | Derechos de titulares (DSAR) | Solicitudes, plazos, borradores | Python, servidor MCP, RAG BM25, SQLite |
| 4 | Evidencia y auditoría | Evaluar evidencias, dictamen propuesto | FastAPI, skill M1/M2/M3 |
| 5 | Terceros y DPA | Auditar contratos de encargo | n8n (14 flujos), skills, Node |
| 6 | Inventario de datos | Activos y tratamientos | HTML estático (**fuera de alcance**) |
| 7 | Controles y SoA | Declaración de aplicabilidad | Flask, reglas + LLM, FAISS |
| 8 | Incidentes y brechas | Triaje, severidad, 48 h, borradores | Node + React, 4 skills |

## 4. Arquitectura completa
```
navegador ─► frontend (nginx, :8080, único puerto publicado)
                │  /api
                ▼
            backend  ── orquestador ── adaptadores ──► G1 G2 G3 G4 G5 G7 G8   (G6: stub "fuera de alcance")
                │                                          │
                ├─► PostgreSQL (Gestitel + esquema orchestrator)
                └─► llm-gateway ◄──────────────────────────┘  (todos los agentes llaman aquí)
                        │
              cloud (Gemini) │ ollama (otra PC) │ mock (simulado)
```

## 5. Orquestador y flujo de comunicación
1. La interfaz envía `POST /api/agents/{id}/execute` con una acción **que el agente realmente tiene**.
2. El orquestador registra la ejecución en PostgreSQL (`queued → running → succeeded|failed`) y llama al adaptador.
3. El adaptador traduce a la API nativa (HTTP, MCP, webhooks de n8n) y normaliza el resultado.
4. La interfaz hace *polling* de la ejecución persistida: no hay progreso inventado.
5. Contrato común por adaptador: `get_info`, `get_capabilities`, `execute`, `health_check`; estado/resultado/historial los da el orquestador.

## 6. Gateway LLM compartido
Un único punto con la API de OpenAI y la de Ollama. Cada agente se redirige **solo por variables de entorno**, sin tocar su código. `LLM_MODE` elige:
- `cloud` (esta laptop): Gemini por su endpoint compatible con OpenAI.
- `ollama` (otra PC): servicio Docker opcional (perfil `ollama`), **preparado pero no verificado**.
- `mock`: respuestas simuladas, siempre etiquetadas.
El gateway aplica reintentos, tiempo límite, concurrencia máxima, lotes y cuota de embeddings, y registra latencia y tokens (sin cuerpos ni claves). En nube la interfaz avisa que **los datos salen de la máquina**.

## 7. PostgreSQL y conocimiento independiente
La base compartida es **Gestitel** (script del profesor, nunca editado), cargada con `psql`. Esquema `orchestrator` propio para ejecuciones y eventos, y un rol por agente con lectura del PIMS. Los agentes 1, 3, 4 y 8 mantienen sus almacenes privados; las bases de conocimiento no se mezclan.

## 8. Despliegue Docker
`docker compose up --build -d`: postgres + db-init, llm-gateway, backend, frontend y un contenedor por agente (G1, G2 con n8n y Qdrant, G3, G4, G5 con n8n, G7, G8). Volúmenes para los datos; solo se publica el puerto del frontend.

## 9. Demostración de la interfaz unificada
Panel (estado real y motivo de cada agente) → página de un agente → ejecución con datos de demostración → historial → `/actividad` → `/configuracion`. La web es nueva y consistente; las interfaces originales de cada grupo se conservan aparte en sus carpetas, sin incrustarlas.

## 10. Orden recomendado y transiciones
| Orden | Grupo | Transición sugerida |
|---|---|---|
| 1 | G1 Formación | "Se empieza por las personas; ahora, qué puede salir mal…" |
| 2 | G2 Riesgos | "…y cuando una persona ejerce un derecho:" |
| 3 | G3 DSAR | "Cada decisión deja evidencia:" |
| 4 | G4 Auditoría | "Los proveedores también tratan datos:" |
| 5 | G5 Terceros | "¿Qué datos hay? (nota: G6 no se integró en esta ronda)" |
| 6 | G6 Inventario (1 min) | "Con riesgos y datos claros, se declaran controles:" |
| 7 | G7 Controles | "Y si algo falla…" |
| 8 | G8 Incidentes | Cierre: lecciones aprendidas vuelven a la formación (G1) |

## 11. Escenario global de demostración (todo con la organización simulada UNSA)
Reporte de correo enviado por error → G8 clasifica y propone borradores (nada se envía) → sus controles sugeridos → G7 muestra la SoA → G4 evalúa una evidencia de la política → G1 propone formación. Nota: hoy **no hay transporte automático de handoffs** entre agentes; la historia se cuenta pasando de página en página.

## 12. Conclusiones generales
- Se integraron 7 de 8 agentes sin modificar ningún archivo fuente (ver `docs/integration/MODIFICACIONES_A_AGENTES.md`).
- La plataforma funciona con un solo `.env`; el cambio nube ↔ Ollama no toca el código.
- Límites honestos: G6 fuera de alcance; G2 bloqueado por su propio control de revisión; modo Ollama sin ejecutar; acciones humanas (aprobar/decidir) aún solo en las interfaces originales.

## 13. Preguntas probables del profesor
- **¿Por qué no reescribieron los agentes?** Regla de integración: conservar skills y lógica; adaptar solo en el borde.
- **¿Cómo saben que no se alteró el comportamiento?** G3 pasa los mismos 115 tests dentro del contenedor; las partes deterministas (plazos, hash, puntaje) dan lo mismo; el texto del LLM se compara por estructura.
- **¿Qué pasa si un agente cae?** Se marca `caído` con el motivo; los demás siguen.
- **¿Los datos salen a la nube?** En modo `cloud`, sí; la interfaz lo indica. Con Ollama, no.
- **¿Por qué G2 está degradado?** Su política exige una revisión humana (`SCOPE_N8N_REVIEWED`); no la activamos nosotros.
- **¿Qué falta?** Ver sección 12 y `docs/integration/RESULTADOS_PRUEBAS.md`.
