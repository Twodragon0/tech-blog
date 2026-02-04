#!/usr/bin/env python3
"""
고퀄리티 포스팅 이미지 생성 스크립트
카테고리별 특화된 아이콘과 시각적 요소를 포함한 프로페셔널 SVG 이미지를 생성합니다.
"""

import os
import re
import sys
import frontmatter
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def log_message(message: str, level: str = "INFO"):
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] [{level}] {icon} {message}")


def _escape_svg_text(text: str) -> str:
    """SVG 텍스트 이스케이프"""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _truncate_title(title: str, max_len: int = 50) -> str:
    """제목 길이 제한"""
    if not title:
        return "Tech Blog Post"
    if len(title) <= max_len:
        return title
    return title[: max_len - 3] + "..."


def extract_post_info(post_file: Path) -> Dict:
    """포스팅 파일에서 정보 추출"""
    try:
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", "")
        categories = post.metadata.get("categories", [])
        if isinstance(categories, str):
            categories = [categories]
        category = categories[0] if categories else post.metadata.get("category", "")
        tags = post.metadata.get("tags", [])
        image_path = post.metadata.get("image", "")
        excerpt = post.metadata.get("excerpt", "")
        content = post.content

        # AI 요약 카드에서 핵심 내용 추출
        highlights = []
        if "핵심 내용" in content:
            highlights_match = re.search(
                r"핵심 내용[^<]*<ul[^>]*>(.*?)</ul>", content, re.DOTALL
            )
            if highlights_match:
                highlights_text = highlights_match.group(1)
                highlights = re.findall(r"<li>(.*?)</li>", highlights_text, re.DOTALL)
                highlights = [re.sub(r"<[^>]+>", "", h).strip() for h in highlights[:5]]

        return {
            "title": title,
            "category": category,
            "tags": tags,
            "image": image_path,
            "excerpt": excerpt,
            "content": content,
            "highlights": highlights,
            "filename": post_file.name,
        }
    except Exception as e:
        log_message(f"포스팅 정보 추출 실패: {str(e)}", "ERROR")
        return {}


def get_security_icons_svg() -> str:
    """보안 관련 아이콘 SVG"""
    return '''
    <!-- Shield Icon -->
    <g transform="translate(80, 280)">
      <path d="M50 10 L90 30 L90 70 Q90 100 50 120 Q10 100 10 70 L10 30 Z" 
            fill="url(#securityGradient)" stroke="#ef4444" stroke-width="2" opacity="0.9"/>
      <path d="M35 60 L45 75 L70 45" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    
    <!-- Lock Icon -->
    <g transform="translate(200, 300)">
      <rect x="15" y="35" width="50" height="40" rx="5" fill="#dc2626" opacity="0.8"/>
      <path d="M25 35 L25 25 Q25 10 40 10 Q55 10 55 25 L55 35" fill="none" stroke="#dc2626" stroke-width="4"/>
      <circle cx="40" cy="55" r="6" fill="white"/>
    </g>
    
    <!-- Alert Triangle -->
    <g transform="translate(320, 290)">
      <path d="M40 15 L75 75 L5 75 Z" fill="#f59e0b" stroke="#d97706" stroke-width="2"/>
      <text x="40" y="60" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="white" text-anchor="middle">!</text>
    </g>
    '''


