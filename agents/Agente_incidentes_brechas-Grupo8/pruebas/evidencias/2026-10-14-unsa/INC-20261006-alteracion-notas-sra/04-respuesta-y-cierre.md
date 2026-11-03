# 04 · Plan de respuesta y cierre — INC-20261006-alteracion-notas-sra

> ESCENARIO SIMULADO. BORRADOR para decisión humana. Estado de cada acción: **Hecha** (verificada) / **Pendiente**. No se ha ejecutado nada fuera del bloqueo de la cuenta.

## 1. Contención
| # | Acción | Responsable sugerido | Plazo | Estado |
|---|---|---|---|---|
| C1 | Bloquear cuenta `rgutierrez` | OTI | — | **Hecha** 12/10 11:20 (`sra-auditoria-notas.log:8`) |
| C2 | Listar y bloquear todas las cuentas de docentes cesados y de secretaría compartidas | OTI | 24 h | Pendiente |
| C3 | Restringir temporalmente la edición de notas a un flujo con aprobación (p. ej. doble validación) | Registros + OTI | 24 h | Pendiente |
| C4 | Aislar el equipo 10.20.5.33 sin apagarlo ni reinstalarlo | OTI | Inmediato | Pendiente |
| C5 | Restablecer contraseñas de cuentas con permisos de edición de notas | OTI | 24 h | Pendiente |

## 2. Evidencia y cadena de custodia (ISO/IEC 27037; control 5.28)
- Exportar el log de auditoría completo del SRA con hash (quién, qué, cuándo, dónde, cómo). La retención es de 60 días: **urgente** (`activos-y-datos.md:33`).
- Imagen forense del equipo 10.20.5.33 y registro de accesos físicos/sesión local de esa noche [VERIFICAR existencia de bitácora o cámaras].
- Actas firmadas de los cursos afectados (S-02) y copia del respaldo del 04/10 como base de comparación. El NAS está permanentemente conectado: sacar una copia de solo lectura y verificar su integridad (nunca se probó una restauración).
- Registrar cadena de custodia y no alterar los originales.

## 3. Investigación (ISO/IEC 27035-1; controles 5.26, 8.15, 8.16)
1. Reconstruir las 23 modificaciones (20 están solo resumidas en el log) y compararlas con las actas.
2. Buscar toda actividad de esa cuenta y de otras cuentas inactivas en los 60 días disponibles, en todas las escuelas.
3. Identificar quién usó el equipo y quién conocía la clave de la cuenta. Las cuentas de secretaría son compartidas, así que la atribución no está probada: evitar conclusiones prematuras.
4. Verificar si hubo consultas o exportaciones (hoy no se auditan; revisar logs de base de datos y servidor).
5. Los hallazgos disciplinarios o penales (venta de notas) corresponden a Asesoría Jurídica y a la autoridad competente; el agente no concluye responsabilidades.

## 4. Erradicación y recuperación
- Restaurar las notas alteradas a su valor válido según acta, con aprobación del área académica, y dejar constancia de cada cambio.
- Confirmar integridad de las notas de las demás escuelas con muestreo contra actas.
- Dar de baja de forma definitiva cuentas no vigentes.

## 5. Notificaciones y comunicación (ver 03-*)
| Obligación | Vence | Estado |
|---|---|---|
| ANPD (art. 34.1) | 2026-10-14 11:20 | Borrador, sin enviar |
| CNSD (art. 34.5) | Igual | Borrador, sin enviar |
| Titulares (art. 34.3) | ~48 h | Borrador, sin enviar; pendiente de validación legal |
| Registro interno (art. 35) | Siempre | Este expediente |

## 6. Causa raíz y brechas de control
| Brecha | Evidencia | Control (ISO/IEC 27002:2022 / reglamento) |
|---|---|---|
| Sin procedimiento de baja de cuentas | `documento-seguridad-extracto.md:4.4` | 5.15, 5.16 · art. 46.1 |
| Cuentas compartidas y heredadas | `documento-seguridad-extracto.md:4.1` | 5.15, 5.17 · art. 46.1 |
| Sin MFA en el SRA | `activos-y-datos.md:31` | 8.5 |
| Auditoría solo de modificaciones, no de consultas | `sra-auditoria-notas.log:7` | 8.15 · art. 46.3 |
| Retención de logs de 60 días (mín. 2 años) | `activos-y-datos.md:33` | 8.15 · art. 46.3 |
| Detección por reclamo y no por alerta; 5 días de demora | Cronología del log | 8.16 |
| Sin procedimiento de notificación ni responsable; la OTI decide el escalamiento | `documento-seguridad-extracto.md:5.2, 5.3`; `plan-respuesta-incidentes.md` | 5.24, 5.26 · arts. 34, 47 |
| Documento de seguridad con revisión vencida (2026-09) | `documento-seguridad-extracto.md:1` | art. 47 |
| Revisión de privilegios no semestral [VERIFICAR] | `activos-y-datos.md:31` | art. 46.1 |

## 7. Acciones correctivas propuestas
| # | Acción | Plazo sugerido |
|---|---|---|
| M1 | Procedimiento de alta/baja de cuentas ligado a RR. HH. y revisión semestral de privilegios | 30 días |
| M2 | MFA para el SRA, empezando por cuentas con edición de notas | 60 días |
| M3 | Auditar también consultas/exportaciones y conservar logs ≥ 2 años; alertas por edición de notas fuera de horario | 60 días |
| M4 | Eliminar cuentas compartidas; cuentas personales trazables | 30 días |
| M5 | Flujo de modificación de notas con doble aprobación y acta/solicitud de respaldo | 30 días |
| M6 | Reemplazar el plan de respuesta: roles, clasificación, plazo de 48 h, plantillas y responsable de notificar | 30 días |
| M7 | Actualizar el documento de seguridad (revisión vencida) | 30 días |

## 8. Criterios de cierre
- [ ] Notificaciones a ANPD y CNSD enviadas y con constancia (por humanos).
- [ ] Titulares comunicados o decisión legal documentada.
- [ ] 23 notas reconciliadas; muestreo de otras escuelas completado.
- [ ] Alcance de consultas determinado o declarado indeterminable.
- [ ] Informe disciplinario/legal en manos de la autoridad competente.
- [ ] Medidas M1–M7 con responsable y fecha.
- [ ] Reunión de lecciones aprendidas (ISO/IEC 27035-1, fase 5; control 5.27).

## 9. Cronología
| Fecha/hora | Evento | Fuente |
|---|---|---|
| 2026-10-04 | Último respaldo completo | `activos-y-datos.md:9` |
| 2026-10-06 22:41 | Inicio de sesión de la cuenta inactiva | log:1 |
| 2026-10-06 22:44 – 10-07 00:40 | 23 modificaciones de notas | log:2-5 |
| 2026-10-07 00:41 | Cierre de sesión | log:6 |
| Fecha no indicada | Reclamo del estudiante; revisión de auditoría | Reporte |
| 2026-10-12 11:20 | Cuenta bloqueada (toma de conocimiento adoptada) | log:8 |
| 2026-10-12 12:00 | Correo a la ODP | Reporte |
| 2026-10-14 11:20 | **Hora límite ANPD/CNSD** | art. 34.1 |
