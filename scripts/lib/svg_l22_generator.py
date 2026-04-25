"""L22 stacked-bands SVG generator library.

Provides reusable building blocks for the "Layout v22" weekly digest cover
style: a 1200x630 SVG composed of three horizontal bands, each with a
themed gradient, headline, metric, detail, badge card, and a domain-
specific visual icon. Used by ``scripts/generate_post_images.py`` to
produce content-driven covers for Tech Security Weekly Digest posts.

Public API:
    THEMES                 -- color palette dictionary (5 named themes)
    render_bands_svg(...)  -- assemble a complete L22 SVG string
    qr_block(url)          -- bottom-right QR code <g> for the post URL
    visual library: v_wallet_forensic, v_senate_columns, v_price_chart,
                    v_network_nodes, v_browser_cve, v_router_mesh,
                    v_code_bars, v_shield, v_lock_cve, v_cloud_k8s,
                    v_bar_graph

The module has no top-level execution and is safe to import.
"""

from __future__ import annotations

from typing import Dict, List

try:
    import qrcode
    import qrcode.constants

    QRCODE_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    QRCODE_AVAILABLE = False


# --- Theme palette ---
THEMES: Dict[str, Dict[str, str]] = {
    "green":  {"bg_a": "#0E2038", "bg_b": "#12283F", "accent": "#4ADE80", "label": "#4ADE80", "metric": "#9FD3B0", "detail": "#BFC9D9", "card": "#0A1B2E", "soft": "#86EFAC", "pattern": "ledgerGrid"},
    "red":    {"bg_a": "#1A0E2E", "bg_b": "#24122F", "accent": "#E63946", "label": "#F87171", "metric": "#FBB6BD", "detail": "#D9C9CE", "card": "#1E0A14", "soft": "#FCA5A5", "pattern": "circuitDot"},
    "amber":  {"bg_a": "#2A1A0C", "bg_b": "#1E1F0A", "accent": "#FFB703", "label": "#FFB703", "metric": "#FFD58A", "detail": "#E0D5B6", "card": "#1E1805", "soft": "#FCD34D", "pattern": "ledgerGrid"},
    "blue":   {"bg_a": "#0A1B35", "bg_b": "#0D2040", "accent": "#60A5FA", "label": "#93C5FD", "metric": "#BFDBFE", "detail": "#D0DCF0", "card": "#0A1628", "soft": "#93C5FD", "pattern": "ledgerGrid"},
    "purple": {"bg_a": "#1E0A3A", "bg_b": "#2A0E4A", "accent": "#A78BFA", "label": "#C4B5FD", "metric": "#DDD6FE", "detail": "#D0CCE5", "card": "#160629", "soft": "#C4B5FD", "pattern": "circuitDot"},
}


# --- QR code ---
def gen_qr(url: str) -> str:
    """Return SVG path data encoding ``url`` as a 84x84 px QR matrix.

    Falls back to an empty path when the optional ``qrcode`` package is
    not installed so the rest of the SVG still renders.
    """
    if not QRCODE_AVAILABLE:
        return ""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    size = len(matrix)
    scale = 84.0 / size
    parts: List[str] = []
    for ri, row in enumerate(matrix):
        j = 0
        while j < size:
            if row[j]:
                run = 0
                while j + run < size and row[j + run]:
                    run += 1
                parts.append(
                    f"M{round(j*scale,3)} {round(ri*scale,3)}"
                    f"h{round(run*scale,3)}v{round(scale,3)}"
                    f"h-{round(run*scale,3)}z"
                )
                j += run
            else:
                j += 1
    return " ".join(parts)


def qr_block(url: str) -> str:
    """Return the bottom-right QR <g> element for a 1200x630 cover."""
    return (
        f'<g transform="translate(1080,504)" filter="url(#softShadow)">\n'
        f'  <rect x="-8" y="-8" width="100" height="100" rx="6" fill="#FFFFFF"/>\n'
        f'  <path fill="#0A1020" d="{gen_qr(url)}"/>\n'
        f'</g>\n'
        f'<text x="1122" y="614" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="10" font-weight="700" fill="#F5F7FA" text-anchor="middle">scan / full post</text>'
    )


