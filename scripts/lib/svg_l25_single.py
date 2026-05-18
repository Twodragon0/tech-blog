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

# Visual dispatch — reuse L20 primitives (theme-aware single-focal builders),
# augmented with two L25-native primitives (``outage_timeline``,
# ``k8s_topology``) registered further down once their bodies are defined.
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

# Per-chip "tone" palette — lets tag chips carry independent theme inflection
# (mirrors the multi-themed badges in the L22 ultra 3-band reference). Tone
# keys map to (stroke/text color, panel fill bias). Unknown tone => fallback
# to the cover-level accent.
_CHIP_TONES: Dict[str, str] = {
    "red":    "#F87171",
    "blue":   "#60A5FA",
    "amber":  "#FFD58A",
    "green":  "#86EFAC",
    "purple": "#C4B5FD",
    "cyan":   "#67E8F9",
    "pink":   "#F9A8D4",
    "neutral": "#94A3B8",
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

def _chip_tone(tag: Any, fallback: str) -> str:
    """Resolve a chip's outline/text color.

    Two YAML-friendly shapes are accepted, alongside legacy plain strings:
      - ``"AWS"``                              -> use cover accent
      - ``{label: AWS, tone: amber}``          -> use amber preset
      - ``{label: AWS, tone: "#FFAA00"}``      -> raw hex passthrough
    Unknown tone keys fall back to the cover accent so a typo can't break a
    render.
    """
    if isinstance(tag, dict):
        tone = str(tag.get("tone", "")).strip()
        if tone.startswith("#") and len(tone) in (4, 7):
            return tone
        return _CHIP_TONES.get(tone, fallback)
    return fallback


def _chip_label(tag: Any) -> str:
    return tag["label"] if isinstance(tag, dict) else tag


def _tag_chip_row(y: int, tags: List[Any], accent: str) -> str:
    """Layout 0-5 tag chips left-aligned starting at x=54 with 12px gaps.
    Chip width = max(70, 7.2 * len(label) + 24) — clamped to 28-char labels
    so the strip stays within the 1136px hero panel.

    Each chip may carry an optional ``tone`` key for per-chip color inflection
    (mirrors the multi-themed bands in L22 ultra digests). When ``tone`` is
    omitted the cover's ``accent`` is used so the legacy plain-string form
    keeps rendering identically.
    """
    if not tags:
        return ""
    parts: List[str] = []
    x = 54
    for tag in tags[:5]:
        label = _escape(str(_chip_label(tag)))[:28]
        color = _chip_tone(tag, accent)
        width = max(70, int(7.2 * len(label)) + 24)
        parts.append(
            f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="0" width="{width}" height="26" rx="13" '
            f'fill="#0A0C16" stroke="{color}" stroke-width="1.2" opacity="0.9"/>'
            f'<text x="{width // 2}" y="17" text-anchor="middle" '
            f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" '
            f'font-weight="700" fill="{color}" letter-spacing="1.5">{label}</text>'
            f'</g>'
        )
        x += width + 12
    return "".join(parts)


def _accent_pulse_strip(x: int, y: int, accent: str, accent_soft: str) -> str:
    """3 thin pulsing accent rects directly under the header — mirrors L22
    ultra's animated section dividers. Adds visual density at zero text
    cost. Each rect uses an offset animation phase so they shimmer
    independently (1.8s / 2.4s / 3.1s)."""
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect x="0"   y="0" width="120" height="3" rx="1.5" fill="{accent}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="1.8s" repeatCount="indefinite"/></rect>'
        f'<rect x="132" y="0" width="68"  height="3" rx="1.5" fill="{accent_soft}" opacity="0.7">'
        f'<animate attributeName="opacity" values="0.3;0.9;0.3" dur="2.4s" repeatCount="indefinite"/></rect>'
        f'<rect x="212" y="0" width="40"  height="3" rx="1.5" fill="{accent}" opacity="0.55">'
        f'<animate attributeName="opacity" values="0.2;0.8;0.2" dur="3.1s" repeatCount="indefinite"/></rect>'
        f'</g>'
    )


