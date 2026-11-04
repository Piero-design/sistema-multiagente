# Guía Grupo 1 — Agente de Formación y Concientización

Tiempo sugerido: **6–8 min** (1 intro, 2 arquitectura, 3 demo, 1 cierre).

## 1–2. Objetivo y responsabilidad
Apoyar la formación y concientización en privacidad (ISO/IEC 27701): consultar capacitaciones, evaluar y medir la concientización del personal. En la plataforma es el agente de las **personas**.

## 3. Arquitectura y tecnologías originales
Backend FastAPI (`backend/main.py`) con autenticación JWT, orquestación con LangGraph, RAG sobre ChromaDB, almacén propio SQLite (usuarios, conversaciones, formaciones, evaluaciones) y servidor MCP propio. Frontend propio en `frontend/`. Base de conocimiento en `knowledge_base/`.

## 4. Skills y funcionalidad
Skill `formacion-conciencia-iso27701` (en `.agents/skills/`). Endpoints nativos: `/chat` (SSE con eventos `token`, `approval_required`, `done`), `/chat/approve`, `/dashboard/estado`, `/dashboard/brechas`, `/dashboard/heatmap`, `/dashboard/radar` y calendario de eventos.

## 5–6. Conocimiento y ejecución paso a paso
1. El usuario inicia sesión (JWT) y crea una conversación. 2. Envía un mensaje a `/chat`. 3. LangGraph clasifica la intención, valida la entrada y consulta el RAG. 4. Si la acción requiere confirmación, emite `approval_required` y espera la decisión humana. 5. Responde por flujo SSE.

## 7. Demostración en la interfaz unificada
`/agentes/formacion` → "Consultar al asistente" con la pregunta precargada (datos de demostración). El adaptador inicia sesión con la cuenta de demostración del propio agente, crea la conversación y entrega el texto. Si el agente pide aprobación, la plataforma **no la aprueba**: la muestra como pendiente.

## 8. Entradas y salidas de ejemplo
Entrada: "¿Qué capacitaciones de protección de datos debería completar el personal administrativo?" Salida: texto basado en su base de conocimiento y en las formaciones de su base; eventos `token` y `done`.

## 9. Interfaz original frente a la integrada
La original (login, chat, dashboards de brechas, mapa de calor y radar) sigue en `frontend/`. La integrada solo expone el chat; los tableros siguen en la original.

## 10. Conexión al gateway LLM
Por su propia rama `ollama` (`LLM_PROVIDER=ollama`, `OLLAMA_HOST` = gateway). Embeddings con `OLLAMA_EMBED_MODEL`. Sin tocar su código.

## 11. PostgreSQL
Mantiene su SQLite privada (en un volumen). No usa Gestitel todavía; las tablas `core_training*` de Gestitel serían el destino de una integración futura mediante un adaptador de repositorio.

## 12. Integración con otros agentes
Recibiría lecciones aprendidas de G8 (por ejemplo phishing). **Hoy no hay conexión automática.**

## 13. Problemas técnicos y soluciones
- `pywin32` (solo Windows) rompía la instalación → se filtra al construir la imagen.
- La base queda vacía al arrancar → se ejecuta su `init_db.py` una vez si no hay usuarios.
- Dependencias pesadas (ChromaDB, fastmcp): la imagen tarda en construirse.

## Base normativa (según el conocimiento del agente)
- **ISO/IEC 27701:2025** y su skill `formacion-conciencia-iso27701`, que se apoya en el control **A.3.17 (Concienciación y formación)** y menciona A.3.11. Su `knowledge_base/normativas/iso/` incluye transcripciones de ISO/IEC 27001, 27002, 27701 y 29100.
- **Ley N.° 29733** y **D.S. 016-2024-JUS** (Reglamento), más material «GDPR-ready», en `normativas/peru/`.
- Reglamentos de la UNSA (ROF, MOF, directiva 001-2025, reglamento de protección de datos de estudiantes, CSIRT) en `normativas/reglamentos_unsa/`.
- *Qué decir:* «las capacitaciones que propone salen de esos documentos». *Cuidado:* son las fuentes que cargó el grupo; no se validó que las transcripciones coincidan con las ediciones oficiales.

## 14. Guion natural
"Nuestro agente acompaña a las personas: responde dudas de formación con base en la norma y en las capacitaciones de la organización. Aquí lo vemos desde la plataforma común: preguntamos qué debe estudiar el personal administrativo y el agente contesta con su propio conocimiento. Cuando una acción necesita confirmación, el agente la pide y no se ejecuta sola."

## 15. Preguntas probables
- *¿Por qué el login con una cuenta fija?* Son cuentas de demostración del propio agente; en producción se gestionarían con la autenticación de la plataforma.
- *¿Dónde se guardan las conversaciones?* En su SQLite privada.
- *¿Qué modelo usa?* El del gateway; el agente no lo elige.

## 16. Conclusiones
El agente se integró sin cambiar su código ni su base de conocimiento; sus tableros y la aprobación de acciones siguen en su interfaz original.
