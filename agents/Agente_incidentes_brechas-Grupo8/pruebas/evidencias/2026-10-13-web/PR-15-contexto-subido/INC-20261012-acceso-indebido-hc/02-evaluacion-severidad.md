# 02 · Evaluación de severidad — INC-20261012-acceso-indebido-hc

> BORRADOR para revisión humana. Metodología: ENISA 2013 + art. 34.1 (`knowledge/metodologia-severidad.md`).

## 1. Puntuación SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| DPC | **4** | Datos de salud y psiquiatría = sensibles (base 4). Ajuste +1 por contexto (pacientes psiquiátricos, personas con exposición pública, relación paciente–clínica) → tope 4 |
| EI | **1** | HC con nombre, DNI y dirección: identificación directa (`activos.md:4`) |
| CB confidencialidad | **+0,25** | Un destinatario conocido (una trabajadora identificada) sin autorización; sin evidencia de copia o difusión |
| CB integridad | 0 | Solo lectura (`VIEW`); sin alteraciones en el log |
| CB disponibilidad | 0 | Sin indisponibilidad |
| CB intención maliciosa | **+0,5** | Uso indebido intencional por personal interno (consulta deliberada de 41 HC sin atención al paciente, según reporte; "curiosidad") |
| **SE** | **4 × 1 + 0,75 = 4,75** | **MUY ALTA (≥ 4)** |

Nota: la severidad está impulsada por la naturaleza sensible de los datos. Aunque no hay evidencia de difusión, el riesgo para los titulares (estigma por psiquiatría, exposición de personas públicas) es grave. Si se confirmara una copia o difusión, CB subiría.

## 2. Decisión legal (art. 34)
| Pregunta | Resultado | Artículo |
|---|---|---|
| ¿Datos sensibles? | **Sí** (salud, psiquiatría) | 34.1 |
| ¿Grandes volúmenes / gran número? | 47 titulares de 6 200 (0,76 %): `[no hay umbral oficial; VERIFICAR lineamientos ANPD]`. No es determinante porque ya aplica el supuesto de datos sensibles | 34.1 |
| ¿Perjuicio evidente a otros derechos o libertades? | **Probable** (SE ≥ 3; datos de salud mental y personas públicas) | 34.1 / 34.3 |
| ¿Entorno digital? | **Sí** | 34.5 |
| ¿Excepción por superado totalmente? | **No aplica**: no se descarta difusión (solo la palabra de la trabajadora), el log solo cubre 60 días, y la cuenta es compartida | 34.4 |

### Conclusión
| Obligación | Decisión |
|---|---|
| **Notificar a la ANPD** (≤ 48 h) | **SÍ — obligatoria** (datos sensibles). No se exime aunque la trabajadora esté suspendida o el hecho se considere resuelto |
| **Comunicar a los titulares** (47) | **SÍ — recomendada** por criterio de apoyo SE ≥ 3 y duda razonable; la decisión final es del Oficial/dirección `[VERIFICAR con asesoría legal]` |
| **Avisar al CNSD** | **SÍ** (art. 34.5) |
| **Documentar** | **SÍ** (art. 35), siempre |

Riesgo de la lectura estricta: aunque el reporte dice "revisión mensual", la herramienta de reporte estuvo disponible y no hubo alertas; una autoridad podría cuestionar la detección tardía (hecho del 1/10, conocido el 12/10). La demora en la detección no cambia el plazo de 48 h, pero sí afecta la valoración de medidas de seguridad (art. 46).

## 3. Límites de la evaluación
- El número de titulares afectados (47) está confirmado por el log, pero podría ser mayor si hubo accesos previos al 1/10 o por otras cuentas.
- No se verificó la identidad de los pacientes "públicos" (el log no tiene nombres).
