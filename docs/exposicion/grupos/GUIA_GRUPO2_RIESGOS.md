# Guía Grupo 2 — Agente de Evaluación de Riesgos

Tiempo sugerido: **7–8 min**. Es el agente con más piezas; explicar primero qué es original y qué es integración.

## 1–2. Objetivo y responsabilidad
Identificar y evaluar riesgos de privacidad (impacto, tratamiento) con base en ISO/IEC 27701. Alcance académico: "Gestión de Riesgos".

## 3. Arquitectura original (entregada por el grupo)
- Aplicación **ISO Studio 7.2**: frontend React + Vite y servidor Express (puerto 4317) que reenvía el chat al **Chat Trigger de n8n**.
- **4 workflows de n8n:** agente (`AI Agent` con memoria, Qdrant como herramienta y dos subflujos), ingesta RAG, skill de riesgos 27701 y skill de artefactos.
- Qdrant como base vectorial; exportación PDF/DOCX/XLSX, diagramas Mermaid, subida con OCR, búsqueda web opcional (Tavily) y una política de alcance (`scope-policy.json`) que bloquea el agente hasta una revisión humana.

## 4. Skills
No hay `SKILL.md`: el contenido vive en los prompts de los workflows (skill de evaluación de riesgos 27701 y skill de artefactos).

## 5–6. Flujo de ejecución
Pregunta → Express (control de alcance) → Chat Trigger → agente → (a) skill de evaluación para el procedimiento y formato, (b) búsqueda en Qdrant en la norma, (c) skill de artefactos si piden PDF/diagrama → respuesta.

## 7. Integración y demostración
`/agentes/riesgos` envía la consulta por `POST /api/chat` de Express. **Estado honesto:** la plataforma lo muestra `degradado` porque el propio agente sigue bloqueado hasta que alguien confirme `SCOPE_N8N_REVIEWED=true`; no lo activamos nosotros. La demo muestra el motivo real y, una vez que el equipo active el control, la consulta de riesgos (probada con el control abierto de forma temporal).

## 8. Ejemplo
Entrada: "Evalúa los riesgos de privacidad de un sistema de matrícula en línea que almacena DNI y correos de estudiantes." Salida obtenida en la prueba real: evaluación estructurada (contexto, activos, partes interesadas, rol de responsable) apoyada en las cláusulas 6.1.2 y 6.1.3. Pregunta de control: «¿qué exige la norma para la evaluación de riesgos?» → cita la cláusula 6.1.2 (páginas 13–14) recuperada de Qdrant. Una pregunta fuera de tema («receta de pizza») es rechazada por el propio agente (`OUT_OF_SCOPE`).

## 9. Original frente a integrada
La UI React original se conserva en su carpeta. La integrada solo invoca el chat; PDF/DOCX, subidas y diagramas siguen en la original.

## 10. Conexión al gateway LLM — qué es integración y qué es original
El original está atado a **Gemini** (chat y embeddings). La integración genera, **solo al desplegar**, copias de los workflows con nodos compatibles con OpenAI apuntando al gateway (detalle en `docs/integration/MODIFICACIONES_A_AGENTES.md`). Los JSON originales no se tocan. La visión de Gemini queda desactivada porque evitaría el gateway.

## 11. PostgreSQL
No usa Gestitel. Su conocimiento vive en **Qdrant** (colección `iso27701_2025`, vectores de 3072 dimensiones con el modelo de embeddings actual). Cambiar de modelo obliga a re-ingestar.

## 12. Otros agentes
G8 le entregaría causa raíz y lecciones aprendidas; G7 usa niveles de riesgo. Sin conexión automática hoy.

## 13. Problemas y soluciones
- Plantillas reconstruidas, no el export real del grupo: el nodo `If` pedía una versión inexistente, los subflujos no tenían id y el formulario de ingesta no tenía `webhookId` → se corrigió **solo en las copias de despliegue**.
- Express escucha solo en loopback → reenvío TCP en el contenedor.
- La norma con licencia es un escaneo sin texto → OCR (Tesseract, confianza media 93,5 %, texto derivado, fuera del repo); se indexaron 271 vectores. No se contrastaron las cláusulas contra las imágenes.
- Cuota de embeddings del proveedor → lotes y límite por minuto en el gateway.
- Gemini 3 exige la «thought signature» en las llamadas a herramientas y n8n la descarta (HTTP 400 en el segundo turno) → el gateway la conserva y la reinyecta.
- El chat intentaba una búsqueda web automática → el adaptador la desactiva (`webMode: off`).

## Base normativa
- Alcance autorizado en `scope-policy.json`: **solo ISO/IEC 27701:2025**, tema «Gestión de Riesgos» con seis subtemas (GR-01 a GR-06). Apoyo académico: extracto del manual CISA (2024).
- Cláusulas que el agente recupera de la norma indexada: **6.1.2 Privacy risk assessment** (probada: páginas 13–14), 6.1.3 y 8.2.
- La norma completa (72 páginas) es un escaneo; se indexó por OCR (confianza media 93,5 %). Es **texto derivado**: no se contrastaron las cláusulas contra las imágenes.
- *Qué decir:* «el agente solo responde dentro de su alcance normativo; una pregunta fuera de tema, como una receta, se rechaza». *Cuidado:* la política de alcance habla de un extracto de 20 páginas y aquí se indexó el documento completo.

## 14. Guion
"Nuestro agente evalúa riesgos de privacidad apoyándose en la norma. En la plataforma común lo ejecutamos detrás del mismo gateway que los demás. Un detalle que mostramos con transparencia: nuestro diseño exige una revisión humana antes de habilitar el agente, y la plataforma respeta ese bloqueo en lugar de saltárselo."

## 15. Preguntas probables
- *¿Por qué está degradado?* Control de revisión humana propio; la plataforma no lo salta.
- *¿Funciona con Ollama?* Requiere tool-calling y re-ingestar la norma; está por verificar en la otra PC.
- *¿La norma es exacta?* Es texto OCR derivado; no se garantiza exactitud normativa.
- *¿Los workflows son los reales?* Son plantillas reconstruidas; si el comportamiento difiere hay que pedir el export real.

## 16. Conclusiones
Es el agente más complejo de integrar: se automatizó su puesta en marcha y se redirigió al gateway sin editar su fuente, con límites documentados.
