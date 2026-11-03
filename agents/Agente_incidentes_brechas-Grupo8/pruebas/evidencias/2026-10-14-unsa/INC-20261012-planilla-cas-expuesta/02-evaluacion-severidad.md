# 02 — Evaluación de severidad · INC-20261012-planilla-cas-expuesta

> BORRADOR para revisión. Metodología: ENISA 2013 + art. 34.1 (`knowledge/metodologia-severidad.md`).

## Puntuación SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| DPC | **4** | Base 3 por datos financieros (cuenta bancaria, remuneración, descuentos). La metodología trata los ingresos económicos como sensibles en Perú, así que la base es 4. Ajuste por contexto +1 (relación de dependencia laboral y perfilamiento por el conjunto), sin pasar el tope de 4 |
| EI | **1** | Nombre completo + DNI + cuenta: identificación directa |
| CB confidencialidad | **+0,5** | Publicada en Internet y hallada por buscador; destinatarios desconocidos |
| CB integridad | 0 | Sin alteración reportada |
| CB disponibilidad | 0 | La hoja sigue existiendo; la UNSA no perdió acceso |
| CB intención maliciosa | 0 | Error humano; sin indicios de uso malicioso `[sin evidencia de acceso]` |

**SE = 4 × 1 + 0,5 = 4,5 → MUY ALTA** (consecuencias graves o difíciles de revertir: fraude con cuenta bancaria y DNI, suplantación, ingeniería social).

Sensibilidad: aun con DPC = 3, SE = 3,5 (Alta). El nivel no baja de Alta.

## Decisión por art. 34.1
| Supuesto | ¿Se cumple? | Razón |
|---|---|---|
| Grandes volúmenes (cantidad o tipo) | Probable | ~320 titulares pero tipo de dato delicado (cuenta bancaria + remuneración + DNI); no hay umbral oficial `[VERIFICAR lineamientos ANPD]` |
| Gran número de personas | Duda | 320 es limitado; ante la duda se notifica |
| Datos sensibles | **Sí (probable)** | Ingresos económicos, según la metodología; los descuentos podrían revelar más |
| Perjuicio evidente a otros derechos | **Sí (probable)** | SE ≥ 3; riesgo de fraude y suplantación; exposición pública prolongada de 5 semanas |
| Entorno digital | **Sí** | Nube y buscador |

## Decisiones
1. **Notificar a la ANPD**: sí (art. 34.1, 34.2). Límite referencial: 2026-10-14 15:45. La contención posterior no exime (art. 34.1: la obligación permanece aunque se haya subsanado).
2. **Comunicar a los 320 titulares**: sí (art. 34.3). El perjuicio probable activa la comunicación, y la excepción del 34.4 no aplica porque no se puede afirmar que la exposición quedó totalmente superada (hay acceso desconocido y posible caché).
3. **Notificar al CNSD**: sí (art. 34.5).
4. **Documentar** (art. 35): sí, en `04-respuesta-y-cierre.md`.
5. **Ante la duda se recomienda notificar**: la sanción por no hacerlo es infracción grave (art. 133 num. 12).

## Incertidumbres que pueden cambiar la evaluación
- Número de accesos o descargas: desconocido. Si hubo uso, empeora; si no, el SE sigue siendo Muy alto por la exposición pública.
- Si el buscador o terceros conservan copias.
- Composición exacta de "descuentos".
- Si hay menores o personas con medidas judiciales en la planilla `[VERIFICAR]`.
