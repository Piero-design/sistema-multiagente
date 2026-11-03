# 01 · Ficha de triaje — INC-20261009-fuga-correo-admision

> BORRADOR para revisión del Oficial de Datos Personales (ODP) y del responsable de seguridad. Escenario simulado (UNSA). No se afirma que algo haya sido notificado o enviado.

## 1. Reloj (primero)

| Ítem | Valor |
|---|---|
| Hecho | Correo enviado con la lista de destinatarios en "Para" (en vez de CCO) |
| Envío del correo | 2026-10-09 13:50 (reportado) |
| **Toma de conocimiento (lectura más temprana)** | **2026-10-09 14:20**: un ingresante respondió "a todos" y la secretaria lo vio (reportado; no hay logs para verificar) |
| Lectura alternativa | 2026-10-09 16:05 (hora del correo de reporte al ODP). Es una referencia, no se usa para el cálculo |
| **Hora límite 48 h (art. 34.1)** | **2026-10-11 14:20** |
| Hora actual (dada por el usuario) | 2026-10-13 09:00 (-05:00) |
| Transcurrido | 90 h 40 min |
| **Estado** | **PLAZO VENCIDO hace 42 h 40 min.** Con la lectura de 16:05, vencido hace 40 h 55 min |

La notificación es **tardía**. Debe presentarse de inmediato con justificación de la demora (art. 34.1). La obligación permanece aunque el incidente se considere subsanado.

## 2. Clasificación

| Campo | Resultado |
|---|---|
| ¿Evento o incidente? | **Incidente**. Se vulneró un control: no se usó CCO y se difundió un archivo con datos |
| ¿Datos personales? | **Sí** |
| Clasificación | **Brecha / incidente de seguridad de datos personales** (art. III num. 16) |
| Tipo (CID) | **Confidencialidad**: comunicación no autorizada |
| Categoría | **FUG**: fuga o divulgación accidental (CC en lugar de CCO) |
| Entorno digital | Sí (correo electrónico) → aplica el CNSD (art. 34.5) |
| Prioridad | **P2 Alta**, con tratamiento urgente: plazo vencido, datos sensibles y menores, amenaza de difusión en prensa |
| Rol de quien reporta | Trabajadora interna del responsable (Oficina de Admisión). No es encargado |

## 3. Hechos por nivel de certeza

**Reportado** (`salidas/_entradas/job1791951809492.md`, líneas 9-13):
- Envío a las 13:50 a **612 ingresantes** con la lista en "Para" (l. 9, 11).
- Se adjuntó la hoja "datos para el carné": apellidos y nombres, DNI, fecha de nacimiento, escuela profesional, correo personal, celular, colegio de procedencia y la columna "condición" (discapacidad o deportista calificado). Unos 40 son menores de 18 años (l. 11).
- Un ingresante respondió a todos a las 14:20 (l. 9).
- Ya se pidió por correo que eliminen el mensaje. Se desconoce si lo hicieron (l. 13).
- Tres ingresantes respondieron molestos y uno dijo que irá a la prensa (l. 13).

**Verificado en el contexto:**
- Existe el tratamiento "Ingresantes (proceso actual)": 612 titulares, datos para el carné y condición (discapacidad, deportista), sensibles (salud), ~40 menores (`demo/unsa-base/inventario/activos-y-datos.md:25`). Coincide con el reporte en cifras y tipos de datos.
- El ODP designado es la Dra. Mariela Quispe Huamaní (`demo/unsa-base/inventario/contactos.md:5`).
- No existe procedimiento ni plazos de notificación a la ANPD, ni se definió quién notifica (`demo/unsa-base/politicas/documento-seguridad-extracto.md:5.3`, línea 19). La OTI decide si escala al ODP (l. 18).
- El plan de respuesta vigente no tiene roles, plazos ni plantillas (`demo/unsa-base/politicas/plan-respuesta-incidentes.md:3-7`).
- No hay seguro cibernético (`contactos.md:11`).

**Supuesto (por confirmar):**
- El envío se hizo desde el correo institucional S-07 (`activos-y-datos.md:15`), proveedor en nube. El reporte no lo dice.
- El archivo adjunto cubre a los 612. No se sabe si tiene más filas.
- Las respuestas "a todos" de los tres ingresantes molestos pudieron difundir el adjunto original o más datos.
- Quién recibió los datos: todos son ingresantes, pero no hay evidencia de que no hayan sido reenviados.

**Sin logs:** el contexto `unsa-base` no trae registros. No se puede verificar la hora de envío, las lecturas, los reenvíos ni las descargas. Hay que pedir la traza del correo (cabeceras y registro de mensajes) a la OTI.

## 4. Decisión del triaje
Brecha confirmada de datos personales con datos sensibles y menores → pasar al paso 2 (severidad) y al paso 3 (notificación). Notificación tardía.

## 5. Acciones inmediatas de contención sugeridas (para aprobación humana)
1. Pedir a la OTI que intente retirar o purgar el mensaje original y las respuestas de los buzones del dominio institucional. Si los destinatarios usan correo personal, no se puede retirar.
2. Verificar que el correo que pidió eliminar el mensaje usó **CCO**, para no generar una segunda fuga.
3. Preservar evidencia: cabeceras, el mensaje original, el adjunto y las respuestas (ISO/IEC 27037, control 5.28). No reenviar ni borrar el original hasta preservarlo.
4. Poner un punto único de contacto para los afectados y para la prensa (Secretaría General / ODP). Sin declaraciones improvisadas.
5. Pedir confirmación escrita de eliminación a los destinatarios, sin presionar ni amenazar.

## 6. Preguntas pendientes
- ¿Cuándo recibió el reporte el ODP realmente? El correo es del 2026-10-09 16:05. ¿Pasó por la OTI antes (documento de seguridad 5.1-5.2)? Explica en parte la demora.
- ¿Los ingresantes tienen correo institucional o el envío fue a correos personales?
- ¿Contenía el adjunto algo más (notas, teléfonos de apoderados)?
- ¿Cuántas respuestas "a todos" hubo y qué contenían?
