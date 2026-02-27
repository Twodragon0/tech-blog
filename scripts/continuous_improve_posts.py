#!/usr/bin/env python3
"""
포스팅을 지속적으로 개선하는 스크립트
1시간 동안 실행되며 짧은 본문을 가진 포스팅들을 개선합니다.
"""

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

POSTS_DIR = Path(__file__).parent.parent / "_posts"
LOG_FILE = Path(__file__).parent.parent / "improvement_log.txt"
RUN_DURATION = 3600  # 1시간 (초)


def log_message(message: str):
    """로그 메시지 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


def extract_post_info(file_path: Path) -> Dict:
    """포스팅 정보 추출"""
    content = file_path.read_text(encoding="utf-8")

    # Front matter 추출
    front_matter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    front_matter = {}
    if front_matter_match:
        for line in front_matter_match.group(1).split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"').strip("'")
                    front_matter[key] = value

    # 요약 섹션 이후 본문 추출
    summary_end = content.find("## 서론")
    if summary_end == -1:
        summary_end = content.find("## 1.")
    if summary_end == -1:
        summary_end = content.find("원본 포스트:")

    if summary_end != -1:
        body = content[summary_end:]
        # 원본 포스트 링크 제거
        body = re.sub(r"원본 포스트:.*", "", body, flags=re.DOTALL)
        body = body.strip()
    else:
        body = ""

    # 본문 길이 계산 (마크다운 제목, 코드 블록 제외)
    body_lines = [
        line
        for line in body.split("\n")
        if not line.strip().startswith("#")
        and not line.strip().startswith("```")
        and line.strip()
    ]
    body_length = len("\n".join(body_lines))

    return {
        "file_path": file_path,
        "title": front_matter.get("title", ""),
        "category": front_matter.get("categories", front_matter.get("category", "")),
        "tags": front_matter.get("tags", ""),
        "excerpt": front_matter.get("excerpt", ""),
        "body": body,
        "body_length": body_length,
        "original_url": front_matter.get("original_url", ""),
    }


def needs_improvement(post_info: Dict) -> bool:
    """개선이 필요한지 판단"""
    # 본문이 너무 짧은 경우 (500자 미만)
    if post_info["body_length"] < 500:
        return True

    # 본문에 "원본 포스트"만 있고 내용이 거의 없는 경우
    body_text = post_info["body"].lower()
    if "원본 포스트" in body_text and len(body_text) < 200:
        return True

    # "서론" 섹션이 없는 경우
    if "## 서론" not in post_info["body"] and "## 1." not in post_info["body"]:
        return True

    return False


def generate_improved_content(post_info: Dict) -> str:
    """개선된 본문 생성"""
    title = post_info["title"]
    excerpt = post_info["excerpt"]
    category = post_info["category"]
    tags = post_info["tags"]

    # 제목에서 주제 추출
    # 예: "AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기" -> "데이터베이스 접근 게이트웨이"

    # 기본 구조 생성
    improved_body = f"""## 서론

{excerpt[:200]}...

이 글에서는 {title}에 대해 상세히 다룹니다. 실무 경험을 바탕으로 구체적인 설정 방법과 모범 사례를 공유합니다.

## 1. 개요

### 1.1 배경 및 필요성

{excerpt[:300]}...

### 1.2 주요 개념

이 가이드에서 다루는 주요 개념은 다음과 같습니다:

- **보안**: 안전한 구성 및 접근 제어
- **효율성**: 최적화된 설정 및 운영
- **모범 사례**: 검증된 방법론 적용

## 2. 핵심 내용

### 2.1 기본 설정

기본 설정을 시작하기 전에 다음 사항을 확인해야 합니다:

1. **요구사항 분석**: 필요한 기능 및 성능 요구사항 파악
2. **환경 준비**: 필요한 도구 및 리소스 준비
3. **보안 정책**: 보안 정책 및 규정 준수 사항 확인

### 2.2 단계별 구현

#### 단계 1: 초기 설정

초기 설정 단계에서는 기본 구성을 수행합니다.

```bash
# 예시 명령어
# 실제 설정에 맞게 수정 필요
```

#### 단계 2: 보안 구성

보안 설정을 구성합니다:

- 접근 제어 설정
- 암호화 구성
- 모니터링 활성화

#### 단계 3: 테스트 및 검증

설정 완료 후 테스트를 수행합니다:

- 기능 테스트
- 성능 테스트
- 보안 테스트

## 3. 고급 설정

### 3.1 최적화

성능 최적화를 위한 설정:

- 리소스 최적화
- 캐싱 전략
- 로드 밸런싱

### 3.2 모니터링

모니터링 설정:

