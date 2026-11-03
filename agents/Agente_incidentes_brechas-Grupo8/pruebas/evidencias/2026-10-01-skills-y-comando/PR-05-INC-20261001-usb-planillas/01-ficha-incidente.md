# Ficha de incidente — INC-20261001-usb-planillas

> **ID provisional.** La fecha del ID (2026-10-01) es la **fecha de registro**, no la de toma de conocimiento, que es **NO INDICADA**. Corregir el ID cuando se confirme.

- **Organización (responsable del tratamiento):** NO INDICADO (inferencia: la organización empleadora del personal cuyas planillas estaban en la USB)
- **Reportado por:** NO INDICADO (inferencia: un trabajador interno, por el uso de "se nos perdió") — ¿Es encargado del tratamiento? NO INDICADO (inferencia: No, parece personal propio; si fuera un proveedor de planillas/contabilidad externo, aplica el art. 36)
- **Canal de reporte:** Mensaje informal al Oficial de Datos Personales

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Ocurrencia del incidente (pérdida de la USB) | NO INDICADO | NO INDICADO |
| **Toma de conocimiento** (inicia el plazo) | NO INDICADO | NO INDICADO — **pendiente crítica** |
| Reporte al responsable (ODP) | 2026-10-01, hora NO INDICADA | Hecho (fecha de recepción del mensaje) |
| **Hora límite de notificación (48 h, art. 34.1)** | **No calculable.** Cota máxima: 2026-10-03 a la misma hora en que se recibió este mensaje, **solo si** la toma de conocimiento fue en ese momento | Calculada / condicionada |

**Advertencia sobre el plazo.** Según el criterio de `knowledge/marco-normativo-peru.md` ("¿Desde cuándo corren las 48 horas?"), el plazo corre desde el primer momento en que **cualquier persona de la organización** supo con certeza razonable de la pérdida (por ejemplo, la persona que notó que ya no tenía la USB), no desde que llegó al ODP. Es probable que esa toma de conocimiento sea **anterior** a este mensaje, por lo que **el plazo ya podría estar corriendo o incluso cerca de vencer**.
- Lectura más temprana (la que se usa): hora en que quien custodiaba la USB notó la pérdida → hora límite = esa hora + 48 h. **Pendiente.**
- Lectura de referencia: hora de recepción de este reporte por el ODP (2026-10-01) + 48 h → 2026-10-03, misma hora.
- Si al confirmar la hora resulta que ya pasaron 48 h, la notificación deberá incluir la **justificación de la demora** con sustento (art. 34.1).

## 2. Descripción de lo ocurrido
Se reporta la pérdida de una memoria USB que contenía "las planillas del personal" (hecho). No se indica cuándo, dónde ni cómo se perdió, quién la custodiaba, si estaba cifrada o protegida con contraseña, ni si existe copia de respaldo (NO INDICADO). Por el contenido habitual de una planilla de remuneraciones, la USB contendría datos identificativos, laborales, económicos y bancarios de los trabajadores (inferencia). No hay indicios aún de que un tercero haya accedido a los archivos, pero tampoco puede descartarse (inferencia).

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☒ **Incidente de seguridad de datos personales (brecha)** — *brecha probable*, hasta confirmar si la USB estaba cifrada.
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"): hubo una vulneración de un control de seguridad (custodia del soporte) que ocasiona la **pérdida** de datos personales y una posible **exposición no autorizada** a ellos. Las planillas contienen datos personales de trabajadores (art. III num. 16 se cumple). Aun si la USB estuviera cifrada, seguiría siendo un incidente que se documenta (art. 35); el cifrado solo influiría en la severidad y en la obligación de notificar.

