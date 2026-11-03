# 00 — Informe del incidente · INC-20261012-planilla-cas-expuesta

> ESCENARIO SIMULADO (UNSA). Todo es BORRADOR para el ODP y el responsable de seguridad. Nada ha sido notificado ni enviado.

## 1. Estado y reloj
| | |
|---|---|
| Clasificación | Incidente de seguridad de datos personales (brecha de confidencialidad, FUG); entorno digital |
| Prioridad | P1 Crítica |
| Severidad | **Muy alta** (SE = 4 × 1 + 0,5 = 4,5) |
| Toma de conocimiento | 2026-10-12 (hora del aviso del docente NO INDICADA; referencia 15:45) |
| **Hora límite 48 h** | **2026-10-14 15:45 (-0500)**, referencia; puede ser anterior |
| Hora actual indicada | 2026-10-13 09:00 |
| **Tiempo restante** | **≈ 30 h 45 min** (menos si el aviso fue antes). Si la fecha real es 2026-10-14 (como indica el sistema), quedan ≤ 6 h 45 min: verificar el reloj |

## 2. Resumen ejecutivo
Una hoja de cálculo con la planilla de ~320 trabajadores CAS (nombres, DNI, cuenta bancaria, remuneración y descuentos) estuvo ~5 semanas accesible por enlace público y fue hallada en un buscador. Ya está en privado, pero no se sabe quién la abrió. Se cumplen los supuestos del art. 34.1 (datos sensibles/financieros, perjuicio probable). Se recomienda notificar a la ANPD, comunicar a los titulares y avisar al CNSD. El contexto confirma que no hay política de uso compartido ni procedimiento de notificación.

## 3. Decisiones humanas pendientes (por urgencia)
1. **Confirmar la hora real de toma de conocimiento** (mensaje del docente) y el reloj actual, para fijar la hora límite.
2. **Aprobar y enviar la notificación a la ANPD** antes de la hora límite (`03-notificacion-anpd.md`). Quién firma, porque el documento de seguridad no define quién notifica.
3. **Aprobar y enviar el aviso al CNSD** (`03-aviso-cnsd.md`).
4. **Aprobar la comunicación a los 320 titulares** y el canal (`03-comunicacion-titulares.md`).
5. **Ordenar la contención y preservación de evidencia** (acciones 1 a 4 de `04-respuesta-y-cierre.md`), incluida la solicitud de desindexación.
6. Decidir si se contacta a bancos y si se evalúa la medida laboral/disciplinaria (con Asesoría Jurídica; el enfoque recomendado es causa sistémica).
7. Aprobar las acciones correctivas y el responsable de cada una.

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
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | art. III num. 16, art. 36 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación | Responder | 5.26 | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28 | art. 35 (más 46.1, 46.3, 46.4, 47 y 48.1 como brechas) |

ISO/IEC 27701:2019 6.13.1.1 y 6.13.1.5; NIST SP 800-61r3 (RS); ISO/IEC 27037 para evidencia. `[VERIFICAR]` la edición de ISO/IEC 27701 que se cite.

## 6. Información pendiente
- Hora del aviso del docente y hora en que se puso en privado.
- Nombre de la plataforma, fecha exacta de publicación y quién tuvo acceso al archivo (copias, reenvíos).
- Columnas exactas, especialmente "descuentos" (¿retenciones judiciales, afiliación sindical?), y presencia de menores.
- Si el enlace sigue indexado o en caché.
- Vigencia del canal de reporte y lineamientos de la ANPD sobre "gran volumen / gran número" `[VERIFICAR]`.
- Quién firma las notificaciones.
- Nota: el contexto `unsa-base` no incluye logs, por lo que ningún acceso de terceros está verificado.
