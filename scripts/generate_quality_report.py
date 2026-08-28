#!/usr/bin/env python3
"""
월간 품질 리포트 생성 스크립트.
validate_post_quality.py를 호출하여 대시보드를 수집하고
/tmp/quality-report.md에 이슈 본문을 작성합니다.

GitHub Actions monthly-quality-report.yml에서 사용됩니다.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

VALIDATOR = Path(__file__).parent / "validate_post_quality.py"
POSTS_DIR = Path(__file__).parent.parent / "_posts"
NEWS_DATA = Path(__file__).parent.parent / "_data" / "collected_news.json"
OUTPUT_FILE = Path("/tmp/quality-report.md")


def generate_trend_coverage() -> str:
    """Analyze _TREND_KR_MAP coverage against collected news data."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.news.content_generator import (
            _STOP_WORDS,
            _TECH_PRESERVE,
            _TREND_KR_MAP,
        )
    except ImportError:
        try:
            from news.content_generator import (
                _STOP_WORDS,
                _TECH_PRESERVE,
                _TREND_KR_MAP,
            )
        except ImportError:
            return "⚠️ content_generator.py import 실패"

    if not NEWS_DATA.exists():
        return "⚠️ 뉴스 데이터 없음 (collected_news.json)"

    with open(NEWS_DATA, encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])
    if not items:
        return "⚠️ 뉴스 항목 없음"

    mapped: Counter[str] = Counter()
    unmapped: Counter[str] = Counter()
    total_titles = 0

    for item in items:
        title = item.get("title", "")
        if not title or re.search(r"[가-힣]", title):
            continue
        total_titles += 1
        for w in title.split():
            clean = w.strip(".,;:!?\"'()[]").lower()
            if not clean or len(clean) <= 1:
                continue
            if clean in _STOP_WORDS or clean in _TECH_PRESERVE:
                continue
            if clean in _TREND_KR_MAP:
                mapped[clean] += 1
            else:
                unmapped[clean] += 1

    total = sum(mapped.values()) + sum(unmapped.values())
    coverage = sum(mapped.values()) / total * 100 if total else 0

    top_mapped = ", ".join(f"{w}({c})" for w, c in mapped.most_common(5))
    top_unmapped = ", ".join(f"{w}({c})" for w, c in unmapped.most_common(10))

    return (
        f"| 항목 | 값 |\n|------|----|\n"
        f"| 영문 제목 | {total_titles}건 |\n"
        f"| 매핑 단어 | {len(mapped)}종 ({sum(mapped.values())}회) |\n"
        f"| 미매핑 단어 | {len(unmapped)}종 ({sum(unmapped.values())}회) |\n"
        f"| **커버리지** | **{coverage:.1f}%** |\n\n"
        f"**매핑 상위**: {top_mapped or 'N/A'}\n\n"
        f"**미매핑 상위 (추가 후보)**: {top_unmapped or 'N/A'}"
    )


