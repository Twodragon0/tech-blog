#!/usr/bin/env python3
"""
Post Image Quality Improvement Script
Each post gets a unique SVG illustration matching its title and content.
20+ visual templates mapped by topic detection.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("Installing python-frontmatter...")
    os.system(f"{sys.executable} -m pip install python-frontmatter")
    import frontmatter

POSTS_DIR = Path(__file__).parent.parent / "_posts"
IMAGES_DIR = Path(__file__).parent.parent / "assets" / "images"


def escape_svg(text):
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def truncate(text, max_len=48):
    if not text:
        return "Tech Blog Post"
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def wrap_title(title, max_chars=40):
    """Split title into up to 2 lines for better display."""
    if len(title) <= max_chars:
        return [title]
    words = title.split()
    line1 = ""
    for i, w in enumerate(words):
        test = f"{line1} {w}".strip()
        if len(test) > max_chars:
            line2 = " ".join(words[i:])
            if len(line2) > max_chars:
                line2 = line2[: max_chars - 3] + "..."
            return [line1, line2]
        line1 = test
    return [line1]


# ─── VISUAL TEMPLATES ──────────────────────────────────────────────

def _svg_header(title, accent="#3b82f6", accent2="#8b5cf6"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{escape_svg(title)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0e1a"/>
      <stop offset="50%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#0f0a1e"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent2}"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="sg"><feGaussianBlur stdDeviation="30"/></filter>
    <filter id="shadow"><feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000" flood-opacity="0.4"/></filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="200" cy="200" r="250" fill="{accent}" opacity="0.06" filter="url(#sg)"/>
  <circle cx="900" cy="400" r="200" fill="{accent2}" opacity="0.05" filter="url(#sg)"/>'''


def _svg_footer(title, subtitle, date_str, label, accent="#3b82f6"):
    lines = wrap_title(title, 44)
    if len(lines) == 1:
        title_svg = f'  <text x="600" y="505" font-family="Arial,sans-serif" font-size="34" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{escape_svg(lines[0])}</text>'
    else:
        title_svg = f'''  <text x="600" y="490" font-family="Arial,sans-serif" font-size="30" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{escape_svg(lines[0])}</text>
  <text x="600" y="525" font-family="Arial,sans-serif" font-size="30" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{escape_svg(lines[1])}</text>'''

    return f'''
{title_svg}
  <text x="600" y="555" font-family="Arial,sans-serif" font-size="15" fill="#94a3b8" text-anchor="middle">{escape_svg(subtitle)}</text>
  <rect x="40" y="22" width="140" height="32" rx="16" fill="{accent}" opacity="0.25" stroke="{accent}" stroke-width="1"/>
  <text x="110" y="44" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="{accent}" text-anchor="middle">{escape_svg(label)}</text>
  <rect x="1020" y="22" width="140" height="32" rx="16" fill="#3b82f6" opacity="0.2" stroke="#3b82f6" stroke-width="1"/>
  <text x="1090" y="44" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#93c5fd" text-anchor="middle">{escape_svg(date_str)}</text>
  <line x1="50" y1="588" x2="1150" y2="588" stroke="#334155" stroke-width="1" opacity="0.5"/>
  <text x="1150" y="612" font-family="Arial,sans-serif" font-size="13" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>'''


def visual_aws_cloud(title, subtitle, date_str, label):
    """AWS/Cloud - Multi-cloud architecture diagram."""
    h = _svg_header(title, "#f59e0b", "#3b82f6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Central hub -->
    <circle r="50" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
    <text x="0" y="6" font-family="Courier New" font-size="14" font-weight="bold" fill="#fbbf24" text-anchor="middle">CLOUD</text>

    <!-- AWS node -->
    <g transform="translate(-200,-80)">
      <rect x="-55" y="-35" width="110" height="70" rx="14" fill="#0f172a" stroke="#f59e0b" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="-8" font-family="Arial,sans-serif" font-size="22" font-weight="bold" fill="#f59e0b" text-anchor="middle">AWS</text>
      <text x="0" y="14" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">EC2 | S3 | IAM</text>
    </g>
    <!-- GCP node -->
    <g transform="translate(200,-80)">
      <rect x="-55" y="-35" width="110" height="70" rx="14" fill="#0f172a" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="-8" font-family="Arial,sans-serif" font-size="22" font-weight="bold" fill="#60a5fa" text-anchor="middle">GCP</text>
      <text x="0" y="14" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">GKE | IAM</text>
    </g>
    <!-- Security node -->
    <g transform="translate(0,140)">
      <rect x="-65" y="-30" width="130" height="60" rx="14" fill="#0f172a" stroke="#10b981" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="-4" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#34d399" text-anchor="middle">SECURITY</text>
      <text x="0" y="16" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">GuardDuty | WAF</text>
    </g>

    <!-- Connection lines -->
    <line x1="-145" y1="-60" x2="-55" y2="-20" stroke="#475569" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5"/>
    <line x1="145" y1="-60" x2="55" y2="-20" stroke="#475569" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5"/>
    <line x1="0" y1="50" x2="0" y2="110" stroke="#475569" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5"/>

    <!-- Floating particles -->
    <circle cx="-100" cy="60" r="3" fill="#f59e0b" opacity="0.4"/>
    <circle cx="120" cy="40" r="2" fill="#3b82f6" opacity="0.5"/>
    <circle cx="-150" cy="-20" r="2" fill="#10b981" opacity="0.3"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#f59e0b")


def visual_kubernetes(title, subtitle, date_str, label):
    """Kubernetes - Pod/container hexagonal cluster."""
    h = _svg_header(title, "#326ce5", "#7c3aed")
    return h + '''
  <g transform="translate(600,250)">
    <!-- K8s helm wheel -->
    <circle r="100" fill="none" stroke="#326ce5" stroke-width="2" opacity="0.3"/>
    <circle r="65" fill="none" stroke="#326ce5" stroke-width="1.5" opacity="0.4"/>
    <circle r="30" fill="#326ce5" opacity="0.15"/>
    <circle r="12" fill="#326ce5" opacity="0.4"/>

    <!-- 7 spokes -->
    <g stroke="#326ce5" stroke-width="2" opacity="0.5">
      <line x1="0" y1="-30" x2="0" y2="-95"/>
      <line x1="26" y1="-15" x2="82" y2="-48"/>
      <line x1="26" y1="15" x2="82" y2="48"/>
      <line x1="0" y1="30" x2="0" y2="95"/>
      <line x1="-26" y1="15" x2="-82" y2="48"/>
      <line x1="-26" y1="-15" x2="-82" y2="-48"/>
    </g>

    <!-- Pod nodes at spoke ends -->
    <g>
      <rect x="-18" y="-115" width="36" height="36" rx="8" fill="#0f172a" stroke="#326ce5" stroke-width="2"/>
      <text x="0" y="-92" font-family="Courier New" font-size="9" fill="#60a5fa" text-anchor="middle">POD</text>
    </g>
    <g transform="translate(95,-55)">
      <rect x="-18" y="-18" width="36" height="36" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="2"/>
      <text x="0" y="5" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">SVC</text>
    </g>
    <g transform="translate(95,55)">
      <rect x="-18" y="-18" width="36" height="36" rx="8" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <text x="0" y="5" font-family="Courier New" font-size="9" fill="#a78bfa" text-anchor="middle">NS</text>
    </g>
    <g transform="translate(-95,-55)">
      <rect x="-18" y="-18" width="36" height="36" rx="8" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
      <text x="0" y="5" font-family="Courier New" font-size="9" fill="#fbbf24" text-anchor="middle">DPL</text>
    </g>
    <g transform="translate(-95,55)">
      <rect x="-18" y="-18" width="36" height="36" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="2"/>
      <text x="0" y="5" font-family="Courier New" font-size="9" fill="#f87171" text-anchor="middle">SEC</text>
    </g>
    <g transform="translate(0,115)">
      <rect x="-18" y="-18" width="36" height="36" rx="8" fill="#0f172a" stroke="#14b8a6" stroke-width="2"/>
      <text x="0" y="5" font-family="Courier New" font-size="9" fill="#2dd4bf" text-anchor="middle">ING</text>
    </g>

    <!-- Floating labels -->
    <text x="-220" y="-20" font-family="Courier New" font-size="11" fill="#475569">kubectl apply -f</text>
    <text x="160" y="-20" font-family="Courier New" font-size="11" fill="#475569">helm upgrade</text>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#326ce5")


def visual_devsecops(title, subtitle, date_str, label):
    """DevSecOps - Infinity loop pipeline."""
    h = _svg_header(title, "#8b5cf6", "#ec4899")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Infinity loop -->
    <path d="M-180,0 C-180,-90 -60,-90 0,0 C60,90 180,90 180,0 C180,-90 60,-90 0,0 C-60,90 -180,90 -180,0Z"
          fill="none" stroke="#8b5cf6" stroke-width="3" opacity="0.6"/>
    <path d="M-180,0 C-180,-90 -60,-90 0,0 C60,90 180,90 180,0 C180,-90 60,-90 0,0 C-60,90 -180,90 -180,0Z"
          fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="8,6" opacity="0.4"/>

    <!-- Pipeline stages on the loop -->
    <g transform="translate(-140,0)">
      <circle r="28" fill="#0f172a" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="4" font-family="Courier New" font-size="10" fill="#60a5fa" text-anchor="middle">PLAN</text>
    </g>
    <g transform="translate(-55,-55)">
      <circle r="28" fill="#0f172a" stroke="#22c55e" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="4" font-family="Courier New" font-size="10" fill="#4ade80" text-anchor="middle">CODE</text>
    </g>
    <g transform="translate(55,-55)">
      <circle r="28" fill="#0f172a" stroke="#f59e0b" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="4" font-family="Courier New" font-size="10" fill="#fbbf24" text-anchor="middle">BUILD</text>
    </g>
    <g transform="translate(140,0)">
      <circle r="28" fill="#0f172a" stroke="#ef4444" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="4" font-family="Courier New" font-size="10" fill="#f87171" text-anchor="middle">TEST</text>
    </g>
    <g transform="translate(55,55)">
      <circle r="28" fill="#0f172a" stroke="#ec4899" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="4" font-family="Courier New" font-size="10" fill="#f472b6" text-anchor="middle">DEPLOY</text>
    </g>
    <g transform="translate(-55,55)">
      <circle r="28" fill="#0f172a" stroke="#8b5cf6" stroke-width="2" filter="url(#shadow)"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#a78bfa" text-anchor="middle">MONITOR</text>
    </g>

    <!-- Center shield -->
    <path d="M0,-18 L16,-10 L16,6 C16,16 0,22 0,22 C0,22 -16,16 -16,6 L-16,-10 Z"
          fill="#8b5cf6" fill-opacity="0.2" stroke="#a78bfa" stroke-width="1.5"/>
    <text x="0" y="6" font-family="Arial,sans-serif" font-size="8" font-weight="bold" fill="#c4b5fd" text-anchor="middle">SEC</text>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#8b5cf6")


def visual_security_shield(title, subtitle, date_str, label):
    """Security - Advanced shield with layers."""
    h = _svg_header(title, "#ef4444", "#dc2626")
    return h + '''
  <g transform="translate(600,255)">
    <!-- Outer shield -->
    <path d="M0,-150 C90,-150 150,-100 150,0 C150,90 90,170 0,190 C-90,170 -150,90 -150,0 C-150,-100 -90,-150 0,-150Z"
          fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" stroke-width="2" opacity="0.5"/>
    <!-- Inner shield -->
    <path d="M0,-105 C60,-105 105,-70 105,0 C105,60 60,120 0,135 C-60,120 -105,60 -105,0 C-105,-70 -60,-105 0,-105Z"
          fill="#ef4444" fill-opacity="0.06" stroke="#fca5a5" stroke-width="1.5" opacity="0.4"/>

    <!-- Lock icon in center -->
    <rect x="-22" y="-5" width="44" height="35" rx="6" fill="#1e293b" stroke="#ef4444" stroke-width="2"/>
    <path d="M-12,-5 v-16 c0,-18 24,-18 24,0 v16" stroke="#ef4444" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="0" cy="14" r="6" fill="#ef4444"/>
    <rect x="-2" y="16" width="4" height="10" rx="2" fill="#ef4444"/>

    <!-- Scanning rings -->
    <circle r="130" fill="none" stroke="#ef4444" stroke-width="0.5" opacity="0.2" stroke-dasharray="4,8"/>
    <circle r="170" fill="none" stroke="#ef4444" stroke-width="0.5" opacity="0.1" stroke-dasharray="3,12"/>

    <!-- Data flow dots -->
    <circle cx="-120" cy="-40" r="3" fill="#ef4444" opacity="0.5"/>
    <circle cx="130" cy="20" r="3" fill="#fca5a5" opacity="0.4"/>
    <circle cx="-80" cy="100" r="2" fill="#f87171" opacity="0.3"/>
    <circle cx="100" cy="-80" r="2" fill="#ef4444" opacity="0.4"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#ef4444")


def visual_ai_neural(title, subtitle, date_str, label):
    """AI/ML - Neural network visualization."""
    h = _svg_header(title, "#22d3ee", "#8b5cf6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Neural network layers -->
    <!-- Input layer -->
    <g opacity="0.8">
      <circle cx="-200" cy="-80" r="16" fill="#0f172a" stroke="#22d3ee" stroke-width="2"/>
      <circle cx="-200" cy="-20" r="16" fill="#0f172a" stroke="#22d3ee" stroke-width="2"/>
      <circle cx="-200" cy="40" r="16" fill="#0f172a" stroke="#22d3ee" stroke-width="2"/>
      <circle cx="-200" cy="100" r="16" fill="#0f172a" stroke="#22d3ee" stroke-width="2"/>
    </g>
    <!-- Hidden layer 1 -->
    <g opacity="0.8">
      <circle cx="-60" cy="-100" r="16" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <circle cx="-60" cy="-40" r="16" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <circle cx="-60" cy="20" r="16" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <circle cx="-60" cy="80" r="16" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <circle cx="-60" cy="140" r="16" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
    </g>
    <!-- Hidden layer 2 -->
    <g opacity="0.8">
      <circle cx="80" cy="-80" r="16" fill="#0f172a" stroke="#a78bfa" stroke-width="2"/>
      <circle cx="80" cy="-20" r="16" fill="#0f172a" stroke="#a78bfa" stroke-width="2"/>
      <circle cx="80" cy="40" r="16" fill="#0f172a" stroke="#a78bfa" stroke-width="2"/>
      <circle cx="80" cy="100" r="16" fill="#0f172a" stroke="#a78bfa" stroke-width="2"/>
    </g>
    <!-- Output layer -->
    <g opacity="0.8">
      <circle cx="220" cy="-30" r="20" fill="#0f172a" stroke="#ec4899" stroke-width="2.5"/>
      <circle cx="220" cy="50" r="20" fill="#0f172a" stroke="#ec4899" stroke-width="2.5"/>
    </g>

    <!-- Connections (sampled) -->
    <g stroke="#475569" stroke-width="0.8" opacity="0.25">
      <line x1="-184" y1="-80" x2="-76" y2="-100"/>
      <line x1="-184" y1="-80" x2="-76" y2="-40"/>
      <line x1="-184" y1="-20" x2="-76" y2="-40"/>
      <line x1="-184" y1="-20" x2="-76" y2="20"/>
      <line x1="-184" y1="40" x2="-76" y2="20"/>
      <line x1="-184" y1="40" x2="-76" y2="80"/>
      <line x1="-184" y1="100" x2="-76" y2="80"/>
      <line x1="-184" y1="100" x2="-76" y2="140"/>
      <line x1="-44" y1="-100" x2="64" y2="-80"/>
      <line x1="-44" y1="-40" x2="64" y2="-20"/>
      <line x1="-44" y1="20" x2="64" y2="40"/>
      <line x1="-44" y1="80" x2="64" y2="100"/>
      <line x1="-44" y1="140" x2="64" y2="40"/>
      <line x1="96" y1="-80" x2="200" y2="-30"/>
      <line x1="96" y1="-20" x2="200" y2="-30"/>
      <line x1="96" y1="40" x2="200" y2="50"/>
      <line x1="96" y1="100" x2="200" y2="50"/>
    </g>

    <!-- Highlighted active connections -->
    <g stroke="#22d3ee" stroke-width="1.5" opacity="0.4">
      <line x1="-184" y1="-20" x2="-76" y2="-40"/>
      <line x1="-44" y1="-40" x2="64" y2="-20"/>
      <line x1="96" y1="-20" x2="200" y2="-30"/>
    </g>

    <!-- Labels -->
    <text x="-200" y="145" font-family="Courier New" font-size="10" fill="#22d3ee" text-anchor="middle">INPUT</text>
    <text x="-60" y="175" font-family="Courier New" font-size="10" fill="#8b5cf6" text-anchor="middle">HIDDEN</text>
    <text x="220" y="95" font-family="Courier New" font-size="10" fill="#ec4899" text-anchor="middle">OUTPUT</text>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#22d3ee")


def visual_blockchain(title, subtitle, date_str, label):
    """Blockchain/Crypto - Chain of blocks."""
    h = _svg_header(title, "#8b5cf6", "#f59e0b")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Block chain -->
    <g filter="url(#shadow)">
      <rect x="-320" y="-50" width="120" height="100" rx="12" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <text x="-260" y="-20" font-family="Courier New" font-size="11" font-weight="bold" fill="#a78bfa" text-anchor="middle">BLOCK #N-2</text>
      <text x="-260" y="2" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">hash: 0x7f3a...</text>
      <text x="-260" y="18" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">prev: 0x2e1b...</text>
      <rect x="-310" y="28" width="100" height="4" rx="2" fill="#8b5cf6" opacity="0.3"/>
    </g>

    <g filter="url(#shadow)">
      <rect x="-110" y="-50" width="120" height="100" rx="12" fill="#0f172a" stroke="#a78bfa" stroke-width="2"/>
      <text x="-50" y="-20" font-family="Courier New" font-size="11" font-weight="bold" fill="#c4b5fd" text-anchor="middle">BLOCK #N-1</text>
      <text x="-50" y="2" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">hash: 0x2e1b...</text>
      <text x="-50" y="18" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">prev: 0x9c4d...</text>
      <rect x="-100" y="28" width="100" height="4" rx="2" fill="#a78bfa" opacity="0.3"/>
    </g>

    <g filter="url(#shadow)">
      <rect x="100" y="-50" width="120" height="100" rx="12" fill="#0f172a" stroke="#f59e0b" stroke-width="2.5"/>
      <text x="160" y="-20" font-family="Courier New" font-size="11" font-weight="bold" fill="#fbbf24" text-anchor="middle">BLOCK #N</text>
      <text x="160" y="2" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">hash: 0x9c4d...</text>
      <text x="160" y="18" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">prev: 0x7f3a...</text>
      <rect x="110" y="28" width="100" height="4" rx="2" fill="#f59e0b" opacity="0.4"/>
    </g>

    <!-- Chain links -->
    <g stroke="#475569" stroke-width="2" opacity="0.6">
      <line x1="-200" y1="0" x2="-110" y2="0"/>
      <line x1="10" y1="0" x2="100" y2="0"/>
    </g>
    <circle cx="-155" cy="0" r="4" fill="#8b5cf6" opacity="0.6"/>
    <circle cx="55" cy="0" r="4" fill="#a78bfa" opacity="0.6"/>

    <!-- Mining indicator -->
    <g transform="translate(290,0)" opacity="0.5">
      <rect x="-30" y="-25" width="60" height="50" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3"/>
      <text x="0" y="4" font-family="Courier New" font-size="8" fill="#4ade80" text-anchor="middle">NEXT</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#8b5cf6")


def visual_tesla_automotive(title, subtitle, date_str, label):
    """Tesla/Automotive - Car with connectivity lines."""
    h = _svg_header(title, "#ef4444", "#3b82f6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Car silhouette (simplified top view) -->
    <path d="M-120,-30 C-120,-80 -80,-100 0,-100 C80,-100 120,-80 120,-30 L130,50 C130,80 80,100 0,100 C-80,100 -130,80 -130,50 Z"
          fill="#1e293b" stroke="#ef4444" stroke-width="2" opacity="0.8"/>
    <!-- Windshield -->
    <path d="M-60,-70 C-40,-75 40,-75 60,-70 L50,-30 L-50,-30 Z"
          fill="#ef4444" fill-opacity="0.1" stroke="#ef4444" stroke-width="1" opacity="0.5"/>
    <!-- Wheels -->
    <circle cx="-100" cy="-20" r="18" fill="#0f172a" stroke="#475569" stroke-width="2"/>
    <circle cx="100" cy="-20" r="18" fill="#0f172a" stroke="#475569" stroke-width="2"/>
    <circle cx="-100" cy="60" r="18" fill="#0f172a" stroke="#475569" stroke-width="2"/>
    <circle cx="100" cy="60" r="18" fill="#0f172a" stroke="#475569" stroke-width="2"/>

    <!-- Connectivity waves -->
    <g opacity="0.4">
      <path d="M0,-110 Q-30,-140 -10,-170" fill="none" stroke="#3b82f6" stroke-width="1.5"/>
      <path d="M0,-110 Q0,-145 0,-175" fill="none" stroke="#3b82f6" stroke-width="1.5"/>
      <path d="M0,-110 Q30,-140 10,-170" fill="none" stroke="#3b82f6" stroke-width="1.5"/>
    </g>

    <!-- Sensor indicators -->
    <g fill="#22d3ee" opacity="0.6">
      <circle cx="0" cy="-100" r="4"/>
      <circle cx="-120" cy="20" r="3"/>
      <circle cx="120" cy="20" r="3"/>
      <circle cx="0" cy="100" r="3"/>
    </g>

    <!-- Labels -->
    <text x="0" y="10" font-family="Courier New" font-size="11" fill="#ef4444" text-anchor="middle" opacity="0.8">FSD v13</text>
    <text x="0" y="28" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">SECURED</text>

    <!-- Side modules -->
    <g transform="translate(-220,0)">
      <rect x="-40" y="-20" width="80" height="40" rx="8" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#60a5fa" text-anchor="middle">OTA</text>
    </g>
    <g transform="translate(220,0)">
      <rect x="-40" y="-20" width="80" height="40" rx="8" fill="#0f172a" stroke="#22d3ee" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#67e8f9" text-anchor="middle">LIDAR</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#ef4444")


def visual_incident(title, subtitle, date_str, label):
    """Incident/Post-Mortem - Alert timeline."""
    h = _svg_header(title, "#ef4444", "#f59e0b")
    return h + '''
  <g transform="translate(600,240)">
    <!-- Alert triangle -->
    <path d="M0,-120 L100,-10 L-100,-10 Z" fill="#ef4444" fill-opacity="0.08" stroke="#ef4444" stroke-width="2" opacity="0.6"/>
    <text x="0" y="-30" font-family="Arial,sans-serif" font-size="48" font-weight="bold" fill="#ef4444" text-anchor="middle" opacity="0.7">!</text>

    <!-- Timeline -->
    <line x1="-280" y1="60" x2="280" y2="60" stroke="#475569" stroke-width="2" opacity="0.5"/>

    <!-- Timeline events -->
    <g transform="translate(-200,60)">
      <circle r="10" fill="#ef4444" opacity="0.8"/>
      <text x="0" y="30" font-family="Courier New" font-size="9" fill="#f87171" text-anchor="middle">DETECT</text>
      <text x="0" y="45" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">T+0m</text>
    </g>
    <g transform="translate(-70,60)">
      <circle r="10" fill="#f59e0b" opacity="0.8"/>
      <text x="0" y="30" font-family="Courier New" font-size="9" fill="#fbbf24" text-anchor="middle">RESPOND</text>
      <text x="0" y="45" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">T+15m</text>
    </g>
    <g transform="translate(70,60)">
      <circle r="10" fill="#3b82f6" opacity="0.8"/>
      <text x="0" y="30" font-family="Courier New" font-size="9" fill="#60a5fa" text-anchor="middle">MITIGATE</text>
      <text x="0" y="45" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">T+45m</text>
    </g>
    <g transform="translate(200,60)">
      <circle r="10" fill="#22c55e" opacity="0.8"/>
      <text x="0" y="30" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">RESOLVE</text>
      <text x="0" y="45" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">T+2h</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#ef4444")


def visual_npm_supply_chain(title, subtitle, date_str, label):
    """npm/Supply Chain - Package dependency tree with warning."""
    h = _svg_header(title, "#cb3837", "#f59e0b")
    return h + '''
  <g transform="translate(600,250)">
    <!-- Central package -->
    <g filter="url(#shadow)">
      <rect x="-50" y="-40" width="100" height="80" rx="12" fill="#0f172a" stroke="#cb3837" stroke-width="2.5"/>
      <text x="0" y="-10" font-family="Courier New" font-size="14" font-weight="bold" fill="#ef4444" text-anchor="middle">npm</text>
      <text x="0" y="12" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">package</text>
      <!-- Warning badge -->
      <circle cx="40" cy="-30" r="12" fill="#ef4444"/>
      <text x="40" y="-26" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">!</text>
    </g>

    <!-- Dependency branches -->
    <g opacity="0.7">
      <!-- Left branch -->
      <line x1="-50" y1="-10" x2="-140" y2="-70" stroke="#475569" stroke-width="1.5"/>
      <rect x="-190" y="-95" width="100" height="50" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="1.5"/>
      <text x="-140" y="-67" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">lodash@4.x</text>

      <line x1="-50" y1="10" x2="-160" y2="70" stroke="#475569" stroke-width="1.5"/>
      <rect x="-210" y="45" width="100" height="50" rx="8" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="-160" y="73" font-family="Courier New" font-size="9" fill="#fbbf24" text-anchor="middle">axios@1.x</text>
      <circle cx="-120" cy="55" r="8" fill="#f59e0b" opacity="0.3"/>

      <!-- Right branch -->
      <line x1="50" y1="-10" x2="140" y2="-70" stroke="#475569" stroke-width="1.5"/>
      <rect x="90" y="-95" width="100" height="50" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="1.5"/>
      <text x="140" y="-67" font-family="Courier New" font-size="9" fill="#f87171" text-anchor="middle">MALICIOUS</text>
      <circle cx="180" cy="-85" r="8" fill="#ef4444" opacity="0.6"/>

      <line x1="50" y1="10" x2="160" y2="70" stroke="#475569" stroke-width="1.5"/>
      <rect x="110" y="45" width="100" height="50" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="1.5"/>
      <text x="160" y="73" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">express@4.x</text>
    </g>

    <!-- Scan indicator -->
    <circle r="160" fill="none" stroke="#ef4444" stroke-width="0.8" opacity="0.15" stroke-dasharray="6,8"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#cb3837")


def visual_email(title, subtitle, date_str, label):
    """Email/DKIM/SPF - Email authentication flow."""
    h = _svg_header(title, "#3b82f6", "#22c55e")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Envelope -->
    <rect x="-100" y="-60" width="200" height="120" rx="12" fill="#0f172a" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
    <path d="M-100,-60 L0,20 L100,-60" fill="none" stroke="#3b82f6" stroke-width="2"/>
    <text x="0" y="40" font-family="Courier New" font-size="10" fill="#64748b" text-anchor="middle">FROM: verified@domain.com</text>

    <!-- Authentication badges -->
    <g transform="translate(-200,-30)">
      <rect x="-40" y="-25" width="80" height="50" rx="10" fill="#0f172a" stroke="#22c55e" stroke-width="2"/>
      <text x="0" y="-4" font-family="Courier New" font-size="12" font-weight="bold" fill="#4ade80" text-anchor="middle">SPF</text>
      <text x="0" y="14" font-family="Courier New" font-size="8" fill="#4ade80" text-anchor="middle">PASS</text>
    </g>
    <g transform="translate(200,-30)">
      <rect x="-40" y="-25" width="80" height="50" rx="10" fill="#0f172a" stroke="#22c55e" stroke-width="2"/>
      <text x="0" y="-4" font-family="Courier New" font-size="12" font-weight="bold" fill="#4ade80" text-anchor="middle">DKIM</text>
      <text x="0" y="14" font-family="Courier New" font-size="8" fill="#4ade80" text-anchor="middle">PASS</text>
    </g>
    <g transform="translate(0,130)">
      <rect x="-50" y="-22" width="100" height="44" rx="10" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
      <text x="0" y="-2" font-family="Courier New" font-size="12" font-weight="bold" fill="#fbbf24" text-anchor="middle">DMARC</text>
      <text x="0" y="14" font-family="Courier New" font-size="8" fill="#fbbf24" text-anchor="middle">ALIGNED</text>
    </g>

    <!-- Flow arrows -->
    <line x1="-160" y1="-10" x2="-105" y2="-10" stroke="#475569" stroke-width="1.5" opacity="0.5"/>
    <line x1="105" y1="-10" x2="160" y2="-10" stroke="#475569" stroke-width="1.5" opacity="0.5"/>
    <line x1="0" y1="60" x2="0" y2="108" stroke="#475569" stroke-width="1.5" opacity="0.5"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#3b82f6")


def visual_owasp(title, subtitle, date_str, label):
    """OWASP - Top 10 ranking bars."""
    h = _svg_header(title, "#ef4444", "#f59e0b")
    risks = [
        ("A01 Broken Access", 95, "#ef4444"),
        ("A02 Crypto Failures", 88, "#f97316"),
        ("A03 Injection", 82, "#f59e0b"),
        ("A04 Insecure Design", 76, "#eab308"),
        ("A05 Misconfiguration", 70, "#22c55e"),
    ]
    bars = ""
    for i, (name, score, color) in enumerate(risks):
        y = -100 + i * 52
        w = score * 2.8
        bars += f'''
    <text x="-250" y="{y + 4}" font-family="Courier New" font-size="11" fill="#94a3b8" text-anchor="start">{name}</text>
    <rect x="30" y="{y - 10}" width="{w}" height="22" rx="4" fill="{color}" opacity="0.3"/>
    <rect x="30" y="{y - 10}" width="{w}" height="22" rx="4" fill="{color}" opacity="0.15"/>
    <text x="{35 + w}" y="{y + 5}" font-family="Courier New" font-size="10" fill="{color}">{score}%</text>'''

    return h + f'''
  <g transform="translate(600,270)">
    {bars}
    <text x="-250" y="-140" font-family="Courier New" font-size="14" font-weight="bold" fill="#f87171">OWASP TOP 10 RISK MATRIX</text>
    <line x1="-250" y1="-120" x2="300" y2="-120" stroke="#334155" stroke-width="1" opacity="0.5"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#ef4444")


def visual_cicd(title, subtitle, date_str, label):
    """CI/CD Pipeline - Stage flow."""
    h = _svg_header(title, "#22c55e", "#3b82f6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Pipeline flow -->
    <line x1="-350" y1="0" x2="350" y2="0" stroke="#334155" stroke-width="3" opacity="0.4"/>

    <!-- Stages -->
    <g transform="translate(-250,0)" filter="url(#shadow)">
      <rect x="-50" y="-35" width="100" height="70" rx="12" fill="#0f172a" stroke="#3b82f6" stroke-width="2"/>
      <text x="0" y="-6" font-family="Courier New" font-size="11" font-weight="bold" fill="#60a5fa" text-anchor="middle">SOURCE</text>
      <text x="0" y="12" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">git push</text>
    </g>
    <g transform="translate(-80,0)" filter="url(#shadow)">
      <rect x="-55" y="-35" width="110" height="70" rx="12" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
      <text x="0" y="-6" font-family="Courier New" font-size="11" font-weight="bold" fill="#fbbf24" text-anchor="middle">BUILD</text>
      <text x="0" y="12" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">docker build</text>
    </g>
    <g transform="translate(90,0)" filter="url(#shadow)">
      <rect x="-50" y="-35" width="100" height="70" rx="12" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <text x="0" y="-6" font-family="Courier New" font-size="11" font-weight="bold" fill="#a78bfa" text-anchor="middle">TEST</text>
      <text x="0" y="12" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">pytest / jest</text>
    </g>
    <g transform="translate(260,0)" filter="url(#shadow)">
      <rect x="-55" y="-35" width="110" height="70" rx="12" fill="#0f172a" stroke="#22c55e" stroke-width="2.5"/>
      <text x="0" y="-6" font-family="Courier New" font-size="11" font-weight="bold" fill="#4ade80" text-anchor="middle">DEPLOY</text>
      <text x="0" y="12" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">k8s apply</text>
    </g>

    <!-- Arrows -->
    <polygon points="-195,0 -180,-8 -180,8" fill="#3b82f6" opacity="0.6"/>
    <polygon points="-20,0 -5,-8 -5,8" fill="#f59e0b" opacity="0.6"/>
    <polygon points="145,0 160,-8 160,8" fill="#8b5cf6" opacity="0.6"/>

    <!-- Security scan badge -->
    <g transform="translate(0,-90)" opacity="0.7">
      <rect x="-60" y="-16" width="120" height="32" rx="16" fill="#ef4444" opacity="0.15" stroke="#ef4444" stroke-width="1"/>
      <text x="0" y="4" font-family="Courier New" font-size="10" fill="#f87171" text-anchor="middle">SECURITY SCAN</text>
    </g>
    <line x1="0" y1="-58" x2="-80" y2="-35" stroke="#ef4444" stroke-width="1" stroke-dasharray="4,3" opacity="0.3"/>
    <line x1="0" y1="-58" x2="90" y2="-35" stroke="#ef4444" stroke-width="1" stroke-dasharray="4,3" opacity="0.3"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#22c55e")


def visual_finops(title, subtitle, date_str, label):
    """FinOps - Cost optimization chart."""
    h = _svg_header(title, "#14b8a6", "#3b82f6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Chart area -->
    <line x1="-250" y1="100" x2="250" y2="100" stroke="#334155" stroke-width="1.5"/>
    <line x1="-250" y1="-120" x2="-250" y2="100" stroke="#334155" stroke-width="1.5"/>

    <!-- Cost bars (before) -->
    <g opacity="0.6">
      <rect x="-220" y="-80" width="50" height="180" rx="4" fill="#ef4444" opacity="0.4"/>
      <rect x="-150" y="-40" width="50" height="140" rx="4" fill="#ef4444" opacity="0.4"/>
      <rect x="-80" y="-100" width="50" height="200" rx="4" fill="#ef4444" opacity="0.4"/>
    </g>
    <!-- Cost bars (after optimization) -->
    <g opacity="0.8">
      <rect x="-10" y="10" width="50" height="90" rx="4" fill="#14b8a6"/>
      <rect x="60" y="30" width="50" height="70" rx="4" fill="#14b8a6"/>
      <rect x="130" y="-10" width="50" height="110" rx="4" fill="#14b8a6"/>
    </g>

    <!-- Arrow showing savings -->
    <path d="M20,-50 C40,-80 120,-80 140,-50" fill="none" stroke="#22c55e" stroke-width="2"/>
    <text x="80" y="-90" font-family="Courier New" font-size="14" font-weight="bold" fill="#4ade80" text-anchor="middle">-40% COST</text>

    <!-- Labels -->
    <text x="-150" y="125" font-family="Courier New" font-size="10" fill="#94a3b8" text-anchor="middle">BEFORE</text>
    <text x="90" y="125" font-family="Courier New" font-size="10" fill="#14b8a6" text-anchor="middle">AFTER</text>

    <!-- Dollar sign -->
    <g transform="translate(220,-60)" opacity="0.5">
      <circle r="30" fill="#14b8a6" opacity="0.15" stroke="#14b8a6" stroke-width="1.5"/>
      <text x="0" y="10" font-family="Arial,sans-serif" font-size="28" font-weight="bold" fill="#2dd4bf" text-anchor="middle">$</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#14b8a6")


def visual_zscaler_network(title, subtitle, date_str, label):
    """Zscaler/Network Security - Zero Trust network."""
    h = _svg_header(title, "#0ea5e9", "#8b5cf6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Central Zscaler cloud -->
    <ellipse cx="0" cy="0" rx="80" ry="50" fill="#0f172a" stroke="#0ea5e9" stroke-width="2.5" filter="url(#shadow)"/>
    <text x="0" y="-8" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">ZERO</text>
    <text x="0" y="14" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="#38bdf8" text-anchor="middle">TRUST</text>

    <!-- User endpoints -->
    <g transform="translate(-240,-60)">
      <rect x="-35" y="-25" width="70" height="50" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">USER</text>
    </g>
    <g transform="translate(-240,60)">
      <rect x="-35" y="-25" width="70" height="50" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">MOBILE</text>
    </g>

    <!-- Cloud apps -->
    <g transform="translate(240,-60)">
      <rect x="-35" y="-25" width="70" height="50" rx="8" fill="#0f172a" stroke="#8b5cf6" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#a78bfa" text-anchor="middle">SaaS</text>
    </g>
    <g transform="translate(240,60)">
      <rect x="-35" y="-25" width="70" height="50" rx="8" fill="#0f172a" stroke="#8b5cf6" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#a78bfa" text-anchor="middle">DC</text>
    </g>

    <!-- SSL inspection indicator -->
    <g transform="translate(0,100)" opacity="0.6">
      <rect x="-45" y="-14" width="90" height="28" rx="14" fill="#f59e0b" opacity="0.2" stroke="#f59e0b" stroke-width="1"/>
      <text x="0" y="4" font-family="Courier New" font-size="9" fill="#fbbf24" text-anchor="middle">SSL INSPECT</text>
    </g>

    <!-- Encrypted tunnels -->
    <g stroke="#0ea5e9" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.4">
      <line x1="-170" y1="-50" x2="-80" y2="-20"/>
      <line x1="-170" y1="60" x2="-80" y2="20"/>
      <line x1="80" y1="-20" x2="170" y2="-50"/>
      <line x1="80" y1="20" x2="170" y2="60"/>
    </g>

    <!-- Blocked threats -->
    <g transform="translate(0,-100)" opacity="0.5">
      <line x1="-15" y1="-15" x2="15" y2="15" stroke="#ef4444" stroke-width="3"/>
      <line x1="15" y1="-15" x2="-15" y2="15" stroke="#ef4444" stroke-width="3"/>
      <text x="30" y="4" font-family="Courier New" font-size="9" fill="#f87171">BLOCKED</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#0ea5e9")


def visual_isms_compliance(title, subtitle, date_str, label):
    """ISMS-P/Compliance - Certification badge with checklist."""
    h = _svg_header(title, "#22c55e", "#3b82f6")
    return h + '''
  <g transform="translate(600,250)">
    <!-- Certificate badge -->
    <circle r="90" fill="#22c55e" opacity="0.06" filter="url(#sg)"/>
    <circle r="70" fill="#0f172a" stroke="#22c55e" stroke-width="2.5" filter="url(#shadow)"/>
    <path d="M0,-40 L8,-15 L35,-15 L14,2 L22,28 L0,14 L-22,28 L-14,2 L-35,-15 L-8,-15 Z"
          fill="#22c55e" opacity="0.3"/>
    <text x="0" y="55" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#4ade80" text-anchor="middle">CERTIFIED</text>

    <!-- Checklist -->
    <g transform="translate(-220,-60)">
      <rect x="-70" y="-60" width="140" height="180" rx="12" fill="#0f172a" stroke="#334155" stroke-width="1.5" filter="url(#shadow)"/>
      <text x="0" y="-35" font-family="Courier New" font-size="10" font-weight="bold" fill="#94a3b8" text-anchor="middle">AUDIT CHECKLIST</text>
      <g transform="translate(-50,-10)" fill="#4ade80" font-family="Courier New" font-size="10">
        <text y="0" fill="#4ade80">&#10003; Access Control</text>
        <text y="22" fill="#4ade80">&#10003; Encryption</text>
        <text y="44" fill="#4ade80">&#10003; Logging</text>
        <text y="66" fill="#fbbf24">&#9679; Monitoring</text>
        <text y="88" fill="#64748b">&#9675; DR Plan</text>
      </g>
    </g>

    <!-- Compliance scores -->
    <g transform="translate(220,-20)">
      <rect x="-65" y="-60" width="130" height="140" rx="12" fill="#0f172a" stroke="#334155" stroke-width="1.5" filter="url(#shadow)"/>
      <text x="0" y="-35" font-family="Courier New" font-size="10" font-weight="bold" fill="#94a3b8" text-anchor="middle">COMPLIANCE</text>
      <text x="0" y="5" font-family="Arial,sans-serif" font-size="36" font-weight="bold" fill="#4ade80" text-anchor="middle">92%</text>
      <rect x="-45" y="25" width="90" height="8" rx="4" fill="#1e293b"/>
      <rect x="-45" y="25" width="82" height="8" rx="4" fill="#22c55e" opacity="0.6"/>
      <text x="0" y="52" font-family="Courier New" font-size="9" fill="#64748b" text-anchor="middle">ISMS-P Ready</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#22c55e")


def visual_docker(title, subtitle, date_str, label):
    """Docker/Container - Container stack visualization."""
    h = _svg_header(title, "#2496ed", "#0ea5e9")
    return h + '''
  <g transform="translate(600,250)">
    <!-- Docker whale simplified -->
    <g transform="translate(0,-40)" opacity="0.6">
      <!-- Container boxes on whale back -->
      <rect x="-70" y="-40" width="28" height="24" rx="3" fill="#2496ed" opacity="0.5" stroke="#2496ed" stroke-width="1.5"/>
      <rect x="-38" y="-40" width="28" height="24" rx="3" fill="#2496ed" opacity="0.6" stroke="#2496ed" stroke-width="1.5"/>
      <rect x="-6" y="-40" width="28" height="24" rx="3" fill="#2496ed" opacity="0.7" stroke="#2496ed" stroke-width="1.5"/>
      <rect x="26" y="-40" width="28" height="24" rx="3" fill="#2496ed" opacity="0.8" stroke="#2496ed" stroke-width="1.5"/>
      <rect x="-38" y="-68" width="28" height="24" rx="3" fill="#2496ed" opacity="0.4" stroke="#2496ed" stroke-width="1.5"/>
      <rect x="-6" y="-68" width="28" height="24" rx="3" fill="#2496ed" opacity="0.5" stroke="#2496ed" stroke-width="1.5"/>
      <!-- Whale body -->
      <path d="M-80,-12 C-120,-12 -130,20 -100,35 C-80,45 60,45 80,35 C100,25 90,0 70,-12 Z"
            fill="#1e293b" stroke="#2496ed" stroke-width="2"/>
      <!-- Whale tail -->
      <path d="M-100,25 C-130,10 -150,-10 -140,-35 C-130,-25 -120,-15 -100,0"
            fill="#1e293b" stroke="#2496ed" stroke-width="2"/>
    </g>

    <!-- Layer stack below -->
    <g transform="translate(0,80)">
      <rect x="-150" y="0" width="300" height="30" rx="6" fill="#0f172a" stroke="#22c55e" stroke-width="1.5"/>
      <text x="0" y="20" font-family="Courier New" font-size="10" fill="#4ade80" text-anchor="middle">APPLICATION LAYER</text>
      <rect x="-150" y="36" width="300" height="30" rx="6" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="0" y="56" font-family="Courier New" font-size="10" fill="#60a5fa" text-anchor="middle">RUNTIME LAYER</text>
      <rect x="-150" y="72" width="300" height="30" rx="6" fill="#0f172a" stroke="#8b5cf6" stroke-width="1.5"/>
      <text x="0" y="92" font-family="Courier New" font-size="10" fill="#a78bfa" text-anchor="middle">OS / KERNEL</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#2496ed")


def visual_conference(title, subtitle, date_str, label):
    """Conference/Review - Multi-event presentation."""
    h = _svg_header(title, "#f59e0b", "#8b5cf6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Presentation cards -->
    <g transform="translate(-180,-30)" filter="url(#shadow)">
      <rect x="-80" y="-70" width="160" height="140" rx="14" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
      <rect x="-65" y="-55" width="130" height="8" rx="4" fill="#f59e0b" opacity="0.3"/>
      <rect x="-65" y="-38" width="90" height="6" rx="3" fill="#334155"/>
      <rect x="-65" y="-24" width="110" height="6" rx="3" fill="#334155"/>
      <rect x="-65" y="-10" width="70" height="6" rx="3" fill="#334155"/>
      <circle cx="0" cy="35" r="20" fill="#f59e0b" opacity="0.15"/>
      <text x="0" y="40" font-family="Arial,sans-serif" font-size="14" fill="#fbbf24" text-anchor="middle">1</text>
    </g>

    <g transform="translate(0,-30)" filter="url(#shadow)">
      <rect x="-80" y="-70" width="160" height="140" rx="14" fill="#0f172a" stroke="#8b5cf6" stroke-width="2"/>
      <rect x="-65" y="-55" width="130" height="8" rx="4" fill="#8b5cf6" opacity="0.3"/>
      <rect x="-65" y="-38" width="100" height="6" rx="3" fill="#334155"/>
      <rect x="-65" y="-24" width="80" height="6" rx="3" fill="#334155"/>
      <rect x="-65" y="-10" width="110" height="6" rx="3" fill="#334155"/>
      <circle cx="0" cy="35" r="20" fill="#8b5cf6" opacity="0.15"/>
      <text x="0" y="40" font-family="Arial,sans-serif" font-size="14" fill="#a78bfa" text-anchor="middle">2</text>
    </g>

    <g transform="translate(180,-30)" filter="url(#shadow)">
      <rect x="-80" y="-70" width="160" height="140" rx="14" fill="#0f172a" stroke="#3b82f6" stroke-width="2"/>
      <rect x="-65" y="-55" width="130" height="8" rx="4" fill="#3b82f6" opacity="0.3"/>
      <rect x="-65" y="-38" width="90" height="6" rx="3" fill="#334155"/>
      <rect x="-65" y="-24" width="120" height="6" rx="3" fill="#334155"/>
      <rect x="-65" y="-10" width="60" height="6" rx="3" fill="#334155"/>
      <circle cx="0" cy="35" r="20" fill="#3b82f6" opacity="0.15"/>
      <text x="0" y="40" font-family="Arial,sans-serif" font-size="14" fill="#60a5fa" text-anchor="middle">3</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#f59e0b")


def visual_ransomware(title, subtitle, date_str, label):
    """Ransomware - Lock with ransom warning."""
    h = _svg_header(title, "#dc2626", "#f59e0b")
    return h + '''
  <g transform="translate(600,250)">
    <!-- Giant padlock -->
    <rect x="-60" y="-10" width="120" height="90" rx="14" fill="#1e293b" stroke="#dc2626" stroke-width="3" filter="url(#shadow)"/>
    <path d="M-35,-10 v-40 c0,-50 70,-50 70,0 v40" stroke="#dc2626" stroke-width="5" fill="none" stroke-linecap="round"/>
    <circle cx="0" cy="35" r="14" fill="#dc2626"/>
    <rect x="-4" y="40" width="8" height="20" rx="4" fill="#dc2626"/>

    <!-- Encrypted file icons -->
    <g transform="translate(-200,-30)" opacity="0.6">
      <rect x="-25" y="-30" width="50" height="60" rx="6" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="0" y="-5" font-family="Courier New" font-size="16" fill="#fbbf24" text-anchor="middle">.enc</text>
      <text x="0" y="15" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">LOCKED</text>
    </g>
    <g transform="translate(200,-30)" opacity="0.6">
      <rect x="-25" y="-30" width="50" height="60" rx="6" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="0" y="-5" font-family="Courier New" font-size="16" fill="#fbbf24" text-anchor="middle">.enc</text>
      <text x="0" y="15" font-family="Courier New" font-size="8" fill="#64748b" text-anchor="middle">LOCKED</text>
    </g>

    <!-- Ransom demand -->
    <g transform="translate(0,140)" opacity="0.7">
      <rect x="-120" y="-18" width="240" height="36" rx="8" fill="#dc2626" opacity="0.15" stroke="#dc2626" stroke-width="1.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="12" font-weight="bold" fill="#f87171" text-anchor="middle">THREAT DETECTED - RESPOND NOW</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#dc2626")


def visual_macos_mdm(title, subtitle, date_str, label):
    """macOS/MDM - Device management dashboard."""
    h = _svg_header(title, "#a855f7", "#3b82f6")
    return h + '''
  <g transform="translate(600,250)">
    <!-- MacBook outline -->
    <rect x="-140" y="-100" width="280" height="170" rx="12" fill="#0f172a" stroke="#a855f7" stroke-width="2" filter="url(#shadow)"/>
    <rect x="-120" y="-85" width="240" height="130" rx="4" fill="#111827"/>
    <!-- Screen content -->
    <rect x="-108" y="-75" width="216" height="110" rx="2" fill="#0f172a"/>
    <text x="0" y="-55" font-family="Courier New" font-size="10" font-weight="bold" fill="#a855f7" text-anchor="middle">MDM DASHBOARD</text>
    <!-- Status bars -->
    <rect x="-95" y="-38" width="100" height="8" rx="4" fill="#22c55e" opacity="0.4"/>
    <rect x="-95" y="-24" width="80" height="8" rx="4" fill="#22c55e" opacity="0.3"/>
    <rect x="-95" y="-10" width="120" height="8" rx="4" fill="#f59e0b" opacity="0.3"/>
    <rect x="-95" y="4" width="60" height="8" rx="4" fill="#3b82f6" opacity="0.3"/>
    <!-- Compliance indicator -->
    <circle cx="70" cy="-10" r="22" fill="#22c55e" opacity="0.15" stroke="#22c55e" stroke-width="1.5"/>
    <text x="70" y="-5" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#4ade80" text-anchor="middle">98</text>
    <text x="70" y="10" font-family="Courier New" font-size="7" fill="#64748b" text-anchor="middle">SCORE</text>

    <!-- Base -->
    <path d="M-160,70 L-140,85 L140,85 L160,70" fill="#1e293b" stroke="#475569" stroke-width="1"/>

    <!-- Side devices -->
    <g transform="translate(-230,20)" opacity="0.5">
      <rect x="-20" y="-35" width="40" height="70" rx="6" fill="#0f172a" stroke="#a855f7" stroke-width="1.5"/>
      <text x="0" y="5" font-family="Courier New" font-size="7" fill="#c084fc" text-anchor="middle">iPHONE</text>
    </g>
    <g transform="translate(230,20)" opacity="0.5">
      <rect x="-25" y="-30" width="50" height="60" rx="6" fill="#0f172a" stroke="#a855f7" stroke-width="1.5"/>
      <text x="0" y="5" font-family="Courier New" font-size="7" fill="#c084fc" text-anchor="middle">iPAD</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#a855f7")


def visual_cloudflare(title, subtitle, date_str, label):
    """Cloudflare - CDN/WAF node network."""
    h = _svg_header(title, "#f6821f", "#3b82f6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Central Cloudflare node -->
    <circle r="50" fill="#0f172a" stroke="#f6821f" stroke-width="2.5" filter="url(#shadow)"/>
    <text x="0" y="-8" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#f6821f" text-anchor="middle">CLOUD</text>
    <text x="0" y="12" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#f6821f" text-anchor="middle">FLARE</text>

    <!-- Edge nodes -->
    <g>
      <circle cx="-180" cy="-80" r="28" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="-180" y="-76" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">EDGE</text>
      <text x="-180" y="-62" font-family="Courier New" font-size="7" fill="#475569" text-anchor="middle">US-EAST</text>
    </g>
    <g>
      <circle cx="180" cy="-80" r="28" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="180" y="-76" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">EDGE</text>
      <text x="180" y="-62" font-family="Courier New" font-size="7" fill="#475569" text-anchor="middle">EU-WEST</text>
    </g>
    <g>
      <circle cx="-180" cy="80" r="28" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="-180" y="84" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">EDGE</text>
      <text x="-180" y="98" font-family="Courier New" font-size="7" fill="#475569" text-anchor="middle">AP-NE</text>
    </g>
    <g>
      <circle cx="180" cy="80" r="28" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="180" y="84" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">EDGE</text>
      <text x="180" y="98" font-family="Courier New" font-size="7" fill="#475569" text-anchor="middle">AP-SE</text>
    </g>

    <!-- Connections -->
    <g stroke="#f6821f" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.4">
      <line x1="-50" y1="-30" x2="-152" y2="-65"/>
      <line x1="50" y1="-30" x2="152" y2="-65"/>
      <line x1="-50" y1="30" x2="-152" y2="65"/>
      <line x1="50" y1="30" x2="152" y2="65"/>
    </g>

    <!-- WAF shield -->
    <g transform="translate(0,-130)" opacity="0.6">
      <path d="M0,-22 L18,-14 L18,6 C18,18 0,26 0,26 C0,26 -18,18 -18,6 L-18,-14 Z"
            fill="#f6821f" fill-opacity="0.2" stroke="#f6821f" stroke-width="1.5"/>
      <text x="0" y="3" font-family="Courier New" font-size="8" fill="#f6821f" text-anchor="middle">WAF</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#f6821f")


def visual_ai_coding(title, subtitle, date_str, label):
    """AI Coding Assistant - Code editor with AI suggestions."""
    h = _svg_header(title, "#22d3ee", "#ec4899")
    return h + '''
  <g transform="translate(600,250)">
    <!-- Code editor window -->
    <rect x="-220" y="-110" width="440" height="260" rx="12" fill="#0f172a" stroke="#334155" stroke-width="2" filter="url(#shadow)"/>
    <!-- Title bar -->
    <rect x="-220" y="-110" width="440" height="30" rx="12" fill="#1e293b"/>
    <circle cx="-198" cy="-95" r="5" fill="#ef4444" opacity="0.7"/>
    <circle cx="-182" cy="-95" r="5" fill="#f59e0b" opacity="0.7"/>
    <circle cx="-166" cy="-95" r="5" fill="#22c55e" opacity="0.7"/>
    <text x="0" y="-90" font-family="Courier New" font-size="10" fill="#64748b" text-anchor="middle">main.py</text>

    <!-- Code lines -->
    <g font-family="Courier New" font-size="11">
      <text x="-200" y="-60" fill="#64748b">1</text>
      <text x="-180" y="-60" fill="#c084fc">def</text>
      <text x="-148" y="-60" fill="#fbbf24"> analyze(data):</text>
      <text x="-200" y="-40" fill="#64748b">2</text>
      <text x="-170" y="-40" fill="#94a3b8">  results = []</text>
      <text x="-200" y="-20" fill="#64748b">3</text>
      <text x="-170" y="-20" fill="#c084fc">  for</text>
      <text x="-134" y="-20" fill="#94a3b8"> item </text>
      <text x="-86" y="-20" fill="#c084fc">in</text>
      <text x="-68" y="-20" fill="#94a3b8"> data:</text>
    </g>

    <!-- AI suggestion highlight -->
    <rect x="-205" y="-2" width="400" height="55" rx="4" fill="#22d3ee" opacity="0.06" stroke="#22d3ee" stroke-width="1" stroke-dasharray="4,3"/>
    <g font-family="Courier New" font-size="11">
      <text x="-200" y="18" fill="#64748b">4</text>
      <text x="-170" y="18" fill="#22d3ee" opacity="0.8">    score = model.predict(item)</text>
      <text x="-200" y="38" fill="#64748b">5</text>
      <text x="-170" y="38" fill="#22d3ee" opacity="0.8">    results.append(score)</text>
    </g>

    <!-- AI badge -->
    <g transform="translate(180,15)">
      <rect x="-25" y="-12" width="50" height="24" rx="12" fill="#22d3ee" opacity="0.2" stroke="#22d3ee" stroke-width="1"/>
      <text x="0" y="4" font-family="Arial,sans-serif" font-size="10" font-weight="bold" fill="#22d3ee" text-anchor="middle">AI</text>
    </g>

    <!-- Bottom status -->
    <text x="-200" y="78" font-family="Courier New" font-size="11" fill="#64748b">6</text>
    <text x="-170" y="78" fill="#c084fc" font-family="Courier New" font-size="11">  return</text>
    <text x="-106" y="78" fill="#94a3b8" font-family="Courier New" font-size="11"> results</text>

    <!-- Autocomplete popup -->
    <g transform="translate(220,-40)" opacity="0.5">
      <rect x="-35" y="-40" width="70" height="80" rx="8" fill="#1e293b" stroke="#22d3ee" stroke-width="1"/>
      <text x="0" y="-20" font-family="Courier New" font-size="8" fill="#22d3ee" text-anchor="middle">Claude</text>
      <text x="0" y="-6" font-family="Courier New" font-size="8" fill="#ec4899" text-anchor="middle">Gemini</text>
      <text x="0" y="8" font-family="Courier New" font-size="8" fill="#4ade80" text-anchor="middle">GPT</text>
      <text x="0" y="22" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">Codex</text>
    </g>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#22d3ee")


def visual_roadmap(title, subtitle, date_str, label):
    """Roadmap/Guide - Path with milestones."""
    h = _svg_header(title, "#8b5cf6", "#22c55e")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Winding path -->
    <path d="M-300,80 C-200,80 -180,-20 -80,-20 C20,-20 20,80 120,80 C220,80 220,-20 300,-20"
          fill="none" stroke="#334155" stroke-width="4" opacity="0.4"/>
    <path d="M-300,80 C-200,80 -180,-20 -80,-20 C20,-20 20,80 120,80 C220,80 220,-20 300,-20"
          fill="none" stroke="url(#accent)" stroke-width="2" stroke-dasharray="10,6" opacity="0.6"/>

    <!-- Milestones -->
    <g transform="translate(-240,80)">
      <circle r="18" fill="#0f172a" stroke="#3b82f6" stroke-width="2.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">START</text>
      <text x="0" y="40" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">Basics</text>
    </g>
    <g transform="translate(-80,-20)">
      <circle r="18" fill="#0f172a" stroke="#8b5cf6" stroke-width="2.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="8" fill="#a78bfa" text-anchor="middle">CORE</text>
      <text x="0" y="40" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">Security</text>
    </g>
    <g transform="translate(120,80)">
      <circle r="18" fill="#0f172a" stroke="#f59e0b" stroke-width="2.5"/>
      <text x="0" y="4" font-family="Courier New" font-size="8" fill="#fbbf24" text-anchor="middle">ADV</text>
      <text x="0" y="40" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">DevOps</text>
    </g>
    <g transform="translate(300,-20)">
      <circle r="22" fill="#0f172a" stroke="#22c55e" stroke-width="3"/>
      <text x="0" y="4" font-family="Courier New" font-size="8" fill="#4ade80" text-anchor="middle">GOAL</text>
      <text x="0" y="44" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">Expert</text>
    </g>

    <!-- Floating icons -->
    <text x="-160" y="-70" font-family="Courier New" font-size="10" fill="#475569">// learning path</text>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#8b5cf6")


def visual_music_creative(title, subtitle, date_str, label):
    """AI Music/Creative - Audio waveform visualization."""
    h = _svg_header(title, "#ec4899", "#8b5cf6")
    bars = ""
    import math
    for i in range(40):
        x = -300 + i * 15
        height = 20 + abs(math.sin(i * 0.5)) * 80 + abs(math.cos(i * 0.3)) * 40
        y = -height / 2
        opacity = 0.3 + abs(math.sin(i * 0.4)) * 0.5
        color = "#ec4899" if i % 3 == 0 else ("#8b5cf6" if i % 3 == 1 else "#3b82f6")
        bars += f'    <rect x="{x}" y="{y}" width="8" height="{height:.0f}" rx="4" fill="{color}" opacity="{opacity:.2f}"/>\n'

    return h + f'''
  <g transform="translate(600,260)">
    <!-- Audio waveform -->
{bars}
    <!-- Play button -->
    <circle r="35" fill="#0f172a" stroke="#ec4899" stroke-width="2.5" filter="url(#shadow)"/>
    <polygon points="-10,-16 -10,16 18,0" fill="#ec4899" opacity="0.8"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#ec4899")


def visual_karpenter(title, subtitle, date_str, label):
    """Karpenter/Autoscaling - Node scaling visualization."""
    h = _svg_header(title, "#326ce5", "#22c55e")
    return h + '''
  <g transform="translate(600,255)">
    <!-- Scaling arrow -->
    <path d="M-280,0 L280,0" stroke="#334155" stroke-width="2" opacity="0.4"/>
    <polygon points="280,-8 300,0 280,8" fill="#22c55e" opacity="0.6"/>

    <!-- Small nodes -->
    <g transform="translate(-200,0)">
      <rect x="-28" y="-50" width="56" height="100" rx="8" fill="#0f172a" stroke="#326ce5" stroke-width="1.5"/>
      <text x="0" y="-20" font-family="Courier New" font-size="8" fill="#60a5fa" text-anchor="middle">NODE</text>
      <rect x="-18" y="-6" width="36" height="14" rx="3" fill="#326ce5" opacity="0.3"/>
      <rect x="-18" y="14" width="36" height="14" rx="3" fill="#326ce5" opacity="0.2"/>
      <text x="0" y="48" font-family="Courier New" font-size="8" fill="#475569" text-anchor="middle">2 CPU</text>
    </g>

    <!-- Medium nodes -->
    <g transform="translate(-60,0)">
      <rect x="-35" y="-60" width="70" height="120" rx="10" fill="#0f172a" stroke="#326ce5" stroke-width="2"/>
      <text x="0" y="-30" font-family="Courier New" font-size="9" fill="#60a5fa" text-anchor="middle">NODE</text>
      <rect x="-22" y="-14" width="44" height="14" rx="3" fill="#326ce5" opacity="0.4"/>
      <rect x="-22" y="6" width="44" height="14" rx="3" fill="#326ce5" opacity="0.3"/>
      <rect x="-22" y="26" width="44" height="14" rx="3" fill="#22c55e" opacity="0.3"/>
      <text x="0" y="58" font-family="Courier New" font-size="8" fill="#475569" text-anchor="middle">4 CPU</text>
    </g>

    <!-- Large node (new) -->
    <g transform="translate(120,0)">
      <rect x="-45" y="-75" width="90" height="150" rx="12" fill="#0f172a" stroke="#22c55e" stroke-width="2.5"/>
      <text x="0" y="-45" font-family="Courier New" font-size="10" font-weight="bold" fill="#4ade80" text-anchor="middle">NODE+</text>
      <rect x="-30" y="-24" width="60" height="14" rx="3" fill="#22c55e" opacity="0.4"/>
      <rect x="-30" y="-4" width="60" height="14" rx="3" fill="#22c55e" opacity="0.3"/>
      <rect x="-30" y="16" width="60" height="14" rx="3" fill="#326ce5" opacity="0.3"/>
      <rect x="-30" y="36" width="60" height="14" rx="3" fill="#326ce5" opacity="0.2"/>
      <text x="0" y="72" font-family="Courier New" font-size="8" fill="#475569" text-anchor="middle">8 CPU</text>
    </g>

    <!-- Karpenter label -->
    <text x="0" y="-120" font-family="Courier New" font-size="12" font-weight="bold" fill="#4ade80" text-anchor="middle">KARPENTER AUTO-SCALING</text>
    <path d="M-100,-105 L100,-105" stroke="#22c55e" stroke-width="1" opacity="0.3"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#326ce5")


def visual_database(title, subtitle, date_str, label):
    """Database/NLB - Database access architecture."""
    h = _svg_header(title, "#f59e0b", "#3b82f6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Database cylinder -->
    <g transform="translate(150,0)" filter="url(#shadow)">
      <ellipse cx="0" cy="-50" rx="55" ry="18" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
      <rect x="-55" y="-50" width="110" height="100" fill="#0f172a"/>
      <line x1="-55" y1="-50" x2="-55" y2="50" stroke="#f59e0b" stroke-width="2"/>
      <line x1="55" y1="-50" x2="55" y2="50" stroke="#f59e0b" stroke-width="2"/>
      <ellipse cx="0" cy="50" rx="55" ry="18" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
      <ellipse cx="0" cy="-20" rx="55" ry="12" fill="none" stroke="#f59e0b" stroke-width="0.8" opacity="0.3"/>
      <ellipse cx="0" cy="15" rx="55" ry="12" fill="none" stroke="#f59e0b" stroke-width="0.8" opacity="0.3"/>
      <text x="0" y="5" font-family="Courier New" font-size="12" font-weight="bold" fill="#fbbf24" text-anchor="middle">RDS</text>
    </g>

    <!-- NLB -->
    <g transform="translate(-150,0)" filter="url(#shadow)">
      <rect x="-55" y="-40" width="110" height="80" rx="12" fill="#0f172a" stroke="#3b82f6" stroke-width="2"/>
      <text x="0" y="-10" font-family="Courier New" font-size="14" font-weight="bold" fill="#60a5fa" text-anchor="middle">NLB</text>
      <text x="0" y="12" font-family="Courier New" font-size="9" fill="#475569" text-anchor="middle">Load Balancer</text>
    </g>

    <!-- Security Group -->
    <rect x="-20" y="-70" width="40" height="140" rx="4" fill="none" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.4"/>
    <text x="10" y="-80" font-family="Courier New" font-size="9" fill="#4ade80" text-anchor="middle">SG</text>

    <!-- Connection -->
    <line x1="-95" y1="0" x2="95" y2="0" stroke="#475569" stroke-width="2" opacity="0.5"/>
    <polygon points="90,-6 100,0 90,6" fill="#475569" opacity="0.6"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#f59e0b")


def visual_generic_tech(title, subtitle, date_str, label):
    """Generic tech - Circuit board pattern."""
    h = _svg_header(title, "#3b82f6", "#8b5cf6")
    return h + '''
  <g transform="translate(600,260)">
    <!-- Circuit board pattern -->
    <g stroke="#3b82f6" stroke-width="1.5" opacity="0.3">
      <line x1="-200" y1="-80" x2="-100" y2="-80"/>
      <line x1="-100" y1="-80" x2="-100" y2="0"/>
      <line x1="-100" y1="0" x2="0" y2="0"/>
      <line x1="0" y1="0" x2="0" y2="80"/>
      <line x1="0" y1="80" x2="100" y2="80"/>
      <line x1="100" y1="80" x2="100" y2="0"/>
      <line x1="100" y1="0" x2="200" y2="0"/>
      <line x1="-200" y1="40" x2="-60" y2="40"/>
      <line x1="-60" y1="40" x2="-60" y2="-40"/>
      <line x1="-60" y1="-40" x2="60" y2="-40"/>
      <line x1="60" y1="-40" x2="60" y2="40"/>
      <line x1="60" y1="40" x2="200" y2="40"/>
    </g>

    <!-- Central processor -->
    <rect x="-45" y="-45" width="90" height="90" rx="12" fill="#0f172a" stroke="#8b5cf6" stroke-width="2.5" filter="url(#shadow)"/>
    <text x="0" y="-8" font-family="Courier New" font-size="14" font-weight="bold" fill="#a78bfa" text-anchor="middle">TECH</text>
    <text x="0" y="14" font-family="Courier New" font-size="10" fill="#64748b" text-anchor="middle">BLOG</text>

    <!-- Junction nodes -->
    <circle cx="-200" cy="-80" r="5" fill="#3b82f6" opacity="0.5"/>
    <circle cx="-100" cy="0" r="5" fill="#3b82f6" opacity="0.5"/>
    <circle cx="0" cy="80" r="5" fill="#3b82f6" opacity="0.5"/>
    <circle cx="100" cy="0" r="5" fill="#3b82f6" opacity="0.5"/>
    <circle cx="200" cy="0" r="5" fill="#3b82f6" opacity="0.5"/>
    <circle cx="-200" cy="40" r="5" fill="#3b82f6" opacity="0.4"/>
    <circle cx="200" cy="40" r="5" fill="#3b82f6" opacity="0.4"/>
    <circle cx="-60" cy="-40" r="4" fill="#8b5cf6" opacity="0.4"/>
    <circle cx="60" cy="40" r="4" fill="#8b5cf6" opacity="0.4"/>
  </g>
''' + _svg_footer(title, subtitle, date_str, label, "#3b82f6")


# ─── DIGEST TEMPLATE (THREAT SIGNAL MAP v2) ────────────────────────

# Node icon definitions for digest SVG - larger, more detailed
DIGEST_ICONS = {
    "malware": {"label": "MALWARE", "color": "#ef4444",
        "icon": '<circle r="20" fill="{c}" opacity="0.15"/><circle cx="-14" cy="-10" r="7" fill="{c}" opacity="0.5"/><circle cx="14" cy="10" r="7" fill="{c}" opacity="0.5"/><circle cx="10" cy="-14" r="5" fill="{c}" opacity="0.4"/><circle cx="-10" cy="14" r="4" fill="{c}" opacity="0.3"/><line x1="-14" y1="-10" x2="14" y2="10" stroke="{c}" stroke-width="1" opacity="0.3"/>'},
    "ransomware": {"label": "RANSOM", "color": "#dc2626",
        "icon": '<rect x="-24" y="-4" width="48" height="38" rx="8" fill="#1a1020" stroke="{c}" stroke-width="2.5"/><path d="M-14 -4 v-18 c0-20 28-20 28 0 v18" stroke="{c}" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="0" cy="16" r="7" fill="{c}"/><rect x="-2" y="20" width="4" height="12" rx="2" fill="{c}"/>'},
    "zero-day": {"label": "ZERO DAY", "color": "#f97316",
        "icon": '<rect x="-24" y="-18" width="48" height="36" rx="8" fill="#1a1020" stroke="{c}" stroke-width="2.5"/><text x="0" y="-2" font-family="Courier New" font-size="14" font-weight="700" fill="{c}" text-anchor="middle">CVE</text><text x="0" y="14" font-family="Courier New" font-size="9" fill="{c}" text-anchor="middle" opacity="0.7">0-DAY</text>'},
    "cloud": {"label": "CLOUD", "color": "#3b82f6",
        "icon": '<path d="M-20 12 C-34 12 -38 -2 -38 -12 C-38 -24 -28 -32 -16 -32 C-12 -44 0 -50 12 -50 C28 -50 38 -38 38 -30 C48 -30 52 -22 52 -12 C52 -2 48 12 32 12 Z" fill="#0b1628" stroke="{c}" stroke-width="2.5" transform="scale(0.65)"/>'},
    "ai": {"label": "AI/ML", "color": "#22d3ee",
        "icon": '<circle r="18" fill="none" stroke="{c}" stroke-width="2.5"/><circle r="8" fill="{c}" opacity="0.35"/><line x1="-24" y1="-16" x2="-10" y2="-8" stroke="{c}" stroke-width="2"/><line x1="24" y1="-16" x2="10" y2="-8" stroke="{c}" stroke-width="2"/><line x1="-24" y1="16" x2="-10" y2="8" stroke="{c}" stroke-width="2"/><line x1="24" y1="16" x2="10" y2="8" stroke="{c}" stroke-width="2"/><circle cx="-24" cy="-16" r="5" fill="{c}" opacity="0.5"/><circle cx="24" cy="-16" r="5" fill="{c}" opacity="0.5"/><circle cx="-24" cy="16" r="5" fill="{c}" opacity="0.5"/><circle cx="24" cy="16" r="5" fill="{c}" opacity="0.5"/>'},
    "kubernetes": {"label": "K8S", "color": "#326ce5",
        "icon": '<polygon points="0,-24 22,-10 14,20 -14,20 -22,-10" fill="none" stroke="{c}" stroke-width="2.5"/><circle r="7" fill="{c}" opacity="0.35"/><line x1="0" y1="-7" x2="0" y2="-20" stroke="{c}" stroke-width="2"/><line x1="6" y1="4" x2="18" y2="14" stroke="{c}" stroke-width="2"/><line x1="-6" y1="4" x2="-18" y2="14" stroke="{c}" stroke-width="2"/>'},
    "patch": {"label": "PATCH", "color": "#22c55e",
        "icon": '<path d="M0,-26 L22,-14 L22,10 C22,24 0,34 0,34 C0,34 -22,24 -22,10 L-22,-14 Z" fill="none" stroke="{c}" stroke-width="2.5"/><path d="M-9,2 L-3,10 L12,-8" stroke="{c}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'},
    "blockchain": {"label": "CHAIN", "color": "#8b5cf6",
        "icon": '<rect x="-20" y="-16" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="2"/><rect x="4" y="-16" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="2"/><rect x="-8" y="4" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="2"/><line x1="-4" y1="0" x2="-1" y2="4" stroke="{c}" stroke-width="2"/><line x1="12" y1="0" x2="5" y2="4" stroke="{c}" stroke-width="2"/>'},
    "botnet": {"label": "BOTNET", "color": "#f59e0b",
        "icon": '<circle r="10" fill="{c}" opacity="0.25"/><circle cx="-22" cy="-14" r="6" fill="{c}" opacity="0.3"/><circle cx="22" cy="-14" r="6" fill="{c}" opacity="0.3"/><circle cx="-22" cy="14" r="6" fill="{c}" opacity="0.3"/><circle cx="22" cy="14" r="6" fill="{c}" opacity="0.3"/><line x1="-5" y1="-5" x2="-16" y2="-11" stroke="{c}" stroke-width="1.5" opacity="0.5"/><line x1="5" y1="-5" x2="16" y2="-11" stroke="{c}" stroke-width="1.5" opacity="0.5"/><line x1="-5" y1="5" x2="-16" y2="11" stroke="{c}" stroke-width="1.5" opacity="0.5"/><line x1="5" y1="5" x2="16" y2="11" stroke="{c}" stroke-width="1.5" opacity="0.5"/>'},
    "phishing": {"label": "PHISH", "color": "#ec4899",
        "icon": '<path d="M-22 -10 L0 14 L22 -10" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/><rect x="-26" y="-18" width="52" height="40" rx="5" fill="none" stroke="{c}" stroke-width="2"/><circle cx="0" cy="-26" r="4" fill="{c}"/>'},
    "auth": {"label": "AUTH", "color": "#eab308",
        "icon": '<rect x="-18" y="-4" width="36" height="28" rx="5" fill="none" stroke="{c}" stroke-width="2.5"/><path d="M-10 -4 v-12 c0-14 20-14 20 0 v12" stroke="{c}" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="0" cy="10" r="5" fill="{c}"/>'},
    "devops": {"label": "DEVOPS", "color": "#f97316",
        "icon": '<path d="M-18 0 A18 18 0 0 1 18 0" fill="none" stroke="{c}" stroke-width="3"/><path d="M18 0 A18 18 0 0 1 -18 0" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="5 3"/><polygon points="18,-5 25,0 18,5" fill="{c}"/><polygon points="-18,5 -25,0 -18,-5" fill="{c}"/>'},
}

DIGEST_KEYWORD_MAP = {
    "ransomware": "ransomware", "ransom": "ransomware",
    "zero-day": "zero-day", "0-day": "zero-day", "cve": "zero-day", "exploit": "zero-day",
    "malware": "malware", "trojan": "malware", "worm": "malware",
    "botnet": "botnet", "bot": "botnet", "ddos": "botnet",
    "blockchain": "blockchain", "bitcoin": "blockchain", "crypto": "blockchain", "defi": "blockchain",
    "ai": "ai", "llm": "ai", "gpt": "ai", "agent": "ai", "ml": "ai",
    "cloud": "cloud", "aws": "cloud", "azure": "cloud", "gcp": "cloud",
    "patch": "patch", "update": "patch", "fix": "patch",
    "kubernetes": "kubernetes", "k8s": "kubernetes", "docker": "kubernetes", "container": "kubernetes",
    "phishing": "phishing", "phish": "phishing",
    "authentication": "auth", "mfa": "auth", "credential": "auth", "zero trust": "auth",
    "devops": "devops", "devsecops": "devops", "cicd": "devops", "ci/cd": "devops",
}


def _detect_digest_nodes(title, tags):
    """Detect up to 3 unique threat signal nodes from title and tags."""
    text = f"{title} {' '.join(str(t) for t in tags)}".lower()
    seen = []
    for keyword in sorted(DIGEST_KEYWORD_MAP.keys(), key=len, reverse=True):
        if len(keyword) <= 2:
            matched = re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None
        else:
            matched = keyword in text
        if matched and DIGEST_KEYWORD_MAP[keyword] not in seen:
            seen.append(DIGEST_KEYWORD_MAP[keyword])
            if len(seen) >= 3:
                break
    # Ensure at least 2 nodes
    for fallback in ["ai", "patch", "malware"]:
        if len(seen) >= 2:
            break
        if fallback not in seen:
            seen.append(fallback)
    return seen[:3]


def visual_digest(title, subtitle, date_str, tags):
    """High-quality THREAT SIGNAL MAP for digest posts."""
    nodes = _detect_digest_nodes(title, tags if isinstance(tags, list) else [])
    node_configs = [DIGEST_ICONS.get(n, DIGEST_ICONS["malware"]) for n in nodes]

    # Node positions
    if len(node_configs) == 2:
        positions = [350, 850]
    else:
        positions = [250, 600, 950]

    # Subtitle from node labels
    node_subtitle = "  ".join(nc["label"] for nc in node_configs)

    # Build node SVGs with larger circles (r=70)
    nodes_svg = ""
    for i, (nc, x_pos) in enumerate(zip(node_configs, positions)):
        c = nc["color"]
        icon = nc["icon"].replace("{c}", c)
        nodes_svg += f'''
  <g transform="translate({x_pos} 320)" filter="url(#shadow)">
    <circle r="70" fill="#0f172a" stroke="{c}" stroke-width="2.5"/>
    <circle r="70" fill="{c}" opacity="0.04"/>
    {icon}
  </g>
  <text x="{x_pos}" y="420" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="{c}" text-anchor="middle">{nc["label"]}</text>
'''

    # Curved attack-flow arrows between nodes
    arrows_svg = ""
    for i in range(len(positions) - 1):
        x1, x2 = positions[i] + 70, positions[i + 1] - 70
        mid = (x1 + x2) // 2
        c1 = node_configs[i]["color"]
        c2 = node_configs[i + 1]["color"]
        arrows_svg += f'''  <path d="M{x1} 320 C{mid} 270 {mid} 270 {x2} 320" fill="none" stroke="{c1}" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.5"/>
  <polygon points="{x2-2},315 {x2+8},320 {x2-2},325" fill="{c2}" opacity="0.6"/>
'''

    # Glow circles behind nodes
    glows = ""
    for i, nc in enumerate(node_configs):
        glows += f'  <circle cx="{positions[i]}" cy="200" r="160" fill="{nc["color"]}" opacity="0.08" filter="url(#glow)"/>\n'

    # Title display (2 lines if needed)
    title_lines = wrap_title(title, 50)
    if len(title_lines) == 1:
        title_svg = f'  <text x="600" y="498" font-family="Arial,sans-serif" font-size="28" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow2)">{escape_svg(title_lines[0])}</text>'
    else:
        title_svg = f'  <text x="600" y="478" font-family="Arial,sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow2)">{escape_svg(title_lines[0])}</text>\n  <text x="600" y="508" font-family="Arial,sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow2)">{escape_svg(title_lines[1])}</text>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{escape_svg(title)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0e1a"/>
      <stop offset="50%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#0f0a1e"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="25"/></filter>
    <filter id="glow2"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="shadow"><feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#020617" flood-opacity="0.5"/></filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
{glows}
  <text x="90" y="90" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#f8fafc">THREAT SIGNAL MAP</text>
  <text x="92" y="120" font-family="Arial,sans-serif" font-size="16" fill="#64748b">{escape_svg(node_subtitle)}</text>

  <line x1="180" y1="320" x2="1020" y2="320" stroke="#334155" stroke-width="3" stroke-dasharray="12 8" opacity="0.4"/>
{arrows_svg}{nodes_svg}
{title_svg}
  <text x="600" y="535" font-family="Arial,sans-serif" font-size="14" fill="#64748b" text-anchor="middle">{escape_svg(subtitle)}</text>

  <rect x="40" y="20" width="120" height="30" rx="15" fill="#ef4444" opacity="0.2" stroke="#ef4444" stroke-width="1"/>
  <text x="100" y="41" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#f87171" text-anchor="middle">SECURITY</text>
  <rect x="1040" y="20" width="120" height="30" rx="15" fill="#3b82f6" opacity="0.2" stroke="#3b82f6" stroke-width="1"/>
  <text x="1100" y="41" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#93c5fd" text-anchor="middle">{escape_svg(date_str)}</text>

  <rect x="70" y="570" width="1060" height="1.5" fill="#334155" opacity="0.6"/>
  <text x="90" y="600" font-family="Arial,sans-serif" font-size="13" fill="#94a3b8">tech.2twodragon.com</text>
  <text x="1110" y="600" font-family="Arial,sans-serif" font-size="13" fill="#64748b" text-anchor="end">Weekly Digest</text>
</svg>'''


# ─── TOPIC DETECTION & MAPPING ─────────────────────────────────────

TOPIC_RULES = [
    # (keywords_any, also_requires_any, visual_func)
    # More specific patterns first; also_requires_any uses ANY match (not ALL)
    (["karpenter", "autoscal", "node scaling"], [], visual_karpenter),
    (["tesla", "fsd", "automotive", "vehicle", "connected car"], [], visual_tesla_automotive),
    (["npm", "shai-hulud"], [], visual_npm_supply_chain),
    (["supply chain", "supply-chain"], ["npm", "package", "dependency"], visual_npm_supply_chain),
    (["blockchain", "crypto", "bitcoin", "defi"], [], visual_blockchain),
    (["email", "sendgrid", "spf", "dkim", "dmarc"], [], visual_email),
    (["kandji", "macos", "mdm"], [], visual_macos_mdm),
    (["post-mortem", "postmortem"], [], visual_incident),
    (["cloudflare"], ["incident", "outage", "장애"], visual_incident),
    (["cloudflare"], [], visual_cloudflare),
    (["zscaler", "zero trust", "ztna"], [], visual_zscaler_network),
    (["ransomware", "ransom", "kara ransomware"], [], visual_ransomware),
    (["conference", "awskrug", "meetup", "컨퍼런스", "회고"], [], visual_conference),
    (["reinforce"], [], visual_conference),
    (["music", "video generation", "creative ai"], [], visual_music_creative),
    (["roadmap", "learning path", "로드맵"], [], visual_roadmap),
    (["ai coding", "coding assistant", "claude code", "chatgpt", "copilot", "opencode"], [], visual_ai_coding),
    (["ai vs", "ai comparison", "코딩 어시스턴트"], [], visual_ai_coding),
    (["owasp"], [], visual_owasp),
    (["isms", "compliance", "certification", "인증"], [], visual_isms_compliance),
    (["ci/cd", "ci cd", "ci_cd"], [], visual_cicd),
    (["database", "rds", "nlb"], ["gateway", "접근"], visual_database),
    (["finops", "cost optimization", "비용"], [], visual_finops),
    (["docker"], ["kubernetes", "k8s", "container"], visual_docker),
    (["docker"], [], visual_docker),
    (["kubernetes", "k8s", "k9s", "minikube", "helm", "eks", "gke"], [], visual_kubernetes),
    (["agentic ai", "agentic-ai", "ai agent", "ai-agent", "llm security", "llm-security", "prompt injection", "prompt-injection"], [], visual_ai_neural),
    (["ai", "llm", "gpt", "ml", "neural"], [], visual_ai_neural),
    (["aws", "gcp", "azure", "cloud security", "vpc", "guardduty", "waf", "cloudfront", "cloud update"], [], visual_aws_cloud),
    (["control tower", "scp", "governance"], [], visual_aws_cloud),
    (["devsecops", "devops"], [], visual_devsecops),
    (["security", "vulnerability", "cve", "patch", "threat", "보안"], [], visual_security_shield),
]


def detect_topic(title, tags, categories):
    text = f"{title} {' '.join(str(t) for t in tags)} {' '.join(str(c) for c in categories)}".lower()

    for any_kw, also_kw, func in TOPIC_RULES:
        # Primary: any keyword must match
        any_match = any(kw in text for kw in any_kw) if any_kw else True
        # Secondary: if provided, at least one must also match
        also_match = any(kw in text for kw in also_kw) if also_kw else True

        if any_match and also_match:
            return func

    return visual_generic_tech


def get_label(categories):
    cat_labels = {
        "security": "SECURITY",
        "devsecops": "DEVSECOPS",
        "devops": "DEVOPS",
        "cloud": "CLOUD",
        "kubernetes": "KUBERNETES",
        "finops": "FINOPS",
        "incident": "INCIDENT",
        "blockchain": "BLOCKCHAIN",
    }
    for c in categories:
        cl = c.lower()
        if cl in cat_labels:
            return cat_labels[cl]
    return "TECH BLOG"


def process_post(post_path):
    """Process a single post and generate its SVG image."""
    try:
        post = frontmatter.load(post_path)
    except Exception as e:
        print(f"  SKIP (parse error): {post_path.name} - {e}")
        return False

    title = post.get("title", "")
    if not title:
        print(f"  SKIP (no title): {post_path.name}")
        return False

    image_path = post.get("image", "")
    if not image_path:
        return False

    # Get image filename from frontmatter
    svg_filename = Path(image_path).name
    if not svg_filename.endswith(".svg"):
        svg_filename = svg_filename.rsplit(".", 1)[0] + ".svg"

    output_path = IMAGES_DIR / svg_filename

    tags = post.get("tags", []) or []
    categories = post.get("categories", []) or []
    if isinstance(categories, str):
        categories = [categories]
    if isinstance(tags, str):
        tags = [tags]

    # Build subtitle from tags
    tag_display = [str(t) for t in tags[:4]] if tags else []
    subtitle = " | ".join(tag_display) if tag_display else "Tech Blog"

    # Extract date
    date_val = post.get("date", "")
    if date_val:
        try:
            if hasattr(date_val, "strftime"):
                date_str = date_val.strftime("%B %d, %Y")
            else:
                parsed = datetime.strptime(str(date_val)[:10], "%Y-%m-%d")
                date_str = parsed.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            date_str = datetime.now().strftime("%B %d, %Y")
    else:
        date_str = datetime.now().strftime("%B %d, %Y")

    # Use English title for SVG display (from filename or image_alt)
    display_title = post.get("image_alt", "") or title
    # Remove emojis
    display_title = re.sub(r'[^\x00-\x7F\uAC00-\uD7A3\u3131-\u3163\u3000-\u303f]+', '', display_title).strip()

    is_digest = "Digest" in post_path.name or "Weekly_Digest" in title

    if is_digest:
        display_title = truncate(display_title, 56)
        svg_content = visual_digest(display_title, subtitle, date_str, tags)
    else:
        display_title = truncate(display_title, 52)
        label = get_label(categories)
        visual_func = detect_topic(title, tags, categories)
        svg_content = visual_func(display_title, subtitle, date_str, label)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    func_name = "visual_digest" if is_digest else visual_func.__name__
    print(f"  OK: {svg_filename} [{func_name}]")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Regenerate all post SVG images with topic-specific visuals")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be generated")
    parser.add_argument("--post", type=str, help="Process a specific post file")
    args = parser.parse_args()

    if not POSTS_DIR.exists():
        print(f"Posts directory not found: {POSTS_DIR}")
        sys.exit(1)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    if args.post:
        post_files = [POSTS_DIR / args.post]
    else:
        post_files = sorted(POSTS_DIR.glob("*.md"))

    total = 0
    generated = 0
    skipped = 0

    for post_file in post_files:
        if not post_file.exists():
            print(f"  NOT FOUND: {post_file}")
            continue

        total += 1

        if args.dry_run:
            try:
                post = frontmatter.load(post_file)
                title = post.get("title", "")
                tags = post.get("tags", []) or []
                categories = post.get("categories", []) or []
                if isinstance(categories, str):
                    categories = [categories]
                if "Digest" in post_file.name:
                    print(f"  {post_file.name} -> visual_digest")
                else:
                    func = detect_topic(title, tags, categories)
                    print(f"  {post_file.name} -> {func.__name__}")
                generated += 1
            except Exception:
                skipped += 1
        else:
            result = process_post(post_file)
            if result:
                generated += 1
            else:
                skipped += 1

    print(f"\nTotal: {total} | Generated: {generated} | Skipped: {skipped}")


if __name__ == "__main__":
    main()
