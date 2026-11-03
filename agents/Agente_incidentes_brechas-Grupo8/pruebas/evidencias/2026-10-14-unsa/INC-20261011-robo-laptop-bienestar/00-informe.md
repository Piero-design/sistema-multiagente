# 00 — Informe del incidente · INC-20261011-robo-laptop-bienestar

> ESCENARIO SIMULADO (TIF UNSA). Todo es BORRADOR para revisión humana. Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| | |
|---|---|
| Clasificación | Brecha de datos personales (FIS: robo físico de laptop) · confidencialidad + disponibilidad · P2 (tratar con urgencia de P1) |
| Severidad | **Muy alta**: SE = 4 × 1 + 1,5 = 5,5 |
| Toma de conocimiento | 2026-10-11 19:30 |
| **Hora límite (48 h)** | **2026-10-13 19:30** |
| Hora actual | 2026-10-13 09:00 |
| **Tiempo restante** | **10 h 30 min** |

## 2. Resumen ejecutivo
Una laptop institucional de una psicóloga de Bienestar fue robada el 2026-10-11 con las fichas de ~150 estudiantes (algunos menores): datos sensibles de salud mental y violencia familiar, sin cifrado y sin respaldo, y con la sesión de correo abierta. Hay datos sensibles y menores, por lo que corresponde notificar a la ANPD (art. 34.1), comunicar a los titulares (art. 34.3) y avisar al CNSD (art. 34.5, ante la duda). Faltan 10 h 30 min. Nadie ha sido notificado todavía y el documento de seguridad no define quién debe hacerlo. Hay que contener ya el acceso al correo.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Ahora:** ordenar a la OTI cerrar sesiones, cambiar claves, activar MFA y bloquear la cuenta.
2. **Hoy a primera hora:** designar quién firma y envía la notificación (el documento de seguridad no lo define).
3. **Antes de las 19:30:** aprobar y enviar la notificación a la ANPD y el aviso al CNSD.
4. **Antes de las 19:30:** aprobar la comunicación a titulares, incluido el canal seguro para víctimas de violencia familiar y los representantes de menores (consultar a Asesoría Jurídica).
5. Confirmar el alcance real del contenido de la laptop (¿solo 150 fichas?).
6. Autorizar la revisión de logs del correo y el borrado remoto, si es posible.
7. Activar apoyo psicológico a los afectados.
8. Si no se llega a las 19:30, preparar la justificación de la demora (art. 34.1).

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
| Severidad | Evaluar y decidir | 5.25 | art. 34.1, 34.4 |
| Notificación | Responder | 5.26, 5.34 | art. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender | 5.26–5.28, 8.13, 8.24 | art. 35 |

ISO/IEC 27701: edición 2019 (6.13.1.1, 6.13.1.5) `[VERIFICAR si se cita la edición 2025]`.

## 6. Información pendiente
- Hora exacta en que se constató el robo `[VERIFICAR]`.
- Contenido exacto de la laptop (150 fichas o más; menores: cantidad).
- ¿Había contraseña de inicio? ¿Existe MDM o borrado remoto?
- Logs de acceso al correo desde el robo (el contexto no trae logs).
- N.º de atestado de la denuncia policial.
- Lineamientos ANPD sobre "gran número" y vigencia del enlace del formulario `[VERIFICAR]`.
- Quién tiene facultad de firmar la notificación.
- Canal seguro para contactar a afectados y a los representantes de menores.
- Existencia de otra copia de las fichas.
