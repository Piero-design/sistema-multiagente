# 04 · Plan de respuesta y cierre — INC-20261009-sqli-admision

> BORRADOR. Ciclo ISO/IEC 27035-1 (fases 4 y 5). Defensivo únicamente: no contraatacar, no negociar ni pagar la extorsión.

## 1. Contención (hoy, 2026-10-13)
| # | Acción | Responsable sugerido | Ref. |
|---|---|---|---|
| 1 | Confirmar que SRV-WEB-ADM sigue fuera de línea y que no hay otra ruta a la base | OTI | 27002 5.26 |
| 2 | Bloquear la IP 203.0.113.77 en el borde (con NetAndes si hace falta); no suficiente por sí solo | OTI / NetAndes | 5.26 |
| 3 | Rotar credenciales de la base y de la aplicación; revisar cuentas creadas | OTI | 5.17 |
| 4 | Revisar S-08 (matrícula) y demás aplicaciones por el mismo patrón de inyección | Desarrollo | 8.28 [VERIFICAR] |
| 5 | Solicitar al canal/plataforma el retiro del contenido publicado (vía de denuncia oficial) | Asesoría Jurídica / ODP | 5.26 |
| 6 | No responder ni pagar a quien extorsiona; registrar cualquier contacto y derivar a la Policía (denuncia) | Rectorado / Asesoría | — |

## 2. Evidencia (ISO/IEC 27037; 27002 5.28)
- Preservar logs completos del servidor web, de la base y del firewall desde, al menos, 2026-10-01; calcular hash SHA-256 y registrar cadena de custodia (quién, qué, cuándo, dónde, cómo).
- Copia forense del servidor y de la base antes de corregir. Las capturas de la publicación (sin copiar datos más allá de lo necesario).
- Los logs actuales cubren solo un extracto; verificar retención (art. 46.3 exige mínimo 2 años).

## 3. Investigación (alcance)
- Contar filas devueltas: 3 400 peticiones × hasta 500 filas; determinar si se leyó toda la tabla `postulantes` y otras (ingresantes, 612).
- Verificar ausencia de escrituras (integridad) y de webshell/persistencia.
- Contrastar la muestra publicada (en custodia del ODP) con la base para estimar autenticidad.
- Cuantificar menores y titulares con dato de discapacidad.

## 4. Recuperación
- No hay respaldo del S-04 (`inventario:12`): crear respaldo íntegro antes de cualquier cambio; reabrir el portal solo tras corregir (consultas parametrizadas, validación de entrada, WAF/limitación de tasa) y hacer prueba de seguridad.
- Monitorear la web y canales para nuevas publicaciones.

## 5. Comunicación y registro
- ANPD, CNSD y titulares: ver archivos 03 (todos vencidos o por vencer; enviar tras aprobación).
- Registrar el incidente (art. 35; ISO 27701 6.13.1.5): descripción, periodo, consecuencias, quién reportó, a quién se notificó, medidas.
- Preparar vocero único (Rectorado/Secretaría General) para consultas de prensa y estudiantes.

## 6. Causa raíz y brechas de control (con evidencia)
| Hallazgo | Evidencia | Control |
|---|---|---|
| Entrada no validada: inyección SQL en `/resultados` | `log:2-6` | 27002 8.28, 8.26 [VERIFICAR] |
| Sin detección ni alerta durante 5 h de extracción | `log:7`; alertas solo en horario de oficina (`seguridad-doc 5.4`) | 8.15, 8.16 |
| Datos sensibles sin cifrado y sin respaldo | `inventario:12` | 8.24, 8.13; art. 48.1 |
| Sin procedimiento ni responsable para notificar a la ANPD | `seguridad-doc 5.3`; `plan-respuesta 1-3` | 5.24, 5.26; arts. 34, 47 |
| Escalamiento discrecional a la OTI | `seguridad-doc 5.2` | 5.24 |
| Documento de seguridad con revisión vencida (2026-09) | `seguridad-doc:3` | art. 47 |
| Retención de logs insuficiente (SRA 60 días; verificar el portal) | `inventario:33` | art. 46.3 |

## 7. Lecciones y plan de mejora
1. Designar formalmente quién notifica y cuándo; plantillas y cronómetro de 48 h desde la primera persona que sabe (5.24).
2. Rediseñar el plan de respuesta: roles, clasificación, contactos externos (ANPD, CNSD, policía, asesoría), guardia de fin de semana.
3. Desarrollo seguro: consultas parametrizadas, revisión de código, pruebas de penetración antes de cada proceso de admisión; WAF y límite de peticiones.
4. Minimizar y cifrar datos sensibles (discapacidad) y depurar datos históricos de procesos antiguos.
5. Respaldo verificado de S-04; registros con retención ≥ 2 años (art. 46.3).
6. Simulacro anual de brecha; revisión del documento de seguridad.

## 8. Criterios de cierre
Notificaciones presentadas y registradas; titulares informados; alcance determinado; vulnerabilidad corregida y verificada; evidencias custodiadas; informe final y lecciones aprobados por ODP y responsable de seguridad.
