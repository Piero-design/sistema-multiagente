# 02 · Evaluación de severidad — INC-20261012-dos-portal-matricula

> BORRADOR. Metodología ENISA 2013 (`knowledge/metodologia-severidad.md`). Evaluación **precautoria**: se puntúa como si el DoS contara como brecha de disponibilidad de datos personales.

## Puntaje: SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| DPC | **2** | Datos simples (nombre, DNI, datos académicos) = 1; +1 por menores (~900 activos ≤17 años, `activos-y-datos.md:22`). No se identificaron datos sensibles en S-08 `[VERIFICAR qué campos guarda el portal]` |
| EI | **1** | Identificación directa (nombre + DNI), aunque no hay evidencia de que se hayan expuesto |
| CB | **0,75** | Disponibilidad +0,25 (temporal; la caída duró 2 h 30 min y el servicio volvió). Intención maliciosa +0,5 (DoS deliberado). Confidencialidad e integridad 0 **según lo reportado (sin verificar)** |
| **SE** | **2 × 1 + 0,75 = 2,75** | **Media** (rango 2 a <3) |

Sensibilidad: si la revisión de logs mostrara exfiltración de datos de menores/identificables (confidencialidad +0,5), SE = 3,25 → **Alta**.

## Supuestos del art. 34.1
| Supuesto | ¿Se cumple? |
|---|---|
| Grandes volúmenes en cantidad o tipo | No hay exposición: no aplica según lo reportado |
| Gran número de personas | ~1 200 afectados en su servicio, no en sus datos; sin umbral oficial `[VERIFICAR lineamientos ANPD]` |
| Datos sensibles | No identificados en S-08 |
| Perjuicio evidente a otros derechos | No: inconveniente superado con ampliación del plazo (verificar que nadie perdió su vacante) |

## Decisión
- **Sobre la información reportada: no hay obligación de notificar a la ANPD (art. 34.1) ni de comunicar a titulares (art. 34.3–34.4).** No ocurrió una vulneración con destrucción, pérdida, alteración o exposición de datos personales. **Se documenta (art. 35).**
- Esta decisión es **condicional**: se apoya en una afirmación no verificada. **Si antes de las 09:10 del 14/10 no se puede comprobar con logs que no hubo acceso o exportación, se recomienda notificar a la ANPD** (regla "ante la duda"), con una nota que lo explique. Con indicios de acceso, notificar sin esperar.
- **CNSD:** el art. 34.5 aplica a incidentes de datos personales en entorno digital. Un DoS es un incidente de seguridad digital; evaluar con Asesoría Legal si el D.U. 007-2020 obliga a reportarlo `[VERIFICAR]`.
- No se generan borradores 03 porque no hay obligación confirmada. Se pueden preparar en minutos si cambia la decisión.
