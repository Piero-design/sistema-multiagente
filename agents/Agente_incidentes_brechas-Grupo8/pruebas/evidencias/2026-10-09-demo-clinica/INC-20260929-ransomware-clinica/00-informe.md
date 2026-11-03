# Informe del incidente — INC-20260929-ransomware-clinica

Clínica San Gabriel S.A.C. (caso ficticio). Preparado con hora de referencia 2026-09-29 09:00 (-05:00). Todo es borrador para revisión; nada ha sido notificado ni enviado.

## 1. Estado y reloj
| Elemento | Valor |
|---|---|
| Clasificación | Incidente de seguridad de datos personales (brecha). MAL ransomware con doble extorsión + intrusión. Confidencialidad (probable), integridad y disponibilidad |
| Prioridad | P1 Crítica |
| Severidad | **Muy alta**: SE = 4 × 1 + 2,0 = 6,0 |
| Toma de conocimiento (lectura más temprana) | 2026-09-28 23:50, alerta del antivirus a TI sin atender |
| **Hora límite ANPD y titulares (48 h)** | **2026-09-30 23:50** |
| **Tiempo restante** | **38 h 50 min** (desde 2026-09-29 09:00) |
| Lectura de referencia | 2026-10-01 07:15, quedan 46 h 15 min |
| Plazo de rescate (inferido) | ~2026-10-02 07:15 |

## 2. Resumen ejecutivo
- Un correo con macro abierto en facturación permitió un acceso de ~8 horas a los servidores de historias clínicas, antes del cifrado de las 07:14.
- Los logs muestran una salida de 3,4 GB hacia una IP externa a las 02:14: la amenaza de publicar la base es creíble; el reporte lo desconocía.
- El respaldo `BKP-01` también está cifrado; no hay copia limpia conocida.
- Se afectan datos de salud de ~18 000 pacientes (~3 100 menores): obligación probable de notificar a la ANPD, comunicar a titulares y avisar al CNSD, todo dentro del plazo.
- El documento de seguridad no define quién notifica (`politicas/documento-seguridad-extracto.md:18`).

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Ahora:** autorizar el aislamiento de red de las 6 PC y el servidor restante (sin apagar), la desactivación de `svc_backup2` y el bloqueo de las dos IP (ficha, sección 8).
2. **Hoy:** designar quién aprueba y envía la notificación a la ANPD y fijar el responsable ante el plazo del 30/09 23:50 (hay lectura más estricta que la del reporte).
3. **Hoy:** aprobar y enviar la notificación **inicial** a la ANPD (`03-notificacion-anpd.md`) y el aviso al CNSD (`03-aviso-cnsd.md`); completar RUC, código de banco y hora de envío; verificar el enlace del formulario.
4. **Antes del 30/09 23:50:** aprobar el texto y el canal de la comunicación a ~18 000 titulares (`03-comunicacion-titulares.md`), con asesoría legal.
5. **Corto plazo:** postura de la alta dirección frente al rescate (el agente no recomienda pagar; no hay seguro cibernético) y denuncia policial `[VERIFICAR]`.
6. **Corto plazo:** contratar apoyo forense para preservar y analizar evidencia, y decidir la ruta de recuperación sin respaldo.

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md)
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md)
- [03-notificacion-anpd.md](03-notificacion-anpd.md)
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md)
- [03-aviso-cnsd.md](03-aviso-cnsd.md)
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md)

## 5. Hechos verificados que contradicen o amplían el reporte
| Reporte dice | Evidencia | Efecto |
|---|---|---|
| "No sabemos si sacaron datos" (`caso-01…md:17`) | 3,4 GB salieron a `203.0.113.9` (`firewall.log:3`); pg_dump 3,4 GB y `archive.7z` 3,4 GB (`auth-hce.log:7-8`); mismo C2 contactado desde el servidor (`firewall.log:2`) | Exfiltración probable; confidencialidad pasa a +0,5 |
| Respaldo de hace 3 semanas, "no sabemos si se cifró" (`:15`) | Cifrado al 100 % (`respaldos.log:5`); 15 y 22/09 omitidos (`respaldos.log:3-4`); última prueba de restauración: nunca (`activos-y-datos.md:33`) | No hay copia limpia |
| Inicio a las 07:15 (`:9`) | Macro abierta 23:48 (`correo-gateway.log:6`); RDP 23:52 (`auth-hce.log:3`); acceso hasta 04:10 (`auth-hce.log:10`) | Ocurrencia 8 h antes; toma de conocimiento más temprana 23:50 |
| Alerta de antivirus "nadie la revisó" (`:14`) | Cuarentena falló, protección detenida por PowerShell, conexión a C2 (`antivirus.log:4-6`); correo sin sandbox (`correo-gateway.log:4-5`); revisión "cuando hay tiempo" (`documento-seguridad-extracto.md:19`) | Confirma el hecho y lo amplía; riesgo de lectura estricta del plazo |
| 18 000 pacientes (`:13`) | Además laboratorio/imágenes (`activos-y-datos.md:22`), seguro ~6 500 (`:23`), facturación ~12 000 (`:24`), personal 74 (`:25`), ~3 100 menores (`:26`) | Alcance mayor; menores no mencionados |
| Desconectó el cable "del servidor" (`:16`) | Dos servidores cifrados (`antivirus.log:7-8`); PC-FACT-01 y `svc_backup2` aún sin neutralizar (`auth-hce.log:5`) | Contención incompleta |
| "6 computadoras" (`:9`) | Inventario: 1 PC de facturación + 5 de admisión (`activos-y-datos.md:11-12`) | Inferencia: son esas 6 |
| "¿Hay que avisar a alguien?" (`:19`) | No hay procedimiento ni responsable (`documento-seguridad-extracto.md:18`) | Sí, ANPD, titulares y CNSD |
| (no dicho) | Atacante desactivó rotación del log de auditoría (`auth-hce.log:9`); app sin control de acceso, SQL injection, `/exportar` sin registro (`app.py:10-21`); `config.py:4,6,8`; logs 90 días (`config.py:9`) | Vacíos de evidencia; no se puede acotar a los afectados |

## 6. Trazabilidad normativa
| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1, 34.3, 34.4, 34.5 |
| Notificación | Responder | 5.26 | arts. 34.1 a 34.5 |
| Respuesta, evidencia y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28, 5.29, 8.13 | arts. 35, 46.3, 48 |

ISO/IEC 27701:2019, 6.13.1.1 y 6.13.1.5 (edición 2019, ver `[VERIFICAR]` sobre la edición 2025).

## 7. Información pendiente
1. Qué datos exactos salieron y si ya hay publicación.
2. RUC, código de inscripción del banco de datos, hora real de envío.
3. Servidor desconectado y hora; contenido de la nota de rescate.
4. Si SoftSalud o NetAndes son encargados y si hay copias externas.
5. Umbrales de "gran volumen" y "gran número" `[VERIFICAR lineamientos ANPD]`; vigencia del enlace del formulario; rango de multa.
6. Ritmo de comunicación masiva a titulares y canal.

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
