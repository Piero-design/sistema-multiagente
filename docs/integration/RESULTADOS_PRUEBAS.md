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

## Pendiente o no verificado

- **Modo `ollama`**: solo `docker compose --profile ollama config`. Ver `docs/installation/OLLAMA_OTRA_PC.md`.
- **G2**: la norma está indexada (271 vectores de 3072 dimensiones) y los workflows activos, pero el chat no se probó porque el control de alcance del grupo sigue bloqueado por decisión humana.
- Las reglas de aprobación humana de G3, G5 y G8 se verifican a nivel de **capacidades expuestas** (ninguna acción de aprobar/decidir/enviar); no se probó contra los endpoints nativos de decisión.
- No hay test de la regla de G3 "la nube solo recibe hechos minimizados": su servidor MCP no usa LLM.
- Handoffs de G3 a otros agentes: no se transportan todavía; la tabla `orchestrator.handoff` existe pero está sin uso.
- Las acciones humanas (verificar identidad y decidir en G3; DPO/Legal en G5; aprobar acciones en G8) no están en la interfaz unificada.
- Campos de respuesta de G2 `/api/chat` no verificados contra un servicio vivo.
