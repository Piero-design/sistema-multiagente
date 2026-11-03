# Informe de evaluación DPA — NubeAndina Contact Services S.A.C.

## 1. Resumen ejecutivo

| Elemento | Resultado |
|---|---|
| Dictamen | **No recomendable sin enmiendas** |
| Puntaje del proveedor | **22 / 100 — Riesgo alto** (base 37,5 − 15 por 3 alertas Altas) |
| Nivel de riesgo PII | **Alto** (datos financieros; ~180 000 titulares) |
| Controles evaluados | 24 — 🟢 1 · 🟡 12 · 🔴 4 · ⚪ 7 · ➖ 0 |
| Alertas | 3 Altas · 3 Medias (1 de renovación, generada por el script) |
| Estado de aprobación | **Pendiente DPO** → luego Legal |

Cuatro defectos concentran el riesgo. El proveedor se reserva el uso de las grabaciones
para entrenar sus propios modelos de analítica de voz (cl. 3), avisa los incidentes en
72 h cuando la política interna exige 24 h (cl. 6), envía datos a Estados Unidos e India
sin garantías de transferencia ni aviso previo de cambios (cl. 7) y sustituye el aviso de
cambio de sub-encargado por una publicación en su web. El contrato tampoco tiene fecha de
vigencia. **Se recomienda no firmar** hasta incorporar las enmiendas de la sección 8.

## 2. Ficha del tercero, rol y vigencia del contrato

| Campo | Valor |
|---|---|
| Proveedor | NubeAndina Contact Services S.A.C. (Lima, Perú) |
| Rol | **Encargado** — cl. 1: "tratará datos personales por cuenta del Cliente conforme a sus instrucciones" |
| Servicio | Centro de contacto: atención telefónica, cobranza preventiva y encuestas de satisfacción |
| Categorías de datos | Identificativos (nombre, DNI), contacto (teléfono, correo, dirección), financieros (historial de pagos, saldos de deuda), grabaciones de voz |
| Países de tratamiento | Perú · Estados Unidos (VoxCloud Inc.) · India (TranscribePro Ltd.) |
| Sub-encargados | VoxCloud Inc. (EE. UU., almacenamiento de grabaciones) · TranscribePro Ltd. (India, transcripción automática). Ninguno con garantías de transferencia |
| Fecha de firma | **No localizada** (null — Supuesto) |
| Inicio / fin de vigencia | **No localizados** (null — Supuesto) |
| Renovación automática | **No indicada** (null — Supuesto) |
| Preaviso de terminación | **No localizado** (null — Supuesto) |
| Ley aplicable | Perú (cl. 11) |
| Hash SHA-256 del documento | `f951d7ebc89995301e785cc5b1857dcc…` (registrado completo en el JSON) |
| ID tercero / ID contrato | No entregados (null) |

## 3. Idoneidad: certificaciones y uso de IA

| Certificación / informe | Tipo | Estado | Observación |
|---|---|---|---|
| ISO/IEC 27001 | Aceptada | **Declarada sin evidencia** | Cl. 5 la declara sin certificado, sin alcance y sin versión ni vigencia |
| ISO/IEC 27701:2025 | Aceptada | **No presentada** | No se menciona |
| Informe de auditoría no identificado | No reconocida | **Declarada sin evidencia** | Cl. 9 ofrece solo un resumen, sin tipo (no consta SOC 2 Tipo II) ni fecha |

**Uso de IA: detectado.** El proveedor aplica transcripción automática a través de
TranscribePro Ltd. (cl. 7) y entrena modelos propios de analítica de voz con las
grabaciones (cl. 3). Ese uso **no está limitado a los fines del Responsable** y **no hay
evidencia de gobernanza de IA** (por ejemplo ISO/IEC 42001). La apelación a información
"agregada y anonimizada" no acredita anonimización efectiva: no se define método ni
umbral, de modo que los datos siguen siendo personales a efectos de la evaluación.

## 4. Matriz de controles ISO/IEC 27701:2025

Ámbito: **A7** = propio del Agente 7 · **SoA** = insumo para el Agente 3.

