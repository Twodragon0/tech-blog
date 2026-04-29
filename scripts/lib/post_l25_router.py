"""Routing helpers: parse a 2025 _posts/*.md and derive a config dict
suitable for ``svg_l25_generator.render_l25_cover_svg``.

Strategy (Korean-friendly):
  - Use ``image_alt`` (always English in 2025 posts) as the canonical
    English headline source.
  - Use the post filename stem (snake_case English) as a token bank.
  - Translate H2 headings via a glossary; fall back to deriving headlines
    from numeric tokens or English sub-strings inside the H2 line.
  - Synthesise bands when fewer than 3 useful H2s exist.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .svg_l25_generator import (  # type: ignore
    CATEGORY_DEFAULT_THEME,
    sanitize_ascii,
)

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PARA_BREAK_RE = re.compile(r"\n\s*\n")
NUMBER_PCT_RE = re.compile(r"(?P<v>[+-]?\d{1,4}(?:[.,]\d+)?(?:%|x)?)")
KOREAN_RUN_RE = re.compile(r"[\uAC00-\uD7A3]+")

# Regex patterns for stripping markdown noise from paragraphs
_MD_TABLE_LINE_RE = re.compile(r"^\|.*\|.*$", re.MULTILINE)
_MD_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.DOTALL)
_MD_LIQUID_RE = re.compile(r"\{[%{][\s\S]*?[%}]\}")
_MD_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MD_BLOCKQUOTE_RE = re.compile(r"^>.*$", re.MULTILINE)
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^\)]*\)")
_MD_ADMONITION_RE = re.compile(r"^\[!.*?\].*$", re.MULTILINE)

# ---------------------------------------------------------------------------
# Korean -> English glossary (single-token to multi-token replacements)
# Applied BEFORE sanitize_ascii. Tokens are matched as substrings.
# ---------------------------------------------------------------------------
KO_GLOSSARY: list[tuple[str, str]] = [
    # Time / duration
    ("타임라인", "Timeline"),
    ("시간순", "Chronology"),
    ("연대기", "Chronology"),
    # Core security
    ("보안", "Security"),
    ("취약점", "Vulnerabilities"),
    ("악성코드", "Malware"),
    ("악성", "Malicious"),
    ("위협", "Threat"),
    ("공격", "Attack"),
    ("침해", "Breach"),
    ("사고", "Incident"),
    ("장애", "Outage"),
    ("점검", "Audit"),
    ("탐지", "Detection"),
    ("대응", "Response"),
    ("방어", "Defense"),
    ("규정", "Compliance"),
    ("준수", "Compliance"),
    ("인증", "Certification"),
    ("감사", "Audit"),
    ("위험", "Risk"),
    ("암호", "Crypto"),
    ("인코딩", "Encoding"),
    ("키", "Key"),
    ("정책", "Policy"),
    # DevOps / infra
    ("아키텍처", "Architecture"),
    ("인프라", "Infrastructure"),
    ("네트워크", "Network"),
    ("클러스터", "Cluster"),
    ("배포", "Deploy"),
    ("운영", "Ops"),
    ("개발", "Dev"),
    ("실습", "Hands-on"),
    ("실전", "Practical"),
    ("실무", "Practice"),
    ("통합", "Integration"),
    ("자동화", "Automation"),
    ("관리", "Management"),
    ("모니터링", "Monitoring"),
    ("분석", "Analysis"),
    ("이해", "Understanding"),
    ("정복", "Mastery"),
    ("정리", "Summary"),
    ("공략", "Strategy"),
    # Generic words
    ("가이드", "Guide"),
    ("기본", "Basics"),
    ("핵심", "Core"),
    ("개요", "Overview"),
    ("들어가며", "Intro"),
    ("서론", "Intro"),
    ("결론", "Wrap-up"),
    ("교훈", "Lessons"),
    ("개선", "Improvements"),
    ("이상", "Anomaly"),
    ("위협 헌팅", "Threat Hunting"),
    ("헌팅", "Hunting"),
    ("매핑", "Mapping"),
    ("종합", "Comprehensive"),
    ("기업", "Enterprise"),
    ("담당자", "Owner"),
    ("증상", "Symptom"),
    ("현재", "Now"),
    ("미래", "Future"),
    ("실시간", "Real-time"),
    # Time scale
    ("주차", "Week"),
    ("기", "Batch"),
    ("월", "Month"),
    ("일", "Day"),
    ("년", "Year"),
    # Korean tech-blog filler
    ("이번", "This"),
    ("회차", "Session"),
    ("환경", "Environment"),
    ("구성", "Setup"),
    ("배경", "Background"),
    ("내용", "Content"),
    ("문제", "Problem"),
    ("해결", "Resolution"),
    ("문제 해결", "Troubleshoot"),
    ("결과", "Result"),
    ("정의", "Definition"),
    ("원리", "Principle"),
    ("동작", "Behavior"),
    ("진단", "Diagnostic"),
    ("최적화", "Optimization"),
    ("성능", "Performance"),
    # Stop-words that we want to drop entirely
    ("그리고", " "),
    ("및", " "),
    ("또는", "or"),
    ("부터", "from"),
    ("까지", "to"),
    ("위한", "for"),
    ("위해", "for"),
    ("관련", "related"),
    ("필요한", "needed"),
    ("및 ", " "),
    ("의 ", " "),
    ("을 ", " "),
    ("를 ", " "),
    ("이 ", " "),
    ("가 ", " "),
    ("에서", " in "),
]


def _ko_to_en(text: str) -> str:
    """Apply Korean glossary substitutions before stripping."""
    s = text
    for ko, en in KO_GLOSSARY:
        if ko in s:
            s = s.replace(ko, f" {en} ")
    return s


def _strip_korean(text: str) -> str:
    """Drop any remaining Korean runs from text."""
    return KOREAN_RUN_RE.sub(" ", text)


def to_english(text: str, max_len: int | None = None) -> str:
    """Best-effort Korean-to-English conversion using glossary, plus
    forbidden-char/accent normalisation via ``sanitize_ascii``.
    """
    if not text:
        return ""
    s = _ko_to_en(text)
    s = _strip_korean(s)
    s = sanitize_ascii(s, max_len=max_len)
    return s


def _parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONT_MATTER_RE.search(text)
    if not m:
        return {}, text
    fm: dict[str, Any] = {}
    body = m.group(1)
    current_key: str | None = None
    for raw_line in body.splitlines():
        if not raw_line.strip():
            current_key = None
            continue
        if raw_line.startswith("- ") and current_key:
            fm.setdefault(current_key, []).append(raw_line[2:].strip())
            continue
        m2 = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw_line)
        if not m2:
            continue
        key, val = m2.group(1), m2.group(2).strip()
        current_key = key
        if val == "":
            fm[key] = []
        else:
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            fm[key] = val
    body_after = text[m.end():]
    return fm, body_after


def _clean_markdown_noise(text: str) -> str:
    """Strip markdown tables, code fences, HTML, Liquid tags, blockquotes from text."""
    s = text
    # Remove code fences first (multiline)
    s = _MD_CODE_FENCE_RE.sub(" ", s)
    # Remove Liquid tags
    s = _MD_LIQUID_RE.sub(" ", s)
    # Remove HTML tags
    s = _MD_HTML_TAG_RE.sub(" ", s)
    # Remove blockquotes (lines starting with >)
    s = _MD_BLOCKQUOTE_RE.sub(" ", s)
    # Remove image markdown
    s = _MD_IMAGE_RE.sub(" ", s)
    # Remove admonition lines [!NOTE] etc
    s = _MD_ADMONITION_RE.sub(" ", s)
    # Remove table lines (lines that are | ... | pattern)
    s = _MD_TABLE_LINE_RE.sub(" ", s)
    # Strip markdown link syntax: keep visible text
    s = re.sub(r"\[([^\]]+)\]\([^\)]*\)", r"\1", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _korean_ratio(text: str) -> float:
    """Return fraction of characters that are Korean."""
    if not text:
        return 0.0
    korean_chars = len(KOREAN_RUN_RE.findall("".join(text.split())))
    total = len("".join(text.split()))
    if total == 0:
        return 0.0
    # Count individual Korean codepoints
    ko_count = sum(1 for ch in text if "\uAC00" <= ch <= "\uD7A3")
    return ko_count / max(len(text), 1)


def _first_paragraph(body_chunk: str, max_len: int = 200) -> str:
    """Extract first meaningful paragraph, stripped of markdown noise.

    Returns empty string if no usable paragraph found.
    Skips paragraphs that are pure markdown tables, code, or mostly Korean
    (those will be handled by caller with fallback).
    """
    paragraphs = PARA_BREAK_RE.split(body_chunk.strip())
    for p in paragraphs:
        s = p.strip()
        if not s:
            continue
        # Skip block-level markers
        if s.startswith(("```", ">", "- ", "* ", "{%", "<", "|", "!", "[!", "[Mermaid", "[ ", ":")):
            continue
        if s.startswith(("#",)):
            continue
        if s.startswith("!["):
            continue
        # Skip lines that are pure numbered list items (likely table-of-contents)
        if re.match(r"^\d+\.\s", s) and len(s) < 60:
            continue
        # Clean markdown noise from this paragraph
        cleaned = _clean_markdown_noise(s)
        if not cleaned or len(cleaned) < 20:
            continue
        # Skip if mostly Korean (>50%): caller will use fallback
        if _korean_ratio(cleaned) > 0.5:
            continue
        # Must have at least 2 meaningful English words
        en_words = re.findall(r"[A-Za-z]{3,}", cleaned)
        if len(en_words) < 2:
            continue
        return cleaned[:max_len]
    return ""


def _extract_stat(s: str) -> str:
    """Return a short stat string ("180", "5%", "v1.5.3") or empty."""
    if not s:
        return ""
    # Try version number pattern first (e.g. v1.5.3)
    m_ver = re.search(r"v?\d+\.\d+(?:\.\d+)?", s)
    if m_ver and len(m_ver.group(0)) <= 8:
        return m_ver.group(0)
    m = NUMBER_PCT_RE.search(s)
    if not m:
        return ""
    val = re.sub(r"\s+", "", m.group("v")).strip()
    return val[:8]


def _category_default_stat(category: str) -> tuple[str, str]:
    cat = (category or "").lower()
    if any(k in cat for k in ("incident", "post-mortem", "outage")):
        return ("P1", "SEVERITY")
    if any(k in cat for k in ("kubernetes", "k8s")):
        return ("k8s", "CLUSTER")
    if any(k in cat for k in ("cloud", "aws")):
        return ("AWS", "CLOUD")
    if any(k in cat for k in ("finops", "cost")):
        return ("SAVE", "BUDGET")
    if any(k in cat for k in ("devsecops",)):
        return ("CI", "PIPELINE")
    if any(k in cat for k in ("devops",)):
        return ("OPS", "STACK")
    if any(k in cat for k in ("security",)):
        return ("CVE", "RISK")
    return ("READ", "GUIDE")


# Per-band stat labels by category (band index 0/1/2)
_BAND_STAT_LABELS: dict[str, list[str]] = {
    "incident":    ["SEVERITY", "IMPACT",  "STATUS"],
    "post-mortem": ["SEVERITY", "IMPACT",  "STATUS"],
    "outage":      ["SEVERITY", "DURATION","STATUS"],
    "kubernetes":  ["CLUSTER",  "NODES",   "PODS"],
    "k8s":         ["CLUSTER",  "NODES",   "PODS"],
    "cloud":       ["CLOUD",    "REGIONS", "SERVICES"],
    "aws":         ["CLOUD",    "REGIONS", "SERVICES"],
    "finops":      ["BUDGET",   "SAVINGS", "USAGE"],
    "cost":        ["BUDGET",   "SAVINGS", "USAGE"],
    "devsecops":   ["PIPELINE", "CHECKS",  "GATES"],
    "devops":      ["STACK",    "BUILDS",  "DEPLOYS"],
    "security":    ["RISK",     "ALERT",   "CVE"],
}

_BAND_MICROS: list[list[str]] = [
    ["first look", "initial scan", "first hit"],
    ["deep dive",  "core analysis","root cause"],
    ["playbook",   "action items", "next steps"],
]


def _band_stat_label(category: str, band_idx: int) -> str:
    """Return a meaningful stat_label for the given category and band index."""
    cat = (category or "").lower()
    for key, labels in _BAND_STAT_LABELS.items():
        if key in cat:
            return labels[band_idx % len(labels)]
    return ["GUIDE", "FOCUS", "ACTION"][band_idx % 3]


def _band_micro(band_idx: int, h2_text: str) -> str:
    """Return a meaningful micro caption for the band."""
    # If H2 starts with a number, keep a "part N" style but use meaningful words
    m = re.match(r"^\s*(\d+)\.", h2_text)
    if m:
        n = int(m.group(1))
        pool = _BAND_MICROS[(n - 1) % len(_BAND_MICROS)]
        return pool[band_idx % len(pool)]
    pool = _BAND_MICROS[band_idx % len(_BAND_MICROS)]
    return pool[0]


def _truncate_label(text: str, max_len: int = 16) -> str:
    """Truncate label at word boundary. No ellipsis - just clean cut."""
    if len(text) <= max_len:
        return text
    # Try to cut at word boundary
    cut = text[:max_len]
    boundary = cut.rfind(" ")
    if boundary > max_len // 2:
        return cut[:boundary].rstrip()
    # No good boundary - use first 1-2 words
    words = text.split()
    result = words[0] if words else cut
    if len(words) > 1 and len(result) + 1 + len(words[1]) <= max_len:
        result = result + " " + words[1]
    return result


def _label_from_h2(h2_text: str, idx: int) -> str:
    """Generate a short uppercase label from an H2 heading (English-first)."""
    s = to_english(h2_text, max_len=40)
    # Strip leading numeric prefixes ("1. ", "2. ", "3)")
    s = re.sub(r"^\d+[\.\)\s]+", "", s).strip()
    if not s:
        return ["OVERVIEW", "ANALYSIS", "ACTION"][idx % 3]
    parts = s.split()
    # Filter out tiny filler words but keep all-caps acronyms and meaningful words
    filtered = [p for p in parts if len(p) > 2 or p.isupper()]
    if not filtered:
        filtered = parts
    # Use first 1-2 meaningful words
    label = " ".join(filtered[:2]).upper()
    return _truncate_label(label, max_len=16)


def _theme_for_category(category: str) -> str:
    cat = (category or "").lower()
    for key, theme_name in CATEGORY_DEFAULT_THEME.items():
        if key in cat:
            return theme_name
    return "rose"


def _band_categories_for(category: str) -> list[str]:
    """Return three band categories that drive illustration variety.

    The first band uses the post's category; the other two rotate
    through related illustrations to avoid 3 identical icons.
    """
    cat = (category or "").lower()
    if any(k in cat for k in ("incident", "post-mortem", "outage")):
        return ["incident", "security", "devops"]
    if any(k in cat for k in ("kubernetes", "k8s")):
        return ["kubernetes", "devops", "security"]
    if any(k in cat for k in ("aws", "cloud")):
        return ["cloud", "security", "finops"]
    if "finops" in cat:
        return ["finops", "cloud", "devops"]
    if "devsecops" in cat:
        return ["devsecops", "security", "kubernetes"]
    if "devops" in cat:
        return ["devops", "kubernetes", "security"]
    # default = security
    return ["security", "devsecops", "incident"]


def _split_into_h2_chunks(body: str) -> list[tuple[str, str]]:
    matches = list(H2_RE.finditer(body))
    if not matches:
        return []
    chunks: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        heading = m.group(1).strip()
        content = body[start:end].strip()
        if len(content) < 40 and i + 1 < len(matches):
            continue
        chunks.append((heading, content))
    return chunks


def _is_boilerplate(heading: str) -> bool:
    low = heading.lower().strip()
    boilerplate = (
        "executive summary",
        "summary",
        "table of contents",
        "toc",
        "appendix",
        "references",
        "footnotes",
        "license",
        "credits",
        "faq",
        "additional resources",
        "further reading",
    )
    if any(b in low for b in boilerplate):
        return True
    # Korean-only boilerplate
    ko_boilerplate = (
        "경영진 요약",
        "요약",
        "참고 자료",
        "참고자료",
        "참고문헌",
        "관련 글",
        "맺음말",
        "결론",
        "마치며",
        "목차",
        "빠른 참조",
        "들어가며",
        "서론",
    )
    return any(b in heading for b in ko_boilerplate)


def _filter_useful_h2s(chunks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out = [(h, c) for h, c in chunks if not _is_boilerplate(h)]
    return out or chunks


def _extract_stat_from_body(body_chunk: str) -> str:
    """Extract a meaningful stat from body text (numbers, versions, percentages).

    Searches first 500 chars of body for the most meaningful numeric token.
    Priority: percentage > version > large count > small number.
    """
    sample = _clean_markdown_noise(body_chunk[:600])
    if not sample:
        return ""
    # Version pattern (v1.5.3, 1.53.0)
    m_ver = re.search(r"\bv?\d+\.\d+(?:\.\d+)?\b", sample)
    if m_ver and len(m_ver.group(0)) <= 8:
        return m_ver.group(0)
    # CVE pattern
    m_cve = re.search(r"CVE-\d{4}-\d{4,7}", sample)
    if m_cve:
        return m_cve.group(0)[-9:]  # last 9 chars to fit
    # Percentage
    m_pct = re.search(r"[+-]?\d{1,3}(?:\.\d+)?%", sample)
    if m_pct:
        return m_pct.group(0)[:8]
    # Large counts (100+)
    m_big = re.search(r"\b(\d{3,})\b", sample)
    if m_big:
        return m_big.group(1)[:6]
    return ""


def _headline_strip_prefix(h2_text: str) -> str:
    """Remove numeric prefix from H2 text: '1. Foo' -> 'Foo'."""
    return re.sub(r"^\s*\d+[\.\)\s]+\s*", "", h2_text).strip()


def _english_word_count(text: str) -> int:
    """Count meaningful English words (3+ chars) in text."""
    return len(re.findall(r"[A-Za-z]{3,}", text))


def _band_from_h2(
    idx: int,
    h2_text: str,
    body_chunk: str,
    category: str,
    default_stat: tuple[str, str],
    fallback_headline: str,
    image_alt_chunks: list[str] | None = None,
) -> dict[str, Any]:
    """Build a band dict from an H2 section."""
    # --- Headline ---
    h2_stripped = _headline_strip_prefix(h2_text)
    head_en = to_english(h2_stripped, max_len=58)
    # Require at least 2 meaningful English words; otherwise use alt/fallback
    if _english_word_count(head_en) < 2:
        # Try image_alt chunk at same index
        if image_alt_chunks and idx < len(image_alt_chunks):
            head_en = sanitize_ascii(image_alt_chunks[idx], max_len=58)
        if _english_word_count(head_en) < 2:
            head_en = fallback_headline
    head_clean = head_en or fallback_headline

    # Truncate headline at word boundary
    if len(head_clean) > 50:
        cut = head_clean[:50]
        boundary = cut.rfind(" ")
        if boundary > 25:
            head_clean = cut[:boundary]
        else:
            head_clean = cut

    # --- Body: cleaned English paragraph ---
    body_clean = _first_paragraph(body_chunk, max_len=120)
    if not body_clean:
        # Fallback: try transliteration of paragraphs
        paragraphs = PARA_BREAK_RE.split(body_chunk.strip())
        for p in paragraphs:
            s = p.strip()
            if not s or len(s) < 10:
                continue
            if s.startswith(("```", ">", "{%", "<", "|", "#", "![", "[!", "[Mermaid")):
                continue
            cleaned = _clean_markdown_noise(s)
            if not cleaned or len(cleaned) < 10:
                continue
            translated = to_english(cleaned, max_len=100)
            # Require at least 4 meaningful English words after transliteration
            if _english_word_count(translated) >= 4:
                body_clean = translated
                break
    # Final fallback: derive from headline or image_alt chunk
    if not body_clean or _english_word_count(body_clean) < 4:
        if image_alt_chunks and idx < len(image_alt_chunks):
            candidate = sanitize_ascii(image_alt_chunks[idx], max_len=100)
            if _english_word_count(candidate) >= 2:
                body_clean = candidate
    if not body_clean or _english_word_count(body_clean) < 2:
        body_clean = "Deep dive in the linked post."

    # --- Caption: second distinct English paragraph ---
    caption_clean = ""
    paragraphs = PARA_BREAK_RE.split(body_chunk.strip())
    used_body = False
    for cand in paragraphs:
        s = cand.strip()
        if not s or len(s) < 15:
            continue
        if s.startswith(("```", ">", "{%", "<", "|", "#", "![", "[!", "[Mermaid", "[ ", ":")):
            continue
        if re.match(r"^[\[\]\(\)\:\-\s]*$", s):
            continue
        cleaned_c = _clean_markdown_noise(s)
        if not cleaned_c or len(cleaned_c) < 15:
            continue
        if _korean_ratio(cleaned_c) > 0.5:
            continue
        en_words = re.findall(r"[A-Za-z]{3,}", cleaned_c)
        if len(en_words) < 2:
            continue
        if not used_body:
            used_body = True
            continue  # skip first usable paragraph (already used as body)
        cap = sanitize_ascii(cleaned_c, max_len=80)
        if cap and cap != body_clean:
            caption_clean = cap
            break

    # --- Stat: hierarchical extraction ---
    # 1. From H2 text itself
    stat_val = _extract_stat(h2_text)
    # 2. From body chunk (first 600 chars)
    if not stat_val:
        stat_val = _extract_stat_from_body(body_chunk)
    # 3. Default from category
    if not stat_val:
        stat_val = default_stat[0]

    # --- Stat label: meaningful by category and band index ---
    stat_label = _band_stat_label(category, idx)
    # Override based on stat_val content
    if "%" in stat_val:
        stat_label = "DELTA"
    elif stat_val.upper().startswith("CVE"):
        stat_label = "CVE"
    elif stat_val.startswith("v") or re.match(r"\d+\.\d+", stat_val):
        stat_label = "VERSION"
    elif stat_val.replace(".", "").isdigit():
        n_int = int(stat_val) if stat_val.isdigit() else 0
        if n_int >= 100:
            stat_label = "COUNT"
        # else keep category-derived label

    # --- Micro caption ---
    micro = _band_micro(idx, h2_text)

    return {
        "label": _label_from_h2(h2_text, idx),
        "headline": head_clean,
        "body": body_clean,
        "caption": caption_clean,
        "stat_value": stat_val,
        "stat_label": stat_label,
        "micro": micro,
        "category": category,
        "theme": "",  # filled by caller
    }


def _stem_to_phrase(stem: str) -> str:
    """Turn '2025-09-17-NPM_Shai-Hulud_180_Large-scale_Analysis' into a
    short English phrase."""
    s = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _split_alt_into_chunks(alt: str) -> list[str]:
    """Split an image_alt string into 2-4 chunks for headlines."""
    # Prefer split at colon
    if ":" in alt:
        head, _, rest = alt.partition(":")
        chunks = [head.strip()]
        # Split tail on commas / 'and' / 'with'
        tail_parts = re.split(r",|\sand\s|\swith\s|\sto\s|\sfrom\s", rest)
        chunks.extend(p.strip() for p in tail_parts if p.strip())
        return chunks[:4]
    # Else split on commas
    return [p.strip() for p in alt.split(",") if p.strip()]


def derive_l25_config(post_path: Path) -> dict[str, Any]:
    text = post_path.read_text(encoding="utf-8")
    fm, body = _parse_front_matter(text)

    title = str(fm.get("title", post_path.stem))
    image_alt = str(fm.get("image_alt", "")).strip()
    excerpt = str(fm.get("excerpt", "") or fm.get("description", ""))
    category_value = fm.get("category", "") or fm.get("categories", "")
    if isinstance(category_value, list):
        category = ", ".join(category_value)
    else:
        category = str(category_value)

    theme = _theme_for_category(category)
    default_stat = _category_default_stat(category)

    # Compute fallback headline pool from image_alt then stem
    fallback_pool: list[str] = []
    if image_alt:
        fallback_pool.extend(_split_alt_into_chunks(image_alt))
    stem_phrase = _stem_to_phrase(post_path.stem)
    if stem_phrase:
        fallback_pool.append(stem_phrase)
    fallback_pool = [sanitize_ascii(x, max_len=58) for x in fallback_pool if x]
    fallback_pool = [x for x in fallback_pool if x]

    # Primary headline from image_alt (or stem)
    if image_alt:
        primary_head = sanitize_ascii(image_alt, max_len=58)
    else:
        primary_head = sanitize_ascii(stem_phrase, max_len=58)

    h2_chunks = _filter_useful_h2s(_split_into_h2_chunks(body))

    # Choose per-band illustration variety: pick 3 illustrations whose
    # primary slot matches the post category, then rotate through siblings.
    band_categories = _band_categories_for(category)

    # Build image_alt chunk list for fallback headlines per band
    alt_chunks = _split_alt_into_chunks(image_alt) if image_alt else []

    bands: list[dict[str, Any]] = []
    fallback_iter = iter(fallback_pool[1:])  # skip first since we may use as primary
    for i, (heading, content) in enumerate(h2_chunks[:3]):
        fb = next(fallback_iter, primary_head)
        b = _band_from_h2(i, heading, content, category, default_stat, fb,
                          image_alt_chunks=alt_chunks)
        b["theme"] = theme
        b["category"] = band_categories[i]
        # If headline ends up empty/numeric-only, use fallback
        if not re.search(r"[A-Za-z]{2,}", b["headline"]):
            b["headline"] = fb or primary_head
        bands.append(b)

    # Pad with synthetic bands when fewer than 3
    while len(bands) < 3:
        idx = len(bands)
        if fallback_pool:
            head = fallback_pool[idx % len(fallback_pool)]
        else:
            head = primary_head or sanitize_ascii(title, max_len=58)
        band_cat = band_categories[idx]
        if idx == 0:
            band = {
                "label": "OVERVIEW",
                "headline": head,
                "body": sanitize_ascii(excerpt, max_len=58)
                        or "Quick map of what this post covers.",
                "caption": "Read the full post for the deep-dive details.",
                "stat_value": default_stat[0],
                "stat_label": default_stat[1],
                "micro": "overview",
                "category": band_cat,
                "theme": theme,
            }
        elif idx == 1:
            band = {
                "label": "WHY IT MATTERS",
                "headline": head,
                "body": "Practical context, threat surface, and risk.",
                "caption": "Mapped to real-world incidents and post-mortems.",
                "stat_value": default_stat[0],
                "stat_label": _band_stat_label(category, 1),
                "micro": "deep dive",
                "category": band_cat,
                "theme": theme,
            }
        else:
            band = {
                "label": "KEY TAKEAWAYS",
                "headline": head or "Action items for the team",
                "body": "Hardening checklist and follow-up tasks.",
                "caption": "Apply, audit, and review on the next cadence.",
                "stat_value": default_stat[0],
                "stat_label": _band_stat_label(category, 2),
                "micro": "playbook",
                "category": band_cat,
                "theme": theme,
            }
        bands.append(band)

    title_english = image_alt or stem_phrase
    aria = f"Cover image for: {sanitize_ascii(title_english, max_len=120)}"
    # Subtitle: prefer English excerpt; if mostly Korean, use image_alt or stem
    excerpt_en = sanitize_ascii(excerpt, max_len=120)
    if not excerpt_en or _english_word_count(excerpt_en) < 3:
        excerpt_en = sanitize_ascii(image_alt or stem_phrase, max_len=120)
    subtitle_clean = excerpt_en

    return {
        "title": title,
        "title_english": title_english,
        "category": category,
        "subtitle": subtitle_clean,
        "bands": bands,
        "aria": aria,
        "url": "",
    }


__all__ = ["derive_l25_config", "to_english"]
