"""M3 consolidates actual persisted M2 outputs; never generates a SoA or infers approval."""
import uuid
from collections import Counter
from backend.services import db


def consolidate(ids):
    if not isinstance(ids, list) or not 1 <= len(ids) <= 50:
        raise ValueError("Selecciona entre 1 y 50 evaluaciones M2")
    ids = list(dict.fromkeys(str(uuid.UUID(str(i))) for i in ids))
    records = db.query("SELECT id::text, agent_id, action, status, simulated, result, created_at FROM orchestrator.execution WHERE id = ANY(%s::uuid[])", (ids,))
    by_id = {str(row["id"]): row for row in records}
    rows = []
    for eid in ids:
        e = by_id.get(eid)
        if not e or e["agent_id"] != "auditoria" or e["action"] != "auditar" or e["status"] != "succeeded":
            raise ValueError("Cada selección debe ser una evaluación M2 de G4 finalizada correctamente")
        o = e["result"].get("output", {})
        if not o.get("dictamen_markdown") or not o.get("sha256"):
            raise ValueError("La evaluación no contiene dictamen y hash verificables")
        rows.append({"ejecucion_id": eid, "evidencia": o.get("nombre_archivo", "Nombre no registrado; consultar dictamen"),
                     "sha256": o["sha256"], "severidad_propuesta": o.get("severidad", "NO VERIFICABLE"),
                     "estado_revision": "Pendiente de validación humana", "simulado": bool(e["simulated"]), "motor_contingencia": bool(o.get("motor_contingencia")),
                     "dictamen_markdown": o["dictamen_markdown"]})
    severity_order = {"NO CONFORMIDAD MAYOR": 0, "NO CONFORMIDAD MENOR": 1, "NO VERIFICABLE": 2, "OBSERVACIÓN": 3, "CONFORME": 4}
    rows.sort(key=lambda x: severity_order.get(x["severidad_propuesta"], 2))
    summary = dict(Counter(x["severidad_propuesta"] for x in rows))
    report = ["# Informe consolidado de evaluación de evidencias (M3)",
              "Propuesta pendiente de validación humana. No es una declaración de aplicabilidad (SoA).",
              f"Evaluaciones incluidas: {len(rows)}. Se cuentan evaluaciones, no controles únicos.",
              "Las severidades son propuestas extraídas por M2; requieren revisión del dictamen."]
    for x in rows:
        report += [f"## {x['evidencia']}", f"Ejecución: {x['ejecucion_id']}", f"SHA-256 del texto: {x['sha256']}",
                   f"Simulado: {x['simulado']}. Contingencia sin LLM: {x['motor_contingencia']}. {x['estado_revision']}.", x["dictamen_markdown"]]
    return {"modo": "M3", "filas": rows, "resumen": summary, "total_evaluaciones": len(rows),
            "estado_revision": "Pendiente de validación humana", "informe_markdown": "\n\n".join(report)}
