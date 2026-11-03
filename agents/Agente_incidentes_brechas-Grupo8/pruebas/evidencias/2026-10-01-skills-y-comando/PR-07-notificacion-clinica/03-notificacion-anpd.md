# Notificación de incidente de seguridad de datos personales — INC-20260929-ransomware-clinica

**Destinatario:** Autoridad Nacional de Protección de Datos Personales (ANPD) — Ministerio de Justicia y Derechos Humanos
**Fundamento:** art. 34 del Reglamento de la Ley N.° 29733 (D.S. N.° 016-2024-JUS)
**Tipo de notificación:** ☒ Inicial ☐ Complementaria ☐ Única — se presentará una **notificación complementaria** con la información pendiente de la sección I.
**Canal:** formulario de reporte de incidentes `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace]`

> Caso ficticio de prueba. Insumos: `01-ficha-incidente.md` y `02-evaluacion-severidad.md`. No contiene datos personales de pacientes: solo categorías y cantidades.

## A. Datos del responsable
- **Titular del banco de datos / responsable del tratamiento:** Clínica San Gabriel S.A.C. (Arequipa) — RUC: `[COMPLETAR: no indicado]`
- **Banco(s) de datos afectado(s):** banco de datos de pacientes / historias clínicas — código de inscripción: `[COMPLETAR: no indicado]`. Además, contenido del servidor de archivos (en inventario; podría incluir datos de personal o proveedores).
- **Encargado del tratamiento involucrado (si aplica):** en investigación. Se está verificando si el sistema de historias clínicas es operado por un proveedor externo. El incidente fue detectado y reportado por personal propio de la clínica (Jefe de TI).

## B. Punto de contacto (art. 34.2 num. 2)
- **Oficial de Datos Personales / contacto:** `[COMPLETAR: nombre]` — `[COMPLETAR: correo institucional]` — `[COMPLETAR: teléfono]`
  > El nombre y los datos de contacto del Oficial de Datos Personales no constan en los insumos. Es un elemento obligatorio del art. 34.2: **no enviar** sin completarlo.

## C. Cronología
- **Ocurrencia:** entre el 2026-09-28 23:50 y el 2026-09-29 07:15 (estimado). A las 23:50 del 28/09 el antivirus alertó sobre un adjunto malicioso abierto en una PC de facturación; la alerta no fue revisada.
- **Toma de conocimiento:** 2026-09-29 07:15 (el personal de admisión encuentra el sistema inaccesible y la nota de rescate).
- **Reporte interno al Oficial de Datos Personales:** 2026-09-29 08:40.
- **Hora límite (48 h, art. 34.1):** 2026-10-01 07:15.
- **Notificación:** `[COMPLETAR: fecha y hora de envío]` — ☐ Dentro de 48 h ☐ Fuera de plazo (ver sección H)
  > Si se envía después del 2026-10-01 07:15, marcar "Fuera de plazo" y completar la sección H. Criterio conservador `[VERIFICAR con asesoría legal]`: si se tomara como conocimiento la alerta del antivirus (2026-09-28 23:50), el plazo habría vencido el 2026-09-30 23:50.

## D. Naturaleza del incidente (art. 34.2 num. 1)
- **Descripción:** ataque de código malicioso de tipo *ransomware*. El 2026-09-29 se encontraron cifrados (extensión `.lck`) el servidor de base de datos del sistema de historias clínicas y el servidor de archivos, y seis computadoras mostraban una nota de rescate que exige un pago en criptomonedas en 72 horas y amenaza con publicar "la base de pacientes" en Internet. El acceso inicial probable fue un correo de suplantación ("factura pendiente") con un adjunto malicioso abierto en una PC de facturación (inferencia, en investigación). Se desconoce, a la fecha, si hubo extracción de datos antes del cifrado; por precaución se trata como probable.
- **Tipo:** ☒ Disponibilidad (confirmada: sistema de historias clínicas inaccesible) ☒ Integridad (datos cifrados ilícitamente por un tercero) ☒ Confidencialidad (probable, no confirmada: amenaza de publicación)
- **Categorías de datos afectados:**
  - Identificación: nombres, DNI, fecha de nacimiento.
  - Contacto: teléfono, dirección.
  - **Datos sensibles de salud:** diagnósticos y resultados de laboratorio.
  - Datos del seguro de salud (contenido exacto en verificación).
  - Contenido del servidor de archivos: en inventario.
- **Categorías y número aproximado de titulares:** pacientes de la clínica, **aproximadamente 18 000** (estimación del área de TI). Es probable que incluya menores de edad (en verificación). Podrían verse afectados también titulares de pólizas, personal o proveedores (en investigación).
- **Severidad estimada:** Muy alta (metodología ENISA, SE = 5,75; se mantiene Muy alta aunque se descarte la extracción).
- **Entorno digital:** Sí — reportado también al CNSD: Sí (art. 34.5; ver aviso separado `03-aviso-cnsd.md`).