# --- Band builder ---
def band(
    idx: int,
    theme: dict,
    label: str,
    headline: str,
    metric: str,
    detail: str,
    badge_value: str,
    badge_label: str,
    badge_sub: str,
    visual_svg: str,
    sfx: str,
) -> str:
    """Build a single horizontal band. ``idx`` 0/1/2 maps to y 0/210/420."""
    y = idx * 210
    yc = y + 105
    label_y = y + 44
    head_y = y + 86
    metric_y = y + 118
    detail_y = y + 146
    pat = theme["pattern"]
    bid = ["bandA", "bandB", "bandC"][idx]
    return f'''<g>
  <rect x="0" y="{y}" width="1200" height="210" fill="url(#{bid}{sfx})"/>
  <rect x="0" y="{y}" width="1200" height="210" fill="url(#{pat})" opacity="0.6"/>
  <rect x="0" y="{y}" width="8" height="210" fill="{theme["accent"]}"/>
  <g filter="url(#textShadow)">
    <text x="30" y="{label_y}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="18" font-weight="700" letter-spacing="2.4" fill="{theme["label"]}">{label}</text>
    <text x="30" y="{head_y}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="36" font-weight="800" fill="#F5F7FA">{headline}</text>
    <text x="30" y="{metric_y}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="20" font-weight="600" fill="{theme["metric"]}">{metric}</text>
    <text x="30" y="{detail_y}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="15" font-weight="500" fill="{theme["detail"]}">{detail}</text>
  </g>
  {visual_svg}
  <g transform="translate(990,{yc})" filter="url(#softShadow)">
    <rect x="-80" y="-65" width="180" height="125" rx="14" fill="{theme["card"]}" stroke="{theme["accent"]}" stroke-width="2.2"/>
    <text x="10" y="-30" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="2" fill="{theme["label"]}">{badge_label}</text>
    <text x="10" y="28" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="{60 if len(badge_value)>3 else 72}" font-weight="900" fill="#F5F7FA">{badge_value}</text>
    <text x="10" y="52" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" font-weight="600" fill="{theme["metric"]}">{badge_sub}</text>
  </g>
  <g transform="translate(990,{yc})"><circle cx="10" cy="-50" r="3" fill="{theme["accent"]}"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" repeatCount="indefinite"/></circle></g>
</g>'''


# --- Visual library (each returns an SVG <g> string) ---
def v_wallet_forensic(cx: int, yc: int, accent: str, soft: str) -> str:
    """Blockchain/wallet nodes connected in forensic fund flow."""
    return f'''<g transform="translate({cx},{yc})">
    <g stroke="{accent}" stroke-width="1" stroke-dasharray="3 4" fill="none" opacity="0.6">
      <line x1="-80" y1="0" x2="-20" y2="-35"/><line x1="-80" y1="0" x2="-20" y2="0"/><line x1="-80" y1="0" x2="-20" y2="35"/>
      <line x1="-20" y1="-35" x2="50" y2="-55"/><line x1="-20" y1="-35" x2="50" y2="-20"/>
      <line x1="-20" y1="0" x2="50" y2="15"/><line x1="-20" y1="35" x2="50" y2="55"/><line x1="-20" y1="35" x2="50" y2="25"/>
    </g>
    <g fill="{accent}" opacity="0.9">
      <circle cx="-80" cy="0" r="12" stroke="{soft}" stroke-width="1.4"><animate attributeName="r" values="10;14;10" dur="2.6s" repeatCount="indefinite"/></circle>
      <circle cx="-20" cy="-35" r="6"/><circle cx="-20" cy="0" r="6"/><circle cx="-20" cy="35" r="6"/>
      <circle cx="50" cy="-55" r="5" opacity="0.8"/><circle cx="50" cy="-20" r="5" opacity="0.8"/><circle cx="50" cy="15" r="5" opacity="0.8"/><circle cx="50" cy="55" r="5" opacity="0.8"/><circle cx="50" cy="25" r="5" opacity="0.8"/>
    </g>
    <g fill="#F5F7FA">
      <circle r="2"><animateMotion path="M-80 0 L-20 -35" dur="2.1s" repeatCount="indefinite"/></circle>
      <circle r="2"><animateMotion path="M-80 0 L-20 0" dur="1.9s" repeatCount="indefinite"/></circle>
      <circle r="2"><animateMotion path="M-80 0 L-20 35" dur="2.3s" repeatCount="indefinite"/></circle>
    </g>
    <text x="-80" y="34" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="{accent}">WALLET</text>
  </g>'''


