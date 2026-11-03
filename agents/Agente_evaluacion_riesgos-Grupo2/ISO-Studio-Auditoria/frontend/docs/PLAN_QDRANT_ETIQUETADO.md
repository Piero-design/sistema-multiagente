# Procedimiento de corpus aprobado en Qdrant (manual, sin sobrescribir la colección anterior)

1. Deja intacta `iso27701_2025` y cualquier colección histórica (respaldo).
2. Crea una nueva colección denominada `iso_gr_2026`, usando el mismo modelo/dimensión de embeddings del workflow RAG.
3. Para ISO/IEC 27701:2025 ingesta SOLO secciones GR-01..06 señaladas en `scope-policy.json`. No ingestar anexos no entregados.
4. Para CISA, NO ingestar las 408 páginas: selecciona solo las páginas enumeradas en el reglamento. Almacena los extractos sin alterar su atribución original.
5. Metadatos obligatorios por fragmento: `scope_id: ISO-GR-2026`, `approved: true` (booleano), `topic_id` (GR-01..06), `source_id` (ISO27701_2025_EXTRACT o CISA_2024_EXTRACT), `source_type` (NORMA_ISO o MANUAL_CISA), `pdf_page` (entero).
6. Configura el nodo Qdrant Vector Store del workflow principal en **Retrieve Documents as Tool** (y/o el workflow RAG) para que apunte a `iso_gr_2026`, no a la colección antigua. Aplica filtro `scope_id == ISO-GR-2026`, `approved == true` y `topic_id` autorizado si la versión del nodo lo soporta. Aun sin filtro, el aislamiento por colección será obligatorio.
7. Confirma con una consulta permitida que aparecen referencias correctas a fuente y página; confirma que preguntas de redes y programación no obtienen fragmentos no autorizados.
8. Comprueba que el subworkflow de ingestión use solo la colección nueva y esté deshabilitado para usuarios comunes; el rol de autor del corpus no debe estar en la interfaz pública.

Este ZIP NO incluye ni distribuye el texto completo de los libros (derechos de autor) ni ejecuta la ingestión en tu Docker. El filtrado es una operación manual por tu entorno n8n/Qdrant.