## E. Posibles consecuencias (art. 34.2 num. 3)
- Exposición pública de diagnósticos y resultados de laboratorio, con daño a la intimidad y posible estigma, si el atacante cumple su amenaza.
- Discriminación (laboral, de seguros o social) por la condición de salud vinculada a la identidad.
- Intentos de extorsión directa a pacientes, dado que el atacante podría contar con teléfono y dirección.
- Suplantación de identidad y fraude, incluido el uso indebido del seguro.
- Llamadas, mensajes o correos fraudulentos que se hagan pasar por la clínica.
- Afectación de la atención de salud: historias clínicas no disponibles, atención en papel, riesgo de demoras o errores por falta de antecedentes y posible pérdida de registros de hasta 3 semanas si el respaldo no es recuperable.

## F. Medidas adoptadas y propuestas (art. 34.2 num. 4)
| Medida | Estado (adoptada/propuesta) | Fecha |
|---|---|---|
| Desconexión de la red del servidor afectado | Adoptada | 2026-09-29 |
| Plan de contingencia: continuidad de la atención de pacientes en papel | Adoptada | 2026-09-29 |
| Conservación de las PC afectadas encendidas para preservar evidencia en memoria | Adoptada | 2026-09-29 |
| Aislamiento de red de las 6 PC y de todo equipo con archivos cifrados o nota de rescate, sin apagarlas ni formatearlas hasta capturar la memoria | Propuesta | `[COMPLETAR]` |
| Desconexión física y custodia del disco de respaldo para preservarlo si aún está íntegro | Propuesta | `[COMPLETAR]` |
| Restablecimiento de contraseñas de cuentas privilegiadas y de la cuenta de facturación; bloqueo del remitente del correo malicioso y búsqueda en los demás buzones | Propuesta | `[COMPLETAR]` |
| Preservación de registros (antivirus, correo, servidores, sistema de historias clínicas, firewall) conforme al art. 46.3, y análisis del tráfico saliente para determinar si hubo extracción | Propuesta | `[COMPLETAR]` |
| Monitoreo de sitios de publicación de filtraciones para detectar si se publican los datos | Propuesta | `[COMPLETAR]` |
| Comunicación a los pacientes afectados con recomendaciones de protección (art. 34.3) | Propuesta | Hasta 2026-10-01 07:15 |
| Notificación al Centro Nacional de Seguridad Digital (art. 34.5) | Propuesta | Junto con esta notificación |
| Recuperación de sistemas desde respaldo verificado y limpio, tras erradicar el código malicioso | Propuesta | `[COMPLETAR]` |
| Revisión del proceso de atención de alertas del antivirus y concientización sobre correos fraudulentos | Propuesta | `[COMPLETAR]` |

La organización no ha pagado el rescate ni ha establecido contacto con el atacante; cualquier decisión al respecto corresponde a la alta dirección con asesoría especializada.

## G. Comunicación a los titulares (art. 34.3)
☒ Se comunicará el `[COMPLETAR: fecha, dentro del plazo de 48 h]` por `[COMPLETAR: correo electrónico / SMS / carta y aviso en la web y en admisión]` ☐ No corresponde (art. 34.4)
No aplica la excepción del art. 34.4: el incidente afecta derechos de los titulares y no ha sido superado. Borrador en `03-comunicacion-titulares.md`.

## H. Motivos de la demora (solo si se notifica después de 48 h)
> Completar solo si el envío ocurre después del 2026-10-01 07:15. Describir hechos verificables y adjuntar sustento probatorio (art. 34.1).
- `[COMPLETAR: motivos, p. ej., priorización de la contención y de la continuidad asistencial, necesidad de dimensionar el alcance; con sustento]`

## I. Información pendiente (para notificación complementaria)
- Confirmación de si hubo extracción de datos (análisis de tráfico saliente, logs de firewall y proxy, posible publicación de una muestra por el atacante).
- Estado del disco de respaldo (cifrado o íntegro) y existencia de otras copias.
- Número exacto de titulares afectados y si incluye menores de edad.
- Contenido exacto de los "datos del seguro" y del servidor de archivos (otros titulares: personal, proveedores).
- Si el sistema de historias clínicas es operado por un encargado del tratamiento y si existe acceso remoto de terceros.
- Hora exacta de aparición de la nota de rescate.
- Causa raíz confirmada y fecha de restablecimiento de los servicios.
- RUC, código de inscripción del banco de datos y datos del Oficial de Datos Personales (si no se completan en esta notificación inicial).

## Verificación de contenido mínimo (art. 34.2) — uso interno, no se envía
| # | Elemento del art. 34.2 | ¿Incluido? | Sección |
|---|---|---|---|
| 1 | Naturaleza del incidente, tipos de datos y número aproximado de titulares | Sí | D (y C para la cronología) |
| 2 | Nombre y contacto del Oficial de Datos Personales u otro punto de contacto | **Parcial: estructura incluida, datos por completar** (no constan en los insumos) | B |
| 3 | Posibles consecuencias | Sí | E |
| 4 | Medidas adoptadas o propuestas para remediar y mitigar | Sí | F |

Otros controles: plazo de 48 h (C, con sección H lista si se vence); comunicación a titulares (G); aviso al CNSD (D, art. 34.5); pendientes para la complementaria (I).

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
