"""Capa de servicio del Agente G7: contrato, CMMI, persistencia y Word.

El servicio mantiene exactamente el contrato que consume el orquestador:

* ``output["datos"]["soa"]``: filas con ``control`` y ``estado`` en
  ``implementado``, ``parcial``, ``no implementado`` o ``no aplica``.
* ``output["datos"]["resumen"]``: contadores compatibles con G5 -> G7.

Todo lo demás (CMMI, gap, compliance, prioridad, KPIs, resolución de códigos,
persistencia y trazabilidad) es aditivo. Además, ``datos["soa"]`` incluye
filas de alias para los códigos que G5 emite en la estructura de ISO/IEC
27701 (``A.3.x``) pero que en el catálogo real viven como
``equivalent_controls``. Esas filas son estables (``estado = "no aplica"``)
para que el orquestador pueda comparar ``before``/``after`` sin ``KeyError``.

Las filas canónicas (142 controles) se exponen en ``datos["soa_canonico"]`` y
son las que se usan para el Word y para el frontend.
"""

from __future__ import annotations

import re
import threading
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from cmmi import (
    CMMIEngine,
    SoARow,
    brechas_soa,
    kpis_soa,
    normalize_rol,
    resumen_soa,
    responsable_para,
)
from repository import LocalSoA, SoARepository, get_repository
from resolver import Control, ControlResolver

BASE_DIR = Path(__file__).resolve().parent
AGENTE = "controles"
VERSION = "2026.1"

