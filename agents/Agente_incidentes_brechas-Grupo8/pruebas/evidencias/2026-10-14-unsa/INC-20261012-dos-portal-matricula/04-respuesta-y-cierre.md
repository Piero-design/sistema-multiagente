# 04 · Respuesta y cierre — INC-20261012-dos-portal-matricula

> BORRADOR. Registro del incidente según art. 35 y ISO/IEC 27701 6.13.1.5. Solo medidas defensivas.

## 1. Registro (art. 35)
| Campo | Contenido |
|---|---|
| Descripción | DoS volumétrico contra el portal de matrícula (S-08), 2026-10-12 09:10–11:40 |
| Quién reportó | Soporte del Centro de Cómputo → Oficial de Datos Personales, 2026-10-12 14:00 |
| Efectos | Indisponibilidad temporal; ~1 200 estudiantes sin poder matricularse; plazo ampliado |
| Datos personales | Sin compromiso reportado; **no verificado** |
| Notificaciones | Ninguna enviada ni redactada. A ANPD/CNSD: pendiente de decisión humana |
| Medidas adoptadas (reportadas) | Filtrado por NetAndes, restablecimiento del servicio, ampliación del plazo |

## 2. Contención, erradicación y recuperación
| # | Acción | Responsable sugerido | Plazo | Estado |
|---|---|---|---|---|
| 1 | **Preservar evidencia** (ISO/IEC 27037, 5.28): copiar logs del servidor web SRV-WEB-MAT, firewall, BD y NetAndes del 12/10 con hash y cadena de custodia. Los logs de auditoría se guardan solo 60 días | OTI | Hoy | Pendiente |
| 2 | **Verificar ausencia de acceso/exfiltración**: autenticaciones anómalas, consultas masivas, exportaciones y cuentas nuevas entre 08:00 y 14:00 y en las 48 h siguientes; buscar volumen de salida inusual | OTI / responsable de seguridad | Antes de las 09:10 del 14/10 | Pendiente |
| 3 | Pedir a NetAndes el informe del ataque (origen, vectores, volumen) y confirmar que el filtrado sigue activo | OTI | 24 h | Pendiente |
| 4 | Confirmar que el servicio y las matrículas realizadas durante y después de la caída son íntegros (sin duplicados ni pérdidas) | Registros Académicos | 24 h | Pendiente |
| 5 | Comunicar a estudiantes la ampliación de plazo por canal oficial; sin detalles técnicos | Registros / Comunicaciones | Hoy | Verificar que ya se hizo |
| 6 | Vigilar nuevos ataques (suelen repetirse) con guardia durante el periodo de matrícula | OTI | Hasta el cierre de matrícula | Pendiente |

## 3. Causa raíz y brechas de control (verificado en el contexto)
| Brecha | Evidencia | Control propuesto |
|---|---|---|
| Sin respaldo del portal de matrícula | `activos-y-datos.md:16` | 8.13 copias de respaldo; art. 48.1 |
| Sin cifrado en reposo | `activos-y-datos.md:16` | 8.24 criptografía |
| Alertas solo en horario de oficina; sin guardia | `activos-y-datos.md:32`; `documento-seguridad-extracto.md:5.4` | 8.16 monitoreo; 5.24 preparación |
| Plan de respuesta sin roles, plazos ni quién notifica a la ANPD | `plan-respuesta-incidentes.md`; `documento-seguridad-extracto.md:5.3` | 5.24, 5.26; arts. 34 y 47 |
| Logs 60 días en vez de 2 años (en el SRA; confirmar S-08) | `activos-y-datos.md:33`; art. 46.3 | 8.15 registro |
| Escalamiento depende de que la OTI decida | `documento-seguridad-extracto.md:5.2` | Aviso inmediato a la ODP ante todo incidente |
| Documento de seguridad con revisión vencida (2026-09) | `documento-seguridad-extracto.md:2` | Art. 47 |
| Sin protección anti-DDoS propia dependiente del ISP (no verificado) | Reporte | 8.20/8.22 redes; acuerdo de nivel de servicio con NetAndes `[VERIFICAR control]` |

Causa raíz del ataque (quién y por qué): **no determinada**. No se atribuye ni se recomienda contraataque.

## 4. Lecciones y criterios de cierre
- Escalar a la ODP en minutos, no al final del día: aquí el reporte llegó 4 h 50 min después del inicio. Definir que el reloj de 48 h cuenta desde el primer conocimiento.
- Plan mínimo: roles, matriz de clasificación, plantilla de notificación, contactos (NetAndes, ANPD, CNSD).
- **Cierre** cuando: (a) logs revisados y acta firmada de "sin acceso" o, si hay indicios, notificación enviada; (b) evidencia preservada; (c) integridad de matrículas confirmada; (d) informe de NetAndes recibido; (e) plan de acción aprobado con responsables.

## 5. Trazabilidad
ISO/IEC 27035-1 fases 4–5 · ISO/IEC 27002: 5.26, 5.27, 5.28, 5.29, 8.13, 8.15/8.16 · ISO/IEC 27701 6.13.1.5 · art. 35 del D.S. 016-2024-JUS.
