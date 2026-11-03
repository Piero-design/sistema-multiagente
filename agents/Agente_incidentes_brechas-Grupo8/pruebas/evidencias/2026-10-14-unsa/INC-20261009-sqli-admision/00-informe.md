# 00 · Informe del incidente — INC-20261009-sqli-admision

> BORRADOR para revisión del ODP y del responsable de seguridad. ESCENARIO SIMULADO. Nada ha sido enviado ni notificado.

## 1. Estado y reloj
| Concepto | Valor |
|---|---|
| Clasificación | Brecha de datos personales (INT: inyección SQL con exfiltración y extorsión); confidencialidad; **P1 Crítica** |
| Severidad | **MUY ALTA** (SE = 4 × 1 + 1,0 = 5,0) |
| Toma de conocimiento | 2026-10-10, mañana (hora exacta NO INDICADA); correo al ODP 11:15 |
| Hora límite 48 h | **2026-10-12 11:15 como máximo** (o antes) |
| Hora actual | 2026-10-13 09:00 |
| Tiempo restante | **Ninguno: plazo vencido hace ≈ 21 h 45 min (mínimo)**. Notificar ya y justificar la demora (art. 34.1) |

## 2. Resumen ejecutivo
Un tercero explotó una inyección SQL en el formulario de resultados del portal de admisión (2026-10-09 22:01 a 10-10 03:00) y publicó una muestra de 300 postulantes, con amenaza de publicar el resto. El reporte habla de 300 registros, pero los logs muestran paginación hasta `OFFSET 17500` y más de 3 400 peticiones: la exposición probable es de **~18 000 titulares**, con datos de discapacidad (sensibles) y menores. Corresponde notificar a la ANPD, comunicar a los titulares y avisar al CNSD, todo ya fuera de plazo.

## 3. Decisiones humanas (por urgencia)
1. **Aprobar y presentar de inmediato la notificación a la ANPD** (`03-notificacion-anpd.md`), con el motivo de la demora redactado con Asesoría Jurídica.
2. **Confirmar la hora exacta de conocimiento** (estudiante, Jefe de Desarrollo) y cuantificar la demora.
3. Aprobar y presentar el aviso al **CNSD**.
4. Aprobar la **comunicación a titulares** y su canal; definir el mecanismo para menores.
5. Autorizar contención: confirmar portal apagado, bloqueo de IP, rotación de credenciales, solicitud de retiro del contenido.
6. Denunciar la extorsión ante la Policía; **no pagar ni negociar**.
7. Ordenar preservación forense y la investigación del alcance (¿se leyó toda la tabla? ¿otras tablas?).
8. Designar el vocero institucional.

## 4. Entregables
- [01 Ficha de triaje](01-ficha-incidente.md)
- [02 Evaluación de severidad](02-evaluacion-severidad.md)
- [03 Notificación ANPD](03-notificacion-anpd.md)
- [03 Comunicación a titulares](03-comunicacion-titulares.md)
- [03 Aviso CNSD](03-aviso-cnsd.md)
- [04 Respuesta y cierre](04-respuesta-y-cierre.md)

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar | 6.8, 5.25 | art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación | Responder | 5.26 | arts. 34.1 a 34.5 |
| Respuesta y cierre | Responder / Lecciones | 5.26, 5.27, 5.28, 8.13, 8.15 | arts. 35, 46.3, 48.1 |
Con ISO/IEC 27701:2019 6.13.1.1 y 6.13.1.5 para registro y notificación [VERIFICAR edición citada].

## 6. Información pendiente
- Hora exacta de toma de conocimiento (crítica).
- Cantidad exacta de titulares y menores afectados; si hay ingresantes (612) incluidos.
- Logs completos (el extracto resume >3 400 peticiones) y existencia de escrituras o persistencia.
- Autenticidad de la muestra publicada.
- Estado real de las medidas de contención.
- Lineamientos de la ANPD sobre "grandes volúmenes" y vigencia del formulario; rango de multa [VERIFICAR].
- Discrepancia de fecha: la orden indica 2026-10-13 09:00; el sistema indica 2026-10-14. Se usó la de la orden.
