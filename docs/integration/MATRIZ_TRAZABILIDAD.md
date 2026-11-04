# Matriz de trazabilidad: equipo → norma

Muestra qué norma y qué requisito respalda a cada equipo, **dónde está implementado** y **cómo se verificó**.
Se construyó leyendo el código y el conocimiento de cada agente; no se reproduce texto de las normas.

**Cómo leerla.** «Evidencia en el agente» es el archivo o la regla donde el grupo usa el requisito. «Verificación» dice qué prueba de esta integración lo ejercita (modo `cloud`). Una celda sin prueba significa que **no está verificado**, aunque el grupo lo declare. La plataforma **no valida** el contenido normativo contra las ediciones oficiales: el respaldo es el que cada grupo cargó en su agente.

Normas: **ISO/IEC 27701:2025** (A.1 responsables, A.2 encargados, A.3 seguridad), **Ley N.° 29733** y su **Reglamento D.S. 016-2024-JUS** (vigente desde 30/03/2025), **ISO 19011:2018**, **ENISA 2013**, **ISO/IEC 27002**.

## 1. Equipo → norma

### Grupo 1 · Formación y concientización
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| ISO/IEC 27701 **A.3.17** Concienciación y formación | Capacitaciones y su seguimiento | Skill `formacion-conciencia-iso27701` (10 menciones); G7 lo asigna a «Agente de Formación» | El chat responde (`test_g1_chat_returns_text`) | No se verificó que las respuestas citen el control |
| ISO/IEC 27701 **A.3.11** (planificación de incidentes) | Lecciones tras incidentes | Skill (2 menciones); flujo G8 → G1 | `test_g8_incident_lessons_reach_g1` | La conexión es por texto, no por el control |
| Ley 29733 y D.S. 016-2024-JUS | Contenido de las capacitaciones | `knowledge_base/normativas/peru/` (ley, reglamento, GDPR-ready) | — | Cargados por el grupo, sin validación |
| ISO/IEC 27001, 27002, 27701, 29100 y reglamentos UNSA | Base de conocimiento | `knowledge_base/normativas/iso/` y `reglamentos_unsa/` | — | Transcripciones del grupo |

### Grupo 2 · Evaluación de riesgos
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| ISO/IEC 27701:2025 **cláusula 6.1.2** (evaluación de riesgos de privacidad) | Metodología de evaluación | Norma indexada en Qdrant (OCR de 72 páginas); skill de evaluación | `test_g2_chat_uses_ingested_norm_when_unlocked` cita 6.1.2 (págs. 13–14) | Prueba omitida si el control de alcance está cerrado; OCR con 93,5 % de confianza media |
| ISO/IEC 27701:2025 **6.1.3** y **8.2** | Tratamiento y evaluación | Recuperación desde Qdrant | Probado a mano (respuesta citó 6.1.3) | Sin prueba automática |
| Alcance «Gestión de Riesgos» (GR-01 a GR-06), solo ISO 27701:2025 | Limita las respuestas | `scope-policy.json` + puerta de Express | `test_g2_out_of_scope_question_is_refused_by_the_agent` | La política cita un extracto de 20 páginas; aquí se indexó el documento completo |
| G7 asigna **A.1.2.6** (DPIA) a «Agente de Riesgos» | Evaluación de impacto | Catálogo de G7 | — | No existe flujo G2 → G7 (salida en texto libre) |

### Grupo 3 · Derechos de titulares (DSAR)
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| D.S. 016-2024-JUS **art. 69.1** (información: 8 días hábiles) | Plazo | `perfil-pe-ley29733.md`, motor de plazos | `test_g3_information_deadline_is_8_business_days` | Determinista |
| **art. 69.2** (acceso: 20 días) y política interna (15) | Plazo | Perfil legal + política de la organización | `test_g3_deadlines_deterministic` y el caso de la web | La política solo puede acortar |
| **art. 69.3** (rectificación, cancelación, oposición: 10 días) y **arts. 82–85** (cancelación) | Plazo y derecho | Perfil legal | `test_g3_case_without_verified_identity...` (supresión = 10 días) | |
| **art. 71** (ampliación) y **art. 76.1** (portabilidad) | Prórroga y portabilidad | Perfil legal, procedimientos | — | Sin prueba específica |
| ISO/IEC 27701 **A.1.3.7**, A.1.3.9, A.1.3.10, A.1.3.2, A.1.3.5, A.1.3.6, A.1.3.8, A.1.3.11 | Atención de derechos | `knowledge/references/iso-control-map.md` | `test_g3_norm_query_returns_citable_fragments` | El mapa es un resumen del propio grupo |
| ISO/IEC 27701 **A.3.9, A.3.14, A.3.25, A.3.31** | Seguridad del caso (acceso, registros, logs) | Mapa de controles | — | Sin prueba específica |
| Handoffs: **A.3.14** → evidencia, **A.1.3.8** → terceros, **A.1.2.9** → inventario | Entrega a otros agentes | `storage/handoffs.py` | `test_dsar_full_cycle_with_real_human_decision_then_handoffs` | G5 no recibe handoffs |
| Decisión humana (`APPROVED`/`REJECTED` solo por una persona) | Regla del agente | `decisions.decide` | `test_dsar_full_cycle...`, `test_roles_are_enforced` | Exigido por la guía del grupo, no por una cláusula |

