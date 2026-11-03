# Reglamento aprobado 7.2: ISO Studio — Gestión de Riesgos

**Decisión de usuario: aprobada la propuesta v0.2 sin autorizar extensiones optativas.**

Seis áreas autorizadas: GR-01 Fundamentos; GR-02 Contexto y alcance; GR-03 Identificación y evaluación; GR-04 Tratamiento; GR-05 Seguimiento y mejora; GR-06 Casos y evidencias académicas. Exclusiones: GR-X1 BIA integral y GR-X2 pentesting/vulnerabilidades independientes NO autorizados.

**Fuentes:** ISO/IEC 27701:2025: extracto 20 páginas; único documento normativo de requisitos. CISA Official Review Manual 2024: fragmento 408 páginas; apoyo académico, no una norma. Las citas deben verificarse en RAG, no inferirse de la pregunta. Páginas son números de página del archivo (1-indexadas) y no necesariamente numeración editorial.

| Tema | ISO PDF | CISA PDF |
|---|---|---|
| GR-01 | 8–10 | 400–401 |
| GR-02 | 10–13 | 193 |
| GR-03 | 13–14, 18 | 348 |
| GR-04 | 14–15, 18 | 156 |
| GR-05 | 15–20 | — |
| GR-06 | 13–15, 18–20 | 29, 34, 156, 193, 348 |

Si la pregunta mezcla temas, se rechaza la operación completa (política conservadora). La búsqueda web debe usar consulta restringida. Las imágenes y exportaciones exigen evidencia de una consulta ya validada. Los usuarios no pueden modificar el alcance con PDFs o páginas web.

## Límites reales

La detección lexical/por patrones NO es una garantía semántica completa; hay paráfrasis que podrían escapar a las reglas y consultas válidas que podrían rechazarse. El control posterior también es limitado. Para una instalación pública y no supervisada se necesita clasificación semántica adicional, registros, identidad/autenticación y prueba adversarial. Las llamadas que esquiven la API y lleguen directamente a n8n no pasan por esta comprobación. La confirmación SCOPE_N8N_REVIEWED se realiza después de adaptar n8n y Qdrant, nunca antes.