def v_senate_columns(cx: int, yc: int, accent: str) -> str:
    """Senate columns with gavel for regulation theme."""
    return f'''<g transform="translate({cx},{yc})">
    <g stroke="{accent}" stroke-width="1.8" fill="{accent}" fill-opacity="0.12">
      <rect x="-75" y="-40" width="10" height="70" rx="1"/>
      <rect x="-50" y="-40" width="10" height="70" rx="1"/>
      <rect x="-25" y="-40" width="10" height="70" rx="1"/>
      <rect x="0" y="-40" width="10" height="70" rx="1"/>
      <rect x="25" y="-40" width="10" height="70" rx="1"/>
      <path d="M-85 -45 L50 -45 L50 -52 L-85 -52 Z"/>
      <path d="M-85 30 L50 30 L50 38 L-85 38 Z"/>
    </g>
    <g transform="translate(72,-5) rotate(25)">
      <rect x="-6" y="-20" width="12" height="30" rx="2" fill="{accent}"/>
      <rect x="-3" y="10" width="6" height="35" fill="{accent}" opacity="0.8"/>
      <animate attributeName="transform" values="translate(72,-5) rotate(25);translate(72,-5) rotate(-10);translate(72,-5) rotate(25)" dur="2.4s" repeatCount="indefinite"/>
    </g>
  </g>'''


def v_price_chart(cx: int, yc: int, accent: str, soft: str) -> str:
    """Downtrend price chart."""
    return f'''<g transform="translate({cx},{yc})">
    <g stroke="{accent}" stroke-width="0.4" opacity="0.3">
      <line x1="-90" y1="-40" x2="90" y2="-40"/><line x1="-90" y1="-15" x2="90" y2="-15"/>
      <line x1="-90" y1="10" x2="90" y2="10"/><line x1="-90" y1="35" x2="90" y2="35"/>
    </g>
    <path d="M-90 -30 L-60 -20 L-30 -25 L0 -5 L30 5 L60 20 L90 35" stroke="{accent}" stroke-width="2.5" fill="none">
      <animate attributeName="stroke-dasharray" values="0 400;400 0" dur="3.2s" repeatCount="indefinite"/>
    </path>
    <path d="M-90 -30 L-60 -20 L-30 -25 L0 -5 L30 5 L60 20 L90 35 L90 40 L-90 40 Z" fill="{accent}" fill-opacity="0.12"/>
    <g fill="{soft}">
      <circle cx="-90" cy="-30" r="3"/><circle cx="-60" cy="-20" r="3"/><circle cx="-30" cy="-25" r="3"/>
      <circle cx="0" cy="-5" r="3"/><circle cx="30" cy="5" r="3"/><circle cx="60" cy="20" r="3"/>
      <circle cx="90" cy="35" r="4"><animate attributeName="r" values="3;6;3" dur="1.8s" repeatCount="indefinite"/></circle>
    </g>
  </g>'''