| Control | Ámbito | Requisito (resumen) | Cláusula | Evidencia (cita ≤20 palabras) | Estado | Severidad | Observación |
|---|---|---|---|---|---|---|---|
| A.2.2.2 | SoA | Instrucciones documentadas y asistencia | 1, 2 | "tratará datos personales por cuenta del Cliente conforme a sus instrucciones" | 🟡 | Alta | Sin anexo de instrucciones, sin duración y sin definir la asistencia en derechos, DPIA e incidentes |
| A.2.2.3 | SoA | Solo fines del responsable | 3 | "para mejorar sus modelos de analítica de voz y la calidad de sus servicios" | 🔴 | Crítica | Fin propio; anonimización sin método ni umbral |
| A.2.2.4 | SoA | Sin marketing ni publicidad | 3 | "El Proveedor utilizará los datos exclusivamente para prestar los servicios" | 🟡 | Alta | Sin prohibición expresa, y la excepción de cl. 3 abre uso comercial |
| A.2.2.5 | SoA | Aviso de instrucción ilícita | No localizada | — | ⚪ | Alta | Sin deber de avisar si una instrucción infringe la Ley N.° 29733 |
| A.2.2.6 | SoA | Información y derecho de auditoría | 9 | "No se permitirán auditorías in situ" | 🟡 | Alta | Solo un resumen y a solicitud; insuficiente para demostrar cumplimiento |
| A.2.2.7 | SoA | Registros del tratamiento | No localizada | — | ⚪ | Alta | Sin obligación de mantener registro por cuenta del Responsable |
| A.2.3.2 | SoA | Asistencia en derechos de titulares | 8 | "colaborará con el Cliente, en la medida de lo razonable" | 🟡 | Alta | Término vago y sin plazo (política: 5 días hábiles) |
| A.2.4.2 | SoA | Archivos temporales | No localizada | — | ⚪ | Alta | Sin período definido de eliminación |
| A.2.4.3 | SoA | Devolución o eliminación al término | 10 | "en un plazo razonable, salvo las copias de respaldo" | 🟡 | Alta | Plazo indeterminado (política: 30 días), respaldos excluidos, sin certificado |
| A.2.4.4 | SoA | Controles de transmisión | 5 | "medidas técnicas y organizativas adecuadas" | 🟡 | Alta | Fórmula genérica, sin cifrado en tránsito |
| A.2.5.2 | SoA | Base de transferencias internacionales | 7 | "autorización general al Proveedor para contratar subencargados" | 🔴 | Crítica | Sin base ni mecanismo de transferencia, sin garantías y sin derecho de objeción |
| A.2.5.3 | SoA | Lista de países destino | 7 | "VoxCloud Inc. … Estados Unidos; TranscribePro Ltd. … India" | 🟡 | Alta | Lista no cerrada; ninguno de los dos países está en `paises_aprobados` |
| A.2.5.4 | SoA | Registro de comunicaciones a terceros | No localizada | — | ⚪ | Alta | Sin registro de qué, a quién y cuándo |
| A.2.5.5 | SoA | Aviso de solicitudes de autoridades | No localizada | — | ⚪ | Alta | Sin deber de avisar ante requerimientos |
| A.2.5.6 | SoA | Solo comunicaciones vinculantes | No localizada | — | ⚪ | Alta | Sin compromiso de rechazar solicitudes no vinculantes |
| A.2.5.7 | **A7** | Divulgación de sub-encargados | 7 | "VoxCloud Inc., almacenamiento de grabaciones, Estados Unidos" | 🟢 | Ninguna | Identifica nombre, servicio y país de los dos sub-encargados en uso |
| A.2.5.8 | **A7** | Contratación con obligaciones equivalentes | 7 | "El Cliente otorga autorización general al Proveedor para contratar subencargados" | 🟡 | Alta | La autorización general es admisible, pero faltan las obligaciones en cascada |
| A.2.5.9 | **A7** | Aviso previo de cambio y objeción | 7 | "publicará en su sitio web las actualizaciones de la lista de subencargados" | 🔴 | Crítica | Aviso posterior y pasivo; sin preaviso (política: 30 días) ni objeción |
| A.3.9 | SoA | Derechos de acceso y confidencialidad | 4 | "su personal está sujeto a obligaciones de confidencialidad" | 🟡 | Alta | Sin necesidad de conocer ni pervivencia tras la relación |
| A.3.10 | **A7** | Seguridad y aviso en acuerdos | 5, 6 | "dentro de las 72 horas siguientes a haber tenido conocimiento" | 🔴 | Crítica | 72 h > 24 h de política; deja al Responsable sin margen ante la ANPD |
| A.3.11 | SoA | Procedimiento de gestión de incidentes | No localizada | — | ⚪ | Alta | Sin compromiso de procedimiento documentado |
| A.3.12 | **SoA** | Contenido del aviso y cooperación | 6 | "notificará al Cliente cualquier violación de seguridad de datos personales" | 🟡 | Alta | Sin contenido mínimo del aviso ni cooperación ante la ANPD |
| A.3.13 | SoA | Requisitos legales y contractuales | 11 | "se rige por las leyes de la República del Perú" | 🟡 | Alta | Sin compromiso expreso de cumplir la Ley N.° 29733 ni Oficial de Datos Personales |
| A.3.15 | SoA | Revisión independiente | 9 | "un resumen de su informe de auditoría más reciente" | 🟡 | Alta | Sin tipo, alcance ni fecha; no consta SOC 2 Tipo II de ≤12 meses |

