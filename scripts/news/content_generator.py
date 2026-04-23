"""Content generation functions for news digest posts."""

import hashlib
import html
import logging
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from scripts.news.analyzer import (
    extract_cve_id,
    generate_mitre_mapping,
    generate_risk_scorecard,
)
from scripts.news.config import (
    CATEGORY_EMOJI,
    CATEGORY_PRIORITY,
    KOREAN_SUMMARY_CACHE,
    KOREAN_TITLE_CACHE,
    MAX_NEWS_PER_CATEGORY,
)
from scripts.news.enhancer import (
    _allow_deepseek,
    _gemini_call,
    check_gemini_available,
    enhance_content_with_fallback,
)
from scripts.news.svg_generator import (
    _escape_svg_text,
    _extract_key_topics,
    _to_english_svg_text,
    _truncate_text,
)


def _html_escape_quotes(text: str) -> str:
    """Escape quotes for safe injection into Liquid include double-quoted args.

    Replaces single quotes with &#x27; and double quotes with &quot; so that
    a value injected inside double-quoted Liquid attributes (title="...") never
    breaks the parser regardless of what characters appear in news headlines.

    & is escaped first to avoid double-escaping existing entities.
    """
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&#x27;")


def _extract_meaningful_topics(news_items: List[Dict], mode: str = "security") -> str:
    if mode == "tech-blog":
        category_labels = {
            "ai": "AI",
            "cloud": "클라우드",
            "devops": "DevOps",
            "tech": "기술 동향",
            "security": "보안",
            "blockchain": "블록체인",
        }
        category_weights = {
            "ai": 3,
            "cloud": 3,
            "devops": 3,
            "security": 2,
            "blockchain": 2,
            "tech": 1,
        }
        source_profiles = [
            (r"OpenAI|Anthropic|Google AI|DeepMind|Hugging Face|NVIDIA AI", "AI", 3),
            (r"Docker|Kubernetes|Red Hat|HashiCorp|Vercel", "DevOps", 3),
            (r"AWS|Google Cloud|Cloudflare|Azure", "클라우드", 3),
            (r"GitHub|GitLab", "개발 플랫폼", 2),
            (r"GeekNews|Hacker News", "기술 동향", 1),
        ]
        topic_patterns = [
            (r"\b(AI Agent|Agentic AI)\b", "AI 에이전트"),
            (r"\b(Claude Code|Cursor|Copilot|ChatGPT|Gemini|LLM)\b", "AI 개발도구"),
            (r"\b(Open Source|Open-Source|OSS)\b", "오픈소스"),
            (r"\b(Kubernetes|K8s)\b", "쿠버네티스"),
            (r"\b(Docker|Container)\b", "컨테이너"),
            (r"\b(Rust|Golang|Go\s+\d|TypeScript)\b", "개발 언어"),
            (r"\b(React|Next\.?js|Vue|Svelte)\b", "프론트엔드"),
            (r"\b(AWS|Azure|GCP|Cloud)\b", "클라우드"),
            (r"\b(GitHub|GitLab)\b", "개발 플랫폼"),
            (r"\b(Apple|Google|Microsoft|Meta|Tesla|Spotify)\b", "빅테크 전략"),
            (r"\b(WebAssembly|WASM|gRPC|GraphQL)\b", "플랫폼 기술"),
            (r"\b(DevOps|CI/CD|Platform Engineering)\b", "플랫폼 엔지니어링"),
        ]
        fallback_topics = ["기술 동향", "DevOps"]
    else:
        category_labels = {
            "security": "보안 위협",
            "devsecops": "DevSecOps",
            "ai": "AI",
            "cloud": "클라우드 보안",
            "devops": "DevOps",
            "blockchain": "블록체인",
            "tech": "기술 동향",
        }
        category_weights = {
            "security": 4,
            "cloud": 3,
            "blockchain": 3,
            "ai": 2,
            "devsecops": 2,
            "devops": 2,
            "tech": 1,
        }
        source_profiles = [
            (
                r"The Hacker News|BleepingComputer|Dark Reading|Krebs|SANS ISC",
                "보안 위협",
                4,
            ),
            (
                r"Cloudflare|AWS|Google Cloud|Microsoft Security|Azure",
                "클라우드 보안",
                3,
            ),
            (r"Cointelegraph|CoinDesk|Bitcoin Magazine|The Block", "블록체인", 3),
            (r"OpenAI|Anthropic|NVIDIA AI|Meta Engineering", "AI", 2),
            (r"GeekNews|Hacker News", "기술 동향", 1),
        ]
        topic_patterns = [
            (r"(CVE-\d{4}-\d+)", "CVE"),
            (r"\b(ransomware|랜섬웨어)\b", "랜섬웨어"),
            (r"\b(zero-day|0-day|제로데이)\b", "제로데이"),
            (
                r"\b(Fortinet|Cisco|Palo Alto|CrowdStrike|SonicWall|Ivanti)\b",
                "보안 벤더",
            ),
            (r"\b(Chrome|Firefox|Windows|Linux|macOS|Android|iOS)\b", "플랫폼 보안"),
            (r"\b(APT\d+|Lazarus|APT28|APT29|Kimsuky)\b", "APT"),
            (r"\b(phishing|피싱)\b", "피싱"),
            (r"\b(supply chain|공급망)\b", "공급망 보안"),
            (r"\b(botnet|봇넷)\b", "봇넷"),
            (r"\b(malware|악성코드)\b", "악성코드"),
            (r"\b(authentication|MFA|SSO|인증)\b", "계정 보호"),
            (r"\b(RCE|remote code execution)\b", "원격 코드 실행"),
            (r"\b(AWS|Azure|GCP|Cloud)\b", "클라우드 보안"),
            (r"\b(Kubernetes|K8s|Docker)\b", "컨테이너 보안"),
            (r"\b(Bitcoin|Ethereum|Crypto|Web3|Blockchain|DeFi)\b", "블록체인"),
            (r"\b(AI Agent|Agentic AI|OpenAI|Gemini|LLM|AI)\b", "AI"),
        ]
        fallback_topics = ["주요 보안 이슈", "기술 동향"]

    scores: Counter[str] = Counter()
    first_seen: Dict[str, int] = {}

    for idx, item in enumerate(news_items):
        category = str(item.get("category", "tech")).lower()
        category_label = category_labels.get(category)
        if category_label:
            scores[category_label] += category_weights.get(category, 1)
            first_seen.setdefault(category_label, idx)

        source_name = str(item.get("source_name", item.get("source", "")))
        for pattern, label, weight in source_profiles:
            if re.search(pattern, source_name, re.IGNORECASE):
                scores[label] += weight
                first_seen.setdefault(label, idx)

        text = f"{item.get('title', '')} {item.get('summary', '')}"
        for pattern, label in topic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[label] += 2
                first_seen.setdefault(label, idx)

    ranked_topics = [
        topic
        for topic, _ in sorted(
            scores.items(), key=lambda item: (-item[1], first_seen.get(item[0], 999))
        )
    ]

    if not ranked_topics:
        ranked_topics = fallback_topics

    if len(ranked_topics) >= 3 and ranked_topics[0] != "기술 동향":
        ranked_topics = [t for t in ranked_topics if t != "기술 동향"] + [
            t for t in ranked_topics if t == "기술 동향"
        ]

    title_keywords = ", ".join(ranked_topics[:3])
    if len(title_keywords) > 80:
        title_keywords = title_keywords[:80].rstrip(" ,.")
    return title_keywords


# Korean particles/endings that indicate an incomplete phrase.
# Shared between _trim_dangling_particles, _title_quality_score, and _smart_truncate_korean.
_DANGLING_SUFFIXES_RE = re.compile(
    r"(?:를|을|의|에|에서|으로|로|이|가|는|은|및|와|과|위해|위한|하는|하기|하여|통해|대한"
    r"|하지|한|된|되는|되며|되지|되고|되자|려는|면서|지만|라는|라고|처럼|마저|까지)"
    r"\s*[,.]?\s*$"
)

# Trailing patterns that signal cut-mid-number or cut-mid-count.
# Compound Korean units (5천만 = 50 million, 2억 5천 등) are matched greedily
# so "5천만" is consumed as a single unit rather than leaving "만" dangling.
_TRAILING_COUNT_RE = re.compile(
    r"(?:\d+(?:천만|백만|억|조|천|만|%|\s?[GMK]B))\s*[,]?\s*$"
)


def _trim_dangling_particles(text: str, min_len: int = 6) -> str:
    """Strip Korean particles/endings that leave a phrase hanging mid-sentence.

    Repeatedly cuts the last token while the result still ends with a dangling
    particle and stays above ``min_len``. Also strips trailing numeric fragments
    like "5천만," that indicate the following noun was truncated away.
    """
    if not text:
        return text
    while len(text) > min_len and (
        _DANGLING_SUFFIXES_RE.search(text) or _TRAILING_COUNT_RE.search(text)
    ):
        stripped = _DANGLING_SUFFIXES_RE.sub("", text)
        stripped = _TRAILING_COUNT_RE.sub("", stripped)
        if " " in stripped:
            stripped = stripped.rsplit(" ", 1)[0]
        stripped = stripped.rstrip(" ,.")
        if stripped == text or not stripped:
            break
        text = stripped
    return text.rstrip(" ,.")


def _smart_truncate_korean(text: str, max_len: int) -> str:
    """Truncate Korean text while preserving sentence/phrase boundaries.

    Preference order for the cut point:
      1. Sentence terminator (. ! ?)
      2. Phrase separator (, ; : — | )
      3. Space
      4. Hard cut (last resort)

    The result is further passed through :func:`_trim_dangling_particles`
    so that common Korean particles aren't left hanging.
    """
    if not text or len(text) <= max_len:
        return _trim_dangling_particles(text.rstrip(" ,.") if text else text)

    window = text[: max_len + 1]
    # Prefer strong terminators
    for terminators in (".!?", ",;:—|"):
        cut = -1
        for ch in terminators:
            idx = window.rfind(ch)
            if idx > cut:
                cut = idx
        if cut > max_len // 2:
            return _trim_dangling_particles(window[:cut].rstrip(" ,."))

    # Fall back to last space
    if " " in window:
        return _trim_dangling_particles(window.rsplit(" ", 1)[0].rstrip(" ,."))

    return _trim_dangling_particles(text[:max_len].rstrip(" ,."))


def _extract_digest_title_phrases(
    news_items: List[Dict], mode: str = "security", limit: int = 3
) -> List[str]:
    """Build a more specific digest title from top headlines."""
    phrases: List[str] = []
    seen: set[str] = set()

    for item in news_items[:8]:
        raw_title = _korean_display_title(item, max_len=72)
        candidate = re.split(r"\s*[|:]+\s*|\s+-\s+", raw_title)[0].strip()
        candidate = re.sub(r"\s+", " ", candidate).strip(" ,.")

        if len(candidate) < 8:
            candidate = raw_title.strip(" ,.")
        if len(candidate) > 26:
            candidate = _smart_truncate_korean(candidate, max_len=26)

        # Trim dangling Korean particles (cut back to last noun)
        candidate = _trim_dangling_particles(candidate, min_len=6)

        if not candidate or len(candidate) < 4:
            continue

        dedupe_key = candidate.lower()
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        phrases.append(candidate)
        if len(phrases) >= limit:
            break

    if mode == "tech-blog":
        generic = {"기술 동향", "개발 플랫폼", "빅테크 전략"}
    else:
        generic = {"보안 위협", "클라우드 보안", "AI", "기술 동향"}

    phrases = [p for p in phrases if p not in generic]
    return phrases[:limit]


def _extract_digest_title_labels(
    news_items: List[Dict], mode: str = "security"
) -> List[str]:
    """Fallback title labels built from high-signal keywords."""
    label_map = [
        (r"zero-day|0-day|제로데이|cve-", "제로데이"),
        (r"ransomware|랜섬웨어", "랜섬웨어"),
        (r"malware|악성코드", "악성코드"),
        (r"byovd|driver|edr", "BYOVD EDR"),
        (r"dns|exfil|data leak|유출", "DNS 유출"),
        (r"telnet", "Telnetd"),
        (r"cisco|fmc", "Cisco FMC"),
        (r"dprk|north korea|북한", "북한 위협"),
        (r"ai agent|agentic|llm|model", "AI 에이전트"),
        (r"kubernetes|k8s|gke|cluster", "쿠버네티스"),
        (r"cloud|aws|azure|gcp", "클라우드"),
        (r"patch|update", "패치"),
    ]
    labels: List[str] = []
    seen: set[str] = set()

    for item in news_items[:8]:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        for pattern, label in label_map:
            if re.search(pattern, text) and label not in seen:
                seen.add(label)
                labels.append(label)
                if len(labels) >= 3:
                    return labels

    fallback = _extract_meaningful_topics(news_items, mode=mode).split(", ")
    for label in fallback:
        if label not in seen:
            labels.append(label)
        if len(labels) >= 3:
            break

    normalized_labels: List[str] = []
    for label in labels:
        if label == "AI" and any(existing.startswith("AI ") for existing in labels):
            continue
        if label == "클라우드" and any("쿠버네티스" in existing for existing in labels):
            continue
        if label not in normalized_labels:
            normalized_labels.append(label)
    return normalized_labels[:3]


def _build_clean_excerpt(
    title_keywords: str,
    date_str: str,
    total: int,
    mode: str,
    topics: list[str] | None = None,
) -> str:
    """품질 검증된 excerpt 생성 - 조사 자동 보정, 150-200자 보장"""
    # 조사 보정: 받침 여부에 따라 을/를 선택
    last_char = title_keywords.rstrip()[-1] if title_keywords.rstrip() else ""
    particle = "을" if _has_batchim(last_char) else "를"

    if mode == "tech":
        first = f"{title_keywords}{particle} 중심으로 {date_str} 주요 기술 블로그 뉴스 {total}건과 개발자 관점의 적용 포인트를 정리합니다."
        # 보충 문장: topics에서 키워드 추가 또는 고정 확장
        extra_topics = [t for t in (topics or []) if t not in title_keywords][:3]
        if extra_topics:
            kw = ", ".join(extra_topics)
            second = f" {kw} 등 최신 개발 트렌드와 실무 적용 사례를 함께 다룹니다."
        else:
            second = " 오픈소스, 클라우드 인프라, AI 도구 등 실무 관련 개발 트렌드와 적용 사례를 함께 다룹니다."
    else:
        first = f"{title_keywords}{particle} 중심으로 {date_str} 주요 보안/기술 뉴스 {total}건과 대응 우선순위를 정리합니다."
        extra_topics = [t for t in (topics or []) if t not in title_keywords][:3]
        if extra_topics:
            kw = ", ".join(extra_topics)
            second = (
                f" {kw} 등 최신 위협 동향과 DevSecOps 실무 대응 방안을 함께 다룹니다."
            )
        else:
            second = " 취약점 패치, 클라우드 보안, 공급망 위협 등 DevSecOps 실무 대응 방안을 함께 다룹니다."

    excerpt = first + second

    # 200자 초과 시 마지막 완성된 문장 단위로 자르되 최소 150자 유지
    if len(excerpt) > 200:
        # 마지막 마침표 기준으로 200자 이내 최대 길이 탐색
        cut = excerpt[:200]
        last_period = max(cut.rfind("다. "), cut.rfind("다."))
        if last_period > 149:
            excerpt = excerpt[: last_period + 2].rstrip()
        else:
            excerpt = excerpt[:200]

    # 150자 미달 시 fallback 보충 문장 추가 (적용 후에도 부족하면 추가 확장)
    if len(excerpt) < 150:
        if mode == "tech":
            filler = " 실무 개발자를 위한 핵심 인사이트와 최신 기술 동향을 한눈에 확인하세요."
        else:
            filler = " 보안 담당자를 위한 핵심 위협 정보와 실무 대응 가이드를 한눈에 확인하세요."
        excerpt = (excerpt + filler)[:200]

    # 여전히 150자 미달이면 주차 정보로 추가 보완
    if len(excerpt) < 150:
        excerpt = (
            excerpt
            + " 매주 업데이트되는 주간 다이제스트를 통해 최신 동향을 놓치지 마세요."
        )[:200]

    return excerpt


def _build_clean_description(
    title_keywords: str, source_list: str, date_str: str, total: int, mode: str
) -> str:
    """품질 검증된 description 생성 - 단어 나열 방지"""
    # title_keywords에서 핵심 구문 3개를 추출하여 자연스러운 문장 구성
    parts = [p.strip() for p in title_keywords.split(",") if p.strip()]
    if len(parts) >= 3:
        keywords_text = f"{parts[0]}, {parts[1]}, {parts[2]}"
    elif len(parts) == 2:
        keywords_text = f"{parts[0]}, {parts[1]}"
    else:
        keywords_text = title_keywords

    # 빈 구문 제거 후 고아 쉼표 정리
    parts = [p for p in parts if len(p.strip()) >= 2]
    if len(parts) >= 3:
        keywords_text = f"{parts[0]}, {parts[1]}, {parts[2]}"
    elif len(parts) == 2:
        keywords_text = f"{parts[0]}, {parts[1]}"
    elif parts:
        keywords_text = parts[0]
    # 각 구문이 너무 짧거나 단어 조각이면 전체 사용
    if not parts or any(len(p) < 2 for p in parts[:3]):
        keywords_text = re.sub(r",\s*,", ",", title_keywords[:60]).rstrip(" ,.")

    if mode == "tech":
        desc = f"{date_str} 기술 블로그 다이제스트. {source_list} 등 {total}건을 분석하고 {keywords_text} 등 개발자 트렌드와 운영 시사점을 정리합니다."
    else:
        desc = f"{date_str} 보안 뉴스 요약. {source_list} 등 {total}건을 분석하고 {keywords_text} 등 DevSecOps 대응 포인트를 정리합니다."

    # 150자 미만이면 보충 문장을 추가하여 SEO 최소 길이 보장 (최대 2회)
    padding_tech = [
        " 매주 업데이트되는 개발자 트렌드 정보를 한곳에서 확인하세요.",
        " 클라우드, 보안, DevOps 최신 동향을 빠르게 파악하세요.",
        " 실무에 바로 적용 가능한 기술 인사이트를 제공합니다.",
    ]
    padding_sec = [
        " 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요.",
        " CVE, 패치, 인프라 보안 이슈를 빠르게 파악하세요.",
        " DevSecOps 실무자를 위한 핵심 보안 정보를 제공합니다.",
    ]
    padding = padding_tech if mode == "tech" else padding_sec
    for pad in padding:
        if len(desc) >= 150:
            break
        desc += pad

    return desc[:300]