def v_network_nodes(cx: int, yc: int, accent: str, soft: str, label: str = "INFRA") -> str:
    """Central hub with radiating infected nodes."""
    return f'''<g transform="translate({cx},{yc})">
    <circle r="60" fill="{accent}" fill-opacity="0.08"><animate attributeName="r" values="50;70;50" dur="3s" repeatCount="indefinite"/></circle>
    <circle r="22" fill="{accent}" stroke="{soft}" stroke-width="2" filter="url(#softShadow)"/>
    <text y="4" text-anchor="middle" font-family="Inter, monospace" font-size="11" font-weight="800" fill="#FFF">{label}</text>
    <g stroke="{accent}" stroke-width="1" stroke-dasharray="2 3" fill="none" opacity="0.55">
      <line x1="0" y1="0" x2="70" y2="-45"/><line x1="0" y1="0" x2="85" y2="0"/><line x1="0" y1="0" x2="70" y2="45"/>
      <line x1="0" y1="0" x2="-70" y2="-45"/><line x1="0" y1="0" x2="-85" y2="0"/><line x1="0" y1="0" x2="-70" y2="45"/>
      <line x1="0" y1="0" x2="40" y2="-70"/><line x1="0" y1="0" x2="-40" y2="-70"/>
    </g>
    <g fill="{soft}">
      <circle cx="70" cy="-45" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" repeatCount="indefinite"/></circle>
      <circle cx="85" cy="0" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.1s" repeatCount="indefinite"/></circle>
      <circle cx="70" cy="45" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" repeatCount="indefinite"/></circle>
      <circle cx="-70" cy="-45" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.9s" repeatCount="indefinite"/></circle>
      <circle cx="-85" cy="0" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.3s" repeatCount="indefinite"/></circle>
      <circle cx="-70" cy="45" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.0s" repeatCount="indefinite"/></circle>
      <circle cx="40" cy="-70" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite"/></circle>
      <circle cx="-40" cy="-70" r="4"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.7s" repeatCount="indefinite"/></circle>
    </g>
    <g fill="#FFF">
      <circle r="1.6"><animateMotion path="M0 0 L70 -45" dur="1.9s" repeatCount="indefinite"/></circle>
      <circle r="1.6"><animateMotion path="M0 0 L85 0" dur="2.1s" repeatCount="indefinite"/></circle>
      <circle r="1.6"><animateMotion path="M0 0 L-70 -45" dur="2.0s" repeatCount="indefinite"/></circle>
      <circle r="1.6"><animateMotion path="M0 0 L-85 0" dur="2.3s" repeatCount="indefinite"/></circle>
    </g>
  </g>'''


def v_browser_cve(cx: int, yc: int, accent: str, soft: str, label: str = "CVE") -> str:
    """Browser window with CVE vulnerability indicator."""
    return f'''<g transform="translate({cx},{yc})">
    <rect x="-75" y="-50" width="150" height="100" rx="8" fill="{accent}" fill-opacity="0.08" stroke="{accent}" stroke-width="1.8" filter="url(#softShadow)"/>
    <rect x="-75" y="-50" width="150" height="18" rx="8" fill="{accent}" fill-opacity="0.3"/>
    <g fill="{accent}"><circle cx="-65" cy="-41" r="3"/><circle cx="-55" cy="-41" r="3"/><circle cx="-45" cy="-41" r="3"/></g>
    <rect x="-65" y="-22" width="130" height="6" rx="2" fill="{accent}" fill-opacity="0.25"/>
    <g transform="translate(0,10)">
      <polygon points="0,-22 22,18 -22,18" fill="{accent}" stroke="{soft}" stroke-width="1.4" filter="url(#softShadow)"><animate attributeName="opacity" values="0.7;1;0.7" dur="1.4s" repeatCount="indefinite"/></polygon>
      <text y="10" text-anchor="middle" font-family="Inter, monospace" font-size="16" font-weight="900" fill="#FFF">!</text>
    </g>
    <text y="62" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="{accent}">{label}</text>
  </g>'''


def v_router_mesh(cx: int, yc: int, accent: str, soft: str) -> str:
    """Router topology mesh."""
    return f'''<g transform="translate({cx},{yc})">
    <g stroke="{accent}" stroke-width="0.8" fill="none" opacity="0.4">
      <line x1="-70" y1="-40" x2="0" y2="0"/><line x1="70" y1="-40" x2="0" y2="0"/>
      <line x1="-70" y1="40" x2="0" y2="0"/><line x1="70" y1="40" x2="0" y2="0"/>
      <line x1="-70" y1="-40" x2="-70" y2="40"/><line x1="70" y1="-40" x2="70" y2="40"/>
    </g>
    <g fill="{accent}" opacity="0.85">
      <rect x="-82" y="-48" width="24" height="16" rx="2"/><rect x="58" y="-48" width="24" height="16" rx="2"/>
      <rect x="-82" y="32" width="24" height="16" rx="2"/><rect x="58" y="32" width="24" height="16" rx="2"/>
    </g>
    <g fill="{soft}">
      <circle cx="-70" cy="-40" r="2"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" repeatCount="indefinite"/></circle>
      <circle cx="70" cy="-40" r="2"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.1s" repeatCount="indefinite"/></circle>
      <circle cx="-70" cy="40" r="2"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.3s" repeatCount="indefinite"/></circle>
      <circle cx="70" cy="40" r="2"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.9s" repeatCount="indefinite"/></circle>
    </g>
    <circle r="16" fill="{accent}" stroke="{soft}" stroke-width="2"/>
    <text y="4" text-anchor="middle" font-family="Inter, monospace" font-size="9" font-weight="800" fill="#FFF">HUB</text>
  </g>'''


