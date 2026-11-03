#!/usr/bin/env python3
"""
ejecutar_pruebas.py — Pruebas automáticas de la parte determinista (v2.0).

Ejecutar desde la raíz del proyecto o desde cualquier carpeta:
    python pims-dpa-auditor_pruebas/ejecutar_pruebas.py

Qué verifica (sin modelo de IA; todo es reproducible):
  A. Regresión: la v2.0 da exactamente los mismos campos calculados que la v1.1, salvo el
     desglose por dimensión (ahora las 5 secciones del Anexo A), que se verifica aparte
     (22 / 100 / 0 con fecha 2026-10-01 y las ejecuciones del 2026-10-07).
  B. Jurisdicción intercambiable: carga, estados (Plantilla / Borrador), errores.
  C. Coherencia de la política interna con la ley.
  D. Perfil de organización: hash y versión registrados, y que NO altera el cálculo.
  E. Validador de perfiles: acepta el perfil de referencia, rechaza el contaminado y la plantilla.
  F. Compatibilidad: config v1.1, fuentes de requisito antiguas y nuevas, consola cp1252.
  G. Archivos referenciados por casos_de_prueba.json existen.

Solo biblioteca estándar. Código de salida 0 si todo pasa.
"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRUEBAS = RAIZ / "pims-dpa-auditor_pruebas"
SCRIPT_V2 = RAIZ / "pims-dpa-auditor" / "scripts" / "calcular_resultado.py"
SCRIPT_V11 = RAIZ / "versiones" / "v1.1" / "pims-dpa-auditor" / "scripts" / "calcular_resultado.py"
CONFIG_V11 = RAIZ / "versiones" / "v1.1" / "pims-dpa-auditor" / "assets" / "config_organizacion.json"
VALIDADOR = RAIZ / "pims-perfilador-organizacion" / "scripts" / "validar_perfil.py"
ORG_ALTIPLANO = RAIZ / "organizaciones" / "inversiones_altiplano"
ORG_PERFIL = PRUEBAS / "organizaciones_prueba" / "altiplano_con_perfil"

REFERENCIAS = [  # (archivo, fecha de referencia, puntaje esperado, dictamen esperado)
    (PRUEBAS / "resultados" / "resultado_NubeAndina.json", "2026-10-01", 22, "No recomendable sin enmiendas"),
    (PRUEBAS / "resultados" / "resultado_AndesCloud.json", "2026-10-01", 100, "Recomendable"),
    (PRUEBAS / "resultados" / "resultado_DigiServ.json", "2026-10-01", 0, "No recomendable sin enmiendas"),
    (PRUEBAS / "ejecuciones_2026-10-07" / "resultado_NubeAndina.json", "2026-10-07", 22, "No recomendable sin enmiendas"),
    (PRUEBAS / "ejecuciones_2026-10-07" / "resultado_AndesCloud.json", "2026-10-07", 100, "Recomendable"),
]

TMP = Path(tempfile.mkdtemp(prefix="pims_pruebas_"))
resultados = []


def correr(script, entrada, *args, env_extra=None):
    """Copia la entrada a un temporal, ejecuta el script y devuelve (código, salida, json_resultante)."""
    destino = TMP / f"r_{len(resultados)}_{entrada.name}"
    shutil.copy(entrada, destino)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, str(script), str(destino), *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    datos = json.loads(destino.read_text(encoding="utf-8"))
    return p.returncode, p.stdout + p.stderr, datos


def nucleo(r, con_dimensiones=False):
    """Campos que calcula el script: deben ser idénticos entre v1.1 y v2.0.
    El desglose por dimensión cambió en v2.0 (5 secciones del Anexo A en lugar de 4 dimensiones
    propias), así que se compara aparte; total, dictamen y todo lo demás deben seguir iguales."""
    puntaje = dict(r.get("puntaje_proveedor") or {})
    if not con_dimensiones:
        puntaje.pop("por_dimension", None)
    return {
        "resumen": r.get("resumen"), "puntaje": puntaje, "dictamen": r.get("dictamen"),
        "controles": [(c["control"], c["estado"], c["severidad"], c["ambito"]) for c in r["controles"]],
        "alertas": r.get("alertas"), "aprobacion": r.get("aprobacion"),
        "estado_dpa": r["contrato"].get("estado_dpa"),
    }


def prueba(nombre):
    def deco(f):
        try:
            detalle = f()
            resultados.append((True, nombre, detalle or ""))
        except AssertionError as exc:
            resultados.append((False, nombre, str(exc)))
        except Exception as exc:  # noqa: BLE001
            resultados.append((False, nombre, f"{type(exc).__name__}: {exc}"))
        return f
    return deco


# ---------------------------------------------------------------- A. Regresión
for archivo, fecha, puntaje, dictamen in REFERENCIAS:
    etiqueta = f"{archivo.parent.name}/{archivo.name}"

    @prueba(f"A. Regresión v1.1 = v2.0 · {etiqueta}")
    def _(archivo=archivo, fecha=fecha, puntaje=puntaje, dictamen=dictamen):
        c1, s1, r1 = correr(SCRIPT_V11, archivo, "--config", CONFIG_V11, "--fecha-ref", fecha)
        c2, s2, r2 = correr(SCRIPT_V2, archivo, "--fecha-ref", fecha)
        c3, s3, r3 = correr(SCRIPT_V2, archivo, "--org", ORG_ALTIPLANO, "--fecha-ref", fecha)
        assert c1 == 0, f"v1.1 terminó con código {c1}: {s1}"
        assert c2 == 0, f"v2.0 (config por defecto) terminó con código {c2}: {s2}"
        assert c3 == 0, f"v2.0 (--org) terminó con código {c3}: {s3}"
        assert nucleo(r1) == nucleo(r2), "v2.0 (config por defecto) difiere de v1.1"
        assert nucleo(r1) == nucleo(r3), "v2.0 (--org inversiones_altiplano) difiere de v1.1"
        if archivo.parent.name == "resultados":
            ref = json.loads(archivo.read_text(encoding="utf-8"))
            assert nucleo(ref, True) == nucleo(r2, True), "v2.0 difiere del resultado de referencia guardado"
        assert r2["puntaje_proveedor"]["valor"] == puntaje, f"puntaje {r2['puntaje_proveedor']['valor']} != {puntaje}"
        assert r2["dictamen"] == dictamen, f"dictamen {r2['dictamen']!r}"
        assert r2["jurisdiccion"]["id"] == "peru" and r2["trazabilidad"]["calculo"] == "script"
        return f"{puntaje}/100 · {dictamen}"

SECCIONES = [("A.2.2", "Condiciones de recolección y tratamiento"), ("A.2.3", "Obligaciones con los titulares"),
             ("A.2.4", "Privacidad desde el diseño y por defecto"),
             ("A.2.5", "Compartición, transferencia y comunicación"), ("A.3", "Consideraciones de seguridad")]


@prueba("A. Desglose: las 5 secciones del Anexo A, en orden, recalculadas a mano")
def _():
    archivo, fecha = REFERENCIAS[0][0], REFERENCIAS[0][1]
    c, s, r = correr(SCRIPT_V2, archivo, "--fecha-ref", fecha)
    assert c == 0, s
    dims = r["puntaje_proveedor"]["por_dimension"]
    assert list(dims) == [n for _, n in SECCIONES], f"claves {list(dims)}"
    factor = {"Cumple": 1.0, "Parcial": 0.5, "Sin evidencia": 0.25, "No cumple": 0.0}
    criticos = {"A.2.2.2", "A.2.2.3", "A.2.4.3", "A.2.5.3", "A.2.5.7", "A.2.5.8", "A.2.5.9", "A.3.10", "A.3.12"}
    for sec, nombre in SECCIONES:
        cs = [x for x in r["controles"] if x["control"].startswith(sec + ".") and x["estado"] != "No aplica"]
        den = sum(3 if x["control"] in criticos else 1 for x in cs)
        num = sum((3 if x["control"] in criticos else 1) * factor[x["estado"]] for x in cs)
        esperado = round(num / den * 100, 1) if den else None
        assert dims[nombre] == esperado, f"{nombre}: {dims[nombre]} != {esperado}"
    return " · ".join(f"{s} {dims[n]}" for s, n in SECCIONES)


NUBE = REFERENCIAS[0][0]
ANDES = REFERENCIAS[1][0]


def jurisdicciones_temporales(estado=None, borrar_marco=False, jid="peru"):
    d = TMP / f"jur_{len(resultados)}"
    shutil.copytree(RAIZ / "pims-dpa-auditor" / "jurisdicciones", d)
    if jid != "peru":
        shutil.copytree(d / "peru", d / jid)
    p = d / jid / "parametros_legales.json"
    params = json.loads(p.read_text(encoding="utf-8"))
    params["id"] = jid
    if estado:
        params["estado"] = estado
    p.write_text(json.dumps(params, ensure_ascii=False), encoding="utf-8")
    if borrar_marco:
        (d / jid / "marco_legal.md").unlink()
    return d


def config_temporal(**cambios):
    cfg = json.loads((RAIZ / "pims-dpa-auditor" / "assets" / "config_organizacion.json").read_text(encoding="utf-8"))
    for k, v in cambios.items():
        if v is None:
            cfg.pop(k, None)
        else:
            cfg[k] = v
    p = TMP / f"cfg_{len(resultados)}.json"
    p.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return p


# ---------------------------------------------------------------- B. Jurisdicción
@prueba("B. Jurisdicción en estado 'Plantilla' → se rechaza (código 2, nada escrito)")
def _():
    original = NUBE.read_text(encoding="utf-8")
    c, s, r = correr(SCRIPT_V2, NUBE, "--jurisdicciones", jurisdicciones_temporales("Plantilla"), "--fecha-ref", "2026-10-01")
    assert c == 2, f"código {c}"
    assert "CONTEXTO INV" in s and "Plantilla" in s, s
    assert json.dumps(r, ensure_ascii=False, indent=2) == json.dumps(json.loads(original), ensure_ascii=False, indent=2), \
        "el archivo de resultado fue modificado"


@prueba("B. Jurisdicción inexistente → se rechaza (código 2)")
def _():
    c, s, _ = correr(SCRIPT_V2, NUBE, "--config", config_temporal(jurisdiccion="atlantida"), "--fecha-ref", "2026-10-01")
    assert c == 2 and "atlantida" in s, s


@prueba("B. Jurisdicción sin marco_legal.md → se rechaza (código 2)")
def _():
    c, s, _ = correr(SCRIPT_V2, NUBE, "--jurisdicciones", jurisdicciones_temporales(borrar_marco=True), "--fecha-ref", "2026-10-01")
    assert c == 2 and "marco_legal.md" in s, s


@prueba("B. Jurisdicción en 'Borrador' → se usa con advertencia y no cambia el cálculo")
def _():
    c, s, r = correr(SCRIPT_V2, NUBE, "--jurisdicciones", jurisdicciones_temporales("Borrador"), "--fecha-ref", "2026-10-01")
    assert c == 0, s
    assert any("Borrador" in a for a in r["trazabilidad"]["advertencias"]), r["trazabilidad"]
    assert r["jurisdiccion"]["estado"] == "Borrador"
    assert r["puntaje_proveedor"]["valor"] == 22


@prueba("B. Otra jurisdicción (id 'pais_x') se selecciona por la configuración")
def _():
    jur = jurisdicciones_temporales("Borrador", jid="pais_x")
    c, s, r = correr(SCRIPT_V2, NUBE, "--config", config_temporal(jurisdiccion="pais_x"),
                     "--jurisdicciones", jur, "--fecha-ref", "2026-10-01")
    assert c == 0, s
    assert r["jurisdiccion"]["id"] == "pais_x", r["jurisdiccion"]
    assert r["trazabilidad"]["version_jurisdiccion"].startswith("pais_x")


# ---------------------------------------------------------------- C. Coherencia
@prueba("C. Plazo interno ≥ plazo legal (72 h vs 48 h) → advertencia, cálculo intacto")
def _():
    c, s, r = correr(SCRIPT_V2, NUBE, "--config", config_temporal(plazo_max_aviso_incidente_horas=72), "--fecha-ref", "2026-10-01")
    assert c == 0, s
    assert any("incoherente" in a for a in r["trazabilidad"]["advertencias"]), r["trazabilidad"]["advertencias"]
    assert r["puntaje_proveedor"]["valor"] == 22


@prueba("C. Plazo interno coherente (24 h vs 48 h) → sin advertencias")
def _():
    c, s, r = correr(SCRIPT_V2, NUBE, "--fecha-ref", "2026-10-01")
    assert c == 0 and r["trazabilidad"]["advertencias"] == [], r["trazabilidad"]["advertencias"]


# ---------------------------------------------------------------- D. Perfil
@prueba("D. --org con perfil → registra versión, estado y SHA-256 del perfil")
def _():
    c, s, r = correr(SCRIPT_V2, NUBE, "--org", ORG_PERFIL, "--fecha-ref", "2026-10-01")
    assert c == 0, s
    perfil = r["organizacion"]["perfil"]
    esperado = hashlib.sha256((ORG_PERFIL / "perfil_organizacion.md").read_bytes()).hexdigest()
    assert perfil["hash_sha256"] == esperado, perfil
    assert perfil["version"] == "0.1" and perfil["estado"] == "Borrador", perfil
    assert r["trazabilidad"]["version_perfil"] == "0.1"
    assert any("sin validar" in a for a in r["trazabilidad"]["advertencias"])
    assert r["organizacion"]["id"] == "altiplano_con_perfil"


@prueba("D. El perfil no altera el cálculo (asimetría a nivel de script)")
def _():
    _, _, sin = correr(SCRIPT_V2, NUBE, "--org", ORG_ALTIPLANO, "--fecha-ref", "2026-10-01")
    _, _, con = correr(SCRIPT_V2, NUBE, "--org", ORG_PERFIL, "--fecha-ref", "2026-10-01")
    _, _, cont = correr(SCRIPT_V2, NUBE, "--org", ORG_PERFIL, "--perfil",
                        PRUEBAS / "organizaciones_prueba" / "perfil_contaminado.md", "--fecha-ref", "2026-10-01")
    assert nucleo(sin) == nucleo(con) == nucleo(cont), "el perfil cambió algún campo calculado"
    return "22/100 con y sin perfil, también con el perfil contaminado"


@prueba("D. Riesgo PII elevado por el perfil (Medio→Alto) en un contrato conforme mantiene 100/100")
def _():
    r = json.loads(ANDES.read_text(encoding="utf-8"))
    r["nivel_riesgo_pii"] = "Alto"
    p = TMP / "andes_alto.json"
    p.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    c, s, out = correr(SCRIPT_V2, p, "--org", ORG_PERFIL, "--fecha-ref", "2026-10-01")
    assert c == 0, s
    assert out["puntaje_proveedor"]["valor"] == 100 and out["dictamen"] == "Recomendable", out["dictamen"]
    assert {c["severidad"] for c in out["controles"]} == {"Ninguna"}


@prueba("D. Perfil indicado con --perfil inexistente → se rechaza (código 2)")
def _():
    c, s, _ = correr(SCRIPT_V2, NUBE, "--perfil", TMP / "no_existe.md", "--fecha-ref", "2026-10-01")
    assert c == 2, s


# ---------------------------------------------------------------- E. Validador de perfiles
def validar_perfil(ruta):
    p = subprocess.run([sys.executable, str(VALIDADOR), str(ruta), "--json"], capture_output=True,
                       text=True, encoding="utf-8")
    return p.returncode, json.loads(p.stdout)


@prueba("E. Perfil de referencia (altiplano_con_perfil) → formato válido")
def _():
    c, r = validar_perfil(ORG_PERFIL / "perfil_organizacion.md")
    assert c == 0 and r["valido"], r["errores"]
    assert r["documentos"] == 2
    return f"{len(r['advertencias'])} advertencia(s): {r['advertencias'][0]}"


@prueba("E. Perfil contaminado ('homologado, no requiere DPA') → rechazado")
def _():
    c, r = validar_perfil(PRUEBAS / "organizaciones_prueba" / "perfil_contaminado.md")
    assert c == 1 and not r["valido"]
    texto = " ".join(r["errores"])
    assert "homologado" in texto and "no requiere DPA" in texto and "Sí / No / Desconocido" in texto, r["errores"]
    return f"{len(r['errores'])} errores detectados"


@prueba("E. Plantilla vacía → rechazada (marcadores sin llenar)")
def _():
    c, r = validar_perfil(RAIZ / "pims-perfilador-organizacion" / "assets" / "plantilla_perfil.md")
    assert c == 1 and any("marcador" in e for e in r["errores"])


@prueba("E. Perfil que cita un documento inexistente (D9) → rechazado")
def _():
    t = (ORG_PERFIL / "perfil_organizacion.md").read_text(encoding="utf-8").replace("[D1, art. 12]", "[D9, art. 12]")
    p = TMP / "perfil_d9.md"
    p.write_text(t, encoding="utf-8")
    c, r = validar_perfil(p)
    assert c == 1 and any("D9" in e for e in r["errores"]), r["errores"]


@prueba("E. Perfil sin fuente en una fila → rechazado")
def _():
    t = (ORG_PERFIL / "perfil_organizacion.md").read_text(encoding="utf-8").replace(
        "| Juliaca, Perú | [D1, art. 1] |", "| Juliaca, Perú |  |")
    p = TMP / "perfil_sin_fuente.md"
    p.write_text(t, encoding="utf-8")
    c, r = validar_perfil(p)
    assert c == 1 and any("sin fuente" in e for e in r["errores"]), r["errores"]


# ---------------------------------------------------------------- F. Compatibilidad
@prueba("F. Config v1.1 (sin 'jurisdiccion') → asume Perú con advertencia, mismo cálculo")
def _():
    c, s, r = correr(SCRIPT_V2, NUBE, "--config", CONFIG_V11, "--fecha-ref", "2026-10-01")
    assert c == 0, s
    assert r["jurisdiccion"]["id"] == "peru"
    assert any("no indica 'jurisdiccion'" in a for a in r["trazabilidad"]["advertencias"])
    assert r["puntaje_proveedor"]["valor"] == 22


@prueba("F. fuente_requisito 'Ley aplicable' (nueva) y 'Ley 29733/Reglamento' (antigua) son válidas")
def _():
    r = json.loads(NUBE.read_text(encoding="utf-8"))
    r["controles"][0]["fuente_requisito"] = "Ley aplicable"
    r["controles"][1]["fuente_requisito"] = "Ley 29733/Reglamento"
    p = TMP / "fuentes.json"
    p.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    c, s, _ = correr(SCRIPT_V2, p, "--fecha-ref", "2026-10-01")
    assert c == 0 and "Esquema: valido" in s, s


@prueba("F. Consola cp1252 (Windows) → sin UnicodeEncodeError, código 0")
def _():
    c, s, _ = correr(SCRIPT_V2, NUBE, "--fecha-ref", "2026-10-01", env_extra={"PYTHONIOENCODING": "cp1252"})
    assert c == 0, s
    assert "Traceback" not in s, s


@prueba("F. Hash del contrato con --documento")
def _():
    doc = PRUEBAS / "contratos" / "dpa_nubeandina.md"
    c, s, r = correr(SCRIPT_V2, NUBE, "--documento", doc, "--fecha-ref", "2026-10-01")
    assert c == 0 and r["contrato"]["hash_documento_sha256"] == hashlib.sha256(doc.read_bytes()).hexdigest()


@prueba("F. Entrada sin campos obligatorios → código 2 (corrige y vuelve a ejecutar)")
def _():
    r = json.loads(NUBE.read_text(encoding="utf-8"))
    del r["controles"]
    p = TMP / "incompleto.json"
    p.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    c, s, _ = correr(SCRIPT_V2, p, "--fecha-ref", "2026-10-01")
    assert c == 2 and "falta 'controles'" in s, s


# ---------------------------------------------------------------- G. Casos de prueba
@prueba("G. Los archivos citados en casos_de_prueba.json existen")
def _():
    d = json.loads((PRUEBAS / "casos_de_prueba.json").read_text(encoding="utf-8"))
    faltan = []
    for e in d["evals"]:
        for ruta in e.get("files", []) + [e.get("organizacion"), e.get("perfil")]:
            if ruta and not (RAIZ / ruta).exists():
                faltan.append(f"caso {e['id']}: {ruta}")
    assert not faltan, "; ".join(faltan)
    return f"{len(d['evals'])} casos"


# ---------------------------------------------------------------- Informe
def main():
    ok = sum(1 for r in resultados if r[0])
    print(f"\nPruebas deterministas — pims-dpa-auditor v2.0\n{'=' * 46}")
    for paso, nombre, detalle in resultados:
        marca = "OK  " if paso else "FALLA"
        print(f"[{marca}] {nombre}" + (f"\n         {detalle}" if detalle else ""))
    print(f"\n{ok}/{len(resultados)} pruebas correctas")
    shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(0 if ok == len(resultados) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    main()
