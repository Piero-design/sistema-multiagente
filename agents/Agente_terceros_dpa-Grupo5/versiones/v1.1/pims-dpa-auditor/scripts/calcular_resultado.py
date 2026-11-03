#!/usr/bin/env python3
"""
calcular_resultado.py — Agente 7 (Terceros/DPA) · v1.1

Completa de forma determinista los campos calculados de una evaluación DPA:
  - alertas de renovación/vencimiento del contrato (criterios §7)
  - resumen por estado
  - puntaje del proveedor 0-100 y desglose por dimensión (criterios §8)
  - dictamen global (criterios §5)
  - hash SHA-256 del documento (opcional)
y valida el resultado contra assets/esquema_salida.json (validador propio, sin dependencias).

Uso:
  python scripts/calcular_resultado.py resultado.json \
      --config assets/config_organizacion.json \
      [--documento contrato.pdf] [--fecha-ref AAAA-MM-DD] [--salida resultado_final.json]

Solo usa la biblioteca estándar de Python 3.8+.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

CRITICOS = {"A.2.2.2", "A.2.2.3", "A.2.4.3", "A.2.5.3", "A.2.5.7",
            "A.2.5.8", "A.2.5.9", "A.3.10", "A.3.12"}
PROPIOS_AGENTE_7 = {"A.1.2.7", "A.2.5.7", "A.2.5.8", "A.2.5.9", "A.3.10"}
FACTOR = {"Cumple": 1.0, "Parcial": 0.5, "Sin evidencia": 0.25, "No cumple": 0.0}
SEVERIDAD = {  # (estado, riesgo) -> severidad
    ("No cumple", "Alto"): "Crítica", ("No cumple", "Medio"): "Alta", ("No cumple", "Bajo"): "Media",
    ("Parcial", "Alto"): "Alta", ("Parcial", "Medio"): "Media", ("Parcial", "Bajo"): "Baja",
    ("Sin evidencia", "Alto"): "Alta", ("Sin evidencia", "Medio"): "Media", ("Sin evidencia", "Bajo"): "Baja",
}
ORDEN_DICTAMEN = ["Recomendable", "Recomendable con condiciones", "No recomendable sin enmiendas"]


def dimension(control: str) -> str:
    if control.startswith("A.2.2.") or control == "A.2.3.2":
        return "Contractual"
    if control.startswith("A.2.4."):
        return "Ciclo de vida del dato"
    if control.startswith("A.2.5."):
        return "Transferencias y sub-encargados"
    if control.startswith("A.3."):
        return "Seguridad e incidentes"
    return "Marco"


def parse_fecha(valor):
    return date.fromisoformat(valor) if valor else None


def alertas_renovacion(contrato: dict, ref: date, dias: int) -> list:
    alertas = []
    fin = parse_fecha(contrato.get("fecha_vigencia_fin"))
    renov = contrato.get("renovacion_automatica")
    preaviso = contrato.get("preaviso_terminacion_dias")
    ventana = ref + timedelta(days=dias)

    def nueva(prioridad, texto):
        alertas.append({"prioridad": prioridad, "tipo": "Renovación", "descripcion": texto,
                        "controles_relacionados": ["A.1.2.7"], "origen": "script"})

    if fin is None:
        nueva("Media", "Sin fecha de fin de vigencia ni mecanismo de revisión periódica definido.")
        return alertas
    if fin < ref and not renov:
        nueva("Alta", f"Contrato vencido el {fin.isoformat()} sin renovación automática.")
    elif fin <= ventana:
        nueva("Media", f"Fin de vigencia el {fin.isoformat()}, dentro de los próximos {dias} días.")
    if renov and preaviso is not None:
        limite = fin - timedelta(days=preaviso)
        if ref <= limite <= ventana:
            nueva("Media", f"Renovación automática: el plazo para preavisar termina el {limite.isoformat()}.")
    return alertas


def calcular(res: dict, cfg: dict, ref: date) -> dict:
    riesgo = res["nivel_riesgo_pii"]

    # Ámbito y severidad derivados de reglas (corrige inconsistencias del modelo)
    for c in res["controles"]:
        c["ambito"] = "Propio Agente 7" if c["control"] in PROPIOS_AGENTE_7 else "Insumo SoA (Agente 3)"
        c["severidad"] = SEVERIDAD.get((c["estado"], riesgo), "Ninguna")

    # Alertas de renovación: el script es dueño de las de origen "script"
    res["alertas"] = [a for a in res["alertas"] if a.get("origen") != "script"]
    res["alertas"] += alertas_renovacion(res["contrato"], ref, cfg.get("dias_alerta_renovacion", 60))

    # Resumen
    estados = [c["estado"] for c in res["controles"]]
    altas = sum(1 for a in res["alertas"] if a["prioridad"] == "Alta")
    res["resumen"] = {
        "cumple": estados.count("Cumple"), "parcial": estados.count("Parcial"),
        "no_cumple": estados.count("No cumple"), "sin_evidencia": estados.count("Sin evidencia"),
        "no_aplica": estados.count("No aplica"), "alertas_altas": altas,
    }

    # Puntaje
    def base_de(controles):
        num = den = 0.0
        for c in controles:
            if c["estado"] == "No aplica":
                continue
            peso = 3 if c["control"] in CRITICOS else 1
            num += peso * FACTOR[c["estado"]]
            den += peso
        return round(num / den * 100, 1) if den else None

    base = base_de(res["controles"])
    penal = min(5 * altas, 20)
    valor = max(0, round((base or 0) - penal))
    banda = "Riesgo bajo" if valor >= 80 else "Riesgo medio" if valor >= 50 else "Riesgo alto"
    dims = {}
    for c in res["controles"]:
        dims.setdefault(dimension(c["control"]), []).append(c)
    res["puntaje_proveedor"] = {
        "valor": valor, "banda": banda, "base": base, "penalizacion": penal,
        "por_dimension": {k: base_de(v) for k, v in dims.items() if k != "Marco"},
    }

    # Dictamen: la más desfavorable entre regla A y regla B
    sevs = {c["severidad"] for c in res["controles"]}
    if altas or "Crítica" in sevs:
        regla_a = "No recomendable sin enmiendas"
    elif sevs & {"Alta", "Media"}:
        regla_a = "Recomendable con condiciones"
    else:
        regla_a = "Recomendable"
    regla_b = ("Recomendable" if valor >= 80 else
               "Recomendable con condiciones" if valor >= 50 else "No recomendable sin enmiendas")
    res["dictamen"] = max(regla_a, regla_b, key=ORDEN_DICTAMEN.index)

    # Aprobación y trazabilidad
    res["aprobacion"] = {"requiere_decision_dpo": True, "requiere_aprobacion_legal": True,
                         "secuencia": cfg.get("aprobadores", ["DPO", "Legal"]),
                         "estado": res.get("aprobacion", {}).get("estado", "Pendiente DPO")}
    res["contrato"]["estado_dpa"] = res["contrato"].get("estado_dpa") or "Pendiente DPO"
    traz = res.setdefault("trazabilidad", {})
    traz["version_config"] = cfg.get("version_config", "sin versión")
    traz["calculo"] = "script"
    traz["parametros_aplicados"] = {k: v for k, v in cfg.items()
                                    if not k.startswith("_") and k not in ("paises_aprobados",)}
    traz["parametros_aplicados"]["n_paises_aprobados"] = len(cfg.get("paises_aprobados", []))
    traz["fecha_referencia"] = ref.isoformat()
    return res


# ---------- Validador mínimo de JSON Schema (subconjunto usado en el esquema) ----------
def validar(dato, esquema, ruta="$"):
    errores = []
    tipos = esquema.get("type")
    if tipos:
        tipos = tipos if isinstance(tipos, list) else [tipos]
        mapa = {"object": dict, "array": list, "string": str, "integer": int,
                "number": (int, float), "boolean": bool, "null": type(None)}
        ok = any(isinstance(dato, mapa[t]) and not (t in ("integer", "number") and isinstance(dato, bool))
                 for t in tipos)
        if not ok:
            return [f"{ruta}: tipo {type(dato).__name__} no es {tipos}"]
    if "const" in esquema and dato != esquema["const"]:
        errores.append(f"{ruta}: debe ser {esquema['const']!r}")
    if "enum" in esquema and dato not in esquema["enum"]:
        errores.append(f"{ruta}: {dato!r} no está en {esquema['enum']}")
    if isinstance(dato, str) and "pattern" in esquema and not re.match(esquema["pattern"], dato):
        errores.append(f"{ruta}: {dato!r} no cumple el patrón")
    if isinstance(dato, (int, float)) and not isinstance(dato, bool):
        if "minimum" in esquema and dato < esquema["minimum"]:
            errores.append(f"{ruta}: menor que {esquema['minimum']}")
        if "maximum" in esquema and dato > esquema["maximum"]:
            errores.append(f"{ruta}: mayor que {esquema['maximum']}")
    if isinstance(dato, dict):
        for req in esquema.get("required", []):
            if req not in dato:
                errores.append(f"{ruta}: falta '{req}'")
        for k, sub in esquema.get("properties", {}).items():
            if k in dato:
                errores += validar(dato[k], sub, f"{ruta}.{k}")
    if isinstance(dato, list):
        if len(dato) < esquema.get("minItems", 0):
            errores.append(f"{ruta}: mínimo {esquema['minItems']} elementos")
        if "items" in esquema:
            for i, el in enumerate(dato):
                errores += validar(el, esquema["items"], f"{ruta}[{i}]")
    return errores


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("resultado")
    ap.add_argument("--config", required=True)
    ap.add_argument("--esquema", default=str(Path(__file__).resolve().parent.parent / "assets" / "esquema_salida.json"))
    ap.add_argument("--documento", help="Contrato evaluado, para calcular su hash SHA-256")
    ap.add_argument("--fecha-ref", help="Fecha de referencia AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--salida", help="Archivo de salida (por defecto sobrescribe el resultado)")
    a = ap.parse_args()

    res = json.loads(Path(a.resultado).read_text(encoding="utf-8"))
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    ref = date.fromisoformat(a.fecha_ref) if a.fecha_ref else date.today()

    if a.documento:
        res.setdefault("contrato", {})["hash_documento_sha256"] = hashlib.sha256(
            Path(a.documento).read_bytes()).hexdigest()

    esquema = json.loads(Path(a.esquema).read_text(encoding="utf-8"))
    # Validación previa de lo que debe aportar el modelo (los campos calculados se excluyen)
    calculados = {"resumen", "puntaje_proveedor", "dictamen", "aprobacion"}
    previo = dict(esquema, required=[k for k in esquema["required"] if k not in calculados],
                  properties={k: v for k, v in esquema["properties"].items() if k not in calculados})
    errores = [e for e in validar(res, previo) if "severidad" not in e and "ambito" not in e]
    if errores:
        print("ENTRADA INVÁLIDA (corrige y vuelve a ejecutar):\n  " + "\n  ".join(errores))
        sys.exit(2)

    res = calcular(res, cfg, ref)
    errores = validar(res, esquema)
    Path(a.salida or a.resultado).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    p = res["puntaje_proveedor"]
    print(f"Puntaje: {p['valor']} ({p['banda']}) | base {p['base']} − {p['penalizacion']}")
    print(f"Dictamen: {res['dictamen']} | Resumen: {res['resumen']}")
    if errores:
        print("ERRORES DE ESQUEMA:\n  " + "\n  ".join(errores))
        sys.exit(1)
    print("Esquema: válido")


if __name__ == "__main__":
    main()
