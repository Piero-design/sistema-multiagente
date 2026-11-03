# 01 · Ficha de triaje — INC-20261009-sqli-admision

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. ESCENARIO SIMULADO (académico).
> Reporte fuente: `salidas/_entradas/job1791983364925.md` · Contexto: `demo/unsa-admision`
> No se reproducen datos personales de afectados: solo categorías y cantidades.

## 1. Reloj (primero)
| Dato | Valor |
|---|---|
| Fin de la actividad atacante (log) | 2026-10-10 03:00:12 (`logs/portal-admision-web.log:7`) |
| Toma de conocimiento | **2026-10-10, "esta mañana"** (un estudiante mostró el canal público). Hora exacta NO INDICADA. El correo al ODP es de las **11:15** (`_entradas/...md:7`) |
| Hora límite 48 h (lectura usada) | **2026-10-12 11:15** como máximo. Puede ser anterior si el conocimiento fue más temprano (se aplica la lectura más temprana, `marco-normativo-peru.md` §2) |
| Hora actual (dada por el usuario) | 2026-10-13 09:00 (-0500) |
| Tiempo transcurrido desde las 11:15 del 10-10 | ≈ 69 h 45 min |
| **Estado** | **PLAZO VENCIDO hace ≈ 21 h 45 min (como mínimo).** Notificar de inmediato y justificar la demora (art. 34.1) |

Nota: el entorno indica fecha del sistema 2026-10-14; se usó la hora entregada en la orden (2026-10-13 09:00). Si es posterior, el retraso es mayor.
Lectura alternativa: la alerta del servidor no existió ("sin bloqueo ni alerta", `log:7`), por lo que el 03:00 del 10-10 no cuenta como conocimiento; solo se deja como referencia.

## 2. Clasificación
- **Es incidente de seguridad de datos personales (brecha)** — art. III num. 16: exposición no autorizada de datos.
- **Categoría:** INT (intrusión por explotación de vulnerabilidad: inyección SQL), con extorsión (amenaza de publicar "la base completa").
- **Tipo:** Confidencialidad (confirmada). Integridad: no evidenciada (solo `SELECT`), por verificar. Disponibilidad: sin pérdida de datos; portal en mantenimiento por contención.
- **Prioridad: P1 Crítica** — datos sensibles expuestos públicamente y amenaza activa.
- **Rol de UNSA:** responsable/titular del banco de datos (portal propio S-04, `inventario/activos-y-datos.md:12`). No es encargado: la obligación de notificar es de la UNSA.

## 3. Hechos en tres niveles
| Nivel | Hecho | Fuente |
|---|---|---|
| Reportado | Muestra de 300 postulantes en canal público de mensajería con nombres, DNI, correo, celular, colegio, puntaje, dirección y, en algunos, tipo de discapacidad | reporte:9 |
| Reportado | Amenaza de publicar la base completa | reporte:9 |
| Reportado | Miles de `UNION SELECT` del viernes 22:00 al sábado 03:00; portal ya en mantenimiento | reporte:11 |
| **Verificado** | IP `203.0.113.77` inicia enumeración de esquema a las 22:01:18 (`information_schema.tables`) | `log:2` |
| **Verificado** | Extracción paginada de `postulantes` en bloques de 500 filas, respuestas 200 de 212–230 KB: dni, nombres, correo (`log:3-4`); celular, dirección, **discapacidad** (`log:5`); puntaje, colegio hasta `OFFSET 17500` (`log:6`) | log |
| **Verificado** | Más de 3 400 peticiones similares entre 22:01 y 03:00, sin bloqueo ni alerta | `log:7` |
| **Verificado** | Tabla `postulantes`: ~18 000 titulares, tres procesos, datos de salud (discapacidad) y menores; sin cifrado ni respaldo | `inventario:12,24` |
| **Contradice al reporte** | El reporte sugiere 300 registros y "no sabemos cuántos salieron". Los logs indican recorrido de toda la tabla (offset 0 a 17 500 de ~18 000): **exposición probable de ~18 000 titulares**, no 300 | `log:3-7` |
| Supuesto | Que el atacante posee ya el 100 % de la tabla; que no hubo escritura (`INSERT/UPDATE/DELETE`); que no se tocaron otras tablas (p. ej. ingresantes, 612, mismo S-04) | — |
| Pendiente | Hora exacta de conocimiento; autenticidad de la muestra; si hubo accesos previos al 09-10 21:55 | — |

Observación: los logs entregados son un extracto (línea 7 resume >3 400 peticiones); hay que obtener el log completo y la copia forense.

## 4. Datos y titulares
- Titulares: ~18 000 postulantes de tres procesos (máx. probable); posiblemente 612 ingresantes si comparten tabla/BD [VERIFICAR].
- Datos: identificación (nombre, DNI), contacto, dirección, colegio, puntaje, **dato de salud (tipo de discapacidad)**.
- Menores de edad: sí (cantidad exacta sin determinar).
- Sin cifrado en reposo y sin respaldo (`inventario:12`).

## 5. Contención ya realizada y por validar
- Reportado: portal en mantenimiento. Pendiente: confirmar que el endpoint vulnerable está realmente fuera de línea y bloquear la IP origen (medida defensiva en el borde, vía NetAndes/firewall).

## 6. Decisión del triaje
Brecha de datos personales → paso 2 (severidad) → paso 3 (notificación) → paso 4. Pendiente crítico: hora de conocimiento exacta.
