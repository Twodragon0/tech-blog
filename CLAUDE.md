# Claude Code Instructions

Instructions for Claude Code when working on this project.

**Last updated**: 2026-02-19

## Quick Reference

| Resource | URL |
|----------|-----|
| **Production** | https://tech.2twodragon.com |
| **Backup** | https://twodragon0.github.io/tech-blog |
| **GitHub** | https://github.com/Twodragon0/tech-blog |
| **RSS** | https://tech.2twodragon.com/feed.xml |

## Project Overview

Jekyll-based DevSecOps technical blog.

- **Topics**: DevSecOps, DevOps, FinOps, Cloud Security, Blockchain
- **Language**: Korean (content), English (code comments)
- **Hosting**: Vercel (production), GitHub Pages (backup)

## Workflow Strategy (Boris Cherny Tips)

### Plan Mode First (TIP 2)
- **복잡한 작업은 반드시 Plan Mode부터 시작**
- 에너지를 "계획"에 집중하면 구현 1-shot 성공률이 올라감
- 문제가 꼬이면 즉시 Plan Mode로 돌아가 재계획 (밀어붙이지 않기)
- 빌드뿐 아니라 **검증 단계**도 Plan에 포함시킬 것

### Parallel Worktrees (TIP 1)
- 3~5개 git worktree를 동시에 운영하고 각각 별도 Claude 세션 실행
- `bash scripts/setup-worktrees.sh setup` 으로 세팅
- alias: `za`, `zb`, `zc` (작업용), `zd` (분석 전용), `zm` (메인)
- **탭 1개 = 작업 1개 = worktree 1개** 원칙

### Subagent 활용 (TIP 8)
- 더 많은 compute가 필요하면 "use subagents" 를 요청에 추가
- 세부 작업을 subagent에게 넘겨 메인 에이전트 컨텍스트를 깨끗하게 유지

### Strict Verification (TIP 6)
- Claude를 단순 실행자가 아니라 **리뷰어/검증자**로 활용
- 변경사항은 반드시 테스트 통과 후 PR 생성
- 어설픈 수정 시: "지금까지 배운 걸 바탕으로 폐기하고 우아한 해결책으로 다시 구현해"
- 일을 넘기기 전에 스펙을 구체적으로 써서 모호성 제거

### Learning Feedback Loop (TIP 3)
- 교정/수정 후 마지막에: **"CLAUDE.md를 업데이트해서 다음엔 같은 실수 하지 않게 해"**
- `notes/` 디렉토리에 작업별 학습 내용 기록
- PR마다 `notes/per-pr/PR-{number}.md` 업데이트
- CLAUDE.md가 notes를 참조하도록 유지

### Bug Fix Protocol (TIP 5)
- 버그 수정은 Claude에게 맡기되 **micromanage 하지 말 것**
- "실패하는 CI 테스트 고쳐" 한 마디로 충분
- 어떻게 고칠지 간섭하지 않기

## Opus 4.6 최대한 활용하기

Claude Opus 4.6는 의미 있는 업그레이드입니다. 복잡한 작업을 위해 맥락을 수집하고, 어려운 작업에 더 오래 매달리며, 독립적으로 작업할 때와 사용자에게 확인을 구할 때를 더 잘 판단합니다.

### 1. 지시사항을 더 정확하게 따름

**핵심 원칙**:
- **반복 지시 불필요**: Opus 4.6는 처음부터 지시사항을 더 꼼꼼하게 따릅니다. 같은 말을 반복할 필요가 없습니다.
- **적은 예시로도 패턴 파악**: 명확한 예시 몇 개면 충분하며, Opus 4.6는 그것으로부터 일반화할 수 있습니다.
- **의도 설명 포함**: 규칙뿐만 아니라 지시의 의도를 설명하면 넓은 범위에 적용할 수 있는 맥락을 갖게 됩니다.

