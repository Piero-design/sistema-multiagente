# 04 · Plan de respuesta, evidencia y cierre — INC-20261008-campus-virtual-proveedor

> BORRADOR para decisión humana. Responsables propuestos por rol; la UNSA no tiene roles definidos (`plan-respuesta-incidentes.md:7`).

## 1. Plan de respuesta (ISO/IEC 27035-1 fase 4; ISO/IEC 27002 5.26)

### Hoy, antes de las 17:55
| # | Acción | Responsable | Plazo |
|---|---|---|---|
| 1 | Aprobar y enviar notificación a la ANPD (parcial si hace falta) | ODP + Secretaría General | **≤ 17:55** (idealmente a media mañana) |
| 2 | Requerir al proveedor por escrito la información (ver `01` §5) y confirmar contacto en soporte 24 h | OTI / Coordinador Campus | 10:00 |
| 3 | Restablecer contraseñas de todos los usuarios, revocar sesiones/tokens | Coordinación Campus + proveedor | 12:00 |
| 4 | Enviar aviso al CNSD | ODP | ≤ 17:55 |
| 5 | Aprobar y enviar comunicación a titulares | ODP + Asesoría Legal | ≤ 17:55 |
| 6 | Vigilar correo institucional por phishing; avisar a seguridad@unsa.example | OTI | continuo |

### Contención y erradicación (UNSA no controla el servidor)
- Exigir al proveedor: expulsión del atacante, parche del vector, rotación de credenciales y claves y aislamiento del servidor compartido.
- Descartar reutilización de credenciales con SRA, correo y VPN (sin MFA, `activos-y-datos.md:30-31`): forzar cambio donde coincidan.
- No pagar ni negociar con quien reclame rescate; no contactar al atacante. Escalar a Asesoría Legal y a las autoridades.

### Recuperación
- Confirmar con el proveedor integridad de la BD y plataforma limpia antes de normalizar. Respaldo propio del Campus: ninguno (solo el del proveedor, `activos-y-datos.md:11`).

## 2. Evidencia y cadena de custodia (ISO/IEC 27037; 27002 5.28)
| Evidencia | Fuente | Acción |
|---|---|---|
| Correo original de ProveedorEdu (17:55 del 11-oct) con cabeceras | Buzón del Coordinador | Exportar `.eml`, calcular hash SHA-256, registrar quién/cuándo |
| Informe forense e IoC del proveedor | Proveedor | Solicitar firmado y con fecha |
| Logs de accesos al Campus (UNSA) | Panel admin del Campus | Exportar de 2026-10-01 en adelante; hash |
| Comunicaciones UNSA–proveedor | OTI | Conservar todas |
| Envíos a ANPD/CNSD/titulares | ODP | Guardar constancias |

El contexto no incluye logs: no hay línea de tiempo verificada. Registrar en el expediente quién custodia cada pieza.

## 3. Registro del incidente (art. 35; ISO/IEC 27701 6.13.1.5)
Descripción: acceso no autorizado en el proveedor, con posible descarga de la BD. Periodo: 2026-10-08 a [fin pendiente]. Consecuencias: ver `03-notificacion-anpd.md`. Reportó: ProveedorEdu → Coordinador. Notificados: [ANPD/CNSD/titulares: fecha y hora al enviarse]. Medidas: secciones 1 y 4.

## 4. Causa raíz y brechas de control (ISO/IEC 27035-1 fase 5; 27002 5.27)
| Brecha | Evidencia | Control propuesto |
|---|---|---|
| Sin procedimiento ni responsable de notificar a la ANPD | `documento-seguridad-extracto.md:19` | Procedimiento con la regla de 48 h y plantillas (27002 5.24, 5.26) |
| Plan de respuesta sin roles ni plazos | `plan-respuesta-incidentes.md:3-7` | Plan con roles, clasificación y contactos externos |
| El reporte llegó al Coordinador y el ODP lo supo 45 min después; la OTI decide si escala | `job1791983211947.md:7`; `documento-seguridad-extracto.md:18` | Escalamiento inmediato al ODP de todo incidente con datos personales (6.8) |
| Contrato/seguimiento del encargado: avisó ~3 días tarde; cifrado "desconocido" | `activos-y-datos.md:11`; art. 36 | Cláusulas de aviso inmediato (≤ 24 h), cifrado, auditoría y evidencia (5.19-5.22 `[VERIFICAR numeración]`) |
| Sin MFA en el Campus ni en VPN | `activos-y-datos.md:30-31` | Autenticación segura (8.5) |
| Logs del SRA solo 60 días (art. 46.3: 2 años) | `activos-y-datos.md:33` | Retención de logs (8.15) |
| Documento de seguridad con revisión vencida (2026-09) | `documento-seguridad-extracto.md:3` | Revisar y aprobar (art. 47) |

## 5. Criterios de cierre
- [ ] Notificaciones enviadas y constancias archivadas (o decisión de no enviar justificada).
- [ ] Alcance confirmado por informe forense del proveedor.
- [ ] Contraseñas restablecidas; atacante expulsado.
- [ ] Comunicación a titulares enviada.
- [ ] Informe complementario a la ANPD con datos finales.
- [ ] Lecciones aprendidas aprobadas y plan de mejora con responsables y fechas.
- [ ] Revisión contractual con el proveedor.

## 6. Seguimiento propuesto
Revisión diaria hasta recibir el informe forense; revisión de cierre en [fecha a definir por el ODP].