def v_code_bars(cx: int, yc: int, accent: str, soft: str, caption: str = "CODE") -> str:
    """Code lines / signal bars as generic technical visual."""
    return f'''<g transform="translate({cx},{yc})">
    <g stroke="{accent}" stroke-width="2" opacity="0.85">
      <line x1="-80" y1="-40" x2="-30" y2="-40"/><line x1="-25" y1="-40" x2="40" y2="-40"/>
      <line x1="-80" y1="-20" x2="-10" y2="-20"/><line x1="-5" y1="-20" x2="55" y2="-20"/>
      <line x1="-80" y1="0" x2="-40" y2="0"/><line x1="-35" y1="0" x2="60" y2="0"/>
      <line x1="-80" y1="20" x2="-20" y2="20"/><line x1="-15" y1="20" x2="30" y2="20"/>
      <line x1="-80" y1="40" x2="-50" y2="40"/><line x1="-45" y1="40" x2="50" y2="40"/>
    </g>
    <rect x="-82" y="-50" width="4" height="110" fill="{accent}" opacity="0.6"/>
    <g fill="{soft}">
      <circle cx="70" cy="-40" r="3"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.6s" repeatCount="indefinite"/></circle>
      <circle cx="70" cy="0" r="3"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.1s" repeatCount="indefinite"/></circle>
      <circle cx="70" cy="40" r="3"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.9s" repeatCount="indefinite"/></circle>
    </g>
    <text y="62" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="{accent}">{caption}</text>
  </g>'''


def v_shield(cx: int, yc: int, accent: str, soft: str, label: str = "SHIELD") -> str:
    """Shield emblem for defense/security theme."""
    return f'''<g transform="translate({cx},{yc})">
    <path d="M0 -60 L55 -40 L50 25 Q40 55 0 65 Q-40 55 -50 25 L-55 -40 Z" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="2.4" filter="url(#softShadow)"/>
    <path d="M0 -50 L45 -33 L40 22 Q32 46 0 55 Q-32 46 -40 22 L-45 -33 Z" fill="none" stroke="{soft}" stroke-width="1" opacity="0.7"/>
    <g transform="translate(0,-5)" stroke="{soft}" stroke-width="3" fill="none">
      <path d="M-18 5 L-4 20 L22 -12"><animate attributeName="stroke-dasharray" values="0 80;80 0" dur="2.4s" repeatCount="indefinite"/></path>
    </g>
    <text y="44" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="{accent}">{label}</text>
  </g>'''


def v_lock_cve(cx: int, yc: int, accent: str, soft: str, cvss: str = "9.8") -> str:
    """Padlock with CVE score."""
    return f'''<g transform="translate({cx},{yc})">
    <path d="M-22 -20 Q-22 -50 0 -50 Q22 -50 22 -20" stroke="{accent}" stroke-width="4" fill="none"/>
    <rect x="-32" y="-22" width="64" height="60" rx="6" fill="{accent}" fill-opacity="0.2" stroke="{accent}" stroke-width="2.2" filter="url(#softShadow)"/>
    <circle r="5" fill="{soft}" cy="2"/>
    <rect x="-3" y="2" width="6" height="18" fill="{soft}"/>
    <text y="60" text-anchor="middle" font-family="Inter, monospace" font-size="14" font-weight="900" fill="{accent}">CVSS {cvss}</text>
    <g fill="{soft}" opacity="0.7">
      <circle cx="-45" cy="-35" r="2"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" repeatCount="indefinite"/></circle>
      <circle cx="45" cy="-35" r="2"><animate attributeName="opacity" values="0.2;1;0.2" dur="2.1s" repeatCount="indefinite"/></circle>
      <circle cx="-45" cy="35" r="2"><animate attributeName="opacity" values="0.2;1;0.2" dur="2.3s" repeatCount="indefinite"/></circle>
      <circle cx="45" cy="35" r="2"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.9s" repeatCount="indefinite"/></circle>
    </g>
  </g>'''


