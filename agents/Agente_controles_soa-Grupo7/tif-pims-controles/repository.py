"""Persistencia de la Declaración de Aplicabilidad (SoA) del Agente G7.

El módulo ofrece una interfaz única (``SoARepository``) con tres
implementaciones:

* ``PostgresSoA``: lee ``demo.core_annexacontrol`` y hace UPSERT en
  ``demo.core_gapannexaassessment`` y ``demo.core_dashboardsnapshot``.
* ``LocalSoA``: fallback indestructible basado en ``catalogo_142.json`` y un
  pequeño estado JSON local. Nunca lanza excepciones por falta de PostgreSQL.
* ``HybridSoA``: intenta PostgreSQL y, ante cualquier fallo de conexión o de
  escritura, degrada silenciosamente a ``LocalSoA`` sin propagar el error.

La conexión a PostgreSQL es perezosa: ``psycopg`` solo se importa cuando se
usa realmente. Así el agente puede arrancar y responder en entornos sin
driver o sin base de datos, tal como exige el modo ``auto``.
"""

from __future__ import annotations

import json
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = BASE_DIR / "knowledge" / "catalogo_142.json"
DEFAULT_STATE = BASE_DIR / "runtime" / "soa_estado_local.json"

VALID_DATA_SOURCES = {"auto", "postgres", "postgresql", "db", "local", "memoria", "memory"}

# ---------------------------------------------------------------------------
# Riesgos y evidencias institucionales de línea base (UNSA)
# Utilizados como fallback robusto cuando las tablas de G2/G4/G5/G6/G8 aún
# no contienen registros o en modo de ejecución desconectado.
# ---------------------------------------------------------------------------

BASELINE_UNSA_RISKS: list[dict[str, Any]] = [
    {
        "id": "RSK-UNSA-01",
        "risk_code": "RSK-UNSA-01",
        "activo": "Sistema Integrado SISUNSA (Servidor de Notas y Matrícula)",
        "propietario": "Dirección Universitaria de Tecnologías de la Información (DUTIC)",
        "amenaza": "Inyección SQL / Fuga de credenciales de acceso docente",
        "vulnerabilidad": "Ausencia de autenticación multifactor (MFA) en accesos privilegiados",
        "descripcion": "Acceso no autorizado y alteración de calificaciones académicas y datos de filiación estudiantil.",
        "nueva_consecuencia": 3,
        "nueva_probabilidad": 1,
        "riesgo_residual": 3.0,
        "residual_score": 3.0,
        "severidad": "A",
        "controles": ["A.5.15", "A.5.16", "A.8.2", "A.8.24"],
        "origen": "UNSA-Baseline",
    },
    {
        "id": "RSK-UNSA-02",
        "risk_code": "RSK-UNSA-02",
        "activo": "Sistema Biométrico del Comedor Universitario",
        "propietario": "Dirección de Bienestar Universitario",
        "amenaza": "Divulgación no autorizada de plantillas biométricas dactilares",
        "vulnerabilidad": "Almacenamiento de minucias dactilares en texto plano sin cifrado en reposo",
        "descripcion": "Filtración de datos biométricos sensibles de estudiantes comensales y beneficiarios.",
        "nueva_consecuencia": 2,
        "nueva_probabilidad": 1,
        "riesgo_residual": 2.0,
        "residual_score": 2.0,
        "severidad": "B",
        "controles": ["A.5.33", "A.8.24", "A.1.2.1"],
        "origen": "UNSA-Baseline",
    },
    {
        "id": "RSK-UNSA-03",
        "risk_code": "RSK-UNSA-03",
        "activo": "Portal Web de Admisión y Procesamiento de Postulantes",
        "propietario": "Dirección Universitaria de Admisión",
        "amenaza": "Denegación de servicio distribuido (DDoS) / Manipulación de vacantes",
        "vulnerabilidad": "Falta de limitación de tasa (rate limiting) y balanceo elástico de carga",
        "descripcion": "Indisponibilidad del portal de inscripción y riesgo de fuga de datos personales de menores postulantes.",
        "nueva_consecuencia": 4,
        "nueva_probabilidad": 1,
        "riesgo_residual": 4.0,
        "residual_score": 4.0,
        "severidad": "A",
        "controles": ["A.8.6", "A.8.20", "A.8.21"],
        "origen": "UNSA-Baseline",
    },
    {
        "id": "RSK-UNSA-04",
        "risk_code": "RSK-UNSA-04",
        "activo": "Servicio de Correo Institucional (Google Workspace UNSA)",
        "propietario": "DUTIC / CISO Institucional",
        "amenaza": "Suplantación de identidad (Phishing / BEC) a autoridades universitarias",
        "vulnerabilidad": "Configuración incompleta de registros SPF, DKIM y política DMARC",
        "descripcion": "Envío de correos fraudulentos en nombre del Rectorado solicitando transferencias o datos reservados.",
        "nueva_consecuencia": 3,
        "nueva_probabilidad": 0.5,
        "riesgo_residual": 1.5,
        "residual_score": 1.5,
        "severidad": "B",
        "controles": ["A.5.19", "A.5.20", "A.8.23"],
        "origen": "UNSA-Baseline",
    },
    {
        "id": "RSK-UNSA-05",
        "risk_code": "RSK-UNSA-05",
        "activo": "Repositorio Institucional de Tesis e Investigaciones de Posgrado",
        "propietario": "Vicerrectorado de Investigación",
        "amenaza": "Exfiltración de patentes no registradas y datos confidenciales de investigación",
        "vulnerabilidad": "Controles de acceso basados en roles (RBAC) desactualizados tras egreso de investigadores",
        "descripcion": "Acceso indebido a propiedad intelectual y datos sensibles de proyectos de investigación financiados.",
        "nueva_consecuencia": 2,
        "nueva_probabilidad": 1,
        "riesgo_residual": 2.0,
        "residual_score": 2.0,
        "severidad": "B",
        "controles": ["A.5.9", "A.5.12", "A.5.33"],
        "origen": "UNSA-Baseline",
    },
]