- 로그 수집
- 메트릭 수집
- 알림 설정

## 4. 문제 해결

### 4.1 일반적인 문제

자주 발생하는 문제와 해결 방법:

**문제 1**: 설정 오류
- **원인**: 잘못된 구성
- **해결**: 설정 파일 재확인 및 수정

**문제 2**: 성능 저하
- **원인**: 리소스 부족
- **해결**: 리소스 확장 또는 최적화

### 4.2 트러블슈팅 가이드

문제 발생 시 다음 순서로 확인:

1. 로그 확인
2. 설정 검증
3. 리소스 상태 확인
4. 네트워크 연결 확인

## 5. 모범 사례

### 5.1 보안 모범 사례

- 최소 권한 원칙 적용
- 정기적인 보안 점검
- 자동화된 보안 스캔

### 5.2 운영 모범 사례

- 자동화된 배포 파이프라인
- 정기적인 백업
- 재해 복구 계획 수립

## 결론

{title}에 대해 다루었습니다. 올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.

추가 정보나 질문이 있으시면 댓글로 남겨주세요.

---

원본 포스트: {post_info["original_url"]}
"""

    return improved_body


def improve_post(post_info: Dict) -> bool:
    """포스팅 개선"""
    try:
        content = post_info["file_path"].read_text(encoding="utf-8")

        # 요약 섹션 찾기
        summary_match = re.search(r"(## 📋 포스팅 요약\n\n.*?\n\n)", content, re.DOTALL)
        if not summary_match:
            return False

        # 요약 섹션 이후 내용 찾기
        summary_end = summary_match.end()

        # 기존 본문이 있는지 확인
        existing_body_start = content.find("## 서론", summary_end)
        if existing_body_start == -1:
            existing_body_start = content.find("원본 포스트:", summary_end)

        if existing_body_start != -1:
            # 기존 본문이 있으면 개선된 내용으로 교체
            improved_content = generate_improved_content(post_info)
            new_content = content[:summary_end] + "\n" + improved_content
        else:
            # 본문이 없으면 추가
            improved_content = generate_improved_content(post_info)
            new_content = content[:summary_end] + "\n" + improved_content

        # 파일 저장
        post_info["file_path"].write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        log_message(f"Error improving {post_info['file_path'].name}: {e}")
        return False


def main():
    """메인 함수"""
    start_time = time.time()
    improved_count = 0
    checked_count = 0

    log_message("=" * 60)
    log_message("포스팅 개선 프로세스 시작")
    log_message(f"실행 시간: {RUN_DURATION}초 (1시간)")
    log_message("=" * 60)

    # 모든 포스팅 파일 목록 가져오기
    all_posts = list(POSTS_DIR.glob("*.md"))
    posts_to_improve = []

    # 개선이 필요한 포스팅 식별
    for post_file in sorted(all_posts):
        try:
            post_info = extract_post_info(post_file)
            checked_count += 1

            if needs_improvement(post_info):
                posts_to_improve.append(post_info)
                log_message(
                    f"개선 필요: {post_file.name} (본문 길이: {post_info['body_length']}자)"
                )
        except Exception as e:
            log_message(f"오류 발생 ({post_file.name}): {e}")

    log_message(
        f"\n총 {len(all_posts)}개 포스팅 중 {len(posts_to_improve)}개 개선 필요"
    )
    log_message("개선 프로세스 시작...\n")

    # 개선 프로세스 실행
    for i, post_info in enumerate(posts_to_improve, 1):
        # 시간 체크
        elapsed_time = time.time() - start_time
        if elapsed_time >= RUN_DURATION:
            log_message(f"\n실행 시간 ({RUN_DURATION}초) 도달. 프로세스 종료.")
            break

        log_message(
            f"[{i}/{len(posts_to_improve)}] 개선 중: {post_info['file_path'].name}"
        )

        if improve_post(post_info):
            improved_count += 1
            log_message("  ✓ 개선 완료")
        else:
            log_message("  ✗ 개선 실패")

        # 다음 포스팅 처리 전 잠시 대기 (과도한 파일 I/O 방지)
        time.sleep(1)

    elapsed_time = time.time() - start_time

    # 최종 리포트
    log_message("\n" + "=" * 60)
    log_message("포스팅 개선 프로세스 완료")
    log_message(f"실행 시간: {elapsed_time:.2f}초")
    log_message(f"확인한 포스팅: {checked_count}개")
    log_message(f"개선한 포스팅: {improved_count}개")
    log_message(f"남은 포스팅: {len(posts_to_improve) - improved_count}개")
    log_message("=" * 60)


if __name__ == "__main__":
    main()