def _build_clean_image_alt(title_keywords: str, mode: str) -> str:
    """품질 검증된 image_alt 생성 - 공백/조각 방지, 영문만"""
    alt_text = _to_english_svg_text(title_keywords)
    # 연속 공백, 고아 쉼표 정리
    alt_text = re.sub(r"\s*,\s*,\s*", ", ", alt_text)
    alt_text = re.sub(r"\s{2,}", " ", alt_text)
    alt_text = alt_text.strip(" ,;:-")
    # 너무 짧거나 폴백인 경우 mode 기반 기본값
    if not alt_text or alt_text == "Security News Update" or len(alt_text) < 10:
        suffix = "security" if mode == "security" else "tech"
        return f"Weekly {suffix} digest overview"
    suffix = "security" if mode == "security" else "tech"
    return f"{alt_text} - {suffix} digest overview"


def _has_batchim(char: str) -> bool:
    """한글 문자의 받침 여부 확인"""
    if not char or not ("가" <= char <= "힣"):
        return False
    code = ord(char) - 0xAC00
    return (code % 28) != 0


def _title_quality_score(title: str) -> int:
    """제목 품질 점수 (0-100). 낮을수록 나쁨."""
    score = 100
    # Dangling Korean particles at phrase boundaries (shared with trim helper)
    for part in title.split(","):
        stripped = part.strip()
        if _DANGLING_SUFFIXES_RE.search(stripped):
            score -= 20
        elif _TRAILING_COUNT_RE.search(stripped):
            score -= 15
    # Too many commas = keyword soup
    comma_count = title.count(",")
    if comma_count > 4:
        score -= 15
    # Very short phrases between commas
    parts = [p.strip() for p in title.split(",")]
    short_parts = sum(1 for p in parts if len(p) < 4)
    score -= short_parts * 10
    # Repeated words
    words = title.lower().split()
    if len(words) != len(set(words)):
        score -= 15
    # Length check
    if len(title) > 70:
        score -= 10
    elif len(title) < 15:
        score -= 10
    return max(0, score)


def _build_digest_title(news_items: List[Dict], mode: str = "security") -> str:
    """Prefer specific headline-driven titles over generic topic buckets.
    Falls back to label-based title if quality score is too low."""
    headline_phrases = _extract_digest_title_phrases(news_items, mode=mode, limit=3)
    weak_english_starts = (
        "how ",
        "when ",
        "why ",
        "what ",
        "inside ",
        "introducing ",
        "announcing ",
        "from ",
    )

    weak_phrase_count = sum(
        1 for p in headline_phrases if p.lower().startswith(weak_english_starts)
    )
    headline_joined = " ".join(headline_phrases)
    has_korean = bool(re.search(r"[가-힣]", headline_joined))
    has_markdown_noise = any("*" in p or "#" in p for p in headline_phrases)

    if headline_phrases and not (
        has_markdown_noise or (weak_phrase_count >= 1 and not has_korean)
    ):
        title = ", ".join(headline_phrases)
        score = _title_quality_score(title)
        logging.info(f"[Title QA] score={score} title={title!r}")
        # Quality gate: reject low-quality titles
        if score < 50:
            label_title = ", ".join(_extract_digest_title_labels(news_items, mode=mode))
            if label_title:
                fallback = label_title[:80].rstrip(" ,.")
                logging.warning(f"[Title QA] fallback={fallback!r} (score {score}<50)")
                return fallback
        if len(title) <= 80:
            return title

    label_title = ", ".join(_extract_digest_title_labels(news_items, mode=mode))
    if label_title:
        return label_title[:80].rstrip(" ,.")

    return _extract_meaningful_topics(news_items, mode=mode)


def _generate_executive_and_risk_sections(
    news_items: List[Dict],
    mode: str = "security",
    counts: Optional[Dict[str, int]] = None,
) -> str:
    if counts is not None:
        # Use caller-supplied rendered-tag counts (post-render path: structural guarantee).
        critical_count = counts.get("Critical", 0)
        high_count = counts.get("High", 0)
        medium_count = counts.get("Medium", 0) + counts.get("Low", 0)
        # Title text for briefing bullets: prefer items whose _determine_severity
        # matches, but fall back to top items by priority when there are fewer
        # matching items than the injected count (e.g. severity logic evolves).
        # The count is authoritative; titles are best-effort display text only.
        _by_sev: Dict[str, List[str]] = {"Critical": [], "High": []}
        _fallback_titles = [
            _korean_display_title(item, max_len=35) for item in news_items
        ]
        for item in news_items:
            sev = _determine_severity(item)
            if sev in _by_sev:
                _by_sev[sev].append(_korean_display_title(item, max_len=35))
        # Fill to the required count using fallback titles when needed.
        def _fill_titles(sev_list: List[str], n: int) -> List[str]:
            result = sev_list[:n]
            if len(result) < n:
                extras = [t for t in _fallback_titles if t not in result]
                result += extras[: n - len(result)]
            return result

        critical_titles = _fill_titles(_by_sev["Critical"], critical_count)
        high_titles = _fill_titles(_by_sev["High"], high_count)
    else:
        critical_count = 0
        high_count = 0
        medium_count = 0
        critical_titles = []
        high_titles = []

        for item in news_items:
            severity = _determine_severity(item)
            title = _korean_display_title(item, max_len=35)
            if severity == "Critical":
                critical_count += 1
                critical_titles.append(title)
            elif severity == "High":
                high_count += 1
                high_titles.append(title)
            else:
                medium_count += 1

    if critical_count > 0 or high_count >= 3:
        overall = "High"
    elif high_count > 0 or medium_count >= 5:
        overall = "Medium"
    else:
        overall = "Low"

    severity_rank = {"Critical": 0, "High": 1, "Medium": 2}
    ranked_items = sorted(
        news_items,
        key=lambda item: (
            severity_rank.get(_determine_severity(item), 3),
            CATEGORY_PRIORITY.get(str(item.get("category", "tech")).lower(), 99),
        ),
    )
    top_items = ranked_items[:3]
    text_blob = " ".join(
        f"{item.get('title', '')} {item.get('summary', '')}" for item in news_items
    ).lower()

    if mode == "tech-blog":
        briefing_lines = []
        for item in top_items[:2]:
            title = _korean_display_title(item, max_len=54)
            action = _generate_contextual_action_point(item)
            briefing_lines.append(f"- {title} 이슈는 {action}")
        if len(briefing_lines) < 2:
            briefing_lines.extend(
                [
                    "- 이번 주기는 기술 도입 속도보다 표준화된 검증 흐름 설계가 더 중요합니다.",
                    "- 배포 전 검증, 권한 통제, 장애 복구 연습을 같은 운영 주기로 관리해야 합니다.",
                ][len(briefing_lines) :]
            )

        rows = [
            "| 영역 | 현재 위험도 | 즉시 조치 |",
            "|------|-------------|-----------|",
            f"| 배포 안정성 | {overall} | 릴리즈 체크리스트와 롤백 절차 점검 |",
            "| 개발 생산성 | Medium | 핵심 도구 표준화 및 팀 가이드 업데이트 |",
        ]
        for item in top_items:
            area = {
                "ai": "AI 자동화",
                "cloud": "플랫폼 운영",
                "devops": "배포 안정성",
                "kubernetes": "클러스터 운영",
            }.get(str(item.get("category", "tech")).lower(), "기술 운영")
            rows.append(
                f"| {area} | {_determine_severity(item)} | {_korean_display_title(item, max_len=34)} 점검 |"
            )
    else:
        briefing_lines = []
        if critical_titles:
            briefing_lines.append(
                f"- **긴급 대응 필요**: {', '.join(critical_titles[:2])} 등 Critical 등급 위협 {critical_count}건이 확인되었습니다."
            )
        if high_titles:
            briefing_lines.append(
                f"- **주요 모니터링 대상**: {', '.join(high_titles[:3])} 등 High 등급 위협 {high_count}건에 대한 탐지 강화가 필요합니다."
            )
        if any(
            kw in text_blob for kw in ["ransomware", "랜섬웨어", "encryption", "암호화"]
        ):
            briefing_lines.append(
                "- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다."
            )
        elif any(kw in text_blob for kw in ["zero-day", "제로데이", "0-day"]):
            briefing_lines.append(
                "- 제로데이 취약점이 보고되었으며, 임시 완화 조치 적용과 벤더 패치 일정 확인이 시급합니다."
            )
        elif any(kw in text_blob for kw in ["supply chain", "공급망"]):
            briefing_lines.append(
                "- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다."
            )
        if not briefing_lines:
            briefing_lines = [
                "- 이번 주기는 취약점 대응과 탐지 체계 운영이 동시에 요구됩니다.",
                "- 노출 자산 우선순위 기반의 패치와 룰 업데이트가 가장 높은 개선 효과를 제공합니다.",
            ]

        candidate_rows = [
            (
                "위협 대응",
                f"| 위협 대응 | {overall} | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |",
            ),
            (
                "탐지/모니터링",
                "| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |",
            ),
        ]
        if any(
            kw in text_blob
            for kw in ["cve", "취약점", "vulnerability", "patch", "패치"]
        ):
            cve_level = "Critical" if critical_count > 0 else "High"
            candidate_rows.append(
                (
                    "취약점 관리",
                    f"| 취약점 관리 | {cve_level} | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |",
                )
            )
        if any(
            kw in text_blob
            for kw in ["cloud", "aws", "gcp", "azure", "kubernetes", "k8s", "iam"]
        ):
            candidate_rows.append(
                (
                    "클라우드 보안",
                    "| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |",
                )
            )
        if any(
            kw in text_blob for kw in ["ai", "llm", "agent", "ml", "prompt injection"]
        ):
            candidate_rows.append(
                (
                    "AI/ML 보안",
                    "| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |",
                )
            )
        if any(
            kw in text_blob for kw in ["ransomware", "랜섬웨어", "encryption", "암호화"]
        ):
            candidate_rows.append(
                (
                    "운영 복원력",
                    "| 운영 복원력 | Medium | 백업/복구 및 사고 대응 절차 리허설 |",
                )
            )

        ordered_labels = [
            "위협 대응",
            "탐지/모니터링",
            "취약점 관리",
            "클라우드 보안",
            "AI/ML 보안",
            "운영 복원력",
        ]
        row_map = {label: row for label, row in candidate_rows}
        selected_rows = [
            row_map[label] for label in ordered_labels if label in row_map
        ][:4]
        rows = [
            "| 영역 | 현재 위험도 | 즉시 조치 |",
            "|------|-------------|-----------|",
            *selected_rows,
        ]

    briefing = "\n".join(briefing_lines)

    return (
        "## 경영진 브리핑\n\n"
        f"{briefing}\n\n"
        "## 위험 스코어카드\n\n" + "\n".join(rows) + "\n\n"
    )


def _run_post_quality_gate(post_path: Path, target: int = 80) -> None:
    try:
        from upgrade_digest_post_quality import process_file as _upgrade_post
        from validate_post_quality import validate_post as _validate_post
    except Exception as e:
        logging.debug(f"quality gate import skipped: {e}")
        return

    first = _validate_post(post_path)
    first_score = first.get("total", 0)
    score_before = first_score if isinstance(first_score, int) else 0

    if score_before >= target:
        logging.info(f"Post quality score {score_before}/100 (target {target})")
        return

    upgraded = _upgrade_post(post_path)
    if not upgraded:
        logging.warning(
            f"Post quality score {score_before}/100 below target {target} (no auto-upgrade applied)"
        )
        return

    second = _validate_post(post_path)
    second_score = second.get("total", 0)
    score_after = second_score if isinstance(second_score, int) else score_before
    logging.info(
        f"Post quality auto-upgrade: {score_before}/100 -> {score_after}/100 (target {target})"
    )


def _format_stats_block(stats: Dict[str, int], total: int) -> str:
    """Build the stats block dynamically so every category is represented.

    Known categories are displayed with Korean labels in a fixed order.
    Any remaining items that don't belong to a known category are summed
    into a '기타 뉴스' line.  An assertion guarantees the displayed
    category counts sum exactly to *total*.
    """
    _KNOWN_CATEGORIES = [
        ("security", "보안 뉴스"),
        ("ai", "AI/ML 뉴스"),
        ("cloud", "클라우드 뉴스"),
        ("devops", "DevOps 뉴스"),
        ("blockchain", "블록체인 뉴스"),
    ]

    lines: list[str] = [f"- **총 뉴스 수**: {total}개"]
    shown_sum = 0
    shown_keys: set[str] = set()

    for key, label in _KNOWN_CATEGORIES:
        count = stats.get(key, 0)
        if count > 0:
            lines.append(f"- **{label}**: {count}개")
            shown_sum += count
            shown_keys.add(key)

    # Remaining categories → '기타 뉴스'
    etc_count = 0
    for key, count in stats.items():
        if key not in shown_keys:
            etc_count += count
    if etc_count > 0:
        lines.append(f"- **기타 뉴스**: {etc_count}개")
        shown_sum += etc_count

    assert shown_sum == total, (
        f"Stats block category sum mismatch: {shown_sum} != {total} (stats={stats})"
    )

    return "\n".join(lines)


def generate_post_content(
    news_items: List[Dict],
    categorized: Dict[str, List[Dict]],
    date: datetime,
    topics_slug: str = "",
) -> str:
    """고품질 포스트 컨텐츠 생성"""

    date_str = date.strftime("%Y년 %m월 %d일")
    date_file = date.strftime("%Y-%m-%d")
    image_filename = (
        f"{date_file}-Tech_Security_Weekly_Digest_{topics_slug}.svg"
        if topics_slug
        else f"{date_file}-Tech_Security_Weekly_Digest.svg"
    )

    stats = {cat: len(items) for cat, items in categorized.items()}
    total = sum(stats.values())

    # 핵심 뉴스 추출
    security_news = categorized.get("security", [])[:3]
    ai_news = categorized.get("ai", [])[:3]
    cloud_news = categorized.get("cloud", [])[:3]
    devops_news = categorized.get("devops", [])[:3]
    blockchain_news = categorized.get("blockchain", [])[:3]
    tech_news = categorized.get("tech", [])[:3]

    # 핵심 하이라이트 생성
    highlights = []
    for item in (security_news + cloud_news)[:4]:
        source = item.get("source_name", item.get("source", "Unknown"))
        title = _korean_display_title(item)
        if len(title) > 60:
            title = title[:60].rsplit(" ", 1)[0].rstrip(" ,.")
        source = html.escape(source)
        title = html.escape(title)
        highlights.append(f"<li><strong>{source}</strong>: {title}</li>")

    highlights_html = (
        "\n      ".join(highlights)
        if highlights
        else "<li>오늘의 주요 뉴스를 확인하세요</li>"
    )

    topics = _extract_key_topics(news_items)

    # Better title generation: extract meaningful topics from content
    title_keywords = _build_digest_title(news_items, mode="security")

    base_tags = [
        "Security-Weekly",
        "DevSecOps",
        "Cloud-Security",
        "Weekly-Digest",
        str(date.year),
    ]
    topic_tags = [t for t in topics if t not in base_tags]
    tags = base_tags + topic_tags[:5]

    top_sources = list(
        {item.get("source_name", ""): True for item in news_items[:5]}.keys()
    )[:3]
    source_list = ", ".join(top_sources)

    # Generate Jekyll include tag for AI summary card - dynamic tags from actual content
    categories_html = '<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
    # Build tags from actual topics instead of hardcoding
    dynamic_tags = ["Security-Weekly"]
    for topic in topics[:4]:
        if topic not in dynamic_tags:
            dynamic_tags.append(topic)
    dynamic_tags.append(str(date.year))
    tags_html = "\n      ".join(
        f'<span class="tag">{t}</span>' for t in dynamic_tags[:6]
    )

    # Escape quotes in title before Liquid injection to prevent parser breakage
    # (e.g. headlines containing inner single quotes like '퇴행적' would terminate
    # a single-quoted arg prematurely). Use double-quoted outer + entity encoding.
    safe_title = _html_escape_quotes(title_keywords)

    content = f'''---
layout: post
title: "{title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [security, devsecops]
tags: [{", ".join(tags)}]
excerpt: "{_build_clean_excerpt(title_keywords, date_str, total, "security", topics)}"
description: "{_build_clean_description(title_keywords, source_list, date_str, total, "security")}"
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "{_build_clean_image_alt(title_keywords, "security")}"
toc: true
---

{{% include ai-summary-card.html
  title="{safe_title}"
  categories_html='{categories_html}'
  tags_html='{tags_html}'
  highlights_html='{highlights_html}'
  period='{date_str} (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}}

---

## 서론

안녕하세요, **Twodragon**입니다.

{date_str} 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
{_format_stats_block(stats, total)}

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
'''

    # 하이라이트 테이블 생성 (주요 섹션 포괄)
    highlight_items = []
    for cat_items in [
        security_news,
        ai_news,
        cloud_news,
        devops_news,
        blockchain_news,
        tech_news,
    ]:
        for it in cat_items:
            if it not in highlight_items:
                highlight_items.append(it)
    for item in highlight_items[:10]:
        source = item.get("source_name", item.get("source", "Unknown"))[:20]
        title = _korean_display_title(item, max_len=60)
        category = item.get("category", "tech")
        emoji = CATEGORY_EMOJI.get(category, "📰")
        # Category display name mapping
        cat_display = {
            "security": "Security",
            "devsecops": "DevSecOps",
            "ai": "AI/ML",
            "cloud": "Cloud",
            "devops": "DevOps",
            "blockchain": "Blockchain",
            "tech": "Tech",
            "kubernetes": "K8s",
            "finops": "FinOps",
        }.get(category, category.title())
        severity = _determine_severity(item)
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(
            severity, "🟡"
        )
        content += f"| {emoji} **{cat_display}** | {source} | {title} | {severity_emoji} {severity} |\n"

    content += "\n---\n\n"

    # Items that will become rendered news cards (used for briefing title text).
    rendered_items = (
        security_news
        + ai_news
        + cloud_news
        + devops_news
        + blockchain_news
        + tech_news
    )

    # Build news sections FIRST so we can count the actual severity="..." tags
    # they emit. This is the structural guarantee that briefing '등 N건' counts
    # always match card reality, regardless of future changes to severity logic.
    section_num = 1
    news_sections = ""

    # 보안 뉴스 섹션 - SK Shieldus 그룹핑 포함
    if security_news:
        news_sections += f"## {section_num}. 보안 뉴스\n\n"

        # Separate SK Shieldus reports from regular security news
        skshieldus_reports = [
            item for item in security_news if item.get("source") == "skshieldus_report"
        ]
        regular_security = [
            item for item in security_news if item.get("source") != "skshieldus_report"
        ]

        for i, item in enumerate(regular_security, 1):
            is_critical = i <= 5  # 상위 5개 뉴스에 AI 강화 적용
            news_sections += generate_news_section(
                item, f"{section_num}.{i}", is_critical=is_critical
            )

        # SK Shieldus reports grouped into a single subsection
        if skshieldus_reports:
            sub_idx = len(regular_security) + 1
            month_str = (
                date.strftime("%-m월")
                if sys.platform != "win32"
                else date.strftime("%m월").lstrip("0")
            )
            news_sections += (
                f"### {section_num}.{sub_idx} SK쉴더스 {month_str} 보안 리포트\n\n"
            )
            news_sections += "SK쉴더스에서 발행한 최신 보안 리포트 모음입니다.\n\n"
            for report in skshieldus_reports:
                report_title = report.get("title", "보안 리포트")
                report_url = report.get("url", "")
                report_summary = report.get("summary", "")
                news_sections += f"- **[{report_title}]({report_url})**"
                if report_summary:
                    short_summary = report_summary[:100].rstrip(".")
                    news_sections += f": {short_summary}"
                news_sections += "\n"
            news_sections += "\n> SK쉴더스 보안 리포트는 국내 보안 환경에 특화된 위협 분석을 제공합니다. 원문을 다운로드하여 상세 내용을 확인하시기 바랍니다.\n\n"
            news_sections += "---\n\n"

        section_num += 1

    # AI/ML 뉴스 섹션
    if ai_news:
        news_sections += f"## {section_num}. AI/ML 뉴스\n\n"
        for i, item in enumerate(ai_news, 1):
            news_sections += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 클라우드 뉴스 섹션
    if cloud_news:
        news_sections += f"## {section_num}. 클라우드 & 인프라 뉴스\n\n"
        for i, item in enumerate(cloud_news, 1):
            news_sections += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # DevOps 뉴스 섹션
    if devops_news:
        news_sections += f"## {section_num}. DevOps & 개발 뉴스\n\n"
        for i, item in enumerate(devops_news, 1):
            news_sections += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 블록체인 뉴스 섹션
    if blockchain_news:
        news_sections += f"## {section_num}. 블록체인 뉴스\n\n"
        for i, item in enumerate(blockchain_news, 1):
            news_sections += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # Count severity tags from the rendered output — this is the ground truth.
    _rendered_sev_tags = re.findall(
        r'severity="(Critical|High|Medium|Low)"', news_sections
    )
    _rendered_counts: Dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for _s in _rendered_sev_tags:
        _rendered_counts[_s] += 1

    # Generate briefing using rendered-tag counts (not re-classified item severities).
    content += _generate_executive_and_risk_sections(
        rendered_items, mode="security", counts=_rendered_counts
    )

    # Append pre-built news sections.
    content += news_sections

    # 기타 뉴스
    if tech_news:
        content += f"## {section_num}. 기타 주목할 뉴스\n\n"
        content += "| 제목 | 출처 | 핵심 내용 |\n"
        content += "|------|------|----------|\n"
        for item in tech_news[:5]:
            title = _korean_display_title(item, max_len=50)
            source = item.get("source_name", "")
            url = item.get("url", "")
            summary = _table_summary(_korean_brief_summary(item).replace("\n", " "))
            content += f"| [{title}]({url}) | {source} | {summary} |\n"
        content += "\n"
        section_num += 1

    # 트렌드 분석 섹션
    content += _generate_trend_analysis(news_items, section_num)
    section_num += 1

    # 뉴스 기반 실무 체크리스트
    content += _generate_news_specific_checklist(news_items)

    content += """## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
"""

    return content


