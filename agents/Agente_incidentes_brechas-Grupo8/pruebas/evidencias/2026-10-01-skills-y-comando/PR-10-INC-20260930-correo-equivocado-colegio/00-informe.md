# Informe del incidente — INC-20260930-correo-equivocado-colegio

> Caso ficticio de prueba (PR-10), modo no interactivo. Generado el 2026-10-01 23:25 (-05:00). Todo es **borrador**: no se ha notificado ni enviado nada.

## 1. Estado y reloj
| Campo | Valor |
|---|---|
| Clasificación | **Incidente de seguridad de datos personales (brecha)**: confidencialidad, categoría FUG (correo a destinatario equivocado), entorno digital |
| Prioridad | P2 Alta |
| Severidad | **Muy alta** (SE = 4 × 1 + 0,25 = 4,25) |
| Toma de conocimiento (inicio del reloj) | **2026-09-30, 15:30**: la secretaria advierte el error cuando la contadora le dice que no recibió el archivo (lectura más temprana) |
| **Hora límite 48 h (art. 34.1 y 34.3)** | **2026-10-02, 15:30 (-05:00)** |
| **Tiempo restante** | **16 h 05 min** (transcurridas 31 h 55 min) — plazo **vigente** |
| Lecturas de referencia | Desde el reporte formal (2026-09-30 16:20) → 2026-10-02 16:20 (16 h 55 min). Lectura estricta no adoptada, desde el envío (2026-09-29 17:05) → habría vencido el 2026-10-01 17:05 (hace 6 h 20 min) `[VERIFICAR con asesoría legal]` |
| Estado de respuesta | En contención; no procede el cierre |

## 2. Resumen ejecutivo
El 29/09 a las 17:05, una hoja de cálculo con datos de 420 alumnos menores (identificación, DNI, notas) y de sus apoderados (celular, situación de pago y monto adeudado) se envió por error a la empresa de fotos de promoción. El error se detectó el 30/09 a las 15:30 y el receptor solo prometió por teléfono que lo borraría. La severidad es Muy alta y hay obligación probable de notificar a la ANPD, comunicar a los apoderados y avisar al CNSD antes del **02/10 a las 15:30**. Los borradores están listos y solo falta la decisión humana y los datos de contacto.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Aprobar y enviar la notificación inicial a la ANPD antes de 2026-10-02 15:30**, completando antes el RUC, el banco de datos y el contacto del Oficial de Datos Personales. Hay una noche de por medio: conviene programar la aprobación a primera hora.
2. **Enviar hoy mismo o a primera hora el requerimiento escrito de eliminación** a la empresa de fotos, con pedido de confirmación escrita, y preservar el correo original con cabeceras y el registro del servidor de correo.
3. **Aprobar y enviar la comunicación a los apoderados** (mismo plazo, art. 34.3), definiendo el canal oficial y el contacto.
4. **Aprobar el aviso al CNSD** (art. 34.5) y confirmar si un mismo formulario cubre a la ANPD y al CNSD `[VERIFICAR]`.
5. Decidir con asesoría legal si el monto adeudado de pensión se trata como dato sensible (no cambia la recomendación de notificar).
6. Asignar responsables y fechas a los controles correctivos (`04-respuesta-y-cierre.md`, sección 4).

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md): triaje, línea de tiempo y acciones inmediatas
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md): cálculo ENISA y decisión art. 34
- [03-notificacion-anpd.md](03-notificacion-anpd.md): borrador de notificación inicial a la ANPD
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md): borrador para apoderados
- [03-aviso-cnsd.md](03-aviso-cnsd.md): borrador para el CNSD
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md): contención, evidencia, causa raíz, controles y registro del art. 35

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1:2023 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16; art. 34.1 (inicio del plazo) |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1, 34.3, 34.4, 34.5 |
| Notificación | Responder | 5.26 | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28 (+ 8.12, 8.24, 5.34, 6.3, 5.15 como mejora) | art. 35; arts. 46.3, 46.4, 48 |

Privacidad: ISO/IEC 27701:2019, 6.13.1.1 y 6.13.1.5 `[VERIFICAR edición citada; la 27701:2025 cambió la numeración]`.

## 6. Información pendiente
- Lo actuado entre 2026-09-30 16:20 y 2026-10-01 23:25: NO INDICADO.
- Confirmación escrita de eliminación y de si el archivo se abrió o reenvió.
- Si el archivo tenía contraseña o cifrado.
- Número real de apoderados y de familias en deuda.
- Datos del Oficial de Datos Personales, RUC y banco de datos inscrito.
- Relación contractual con la empresa de fotos y con la contadora.
- Calificación del dato de deuda como sensible; umbrales de la ANPD para "gran número" y "grandes volúmenes" `[VERIFICAR]`.
- Vigencia del enlace del formulario de reporte `[VERIFICAR]`.

---
*Borrador de apoyo para el Oficial de Datos Personales y el responsable de seguridad. No se ha enviado ninguna comunicación.*
