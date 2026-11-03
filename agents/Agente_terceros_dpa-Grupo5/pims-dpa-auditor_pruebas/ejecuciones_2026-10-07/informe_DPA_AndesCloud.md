# Informe de evaluación DPA — AndesCloud Hosting S.A.C.

## 1. Resumen ejecutivo

| Elemento | Resultado |
|---|---|
| Dictamen | **Recomendable** |
| Puntaje del proveedor | **100 / 100 — Riesgo bajo** (base 100,0 − 0) |
| Nivel de riesgo PII | **Medio** (datos identificativos y de contacto de clientes; Supuesto) |
| Controles evaluados | 24 — 🟢 24 · 🟡 0 · 🔴 0 · ⚪ 0 · ➖ 0 |
| Alertas | 0 Altas · 1 Media (de renovación, generada por el script) |
| Estado de aprobación | **Pendiente DPO** → luego Legal |

El acuerdo cubre los 24 controles evaluados con cláusulas explícitas y plazos concretos
que no superan ningún parámetro de la política interna. Prohíbe expresamente los fines
propios y el uso de IA, notifica incidentes en 24 h, limita el tratamiento a Perú y
Alemania con cláusulas de protección equivalente, y adjunta certificación e informe
independiente verificables. **No requiere enmiendas.**

Un único punto de gestión, sin efecto en el puntaje: el plazo para preavisar la
terminación vence el **2 de diciembre de 2026**, dentro de la ventana de 60 días. Si no
se desea la renovación automática por un año más, hay que decidirlo antes de esa fecha
(sección 6).

## 2. Ficha del tercero, rol y vigencia del contrato

| Campo | Valor |
|---|---|
| Proveedor | AndesCloud Hosting S.A.C. (Arequipa, Perú) |
| Rol | **Encargado** — el contrato designa expresamente a las partes como Responsable y Encargado |
| Servicio | Alojamiento (hosting) de la plataforma de ventas del Responsable |
| Categorías de datos | Identificativos y de contacto de clientes de la plataforma, según el Anexo 1 |
| Países de tratamiento | Perú · Alemania (ambos en `paises_aprobados`) |
| Sub-encargados | DataVault GmbH (Alemania, respaldo cifrado), con garantías de transferencia |
| Fecha de firma | 2026-01-15 |
| Vigencia | 2026-02-01 → **2027-01-31** |
| Renovación automática | **Sí**, anual, salvo preaviso |
| Preaviso de terminación | **60 días** → fecha límite: 2026-12-02 |
| Ley aplicable | Ley N.° 29733 y su Reglamento (D.S. 016-2024-JUS), cl. 13 |
| Hash SHA-256 del documento | `40de16dbfdd638a30bfcc42171bb485c…` (registrado completo en el JSON) |
| ID tercero / ID contrato | No entregados (null) |

## 3. Idoneidad: certificaciones y uso de IA

| Certificación / informe | Tipo | Estado | Observación |
|---|---|---|---|
| ISO/IEC 27001:2022 | Aceptada | **Verificada con evidencia** | Certificado anexo, alcance declarado (servicios de hosting), vigente hasta 31/03/2028 |
| SOC 2 Tipo II | Aceptada | **Verificada con evidencia** | Último informe del 30/06/2026, anexo, con entrega anual comprometida. Antigüedad 3,2 meses, por debajo del máximo de 12 |
| ISO/IEC 42001:2023 | Complementaria | No presentada | **No se requiere**: la cl. 2 prohíbe el uso de IA sobre los datos |

Es la diferencia de fondo con un contrato deficiente: aquí las certificaciones no están
*declaradas*, están **anexadas, fechadas y con alcance**, lo que permite verificarlas.

**Uso de IA: no detectado.** La cl. 2 prohíbe expresamente el uso de los datos para
analítica y entrenamiento de modelos de IA, y declara que el Encargado no aplica sistemas
de IA sobre ellos. No procede exigir evidencia de gobernanza de IA.

## 4. Matriz de controles ISO/IEC 27701:2025

Ámbito: **A7** = propio del Agente 7 · **SoA** = insumo para el Agente 3.