def generate_tech_blog_content(
    news_items: List[Dict],
    categorized: Dict[str, List[Dict]],
    date: datetime,
    topics_slug: str = "",
) -> str:
    """Tech Blog Weekly Digest 컨텐츠 생성.

    Filters for geeknews, hackernews, and tech blog sources (NOT security/blockchain).
    Groups by topic: AI/ML, DevOps/Cloud, Open Source, General.
    Uses GeekNews Korean summaries prominently.
    """
    date_str = date.strftime("%Y년 %m월 %d일")
    date_file = date.strftime("%Y-%m-%d")
    image_filename = (
        f"{date_file}-Tech_Blog_Weekly_Digest_{topics_slug}.svg"
        if topics_slug
        else f"{date_file}-Tech_Blog_Weekly_Digest.svg"
    )

    total = len(news_items)

    # Group items by topic
    topic_groups = {
        "AI/ML": [],
        "DevOps/Cloud": [],
        "Open Source": [],
        "General": [],
    }

    ai_keywords = [
        "ai",
        "ml",
        "llm",
        "gpt",
        "claude",
        "gemini",
        "chatgpt",
        "copilot",
        "machine learning",
        "deep learning",
        "neural",
        "transformer",
        "agent",
    ]
    devops_keywords = [
        "kubernetes",
        "k8s",
        "docker",
        "cloud",
        "aws",
        "azure",
        "gcp",
        "terraform",
        "ci/cd",
        "devops",
        "sre",
        "infrastructure",
        "helm",
        "container",
        "serverless",
        "microservice",
    ]
    oss_keywords = [
        "open source",
        "open-source",
        "oss",
        "github",
        "rust",
        "golang",
        "go ",
        "python",
        "typescript",
        "linux",
        "apache",
        "mit license",
        "cncf",
    ]

    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()
        category = item.get("category", "tech")

        if any(kw in text for kw in ai_keywords) or category == "ai":
            topic_groups["AI/ML"].append(item)
        elif any(kw in text for kw in devops_keywords) or category in (
            "devops",
            "cloud",
        ):
            topic_groups["DevOps/Cloud"].append(item)
        elif any(kw in text for kw in oss_keywords):
            topic_groups["Open Source"].append(item)
        else:
            topic_groups["General"].append(item)

    # Invariant: topic_groups must account for all items
    group_sum = sum(len(v) for v in topic_groups.values())
    assert group_sum == total, (
        f"Tech-blog topic group sum mismatch: {group_sum} != {total}"
    )

    # Title generation for tech-blog mode
    title_keywords = _build_digest_title(news_items, mode="tech-blog")

    topics = _extract_key_topics(news_items)
    base_tags = ["Tech-Blog", "Weekly-Digest", "Developer", str(date.year)]
    topic_tags = [t for t in topics if t not in base_tags]
    tags = base_tags + topic_tags[:5]

    # GeekNews items for prominent display
    geeknews_items = [item for item in news_items if item.get("source") == "geeknews"]

    top_sources = list(
        {item.get("source_name", ""): True for item in news_items[:5]}.keys()
    )[:3]
    source_list = ", ".join(top_sources)

    # Build highlights from top items
    highlights = []
    for item in news_items[:4]:
        source = html.escape(item.get("source_name", item.get("source", "Unknown")))
        title = _korean_display_title(item)
        if len(title) > 60:
            title = title[:60].rsplit(" ", 1)[0].rstrip(" ,.")
        title = html.escape(title)
        highlights.append(f"<li><strong>{source}</strong>: {title}</li>")

    highlights_html = (
        "\n      ".join(highlights)
        if highlights
        else "<li>이번 주 주요 기술 뉴스를 확인하세요</li>"
    )

    # Generate Jekyll include tag for AI summary card - dynamic tags from actual content
    categories_html = '<span class="category-tag tech">기술</span> <span class="category-tag devops">DevOps</span>'
    # Build tags from actual topics
    dynamic_tags = ["Tech-Blog"]
    for topic in topics[:4]:
        if topic not in dynamic_tags:
            dynamic_tags.append(topic)
    dynamic_tags.append(str(date.year))
    tags_html = "\n      ".join(
        f'<span class="tag">{t}</span>' for t in dynamic_tags[:6]
    )

    # Escape quotes in title before Liquid injection (same guard as security template)
    safe_title = _html_escape_quotes(title_keywords)

    content = f'''---
layout: post
title: "기술 블로그 주간 다이제스트: {title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [tech, devops]
tags: [{", ".join(tags)}]
excerpt: "{_build_clean_excerpt(title_keywords, date_str, total, "tech", topics)}"
description: "{_build_clean_description(title_keywords, source_list, date_str, total, "tech")}"
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "{_build_clean_image_alt(title_keywords, "tech")}"
toc: true
---

{{% include ai-summary-card.html
  title="기술 블로그 주간 다이제스트: {safe_title}"
  categories_html='{categories_html}'
  tags_html='{tags_html}'
  highlights_html='{highlights_html}'
  period='{date_str} (24시간)'
  audience='소프트웨어 개발자, DevOps 엔지니어, 테크 리드, CTO'
%}}

---

{_generate_executive_and_risk_sections(news_items, mode="tech-blog")}
## 서론

안녕하세요, **Twodragon**입니다.

{date_str} 기준, 주요 기술 블로그와 커뮤니티에서 발표된 개발자 뉴스를 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: {total}개
- **AI/ML**: {len(topic_groups["AI/ML"])}개
- **DevOps/Cloud**: {len(topic_groups["DevOps/Cloud"])}개
- **Open Source**: {len(topic_groups["Open Source"])}개
- **General**: {len(topic_groups["General"])}개

---

'''

    section_num = 1

    # GeekNews 하이라이트 (Korean summaries prominently displayed)
    if geeknews_items:
        content += f"## {section_num}. GeekNews 하이라이트\n\n"
        content += "GeekNews에서 주목받은 기술 뉴스입니다.\n\n"
        for item in geeknews_items[:5]:
            title = _korean_display_title(item)
            url = item.get("url", "")
            source_name = item.get("source_name", "GeekNews")
            ko_summary = _korean_brief_summary(item)

            content += f"### {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략
        section_num += 1

    # AI/ML 섹션
    if topic_groups["AI/ML"]:
        content += f"## {section_num}. AI/ML 트렌드\n\n"
        for i, item in enumerate(topic_groups["AI/ML"][:5], 1):
            title = _korean_display_title(item)
            url = item.get("url", "")
            source = item.get("source_name", item.get("source", "Unknown"))
            ko_summary = _korean_brief_summary(item)

            content += f"### {section_num}.{i} {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략

            # Key points
            key_points = _generate_key_points(item)
            if key_points:
                content += "**핵심 포인트:**\n\n"
                content += key_points + "\n"
        section_num += 1

    # DevOps/Cloud 섹션
    if topic_groups["DevOps/Cloud"]:
        content += f"## {section_num}. DevOps & Cloud\n\n"
        for i, item in enumerate(topic_groups["DevOps/Cloud"][:5], 1):
            title = _korean_display_title(item)
            url = item.get("url", "")
            source = item.get("source_name", item.get("source", "Unknown"))
            ko_summary = _korean_brief_summary(item)

            content += f"### {section_num}.{i} {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략
        section_num += 1

    # Open Source 섹션
    if topic_groups["Open Source"]:
        content += f"## {section_num}. Open Source\n\n"
        for i, item in enumerate(topic_groups["Open Source"][:5], 1):
            title = _korean_display_title(item)
            url = item.get("url", "")
            source = item.get("source_name", item.get("source", "Unknown"))
            ko_summary = _korean_brief_summary(item)

            content += f"### {section_num}.{i} {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략
        section_num += 1

    # General 섹션
    if topic_groups["General"]:
        content += f"## {section_num}. 기타 주목할 뉴스\n\n"
        content += "| 제목 | 출처 | 핵심 내용 |\n"
        content += "|------|------|----------|\n"
        for item in topic_groups["General"][:5]:
            title = _korean_display_title(item, max_len=50)
            source = item.get("source_name", "")
            url = item.get("url", "")
            ko_summary = _table_summary(_korean_brief_summary(item).replace("\n", " "))
            content += f"| [{title}]({url}) | {source} | {ko_summary} |\n"
        content += "\n"
        section_num += 1

    # 트렌드 분석
    content += _generate_tech_trend_analysis(news_items, section_num)
    content += _generate_news_specific_checklist(news_items)

    content += """---

**작성자**: Twodragon
"""

    return content


def _generate_tech_trend_analysis(news_items: List[Dict], section_num: int) -> str:
    """기술 블로그 트렌드 분석 섹션 생성"""
    content = f"\n---\n\n## {section_num}. 트렌드 분석\n\n"

    trend_defs = {
        "AI/LLM": [
            "ai",
            "llm",
            "gpt",
            "claude",
            "gemini",
            "machine learning",
            "인공지능",
            "생성형",
        ],
        "클라우드 네이티브": ["cloud", "aws", "azure", "gcp", "serverless", "클라우드"],
        "컨테이너/K8s": ["kubernetes", "k8s", "container", "docker", "컨테이너"],
        "개발 도구": [
            "ide",
            "editor",
            "cli",
            "developer experience",
            "dx",
            "cursor",
            "copilot",
        ],
        "오픈소스": ["open source", "open-source", "oss", "github", "cncf"],
        "프로그래밍 언어": [
            "rust",
            "golang",
            "typescript",
            "python",
            "java",
            "swift",
        ],
        "플랫폼 엔지니어링": [
            "platform",
            "internal developer",
            "golden path",
            "backstage",
        ],
    }

    trend_results = []
    matched_indices: set[int] = set()
    for trend_name, keywords in trend_defs.items():
        count = 0
        matched_kws = set()
        for idx, item in enumerate(news_items):
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for kw in keywords:
                if kw in text:
                    count += 1
                    matched_kws.add(kw)
                    matched_indices.add(idx)
                    break
        if count > 0:
            trend_results.append((trend_name, count, ", ".join(list(matched_kws)[:3])))

    # Add "기타" for unmatched items so trend sum == total
    etc_count = len(news_items) - len(matched_indices)
    if etc_count > 0:
        trend_results.append(("기타", etc_count, "기타 주제"))

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws in trend_results:
            content += f"| **{name}** | {count}건 | {kws} |\n"
        content += "\n"

        top = trend_results[0]
        content += (
            f"이번 주기에서 가장 많이 언급된 트렌드는 **{top[0]}** ({top[1]}건)입니다. "
        )
        if len(trend_results) > 1:
            second = trend_results[1]
            content += (
                f"그 다음으로 **{second[0]}** ({second[1]}건)이 주목받고 있습니다. "
            )
        content += (
            "관련 기술 동향을 파악하고 팀 내 기술 공유에 활용하시기 바랍니다.\n\n"
        )
    else:
        content += "이번 주기에는 두드러진 트렌드가 감지되지 않았습니다.\n\n"

    return content


def _determine_severity(item: Dict) -> str:
    """뉴스 심각도 결정 - news_utils.determine_severity 위임."""
    try:
        from news_utils import determine_severity
    except ImportError:
        from scripts.news_utils import determine_severity

    text = (
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
    )
    category = item.get("category", "tech")
    return determine_severity(text, category)


def _extract_cve_ids(item: Dict) -> List[str]:
    """뉴스 아이템에서 모든 CVE ID 추출"""
    text = (
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
    )
    cves = re.findall(r"CVE-\d{4}-\d+", text)
    # 중복 제거하면서 순서 유지
    seen = set()
    unique = []
    for cve in cves:
        if cve not in seen:
            seen.add(cve)
            unique.append(cve)
    return unique


def _generate_key_points(item: Dict) -> str:
    """뉴스 아이템에서 핵심 포인트 추출"""
    summary = _korean_brief_summary(item)
    if not summary:
        return ""

    # 문장 단위로 분리하여 핵심 포인트 생성
    sentences = re.split(r"(?<=[.!?。다])\s+", summary)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if not sentences:
        return ""

    points = ""
    for s in sentences[:4]:
        # 마침표 제거 후 포인트로
        s = s.rstrip(".")
        points += f"- {s}\n"
    return points


def _pick_variant(item: Dict, variants: List[str]) -> str:
    """Deterministically select one variant based on article identity.

    Keeps the same article stable across regenerations while diversifying
    output across different articles that share the same keyword branch.
    """
    if not variants:
        return ""
    if len(variants) == 1:
        return variants[0]
    key = f"{item.get('title', '')}|{item.get('url', '')}".encode("utf-8", "ignore")
    digest = hashlib.md5(key).digest()
    idx = int.from_bytes(digest[:4], "big") % len(variants)
    return variants[idx]


