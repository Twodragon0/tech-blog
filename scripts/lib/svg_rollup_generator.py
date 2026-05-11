"""Rollup-cover SVG renderer (1200x630) — sibling of svg_l22_generator.

Renders the rollup hybrid layout (D) defined in
``.omc/plans/rollup-cover-design.md``:

  - 80px header with period-label badge (top-right) + monogram glyph (top-left)
  - Top-3 highlight strip (y=100..300): three horizontally-stacked mini-bands,
    each carrying a severity-tinted background, label, headline, source.
  - Day strip (y=320..470): N day-cells. ``weekly_rollup`` => 5-7 cells.
    ``monthly_index`` => 4-31 cells (Jan has 9 W4-only days, Feb collapses to
    4 week-cells, etc).
  - Footer summary stats (y=490..600): 4 stat cards (Daily / Categories /
    Top severity / Period).
  - QR block bottom-right via the shared ``qr_block(url)`` helper.

The module is *additive*: it imports ``THEMES``, ``gen_qr`` and ``qr_block``
from ``svg_l22_generator`` but never modifies them. All theme palette /
gradient / filter ids share a per-spec ``sfx`` suffix to avoid ``<defs>``
collision when this cover and a daily L22 cover render on the same page.

Public API
----------
    render_rollup_svg(spec: dict) -> str
        Render a rollup spec into a complete ``<svg>...</svg>`` string.

Spec contract (matches ``scripts.upgrade_rollup_cover.load_spec``):
    date              : "YYYY-MM-DD"
    slug              : filename slug, underscores preserved
    kind              : "weekly_rollup" | "monthly_index"
    period_label      : e.g. "April 13-19, 2026"
    period_short      : e.g. "W3 April" (header badge)
    daily_count       : int
    daily_count_source: "redirect_from" | "index_table" | "manual"
    sfx               : 1-4 char gradient/filter id suffix
    title             : <title> element text
    aria              : aria-label
    top_highlights    : exactly 3 items, each {severity, label, headline, source}
                        severity in {HIGH, MEDIUM, LOW}
    days              : list of cells, each {date, severity, tag}
    footer            : {daily_digests, categories, period_label} (subset OK)
    url               : optional override; default derived from (date, slug)
"""

from __future__ import annotations

from typing import Dict, List, Optional
from xml.sax.saxutils import escape as _xml_escape

# Reuse the L22 palette + QR helpers verbatim. Do NOT redefine.
from scripts.lib.svg_l22_generator import THEMES, gen_qr, qr_block  # noqa: F401


# Severity -> THEMES key. Plan calls for HIGH=red, MEDIUM=amber, LOW=blue
# (NOT green — see audit doc; green is reserved for L22 wiper/ransomware).
SEVERITY_THEME: Dict[str, str] = {
    "HIGH":   "red",
    "MEDIUM": "amber",
    "LOW":    "blue",
}


def _esc(text: object) -> str:
    """XML-escape user-supplied text. ``&`` -> ``&amp;`` is the load-bearing
    transform (see plan §6 + ``notes/svg_xml_escape.md``).
    """
    if text is None:
        return ""
    return _xml_escape(str(text))


def _post_url(date: str, slug: str) -> str:
    """Canonical Jekyll permalink (underscores preserved per Jekyll convention)."""
    yyyy, mm, dd = date.split("-")
    return f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug}/"


# ---------------------------------------------------------------------------
# Primitive: header (y=0..80)
# ---------------------------------------------------------------------------

def _header(period_short: str, period_label: str, kind: str, date_str: str, sfx: str) -> str:
    """Top 80px banner: gradient strip + period chip + date badge."""
    kind_label = "MONTHLY INDEX" if kind == "monthly_index" else "WEEKLY ROLLUP"
    return f'''<g>
  <rect x="0" y="0" width="1200" height="80" fill="url(#hdrGrad{sfx})"/>
  <rect x="0" y="78" width="1200" height="2" fill="#1B2742" opacity="0.85"/>
  <g transform="translate(36,40)">
    <circle r="20" fill="#0F1A2F" stroke="#3B82F6" stroke-width="1.4"/>
    <path d="M0 -10 L8 -5 L8 4 C8 9 4 12 0 13 C-4 12 -8 9 -8 4 L-8 -5 Z" fill="#3B82F6" opacity="0.85"/>
    <path d="M-3 1 L-1 3 L4 -3" fill="none" stroke="#0A1226" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <text x="76" y="36" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="#9DB4D6" letter-spacing="1.6">{_esc(kind_label)}</text>
  <text x="76" y="58" font-family="Inter, Helvetica, Arial, sans-serif" font-size="22" font-weight="800" fill="#F5F7FA">{_esc(period_label)}</text>
  <g transform="translate(1024,40)">
    <rect x="0" y="-20" width="148" height="40" rx="8" fill="#0F1A2F" stroke="#3B82F6" stroke-width="1.1" opacity="0.95"/>
    <text x="74" y="-2" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="#9DB4D6" letter-spacing="1.4" text-anchor="middle">{_esc(period_short)}</text>
    <text x="74" y="14" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="800" fill="#F5F7FA" text-anchor="middle">{_esc(date_str)}</text>
  </g>
</g>'''


