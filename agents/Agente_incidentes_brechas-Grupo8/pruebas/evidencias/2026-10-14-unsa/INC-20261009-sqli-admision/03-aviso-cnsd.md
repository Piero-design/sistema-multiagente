# 03 · Aviso al Centro Nacional de Seguridad Digital (CNSD) — BORRADOR (NO ENVIADO)

> Base: art. 34.5 D.S. 016-2024-JUS (incidente en entorno digital; Registro Nacional de Incidentes de Seguridad Digital, D.U. 007-2020). Canal: `https://reporte.cnsd.gob.pe` [VERIFICAR vigencia]. Aprobación: ODP y responsable de seguridad.

| Campo | Contenido |
|---|---|
| Organización | Universidad Nacional de San Agustín (simulado) |
| Contacto técnico | Ing. Rodrigo Mamani Cáceres, Jefe de OTI — oti@unsa.example — 999 000 302 |
| Contacto de datos personales | Dra. Mariela Quispe Huamaní — odp@unsa.example — 054-555-0301 |
| Sistema afectado | Portal de admisión y resultados (SRV-WEB-ADM), servidor propio |
| Tipo | Intrusión por explotación de vulnerabilidad (inyección SQL) con exfiltración y extorsión |
| Inicio / fin de la actividad | 2026-10-09 22:01 / 2026-10-10 03:00 (más de 3 400 peticiones) |
| Detección | 2026-10-10 (mañana), por aviso de un estudiante que vio la publicación |
| Indicador de compromiso | IP origen 203.0.113.77 (rango de documentación en el escenario) |
| Impacto | Confidencialidad: hasta ~18 000 postulantes, datos de salud y menores |
| Contención | Portal en mantenimiento; [bloqueo de IP y parche: confirmar] |
| Evidencia | Registros del servidor web, copia forense (pendiente) |
| Relación | Notificación paralela a la ANPD (ver `03-notificacion-anpd.md`) |
| Demora | Presentado fuera de las 48 h; motivo en la notificación a la ANPD |
