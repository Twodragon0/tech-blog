# Team: 성능/SEO 최적화 (Multi-Agent)

멀티 에이전트 팀을 활용하여 블로그의 성능과 SEO를 최적화합니다.

## 팀 구성

| Agent | Role | Model |
|-------|------|-------|
| explore | 현재 상태 분석 | haiku |
| researcher | 최신 최적화 기법 조사 | sonnet |
| analyst | 최적화 전략 수립 | opus |
| executor | 최적화 적용 | sonnet |
| qa-tester | 최적화 결과 검증 | sonnet |

## 실행 워크플로우

### Phase 1: 현재 상태 분석 (병렬)

**Agent 1 - explore (성능 분석):**
Task(subagent_type="oh-my-claudecode:explore", model="haiku", run_in_background=true):
- assets/css/ 파일 크기 및 구조 분석
- assets/js/ 파일 크기 및 로딩 패턴
- _includes/ 에서 외부 리소스 로딩 확인
- Service Worker 설정 확인
- 이미지 최적화 상태 (lazy loading, 크기)

**Agent 2 - explore (SEO 분석):**
Task(subagent_type="oh-my-claudecode:explore", model="haiku", run_in_background=true):
- sitemap.xml 생성 상태
- robots.txt 설정
- Open Graph / Twitter Card 메타태그
- JSON-LD 구조화 데이터
- 포스트 Front matter SEO 필드 완성도
- 내부 링크 구조

**Agent 3 - researcher (최신 기법):**
Task(subagent_type="oh-my-claudecode:researcher", model="sonnet", run_in_background=true):
- Core Web Vitals 최적화 최신 기법
- Jekyll 성능 최적화 모범 사례
- 기술 블로그 SEO 트렌드 2026

### Phase 2: 전략 수립 (analyst)

Task(subagent_type="oh-my-claudecode:analyst", model="opus"):
- Phase 1 결과 종합 분석
- 현재 점수 대비 개선 가능 영역 식별
- ROI 기반 우선순위 결정 (효과 대비 노력)
- 구체적 실행 계획 수립
- 예상 개선 효과 수치 제시

사용자에게 계획 확인 (AskUserQuestion)

### Phase 3: 최적화 적용 (executor)

Task(subagent_type="oh-my-claudecode:executor", model="sonnet"):
- 승인된 최적화만 적용
- CSS/JS 최적화
- 메타태그 개선
- 이미지 최적화 설정
- 캐싱 설정 개선

### Phase 4: 검증 (qa-tester)

Task(subagent_type="oh-my-claudecode:qa-tester", model="sonnet"):
- 변경사항이 기존 기능을 깨뜨리지 않는지 확인
- python3 scripts/check_posts.py 실행
- 주요 페이지 렌더링 확인

### Phase 5: 결과 보고

```markdown
## 최적화 결과 보고

### 성능 개선
| 메트릭 | 이전 | 이후 | 변화 |
|--------|------|------|------|
| LCP    | -    | -    | -    |
| FID    | -    | -    | -    |
| CLS    | -    | -    | -    |

### SEO 개선
| 항목 | 이전 | 이후 |
|------|------|------|
| 메타태그 완성도 | -% | -% |
| 구조화 데이터 | - | - |
| 내부 링크 | - | - |

### 적용된 최적화
1. 최적화 1: 설명
2. 최적화 2: 설명

### 추가 권장 사항
- 수동 조치 필요 항목
```

## 실행 옵션
- `/team-optimize` - 전체 최적화
- `/team-optimize --performance` - 성능만
- `/team-optimize --seo` - SEO만

## 비용 최적화
- Phase 1 탐색은 haiku (3개 병렬 = 저비용)
- analyst만 opus (전략적 판단에 필요)
- 나머지는 sonnet
