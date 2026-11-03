= Desarrollo Metodológico e Implementación

== De Prompt a Skill: Transformación y Metodología

En las etapas iniciales de la adopción de inteligencia artificial generativa en labores de auditoría de sistemas, las tareas de verificación del cumplimiento suelen abordarse mediante *prompts* empíricos en lenguaje natural enviados directamente a un modelo fundacional de lenguaje (LLM). Si bien este paradigma conversacional ofrece rapidez de exploración, en un contexto formal de auditoría y cumplimiento regulatorio alineado con el estándar internacional ISO/IEC 27701:2025 @iso27701, los prompts libres manifiestan deficiencias estructurales insalvables: ausencia de garantías de reproducibilidad, variabilidad estocástica en la toma de decisiones críticas, vulnerabilidad a la complacencia conversacional (alucinando estados de conformidad inexistentes) e incapacidad de generar trazas documentales que satisfagan los criterios de evidencia suficiente y apropiada exigidos por un marco de aseguramiento.

Frente a estas limitaciones, el presente proyecto transita de una interacción basada en prompts hacia un paradigma de *Skills Especializados* (habilidades algorítmicas desacopladas). Un Skill encapsula una unidad de lógica de negocio determinista, gobernada por contratos de interfaz rigurosos y respaldada por mecanismos de recuperación semántica local que asisten al auditor sin sustituir su juicio profesional:

#table(
  columns: (1.1fr, 2.2fr, 2.2fr),
  align: (center, left, left),
  stroke: 0.5pt + rgb("#b8c2cc"),
  fill: (_, row) => if row == 0 { rgb("#d9e8f5") } else { none },
  [*Dimensión*], [*Enfoque con Prompt Tradicional*], [*Enfoque con Skill Especializado*],
  [Determinismo y Repetibilidad], [Comportamiento estocástico; respuestas divergentes y cambios de juicio ante entradas equivalentes.], [Ejecución algorítmica puramente determinista gobernada por reglas de negocio invariantes y reproducibles.],
  [Estructura y Contratos], [Salidas en texto libre con formatos impredecibles, difíciles de automatizar o integrar en canalizaciones.], [Contratos JSON estrictos con tipado de datos estático, esquemas declarativos y validaciones de frontera.],
  [Rigor Probatorio], [Tendencia a calificar controles como "cumplidos" por cortesía generativa o inferencias infundadas.], [Imposibilidad formal de certificar conformidad sin la existencia de evidencias documentadas contrastables.],
  [Trazabilidad Regulatoria], [Omite el fundamento normativo o asocia justificaciones genéricas desvinculadas de la realidad corporativa.], [Justificación técnica obligatoria asociada a la taxonomía normativa, riesgos reales y políticas indexadas.],
  [Reusabilidad e Integración], [Instrucciones efímeras dependientes de la destreza del usuario; no apto para orquestación multi-agente.], [Servicios modulares invocables vía API REST tanto por auditores humanos como por agentes coordinadores.]
)

=== Transformación del Caso 1: Elaboración de la Declaración de Aplicabilidad (SoA) y Mapeo de Políticas
- *Formulación Inicial mediante Prompt:* _"Tengo estas políticas de privacidad de mi organización y necesito saber qué controles de ISO 27701 aplican, qué directrices internas los respaldan y en qué estado de cumplimiento nos encontramos."_
- *Skill Especializado Resultante (`generar-soa`):* Procedimiento algorítmico formal que valida rigurosamente el rol de privacidad declarado (`responsable`, `encargado` o `ambos`), procesa la matriz de riesgos corporativos provista por el Agente de Riesgos, determina de manera estricta el estado de implementación evaluando evidencias fehacientes, contrasta las medidas y directivas internas mediante búsqueda semántica vectorial en FAISS @johnson2019billion sobre el repositorio corporativo de políticas, y estructura la SoA en una matriz de datos tipada. Dicha matriz incluye la detección explícita de brechas de cumplimiento, el agente específico responsable de su tratamiento y el indicador perentorio de supervisión humana (`requiere_revision_humana = true`), asegurando que ninguna declaración entre en vigor sin revisión del auditor líder.

