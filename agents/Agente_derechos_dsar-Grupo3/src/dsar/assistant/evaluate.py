"""Mide el filtro de evasión, el control de alcance y el enrutador con los conjuntos de tests/fixtures/.

Uso (desde backend/): python -m dsar.assistant.evaluate [--sin-semantica] [--json]
Sin el modelo denso (o con --sin-semantica) mide solo las reglas.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from dsar.assistant import guard
from dsar.assistant.guided import QUICK_QUESTIONS
from dsar.assistant.router import TASKS, classify_task
from dsar.assistant.scope import scope_details
from dsar.paths import FIXTURES_DIR, KNOWLEDGE_DIR
from dsar.rag import dense

BYPASS_SETS = ("bypass-eval.json", "bypass-eval-holdout.json", "bypass-eval-holdout2.json",
               "bypass-eval-holdout3.json", "bypass-eval-holdout4.json")
RAG_SETS = ("rag-eval.json", "rag-eval-holdout.json", "rag-eval-holdout2.json")
ROUTER_SETS = ("router-eval.json", "router-eval-holdout.json")


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def in_scope_questions() -> list[str]:
    questions = list(load("scope-eval.json")["en_alcance"]) + list(QUICK_QUESTIONS)
    for name in RAG_SETS:
        questions += [item["query"] for item in load(name)["queries"]]
    return questions


def router_sets() -> dict[str, list[tuple[str, str]]]:
    cases = json.loads((KNOWLEDGE_DIR / "evals" / "evals.json").read_text(encoding="utf-8"))["cases"]
    sets = {"evals.json": [(c["query"], c["expected_task"]) for c in cases if c.get("expected_task") in TASKS]}
    for name in ROUTER_SETS:
        sets[name] = [(item["texto"], item["tarea"]) for item in load(name)["preguntas"]]
    return sets


def measure_guard(semantic: bool) -> dict[str, dict[str, int]]:
    results = {}
    for name in BYPASS_SETS:
        data = load(name)
        results[name] = {
            "evasiones": len(data["evasiones"]),
            "bloqueadas": sum(1 for item in data["evasiones"] if guard.detect_evasion(item["texto"], semantic)),
            "legitimas": len(data["legitimas"]),
            "falsos_positivos": sum(1 for text in data["legitimas"] if guard.detect_evasion(text, semantic)),
        }
    return results


def measure_scope(semantic: bool) -> dict[str, int]:
    data = load("scope-eval.json")
    inside = in_scope_questions()

    def scope(question: str) -> str:
        return scope_details(question, semantic=semantic)["scope"]
    return {
        "dominio": len(inside), "dominio_aceptadas": sum(scope(q) == "dsar" for q in inside),
        "ajenas": len(data["ajenas"]), "ajenas_rechazadas": sum(scope(q) != "dsar" for q in data["ajenas"]),
        "cercanas": len(data["cercanas"]), "cercanas_rechazadas": sum(scope(q) != "dsar" for q in data["cercanas"]),
    }


def measure_weak_scope(semantic: bool) -> dict[str, int]:
    """Preguntas con palabras del dominio que también se usan fuera de él (conjunto nuevo, sin umbral ajustado a él)."""
    data = load("scope-eval-palabras-debiles.json")

    def scope(question: str) -> str:
        return scope_details(question, semantic=semantic)["scope"]
    return {
        "ajenas": len(data["ajenas_con_palabra_debil"]),
        "ajenas_rechazadas": sum(scope(q) != "dsar" for q in data["ajenas_con_palabra_debil"]),
        "dominio": len(data["dominio_con_palabra_debil"]),
        "dominio_aceptadas": sum(scope(q) == "dsar" for q in data["dominio_con_palabra_debil"]),
    }


def measure_router() -> dict[str, dict[str, int]]:
    return {name: {"n": len(items), "aciertos": sum(classify_task(text) == task for text, task in items)}
            for name, items in router_sets().items()}


def measure(semantic: bool = True) -> dict[str, Any]:
    if semantic and dense.available() is not None:
        semantic = False  # sin modelo denso solo se pueden medir las reglas
    return {"semantica": semantic, "guard": measure_guard(semantic), "scope": measure_scope(semantic),
            "weak_scope": measure_weak_scope(semantic), "router": measure_router()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sin-semantica", action="store_true", help="Medir solo las reglas")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = measure(semantic=not args.sin_semantica)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    print(f"Capa semantica: {'si' if result['semantica'] else 'no (solo reglas)'}")
    print(f"{'conjunto':<28}{'evasiones bloqueadas':>22}{'legitimas bloqueadas':>22}")
    for name, item in result["guard"].items():
        print(f"{name:<28}{item['bloqueadas']:>15}/{item['evasiones']:<6}{item['falsos_positivos']:>15}/{item['legitimas']:<6}")
    scope = result["scope"]
    print(f"\nAlcance: dominio aceptadas {scope['dominio_aceptadas']}/{scope['dominio']}; ajenas rechazadas "
          f"{scope['ajenas_rechazadas']}/{scope['ajenas']}; cercanas rechazadas {scope['cercanas_rechazadas']}/{scope['cercanas']}")
    weak = result["weak_scope"]
    print(f"Alcance con palabras débiles (conjunto nuevo): ajenas rechazadas {weak['ajenas_rechazadas']}/{weak['ajenas']}; "
          f"dominio aceptadas {weak['dominio_aceptadas']}/{weak['dominio']}")
    for name, item in result["router"].items():
        print(f"Enrutador {name}: {item['aciertos']}/{item['n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