def _generate_contextual_action_point(item: Dict) -> str:
    """Generate a context-aware action point based on actual article content.

    Extracts keywords from the title/summary to produce specific advice
    instead of generic category-based text. For high-traffic keywords,
    rotates among multiple variants per article to prevent copy-paste feel
    across weekly digests.
    """
    title = (item.get("title", "") or "").lower()
    summary = (item.get("summary", "") or "").lower()
    combined = f"{title} {summary}"
    category = item.get("category", "tech")

    # Security-specific contextual hints
    if category in ("security", "devsecops"):
        if any(kw in combined for kw in ["patch", "update", "패치", "업데이트"]):
            return _pick_variant(item, [
                "영향받는 시스템 버전을 확인하고 패치 적용 일정을 수립하세요.",
                "CVSS와 KEV 포함 여부를 검토한 뒤 유지보수 창과 롤백 플랜을 준비하세요.",
                "패치 전/후 설정 드리프트를 비교하고 핫픽스 검증 환경부터 단계적 배포하세요.",
            ])
        if any(kw in combined for kw in ["ransomware", "랜섬웨어"]):
            return _pick_variant(item, [
                "백업 상태 확인, 네트워크 세그먼테이션 점검, 이메일 필터링 강화를 권장합니다.",
                "복구 리허설을 오프라인 백업 기준으로 수행하고 횡적 이동 차단 정책을 재검증하세요.",
                "SMB/RDP 노출 면을 축소하고 섀도 카피·비볼륨 암호화 방어 설정을 재확인하세요.",
            ])
        if any(kw in combined for kw in ["phishing", "피싱", "credential", "자격증명"]):
            return _pick_variant(item, [
                "MFA 적용 현황 점검 및 사용자 보안 인식 교육을 강화하세요.",
                "FIDO2/패스키 기반 피싱 저항 인증으로의 마이그레이션 경로를 수립하세요.",
                "조건부 액세스 정책과 비정상 토큰 발급 탐지 룰을 재조정하세요.",
            ])
        if any(kw in combined for kw in ["supply chain", "공급망", "dependency"]):
            return _pick_variant(item, [
                "서드파티 의존성 감사(SCA)를 수행하고 SBOM을 최신 상태로 유지하세요.",
                "빌드 재현성 확인과 아티팩트 서명 검증(cosign)을 파이프라인에 강제하세요.",
                "종속성 업데이트 정책을 pin-and-verify 기반으로 전환하고 의심 릴리스를 격리하세요.",
            ])
        if any(kw in combined for kw in ["data breach", "유출", "leak"]):
            return _pick_variant(item, [
                "영향 범위 파악, 인시던트 대응 절차 발동, 규제 기관 통보 여부를 확인하세요.",
                "노출된 식별자 유형별로 재인증·토큰 회전을 우선순위화하고 법무팀과 통보 시점을 합의하세요.",
                "침해 경로 타임라인을 포렌식으로 재구성해 재발 방지 통제와 감사 로그 보존을 강화하세요.",
            ])
        if any(kw in combined for kw in ["malware", "악성코드", "trojan", "backdoor"]):
            return _pick_variant(item, [
                "EDR/SIEM에서 IoC 기반 탐지 룰을 업데이트하세요.",
                "관련 해시/도메인/뮤텍스를 위협 인텔리전스 피드에 반영하고 헌팅 쿼리를 작성하세요.",
                "의심 바이너리의 부모 프로세스·서명 체인을 점검하고 자동 격리 정책을 확인하세요.",
            ])
        if re.search(r"cve-\d{4}-\d+", combined):
            return _pick_variant(item, [
                "해당 CVE의 영향 범위와 CVSS 점수를 확인 후 패치 우선순위를 결정하세요.",
                "CVE 공개 후 KEV/EPSS 지표를 교차 확인하고 노출 자산 기준 패치 SLA를 재산정하세요.",
                "CVE 익스플로잇 PoC 공개 여부를 모니터링하면서 핫픽스 적용과 탐지 룰 추가를 병행하세요.",
            ])
        return "보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요."

    # AI category
    if category == "ai":
        if any(kw in combined for kw in ["agent", "에이전트", "agentic"]):
            return _pick_variant(item, [
                "AI Agent 도입 시 권한 범위 설정과 출력 검증 체계를 사전에 수립하세요.",
                "AI Agent의 도구 호출 권한을 최소화하고 의심 행동에 대한 Human-in-the-Loop 승인 경로를 구성하세요.",
                "Agent 실행 로그와 프롬프트 히스토리를 감사 로그로 축적하고 권한 escalation 탐지 룰을 추가하세요.",
            ])
        if any(
            kw in combined
            for kw in [
                "coding",
                "코딩",
                "copilot",
                "cursor",
                "코드 생성",
                "code generation",
            ]
        ):
            return _pick_variant(item, [
                "AI 생성 코드에 대한 보안 스캔(SAST/SCA) 게이트를 CI/CD에 필수 적용하세요.",
                "AI 코딩 도구가 생성한 변경분의 보안 스캔 결과를 리뷰 체크리스트에 포함하세요.",
                "Copilot/Cursor 등 AI 코딩 어시스턴트 사용 로그를 수집해 SAST 탐지 패턴과 상관 분석하세요.",
            ])
        if any(kw in combined for kw in ["llm", "gpt", "claude", "gemini"]):
            return _pick_variant(item, [
                "LLM 서빙 환경의 접근 제어와 프롬프트 인젝션 방어 체계를 점검하세요.",
                "LLM 응답의 민감 데이터 리덕션 레이어와 프롬프트 필터링 규칙을 정기적으로 감사하세요.",
                "LLM 업그레이드 시 프롬프트 회귀 테스트와 비용/지연 트레이드오프 모니터링을 동시에 수행하세요.",
            ])
        if any(
            kw in combined for kw in ["gpu", "nvidia", "compute", "training", "factory"]
        ):
            return _pick_variant(item, [
                "AI 인프라 도입 시 보안 경계 설계와 데이터 프라이버시 규정 준수를 확인하세요.",
                "GPU 공유 환경에서는 테넌트 격리 경계와 학습 데이터 저장소 접근 제어를 재점검하세요.",
                "AI 인프라 도입 시 모델 가중치 유출 방지 통제와 네트워크 이탈 방지 정책을 병행 점검하세요.",
            ])
        if any(
            kw in combined
            for kw in ["open source", "오픈소스", "hugging face", "ollama"]
        ):
            return _pick_variant(item, [
                "오픈소스 모델 도입 시 출처 검증, 라이선스 및 학습 데이터 리스크를 평가하세요.",
                "오픈소스 모델 체크포인트의 해시 검증과 공식 배포 채널 이외 경로 차단 정책을 수립하세요.",
                "Hugging Face 등 오픈소스 허브 다운로드 출처를 화이트리스트로 관리하고 라이선스 감사 프로세스를 정례화하세요.",
            ])
        if any(kw in combined for kw in ["model", "모델"]):
            return _pick_variant(item, [
                "자사 AI 워크로드에 적용 가능성과 비용/성능 트레이드오프를 평가하세요.",
                "신규 LLM 모델의 자사 워크로드 적합성을 응답 품질·비용·지연 3축 트레이드오프로 비교하세요.",
                "모델 변경 시 프롬프트 호환성 회귀와 추론 비용 단가 변동을 동시에 측정하세요.",
            ])
        return "AI/ML 파이프라인 및 서비스에 미치는 영향을 검토하세요."

    # Cloud / DevOps
    if category in ("cloud", "devops", "kubernetes"):
        if any(kw in combined for kw in ["rbac", "iam", "권한", "identity"]):
            return _pick_variant(item, [
                "IAM/RBAC 정책의 최소 권한 원칙 준수와 서비스 계정 감사를 수행하세요.",
                "IAM/RBAC 바인딩의 최소 권한 여부와 휴면 서비스 계정 정리 주기를 재검토하세요.",
                "IAM/RBAC 정책 변경 이력을 감사 로그 기반으로 리뷰하고 최소 권한 드리프트를 자동 탐지하세요.",
            ])
        if any(kw in combined for kw in ["kubernetes", "k8s", "쿠버네티스"]):
            return _pick_variant(item, [
                "클러스터 버전 호환성과 워크로드 영향을 확인하세요.",
                "클러스터 업그레이드 시 Admission Controller·네트워크 폴리시 호환성을 사전 검증하세요.",
                "클러스터 노드별 리소스/보안 컨텍스트 드리프트를 주기적으로 스캔하세요.",
            ])
        if any(kw in combined for kw in ["docker", "container", "컨테이너"]):
            return _pick_variant(item, [
                "컨테이너 이미지 업데이트 및 런타임 보안 설정을 점검하세요.",
                "컨테이너 베이스 이미지의 CVE 스캔과 최소 권한 런타임 옵션을 재확인하세요.",
                "컨테이너 빌드 파이프라인에서 서명(cosign) 검증 단계를 필수화하세요.",
            ])
        if any(kw in combined for kw in ["terraform", "iac", "인프라 코드"]):
            return _pick_variant(item, [
                "IaC 템플릿 보안 스캔(Checkov/tfsec)과 드리프트 탐지를 확인하세요.",
                "IaC 변경분에 대한 Checkov/tfsec 정적 분석을 PR 게이트로 강제하세요.",
                "IaC 상태 파일 접근 통제와 원격 백엔드 암호화 설정을 재점검하세요.",
            ])
        if any(
            kw in combined for kw in ["serverless", "lambda", "서버리스", "function"]
        ):
            return _pick_variant(item, [
                "서버리스 함수의 IAM 역할 최소화와 실행 환경 보안 설정을 점검하세요.",
                "서버리스 함수의 환경 변수 민감 정보 저장을 KMS/Secrets Manager로 이관하세요.",
                "서버리스 콜드 스타트 로그와 IAM 권한 남용 이상 징후 탐지 룰을 추가하세요.",
            ])
        if any(kw in combined for kw in ["aws", "azure", "gcp"]):
            return _pick_variant(item, [
                "클라우드 서비스 변경사항이 인프라 구성에 미치는 영향을 확인하세요.",
                "클라우드 서비스 업데이트에 따른 네트워크/보안 기본값 변경 여부를 릴리스 노트로 추적하세요.",
                "클라우드 인프라 구성 드리프트를 CSPM으로 지속 모니터링하고 규제 매핑을 갱신하세요.",
            ])
        return "인프라 및 운영 환경 영향을 검토하세요."

    # Blockchain
    if category == "blockchain":
        if any(
            kw in combined
            for kw in [
                "hack",
                "exploit",
                "attack",
                "공격",
                "breach",
                "침해",
                "vulnerability",
            ]
        ):
            return _pick_variant(item, [
                "블록체인 보안 사고 관련 IoC를 확인하고 유사 공격 벡터에 대한 방어 체계를 점검하세요.",
                "해킹 발표 후 공개된 IoC와 지갑 주소를 위협 인텔에 반영하고 유사 서비스의 방어 설정을 재검증하세요.",
                "사고 원인 분석 리포트가 공개되면 IoC·패턴을 추출해 자사 스마트 컨트랙트 방어 룰에 적용하세요.",
            ])
        if any(
            kw in combined
            for kw in [
                "regulation",
                "규제",
                "법안",
                "act",
                "compliance",
                "컴플라이언스",
                "sec",
                "cftc",
            ]
        ):
            return _pick_variant(item, [
                "규제 변화에 따른 컴플라이언스 영향을 법무팀과 사전 검토하세요.",
                "규제 발표 내용을 법무 및 컴플라이언스 조직과 공유하고 영향 받는 서비스 흐름을 도식화하세요.",
                "규제 시행 일정에 맞춰 KYC/AML 통제와 컴플라이언스 보고 프로세스를 업데이트하세요.",
            ])
        if any(
            kw in combined
            for kw in [
                "defi",
                "protocol",
                "프로토콜",
                "swap",
                "스왑",
                "lending",
                "대출",
            ]
        ):
            return _pick_variant(item, [
                "관련 DeFi 프로토콜의 스마트 컨트랙트 감사 현황과 비상 정지 메커니즘을 확인하세요.",
                "해당 DeFi 프로토콜의 스마트 컨트랙트 감사 리포트와 타임락·멀티시그 구성을 재점검하세요.",
                "연동 중인 DeFi 서비스의 스마트 컨트랙트 업그레이드 패턴과 긴급 정지 거버넌스를 검토하세요.",
            ])
        if any(
            kw in combined
            for kw in ["conference", "컨퍼런스", "summit", "speaker", "연사"]
        ):
            return _pick_variant(item, [
                "대규모 행사 전후로 관련 토큰 사기 및 가짜 이벤트 피싱이 증가합니다. 공식 채널만 이용하세요.",
                "컨퍼런스 시즌 피싱 도메인과 가짜 연사 에어드롭 사기 패턴을 모니터링하고 공식 채널 공지를 사내에 배포하세요.",
                "대형 행사 기간에는 관련 키워드 기반 피싱이 증가하므로 공식 채널 링크만 사내 승인하도록 커뮤니케이션하세요.",
            ])
        if any(kw in combined for kw in ["bitcoin", "비트코인", "btc"]):
            return _pick_variant(item, [
                "시장 변동성 확대 시기에 피싱 도메인 모니터링을 강화하고 고액 출금 인증 절차를 점검하세요.",
                "하드웨어 지갑 키 관리와 출금 서명 흐름을 재점검해 조작된 트랜잭션 승인 리스크를 차단하세요.",
                "거래소 API 키 권한을 읽기 전용 기준으로 최소화하고 출금 화이트리스트를 의무화하세요.",
            ])
        if any(
            kw in combined
            for kw in ["ethereum", "이더리움", "eth", "stablecoin", "스테이블코인"]
        ):
            return _pick_variant(item, [
                "스마트 컨트랙트 기반 서비스의 접근 제어와 트랜잭션 모니터링을 점검하세요.",
                "이더리움 기반 서비스의 승인(approve) 오남용 탐지와 트랜잭션 모니터링 룰을 강화하세요.",
                "스테이블코인 결제/브릿지의 접근 제어와 대규모 트랜잭션 모니터링 임계치를 재설정하세요.",
            ])
        return "관련 프로토콜 및 스마트 컨트랙트 영향을 확인하세요."

    return "실무 적용 전에 상세 내용을 확인하세요."