=== Transformación del Caso 2: Auditoría y Verificación de un Control Específico
- *Formulación Inicial mediante Prompt:* _"Revisa si el control de Evaluación de Impacto en la Privacidad (DPIA) está efectivamente implementado considerando los documentos que te adjunto y dime qué observaciones tienes."_
- *Skill Especializado Resultante (`verificar-controles`):* Procedimiento de inspección puntual que verifica la vigencia y correspondencia del control en el catálogo normativo oficial, audita la calidad y suficiencia de las evidencias aportadas para computar de forma exacta la brecha existente, y emite recomendaciones prescriptivas dirigidas inequívocamente al rol o agente temático responsable de subsanar los hallazgos.

== Especificación Formal de los Skills

La especificación de los Skills adopta el estándar de definición de capacidades agénticas mediante descriptores `SKILL.md` alojados en el directorio `skills/`. Para garantizar la integridad metodológica de la auditoría, la arquitectura distingue con nitidez dos capas conceptuales:

1. *Requisitos del Estándar Internacional ISO/IEC 27701:2025:* La norma internacional, en su cláusula 5 (en consonancia directa con el requisito 6.1.3 de ISO/IEC 27001:2022 @iso27001), impone la elaboración de una Declaración de Aplicabilidad (SoA). Este documento mandatorio debe inventariar todos los controles necesarios, motivar técnicamente la inclusión o exclusión de cada salvaguarda —estableciendo una separación nítida entre los deberes de un *responsable del tratamiento* (PII controller) y un *encargado del tratamiento* (PII processor)— y reflejar con transparencia su estado de implementación.
2. *Reglas de Negocio del Agente (Diseño de Ingeniería):* Corresponden a los axiomas algorítmicos implementados para guiar el comportamiento del prototipo:
  - *Mapeo taxonómico:* Asignación automática de aplicabilidad según la estructura por dominios del Anexo A de la norma (`A.1` para responsables, `A.2` para encargados, `A.3` transversal a ambos perfiles).
  - *Determinismo en la evaluación de evidencias:* Criterio booleano estricto que prohíbe inferencias generativas al calificar el estado de un control.
  - *Canalización inter-agente:* Vinculación de cada brecha detectada con el agente temático del ecosistema PIMS con atribución funcional para mitigarla.
  - *Garantía de supervisión humana:* Inclusión sistemática e inmutable de la bandera de aprobación manual, preservando el principio ético y regulatorio de intervención humana (*human-in-the-loop*).

=== Ficha Técnica del Skill `generar-soa`
- *Nombre Canónico:* `generar-soa`
- *Propósito Operativo:* Construir de forma estructurada la Declaración de Aplicabilidad (SoA) integral conforme a los principios de la norma ISO/IEC 27701:2025 sobre el catálogo normativo representativo configurado.
- *Condición de Disparo:* Peticiones de elaboración inicial, actualización periódica o auditoría global de la SoA organizacional.
- *Parámetros de Entrada (Contrato de Interfaz):*
  - `perfil`: Objeto con las propiedades `organizacion` (cadena descriptiva) y `rol` (valor enumerado estricto: `"responsable"`, `"encargado"` o `"ambos"`).
  - `riesgos`: Matriz de objetos `{ id: string, descripcion: string, controles: string[] }`, suministrada de forma interoperable por el Agente de Riesgos.
  - `evidencias`: Matriz de objetos `{ control: string, descripcion: string, estado: "implementado" | "parcial" }`, aportada por el auditor o extraída de repositorios documentales.
  - `base_politicas`: Repositorio corporativo de políticas y directivas internas indexado en `knowledge/politicas/`.
