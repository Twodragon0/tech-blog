"""Explicit local ledger backup/verified restore; no bootstrap or auto-resume."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.news.translation_backup import LedgerBackup
from scripts.news.translation_budget import BudgetError
from scripts.news.translation_production import ProductionBudgetLedger


def _outside_checkout(path: Path) -> Path:
    target = path.resolve()
    if target == ROOT or ROOT in target.parents:
        raise BudgetError("Ledger state and snapshots must be outside the checkout")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--ledger", type=Path, required=True)
    common.add_argument("--snapshot-dir", type=Path, required=True)
    common.add_argument("--daily-limit-microusd", type=int, required=True)
    common.add_argument("--batch-limit-microusd", type=int, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("backup", parents=[common])
    restore = commands.add_parser("restore", parents=[common])
    restore.add_argument("--operation-id", required=True)
    args = parser.parse_args(argv)
    try:
        ledger_path = _outside_checkout(args.ledger)
        if args.snapshot_dir.is_symlink():
            raise BudgetError("Explicit non-symlink snapshot directory required")
        snapshot = _outside_checkout(args.snapshot_dir)
        ledger = ProductionBudgetLedger(
            ledger_path,
            daily_limit_microusd=args.daily_limit_microusd,
            batch_limit_microusd=args.batch_limit_microusd,
        )
        tool = LedgerBackup(ledger)
        result = (
            tool.backup(snapshot)
            if args.command == "backup"
            else tool.restore(snapshot, args.operation_id)
        )
    except BudgetError as error:
        print(f"Ledger operation refused: {error}", file=sys.stderr)
        return 1
    except OSError:
        print(
            "Ledger filesystem operation failed; inspect maintenance state.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"action": args.command, "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
