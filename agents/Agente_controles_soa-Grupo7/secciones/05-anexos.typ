= Anexos

== Anexo A: Catálogo de Controles de Privacidad (`catalogo_controles.json`)

El catálogo normativo base mapea cada control del Anexo A con el agente especializado encargado de su gestión:

```json
[
  {"id": "A.1.2.2", "nombre": "Identificar propósito", "agente_responsable": "Agente de Inventario"},
  {"id": "A.1.2.9", "nombre": "Registros de tratamiento", "agente_responsable": "Agente de Inventario"},
  {"id": "A.1.2.6", "nombre": "Evaluación de impacto de privacidad (DPIA)", "agente_responsable": "Agente de Riesgos"},
  {"id": "A.1.2.7", "nombre": "Contratos con encargados", "agente_responsable": "Agente de Terceros"},
  {"id": "A.1.3.7", "nombre": "Acceso, corrección o supresión", "agente_responsable": "Agente de Derechos"},
  {"id": "A.1.3.9", "nombre": "Copia de PII", "agente_responsable": "Agente de Derechos"},
  {"id": "A.2.5.7", "nombre": "Divulgación de subcontratistas", "agente_responsable": "Agente de Terceros"},
  {"id": "A.3.11", "nombre": "Planificación de incidentes", "agente_responsable": "Agente de Incidentes"},
  {"id": "A.3.12", "nombre": "Respuesta a incidentes", "agente_responsable": "Agente de Incidentes"},
  {"id": "A.3.17", "nombre": "Concienciación y formación", "agente_responsable": "Agente de Formación"}
]
```

== Anexo B: Especificación de Archivos `SKILL.md`

=== Skill `generar-soa` (`skills/generar-soa/SKILL.md`)

```markdown
---
name: generar-soa
version: 2.1.0
author: Escuela Profesional de Ingeniería de Sistemas - UNSA
category: auditoria-sistemas-pims
standard: ISO/IEC 27701:2025 (Harmonized Structure & Anexo A)
description: Genera la Declaración de Aplicabilidad (SoA) formal, algorítmica y determinista del
  PIMS conforme a ISO/IEC 27701:2025, contextualizada para la UNSA. Evalúa aplicabilidad por rol,
  calcula estados probatorios estrictos, vincula directivas institucionales mediante búsqueda
  semántica vectorial (FAISS) y emite la matriz de brechas con gobernanza humana obligatoria.
tools:
  - engine_regla_aplicabilidad
  - engine_regla_estado_probatorio
  - faiss_rag_politicas_retriever
  - gap_matrix_analyzer
---

# SKILL-01: Generación de la Declaración de Aplicabilidad (SoA)

## 1. Activación
- Invocación desde el orquestador n8n mediante HTTP POST `/api/controles/ejecutar`.
- Ciclo de auditoría global tras recopilación de artefactos del Agente de Evidencia.
- Actualización de amenazas por el Agente de Riesgos.

## 2. Entrada (JSON Tipado)
- perfil: { organizacion: string, rol: "responsable" | "encargado" | "ambos" }
- riesgos: lista de { id: string, descripcion: string, controles: string[] }
- evidencias: lista de { control: string, descripcion: string, estado: "implementado" | "parcial" }

## 3. Algoritmo Operativo Estándar
1. Validar perfil.rol; si es inválido, abortar con estado "rechazada".
2. Cargar catálogo de controles (catalogo_controles.json).
3. Evaluar aplicabilidad por rol: A.1 (responsable), A.2 (encargado), A.3 (común universal).
4. Redactar justificación formal; asociar IDs de riesgos vinculados.
5. Computar estado probatorio: implementado (≥1 evidencia "implementado"), parcial (solo evidencias "parcial"), no implementado (sin evidencias), no aplica (excluido).
6. Búsqueda semántica FAISS sobre directivas de la UNSA (DIR-OTIC-004-UNSA).
7. Identificar brechas y asignar solicitud al agente_responsable del catálogo.
8. Consolidar totales estadísticos y establecer requiere_revision_humana = true.

## 4. Salida
Contrato estándar JSON con { soa, brechas, resumen }, fuentes citadas, confianza 1.0 y bandera de supervisión humana obligatoria.
```

=== Skill `verificar-controles` (`skills/verificar-controles/SKILL.md`)

