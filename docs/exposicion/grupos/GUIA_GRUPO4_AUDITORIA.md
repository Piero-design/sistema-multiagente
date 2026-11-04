# Guía Grupo 4 — Agente de Evidencia y Auditoría (AuditPIMS)

Tiempo sugerido: **6–8 min**.

## 1–2. Objetivo y responsabilidad
Evaluar evidencias contra los controles de ISO/IEC 27701 y proponer un dictamen. **Es una propuesta que valida un auditor humano.**

## 3. Arquitectura original
`app_dashboard.py` (FastAPI con dashboard web), `auditor_con_ia.py` (CLI) y `probar_auditor.py` (8 casos offline). La skill `auditoria-evidencias-pims/` con `references/` (catálogo y criterios) y `assets/` (plantillas). Cliente `openai` con proveedor por petición: `gemini`, `groq`, `openai`, `ollama` o `simulador`.

## 4. Skills
`SKILL.md` con tres modos: **M1** planificar, **M2** evaluar evidencias, **M3** consolidar. La evaluación conserva M2; la rama `agente4` incorpora M1 nativo y M3 de consolidación de resultados persistidos.

## 5–6. Flujo
`POST /api/auditar` con `nombre_archivo` y `contenido` → calcula el SHA-256 del texto → carga la skill y las referencias en el contexto del modelo → llama al modelo (hasta 3 intentos) → extrae la severidad buscando frases en la respuesta → devuelve el dictamen en Markdown. Ante errores de cuota existe un motor de contingencia con plantillas (no es un LLM).

## 7. Demostración
`/agentes/auditoria` → "Evaluar evidencia" con una política sin plazos de conservación ni procedimiento de brechas (datos de demostración). Resultado real obtenido: **NO CONFORMIDAD MAYOR** con ficha de evaluación. También "Calcular SHA-256".

## 8. Ejemplo
Entrada: texto de política y nombre de archivo. Salida: `exito`, `sha256`, `severidad`, `dictamen_markdown`, `tiempo_segundos`. El hash es determinista (`abc` → `ba7816bf…15ad`, comprobado en las pruebas).

## 9. Original frente a integrada
El dashboard original (con Tailwind y recursos web externos) se conserva. La integrada ofrece planificar, evaluar, calcular hash y consolidar; la subida de archivos del original no extrae texto de PDFs.

## 10. Gateway LLM
El adaptador envía `proveedor=ollama` y `url_base` del gateway en **cada petición**: el agente no se modifica. Detalle a presentar con honestidad: la etiqueta fija "Ollama Local GPU" del código no es el proveedor real, así que el adaptador la sustituye por "Gateway LLM compartido (modo)".

## 11. PostgreSQL
Sin persistencia propia (devuelve el resultado en memoria); el orquestador guarda la ejecución. Tablas `core_audit*` y `core_document*` de Gestitel serían el destino de resultados en una siguiente etapa.

## 12. Otros agentes
Recibe el handoff `archivar_expediente` de G3 (control A.3.14) y evidencia de G8 (controles 5.24–5.28). El transporte automático no está implementado.

## 13. Problemas y soluciones
- La severidad se obtiene por búsqueda de frases, no por un esquema validado: se documenta como limitación.

## Base normativa
- **ISO/IEC 27701:2025**, **ISO 19011:2018** (auditoría) y **Ley 29733 / D.S. 016-2024-JUS**, según el encabezado de su CLI y sus `references/` (`controles_iso27701.md`, `criterios_evaluacion.md`, `ley29733_resumen.md`).
- Seis criterios de evaluación de la evidencia: pertinencia, suficiencia, vigencia, aprobación, trazabilidad y completitud, con una tabla de decisión que clasifica en **No conformidad mayor**, **menor**, etc.
- **Cuidado:** su catálogo usa identificadores propios (CL-, RT-, EN-, SG-) que **no son números de control de la norma**; el propio archivo dice que la numeración es referencial y debe verificarse con el texto oficial.

## 14. Guion
"Nuestro agente no certifica: propone. Evalúa una evidencia con la skill de auditoría y entrega un dictamen para el auditor. Aquí cargamos una política incompleta y el agente la marca como no conformidad mayor, calculando además el hash para trazabilidad."

## 15. Preguntas probables
- *¿Es confiable la severidad?* Es una propuesta; la extrae de frases del modelo y requiere validación humana.
- *¿Qué modelo usa?* El del gateway.
- *¿Guarda las evidencias?* No; solo calcula el hash del texto y devuelve el resultado.

## 16. Conclusiones
Integración limpia: solo cambió la configuración de la petición. Queda pendiente persistir dictámenes en Gestitel.


## Ampliación de la rama agente4
La interfaz integrada incorpora M1 (checklist inicial filtrado por rol), M2 con casos originales y carga de texto, y M3 (matriz e informe de evaluaciones persistidas, no SoA). Ver `docs/integration/GRUPO4_M1_M3.md` para demostración y límites. La validación permanece pendiente; no hay aprobación de auditor registrada.