**활용 방법**:
- ✅ **한 번만 말하세요**: 요구사항을 명확하게 전달하면 세션 도중에 반복 강조가 필요할 가능성이 낮습니다.
- ✅ **명확한 예시 몇 개면 충분**: Opus 4.6는 그것으로부터 일반화할 수 있습니다.
- ✅ **의도 설명**: "이렇게 하면 Opus 4.6가 좁은 범위에서 따르는 것이 아니라 넓은 범위에 적용할 수 있는 맥락을 갖게 됩니다."
- ❌ **리마인더 불필요**: "그리고 잊지 말고…" 같은 리마인더는 불필요합니다.

**프로젝트 적용 예시**:
```markdown
# 좋은 예: 의도와 함께 명확한 지시
"보안을 최우선으로 고려하여 API 키는 환경 변수로 관리하고, 
로그에는 민감 정보가 노출되지 않도록 마스킹을 적용해줘. 
이렇게 하면 실수로 커밋되거나 로그에 노출되는 위험을 방지할 수 있어."

# 나쁜 예: 반복적인 리마인더
"API 키는 환경 변수로 관리해줘. 그리고 잊지 말고 로그에는 마스킹을 적용해줘. 
그리고 API 키는 절대 하드코딩하지 말아줘."
```

### 2. 행동하기 전에 맥락을 파악

**핵심 원칙**:
- **전체 그림 파악**: 변경 사항을 만들기 전에, Opus 4.6는 전체 그림을 파악합니다 (파일 구조, 기존 패턴, 의존성, 각 요소가 어떻게 연결되는지).
- **대용량 파일 처리**: Opus 4.6는 대용량 파일, 데이터셋, 코드베이스, 긴 문서 전체를 훑어 응답하기 전에 이해를 구축할 수 있습니다.
- **세션 시작이 느려질 수 있음**: Opus 4.6가 행동하기 전에 먼저 읽기 때문에 세션 시작이 느려진 것을 느낄 수 있습니다.

**활용 방법**:
- ✅ **맥락을 미리 제공**: 처음에 공유하는 정보의 품질이 출력의 품질을 직접적으로 좌우합니다. 관련 파일을 공유하고, 연관 문서를 연결하고, 더 넓은 시스템을 설명하세요.
- ✅ **역할 설정은 건너뛰기**: "[전문가]로서 행동해"라거나 "…의 전문가가 되어"라고 말할 필요가 없습니다. Opus 4.6는 제공된 작업과 맥락에서 적절한 전문성 수준을 추론합니다.
- ✅ **간단한 작업은 범위를 좁히기**: 모든 작업에 전체 그림이 필요한 것은 아닙니다. 빠른 요청의 경우 "이 파일만 봐주세요" 또는 "정확히 이것만 필요해요, 넓은 맥락은 건너뛰세요."
- ✅ **이해한 내용 확인 요청**: "이 구조가 어떻게 되어 있는지 설명해주고 나서 X를 업데이트해줘." 이렇게 하면 사각지대를 일찍 발견할 수 있습니다.

**프로젝트 적용 예시**:
```markdown
# 좋은 예: 맥락 제공
"이 프로젝트는 Jekyll 기반 기술 블로그입니다. 
_posts/ 디렉토리에 마크다운 포스트가 있고, 
assets/images/에 이미지가 저장됩니다. 
이 구조를 이해한 후 새로운 포스트 생성 스크립트를 작성해줘."

# 좋은 예: 간단한 작업은 범위 좁히기
"이 파일만 봐주세요: scripts/check_posts.py의 50-60줄만 수정해줘. 
넓은 맥락은 건너뛰세요."
```

### 3. 어려운 작업에서 끈기 있게 작업