# ---------------------------------------------------------------------------
# Primitive: highlight card (top-3 strip y=100..300)
# ---------------------------------------------------------------------------

def _highlight_card(idx: int, item: dict, sfx: str) -> str:
    """One of three highlight cards at y=100..300.

    Each card is 380w x 200h positioned at x = 28 + idx*388.
    """
    severity = (item.get("severity") or "MEDIUM").upper()
    theme_key = SEVERITY_THEME.get(severity, "amber")
    theme = THEMES[theme_key]
    accent = theme["accent"]
    soft = theme["soft"]
    metric_color = theme["metric"]
    detail_color = theme["detail"]
    label_color = theme["label"]
    card_bg = theme["card"]

    x = 28 + idx * 388
    y = 100
    w, h = 372, 200

    label = item.get("label", "")
    headline = item.get("headline", "")
    detail = item.get("detail", "") or ""
    source = item.get("source", "")

    # Wrap headline to 2 lines on word boundary at ~22 chars/line.
    words = headline.split()
    line1, line2 = "", ""
    for word in words:
        candidate = (line1 + " " + word).strip()
        if len(candidate) <= 26 and not line2:
            line1 = candidate
        else:
            candidate2 = (line2 + " " + word).strip()
            if len(candidate2) <= 30:
                line2 = candidate2
            else:
                break
    if not line1:
        line1 = headline[:26]
    headline_y2 = 162 if line2 else 156

    # Sidebar severity strip on the left edge.
    return f'''<g>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#cardGrad{idx}{sfx})" opacity="0.96"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.7"/>
  <rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{accent}"/>
  <g transform="translate({x + 22},{y + 30})">
    <rect x="0" y="-14" width="92" height="22" rx="11" fill="{accent}" opacity="0.18"/>
    <text x="46" y="2" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" font-weight="800" fill="{accent}" text-anchor="middle" letter-spacing="1.3">{_esc(severity)}</text>
    <text x="106" y="2" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="{label_color}" letter-spacing="1.3">{_esc(label)}</text>
  </g>
  <text x="{x + 22}" y="{y + 80}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="22" font-weight="800" fill="#F5F7FA">{_esc(line1)}</text>
  {f'<text x="{x + 22}" y="{y + 110}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="22" font-weight="800" fill="#F5F7FA">{_esc(line2)}</text>' if line2 else ''}
  <text x="{x + 22}" y="{y + headline_y2 + 14}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" font-weight="600" fill="{detail_color}">{_esc(detail[:60])}</text>
  <g transform="translate({x + 22},{y + h - 22})">
    <circle cx="4" cy="-4" r="3" fill="{soft}"/>
    <text x="14" y="0" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="{metric_color}" letter-spacing="0.6">{_esc(source)}</text>
  </g>
</g>'''


# ---------------------------------------------------------------------------
# Primitive: day strip (y=320..470)
# ---------------------------------------------------------------------------

