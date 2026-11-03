#!/usr/bin/env python3
"""
calcular_resultado.py — Agente 7 (Terceros/DPA) · v2.0

Completa de forma determinista los campos calculados de una evaluación DPA:
  - alertas de renovación/vencimiento del contrato (criterios §7)
  - resumen por estado
  - puntaje del proveedor 0-100 y desglose por dimensión (criterios §8)
  - dictamen global (criterios §5)
  - organización, jurisdicción y perfil aplicados (v2.0)
  - hash SHA-256 del documento (opcional)
y valida el resultado contra assets/esquema_salida.json (validador propio, sin dependencias).

Puntaje total, dictamen y alertas se calculan igual que en la v1.1: la v2.0 añade el contexto
(organización, jurisdicción, perfil) y la comprobación de coherencia de la política interna, y
desglosa el puntaje por las 5 secciones del Anexo A (antes, 4 dimensiones propias).

Uso:
  # con una organización (lee su config_organizacion.json y, si existe, su perfil_organizacion.md)
  python scripts/calcular_resultado.py resultado.json --org ../organizaciones/unsa

  # con un archivo de configuración concreto (compatible con la v1.1)
  python scripts/calcular_resultado.py resultado.json --config assets/config_organizacion.json

  Opciones: [--perfil perfil.md] [--jurisdicciones DIR] [--documento contrato.pdf]
            [--fecha-ref AAAA-MM-DD] [--salida resultado_final.json]

Códigos de salida: 0 correcto · 1 JSON escrito con errores de esquema · 2 entrada o contexto inválidos (nada escrito).
Solo usa la biblioteca estándar de Python 3.8+.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

VERSION_SCRIPT = "2.0"
SKILL_DIR = Path(__file__).resolve().parent.parent

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
ESTADOS_JURISDICCION_USABLES = {"Borrador", "En uso", "Verificada"}


class ErrorContexto(Exception):
    """Configuración, jurisdicción o perfil inválidos: se aborta sin escribir nada."""


# Dimensiones del desglose: las secciones del Anexo A de ISO/IEC 27701:2025 (Tablas A.2 y A.3),
# en el orden de la norma. Títulos parafraseados en español.
DIMENSIONES = [
    ("A.2.2", "Condiciones de recolección y tratamiento"),
    ("A.2.3", "Obligaciones con los titulares"),
    ("A.2.4", "Privacidad desde el diseño y por defecto"),
    ("A.2.5", "Compartición, transferencia y comunicación"),
    ("A.3", "Consideraciones de seguridad"),
]


def dimension(control: str) -> str:
    for sec, nombre in DIMENSIONES:
        if control.startswith(sec + "."):
            return nombre
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
    """Núcleo determinista. Idéntico a la v1.1 (verificado por la prueba de regresión)."""
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
    res["puntaje_proveedor"] = {
        "valor": valor, "banda": banda, "base": base, "penalizacion": penal,
        "por_dimension": {nombre: base_de([c for c in res["controles"] if dimension(c["control"]) == nombre])
                          for _, nombre in DIMENSIONES},
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


# ---------- Contexto v2.0: organización, jurisdicción y perfil ----------
def leer_json(ruta: Path, que: str) -> dict:
    if not ruta.is_file():
        raise ErrorContexto(f"No se encontró {que}: {ruta}")
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ErrorContexto(f"{que} no es JSON válido ({ruta}): {exc}") from exc


def cargar_jurisdiccion(cfg: dict, dir_jur: Path, advertencias: list) -> dict:
    jid = cfg.get("jurisdiccion")
    if not jid:
        jid = "peru"
        advertencias.append("La configuración no indica 'jurisdiccion'; se asumió 'peru' "
                            "(comportamiento de la v1.1).")
    params = leer_json(dir_jur / jid / "parametros_legales.json", f"la jurisdicción '{jid}'")
    if not (dir_jur / jid / "marco_legal.md").is_file():
        raise ErrorContexto(f"Falta marco_legal.md en la jurisdicción '{jid}' ({dir_jur / jid}).")
    estado = params.get("estado")
    if estado not in ESTADOS_JURISDICCION_USABLES:
        raise ErrorContexto(f"La jurisdicción '{jid}' está en estado {estado!r} y no se puede usar. "
                            f"Complétala y márcala como 'Borrador' o superior (ver jurisdicciones/LEEME.md).")
    if estado == "Borrador":
        advertencias.append(f"Jurisdicción '{jid}' en estado Borrador: pendiente de verificación legal.")
    return params


def leer_perfil(ruta: Path, advertencias: list) -> dict:
    texto = ruta.read_text(encoding="utf-8")

    def campo(nombre):
        m = re.search(rf"^\|\s*{nombre}\s*\|\s*(.+?)\s*\|\s*$", texto, flags=re.MULTILINE | re.IGNORECASE)
        return re.sub(r"[*`]", "", m.group(1)).strip() if m else None

    estado = campo("Estado")
    if not estado or not estado.lower().startswith("validado"):
        advertencias.append(f"Perfil de la organización sin validar por el DPO (estado: {estado or 'no indicado'}).")
    return {"ruta": str(ruta), "version": campo("Versión"), "estado": estado,
            "hash_sha256": hashlib.sha256(ruta.read_bytes()).hexdigest()}


def coherencia_politica(cfg: dict, jur: dict, advertencias: list) -> None:
    """La política interna debe dejar margen para cumplir la ley; si no, se advierte (no cambia el cálculo)."""
    interno = cfg.get("plazo_max_aviso_incidente_horas")
    legal = (jur.get("incidentes") or {}).get("plazo_notificacion_autoridad_horas")
    if isinstance(interno, (int, float)) and isinstance(legal, (int, float)) and interno >= legal:
        advertencias.append(
            f"Política interna incoherente con la ley: el plazo máximo de aviso del encargado "
            f"({interno} h) no es menor que el plazo legal de notificación a la autoridad ({legal} h).")


def aplicar_contexto(res: dict, cfg: dict, jur: dict, perfil, advertencias: list) -> dict:
    res["organizacion"] = {"id": cfg.get("id_organizacion", "sin id"),
                           "nombre": cfg.get("organizacion", "Organización usuaria"),
                           "perfil": perfil}
    res["jurisdiccion"] = {k: jur.get(k) for k in ("id", "pais", "ley_aplicable", "autoridad", "version", "estado")}
    traz = res["trazabilidad"]
    traz["version_jurisdiccion"] = f"{jur.get('id')} {jur.get('version')}"
    traz["version_perfil"] = perfil.get("version") if perfil else None
    previas = [a for a in traz.get("advertencias", []) if a not in advertencias]
    traz["advertencias"] = previas + advertencias
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
    grupo = ap.add_mutually_exclusive_group()
    grupo.add_argument("--org", help="Carpeta de la organización (con config_organizacion.json y, opcional, perfil_organizacion.md)")
    grupo.add_argument("--config", help="Archivo de configuración (por defecto assets/config_organizacion.json)")
    ap.add_argument("--perfil", help="Perfil de la organización (por defecto <org>/perfil_organizacion.md si existe)")
    ap.add_argument("--jurisdicciones", default=str(SKILL_DIR / "jurisdicciones"),
                    help="Carpeta de jurisdicciones (por defecto la de la skill)")
    ap.add_argument("--esquema", default=str(SKILL_DIR / "assets" / "esquema_salida.json"))
    ap.add_argument("--documento", help="Contrato evaluado, para calcular su hash SHA-256")
    ap.add_argument("--fecha-ref", help="Fecha de referencia AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--salida", help="Archivo de salida (por defecto sobrescribe el resultado)")
    a = ap.parse_args()

    advertencias = []
    try:
        if a.org:
            dir_org = Path(a.org)
            cfg = leer_json(dir_org / "config_organizacion.json", "la configuración de la organización")
            ruta_perfil = Path(a.perfil) if a.perfil else dir_org / "perfil_organizacion.md"
        else:
            cfg = leer_json(Path(a.config) if a.config else SKILL_DIR / "assets" / "config_organizacion.json",
                            "la configuración")
            ruta_perfil = Path(a.perfil) if a.perfil else None
        if a.perfil and not ruta_perfil.is_file():
            raise ErrorContexto(f"No se encontró el perfil: {ruta_perfil}")
        perfil = leer_perfil(ruta_perfil, advertencias) if ruta_perfil and ruta_perfil.is_file() else None
        jur = cargar_jurisdiccion(cfg, Path(a.jurisdicciones), advertencias)
        coherencia_politica(cfg, jur, advertencias)
        res = leer_json(Path(a.resultado), "el resultado a calcular")
    except ErrorContexto as exc:
        print(f"CONTEXTO INVÁLIDO (nada escrito):\n  {exc}")
        sys.exit(2)

    ref = date.fromisoformat(a.fecha_ref) if a.fecha_ref else date.today()

    if a.documento:
        res.setdefault("contrato", {})["hash_documento_sha256"] = hashlib.sha256(
            Path(a.documento).read_bytes()).hexdigest()
    if not res.get("marco_legal") and jur.get("marco_legal"):
        res["marco_legal"] = list(jur["marco_legal"])

    esquema = json.loads(Path(a.esquema).read_text(encoding="utf-8"))
    # Validación previa de lo que debe aportar el modelo (los campos calculados se excluyen)
    calculados = {"resumen", "puntaje_proveedor", "dictamen", "aprobacion", "organizacion", "jurisdiccion"}
    previo = dict(esquema, required=[k for k in esquema["required"] if k not in calculados],
                  properties={k: v for k, v in esquema["properties"].items() if k not in calculados})
    errores = [e for e in validar(res, previo) if "severidad" not in e and "ambito" not in e]
    if errores:
        print("ENTRADA INVÁLIDA (corrige y vuelve a ejecutar):\n  " + "\n  ".join(errores))
        sys.exit(2)

    res = calcular(res, cfg, ref)
    res = aplicar_contexto(res, cfg, jur, perfil, advertencias)
    errores = validar(res, esquema)
    Path(a.salida or a.resultado).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    # Solo caracteres ASCII en los separadores: evita UnicodeEncodeError en consolas cp1252 (Windows).
    p = res["puntaje_proveedor"]
    print(f"Puntaje: {p['valor']} ({p['banda']}) | base {p['base']} - {p['penalizacion']}")
    print(f"Dictamen: {res['dictamen']} | Resumen: {res['resumen']}")
    print(f"Organizacion: {res['organizacion']['nombre']} | Jurisdiccion: {jur.get('id')} ({jur.get('estado')})"
          f" | Perfil: {perfil['version'] if perfil else 'ninguno'}")
    for adv in advertencias:
        print(f"ADVERTENCIA: {adv}")
    if errores:
        print("ERRORES DE ESQUEMA:\n  " + "\n  ".join(errores))
        sys.exit(1)
    print("Esquema: valido")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")  # nunca abortar por la codificación de la consola
    except (AttributeError, ValueError):
        pass
    main()