**핵심 원칙**:
- **더 오래 매달림**: Opus 4.6는 문제에 더 오래 매달리고 독립적으로 대안을 탐색합니다.
- **복잡한 작업 성공률 향상**: 복잡한 다단계 작업이 첫 번째 시도에서 성공할 가능성이 높아집니다.
- **더 오래 걸릴 수 있음**: 복잡한 작업은 더 오래 걸릴 수 있습니다. Claude가 사용자에게 확인하기 전에 여러 접근법을 시도합니다.

**활용 방법**:
- ✅ **확인 지점 설정**: 작은 단계로 나누어 작업하는 것을 선호한다면, Opus 4.6에게 언제 멈출지 알려주세요. "각 주요 단계 후에 확인해줘" 또는 "두세 가지 이상의 접근법을 시도하기 전에 물어봐줘."
- ✅ **루프 인식**: Claude가 실질적인 진전 없이 같은 접근법의 변형을 반복하고 있다면, 구체적인 대안을 제시하며 개입하세요.
- ✅ **협업 요청**: 계속 관여하고 싶은 작업의 경우, 그 기대를 처음부터 설정하세요. "이걸 대화형으로 작업하자. 단계별로 나에게 설명해줘."

**프로젝트 적용 예시**:
```markdown
# 좋은 예: 확인 지점 설정
"포스트 개선 스크립트를 작성해줘. 각 주요 단계 후에 확인해줘:
1. 파일 구조 분석 후 확인
2. 개선 로직 설계 후 확인
3. 구현 후 확인"

# 좋은 예: 협업 요청
"이걸 대화형으로 작업하자. 
단계별로 나에게 설명해줘:
1. 어떤 파일들을 읽어야 하는지
2. 어떤 로직이 필요한지
3. 어떤 테스트가 필요한지"
```

### 4. 더 적극적으로 의견을 제시

**핵심 원칙**:
- **빠른 결정**: Opus 4.6는 방향을 더 빠르게 결정하고, 다른 경로가 보일 때 대안을 더 기꺼이 제안합니다.
- **바로 작업 착수**: Opus 4.6는 먼저 확인을 구하기보다 바로 작업에 착수할 수 있습니다.
- **유도 질문에 덜 흔들림**: Opus 4.6는 유도 질문에 덜 흔들리고, 제시된 내용을 즉시 확인하는 경향이 줄었습니다.

**활용 방법**:
- ✅ **대안 탐색 요청**: "이걸 접근하는 세 가지 방법이 뭐가 있을까?"
- ✅ **멈춰야 할 시점 설정**: Opus 4.6가 변경하기 전에 계획을 공유하기를 원한다면 말하세요. "변경하기 전에 접근 방식을 먼저 설명해줘."
- ✅ **결정이 끝났을 때 직접적으로 말하기**: "대안은 이미 고려했어. 이 접근 방식으로 진행해줘."
- ✅ **의도적으로 스트레스 테스트**: "이 계획의 문제점은 뭐야?" 또는 "내가 놓치고 있는 게 뭐야?"

**프로젝트 적용 예시**:
```markdown
# 좋은 예: 대안 탐색 요청
"이미지 최적화를 위한 세 가지 방법이 뭐가 있을까?
각 방법의 장단점도 설명해줘."

# 좋은 예: 스트레스 테스트
"이 보안 설정의 문제점은 뭐야? 
어떤 공격 벡터가 남아있을까?"
```

### 5. 더 강력한 글쓰기

**핵심 원칙**:
- **스타일 매칭**: Opus 4.6는 스타일 매칭, 긴 글에서의 목소리 유지, 복잡한 문서의 일관성과 구조 유지에서 더 뛰어납니다.
- **이전 작업 스타일 매칭**: Opus 4.6는 이전 작업의 스타일을 매칭할 수 있습니다.
- **명확한 목소리 설정**: 가이드 없는 출력에는 여전히 인식 가능한 AI 패턴이 있을 수 있습니다. 명확한 목소리와 톤 설정이 도움이 됩니다.

