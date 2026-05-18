"""L25-single SVG generator (1200x630 single-topic post cover).

Sibling of L22 (3-band digest), L20 (hero + 2 cards), rollup (week/month
index). The 28 hand-crafted 2025-* covers carrying the marker
``profile: high-quality-cover (2025 upgraded L25-single)`` are
**grandfathered** — no spec→render mapping. This module is forward-
looking infra for FUTURE single-topic post covers.

Layout (1200x630): header strip (y=0..56) | hero panel (32,80,1136x420)
with title-left + visual-centered-at-(840,290) | tag-chip row (y=520) |
KPI strip (y=562..614) | QR (bottom-right via ``l22.qr_block``).

Public API: ``CATEGORIES``, ``THEMES`` (proxied from L20),
``VISUAL_BUILDERS``, ``render_l25_single(spec)``. Marker comment is
emitted on **line 3** verbatim.

English-only guarantee: ``_escape`` delegates to L20 (strips Hangul
before XML escaping — defense in depth for the check-svg gate).
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping

from scripts.lib import svg_l20_hero as l20
from scripts.lib import svg_l22_generator as l22

# Re-export L20 themes so callers can ``from svg_l25_single import THEMES``.
THEMES = l20.THEMES
CATEGORIES = frozenset({"incident", "course", "tutorial", "guide", "event"})

# Visual dispatch — reuse L20 primitives (theme-aware single-focal builders).
# Aliases: network_nodes/hub_spoke → vb_hub_spoke; code_bars → vb_code_injection;
# shield → vb_ransomware_lock; supply_chain_pipe → vb_supply_chain_pipe;
# lock_cve → vb_cve_chain.
VISUAL_BUILDERS: Dict[str, Any] = {
    "network_nodes":     l20.vb_hub_spoke,
    "code_bars":         l20.vb_code_injection,
    "shield":            l20.vb_ransomware_lock,
    "hub_spoke":         l20.vb_hub_spoke,
    "supply_chain_pipe": l20.vb_supply_chain_pipe,
    "lock_cve":          l20.vb_cve_chain,
}

# Header badge tint per topic type.
_CATEGORY_COLORS: Dict[str, str] = {
    "incident": "#F87171", "course": "#A78BFA", "tutorial": "#4ADE80",
    "guide":    "#60A5FA", "event":  "#FFD58A",
}


# Small wrappers around L20 primitives -------------------------------------

def _escape(text: str) -> str:
    """Delegate to L20's hangul-stripping XML escape (single source of truth)."""
    return l20._escape(text)


def _theme(name: str) -> Dict[str, str]:
    return THEMES.get(name, THEMES["red"])


def _render_visual(visual_id: str, cx: int, cy: int, theme: str, label: str = "") -> str:
    """Dispatch to a visual builder; ``hub_spoke``/``network_nodes`` accept
    a ``center_label`` kwarg (others ignore ``label``)."""
    fn = VISUAL_BUILDERS.get(visual_id, l20.vb_cve_chain)
    if visual_id in ("hub_spoke", "network_nodes") and label:
        return fn(cx, cy, theme=theme, center_label=label)
    return fn(cx, cy, theme=theme)


def _post_url(date: str, slug: str) -> str:
    """Canonical Jekyll permalink (underscore-preserved, matches L20)."""
    yyyy, mm, dd = date.split("-")
    return f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug}/"


def _hero_panel_grad(theme: str) -> str:
    """L20-defined gradient id (reuses ``_defs`` palette)."""
    return {
        "red":    "heroPanel",
        "blue":   "heroPanelBlue",
        "amber":  "heroPanelAmber",
        "green":  "heroPanelGreen",
        "purple": "heroPanelPurple",
    }.get(theme, "heroPanel")


# Layout blocks ------------------------------------------------------------

def _tag_chip_row(y: int, tags: List[str], accent: str) -> str:
    """Layout 0-5 tag chips left-aligned starting at x=54 with 12px gaps.
    Chip width = max(70, 7.2 * len(label) + 24) — clamped to 28-char labels
    so the strip stays within the 1136px hero panel."""
    if not tags:
        return ""
    parts: List[str] = []
    x = 54
    for tag in tags[:5]:
        label = _escape(tag)[:28]
        width = max(70, int(7.2 * len(label)) + 24)
        parts.append(
            f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="0" width="{width}" height="26" rx="13" '
            f'fill="#0A0C16" stroke="{accent}" stroke-width="1.2" opacity="0.9"/>'
            f'<text x="{width // 2}" y="17" text-anchor="middle" '
            f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" '
            f'font-weight="700" fill="{accent}" letter-spacing="1.5">{label}</text>'
            f'</g>'
        )
        x += width + 12
    return "".join(parts)


def _kpi_strip(y: int, kpis: List[Mapping[str, Any]], theme: str) -> str:
    """3-cell KPI strip below the hero: 320x52 cells, 23px gaps, value left
    (22pt bold) + label right (10pt uppercase)."""
    if not kpis:
        return ""
    t = _theme(theme)
    accent = t["accent"]
    label_col = t["label_color"]
    cell_w = 320
    gap = 23
    parts: List[str] = []
    x = 54
    for cell in kpis[:3]:
        value = _escape(str(cell.get("value", "")))[:10]
        label = _escape(str(cell.get("label", "")))[:18]
        parts.append(
            f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="0" width="{cell_w}" height="52" rx="6" '
            f'fill="#0A0C16" stroke="{accent}" stroke-width="1.2" opacity="0.85"/>'
            f'<text x="14" y="34" font-family="Inter, Helvetica, Arial, sans-serif" '
            f'font-size="22" font-weight="800" fill="#F5F7FA">{value}</text>'
            f'<text x="{cell_w - 14}" y="22" text-anchor="end" '
            f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="10" '
            f'font-weight="700" fill="{label_col}" letter-spacing="2">{label}</text>'
            f'</g>'
        )
        x += cell_w + gap
    return "".join(parts)


