# Mapa de controles ISO/IEC 27701:2025 para DSAR

Verificado contra ISO/IEC 27701:2025 (segunda edición, 2025-10): Anexo A, tablas A.1 y A.3, y guía de implementación del Anexo B, apartado B.1.3. Es un resumen para el skill, no reproduce la norma.

## Controles principales

| Control | Título | Qué exige | Cómo lo cumple el skill |
|---|---|---|---|
| A.1.3.7 | Access, correction or erasure | Políticas, procedimientos o mecanismos para que el titular acceda, corrija o borre su PII sin demora indebida (B.1.3.7) | Tareas T1 y T3; rectificación y supresión siempre con HITL |
| A.1.3.9 | Providing copy of PII processed | Entregar copia en formato estructurado y de uso común, solo del titular correcto; portabilidad legible por máquina donde la ley lo pida (B.1.3.9) | Filtro por `principal_id`, retiro de terceros, derecho `portability` |
| A.1.3.10 | Handling requests | Definir y documentar políticas y procedimientos para responder solicitudes legítimas dentro de tiempos definidos (B.1.3.10) | Perfil de jurisdicción, `deadlines`, expediente y validador |

## Controles complementarios

| Control | Título | Aplicación en el skill |
|---|---|---|
| A.1.3.2 | Determining and fulfilling obligations to PII principals | Paso 1 del skill: fijar el perfil legal antes de decidir |
| A.1.3.3 / A.1.3.4 | Determining / providing information to PII principals | Derecho `information` (PE) y estilo claro del borrador (B.1.3.4) |
| A.1.3.5 | Mechanism to modify or withdraw consent | Retiro de consentimiento como causa de cancelación (PE, art. 82.1) |
| A.1.3.6 | Mechanism to object to PII processing | Derecho `objection`, con HITL |
| A.1.3.8 | PII controllers' obligations to inform third parties | Rectificación, supresión u oposición sobre datos compartidos → derivar al Agente de Terceros y monitorear el acuse (B.1.3.8) |
| A.1.3.11 | Automated decision making | Las decisiones automatizadas se derivan al DPO; el agente nunca decide solo |
| A.1.4.8 / A.1.4.9 | Retention / Disposal | Restricciones de conservación en los registros → HITL antes de proponer supresión |
| A.1.5.4 / A.1.5.5 | Records of transfer / of disclosures to third parties | Saber a quién notificar las correcciones y supresiones |
| A.3.9 | Access rights | Mínimo privilegio para el agente y sus herramientas |
| A.3.14 | Protection of records | Expediente con hashes SHA-256 y rastro de auditoría continuo |
| A.3.25 | Logging | `audit_trail` de cada paso y decisión |
| A.3.31 | Test information | Solo datos sintéticos (`example.test`) en pruebas y demostraciones |

## Interpretación aplicada

- La norma exige definir un tiempo de respuesta y atender dentro de él (B.1.3.7 y B.1.3.10), pero **no fija un número de días**. El número lo pone la ley del perfil.
- Toda corrección o supresión debe difundirse a los usuarios autorizados y a los terceros a quienes se transfirió la PII (B.1.3.7 y B.1.3.8).
- Si los datos ya se suprimieron por la política de conservación, se informa al titular que fueron eliminados (B.1.3.9).
- No se re-identifica a un titular solo para atender la solicitud cuando sus datos fueron desidentificados (B.1.3.9).
- Algunas jurisdicciones permiten cobrar por solicitudes excesivas o repetitivas (B.1.3.10). En Perú, sector privado, es gratuito (art. 67).
- Las excepciones legales no las deduce el modelo: vienen del perfil y las aprueba una persona.
