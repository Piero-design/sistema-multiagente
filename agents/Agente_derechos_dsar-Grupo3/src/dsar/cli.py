"""CLI de demostración del motor DSAR (sucesora de demo/dsar_simulator.py de v4).

Uso (desde backend/):
    python -m dsar.cli --scenario access --output-dir salidas/access
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dsar.core.engine import build_case
from dsar.core.errors import CaseInputError
from dsar.core.hashing import sha256_file, sha256_json
from dsar.core.policy import load_org_policy
from dsar.core.profiles import load_profiles
from dsar.core.render import render_response
from dsar.core.validator import validate
from dsar.paths import FIXTURES_DIR, ORGANIZATION_PATH, PROFILES_PATH

RECORDS_PATH = FIXTURES_DIR / "subject-data.json"
SCENARIOS = {
    "access": "request-access.json",
    "pending": "request-identity-pending.json",
    "erasure": "request-erasure.json",
    "pe-combined": "request-pe-combined.json",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def run(scenario: str, output_dir: Path, use_organization: bool = True) -> dict[str, Any]:
    request = read_json(FIXTURES_DIR / SCENARIOS[scenario])
    profiles = load_profiles(PROFILES_PATH)
    organization = load_org_policy(ORGANIZATION_PATH, profiles) if use_organization else None
    package = build_case(
        request,
        read_json(RECORDS_PATH),
        profiles,
        generated_at=datetime.now(timezone.utc),
        source_hashes={
            "request": sha256_json(request),
            "data": sha256_file(RECORDS_PATH),
            "policies": sha256_file(PROFILES_PATH),
        },
        organization=organization,
    )
    errors = validate(package)
    if errors:
        raise CaseInputError("Expediente invalido: " + "; ".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "request.json", request)
    write_json(output_dir / "case-package.json", package)
    write_text(output_dir / "response-draft.md", render_response(package))
    return package


def print_summary(package: dict[str, Any], output_dir: Path) -> None:
    print("=== RESULTADO DE LA SIMULACION ===")
    print(f"Caso:              {package['case_id']}")
    print(f"Derechos:          {', '.join(package['request_types'])}")
    print(f"Estado:            {package['status']}")
    print(f"Fecha limite:      {package['deadline_at']}")
    print(f"Registros:         {len(package['discovered_records'])}")
    print(f"Revision humana:   {'SI' if package['hitl']['required'] else 'NO'}")
    for reason in package["hitl"]["reasons"]:
        print(f"  - {reason}")
    print(f"Archivos en:       {output_dir}")
    print("La respuesta es un borrador. Ninguna accion fue ejecutada.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--sin-organizacion", action="store_true",
                        help="No aplicar la politica de la organizacion")
    args = parser.parse_args(argv)
    output_dir = args.output_dir.resolve()
    try:
        package = run(args.scenario, output_dir, use_organization=not args.sin_organizacion)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print_summary(package, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
