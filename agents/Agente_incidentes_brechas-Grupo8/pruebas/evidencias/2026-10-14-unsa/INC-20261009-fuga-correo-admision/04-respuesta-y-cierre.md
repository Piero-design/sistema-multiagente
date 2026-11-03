# 04 · Plan de respuesta y cierre — INC-20261009-fuga-correo-admision

> BORRADOR. Responsables propuestos por rol; el ODP los confirma. Plazos son propuestas internas, salvo el legal.

## 1. Contención y erradicación (ISO/IEC 27035-3; control 5.26)

| # | Acción | Responsable | Plazo propuesto |
|---|---|---|---|
| 1 | Aprobar y presentar la notificación a la ANPD con justificación de demora | ODP | **Inmediato (hoy)** |
| 2 | Presentar el aviso al CNSD | ODP / OTI | Hoy |
| 3 | Preservar evidencia: mensaje original con cabeceras, adjunto, respuestas "a todos", mensaje de solicitud de eliminación; calcular hash (ISO/IEC 27037, 5.28) | OTI | Hoy, antes de cualquier purga |
| 4 | Purgar el mensaje y las respuestas de los buzones institucionales (tras 3) | OTI | Hoy |
| 5 | Confirmar que el mensaje de eliminación usó CCO; enviar toda comunicación del caso con CCO | Oficina de Admisión | Hoy |
| 6 | Enviar la comunicación a titulares y a padres o representantes de menores | ODP | Hoy, tras aprobar la notificación a ANPD |
| 7 | Recoger confirmaciones de eliminación y reportes de uso indebido | ODP | 7 días |
| 8 | Protocolo de prensa: un solo vocero, texto aprobado por Secretaría General y Asesoría Jurídica | Secretaría General | Hoy |
| 9 | Vigilar menciones en redes y medios; si el archivo aparece publicado, solicitar su retiro | OTI / Comunicaciones | 7 días |
| 10 | Atender a los tres ingresantes molestos con respuesta individual y empática | ODP | 48 h |

## 2. Recuperación
No hay indisponibilidad ni alteración de datos (control 8.13 no aplica). Recuperar la confianza de los titulares mediante atención y seguimiento. Ofrecer canal para consultas y para ejercer derechos.

## 3. Análisis de causa raíz

| Nivel | Causa |
|---|---|
| Inmediata | Destinatarios en "Para" en lugar de CCO, y adjunto con datos sensibles dentro de un correo de bienvenida |
| Contribuyente | Datos para el carné, incluida la condición, en una hoja enviada a todos, sin minimización. Archivos con datos personales circulan por correo y enlaces sin política (`documento-seguridad-extracto.md:7.1`) |
| Contribuyente | El correo permite responder a todos en listas grandes sin bloqueo (por confirmar) |
| De gestión | No hay procedimiento ni plazos de notificación ni responsable (`documento-seguridad-extracto.md:5.3`); la OTI filtra el escalamiento (l. 18); el plan de respuesta carece de roles y plantillas (`plan-respuesta-incidentes.md:3-7`) |
| De gestión | Documento de seguridad con revisión vencida (2026-09) (`documento-seguridad-extracto.md:3`) |

## 4. Lecciones aprendidas y controles propuestos

| Mejora | Control ISO/IEC 27002:2022 | Art. D.S. 016-2024-JUS |
|---|---|---|
| Procedimiento de incidentes con reloj de 48 h, rol de notificador y escalamiento directo al ODP para todo incidente con datos personales | 5.24, 5.26, 6.8 | 34, 35, 36 |
| Capacitación en envío con CCO y manejo de datos sensibles | 6.3 | 46.4 |
| Prevención de fuga de datos: avisos o bloqueo de adjuntos con DNI y datos de salud, límite de "Responder a todos", listas de distribución | 8.12 | 46.4 |
| Minimizar datos: no enviar la condición de discapacidad ni datos del carné a grupos; usar el portal con acceso individual | 5.34 | `[VERIFICAR artículo de minimización]` |
| Política de uso de correo y nube aprobada para archivos con datos personales | 5.34, 8.12 | 46.4 |
| Registros de correo con retención de 2 años | 8.15, 8.16 | 46.3 |
| Actualizar el documento de seguridad y el plan de respuesta | 5.24 | 47 |
| Plantillas de notificación y simulacro anual | 5.24, 5.27 | 34 |

## 5. Documentación del incidente (art. 35; ISO/IEC 27701 6.13.1.5)

| Campo | Registro |
|---|---|
| Descripción | Fuga de confidencialidad por correo masivo con datos de 612 ingresantes |
| Periodo | Envío 2026-10-09 13:50; conocimiento 14:20; contención en curso |
| Consecuencias | Exposición de datos de identificación y de condición de discapacidad; ~40 menores |
| Quién reportó | Secretaria de la Oficina de Admisión, al ODP el 2026-10-09 16:05 |
| A quién se notificó | `[PENDIENTE: ANPD, CNSD, titulares: completar fecha y hora al enviar]` |
| Medidas | Ver sección 1 |

## 6. Criterios de cierre
- Notificación a ANPD y aviso al CNSD presentados, con constancia.
- Comunicación enviada a los 612 titulares y a los representantes de los menores.
- Evidencia preservada y mensajes purgados de los buzones institucionales.
- Confirmaciones de eliminación recogidas o declaradas como no obtenidas.
- Causa raíz aprobada y plan de mejoras con responsables y fechas.
- Sesión de lecciones aprendidas realizada y expediente firmado por el ODP.
