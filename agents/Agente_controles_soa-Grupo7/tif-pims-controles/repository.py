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
    "HybridSoA",
    "LocalSoA",
    "PostgresSoA",
    "RepositoryError",
    "SoARepository",
    "get_repository",
    "probar_conexion",
]
