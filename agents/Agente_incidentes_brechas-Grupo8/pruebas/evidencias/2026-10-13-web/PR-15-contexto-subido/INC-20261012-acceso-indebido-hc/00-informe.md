# 00 · Informe del incidente — INC-20261012-acceso-indebido-hc

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Nada ha sido notificado ni enviado. Caso ficticio.

## 1. Estado y reloj
| Concepto | Valor |
|---|---|
| Clasificación | Brecha de datos personales (incidente de seguridad de datos personales); categoría INS, confidencialidad; prioridad P2 |
| Severidad | **Muy alta** (SE = 4 × 1 + 0,75 = 4,75) |
| Toma de conocimiento | 2026-10-12, antes de las 11:05 `[hora exacta pendiente]` |
| **Hora límite 48 h** | **2026-10-14 11:05 (máximo; el real puede ser anterior)** |
| Hora actual | 2026-10-13 10:00 |
| **Tiempo restante** | **≤ 25 h 05 min** |

## 2. Resumen ejecutivo
Una trabajadora de admisión consultó 47 historias clínicas (8 de psiquiatría) entre el 1 y 10/10 sin necesidad asistencial aparente (log verificado). No hay evidencia de copia o difusión, pero hay datos sensibles y personas con exposición pública. Aplica el art. 34.1 (datos sensibles): **notificación obligatoria a la ANPD**, aviso al CNSD y comunicación recomendada a los 47 titulares. Controles débiles: cuentas compartidas, sin alertas, sin cifrado, logs de 60 días.

## 3. Decisiones humanas (por urgencia)
1. **Hoy:** aprobar, completar y presentar la notificación a la ANPD (antes de las 11:05 del 14/10; mejor hoy). Confirmar la hora exacta de descubrimiento.
2. **Hoy:** ordenar la preservación de logs (retención de 60 días) y el bloqueo de `admision3`.
3. Aprobar el aviso al CNSD (art. 34.5).
4. Decidir la comunicación a los 47 titulares (recomendada) y el canal para los 8 pacientes de psiquiatría y las personas públicas.
5. Autorizar la ampliación de la investigación (accesos previos al 1/10 y otras cuentas).
6. Coordinar con Legal/RR. HH. el proceso disciplinario.
7. Aprobar el plan de mejora de controles.

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md)
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md)
- [03-notificacion-anpd.md](03-notificacion-anpd.md)
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md)
- [03-aviso-cnsd.md](03-aviso-cnsd.md)
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md)

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar | 6.8, 5.25 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación ANPD / titulares / CNSD | Responder | 5.26 | arts. 34.1, 34.3, 34.5 |
| Respuesta y cierre | Responder / Aprender | 5.26–5.28, 5.15, 8.15, 8.16 | arts. 35, 46.1, 46.3 |

## 6. Información pendiente
- Hora exacta de toma de conocimiento en Calidad (define el plazo real).
- RUC, banco de datos y hora de presentación.
- Si `admision3` es una cuenta compartida y quién la usó.
- Registro de admisiones para confirmar los 41 accesos sin justificación; identificación de las HC de personas públicas.
- Accesos anteriores al 1/10; anomalías del log (horas desordenadas, sesión de 10 días, fines de semana).
- Si existen copias, capturas o impresiones; medidas ya ejecutadas.
- Lineamientos de la ANPD sobre "gran número" y vigencia del formulario `[VERIFICAR]`.
- Si el CNSD y la ANPD usan el mismo formulario.
