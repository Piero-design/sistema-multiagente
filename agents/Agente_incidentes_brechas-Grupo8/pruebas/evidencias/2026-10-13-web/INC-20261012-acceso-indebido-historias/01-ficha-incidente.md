# 01 · Ficha de triaje — INC-20261012-acceso-indebido-historias

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Caso ficticio de pruebas. Nada ha sido notificado ni enviado.

## 1. Reloj
| Dato | Valor |
|---|---|
| Toma de conocimiento (lectura temprana) | 2026-10-12, **antes de las 11:05** (hora del correo de la Jefa de Calidad; la hora exacta de la revisión es `[VERIFICAR]`) |
| Hora límite 48 h (máxima) | **2026-10-14 11:05 (-05:00)**; será más temprana si la revisión empezó antes de las 11:05 |
| Hora actual indicada | 2026-10-13 10:00 |
| Tiempo restante | **≤ 25 h 05 min** (planificar como si fueran ~24 h) |
| Lectura más estricta (referencia) | Los accesos ocurrieron del 01 al 11/10 sin alertas. El sistema no tiene alertas ni monitoreo, y eso es una brecha de control, no una toma de conocimiento. No adelanta el reloj, pero conviene registrarlo. |
| Nota sobre el ID | Se usó la fecha de detección (2026-10-12). Los accesos son del 2026-10-01 al 2026-10-11. |

## 2. Hechos (nivel: todos **reportados**; sin contexto verificable)
- Reporta la Jefa de Calidad, Clínica Santa Rosa S.A. (Arequipa), el 2026-10-12 11:05, al Oficial de Datos Personales. Revisión mensual de accesos al sistema de historias clínicas.
- Usuario `admision3` (técnica administrativa de admisión) consultó **47 historias clínicas** entre el 01 y el 11/10/2026. Solo 6 de esos pacientes pasaron por admisión en esos días, así que **~41 consultas no tienen justificación aparente**.
- Entre las historias hay las de una regidora municipal, una cantante local y pacientes de psiquiatría.
- No hay evidencia de copia, impresión ni envío. Esto **no está verificado**: no se revisó exportación ni impresión.
- La persona dijo que "era curiosidad". El jefe la suspendió con goce de haber. El sistema no tiene alertas.

**Supuestos:** que el acceso fue solo lectura en pantalla; que no hubo otros usuarios con el mismo patrón; que las credenciales de `admision3` no fueron compartidas o robadas (la persona admitió el acceso).

## 3. Clasificación
| Pregunta | Respuesta |
|---|---|
| ¿Se vulneró un control? | Sí. Acceso sin necesidad de servicio (principio de mínimo privilegio y necesidad de conocer). |
| ¿Se afectó la C-I-D? | **Confidencialidad** (integridad y disponibilidad: sin indicios, `[VERIFICAR]` en logs). |
| ¿Hay datos personales? | Sí, y **sensibles** (salud, incluida salud mental). |
| Categoría | **INS**, uso indebido interno. |
| Clasificación | **Incidente de seguridad de datos personales (brecha)**, art. III num. 16 ("comunicación o exposición no autorizada"). |
| Prioridad | **P2 Alta** (datos sensibles, reloj de 48 h corriendo). Si aparece exfiltración o difusión, pasa a P1. |
| Rol del reportante | La clínica es el responsable. No hay encargado, así que la obligación de notificar es propia (art. 34). |
| Entorno digital | Sí (sistema de historias clínicas). |

## 4. Acciones inmediatas de contención (propuestas)
1. **Preservar evidencia ya:** exportar y bloquear el reporte de accesos completo de `admision3` y del sistema (art. 46.3), con hash y cadena de custodia (ISO/IEC 27037).
2. **Deshabilitar** las credenciales y sesiones de `admision3`; la suspensión laboral no desactiva la cuenta.
3. Revisar si otros usuarios tienen el mismo patrón, y buscar exportaciones, impresiones o capturas.
4. Recoger por escrito la declaración de la persona (con RR. HH./legal) y pedirle que confirme que no copió ni compartió nada.
5. Reservar el expediente: acceso restringido a Oficial de Datos, Seguridad, Legal y Dirección.

## 5. Pendientes críticos
- Hora exacta en que Calidad vio el reporte de accesos.
- Lista de las 47 historias, con la segmentación sensible, psiquiatría y personas públicas.
- Datos de contacto del Oficial de Datos Personales.