def run_validator(*args: str) -> str:
    """validate_post_quality.py를 실행하고 stdout을 반환합니다."""
    cmd = [sys.executable, str(VALIDATOR)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return (result.stdout + result.stderr).strip()


def get_posts_for_month(year_month: str) -> list[str]:
    """YYYY-MM 패턴에 맞는 포스트 파일 경로를 반환합니다."""
    posts = sorted(POSTS_DIR.glob(f"{year_month}-*.md"))
    return [str(p) for p in posts]


def main() -> None:
    all_posts = sorted(str(p) for p in POSTS_DIR.glob("*.md"))
    if not all_posts:
        print("No posts found.")
        sys.exit(0)

    total_count = len(all_posts)
    now = datetime.now()
    current_month = now.strftime("%Y-%m")

    # Previous month
    first_of_month = now.replace(day=1)
    prev_date = first_of_month - timedelta(days=1)
    prev_month = prev_date.strftime("%Y-%m")

    # Generate reports
    print(f"Total posts: {total_count}")
    print(f"Current month: {current_month}")
    print(f"Previous month: {prev_month}")

    dashboard = run_validator("--summary", *all_posts)
    print(dashboard)

    current_posts = get_posts_for_month(current_month)
    current_count = len(current_posts)
    current_scores = (
        run_validator("--summary", *current_posts)
        if current_posts
        else "No posts this month"
    )

    prev_posts = get_posts_for_month(prev_month)
    prev_count = len(prev_posts)
    prev_scores = (
        run_validator("--summary", *prev_posts) if prev_posts else "No posts last month"
    )

    # Below 80
    below_80_output = run_validator("--warn-below", "80", "--quiet", *all_posts)
    below_80_count = below_80_output.count("WARNING")

    # Trend coverage
    trend_coverage = generate_trend_coverage()

    # Structural element counts. Read each post once.
    #
    # These are reported as counts and NOT graded. Grading presence turns it into
    # a target: this table used to print "🟢 우수" once mermaid_count passed 30,
    # and in 2026-08 a pipeline raised that number by injecting the same
    # hardcoded diagram into 43 posts. Presence of a diagram is not evidence of
    # a good diagram. See notes/autonomous-modernizer-retro.md.
    #
    # The FAQ row IS graded, because there the target is genuinely a fixed
    # number: FAQ sections are banned outright, so 0 is the only correct value.
    _FAQ_HEADING = re.compile(
        r"^#{1,4}\s*.*(?:자주\s*묻는\s*질문|\bFAQ\b)", re.MULTILINE | re.IGNORECASE
    )
    # A markdown table needs a header row followed by a delimiter row. The old
    # check was `"|" in text`, which matched Liquid tags and inline code and so
    # reported nearly every post.
    _MD_TABLE = re.compile(r"\|.*\|.*\n\|[-:\s|]+\|")

    mermaid_count = checklist_count = table_count = faq_count = 0
    for p in POSTS_DIR.glob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "```mermaid" in text:
            mermaid_count += 1
        if re.search(r"-\s*\[\s*[ xX]?\s*\]", text):
            checklist_count += 1
        if _MD_TABLE.search(text):
            table_count += 1
        if _FAQ_HEADING.search(text) or "schema_type: FAQPage" in text:
            faq_count += 1

    # Build issue body
    body = f"""## 월간 포스트 품질 리포트

**보고 기간**: {current_month}
**총 포스트**: {total_count}개

### 🏗️ 구조 요소 분포

관측값이며 목표치가 아니다. 이 표는 이전에 Mermaid 30개를 넘기면 "🟢 우수"로
표시했고, 2026-08에 한 파이프라인이 동일한 하드코딩 다이어그램을 43개 포스트에
주입해 그 숫자를 올렸다. 다이어그램의 **존재**는 좋은 다이어그램의 근거가 아니다
(`notes/autonomous-modernizer-retro.md`). 숫자가 낮다고 채워 넣지 말 것 —
같은 블록의 반복은 `scripts/check_post_boilerplate.py`가 차단한다.

| 구조 요소 | 포함 포스트 수 | 전체 대비 비율 |
|---|---|---|
| Mermaid 다이어그램 | {mermaid_count}개 | {mermaid_count / total_count * 100:.1f}% |
| 체크리스트 (`- [ ]`) | {checklist_count}개 | {checklist_count / total_count * 100:.1f}% |
| 마크다운 표 | {table_count}개 | {table_count / total_count * 100:.1f}% |

| 금지 항목 | 검출 | 상태 |
|---|---|:---:|
| FAQ 섹션 / `schema_type: FAQPage` | {faq_count}개 | {"🟢 준수 (0건)" if faq_count == 0 else "🔴 제거 필요"} |

### 전체 품질 대시보드

```
{dashboard}
```

### 이번 달 ({current_month}) - {current_count}개 포스트

```
{current_scores}
```

### 지난 달 ({prev_month}) - {prev_count}개 포스트

```
{prev_scores}
```

### 80점 미만 포스트 ({below_80_count}개)

<details>
<summary>상세 보기</summary>

```
{below_80_output if below_80_output.strip() else "All posts are above 80 points!"}
```

</details>

### 트렌드 키워드 커버리지 (_TREND_KR_MAP)

{trend_coverage}

### 조치 사항

- [ ] 80점 미만 포스트 품질 개선 (포스트 고유 내용으로. 고정 블록 주입 금지 — `scripts/check_post_boilerplate.py`가 차단한다)
- [ ] 신규 포스트 품질 기준 준수 확인
- [ ] 미매핑 상위 단어 _TREND_KR_MAP 추가 검토
"""

    OUTPUT_FILE.write_text(body, encoding="utf-8")
    print(f"\nReport written to {OUTPUT_FILE} ({len(body)} chars)")


if __name__ == "__main__":
    main()
