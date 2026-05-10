#!/usr/bin/env python3
"""L22 ultra dispatch for auto-publish blogwatcher.

Wraps :mod:`scripts.lib.svg_l22_generator` so the publisher can emit
the rich 67-70 KB three-band cover (red / amber / green stripes, KPI
badges, themed visual primitives, animated dividers) at publish time
instead of the 19 KB L20 hero default.

The auto-derived stories will not match the editorial polish of a
hand-curated ``scripts/upgrade_2026_05_to_ultra.py`` config, but the
visual structure, QR contract, and English-only enforcement are
identical, so the cover sits cleanly alongside the hand-curated
backlog without retroactive upgrades.

Three layers:

1. ``extract_three_stories`` (re-exported from ``l20_dispatch``) gives
   us ``(hero, top_right, bottom_right)`` headline+subheadline tuples
   from the post title + excerpt.
2. ``_route_*`` helpers map each story to (theme, label, visual kind,
   badge values) using simple keyword heuristics.
3. ``generate_l22_digest_svg`` builds the bands_cfg list and calls
   :func:`scripts.lib.svg_l22_generator.render_bands_svg`.

Env-flag wiring lives in ``scripts.auto_publish_news.USE_L22_ULTRA``.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Re-export the L20 helpers we depend on so callers don't need two imports.
from scripts.news.l20_dispatch import (
    _date_str_from_filename,
    _infer_kpi,
    _post_url_from_filename,
    extract_three_stories,
)

# ---------------------------------------------------------------------------
# Visual / theme / label heuristics
# ---------------------------------------------------------------------------

# Each entry: (regex on headline.lower(), visual kind). First match wins.
_VISUAL_HEURISTICS: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bcve[- ]?\d|\bzero[- ]?day|\bnetwork worm|\brce|\bexploit|\bvuln"), "lock_cve"),
    (re.compile(r"\bbotnet|\bddos|\bworm|\blateral|\binfra"), "network_nodes"),
    (re.compile(r"\bbrowser|\bchrome|\bfirefox|\bsafari|\bedge\b"), "browser_cve"),
    (re.compile(r"\bk8s|\bkubernetes|\bcontainer|\bdocker|\bcluster"), "cloud_k8s"),
    (re.compile(r"\brouter|\bfirewall|\bvpn\b|\bnetwork"), "router_mesh"),
    (re.compile(r"\bphish|\bsupply chain|\bpackage|\bregistry|\bnpm\b|\bpypi\b"), "lock_cve"),
    (re.compile(r"\bai\b|\bllm\b|\bagent|\bmodel\b|\bopenai|\bhugging|\bml\b"), "code_bars"),
    (re.compile(r"\bpatch|\bfix(es)?\b|\bupdate|\bhardening"), "shield"),
    (re.compile(r"\bbitcoin|\bcrypto|\bwallet|\bdeFi|\bblockchain"), "wallet_forensic"),
]


def _route_visual_kind(headline: str, band_idx: int) -> str:
    """Pick a visual primitive name for the band.

    Falls back to a stable rotation by band index so 3 bands always get
    visually distinct primitives even when no keyword matches.
    """
    h = (headline or "").lower()
    for pat, kind in _VISUAL_HEURISTICS:
        if pat.search(h):
            return kind
    return ["lock_cve", "network_nodes", "code_bars"][band_idx % 3]


def _route_theme(band_idx: int) -> str:
    """Hero band = red, second = amber, third = green.

    This mirrors the hand-curated convention in
    ``scripts/upgrade_2026_05_to_ultra.py``: severity descends across
    the three stripes top→bottom.
    """
    return ["red", "amber", "green"][band_idx]


_LABEL_HEURISTICS: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bransom"), "RANSOMWARE"),
    (re.compile(r"\btrojan"), "BANKING TROJAN"),
    (re.compile(r"\bworm"), "WORM CHAIN"),
    (re.compile(r"\brce|\badmin (access|exec)|\bremote code"), "ADMIN RCE"),
    (re.compile(r"\bai agent|\bagent framework"), "AI AGENT"),
    (re.compile(r"\bsupply chain|\bnpm\b|\bpypi\b|\bpackage"), "SUPPLY CHAIN"),
    (re.compile(r"\bpatch|\bfix(es)?\b"), "PATCH NOW"),
    (re.compile(r"\bcve[- ]?\d|\bvuln"), "CVE EXPLOIT"),
    (re.compile(r"\bphish"), "PHISHING"),
    (re.compile(r"\bkubernetes|\bk8s"), "KUBERNETES"),
    (re.compile(r"\bbotnet|\bddos|\bmirai"), "IOT BOTNET"),
    (re.compile(r"\bbrowser|\bchrome|\bfirefox"), "BROWSER CVE"),
    (re.compile(r"\bcrypto|\bbitcoin|\bwallet"), "CRYPTO WATCH"),
    (re.compile(r"\bzero[- ]?day"), "ZERO DAY"),
    (re.compile(r"\bcompliance|\biso\b|\bgdpr"), "COMPLIANCE"),
]


def _route_label(headline: str) -> str:
    """Short ALL-CAPS band label (≤16 chars). Falls back to ``ALERT``."""
    h = (headline or "").lower()
    for pat, label in _LABEL_HEURISTICS:
        if pat.search(h):
            return label
    return "ALERT"


def _shorten_for_metric(text: str, max_len: int = 38) -> str:
    """Trim a string to fit the metric-row text width without ellipses."""
    s = re.sub(r"\s+", " ", (text or "").strip())
    if len(s) <= max_len:
        return s
    # Cut at the last word boundary before max_len.
    cut = s[:max_len].rsplit(" ", 1)[0]
    return cut or s[:max_len]


def _shorten_for_detail(text: str, max_len: int = 110) -> str:
    """Trim a string to fit the detail row's two-line cap."""
    return _shorten_for_metric(text, max_len)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _build_band_cfg(
    headline: str,
    subheadline: str,
    band_idx: int,
) -> dict:
    """Translate (headline, subheadline) into a render_bands_svg band dict.

    All values are derived heuristically:

    * ``theme``       — by band index (red / amber / green)
    * ``visual``      — keyword-matched primitive call with sensible kwargs
    * ``label``       — keyword-matched short caps tag
    * ``badge_*``     — :func:`l20_dispatch._infer_kpi` on the headline
    * ``mini*_*``     — small stable identifiers from the band index/category
    * ``metric/detail`` and ``metric_b/detail_b`` — the headline + sub
    """
    # Lazy-import the renderer to avoid a hard dep when only metadata
    # helpers are exercised (e.g. unit tests that patch the renderer).
    from scripts.lib import svg_l22_generator as l22

    theme_name = _route_theme(band_idx)
    theme = l22.THEMES[theme_name]
    label = _route_label(headline)
    visual_kind = _route_visual_kind(headline, band_idx)

    badge_value, badge_label, badge_sub = _infer_kpi(headline)

    cy = [105, 315, 525][band_idx]

    visual_dispatch = {
        "lock_cve":       lambda: l22.v_lock_cve(500, cy, theme["accent"], theme["soft"], cvss=badge_value if len(badge_value) <= 4 else "HIGH"),
        "network_nodes":  lambda: l22.v_network_nodes(500, cy, theme["accent"], theme["soft"], label=label[:8] or "INFRA"),
        "browser_cve":    lambda: l22.v_browser_cve(500, cy, theme["accent"], theme["soft"], label=label[:6] or "CVE"),
        "cloud_k8s":      lambda: l22.v_cloud_k8s(500, cy, theme["accent"], theme["soft"]),
        "router_mesh":    lambda: l22.v_router_mesh(500, cy, theme["accent"], theme["soft"]),
        "code_bars":      lambda: l22.v_code_bars(500, cy, theme["accent"], theme["soft"], caption=label[:8] or "CODE"),
        "shield":         lambda: l22.v_shield(500, cy, theme["accent"], theme["soft"], label=label[:8] or "PATCH"),
        "wallet_forensic": lambda: l22.v_wallet_forensic(500, cy, theme["accent"], theme["soft"]),
    }
    visual_fn = visual_dispatch.get(visual_kind, visual_dispatch["lock_cve"])

    return dict(
        theme=theme_name,
        label=label,
        headline=_shorten_for_metric(headline, 32),
        metric=_shorten_for_metric(subheadline or label, 38),
        detail=_shorten_for_detail(subheadline or headline, 110),
        metric_b="See post for response checklist + CISO actions",
        detail_b=(
            "Detection rule + IOC sweep : patch state audit : "
            "tabletop drill across affected environments"
        ),
        badge_value=badge_value,
        badge_label=badge_label,
        badge_sub=badge_sub,
        mini_value=["MAY", "WK", "Q2"][band_idx % 3],
        mini_label="ISSUE",
        mini_sub="weekly",
        mini2_value=["HI", "MID", "LO"][band_idx],
        mini2_label="TIER",
        mini2_sub=theme_name,
        visual=visual_fn(),
    )


