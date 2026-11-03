# Informe del incidente — INC-20260930-phishing-bloqueado

> BORRADOR para revisión humana. Caso ficticio. Nada se ha notificado ni enviado.

## 1. Estado y reloj
| Concepto | Valor |
|---|---|
| Clasificación | **Evento sin incidente** (FRA, phishing bloqueado) |
| Severidad | No aplica (no hay brecha, así que no se aplicó la fórmula ENISA). Prioridad P4 |
| Toma de conocimiento | 2026-09-30 11:45 |
| Referencia de 48 h | 2026-10-02 11:45 |
| Hora actual | 2026-10-13 10:00 (-0500) |
| Tiempo restante | **No hay plazo legal vigente.** La referencia de 48 h pasó hace unos 12 días y 22 h, pero no corre para un evento que no es incidente de datos personales |

## 2. Resumen ejecutivo
Un correo de phishing que suplantaba al banco llegó a 37 buzones. El reportante no hizo clic y lo reenvió a soporte. Soporte informa que nadie más hizo clic (según el proxy), bloqueó el dominio y eliminó el correo. No hay vulneración ni datos personales afectados según lo reportado, así que no corresponde notificar a la ANPD, comunicar a titulares ni avisar al CNSD. Se recomienda documentarlo y cerrarlo, una vez confirmadas las verificaciones pendientes.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. Confirmar que ningún usuario hizo clic, respondió o abrió adjuntos. Revisar los logs del proxy, DNS y correo, incluida la navegación móvil o externa. Esto es lo único que podría cambiar la conclusión.
2. Aprobar el cierre como evento sin incidente. Si algo falla, reclasificar y recalcular las 48 h desde la nueva toma de conocimiento.
3. Aprobar el registro interno del evento (art. 35 aplica a incidentes; registrarlo es buena práctica).
4. Decidir sobre medidas preventivas: refuerzo de la capacitación, reconocimiento al reportante y búsqueda de otras oleadas del mismo remitente o dominio.

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md)
- No se generaron 02, 03 ni 04, porque el flujo termina en el triaje cuando es un evento sin incidente.

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje y clasificación | Detección y evaluación `[VERIFICAR fase en knowledge/estandares-incidentes.md]` | `[VERIFICAR código]` | Art. III num. 16 (definición): no hay vulneración con datos personales |
| Notificación a la ANPD | — | — | Art. 34.1: no aplica |
| Comunicación a titulares y aviso al CNSD | — | — | Arts. 34.3 y 34.5: no aplican |
| Registro | Lecciones aprendidas | `[VERIFICAR]` | Art. 35 (documentar incidentes): buena práctica |

## 6. Información pendiente
- Hora de recepción del correo y del reporte a soporte.
- Evidencia de logs (proxy, DNS, correo, filtro) para sostener "nadie hizo clic". Hoy es solo lo dicho por soporte.
- Remitente, asunto y dominio del correo, para buscar otras oleadas.
- Oficial de Datos Personales y contacto, por si hay que reclasificar.
- No se indicó carpeta de contexto, así que no hay inventario ni logs verificables.
