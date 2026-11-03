# Informe del incidente — INC-20260929-laptop-robada-financiera

> Caso ficticio de prueba. El reporte no contiene datos personales de socios concretos; se trabajó solo con categorías y cantidades.

## 1. Estado y reloj
| Campo | Valor |
|---|---|
| Clasificación | **Incidente de seguridad de datos personales (brecha)**: FIS (robo físico) con riesgo de INT (sesión de correo abierta). Confidencialidad + disponibilidad |
| Prioridad | P1 Crítica |
| Severidad (ENISA) | **SE = 4 × 1 + 1,0 = 5,0 → Muy alta** (supone que el disco no estaba cifrado; si se confirma BitLocker, sería 1,5) |
| Toma de conocimiento | **2026-09-29 ~21:00** (el trabajador, al sufrir el robo). Criterio aplicado: sección "¿Desde cuándo corren las 48 horas?" de `knowledge/marco-normativo-peru.md`, lectura más temprana |
| **Hora límite 48 h** | **2026-10-01 21:00 (HOY)**. Tiempo restante: menos de 24 h (el agente no conoce la hora actual) |
| Lectura de referencia | Conocimiento del ODP el 2026-09-30 09:10, con límite el 2026-10-02 09:10. No usar para planificar |
| Estado | En contención. Notificaciones en borrador, **nada enviado** |

## 2. Resumen ejecutivo
El 29/09/2026 a eso de las 21:00 le robaron a un analista de créditos una laptop institucional con un Excel de unos 1 500 socios (identificación, contacto, deuda, morosidad e ingresos declarados, que son dato sensible) y con la sesión del correo institucional abierta. No se sabe si el disco estaba cifrado. Hay obligación probable de notificar a la ANPD y de comunicar a los socios, y se recomienda avisar al CNSD. El plazo vence **hoy a las 21:00**. Lo más urgente es revocar los accesos al correo y aprobar los envíos.

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Ordenar ya** la exportación de los registros del correo y luego el cierre de sesiones, el cambio de credenciales y la activación de MFA (C1–C3). El riesgo sigue en curso.
2. **Aprobar y enviar la notificación inicial a la ANPD antes del 01/10/2026 21:00** (`03-notificacion-anpd.md`), completando los datos del ODP, el RUC y el código del banco de datos.
3. **Aprobar y enviar la comunicación a los ~1 500 socios** antes del mismo límite (`03-comunicacion-titulares.md`): elegir el medio (SMS sin enlaces, llamada o carta) y completar los canales oficiales.
4. **Decidir si se avisa al CNSD** (`03-aviso-cnsd.md`). El agente recomienda hacerlo porque hay duda sobre el "entorno digital" (art. 34.5).
5. Autorizar el **borrado remoto** del equipo (C5), si existe MDM, después de registrar su estado.
6. Validar la **toma de conocimiento** (29/09 21:00) con asesoría legal y conservar la evidencia del WhatsApp.
7. Evaluar con asesoría si hay obligaciones de reporte ante la SBS u otro supervisor sectorial `[VERIFICAR: fuera de knowledge/]`.
8. Aprobar el plan de controles correctivos (sección 4 de `04-respuesta-y-cierre.md`).

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md): triaje, línea de tiempo y acciones inmediatas
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md): cálculo ENISA y decisión de notificación
- [03-notificacion-anpd.md](03-notificacion-anpd.md): borrador de la notificación inicial (art. 34.2)
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md): borrador para los socios (art. 34.3), con versión SMS
- [03-aviso-cnsd.md](03-aviso-cnsd.md): borrador para el CNSD (art. 34.5), sujeto a decisión
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md): contención, evidencia, causa raíz, controles y registro del art. 35

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1:2023 | ISO/IEC 27002:2022 | ISO/IEC 27701:2019 | D.S. 016-2024-JUS |
|---|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | 6.13.1.5 | art. III num. 16, art. 34.1 (inicio del plazo) |
| Severidad | Evaluar y decidir | 5.25 | 6.13.1.5 | art. 34.1, 34.3, 34.4, 34.5 |
| Notificación | Responder | 5.26 | 6.13.1.1, 6.13.1.5 | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28; preventivos 8.24, 8.1, 8.12, 5.15, 8.5, 6.3, 6.8, 5.24 | 6.13.1.5 (registro) | art. 35; arts. 46.3, 46.4, 47, 48.1 |

> Edición de ISO/IEC 27701 citada: 2019 `[VERIFICAR numeración frente a la edición 2025]`.

## 6. Información pendiente
- **PENDIENTE CRÍTICA:** confirmar la hora del robo y la hora del WhatsApp al jefe (definen el reloj).
- Estado de BitLocker del equipo (puede bajar la severidad de 5,0 a 1,5, pero no elimina el riesgo del correo).
- Accesos al correo institucional después del robo y contenido del buzón.
- Número exacto de socios y campos del archivo (logs de exportación, art. 46.3).
- Datos del ODP (nombre, correo, teléfono), RUC y código de inscripción del banco de datos.
- Número de la denuncia policial.
- Existencia de MDM o borrado remoto.
- Umbrales de "gran número" y "grandes volúmenes" `[VERIFICAR lineamientos ANPD]`; vigencia del enlace del formulario `[VERIFICAR]`; rango de multa `[VERIFICAR art. 39 Ley 29733]`.

---
*Borrador de apoyo para el Oficial de Datos Personales y el responsable de seguridad. Nada de lo aquí descrito ha sido notificado ni enviado.*