**활용 방법**:
- ✅ **예시로 시작**: 원하는 스타일의 샘플을 공유하세요. Opus 4.6가 매칭할 수 있습니다.
- ✅ **피해야 할 것을 명시**: Opus 4.6는 스타일 제약을 따릅니다.
- ✅ **글쓰기 파트너로 활용**: 공동 집필이나 기존 작업의 연속에 활용하세요.
- ✅ **더 길고 야심찬 창작 프로젝트**: 더 길고 야심찬 창작 프로젝트를 Claude에게 맡기세요.

**프로젝트 적용 예시**:
```markdown
# 좋은 예: 스타일 예시 제공
"다음 스타일로 기술 블로그 포스트를 작성해줘:
- 실무 중심의 구체적인 내용
- 보안 모범 사례 강조
- 코드 예제와 설정 파일 포함
- 문제 해결 과정과 트러블슈팅 포함"

# 좋은 예: 피해야 할 것 명시
"다음은 피해줘:
- 이론적인 설명만 하는 것
- FAQ 섹션 추가
- 과도한 마케팅 톤"
```

### 실제 작업에서의 활용

Opus 4.6는 더 많은 것을 처리하므로 더 크게 생각할 수 있습니다:

- **복잡한 분석**: 여러 파일, 데이터셋, 문서를 종합하여 분석
- **연결된 인사이트 수집**: 연결된 도구 전체에서 단서를 추적하고, 단일 소스에서는 보이지 않는 것을 찾아냄
- **시나리오 전반에 걸친 테스트**: 전체 범위의 결과에 대해 계획을 테스트하고, 각 리스크가 나머지에 어떻게 연쇄적으로 영향을 미치는지 추적
- **이해도 매핑**: 혼란의 원인을 추적하고, 이미 이해하고 있는 것을 매핑한 후, 그 빈틈을 중심으로 작업 구성

## Custom Skills (TIP 4)

하루에 1번 이상 하는 작업은 스킬로 만들어 재사용합니다.

### 기본 스킬

| Skill | Command | Purpose |
|-------|---------|---------|
| 새 포스트 생성 | `/new-post` | 제목/카테고리 입력 → 파일 자동 생성 |
| 포스트 검증 | `/validate-post` | Front matter, 이미지, 코드 블록 검증 |
| 기술 부채 탐지 | `/techdebt` | 중복 코드, 미사용 리소스, TODO 탐지 |
| CI 수정 | `/fix-ci` | Jekyll 빌드 에러 자동 진단/수정 |
| 일일 점검 | `/daily-review` | Git 상태, SEO, 이미지 종합 점검 |

### Agent Team 스킬 (Multi-Agent)

| Skill | Command | 팀 구성 | Purpose |
|-------|---------|---------|---------|
| 팀 포스트 생성 | `/team-create-post` | researcher → writer → executor → qa | 조사부터 검증까지 자동화 |
| 팀 종합 감사 | `/team-audit` | explore + security → architect → executor | 보안/성능/SEO 종합 감사 |
| 팀 콘텐츠 개선 | `/team-improve` | explore → critic → executor → reviewer | 기존 포스트 품질 개선 |
| 팀 성능 최적화 | `/team-optimize` | explore + researcher → analyst → executor | 성능/SEO 최적화 |

스킬 파일 위치: `.claude/commands/`

## Agent Team 활용 가이드

### 기본 개념

Claude Code Agent Team은 전문화된 AI 에이전트들이 협업하여 작업을 수행하는 멀티 에이전트 오케스트레이션 시스템입니다.

```
사용자 요청 → 오케스트레이터(Claude) → 전문 에이전트 팀 → 결과 통합 → 사용자에게 보고
```

### 에이전트 역할별 분류

