#!/usr/bin/env python3
"""CLI driver for L25-single (single-topic post) covers.

Sibling of ``upgrade_l20_cover.py`` / ``upgrade_digest_cover.py`` /
``upgrade_rollup_cover.py``. Shared CLI: ``--spec`` / ``--all`` /
``--since`` / ``--check`` / ``--dry-run``. Same byte-stable drift-gate
contract. Each pipeline uses its own renderer + spec dir:

  - L22 daily digests:        ``_data/digest_covers/*.yml``
  - rollup index covers:      ``_data/rollup_covers/*.yml``
  - L20 hero + 2-card covers: ``_data/l20_covers/*.yml``
  - L25 single-topic covers:  ``_data/l25_covers/*.yml`` (THIS)

L25-single is **forward-looking** — the 28 hand-crafted 2025 SVGs that
carry the marker ``profile: high-quality-cover (2025 upgraded L25-
single)`` are grandfathered and must NOT be regenerated from YAML. The
spec dir ships empty (``.gitkeep``).

Spec format (YAML)::

    date: 2026-06-01
    slug: My_Single_Topic_Post
    post_title: "My Single Topic Post"
    category: incident        # incident | course | tutorial | guide | event
    theme: red                # red | blue | amber | green | purple
    headline: "Main 34pt headline"
    subheadline: "Secondary 18pt line"
    visual: network_nodes     # one of svg_l25_single.VISUAL_BUILDERS
    tag_chips:    [SUPPLY CHAIN, CVE-2026-1234]   # optional, 0-5
    kpi_strip:                                    # optional, 0-3
      - { label: SEVERITY, value: HIGH }
    url: https://...          # optional; derived from (date, slug) when absent

Output: ``assets/images/{date}-{slug}.svg``.

CLI::

    python3 scripts/upgrade_l25_cover.py --spec _data/l25_covers/X.yml
    python3 scripts/upgrade_l25_cover.py --all
    python3 scripts/upgrade_l25_cover.py --all --since 2026-06-01
    python3 scripts/upgrade_l25_cover.py --all --check       # CI gate
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l25_single as l25  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"
SPECS_DIR = REPO_ROOT / "_data" / "l25_covers"


# Schema -------------------------------------------------------------------

_ALLOWED_TOP_LEVEL_KEYS = frozenset({
    "date", "slug", "post_title", "category", "theme",
    "headline", "subheadline", "visual",
    "tag_chips", "kpi_strip", "url",
})
_REQUIRED_TOP_LEVEL_KEYS = (
    "date", "slug", "post_title", "category", "theme",
    "headline", "subheadline", "visual",
)
_KPI_REQUIRED = ("label", "value")
_KPI_ALLOWED = frozenset(_KPI_REQUIRED)


def _short_path(p: Path) -> str:
    """REPO_ROOT-relative path when possible, else absolute (tmp dirs)."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


@dataclass(frozen=True)
class Spec:
    """In-memory representation of one L25-single YAML spec."""
    date: str
    slug: str
    post_title: str
    category: str
    theme: str
    headline: str
    subheadline: str
    visual: str
    tag_chips: tuple
    kpi_strip: tuple
    url_override: Optional[str] = None

    @property
    def filename(self) -> str:
        return f"{self.date}-{self.slug}.svg"

    @property
    def output_path(self) -> Path:
        return ASSETS / self.filename

    @property
    def url(self) -> str:
        return self.url_override or l25._post_url(self.date, self.slug)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date, "slug": self.slug, "post_title": self.post_title,
            "category": self.category, "theme": self.theme,
            "headline": self.headline, "subheadline": self.subheadline,
            "visual": self.visual, "tag_chips": list(self.tag_chips),
            "kpi_strip": [dict(c) for c in self.kpi_strip], "url": self.url,
        }


# Validation ---------------------------------------------------------------

def _validate_kpi(idx: int, raw: Any) -> Dict[str, str]:
    """Validate a single KPI cell dict ({label, value})."""
    if not isinstance(raw, dict):
        raise ValueError(
            f"kpi_strip[{idx}]: expected dict, got {type(raw).__name__}"
        )
    missing = [k for k in _KPI_REQUIRED if k not in raw]
    if missing:
        raise ValueError(f"kpi_strip[{idx}]: missing keys: {missing}")
    extra = set(raw) - _KPI_ALLOWED
    if extra:
        raise ValueError(f"kpi_strip[{idx}]: unknown keys: {sorted(extra)}")
    # Coerce scalars to str — YAML may decode "1.0" as float.
    return {k: "" if raw[k] is None else str(raw[k]) for k in _KPI_REQUIRED}


def _require_enum(path: Path, field: str, value: str, allowed) -> None:
    if value not in allowed:
        raise ValueError(
            f"{path}: unknown {field} {value!r}; valid: {sorted(allowed)}"
        )


def _require_list(path: Path, field: str, value, max_len: int) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{path}: {field} must be a list")
    if len(value) > max_len:
        raise ValueError(
            f"{path}: {field} must have at most {max_len} entries (got {len(value)})"
        )
    return value


