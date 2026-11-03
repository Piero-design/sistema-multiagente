# 03 · Borrador de aviso al CNSD — INC-20261013-acceso-indebido-sigep

> ESCENARIO SIMULADO. **BORRADOR. No ha sido enviado.** Corresponde por art. 34.5: el incidente ocurrió en el entorno digital (SIGEP). Va además de la notificación a la ANPD, para el Registro Nacional de Incidentes de Seguridad Digital (D.U. N.° 007-2020).
> Canal: `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace y si el mismo formulario cubre a la ANPD y al CNSD]`

| Campo | Contenido |
|---|---|
| Organización | UNSA, Escuela de Posgrado `[VERIFICAR RUC y datos]` |
| Sistema afectado | SIGEP, Sistema de Gestión de Posgrado |
| Tipo de incidente | Acceso no autorizado / uso indebido interno de credenciales y privilegios (categoría INS) |
| Inicio del incidente | 2026-10-05 08:00 (primera consulta registrada) `[VERIFICAR accesos anteriores]` |
| Fin de la actividad registrada | 2026-10-12 17:31 (cierre de sesión) |
| Detección | 2026-10-13 (revisión semanal de accesos) |
| Impacto | Confidencialidad. 85 expedientes consultados. Posibles datos de salud. Sin evidencia de exfiltración. |
| Datos personales | Sí. Notificado a la ANPD. |
| Disponibilidad e integridad | Sin afectación reportada |
| Estado | En contención `[ACTUALIZAR: cuenta suspendida sí/no, hora]` |
| Medidas | Ver 03-notificacion-anpd.md, sección 4 |
| Contacto técnico | `[Responsable de seguridad de la información — COMPLETAR]` |
| Contacto de privacidad | Oficial de Datos Personales, odp@unsa.example, 054-555-0301 |

Indicadores técnicos: cuenta `secretaria2`; IP de inicio de sesión 10.30.2.15 (`logs/accesos-sigep.log:1`). No se identificaron indicadores externos.
