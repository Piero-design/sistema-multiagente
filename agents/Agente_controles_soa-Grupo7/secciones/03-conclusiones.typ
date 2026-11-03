= Conclusiones y Trabajo Futuro

== Conclusiones

A partir del diseño, implementación y validación experimental del *Agente de Controles* para el Sistema de Gestión de Información de Privacidad (PIMS) bajo ISO/IEC 27701:2025, se concluye lo siguiente:

1. *Superación del paradigma de prompts no estructurados:* La transición *"De Prompt a Skill"* resulta imperativa en la ingeniería de software aplicada a la auditoría de sistemas. Al encapsular la lógica en procedimientos formales (`generar-soa` y `verificar-controles`), se transforma una interacción estocástica e informal en un proceso algorítmico, determinista, tipado y 100% reproducible.
2. *Garantía de auditabilidad e inmunidad a alucinaciones:* La adopción de una arquitectura híbrida —que confía las decisiones de aplicabilidad y estado a un motor de reglas determinista y la vinculación contextual a un índice vectorial local (FAISS)— asegura que ningún control sea declarado falsamente como "implementado" sin evidencias probatorias objetivas, satisfaciendo el estándar de las cláusulas 6.1.3 y 9.2 de la norma.
3. *Articulación del ecosistema multi-agente:* El Agente de Controles cumple con éxito su función como elemento de cierre del ciclo del PIMS. Mediante el contrato estándar JSON, recibe los insumos de Inventario, Riesgos y Evidencias, generando de manera unificada la SoA corporativa y la matriz prescriptiva de brechas.
4. *Preservación del principio de supervisión humana y gobernanza:* La inclusión del atributo mandatorio `requiere_revision_humana = true` garantiza el cumplimiento ético y regulatorio del sistema. La IA actúa como un instrumento de diagnóstico y auditoría asistida, reservando la aprobación final de la SoA a la alta dirección y al Oficial de Protección de Datos (DPO).

== Limitaciones

- *Catálogo inicial acotado:* La presente entrega incorpora 10 controles representativos del Anexo A para validar la arquitectura funcional; el estándar completo en un entorno corporativo de producción abarca más de 30 controles y subcontroles.
- *Calibración de umbrales vectoriales:* Los coeficientes de similitud coseno ($0.45$ para políticas y $0.30$ para consultas normativas) requieren ajuste continuo conforme crezca el volumen y variedad de la base documental.

== Hoja de Ruta y Recomendaciones para la Entrega 2

Con miras a la segunda entrega del proyecto integral del curso, se plantean las siguientes líneas de desarrollo:

- *Ampliación Integral del Catálogo Normativo:* Incorporar la totalidad de controles del Anexo A de ISO/IEC 27701:2025, cubriendo la totalidad de directrices para responsables y encargados.
- *Orquestación y Despliegue en Red (Docker):* Desplegar los 8 agentes en contenedores Docker independientes intercomunicados a través de un bus de mensajería (o protocolo MCP), permitiendo la interoperabilidad unificada entre los grupos de trabajo en servidores locales o instancias en la nube.
- *Integración con Datos Sintéticos y Bases de Datos:* Conectar la capa agéntica ("segundo piso") con la base de datos relacional transaccional ("primer piso"), poblando el sistema con datos sintéticos representativos de organizaciones de sectores de alta criticidad (empresas de energía/utilities, universidades y entidades financieras).
- *Capa de Generación Asistida con SLMs Locales:* Integrar un modelo de lenguaje local ligero (e.g. Ollama con modelos cuantizados) exclusivamente para la redacción de informes ejecutivos y explicaciones pedagógicas guiadas por RAG, blindando las reglas de la SoA en código determinista.
