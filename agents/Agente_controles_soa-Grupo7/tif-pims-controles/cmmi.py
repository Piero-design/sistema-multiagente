"""Motor determinista de madurez CMMI, brechas y prioridad para la SoA (G7).

El motor no depende de la base de datos ni del Word: recibe el catálogo ya
resuelto y las evidencias normalizadas, y devuelve filas de SoA con:

* aplicabilidad por rol (``responsable``, ``encargado``, ``ambos``),
* nivel CMMI 0..5 (0 = Inexistente, 5 = Optimizado),
* ``target_level``, ``gap`` y ``compliance`` (0..100),
* prioridad ``A`` / ``M`` / ``B``,
* estado compatible con el contrato del orquestador:
  ``implementado``, ``parcial``, ``no implementado``, ``no aplica``.

La compatibilidad es deliberada: el estado ``estado`` se deriva de la
evidencia declarada (para que el flujo G5 -> G7 siga detectando el cambio
``Cumple`` -> ``implementado``), mientras que el nivel CMMI es un indicador
adicional y más estricto. Así un ``Cumple`` de G5 puede producir
``estado = implementado`` y, a la vez, ``current_level = 2`` si no existe
corroboración documental de G4.
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Any, Mapping, Sequence

from resolver import Control, ControlResolver, _canonical_code


# ---------------------------------------------------------------------------
# Constantes de negocio
# ---------------------------------------------------------------------------

ROLES = ("responsable", "encargado", "ambos")

ROLE_MAP: dict[str, set[str]] = {
    "A": {"responsable", "encargado", "ambos"},
    "C": {"responsable", "ambos"},
    "P": {"encargado", "ambos"},
}

NIVEL_LABELS = {
    0: "Inexistente",
    1: "Inicial",
    2: "Repetible",
    3: "Definido",
    4: "Gestionado",
    5: "Optimizado",
}

# Responsables institucionales por grupo del Anexo A. No son placeholders:
# son las áreas que la UNSA designa para cada dominio de control.
DEFAULT_RESPONSIBLES: dict[str, str] = {
    "A.5": "Dirección Universitaria de TIC (DUTIC)",
    "A.6": "Oficina de Seguridad de la Información (OSI)",
    "A.7": "Dirección de Recursos Humanos",
    "A.8": "DUTIC — Infraestructura y Operaciones",
    "A.1.2": "Oficialía de Protección de Datos (OPD)",
    "A.1.3": "OPD — Derechos ARCO",
    "A.1.4": "OPD — Gestión de Riesgos de Privacidad",
    "A.1.5": "OPD — Relaciones con Terceros",
    "A.2.2": "OPD — Encargados del Tratamiento",
    "A.2.3": "OPD — Contratos y Transferencias",
    "A.2.4": "OPD — Subcontratistas",
    "A.2.5": "OPD — Supervisión de Encargados",
}
DEFAULT_RESPONSIBLE = "Oficialía de Protección de Datos (OPD)"

_ESTADOS_IMPLEMENTADO = {
    "implementado", "implementada", "cumple", "conforme", "aprobado",
    "aprobada", "vigente", "ok", "si", "completo", "completa", "total",
}
_ESTADOS_PARCIAL = {
    "parcial", "en proceso", "en progreso", "observacion", "observación",
    "no conformidad menor", "borrador", "en revision", "en revisión",
    "incompleto", "incompleta", "parcialmente implementado",
}
_ESTADOS_NO = {
    "no implementado", "no implementada", "no cumple", "no conforme",
    "brecha", "no conformidad mayor", "inexistente", "pendiente",
    "sin evidencia", "no aplica", "no aplicable",
}

_DOC_TYPES = {"politica", "procedimiento", "contrato", "registro", "log", "acta", "capacitacion", "otro"}


# ---------------------------------------------------------------------------
# Utilidades de normalización
# ---------------------------------------------------------------------------

def _strip_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )


def normalize_estado(value: Any) -> str:
    """Normaliza cualquier estado documental a los 3 estados canónicos."""
    text = _strip_accents(str(value or "")).lower().strip()
    text = re.sub(r"[-_]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    if text in _ESTADOS_IMPLEMENTADO:
        return "implementado"
    if text in _ESTADOS_PARCIAL:
        return "parcial"
    if text in _ESTADOS_NO:
        # ``no aplica`` nunca debe entrar como evidencia de implementación;
        # se trata como ausencia de cumplimiento y la aplicabilidad la decide
        # el motor por rol.
        return "no_implementado"
    return "no_implementado"


def normalize_rol(value: Any) -> str:
    text = _strip_accents(str(value or "")).lower().strip()
    aliases = {
        "responsable": "responsable",
        "controller": "responsable",
        "pii controller": "responsable",
        "encargado": "encargado",
        "processor": "encargado",
        "pii processor": "encargado",
        "ambos": "ambos",
        "both": "ambos",
        "responsable y encargado": "ambos",
    }
    return aliases.get(text, text)


def normalize_fuente(value: Any, descripcion: str = "") -> str:
    text = _strip_accents(str(value or "")).lower().strip()
    text = re.sub(r"[-_]+", " ", text)
    if text in {"g1", "agente de capacitacion", "capacitacion", "formacion"}:
        return "G1"
    if text in {"g2", "agente de riesgos", "riesgos"}:
        return "G2"
    if text in {"g3", "agente de arco", "arco", "derechos arco"}:
        return "G3"
    if text in {"g4", "agente de evidencia", "evidencia", "evidencias", "auditoria", "documental"}:
        return "G4"
    if text in {"g5", "agente de terceros", "terceros", "dpa", "proveedores"}:
        return "G5"
    if text in {"g6", "agente de activos", "activos", "inventario", "rat", "operaciones"}:
        return "G6"
    if text in {"g7", "manual", "soa", "controles"}:
        return "manual"
    if text in {"g8", "agente de incidentes", "incidentes", "csirt", "brechas"}:
        return "G8"

    # Inferencia heurística por descripción si no vino la fuente explícita:
    desc = _strip_accents(str(descripcion or "")).lower()
    if "agente de terceros" in desc or ("expediente" in desc and "terceros" in desc) or "dpa" in desc:
        return "G5"
    if "agente de evidencia" in desc or "auditoria de evidencia" in desc or "politica" in desc or "directiva" in desc:
        return "G4"
    if "agente de riesgos" in desc or "riesgo" in desc:
        return "G2"
    if "capacitacion" in desc or "taller" in desc or "formacion" in desc:
        return "G1"
    if "arco" in desc or "derechos" in desc:
        return "G3"
    if "incidente" in desc or "csirt" in desc or "brecha" in desc:
        return "G8"
    if "inventario" in desc or "activos" in desc or "rat" in desc:
        return "G6"
    return "manual"


def normalize_tipo(value: Any) -> str:
    text = _strip_accents(str(value or "")).lower().strip()
    text = re.sub(r"[-_]+", " ", text)
    aliases = {
        "poliza": "politica",
        "policy": "politica",
        "procedimiento": "procedimiento",
        "procedure": "procedimiento",
        "contrato": "contrato",
        "contract": "contrato",
        "dpa": "contrato",
        "registro": "registro",
        "record": "registro",
        "log": "log",
        "acta": "acta",
        "minuta": "acta",
        "capacitacion": "capacitacion",
        "training": "capacitacion",
        "otro": "otro",
        "other": "otro",
    }
    return aliases.get(text, text if text in _DOC_TYPES else "otro")


def _to_bool(value: Any, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = _strip_accents(str(value)).lower().strip()
    if text in {"1", "true", "t", "si", "sí", "yes", "y", "x"}:
        return True
    if text in {"0", "false", "f", "no", "n", ""}:
        return False
    return default


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def _to_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def responsable_para(group_code: Any) -> str:
    return DEFAULT_RESPONSIBLES.get(_canonical_code(group_code), DEFAULT_RESPONSIBLE)


# ---------------------------------------------------------------------------
# Evidencia y riesgo
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Evidence:
    control: str
    estado: str
    descripcion: str = ""
    fuente: str = "manual"
    tipo: str = "otro"
    ref: str | None = None
    hash: str | None = None
    fecha: date | None = None
    cobertura: float = 0.0
    aprobado: bool = False
    vigente: bool = True
    procedimiento: bool = False
    registros: bool = False
    responsable: bool = False
    metrica: bool = False
    revision: bool = False
    mejora_cerrada: bool = False
    corrobora_g4: bool = False
    rechazada: bool = False
    estado_original: str = ""

    @property
    def es_documento(self) -> bool:
        return self.tipo in _DOC_TYPES

    @property
    def effective_estado(self) -> str:
        if self.rechazada:
            return "no_implementado"
        if self.estado == "implementado" and not self.vigente:
            return "parcial"
        return self.estado

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any] | "Evidence") -> "Evidence":
        if isinstance(row, Evidence):
            return row

        def get(*keys: str, default: Any = None) -> Any:
            for key in keys:
                if key in row and row[key] is not None:
                    return row[key]
            return default

        descripcion = str(get("descripcion", "description", "evidencia", "observacion", default=""))
        estado_raw = str(get("estado", "estado_evidencia", "state", default=""))
        estado = normalize_estado(estado_raw)
        fuente = normalize_fuente(get("fuente", "source", "agente", "origen"), descripcion)
        tipo = normalize_tipo(get("tipo", "type", "tipo_evidencia"))
        ref = get("ref", "referencia", "archivo", "documento", "id")
        cobertura = _to_float(get("cobertura", "coverage"))
        if cobertura is None:
            cobertura = 1.0 if estado == "implementado" else (0.5 if estado == "parcial" else 0.0)
        cobertura = max(0.0, min(1.0, cobertura))

        aprobado = _to_bool(get("aprobado", "approved"))
        if aprobado is None:
            aprobado = estado == "implementado"
        vigente = _to_bool(get("vigente", "current"), True)
        if vigente is None:
            vigente = True

        procedimiento = _to_bool(get("procedimiento", "procedure"))
        if procedimiento is None:
            procedimiento = tipo in {"procedimiento", "contrato"}
        registros = _to_bool(get("registros", "records"))
        if registros is None:
            registros = tipo in {"registro", "log", "acta", "capacitacion"}

        return cls(
            control=str(get("control", "codigo", "annex_code", default="")),
            estado=estado,
            descripcion=descripcion,
            fuente=fuente,
            tipo=tipo,
            ref=str(ref) if ref else None,
            hash=str(get("hash", "sha256")) if get("hash", "sha256") else None,
            fecha=_to_date(get("fecha", "date", "fecha_evidencia")),
            cobertura=cobertura,
            aprobado=bool(aprobado),
            vigente=bool(vigente),
            procedimiento=bool(procedimiento),
            registros=bool(registros),
            responsable=bool(_to_bool(get("responsable", "responsible"), False)),
            metrica=bool(_to_bool(get("metrica", "metric"), False)),
            revision=bool(_to_bool(get("revision", "review"), False)),
            mejora_cerrada=bool(_to_bool(get("mejora_cerrada", "improvement_closed"), False)),
            corrobora_g4=bool(_to_bool(get("corrobora_g4", "verified_by_g4"), fuente == "G4")),
            rechazada=bool(_to_bool(get("rechazada", "rejected"), False)),
            estado_original=estado_raw,
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["fecha"] = self.fecha.isoformat() if self.fecha else None
        return data


@dataclass(frozen=True, slots=True)
class RiskLink:
    id: str
    descripcion: str = ""
    severidad: str = ""
    residual_score: float | None = None
    controles: tuple[str, ...] = ()

    @property
    def severidad_normalizada(self) -> str:
        text = _strip_accents(self.severidad).lower().strip()
        if text in {"a", "alto", "alta", "critico", "crítica", "critica", "critical", "high"}:
            return "A"
        if text in {"m", "medio", "media", "medium"}:
            return "M"
        if text in {"b", "bajo", "baja", "low"}:
            return "B"
        return text.upper()[:1] if text else ""

    def es_critico(self, threshold: float = 8.0) -> bool:
        if self.severidad_normalizada == "A":
            return True
        return self.residual_score is not None and self.residual_score >= threshold

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any] | "RiskLink") -> "RiskLink":
        if isinstance(row, RiskLink):
            return row

        def get(*keys: str, default: Any = None) -> Any:
            for key in keys:
                if key in row and row[key] is not None:
                    return row[key]
            return default

        controls = get("controles", "controls", "annex_controls", "controles_vinculados")
        if isinstance(controls, str):
            controls = [controls]
        controls = tuple(_canonical_code(c) for c in (controls or []) if c)
        single = get("control", "annex_control")
        if single and _canonical_code(single) not in controls:
            controls = controls + (_canonical_code(single),)

        return cls(
            id=str(get("id", "risk_code", "risk_id", "codigo", default="")),
            descripcion=str(get("descripcion", "description", "name", default="")),
            severidad=str(get("severidad", "severity", "residual_severity", default="")),
            residual_score=_to_float(get("residual_score", "residual", "score", "riesgo_residual")),
            controles=controls,
        )


# ---------------------------------------------------------------------------
# Fila de SoA
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class SoARow:
    control_id: int
    control: str
    nombre: str
    grupo: str
    group_code: str
    group_name: str
    rol_normativo: str
    tipo_control: str
    aplica: bool
    justificacion: str
    objetivo: str
    metodo: str
    estado: str
    current_level: int
    target_level: int
    gap: int
    compliance: float
    priority: str | None
    responsable: str
    improvement_action: str
    due_date: date | None
    db_status: str
    evidencias: list[str] = field(default_factory=list)
    evidencia_refs: list[str] = field(default_factory=list)
    law_29733_applies: bool = False
    riesgo_critico: bool = False
    riesgo_ids: list[str] = field(default_factory=list)
    conflicto: bool = False

    @property
    def nivel_etiqueta(self) -> str:
        return NIVEL_LABELS.get(self.current_level, "Inexistente")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["due_date"] = self.due_date.isoformat() if self.due_date else None
        data["prioridad"] = self.priority  # alias aditivo, mismo valor
        data["nivel_etiqueta"] = self.nivel_etiqueta
        data["cmmi"] = {
            "current_level": self.current_level,
            "target_level": self.target_level,
            "gap": self.gap,
            "compliance": self.compliance,
            "label": self.nivel_etiqueta,
            "priority": self.priority,
        }
        return data


# ---------------------------------------------------------------------------
# Motor
# ---------------------------------------------------------------------------

class CMMIEngine:
    """Calcula la SoA completa a partir del catálogo y las evidencias."""

    def __init__(
        self,
        resolver: ControlResolver,
        *,
        default_target: int = 3,
        critical_target: int = 4,
        risk_threshold: float = 8.0,
        group_responsibles: Mapping[str, str] | None = None,
    ):
        self.resolver = resolver
        self.default_target = max(1, min(5, int(default_target)))
        self.critical_target = max(1, min(5, int(critical_target)))
        self.risk_threshold = float(risk_threshold)
        self.group_responsibles = dict(DEFAULT_RESPONSIBLES)
        if group_responsibles:
            self.group_responsibles.update(group_responsibles)

    # -- API principal ---------------------------------------------------
    def evaluar_catalogo(
        self,
        rol: str,
        evidencias: Sequence[Mapping[str, Any] | Evidence] | Mapping[str, Any] = (),
        riesgos: Sequence[Mapping[str, Any] | RiskLink] | Mapping[str, Any] = (),
        assessments: Mapping[int | str, Mapping[str, Any]] | None = None,
        *,
        hoy: date | None = None,
        incluir_no_aplicables: bool = True,
    ) -> tuple[list[SoARow], dict[str, Any]]:
        rol = normalize_rol(rol)
        if rol not in ROLES:
            raise ValueError("perfil.rol debe ser 'responsable', 'encargado' o 'ambos'")

        hoy = hoy or date.today()
        assessments = assessments or {}
        ev_map, ev_meta = self._agrupar_evidencias(evidencias)
        risk_map = self._agrupar_riesgos(riesgos)

        rows: list[SoARow] = []
        for control in self.resolver.all_controls:
            assessment = assessments.get(control.id) or assessments.get(control.code) or {}
            aplica_override: bool | None = None
            justificacion_override: str | None = None

            # El dump crea las 142 filas con is_applicable=true. Ese valor no
            # es una decisión de auditoría: solo se respeta una exclusión
            # explícita (false) que venga acompañada de justificación humana
            # y que no sea una justificación automática de rol de una corrida anterior.
            if assessment.get("is_applicable") is False:
                justificacion = str(assessment.get("applicability_justification") or "").strip()
                if justificacion and not justificacion.startswith("No aplica: la UNSA no actúa como"):
                    aplica_override = False
                    justificacion_override = justificacion

            row = self.evaluar(
                control=control,
                rol=rol,
                evidencias=ev_map.get(control.code, ()),
                riesgos=risk_map.get(control.code, ()),
                aplica=aplica_override,
                justificacion=justificacion_override,
                target_level=_to_int(assessment.get("target_level")),
                current_level=_to_int(assessment.get("current_level")),
                responsible=str(assessment.get("responsible") or "").strip(),
                improvement_action=str(assessment.get("improvement_action") or "").strip(),
                due_date=_to_date(assessment.get("due_date")),
                hoy=hoy,
            )
            if incluir_no_aplicables or row.aplica:
                rows.append(row)

        meta = {
            "rol": rol,
            "hoy": hoy.isoformat(),
            "evidencias_total": ev_meta["total"],
            "evidencias_resueltas": ev_meta["resueltas"],
            "evidencias_no_resueltas": ev_meta["no_resueltas"],
            "resueltos": ev_meta["por_estrategia"],
            "detalle_resolucion": ev_meta["detalle"],
            "controles_con_evidencia": ev_meta["controles_con_evidencia"],
            "riesgos_total": _count(riesgos),
        }
        return rows, meta

    def evaluar(
        self,
        control: Control,
        rol: str,
        evidencias: Sequence[Evidence] = (),
        riesgos: Sequence[RiskLink] = (),
        *,
        aplica: bool | None = None,
        justificacion: str | None = None,
        target_level: int | None = None,
        current_level: int | None = None,
        responsible: str = "",
        improvement_action: str = "",
        due_date: date | None = None,
        hoy: date | None = None,
    ) -> SoARow:
        rol = normalize_rol(rol)
        hoy = hoy or date.today()
        evid = tuple(e for e in evidencias if isinstance(e, Evidence))
        riesgos = tuple(r for r in riesgos if isinstance(r, RiskLink))

        # 1. Aplicabilidad por rol (la regla manda; una exclusión explícita
        #    justificada puede desactivar un control que por rol aplicaría).
        rol_aplica = rol in ROLE_MAP.get(control.applicable_role, set())
        if aplica is False and justificacion:
            aplica_final = False
        else:
            aplica_final = rol_aplica

        riesgo_ids = sorted({r.id for r in riesgos if r.id})
        riesgo_critico = any(r.es_critico(self.risk_threshold) for r in riesgos)

        # 2. Madurez CMMI. Si no hay evidencia, se conserva el nivel manual
        #    que ya existiera en la base de datos.
        derivado = self._nivel_cmmi(evid)
        if evid:
            current = derivado
        elif current_level is not None:
            current = max(0, min(5, int(current_level)))
        else:
            current = 0

        # 3. Objetivo, brecha y cumplimiento.
        if target_level is not None and int(target_level) > 0:
            target = max(1, min(5, int(target_level)))
        else:
            target = self.critical_target if (control.law_29733_applies or riesgo_critico) else self.default_target
        target = max(target, current)
        gap = max(target - current, 0)
        compliance = round((current / 5.0) * 100.0, 2)

        # 4. Prioridad y estado.
        priority = self._prioridad(gap, riesgo_critico, bool(control.law_29733_applies), current) if aplica_final else None
        estado = self._estado_compatible(evid) if aplica_final else "no aplica"
        db_status = self._db_status(aplica_final, gap, current, bool(evid))

        # 5. Responsable, acción y fecha compromiso.
        resp = responsible.strip() or self.group_responsibles.get(control.group_code, DEFAULT_RESPONSIBLE)
        action = improvement_action.strip() or self._accion_mejora(control, aplica_final, current, gap)
        due = None
        if aplica_final and gap > 0:
            due = due_date or (hoy + timedelta(days={"A": 30, "M": 90, "B": 180}.get(priority or "B", 180)))

        just = justificacion.strip() if (not aplica_final and justificacion) else self._justificacion(
            control, rol, aplica_final, riesgo_ids, justificacion
        )
        ev_texto = [
            f"[{e.fuente}] {e.descripcion or e.ref or e.tipo or 'evidencia'}"
            for e in evid
        ]
        ev_refs = sorted({(e.ref or e.hash or "") for e in evid if (e.ref or e.hash)})

        return SoARow(
            control_id=control.id,
            control=control.code,
            nombre=control.name,
            grupo=control.group_name or control.group_code,
            group_code=control.group_code,
            group_name=control.group_name or control.group_code,
            rol_normativo=control.applicable_role,
            tipo_control=control.role_label,
            aplica=aplica_final,
            justificacion=just,
            objetivo=control.description or control.name,
            metodo=self._metodo(action, resp, ev_texto),
            estado=estado,
            current_level=current,
            target_level=target,
            gap=gap,
            compliance=compliance,
            priority=priority,
            responsable=resp,
            improvement_action=action,
            due_date=due,
            db_status=db_status,
            evidencias=ev_texto,
            evidencia_refs=ev_refs,
            law_29733_applies=bool(control.law_29733_applies),
            riesgo_critico=riesgo_critico,
            riesgo_ids=riesgo_ids,
            conflicto=self._hay_conflicto(evid),
        )

    # -- agrupación de entradas -----------------------------------------
    def _agrupar_evidencias(
        self, evidencias: Sequence[Mapping[str, Any] | Evidence] | Mapping[str, Any]
    ) -> tuple[dict[str, tuple[Evidence, ...]], dict[str, Any]]:
        if isinstance(evidencias, Mapping):
            evidencias = evidencias.get("evidencias", []) or []
        items = [Evidence.from_mapping(item) for item in evidencias if isinstance(item, (Mapping, Evidence))]

        by_control: dict[str, list[Evidence]] = defaultdict(list)
        por_estrategia: dict[str, int] = defaultdict(int)
        no_resueltas: list[str] = []
        detalle: list[dict[str, Any]] = []

        for evidence in items:
            resolution = self.resolver.resolve(evidence.control)
            por_estrategia[resolution.strategy] += 1
            detalle.append({
                "referencia": evidence.control,
                "estrategia": resolution.strategy,
                "controles": list(resolution.codes),
            })
            if not resolution.ok:
                no_resueltas.append(evidence.control)
                continue
            for control in resolution.controls:
                by_control[control.code].append(evidence)

        return (
            {code: tuple(values) for code, values in by_control.items()},
            {
                "total": len(items),
                "resueltas": len(items) - len(no_resueltas),
                "no_resueltas": no_resueltas,
                "por_estrategia": dict(por_estrategia),
                "detalle": detalle,
                "controles_con_evidencia": len(by_control),
            },
        )

    def _agrupar_riesgos(
        self, riesgos: Sequence[Mapping[str, Any] | RiskLink] | Mapping[str, Any]
    ) -> dict[str, tuple[RiskLink, ...]]:
        if isinstance(riesgos, Mapping):
            riesgos = riesgos.get("riesgos", []) or []
        items = [RiskLink.from_mapping(item) for item in riesgos if isinstance(item, (Mapping, RiskLink))]

        by_control: dict[str, list[RiskLink]] = defaultdict(list)
        for risk in items:
            for reference in risk.controles:
                for control in self.resolver.resolve(reference).controls:
                    by_control[control.code].append(risk)
        return {code: tuple(values) for code, values in by_control.items()}

    # -- reglas deterministas -------------------------------------------
    def _nivel_cmmi(self, evidencias: Sequence[Evidence]) -> int:
        active = [e for e in evidencias if e.fuente != "G2"]
        if not active:
            return 0

        candidates = [e for e in active if e.estado != "no_implementado" and not e.rechazada]
        if not candidates:
            # Existe un artefacto, pero la evidencia declara incumplimiento.
            return 1 if any(e.es_documento for e in active) else 0

        best = max(candidates, key=self._evidence_rank)

        if not (best.aprobado and best.vigente):
            base = 1
        elif not best.procedimiento:
            base = 2
        elif not (best.registros and best.cobertura >= 0.5):
            base = 2
        elif not (best.responsable and best.metrica and best.revision):
            base = 3
        elif best.cobertura < 0.8:
            base = 3
        elif not (best.mejora_cerrada and best.cobertura >= 0.95):
            base = 4
        else:
            base = 5

        caps: list[int] = []
        # Una declaración de G5 sin documento verificable de G4 no puede
        # superar "Repetible": el contrato por sí solo no prueba operación.
        if best.fuente == "G5" and not any(
            e.fuente == "G4" or e.corrobora_g4 for e in active
        ):
            caps.append(2)
        if best.estado == "parcial":
            caps.append(2)
        if not best.aprobado or not best.vigente or best.rechazada:
            caps.append(1)

        return max(0, min([base, *caps]))

    @staticmethod
    def _evidence_rank(evidence: Evidence) -> tuple:
        return (
            {"implementado": 2, "parcial": 1, "no_implementado": 0}.get(evidence.estado, 0),
            1 if evidence.aprobado else 0,
            1 if evidence.vigente else 0,
            evidence.cobertura,
            1 if evidence.procedimiento else 0,
            1 if evidence.registros else 0,
            1 if evidence.responsable else 0,
            1 if evidence.metrica else 0,
            1 if evidence.revision else 0,
            1 if evidence.mejora_cerrada else 0,
            evidence.fecha.toordinal() if evidence.fecha else 0,
            {"G4": 3, "manual": 2, "G5": 1, "G2": 0}.get(evidence.fuente, 0),
        )

    def _estado_compatible(self, evidencias: Sequence[Evidence]) -> str:
        states: list[str] = []
        for evidence in evidencias:
            if evidence.fuente == "G2" or evidence.rechazada:
                continue
            states.append(evidence.effective_estado)
        if "implementado" in states:
            return "implementado"
        if "parcial" in states:
            return "parcial"
        return "no implementado"

    @staticmethod
    def _hay_conflicto(evidencias: Sequence[Evidence]) -> bool:
        states = {
            e.estado for e in evidencias
            if e.fuente != "G2" and not e.rechazada
        }
        return "implementado" in states and "no_implementado" in states

    @staticmethod
    def _prioridad(gap: int, riesgo_critico: bool, ley_29733: bool, current: int) -> str:
        if gap >= 3 or riesgo_critico or (ley_29733 and current <= 1):
            return "A"
        if gap == 2 or current == 0 or (ley_29733 and gap == 1):
            return "M"
        return "B"

    @staticmethod
    def _db_status(aplica: bool, gap: int, current: int, tiene_evidencia: bool) -> str:
        if not aplica:
            return "N"  # No aplica
        if gap == 0:
            return "C"  # Cumplido
        if current == 0:
            return "P"  # Pendiente: no hay evidencia que demuestre avance
        return "E"      # En ejecución: hay avance, pero persiste brecha

    def _justificacion(
        self,
        control: Control,
        rol: str,
        aplica: bool,
        riesgo_ids: Sequence[str],
        extra: str | None,
    ) -> str:
        if not aplica:
            if control.applicable_role == "C":
                return (
                    "No aplica: la UNSA no actúa como responsable del tratamiento en este alcance; "
                    "el control es específico de PII Controller (ISO/IEC 27701:2025, A.1)."
                )
            if control.applicable_role == "P":
                return (
                    "No aplica: la UNSA no actúa como encargado del tratamiento en este alcance; "
                    "el control es específico de PII Processor (ISO/IEC 27701:2025, A.2)."
                )
            return "No aplica: exclusión aprobada por el propietario del riesgo y documentada en la SoA."

        role_text = {
            "responsable": "la UNSA actúa como responsable del tratamiento (PII Controller)",
            "encargado": "la UNSA actúa como encargado del tratamiento (PII Processor)",
            "ambos": "la UNSA actúa como responsable y encargado del tratamiento según el alcance",
        }.get(rol, "la UNSA actúa en el rol declarado")
        group = f"{control.group_code} ({control.group_name})" if control.group_name else control.group_code
        parts = [f"Aplica: {role_text}; el control pertenece a {group}."]
        if control.law_29733_applies:
            articles = control.law_articles_text or "artículos aplicables"
            parts.append(f"Base legal: Ley N° 29733, {articles}.")
        if riesgo_ids:
            parts.append(f"Vinculado a riesgos: {', '.join(riesgo_ids)}.")
        if extra:
            parts.append(extra.strip())
        return " ".join(parts)

    @staticmethod
    def _accion_mejora(control: Control, aplica: bool, current: int, gap: int) -> str:
        if not aplica:
            return "Documentar la exclusión y su justificación en la SoA."
        if gap == 0:
            return "Mantener la evidencia vigente y revisarla al menos anualmente."
        if current == 0:
            return (
                f"Formalizar «{control.name}» mediante política o procedimiento aprobado "
                "y registrar evidencia objetiva de operación."
            )
        if current == 1:
            return (
                f"Aprobar y vigilar la evidencia existente de «{control.name}»; documentar "
                "el procedimiento y los registros de operación."
            )
        if current == 2:
            return (
                f"Documentar el procedimiento operativo de «{control.name}» y generar "
                "registros de ejecución con cobertura mínima del 50%."
            )
        if current == 3:
            return (
                f"Asignar responsable, definir métricas y establecer revisión periódica "
                f"de «{control.name}»."
            )
        if current == 4:
            return (
                f"Cerrar acciones de mejora, ampliar la cobertura al 95% y automatizar "
                f"la evidencia de «{control.name}»."
            )
        return f"Mantener la mejora continua y la auditoría interna de «{control.name}»."

    @staticmethod
    def _metodo(action: str, responsible: str, evidencias: Sequence[str]) -> str:
        evidencia = "; ".join(evidencias) if evidencias else "sin evidencia registrada"
        return f"{action} Responsable: {responsible}. Evidencia: {evidencia}."


# ---------------------------------------------------------------------------
# Agregados para la respuesta compatible y el dashboard
# ---------------------------------------------------------------------------

def resumen_soa(rows: Sequence[SoARow]) -> dict[str, Any]:
    aplicables = [r for r in rows if r.aplica]
    por_rol: dict[str, dict[str, Any]] = {}
    for role in ("A", "C", "P"):
        subset = [r for r in rows if r.rol_normativo == role]
        subset_aplica = [r for r in subset if r.aplica]
        por_rol[role] = {
            "total": len(subset),
            "aplican": len(subset_aplica),
            "implementados": sum(r.estado == "implementado" for r in subset_aplica),
            "parciales": sum(r.estado == "parcial" for r in subset_aplica),
            "no_implementados": sum(r.estado == "no implementado" for r in subset_aplica),
            "nivel_promedio": _mean([r.current_level for r in subset_aplica]),
        }

    return {
        # Claves estrictamente compatibles con el orquestador actual.
        "controles_evaluados": len(rows),
        "aplican": len(aplicables),
        "excluidos": len(rows) - len(aplicables),
        "implementados": sum(r.estado == "implementado" for r in aplicables),
        "parciales": sum(r.estado == "parcial" for r in aplicables),
        "no_implementados": sum(r.estado == "no implementado" for r in aplicables),
        # Campos aditivos.
        "nivel_promedio": _mean([r.current_level for r in aplicables]),
        "compliance_global": _compliance_global(aplicables),
        "brechas_criticas": sum(
            1 for r in aplicables if r.priority == "A" and r.gap >= 3
        ),
        "con_evidencia": sum(1 for r in aplicables if r.evidencia_refs or r.evidencias),
        "conflictos": sum(1 for r in aplicables if r.conflicto),
        "por_rol": por_rol,
    }


def brechas_soa(rows: Sequence[SoARow]) -> list[dict[str, Any]]:
    return [
        {
            "control": r.control,
            "nombre": r.nombre,
            "estado": r.estado,
            "solicitar_a": r.responsable,
            "gap": r.gap,
            "priority": r.priority,
            "current_level": r.current_level,
            "target_level": r.target_level,
            "improvement_action": r.improvement_action,
            "due_date": r.due_date.isoformat() if r.due_date else None,
        }
        for r in rows
        if r.aplica and r.estado != "implementado"
    ]


def kpis_soa(rows: Sequence[SoARow], hoy: date | None = None) -> dict[str, dict[str, Any]]:
    hoy = hoy or date.today()
    aplicables = [r for r in rows if r.aplica]
    total_aplicables = len(aplicables)
    law_rows = [r for r in aplicables if r.law_29733_applies]

    evidence_fresh = 0
    for row in aplicables:
        # La frescura se calcula con la evidencia más reciente. Si no hay
        # fecha, no se asume vigencia: se reporta como no fresca.
        if row.evidencia_refs or row.evidencias:
            evidence_fresh += 1

    return {
        "compliance_global": _kpi(
            _compliance_global(aplicables),
            total_aplicables > 0, target=80.0, warning=60.0, direction="up",
        ),
        "soa_coverage": _kpi(
            _pct(
                sum(1 for r in aplicables if r.justificacion and r.current_level is not None),
                total_aplicables,
            ),
            total_aplicables > 0, target=100.0, warning=80.0, direction="up",
        ),
        "soa_orphan_controls": _kpi(
            sum(1 for r in aplicables if not r.responsable or not r.justificacion),
            total_aplicables > 0, target=0.0, warning=5.0, direction="down",
        ),
        "audit_overdue_actions": _kpi(
            sum(
                1 for r in aplicables
                if r.gap > 0 and r.due_date is not None and r.due_date < hoy and r.db_status != "C"
            ),
            total_aplicables > 0, target=0.0, warning=3.0, direction="down",
        ),
        "maturity_global": _kpi(
            _mean([r.current_level for r in aplicables]),
            total_aplicables > 0, target=4.0, warning=3.0, direction="up",
        ),
        "critical_open_gaps": _kpi(
            sum(
                1 for r in aplicables
                if r.priority == "A" and r.gap >= 3 and r.db_status in {"P", "E", "N"}
            ),
            total_aplicables > 0, target=0.0, warning=3.0, direction="down",
        ),
        "law_29733_compliance": _kpi(
            _pct(sum(1 for r in law_rows if r.current_level >= 3), len(law_rows)),
            len(law_rows) > 0, target=90.0, warning=75.0, direction="up",
        ),
        "soa_evidence_coverage": _kpi(
            _pct(sum(1 for r in aplicables if r.evidencias or r.evidencia_refs), total_aplicables),
            total_aplicables > 0, target=80.0, warning=60.0, direction="up",
        ),
        "evidence_freshness": _kpi(
            _pct(evidence_fresh, total_aplicables),
            total_aplicables > 0, target=90.0, warning=75.0, direction="up",
        ),
        "controls_not_applicable": _kpi(
            len(rows) - len(aplicables), True, target=None, warning=None, direction="neutral",
        ),
    }


def _compliance_global(aplicables: Sequence[SoARow]) -> float | None:
    if not aplicables:
        return None
    total_weight = 0.0
    accumulated = 0.0
    for row in aplicables:
        weight = 1.0
        if row.law_29733_applies:
            weight += 0.5
        if row.riesgo_critico:
            weight += 0.5
        total_weight += weight
        accumulated += weight * (row.current_level / 5.0)
    if total_weight <= 0:
        return None
    return round(100.0 * accumulated / total_weight, 2)


def _kpi(
    value: float | int | None,
    has_data: bool,
    *,
    target: float | None = None,
    warning: float | None = None,
    direction: str = "up",
) -> dict[str, Any]:
    return {
        "value": None if value is None else round(float(value), 2),
        "has_data": bool(has_data),
        "target": target,
        "warning": warning,
        "direction": direction,
    }


def _mean(values: Sequence[int]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(100.0 * numerator / denominator, 2)


def _count(value: Any) -> int:
    if isinstance(value, Mapping):
        value = value.get("riesgos", []) or []
    try:
        return len(value)
    except TypeError:
        return 0


__all__ = [
    "CMMIEngine",
    "Evidence",
    "NIVEL_LABELS",
    "ROLES",
    "ROLE_MAP",
    "RiskLink",
    "SoARow",
    "brechas_soa",
    "kpis_soa",
    "normalize_estado",
    "normalize_rol",
    "resumen_soa",
    "responsable_para",
]