Los 19 controles marcados **SoA** se envían como insumo al **Agente 3**, que consolida su
estado en la Declaración de Aplicabilidad. Los 5 marcados **A7** los decide este agente.

## 5. Contraste con la Ley N.° 29733 y la política interna

| Parámetro | Política interna v1.1 | Contrato | Resultado |
|---|---|---|---|
| Aviso de incidentes | ≤ 24 h | 72 h (cl. 6) | 🔴 Impide notificar a la ANPD dentro de las 48 h del Reglamento |
| Asistencia en derechos | ≤ 5 días hábiles | "en la medida de lo razonable" (cl. 8) | 🟡 Sin plazo |
| Devolución o eliminación | ≤ 30 días | "plazo razonable", respaldos excluidos (cl. 10) | 🟡 Sin plazo ni certificado |
| Aviso de cambio de sub-encargado | 30 días de preaviso | Publicación en web (cl. 7) | 🔴 Aviso posterior |
| Países de tratamiento | Perú + UE/EEE (31 países) | EE. UU. e India, sin garantías (cl. 7) | Alerta Alta |

**Ley N.° 29733 y Reglamento (D.S. 016-2024-JUS).** Tres puntos concretos:

1. El encargado debe informar **de inmediato** al responsable ante un incidente, y el
   responsable notificar a la ANPD **dentro de las 48 h**. Un aviso contractual de 72 h
   consume el plazo legal antes de que el Responsable tenga noticia. Las 72 h son el
   plazo del RGPD: aquí no aplica y no sustituye al peruano.
2. El art. 15 condiciona el flujo transfronterizo a un nivel de protección adecuado en
   destino o a garantías del emisor. La cl. 7 no identifica ninguna de las dos vías para
   EE. UU. ni para India.
3. El encargado **no puede tratar los datos para fines propios**; si lo hace, asume
   responsabilidad como responsable. La excepción de la cl. 3 lo coloca exactamente en
   ese supuesto.

El RGPD no se declara aplicable en este contrato, por lo que solo se menciona como
referencia informativa y no modifica el semáforo.

## 6. Alertas (riesgo y renovación)

| Prioridad | Tipo | Descripción | Controles | Origen |
|---|---|---|---|---|
| **Alta** | Riesgo | Uso de las grabaciones para fines propios (entrenar modelos de analítica de voz); anonimización invocada sin método definido | A.2.2.3, A.2.2.4 | modelo |
| **Alta** | Seguridad | Aviso de incidentes en 72 h, mayor al máximo interno de 24 h; impide notificar a la ANPD en 48 h | A.3.10, A.3.12 | modelo |
| **Alta** | Riesgo | Sub-encargados en EE. UU. e India, fuera de `paises_aprobados`, sin garantías ni mecanismo de transferencia | A.2.5.2, A.2.5.3, A.2.5.8 | modelo |
| Media | Riesgo | Certificación ISO/IEC 27001 solo declarada, sin certificado, alcance ni vigencia, con riesgo PII Alto | A.3.15, A.2.2.6 | modelo |
| Media | Riesgo | Uso de IA sobre los datos sin evidencia de gobernanza de IA | A.2.2.3 | modelo |
| Media | Renovación | Sin fecha de fin de vigencia ni mecanismo de revisión periódica definido | A.1.2.7 | **script** |

## 7. Puntaje del proveedor

| Dimensión | Puntaje base |
|---|---|
| Contractual (A.2.2.x, A.2.3.2) | 31,8 |
| Ciclo de vida del dato (A.2.4.x) | 45,0 |
| Transferencias y sub-encargados (A.2.5.x) | 42,2 |
| Seguridad e incidentes (A.3.x) | 32,5 |
| **Puntaje base total** | **37,5** |
| Penalización (3 alertas Altas × −5) | **−15** |
| **Total** | **22 / 100 — Riesgo alto** |

Cálculo por `scripts/calcular_resultado.py` (`trazabilidad.calculo: "script"`), con los
pesos de criterios §8: 3 para los 9 controles críticos, 1 para los 15 restantes;
factores Cumple 1,0 · Parcial 0,5 · Sin evidencia 0,25 · No cumple 0.
Σ(peso × factor) / Σ(peso) = 15,75 / 42 = 0,375.

