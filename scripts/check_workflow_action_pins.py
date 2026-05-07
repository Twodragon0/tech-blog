#!/usr/bin/env python3
"""
check_workflow_action_pins.py — GitHub Actions pin consistency checker.

Scans .github/workflows/*.yml for `uses:` directives and validates:
  1. SHA consistency: same action used with the same 40-char SHA across all workflows.
  2. SHA format: floating tags (@v1, @v2) flagged as warnings (CIA supply-chain best practice).
  3. Existence (optional, --check-existence): GitHub API confirms each SHA is real.

Exit codes:
  0 — all checks pass (or --warn-only)
  1 — violations found

Environment variables:
  GITHUB_TOKEN       — Bearer token for GitHub API (avoids rate-limit on --check-existence)
  SKIP_PIN_CHECK=1   — emergency bypass, exits 0 immediately
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKFLOWS_DIR = Path(__file__).parent.parent / ".github" / "workflows"
SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
# Matches:  uses: owner/repo@ref  (with optional leading spaces/dashes and trailing comment)
USES_RE = re.compile(r"""^\s*-?\s*uses:\s+([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)@([^\s#]+)""")


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class ActionPin(NamedTuple):
    action: str   # e.g. "actions/checkout"
    ref: str      # e.g. "de0fac2e4500dabe..." or "v4"
    workflow: str  # workflow filename (basename)
    line: int


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def collect_pins(workflows_dir: Path = WORKFLOWS_DIR) -> list[ActionPin]:
    """Return all ActionPin entries found in .github/workflows/*.yml."""
    pins: list[ActionPin] = []
    for yml in sorted(workflows_dir.glob("*.yml")):
        for lineno, raw in enumerate(yml.read_text(encoding="utf-8").splitlines(), 1):
            m = USES_RE.match(raw)
            if m:
                pins.append(ActionPin(
                    action=m.group(1),
                    ref=m.group(2),
                    workflow=yml.name,
                    line=lineno,
                ))
    return pins


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_sha_format(pins: list[ActionPin]) -> list[str]:
    """Warn when a ref is NOT a 40-char hex SHA (i.e. floating tag)."""
    warnings: list[str] = []
    for p in pins:
        if not SHA_RE.match(p.ref):
            warnings.append(
                f"  FLOATING TAG  {p.workflow}:{p.line}  {p.action}@{p.ref}"
            )
    return warnings


def check_consistency(pins: list[ActionPin]) -> list[str]:
    """Error when the same action is pinned to different SHAs across workflows."""
    # group SHA pins only (floating tags checked separately)
    sha_pins: dict[str, dict[str, list[ActionPin]]] = defaultdict(lambda: defaultdict(list))
    for p in pins:
        if SHA_RE.match(p.ref):
            sha_pins[p.action][p.ref].append(p)

    errors: list[str] = []
    for action, sha_map in sorted(sha_pins.items()):
        if len(sha_map) > 1:
            errors.append(f"  INCONSISTENT  {action}  — {len(sha_map)} different SHAs in use:")
            for sha, instances in sorted(sha_map.items(), key=lambda kv: -len(kv[1])):
                for inst in instances:
                    errors.append(f"      {sha[:12]}...  {inst.workflow}:{inst.line}")
    return errors


def check_existence_via_api(pins: list[ActionPin]) -> list[str]:
    """
    For each unique (action, sha) pair call the GitHub commits API.
    Returns a list of error strings for SHAs that could not be found.
    Requires GITHUB_TOKEN env var to avoid rate-limiting (optional but recommended).
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    seen: set[tuple[str, str]] = set()
    errors: list[str] = []

    for p in pins:
        if not SHA_RE.match(p.ref):
            continue
        key = (p.action, p.ref)
        if key in seen:
            continue
        seen.add(key)

        url = f"https://api.github.com/repos/{p.action}/commits/{p.ref}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if token:
            req.add_header("Authorization", f"Bearer {token}")

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status not in (200, 201):
                    errors.append(
                        f"  NONEXISTENT   {p.action}@{p.ref[:12]}...  "
                        f"(HTTP {resp.status})  first seen in {p.workflow}:{p.line}"
                    )
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                errors.append(
                    f"  NONEXISTENT   {p.action}@{p.ref[:12]}...  "
                    f"(HTTP 404)  first seen in {p.workflow}:{p.line}"
                )
            elif exc.code == 422:
                errors.append(
                    f"  NONEXISTENT   {p.action}@{p.ref[:12]}...  "
                    f"(HTTP 422 invalid SHA)  first seen in {p.workflow}:{p.line}"
                )
            else:
                # rate-limit or transient error — warn but don't fail
                print(f"  [warn] API error for {p.action}@{p.ref[:12]}...: HTTP {exc.code}")
        except Exception as exc:  # network down, timeout, etc.
            print(f"  [warn] API check skipped for {p.action}@{p.ref[:12]}...: {exc}")

    return errors


# ---------------------------------------------------------------------------
# Fix (auto-unify inconsistent SHAs to majority SHA)
# ---------------------------------------------------------------------------


def fix_inconsistencies(
    pins: list[ActionPin],
    workflows_dir: Path = WORKFLOWS_DIR,
    dry_run: bool = False,
) -> int:
    """Replace minority SHAs with the majority SHA for each inconsistent action.

    Returns the number of replacements made (or that would be made in dry_run).
    """
    sha_pins: dict[str, dict[str, list[ActionPin]]] = defaultdict(lambda: defaultdict(list))
    for p in pins:
        if SHA_RE.match(p.ref):
            sha_pins[p.action][p.ref].append(p)

    total_fixes = 0
    for action, sha_map in sorted(sha_pins.items()):
        if len(sha_map) <= 1:
            continue
        # majority = SHA with most occurrences
        canonical = max(sha_map, key=lambda s: len(sha_map[s]))
        minority_shas = {s for s in sha_map if s != canonical}
        print(f"  FIX  {action}")
        print(f"       canonical SHA (most uses): {canonical[:16]}...")
        for minority in sorted(minority_shas):
            affected = sha_map[minority]
            print(f"       replacing {minority[:16]}... in: "
                  + ", ".join(f"{p.workflow}:{p.line}" for p in affected))
            if not dry_run:
                for pin in affected:
                    yml_path = workflows_dir / pin.workflow
                    text = yml_path.read_text(encoding="utf-8")
                    new_text = text.replace(
                        f"{action}@{minority}",
                        f"{action}@{canonical}",
                    )
                    if new_text != text:
                        yml_path.write_text(new_text, encoding="utf-8")
                        total_fixes += len(affected)
            else:
                total_fixes += len(affected)
    return total_fixes


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate GitHub Actions pin consistency across .github/workflows/*.yml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--check-existence",
        action="store_true",
        help="Call GitHub API to verify each SHA exists (slow, requires network)",
    )
    p.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix SHA inconsistencies by rewriting minority SHAs to canonical (majority) SHA",
    )
    p.add_argument(
        "--warn-only",
        action="store_true",
        help="Print all warnings/errors but always exit 0",
    )
    p.add_argument(
        "--workflows-dir",
        type=Path,
        default=WORKFLOWS_DIR,
        help=f"Override workflow directory (default: {WORKFLOWS_DIR})",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    if os.environ.get("SKIP_PIN_CHECK") == "1":
        print("[check-pins] SKIP_PIN_CHECK=1 — skipping.")
        return 0

    args = build_parser().parse_args(argv)
    workflows_dir: Path = args.workflows_dir

    pins = collect_pins(workflows_dir)
    if not pins:
        print("[check-pins] No 'uses:' directives found — nothing to check.")
        return 0

    print(f"[check-pins] Scanned {len(set(p.workflow for p in pins))} workflow(s), "
          f"found {len(pins)} action pin(s).")

    # --- 1. Floating tag warnings ---
    floating = check_sha_format(pins)
    if floating:
        print(f"\n[check-pins] WARNINGS — floating tags ({len(floating)}):")
        for w in floating:
            print(w)

    # --- 2. SHA consistency errors ---
    inconsistent = check_consistency(pins)
    if inconsistent:
        print(f"\n[check-pins] ERRORS — inconsistent SHAs ({len(inconsistent)}):")
        for e in inconsistent:
            print(e)

    # --- 3. Existence check (optional) ---
    nonexistent: list[str] = []
    if args.check_existence:
        print("\n[check-pins] Checking SHA existence via GitHub API ...")
        nonexistent = check_existence_via_api(pins)
        if nonexistent:
            print(f"[check-pins] ERRORS — non-existent SHAs ({len(nonexistent)}):")
            for e in nonexistent:
                print(e)

    # --- 4. Auto-fix ---
    if args.fix:
        if inconsistent:
            print("\n[check-pins] Applying fixes ...")
            n = fix_inconsistencies(pins, workflows_dir=workflows_dir, dry_run=False)
            print(f"[check-pins] Fixed {n} occurrence(s). Re-run to verify.")
        else:
            print("\n[check-pins] Nothing to fix — SHAs are already consistent.")

    # --- Summary ---
    has_errors = bool(inconsistent or nonexistent)
    if not has_errors and not floating:
        print("\n[check-pins] All pins consistent. No floating tags.")

    if args.warn_only:
        return 0
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
