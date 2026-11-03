# Notificación de incidente de seguridad de datos personales — INC-20260929-ransomware-clinica

**Destinatario:** Autoridad Nacional de Protección de Datos Personales (ANPD) — Ministerio de Justicia y Derechos Humanos
**Fundamento:** art. 34 del Reglamento de la Ley N.° 29733 (D.S. N.° 016-2024-JUS)
**Tipo de notificación:** ☒ Inicial ☐ Complementaria ☐ Única (la investigación sigue; se anuncia una complementaria)
**Canal:** formulario de reporte de incidentes `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace]`

## A. Datos del responsable
- **Titular del banco de datos / responsable del tratamiento:** Clínica San Gabriel S.A.C. — RUC: `[COMPLETAR]`
- **Banco(s) de datos afectado(s):** Historias clínicas de pacientes; resultados de laboratorio e imágenes; datos de seguro; facturación; personal. Código de inscripción: `[COMPLETAR]`
- **Encargado del tratamiento involucrado (si aplica):** en investigación. Proveedor de software de la HCE: SoftSalud S.A.C. `[VERIFICAR si es encargado]`

## B. Punto de contacto (art. 34.2 num. 2)
- **Oficial de Datos Personales:** Dra. Lucía Paredes Quispe — odp@clinicasangabriel.example — 054-555-0101 / 999 000 101 (`demo/clinica-san-gabriel/inventario/contactos.md:5`)

## C. Cronología
- Ocurrencia: inicio del acceso no autorizado el 2026-09-28 a las 23:48; cifrado de servidores el 2026-09-29 entre 07:14 y 07:30.
- Toma de conocimiento: el personal detectó el cifrado el 2026-09-29 a las 07:15; el antivirus había emitido una alerta a TI el 2026-09-28 a las 23:50 que no fue atendida. Para el cómputo del plazo se considera la fecha más temprana.
- Notificación: `[COMPLETAR fecha y hora de envío]` — ☐ Dentro de 48 h (límite 2026-09-30 23:50) ☐ Fuera de plazo (ver sección H)

## D. Naturaleza del incidente (art. 34.2 num. 1)
- **Descripción:** Ataque de ransomware con intrusión previa. Un correo con archivo adjunto malicioso fue abierto en una estación de facturación; a partir de ella el atacante accedió a los servidores de historias clínicas y de archivos, creó una cuenta con privilegios de administrador, generó copias de la base de datos y de resultados de laboratorio, y se registró una salida de unos 3,4 GB de datos hacia una dirección externa (probable exfiltración, contenido en verificación). Luego cifró ambos servidores y el disco de respaldo, y exige un pago en criptomonedas bajo amenaza de publicar "la base de pacientes".
- **Tipo:** confidencialidad (probable), integridad y disponibilidad.
- **Categorías de datos afectados:** identificación y contacto (nombres, DNI, fecha de nacimiento, teléfono, dirección); **datos sensibles de salud** (diagnósticos, evolución, recetas, resultados de laboratorio, imágenes diagnósticas); datos de seguro; datos de facturación; datos de personal, incluidos certificados médicos.
- **Categorías y número aproximado de titulares:** pacientes, aprox. 18 000, de los cuales aprox. 3 100 son menores de edad; aprox. 6 500 con datos de seguro; aprox. 12 000 con datos de facturación; 74 trabajadores (afectación de disponibilidad; exfiltración en investigación).
- **Entorno digital:** Sí — reportado también al CNSD: `[COMPLETAR tras el envío de 03-aviso-cnsd.md]`

## E. Posibles consecuencias (art. 34.2 num. 3)
- Publicación de información de salud, con riesgo de discriminación, estigma y daño personal.
- Suplantación de identidad, fraude y estafas telefónicas con datos reales de pacientes y de sus seguros.
- Extorsión a titulares individuales.
- Riesgo para la continuidad de la atención por falta de acceso a las historias clínicas.
- Riesgo particular para los menores de edad.

## F. Medidas adoptadas y propuestas (art. 34.2 num. 4)
| Medida | Estado (adoptada/propuesta) | Fecha |
|---|---|---|
| Desconexión de red del servidor afectado | Adoptada | 2026-09-29 (hora `[COMPLETAR]`) |
| Atención de pacientes con registros en papel | Adoptada | 2026-09-29 |
| Aislamiento de las estaciones comprometidas y del segundo servidor, sin apagarlos | Propuesta | `[COMPLETAR]` |
| Deshabilitar la cuenta creada por el atacante, cambiar credenciales administrativas y de base de datos, bloquear direcciones externas identificadas | Propuesta | `[COMPLETAR]` |
| Preservación de evidencia (registros, imágenes de disco y memoria, disco de respaldo) con cadena de custodia | Propuesta | `[COMPLETAR]` |
| Análisis forense para determinar qué datos salieron | Propuesta | `[COMPLETAR]` |
| Recuperación en equipos limpios; autenticación multifactor y respaldos aislados | Propuesta | `[COMPLETAR]` |
| Comunicación a los titulares afectados | Propuesta | Ver sección G |
| Denuncia ante la autoridad policial competente | Propuesta `[VERIFICAR]` | `[COMPLETAR]` |

## G. Comunicación a los titulares (art. 34.3)
☒ Se comunicará el `[COMPLETAR fecha, límite 48 h]` por `[COMPLETAR: SMS, correo, aviso en la web y en recepción]` (borrador en `03-comunicacion-titulares.md`) ☐ No corresponde (art. 34.4): no aplica, el incidente no está superado.

## H. Motivos de la demora (solo si se notifica después de 48 h)
- No aplica si se envía antes del 2026-09-30 23:50. Si se superara el plazo, indicar aquí los motivos y el sustento probatorio. `[COMPLETAR solo si corresponde]`

## I. Información pendiente (para notificación complementaria)
- Confirmación de qué datos fueron efectivamente extraídos y el número real de titulares afectados.
- Vector exacto y alcance del acceso del atacante; si otros sistemas o proveedores fueron alcanzados.
- Posibilidad y plazo de recuperación de los datos.
- Si el atacante publicó información y dónde.
- Fecha de la comunicación a los titulares y notificación al CNSD.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*

## Verificación de contenido (art. 34.2) — no se envía
| Elemento | ¿Incluido? | Sección |
|---|---|---|
| 1. Naturaleza, tipos de datos y número aproximado de titulares | Sí | D |
| 2. Nombre y contacto del Oficial de Datos Personales | Sí | B |
| 3. Posibles consecuencias | Sí | E |
| 4. Medidas adoptadas o propuestas | Sí | F |
| Motivos de la demora (si hubiera) | Condicional | H |
