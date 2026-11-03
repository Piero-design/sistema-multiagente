# Informe de evaluación DPA — NubeAndina Contact Services S.A.C.

## 1. Resumen ejecutivo

| Elemento | Resultado |
|---|---|
| Dictamen | **No recomendable sin enmiendas** |
| Puntaje del proveedor | **22 / 100 — Riesgo alto** (base 37,5 − 15 por 3 alertas Altas) |
| Nivel de riesgo PII | **Alto** (datos financieros; ~180 000 titulares) |
| Controles evaluados | 24 — 🟢 1 · 🟡 12 · 🔴 4 · ⚪ 7 · ➖ 0 |
| Alertas | 3 Altas · 3 Medias (1 de renovación) |
| Estado de aprobación | **Pendiente DPO** → luego Legal |

El proveedor puede usar las grabaciones para sus propios modelos de analítica de voz (cl. 3), avisa incidentes en 72 h (cl. 6) y envía datos a EE. UU. e India sin garantías ni aviso previo de cambios (cl. 7). Además, el contrato no tiene fecha de vigencia. Se recomienda no firmar hasta obtener las enmiendas de la sección 8.

## 2. Ficha del tercero, rol y vigencia del contrato

| Campo | Valor |
|---|---|
| Proveedor | NubeAndina Contact Services S.A.C. (Lima, Perú) |
| Rol | **Encargado** (cl. 1: "por cuenta del Cliente conforme a sus instrucciones") |
| Servicio | Centro de contacto: atención, cobranza preventiva, encuestas |
| Datos | Identificativos, contacto, domicilio, pagos y deuda, grabaciones de voz |
| Países | Perú · EE. UU. (VoxCloud Inc.) · India (TranscribePro Ltd.) |
| Fecha de firma / vigencia / renovación / preaviso | **No localizadas** en el contrato (null) |
| Hash SHA-256 del documento | Registrado en el JSON |
| ID tercero / ID contrato | No entregados (null) |

## 3. Idoneidad: certificaciones y uso de IA

| Certificación | Tipo | Estado | Observación |
|---|---|---|---|
| ISO/IEC 27001 | Aceptada | Declarada sin evidencia | Cl. 5, sin certificado, alcance ni vigencia |
| ISO/IEC 27701 | Aceptada | No presentada | |
| Informe de auditoría | No reconocida | Declarada sin evidencia | Cl. 9: "resumen", sin tipo ni fecha |

**Uso de IA: detectado.** El proveedor usa transcripción automática (TranscribePro) y analítica de voz con modelos propios. Ese uso **no está limitado** a los fines del Responsable (cl. 3) y no hay evidencia de gobernanza de IA (p. ej. ISO/IEC 42001).

## 4. Matriz de controles ISO/IEC 27701:2025

Ámbito: **A7** = propio del Agente 7 · **SoA** = insumo para el Agente 3.

