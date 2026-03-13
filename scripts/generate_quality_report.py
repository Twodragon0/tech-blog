#!/usr/bin/env python3
"""
월간 품질 리포트 생성 스크립트.
validate_post_quality.py를 호출하여 대시보드를 수집하고
/tmp/quality-report.md에 이슈 본문을 작성합니다.

GitHub Actions monthly-quality-report.yml에서 사용됩니다.
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


VALIDATOR = Path(__file__).parent / "validate_post_quality.py"
POSTS_DIR = Path(__file__).parent.parent / "_posts"
OUTPUT_FILE = Path("/tmp/quality-report.md")


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
    current_scores = run_validator("--summary", *current_posts) if current_posts else "No posts this month"

    prev_posts = get_posts_for_month(prev_month)
    prev_count = len(prev_posts)
    prev_scores = run_validator("--summary", *prev_posts) if prev_posts else "No posts last month"

    # Below 80
    below_80_output = run_validator("--warn-below", "80", "--quiet", *all_posts)
    below_80_count = below_80_output.count("WARNING")

    # Build issue body
    body = f"""## 월간 포스트 품질 리포트

**보고 기간**: {current_month}
**총 포스트**: {total_count}개

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

### 조치 사항

- [ ] 80점 미만 포스트 품질 개선
- [ ] 신규 포스트 품질 기준 준수 확인
- [ ] Front matter 크기 최적화
"""

    OUTPUT_FILE.write_text(body, encoding="utf-8")
    print(f"\nReport written to {OUTPUT_FILE} ({len(body)} chars)")


if __name__ == "__main__":
    main()
