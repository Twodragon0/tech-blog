#!/usr/bin/env python3
"""Auto Publish News - thin wrapper around scripts.news package.

All logic lives in scripts/news/. This module re-exports everything
for backward compatibility with tests and other scripts that do
``import auto_publish_news`` or ``from auto_publish_news import X``.

Mutable module-level state (_GEMINI_AVAILABLE, _GEMINI_CIRCUIT_OPEN,
KOREAN_TITLE_CACHE) is proxied to scripts.news.config so that
test-time patches applied to *this* module propagate correctly.
"""

import argparse
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Ensure project root is on sys.path so ``scripts.news`` is importable
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Import the news package modules
# ---------------------------------------------------------------------------
import scripts.news.config as _news_config  # noqa: E402

# Re-export analyzer functions
from scripts.news.analyzer import (  # noqa: E402,F401
    extract_cve_id,
    generate_mitre_mapping,
    generate_risk_scorecard,
)

# Re-export config constants
from scripts.news.config import (  # noqa: E402,F401
    _AI_MODE,
    _CLAUDE_API_KEY,
    _CLAUDE_MODEL,
    _GEMINI_API_KEY,
    _GEMINI_AVAILABLE,
    _GEMINI_CALL_TIMEOUT,
    _GEMINI_CIRCUIT_OPEN,
    _GEMINI_CONSECUTIVE_FAILURES,
    _GEMINI_MAX_RETRIES,
    _OPENAI_API_KEY,
    _OPENAI_GPT54_MODEL,
    CATEGORY_COLOR,
    CATEGORY_EMOJI,
    CATEGORY_PRIORITY,
    CATEGORY_SVG_CONFIG,
    DATA_DIR,
    IMAGES_DIR,
    KOREAN_SUMMARY_CACHE,
    KOREAN_TITLE_CACHE,
    MAX_NEWS_PER_CATEGORY,
    MIN_NEWS_COUNT,
    POSTS_DIR,
    PUBLISHED_URLS_FILE,
    PUBLISHED_URLS_TTL_DAYS,
    SOURCE_PRIORITY,
    SVG_MAX_FOCUS_LABELS,
    SVG_MAX_LABEL_CHARS,
    SVG_MAX_SUBTITLE_CHARS,
    SVG_TEMPLATE_BEFORE_AFTER,
    SVG_TEMPLATE_HUB_SPOKE,
    SVG_TEMPLATE_TIMELINE,
    TECH_BLOG_SOURCES,
    _OPENAI_Codex_MODEL,
)

# Re-export content generator functions
from scripts.news.content_generator import (  # noqa: E402,F401
    _apply_trend_kr_map,
    _build_digest_title,
    _html_escape_quotes,
    _determine_severity,
    _extract_cve_ids,
    _extract_digest_title_labels,
    _extract_digest_title_phrases,
    _extract_meaningful_topics,
    _extract_trend_keyword,
    _generate_ai_analysis_template,
    _generate_contextual_action_point,
    _generate_devops_template,
    _generate_executive_and_risk_sections,
    _generate_key_points,
    _generate_news_specific_checklist,
    _generate_security_analysis_template,
    _generate_security_brief_template,
    _generate_tech_trend_analysis,
    _generate_trend_analysis,
    _korean_brief_summary,
    _korean_display_title,
    _run_post_quality_gate,
    _table_summary,
    _translate_to_korean_deepseek,
    _truncate_korean_sentence,
    generate_news_section,
    generate_post_content,
    generate_tech_blog_content,
)

# Re-export enhancer functions
from scripts.news.enhancer import (  # noqa: E402,F401
    _allow_deepseek,
    _allow_gemini,
    _gemini_api_call,
    _gemini_call,
    check_gemini_available,
    enhance_content_with_fallback,
    enhance_with_claude,
    enhance_with_deepseek,
    enhance_with_gemini,
    enhance_with_openai_codex_medium,
    enhance_with_openai_gpt54,
)

# Re-export loader functions
from scripts.news.loader import (  # noqa: E402,F401
    _deduplicate_crypto_stories,
    _filter_by_cutoff,
    categorize_news,
    filter_and_prioritize_news,
    filter_published_urls,
    load_collected_news,
    load_published_urls,
    save_published_urls,
    select_top_news,
)

# Re-export QA gate functions
from scripts.news.qa_gate import (  # noqa: E402,F401
    QAGateError,
    run_qa_gate,
    validate_sentence_completeness,
    validate_stats_consistency,
    validate_trend_analysis,
)

# Re-export SVG generator functions
from scripts.news.svg_generator import (  # noqa: E402,F401
    _compose_svg_subtitle,
    _convert_svg_to_og_png,
    _escape_svg_text,
    _extract_key_topics,
    _extract_visual_focus_labels,
    _match_svg_icon,
    _normalize_svg_focus_label,
    _render_before_after_svg,
    _render_hub_spoke_svg,
    _render_timeline_svg,
    _select_svg_template,
    _svg_base_frame,
    _svg_footer,
    _svg_icon_templates,
    _to_english_svg_text,
    _truncate_text,
    generate_svg_image,
)

