# 02 · Evaluación de severidad — INC-20261012-acceso-indebido-historias

> BORRADOR para revisión humana. Metodología: `knowledge/metodologia-severidad.md` (ENISA 2013) + art. 34.1 D.S. 016-2024-JUS.

## Cálculo: SE = DPC × EI + CB
| Componente | Valor | Justificación (reportado) |
|---|---|---|
| DPC | **4** | Datos de salud (sensibles). Ajuste +1 posible por pacientes de psiquiatría y personas con exposición pública (perfilamiento y estigma), pero el tope es 4. |
| EI | **1** | Historia clínica con identificación directa de cada paciente. |
| CB confidencialidad | **+0,25** | Un destinatario conocido (una persona identificada), no autorizado, sin evidencia de copia ni difusión. |
| CB integridad / disponibilidad | 0 / 0 | Sin indicios de alteración ni indisponibilidad `[VERIFICAR en logs]`. |
| CB intención | **+0,5** | Uso indebido intencional por personal interno (consultó sin necesidad; "curiosidad"). |
| **SE** | **4 × 1 + 0,75 = 4,75** | **MUY ALTA** (≥ 4). |

Nota de sensibilidad: aunque no haya difusión, la fuga a un tercero interno conocido es un riesgo grave para pacientes de psiquiatría y personas públicas (daño reputacional, discriminación). Si se confirma copia o difusión, CB sube a +0,5 en confidencialidad y SE = 5,0.

## Decisión (art. 34)
| Pregunta | Resultado |
|---|---|
| ¿Datos sensibles? | **Sí** → notificar a la ANPD (art. 34.1). Basta este supuesto. |
| ¿Gran número o grandes volúmenes? | 47 titulares: no se puede afirmar `[VERIFICAR lineamientos ANPD]`. No es necesario, ya que lo activa lo sensible. |
| ¿Perjuicio evidente a otros derechos? | Probable. SE ≥ 3 activa el criterio de apoyo → **comunicar a los titulares** (art. 34.3). |
| ¿Excepción art. 34.4? | **No aplica**: no se descarta la afectación, y no se puede considerar superado totalmente porque la información ya fue vista y no es reversible. |
| ¿Entorno digital? | Sí → **aviso al CNSD** (art. 34.5). |
| Documentación (art. 35) | Obligatoria (este expediente). |

**Resultado: notificar a la ANPD (dentro de 48 h), comunicar a los 47 titulares y avisar al CNSD.**
Aunque la persona está suspendida y no hay evidencia de copia, el art. 34.1 aclara que la obligación permanece aun si el incidente se considera resuelto internamente.

## Matiz sobre los titulares
- Prioridad de comunicación individual y cuidadosa: pacientes de psiquiatría y las dos personas con exposición pública. Evitar mencionar sus identidades en cualquier documento general.
- Se recomienda que la decisión sobre el canal (llamada, carta, presencial) la tome el Oficial de Datos con el área clínica. En psiquiatría puede ser conveniente un contacto asistido.
- Los 6 pacientes que sí pasaron por admisión: validar si su consulta fue justificada. Si lo fue, se excluyen de la comunicación (**41 titulares probables**, 47 si no se puede validar). `[VERIFICAR]`
