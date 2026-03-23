#!/usr/bin/env python3
"""
regenerate_svgs.py - Regenerate all 38 placeholder SVG hero images with rich visual content.
Each SVG is 1200x630px with dark gradient background, topic-specific colors, and visual elements.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")


# ── Topic detection & theming ────────────────────────────────────────────────


def detect_topic(title_en: str, image_path: str) -> dict:
    """Return theme dict based on keywords in the English title/path."""
    text = (title_en + " " + image_path).lower()

    if any(k in text for k in ["weekly digest", "weekly review", "digest"]):
        return {
            "accent": "#6366f1",
            "accent2": "#818cf8",
            "category": "WEEKLY DIGEST",
            "visual": "newspaper",
            "cards": [("Week", "Digest"), ("CVE", "Alerts"), ("Threat", "Intel")],
        }
    if any(k in text for k in ["ransomware", "malware", "kimwolf", "threat", "kara"]):
        return {
            "accent": "#dc2626",
            "accent2": "#ef4444",
            "category": "THREAT INTEL",
            "visual": "warning",
            "cards": [("IOC", "Feeds"), ("TTPs", "MITRE"), ("YARA", "Rules")],
        }
    if any(
        k in text
        for k in [
            "incident",
            "post-mortem",
            "postmortem",
            "karpenter",
            "outage",
            "5xx",
            "cloudflare global",
        ]
    ):
        return {
            "accent": "#ef4444",
            "accent2": "#f87171",
            "category": "INCIDENT",
            "visual": "warning",
            "cards": [("RCA", "Analysis"), ("MTTR", "Response"), ("SLO", "Impact")],
        }
    if any(k in text for k in ["npm", "supply chain", "shai-hulud", "package"]):
        return {
            "accent": "#f97316",
            "accent2": "#fb923c",
            "category": "SUPPLY CHAIN",
            "visual": "warning",
            "cards": [("NPM", "Registry"), ("SBOM", "Audit"), ("CVE", "Scan")],
        }
    if any(k in text for k in ["email", "sendgrid", "dkim", "spf", "dmarc"]):
        return {
            "accent": "#0ea5e9",
            "accent2": "#38bdf8",
            "category": "EMAIL SECURITY",
            "visual": "shield",
            "cards": [("SPF", "Record"), ("DKIM", "Signing"), ("DMARC", "Policy")],
        }
    if any(k in text for k in ["blockchain", "crypto", "bitcoin", "ethereum"]):
        return {
            "accent": "#10b981",
            "accent2": "#34d399",
            "category": "BLOCKCHAIN",
            "visual": "network",
            "cards": [
                ("DeFi", "Protocol"),
                ("Smart", "Contract"),
                ("Web3", "Security"),
            ],
        }
    if any(
        k in text
        for k in ["tesla", "automotive", "vehicle", "fsd", "model y", "connected car"]
    ):
        return {
            "accent": "#a855f7",
            "accent2": "#c084fc",
            "category": "AUTOMOTIVE",
            "visual": "geometric",
            "cards": [("FSD", "Safety"), ("OTA", "Updates"), ("CAN", "Security")],
        }
    if any(k in text for k in ["owasp"]):
        return {
            "accent": "#0066cc",
            "accent2": "#3b82f6",
            "category": "WEB SECURITY",
            "visual": "shield",
            "cards": [
                ("Top 10", "Risks"),
                ("MITRE", "ATT&CK"),
                ("Zero Trust", "Framework"),
            ],
        }
    if any(k in text for k in ["finops", "cost", "billing"]):
        return {
            "accent": "#eab308",
            "accent2": "#facc15",
            "category": "FINOPS",
            "visual": "geometric",
            "cards": [
                ("Cost", "Optimize"),
                ("Reserved", "Instances"),
                ("Budget", "Alerts"),
            ],
        }
    if any(
        k in text
        for k in [
            "kubernetes",
            "k8s",
            "k9s",
            "minikube",
            "karpenter",
            "container",
            "docker",
        ]
    ):
        return {
            "accent": "#3b82f6",
            "accent2": "#60a5fa",
            "category": "INFRASTRUCTURE",
            "visual": "containers",
            "cards": [("Pod", "Security"), ("RBAC", "Access"), ("Network", "Policy")],
        }
    if any(k in text for k in ["devsecops", "ci/cd", "pipeline", "roadmap", "devops"]):
        return {
            "accent": "#8b5cf6",
            "accent2": "#a78bfa",
            "category": "DEVSECOPS",
            "visual": "pipeline",
            "cards": [("SAST", "Scan"), ("DAST", "Test"), ("SCA", "Audit")],
        }
    if any(
        k in text
        for k in [
            "ai",
            "ml",
            "llm",
            "claude",
            "gemini",
            "music video",
            "coding assistant",
            "agentic",
            "neural",
        ]
    ):
        return {
            "accent": "#06b6d4",
            "accent2": "#22d3ee",
            "category": "AI & ML",
            "visual": "network",
            "cards": [("LLM", "Safety"), ("Prompt", "Injection"), ("RAG", "Security")],
        }
    if any(
        k in text
        for k in [
            "aws",
            "gcp",
            "azure",
            "cloud",
            "waf",
            "cloudfront",
            "vpc",
            "iam",
            "eks",
            "control tower",
            "guardrail",
        ]
    ):
        return {
            "accent": "#f59e0b",
            "accent2": "#fbbf24",
            "category": "CLOUD",
            "visual": "cloud",
            "cards": [
                ("VPC", "Network"),
                ("IAM", "Access"),
                ("GuardDuty", "Detection"),
            ],
        }
    if any(
        k in text
        for k in [
            "security",
            "vulnerability",
            "isms",
            "waf",
            "passkey",
            "mfa",
            "imei",
            "usim",
            "nlb",
            "zero-day",
            "patch",
            "cve",
            "rce",
        ]
    ):
        return {
            "accent": "#ef4444",
            "accent2": "#f87171",
            "category": "SECURITY",
            "visual": "shield",
            "cards": [
                ("Top 10", "Risks"),
                ("MITRE", "ATT&CK"),
                ("Zero Trust", "Framework"),
            ],
        }
    # default
    return {
        "accent": "#6366f1",
        "accent2": "#818cf8",
        "category": "TECH",
        "visual": "geometric",
        "cards": [("Security", "First"), ("DevSecOps", "Guide"), ("Best", "Practice")],
    }


# ── Title cleaning (Korean → English fallback) ───────────────────────────────


def clean_title_for_svg(raw_title: str, image_path: str) -> str:
    """Return a clean ASCII title suitable for SVG text."""
    # If title is mostly Korean or very short, derive from image path
    korean_chars = len(re.findall(r"[\uac00-\ud7af]", raw_title))
    total_chars = len(raw_title.strip())

    if korean_chars / max(total_chars, 1) > 0.3 or total_chars < 5:
        # Derive from image filename
        stem = os.path.basename(image_path).replace(".svg", "")
        # Remove date prefix
        stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
        # Clean up encoded chars
        stem = re.sub(r"ampquot|ampamp|amplsquot|amprsquo|amp", "", stem)
        stem = stem.replace("_", " ").replace("-", " ")
        stem = re.sub(r"\s+", " ", stem).strip()
        # Remove trailing known noise
        stem = re.sub(
            r"\s*(Large scale|Complete Guide|and Resolution|From Practical To)\s*$",
            "",
            stem,
        )
        return stem[:80]
    else:
        # Strip Korean, keep English tokens
        # First try extracting English portion after colon
        if ":" in raw_title:
            after = raw_title.split(":", 1)[1]
            eng = re.sub(r"[\uac00-\ud7af\u3131-\u318e]+", "", after)
            eng = re.sub(r"\s+", " ", eng).strip(" ,.-")
            if len(eng) > 10:
                return eng[:80]
        # Strip Korean chars
        eng = re.sub(r"[\uac00-\ud7af\u3131-\u318e]+", "", raw_title)
        # Remove emoji
        eng = re.sub(r"[\U00010000-\U0010ffff]", "", eng)
        eng = re.sub(r"[^\x00-\x7F]", "", eng)
        eng = re.sub(r"\s+", " ", eng).strip(" :,.-&")
        if len(eng) < 5:
            return clean_title_for_svg("", image_path)
        return eng[:80]


def split_title_lines(title: str, max_chars: int = 28) -> list[str]:
    """Split title into 2-3 lines for SVG display."""
    words = title.split()
    lines: list[str] = []
    current: list[str] = []
    for w in words:
        current_len: int = sum([len(x) for x in current])
        if current_len + len(current) + len(w) <= max_chars:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
        if len(lines) == 2:
            # dump rest into 3rd line
            current.extend(words[words.index(w) + 1 :])
            break
    if current:
        lines.append(" ".join(current))
    return lines[:3]


# ── Visual elements ──────────────────────────────────────────────────────────


def visual_shield(cx: float, cy: float, color: str) -> str:
    """Shield with lock icon."""
    return f"""
    <!-- Shield -->
    <path d="M{cx},{cy - 80} L{cx + 65},{cy - 50} L{cx + 65},{cy + 30} Q{cx + 65},{cy + 80} {cx},{cy + 100} Q{cx - 65},{cy + 80} {cx - 65},{cy + 30} L{cx - 65},{cy - 50} Z"
          fill="none" stroke="{color}" stroke-width="4" opacity="0.25"/>
    <path d="M{cx},{cy - 60} L{cx + 48},{cy - 36} L{cx + 48},{cy + 20} Q{cx + 48},{cy + 60} {cx},{cy + 76} Q{cx - 48},{cy + 60} {cx - 48},{cy + 20} L{cx - 48},{cy - 36} Z"
          fill="{color}" opacity="0.12"/>
    <!-- Lock body -->
    <rect x="{cx - 18}" y="{cy - 5}" width="36" height="28" rx="5" fill="{color}" opacity="0.7"/>
    <!-- Shackle -->
    <path d="M{cx - 12},{cy - 5} L{cx - 12},{cy - 20} Q{cx - 12},{cy - 35} {cx},{cy - 35} Q{cx + 12},{cy - 35} {cx + 12},{cy - 20} L{cx + 12},{cy - 5}"
          fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" opacity="0.7"/>
    <!-- Keyhole -->
    <circle cx="{cx}" cy="{cx * 0 + cy + 7}" r="5" fill="#0f172a"/>
    <rect x="{cx - 2.5}" y="{cy + 7}" width="5" height="8" fill="#0f172a"/>
    """


def visual_cloud(cx: float, cy: float, color: str) -> str:
    """Stacked cloud shapes."""
    return f"""
    <!-- Cloud layers -->
    <ellipse cx="{cx}" cy="{cy + 20}" rx="70" ry="35" fill="{color}" opacity="0.08"/>
    <ellipse cx="{cx - 20}" cy="{cy}" rx="50" ry="28" fill="{color}" opacity="0.15"/>
    <ellipse cx="{cx + 20}" cy="{cy}" rx="50" ry="28" fill="{color}" opacity="0.15"/>
    <ellipse cx="{cx}" cy="{cy - 20}" rx="60" ry="30" fill="{color}" opacity="0.20"/>
    <ellipse cx="{cx}" cy="{cy - 20}" rx="42" ry="22" fill="{color}" opacity="0.25"/>
    <!-- Small accent dots -->
    <circle cx="{cx - 55}" cy="{cy + 40}" r="6" fill="{color}" opacity="0.3"/>
    <circle cx="{cx + 55}" cy="{cy + 40}" r="4" fill="{color}" opacity="0.2"/>
    <circle cx="{cx}" cy="{cy + 55}" r="5" fill="{color}" opacity="0.25"/>
    """


def visual_containers(cx: float, cy: float, color: str) -> str:
    """Stacked container boxes."""
    boxes = []
    colors_alpha = [0.30, 0.20, 0.12]
    for i, alpha in enumerate(colors_alpha):
        bx = cx - 55 + i * 8
        by = cy - 60 + i * 50
        boxes.append(
            f'<rect x="{bx}" y="{by}" width="110" height="42" rx="6" '
            f'fill="{color}" opacity="{alpha}" stroke="{color}" stroke-width="1.5" stroke-opacity="0.4"/>'
        )
        # horizontal line inside
        boxes.append(
            f'<line x1="{bx + 10}" y1="{by + 14}" x2="{bx + 100}" y2="{by + 14}" '
            f'stroke="{color}" stroke-width="1" opacity="0.4"/>'
        )
    return "\n    ".join(boxes)


def visual_network(cx: float, cy: float, color: str) -> str:
    """Neural network nodes."""
    nodes = [
        (cx, cy - 60),
        (cx - 50, cy),
        (cx + 50, cy),
        (cx - 25, cy + 55),
        (cx + 25, cy + 55),
        (cx, cy + 10),
    ]
    lines = []
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j > i:
                lines.append(
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                    f'stroke="{color}" stroke-width="1.5" opacity="0.25"/>'
                )
    circles = [
        f'<circle cx="{x}" cy="{y}" r="10" fill="{color}" opacity="0.35"/>'
        for x, y in nodes
    ]
    return "\n    ".join(lines + circles)


def visual_warning(cx: float, cy: float, color: str) -> str:
    """Warning triangle + crosshair."""
    return f"""
    <!-- Warning triangle -->
    <polygon points="{cx},{cy - 80} {cx - 70},{cy + 40} {cx + 70},{cy + 40}"
             fill="none" stroke="{color}" stroke-width="4" opacity="0.25"/>
    <polygon points="{cx},{cy - 55} {cx - 50},{cy + 30} {cx + 50},{cy + 30}"
             fill="{color}" opacity="0.12"/>
    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="42"
          font-family="monospace" fill="{color}" opacity="0.7">!</text>
    <!-- Crosshair circles -->
    <circle cx="{cx + 80}" cy="{cy - 40}" r="22" fill="none" stroke="{color}" stroke-width="2" opacity="0.3"/>
    <line x1="{cx + 58}" y1="{cy - 40}" x2="{cx + 102}" y2="{cy - 40}" stroke="{color}" stroke-width="1.5" opacity="0.4"/>
    <line x1="{cx + 80}" y1="{cy - 62}" x2="{cx + 80}" y2="{cy - 18}" stroke="{color}" stroke-width="1.5" opacity="0.4"/>
    """


def visual_newspaper(cx: float, cy: float, color: str) -> str:
    """Newspaper icon + calendar grid."""
    lines_svg = []
    # Newspaper rect
    lines_svg.append(
        f'<rect x="{cx - 65}" y="{cy - 75}" width="130" height="100" rx="6" '
        f'fill="{color}" opacity="0.1" stroke="{color}" stroke-width="2" stroke-opacity="0.3"/>'
    )
    for i in range(5):
        y = cy - 55 + i * 17
        w = 100 if i == 0 else (80 if i % 2 == 0 else 90)
        lines_svg.append(
            f'<rect x="{cx - 50}" y="{y}" width="{w}" height="8" rx="3" fill="{color}" opacity="0.3"/>'
        )
    # Calendar grid
    for row in range(3):
        for col in range(4):
            gx = cx - 55 + col * 30
            gy = cy + 40 + row * 24
            lines_svg.append(
                f'<rect x="{gx}" y="{gy}" width="20" height="16" rx="3" '
                f'fill="{color}" opacity="{0.15 + row * 0.08}"/>'
            )
    return "\n    ".join(lines_svg)


def visual_pipeline(cx: float, cy: float, color: str) -> str:
    """CI/CD pipeline arrows."""
    stages = ["Code", "Build", "Test", "Deploy"]
    items = []
    for i, label in enumerate(stages):
        bx = cx - 70 + i * 45
        by = cy - 20
        items.append(
            f'<rect x="{bx}" y="{by}" width="38" height="28" rx="5" '
            f'fill="{color}" opacity="{0.15 + i * 0.05}"/>'
        )
        items.append(
            f'<text x="{bx + 19}" y="{by + 18}" text-anchor="middle" '
            f'font-size="9" font-family="Space Grotesk, Inter, system-ui, sans-serif" '
            f'fill="{color}" opacity="0.8">{label}</text>'
        )
        if i < 3:
            ax = bx + 38
            items.append(
                f'<polygon points="{ax},{by + 8} {ax + 6},{by + 14} {ax},{by + 20}" '
                f'fill="{color}" opacity="0.5"/>'
            )
    # Row 2
    stages2 = ["SAST", "DAST", "SCA"]
    for i, label in enumerate(stages2):
        bx = cx - 55 + i * 55
        by = cy + 30
        items.append(
            f'<rect x="{bx}" y="{by}" width="42" height="28" rx="5" '
            f'fill="{color}" opacity="{0.10 + i * 0.04}"/>'
        )
        items.append(
            f'<text x="{bx + 21}" y="{by + 18}" text-anchor="middle" '
            f'font-size="9" font-family="Space Grotesk, Inter, system-ui, sans-serif" '
            f'fill="{color}" opacity="0.7">{label}</text>'
        )
    return "\n    ".join(items)


def visual_geometric(cx: float, cy: float, color: str) -> str:
    """Abstract hexagon/circle pattern."""
    items = []
    # Hexagon outline
    pts = []
    import math

    for i in range(6):
        angle = math.pi / 180 * (60 * i - 30)
        px = cx + 65 * math.cos(angle)
        py = cy + 65 * math.sin(angle)
        pts.append(f"{px:.1f},{py:.1f}")
    items.append(
        f'<polygon points="{" ".join(pts)}" fill="none" stroke="{color}" '
        f'stroke-width="3" opacity="0.2"/>'
    )
    # Inner hexagon
    pts2 = []
    for i in range(6):
        angle = math.pi / 180 * (60 * i - 30)
        px = cx + 38 * math.cos(angle)
        py = cy + 38 * math.sin(angle)
        pts2.append(f"{px:.1f},{py:.1f}")
    items.append(f'<polygon points="{" ".join(pts2)}" fill="{color}" opacity="0.12"/>')
    # Circles at corners
    for i in range(6):
        angle = math.pi / 180 * (60 * i)
        px = cx + 80 * math.cos(angle)
        py = cy + 80 * math.sin(angle)
        items.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{color}" opacity="0.2"/>'
        )
    return "\n    ".join(items)


VISUAL_FNS = {
    "shield": visual_shield,
    "cloud": visual_cloud,
    "containers": visual_containers,
    "network": visual_network,
    "warning": visual_warning,
    "newspaper": visual_newspaper,
    "pipeline": visual_pipeline,
    "geometric": visual_geometric,
}


# ── Stat cards ───────────────────────────────────────────────────────────────


def render_stat_cards(cards: list, accent: str) -> str:
    """Render 3 stat cards at bottom-left."""
    card_colors = [accent, "#f59e0b", "#10b981"]
    parts = []
    for i, ((val, lbl), color) in enumerate(zip(cards, card_colors)):
        x = 60 + i * 148
        y = 520
        parts.append(f"""
    <rect x="{x}" y="{y}" width="130" height="66" rx="8"
          fill="rgba(255,255,255,0.04)" stroke="{color}" stroke-width="1.5"/>
    <text x="{x + 65}" y="{y + 28}" text-anchor="middle"
          font-family="Space Grotesk, Inter, system-ui, sans-serif"
          font-size="19" font-weight="700" fill="{color}">{val}</text>
    <text x="{x + 65}" y="{y + 48}" text-anchor="middle"
          font-family="Space Grotesk, Inter, system-ui, sans-serif"
          font-size="10" fill="#94a3b8" letter-spacing="1">{lbl}</text>""")
    return "\n".join(parts)


# ── Main SVG builder ─────────────────────────────────────────────────────────


def build_svg(title_raw: str, image_path: str, date_str: str) -> str:
    title_en = clean_title_for_svg(title_raw, image_path)
    theme = detect_topic(title_en, image_path)

    accent = theme["accent"]
    accent2 = theme["accent2"]
    category = theme["category"]
    visual_key = theme["visual"]
    cards = theme["cards"]

    title_lines = split_title_lines(title_en, max_chars=30)

    # Right-side visual center
    visual_cx = 980.0
    visual_cy = 290.0
    visual_fn = VISUAL_FNS.get(visual_key, visual_geometric)
    visual_svg = visual_fn(visual_cx, visual_cy, accent)

    # Title text lines
    title_y_start = 230
    title_line_h = 58
    title_svgs = []
    for i, line in enumerate(title_lines):
        y = title_y_start + i * title_line_h
        title_svgs.append(
            f'<text x="60" y="{y}" '
            f'font-family="Space Grotesk, Inter, system-ui, sans-serif" '
            f'font-size="47" font-weight="700" fill="#ffffff" opacity="0.95">'
            f"{line}</text>"
        )

    # Subtitle from category
    subtitles = {
        "WEEKLY DIGEST": "Weekly Tech and Security Insights",
        "THREAT INTEL": "Threat Intelligence and Attack Analysis",
        "INCIDENT": "Incident Analysis and Post-Mortem",
        "SUPPLY CHAIN": "Supply Chain Attack Analysis",
        "EMAIL SECURITY": "Email Security Configuration Guide",
        "BLOCKCHAIN": "Blockchain and Crypto Security",
        "AUTOMOTIVE": "Automotive Cybersecurity Guide",
        "WEB SECURITY": "Web Application Security Standards",
        "FINOPS": "Cloud Cost Optimization",
        "INFRASTRUCTURE": "Container and Orchestration Security",
        "DEVSECOPS": "DevSecOps Pipeline and Best Practices",
        "AI & ML": "Artificial Intelligence Security Guide",
        "CLOUD": "Cloud Security Architecture and Best Practices",
        "SECURITY": "Security Hardening and Compliance Guide",
        "TECH": "Technology and Security Insights",
    }
    subtitle = subtitles.get(category, "Technical Security Guide")

    title_bottom = title_y_start + len(title_lines) * title_line_h

    stat_cards_svg = render_stat_cards(cards, accent)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{headline}</title>
  <defs>
    <!-- Background gradient -->
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0f1e"/>
      <stop offset="50%" stop-color="#0d1b2a"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <!-- Accent gradient top bar -->
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent2}"/>
    </linearGradient>
    <!-- Radial glow -->
    <radialGradient id="glow" cx="75%" cy="45%" r="45%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <!-- Grid pattern -->
    <pattern id="grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="0.5"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>
  <rect width="1200" height="630" fill="url(#glow)"/>

  <!-- Top accent bar -->
  <rect x="0" y="0" width="1200" height="4" fill="url(#accentGrad)"/>

  <!-- Bottom accent bar -->
  <rect x="0" y="626" width="1200" height="4" fill="url(#accentGrad)"/>

  <!-- Left vertical accent line -->
  <rect x="0" y="4" width="3" height="622" fill="{accent}" opacity="0.4"/>

  <!-- Right-side visual element -->
  <g opacity="0.85">
    {visual_svg}
  </g>

  <!-- Category label -->
  <text x="60" y="100"
        font-family="Space Grotesk, Inter, system-ui, sans-serif"
        font-size="13" font-weight="600" fill="{accent}"
        letter-spacing="3" opacity="0.9">{category}</text>

  <!-- Accent underline under category -->
  <rect x="60" y="108" width="50" height="2" rx="1" fill="{accent}" opacity="0.5"/>

  <!-- Title lines -->
  {"".join(title_svgs)}

  <!-- Accent underline bar -->
  <rect x="60" y="{title_bottom + 8}" width="300" height="4" rx="2" fill="{accent}" opacity="0.7"/>

  <!-- Subtitle -->
  <text x="60" y="{title_bottom + 40}"
        font-family="Space Grotesk, Inter, system-ui, sans-serif"
        font-size="21" fill="#94a3b8" opacity="0.85">{subtitle}</text>

  <!-- Date -->
  <text x="60" y="{title_bottom + 74}"
        font-family="Space Grotesk, Inter, system-ui, sans-serif"
        font-size="16" fill="#64748b">{date_str}</text>

  <!-- Stat cards -->
  {stat_cards_svg}

  <!-- Branding -->
  <text x="1140" y="600"
        font-family="Space Grotesk, Inter, system-ui, sans-serif"
        font-size="15" fill="#475569" text-anchor="end" opacity="0.7">Twodragon Tech Blog</text>

  <!-- Corner decoration dots -->
  <circle cx="1170" cy="30" r="4" fill="{accent}" opacity="0.4"/>
  <circle cx="1185" cy="30" r="2.5" fill="{accent}" opacity="0.25"/>
  <circle cx="1155" cy="30" r="2.5" fill="{accent}" opacity="0.25"/>
</svg>"""
    return svg


