# 00 · Informe del incidente — INC-20261008-campus-virtual-proveedor

> Todo es BORRADOR para revisión del ODP y del responsable de seguridad. Nada ha sido notificado ni enviado. ESCENARIO SIMULADO.

## 1. Estado y reloj
| | |
|---|---|
| Clasificación | Incidente de seguridad de datos personales (brecha) **probable**; PRV + INT; confidencialidad; P2 Alta |
| Severidad | **Muy alta** (SE = 3 × 1 + 1 = 4); Alta (3) si no se aplica el ajuste de DPC |
| Toma de conocimiento | 2026-10-11 17:55 (correo del proveedor al Coordinador) |
| **Hora límite 48 h** | **2026-10-13 17:55 (-05)** |
| Hora actual | 2026-10-13 09:00 (dada por el usuario) |
| **Tiempo restante** | **8 h 55 min** |

Nota: el entorno indica fecha del sistema 2026-10-14; se usó la hora indicada en la solicitud (13-oct 09:00). Si en realidad ya es 14-oct, el plazo está vencido y debe agregarse la justificación de demora (art. 34.1). `[VERIFICAR hora real]`

## 2. Resumen ejecutivo
El proveedor ProveedorEdu (encargado) informó el 11-oct que el 8-oct hubo un acceso no autorizado a un servidor compartido y que la base del Campus Virtual de la UNSA (~22 000 usuarios: nombre, DNI, correo, notas, mensajes) podría haberse descargado. Alcance, cifrado y contraseñas se desconocen. La UNSA es la responsable y debe notificar: ANPD (gran número de titulares, ante la duda), titulares (SE ≥ 3) y CNSD (entorno digital). El proveedor tardó ~3 días en avisar; hay que documentarlo. El contexto no trae logs, así que el alcance es solo reportado.

## 3. Decisiones humanas (por urgencia)
1. **Aprobar y enviar la notificación a la ANPD antes de las 17:55** (parcial si hace falta; no esperar al proveedor). Quién: ODP + Secretaría General.
2. **Decidir cómo tratar la lectura estricta del plazo** (desde 8-oct): si se incluye la justificación de demora. Consultar a Asesoría Legal.
3. Aprobar el aviso al CNSD.
4. Aprobar la comunicación masiva a titulares (y si se avisa a representantes de menores).
5. Autorizar el restablecimiento forzado de contraseñas y la exigencia formal al proveedor (información, forense, SLA).
6. Designar responsable de custodia de evidencia y de seguimiento; escalar al Rectorado.
7. Definir si se valoran acciones contractuales contra el proveedor (art. 36).

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
| Triaje | Detectar y reportar / Evaluar | 6.8, 5.25 | art. III num. 16; art. 36 |
| Severidad | Evaluar y decidir | 5.25 | art. 34.1 |
| Notificación | Responder | 5.26 | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender | 5.26–5.28, 8.5, 8.15 | art. 35; 46.3; 47 |

## 6. Información pendiente
- **Crítica:** qué se descargó realmente y cuántos titulares; cómo se almacenan las contraseñas; cifrado de la BD.
- Hora exacta del acceso del 8-oct y estado del atacante.
- Presencia de menores y de información sensible en mensajes.
- Confirmar la hora actual real (ver nota de la sección 1).
- `[VERIFICAR]`: lineamientos ANPD sobre "gran número", vigencia del formulario, plazo del aviso al CNSD, rango de multa.
- Contexto sin logs de la UNSA ni del proveedor: no hay línea de tiempo verificada.
