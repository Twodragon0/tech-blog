#!/usr/bin/env python3
"""One-off extractor: convert hardcoded ``cfg_<date>()`` Python functions
into per-date YAML specs under ``_data/digest_covers/``.

This is step 2 of `.omc/plans/upgrade-script-unification.md`. Once each
source script has been extracted and the byte-identical re-render gate
(``upgrade_digest_cover.py --all --check``) passes, the source script
becomes deletable.

Strategy:

1. Monkeypatch every ``svg_l22_generator.v_*`` function with a recorder
   that captures the kwargs it was called with. The cfg's
   ``visual=l22.v_lock_cve(500, 105, accent, soft, cvss="HIGH")`` then
   gets reverse-engineered into ``visual: {kind: lock_cve, cvss: HIGH}``.
2. Import the source upgrade script's module (its top-level
   ``SPECS`` list maps filename → cfg function).
3. For each (filename, cfg_fn): call cfg_fn(), pair the recorded
   ``v_*`` calls with the cfg's bands array (one per band), translate
   into the YAML schema, and write to
   ``_data/digest_covers/{date}.yml``.

Usage::

    python3 scripts/extract_cfg_to_yaml.py scripts/upgrade_2026_05_to_ultra.py
    python3 scripts/extract_cfg_to_yaml.py --all-l22-scripts
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path
from typing import List, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.lib import svg_l22_generator as l22  # noqa: E402

SPECS_DIR = REPO_ROOT / "_data" / "digest_covers"

# Default L22 ultra source scripts to extract.
#
# We exclude `upgrade_2026_01_02_digests_to_ultra.py` because it is
# content-derived — it auto-extracts story metadata from each post body
# at runtime instead of carrying hand-curated cfg_<date>() functions.
# Static-YAML extraction wouldn't capture its dynamic behavior, so it
# stays as-is and gets phased out separately if/when its target dates
# move to hand-curation.
DEFAULT_L22_SCRIPTS = [
    "scripts/upgrade_2026_02_25_to_ultra.py",
    "scripts/upgrade_2026_04_26_to_ultra.py",
    "scripts/upgrade_2026_04_27_29_to_ultra.py",
    "scripts/upgrade_2026_05_to_ultra.py",
    "scripts/upgrade_5_digest_svgs_to_ultra.py",
]


# ---------------------------------------------------------------------------
# v_* recorder: capture (kind, kwargs) tuples for the bands in invocation order
# ---------------------------------------------------------------------------


_visual_calls: List[dict] = []


def _install_visual_recorders() -> None:
    """Wrap every ``l22.v_*`` with a recorder that captures call args."""
    for name in dir(l22):
        if not name.startswith("v_"):
            continue
        original = getattr(l22, name)
        if not callable(original):
            continue
        kind = name[2:]  # strip "v_" prefix

        def make_wrapper(orig, k):
            def wrapper(*args, **kwargs):
                # Positional args[0..3] = (cx, yc, accent, soft); the rest
                # are kwargs we want to preserve in the spec.
                _visual_calls.append({"kind": k, "kwargs": dict(kwargs)})
                return orig(*args, **kwargs)
            return wrapper

        setattr(l22, name, make_wrapper(original, kind))


# ---------------------------------------------------------------------------
# Filename / URL parsing
# ---------------------------------------------------------------------------


_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.svg$")
_URL_RE = re.compile(
    r"https://tech\.2twodragon\.com/posts/(\d{4})/(\d{2})/(\d{2})/(.+?)/"
)


def _date_slug_from_filename(filename: str) -> tuple[str, str]:
    m = _FILENAME_RE.match(filename)
    if not m:
        raise ValueError(f"unexpected filename format: {filename}")
    return m.group(1), m.group(2)


def _date_slug_from_url(url: str) -> Optional[tuple[str, str]]:
    m = _URL_RE.match(url)
    if not m:
        return None
    yyyy, mm, dd, slug = m.groups()
    return f"{yyyy}-{mm}-{dd}", slug


# ---------------------------------------------------------------------------
# cfg dict → YAML-spec dict translation
# ---------------------------------------------------------------------------


def _cfg_to_spec_dict(cfg: dict, filename: str, visual_calls: List[dict]) -> dict:
    """Convert a cfg returned by ``cfg_<date>()`` into a YAML-ready dict."""
    if len(visual_calls) != 3:
        raise RuntimeError(
            f"expected 3 visual calls per cfg, got {len(visual_calls)} "
            f"(cfg has {len(cfg.get('bands', []))} bands)"
        )

    date_str, slug = _date_slug_from_filename(filename)

    bands_yaml: List[dict] = []
    for i, band in enumerate(cfg["bands"]):
        v = visual_calls[i]
        # Build the visual: dict — kind + any kwargs the v_* received.
        visual_dict = {"kind": v["kind"]}
        visual_dict.update(v["kwargs"])

        spec_band: dict = {
            "theme": band["theme"],
            "label": band["label"],
            "headline": band["headline"],
            "metric": band["metric"],
            "detail": band["detail"],
            "badge": {
                "value": band.get("badge_value", ""),
                "label": band.get("badge_label", ""),
                "sub": band.get("badge_sub", ""),
            },
            "visual": visual_dict,
        }
        if "metric_b" in band:
            spec_band["metric_b"] = band["metric_b"]
        if "detail_b" in band:
            spec_band["detail_b"] = band["detail_b"]
        if any(k in band for k in ("mini_value", "mini_label", "mini_sub")):
            spec_band["mini"] = {
                "value": band.get("mini_value", ""),
                "label": band.get("mini_label", ""),
                "sub": band.get("mini_sub", ""),
            }
        if any(k in band for k in ("mini2_value", "mini2_label", "mini2_sub")):
            spec_band["mini2"] = {
                "value": band.get("mini2_value", ""),
                "label": band.get("mini2_label", ""),
                "sub": band.get("mini2_sub", ""),
            }
        bands_yaml.append(spec_band)

    spec: dict = {
        "date": date_str,
        "slug": slug,
        "sfx": cfg.get("sfx", date_str.replace("-", "")[-4:]),
        "title": cfg["title"],
        "aria": cfg["aria"],
        "bands": bands_yaml,
    }
    # Preserve non-canonical URLs (e.g. older /security/.../html format
    # used by 2026-02-25). The renderer auto-derives the canonical
    # /posts/YYYY/MM/DD/slug/ form when this field is omitted.
    canonical_url = (
        f"https://tech.2twodragon.com/posts/{date_str.replace('-', '/')}/{slug}/"
    )
    if cfg.get("url") and cfg["url"] != canonical_url:
        spec["url"] = cfg["url"]
    if cfg.get("tier") and cfg["tier"] != "ultra":
        spec["tier"] = cfg["tier"]
    return spec


# ---------------------------------------------------------------------------
# Per-script extraction
# ---------------------------------------------------------------------------


def extract_script(script_rel_path: str) -> List[Path]:
    """Import a source script, walk its SPECS list, write one YAML per date.

    Returns the list of YAML files written.
    """
    script_path = REPO_ROOT / script_rel_path
    if not script_path.exists():
        raise FileNotFoundError(script_rel_path)

    # Translate "scripts/foo.py" → "scripts.foo"
    module_name = (
        script_rel_path.removeprefix("scripts/").removesuffix(".py")
    )
    module_name = f"scripts.{module_name}"

    # Force reimport so module-level state (including freshly-monkeypatched
    # l22 references that the module captured at import time) is rebuilt.
    if module_name in sys.modules:
        del sys.modules[module_name]
    module = importlib.import_module(module_name)

    if not hasattr(module, "SPECS"):
        raise RuntimeError(f"{script_rel_path}: no top-level SPECS list found")

    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for filename, cfg_fn in module.SPECS:
        _visual_calls.clear()
        cfg = cfg_fn()
        # The cfg's bands list now has rendered SVG strings in 'visual'
        # — but we also captured the (kind, kwargs) via the recorder.
        spec_dict = _cfg_to_spec_dict(cfg, filename, list(_visual_calls))

        out = SPECS_DIR / f"{spec_dict['date']}.yml"
        # For multi-cover-per-date scripts (rare) we'd need to namespace
        # by slug too; the extractor errors out if it would overwrite.
        if out.exists():
            raise RuntimeError(
                f"{out} already exists (date collision); "
                f"two cfg functions produce the same date — "
                f"current cfg targets filename={filename}"
            )

        # Use safe_dump with sort_keys=False so we get a stable, readable
        # ordering matching the source cfg.
        out.write_text(
            yaml.safe_dump(spec_dict, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        written.append(out)
        print(f"  wrote {out.relative_to(REPO_ROOT)}  ({len(spec_dict['bands'])} bands)")

    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "script",
        nargs="?",
        help="Path to a single upgrade_*.py script to extract",
    )
    src.add_argument(
        "--all-l22-scripts",
        action="store_true",
        help=f"Extract every script in {DEFAULT_L22_SCRIPTS}",
    )
    args = parser.parse_args(argv)

    _install_visual_recorders()

    if args.all_l22_scripts:
        targets = DEFAULT_L22_SCRIPTS
    else:
        targets = [args.script]

    total_written = 0
    for t in targets:
        print(f"\nExtracting from {t} ...")
        try:
            written = extract_script(t)
        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            return 2
        total_written += len(written)

    print(f"\nDone. {total_written} YAML spec(s) written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
