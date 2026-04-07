"""SVG image generation functions."""

import logging
import re
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scripts.news.config import (
    CATEGORY_SVG_CONFIG,
    SVG_MAX_FOCUS_LABELS,
    SVG_MAX_LABEL_CHARS,
    SVG_MAX_SUBTITLE_CHARS,
    SVG_TEMPLATE_BEFORE_AFTER,
    SVG_TEMPLATE_HUB_SPOKE,
    SVG_TEMPLATE_TIMELINE,
)


def _escape_svg_text(text: str) -> str:
    """SVG 텍스트 이스케이프 처리"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _to_english_svg_text(text: str) -> str:
    """SVG 텍스트에서 비영문 문자 제거 (SVG는 영문만 허용)"""
    result = []
    for char in text:
        if ord(char) < 128:  # ASCII
            result.append(char)
        elif unicodedata.category(char).startswith("L"):
            # Non-ASCII letter - skip (Korean, etc.)
            continue
        else:
            result.append(" ")
    # Clean up multiple spaces and orphaned punctuation
    cleaned = "".join(result)
    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)  # normalize comma spacing
    cleaned = re.sub(r"(,\s*){2,}", ", ", cleaned)  # collapse repeated commas
    cleaned = " ".join(cleaned.split())  # normalize whitespace
    cleaned = cleaned.strip(" ,;:-")  # strip leading/trailing punctuation
    if not cleaned:
        return "Security News Update"
    return cleaned


def _truncate_text(text: str, max_len: int) -> str:
    """텍스트 길이 제한 (단어 경계에서 자름)"""
    if len(text) <= max_len:
        return text
    # Find last space before max_len to avoid cutting mid-word
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.6:  # Only use word boundary if reasonable
        return truncated[:last_space]
    return truncated.rstrip(" ,.")


def _extract_key_topics(news_items: List[Dict]) -> List[str]:
    """뉴스에서 핵심 토픽 추출"""
    topics = []
    keywords = [
        "Zero-Day",
        "CVE",
        "Vulnerability",
        "Patch",
        "Update",
        "AI",
        "ML",
        "Cloud",
        "Kubernetes",
        "Docker",
        "AWS",
        "Azure",
        "GCP",
        "Security",
        "Threat",
        "Malware",
        "Ransomware",
        "Botnet",
        "Bitcoin",
        "Ethereum",
        "DeFi",
        "Web3",
        "Blockchain",
        "LLM",
        "GPT",
        "Agent",
        "Data",
        "Palantir",
        "Tesla",
        "Apple",
        "Rust",
        "Go",
        "Open-Source",
        "API",
    ]

    for item in news_items[:6]:
        title = item.get("title", "")
        for kw in keywords:
            if kw.lower() in title.lower() and kw not in topics:
                topics.append(kw)
                if len(topics) >= 4:
                    return topics
    return topics[:4] if topics else ["Security", "Cloud", "DevOps", "AI"]


# Constants are imported from config; removed duplicate local definitions


def _normalize_svg_focus_label(label: str) -> str:
    label = re.sub(r"\s+", " ", label.strip().upper())
    label = re.sub(r"[^A-Z0-9 /+-]", "", label)
    return _truncate_text(label, SVG_MAX_LABEL_CHARS)


def _compose_svg_subtitle(labels: List[str]) -> str:
    subtitle = "  ".join(labels[:SVG_MAX_FOCUS_LABELS])
    return _truncate_text(subtitle, SVG_MAX_SUBTITLE_CHARS)


def _extract_visual_focus_labels(news_items: List[Dict], limit: int = 3) -> List[str]:
    """Return short English labels for low-text digest SVGs."""
    label_patterns = [
        (r"zero-day|0-day|제로데이|cve-", "ZERO DAY"),
        (r"ransomware|랜섬웨어", "RANSOM"),
        (r"byovd|driver|edr", "BYOVD"),
        (r"dns|exfil|data leak|유출", "DNS EXFIL"),
        (r"malware|악성코드", "MALWARE"),
        (r"telnet", "TELNETD"),
        (r"cisco|fmc", "FMC"),
        (r"dprk|north korea|북한", "DPRK"),
        (r"ai agent|agentic|llm|model", "AI AGENT"),
        (r"kubernetes|k8s|gke|cluster", "K8S"),
        (r"cloud|aws|azure|gcp", "CLOUD"),
        (r"patch|update", "PATCH"),
    ]

    labels: List[str] = []
    seen: set[str] = set()
    for item in news_items[:8]:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        for pattern, label in label_patterns:
            normalized = _normalize_svg_focus_label(label)
            if re.search(pattern, text) and normalized and normalized not in seen:
                seen.add(normalized)
                labels.append(normalized)
                if len(labels) >= limit:
                    return labels

    for topic in _extract_key_topics(news_items):
        label = _normalize_svg_focus_label(_to_english_svg_text(topic))
        if label and label not in seen:
            seen.add(label)
            labels.append(label)
            if len(labels) >= limit:
                break

    return labels[:limit] if labels else ["SECURITY", "CLOUD", "AI"]


def _svg_icon_templates() -> Dict[str, str]:
    return {
        "malware": '<circle r="16" fill="{c}" opacity="0.2"/><circle cx="-12" cy="-8" r="6" fill="{c}" opacity="0.5"/><circle cx="12" cy="8" r="6" fill="{c}" opacity="0.5"/><circle cx="8" cy="-12" r="4" fill="{c}" opacity="0.4"/>',
        "ransom": '<rect x="-22" y="-4" width="44" height="36" rx="8" fill="#221617" stroke="{c}" stroke-width="2"/><path d="M-12 -4 v-16 c0-18 24-18 24 0 v16" stroke="{c}" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="0" cy="16" r="6" fill="{c}"/><rect x="-2" y="20" width="4" height="10" rx="2" fill="{c}"/>',
        "phish": '<path d="M-20 -8 L0 12 L20 -8" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/><rect x="-24" y="-16" width="48" height="36" rx="4" fill="none" stroke="{c}" stroke-width="2"/><circle cx="0" cy="-24" r="4" fill="{c}"/>',
        "cve": '<rect x="-20" y="-16" width="40" height="32" rx="6" fill="#1a1020" stroke="{c}" stroke-width="2"/><text x="0" y="-2" font-family="Courier New" font-size="11" font-weight="700" fill="{c}" text-anchor="middle">CVE</text><text x="0" y="12" font-family="Courier New" font-size="8" fill="{c}" text-anchor="middle" opacity="0.7">PATCH</text>',
        "cloud": '<path d="M-16 10 C-28 10 -32 -2 -32 -10 C-32 -20 -24 -26 -14 -26 C-10 -36 0 -42 10 -42 C24 -42 32 -32 32 -26 C40 -26 44 -20 44 -10 C44 -2 40 10 28 10 Z" fill="#0b1628" stroke="{c}" stroke-width="2" transform="scale(0.7)"/>',
        "ai": '<rect x="-28" y="-20" width="56" height="40" rx="8" fill="#111c35" stroke="{c}" stroke-width="2"/><circle cx="0" cy="-4" r="14" fill="#12345c" stroke="{c}" stroke-width="1.5"/><text x="0" y="1" font-family="Arial" font-size="12" font-weight="700" fill="{c}" text-anchor="middle">AI</text>',
        "k8s": '<circle cx="-16" cy="-12" r="12" fill="#09261d" stroke="{c}" stroke-width="1.5"/><circle cx="16" cy="-12" r="12" fill="#09261d" stroke="{c}" stroke-width="1.5"/><circle cx="0" cy="16" r="12" fill="#09261d" stroke="{c}" stroke-width="1.5"/><path d="M-8 -6 L8 -6 M-12 2 L0 14 M12 2 L0 14" stroke="{c}" stroke-width="1.5"/>',
        "dns": '<circle r="16" fill="{c}" opacity="0.15"/><circle cx="-10" cy="-6" r="5" fill="{c}" opacity="0.6"/><circle cx="10" cy="6" r="5" fill="{c}" opacity="0.6"/><circle cx="12" cy="-10" r="3" fill="{c}" opacity="0.4"/>',
        "edr": '<rect x="-22" y="-18" width="44" height="36" rx="6" fill="#0f172a" stroke="{c}" stroke-width="2"/><path d="M-12 -6 L-4 6 L14 -10" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/><line x1="-14" y1="14" x2="14" y2="14" stroke="{c}" stroke-width="1.5" opacity="0.5"/>',
        "default": '<circle r="18" fill="{c}" opacity="0.18"/><circle r="8" fill="{c}" opacity="0.3"/>',
    }


def _match_svg_icon(label: str) -> str:
    lbl = label.lower()
    for key in _svg_icon_templates():
        if key in lbl:
            return key
    if any(k in lbl for k in ["exploit", "vuln", "patch", "zero"]):
        return "cve"
    if any(k in lbl for k in ["encrypt", "lock", "ransom"]):
        return "ransom"
    if any(k in lbl for k in ["aws", "gcp", "azure", "cloud"]):
        return "cloud"
    if any(k in lbl for k in ["agent", "llm", "model"]):
        return "ai"
    if any(k in lbl for k in ["k8s", "kube", "gke", "eks"]):
        return "k8s"
    if any(k in lbl for k in ["bot", "worm", "trojan"]):
        return "malware"
    return "default"


def _select_svg_template(news_items: List[Dict], focus_labels: List[str]) -> str:
    title_joined = " ".join(item.get("title", "") for item in news_items[:8]).lower()
    joined = " ".join(
        f"{item.get('title', '')} {item.get('summary', '')}" for item in news_items[:8]
    ).lower()
    before_after_patterns = [
        r"\bbefore\b",
        r"\bafter\b",
        r"\bfrom\b.{0,80}\bto\b",
        r"\b(?:replace|replaced|replacing|migration|migrate|migrates|migrating)\b",
        r"\b(?:upgrade|downgrade|rollback|rollbacks|rollbacked|rollbacking|swap|swaps|swapped|transition|transitions|transitioning)\b",
        r"\bvs\.?(?!\s*code\b)\b",
        r"\bversus\b",
        r"비교",
        r"전환",
        r"이전.*이후",
        r"마이그레이션",
        r"교체",
    ]
    if any(re.search(pattern, joined) for pattern in before_after_patterns):
        return SVG_TEMPLATE_BEFORE_AFTER

    digest_patterns = [
        r"\bweekly\b",
        r"\broundup\b",
        r"\bdigest\b",
        r"주간",
        r"다이제스트",
        r"종합",
        r"요약",
    ]
    timeline_patterns = [
        r"\btimeline\b",
        r"\bcampaign\b",
        r"\bwave\b",
        r"\bseries\b",
        r"\bpatch tuesday\b",
        r"위협 인텔리전스",
        r"패치 화요일",
        r"캠페인",
        r"연쇄",
        r"흐름",
    ]
    incident_patterns = [
        r"\bzero-day\b",
        r"\b0-day\b",
        r"cve-\d{4}-\d+",
        r"\bpatch(?:ed|ing)?\b",
        r"\bransom(?:ware)?\b",
        r"\bmalware\b",
        r"\bexploit\b",
        r"\battack\b",
        r"\bbreach\b",
        r"\bincident\b",
        r"\bthreat\b",
        r"\bbotnet\b",
        r"제로데이",
        r"패치",
        r"랜섬웨어",
        r"악성코드",
        r"봇넷",
        r"공격",
        r"침해",
        r"위협",
        r"취약점",
    ]
    hub_patterns = [
        r"\bai\b",
        r"\bagentic\b",
        r"\bagent\b",
        r"\bllm\b",
        r"\bcloud\b",
        r"\baws\b",
        r"\bazure\b",
        r"\bgcp\b",
        r"\bkubernetes\b",
        r"\bk8s\b",
        r"\bdocker\b",
        r"\bblockchain\b",
        r"\bbitcoin\b",
        r"\bdevops\b",
        r"\bdata\b",
        r"\brust\b",
        r"\bgo\b",
        r"에이전트",
        r"클라우드",
        r"쿠버네티스",
        r"블록체인",
        r"비트코인",
        r"데이터",
        r"개발자",
        r"플랫폼",
    ]
    digest_score = sum(1 for pattern in digest_patterns if re.search(pattern, joined))
    timeline_score = sum(
        1 for pattern in timeline_patterns if re.search(pattern, joined)
    )
    incident_score = sum(
        1 for pattern in incident_patterns if re.search(pattern, joined)
    )
    title_incident_score = sum(
        1 for pattern in incident_patterns if re.search(pattern, title_joined)
    )
    hub_score = sum(1 for pattern in hub_patterns if re.search(pattern, joined))
    risk_focus_score = sum(
        1 for label in focus_labels if label in {"PATCH", "ZERO DAY", "RANSOM"}
    )

    if timeline_score >= 1:
        return SVG_TEMPLATE_TIMELINE
    if (
        digest_score >= 1
        and hub_score >= 3
        and title_incident_score == 0
        and incident_score <= 1
    ):
        return SVG_TEMPLATE_HUB_SPOKE
    if digest_score >= 1 and (incident_score >= 2 or title_incident_score >= 1):
        return SVG_TEMPLATE_TIMELINE
    if incident_score >= 2 and hub_score <= 2:
        return SVG_TEMPLATE_TIMELINE
    if risk_focus_score >= 1 and hub_score <= 1:
        return SVG_TEMPLATE_TIMELINE
    return SVG_TEMPLATE_HUB_SPOKE


def _svg_base_frame(
    accent: str, headline: str, subtitle: str, date_display: str
) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{_escape_svg_text(headline)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120"/>
      <stop offset="55%" stop-color="#151b32"/>
      <stop offset="100%" stop-color="#181024"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="18" flood-color="#020617" flood-opacity="0.5"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="210" cy="170" r="180" fill="{accent}" opacity="0.14" filter="url(#glow)"/>
  <circle cx="980" cy="220" r="170" fill="#2563eb" opacity="0.12" filter="url(#glow)"/>
  <circle cx="930" cy="500" r="180" fill="#f59e0b" opacity="0.1" filter="url(#glow)"/>
  <text x="90" y="164" font-family="Arial, sans-serif" font-size="52" font-weight="700" fill="#f8fafc">{headline}</text>
  <text x="92" y="204" font-family="Arial, sans-serif" font-size="20" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
"""