BASELINE_UNSA_EVIDENCE: list[dict[str, Any]] = [
    # G4 - Gestión Documental y Políticas
    {
        "control": "A.5.1",
        "descripcion": "Política General de Seguridad de la Información UNSA aprobada por Res. Consejo Universitario CU-2024-089",
        "estado": "implementado",
        "fuente": "G4",
        "tipo": "politica",
        "ref": "POL-UNSA-SEG-01",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.5.15",
        "descripcion": "Directiva de Control de Acceso y Gestión de Identidades en Sistemas Académicos y Administrativos",
        "estado": "parcial",
        "fuente": "G4",
        "tipo": "directiva",
        "ref": "DIR-UNSA-TI-03",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.8.13",
        "descripcion": "Procedimiento Operativo de Respaldos Diarios y Almacenamiento Seguro Off-site de Bases de Datos",
        "estado": "implementado",
        "fuente": "G4",
        "tipo": "procedimiento",
        "ref": "PRC-DUTIC-BCK-02",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.6.7",
        "descripcion": "Lineamientos de Teletrabajo y Seguridad en Dispositivos Personales (BYOD) para Docentes",
        "estado": "implementado",
        "fuente": "G4",
        "tipo": "lineamiento",
        "ref": "LIN-RRHH-TEL-01",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.5.33",
        "descripcion": "Política Institucional de Protección de Datos Personales en cumplimiento de la Ley 29733",
        "estado": "implementado",
        "fuente": "G4",
        "tipo": "politica",
        "ref": "POL-UNSA-DP-02",
        "aprobado": True,
        "vigente": True,
    },
    # G5 - Terceros y Acuerdos de Tratamiento de Datos (DPA)
    {
        "control": "A.5.19",
        "descripcion": "Acuerdo de Tratamiento de Datos (DPA) suscrito con Google LLC para Google Workspace for Education",
        "estado": "implementado",
        "fuente": "G5",
        "tipo": "contrato",
        "ref": "CTR-DPA-GOOGLE-2024",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.5.20",
        "descripcion": "Cláusulas de Privacidad, Seguridad y Confidencialidad en Contrato de Plataforma LMS Canvas (Instructure)",
        "estado": "implementado",
        "fuente": "G5",
        "tipo": "contrato",
        "ref": "CTR-DPA-CANVAS-2024",
        "aprobado": True,
        "vigente": True,
    },
    # G8 - Incidentes de Seguridad de la Información
    {
        "control": "A.5.24",
        "descripcion": "Bitácora CSIRT-UNSA: Procedimiento formal de notificación y escalamiento de incidentes cibernéticos",
        "estado": "implementado",
        "fuente": "G8",
        "tipo": "registro",
        "ref": "INC-PROC-CSIRT-01",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.5.26",
        "descripcion": "Registro y análisis post-incidente de campaña de suplantación phishing en portal docente",
        "estado": "parcial",
        "fuente": "G8",
        "tipo": "informe",
        "ref": "INC-REP-2025-001",
        "aprobado": False,
        "vigente": True,
    },
    # G1 - Capacitación y Concientización
    {
        "control": "A.6.3",
        "descripcion": "Acta y registro de asistencia al Programa de Capacitación en Ley 29733 y Seguridad Digital 2025",
        "estado": "implementado",
        "fuente": "G1",
        "tipo": "capacitacion",
        "ref": "CAP-UNSA-2025-01",
        "registros": True,
        "vigente": True,
    },
    # G3 - Derechos ARCO
    {
        "control": "A.1.2.6",
        "descripcion": "Mesa de Partes Digital y Procedimiento Administrativo de Atención de Solicitudes ARCO (TUPA-UNSA)",
        "estado": "implementado",
        "fuente": "G3",
        "tipo": "procedimiento",
        "ref": "PROC-ARCO-MESA-01",
        "aprobado": True,
        "vigente": True,
    },
    # G6 - Inventario de Activos y RAT
    {
        "control": "A.5.9",
        "descripcion": "Inventario Consolidado de Activos de Información y Bancos de Datos Personales Registrados ante la ANPD",
        "estado": "implementado",
        "fuente": "G6",
        "tipo": "registro",
        "ref": "INV-ACT-DATOS-2025",
        "registros": True,
        "vigente": True,
    },
    {
        "control": "A.5.12",
        "descripcion": "Esquema y Matriz de Clasificación de Información: Pública, Confidencial, Secreta y Datos Sensibles",
        "estado": "implementado",
        "fuente": "G6",
        "tipo": "directiva",
        "ref": "DIR-SEG-CLASF-02",
        "aprobado": True,
        "vigente": True,
    },
    {
        "control": "A.1.2.1",
        "descripcion": "Registro de Actividades de Tratamiento (RAT): Operaciones de matrícula, bienestar comedor y RRHH",
        "estado": "implementado",
        "fuente": "G6",
        "tipo": "registro",
        "ref": "RAT-UNSA-PIMS-01",
        "registros": True,
        "vigente": True,
    },
]


