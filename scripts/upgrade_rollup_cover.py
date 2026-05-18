#!/usr/bin/env python3
"""Parameterized renderer for rollup (weekly/monthly) digest covers.

Sibling of ``scripts/upgrade_digest_cover.py``. Both pipelines share the
same CLI surface (``--spec``, ``--all``, ``--since``, ``--check``,
``--dry-run``) and the same byte-stable drift-gate contract, but they
use separate renderers + spec dirs to avoid schema-union foot-guns:

  - daily L22 ultra weekly digests: ``_data/digest_covers/*.yml``
    rendered by ``scripts/upgrade_digest_cover.py``.
  - rollup (week/month index) covers: ``_data/rollup_covers/*.yml``
    rendered by THIS script.
  - L20 hero + 2-card covers:        ``_data/l20_covers/*.yml``
    rendered by ``scripts/upgrade_l20_cover.py``.
  - L25 single-topic post covers:    ``_data/l25_covers/*.yml``
    rendered by ``scripts/upgrade_l25_cover.py`` (forward-looking;
    spec dir ships empty).

See ``.omc/plans/rollup-cover-design.md`` for the design rationale and
spec schema.

CLI usage::

    python3 scripts/upgrade_rollup_cover.py --spec _data/rollup_covers/2026-04-19.yml
    python3 scripts/upgrade_rollup_cover.py --all
    python3 scripts/upgrade_rollup_cover.py --all --since 2026-04-01
    python3 scripts/upgrade_rollup_cover.py --all --check      # CI gate
    python3 scripts/upgrade_rollup_cover.py --all --dry-run    # no writes
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Make project imports work whether invoked as script or module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_rollup_generator as roll  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"
SPECS_DIR = REPO_ROOT / "_data" / "rollup_covers"


# ---------------------------------------------------------------------------
# Schema enums
# ---------------------------------------------------------------------------

VALID_KINDS = ("weekly_rollup", "monthly_index")
VALID_SOURCES = ("redirect_from", "index_table", "manual")
VALID_SEVERITIES = ("HIGH", "MEDIUM", "LOW")

# Allowed top-level keys; anything else triggers a "unknown key" rejection.
ALLOWED_KEYS = frozenset({
    "date", "slug", "kind", "period_label", "period_short",
    "daily_count", "daily_count_source", "sfx", "title", "aria",
    "top_highlights", "days", "footer", "url",
})


def _short_path(p: Path) -> str:
    """Render a path relative to REPO_ROOT when possible, else absolute."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Spec dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Spec:
    """In-memory representation of one rollup-cover YAML spec.

    Mirrors the field layout of ``rollup_covers/*.yml`` so ``render_rollup_svg``
    can consume ``spec.as_dict()`` directly.
    """
    date: str
    slug: str
    kind: str
    period_label: str
    period_short: str
    daily_count: int
    daily_count_source: str
    sfx: str
    title: str
    aria: str
    top_highlights: List[dict]
    days: List[dict]
    footer: Dict[str, Any] = field(default_factory=dict)
    url_override: Optional[str] = None

    @property
    def filename(self) -> str:
        return f"{self.date}-{self.slug}.svg"

    @property
    def output_path(self) -> Path:
        return ASSETS / self.filename

    @property
    def url(self) -> str:
        if self.url_override:
            return self.url_override
        yyyy, mm, dd = self.date.split("-")
        return f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{self.slug}/"

    def as_dict(self) -> dict:
        return {
            "date": self.date,
            "slug": self.slug,
            "kind": self.kind,
            "period_label": self.period_label,
            "period_short": self.period_short,
            "daily_count": self.daily_count,
            "daily_count_source": self.daily_count_source,
            "sfx": self.sfx,
            "title": self.title,
            "aria": self.aria,
            "top_highlights": self.top_highlights,
            "days": self.days,
            "footer": self.footer,
            "url": self.url,
        }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_highlight(idx: int, raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise ValueError(f"top_highlights[{idx}]: expected dict, got {type(raw).__name__}")
    required = ("severity", "label", "headline", "source")
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"top_highlights[{idx}]: missing keys {missing}")
    sev = str(raw["severity"]).upper()
    if sev not in VALID_SEVERITIES:
        raise ValueError(
            f"top_highlights[{idx}]: severity must be one of {VALID_SEVERITIES}, got {raw['severity']!r}"
        )
    return {
        "severity": sev,
        "label": str(raw["label"]),
        "headline": str(raw["headline"]),
        "detail": str(raw.get("detail", "") or ""),
        "source": str(raw["source"]),
    }


def _validate_day(idx: int, raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise ValueError(f"days[{idx}]: expected dict, got {type(raw).__name__}")
    required = ("date", "severity", "tag")
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"days[{idx}]: missing keys {missing}")
    sev = str(raw["severity"]).upper()
    if sev not in VALID_SEVERITIES:
        raise ValueError(
            f"days[{idx}]: severity must be one of {VALID_SEVERITIES}, got {raw['severity']!r}"
        )
    return {
        "date": str(raw["date"]),
        "severity": sev,
        "tag": str(raw["tag"]),
    }