```markdown
---
name: verificar-controles
version: 2.1.0
author: Escuela Profesional de Ingeniería de Sistemas - UNSA
category: auditoria-sistemas-pims
standard: ISO/IEC 27701:2025 (Harmonized Structure & Anexo A)
description: Audita el estado de cumplimiento de un control individual del PIMS bajo ISO/IEC 27701:2025
  para la UNSA. Evalúa su aplicabilidad, verifica evidencias documentales, asocia la política institucional
  mediante RAG (FAISS) y genera una prescripción técnica accionable dirigida al agente correspondiente.
tools:
  - engine_regla_aplicabilidad
  - engine_regla_estado_probatorio
  - faiss_rag_politicas_retriever
  - prescriptive_recommender
---

# SKILL-02: Verificación y Auditoría Puntual de Controles

## 1. Activación
- Auditoría puntual sobre un control específico (ej. A.1.2.6 DPIA o A.3.12 CSIRT).
- Inspección preliminar antes de auditorías de certificación externa.

## 2. Entrada
- control: identificador normativo exacto (ej. "A.1.2.6")
- perfil: { organizacion, rol }
- riesgos y evidencias: arreglos tipados con artefactos probatorios.

## 3. Procedimiento y Prescripción Accionable
1. Validar que el control exista en el catálogo y que el rol sea válido.
2. Determinar aplicabilidad al rol de la organización.
3. Evaluar estado probatorio determinista a partir de las evidencias del control.
4. Recuperar directiva institucional de la UNSA asociada vía RAG vectorial.
5. Formular prescripción prescriptiva:
   - "no aplica": Documentar formalmente el motivo de exclusión en la SoA.
   - "implementado": Mantener evidencia vigente para la auditoría interna (9.2).
   - "parcial": Completar los requisitos pendientes con el agente responsable.
   - "no implementado": Solicitar formalmente la implementación al agente responsable.
6. Retornar fila diagnóstica tipada en contrato estándar con requiere_revision_humana = true.
```

== Anexo C: Código Fuente Base

=== Módulo RAG Local (`rag.py`)

```python
import glob, os, requests, faiss, numpy as np

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def obtener_embeddings(textos):
    r = requests.post(f"{OLLAMA_URL}/api/embed", json={"model": "all-minilm", "input": textos}, timeout=45)
    vecs = np.asarray(r.json().get("embeddings", []), dtype="float32")
    normas = np.linalg.norm(vecs, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return vecs / normas

class Indice:
    def __init__(self, textos, metas):
        self.textos, self.metas = textos, metas
        self.index = None
        if not textos: return
        vecs = obtener_embeddings(textos)
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(np.asarray(vecs, dtype="float32"))

    def buscar(self, consulta, k=3):
        if self.index is None or not self.textos: return []
        q = obtener_embeddings([consulta])
        scores, ids = self.index.search(q, min(k, len(self.textos)))
        return [
            {"texto": self.textos[i], "meta": self.metas[i], "score": float(s)}
            for s, i in zip(scores[0], ids[0]) if i != -1
        ]

def desde_carpeta(carpeta):
    """Lee los .md de una carpeta y los parte por párrafos extrayendo su identificador."""
    textos, metas = [], []
    for ruta in sorted(glob.glob(os.path.join(carpeta, "*.md"))):
        with open(ruta, encoding="utf-8") as f:
            for parte in f.read().split("\n\n"):
                p = parte.strip()
                if p:
                    textos.append(p)
                    primera_linea = p.split("\n")[0].replace("#", "").strip()
                    if ":" in primera_linea and len(primera_linea.split(":")[0]) < 80:
                        meta_label = primera_linea.split(":")[0].strip()
                    elif len(primera_linea) < 70:
                        meta_label = primera_linea
                    else:
                        meta_label = os.path.basename(ruta)
                    metas.append(meta_label)
    return Indice(textos, metas)
```

=== Agente de Controles (`agents/controles.py`)

