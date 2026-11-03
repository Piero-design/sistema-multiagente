#!/usr/bin/env python3
"""
equivalencia_py_js.py — Demuestra que n8n/lib/calcular.js calcula EXACTAMENTE lo mismo
que pims-dpa-auditor/scripts/calcular_resultado.py.

    python n8n/pruebas/equivalencia_py_js.py [--casos 3000]

Compara, caso por caso, todos los campos calculados (resumen, puntaje, dictamen, severidades,
ámbitos, alertas de renovación, aprobación, organización, jurisdicción, advertencias, hash):
  1. Los 5 registros de referencia (22 / 100 / 0 / 22 / 100).
  2. Variantes de contexto: perfil, perfil contaminado, jurisdicción en borrador, config v1.1,
     política incoherente, hash del contrato.
  3. N casos aleatorios: estados de control, riesgo PII, fechas de vigencia, renovación,
     preaviso y alertas al azar (incluye empates de redondeo como 22.5).

Requiere Node.js (el mismo que usa n8n). Código de salida 0 si no hay diferencias.
"""
import argparse
import copy
import importlib.util
import json
import random
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SKILL = RAIZ / "pims-dpa-auditor"
PRUEBAS = RAIZ / "pims-dpa-auditor_pruebas"

spec = importlib.util.spec_from_file_location("calc", SKILL / "scripts" / "calcular_resultado.py")
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)

ESQUEMA = json.loads((SKILL / "assets" / "esquema_salida.json").read_text(encoding="utf-8"))
CFG = json.loads((SKILL / "assets" / "config_organizacion.json").read_text(encoding="utf-8"))
CFG_V11 = json.loads((RAIZ / "versiones/v1.1/pims-dpa-auditor/assets/config_organizacion.json").read_text(encoding="utf-8"))
JUR = json.loads((SKILL / "jurisdicciones/peru/parametros_legales.json").read_text(encoding="utf-8"))
PERFIL = PRUEBAS / "organizaciones_prueba/altiplano_con_perfil/perfil_organizacion.md"
PERFIL_CONT = PRUEBAS / "organizaciones_prueba/perfil_contaminado.md"
CONTRATO = PRUEBAS / "contratos/dpa_nubeandina.md"


def python_ejecutar(caso):
    """Reproduce main() del script sin subprocess, para comparar campo a campo."""
    adv = []
    perfil = None
    if caso.get("perfil"):
        ruta = Path(caso["perfil"]["ruta_real"])
        perfil = calc.leer_perfil(ruta, adv)
        perfil["ruta"] = caso["perfil"]["ruta"]
    try:
        jur = calc.cargar_jurisdiccion_dict(caso["config"], caso["jurisdiccion"], adv)
    except calc.ErrorContexto:
        return {"codigo": 2}
    calc.coherencia_politica(caso["config"], jur, adv)
    res = copy.deepcopy(caso["resultado"])
    if caso.get("documento") is not None:
        res.setdefault("contrato", {})["hash_documento_sha256"] = __import__("hashlib").sha256(
            caso["documento"].encode("utf-8")).hexdigest()
    if not res.get("marco_legal") and jur.get("marco_legal"):
        res["marco_legal"] = list(jur["marco_legal"])
    res = calc.calcular(res, caso["config"], date.fromisoformat(caso["fechaRef"]))
    res = calc.aplicar_contexto(res, caso["config"], jur, perfil, adv)
    errores = calc.validar(res, ESQUEMA)
    return {"codigo": 1 if errores else 0, "resultado": res, "advertencias": adv}


# cargar_jurisdiccion del script lee de disco; aquí se replica con el dict en memoria
def _cargar_dict(cfg, params, adv):
    jid = cfg.get("jurisdiccion")
    if not jid:
        jid = "peru"
        adv.append("La configuración no indica 'jurisdiccion'; se asumió 'peru' (comportamiento de la v1.1).")
    estado = params.get("estado")
    if estado not in calc.ESTADOS_JURISDICCION_USABLES:
        raise calc.ErrorContexto(estado)
    if estado == "Borrador":
        adv.append(f"Jurisdicción '{jid}' en estado Borrador: pendiente de verificación legal.")
    return params