def _svg_footer(date_display: str) -> str:
    return f"""
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""


def _render_hub_spoke_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    node_colors = [accent, "#67e8f9", "#f59e0b"]
    node_positions = [(250, 360), (600, 210), (950, 360)]
    icons = _svg_icon_templates()
    svg = _svg_base_frame(accent, headline, subtitle, date_display)
    svg += f"""
  <g transform="translate(600 336)" filter="url(#shadow)">
    <circle r="102" fill="#111827" stroke="{accent}" stroke-width="2.5"/>
    <circle r="44" fill="#0f172a" stroke="#e2e8f0" stroke-width="2"/>
    <path d="M-18 0 h36" stroke="#e2e8f0" stroke-width="8" stroke-linecap="round"/>
    <path d="M0 -18 v36" stroke="#e2e8f0" stroke-width="8" stroke-linecap="round"/>
  </g>
"""
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        x, y = node_positions[idx]
        color = node_colors[idx % len(node_colors)]
        cx1 = 600 + (x - 600) * 0.3
        cy1 = 336 + (y - 336) * 0.1
        cx2 = 600 + (x - 600) * 0.7
        cy2 = 336 + (y - 336) * 0.9
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        svg += f"""
  <path d="M600 336 C{cx1:.0f} {cy1:.0f} {cx2:.0f} {cy2:.0f} {x} {y}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="12 10" stroke-linecap="round" opacity="0.8"/>
  <g transform="translate({x} {y})" filter="url(#shadow)">
    <circle r="58" fill="#0f172a" stroke="{color}" stroke-width="2"/>
    {icon_svg}
    <text x="0" y="92" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  </g>
