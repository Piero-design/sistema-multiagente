# 01 · Ficha de triaje — INC-20261013-acceso-indebido-sigep

> ESCENARIO SIMULADO (fines académicos). BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad.
> Nota sobre el ID: la fecha 20261013 es la de toma de conocimiento y registro. El acceso indebido ocurrió del 05 al 12/10/2026.

## 1. Reloj (primero)

| Dato | Valor |
|---|---|
| Toma de conocimiento (reportada) | 2026-10-13, "esta mañana", en la Escuela de Posgrado. El correo se envió a las **10:20**. La hora exacta del hallazgo no consta `[VERIFICAR]`. |
| Hora de referencia usada | 2026-10-13 10:20 (la más tardía posible; el hallazgo pudo ser antes) |
| **Hora límite (48 h, art. 34.1)** | **2026-10-15 10:20 como máximo.** Si el hallazgo fue antes, la hora límite es anterior. |
| Hora actual (dada por el usuario) | 2026-10-13 11:20 (-05:00) |
| **Tiempo restante** | **47 h como máximo** (han pasado 1 h desde el correo). |
| Lectura más estricta | La política dice que los accesos se revisan semanalmente (`politicas/politica-posgrado.md:7`). El acceso empezó el 05/10. Si se considera que la Escuela debió detectarlo antes, el reloj podría contarse desde antes `[VERIFICAR con Asesoría Jurídica]`. Se usa la lectura más temprana documentada, que es el 13/10. |
| Fecha del entorno | El entorno del agente indica 2026-10-14, y el usuario indicó 2026-10-13 11:20. Se usó la del usuario. Si en realidad es el 14, el tiempo restante es menor. Verificar. |

## 2. Clasificación

- **Incidente de seguridad de datos personales (brecha)**, art. III num. 16: exposición/comunicación no autorizada de datos personales.
- **Categoría:** INS, uso indebido interno. Se vincula también con INT/control de acceso por privilegios excesivos.
- **Tipo:** confidencialidad. Integridad y disponibilidad no están afectadas según lo reportado.
- **Prioridad:** **P2 Alta** (brecha confirmada con datos personales y reloj de 48 h corriendo). Pasa a **P1** si se confirma que se copiaron datos, o si la cuenta sigue activa y se detecta acceso en curso.
- **Rol de la UNSA:** responsable del tratamiento. No es encargado, así que la obligación de notificar es suya (arts. 34 y 36).

## 3. Hechos en tres niveles

### Verificado en el contexto
| Hecho | Fuente |
|---|---|
| 85 consultas `VIEW expediente` de la cuenta `secretaria2`, con 85 IDs distintos (PG-2100 a PG-2688). 68 de maestría y 17 de doctorado. | `logs/accesos-sigep.log:2-86` |
| Periodo del 2026-10-05 08:00 al 2026-10-12 16:40 (última consulta). Cierre de sesión el 12/10 17:31. | `logs/accesos-sigep.log:2`, `:82`, `:87` |
| Consultas por día: 05/10: 11, 06/10: 11, 07/10: 10, 08/10: 11, 09/10: 11, 10/10: 10, 11/10: 11, 12/10: 10. | `logs/accesos-sigep.log:2-86` |
| El registro indica que no hay descargas ni exportaciones, solo consultas en pantalla. | `logs/accesos-sigep.log:88` |
| La política dice que la secretaria registra matrículas y que los expedientes completos los ve la coordinación académica. | `politicas/politica-posgrado.md:3` |
| El sistema no impide que la secretaria abra expedientes completos. No hay alertas de consulta masiva. | `politicas/politica-posgrado.md:4`, `inventario/inventario-posgrado.md:10` |
| SIGEP no está cifrado. Los respaldos están en el mismo servidor. | `inventario/inventario-posgrado.md:5` |
| SIGEP tiene 1 450 maestrandos y doctorandos y 320 docentes asesores. | `inventario/inventario-posgrado.md:5` |
| Hay constancias de aptitud médica (salud, dato sensible) de unos 210 postulantes. | `inventario/inventario-posgrado.md:5`, `:8` |
| No hay menores. | `inventario/inventario-posgrado.md:8` |
| No existe procedimiento de notificación a la ANPD ni persona designada. | `politicas/politica-posgrado.md:8` |
| Los registros de acceso se conservan 45 días. | `inventario/inventario-posgrado.md:10` |