def get_cloud_icons_svg() -> str:
    """클라우드 관련 아이콘 SVG"""
    return '''
    <!-- Cloud Icon -->
    <g transform="translate(80, 280)">
      <path d="M30 80 Q10 80 10 60 Q10 40 30 40 Q30 20 55 20 Q80 20 80 45 Q100 45 100 65 Q100 80 80 80 Z" 
            fill="url(#cloudGradient)" stroke="#0ea5e9" stroke-width="2" opacity="0.9"/>
    </g>
    
    <!-- Server Stack -->
    <g transform="translate(200, 290)">
      <rect x="10" y="10" width="60" height="20" rx="3" fill="#14b8a6" stroke="#0d9488" stroke-width="2"/>
      <rect x="10" y="35" width="60" height="20" rx="3" fill="#14b8a6" stroke="#0d9488" stroke-width="2"/>
      <rect x="10" y="60" width="60" height="20" rx="3" fill="#14b8a6" stroke="#0d9488" stroke-width="2"/>
      <circle cx="55" cy="20" r="4" fill="#22d3ee"/>
      <circle cx="55" cy="45" r="4" fill="#22d3ee"/>
      <circle cx="55" cy="70" r="4" fill="#22d3ee"/>
    </g>
    
    <!-- Network Node -->
    <g transform="translate(330, 300)">
      <circle cx="30" cy="30" r="20" fill="#0284c7" stroke="#0369a1" stroke-width="2"/>
      <circle cx="30" cy="30" r="8" fill="white"/>
      <line x1="10" y1="30" x2="-10" y2="30" stroke="#0284c7" stroke-width="2"/>
      <line x1="50" y1="30" x2="70" y2="30" stroke="#0284c7" stroke-width="2"/>
      <line x1="30" y1="10" x2="30" y2="-10" stroke="#0284c7" stroke-width="2"/>
    </g>
    '''


def get_devops_icons_svg() -> str:
    """DevOps 관련 아이콘 SVG"""
    return '''
    <!-- Infinity/DevOps Loop -->
    <g transform="translate(80, 290)">
      <path d="M10 40 Q10 10 40 10 Q70 10 70 40 Q70 70 100 70 Q130 70 130 40 Q130 10 100 10 Q70 10 70 40 Q70 70 40 70 Q10 70 10 40" 
            fill="none" stroke="url(#devopsGradient)" stroke-width="6" stroke-linecap="round"/>
    </g>
    
    <!-- Gear Icon -->
    <g transform="translate(220, 290)">
      <circle cx="35" cy="35" r="25" fill="#f59e0b" stroke="#d97706" stroke-width="2"/>
      <circle cx="35" cy="35" r="10" fill="#0f172a"/>
      <rect x="30" y="2" width="10" height="15" rx="2" fill="#f59e0b"/>
      <rect x="30" y="53" width="10" height="15" rx="2" fill="#f59e0b"/>
      <rect x="2" y="30" width="15" height="10" rx="2" fill="#f59e0b"/>
      <rect x="53" y="30" width="15" height="10" rx="2" fill="#f59e0b"/>
    </g>
    
    <!-- Code Bracket -->
    <g transform="translate(330, 295)">
      <text x="0" y="45" font-family="monospace" font-size="50" font-weight="bold" fill="#a855f7">&lt;/&gt;</text>
    </g>
    '''


def get_kubernetes_icons_svg() -> str:
    """Kubernetes 관련 아이콘 SVG"""
    return '''
    <!-- Kubernetes Wheel -->
    <g transform="translate(100, 290)">
      <circle cx="50" cy="50" r="40" fill="none" stroke="#326ce5" stroke-width="4"/>
      <circle cx="50" cy="50" r="15" fill="#326ce5"/>
      <g stroke="#326ce5" stroke-width="4">
        <line x1="50" y1="10" x2="50" y2="35"/>
        <line x1="50" y1="65" x2="50" y2="90"/>
        <line x1="10" y1="50" x2="35" y2="50"/>
        <line x1="65" y1="50" x2="90" y2="50"/>
        <line x1="22" y1="22" x2="39" y2="39"/>
        <line x1="61" y1="61" x2="78" y2="78"/>
        <line x1="22" y1="78" x2="39" y2="61"/>
        <line x1="61" y1="39" x2="78" y2="22"/>
      </g>
    </g>
    
    <!-- Container Box -->
    <g transform="translate(230, 300)">
      <rect x="10" y="20" width="60" height="50" rx="5" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>
      <rect x="10" y="10" width="60" height="15" rx="3" fill="#60a5fa"/>
      <rect x="20" y="35" width="40" height="25" rx="3" fill="#1e3a8a"/>
    </g>
    
    <!-- Pod Circle -->
    <g transform="translate(340, 310)">
      <circle cx="30" cy="30" r="25" fill="#8b5cf6" stroke="#7c3aed" stroke-width="2"/>
      <text x="30" y="38" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white" text-anchor="middle">Pod</text>
    </g>
    '''


