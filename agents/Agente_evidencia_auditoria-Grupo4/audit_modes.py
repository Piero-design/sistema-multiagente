"""M1: checklist from the group's reference catalog, without invented ISO identifiers."""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter()
ROOT = Path(__file__).parent / "auditoria-evidencias-pims"

class PlanRequest(BaseModel):
    rol: Literal["responsable", "encargado", "ambos"]
    alcance: str = Field(min_length=1, max_length=2000)

@router.post("/api/planificar")
def planificar(req: PlanRequest):
    if not req.alcance.strip():
        raise HTTPException(422, "Indica el alcance de la auditoría")
    prefixes = {"CL", "SG"} | ({"RT"} if req.rol == "responsable" else {"EN"} if req.rol == "encargado" else {"RT", "EN"})
    items = []
    for line in (ROOT / "references/controles_iso27701.md").read_text().splitlines():
        c = [s.strip() for s in line.strip().strip("|").split("|")]
        if len(c) != 5 or c[0].split("-")[0] not in prefixes:
            continue
        management = c[0].startswith("CL-")
        items.append({"codigo_interno": c[0], "tema": c[1], "requisito": c[2], "evidencia_esperada": c[3],
                      "responsable": c[4] if management else "Por asignar",
                      "base_legal": "Ver registro legal aplicable" if management else c[4]})
    return {"modo": "M1", "rol": req.rol, "alcance": req.alcance.strip(), "items": items, "total": len(items),
            "estado_revision": "Pendiente de validación humana",
            "nota": "Checklist inicial filtrado por rol. El auditor ajusta los ítems al alcance y riesgos. Los códigos CL/RT/EN/SG son internos; contrastar referencias normativas y legales con el texto oficial."}
