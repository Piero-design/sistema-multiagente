# Respuesta y cierre — INC-20260930-correo-equivocado-colegio

- **Estado:** ☑ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md`
- **Fecha/hora:** 2026-10-01 23:25 (-05:00). Hora límite de notificación: **2026-10-02 15:30**.

## 1. Plan de respuesta

### 1.1 Contención
| # | Acción | Plazo | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Requerimiento **escrito** a la empresa de fotos: no abrir, no usar ni reenviar; eliminar el correo y el adjunto de bandeja, papelera, descargas, equipos, nube y respaldos; responder por escrito con quién lo recibió, si se abrió o reenvió y la fecha de eliminación. Si se reenvió, pedir que identifique a los destinatarios y que se repita el pedido de eliminación con ellos | Inmediata (primera hora 2026-10-02) | Dirección / Oficial de Datos Personales | No, siempre que el colegio conserve su copia del envío (ver 1.2) |
| C2 | Intentar retirar o revocar el mensaje si la plataforma lo permite, dejando registro (poco eficaz con dominios externos) | Inmediata | TI | Bajo: registrar antes el estado del mensaje |
| C3 | Si la empresa de fotos tiene relación contractual con el colegio, invocar las cláusulas de confidencialidad y pedir una declaración firmada de eliminación | Corto plazo | Dirección / asesoría legal | No |
| C4 | Enviar a la contadora solo los datos de pensiones que necesita, con el destinatario verificado y el archivo protegido con contraseña enviada por otro canal | Corto plazo | Secretaria académica | No |
| C5 | Vigilar si llegan a los apoderados reportes de falsas cobranzas y canalizarlos a un único punto de contacto | Corto plazo (2–4 semanas) | Secretaría / Oficial de Datos Personales | No |

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)
| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| Correo enviado con cabeceras completas y adjunto | Carpeta "Enviados" de la cuenta institucional | Exportar en formato .eml, **sin borrarlo** de la cuenta; guardar copia en almacenamiento de solo lectura con acceso restringido | Calcular hash (p. ej. SHA-256) de la copia exportada y anotarlo | Responsable de seguridad / TI |
| Registro de seguimiento del mensaje (hora, remitente, destinatario, entrega) | Servidor / consola de la plataforma de correo | Exportar antes de que el registro rote (art. 46.3: conservación mínima de 2 años) | Hash del archivo exportado | TI |
| Constancia de detección | Mensaje o declaración de la contadora con la hora (15:30 del 30/09) | Copia o declaración escrita fechada | — | Oficial de Datos Personales |
| Constancia de la llamada al receptor | Declaración escrita de la secretaria (hora, interlocutor, lo dicho) | Documento firmado y fechado | — | Oficial de Datos Personales |
| Requerimiento y confirmación escrita del receptor | Correo o carta | Conservar con cabeceras / original firmado | Hash si es digital | Oficial de Datos Personales |
| Versión del archivo enviado | Fuente original del colegio | Conservar la versión tal como se envió (no editarla) | Hash | Responsable de seguridad |

**Registro de cadena de custodia:** para cada ítem anotar quién lo recolectó, fecha y hora, ubicación, hash y cada traspaso (de quién a quién, cuándo y por qué). El archivo contiene datos de menores: la copia de evidencia se guarda cifrada y con acceso limitado.

### 1.3 Erradicación
- No hay malware ni cuenta comprometida que erradicar: la causa es el error de destinatario.
- Eliminar la causa en el proceso (inferencia, a confirmar): revisar si el autocompletado de direcciones contribuyó al error y depurar los contactos sugeridos de la cuenta; establecer que los archivos con datos de alumnos y pensiones no se envíen como adjunto abierto.
- Retirar la exposición: obtener la confirmación escrita de eliminación (C1).

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** no aplica; no hubo pérdida de integridad ni de disponibilidad (el colegio conserva el original).
- **Verificación de integridad:** confirmar que el archivo original no fue modificado (hash de 1.2).
- **Criterio para volver a operación normal:** confirmación escrita de eliminación recibida; envío correcto a la contadora; medidas de verificación de destinatarios y de protección de adjuntos en uso por la secretaría.

## 2. Análisis de causa raíz (5 porqués)
| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué el archivo llegó a la empresa de fotos? | Se envió por correo a la dirección equivocada | Hecho |
| 2. ¿Por qué se eligió la dirección equivocada? | Posible selección errónea por autocompletado o contactos similares en la libreta de direcciones | Inferencia |
| 3. ¿Por qué no se detectó antes de enviar? | No hay verificación ni alerta para envíos a dominios externos con datos personales | Inferencia |
| 4. ¿Por qué el archivo expuso tantos datos? | Un único archivo combinaba notas y pensiones de todo el colegio, sin protección | Hecho (contenido) / inferencia (sin protección) |
| 5. ¿Por qué se preparó así? | No hay una regla de minimización ni de envío seguro de información con datos de alumnos y familias | Inferencia |

- **Causa técnica:** sin control de prevención de fuga ni advertencia en envíos externos; adjunto sin cifrar (inferencia).
- **Causa de proceso:** falta de procedimiento para transferir información personal a terceros y de minimización (enviar solo lo necesario).
- **Causa humana:** error de selección del destinatario; además, el error tardó unas 22 h y 25 min en detectarse (de 17:05 del 29/09 a 15:30 del 30/09).

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)
- **Qué funcionó:** la secretaria reportó el hecho por escrito 50 minutos después de advertirlo y contactó al receptor.
- **Qué falló:** no hubo verificación previa al envío; el archivo no estaba minimizado ni protegido; el pedido al receptor fue solo verbal, sin constancia; el reporte no indica que se haya escalado a tiempo al Oficial de Datos Personales (PENDIENTE: lo actuado entre 2026-09-30 16:20 y 2026-10-01 23:25).
- **Qué cambiaremos:** procedimiento de envío seguro y minimizado; requerimientos de eliminación siempre por escrito; escalamiento inmediato al Oficial de Datos Personales con el reloj de 48 h a la vista.

## 4. Controles propuestos
| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| 8.12 Prevención de fuga de datos | Alerta o retención antes de enviar a dominios externos correos con adjuntos que contengan DNI o datos de alumnos; desactivar o depurar el autocompletado para cuentas administrativas | Envío a destinatario equivocado sin verificación | Alta | TI |
| 8.24 Uso de criptografía | Adjuntos con datos personales protegidos con contraseña o cifrado, con la clave enviada por canal separado | Exposición directa si el envío se equivoca | Alta | TI / secretaría |
| 5.34 Privacidad y protección de datos personales | Regla de minimización: enviar a cada destinatario solo los datos que necesita (p. ej., a la contadora, solo pensiones y no notas) | Archivo que mezclaba datos innecesarios | Alta | Oficial de Datos Personales |
| 6.3 Concienciación y formación | Capacitación breve a personal administrativo: verificación de destinatarios, qué hacer ante un envío equivocado, reporte inmediato | Error humano y respuesta solo verbal | Media | Oficial de Datos Personales / RR. HH. |
| 5.24 / 5.26 Planificación y respuesta a incidentes | Procedimiento con modelo de requerimiento de eliminación y escalamiento inmediato al Oficial de Datos Personales | Contención sin constancia escrita; riesgo con el plazo de 48 h | Media | Responsable de seguridad |
| 5.15 Control de acceso | Restringir quién puede generar o exportar archivos que combinan notas y deuda | Concentración de datos en un solo archivo | Media | TI / dirección |
| Transferencia de información `[VERIFICAR número de control en ISO/IEC 27002:2022; no figura en knowledge/]` | Acuerdos y reglas para intercambiar información con proveedores (fotos, contadora); art. 46.4 del reglamento: canales aprobados formalmente | Envío a terceros sin reglas | Media | Dirección / asesoría legal |

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)
| Campo | Valor |
|---|---|
| Descripción | Envío por error de `notas_y_pensiones_2026.xlsx` desde una cuenta institucional a una empresa de fotos de promoción en lugar de a la contadora. Categoría FUG; confidencialidad. |
| Periodo del incidente | Desde 2026-09-29 17:05 (envío); detectado el 2026-09-30 15:30; exposición vigente hasta que se confirme la eliminación (PENDIENTE). |
| Datos y titulares afectados | 420 alumnos menores (nombres, DNI, grado, notas) y hasta 420 apoderados (nombre, celular, situación de pago y monto adeudado). |
| Efectos / consecuencias | Severidad Muy alta (SE = 4,25). Riesgos: afectación de la intimidad, estigmatización de menores, falsas cobranzas a apoderados. Sin evidencia de uso a la fecha. |
| Quién reportó y cuándo | Secretaria académica, 2026-09-30 16:20. |
| Notificación ANPD | Obligación probable. Borrador listo (`03-notificacion-anpd.md`). **PENDIENTE: aprobación y envío antes de 2026-10-02 15:30.** No consta como enviada. |
| Comunicación a titulares | Obligación probable (no aplica la excepción del art. 34.4). Borrador listo (`03-comunicacion-titulares.md`). **PENDIENTE: aprobación y envío.** |
| Notificación CNSD | Corresponde (entorno digital, art. 34.5). Borrador listo (`03-aviso-cnsd.md`). **PENDIENTE.** |
| Medidas adoptadas | Llamada telefónica al receptor (sin constancia). Las demás medidas están propuestas (secciones 1 y 4). |

## 6. Criterios de cierre
- [ ] Incidente contenido (confirmación escrita de eliminación por el receptor)
- [x] Causa erradicada: no aplica en lo técnico; las medidas de proceso quedan en la sección 4
- [x] Servicios y datos recuperados: no hubo pérdida de disponibilidad
- [ ] Notificaciones realizadas o descartadas con fundamento (ANPD, titulares, CNSD)
- [ ] Acciones correctivas asignadas con fecha
- [ ] Registro del art. 35 completo (faltan las fechas de notificación y de confirmación)

**No procede el cierre.** El incidente sigue en contención.

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
