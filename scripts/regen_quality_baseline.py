#!/usr/bin/env python3
"""Regenerate the quality-scoring golden baseline used by test_index_scoring.py.

scripts/tests/test_index_scoring.py asserts that every non-index post's
validate_post() score stays byte-identical to the snapshot committed at
scripts/tests/fixtures/quality_baseline.json. Posts not present in that
snapshot are silently SKIPPED by the isolation test (see
test_non_index_scores_byte_identical), so posts added by the daily
blogwatcher cron accumulate as untested coverage over time. This script
refreshes the snapshot so cron-added posts are folded back into the
isolation guarantee.

Usage:
    python3 scripts/regen_quality_baseline.py          # write/refresh the baseline
    python3 scripts/regen_quality_baseline.py --check  # dry-run; exit 1 if posts are
                                                        # missing from the current baseline

Does NOT modify validate_post_quality.py, any post under _posts/, any cover
asset, or the isolation test logic — it only reads scores and writes the
fixture JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_post_quality import validate_post  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
BASELINE_PATH = (
    Path(__file__).resolve().parent / "tests" / "fixtures" / "quality_baseline.json"
)


def score_all_posts(posts_dir: Path = POSTS_DIR) -> dict[str, dict[str, object]]:
    """Score every post under posts_dir and return {filename: {total, scores}}."""
    result: dict[str, dict[str, object]] = {}
    for post in sorted(posts_dir.glob("*.md")):
        r = validate_post(post)
        result[post.name] = {"total": r["total"], "scores": r["scores"]}
    return result


def render_baseline(scored: dict[str, dict[str, object]]) -> str:
    """Render scored posts as deterministic, minimal-diff JSON text.

    Top-level keys (filenames) are sorted for a stable diff order. Inner
    dict order (total/scores and each score dimension) is left as produced
    by validate_post(), which builds them in a fixed order every run — NOT
    alphabetically re-sorted, to match the existing committed fixture's
    key order and avoid a spurious full-file diff on regen.
    """
    ordered = {name: scored[name] for name in sorted(scored)}
    return json.dumps(ordered, indent=2) + "\n"


def load_current_baseline(baseline_path: Path = BASELINE_PATH) -> dict[str, dict]:
    if not baseline_path.exists():
        return {}
    return json.loads(baseline_path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate scripts/tests/fixtures/quality_baseline.json "
            "(the isolation-test golden snapshot)."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: list posts missing from the current baseline and exit 1 "
        "if any are found, without writing.",
    )
    args = parser.parse_args(argv)

    # Reference the module globals explicitly (not via default args) so a
    # monkeypatched POSTS_DIR / BASELINE_PATH (e.g. in tests) is honored.
    scored = score_all_posts(POSTS_DIR)
    current = load_current_baseline(BASELINE_PATH)

    added = sorted(set(scored) - set(current))
    removed = sorted(set(current) - set(scored))

    if args.check:
        if added:
            print(
                f"[regen_quality_baseline] {len(added)} post(s) missing from "
                "baseline (added since last regen):",
                file=sys.stderr,
            )
            for name in added:
                print(f"  MISSING  {name}", file=sys.stderr)
            print(
                "\nRun `python3 scripts/regen_quality_baseline.py` to refresh.",
                file=sys.stderr,
            )
            return 1
        print(
            f"[regen_quality_baseline] baseline is up to date "
            f"({len(scored)} posts scored, 0 missing)."
        )
        return 0

    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(render_baseline(scored), encoding="utf-8")
    print(
        f"[regen_quality_baseline] scored {len(scored)} posts — "
        f"{len(added)} newly added, {len(removed)} removed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
