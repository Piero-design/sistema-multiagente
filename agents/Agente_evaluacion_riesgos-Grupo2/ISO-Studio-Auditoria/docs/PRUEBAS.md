# Plan de validación para integrantes del equipo

Registrar fecha, equipo, versiones y capturas de pantalla de cada prueba (sin mostrar secretos).

| Caso | Acción | Evidencia esperada |
|---|---|---|
| INF-01 | `docker info` y `docker compose ps` | n8n + Qdrant Up |
| N8N-01 | Preguntar «¿qué funciones tienes?» en chat n8n | respuesta de Gemini |
| SKL-01 | Pedir evaluación de un sistema ficticio | nodo `obtener_skill_evaluacion` en verde; preguntas por contexto |
| RAG-01 | Cargar `examples/Documento_Prueba_FARO.pdf` en `prueba_rag_faro` | workflow RAG en verde |
| RAG-02 | Preguntar ID y hora de FARO con Qdrant apuntando a `prueba_rag_faro` | FARO-7429; martes 18:00; nodo Qdrant ejecutado |
| RAG-03 | Reiniciar n8n/Qdrant; nueva sesión; repetir consulta | datos recuperados sin reingesta |
| UI-01 | Mensaje desde React | respuesta real, sin etiqueta «Vista previa» |
| DIA-01 | Pedir diagrama Mermaid de auditoría | diagrama renderizado + SVG/PNG |
| DOC-01 | Crear informe Word | .docx válido, títulos y tabla |
| PDF-01 | Exportar mismo informe a PDF | PDF válido, tablas legibles |
| NOR-01 | Cargar PDF normativo autorizado | verificar cláusulas y páginas contra texto auténtico |

### Ejemplo de consultas

- «Consulta el documento de prueba FARO: ¿cuál es su identificador y cuándo se revisan incidentes?»
- «Crea un diagrama Mermaid de planificación, revisión de controles, evidencias e informe.»
- «Genera en Word un informe con título, resumen, matriz de riesgos y conclusiones para un caso ficticio.»
- «Exporta un informe de auditoría en PDF con tablas y recomendaciones.»

**No interpretar una salida exitosa de Mermaid/Word/PDF como certificación de cumplimiento ISO.**
