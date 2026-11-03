# Respuesta y cierre — INC-20260930-correo-equivocado-colegio

- **Estado:** ☒ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md`

## 1. Plan de respuesta

### 1.1 Contención
| # | Acción | Plazo | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Enviar un requerimiento **escrito** a la empresa de fotos para que elimine el archivo de la bandeja de entrada, la papelera, las descargas, la nube y los dispositivos; para que declare si lo abrió, reenvió o copió, y para que confirme por escrito con firma del representante | Inmediata (01/10) | Dirección / Oficial de Datos Personales | No. Guardar el requerimiento y la respuesta como evidencia |
| C2 | Pedir a la empresa que firme un **compromiso de confidencialidad** sobre la información recibida | Inmediata | Dirección / asesoría legal | No |
| C3 | Si la plataforma lo permite, intentar recuperar el mensaje y revocar cualquier enlace compartido | Inmediata | TI | Bajo. Antes, exportar el mensaje y su registro (E1, E2) |
| C4 | Hacer seguimiento: si no hay respuesta escrita en 24 h, reiterar el requerimiento por carta notarial `[evaluar con asesoría legal]` | Corto plazo | Dirección / asesoría legal | No |
| C5 | Comunicar a los apoderados (ver `03-comunicacion-titulares.md`) para que puedan protegerse de posibles fraudes | Antes del 02/10, 15:30 | Oficial de Datos Personales | No |
| C6 | Mientras se revisa el procedimiento, suspender temporalmente el envío por correo de archivos con datos de alumnos o pensiones sin protección | Corto plazo | Dirección | No |

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)
| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| E1. Correo enviado (29/09, 17:05) con cabeceras completas y adjunto | Carpeta "Enviados" de la cuenta institucional | Exportar en formato .eml/.msg y copiar a un almacenamiento de solo lectura; **no borrar el original** | SHA-256 del .eml y del adjunto | Responsable de TI |
| E2. Registro de seguimiento de mensajes / logs de la plataforma de correo (envío, destinatario, entrega) | Consola de administración del correo | Exportar antes de que roten; los logs de interacción deben conservarse al menos 2 años (art. 46.3) | SHA-256 del archivo exportado | Responsable de TI |
| E3. Constancia de la llamada a la empresa de fotos (hora, interlocutor, contenido) | Declaración escrita de la secretaria académica | Documento firmado y fechado | Copia escaneada con hash | Oficial de Datos Personales |
| E4. Requerimiento escrito a la empresa y su respuesta | Correo / carta | Exportar y archivar | SHA-256 | Oficial de Datos Personales |
| E5. Reporte interno del incidente (30/09, 16:20) | Reporte de la secretaria | Archivar el original | SHA-256 | Oficial de Datos Personales |

**Registro de cadena de custodia:** por cada evidencia, anotar quién la recolectó, la fecha y hora, dónde se guarda, el hash y cada traspaso (de quién a quién, cuándo y para qué). Formato sugerido: tabla en el expediente del incidente, firmada por el custodio.

### 1.3 Erradicación
- No hay malware ni intrusión que eliminar. La "causa" que se erradica es la copia no autorizada: se da por erradicada cuando llegue la **confirmación escrita** de eliminación del receptor (C1).
- Revisar si la libreta de direcciones o el autocompletado del correo de la secretaria mezcla contactos de proveedores con los de la contadora y, si es así, depurarlo.

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** no aplica. No hubo pérdida de disponibilidad ni de integridad: el colegio conserva el archivo original (inferencia).
- **Verificación de integridad:** confirmar que el archivo original sigue igual en el sistema de origen.
- **Envío correcto a la contadora:** solo con los datos necesarios para su función (pensiones; **sin notas**), por un canal protegido (enlace con acceso restringido o archivo cifrado con la contraseña enviada por otro medio) y verificando el destinatario.
- **Criterio para volver a la operación normal:** confirmación escrita del receptor, comunicación a los titulares enviada y nuevo procedimiento de envío aprobado.

## 2. Análisis de causa raíz (5 porqués)
| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué se expusieron los datos? | Porque el archivo se envió a la empresa de fotos en lugar de a la contadora | Hecho |
| 2. ¿Por qué se envió al destinatario equivocado? | Probablemente por elegir el contacto equivocado (autocompletado o confusión de direcciones) sin verificar antes de enviar | Inferencia |
| 3. ¿Por qué el error no se detectó a tiempo? | Porque no hay ningún control que alerte al enviar adjuntos con datos personales a dominios externos ni que retrase el envío para poder cancelarlo | Inferencia |
| 4. ¿Por qué el error tuvo tanto impacto? | Porque el archivo no estaba protegido y mezclaba en un solo documento notas y deudas de todo el colegio, más de lo que la contadora necesitaba | Hecho (contenido) / inferencia (falta de protección) |
| 5. ¿Por qué se preparó y envió así? | Porque no hay un procedimiento formal de envío de información personal (minimización, cifrado, canal aprobado) ni capacitación al respecto (art. 46.4) | Inferencia (por confirmar con el documento de seguridad, art. 47) |

- **Causa técnica:** correo sin controles de prevención de fuga (alerta ante destinatarios externos, retraso de envío, cifrado de adjuntos).
- **Causa de proceso:** no hay minimización (un mismo archivo con notas y pensiones) ni un procedimiento de envío seguro de datos personales.
- **Causa humana:** error en la selección del destinatario y falta de verificación antes de enviar.

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)
- **Qué funcionó:** el error se detectó en menos de 24 h; la secretaria reportó con rapidez (50 min después de detectarlo) e intentó contener de inmediato.
- **Qué falló:** no había protección del archivo ni minimización de datos; la contención se hizo solo de palabra, sin constancia escrita; no estaba claro a quién reportar.
- **Qué cambiaremos:** aplicar minimización por destinatario, usar canales protegidos, activar controles en el correo, documentar el procedimiento de reporte y capacitar al personal.

## 4. Controles propuestos
| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| 8.12 Prevención de fuga de datos | Alerta y confirmación obligatoria al enviar adjuntos a dominios externos; retraso de envío de 1 o 2 minutos para poder cancelar; detección de patrones de DNI en adjuntos | Técnica | Alta | TI |
| 8.24 Uso de criptografía | Archivos con datos de alumnos o pensiones cifrados o compartidos solo por enlaces con acceso restringido; contraseña enviada por otro canal | Técnica | Alta | TI |
| 5.34 Privacidad y protección de datos personales | Minimización: un archivo por finalidad (contabilidad sin notas; proveedor de fotos solo con lo mínimo y con contrato de encargo) | Proceso | Alta | Oficial de Datos Personales |
| 6.3 Concienciación y formación | Capacitación breve al personal administrativo: verificar el destinatario, clasificar la información, reportar incidentes de inmediato | Humana | Media | Dirección / Oficial de Datos Personales |
| 5.15 Control de acceso | Limitar quién puede exportar listados completos de notas y pensiones | Proceso | Media | TI / Dirección |
| 6.8 Reporte de eventos de seguridad | Procedimiento y canal de reporte de incidentes conocido por todo el personal, con plantilla | Proceso | Media | Oficial de Datos Personales |
| 5.24 Planificación y preparación de la gestión de incidentes | Modelo de requerimiento de eliminación a terceros y de comunicación a familias listos para usar | Proceso | Baja | Oficial de Datos Personales |

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)
| Campo | Valor |
|---|---|
| Descripción | Envío por error, desde una cuenta institucional, de un archivo con datos de alumnos y apoderados a un proveedor de fotografía no autorizado (categoría FUG, confidencialidad) |
| Periodo del incidente | Desde el 29/09/2026, 17:05, hasta la confirmación escrita de eliminación (pendiente) |
| Datos y titulares afectados | 420 alumnos menores (nombre, DNI, grado, notas) y sus apoderados, hasta 420 (nombre, celular, estado y monto de deuda de la pensión) |
| Efectos / consecuencias | Exposición ante un tercero; riesgo de estigmatización, fraude dirigido a apoderados y uso indebido del DNI. Severidad ENISA: 4,25 (Muy alta) |
| Quién reportó y cuándo | Secretaria académica, 30/09/2026, 16:20 (toma de conocimiento: 15:30) |
| Notificación ANPD | Recomendada; borrador listo. Fecha de envío: `[COMPLETAR]` (límite: 02/10/2026, 15:30) |
| Comunicación a titulares | Recomendada; borrador listo. Fecha de envío: `[COMPLETAR]` (límite: 02/10/2026, 15:30) |
| Notificación CNSD | Recomendada (entorno digital); borrador listo. Fecha de envío: `[COMPLETAR]` |
| Medidas adoptadas | Llamada al receptor (30/09). Las demás medidas están propuestas (ver 1.1 y 4) |

## 6. Criterios de cierre
- [ ] Incidente contenido (confirmación escrita de eliminación del receptor)
- [x] Causa erradicada: no aplica en sentido técnico; depende de C1
- [x] Servicios y datos recuperados: no hubo pérdida de disponibilidad
- [ ] Notificaciones realizadas o descartadas con fundamento (ANPD, titulares, CNSD)
- [ ] Acciones correctivas asignadas con fecha
- [ ] Registro del art. 35 completo (faltan fechas de notificación)
- [ ] Notificación complementaria a la ANPD enviada, si corresponde

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
