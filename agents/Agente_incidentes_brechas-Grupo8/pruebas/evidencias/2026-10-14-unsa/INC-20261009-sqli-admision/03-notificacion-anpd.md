# 03 · Notificación a la ANPD — BORRADOR (NO ENVIADO)

> Para revisión y aprobación del Oficial de Datos Personales. Canal: formulario de reporte de incidentes `https://reporte.cnsd.gob.pe/home/minjus` [VERIFICAR vigencia]. Contenido según art. 34.2 D.S. 016-2024-JUS.

**Asunto:** Notificación de incidente de seguridad de datos personales — Universidad Nacional de San Agustín (UNSA) — Portal de Admisión

**Responsable del tratamiento:** Universidad Nacional de San Agustín (simulado).

## 0. Justificación de la demora (art. 34.1)
La UNSA tomó conocimiento del incidente la mañana del 2026-10-10 [hora exacta: COMPLETAR]. Esta notificación se presenta fuera del plazo de 48 horas. Motivos: [COMPLETAR por el ODP; p. ej., la institución no cuenta con procedimiento ni responsable definido para notificar (documento de seguridad 5.3), lo que retrasó el escalamiento, y se priorizó la contención y el análisis de los registros]. Sustento: línea de tiempo y correo de reporte del 2026-10-10 11:15, adjuntables. [El ODP y Asesoría Jurídica decidirán cómo redactar el motivo; no se debe afirmar nada que no sea cierto.]

## 1. Naturaleza del incidente (34.2 num. 1)
- Tipo: acceso no autorizado por explotación de una vulnerabilidad de inyección SQL en el formulario de consulta de resultados del portal de admisión; vulneración de la confidencialidad.
- Fechas: actividad del 2026-10-09 22:01 al 2026-10-10 03:00 (más de 3 400 peticiones desde una sola IP). Un tercero publicó una muestra de 300 registros en un canal público de mensajería y amenaza con publicar el resto.
- Datos: nombres, DNI, correo, celular, dirección, colegio, puntaje y **tipo de discapacidad declarado** (dato de salud, en algunos casos).
- Titulares: hasta **~18 000 postulantes** de tres procesos de admisión, incluidos **menores de edad** (cantidad exacta por determinar). 300 confirmados como publicados según el reporte. Los registros del servidor indican recorrido de la tabla completa.
- Supuestos del art. 34.1 que se cumplen: datos sensibles, gran número de personas, posible perjuicio a otros derechos.

## 2. Punto de contacto (34.2 num. 2)
Dra. Mariela Quispe Huamaní, Oficial de Datos Personales — odp@unsa.example — 054-555-0301 / 999 000 301.

## 3. Posibles consecuencias (34.2 num. 3)
Discriminación o estigmatización por discapacidad; suplantación de identidad y fraude; phishing y acoso dirigidos a postulantes y menores; extorsión; afectación psicológica de los titulares.

## 4. Medidas adoptadas y propuestas (34.2 num. 4)
Adoptadas: portal puesto en mantenimiento (reportado).
En curso/propuestas [confirmar cuáles están ejecutadas antes de enviar]: bloqueo de la IP origen; corrección de la consulta vulnerable (consultas parametrizadas) y revisión de las demás; preservación de logs y copia forense del servidor; solicitud de retiro del contenido al canal de mensajería; rotación de credenciales de la base de datos; comunicación a los titulares (art. 34.3); aviso al CNSD (34.5); revisión de cifrado y respaldos; análisis para determinar el alcance exacto.
Se informará cualquier avance relevante. La notificación permanece vigente aunque el incidente se considere contenido.

## 5. Pendientes a completar antes de enviar
- Hora exacta de toma de conocimiento y motivo de la demora.
- Número exacto de titulares y menores.
- Aprobación del ODP y de Asesoría Jurídica.
