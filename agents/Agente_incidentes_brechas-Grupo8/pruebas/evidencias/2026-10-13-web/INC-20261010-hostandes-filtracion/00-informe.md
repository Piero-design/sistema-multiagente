# 00 · Informe del incidente — INC-20261010-hostandes-filtracion

> Todo es BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| | |
|---|---|
| Clasificación | Incidente de seguridad de datos personales (brecha probable de confidencialidad). Categoría PRV + INT. Prioridad P2 |
| Severidad | **ALTA** (SE = 2 × 1 + 1,0 = 3,0) |
| Toma de conocimiento | 2026-10-12 15:50 (-05:00) |
| **Hora límite 48 h** | **2026-10-14 15:50 (-05:00)** |
| Hora actual | 2026-10-13 10:00 |
| **Tiempo restante** | **29 h 50 min** |

## 2. Resumen ejecutivo
El proveedor HostAndes (encargado) informó el 12/10 que el 10/10 hubo acceso no autorizado a un servidor compartido y que la base de datos de la Academia podría haberse descargado. Son ~2 400 alumnos, muchos menores, con DNI, fecha de nacimiento, dirección y contacto de apoderados. La descarga no está confirmada, pero la duda favorece notificar. Corresponde notificar a la ANPD, comunicar a los titulares y avisar al CNSD. El aviso del proveedor llegó con 2 días de retraso, lo que debe reclamarse y documentarse.

## 3. Decisiones humanas (por urgencia)
1. **Aprobar y presentar la notificación a la ANPD** antes del 14/10 15:50 (completar RUC, contacto del ODP y RNPDP).
2. **Aprobar el aviso al CNSD** (mismo plazo, `[VERIFICAR canal]`).
3. **Aprobar y enviar la comunicación a titulares** (art. 34.3, mismo plazo).
4. **Ordenar el restablecimiento de todas las credenciales y MFA**, y exigir a HostAndes el informe técnico (hoy).
5. Decidir con asesoría legal la lectura del plazo (conocimiento de HostAndes desde el 10/10) y si hace falta justificar la demora.
6. Decidir sobre la relación contractual con HostAndes.

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
| Triaje | Detectar y reportar / Evaluar | 6.8, 5.25 | art. III num. 16; art. 36 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación | Responder | 5.26 | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender | 5.26–5.28 | art. 35 (también 46.3, 47) |

## 6. Información pendiente
- Confirmación de la descarga, hora exacta de la intrusión, vector y tablas afectadas (HostAndes).
- **Cifrado y hash de contraseñas** (crítico).
- Cifra exacta de titulares y apoderados; presencia de datos sensibles (p. ej. salud) en la BD.
- RUC, inscripción RNPDP, datos del ODP y canal vigente del CNSD.
- Existencia de respaldo, logs propios, contrato de encargo y documento de seguridad.
- Hora en que HostAndes tomó conocimiento y cuándo avisó a otros clientes o a la ANPD.
- Lineamientos de la ANPD sobre "gran volumen / gran número" `[VERIFICAR]`.
- No se indicó carpeta de contexto, por lo que todos los hechos son "reportados".
