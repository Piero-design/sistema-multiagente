# Informe del incidente — INC-20260929-ransomware-clinica

> Caso ficticio de prueba. Expediente en **borrador**: no se ha notificado ni enviado nada.

## 1. Estado y reloj
| Campo | Valor |
|---|---|
| Clasificación | **Incidente de seguridad de datos personales (brecha)**: `MAL` ransomware con extorsión. Tipo: disponibilidad + integridad (confirmadas) + confidencialidad (probable) |
| Prioridad | **P1 Crítica** |
| Severidad | **SE = 4 × 1 + 1,75 = 5,75 → Muy alta** (sin extracción sería 5,25, igualmente Muy alta) |
| Toma de conocimiento | 2026-09-29 07:15 |
| **Hora límite (48 h, art. 34.1 y 34.3)** | **2026-10-01 07:15** |
| Tiempo restante | El agente no tiene la hora actual. A la fecha del expediente (2026-10-01) quedan **pocas horas como máximo, o el plazo ya está VENCIDO**. Si se envía después de las 07:15, completar la sección H (motivos de la demora) |
| Criterio conservador | Si la toma de conocimiento se fija en la alerta del antivirus (28/09 23:50), el plazo venció el 30/09 a las 23:50 `[VERIFICAR con asesoría legal]` |
| Estado de la respuesta | En contención |

## 2. Resumen ejecutivo
Un ransomware, probablemente introducido por un correo de phishing abierto en facturación, cifró el sistema de historias clínicas de la Clínica San Gabriel y seis PC. Los atacantes exigen 3 BTC y amenazan con publicar la base de ~18 000 pacientes, que incluye datos de salud (sensibles). No se sabe si hubo extracción y el único respaldo, de hace 3 semanas, puede estar comprometido. Se cumplen los cuatro supuestos del art. 34.1: **obligación probable de notificar a la ANPD, comunicar a los pacientes y avisar al CNSD**, todo antes del 01/10/2026 a las 07:15. No se recomienda pagar el rescate.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Aprobar y enviar la notificación inicial a la ANPD** (`03-notificacion-anpd.md`) antes del 01/10/2026 07:15, después de completar el RUC, el código del banco de datos y el contacto del Oficial de Datos Personales. Si ya pasó esa hora, redactar los motivos de la demora (sección H). Responsables: responsable del tratamiento y Oficial de Datos Personales.
2. **Aprobar y enviar el aviso al CNSD** (`03-aviso-cnsd.md`) con los indicadores de compromiso.
3. **Aprobar la comunicación a los ~18 000 pacientes** (`03-comunicacion-titulares.md`): medio, canal de atención y fecha (mismo plazo de 48 h).
4. **Decidir sobre el rescate:** la recomendación es no pagar y no contactar al atacante. La decisión es de la alta dirección, con asesoría legal y especializada.
5. **Autorizar a TI (o contratar un servicio forense externo)** para aislar las PC sin apagarlas, desconectar y custodiar el disco de respaldo y preservar la evidencia antes de restaurar.
6. **Decidir si se presenta denuncia policial** `[VERIFICAR unidad]`.
7. **Fijar el criterio de toma de conocimiento** (07:15 del 29/09 o la alerta de las 23:50 del 28/09) con asesoría legal.

## 4. Entregables
| Archivo | Contenido |
|---|---|
| [01-ficha-incidente.md](01-ficha-incidente.md) | Triaje, línea de tiempo, clasificación, datos afectados y acciones inmediatas |
| [02-evaluacion-severidad.md](02-evaluacion-severidad.md) | Cálculo ENISA y decisión de notificación según el art. 34 |
| [03-notificacion-anpd.md](03-notificacion-anpd.md) | Borrador de la notificación inicial a la ANPD con la verificación del art. 34.2 |
| [03-comunicacion-titulares.md](03-comunicacion-titulares.md) | Borrador del aviso a los pacientes en lenguaje sencillo |
| [03-aviso-cnsd.md](03-aviso-cnsd.md) | Borrador del aviso al CNSD |
| [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md) | Contención, evidencia, erradicación, recuperación, causa raíz, controles y registro del art. 35 |

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1:2023 | ISO/IEC 27002:2022 | ISO/IEC 27701:2019 | D.S. 016-2024-JUS |
|---|---|---|---|---|
| 1. Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | 6.13.1.5 | art. III num. 16; art. 36 (no aplica: el reportante no es encargado) |
| 2. Severidad | Evaluar y decidir | 5.25 | 6.13.1.5 | art. 34.1, 34.3, 34.4, 34.5 |
| 3. Notificación | Responder | 5.26 | 6.13.1.1, 6.13.1.5 | arts. 34.1, 34.2, 34.3, 34.5 |
| 4. Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28, 5.29, 8.13 | 6.13.1.5 (registro) | art. 35; arts. 46.3 y 48.1 (logs y respaldos) |

## 6. Información pendiente
1. **Crítica:** la hora actual frente a la hora límite (01/10/2026 07:15) y si ya se envió alguna notificación.
2. Si hubo extracción de datos (análisis de tráfico saliente y logs).
3. Estado del disco de respaldo y si existen otras copias.
4. Número exacto de titulares, presencia de menores de edad y contenido del servidor de archivos.
5. RUC, código de inscripción del banco de datos y nombre y contacto del Oficial de Datos Personales.
6. Si el sistema de historias clínicas lo opera un proveedor (encargado, art. 36) y si hay accesos remotos de terceros.
7. Hora exacta en que apareció la nota de rescate.
8. Lineamientos de la ANPD sobre "gran volumen" y "gran número" `[VERIFICAR]`; vigencia del enlace del formulario `[VERIFICAR]`; rango de la multa por infracción grave `[VERIFICAR]`.

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad. Nada de este expediente ha sido notificado ni enviado.*
