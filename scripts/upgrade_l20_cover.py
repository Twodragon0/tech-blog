#!/usr/bin/env python3
"""Parameterized renderer for L20 hero (HERO + 2 CARDS) weekly-digest covers.

Sibling of ``scripts/upgrade_digest_cover.py`` and
``scripts/upgrade_rollup_cover.py``. All three pipelines share the same
CLI surface (``--spec``, ``--all``, ``--since``, ``--check``,
``--dry-run``) and the same byte-stable drift-gate contract, but they
use separate renderers + spec dirs to avoid schema-union foot-guns:

  - daily L22 ultra weekly digests:   ``_data/digest_covers/*.yml``
    rendered by ``scripts/upgrade_digest_cover.py``
  - weekly/monthly rollup index covers: ``_data/rollup_covers/*.yml``
    rendered by ``scripts/upgrade_rollup_cover.py``
  - L20 hero + 2-card covers:          ``_data/l20_covers/*.yml``
    rendered by THIS script

See ``.omc/plans/l20-hero-unification.md`` for the design rationale and
spec schema.

Spec format (YAML)::

    date: 2026-03-16
    slug: Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update
    date_str: 2026.03.16                # display string for header
    post_title: "..."                   # SVG <title>
    url: https://...                    # optional override
    hero:
      tag: OSS RELEASE
      index: "01"
      theme: red                        # red | blue | amber | green | purple
      visual: code_injection            # one of 8 vb_* keys
      headline: "..."
      subheadline: "..."
      kpi_value: v1.0
      kpi_label: RELEASE
      kpi_sub: "MIT licensed"
      action: "ADOPT - HARDEN AI AGENTS NOW"
    top_right:
      tag: HIGH
      index: "02"
      theme: blue
      visual: hub_spoke
      headline: "..."
      subheadline: "..."
      kpi_value: GA
      kpi_label: STATUS
      kpi_sub: "..."
    bottom_right:
      tag: MEDIUM
      index: "03"
      theme: amber
      visual: supply_chain_pipe
      headline: "..."
      subheadline: "..."
      kpi_value: "$50M"
      kpi_label: TVL
      kpi_sub: "first 24h"

Output goes to ``assets/images/{date}-{slug}.svg``. The QR code is
generated from the canonical Jekyll permalink so mobile scans land on
the right URL.

CLI usage::

    # Single spec
    python3 scripts/upgrade_l20_cover.py --spec _data/l20_covers/2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update.yml

    # All specs
    python3 scripts/upgrade_l20_cover.py --all

    # All specs from 2026-03-16 onward
    python3 scripts/upgrade_l20_cover.py --all --since 2026-03-16

    # CI gate: re-render every spec, diff vs on-disk, exit 1 on drift
    python3 scripts/upgrade_l20_cover.py --all --check
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Make project imports work whether invoked as script or module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l20_hero as l20  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"
SPECS_DIR = REPO_ROOT / "_data" / "l20_covers"


# ---------------------------------------------------------------------------
# Schema enums
# ---------------------------------------------------------------------------

# Allowed top-level keys; anything else triggers a "unknown key" rejection.
_ALLOWED_TOP_LEVEL_KEYS = frozenset({
    "date", "slug", "date_str", "post_title", "url",
    "hero", "top_right", "bottom_right",
})

# Required top-level keys.
_REQUIRED_TOP_LEVEL_KEYS = (
    "date", "slug", "date_str", "post_title",
    "hero", "top_right", "bottom_right",
)

# Story-dict required keys (cards). The hero dict additionally requires `action`.
_STORY_REQUIRED = (
    "tag", "index", "theme", "visual",
    "headline", "subheadline",
    "kpi_value", "kpi_label", "kpi_sub",
)
_HERO_REQUIRED = _STORY_REQUIRED + ("action",)

_STORY_ALLOWED = frozenset(_STORY_REQUIRED)
_HERO_ALLOWED = frozenset(_HERO_REQUIRED)


def _short_path(p: Path) -> str:
    """Render a path relative to REPO_ROOT when possible, else absolute.

    Tests redirect ASSETS / SPECS_DIR to tmp dirs outside the repo;
    ``Path.relative_to(REPO_ROOT)`` raises ValueError in that case, so
    fall back to the absolute string when the path is unrelated.
    """
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Spec dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Spec:
    """In-memory representation of one L20 hero YAML spec.

    Field order mirrors :func:`scripts.lib.svg_l20_hero.render_l20_hero`
    so ``render(spec)`` is a thin glue layer.
    """
    date: str
    slug: str
    date_str: str
    post_title: str
    hero: Dict[str, Any]
    top_right: Dict[str, Any]
    bottom_right: Dict[str, Any]
    # Optional explicit URL override. When unset, the URL is derived
    # from (date, slug) via the canonical Jekyll permalink format.
    url_override: Optional[str] = None

    @property
    def filename(self) -> str:
        return f"{self.date}-{self.slug}.svg"

    @property
    def output_path(self) -> Path:
        return ASSETS / self.filename

    @property
    def url(self) -> str:
        return self.url_override or _post_url(self.date, self.slug)


def _post_url(date: str, slug: str) -> str:
    """Canonical Jekyll permalink (underscore-preserved per Jekyll convention)."""
    yyyy, mm, dd = date.split("-")
    return f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug}/"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_story(name: str, raw: Any, *, is_hero: bool) -> Dict[str, Any]:
    """Validate a hero / top_right / bottom_right dict.

    The hero dict additionally requires ``action`` (the red call-to-action
    ribbon at y=548 in the rendered SVG). Card dicts must NOT carry
    ``action`` — accepting it silently would let editors leak hero copy
    into a card slot where the renderer would ignore it.
    """
    if not isinstance(raw, dict):
        raise ValueError(f"{name}: expected dict, got {type(raw).__name__}")

    required = _HERO_REQUIRED if is_hero else _STORY_REQUIRED
    allowed = _HERO_ALLOWED if is_hero else _STORY_ALLOWED

    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"{name}: missing required keys: {missing}")

    extra = set(raw) - allowed
    if extra:
        raise ValueError(f"{name}: unknown keys: {sorted(extra)}")

    theme = raw["theme"]
    if theme not in l20.THEMES:
        raise ValueError(
            f"{name}: unknown theme {theme!r}; valid: {sorted(l20.THEMES)}"
        )

    visual = raw["visual"]
    if visual not in l20.VISUAL_BUILDERS:
        raise ValueError(
            f"{name}: unknown visual {visual!r}; valid: {sorted(l20.VISUAL_BUILDERS)}"
        )

    # Stringify scalar fields. The renderer escapes / strips Hangul, but
    # YAML may decode numeric-looking values (e.g., 9.8) to float; coerce
    # to str so the renderer never crashes on .replace(). Coercion is
    # also a defense against YAML auto-typing of versions like ``1.0``.
    out: Dict[str, Any] = {}
    for k in required:
        out[k] = "" if raw[k] is None else str(raw[k])
    return out


def load_spec(path: Path) -> Spec:
    """Parse and validate a single YAML spec file.

    Raises:
        ValueError: missing/unknown fields, wrong enums, malformed types.
        FileNotFoundError: ``path`` does not exist.
        yaml.YAMLError: malformed YAML.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: spec must be a YAML mapping at the top level")

    # Reject unknown top-level keys early — protects against typos.
    extra = set(raw) - _ALLOWED_TOP_LEVEL_KEYS
    if extra:
        raise ValueError(f"{path}: unknown top-level keys: {sorted(extra)}")

    missing = [k for k in _REQUIRED_TOP_LEVEL_KEYS if k not in raw]
    if missing:
        raise ValueError(f"{path}: missing required keys: {missing}")

    hero = _validate_story("hero", raw["hero"], is_hero=True)
    top_right = _validate_story("top_right", raw["top_right"], is_hero=False)
    bottom_right = _validate_story("bottom_right", raw["bottom_right"], is_hero=False)

    return Spec(
        date=str(raw["date"]),
        slug=str(raw["slug"]),
        date_str=str(raw["date_str"]),
        post_title=str(raw["post_title"]),
        hero=hero,
        top_right=top_right,
        bottom_right=bottom_right,
        url_override=str(raw["url"]) if raw.get("url") else None,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render(spec: Spec) -> str:
    """Render a Spec to a complete SVG string via :func:`l20.render_l20_hero`."""
    return l20.render_l20_hero(
        date_str=spec.date_str,
        hero=spec.hero,
        top_right=spec.top_right,
        bottom_right=spec.bottom_right,
        url=spec.url,
        post_title=spec.post_title,
    )


def write(spec: Spec, *, dry_run: bool = False) -> int:
    """Render and write a spec to disk. Returns size in bytes (0 if dry-run).

    Matches the L22 digest CLI semantics (``upgrade_digest_cover.py:write``):
    a dry-run returns 0 bytes rather than the rendered-but-not-written size.
    The rollup CLI returns the rendered byte count even on dry-run; we
    deliberately mirror the digest CLI here to keep the more useful
    "did it actually hit disk?" signal in CLI output.
    """
    svg = render(spec)
    if dry_run:
        return 0
    spec.output_path.write_text(svg, encoding="utf-8")
    return len(svg.encode("utf-8"))


def check(spec: Spec) -> Optional[str]:
    """Re-render a spec and compare against the on-disk SVG.

    Returns:
        ``None`` if on-disk content matches the freshly-rendered output.
        A diff-like description string when they differ (drift detected).
    """
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
        # Filter by spec date. This is cheap because the date is the
        # filename prefix (YYYY-MM-DD-<slug>.yml).
        paths = [p for p in paths if p.stem >= args.since]
    return paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render L20 hero (HERO + 2 cards) weekly-digest covers from YAML specs.",
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
        "--tier",
        choices=("l20",),
        default="l20",
        help="Tier selector (only 'l20' supported today; kept for CLI symmetry)",
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
