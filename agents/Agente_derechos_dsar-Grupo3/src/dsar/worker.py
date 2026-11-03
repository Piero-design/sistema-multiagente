"""Revisa el buzón y analiza la cola cada cierto tiempo: python -m dsar.worker --interval 60."""

from __future__ import annotations

import argparse
import logging
import time

from dsar.services import intake
from dsar.services.context import ServiceContext, build_context, load_env_file
from dsar.services.errors import MailboxError

logger = logging.getLogger("dsar.worker")


def run_once(ctx: ServiceContext, limit: int) -> dict:
    try:
        fetched = intake.ingest(ctx)
    except MailboxError as exc:
        logger.warning("%s", exc)
        fetched = {}
    processed = intake.process_pending(ctx, limit)
    return {"fetched": fetched, "processed": len(processed), "pending": intake.summary(ctx)["recibido"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Worker de correo del Agente DSAR")
    parser.add_argument("--interval", type=int, default=60, help="segundos entre revisiones")
    parser.add_argument("--limit", type=int, default=50, help="correos analizados por vuelta")
    parser.add_argument("--once", action="store_true", help="una sola vuelta")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_env_file()
    ctx = build_context()
    while True:
        logger.info("Vuelta: %s", run_once(ctx, args.limit))
        if args.once:
            return 0
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
