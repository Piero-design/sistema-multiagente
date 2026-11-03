# Informe del incidente — INC-20260929-laptop-robada-cooperativa

> Caso ficticio (Cooperativa Misti Ahorro). Expediente de borradores para decisión humana. **Nada ha sido notificado ni enviado.**

## 1. Estado y reloj
| Campo | Valor |
|---|---|
| Clasificación | **Incidente de seguridad de datos personales (brecha)**: confidencialidad + disponibilidad; categoría FIS (robo físico), con riesgo derivado INT (sesión de correo abierta) |
| Prioridad | **P1 Crítica** (subida desde P2 por datos sensibles, vector de correo activo y plazo que vence hoy) |
| Severidad | **SE = 4 × 1 + 1,0 = 5,0 → Muy alta** (escenario base, sin cifrado confirmado). Si se confirma BitLocker con equipo apagado o bloqueado: 4 × 0,25 + 0,5 = 1,5 → Baja |
| Toma de conocimiento | 2026-09-29, ~21:00 (criterio conservador: el robo le ocurre a un trabajador del responsable) |
| **Hora límite 48 h** | **2026-10-01, 21:00**. Hoy es 01/10/2026: **vence hoy, quedan menos de 24 h** (la hora actual no está disponible para el agente) |
| Límite alternativo (no recomendado) | 2026-10-02, 09:10 (contado desde el reenvío al ODP) |
| Estado de respuesta | En contención; no consta ninguna medida técnica ejecutada |

## 2. Resumen ejecutivo
El 29/09/2026 (~21:00) robaron una laptop institucional con un Excel de la cartera de unos 1 500 socios: identificación, contacto, deuda, cuotas atrasadas e **ingresos declarados (dato sensible)**. No se sabe si el disco estaba cifrado, y el correo institucional quedó con la sesión abierta. Severidad Muy alta (5,0). Hay **obligación probable** de notificar a la ANPD (datos sensibles y perjuicio evidente) y de comunicar a los socios; además, se recomienda avisar al CNSD. **El plazo vence hoy a las 21:00.**

## 3. Decisiones que debe tomar un humano (por urgencia)
1. **Ya:** ordenar a TI preservar los logs y luego cerrar las sesiones del correo, rotar credenciales y verificar BitLocker (ficha, acciones 1–4). *Responsable de seguridad.*
2. **Antes de las 21:00 de hoy:** completar los datos del ODP y el RUC, revisar y **aprobar el envío de la notificación inicial a la ANPD** (`03-notificacion-anpd.md`). *ODP + representante del responsable.*
3. **Antes de las 21:00 de hoy:** aprobar el envío del **aviso al CNSD** o descartarlo con fundamento escrito (`03-aviso-cnsd.md`). *ODP.*
4. **Hoy (dentro de las 48 h):** aprobar el texto, el medio y el envío de la **comunicación a los ~1 500 socios** y preparar a atención y cobranzas (`03-comunicacion-titulares.md`). *ODP + gerencia.*
5. Confirmar el criterio legal sobre el momento de toma de conocimiento `[VERIFICAR con asesoría legal]`.
6. Aprobar el borrado remoto del equipo (pierde evidencia del dispositivo, que de todos modos no se tiene). *Responsable de seguridad.*
7. Aprobar los controles correctivos y sus responsables (`04-respuesta-y-cierre.md`, sección 4). *Gerencia.*

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md): triaje, línea de tiempo y acciones inmediatas
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md): cálculo ENISA y decisión del art. 34
- [03-notificacion-anpd.md](03-notificacion-anpd.md): notificación inicial a la ANPD
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md): comunicación a los socios
- [03-aviso-cnsd.md](03-aviso-cnsd.md): aviso al CNSD
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md): contención, evidencia, causa raíz, controles y registro del art. 35

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1:2023 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16 (definición); art. 36 (no aplica: no hay encargado) |
| Severidad y decisión | Evaluar y decidir | 5.25 | arts. 34.1, 34.3, 34.4, 34.5 |
| Notificación ANPD / titulares / CNSD | Responder | 5.26 | arts. 34.1 (48 h), 34.2 (contenido mínimo), 34.3, 34.5 |
| Contención y evidencia | Responder | 5.26, 5.28 | art. 46.3 (logs, 2 años) |
| Causa raíz y controles | Aprender lecciones | 5.27; 8.24, 8.1, 8.12, 5.15, 8.5, 5.17, 6.3, 6.8, 8.15/8.16 | arts. 46.1, 46.4, 48.1 |
| Registro | Aprender lecciones | 5.27 | art. 35 (ISO/IEC 27701:2019 6.13.1.5) |

## 6. Información pendiente
1. **(Crítica)** Hora del aviso por WhatsApp al jefe, y criterio legal sobre la toma de conocimiento.
2. **(Crítica)** Estado de BitLocker, custodia de la clave y estado del equipo (apagado, suspendido o bloqueado) al momento del robo.
3. **(Crítica)** Nombre y contacto del ODP y RUC de la cooperativa, necesarios para el art. 34.2 num. 2.
4. Actividad en la cuenta de correo después del 29/09 21:00; otros archivos o credenciales en el equipo.
5. Número exacto de socios afectados y de socios con cuotas atrasadas; banco de datos y código de inscripción.
6. Constancia de la denuncia policial.
7. `[VERIFICAR]`: vigencia del formulario del CNSD; lineamientos de la ANPD sobre "gran número" y "grandes volúmenes"; alcance de "entorno digital"; rango de multa en UIT; obligaciones sectoriales de cooperativas.

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
