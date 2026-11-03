# Evaluación de severidad — INC-20260930-correo-equivocado-colegio

- **Insumo:** `salidas/INC-20260930-correo-equivocado-colegio/01-ficha-incidente.md`
- **Metodología:** ENISA (2013), SE = DPC × EI + CB — ver `knowledge/metodologia-severidad.md`
- **Fecha/hora de la evaluación:** 2026-10-01 23:25 (-05:00). Caso ficticio de prueba (PR-10).

## 1. Cálculo

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 3 | Dato más delicado: situación de pago de la pensión y **monto adeudado** (dato financiero, "deudas" → 3). No se asigna 4 porque no está confirmado que una deuda de pensión sea "ingresos económicos" (sensible) `[VERIFICAR]`. |
| Ajuste de contexto | +1 | Datos de **420 menores** (identidad + notas) cruzados con la situación de deuda de su familia: el conjunto permite perfilar y estigmatizar al alumno. |
| **DPC final** | **4** | 3 + 1 (tope de la escala). |
| **EI** | **1** | Identificación directa: nombre completo + DNI del alumno; nombre + celular del apoderado. Sin cifrado conocido (se presume que no lo había). |
| CB — confidencialidad | +0,25 | Un destinatario no autorizado **conocido** (empresa de fotos); sin evidencia de publicación ni reenvío, pero sin confirmación escrita de eliminación, así que no corresponde 0. |
| CB — integridad | 0 | No hay alteración; el colegio conserva el original. |
| CB — disponibilidad | 0 | Sin pérdida de disponibilidad. |
| CB — intención maliciosa | 0 | Error humano; sin indicios de ataque ni uso intencional. |
| **CB total** | **0,25** | 0,25 + 0 + 0 + 0 |

**SE = 4 × 1 + 0,25 = 4,25 → Severidad MUY ALTA** (SE ≥ 4)

> Sensibilidad: sin el ajuste por menores (DPC = 3), SE = 3 × 1 + 0,25 = 3,25, que sigue siendo **Alta**. Si la empresa reconociera un reenvío, CB de confidencialidad pasaría a +0,5 y SE = 4,5. En cualquier lectura razonable, la severidad es Alta o mayor.

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad | Motivo |
|---|---|---|
| Discriminación o estigmatización del alumno por la deuda familiar o por sus notas | Media | El archivo une identidad del menor, rendimiento y situación de pago, en manos de un tercero sin control verificado. |
| Afectación de la intimidad y daño reputacional de las familias (situación económica expuesta) | Media | Estado "en deuda" y monto asociados a nombre y celular del apoderado. |
| Estafa dirigida a apoderados (falsas cobranzas de pensión por llamada o mensaje) | Media | Un tercero tiene nombre, celular, condición de deudor y monto exacto, lo que basta para un engaño creíble. |
| Suplantación de identidad del menor o del apoderado | Baja | Nombre + DNI sirven para algunos trámites, pero no hay datos de autenticación ni bancarios. |
| Acoso o presión indebida | Baja | Requeriría uso intencional por el receptor; no hay indicios. |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Duda** | Monto adeudado: financiero; su encaje en "ingresos económicos" no está confirmado `[VERIFICAR]`. |
| | Grandes volúmenes (cantidad o tipo) | **Duda (probable por tipo)** | 420 registros de menores con datos financieros de sus familias; el reglamento no fija umbral `[VERIFICAR lineamientos ANPD]`. |
| | Gran número de personas | **Duda** | Hasta ~840 titulares; sin umbral oficial `[VERIFICAR lineamientos ANPD]`. |
| | Perjuicio evidente a derechos o libertades | **Sí (probable)** | SE = 4,25 (Muy alta); criterio de apoyo: SE ≥ 3 se trata como perjuicio evidente probable (intimidad, no discriminación de menores). |
| **Resultado ANPD** | Basta un supuesto, y hay duda razonable en los otros tres | **Notificar** (obligación probable) | Art. 34.1. Ante la duda, se recomienda notificar. La obligación se mantiene aunque la empresa confirme después la eliminación ("aun cuando [...] haya sido subsanado"). |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí, comunicar** (obligación probable) | Afectación probable a la intimidad y a la no discriminación. La excepción del art. 34.4 **no aplica**: falta la constancia escrita de eliminación, así que el incidente no está "superado totalmente" (y la afectación no se descarta). Destinatarios: apoderados, por sí y como representantes de los menores. |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Sí** | La exposición se produjo mediante correo electrónico institucional. |
| Documentar (art. 35) | Siempre | **Sí** | Hechos, efectos y medidas: ver `04-respuesta-y-cierre.md`, sección 5. |

## 4. Plazos
- **Toma de conocimiento:** 2026-09-30, 15:30 (lectura más temprana; referencia: reporte formal a las 16:20)
- **Hora límite (48 h):** **2026-10-02, 15:30**. Al 2026-10-01 23:25 han pasado 31 h 55 min y **quedan 16 h 05 min** (plazo **vigente**). Aplica a la ANPD y también a la comunicación a titulares (art. 34.3).
- El plazo vence en horario de oficina del día siguiente y queda una noche de por medio: la aprobación debe programarse a primera hora del 2026-10-02.
- Si se notifica después de 2026-10-02 15:30, la notificación debe incluir los **motivos de la demora** y su sustento (art. 34.1).
- Riesgo de lectura estricta (no adoptada): contando desde el envío (2026-09-29 17:05), el plazo habría vencido el 2026-10-01 17:05 `[VERIFICAR con asesoría legal]`.

## 5. Nota aparte: impacto para la organización
- Riesgo de **infracción grave** (art. 133 num. 12) si no se notifica a la ANPD cuando corresponde según el art. 34.
- Daño reputacional ante las familias y la comunidad educativa.
- Posible falta de minimización: el archivo mezclaba notas y pensiones, aunque la contadora probablemente solo necesitaba los datos de pago (inferencia).
- Estos puntos **no** se suman a la severidad para los titulares.

## 6. Supuestos e información pendiente
- Se presume que el archivo no tenía contraseña ni cifrado (NO INDICADO). Si la tuviera y la clave no se hubiera compartido, EI = 0,25 y CB de confidencialidad = 0 (SE = 1,0).
- Calificación del monto adeudado como dato sensible: `[VERIFICAR]`. Si se confirma, el supuesto "datos sensibles" basta por sí solo (SE no cambia).
- Falta la confirmación escrita de la empresa de fotos sobre eliminación y no uso.
- Número real de apoderados y de familias "en deuda": NO INDICADO.
- Umbrales de "grandes volúmenes" y "gran número": `[VERIFICAR lineamientos ANPD]`.
- Datos del Oficial de Datos Personales (art. 34.2 num. 2): NO INDICADO.

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
