# 02 · Evaluación de severidad — INC-20261013-acceso-indebido-sigep

> ESCENARIO SIMULADO. BORRADOR para revisión humana. Metodología: ENISA 2013 (`knowledge/metodologia-severidad.md`). SE = DPC × EI + CB. La severidad se mide sobre los titulares.

## 1. Puntuación

### DPC (contexto de los datos)
- Los datos básicos (nombre, DNI, correo, teléfono, programa, tema y asesor de tesis) son **simples (base 1)**.
- Los expedientes pueden incluir constancias de aptitud médica, que son **datos de salud (base 4)**. En SIGEP hay unas 210 (`inventario-posgrado.md:8`). **No sabemos si alguna de las 85 consultadas las contiene.**
- Entre los consultados hay docentes y dos autoridades. Esto es una posible relación de dependencia con la institución, pero no es un agravante claro.

| Escenario | DPC | Justificación |
|---|---|---|
| **A. Conservador (el que se usa para decidir)** | **4** | Hay datos sensibles probables. Ante la duda se asume lo peor. |
| B. Si el conteo en SIGEP muestra que **ninguno** de los 85 tiene constancia médica | 2 | Base 1, más 1 porque el conjunto permite perfilar a personas concretas y entre ellas hay autoridades y docentes. |

### EI (facilidad de identificación) = **1 (máxima)**
Nombre completo más DNI, correo y teléfono permiten identificar directamente a cada persona.

### CB (circunstancias)
| Factor | Valor | Justificación |
|---|---|---|
| Confidencialidad | +0,25 | Una sola persona conocida, empleada de la institución, accedió sin autorización. No hay evidencia de difusión. |
| Integridad | 0 | No se reportan alteraciones. `[VERIFICAR en el log si hubo escrituras]` |
| Disponibilidad | 0 | Los datos siguen disponibles. |
| Intención | +0,5 | Uso indebido intencional por personal interno. La persona declaró que fue "curiosidad", y 85 consultas en 8 días no son accidentales. |
| **CB total** | **0,75** | |

## 2. Resultado

| Escenario | Cálculo | SE | Nivel |
|---|---|---|---|
| **A (conservador)** | 4 × 1 + 0,75 | **4,75** | **Muy alta** |
| B | 2 × 1 + 0,75 | 2,75 | Media |

**Lectura.** El nivel "Muy alta" viene sobre todo de que podría haber datos de salud. Los hechos atenuantes son que no hay evidencia de copia o difusión, que fue una persona interna y que no hay menores. Aun así, la metodología con datos sensibles probables da Muy alta. **Se recomienda usar el escenario A hasta que SIGEP confirme cuántos expedientes tienen constancia médica.** Es la tarea que más cambia la evaluación y debe hacerse hoy.

## 3. Decisión legal (art. 34 y `metodologia-severidad.md` sección 5)

| Pregunta | Respuesta | Consecuencia |
|---|---|---|
| ¿Datos sensibles afectados? | **Probable** (salud). Aún sin confirmar. | Notificar a la ANPD (art. 34.1). |
| ¿Grandes volúmenes o gran número de personas? | Dudoso: 85 titulares (5,9 % de 1 450). No hay umbral oficial `[VERIFICAR lineamientos ANPD]`. Pero el tipo de dato (expediente completo) sí es amplio. | Ante la duda, notificar. |
| ¿Perjuicio evidente a otros derechos o libertades? | SE ≥ 3 en el escenario A (criterio de apoyo). No hay perjuicio concreto conocido. | Preparar la comunicación a titulares (art. 34.3). |
| ¿En entorno digital? | Sí, ocurrió dentro de SIGEP. | Notificar también al CNSD (art. 34.5). |
| ¿Superado totalmente (art. 34.4)? | **No.** La cuenta sigue activa y no se ha comprobado que no hubo copias. | La excepción a comunicar no se puede aplicar todavía. |

## 4. Recomendaciones

1. **Notificar a la ANPD antes de la hora límite** (2026-10-15 10:20 como máximo; ver 03-notificacion-anpd.md). Si no se logra confirmar los datos sensibles a tiempo, notificar igual y completar después. La obligación permanece aunque el incidente se considere resuelto (art. 34.1).
2. **Notificar al CNSD** por el entorno digital (03-aviso-cnsd.md).
3. **Comunicar a los titulares** (03-comunicacion-titulares.md). Recomendación: comunicar a los 85, empezando por los que tengan constancia médica, salvo que Asesoría Jurídica documente que se cumple la excepción del art. 34.4. Es una decisión humana.
4. **Documentar** todo (art. 35), incluso si se decidiera lo contrario.
5. **Riesgo de no actuar:** no comunicar a la ANPD un incidente que corresponde es infracción grave (art. 133 num. 12). `[VERIFICAR rango de multa]`

## 5. Consecuencias posibles para los titulares
- Pérdida de confidencialidad de información de salud (si se confirma) y de datos de contacto.
- Uso de los datos para presión, acoso o suplantación si la persona los hubiera copiado, hipótesis sin evidencia hoy.
- Para docentes y autoridades, posible exposición de su relación con un programa o tema de tesis.