| Control | Ámbito | Requisito (resumen) | Cláusula | Evidencia (cita ≤20 palabras) | Estado | Severidad | Observación |
|---|---|---|---|---|---|---|---|
| A.2.2.2 | SoA | Instrucciones documentadas y asistencia | 1 | "solo según las instrucciones documentadas del Anexo 1" | 🟢 | Ninguna | Anexo 1 con objeto, finalidad, categorías y duración; asistencia en DPIA e incidentes |
| A.2.2.3 | SoA | Solo fines del responsable | 2 | "Se prohíbe su uso para fines propios, analítica, entrenamiento de modelos de IA" | 🟢 | Ninguna | Prohibición expresa, sin excepción de mejora del servicio |
| A.2.2.4 | SoA | Sin marketing ni publicidad | 2 | "marketing o publicidad" | 🟢 | Ninguna | Prohibición expresa |
| A.2.2.5 | SoA | Aviso de instrucción ilícita | 3 | "avisará de inmediato si una instrucción infringe la Ley N.° 29733" | 🟢 | Ninguna | Referido a la norma peruana aplicable |
| A.2.2.6 | SoA | Información y derecho de auditoría | 4 | "permite auditorías con preaviso de 10 días hábiles" | 🟢 | Ninguna | Auditoría efectiva más certificación e informe anexos |
| A.2.2.7 | SoA | Registros del tratamiento | 4 | "mantiene un registro de las actividades de tratamiento por cuenta del Responsable" | 🟢 | Ninguna | Registro comprometido |
| A.2.3.2 | SoA | Asistencia en derechos de titulares | 5 | "Reenviará toda solicitud en 2 días hábiles y asistirá en un máximo de 5 días hábiles" | 🟢 | Ninguna | Igual al máximo de política (5 días hábiles) |
| A.2.4.2 | SoA | Archivos temporales | 6 | "Los archivos temporales se eliminan en 7 días" | 🟢 | Ninguna | Período concreto |
| A.2.4.3 | SoA | Devolución o eliminación al término | 7 | "devolverá o eliminará los datos y respaldos en 30 días y emitirá certificado" | 🟢 | Ninguna | A elección del Responsable, respaldos incluidos, con certificado |
| A.2.4.4 | SoA | Controles de transmisión | 6 | "Toda transmisión se cifra con TLS 1.2 o superior" | 🟢 | Ninguna | Medida técnica concreta |
| A.2.5.2 | SoA | Base de transferencias internacionales | 8 | "cláusulas contractuales que imponen protección equivalente a la Ley N.° 29733" | 🟢 | Ninguna | Mecanismo identificado, con aviso de 30 días y objeción |
| A.2.5.3 | SoA | Lista de países destino | 8 | "Los datos se alojan solo en Perú y Alemania (Anexo 2)" | 🟢 | Ninguna | Lista cerrada; ambos en `paises_aprobados` |
| A.2.5.4 | SoA | Registro de comunicaciones a terceros | 9 | "Registra toda comunicación a terceros" | 🟢 | Ninguna | Obligación expresa |
| A.2.5.5 | SoA | Aviso de solicitudes de autoridades | 9 | "notificará al Responsable antes de comunicar, salvo prohibición legal" | 🟢 | Ninguna | Aviso previo con la única excepción admisible |
| A.2.5.6 | SoA | Solo comunicaciones vinculantes | 9 | "solo entregará lo legalmente exigido" | 🟢 | Ninguna | Entrega limitada a lo exigible |
| A.2.5.7 | **A7** | Divulgación de sub-encargados | 10 | "Anexo 3: DataVault GmbH, respaldo cifrado, Alemania" | 🟢 | Ninguna | Identificado con nombre, servicio y país |
| A.2.5.8 | **A7** | Contratación con obligaciones equivalentes | 10 | "Todo sub-encargado firma contrato con obligaciones equivalentes" | 🟢 | Ninguna | Obligaciones en cascada; el Encargado responde por ellos |
| A.2.5.9 | **A7** | Aviso previo de cambio y objeción | 10 | "Cambios con aviso previo de 30 días y derecho de objeción" | 🟢 | Ninguna | Igual al mínimo de política (30 días) |
| A.3.9 | SoA | Derechos de acceso y confidencialidad | 11 | "Acceso limitado al personal que lo necesita, con confidencialidad que subsiste" | 🟢 | Ninguna | Necesidad de conocer y pervivencia del deber |
| A.3.10 | **A7** | Seguridad y aviso en acuerdos | 12, 13 | "notificará al Responsable en máximo 24 horas" | 🟢 | Ninguna | Igual al máximo de política; deja margen ante la ANPD |
| A.3.11 | SoA | Procedimiento de gestión de incidentes | 12 | "mantiene un procedimiento de gestión de incidentes" | 🟢 | Ninguna | Procedimiento comprometido |
| A.3.12 | SoA | Contenido del aviso y cooperación | 12 | "indicando naturaleza, datos y titulares afectados, consecuencias, medidas y contacto" | 🟢 | Ninguna | Contenido mínimo completo y cooperación con la ANPD y titulares |
| A.3.13 | SoA | Requisitos legales y contractuales | 13 | "Cumplirá la Ley N.° 29733 y su Reglamento (D.S. 016-2024-JUS)" | 🟢 | Ninguna | Compromiso expreso y Oficial de Datos Personales designado |
| A.3.15 | SoA | Revisión independiente | 4 | "Entrega anualmente su informe SOC 2 Tipo II (último: 30/06/2026)" | 🟢 | Ninguna | Informe fechado, dentro de los 12 meses, con entrega anual |

