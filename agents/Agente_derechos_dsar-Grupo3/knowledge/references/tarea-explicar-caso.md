# Tarea T5: explicar un expediente

Explica a la persona responsable en qué estado está un caso, por qué y qué sigue. Trabaja solo con hechos del expediente.

**Contesta la pregunta concreta.** La lista de control de abajo es para cuando piden *explicar el caso completo* («explica este caso», «qué debo hacer ahora»). Si preguntan por un solo asunto (por qué requiere revisión, quién aprueba, qué campos se retiraron, cuándo vence), responde solo eso en pocas líneas; no repitas el estado, los motivos ni el plazo si no los pidieron.

## Hechos que puedes usar

`case_id`, `request_types`, `status`, `received_at`, `deadlines`, `deadline_at`, `policy`, `hitl.reasons`, `proposed_actions`, `identity_status`, `record_count` y los nombres de `redacted_fields`.

No uses los valores de los registros ni el texto libre del solicitante, sobre todo con un modelo en la nube.

## Lista de control

```
Explicación:
- [ ] 1. Estado actual y qué significa (workflow-and-states.md)
- [ ] 2. Cada motivo HITL en una línea
- [ ] 3. Siguiente paso concreto y quién lo da
- [ ] 4. Plazo más cercano
- [ ] 5. Derivaciones a otros agentes, si las hay
```

## Siguiente paso según el estado

| Estado | Quién actúa | Qué hace |
|---|---|---|
| `IDENTITY_PENDING` | Responsable | Verificar identidad por el canal autorizado; luego volver a tramitar |
| `APPROVAL_REQUIRED` | DPO u Oficial de Datos Personales | Resolver cada motivo HITL y aprobar o ajustar la propuesta |
| `REVIEW` | Responsable | Revisar y aprobar el borrador |

## Preguntas que debes rechazar

Si piden saltarse la verificación, aprobar en nombre del DPO o marcar algo como ejecutado, responde que no está permitido y explica qué control lo impide (reglas 1–3 de `SKILL.md`).
