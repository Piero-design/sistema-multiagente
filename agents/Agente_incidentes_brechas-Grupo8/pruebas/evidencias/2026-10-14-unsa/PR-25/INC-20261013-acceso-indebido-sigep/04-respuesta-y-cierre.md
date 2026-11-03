# 04 · Plan de respuesta y cierre — INC-20261013-acceso-indebido-sigep

> ESCENARIO SIMULADO. BORRADOR para revisión. No se recomiendan contraataques. El incidente es interno.
> Fases ISO/IEC 27035-1: responder y aprender lecciones. Controles ISO/IEC 27002:2022: 5.26, 5.27, 5.28, 8.15/8.16.

## 1. Contención (hoy, 13/10)
| # | Acción | Responsable sugerido | Plazo | Estado |
|---|---|---|---|---|
| 1 | Suspender `secretaria2`, cerrar sesiones y cambiar credenciales asociadas | Seguridad / TI | Inmediato | Pendiente |
| 2 | Quitar al rol de secretaría la vista de expedientes completos, o bloquear ese módulo | TI SIGEP | Hoy | Pendiente |
| 3 | Designar quién decide y envía las notificaciones (hoy no existe) | Dirección | Hoy | Pendiente |
| 4 | Pedir a Asesoría Jurídica criterio sobre el inicio del reloj y la comunicación a titulares | Asesoría Jurídica | Hoy | Pendiente |

## 2. Evidencia (ISO/IEC 27037; 27002 5.28)
1. Copia forense del log de SIGEP completo y de registros del servidor, red y correo. Calcular hash (SHA-256) y registrar quién, cuándo, dónde y cómo.
2. Los registros se conservan solo 45 días. Hay que extender la retención de inmediato (en ese plazo se pierde lo del 05/10 hacia el 19/11/2026).
3. Aclarar las anomalías del log (hora de consulta anterior al login, orden, sesión única, fines de semana) con el administrador de SIGEP. Documentar la zona horaria y la sincronización del reloj.
4. Declaración escrita de la persona, con Asesoría Jurídica y su área. No sacar conclusiones antes.
5. No alterar el equipo de la persona hasta tener copia de su estado.

## 3. Investigación y alcance
- ¿Hubo accesos de `secretaria2` antes del 05/10, o de otras cuentas con el mismo patrón?
- Lista de los 85 IDs (PG-2100 a PG-2688, de 7 en 7). **Contar cuántos tienen constancia médica.** Esto fija el escenario de severidad (02).
- ¿SIGEP registra exportaciones, impresiones y capturas? Si no, el "sin descargas" no es concluyente.
- Revisar correo institucional, impresoras, USB y mensajería del equipo de la persona. ¿Se compartió algo?
- Confirmar que la cuenta era usada solo por su titular (ver anomalía 3: sesión continua).
- Verificar el uso de los datos de docentes y autoridades si hay indicios de exposición.

## 4. Recuperación
- No hay pérdida de datos ni indisponibilidad. No se requiere restauración.
- Después de contener, restablecer el acceso de la persona solo con el privilegio mínimo y si la decisión de personal lo permite `[decisión de RR. HH. / Asesoría Jurídica]`.
- Monitoreo reforzado de consultas masivas durante 30 días `[plazo sugerido, no normativo]`.

## 5. Comunicaciones (ver 03)
| Destino | Plazo | Estado |
|---|---|---|
| ANPD | 15/10 10:20 como máximo | Borrador, pendiente de aprobación |
| CNSD | Junto con la ANPD | Borrador |
| 85 titulares | 15/10 10:20 como máximo, si se decide comunicar | Borrador |

## 6. Causa raíz (preliminar, a confirmar con la investigación)
| Causa | Evidencia | Control propuesto (ISO/IEC 27002:2022) |
|---|---|---|
| El sistema no aplica la política de roles. La secretaria abre expedientes completos. | `politica-posgrado.md:3`, `inventario-posgrado.md:10` | 5.15 control de acceso, privilegio mínimo |
| Sin alertas de consulta masiva | `inventario-posgrado.md:10` | 8.16 monitoreo, 8.12 prevención de fuga de datos |
| Revisión de accesos solo semanal, y detección ocho días después del inicio | `politica-posgrado.md:7` | 8.15 registro y monitoreo continuo |
| Conservación de registros de 45 días (el reglamento pide mínimo 2 años, art. 46.3) | `inventario-posgrado.md:10` | 8.15 |
| Datos de salud sin cifrado | `inventario-posgrado.md:5` | 8.24 criptografía |
| Respaldos en el mismo servidor | `inventario-posgrado.md:5` | 8.13 copias de respaldo (art. 48.1) |
| Sin procedimiento ni responsable para notificar a la ANPD | `politica-posgrado.md:8` | 5.24 preparación, 6.8 reporte de eventos |
| Falta de concienciación y de sanciones previas por uso indebido | No evidenciado `[VERIFICAR]` | 6.3 concienciación |

## 7. Plan de mejora
| # | Acción | Plazo sugerido | Estado |
|---|---|---|---|
| 1 | Aplicar permisos por rol en SIGEP y revisar privilegios (art. 46.1: al menos semestral) | 15 días | Propuesto |
| 2 | Alertas de consulta masiva y registro de exportaciones | 30 días | Propuesto |
| 3 | Ampliar la retención de registros a 2 años (art. 46.3) | 30 días | Propuesto |
| 4 | Cifrar datos de salud y sacar el respaldo del mismo servidor | 60 días | Propuesto |
| 5 | Procedimiento de incidentes con roles y plantillas (ISO/IEC 27035-2) | 30 días | Propuesto |
| 6 | Capacitación de personal administrativo | 60 días | Propuesto |
| 7 | Documento de seguridad actualizado (art. 47) | 60 días | Propuesto |

Los plazos son propuestas del agente, no exigencias normativas.

## 8. Criterios de cierre
- [ ] Cuenta suspendida y sesiones cerradas, con hora registrada.
- [ ] Evidencia preservada con hash.
- [ ] Alcance confirmado (accesos previos, exportaciones, nº de constancias médicas).
- [ ] ANPD y CNSD notificados, con constancia guardada por la organización.
- [ ] Decisión sobre comunicar a titulares, documentada.
- [ ] Registro del incidente completo (art. 35 y ISO/IEC 27701 6.13.1.5): descripción, periodo, consecuencias, quién reportó, a quién se notificó, medidas.
- [ ] Plan de mejora con responsables y fechas.
- [ ] Lecciones aprendidas revisadas (ISO/IEC 27002 5.27).
