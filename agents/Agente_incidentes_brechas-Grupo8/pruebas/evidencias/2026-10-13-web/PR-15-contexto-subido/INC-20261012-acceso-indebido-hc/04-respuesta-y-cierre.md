# 04 · Plan de respuesta y cierre — INC-20261012-acceso-indebido-hc

> BORRADOR para revisión humana. Estado: **abierto**.

## 1. Contención (hoy)
| # | Acción | Responsable sugerido | Ref. |
|---|---|---|---|
| 1 | Bloquear `admision3`, revocar sesiones, rotar credenciales; revisar si las mismas credenciales dan acceso a otros sistemas | TI / Seguridad | ISO 27002 5.26, 5.17 |
| 2 | Identificar a todas las personas que usan cuentas compartidas de admisión | TI / Jefe de admisión | 5.15 |
| 3 | Mantener la suspensión; no permitir acceso físico a equipos o impresoras hasta revisar | RR. HH. | 5.26 |

## 2. Evidencia (ISO/IEC 27037, 27002 5.28)
- **Urgente:** el log solo se conserva 60 días. Exportar los logs completos de SIS-HC (no solo `admision3`) con hash SHA-256, registrar quién, cuándo, cómo; copiar a medio protegido.
- Obtener logs de impresión, red/proxy y correo de la estación 10.1.0.23 y de la cuenta, para descartar copia o envío `[VERIFICAR disponibilidad]`.
- Documentar la entrevista (acta firmada) y solicitar declaración escrita.
- Investigar las anomalías del log (orden de horas, sesión de 10 días, fines de semana, intervalos regulares) — 5.28, 8.15.

## 3. Investigación pendiente
1. Ampliar rango: accesos de `admision3` y de todos los usuarios de admisión desde el máximo disponible (60 días).
2. Contrastar los 47 HC con el registro de admisiones/citas para confirmar los 41 sin justificación.
3. Confirmar qué HC corresponden a las personas públicas mencionadas (sin copiar sus datos al expediente).
4. Verificar si hubo acceso a datos de otros titulares por otras vías (búsquedas, reportes).
5. Si aparece difusión: reevaluar severidad (CB), actualizar la ANPD y reforzar la comunicación a titulares.

## 4. Notificaciones (ver carpeta)
ANPD → `03-notificacion-anpd.md`; titulares → `03-comunicacion-titulares.md`; CNSD → `03-aviso-cnsd.md`. Registrar fecha, hora, canal y número de constancia al enviarlas.

## 5. Causa raíz y brechas de control
| Hallazgo | Evidencia | Control | Art. D.S. 016-2024-JUS |
|---|---|---|---|
| Cuentas compartidas en admisión: no hay trazabilidad individual | `activos.md:6` | 5.15, 5.16, 5.17 | 46.1 |
| Admisión puede ver HC clínicas e historias de psiquiatría (sin mínimo privilegio) | `accesos-sis-hc.log:2-48` | 5.15, 8.3 | 46.1 |
| Sin alertas de consulta / detección solo por revisión casual | `activos.md:6` | 8.15, 8.16 | 46.3 |
| Retención de 60 días (exigido ≥ 2 años) | `activos.md:6` | 8.15 | 46.3 |
| SIS-HC sin cifrado | `activos.md:4` | 8.24 | 46 `[VERIFICAR artículo aplicable]` |
| Falta de concienciación sobre confidencialidad médica `[VERIFICAR: no hay política en el contexto]` | — | 6.3 | — |
| Posible sesión abierta durante 10 días | `accesos-sis-hc.log:1,49` | 8.5 | 46.1 |

## 6. Plan de mejora (lecciones aprendidas, ISO 27035 fase 5 / 27002 5.27)
| Acción | Plazo propuesto | Responsable |
|---|---|---|
| Cuentas nominales; eliminar cuentas compartidas; MFA/cierre de sesión por inactividad | 30 días | TI |
| Perfiles de mínimo privilegio; acceso a psiquiatría solo por necesidad asistencial ("romper el vidrio" con justificación) | 30–60 días | TI / Dirección médica |
| Alertas de acceso inusual y revisión semanal de accesos (no mensual) | 30 días | Seguridad |
| Ampliar retención de logs a 2 años, con integridad | 30 días | TI |
| Cifrado de SIS-HC y respaldos | 90 días | TI |
| Capacitación y firma de acuerdo de confidencialidad; sanciones comunicadas | 30 días | RR. HH. / ODP |
| Revisión semestral de privilegios | recurrente | ODP |
| Actualizar documento de seguridad (art. 47) y registro del incidente (art. 35) | 15 días | ODP |

## 7. Criterios de cierre
- [ ] Notificaciones ANPD / CNSD presentadas y con constancia.
- [ ] Titulares comunicados.
- [ ] Alcance final confirmado (¿solo 47?).
- [ ] Descartada o confirmada la difusión.
- [ ] Evidencia preservada y cadena de custodia completa.
- [ ] Controles de la sección 6 implementados o con fecha comprometida.
- [ ] Registro art. 35 completo: hechos, efectos, medidas; informe final aprobado.
