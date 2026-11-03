# Aviso de incidente de seguridad digital — INC-20260929-ransomware-clinica

**Destinatario:** Centro Nacional de Seguridad Digital (CNSD) — para el **Registro Nacional de Incidentes de Seguridad Digital**
**Fundamento:** art. 34.5 del Reglamento de la Ley N.° 29733 (D.S. N.° 016-2024-JUS) y D.U. N.° 007-2020 (Marco de Confianza Digital). El incidente se desarrolló en y mediante el entorno digital; se notifica además a la ANPD.
**Tipo de aviso:** ☒ Inicial ☐ Complementario
**Canal:** `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace y si el CNSD exige un canal o formulario propio]`

## 1. Entidad que reporta
- **Organización:** Clínica San Gabriel S.A.C. (Arequipa) — RUC `[COMPLETAR]` — sector salud (privado).
- **Punto de contacto:** Oficial de Datos Personales `[COMPLETAR: nombre, correo, teléfono]`; contacto técnico: Jefe de TI `[COMPLETAR]`.

## 2. Cronología
- Alerta del antivirus (adjunto malicioso abierto en PC de facturación), no revisada: 2026-09-28 23:50.
- Ocurrencia estimada del cifrado: entre 2026-09-28 23:50 y 2026-09-29 07:15.
- Detección / toma de conocimiento: 2026-09-29 07:15.
- Fecha y hora de este aviso: `[COMPLETAR]`.

## 3. Descripción técnica
- **Categoría:** código malicioso — *ransomware* con probable doble extorsión (cifrado + amenaza de publicación). Vector probable: phishing con adjunto ("factura pendiente") — inferencia en investigación.
- **Activos afectados:** servidor de base de datos del sistema de historias clínicas (cifrado, extensión `.lck`); servidor de archivos (cifrado); 6 estaciones de trabajo con nota de rescate; disco de respaldo conectado permanentemente al servidor (estado desconocido); correo institucional (vector).
- **Demanda del atacante:** 3 BTC en 72 h, con amenaza de publicar la base de pacientes en un sitio web.
- **Impacto:** disponibilidad (confirmada, servicio de historias clínicas caído; atención en papel), integridad (datos cifrados por un tercero), confidencialidad (probable, extracción no confirmada).
- **Indicadores de compromiso:** `[COMPLETAR: remitente y dominio del correo, hash del adjunto, extensión .lck, texto de la nota de rescate, direcciones de pago/contacto del atacante, IP de salida sospechosas]`.

## 4. Datos personales involucrados
Identificación (nombres, DNI, fecha de nacimiento), contacto (teléfono, dirección), **datos sensibles de salud** (diagnósticos, resultados de laboratorio) y datos del seguro de aproximadamente **18 000 pacientes** (estimado; posible inclusión de menores). Contenido del servidor de archivos en inventario.

## 5. Posibles consecuencias
Publicación de datos de salud, extorsión a pacientes, suplantación de identidad y fraude de seguros, phishing dirigido haciéndose pasar por la clínica y afectación de la continuidad de la atención de salud (posible pérdida de hasta 3 semanas de registros).

## 6. Medidas adoptadas y propuestas
- **Adoptadas:** desconexión de red del servidor; contingencia en papel; PC afectadas encendidas para preservar evidencia en memoria.
- **Propuestas:** aislamiento de las 6 PC y de todo equipo comprometido; custodia del disco de respaldo; restablecimiento de credenciales privilegiadas y de la cuenta de facturación; bloqueo del remitente y búsqueda del correo en otros buzones; preservación de logs (antivirus, correo, servidores, firewall) y análisis de tráfico saliente; erradicación y recuperación desde respaldo limpio verificado; monitoreo de sitios de filtración.
- No se ha pagado el rescate ni contactado al atacante.

## 7. Información pendiente
Confirmación de exfiltración; estado del respaldo; alcance exacto (titulares, menores, servidor de archivos); participación de proveedores con acceso remoto; IoC completos; causa raíz.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