def _detail_line(y: int, bullets: List[str], accent_text: str, accent: str) -> str:
    """Up to 2 bullet phrases joined with a dot separator, styled like
    L22 ultra's "UAC-0255 - password-protected ZIP - remote access trojan"
    detail row. Renders nothing when the list is empty."""
    cleaned = [_escape(str(b)).strip() for b in bullets if str(b).strip()][:2]
    if not cleaned:
        return ""
    joined = " &#8226; ".join(cleaned)
    return (
        f'<text x="54" y="{y}" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="13" font-weight="500" fill="{accent_text}" fill-opacity="0.85" '
        f'letter-spacing="0.4">'
        f'<tspan fill="{accent}" font-weight="700">&#9656; </tspan>{joined}'
        f'</text>'
    )


def _visual_frame(cx: int, cy: int, w: int, h: int, theme: str, label: str) -> str:
    """Translucent inner frame around the right-half visual zone with
    animated corner ticks and a small caption tag — mirrors L22 ultra's
    visual-zone decoration so a single hero illustration doesn't feel
    empty next to the dense badge stack."""
    t = _theme(theme)
    accent = t["accent"]
    soft = t["accent_soft"]
    lab = _escape(label)[:22]
    # Caption tag width scales with label length so 22-char labels still fit.
    cap_w = max(92, int(7.4 * len(lab)) + 16)
    cap_hw = cap_w // 2
    hw, hh = w // 2, h // 2
    return (
        f'<g transform="translate({cx},{cy})" opacity="0.85">'
        # Rounded outline.
        f'<rect x="-{hw}" y="-{hh}" width="{w}" height="{h}" rx="12" '
        f'fill="none" stroke="{accent}" stroke-width="0.9" '
        f'stroke-opacity="0.55" stroke-dasharray="6 4"/>'
        # Inner dot grid hint (3 dots top + 3 dots bottom).
        f'<g fill="{soft}" opacity="0.45">'
        f'<circle cx="-{hw - 18}" cy="-{hh - 14}" r="1.4"/>'
        f'<circle cx="0"          cy="-{hh - 14}" r="1.4"/>'
        f'<circle cx="{hw - 18}"  cy="-{hh - 14}" r="1.4"/>'
        f'<circle cx="-{hw - 18}" cy="{hh - 14}"  r="1.4"/>'
        f'<circle cx="0"          cy="{hh - 14}"  r="1.4"/>'
        f'<circle cx="{hw - 18}"  cy="{hh - 14}"  r="1.4"/>'
        f'</g>'
        # Top-left + top-right corner brackets.
        f'<polyline points="-{hw + 4},-{hh - 16} -{hw + 4},-{hh + 4} '
        f'-{hw - 16},-{hh + 4}" fill="none" stroke="{accent}" '
        f'stroke-width="1.6" stroke-opacity="0.8"/>'
        f'<polyline points="{hw + 4},-{hh - 16} {hw + 4},-{hh + 4} '
        f'{hw - 16},-{hh + 4}" fill="none" stroke="{accent}" '
        f'stroke-width="1.6" stroke-opacity="0.8"/>'
        # Bottom-left + bottom-right corner brackets.
        f'<polyline points="-{hw + 4},{hh - 16} -{hw + 4},{hh + 4} '
        f'-{hw - 16},{hh + 4}" fill="none" stroke="{accent}" '
        f'stroke-width="1.6" stroke-opacity="0.8"/>'
        f'<polyline points="{hw + 4},{hh - 16} {hw + 4},{hh + 4} '
        f'{hw - 16},{hh + 4}" fill="none" stroke="{accent}" '
        f'stroke-width="1.6" stroke-opacity="0.8"/>'
        # Frame caption tag (top-center) — width scales with label length.
        f'<g transform="translate(0,-{hh - 2})">'
        f'<rect x="-{cap_hw}" y="-12" width="{cap_w}" height="20" rx="6" '
        f'fill="#0A0C16" stroke="{accent}" stroke-width="1" opacity="0.92"/>'
        f'<text x="0" y="2" text-anchor="middle" '
        f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="10" '
        f'font-weight="700" fill="{soft}" letter-spacing="2">{lab}</text>'
        f'</g>'
        # Pulse marker at top-right of frame.
        f'<circle cx="{hw - 4}" cy="-{hh + 2}" r="2" fill="{accent}">'
        f'<animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/></circle>'
        f'</g>'
    )


