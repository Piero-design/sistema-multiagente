# 04 · Plan de respuesta y cierre — INC-20261011-ransomware-sra

> BORRADOR. Responsables propuestos; deben ser confirmados por la UNSA. Ciclo ISO/IEC 27035-1, fases 4 y 5. No se recomienda pagar el rescate ni realizar contraataques.

## 1. Respuesta inmediata (hoy, 2026-10-13)

| # | Acción | Responsable propuesto | Ref. |
|---|---|---|---|
| 1 | Aprobar y enviar la notificación a la ANPD, con justificación de la demora | ODP + Secretaría General | 34.1 |
| 2 | Aprobar y emitir la comunicación a titulares, y enviar el aviso al CNSD | ODP / Secretaría General / OTI | 34.3, 34.5 |
| 3 | **Contención**: aislar el segmento de red; bloquear 203.0.113.50 y 198.51.100.200; suspender la VPN | OTI | 5.26 |
| 4 | **Erradicación de accesos**: deshabilitar `jperez.docente`, `svc_mant`, `mquispe.admin` y `Administrador`; rotar todas las contraseñas privilegiadas y compartidas; buscar otras cuentas nuevas | OTI | 5.15, 5.17 |
| 5 | **Evidencia (ISO 27037)**: no apagar ni reinstalar aún; conservar copia forense de los discos, memoria si es posible, logs de VPN, firewall, antivirus y SRA; registrar cadena de custodia (quién, qué, cuándo, hash). Suspender la purga de logs (`firewall.log:5`) | OTI + seguridad | 5.28 |
| 6 | Revisar los demás sistemas (S-03 a S-08), en especial admisión y bienestar, por datos de salud | OTI | 5.25 |
| 7 | Confirmar el alcance de la exfiltración: tráfico a 198.51.100.200, contenido del envío de 5,1 GB, muestras en sitios de filtración | OTI | 8.16 |
| 8 | Consultar a Asesoría Legal sobre denuncia penal y otras entidades públicas aplicables `[VERIFICAR; no consta en knowledge/]` | Asesoría Jurídica | — |
| 9 | Contacto con el proveedor de internet NetAndes por filtrado de las IP | OTI | — |

## 2. Recuperación y continuidad (5.29, 8.13)
- **Los respaldos están cifrados** (`respaldos.log:3`). Evaluar copias antiguas fuera del NAS, réplicas, exportaciones en papel o PDF, el portal de matrícula S-08 y el correo institucional. `[Pendiente: inventario de fuentes alternas]`
- Reconstruir los servidores desde cero en un entorno limpio, sin reconectar los equipos afectados. Verificar la integridad de los datos recuperados antes de abrir el servicio.
- Continuidad de la matrícula: definir un procedimiento manual o alterno, con comunicación a estudiantes.
- Ante el plazo de extorsión (aprox. 2026-10-14 06:40) el criterio es no pagar y no negociar sin decisión de la alta dirección y Asesoría Legal. El pago no garantiza la devolución ni la no publicación.
- Monitorear la publicación de los datos y, si ocurre, ampliar la comunicación a los titulares y a la ANPD.

## 3. Documentación del incidente (art. 35)
Registrar hechos, efectos y medidas, cronología (ver `01-ficha-incidente.md`), quién reportó, a quién se notificó y cuándo (ISO/IEC 27701 6.13.1.5). Archivar con el expediente las constancias de envío.

## 4. Causa raíz y brechas de control

| Brecha | Evidencia | Control propuesto | Ref. |
|---|---|---|---|
| VPN sin MFA ni bloqueo por intentos; 198 fallos no detenidos | `vpn.log:4,7` | MFA, bloqueo de cuenta, alertas por geolocalización | 8.5, 5.15 |
| Alertas sin revisar el fin de semana (VPN 21:14, AV 05:12) | `documento-seguridad-extracto.md:5.4` | Guardia o monitoreo 24x7, escalamiento automático | 8.16, 5.24 |
| Cuentas compartidas, heredadas y sin baja; contraseña de Administrador compartida | `documento-seguridad-extracto.md:4.1,4.4`; `sra-auth.log:1` | Cuentas personales, gestión de privilegios, baja de cuentas, revisión semestral | 5.15, 5.17; art. 46.1 |
| NAS siempre conectado, sin copia offline, sin pruebas de restauración | `documento-seguridad-extracto.md:3.2-3.3`; `respaldos.log:4` | Regla 3-2-1 con copia inmutable u offline y prueba periódica | 8.13; art. 48.1 |
| Datos sin cifrado en reposo | `activos-y-datos.md:9-10` | Cifrado de BD y archivos | 8.24 |
| Antivirus desactivable con PowerShell | `antivirus.log:2-3` | EDR con protección contra manipulación, restricción de PowerShell | 8.7 |
| Sin segmentación: el servidor accede a Internet y envía 5,1 GB | `firewall.log:3` | Filtrado de salida, DLP, segmentación | 8.12, 8.22 |
| Logs de 30 y 60 días; rotación desactivable | `firewall.log:5`; `sra-auth.log:6` | Conservación de 2 años y logs inmutables | 8.15; art. 46.3 |
| Sin procedimiento ni responsable para notificar a la ANPD; plan de 3 líneas | `documento-seguridad-extracto.md:5.3`; `plan-respuesta-incidentes.md` | Plan de respuesta con roles, clasificación, plazos 48 h, plantillas, contactos y guardia | 5.24; art. 34, 47 |
| Documento de seguridad con revisión vencida | `documento-seguridad-extracto.md:3` | Revisar y aprobar | art. 47 |
| Compartir datos por enlaces de nube sin política | `documento-seguridad-extracto.md:7.1` | Servicios aprobados | art. 46.4 |
| Sin seguro cibernético | `contactos.md:11` | Evaluar | — |

## 5. Plan de mejora priorizado
- **0-7 días:** MFA y bloqueo en VPN, cuentas y credenciales privilegiadas, copia offline, retención de logs, guardia de seguridad, designar quién notifica.
- **30 días:** nuevo plan de respuesta y simulacro, EDR, filtrado de salida, política de bajas, cifrado.
- **90 días:** prueba de restauración, DLP, revisión del documento de seguridad, capacitación (6.3).

## 6. Criterios de cierre
- Notificaciones enviadas y constancias archivadas (ANPD, CNSD, titulares).
- Accesos del atacante eliminados y confirmado que no hay persistencia.
- Servicios restaurados y verificados.
- Alcance de la exfiltración determinado y comunicado.
- Informe de causa raíz y lecciones aprendidas (5.27) aprobado, con plan de mejora asignado.
- Seguimiento: cualquier novedad se informa a la ANPD.
