# Informe del incidente — INC-20261012-phishing-rrhh-bloqueado

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Escenario simulado (UNSA). Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| Concepto | Valor |
|---|---|
| Clasificación | **Evento sin incidente** (FRA, phishing bloqueado), cierre condicionado a verificación |
| Severidad | No aplica (no hay brecha de datos personales; no se ejecutó la evaluación ENISA) |
| Prioridad | P4 Baja |
| Toma de conocimiento | 2026-10-12 08:05 |
| Hora límite de 48 h (referencial) | 2026-10-14 08:05 |
| Hora actual indicada | 2026-10-13 09:00 (-0500) |
| Tiempo restante | 23 h 05 min |

## 2. Resumen ejecutivo
- El 2026-10-12 el filtro de correo detectó un phishing que suplantaba a RR. HH. y apuntaba a unos 900 docentes.
- Según el reporte, el 100 % quedó en cuarentena, nadie abrió el mensaje ni hizo clic, y el dominio está bloqueado. Es un intento bloqueado, no una brecha.
- No hay obligación de notificar a la ANPD ni a los titulares (art. 34), porque no se vulneró la seguridad de datos personales.
- Esas afirmaciones son **reportadas**. El contexto no tiene logs para contrastarlas, así que se piden 4 verificaciones antes de cerrar.
- Si alguna falla, se reclasifica y el reloj de 48 h (límite 2026-10-14 08:05) ya está corriendo.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Hoy, antes del 2026-10-14 08:05:** ordenar a la OTI las verificaciones de logs de la ficha §4 (correo, proxy/DNS, autenticación) y adjuntar la evidencia. Si todas están limpias, confirmar el cierre como evento. Si alguna muestra clic o acceso anómalo, reclasificar y reiniciar el flujo de brecha (severidad y notificación). Ante la duda, notificar.
2. Aprobar el aviso de concienciación a los docentes.
3. Decidir si registrar el evento en el registro interno (art. 35 / ISO/IEC 27701 6.13.1.5). Se recomienda hacerlo.
4. Si se desea, compartir el indicador (dominio) con el CNSD. No es obligatorio porque no hay incidente `[VERIFICAR]`.

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md)
- No generados por no ser aplicables: 02-evaluacion-severidad, 03-notificacion-anpd, 03-comunicacion-titulares, 03-aviso-cnsd y 04-respuesta-y-cierre.

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16 (definición): no se cumple |
| Verificación de logs | Evaluar y decidir | 8.15, 8.16 | art. 46.3 (logs) |
| Conservación de evidencia | Responder | 5.28 | — |
| Concienciación | Aprender lecciones | 6.3, 8.7, 8.23 | — |
| Registro del evento | Aprender lecciones | 5.27 | art. 35 (documentar) |
| Notificación | Responder | 5.26 | art. 34: no se activa ningún supuesto |

## 6. Información pendiente
- Evidencia de logs: cuarentena, proxy/DNS y autenticación (el contexto no la incluye).
- Fecha y hora actual: la indicada por el usuario es 2026-10-13 09:00. El entorno marca 2026-10-14. Si fuera 14/10, el plazo referencial vence ese mismo día a las 08:05, así que conviene confirmarla.
- Si hubo destinatarios fuera de la red institucional o en dispositivos móviles.
- Si el plan de respuesta vigente (3 pasos, sin roles ni plazos) se actualizará. Es una mejora a medio plazo, fuera de este evento.
