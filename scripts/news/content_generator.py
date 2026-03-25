"""Content generation functions for news digest posts."""

import html
import logging
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

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
from scripts.news.analyzer import (
    extract_cve_id,
    generate_mitre_mapping,
    generate_risk_scorecard,
)
from scripts.news.svg_generator import (
    _escape_svg_text,
    _extract_key_topics,
    _to_english_svg_text,
    _truncate_text,
)


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
            candidate = candidate[:26].rsplit(" ", 1)[0].rstrip(" ,.")
        if not candidate:
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


def _build_clean_excerpt(title_keywords: str, date_str: str, total: int, mode: str) -> str:
    """품질 검증된 excerpt 생성 - 조사 자동 보정, 150-200자 목표"""
    # 조사 보정: 받침 여부에 따라 을/를 선택
    last_char = title_keywords.rstrip()[-1] if title_keywords.rstrip() else ""
    particle = "을" if _has_batchim(last_char) else "를"
    if mode == "tech":
        return f"{title_keywords}{particle} 중심으로 {date_str} 주요 기술 블로그 뉴스 {total}건과 개발자 관점의 적용 포인트를 정리합니다."
    return f"{title_keywords}{particle} 중심으로 {date_str} 주요 보안/기술 뉴스 {total}건과 대응 우선순위를 정리합니다."


def _build_clean_description(title_keywords: str, source_list: str, date_str: str, total: int, mode: str) -> str:
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
        return f"{date_str} 기술 블로그 다이제스트. {source_list} 등 {total}건을 분석하고 {keywords_text} 등 개발자 트렌드와 운영 시사점을 정리합니다."
    return f"{date_str} 보안 뉴스 요약. {source_list} 등 {total}건을 분석하고 {keywords_text} 등 DevSecOps 대응 포인트를 정리합니다."


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


def _build_digest_title(news_items: List[Dict], mode: str = "security") -> str:
    """Prefer specific headline-driven titles over generic topic buckets."""
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
        if len(title) <= 80:
            return title

    label_title = ", ".join(_extract_digest_title_labels(news_items, mode=mode))
    if label_title:
        return label_title[:80].rstrip(" ,.")

    return _extract_meaningful_topics(news_items, mode=mode)


def _generate_executive_and_risk_sections(
    news_items: List[Dict], mode: str = "security"
) -> str:
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

    content = f'''---
layout: post
title: "{title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [security, devsecops]
tags: [{", ".join(tags)}]
excerpt: "{_build_clean_excerpt(title_keywords, date_str, total, 'security')}"
description: "{_build_clean_description(title_keywords, source_list, date_str, total, 'security')}"
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "{_build_clean_image_alt(title_keywords, 'security')}"
toc: true
---

{{% include ai-summary-card.html
  title='{title_keywords}'
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
- **총 뉴스 수**: {total}개
- **보안 뉴스**: {stats.get("security", 0)}개
- **AI/ML 뉴스**: {stats.get("ai", 0)}개
- **클라우드 뉴스**: {stats.get("cloud", 0)}개
- **DevOps 뉴스**: {stats.get("devops", 0)}개
- **블록체인 뉴스**: {stats.get("blockchain", 0)}개

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

    content += _generate_executive_and_risk_sections(news_items, mode="security")

    section_num = 1

    # 보안 뉴스 섹션 - SK Shieldus 그룹핑 포함
    if security_news:
        content += f"## {section_num}. 보안 뉴스\n\n"

        # Separate SK Shieldus reports from regular security news
        skshieldus_reports = [
            item for item in security_news if item.get("source") == "skshieldus_report"
        ]
        regular_security = [
            item for item in security_news if item.get("source") != "skshieldus_report"
        ]

        for i, item in enumerate(regular_security, 1):
            is_critical = i <= 5  # 상위 5개 뉴스에 AI 강화 적용
            content += generate_news_section(
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
            content += (
                f"### {section_num}.{sub_idx} SK쉴더스 {month_str} 보안 리포트\n\n"
            )
            content += "SK쉴더스에서 발행한 최신 보안 리포트 모음입니다.\n\n"
            for report in skshieldus_reports:
                report_title = report.get("title", "보안 리포트")
                report_url = report.get("url", "")
                report_summary = report.get("summary", "")
                content += f"- **[{report_title}]({report_url})**"
                if report_summary:
                    short_summary = report_summary[:100].rstrip(".")
                    content += f": {short_summary}"
                content += "\n"
            content += "\n> SK쉴더스 보안 리포트는 국내 보안 환경에 특화된 위협 분석을 제공합니다. 원문을 다운로드하여 상세 내용을 확인하시기 바랍니다.\n\n"
            content += "---\n\n"

        section_num += 1

    # AI/ML 뉴스 섹션
    if ai_news:
        content += f"## {section_num}. AI/ML 뉴스\n\n"
        for i, item in enumerate(ai_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 클라우드 뉴스 섹션
    if cloud_news:
        content += f"## {section_num}. 클라우드 & 인프라 뉴스\n\n"
        for i, item in enumerate(cloud_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # DevOps 뉴스 섹션
    if devops_news:
        content += f"## {section_num}. DevOps & 개발 뉴스\n\n"
        for i, item in enumerate(devops_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 블록체인 뉴스 섹션
    if blockchain_news:
        content += f"## {section_num}. 블록체인 뉴스\n\n"
        for i, item in enumerate(blockchain_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

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

    content = f'''---
