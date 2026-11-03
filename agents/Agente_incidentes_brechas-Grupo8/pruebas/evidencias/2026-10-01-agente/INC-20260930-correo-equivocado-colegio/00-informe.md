# Informe del incidente — INC-20260930-correo-equivocado-colegio

## 1. Estado y reloj
| Campo | Valor |
|---|---|
| Clasificación | **Incidente de seguridad de datos personales (brecha)**: confidencialidad, categoría FUG (correo al destinatario equivocado), entorno digital |
| Prioridad | P2 Alta |
| Severidad (ENISA) | **SE = DPC 4 × EI 1 + CB 0,25 = 4,25 → Muy alta** |
| Toma de conocimiento | 30/09/2026, 15:30 |
| **Hora límite (48 h, art. 34.1 y 34.3)** | **02/10/2026, 15:30** |
| Tiempo restante | 39 h 30 min al inicio del 01/10/2026; recalcular con la hora real de aprobación. **No vencido.** |
| Estado | En contención: no hay confirmación escrita de eliminación |

## 2. Resumen ejecutivo
El 29/09/2026, la secretaria académica del Colegio Los Andes envió por error a la empresa de fotos de promoción un Excel con datos de 420 alumnos menores (nombre, DNI, grado, notas) y de sus apoderados (nombre, celular, deuda de pensión y monto). Es una brecha de confidencialidad de severidad Muy alta (4,25) por tratarse de menores y de datos financieros. Se recomienda notificar a la ANPD y al CNSD y comunicar a los apoderados antes del 02/10/2026 a las 15:30. La contención depende de que el receptor confirme por escrito la eliminación del archivo.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Hoy:** aprobar y enviar el requerimiento escrito de eliminación y confidencialidad a la empresa de fotos (Dirección / Oficial de Datos Personales).
2. **Hoy:** designar o confirmar al Oficial de Datos Personales como punto de contacto y completar sus datos en los borradores (art. 34.2 num. 2).
3. **Antes del 02/10/2026, 15:30:** aprobar y enviar la notificación a la ANPD (`03-notificacion-anpd.md`). Es una obligación probable aunque el receptor confirme la eliminación (art. 34.1).
4. **Antes del 02/10/2026, 15:30:** aprobar y enviar la comunicación individual a los apoderados (`03-comunicacion-titulares.md`), cuidando que el canal no revele la deuda de cada familia.
5. **Junto con la ANPD:** aprobar el aviso al CNSD (`03-aviso-cnsd.md`, art. 34.5).
6. **Corto plazo:** aprobar los controles correctivos y asignarles responsables y fechas (`04-respuesta-y-cierre.md`, sección 4).

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md): triaje, línea de tiempo y clasificación
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md): cálculo ENISA y decisión del art. 34
- [03-notificacion-anpd.md](03-notificacion-anpd.md): borrador de notificación inicial a la ANPD
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md): borrador de aviso a los apoderados
- [03-aviso-cnsd.md](03-aviso-cnsd.md): borrador de aviso al CNSD
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md): contención, evidencia, causa raíz, controles y registro del art. 35

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1:2023 | ISO/IEC 27002:2022 | ISO/IEC 27701:2019 | D.S. 016-2024-JUS |
|---|---|---|---|---|
| 1. Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | 6.13.1.5 | art. III num. 16 (art. 36 no aplica: el reportante no es encargado) |
| 2. Severidad | Evaluar y decidir | 5.25 | 6.13.1.5 | art. 34.1 |
| 3. Notificación | Responder | 5.26 | 6.13.1.1, 6.13.1.5 | arts. 34.1 a 34.5 |
| 4. Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28 (más 8.12, 8.24, 5.34, 6.3 como mejoras) | 6.13.1.5 (registro) | arts. 35, 46.3, 46.4 |

> Edición de ISO/IEC 27701 citada: 2019 `[VERIFICAR correspondencia con la edición 2025]`.

## 6. Información pendiente
- **Crítica:** nombre y contacto del Oficial de Datos Personales; confirmación escrita de eliminación del receptor.
- RUC del colegio, banco(s) de datos inscritos y razón social del proveedor receptor.
- Dirección receptora exacta, otros destinatarios (CC/CCO) y si el archivo tenía protección.
- Número exacto de apoderados afectados y de apoderados con deuda registrada.
- Si la contadora es interna o externa (encargada) y si necesitaba las notas.
- `[VERIFICAR]`: si la deuda de pensión es dato sensible ("ingresos económicos"); umbrales de la ANPD para "gran número" o "grandes volúmenes"; vigencia del formulario `reporte.cnsd.gob.pe`; rango de multa del art. 39 de la Ley 29733.

---
*Todo el expediente es un borrador para revisión del Oficial de Datos Personales y del responsable de seguridad. Nada ha sido notificado ni enviado.*
