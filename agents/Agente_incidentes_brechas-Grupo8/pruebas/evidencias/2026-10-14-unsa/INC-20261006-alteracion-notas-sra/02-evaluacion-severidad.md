# 02 · Evaluación de severidad — INC-20261006-alteracion-notas-sra

> ESCENARIO SIMULADO. BORRADOR para revisión del ODP. Metodología: ENISA (2013) + art. 34.1 (`knowledge/metodologia-severidad.md`).

## 1. Puntuación SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| **DPC** | **2** | Base 1 (datos académicos simples). **+1** por contexto: una nota alterada afecta aprobación, grado/título y la reputación académica del titular, con relación de dependencia con la universidad. Entre los ~28 000 activos hay ~900 menores (`activos-y-datos.md:22`); no se sabe si hay menores entre los 23 |
| **EI** | **1** | El SRA vincula cada nota con nombre y DNI del estudiante (identificación directa) |
| **CB integridad** | +0,25 | Alteradas, posiblemente usadas (un estudiante ya reclamó, el acta difiere); recuperables con actas firmadas (S-02) y respaldo del 04/10 `[VERIFICAR integridad del respaldo; nunca se probó la restauración]` |
| **CB confidencialidad** | +0,25 | Acceso por persona no autorizada (número limitado, desde un equipo conocido). Lectura no verificable (solo se auditan modificaciones). Valor prudente |
| **CB disponibilidad** | 0 | Sin indicios de indisponibilidad |
| **CB intención maliciosa** | +0,5 | Uso deliberado de una cuenta ajena, de madrugada, para subir notas (uso indebido intencional) |
| **CB total** | **1,0** | |

**SE = 2 × 1 + 1,0 = 3,0 → ALTA** (3 a < 4).
Sensibilidad: sin el +0,25 de confidencialidad, SE = 2,75 (Media). Si se comprobara el acceso a otras escuelas o la extracción de datos, el valor sube (más titulares y CB). Se mantiene Alta por prudencia.

## 2. Decisión sobre el art. 34.1
| Supuesto | ¿Se cumple? | Razón |
|---|---|---|
| Grandes volúmenes (cantidad o tipo) | **Duda** | Confirmados 23 registros, pero la cuenta pudo acceder a un banco de 89 000 titulares (28 000 + 61 000) y no hay log de lectura |
| Gran número de personas | **Duda** | Alcance no delimitado: solo se revisó una cuenta y no se sabe de otras escuelas |
| Datos sensibles | No | Datos académicos. [VERIFICAR] si en el SRA hay datos de discapacidad u otros sensibles accesibles con ese perfil |
| Perjuicio evidente a otros derechos o libertades | **Probable** | Notas fraudulentas pueden invalidar aprobaciones, grados o títulos y perjudicar a quienes no se beneficiaron. SE = 3 se trata como "perjuicio evidente" probable (criterio de apoyo) |

### Recomendación (ante la duda, notificar)
1. **Notificar a la ANPD** dentro de las 48 h (art. 34.1). Se presenta con la información disponible y se complementa después. Si se pasa de la hora límite, justificar la demora. La obligación existe aunque la cuenta ya esté bloqueada.
2. **Notificar al CNSD** (art. 34.5): ocurrió en el SRA, un entorno digital.
3. **Comunicar a los titulares** (art. 34.3). SE ≥ 3 activa el criterio de perjuicio evidente.
   - Públicos: los 23 estudiantes. Se amplía si la revisión descubre más.
   - Cautela: antes de enviar, Asesoría Legal y la autoridad competente deben decidir cómo y cuándo, para no perjudicar la investigación disciplinaria ni afectar a quien no participó. `[VERIFICAR]` compatibilidad con el plazo de 48 h.
   - La excepción del art. 34.4 **no aplica**: no se ha superado totalmente la afectación; la restauración de las notas no está hecha.
4. **Documentar** (art. 35) en cualquier caso.

## 3. Factores que agravan la lectura
- Cuenta de jubilado sin baja y sin MFA (`activos-y-datos.md:31`; `documento-seguridad-extracto.md:4.1, 4.4`).
- Cuentas de secretaría compartidas (4.1): dificulta atribuir la autoría.
- Retención de logs de 60 días frente a los 2 años del art. 46.3 (`activos-y-datos.md:33`).
- El documento de seguridad dice que no hay procedimiento de notificación a la ANPD ni responsable definido (`documento-seguridad-extracto.md:5.3`).
- Detección tardía: 5 días entre el hecho (06–07/10) y el bloqueo (12/10); la detección vino de un reclamo, no de una alerta.

## 4. Supuestos y límites
- No existe un umbral oficial de "grandes volúmenes" ni de "gran número"; los lineamientos de la ANPD quedan `[VERIFICAR si se publicaron]`.
- Puntuación basada solo en el reporte y un log resumido (20 de las 23 modificaciones no están detalladas).