calc.cargar_jurisdiccion_dict = _cargar_dict


def js_ejecutar(casos):
    lote = {"esquema": ESQUEMA, "casos": [
        {k: v for k, v in c.items() if k != "perfil"} | (
            {"perfil": {"texto": Path(c["perfil"]["ruta_real"]).read_text(encoding="utf-8"), "ruta": c["perfil"]["ruta"]}}
            if c.get("perfil") else {})
        for c in casos]}
    p = subprocess.run(["node", str(Path(__file__).parent / "ejecutar_js.js")], input=json.dumps(lote),
                       capture_output=True, text=True, encoding="utf-8")
    if p.returncode:
        sys.exit(f"Error al ejecutar Node: {p.stderr}")
    return json.loads(p.stdout)


def normal(x):
    """Normaliza números (100.0 == 100) para comparar Python y JS."""
    return json.loads(json.dumps(x), parse_float=lambda s: float(s) if "." in s or "e" in s.lower() else int(s),
                      parse_int=float)


def comparar(py, js):
    if py["codigo"] != js["codigo"]:
        return f"código {py['codigo']} vs {js['codigo']}"
    if py["codigo"] == 2:
        return None
    a, b = normal(py["resultado"]), normal(js["resultado"])
    for clave in sorted(set(a) | set(b)):
        if a.get(clave) != b.get(clave):
            return f"campo '{clave}' difiere:\n    py={json.dumps(a.get(clave), ensure_ascii=False)[:300]}\n    js={json.dumps(b.get(clave), ensure_ascii=False)[:300]}"
    if py["advertencias"] != js["advertencias"]:
        return f"advertencias difieren: {py['advertencias']} vs {js['advertencias']}"
    return None


ESTADOS = ["Cumple", "Parcial", "No cumple", "Sin evidencia", "No aplica"]
CONTROLES = ["A.1.2.7", "A.2.2.2", "A.2.2.3", "A.2.2.4", "A.2.2.5", "A.2.2.6", "A.2.2.7", "A.2.3.2",
             "A.2.4.2", "A.2.4.3", "A.2.4.4", "A.2.5.2", "A.2.5.3", "A.2.5.4", "A.2.5.5", "A.2.5.6",
             "A.2.5.7", "A.2.5.8", "A.2.5.9", "A.3.9", "A.3.10", "A.3.11", "A.3.12", "A.3.13", "A.3.15", "A.3.18", "A.3.24"]


