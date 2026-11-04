"""Generación del Word oficial de la SoA usando la plantilla docente.

La plantilla ``Declaracion_de_aplicabilidad_ES.docx`` es un documento real de
ISO/IEC 27001:2013 con tres tablas relevantes:

* Tabla 1: historial de modificaciones.
* Tabla 2: matriz de aplicabilidad (7 columnas, encabezado azul y filas de
  grupo grises).
* Tabla 3: aceptación de riesgos residuales (8 columnas).

Este módulo **no reconstruye el documento desde cero**. Abre la plantilla,
localiza las tablas por su encabezado, conserva el encabezado/pie de página y
los estilos, y reconstruye únicamente el cuerpo de la Tabla 2 clonando las
filas XML originales (una para grupos y otra para controles). Después rellena
la Tabla 3 con los riesgos residuales. El guardado es atómico para que una
descarga concurrente nunca vea un archivo a medio escribir.
"""

from __future__ import annotations

import copy
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DEFAULT_ORGANIZATION = "Universidad Nacional de San Agustín de Arequipa (UNSA)"
DEFAULT_TEMPLATE = Path(__file__).resolve().parent / "templates" / "Declaracion_de_aplicabilidad_ES.docx"

ESTADO_LABELS = {
    "implementado": "Implementado",
    "parcial": "Parcial",
    "no implementado": "No implementado",
    "no aplica": "No aplica",
}

GROUP_FILLS = {"D9D9D9", "F2F2F2", "E7E6E6"}
NON_GROUP_FILLS = {None, "", "auto", "FFFFFF"}


class DocxBuildError(RuntimeError):
    """La plantilla no tiene la estructura esperada."""


# ---------------------------------------------------------------------------
# Utilidades XML
# ---------------------------------------------------------------------------

def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "SÍ" if value else "NO"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _cell_text(tc: Any) -> str:
    return "".join(node.text or "" for node in tc.iter(qn("w:t"))).strip()


def _row_text(tr: Any) -> str:
    return " | ".join(_cell_text(tc) for tc in tr.findall(qn("w:tc"))).strip()


def _cell_fill(tc: Any) -> str | None:
    tc_pr = tc.find(qn("w:tcPr"))
    if tc_pr is None:
        return None
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        return None
    return (shd.get(qn("w:fill")) or "").upper() or None


def _is_group_row(tr: Any) -> bool:
    cells = tr.findall(qn("w:tc"))
    if len(cells) < 2:
        return False
    code = _cell_text(cells[0])
    fill = _cell_fill(cells[0])
    if fill not in GROUP_FILLS:
        return False
    return bool(code.startswith("A."))


def _is_control_row(tr: Any) -> bool:
    cells = tr.findall(qn("w:tc"))
    if not cells:
        return False
    code = _cell_text(cells[0])
    if not code.startswith("A."):
        return False
    return _cell_fill(cells[0]) in NON_GROUP_FILLS or _cell_fill(cells[0]) is None


def _find_table(doc: Any, required: Sequence[str]) -> Any:
    needles = [needle.lower() for needle in required]
    for table in doc.tables:
        if not table.rows:
            continue
        header = " ".join(cell.text.lower() for cell in table.rows[0].cells)
        if all(needle in header for needle in needles):
            return table
    raise DocxBuildError(f"no se encontró una tabla con encabezado {required!r}")


def _remove_children(parent: Any, allowed: set[str]) -> None:
    for child in list(parent):
        if child.tag not in allowed:
            parent.remove(child)


def _append_text(run: Any, value: str) -> None:
    """Escribe texto en un ``w:r`` conservando su ``w:rPr`` y saltos de línea."""
    _remove_children(run, {qn("w:rPr")})
    lines = str(value).split("\n")
    for index, line in enumerate(lines):
        if index:
            run.append(OxmlElement("w:br"))
        node = OxmlElement("w:t")
        node.set(qn("xml:space"), "preserve")
        node.text = line
        run.append(node)


def _new_run(paragraph: Any) -> Any:
    run = OxmlElement("w:r")
    paragraph.append(run)
    return run


def _paragraph_rpr(paragraph: Any) -> Any:
    ppr = paragraph.find(qn("w:pPr"))
    if ppr is None:
        return None
    rpr = ppr.find(qn("w:rPr"))
    return copy.deepcopy(rpr) if rpr is not None else None