### Grupo 4 · Evidencia y auditoría
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| ISO/IEC 27701:2025 (catálogo de controles) | Qué evidencia se espera | `references/controles_iso27701.md` | `test_g4_audit_structure_and_hash` | Sus IDs (CL-, RT-, EN-, SG-) son **propios**, no números de la norma; el archivo mismo dice «numeración referencial» |
| ISO 19011:2018 | Método de auditoría | Encabezado de su CLI y skill (M1, M2, M3) | — | Sin prueba |
| Ley 29733 / D.S. 016-2024-JUS | Marco legal | `references/ley29733_resumen.md` | — | Resumen del grupo |
| Criterios: pertinencia, suficiencia, vigencia, aprobación, trazabilidad, completitud | Clasificación (No conformidad mayor/menor…) | `criterios_evaluacion.md` | Severidad devuelta en las pruebas | La severidad se extrae de frases del modelo |
| Integridad: SHA-256 del texto | Trazabilidad de la evidencia | `app_dashboard.py` | `test_g4_audit_structure_and_hash` (valor exacto) | El hash identifica el texto, no prueba cadena de custodia |

### Grupo 5 · Terceros y DPA
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| ISO/IEC 27701 **A.2.2** (condiciones), **A.2.3** (titulares), **A.2.4** (privacidad desde el diseño), **A.2.5** (compartición y transferencia), **A.3** (seguridad): **26 controles** | Matriz de controles del contrato | `pims-dpa-auditor/references/controles_iso27701_2025.md`, `n8n/lib/calcular.js` | `test_g5_audit_is_persisted_in_gestitel_with_26_controls...` | |
| **A.2.5.7** (subcontratistas), **A.3.11**, **A.3.12** (incidentes) | Controles que también conoce G7 | Resultados por control | Flujo G5 → G7: 0 → 3 controles «implementados» | Solo 3 coinciden entre catálogos |
| Puntaje: Cumple 1, Parcial 0,5, Sin evidencia 0,25, No cumple 0; críticos ×3; −5 por alerta Alta (máx. 20) | Cálculo determinista | `calcular.js` (el modelo solo califica) | `test_g5_audit_is_computed_by_code...` | Fórmula del grupo, no de la norma |
| Ley 29733, D.S. 016-2024-JUS y política interna | Contraste legal | Informe del expediente (sección 5) | — | |
| Doble aprobación DPO → Legal | Regla del agente | Flujo `pims/aprobar` | `test_g5_two_gate_approval_order_is_enforced_by_the_agent` (409) | |
| G7 asigna **A.1.2.7** (contratos con encargados) a «Agente de Terceros» | Contratos | Catálogo de G7 | Flujo G5 → G7 | |

### Grupo 6 · Inventario de datos
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| ISO/IEC 27701 **A.1.2.9** (registros de tratamiento) | Inventario y mapa de tratamientos | Handoff de G3 (`control_ref`); G7 lo asigna a «Agente de Inventario» | `test_g3_handoffs...` verifica el hash del sobre de G3 | Ni el código ni las skills de G6 citan el control |
| ISO/IEC 27701 **A.1.2.2** (identificar propósito) | Finalidad declarada por activo | G7 lo asigna a «Agente de Inventario»; campo `finalidad` | `test_g6_classifies_fields...` (contexto «Por determinar» si falta) | Idem |
| ISO/IEC 27701 (referencia general) | Marco del informe | `SKILL.md` (1 mención); informe original, págs. 8 y 12 | — | **Trazabilidad débil**: no hay artículos ni controles citados por el grupo |
| No conservar valores de datos personales | Minimización | Regla del agente | `test_g6_classifies_fields_and_never_keeps_values` | No es una cláusula citada |

### Grupo 7 · Controles y SoA
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| ISO/IEC 27701:2025 Anexo A, **A.1** responsable / **A.2** encargado / **A.3** común | Aplicabilidad por rol | `agents/controles.py::_aplica` | `test_g7_applicability_rules_by_role` (exacto) | |
| 10 controles: A.1.2.2, A.1.2.6, A.1.2.7, A.1.2.9, A.1.3.7, A.1.3.9, A.2.5.7, A.3.11, A.3.12, A.3.17 | Catálogo de la SoA | `knowledge/catalogo_controles.json` | Catálogo y SoA | **Subconjunto**, no el Anexo A completo |
| Estado de implementación según evidencias | Declaración de aplicabilidad | `_estado`, `_fila` | Flujo G5 → G7 | |
| Resumen de la 27701 y normativa UNSA | Conocimiento para el RAG | `knowledge/normativa/` | `test_g7_rag_returns_hits_through_gateway_embeddings` | |