# ---------------------------------------------------------------------------
# Errores y utilidades
# ---------------------------------------------------------------------------

class RepositoryError(RuntimeError):
    """Error controlado de persistencia (siempre degradable)."""


def _row_get(row: Any, *keys: str, default: Any = None) -> Any:
    """Lee un valor de un ``SoARow``, dataclass o mapping sin acoplarse al tipo."""
    for key in keys:
        if isinstance(row, Mapping):
            if key in row and row[key] is not None:
                return row[key]
        else:
            value = getattr(row, key, None)
            if value is not None:
                return value
    return default


def _as_jsonable(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (tuple, list, set)):
        return [_as_jsonable(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _as_jsonable(v) for k, v in value.items()}
    return value


def _first_day_of_month(month: Any = None) -> date:
    if isinstance(month, datetime):
        return month.date().replace(day=1)
    if isinstance(month, date):
        return month.replace(day=1)
    if isinstance(month, str) and month.strip():
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m"):
            try:
                return datetime.strptime(month.strip()[:10], fmt).date().replace(day=1)
            except ValueError:
                continue
    today = date.today()
    return today.replace(day=1)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _evidence_text(row: Any) -> str:
    evidencias = _row_get(row, "evidencias", default=[])
    refs = _row_get(row, "evidencia_refs", default=[])
    parts: list[str] = []
    if isinstance(evidencias, (list, tuple)):
        parts.extend(str(item) for item in evidencias if item)
    if isinstance(refs, (list, tuple)):
        parts.extend(str(item) for item in refs if item)
    text = "; ".join(dict.fromkeys(parts))
    return text[:8000]


def _status_for_row(row: Any) -> str:
    explicit = _row_get(row, "db_status")
    if explicit:
        return str(explicit)[:1].upper()
    if not bool(_row_get(row, "aplica", default=True)):
        return "N"
    gap = int(_row_get(row, "gap", default=0) or 0)
    current = int(_row_get(row, "current_level", default=0) or 0)
    if gap == 0:
        return "C"
    return "E" if current > 0 else "P"


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------

class SoARepository(ABC):
    """Contrato mínimo que el servicio G7 necesita de una fuente de datos."""

    name: str = "abstract"
    degraded: bool = False
    last_error: str | None = None

    # -- lectura ---------------------------------------------------------
    @abstractmethod
    def load_catalog(self) -> list[dict[str, Any]]:
        """Devuelve las filas de ``core_annexacontrol`` (142 controles)."""

    @abstractmethod
    def load_assessments(self) -> dict[Any, dict[str, Any]]:
        """Devuelve evaluaciones indexadas por ``annex_a_control_id`` y código."""

    @abstractmethod
    def load_risks(self) -> list[dict[str, Any]]:
        """Devuelve los riesgos residuales desde PostgreSQL o fallback institucional."""

    @abstractmethod
    def load_evidence_from_db(self) -> list[dict[str, Any]]:
        """Devuelve evidencias multidisciplinarias desde las tablas del ecosistema (G1..G8)."""

    # -- escritura -------------------------------------------------------
    @abstractmethod
    def save_assessments(self, rows: Sequence[Any]) -> dict[str, Any]:
        """UPSERT de las filas de SoA. Devuelve métricas de la operación."""

    @abstractmethod
    def save_kpis(self, kpis: Mapping[str, Any], month: Any = None) -> dict[str, Any]:
        """UPSERT de los KPI mensuales del dashboard."""

    # -- estado ----------------------------------------------------------
    def status(self) -> dict[str, Any]:
        return {
            "fuente": self.name,
            "degradado": bool(self.degraded),
            "ultimo_error": self.last_error,
        }

    def close(self) -> None:  # pragma: no cover - interfaz
        return None


# ---------------------------------------------------------------------------
# Implementación local (fallback)
# ---------------------------------------------------------------------------

class LocalSoA(SoARepository):
    """Fallback indestructible basado en el catálogo JSON empaquetado."""

    name = "local"

    def __init__(
        self,
        catalog_path: str | os.PathLike[str] | None = None,
        state_path: str | os.PathLike[str] | None = None,
    ):
        self.catalog_path = Path(catalog_path or os.getenv("G7_LOCAL_CATALOG") or DEFAULT_CATALOG)
        self.state_path = Path(state_path or os.getenv("G7_LOCAL_STATE") or DEFAULT_STATE)
        self._catalog: list[dict[str, Any]] | None = None
        self._state: dict[str, Any] = {"assessments": {}, "kpis": {}, "updated_at": None}
        self._load_state()

    # -- estado local ----------------------------------------------------
    def _load_state(self) -> None:
        try:
            if self.state_path.is_file():
                data = json.loads(self.state_path.read_text("utf-8"))
                if isinstance(data, dict):
                    self._state.update(data)
        except Exception as exc:  # noqa: BLE001 - el fallback nunca debe caer
            self.last_error = f"estado local ilegible: {exc}"
        self._state.setdefault("assessments", {})
        self._state.setdefault("kpis", {})
        if not isinstance(self._state.get("assessments"), dict):
            self._state["assessments"] = {}
        if not isinstance(self._state.get("kpis"), dict):
            self._state["kpis"] = {}

    def _persist_state(self) -> bool:
        try:
            payload = {
                "assessments": self._state.get("assessments", {}),
                "kpis": self._state.get("kpis", {}),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            _atomic_write_text(
                self.state_path,
                json.dumps(_as_jsonable(payload), ensure_ascii=False, sort_keys=True),
            )
            return True
        except Exception as exc:  # noqa: BLE001 - persistir es best-effort
            self.last_error = f"no se pudo persistir el estado local: {exc}"
            return False

    # -- lectura ---------------------------------------------------------
    def load_catalog(self) -> list[dict[str, Any]]:
        if self._catalog is None:
            if not self.catalog_path.is_file():
                raise RepositoryError(f"no existe el catálogo local {self.catalog_path}")
            try:
                data = json.loads(self.catalog_path.read_text("utf-8"))
            except Exception as exc:  # noqa: BLE001
                raise RepositoryError(f"catálogo local inválido: {exc}") from exc
            if not isinstance(data, list):
                raise RepositoryError("el catálogo local debe ser una lista JSON")
            self._catalog = [dict(item) for item in data if isinstance(item, Mapping)]
        return [dict(item) for item in self._catalog]

    def load_assessments(self) -> dict[Any, dict[str, Any]]:
        raw = self._state.get("assessments", {})
        if not isinstance(raw, dict):
            return {}
        out: dict[Any, dict[str, Any]] = {}
        for key, value in raw.items():
            if not isinstance(value, Mapping):
                continue
            item = dict(value)
            try:
                numeric = int(key)
            except (TypeError, ValueError):
                numeric = None
            out[key] = item
            if numeric is not None:
                out.setdefault(numeric, item)
            code = item.get("control") or item.get("code")
            if code:
                out.setdefault(str(code), item)
        return out

    def load_risks(self) -> list[dict[str, Any]]:
        return [dict(item) for item in BASELINE_UNSA_RISKS]

    def load_evidence_from_db(self) -> list[dict[str, Any]]:
        return [dict(item) for item in BASELINE_UNSA_EVIDENCE]

    # -- escritura -------------------------------------------------------
    def save_assessments(self, rows: Sequence[Any]) -> dict[str, Any]:
        saved = 0
        for row in rows:
            control_id = _row_get(row, "control_id", "id")
            code = _row_get(row, "control", "code")
            if control_id in (None, 0) and not code:
                continue
            payload = {
                "control_id": int(control_id or 0),
                "control": str(code or ""),
                "is_applicable": bool(_row_get(row, "aplica", default=True)),
                "applicability_justification": str(_row_get(row, "justificacion", default="") or ""),
                "current_level": int(_row_get(row, "current_level", default=0) or 0),
                "target_level": int(_row_get(row, "target_level", default=0) or 0),
                "gap": int(_row_get(row, "gap", default=0) or 0),
                "compliance": float(_row_get(row, "compliance", default=0.0) or 0.0),
                "evidence": _evidence_text(row),
                "improvement_action": str(_row_get(row, "improvement_action", default="") or ""),
                "responsible": str(_row_get(row, "responsable", "responsible", default="") or ""),
                "priority": _row_get(row, "priority"),
                "due_date": _as_jsonable(_row_get(row, "due_date")),
                "status": _status_for_row(row),
                "estado": str(_row_get(row, "estado", default="") or ""),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            key = str(payload["control_id"]) if payload["control_id"] else payload["control"]
            self._state.setdefault("assessments", {})[key] = payload
            saved += 1
        persisted = self._persist_state()
        return {"guardadas": saved, "fuente": self.name, "persistido": persisted}

    def save_kpis(self, kpis: Mapping[str, Any], month: Any = None) -> dict[str, Any]:
        period = _first_day_of_month(month).isoformat()
        store = self._state.setdefault("kpis", {})
        bucket = store.setdefault(period, {})
        saved = 0
        if isinstance(kpis, Mapping):
            for key, value in kpis.items():
                if isinstance(value, Mapping):
                    item = {
                        "value": value.get("value"),
                        "has_data": bool(value.get("has_data", False)),
                    }
                else:
                    item = {"value": value, "has_data": value is not None}
                bucket[str(key)] = item
                saved += 1
        persisted = self._persist_state()
        return {"guardados": saved, "mes": period, "fuente": self.name, "persistido": persisted}


# ---------------------------------------------------------------------------
# Implementación PostgreSQL
# ---------------------------------------------------------------------------

class PostgresSoA(SoARepository):
    """Acceso real al esquema ``demo`` de Gestitel."""

    name = "postgres"
    CATALOG_SQL = """
        SELECT id, code, name, "position", group_code, group_name,
               applicable_role, sort_order, source_standard, description,
               equivalent_controls, law_29733_applies, law_29733_articles,
               law_29733_explanation
          FROM demo.core_annexacontrol
         ORDER BY sort_order, id
    """
    ASSESSMENT_SQL = """
        SELECT id, created_at, updated_at, is_deleted, deleted_at,
               is_applicable, applicability_justification, current_level,
               target_level, gap, compliance, evidence, improvement_action,
               responsible, priority, due_date, status, annex_a_control_id
          FROM demo.core_gapannexaassessment
         WHERE is_deleted = false
         ORDER BY annex_a_control_id
    """
    RISK_SQL = """
        SELECT
            re.id AS risk_id,
            re.risk_code,
            COALESCE(a.name, 'Activo no asignado') AS activo,
            COALESCE(re.risk_owner, a.owner, 'Oficialía de Seguridad de la Información (CISO)') AS propietario,
            COALESCE(re.threat, re.threat_code, 'Amenaza no especificada') AS amenaza,
            COALESCE(re.vulnerability, re.vulnerability_code, 'Vulnerabilidad no especificada') AS vulnerabilidad,
            re.description AS descripcion,
            COALESCE(re.residual_impact, re.controlled_impact, 1) AS nueva_consecuencia,
            COALESCE(re.residual_probability, re.controlled_probability, 1) AS nueva_probabilidad,
            COALESCE(re.residual_score, re.controlled_score, 1.0) AS riesgo_residual,
            re.residual_severity AS severidad,
            COALESCE(re.evidence, '') AS evidencia,
            ARRAY_REMOVE(ARRAY_AGG(DISTINCT ac.code), NULL) AS controles
          FROM demo.core_riskevaluation re
          LEFT JOIN demo.core_riskevaluationasset rea ON rea.evaluation_id = re.id
          LEFT JOIN demo.core_asset a ON a.id = rea.asset_id
          LEFT JOIN demo.core_riskcontrol rc ON rc.line_id = rea.id
          LEFT JOIN demo.core_riskcontrol_annex_a_controls rca ON rca.riskcontrol_id = rc.id
          LEFT JOIN demo.core_annexacontrol ac ON ac.id = rca.annexacontrol_id
         WHERE re.is_deleted = false
         GROUP BY re.id, re.risk_code, a.name, re.risk_owner, a.owner, re.threat, re.threat_code,
                  re.vulnerability, re.vulnerability_code, re.description, re.residual_impact,
                  re.controlled_impact, re.residual_probability, re.controlled_probability,
                  re.residual_score, re.controlled_score, re.residual_severity, re.evidence
         ORDER BY re.id
    """
    UPSERT_ASSESSMENT_SQL = """
        INSERT INTO demo.core_gapannexaassessment (
            created_at, updated_at, is_deleted, is_applicable,
            applicability_justification, current_level, target_level, gap,
            compliance, evidence, improvement_action, responsible, priority,
            due_date, status, annex_a_control_id
        ) VALUES (
            now(), now(), false, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (annex_a_control_id) DO UPDATE SET
            updated_at = now(),
            is_deleted = false,
            deleted_at = NULL,
            is_applicable = EXCLUDED.is_applicable,
            applicability_justification = EXCLUDED.applicability_justification,
            current_level = EXCLUDED.current_level,
            target_level = EXCLUDED.target_level,
            gap = EXCLUDED.gap,
            compliance = EXCLUDED.compliance,
            evidence = EXCLUDED.evidence,
            improvement_action = EXCLUDED.improvement_action,
            responsible = EXCLUDED.responsible,
            priority = EXCLUDED.priority,
            due_date = EXCLUDED.due_date,
            status = EXCLUDED.status
    """
    UPSERT_KPI_SQL = """
        INSERT INTO demo.core_dashboardsnapshot (month, kpi_key, value, has_data, captured_at)
        VALUES (%s, %s, %s, %s, now())
        ON CONFLICT (month, kpi_key) DO UPDATE SET
            value = EXCLUDED.value,
            has_data = EXCLUDED.has_data,
            captured_at = now()
    """

    def __init__(self, dsn: str | None = None, *, connect_timeout: int = 3):
        self.dsn = dsn or os.getenv("G7_DATABASE_URL") or os.getenv("DATABASE_URL") or ""
        self.connect_timeout = max(1, int(connect_timeout))
        self._params = self._params_from_env()
        self._driver: Any = None

    # -- configuración ---------------------------------------------------
    @staticmethod
    def _params_from_env() -> dict[str, Any]:
        def pick(*names: str, default: str = "") -> str:
            for name in names:
                value = os.getenv(name)
                if value:
                    return value
            return default

        host = pick("G7_DB_HOST", "DB_HOST", "PGHOST", "POSTGRES_HOST")
        if not host:
            return {}
        return {
            "host": host,
            "port": int(pick("G7_DB_PORT", "DB_PORT", "PGPORT", default="5432")),
            "dbname": pick("G7_DB_NAME", "DB_NAME", "PGDATABASE", "POSTGRES_DB", default="gestitel"),
            "user": pick("G7_DB_USER", "DB_USER", "PGUSER", "POSTGRES_USER", default="agente_g7"),
            "password": pick("G7_DB_PASSWORD", "DB_PASSWORD", "PGPASSWORD", "POSTGRES_PASSWORD"),
        }

    @property
    def configured(self) -> bool:
        return bool(self.dsn or self._params)

    def _driver_module(self) -> Any:
        if self._driver is None:
            try:
                import psycopg  # type: ignore import-not-found
                from psycopg.rows import dict_row  # type: ignore import-not-found
            except Exception as exc:  # noqa: BLE001
                raise RepositoryError(
                    "psycopg no está instalado; se usará el catálogo local"
                ) from exc
            self._driver = (psycopg, dict_row)
        return self._driver

    def _connect(self) -> Any:
        if not self.configured:
            raise RepositoryError("PostgreSQL no configurado (faltan G7_DB_* o DB_*)")
        psycopg, dict_row = self._driver_module()
        kwargs: dict[str, Any] = {"connect_timeout": self.connect_timeout, "row_factory": dict_row}
        if self.dsn:
            return psycopg.connect(self.dsn, **kwargs)
        return psycopg.connect(**self._params, **kwargs)

    # -- lectura ---------------------------------------------------------
    def available(self) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
            self.last_error = None
            return True
        except Exception as exc:  # noqa: BLE001
            self.last_error = f"{type(exc).__name__}: {exc}"
            return False

    def load_catalog(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self.CATALOG_SQL)
                rows = cur.fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            for key in ("equivalent_controls", "law_29733_articles"):
                value = item.get(key)
                if isinstance(value, str):
                    try:
                        item[key] = json.loads(value)
                    except json.JSONDecodeError:
                        item[key] = []
                elif value is None:
                    item[key] = []
            out.append(item)
        if not out:
            raise RepositoryError("demo.core_annexacontrol está vacía")
        return out

    def load_assessments(self) -> dict[Any, dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self.ASSESSMENT_SQL)
                rows = cur.fetchall()
        out: dict[Any, dict[str, Any]] = {}
        for row in rows:
            item = dict(row)
            out[item.get("annex_a_control_id")] = item
        return out

    def load_risks(self) -> list[dict[str, Any]]:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(self.RISK_SQL)
                    rows = cur.fetchall()
            out: list[dict[str, Any]] = []
            for row in rows:
                item = dict(row)
                score = float(item.get("riesgo_residual") or 1.0)
                out.append({
                    "id": item.get("risk_code") or f"RSK-{item.get('risk_id')}",
                    "risk_code": item.get("risk_code") or f"RSK-{item.get('risk_id')}",
                    "activo": item.get("activo") or "Activo general",
                    "propietario": item.get("propietario") or "CISO",
                    "amenaza": item.get("amenaza") or "",
                    "vulnerabilidad": item.get("vulnerabilidad") or "",
                    "descripcion": item.get("descripcion") or "",
                    "nueva_consecuencia": item.get("nueva_consecuencia") or 1,
                    "nueva_probabilidad": item.get("nueva_probabilidad") or 1,
                    "riesgo_residual": score,
                    "residual_score": score,
                    "severidad": item.get("severidad") or ("A" if score > 2.0 else "B"),
                    "controles": list(item.get("controles") or []),
                    "origen": "PostgreSQL (demo.core_riskevaluation)",
                })
            if out:
                return out
        except Exception as exc:  # noqa: BLE001
            self.last_error = f"load_risks: {type(exc).__name__}: {exc}"
        return LocalSoA().load_risks()

    def load_evidence_from_db(self) -> list[dict[str, Any]]:
        evidencias: list[dict[str, Any]] = []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    # G4 - Documentos
                    try:
                        cur.execute("""
                            SELECT code, name, category, status, current_version, responsible
                              FROM demo.core_document
                             WHERE is_deleted = false
                             ORDER BY code
                        """)
                        for doc in cur.fetchall():
                            d = dict(doc)
                            code = str(d.get("code") or "")
                            name = str(d.get("name") or "")
                            cat = str(d.get("category") or "").lower()
                            target_control = "A.5.1"
                            name_low = name.lower()
                            if "acceso" in name_low or "identidad" in name_low:
                                target_control = "A.5.15"
                            elif "backup" in name_low or "copia" in name_low or "respaldo" in name_low:
                                target_control = "A.8.13"
                            elif "teletrabajo" in name_low or "remoto" in name_low:
                                target_control = "A.6.7"
                            elif "privacidad" in name_low or "datos personales" in name_low or "retenci" in name_low:
                                target_control = "A.5.33"
                            elif "proveedor" in name_low or "tercero" in name_low:
                                target_control = "A.5.19"
                            elif "incidente" in name_low:
                                target_control = "A.5.24"

                            status_code = str(d.get("status") or "").upper()
                            aprobado = status_code in {"A", "APROBADO", "V", "VIGENTE"}
                            evidencias.append({
                                "control": target_control,
                                "descripcion": f"{name} (v{d.get('current_version') or '1.0'}) - Resp: {d.get('responsible') or 'OPD'}",
                                "estado": "implementado" if aprobado else "parcial",
                                "fuente": "G4",
                                "tipo": "politica" if "pol" in code.lower() or cat == "policy" else "procedimiento",
                                "ref": code,
                                "aprobado": aprobado,
                                "vigente": True,
                            })
                    except Exception:
                        pass

                    # G5 - DPA / Terceros (si existe la tabla extendida)
                    try:
                        cur.execute("""
                            SELECT c.contract_code, c.title, c.status, tp.name AS proveedor, a.verdict, a.score
                              FROM demo.core_dpacontract c
                              LEFT JOIN demo.core_thirdparty tp ON tp.id = c.third_party_id
                              LEFT JOIN demo.core_dpaassessment a ON a.contract_id = c.id
                             WHERE c.is_deleted = false
                        """)
                        for c in cur.fetchall():
                            cd = dict(c)
                            verdict = str(cd.get("verdict") or "").upper()
                            evidencias.append({
                                "control": "A.5.19",
                                "descripcion": f"DPA con {cd.get('proveedor') or 'Tercero'}: {cd.get('title')}. Dictamen: {verdict or 'Auditado'}",
                                "estado": "implementado" if verdict in {"R", "A"} else "parcial",
                                "fuente": "G5",
                                "tipo": "contrato",
                                "ref": cd.get("contract_code"),
                                "aprobado": verdict in {"R", "A"},
                                "vigente": True,
                            })
                    except Exception:
                        pass

                    # G8 - Incidentes
                    try:
                        cur.execute("""
                            SELECT incident_code, created_at, entity_type, rep_position
                              FROM demo.core_incident
                             WHERE is_deleted = false
                             ORDER BY id DESC
                             LIMIT 50
                        """)
                        for inc in cur.fetchall():
                            idict = dict(inc)
                            evidencias.append({
                                "control": "A.5.24",
                                "descripcion": f"Registro de incidente de seguridad {idict.get('incident_code')}",
                                "estado": "implementado",
                                "fuente": "G8",
                                "tipo": "registro",
                                "ref": idict.get("incident_code"),
                                "registros": True,
                                "vigente": True,
                            })
                    except Exception:
                        pass

                    # G1 - Capacitaciones
                    try:
                        cur.execute("""
                            SELECT training_code, title, area, presenter
                              FROM demo.core_training
                             WHERE is_deleted = false
                             ORDER BY id DESC
                             LIMIT 50
                        """)
                        for tr in cur.fetchall():
                            td = dict(tr)
                            evidencias.append({
                                "control": "A.6.3",
                                "descripcion": f"Capacitación institucional {td.get('training_code')}: {td.get('title')} ({td.get('area') or 'General'})",
                                "estado": "implementado",
                                "fuente": "G1",
                                "tipo": "capacitacion",
                                "ref": td.get("training_code"),
                                "registros": True,
                                "vigente": True,
                            })
                    except Exception:
                        pass

                    # G3 - Derechos ARCO
                    try:
                        cur.execute("""
                            SELECT case_code, channel, created_at
                              FROM demo.core_arcorequest
                             WHERE is_deleted = false
                             ORDER BY id DESC
                             LIMIT 50
                        """)
                        for ar in cur.fetchall():
                            ad = dict(ar)
                            evidencias.append({
                                "control": "A.1.2.6",
                                "descripcion": f"Solicitud ARCO expediente {ad.get('case_code')} por canal {ad.get('channel') or 'Virtual'}",
                                "estado": "implementado",
                                "fuente": "G3",
                                "tipo": "procedimiento",
                                "ref": ad.get("case_code"),
                                "registros": True,
                                "vigente": True,
                            })
                    except Exception:
                        pass

                    # G6 - Activos y Operaciones
                    try:
                        cur.execute("""
                            SELECT code, name, category, classification, owner
                              FROM demo.core_asset
                             WHERE is_deleted = false
                             ORDER BY code
                             LIMIT 50
                        """)
                        for ass in cur.fetchall():
                            ast = dict(ass)
                            evidencias.append({
                                "control": "A.5.9",
                                "descripcion": f"Activo inventariado {ast.get('code')}: {ast.get('name')} (Custodio: {ast.get('owner') or 'CISO'})",
                                "estado": "implementado",
                                "fuente": "G6",
                                "tipo": "registro",
                                "ref": ast.get("code"),
                                "registros": True,
                                "vigente": True,
                            })
                    except Exception:
                        pass

                    try:
                        cur.execute("""
                            SELECT operation_type, purpose, legal_basis, is_cross_border
                              FROM demo.core_personaldataoperation
                             ORDER BY id DESC
                             LIMIT 50
                        """)
                        for op in cur.fetchall():
                            opd = dict(op)
                            evidencias.append({
                                "control": "A.1.2.1",
                                "descripcion": f"Tratamiento RAT: {opd.get('operation_type')} ({opd.get('purpose')}) - Base: {opd.get('legal_basis')}",
                                "estado": "implementado",
                                "fuente": "G6",
                                "tipo": "registro",
                                "ref": f"RAT-{opd.get('operation_type')}",
                                "registros": True,
                                "vigente": True,
                            })
                    except Exception:
                        pass

            if evidencias:
                return evidencias
        except Exception as exc:  # noqa: BLE001
            self.last_error = f"load_evidence_from_db: {type(exc).__name__}: {exc}"
        return LocalSoA().load_evidence_from_db()

    # -- escritura -------------------------------------------------------
    def save_assessments(self, rows: Sequence[Any]) -> dict[str, Any]:
        payload: list[tuple[Any, ...]] = []
        skipped = 0
        for row in rows:
            control_id = _row_get(row, "control_id", "id")
            if not control_id:
                skipped += 1
                continue
            estado = str(_row_get(row, "estado", default="") or "")
            aplica = bool(_row_get(row, "aplica", default=estado != "no aplica"))
            payload.append((
                aplica,
                str(_row_get(row, "justificacion", default="") or ""),
                int(_row_get(row, "current_level", default=0) or 0),
                int(_row_get(row, "target_level", default=0) or 0),
                int(_row_get(row, "gap", default=0) or 0),
                float(_row_get(row, "compliance", default=0.0) or 0.0),
                _evidence_text(row),
                str(_row_get(row, "improvement_action", default="") or ""),
                str(_row_get(row, "responsable", "responsible", default="") or "")[:100],
                _row_get(row, "priority"),
                _row_get(row, "due_date"),
                _status_for_row(row),
                int(control_id),
            ))
        if not payload:
            return {"guardadas": 0, "omitidas": skipped, "fuente": self.name, "persistido": True}
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(self.UPSERT_ASSESSMENT_SQL, payload)
        return {"guardadas": len(payload), "omitidas": skipped, "fuente": self.name, "persistido": True}

    def save_kpis(self, kpis: Mapping[str, Any], month: Any = None) -> dict[str, Any]:
        period = _first_day_of_month(month)
        payload: list[tuple[Any, ...]] = []
        if isinstance(kpis, Mapping):
            for key, value in kpis.items():
                if isinstance(value, Mapping):
                    number = value.get("value")
                    has_data = bool(value.get("has_data", number is not None))
                else:
                    number = value
                    has_data = number is not None
                if number is not None:
                    try:
                        number = float(number)
                    except (TypeError, ValueError):
                        number = None
                        has_data = False
                payload.append((period, str(key), number, has_data))
        if not payload:
            return {"guardados": 0, "mes": period.isoformat(), "fuente": self.name, "persistido": True}
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(self.UPSERT_KPI_SQL, payload)
        return {"guardados": len(payload), "mes": period.isoformat(), "fuente": self.name, "persistido": True}


# ---------------------------------------------------------------------------
# Implementación híbrida
# ---------------------------------------------------------------------------

class HybridSoA(SoARepository):
    """PostgreSQL con degradación silenciosa a ``LocalSoA``."""

    name = "hybrid"

    def __init__(self, primary: SoARepository, fallback: SoARepository):
        self.primary = primary
        self.fallback = fallback
        self.degraded = False
        self.last_error: str | None = None
        self._using_fallback = False

    def _degrade(self, operation: str, exc: Exception) -> None:
        self.degraded = True
        self._using_fallback = True
        self.last_error = f"{operation}: {type(exc).__name__}: {exc}"

    def _recover(self) -> None:
        self.degraded = False
        self._using_fallback = False
        self.last_error = None

    def _active(self) -> SoARepository:
        return self.fallback if self._using_fallback else self.primary

    # -- lectura ---------------------------------------------------------
    def load_catalog(self) -> list[dict[str, Any]]:
        try:
            data = self.primary.load_catalog()
            self._recover()
            return data
        except Exception as exc:  # noqa: BLE001
            self._degrade("load_catalog", exc)
            return self.fallback.load_catalog()

    def load_assessments(self) -> dict[Any, dict[str, Any]]:
        try:
            return self.primary.load_assessments()
        except Exception as exc:  # noqa: BLE001
            self._degrade("load_assessments", exc)
            return self.fallback.load_assessments()

    def load_risks(self) -> list[dict[str, Any]]:
        try:
            return self.primary.load_risks()
        except Exception as exc:  # noqa: BLE001
            self._degrade("load_risks", exc)
            return self.fallback.load_risks()

    def load_evidence_from_db(self) -> list[dict[str, Any]]:
        try:
            return self.primary.load_evidence_from_db()
        except Exception as exc:  # noqa: BLE001
            self._degrade("load_evidence_from_db", exc)
            return self.fallback.load_evidence_from_db()

    # -- escritura -------------------------------------------------------
    def save_assessments(self, rows: Sequence[Any]) -> dict[str, Any]:
        try:
            result = self.primary.save_assessments(rows)
            self._recover()
            return result
        except Exception as exc:  # noqa: BLE001
            self._degrade("save_assessments", exc)
            return self.fallback.save_assessments(rows)

    def save_kpis(self, kpis: Mapping[str, Any], month: Any = None) -> dict[str, Any]:
        try:
            result = self.primary.save_kpis(kpis, month)
            self._recover()
            return result
        except Exception as exc:  # noqa: BLE001
            self._degrade("save_kpis", exc)
            return self.fallback.save_kpis(kpis, month)

    # -- estado ----------------------------------------------------------
    def status(self) -> dict[str, Any]:
        result = {
            "fuente": self.name,
            "degradado": bool(self.degraded),
            "usando_fallback": bool(self._using_fallback),
            "ultimo_error": self.last_error,
            "primario": self.primary.status(),
            "fallback": self.fallback.status(),
        }
        return result

    def close(self) -> None:
        self.primary.close()
        self.fallback.close()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_repository(mode: str | None = None, *, probe: bool = True) -> SoARepository:
    """Construye el repositorio según ``G7_DATA_SOURCE`` (por defecto ``auto``).

    * ``auto``: PostgreSQL si responde; en caso contrario ``LocalSoA``.
    * ``postgres``/``db``: intenta PostgreSQL y mantiene ``LocalSoA`` como red
      de seguridad para que el endpoint nunca devuelva HTTP 500.
    * ``local``/``memoria``: solo catálogo JSON local.
    """
    selected = str(mode or os.getenv("G7_DATA_SOURCE") or "auto").strip().lower()
    if selected not in VALID_DATA_SOURCES:
        selected = "auto"

    local = LocalSoA()
    if selected in {"local", "memoria", "memory"}:
        return local

    primary = PostgresSoA()
    if not primary.configured:
        primary.last_error = "PostgreSQL no configurado"
        return local

    if probe and selected == "auto" and not primary.available():
        return local

    return HybridSoA(primary, local)


def probar_conexion(dsn: str | None = None) -> dict[str, Any]:
    """Diagnóstico rápido usado por ``/api/controles/salud`` y pruebas."""
    pg = PostgresSoA(dsn)
    return {
        "configurado": pg.configured,
        "disponible": pg.available() if pg.configured else False,
        "error": pg.last_error,
    }


__all__ = [
    "BASELINE_UNSA_EVIDENCE",
    "BASELINE_UNSA_RISKS",
    "HybridSoA",
    "LocalSoA",
    "PostgresSoA",
    "RepositoryError",
    "SoARepository",
    "get_repository",
    "probar_conexion",
]
