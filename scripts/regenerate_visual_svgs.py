#!/usr/bin/env python3
"""
Batch convert card-based SVGs to visual illustration SVGs.
Reads filename keywords to select appropriate visual theme.

Usage:
    python3 scripts/regenerate_visual_svgs.py --dry-run
    python3 scripts/regenerate_visual_svgs.py
    python3 scripts/regenerate_visual_svgs.py --file assets/images/some-file.svg
"""

import argparse
import hashlib
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

IMAGES_DIR = Path("assets/images")

THEME_KEYWORDS = {
    "threat": ["zero-day", "cve", "vulnerability", "ransomware", "malware",
               "exploit", "threat", "attack", "patch", "breach", "security",
               "incident", "phishing", "botnet", "ddos", "worm", "edr"],
    "neural": ["ai", "ml", "llm", "agent", "gpt", "model", "deep",
               "coding", "assistant", "openai", "gemini", "claude", "chatgpt"],
    "cloud": ["cloud", "aws", "gcp", "azure", "kubernetes", "k8s",
              "docker", "eks", "gke", "iam", "vpc", "waf", "guardduty",
              "cloudfront", "cloudflare", "control-tower", "isms"],
    "pipeline": ["devops", "devsecops", "pipeline", "deploy", "container",
                 "go", "rust", "ci", "cd", "helm", "karpenter", "datadog",
                 "terraform", "roadmap"],
    "chain": ["blockchain", "bitcoin", "ethereum", "defi", "web3", "crypto",
              "cryptocurrency"],
}

THEME_COLORS = {
    "threat": ("#ef4444", "#fca5a5"),
    "neural": ("#6366f1", "#a5b4fc"),
    "cloud": ("#3b82f6", "#93c5fd"),
    "pipeline": ("#f59e0b", "#fde68a"),
    "chain": ("#f97316", "#fdba74"),
}


