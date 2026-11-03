---
name: generar-soa
version: 2.1.0
author: Escuela Profesional de Ingeniería de Sistemas - UNSA
category: auditoria-sistemas-pims
standard: ISO/IEC 27701:2025 (Harmonized Structure & Anexo A)
description: >
  Genera la Declaración de Aplicabilidad (SoA) formal, algorítmica y determinista del
  Sistema de Gestión de Información de Privacidad (PIMS) conforme a ISO/IEC 27701:2025,
  contextualizada para la Universidad Nacional de San Agustín de Arequipa (UNSA).
  Evalúa aplicabilidad por rol (A.1 Responsable, A.2 Encargado, A.3 Común), calcula estados
  probatorios estrictos, vincula directivas institucionales mediante búsqueda semántica
  vectorial (FAISS) y emite la matriz de brechas con trazabilidad de gobernanza humana.
tools:
  - engine_regla_aplicabilidad
  - engine_regla_estado_probatorio
  - faiss_rag_politicas_retriever
  - gap_matrix_analyzer
---

# SKILL-01: Generación de la Declaración de Aplicabilidad (SoA)

## 1. Identidad y Ficha Metodológica
- **Identificador Único:** `SKILL-PIMS-CONTROLES-001`
- **Nombre:** `generar-soa`
- **Paradigma:** Transición formal *"De Prompt a Skill"* (Procedimiento determinista, tipado y reproducible).
- **Alcance Institucional:** Sistemas de información de la Universidad Nacional de San Agustín (UNSA): SISUNSA, Comedor Universitario, Admisión y Biblioteca Central.
- **Marco Normativo:** Cláusula 6.1.3 y Anexo A de la norma ISO/IEC 27701:2025; Ley N° 29733 (Ley de Protección de Datos Personales del Perú).

---

## 2. Condiciones de Activación (Triggers)

### Activación Automática / Vía Orquestador:
- Invocación desde el orquestador **n8n** mediante el nodo HTTP POST `/api/controles/ejecutar`.
- Finalización de un ciclo de recopilación de evidencias por parte del *Agente de Evidencia*.
- Actualización de la matriz de riesgos por parte del *Agente de Riesgos*.
- Petición explícita del Oficial de Protección de Datos (DPO) o auditor líder para emitir la SoA oficial.

### Cuándo NO se activa:
- Consultas conceptuales o de texto libre sobre la norma (usar operación `consultar`).
- Auditorías sobre un único control específico (usar `verificar-controles`).

---