# Top-level renderer -------------------------------------------------------

def render_l25_single(spec: Mapping[str, Any]) -> str:
    """Render a full L25-single 1200x630 SVG from a spec dict.

    Required keys: date, slug, post_title, category (CATEGORIES), theme
    (THEMES), headline, subheadline, visual (VISUAL_BUILDERS).
    Optional: tag_chips (list[str], <=5), kpi_strip (list[{label,value}],
    <=3), url (defaults to canonical Jekyll permalink).

    Output is deterministic — no randomness, no clock reads.

    Raises:
        KeyError: required key missing.
        ValueError: theme/category/visual outside its allowed set.
    """
    date = str(spec["date"])
    slug = str(spec["slug"])
    post_title = str(spec["post_title"])
    category = str(spec["category"])
    theme = str(spec["theme"])
    headline = str(spec["headline"])
    subheadline = str(spec["subheadline"])
    visual = str(spec["visual"])
    tag_chips: List[str] = list(spec.get("tag_chips") or [])
    kpi_strip: List[Mapping[str, Any]] = list(spec.get("kpi_strip") or [])
    url = str(spec.get("url") or _post_url(date, slug))

    # Validate enums up front — fail loud so YAML typos never reach disk.
    if category not in CATEGORIES:
        raise ValueError(
            f"unknown category {category!r}; valid: {sorted(CATEGORIES)}"
        )
    if theme not in THEMES:
        raise ValueError(f"unknown theme {theme!r}; valid: {sorted(THEMES)}")
    if visual not in VISUAL_BUILDERS:
        raise ValueError(
            f"unknown visual {visual!r}; valid: {sorted(VISUAL_BUILDERS)}"
        )

    t = _theme(theme)
    accent = t["accent"]
    accent_soft = t["accent_soft"]
    accent_text = t["accent_text"]
    panel_grad = _hero_panel_grad(theme)
    cat_color = _CATEGORY_COLORS.get(category, accent_soft)
    date_str = date.replace("-", ".")

    aria = _escape(f"{category} cover {date_str}: {headline}")
    title = _escape(post_title)

    cat_u = _escape(category.upper())
    theme_u = _escape(theme.upper())

    # Marker MUST sit on line 3 — check-svg gate keys on this exact string.
    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" '
        f'width="1200" height="630" role="img" aria-label="{aria}">',
        f'<title>{title}</title>',
        '<!-- profile: high-quality-cover (2025 upgraded L25-single) -->',
        l20._defs(),
        # Background
        '<rect width="1200" height="630" fill="url(#bgSpread)"/>',
        '<rect width="1200" height="630" fill="url(#envGrid)"/>',
        l20._ambient_layer(),
        # Header bar
        '<rect x="0" y="0" width="1200" height="56" fill="#050813" opacity="0.92"/>',
        f'<text x="36" y="36" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="18" font-weight="700" fill="{cat_color}" letter-spacing="2.5">'
        f'{cat_u}</text>',
        f'<text x="1164" y="36" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="15" font-weight="600" fill="#7DA3D9" letter-spacing="1.5" '
        f'text-anchor="end">{_escape(date_str)}</text>',
        f'<rect x="0" y="54" width="1200" height="2" fill="{accent}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="4.8s" '
        f'repeatCount="indefinite"/></rect>',
        # Hero panel + halo + accent stripe
        f'<rect x="32" y="80" width="1136" height="420" rx="14" ry="14" '
        f'fill="url(#{panel_grad})" stroke="{accent}" stroke-width="1.8" opacity="0.98"/>',
        f'<circle cx="840" cy="290" r="240" fill="url(#{t["halo_id"]})" opacity="0.28"/>',
        f'<rect x="32" y="80" width="1136" height="4" fill="{accent}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.5;1;0.5" dur="3.4s" '
        f'repeatCount="indefinite"/></rect>',
        # Title hierarchy (left half)
        '<g filter="url(#textShadow)">',
        f'<text x="54" y="120" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="13" font-weight="700" fill="{accent_soft}" letter-spacing="3">'
        f'{cat_u}  /  {theme_u}</text>',
        f'<text x="54" y="172" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="34" font-weight="800" fill="#F8FAFC">{_escape(headline)}</text>',
        f'<text x="54" y="208" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="18" font-weight="500" fill="{accent_text}">'
        f'{_escape(subheadline)}</text>',
        '</g>',
        # Single hero visualization (right half, centered at 840,290)
        _render_visual(visual, 840, 290, theme, category.upper()),
        # Tag-chip row + KPI strip + QR (deterministic, no clock reads)
        _tag_chip_row(520, tag_chips, accent),
        _kpi_strip(562, kpi_strip, theme),
        l22.qr_block(url),
        '</svg>',
    ]
    return "\n".join(parts) + "\n"
