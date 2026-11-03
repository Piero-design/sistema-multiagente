# Informe del evento — INC-20260930-phishing-bloqueado

> Caso ficticio de prueba (caso de control). Informe breve de registro y cierre de un **evento sin incidente**, según el flujo del agente. No se generan los archivos 02, 03 ni 04 porque no hay incidente que evaluar, notificar ni responder.

## 1. Estado y reloj
| Campo | Valor |
|---|---|
| Clasificación | **Evento sin incidente** (FRA, intento de phishing bloqueado) |
| Severidad (ENISA) | **No aplica**: no se afectaron datos personales |
| Prioridad | P4 Baja |
| Toma de conocimiento | 2026-09-30 11:45 (reporte a soporte) |
| Hora límite de 48 h (art. 34.1) | **No aplica**: no hay incidente de seguridad de datos personales. Solo como referencia, si el caso se reabriera con esta misma toma de conocimiento, sería el 2026-10-02 11:45 |
| Estado | Propuesto para cierre, sujeto a dos verificaciones (sección 3) |

## 2. Resumen ejecutivo
Una asistente de Rentas recibió un correo que suplantaba a un banco, no hizo clic y lo reportó. Según soporte, el filtro ya lo había marcado y el proxy no registra accesos al dominio. Soporte bloqueó el dominio y retiró el correo de 37 buzones. No hubo vulneración de controles ni afectación de datos personales (art. III num. 16), así que no existen obligaciones de notificar a la ANPD, a los titulares ni al CNSD. Se recomienda registrar el evento y cerrarlo una vez confirmado que nadie respondió al correo ni accedió desde fuera del proxy.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Confirmar o descartar el compromiso fuera del proxy** (TI, hoy): revisar las respuestas enviadas al remitente, los inicios de sesión anómalos de las 37 cuentas y los accesos al dominio desde móviles o redes externas. Si aparece alguno, **reabrir** como incidente INT/FRA y reiniciar el reloj de 48 h desde esa toma de conocimiento.
2. **Aprobar el cierre como evento** (responsable de seguridad y Oficial de Datos Personales), una vez cumplido el punto 1.
3. **Decidir si se ajusta el filtro de correo** para que ponga en cuarentena (y no solo marque) los mensajes que detecta como phishing (controles 8.7 y 8.23 `[VERIFICAR]`; ver sección 7).
4. **Aprobar el aviso de concienciación** al personal y el reconocimiento a la reportante (control 6.3).

## 4. Entregables
| Archivo | Contenido |
|---|---|
| [01-ficha-incidente.md](01-ficha-incidente.md) | Ficha de triaje: línea de tiempo, decisión "evento sin incidente", clasificación y acciones sugeridas |
| [00-informe.md](00-informe.md) | Este informe breve de registro y cierre |
| 02 / 03 / 04 | **No generados**: según el flujo, un evento sin incidente no pasa a severidad, notificación ni respuesta formal |

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1:2023 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Reporte de la asistente a soporte | Detectar y reportar | 6.8 (reporte de eventos) | — |
| Triaje: evento sin incidente | Evaluar y decidir | 5.25 | art. III num. 16 (no se configura el incidente) |
| Decisión de no notificar | Evaluar y decidir | 5.25 | art. 34.1, 34.3 y 34.5: no se activan (presuponen un incidente de seguridad de datos personales) |
| Registro del evento | Detectar y reportar (registro) | 5.25, 8.15 | art. 35: obliga a documentar los **incidentes**. Aquí se documenta por buena práctica (inferencia: no es obligación legal estricta para un evento) |
| Lección aprendida (filtro y concienciación) | Aprender lecciones | 5.27, 6.3, 8.7 | art. 48.2 (referencia NTP-ISO/IEC 27001:2022) |

## 6. Registro y cierre del evento
- **Hechos:** se recibió un correo de phishing que suplantaba a un banco en 37 buzones; fue reportado y no se usó.
- **Efectos:** ninguno confirmado sobre la confidencialidad, integridad o disponibilidad de la información ni sobre datos personales.
- **Medidas:** dominio bloqueado, correo eliminado de los 37 buzones, revisión del proxy.
- **Notificaciones:** ninguna. Se descartan con fundamento en el art. III num. 16 y el art. 34. No se ha enviado nada.
- **Criterios de cierre:** ☒ contenido ☒ causa neutralizada (dominio bloqueado) ☐ verificación de respuestas al correo e inicios de sesión ☐ verificación de accesos fuera del proxy ☐ aprobación del responsable de seguridad.

## 7. Lecciones aprendidas (propuesta)
- **Qué funcionó:** la persona reconoció el phishing y lo reportó gracias a la capacitación (6.3, 6.8). Soporte respondió en 25 minutos y usó el proxy como evidencia (8.15, 8.16).
- **Qué mejorar:** el filtro detectó el correo pero lo entregó en 37 buzones. Se propone cuarentena automática para el phishing detectado (8.7, protección contra malware; `[VERIFICAR]` 8.23 filtrado web no figura en `knowledge/`). También se recomienda reforzar MFA en las cuentas institucionales (8.5) como defensa si alguna vez se entregan credenciales.

## 8. Información pendiente
1. Hora de llegada del correo y hora en que lo marcó el filtro.
2. Si algún destinatario respondió al correo o accedió al enlace fuera del proxy.
3. Inicios de sesión anómalos en las 37 cuentas.
4. Configuración del filtro (solo marca o pone en cuarentena).

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