**Dictamen:** regla A → *No recomendable sin enmiendas* (hay alertas Altas y severidades
Críticas); regla B → *No recomendable sin enmiendas* (22 < 50). Coinciden.

## 8. Plan de remediación

| Prioridad | Control | Acción | Cláusula baseline |
|---|---|---|---|
| Alta | A.2.2.3 | Suprimir de la cl. 3 la excepción de fines propios y limitar el uso de IA a los fines del Responsable | 2 y 17 |
| Alta | A.3.10 | Aviso de incidentes en ≤ 24 h, con contenido mínimo y cooperación ante la ANPD | 14 |
| Alta | A.2.5.2 | Identificar base y mecanismo de transferencia con garantías equivalentes a la Ley 29733 para EE. UU. e India | 10 |
| Alta | A.2.5.9 | Aviso previo de 30 días de alta o cambio de sub-encargado, con derecho de objeción | 12 |
| Alta | A.2.5.3 | Cerrar la lista de países en un anexo | 10 |
| Alta | A.2.5.8 | Contrato escrito con obligaciones equivalentes para cada sub-encargado; responsabilidad del Encargado por ellos | 12 |
| Alta | A.2.4.3 | Devolución o eliminación en 30 días a elección del Responsable, respaldos incluidos, con certificado | 9 |
| Alta | A.2.2.2 | Anexo 1 con objeto, duración, naturaleza, finalidad y categorías de datos y titulares | 1 |
| Alta | A.3.12 | Detallar contenido mínimo del aviso de incidente y cooperación posterior | 14 |
| Media | A.2.3.2 | Reenvío de solicitudes en 2 días hábiles y asistencia en ≤ 5 días hábiles | 7 |
| Media | A.2.2.6 | Derecho de auditoría con preaviso de 10 días hábiles; entregar certificado ISO 27001 con alcance | 5 |
| Media | A.2.4.4 | Cifrado de toda transmisión por redes y anexo de medidas concretas | 8 |
| Media | A.2.2.4 | Prohibición expresa de marketing y publicidad | 3 |
| Media | A.2.2.5 | Deber de informar instrucciones que infrinjan la norma | 4 |
| Media | A.2.2.7 | Registro de actividades de tratamiento, entregable a solicitud | 6 |
| Media | A.2.5.4 | Registro de comunicaciones a terceros | 11 |
| Media | A.2.5.5 | Aviso previo ante requerimientos de autoridad, salvo prohibición legal | 11 |
| Media | A.2.5.6 | Rechazo de solicitudes no vinculantes y entrega limitada a lo exigido | 11 |
| Media | A.3.9 | Acceso por necesidad de conocer y confidencialidad que subsista | 13 |
| Media | A.3.11 | Procedimiento documentado de gestión de incidentes | 14 |
| Media | A.3.13 | Compromiso expreso con la Ley 29733 y designación de Oficial de Datos Personales | 15 |
| Media | A.3.15 | Informe de revisión independiente identificable (SOC 2 Tipo II ≤ 12 meses) o certificación vigente | 5 |
| Media | A.1.2.7 | Fecha de firma, vigencia con fin expreso, renovación, preaviso y revisión anual | 16 |
| Baja | A.2.4.2 | Plazo máximo documentado de eliminación de archivos temporales | 8 |

## 9. Borrador de correo al proveedor

