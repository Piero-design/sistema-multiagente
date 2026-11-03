---
name: seguimiento_solicitudes
description: Monitorea el estado y los plazos legales de las solicitudes DSAR — lista expedientes, explica en qué estado está cada uno y qué sigue, y calcula o explica plazos por derecho (días hábiles de la Ley 29733, prórroga, suspensión y subsanación) usando solo el motor determinista. Usar ante "plazo", "cuándo vence", "prórroga", "estado", "qué sigue", "explica este caso" o "qué solicitudes están pendientes". No usar para registrar solicitudes (registrar_solicitudes) ni para redactar respuestas o consultar la norma (gestionar_derechos).
---

# Seguimiento de solicitudes DSAR

## Qué hace

Responde en qué estado está cada solicitud, por qué, quién debe actuar y cuándo vence. **El plazo lo calcula el motor** (`dsar.core`) desde el perfil; nunca se estima de memoria. ISO/IEC 27701 no fija un número de días.

## Tareas

| Señal en la petición | Tarea | Lee | Herramienta |
|---|---|---|---|
| "qué solicitudes hay", "pendientes", "vencen pronto" | Listar | — | `dsar_listar(status)` |
| "plazo", "cuándo vence", "cuántos días", "prórroga" | Plazos | [tarea-plazos.md](../../knowledge/references/tarea-plazos.md) | `dsar_plazos(case_id)` · `dsar_calcular_plazos(request_types, received_at, policy_id)` sin expediente |
| "por qué", "qué sigue", "estado", "explica este caso" | Explicar caso | [tarea-explicar-caso.md](../../knowledge/references/tarea-explicar-caso.md) | `dsar_estado(case_id)` |

Si la petición combina tareas: primero plazos, luego explicación.

## Reglas de plazos

- El conteo empieza el **día siguiente** a la recepción (D.S. 016-2024-JUS, art. 69).
- Perfil PE: **días hábiles** (sin sábados, domingos ni feriados del perfil). Perfil LAB: días naturales.
- Cada derecho conserva su plazo; `deadline_at` es el más cercano.
- Si la política interna es más estricta, menciona el plazo interno (`deadline_at`) y el legal (`legal_deadline_at`).
- Prórroga (art. 71), suspensión por información adicional (art. 70) y subsanación (art. 66.2): el motor calcula las fechas, pero **solo las aplica una persona**. Preséntalas como pendientes de aprobación.
- Si el cálculo trae `error` (por ejemplo, el perfil no admite ese derecho), explica el motivo y no propongas otra fecha. Sin fecha de recepción, derechos y perfil, pídelos.

## Estado y quién actúa

| Estado | Quién actúa | Qué hace |
|---|---|---|
| `IDENTITY_PENDING` | Responsable | Verificar la identidad por el canal autorizado; sin ella, cero registros |
| `APPROVAL_REQUIRED` | DPO u Oficial de Datos Personales | Resolver cada motivo HITL y aprobar o rechazar |
| `REVIEW` | Responsable | Revisar y aprobar el borrador |
| `ON_HOLD` | Titular / responsable | Esperar subsanación o información adicional (plazo suspendido) |
| `APPROVED` / `REJECTED` / `CANCELLED` | — | Decisión humana registrada; ver derivaciones en gestionar_derechos |

Estados y transiciones completos: [workflow-and-states.md](../../knowledge/references/workflow-and-states.md).

## Cómo responder

- Contesta la pregunta concreta en pocas líneas; la explicación completa (estado, motivos HITL, siguiente paso, plazo más cercano, derivaciones) solo si piden "explica este caso".
- Usa solo hechos del expediente: `case_id`, `request_types`, `status`, `received_at`, `deadlines`, `deadline_at`, `policy`, `hitl.reasons`, `proposed_actions`, `identity_status`, `record_count` y los nombres de `redacted_fields`. Nunca valores de registros ni el texto del solicitante.
- Si recibes `plazos_calculados_por_motor`, úsalos tal cual; las fechas del expediente están en UTC.
- Si piden saltarse la verificación, aprobar en nombre del DPO o marcar algo como ejecutado, responde que no está permitido y qué control lo impide.
