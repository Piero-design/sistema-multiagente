# 00 · Informe del incidente — INC-20261009-fuga-correo-admision

> Escenario simulado (UNSA). Todo es BORRADOR para decisión del ODP y del responsable de seguridad. Nada ha sido notificado ni enviado.

## 1. Estado y reloj

| Ítem | Valor |
|---|---|
| Clasificación | Brecha de datos personales · FUG (fuga accidental) · confidencialidad · P2 con tratamiento urgente |
| Severidad | **MUY ALTA** (SE = 4 × 1 + 0,25 = 4,25) |
| Toma de conocimiento | 2026-10-09 14:20 (alternativa 16:05) |
| **Hora límite 48 h** | **2026-10-11 14:20** |
| Hora actual | 2026-10-13 09:00 |
| **Tiempo restante** | **VENCIDO hace 42 h 40 min** (90 h 40 min transcurridas). Notificar ya, con justificación |

## 2. Resumen ejecutivo
Por un envío con la lista en "Para" en lugar de CCO, 612 ingresantes recibieron un correo con una hoja de datos para el carné: nombres, DNI, fecha de nacimiento, contacto, colegio y condición (discapacidad, dato sensible). Unos 40 son menores. La contención por correo no es fiable y hay amenaza de difusión en prensa. Corresponde notificar a la ANPD (tardíamente), comunicar a los titulares y avisar al CNSD. La causa de fondo es la ausencia de procedimiento de notificación y de responsable.

## 3. Decisiones humanas (por urgencia)
1. **Aprobar y presentar hoy la notificación a la ANPD** con justificación de la demora. El ODP debe completar la fecha real en que recibió el reporte.
2. **Presentar el aviso al CNSD.**
3. **Autorizar la comunicación a los 612 titulares**, y a padres o representantes de menores, con CCO.
4. **Ordenar a la OTI** preservar la evidencia y luego purgar los mensajes de los buzones institucionales.
5. **Aprobar el protocolo de prensa** y el vocero único (Secretaría General y Asesoría Jurídica).
6. Confirmar el supuesto de "gran número" y la lectura de la toma de conocimiento con Asesoría Jurídica `[VERIFICAR lineamientos ANPD]`.
7. Aprobar el plan de mejoras (sección 4 del archivo 04).

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
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación ANPD, titulares y CNSD | Responder | 5.26 | arts. 34.1, 34.3, 34.5 |
| Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28 | art. 35 |
| Mejoras | Aprender lecciones | 6.3, 8.12, 8.15 | arts. 46.3, 46.4, 47 |

ISO/IEC 27701:2019: 6.13.1.1 y 6.13.1.5. `[VERIFICAR edición citada]`

## 6. Información pendiente
- **Crítica:** fecha y hora reales en que el ODP recibió el reporte, y por qué vías pasó (sustenta la demora).
- Traza del correo (cabeceras, entregas, lecturas) y contenido de las respuestas "a todos". No hay logs en el contexto.
- Si el envío salió del correo institucional o de otra cuenta.
- Número exacto de personas con discapacidad y de menores en la hoja.
- Si hay reenvíos o publicación; qué medio de prensa, si lo hay.
- Estado real de cada medida de contención.
- Requisito aplicable para comunicar a padres o representantes de menores `[VERIFICAR]`.
- Lineamientos de la ANPD sobre "gran número" y vigencia del enlace de reporte `[VERIFICAR]`.