def generate_l22_digest_svg(post_info: Dict, output_path: Path) -> bool:
    """Render an L22 ultra weekly-digest cover to ``output_path``.

    Mirrors :func:`scripts.news.l20_dispatch.generate_l20_digest_svg`'s
    return-bool + write-on-success contract so the publisher can call
    either dispatch interchangeably.
    """
    try:
        from scripts.lib import svg_l22_generator as l22
    except Exception as exc:
        logging.warning(f"L22 import failed, cannot render: {exc}")
        return False

    title = str(post_info.get("title", "") or "")
    excerpt = str(post_info.get("excerpt", "") or "")
    filename = str(post_info.get("filename", "") or "")
    if not filename:
        return False

    try:
        h, tr, br = extract_three_stories(title, excerpt)
        bands_cfg = [
            _build_band_cfg(h["headline"], h["subheadline"], 0),
            _build_band_cfg(tr["headline"], tr["subheadline"], 1),
            _build_band_cfg(br["headline"], br["subheadline"], 2),
        ]
        date_str = _date_str_from_filename(filename) or ""
        url = _post_url_from_filename(filename)
        sfx_match = re.search(r"(\d{2})-(\d{2})\.svg|(\d{2})-(\d{2})$", filename)
        # Simpler: take last 4 digits of date as suffix to keep gradient ids unique.
        sfx = (date_str.replace(".", "")[-4:] if date_str else "L22")[:4] or "L22"

        aria = (
            f"Weekly digest cover {date_str}: "
            f"{h['headline']}, {tr['headline']}, {br['headline']}"
        )
        svg = l22.render_bands_svg(
            sfx=sfx,
            aria=aria,
            title=f"{date_str}: {h['headline']}",
            url=url,
            bands_cfg=bands_cfg,
            tier="ultra",
        )
        output_path.write_text(svg, encoding="utf-8")
        return True
    except Exception as exc:
        logging.warning(f"L22 SVG render failed: {exc}")
        return False


