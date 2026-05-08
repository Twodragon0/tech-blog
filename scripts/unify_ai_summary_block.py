#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"


CATEGORY_LABEL = {
    "security": ("security", "보안"),
    "devsecops": ("devsecops", "DevSecOps"),
    "devops": ("devops", "DevOps"),
    "cloud": ("cloud", "클라우드"),
    "kubernetes": ("devops", "쿠버네티스"),
    "incident": ("incident", "인시던트"),
    "finops": ("cloud", "FinOps"),
    "tech": ("tech", "기술"),
    "ai": ("tech", "AI"),
    "blockchain": ("tech", "블록체인"),
}


def _to_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        return [x.strip() for x in s.split(",") if x.strip()]
    return []


def _escape_attr(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("'", "&#39;")
        .replace("\n", " ")
        .strip()
    )


def _clean_summary_text(text: str) -> str:
    cleaned = re.sub(r"\.{2,}", ".", text)
    cleaned = cleaned.replace("…", ".")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip()
    return cleaned


def _categories_data(categories: list[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in categories[:3]:
        key = str(raw).strip().lower()
        css, label = CATEGORY_LABEL.get(key, ("tech", str(raw).strip()))
        out.append((css, label))
    return out or [("tech", "기술")]


def _tags_data(tags: list[str]) -> list[str]:
    if not tags:
        return ["요약"]
    return [str(t).strip() for t in tags[:8] if str(t).strip()]


def _highlights_data(excerpt: str, summary_lines: list[str]) -> list[tuple[str, str]]:
    points: list[str] = []
    for line in summary_lines:
        if line:
            points.append(_clean_summary_text(line))
        if len(points) >= 3:
            break

    if not points:
        text = _clean_summary_text(re.sub(r"\s+", " ", (excerpt or "").strip()))
        if not text:
            text = "핵심 이슈를 요약했습니다"
        points.append(text[:120].rstrip(" ,."))

    while len(points) < 3:
        if len(points) == 1:
            points.append("실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다")
        else:
            points.append(
                "운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다"
            )

    return [
        (f"포인트 {idx + 1}", point) for idx, point in enumerate(points[:3])
    ]


def _yaml_escape_dq(text: str) -> str:
    """Escape `\\` and `"` for safe inclusion inside YAML double-quoted scalar."""
    return (text or "").replace("\\", "\\\\").replace('"', '\\"')


def _emit_summary_card_yaml(
    title: str,
    period: str,
    audience: str,
    categories: list[tuple[str, str]],
    tags: list[str],
    highlights: list[tuple[str, str]],
) -> str:
    """Mirror scripts/news/content_generator._emit_summary_card_yaml.

    Kept locally to avoid a cross-package import at module load time.
    """
    def esc(s: str) -> str:
        return _yaml_escape_dq(s)

    lines: list[str] = ["summary_card:"]
    lines.append(f'  title: "{esc(title)}"')
    if period:
        lines.append(f'  period: "{esc(period)}"')
    if audience:
        lines.append(f'  audience: "{esc(audience)}"')
    if categories:
        lines.append("  categories:")
        for cls, label in categories:
            lines.append(f'    - {{ class: "{esc(cls)}", label: "{esc(label)}" }}')
    else:
        lines.append("  categories: []")
    if tags:
        lines.append("  tags:")
        for t in tags:
            lines.append(f'    - "{esc(t)}"')
    else:
        lines.append("  tags: []")
    if highlights:
        lines.append("  highlights:")
        for src, ttl in highlights:
            lines.append(f'    - {{ source: "{esc(src)}", title: "{esc(ttl)}" }}')
    else:
        lines.append("  highlights: []")
    return "\n".join(lines)


def _build_summary_card_yaml(front: dict[str, Any], summary_lines: list[str]) -> str:
    """Build the `summary_card:` YAML block for injection into frontmatter."""
    title = str(front.get("title", "최신 기술 동향 요약")).strip()
    categories = _to_list(front.get("categories") or front.get("category"))
    tags = _to_list(front.get("tags"))
    excerpt = str(front.get("excerpt", "")).strip()
    date_value = str(front.get("date", "")).split(" ")[0]
    period = f"{date_value} (24시간)" if date_value else "최근 24시간"
    return _emit_summary_card_yaml(
        title=title,
        period=period,
        audience="보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자",
        categories=_categories_data(categories),
        tags=_tags_data(tags),
        highlights=_highlights_data(excerpt, summary_lines),
    )


def _extract_summary_lines(body: str) -> list[str]:
    lines = body.splitlines()
    in_summary = False
    collected: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if in_summary:
                break
            in_summary = line.startswith("## 핵심 요약") or line.startswith(
                "## Executive Summary"
            )
            continue

        if not in_summary:
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("|"):
            break
        if stripped.startswith("- "):
            continue
        if stripped.startswith(">"):
            continue

        cleaned = _clean_summary_text(stripped)
        if cleaned:
            collected.append(cleaned)
        if len(collected) >= 3:
            break

    return collected


def _normalize_summary_section(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    in_summary = False
    for line in lines:
        if line.startswith("## "):
            in_summary = line.startswith("## 핵심 요약") or line.startswith(
                "## Executive Summary"
            )
            out.append(line)
            continue

        if in_summary and line.strip() and not line.strip().startswith("|"):
            cleaned_line = _clean_summary_text(line)
            out.append(cleaned_line)
            continue

        out.append(line)

    return "\n".join(out)


def _extract_existing_include(body: str) -> str:
    m = re.search(r"\{%\s*include\s+ai-summary-card\.html[\s\S]*?%\}", body)
    return m.group(0) if m else ""


def _remove_summary_heading_section(body: str) -> str:
    pattern = r"\n?##\s+📋\s+포스팅\s+요약\s*\n[\s\S]*?(?=\n##\s+|\Z)"
    return re.sub(pattern, "\n", body)


def _remove_all_includes(body: str) -> str:
    return re.sub(r"\n?\{%\s*include\s+ai-summary-card\.html[\s\S]*?%\}\n?", "\n", body)


_SUMMARY_CARD_BLOCK_RE = re.compile(
    r"\nsummary_card:\s*\n(?:[ \t].*\n|\n)*",
)


def _replace_or_append_summary_card(fm_raw: str, sc_yaml: str) -> str:
    """Replace existing summary_card block in fm_raw with sc_yaml, else append.

    fm_raw is the inner frontmatter text (between the leading and trailing
    `---\\n` fences) — i.e. parts[1] from `content.split("---", 2)`.
    """
    sc_block = "\n" + sc_yaml + "\n"
    if _SUMMARY_CARD_BLOCK_RE.search(fm_raw):
        return _SUMMARY_CARD_BLOCK_RE.sub(sc_block, fm_raw, count=1)
    # Append before the trailing newline so the closing fence stays on its
    # own line.
    if fm_raw.endswith("\n"):
        return fm_raw + sc_yaml + "\n"
    return fm_raw + "\n" + sc_yaml + "\n"


def process_post(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return False
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    fm_raw = parts[1]
    body = parts[2]

    # Idempotency guard (post-2026-05-08): once a post carries a
    # `summary_card:` block (from content_generator.py or
    # migrate_summary_cards_to_frontmatter.py), this script must not touch
    # it. The structured highlights from those sources are richer than the
    # synthetic "포인트 N" placeholders this normalizer would emit, and a
    # blind rewrite would clobber the curated source/title pairs.
    if re.search(r"^summary_card:\s*$", fm_raw, re.MULTILINE):
        return False

    front_data = yaml.safe_load(fm_raw)
    front = front_data if isinstance(front_data, dict) else {}

    body = _normalize_summary_section(body)
    summary_lines = _extract_summary_lines(body)
    sc_yaml = _build_summary_card_yaml(front, summary_lines)

    body = _remove_summary_heading_section(body)
    body = _remove_all_includes(body)
    body = body.lstrip("\n")
    body = "{% include ai-summary-card.html %}\n\n" + body
    body = re.sub(r"\n{3,}", "\n\n", body)

    new_fm_raw = _replace_or_append_summary_card(fm_raw, sc_yaml)
    new_content = f"---{new_fm_raw}---\n\n{body}"
    if new_content != content:
        _ = path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    files = sorted(POSTS_DIR.glob("*.md"))
    for file_path in files:
        if process_post(file_path):
            changed += 1
    print(f"summary_unified={changed} total={len(files)}")


if __name__ == "__main__":
    main()