- *Algoritmo de Ejecución:*
  1. *Validación y control de frontera:* Verificar la presencia obligatoria del parámetro `perfil.rol`. Si no se especifica o difiere del dominio permitido, abortar inmediatamente retornando estado `"rechazada"`.
  2. *Ingesta de catálogo:* Cargar en memoria el catálogo normativo representativo (`catalogo_controles.json`).
  3. *Evaluación de aplicabilidad (regla de asignación por rol):*
    - *Controles del Anexo A.1:* Aplican si el rol es `"responsable"` o `"ambos"`. Si el perfil auditado es `"encargado"`, se excluyen registrando la justificación formal: _"Excluido: la organización no actúa como responsable (controles A.1)"_.
    - *Controles del Anexo A.2:* Aplican si el rol es `"encargado"` o `"ambos"`. Si el perfil es `"responsable"`, se excluyen registrando: _"Excluido: la organización no actúa como encargada (controles A.2)"_.
    - *Controles del Anexo A.3:* Aplican universalmente con independencia del rol, al regular aspectos compartidos de gobernanza de la seguridad, gestión de incidentes y concienciación del personal.
  4. *Trazabilidad con el análisis de riesgos:* Formular la justificación técnica inicial y contrastar con la lista de riesgos del Agente de Riesgos; si uno o varios riesgos vinculan el ID del control, se concatena explícitamente la referencia al identificador (p. ej., _"Vinculado a los riesgos: R1, R3"_).
  5. *Evaluación determinista del estado de implementación:*
    - Si el control fue catalogado como no aplicable: Se asigna directamente el estado `"no aplica"`, prescindiendo de análisis probatorio.
    - Si el control resulta aplicable: Se aíslan las evidencias cuyo campo `control` coincida con el ID evaluado. Si existe al menos una evidencia calificada con `"implementado"`, se dictamina `"implementado"`. En caso contrario, si existe al menos una calificada como `"parcial"`, se asigna `"parcial"`. Si no constan evidencias asociadas para dicho control, se concluye de forma categórica `"no implementado"`.
  6. *Recuperación contextual de políticas corporativas:* Ejecutar una búsqueda de máxima similitud en el espacio vectorial de FAISS @johnson2019billion sobre el repositorio de políticas corporativas indexado con embeddings locales servidos mediante Ollama. Si el puntaje de similitud coseno supera el umbral configurado ($>= 0.35$), se indexa el metadato del documento corporativo correspondiente.
  7. *Detección de brechas y canalización:* Identificar la totalidad de controles aplicables cuyo estado final sea `"no implementado"` o `"parcial"`, incorporándolos a la lista de brechas y designando el agente del PIMS responsable de implementar o recopilar la salvaguarda.
  8. *Agregación y aseguramiento:* Calcular los totales consolidados (evaluados, aplicables, implementados, parciales, brechas) y adjuntar la bandera mandatoria `requiere_revision_humana = true`.
- *Restricciones y Salvaguardas:* Prohibición absoluta de certificar controles como implementados sobre la base de inferencias no probadas; exigencia ineludible de justificación técnica para cualquier exclusión; y emisión de la SoA como propuesta técnica sujeta a homologación humana.

=== Ficha Técnica del Skill `verificar-controles`
- *Nombre Canónico:* `verificar-controles`
- *Propósito Operativo:* Realizar la auditoría de conformidad de un control normativo puntual y derivar acciones correctivas ante discrepancias.
- *Parámetros de Entrada:* Identificador normativo `control` (p. ej., `"A.1.2.6"`), `perfil`, catálogo de `riesgos` y lote de `evidencias`.
- *Resultado Producido:* Fila de control tipada con diagnóstico determinista, detalle de evidencias vinculadas, política corporativa asociada y prescripción correctiva personalizada dirigida al agente del PIMS competente.

== Definición y Modelado del Asistente

El Asistente de Controles se modela bajo un principio de especialización técnica delimitada dentro del ecosistema PIMS:

- *Identidad Sistémica:* _"Soy el Agente de Controles del sistema de gestión de privacidad (PIMS) basado en ISO/IEC 27701:2025. Mi función es determinar qué controles del Anexo A aplican a la organización, generar la Declaración de Aplicabilidad (SoA) y verificar el estado de implementación de cada control."_
- *Directrices Operativas de Auditoría:* Priorizar la ejecución de los Skills estructurados frente a respuestas conversacionales abiertas; no inferir ni asumir la existencia de políticas o evidencias documentales no suministradas formalmente; declinar solicitudes con parámetros incompletos solicitando la aclaración de las partes interesadas; y asegurar total neutralidad técnica, repetibilidad y auditabilidad en cada dictamen.
- *Catálogo Reducido de Demostración:* Para validar experimentalmente el funcionamiento del prototipo y facilitar la integración con los restantes componentes del curso, se configuró un catálogo representativo compuesto por 10 controles seleccionados de los dominios A.1, A.2 y A.3 de ISO/IEC 27701:2025 (incluyendo controles sobre propósitos legítimos, registros de actividades, DPIA, relación con encargados, derechos de los titulares, gestión de brechas de privacidad y capacitación). Se enfatiza que este conjunto constituye una muestra representativa de prueba para verificar la interoperabilidad multi-agente, y no abarca el universo exhaustivo de la norma completa.
- *Base de Conocimiento Local y Fuentes Documentales:*
  - `knowledge/catalogo_controles.json`: Estructura JSON tipada que formaliza el catálogo representativo con metadatos de ámbito, nombre y agente responsable.
  - `knowledge/normativa/resumen_27701.md`: Síntesis local de referencia y consulta conceptual estructurada sobre las cláusulas y directrices de ISO/IEC 27701:2025. Se utiliza exclusivamente para la recuperación semántica en lenguaje natural ante preguntas conceptuales de los usuarios (no constituye una fuente normativa oficial de certificación ni sustituye el texto formal emitido por ISO).
  - `knowledge/politicas/politica_privacidad_ejemplo.md`: Corpus corporativo de políticas internas de privacidad y directrices de seguridad, fragmentado y vectorizado para la contrastación de evidencias frente a las declaraciones organizacionales.

== Arquitectura del Sistema, Papel del Agente de Riesgos y Contratos de Integración

La solución se concibe como una arquitectura orientada a servicios desacoplados bajo protocolos ligeros de mensajería JSON, diseñada para ejecutarse como microservicio autónomo o como nodo colaborador dentro de un bus de integración inter-agentes.

#align(center)[
  #image("../imagenes/Arquitectura.png", width: 95%)
]
#align(center)[_Figura 1: Arquitectura de Componentes del Ecosistema PIMS y el Agente de Controles._]

=== El Papel del Agente de Riesgos en la Arquitectura Multi-Agente
En el ecosistema integral del PIMS compuesto por 8 agentes especializados (Controles, Riesgos, Inventario, Terceros, Derechos, Incidentes, Formación y Gobernanza), el *Agente de Riesgos* desempeña un rol de proveedor crítico de contexto para la labor del Agente de Controles:
1. *Fundamento para la Selección de Salvaguardas:* La cláusula 5 de ISO/IEC 27701:2025 y el marco general de ISO/IEC 27001:2022 estipulan que la inclusión de controles en la Declaración de Aplicabilidad debe derivarse de un proceso documentado de apreciación y tratamiento de riesgos de privacidad (PII risks). El Agente de Riesgos analiza los flujos de datos personales, detecta amenazas, estima impactos y produce la matriz de riesgos formalizada (identificadores `R1`, `R2`, etc.) indicando los controles requeridos para mitigar cada escenario.
2. *Trazabilidad Bidireccional en la SoA:* El Agente de Controles procesa dicho lote a través de la interfaz de entrada y lo asocia algorítmicamente en la columna de justificación técnica de la SoA, demostrando la causalidad entre riesgo mitigado y control implantado. Complementariamente, cuando el Agente de Controles identifica que un control preventivo crucial se encuentra en estado de brecha —como el control `A.1.2.6` relativo a la Evaluación de Impacto en la Privacidad (DPIA)—, la recomendación prescriptiva se canaliza directamente hacia el Agente de Riesgos, señalándolo como el actor responsable de conducir dicha evaluación técnica.