def _translate_to_korean_deepseek(
    text: str, context: str = "기술 뉴스", mode: str = "summary"
) -> str:
    """DeepSeek API를 활용한 한국어 번역 폴백

    Args:
        text: 번역할 영어 텍스트
        context: 번역 컨텍스트 (예: "기술 뉴스 제목", "보안 뉴스 요약")
        mode: "title" (제목 번역) 또는 "summary" (요약 번역)

    Returns:
        한국어 번역 텍스트 (실패 시 빈 문자열)
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or not text:
        return ""

    try:
        import requests

        if mode == "title":
            prompt = (
                f"다음 {context} 제목을 한국어로 자연스럽게 번역해 주세요. "
                "고유명사(회사명/제품명)는 원문 표기를 유지하세요. "
                "답변은 번역된 제목 한 줄만 출력하세요. "
                "따옴표, 번호, 불릿, 설명은 포함하지 마세요.\n\n"
                f"원문: {text}\n번역:"
            )
        else:
            prompt = (
                f"다음 {context}를 한국어 2~3문장으로 간결하게 요약해 주세요. "
                "기술 용어와 고유명사는 원문 표기를 유지하세요. "
                "마크다운, 불릿, 번호 없이 순수 문장만 출력하세요.\n\n"
                f"원문: {text[:1000]}\n요약:"
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300,
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )

        if response.status_code == 200:
            result = response.json()
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            translated = re.sub(r"\s+", " ", content.strip()).strip("\"'")
            if translated and re.search(r"[가-힣]", translated):
                logging.info(f"DeepSeek translated ({mode}): {text[:40]}...")
                return translated
        else:
            logging.warning(f"DeepSeek translate API status {response.status_code}")
    except ImportError:
        logging.debug("requests library not available for DeepSeek translation")
    except Exception as e:
        logging.warning(f"DeepSeek translate error: {e}")

    return ""


def _korean_display_title(item: Dict, max_len: int = 72) -> str:
    raw_title = (item.get("title", "") or "").strip()
    if not raw_title:
        return "제목 없음"

    if re.search(r"[가-힣]", raw_title):
        return raw_title

    cache_key = item.get("id") or item.get("url") or raw_title
    if cache_key in KOREAN_TITLE_CACHE:
        return KOREAN_TITLE_CACHE[cache_key]

    translated = ""
    if check_gemini_available():
        prompt = (
            "다음 기술 뉴스 제목을 한국어 한 줄로 번역. "
            "고유명사는 원문 유지. 따옴표/번호/설명 금지.\n"
            f"원문: {raw_title}\n번역:"
        )
        candidate = _gemini_call(prompt, timeout=15)
        if candidate:
            candidate = re.sub(r"\s+", " ", candidate).strip("\"'")
            if re.search(r"[가-힣]", candidate):
                translated = candidate

    if translated:
        KOREAN_TITLE_CACHE[cache_key] = translated
        return translated

    # Gemini 실패 시: DeepSeek API 폴백
    category = item.get("category", "tech")
    if _allow_deepseek():
        deepseek_translated = _translate_to_korean_deepseek(
            raw_title, context=f"{category} 뉴스", mode="title"
        )
        if deepseek_translated:
            KOREAN_TITLE_CACHE[cache_key] = deepseek_translated
            return deepseek_translated

    if raw_title:
        # AI 번역 실패 시: 실제 RSS 제목을 그대로 사용 (일반적 토픽 구문 대신)
        # CVE가 포함된 경우만 한국어 레이블 추가
        cve_match = re.search(r"CVE-\d{4}-\d+", raw_title, re.IGNORECASE)
        category_label = {
            "security": "보안",
            "devsecops": "DevSecOps",
            "ai": "AI",
            "cloud": "클라우드",
            "devops": "DevOps",
            "blockchain": "블록체인",
            "kubernetes": "쿠버네티스",
            "tech": "기술",
        }.get(category, "기술")

        if cve_match:
            display_title = (
                f"[{category_label}] {cve_match.group(0).upper()} 취약점 보안 업데이트"
            )
        else:
            # 실제 영문 제목을 그대로 사용하여 구체성 유지
            display_title = raw_title

        if len(display_title) > max_len:
            display_title = _smart_truncate_korean(display_title, max_len=max_len)

        KOREAN_TITLE_CACHE[cache_key] = display_title
        return display_title
    source_name = (
        item.get("source_name", "") or item.get("source", "해외 기술 매체")
    ).strip()
    if not source_name:
        source_name = "해외 기술 매체"
    fallback = f"{source_name} 기술 업데이트"
    KOREAN_TITLE_CACHE[cache_key] = fallback
    return fallback


def _korean_brief_summary(item: Dict, max_sentences: int = 2) -> str:
    summary = (item.get("summary", "") or "").strip()
    content_text = (item.get("content", "") or "").strip()
    text = summary or content_text
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"URL:\s*https?://\S+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"https?://\S+", "", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    selected = sentences[:max_sentences] if sentences else [text[:220]]

    cache_key = item.get("id") or item.get("url") or item.get("title") or text[:80]
    if cache_key in KOREAN_SUMMARY_CACHE:
        return KOREAN_SUMMARY_CACHE[cache_key]

    has_korean = bool(re.search(r"[가-힣]", text))
    if has_korean:
        needs_refine = len(text) > 220 or "URL:" in summary or "http" in summary
        if needs_refine and check_gemini_available():
            prompt = (
                "다음 기술 뉴스를 한국어 2문장 요약. URL/불릿/번호 금지.\n"
                f"제목: {item.get('title', '')}\n본문: {text[:600]}\n요약:"
            )
            generated = _gemini_call(prompt, timeout=15)
            if generated:
                generated = re.sub(r"\s+", " ", generated)
                generated = generated.replace("...", " ").replace("…", " ").strip(" .")
                if len(generated) >= 25:
                    KOREAN_SUMMARY_CACHE[cache_key] = generated
                    return generated

        concise = " ".join(selected).replace("...", " ").replace("…", " ").strip(" .")
        if len(concise) > 220:
            concise = _truncate_korean_sentence(concise, 220)
        KOREAN_SUMMARY_CACHE[cache_key] = concise
        return concise

    if check_gemini_available():
        prompt = (
            "다음 기술 뉴스를 한국어 2문장으로 요약. 마크다운/불릿 금지.\n"
            f"제목: {item.get('title', '')}\n요약: {text[:500]}\n응답:"
        )
        generated = _gemini_call(prompt, timeout=15)
        if generated:
            generated = re.sub(r"\s+", " ", generated)
            if len(generated) >= 30 and re.search(r"[가-힣]", generated):
                KOREAN_SUMMARY_CACHE[cache_key] = generated
                return generated

    # Gemini 실패 시: DeepSeek API 폴백으로 한국어 번역
    raw_summary = (item.get("summary", "") or "").strip()
    raw_content = (item.get("content", "") or "").strip()
    raw_text = raw_summary or raw_content

    if raw_text:
        category = item.get("category", "tech")
        title_text = item.get("title", "")
        translate_input = f"제목: {title_text}\n내용: {raw_text[:800]}"

        if _allow_deepseek():
            deepseek_translated = _translate_to_korean_deepseek(
                translate_input,
                context=f"{category} 뉴스 요약",
                mode="summary",
            )
            if deepseek_translated:
                # Use translated content directly; contextual action points are
                # added by generate_news_section() to avoid duplication
                KOREAN_SUMMARY_CACHE[cache_key] = deepseek_translated
                return deepseek_translated

        # AI 번역 실패 시: 실제 RSS 요약 텍스트를 정리하여 사용
        # 일반적 템플릿 문구 대신 원본 콘텐츠의 구체성을 유지
        source_name = item.get("source_name", item.get("source", ""))

        # HTML 태그 제거 및 정리
        clean_text = re.sub(r"<[^>]+>", "", raw_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # 첫 2~3문장 추출 (최대 300자)
        sentences = re.split(r"(?<=[.!?。])\s+", clean_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        summary_text = " ".join(sentences[:3])
        if len(summary_text) > 300:
            summary_text = _truncate_korean_sentence(summary_text, 300)

        action = _generate_contextual_action_point(item)
        if summary_text:
            result = f"{summary_text} {action}"
        else:
            title_ko = _korean_display_title(item)
            result = f"{title_ko}. {action}"

        KOREAN_SUMMARY_CACHE[cache_key] = result
        return result

    # No raw_text at all - use title-based fallback
    category = item.get("category", "tech")
    title_ko = _korean_display_title(item)
    source_name = item.get("source_name", item.get("source", ""))
    fallback = f"{title_ko} ({source_name}). 상세 내용은 출처 링크를 참조하세요."
    KOREAN_SUMMARY_CACHE[cache_key] = fallback
    return fallback


def generate_news_section(
    item: Dict, section_num: str, is_critical: bool = False
) -> str:
    """개별 뉴스 섹션 생성 - 고품질 분석 포함"""
    # fmt: off
    _CURLY_QUOTES = {"\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'"}
    # fmt: on

    def _sanitize_liquid_param(text: str) -> str:
        """Liquid include 파라미터용 문자열 정리 - curly quotes, 이중 따옴표 이스케이프"""
        for curly, straight in _CURLY_QUOTES.items():
            text = text.replace(curly, straight)
        return text.replace('"', '\\"')

    title = _korean_display_title(item)
    url = item.get("url", "")
    source = item.get("source_name", item.get("source", "Unknown"))
    content_text = item.get("content", "")
    category = item.get("category", "tech")

    severity = _determine_severity(item)
    cve_ids = _extract_cve_ids(item)
    image = item.get("image", "")
    ko_summary = _korean_brief_summary(item)

    section = f"### {section_num} {title}\n\n"

    # 뉴스 카드 (이미지 + 요약)
    if image or ko_summary:
        card_parts = [
            "{% include news-card.html",
            '  title="%s"' % _sanitize_liquid_param(title),
            '  url="%s"' % _sanitize_liquid_param(url),
        ]
        if image:
            # Strip query params that break Jekyll include parser
            clean_image = image.split("?")[0] if "?" in image else image
            card_parts.append('  image="%s"' % _sanitize_liquid_param(clean_image))
        if ko_summary:
            card_summary = _sanitize_liquid_param(ko_summary[:200])
            card_parts.append('  summary="%s"' % card_summary)
        card_parts.append('  source="%s"' % _sanitize_liquid_param(source))
        card_parts.append('  severity="%s"' % severity)
        card_parts.append("%}")
        section += "\n".join(card_parts) + "\n\n"

    # 심각도 및 CVE 뱃지
    if cve_ids or severity == "Critical":
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(
            severity, "🟡"
        )
        section += f"> {severity_emoji} **심각도**: {severity}"
        if cve_ids:
            section += f" | **CVE**: {', '.join(cve_ids[:5])}"
        section += "\n\n"

    # AI 강화 시도 (Critical/High 보안 뉴스만) - 3단계 폴백 체인 사용
    if is_critical and category in ("security", "devsecops"):
        enhanced = enhance_content_with_fallback(item)
        if enhanced:
            section += enhanced + "\n\n"

            # CVE가 있으면 MITRE 매핑 추가
            if cve_ids:
                section += generate_mitre_mapping(cve_ids[0], item)

            section += "\n---\n\n"
            return section

    # 폴백: 기존 템플릿
    section += "#### 요약\n\n"
    if ko_summary:
        section += f"{ko_summary}\n\n"
    elif content_text:
        section += f"{content_text[:800]}...\n\n"

    # Context-aware action point (skip if summary already contains 실무 포인트)
    if "실무 포인트" not in (ko_summary or ""):
        action_point = _generate_contextual_action_point(item)
        if action_point:
            section += f"**실무 포인트**: {action_point}\n\n"

    # 출처는 news-card에 포함되므로 별도 blockquote 생략

    # 핵심 포인트 - only if content differs from summary
    key_points = _generate_key_points(item)
    if key_points:
        # Check if key points are substantially different from summary
        ko_summary_stripped = (ko_summary or "").replace(" ", "").replace("\n", "")
        key_points_stripped = (
            key_points.replace("- ", "").replace(" ", "").replace("\n", "")
        )
        # Only show if less than 70% overlap
        if ko_summary_stripped and key_points_stripped:
            overlap = sum(
                1 for c in key_points_stripped[:100] if c in ko_summary_stripped[:200]
            )
            similarity = overlap / max(len(key_points_stripped[:100]), 1)
            if similarity < 0.7:
                section += "#### 핵심 포인트\n\n"
                section += key_points + "\n"

    # 카테고리별 상세 분석 템플릿
    if category in ("security", "devsecops") and is_critical:
        section += _generate_security_analysis_template(item)
    elif category in ("security", "devsecops"):
        section += _generate_security_brief_template(item)
    elif category == "ai":
        section += _generate_ai_analysis_template(item)
    elif category in ("cloud", "devops", "kubernetes"):
        section += _generate_devops_template(item)

    section += "\n---\n\n"
    return section


def _table_summary(text: str, max_len: int = 200) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    cleaned = cleaned.replace("...", " ").replace("…", " ").strip(" .")
    if len(cleaned) <= max_len:
        return cleaned
    return _truncate_korean_sentence(cleaned, max_len)


def _truncate_korean_sentence(text: str, max_len: int) -> str:
    """Truncate text at a Korean sentence boundary, ensuring proper ending."""
    if len(text) <= max_len:
        return text
    clipped = text[:max_len]
    # Find the latest sentence boundary (prefer more text over separator type)
    best_idx, best_len = -1, 0
    for sep in [
        "습니다.",
        "니다.",
        "했습니다.",
        "됩니다.",
        "입니다.",
        "다.",
        "됨.",
        "임.",
    ]:
        idx = clipped.rfind(sep)
        if idx > max_len * 0.4 and idx > best_idx:
            best_idx, best_len = idx, len(sep)
    if best_idx > 0:
        return clipped[: best_idx + best_len]
    # Word boundary fallback
    clipped = clipped.rsplit(" ", 1)[0].rstrip(" ,.·:;")
    if re.search(r"[가-힣]", clipped):
        clipped = re.sub(
            r"\s+(에|의|을|를|이|가|은|는|와|과|로|으로|에서|한|된|인|할)$", "", clipped
        )
        if not re.search(r"[.다됨임]$", clipped):
            clipped += " 등이 확인되었습니다."
    return clipped


def _generate_security_analysis_template(item: Dict) -> str:
    """보안 뉴스 상세 분석 템플릿 - 실제 데이터 기반"""
    cve_ids = _extract_cve_ids(item)
    severity = _determine_severity(item)
    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()

    # 대응 우선순위 결정
    priority = "P0 - 즉시 대응" if severity == "Critical" else "P1 - 7일 이내 검토 권장"

    template = "\n#### 위협 분석\n\n"
    template += "| 항목 | 내용 |\n"
    template += "|------|------|\n"

    if cve_ids:
        template += f"| **CVE ID** | {', '.join(cve_ids[:5])} |\n"
    else:
        template += "| **CVE ID** | 미공개 또는 해당 없음 |\n"

    template += f"| **심각도** | {severity} |\n"
    template += f"| **대응 우선순위** | {priority} |\n"
    template += "\n"

    # SIEM 탐지 힌트 (취약점 유형 기반)
    siem_hints = []
    mitre_techniques = []

    if "rce" in text or "remote code execution" in text:
        siem_hints.append(
            '```splunk\nindex=security sourcetype=syslog ("exploit" OR "remote code execution" OR "shell")\n| stats count by src_ip, dest_ip, action\n| where count > 3\n```'
        )
        mitre_techniques.append("T1203 (Exploitation for Client Execution)")
    if "authentication" in text or "인증" in text or "auth bypass" in text:
        siem_hints.append(
            '```splunk\nindex=security sourcetype=auth ("bypass" OR "unauthorized" OR "failed_login")\n| stats count by user, src_ip\n| where count > 10\n```'
        )
        mitre_techniques.append("T1078 (Valid Accounts)")
    if "injection" in text or "sql" in text or "xss" in text:
        siem_hints.append(
            '```splunk\nindex=web sourcetype=access_combined (SELECT OR UNION OR script OR "\\x" OR "%27")\n| stats count by uri, src_ip\n| where count > 5\n```'
        )
        mitre_techniques.append("T1190 (Exploit Public-Facing Application)")
    if "supply chain" in text or "공급망" in text:
        mitre_techniques.append("T1195 (Supply Chain Compromise)")
    if "zero-day" in text or "제로데이" in text or "0-day" in text:
        mitre_techniques.append("T1068 (Exploitation for Privilege Escalation)")
    if "privilege" in text or "권한 상승" in text:
        mitre_techniques.append("T1068 (Exploitation for Privilege Escalation)")

    if siem_hints:
        template += "#### SIEM 탐지 쿼리 (참고용)\n\n"
        template += siem_hints[0] + "\n\n"

    if mitre_techniques:
        template += "#### MITRE ATT&CK 매핑\n\n"
        for tech in mitre_techniques[:3]:
            template += f"- **{tech}**\n"
        template += "\n"

    template += """#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화

"""
    return template


def _generate_security_brief_template(item: Optional[Dict] = None) -> str:
    """보안 뉴스 간략 분석 템플릿 - 토픽별 맞춤 조언 제공"""
    if item is None:
        return """
#### 권장 조치

- 관련 시스템 목록 확인
- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다

"""

    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()

    # Ransomware-related advice
    if any(kw in text for kw in ["ransomware", "랜섬웨어", "ransom", "encrypt"]):
        return """
#### 권장 조치

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인

"""

    # Authentication-related advice
    if any(
        kw in text
        for kw in [
            "authentication",
            "인증",
            "credential",
            "password",
            "mfa",
            "sso",
            "auth bypass",
            "인증 우회",
            "login",
        ]
    ):
        return """
#### 권장 조치

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사

"""

    # Supply chain-related advice
    if any(
        kw in text
        for kw in [
            "supply chain",
            "공급망",
            "dependency",
            "package",
            "npm",
            "pypi",
            "maven",
            "sbom",
        ]
    ):
        return """
#### 권장 조치

- 의존성 감사(dependency audit) 즉시 실행: `npm audit`, `pip audit`, `bundle audit`
- SBOM(Software Bill of Materials) 최신 상태 확인
- 서드파티 라이브러리 버전 고정 및 무결성 검증(checksum/signature)
- CI/CD 파이프라인의 의존성 스캔 정책 점검

"""

    # Zero-day / exploit advice
    if any(
        kw in text
        for kw in ["zero-day", "제로데이", "0-day", "exploit", "actively exploited"]
    ):
        return """
#### 권장 조치

- 영향받는 소프트웨어/버전 인벤토리 즉시 확인 및 패치 적용
- 패치 불가 시 WAF 규칙 추가 또는 취약 서비스 네트워크 격리
- CISA KEV 카탈로그 등재 여부 확인 및 패치 SLA 적용
- EDR/NDR에서 관련 공격 패턴 탐지 룰 활성화

"""

    # Phishing / social engineering advice
    if any(
        kw in text
        for kw in [
            "phishing",
            "피싱",
            "social engineering",
            "사회공학",
            "vishing",
            "smishing",
        ]
    ):
        return """
#### 권장 조치

- 직원 대상 피싱 인식 교육 및 시뮬레이션 테스트 실시
- 이메일 보안 게이트웨이(SEG) 필터링 정책 업데이트
- 피싱 신고 채널 점검 및 의심 이메일 자동 격리 설정
- DMARC/SPF/DKIM 설정 상태 확인 및 정책 강화

"""

    # Data breach / leak advice
    if any(
        kw in text
        for kw in ["data breach", "데이터 유출", "leak", "유출", "exposed", "노출"]
    ):
        return """
#### 권장 조치

- 유출 범위 파악: 영향받는 데이터 유형, 건수, 시스템 식별
- 관련 계정 비밀번호 즉시 로테이션 및 세션 무효화
- 개인정보 유출 시 관할 기관 신고 의무 타임라인 확인
- DLP 정책 점검 및 민감 데이터 접근 로그 감사

"""

    # Default: improved generic
    return """
#### 권장 조치

- 관련 시스템 목록 확인 및 자사 환경 해당 여부 평가
- 벤더 보안 권고 확인 후 패치 또는 완화 조치 적용
- SIEM/EDR 탐지 룰에 관련 IoC 추가
- 보안팀 내 공유 및 모니터링 강화

