# 01 — Ficha de triaje · INC-20261011-robo-laptop-bienestar

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. ESCENARIO SIMULADO (TIF UNSA).

## Reloj
| Dato | Valor |
|---|---|
| Toma de conocimiento (criterio más temprano) | 2026-10-11 19:30 (la psicóloga; `salidas/_entradas` reporte, línea 9) `[VERIFICAR hora exacta en que ella constató el robo]` |
| **Hora límite 48 h (art. 34.1)** | **2026-10-13 19:30** |
| Hora actual (dada por el usuario) | 2026-10-13 09:00 |
| **Tiempo restante** | **10 h 30 min** |
| Lectura alternativa (referencia) | Aviso a la Directora, 2026-10-12 09:10 → límite 2026-10-14 09:10. No se usa: prevalece la más temprana |

## Clasificación
- **Evento → incidente → brecha de datos personales** (art. III num. 16). Hay pérdida de datos personales y posible exposición no autorizada.
- Categoría: **FIS** (pérdida o robo físico), con posible **INT** (sesión de correo institucional abierta).
- Tipo: confidencialidad + disponibilidad.
- Prioridad: **P2 Alta**, pero con datos sensibles posiblemente expuestos y reloj corriendo; tratar con urgencia de P1.

## Hechos por nivel
| Nivel | Hecho | Fuente |
|---|---|---|
| Reportado | Robo de laptop institucional del auto de una psicóloga, 2026-10-11 19:30 | reporte, línea 9 |
| Reportado | Denuncia policial presentada la mañana del 2026-10-12 | reporte, línea 9 |
| Reportado | ~150 estudiantes: nombre, DNI, escuela, motivo de consulta, notas de sesión | reporte, línea 11 |
| Reportado | Sin cifrado de disco (según la psicóloga); sesión de correo abierta; contraseña de inicio desconocida | reporte, línea 11 |
| Reportado | Hay menores de 18 años; nadie ha sido avisado | reporte, línea 13 |
| Verificado | Fichas de Bienestar (S-05) están en laptops y carpeta local, **sin cifrado y sin respaldo** | `demo/unsa-base/inventario/activos-y-datos.md:13` |
| Verificado | Son datos sensibles (salud) y de menores; 150 fichas del semestre dentro de ~4 200 históricas | `activos-y-datos.md:26` |
| Verificado | El correo institucional es de nube del proveedor (cifrado del proveedor), accesible desde la sesión abierta | `activos-y-datos.md:15` |
| Verificado | No existe procedimiento ni responsable para notificar a la ANPD; la OTI decide si escala | `politicas/documento-seguridad-extracto.md:17-19` |
| Verificado | El plan de respuesta no tiene roles, plazos ni plantillas | `politicas/plan-respuesta-incidentes.md:3-7` |
| Verificado | Contacto ODP: Dra. Mariela Quispe Huamaní | `inventario/contactos.md:5` |
| Supuesto | Que en la laptop solo estén las 150 fichas (podrían estar las ~4 200 históricas en la "carpeta local") | — |
| Supuesto | Que el ladrón accederá a los datos (no hay evidencia de acceso) | — |
| Sin logs | El contexto no trae logs. No se puede confirmar si la sesión de correo fue usada tras el robo | — |

## Contradicciones y vacíos
- El reporte dice "150 estudiantes", pero el inventario indica que Bienestar guarda las fichas en carpeta local sin respaldo. El volumen real en el equipo puede ser mayor: **verificar**.
- No hay MDM ni borrado remoto documentado en el contexto `[VERIFICAR]`.
- No hay logs de acceso al correo en el contexto. Pedirlos al proveedor / OTI.
- El reportante es personal propio de la UNSA (no es un encargado), así que la obligación de notificar es directa del responsable.

## Contención inmediata recomendada (hoy)
1. Cerrar todas las sesiones del correo de la psicóloga, restablecer contraseña y activar MFA si es posible.
2. Revocar tokens y VPN, y bloquear la cuenta de la laptop en directorio.
3. Revisar el historial de accesos del correo desde el 2026-10-11 19:30 (IP, dispositivos).
4. Si hay MDM/borrado remoto, ordenarlo. Si no, documentar que no existe.
5. Obtener copia de la denuncia policial y el número de atestado.
6. Inventariar con la psicóloga qué carpetas y archivos había en el equipo.
7. Reconstruir las fichas desde otras fuentes, porque no hay respaldo.

## Trazabilidad
ISO/IEC 27035-1: Detectar y reportar / Evaluar y decidir · ISO/IEC 27002: 6.8, 5.25 · ISO/IEC 27701:2019: 6.13.1.5 · D.S. 016-2024-JUS: art. III num. 16.