def get_ai_icons_svg() -> str:
    """AI 관련 아이콘 SVG"""
    return '''
    <!-- Brain/Neural Network -->
    <g transform="translate(80, 280)">
      <ellipse cx="50" cy="50" rx="45" ry="35" fill="url(#aiGradient)" stroke="#8b5cf6" stroke-width="2" opacity="0.9"/>
      <circle cx="30" cy="40" r="8" fill="white" opacity="0.8"/>
      <circle cx="50" cy="55" r="8" fill="white" opacity="0.8"/>
      <circle cx="70" cy="40" r="8" fill="white" opacity="0.8"/>
      <line x1="30" y1="40" x2="50" y2="55" stroke="white" stroke-width="2" opacity="0.8"/>
      <line x1="50" y1="55" x2="70" y2="40" stroke="white" stroke-width="2" opacity="0.8"/>
      <line x1="30" y1="40" x2="70" y2="40" stroke="white" stroke-width="2" opacity="0.8"/>
    </g>
    
    <!-- Robot Head -->
    <g transform="translate(210, 285)">
      <rect x="10" y="20" width="60" height="50" rx="10" fill="#6366f1" stroke="#4f46e5" stroke-width="2"/>
      <rect x="25" y="5" width="30" height="20" rx="5" fill="#818cf8"/>
      <circle cx="30" cy="40" r="8" fill="#22d3ee"/>
      <circle cx="50" cy="40" r="8" fill="#22d3ee"/>
      <rect x="25" y="55" width="30" height="8" rx="2" fill="#c7d2fe"/>
    </g>
    
    <!-- Chip/Processor -->
    <g transform="translate(330, 295)">
      <rect x="15" y="15" width="50" height="50" rx="5" fill="#7c3aed" stroke="#6d28d9" stroke-width="2"/>
      <rect x="25" y="25" width="30" height="30" rx="3" fill="#a78bfa"/>
      <g stroke="#7c3aed" stroke-width="3">
        <line x1="40" y1="5" x2="40" y2="15"/>
        <line x1="40" y1="65" x2="40" y2="75"/>
        <line x1="5" y1="40" x2="15" y2="40"/>
        <line x1="65" y1="40" x2="75" y2="40"/>
      </g>
    </g>
    '''


def get_devsecops_icons_svg() -> str:
    """DevSecOps 관련 아이콘 SVG"""
    return '''
    <!-- Shield with Code -->
    <g transform="translate(80, 275)">
      <path d="M50 5 L95 25 L95 65 Q95 100 50 120 Q5 100 5 65 L5 25 Z" 
            fill="url(#devsecopsGradient)" stroke="#8b5cf6" stroke-width="2" opacity="0.9"/>
      <text x="50" y="75" font-family="monospace" font-size="28" font-weight="bold" fill="white" text-anchor="middle">&lt;/&gt;</text>
    </g>
    
    <!-- Pipeline Arrow -->
    <g transform="translate(200, 300)">
      <rect x="0" y="20" width="30" height="30" rx="5" fill="#3b82f6"/>
      <text x="15" y="42" font-family="Arial" font-size="16" fill="white" text-anchor="middle">D</text>
      <path d="M35 35 L50 35" stroke="#64748b" stroke-width="3"/>
      <rect x="55" y="20" width="30" height="30" rx="5" fill="#8b5cf6"/>
      <text x="70" y="42" font-family="Arial" font-size="16" fill="white" text-anchor="middle">S</text>
      <path d="M90 35 L105 35" stroke="#64748b" stroke-width="3"/>
      <rect x="110" y="20" width="30" height="30" rx="5" fill="#22c55e"/>
      <text x="125" y="42" font-family="Arial" font-size="16" fill="white" text-anchor="middle">O</text>
    </g>
    
    <!-- Security Scanner -->
    <g transform="translate(360, 290)">
      <circle cx="30" cy="35" r="25" fill="none" stroke="#ef4444" stroke-width="3"/>
      <line x1="48" y1="53" x2="65" y2="70" stroke="#ef4444" stroke-width="4" stroke-linecap="round"/>
      <path d="M20 35 L25 40 L40 25" fill="none" stroke="#22c55e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    '''