## 4. Clasificación
- **Tipo:** ☒ Confidencialidad (posible acceso de quien encuentre la USB) ☐ Integridad ☒ Disponibilidad (pérdida del soporte; relevante si no hay respaldo — NO INDICADO)
- **Categoría:** `FIS` — Pérdida o robo físico
- **Entorno digital:** Por confirmar `[VERIFICAR]`. La pérdida es física, pero los datos están en soporte digital. Inferencia: no se desarrolla "en y/o mediante el entorno digital" en sentido estricto, salvo que se detecte uso de los datos en línea o que la USB haya sido conectada a sistemas. → Notificación adicional al CNSD (art. 34.5): **Por decidir** con asesoría; criterio prudente, evaluarlo en la etapa de severidad/notificación.
- **Prioridad:** **P2 Alta** — brecha probable con datos personales y reloj de 48 h corriendo (con hora de inicio desconocida). Escalar a **P1** si se confirma que los archivos incluyen datos sensibles (p. ej., salud o afiliación sindical) y no estaban cifrados, o si aparecen expuestos públicamente.

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Identificativos (nombres, DNI, cargo, área) | No | Trabajadores | NO INDICADO (inferencia: no, salvo practicantes menores) | NO INDICADO | Inferencia |
| Económicos y laborales (remuneración, descuentos, aportes AFP/ONP, retenciones) | No (pero de alto impacto por riesgo de fraude) | Trabajadores | — | NO INDICADO | Inferencia |
| Datos bancarios (cuenta de abono de haberes) | No (alto impacto) | Trabajadores | — | NO INDICADO | Inferencia |
| Posible afiliación sindical (descuento de cuota sindical) | **Sí** (dato sensible, Ley 29733) | Trabajadores | — | NO INDICADO | Inferencia — confirmar |
| Posible información de salud (descansos médicos, subsidios, EPS) | **Sí** (dato sensible) | Trabajadores | — | NO INDICADO | Inferencia — confirmar |
| Derechohabientes / dependientes (asignación familiar, EPS) | Por confirmar | Familiares de trabajadores | **Posible** (hijos) | NO INDICADO | Inferencia — confirmar |

## 6. Sistemas, activos y terceros involucrados
- Memoria USB (soporte extraíble) — marca, capacidad, cifrado: NO INDICADO.
- Sistema de origen de las planillas (software de planillas / hojas de cálculo) — NO INDICADO.
- Terceros: NO INDICADO (confirmar si interviene un proveedor de planillas o contabilidad externa).

## 7. Medidas ya adoptadas (según el reporte)
- Ninguna indicada (NO INDICADO).

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo (contener / preservar evidencia / informar) | Responsable sugerido |
|---|---|---|---|
| 1 | Registrar por escrito, hoy, la **fecha y hora** en que la persona custodia notó la pérdida, el último lugar y momento en que se vio la USB, y quién la tenía | Informar / fijar el inicio del plazo de 48 h | Quien reporta + ODP |
| 2 | Búsqueda inmediata en los lugares donde estuvo (oficina, vehículo, áreas comunes) y consulta a seguridad/recepción por objetos perdidos; si fue en vía pública o hay indicio de robo, evaluar denuncia policial | Contener / preservar evidencia | Custodio de la USB + seguridad |
| 3 | Confirmar **qué archivos exactos** contenía (a partir de la copia en el sistema de origen), periodos, número de trabajadores y si estaban **cifrados o con contraseña**; no modificar ni borrar los originales | Preservar evidencia / dimensionar | Área de RR. HH. + TI |
| 4 | Si la USB tenía credenciales o contraseñas (p. ej., de banca empresa o del sistema de planillas), **cambiarlas** y revisar con el banco movimientos o cambios de cuentas de abono | Contener | TI + Tesorería |
| 5 | Informar a la alta dirección y no comunicar todavía a los trabajadores hasta que el ODP decida el contenido y momento de la comunicación (art. 34.3) | Informar | ODP |

## 9. Preguntas pendientes
1. **(Crítica)** ¿En qué **fecha y hora** se supo por primera vez de la pérdida, y quién lo supo? — define la hora límite de notificación a la ANPD; el plazo podría estar corriendo ya.
2. ¿La USB estaba **cifrada** o los archivos protegidos con contraseña robusta? ¿Se conoce la clave por terceros?
3. ¿Cuántos trabajadores (y, en su caso, derechohabientes) figuran en las planillas y de qué periodos?
4. ¿Las planillas incluyen datos sensibles (salud, afiliación sindical) o datos de menores?
5. ¿Dónde y cómo se perdió (dentro de las instalaciones, en tránsito, posible robo)?
6. ¿Existe copia de respaldo de la información? (disponibilidad)
7. ¿Quién reporta y quién custodiaba la USB? ¿Es personal propio o de un proveedor (encargado, art. 36)?
8. ¿Estaba autorizado copiar las planillas a un medio extraíble (art. 46.4)?

## 10. Siguiente paso
☐ Cerrar como evento ☒ Pasar a `brecha-evaluacion-severidad` — en cuanto se respondan las preguntas 1 a 4. Mientras tanto, criterio del proyecto: **ante la duda, recomendar notificar**; si las planillas contienen datos sensibles y la USB no estaba cifrada, se cumple el supuesto 3 del art. 34.1 y habría que notificar a la ANPD dentro de las 48 h.

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