=== Contrato Estándar de Comunicación Inter-Agentes
Para asegurar la interoperabilidad entre los diferentes módulos y agentes del sistema, se definió un esquema de comunicación uniforme bajo formato JSON:

```json
{
  "agente": "controles",
  "operacion": "generar_soa | verificar_control | consultar",
  "estado": "ok | rechazada | sin_respuesta",
  "respuesta": "Resumen ejecutivo en lenguaje natural",
  "datos": {
    "soa": [ /* Matriz de controles evaluados */ ],
    "brechas": [ /* Controles aplicables no implementados con responsable */ ],
    "resumen": { /* Métricas agregadas */ }
  },
  "fuentes": ["catalogo_controles.json", "politica_privacidad_ejemplo.md"],
  "confianza": 1.0,
  "requiere_revision_humana": true
}
```

*Funcionamiento y Fundamentación del Campo `confianza`:*
- *En operaciones deterministas (`generar_soa` y `verificar_control`):* El campo reporta un valor de calibración nominal de `1.0`. Este valor refleja formalmente que el resultado fue derivado mediante métodos lógicos puros sobre reglas taxonómicas y correspondencias exactas sobre el catálogo local, sin introducir variabilidad estocástica ni inferencias generativas aproximadas.
- *En la operación de consulta conceptual (`consultar`):* El campo refleja un cálculo matemático dinámico. Corresponde al puntaje de similitud coseno vectorial (normalizado en el rango $[0.0, 1.0]$) devuelto por el motor FAISS @johnson2019billion para el fragmento textual de mayor proximidad respecto a la consulta del usuario. Cuando dicho coeficiente no alcanza el umbral de corte de relevancia ($0.30$), el sistema omite emitir conjeturas infundadas, retorna estado `"sin_respuesta"` y transparenta el valor numérico obtenido, posibilitando que el orquestador decida si reformular la consulta o canalizarla a un auditor humano.

=== Flujo de Ejecución e Interacción Temporal
La interacción temporal entre el usuario, las interfaces de servicio y la base de conocimiento se ilustra a continuación:

#align(center)[
  #image("../imagenes/Flujo.png", width: 95%)
]
#align(center)[_Figura 2: Diagrama de Secuencia del flujo de generación y verificación de la SoA._]

== Tecnologías, Motor Determinista e Infraestructura

La implementación técnica adopta una arquitectura de software híbrida diseñada específicamente para conciliar determinismo algorítmico, preservación estricta de la privacidad de los datos organizacionales y alta eficiencia computacional:

1. *Lenguaje Backend y Capa de Servicios Web:* El núcleo lógico y los adaptadores de servicio fueron codificados en *Python 3.10+*, haciendo uso del microframework *Flask* para exponer interfaces de programación REST livianas y desacopladas (`/api/controles/ejecutar` y `/api/controles/catalogo`). La elección de Flask obedece a su mínimo consumo de recursos en entornos restringidos, facilitando la rápida serialización y deserialización de estructuras JSON y permitiendo tanto su invocación interactiva desde interfaces web como su orquestación desatendida mediante llamadas inter-agente.