"""


def _generate_ai_analysis_template(item: Dict) -> str:
    """AI/ML 관련 뉴스 분석 템플릿"""
    title = item.get("title", "")
    summary = item.get("summary", "")

    text = f"{title} {summary}".lower()

    template = "\n#### 실무 적용 포인트\n\n"
    if any(kw in text for kw in ["agent", "에이전트", "agentic"]):
        template += _pick_variant(item, [
            "- AI 에이전트 도구 호출 권한 및 접근 범위 최소화 설계\n"
            "- 에이전트 행동 로깅 및 감사 파이프라인 구축 검토\n"
            "- 에이전트 출력에 대한 검증 및 사람 감독(Human-in-the-Loop) 설계\n",
            "- 에이전트 작업 범위를 최소 권한 원칙으로 제한하고 도구 호출 권한 화이트리스트 관리\n"
            "- Human-in-the-Loop 승인 게이트를 고위험 에이전트 액션에 필수 적용\n"
            "- 에이전트 실행 로그를 SIEM에 연동해 비정상 패턴 실시간 탐지\n",
            "- 멀티 에이전트 파이프라인에서 도구 호출 권한 격리 및 샌드박스 경계 설계\n"
            "- 에이전트 오케스트레이션 레이어에 Human-in-the-Loop 검증 체크포인트 삽입\n"
            "- 에이전트 출력 스키마 검증으로 프롬프트 인젝션 경유 데이터 유출 차단\n",
        ])
    elif any(kw in text for kw in ["llm", "gpt", "claude", "gemini", "model"]):
        template += _pick_variant(item, [
            "- LLM 입출력 데이터 보안 및 프라이버시 검토\n"
            "- 모델 서빙 환경의 접근 제어 및 네트워크 격리 확인\n"
            "- 프롬프트 인젝션 등 적대적 공격 대응 방안 점검\n",
            "- LLM 입출력 로그를 DLP 정책으로 필터링해 민감 데이터 노출 방지\n"
            "- 프롬프트 인젝션 방어를 위한 입력 정규화·출력 검증 레이어 추가\n"
            "- 모델 API 키를 시크릿 매니저에 통합하고 최소 권한 서비스 계정으로 교체\n",
            "- LLM 서빙 엔드포인트에 레이트 리미팅과 인증 토큰 로테이션 정책 적용\n"
            "- 프롬프트 인젝션 시도를 SIEM 규칙으로 탐지하고 자동 차단 임계 설정\n"
            "- 모델 응답의 PII·시크릿 포함 여부를 LLM 입출력 감사 파이프라인으로 검증\n",
        ])
    elif any(
        kw in text
        for kw in ["gpu", "nvidia", "인프라", "factory", "compute", "training"]
    ):
        template += _pick_variant(item, [
            "- 대규모 AI 인프라 도입 시 보안 경계 및 접근 제어 설계 검토\n"
            "- GPU 클러스터 운영 환경의 취약점 관리 및 패치 정책 수립\n"
            "- AI 워크로드 데이터 프라이버시 규정(GDPR, HIPAA) 준수 확인\n",
            "- GPU 클러스터 노드별 접근 제어와 네트워크 분리로 횡적 이동 경로 차단\n"
            "- AI 인프라 드라이버·펌웨어 패치 주기를 취약점 SLA에 포함해 추적\n"
            "- 학습 데이터셋의 PII 처리 방침과 데이터 레지던시 요구사항 재검토\n",
            "- AI 인프라 접근 제어를 IAM 역할 기반으로 재설계해 공유 자격증명 제거\n"
            "- GPU 클러스터 상태 모니터링에 보안 이벤트(비인가 접근·이상 부하) 연계\n"
            "- 학습·추론 환경의 네트워크 분리 현황과 VPC 피어링 정책 검토\n",
        ])
    elif any(
        kw in text
        for kw in ["simulation", "시뮬레이션", "digital twin", "optimize", "최적화"]
    ):
        template += _pick_variant(item, [
            "- 시뮬레이션 기반 인프라 검증으로 배포 전 보안 취약점 사전 식별 활용\n"
            "- AI 서비스 성능 최적화와 보안 모니터링 균형 설계\n"
            "- 운영 비용 절감 효과와 보안 투자 ROI 분석\n",
            "- 시뮬레이션 환경을 카오스 엔지니어링에 활용해 보안 통제 회복력 검증\n"
            "- 최적화 파이프라인에 보안 정책 드리프트 탐지 단계 포함\n"
            "- 시뮬레이션 결과 기반 ROI 모델에 보안 사고 비용 항목 반영\n",
            "- 디지털 트윈·시뮬레이션 데이터 접근 권한을 역할별로 분리해 유출 위험 저감\n"
            "- 최적화 알고리즘이 민감 운영 데이터를 훈련에 사용할 때의 동의·익명화 정책 확인\n"
            "- 시뮬레이션 ROI 지표에 보안 투자 절감 효과(MTTD/MTTR 개선)를 포함\n",
        ])
    elif any(
        kw in text
        for kw in [
            "coding",
            "코딩",
            "copilot",
            "cursor",
            "code generation",
            "코드 생성",
            "devtool",
            "ide",
            "vscode",
        ]
    ):
        template += _pick_variant(item, [
            "- AI 코딩 도구가 생성한 코드에 대한 자동 보안 스캔(SAST/SCA) 게이트 필수 적용\n"
            "- AI 생성 코드의 시크릿/자격증명 하드코딩 여부 자동 탐지 설정\n"
            "- 개발자 대상 AI 코딩 도구 보안 사용 가이드라인 수립 및 교육\n",
            "- AI 코딩 어시스턴트 제안 코드에 SAST 파이프라인 필수 통과 정책 적용\n"
            "- 코드 생성 결과의 시크릿·API 키 노출을 pre-commit 훅으로 자동 차단\n"
            "- AI 생성 코드 리뷰 체크리스트에 입력 검증·SQL 인젝션·XSS 항목 포함\n",
            "- IDE 플러그인 접근 권한을 최소화하고 벤더 데이터 전송 정책 재검토\n"
            "- AI 코딩 도구 사용 로그를 감사 파이프라인에 연계해 민감 코드 노출 추적\n"
            "- 코드 생성 품질 게이트에 SAST 보안 스캔 결과를 병합 차단 조건으로 설정\n",
        ])
    elif any(
        kw in text for kw in ["attack", "공격", "threat", "위협", "malware", "악성"]
    ):
        template += _pick_variant(item, [
            "- AI 기반 위협 탐지 및 자동 대응 파이프라인 구축 검토\n"
            "- AI 모델 자체의 적대적 공격(Adversarial Attack) 방어 설계\n"
            "- 보안 팀의 AI 도구 활용 역량 강화 교육 계획 수립\n",
            "- 위협 탐지 모델에 최신 공격 패턴(TTPs) 피드를 연동해 탐지율 향상\n"
            "- Adversarial Attack 방어를 위한 모델 입력 정규화·이상치 필터링 레이어 적용\n"
            "- AI 기반 위협 인텔리전스 플랫폼 도입 효과를 MTTD 지표로 정기 검증\n",
            "- AI 위협 탐지 파이프라인의 false positive 임계를 재조정해 운영 피로 감소\n"
            "- Adversarial Attack 시나리오를 레드팀 훈련에 포함해 방어 체계 실전 검증\n"
            "- 위협 탐지 결과를 SOAR 플레이북과 연동해 자동 격리·알림 흐름 구성\n",
        ])
    elif any(
        kw in text
        for kw in [
            "open source",
            "오픈소스",
            "hugging face",
            "허깅페이스",
            "올라마",
            "ollama",
        ]
    ):
        template += _pick_variant(item, [
            "- 오픈소스 AI 모델 도입 시 라이선스 및 보안 취약점 검토\n"
            "- 모델 다운로드 출처 검증 및 체크섬/서명 확인 절차 수립\n"
            "- 오픈소스 모델의 학습 데이터 편향 및 프라이버시 리스크 평가\n",
            "- 오픈소스 모델 레지스트리 접근을 내부 미러로 제한해 공급망 위험 축소\n"
            "- 모델 다운로드 시 해시 검증과 서명 확인을 CI 파이프라인에 자동화\n"
            "- 오픈소스 라이선스 의무(GPL·AGPL)가 프로덕션 서비스에 미치는 영향 법무 검토\n",
            "- HuggingFace·Ollama 모델의 CVE 이력을 SCA 도구로 스캔 후 배포 승인\n"
            "- 오픈소스 모델 학습 데이터 출처와 PII 포함 여부를 모델 카드로 문서화\n"
            "- 커뮤니티 기여 코드에 대한 내부 보안 리뷰 게이트 수립 및 주기적 감사\n",
        ])
    else:
        logging.info(
            f"AI template fallback triggered for: {item.get('title', '')[:60]}"
        )
        template += _pick_generic_ai_bullets(item)

    template += "\n"
    return _contextualize_practical_points(template, item)


# AI/ML fallback bullet pools — parallel to the DevOps fallback pools.
_AI_FALLBACK_POOLS: List[List[str]] = [
    [
        "- AI/ML 기술 도입 시 데이터 파이프라인 보안 및 접근 제어 검토",
        "- 모델 학습/추론 환경의 네트워크 격리 및 인증 체계 확인",
        "- 관련 기술의 자사 환경 적용 가능성 평가 및 보안 영향 분석",
    ],
    [
        "- 벤더 AI 서비스의 데이터 처리 약관·데이터 레지던시 요구사항 재검토",
        "- 실험(research) 모델이 프로덕션 데이터에 접근할 때의 격리 경계 명문화",
        "- 모델 업데이트 주기·회귀 테스트 셋을 MLOps 파이프라인에 기본값으로 포함",
    ],
    [
        "- 학습 데이터셋의 PII·라이선스 출처 감사 자동화로 재배포 리스크 제거",
        "- 모델 카드·시스템 카드에 알려진 실패 모드와 완화 전략 문서화",
        "- 평가(eval) 지표에 안전성(safety)·편향(bias) 항목을 명시적으로 포함",
    ],
    [
        "- 멀티 모델 라우팅에서 민감 쿼리는 특정 리전·벤더로 고정하는 정책 설정",
        "- 프롬프트·시스템 메시지를 시크릿으로 분류해 버전 관리·감사 로그에 연계",
        "- 사용량 상위 10% 프롬프트에 대한 red-team 리뷰를 주기적으로 실시",
    ],
    [
        "- RAG 인덱스의 컬렉션·네임스페이스 단위 접근 제어와 테넌트 분리 검증",
        "- 벡터 DB의 임베딩 유사도 기반 정보 누출(membership inference) 위험 모델링",
        "- AI 응답에 인용 출처를 포함하도록 강제해 hallucination 추적성을 확보",
    ],
]


def _pick_generic_ai_bullets(item: Optional[Dict]) -> str:
    """Deterministic fallback bullet picker for AI template."""
    if item is None:
        return "\n".join(_AI_FALLBACK_POOLS[0]) + "\n"
    seed = item.get("url") or item.get("title", "") or ""
    if not seed:
        return "\n".join(_AI_FALLBACK_POOLS[0]) + "\n"
    bucket = sum(ord(c) for c in seed) % len(_AI_FALLBACK_POOLS)
    return "\n".join(_AI_FALLBACK_POOLS[bucket]) + "\n"


# Per-item unique bullet templates — appended as a 4th practical-point bullet
# so that news items in the same keyword bucket still receive at least one
# distinctive, title-specific action item instead of three identical lines.
_UNIQUE_ITEM_BULLET_TEMPLATES: List[str] = [
    "- 본 사안({topic}) 관련 자사 환경 영향도 평가 및 담당 팀 에스컬레이션 경로 확인",
    "- {topic} 이슈의 공개 IoC·지표를 SIEM/보안 이벤트 룰에 반영하고 탐지 검증",
    "- {topic} 관련 내부 시스템 노출 여부 스캔 및 변경 이력 감사 로그 점검",
    "- {topic} 사례를 내부 런북·체크리스트에 기록해 유사 상황 대응 시간 단축",
    "- {topic}의 기술·비즈니스 영향 범위를 표로 정리해 분기 리스크 리뷰에 포함",
    "- {topic} 관련 서드파티·SaaS 의존성 맵 갱신 및 벤더 커뮤니케이션 로그 남기기",
    "- {topic} 관련 테스트 케이스를 스테이징 환경에서 재현해 패치·완화 조치 검증",
    "- {topic} 이슈 대응 경과를 보안 인시던트 보고서 템플릿에 맞춰 정리·공유",
]


def _item_hash_seed(item: Optional[Dict]) -> str:
    """Return a deterministic seed string for variant selection.

    Prefers URL (unique per article) and falls back to title. Empty when both
    are missing so callers can short-circuit.
    """
    if not item:
        return ""
    return item.get("url") or item.get("title", "") or ""


def _extract_primary_news_keyword(item: Optional[Dict]) -> str:
    """Extract a short distinctive topic phrase from the news title.

    Reuses ``_korean_display_title`` for consistent Korean-first normalization
    but allows a longer phrase than the first-bullet label so the uniqueness
    bullet differs from the ``[label]`` prefix.
    """
    if not item:
        return ""
    display = _korean_display_title(item, max_len=48)
    if not display:
        return ""
    phrase = re.split(r"\s*[|:,]+\s*|\s+-\s+", display)[0].strip(" ,.·")
    return _smart_truncate_korean(phrase, 24)


def _build_unique_practical_bullet(item: Optional[Dict]) -> Optional[str]:
    """Build an item-specific bullet line appended after the branch bullets.

    Uses a deterministic hash of the item URL/title so the same news produces
    the same bullet every run, while two items in the same keyword branch
    pick different variants (and embed their own topic phrase).
    """
    seed = _item_hash_seed(item)
    if not seed:
        return None
    topic = _extract_primary_news_keyword(item)
    if not topic:
        return None
    variant_idx = sum(ord(c) for c in seed) % len(_UNIQUE_ITEM_BULLET_TEMPLATES)
    return _UNIQUE_ITEM_BULLET_TEMPLATES[variant_idx].format(topic=topic)


def _contextualize_practical_points(template: str, item: Optional[Dict]) -> str:
    """Diversify practical-point bullets so each news item has unique content.

    Two passes:
    1. Stamp the first bullet with a short ``[label]`` topic prefix.
    2. Append an item-hash-selected 4th bullet embedding a distinctive topic
       phrase extracted from the title. This guarantees that two items sharing
       the same keyword branch (e.g. both matched "docker") still receive at
       least one bullet that references their specific story.
    """
    if not item or "#### 실무 적용 포인트" not in template:
        return template

    lines = template.splitlines()

    raw_label = _korean_display_title(item, max_len=36)
    label = re.split(r"\s*[|:]+\s*|\s+-\s+", raw_label)[0].strip(" ,.")
    label = _smart_truncate_korean(label, 18)
    if label:
        for index, line in enumerate(lines):
            if line.startswith("- "):
                lines[index] = f"- [{label}] {line[2:]}"
                break

    unique_bullet = _build_unique_practical_bullet(item)
    if unique_bullet:
        last_bullet_idx = -1
        for index, line in enumerate(lines):
            if line.startswith("- "):
                last_bullet_idx = index
        if last_bullet_idx >= 0:
            lines.insert(last_bullet_idx + 1, unique_bullet)

    if not label and not unique_bullet:
        return template
    return "\n".join(lines).rstrip() + "\n"


def _generate_devops_template(item: Optional[Dict] = None) -> str:
    if item is None:
        return """
#### 실무 적용 포인트

- 운영 환경 변경 시 보안 구성 검증 자동화 파이프라인 점검
- 인프라 코드(IaC) 보안 스캔 도구 통합 및 정책 업데이트
- 변경 관리 프로세스에 보안 검토 단계 포함 확인

