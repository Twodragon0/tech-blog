# Team: 콘텐츠 개선 (Multi-Agent)

멀티 에이전트 팀을 활용하여 기존 블로그 포스트를 개선합니다.

## 팀 구성

| Agent | Role | Model |
|-------|------|-------|
| explore-medium | 기존 포스트 분석 | sonnet |
| critic | 개선점 도출 및 품질 평가 | opus |
| executor | 개선 사항 구현 | sonnet |
| code-reviewer-low | 변경사항 검증 | haiku |

## 실행 워크플로우

### Phase 1: 대상 선정
AskUserQuestion으로 개선 대상 확인:
- 특정 포스트 지정 (파일명 또는 제목)
- 최근 N개 포스트 전체
- 특정 카테고리 포스트 전체
- 개선 유형: 내용보강, SEO최적화, 코드업데이트, 구조개선

### Phase 2: 분석 (explore-medium + parallel researcher)

**Agent 1 - explore-medium (포스트 분석):**
Task(subagent_type="oh-my-claudecode:explore-medium", model="sonnet"):
- 대상 포스트 전체 내용 분석
- 구조, 길이, 코드 블록, 이미지 현황
- Front matter 완전성 평가
- 내부 링크 연결 상태

**Agent 2 - researcher (선택, 내용보강 시):**
Task(subagent_type="oh-my-claudecode:researcher", model="sonnet", run_in_background=true):
- 포스트 주제의 최신 업데이트 조사
- 새로운 모범 사례 확인
- 관련 참고 자료 수집

### Phase 3: 개선 계획 (critic agent)

Task(subagent_type="oh-my-claudecode:critic", model="opus"):
- Phase 2 분석 결과를 기반으로 구체적 개선점 도출
- 각 개선점의 영향도 평가 (HIGH/MEDIUM/LOW)
- 개선 우선순위 결정
- 개선 전후 예상 변화 설명
- 개선 계획서 작성

사용자에게 개선 계획 확인 받기 (AskUserQuestion)

### Phase 4: 구현 (executor agent)

Task(subagent_type="oh-my-claudecode:executor", model="sonnet"):
- 승인된 개선 사항만 구현
- CLAUDE.md 규칙 준수 (파일명 영문, 코드 태그 등)
- FAQ 섹션 추가 금지
- 각 파일 수정 후 git diff로 변경 확인

### Phase 5: 검증 (code-reviewer-low)

Task(subagent_type="oh-my-claudecode:code-reviewer-low", model="haiku"):
- 변경된 포스트 검증
- Front matter 완전성
- 코드 블록 언어 태그
- 보안 검증 (하드코딩 없음)
- 링크 유효성

### Phase 6: 결과 보고

```markdown
## 콘텐츠 개선 결과

### 개선 대상
- 포스트: [제목] (파일명)

### 개선 내역
| 항목 | 변경 전 | 변경 후 | 영향도 |
|------|---------|---------|--------|
| 항목1 | 이전 | 이후 | HIGH |

### 검증 결과
- 전체 검증: PASS/FAIL
- 세부 결과: ...

### 다음 단계
- git diff로 변경사항 확인
- 커밋 진행 여부 결정
```

## 개선 유형별 에이전트 활용

| 유형 | 주요 에이전트 | 특이사항 |
|------|---------------|----------|
| 내용보강 | researcher + writer + executor | researcher 선행 |
| SEO최적화 | explore + analyst + executor | front matter 집중 |
| 코드업데이트 | explore + executor + build-fixer | 코드 블록 중심 |
| 구조개선 | explore-medium + critic + executor | 전체 구조 리뷰 |

## 비용 최적화
- critic만 opus (핵심 판단에 필요)
- explore/executor는 sonnet (작업 정확성)
- 최종 검증은 haiku (충분한 품질)