| 역할 | 에이전트 | 모델 | 사용 시점 |
|------|---------|------|-----------|
| 탐색 | `explore` / `explore-medium` / `explore-high` | haiku/sonnet/opus | 코드베이스 파악, 파일 검색 |
| 조사 | `researcher` / `researcher-low` | sonnet/haiku | 외부 자료 조사, 문서 검색 |
| 분석 | `architect` / `architect-medium` / `architect-low` | opus/sonnet/haiku | 아키텍처 분석, 디버깅 |
| 계획 | `planner` / `analyst` | opus | 전략 수립, 요구사항 분석 |
| 실행 | `executor` / `executor-low` / `executor-high` | sonnet/haiku/opus | 코드 작성, 파일 수정 |
| 검증 | `qa-tester` / `code-reviewer` / `security-reviewer` | sonnet/opus | 테스트, 코드리뷰, 보안검사 |
| 작성 | `writer` | haiku | 문서 작성, 주석 |
| 비평 | `critic` | opus | 계획 검토, 품질 평가 |
| 디자인 | `designer` / `designer-high` | sonnet/opus | UI/UX 작업 |
| 데이터 | `scientist` / `scientist-high` | sonnet/opus | 데이터 분석, 통계 |

### 실행 모드

| 모드 | 키워드 | 설명 |
|------|--------|------|
| **autopilot** | "autopilot", "build me" | 아이디어 → 완성 코드까지 자율 실행 |
| **ultrawork** | "ulw", "ultrawork" | 최대 병렬 에이전트 실행 (기본 모드) |
| **ecomode** | "eco", "ecomode" | 토큰 절약형 병렬 실행 |
| **ralph** | "ralph", "don't stop" | 완료될 때까지 반복 |
| **ultrapilot** | "ultrapilot" | 병렬 autopilot (3-5배 속도) |
| **pipeline** | "pipeline" | 에이전트 체이닝 |
| **swarm** | "swarm" | N개 에이전트 협업 |

### 자주 쓰는 팀 패턴

```bash
# 1. 포스트 생성 (조사 → 작성 → 검증)
/team-create-post

# 2. 종합 감사 (보안 + 성능 + SEO)
/team-audit

# 3. 콘텐츠 개선
/team-improve

# 4. 성능 최적화
/team-optimize

# 5. 자연어로 팀 실행 (autopilot)
"Kubernetes 보안 모범사례 포스트를 작성해줘"  → autopilot 자동 활성화

# 6. 빠른 병렬 작업
"ulw 모든 포스트 이미지 검증하고 누락된 것 수정해줘"

# 7. 절약 모드
"eco 최근 포스트 5개 SEO 점검해줘"
```

### 비용 최적화 원칙

| 원칙 | 설명 |
|------|------|
| 탐색은 haiku | `explore`, `explore-medium`은 가벼운 모델로 충분 |
| 판단은 opus | `architect`, `critic`, `analyst`는 정확성 필요 |
| 실행은 sonnet | `executor`는 sonnet이 가성비 최적 |
| 검증은 haiku | 간단한 검증은 `*-low` 에이전트 활용 |
| 병렬 실행 | 독립 작업은 반드시 병렬로 (비용 동일, 시간 절약) |

### 네이티브 Agent Teams (실험적 기능)

Claude Code v2.1.32+의 네이티브 Agent Teams 기능을 활성화했습니다.

**활성화 설정** (`~/.claude/settings.json`):
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**실행 방법**:
```bash
# 기본 모드 (in-process, 터미널 내 전환)
claude

# tmux 분할 화면 모드 (각 에이전트 실시간 확인)
claude --teammate-mode tmux
```

**팀 생성 (자연어)**:
```
"보안 전문가와 성능 전문가로 팀을 만들어서 블로그 전체 감사해줘"
"포스트 조사팀 1명, 작성팀 1명, 검증팀 1명으로 Kubernetes 보안 포스트 작성해줘"
"아키텍트와 비평가로 팀을 구성해서 블로그 구조 개선안을 만들어줘"
```

