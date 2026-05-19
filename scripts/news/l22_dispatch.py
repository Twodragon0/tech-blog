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

# ---------------------------------------------------------------------------
# Band-visual marker injection
# ---------------------------------------------------------------------------

# The three band visual groups are positioned at fixed cy values in every
# L22 cover.  The auto-publish path injects a comment marker immediately
# before each group so the CI gate can verify visual variety without parsing
# SVG primitives.
_BAND_CY = [105, 315, 525]


def _inject_band_visual_markers(svg: str, visual_kinds: List[str]) -> str:
    """Inject ``<!-- band-visual: {kind} -->`` before each band visual group.

    Targets the three ``<g transform="translate(500,{cy})">`` elements that
    each visual function (``v_lock_cve``, ``v_network_nodes``, …) emits.
    The golden-snapshot / spec-driven render path does NOT call this
    function, so byte-stable YAML specs remain unchanged.

    Args:
        svg: Rendered SVG string from ``render_bands_svg``.
        visual_kinds: List of 3 visual kind strings (same order as bands).

    Returns:
        SVG string with markers prepended to each band visual group.
    """
    for cy, kind in zip(_BAND_CY, visual_kinds):
        target = f'<g transform="translate(500,{cy})">'
        replacement = f'<!-- band-visual: {kind} -->\n{target}'
        svg = svg.replace(target, replacement, 1)
    return svg