def select_theme(filename: str) -> str:
    name_lower = filename.lower().replace("_", " ").replace("-", " ")
    scores = {}
    for theme, keywords in THEME_KEYWORDS.items():
        scores[theme] = sum(1 for kw in keywords if kw in name_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "threat"


def extract_title(filename: str) -> str:
    name = Path(filename).stem
    # Remove date prefix
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    # Convert underscores to spaces
    title = name.replace("_", " ").replace("-", " ")
    # Truncate if too long
    if len(title) > 45:
        words = title.split()
        title = ""
        for w in words:
            if len(title + " " + w) > 45:
                break
            title = (title + " " + w).strip()
    return title


def extract_date(filename: str) -> str:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", Path(filename).name)
    if match:
        months = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
        y, m, d = match.groups()
        return f"{months[int(m)]} {int(d)}, {y}"
    return "2026"


def extract_subtopics(filename: str) -> str:
    name = Path(filename).stem.lower()
    found = []
    topic_map = {
        "security": "Security", "aws": "AWS", "cloud": "Cloud",
        "kubernetes": "K8s", "docker": "Docker", "ai": "AI",
        "devsecops": "DevSecOps", "devops": "DevOps",
        "blockchain": "Blockchain", "bitcoin": "Bitcoin",
        "ransomware": "Ransomware", "zero.day": "Zero-Day",
        "malware": "Malware", "isms": "ISMS-P",
        "finops": "FinOps", "llm": "LLM", "mcp": "MCP",
        "tesla": "Tesla", "owasp": "OWASP",
    }
    for key, label in topic_map.items():
        if key in name and label not in found:
            found.append(label)
        if len(found) >= 4:
            break
    return " | ".join(found) if found else "Security | Cloud | DevOps"


def scene_threat() -> str:
    return """
  <g transform="translate(600,255)">
    <path d="M0,-135 C75,-135 125,-95 125,-15 C125,65 65,125 0,155 C-65,125 -125,65 -125,-15 C-125,-95 -75,-135 0,-135Z"
          fill="#ef4444" fill-opacity="0.05" stroke="#ef4444" stroke-width="2.5" opacity="0.7"/>
    <path d="M0,-100 C55,-100 90,-70 90,-10 C90,45 50,85 0,110 C-50,85 -90,45 -90,-10 C-90,-70 -55,-100 0,-100Z"
          fill="#ef4444" fill-opacity="0.03" stroke="#ef4444" stroke-width="1" opacity="0.35"/>
    <path d="M-5,-115 L10,-65 L-12,-20 L14,35 L-10,75 L6,125"
          fill="none" stroke="#fca5a5" stroke-width="3" stroke-linecap="round"/>
    <rect x="-20" y="-15" width="40" height="32" rx="5" fill="none" stroke="#ef4444" stroke-width="2"/>
    <path d="M-12,-15 L-12,-28 C-12,-45 12,-45 12,-28 L12,-15" fill="none" stroke="#ef4444" stroke-width="2.5"/>
    <circle cx="0" cy="5" r="5" fill="#ef4444" opacity="0.7"/>
    <rect x="-1.5" y="8" width="3" height="8" rx="1.5" fill="#ef4444" opacity="0.7"/>
  </g>
  <g opacity="0.5">
    <path d="M120,100 C250,150 380,200 485,240" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="8,4"/>
    <polygon points="483,235 495,240 483,245" fill="#ef4444"/>
    <path d="M1080,100 C950,150 820,200 715,240" fill="none" stroke="#f59e0b" stroke-width="2" stroke-dasharray="8,4"/>
    <polygon points="717,235 705,240 717,245" fill="#f59e0b"/>
    <path d="M120,420 C250,370 380,310 490,275" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-dasharray="8,4"/>
    <polygon points="488,270 500,275 488,280" fill="#8b5cf6"/>
    <path d="M1080,420 C950,370 820,310 710,275" fill="none" stroke="#3b82f6" stroke-width="2" stroke-dasharray="8,4"/>
    <polygon points="712,270 700,275 712,280" fill="#3b82f6"/>
  </g>
  <g opacity="0.35">
    <polygon points="170,160 180,145 190,160" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="180" y="158" font-family="Arial" font-size="7" fill="#f59e0b" text-anchor="middle">!</text>
    <polygon points="1010,160 1020,145 1030,160" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="1020" y="158" font-family="Arial" font-size="7" fill="#f59e0b" text-anchor="middle">!</text>
  </g>"""


def scene_neural() -> str:
    return """
  <g transform="translate(600,255)">
    <circle cx="0" cy="0" r="50" fill="#6366f1" fill-opacity="0.08" stroke="#818cf8" stroke-width="2"/>
    <circle cx="0" cy="0" r="30" fill="#6366f1" fill-opacity="0.12" stroke="#a5b4fc" stroke-width="1.5"/>
    <circle cx="0" cy="0" r="12" fill="#818cf8" opacity="0.6"/>
    <circle cx="-180" cy="-80" r="22" fill="#1e293b" stroke="#60a5fa" stroke-width="1.5"/>
    <circle cx="-180" cy="-80" r="8" fill="#3b82f6" opacity="0.5"/>
    <circle cx="180" cy="-80" r="22" fill="#1e293b" stroke="#60a5fa" stroke-width="1.5"/>
    <circle cx="180" cy="-80" r="8" fill="#3b82f6" opacity="0.5"/>
    <circle cx="-200" cy="80" r="18" fill="#1e293b" stroke="#a78bfa" stroke-width="1.5"/>
    <circle cx="200" cy="80" r="18" fill="#1e293b" stroke="#a78bfa" stroke-width="1.5"/>
    <circle cx="0" cy="-140" r="20" fill="#1e293b" stroke="#34d399" stroke-width="1.5"/>
    <circle cx="0" cy="140" r="20" fill="#1e293b" stroke="#fbbf24" stroke-width="1.5"/>
    <circle cx="-100" cy="-40" r="14" fill="#1e293b" stroke="#818cf8" stroke-width="1"/>
    <circle cx="100" cy="-40" r="14" fill="#1e293b" stroke="#818cf8" stroke-width="1"/>
    <circle cx="-100" cy="50" r="14" fill="#1e293b" stroke="#818cf8" stroke-width="1"/>
    <circle cx="100" cy="50" r="14" fill="#1e293b" stroke="#818cf8" stroke-width="1"/>
    <g stroke="#6366f1" stroke-width="1" opacity="0.3">
      <line x1="0" y1="0" x2="-100" y2="-40"/><line x1="0" y1="0" x2="100" y2="-40"/>
      <line x1="0" y1="0" x2="-100" y2="50"/><line x1="0" y1="0" x2="100" y2="50"/>
      <line x1="0" y1="0" x2="0" y2="-140"/><line x1="0" y1="0" x2="0" y2="140"/>
      <line x1="-100" y1="-40" x2="-180" y2="-80"/><line x1="100" y1="-40" x2="180" y2="-80"/>
      <line x1="-100" y1="50" x2="-200" y2="80"/><line x1="100" y1="50" x2="200" y2="80"/>
    </g>
    <g opacity="0.5">
      <circle cx="-50" cy="-20" r="3" fill="#818cf8"/><circle cx="50" cy="-20" r="3" fill="#818cf8"/>
      <circle cx="-140" cy="-60" r="2.5" fill="#60a5fa"/><circle cx="140" cy="-60" r="2.5" fill="#60a5fa"/>
    </g>
  </g>"""


def scene_cloud() -> str:
    return """
  <g transform="translate(600,240)">
    <path d="M-60,40 C-95,40 -120,15 -120,-15 C-120,-45 -95,-70 -65,-70 C-60,-100 -30,-120 0,-120 C35,-120 65,-95 65,-70 C100,-70 120,-45 120,-15 C120,15 100,40 65,40 Z"
          fill="#3b82f6" fill-opacity="0.06" stroke="#60a5fa" stroke-width="2" opacity="0.7"/>
    <rect x="-50" y="-50" width="30" height="40" rx="4" fill="#1e293b" stroke="#60a5fa" stroke-width="1.2"/>
    <line x1="-45" y1="-35" x2="-25" y2="-35" stroke="#3b82f6" stroke-width="1" opacity="0.5"/>
    <line x1="-45" y1="-28" x2="-25" y2="-28" stroke="#3b82f6" stroke-width="1" opacity="0.5"/>
    <rect x="10" y="-50" width="30" height="40" rx="4" fill="#1e293b" stroke="#60a5fa" stroke-width="1.2"/>
    <line x1="15" y1="-35" x2="35" y2="-35" stroke="#3b82f6" stroke-width="1" opacity="0.5"/>
    <line x1="15" y1="-28" x2="35" y2="-28" stroke="#3b82f6" stroke-width="1" opacity="0.5"/>
  </g>
  <g transform="translate(600,350)">
    <g stroke="#475569" stroke-width="1" opacity="0.4">
      <line x1="-180" y1="-20" x2="-60" y2="-20"/><line x1="60" y1="-20" x2="180" y2="-20"/>
      <line x1="0" y1="-30" x2="0" y2="-60"/>
      <line x1="-180" y1="-20" x2="-180" y2="10"/><line x1="180" y1="-20" x2="180" y2="10"/>
    </g>
    <rect x="-205" y="10" width="50" height="35" rx="6" fill="#1e293b" stroke="#10b981" stroke-width="1.2"/>
    <text x="-180" y="32" font-family="Courier New" font-size="9" fill="#6ee7b7" text-anchor="middle">K8s</text>
    <rect x="-85" y="10" width="50" height="35" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="-60" y="32" font-family="Courier New" font-size="9" fill="#fbbf24" text-anchor="middle">DB</text>
    <rect x="35" y="10" width="50" height="35" rx="6" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
    <text x="60" y="32" font-family="Courier New" font-size="9" fill="#fca5a5" text-anchor="middle">WAF</text>
    <rect x="155" y="10" width="50" height="35" rx="6" fill="#1e293b" stroke="#8b5cf6" stroke-width="1.2"/>
    <text x="180" y="32" font-family="Courier New" font-size="9" fill="#c4b5fd" text-anchor="middle">IAM</text>
  </g>
  <rect x="300" y="100" width="600" height="330" rx="20" fill="none" stroke="#334155" stroke-width="1.5" stroke-dasharray="10,5" opacity="0.3"/>"""


def scene_pipeline() -> str:
    return """
  <g transform="translate(600,255)">
    <path d="M-400,0 L400,0" fill="none" stroke="#475569" stroke-width="3" opacity="0.3"/>
    <g transform="translate(-300,0)">
      <rect x="-40" y="-35" width="80" height="70" rx="10" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
      <text x="0" y="-5" font-family="Courier New" font-size="12" fill="#60a5fa" text-anchor="middle">&lt;/&gt;</text>
      <text x="0" y="15" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">CODE</text>
      <polygon points="45,0 55,-8 55,8" fill="#3b82f6" opacity="0.5"/>
    </g>
    <g transform="translate(-100,0)">
      <rect x="-40" y="-35" width="80" height="70" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
      <circle cx="0" cy="-5" r="15" fill="none" stroke="#f59e0b" stroke-width="2" opacity="0.6"/>
      <circle cx="0" cy="-5" r="5" fill="#f59e0b" opacity="0.4"/>
      <text x="0" y="18" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">BUILD</text>
      <polygon points="45,0 55,-8 55,8" fill="#f59e0b" opacity="0.5"/>
    </g>
    <g transform="translate(100,0)">
      <rect x="-40" y="-35" width="80" height="70" rx="10" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
      <path d="M-8,-12 L-2,0 L12,-16" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
      <text x="0" y="18" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">TEST</text>
      <polygon points="45,0 55,-8 55,8" fill="#10b981" opacity="0.5"/>
    </g>
    <g transform="translate(300,0)">
      <rect x="-40" y="-35" width="80" height="70" rx="10" fill="#1e293b" stroke="#8b5cf6" stroke-width="2"/>
      <path d="M0,-18 L12,2 L4,2 L4,14 L-4,14 L-4,2 L-12,2 Z" fill="#8b5cf6" opacity="0.5" transform="rotate(180,0,-2)"/>
      <text x="0" y="18" font-family="Courier New" font-size="9" fill="#94a3b8" text-anchor="middle">DEPLOY</text>
    </g>
  </g>"""


def scene_chain() -> str:
    return """
  <g transform="translate(600,240)">
    <g fill="#1e293b" stroke="#f97316" stroke-width="2">
      <rect x="-310" y="-30" width="100" height="65" rx="8"/>
      <rect x="-160" y="-30" width="100" height="65" rx="8"/>
      <rect x="-10" y="-30" width="100" height="65" rx="8"/>
      <rect x="140" y="-30" width="100" height="65" rx="8"/>
      <rect x="290" y="-30" width="100" height="65" rx="8"/>
    </g>
    <g font-family="Courier New" text-anchor="middle" opacity="0.7">
      <text x="-260" y="-5" font-size="8" fill="#fdba74">BLOCK 101</text>
      <text x="-260" y="12" font-size="7" fill="#94a3b8">0xa3f2...</text>
      <text x="-110" y="-5" font-size="8" fill="#fdba74">BLOCK 102</text>
      <text x="-110" y="12" font-size="7" fill="#94a3b8">0x7b1c...</text>
      <text x="40" y="-5" font-size="8" fill="#fdba74">BLOCK 103</text>
      <text x="40" y="12" font-size="7" fill="#94a3b8">0xd9e4...</text>
      <text x="190" y="-5" font-size="8" fill="#fdba74">BLOCK 104</text>
      <text x="340" y="-5" font-size="8" fill="#fdba74">BLOCK 105</text>
    </g>
    <g stroke="#f97316" stroke-width="2.5" opacity="0.5">
      <line x1="-210" y1="2" x2="-160" y2="2"/><line x1="-60" y1="2" x2="-10" y2="2"/>
      <line x1="90" y1="2" x2="140" y2="2"/><line x1="240" y1="2" x2="290" y2="2"/>
    </g>
    <g fill="#f97316" opacity="0.5">
      <polygon points="-165,2 -155,-4 -155,8"/><polygon points="-15,2 -5,-4 -5,8"/>
      <polygon points="135,2 145,-4 145,8"/><polygon points="285,2 295,-4 295,8"/>
    </g>
  </g>
  <g transform="translate(600,370)">
    <g stroke="#f97316" stroke-width="1" opacity="0.25">
      <line x1="-120" y1="0" x2="0" y2="50"/><line x1="120" y1="0" x2="0" y2="50"/>
      <line x1="-120" y1="0" x2="120" y2="0"/>
    </g>
    <g fill="#1e293b" stroke="#f97316" stroke-width="1.5">
      <circle cx="-120" cy="0" r="14"/><circle cx="120" cy="0" r="14"/><circle cx="0" cy="50" r="14"/>
    </g>
    <g font-family="Courier New" font-size="7" fill="#fdba74" text-anchor="middle">
      <text x="-120" y="3">N1</text><text x="120" y="3">N2</text><text x="0" y="53">N3</text>
    </g>
  </g>"""


def scene_threat_v2() -> str:
    """Shield and firewall variant"""
    return """
  <g transform="translate(600,255)">
    <!-- Large shield outline -->
    <path d="M0,-140 C80,-140 140,-100 140,0 C140,80 80,160 0,180 C-80,160 -140,80 -140,0 C-140,-100 -80,-140 0,-140Z"
          fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" stroke-width="2" opacity="0.6"/>
    <path d="M0,-100 C55,-100 100,-70 100,0 C100,55 55,110 0,130 C-55,110 -100,55 -100,0 C-100,-70 -55,-100 0,-100Z"
          fill="#ef4444" fill-opacity="0.06" stroke="#fca5a5" stroke-width="1.5" opacity="0.4"/>
    <!-- Checkmark inside shield -->
    <path d="M-25,10 L-8,30 L30,-20" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.7"/>
    <!-- Firewall bricks -->
    <g opacity="0.3">
      <rect x="-250" y="-30" width="80" height="25" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
      <rect x="-250" y="5" width="80" height="25" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
      <rect x="-250" y="40" width="80" height="25" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
      <rect x="170" y="-30" width="80" height="25" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
      <rect x="170" y="5" width="80" height="25" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
      <rect x="170" y="40" width="80" height="25" rx="3" fill="#1e293b" stroke="#ef4444" stroke-width="1.2"/>
    </g>
  </g>"""


def scene_threat_v3() -> str:
    """Radar scanning variant"""
    return """
  <g transform="translate(600,255)">
    <!-- Radar circles -->
    <circle cx="0" cy="0" r="140" fill="none" stroke="#ef4444" stroke-width="1" opacity="0.15"/>
    <circle cx="0" cy="0" r="105" fill="none" stroke="#ef4444" stroke-width="1" opacity="0.2"/>
    <circle cx="0" cy="0" r="70" fill="none" stroke="#ef4444" stroke-width="1.5" opacity="0.3"/>
    <circle cx="0" cy="0" r="35" fill="none" stroke="#ef4444" stroke-width="1.5" opacity="0.4"/>
    <circle cx="0" cy="0" r="6" fill="#ef4444" opacity="0.6"/>
    <!-- Radar sweep line -->
    <line x1="0" y1="0" x2="100" y2="-100" stroke="#fca5a5" stroke-width="2" opacity="0.5"/>
    <path d="M0,0 L70,-70 A100,100 0 0,1 100,0 Z" fill="#ef4444" fill-opacity="0.08"/>
    <!-- Cross hairs -->
    <line x1="-145" y1="0" x2="145" y2="0" stroke="#475569" stroke-width="0.5" opacity="0.3"/>
    <line x1="0" y1="-145" x2="0" y2="145" stroke="#475569" stroke-width="0.5" opacity="0.3"/>
    <!-- Threat dots -->
    <circle cx="60" cy="-80" r="5" fill="#ef4444" opacity="0.7"/>
    <circle cx="60" cy="-80" r="10" fill="none" stroke="#ef4444" stroke-width="1" opacity="0.4"/>
    <circle cx="-40" cy="50" r="4" fill="#f59e0b" opacity="0.6"/>
    <circle cx="-40" cy="50" r="8" fill="none" stroke="#f59e0b" stroke-width="1" opacity="0.3"/>
    <circle cx="90" cy="30" r="3" fill="#f59e0b" opacity="0.5"/>
  </g>"""


def scene_neural_v2() -> str:
    """Circuit brain variant"""
    return """
  <g transform="translate(600,255)">
    <!-- Brain outline -->
    <path d="M0,-110 C60,-110 110,-70 120,-20 C130,30 100,80 60,100 C30,115 -30,115 -60,100 C-100,80 -130,30 -120,-20 C-110,-70 -60,-110 0,-110Z"
          fill="#6366f1" fill-opacity="0.05" stroke="#818cf8" stroke-width="2" opacity="0.5"/>
    <!-- Center division -->
    <path d="M0,-110 C10,-60 -10,0 5,50 C10,80 0,100 0,100"
          fill="none" stroke="#a5b4fc" stroke-width="1.5" opacity="0.4"/>
    <!-- Circuit traces -->
    <g stroke="#818cf8" stroke-width="1.5" opacity="0.4" fill="none">
      <path d="M-60,-50 L-30,-50 L-30,-20 L0,-20"/>
      <path d="M60,-50 L30,-50 L30,-20 L0,-20"/>
      <path d="M-80,20 L-40,20 L-40,50 L0,50"/>
      <path d="M80,20 L40,20 L40,50 L0,50"/>
    </g>
    <!-- Junction dots -->
    <circle cx="0" cy="-20" r="6" fill="#818cf8" opacity="0.6"/>
    <circle cx="0" cy="50" r="5" fill="#a5b4fc" opacity="0.5"/>
    <circle cx="-60" cy="-50" r="4" fill="#60a5fa" opacity="0.5"/>
    <circle cx="60" cy="-50" r="4" fill="#60a5fa" opacity="0.5"/>
    <circle cx="-80" cy="20" r="3.5" fill="#a78bfa" opacity="0.5"/>
    <circle cx="80" cy="20" r="3.5" fill="#a78bfa" opacity="0.5"/>
    <!-- Pulse rings -->
    <circle cx="0" cy="-20" r="18" fill="none" stroke="#6366f1" stroke-width="1" opacity="0.2"/>
    <circle cx="0" cy="-20" r="35" fill="none" stroke="#6366f1" stroke-width="0.5" opacity="0.1"/>
  </g>"""


def scene_neural_v3() -> str:
    """Transformer layers variant"""
    return """
  <g transform="translate(600,255)">
    <!-- Stacked layers -->
    <g opacity="0.6">
      <rect x="-120" y="-120" width="240" height="45" rx="8" fill="#1e293b" stroke="#818cf8" stroke-width="1.5"/>
      <text x="0" y="-93" font-family="Courier New" font-size="10" fill="#a5b4fc" text-anchor="middle">ATTENTION</text>
      <rect x="-120" y="-60" width="240" height="45" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="1.5"/>
      <text x="0" y="-33" font-family="Courier New" font-size="10" fill="#818cf8" text-anchor="middle">FEED FORWARD</text>
      <rect x="-120" y="0" width="240" height="45" rx="8" fill="#1e293b" stroke="#818cf8" stroke-width="1.5"/>
      <text x="0" y="27" font-family="Courier New" font-size="10" fill="#a5b4fc" text-anchor="middle">ATTENTION</text>
      <rect x="-120" y="60" width="240" height="45" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="1.5"/>
      <text x="0" y="87" font-family="Courier New" font-size="10" fill="#818cf8" text-anchor="middle">OUTPUT</text>
    </g>
    <!-- Arrows between layers -->
    <g stroke="#6366f1" stroke-width="1.5" opacity="0.3" fill="#6366f1">
      <line x1="0" y1="-75" x2="0" y2="-62"/><polygon points="-4,-64 0,-58 4,-64"/>
      <line x1="0" y1="-15" x2="0" y2="-2"/><polygon points="-4,-4 0,2 4,-4"/>
      <line x1="0" y1="45" x2="0" y2="58"/><polygon points="-4,56 0,62 4,56"/>
    </g>
    <!-- Side connections -->
    <g stroke="#a5b4fc" stroke-width="1" opacity="0.2">
      <path d="M125,-97 C170,-97 170,-37 125,-37" fill="none"/>
      <path d="M125,23 C170,23 170,83 125,83" fill="none"/>
    </g>
  </g>"""


def scene_cloud_v2() -> str:
    """Multi-cloud architecture variant"""
    return """
  <g transform="translate(600,240)">
    <!-- Three cloud shapes -->
    <g opacity="0.5">
      <path d="M-200,-20 C-215,-20 -225,-10 -225,0 C-225,10 -215,20 -200,20 L-140,20 C-125,20 -115,10 -115,0 C-115,-10 -125,-20 -130,-20 C-132,-35 -145,-45 -160,-45 C-180,-45 -195,-35 -200,-20Z"
            fill="#3b82f6" fill-opacity="0.08" stroke="#60a5fa" stroke-width="1.5"/>
      <text x="-170" y="5" font-family="Courier New" font-size="9" fill="#60a5fa" text-anchor="middle">AWS</text>
    </g>
    <g opacity="0.5">
      <path d="M-30,-30 C-50,-30 -60,-15 -60,0 C-60,15 -50,30 -30,30 L30,30 C50,30 60,15 60,0 C60,-15 50,-30 35,-30 C32,-50 15,-65 0,-65 C-20,-65 -35,-50 -30,-30Z"
            fill="#f59e0b" fill-opacity="0.08" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="0" y="5" font-family="Courier New" font-size="9" fill="#fbbf24" text-anchor="middle">GCP</text>
    </g>
    <g opacity="0.5">
      <path d="M140,-20 C125,-20 115,-10 115,0 C115,10 125,20 140,20 L200,20 C215,20 225,10 225,0 C225,-10 215,-20 210,-20 C208,-35 195,-45 180,-45 C160,-45 145,-35 140,-20Z"
            fill="#0ea5e9" fill-opacity="0.08" stroke="#38bdf8" stroke-width="1.5"/>
      <text x="170" y="5" font-family="Courier New" font-size="9" fill="#38bdf8" text-anchor="middle">Azure</text>
    </g>
    <!-- Connection lines -->
    <g stroke="#475569" stroke-width="1" stroke-dasharray="4,3" opacity="0.3">
      <line x1="-115" y1="0" x2="-60" y2="0"/>
      <line x1="60" y1="0" x2="115" y2="0"/>
      <line x1="0" y1="30" x2="0" y2="70"/>
    </g>
  </g>
  <g transform="translate(600,330)">
    <rect x="-80" y="0" width="160" height="50" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="1.5" opacity="0.6"/>
    <text x="0" y="30" font-family="Courier New" font-size="11" fill="#6ee7b7" text-anchor="middle">SECURITY HUB</text>
  </g>"""


def scene_pipeline_v2() -> str:
    """DevOps infinity loop variant"""
    return """
  <g transform="translate(600,255)">
    <!-- Infinity/figure-8 loop -->
    <path d="M-80,0 C-80,-60 -160,-60 -160,0 C-160,60 -80,60 -80,0 C-80,-60 0,-60 0,0"
          fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.3"/>
    <path d="M80,0 C80,60 160,60 160,0 C160,-60 80,-60 80,0 C80,60 0,60 0,0"
          fill="none" stroke="#3b82f6" stroke-width="2.5" opacity="0.3"/>
    <!-- Stage labels around the loop -->
    <g font-family="Courier New" font-size="9" text-anchor="middle" opacity="0.7">
      <circle cx="-160" cy="-35" r="18" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="-160" y="-32" fill="#fbbf24">PLAN</text>
      <circle cx="-120" cy="35" r="18" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="-120" y="38" fill="#fbbf24">CODE</text>
      <circle cx="-40" cy="-35" r="18" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="-40" y="-32" fill="#fbbf24">BUILD</text>
      <circle cx="40" cy="35" r="18" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="40" y="38" fill="#60a5fa">TEST</text>
      <circle cx="120" cy="-35" r="18" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="120" y="-32" fill="#60a5fa">DEPLOY</text>
      <circle cx="160" cy="35" r="18" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="160" y="38" fill="#60a5fa">MONITOR</text>
    </g>
    <!-- Dev / Ops labels -->
    <text x="-120" y="-75" font-family="Arial" font-size="11" fill="#f59e0b" text-anchor="middle" opacity="0.5">Dev</text>
    <text x="120" y="-75" font-family="Arial" font-size="11" fill="#3b82f6" text-anchor="middle" opacity="0.5">Ops</text>
  </g>"""


def scene_chain_v2() -> str:
    """Distributed ledger variant"""
    return """
  <g transform="translate(600,255)">
    <!-- Central ledger -->
    <rect x="-60" y="-80" width="120" height="160" rx="10" fill="#1e293b" stroke="#f97316" stroke-width="2" opacity="0.7"/>
    <g font-family="Courier New" font-size="8" fill="#fdba74" opacity="0.6">
      <text x="-40" y="-55">TX: 0xa3f2..</text>
      <text x="-40" y="-38">TX: 0x7b1c..</text>
      <text x="-40" y="-21">TX: 0xd9e4..</text>
      <line x1="-45" y1="-12" x2="45" y2="-12" stroke="#f97316" stroke-width="0.5" opacity="0.3"/>
      <text x="-40" y="5">TX: 0x2ef8..</text>
      <text x="-40" y="22">TX: 0xc1a7..</text>
      <text x="-40" y="39">TX: 0xb5d3..</text>
      <line x1="-45" y1="48" x2="45" y2="48" stroke="#f97316" stroke-width="0.5" opacity="0.3"/>
      <text x="-40" y="65">TX: 0x9f6e..</text>
    </g>
    <!-- Connected nodes -->
    <g opacity="0.4">
      <circle cx="-200" cy="-60" r="25" fill="#1e293b" stroke="#f97316" stroke-width="1.5"/>
      <text x="-200" y="-57" font-family="Courier New" font-size="8" fill="#fdba74" text-anchor="middle">NODE</text>
      <circle cx="200" cy="-60" r="25" fill="#1e293b" stroke="#f97316" stroke-width="1.5"/>
      <text x="200" y="-57" font-family="Courier New" font-size="8" fill="#fdba74" text-anchor="middle">NODE</text>
      <circle cx="-200" cy="60" r="25" fill="#1e293b" stroke="#f97316" stroke-width="1.5"/>
      <text x="-200" y="63" font-family="Courier New" font-size="8" fill="#fdba74" text-anchor="middle">NODE</text>
      <circle cx="200" cy="60" r="25" fill="#1e293b" stroke="#f97316" stroke-width="1.5"/>
      <text x="200" y="63" font-family="Courier New" font-size="8" fill="#fdba74" text-anchor="middle">NODE</text>
    </g>
    <!-- Connection lines -->
    <g stroke="#f97316" stroke-width="1" stroke-dasharray="6,3" opacity="0.25">
      <line x1="-175" y1="-50" x2="-60" y2="-30"/>
      <line x1="175" y1="-50" x2="60" y2="-30"/>
      <line x1="-175" y1="50" x2="-60" y2="30"/>
      <line x1="175" y1="50" x2="60" y2="30"/>
    </g>
  </g>"""


SCENE_MAP = {
    "threat": scene_threat,
    "neural": scene_neural,
    "cloud": scene_cloud,
    "pipeline": scene_pipeline,
    "chain": scene_chain,
}

SCENE_VARIANTS = {
    "threat": [scene_threat, scene_threat_v2, scene_threat_v3],
    "neural": [scene_neural, scene_neural_v2, scene_neural_v3],
    "cloud": [scene_cloud, scene_cloud_v2],
    "pipeline": [scene_pipeline, scene_pipeline_v2],
    "chain": [scene_chain, scene_chain_v2],
}


def select_scene_variant(theme: str, filename: str):
    """Deterministically select a scene variant based on filename hash."""
    variants = SCENE_VARIANTS.get(theme, [scene_threat])
    hash_val = int(hashlib.md5(filename.encode()).hexdigest(), 16)
    return variants[hash_val % len(variants)]


def generate_visual_svg(filename: str) -> str:
    theme = select_theme(filename)
    primary, accent = THEME_COLORS.get(theme, ("#3b82f6", "#93c5fd"))
    title = extract_title(filename)
    date_str = extract_date(filename)
    subtopics = extract_subtopics(filename)
    scene_fn = select_scene_variant(theme, filename)

    # Determine if this is a digest or article
    is_digest = "digest" in filename.lower() or "weekly" in filename.lower()
    badge_text = "WEEKLY DIGEST" if is_digest else "TECH BLOG"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a1a"/>
      <stop offset="50%" style="stop-color:#0f1629"/>
      <stop offset="100%" style="stop-color:#1a0a2e"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="sg"><feGaussianBlur stdDeviation="25"/></filter>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)"/>

  <circle cx="400" cy="250" r="200" fill="{primary}" opacity="0.04" filter="url(#sg)"/>
  <circle cx="800" cy="300" r="180" fill="{primary}" opacity="0.03" filter="url(#sg)"/>
  <circle cx="200" cy="400" r="150" fill="#8b5cf6" opacity="0.02" filter="url(#sg)"/>
{scene_fn()}
  <text x="600" y="510" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{title}</text>
  <text x="600" y="548" font-family="Arial, sans-serif" font-size="16" fill="#94a3b8" text-anchor="middle">{subtopics}</text>

  <rect x="40" y="25" width="160" height="32" rx="16" fill="{primary}" opacity="0.2" stroke="{primary}" stroke-width="1"/>
  <text x="120" y="47" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="{accent}" text-anchor="middle">{badge_text}</text>

  <rect x="1000" y="25" width="160" height="32" rx="16" fill="#3b82f6" opacity="0.2" stroke="#3b82f6" stroke-width="1"/>
  <text x="1080" y="47" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#93c5fd" text-anchor="middle">{date_str}</text>

  <line x1="50" y1="590" x2="1150" y2="590" stroke="#334155" stroke-width="1" opacity="0.5"/>
  <text x="1150" y="615" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""
    return svg