| Control | Ámbito | Requisito (resumen) | Cláusula | Evidencia (cita ≤20 palabras) | Estado | Severidad | Observación |
|---|---|---|---|---|---|---|---|
| A.2.2.2 | SoA | Instrucciones documentadas y asistencia | 1, 2 | "conforme a sus instrucciones" | 🟡 | Alta | Sin duración ni anexo de instrucciones |
| A.2.2.3 | SoA | Solo fines del responsable | 3 | "para mejorar sus modelos de analítica de voz" | 🔴 | Crítica | Fin propio; anonimización sin método |
| A.2.2.4 | SoA | Sin marketing | 3 | "exclusivamente para prestar los servicios" | 🟡 | Alta | Sin prohibición expresa |
| A.2.2.5 | SoA | Aviso de instrucción ilícita | No localizada | — | ⚪ | Alta | |
| A.2.2.6 | SoA | Información y auditoría | 9 | "No se permitirán auditorías in situ" | 🟡 | Alta | Solo un resumen |
| A.2.2.7 | SoA | Registros del tratamiento | No localizada | — | ⚪ | Alta | |
| A.2.3.2 | SoA | Asistencia en derechos | 8 | "en la medida de lo razonable" | 🟡 | Alta | Sin plazo (política: 5 días hábiles) |
| A.2.4.2 | SoA | Archivos temporales | No localizada | — | ⚪ | Alta | |
| A.2.4.3 | SoA | Devolución/eliminación | 10 | "en un plazo razonable, salvo las copias de respaldo" | 🟡 | Alta | Sin plazo (política: 30 días) ni certificado |
| A.2.4.4 | SoA | Transmisión protegida | 5 | "medidas técnicas y organizativas adecuadas" | 🟡 | Alta | Sin cifrado explícito |
| A.2.5.2 | SoA | Base de transferencias | 7 | "autorización general al Proveedor para contratar subencargados" | 🔴 | Crítica | Sin mecanismo ni garantías |
| A.2.5.3 | SoA | Lista de países | 7 | "Estados Unidos … India" | 🟡 | Alta | Sin lista cerrada |
| A.2.5.4 | SoA | Registro de comunicaciones | No localizada | — | ⚪ | Alta | |
| A.2.5.5 | SoA | Aviso de solicitudes de autoridades | No localizada | — | ⚪ | Alta | |
| A.2.5.6 | SoA | Solo comunicaciones vinculantes | No localizada | — | ⚪ | Alta | |
| A.2.5.7 | **A7** | Divulgación de sub-encargados | 7 | "VoxCloud Inc., almacenamiento de grabaciones, Estados Unidos" | 🟢 | Ninguna | |
| A.2.5.8 | **A7** | Contratación con obligaciones equivalentes | 7 | "autorización general" | 🟡 | Alta | Sin obligaciones en cascada |
| A.2.5.9 | **A7** | Aviso previo y objeción | 7 | "publicará en su sitio web las actualizaciones" | 🔴 | Crítica | Sin aviso previo (política: 30 días) |
| A.3.9 | SoA | Acceso y confidencialidad | 4 | "su personal está sujeto a obligaciones de confidencialidad" | 🟡 | Alta | |
| A.3.10 | **A7** | Seguridad y aviso en acuerdos | 6 | "dentro de las 72 horas siguientes" | 🔴 | Crítica | 72 h > 24 h (política) |
| A.3.11 | SoA | Procedimiento de incidentes | No localizada | — | ⚪ | Alta | |
| A.3.12 | SoA | Contenido del aviso y cooperación | 6 | "notificará al Cliente cualquier violación" | 🟡 | Alta | |
| A.3.13 | SoA | Compromiso legal | 11 | "se rige por las leyes de la República del Perú" | 🟡 | Alta | |
| A.3.15 | SoA | Revisión independiente | 9 | "un resumen de su informe de auditoría" | 🟡 | Alta | |

Los 19 controles marcados SoA se envían como insumo al Agente 3, que consolida su estado en la SoA.

## 5. Contraste con Ley 29733 y política interna

| Parámetro | Política v1.1 | Contrato | Resultado |
|---|---|---|---|
| Aviso de incidentes | ≤ 24 h | 72 h | 🔴 Impide notificar a la ANPD en 48 h |
| Asistencia en derechos | ≤ 5 días hábiles | "razonable" | 🟡 |
| Devolución/eliminación | ≤ 30 días | "razonable"; respaldos excluidos | 🟡 |
| Aviso de cambio de sub-encargado | 30 días | Publicación en web | 🔴 |
| Países | Perú + UE/EEE | EE. UU., India sin garantías | Alerta Alta |

Si el proveedor usa los datos para fines propios, actúa fuera del encargo y asume responsabilidad como responsable. El RGPD no aplica a este contrato.

## 6. Alertas

| Prioridad | Tipo | Descripción | Controles |
|---|---|---|---|
| **Alta** | Riesgo | Uso de grabaciones para fines propios; anonimización sin método | A.2.2.3, A.2.2.4 |
| **Alta** | Seguridad | Aviso de incidentes en 72 h > 24 h | A.3.10, A.3.12 |
| **Alta** | Riesgo | EE. UU. e India fuera de la lista aprobada, sin garantías | A.2.5.2, A.2.5.3, A.2.5.8 |
| Media | Riesgo | Certificaciones solo declaradas con riesgo PII Alto | A.3.15 |
| Media | Riesgo | Uso de IA sin evidencia de gobernanza | A.2.2.3 |
| Media | Renovación | Sin fecha de fin de vigencia ni revisión periódica *(script)* | A.1.2.7 |

