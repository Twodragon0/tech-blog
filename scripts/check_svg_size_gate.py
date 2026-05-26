#!/usr/bin/env python3
"""SVG Quality Gate — size-band check shared by pre-commit and CI.

Three profiles, matched in this order on each post-date SVG
(``assets/images/YYYY-MM-DD-*.svg``):

  1. rollup cover         (WEEKLY ROLLUP / MONTHLY INDEX, ``bgRoll*`` defs)
                          → 38000-83968 bytes
  2. high-quality cover   (``profile: high-quality-cover``, ``bgSpread*``,
                          ``heroPanel*``, scene-glow / float keyframes)
                          → 18000-73728 bytes
  3. lane / digest        (everything else)
                          → 5000-24576 bytes

Exempt filenames: ``section-*``, ``news-fallback.svg``, ``*-mermaid-*``,
``*-og.svg``. Non-date filenames are skipped silently.

Usage::

  python3 scripts/check_svg_size_gate.py --staged          # files in git index
  python3 scripts/check_svg_size_gate.py --changed BASE    # diff BASE..HEAD
  python3 scripts/check_svg_size_gate.py --all             # every SVG in repo
  python3 scripts/check_svg_size_gate.py path/to/file.svg  # explicit list

Baseline (allow-list known legacy violations)::

  python3 scripts/check_svg_size_gate.py --all --baseline scripts/svg_size_gate_baseline.txt
  python3 scripts/check_svg_size_gate.py --update-baseline scripts/svg_size_gate_baseline.txt

The baseline is a newline-delimited list of paths (relative to repo
root) whose current band violations are intentionally grandfathered.
With ``--baseline`` set, files listed inside are still classified and
warned about, but their warnings do not contribute to the strict-mode
exit code so CI does not block on pre-existing legacy state.

Exit codes:
  0  no violations OR warn-only mode (default) OR all violations baselined
  1  one or more *non-baselined* files outside their profile band (with --strict)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"


# Profile bands (keep in sync with scripts/check_svg_precommit.sh).
BANDS = {
    "std": (5000, 24576),
    "hq": (18000, 73728),
    "rollup": (38000, 83968),
}


HQ_RE = re.compile(
    r'sceneGlow1|sceneGlow2|@keyframes [^ ]*floatUp|clipPath id="[^"]*clip"'
    r'|profile: high-quality-cover|id="bgSpread[A-Z0-9]*"'
    r'|id="heroPanel[A-Z0-9]*"|id="bandA[A-Z0-9]+"'
)
ROLLUP_RE = re.compile(
    r'>WEEKLY ROLLUP<|>MONTHLY INDEX<|id="bgRoll[A-Z0-9]+"|id="hdrGrad[A-Z0-9]+"'
)
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
EXEMPT_PATTERNS = (
    re.compile(r"^section-"),
    re.compile(r"^news-fallback\.svg$"),
    re.compile(r"-mermaid-"),
    re.compile(r"-og\.svg$"),
    # Inline diagram SVGs embedded in post body (not the post's primary cover).
    # These are intentionally small (~4-5 KB) hand-drawn flow charts / timelines
    # / framework diagrams; they should not be force-fit into the std lane band.
    # ``[_-]`` allows both underscore-cased (Detection_Flow) and kebab-cased
    # (key-flow) filename conventions.
    re.compile(r"[_-][Aa]ttack[_-][Ff]low\.svg$"),
    re.compile(r"[_-][Dd]etection[_-][Ff]low\.svg$"),
    re.compile(r"[_-][Kk]ey[_-][Ff]low\.svg$"),
    re.compile(r"[_-][Tt]imeline\.svg$"),
    re.compile(r"[_-][Ff]ramework\.svg$"),
    re.compile(r"-quadruple-extortion\.svg$"),
)


def is_exempt(name: str) -> bool:
    return any(p.search(name) for p in EXEMPT_PATTERNS)


def classify(svg: Path) -> str:
    """Return 'rollup' / 'hq' / 'std' per the marker rules above."""
    text = svg.read_text(encoding="utf-8", errors="replace")
    if ROLLUP_RE.search(text):
        return "rollup"
    if HQ_RE.search(text):
        return "hq"
    return "std"


def check_one(svg: Path) -> Tuple[List[str], bool]:
    """Return (warnings, in_band) for this file.

    ``in_band`` is False if the file is outside its profile band.
    Callers combine warnings + baseline membership to decide exit code.
    """
    if not svg.exists():
        return [f"[svg-gate] WARN: {svg} does not exist."], False
    if is_exempt(svg.name) or not DATE_PREFIX_RE.match(svg.name):
        return [], True
    size = svg.stat().st_size
    profile = classify(svg)
    mn, mx = BANDS[profile]
    if size < mn:
        return (
            [
                f"[svg-gate] WARN: {svg} is {size} bytes (< {mn}) for a "
                f"{profile} SVG profile."
            ],
            False,
        )
    if size > mx:
        return (
            [
                f"[svg-gate] WARN: {svg} is {size} bytes (> {mx}) for a "
                f"{profile} SVG profile."
            ],
            False,
        )
    return [], True


def load_baseline(path: Path) -> set:
    """Load a newline-delimited list of grandfathered paths.

    Lines starting with ``#`` and blank lines are ignored. Paths are
    normalized to be repo-relative (POSIX-style) for stable comparison.
    """
    if not path.exists():
        return set()
    out = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line.replace("\\", "/"))
    return out


def repo_rel(svg: Path) -> str:
    """Return the POSIX-style repo-relative path for ``svg``."""
    try:
        return svg.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return svg.as_posix()


def _run_git(*args: str) -> List[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        return []
    return [line for line in out.stdout.splitlines() if line]


def _filter_post_svgs(paths: Iterable[str]) -> List[Path]:
    keep = []
    for raw in paths:
        # Restrict to assets/images/*.svg (root of that dir, no subdirs).
        p = Path(raw)
        if (
            p.parts[:2] == ("assets", "images")
            and len(p.parts) == 3
            and p.suffix == ".svg"
        ):
            keep.append(REPO / p)
    return keep


def collect_staged() -> List[Path]:
    return _filter_post_svgs(
        _run_git("diff", "--cached", "--name-only", "--diff-filter=ACM")
    )


def collect_changed(base: str) -> List[Path]:
    return _filter_post_svgs(
        _run_git("diff", "--name-only", "--diff-filter=ACM", f"{base}...HEAD")
    )


def collect_all() -> List[Path]:
    return sorted(p for p in ASSETS.glob("*.svg") if not is_exempt(p.name))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true", help="Check files in the git index (default for pre-commit).")
    group.add_argument("--changed", metavar="BASE", help="Check files changed since BASE (e.g. origin/main).")
    group.add_argument("--all", action="store_true", help="Check every post-date SVG in assets/images/.")
    parser.add_argument("paths", nargs="*", help="Explicit file paths to check (overrides selector flags).")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any non-baselined WARN (default warn-only).")
    parser.add_argument("--baseline", metavar="FILE", help="Allow-list of grandfathered violations (newline-delimited paths).")
    parser.add_argument("--update-baseline", metavar="FILE", help="Write the current set of violations into FILE then exit 0.")
    args = parser.parse_args()

    if args.paths:
        targets = [Path(p) if Path(p).is_absolute() else REPO / p for p in args.paths]
    elif args.all or args.update_baseline:
        targets = collect_all()
    elif args.changed:
        targets = collect_changed(args.changed)
    else:
        # Default: --staged
        targets = collect_staged()

    if not targets:
        if args.update_baseline:
            Path(args.update_baseline).write_text("", encoding="utf-8")
        return 0

    baseline = load_baseline(Path(args.baseline)) if args.baseline else set()

    all_warnings: List[str] = []
    new_violations: List[str] = []  # paths NOT in baseline
    current_violations: List[str] = []  # every path with out-of-band size

    for svg in targets:
        warnings, in_band = check_one(svg)
        all_warnings.extend(warnings)
        if not in_band:
            rel = repo_rel(svg)
            current_violations.append(rel)
            if rel not in baseline:
                new_violations.append(rel)

    if args.update_baseline:
        out_lines = [
            "# scripts/svg_size_gate_baseline.txt",
            "# Grandfathered SVG size-gate violations.",
            "# Auto-generated by: python3 scripts/check_svg_size_gate.py --update-baseline scripts/svg_size_gate_baseline.txt",
            "# Each line is a repo-relative POSIX path of an SVG currently outside",
            "# its profile band (std / hq / rollup) that is intentionally allowed.",
            "# Re-run --update-baseline whenever a legacy file is fixed or a new",
            "# legacy-class file enters the repo.",
            "",
        ]
        out_lines.extend(sorted(current_violations))
        Path(args.update_baseline).write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        print(f"[svg-gate] wrote baseline with {len(current_violations)} entries → {args.update_baseline}")
        return 0

    if all_warnings:
        for w in all_warnings:
            print(w)
        baselined = len(current_violations) - len(new_violations)
        print(
            f"[svg-gate] {len(current_violations)} file(s) outside their expected size band "
            f"({baselined} baselined, {len(new_violations)} new).\n"
            "           Bands (std / hq / rollup):\n"
            f"             std   : {BANDS['std'][0]}-{BANDS['std'][1]} bytes\n"
            f"             hq    : {BANDS['hq'][0]}-{BANDS['hq'][1]} bytes\n"
            f"             rollup: {BANDS['rollup'][0]}-{BANDS['rollup'][1]} bytes"
        )
        if new_violations and args.strict:
            print("[svg-gate] FAIL: new (non-baselined) violations present:")
            for v in new_violations:
                print(f"  - {v}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