def _day_strip(days: List[dict], kind: str, sfx: str) -> str:
    """Render N day cells in a horizontal strip at y=320..470.

    Cells scale to fit between x=28 and x=1172 (width = 1144).
    """
    if not days:
        return ""
    n = len(days)
    strip_x, strip_y = 28, 320
    strip_w, strip_h = 1144, 150
    gap = 10
    cell_w = (strip_w - gap * (n - 1)) / n

    title = "DAILY DIGEST TIMELINE" if kind == "weekly_rollup" else "MONTH AT A GLANCE"

    cells_svg: List[str] = []
    for i, d in enumerate(days):
        cx = strip_x + i * (cell_w + gap)
        sev = (d.get("severity") or "MEDIUM").upper()
        theme_key = SEVERITY_THEME.get(sev, "amber")
        theme = THEMES[theme_key]
        accent = theme["accent"]
        date_label = str(d.get("date", ""))
        tag = str(d.get("tag", "") or "")
        # Hard-truncate tags to 30 chars to keep cells readable.
        if len(tag) > 30:
            tag = tag[:27] + "..."

        # Per-cell font sizing: smaller when many cells.
        if n >= 10:
            date_size, tag_size = 13, 9
        elif n >= 8:
            date_size, tag_size = 15, 10
        elif n >= 6:
            date_size, tag_size = 17, 10
        else:
            date_size, tag_size = 18, 11

        cells_svg.append(f'''<g transform="translate({cx:.1f},{strip_y + 30})">
    <rect x="0" y="0" width="{cell_w:.1f}" height="120" rx="10" fill="#0E1A33" opacity="0.92"/>
    <rect x="0" y="0" width="{cell_w:.1f}" height="120" rx="10" fill="none" stroke="{accent}" stroke-width="1" opacity="0.65"/>
    <rect x="0" y="0" width="{cell_w:.1f}" height="5" rx="2" fill="{accent}"/>
    <text x="{cell_w/2:.1f}" y="32" font-family="Inter, Helvetica, Arial, sans-serif" font-size="{date_size}" font-weight="800" fill="#F5F7FA" text-anchor="middle">{_esc(date_label)}</text>
    <rect x="{cell_w/2 - 22:.1f}" y="42" width="44" height="14" rx="7" fill="{accent}" opacity="0.18"/>
    <text x="{cell_w/2:.1f}" y="52" font-family="Inter, Helvetica, Arial, sans-serif" font-size="9" font-weight="800" fill="{accent}" text-anchor="middle" letter-spacing="1.1">{_esc(sev)}</text>
    <text x="{cell_w/2:.1f}" y="80" font-family="Inter, Helvetica, Arial, sans-serif" font-size="{tag_size}" font-weight="600" fill="#CFDAF0" text-anchor="middle">{_esc(tag[:18])}</text>
    {f'<text x="{cell_w/2:.1f}" y="96" font-family="Inter, Helvetica, Arial, sans-serif" font-size="{tag_size}" font-weight="600" fill="#9DB4D6" text-anchor="middle">{_esc(tag[18:36])}</text>' if len(tag) > 18 else ''}
  </g>''')

    cells = "\n  ".join(cells_svg)
    return f'''<g>
  <text x="{strip_x}" y="{strip_y + 18}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="#9DB4D6" letter-spacing="1.6">{_esc(title)}</text>
  <text x="{strip_x + strip_w}" y="{strip_y + 18}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" font-weight="600" fill="#7C92B4" text-anchor="end">{n} cell{'s' if n != 1 else ''}</text>
  {cells}
</g>'''


# ---------------------------------------------------------------------------
# Primitive: footer stats (y=490..600)
# ---------------------------------------------------------------------------