Los 19 controles marcados **SoA** se envían como insumo al **Agente 3** para la
Declaración de Aplicabilidad. Los 5 marcados **A7** los decide este agente.

## 5. Contraste con la Ley N.° 29733 y la política interna

| Parámetro | Política interna v1.1 | Contrato | Resultado |
|---|---|---|---|
| Aviso de incidentes | ≤ 24 h | **24 h** (cl. 12) | 🟢 En el límite; deja margen para notificar a la ANPD en 48 h |
| Asistencia en derechos | ≤ 5 días hábiles | **5 días hábiles** (cl. 5) | 🟢 En el límite; reenvío en 2 días hábiles |
| Devolución o eliminación | ≤ 30 días | **30 días**, respaldos incluidos, con certificado (cl. 7) | 🟢 En el límite |
| Aviso de cambio de sub-encargado | 30 días de preaviso | **30 días** con objeción (cl. 10) | 🟢 En el límite |
| Países de tratamiento | Perú + UE/EEE (31 países) | **Perú y Alemania** (cl. 8) | 🟢 Ambos aprobados, y con garantías |
| Antigüedad del informe SOC 2 | ≤ 12 meses | 3,2 meses (30/06/2026) | 🟢 |

Los cuatro plazos coinciden exactamente con los máximos de la política interna, no los
superan. Conforme a criterios §2, un plazo igual al parámetro es 🟢; solo uno **mayor**
degradaría el control.

**Ley N.° 29733 y Reglamento.** La cl. 13 incorpora el compromiso expreso de cumplir
ambos y designa un Oficial de Datos Personales con contacto, lo que satisface la
exigencia del Reglamento para encargados. El flujo transfronterizo a Alemania se apoya en
cláusulas contractuales de protección equivalente, una de las vías del art. 15. La cl. 2
excluye el tratamiento para fines propios, de modo que el proveedor no corre el riesgo de
convertirse en responsable.

## 6. Alertas (riesgo y renovación)

| Prioridad | Tipo | Descripción | Controles | Origen |
|---|---|---|---|---|
| Media | Renovación | Renovación automática: el plazo para preavisar termina el **2026-12-02** | A.1.2.7 | **script** |

**Ninguna alerta de riesgo.** No se cumple ningún disparador de criterios §6: no hay
fines propios, ni países fuera de la lista aprobada, ni falta de aviso de incidentes, ni
ausencia de devolución o eliminación, ni certificaciones sin evidencia, ni falta de
derecho de auditoría, ni uso de IA.

**Sobre la alerta de renovación.** Es sensible a la fecha de evaluación y no indica
ningún defecto del contrato:

| | 01/10/2026 | **07/10/2026 (esta evaluación)** |
|---|---|---|
| Fin de vigencia | 2027-01-31 | 2027-01-31 |
| Fecha límite de preaviso (fin − 60 días) | 2026-12-02 | 2026-12-02 |
| Ventana de alerta (referencia + 60 días) | hasta 2026-11-30 | hasta **2026-12-06** |
| ¿Límite dentro de la ventana? | No → sin alerta | **Sí → alerta Media** |

Es la oportunidad de renegociar antes de que el acuerdo se renueve por otro año. No
penaliza el puntaje: solo las alertas **Altas** restan (−5 cada una, hasta −20).

## 7. Puntaje del proveedor

| Dimensión | Puntaje base |
|---|---|
| Contractual (A.2.2.x, A.2.3.2) | 100,0 |
| Ciclo de vida del dato (A.2.4.x) | 100,0 |
| Transferencias y sub-encargados (A.2.5.x) | 100,0 |
| Seguridad e incidentes (A.3.x) | 100,0 |
| **Puntaje base total** | **100,0** |
| Penalización (0 alertas Altas) | **−0** |
| **Total** | **100 / 100 — Riesgo bajo** |

Los 24 controles en 🟢 dan factor 1,0 en todos los pesos: Σ(peso × factor) / Σ(peso) =
42 / 42 = 1,0. Cálculo por `scripts/calcular_resultado.py`
(`trazabilidad.calculo: "script"`, esquema válido).

**Dictamen:** regla A → *Recomendable* (sin alertas Altas y sin severidades distintas de
Ninguna); regla B → *Recomendable* (100 ≥ 80). Coinciden.

## 8. Plan de remediación

**No se requieren enmiendas.** No hay controles en 🟡, 🔴 ni ⚪, de modo que el plan de
remediación está vacío (`remediacion: []` en el JSON).