### Grupo 8 · Incidentes y brechas
| Norma / requisito | Qué respalda | Evidencia en el agente | Verificación | Observación |
|---|---|---|---|---|
| D.S. 016-2024-JUS **art. 34.1** (notificar a la ANPD en máx. **48 h**; comunicar a los titulares) | Plazo y obligación | `knowledge/marco-normativo-peru.md`; skill `brecha-notificacion` | `test_g8_breach_analysis_produces_draft_only` (menciona 48 h) | Hay pasajes marcados `[VERIFICAR]` en el propio marco |
| **art. III num. 16** (definición de incidente) y **art. 34.7** (lineamientos de la ANPD) | Clasificación | Mismo marco | — | Sin prueba específica |
| ENISA 2013: **SE = DPC × EI + CB** | Severidad | `metodologia-severidad.md`; skill de severidad | Se ve la severidad en el resultado | No se comprobó la fórmula |
| ISO/IEC 27002 **5.24–5.28, 6.8** | Controles propuestos y evidencia | Skills de respuesta y cierre | — | Son controles de la 27002, no de la 27701 |
| G7 asigna **A.3.11** y **A.3.12** a «Agente de Incidentes» | Incidentes | Catálogo de G7 | Flujo G5 → G7 muestra esos controles | |
| Solo borradores; nada se envía sin aprobación humana | Regla del agente | Skills | `test_g8_breach_analysis_produces_draft_only` | |

## 2. Norma → equipo (vista inversa)

| Requisito | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| 27701 **6.1.2 / 6.1.3 / 8.2** (riesgos) | | ● | | | | | | |
| 27701 **A.1.2.2** (propósito) | | | | | | ◐ | ● | |
| 27701 **A.1.2.6** (DPIA) | | ◐ | | | | | ● | |
| 27701 **A.1.2.7** (contratos con encargados) | | | | | ● | | ● | |
| 27701 **A.1.2.9** (registros de tratamiento) | | | ◐ (handoff) | | | ◐ | ● | |
| 27701 **A.1.3.x** (derechos de titulares) | | | ● | | | | ◐ (A.1.3.7, A.1.3.9) | |
| 27701 **A.2.2–A.2.5** (encargados) | | | | | ● (26) | | ◐ (A.2.5.7) | |
| 27701 **A.3.9 / A.3.14** | | | ● | ◐ (recibe evidencia) | ◐ | | | |
| 27701 **A.3.11 / A.3.12** (incidentes) | ◐ (A.3.11) | | | | ● | | ● | ◐ (G7 se los asigna; su código cita ISO/IEC 27002) |
| 27701 **A.3.17** (formación) | ● | | | | | | ● | |
| D.S. 016-2024-JUS **art. 34** (brechas, 48 h) | | | | | | | | ● |
| D.S. 016-2024-JUS **arts. 69, 71, 76, 82–85** (derechos) | | | ● | | | | | |
| Ley 29733 / D.S. 016-2024-JUS (marco) | ● | | ● | ● | ● | | | ● |
| ISO 19011:2018 | | | | ● | | | | |
| ENISA 2013 | | | | | | | | ● |
| ISO/IEC 27002 | ◐ (transcripción) | | | | | | | ● |

● el agente lo implementa o lo declara como base. ◐ lo usa de forma parcial, indirecta o por un tercero (por ejemplo, G7 lo lista como responsable o llega por un handoff).

## 3. Lo que esta matriz permite afirmar, y lo que no
- **Sí:** qué requisito respalda a cada equipo según el propio agente, dónde está y qué prueba lo ejercita.
- **Sí, y está probado:** plazos de G3, reglas de aplicabilidad de G7, 26 controles de G5, hash de G4, regla de 48 h mencionada por G8, cláusula 6.1.2 recuperada por G2.
- **No:** que los textos normativos coincidan con las ediciones oficiales. Los catálogos de G3 y G4 se declaran resúmenes; G2 usa un escaneo con OCR; G8 marca puntos `[VERIFICAR]`.
- **Brechas de trazabilidad:** G6 no cita controles en su código; G1 y G4 no tienen pruebas que ejerzan su respaldo normativo; la fórmula de severidad de G8 y los controles A.3.x de G3 no tienen prueba específica.
- **Cobertura de G7:** su catálogo tiene 10 controles; el resto del Anexo A no está representado en la SoA.