def _ensure_run(paragraph: Any) -> Any:
    """Devuelve un run editable conservando el ``rPr`` del párrafo/celda."""
    runs = paragraph.findall(qn("w:r"))
    if runs:
        keep = runs[0]
        for extra in runs[1:]:
            paragraph.remove(extra)
        if keep.find(qn("w:rPr")) is None:
            rpr = _paragraph_rpr(paragraph)
            if rpr is not None:
                keep.insert(0, rpr)
        return keep

    run = _new_run(paragraph)
    rpr = _paragraph_rpr(paragraph)
    if rpr is not None:
        run.append(rpr)
    return run


def _set_cell(cell: Any, value: Any) -> None:
    """Reemplaza el contenido de una celda preservando fuente y párrafo."""
    tc = cell._tc
    paragraphs = tc.findall(qn("w:p"))
    if not paragraphs:
        paragraph = OxmlElement("w:p")
        tc.append(paragraph)
        paragraphs = [paragraph]
    paragraph = paragraphs[0]
    for extra in paragraphs[1:]:
        tc.remove(extra)

    _remove_children(paragraph, {qn("w:pPr"), qn("w:r")})
    _append_text(_ensure_run(paragraph), _text(value))


# ---------------------------------------------------------------------------
# Normalización de entradas
# ---------------------------------------------------------------------------

def _as_rows(value: Any) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    if value is None:
        return rows
    if isinstance(value, Mapping):
        for key in ("soa", "soa_canonico", "filas", "rows", "riesgos", "riesgos_residuales"):
            nested = value.get(key)
            if isinstance(nested, (list, tuple)):
                rows = [item for item in nested if isinstance(item, Mapping)]
                break
    elif isinstance(value, (list, tuple)):
        rows = [item for item in value if isinstance(item, Mapping)]
    # Las filas de alias (códigos A.3.x de ISO/IEC 27701) no son controles
    # canónicos y no deben duplicar la Tabla 2.
    return [row for row in rows if not row.get("es_alias")]