"""

    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    template = "\n#### 실무 적용 포인트\n\n"

    if any(kw in text for kw in ["docker", "container", "컨테이너"]):
        template += _pick_variant(item, [
            "- 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
            "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
            "- 컨테이너 런타임 보안 모니터링 강화\n",
            "- 컨테이너 이미지 보안 스캔을 CI 게이트에 연동해 취약 레이어 빌드 차단\n"
            "- Docker 소켓 마운트 여부 감사 및 컨테이너 탈출 위험 경로 점검\n"
            "- non-root 사용자 강제 및 읽기 전용 파일시스템 런타임 정책 적용\n",
            "- 컨테이너 이미지 보안 스캔과 서명·무결성 검증을 레지스트리 푸시 단계에 자동화\n"
            "- 컨테이너 런타임(containerd/runc) 최신 보안 패치 적용 현황 점검\n"
            "- 컨테이너 네트워크 격리 정책과 Seccomp/AppArmor 프로파일 적용 여부 확인\n",
        ])
    elif any(
        kw in text
        for kw in [
            "rbac",
            "admission controller",
            "pod security",
            "psa",
            "psp",
            "opa",
            "gatekeeper",
        ]
    ):
        template += _pick_variant(item, [
            "- Kubernetes RBAC 역할 및 바인딩 최소 권한 원칙 준수 감사\n"
            "- Admission Controller/OPA 정책으로 비인가 리소스 생성 차단\n"
            "- Pod Security Admission(PSA) restricted 프로필 적용 현황 점검\n",
            "- RBAC ClusterRole 권한 범위를 네임스페이스 단위로 축소하고 미사용 바인딩 제거\n"
            "- OPA/Gatekeeper Constraint 위반 현황을 대시보드로 시각화해 정책 공백 탐지\n"
            "- PSA restricted 프로파일 마이그레이션 현황과 예외 처리 목록 주기적 감사\n",
            "- Admission Controller 웹훅 TLS 인증서 만료 주기 관리 및 자동 갱신 설정\n"
            "- RBAC 감사 로그를 SIEM에 연동해 권한 상승 시도 실시간 탐지\n"
            "- OPA 정책 변경을 GitOps 흐름으로 관리해 무단 정책 수정 방지\n",
        ])
    elif any(
        kw in text
        for kw in [
            "image",
            "이미지",
            "registry",
            "레지스트리",
            "cosign",
            "sigstore",
            "sbom",
        ]
    ):
        template += _pick_variant(item, [
            "- 컨테이너 이미지 서명(cosign/sigstore) 및 무결성 검증 파이프라인 확인\n"
            "- 프라이빗 레지스트리 접근 제어 및 이미지 스캔 정책 점검\n"
            "- SBOM 기반 이미지 의존성 취약점 추적 자동화 설정\n",
            "- cosign 서명 정책을 Admission Controller에 연동해 미서명 이미지 배포 차단\n"
            "- 레지스트리 접근 토큰 로테이션 주기를 단축하고 서비스 계정 권한 최소화\n"
            "- SBOM을 CI 산출물로 생성·저장하고 신규 CVE 발생 시 자동 알림 연계\n",
            "- sigstore Rekor 투명성 로그로 이미지 서명 이력 감사 자동화\n"
            "- 이미지 레지스트리 취약점 스캔 결과를 SBOM과 결합해 영향 범위 신속 파악\n"
            "- 베이스 이미지 업데이트 트리거를 Dependabot·Renovate로 자동화해 패치 지연 방지\n",
        ])
    elif any(kw in text for kw in ["서비스 메시", "service mesh", "istio", "envoy"]):
        template += _pick_variant(item, [
            "- mTLS 기반 서비스 간 통신 암호화 적용 검토\n"
            "- 서비스 메시 관측성 활용한 이상 트래픽 탐지 설계\n"
            "- 네트워크 폴리시와 서비스 메시 정책 통합 관리\n",
            "- Istio AuthorizationPolicy로 서비스 간 최소 권한 통신 규칙 적용\n"
            "- 서비스 메시 텔레메트리(Kiali/Jaeger)로 동서 트래픽 이상 패턴 실시간 탐지\n"
            "- mTLS STRICT 모드 전환 현황을 네임스페이스별로 점검하고 로드맵 수립\n",
            "- Envoy 사이드카 프록시 버전 드리프트를 정기 스캔해 패치 공백 제거\n"
            "- 서비스 메시 정책을 GitOps로 관리해 무단 변경 감사 추적\n"
            "- mTLS 인증서 만료 모니터링을 알림 파이프라인에 연계해 서비스 중단 예방\n",
        ])
    elif any(
        kw in text
        for kw in ["network policy", "네트워크 폴리시", "ingress", "egress", "cilium"]
    ):
        template += _pick_variant(item, [
            "- Kubernetes NetworkPolicy로 Pod 간 불필요한 통신 차단 설정\n"
            "- Ingress/Egress 트래픽 암호화(mTLS) 적용 현황 검토\n"
            "- 네트워크 관측성 도구(Cilium Hubble 등)로 이상 트래픽 탐지 강화\n",
            "- NetworkPolicy 기본 거부(default-deny) 정책을 모든 네임스페이스에 적용\n"
            "- Cilium Hubble 플로우 로그를 SIEM에 연동해 비인가 Egress 탐지\n"
            "- Ingress 컨트롤러 WAF 규칙을 최신 OWASP Top 10 기준으로 업데이트\n",
            "- 클러스터 외부 Egress IP를 고정하고 방화벽 화이트리스트로 통신 범위 제한\n"
            "- NetworkPolicy 변경 이력을 GitOps 파이프라인으로 추적해 무단 수정 방지\n"
            "- Cilium 네트워크 정책과 서비스 메시 정책 간 충돌 여부 정기 검증\n",
        ])
    elif any(
        kw in text for kw in ["kubecon", "conference", "컨퍼런스", "행사", "summit"]
    ):
        template += _pick_variant(item, [
            "- 컨퍼런스에서 발표된 새로운 보안 프레임워크 및 도구 검토\n"
            "- 커뮤니티 모범 사례의 자사 환경 적용 가능성 평가\n"
            "- 발표된 오픈소스 프로젝트의 보안 성숙도 및 도입 로드맵 검토\n",
            "- 컨퍼런스 발표 내용을 내부 기술 공유 세션으로 전파하고 적용 우선순위 결정\n"
            "- 발표된 신규 CNCF 프로젝트의 보안 감사 결과와 프로덕션 준비도 평가\n"
            "- 커뮤니티 CVE 발표 세션에서 자사 환경 영향 항목을 즉시 식별해 조치\n",
            "- 행사 발표 자료를 팀 위키에 정리하고 도입 검토 이슈 트래커에 연결\n"
            "- 오픈소스 프로젝트 도입 전 보안 성숙도 평가 체크리스트(SLSA·OpenSSF Scorecard) 적용\n"
            "- 컨퍼런스에서 공개된 취약점 정보를 패치 SLA 프로세스에 즉시 반영\n",
        ])
    elif any(kw in text for kw in ["kubernetes", "k8s", "kcd", "cncf"]):
        template += _pick_variant(item, [
            "- Kubernetes 클러스터 보안 벤치마크(CIS) 준수 점검\n"
            "- API 서버 접근 제어 및 감사 로그(Audit Log) 활성화 확인\n"
            "- 클러스터 업그레이드 주기 및 보안 패치 적용 현황 검토\n",
            "- kube-bench 도구로 CIS Kubernetes 벤치마크 준수 현황을 정기 스캔\n"
            "- API 서버 감사 로그 정책을 세분화해 민감 리소스 접근을 SIEM에 연동\n"
            "- EoL 버전 클러스터 업그레이드 일정과 취약점 익스플로잇 위험을 연계 관리\n",
            "- CNCF 프로젝트 도입 시 OpenSSF Scorecard 점수와 보안 감사 이력 확인\n"
            "- Kubernetes API 서버 익명 접근 비활성화 및 ServiceAccount 자동 마운트 제한\n"
            "- CIS 벤치마크 미준수 항목을 OPA 정책으로 자동 탐지·리포트하는 파이프라인 구축\n",
        ])
    elif any(
        kw in text for kw in ["ci/cd", "pipeline", "github action", "jenkins", "배포"]
    ):
        template += _pick_variant(item, [
            "- CI/CD 파이프라인 보안 강화: 시크릿 관리, 토큰 권한 최소화\n"
            "- 서드파티 Actions/플러그인의 출처 검증 및 버전 고정\n"
            "- 빌드/배포 로그 모니터링으로 비정상 행위 탐지\n",
            "- CI/CD 파이프라인 시크릿을 외부 시크릿 매니저로 이전하고 런타임 주입으로 전환\n"
            "- GitHub Actions 워크플로우에 쓰기 권한 범위를 필요한 단계에만 한정\n"
            "- 빌드 산출물 서명·무결성 검증을 배포 승인 게이트에 포함\n",
            "- 서드파티 Actions를 SHA 고정 버전으로 참조하고 Dependabot으로 자동 업데이트\n"
            "- CI/CD 파이프라인 실행 로그를 SIEM에 연동해 비인가 시크릿 접근 탐지\n"
            "- 스테이징과 프로덕션 배포 승인을 별도 보호된 환경 변수로 분리 관리\n",
        ])
    elif any(
        kw in text
        for kw in [
            "database",
            "데이터베이스",
            "db",
            "sql",
            "cache",
            "캐시",
            "redis",
            "valkey",
            "memorystore",
        ]
    ):
        template += _pick_variant(item, [
            "- 데이터베이스/캐시 서비스 업그레이드 시 데이터 무결성 검증 및 접근 제어 점검\n"
            "- DB 연결 암호화(SSL/TLS) 설정이 모든 복제본/노드에 적용되는지 확인\n"
            "- 자동 확장 이벤트 감사 로그 모니터링으로 비정상 리소스 증가 탐지\n",
            "- 데이터베이스 계정 권한을 최소화하고 애플리케이션별 전용 서비스 계정으로 분리 운영\n"
            "- 쿼리 실행 계획 분석으로 SQL 인젝션 취약 패턴과 성능 병목을 동시에 점검\n"
            "- 캐시(Redis·Valkey) 외부 노출 여부를 확인하고 AUTH·TLS 설정 일관성 검토\n",
            "- 데이터베이스 스냅샷·백업 복원 테스트를 정기 실행해 RTO/RPO 목표 달성 여부 검증\n"
            "- DB 감사 로그(DDL·DML)를 SIEM에 연동해 비인가 스키마 변경 실시간 탐지\n"
            "- 캐시 계층 데이터 만료 정책과 민감 정보 저장 여부를 보안 요구사항과 일치시키기\n",
        ])
    elif any(
        kw in text
        for kw in [
            "mobile",
            "모바일",
            "maui",
            "flutter",
            "react native",
            "ios",
            "android app",
        ]
    ):
        template += _pick_variant(item, [
            "- 모바일 앱 업데이트에 포함된 보안 패치 및 의존성 변경사항 검토\n"
            "- API 키 및 민감 데이터의 클라이언트 측 노출 방지 설정 점검\n"
            "- 사용자 데이터 수집 시 개인정보 보호 정책(GDPR, 개인정보보호법) 준수 확인\n",
            "- 모바일 앱 네이티브 브리지 권한 범위를 최소화해 앱 샌드박스 우회 위험 감소\n"
            "- 클라이언트 바이너리에 하드코딩된 API 키·시크릿을 정적 분석 도구로 자동 탐지\n"
            "- 모바일 앱 배포 전 OWASP MASVS L1 체크리스트로 인증·암호화·데이터 저장 항목 검증\n",
            "- 모바일 클라이언트 인증서 피닝 설정으로 중간자 공격(MITM) 위험을 런타임에 차단\n"
            "- 사용자 단말 OS 버전·루팅 탐지 로직을 정기 업데이트해 최신 우회 기법 대응\n"
            "- 모바일 앱 내 개인정보 처리 목적·보존 기간을 코드 주석과 개인정보처리방침에 동기화\n",
        ])
    elif any(kw in text for kw in ["네트워크", "network"]):
        template += _pick_variant(item, [
            "- 네트워크 세그멘테이션 및 방화벽 규칙 최신화 점검\n"
            "- 비정상 트래픽 패턴 탐지를 위한 모니터링 강화\n"
            "- 네트워크 접근 제어 정책(Zero Trust) 적용 현황 검토\n",
            "- 동서(East-West) 트래픽에도 마이크로 세그멘테이션 정책을 적용해 내부 이동 경로 차단\n"
            "- NDR 솔루션에서 DNS 터널링·이상 포트 스캔 알림 임계값을 최신 위협 수준으로 재보정\n"
            "- VPN·SD-WAN 어플라이언스의 펌웨어 패치 현황과 관리 포털 MFA 적용 여부 확인\n",
            "- 제로 트러스트 전환 로드맵에 미반영 레거시 VLAN 구간을 식별하고 마이그레이션 우선순위 지정\n"
            "- 방화벽 정책 리뷰 주기를 분기 1회로 고정하고 미사용 허용 규칙 자동 탐지 도구 연동\n"
            "- 네트워크 플로우 데이터를 SIEM에 수집해 DGA 도메인·C2 통신 패턴 상관 분석\n",
        ])
    elif any(
        kw in text
        for kw in ["copilot", "github blog", "github action", "changelog", "코파일럿"]
    ):
        template += _pick_variant(item, [
            "- Copilot/Actions 플랜·쿼터 변경이 내부 파이프라인에 미치는 영향 회귀 테스트\n"
            "- 에이전트 응답 로그를 SIEM에 연동해 민감 코드/시크릿 노출 사례 감사\n"
            "- 팀별 Copilot 사용량 지표(AAU, MAU, 토큰)를 라이선스 리포트에 통합\n",
            "- GitHub Actions 워크플로우 권한을 최소화하고 제3자 Action은 SHA 고정 버전으로 참조\n"
            "- Copilot 제안 코드에 SAST 게이트를 의무화해 시크릿 하드코딩·인젝션 취약점 자동 차단\n"
            "- 변경 로그(changelog) 릴리스 노트에서 보안 관련 항목을 파싱해 내부 패치 SLA에 반영\n",
            "- GitHub Advanced Security(GHAS) 코드 스캔 결과를 PR 머지 차단 조건으로 설정\n"
            "- Copilot Business 정책에서 공개 코드 제안 수락 여부를 조직 정책으로 통일 관리\n"
            "- Actions 실행 로그 보존 기간을 감사 요구사항(90일 이상)에 맞게 재설정\n",
        ])
    elif any(
        kw in text
        for kw in ["metric", "observability", "dashboard", "대시보드", "메트릭", "로그"]
    ):
        template += _pick_variant(item, [
            "- 메트릭·로그 스키마 변경 시 기존 Grafana/Looker 대시보드 호환성 회귀 확인\n"
            "- 신규 지표(AAU·MAU 등)를 SLO·SLA 보고서에 통합해 정책 공백 감지\n"
            "- 관측성 데이터의 보존 기간과 접근 제어(RBAC)를 거버넌스 정책과 일치시키기\n",
            "- OpenTelemetry 트레이스에 사용자 ID·세션 토큰이 포함되지 않도록 데이터 마스킹 설정\n"
            "- 경보(Alert) 임계값과 on-call 정책을 분기마다 재검토해 알림 피로(alert fatigue) 감소\n"
            "- 로그 집계 파이프라인의 접근 제어를 최소 권한으로 재설정하고 감사 추적 활성화\n",
            "- 분산 추적(Distributed Tracing) 데이터에서 PII 노출 여부를 자동 스캔하는 규칙 수립\n"
            "- 관측성 플랫폼(Grafana/Datadog) 대시보드 접근 권한을 역할 기반으로 재구성\n"
            "- SLO 오류 예산 소진 속도를 보안 인시던트 지표와 상관 분석해 리스크 조기 감지\n",
        ])
    elif any(
        kw in text
        for kw in ["serverless", "lambda", "cloud run", "cloud functions", "function"]
    ):
        template += _pick_variant(item, [
            "- 서버리스 워크로드 실행 역할(IAM)의 최소 권한·일시성 로그 감사 정책 점검\n"
            "- Cold start·burst 스케일 시 비밀값 주입 지연과 cache-poisoning 위험 평가\n"
            "- 이벤트 소스(버킷·큐·스케줄러)별 invoke 권한과 VPC 경계 분리 검증\n",
            "- Lambda/Cloud Run 함수에 환경 변수 대신 런타임 시크릿 매니저 주입 방식 적용\n"
            "- 함수 실행 타임아웃과 메모리 상한을 설정해 DoS 남용 시 비용 폭증 방지\n"
            "- 서버리스 이벤트 트리거(S3·Pub/Sub·SQS)의 입력 스키마 검증으로 인젝션 차단\n",
            "- 서버리스 함수의 의존성 패키지를 정기 갱신하고 CVE 스캔을 배포 파이프라인에 통합\n"
            "- VPC 커넥터 경유 내부 리소스 접근 시 Security Group 규칙을 함수 단위로 최소화\n"
            "- 함수 호출 로그와 X-Ray·Cloud Trace를 SIEM에 연동해 비인가 invoke 탐지\n",
        ])
    elif any(
        kw in text
        for kw in [
            "gpu",
            "cuda",
            "nccl",
            "training",
            "학습 인프라",
            "infiniband",
            "nvlink",
        ]
    ):
        template += _pick_variant(item, [
            "- GPU 드라이버·CUDA·NCCL 버전 고정 및 헬스체크 훅으로 단일 장애 노드 자동 격리\n"
            "- 토폴로지 인식 스케줄링(Kueue/Ray)으로 NVLink/InfiniBand 장애 도메인 분리\n"
            "- 분산 체크포인트 RPO 기준 설계 및 복구 시간 테스트 자동화\n",
            "- GPU 노드 접근을 전용 서비스 계정으로 제한하고 SSH 키 대신 임시 자격증명 발급\n"
            "- CUDA 커널 취약점(CVE) 발생 시 드라이버 롤백 절차를 Runbook으로 문서화\n"
            "- 분산 학습 데이터셋의 PII 포함 여부를 파이프라인 진입 단계에서 자동 검사\n",
            "- InfiniBand/NVLink 네트워크 트래픽에 암호화 정책 적용 가능성과 성능 영향 평가\n"
            "- GPU 클러스터 사용량 대시보드에 비인가 job 제출 탐지 경보 규칙 추가\n"
            "- 체크포인트 저장소의 접근 제어(버킷 ACL·IAM)를 학습 완료 후 즉시 최소화\n",
        ])
    elif any(
        kw in text
        for kw in [
            "trial",
            "체험판",
            "abuse",
            "남용",
            "rate limit",
            "레이트 리미트",
            "quota",
            "쿼터",
        ]
    ):
        template += _pick_variant(item, [
            "- 가입·세션 생성 엔드포인트의 IP·디바이스 지문 기반 중복 탐지 룰과 CAPTCHA 단계 강화\n"
            "- 체험판 API에 별도 quota 버킷을 할당하고 burst·cumulative 임계 기반 실시간 알림 구성\n"
            "- 남용 패턴(봇 가입, 카드 재사용, 일회용 이메일)을 Risk Engine에 공급해 자동 차단·수동 리뷰 분리\n",
            "- 레이트 리미팅 정책을 사용자 티어별로 세분화하고 한도 초과 시 graceful degradation 응답 반환\n"
            "- 일회용 이메일·VPN IP 차단 목록을 외부 위협 인텔리전스 피드와 자동 동기화\n"
            "- 쿼터 소진 패턴을 ML 이상 탐지 모델에 학습시켜 정상 급증과 남용 사례를 자동 분류\n",
            "- 체험판 계정의 API 키 유효기간을 72시간으로 제한하고 만료 후 자동 폐기 처리\n"
            "- 남용 신고 접수 채널과 대응 SLA(4시간 이내 차단)를 고객 약관에 명시해 법적 근거 확보\n"
            "- 어뷰징 시도 로그를 SIEM에 수집해 조직 단위 패턴 분석으로 공모형 남용 탐지\n",
        ])
    elif any(
        kw in text
        for kw in [
            "bigquery",
            "data cloud",
            "데이터 큐레이션",
            "etl",
            "analytics",
            "warehouse",
            "lakehouse",
            "iceberg",
        ]
    ):
        template += _pick_variant(item, [
            "- 데이터 파이프라인의 출처·목적지별 PII 분류와 DLP 마스킹 정책 적용 검토\n"
            "- ETL/큐레이션 작업의 서비스 계정 권한을 테이블 단위 IAM으로 축소하고 감사\n"
            "- 컬럼 단위 암호화(CMEK)와 BigQuery row-level security 정책 일관성 확인\n",
            "- Iceberg/Delta Lake 테이블의 time-travel 스냅샷에 포함된 PII 보존 기간 정책 수립\n"
            "- 데이터 웨어하우스 쿼리 로그를 감사 데이터셋에 별도 저장해 이상 접근 분석\n"
            "- ETL 오케스트레이터(Airflow/Dataform) 시크릿을 시크릿 매니저로 이전하고 로테이션 자동화\n",
            "- BigQuery authorized view로 민감 컬럼 접근을 팀 단위로 제한하고 주기적 권한 리뷰\n"
            "- 데이터 레이크하우스의 외부 테이블 경로 검증으로 경로 조작 인젝션 위험 차단\n"
            "- Analytics 파이프라인 실패 이벤트를 PagerDuty·Slack에 연동해 데이터 지연 MTTD 단축\n",
        ])
    elif any(
        kw in text
        for kw in [
            "gemini",
            "enterprise ai",
            "엔터프라이즈 ai",
            "agentic",
            "에이전틱",
            "public sector",
            "공공 부문",
        ]
    ):
        template += _pick_variant(item, [
            "- 엔터프라이즈 AI 도입 시 데이터 분류(공개/내부/기밀/규제) 등급별 RAG 접근 통제 설계\n"
            "- 에이전트 도구 호출(Tool Use)에 화이트리스트·스키마 검증과 human-in-the-loop 승인 게이트 적용\n"
            "- 컴플라이언스(FedRAMP/KISA/CSAP) 요구사항과 모델 계층 책임 공유 모델 문서화\n",
            "- 엔터프라이즈 AI 서비스의 데이터 레지던시(국가 경계) 요구사항과 모델 학습 약관 재검토\n"
            "- RAG 인덱스 내 기밀 문서 접근 권한을 사용자 역할에 연동해 정보 누출 경로 차단\n"
            "- AI 솔루션 공급망 보안(모델 업데이트 검증·서명)을 계약 조항에 명시하고 정기 감사\n",
            "- 공공 부문 AI 도입 시 개인정보보호위원회 가이드라인과 자동화 의사결정 고지 의무 준수 확인\n"
            "- 에이전틱 워크플로우에서 민감 데이터 처리 단계를 격리된 실행 환경(Sandbox)에서 수행\n"
            "- 엔터프라이즈 AI 로그(프롬프트·응답)의 보존 기간과 접근 제어를 규정 요건에 맞게 설정\n",
        ])
    else:
        logging.info(
            f"DevOps template fallback triggered for: {item.get('title', '')[:60]}"
        )
        template += _pick_generic_devops_bullets(item)

    template += "\n"
    return _contextualize_practical_points(template, item)


# Diverse fallback bullet pools — selected deterministically by item hash so
# that multiple items in the same digest post don't all get identical bullets.
_DEVOPS_FALLBACK_POOLS: List[List[str]] = [
    [
        "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인",
        "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검",
        "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정",
    ],
    [
        "- 변경 관리 티켓과 IaC 커밋의 1:1 추적성 확보로 사후 감사 대응 간소화",
        "- 스테이징-프로덕션 파리티 점검으로 구성 차이에서 오는 운영 위험 제거",
        "- 변경 롤백 플랜(Runbook)을 워크플로우에 포함시켜 MTTR 단축",
    ],
    [
        "- 서비스 의존성 그래프 기반으로 변경 파급 범위(blast radius)를 사전 가시화",
        "- 운영 지표(SLO·error budget)가 변경 이전 수준으로 수렴하는지 release gate 자동화",
        "- 주요 서드파티 서비스의 Status 페이지를 내부 알림 파이프라인에 연동",
    ],
    [
        "- 기능 플래그(Feature Flag) 점진 롤아웃으로 회귀 리스크를 단계적으로 검증",
        "- 운영 툴 접근(SSH/kubectl/cloud CLI) 이력의 JIT 권한과 감사 로그 정기 리뷰",
        "- 쉘·플레이북 자동화에 dry-run 모드와 승인 게이트를 기본값으로 설정",
    ],
    [
        "- Prometheus/OpenTelemetry 경보 룰을 변경 이벤트와 상관관계 분석해 회귀 탐지",
        "- 인프라 스냅샷·백업의 복구 리허설을 분기별로 실제 집행하고 결과 기록",
        "- 서비스 오너·오너십 메타데이터를 catalog화해 변경 책임 소재 명확화",
    ],
]


def _pick_generic_devops_bullets(item: Optional[Dict]) -> str:
    """Deterministically pick one of the fallback bullet pools based on item hash.

    Ensures different items in the same digest post receive different bullets
    even when they all fall through to the generic fallback branch.
    """
    if item is None:
        return "\n".join(_DEVOPS_FALLBACK_POOLS[0]) + "\n"
    seed = item.get("url") or item.get("title", "") or ""
    if not seed:
        return "\n".join(_DEVOPS_FALLBACK_POOLS[0]) + "\n"
    # Non-crypto stable hash — stdlib hash() varies per run, so use a sum
    bucket = sum(ord(c) for c in seed) % len(_DEVOPS_FALLBACK_POOLS)
    return "\n".join(_DEVOPS_FALLBACK_POOLS[bucket]) + "\n"


def _generate_trend_analysis(news_items: List[Dict], section_num: int) -> str:
    """뉴스 기반 트렌드 분석 섹션 생성 - 기사 제목 기반 구체적 키워드 추출"""
    content = f"\n---\n\n## {section_num}. 트렌드 분석\n\n"

    # 트렌드 키워드 카운트 + 대표 기사 수집
    trend_defs = {
        "AI/ML": ["ai", "ml", "llm", "gpt", "machine learning", "인공지능", "생성형"],
        "제로데이": ["zero-day", "0-day", "제로데이"],
        "클라우드 보안": ["cloud", "aws", "azure", "gcp", "클라우드"],
        "공급망 보안": ["supply chain", "공급망", "dependency", "package"],
        "랜섬웨어": ["ransomware", "랜섬웨어"],
        "컨테이너/K8s": ["kubernetes", "k8s", "container", "docker", "컨테이너"],
        "인증 보안": ["authentication", "인증", "credential", "identity", "sso"],
    }

    trend_results = []
    matched_indices: set[int] = set()
    for trend_name, keywords in trend_defs.items():
        count = 0
        representative_titles = []
        for idx, item in enumerate(news_items):
            # Use title primarily for classification to avoid false positives
            title_text = item.get("title", "").lower()
            for kw in keywords:
                # Require word boundary match for short keywords (<=3 chars)
                if len(kw) <= 3:
                    if re.search(r"\b" + re.escape(kw) + r"\b", title_text):
                        matched = True
                    else:
                        matched = False
                else:
                    matched = kw in title_text
                if matched:
                    count += 1
                    matched_indices.add(idx)
                    title = item.get("title", "")
                    source = item.get("source_name", "")
                    short_ref = _extract_trend_keyword(title, source)
                    if short_ref and short_ref not in representative_titles:
                        representative_titles.append(short_ref)
                    break  # count each news item once
        if count > 0:
            # Show article-specific keywords instead of generic match keywords
            display_kws = (
                ", ".join(representative_titles[:3])
                if representative_titles
                else trend_name
            )
            trend_results.append(
                (trend_name, count, display_kws, representative_titles)
            )

    # Add "기타" for unmatched items so trend sum == total
    etc_count = len(news_items) - len(matched_indices)
    if etc_count > 0:
        trend_results.append(("기타", etc_count, "기타 주제", []))

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws, _ in trend_results:
            content += f"| **{name}** | {count}건 | {kws} |\n"
        content += "\n"

        # Generate specific analysis based on actual articles
        top = trend_results[0]
        top_refs = top[3][:2]  # top 2 representative titles
        content += f"이번 주기의 핵심 트렌드는 **{top[0]}**({top[1]}건)입니다. "
        if top_refs:
            content += f"{', '.join(top_refs)} 등이 주요 이슈입니다. "

        if len(trend_results) > 1:
            second = trend_results[1]
            second_refs = second[3][:2]
            if second_refs:
                content += f"**{second[0]}** 분야에서는 {', '.join(second_refs)} 관련 동향에 주목할 필요가 있습니다."
            else:
                content += f"**{second[0]}**({second[1]}건)도 주목할 트렌드입니다."
        content += "\n\n"
    else:
        content += "이번 주기에는 두드러진 트렌드가 감지되지 않았습니다.\n\n"

    return content


# Common English phrases to Korean mapping for trend keywords
_TREND_KR_MAP = {
    "vulnerability": "취약점",
    "vulnerabilities": "취약점",
    "attack": "공격",
    "attacks": "공격",
    "breach": "침해",
    "exploit": "익스플로잇",
    "exploits": "익스플로잇",
    "malware": "악성코드",
    "ransomware": "랜섬웨어",
    "phishing": "피싱",
    "zero-day": "제로데이",
    "zero day": "제로데이",
    "supply chain": "공급망",
    "patch": "패치",
    "update": "업데이트",
    "updates": "업데이트",
    "security": "보안",
    "threat": "위협",
    "threats": "위협",
    "critical": "심각한",
    "new": "신규",
    "found": "발견",
    "targets": "표적",
    "warns": "경고",
    "flaw": "결함",
    "flaws": "결함",
    "bug": "버그",
    "bugs": "버그",
    "leaked": "유출",
    "stolen": "탈취",
    "exposed": "노출",
    "compromised": "침해된",
    "scanner": "스캐너",
    "scanning": "스캐닝",
    "detection": "탐지",
    "detected": "탐지된",
    "campaign": "캠페인",
    "campaigns": "캠페인",
    "credential": "자격증명",
    "credentials": "자격증명",
    "backdoor": "백도어",
    "botnet": "봇넷",
    "spyware": "스파이웨어",
    "trojan": "트로이목마",
    "intrusion": "침입",
    "encryption": "암호화",
    "decryption": "복호화",
    "authentication": "인증",
    "authorization": "인가",
    "misconfiguration": "설정 오류",
    "privilege escalation": "권한 상승",
    "data exfiltration": "데이터 유출",
    "lateral movement": "횡적 이동",
    "command and control": "명령제어",
    "indicators of compromise": "침해 지표",
    "affected": "영향받은",
    "disclosure": "공개",
    "advisory": "권고",
    "remediation": "조치",
    "mitigation": "완화",
    "workaround": "우회 조치",
    # Crypto & finance terms
    "bitcoin": "비트코인",
    "crypto": "암호화폐",
    "cryptocurrency": "암호화폐",
    "blockchain": "블록체인",
    "staking": "스테이킹",
    "wallet": "지갑",
    "token": "토큰",
    "tokens": "토큰",
    "exchange": "거래소",
    "mining": "채굴",
    "defi": "디파이",
    "nft": "NFT",
    "scam": "사기",
    "fraud": "사기",
    "laundering": "자금세탁",
    # Common security news verbs/nouns from THN analysis
    "hackers": "해커",
    "hacker": "해커",
    "steal": "탈취",
    "target": "표적",
    "targeting": "표적 공격",
    "unpatched": "미패치",
    "patches": "패치",
    "patched": "패치된",
    "enable": "허용",
    "enables": "허용",
    "remote": "원격",
    "execution": "실행",
    "access": "접근",
    "data": "데이터",
    "server": "서버",
    "servers": "서버",
    "devices": "장치",
    "device": "장치",
    "network": "네트워크",
    "networks": "네트워크",
    "code": "코드",
    "payload": "페이로드",
    "root": "루트",
    "privilege": "권한",
    "bypass": "우회",
    "hijack": "하이재킹",
    "hijacking": "하이재킹",
    # Trend header / category phrases
    "cloud security": "클라우드 보안",
    "cloud native": "클라우드 네이티브",
    "market risk": "시장 리스크",
    "product strategy": "제품 전략",
    "ai strategy": "AI 전략",
    "vertical ai": "버티컬 AI",
    "open source": "오픈소스",
    "platform engineering": "플랫폼 엔지니어링",
    "developer tools": "개발 도구",
    "programming languages": "프로그래밍 언어",
    "push": "추진",
    "pushes": "추진",
    "banks": "은행",
    "divergence": "괴리",
    "reflects": "반영",
    "tokenized": "토큰화",
    "deposits": "예금",
    "hack": "해킹",
    "report": "보고서",
    "reports": "보고서",
    "analysis": "분석",
    "risk": "리스크",
    "risks": "리스크",
    "response": "대응",
    "strategy": "전략",
    "management": "관리",
    "investment": "투자",
    "regulation": "규제",
    "market": "시장",
    "platform": "플랫폼",
    "infrastructure": "인프라",
    "framework": "프레임워크",
    "migration": "마이그레이션",
    "integration": "통합",
    "automation": "자동화",
    "deployment": "배포",
    "performance": "성능",
    "reliability": "안정성",
    "resilience": "복원력",
    # Cloud & infrastructure terms (note: "misconfiguration" already defined above)
    "misconfigured": "잘못 설정된",
    "overprivileged": "과잉 권한",
    "drift": "드리프트",
    "compliance": "컴플라이언스",
    "governance": "거버넌스",
    "provisioning": "프로비저닝",
    "workload": "워크로드",
    "workloads": "워크로드",
    "container": "컨테이너",
    "containers": "컨테이너",
    "serverless": "서버리스",
    "microservice": "마이크로서비스",
    "microservices": "마이크로서비스",
    "outage": "장애",
    "downtime": "다운타임",
    "latency": "지연",
    "throttling": "쓰로틀링",
    "scaling": "스케일링",
    "autoscaling": "오토스케일링",
    "observability": "옵저버빌리티",
    "monitoring": "모니터링",
    "incident": "인시던트",
    "cost optimization": "비용 최적화",
    "identity federation": "ID 페더레이션",
    "secret sprawl": "시크릿 난립",
}

# Technical terms to preserve as-is (not translated)
_TECH_PRESERVE = {
    "kubernetes",
    "docker",
    "aws",
    "azure",
    "gcp",
    "linux",
    "windows",
    "android",
    "ios",
    "macos",
    "python",
    "java",
    "golang",
    "rust",
    "github",
    "gitlab",
    "npm",
    "pip",
    "helm",
    "terraform",
    "ansible",
    "nginx",
    "apache",
    "redis",
    "mysql",
    "postgresql",
    "mongodb",
    "cve",
    "rce",
    "xss",
    "ssrf",
    "sqli",
    "csrf",
    "idor",
    "ai",
    "llm",
    "gpt",
    "ml",
    "api",
    "sdk",
    "cli",
    "vpn",
    "tls",
    "ssl",
    # Security tools & platforms
    "burp",
    "nessus",
    "qualys",
    "snyk",
    "sonarqube",
    "trivy",
    "grype",
    "falco",
    "wazuh",
    "splunk",
    "datadog",
    "grafana",
    "prometheus",
    "nmap",
    "wireshark",
    "metasploit",
    "cobalt",
    "crowdstrike",
    "sentinel",
    "owasp",
    "mitre",
    "siem",
    "edr",
    "xdr",
    "soar",
    "cnapp",
    "cspm",
    "zscaler",
    "cloudflare",
    "paloalto",
    "fortinet",
    "checkpoint",
    # Additional from THN coverage analysis
    "cisa",
    "apple",
    "google",
    "microsoft",
    "samsung",
    "cisco",
    "vmware",
    "chrome",
    "firefox",
    "safari",
    "edge",
    "outlook",
    "wordpress",
    "ivanti",
    "juniper",
    "sophos",
    "zyxel",
}


# Sanity check: no duplicate keys in mapping dicts
assert len(_TREND_KR_MAP) == len(dict(_TREND_KR_MAP)), (
    "Duplicate key in _TREND_KR_MAP — check for repeated entries"
)

# Stop words to drop from translated output
_STOP_WORDS = {
    "a",
    "an",
    "the",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "by",
    "with",
    "from",
    "and",
    "or",
    "but",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "has",
    "have",
    "had",
    "do",
    "does",
    "did",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "as",
    "how",
    "what",
    "why",
    "who",
    "when",
    "where",
    "which",
    "not",
    "no",
    "just",
    "over",
    "up",
    "out",
    "all",
    "can",
    "may",
    "will",
    "would",
    "could",
    "should",
    "here's",
    "there's",
    "more",
    "most",
    "very",
    "also",
    "than",
    "then",
    "so",
    "if",
    "about",
    "into",
    "after",
    "before",
    "between",
    "under",
    "above",
}


def _apply_trend_kr_map(phrase: str) -> str:
    """Apply Korean mapping to English phrase, preserving tech terms."""
    # Multi-word phrase replacements first
    result = phrase
    for en, kr in _TREND_KR_MAP.items():
        if " " in en:
            pattern = re.compile(re.escape(en), re.IGNORECASE)
            result = pattern.sub(kr, result)

    # Word-by-word replacement
    tokens = result.split()
    translated = []
    for token in tokens:
        # Strip punctuation for lookup
        clean = token.strip(".,;:!?\"'()[]")
        low = clean.lower()
        # Drop stop words (articles, prepositions, conjunctions)
        if low in _STOP_WORDS:
            continue
        if low in _TECH_PRESERVE:
            translated.append(token)
        elif low in _TREND_KR_MAP:
            translated.append(_TREND_KR_MAP[low])
        else:
            translated.append(token)
    return " ".join(translated)


def _extract_trend_keyword(title: str, source: str) -> str:
    """Extract concise descriptive keyword from article title for trend table.

    Returns a short Korean phrase suitable for the trend analysis table.
    English titles are translated via _apply_trend_kr_map; if the result
    is still mostly English, fall back to a source-based label.
    """
    if not title:
        return ""
    # Remove common prefixes/noise
    title = re.sub(r"^\[.*?\]\s*", "", title)
    # For Korean titles, extract key noun phrases
    if re.search(r"[가-힣]", title):
        parts = re.split(r"[,:\-–—·]", title)
        segment = parts[0].strip()
        if len(segment) > 40:
            segment = segment[:40]
        return segment
    # For English titles, extract product/topic name then apply Korean mapping
    words = title.split()
    if len(words) <= 6:
        phrase = title.strip()
    else:
        # Take first meaningful phrase (up to 7 words, max 60 chars)
        phrase = " ".join(words[:7])
        if len(phrase) > 60:
            phrase = phrase[:60].rsplit(" ", 1)[0]
    translated = _apply_trend_kr_map(phrase)
    # If still mostly English after mapping, use a shorter source-based label
    kr_chars = len(re.findall(r"[가-힣]", translated))
    total_alpha = len(re.findall(r"[a-zA-Z]", translated))
    if total_alpha > 0 and kr_chars / max(total_alpha + kr_chars, 1) < 0.3:
        # Try translating the full title for better coverage
        full_translated = _apply_trend_kr_map(title.strip())
        kr_full = len(re.findall(r"[가-힣]", full_translated))
        total_full = len(re.findall(r"[a-zA-Z]", full_translated))
        if kr_full / max(total_full + kr_full, 1) >= 0.3:
            # Truncate to reasonable length
            if len(full_translated) > 40:
                full_translated = full_translated[:40].rsplit(" ", 1)[0]
            return full_translated
        # Final fallback: source name as context
        if source:
            return f"{source} 관련 동향"
    return translated


def _generate_news_specific_checklist(news_items: List[Dict]) -> str:
    """뉴스 기반 실무 체크리스트 생성"""
    content = "---\n\n## 실무 체크리스트\n\n"

    p0_items = []
    p1_items = []

    for item in news_items:
        category = item.get("category", "tech")
        # Only include security-relevant items in the checklist
        if category not in (
            "security",
            "devsecops",
            "ai",
            "cloud",
            "devops",
            "kubernetes",
        ):
            continue
        severity = _determine_severity(item)
        title = _korean_display_title(item, max_len=50)
        cve_ids = _extract_cve_ids(item)
        cve_str = f" ({', '.join(cve_ids[:2])})" if cve_ids else ""
        if severity == "Critical":
            p0_items.append(f"- [ ] **{title}**{cve_str} 관련 긴급 패치 및 영향도 확인")
        elif severity == "High":
            p1_items.append(f"- [ ] **{title}**{cve_str} 관련 보안 검토 및 모니터링")

    content += "### P0 (즉시)\n\n"
    if p0_items:
        content += "\n".join(p0_items[:5]) + "\n"
    else:
        # Generate specific P0 from top security news
        sec_items = [n for n in news_items if n.get("category") == "security"]
        if sec_items:
            top_sec = sec_items[0]
            title = _korean_display_title(top_sec, max_len=40)
            content += f"- [ ] **{title}** 관련 보안 영향도 분석 및 모니터링 강화\n"
        else:
            content += "- [ ] 이번 주기 주요 보안 이슈 영향도 분석\n"

    content += "\n### P1 (7일 내)\n\n"
    if p1_items:
        content += "\n".join(p1_items[:5]) + "\n"
    else:
        # Generate P1 from actual news categories
        categories_present = {n.get("category", "tech") for n in news_items}
        if "security" in categories_present:
            content += "- [ ] 보안 뉴스 기반 SIEM/EDR 탐지 룰 업데이트\n"
        if "cloud" in categories_present or "devops" in categories_present:
            cloud_items = [
                n for n in news_items if n.get("category") in ("cloud", "devops")
            ]
            if cloud_items:
                title = _korean_display_title(cloud_items[0], max_len=40)
                content += f"- [ ] **{title}** 관련 인프라 설정 점검\n"
        if not p1_items and "security" not in categories_present:
            content += "- [ ] 이번 주기 기술 동향 기반 보안 정책 검토\n"

    content += "\n### P2 (30일 내)\n\n"
    # Generate dynamic P2 based on news content
    p2_items = []
    categories_present = {n.get("category", "tech") for n in news_items}
    if "ai" in categories_present:
        ai_items = [n for n in news_items if n.get("category") == "ai"]
        if ai_items:
            title = _korean_display_title(ai_items[0], max_len=40)
            p2_items.append(f"- [ ] **{title}** 관련 AI 보안 정책 검토")
    if "cloud" in categories_present:
        p2_items.append("- [ ] 클라우드 인프라 보안 설정 정기 감사")
    if "blockchain" in categories_present:
        p2_items.append("- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검")
    if not p2_items:
        p2_items.append("- [ ] 이번 주기 트렌드 기반 보안 아키텍처 검토")
    content += "\n".join(p2_items[:3]) + "\n"

    return content