# Re-export the L20 helpers we depend on so callers don't need two imports.
from scripts.news.l20_dispatch import (
    _date_str_from_filename,
    _has_hangul,
    _infer_kpi,
    _post_url_from_filename,
    _shorten,
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
# Excerpt-driven headline extraction (Fix 2)
# ---------------------------------------------------------------------------

# Korean-locale boilerplate that wraps the 3 anchor stories in auto-published
# digest excerpts. Examples (from 2026-05-12..18 excerpts):
#
#   "...을 중심으로 2026년 05월 13일 주요 보안/기술 뉴스 29건과 대응 우선순위를 정리합니다."
#   "Vulnerability, Security, Agent 등 최신 위협 동향과 ..."
#
# We chop everything from "을/를 중심으로" (or the literal phrase "정리합니다")
# onward, then split the prefix on the standard Korean enumerator chars
# ( , / · / · ) to recover the 3 anchor story phrases.
_EXCERPT_BOILERPLATE_RE = re.compile(
    r"(?:을|를)\s*중심으로.*$|정리합니다.*$|등\s*최신.*$|등\s*DevSecOps.*$",
)

# Splitter for the prefix: comma, semicolon, the unicode middle-dot
# (U+00B7), ASCII bullet, pipe. Hyphens stay attached to words
# ("Exim BDAT"). Whitespace around separators is optional.
_EXCERPT_SPLIT_RE = re.compile(r"\s*[,;\u00b7\u2022|/]\s*")


def extract_three_stories_from_excerpt(
    title: str,
    excerpt: str,
    filename: str,
) -> Optional[Tuple[Dict, Dict, Dict]]:
    """Mine 3 short anchor-story headlines from a Korean digest excerpt.

    Returns ``None`` when the excerpt does not carry the auto-publisher's
    boilerplate shape (i.e. cannot be parsed with confidence) — callers
    must fall back to :func:`extract_three_stories`.

    The auto-publisher emits excerpts of the form::

        "<anchor1>, <anchor2>, <anchor3>을 중심으로 ... 정리합니다.
         <tag1>, <tag2> 등 최신 위협 동향과 ..."

    so we trim everything after the first "을/를 중심으로" (or fallback
    phrases) and split the remaining prefix on standard enumerators.
    """
    text = (excerpt or "").strip()
    if not text:
        return None

    prefix = _EXCERPT_BOILERPLATE_RE.split(text, maxsplit=1)[0].strip()
    if not prefix or prefix == text:
        # No boilerplate marker found — refuse to guess.
        return None

    raw = [p.strip() for p in _EXCERPT_SPLIT_RE.split(prefix) if p.strip()]
    if len(raw) < 3:
        return None

    # Take the first 3 segments. Each segment is a Korean phrase that we
    # keep in Korean (the L22 SVG renderer's <text> elements DO accept
    # Hangul — only L20's check-svg gate rejects it).
    segments = raw[:3]

    # Sanity gate: at least one segment must contain Hangul, otherwise
    # we're probably re-parsing an English title and the original
    # extract_three_stories path is the correct one.
    if not any(_has_hangul(s) for s in segments):
        return None

    stories: List[Dict] = []
    for seg in segments:
        # 15-25 Korean chars per the spec. Use 28 as a soft cap so a
        # tight 3-word phrase like "AI 속도의 방어" stays intact.
        head = _shorten(seg, 28)
        stories.append({
            "headline": head,
            # Subheadline reuses the trimmed segment so the second metric
            # row carries the full context rather than the boilerplate.
            "subheadline": _shorten(seg, 60),
        })

    return stories[0], stories[1], stories[2]


# ---------------------------------------------------------------------------
# KPI inference with excerpt fallback (Fix 3)
# ---------------------------------------------------------------------------

# Korean count suffix (e.g. "29건", "16건") — the auto-publisher injects
# the news article count into every excerpt: "주요 보안/기술 뉴스 29건과
# 대응 우선순위를 정리합니다."
_KO_COUNT_RE = re.compile(r"(\d{1,4})\s*건")


def _infer_kpi_with_excerpt(
    headline: str,
    excerpt: str = "",
) -> Tuple[str, str, str]:
    """:func:`_infer_kpi` with an excerpt-scan fallback.

    Heuristics tried in order:

    1. :func:`scripts.news.l20_dispatch._infer_kpi` on the headline.
    2. If (1) returned the ``("TBD", "STATUS", "NEW")`` default, retry the
       same matcher on the excerpt.
    3. Korean-locale "<count>건" pattern in the excerpt — auto-published
       digest excerpts always include "뉴스 29건과 대응 우선순위를
       정리합니다" so the count anchors the KPI when nothing else does.
    4. Final fall-through: return the original default so the L22 renderer
       still has a 3-string KPI triple to draw.
    """
    value, label, sub = _infer_kpi(headline)
    if value != "TBD":
        return value, label, sub

    if excerpt:
        ev, el, es = _infer_kpi(excerpt)
        if ev != "TBD":
            return ev, el, es

        m = _KO_COUNT_RE.search(excerpt)
        if m:
            return (m.group(1)[:6], "COUNT", "items")

    return value, label, sub


# ---------------------------------------------------------------------------
# Visual-variety enforcement (Fix 1)
# ---------------------------------------------------------------------------

# Deterministic rotation pool for the "force 3 distinct primitives" pass.
# Chosen for maximum visual contrast: lock_cve (padlock + CVSS chip) ≠
# network_nodes (graph) ≠ code_bars (bar chart with caption).
_VARIETY_ROTATIONS: List[List[str]] = [
    ["lock_cve", "network_nodes", "code_bars"],
    ["network_nodes", "code_bars", "shield"],
    ["lock_cve", "code_bars", "router_mesh"],
    ["browser_cve", "network_nodes", "code_bars"],
    ["shield", "router_mesh", "code_bars"],
    ["lock_cve", "cloud_k8s", "network_nodes"],
    ["code_bars", "wallet_forensic", "lock_cve"],
    ["cloud_k8s", "code_bars", "shield"],
]


def _force_variety(visual_kinds: List[str], seed_hex: str) -> List[str]:
    """Override duplicates so all 3 bands carry distinct primitives.

    When ``visual_kinds`` already has 3 distinct entries, return it
    unchanged. Otherwise pick a deterministic rotation from
    :data:`_VARIETY_ROTATIONS` keyed by the post-date hex so the same
    post always renders the same triple, but neighbouring dates rotate
    through different combinations.
    """
    if len(set(visual_kinds)) == 3:
        return visual_kinds

    # Deterministic seed: sum of hex digits in ``seed_hex`` (e.g. the
    # YYYYMMDD digits with no separators). Anything non-hex contributes 0.
    s = 0
    for ch in (seed_hex or "L22"):
        try:
            s += int(ch, 16)
        except ValueError:
            pass
    return list(_VARIETY_ROTATIONS[s % len(_VARIETY_ROTATIONS)])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _build_band_cfg(
    headline: str,
    subheadline: str,
    band_idx: int,
    excerpt: str = "",
    visual_kind_override: Optional[str] = None,
) -> dict:
    """Translate (headline, subheadline) into a render_bands_svg band dict.

    All values are derived heuristically:

    * ``theme``       — by band index (red / amber / green)
    * ``visual``      — keyword-matched primitive call with sensible kwargs
                        (override-able for the post-routing variety pass)
    * ``label``       — keyword-matched short caps tag
    * ``badge_*``     — :func:`_infer_kpi_with_excerpt` (headline first,
                        excerpt fallback for KPI mining)
    * ``mini*_*``     — band-specific severity / priority labels
    * ``metric/detail`` and ``metric_b/detail_b`` — the headline + sub
    """
    # Lazy-import the renderer to avoid a hard dep when only metadata
    # helpers are exercised (e.g. unit tests that patch the renderer).
    from scripts.lib import svg_l22_generator as l22

    theme_name = _route_theme(band_idx)
    theme = l22.THEMES[theme_name]
    label = _route_label(headline)
    visual_kind = visual_kind_override or _route_visual_kind(headline, band_idx)

    badge_value, badge_label, badge_sub = _infer_kpi_with_excerpt(headline, excerpt)

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

    # Fix 4: band-specific priority/severity badge labels so the 3 stripes
    # do not all carry the literal "MAY / WK / Q2" placeholders. The mini
    # badges now read (P0 / HIGH / red) → (P1 / MED / amber) → (P2 / LOW /
    # green), matching the severity descent down the band stack.
    severity_rank = ["P0", "P1", "P2"][band_idx]
    severity_tier = ["HIGH", "MED", "LOW"][band_idx]

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
        mini_value=severity_rank,
        mini_label="PRI",
        mini_sub=theme_name,
        mini2_value=severity_tier,
        mini2_label="TIER",
        mini2_sub=theme_name,
        visual=visual_fn(),
    )


