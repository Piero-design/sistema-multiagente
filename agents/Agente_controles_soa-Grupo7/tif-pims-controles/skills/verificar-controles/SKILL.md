---
name: verificar-controles
version: 2.1.0
author: Escuela Profesional de Ingeniería de Sistemas - UNSA
category: auditoria-sistemas-pims
standard: ISO/IEC 27701:2025 (Harmonized Structure & Anexo A)
description: >
  Audita el estado de cumplimiento de un control individual del PIMS bajo ISO/IEC 27701:2025
  para la Universidad Nacional de San Agustín (UNSA). Evalúa su aplicabilidad, verifica
  la validez de sus evidencias documentales, asocia la política institucional mediante RAG (FAISS)
  y genera una prescripción técnica accionable dirigida al agente especializado correspondiente.
tools:
  - engine_regla_aplicabilidad
  - engine_regla_estado_probatorio
  - faiss_rag_politicas_retriever
  - prescriptive_recommender
---

# SKILL-02: Verificación y Auditoría Puntual de Controles

## 1. Identidad y Ficha Metodológica
- **Identificador Único:** `SKILL-PIMS-CONTROLES-002`
- **Nombre:** `verificar-controles`
- **Paradigma:** Diagnóstico determinista puntual y emisión de prescripciones técnicas.
- **Alcance Institucional:** Auditoría granular sobre sistemas universitarios (ej. control `A.1.2.6` DPIA en Comedor Universitario o `A.3.12` respuesta a incidentes en OTIC-UNSA).
- **Marco Normativo:** Cláusulas 6.1.3, 9.1 (Seguimiento y Medición), 9.2 (Auditoría Interna) y Anexo A de ISO/IEC 27701:2025.

---

## 2. Condiciones de Activación (Triggers)

### Activación Automática / Vía Orquestador:
- Solicitud de verificación sobre un control específico desde **n8n** o mesa de trabajo del auditor.
- Inspección preliminar de controles de alto riesgo antes de auditorías de certificación externa.
- Re-evaluación rápida de un control tras el envío de una nueva evidencia por parte del *Agente de Evidencia*.

### Cuándo NO se activa:
- Solicitudes de elaboración, actualización global o consolidación de la SoA completa (usar `generar-soa`).

---

## 3. Especificación del Contrato de Entrada (Input Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VerificarControlInput",
  "type": "object",
  "required": ["operacion", "control", "perfil"],
  "properties": {
    "operacion": {
      "type": "string",
      "enum": ["verificar_control"]
    },
    "control": {
      "type": "string",
      "description": "Identificador normativo exacto del control del Anexo A.",
      "example": "A.1.2.6"
    },
    "perfil": {
      "type": "object",
      "required": ["rol"],
      "properties": {
        "organizacion": { "type": "string", "default": "Universidad Nacional de San Agustín (UNSA)" },
        "rol": { "type": "string", "enum": ["responsable", "encargado", "ambos"] }
      }
    },
    "riesgos": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "controles"],
        "properties": {
          "id": { "type": "string" },
          "descripcion": { "type": "string" },
          "controles": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "evidencias": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["control", "descripcion", "estado"],
        "properties": {
          "control": { "type": "string" },
          "descripcion": { "type": "string" },
          "estado": { "type": "string", "enum": ["implementado", "parcial"] }
        }
      }
    }
  }
}
```

---

## 4. Procedimiento Operativo Estándar (Algoritmo de Diagnóstico)

```
[Paso 1: Validación de Integridad]
  ├── Validar que control_id exista en catalogo_controles.json.
  │     └── Si no existe: Abortar con estado="rechazada" ("Control no reconocido en catálogo").
  └── Validar que perfil.rol ∈ {"responsable", "encargado", "ambos"}.
[Paso 2: Evaluación de Aplicabilidad]
  └── Aplicar regla: A.1 (Responsable), A.2 (Encargado), A.3 (Universal).
[Paso 3: Búsqueda y Filtrado de Evidencias Propias]
  └── Filtrar Evidencias(control_id).
[Paso 4: Determinación de Estado Probatorio]
  ├── Si Aplica == False ➔ estado = "no aplica".
  ├── Si hay al menos un artefacto "implementado" ➔ estado = "implementado".
  ├── Si hay al menos un artefacto "parcial" ➔ estado = "parcial".
  └── Si no hay artefactos ➔ estado = "no implementado".
