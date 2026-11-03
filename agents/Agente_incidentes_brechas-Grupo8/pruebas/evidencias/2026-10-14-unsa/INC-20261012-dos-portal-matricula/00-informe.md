# 00 · Informe del incidente — INC-20261012-dos-portal-matricula

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Escenario simulado (UNSA). Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| Dato | Valor |
|---|---|
| Clasificación | Incidente de seguridad de la información (DIS/DoS, disponibilidad). **Brecha de datos personales no confirmada** |
| Prioridad | P3 (sube a P2 si hay indicios de acceso) |
| Severidad (precautoria, ENISA) | **Media**, SE = 2 × 1 + 0,75 = 2,75 |
| Hora de toma de conocimiento | 2026-10-12 09:10 (más temprana); correo: 14:00 |
| **Hora límite 48 h** | **2026-10-14 09:10** (referencia: 14:00) |
| Hora actual indicada | 2026-10-13 09:00 |
| **Tiempo restante** | **24 h 10 min** |

Advertencia: el entorno también indica la fecha 2026-10-14. Si esa fuera la fecha real, el plazo estaría por vencer o vencido. **Confirmar la hora actual**.

## 2. Resumen ejecutivo
- El 12/10, entre 09:10 y 11:40, un DoS dejó fuera el portal de matrícula (S-08); ~1 200 estudiantes se vieron afectados en su servicio.
- Según Soporte, no hubo acceso, modificación ni exportación de datos. Esa afirmación **no se puede verificar**: el contexto no tiene logs.
- Sobre lo reportado, no hay obligación de notificar a la ANPD ni a los titulares; se documenta (art. 35).
- La decisión depende de revisar los logs antes de la hora límite. Sin verificación, se recomienda notificar por precaución.
- Hay brechas de control: S-08 sin respaldo ni cifrado, sin guardia y con un plan de respuesta sin roles ni plazos.

## 3. Decisiones humanas (en orden de urgencia)
1. **Hoy:** ordenar a la OTI revisar y preservar los logs de S-08, la BD, el firewall y NetAndes (08:00–14:00 del 12/10 y posteriores) para confirmar la ausencia de acceso o exfiltración.
2. **Antes del 14/10 09:10:** decidir con el resultado: (a) sin indicios → aprobar el registro del art. 35 y no notificar; (b) indicios o sin poder verificar → aprobar notificación a la ANPD (art. 34.1/34.2) y pedir los borradores (03). Con datos de menores, valorar comunicar a titulares.
3. Consultar con Asesoría Jurídica si el DoS debe reportarse al CNSD (D.U. 007-2020) `[VERIFICAR]`.
4. Confirmar la hora actual real y el criterio de toma de conocimiento (09:10 frente a 14:00).
5. Aprobar el plan de acción y designar quién notifica a la ANPD (hoy no está definido).

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md)
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md)
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md)
- No se generaron 03-notificacion-anpd / comunicación a titulares / aviso CNSD porque no hay obligación confirmada.

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035 | ISO/IEC 27002:2022 | Art. D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar | 6.8, 5.25 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación (condicional) | Responder | 5.26 | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender | 5.26–5.29, 8.13, 8.15 | art. 35 (y 46.3, 48.1) |

## 6. Información pendiente
- Logs de S-08 y la BD, y confirmación de que no hubo exfiltración.
- Qué datos guarda exactamente el portal (¿incluye datos sensibles o de menores?).
- Informe técnico de NetAndes.
- Hora actual real; hora exacta en que Soporte supo del ataque.
- Integridad de las matrículas hechas durante y después de la caída.
- Lineamientos de la ANPD sobre "gran número" `[VERIFICAR]`; obligación hacia el CNSD `[VERIFICAR]`.