# ── Entry point ──────────────────────────────────────────────────────────────

# Mapping: output SVG path (relative) -> (post title, date string)
SVG_ENTRIES = [
    (
        "assets/images/2025-04-29-SKT_Security_Issue_Complete_Response_Guide_IMEI_Check_USIMeSIM_Replace_and_MFA_Importance.svg",
        "SKT Security Issue: IMEI Check, USIM/eSIM Replace and MFA Importance",
        "April 29, 2025",
    ),
    (
        "assets/images/2025-04-30-Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage.svg",
        "Passkey, OTP and Strong Password Management on Public PC",
        "April 30, 2025",
    ),
    (
        "assets/images/2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_and_Finops.svg",
        "Cloud Security Course 7th Batch: AWS Security and FinOps",
        "May 2, 2025",
    ),
    (
        "assets/images/2025-05-09-Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_and_ISMS_Response_Guide.svg",
        "Cloud Security 7th Batch: AWS Vulnerability Inspection and ISMS Response",
        "May 9, 2025",
    ),
    (
        "assets/images/2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_and_ZTNA.svg",
        "Cloud Security 7th Batch: AWS Control Tower and ZTNA",
        "May 16, 2025",
    ),
    (
        "assets/images/2025-05-24-Amazon_Q_Developerand_GitHub_Advanced_Security_Security_and_AWS.svg",
        "Amazon Q Developer and GitHub Advanced Security for AWS",
        "May 24, 2025",
    ),
    (
        "assets/images/2025-05-30-Cloud_Security_Course_7Batch_-_7Week_Docker_and_Kubernetes.svg",
        "Cloud Security 7th Batch: Docker and Kubernetes Understanding",
        "May 30, 2025",
    ),
    (
        "assets/images/2025-05-30-Kubernetes_Minikube_ampamp_K9s_Guide_From_Practical_To.svg",
        "Kubernetes Minikube and K9s Practice Guide",
        "May 30, 2025",
    ),
    (
        "assets/images/2025-06-05-Email_Delivery_Trust_Improve_SendGrid_SPF_DKIM_DMARC_Setup_Complete_Guide.svg",
        "Email Delivery Trust: SendGrid SPF, DKIM, DMARC Setup Guide",
        "June 5, 2025",
    ),
    (
        "assets/images/2025-06-13-Cloud_Security_Course_7Batch_-_9Week_DevSecOps_Integration.svg",
        "Cloud Security 7th Batch: DevSecOps Integration",
        "June 13, 2025",
    ),
    (
        "assets/images/2025-09-17-NPM_ampquotShai-Huludampquot_180_Large-scale_Analysis.svg",
        "NPM Shai-Hulud Worm: 180+ Package Breach Supply Chain Attack Analysis",
        "September 17, 2025",
    ),
    (
        "assets/images/2025-10-02-Karpenter_v153_Node_Integration_Due_to_Large-scale_Incident_Analysis_and_Resolution.svg",
        "Karpenter v1.5.3 Node Integration: Large-scale Incident Analysis and Resolution",
        "October 2, 2025",
    ),
    (
        "assets/images/2025-10-03-AWSin_Database_Access_Gateway_Build_NLB_Security_Group_Complete_Guide.svg",
        "AWS Database Access Gateway: NLB and Security Group Complete Guide",
        "October 3, 2025",
    ),
    (
        "assets/images/2025-10-31-AI_amplsquoamprsquo_amplsquoSecurity_amprsquo_Batch_AI_Security_Guide.svg",
        "Enterprise AI Service Security Guide: AI Secretary and Security Holes",
        "October 31, 2025",
    ),
    (
        "assets/images/2025-11-21-Cloud_Security_8Batch_OT_Guide_DevSecOpsFrom_FinOpsTo_Practical_Talent_Leap.svg",
        "Cloud Security 8th Batch OT Guide: DevSecOps to FinOps Practical Talent Leap",
        "November 21, 2025",
    ),
    (
        "assets/images/2025-11-26-Cloud_Security_8Batch_1Week_Infrastructure_EssenceFrom_Security_FutureTo.svg",
        "Cloud Security 8th Batch Week 1: Infrastructure Essence to Security Future",
        "November 26, 2025",
    ),
    (
        "assets/images/2025-12-24-Cloud_Security_Course_8Batch_5Week_AWS_Control_TowerSCP_Based_Governance_and_Datadog_SIEM_Cloudflare_Security.svg",
        "Cloud Security 8th Batch Week 5: AWS Control Tower SCP Governance and Datadog SIEM",
        "December 24, 2025",
    ),
    (
        "assets/images/2026-01-01-Tesla_FSD_2026_Complete_Guide_Model_Y_Juniper_Security_DevSecOps.svg",
        "Tesla FSD 2026 Complete Guide: Model Y Juniper Security and DevSecOps",
        "January 1, 2026",
    ),
    (
        "assets/images/2026-01-06-DevSecOps_Viewing_Automotive_Security_Complete_Guide.svg",
        "DevSecOps Automotive Security Complete Guide: Connected Car Era",
        "January 6, 2026",
    ),
    (
        "assets/images/2026-01-08-Blockchain_Cryptocurrency_Security_Complete_Guide_DevSecOps_From_Perspective_View_GitHub_Security_Tools_and_Best_Practice.svg",
        "Blockchain Cryptocurrency Security: DevSecOps and GitHub Security Tools",
        "January 8, 2026",
    ),
    (
        "assets/images/2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg",
        "Cloud Security 8th Batch Week 6: AWS WAF CloudFront and GitHub DevSecOps",
        "January 8, 2026",
    ),
    (
        "assets/images/2026-01-10-2026_DevSecOps_Roadmap_Complete_Guide_roadmap.sh_Analysis.svg",
        "2026 DevSecOps Roadmap Complete Guide: roadmap.sh Analysis",
        "January 10, 2026",
    ),
    (
        "assets/images/2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.svg",
        "AI Music Video Generation: DevSecOps Perspective on Generative AI",
        "January 11, 2026",
    ),
    (
        "assets/images/2026-01-14-AWS_Cloud_Security_Complete_Guide_IAM_to_EKS_Practical_Security_Architecture.svg",
        "AWS Cloud Security: IAM to EKS Practical Security Architecture",
        "January 14, 2026",
    ),
    (
        "assets/images/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.svg",
        "Cloud Security 8th Batch Week 7: Docker and Kubernetes Security Practical Guide",
        "January 15, 2026",
    ),
    (
        "assets/images/2026-01-22-AWS_GCP_Cloud_Updates_January_2026.svg",
        "AWS and GCP Cloud Updates January 2026: EC2 G7e X8i Bangkok Region",
        "January 22, 2026",
    ),
    (
        "assets/images/2026-01-22-KARA_Ransomware_Trends_2025_Q3.svg",
        "KARA Ransomware Trends Report 2025 Q3: SK Shieldus EQST Analysis",
        "January 22, 2026",
    ),
    (
        "assets/images/2026-01-22-Security_Vendor_Blog_Weekly_Review.svg",
        "Security Vendor Blog Weekly Review: January 22, 2026",
        "January 22, 2026",
    ),
    (
        "assets/images/2026-01-23-Tech_Security_Weekly_Digest.svg",
        "Tech Security Weekly Digest: Microsoft AitM Phishing, Agentic AI Zero Trust",
        "January 23, 2026",
    ),
    (
        "assets/images/2026-01-24-Tech_Security_Weekly_Digest.svg",
        "Tech Security Weekly Digest: BitLocker FBI, Cloudflare Route Leak, Docker",
        "January 24, 2026",
    ),
    (
        "assets/images/2026-01-25-Tech_Security_Weekly_Digest.svg",
        "Tech Security Weekly Digest: VMware vCenter, Fortinet SSO, Sandworm DynoWiper",
        "January 25, 2026",
    ),
    (
        "assets/images/2026-01-27-Tech_Security_Weekly_Digest_MS_Office_Kimi_Kimwolf_AWS.svg",
        "Tech Security Weekly Digest: MS Office Zero-Day, Kimi K2.5, Kimwolf Botnet",
        "January 27, 2026",
    ),
    (
        "assets/images/2026-01-28-Claude_MD_Security_Guide.svg",
        "CLAUDE.md Security Guide: AI Agent Project Security Design",
        "January 28, 2026",
    ),
    (
        "assets/images/2026-01-28-Tech_Security_Weekly_Digest_MS_Office_Zero_Day_CTEM_Grist_Core_RCE.svg",
        "Tech Security Weekly Digest: MS Office Zero-Day, CTEM, Grist Core RCE",
        "January 28, 2026",
    ),
    (
        "assets/images/2026-01-30-Tech_Security_Weekly_Digest_Ollama_AI_SolarWinds_RCE_Google_IPIDEA.svg",
        "Tech Security Weekly Digest: Ollama AI 175K Exposed, SolarWinds RCE",
        "January 30, 2026",
    ),
    (
        "assets/images/2026-02-04-AI_vs_Claude_Code_AI_Coding_Assistant_Comparison.svg",
        "AI vs Claude Code: Coding Assistant Deep Comparison Security DevSecOps",
        "February 4, 2026",
    ),
    (
        "assets/images/2026-02-04-Tech_Security_Weekly_Digest_AI_Docker_Data_Go.svg",
        "Tech Security Weekly Digest: Docker AI Vulnerability, CVE-2025-11953, RCE",
        "February 4, 2026",
    ),
    (
        "assets/images/2026-02-11-Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI.svg",
        "Tech Security Weekly Digest: Ransomware, CVE-2026-21643, Fortinet Patch",
        "February 11, 2026",
    ),
]


def main():
    generated = 0
    errors = 0

    for rel_path, title, date_str in SVG_ENTRIES:
        out_path = os.path.join(BASE_DIR, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            svg_content = build_svg(title, rel_path, date_str)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            size = os.path.getsize(out_path)
            print(f"[OK]  {os.path.basename(out_path)} ({size:,} bytes)")
            generated += 1
        except Exception as e:
            print(f"[ERR] {os.path.basename(out_path)}: {e}")
            errors += 1

    print(f"\nDone: {generated} generated, {errors} errors.")


if __name__ == "__main__":
    main()
