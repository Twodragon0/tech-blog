#!/usr/bin/env python3

from pathlib import Path
import re
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


def _categories_html(categories: list[str]) -> str:
    chips: list[str] = []
    for raw in categories[:3]:
        key = str(raw).strip().lower()
        css, label = CATEGORY_LABEL.get(key, ("tech", str(raw).strip()))
        chips.append(f'<span class="category-tag {css}">{label}</span>')
    return " ".join(chips) if chips else '<span class="category-tag tech">기술</span>'


def _tags_html(tags: list[str]) -> str:
    if not tags:
        return '<span class="tag">요약</span>'
    return " ".join(f'<span class="tag">{t}</span>' for t in tags[:8])


def _highlights_html(excerpt: str) -> str:
    text = re.sub(r"\s+", " ", (excerpt or "").strip())
    text = re.sub(r"\.{2,}|…", " ", text).strip(" .")
    if not text:
        text = "핵심 이슈를 요약했습니다"
    point1 = text[:100].rstrip(" ,.")
    point2 = "실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다"
    point3 = "운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다"
    return (
        f"<li><strong>포인트 1</strong>: {point1}</li> "
        f"<li><strong>포인트 2</strong>: {point2}</li> "
        f"<li><strong>포인트 3</strong>: {point3}</li>"
    )


def _build_include(front: dict[str, Any]) -> str:
    title = str(front.get("title", "최신 기술 동향 요약")).strip()
    categories = _to_list(front.get("categories") or front.get("category"))
    tags = _to_list(front.get("tags"))
    excerpt = str(front.get("excerpt", "")).strip()
    date_value = str(front.get("date", "")).split(" ")[0]
    period = f"{date_value} (24시간)" if date_value else "최근 24시간"
    return (
        "{% include ai-summary-card.html\n"
        f"  title='{_escape_attr(title)}'\n"
        f"  categories_html='{_escape_attr(_categories_html(categories))}'\n"
        f"  tags_html='{_escape_attr(_tags_html(tags))}'\n"
        f"  highlights_html='{_escape_attr(_highlights_html(excerpt))}'\n"
        f"  period='{_escape_attr(period)}'\n"
        "  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'\n"
        "%}"
    )


def _extract_existing_include(body: str) -> str:
    m = re.search(r"\{%\s*include\s+ai-summary-card\.html[\s\S]*?%\}", body)
    return m.group(0) if m else ""


def _remove_summary_heading_section(body: str) -> str:
    pattern = r"\n?##\s+📋\s+포스팅\s+요약\s*\n[\s\S]*?(?=\n##\s+|\Z)"
    return re.sub(pattern, "\n", body)


def _remove_all_includes(body: str) -> str:
    return re.sub(r"\n?\{%\s*include\s+ai-summary-card\.html[\s\S]*?%\}\n?", "\n", body)


def process_post(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return False
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    fm_raw = parts[1]
    body = parts[2]
    front_data = yaml.safe_load(fm_raw)
    front = front_data if isinstance(front_data, dict) else {}

    existing = _extract_existing_include(body)
    include_block = existing if existing else _build_include(front)

    body = _remove_summary_heading_section(body)
    body = _remove_all_includes(body)
    body = body.lstrip("\n")
    body = include_block + "\n\n" + body
    body = re.sub(r"\n{3,}", "\n\n", body)

    new_content = f"---{fm_raw}---\n\n{body}"
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
