"""Resolución de códigos de control para la SoA del Agente G7.

El catálogo real de Gestitel contiene 142 controles:

* 93 controles comunes ISO/IEC 27001:2022 (``applicable_role = 'A'``),
* 31 controles de responsable ISO/IEC 27701:2025 (``applicable_role = 'C'``),
* 18 controles de encargado ISO/IEC 27701:2025 (``applicable_role = 'P'``).

El Agente de Terceros (G5) no siempre emite los códigos del catálogo: usa
códigos de la estructura común de ISO/IEC 27701 (``A.3.8``, ``A.3.10`` ...),
que en el dump aparecen únicamente dentro de ``equivalent_controls``. Este
módulo construye los índices necesarios para resolver, sin ambigüedad y sin
dependencias externas:

1. código directo (``A.1.2.7``, ``A.2.5.7``),
2. código equivalente ISO/IEC 27701:2025 (``A.3.10`` -> ``A.5.20``),
3. código de grupo (``A.2.5`` -> todos los ``A.2.5.x``),
4. prefijo de dominio (``A.1`` -> todos los ``A.1.x``).

La resolución devuelve siempre una tupla inmutable de ``Control`` y la
estrategia utilizada, de modo que la trazabilidad quede en la respuesta del
agente y no dependa de coincidencias difusas.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


# ---------------------------------------------------------------------------
# Modelo de control
# ---------------------------------------------------------------------------

_ROLE_NAMES = {
    "A": "Común ISO/IEC 27001:2022",
    "C": "Privacidad — Responsable (ISO/IEC 27701:2025)",
    "P": "Privacidad — Encargado (ISO/IEC 27701:2025)",
}

_CODE_RE = re.compile(r"^A(?:\.\d+)+$")
_DOMAIN_RE = re.compile(r"^A\.\d+$")


def _as_list(value: Any) -> list[Any]:
    """Normaliza listas/tuplas/JSON-string a una lista de Python."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        return list(parsed) if isinstance(parsed, (list, tuple)) else [parsed]
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _canonical_code(value: Any) -> str:
    """Normaliza un código de control para comparaciones.

    Se eliminan espacios, se pasa a mayúsculas y se quitan ceros a la
    izquierda de cada segmento numérico (``A.05.01`` -> ``A.5.1``). No se
    inventan prefijos: si el valor no parece un código ``A.n...`` se devuelve
    tal cual, en mayúsculas, para poder reportarlo como no resuelto.
    """
    if value is None:
        return ""
    text = str(value).strip().upper().replace(" ", "")
    text = text.replace("ISO/IEC27701:", "").replace("ISO27701:", "")
    if not text.startswith("A"):
        return text
    parts = text.split(".")
    if not parts or parts[0] != "A":
        return text
    normalized = ["A"]
    for part in parts[1:]:
        if part.isdigit():
            normalized.append(str(int(part)))
        elif part:
            normalized.append(part)
    return ".".join(normalized)