def get_incident_icons_svg() -> str:
    """인시던트 관련 아이콘 SVG"""
    return '''
    <!-- Warning Bell -->
    <g transform="translate(80, 280)">
      <path d="M50 15 Q30 15 30 40 L30 65 L20 75 L80 75 L70 65 L70 40 Q70 15 50 15" 
            fill="#ef4444" stroke="#dc2626" stroke-width="2"/>
      <circle cx="50" cy="85" r="8" fill="#ef4444"/>
      <line x1="50" y1="5" x2="50" y2="15" stroke="#ef4444" stroke-width="3"/>
      <circle cx="50" cy="3" r="3" fill="#ef4444"/>
    </g>
    
    <!-- Timeline -->
    <g transform="translate(200, 310)">
      <line x1="0" y1="30" x2="140" y2="30" stroke="#64748b" stroke-width="3"/>
      <circle cx="0" cy="30" r="8" fill="#ef4444"/>
      <circle cx="50" cy="30" r="8" fill="#f59e0b"/>
      <circle cx="100" cy="30" r="8" fill="#22c55e"/>
      <circle cx="140" cy="30" r="8" fill="#3b82f6"/>
    </g>
    
    <!-- Fire Icon -->
    <g transform="translate(370, 285)">
      <path d="M30 70 Q10 50 20 30 Q25 40 35 35 Q30 20 40 5 Q50 25 55 20 Q65 35 60 50 Q70 55 65 70 Z" 
            fill="url(#fireGradient)" stroke="#dc2626" stroke-width="2"/>
    </g>
    '''


def get_finops_icons_svg() -> str:
    """FinOps 관련 아이콘 SVG"""
    return '''
    <!-- Dollar Chart -->
    <g transform="translate(80, 280)">
      <rect x="5" y="5" width="90" height="70" rx="5" fill="#0f172a" stroke="#14b8a6" stroke-width="2"/>
      <polyline points="15,60 30,45 50,55 70,30 85,40" fill="none" stroke="#22d3ee" stroke-width="3"/>
      <text x="50" y="55" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#14b8a6" text-anchor="middle">$</text>
    </g>
    
    <!-- Cloud Cost -->
    <g transform="translate(210, 290)">
      <path d="M20 50 Q5 50 5 35 Q5 20 20 20 Q20 5 40 5 Q60 5 60 25 Q75 25 75 40 Q75 50 60 50 Z" 
            fill="#14b8a6" stroke="#0d9488" stroke-width="2" opacity="0.8"/>
      <text x="40" y="38" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white" text-anchor="middle">$</text>
    </g>
    
    <!-- Savings Piggy -->
    <g transform="translate(330, 295)">
      <ellipse cx="40" cy="40" rx="35" ry="25" fill="#14b8a6" stroke="#0d9488" stroke-width="2"/>
      <ellipse cx="65" cy="35" rx="8" ry="5" fill="#14b8a6" stroke="#0d9488" stroke-width="2"/>
      <circle cx="60" cy="30" r="3" fill="#0f172a"/>
      <rect x="30" y="10" width="20" height="8" rx="2" fill="#0d9488"/>
      <ellipse cx="25" cy="55" rx="8" ry="5" fill="#0d9488"/>
      <ellipse cx="55" cy="55" rx="8" ry="5" fill="#0d9488"/>
    </g>
    '''