def v_cloud_k8s(cx: int, yc: int, accent: str, soft: str) -> str:
    """Cloud with K8s hexagonal nodes."""
    return f'''<g transform="translate({cx},{yc})">
    <path d="M-60 0 Q-70 -25 -45 -30 Q-40 -50 -10 -45 Q10 -60 30 -45 Q55 -50 60 -20 Q80 -15 70 10 Q65 25 40 25 L-40 25 Q-70 25 -60 0 Z" fill="{accent}" fill-opacity="0.12" stroke="{accent}" stroke-width="1.8"/>
    <g fill="{accent}" stroke="{soft}" stroke-width="1.2">
      <polygon points="-30,-10 -18,-17 -6,-10 -6,4 -18,11 -30,4"/>
      <polygon points="0,-10 12,-17 24,-10 24,4 12,11 0,4"/>
      <polygon points="-15,10 -3,3 9,10 9,24 -3,31 -15,24"/>
    </g>
    <g fill="{soft}">
      <circle cx="-18" cy="-3" r="2"/><circle cx="12" cy="-3" r="2"/><circle cx="-3" cy="17" r="2"/>
    </g>
    <text y="55" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="{accent}">K8s CLOUD</text>
  </g>'''


def v_bar_graph(cx: int, yc: int, accent: str, soft: str, caption: str = "GROWTH") -> str:
    """Bar graph with animated bars."""
    bars = ""
    heights = [30, 55, 40, 70, 85, 62]
    for i, h in enumerate(heights):
        x = -75 + i * 28
        bars += (
            f'<rect x="{x}" y="{40 - h}" width="20" height="{h}" rx="2" fill="{accent}" opacity="{0.5 + i * 0.08}">'
            f'<animate attributeName="height" values="{h - 10};{h};{h - 10}" dur="{1.6 + i * 0.2}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{50 - h};{40 - h};{50 - h}" dur="{1.6 + i * 0.2}s" repeatCount="indefinite"/>'
            f'</rect>'
        )
    return f'''<g transform="translate({cx},{yc})">
    <line x1="-85" y1="40" x2="95" y2="40" stroke="{accent}" stroke-width="1" opacity="0.5"/>
    {bars}
    <text y="58" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="{soft}">{caption}</text>
  </g>'''


# --- Decorative ambient layer ---
def deco_layer(theme_a: dict, theme_b: dict, theme_c: dict) -> str:
    """Small animated particles overlay tied to each band's accent."""
    return f'''<g opacity="0.9">
  <g fill="{theme_a["accent"]}">
    <circle cx="240" cy="168" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.8s" repeatCount="indefinite"/></circle>
    <circle cx="310" cy="168" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="0.2s" repeatCount="indefinite"/></circle>
    <circle cx="380" cy="168" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="2.0s" begin="0.4s" repeatCount="indefinite"/></circle>
    <circle cx="820" cy="168" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.9s" repeatCount="indefinite"/></circle>
    <circle cx="880" cy="168" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="2.1s" begin="0.3s" repeatCount="indefinite"/></circle>
  </g>
  <g fill="{theme_b["label"]}">
    <circle cx="560" cy="260" r="1.2"><animate attributeName="opacity" values="0;1;0" dur="1.8s" repeatCount="indefinite"/></circle>
    <circle cx="600" cy="268" r="1.2"><animate attributeName="opacity" values="0;1;0" dur="2.0s" begin="0.4s" repeatCount="indefinite"/></circle>
    <circle cx="640" cy="268" r="1.2"><animate attributeName="opacity" values="0;1;0" dur="1.9s" begin="0.8s" repeatCount="indefinite"/></circle>
  </g>
  <g fill="{theme_c["accent"]}">
    <circle cx="260" cy="442" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.5s" repeatCount="indefinite"/></circle>
    <circle cx="330" cy="442" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.7s" begin="0.2s" repeatCount="indefinite"/></circle>
    <circle cx="400" cy="442" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.9s" begin="0.4s" repeatCount="indefinite"/></circle>
    <circle cx="470" cy="442" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="0.6s" repeatCount="indefinite"/></circle>
  </g>
</g>'''


