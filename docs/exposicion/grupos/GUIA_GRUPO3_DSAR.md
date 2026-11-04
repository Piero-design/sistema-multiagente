# Guía Grupo 3 — Agente de Derechos de Titulares (DSAR)

Tiempo sugerido: **6–8 min**.

## 1–2. Objetivo y responsabilidad
Registrar solicitudes de derechos (información, acceso, portabilidad, rectificación, supresión, oposición), calcular plazos legales (Ley 29733, días hábiles), consultar la norma con citas y preparar borradores. **No aprueba, rechaza ni ejecuta: lo decide una persona.**

## 3. Arquitectura original
Paquete Python `dsar` (≥3.12): servidor **MCP** (`dsar.mcp.server`), RAG BM25, SQLite propia (`dsar.sqlite3`), perfiles legales y política de la organización, y 115 pruebas en `tests/core`.

## 4. Skills y herramientas
Skills `gestionar_derechos`, `registrar_solicitudes`, `seguimiento_solicitudes`. Herramientas MCP: `dsar_crear_caso`, `dsar_estado`, `dsar_plazos`, `dsar_calcular_plazos`, `dsar_listar`, `dsar_borrador` (solo expedientes `APPROVED`), `dsar_consultar_norma`, `dsar_handoffs`.

## 5–6. Flujo
Se crea un expediente con tipo de derecho y fecha → el código calcula plazos (la política interna puede acortarlos, nunca alargarlos) → sin identidad verificada **no se busca ningún registro** (`IDENTITY_PENDING`) → rectificación/supresión/oposición siempre requieren aprobación humana → el borrador solo existe tras la decisión humana.

## 7. Demostración
`/agentes/dsar`: "Calcular plazos" con acceso + supresión (datos de demostración). Resultado verificado: acceso 15 días hábiles por política interna (legal 20), supresión 10 días hábiles. También "Consultar la norma" y "Listar expedientes".

## 8. Entradas y salidas
Entrada: `request_types=[access, erasure]`, `received_at=2026-11-03`. Salida: plazos por derecho con base legal (D.S. 016-2024-JUS, arts. 69 y 82-85) y fechas límite. Es determinista, idéntico antes y después de integrar.

## 9. Original frente a integrado
El agente entregado no trae interfaz de decisión humana. La plataforma ofrece la decisión **solo a una persona con sesión y rol DPO**, en `/revision`: `verify_identity` y `decide` existen solo como funciones Python y **no son herramientas de un modelo**. Se exponen mediante un puente interno que únicamente el backend puede llamar, y la decisión queda atribuida a quien la tomó. Demostración: crear caso → `/revision` → verificar identidad → aprobar → ver los handoffs.

## 10. Gateway LLM
**Hallazgo:** su servidor MCP es determinista y no llama a ningún LLM. La capa `assistant/llm` (Ollama solo en 127.0.0.1, Gemini y Claude Code) existe en el paquete pero este servidor no la usa. Por eso G3 no cambia entre modos `cloud`/`ollama`. La restricción de loopback no se tocó.

## 11. PostgreSQL
Almacén privado SQLite en volumen. Su guía deja abierto si los handoffs se leen como archivos, por MCP o desde la base común.

## 12. Handoffs a otros agentes
El código genera tres: `evidencia` (siempre que hay decisión humana; control A.3.14), `terceros` (rectificación/supresión/oposición aprobadas) e `inventario` (sistemas sin registros). **No genera** handoffs a G8. En la plataforma se pueden leer con `dsar_handoffs`; el transporte automático a otros agentes no está implementado.

## 13. Problemas y soluciones
- El servidor MCP escucha solo en 127.0.0.1 → wrapper de despliegue que fija el host sin editar el módulo.
- Formato de fecha: acepta `AAAA-MM-DD`, no ISO con hora (se detectó al probar).

## Base normativa
- **Ley N.° 29733 y D.S. 016-2024-JUS:** plazos del art. 69 (información 8 días hábiles; acceso 20; rectificación, cancelación y oposición 10), ampliación del art. 71, portabilidad (art. 76.1) y cancelación (arts. 82–85). Verificados en la prueba: acceso 20 legal / 15 por política interna.
- **ISO/IEC 27701:2025**, mapa en `knowledge/references/iso-control-map.md`: A.1.3.2, A.1.3.5, A.1.3.6, A.1.3.7 (acceso, corrección o supresión), A.1.3.8, A.1.3.9, A.1.3.10, A.1.3.11, y de seguridad A.3.9, A.3.14, A.3.25, A.3.31. Los handoffs citan A.3.14, A.1.3.8 y A.1.2.9.
- *Qué decir:* «el plazo no lo calcula un modelo: sale del perfil legal, y la política de la organización solo puede acortarlo». El propio mapa advierte que es un resumen y no reproduce la norma.

## 14. Guion
"Nuestro agente nunca decide por una persona. Calcula plazos con reglas, no con un modelo, y mantiene a un humano en cada decisión que afecta a un titular. Fíjense: sin verificar identidad no busca ningún dato."

## 15. Preguntas probables
- *¿Y si un modelo en la nube viera los datos del titular?* Su diseño solo permite enviar hechos minimizados; además el servidor MCP no usa modelo. No hay prueba automática de esa regla en la plataforma.
- *¿Por qué no hay botón de aprobar?* Es una decisión humana; falta exponerla autenticada.
- *¿Pasó las pruebas tras integrar?* Sí: 115 pasan dentro del contenedor.

## 16. Conclusiones
Es el agente con reglas más estrictas; la integración las conservó (115 pruebas) y evitó exponer acciones de decisión a modelos.