def generate_high_quality_svg(post_info: Dict, output_path: Path) -> bool:
    """고퀄리티 SVG 이미지 생성"""
    try:
        title = post_info.get("title", "Tech Blog Post")
        category = post_info.get("category", "tech").lower()
        tags = post_info.get("tags", [])
        excerpt = post_info.get("excerpt", "")
        highlights = post_info.get("highlights", [])

        # 카테고리별 설정
        category_config = {
            "security": {
                "gradient_start": "#dc2626",
                "gradient_end": "#991b1b",
                "gradient_id": "securityGradient",
                "label": "SECURITY",
                "accent": "#ef4444",
                "icons_func": get_security_icons_svg,
                "bg_accent_1": "#ef4444",
                "bg_accent_2": "#dc2626",
            },
            "devsecops": {
                "gradient_start": "#8b5cf6",
                "gradient_end": "#6d28d9",
                "gradient_id": "devsecopsGradient",
                "label": "DEVSECOPS",
                "accent": "#a78bfa",
                "icons_func": get_devsecops_icons_svg,
                "bg_accent_1": "#8b5cf6",
                "bg_accent_2": "#7c3aed",
            },
            "cloud": {
                "gradient_start": "#0ea5e9",
                "gradient_end": "#0284c7",
                "gradient_id": "cloudGradient",
                "label": "CLOUD",
                "accent": "#38bdf8",
                "icons_func": get_cloud_icons_svg,
                "bg_accent_1": "#0ea5e9",
                "bg_accent_2": "#0284c7",
            },
            "devops": {
                "gradient_start": "#f59e0b",
                "gradient_end": "#d97706",
                "gradient_id": "devopsGradient",
                "label": "DEVOPS",
                "accent": "#fbbf24",
                "icons_func": get_devops_icons_svg,
                "bg_accent_1": "#f59e0b",
                "bg_accent_2": "#d97706",
            },
            "kubernetes": {
                "gradient_start": "#3b82f6",
                "gradient_end": "#1d4ed8",
                "gradient_id": "k8sGradient",
                "label": "KUBERNETES",
                "accent": "#60a5fa",
                "icons_func": get_kubernetes_icons_svg,
                "bg_accent_1": "#3b82f6",
                "bg_accent_2": "#1d4ed8",
            },
            "finops": {
                "gradient_start": "#14b8a6",
                "gradient_end": "#0d9488",
                "gradient_id": "finopsGradient",
                "label": "FINOPS",
                "accent": "#2dd4bf",
                "icons_func": get_finops_icons_svg,
                "bg_accent_1": "#14b8a6",
                "bg_accent_2": "#0d9488",
            },
            "incident": {
                "gradient_start": "#ef4444",
                "gradient_end": "#b91c1c",
                "gradient_id": "incidentGradient",
                "label": "INCIDENT",
                "accent": "#f87171",
                "icons_func": get_incident_icons_svg,
                "bg_accent_1": "#ef4444",
                "bg_accent_2": "#dc2626",
            },
            "tech": {
                "gradient_start": "#6366f1",
                "gradient_end": "#4f46e5",
                "gradient_id": "aiGradient",
                "label": "TECH",
                "accent": "#818cf8",
                "icons_func": get_ai_icons_svg,
                "bg_accent_1": "#6366f1",
                "bg_accent_2": "#4f46e5",
            },
        }

        config = category_config.get(category, category_config["tech"])
        
        display_title = _escape_svg_text(_truncate_title(title, 48))
        
        # 태그 처리
        display_tags = tags[:4] if tags else ["Tech", "Blog", "Update"]
        
        # 요약 라인 처리
        summary_lines = []
        if highlights:
            for h in highlights[:3]:
                clean_h = re.sub(r"<[^>]+>", "", h)
                if len(clean_h) > 70:
                    clean_h = clean_h[:67] + "..."
                summary_lines.append(_escape_svg_text(clean_h))
        elif excerpt:
            words = excerpt.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if len(test_line) > 70:
                    summary_lines.append(_escape_svg_text(line))
                    line = word
                    if len(summary_lines) >= 3:
                        break
                else:
                    line = test_line
            if line and len(summary_lines) < 3:
                summary_lines.append(_escape_svg_text(line))

        date_str = datetime.now().strftime("%B %d, %Y")
        icons_svg = config["icons_func"]()

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <!-- Background Gradients -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a1a"/>
      <stop offset="30%" style="stop-color:#0f1629"/>
      <stop offset="70%" style="stop-color:#1a1f3a"/>
      <stop offset="100%" style="stop-color:#0d1117"/>
    </linearGradient>
    
    <!-- Category Gradient -->
    <linearGradient id="{config["gradient_id"]}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{config["gradient_start"]}"/>
      <stop offset="100%" style="stop-color:{config["gradient_end"]}"/>
    </linearGradient>
    
    <!-- Accent Gradient -->
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3b82f6"/>
      <stop offset="33%" style="stop-color:#8b5cf6"/>
      <stop offset="66%" style="stop-color:#ec4899"/>
      <stop offset="100%" style="stop-color:#f59e0b"/>
    </linearGradient>
    
    <!-- Card Gradient -->
    <linearGradient id="cardGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e293b"/>
      <stop offset="100%" style="stop-color:#0f172a"/>
    </linearGradient>
    
    <!-- Fire Gradient for Incident -->
    <linearGradient id="fireGradient" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" style="stop-color:#dc2626"/>
      <stop offset="50%" style="stop-color:#f59e0b"/>
      <stop offset="100%" style="stop-color:#fbbf24"/>
    </linearGradient>
    
    <!-- Glow Effects -->
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <filter id="strongGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <!-- Shadow -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000" flood-opacity="0.4"/>
    </filter>
    
    <!-- Inner Glow -->
    <filter id="innerGlow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
      <feOffset in="blur" dx="0" dy="0"/>
      <feComposite in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1"/>
      <feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.5 0"/>
      <feBlend in2="SourceGraphic"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bgGradient)"/>
  
  <!-- Animated Grid Pattern -->
  <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
    <path d="M 60 0 L 0 0 0 60" fill="none" stroke="{config["accent"]}" stroke-opacity="0.05" stroke-width="1"/>
  </pattern>
  <rect width="1200" height="630" fill="url(#grid)"/>
  
  <!-- Background Decorative Elements -->
  <circle cx="0" cy="0" r="300" fill="{config["bg_accent_1"]}" fill-opacity="0.03"/>
  <circle cx="1200" cy="630" r="350" fill="{config["bg_accent_2"]}" fill-opacity="0.04"/>
  <circle cx="600" cy="315" r="400" fill="{config["gradient_start"]}" fill-opacity="0.02"/>
  
  <!-- Decorative Lines -->
  <line x1="0" y1="200" x2="150" y2="200" stroke="{config["accent"]}" stroke-width="1" opacity="0.3"/>
  <line x1="1050" y1="430" x2="1200" y2="430" stroke="{config["accent"]}" stroke-width="1" opacity="0.3"/>
  
  <!-- Top Header Bar -->
  <rect x="0" y="0" width="1200" height="6" fill="url(#accentGradient)"/>
  
  <!-- Category Badge -->
  <g filter="url(#shadow)">
    <rect x="40" y="25" width="160" height="40" rx="20" fill="url(#{config["gradient_id"]})"/>
    <text x="120" y="51" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">{config["label"]}</text>
  </g>
  
  <!-- Date Badge -->
  <g filter="url(#shadow)">
    <rect x="1000" y="25" width="160" height="40" rx="20" fill="url(#accentGradient)"/>
    <text x="1080" y="51" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white" text-anchor="middle">{date_str}</text>
  </g>
  
  <!-- Main Title -->
  <text x="600" y="110" font-family="Arial, sans-serif" font-size="36" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{display_title}</text>
  
  <!-- Subtitle Line -->
  <rect x="400" y="135" width="400" height="4" rx="2" fill="url(#accentGradient)"/>
  
  <!-- Icon Section - Left Side -->
  <g opacity="0.95">
    {icons_svg}
  </g>
  
  <!-- Main Content Card -->
  <g transform="translate(450, 180)" filter="url(#shadow)">
    <rect width="720" height="340" rx="16" fill="url(#cardGradient)" stroke="{config["accent"]}" stroke-width="1" stroke-opacity="0.3"/>
    
    <!-- Card Header Accent -->
    <rect x="0" y="0" width="720" height="8" rx="4" fill="url(#{config["gradient_id"]})"/>
    
    <!-- Card Title -->
    <text x="30" y="50" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="{config["accent"]}">Key Highlights</text>
    
    <!-- Summary Content -->'''

        # 요약 내용 추가
        if summary_lines:
            for idx, line in enumerate(summary_lines[:3]):
                y_offset = 90 + idx * 35
                svg_content += f'''
    <g transform="translate(30, {y_offset})">
      <circle cx="8" cy="8" r="4" fill="{config["accent"]}"/>
      <text x="25" y="13" font-family="Arial, sans-serif" font-size="14" fill="#e2e8f0">{line}</text>
    </g>'''
        else:
            svg_content += f'''
    <g transform="translate(30, 90)">
      <circle cx="8" cy="8" r="4" fill="{config["accent"]}"/>
      <text x="25" y="13" font-family="Arial, sans-serif" font-size="14" fill="#e2e8f0">Read the full article for detailed insights</text>
    </g>
    <g transform="translate(30, 125)">
      <circle cx="8" cy="8" r="4" fill="{config["accent"]}"/>
      <text x="25" y="13" font-family="Arial, sans-serif" font-size="14" fill="#e2e8f0">Stay updated with the latest tech and security news</text>
    </g>'''

        # 태그 추가
        svg_content += '''
    
    <!-- Tags Section -->
    <g transform="translate(30, 230)">'''
        
        tag_x = 0
        for idx, tag in enumerate(display_tags[:4]):
            tag_text = _escape_svg_text(f"#{tag}" if not str(tag).startswith("#") else str(tag))
            tag_width = len(tag_text) * 9 + 24
            svg_content += f'''
      <rect x="{tag_x}" y="0" width="{tag_width}" height="30" rx="15" fill="{config["accent"]}" fill-opacity="0.15" stroke="{config["accent"]}" stroke-width="1" stroke-opacity="0.4"/>
      <text x="{tag_x + tag_width // 2}" y="20" font-family="Arial, sans-serif" font-size="12" fill="{config["accent"]}" text-anchor="middle">{tag_text}</text>'''
            tag_x += tag_width + 12

        svg_content += f'''
    </g>
    
    <!-- CTA Button -->
    <g transform="translate(540, 280)">
      <rect width="150" height="45" rx="22" fill="url(#accentGradient)" filter="url(#glow)"/>
      <text x="75" y="29" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">Read More</text>
    </g>
  </g>
  
  <!-- Bottom Section -->
  <line x1="40" y1="560" x2="1160" y2="560" stroke="#334155" stroke-width="1"/>
  
  <!-- Blog Branding -->
  <g transform="translate(50, 575)">
    <rect width="45" height="45" rx="10" fill="url(#{config["gradient_id"]})" filter="url(#shadow)"/>
    <text x="22" y="32" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="white" text-anchor="middle">TD</text>
  </g>
  
  <text x="110" y="595" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white">Twodragon Tech Blog</text>
  <text x="110" y="615" font-family="Arial, sans-serif" font-size="12" fill="#64748b">tech.2twodragon.com</text>
  
  <!-- Tech Stack -->
  <text x="1150" y="595" font-family="Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="end">DevSecOps | Cloud | Security | AI</text>
  <text x="1150" y="615" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="end">Powered by Claude AI</text>
