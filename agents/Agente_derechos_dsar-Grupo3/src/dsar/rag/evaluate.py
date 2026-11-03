"""Mide hit@1, hit@k y MRR del RAG con un conjunto de consultas etiquetadas.

Cada consulta indica los `chunk_id` que la responden; basta recuperar uno dentro del top-k.
Uso (desde backend/): python -m dsar.rag.evaluate [--eval ARCHIVO] [--top-k 3] [--detail]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dsar.paths import FIXTURES_DIR
from dsar.rag.dense import DenseUnavailable
from dsar.rag.lexical import LEXICAL_VARIANTS
from dsar.rag.applicability import drop_technical
from dsar.rag.relevance import visible_chunks
from dsar.rag.retrieve import search
from dsar.rag.store import load_index

METHODS = ("tfidf", *LEXICAL_VARIANTS, "dense", "hybrid")
EVAL_SETS = ("rag-eval.json", "rag-eval-holdout.json", "rag-eval-holdout2.json")


def load_queries(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["queries"]


def base_chunk_id(chunk_id: str) -> str:
    """Las ventanas de una sección larga (`-03b`) cuentan como la sección (`-03`)."""
    return chunk_id[:-1] if chunk_id[-1:].isalpha() and chunk_id[-3:-1].isdigit() else chunk_id


def evaluate(queries: list[dict[str, Any]], index: dict[str, Any], method: str, top_k: int = 3) -> list[dict[str, Any]]:
    rows = []
    for item in queries:
        ranked = [hit["chunk_id"] for hit in search(item["query"], index, top_k, method)]
        position = next((i for i, chunk in enumerate(ranked, 1) if base_chunk_id(chunk) in item["relevant"]), None)
        rows.append({"id": item["id"], "query": item["query"], "kind": item["kind"],
                     "position": position, "ranked": ranked})
    return rows


def summarize(rows: list[dict[str, Any]], top_k: int = 3) -> dict[str, float]:
    total = len(rows) or 1
    return {
        "n": len(rows),
        "hit@1": sum(1 for r in rows if r["position"] == 1) / total,
        f"hit@{top_k}": sum(1 for r in rows if r["position"]) / total,
        "mrr": sum(1 / r["position"] for r in rows if r["position"]) / total,
    }


def measure(methods: tuple[str, ...] = METHODS, top_k: int = 3,
            eval_sets: tuple[str, ...] = EVAL_SETS) -> dict[str, dict[str, dict[str, float]]]:
    """Resumen por conjunto y método; los métodos densos se omiten si falta el modelo."""
    index = load_index()
    results: dict[str, dict[str, dict[str, float]]] = {}
    for name in eval_sets:
        queries = load_queries(FIXTURES_DIR / name)
        results[name] = {}
        for method in methods:
            try:
                results[name][method] = summarize(evaluate(queries, index, method, top_k), top_k)
            except DenseUnavailable:
                continue
    return results


def evaluate_sources(path: Path | None = None, method: str = "hybrid", top_k: int = 3) -> dict[str, Any]:
    """Coherencia de las fuentes que muestra el chat: con `rag-eval-fuentes.json`, ¿aparece la que responde y no las ajenas?

    Aplica el mismo filtro que el chat (`visible_chunks`) sobre lo recuperado.
    """
    index = load_index()
    queries = json.loads((path or FIXTURES_DIR / "rag-eval-fuentes.json").read_text(encoding="utf-8"))["queries"]
    rows = []
    for item in queries:
        shown = [hit["chunk_id"] for hit in visible_chunks(drop_technical(search(item["query"], index, top_k, method), item["query"]))]
        rows.append({"id": item["id"], "query": item["query"], "shown": shown,
                     "answered": any(base_chunk_id(c) in item["answers"] for c in shown),
                     "unrelated_shown": [c for c in shown if base_chunk_id(c) in item["unrelated"]]})
    total = len(rows) or 1
    return {"n": len(rows), "answered": sum(r["answered"] for r in rows) / total,
            "unrelated_shown": sum(len(r["unrelated_shown"]) for r in rows),
            "avg_sources": sum(len(r["shown"]) for r in rows) / total, "rows": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--eval", type=Path, default=FIXTURES_DIR / "rag-eval.json")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--detail", action="store_true", help="Lista las consultas que fallan")
    parser.add_argument("--sources", action="store_true", help="Mide las fuentes que muestra el chat (rag-eval-fuentes.json)")
    args = parser.parse_args(argv)
    if args.sources:
        result = evaluate_sources(top_k=args.top_k)
        print(f"preguntas {result['n']} · con la fuente que responde {result['answered']:.0%} · "
              f"fuentes ajenas mostradas {result['unrelated_shown']} · fuentes por pregunta {result['avg_sources']:.2f}")
        if args.detail:
            for row in result["rows"]:
                flag = "" if row["answered"] and not row["unrelated_shown"] else "  <-- revisar"
                print(f"  {row['id']} {row['query']!r} -> {row['shown']} ajenas={row['unrelated_shown']}{flag}")
        return 0
    queries = load_queries(args.eval)
    index = load_index()
    key = f"hit@{args.top_k}"
    kinds = ["todas", *sorted({q["kind"] for q in queries})]
    print(f"{'metodo':<20}" + "".join(f"{kind + ' ' + key:>22}{'MRR':>7}" for kind in kinds))
    for method in METHODS:
        try:
            rows = evaluate(queries, index, method, args.top_k)
        except DenseUnavailable as exc:
            print(f"(se omite {method}: {exc})", file=sys.stderr)
            continue
        line = f"{method:<20}"
        for kind in kinds:
            summary = summarize([r for r in rows if kind == "todas" or r["kind"] == kind], args.top_k)
            line += f"{summary[key]:>22.0%}{summary['mrr']:>7.2f}"
        print(line)
        if args.detail:
            for row in (r for r in rows if not r["position"]):
                print(f"   sin acierto {row['id']} {row['query']!r} -> {row['ranked']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