### Anomalías del log (por aclarar antes de concluir)
1. **Fecha y hora.** El log dice que la sesión se abrió el 05/10 a las 08:12:03 (`:1`). La primera consulta es a las 08:00:00 (`:2`), es decir, antes del inicio de sesión.
2. **Orden del tiempo.** Dentro de cada día las horas no van en orden cronológico (ej. `:10` a las 16:28 y `:11` a las 08:39). Esto sugiere que el log fue reordenado o tiene problemas de reloj, y afecta su valor probatorio.
3. **Una sola sesión.** Hay un único `login` (05/10) y un único `logout` (12/10) para 8 días. Puede ser una sesión abierta durante una semana o un registro incompleto.
4. **Fines de semana.** Se registran 21 consultas el sábado 10/10 y el domingo 11/10. Las del sábado y el domingo (10 y 11) no coinciden con un horario administrativo normal `[VERIFICAR si hubo trabajo ese fin de semana]`.
5. **Ritmo regular.** Cerca de 10-11 consultas por día, con IDs espaciados de 7 en 7. Parece un patrón sistemático o automatizado, y no una consulta casual. Es un indicio, no una conclusión.
6. **Un solo origen.** Solo se registra una IP (10.30.2.15), en el login. Las consultas no llevan IP.
7. **Ausencia de descargas.** El log dice que no hay descargas, pero la directora aclara que "tampoco hay registros de descargas". Puede significar que no ocurrieron o que el sistema no las registra. Esto debe verificarse (art. 46.3 exige registrar exportación e importación).

### Reportado, sin verificar en el contexto
- Los expedientes tienen nombre, DNI, correo, teléfono, grado y programa, tema y asesor de tesis, y constancias médicas de algunos postulantes (`salidas/_entradas`, líneas 9-11). El inventario confirma las categorías de datos. **No confirma cuántas de las 85 personas tienen constancia médica.**
- Entre los consultados hay docentes de la universidad y dos autoridades (el log no identifica titulares).
- La secretaria dijo que "era curiosidad". No consta acta ni declaración escrita.
- No hay evidencia de que copiara o enviara información.
- La cuenta **no ha sido suspendida** todavía.

### Supuesto
- La persona que usó `secretaria2` es la titular de la cuenta. Podría ser una cuenta compartida o comprometida. Su declaración apunta a que es ella.
- Tomando el porcentaje general (210 de 1 450), se esperarían unos 12 expedientes con constancia médica entre los 85. Es solo una estimación, y el número real debe contarse en SIGEP.

## 4. Decisión del triaje

| Pregunta | Respuesta |
|---|---|
| ¿Se vulneró un control? | Sí. El privilegio excesivo permitió acceder a expedientes que no corresponden al rol. |
| ¿Se afectó la confidencialidad? | Sí. Hubo consulta no autorizada. |
| ¿Hay datos personales? | Sí, incluyendo datos sensibles de salud en algunos expedientes (probable). |
| **Resultado** | **Brecha de datos personales** → pasa a evaluación de severidad (02). |

## 5. Acciones inmediatas recomendadas
Son propuestas. Las decide y ejecuta la organización.
1. Suspender la cuenta `secretaria2` y cerrar sus sesiones activas. **Es lo más urgente.**
2. Preservar los registros (`accesos-sigep.log` y los de otros módulos, el servidor y los accesos de red). Calcular hash y registrar la cadena de custodia (ISO/IEC 27037). Con retención de 45 días, los registros del 05/10 se perderían hacia el 19/11/2026 `[calculado: 05/10 + 45 días]`.
3. Retirar el permiso de ver expedientes completos al rol de secretaría mientras se corrige el sistema.
4. Revisar el equipo de la secretaria y su correo institucional, y los registros de impresión, en busca de copias. Hacerlo con Asesoría Jurídica.
5. No confrontar ni tomar medidas disciplinarias sin asesoría legal `[VERIFICAR procedimiento interno]`.
6. Verificar si hay accesos de esa cuenta antes del 05/10 (el log entregado empieza ese día).
7. Designar hoy a la persona que decide la notificación (la política dice que no existe).
