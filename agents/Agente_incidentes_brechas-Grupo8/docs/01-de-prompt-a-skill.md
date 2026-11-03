# Etapa 1 — De prompt a skill

**Objetivo:** transformar una tarea que se resolvía con un prompt suelto en un proceso reutilizable.

## Problema con el prompt suelto
Cuando ocurre un incidente, la presión es alta y el tiempo corto: el reglamento da **48 horas** para notificar. Un prompt improvisado produce respuestas distintas cada vez, no deja registro del razonamiento y puede omitir pasos obligatorios.

## Los prompts originales

| # | Prompt suelto |
|---|---|
| 1 | "Nos hackearon, ¿qué hacemos?" |
| 2 | "¿Esto es grave? ¿Tenemos que avisar a alguien?" |
| 3 | "Escríbeme un correo para avisar a los clientes que se filtraron sus datos." |
| 4 | "Hazme un informe de lo que pasó." |

## Qué les faltaba (resultado de probarlos con los casos de `examples/entradas/`)

| Carencia | Consecuencia observada |
|---|---|
| No distinguía evento, incidente y brecha | Trataba un phishing bloqueado como brecha, o un correo equivocado como "no pasó nada" |
| Sin reloj | No calculaba el plazo de 48 h ni preguntaba cuándo se tomó conocimiento |
| Sin criterio de severidad | "Es grave" o "es leve" sin justificación reproducible |
| Marco legal genérico o extranjero | Citaba el RGPD (72 h) en lugar del D.S. 016-2024-JUS (48 h) |
| Sin contenido mínimo | La notificación omitía el punto de contacto o las medidas (art. 34.2) |
| Destruía evidencia | Recomendaba "formatear y restaurar" antes de preservar logs y discos |
| Sin registro | No dejaba la documentación que exige el art. 35 |

## Proceso de transformación

1. **Ejecutar** cada prompt con un caso ficticio y anotar los fallos (tabla anterior).
2. **Mapear la tarea a un estándar:** las fases de ISO/IEC 27035-1:2023 dieron la secuencia natural de pasos.
3. **Descomponer** cada fase en los pasos que seguiría un analista de respuesta a incidentes.
4. **Externalizar criterios** en `knowledge/`: definición legal, supuestos del art. 34.1, fórmula ENISA, taxonomía.
5. **Fijar la salida** con plantillas: ficha, evaluación, notificación, informe de cierre.
6. **Añadir reglas:** no inventar, primero el reloj, ante la duda notificar, borrador para revisión humana.
7. **Definir la activación** con descripciones precisas (etapa 2).
8. **Probar y ajustar** (`pruebas/`).

## Resultado

| Prompt original | Skill resultante | Fase ISO/IEC 27035 |
|---|---|---|
| Prompt 1 (parte "¿qué es?") | `brecha-triaje` | Detectar y reportar / Evaluar y decidir |
| Prompt 2 | `brecha-evaluacion-severidad` | Evaluar y decidir |
| Prompt 3 | `brecha-notificacion` | Responder |
| Prompts 1 (parte "¿qué hacemos?") y 4 | `brecha-respuesta-cierre` | Responder / Aprender lecciones |

## Ganancias
- **Consistencia:** el mismo caso produce la misma estructura y la misma decisión.
- **Cumplimiento:** cada salida cubre el contenido mínimo del art. 34.2 y el registro del art. 35.
- **Trazabilidad:** cada decisión cita una fase ISO, un control o un artículo.
- **Encadenamiento:** la ficha alimenta la severidad, la severidad alimenta la notificación y todo alimenta el cierre.