def aleatorio(base, rnd):
    r = copy.deepcopy(base)
    r["nivel_riesgo_pii"] = rnd.choice(["Alto", "Medio", "Bajo"])
    n = rnd.randint(1, len(CONTROLES))
    pesos = rnd.choice([[1] * 5, [6, 1, 1, 1, 1], [1, 1, 6, 1, 0], [1, 6, 1, 1, 1], [1, 1, 1, 6, 1]])
    r["controles"] = [{"control": c, "titulo": "t", "ambito": "Insumo SoA (Agente 3)", "clausula_dpa": "x",
                       "estado": rnd.choices(ESTADOS, weights=pesos)[0], "severidad": "Ninguna",
                       "fuente_requisito": "ISO 27701"} for c in rnd.sample(CONTROLES, n)]
    r["alertas"] = [{"prioridad": rnd.choice(["Alta", "Media"]), "tipo": "Riesgo", "descripcion": "d",
                     "origen": rnd.choice(["modelo", "script"])} for _ in range(rnd.randint(0, 6))]
    ref = date(2026, 10, 1) + timedelta(days=rnd.randint(-400, 400))
    fin = None if rnd.random() < 0.15 else ref + timedelta(days=rnd.randint(-120, 200))
    c = r["contrato"]
    c["fecha_vigencia_fin"] = fin.isoformat() if fin else None
    c["renovacion_automatica"] = rnd.choice([True, False, None])
    c["preaviso_terminacion_dias"] = rnd.choice([None, 0, 15, 30, 60, 90])
    c["estado_dpa"] = rnd.choice(["Pendiente DPO", "Pendiente Legal", "En evaluación"])
    if rnd.random() < 0.2:
        r.pop("aprobacion", None)
    return r, ref.isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", type=int, default=3000)
    ap.add_argument("--semilla", type=int, default=29733)
    a = ap.parse_args()

    refs = [(PRUEBAS / "resultados" / f"resultado_{n}.json", "2026-10-01") for n in ("NubeAndina", "AndesCloud", "DigiServ")]
    refs += [(PRUEBAS / "ejecuciones_2026-10-07" / f"resultado_{n}.json", "2026-10-07") for n in ("NubeAndina", "AndesCloud")]
    casos, nombres = [], []
    for ruta, f in refs:
        casos.append({"resultado": json.loads(ruta.read_text(encoding="utf-8")), "config": CFG, "jurisdiccion": JUR, "fechaRef": f})
        nombres.append(f"referencia {ruta.parent.name}/{ruta.name}")

    nube = json.loads(refs[0][0].read_text(encoding="utf-8"))
    jur_borrador = dict(JUR, estado="Borrador")
    variantes = [
        ("perfil de referencia", {"perfil": {"ruta": "perfil_organizacion.md", "ruta_real": str(PERFIL)}}),
        ("perfil contaminado", {"perfil": {"ruta": "perfil_contaminado.md", "ruta_real": str(PERFIL_CONT)}}),
        ("jurisdicción en Borrador", {"jurisdiccion": jur_borrador}),
        ("jurisdicción en Plantilla (rechazo)", {"jurisdiccion": dict(JUR, estado="Plantilla")}),
        ("config v1.1 sin 'jurisdiccion'", {"config": CFG_V11}),
        ("política incoherente 72 h", {"config": dict(CFG, plazo_max_aviso_incidente_horas=72)}),
        ("hash del contrato", {"documento": CONTRATO.read_text(encoding="utf-8")}),
    ]
    for nombre, cambios in variantes:
        caso = {"resultado": nube, "config": CFG, "jurisdiccion": JUR, "fechaRef": "2026-10-01"}
        caso.update(cambios)
        casos.append(caso)
        nombres.append(f"variante: {nombre}")

    rnd = random.Random(a.semilla)
    for i in range(a.casos):
        r, f = aleatorio(nube, rnd)
        casos.append({"resultado": r, "config": rnd.choice([CFG, dict(CFG, dias_alerta_renovacion=rnd.choice([30, 60, 90]))]),
                      "jurisdiccion": JUR, "fechaRef": f})
        nombres.append(f"aleatorio #{i}")

    js = js_ejecutar(casos)
    fallas = 0
    empates = 0
    for nombre, caso, salida_js in zip(nombres, casos, js):
        py = python_ejecutar(caso)
        if py["codigo"] in (0, 1):
            b = py["resultado"]["puntaje_proveedor"]["base"] or 0
            if (b - py["resultado"]["puntaje_proveedor"]["penalizacion"]) % 1 == 0.5:
                empates += 1
        dif = comparar(py, salida_js)
        if dif:
            fallas += 1
            if fallas <= 5:
                print(f"DIFERENCIA en {nombre}: {dif}")
    print(f"Casos comparados: {len(casos)} ({len(refs)} de referencia, {len(variantes)} variantes, {a.casos} aleatorios)")
    print(f"Casos con empate de redondeo (x.5): {empates}")
    print("Resultado: IDÉNTICOS" if not fallas else f"Resultado: {fallas} DIFERENCIAS")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