def _accent_badge(cx: int, cy: int, theme: str, value: str, label: str, sub: str) -> str:
    """Standalone hero-card-style KPI badge (160x120) centered at (cx,cy).
    Mirrors L22 ultra's right-side "1M+ EMAILS SENT" card: big value, small
    uppercase label above, sub-label below, animated corner ticks.

    The badge is anchored at the top-right of the hero panel (x=1075) and
    the host renderer shifts the right-half visual leftward when this
    optional element is present so the two never overlap.

    Renders nothing when ``value`` is empty so the field stays optional."""
    if not value:
        return ""
    t = _theme(theme)
    accent = t["accent"]
    soft = t["accent_soft"]
    label_col = t["label_color"]
    val = _escape(value)[:6]
    lab = _escape(label)[:14]
    s = _escape(sub)[:22]
    val_fs = 52 if len(val) <= 3 else (40 if len(val) <= 4 else 30)
    return (
        f'<g transform="translate({cx},{cy})" filter="url(#softShadow)">'
        f'<rect x="-80" y="-60" width="160" height="120" rx="14" '
        f'fill="#0A0C16" stroke="{accent}" stroke-width="2.2" opacity="0.96"/>'
        f'<text x="0" y="-32" text-anchor="middle" '
        f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" '
        f'font-weight="700" letter-spacing="2.4" fill="{label_col}">{lab}</text>'
        f'<text x="0" y="22" text-anchor="middle" '
        f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="{val_fs}" '
        f'font-weight="900" fill="#F5F7FA">{val}</text>'
        f'<text x="0" y="44" text-anchor="middle" '
        f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="9" '
        f'font-weight="600" fill="{soft}" letter-spacing="1.2">{s}</text>'
        f'<line x1="-60" y1="50" x2="60" y2="50" stroke="{accent}" stroke-width="0.8" '
        f'stroke-opacity="0.5"/>'
        # Animated corner ticks (top-left, top-right, plus pulse dot).
        f'<rect x="-76" y="-56" width="14" height="2" rx="1" fill="{accent}" opacity="0.7">'
        f'<animate attributeName="opacity" values="0.3;1;0.3" dur="1.6s" repeatCount="indefinite"/></rect>'
        f'<rect x="62" y="-56" width="14" height="2" rx="1" fill="{accent}" opacity="0.7">'
        f'<animate attributeName="opacity" values="0.3;1;0.3" dur="1.7s" begin="0.5s" repeatCount="indefinite"/></rect>'
        f'<circle cx="0" cy="-48" r="2.4" fill="{accent}">'
        f'<animate attributeName="opacity" values="0.25;1;0.25" dur="2s" repeatCount="indefinite"/></circle>'
        f'</g>'
    )


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


# L25-native visual primitives --------------------------------------------

