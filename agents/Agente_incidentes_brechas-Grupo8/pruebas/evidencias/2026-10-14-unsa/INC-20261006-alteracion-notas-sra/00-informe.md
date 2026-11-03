# 00 · Informe del incidente — INC-20261006-alteracion-notas-sra

> ESCENARIO SIMULADO (TIF de Auditoría de Sistemas). Todo es BORRADOR para revisión del ODP y del responsable de seguridad. Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| Concepto | Valor |
|---|---|
| Clasificación | Incidente de seguridad de datos personales (brecha). Integridad confirmada, confidencialidad no descartada. ALT + INT + INS |
| Prioridad | P2 Alta |
| Severidad | **Alta** (SE = 3,0) |
| Toma de conocimiento | 2026-10-12 11:20 (puede ser anterior: falta la hora del reclamo del estudiante) |
| **Hora límite 48 h** | **2026-10-14 11:20 (-05:00)** |
| Hora actual (comando) | 2026-10-13 09:00 |
| **Tiempo restante** | **26 h 20 min** |
| Aviso | El entorno marca el 14/10; si esa fuera la fecha real, quedarían menos de 26 h (a las 09:00 del 14/10, 2 h 20 min). Verificar la hora real |

## 2. Resumen ejecutivo
- Entre el 06/10 22:41 y el 07/10 00:41 se usó la cuenta de un docente jubilado en 2024, sin baja, para subir 23 notas de Ingeniería de Sistemas desde la IP 10.20.5.33.
- La cuenta se bloqueó el 12/10 11:20. El log no registra consultas, así que no se sabe si se leyeron otros datos ni si hubo cambios en otras escuelas.
- Es una alteración ilícita de datos personales. Ante la duda sobre "gran número" y "perjuicio evidente", se recomienda notificar a la ANPD y al CNSD y comunicar a los 23 titulares tras validación legal.
- Causas probables: sin baja de cuentas, sin MFA, cuentas compartidas, logs de 60 días y ausencia de procedimiento de notificación.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Aprobar y enviar la notificación a la ANPD antes del 14/10 11:20** (`03-notificacion-anpd.md`). Designar quién la envía, porque el documento de seguridad no lo define.
2. **Aprobar y enviar el aviso al CNSD** en el mismo plazo (`03-aviso-cnsd.md`).
3. **Ordenar hoy la preservación de evidencia:** logs del SRA (retención 60 días), equipo 10.20.5.33 y actas firmadas.
4. **Confirmar la hora real de toma de conocimiento** (reclamo del estudiante, revisión de auditoría). Puede adelantar la hora límite.
5. **Decidir con Asesoría Jurídica la comunicación a los 23 titulares** (`03-comunicacion-titulares.md`): contenido, momento y compatibilidad con la investigación.
6. **Autorizar la ampliación del alcance:** revisar todas las escuelas y las cuentas inactivas o compartidas.
7. **Autorizar la restauración de las notas** y el flujo de aprobación para cambios (con el área académica).
8. **Decidir las vías disciplinaria y legal** (el agente no atribuye responsabilidad; la atribución no está probada).

## 4. Entregables
| Archivo | Contenido |
|---|---|
| [01-ficha-incidente.md](01-ficha-incidente.md) | Triaje, reloj, hechos verificados/reportados/supuestos |
| [02-evaluacion-severidad.md](02-evaluacion-severidad.md) | SE = 3,0 Alta; decisión art. 34 |
| [03-notificacion-anpd.md](03-notificacion-anpd.md) | Borrador art. 34.1/34.2 |
| [03-comunicacion-titulares.md](03-comunicacion-titulares.md) | Borrador art. 34.3 |
| [03-aviso-cnsd.md](03-aviso-cnsd.md) | Borrador art. 34.5 |
| [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md) | Contención, evidencia, causa raíz, mejoras y cierre |

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | ISO/IEC 27701:2019 | D.S. 016-2024-JUS |
|---|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | 6.13.1.5 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | 6.13.1.5 | art. 34.1 |
| Notificación | Responder | 5.26 | 6.13.1.1, 6.13.1.5 | arts. 34.1, 34.3, 34.5 |
| Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28, 8.15 | 6.13.1.5 | arts. 35, 46.1, 46.3, 47 |

## 6. Información pendiente
- Fecha y hora del reclamo del estudiante y de la revisión del log (define el reloj).
- Detalle de las 20 modificaciones resumidas y comparación con actas.
- Perfil de permisos de la cuenta y si pudo leer/exportar datos de otras escuelas.
- Persona que usó el equipo 10.20.5.33 y quién conocía la clave (la cuenta de secretaría es compartida).
- Existencia de menores o datos sensibles entre los afectados.
- Estado del respaldo del 04/10 (restauración nunca probada).
- Vigencia del formulario de reporte y lineamientos de la ANPD sobre "gran volumen" (`[VERIFICAR]`).
- Rango de multa por no notificar (infracción grave, art. 133 num. 12): `[VERIFICAR]` en el art. 39 de la Ley.