layout: post
title: "기술 블로그 주간 다이제스트: {title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [tech, devops]
tags: [{", ".join(tags)}]
excerpt: "{_build_clean_excerpt(title_keywords, date_str, total, 'tech')}"
description: "{_build_clean_description(title_keywords, source_list, date_str, total, 'tech')}"
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "{_build_clean_image_alt(title_keywords, 'tech')}"
toc: true
---

{{% include ai-summary-card.html
  title='기술 블로그 주간 다이제스트: {title_keywords}'
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
    for trend_name, keywords in trend_defs.items():
        count = 0
        matched_kws = set()
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for kw in keywords:
                if kw in text:
                    count += 1
                    matched_kws.add(kw)
                    break
        if count > 0:
            trend_results.append((trend_name, count, ", ".join(list(matched_kws)[:3])))

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws in trend_results[:7]:
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


def _generate_contextual_action_point(item: Dict) -> str:
    """Generate a context-aware action point based on actual article content.

    Extracts keywords from the title/summary to produce specific advice
    instead of generic category-based text.
    """
    title = (item.get("title", "") or "").lower()
    summary = (item.get("summary", "") or "").lower()
    combined = f"{title} {summary}"
    category = item.get("category", "tech")

    # Security-specific contextual hints
    if category in ("security", "devsecops"):
        if any(kw in combined for kw in ["patch", "update", "패치", "업데이트"]):
            return "영향받는 시스템 버전을 확인하고 패치 적용 일정을 수립하세요."
        if any(kw in combined for kw in ["ransomware", "랜섬웨어"]):
            return "백업 상태 확인, 네트워크 세그먼테이션 점검, 이메일 필터링 강화를 권장합니다."
        if any(kw in combined for kw in ["phishing", "피싱", "credential", "자격증명"]):
            return "MFA 적용 현황 점검 및 사용자 보안 인식 교육을 강화하세요."
        if any(kw in combined for kw in ["supply chain", "공급망", "dependency"]):
            return "서드파티 의존성 감사(SCA)를 수행하고 SBOM을 최신 상태로 유지하세요."
        if any(kw in combined for kw in ["data breach", "유출", "leak"]):
            return "영향 범위 파악, 인시던트 대응 절차 발동, 규제 기관 통보 여부를 확인하세요."
        if any(kw in combined for kw in ["malware", "악성코드", "trojan", "backdoor"]):
            return "EDR/SIEM에서 IoC 기반 탐지 룰을 업데이트하세요."
        if re.search(r"cve-\d{4}-\d+", combined):
            return (
                "해당 CVE의 영향 범위와 CVSS 점수를 확인 후 패치 우선순위를 결정하세요."
            )
        return "보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요."

    # AI category
    if category == "ai":
        if any(kw in combined for kw in ["agent", "에이전트", "agentic"]):
            return (
                "AI Agent 도입 시 권한 범위 설정과 출력 검증 체계를 사전에 수립하세요."
            )
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
            return "AI 생성 코드에 대한 보안 스캔(SAST/SCA) 게이트를 CI/CD에 필수 적용하세요."
        if any(kw in combined for kw in ["llm", "gpt", "claude", "gemini"]):
            return "LLM 서빙 환경의 접근 제어와 프롬프트 인젝션 방어 체계를 점검하세요."
        if any(
            kw in combined for kw in ["gpu", "nvidia", "compute", "training", "factory"]
        ):
            return "AI 인프라 도입 시 보안 경계 설계와 데이터 프라이버시 규정 준수를 확인하세요."
        if any(
            kw in combined
            for kw in ["open source", "오픈소스", "hugging face", "ollama"]
        ):
            return "오픈소스 모델 도입 시 출처 검증, 라이선스 및 학습 데이터 리스크를 평가하세요."
        if any(kw in combined for kw in ["model", "모델"]):
            return (
                "자사 AI 워크로드에 적용 가능성과 비용/성능 트레이드오프를 평가하세요."
            )
        return "AI/ML 파이프라인 및 서비스에 미치는 영향을 검토하세요."

    # Cloud / DevOps
    if category in ("cloud", "devops", "kubernetes"):
        if any(kw in combined for kw in ["rbac", "iam", "권한", "identity"]):
            return (
                "IAM/RBAC 정책의 최소 권한 원칙 준수와 서비스 계정 감사를 수행하세요."
            )
        if any(kw in combined for kw in ["kubernetes", "k8s", "쿠버네티스"]):
            return "클러스터 버전 호환성과 워크로드 영향을 확인하세요."
        if any(kw in combined for kw in ["docker", "container", "컨테이너"]):
            return "컨테이너 이미지 업데이트 및 런타임 보안 설정을 점검하세요."
        if any(kw in combined for kw in ["terraform", "iac", "인프라 코드"]):
            return "IaC 템플릿 보안 스캔(Checkov/tfsec)과 드리프트 탐지를 확인하세요."
        if any(
            kw in combined for kw in ["serverless", "lambda", "서버리스", "function"]
        ):
            return "서버리스 함수의 IAM 역할 최소화와 실행 환경 보안 설정을 점검하세요."
        if any(kw in combined for kw in ["aws", "azure", "gcp"]):
            return "클라우드 서비스 변경사항이 인프라 구성에 미치는 영향을 확인하세요."
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
            return "블록체인 보안 사고 관련 IoC를 확인하고 유사 공격 벡터에 대한 방어 체계를 점검하세요."
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
            return "규제 변화에 따른 컴플라이언스 영향을 법무팀과 사전 검토하세요."
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
            return "관련 DeFi 프로토콜의 스마트 컨트랙트 감사 현황과 비상 정지 메커니즘을 확인하세요."
        if any(
            kw in combined
            for kw in ["conference", "컨퍼런스", "summit", "speaker", "연사"]
        ):
            return "대규모 행사 전후로 관련 토큰 사기 및 가짜 이벤트 피싱이 증가합니다. 공식 채널만 이용하세요."
        if any(kw in combined for kw in ["bitcoin", "비트코인", "btc"]):
            return "시장 변동성 확대 시기에 피싱 도메인 모니터링을 강화하고 고액 출금 인증 절차를 점검하세요."
        if any(
            kw in combined
            for kw in ["ethereum", "이더리움", "eth", "stablecoin", "스테이블코인"]
        ):
            return "스마트 컨트랙트 기반 서비스의 접근 제어와 트랜잭션 모니터링을 점검하세요."
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
            display_title = display_title[:max_len].rsplit(" ", 1)[0].rstrip(" ,.")

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
            '  title="%s"' % title.replace('"', '\\"'),
            '  url="%s"' % url,
        ]
        if image:
            # Strip query params that break Jekyll include parser
            clean_image = image.split("?")[0] if "?" in image else image
            card_parts.append('  image="%s"' % clean_image)
        if ko_summary:
            card_summary = ko_summary[:200].replace('"', '\\"')
            card_parts.append('  summary="%s"' % card_summary)
        card_parts.append('  source="%s"' % source.replace('"', '\\"'))
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
    for sep in ["습니다.", "니다.", "했습니다.", "됩니다.", "입니다.", "다.", "됨.", "임."]:
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
        template += "- AI 에이전트 도구 호출 권한 및 접근 범위 최소화 설계\n"
        template += "- 에이전트 행동 로깅 및 감사 파이프라인 구축 검토\n"
        template += "- 에이전트 출력에 대한 검증 및 사람 감독(Human-in-the-Loop) 설계\n"
    elif any(kw in text for kw in ["llm", "gpt", "claude", "gemini", "model"]):
        template += "- LLM 입출력 데이터 보안 및 프라이버시 검토\n"
        template += "- 모델 서빙 환경의 접근 제어 및 네트워크 격리 확인\n"
        template += "- 프롬프트 인젝션 등 적대적 공격 대응 방안 점검\n"
    elif any(
        kw in text
        for kw in ["gpu", "nvidia", "인프라", "factory", "compute", "training"]
    ):
        template += "- 대규모 AI 인프라 도입 시 보안 경계 및 접근 제어 설계 검토\n"
        template += "- GPU 클러스터 운영 환경의 취약점 관리 및 패치 정책 수립\n"
        template += "- AI 워크로드 데이터 프라이버시 규정(GDPR, HIPAA) 준수 확인\n"
    elif any(
        kw in text
        for kw in ["simulation", "시뮬레이션", "digital twin", "optimize", "최적화"]
    ):
        template += (
            "- 시뮬레이션 기반 인프라 검증으로 배포 전 보안 취약점 사전 식별 활용\n"
        )
        template += "- AI 서비스 성능 최적화와 보안 모니터링 균형 설계\n"
        template += "- 운영 비용 절감 효과와 보안 투자 ROI 분석\n"
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
        template += "- AI 코딩 도구가 생성한 코드에 대한 자동 보안 스캔(SAST/SCA) 게이트 필수 적용\n"
        template += "- AI 생성 코드의 시크릿/자격증명 하드코딩 여부 자동 탐지 설정\n"
        template += "- 개발자 대상 AI 코딩 도구 보안 사용 가이드라인 수립 및 교육\n"
    elif any(
        kw in text for kw in ["attack", "공격", "threat", "위협", "malware", "악성"]
    ):
        template += "- AI 기반 위협 탐지 및 자동 대응 파이프라인 구축 검토\n"
        template += "- AI 모델 자체의 적대적 공격(Adversarial Attack) 방어 설계\n"
        template += "- 보안 팀의 AI 도구 활용 역량 강화 교육 계획 수립\n"
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
        template += "- 오픈소스 AI 모델 도입 시 라이선스 및 보안 취약점 검토\n"
        template += "- 모델 다운로드 출처 검증 및 체크섬/서명 확인 절차 수립\n"
        template += "- 오픈소스 모델의 학습 데이터 편향 및 프라이버시 리스크 평가\n"
    else:
        logging.info(
            f"AI template fallback triggered for: {item.get('title', '')[:60]}"
        )
        template += "- AI/ML 기술 도입 시 데이터 파이프라인 보안 및 접근 제어 검토\n"
        template += "- 모델 학습/추론 환경의 네트워크 격리 및 인증 체계 확인\n"
        template += "- 관련 기술의 자사 환경 적용 가능성 평가 및 보안 영향 분석\n"

    template += "\n"
    return template


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
        template += "- 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
        template += "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
        template += "- 컨테이너 런타임 보안 모니터링 강화\n"
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
        template += "- Kubernetes RBAC 역할 및 바인딩 최소 권한 원칙 준수 감사\n"
        template += "- Admission Controller/OPA 정책으로 비인가 리소스 생성 차단\n"
        template += "- Pod Security Admission(PSA) restricted 프로필 적용 현황 점검\n"
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
        template += (
            "- 컨테이너 이미지 서명(cosign/sigstore) 및 무결성 검증 파이프라인 확인\n"
        )
        template += "- 프라이빗 레지스트리 접근 제어 및 이미지 스캔 정책 점검\n"
        template += "- SBOM 기반 이미지 의존성 취약점 추적 자동화 설정\n"
    elif any(kw in text for kw in ["서비스 메시", "service mesh", "istio", "envoy"]):
        template += "- mTLS 기반 서비스 간 통신 암호화 적용 검토\n"
        template += "- 서비스 메시 관측성 활용한 이상 트래픽 탐지 설계\n"
        template += "- 네트워크 폴리시와 서비스 메시 정책 통합 관리\n"
    elif any(
        kw in text
        for kw in ["network policy", "네트워크 폴리시", "ingress", "egress", "cilium"]
    ):
        template += "- Kubernetes NetworkPolicy로 Pod 간 불필요한 통신 차단 설정\n"
        template += "- Ingress/Egress 트래픽 암호화(mTLS) 적용 현황 검토\n"
        template += "- 네트워크 관측성 도구(Cilium Hubble 등)로 이상 트래픽 탐지 강화\n"
    elif any(
        kw in text for kw in ["kubecon", "conference", "컨퍼런스", "행사", "summit"]
    ):
        template += "- 컨퍼런스에서 발표된 새로운 보안 프레임워크 및 도구 검토\n"
        template += "- 커뮤니티 모범 사례의 자사 환경 적용 가능성 평가\n"
        template += "- 발표된 오픈소스 프로젝트의 보안 성숙도 및 도입 로드맵 검토\n"
    elif any(kw in text for kw in ["kubernetes", "k8s", "kcd", "cncf"]):
        template += "- Kubernetes 클러스터 보안 벤치마크(CIS) 준수 점검\n"
        template += "- API 서버 접근 제어 및 감사 로그(Audit Log) 활성화 확인\n"
        template += "- 클러스터 업그레이드 주기 및 보안 패치 적용 현황 검토\n"
    elif any(
        kw in text for kw in ["ci/cd", "pipeline", "github action", "jenkins", "배포"]
    ):
        template += "- CI/CD 파이프라인 보안 강화: 시크릿 관리, 토큰 권한 최소화\n"
        template += "- 서드파티 Actions/플러그인의 출처 검증 및 버전 고정\n"
        template += "- 빌드/배포 로그 모니터링으로 비정상 행위 탐지\n"
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
        template += "- 데이터베이스/캐시 서비스 업그레이드 시 데이터 무결성 검증 및 접근 제어 점검\n"
        template += (
            "- DB 연결 암호화(SSL/TLS) 설정이 모든 복제본/노드에 적용되는지 확인\n"
        )
        template += (
            "- 자동 확장 이벤트 감사 로그 모니터링으로 비정상 리소스 증가 탐지\n"
        )
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
        template += "- 모바일 앱 업데이트에 포함된 보안 패치 및 의존성 변경사항 검토\n"
        template += "- API 키 및 민감 데이터의 클라이언트 측 노출 방지 설정 점검\n"
        template += "- 사용자 데이터 수집 시 개인정보 보호 정책(GDPR, 개인정보보호법) 준수 확인\n"
    elif any(kw in text for kw in ["네트워크", "network"]):
        template += "- 네트워크 세그멘테이션 및 방화벽 규칙 최신화 점검\n"
        template += "- 비정상 트래픽 패턴 탐지를 위한 모니터링 강화\n"
        template += "- 네트워크 접근 제어 정책(Zero Trust) 적용 현황 검토\n"
    else:
        logging.info(
            f"DevOps template fallback triggered for: {item.get('title', '')[:60]}"
        )
        template += "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
        template += "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
        template += "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"

    template += "\n"
    return template


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
    for trend_name, keywords in trend_defs.items():
        count = 0
        representative_titles = []
        for item in news_items:
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

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws, _ in trend_results[:7]:
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
    "kubernetes", "docker", "aws", "azure", "gcp", "linux", "windows",
    "android", "ios", "macos", "python", "java", "golang", "rust",
    "github", "gitlab", "npm", "pip", "helm", "terraform", "ansible",
    "nginx", "apache", "redis", "mysql", "postgresql", "mongodb",
    "cve", "rce", "xss", "ssrf", "sqli", "csrf", "idor",
    "ai", "llm", "gpt", "ml", "api", "sdk", "cli", "vpn", "tls", "ssl",
    # Security tools & platforms
    "burp", "nessus", "qualys", "snyk", "sonarqube", "trivy", "grype",
    "falco", "wazuh", "splunk", "datadog", "grafana", "prometheus",
    "nmap", "wireshark", "metasploit", "cobalt", "crowdstrike", "sentinel",
    "owasp", "mitre", "siem", "edr", "xdr", "soar", "cnapp", "cspm",
    "zscaler", "cloudflare", "paloalto", "fortinet", "checkpoint",
    # Additional from THN coverage analysis
    "cisa", "apple", "google", "microsoft", "samsung", "cisco", "vmware",
    "chrome", "firefox", "safari", "edge", "outlook", "wordpress",
    "ivanti", "juniper", "sophos", "zyxel",
}


# Sanity check: no duplicate keys in mapping dicts
assert len(_TREND_KR_MAP) == len(dict(_TREND_KR_MAP)), (
    "Duplicate key in _TREND_KR_MAP — check for repeated entries"
)

# Stop words to drop from translated output
_STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "by",
    "with", "from", "and", "or", "but", "is", "are", "was", "were",
    "be", "been", "being", "has", "have", "had", "do", "does", "did",
    "that", "this", "these", "those", "it", "its",
    "as", "how", "what", "why", "who", "when", "where", "which",
    "not", "no", "just", "over", "up", "out", "all", "can", "may",
    "will", "would", "could", "should", "here's", "there's",
    "more", "most", "very", "also", "than", "then", "so", "if",
    "about", "into", "after", "before", "between", "under", "above",
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

