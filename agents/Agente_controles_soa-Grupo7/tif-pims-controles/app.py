"""API Flask del Agente G7 — Controles y Declaración de Aplicabilidad (SoA).

Contrato con el orquestador (no negociable):

* ``POST /api/controles/ejecutar`` devuelve siempre HTTP 200 con
  ``output["datos"]["soa"]`` (filas con ``control`` y ``estado``) y
  ``output["datos"]["resumen"]``.
* Cualquier fallo de PostgreSQL se degrada a ``LocalSoA`` y el endpoint sigue
  respondiendo. Nunca se propaga un HTTP 500 al orquestador.

Rutas adicionales: catálogo, salud y exportación Word con la plantilla
docente (Tabla 2 reconstruida con 142 controles y Tabla 3 de riesgos).
"""

from __future__ import annotations

import math
import os
import tempfile
import threading
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping

from flask import Flask, after_this_request, jsonify, request, send_file

from docx_builder import DEFAULT_TEMPLATE, generar_soa_word
from repository import LocalSoA
from service import AGENTE, VERSION, SoAService

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
RUNTIME_DIR = BASE_DIR / "runtime"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOWNLOAD_NAME = "Declaracion_de_Aplicabilidad_ISO_27701_UNSA.docx"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["JSON_SORT_KEYS"] = False

_servicio: SoAService | None = None
_servicio_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _json_safe(value: Any) -> Any:
    """Convierte fechas, Decimal, NaN y objetos raros a JSON válido."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    try:
        return value.item()  # numpy / Decimal
    except Exception:  # noqa: BLE001
        return str(value)


def get_service() -> SoAService:
    global _servicio
    if _servicio is not None:
        return _servicio
    with _servicio_lock:
        if _servicio is None:
            try:
                _servicio = SoAService()
            except Exception as exc:  # noqa: BLE001 - arranque a prueba de fallos
                app.logger.warning("G7: fallo al inicializar el repositorio: %s", exc)
                _servicio = SoAService(LocalSoA())
    return _servicio


def _respuesta(payload: Mapping[str, Any], status: int = 200):
    return app.response_class(
        response=app.json.dumps(_json_safe(payload), ensure_ascii=False),
        status=status,
        mimetype="application/json",
    )


def _temp_docx_path() -> str:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix="SoA_UNSA_", suffix=".docx", dir=str(RUNTIME_DIR))
    os.close(fd)
    return path


def _datos_word(entrada: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Extrae ``datos`` y el payload original para la exportación Word."""
    datos = entrada.get("datos")
    if isinstance(datos, Mapping) and ("soa" in datos or "soa_canonico" in datos):
        return datos, entrada
    return entrada, entrada


def _metadata_word(datos: Mapping[str, Any], entrada: Mapping[str, Any]) -> dict[str, Any]:
    perfil = entrada.get("perfil") if isinstance(entrada.get("perfil"), Mapping) else {}
    meta = datos.get("meta") if isinstance(datos.get("meta"), Mapping) else {}
    organizacion = (
        datos.get("organizacion")
        or perfil.get("organizacion")
        or os.getenv("G7_ORGANIZATION")
        or "Universidad Nacional de San Agustín de Arequipa (UNSA)"
    )
    return {
        "codigo": "SoA-UNSA-2026",
        "version": "1.0",
        "fecha": date.today().strftime("%d/%m/%Y"),
        "creado_por": "Oficialía de Protección de Datos (OPD)",
        "aprobado_por": "",
        "confidencialidad": "Uso interno",
        "organizacion": organizacion,
        "rol": meta.get("rol") if isinstance(meta, Mapping) else None,
    }


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

@app.after_request
def habilitar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.get("/")
def inicio():
    index = STATIC_DIR / "index.html"
    if index.is_file():
        return app.send_static_file("index.html")
    return _respuesta({
        "agente": AGENTE,
        "version": VERSION,
        "mensaje": "Agente G7 operativo. Use /api/controles/ejecutar.",
    })


@app.get("/api/health")
@app.get("/api/controles/salud")
def salud():
    try:
        estado = get_service().salud()
    except Exception as exc:  # noqa: BLE001 - salud nunca debe caerse
        estado = {"agente": AGENTE, "version": VERSION, "estado": "degradado",
                  "error": f"{type(exc).__name__}: {exc}"}
    return _respuesta(estado)


@app.route("/api/controles/catalogo", methods=["GET", "OPTIONS"])
def catalogo():
    if request.method == "OPTIONS":
        return "", 204
    try:
        datos = get_service().catalogo()
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("G7: catálogo no disponible: %s", exc)
        datos = []
    # El frontend espera una lista y el health check del orquestador solo
    # necesita un HTTP < 400; nunca devolvemos 500 por esta ruta.
    return _respuesta(datos)


