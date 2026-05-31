# Learnings

기술적 발견과 패턴을 기록합니다.

## 2026-02

- Jekyll 빌드 시 한글 파일명은 URL 인코딩 이슈 발생 → 영문 파일명 필수
- SVG 내 한글 텍스트는 일부 브라우저에서 깨짐 → 영문만 사용

## 2026-03-07

### 포스트 품질 검증에서 발견된 패턴
- `verify_images_unified.py --all` 실행 시 포스트에서 참조하는 섹션 배너 SVG가 실제로 존재하는지 확인됨
- 기존 섹션 배너: `section-security.svg`, `section-devops.svg`, `section-ai-ml.svg`, `section-cloud.svg`, `section-blockchain.svg`
- 새 포스트에서 `section-devsecops.svg`, `section-ai.svg` 참조 시 기존 파일명과 불일치 → 신규 생성 필요
- 코드 블록 bare ``` 패턴 중 대부분은 닫는 태그 → `^```$` grep 결과만으로는 opening/closing 구분 불가, 앞뒤 컨텍스트 확인 필수

### 코드 블록 언어 태그 누락 패턴
- 공격 시나리오 (번호 목록) → `text`
- 아키텍처 다이어그램 (화살표/박스) → `text`
- SIEM 탐지 쿼리 (필드 기반) → `splunk` 또는 해당 언어
- 닫는 태그는 항상 bare ``` 이므로 수정 불필요

## 2026-03-17~18

### 자동 생성 포스트 템플릿 품질 개선

**문제**: `auto_publish_news.py`의 `_generate_ai_analysis_template()`과 `_generate_devops_template()`에서 키워드 매칭 실패 시 동일한 generic 3줄이 복붙되어 한 포스트 내 여러 섹션에서 반복됨.

**해결 패턴**:
1. `else` fallback 하나를 세부 키워드 분기로 세분화 (AI: 6→8분기, DevOps: 2→10분기, Blockchain: 2→7분기)
2. `check_posts.py`에 `check_duplicate_practical_points()` 추가하여 동일 bullet 3회+ 반복 자동 감지
3. anti-regression 테스트로 banned phrases 자동 차단 (총 141건 테스트)

**키워드 분기 설계 시 주의사항**:
- 분기 순서가 중요: 구체적 키워드(istio, cosign)를 일반 키워드(network, image)보다 먼저 배치
- `policy`, `container` 같은 광범위 키워드는 다른 분기에 과매칭 → `admission controller`, `pod security`처럼 구체화
- 테스트 입력 작성 시 다른 분기 키워드를 포함하지 않도록 주의 (예: "Container image signing" → `container`가 docker 분기에 매칭)
- `elif` 체인에서 새 분기 추가 시 반드시 기존 테스트 전체 실행하여 우선순위 충돌 확인

**SVG 이미지 품질 개선**:
- `_truncate_text()`: 단어 중간 절단 → `rfind(" ")`로 단어 경계 절단 (60% 임계값)
- SVG `<defs>` 내부와 외부에 동일 `id` 패턴 중복 → 하나만 유지
- `generate_svg_image()` 템플릿에서 소스 레벨 수정으로 향후 자동 생성 시 적용

**CI 통합**:
- `requirements-ci.txt`에 `pytest`, `requests`, `beautifulsoup4` 추가 (news_utils import 체인)
- Jekyll CI에 pytest 스텝 추가 (빌드 전 블로킹 실행)
- `check_posts.py --changed`의 PR diff 감지: `origin/main...HEAD` 비교 추가

**포스트 제목 접두사 제거**:
- 기존 46개 포스트에서 '기술·보안 주간 다이제스트:' 접두사 제거 (커밋 `171ab94`)
- `auto_publish_news.py`의 title/ai-summary-card에서도 접두사 제거 동기화
- `generate_cross_refs()` dead code 90줄 제거 (레이아웃 자동 관련 포스트로 대체)

**로컬 환경**:
- Python 3.14 + `chardet 7.x` → `requests 2.32.5`의 `chardet<6` 요구와 충돌
- 해결: `chardet 5.2.0` 다운그레이드 + `~/.config/pip/constraints.txt`에 `chardet<6` 설정

## 2026-06-01

### L20 side-panel headline cap 설계 교훈

**상황**: `<text x="670" y="140|404" font-size="24" font-weight="800">` 가 글자수
제한 없이 렌더 → 27자 초과 헤드라인이 KPI 카드(x=1024-1164) 영역과 겹침. 21개
운영 SVG에서 가시적 오버레이 발생.

**교훈 1 — 픽셀 예산은 코드 상수로 표현해야 함**:
구획별 픽셀 예산이 docstring에 적혀있어도 호출부 코드에는 noop. 비슷한 문제 회피:
side-card subheadline에는 이미 `_fit_subheadline(max_chars=54)` 가드가 존재. 패턴
복제로 `_fit_panel_headline(max_chars=27)` 헬퍼 + 양쪽 call site (top_right,
bottom_right) 둘 다 적용. 누락된 visual-budget guard는 항상 호출부에 명시.

**교훈 2 — 일괄 재생성과 surgical patch는 결과물이 다름**:
`generate_post_images.py --force` 로 재생성하면 `extract_three_stories()` 가
title+excerpt+filename 만 사용해 헤드라인이 단일 토큰("Agent", "Cloud")으로 축소.
원본은 L22 dispatch 시절 본문 H3에서 추출한 풍부한 문구(`AWS Serverless AI Defense
Architecture`)였음. 편집 가치를 보존하려면 `scripts/fix_panel_headline_overflow.py`
같은 in-place regex 패치 도구로 헤드라인 문자열만 잘라내는 방식이 안전. 향후
유사 회귀(텍스트 overflow, 색상 충돌 등)에서 동일 접근 적용 가능.

**교훈 3 — cap 함수의 ellipsis budget**:
초기 구현은 `max_chars - 1` 위치에서 자르고 "..." 추가 → 결과 길이가 `max_chars + 2`
까지 늘어남. 수정: `budget = max_chars - 3` 으로 ellipsis 자리 예약. 단위 테스트
`test_result_never_exceeds_max_chars` 가 이 invariant를 강제. (commit `6b5a621b`)
