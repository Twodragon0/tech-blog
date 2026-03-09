# Team: 블로그 종합 감사 (Multi-Agent)

멀티 에이전트 팀을 활용하여 블로그의 보안, 성능, SEO, 콘텐츠를 종합 감사합니다.

## 팀 구성

| Agent | Role | Model |
|-------|------|-------|
| explore | 코드베이스 탐색 및 구조 파악 | haiku |
| security-reviewer-low | 보안 취약점 스캔 | haiku |
| architect-medium | 이슈 분석 및 우선순위 결정 | sonnet |
| executor | 자동 수정 가능 이슈 해결 | sonnet |

## 실행 워크플로우

### Phase 1: 병렬 탐색 (3개 에이전트 동시 실행)

**Agent 1 - explore (코드베이스 탐색):**
Task(subagent_type="oh-my-claudecode:explore", model="haiku", run_in_background=true):
- _posts/ 디렉토리 포스트 현황 (총 수, 최근 7일, 카테고리별)
- assets/images/ 이미지 현황 (누락, 미사용)
- _layouts/, _includes/ 템플릿 상태
- scripts/ 스크립트 상태

**Agent 2 - security-reviewer-low (보안 스캔):**
Task(subagent_type="oh-my-claudecode:security-reviewer-low", model="haiku", run_in_background=true):
- 하드코딩된 시크릿 탐지 (API 키, 토큰, 비밀번호)
- CSP 헤더 검토
- 외부 스크립트/리소스 보안 확인
- JavaScript 보안 패턴 검사

**Agent 3 - code-reviewer-low (코드 품질):**
Task(subagent_type="oh-my-claudecode:code-reviewer-low", model="haiku", run_in_background=true):
- Front matter 일관성 점검
- 코드 블록 언어 태그 누락 탐지
- 깨진 링크 패턴 탐지
- 중복 코드/콘텐츠 탐지

### Phase 2: 분석 및 우선순위 결정 (architect-medium)

Task(subagent_type="oh-my-claudecode:architect-medium", model="sonnet"):
- Phase 1의 모든 결과를 종합
- 이슈를 HIGH/MEDIUM/LOW로 분류
- 자동 수정 가능 vs 수동 수정 필요 구분
- 수정 계획 수립

### Phase 3: 자동 수정 (executor, 선택)

사용자가 `--fix` 옵션을 지정한 경우에만:
Task(subagent_type="oh-my-claudecode:executor", model="sonnet"):
- 자동 수정 가능 이슈만 처리
- 각 수정 전 확인
- 수정 내역 기록

### Phase 4: 감사 보고서

```markdown
## 블로그 종합 감사 결과 (YYYY-MM-DD)

### 전체 요약
- 검사 항목: N개
- 정상: X개 | 경고: Y개 | 오류: Z개

### 보안 (Security)
- [HIGH/MEDIUM/LOW] 이슈 설명
- 권장 조치

### 성능 (Performance)
- [HIGH/MEDIUM/LOW] 이슈 설명
- 권장 조치

### SEO
- [HIGH/MEDIUM/LOW] 이슈 설명
- 권장 조치

### 콘텐츠 품질
- [HIGH/MEDIUM/LOW] 이슈 설명
- 권장 조치

### 자동 수정 완료 항목
- 수정 1: 설명
- 수정 2: 설명

### 수동 조치 필요 항목
1. [HIGH] 조치 설명
2. [MEDIUM] 조치 설명
```

## 실행 옵션
- `/team-audit` - 감사만 실행 (수정 없음)
- `/team-audit --fix` - 감사 + 자동 수정
- `/team-audit --security` - 보안 감사만
- `/team-audit --seo` - SEO 감사만

## 비용 최적화
- Phase 1은 모두 haiku (병렬 3개 = haiku 비용만)
- Phase 2만 sonnet (분석에 필요)
- Phase 3는 사용자 요청 시에만 실행