def _visual_outage_timeline(cx: int, cy: int, theme: str = "red") -> str:
    """Incident-postmortem visual: 5-phase horizontal timeline plus a
    blast-radius indicator below.

    Design intent: replaces the generic ``shield``/ransomware-lock visual
    on outage RCA posts where there is no encryption / ransom note — just
    an SRE-style incident lifecycle. The "Mitigate" marker is highlighted
    in the theme accent (others muted to ``accent_soft``) so the eye lands
    on the active response phase. Concentric arcs underneath label the
    blast radius from GLOBAL inward to ASIA — read as "the outage rippled
    out from the edge". Deterministic (no time-dependent values)."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    phases = [
        (-150, "DETECT"),
        (-78, "DIAGNOSE"),
        (0, "MITIGATE"),     # current/highlighted
        (78, "RESOLVE"),
        (150, "POSTMORTEM"),
    ]
    nodes = []
    for x, label in phases:
        is_cur = (label == "MITIGATE")
        r = 9 if is_cur else 6
        fill = a if is_cur else "#0A0C16"
        stroke = a if is_cur else soft
        nodes.append(
            f'<circle cx="{x}" cy="-30" r="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{2 if is_cur else 1.4}">'
            + (
                f'<animate attributeName="r" values="8;11;8" dur="2s" '
                f'repeatCount="indefinite"/>' if is_cur else ""
            )
            + '</circle>'
        )
        nodes.append(
            f'<text x="{x}" y="-50" text-anchor="middle" '
            f'font-family="Inter, monospace" font-size="8" font-weight="800" '
            f'fill="{a if is_cur else soft}" letter-spacing="1.2">{label}</text>'
        )
    # Concentric blast-radius arcs (top-down semicircles centered at (0,90)).
    arcs = []
    for radius, opacity, region in [
        (96, 0.30, "GLOBAL"),
        (74, 0.45, "US-EAST"),
        (52, 0.65, "EU"),
        (30, 0.90, "ASIA"),
    ]:
        arcs.append(
            f'<path d="M{-radius} 90 A{radius} {radius} 0 0 1 {radius} 90" '
            f'fill="none" stroke="{a}" stroke-width="1.2" '
            f'stroke-opacity="{opacity}"/>'
        )
        arcs.append(
            f'<text x="0" y="{90 - radius + 12}" text-anchor="middle" '
            f'font-family="Inter, monospace" font-size="7" font-weight="700" '
            f'fill="{soft}" opacity="{opacity + 0.2:.2f}" letter-spacing="1">'
            f'{region}</text>'
        )
    return (
        f'<g transform="translate({cx},{cy})">'
        # (No internal header — the visual_frame caption "OUTAGE TIMELINE"
        # already labels this zone; an inner label would duplicate it.)
        # Horizontal axis.
        f'<line x1="-168" y1="-30" x2="168" y2="-30" stroke="{soft}" '
        f'stroke-width="1.2" stroke-opacity="0.55" stroke-dasharray="4 3"/>'
        # Phase markers + labels.
        + "".join(nodes) +
        # Sweep pulse along the axis (motion dot, no scripts).
        f'<circle r="2.4" fill="{a}">'
        f'<animateMotion path="M-150 -30 L150 -30" dur="3.6s" '
        f'repeatCount="indefinite"/></circle>'
        # Blast-radius header.
        f'<text x="0" y="22" text-anchor="middle" '
        f'font-family="Inter, monospace" font-size="9" font-weight="800" '
        f'fill="{soft}" letter-spacing="2">BLAST RADIUS</text>'
        # Concentric arcs + region labels + epicenter dot.
        + "".join(arcs) +
        f'<circle cx="0" cy="90" r="3" fill="{a}">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="1.8s" '
        f'repeatCount="indefinite"/></circle>'
        f'</g>'
    )


def _visual_k8s_topology(cx: int, cy: int, theme: str = "blue") -> str:
    """Kubernetes-cluster topology: central control-plane hex with 6
    satellite objects (POD, SVC, NS, CRD, CM, NODE).

    Design intent: replaces the generic CROSS/VECTOR/PROXY hub-spoke when
    the post is a hands-on K8s tutorial — the labels are now genuine K8s
    object kinds an operator would recognize. The center is drawn as a
    hex (api-server crown) rather than a plain circle to mark it as the
    control plane. Connections are subtle curved guides with a slow
    stroke-dash sweep to suggest reconciliation traffic without the
    busy attack-style motion the L20 hub-spoke uses. Deterministic."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    # Hex points (radius 26 around 0,0) — api-server "crown".
    hex_pts = "0,-26 22,-13 22,13 0,26 -22,13 -22,-13"
    # 6 satellite positions on a 100-unit radius circle, with labels.
    sats = [
        (   0,  -92, "POD",  "#86EFAC"),  # green
        (  92,  -34, "SVC",  "#67E8F9"),  # cyan
        (  82,   54, "NS",   "#C4B5FD"),  # purple
        (   0,   92, "CM",   "#FFD58A"),  # amber
        ( -82,   54, "CRD",  "#F9A8D4"),  # pink
        ( -92,  -34, "NODE", soft),       # theme-soft (blue)
    ]
    nodes_svg = []
    lines_svg = []
    for x, y, label, col in sats:
        # Curved control-line from center (0,0) to satellite (x,y) via a
        # subtle quadratic midpoint that bows outward away from origin.
        mx = x * 0.55 + (-y * 0.18)
        my = y * 0.55 + (x * 0.18)
        lines_svg.append(
            f'<path d="M0 0 Q{mx:.1f} {my:.1f} {x} {y}" stroke="{a}" '
            f'stroke-width="1" stroke-opacity="0.5" fill="none" '
            f'stroke-dasharray="3 3">'
            f'<animate attributeName="stroke-dashoffset" values="0;-12" '
            f'dur="2.6s" repeatCount="indefinite"/></path>'
        )
        nodes_svg.append(
            f'<g transform="translate({x},{y})">'
            f'<rect x="-24" y="-13" width="48" height="26" rx="5" '
            f'fill="#0A1A30" stroke="{col}" stroke-width="1.4"/>'
            f'<text x="0" y="4" text-anchor="middle" '
            f'font-family="Inter, monospace" font-size="10" font-weight="900" '
            f'fill="{col}" letter-spacing="1">{label}</text>'
            f'</g>'
        )
    return (
        f'<g transform="translate({cx},{cy})">'
        # (No internal header — the visual_frame caption "K8S TOPOLOGY"
        # already labels this zone; an inner label would duplicate it.)
        # Curved control-plane connections (drawn first, under the boxes).
        + "".join(lines_svg) +
        # Central control-plane hex + label.
        f'<polygon points="{hex_pts}" fill="#0A1A30" stroke="{a}" '
        f'stroke-width="2" filter="url(#softShadow)">'
        f'<animate attributeName="stroke-opacity" values="0.7;1;0.7" '
        f'dur="3s" repeatCount="indefinite"/></polygon>'
        f'<text x="0" y="-3" text-anchor="middle" '
        f'font-family="Inter, monospace" font-size="9" font-weight="900" '
        f'fill="{soft}">api-server</text>'
        f'<text x="0" y="9" text-anchor="middle" '
        f'font-family="Inter, monospace" font-size="7" font-weight="700" '
        f'fill="{a}" letter-spacing="1.2">CONTROL PLANE</text>'
        # Satellite nodes.
        + "".join(nodes_svg) +
        # Bottom-corner mode badge ("single-node" — accurate for minikube).
        f'<g transform="translate(-120,124)">'
        f'<rect x="0" y="0" width="86" height="18" rx="3" fill="#0A0C16" '
        f'stroke="{a}" stroke-width="1"/>'
        f'<text x="43" y="13" text-anchor="middle" '
        f'font-family="Inter, monospace" font-size="8" font-weight="800" '
        f'fill="{soft}" letter-spacing="1.4">single-node</text>'
        f'</g>'
        f'</g>'
    )