```python
import json
import os
from rag import desde_carpeta

ROLES = ("responsable", "encargado", "ambos")
UMBRAL_POLITICA = 0.45
UMBRAL_CONSULTA = 0.30

class AgenteControles:
    nombre = "controles"
    descripcion = "Genera la SoA y verifica la implementación de controles de ISO/IEC 27701:2025."

    def __init__(self, carpeta="knowledge"):
        with open(os.path.join(carpeta, "catalogo_controles.json"), encoding="utf-8") as f:
            self.catalogo = json.load(f)
        self.normativa = desde_carpeta(os.path.join(carpeta, "normativa"))
        self.politicas = desde_carpeta(os.path.join(carpeta, "politicas"))

    def ejecutar(self, entrada):
        operacion = entrada.get("operacion", "consultar")
        try:
            if operacion == "generar_soa":
                return self._generar_soa(entrada)
            if operacion == "verificar_control":
                return self._verificar_control(entrada)
            return self._consultar(entrada.get("solicitud", ""))
        except ValueError as e:
            return self._resp(operacion, "rechazada", f"Entrada inválida: {e}")

    @staticmethod
    def _aplica(control, rol):
        ambito = control["id"][:3]
        if ambito == "A.3":
            return True, "Control común de seguridad: aplica a cualquier rol."
        if ambito == "A.1":
            if rol in ("responsable", "ambos"):
                return True, "La organización actúa como responsable del tratamiento."
            return False, "Excluido: la organización no actúa como responsable (controles A.1)."
        if ambito == "A.2":
            if rol in ("encargado", "ambos"):
                return True, "La organización actúa como encargada del tratamiento."
            return False, "Excluido: la organización no actúa como encargada (controles A.2)."
        raise ValueError(f"ámbito desconocido en el control {control['id']}")

    @staticmethod
    def _estado(control_id, evidencias):
        propias = [e for e in evidencias if e.get("control") == control_id]
        if any(e.get("estado") == "implementado" for e in propias):
            return "implementado", propias
        if any(e.get("estado") == "parcial" for e in propias):
            return "parcial", propias
        return "no implementado", propias

    def _fila(self, control, rol, riesgos, evidencias):
        aplica, justificacion = self._aplica(control, rol)
        vinculados = [r["id"] for r in riesgos if control["id"] in r.get("controles", [])]
        if aplica and vinculados:
            justificacion += f" Vinculado a los riesgos: {', '.join(vinculados)}."

        if aplica:
            estado, propias = self._estado(control["id"], evidencias)
        else:
            estado, propias = "no aplica", []

        hits = self.politicas.buscar(control["nombre"], k=1)
        politica = hits[0]["meta"] if hits and hits[0]["score"] >= UMBRAL_POLITICA else None

        return {
            "control": control["id"],
            "nombre": control["nombre"],
            "aplica": aplica,
            "justificacion": justificacion,
            "estado": estado,
            "evidencias": [e.get("descripcion", "") for e in propias],
            "politica_relacionada": politica,
            "responsable": control["agente_responsable"],
        }

    def _generar_soa(self, entrada):
        perfil = entrada.get("perfil") or {}
        rol = perfil.get("rol")
        if rol not in ROLES:
            raise ValueError("perfil.rol debe ser 'responsable', 'encargado' o 'ambos'")
        riesgos = entrada.get("riesgos", [])
        evidencias = entrada.get("evidencias", [])

        soa = [self._fila(c, rol, riesgos, evidencias) for c in self.catalogo]
        aplicables = [f for f in soa if f["aplica"]]
        brechas = [
            {"control": f["control"], "nombre": f["nombre"], "estado": f["estado"],
             "solicitar_a": f["responsable"]}
            for f in aplicables if f["estado"] != "implementado"
        ]
        resumen = {
            "controles_evaluados": len(soa),
            "aplican": len(aplicables),
            "excluidos": len(soa) - len(aplicables),
            "implementados": sum(f["estado"] == "implementado" for f in aplicables),
            "parciales": sum(f["estado"] == "parcial" for f in aplicables),
            "no_implementados": sum(f["estado"] == "no implementado" for f in aplicables),
        }
        org = perfil.get("organizacion", "la organización")
        texto = (
            f"SoA generada para {org} (rol: {rol}). Controles evaluados: "
            f"{resumen['controles_evaluados']}; aplican: {resumen['aplican']}; "
            f"implementados: {resumen['implementados']}; brechas: {len(brechas)}. "
            "Requiere revisión y aprobación humana."
        )
        return self._resp(
            "generar_soa", "ok", texto,
            datos={"soa": soa, "brechas": brechas, "resumen": resumen},
            fuentes=["catalogo_controles.json"], confianza=1.0, revision=True,
        )

    def _verificar_control(self, entrada):
        cid = entrada.get("control")
        control = next((c for c in self.catalogo if c["id"] == cid), None)
        if control is None:
            raise ValueError(f"el control '{cid}' no está en el catálogo")
        rol = (entrada.get("perfil") or {}).get("rol")
        if rol not in ROLES:
            raise ValueError("perfil.rol debe ser 'responsable', 'encargado' o 'ambos'")

        fila = self._fila(control, rol, entrada.get("riesgos", []), entrada.get("evidencias", []))
        fila["recomendacion"] = self._recomendar(fila)
        texto = f"Control {fila['control']} ({fila['nombre']}): {fila['estado']}. {fila['recomendacion']}"
        return self._resp(
            "verificar_control", "ok", texto, datos=fila,
            fuentes=["catalogo_controles.json"], confianza=1.0,
        )

    @staticmethod
    def _recomendar(fila):
        if not fila["aplica"]:
            return "Documentar la exclusión y su justificación en la SoA."
        if fila["estado"] == "implementado":
            return "Mantener la evidencia vigente para la auditoría interna (cláusula 9.2)."
        if fila["estado"] == "parcial":
            return f"Completar la implementación; coordinar con el {fila['responsable']}."
        return f"Solicitar evidencia o implementación al {fila['responsable']}."

    def _consultar(self, solicitud):
        if not solicitud.strip():
            return self._resp("consultar", "rechazada", "La consulta está vacía.")
        hits = self.normativa.buscar(solicitud, k=3)
        if not hits or hits[0]["score"] < UMBRAL_CONSULTA:
            return self._resp(
                "consultar", "sin_respuesta",
                "No tengo información suficiente en mi base de conocimiento para responder.",
                confianza=hits[0]["score"] if hits else 0.0,
            )
        return self._resp(
            "consultar", "ok", "\n\n".join(h["texto"] for h in hits),
            fuentes=sorted({h["meta"] for h in hits}),
            confianza=round(hits[0]["score"], 3),
        )

    @staticmethod
    def _resp(operacion, estado, respuesta, datos=None, fuentes=None,
              confianza=0.0, revision=False):
        return {
            "agente": "controles",
            "operacion": operacion,
            "estado": estado,
            "respuesta": respuesta,
            "datos": datos or {},
            "fuentes": fuentes or [],
            "confianza": confianza,
            "requiere_revision_humana": revision,
        }
```
