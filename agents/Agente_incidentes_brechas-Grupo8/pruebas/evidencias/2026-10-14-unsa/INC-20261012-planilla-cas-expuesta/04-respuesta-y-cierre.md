# 04 — Respuesta y cierre · INC-20261012-planilla-cas-expuesta

> BORRADOR (registro del art. 35 y lecciones aprendidas). Estado: ABIERTO.

## 1. Línea de tiempo
| Fecha/hora | Hecho | Nivel |
|---|---|---|
| ~2026-09-07 | Se comparte la hoja con "cualquier persona con el enlace" (5 semanas antes, según historial) | Reportado |
| 2026-10-12, hora ? | Un docente informa a RR. HH. del hallazgo vía buscador | Reportado |
| 2026-10-12, hora ? | RR. HH. pone el archivo en privado | Reportado |
| 2026-10-12 15:45 | El Jefe de RR. HH. escribe al ODP | Reportado |
| 2026-10-13 09:00 | Inicio de gestión del expediente (hora indicada) | Dato del comando |
| 2026-10-14 15:45 | **Límite de notificación (referencia)** | Calculado |

## 2. Plan de contención y respuesta
| # | Acción | Responsable sugerido | Plazo |
|---|---|---|---|
| 1 | Preservar evidencia antes de más cambios: capturas del historial de uso compartido, configuración, URL, hora del cambio; hash de una copia del archivo, con cadena de custodia (ISO/IEC 27037) | OTI + ODP | Hoy |
| 2 | Confirmar que el enlace ya no es accesible desde una sesión externa | OTI | Hoy |
| 3 | Solicitar al buscador retiro de la URL y de la caché; buscar otras copias del archivo y del nombre de la hoja | OTI | Hoy |
| 4 | Pedir a la plataforma lo que ofrezca sobre accesos (la versión gratuita no da detalle; documentar la limitación) | OTI | 24 h |
| 5 | Inventariar otros archivos con datos personales compartidos por enlace público, por ejemplo planillas, bienestar, admisión | OTI + RR. HH. | 72 h |
| 6 | Entrevistar a la analista y a contabilidad (sin sanción inicial; recoger hechos): ¿otras copias, reenvíos, dispositivos? | RR. HH. + ODP | 24 h |
| 7 | Mover el intercambio de planillas a un canal institucional con permisos nominales | OTI | 72 h |
| 8 | Aprobar y enviar notificación ANPD, aviso CNSD y comunicación a titulares | ODP / Rectorado | **antes de 2026-10-14 15:45** |
| 9 | Contactar a los bancos si procede; monitorear intentos de fraude, phishing o reclamos de trabajadores | RR. HH. | 7 días |
| 10 | Recibir y documentar consultas de los titulares | ODP | continuo |

No se recomienda contactar a quienes pudieron haber accedido de forma ofensiva ni medidas de contraataque.

## 3. Causa raíz y brechas de control (verificado en contexto)
| Hallazgo | Evidencia | Control |
|---|---|---|
| El compartir por enlace público está permitido sin lista de servicios aprobados | `documento-seguridad-extracto.md:26`; `activos-y-datos.md:35` | ISO 27002: 8.12 (prevención de fuga), 5.15, 5.34. Reglamento art. 46.4 |
| Planillas CAS en hojas de cálculo sin cifrado y con respaldo parcial | `activos-y-datos.md:14` | 8.24, 8.13. Art. 48.1 |
| No hay procedimiento ni responsable de notificación a la ANPD | `documento-seguridad-extracto.md:19` | 5.24, art. 34 |
| Escalamiento depende de la OTI (que decide si avisa al ODP) | `documento-seguridad-extracto.md:17-18`; `plan-respuesta-incidentes.md:1-3` | 5.24, 6.8 |
| Documento de seguridad vencido (revisión 2026-09) | `documento-seguridad-extracto.md:3` | Art. 47 |
| Sin registros de uso de la nube (art. 46.3) | Reportado | 8.15 |
| Falta de concienciación del personal sobre compartir datos | Supuesto | 6.3 |

Causa raíz preliminar: error humano habilitado por la ausencia de política y de herramientas aprobadas (causa sistémica, no solo individual).

## 4. Acciones correctivas (lecciones aprendidas, ISO/IEC 27035-1 fase 5)
1. Política de uso compartido: servicios aprobados, prohibición de enlaces públicos para datos personales, uso de permisos nominales.
2. Controles de prevención de fuga (DLP o bloqueo del uso compartido público en el correo/almacenamiento institucional).
3. Capacitación a RR. HH., contabilidad y personal con acceso a planillas.
4. Actualizar el plan de respuesta: roles, clasificación, plazos de 48 h, quién notifica y plantillas (esto cubre la brecha de `plan-respuesta-incidentes.md`).
5. Revisar y actualizar el documento de seguridad.
6. Cifrar o proteger con contraseña las planillas; registro de accesos con retención mínima de 2 años.
7. Revisión semestral de accesos (art. 46.1).

## 5. Criterios de cierre
- [ ] Enlace inaccesible y desindexado.
- [ ] Evidencia preservada.
- [ ] Notificaciones a ANPD y CNSD enviadas y con constancia (no afirmar antes).
- [ ] Titulares comunicados.
- [ ] Inventario de otros enlaces públicos revisado.
- [ ] Acciones correctivas asignadas con fecha.
- [ ] Informe final aprobado por el ODP.

## 6. Registro del incidente (art. 35)
Hechos, efectos y medidas: ver secciones 1 a 3. Quién reportó: docente → Jefe de RR. HH. → ODP. Notificado a: `[pendiente]`.