def _get(row: Mapping[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def _group_of(row: Mapping[str, Any]) -> str:
    group = str(_get(row, "group_code", "grupo_codigo", "grupo", default="") or "").strip()
    if group:
        return group
    code = str(_get(row, "control", "codigo", "id", default="") or "").strip()
    parts = code.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else "A"


def _estado_label(row: Mapping[str, Any]) -> str:
    estado = str(_get(row, "estado", default="") or "").strip().lower()
    return ESTADO_LABELS.get(estado, _text(estado))


def _risk_value(risk: Mapping[str, Any], *keys: str, default: Any = "") -> Any:
    value = _get(risk, *keys, default=default)
    if isinstance(value, Mapping):
        for nested_key in ("valor", "value", "nivel", "score", "descripcion"):
            if nested_key in value and value[nested_key] not in (None, ""):
                return value[nested_key]
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(item) for item in value if item not in (None, ""))
    return value


def _risk_cells(risk: Mapping[str, Any], index: int) -> list[str]:
    score_raw = _risk_value(
        risk,
        "riesgo_residual",
        "residual_score",
        "residual",
        "nivel_residual",
        "score",
        "severidad",
    )
    severidad_raw = _text(
        _risk_value(risk, "severidad", "severity", "residual_severity")
    ).strip().upper()

    score_num: float | None = None
    try:
        score_num = float(score_raw)
    except (ValueError, TypeError):
        score_num = None

    # Etiquetar según umbral <= 2 (Aceptable) vs > 2 (No aceptable)
    if score_num is not None:
        if score_num <= 2.0:
            etiqueta = f"{score_num:.1f} [ACEPTADO - TOLERANCIA INSTITUCIONAL]"
        else:
            etiqueta = f"{score_num:.1f} [NO ACEPTABLE - ACCIÓN REQUERIDA]"
    elif severidad_raw in {"B", "BAJO", "BAJA", "LOW"}:
        etiqueta = f"{score_raw} [ACEPTADO - TOLERANCIA INSTITUCIONAL]" if score_raw else "[ACEPTADO - TOLERANCIA INSTITUCIONAL]"
    elif severidad_raw in {"A", "ALTO", "ALTA", "CRITICO", "CRITICA", "M", "MEDIO", "MEDIA"}:
        etiqueta = f"{score_raw} [NO ACEPTABLE - ACCIÓN REQUERIDA]" if score_raw else "[NO ACEPTABLE - ACCIÓN REQUERIDA]"
    else:
        etiqueta = _text(score_raw)

    return [
        str(index),
        _text(_risk_value(risk, "activo", "nombre_activo", "asset", "asset_name", "nombre", "descripcion", "id")),
        _text(_risk_value(risk, "propietario", "propietario_activo", "owner", "responsable", "dueno")),
        _text(_risk_value(risk, "amenaza", "threat", "evento", "causa")),
        _text(_risk_value(risk, "vulnerabilidad", "vulnerability", "debilidad", "debilidad_explotada")),
        _text(_risk_value(risk, "nueva_consecuencia", "consecuencia", "impacto", "nuevo_impacto")),
        _text(_risk_value(risk, "nueva_probabilidad", "probabilidad", "likelihood", "nueva_prob")),
        etiqueta,
    ]


# ---------------------------------------------------------------------------
# Reconstrucción de la Tabla 2
# ---------------------------------------------------------------------------

def _rebuild_table_2(doc: Any, rows: Sequence[Mapping[str, Any]]) -> int:
    table = _find_table(doc, ("aplicabilidad", "justificación", "estado"))
    tbl = table._tbl
    body_rows = tbl.findall(qn("w:tr"))
    if not body_rows:
        raise DocxBuildError("la tabla de aplicabilidad no tiene encabezado")

    header = body_rows[0]
    group_template = next((tr for tr in body_rows[1:] if _is_group_row(tr)), None)
    control_template = next((tr for tr in body_rows[1:] if _is_control_row(tr)), None)

    if group_template is None:
        raise DocxBuildError("la tabla de aplicabilidad no tiene una fila de grupo clonable")
    if control_template is None:
        control_template = body_rows[-1]

    group_template = copy.deepcopy(group_template)
    control_template = copy.deepcopy(control_template)

    # Actualiza el encabezado normativo sin tocar su formato azul.
    if len(header.findall(qn("w:tc"))) > 1:
        header_cell = table.rows[0].cells[1]
        current = header_cell.text
        if "27001" in current:
            _set_cell(header_cell, "Controles según ISO/IEC 27001:2022 e ISO/IEC 27701:2025")

    # Agrupa preservando el orden del catálogo (sort_order).
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    group_names: dict[str, str] = {}
    order: list[str] = []
    for row in rows:
        group = _group_of(row)
        if group not in grouped:
            grouped[group] = []
            order.append(group)
            group_names[group] = str(_get(row, "group_name", "grupo_nombre", default=group) or group)
        grouped[group].append(row)

    for tr in body_rows[1:]:
        tbl.remove(tr)

    emitted = 0
    for group in order:
        group_tr = copy.deepcopy(group_template)
        group_cells = group_tr.findall(qn("w:tc"))
        for index, cell in enumerate(group_cells):
            value = group if index == 0 else (group_names.get(group, group) if index == 1 else "")
            _set_cell_element(cell, value)
        _append_row(tbl, group_tr)
        emitted += 1

        for row in grouped[group]:
            control_tr = copy.deepcopy(control_template)
            cells = control_tr.findall(qn("w:tc"))
            valores = [
                _text(_get(row, "control", "codigo", "id")),
                _text(_get(row, "nombre", "name")),
                "SÍ" if bool(_get(row, "aplica", default=True)) else "NO",
                _text(_get(row, "justificacion", "justification")),
                _text(_get(row, "objetivo", "description")),
                _text(_get(row, "metodo", "method")),
                _estado_label(row),
            ]
            for index, cell in enumerate(cells):
                _set_cell_element(cell, valores[index] if index < len(valores) else "")
            _append_row(tbl, control_tr)
            emitted += 1

    return emitted


def _append_row(tbl: Any, tr: Any) -> None:
    """Inserta una fila antes del ``w:tblPrEx``/fin de tabla, si existiera."""
    tbl.append(tr)


def _set_cell_element(tc: Any, value: Any) -> None:
    """Versión de ``_set_cell`` que trabaja directamente sobre ``w:tc``."""
    paragraphs = tc.findall(qn("w:p"))
    if not paragraphs:
        paragraph = OxmlElement("w:p")
        tc.append(paragraph)
        paragraphs = [paragraph]
    paragraph = paragraphs[0]
    for extra in paragraphs[1:]:
        tc.remove(extra)
    _remove_children(paragraph, {qn("w:pPr"), qn("w:r")})
    _append_text(_ensure_run(paragraph), _text(value))


# ---------------------------------------------------------------------------
# Tabla 3: riesgos residuales
# ---------------------------------------------------------------------------

def _fill_table_3(doc: Any, riesgos: Sequence[Mapping[str, Any]]) -> int:
    table = _find_table(doc, ("riesgo residual", "amenaza", "vulnerabilidad"))
    rows = table.rows
    if len(rows) < 2:
        raise DocxBuildError("la tabla de riesgos residuales no tiene filas de cuerpo")

    body_trs = [row._tr for row in rows[1:]]
    template_tr = copy.deepcopy(body_trs[-1])
    while len(body_trs) < len(riesgos):
        new_tr = copy.deepcopy(template_tr)
        table._tbl.append(new_tr)
        body_trs.append(new_tr)

    for index, tr in enumerate(body_trs):
        cells = tr.findall(qn("w:tc"))
        values = _risk_cells(riesgos[index], index + 1) if index < len(riesgos) else [""] * len(cells)
        for cell_index, cell in enumerate(cells):
            _set_cell_element(cell, values[cell_index] if cell_index < len(values) else "")
    return min(len(riesgos), len(body_trs))


# ---------------------------------------------------------------------------
# Metadatos, historial y marcadores
# ---------------------------------------------------------------------------

def _fill_metadata(doc: Any, metadata: Mapping[str, Any], *, today: date) -> None:
    table = None
    for candidate in doc.tables:
        if len(candidate.rows) >= 4:
            first = candidate.rows[0].cells
            if len(first) == 2 and "código" in first[0].text.lower():
                table = candidate
                break
    if table is None:
        return

    defaults = {
        "código": metadata.get("codigo") or metadata.get("code") or "SoA-UNSA-2026",
        "versión": metadata.get("version") or metadata.get("versión") or "1.0",
        "fecha de la versión": metadata.get("fecha") or today.strftime("%d/%m/%Y"),
        "creado por": metadata.get("creado_por") or "Oficialía de Protección de Datos (OPD)",
        "aprobado por": metadata.get("aprobado_por") or "Comité de Gobierno Digital y DPO - UNSA",
        "nivel de confidencialidad": metadata.get("confidencialidad") or "Uso interno",
    }
    for row in table.rows:
        cells = row.cells
        if len(cells) < 2:
            continue
        label = cells[0].text.strip().lower().rstrip(":")
        if label in defaults:
            _set_cell(cells[1], defaults[label])


def _fill_history(doc: Any, metadata: Mapping[str, Any], *, today: date) -> None:
    table = None
    for candidate in doc.tables:
        if not candidate.rows:
            continue
        header = [cell.text.strip().lower() for cell in candidate.rows[0].cells]
        if len(header) == 4 and "fecha" in header[0] and "versión" in header[1]:
            table = candidate
            break
    if table is None:
        return

    # Fila 1: Sustituye el autor original de plantilla por el borrador institucional
    if len(table.rows) > 1:
        values_v01 = [
            "15/10/2026",
            "0.1",
            "Dirección Universitaria de TIC (DUTIC)",
            "Elaboración del borrador inicial del alcance SGSI y PIMS institucional.",
        ]
        for cell, value in zip(table.rows[1].cells, values_v01):
            _set_cell(cell, value)

    # Fila 2: Versión oficial actual (1.0) emitida por la OPD
    if len(table.rows) > 2:
        values_v10 = [
            today.strftime("%d/%m/%Y"),
            str(metadata.get("version") or metadata.get("versión") or "1.0"),
            str(metadata.get("creado_por") or "Oficialía de Protección de Datos (OPD)"),
            "Emisión oficial de la Declaración de Aplicabilidad (SoA) bajo ISO/IEC 27701:2025 y Ley N° 29733 (142 controles).",
        ]
        for cell, value in zip(table.rows[2].cells, values_v10):
            _set_cell(cell, value)

    # Limpiar filas restantes no utilizadas
    for row in table.rows[3:]:
        for cell in row.cells:
            _set_cell(cell, "")


def _replace_placeholders(doc: Any, organization: str, *, today: date, has_risks: bool) -> None:
    replacements = {
        "[nombre de la organización]": organization,
        "[fecha]": today.strftime("%d/%m/%Y"),
        "[cargo]": "Oficial de Protección de Datos (DPO) / Director de DUTIC",
        "[nombre]": "Universidad Nacional de San Agustín de Arequipa (UNSA)",
        "[firma]": "Firma Digital y Certificación Institucional",
        "Anexo A de la norma ISO 27001": "Anexo A de las normas ISO/IEC 27001:2022 e ISO/IEC 27701:2025 (PIMS) y la Ley N° 29733",
        "Norma ISO/IEC 27001, capítulo 6.1.3 d)": "Normas ISO/IEC 27701:2025 (cláusula 6.1.3 d) e ISO/IEC 27001:2022",
        "Norma ISO/IEC 27001": "Normas ISO/IEC 27001:2022 e ISO/IEC 27701:2025",
        "norma ISO 27001": "normas ISO/IEC 27001:2022 e ISO/IEC 27701:2025 (PIMS)",
        "Sistema de gestión de seguridad de la información (SGSI)": "Sistema de Gestión de Información de Privacidad y Seguridad (PIMS / SGSI)",
        "Son aplicables los siguientes controles del Anexo A de la norma ISO 27001:": "Son aplicables los siguientes controles del catálogo conjunto ISO/IEC 27001:2022 e ISO/IEC 27701:2025 (Anexo A):",
    }

    def replace_in_paragraph(paragraph: Any) -> None:
        if not paragraph.runs:
            return
        original = paragraph.text
        text = original

        # Purgado riguroso de la nota instructiva del cuadro de riesgos residuales
        if "[completar el cuadro" in text.lower():
            text = "Los riesgos residuales evaluados y su criterio de tolerancia institucional se detallan en la Tabla 3 a continuación:"
        else:
            for old, new in replacements.items():
                text = text.replace(old, new)

        if text == original:
            return
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""

    for paragraph in doc.paragraphs:
        replace_in_paragraph(paragraph)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_in_paragraph(paragraph)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def generar_soa_word(
    template_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    soa_filas: Any,
    riesgos_residuales: Any = None,
    *,
    metadata: Mapping[str, Any] | None = None,
    organizacion: str | None = None,
) -> str:
    """Genera el Word oficial de la SoA a partir de la plantilla docente.

    Parámetros
    ----------
    template_path:
        Ruta de la plantilla ``.docx`` (se abre, nunca se sobrescribe).
    output_path:
        Ruta del documento resultante.
    soa_filas:
        Lista de filas (dicts o ``SoARow`` convertidos) con ``control``,
        ``nombre``, ``aplica``, ``justificacion``, ``objetivo``, ``metodo``,
        ``estado``, ``group_code`` y ``group_name``.
    riesgos_residuales:
        Lista de dicts con los campos de la Tabla 3. También acepta el sobre
        ``{"riesgos": [...]}``.
    metadata:
        Valores opcionales para la tabla de metadatos (código, versión,
        creado_por, aprobado_por, confidencialidad, fecha).
    organizacion:
        Nombre que sustituye ``[nombre de la organización]``.

    Returns
    -------
    str
        Ruta absoluta del documento generado.
    """
    template = Path(template_path or DEFAULT_TEMPLATE)
    if not template.is_file():
        raise DocxBuildError(f"no existe la plantilla {template}")

    rows = _as_rows(soa_filas)
    risks = _as_rows(riesgos_residuales)
    metadata = dict(metadata or {})
    organization = (
        organizacion
        or metadata.get("organizacion")
        or os.getenv("G7_ORGANIZATION")
        or DEFAULT_ORGANIZATION
    )
    today = date.today()

    document = Document(str(template))
    _fill_metadata(document, metadata, today=today)
    _fill_history(document, metadata, today=today)
    controles = _rebuild_table_2(document, rows)
    riesgos = _fill_table_3(document, risks)
    _replace_placeholders(document, str(organization), today=today, has_risks=riesgos > 0)

    # El documento conserva encabezados, pies, estilos y relaciones porque se
    # guarda sobre la propia plantilla abierta; solo se reemplaza el archivo.
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=destination.stem + ".", suffix=".docx", dir=str(destination.parent))
    os.close(fd)
    try:
        document.save(tmp_name)
        os.replace(tmp_name, destination)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise

    return str(destination.resolve())


def resumen_documento(ruta: str | os.PathLike[str]) -> dict[str, Any]:
    """Diagnóstico rápido del DOCX generado (útil para pruebas y salud)."""
    document = Document(str(ruta))
    info = {"tablas": len(document.tables), "parrafos": len(document.paragraphs)}
    for index, table in enumerate(document.tables):
        info[f"tabla_{index}_filas"] = len(table.rows)
    return info


__all__ = [
    "DEFAULT_TEMPLATE",
    "DocxBuildError",
    "ESTADO_LABELS",
    "generar_soa_word",
    "resumen_documento",
]
