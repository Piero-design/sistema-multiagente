# Evaluación de severidad — INC-20260930-correo-equivocado-colegio

- **Insumo:** `pruebas/evidencias/2026-10-01-agente/INC-20260930-correo-equivocado-colegio/01-ficha-incidente.md` (única fuente; prueba PR-06 de reproducibilidad)
- **Metodología:** ENISA (2013), SE = DPC × EI + CB — ver `knowledge/metodologia-severidad.md`
- **Caso ficticio de prueba.** Se trabaja solo con categorías y cantidades.

## 1. Cálculo

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 3 | Dato más delicado afectado: estado de pago de la pensión y **monto adeudado** (dato financiero: deudas → 3). No se toma 4 porque una deuda no es con certeza "ingresos económicos" (dato sensible); queda como duda `[VERIFICAR]` (ver sección 6). |
| Ajuste de contexto | +1 | Datos de **420 menores** (identidad y notas del bimestre) vinculados a la situación de deuda de su familia: el conjunto permite perfilar y estigmatizar al alumno ante un tercero. |
| **DPC final** | **4** | 3 + 1 (tope de la escala: 4). |
| **EI** | **1** | Identificación directa: nombre completo + DNI del alumno, y nombre + celular del apoderado. No consta cifrado ni contraseña (se presume que no). |
| CB — confidencialidad | +0,25 | Expuestos a un número conocido de destinatarios no autorizados (la empresa de fotos); sin evidencia de publicación ni reenvío, pero tampoco confirmación escrita de eliminación → no corresponde 0. |
| CB — integridad | 0 | No hay alteración de datos; el colegio conserva el archivo original. |
| CB — disponibilidad | 0 | Sin pérdida de disponibilidad: el original sigue en poder del colegio. |
| CB — intención maliciosa | 0 | Error humano (destinatario equivocado), sin indicios de robo, ataque ni uso intencional indebido. |
| **CB total** | **0,25** | 0,25 + 0 + 0 + 0 |

**SE = 4 × 1 + 0,25 = 4,25 → Severidad Muy alta** (SE ≥ 4)

> Sensibilidad del resultado: aun si el DPC final se fijara en 3 (sin ajuste), SE = 3 × 1 + 0,25 = 3,25 → Alta. En cualquier lectura razonable, la severidad es ≥ Alta.

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad (baja/media/alta) | Motivo |
|---|---|---|
| Discriminación o estigmatización del alumno por la deuda de su familia o por sus notas | Media | El archivo cruza identidad del menor, rendimiento académico y situación de pago; un tercero ajeno al colegio lo tiene sin control verificado. |
| Daño reputacional y afectación de la intimidad de las familias (exposición de su situación económica) | Media | Monto adeudado y estado "en deuda" asociados a nombre y celular del apoderado. |
| Fraude o estafa dirigida a apoderados (llamadas o mensajes falsos de "cobranza" de la pensión) | Media | El receptor tiene nombre, celular, condición de deudor y monto exacto: insumo directo para *phishing*/*vishing* creíble. |
| Suplantación de identidad del menor o del apoderado | Baja | Nombre + DNI permiten algunos trámites, pero no hay datos de autenticación ni bancarios. |
| Acoso o presión de cobranza indebida | Baja | Requeriría uso intencional por el receptor; no hay indicios. |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Duda** | El monto adeudado es financiero; no está confirmado que encaje en "ingresos económicos" (dato sensible, Ley 29733). `[VERIFICAR]` |
| | Grandes volúmenes (cantidad o tipo) | **Duda (probable por tipo)** | 420 registros de menores + datos financieros de sus apoderados en un solo archivo; el reglamento no fija umbral. `[VERIFICAR lineamientos ANPD]` |
| | Gran número de personas | **Duda** | Hasta ~840 titulares (420 alumnos + hasta 420 apoderados); sin umbral oficial. `[VERIFICAR lineamientos ANPD]` |
| | Perjuicio evidente a derechos o libertades | **Sí (probable)** | SE = 4,25 (Muy alta); criterio de apoyo: SE ≥ 3 se trata como perjuicio evidente probable (intimidad, no discriminación de menores). |
| **Resultado ANPD** | Basta un supuesto; además hay duda razonable en los otros tres | **Notificar** (obligación probable) | Art. 34.1; ante la duda, se recomienda notificar. La obligación subsiste aunque la empresa luego confirme la eliminación. |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí — comunicar** (obligación probable) | Hay afectación probable a la intimidad y a la no discriminación; la excepción del art. 34.4 **no aplica**: no hay constancia escrita de eliminación, así que el incidente no está "superado totalmente". Comunicar a los apoderados (por sí y como representantes de los menores), en lenguaje claro. |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Sí** | La exposición ocurrió mediante correo electrónico institucional. |
| Documentar (art. 35) | Siempre | **Sí** | Registrar hechos, efectos y medidas adoptadas. |

## 4. Plazos
- **Toma de conocimiento:** 2026-09-30, 15:30 (la contadora avisa que no recibió el archivo)
- **Hora límite (48 h):** **2026-10-02, 15:30** — Tiempo restante: plazo **vigente**; a las 00:00 del 2026-10-01 quedaban 39 h 30 min (la hora exacta de esta evaluación no consta: calcular desde el momento de lectura). Aplica tanto a la ANPD como a la comunicación a titulares (art. 34.3).

## 5. Nota aparte: impacto para la organización
- Riesgo de **infracción grave** (art. 133 num. 12) si no se notifica a la ANPD cuando corresponde conforme al art. 34.
- Daño reputacional ante las familias y la comunidad educativa; posible pérdida de confianza y reclamos.
- Revisión del principio de minimización: un mismo archivo mezclaba notas y pensiones, aunque la contadora probablemente solo necesitaba los datos de pago (pendiente en la ficha).
- Estos puntos **no** se suman a la severidad para los titulares.

## 6. Supuestos e información pendiente
- Se presume que el archivo no tenía contraseña ni cifrado (NO INDICADO en la ficha). Si estuviera cifrado con clave no comprometida, EI bajaría a 0,25 y CB de confidencialidad a 0.
- Calificación del monto adeudado como dato sensible ("ingresos económicos"): `[VERIFICAR]`. Si se confirmara, DPC base = 4 y el supuesto "datos sensibles" del art. 34.1 se cumpliría por sí solo (el resultado de SE no cambia: 4,25).
- Falta confirmación escrita de la empresa de fotos sobre eliminación y no uso; si reconociera reenvío o uso, CB de confidencialidad subiría a +0,5 (SE = 4,5).
- Número real de apoderados distintos y de apoderados "en deuda": NO INDICADO.
- Umbrales de "grandes volúmenes" y "gran número de personas": no fijados por el reglamento `[VERIFICAR lineamientos ANPD]`.
- Datos del Oficial de Datos Personales o punto de contacto (art. 34.2 num. 2): NO INDICADO; necesarios para la notificación.

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