**프로젝트 전용 서브에이전트** (`.claude/agents/`):

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| `post-researcher` | sonnet | 포스트 주제 조사, 최신 트렌드 수집 |
| `post-validator` | haiku | 포스트 검증 (frontmatter, 이미지, 보안) |
| `security-auditor` | sonnet | 보안 감사 (시크릿, CSP, XSS) |
| `seo-optimizer` | haiku | SEO 분석 및 개선 권장 |
| `performance-analyst` | haiku | 성능 분석 (Core Web Vitals) |

**키보드 단축키** (in-process 모드):

| 키 | 기능 |
|----|------|
| `Shift+Down` | 다음 팀원으로 이동 |
| `Enter` | 팀원 세션 보기 |
| `Escape` | 팀원 현재 턴 중단 |
| `Ctrl+T` | 작업 목록 토글 |
| `Ctrl+F` | 모든 백그라운드 에이전트 종료 |

**제약 사항**:
- 팀원은 리더의 대화 히스토리를 상속하지 않음 (각자 독립 컨텍스트)
- 중첩 팀 불가 (팀원이 자체 팀원 생성 불가)
- 세션당 1개 팀만 운영 가능
- tmux 모드는 VS Code 터미널에서 미지원

## Auto-Yes for project / tmp (Claude Code, Cursor)
- **Scope**: Work inside this repo or under `/tmp` → treat all confirmations as **yes**.
- **Scripts**: Run confirmation prompts with `--yes` / `-y` when available (e.g. `rename_images_to_english.py --yes`).
- **Env**: Set or assume `TECH_BLOG_AUTO_YES=1` or `CI=1` so supported scripts skip interactive prompts.

## Core Principles

### 1. Security First
- **Never hardcode** API keys, passwords, tokens
- Use `os.getenv("API_KEY", "")` for sensitive data
- Mask logs with `mask_sensitive_info()` before output
- Validate with `_validate_masked_text()` before file writes
- **CSP Compliance**: Review CSP headers when adding external scripts
- **Input Validation**: Always validate and sanitize user inputs
- **Error Handling**: Never expose sensitive information in error messages
- **Dependency Security**: Run `npm audit` and `bundle audit` regularly

### 2. Cost Optimization
Priority order for AI operations:
1. **Gemini CLI** (`gemini` command) - Free with OAuth 2.0 ⭐ **최우선**
2. **Local templates** - No API cost
3. **Cursor/Claude Console** - Free allocation
4. **API calls** - Last resort (costs money)

**Cost Management Rules**:
- Use Context Caching for DeepSeek API (up to 90% cost reduction)
- Cache API responses for 7 days when possible
- Monitor API usage with `scripts/monitor_api_usage.py`
- Set rate limits to prevent unexpected costs
- Use off-peak hours for DeepSeek API (50-75% discount)

### 3. Operational Efficiency
- **Automation First**: Use scripts instead of manual work
- **Monitoring**: Check Sentry and Vercel Analytics regularly
- **Error Recovery**: Implement automatic retry with exponential backoff
- **Logging**: Use structured logging with context
- **Performance**: Monitor Core Web Vitals (LCP, FID, CLS)

### 4. UI/UX Excellence
- **Accessibility**: WCAG 2.1 AA compliance required
- **Responsive Design**: Mobile-first approach
- **Performance**: Target LCP < 2.5s, FID < 100ms, CLS < 0.1
- **User Feedback**: Provide loading states and error messages
- **Dark Mode**: Support system preference + manual toggle

### 5. Commit Rules
- **No `Co-Authored-By: Claude`** in commit messages
- Concise messages in Korean or English
- Use conventional commits: `fix:`, `feat:`, `docs:`, `refactor:`

```bash
git commit -m "fix: 보안 경고 수정"
git commit -m "feat: Add new feature"
git commit -m "docs: Update SPEC.md with security improvements"
```

## File Structure