"""
    return svg + _svg_footer(date_display)


def _render_timeline_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    node_colors = [accent, "#67e8f9", "#f59e0b"]
    centers = [250, 600, 950]
    icons = _svg_icon_templates()
    svg = _svg_base_frame(accent, headline, subtitle, date_display)
    svg += '  <line x1="180" y1="340" x2="1020" y2="340" stroke="#475569" stroke-width="4" stroke-dasharray="14 10" opacity="0.8"/>'
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        color = node_colors[idx % len(node_colors)]
        center = centers[idx]
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        svg += f"""
  <g transform="translate({center} 340)" filter="url(#shadow)">
    <circle r="56" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
  </g>
  <text x="{center}" y="448" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
"""
    return svg + _svg_footer(date_display)


def _render_before_after_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    left_label = focus_labels[0] if focus_labels else "BEFORE"
    right_label = focus_labels[1] if len(focus_labels) > 1 else "AFTER"
    center_label = focus_labels[2] if len(focus_labels) > 2 else "PATCH"
    icons = _svg_icon_templates()
    left_icon = icons[_match_svg_icon(left_label)].replace("{c}", "#ef4444")
    right_icon = icons[_match_svg_icon(right_label)].replace("{c}", "#22c55e")
    center_icon = icons[_match_svg_icon(center_label)].replace("{c}", accent)
    svg = _svg_base_frame(accent, headline, subtitle, date_display)
    svg += f"""
  <g transform="translate(250 340)" filter="url(#shadow)">
    <rect x="-85" y="-85" width="170" height="170" rx="28" fill="#0f172a" stroke="#ef4444" stroke-width="2.5"/>
    {left_icon}
  </g>
  <g transform="translate(600 340)" filter="url(#shadow)">
    <circle r="62" fill="#111827" stroke="{accent}" stroke-width="2.5"/>
    {center_icon}
  </g>
  <g transform="translate(950 340)" filter="url(#shadow)">
    <rect x="-85" y="-85" width="170" height="170" rx="28" fill="#0f172a" stroke="#22c55e" stroke-width="2.5"/>
    {right_icon}
  </g>
  <path d="M340 340 C430 300 500 300 538 340" fill="none" stroke="#ef4444" stroke-width="3" stroke-dasharray="12 10"/>
  <path d="M662 340 C720 300 820 300 860 340" fill="none" stroke="#22c55e" stroke-width="3" stroke-dasharray="12 10"/>
  <text x="250" y="458" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#ef4444" text-anchor="middle">{_escape_svg_text(left_label)}</text>
  <text x="600" y="458" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="{accent}" text-anchor="middle">{_escape_svg_text(center_label)}</text>
  <text x="950" y="458" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#22c55e" text-anchor="middle">{_escape_svg_text(right_label)}</text>
