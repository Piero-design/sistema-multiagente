# 00 · Informe del incidente — INC-20261011-ransomware-sra

> BORRADOR para decisión del Oficial de Datos Personales y del responsable de seguridad. ESCENARIO SIMULADO. Nada ha sido notificado ni enviado.

## 1. Estado y reloj

| Campo | Valor |
|---|---|
| Clasificación | Brecha de datos personales. Ransomware con doble extorsión (MAL + INT). Disponibilidad total y confidencialidad probable. **P1 Crítica** |
| Severidad | **ALTA** (SE = 2 × 1 + 1,5 = 3,5). Sería Muy alta (4,5) si hay datos sensibles |
| Toma de conocimiento | 2026-10-11 06:40 (lectura estricta: 05:12) |
| **Hora límite 48 h** | **2026-10-13 06:40** (lectura estricta: 05:12) |
| **Tiempo restante** | **Vencido. Excedido por 2 h 20 min** a las 09:00 del 2026-10-13 (3 h 48 min en la lectura estricta). Notificar de inmediato con justificación de la demora |
| Plazo de la extorsión (reportado) | aprox. 2026-10-14 06:40, unas 21 h 40 min |

## 2. Resumen ejecutivo
Un atacante entró por la VPN con una cuenta docente tras 198 intentos fallidos, se hizo administrador y creó la cuenta `svc_mant`. Exportó la BD y las actas (5,1 GB), de los cuales 5,1 GB salieron a una IP externa. Luego cifró el SRA, las actas y el NAS de respaldos, que quedó inservible. Están afectados hasta 89 000 titulares, unos 900 menores. Corresponde notificar a la ANPD, comunicar a los titulares y avisar al CNSD, y el plazo legal ya venció. Contrario a lo reportado, el NAS sí se cifró y la exfiltración es probable.

## 3. Decisiones humanas, por urgencia
1. **Aprobar y enviar YA la notificación a la ANPD**, con la justificación de la demora (`03-notificacion-anpd.md`). Decidir si se incluye la admisión de que no existía procedimiento de notificación, con Asesoría Legal.
2. **Aprobar el aviso al CNSD** (`03-aviso-cnsd.md`) y enviarlo junto con el anterior.
3. **Autorizar la contención**: aislar el segmento, bloquear IP, revocar cuentas y rotar credenciales, suspender o proteger la VPN con MFA. Preservar la evidencia antes de reinstalar.
4. **Postura ante la extorsión** antes de las 06:40 del 10-14: el agente no recomienda pagar. La decisión es de la alta dirección con Asesoría Legal.
5. **Aprobar la comunicación a titulares** (`03-comunicacion-titulares.md`), canales y versión para menores.
6. **Plan alterno de matrícula** y comunicación a estudiantes.
7. Decidir con Asesoría Legal si corresponde denuncia penal u otras entidades `[VERIFICAR]`.
8. Ordenar la revisión de S-03 a S-08, en especial admisión y bienestar (datos de salud).

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md): triaje, reloj, hechos verificados, línea de tiempo.
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md): puntuación y decisión legal.
- [03-notificacion-anpd.md](03-notificacion-anpd.md)
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md)
- [03-aviso-cnsd.md](03-aviso-cnsd.md)
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md): respuesta, causa raíz, mejoras, cierre.

## 5. Trazabilidad normativa

| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación ANPD, titulares y CNSD | Responder | 5.26 (ISO 27701 6.13.1.1 y 6.13.1.5) | arts. 34.1, 34.3, 34.5 |
| Respuesta y evidencia | Responder | 5.26, 5.28, 5.29, 8.13 | art. 35, 46.3, 48.1 |
| Lecciones aprendidas | Aprender lecciones | 5.27 | art. 47 |

## 6. Información pendiente
- Contenido exacto de lo exfiltrado (BD, actas o ambos) y si se publicó algo.
- Presencia de datos sensibles en las actas o en otros sistemas (S-03 a S-08).
- Cuentas y equipos comprometidos además de `svc_mant`. Origen del PowerShell de las 04:48 tras cerrarse la RDP a las 04:40.
- Fuentes alternativas de recuperación; estado real de la matrícula del 2026-10-12.
- Plazo exacto del aviso al CNSD, campos del formulario y vigencia del enlace `[VERIFICAR]`.
- Lineamientos de la ANPD sobre "gran volumen" y criterio de toma de conocimiento `[VERIFICAR]`.
- Hora real de la toma de conocimiento (confirmar con la guardia) y quién decide notificar.
- Fecha: el entorno indicaba 2026-10-14; se usó 2026-10-13 09:00 por instrucción.
