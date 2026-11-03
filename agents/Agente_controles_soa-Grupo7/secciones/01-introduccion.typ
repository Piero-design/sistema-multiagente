= Introducción y Marco General

== Introducción

El aseguramiento de la privacidad y la protección de los Datos de Identificación Personal (PII, _Personally Identifiable Information_) se han consolidado como pilares regulatorios, operacionales y éticos en la era digital. En este contexto, la norma internacional *ISO/IEC 27701:2025* @iso27701 establece los requisitos y directrices para implementar, mantener y auditar un Sistema de Gestión de Información de Privacidad (PIMS, _Privacy Information Management System_). Concebida en su edición 2025 como una norma de gestión independiente y autónoma pero armonizada con las normas ISO/IEC 27001:2022 @iso27001 e ISO/IEC 27002, se alinea además con marcos regulatorios globales como el Reglamento General de Protección de Datos (GDPR) @gdpr2016 y los estándares de gobernanza de inteligencia artificial como ISO/IEC 42001:2023 @iso42001.

Dentro del ciclo de vida de un PIMS, la *Declaración de Aplicabilidad (SoA, _Statement of Applicability_)* representa el instrumento técnico y legal más crítico. En ella se documenta formalmente qué controles normativos aplican a la organización, cuáles se excluyen, la justificación preceptiva de cada decisión y el estado real y verificable de su implementación. No obstante, la gestión tradicional de la SoA suele sufrir de dispersión probatoria, inconsistencias humanas y una alta carga burocrática.

Para superar estas limitaciones, este proyecto aborda la transición paradigmática *De Prompt a Skill* en el marco de una arquitectura de *Sistemas Multi-Agente (MAS, _Multi-Agent Systems_)*. Mientras que un prompt convencional es una instrucción no estructurada, reactiva y propensa a alucinaciones, un *Skill* es una unidad de procedimiento determinista, modular, reusable y gobernada por contratos de datos tipados. En este informe se detalla el diseño y construcción del *Agente de Controles*, el componente articulador que sintetiza la información de todo el sistema para emitir la SoA y auditar el cumplimiento normativo.

== Objetivos del Proyecto

=== Objetivo General
Diseñar, implementar y validar experimentalmente el *Agente de Controles* para un PIMS bajo la norma ISO/IEC 27701:2025, transformando tareas de auditoría en *Skills especializados deterministas* e interoperables mediante contratos JSON estándar en una arquitectura multi-agente.

=== Objetivos Específicos
- *Formalizar la metodología "De Prompt a Skill":* Transformar consultas abiertas y ad-hoc en procedimientos reproducibles y tipados (`generar-soa` y `verificar-controles`).
- *Garantizar la auditabilidad y mitigación de alucinaciones:* Implementar un motor de reglas determinista que impida declarar controles implementados sin evidencias objetivas y verificables.
- *Integrar conocimiento semántico local (RAG):* Implementar un índice vectorial con embeddings multilingües y FAISS para vincular políticas internas y cláusulas de la norma sin dependencia de servicios externos.
- *Establecer el protocolo de interoperabilidad inter-agentes:* Diseñar el contrato estándar JSON para la comunicación horizontal con los otros 7 agentes del PIMS y la integración vertical con el orquestador.
- *Establecer las bases para la Entrega 2:* Diseñar una arquitectura modular capaz de evolucionar hacia la orquestación distribuida, contenedores Docker y validación con datos sintéticos y entornos reales.

== Contexto Normativo: Estructura Armonizada e ISO/IEC 27701:2025

=== Estructura de Alto Nivel (Cláusulas 1 a 10)
Al igual que los estándares modernos de gestión (como ISO/IEC 27001 e ISO/IEC 42001), la norma ISO/IEC 27701:2025 adopta la Estructura Armonizada (_Harmonized Structure_ / HLS), compuesta por 10 cláusulas fundamentales:

#table(
  columns: (1.2fr, 2.8fr, 2fr),
  align: (center, left, left),
  stroke: 0.5pt + rgb("#b8c2cc"),
  fill: (_, row) => if row == 0 { rgb("#d9e8f5") } else { none },
  [*Cláusula*], [*Denominación y Alcance*], [*Relevancia en el PIMS / Agente*],
  [1. Alcance], [Delimitación del PIMS y tipos de organizaciones cubiertas], [Define si la entidad es responsable o encargada],
  [2. Normas de referencia], [Vínculo mandatorio con ISO/IEC 27001 e ISO/IEC 27002], [Marco de seguridad base],
  [3. Términos y definiciones], [Conceptos clave: PII, titular de datos, DPO, brecha], [Vocabulario formal del sistema],
  [4. Contexto], [Comprensión de la organización, partes interesadas y PII], [Entrada del Agente de Inventario],
  [5. Liderazgo], [Compromiso de la alta dirección y política de privacidad], [Marco de gobernanza institucional],
  [6. Planificación], [6.1.2 Evaluación de riesgos; 6.1.3 Tratamiento de riesgos / SoA], [*Núcleo del Agente de Controles y Riesgos*],
  [7. Soporte], [Recursos, competencia (7.2), concienciación (7.3) e info. doc. (7.5)], [Agente de Formación y Repositorio],
  [8. Operación], [Planificación y control operacional; evaluaciones DPIA], [Agente de Riesgos y Terceros],
  [9. Evaluación de desempeño], [9.1 Seguimiento y medición; 9.2 Auditoría interna; 9.3 Revisión], [*Base probatoria del Agente de Evidencia*],
  [10. Mejora], [No conformidades, acciones correctivas y mejora continua], [Agente de Incidentes y Planes de acción]
)