```
tech-blog/
├── _posts/              # Blog posts (YYYY-MM-DD-Title.md)
├── _layouts/            # Jekyll layouts
├── _includes/           # Reusable components
├── _data/               # Jekyll data (e.g. collected_news.json)
├── assets/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript
│   └── images/          # Images (English filenames only!)
├── scripts/             # Python/Bash utilities
│   └── docs/            # Script documentation
├── docs/                # Project documentation
│   ├── guides/          # Content creation guides
│   ├── optimization/    # Performance guides
│   ├── setup/           # Setup guides
│   └── troubleshooting/ # Troubleshooting guides
├── api/                 # Vercel Serverless Functions
├── .claude/
│   └── commands/        # Custom skills (/new-post, /validate-post, etc.)
├── .opencode/           # OpenCode Sisyphus + Ralph Loop config
├── notes/               # 작업별 학습/결정/이슈 기록 (TIP 3)
│   ├── learnings.md     # 기술적 발견, 패턴
│   ├── decisions.md     # 아키텍처 결정 기록
│   ├── issues.md        # 알려진 이슈/해결법
│   └── per-pr/          # PR별 노트
├── .cursorrules         # Detailed Cursor AI rules
├── AGENTS.md            # AI agent coding guidelines
├── CLAUDE.md            # This file
└── SECURITY.md          # Security policy
```

## Post Writing Rules

### Filename Format
- Format: `YYYY-MM-DD-English_Title.md`
- **No Korean in filenames**

### Front Matter
```yaml
---
layout: post
title: "제목 (Korean OK)"
date: YYYY-MM-DD HH:MM:SS +0900
category: [security|devsecops|devops|cloud|kubernetes|finops|incident]
categories: [category1, category2]
tags: [tag1, tag2]
excerpt: "Summary (150-200 chars)"
image: /assets/images/YYYY-MM-DD-English_Title.svg
---
```

### Code Blocks
- **Always** include language tags: ```python, ```bash, ```yaml
- **>10 lines**: Replace with GitHub link + HTML comment for original
- **3-10 lines**: Keep with reference link
- **<3 lines**: Keep original
- **Mask** sensitive data: `YOUR_API_KEY`, `***MASKED***`

### Content Structure
- **NO FAQ sections**: Do not add FAQ (자주 묻는 질문) sections to blog posts
  - FAQ content is unnecessary and adds no value
  - Do not include `schema_type: FAQPage` in front matter
  - Do not include JSON-LD FAQPage structured data
  - SEO/AEO optimization does NOT require FAQ sections
- Focus on core technical content and actionable insights instead

## Image Rules

### Filenames
- **English only** - No Korean characters
- Format: `YYYY-MM-DD-English_Title.svg`
- Convert script: `python3 scripts/rename_images_to_english.py`

### SVG Text
- **English only** in SVG text elements
- No special chars: `·`, `•`, `—`, `"`, `'`
- UTF-8 encoding required

## Common Commands

```bash
# Worktree 병렬 세션 (TIP 1)
bash scripts/setup-worktrees.sh setup    # 워크트리 생성
bash scripts/setup-worktrees.sh aliases  # .zshrc alias 출력
bash scripts/setup-worktrees.sh status   # 상태 확인

# Local development (AGENTS.md에 상세 빌드/린트 명령 있음)
bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload
bundle exec jekyll build --destination _site

# Convert image filenames to English
python3 scripts/rename_images_to_english.py --yes

# Generate post images
python3 scripts/generate_post_images.py --all --force

# Validate posts
python3 scripts/check_posts.py

# Fix links
python3 scripts/fix_links_unified.py --fix

# Verify images
python3 scripts/verify_images_unified.py --all
```

## Implementation Status

