# 01 · Ficha de triaje — INC-20261012-acceso-indebido-hc

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Caso ficticio de prueba.

## 1. Reloj (primero)
| Dato | Valor |
|---|---|
| Toma de conocimiento | **2026-10-12, a una hora anterior a las 11:05** (hora del correo de la Jefa de Calidad; la revisión y la citación a la trabajadora ocurrieron antes) — `job1791950236356.md:7,11` |
| Hora límite 48 h (referencial, usando 11:05 como cota superior) | **2026-10-14 11:05** |
| Hora actual indicada | 2026-10-13 10:00 (-0500) |
| Tiempo transcurrido | ~22 h 55 min (como mínimo) |
| **Tiempo restante (máximo)** | **≤ 25 h 05 min**. La hora real de descubrimiento fue más temprana el 12/10, así que el plazo real vence antes de las 11:05 del 14/10 `[VERIFICAR hora exacta]` |
| Criterio | Se usa la lectura más temprana (cualquier persona de la organización, aquí Calidad) — `marco-normativo-peru.md` §2 |

## 2. Hechos en tres niveles
| Nivel | Hecho | Fuente |
|---|---|---|
| Reportado | Usuario `admision3` consultó 47 HC entre el 1 y 11/10 | `job1791950236356.md:9` |
| **Verificado** | 47 eventos `VIEW historia_clinica`, 47 HC distintas (HC-4000 a HC-4598, paso 13), del 01/10 08:00 al 10/10 15:22 | `logs/accesos-sis-hc.log:2-48` |
| **Verificado** | 8 de esas consultas son de `area=psiquiatria` (HC-4000, 4078, 4156, 4234, 4312, 4390, 4468, 4546) | `accesos-sis-hc.log:2,8,14,20,26,32,38,44` |
| **Verificado** | Origen único: IP interna 10.1.0.23; login 01/10 08:00:11; logout 11/10 17:02:44 | `accesos-sis-hc.log:1,49` |
| **Verificado** | SIS-HC: datos de salud, diagnósticos, psiquiatría, DNI, dirección; 6 200 titulares; **sin cifrado** | `inventario/activos.md:4` |
| **Verificado** | Cuentas compartidas en admisión, sin alertas de consulta, registros de 60 días | `inventario/activos.md:6` |
| Reportado, no verificable | Solo 6 de los 47 pacientes pasaron por admisión (el contexto no tiene registro de admisiones) → 41 sin justificación aparente | `job...md:9` |
| Reportado, no verificable | Entre las HC hay personas con exposición pública (una autoridad municipal y una artista local). El log solo trae IDs de HC, no nombres | `job...md:9` |
| Reportado | No hay evidencia de copia, impresión o envío; la trabajadora dijo que "era curiosidad"; fue suspendida con goce de haber | `job...md:11` |
| Supuesto | Que `admision3` fue usada solo por una persona (la cuenta puede ser compartida) | — |

### Anomalías del log a investigar
- Marcas de hora fuera de orden (p. ej. línea 10, 02/10 09:56, después de la línea 9, 02/10 16:49; también líneas 18, 26, 34, 42): posible log incompleto, reloj desajustado o manipulación `[VERIFICAR]`.
- Un solo login (01/10) y un solo logout (11/10) para 10 días, con consultas en fin de semana (04, 05, 10/10 son sábado/domingo según calendario `[VERIFICAR]`): sesión abierta durante días o log incompleto.
- Intervalos casi regulares (~67 min) entre consultas: confirmar si es patrón humano o automatizado.
- Retención de 60 días: el análisis solo cubre desde el 1/10; **no se sabe si hubo accesos anteriores**.

## 3. Clasificación
| Pregunta | Respuesta |
|---|---|
| ¿Vulneración de control? | Sí: acceso sin necesidad de servicio (principio de mínimo privilegio) |
| ¿Afecta CID? | Sí, **confidencialidad** (acceso no autorizado a datos). Integridad y disponibilidad: sin indicios |
| ¿Datos personales? | Sí, **sensibles** (salud, psiquiatría) |
| **Clasificación** | **Incidente de seguridad de datos personales (brecha)** — art. III num. 16 |
| Categoría taxonomía | **INS** Uso indebido interno (con componente INT si la cuenta es compartida/usada por otra persona) |
| Prioridad | **P2 Alta** (brecha confirmada con datos personales, reloj de 48 h corriendo) |
| Rol del reportante | La clínica es el responsable; no es encargado → la obligación de notificar es suya (art. 34) |
| Entorno digital | Sí (SIS-HC) → aplica art. 34.5 |

## 4. Acciones inmediatas sugeridas (contención)
1. Mantener `admision3` bloqueada y cerrar sesiones activas; cambiar credenciales; desactivar acceso a otros sistemas.
2. **Exportar y preservar ya los logs** (retención de 60 días) con hash y cadena de custodia.
3. Ampliar la búsqueda: accesos de `admision3` antes del 1/10 y de otras cuentas de admisión.
4. Documentar la entrevista y obtener declaración escrita sobre copias/capturas/impresiones.

Siguiente paso: `02-evaluacion-severidad.md`.
