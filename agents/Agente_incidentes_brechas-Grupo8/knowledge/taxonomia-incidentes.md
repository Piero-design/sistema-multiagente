# Taxonomía de incidentes

Sirve para clasificar el incidente en el triaje. Combina la dimensión afectada (tríada CID) con categorías inspiradas en la taxonomía de referencia de ENISA / CSIRTs (*Reference Security Incident Taxonomy*) `[VERIFICAR versión citada]`.

## 1. Tipo de brecha según la dimensión afectada
Un incidente puede tener más de un tipo.

| Tipo | Definición | Equivalente en el art. III num. 16 del reglamento |
|---|---|---|
| **Confidencialidad** | Acceso o divulgación no autorizada o accidental | "comunicación o exposición no autorizada" |
| **Integridad** | Alteración no autorizada o accidental | "alteración ilícita" |
| **Disponibilidad** | Pérdida de acceso o destrucción, temporal o permanente | "destrucción, pérdida" |

## 2. Categorías

| Código | Categoría | Ejemplos | Tipo habitual |
|---|---|---|---|
| MAL | Código malicioso | Ransomware, troyano, infostealer | Disponibilidad + confidencialidad (doble extorsión) |
| INT | Intrusión / acceso no autorizado | Cuenta comprometida, explotación de vulnerabilidad, credenciales filtradas | Confidencialidad |
| FRA | Fraude e ingeniería social | Phishing, suplantación, fraude del CEO | Confidencialidad |
| FUG | Fuga o divulgación accidental | Correo al destinatario equivocado, CC en lugar de CCO, archivo público por error | Confidencialidad |
| FIS | Pérdida o robo físico | Laptop, USB o documentos perdidos o robados | Confidencialidad + disponibilidad |
| INS | Uso indebido interno | Empleado consulta o extrae datos sin necesidad | Confidencialidad |
| PRV | Incidente en un encargado/proveedor | Brecha en la nube, call center o software de terceros | Variable (art. 36: el encargado avisa de inmediato) |
| DIS | Indisponibilidad | Falla sin respaldo, borrado accidental, DoS | Disponibilidad |
| ALT | Alteración de datos | Modificación indebida de notas, montos o historiales | Integridad |
| OTR | Otro / por clasificar | — | — |

## 3. Evento vs. incidente vs. brecha (criterios del triaje)

| Pregunta | No | Sí |
|---|---|---|
| ¿Hay indicios de que se vulneró un control de seguridad? | **Evento sin incidente** (falso positivo, intento bloqueado). Registrar y cerrar | Continuar |
| ¿Se afectó la confidencialidad, integridad o disponibilidad de información? | Evento registrado | **Incidente de seguridad** |
| ¿La información afectada incluye **datos personales**? | Incidente de seguridad de la información (gestión ISO 27035, sin obligaciones de la Ley 29733) | **Incidente de seguridad de datos personales (brecha)** → evaluar severidad y notificación |

Ejemplos de **eventos que no son incidentes**: correo de phishing reportado y no abierto; intento de inicio de sesión bloqueado por MFA; alerta de antivirus que eliminó el archivo antes de ejecutarse; laptop perdida con disco cifrado y sin clave comprometida (es incidente, pero puede no requerir notificación: evaluarlo).

## 4. Prioridad operativa del triaje

| Prioridad | Criterio | Tiempo de primera respuesta sugerido |
|---|---|---|
| P1 Crítica | Ataque en curso, ransomware, datos sensibles expuestos públicamente | Inmediato |
| P2 Alta | Brecha confirmada con datos personales; reloj de 48 h corriendo | Mismo día |
| P3 Media | Incidente sin datos personales o con exposición contenida | 24 h |
| P4 Baja | Evento sin impacto | Registro rutinario |

> Los tiempos de primera respuesta son una propuesta interna del proyecto, no una exigencia normativa.
