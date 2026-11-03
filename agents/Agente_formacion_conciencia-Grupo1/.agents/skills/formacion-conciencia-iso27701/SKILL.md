---
name: formacion-conciencia-iso27701
description: Especificación técnica y catálogo de Herramientas MCP (Model Context Protocol) del Agente #8 PIMS UNSA (Formación, Concienciación y Cultura de Privacidad ISO/IEC 27701:2025 Control A.3.17, Ley 29733 Art. 38). Diseñado para integración con el Orquestador Global Multiagente.
---

# Skill: Agente #8 — Formación y Conciencia en Privacidad (PIMS UNSA)

Este documento formaliza la especificación técnica del **Agente #8** dentro del ecosistema multiagente del **Privacy Information Management System (PIMS)** de la **Universidad Nacional de San Agustín de Arequipa (UNSA)**.

---

## 1. Identificación y Alcance Normativo

| Metadato | Detalle Técnico |
| :--- | :--- |
| **Identificador** | `agente-formacion-conciencia-iso27701` (Agente #8) |
| **Rol en el PIMS** | Copiloto del DPO y supervisor pedagógico de competencias y concienciación en privacidad |
| **Control ISO 27701 A.3.17** | Formación continua, concienciación y evaluación de competencias en privacidad (Cláusulas 7.2 y 7.3) |
| **Marco Legal Nacional** | Ley N° 29733 (Art. 19 Seguridad) y D.S. 003-2013-JUS (Art. 38 Capacitación Continua Obligatoria) |
| **Protocolo de Integración** | **Model Context Protocol (FastMCP)** + **LangGraph StateGraph** |

---

## 2. Integración con el Orquestador Global del PIMS

El Agente #8 expone su servidor **FastMCP** (`backend/mcp_server.py`) para ser descubierto y consumido por el **Orquestador Central Multiagente** mediante dos modalidades estándar:

```text
       +-------------------------------------------------------+
       |             ORQUESTADOR GLOBAL PIMS UNSA              |
       +-------------------------------------------------------+
                                  |
              Protocolo MCP (SSE / stdio / JSON-RPC)
                                  v
+---------------------------------------------------------------------+
|              AGENTE #8: FORMACIÓN Y CONCIENCIA (FASTMCP)             |
|                                                                     |
|  [Tools de Dominio]                                                 |
|   ├── Tool: consultar_estado_formacion()                            |
|   ├── Tool: gestionar_alta_formacion()  ──────> MCP LMS Mock (Moodle)|
|   ├── Tool: generar_reporte_conciencia()                            |
|   ├── Tool: listar_usuarios()                                       |
|   └── Tool: enviar_correo_masivo() ───────────> MCP Correo Mock     |
|                                                                     |
|  [Motor RAG Semántico] (ChromaDB + ONNX)                             |
|   ├── buscar_normativa_iso() (1,285 chunks)                         |
|   └── buscar_politica_negocio() (319 chunks)                        |
|                                                                     |
|  [Gobernanza y Supervisión Humana]                                  |
|   └── Protocolo HITL (Human-in-the-Loop) con validación SHA-256    |
+---------------------------------------------------------------------+
```

### Protocolo de Comunicación con el Orquestador:
1. **Descubrimiento de Herramientas (`tools/list`):** El Orquestador consulta la lista de herramientas disponibles mediante FastMCP y recibe los esquemas JSON de cada Tool.
2. **Invocación de Herramientas (`tools/call`):** El Orquestador solicita la ejecución de una herramienta pasando parámetros tipados (`user_id`, `formacion_id`, `filtros`, etc.).
3. **Cliente Despachador Interno (`MCPClient`):** En `backend/mcp_client.py`, el agente gestiona tanto las herramientas propias como los conectores externos hacia otros servicios del PIMS.

---

## 3. Catálogo Exhaustivo de Herramientas MCP (FastMCP Tools)

Ubicación del código fuente: [`backend/mcp_server.py`](file:///c:/Users/dhuam/Desktop/REM/auditorioa/agente-formacion-conciencia-iso27701/backend/mcp_server.py)

### Tool 1: `consultar_estado_formacion`
- **Propósito:** Evalúa el avance del personal frente a la matriz formativa obligatoria en privacidad.
- **Firma:** `consultar_estado_formacion(user_id: str) -> dict`
- **Parámetros:**
  - `user_id` *(str, requerido)*: Identificador institucional del usuario (ej: `carlos.ruiz`, `maria.lopez`).
- **Retorno:**
  - `status`: `"success"` | `"error"`
  - `usuario`: Datos de identidad, rol y facultad.
  - `resumen`: `total_formaciones`, `completadas`, `pendientes`, `vencidas`, `porcentaje_cumplimiento`.
  - `formaciones`: Lista detallada de cursos con fechas de vencimiento y URLs de certificados.
- **Control ISO:** A.3.17 (Cláusulas 7.2 y 7.3).

---

### Tool 2: `gestionar_alta_formacion`
- **Propósito:** Asigna un módulo formativo en base de datos y orquesta la matrícula física en el LMS institucional.
- **Firma:** `gestionar_alta_formacion(user_id: str, formacion_id: str) -> dict`
- **Parámetros:**
  - `user_id` *(str, requerido)*: Identificador del usuario a matricular.
  - `formacion_id` *(str, requerido)*: Código de la formación (ej: `f001` Ley 29733, `f002` Fundamentos PIMS, `f003` Cultura y Concienciación).
- **Conector Externo Invocado:**
  - **`mcp_externos.lms_mock.matricular`**: Simula la integración con Moodle UNSA, genera ID de matrícula persistente en `matriculas_lms_mock` y audita la acción.
- **Retorno:** `asignacion_id`, `curso`, `control_iso`, `fecha_vencimiento` (30 días), `lms_integracion`.
- **Control ISO:** A.3.17 (Cláusula 7.2).

---

### Tool 3: `generar_reporte_conciencia`
- **Propósito:** Agrega y consolida métricas cuantitativas de avance y sensibilización para auditorías PIMS del DPO y decanatos.
- **Firma:** `generar_reporte_conciencia(facultad: Optional[str] = None) -> dict`
- **Parámetros:**
  - `facultad` *(str, opcional)*: Nombre de la facultad a filtrar (ej: `"Ingeniería"`, `"Medicina"`, `"Derecho"`). Si se omite, calcula la métrica global de la universidad.
- **Retorno:**
  - `total_usuarios`: Número de personas evaluadas.
  - `tasa_cumplimiento_formacion_pct`: Tasa de finalización formativa.
  - `formaciones`: Detalle de cursos completados, pendientes y vencidos.
- **Control ISO:** A.3.17 (Cláusulas 7.2 y 9.1).

---

### Tool 4: `evaluar_matriz_brechas`
- **Propósito:** Computa la Matriz de Brechas de Competencia por Rol (Skill Gap Analysis) cruzando usuarios activos contra requisitos formativos normativos.
- **Firma:** `evaluar_matriz_brechas(rol: Optional[str] = None) -> dict`
- **Parámetros:**
  - `rol` *(str, opcional)*: Filtrar por estamento (`"docente"`, `"administrativo"`, `"jefe"`, `"admin"`). Si se omite, calcula la matriz integral universitaria.
- **Retorno:**
  - `normas_aplicadas`: Lista de estándares (ISO 27701 Cl. 7.2, 7.3, A.3.17, A.3.11, Ley 29733 Art. 38).
  - `kpis`: `cumplimiento_global_pct`, `gap_promedio_pct`, `meta_institucional_pct` (85%), `brechas_criticas_conteo`.
  - `roles`: Desglose detallado por rol con competencias, % de brecha, severidad y personal afectado.
- **Control ISO:** Cláusula 7.2 (Competencia), Cláusula 7.3 (Toma de conciencia) y Control A.3.17.

---

### Tool 5: `evaluar_mapa_calor`
- **Propósito:** Computa el Mapa de Calor (Heatmap) de Vulnerabilidad y Sensibilización sobre Riesgos PII en 6 dominios temáticos clave.
- **Firma:** `evaluar_mapa_calor(facultad: Optional[str] = None) -> dict`
- **Parámetros:**
  - `facultad` *(str, opcional)*: Filtrar por unidad académica o facultad (ej: `"Ingeniería"`, `"Medicina"`).
- **Retorno:**
  - `kpis`: `indice_global_sensibilizacion` (0-100), `vulnerabilidad_promedio_pct`, `zona_termica_critica`, `ejes_en_alerta_roja`.
  - `ejes`: 6 dominios con su temperatura (°), índice, nivel térmico y estado de cursos.
  - `matriz_bidimensional`: Distribución de calor térmico cruzada (Eje x Facultad).
- **Control ISO:** Control A.3.17 (Sensibilización), Control A.3.11 (Gestión de Incidentes) y Ley N° 29733 Art. 19.

---

### Tool 6: `evaluar_radar_cobertura`
- **Propósito:** Computa el Gráfico de Radar de Cobertura Multiaxial por Estamento Universitario (Docentes, Administrativos, Jefaturas, TI y Auditoría).
- **Firma:** `evaluar_radar_cobertura(estamento: Optional[str] = None, facultad: Optional[str] = None) -> dict`
- **Parámetros:**
  - `estamento` *(str, opcional)*: Filtrar por estamento universitario (`"docente"`, `"administrativo"`, `"jefe"`, `"admin"`, `"auditor"`).
  - `facultad` *(str, opcional)*: Filtrar por unidad académica (ej: `"Ingeniería"`, `"Medicina"`).
- **Retorno:**
  - `kpis`: `cobertura_global_pct`, `eficacia_global_pct`, `meta_institucional_pct` (90%), `estamento_lider`, `estamento_rezagado`.
  - `estamentos`: Detalle multiaxial de padrón, inscritos, aprobados, tasas de cobertura y estado del radar.
  - `radar_chart`: Coordenadas poligonales SVG calculadas para renderizar el Spider Chart.
- **Control ISO:** Control A.3.17 (Formación y Conciencia), Cláusula 7.2 (Competencia) y Ley N° 29733 Art. 19.

---

### Tool 7: `crear_formulario_capacitacion`
- **Propósito:** Genera y gestiona formularios interactivos tipo Google Forms / encuestas formativas para medir el nivel de conciencia y evaluar conocimientos en privacidad.
- **Firma:** `crear_formulario_capacitacion(titulo: str, descripcion: str, curso_id: Optional[str] = None, preguntas: Optional[list] = None, destinatarios: Optional[list] = None) -> dict`
- **Parámetros:**
  - `titulo` *(str)*: Nombre formal del formulario o cuestionario de evaluación.
  - `descripcion` *(str)*: Instrucciones para los participantes y referencia al curso PIMS.
  - `preguntas` *(list, opcional)*: Lista estructurada de preguntas con opciones múltiples, escalas de vulnerabilidad y control ISO asociado.
  - `destinatarios` *(list, opcional)*: Lista de correos o IDs de personal convocados a responder.
- **Retorno:** `form_id`, `enlace_formulario`, `total_preguntas`, `destinatarios`, `mensaje`.
- **Protocolo de Seguridad:** Requiere aprobación previa mediante **Human-in-the-Loop (HITL)** para previsualizar el formulario y autorizar el despacho masivo.

---

### Tool 8: `programar_evento_calendario`
- **Propósito:** Agenda sesiones formativas, seminarios y recordatorios en los calendarios institucionales (Google Calendar / Outlook mock) con sincronización de invitaciones y enlace Google Meet.
- **Firma:** `programar_evento_calendario(titulo: str, fecha_inicio: str, duracion_minutos: int, descripcion: str, asistentes: list, ubicacion: str, enlace_reunion: str) -> dict`
- **Parámetros:**
  - `titulo` *(str)*: Asunto del evento o taller formativo.
  - `fecha_inicio` *(str)*: Fecha y hora en formato ISO (ej: `"2026-10-26T10:00:00"`).
  - `duracion_minutos` *(int, default=60)*: Duración de la sesión.
  - `asistentes` *(list)*: Direcciones de correo electrónico del personal convocado.
  - `ubicacion` *(str)*: Google Meet o sala física universitaria.
- **Retorno:** `evento_id`, `fecha_inicio`, `enlace_reunion`, `recordatorio` (15 min antes), `asistentes`.
- **Protocolo de Seguridad:** Requiere aprobación previa mediante **Human-in-the-Loop (HITL)** para confirmar fecha, hora y lista de invitados.

---

### Tool 9: `listar_usuarios`
- **Propósito:** Consulta y segmenta el personal aplicando control de acceso basado en roles (RBAC).
- **Firma:** `listar_usuarios(filtros: dict, solicitante_rol: str, solicitante_facultad: str, solicitante_id: str) -> dict`
- **Parámetros:**
  - `filtros` *(dict)*: Criterios de filtrado (`"rol"`, `"facultad"`, `"antiguedad_dias"`).
  - `solicitante_rol` *(str)*: Rol del solicitante (`"admin"`, `"jefe"`, `"docente"`).
- **Regla de Privacidad (RBAC):** Jefes de departamento solo pueden visualizar personal de su propia facultad; docentes y administrativos solo acceden a sus propios datos.
- **Retorno:** `total`, `usuarios` (lista sanitizada sin hashes de contraseña).

---

### Tool 10: `enviar_correo_masivo`
- **Propósito:** Envío auditado de convocatorias a talleres, recordatorios de vencimiento de cursos y notificaciones preventivas con supervisión humana.
- **Firma:** `enviar_correo_masivo(user_ids: list, asunto: str, cuerpo: str, remitente_id: str) -> dict`
- **Parámetros:**
  - `user_ids` *(list)*: Lista de IDs de usuarios o direcciones de correo electrónico.
  - `asunto` *(str)*: Asunto formal de la comunicación.
  - `cuerpo` *(str)*: Contenido redactado del correo.
  - `remitente_id` *(str, default="admin")*: Identificador del usuario que autoriza el despacho.
- **Conector Externo Invocado:**
  - **`mcp_externos.correo_mock.enviar_correo`**: Soporta despacho físico real vía **Resend API** o **SMTP Gmail / Google Workspace**, y genera un hash criptográfico **SHA-256** registrado en `correos_enviados` para no repudio.
- **Protocolo de Seguridad:** Esta herramienta requiere aprobación previa mediante **Human-in-the-Loop (HITL)**.

---

### Herramientas Auxiliares de Integración Externa:
- **`consultar_pii(query)`**: Consulta simulada de bases de datos legadas con filtrado de datos sensibles en `mcp_externos/postgres_mock.py`.
- **`guardar_evidencia(user_id, archivo, control_iso, contenido)`**: Almacena evidencias documentales y certificados en el directorio `./evidencias/` mediante `mcp_externos/evidencias_mock.py`.

---

## 4. Estándar de Excelencia y Artesanía en Respuestas (Diseño Impeccable)

Para garantizar una experiencia de usuario de nivel institucional y erradicar patrones de respuestas genéricas o descuidadas, el Agente debe ceñirse a las siguientes directivas de artesanía:

1. **Tipografía y Estructura Jerárquica:**
   - Utilizar Markdown estructurado con títulos claros (`###`), tablas comparativas cuando existan métricas o fechas, y bloques de código para identificadores (`fu_001`, `f001`, hashes SHA-256).
   - Evitar bloques densos e interminables de texto; priorizar listas con viñetas temáticas y descansos visuales.

2. **Cero Relleno ("No AI Fluff"):**
   - Prohibido utilizar introducciones o conclusiones vacías (*"¡Hola! Claro que sí, con mucho gusto te ayudo con eso..."*).
   - Iniciar inmediatamente con la respuesta concreta, el diagnóstico o la acción solicitada.

3. **Rigor Jurídico Agustino:**
   - Citar siempre con precisión el marco normativo aplicable: **Control ISO/IEC 27701:2025 A.3.17**, **Ley N° 29733** y **D.S. 003-2013-JUS Art. 38**.

4. **Accionabilidad Proactiva:**
   - Al finalizar cada interacción, sugerir los siguientes pasos institucionales lógicos (ej: *"¿Deseas que redacte la convocatoria por correo para los 5 usuarios pendientes?"*).

