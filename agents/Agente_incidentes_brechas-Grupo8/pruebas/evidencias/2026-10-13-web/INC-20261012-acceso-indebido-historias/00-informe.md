# 00 · Informe del incidente — INC-20261012-acceso-indebido-historias

> BORRADOR para decisión humana. Nada ha sido notificado ni enviado. Caso ficticio.

## 1. Estado y reloj
| | |
|---|---|
| Clasificación | Brecha de datos personales (categoría INS, uso indebido interno), confidencialidad, datos sensibles |
| Prioridad | P2 Alta |
| Severidad | **MUY ALTA**: SE = 4 × 1 + 0,75 = **4,75** |
| Toma de conocimiento | 2026-10-12, antes de las 11:05 |
| **Hora límite 48 h** | **2026-10-14 11:05 (-05:00)** como máximo, o antes si la revisión empezó antes de las 11:05 |
| Hora actual | 2026-10-13 10:00 |
| **Tiempo restante** | **≤ 25 h 05 min** |
| Obligaciones | Notificar ANPD, comunicar a titulares, avisar al CNSD, documentar (arts. 34.1, 34.3, 34.5, 35) |

## 2. Resumen ejecutivo
Una técnica de admisión (`admision3`) consultó 47 historias clínicas entre el 01 y el 11/10, y solo 6 tenían relación con su trabajo. Hay pacientes de psiquiatría, una regidora y una cantante local. El hallazgo fue casual, porque no hay alertas. No hay evidencia de copia, aunque no está verificada. Al ser datos de salud (sensibles), la notificación a la ANPD es obligatoria, y por la severidad corresponde comunicar a los titulares y avisar al CNSD. No se pudo contrastar nada con el entorno: todo es "reportado".

## 3. Decisiones humanas (por urgencia)
1. **Hoy:** ordenar el bloqueo de la cuenta `admision3` y la preservación de logs con cadena de custodia.
2. **Antes de las 11:05 del 14/10 (mejor hoy):** aprobar y enviar la notificación a la ANPD (completar RUC, contacto y hora exacta de conocimiento).
3. **Mismo plazo:** aprobar y enviar el aviso al CNSD.
4. **Mismo plazo:** aprobar la comunicación a los titulares y definir el canal. Se necesita la lista de pacientes y la validación de los 6 con justificación. Tratamiento especial para psiquiatría y personas públicas.
5. Autorizar la revisión de otros usuarios y de exportaciones o impresiones.
6. Decisión disciplinaria con Legal y RR. HH.
7. Si se confirma copia o difusión: recalcular severidad (SE 5,0, P1) y ampliar la notificación.

## 4. Entregables
- [01-ficha-incidente.md](01-ficha-incidente.md)
- [02-evaluacion-severidad.md](02-evaluacion-severidad.md)
- [03-notificacion-anpd.md](03-notificacion-anpd.md)
- [03-comunicacion-titulares.md](03-comunicacion-titulares.md)
- [03-aviso-cnsd.md](03-aviso-cnsd.md)
- [04-respuesta-y-cierre.md](04-respuesta-y-cierre.md)

## 5. Trazabilidad normativa
| Paso | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | D.S. 016-2024-JUS |
|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar | 6.8, 5.25 | Art. III num. 16 |
| Severidad | Evaluar y decidir | 5.25 | Art. 34.1 |
| Notificación | Responder | 5.26 | Arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender | 5.26, 5.27, 5.28 | Art. 35, 46.1, 46.3 |

## 6. Información pendiente
- Hora exacta de toma de conocimiento en Calidad (define la hora límite real).
- RUC, inscripción del banco de datos y contacto del Oficial de Datos.
- Lista de los 47 pacientes y cuáles de los 6 tuvieron acceso justificado.
- Logs completos: exportación, impresión, alteraciones, accesos de otros usuarios.
- Vigencia del enlace del formulario y lineamientos ANPD sobre "gran número" `[VERIFICAR]`.
- Controles marcados `[VERIFICAR]` en `04-respuesta-y-cierre.md` (8.3, 6.6, 5.18 no están en `knowledge/`).
