# Aviso al Centro Nacional de Seguridad Digital (CNSD) — INC-20260929-ransomware-clinica

**Destinatario:** Centro Nacional de Seguridad Digital (CNSD), para el Registro Nacional de Incidentes de Seguridad Digital
**Fundamento:** art. 34.5 del D.S. N.° 016-2024-JUS; D.U. N.° 007-2020 (Marco de Confianza Digital)
**Motivo:** el incidente ocurrió en y mediante el entorno digital, así que se reporta al CNSD además de a la ANPD.
**Canal:** `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia y si el mismo formulario cubre ambos reportes]`
**Plazo de referencia:** el mismo que el de la ANPD (hasta el 2026-10-01 07:15) `[VERIFICAR plazo específico del CNSD]`

## Contenido técnico (igual al de la notificación a la ANPD)
- **Organización:** Clínica San Gabriel S.A.C., Arequipa. RUC `[COMPLETAR]`. Sector salud (privado).
- **Contacto:** `[Oficial de Datos Personales / responsable de seguridad: nombre, correo, teléfono]`
- **Tipo de incidente:** código malicioso, ransomware con extorsión (amenaza de publicar datos). Vector probable: correo de phishing con adjunto ("factura pendiente"), en investigación.
- **Cronología:** alerta del antivirus el 28/09/2026 23:50; cifrado detectado el 29/09/2026 07:15.
- **Activos afectados:** servidor de archivos, servidor de base de datos del sistema de historias clínicas y 6 estaciones de trabajo. Extensión de los archivos cifrados: `.lck`. El respaldo local está en estado desconocido.
- **Indicadores de compromiso:** `[COMPLETAR: hash del adjunto, remitente y dominio del correo, nombre de la nota de rescate, dirección de la billetera BTC, sitio de filtración mencionado]`. La dirección de la billetera y el sitio se informan solo como indicadores, sin interactuar con ellos.
- **Datos personales afectados:** ~18 000 pacientes; datos de identificación, contacto, salud (sensibles) y seguro.
- **Impacto operativo:** sistema de historias clínicas no disponible; atención en contingencia en papel.
- **Medidas:** las mismas de la sección F de `03-notificacion-anpd.md`.
- **Exfiltración:** en investigación.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