| Feature | Score | Status | Next Steps |
|---------|-------|--------|------------|
| **Security** | 9/10 | CSP, HSTS, Sentry (Free Tier optimized), Masking, Input Validation | Periodic CSP review, dependency updates |
| **Performance** | 9/10 | Service Worker, Caching, Lazy Loading, Critical CSS | Image optimization, bundle size reduction |
| **SEO** | 10/10 | Open Graph, Twitter Cards, JSON-LD, Sitemap, RSS | Maintain current level |
| **User Features** | 9/10 | Giscus comments, DeepSeek chatbot, Dark/Light mode, Search | Accessibility improvements |
| **Cost Optimization** | 9/10 | API caching, rate limiting, free tier optimization | Monitor usage, optimize further |
| **Operational Efficiency** | 8/10 | Automation scripts, CI/CD, monitoring | Enhanced error recovery |

## OpenCode Integration

### OpenCode Sisyphus Mode with Ralph Loop

This project uses OpenCode with Sisyphus mode and Ralph Loop for automated content improvement.

#### Quick Start
```bash
# Start OpenCode in Sisyphus mode
opencode sisyphus

# Ralph Loop commands (see AGENTS.md §14 for full list)
/improve-posts
/collect-news
/validate-posts
/generate-images
/security-audit
/write-code
/refactor
/fix-bugs
```

#### Model Selection Strategy
- **High-Quality Tasks** (Opus 4.5): Content generation, code writing, image generation, refactor, fix-bugs
- **Cost-Efficient Tasks** (Sonnet 4): Validation, analysis, read-only operations, security-audit

#### Cost Optimization
1. **Cache First**: Check `_data/collected_news.json` (7-day TTL) before API calls
2. **Local Scripts**: Use `python3 scripts/*.py` (no API cost)
3. **Gemini CLI**: Free OAuth 2.0 (first choice)
4. **Batch Operations**: Group operations to reduce API calls

#### Security
- All agents follow principle of least privilege
- Sensitive data automatically masked in logs
- Input validation for all commands
- Security audit command available: `/security-audit`

See `.opencode/README.md` for detailed documentation.

## Related Documentation

| Document | Purpose |
|----------|---------|
| `.cursorrules` | Detailed Cursor AI rules (comprehensive) |
| `AGENTS.md` | AI agent coding guidelines; build/lint/test 명령 정리 |
| `.opencode/README.md` | OpenCode configuration and usage |
| `SECURITY.md` | Security policy |
| `notes/` | 작업별 학습/결정/이슈 기록 (TIP 3) |
| `.claude/commands/` | Custom skills for Claude Code (TIP 4) |
| `docs/` | All project documentation |
| `scripts/README.md` | Script documentation |

## Quick Checklist

### Pre-Commit Checklist
- [ ] No hardcoded secrets
- [ ] Image filenames are English only
- [ ] SVG text is English only
- [ ] Code blocks have language tags
- [ ] Links point to real resources (no example.com)
- [ ] Front matter follows format
- [ ] `lsp_diagnostics` clean on changed files

### Security Checklist
- [ ] Input validation implemented
- [ ] Error messages don't expose sensitive info
- [ ] CSP headers reviewed (if adding external scripts)
- [ ] Dependencies audited (`npm audit`, `bundle audit`)
- [ ] API keys use environment variables
- [ ] Logs mask sensitive information

### Performance Checklist
- [ ] Images optimized and lazy-loaded
- [ ] CSS/JS minified for production
- [ ] Service Worker updated (if changed)
- [ ] Cache headers appropriate
- [ ] Core Web Vitals checked

### Cost Optimization Checklist
- [ ] API calls minimized (use Gemini CLI first)
- [ ] Caching implemented where possible (7-day TTL)
- [ ] Rate limiting configured
- [ ] Free tier limits respected (Sentry, Vercel)
- [ ] OpenCode model selection optimized (Opus 4.5 for generation, Sonnet 4 for validation)
- [ ] Local scripts used before API calls

### UI/UX Checklist
- [ ] Accessibility: ARIA attributes, keyboard navigation
- [ ] Responsive: Mobile, tablet, desktop tested
- [ ] Dark mode: Works correctly
- [ ] Loading states: Provided for async operations
- [ ] Error handling: User-friendly messages
