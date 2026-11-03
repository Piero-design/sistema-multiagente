# Evaluación de severidad — INC-20260929-ransomware-clinica

- **Insumo:** `salidas/INC-20260929-ransomware-clinica/01-ficha-incidente.md`
- **Metodología:** ENISA (2013), SE = DPC × EI + CB. Ver `knowledge/metodologia-severidad.md`

## 1. Cálculo

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 4 | El dato más delicado son los de salud (diagnósticos y resultados de laboratorio), que son sensibles según la Ley 29733 |
| Ajuste de contexto | +0 (ya está en el tope) | El contexto agrava el daño: se combinan salud, DNI, dirección y seguro, lo que permite perfilar, y probablemente hay menores (inferencia). Pero la escala no pasa de 4 |
| **DPC final** | **4** | |
| **EI** | **1** | Identificación directa: nombre completo + DNI + fecha de nacimiento. No consta que los datos estuvieran cifrados por la clínica |
| CB — confidencialidad | +0,5 | El atacante (destinatario desconocido) amenaza con publicarlos en Internet. La extracción no está confirmada, pero se trata como probable porque ante la duda se presume |
| CB — integridad | +0,25 | Los datos fueron alterados (cifrados) de forma ilícita. Que se puedan recuperar depende del respaldo, cuyo estado se desconoce |
| CB — disponibilidad | +0,5 | El sistema de historias clínicas está totalmente inaccesible. El único respaldo tiene 3 semanas y puede estar cifrado, así que los registros de ese periodo podrían perderse para siempre |
| CB — intención maliciosa | +0,5 | Ataque deliberado con extorsión (ransomware) |
| **CB total** | **1,75** | 0,5 + 0,25 + 0,5 + 0,5 |

**SE = 4 × 1 + 1,75 = 5,75 → Severidad MUY ALTA** (SE ≥ 4)

> Sensibilidad del resultado: aunque se confirmara que **no** hubo extracción (CB de confidencialidad = 0), SE = 4 × 1 + 1,25 = 5,25, que sigue siendo **Muy alta**. La conclusión no cambia.

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad | Motivo |
|---|---|---|
| Exposición pública de diagnósticos y resultados (daño a la intimidad, estigma) | Alta | El atacante amenaza con publicar. Los datos de salud no se pueden "cambiar" como una contraseña |
| Discriminación (laboral, de seguros, social) por la condición de salud | Media | Diagnósticos vinculados a un DNI |
| Extorsión directa a pacientes | Media | Es un patrón conocido en ataques a centros de salud (inferencia); tienen teléfono y dirección |
| Suplantación de identidad y fraude (también con el seguro) | Media-alta | Nombre + DNI + fecha de nacimiento + datos del seguro |
| Phishing o llamadas fraudulentas que se hacen pasar por la clínica | Alta | Tienen contacto y contexto clínico creíble |
| Afectación de la atención de salud (historia no disponible, errores por falta de antecedentes, demoras) | Alta | El sistema está caído, se trabaja en papel y puede haberse perdido información de 3 semanas |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Sí** | Diagnósticos y resultados de laboratorio |
| | Grandes volúmenes (cantidad o tipo) | **Sí (probable)** | Una base clínica completa con datos sensibles. El reglamento no fija un umbral `[VERIFICAR lineamientos ANPD]` |
| | Gran número de personas | **Sí (probable)** | ~18 000 titulares. No hay umbral oficial `[VERIFICAR lineamientos ANPD]`; ante la duda, notificar |
| | Perjuicio evidente a derechos o libertades | **Sí** | SE Muy alta, amenaza de publicación y afectación de la atención de salud |
| **Resultado ANPD** | | **Obligación probable: NOTIFICAR** | Basta un solo supuesto; aquí se cumplen los cuatro |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí: comunicar** | No aplica la excepción del art. 34.4: hay afectación y el incidente no está superado |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Sí** | Ataque a sistemas informáticos mediante correo y malware |
| Documentar (art. 35) | Siempre | **Sí** | Registro en `04-respuesta-y-cierre.md` |

## 4. Plazos
- **Toma de conocimiento:** 2026-09-29 07:15 (hallazgo por el personal de admisión)
- **Hora límite (48 h):** **2026-10-01 07:15**. Tiempo restante: el agente no conoce la hora actual. A la fecha de este borrador (2026-10-01) quedan **como máximo algunas horas, o el plazo ya está VENCIDO**. Si se envía después de las 07:15, se debe completar la sección H (motivos de la demora) de `03-notificacion-anpd.md`.
- **Criterio conservador `[VERIFICAR]`:** si la toma de conocimiento se fija en la alerta del antivirus (2026-09-28 23:50), el plazo venció el 2026-09-30 23:50.
- La comunicación a los titulares también tiene un plazo de 48 h (art. 34.3): misma hora límite.

## 5. Nota aparte: impacto para la organización
- No notificar cuando corresponde es una **infracción grave** (art. 133 num. 12) `[VERIFICAR rango de multa en UIT, art. 39 de la Ley]`.
- Continuidad operativa: la atención clínica está en papel y hay un riesgo asistencial (control 5.29).
- Reputación y posible publicación de los datos. Pagar el rescate no garantiza que no se publiquen y no se recomienda.
- La alerta del antivirus que nadie revisó es una debilidad del proceso de monitoreo que la ANPD podría valorar.

## 6. Supuestos e información pendiente
- Se supone que hubo extracción porque no hay evidencia en contra (falta el análisis de tráfico saliente).
- El número de titulares (~18 000) es una estimación de TI.
- Falta confirmar si hay menores de edad y qué contiene exactamente el campo "datos del seguro".
- Falta determinar si el respaldo está íntegro.
- Falta revisar el contenido del servidor de archivos (otros titulares, como personal o proveedores).

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