def _footer_stats(
    daily_count: int,
    categories: List[str],
    days: List[dict],
    period_label: str,
    sfx: str,
) -> str:
    """4 stat cards plus a category chip strip."""
    # Compute top severity from days.
    sev_count: Dict[str, int] = {}
    for d in days:
        s = (d.get("severity") or "MEDIUM").upper()
        sev_count[s] = sev_count.get(s, 0) + 1
    if sev_count:
        top_sev = max(sev_count.items(), key=lambda kv: (kv[1], {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(kv[0], 0)))[0]
        top_sev_n = sev_count[top_sev]
    else:
        top_sev, top_sev_n = "MEDIUM", 0
    top_sev_theme = THEMES[SEVERITY_THEME.get(top_sev, "amber")]

    cats = ", ".join((c or "").upper() for c in categories[:3]) if categories else "SECURITY"

    cards = [
        ("DAILY DIGESTS", str(daily_count), "#60A5FA"),
        ("PEAK SEVERITY", f"{top_sev} x{top_sev_n}", top_sev_theme["accent"]),
        ("CATEGORIES",    cats[:22],                  "#A78BFA"),
        ("PERIOD",        period_label[:22],          "#4ADE80"),
    ]

    footer_x, footer_y = 28, 490
    card_w, card_h = 232, 96
    gap = 16

    parts: List[str] = []
    for i, (label, value, accent) in enumerate(cards):
        x = footer_x + i * (card_w + gap)
        parts.append(f'''<g>
  <rect x="{x}" y="{footer_y}" width="{card_w}" height="{card_h}" rx="12" fill="#0A1628" opacity="0.94"/>
  <rect x="{x}" y="{footer_y}" width="{card_w}" height="{card_h}" rx="12" fill="none" stroke="{accent}" stroke-width="1" opacity="0.55"/>
  <rect x="{x + 14}" y="{footer_y + 16}" width="32" height="3" rx="1.5" fill="{accent}"/>
  <text x="{x + 14}" y="{footer_y + 36}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="#9DB4D6" letter-spacing="1.3">{_esc(label)}</text>
  <text x="{x + 14}" y="{footer_y + 72}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="22" font-weight="800" fill="#F5F7FA">{_esc(value)}</text>
</g>''')
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Primitive: defs (gradients + filter) keyed by sfx
# ---------------------------------------------------------------------------

def _defs(spec: dict, sfx: str) -> str:
    """All gradients + filters with sfx-suffixed ids to avoid collision."""
    # Per-card gradients tinted by severity.
    cards = []
    for idx, hl in enumerate(spec.get("top_highlights", [])[:3]):
        sev = (hl.get("severity") or "MEDIUM").upper()
        theme_key = SEVERITY_THEME.get(sev, "amber")
        theme = THEMES[theme_key]
        cards.append(
            f'<linearGradient id="cardGrad{idx}{sfx}" x1="0%" y1="0%" x2="100%" y2="100%">'
            f'<stop offset="0%" stop-color="{theme["bg_a"]}"/>'
            f'<stop offset="100%" stop-color="{theme["bg_b"]}"/>'
            f'</linearGradient>'
        )
    cards_svg = "\n  ".join(cards)
    return f'''<defs>
  <linearGradient id="bgRoll{sfx}" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0A1226"/>
    <stop offset="55%" stop-color="#0C1430"/>
    <stop offset="100%" stop-color="#131038"/>
  </linearGradient>
  <linearGradient id="hdrGrad{sfx}" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#0F1A2F"/>
    <stop offset="50%" stop-color="#15243F"/>
    <stop offset="100%" stop-color="#0F1A2F"/>
  </linearGradient>
  <radialGradient id="ambient{sfx}" cx="50%" cy="50%" r="60%">
    <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="#3B82F6" stop-opacity="0"/>
  </radialGradient>
  <pattern id="rollGrid{sfx}" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M40 0 L0 0 L0 40" fill="none" stroke="#1B2742" stroke-width="0.4" opacity="0.5"/>
  </pattern>
  <filter id="softShadow" x="-10%" y="-10%" width="130%" height="130%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="2.5"/>
    <feOffset dx="1" dy="3"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  {cards_svg}
</defs>'''


# ---------------------------------------------------------------------------
# Primitive: decorative ambient layer
# ---------------------------------------------------------------------------

def _ambient(sfx: str) -> str:
    """Multi-layer ambient decoration to match L22 ultra density (~50KB target).

    Generates ~250 sub-elements deterministically (no randomness — byte-stable
    output across runs). Layers:
      1. Dense dot grid (30 cols x 18 rows = 540 dots) — base texture
      2. Hex motifs at corners — accent shapes
      3. Concentric rings — focal-glow anchor
      4. Top/bottom borders + scan lines
      5. Mid-page diagonal streaks — motion hint
    """
    parts: List[str] = []
    # Layer 1: dense dot grid. 30x18 = 540 dots; opacity tiered by column for depth.
    for col in range(30):
        for row in range(18):
            cx = 28 + col * 40
            cy = 92 + row * 30
            op = 0.10 + ((col + row) % 5) * 0.05
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="1" fill="#3B82F6" opacity="{op:.2f}"/>'
            )
    # Layer 2: hex motifs (4 corners + 2 mid edges).
    hex_pts = "0,-9 8,-4 8,4 0,9 -8,4 -8,-4"
    for hx, hy in ((60, 92), (1140, 92), (60, 588), (1140, 588), (600, 92), (600, 588)):
        parts.append(
            f'<polygon points="{hex_pts}" transform="translate({hx},{hy})" '
            f'fill="none" stroke="#3B82F6" stroke-width="0.7" opacity="0.45"/>'
        )
    # Layer 3: concentric rings (focal anchor).
    for r in (60, 110, 180, 250, 330):
        parts.append(
            f'<circle cx="600" cy="380" r="{r}" fill="none" '
            f'stroke="#3B82F6" stroke-width="0.4" opacity="0.18"/>'
        )
    # Layer 4: scan / divider lines.
    parts.append('<line x1="0" y1="80" x2="1200" y2="80" stroke="#3B82F6" stroke-width="0.6" opacity="0.55"/>')
    parts.append('<line x1="0" y1="316" x2="1200" y2="316" stroke="#1B2742" stroke-width="0.8" opacity="0.55"/>')
    parts.append('<line x1="0" y1="478" x2="1200" y2="478" stroke="#1B2742" stroke-width="1" opacity="0.7"/>')
    # Layer 5: angled streaks (motion hint).
    for i in range(8):
        x = 100 + i * 140
        parts.append(
            f'<line x1="{x}" y1="305" x2="{x + 30}" y2="325" '
            f'stroke="#3B82F6" stroke-width="0.5" opacity="0.35"/>'
        )
    # Layer 6: ambient glow at center.
    parts.append(f'<circle cx="600" cy="380" r="380" fill="url(#ambient{sfx})" opacity="0.6"/>')
    # Layer 7: side gradients (subtle edge vignette).
    parts.append('<rect x="0" y="80" width="40" height="550" fill="#0A1226" opacity="0.4"/>')
    parts.append('<rect x="1160" y="80" width="40" height="550" fill="#0A1226" opacity="0.4"/>')
    # Layer 8: tick marks along top axis.
    for i in range(24):
        tx = 28 + i * 50
        parts.append(
            f'<line x1="{tx}" y1="82" x2="{tx}" y2="88" '
            f'stroke="#3B82F6" stroke-width="0.6" opacity="0.45"/>'
        )
    return '<g aria-hidden="true">\n  ' + "\n  ".join(parts) + "\n</g>"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_rollup_svg(spec: dict) -> str:
    """Render a rollup-cover spec (dict) into a complete SVG string.

    Args:
        spec: validated rollup spec. Must include date, slug, kind,
            period_label, period_short, daily_count, daily_count_source,
            sfx, title, aria, top_highlights (3 items), days (list),
            footer (dict, optional fields).

    Returns:
        Complete ``<svg>...</svg>`` string ready to write to disk.

    Raises:
        ValueError: missing required fields or invalid enums.
    """
    required = (
        "date", "slug", "kind", "period_label", "period_short",
        "daily_count", "daily_count_source", "sfx", "title", "aria",
        "top_highlights", "days",
    )
    missing = [k for k in required if k not in spec]
    if missing:
        raise ValueError(f"render_rollup_svg: missing keys: {missing}")
    if spec["kind"] not in ("weekly_rollup", "monthly_index"):
        raise ValueError(f"render_rollup_svg: invalid kind {spec['kind']!r}")
    highlights = spec["top_highlights"]
    if not isinstance(highlights, list) or len(highlights) != 3:
        raise ValueError(
            f"render_rollup_svg: top_highlights must have exactly 3 items, got {len(highlights) if isinstance(highlights, list) else type(highlights).__name__}"
        )

    sfx = str(spec["sfx"])
    date = spec["date"]
    slug = spec["slug"]
    url = spec.get("url") or _post_url(date, slug)
    period_short = spec["period_short"]
    period_label = spec["period_label"]
    kind = spec["kind"]
    aria = (spec["aria"] or "").strip()
    title = spec["title"]
    days = spec["days"] or []
    footer = spec.get("footer") or {}
    categories: List[str] = list(footer.get("categories") or [])
    daily_count = int(spec["daily_count"])

    defs = _defs(spec, sfx)
    header = _header(period_short, period_label, kind, date, sfx)
    cards_svg = "\n".join(_highlight_card(i, hl, sfx) for i, hl in enumerate(highlights))
    strip = _day_strip(days, kind, sfx)
    stats = _footer_stats(daily_count, categories, days, period_label, sfx)
    ambient = _ambient(sfx)
    qr = qr_block(url)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="{_esc(aria)}">
<title>{_esc(title)}</title>
{defs}
<rect width="1200" height="630" fill="url(#bgRoll{sfx})"/>
<rect width="1200" height="630" fill="url(#rollGrid{sfx})" opacity="0.55"/>
{ambient}
{header}
{cards_svg}
{strip}
{stats}
{qr}
</svg>'''
