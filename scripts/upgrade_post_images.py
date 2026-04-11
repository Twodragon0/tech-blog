#!/usr/bin/env python3
"""Batch-upgrade blog post SVG images from basic ~4.7KB template to high-quality
~20KB+ template with visual narratives, gradients, filters, and animations.

Usage:
    python3 scripts/upgrade_post_images.py [--all] [--before DATE] [--post FILENAME] [--dry-run] [--force]
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import frontmatter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
POSTS_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images")
SIZE_THRESHOLD = 15_000  # bytes; skip SVGs already above this unless --force
DEFAULT_BEFORE = "2026-04-02"

# ---------------------------------------------------------------------------
# Theme detection
# ---------------------------------------------------------------------------
THEME_RULES: list[tuple[str, list[str]]] = [
    ("security",    ["security", "cve", "ransomware", "malware", "apt", "threat",
                     "vulnerability", "exploit", "breach", "incident", "pentest",
                     "soc", "siem", "edr", "xdr", "forensic"]),
    ("cloud",       ["cloud", "aws", "gcp", "azure", "s3", "ec2", "lambda",
                     "vpc", "iam", "cloudflare", "vercel", "serverless"]),
    ("kubernetes",  ["kubernetes", "k8s", "docker", "container", "pod", "helm",
                     "minikube", "k9s", "istio", "service-mesh"]),
    ("ai",          ["ai", "ml", "llm", "gpt", "gemini", "claude", "deepseek",
                     "chatgpt", "neural", "model", "transformer", "agent"]),
    ("devops",      ["devops", "devsecops", "ci/cd", "ci-cd", "cicd", "pipeline",
                     "github-actions", "terraform", "ansible", "argo"]),
    ("finops",      ["finops", "cost", "billing", "cost-optimization",
                     "budget", "savings"]),
    ("blockchain",  ["blockchain", "crypto", "bitcoin", "ethereum", "web3",
                     "defi", "nft", "smart-contract"]),
]


def detect_theme(tags: list[str], categories: list[str], title: str) -> str:
    """Return the best-matching theme key based on tags, categories, title."""
    haystack = " ".join(
        str(t).lower() for t in (tags + categories + [title])
    )
    scores: dict[str, int] = {}
    for theme, keywords in THEME_RULES:
        score = sum(1 for kw in keywords if kw in haystack)
        if score:
            scores[theme] = score
    if not scores:
        return "general"
    return max(scores, key=scores.get)


# ---------------------------------------------------------------------------
# Theme color palettes
# ---------------------------------------------------------------------------
PALETTES = {
    "security": {
        "bg1": "#0f172a", "bg2": "#1a0505", "bg3": "#0a0f1e",
        "accent1": "#ef4444", "accent2": "#f97316", "accent3": "#dc2626",
        "node1": "#ef4444", "node2": "#dc2626", "node3": "#f97316",
        "glow": "#dc2626", "text_accent": "#fca5a5",
        "badge_bg": "#7f1d1d", "badge_border": "#dc2626",
        "badge_text": "SECURITY ALERT", "corner": "#dc2626",
    },
    "cloud": {
        "bg1": "#0a1628", "bg2": "#0d1525", "bg3": "#081020",
        "accent1": "#06b6d4", "accent2": "#3b82f6", "accent3": "#0ea5e9",
        "node1": "#06b6d4", "node2": "#3b82f6", "node3": "#22d3ee",
        "glow": "#06b6d4", "text_accent": "#67e8f9",
        "badge_bg": "#0c4a6e", "badge_border": "#0ea5e9",
        "badge_text": "CLOUD INFRA", "corner": "#06b6d4",
    },
    "kubernetes": {
        "bg1": "#0f0a2a", "bg2": "#0d1525", "bg3": "#0a0f2e",
        "accent1": "#818cf8", "accent2": "#06b6d4", "accent3": "#6366f1",
        "node1": "#818cf8", "node2": "#06b6d4", "node3": "#a78bfa",
        "glow": "#6366f1", "text_accent": "#c4b5fd",
        "badge_bg": "#312e81", "badge_border": "#6366f1",
        "badge_text": "K8S / CONTAINER", "corner": "#818cf8",
    },
    "ai": {
        "bg1": "#0f172a", "bg2": "#0a1a0a", "bg3": "#0d0f25",
        "accent1": "#a855f7", "accent2": "#22c55e", "accent3": "#8b5cf6",
        "node1": "#a855f7", "node2": "#22c55e", "node3": "#c084fc",
        "glow": "#8b5cf6", "text_accent": "#d8b4fe",
        "badge_bg": "#3b0764", "badge_border": "#a855f7",
        "badge_text": "AI / ML", "corner": "#a855f7",
    },
    "devops": {
        "bg1": "#0a1628", "bg2": "#0a1a10", "bg3": "#081020",
        "accent1": "#06b6d4", "accent2": "#22c55e", "accent3": "#0ea5e9",
        "node1": "#06b6d4", "node2": "#22c55e", "node3": "#4ade80",
        "glow": "#06b6d4", "text_accent": "#67e8f9",
        "badge_bg": "#064e3b", "badge_border": "#22c55e",
        "badge_text": "DEVOPS PIPELINE", "corner": "#22c55e",
    },
    "finops": {
        "bg1": "#1a1505", "bg2": "#0a1a10", "bg3": "#0f0f05",
        "accent1": "#f59e0b", "accent2": "#22c55e", "accent3": "#eab308",
        "node1": "#f59e0b", "node2": "#22c55e", "node3": "#fbbf24",
        "glow": "#f59e0b", "text_accent": "#fde68a",
        "badge_bg": "#713f12", "badge_border": "#f59e0b",
        "badge_text": "FINOPS", "corner": "#f59e0b",
    },
    "blockchain": {
        "bg1": "#1a1005", "bg2": "#150a25", "bg3": "#0f0f1a",
        "accent1": "#f59e0b", "accent2": "#a855f7", "accent3": "#eab308",
        "node1": "#f59e0b", "node2": "#a855f7", "node3": "#fbbf24",
        "glow": "#f59e0b", "text_accent": "#fde68a",
        "badge_bg": "#713f12", "badge_border": "#f59e0b",
        "badge_text": "BLOCKCHAIN", "corner": "#f59e0b",
    },
    "general": {
        "bg1": "#0a1628", "bg2": "#0d1525", "bg3": "#081020",
        "accent1": "#06b6d4", "accent2": "#3b82f6", "accent3": "#0ea5e9",
        "node1": "#06b6d4", "node2": "#3b82f6", "node3": "#22d3ee",
        "glow": "#06b6d4", "text_accent": "#67e8f9",
        "badge_bg": "#0c4a6e", "badge_border": "#0ea5e9",
        "badge_text": "TECH BLOG", "corner": "#06b6d4",
    },
}


# ---------------------------------------------------------------------------
# Title / tag helpers
# ---------------------------------------------------------------------------
TAG_ENGLISH_MAP = {
    "보안": "Security", "클라우드": "Cloud", "쿠버네티스": "Kubernetes",
    "도커": "Docker", "인공지능": "AI", "블록체인": "Blockchain",
}


def english_tags(tags: list, limit: int = 4) -> list[str]:
    """Return up to *limit* English tag labels, preferring specific tags."""
    generic = {"security-weekly", "weekly-digest", "daily-digest",
               "tech-newsletter", "2025", "2026", "2024"}
    specific = []
    fallback = []
    for t in tags:
        t_str = str(t).strip()
        if t_str.lower() in generic:
            fallback.append(t_str)
            continue
        # Map Korean if needed
        mapped = TAG_ENGLISH_MAP.get(t_str, t_str)
        # Clean hyphens for display
        label = mapped.replace("-", " ").title()
        if len(label) > 18:
            label = label[:17].rstrip() + "."
        specific.append(label)
    result = specific[:limit]
    while len(result) < limit and fallback:
        t_str = fallback.pop(0)
        label = t_str.replace("-", " ").title()
        if len(label) > 18:
            label = label[:17].rstrip() + "."
        result.append(label)
    return result[:limit]


def split_title(title: str, max_chars: int = 22) -> list[str]:
    """Split a title into 2-3 lines, each at most max_chars."""
    # Remove Korean, keep English and common chars
    en = re.sub(r"[^\x00-\x7F]+", " ", title)
    # Clean up artifacts from Korean removal
    en = re.sub(r"\s+[-:]+\s+", " ", en)       # isolated colons/hyphens
    en = re.sub(r"(?<!\w)\d{1,2}(?!\w)", "", en)  # isolated 1-2 digit numbers
    en = re.sub(r"\s+", " ", en).strip()
    en = re.sub(r"^[^a-zA-Z0-9]+", "", en).strip()  # leading punctuation
    en = en.replace("&", "&amp;")  # XML-escape ampersands for SVG
    if not en:
        en = "Tech Blog Post"
    words = en.split()
    lines: list[str] = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip() if current else w
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
        if len(lines) >= 2:
            # Put remainder on last line
            remaining = " ".join(words[words.index(w):])
            if remaining != current:
                current = remaining
            break
    if current:
        lines.append(current)
    if not lines:
        lines = ["Tech Blog Post"]
    return lines[:3]


def format_date(date_val) -> str:
    """Format date for SVG badge."""
    if isinstance(date_val, datetime):
        return date_val.strftime("%B %d, %Y").upper()
    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_val.strip()[:19], fmt[:len(date_val.strip()[:19])]).strftime("%B %d, %Y").upper()
            except ValueError:
                continue
    # Fallback: extract from filename-like string
    return str(date_val)[:10].upper()


def uid(filepath: str) -> str:
    """Short unique prefix for SVG IDs to avoid cross-file conflicts."""
    h = hashlib.md5(filepath.encode()).hexdigest()[:6]
    return f"u{h}"


# ---------------------------------------------------------------------------
# Common decorative elements (~10KB of shared visual content)
# ---------------------------------------------------------------------------

def _common_decorations(p: dict, u: str, tag_labels: list[str]) -> str:
    """Generate shared decorative elements for all themes to reach 18-25KB."""
    labels = tag_labels[:3] if tag_labels else ["Tech"]
    return f"""
    <!-- ===== COMMON DECORATIONS ===== -->

    <!-- Hex grid overlay (right area) -->
    <defs>
      <pattern id="{u}hex" x="0" y="0" width="24" height="28" patternUnits="userSpaceOnUse">
        <polygon points="12,0 24,7 24,21 12,28 0,21 0,7"
                 fill="none" stroke="{p['accent1']}" stroke-width="0.4" opacity="0.15"/>
      </pattern>
    </defs>
    <rect x="380" y="40" width="780" height="550" fill="url(#{u}hex)" opacity="0.35"/>

    <!-- Orbital rings -->
    <circle cx="720" cy="300" r="220" fill="none" stroke="{p['accent1']}" stroke-width="0.6"
            stroke-dasharray="5 8" opacity="0.2"/>
    <circle cx="720" cy="300" r="180" fill="none" stroke="{p['accent3']}" stroke-width="0.5"
            stroke-dasharray="3 6" opacity="0.15"/>
    <circle cx="720" cy="300" r="260" fill="none" stroke="{p['accent2']}" stroke-width="0.4"
            stroke-dasharray="8 12" opacity="0.1"/>

    <!-- Radial grid lines -->
    <line x1="720" y1="80" x2="720" y2="520" stroke="{p['accent1']}" stroke-width="0.3" opacity="0.1"/>
    <line x1="460" y1="300" x2="980" y2="300" stroke="{p['accent1']}" stroke-width="0.3" opacity="0.1"/>
    <line x1="535" y1="120" x2="905" y2="480" stroke="{p['accent2']}" stroke-width="0.3" opacity="0.08"/>
    <line x1="905" y1="120" x2="535" y2="480" stroke="{p['accent2']}" stroke-width="0.3" opacity="0.08"/>

    <!-- Top-right data panel -->
    <rect x="960" y="50" width="190" height="110" rx="6" fill="{p['bg1']}" stroke="{p['accent1']}"
          stroke-width="1" opacity="0.7"/>
    <rect x="960" y="50" width="190" height="22" rx="6" fill="{p['accent1']}" opacity="0.12"/>
    <text x="975" y="66" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent1']}" font-weight="bold" letter-spacing="1">STATUS</text>
    <circle cx="1135" cy="61" r="4" fill="#22c55e" opacity="0.7"
            style="animation: {u}pulse 2s ease-in-out infinite"/>
    <text x="975" y="90" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" opacity="0.7">INTEGRITY</text>
    <rect x="1050" y="82" width="88" height="6" rx="3" fill="{p['accent1']}" opacity="0.15"/>
    <rect x="1050" y="82" width="62" height="6" rx="3" fill="{p['accent1']}" opacity="0.5"/>
    <text x="975" y="108" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" opacity="0.7">COVERAGE</text>
    <rect x="1050" y="100" width="88" height="6" rx="3" fill="{p['accent2']}" opacity="0.15"/>
    <rect x="1050" y="100" width="75" height="6" rx="3" fill="{p['accent2']}" opacity="0.5"/>
    <text x="975" y="126" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" opacity="0.7">UPTIME</text>
    <rect x="1050" y="118" width="88" height="6" rx="3" fill="#22c55e" opacity="0.15"/>
    <rect x="1050" y="118" width="82" height="6" rx="3" fill="#22c55e" opacity="0.45"/>
    <text x="975" y="148" font-family="Courier New, monospace" font-size="7"
          fill="#64748b" opacity="0.6">SYS.OK | v2.1.4</text>

    <!-- Bottom-right metrics panel -->
    <rect x="920" y="480" width="220" height="100" rx="6" fill="{p['bg1']}" stroke="{p['accent2']}"
          stroke-width="1" opacity="0.65"/>
    <text x="935" y="500" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent2']}" font-weight="bold" letter-spacing="1">METRICS</text>
    <line x1="920" y1="506" x2="1140" y2="506" stroke="{p['accent2']}" stroke-width="0.5" opacity="0.3"/>
    <!-- Mini bar chart -->
    <rect x="940" y="545" width="14" height="28" rx="2" fill="{p['accent1']}" opacity="0.3"/>
    <rect x="940" y="555" width="14" height="18" rx="2" fill="{p['accent1']}" opacity="0.6"/>
    <rect x="960" y="535" width="14" height="38" rx="2" fill="{p['accent2']}" opacity="0.3"/>
    <rect x="960" y="550" width="14" height="23" rx="2" fill="{p['accent2']}" opacity="0.6"/>
    <rect x="980" y="540" width="14" height="33" rx="2" fill="{p['accent1']}" opacity="0.3"/>
    <rect x="980" y="548" width="14" height="25" rx="2" fill="{p['accent1']}" opacity="0.5"/>
    <rect x="1000" y="530" width="14" height="43" rx="2" fill="{p['accent3']}" opacity="0.3"/>
    <rect x="1000" y="545" width="14" height="28" rx="2" fill="{p['accent3']}" opacity="0.6"/>
    <rect x="1020" y="538" width="14" height="35" rx="2" fill="{p['accent2']}" opacity="0.3"/>
    <rect x="1020" y="552" width="14" height="21" rx="2" fill="{p['accent2']}" opacity="0.5"/>
    <rect x="1040" y="525" width="14" height="48" rx="2" fill="{p['accent1']}" opacity="0.3"/>
    <rect x="1040" y="540" width="14" height="33" rx="2" fill="{p['accent1']}" opacity="0.6"
          style="animation: {u}glimmer 3s ease-in-out infinite"/>
    <!-- Metric labels -->
    <!-- Circuit traces (decorative) -->
    <polyline points="400,100 430,100 430,140 480,140" fill="none"
              stroke="{p['accent1']}" stroke-width="0.8" opacity="0.2"/>
    <circle cx="480" cy="140" r="3" fill="{p['accent1']}" opacity="0.3"/>
    <polyline points="400,160 420,160 420,200 460,200 460,180" fill="none"
              stroke="{p['accent2']}" stroke-width="0.8" opacity="0.15"/>
    <circle cx="460" cy="180" r="2.5" fill="{p['accent2']}" opacity="0.25"/>
    <polyline points="1100,200 1130,200 1130,260 1100,260 1100,300" fill="none"
              stroke="{p['accent3']}" stroke-width="0.8" opacity="0.18"/>
    <circle cx="1100" cy="300" r="3" fill="{p['accent3']}" opacity="0.3"/>
    <polyline points="1120,350 1150,350 1150,420 1120,420" fill="none"
              stroke="{p['accent1']}" stroke-width="0.8" opacity="0.15"/>
    <circle cx="1120" cy="420" r="2.5" fill="{p['accent1']}" opacity="0.25"/>
    <polyline points="450,500 480,500 480,520 520,520" fill="none"
              stroke="{p['accent2']}" stroke-width="0.7" opacity="0.15"/>
    <circle cx="520" cy="520" r="2" fill="{p['accent2']}" opacity="0.2"/>
    <polyline points="1060,460 1090,460 1090,440 1120,440" fill="none"
              stroke="{p['accent1']}" stroke-width="0.7" opacity="0.15"/>

    <!-- Left panel data readout -->
    <rect x="40" y="430" width="280" height="80" rx="6" fill="{p['bg2']}" stroke="{p['accent1']}"
          stroke-width="1" opacity="0.6"/>
    <rect x="40" y="430" width="4" height="80" rx="2" fill="{p['accent1']}"/>
    <text x="56" y="466" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" opacity="0.6">{labels[0] if labels else 'DATA'}</text>
    <rect x="56" y="474" width="200" height="5" rx="2" fill="{p['accent1']}" opacity="0.12"/>
    <rect x="56" y="474" width="145" height="5" rx="2" fill="{p['accent1']}" opacity="0.45"/>
    <text x="56" y="492" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" opacity="0.6">{labels[1] if len(labels) > 1 else 'SCAN'}</text>
    <rect x="56" y="496" width="200" height="5" rx="2" fill="{p['accent2']}" opacity="0.12"/>
    <rect x="56" y="496" width="170" height="5" rx="2" fill="{p['accent2']}" opacity="0.45"/>

    <!-- Scattered micro-nodes -->
    <circle cx="420" cy="80" r="5" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.5"/>
    <circle cx="420" cy="80" r="2" fill="{p['accent1']}" opacity="0.4"/>
    <circle cx="1150" cy="140" r="5" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1" opacity="0.4"/>
    <circle cx="1150" cy="140" r="2" fill="{p['accent2']}" opacity="0.3"/>
    <circle cx="480" cy="560" r="4" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1" opacity="0.4"/>
    <circle cx="480" cy="560" r="1.5" fill="{p['accent3']}" opacity="0.3"/>
    <circle cx="1080" cy="570" r="4" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.35"/>
    <circle cx="1080" cy="570" r="1.5" fill="{p['accent1']}" opacity="0.25"/>

    <!-- Scanning beam effect -->
    <line x1="380" y1="300" x2="1160" y2="300" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.06"/>
    <rect x="380" y="298" width="40" height="4" rx="2" fill="{p['accent1']}" opacity="0.15">
      <animate attributeName="x" values="380;1120;380" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.15;0.3;0.15" dur="8s" repeatCount="indefinite"/>
    </rect>

    <!-- Animated dashed orbit arc -->
    <path d="M 500 100 A 280 250 0 0 1 940 100" fill="none" stroke="{p['accent1']}"
          stroke-width="1" stroke-dasharray="6 8" opacity="0.15"
          style="animation: {u}dash 4s linear infinite"/>
    <path d="M 940 500 A 280 250 0 0 1 500 500" fill="none" stroke="{p['accent2']}"
          stroke-width="0.8" stroke-dasharray="4 6" opacity="0.12"
          style="animation: {u}dash 5s linear infinite"/>

    <!-- Corner decorative brackets -->
    <polyline points="390,55 390,45 400,45" fill="none" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.4"/>
    <polyline points="1150,45 1160,45 1160,55" fill="none" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.4"/>
    <polyline points="390,575 390,585 400,585" fill="none" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.35"/>
    <polyline points="1150,585 1160,585 1160,575" fill="none" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.35"/>

    <!-- Crosshair on center -->
    <circle cx="720" cy="300" r="8" fill="none" stroke="{p['accent1']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="720" y1="288" x2="720" y2="294" stroke="{p['accent1']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="720" y1="306" x2="720" y2="312" stroke="{p['accent1']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="708" y1="300" x2="714" y2="300" stroke="{p['accent1']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="726" y1="300" x2="732" y2="300" stroke="{p['accent1']}" stroke-width="0.6" opacity="0.2"/>

    <!-- Horizontal data lines -->
    <line x1="400" y1="48" x2="470" y2="48" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.15"/>
    <line x1="475" y1="48" x2="500" y2="48" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.1"/>
    <line x1="400" y1="585" x2="450" y2="585" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.12"/>
    <line x1="455" y1="585" x2="490" y2="585" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.08"/>
    <line x1="1060" y1="48" x2="1120" y2="48" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.12"/>
    <line x1="1060" y1="585" x2="1100" y2="585" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.1"/>

    <!-- Animated pulse dot (center) -->
    <circle cx="720" cy="300" r="4" fill="{p['accent1']}" opacity="0.3">
      <animate attributeName="r" values="4;8;4" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.3;0.1;0.3" dur="3s" repeatCount="indefinite"/>
    </circle>

    <!-- Perspective vanishing lines (tunnel effect) -->
    <line x1="720" y1="315" x2="400" y2="50" stroke="{p['accent1']}" stroke-width="0.4" opacity="0.08"/>
    <line x1="720" y1="315" x2="1150" y2="50" stroke="{p['accent1']}" stroke-width="0.4" opacity="0.08"/>
    <line x1="720" y1="315" x2="400" y2="580" stroke="{p['accent2']}" stroke-width="0.4" opacity="0.06"/>
    <line x1="720" y1="315" x2="1150" y2="580" stroke="{p['accent2']}" stroke-width="0.4" opacity="0.06"/>
    <line x1="720" y1="315" x2="400" y2="315" stroke="{p['accent1']}" stroke-width="0.3" opacity="0.07"/>
    <line x1="720" y1="315" x2="1150" y2="315" stroke="{p['accent1']}" stroke-width="0.3" opacity="0.07"/>
    <line x1="720" y1="315" x2="500" y2="50" stroke="{p['accent3']}" stroke-width="0.3" opacity="0.06"/>
    <line x1="720" y1="315" x2="940" y2="580" stroke="{p['accent3']}" stroke-width="0.3" opacity="0.06"/>

    <!-- Breach crack line (jagged polyline across y=315) -->
    <polyline points="400,315 435,310 460,320 495,308 530,318 565,306 600,322 640,310 680,316 720,304 760,320 800,308 840,318 880,306 920,322 960,310 1000,318 1040,308 1080,316 1120,310 1155,315"
              fill="none" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.35"
              filter="url(#{u}fxRed)" class="{u}crack"/>
    <polyline points="400,315 435,312 460,318 495,310 530,316 565,308 600,320 640,312 680,314 720,306 760,318 800,310 840,316 880,308 920,320 960,312 1000,316 1040,310 1080,314 1120,312 1155,315"
              fill="none" stroke="{p['accent3']}" stroke-width="0.8" opacity="0.2"/>

    <!-- Floating particles with animation classes -->
    <circle cx="480" cy="120" r="2.5" fill="{p['accent1']}" opacity="0.7" class="{u}fa"/>
    <circle cx="620" cy="480" r="2" fill="{p['accent2']}" opacity="0.6" class="{u}fb"/>
    <circle cx="900" cy="100" r="3" fill="{p['accent3']}" opacity="0.5" class="{u}fc"/>
    <circle cx="1050" cy="350" r="2" fill="{p['accent1']}" opacity="0.6" class="{u}fa"/>
    <circle cx="550" cy="550" r="2.5" fill="{p['accent2']}" opacity="0.5" class="{u}fb"/>
    <circle cx="850" cy="520" r="1.8" fill="{p['accent1']}" opacity="0.55" class="{u}fc"/>
    <circle cx="750" cy="80" r="2.2" fill="{p['accent3']}" opacity="0.45" class="{u}fa"/>

    <!-- Additional data panel (mid-right) -->
    <rect x="960" y="180" width="190" height="76" rx="6" fill="{p['bg1']}" stroke="{p['accent3']}"
          stroke-width="0.8" opacity="0.55"/>
    <rect x="960" y="180" width="190" height="18" rx="6" fill="{p['accent3']}" opacity="0.10"/>
    <text x="975" y="193" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent3']}" font-weight="bold" letter-spacing="1">TELEMETRY</text>
    <text x="975" y="214" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" opacity="0.6">LATENCY</text>
    <rect x="1050" y="207" width="88" height="5" rx="2" fill="{p['accent3']}" opacity="0.12"/>
    <rect x="1050" y="207" width="55" height="5" rx="2" fill="{p['accent3']}" opacity="0.45"/>
    <text x="975" y="230" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" opacity="0.6">THROUGHPUT</text>
    <rect x="1050" y="223" width="88" height="5" rx="2" fill="{p['accent1']}" opacity="0.12"/>
    <rect x="1050" y="223" width="72" height="5" rx="2" fill="{p['accent1']}" opacity="0.4"/>
    <text x="975" y="246" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" opacity="0.6">ERROR RATE</text>
    <rect x="1050" y="239" width="88" height="5" rx="2" fill="{p['accent1']}" opacity="0.12"/>
    <rect x="1050" y="239" width="18" height="5" rx="2" fill="#22c55e" opacity="0.5"/>
    <text x="1120" y="246" font-family="Courier New, monospace" font-size="6"
          fill="#22c55e" opacity="0.5">LOW</text>

    <!-- Timestamp watermark -->
    <text x="1160" y="598" font-family="Courier New, monospace" font-size="7"
          fill="#1e293b" text-anchor="end" opacity="0.5">2TWODRAGON // DIGEST</text>
"""


# ---------------------------------------------------------------------------
# Scene renderers (right-side area, x=380..1160, y=40..590)
# ---------------------------------------------------------------------------

def _scene_security(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: Security Breach -->
    <!-- Shield (broken) -->
    <g filter="url(#{u}glow)">
      <circle cx="600" cy="200" r="55" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2.5" opacity="0.9"/>
      <circle cx="600" cy="200" r="55" fill="{p['glow']}" opacity="0.08"/>
    </g>
    <path d="M600 165 L625 175 L625 200 Q625 220 600 230 Q575 220 575 200 L575 175 Z"
          fill="none" stroke="{p['accent1']}" stroke-width="2"/>
    <line x1="590" y1="180" x2="610" y2="220" stroke="{p['accent2']}" stroke-width="2.5" opacity="0.9"/>
    <line x1="610" y1="180" x2="590" y2="220" stroke="{p['accent2']}" stroke-width="2.5" opacity="0.9"/>

    <!-- Threat node 1 - skull warning -->
    <g filter="url(#{u}glow)">
      <circle cx="800" cy="140" r="38" fill="{p['bg2']}" stroke="{p['accent1']}" stroke-width="2"/>
      <circle cx="800" cy="140" r="38" fill="{p['glow']}" opacity="0.1"/>
    </g>
    <polygon points="800,118 815,142 808,148 800,155 792,148 785,142"
             fill="none" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="800" y="140" font-family="Courier New, monospace" font-size="14"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">!</text>
    <text x="800" y="170" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.8">THREAT</text>

    <!-- Threat node 2 - lock -->
    <g filter="url(#{u}glow)">
      <circle cx="950" cy="280" r="35" fill="{p['bg2']}" stroke="{p['accent3']}" stroke-width="2"/>
    </g>
    <rect x="937" y="278" width="26" height="20" rx="3" fill="none" stroke="{p['accent2']}" stroke-width="1.5"/>
    <path d="M943 278 L943 270 Q943 262 950 262 Q957 262 957 270 L957 278"
          fill="none" stroke="{p['accent2']}" stroke-width="1.5"/>
    <circle cx="950" cy="289" r="2.5" fill="{p['accent2']}"/>
    <text x="950" y="308" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.8">LOCK</text>

    <!-- Threat node 3 - exploit -->
    <g filter="url(#{u}glow)">
      <circle cx="750" cy="430" r="35" fill="{p['bg2']}" stroke="{p['accent1']}" stroke-width="2"/>
    </g>
    <polygon points="750,412 765,440 735,440" fill="none" stroke="{p['accent1']}" stroke-width="1.8"/>
    <text x="750" y="434" font-family="Courier New, monospace" font-size="12"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">!</text>
    <text x="750" y="460" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.8">EXPLOIT</text>

    <!-- Connection lines -->
    <line x1="650" y1="190" x2="765" y2="148" stroke="{p['accent1']}" stroke-width="1.5"
          opacity="0.4" stroke-dasharray="4 4" style="animation: {u}dash 2s linear infinite"/>
    <line x1="650" y1="210" x2="918" y2="272" stroke="{p['accent3']}" stroke-width="1.5"
          opacity="0.35" stroke-dasharray="4 4"/>
    <line x1="620" y1="248" x2="722" y2="418" stroke="{p['accent1']}" stroke-width="1.5"
          opacity="0.3" stroke-dasharray="4 4"/>
    <path d="M 800 175 Q 870 220 950 248" fill="none" stroke="{p['accent1']}"
          stroke-width="1" opacity="0.25" stroke-dasharray="3 5"/>
    <path d="M 920 305 Q 850 370 780 420" fill="none" stroke="{p['accent3']}"
          stroke-width="1" opacity="0.25" stroke-dasharray="3 5"/>

    <!-- Alert badge -->
    <rect x="560" y="340" width="110" height="30" rx="5" fill="{p['badge_bg']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="615" y="360" font-family="Courier New, monospace" font-size="11"
          fill="{p['text_accent']}" text-anchor="middle" font-weight="bold" letter-spacing="1">CRITICAL</text>

    <!-- Pulsing ring -->
    <circle cx="600" cy="200" r="70" fill="none" stroke="{p['accent1']}" stroke-width="1"
            opacity="0.3" style="animation: {u}pulse 3s ease-in-out infinite"/>
    <circle cx="800" cy="140" r="50" fill="none" stroke="{p['accent1']}" stroke-width="0.8"
            opacity="0.2" style="animation: {u}pulse 4s ease-in-out infinite"/>

    <!-- Cracked shield detail -->
    <path d="M600 170 L600 230" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.6" stroke-dasharray="3 2"/>
    <path d="M585 195 L615 205" stroke="{p['accent2']}" stroke-width="1" opacity="0.5"/>

    <!-- Broken padlock -->
    <g transform="translate(680,430)">
      <rect x="-12" y="0" width="24" height="18" rx="3" fill="none" stroke="{p['accent1']}" stroke-width="1.5"/>
      <path d="M-6 0 L-6 -8 Q-6 -16 0 -16 Q6 -16 6 -8 L6 -4" fill="none" stroke="{p['accent1']}" stroke-width="1.5"/>
      <line x1="6" y1="-8" x2="10" y2="-12" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.8"/>
      <circle cx="0" cy="9" r="2" fill="{p['accent1']}" opacity="0.7"/>
    </g>
    <text x="680" y="460" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">BREACH</text>

    <!-- Attack flow arrows with dashed lines -->
    <path d="M 830 160 Q 870 180 880 220" fill="none" stroke="{p['accent1']}"
          stroke-width="1.2" opacity="0.35" stroke-dasharray="5 3" style="animation: {u}dash 2.5s linear infinite"/>
    <polygon points="878,215 885,222 875,220" fill="{p['accent1']}" opacity="0.35"/>
    <path d="M 780 445 Q 830 460 870 440" fill="none" stroke="{p['accent3']}"
          stroke-width="1" opacity="0.3" stroke-dasharray="4 3"/>
    <polygon points="867,443 875,438 870,447" fill="{p['accent3']}" opacity="0.3"/>

    <!-- Skull warning icon -->
    <g transform="translate(520,440)" filter="url(#{u}fxRed)">
      <circle cx="0" cy="0" r="18" fill="{p['bg2']}" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.8"/>
      <circle cx="-5" cy="-3" r="2.5" fill="{p['accent1']}" opacity="0.7"/>
      <circle cx="5" cy="-3" r="2.5" fill="{p['accent1']}" opacity="0.7"/>
      <path d="M-4 6 L-2 4 L0 6 L2 4 L4 6" fill="none" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    </g>
    <text x="520" y="468" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">MALWARE</text>

    <!-- ALERT badge -->
    <rect x="850" y="390" width="80" height="24" rx="4" fill="{p['accent1']}" opacity="0.15"
          stroke="{p['accent1']}" stroke-width="1.2"/>
    <text x="890" y="406" font-family="Courier New, monospace" font-size="10"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold" class="{u}blink">ALERT</text>

    <!-- CVE reference label -->
    <rect x="560" y="260" width="100" height="18" rx="3" fill="{p['bg2']}" stroke="{p['accent3']}" stroke-width="0.8" opacity="0.6"/>
    <text x="610" y="273" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent3']}" text-anchor="middle" opacity="0.7">CVE-2025-XXXX</text>

    <!-- Ambient glow -->
    <ellipse cx="750" cy="280" rx="250" ry="200" fill="{p['glow']}" opacity="0.04"/>
"""


def _scene_cloud(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: Cloud Infrastructure -->
    <!-- Cloud shape -->
    <ellipse cx="700" cy="180" rx="120" ry="55" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.7"/>
    <ellipse cx="665" cy="200" rx="80" ry="42" fill="{p['accent1']}" opacity="0.05"/>
    <ellipse cx="740" cy="205" rx="70" ry="38" fill="{p['accent2']}" opacity="0.04"/>
    <text x="700" y="185" font-family="Courier New, monospace" font-size="10"
          fill="{p['text_accent']}" text-anchor="middle" font-weight="bold">CLOUD</text>

    <!-- Server rack -->
    <rect x="880" y="220" width="90" height="120" rx="6" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.8"/>
    <line x1="880" y1="260" x2="970" y2="260" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.5"/>
    <line x1="880" y1="300" x2="970" y2="300" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.5"/>
    <circle cx="955" cy="240" r="4" fill="#22c55e" opacity="0.6" style="animation: {u}pulse 2s ease-in-out infinite"/>
    <circle cx="955" cy="280" r="4" fill="#22c55e" opacity="0.4"/>
    <circle cx="955" cy="320" r="4" fill="{p['accent2']}" opacity="0.5"/>
    <text x="925" y="360" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">SERVER</text>

    <!-- Region nodes -->
    <g filter="url(#{u}glow)">
      <circle cx="580" cy="340" r="32" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2"/>
    </g>
    <text x="580" y="338" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle">REGION</text>
    <text x="580" y="350" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">us-east-1</text>

    <g filter="url(#{u}glow)">
      <circle cx="800" cy="420" r="32" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="2"/>
    </g>
    <text x="800" y="418" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent2']}" text-anchor="middle">REGION</text>
    <text x="800" y="430" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">ap-ne-2</text>

    <!-- VPC box -->
    <rect x="620" y="400" width="120" height="70" rx="4" fill="none"
          stroke="{p['accent1']}" stroke-width="1" stroke-dasharray="5 3" opacity="0.4"/>
    <text x="680" y="418" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.6">VPC</text>

    <!-- Data flow lines -->
    <line x1="700" y1="235" x2="700" y2="310" stroke="{p['accent1']}" stroke-width="1.5"
          opacity="0.4" stroke-dasharray="4 4" style="animation: {u}dash 2s linear infinite"/>
    <line x1="750" y1="220" x2="880" y2="250" stroke="{p['accent2']}" stroke-width="1.5"
          opacity="0.35" stroke-dasharray="4 4"/>
    <line x1="610" y1="340" x2="770" y2="415" stroke="{p['accent1']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="3 5"/>
    <path d="M 925 340 Q 900 390 830 420" fill="none" stroke="{p['accent2']}"
          stroke-width="1" opacity="0.25" stroke-dasharray="3 5"/>

    <!-- Server rack blinking LEDs -->
    <circle cx="895" cy="240" r="3" fill="#ef4444" opacity="0.5" class="{u}blink"/>
    <circle cx="895" cy="280" r="3" fill="{p['accent1']}" opacity="0.4" class="{u}blink"/>
    <circle cx="895" cy="320" r="3" fill="#f59e0b" opacity="0.45"/>
    <rect x="892" y="234" width="14" height="4" rx="1" fill="{p['accent2']}" opacity="0.2"/>
    <rect x="892" y="274" width="14" height="4" rx="1" fill="{p['accent2']}" opacity="0.2"/>
    <rect x="892" y="314" width="14" height="4" rx="1" fill="{p['accent2']}" opacity="0.2"/>

    <!-- VPC boundary box (larger) -->
    <rect x="450" y="260" width="280" height="220" rx="8" fill="none"
          stroke="{p['accent1']}" stroke-width="1.2" stroke-dasharray="8 4" opacity="0.25"/>
    <text x="460" y="278" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" opacity="0.5" font-weight="bold">VPC-BOUNDARY</text>

    <!-- Data flow arrows -->
    <path d="M 770 190 Q 820 210 880 225" fill="none" stroke="{p['accent2']}"
          stroke-width="1.5" opacity="0.4" stroke-dasharray="5 3" style="animation: {u}dash 2s linear infinite"/>
    <polygon points="876,222 885,226 878,230" fill="{p['accent2']}" opacity="0.4"/>
    <path d="M 600 345 Q 650 380 700 400" fill="none" stroke="{p['accent1']}"
          stroke-width="1" opacity="0.3" stroke-dasharray="4 3"/>
    <polygon points="696,397 705,402 698,406" fill="{p['accent1']}" opacity="0.3"/>

    <!-- Region label badges -->
    <rect x="480" y="300" width="72" height="20" rx="3" fill="{p['badge_bg']}" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.6"/>
    <text x="516" y="314" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.8">us-west-2</text>
    <rect x="830" y="450" width="72" height="20" rx="3" fill="{p['badge_bg']}" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.6"/>
    <text x="866" y="464" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent2']}" text-anchor="middle" opacity="0.8">eu-west-1</text>

    <!-- Load balancer icon -->
    <g transform="translate(700,320)" filter="url(#{u}fxGlow)">
      <circle cx="0" cy="0" r="22" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
      <line x1="-8" y1="-5" x2="8" y2="-5" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.7"/>
      <line x1="-8" y1="0" x2="8" y2="0" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.7"/>
      <line x1="-8" y1="5" x2="8" y2="5" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.7"/>
      <polygon points="-10,0 -14,-4 -14,4" fill="{p['accent1']}" opacity="0.5"/>
      <polygon points="10,0 14,-4 14,4" fill="{p['accent1']}" opacity="0.5"/>
    </g>
    <text x="700" y="350" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">ALB</text>

    <!-- Pulsing ring on cloud -->
    <ellipse cx="700" cy="180" rx="140" ry="70" fill="none" stroke="{p['accent1']}"
             stroke-width="0.8" opacity="0.2" style="animation: {u}pulse 4s ease-in-out infinite"/>

    <!-- Ambient glow -->
    <ellipse cx="750" cy="300" rx="250" ry="180" fill="{p['glow']}" opacity="0.04"/>
"""


def _scene_kubernetes(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: Kubernetes / Container -->
    <!-- Cluster circle -->
    <circle cx="720" cy="280" r="160" fill="none" stroke="{p['accent1']}" stroke-width="1"
            stroke-dasharray="6 4" opacity="0.3"/>
    <circle cx="720" cy="280" r="120" fill="none" stroke="{p['accent3']}" stroke-width="0.8"
            opacity="0.2"/>
    <text x="720" y="130" font-family="Courier New, monospace" font-size="9"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">CLUSTER</text>

    <!-- Pod boxes -->
    <rect x="640" y="200" width="70" height="50" rx="6" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <rect x="644" y="204" width="62" height="42" rx="4" fill="none" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.4"/>
    <text x="675" y="230" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">POD</text>

    <rect x="760" y="200" width="70" height="50" rx="6" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <rect x="764" y="204" width="62" height="42" rx="4" fill="none" stroke="{p['accent2']}" stroke-width="0.5" opacity="0.4"/>
    <text x="795" y="230" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent2']}" text-anchor="middle" font-weight="bold">POD</text>

    <rect x="700" y="310" width="70" height="50" rx="6" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1.5"/>
    <rect x="704" y="314" width="62" height="42" rx="4" fill="none" stroke="{p['accent3']}" stroke-width="0.5" opacity="0.4"/>
    <text x="735" y="340" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent3']}" text-anchor="middle" font-weight="bold">POD</text>

    <!-- Docker whale -->
    <g filter="url(#{u}glow)" transform="translate(580,380)">
      <circle cx="0" cy="0" r="35" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="2"/>
      <rect x="-15" y="-8" width="8" height="6" rx="1" fill="{p['accent2']}" opacity="0.7"/>
      <rect x="-5" y="-8" width="8" height="6" rx="1" fill="{p['accent2']}" opacity="0.7"/>
      <rect x="5" y="-8" width="8" height="6" rx="1" fill="{p['accent2']}" opacity="0.7"/>
      <rect x="-15" y="-16" width="8" height="6" rx="1" fill="{p['accent2']}" opacity="0.5"/>
      <rect x="-5" y="-16" width="8" height="6" rx="1" fill="{p['accent2']}" opacity="0.5"/>
      <ellipse cx="0" cy="5" rx="20" ry="10" fill="none" stroke="{p['accent2']}" stroke-width="1.2"/>
    </g>
    <text x="580" y="425" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">DOCKER</text>

    <!-- Node connections -->
    <g filter="url(#{u}glow)">
      <circle cx="900" cy="350" r="30" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2"/>
    </g>
    <text x="900" y="348" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle">NODE</text>
    <text x="900" y="360" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">worker-1</text>

    <!-- Connection lines -->
    <line x1="710" y1="250" x2="735" y2="310" stroke="{p['accent1']}" stroke-width="1.2"
          opacity="0.4" stroke-dasharray="4 3"/>
    <line x1="830" y1="225" x2="770" y2="310" stroke="{p['accent2']}" stroke-width="1.2"
          opacity="0.35" stroke-dasharray="4 3"/>
    <line x1="770" y1="335" x2="870" y2="348" stroke="{p['accent1']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="3 5" style="animation: {u}dash 2s linear infinite"/>
    <line x1="615" y1="380" x2="640" y2="250" stroke="{p['accent2']}" stroke-width="1"
          opacity="0.25" stroke-dasharray="3 5"/>

    <!-- Container escape visualization (cracked box) -->
    <g transform="translate(870,200)">
      <rect x="-25" y="-20" width="50" height="40" rx="4" fill="{p['bg2']}" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.7"/>
      <line x1="-10" y1="-20" x2="5" y2="20" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.6" class="{u}crack"/>
      <path d="M-5,-20 L0,-15 L5,-20" fill="none" stroke="{p['accent1']}" stroke-width="1" opacity="0.5"/>
      <text x="0" y="3" font-family="Courier New, monospace" font-size="7"
            fill="{p['accent1']}" text-anchor="middle" opacity="0.8">ESC</text>
    </g>
    <text x="870" y="230" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">ESCAPE</text>

    <!-- Namespace labels -->
    <rect x="625" y="260" width="60" height="16" rx="3" fill="{p['badge_bg']}" stroke="{p['accent1']}" stroke-width="0.6" opacity="0.5"/>
    <text x="655" y="271" font-family="Courier New, monospace" font-size="6"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.7">ns:prod</text>
    <rect x="770" y="260" width="56" height="16" rx="3" fill="{p['badge_bg']}" stroke="{p['accent2']}" stroke-width="0.6" opacity="0.5"/>
    <text x="798" y="271" font-family="Courier New, monospace" font-size="6"
          fill="{p['accent2']}" text-anchor="middle" opacity="0.7">ns:dev</text>

    <!-- Helm icon -->
    <g transform="translate(950,440)" filter="url(#{u}fxGlow)">
      <circle cx="0" cy="0" r="22" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1.5"/>
      <circle cx="0" cy="0" r="10" fill="none" stroke="{p['accent3']}" stroke-width="1" opacity="0.6"/>
      <line x1="0" y1="-14" x2="0" y2="-18" stroke="{p['accent3']}" stroke-width="2" opacity="0.5"/>
      <line x1="0" y1="14" x2="0" y2="18" stroke="{p['accent3']}" stroke-width="2" opacity="0.5"/>
      <line x1="-14" y1="0" x2="-18" y2="0" stroke="{p['accent3']}" stroke-width="2" opacity="0.5"/>
      <line x1="14" y1="0" x2="18" y2="0" stroke="{p['accent3']}" stroke-width="2" opacity="0.5"/>
    </g>
    <text x="950" y="470" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">HELM</text>

    <!-- Service mesh lines -->
    <path d="M 675 250 Q 720 270 735 310" fill="none" stroke="{p['accent1']}" stroke-width="0.8"
          opacity="0.2" stroke-dasharray="2 3"/>
    <path d="M 795 250 Q 770 280 735 310" fill="none" stroke="{p['accent2']}" stroke-width="0.8"
          opacity="0.2" stroke-dasharray="2 3"/>
    <path d="M 770 340 Q 830 370 900 355" fill="none" stroke="{p['accent3']}" stroke-width="0.8"
          opacity="0.2" stroke-dasharray="2 3"/>

    <!-- Pulsing rings -->
    <circle cx="720" cy="280" r="90" fill="none" stroke="{p['accent3']}" stroke-width="0.8"
            opacity="0.15" style="animation: {u}pulse 3s ease-in-out infinite"/>

    <!-- Ambient glow -->
    <ellipse cx="720" cy="300" rx="220" ry="180" fill="{p['glow']}" opacity="0.04"/>
"""


def _scene_ai(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: AI / ML -->
    <!-- Neural network center -->
    <g filter="url(#{u}glow)">
      <circle cx="700" cy="260" r="50" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2.5"/>
      <circle cx="700" cy="260" r="50" fill="{p['glow']}" opacity="0.08"/>
    </g>
    <!-- Brain circuit paths -->
    <ellipse cx="700" cy="255" rx="22" ry="18" fill="none" stroke="{p['accent1']}" stroke-width="1.5"/>
    <path d="M685 250 Q700 235 715 250" fill="none" stroke="{p['accent1']}" stroke-width="1" opacity="0.7"/>
    <path d="M685 260 Q700 275 715 260" fill="none" stroke="{p['accent3']}" stroke-width="1" opacity="0.7"/>
    <circle cx="700" cy="255" r="5" fill="{p['accent1']}" opacity="0.6"/>
    <text x="700" y="300" font-family="Courier New, monospace" font-size="9"
          fill="{p['text_accent']}" text-anchor="middle" font-weight="bold">AI MODEL</text>

    <!-- Layer nodes (input) -->
    <circle cx="540" cy="180" r="18" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <circle cx="540" cy="260" r="18" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <circle cx="540" cy="340" r="18" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>

    <!-- Layer nodes (output) -->
    <circle cx="860" cy="200" r="18" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1.5"/>
    <circle cx="860" cy="320" r="18" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1.5"/>

    <!-- Data pipeline connections -->
    <line x1="558" y1="185" x2="652" y2="248" stroke="{p['accent2']}" stroke-width="1" opacity="0.4"/>
    <line x1="558" y1="260" x2="652" y2="260" stroke="{p['accent2']}" stroke-width="1.2" opacity="0.5"
          stroke-dasharray="4 3" style="animation: {u}dash 2s linear infinite"/>
    <line x1="558" y1="335" x2="652" y2="272" stroke="{p['accent2']}" stroke-width="1" opacity="0.4"/>
    <line x1="748" y1="250" x2="842" y2="205" stroke="{p['accent3']}" stroke-width="1" opacity="0.4"/>
    <line x1="748" y1="270" x2="842" y2="315" stroke="{p['accent3']}" stroke-width="1" opacity="0.4"/>

    <!-- Model card -->
    <rect x="620" y="380" width="160" height="80" rx="6" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.8"/>
    <text x="700" y="405" font-family="Courier New, monospace" font-size="9"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.8">PARAMETERS</text>
    <rect x="640" y="415" width="120" height="8" rx="3" fill="{p['accent1']}" opacity="0.15"/>
    <rect x="640" y="415" width="85" height="8" rx="3" fill="{p['accent1']}" opacity="0.4"/>
    <rect x="640" y="430" width="120" height="8" rx="3" fill="{p['accent3']}" opacity="0.15"/>
    <rect x="640" y="430" width="60" height="8" rx="3" fill="{p['accent3']}" opacity="0.4"/>
    <rect x="640" y="445" width="120" height="8" rx="3" fill="{p['accent2']}" opacity="0.15"/>
    <rect x="640" y="445" width="100" height="8" rx="3" fill="{p['accent2']}" opacity="0.4"/>

    <!-- Gradient computation node -->
    <g filter="url(#{u}glow)">
      <circle cx="950" cy="260" r="28" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    </g>
    <text x="950" y="258" font-family="Courier New, monospace" font-size="16"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.8">&#x2207;</text>
    <text x="950" y="280" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">GRADIENT</text>
    <line x1="878" y1="210" x2="924" y2="250" stroke="{p['accent3']}" stroke-width="1" opacity="0.3" stroke-dasharray="3 5"/>
    <line x1="878" y1="315" x2="924" y2="270" stroke="{p['accent3']}" stroke-width="1" opacity="0.3" stroke-dasharray="3 5"/>

    <!-- Neural network 3 layers of connected nodes -->
    <!-- Hidden layer -->
    <circle cx="620" cy="180" r="10" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    <circle cx="620" cy="220" r="10" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    <circle cx="620" cy="260" r="10" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    <circle cx="620" cy="300" r="10" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    <circle cx="620" cy="340" r="10" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    <!-- Hidden layer 2 -->
    <circle cx="780" cy="200" r="10" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1" opacity="0.6"/>
    <circle cx="780" cy="240" r="10" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1" opacity="0.6"/>
    <circle cx="780" cy="280" r="10" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1" opacity="0.6"/>
    <circle cx="780" cy="320" r="10" fill="{p['bg1']}" stroke="{p['accent3']}" stroke-width="1" opacity="0.6"/>
    <!-- Neural connections (sparse) -->
    <line x1="558" y1="180" x2="610" y2="180" stroke="{p['accent2']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="558" y1="260" x2="610" y2="220" stroke="{p['accent2']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="558" y1="260" x2="610" y2="300" stroke="{p['accent2']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="558" y1="340" x2="610" y2="340" stroke="{p['accent2']}" stroke-width="0.6" opacity="0.2"/>
    <line x1="630" y1="185" x2="770" y2="200" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.15"/>
    <line x1="630" y1="220" x2="770" y2="240" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.15"/>
    <line x1="630" y1="260" x2="770" y2="280" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.18"/>
    <line x1="630" y1="300" x2="770" y2="280" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.15"/>
    <line x1="630" y1="340" x2="770" y2="320" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.15"/>
    <line x1="790" y1="205" x2="842" y2="200" stroke="{p['accent3']}" stroke-width="0.5" opacity="0.15"/>
    <line x1="790" y1="280" x2="842" y2="260" stroke="{p['accent3']}" stroke-width="0.5" opacity="0.18"/>
    <line x1="790" y1="320" x2="842" y2="320" stroke="{p['accent3']}" stroke-width="0.5" opacity="0.15"/>

    <!-- Brain circuit pattern -->
    <path d="M 680 240 Q 700 220 720 240 Q 740 260 720 280 Q 700 300 680 280 Q 660 260 680 240"
          fill="none" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.2"/>
    <path d="M 690 248 Q 700 238 710 248" fill="none" stroke="{p['accent3']}" stroke-width="0.6" opacity="0.25"/>
    <path d="M 690 268 Q 700 278 710 268" fill="none" stroke="{p['accent3']}" stroke-width="0.6" opacity="0.25"/>

    <!-- Data pipeline arrows -->
    <path d="M 470 260 L 520 260" fill="none" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.4"
          stroke-dasharray="4 3" style="animation: {u}dash 2s linear infinite"/>
    <polygon points="518,255 528,260 518,265" fill="{p['accent2']}" opacity="0.4"/>
    <path d="M 878 260 L 930 260" fill="none" stroke="{p['accent3']}" stroke-width="1.5" opacity="0.35"/>
    <polygon points="928,255 938,260 928,265" fill="{p['accent3']}" opacity="0.35"/>

    <!-- Training progress badge -->
    <rect x="830" y="370" width="100" height="28" rx="4" fill="{p['bg2']}" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.6"/>
    <text x="880" y="384" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.7">EPOCH 42/100</text>
    <rect x="840" y="390" width="80" height="4" rx="2" fill="{p['accent1']}" opacity="0.15"/>
    <rect x="840" y="390" width="34" height="4" rx="2" fill="{p['accent1']}" opacity="0.5"/>

    <!-- Pulsing rings -->
    <circle cx="700" cy="260" r="70" fill="none" stroke="{p['accent1']}" stroke-width="0.8"
            opacity="0.2" style="animation: {u}pulse 3s ease-in-out infinite"/>

    <!-- Ambient glow -->
    <ellipse cx="720" cy="280" rx="260" ry="180" fill="{p['glow']}" opacity="0.035"/>
"""


def _scene_devops(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: DevOps Pipeline -->
    <!-- Pipeline stages -->
    <rect x="480" y="200" width="100" height="60" rx="8" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <text x="530" y="225" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent2']}" text-anchor="middle" font-weight="bold">BUILD</text>
    <circle cx="530" y="248" r="4" fill="{p['accent2']}" opacity="0.6" style="animation: {u}pulse 2s ease-in-out infinite"/>

    <rect x="630" y="200" width="100" height="60" rx="8" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="680" y="225" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">TEST</text>
    <circle cx="680" y="248" r="4" fill="{p['accent1']}" opacity="0.6"/>

    <rect x="780" y="200" width="100" height="60" rx="8" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="830" y="225" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">DEPLOY</text>
    <circle cx="830" y="248" r="4" fill="#22c55e" opacity="0.6"/>

    <rect x="930" y="200" width="100" height="60" rx="8" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <text x="980" y="225" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent2']}" text-anchor="middle" font-weight="bold">MONITOR</text>

    <!-- Pipeline arrows -->
    <line x1="580" y1="230" x2="625" y2="230" stroke="{p['accent2']}" stroke-width="2" opacity="0.6"
          stroke-dasharray="4 3" style="animation: {u}dash 1.5s linear infinite"/>
    <polygon points="625,225 635,230 625,235" fill="{p['accent2']}" opacity="0.6"/>
    <line x1="730" y1="230" x2="775" y2="230" stroke="{p['accent1']}" stroke-width="2" opacity="0.5"/>
    <polygon points="775,225 785,230 775,235" fill="{p['accent1']}" opacity="0.5"/>
    <line x1="880" y1="230" x2="925" y2="230" stroke="{p['accent2']}" stroke-width="2" opacity="0.5"/>
    <polygon points="925,225 935,230 925,235" fill="{p['accent2']}" opacity="0.5"/>

    <!-- Git branch visualization -->
    <circle cx="600" cy="380" r="8" fill="{p['accent2']}" opacity="0.7"/>
    <circle cx="700" cy="380" r="8" fill="{p['accent1']}" opacity="0.7"/>
    <circle cx="800" cy="380" r="8" fill="{p['accent2']}" opacity="0.7"/>
    <circle cx="700" cy="430" r="8" fill="{p['accent3']}" opacity="0.5"/>
    <line x1="608" y1="380" x2="692" y2="380" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.5"/>
    <line x1="708" y1="380" x2="792" y2="380" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.5"/>
    <line x1="700" y1="388" x2="700" y2="422" stroke="{p['accent3']}" stroke-width="1" opacity="0.4" stroke-dasharray="3 3"/>
    <text x="600" y="400" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">main</text>
    <text x="700" y="452" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">feature</text>

    <!-- Shield with checkmark -->
    <g filter="url(#{u}glow)" transform="translate(950,380)">
      <circle cx="0" cy="0" r="30" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="2"/>
      <path d="M0,-15 L12,-9 L12,3 Q12,12 0,18 Q-12,12 -12,3 L-12,-9 Z"
            fill="none" stroke="{p['accent2']}" stroke-width="1.5"/>
      <polyline points="-6,2 -2,7 8,-5" fill="none" stroke="{p['accent2']}" stroke-width="2"/>
    </g>
    <text x="950" y="420" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">SECURE</text>

    <!-- Pipeline stage labels -->
    <rect x="485" y="262" width="90" height="14" rx="3" fill="{p['accent2']}" opacity="0.1"/>
    <text x="530" y="273" font-family="Courier New, monospace" font-size="6"
          fill="{p['accent2']}" text-anchor="middle" opacity="0.6">COMPILE OK</text>
    <rect x="635" y="262" width="90" height="14" rx="3" fill="{p['accent1']}" opacity="0.1"/>
    <text x="680" y="273" font-family="Courier New, monospace" font-size="6"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.6">42/42 PASS</text>
    <rect x="785" y="262" width="90" height="14" rx="3" fill="#22c55e" opacity="0.1"/>
    <text x="830" y="273" font-family="Courier New, monospace" font-size="6"
          fill="#22c55e" text-anchor="middle" opacity="0.6">LIVE v2.1</text>

    <!-- CI/CD badges -->
    <rect x="480" y="130" width="80" height="22" rx="4" fill="{p['badge_bg']}" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.6"/>
    <circle cx="495" cy="141" r="4" fill="#22c55e" opacity="0.6"/>
    <text x="525" y="145" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" opacity="0.7">CI/CD</text>
    <rect x="580" y="130" width="80" height="22" rx="4" fill="{p['badge_bg']}" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.6"/>
    <circle cx="595" cy="141" r="4" fill="{p['accent1']}" opacity="0.5" class="{u}blink"/>
    <text x="625" y="145" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" opacity="0.7">SCAN</text>

    <!-- Terraform icon -->
    <g transform="translate(480,430)" filter="url(#{u}fxGlow)">
      <rect x="-18" y="-14" width="36" height="28" rx="4" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.2"/>
      <rect x="-10" y="-8" width="8" height="8" rx="1" fill="{p['accent2']}" opacity="0.5"/>
      <rect x="2" y="-8" width="8" height="8" rx="1" fill="{p['accent2']}" opacity="0.5"/>
      <rect x="-10" y="2" width="8" height="8" rx="1" fill="{p['accent2']}" opacity="0.4"/>
      <rect x="2" y="2" width="8" height="8" rx="1" fill="{p['accent2']}" opacity="0.3"/>
    </g>
    <text x="480" y="458" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">IaC</text>

    <!-- Additional git branch detail -->
    <circle cx="900" cy="380" r="8" fill="{p['accent1']}" opacity="0.5"/>
    <line x1="808" y1="380" x2="892" y2="380" stroke="{p['accent1']}" stroke-width="1.5" opacity="0.4"/>
    <text x="900" y="400" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">release</text>
    <line x1="700" y1="430" x2="800" y2="430" stroke="{p['accent3']}" stroke-width="1" opacity="0.3" stroke-dasharray="3 3"/>
    <text x="750" y="448" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.5">merge --no-ff</text>

    <!-- Ambient glow -->
    <ellipse cx="730" cy="280" rx="260" ry="160" fill="{p['glow']}" opacity="0.035"/>
"""


def _scene_finops(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: FinOps -->
    <!-- Cost chart bars -->
    <rect x="520" y="320" width="40" height="120" rx="4" fill="{p['accent1']}" opacity="0.25"/>
    <rect x="520" y="370" width="40" height="70" rx="4" fill="{p['accent1']}" opacity="0.5"/>
    <rect x="580" y="280" width="40" height="160" rx="4" fill="{p['accent1']}" opacity="0.25"/>
    <rect x="580" y="350" width="40" height="90" rx="4" fill="{p['accent2']}" opacity="0.5"/>
    <rect x="640" y="300" width="40" height="140" rx="4" fill="{p['accent1']}" opacity="0.25"/>
    <rect x="640" y="340" width="40" height="100" rx="4" fill="{p['accent1']}" opacity="0.4"/>
    <rect x="700" y="340" width="40" height="100" rx="4" fill="{p['accent2']}" opacity="0.25"/>
    <rect x="700" y="380" width="40" height="60" rx="4" fill="{p['accent2']}" opacity="0.6"
          style="animation: {u}glimmer 3s ease-in-out infinite"/>
    <text x="630" y="465" font-family="Courier New, monospace" font-size="9"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">COST TREND</text>

    <!-- Dollar sign node -->
    <g filter="url(#{u}glow)">
      <circle cx="600" cy="200" r="40" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2"/>
    </g>
    <text x="600" y="210" font-family="Courier New, monospace" font-size="28"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">$</text>

    <!-- Cloud with price tag -->
    <ellipse cx="850" cy="200" rx="80" ry="40" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5" opacity="0.7"/>
    <text x="850" y="198" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent2']}" text-anchor="middle">CLOUD</text>
    <text x="850" y="212" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">SPEND</text>

    <!-- Optimization arrows -->
    <g transform="translate(900,350)">
      <circle cx="0" cy="0" r="30" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
      <polyline points="-10,-8 0,8 10,-8" fill="none" stroke="{p['accent2']}" stroke-width="2"/>
      <line x1="0" y1="-12" x2="0" y2="2" stroke="{p['accent2']}" stroke-width="2"/>
    </g>
    <text x="900" y="392" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">OPTIMIZE</text>

    <!-- Connection lines -->
    <line x1="640" y1="200" x2="770" y2="200" stroke="{p['accent1']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="4 4" style="animation: {u}dash 2s linear infinite"/>
    <line x1="850" y1="240" x2="900" y2="320" stroke="{p['accent2']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="3 5"/>
    <line x1="600" y1="240" x2="600" y2="310" stroke="{p['accent1']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="3 5"/>

    <!-- Bar chart with axis -->
    <line x1="510" y1="440" x2="750" y2="440" stroke="{p['text_accent']}" stroke-width="0.8" opacity="0.3"/>
    <line x1="510" y1="300" x2="510" y2="440" stroke="{p['text_accent']}" stroke-width="0.8" opacity="0.3"/>
    <text x="505" y="445" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" text-anchor="end" opacity="0.4">$0</text>
    <text x="505" y="370" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" text-anchor="end" opacity="0.4">$5K</text>
    <text x="505" y="310" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" text-anchor="end" opacity="0.4">$10K</text>

    <!-- Cost arrow trending down -->
    <path d="M 780 180 Q 820 200 860 260 Q 900 320 940 310" fill="none"
          stroke="{p['accent2']}" stroke-width="2" opacity="0.5" stroke-dasharray="6 3"
          style="animation: {u}dash 3s linear infinite"/>
    <polygon points="938,305 948,310 938,315" fill="{p['accent2']}" opacity="0.5"/>
    <text x="960" y="315" font-family="Courier New, monospace" font-size="9"
          fill="{p['accent2']}" opacity="0.7" font-weight="bold">-23%</text>

    <!-- Dollar sign coin -->
    <g transform="translate(850,380)" filter="url(#{u}fxGlow)">
      <circle cx="0" cy="0" r="25" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2"/>
      <circle cx="0" cy="0" r="20" fill="none" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.4"/>
      <text x="0" y="7" font-family="Courier New, monospace" font-size="18"
            fill="{p['accent1']}" text-anchor="middle" font-weight="bold" opacity="0.8">$</text>
    </g>

    <!-- Cloud with price tags -->
    <rect x="920" y="420" width="70" height="20" rx="3" fill="{p['badge_bg']}" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.6"/>
    <text x="955" y="434" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent2']}" text-anchor="middle" opacity="0.7">$142/mo</text>
    <rect x="920" y="445" width="70" height="20" rx="3" fill="{p['badge_bg']}" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.6"/>
    <text x="955" y="459" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent1']}" text-anchor="middle" opacity="0.7">$89/mo</text>

    <!-- Savings badge -->
    <rect x="780" y="470" width="90" height="24" rx="4" fill="{p['bg2']}" stroke="#22c55e" stroke-width="1.2" opacity="0.6"/>
    <text x="825" y="486" font-family="Courier New, monospace" font-size="9"
          fill="#22c55e" text-anchor="middle" font-weight="bold" opacity="0.8">SAVED 37%</text>

    <!-- Ambient glow -->
    <ellipse cx="730" cy="300" rx="240" ry="170" fill="{p['glow']}" opacity="0.035"/>
"""


def _scene_blockchain(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: Blockchain -->
    <!-- Chain blocks -->
    <rect x="480" y="240" width="80" height="60" rx="6" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="520" y="270" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">BLOCK</text>
    <text x="520" y="284" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">#N-2</text>

    <rect x="610" y="240" width="80" height="60" rx="6" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="650" y="270" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">BLOCK</text>
    <text x="650" y="284" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">#N-1</text>

    <rect x="740" y="240" width="80" height="60" rx="6" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="2"
          style="animation: {u}glimmer 3s ease-in-out infinite"/>
    <text x="780" y="270" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent2']}" text-anchor="middle" font-weight="bold">BLOCK</text>
    <text x="780" y="284" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">#N</text>

    <!-- Chain links -->
    <line x1="560" y1="270" x2="608" y2="270" stroke="{p['accent1']}" stroke-width="2" opacity="0.6"
          stroke-dasharray="4 3" style="animation: {u}dash 2s linear infinite"/>
    <line x1="690" y1="270" x2="738" y2="270" stroke="{p['accent1']}" stroke-width="2" opacity="0.6"/>

    <!-- Network nodes -->
    <g filter="url(#{u}glow)">
      <circle cx="650" cy="160" r="30" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    </g>
    <text x="650" y="158" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle">NODE</text>
    <text x="650" y="170" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">peer-1</text>

    <g filter="url(#{u}glow)">
      <circle cx="900" cy="280" r="30" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    </g>
    <text x="900" y="278" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent2']}" text-anchor="middle">NODE</text>
    <text x="900" y="290" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">peer-2</text>

    <!-- Smart contract box -->
    <rect x="600" y="370" width="140" height="70" rx="6" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.8"/>
    <text x="670" y="395" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle" font-weight="bold">SMART CONTRACT</text>
    <text x="670" y="412" font-family="Courier New, monospace" font-size="7"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.6">0x7f2c...a3b8</text>
    <rect x="620" y="420" width="100" height="6" rx="2" fill="{p['accent2']}" opacity="0.2"/>
    <rect x="620" y="420" width="65" height="6" rx="2" fill="{p['accent2']}" opacity="0.5"/>

    <!-- Connections -->
    <line x1="650" y1="190" x2="650" y2="240" stroke="{p['accent1']}" stroke-width="1" opacity="0.4" stroke-dasharray="3 4"/>
    <line x1="820" y1="270" x2="870" y2="278" stroke="{p['accent2']}" stroke-width="1" opacity="0.3" stroke-dasharray="3 5"/>
    <line x1="670" y1="300" x2="670" y2="370" stroke="{p['accent1']}" stroke-width="1" opacity="0.3" stroke-dasharray="3 5"/>

    <!-- Chain link icons between blocks -->
    <g transform="translate(575,270)">
      <ellipse cx="0" cy="0" rx="8" ry="5" fill="none" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.5"/>
      <ellipse cx="6" cy="0" rx="8" ry="5" fill="none" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.5"/>
    </g>
    <g transform="translate(705,270)">
      <ellipse cx="0" cy="0" rx="8" ry="5" fill="none" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.5"/>
      <ellipse cx="6" cy="0" rx="8" ry="5" fill="none" stroke="{p['accent1']}" stroke-width="1.2" opacity="0.5"/>
    </g>

    <!-- Block internal hash pattern -->
    <text x="520" y="295" font-family="Courier New, monospace" font-size="5"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.35">0xfa3b..c2</text>
    <text x="650" y="295" font-family="Courier New, monospace" font-size="5"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.35">0x8e1d..a7</text>
    <text x="780" y="295" font-family="Courier New, monospace" font-size="5"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.35">0x2c4f..91</text>

    <!-- Crypto coin with hash pattern -->
    <g transform="translate(950,180)" filter="url(#{u}fxGlow)">
      <circle cx="0" cy="0" r="28" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2"/>
      <circle cx="0" cy="0" r="22" fill="none" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.4"/>
      <text x="0" y="4" font-family="Courier New, monospace" font-size="12"
            fill="{p['accent1']}" text-anchor="middle" font-weight="bold" opacity="0.8">ETH</text>
      <text x="0" y="14" font-family="Courier New, monospace" font-size="5"
            fill="{p['text_accent']}" text-anchor="middle" opacity="0.5">#HASH</text>
    </g>

    <!-- Consensus badge -->
    <rect x="850" y="340" width="95" height="24" rx="4" fill="{p['bg2']}" stroke="{p['accent2']}" stroke-width="1" opacity="0.6"/>
    <text x="897" y="356" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent2']}" text-anchor="middle" font-weight="bold" opacity="0.7">CONSENSUS</text>

    <!-- Merkle tree hint -->
    <circle cx="520" cy="380" r="6" fill="{p['accent1']}" opacity="0.3"/>
    <circle cx="500" cy="410" r="5" fill="{p['accent1']}" opacity="0.2"/>
    <circle cx="540" cy="410" r="5" fill="{p['accent1']}" opacity="0.2"/>
    <line x1="520" y1="386" x2="500" y2="405" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.2"/>
    <line x1="520" y1="386" x2="540" y2="405" stroke="{p['accent1']}" stroke-width="0.8" opacity="0.2"/>
    <circle cx="490" cy="435" r="4" fill="{p['accent3']}" opacity="0.15"/>
    <circle cx="510" cy="435" r="4" fill="{p['accent3']}" opacity="0.15"/>
    <circle cx="530" cy="435" r="4" fill="{p['accent3']}" opacity="0.15"/>
    <circle cx="550" cy="435" r="4" fill="{p['accent3']}" opacity="0.15"/>
    <line x1="500" y1="415" x2="490" y2="431" stroke="{p['accent3']}" stroke-width="0.6" opacity="0.15"/>
    <line x1="500" y1="415" x2="510" y2="431" stroke="{p['accent3']}" stroke-width="0.6" opacity="0.15"/>
    <line x1="540" y1="415" x2="530" y2="431" stroke="{p['accent3']}" stroke-width="0.6" opacity="0.15"/>
    <line x1="540" y1="415" x2="550" y2="431" stroke="{p['accent3']}" stroke-width="0.6" opacity="0.15"/>
    <text x="520" y="455" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.4">MERKLE</text>

    <!-- Ambient glow -->
    <ellipse cx="700" cy="290" rx="240" ry="160" fill="{p['glow']}" opacity="0.035"/>
"""


def _scene_general(p: dict, u: str, tag_labels: list[str]) -> str:
    return f"""
    <!-- SCENE: General Tech -->
    <!-- Network central node -->
    <g filter="url(#{u}glow)">
      <circle cx="700" cy="260" r="45" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="2.5"/>
      <circle cx="700" cy="260" r="45" fill="{p['glow']}" opacity="0.08"/>
    </g>
    <!-- Code brackets -->
    <text x="688" y="268" font-family="Courier New, monospace" font-size="22"
          fill="{p['accent1']}" opacity="0.8">&lt;/&gt;</text>

    <!-- Terminal window -->
    <rect x="830" y="160" width="140" height="90" rx="6" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <rect x="830" y="160" width="140" height="18" rx="6" fill="{p['accent2']}" opacity="0.15"/>
    <circle cx="844" cy="169" r="3" fill="#ef4444" opacity="0.6"/>
    <circle cx="856" cy="169" r="3" fill="#f59e0b" opacity="0.6"/>
    <circle cx="868" cy="169" r="3" fill="#22c55e" opacity="0.6"/>
    <text x="842" y="198" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent2']}" opacity="0.7">$ deploy --prod</text>
    <text x="842" y="212" font-family="Courier New, monospace" font-size="8"
          fill="#22c55e" opacity="0.5">OK: deployed v2.1</text>
    <rect x="842" y="220" width="6" height="12" fill="{p['accent2']}" opacity="0.5"
          style="animation: {u}pulse 1s steps(2) infinite"/>

    <!-- Gear icon -->
    <g filter="url(#{u}glow)" transform="translate(550,380)">
      <circle cx="0" cy="0" r="32" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
      <circle cx="0" cy="0" r="14" fill="none" stroke="{p['accent1']}" stroke-width="2" opacity="0.7"/>
      <circle cx="0" cy="0" r="6" fill="{p['accent1']}" opacity="0.5"/>
      <line x1="0" y1="-18" x2="0" y2="-24" stroke="{p['accent1']}" stroke-width="2.5" opacity="0.6"/>
      <line x1="0" y1="18" x2="0" y2="24" stroke="{p['accent1']}" stroke-width="2.5" opacity="0.6"/>
      <line x1="-18" y1="0" x2="-24" y2="0" stroke="{p['accent1']}" stroke-width="2.5" opacity="0.6"/>
      <line x1="18" y1="0" x2="24" y2="0" stroke="{p['accent1']}" stroke-width="2.5" opacity="0.6"/>
    </g>
    <text x="550" y="422" font-family="Courier New, monospace" font-size="8"
          fill="{p['text_accent']}" text-anchor="middle" opacity="0.7">CONFIG</text>

    <!-- Network satellite nodes -->
    <circle cx="850" cy="380" r="22" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1.5"/>
    <text x="850" y="384" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent2']}" text-anchor="middle">API</text>

    <circle cx="600" cy="180" r="22" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1.5"/>
    <text x="600" y="184" font-family="Courier New, monospace" font-size="8"
          fill="{p['accent1']}" text-anchor="middle">DB</text>

    <!-- Connection web -->
    <line x1="740" y1="252" x2="830" y2="178" stroke="{p['accent2']}" stroke-width="1.2"
          opacity="0.4" stroke-dasharray="4 3"/>
    <line x1="700" y1="305" x2="560" y2="352" stroke="{p['accent1']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="4 4" style="animation: {u}dash 2s linear infinite"/>
    <line x1="740" y1="285" x2="835" y2="365" stroke="{p['accent2']}" stroke-width="1"
          opacity="0.3" stroke-dasharray="3 5"/>
    <line x1="665" y1="240" x2="618" y2="195" stroke="{p['accent1']}" stroke-width="1"
          opacity="0.35" stroke-dasharray="4 3"/>
    <path d="M 600 200 Q 650 280 700 260" fill="none" stroke="{p['accent1']}"
          stroke-width="0.8" opacity="0.2"/>

    <!-- Database cylinder icon -->
    <g transform="translate(600,180)">
      <ellipse cx="0" cy="-8" rx="14" ry="5" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1"/>
      <rect x="-14" y="-8" width="28" height="16" fill="{p['bg1']}" stroke="none"/>
      <line x1="-14" y1="-8" x2="-14" y2="8" stroke="{p['accent1']}" stroke-width="1"/>
      <line x1="14" y1="-8" x2="14" y2="8" stroke="{p['accent1']}" stroke-width="1"/>
      <ellipse cx="0" cy="8" rx="14" ry="5" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1"/>
      <ellipse cx="0" cy="-1" rx="14" ry="5" fill="none" stroke="{p['accent1']}" stroke-width="0.5" opacity="0.3"/>
    </g>

    <!-- Microservice boxes -->
    <rect x="440" y="280" width="65" height="35" rx="4" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1" opacity="0.6"/>
    <text x="472" y="302" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent2']}" text-anchor="middle" opacity="0.7">SVC-A</text>
    <rect x="440" y="330" width="65" height="35" rx="4" fill="{p['bg1']}" stroke="{p['accent2']}" stroke-width="1" opacity="0.6"/>
    <text x="472" y="352" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent2']}" text-anchor="middle" opacity="0.7">SVC-B</text>
    <line x1="505" y1="297" x2="660" y2="260" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.25" stroke-dasharray="3 3"/>
    <line x1="505" y1="347" x2="660" y2="265" stroke="{p['accent2']}" stroke-width="0.8" opacity="0.25" stroke-dasharray="3 3"/>

    <!-- Monitoring dashboard mini -->
    <rect x="800" y="420" width="130" height="65" rx="5" fill="{p['bg1']}" stroke="{p['accent1']}" stroke-width="1" opacity="0.6"/>
    <text x="810" y="436" font-family="Courier New, monospace" font-size="7"
          fill="{p['accent1']}" font-weight="bold" opacity="0.7">MONITOR</text>
    <!-- Sparkline -->
    <polyline points="810,455 825,448 840,460 855,445 870,452 885,442 900,450 915,440"
              fill="none" stroke="{p['accent2']}" stroke-width="1" opacity="0.5"/>
    <text x="810" y="475" font-family="Courier New, monospace" font-size="6"
          fill="{p['text_accent']}" opacity="0.5">CPU: 42% | MEM: 67%</text>

    <!-- Webhook arrow -->
    <path d="M 870 380 Q 890 400 870 420" fill="none" stroke="{p['accent1']}"
          stroke-width="1" opacity="0.3" stroke-dasharray="3 3" style="animation: {u}dash 2s linear infinite"/>
    <polygon points="867,418 875,425 873,415" fill="{p['accent1']}" opacity="0.3"/>

    <!-- Pulsing ring -->
    <circle cx="700" cy="260" r="70" fill="none" stroke="{p['accent1']}" stroke-width="0.8"
            opacity="0.2" style="animation: {u}pulse 3s ease-in-out infinite"/>

    <!-- Ambient glow -->
    <ellipse cx="720" cy="280" rx="250" ry="180" fill="{p['glow']}" opacity="0.035"/>
"""


SCENE_RENDERERS = {
    "security":   _scene_security,
    "cloud":      _scene_cloud,
    "kubernetes": _scene_kubernetes,
    "ai":         _scene_ai,
    "devops":     _scene_devops,
    "finops":     _scene_finops,
    "blockchain": _scene_blockchain,
    "general":    _scene_general,
}


# ---------------------------------------------------------------------------
# SVG assembly
# ---------------------------------------------------------------------------

def generate_svg(
    title: str,
    date_str: str,
    tags: list[str],
    categories: list[str],
    theme: str,
    filepath: str,
) -> str:
    """Build the full SVG string."""
    p = PALETTES[theme]
    u = uid(filepath)
    title_lines = split_title(title)
    tag_labels = english_tags(tags)
    date_display = format_date(date_str)

    # Build tag pills (up to 3)
    pill_colors = [p["accent1"], p["accent2"], p["accent3"]]
    pill_bgs = [p["badge_bg"], p["bg2"], p["bg1"]]
    tag_pills = ""
    x_off = 40
    for i, label in enumerate(tag_labels[:3]):
        w = max(len(label) * 8 + 16, 54)
        c = pill_colors[i % len(pill_colors)]
        bg = pill_bgs[i % len(pill_bgs)]
        tag_pills += (
            f'    <rect x="{x_off}" y="525" width="{w}" height="24" rx="12" '
            f'fill="{bg}" stroke="{c}" stroke-width="1.2"/>\n'
            f'    <text x="{x_off + w // 2}" y="541" font-family="Courier New, monospace" '
            f'font-size="10" fill="{c}" text-anchor="middle" font-weight="bold">{label}</text>\n'
        )
        x_off += w + 10

    # Build title lines
    title_svg = ""
    y_start = 155
    for i, line in enumerate(title_lines):
        y = y_start + i * 48
        fs = 40 if len(line) > 16 else 44
        title_svg += (
            f'    <text x="40" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="{fs}" fill="url(#{u}title)" font-weight="700" '
            f'letter-spacing="-1">{line}</text>\n'
        )
    accent_y = y_start + len(title_lines) * 48 - 30

    # Severity / topic bars
    bar_labels = tag_labels[:2] if len(tag_labels) >= 2 else tag_labels
    bars_svg = ""
    for i, bl in enumerate(bar_labels):
        by = accent_y + 38 + i * 26
        bars_svg += (
            f'    <text x="40" y="{by}" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="16" fill="{pill_colors[i % len(pill_colors)]}" '
            f'font-weight="600">{bl}</text>\n'
        )

    # Scene + common decorations
    scene_fn = SCENE_RENDERERS.get(theme, _scene_general)
    scene_svg = scene_fn(p, u, tag_labels)
    decorations_svg = _common_decorations(p, u, tag_labels)

    # Floating particles
    particles = ""
    particle_data = [
        (150, 100, 2.5, p["accent1"], 0.5, 3.0),
        (1060, 150, 2.0, p["accent2"], 0.4, 2.8),
        (100, 480, 2.5, p["accent1"], 0.4, 3.5),
        (1100, 520, 2.0, p["accent3"], 0.5, 4.0),
        (180, 560, 1.5, p["accent2"], 0.35, 3.2),
        (1030, 80, 2.0, p["accent1"], 0.4, 2.5),
    ]
    for px, py, pr, pc, po, pd in particle_data:
        particles += (
            f'    <circle cx="{px}" cy="{py}" r="{pr}" fill="{pc}" opacity="{po}">\n'
            f'      <animate attributeName="opacity" values="{po};{po*0.3:.2f};{po}" '
            f'dur="{pd}s" repeatCount="indefinite"/>\n'
            f'    </circle>\n'
        )

    # Data stream lines
    streams = (
        f'    <line x1="50" y1="200" x2="120" y2="200" stroke="{p["accent1"]}" stroke-width="1" opacity="0.15"/>\n'
        f'    <line x1="50" y1="215" x2="95" y2="215" stroke="{p["accent1"]}" stroke-width="1" opacity="0.1"/>\n'
        f'    <line x1="1080" y1="400" x2="1150" y2="400" stroke="{p["accent3"]}" stroke-width="1" opacity="0.15"/>\n'
        f'    <line x1="1095" y1="415" x2="1150" y2="415" stroke="{p["accent3"]}" stroke-width="1" opacity="0.1"/>\n'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{title_lines[0]}</title>
  <!-- generator: upgrade_post_images.py; profile: high-quality-cover -->
  <defs>
    <linearGradient id="{u}bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{p['bg1']}"/>
      <stop offset="50%" style="stop-color:{p['bg2']}"/>
      <stop offset="100%" style="stop-color:{p['bg3']}"/>
    </linearGradient>
    <linearGradient id="{u}accent" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{p['accent1']}"/>
      <stop offset="100%" style="stop-color:{p['accent2']}"/>
    </linearGradient>
    <linearGradient id="{u}title" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f8fafc"/>
      <stop offset="100%" style="stop-color:#cbd5e1"/>
    </linearGradient>
    <linearGradient id="{u}panel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#020810;stop-opacity:0.85"/>
      <stop offset="100%" style="stop-color:#0a0f1e;stop-opacity:0.75"/>
    </linearGradient>
    <radialGradient id="{u}ambientL" cx="20%" cy="50%" r="40%">
      <stop offset="0%" style="stop-color:{p['accent1']};stop-opacity:0.06"/>
      <stop offset="100%" style="stop-color:{p['accent1']};stop-opacity:0"/>
    </radialGradient>
    <radialGradient id="{u}ambientR" cx="70%" cy="45%" r="35%">
      <stop offset="0%" style="stop-color:{p['glow']};stop-opacity:0.08"/>
      <stop offset="100%" style="stop-color:{p['glow']};stop-opacity:0"/>
    </radialGradient>
    <filter id="{u}glow" x="-100%" y="-100%" width="300%" height="300%">
      <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="{p['glow']}" flood-opacity="0.7"/>
    </filter>
    <filter id="{u}blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="12"/>
    </filter>
    <filter id="{u}textglow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{p['accent1']}" flood-opacity="0.5"/>
    </filter>
    <filter id="{u}fxGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feColorMatrix in="b" type="matrix" values="1.2 0.4 0 0 0 0.5 0.6 0 0 0 0 0 0 0 0 0 0 0 0.85 0" result="g"/>
      <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="{u}fxRed" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="8" result="b"/>
      <feColorMatrix in="b" type="matrix" values="1.3 0 0 0 0.7 0 0 0 0 0 0 0 0 0 0 0 0 0 0.95 0" result="g"/>
      <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="{u}sceneGlow1" cx="75%" cy="30%" r="50%">
      <stop offset="0%" stop-color="{p['accent1']}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{p['accent1']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{u}sceneGlow2" cx="60%" cy="70%" r="60%">
      <stop offset="0%" stop-color="{p['accent2']}" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="{p['accent2']}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="{u}dots" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
      <circle cx="15" cy="15" r="1" fill="#1e293b" opacity="0.7"/>
    </pattern>
    <clipPath id="{u}clip">
      <rect x="1" y="1" width="1198" height="628" rx="8" ry="8"/>
    </clipPath>
    <style>
      @keyframes {u}floatUp {{ 0%{{transform:translateY(0);opacity:0.9}} 85%{{opacity:0.5}} 100%{{transform:translateY(-80px);opacity:0}} }}
      @keyframes {u}pulse {{ 0%,100%{{opacity:0.5}} 50%{{opacity:1}} }}
      @keyframes {u}crackFx {{ 0%,100%{{stroke-opacity:0.6}} 50%{{stroke-opacity:1}} }}
      @keyframes {u}glimmer {{ 0%{{opacity:0.3}} 50%{{opacity:0.85}} 100%{{opacity:0.3}} }}
      @keyframes {u}dash {{ to{{stroke-dashoffset:-20}} }}
      @keyframes {u}rotSpin {{ from{{transform:rotate(0deg)}} to{{transform:rotate(360deg)}} }}
      .{u}fa {{ animation: {u}floatUp 3.2s ease-in infinite; }}
      .{u}fb {{ animation: {u}floatUp 3.8s ease-in infinite; animation-delay:0.9s; }}
      .{u}fc {{ animation: {u}floatUp 2.9s ease-in infinite; animation-delay:1.7s; }}
      .{u}crack {{ animation: {u}crackFx 1.9s ease-in-out infinite; }}
      .{u}blink {{ animation: {u}pulse 2.2s ease-in-out infinite; }}
    </style>
  </defs>

  <!-- BACKGROUND -->
  <rect width="1200" height="630" fill="url(#{u}bg)"/>
  <g clip-path="url(#{u}clip)">
    <rect width="1200" height="630" fill="url(#{u}dots)" opacity="0.6"/>
    <rect width="1200" height="630" fill="url(#{u}ambientL)"/>
    <rect width="1200" height="630" fill="url(#{u}ambientR)"/>

    <!-- LEFT PANEL -->
    <rect x="0" y="0" width="370" height="630" fill="url(#{u}panel)"/>
    <rect x="0" y="0" width="4" height="630" fill="url(#{u}accent)"/>

    <!-- Badge -->
    <rect x="40" y="40" width="160" height="28" rx="4" fill="{p['badge_bg']}" stroke="{p['badge_border']}" stroke-width="1.5"/>
    <text x="120" y="58" font-family="Courier New, monospace" font-size="11"
          fill="{p['text_accent']}" text-anchor="middle" letter-spacing="2" font-weight="bold">{p['badge_text']}</text>

    <!-- Date -->
    <text x="40" y="100" font-family="Courier New, monospace" font-size="10"
          fill="#64748b" letter-spacing="1">{date_display}</text>

    <!-- Title -->
{title_svg}
    <!-- Accent divider -->
    <rect x="40" y="{accent_y}" width="260" height="2" rx="1" fill="url(#{u}accent)" opacity="0.8"/>

    <!-- Topic bars -->
{bars_svg}
    <!-- Tag pills -->
{tag_pills}
    <!-- Site URL -->
    <text x="40" y="572" font-family="Courier New, monospace" font-size="10"
          fill="#475569" letter-spacing="0.5">tech.2twodragon.com</text>

    <!-- RIGHT SCENE AREA -->
    <!-- Scene ambient glow overlays -->
    <rect x="380" y="40" width="780" height="550" fill="url(#{u}sceneGlow1)" opacity="0.6"/>
    <rect x="380" y="40" width="780" height="550" fill="url(#{u}sceneGlow2)" opacity="0.5"/>
{scene_svg}
    <!-- COMMON DECORATIONS -->
{decorations_svg}
    <!-- FLOATING PARTICLES -->
{particles}
    <!-- DATA STREAMS -->
{streams}
    <!-- CRT scan line -->
    <rect width="1200" height="2" x="0" y="0" fill="{p['accent1']}" opacity="0">
      <animate attributeName="y" values="-2;632" dur="6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.03;0.03;0" dur="6s" repeatCount="indefinite" keyTimes="0;0.1;0.9;1"/>
    </rect>
  </g>

  <!-- FOOTER -->
  <line x1="40" y1="608" x2="1160" y2="608" stroke="#1e293b" stroke-width="1"/>
  <text x="1160" y="622" font-family="Courier New, monospace" font-size="11"
        fill="#475569" text-anchor="end" letter-spacing="0.5">tech.2twodragon.com</text>

  <!-- BORDER -->
  <rect x="0.5" y="0.5" width="1199" height="629" rx="8" ry="8" fill="none" stroke="#1e293b" stroke-width="1"/>
  <!-- Corner accents -->
  <polyline points="0,25 0,0 25,0" fill="none" stroke="{p['corner']}" stroke-width="2" opacity="0.6"/>
  <polyline points="1175,0 1200,0 1200,25" fill="none" stroke="{p['corner']}" stroke-width="2" opacity="0.6"/>
  <polyline points="0,605 0,630 25,630" fill="none" stroke="{p['accent2']}" stroke-width="2" opacity="0.5"/>
  <polyline points="1175,630 1200,630 1200,605" fill="none" stroke="{p['accent2']}" stroke-width="2" opacity="0.5"/>
</svg>
'''
    return svg


# ---------------------------------------------------------------------------
# Post processing
# ---------------------------------------------------------------------------

def process_post(post_path: Path, dry_run: bool, force: bool) -> tuple[bool, str]:
    """Process a single post. Returns (upgraded, message)."""
    post = frontmatter.load(str(post_path))
    image_field = post.get("image", "")
    if not image_field:
        return False, f"SKIP (no image field): {post_path.name}"

    svg_path = Path(str(image_field).lstrip("/"))
    if not svg_path.suffix == ".svg":
        return False, f"SKIP (not SVG): {post_path.name}"

    if not svg_path.exists():
        return False, f"SKIP (file missing): {svg_path}"

    current_size = svg_path.stat().st_size
    if current_size > SIZE_THRESHOLD and not force:
        return False, f"SKIP (already {current_size / 1024:.1f}KB): {svg_path.name}"

    title = post.get("title", post_path.stem)
    date_val = post.get("date", "")
    tags = post.get("tags", []) or []
    categories = post.get("categories", []) or []
    cat = post.get("category", "")
    if cat and isinstance(cat, str):
        categories = categories + [cat]
    if cat and isinstance(cat, list):
        categories = categories + cat

    theme = detect_theme(tags, categories, title)
    svg_content = generate_svg(
        title=title,
        date_str=str(date_val),
        tags=tags,
        categories=categories,
        theme=theme,
        filepath=str(svg_path),
    )

    old_kb = current_size / 1024
    new_kb = len(svg_content.encode("utf-8")) / 1024

    if dry_run:
        return True, f"DRY-RUN: {svg_path.name} ({old_kb:.1f}KB -> {new_kb:.1f}KB) theme={theme}"

    svg_path.write_text(svg_content, encoding="utf-8")
    return True, f"Upgraded: {svg_path.name} ({old_kb:.1f}KB -> {new_kb:.1f}KB) theme={theme}"


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade blog post SVG images to high-quality templates"
    )
    parser.add_argument("--all", action="store_true",
                        help="Process all posts")
    parser.add_argument("--before", type=str, default=DEFAULT_BEFORE,
                        help=f"Process posts before this date (default: {DEFAULT_BEFORE})")
    parser.add_argument("--post", type=str, default=None,
                        help="Process a specific post filename")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without writing")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite even if SVG is already >15KB")

    args = parser.parse_args()

    if not POSTS_DIR.exists():
        print(f"Error: {POSTS_DIR} not found. Run from project root.", file=sys.stderr)
        sys.exit(1)

    # Collect target posts
    if args.post:
        targets = [POSTS_DIR / args.post]
        if not targets[0].exists():
            print(f"Error: {targets[0]} not found.", file=sys.stderr)
            sys.exit(1)
    else:
        targets = sorted(
            p for p in POSTS_DIR.iterdir()
            if p.suffix == ".md" and p.is_file()
        )
        if not args.all:
            targets = [p for p in targets if p.name < args.before]

    total = len(targets)
    upgraded = 0
    skipped = 0

    print(f"Processing {total} posts (before={args.before}, force={args.force}, dry_run={args.dry_run})")
    print("-" * 70)

    for i, post_path in enumerate(targets, 1):
        success, msg = process_post(post_path, args.dry_run, args.force)
        if success:
            upgraded += 1
        else:
            skipped += 1
        print(f"[{i}/{total}] {msg}")

    print("-" * 70)
    print(f"Done: {upgraded} upgraded, {skipped} skipped out of {total} posts")


if __name__ == "__main__":
    main()
