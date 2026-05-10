#!/usr/bin/env python3
"""Parameterized renderer for weekly-digest L22 ultra covers.

Step 1 of `.omc/plans/upgrade-script-unification.md` — replaces the
hardcoded ``upgrade_*_to_ultra.py`` family with one CLI + per-date
YAML specs under ``_data/digest_covers/``.

Spec format (YAML)::

    date: 2026-05-10
    slug: Tech_Security_Weekly_Digest_Malware_Patch_AI_Agent
    sfx: MY10                 # 1-4 char suffix; gradient/filter id
    tier: ultra               # default; only "ultra" supported today
    title: "..."
    aria: |
      ...
    bands:
      - theme: red             # red | amber | green | blue | purple
        label: SUPPLY CHAIN
        headline: "..."
        metric: "..."
        detail: |
          ...
        metric_b: "..."        # optional, ultra tier only
        detail_b: |            # optional
          ...
        badge: { value: RAT, label: PAYLOAD, sub: Python }
        mini:  { value: DL,  label: VECTOR,  sub: installer }
        mini2: { value: JD,  label: VENDOR,  sub: JDownloader }
        visual:
          kind: lock_cve       # lock_cve | network_nodes | shield | code_bars
          # ...                # remaining keys passed as kwargs to v_*
          cvss: HIGH

Output goes to ``assets/images/{date}-{slug}.svg``. The QR code is
generated from the canonical Jekyll permalink so mobile scans land on
the right URL — same contract enforced by
``scripts/check_cover_qr_urls.py``.

CLI usage::

    # Single spec
    python3 scripts/upgrade_digest_cover.py --spec _data/digest_covers/2026-05-10.yml

    # All specs
    python3 scripts/upgrade_digest_cover.py --all

    # All specs from 2026-05-09 onward
    python3 scripts/upgrade_digest_cover.py --all --since 2026-05-09

    # CI gate: re-render every spec, diff vs on-disk, exit 1 on drift
    python3 scripts/upgrade_digest_cover.py --all --check
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import yaml

# Make project imports work whether invoked as script or module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"
SPECS_DIR = REPO_ROOT / "_data" / "digest_covers"


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

# Band y-coordinates inside the 1200x630 frame: top / middle / bottom.
_BAND_YC = (105, 315, 525)


# ---------------------------------------------------------------------------
# Visual primitive registry
# ---------------------------------------------------------------------------

# Each entry: (visual.kind string, callable that accepts (cx, yc, accent, soft, **kwargs))
VISUAL_REGISTRY: Dict[str, Callable[..., str]] = {
    "lock_cve":         l22.v_lock_cve,
    "network_nodes":    l22.v_network_nodes,
    "browser_cve":      l22.v_browser_cve,
    "router_mesh":      l22.v_router_mesh,
    "code_bars":        l22.v_code_bars,
    "shield":           l22.v_shield,
    "cloud_k8s":        l22.v_cloud_k8s,
    "bar_graph":        l22.v_bar_graph,
    "wallet_forensic":  l22.v_wallet_forensic,
    "senate_columns":   l22.v_senate_columns,
    "price_chart":      l22.v_price_chart,
}


# ---------------------------------------------------------------------------
# Spec loading + validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Spec:
    """In-memory representation of one digest-cover YAML spec."""
    date: str
    slug: str
    sfx: str
    title: str
    aria: str
    bands_cfg: List[dict]      # ready for l22.render_bands_svg
    tier: str = "ultra"
    # Optional explicit URL override. When unset, the URL is derived
    # from (date, slug) via the canonical Jekyll permalink format.
    # Used to preserve historical (non-canonical) URLs during extraction
    # of old cfg_*() functions that pre-date the current permalink scheme.
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


def _validate_band(idx: int, raw: dict) -> dict:
    """Convert a raw spec band dict into the kwargs render_bands_svg expects.

    Resolves the ``visual.kind`` indirection by looking up the renderer
    callable in :data:`VISUAL_REGISTRY` and invoking it with the band's
    geometric position + theme color + extra kwargs from the spec.
    """
    if not isinstance(raw, dict):
        raise ValueError(f"band {idx}: expected dict, got {type(raw).__name__}")

    required = ("theme", "label", "headline", "metric", "detail", "badge", "visual")
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"band {idx}: missing required keys: {missing}")

    theme_name = raw["theme"]
    if theme_name not in l22.THEMES:
        raise ValueError(
            f"band {idx}: unknown theme {theme_name!r}; "
            f"valid: {sorted(l22.THEMES)}"
        )
    theme = l22.THEMES[theme_name]

    visual_raw = raw["visual"]
    if not isinstance(visual_raw, dict) or "kind" not in visual_raw:
        raise ValueError(f"band {idx}: visual must be a dict with a 'kind' key")
    kind = visual_raw["kind"]
    if kind not in VISUAL_REGISTRY:
        raise ValueError(
            f"band {idx}: unknown visual.kind {kind!r}; "
            f"valid: {sorted(VISUAL_REGISTRY)}"
        )

    extra_kwargs = {k: v for k, v in visual_raw.items() if k != "kind"}
    visual_fn = VISUAL_REGISTRY[kind]
    visual_svg = visual_fn(500, _BAND_YC[idx], theme["accent"], theme["soft"], **extra_kwargs)

    badge = raw["badge"]
    mini = raw.get("mini") or {}
    mini2 = raw.get("mini2") or {}

    band_cfg: dict = {
        "theme": theme_name,
        "label": raw["label"],
        "headline": raw["headline"],
        "metric": raw["metric"],
        "detail": raw["detail"],
        "badge_value": badge.get("value", ""),
        "badge_label": badge.get("label", ""),
        "badge_sub": badge.get("sub", ""),
        "visual": visual_svg,
    }

    # Optional ultra-tier rows + secondary cards.
    if "metric_b" in raw:
        band_cfg["metric_b"] = raw["metric_b"]
    if "detail_b" in raw:
        band_cfg["detail_b"] = raw["detail_b"]
    if mini:
        band_cfg["mini_value"] = mini.get("value", "")
        band_cfg["mini_label"] = mini.get("label", "")
        band_cfg["mini_sub"] = mini.get("sub", "")
    if mini2:
        band_cfg["mini2_value"] = mini2.get("value", "")
        band_cfg["mini2_label"] = mini2.get("label", "")
        band_cfg["mini2_sub"] = mini2.get("sub", "")

    return band_cfg


def load_spec(path: Path) -> Spec:
    """Parse and validate a single YAML spec file.

    Raises:
        ValueError: missing/unknown fields, wrong band count, etc.
        FileNotFoundError: if ``path`` does not exist.
        yaml.YAMLError: malformed YAML.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: spec must be a YAML mapping at the top level")

    for key in ("date", "slug", "title", "aria", "bands"):
        if key not in raw:
            raise ValueError(f"{path}: missing required key {key!r}")

    bands = raw["bands"]
    if not isinstance(bands, list) or len(bands) != 3:
        raise ValueError(
            f"{path}: bands must be a list of exactly 3 entries; got {len(bands) if isinstance(bands, list) else type(bands).__name__}"
        )

    bands_cfg = [_validate_band(i, b) for i, b in enumerate(bands)]

    sfx = raw.get("sfx") or raw["date"].replace("-", "")[-4:]
    tier = raw.get("tier", "ultra")
    if tier not in ("ultra", "standard"):
        raise ValueError(f"{path}: tier must be 'ultra' or 'standard', got {tier!r}")

    return Spec(
        date=raw["date"],
        slug=raw["slug"],
        sfx=sfx,
        title=raw["title"],
        aria=raw["aria"].strip(),
        bands_cfg=bands_cfg,
        tier=tier,
        url_override=raw.get("url"),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render(spec: Spec) -> str:
    """Render a Spec to an SVG string via :func:`l22.render_bands_svg`."""
    return l22.render_bands_svg(
        sfx=spec.sfx,
        aria=spec.aria,
        title=spec.title,
        url=spec.url,
        bands_cfg=spec.bands_cfg,
        tier=spec.tier,
    )


def write(spec: Spec, *, dry_run: bool = False) -> int:
    """Render and write a spec to disk. Returns size in bytes (0 if dry-run)."""
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
    # Avoid dumping the entire SVG on stderr; report sizes + first-diff line.
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
    """Resolve the CLI flags into a deduplicated list of spec paths."""
    if args.spec:
        return [Path(args.spec)]
    if not args.all:
        raise SystemExit("error: pass --spec PATH or --all")
    if not SPECS_DIR.exists():
        return []
    paths = sorted(SPECS_DIR.glob("*.yml"))
    if args.since:
        # Filter by spec date. This is cheap because the date is also
        # the filename prefix (YYYY-MM-DD-... or YYYY-MM-DD.yml).
        paths = [p for p in paths if p.stem >= args.since]
    return paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render L22 ultra weekly-digest covers from YAML specs.",
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
        choices=("ultra", "standard"),
        help="Override the spec's tier field for every spec rendered",
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
        if args.tier:
            spec = Spec(**{**spec.__dict__, "tier": args.tier})

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
