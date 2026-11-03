# Notificación de incidente de seguridad de datos personales — INC-20260929-ransomware-clinica

**Destinatario:** Autoridad Nacional de Protección de Datos Personales (ANPD), Ministerio de Justicia y Derechos Humanos
**Fundamento:** art. 34 del Reglamento de la Ley N.° 29733 (D.S. N.° 016-2024-JUS)
**Tipo de notificación:** ☒ Inicial ☐ Complementaria ☐ Única. Se presentará una notificación complementaria cuando termine la investigación.
**Canal:** formulario de reporte de incidentes `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR enlace vigente]`

## A. Datos del responsable
- **Titular del banco de datos / responsable del tratamiento:** Clínica San Gabriel S.A.C., Arequipa. RUC: `[COMPLETAR]`
- **Banco(s) de datos afectado(s):** banco de datos de pacientes / historias clínicas. Código de inscripción: `[COMPLETAR]`
- **Encargado del tratamiento involucrado (si aplica):** en investigación (proveedor del sistema de historias clínicas, si lo hubiera) `[COMPLETAR]`

## B. Punto de contacto (art. 34.2 num. 2)
- **Oficial de Datos Personales / contacto:** `[NOMBRE]` — `[CORREO]` — `[TELÉFONO]`

## C. Cronología
- Ocurrencia: entre el 28/09/2026 a las 23:50 (alerta del antivirus por un adjunto malicioso) y el 29/09/2026 a las 07:15 (estimado; en investigación).
- Toma de conocimiento: 29/09/2026, 07:15.
- Notificación: `[FECHA Y HORA DE ENVÍO]` — ☐ Dentro de 48 h (hasta el 01/10/2026 07:15) ☐ Fuera de plazo (ver sección H)

## D. Naturaleza del incidente (art. 34.2 num. 1)
- **Descripción:** ataque de código malicioso de tipo ransomware que cifró el servidor de archivos y la base de datos del sistema de historias clínicas, además de 6 estaciones de trabajo. El atacante dejó un mensaje que exige un pago y amenaza con publicar la base de pacientes. Todo indica que el acceso inicial fue un correo con un adjunto malicioso abierto en un equipo administrativo (en investigación). Aún no se sabe si se extrajeron datos.
- **Tipo:** disponibilidad (confirmada), integridad (confirmada: datos cifrados ilícitamente) y confidencialidad (probable; en investigación).
- **Categorías de datos afectados:** identificación (nombres, DNI, fecha de nacimiento), contacto (teléfono, dirección), **datos de salud (diagnósticos, resultados de laboratorio): datos sensibles**, y datos del seguro de salud.
- **Categorías y número aproximado de titulares:** pacientes de la clínica, aproximadamente **18 000** (estimación preliminar). Se está verificando si hay menores de edad.
- **Entorno digital:** Sí. Se reporta también al CNSD: ☐ Sí (fecha: `[ ]`) — ver borrador `03-aviso-cnsd.md`.

## E. Posibles consecuencias (art. 34.2 num. 3)
- Divulgación pública de información de salud, con daño a la intimidad y riesgo de discriminación.
- Extorsión o intentos de fraude dirigidos a los pacientes.
- Suplantación de identidad, también ante aseguradoras.
- Afectación de la continuidad de la atención de salud por la falta de acceso a las historias clínicas y la posible pérdida de registros recientes.

## F. Medidas adoptadas y propuestas (art. 34.2 num. 4)
| Medida | Estado | Fecha |
|---|---|---|
| Desconexión de la red del servidor afectado | Adoptada | 29/09/2026 |
| Atención de pacientes mediante procedimiento de contingencia en papel | Adoptada | 29/09/2026 |
| Aislamiento de las estaciones afectadas sin apagarlas, para preservar evidencia | Propuesta / en curso `[CONFIRMAR]` | |
| Aislamiento y custodia del disco de respaldo | Propuesta / en curso `[CONFIRMAR]` | |
| Restablecimiento de credenciales y bloqueo del correo malicioso | Propuesta | |
| Preservación de registros (logs) y análisis forense para determinar si hubo extracción | Propuesta | |
| Comunicación a los pacientes afectados con recomendaciones | Propuesta (borrador listo) | |
| Restauración desde un respaldo verificado y refuerzo de los controles (MFA, respaldos fuera de línea, monitoreo de alertas, capacitación contra phishing) | Propuesta | |

## G. Comunicación a los titulares (art. 34.3)
☒ Se comunicará el `[FECHA]` por `[MEDIO: SMS / llamada / carta / aviso en sede y web]` ☐ No corresponde (art. 34.4)

## H. Motivos de la demora (solo si se notifica después de las 48 h)
> Completar solo si el envío ocurre después del 01/10/2026 a las 07:15. El agente no conoce los motivos reales; no inventar.
- `[Exponer los motivos y, si existe, el sustento probatorio (art. 34.1)]`

## I. Información pendiente (para la notificación complementaria)
- Si hubo extracción de datos (análisis de tráfico y logs) y si se publicó alguna muestra.
- Número definitivo de titulares y presencia de menores de edad.
- Contenido del servidor de archivos (otros titulares afectados).
- Estado del respaldo y plazo de recuperación.
- Causa raíz y medidas correctivas definitivas.

## Verificación de contenido mínimo (art. 34.2) — no se envía
| Elemento del art. 34.2 | ¿Incluido? | Sección |
|---|---|---|
| 1. Naturaleza del incidente, tipos de datos y número aproximado de titulares | Sí | D |
| 2. Nombre y contacto del Oficial de Datos Personales / punto de contacto | **Parcial: faltan los datos** `[COMPLETAR]` | B |
| 3. Posibles consecuencias | Sí | E |
| 4. Medidas adoptadas o propuestas | Sí | F |
| Motivos de la demora (art. 34.1, si pasan las 48 h) | Plantilla lista, condicional | H |

## Destinatarios y omisiones
- ANPD: sí (art. 34.1, se cumplen los cuatro supuestos).
- Titulares: sí, en `03-comunicacion-titulares.md` (art. 34.3; no aplica la excepción del 34.4).
- CNSD: sí, en `03-aviso-cnsd.md` (art. 34.5, entorno digital).
- No se omite ningún destinatario.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
