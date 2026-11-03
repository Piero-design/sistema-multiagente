# 01 · Ficha de incidente (triaje) — INC-20261006-alteracion-notas-sra

> ESCENARIO SIMULADO (TIF). BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Nada de lo aquí descrito ha sido notificado ni enviado.

## 1. Reloj (primero)
| Dato | Valor | Fuente |
|---|---|---|
| Toma de conocimiento (lectura adoptada, la más temprana comprobable) | **2026-10-12 11:20** (OTI bloquea la cuenta tras revisar la auditoría) | `demo/unsa-notas/logs/sra-auditoria-notas.log:8` |
| Referencia posterior | 2026-10-12 12:00, correo de la Jefa de Registros al ODP | `salidas/_entradas/job1791983366976.md:7` |
| Lectura aún más temprana (NO CONFIRMADA) | Fecha/hora del reclamo del estudiante y de la revisión de auditoría: **no indicadas**. Si fueron antes del 12/10 11:20, la hora límite es anterior | Reporte, línea 9 |
| **Hora límite 48 h** | **2026-10-14 11:20 (-05:00)** | art. 34.1 |
| Hora actual indicada | 2026-10-13 09:00 (-05:00) | comando del usuario |
| **Tiempo restante** | **26 h 20 min** | cálculo |
| Aviso | El entorno marca como fecha del día 2026-10-14. Si fuera esa, quedaría menos tiempo (verificar). Con 14/10 09:00 quedarían 2 h 20 min | — |

## 2. Hechos en tres niveles
| Hecho | Nivel | Evidencia |
|---|---|---|
| Cuenta `rgutierrez` (docente inactiva desde 2024) inició sesión el 06/10 22:41 y cerró a las 00:41 del 07/10 | **Verificado** | `sra-auditoria-notas.log:1,6` |
| 23 modificaciones de notas, escuela de Ingeniería de Sistemas | **Verificado** (3 detalladas + 20 resumidas) | `sra-auditoria-notas.log:2-5` |
| Cambios que suben la nota (ej. 08→14, 07→13, 09→15) | **Verificado** | `sra-auditoria-notas.log:2-4` |
| Todas desde la IP 10.20.5.33 | **Verificado** | `sra-auditoria-notas.log:1-6` |
| IP corresponde a un equipo de la secretaría de la escuela | **Reportado** (el log solo muestra IP; no hay inventario IP→equipo) | Reporte, línea 9 |
| Fuera de horario laboral | **Verificado** (22:41–00:41) | log |
| Cuenta de docente jubilado nunca dada de baja | **Verificado** (el documento de seguridad confirma que no hay procedimiento de baja) | `documento-seguridad-extracto.md:4.4`; `activos-y-datos.md:31` |
| Cuenta bloqueada el 12/10 11:20 | **Verificado** | `sra-auditoria-notas.log:8` |
| Acta firmada con 08 vs. sistema con 14 | **Reportado** (no hay copia del acta en el contexto) | Reporte, línea 9 |
| Hubo venta de notas o favores | **Supuesto** (sospecha de la reportante) | Reporte, línea 11 |
| Cambios en otras escuelas | **Desconocido**: el log del contexto solo cubre esta cuenta | Reporte, línea 11 |
| Consulta/extracción de datos de otros estudiantes | **Desconocido**: "solo se auditan modificaciones" | `sra-auditoria-notas.log:7` |
| El jefe de secretaría "no sabe nada" | **Reportado** (dato a investigar, no concluyente) | Reporte, línea 11 |

Contradicciones: ninguna con el contexto. El log respalda el reporte.

## 3. Clasificación
- **¿Evento o incidente?** Incidente: se vulneró el control de acceso y se alteró información.
- **¿Datos personales?** Sí: notas, identificación y situación académica de estudiantes (banco "Estudiantes y egresados", S-01; ~28 000 activos y 61 000 históricos; ~900 activos son menores) — `activos-y-datos.md:9,22`.
- **Tipo (CID):** Integridad (confirmada). Confidencialidad: **no descartada** (sin logs de lectura). Disponibilidad: sin afectación conocida.
- **Categorías (taxonomía):** ALT (alteración de datos) + INT (uso de cuenta no autorizada) + INS (posible uso indebido interno).
- **Definición art. III num. 16:** "alteración ilícita de los datos personales" → **brecha de datos personales**.
- **Prioridad:** **P2 Alta** (brecha confirmada con datos personales, reloj de 48 h corriendo).
- **Rol de la UNSA:** responsable del banco de datos (no es encargado) → la obligación de notificar es suya (art. 34).
- **Entorno digital:** sí (SRA) → aplica el art. 34.5 (CNSD).

## 4. Alcance conocido y desconocido
- Afectados confirmados: **23 titulares** (estudiantes de una escuela), más las notas ya alteradas en el SRA.
- Alcance potencial: la cuenta pudo consultar o modificar otros registros. Los logs solo auditan modificaciones y se conservan 60 días (`activos-y-datos.md:33`).
- Los registros del 06–07/10 caducan hacia el **2026-12-05** [VERIFICAR el cálculo con OTI]: preservarlos ya.

## 5. Acciones inmediatas (mismo día)
1. Conservar copia íntegra del log de auditoría del SRA y registrar hash (ISO/IEC 27037).
2. Aislar y preservar el equipo asociado a 10.20.5.33 sin apagarlo ni reinstalarlo hasta decidir con OTI.
3. Revisar en el SRA todas las modificaciones de los últimos 60 días en todas las escuelas, y todas las cuentas inactivas y compartidas.
4. Reunir las actas firmadas (S-02) de los cursos afectados.
5. Decidir la notificación a la ANPD antes de la hora límite (ver `02-evaluacion-severidad.md`).

## 6. Pendientes críticos
- Fecha/hora del reclamo del estudiante y de la revisión del log (define la hora de toma de conocimiento).
- Quién tuvo acceso físico al equipo y las credenciales de la cuenta.
- Qué otros datos se pudieron consultar con esa cuenta (perfil de permisos).
