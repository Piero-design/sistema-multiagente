# 04 · Plan de respuesta y cierre — INC-20261012-acceso-indebido-historias

> BORRADOR. Responsables y fechas son propuestas para validar.

## 1. Contención y erradicación
| # | Acción | Responsable | Plazo |
|---|---|---|---|
| 1 | Deshabilitar la cuenta `admision3`, cerrar sesiones, rotar credenciales compartidas | Seguridad / TI | Inmediato |
| 2 | Congelar y exportar logs de acceso (hash, cadena de custodia, ISO/IEC 27037) | Seguridad | Hoy |
| 3 | Buscar el mismo patrón en otros usuarios (últimos 90 días como mínimo, `[VERIFICAR]`) | Calidad / Seguridad | 24 h |
| 4 | Verificar exportaciones, impresiones, capturas, USB, correo y mensajería personal | Seguridad / TI | 24 h |
| 5 | Declaración escrita de la persona involucrada, con RR. HH. y Legal | RR. HH. / Legal | 24 h |

## 2. Recuperación
No hay pérdida de integridad ni disponibilidad reportada. Validar con los logs que no hubo modificaciones. Restablecer el servicio normal de admisión con una cuenta nueva, con permisos mínimos, para el reemplazo.

## 3. Comunicaciones
- ANPD y CNSD: borradores `03-notificacion-anpd.md` y `03-aviso-cnsd.md`.
- Titulares: `03-comunicacion-titulares.md`; llevar un registro por titular (fecha, canal, constancia).
- Comunicación pública: no proactiva. Preparar una respuesta reservada por si algún medio pregunta por las personas públicas.
- Medidas disciplinarias: Legal y RR. HH. definen según el reglamento interno y la normativa laboral. No hay recomendaciones ofensivas ni acciones fuera del marco legal.

## 4. Causa raíz (hipótesis a validar)
1. Acceso excesivo: admisión puede abrir cualquier historia clínica, sin acceso por necesidad de conocer ni por episodio de atención.
2. Sin monitoreo ni alertas de accesos anómalos (el hallazgo fue casual, tras 11 días).
3. Sin "romper el vidrio" ni justificación obligatoria para historias sensibles (psiquiatría, personas públicas).
4. Concienciación insuficiente sobre confidencialidad.

## 5. Acciones correctivas y preventivas
| Acción | Control ISO/IEC 27002:2022 | Reglamento |
|---|---|---|
| Roles por función; admisión sin historia clínica completa | 5.15, 8.3 `[VERIFICAR 8.3]` | 46.1 |
| Alertas de acceso a historias sin cita, y reporte semanal | 8.15, 8.16 | 46.3 |
| Restricción reforzada y justificación en historias sensibles o VIP | 5.15, 8.12 | 46.1, 46.4 |
| Capacitación y acuerdo de confidencialidad firmado | 6.3, 6.6 `[VERIFICAR 6.6]` | 47 |
| Revisión semestral de privilegios | 5.18 `[VERIFICAR]` | 46.1 |
| Actualizar el documento de seguridad y el procedimiento de incidentes | 5.24, 5.27 | 47, 35 |

## 6. Criterios de cierre
- [ ] ANPD notificada (constancia guardada).
- [ ] CNSD avisado.
- [ ] 100 % de titulares comunicados (registro).
- [ ] Revisión de otros usuarios completada.
- [ ] Cuenta bloqueada y controles correctivos implementados.
- [ ] Informe de lecciones aprendidas aprobado (ISO/IEC 27035-1, fase 5).
- [ ] Expediente archivado (art. 35).