Dos acciones de gestión, no de remediación contractual:

| Prioridad | Asunto | Acción |
|---|---|---|
| Media | Vigencia (A.1.2.7) | Decidir antes del **2026-12-02** si se deja operar la renovación automática o se preavisa la terminación |
| Baja | Anexos 1 a 4 | Verificar que los anexos citados (instrucciones, países, sub-encargados y medidas de seguridad) se adjunten firmados; se dan por existentes por remisión contractual pero no se aportaron |

## 9. Borrador de correo al proveedor

**No procede un correo de enmiendas.** El contrato no requiere cambios. Si el DPO desea
cerrar los dos puntos de la sección 8, este es el borrador:

> **Asunto:** Acuerdo de Encargo de Tratamiento — confirmación de anexos y de vigencia
>
> Estimados señores de AndesCloud Hosting S.A.C.:
>
> Hemos completado la revisión del Acuerdo de Encargo de Tratamiento conforme a la Ley
> N.° 29733, su Reglamento (D.S. 016-2024-JUS) y nuestro sistema de gestión de
> privacidad, alineado con ISO/IEC 27701:2025. El acuerdo cubre satisfactoriamente los
> controles aplicables y no requiere enmiendas.
>
> Para completar nuestro expediente les solicitamos únicamente:
>
> 1. Copia firmada de los Anexos 1 a 4 (instrucciones de tratamiento, países, lista de
>    sub-encargados y medidas de seguridad), citados en el acuerdo.
> 2. Confirmación del procedimiento y del punto de contacto para ejercer el preaviso de
>    terminación, cuyo plazo vence el 2 de diciembre de 2026.
>
> Agradecemos la claridad del documento, en particular la limitación de fines, los plazos
> de notificación de incidentes y la documentación de certificación adjunta.
>
> *[Borrador — requiere aprobación del DPO y de Legal antes de su envío]*

## 10. Aprobaciones requeridas (DPO → Legal)

| Orden | Aprobador | Decide | Estado |
|---|---|---|---|
| 1 | **DPO** | Valida el dictamen y la decisión sobre la renovación automática | **Pendiente** |
| 2 | **Legal** | Aprueba la firma del DPA | En espera de la decisión del DPO |

Un dictamen *Recomendable* **no es una aprobación**. El estado del registro queda en
`Pendiente DPO` y la firma requiere ambas aprobaciones.

## 11. Supuestos, limitaciones y trazabilidad

**Supuestos**

- Ficha del tercero inferida del propio contrato; no se entregaron ID de tercero del
  inventario PIMS ni ID de contrato (null).
- Riesgo PII **Medio**: el contrato remite las categorías de datos al Anexo 1, que no se
  adjuntó. Se asume tratamiento de datos identificativos y de contacto de clientes en
  volumen relevante, sin datos sensibles ni financieros declarados. Criterios §1: si no
  se puede determinar, Medio.
- Los Anexos 1 a 4 se citan en el contrato pero no se aportaron; su contenido se da por
  existente según la remisión contractual y debe verificarse antes de la firma.
- Antigüedad del informe SOC 2 calculada a la fecha de evaluación (07/10/2026) sobre el
  informe del 30/06/2026: 3,2 meses.
- Perú y Alemania figuran en `paises_aprobados` de la configuración v1.1, por lo que la
  transferencia a Alemania no genera alerta; aun así el contrato aporta cláusulas de
  protección equivalente.

**Limitaciones**

- Los resúmenes de controles están parafraseados y la numeración proviene de fuentes
  secundarias: debe verificarse contra el texto oficial licenciado de ISO/IEC 27701:2025
  (Anexos A y F) antes de cualquier uso formal.
- Evaluación **documental**: un 100/100 significa que el contrato obliga correctamente,
  **no** que el proveedor haya implementado las medidas. La verificación de la
  implementación real queda fuera de este alcance.
- **No constituye asesoría legal.**
- Los parámetros de política interna son decisiones de diseño de la configuración v1.1 y
  están pendientes de validación por el DPO.
- Los Anexos 1 a 4 no se revisaron por no haberse aportado; varios controles en 🟢 se
  apoyan en la remisión del contrato a esos anexos.

**Trazabilidad**

| Campo | Valor |
|---|---|
| Versión de skill | 1.1 |
| Versión de configuración | 1.1 |
| Evaluador | Agente 7 (Terceros/DPA) — Claude Opus 5 en Claude Code, skill instalada en `~/.claude/skills/pims-dpa-auditor` |
| Cálculo | **script** (`calcular_resultado.py`, esquema válido) |
| Fecha de referencia | 2026-10-07 |
| ID de evaluación | DPA-20261007-ACH |
