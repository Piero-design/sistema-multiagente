---
name: mapear-tratamientos-inventario
description: Prepara el mapa de tratamientos y flujos por activo del Grupo 06 con contexto declarado y pendientes. Usar al consultar finalidades, responsables, accesos, conservación, transferencias o cobertura de sistemas.
---

# Mapear tratamientos

- Usa `inventario_mapear_tratamientos(organizacion, sistema)` para activos persistidos; el análisis también devuelve una propuesta sin guardar.
- Genera un tratamiento por activo, vinculado por `activo_id`, sistema, campos y categorías. Este agrupamiento es preliminar: un activo con varias finalidades debe separarse en fuentes distintas o refinarse manualmente.
- `contexto` solo admite finalidad, base jurídica, categorías de titulares, responsable, roles con acceso, almacenamiento, transferencias y retención. Los valores explícitos son `declarado_en_solicitud`; los ausentes, `pendiente`.
- No deduzcas finalidad por el nombre de un sistema, consentimiento por la existencia de un formulario ni retención por costumbre.
- Crea aristas de flujo solo hacia los destinatarios declarados en `transferencias`; si no están documentados, lista el pendiente y no inventes destinos. Una lista ausente/vacía significa desconocido, no «sin transferencias».
- No rellenes bases jurídicas por analogía. La versión actual prepara un borrador técnico, no un RAT jurídicamente validado.
- Para el Grupo 3, `confirmar_cobertura` indica sistemas inventariados o sin activos y devuelve validación requerida. No busca personas, no cambia expedientes DSAR ni aprueba solicitudes.
- Para los grupos 2, 4, 5, 7 y 8, entrega referencias de activo y metadatos pertinentes. Los intercambios preparados no son envíos automáticos ni integración central demostrada.