2. *Motor de Reglas Determinista y Repetibilidad:* Implementado mediante métodos puros (`_aplica()` y `_estado()`) dentro de la clase principal `AgenteControles`. A diferencia de los modelos generativos estocásticos tradicionales —cuyas inferencias probabilísticas pueden oscilar ante leves variaciones léxicas en la formulación de consultas—, la adopción de axiomas booleanos y árboles de decisión explícitos reduce significativamente la dependencia de respuestas generativas no deterministas en decisiones regulatorias críticas. Este enfoque garantiza que, ante un conjunto idéntico de parámetros de perfil, catálogo de riesgos y evidencias aportadas, el dictamen emitido sobre el Anexo A de ISO/IEC 27701:2025 sea un procedimiento 100% determinista, auditable, libre de sesgos de indulgencia y verificable matemáticamente por cualquier revisor externo.

3. *Motor de Embeddings Local y Privacidad de Datos:* Para la vectorización semántica de las políticas y normativas internas, se integró el servidor local de Ollama utilizando el modelo de embeddings `all-minilm`. Este modelo proyecta fragmentos textuales en un espacio denso de 384 dimensiones optimizado para el procesamiento semántico en idioma español. Crucialmente, la inferencia se ejecuta de forma 100% offline sobre la infraestructura local de Ollama, eliminando cualquier transmisión de información corporativa o de datos personales hacia proveedores de nube externos, salvaguardando el secreto profesional y mitigando riesgos de fuga de información conforme al artículo 28 del RGPD @gdpr2016.

4. *Indexación Vectorial y Búsqueda Semántica con FAISS:* La indexación y consulta ultrarrápida de fragmentos normativos y políticas corporativas se sustenta en la biblioteca `faiss-cpu` (Facebook AI Similarity Search) @johnson2019billion. Se implementó una estructura de índice plano de producto interno (`IndexFlatIP`) operando sobre vectores previamente normalizados en norma $L_2$, lo que equivale al cómputo exacto de la similitud coseno. Esto permite efectuar comparaciones semánticas exhaustivas en el corpus documental con latencias inferiores a un milisegundo, permitiendo asociar de manera automatizada directrices internas a cada control evaluado sin penalizar el rendimiento global del sistema.

5. *Integración Opcional de Modelos de Lenguaje (SLMs/LLMs) bajo Paradigma RAG:* En el módulo específico de asistencia conceptual y resolución de dudas normativas (`_consultar`), la arquitectura contempla la integración opcional de modelos locales compactos (Small Language Models ejecutados mediante entornos locales como Ollama, e.g., Llama 3 o Mistral). Siguiendo las directrices de la Generación Aumentada por Recuperación (RAG) @lewis2020rag, el contexto inyectado al modelo queda rígidamente condicionado a los fragmentos textuales previamente recuperados y validados por el índice FAISS. De esta manera, el modelo generativo se limita exclusivamente a tareas de síntesis expositiva y redacción en lenguaje natural, prohibiéndose su intervención en la lógica de evaluación de aplicabilidad y estado de los controles, la cual permanece bajo custodia exclusiva del código determinista.

6. *Estrategia de Despliegue, Contenedorización e Infraestructura:* El agente fue diseñado bajo principios de portabilidad y bajo acoplamiento ambiental, permitiendo su ejecución sin fricciones tanto en estaciones locales de trabajo para entornos académicos de laboratorio como en infraestructuras productivas virtualizadas. La solución cuenta con manifiestos de despliegue mediante contenedores *Docker*, lo que estandariza las dependencias de sistema y bibliotecas numéricas, aislando el entorno de ejecución y facilitando la interoperabilidad en redes privadas locales (LAN) o en servidores privados virtuales (VPS), asegurando tanto la reproducibilidad técnica como la soberanía integral de los datos auditados.

== Demostración y Plan de Pruebas

Para validar rigurosamente la estabilidad de la arquitectura, la exactitud de los algoritmos y la coherencia del motor determinista frente a variaciones en los datos de entrada, se diseñó e implementó una batería de 6 casos de prueba estructurados. Las pruebas fueron ejecutadas sobre el catálogo reducido de 10 controles demostrativos que conforman el entorno experimental del prototipo:

#table(
  columns: (0.4fr, 1.2fr, 1.8fr, 2.6fr),
  align: (center, center, left, left),
  stroke: 0.5pt + rgb("#b8c2cc"),
  fill: (_, row) => if row == 0 { rgb("#d9e8f5") } else { none },
  [*N°*], [*Caso de Prueba*], [*Datos de Entrada*], [*Resultado Esperado y Verificado en la Auditoría*],
  [1], [Generación SoA (Responsable)], [Rol: `responsable`, Riesgo: `R1`, Evidencias: `A.1.2.2` (imp.), `A.3.12` (parcial)], [10 controles evaluados (muestra representativa): 9 declarados aplicables, 1 formalmente excluido (`A.2.5.7`). Diagnóstico: 1 implementado, 1 parcial, 7 no implementados. 8 brechas detectadas con indicación precisa del agente responsable de mitigación. Trazabilidad con riesgo `R1` verificada. Flag `requiere_revision_humana: true`. Confianza nominal: 1.0.],
  [2], [Cambio de Rol a Encargado], [Rol: `encargado`, mismas evidencias de prueba], [Inversión automática de aplicabilidad: controles `A.1` quedan formalmente excluidos con justificación explícita de no actuar como responsable; pasan a aplicar el control `A.2.5.7` y los controles comunes `A.3`. Se garantiza que no se arrastren clasificaciones erróneas.],
  [3], [Cambio de Rol a Ambos Perfiles], [Rol: `ambos`], [Los 10 controles del catálogo piloto resultan 100% aplicables al ostentar la entidad ambas figuras normativas. Generación automática de justificaciones técnicas individualizadas por dominio taxonómico.],
  [4], [Verificación Puntual de Brecha (A.1.2.6)], [Control: `A.1.2.6`, Rol: `responsable`, ausencia total de evidencias], [Diagnóstico determinista categórico: `no implementado` (no se infiere cumplimiento por omisión). Emisión de recomendación prescriptiva dirigida: "Solicitar evidencia o implementación al Agente de Riesgos" para la realización de la DPIA.],
  [5], [Consulta Normativa RAG Local], [Pregunta: "¿Qué debe incluir la Declaración de Aplicabilidad?"], [Recuperación semántica de fragmentos relevantes sobre `resumen_27701.md`. Transparencia en fuentes documentales y reporte del campo `confianza` mediante el score real continuo de similitud coseno vectorial obtenido por FAISS.],
  [6], [Validación de Entrada Malformada], [Entrada con parámetro `perfil.rol` ausente, nulo o léxicamente inválido], [Rechazo preventivo con estado `"rechazada"` y mensaje descriptivo de validación de esquema JSON, garantizando tolerancia a fallos sin generar excepciones ni bloqueos de ejecución.]
)

=== Análisis y Verificación de los Resultados del Plan de Pruebas
Los resultados obtenidos a través de la ejecución de esta matriz de pruebas permiten constatar tres atributos esenciales de la solución implementada:
1. *Consistencia y determinismo absoluto en el control de acceso a roles:* Los casos 1, 2 y 3 validan que el sistema responde de forma instantánea y matemáticamente reproducible ante cambios organizacionales, impidiendo que una entidad asuma responsabilidades que no le corresponden según la taxonomía de la norma ISO/IEC 27701:2025.
2. *Rigor probatorio y prescriptividad orientada a la acción:* El caso 4 demuestra el blindaje contra la indulgencia conversacional, obligando al auditor a ingresar evidencias explícitas para certificar el estado y vinculando de manera automática al Agente de Riesgos para resolver el hallazgo.
3. *Resiliencia ante entradas no confiables y transparencia heurística:* Los casos 5 y 6 prueban que el sistema rechaza anomalías de esquema sin corromper el estado y transparenta numéricamente la certeza semántica en consultas de texto libre, satisfaciendo plenamente los requerimientos de gobernanza y aseguramiento técnico en auditoría.