## 3. Especificación del Contrato de Entrada (Input Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GenerarSoAInput",
  "type": "object",
  "required": ["operacion", "perfil"],
  "properties": {
    "operacion": {
      "type": "string",
      "enum": ["generar_soa"]
    },
    "perfil": {
      "type": "object",
      "required": ["rol"],
      "properties": {
        "organizacion": {
          "type": "string",
          "default": "Universidad Nacional de San Agustín (UNSA)",
          "description": "Nombre o entidad institucional auditada."
        },
        "rol": {
          "type": "string",
          "enum": ["responsable", "encargado", "ambos"],
          "description": "Rol PIMS: 'responsable' (PII Controller), 'encargado' (PII Processor) o 'ambos'."
        }
      }
    },
    "riesgos": {
      "type": "array",
      "description": "Matriz de riesgos provista por el Agente de Riesgos.",
      "items": {
        "type": "object",
        "required": ["id", "controles"],
        "properties": {
          "id": { "type": "string", "example": "R-UNSA-01" },
          "descripcion": { "type": "string" },
          "controles": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "evidencias": {
      "type": "array",
      "description": "Inventario de artefactos probatorios recopilados por el Agente de Evidencia.",
      "items": {
        "type": "object",
        "required": ["control", "descripcion", "estado"],
        "properties": {
          "control": { "type": "string", "example": "A.1.2.2" },
          "descripcion": { "type": "string", "example": "[Archivo: Res-CU-045-2026.pdf] Reglamento de SISUNSA" },
          "estado": { "type": "string", "enum": ["implementado", "parcial"] }
        }
      }
    }
  }
}
```

---

## 4. Recursos del Conocimiento (Knowledge Base & RAG)

El Skill consume recursos locales blindados sin dependencia de internet ni servicios de terceros:
1. `knowledge/catalogo_controles.json`: Catálogo normativo con 10 controles representativos del Anexo A y su agente responsable asignado.
2. `knowledge/politicas/`: Repositorio de políticas institucionales (Directiva `DIR-OTIC-004-UNSA`).
3. **Índice Vectorial Local:** Modelo `paraphrase-multilingual-MiniLM-L12-v2` con índice `FAISS IndexFlatIP` (similitud coseno normalizada).

---

## 5. Procedimiento Operativo Estándar (Algoritmo Determinista)

```
[Paso 1: Validación Estricta]
  │── Validar perfil.rol ∈ {"responsable", "encargado", "ambos"}.
  └── Si falla: Abortar inmediatamente con estado="rechazada" (HTTP 400).
[Paso 2: Carga de Catálogo]
  └── Cargar la totalidad de controles C_i ∈ catalogo_controles.json.
[Paso 3: Evaluación de Aplicabilidad por Rol]
  ├── Si Prefijo(C_i) == "A.1" ➔ Aplica si rol ∈ {"responsable", "ambos"}.
  ├── Si Prefijo(C_i) == "A.2" ➔ Aplica si rol ∈ {"encargado", "ambos"}.
  └── Si Prefijo(C_i) == "A.3" ➔ Aplica SIEMPRE (Controles comunes universales).
[Paso 4: Redacción de Justificación Normativa]
  ├── Si Aplica: Redactar motivo por rol + vincular IDs de riesgos {R_k | C_i ∈ R_k.controles}.
  └── Si No Aplica: Justificación formal obligatoria de exclusión (Prohibida la exclusión en blanco).
[Paso 5: Cálculo Determinista del Estado Probatorio]
  ├── Si Aplica == False ➔ estado = "no aplica".
  ├── Si Existe e ∈ Evidencias(C_i) con e.estado == "implementado" ➔ estado = "implementado".
  ├── Si Existe e ∈ Evidencias(C_i) con e.estado == "parcial" ➔ estado = "parcial".
  └── Si Evidencias(C_i) == ∅ ➔ estado = "no implementado" (Regla de oro: Sin evidencia = No cumple).
[Paso 6: Asociación Semántica de Directivas (RAG)]
  └── Ejecutar consulta FAISS con C_i.nombre sobre políticas UNSA (Umbral θ = 0.30).
[Paso 7: Detección y Asignación de Brechas]
  └── ∀ C_i donde Aplica == True ∧ estado ≠ "implementado":
        Registrar en brechas con solicitar_a = C_i.agente_responsable.
[Paso 8: Agregación de Métricas]
  └── Computar totales: evaluados, aplican, excluidos, implementados, parciales, no_implementados.
[Paso 9: Marcado de Gobernanza y Supervisión Humana]
  └── Asignar requiere_revision_humana = True y confianza = 1.0.
```

---

## 6. Especificación del Contrato de Salida (Output Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GenerarSoAOutput",
  "type": "object",
  "required": ["agente", "operacion", "estado", "respuesta", "datos", "requiere_revision_humana"],
  "properties": {
    "agente": { "type": "string", "const": "controles" },
    "operacion": { "type": "string", "const": "generar_soa" },
    "estado": { "type": "string", "enum": ["ok", "rechazada"] },
    "respuesta": { "type": "string" },
    "datos": {
      "type": "object",
      "required": ["soa", "brechas", "resumen"],
      "properties": {
        "soa": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "control": { "type": "string" },
              "nombre": { "type": "string" },
              "aplica": { "type": "boolean" },
              "justificacion": { "type": "string" },
              "estado": { "type": "string", "enum": ["implementado", "parcial", "no implementado", "no aplica"] },
              "evidencias": { "type": "array", "items": { "type": "string" } },
              "politica_relacionada": { "type": ["string", "null"] },
              "responsable": { "type": "string" }
            }
          }
        },
        "brechas": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "control": { "type": "string" },
              "nombre": { "type": "string" },
              "estado": { "type": "string" },
              "solicitar_a": { "type": "string" }
            }
          }
        },
        "resumen": {
          "type": "object",
          "properties": {
            "controles_evaluados": { "type": "integer" },
            "aplican": { "type": "integer" },
            "excluidos": { "type": "integer" },
            "implementados": { "type": "integer" },
            "parciales": { "type": "integer" },
            "no_implementados": { "type": "integer" }
          }
        }
      }
    },
    "fuentes": { "type": "array", "items": { "type": "string" } },
    "confianza": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "requiere_revision_humana": { "type": "boolean", "const": true }
  }
}
```

---

## 7. Matriz de Manejo de Errores y Excepciones

| Código / Condición de Excepción | Causa Raíz | Acción del Skill | Estado Emitido |
|---|---|---|---|
| `ERR_ROL_INVALIDO` | `perfil.rol` ausente o fuera de enum | Abortar ejecución; solicitar definición de rol en el perfil. | `"rechazada"` |
| `ERR_CATALOGO_NO_DISPONIBLE` | Fallo de lectura en `catalogo_controles.json` | Notificar error crítico de configuración de conocimiento. | `"rechazada"` |
| `WARN_SIN_EVIDENCIAS` | Arreglo `evidencias` vacío o no provisto | Procesar normalmente; calificar 100% de aplicables como "no implementado". | `"ok"` |
| `WARN_POLITICA_BAJA_SIMILITUD` | Score FAISS < 0.30 para un control | Asignar `politica_relacionada: null` sin detener el flujo. | `"ok"` |

---

## 8. Invariantes de Seguridad y Reglas de Oro

1. **Principio de Verificación Probatoria (Inmunidad a Alucinaciones):** Bajo ninguna circunstancia un control puede ser calificado como `"implementado"` mediante razonamiento generativo. La calificación depende estrictamente de la presencia de un artefacto probatorio registrado.
2. **Prohibición de Exclusión Silenciosa:** Todo control del catálogo excluido debe contar con una justificación documentada basada en el rol de la organización.
3. **Principio de Supervisión Humana (Human-in-the-Loop):** El sistema opera como un instrumento analítico; la SoA tiene rango de *propuesta técnica* y nunca posee carácter auto-aprobatorio.
4. **Determinismo Algorítmico:** Dos ejecuciones con el mismo payload de entrada deben generar exactamente la misma matriz SoA e idénticas métricas numéricas.