def load_spec(path: Path) -> Spec:
    """Parse + validate a YAML spec.  Raises ValueError on schema issues."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: spec must be a YAML mapping at the top level")

    extra = set(raw) - _ALLOWED_TOP_LEVEL_KEYS
    if extra:
        raise ValueError(f"{path}: unknown top-level keys: {sorted(extra)}")
    missing = [k for k in _REQUIRED_TOP_LEVEL_KEYS if k not in raw]
    if missing:
        raise ValueError(f"{path}: missing required keys: {missing}")

    category, theme, visual = str(raw["category"]), str(raw["theme"]), str(raw["visual"])
    _require_enum(path, "category", category, l25.CATEGORIES)
    _require_enum(path, "theme", theme, l25.THEMES)
    _require_enum(path, "visual", visual, l25.VISUAL_BUILDERS)

    chips = _require_list(path, "tag_chips", raw.get("tag_chips") or [], 5)
    kpis = _require_list(path, "kpi_strip", raw.get("kpi_strip") or [], 3)

    return Spec(
        date=str(raw["date"]), slug=str(raw["slug"]),
        post_title=str(raw["post_title"]),
        category=category, theme=theme, visual=visual,
        headline=str(raw["headline"]), subheadline=str(raw["subheadline"]),
        tag_chips=tuple(str(t) for t in chips),
        kpi_strip=tuple(_validate_kpi(i, c) for i, c in enumerate(kpis)),
        url_override=str(raw["url"]) if raw.get("url") else None,
    )


# Render / write / check ---------------------------------------------------

def render(spec: Spec) -> str:
    return l25.render_l25_single(spec.to_dict())


def write(spec: Spec, *, dry_run: bool = False) -> int:
    """Render + write.  Returns bytes written (0 if dry-run).  Matches the
    L20/L22 digest CLI semantic: dry-run reports 0 so the "did it hit
    disk?" signal stays in CLI output."""
    svg = render(spec)
    if dry_run:
        return 0
    spec.output_path.write_text(svg, encoding="utf-8")
    return len(svg.encode("utf-8"))


def check(spec: Spec) -> Optional[str]:
    """Returns None when on-disk SVG matches the freshly-rendered output,
    else a DRIFT description string."""
    fresh = render(spec)
    if not spec.output_path.exists():
        return f"DRIFT: {_short_path(spec.output_path)} does not exist on disk"
    on_disk = spec.output_path.read_text(encoding="utf-8")
    if fresh == on_disk:
        return None
    fresh_lines = fresh.splitlines()
    on_disk_lines = on_disk.splitlines()
    first_diff: Optional[int] = None
    for i, (a, b) in enumerate(zip(on_disk_lines, fresh_lines), 1):
        if a != b:
            first_diff = i
            break
    return (
        f"DRIFT: {_short_path(spec.output_path)} "
        f"on_disk={len(on_disk)}B/{len(on_disk_lines)}L vs "
        f"fresh={len(fresh)}B/{len(fresh_lines)}L "
        f"first_diff_line={first_diff}"
    )


# CLI ----------------------------------------------------------------------

def _gather_specs(args: argparse.Namespace) -> List[Path]:
    if args.spec:
        return [Path(args.spec)]
    if not args.all:
        raise SystemExit("error: pass --spec PATH or --all")
    if not SPECS_DIR.exists():
        return []
    paths = sorted(SPECS_DIR.glob("*.yml"))
    if args.since:
        paths = [p for p in paths if p.stem >= args.since]
    return paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render L25 single-topic post covers from YAML specs.",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--spec", help="Render exactly one spec file")
    src.add_argument(
        "--all", action="store_true",
        help=f"Walk {_short_path(SPECS_DIR)}/*.yml and render each",
    )
    parser.add_argument("--since", help="With --all, skip stems < SINCE")
    parser.add_argument(
        "--tier", choices=("l25",), default="l25",
        help="Tier selector (only 'l25' today; kept for CLI symmetry)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Render in memory; do not write any SVG",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Re-render each spec and exit 1 if any on-disk SVG drifts",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    paths = _gather_specs(args)
    if not paths:
        # Forward-looking infra: empty spec dir is a valid steady state.
        print("no specs to process")
        return 0

    drift: List[str] = []
    rendered = 0
    for p in paths:
        try:
            spec = load_spec(p)
        except (ValueError, yaml.YAMLError) as exc:
            print(f"  ERROR loading {_short_path(p)}: {exc}", file=sys.stderr)
            return 2

        if args.check:
            issue = check(spec)
            if issue:
                print(f"  {issue}", file=sys.stderr)
                drift.append(issue)
            else:
                print(f"  OK    {spec.filename}")
        else:
            size = write(spec, dry_run=args.dry_run)
            tag = "[DRY] " if args.dry_run else ""
            print(f"  {tag}wrote {spec.filename}: {size} bytes")
            rendered += 1

    if args.check:
        if drift:
            print(f"\n{len(drift)} spec(s) drifted from on-disk SVG", file=sys.stderr)
            return 1
        print(f"\n{len(paths)} specs OK")
        return 0
    print(f"\n{rendered} spec(s) rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
