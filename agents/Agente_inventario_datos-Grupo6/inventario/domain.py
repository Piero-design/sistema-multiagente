"""Motor determinista: identifica metadatos, no valores de personas ni obligaciones legales."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import unicodedata
from typing import Any

from .models import Fuente

PENDIENTE = "Por determinar"
RULES = [
    ("nombre", "Identificación", ["nombre", "nombres", "apellidos", "nombre completo", "nombres y apellidos", "full name", "first name", "last name"]),
    ("dni", "Identificación", ["dni", "documento nacional de identidad", "numero de documento"]),
    ("pasaporte", "Identificación", ["pasaporte", "passport"]),
    ("codigo_estudiante", "Identificación", ["codigo de estudiante", "codigo de alumno", "student id"]),
    ("correo", "Contacto", ["correo", "correo electronico", "correo institucional", "email", "e mail"]),
    ("telefono", "Contacto", ["telefono", "celular", "phone", "phone number"]),
    ("direccion", "Contacto", ["direccion", "domicilio", "address"]),
    ("fecha_nacimiento", "Demográficos", ["fecha de nacimiento", "fecha nacimiento", "birth date", "date of birth"]),
    ("nacionalidad", "Demográficos", ["nacionalidad", "nationality"]),
    ("estado_civil", "Demográficos", ["estado civil", "marital status"]),
    ("cuenta_bancaria", "Económicos", ["cuenta bancaria", "bank account", "iban", "cci"]),
    ("salario", "Económicos", ["salario", "sueldo", "salary"]),
    ("calificaciones", "Académicos", ["calificaciones", "notas", "grades"]),
    ("matricula", "Académicos", ["numero de matricula", "numero matricula", "enrollment id"]),
    ("cargo", "Laborales", ["cargo laboral", "puesto de trabajo", "job title"]),
    ("historial_laboral", "Laborales", ["historial laboral", "employment history"]),
    ("salud", "Salud", ["diagnostico", "historia clinica", "medical history", "grupo sanguineo"]),
    ("huella", "Biométricos", ["huella dactilar", "fingerprint"]),
    ("rostro", "Biométricos", ["reconocimiento facial", "face embedding"]),
    ("genetica", "Genéticos", ["informacion genetica", "datos geneticos", "perfil genetico", "genetic data"]),
]
SENSITIVE = {"Salud", "Biométricos", "Genéticos"}


class DomainError(ValueError):
    def __init__(self, message: str, code: str = "FUENTE_INVALIDA", status: int = 422):
        super().__init__(message)
        self.code, self.status = code, status


def normalizar(value: str) -> str:
    text = unicodedata.normalize("NFD", value)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.casefold().replace("_", " ").replace("-", " ")).strip()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def clasificar(nombre: str, *, exacto: bool = True) -> dict[str, Any]:
    norm = normalizar(nombre)
    matches = [(key, cat, alias) for key, cat, aliases in RULES for alias in aliases
               if (norm == alias if exacto else re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", norm))]
    if not matches:
        return {"nombre": nombre, "categoria": PENDIENTE, "es_pii": None, "sensibilidad": PENDIENTE,
                "clasificacion": "pendiente", "confianza": "Sin regla aplicable", "requiere_validacion": True}
    _, cat, _ = max(matches, key=lambda m: len(m[2]))
    return {"nombre": nombre, "categoria": cat, "es_pii": True,
            "sensibilidad": "Potencialmente sensible; revisión contextual" if cat in SENSITIVE else PENDIENTE,
            "clasificacion": "inferida_por_nombre", "confianza": "Coincidencia de taxonomía; no probabilidad",
            "requiere_validacion": True}


def extraer(fuente: Fuente) -> tuple[list[dict[str, Any]], list[str]]:
    """Extrae solo nombres, ubicaciones y categorías. Descarta valores del CSV/JSON."""
    fields: list[tuple[str, str]] = []
    warnings: list[str] = []
    if fuente.formato == "campos":
        fields = [(n, f"campos[{i}]") for i, n in enumerate(fuente.campos)]
    elif fuente.formato == "csv":
        try:
            content = (fuente.contenido or "").lstrip("\ufeff")
            sample = content[:8192]
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(io.StringIO(content), dialect=dialect, strict=True)
            headers = next(reader)
            if not headers or any(not h.strip() or len(h) > 120 for h in headers) or len(headers) > 200:
                raise DomainError("CSV: cabeceras vacías, demasiado largas o más de 200 columnas.")
            if len({normalizar(h) for h in headers}) != len(headers):
                raise DomainError("CSV: hay cabeceras duplicadas.")
            for row in reader:
                if row and len(row) != len(headers):
                    raise DomainError(f"CSV: número de columnas inconsistente en línea {reader.line_num}.")
            fields = [(h.strip(), f"cabecera.columna[{i + 1}]") for i, h in enumerate(headers)]
        except (csv.Error, StopIteration) as exc:
            raise DomainError("No se pudo leer el CSV. Revisa su estructura.") from exc
    elif fuente.formato == "json":
        try:
            obj = json.loads(fuente.contenido or "")
        except (json.JSONDecodeError, RecursionError) as exc:
            raise DomainError("JSON inválido o demasiado anidado.") from exc
        if not isinstance(obj, (dict, list)):
            raise DomainError("JSON: se requiere un objeto o una lista de objetos.")
        def walk(node, path="$", depth=0):
            if depth > 12:
                raise DomainError("JSON: máximo 12 niveles de anidación.")
            if isinstance(node, dict):
                for key, value in node.items():
                    if not key.strip() or len(key) > 120:
                        raise DomainError("JSON: nombres de propiedades vacíos o demasiado largos.")
                    child = path + "[" + json.dumps(key, ensure_ascii=False) + "]"
                    if isinstance(value, (dict, list)):
                        walk(value, child, depth + 1)
                    else:
                        fields.append((key, child))
                        if len(fields) > 10000:
                            raise DomainError("JSON: demasiadas propiedades; usa un esquema de campos.")
            elif isinstance(node, list):
                for value in node:
                    if not isinstance(value, dict):
                        raise DomainError("JSON: las listas deben contener objetos; usa campos para un esquema simple.")
                    walk(value, path + "[*]", depth + 1)
        walk(obj)
    else:
        # Texto libre: busca menciones por oración; no extrae pares nombre/valor.
        # La omisión por negación es conservadora y se declara en advertencias.
        warnings.append("Texto: coincidencias por alias; las cláusulas con negación se omiten. Puede haber falsos positivos y negativos.")
        for line_no, line in enumerate((fuente.contenido or "").splitlines(), 1):
            for clause in re.split(r"[.;!?]", normalizar(line)):
                if re.search(r"\b(no|sin|excepto|excluye|excluir)\b", clause):
                    continue
                for _, _, aliases in RULES:
                    hits = [alias for alias in aliases if re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", clause)]
                    if hits:
                        fields.append((max(hits, key=len), f"línea[{line_no}]"))
    result, seen = [], set()
    for name, location in fields:
        key = (normalizar(name), location)
        if key in seen:
            continue
        seen.add(key)
        item = clasificar(name)
        item["evidencia"] = {"fuente_id": fuente.id, "ubicacion": location, "campo": name,
                             "tipo": "mencion_en_texto" if fuente.formato == "texto" else "campo_en_fuente"}
        result.append(item)
        if len(result) > 500:
            raise DomainError("Máximo 500 campos distintos por fuente; divide la entrada.")
    if not result:
        warnings.append("No se reconocieron campos; esto no demuestra ausencia de datos personales.")
    if any(r["es_pii"] is None for r in result):
        warnings.append("Hay campos sin clasificar; no se declaran automáticamente no personales.")
    return result, warnings


def analizar_fuentes(organizacion: str, fuentes: list[Fuente]) -> dict[str, Any]:
    activos, warnings = [], []
    for fuente in fuentes:
        fields, notes = extraer(fuente)
        warnings.extend(f"{fuente.id}: {n}" for n in notes)
        if not fields:
            continue
        context = fuente.contexto.model_dump()
        declared = {k: {"valor": value or PENDIENTE,
                        "origen": "declarado_en_solicitud" if value else "pendiente",
                        "evidencia": f"fuente[{fuente.id}].contexto.{k}" if value else None}
                    for k, value in context.items()}
        raw = fuente.contenido if fuente.formato != "campos" else json.dumps(fuente.campos, ensure_ascii=False)
        source_hash = hashlib.sha256((raw or "").encode("utf-8")).hexdigest()
        identity = {"organizacion": organizacion, "sistema": normalizar(fuente.sistema), "fuente_id": fuente.id}
        activo = {"id": "ACT-" + digest(identity)[:24], "organizacion": organizacion,
                  "sistema": fuente.sistema, "fuente": {"id": fuente.id, "nombre": fuente.nombre, "formato": fuente.formato,
                                                        "sha256": source_hash},
                  "campos": fields, "contexto": declared, "estado": "pendiente_validacion",
                  "requiere_validacion": True, "motor": "reglas_locales", "simulado": False}
        activo["revision_sha256"] = digest(activo)
        activos.append(activo)
    return {"activos": activos, "total_activos": len(activos),
            "total_campos": sum(len(a["campos"]) for a in activos), "advertencias": warnings,
            "requiere_validacion": True}


def mapear(activos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for asset in activos:
        context = asset["contexto"]
        pending = [key for key, value in context.items() if value["origen"] == "pendiente"]
        fields = [f["nombre"] for f in asset["campos"]]
        destinations = context["transferencias"]["valor"]
        results.append({"id": "TRAT-" + asset["id"][4:], "activo_id": asset["id"], "sistema": asset["sistema"],
                        "datos": fields, "categorias": sorted({f["categoria"] for f in asset["campos"]}),
                        "contexto": context, "pendientes": pending, "estado": "borrador",
                        "flujos": [{"origen": asset["sistema"], "destino": dest, "campos": fields,
                                    "evidencia": context["transferencias"]["evidencia"],
                                    "estado": "declarado_pendiente_validacion"} for dest in destinations]
                        if isinstance(destinations, list) else [],
                        "requiere_validacion": True})
    return results