"""
    return svg + _svg_footer(date_display)


def _render_fractured_core_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    """Style 0: Fractured Core - Central hexagon with orbiting nodes (red/cyan)."""
    node_colors = ["#ef4444", "#22d3ee", "#f59e0b"]
    icons = _svg_icon_templates()
    # Hexagon points for center shape
    hex_pts = "600,270 660,300 660,360 600,390 540,360 540,300"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{_escape_svg_text(headline)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#1e1030"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="20"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#020617" flood-opacity="0.6"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="600" cy="330" r="260" fill="#ef4444" opacity="0.06" filter="url(#glow)"/>
  <circle cx="600" cy="330" r="180" fill="#22d3ee" opacity="0.07" filter="url(#glow)"/>
  <!-- Fractured crack lines from center -->
  <line x1="600" y1="330" x2="160" y2="120" stroke="#ef4444" stroke-width="1.5" opacity="0.25"/>
  <line x1="600" y1="330" x2="1040" y2="110" stroke="#22d3ee" stroke-width="1.5" opacity="0.25"/>
  <line x1="600" y1="330" x2="600" y2="560" stroke="#f59e0b" stroke-width="1.5" opacity="0.20"/>
  <!-- Central hexagon -->
  <polygon points="{hex_pts}" fill="#111827" stroke="{accent}" stroke-width="3" filter="url(#shadow)"/>
  <polygon points="600,286 634,304 634,342 600,360 566,342 566,304" fill="#0f172a" stroke="#e2e8f0" stroke-width="1.5"/>
  <text x="600" y="336" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="#e2e8f0" text-anchor="middle">CORE</text>
  <!-- Orbit ring -->
  <circle cx="600" cy="330" r="148" fill="none" stroke="#334155" stroke-width="1" stroke-dasharray="8 6" opacity="0.5"/>
"""
    orbit_positions = [(452, 210), (748, 210), (600, 478)]
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        x, y = orbit_positions[idx]
        color = node_colors[idx % len(node_colors)]
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        svg += f"""  <line x1="600" y1="330" x2="{x}" y2="{y}" stroke="{color}" stroke-width="2" stroke-dasharray="10 8" opacity="0.6"/>
  <g transform="translate({x} {y})" filter="url(#shadow)">
    <circle r="52" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
    <text x="0" y="82" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  </g>
"""
    # WEEKLY DIGEST badge
    svg += f"""  <rect x="90" y="62" width="196" height="32" rx="6" fill="{accent}" opacity="0.18"/>
  <text x="188" y="83" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{accent}" text-anchor="middle" letter-spacing="2">WEEKLY DIGEST</text>
  <text x="90" y="134" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#f8fafc">{_escape_svg_text(headline)}</text>
  <text x="90" y="170" font-family="Arial,sans-serif" font-size="18" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""
    return svg


def _render_dossier_strike_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    """Style 1: Dossier Strike - Diagonal split with classified stamp motif (purple/gold)."""
    icons = _svg_icon_templates()
    node_colors = ["#a855f7", "#f59e0b", "#22d3ee"]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{_escape_svg_text(headline)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1a0a2e"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#020617" flood-opacity="0.6"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <!-- Diagonal divider -->
  <polygon points="0,0 820,0 560,630 0,630" fill="#110d20" opacity="0.7"/>
  <line x1="820" y1="0" x2="560" y2="630" stroke="#a855f7" stroke-width="3" opacity="0.5"/>
  <circle cx="200" cy="200" r="220" fill="#a855f7" opacity="0.08" filter="url(#glow)"/>
  <circle cx="1000" cy="400" r="200" fill="#f59e0b" opacity="0.08" filter="url(#glow)"/>
  <!-- Classified stamp rotated -->
  <g transform="translate(900 310) rotate(-22)">
    <rect x="-110" y="-38" width="220" height="76" rx="8" fill="none" stroke="#f59e0b" stroke-width="3" opacity="0.4"/>
    <text x="0" y="12" font-family="Arial,sans-serif" font-size="22" font-weight="700" fill="#f59e0b" text-anchor="middle" opacity="0.35" letter-spacing="4">CLASSIFIED</text>
  </g>
  <!-- Corner bracket marks -->
  <path d="M70 60 L70 90 L100 90" fill="none" stroke="#a855f7" stroke-width="2" opacity="0.5"/>
  <path d="M1130 60 L1130 90 L1100 90" fill="none" stroke="#a855f7" stroke-width="2" opacity="0.5"/>
  <path d="M70 570 L70 540 L100 540" fill="none" stroke="#a855f7" stroke-width="2" opacity="0.5"/>
  <path d="M1130 570 L1130 540 L1100 540" fill="none" stroke="#a855f7" stroke-width="2" opacity="0.5"/>
  <!-- WEEKLY DIGEST badge -->
  <rect x="90" y="62" width="196" height="32" rx="6" fill="#a855f7" opacity="0.18"/>
  <text x="188" y="83" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#a855f7" text-anchor="middle" letter-spacing="2">WEEKLY DIGEST</text>
  <text x="90" y="140" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#f8fafc">{_escape_svg_text(headline)}</text>
  <text x="90" y="176" font-family="Arial,sans-serif" font-size="18" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
"""
    node_positions = [(280, 360), (680, 280), (1000, 420)]
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        x, y = node_positions[idx]
        color = node_colors[idx % len(node_colors)]
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        svg += f"""  <g transform="translate({x} {y})" filter="url(#shadow)">
    <rect x="-58" y="-58" width="116" height="116" rx="14" fill="#0f172a" stroke="{color}" stroke-width="2"/>
    {icon_svg}
    <text x="0" y="84" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  </g>
"""
    svg += f"""  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""
    return svg


def _render_pipeline_triptych_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    """Style 2: Pipeline Triptych - Three vertical columns (cyan/green/orange)."""
    col_colors = ["#22d3ee", "#22c55e", "#f97316"]
    col_x = [260, 600, 940]
    icons = _svg_icon_templates()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{_escape_svg_text(headline)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#0a1628"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#020617" flood-opacity="0.6"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
"""
    # Column backgrounds and top connectors
    for idx, (x, color) in enumerate(zip(col_x, col_colors)):
        svg += f"""  <rect x="{x - 90}" y="200" width="180" height="300" rx="12" fill="#111827" stroke="{color}" stroke-width="1.5" opacity="0.6"/>
  <circle cx="{x}" cy="180" r="30" fill="{color}" opacity="0.15" filter="url(#glow)"/>
  <line x1="{x}" y1="200" x2="{x}" y2="160" stroke="{color}" stroke-width="2" opacity="0.5"/>
"""
    # Flow arrows between columns
    svg += f"""  <path d="M{col_x[0] + 90} 340 L{col_x[1] - 90} 340" fill="none" stroke="#334155" stroke-width="2" stroke-dasharray="8 6" marker-end="url(#arr)"/>
  <path d="M{col_x[1] + 90} 340 L{col_x[2] - 90} 340" fill="none" stroke="#334155" stroke-width="2" stroke-dasharray="8 6"/>
"""
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        x = col_x[idx]
        color = col_colors[idx % len(col_colors)]
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        svg += f"""  <g transform="translate({x} 340)" filter="url(#shadow)">
    <circle r="56" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
  </g>
  <text x="{x}" y="436" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  <rect x="{x - 50}" y="448" width="100" height="4" rx="2" fill="{color}" opacity="0.3"/>
"""
    svg += f"""  <rect x="90" y="62" width="196" height="32" rx="6" fill="{accent}" opacity="0.18"/>
  <text x="188" y="83" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{accent}" text-anchor="middle" letter-spacing="2">WEEKLY DIGEST</text>
  <text x="90" y="140" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#f8fafc">{_escape_svg_text(headline)}</text>
  <text x="90" y="176" font-family="Arial,sans-serif" font-size="18" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""
    return svg


def _render_shattered_vault_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    """Style 3: Shattered Vault - Horizontal split with breach crack (gold/blue)."""
    icons = _svg_icon_templates()
    node_colors = ["#f59e0b", "#3b82f6", "#ef4444"]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{_escape_svg_text(headline)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#111c35"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#020617" flood-opacity="0.6"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <!-- Vault door outline -->
  <rect x="380" y="200" width="440" height="300" rx="16" fill="#111827" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <!-- Vault hinge marks -->
  <rect x="390" y="230" width="18" height="40" rx="4" fill="#f59e0b" opacity="0.4"/>
  <rect x="390" y="430" width="18" height="40" rx="4" fill="#f59e0b" opacity="0.4"/>
  <!-- Breach crack down the middle -->
  <path d="M600 200 L590 260 L614 310 L588 370 L606 430 L600 500" fill="none" stroke="#ef4444" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
  <!-- Glow behind crack -->
  <path d="M600 200 L590 260 L614 310 L588 370 L606 430 L600 500" fill="none" stroke="#ef4444" stroke-width="16" stroke-linecap="round" opacity="0.12" filter="url(#glow)"/>
  <!-- Lock wheel center -->
  <circle cx="600" cy="350" r="40" fill="#0f172a" stroke="#f59e0b" stroke-width="2.5"/>
  <circle cx="600" cy="350" r="18" fill="#111827" stroke="#f59e0b" stroke-width="1.5"/>
  <circle cx="600" cy="350" r="6" fill="#f59e0b" opacity="0.6"/>
  <circle cx="600" cy="330" r="4" fill="#f59e0b" opacity="0.5"/>
  <circle cx="600" cy="370" r="4" fill="#f59e0b" opacity="0.5"/>
  <circle cx="580" cy="350" r="4" fill="#f59e0b" opacity="0.5"/>
  <circle cx="620" cy="350" r="4" fill="#f59e0b" opacity="0.5"/>
  <!-- Ambient glows -->
  <circle cx="240" cy="350" r="180" fill="#f59e0b" opacity="0.07" filter="url(#glow)"/>
  <circle cx="960" cy="350" r="180" fill="#3b82f6" opacity="0.07" filter="url(#glow)"/>
"""
    node_positions = [(200, 350), (600, 490), (1000, 350)]
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        x, y = node_positions[idx]
        color = node_colors[idx % len(node_colors)]
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        if idx == 1:
            # Bottom center - below the vault
            svg += f"""  <g transform="translate({x} {y})" filter="url(#shadow)">
    <circle r="46" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
    <text x="0" y="72" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  </g>
"""
        else:
            svg += f"""  <g transform="translate({x} {y})" filter="url(#shadow)">
    <circle r="52" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
    <text x="0" y="78" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  </g>
"""
    svg += f"""  <rect x="90" y="62" width="196" height="32" rx="6" fill="{accent}" opacity="0.18"/>
  <text x="188" y="83" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{accent}" text-anchor="middle" letter-spacing="2">WEEKLY DIGEST</text>
  <text x="90" y="134" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#f8fafc">{_escape_svg_text(headline)}</text>
  <text x="90" y="170" font-family="Arial,sans-serif" font-size="18" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""
    return svg


def _render_global_gavel_svg(
    accent: str,
    headline: str,
    subtitle: str,
    date_display: str,
    focus_labels: List[str],
) -> str:
    """Style 4: Global Gavel - World map grid with depth layers (navy/crimson/silver)."""
    icons = _svg_icon_templates()
    node_colors = ["#dc2626", "#e2e8f0", "#3b82f6"]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{_escape_svg_text(headline)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0f1e"/>
      <stop offset="60%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#141030"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#020617" flood-opacity="0.6"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <!-- Globe grid lines (longitude/latitude) -->
  <ellipse cx="600" cy="350" rx="300" ry="200" fill="none" stroke="#1e3a5f" stroke-width="1" opacity="0.6"/>
  <ellipse cx="600" cy="350" rx="220" ry="200" fill="none" stroke="#1e3a5f" stroke-width="1" opacity="0.4"/>
  <ellipse cx="600" cy="350" rx="120" ry="200" fill="none" stroke="#1e3a5f" stroke-width="1" opacity="0.3"/>
  <line x1="300" y1="350" x2="900" y2="350" stroke="#1e3a5f" stroke-width="1" opacity="0.6"/>
  <line x1="300" y1="300" x2="900" y2="300" stroke="#1e3a5f" stroke-width="1" opacity="0.35"/>
  <line x1="300" y1="400" x2="900" y2="400" stroke="#1e3a5f" stroke-width="1" opacity="0.35"/>
  <line x1="300" y1="250" x2="900" y2="250" stroke="#1e3a5f" stroke-width="1" opacity="0.2"/>
  <line x1="300" y1="450" x2="900" y2="450" stroke="#1e3a5f" stroke-width="1" opacity="0.2"/>
  <!-- Globe equator highlight -->
  <ellipse cx="600" cy="350" rx="300" ry="200" fill="none" stroke="#1e3a5f" stroke-width="2" opacity="0.8"/>
  <!-- Globe fill -->
  <ellipse cx="600" cy="350" rx="298" ry="198" fill="#0d1b2a" opacity="0.6"/>
  <!-- Crimson glow center -->
  <circle cx="600" cy="350" r="220" fill="#dc2626" opacity="0.06" filter="url(#glow)"/>
  <circle cx="600" cy="350" r="80" fill="#3b82f6" opacity="0.07" filter="url(#glow)"/>
  <!-- Gavel handle -->
  <rect x="660" y="380" width="16" height="110" rx="6" fill="#e2e8f0" opacity="0.25" transform="rotate(40 668 435)"/>
  <!-- Gavel head -->
  <rect x="560" y="290" width="90" height="50" rx="8" fill="#e2e8f0" opacity="0.2" transform="rotate(40 605 315)"/>
  <!-- Impact lines -->
  <line x1="560" y1="340" x2="510" y2="300" stroke="#dc2626" stroke-width="2" opacity="0.4"/>
  <line x1="555" y1="355" x2="495" y2="330" stroke="#dc2626" stroke-width="1.5" opacity="0.3"/>
  <line x1="565" y1="330" x2="520" y2="280" stroke="#dc2626" stroke-width="1" opacity="0.25"/>
"""
    node_positions = [(200, 350), (600, 350), (1000, 350)]
    for idx, label in enumerate(focus_labels[:SVG_MAX_FOCUS_LABELS]):
        x, y = node_positions[idx]
        color = node_colors[idx % len(node_colors)]
        icon_key = _match_svg_icon(label)
        icon_svg = icons[icon_key].replace("{c}", color)
        node_y_offset = [460, 490, 460][idx]
        radius = [52, 58, 52][idx]
        svg += f"""  <g transform="translate({x} {y})" filter="url(#shadow)">
    <circle r="{radius}" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
  </g>
  <text x="{x}" y="{node_y_offset}" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
"""
    svg += f"""  <rect x="90" y="62" width="196" height="32" rx="6" fill="{accent}" opacity="0.18"/>
  <text x="188" y="83" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{accent}" text-anchor="middle" letter-spacing="2">WEEKLY DIGEST</text>
  <text x="90" y="134" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#f8fafc">{_escape_svg_text(headline)}</text>
  <text x="90" y="170" font-family="Arial,sans-serif" font-size="18" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""
    return svg


def _convert_svg_to_og_png(svg_path: Path) -> None:
    """Convert SVG to PNG for Open Graph social media previews using rsvg-convert."""
    import shutil

    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        logging.debug("rsvg-convert not found, skipping PNG conversion")
        return

    png_path = svg_path.with_name(svg_path.stem + "_og.png")
    try:
        result = subprocess.run(
            [rsvg, "-w", "1200", "-h", "630", str(svg_path), "-o", str(png_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"✅ Created OG image: {png_path}")
        else:
            logging.warning(f"rsvg-convert failed: {result.stderr[:200]}")
    except Exception as e:
        logging.warning(f"PNG conversion skipped: {e}")


def generate_svg_image(
    date: datetime, categorized: Dict[str, List[Dict]], news_items: List[Dict]
) -> str:
    """Generate low-text digest SVG focused on standalone comprehension.

    Layout cycles through 5 visually distinct styles based on day of month (day % 5):
      0 - Fractured Core: central hexagon with orbiting nodes (red/cyan)
      1 - Dossier Strike: diagonal split with classified stamp motif (purple/gold)
      2 - Pipeline Triptych: three vertical columns (cyan/green/orange)
      3 - Shattered Vault: horizontal split with breach crack (gold/blue)
      4 - Global Gavel: world map grid with depth layers (navy/crimson/silver)
    """

    date_display = date.strftime("%B %d, %Y")
    focus_labels = _extract_visual_focus_labels(news_items, limit=SVG_MAX_FOCUS_LABELS)

    if categorized.get("security") or categorized.get("devsecops"):
        main_category = "security"
    elif categorized.get("ai"):
        main_category = "ai"
    elif categorized.get("cloud"):
        main_category = "cloud"
    else:
        main_category = "tech"

    config = CATEGORY_SVG_CONFIG.get(main_category, CATEGORY_SVG_CONFIG["tech"])
    accent = config["icon_color"]
    headline = "THREAT SIGNAL MAP" if main_category == "security" else "TECH SIGNAL MAP"
    subtitle = _compose_svg_subtitle(focus_labels)

    layout_index = date.day % 5
    layout_renderers = [
        _render_fractured_core_svg,
        _render_dossier_strike_svg,
        _render_pipeline_triptych_svg,
        _render_shattered_vault_svg,
        _render_global_gavel_svg,
    ]
    return layout_renderers[layout_index](
        accent, headline, subtitle, date_display, focus_labels
    )
