"""Mide la entrada de correo con un conjunto etiquetado, en una base de datos temporal.

python -m dsar.services.intake_eval --dataset mail/esperado.json
python -m dsar.services.intake_eval --dataset tests/fixtures/intake-eval-holdout.json --sin-modelo
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import fields
from datetime import datetime, timedelta, timezone
from email.utils import make_msgid
from pathlib import Path
from typing import Any

from dsar.core.validator import validate
from dsar.mail.demo import DemoMail, to_message
from dsar.services import cases, intake
from dsar.services.context import ServiceContext, Settings, build_context

START = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)
FIELDS = {item.name for item in fields(DemoMail)}


def load_dataset(path: Path) -> list[DemoMail]:
    mails = []
    for number, item in enumerate(json.loads(path.read_text(encoding="utf-8")), start=1):
        data = {key: value for key, value in item.items() if key in FIELDS}
        data.setdefault("number", number)
        mail = DemoMail(**data)
        mail.message_id = mail.message_id or make_msgid(idstring=f"eval-{number}", domain="example.test")
        mails.append(mail)
    return mails


def _case_checks(ctx: ServiceContext, case_ids: list[str]) -> dict[str, int]:
    invalid = with_records = not_pending = 0
    for case_id in case_ids:
        package = cases.get(ctx, case_id)
        invalid += bool(validate(package))
        with_records += bool(package["discovered_records"])
        not_pending += package["status"] != "IDENTITY_PENDING"
    return {"invalid": invalid, "with_records": with_records, "not_identity_pending": not_pending}


def evaluate(ctx: ServiceContext, mails: list[DemoMail]) -> dict[str, Any]:
    queued = {}
    for mail in mails:
        sent_at = START + timedelta(seconds=30 * mail.number)
        queued[mail.number] = intake.enqueue(ctx, bytes(to_message(mail, sent_at)))
    intake.process_pending(ctx, len(mails))
    rows = {row["message_id"]: row for row in ctx.repository.list_inbound(limit=len(mails) + 10)}

    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    outcomes = Counter()
    lost = wrong_rights = right_rights = injections_registered = 0
    times = []
    for mail in mails:
        row = rows.get(mail.message_id)
        actual = "duplicado" if queued[mail.number] == "duplicado" and mail.category == "duplicado" else (
            row["status"] if row else "perdido")
        lost += actual == "perdido"
        by_category[mail.category]["acierta" if actual == mail.expected_status else actual] += 1
        outcomes[actual] += 1
        if row and row["analysis_s"] is not None:
            times.append(row["analysis_s"])
        if actual == "registrado" and row and row["case_id"]:
            rights = set(cases.get(ctx, row["case_id"])["request_types"])
            injections_registered += mail.category == "inyeccion"
            if mail.expected_rights and rights == set(mail.expected_rights):
                right_rights += 1
            else:
                wrong_rights += 1
    expected_unique = len({mail.message_id for mail in mails})
    registered = [row["case_id"] for row in rows.values() if row["status"] == "registrado" and row["case_id"]]
    return {
        "correos": len(mails),
        "perdidos": lost,
        "filas_en_cola": len(rows),
        "filas_esperadas": expected_unique,
        "destinos": dict(outcomes),
        "por_categoria": {name: dict(counter) for name, counter in sorted(by_category.items())},
        "aciertos_destino": sum(counter["acierta"] for counter in by_category.values()),
        "registrados_con_derechos_correctos": right_rights,
        "registrados_con_derechos_incorrectos": wrong_rights,
        "inyecciones_registradas": injections_registered,
        "expedientes": _case_checks(ctx, registered),
        "segundos_por_correo": round(sum(times) / len(times), 2) if times else None,
    }


def isolated_context(base: Path, with_model: bool) -> ServiceContext:
    settings = Settings(db_path=base / "eval.sqlite3", handoff_dir=base / "handoffs", export_dir=base / "exports",
                        warmup=False)
    ctx = build_context(settings)
    if not with_model:
        ctx.providers = {}
    return ctx


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluación de la entrada de correo")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--sin-modelo", action="store_true", help="sin Ollama: todo lo dudoso va a triaje")
    parser.add_argument("--modelo", help="modelo de Ollama para leer los correos (p. ej. qwen2.5:7b)")
    args = parser.parse_args(argv)
    if args.modelo:
        os.environ["DSAR_MAIL_MODEL"] = args.modelo
    with tempfile.TemporaryDirectory() as folder:
        report = evaluate(isolated_context(Path(folder), not args.sin_modelo), load_dataset(args.dataset))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
