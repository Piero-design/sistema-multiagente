#!/usr/bin/env python3
"""
build_embed.py — Genera `corpus.js` para la demo web del Agente 7 (PIMS DPA Auditor).

La demo es una página estática: no puede leer archivos del disco ni ejecutar
`calcular_resultado.py`. Por eso todo lo que la skill necesita (SKILL.md y sus
archivos de referencia) se embebe como strings de JavaScript, junto con los tres
contratos de prueba.

Ejecuta este script cada vez que cambie la skill, para que la demo use la versión
vigente:

    python build_embed.py

Escribe `corpus.js` en la misma carpeta. Solo biblioteca estándar.
"""
import json
from pathlib import Path

DEMO = Path(__file__).resolve().parent
RAIZ = DEMO.parent
SKILL = RAIZ / "pims-dpa-auditor"
PRUEBAS = RAIZ / "pims-dpa-auditor_pruebas"

# Archivos de la skill que el modelo necesita tener delante.
# SKILL.md manda leer estos archivos en pasos concretos; en el navegador no hay
# disco, así que se los entregamos ya cargados en el system prompt.
REFERENCIAS = [
    ("references/criterios_semaforo.md", SKILL / "references" / "criterios_semaforo.md"),
    ("references/controles_iso27701_2025.md", SKILL / "references" / "controles_iso27701_2025.md"),
    # v2.0: el marco legal vive en jurisdicciones/<id>/. La demo usa la jurisdicción por defecto (peru).
    ("jurisdicciones/peru/marco_legal.md", SKILL / "jurisdicciones" / "peru" / "marco_legal.md"),
    ("jurisdicciones/peru/parametros_legales.json", SKILL / "jurisdicciones" / "peru" / "parametros_legales.json"),
    ("assets/config_organizacion.json", SKILL / "assets" / "config_organizacion.json"),
    ("assets/plantilla_dpa_baseline.md", SKILL / "assets" / "plantilla_dpa_baseline.md"),
    ("assets/esquema_salida.json", SKILL / "assets" / "esquema_salida.json"),
]

CONTRATOS = [
    ("nubeandina", "NubeAndina Contact Services S.A.C.", "deficiente",
     PRUEBAS / "contratos" / "dpa_nubeandina.md"),
    ("andescloud", "AndesCloud Hosting S.A.C.", "conforme",
     PRUEBAS / "contratos" / "dpa_andescloud_bueno.md"),
    ("digiserv", "DigiServ Perú S.A.C.", "inyección",
     PRUEBAS / "contratos" / "dpa_ambiguo_inyeccion.md"),
]


def leer(ruta: Path) -> str:
    if not ruta.exists():
        raise SystemExit(f"No se encontró {ruta}. Ejecuta el script desde project/demo/.")
    return ruta.read_text(encoding="utf-8")


def main() -> None:
    skill_md = leer(SKILL / "SKILL.md")

    referencias = [{"ruta": ruta, "contenido": leer(p)} for ruta, p in REFERENCIAS]
    contratos = {
        clave: {"proveedor": prov, "tipo": tipo, "texto": leer(p)}
        for clave, prov, tipo, p in CONTRATOS
    }

    corpus = {
        "skill_md": skill_md,
        "referencias": referencias,
        "contratos": contratos,
    }

    salida = DEMO / "corpus.js"
    cuerpo = json.dumps(corpus, ensure_ascii=False, indent=2)
    salida.write_text(
        "// corpus.js — GENERADO POR build_embed.py. No editar a mano.\n"
        "// Contiene SKILL.md, los archivos de referencia de la skill y los 3 contratos de prueba.\n"
        "// Regenerar con:  python build_embed.py\n"
        "window.PIMS_CORPUS = " + cuerpo + ";\n",
        encoding="utf-8",
    )

    kb = len(cuerpo.encode("utf-8")) / 1024
    print(f"corpus.js escrito ({kb:.1f} KB)")
    print(f"  SKILL.md: {len(skill_md)} caracteres")
    for r in referencias:
        print(f"  {r['ruta']}: {len(r['contenido'])} caracteres")
    for clave, c in contratos.items():
        print(f"  contrato {clave} ({c['tipo']}): {len(c['texto'])} caracteres")


if __name__ == "__main__":
    main()