# Register the L25-native primitives after their bodies are defined.
VISUAL_BUILDERS["outage_timeline"] = _visual_outage_timeline
VISUAL_BUILDERS["k8s_topology"]    = _visual_k8s_topology


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
    tag_chips: List[Any] = list(spec.get("tag_chips") or [])
    kpi_strip: List[Mapping[str, Any]] = list(spec.get("kpi_strip") or [])
    detail_line: List[str] = list(spec.get("detail_line") or [])
    accent_badge: Mapping[str, Any] = dict(spec.get("accent_badge") or {})
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
        # Animated triple-pulse strip under the subheadline (L22-ultra parity).
        _accent_pulse_strip(54, 226, accent, accent_soft),
        # Optional detail-bullet line (2 phrases, like L22 ultra's "UAC-0255 -
        # password-protected ZIP - remote access trojan" callout).
        _detail_line(
            254,
            detail_line,
            accent_text,
            accent,
        ),
        # Visual frame: translucent dashed outline + corner brackets +
        # caption tag around the right-half visual zone. Pushes the SVG
        # toward L22-ultra visual density without adding text content.
        _visual_frame(
            740 if accent_badge.get("value") else 840,
            340 if accent_badge.get("value") else 290,
            360,
            300 if accent_badge.get("value") else 340,
            theme,
            visual.replace("_", " ").upper(),
        ),
        # Single hero visualization. When the optional accent_badge is
        # present, shift the visual leftward (cx=740 -> ~590..890) so the
        # 160x120 badge at x=1080 stays clear; otherwise centre as before.
        _render_visual(
            visual,
            740 if accent_badge.get("value") else 840,
            340 if accent_badge.get("value") else 290,
            theme, category.upper(),
        ),
        # Optional standalone accent badge (top-right of hero, mirrors L22
        # ultra's right-side "1M+ EMAILS SENT" KPI hero card).
        _accent_badge(
            1080, 165, theme,
            str(accent_badge.get("value", "")),
            str(accent_badge.get("label", "")),
            str(accent_badge.get("sub", "")),
        ),
        # Tag-chip row + KPI strip + QR (deterministic, no clock reads).
        _tag_chip_row(520, tag_chips, accent),
        _kpi_strip(562, kpi_strip, theme),
        l22.qr_block(url),
        '</svg>',
    ]
    return "\n".join(parts) + "\n"
