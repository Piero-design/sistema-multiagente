"""CLI JSON del Grupo 6. Los errores también se devuelven como JSON y con exit code 1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from inventario.service import InventoryAgent, respuesta


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Grupo 6 · Inventario de datos personales")
    parser.add_argument("--entrada", type=Path, help="Solicitud JSON; omitir para leer stdin")
    parser.add_argument("--db", type=Path, help="SQLite propia; predeterminado: data/inventario.sqlite3")
    parser.add_argument("--estado", action="store_true")
    parser.add_argument("--handoff", action="store_true", help="La entrada es un sobre del Grupo 3")
    parser.add_argument("--organizacion", help="Obligatoria con --handoff: el sobre DSAR no incluye organización")
    args = parser.parse_args(argv)
    agent = InventoryAgent(args.db)
    if args.estado:
        print(json.dumps(agent.estado(), ensure_ascii=False, indent=2))
        return 0
    try:
        raw = args.entrada.read_text(encoding="utf-8") if args.entrada else sys.stdin.read(1000001)
        if len(raw) > 1000000:
            raise ValueError("Entrada demasiado grande")
        payload = json.loads(raw)
        if args.handoff:
            if not args.organizacion:
                raise ValueError("Indica --organizacion para un handoff")
            result, status = agent.recibir_handoff(payload, args.organizacion)
        else:
            result, status = agent.ejecutar(payload)
    except (OSError, ValueError, UnicodeError):
        result, status = respuesta(None, error={"code": "ENTRADA_INVALIDA", "message": "No se pudo leer la solicitud JSON. Para handoffs indica --organizacion.", "retryable": False}), 422
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
