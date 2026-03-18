# Session: 포스트 콘텐츠 품질 및 자동 생성 개선
**기간**: 2026-03-17 ~ 2026-03-18
**범위**: 포스트 내용 품질, SVG 이미지, 자동 생성 스크립트, 테스트, CI

## 요약

blogwatcher 자동 생성 포스트에서 "실무 적용 포인트"가 동일한 generic 텍스트로 반복되는 문제를 발견하고, 템플릿 키워드 분기 세분화 + 반복 감지 + 테스트 자동화로 근본 해결.

## 주요 변경

### 1. 포스트 콘텐츠 개선 (수동)
- 3/17, 3/16 포스트 3개의 반복 실무 포인트 → 뉴스 주제별 구체적 보안 지침으로 교체
- 3/16 Bitcoin 포스트 영문 제목/요약 → 한국어 번역
- 3/10 포스트 블록체인 반복 패턴 제거

### 2. SVG 이미지 개선
- 카드 텍스트 잘림 5건 수정
- 중복 `id="grid"` 패턴 제거 (3개 SVG + 소스 스크립트)
- `_truncate_text()` 단어 경계 절단 로직 추가

### 3. 자동 생성 스크립트 (`auto_publish_news.py`)
- `_generate_ai_analysis_template`: 2→8분기 (agent/LLM/GPU/simulation/coding/attack/opensource/fallback)
- `_generate_devops_template`: 2→10분기 (docker/RBAC/이미지/서비스메시/네트워크정책/K8s/CI-CD/컨퍼런스/네트워크/fallback)
- `_generate_contextual_action_point` AI: 2→6분기, Cloud: 3→6분기, Blockchain: 2→7분기
- 제목 접두사 '기술·보안 주간 다이제스트:' 제거
- `generate_cross_refs()` dead code 90줄 제거

### 4. 검증 자동화
- `check_posts.py`에 `check_duplicate_practical_points()` 추가 (3회+ 반복 감지)
- `check_posts.py --changed` PR diff 감지: `origin/main...HEAD` 비교 추가
- pre-commit hook: 스크립트 변경 시 pytest 자동 실행

### 5. 테스트 (162건)
- `_generate_ai_analysis_template`: 39건 (8분기 + banned phrases)
- `_generate_devops_template`: 43건 (10분기 + banned phrases)
- `_generate_contextual_action_point`: 23건 (블록체인 7분기 + AI/Cloud)
- `_generate_security_brief_template`: 22건 (4분기 + edge cases)
- `_generate_security_analysis_template`: 22건 (CVE/SIEM/MITRE)
- `TestBranchPriorityConflicts`: 13건 (parametrized 우선순위 충돌 감지)

### 6. CI
- `requirements-ci.txt`: pytest, requests, beautifulsoup4 추가
- `jekyll.yml`: pytest 스텝 추가 (빌드 전 블로킹)

## 키워드 분기 설계 교훈

1. **분기 순서 = 우선순위**: 구체적 키워드를 먼저, 광범위 키워드를 나중에
2. **과매칭 주의**: `policy`, `container`, `network` 같은 일반 단어는 `admission controller`, `pod security` 같이 구체화
3. **테스트 입력 설계**: 다른 분기 키워드를 포함하지 않도록 (예: "Container image" → docker 분기 매칭)
4. **parametrized 테스트**: 새 분기 추가 시 기존 분기와의 충돌을 자동 감지

## 커밋 목록 (세션에서 직접 작성한 것만)

| 커밋 | 내용 |
|------|------|
| `bf17ca1` | 포스트 콘텐츠 + SVG 이미지 개선 |
| `b9c0b98` | 잔여 복붙 제거 + 블록체인 7분기 |
| `993e292` | 단위 테스트 68건 |
| `6f9f2bd` | CI pytest + 블록체인 테스트 (83건) |
| `df205da` | Security Brief 테스트 (101건) |
| `2cda2ed` | Security Analysis + edge case (123건) |
| `55539ba` | check_posts.py 반복 감지 + pytest 설정 |
| `6cec7c0` | CI requests 의존성 |
| `c1d8e3c` | CI beautifulsoup4 의존성 |
| `75a8a70` | check_posts.py PR diff 감지 수정 |
| `3193157` | 제목 접두사 제거 |
| `c2c2476` | 중복 관련 포스트 섹션 제거 |
| `af694d2` | dead code 90줄 제거 |
| `845fbcf` | K8s 세부 분기 테스트 (133건) |
| `b79c7e8` | K8s 분기 세분화 |
| `c7dc6dd` | AI coding/오픈소스 분기 + learnings.md |
| `47e5fe8` | contextual action point 세분화 + 우선순위 충돌 테스트 (162건) |
| `5a0a225` | pre-commit hook 템플릿 테스트 |
| `1fb7643` | pre-commit hook 스크립트 변경 감지 |
| `640c0c5` | Security Brief 7분기 + pytest 커버리지 설정 |
| `8142f4d` | CI pytest-cov 커버리지 리포트 |
| `1bff129` | PR 커버리지 코멘트 자동 표시 |
| `810e5b8` | trend/checklist 테스트 23건 + CLAUDE.md 규칙 |
| `1e0c122` | 테스트 50초→0.11초 성능 최적화 (lazy import) |
| `30c0671` | conftest.py 공통화 |

## 최종 성과 요약

| 지표 | Before | After |
|------|--------|-------|
| 템플릿 분기 수 | 10개 | **44개** (AI 8 + DevOps 10 + Inline AI 6 + Cloud 6 + Blockchain 7 + Security Brief 7) |
| 테스트 | 0건 | **194건** |
| 테스트 실행 시간 | N/A | **0.15초** |
| 반복 실무 포인트 | 매 포스트 3~5건 | **0건** (자동 감지 차단) |
| pre-commit 검증 | 포스트 품질만 | 포스트 품질 + **템플릿 테스트 자동 실행** |
| CI 커버리지 | 없음 | **pytest + coverage 리포트** |
| dead code | ~90줄 | **제거** |
| SVG 텍스트 잘림 | 다수 | **단어 경계 절단으로 해결** |
