# Reporte de incidente — Oficina Universitaria de Informática y Sistemas, UNSA (ESCENARIO SIMULADO)

> ESCENARIO SIMULADO para fines académicos (TIF de Auditoría de Sistemas). Los nombres de oficinas, los sistemas y las cifras públicas salen de fuentes públicas de la UNSA (ver `demo/unsa-base/FUENTES.md`). El incidente, las cifras internas, los controles y las personas son inventados y no describen hechos reales de la universidad.

**De:** Jefatura de la Oficina Universitaria de Informática y Sistemas (OUIS)
**Para:** Oficial de Datos Personales
**Fecha del correo:** 2026-10-11 (domingo), 08:00

Hoy a las 06:40 el personal de guardia del Centro de Datos encontró caído el Sistema Académico (SISACAD: libretas, notas y sistema docente) y la Matrícula en línea. En la pantalla de los servidores aparece una nota que dice que los archivos fueron cifrados y que, si la Universidad no paga en 72 horas, publicarán "las notas y datos de todos los estudiantes". Mañana lunes se abre la matrícula del semestre.

Lo que sabemos:
- Los servidores del SISACAD (aplicación y base de datos) y la carpeta compartida de actas escaneadas tienen archivos con extensión `.lck`.
- La base guarda estudiantes y egresados (más de 24 000 activos y el histórico): nombres, DNI, fecha de nacimiento, domicilio, correo, teléfono, escuela profesional, notas y situación académica.
- El antivirus envió una alerta a la bandeja del área de seguridad a las 05:12 y ayer a las 21:14 la VPN generó un aviso de "inicio de sesión inusual"; nadie los revisó porque era fin de semana.
- La copia de seguridad semanal está en un NAS conectado todo el tiempo a la red. No sabemos si también se cifró.
- Desconecté el servidor de la red. Las demás máquinas siguen encendidas.
- No sabemos si sacaron información antes de cifrar.

¿Qué hacemos? ¿Hay que avisar a alguien? La matrícula no puede esperar.