def load_spec(path: Path) -> Spec:
    """Parse and validate a single rollup-cover YAML spec file.

    Raises:
        ValueError: missing/unknown fields, wrong types, invalid enums.
        FileNotFoundError: ``path`` does not exist.
        yaml.YAMLError: malformed YAML.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: spec must be a YAML mapping at the top level")

    # Reject unknown top-level keys early — protects against typos.
    extra = set(raw) - ALLOWED_KEYS
    if extra:
        raise ValueError(f"{path}: unknown top-level keys: {sorted(extra)}")

    required = (
        "date", "slug", "kind", "period_label", "period_short",
        "daily_count", "daily_count_source",
        "title", "aria", "top_highlights", "days",
    )
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"{path}: missing required keys: {missing}")

    kind = raw["kind"]
    if kind not in VALID_KINDS:
        raise ValueError(f"{path}: kind must be one of {VALID_KINDS}, got {kind!r}")

    source = raw["daily_count_source"]
    if source not in VALID_SOURCES:
        raise ValueError(
            f"{path}: daily_count_source must be one of {VALID_SOURCES}, got {source!r}"
        )

    top_highlights = raw["top_highlights"]
    if not isinstance(top_highlights, list) or len(top_highlights) != 3:
        raise ValueError(
            f"{path}: top_highlights must be a list of exactly 3 entries; "
            f"got {len(top_highlights) if isinstance(top_highlights, list) else type(top_highlights).__name__}"
        )
    top_highlights = [_validate_highlight(i, h) for i, h in enumerate(top_highlights)]

    days = raw["days"]
    if not isinstance(days, list) or not days:
        raise ValueError(f"{path}: days must be a non-empty list")
    # Schema gate: weekly_rollup 5-7, monthly_index 4-31. The 5-7 weekly range
    # accommodates Week1 April (5 dailies 4/1..4/5); Week2/Week3 have 7.
    n = len(days)
    if kind == "weekly_rollup" and not (5 <= n <= 7):
        raise ValueError(
            f"{path}: weekly_rollup requires 5..7 days, got {n}"
        )
    if kind == "monthly_index" and not (4 <= n <= 31):
        raise ValueError(
            f"{path}: monthly_index requires 4..31 days, got {n}"
        )
    days = [_validate_day(i, d) for i, d in enumerate(days)]

    daily_count = raw["daily_count"]
    if not isinstance(daily_count, int) or daily_count < 1:
        raise ValueError(f"{path}: daily_count must be a positive int, got {daily_count!r}")

    sfx = raw.get("sfx") or raw["date"].replace("-", "")[-4:]

    return Spec(
        date=str(raw["date"]),
        slug=str(raw["slug"]),
        kind=kind,
        period_label=str(raw["period_label"]),
        period_short=str(raw["period_short"]),
        daily_count=daily_count,
        daily_count_source=source,
        sfx=str(sfx),
        title=str(raw["title"]),
        aria=str(raw["aria"]).strip(),
        top_highlights=top_highlights,
        days=days,
        footer=raw.get("footer") or {},
        url_override=raw.get("url"),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render(spec: Spec) -> str:
    """Render a Spec to a complete SVG string."""
    return roll.render_rollup_svg(spec.as_dict())


def write(spec: Spec, *, dry_run: bool = False) -> int:
    """Render and write a spec to disk. Returns size in bytes (0 if dry-run)."""
    svg = render(spec)
    if dry_run:
        return len(svg.encode("utf-8"))
    spec.output_path.write_text(svg, encoding="utf-8")
    return len(svg.encode("utf-8"))


def check(spec: Spec) -> Optional[str]:
    """Re-render a spec and compare against the on-disk SVG.

    Returns ``None`` on byte-equal match, otherwise a diff summary string.
    """
    fresh = render(spec)
    if not spec.output_path.exists():
        return f"DRIFT: {_short_path(spec.output_path)} does not exist on disk"
    on_disk = spec.output_path.read_text(encoding="utf-8")
    if fresh == on_disk:
        return None
    fresh_lines = fresh.splitlines()
    on_disk_lines = on_disk.splitlines()
    first_diff = None
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _gather_specs(args: argparse.Namespace) -> List[Path]:
    """Resolve CLI flags into a deduplicated list of spec paths."""
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
        description="Render rollup (weekly/monthly) digest covers from YAML specs.",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--spec", help="Render exactly one spec file")
    src.add_argument(
        "--all",
        action="store_true",
        help=f"Walk {_short_path(SPECS_DIR)}/*.yml and render each",
    )
    parser.add_argument(
        "--since",
        help="With --all, skip spec files whose stem (date) is < SINCE",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render in memory and report stats; do not write any SVG",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Re-render each spec and exit 1 if any on-disk SVG drifts",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    paths = _gather_specs(args)
    if not paths:
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