def _resolve_three_stories(
    title: str,
    excerpt: str,
    filename: str,
) -> Tuple[Dict, Dict, Dict]:
    """Pick the richest 3-story tuple available for the band builder.

    Order:

    1. :func:`extract_three_stories_from_excerpt` — works for Korean-only
       auto-published digests where the title is one merged phrase but
       the excerpt has 3 enumerated anchor stories.
    2. :func:`extract_three_stories` — original English-keyword fallback
       used for titles that already split on commas.
    """
    excerpt_stories = extract_three_stories_from_excerpt(title, excerpt, filename)
    if excerpt_stories is not None:
        return excerpt_stories
    return extract_three_stories(title, excerpt, filename=filename)


def _build_bands_with_variety(
    h: Dict,
    tr: Dict,
    br: Dict,
    excerpt: str,
    seed_hex: str,
) -> List[dict]:
    """Build the 3-band config and apply the variety-enforcement pass.

    Each band's initial ``visual_kind`` comes from the keyword router.
    If 2+ bands collide on the same primitive (common for
    single-keyword Korean filenames like "AI / Vulnerability /
    Security" that all route to ``lock_cve``), the variety pass
    rewrites the duplicates to a deterministic 3-distinct rotation
    seeded by ``seed_hex``.
    """
    initial_kinds = [
        _route_visual_kind(h["headline"], 0),
        _route_visual_kind(tr["headline"], 1),
        _route_visual_kind(br["headline"], 2),
    ]
    final_kinds = _force_variety(initial_kinds, seed_hex)

    return [
        _build_band_cfg(
            h["headline"], h["subheadline"], 0,
            excerpt=excerpt, visual_kind_override=final_kinds[0],
        ),
        _build_band_cfg(
            tr["headline"], tr["subheadline"], 1,
            excerpt=excerpt, visual_kind_override=final_kinds[1],
        ),
        _build_band_cfg(
            br["headline"], br["subheadline"], 2,
            excerpt=excerpt, visual_kind_override=final_kinds[2],
        ),
    ]


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
        h, tr, br = _resolve_three_stories(title, excerpt, filename)
        date_str = _date_str_from_filename(filename) or ""
        sfx = (date_str.replace(".", "")[-4:] if date_str else "L22")[:4] or "L22"
        seed = date_str.replace(".", "") or filename or "L22"
        initial_kinds = [
            _route_visual_kind(h["headline"], 0),
            _route_visual_kind(tr["headline"], 1),
            _route_visual_kind(br["headline"], 2),
        ]
        final_kinds = _force_variety(initial_kinds, seed)
        bands_cfg = _build_bands_with_variety(h, tr, br, excerpt, seed_hex=seed)
        url = _post_url_from_filename(filename)

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
        svg = _inject_band_visual_markers(svg, final_kinds)
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

        h, tr, br = _resolve_three_stories(title, excerpt, filename)
        date_str = _date_str_from_filename(filename) or ""
        sfx = (date_str.replace(".", "")[-4:] if date_str else "L22")[:4] or "L22"
        seed = date_str.replace(".", "") or filename or "L22"
        initial_kinds = [
            _route_visual_kind(h["headline"], 0),
            _route_visual_kind(tr["headline"], 1),
            _route_visual_kind(br["headline"], 2),
        ]
        final_kinds = _force_variety(initial_kinds, seed)
        bands_cfg = _build_bands_with_variety(h, tr, br, excerpt, seed_hex=seed)
        url = _post_url_from_filename(filename)

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
        return _inject_band_visual_markers(svg, final_kinds)
    except Exception as exc:
        logging.warning(f"L22 SVG render failed, falling back: {exc}")
        return ""
