# 03 · Notificación a la ANPD — BORRADOR (no enviada)

> BORRADOR para aprobación del Oficial de Datos Personales. **No se afirma que haya sido enviada.** Canal: formulario `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace]`.
> ESCENARIO SIMULADO: datos y cifras ficticios.

**Asunto:** Notificación de incidente de seguridad de datos personales (art. 34 del D.S. 016-2024-JUS). Universidad Nacional de San Agustín (UNSA). Ref. INC-20261011-ransomware-sra.

**Fecha de notificación:** 2026-10-13 `[completar con la hora real de envío]`

## 1. Justificación de la demora (art. 34.1)
La UNSA tomó conocimiento del incidente el 2026-10-11 a las 06:40. El plazo de 48 horas venció el 2026-10-13 a las 06:40. Esta notificación se presenta con una demora de `[X]` horas por las siguientes razones, con sustento probatorio disponible:
- La UNSA no tenía un procedimiento ni un responsable definidos para notificar a la ANPD (documento de seguridad, sección 5.3). `[Aprobar si se incluye esta admisión: consultar con Asesoría Legal]`
- Durante el fin de semana la prioridad fue contener el ataque, aislar los servidores y determinar el alcance. `[Ajustar a lo realmente ocurrido]`
- Se acompañan registros de VPN, firewall, antivirus, auditoría y respaldos que sustentan la cronología.

Se hace constar que una alerta del antivirus llegó a las 05:12 del 2026-10-11 a una bandeja de seguridad no atendida fuera del horario de oficina. La UNSA no la consideró toma de conocimiento por sí sola `[VERIFICAR criterio con Asesoría Legal]`.

## 2. Naturaleza del incidente (art. 34.2.1)
- **Tipo:** ransomware con doble extorsión (cifrado de datos y amenaza de publicarlos). Afecta **disponibilidad** (total) y **confidencialidad** (probable).
- **Vector probable:** acceso por VPN con credenciales de una cuenta docente comprometida tras un ataque de fuerza bruta, escalamiento a administrador y creación de una cuenta persistente.
- **Sistemas afectados:** Sistema de Registro Académico (aplicación y base de datos), carpeta de actas escaneadas y el servidor de respaldos (NAS). Todos con archivos cifrados.
- **Exfiltración:** se registró la salida de 5,1 GB hacia una IP externa tras exportar la BD y las actas. El contenido exacto no está confirmado.
- **Inicio estimado:** 2026-10-10 20:50. **Cifrado:** 2026-10-11 05:10-05:30. **Conocimiento:** 2026-10-11 06:40.
- **Tipos de dato:** nombres, DNI, fecha de nacimiento, domicilio, correo, teléfono, escuela profesional, notas y situación académica; actas escaneadas.
- **Titulares afectados (aproximado):** 28 000 estudiantes activos y 61 000 egresados e históricos (hasta 89 000), incluidos unos 900 menores de edad. No se ha confirmado la presencia de datos sensibles `[VERIFICAR actas]`.
- **Fundamento de la notificación:** art. 34.1 (gran volumen, gran número de personas y posible perjuicio a otros derechos).

## 3. Punto de contacto (art. 34.2.2)
Dra. Mariela Quispe Huamaní, Oficial de Datos Personales. odp@unsa.example · 054-555-0301 / 999 000 301.

## 4. Posibles consecuencias (art. 34.2.3)
Suplantación de identidad y fraude, phishing dirigido, publicación de notas y datos de estudiantes (incluidos menores), acoso o daño reputacional, y pérdida de continuidad académica.

## 5. Medidas adoptadas o propuestas (art. 34.2.4)
**Adoptadas (reportadas):** desconexión de la red del servidor afectado.
**Propuestas (pendientes de aprobación y ejecución):**
1. Aislar todos los equipos del segmento; revocar `svc_mant`, la cuenta `jperez.docente` y las credenciales de administrador; rotar contraseñas.
2. Bloquear la IP 203.0.113.50 y el destino 198.51.100.200; suspender la VPN o exigir MFA y bloqueo por intentos.
3. Preservar evidencia con cadena de custodia (discos, logs, imágenes forenses) antes de restaurar.
4. Evaluar la recuperación desde otras fuentes; no se ha considerado el pago del rescate.
5. Comunicar a los titulares (borrador adjunto) y avisar al CNSD.
6. Monitorear la publicación de los datos y coordinar con Asesoría Legal las acciones correspondientes `[VERIFICAR]`.
7. Informar a la ANPD cualquier novedad (confirmación de exfiltración, alcance en otros sistemas).

**Anexos propuestos:** línea de tiempo, extractos de logs, inventario de datos, borrador de comunicación a titulares.

Firma: `[Oficial de Datos Personales / representante legal de la UNSA]`