=== Roles Organizacionales y Estructura del Anexo A
La norma ISO/IEC 27701:2025 exige diferenciar explícitamente el rol que asume la organización:
1. *Responsable del Tratamiento (_PII Controller_):* Determina las finalidades y medios del tratamiento de datos personales. Está sujeto a los *Controles A.1* (gobierno, finalidades, derechos de titulares y DPIA).
2. *Encargado del Tratamiento (_PII Processor_):* Trata datos exclusivamente bajo instrucciones del responsable. Está sujeto a los *Controles A.2* (gestión de subencargados, asistencia técnica y transferencias).
3. *Controles Comunes (A.3):* Controles transversales de seguridad operacional, respuesta a incidentes y concienciación, obligatorios para *ambos roles*.

=== El Rol del DPO y la Gobernanza
El estándar contempla la figura del *Oficial de Protección de Datos (DPO, _Data Protection Officer_)* como garante del cumplimiento normativo. En nuestra arquitectura, el sistema automatizado actúa como un asistente analítico avanzado; por tanto, la SoA emitida ostenta carácter de *propuesta técnica auditada*, requiriendo preceptivamente la bandera de supervisión y aprobación humana (`requiere_revision_humana = true`).

== El Ecosistema Multi-Agente: Arquitectura en Dos Pisos

Para abordar la complejidad de un PIMS corporativo, la solución se concibe en dos niveles arquitectónicos:
- *Primer Piso (Capa Tradicional / Transaccional):* Modelado de datos, tablas maestras de sistemas, repositorios de políticas, registros de actividades de tratamiento (RAT) y almacenamiento de evidencias (similar a las plataformas tradicionales de cumplimiento y GDPR).
- *Segundo Piso (Capa Agéntica Multi-Agente):* Capa de razonamiento compuesta por 8 agentes especializados que se comunican mediante protocolos estándar (JSON / MCP - _Model Context Protocol_), automatizando el cruce de requisitos, riesgos y evidencias.

#table(
  columns: (1.1fr, 1.8fr, 1.3fr, 1.8fr),
  align: (center, left, center, left),
  stroke: 0.5pt + rgb("#b8c2cc"),
  fill: (_, row) => if row == 0 { rgb("#d9e8f5") } else { none },
  [*Agente*], [*Rol y Responsabilidad*], [*Cláusula ISO*], [*Aporte e Interacción*],
  [Inventario], [Descubre sistemas, cataloga PII y propósitos], [4.1, 4.2, A.1.2.2], [Provee el objeto `perfil` y contexto],
  [Riesgos], [Ejecuta DPIAs y análisis de riesgos], [6.1.2, 8.2, A.1.2.6], [Provee el arreglo `riesgos`],
  [*Controles (Nuestro)*], [*Evalúa aplicabilidad, cruza evidencias y genera SoA*], [*6.1.3, Anexo A*], [*Síntesis, SoA y Matriz de Brechas*],
  [Evidencia], [Recopila artefactos probatorios y logs], [9.1, 9.2, 7.5], [Provee el arreglo `evidencias`],
  [Derechos (DSAR)], [Gestiona solicitudes de acceso y rectificación], [A.1.3.7, A.1.3.9], [Evidencias de ejercicio de derechos],
  [Incidentes], [Clasifica, notifica y gestiona brechas (Ishikawa)], [A.3.11, A.3.12, 10.1], [Evidencias de gestión de incidentes],
  [Terceros], [Audita contratos DPA y subencargados], [A.1.2.7, A.2.5.7], [Evidencias de proveedores y DPAs],
  [Formación], [Monitorea la capacitación y cultura de privacidad], [7.2, 7.3, A.3.17], [Evidencias de sensibilización anual]
)

El *Agente de Controles "cierra el círculo del PIMS":* toma los riesgos identificados, las actividades inventariadas y las pruebas recopiladas por los demás agentes para emitir la SoA definitiva y señalar las brechas de cumplimiento con sus respectivos responsables.