@dataclass(frozen=True, slots=True)
class Control:
    """Control del catálogo ``demo.core_annexacontrol``."""

    id: int
    code: str
    name: str
    group_code: str
    group_name: str
    applicable_role: str
    sort_order: int = 0
    source_standard: str = ""
    description: str = ""
    equivalent_controls: tuple[Mapping[str, Any], ...] = ()
    law_29733_applies: bool | None = None
    law_29733_articles: tuple[str, ...] = ()
    law_29733_explanation: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _canonical_code(self.code))
        object.__setattr__(self, "group_code", _canonical_code(self.group_code))
        object.__setattr__(self, "applicable_role", str(self.applicable_role).upper()[:1])

    @property
    def role_label(self) -> str:
        return _ROLE_NAMES.get(self.applicable_role, "Control")

    @property
    def is_common(self) -> bool:
        return self.applicable_role == "A"

    @property
    def is_controller(self) -> bool:
        return self.applicable_role == "C"

    @property
    def is_processor(self) -> bool:
        return self.applicable_role == "P"

    @property
    def law_articles_text(self) -> str:
        return ", ".join(str(a) for a in self.law_29733_articles)

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any] | "Control") -> "Control":
        """Construye un ``Control`` desde una fila de PostgreSQL o un dict."""
        if isinstance(row, Control):
            return row

        def get(*keys: str, default: Any = None) -> Any:
            for key in keys:
                if key in row and row[key] is not None:
                    return row[key]
            return default

        equivalents = tuple(
            dict(item) for item in _as_list(get("equivalent_controls", "equivalentes"))
            if isinstance(item, Mapping)
        )
        articles = tuple(str(item) for item in _as_list(get("law_29733_articles", "articulos_ley")))

        law = get("law_29733_applies", "aplica_ley_29733")
        if isinstance(law, str):
            law = law.strip().lower() in {"t", "true", "1", "si", "sí", "yes"}

        return cls(
            id=int(get("id", "control_id", default=0) or 0),
            code=str(get("code", "codigo", "control", default="")),
            name=str(get("name", "nombre", default="")),
            group_code=str(get("group_code", "grupo_codigo", default="")),
            group_name=str(get("group_name", "grupo_nombre", default="")),
            applicable_role=str(get("applicable_role", "rol_normativo", "role", default="A")),
            sort_order=int(get("sort_order", "orden", default=0) or 0),
            source_standard=str(get("source_standard", "norma", default="")),
            description=str(get("description", "descripcion", "objetivo", default="")),
            equivalent_controls=equivalents,
            law_29733_applies=law if isinstance(law, bool) else None,
            law_29733_articles=articles,
            law_29733_explanation=str(get("law_29733_explanation", "explicacion_ley", default="")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "group_code": self.group_code,
            "group_name": self.group_name,
            "applicable_role": self.applicable_role,
            "sort_order": self.sort_order,
            "source_standard": self.source_standard,
            "description": self.description,
            "equivalent_controls": [dict(e) for e in self.equivalent_controls],
            "law_29733_applies": self.law_29733_applies,
            "law_29733_articles": list(self.law_29733_articles),
            "law_29733_explanation": self.law_29733_explanation,
        }


# ---------------------------------------------------------------------------
# Resultado de resolución
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Resolution:
    """Resultado trazable de resolver una referencia de control."""

    reference: str
    controls: tuple[Control, ...]
    strategy: str  # direct | equivalence | group | prefix | none
    matched: str | None = None

    @property
    def ok(self) -> bool:
        return bool(self.controls)

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(c.code for c in self.controls)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "strategy": self.strategy,
            "matched": self.matched,
            "controls": list(self.codes),
            "ok": self.ok,
        }


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class ControlResolver:
    """Índice inmutable y resolución determinista de códigos de control."""

    def __init__(self, controls: Iterable[Control | Mapping[str, Any]]):
        parsed: list[Control] = []
        seen: set[str] = set()
        for item in controls:
            control = Control.from_mapping(item)
            if not control.code or control.code in seen:
                continue
            seen.add(control.code)
            parsed.append(control)

        # Orden estable: el del dump (sort_order) y, como desempate, el id.
        parsed.sort(key=lambda c: (c.sort_order, c.id, c.code))

        self._controls: tuple[Control, ...] = tuple(parsed)
        self._by_code: dict[str, Control] = {c.code: c for c in parsed}
        self._by_equiv: dict[str, tuple[Control, ...]] = {}
        self._equiv_names: dict[str, str] = {}
        self._by_group: dict[str, tuple[Control, ...]] = {}
        self._by_prefix: dict[str, tuple[Control, ...]] = {}

        equiv_index: dict[str, list[Control]] = defaultdict(list)
        equiv_names: dict[str, str] = {}
        for control in parsed:
            for equivalent in control.equivalent_controls:
                code = _canonical_code(equivalent.get("code"))
                if not code or code in self._by_code:
                    # Un código directo siempre gana; no se indexa como alias.
                    continue
                if control not in equiv_index[code]:
                    equiv_index[code].append(control)
                name = equivalent.get("name") or control.name
                equiv_names.setdefault(code, str(name))

        self._by_equiv = {code: tuple(items) for code, items in equiv_index.items()}
        self._equiv_names = equiv_names

        group_index: dict[str, list[Control]] = defaultdict(list)
        prefix_index: dict[str, list[Control]] = defaultdict(list)
        for control in parsed:
            group_index[control.group_code].append(control)
            parts = control.code.split(".")
            # A.5.1 -> A.5 ; A.1.2.7 -> A.1.2, A.1 ; A.2.5.7 -> A.2.5, A.2
            for end in range(2, len(parts)):
                prefix = ".".join(parts[:end])
                prefix_index[prefix].append(control)
        self._by_group = {code: tuple(items) for code, items in group_index.items()}
        self._by_prefix = {code: tuple(items) for code, items in prefix_index.items()}

    # -- propiedades -----------------------------------------------------
    @property
    def all_controls(self) -> tuple[Control, ...]:
        return self._controls

    @property
    def by_code(self) -> Mapping[str, Control]:
        return self._by_code

    @property
    def equivalence_codes(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_equiv, key=_code_sort_key))

    @property
    def size(self) -> int:
        return len(self._controls)

    def counts_by_role(self) -> dict[str, int]:
        counts = {"A": 0, "C": 0, "P": 0}
        for control in self._controls:
            counts[control.applicable_role] = counts.get(control.applicable_role, 0) + 1
        return counts

    def counts_by_group(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for control in self._controls:
            counts[control.group_code] = counts.get(control.group_code, 0) + 1
        return counts

    def stats(self) -> dict[str, Any]:
        return {
            "total": self.size,
            "por_rol": self.counts_by_role(),
            "por_grupo": self.counts_by_group(),
            "codigos_equivalencia": len(self._by_equiv),
        }

    # -- resolución ------------------------------------------------------
    def resolve(self, reference: Any) -> Resolution:
        """Resuelve una referencia y explica la estrategia usada."""
        raw = "" if reference is None else str(reference).strip()
        code = _canonical_code(raw)
        if not code:
            return Resolution(raw, (), "none")

        direct = self._by_code.get(code)
        if direct is not None:
            return Resolution(raw, (direct,), "direct", direct.code)

        equivalent = self._by_equiv.get(code)
        if equivalent:
            return Resolution(raw, equivalent, "equivalence", code)

        group = self._by_group.get(code)
        if group:
            return Resolution(raw, group, "group", code)

        prefix = self._by_prefix.get(code)
        if prefix:
            return Resolution(raw, prefix, "prefix", code)

        return Resolution(raw, (), "none")

    def resolve_controls(self, reference: Any) -> tuple[Control, ...]:
        return self.resolve(reference).controls

    def resolve_code(self, reference: Any) -> str | None:
        """Devuelve el código canónico de una referencia única.

        Para referencias de grupo/prefijo devuelve ``None``: no existe un
        único código canónico y el llamador debe usar ``resolve``.
        """
        resolution = self.resolve(reference)
        if len(resolution.controls) == 1:
            return resolution.controls[0].code
        return None

    def resolve_many(self, references: Iterable[Any]) -> tuple[list[Control], dict[str, Any]]:
        """Resuelve muchas referencias y devuelve controles + traza agregada."""
        resolved: list[Control] = []
        seen: set[str] = set()
        by_strategy: dict[str, int] = defaultdict(int)
        unresolved: list[str] = []
        detail: dict[str, Any] = {}

        for reference in references:
            resolution = self.resolve(reference)
            by_strategy[resolution.strategy] += 1
            detail[str(reference)] = resolution.to_dict()
            if not resolution.ok:
                unresolved.append(str(reference))
                continue
            for control in resolution.controls:
                if control.code not in seen:
                    seen.add(control.code)
                    resolved.append(control)

        return resolved, {
            "por_estrategia": dict(by_strategy),
            "no_resueltos": unresolved,
            "detalle": detail,
            "controles_unicos": len(resolved),
        }

    def alias_name(self, code: Any) -> str:
        return self._equiv_names.get(_canonical_code(code), "")

    def aliases(self) -> list[dict[str, Any]]:
        """Pares ``código equivalente -> control canónico``.

        Se usa para construir las filas de referencia que el orquestador
        necesita para contar los códigos de G5 sin duplicar la evaluación.
        """
        result: list[dict[str, Any]] = []
        for code in self.equivalence_codes:
            for control in self._by_equiv.get(code, ()):
                result.append({
                    "code": code,
                    "name": self._equiv_names.get(code) or control.name,
                    "canonical": control.code,
                    "control": control,
                })
        return result


def _code_sort_key(code: str) -> tuple[int, ...]:
    numbers = tuple(int(part) for part in re.findall(r"\d+", code))
    return numbers or (0,)


__all__ = [
    "Control",
    "ControlResolver",
    "Resolution",
    "_canonical_code",
]
