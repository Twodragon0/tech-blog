"""Module-level constants, API keys, paths, and shared configuration."""

import logging
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================================================
# Paths
# ============================================================================

POSTS_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images")
DATA_DIR = Path("_data")
PUBLISHED_URLS_FILE = DATA_DIR / "published_news_urls.json"
PUBLISHED_URLS_TTL_DAYS = 7

# ============================================================================
# Caches (mutable module-level state)
# ============================================================================

KOREAN_SUMMARY_CACHE: Dict[str, str] = {}
KOREAN_TITLE_CACHE: Dict[str, str] = {}

# ============================================================================
# Category configuration
# ============================================================================

CATEGORY_PRIORITY = {
    "security": 1,
    "devsecops": 2,
    "ai": 3,
    "cloud": 4,
    "devops": 5,
    "blockchain": 6,
    "tech": 7,
}

CATEGORY_EMOJI = {
    "security": "\U0001f512",
    "devsecops": "\U0001f6e1\ufe0f",
    "ai": "\U0001f916",
    "cloud": "\u2601\ufe0f",
    "devops": "\u2699\ufe0f",
    "tech": "\U0001f4bb",
    "kubernetes": "\U0001f680",
    "blockchain": "\u26d3\ufe0f",
    "finops": "\U0001f4b0",
}

CATEGORY_COLOR = {
    "security": "#ef4444",
    "devsecops": "#8b5cf6",
    "ai": "#6366f1",
    "cloud": "#22c55e",
    "devops": "#f59e0b",
    "blockchain": "#f97316",
    "tech": "#3b82f6",
}

# ============================================================================
# Source configuration
# ============================================================================

SOURCE_PRIORITY = {
    "thehackernews": 1,
    "microsoft_security": 1,
    "aws_security": 1,
    "gcp": 2,
    "hashicorp": 2,
    "cncf": 2,
    "geeknews": 2,
    "hackernews": 3,
    "skshieldus": 2,
    "skshieldus_report": 2,
    "palantir": 1,
    "openai": 1,
    "google_ai": 1,
    "meta_engineering": 1,
    "huggingface": 2,
    "google_research": 1,
    "netflix_tech": 2,
    "bitcoin_magazine": 1,
    "cointelegraph": 2,
    "vitalik": 1,
    "chainalysis": 1,
    "microsoft_devblogs": 1,
    "microsoft_dotnet": 2,
    "github_blog": 1,
    "stripe": 2,
    "slack_engineering": 2,
    "x_engineering": 1,
    "apple_ml": 1,
    "spotify_engineering": 2,
    "discord": 2,
    "docker": 1,
    "google_developers": 1,
    "rust_lang": 2,
    "golang": 2,
    "apple_developer": 1,
    "apple_newsroom": 2,
    "webkit": 2,
    "worldmonitor_tech": 1,
    # Korean tech blogs
    "kakao_tech": 1,
    "naver_d2": 1,
    "line_engineering": 2,
    "toss_tech": 1,
    "woowahan_tech": 2,
    "daangn_tech": 2,
    "coupang_tech": 2,
    # Korean security vendors
    "ahnlab_asec": 1,
    # AI/ML blogs
    "nvidia_ai": 1,
    # DevOps/Platform blogs
    "gitlab": 1,
    "vercel": 2,
    # Additional security vendors
    "sophos": 2,
}

TECH_BLOG_SOURCES = {
    "geeknews",
    "hackernews",
    "palantir",
    "openai",
    "google_ai",
    "meta_engineering",
    "huggingface",
    "google_research",
    "netflix_tech",
    "microsoft_devblogs",
    "microsoft_dotnet",
    "github_blog",
    "stripe",
    "slack_engineering",
    "x_engineering",
    "apple_ml",
    "spotify_engineering",
    "discord",
    "docker",
    "google_developers",
    "rust_lang",
    "golang",
    "apple_developer",
    "apple_newsroom",
    "webkit",
    "hashicorp",
    "cncf",
    "gcp",
    "worldmonitor_tech",
    # Korean tech blogs
    "kakao_tech",
    "naver_d2",
    "line_engineering",
    "toss_tech",
    "woowahan_tech",
    "daangn_tech",
    "coupang_tech",
    # AI/ML blogs
    "nvidia_ai",
    # DevOps/Platform blogs
    "gitlab",
    "vercel",
}

MIN_NEWS_COUNT = 5
MAX_NEWS_PER_CATEGORY = 5

# ============================================================================
# AI configuration
# ============================================================================

_GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
_CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
_OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
_GEMINI_AVAILABLE: Optional[bool] = None
_GEMINI_CONSECUTIVE_FAILURES: int = 0
_GEMINI_CIRCUIT_OPEN: bool = False
_AI_MODE: str = os.getenv("AUTO_PUBLISH_USE_AI", "auto").lower()
_GEMINI_CALL_TIMEOUT: int = max(8, int(os.getenv("AUTO_PUBLISH_GEMINI_TIMEOUT", "15")))
_GEMINI_MAX_RETRIES: int = max(1, int(os.getenv("AUTO_PUBLISH_GEMINI_RETRIES", "1")))
_CLAUDE_MODEL: str = os.getenv("AUTO_PUBLISH_CLAUDE_MODEL", "claude-3-5-sonnet-latest")
_OPENAI_Codex_MODEL: str = os.getenv("AUTO_PUBLISH_OPENAI_CODEX_MODEL", "gpt-5.3-codex")
_OPENAI_GPT54_MODEL: str = os.getenv("AUTO_PUBLISH_OPENAI_GPT54_MODEL", "gpt-5.4")

# ============================================================================
# SVG configuration
# ============================================================================

CATEGORY_SVG_CONFIG = {
    "security": {
        "gradient": ("dc2626", "991b1b"),
        "label": "SECURITY",
        "icon": "!",
        "icon_color": "#dc2626",
    },
    "cloud": {
        "gradient": ("10b981", "059669"),
        "label": "CLOUD",
        "icon": "AWS",
        "icon_color": "#10b981",
    },
    "devops": {
        "gradient": ("f59e0b", "d97706"),
        "label": "DEVOPS",
        "icon": "DEV",
        "icon_color": "#f59e0b",
    },
    "tech": {
        "gradient": ("3b82f6", "1d4ed8"),
        "label": "TECH",
        "icon": "AI",
        "icon_color": "#3b82f6",
    },
    "devsecops": {
        "gradient": ("8b5cf6", "6d28d9"),
        "label": "DEVSECOPS",
        "icon": "SEC",
        "icon_color": "#8b5cf6",
    },
    "ai": {
        "gradient": ("6366f1", "4f46e5"),
        "label": "AI/ML",
        "icon": "AI",
        "icon_color": "#6366f1",
    },
    "blockchain": {
        "gradient": ("f97316", "ea580c"),
        "label": "BLOCKCHAIN",
        "icon": "BC",
        "icon_color": "#f97316",
    },
}

SVG_TEMPLATE_HUB_SPOKE = "hub-spoke"
SVG_TEMPLATE_TIMELINE = "timeline"
SVG_TEMPLATE_BEFORE_AFTER = "before-after"
SVG_MAX_FOCUS_LABELS = 3
SVG_MAX_LABEL_CHARS = 10
SVG_MAX_SUBTITLE_CHARS = 32
