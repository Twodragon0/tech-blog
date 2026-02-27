#!/usr/bin/env python3

import re
from pathlib import Path

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


def _to_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        return [x.strip() for x in s.split(",") if x.strip()]
    return []


def _normalize_title(title: str) -> str:
    t = (title or "").strip()
    t = t.replace("Tech Blog Weekly Digest", "기술 블로그 주간 다이제스트")
    t = t.replace("Tech & Security Weekly Digest", "기술·보안 주간 다이제스트")
    t = t.replace("Tech Security Weekly Digest", "기술·보안 주간 다이제스트")
    return t


def _escape_attr(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("'", "&#39;")
        .replace("\n", " ")
        .strip()
    )


def _build_categories_html(categories):
    chips = []
    for raw in categories[:3]:
        key = str(raw).strip().lower()
        css, label = CATEGORY_LABEL.get(key, ("tech", str(raw).strip()))
        chips.append(f'<span class="category-tag {css}">{label}</span>')
    return " ".join(chips) if chips else '<span class="category-tag tech">기술</span>'


def _build_tags_html(tags):
    if not tags:
        return '<span class="tag">요약</span>'
    return "\n      ".join(f'<span class="tag">{t}</span>' for t in tags[:8])


def _build_highlights_html(excerpt: str):
    text = re.sub(r"\s+", " ", (excerpt or "").strip())
    text = re.sub(r"\.{2,}|…", " ", text)
    text = text.replace("핵심 요약(원문 기반):", "")
    text = text.replace("원문 제목 기반:", "")
    text = re.sub(r"\s+", " ", text).strip(" .")
    if not text:
        return "<li><strong>핵심</strong>: 주요 내용을 요약했습니다.</li>"
    chunks = [c.strip(" .") for c in re.split(r"[;]| - |,", text) if c.strip()]
    base = chunks[0] if chunks else text
    if len(base) > 120:
        base = base[:120].rstrip(" ,.")

    points = [
        f"핵심 주제는 {base} 입니다",
        "실무 관점에서 영향 범위와 우선순위를 함께 검토해야 합니다",
        "팀 운영에서는 재현 가능한 적용 절차와 검증 기준을 문서화해야 합니다",
    ]

    lis = []
    for i, p in enumerate(points, start=1):
        lis.append(f"<li><strong>포인트 {i}</strong>: {p}</li>")
    return "\n      ".join(lis)


def _replace_summary_section(body: str, include_block: str) -> str:
    heading = "## 📋 포스팅 요약"
    idx = body.find(heading)
    if idx == -1:
        return include_block + "\n\n" + body.lstrip()

    next_heading = re.search(r"\n##\s+", body[idx + len(heading) :])
    if next_heading:
        end = idx + len(heading) + next_heading.start() + 1
    else:
        end = len(body)

    replacement = f"{heading}\n\n{include_block}\n\n"
    return body[:idx] + replacement + body[end:].lstrip("\n")


def normalize_post(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    fm_raw = parts[1]
    body = parts[2].lstrip("\n")
    front = yaml.safe_load(fm_raw) or {}

    title = _normalize_title(str(front.get("title", "")))

    categories = _to_list(front.get("categories") or front.get("category"))
    tags = _to_list(front.get("tags"))
    excerpt = str(front.get("excerpt", ""))
    date_value = str(front.get("date", ""))

    if "Tech Blog Weekly Digest" in body:
        body = body.replace("Tech Blog Weekly Digest", "기술 블로그 주간 다이제스트")
    if "Tech & Security Weekly Digest" in body:
        body = body.replace(
            "Tech & Security Weekly Digest", "기술·보안 주간 다이제스트"
        )
    if "## Executive Summary" in body:
        body = body.replace("## Executive Summary", "## 핵심 요약")

    period = f"{date_value.split(' ')[0]} (24시간)" if date_value else "최근 24시간"
    include_block = (
        "{% include ai-summary-card.html\n"
        f"  title='{_escape_attr(title)}'\n"
        f"  categories_html='{_escape_attr(_build_categories_html(categories))}'\n"
        f"  tags_html='{_escape_attr(_build_tags_html(tags))}'\n"
        f"  highlights_html='{_escape_attr(_build_highlights_html(excerpt))}'\n"
        f"  period='{_escape_attr(period)}'\n"
        "  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'\n"
        "%}"
    )

    body = _replace_summary_section(body, include_block)

    new_content = f"---{fm_raw}---\n\n{body}"

    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    changed = 0
    files = sorted(POSTS_DIR.glob("*.md"))
    for f in files:
        if normalize_post(f):
            changed += 1
    print(f"updated={changed} total={len(files)}")


if __name__ == "__main__":
    main()