def is_card_based(filepath: str) -> bool:
    try:
        with open(filepath, "r") as f:
            content = f.read(2000)
        return "cardGradient" in content
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert card-based SVGs to visual illustrations")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--file", type=str, help="Convert specific file")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    if args.file:
        targets = [Path(args.file)]
    else:
        targets = sorted(IMAGES_DIR.glob("*.svg"))

    card_based = [f for f in targets if is_card_based(str(f))]

    if not card_based:
        print("No card-based SVGs found.")
        return

    print(f"Found {len(card_based)} card-based SVGs to convert:")
    for f in card_based[:10]:
        theme = select_theme(f.name)
        print(f"  [{theme:8s}] {f.name}")
    if len(card_based) > 10:
        print(f"  ... and {len(card_based) - 10} more")

    if args.dry_run:
        print("\nDry run - no files written.")
        return

    if not args.yes:
        confirm = input(f"\nConvert {len(card_based)} files? [y/N] ")
        if confirm.lower() != "y":
            print("Aborted.")
            return

    converted = 0
    for f in card_based:
        try:
            svg = generate_visual_svg(f.name)
            # Validate XML
            ET.fromstring(svg)
            with open(f, "w") as fh:
                fh.write(svg)
            converted += 1
            print(f"  OK: {f.name}")
        except Exception as e:
            print(f"  ERROR: {f.name} - {e}")

    print(f"\nConverted {converted}/{len(card_based)} SVGs.")


if __name__ == "__main__":
    main()
