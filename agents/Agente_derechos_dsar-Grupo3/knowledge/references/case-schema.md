# Esquema del caso de demostracion

## Solicitud de entrada

Campos obligatorios:

```json
{
  "request_id": "DSAR-DEMO-001",
  "principal_id": "person-001",
  "request_types": ["access", "rectification"],
  "received_at": "2026-10-01",
  "policy_id": "PE-LEY29733",
  "identity_verification": {
    "status": "verified",
    "method": "portal-demo",
    "reference": "verification-demo-001"
  }
}
```

`request_types` es una lista con uno o mas derechos: `information`, `access`, `portability`, `rectification`, `erasure` u `objection`. Por compatibilidad se acepta `request_type` con un solo derecho. El perfil decide cuales admite (`information` solo existe en `PE-LEY29733`). El texto libre puede guardarse como contexto, pero nunca se ejecuta ni se interpreta como una instruccion del sistema.

## Perfil de jurisdiccion (politica)

```json
{
  "PE-LEY29733": {
    "label": "Perú - Ley 29733 y Reglamento D.S. 016-2024-JUS",
    "jurisdiction": "PE",
    "day_type": "business",
    "supported_rights": ["information", "access", "portability", "rectification", "erasure", "objection"],
    "response_days_by_right": {"information": 8, "access": 20, "rectification": 10},
    "legal_basis": {"access": "D.S. 016-2024-JUS, art. 69.2"},
    "extension": {"allowed": true, "max_times": 1},
    "holidays": {"2026": ["2026-10-08"]},
    "legal_review_required": false,
    "disclaimer": "Plazos del D.S. 016-2024-JUS para demostracion academica."
  },
  "LAB-30": {
    "label": "Política académica de 30 días",
    "day_type": "calendar",
    "response_days": 30,
    "legal_review_required": false,
    "disclaimer": "Configuracion ficticia; no constituye plazo legal."
  }
}
```

- `day_type`: `business` (excluye sabados, domingos y `holidays`) o `calendar`.
- `response_days_by_right` tiene prioridad sobre `response_days`.
- Sin `supported_rights`, el perfil admite los cinco derechos clasicos (sin `information`).

## Registro sintetico

```json
{
  "principal_id": "person-001",
  "record_id": "crm-001",
  "source_system": "crm-demo",
  "category": "contact",
  "sensitive": false,
  "data": {"email": "demo@example.test"},
  "third_party_fields": []
}
```

## Expediente generado

El expediente incluye como minimo:

- `case_id`, `request_type` (primer derecho), `request_types`, `status` y `deadline_at` (plazo mas cercano);
- `deadlines`: por derecho, `days`, `day_type`, `deadline_at` y `legal_basis`;
- `policy` con `jurisdiction`, `day_type` y `extension`;
- resumen de verificacion de identidad, sin documento identificatorio;
- `discovered_records` con procedencia;
- `hitl.required` y sus razones;
- `proposed_action` (primer derecho) y `proposed_actions` (uno por derecho), todos con `executed: false`;
- `audit_trail` ordenado;
- hashes SHA-256 de los archivos de entrada;
- `rag` con consulta, metodo y fragmentos recuperados;
- advertencia de que se trata de una demostracion academica.

## Contexto RAG

El bloque `rag` identifica el método de recuperación (`retrieval_method`), el modelo, el almacén de fragmentos y su huella. El almacén se guarda en `rag/store/`; el método por defecto (`auto`) es híbrido: fusiona BM25 (raíces de palabras, sinónimos del dominio y títulos) con embeddings densos multilingües (`BAAI/bge-m3`); si el modelo no está disponible usa solo BM25 y lo deja anotado en `fallback_reason`. Los fragmentos y sus metadatos están en `rag/store/chunks.json` y los vectores en `rag/store/vectors.npy`.

Cada fragmento recuperado conserva evidencia suficiente para reproducir la consulta:

```json
{
  "rank": 1,
  "score": 4.281,
  "chunk_id": "iso-control-map-02",
  "source": "iso-control-map.md",
  "section": "Controles principales",
  "sha256": "huella-de-64-caracteres",
  "excerpt": "Fragmento recuperado para fundamentar el borrador."
}
```

El contenido recuperado es contexto de apoyo. No constituye por si mismo una decision legal ni autoriza ejecutar acciones sobre sistemas.