# ---------------------------------------------------------------------------
# Module-level __setattr__ / __getattr__ to proxy mutable config state.
#
# When conftest.py does ``auto_publish_news._GEMINI_CIRCUIT_OPEN = True``,
# this propagates the write to scripts.news.config so the actual code
# (which reads from _cfg) picks it up.
# ---------------------------------------------------------------------------
_PROXIED_CONFIG_ATTRS = frozenset(
    {
        "_GEMINI_AVAILABLE",
        "_GEMINI_CIRCUIT_OPEN",
        "_GEMINI_CONSECUTIVE_FAILURES",
        "_AI_MODE",
        "_GEMINI_API_KEY",
        "_CLAUDE_API_KEY",
        "_OPENAI_API_KEY",
    }
)

_PROXIED_CONFIG_DICTS = frozenset(
    {
        "KOREAN_TITLE_CACHE",
        "KOREAN_SUMMARY_CACHE",
    }
)

_this_module = sys.modules[__name__]


def __getattr__(name):
    if name in _PROXIED_CONFIG_ATTRS or name in _PROXIED_CONFIG_DICTS:
        return getattr(_news_config, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class _ConfigProxy:
    """Thin proxy so that ``auto_publish_news.X = val`` writes through to config."""

    def __init__(self, real_module):
        object.__setattr__(self, "_real", real_module)

    def __setattr__(self, name, value):
        if name in _PROXIED_CONFIG_ATTRS:
            setattr(_news_config, name, value)
            return
        if name in _PROXIED_CONFIG_DICTS:
            # For dict attrs like KOREAN_TITLE_CACHE, replace the dict in config
            setattr(_news_config, name, value)
            return
        object.__setattr__(self._real, name, value)

    def __getattr__(self, name):
        if name in _PROXIED_CONFIG_ATTRS or name in _PROXIED_CONFIG_DICTS:
            return getattr(_news_config, name)
        return getattr(object.__getattribute__(self, "_real"), name)

    def __repr__(self):
        return repr(object.__getattribute__(self, "_real"))


sys.modules[__name__] = _ConfigProxy(_this_module)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Auto publish news to _posts")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without publishing"
    )
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--max-news", type=int, default=15, help="Maximum news items")
    parser.add_argument(
        "--mode",
        choices=["security", "tech-blog"],
        default="security",
        help="Post mode: security (default) or tech-blog digest",
    )
    parser.add_argument(
        "--use-ai",
        choices=[
            "auto",
            "claude",
            "gemini",
            "gpt-5.4",
            "codex-medium",
            "deepseek",
            "none",
        ],
        default=os.getenv("AUTO_PUBLISH_USE_AI", "auto"),
        help="AI enrichment mode (default: auto)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force publish even if same-day post exists",
    )
    parser.add_argument(
        "--date",
        type=str,
        default="",
        help="Target publish date in YYYY-MM-DD (default: today KST)",
    )
    parser.add_argument(
        "--post-filename",
        type=str,
        default="",
        help="Override output post filename (e.g., 2026-02-21-...md)",
    )
    parser.add_argument(
        "--image-filename",
        type=str,
        default="",
        help="Override output image filename (e.g., 2026-02-21-...svg)",
    )
    args = parser.parse_args()

    _news_config._AI_MODE = args.use_ai

    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_api_key:
        logging.warning("GEMINI_API_KEY not set - API features disabled")

    print(
        f"\U0001f4f0 Auto Publish News (mode: {args.mode}, ai: {_news_config._AI_MODE})"
    )
    print("=" * 50)

    # Load news
    news_data = load_collected_news()
    print(f"\u2705 Loaded {news_data.get('total_items', 0)} news items")

    # Data freshness check
    collected_at_str = news_data.get("collected_at", "")
    if collected_at_str:
        try:
            collected_at = datetime.fromisoformat(
                collected_at_str.replace("Z", "+00:00")
            )
            data_age_hours = (
                datetime.now(timezone.utc) - collected_at
            ).total_seconds() / 3600
            if data_age_hours > 24:
                print(
                    f"\u26a0\ufe0f Data is {data_age_hours:.1f}h old. Time filter will be relaxed automatically."
                )
        except (ValueError, TypeError):
            pass

    # Filter and categorize
    filtered = filter_and_prioritize_news(news_data, hours=args.hours)

    # Cross-day dedup: remove items already published in recent posts
    published_urls = load_published_urls()
    if published_urls:
        print(f"  \U0001f4cb Loaded {len(published_urls)} previously published URLs")
    filtered = filter_published_urls(filtered, published_urls)

    if len(filtered) < MIN_NEWS_COUNT:
        print(
            f"\u26a0\ufe0f Not enough news ({len(filtered)} < {MIN_NEWS_COUNT}). Skipping."
        )
        return

    categorized = categorize_news(filtered)

    # Date setup
    now = datetime.now(timezone(timedelta(hours=9)))  # KST
    if args.date:
        try:
            forced_date = datetime.strptime(args.date, "%Y-%m-%d")
            now = now.replace(
                year=forced_date.year,
                month=forced_date.month,
                day=forced_date.day,
            )
        except ValueError:
            print(f"\u274c Invalid --date format: {args.date} (expected YYYY-MM-DD)")
            return
    date_str = now.strftime("%Y-%m-%d")

    # Duplicate check - only ONE post per day (any pattern)
    if not args.force:
        existing = list(POSTS_DIR.glob(f"{date_str}-*Digest*.md"))
        existing += list(POSTS_DIR.glob(f"{date_str}-*Weekly*.md"))
        # Deduplicate by filename
        existing = list({p.name: p for p in existing}.values())
        if existing:
            print(
                f"\u23ed\ufe0f Same-day post already exists ({len(existing)} found): {existing[0].name}"
            )
            print("   Only 1 post per day is allowed. Use --force to override.")
            return

    if args.mode == "tech-blog":
        # Filter for tech blog content only
        tech_categorized = {
            k: v
            for k, v in categorized.items()
            if k in ("tech", "devops", "ai", "cloud")
        }
        if not tech_categorized:
            print("\u26a0\ufe0f No tech blog content found. Skipping.")
            return
        selected = select_top_news(tech_categorized, args.max_news)
        topics = _extract_key_topics(selected)
        topics_slug = "_".join(topics[:3]) if topics else "Tech"

        post_content = generate_tech_blog_content(
            selected, tech_categorized, now, topics_slug
        )
        post_filename = f"{date_str}-Tech_Blog_Weekly_Digest_{topics_slug}.md"
        svg_filename = f"{date_str}-Tech_Blog_Weekly_Digest_{topics_slug}.svg"
    else:
        selected = select_top_news(categorized, args.max_news)
        topics = _extract_key_topics(selected)
        topics_slug = "_".join(topics[:4]) if topics else "News"

        post_content = generate_post_content(selected, categorized, now, topics_slug)
        post_filename = f"{date_str}-Tech_Security_Weekly_Digest_{topics_slug}.md"
        svg_filename = f"{date_str}-Tech_Security_Weekly_Digest_{topics_slug}.svg"

    if args.post_filename:
        post_filename = Path(args.post_filename).name
    if args.image_filename:
        svg_filename = Path(args.image_filename).name
        post_content = re.sub(
            r"^image:\s+.+$",
            f"image: /assets/images/{svg_filename}",
            post_content,
            flags=re.MULTILINE,
        )

    post_path = POSTS_DIR / post_filename
    svg_path = IMAGES_DIR / svg_filename

    print(f"\u2705 Selected {len(selected)} top news items")
    for cat, items in categorized.items():
        print(f"   - {cat}: {len(items)} items")

    # Generate SVG
    svg_content = generate_svg_image(now, categorized, selected)

    # Existing post protection
    if post_path.exists():
        existing_size = post_path.stat().st_size
        new_size = len(post_content.encode("utf-8"))
        if existing_size > new_size and not args.force:
            print(
                f"\u23ed\ufe0f Existing post is larger ({existing_size}B > {new_size}B). Skipping to preserve manual post."
            )
            print(f"   File: {post_path}")
            return
        else:
            print(
                f"\U0001f4dd Overwriting existing post ({existing_size}B \u2192 {new_size}B)"
            )

    # --- Pre-publish QA gate ---
    qa_issues = run_qa_gate(post_content, post_filename)
    if qa_issues:
        print(f"\u26a0\ufe0f QA gate found {len(qa_issues)} issue(s):")
        for qi in qa_issues:
            print(f"   - {qi}")

    if args.dry_run:
        print("\n\U0001f4dd [DRY RUN] Would create:")
        print(f"   - Post: {post_path}")
        print(f"   - Image: {svg_path}")
        print("\n--- Post Preview (first 500 chars) ---")
        print(post_content[:500])
        return

    # Save files
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(post_content)
    _run_post_quality_gate(post_path, target=80)

    # --- Digest quality self-check (truncation / English-header gate) ---
    try:
        from digest_quality_report import check_file as _check_digest_quality
        quality_issues = _check_digest_quality(post_path)
    except Exception as _qe:
        logging.debug(f"digest quality self-check skipped: {_qe}")
        quality_issues = []

    if quality_issues:
        post_path.unlink(missing_ok=True)
        print(
            f"\u274c Digest quality gate FAILED for {post_path.name}:",
            file=sys.stderr,
        )
        for qi in quality_issues:
            print(f"   {qi}", file=sys.stderr)
        print(
            "   Post file removed. Fix the content generator and retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\u2705 Created post: {post_path}")

    # Track published URLs for cross-day dedup
    save_published_urls(selected, date_str)

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"\u2705 Created image: {svg_path}")

    # Generate PNG for Open Graph social previews
    _convert_svg_to_og_png(svg_path)

    print(f"\n\U0001f389 Auto publish completed! (mode: {args.mode})")


if __name__ == "__main__":
    main()