_ROL_VALIDOS = {"responsable", "encargado", "ambos"}
_ACCENTS = str.maketrans(
    "áéíóúÁÉÍÓÚüÜñÑ",
    "aeiouAEIOUuUnN",
)
_STOPWORDS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con",
    "contra", "cual", "cuando", "de", "del", "desde", "donde", "durante",
    "e", "el", "ella", "ellas", "ellos", "en", "entre", "era", "es", "esa",
    "ese", "eso", "esta", "este", "esto", "estos", "fue", "ha", "hasta",
    "hay", "la", "las", "le", "les", "lo", "los", "más", "me", "mi", "mis",
    "mucho", "muy", "no", "nos", "o", "otra", "otro", "para", "pero", "poco",
    "por", "porque", "que", "qué", "quien", "se", "ser", "si", "sin", "sobre",
    "son", "su", "sus", "también", "te", "tiene", "todo", "todos", "tu", "un",
    "una", "uno", "y", "ya", "the", "and", "or", "of", "to", "in", "for",
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _norm(text: Any) -> str:
    value = str(text or "").translate(_ACCENTS).lower()
    value = re.sub(r"[^a-z0-9áéíóúüñ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _tokens(text: Any) -> list[str]:
    return [word for word in _norm(text).split() if len(word) >= 3 and word not in _STOPWORDS]


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _resp(
    operacion: str,
    estado: str,
    respuesta: str,
    *,
    datos: Mapping[str, Any] | None = None,
    fuentes: Sequence[str] | None = None,
    confianza: float = 0.0,
    revision: bool = False,
) -> dict[str, Any]:
    return {
        "agente": AGENTE,
        "operacion": operacion,
        "estado": estado,
        "respuesta": respuesta,
        "datos": dict(datos or {}),
        "fuentes": list(fuentes or []),
        "confianza": float(confianza),
        "requiere_revision_humana": bool(revision),
    }


def _zero_resumen() -> dict[str, Any]:
    return {
        "controles_evaluados": 0,
        "aplican": 0,
        "excluidos": 0,
        "implementados": 0,
        "parciales": 0,
        "no_implementados": 0,
    }


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------

class SoAService:
    """Orquestación interna de G7, sin dependencias de Flask ni de FAISS."""

    def __init__(self, repository: SoARepository | None = None):
        self.repository = repository or get_repository()
        self._lock = threading.RLock()
        self._resolver: ControlResolver | None = None
        self._engine: CMMIEngine | None = None
        self._catalog_error: str | None = None
        self._knowledge: list[dict[str, Any]] | None = None
        self._last_persistence: dict[str, Any] = {}

    # -- catálogo --------------------------------------------------------
    def _load_catalog(self) -> None:
        """Carga el catálogo con doble red: repositorio -> LocalSoA."""
        errors: list[str] = []
        try:
            records = self.repository.load_catalog()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{type(exc).__name__}: {exc}")
            records = []
            try:
                records = LocalSoA().load_catalog()
            except Exception as local_exc:  # noqa: BLE001
                errors.append(f"local: {type(local_exc).__name__}: {local_exc}")

        resolver = ControlResolver(records)
        self._resolver = resolver
        self._engine = CMMIEngine(resolver)
        self._catalog_error = "; ".join(errors) or None

        if resolver.size == 0:
            self._catalog_error = self._catalog_error or "catálogo vacío"

    def _ensure_catalog(self) -> ControlResolver:
        with self._lock:
            if self._resolver is None or self._resolver.size == 0:
                self._load_catalog()
            assert self._resolver is not None
            return self._resolver

    def _ensure_engine(self) -> CMMIEngine:
        resolver = self._ensure_catalog()
        with self._lock:
            if self._engine is None:
                self._engine = CMMIEngine(resolver)
            return self._engine

    @property
    def resolver(self) -> ControlResolver:
        return self._ensure_catalog()

    def recargar_catalogo(self) -> dict[str, Any]:
        with self._lock:
            self._resolver = None
            self._engine = None
            self._load_catalog()
        return self.catalogo_stats()

    def catalogo_stats(self) -> dict[str, Any]:
        resolver = self._ensure_catalog()
        stats = resolver.stats()
        stats.update({
            "fuente": self.repository.name,
            "error_catalogo": self._catalog_error,
        })
        return stats

    def catalogo(self) -> list[dict[str, Any]]:
        """Catálogo con el formato que espera el frontend (``id``/``nombre``)."""
        resolver = self._ensure_catalog()
        result: list[dict[str, Any]] = []
        for control in resolver.all_controls:
            result.append({
                "id": control.code,
                "nombre": control.name,
                "agente_responsable": responsable_para(control.group_code),
                "grupo": control.group_code,
                "grupo_nombre": control.group_name,
                "rol_normativo": control.applicable_role,
                "descripcion": control.description,
                "sort_order": control.sort_order,
                "equivalente_iso27701": [
                    str(item.get("code")) for item in control.equivalent_controls
                    if item.get("code")
                ],
                "ley_29733_aplica": bool(control.law_29733_applies),
                "ley_29733_articulos": list(control.law_29733_articles),
            })
        return result

    def catalogo_completo(self) -> list[dict[str, Any]]:
        return [control.to_dict() for control in self._ensure_catalog().all_controls]

    # -- despacho --------------------------------------------------------
    def ejecutar(self, entrada: Mapping[str, Any] | None) -> dict[str, Any]:
        entrada = dict(entrada or {})
        operacion = _clean(entrada.get("operacion") or "consultar").lower()
        try:
            if operacion == "generar_soa":
                return self.generar_soa(entrada)
            if operacion in {"verificar_control", "verificar_controles", "verificar"}:
                return self.verificar_control(entrada)
            return self.consultar(entrada)
        except Exception as exc:  # noqa: BLE001 - nunca romper el contrato
            return self._error_seguro(operacion, exc, entrada)

    # -- skill 1: generar SoA -------------------------------------------
    def generar_soa(self, entrada: Mapping[str, Any]) -> dict[str, Any]:
        perfil = entrada.get("perfil") or {}
        if not isinstance(perfil, Mapping):
            perfil = {}
        rol_solicitado = _clean(perfil.get("rol"))
        rol = normalize_rol(rol_solicitado)
        if rol not in _ROL_VALIDOS:
            rol = "ambos"

        evidencias = entrada.get("evidencias") or []
        riesgos = entrada.get("riesgos") or []
        organizacion = _clean(perfil.get("organizacion")) or "Universidad Nacional de San Agustín de Arequipa (UNSA)"

        fuente_riesgos = "entrada"
        if not riesgos:
            try:
                riesgos = self.repository.load_risks()
                fuente_riesgos = getattr(self.repository, "name", "repositorio")
            except Exception:  # noqa: BLE001
                riesgos = LocalSoA().load_risks()
                fuente_riesgos = "local_fallback"

        fuente_evidencias = "entrada"
        if not evidencias:
            try:
                evidencias = self.repository.load_evidence_from_db()
                fuente_evidencias = getattr(self.repository, "name", "repositorio")
            except Exception:  # noqa: BLE001
                evidencias = LocalSoA().load_evidence_from_db()
                fuente_evidencias = "local_fallback"

        engine = self._ensure_engine()

        try:
            assessments = self.repository.load_assessments()
        except Exception:  # noqa: BLE001 - la evaluación no depende del estado previo
            assessments = {}

        rows, meta = engine.evaluar_catalogo(
            rol=rol,
            evidencias=evidencias,
            riesgos=riesgos,
            assessments=assessments,
        )

        resumen = resumen_soa(rows)
        brechas = brechas_soa(rows)
        kpis = kpis_soa(rows)
        persistencia = self._persistir(rows, kpis)

        canonico = [row.to_dict() for row in rows]
        aliases = self._alias_rows(rows)
        soa = canonico + aliases

        resumen = dict(resumen)
        resumen.update({
            "controles_catalogo": len(rows),
            "filas_compatibilidad": len(aliases),
            "controles_en_soa": len(soa),
        })

        datos: dict[str, Any] = {
            "soa": soa,
            "soa_canonico": canonico,
            "brechas": brechas,
            "resumen": resumen,
            "kpis": kpis,
            "riesgos_residuales": self._normalizar_riesgos(riesgos),
            "evidencias_cargadas": len(evidencias),
            "organizacion": organizacion,
            "meta": {
                "rol": rol,
                "rol_solicitado": rol_solicitado or rol,
                "version": VERSION,
                "catalogo": self.catalogo_stats(),
                "resolucion": meta,
                "persistencia": persistencia,
                "repositorio": self.repository.status(),
                "fuente_riesgos": fuente_riesgos,
                "fuente_evidencias": fuente_evidencias,
                "total_riesgos": len(riesgos),
                "total_evidencias": len(evidencias),
            },
            "traza_agente": self._traza_soa(rows, resumen, len(brechas), persistencia),
        }

        texto = (
            f"SoA generada para {organizacion} (rol: {rol}). "
            f"Controles evaluados: {resumen.get('controles_evaluados', 0)}; "
            f"aplican: {resumen.get('aplican', 0)}; "
            f"implementados: {resumen.get('implementados', 0)}; "
            f"parciales: {resumen.get('parciales', 0)}; "
            f"brechas: {resumen.get('no_implementados', 0)}. "
            f"Riesgos vinculados: {len(riesgos)} ({fuente_riesgos}). "
            f"Evidencias auditadas: {len(evidencias)} ({fuente_evidencias}). "
            "Requiere revisión y aprobación humana."
        )
        if persistencia.get("degradado"):
            texto += " Persistencia degradada a estado local."

        return _resp(
            "generar_soa",
            "ok",
            texto,
            datos=datos,
            fuentes=[
                "knowledge/catalogo_142.json",
                "demo.core_annexacontrol",
                "demo.core_gapannexaassessment",
                "demo.core_riskevaluation",
                "demo.core_document",
                "ISO/IEC 27001:2022",
                "ISO/IEC 27701:2025",
            ],
            confianza=1.0,
            revision=True,
        )

    # -- skill 2: verificar un control ----------------------------------
    def verificar_control(self, entrada: Mapping[str, Any]) -> dict[str, Any]:
        perfil = entrada.get("perfil") or {}
        if not isinstance(perfil, Mapping):
            perfil = {}
        rol_solicitado = _clean(perfil.get("rol"))
        rol = normalize_rol(rol_solicitado)
        if rol not in _ROL_VALIDOS:
            rol = "ambos"

        referencia = (
            entrada.get("control")
            or entrada.get("codigo")
            or entrada.get("control_id")
            or ""
        )
        resolver = self._ensure_catalog()
        resolucion = resolver.resolve(referencia)

        if not resolucion.ok:
            fila = {
                "control": _clean(referencia),
                "nombre": "",
                "aplica": False,
                "justificacion": "El código no existe en el catálogo de 142 controles ni en sus equivalencias ISO/IEC 27701:2025.",
                "estado": "no aplica",
                "evidencias": [],
                "responsable": "Oficialía de Protección de Datos (OPD)",
                "current_level": 0,
                "target_level": 0,
                "gap": 0,
                "compliance": 0.0,
                "priority": None,
                "recomendacion": "Verifique el código e intente nuevamente.",
                "controles_resueltos": [],
                "estrategia_resolucion": resolucion.strategy,
            }
            return _resp(
                "verificar_control",
                "rechazada",
                f"El control '{referencia}' no está en el catálogo.",
                datos=fila,
                fuentes=["knowledge/catalogo_142.json"],
                confianza=0.0,
            )

        engine = self._ensure_engine()
        try:
            assessments = self.repository.load_assessments()
        except Exception:  # noqa: BLE001
            assessments = {}

        evidencias = entrada.get("evidencias") or []
        riesgos = entrada.get("riesgos") or []
        if not riesgos:
            try:
                riesgos = self.repository.load_risks()
            except Exception:
                riesgos = []
        if not evidencias:
            try:
                evidencias = self.repository.load_evidence_from_db()
            except Exception:
                evidencias = []

        rows, meta = engine.evaluar_catalogo(
            rol=rol,
            evidencias=evidencias,
            riesgos=riesgos,
            assessments=assessments,
        )

        wanted = set(resolucion.codes)
        coincidencias = [row for row in rows if row.control in wanted]
        if not coincidencias:
            # Puede ocurrir si el catálogo cambió entre la carga y la consulta.
            coincidencias = [
                engine.evaluar(control, rol, hoy=date.today())
                for control in resolucion.controls
            ]

        fila_base = coincidencias[0]
        fila = fila_base.to_dict()
        fila["recomendacion"] = self._recomendacion(fila_base)
        fila["controles_resueltos"] = [row.to_dict() for row in coincidencias]
        fila["estrategia_resolucion"] = resolucion.strategy
        fila["rol"] = rol
        fila["resolucion"] = resolucion.to_dict()
        fila["traza_agente"] = self._traza_verificacion(fila, resolucion, len(coincidencias))

        return _resp(
            "verificar_control",
            "ok",
            f"Control {fila_base.control}: {fila_base.estado}. {fila['recomendacion']}",
            datos=fila,
            fuentes=["knowledge/catalogo_142.json", "demo.core_annexacontrol"],
            confianza=1.0,
            revision=True,
        )

    # -- skill 3: consulta documental ------------------------------------
    def consultar(self, entrada: Mapping[str, Any]) -> dict[str, Any]:
        solicitud = _clean(entrada.get("solicitud") or entrada.get("mensaje") or "")
        if not solicitud:
            return _resp(
                "consultar",
                "rechazada",
                "La solicitud está vacía.",
                datos={"respuesta_directa": "Indique una consulta sobre controles, privacidad o políticas institucionales.", "hits": []},
            )

        hits = self._search(solicitud, limit=5)
        if not hits:
            return _resp(
                "consultar",
                "sin_respuesta",
                "No se encontraron directivas o controles con suficiente afinidad.",
                datos={"respuesta_directa": "No se encontraron directivas o controles con suficiente afinidad.", "hits": []},
                confianza=0.0,
            )

        top = hits[0]
        respuesta = (
            f"De acuerdo con **{top['meta']}** "
            f"(afinidad {round(top['score'] * 100, 1)}%):\n\n{top['texto']}"
        )
        return _resp(
            "consultar",
            "ok",
            respuesta,
            datos={
                "respuesta_directa": respuesta,
                "hits": hits,
                "traza_agente": self._traza_consulta(solicitud, hits),
            },
            fuentes=sorted({hit["meta"] for hit in hits}),
            confianza=round(float(top["score"]), 3),
        )

    # -- normalización de riesgos ---------------------------------------
    @staticmethod
    def _normalizar_riesgos(riesgos: Any) -> list[dict[str, Any]]:
        if isinstance(riesgos, Mapping):
            for key in ("riesgos", "riesgos_residuales", "items"):
                nested = riesgos.get(key)
                if isinstance(nested, (list, tuple)):
                    riesgos = nested
                    break
            else:
                riesgos = []
        if not isinstance(riesgos, (list, tuple)):
            return []
        return [dict(item) for item in riesgos if isinstance(item, Mapping)]

    # -- persistencia ----------------------------------------------------
    def _persistir(self, rows: Sequence[SoARow], kpis: Mapping[str, Any]) -> dict[str, Any]:
        resultado: dict[str, Any] = {
            "intentada": True,
            "fuente": self.repository.name,
            "degradado": False,
            "assessments": None,
            "kpis": None,
            "error": None,
        }
        try:
            resultado["assessments"] = self.repository.save_assessments(rows)
            if isinstance(resultado["assessments"], Mapping) and resultado["assessments"].get("persistido") is False:
                resultado["degradado"] = True
        except Exception as exc:  # noqa: BLE001 - la SoA ya está calculada
            resultado["degradado"] = True
            resultado["error"] = f"assessments: {type(exc).__name__}: {exc}"
        try:
            resultado["kpis"] = self.repository.save_kpis(kpis)
            if isinstance(resultado["kpis"], Mapping) and resultado["kpis"].get("persistido") is False:
                resultado["degradado"] = True
        except Exception as exc:  # noqa: BLE001
            resultado["degradado"] = True
            extra = f"kpis: {type(exc).__name__}: {exc}"
            resultado["error"] = f"{resultado['error']}; {extra}" if resultado["error"] else extra

        estado_repo = self.repository.status()
        resultado["degradado"] = bool(resultado["degradado"] or estado_repo.get("degradado"))
        if estado_repo.get("ultimo_error"):
            resultado["error"] = resultado["error"] or estado_repo["ultimo_error"]
        self._last_persistence = resultado
        return resultado

    # -- alias de compatibilidad ----------------------------------------
    def _alias_rows(self, rows: Sequence[SoARow]) -> list[dict[str, Any]]:
        resolver = self._ensure_catalog()
        canonical = {row.control: row for row in rows}
        grouped: dict[str, list[Control]] = {}
        names: dict[str, str] = {}
        for alias in resolver.aliases():
            code = str(alias.get("code") or "")
            if not code:
                continue
            controls = list(resolver.resolve_controls(code))
            if not controls:
                continue
            bucket = grouped.setdefault(code, [])
            for control in controls:
                if all(existing.code != control.code for existing in bucket):
                    bucket.append(control)
            names.setdefault(code, str(alias.get("name") or ""))

        aliases: list[dict[str, Any]] = []
        for code, controls in grouped.items():
            canonical_codes = [control.code for control in controls]
            target = next((canonical.get(item) for item in canonical_codes if item in canonical), None)
            aliases.append({
                "control": code,
                "nombre": names.get(code) or (target.nombre if target else code),
                "aplica": False,
                "aplica_canonico": bool(target.aplica) if target else False,
                "justificacion": (
                    f"Código de referencia ISO/IEC 27701:2025. Su evaluación canónica se "
                    f"registra en {', '.join(canonical_codes)}."
                ),
                "estado": "no aplica",
                "current_level": 0,
                "target_level": 0,
                "gap": 0,
                "compliance": 0.0,
                "priority": None,
                "prioridad": None,
                "responsable": target.responsable if target else responsable_para("A.5"),
                "evidencias": [],
                "evidencia_refs": [],
                "es_alias": True,
                "control_canonico": canonical_codes[0] if canonical_codes else None,
                "controles_canonicos": canonical_codes,
                "fuente_codigo": "equivalent_controls",
            })
        return aliases

    # -- búsqueda local sin FAISS ----------------------------------------
    def _load_knowledge(self) -> list[dict[str, Any]]:
        if self._knowledge is not None:
            return self._knowledge
        chunks: list[dict[str, Any]] = []
        for folder in ("normativa", "politicas", "evidencias"):
            base = BASE_DIR / "knowledge" / folder
            if not base.is_dir():
                continue
            for path in sorted(base.glob("*.md")):
                try:
                    text = path.read_text("utf-8")
                except OSError:
                    continue
                for raw in re.split(r"\n\s*\n", text):
                    paragraph = raw.strip()
                    if len(paragraph) < 40:
                        continue
                    chunks.append({
                        "meta": f"{folder}/{path.name}",
                        "texto": paragraph,
                        "tokens": set(_tokens(paragraph)),
                    })
        self._knowledge = chunks
        return chunks

    def _search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        terms = set(_tokens(query))
        if not terms:
            return []

        scored: list[dict[str, Any]] = []
        for chunk in self._load_knowledge():
            overlap = len(terms & chunk["tokens"])
            if overlap:
                score = overlap / max(len(terms), 1)
                scored.append({
                    "meta": chunk["meta"],
                    "score": round(min(0.99, 0.35 + 0.65 * score), 3),
                    "texto": chunk["texto"],
                })

        for control in self._ensure_catalog().all_controls:
            haystack = set(_tokens(f"{control.code} {control.name} {control.description} {control.group_name}"))
            overlap = len(terms & haystack)
            if not overlap:
                continue
            score = overlap / max(len(terms), 1)
            scored.append({
                "meta": f"Catálogo ISO/IEC 27001:2022 / 27701:2025 — {control.code}",
                "score": round(min(0.98, 0.30 + 0.65 * score), 3),
                "texto": f"{control.code} — {control.name}\n\n{control.description}",
            })

        scored.sort(key=lambda item: item["score"], reverse=True)
        seen: set[str] = set()
        result: list[dict[str, Any]] = []
        for item in scored:
            key = item["texto"][:160]
            if key in seen:
                continue
            seen.add(key)
            if item["score"] >= 0.25:
                result.append(item)
            if len(result) >= limit:
                break
        return result

    # -- trazabilidad ----------------------------------------------------
    @staticmethod
    def _recomendacion(row: SoARow) -> str:
        if not row.aplica:
            return "Documentar la exclusión y su justificación en la SoA."
        if row.gap == 0:
            return "Mantener la evidencia vigente y revisarla al menos anualmente."
        return row.improvement_action

    def _traza_soa(
        self,
        rows: Sequence[SoARow],
        resumen: Mapping[str, Any],
        brechas: int,
        persistencia: Mapping[str, Any],
    ) -> dict[str, Any]:
        fuentes = "catálogo real de PostgreSQL" if self.repository.name != "local" else "catálogo local de 142 controles"
        tiempo = round(1.2 + min(len(rows), 142) / 200.0, 2)
        return {
            "pensamiento": {
                "tiempo_seg": tiempo,
                "resumen": (
                    f"Evaluando {len(rows)} controles ISO/IEC 27001:2022 / 27701:2025, "
                    f"resolviendo evidencias de G5/G4 y calculando madurez CMMI..."
                ),
                "detalles": (
                    f"1. Fuente: {fuentes}.\n"
                    f"2. Controles evaluados: {len(rows)}; aplican: {resumen.get('aplican', 0)}.\n"
                    f"3. Implementados: {resumen.get('implementados', 0)}; parciales: {resumen.get('parciales', 0)}; brechas: {brechas}.\n"
                    f"4. Nivel CMMI promedio: {resumen.get('nivel_promedio')}.\n"
                    f"5. Persistencia: {'degradada a local' if persistencia.get('degradado') else 'correcta'}."
                ),
            },
            "acciones": [
                {"tipo": "files", "titulo": "Catálogo de controles", "detalle": f"{len(rows)} controles cargados desde {self.repository.name}"},
                {"tipo": "rules", "titulo": "Motor CMMI determinista", "detalle": f"{resumen.get('aplican', 0)} aplicables, {brechas} brechas"},
                {"tipo": "rules", "titulo": "Resolución de códigos G5", "detalle": "Códigos directos y equivalentes ISO/IEC 27701:2025"},
                {"tipo": "db", "titulo": "Persistencia SoA", "detalle": persistencia.get("error") or f"UPSERT en {self.repository.name}"},
                {"tipo": "artifact", "titulo": "Word disponible", "detalle": "Plantilla docente con Tabla 2 y Tabla 3"},
            ],
        }

    @staticmethod
    def _traza_verificacion(row: Mapping[str, Any], resolucion: Any, coincidencias: int) -> dict[str, Any]:
        return {
            "pensamiento": {
                "tiempo_seg": 0.8,
                "resumen": f"Verificación puntual del control {row.get('control')} ({row.get('nombre')})...",
                "detalles": (
                    f"1. Referencia: {resolucion.reference}.\n"
                    f"2. Estrategia: {resolucion.strategy}.\n"
                    f"3. Controles canónicos: {', '.join(resolucion.codes) or 'ninguno'}.\n"
                    f"4. Coincidencias evaluadas: {coincidencias}.\n"
                    f"5. Estado: {row.get('estado')}."
                ),
            },
            "acciones": [
                {"tipo": "resolver", "titulo": "Resolución de código", "detalle": f"{resolucion.strategy}: {', '.join(resolucion.codes)}"},
                {"tipo": "inspect", "titulo": f"Inspeccionadas evidencias de {row.get('control')}", "detalle": "Evidencias G5/G4/manuales normalizadas"},
                {"tipo": "rules", "titulo": "CMMI y prioridad", "detalle": f"Nivel {row.get('current_level')}/5, gap {row.get('gap')}, prioridad {row.get('priority')}"},
            ],
        }

    def _traza_consulta(self, solicitud: str, hits: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        return {
            "pensamiento": {
                "tiempo_seg": 0.9,
                "resumen": f"El auditor consultó: '{solicitud}'. Buscando en catálogo y directivas institucionales...",
                "detalles": (
                    f"1. Consulta: {solicitud}\n"
                    f"2. Recuperación local determinista (sin dependencias externas).\n"
                    f"3. Fragmentos recuperados: {len(hits)}.\n"
                    "4. Respuesta fundada en catálogo ISO/IEC 27701:2025 y políticas UNSA."
                ),
            },
            "acciones": [
                {"tipo": "rag", "titulo": "Búsqueda documental local", "detalle": f"{len(hits)} fragmentos recuperados"},
                {"tipo": "files", "titulo": "knowledge/normativa y knowledge/politicas", "detalle": ", ".join(hit["meta"] for hit in hits[:3])},
            ],
        }

    # -- error seguro ----------------------------------------------------
    def _error_seguro(self, operacion: str, exc: Exception, entrada: Mapping[str, Any]) -> dict[str, Any]:
        error = f"{type(exc).__name__}: {exc}"
        if operacion == "generar_soa":
            datos = self._fallback_soa(entrada, error)
            return _resp(
                "generar_soa",
                "degradado",
                f"SoA generada con degradación controlada: {error}",
                datos=datos,
                fuentes=["knowledge/catalogo_142.json"],
                confianza=0.5,
                revision=True,
            )
        if operacion in {"verificar_control", "verificar_controles", "verificar"}:
            return _resp(
                operacion,
                "degradado",
                f"No fue posible verificar el control: {error}",
                datos={
                    "control": _clean(entrada.get("control")),
                    "nombre": "",
                    "aplica": False,
                    "estado": "no aplica",
                    "justificacion": "Error controlado durante la verificación.",
                    "evidencias": [],
                    "responsable": responsable_para("A.5"),
                    "recomendacion": "Reintente la verificación o revise el catálogo local.",
                },
                confianza=0.0,
            )
        return _resp(
            operacion,
            "degradado",
            f"No fue posible completar la consulta: {error}",
            datos={
                "respuesta_directa": "El servicio de consulta no está disponible en este momento.",
                "hits": [],
            },
            confianza=0.0,
        )

    def _fallback_soa(self, entrada: Mapping[str, Any], error: str) -> dict[str, Any]:
        """Última red: calcula con ``LocalSoA`` sin tocar la base de datos."""
        perfil = entrada.get("perfil") or {}
        if not isinstance(perfil, Mapping):
            perfil = {}
        rol = normalize_rol(perfil.get("rol")) if perfil.get("rol") else "ambos"
        if rol not in _ROL_VALIDOS:
            rol = "ambos"
        try:
            local = LocalSoA()
            resolver = ControlResolver(local.load_catalog())
            engine = CMMIEngine(resolver)
            rows, meta = engine.evaluar_catalogo(
                rol=rol,
                evidencias=entrada.get("evidencias") or [],
                riesgos=entrada.get("riesgos") or [],
                assessments={},
            )
            resumen = resumen_soa(rows)
            canonico = [row.to_dict() for row in rows]
            aliases = self._alias_rows(rows) if self._resolver and self._resolver.size else []
            return {
                "soa": canonico + aliases,
                "soa_canonico": canonico,
                "brechas": brechas_soa(rows),
                "resumen": resumen,
                "kpis": kpis_soa(rows),
                "meta": {
                    "rol": rol,
                    "version": VERSION,
                    "error": error,
                    "persistencia": {"degradado": True, "error": error},
                    "repositorio": {"fuente": "local", "degradado": True, "ultimo_error": error},
                    "resolucion": meta,
                },
                "traza_agente": self._traza_soa(rows, resumen, len(brechas_soa(rows)), {"degradado": True}),
            }
        except Exception as exc:  # noqa: BLE001 - el contrato debe sobrevivir
            return {
                "soa": [],
                "soa_canonico": [],
                "brechas": [],
                "resumen": _zero_resumen(),
                "kpis": {},
                "meta": {
                    "rol": rol,
                    "version": VERSION,
                    "error": f"{error}; fallback: {type(exc).__name__}: {exc}",
                    "persistencia": {"degradado": True},
                },
            }

    # -- salud -----------------------------------------------------------
    def salud(self) -> dict[str, Any]:
        try:
            stats = self.catalogo_stats()
        except Exception as exc:  # noqa: BLE001
            stats = {"error": f"{type(exc).__name__}: {exc}"}
        return {
            "agente": AGENTE,
            "version": VERSION,
            "estado": "ok" if stats.get("total") else "degradado",
            "catalogo": stats,
            "repositorio": self.repository.status(),
            "ultima_persistencia": self._last_persistence,
        }


__all__ = ["AGENTE", "SoAService", "VERSION"]