</svg>'''

        output_svg = output_path.with_suffix(".svg")
        with open(output_svg, "w", encoding="utf-8") as f:
            f.write(svg_content)

        log_message(f"✅ 고퀄리티 SVG 이미지 생성 완료: {output_svg.name}", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"❌ 이미지 생성 실패: {str(e)}", "ERROR")
        return False


def process_post(post_file: Path, force: bool = False) -> bool:
    """단일 포스팅 처리"""
    log_message(f"📄 포스팅 처리 시작: {post_file.name}")

    post_info = extract_post_info(post_file)
    if not post_info:
        log_message(f"❌ 포스팅 정보 추출 실패: {post_file.name}", "ERROR")
        return False

    image_path = post_info.get("image", "")
    
    # 이미지 경로 결정
    if not image_path:
        post_stem = post_file.stem
        image_filename = f"{post_stem}.svg"
        image_path = f"/assets/images/{image_filename}"
    
    # 출력 경로 결정
    if image_path.startswith("/assets/images/"):
        output_path = PROJECT_ROOT / image_path.lstrip("/")
    elif image_path.startswith("assets/images/"):
        output_path = PROJECT_ROOT / image_path
    else:
        output_path = IMAGES_DIR / Path(image_path).name
    
    # 기존 이미지 확인
    if output_path.exists() and not force:
        log_message(f"⚠️ 이미지가 이미 존재합니다. --force 옵션으로 덮어쓰기: {output_path.name}", "WARNING")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 고퀄리티 SVG 생성
    return generate_high_quality_svg(post_info, output_path)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="고퀄리티 포스팅 이미지 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 최근 포스팅 이미지 생성 (강제 덮어쓰기)
  python3 scripts/generate_high_quality_images.py --recent 5 --force
  
  # 특정 포스팅 이미지 생성
  python3 scripts/generate_high_quality_images.py _posts/2026-02-04-OpenClaw_vs_Claude_Code_AI_Coding_Assistant_Comparison.md --force
  
  # 2026년 포스팅 모두 처리
  python3 scripts/generate_high_quality_images.py --year 2026 --force
  
  # 모든 포스팅 이미지 재생성
  python3 scripts/generate_high_quality_images.py --all --force
        """,
    )

    parser.add_argument("post_file", nargs="?", help="처리할 포스팅 파일 (선택사항)")
    parser.add_argument("--all", action="store_true", help="모든 포스팅 처리")
    parser.add_argument("--recent", type=int, default=0, help="최근 N개 포스팅만 처리")
    parser.add_argument("--year", type=int, help="특정 연도 포스팅만 처리")
    parser.add_argument("--force", action="store_true", help="이미지가 있어도 강제로 재생성")

    args = parser.parse_args()

    # 포스팅 파일 목록
    posts = []

    if args.post_file:
        # 특정 파일 처리
        post_path = Path(args.post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_path

        if not post_path.exists():
            log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
            sys.exit(1)

        posts = [post_path]
    elif args.year:
        # 특정 연도 포스팅 처리
        year_prefix = f"{args.year}-"
        posts = sorted(
            [p for p in POSTS_DIR.glob("*.md") if p.name.startswith(year_prefix)],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
    elif args.all:
        # 모든 포스팅 처리
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
    elif args.recent > 0:
        # 최근 N개 포스팅 처리
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )[: args.recent]
    else:
        # 기본: 최근 10개
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )[:10]

    if not posts:
        log_message("❌ 처리할 포스팅이 없습니다.", "ERROR")
        sys.exit(1)

    log_message(f"📊 {len(posts)}개 포스팅 처리 시작\n")

    # 각 포스팅 처리
    success_count = 0
    for post_file in posts:
        try:
            if process_post(post_file, force=args.force):
                success_count += 1
        except Exception as e:
            log_message(f"❌ 포스팅 처리 실패: {post_file.name} - {str(e)}", "ERROR")

        print()  # 빈 줄 추가

    # 요약
    log_message("=" * 80)
    log_message(f"📊 처리 완료: {success_count}/{len(posts)}개 성공", "SUCCESS")
    log_message("=" * 80)


if __name__ == "__main__":
    main()
