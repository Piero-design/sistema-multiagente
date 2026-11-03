# 04 — Plan de respuesta y cierre · INC-20261011-robo-laptop-bienestar

> BORRADOR. Los plazos son propuestas del proyecto, salvo las 48 h legales.

## 1. Plan de respuesta
| # | Acción | Responsable propuesto | Plazo | Estado |
|---|---|---|---|---|
| 1 | Cerrar sesiones del correo, resetear clave, activar MFA | OTI (Ing. Rodrigo Mamani) | Inmediato | Pendiente |
| 2 | Revocar VPN/credenciales del equipo y bloquear cuenta | OTI | Inmediato | Pendiente |
| 3 | Revisar logs de acceso al correo desde 2026-10-11 19:30 (pedir al proveedor si hace falta) | OTI | Hoy, antes de las 14:00 | Pendiente |
| 4 | Borrado remoto si existe herramienta | OTI | Inmediato | `[VERIFICAR si existe]` |
| 5 | Inventariar contenido del equipo con la psicóloga (¿solo 150 fichas o también históricas?) | ODP + Bienestar | Hoy | Pendiente |
| 6 | Obtener copia de la denuncia y n.º de atestado | Bienestar | Hoy | Pendiente |
| 7 | **Aprobar y enviar notificación a ANPD (+ CNSD)** | ODP / Secretaría General / Rectorado `[definir]` | **Antes del 2026-10-13 19:30** | Pendiente |
| 8 | Aprobar y enviar comunicación a titulares (menores → representantes) | ODP + Bienestar + Asesoría Jurídica | **Antes del 2026-10-13 19:30** | Pendiente |
| 9 | Ofrecer apoyo psicológico a los afectados, con atención a víctimas de violencia | Bienestar | 24–48 h | Pendiente |
| 10 | Reconstruir las fichas si no hay otra copia | Bienestar | 7 días | Pendiente |
| 11 | Documentar el incidente en el registro (art. 35) | ODP | Continuo | En curso con este expediente |

## 2. Evidencia (ISO/IEC 27037, control 5.28)
Preservar con cadena de custodia (quién, qué, cuándo, dónde, cómo):
- Denuncia policial y atestado.
- Declaración escrita de la psicóloga (hora, lugar, circunstancias, medidas del equipo).
- Inventario y ficha de activo de la laptop (serie, usuario, configuración).
- Logs de acceso al correo y a la VPN, exportados con hash.
- Capturas de las acciones de contención con fecha/hora.
- Copias de las notificaciones enviadas y sus acuses.
Nota: los registros de auditoría solo se guardan 60 días en el SRA (`activos-y-datos.md:33`). Exportar ya los que sirvan.

## 3. Análisis de causa raíz (preliminar)
| Factor | Evidencia | Control faltante |
|---|---|---|
| Datos sensibles en laptop sin cifrado | `activos-y-datos.md:13` | 8.24 cifrado, 8.1 dispositivos de usuario final |
| Equipo con datos dejado en un vehículo | Reporte | 7.9 activos fuera de las instalaciones, 6.3 concienciación |
| Sesión de correo abierta | Reporte | 8.5 autenticación segura, bloqueo de sesión |
| Sin respaldo de fichas | `activos-y-datos.md:13` | 8.13 copias de respaldo |
| Datos clínicos en carpeta local en vez de sistema controlado | `activos-y-datos.md:13` | 8.12 prevención de fuga de datos, 5.15 control de acceso |
| Sin procedimiento ni responsable de notificación | `documento-seguridad-extracto.md:17-19` | 5.24 preparación de incidentes |
| Plan de respuesta rudimentario | `plan-respuesta-incidentes.md` | 5.24, 5.26 |
| Documento de seguridad con revisión vencida | `documento-seguridad-extracto.md:3` | Art. 47 |

## 4. Lecciones y mejoras
**Corto plazo (≤30 días):** cifrar todos los equipos de Bienestar y de quien trate datos sensibles; bloqueo automático de sesión y contraseña de inicio obligatoria; política de no dejar equipos en vehículos; respaldo cifrado de las fichas.
**Mediano plazo (≤90 días):** trasladar las fichas a un sistema con control de acceso y logs; MDM con borrado remoto; MFA en correo y VPN; actualizar el documento de seguridad (revisión vencida) y el plan de respuesta con roles, árbol de decisión, reloj de 48 h, plantillas y contactos; designar quién firma las notificaciones a la ANPD; capacitación al personal.
**Indicadores:** % de equipos cifrados, tiempo desde el incidente hasta la notificación, simulacro semestral.

## 5. Criterios de cierre
- [ ] Notificación a ANPD y aviso a CNSD enviados y con acuse.
- [ ] Titulares comunicados.
- [ ] Alcance real confirmado (¿150 o más?).
- [ ] Revisión de logs concluida: acceso confirmado o descartado.
- [ ] Medidas de contención verificadas.
- [ ] Causa raíz aprobada y acciones asignadas.
- [ ] Expediente archivado (art. 35).

Trazabilidad: ISO 27035-1 Responder / Aprender lecciones · ISO 27002 5.26, 5.27, 5.28 · ISO 27701 6.13.1.5 · art. 35.
