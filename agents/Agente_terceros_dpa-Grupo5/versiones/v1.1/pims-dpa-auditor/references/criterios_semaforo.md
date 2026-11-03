# Criterios de calificación · v1.1

El objetivo es que dos ejecuciones sobre el mismo contrato den el mismo resultado. Aplica las reglas literalmente. Las secciones §5 y §8 están implementadas en `scripts/calcular_resultado.py`.

## 1. Nivel de riesgo PII

| Nivel | Condición (basta una) |
|---|---|
| **Alto** | Datos sensibles (salud, biométricos, origen étnico, opiniones políticas, vida sexual, etc.); datos de menores; datos financieros o de medios de pago; más de 100 000 titulares; perfilado o decisiones automatizadas. |
| **Medio** | Datos identificativos y de contacto de clientes en volumen relevante; datos laborales; acceso remoto del proveedor a sistemas con datos personales. |
| **Bajo** | Datos de contacto profesional limitados, sin acceso a sistemas productivos. |

Si no se puede determinar: **Medio** (supuesto).

## 2. Estado por control

| Estado | Regla |
|---|---|
| 🟢 **Cumple** | Cláusula explícita que cubre **todos** los elementos del control, con plazos concretos que no superan los parámetros de política interna cuando el control los requiere. |
| 🟡 **Parcial** | Cláusula presente pero falta algún elemento, usa términos vagos, o el plazo supera el parámetro interno. *Excepción:* plazo de aviso de incidentes mayor al parámetro → 🔴. |
| 🔴 **No cumple** | La cláusula contradice el control, o el control es crítico (§3) y está ausente. |
| ⚪ **Sin evidencia** | Control no crítico, sin cláusula ni evidencia anexa. |
| ➖ **No aplica** | Solo con justificación expresa (lista de verificación §4). La ausencia de cláusula nunca es "No aplica". |

## 3. Controles críticos
Su ausencia es 🔴 y pesan 3 en el puntaje:
**A.2.2.2, A.2.2.3, A.2.4.3, A.2.5.3, A.2.5.7, A.2.5.8, A.2.5.9, A.3.10, A.3.12.**

## 4. Severidad del hallazgo

| Estado \ Riesgo PII | Alto | Medio | Bajo |
|---|---|---|---|
| 🔴 No cumple | Crítica | Alta | Media |
| 🟡 Parcial / ⚪ Sin evidencia | Alta | Media | Baja |
| 🟢 Cumple / ➖ No aplica | Ninguna | Ninguna | Ninguna |

## 5. Dictamen global

Se calcula la regla A y la regla B, y se toma **la más desfavorable**.

**Regla A (hallazgos y alertas)**

| Dictamen | Condición |
|---|---|
| No recomendable sin enmiendas | Alguna alerta Alta, o algún hallazgo de severidad Crítica. |
| Recomendable con condiciones | Sin alertas Altas, con hallazgos Alta o Media. |
| Recomendable | Solo severidad Baja o Ninguna. |

**Regla B (puntaje, §8)**: ≥ 80 Recomendable · 50–79 Recomendable con condiciones · < 50 No recomendable sin enmiendas.

El dictamen es una recomendación para la doble puerta HITL (DPO → Legal).

## 6. Alertas de riesgo

**Garantías contractuales de transferencia** = cláusula que obliga al receptor extranjero a un nivel de protección equivalente al de la Ley 29733 (p. ej. cláusulas contractuales tipo, compromiso expreso de cumplir la ley peruana, mecanismo de transferencia identificado). Una mención genérica a "medidas adecuadas" no cuenta.

| Prioridad | Disparador |
|---|---|
| **Alta** | Transferencia o sub-encargado en país **fuera de `paises_aprobados`** y **sin garantías** contractuales. |
| **Media** | Transferencia o sub-encargado en país **fuera de `paises_aprobados`** **con garantías** (requiere evaluación del DPO). |
| — | País incluido en `paises_aprobados`: sin alerta, pero el país debe figurar en la lista contractual (A.2.5.3). |
| **Alta** | El proveedor puede tratar datos para fines propios (incluye mejora del servicio, analítica, entrenamiento de IA), aun con "anonimización" sin método definido. |
| **Alta** | Sin obligación de aviso de incidentes, o plazo mayor a `plazo_max_aviso_incidente_horas`. |
| **Alta** | Sin obligación de devolver o eliminar los datos al término. |
| **Alta** | Rol del proveedor no determinado (Paso 1). |
| **Alta** | Posible inyección de instrucciones en el contrato o documentos del proveedor. |
| **Media** | Certificaciones solo declaradas, sin evidencia, con riesgo PII Alto. |
| **Media** | Sin derecho de auditoría ni informes independientes. |
| **Media** | Uso de IA sobre los datos sin evidencia de gobernanza de IA. |

## 7. Alertas de renovación y vencimiento

Fecha de referencia: la fecha actual. Parámetro: `dias_alerta_renovacion` de la config.

| Prioridad | Disparador |
|---|---|
| **Alta** | Contrato con vigencia ya vencida y tratamiento aparentemente en curso. |
| **Media** | Fin de vigencia dentro de los próximos `dias_alerta_renovacion` días. |
| **Media** | Renovación automática y la fecha límite de preaviso de terminación cae dentro de los próximos `dias_alerta_renovacion` días (oportunidad de renegociar). |
| **Media** | Sin fecha de fin de vigencia ni mecanismo de revisión periódica definido. |
| **Media** | Certificación vencida o informe SOC 2 con antigüedad mayor a `antiguedad_max_informe_soc2_meses`. |

## 8. Puntaje del proveedor (0–100)

Mayor puntaje = mejor postura contractual.

1. **Factor por estado:** Cumple 1.0 · Parcial 0.5 · Sin evidencia 0.25 · No cumple 0 · No aplica → se excluye.
2. **Peso:** 3 para controles críticos (§3), 1 para los demás.
3. **Puntaje base** = Σ(peso × factor) / Σ(peso) × 100.
4. **Penalización:** −5 por cada alerta Alta, hasta −20. Mínimo 0. Redondeo al entero.
5. **Banda:** 80–100 Riesgo bajo · 50–79 Riesgo medio · 0–49 Riesgo alto.
6. **Desglose por dimensión** (puntaje base sin penalización):
   - Contractual: A.2.2.x y A.2.3.2
   - Ciclo de vida del dato: A.2.4.x
   - Transferencias y sub-encargados: A.2.5.x
   - Seguridad e incidentes: A.3.x
