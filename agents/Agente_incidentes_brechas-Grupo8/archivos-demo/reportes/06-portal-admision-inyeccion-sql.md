# Reporte de incidente — Portal de Admisión, UNSA (ESCENARIO SIMULADO)

> ESCENARIO SIMULADO para fines académicos (TIF de Auditoría de Sistemas). Los nombres de oficinas, los sistemas y las cifras públicas salen de fuentes públicas de la UNSA (ver `demo/unsa-base/FUENTES.md`). El incidente, las cifras internas, los controles y las personas son inventados y no describen hechos reales de la universidad.

**De:** Desarrollo de Sistemas de la OUIS, con la Dirección Universitaria de Admisión
**Para:** Oficial de Datos Personales
**Fecha del correo:** 2026-10-10, 11:15

Esta mañana un estudiante nos mostró un canal público de mensajería donde alguien publicó una muestra de **300 postulantes** del portal de resultados de admisión y amenaza con publicar "la base completa" si no se responde. La muestra tiene nombres, DNI, correo, celular, colegio, puntaje, dirección y, en algunos casos, el tipo de discapacidad declarado para la exoneración.

En los registros del servidor web vimos miles de peticiones con `UNION SELECT` al formulario de consulta de resultados, desde el viernes 22:00 hasta el sábado 03:00. La tabla de postulantes tiene **unos 45 000 registros** de varios procesos (cada proceso ronda los 17 000 postulantes), con menores de 17 años. Ya pusimos el portal en mantenimiento. No sabemos cuántos registros salieron en total.
