# 02 — Evaluación de severidad · INC-20261011-robo-laptop-bienestar

> BORRADOR. Metodología: ENISA 2013 + art. 34.1 (`knowledge/metodologia-severidad.md`).

## Cálculo: SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| DPC | **4** | Salud mental, violencia familiar y situación económica son datos sensibles (4). El ajuste +1 por menores y víctimas sube el contexto, pero ya está en el tope de 4 |
| EI | **1** | Nombre completo + DNI + escuela: identificación directa |
| CB confidencialidad | +0,5 | Equipo robado sin cifrado; destinatario desconocido. Aún no hay evidencia de acceso (si se confirmara que tenía contraseña robusta y cifrado, se reevalúa, pero el reporte indica lo contrario) |
| CB disponibilidad | +0,5 | S-05 no tiene respaldo (`activos-y-datos.md:13`); las fichas del semestre pueden perderse de forma permanente salvo copia en otro lugar `[VERIFICAR]` |
| CB integridad | 0 | Sin indicio de alteración |
| CB intención maliciosa | +0,5 | Robo (aunque pudiera ser oportunista, el modelo lo puntúa) |
| **CB total** | **1,5** | |

**SE = 4 × 1 + 1,5 = 5,5 → MUY ALTA** (consecuencias graves o irreversibles: estigma, riesgo para víctimas de violencia familiar, menores).

Escenario más favorable (sin pérdida de disponibilidad y sin confidencialidad comprometida): 4 × 1 + 0,5 = 4,5, que sigue siendo Muy alta. La conclusión no cambia.

## Decisión según art. 34.1
| Pregunta | Respuesta | Resultado |
|---|---|---|
| ¿Datos sensibles? | **Sí** (salud mental, violencia familiar) | **Notificar a la ANPD** |
| ¿Gran volumen / gran número? | ~150 titulares; sin umbral oficial `[VERIFICAR lineamientos ANPD]`. Ante la duda, sí | Refuerza |
| ¿Perjuicio evidente a otros derechos? | Probable: SE ≥ 3, menores, víctimas de violencia | **Comunicar a los titulares (art. 34.3)** |
| ¿Entorno digital? | Sí, parcialmente: equipo informático y sesión de correo abierta | **Aviso al CNSD (art. 34.5)**; ante la duda, hacerlo |
| ¿Excepción del art. 34.4? | No aplica: no está superado totalmente, no hay cifrado ni confirmación de recuperación | — |

## Conclusión
- **Notificar a la ANPD: SÍ**, antes del 2026-10-13 19:30.
- **Comunicar a titulares: SÍ**, dentro del mismo plazo de 48 h. Para menores, dirigir a su representante `[VERIFICAR con Asesoría Legal el procedimiento]`.
- **Aviso al CNSD: SÍ** (recomendado ante la duda).
- Documentar todo (art. 35).

## Riesgos
- Si no se notifica a tiempo, es infracción grave (art. 133 num. 12). Si se hace tarde, hay que justificar la demora (art. 34.1).
- El plan vigente no define quién notifica (`documento-seguridad-extracto.md:19`). La falta de un responsable designado es un riesgo real de incumplir el plazo.

Trazabilidad: ISO 27035-1 Evaluar y decidir · ISO 27002 5.25 · ISO 27701 6.13.1.5 · art. 34.1, 34.3, 34.4, 34.5.