[Paso 5: Vinculación Semántica con Directiva UNSA (RAG)]
  └── Búsqueda vectorial FAISS con control.nombre (Umbral θ = 0.30).
[Paso 6: Emisión de Prescripción y Recomendación Técnica]
  ├── Si "no aplica" ➔ "Documentar formalmente el motivo de exclusión en la SoA institucional."
  ├── Si "implementado" ➔ "Control operativo. Mantener la evidencia vigente para la auditoría interna (Cláusula 9.2)."
  ├── Si "parcial" ➔ "Completar los requisitos pendientes del control con el " + control.agente_responsable + "."
  └── Si "no implementado" ➔ "Solicitar formalmente la implementación y evidencia documental al " + control.agente_responsable + "."
[Paso 7: Empaquetado en Contrato Estándar]
  └── Emitir respuesta JSON con requiere_revision_humana = True.
```

---

## 5. Especificación del Contrato de Salida (Output Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VerificarControlOutput",
  "type": "object",
  "required": ["agente", "operacion", "estado", "respuesta", "datos", "requiere_revision_humana"],
  "properties": {
    "agente": { "type": "string", "const": "controles" },
    "operacion": { "type": "string", "const": "verificar_control" },
    "estado": { "type": "string", "enum": ["ok", "rechazada"] },
    "respuesta": { "type": "string" },
    "datos": {
      "type": "object",
      "required": ["control", "nombre", "aplica", "justificacion", "estado", "responsable", "recomendacion"],
      "properties": {
        "control": { "type": "string", "example": "A.1.2.6" },
        "nombre": { "type": "string", "example": "Evaluación de impacto de privacidad (DPIA)" },
        "aplica": { "type": "boolean", "example": true },
        "justificacion": { "type": "string" },
        "estado": { "type": "string", "enum": ["implementado", "parcial", "no implementado", "no aplica"] },
        "evidencias": { "type": "array", "items": { "type": "string" } },
        "politica_relacionada": { "type": ["string", "null"] },
        "responsable": { "type": "string", "example": "Agente de Riesgos" },
        "recomendacion": { "type": "string", "example": "Solicitar evidencia o implementación al Agente de Riesgos." }
      }
    },
    "fuentes": { "type": "array", "items": { "type": "string" } },
    "confianza": { "type": "number", "const": 1.0 },
    "requiere_revision_humana": { "type": "boolean", "const": true }
  }
}
```

---

## 6. Caso de Uso Canónico (UNSA: Auditoría de DPIA en Comedor)

### Solicitud de Entrada:
```json
{
  "operacion": "verificar_control",
  "control": "A.1.2.6",
  "perfil": { "organizacion": "UNSA", "rol": "responsable" },
  "riesgos": [
    { "id": "R-UNSA-02", "descripcion": "Tratamiento de biometría en Comedor Universitario", "controles": ["A.1.2.6"] }
  ],
  "evidencias": [
    { "control": "A.1.2.6", "descripcion": "[Doc: DPIA-Biometria-Borrador.docx] Avance preliminar", "estado": "parcial" }
  ]
}
```

### Respuesta Emitida:
```json
{
  "agente": "controles",
  "operacion": "verificar_control",
  "estado": "ok",
  "respuesta": "Control A.1.2.6: parcial. Recomendación: Completar la implementación con el Agente de Riesgos.",
  "datos": {
    "control": "A.1.2.6",
    "nombre": "Evaluación de impacto de privacidad (DPIA)",
    "aplica": true,
    "justificacion": "La organización actúa como responsable del tratamiento. Vinculado a los riesgos: R-UNSA-02.",
    "estado": "parcial",
    "evidencias": ["[Doc: DPIA-Biometria-Borrador.docx] Avance preliminar"],
    "politica_relacionada": "POL-UNSA-03. Evaluación de Impacto en la Privacidad (DPIA) para Sistemas Críticos y Biometría",
    "responsable": "Agente de Riesgos",
    "recomendacion": "Completar la implementación con el Agente de Riesgos."
  },
  "fuentes": ["catalogo_controles.json"],
  "confianza": 1.0,
  "requiere_revision_humana": true
}
```