def render_l22_svg_string(post_info: Dict) -> str:
    """Return the rendered L22 ultra SVG as a string (no disk write).

    Mirrors :func:`scripts.auto_publish_news._render_l20_svg_string` so
    the publisher's existing string-pipeline can swap dispatchers on
    the ``USE_L22_ULTRA`` env flag.
    """
    try:
        from scripts.lib import svg_l22_generator as l22
    except Exception as exc:
        logging.debug(f"L22 import failed, falling back: {exc}")
        return ""

    try:
        title = str(post_info.get("title", "") or "")
        excerpt = str(post_info.get("excerpt", "") or "")
        filename = str(post_info.get("filename", "") or "")

        h, tr, br = extract_three_stories(title, excerpt)
        bands_cfg = [
            _build_band_cfg(h["headline"], h["subheadline"], 0),
            _build_band_cfg(tr["headline"], tr["subheadline"], 1),
            _build_band_cfg(br["headline"], br["subheadline"], 2),
        ]
        date_str = _date_str_from_filename(filename) or ""
        url = _post_url_from_filename(filename)
        sfx = (date_str.replace(".", "")[-4:] if date_str else "L22")[:4] or "L22"

        aria = (
            f"Weekly digest cover {date_str}: "
            f"{h['headline']}, {tr['headline']}, {br['headline']}"
        )
        return l22.render_bands_svg(
            sfx=sfx,
            aria=aria,
            title=f"{date_str}: {h['headline']}",
            url=url,
            bands_cfg=bands_cfg,
            tier="ultra",
        )
    except Exception as exc:
        logging.warning(f"L22 SVG render failed, falling back: {exc}")
        return ""