@app.route("/api/controles/ejecutar", methods=["POST", "OPTIONS"])
def ejecutar():
    if request.method == "OPTIONS":
        return "", 204

    entrada = request.get_json(silent=True)
    if not isinstance(entrada, Mapping):
        entrada = {}

    try:
        resultado = get_service().ejecutar(entrada)
    except Exception as exc:  # noqa: BLE001 - contrato blindado
        app.logger.exception("G7: error no controlado en ejecutar")
        servicio = get_service()
        resultado = servicio._error_seguro(  # noqa: SLF001 - última red contractual
            str(entrada.get("operacion") or "consultar"),
            exc,
            entrada,
        )

    # Defensa adicional: el contrato exige ``datos.soa`` y ``datos.resumen``
    # en toda respuesta de ejecución. Si el servicio devolviera un sobre
    # incompleto, se completa sin alterar los campos específicos de la skill.
    if not isinstance(resultado, Mapping):
        resultado = {}
    datos = resultado.get("datos")
    if not isinstance(datos, Mapping):
        datos = {}
        resultado["datos"] = datos

    soa = datos.get("soa")
    if not isinstance(soa, list):
        soa = []
    validos = {"implementado", "parcial", "no implementado", "no aplica"}
    filas: list[dict[str, Any]] = []
    for fila in soa:
        if not isinstance(fila, Mapping):
            continue
        item = dict(fila)
        item.setdefault("control", "")
        estado = str(item.get("estado") or "")
        if estado not in validos:
            estado = "no aplica" if item.get("aplica") is False else "no implementado"
        item["estado"] = estado
        filas.append(item)
    datos["soa"] = filas

    resumen = datos.get("resumen")
    if not isinstance(resumen, Mapping):
        resumen = {
            "controles_evaluados": 0, "aplican": 0, "excluidos": 0,
            "implementados": 0, "parciales": 0, "no_implementados": 0,
        }
    datos["resumen"] = dict(resumen)
    datos.setdefault("soa_canonico", filas)
    datos.setdefault("brechas", [])

    return _respuesta(resultado)


@app.route("/api/controles/exportar-docx", methods=["POST", "OPTIONS"])
def exportar_docx():
    if request.method == "OPTIONS":
        return "", 204

    entrada = request.get_json(silent=True)
    if not isinstance(entrada, Mapping):
        entrada = {}

    ruta: str | None = None
    try:
        datos, original = _datos_word(entrada)
        soa = datos.get("soa_canonico") or datos.get("soa") or original.get("soa") or []
        riesgos = (
            datos.get("riesgos_residuales")
            or datos.get("riesgos")
            or original.get("riesgos_residuales")
            or original.get("riesgos")
            or []
        )

        # Si el cliente envía solo el perfil, se genera la SoA al vuelo.
        if not soa:
            generado = get_service().ejecutar({
                "operacion": "generar_soa",
                **{key: value for key, value in original.items() if key != "datos"},
            })
            datos = generado.get("datos") or {}
            soa = datos.get("soa_canonico") or datos.get("soa") or []
            riesgos = datos.get("riesgos_residuales") or riesgos

        # Red de seguridad: si la SoA existe pero no llegaron riesgos, cargarlos desde el repositorio
        if not riesgos:
            try:
                riesgos = get_service().repository.load_risks()
            except Exception:
                riesgos = []

        if not isinstance(soa, (list, tuple)) or not soa:
            return _respuesta({"error": "La SoA está vacía; genere la SoA antes de exportar."}, status=400)

        metadata = _metadata_word(datos, original)
        organizacion = metadata.get("organizacion")
        plantilla = Path(os.getenv("G7_SOA_TEMPLATE") or DEFAULT_TEMPLATE)
        ruta = _temp_docx_path()

        try:
            generar_soa_word(
                plantilla,
                ruta,
                soa,
                riesgos,
                metadata=metadata,
                organizacion=organizacion,
            )
        except Exception as exc:  # noqa: BLE001 - red de seguridad del docente
            app.logger.warning("G7: plantilla docente no disponible (%s); usando generador de respaldo", exc)
            from exportar_soa_docx import generar_documento_soa

            datos_respaldo = dict(datos)
            datos_respaldo.setdefault("soa", soa)
            datos_respaldo.setdefault("resumen", {})
            generar_documento_soa(datos_respaldo, ruta_salida=ruta)

        @after_this_request
        def _limpiar(response):
            try:
                os.unlink(ruta)
            except OSError:
                pass
            return response

        return send_file(
            ruta,
            as_attachment=True,
            download_name=DOWNLOAD_NAME,
            mimetype=DOCX_MIME,
        )
    except Exception as exc:  # noqa: BLE001 - nunca romper la descarga con 500
        app.logger.exception("G7: error generando el Word")
        if ruta:
            try:
                os.unlink(ruta)
            except OSError:
                pass
        return _respuesta({"error": f"No fue posible generar el documento: {type(exc).__name__}: {exc}"}, status=503)


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5007))
    print(f"Servidor Agente de Controles (G7) iniciado en http://127.0.0.1:{puerto}")
    app.run(host="0.0.0.0", port=puerto, debug=False)
