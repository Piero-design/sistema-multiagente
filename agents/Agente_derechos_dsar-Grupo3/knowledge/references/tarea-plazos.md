# Tarea T4: calcular y explicar plazos

El cálculo es determinista y lo hace el motor (`compute_deadlines`). Tu trabajo es leer el resultado y explicarlo, nunca calcularlo de memoria.

## De dónde salen las fechas

- **Con expediente cargado:** `deadlines` y `deadline_at` de los hechos del expediente.
- **Sin expediente, con fecha y derechos en la pregunta:** el servicio llama al motor (`standalone_deadlines`) y te entrega `plazos_calculados_por_motor`. Usa esas fechas tal cual. Si la política interna es más estricta, cada derecho trae el plazo interno (`deadline_at`) y el legal (`legal_deadline_at`): menciona ambos.
- **Si `plazos_calculados_por_motor` trae `error`:** explica el motivo (por ejemplo, el perfil no admite ese derecho); no propongas otra fecha.
- **Sin expediente ni cálculo:** pide la fecha de recepción, los derechos y el perfil. No estimes la fecha.

## Lista de control

```
Plazos:
- [ ] 1. Leer deadlines del expediente o de plazos_calculados_por_motor (uno por derecho)
- [ ] 2. Indicar el tipo de día: hábil (PE) o natural (LAB)
- [ ] 3. Citar la base legal de cada plazo (campo legal_basis)
- [ ] 4. Señalar el plazo más cercano (deadline_at)
- [ ] 5. Si se pide prórroga, marcarla como pendiente de aprobación
```

## Reglas de cómputo del motor

- El conteo empieza el **día siguiente** a la recepción (D.S. 016-2024-JUS, art. 69).
- **Días hábiles (PE):** se excluyen sábados, domingos y los feriados nacionales listados en el perfil.
- **Días naturales (LAB):** se suman días corridos.
- **Solicitud combinada:** cada derecho conserva su plazo; `deadline_at` es el más cercano.

## Prórroga, suspensión y subsanación (perfil PE)

El motor calcula estas fechas, pero **solo las aplica una persona** desde el panel. Tú no las aplicas ni las propones como hechas: explica la regla y márcala como pendiente de aprobación.

| Situación | Regla | Qué calcula el motor |
|---|---|---|
| Prórroga (art. 71) | Una sola vez, por un plazo igual como máximo, justificada y comunicada dentro del plazo original. No aplica al derecho de información. | Nuevo vencimiento del derecho (`extended`, `extension.original_deadline_at`) |
| Requerimiento de información adicional (art. 70) | El responsable puede pedirla dentro de 7 días hábiles; el titular tiene 10 y el plazo se suspende mientras tanto. | Estado `ON_HOLD`; al reanudar, todos los plazos se desplazan los días hábiles suspendidos (`suspended_days`) |
| Solicitud incompleta (art. 66.2) | Observación en 5 días hábiles y subsanación en 5; si no se subsana, se tiene por no presentada. | Estado `ON_HOLD`; si vence sin subsanar, **propone** `CANCELLED` y una persona decide |

Con recepción el 2026-10-01, el requerimiento del art. 70 puede hacerse hasta el 2026-10-13 y la observación del art. 66.2 hasta el 2026-10-09.

## Ejemplo

Solicitud recibida el jueves 2026-10-01 con perfil `PE-LEY29733` (feriado el 2026-10-08):

- Información: 8 días hábiles → 2026-10-14
- Rectificación: 10 días hábiles → 2026-10-16
- Acceso: 20 días hábiles → 2026-10-30
