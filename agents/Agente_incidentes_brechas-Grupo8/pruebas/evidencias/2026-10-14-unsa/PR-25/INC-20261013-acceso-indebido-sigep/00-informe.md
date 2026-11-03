# 00 · Informe del incidente — INC-20261013-acceso-indebido-sigep

> ESCENARIO SIMULADO (fines académicos). Todo es BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| Concepto | Valor |
|---|---|
| Clasificación | Brecha de datos personales (incidente de seguridad de datos personales). Categoría INS (uso indebido interno). Confidencialidad. |
| Prioridad | P2 Alta (sube a P1 si se confirma copia de datos) |
| Severidad | **SE = 4,75, Muy alta** (escenario conservador con datos de salud). Si no hay datos de salud: 2,75, Media. |
| Toma de conocimiento | 2026-10-13, mañana (correo de las 10:20) |
| **Hora límite (48 h)** | **2026-10-15 10:20 como máximo** (antes si el hallazgo fue más temprano) |
| Hora actual (dada) | 2026-10-13 11:20 (-05:00) |
| **Tiempo restante** | **47 h como máximo** |
| Aviso sobre fecha | El entorno indica 2026-10-14. Se usó la hora que dio el usuario. Verificar. |

## 2. Resumen ejecutivo
- Una cuenta de secretaría (`secretaria2`) abrió **85 expedientes** completos de posgrado entre el 05 y el 12/10, lo cual consta en el log (`logs/accesos-sigep.log:2-86`). No es su función.
- Los expedientes tienen datos de identificación y contacto, y posiblemente constancias médicas (dato sensible). El número exacto está sin confirmar.
- No hay evidencia de copia o envío, pero tampoco hay certeza: el log tiene anomalías y puede no registrar exportaciones.
- La cuenta sigue activa. Hay que notificar a la ANPD y al CNSD, y se recomienda comunicar a los titulares.
- La causa raíz es un control de acceso que no aplica la política de roles, sin alertas ni procedimiento de notificación.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Ahora: suspender la cuenta `secretaria2` y cerrar sesiones.** La cuenta sigue activa.
2. **Ahora: preservar los registros** (hash, cadena de custodia) y ampliar la retención de 45 días.
3. **Hoy: contar cuántos de los 85 expedientes tienen constancia médica** en SIGEP. Esto confirma el escenario de severidad.
4. **Hoy: designar a quién aprueba y envía las notificaciones.** La política dice que no existe.
5. **Antes del 15/10 10:20: aprobar y enviar la notificación a la ANPD** (art. 34.1), con los datos pendientes completados. Si faltan datos, enviar igual y ampliar después.
6. **Junto con la anterior: aviso al CNSD** (art. 34.5).
7. **Hasta el 15/10 10:20: decidir si se comunica a los 85 titulares** (art. 34.3). Se recomienda comunicar. Si se decide no hacerlo, documentar el motivo.
8. Con Asesoría Jurídica: criterio sobre el inicio del reloj (lectura estricta por la revisión semanal) y la vía de la acción de personal. No actuar contra la persona sin ese criterio.

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md) — triaje, hechos verificados/reportados/supuestos, anomalías del log
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md) — cálculo ENISA y decisión legal
- [03-notificacion-anpd.md](03-notificacion-anpd.md) — borrador con el contenido del art. 34.2
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md) — borrador en dos versiones
- [03-aviso-cnsd.md](03-aviso-cnsd.md) — borrador
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md) — contención, evidencia, causa raíz, mejora y cierre

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16, art. 36 (no aplica, no es encargado) |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación ANPD, titulares y CNSD | Responder | 5.26 | arts. 34.1 a 34.5 |
| Respuesta y evidencia | Responder | 5.26, 5.28, 8.15/8.16 | arts. 35, 46.3 |
| Cierre y lecciones | Aprender lecciones | 5.27 | art. 35 |

Para ISO/IEC 27701 se cita la edición 2019 (6.13.1.1 y 6.13.1.5). `[VERIFICAR edición 2025]`

## 6. Información pendiente
- Hora exacta en que la Escuela tomó conocimiento (define la hora límite real).
- Cuántos de los 85 expedientes contienen constancia médica, y cuántos titulares son docentes y autoridades.
- Si SIGEP registra exportaciones, impresiones y capturas, y si hubo accesos antes del 05/10.
- Explicación de las anomalías del log: consulta antes del login, orden de horas, una sola sesión en 8 días, accesos en sábado y domingo.
- Si la titular de la cuenta es la única que la usaba. Existe su declaración de "curiosidad", pero no consta acta.
- Razón social, RUC y registro del banco de datos de la UNSA para los formularios.
- Responsable de seguridad de la información (nombre y contacto).
- Vigencia del enlace del formulario `[VERIFICAR]`.
- Si ya hay lineamientos de la ANPD sobre "gran número" y "grandes volúmenes" `[VERIFICAR]`.
- Rango de multa por infracción grave `[VERIFICAR]`.