# --- Full 3-band SVG assembly ---
def render_bands_svg(
    sfx: str,
    aria: str,
    title: str,
    url: str,
    bands_cfg: List[dict],
) -> str:
    """Render a complete L22 stacked-bands cover SVG.

    Args:
        sfx: Unique 1-2 char suffix for gradient/filter ids (avoids
            collisions when multiple SVGs are inlined on the same page).
        aria: ARIA label for accessibility.
        title: ``<title>`` element text.
        url: Post URL encoded as the QR block.
        bands_cfg: List of exactly 3 dicts, each with keys:
            theme, label, headline, metric, detail,
            badge_value, badge_label, badge_sub, visual.

    Returns:
        Complete ``<svg>...</svg>`` string ready to write to disk.
    """
    if len(bands_cfg) != 3:
        raise ValueError(f"render_bands_svg requires exactly 3 bands, got {len(bands_cfg)}")

    t0 = THEMES[bands_cfg[0]["theme"]]
    t1 = THEMES[bands_cfg[1]["theme"]]
    t2 = THEMES[bands_cfg[2]["theme"]]
    defs = f'''<defs>
<linearGradient id="bgSpread{sfx}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0A1226"/><stop offset="50%" stop-color="#0C1430"/><stop offset="100%" stop-color="#131038"/></linearGradient>
<linearGradient id="bandA{sfx}" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{t0["bg_a"]}"/><stop offset="100%" stop-color="{t0["bg_b"]}"/></linearGradient>
<linearGradient id="bandB{sfx}" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{t1["bg_a"]}"/><stop offset="100%" stop-color="{t1["bg_b"]}"/></linearGradient>
<linearGradient id="bandC{sfx}" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{t2["bg_a"]}"/><stop offset="100%" stop-color="{t2["bg_b"]}"/></linearGradient>
<filter id="softShadow" x="-10%" y="-10%" width="130%" height="130%"><feGaussianBlur in="SourceAlpha" stdDeviation="2.5"/><feOffset dx="1" dy="3"/><feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="textShadow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur in="SourceAlpha" stdDeviation="1.2"/><feOffset dx="0" dy="1.5"/><feComponentTransfer><feFuncA type="linear" slope="0.85"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="ledgerGrid" x="0" y="0" width="40" height="20" patternUnits="userSpaceOnUse"><path d="M0 20 L40 20" stroke="#2A3A56" stroke-width="0.4" opacity="0.5"/><path d="M40 0 L40 20" stroke="#2A3A56" stroke-width="0.4" opacity="0.5"/></pattern>
<pattern id="circuitDot" x="0" y="0" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="9" cy="9" r="0.8" fill="#3A2A4E" opacity="0.55"/></pattern>
</defs>'''

    body_parts = []
    for i, cfg in enumerate(bands_cfg):
        theme = THEMES[cfg["theme"]]
        body_parts.append(band(
            idx=i, theme=theme,
            label=cfg["label"], headline=cfg["headline"],
            metric=cfg["metric"], detail=cfg["detail"],
            badge_value=cfg["badge_value"], badge_label=cfg["badge_label"], badge_sub=cfg["badge_sub"],
            visual_svg=cfg["visual"], sfx=sfx,
        ))
    bands_svg = "\n".join(body_parts)
    deco = deco_layer(t0, t1, t2)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="{aria}">
<title>{title}</title>
{defs}
<rect width="1200" height="630" fill="url(#bgSpread{sfx})"/>
{bands_svg}
{deco}
{qr_block(url)}
</svg>'''