> **Asunto:** Observaciones al Acuerdo de Tratamiento de Datos Personales — enmiendas y evidencias requeridas
>
> Estimados señores de NubeAndina Contact Services S.A.C.:
>
> Hemos revisado el Acuerdo de Tratamiento de Datos Personales propuesto conforme a la
> Ley N.° 29733, su Reglamento (D.S. 016-2024-JUS) y nuestro sistema de gestión de
> privacidad, alineado con ISO/IEC 27701:2025. Antes de proceder a la firma requerimos
> las siguientes enmiendas:
>
> 1. **Cláusula 3 — Limitación de fines.** Suprimir la facultad de utilizar información
>    derivada de las grabaciones para mejorar modelos propios de analítica de voz. El
>    tratamiento debe limitarse a los fines que esta parte indique.
> 2. **Cláusula 6 — Incidentes.** Reducir el plazo de aviso a un máximo de 24 horas desde
>    su conocimiento, precisar el contenido mínimo del aviso (naturaleza, categorías y
>    volumen de datos y titulares afectados, consecuencias probables, medidas adoptadas y
>    punto de contacto) y comprometer cooperación en las notificaciones a la ANPD y a los
>    titulares.
> 3. **Cláusula 7 — Transferencias y sub-encargados.** Incluir la lista cerrada de países
>    en un anexo, identificar el mecanismo de transferencia y las garantías de protección
>    equivalente a la Ley N.° 29733 para Estados Unidos e India, sustituir la publicación
>    en web por aviso previo de 30 días con derecho de objeción, y acreditar que cada
>    sub-encargado está vinculado por contrato escrito con obligaciones equivalentes.
> 4. **Cláusula 10 — Fin del encargo.** Devolución o eliminación a nuestra elección en un
>    plazo de 30 días, incluidas las copias de respaldo, con certificado de eliminación.
> 5. **Anexo de instrucciones.** Incorporar objeto, duración, naturaleza, finalidad y
>    categorías de datos y de titulares, junto con el detalle de la asistencia que
>    prestarán en derechos de titulares, evaluaciones de impacto e incidentes.
> 6. **Vigencia.** Fijar fecha de firma, inicio y fin de vigencia, régimen de renovación,
>    preaviso de terminación y una revisión anual del acuerdo.
>
> Asimismo, solicitamos la siguiente documentación:
>
> - Certificado ISO/IEC 27001 vigente, con su alcance y fecha de caducidad.
> - El informe de auditoría independiente más reciente, identificando su tipo y fecha
>   (de disponer de SOC 2 Tipo II, con antigüedad no mayor a 12 meses).
> - Descripción de los sistemas de inteligencia artificial que aplican sobre los datos
>   —en particular la transcripción automática de TranscribePro Ltd. y la analítica de
>   voz— junto con la evidencia de gobernanza de IA de que dispongan, por ejemplo
>   ISO/IEC 42001.
>
> Quedamos a disposición para revisar en detalle cada punto.
>
> *[Borrador — requiere aprobación del DPO y de Legal antes de su envío]*

## 10. Aprobaciones requeridas (DPO → Legal)

| Orden | Aprobador | Decide | Estado |
|---|---|---|---|
| 1 | **DPO** | Valida el dictamen, el nivel de riesgo y el alcance de las enmiendas | **Pendiente** |
| 2 | **Legal** | Aprueba las enmiendas y la firma del DPA nuevo | En espera de la decisión del DPO |

Este informe **no constituye una aprobación**. El estado del registro queda en
`Pendiente DPO` y ningún borrador se envía al proveedor sin ambas aprobaciones.

## 11. Supuestos, limitaciones y trazabilidad

**Supuestos**

- Ficha del tercero inferida del propio contrato; no se entregaron ID de tercero del
  inventario PIMS ni ID de contrato (null).
- Riesgo PII Alto por datos financieros (historial de pagos y saldos de deuda) y por
  superar los 100 000 titulares (~180 000 según cl. 2).
- Fecha de firma, inicio y fin de vigencia, renovación automática y preaviso de
  terminación no localizados en el contrato (null).
- La ISO/IEC 27001 de la cl. 5 se trata como certificación aceptada pese a no indicar
  versión; sin certificado, alcance ni vigencia, su estado es *Declarada sin evidencia*.
- El informe de auditoría de la cl. 9 no se identifica como SOC 2 Tipo II, por lo que no
  cuenta como certificación aceptada.
- Ni Estados Unidos ni India figuran en `paises_aprobados` de la configuración v1.1, y el
  contrato no aporta garantías contractuales de transferencia.
- La mención a información "agregada y anonimizada" no acredita anonimización efectiva,
  al no definirse método ni umbral.

**Limitaciones**

- Los resúmenes de controles están parafraseados y la numeración proviene de fuentes
  secundarias: debe verificarse contra el texto oficial licenciado de ISO/IEC 27701:2025
  (Anexos A y F) antes de cualquier uso formal.
- Evaluación **documental**: verifica lo que el contrato obliga, no la implementación
  técnica real del proveedor.
- **No constituye asesoría legal.**
- Los parámetros de política interna son decisiones de diseño de la configuración v1.1 y
  están pendientes de validación por el DPO.

**Trazabilidad**

| Campo | Valor |
|---|---|
| Versión de skill | 1.1 |
| Versión de configuración | 1.1 |
| Evaluador | Agente 7 (Terceros/DPA) — Claude Opus 5 en Claude Code, skill instalada en `~/.claude/skills/pims-dpa-auditor` |
| Cálculo | **script** (`calcular_resultado.py`, esquema válido) |
| Fecha de referencia | 2026-10-07 |
| ID de evaluación | DPA-20261007-NACS |