## 7. Puntaje del proveedor

| Sección del Anexo A | Puntaje base |
|---|---|
| A.2.2 Condiciones de recolección y tratamiento | 30,0 |
| A.2.3 Obligaciones con los titulares | 50,0 |
| A.2.4 Privacidad desde el diseño y por defecto | 45,0 |
| A.2.5 Compartición, transferencia y comunicación | 42,2 |
| A.3 Consideraciones de seguridad | 32,5 |
| **Total** | **37,5 − 15 = 22 → Riesgo alto** |

## 8. Plan de remediación

| Prioridad | Control | Acción | Cláusula baseline |
|---|---|---|---|
| Alta | A.2.2.3 | Eliminar la excepción de fines propios; regular el uso de IA | 2 y 17 |
| Alta | A.3.10 | Aviso ≤ 24 h con contenido mínimo y cooperación ante la ANPD | 14 |
| Alta | A.2.5.2 | Lista cerrada de países y garantías para EE. UU. e India | 10 |
| Alta | A.2.5.9 | Aviso previo de 30 días y derecho de objeción | 12 |
| Alta | A.2.4.3 | Devolución/eliminación en 30 días, incluidos respaldos, con certificado | 9 |
| Media | A.1.2.7 | Vigencia, renovación y revisión anual | 16 |
| Media | A.2.2.6 | Derecho de auditoría; certificado ISO 27001 con alcance | 5 |

## 9. Borrador de correo al proveedor

> **Asunto:** Observaciones al Acuerdo de Tratamiento de Datos — enmiendas y evidencias requeridas
>
> Estimados señores de NubeAndina Contact Services S.A.C.:
>
> Tras revisar el acuerdo propuesto conforme a la Ley N.° 29733, su Reglamento y nuestro sistema de gestión de privacidad (ISO/IEC 27701:2025), requerimos antes de su firma:
>
> 1. Eliminar de la cláusula 3 el uso de información de las grabaciones para fines propios.
> 2. Notificar incidentes en un máximo de 24 horas, con contenido mínimo y cooperación.
> 3. Incluir una lista cerrada de países y las garantías para las transferencias a EE. UU. e India.
> 4. Avisar con 30 días de anticipación los cambios de subencargados, con derecho de objeción, y trasladarles obligaciones equivalentes.
> 5. Devolver o eliminar los datos, incluidos respaldos, en 30 días, con certificado.
> 6. Definir la vigencia del acuerdo, su renovación y una revisión anual.
>
> Solicitamos además: certificado ISO/IEC 27001 vigente con su alcance; el informe de auditoría independiente más reciente; y una descripción de los sistemas de IA que aplican sobre los datos (transcripción y analítica), con la evidencia de gobernanza de IA de que dispongan.
>
> *[Borrador — requiere aprobación del DPO y de Legal antes de su envío]*

## 10. Aprobaciones requeridas

| Orden | Aprobador | Decide | Estado |
|---|---|---|---|
| 1 | DPO | Valida el dictamen y las enmiendas | **Pendiente** |
| 2 | Legal | Aprueba las enmiendas y la firma del DPA nuevo | En espera del DPO |

## 11. Supuestos, limitaciones y trazabilidad

- Ficha del tercero inferida del contrato; ID de tercero y de contrato no entregados.
- Parámetros de política v1.1, que son decisiones de diseño del TIF pendientes de validación del DPO.
- Numeración de controles tomada de fuentes secundarias; verificar con el texto oficial (Anexos A y F).
- Evaluación documental; no constituye asesoría legal.
- Trazabilidad: skill v1.1 · config v1.1 · evaluador Agente 7 (Claude Opus 5.5) · cálculo por script · fecha de referencia 01/10/2026.
