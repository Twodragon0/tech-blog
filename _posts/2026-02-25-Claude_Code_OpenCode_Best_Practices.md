---
layout: post
title: 'Claude Code & OpenCode Best Practices: 38가지 실전 가이드'
date: 2026-02-25 10:00:00 +0900
categories:
- devops
comments: true
description: Claude Code와 OpenCode의 38가지 Best Practice를 정리한 실전 가이드. 환경 설정부터 CLAUDE.md 작성법, 프롬프팅, 에이전트 팀, Hook & Skills, 세션 관리, 자동화까지 공식 문서와 실무 경험을 바탕으로 한 종합 레퍼런스
excerpt: Claude Code와 OpenCode 38가지 Best Practice 종합 가이드. 컨텍스트 윈도우 관리, CLAUDE.md 작성법, 에이전트 팀 운영, 프롬프팅 전략까지 실전 노하우
image: /assets/images/2026-02-25-Claude_Code_OpenCode_Best_Practices.svg
image_alt: Claude Code and OpenCode Best Practices 38 Guide Agent Teams Context Window CLAUDE.md Workflow
keywords:
- Claude Code
- OpenCode
- Best Practices
- AI Agent
- CLAUDE.md
- Agent Teams
- MCP Server
- Opus 4.6
- Subagents
- AI Coding
tags:
- Claude-Code
- OpenCode
- Best-Practices
- AI-Agent
- Prompt-Engineering
- Agent-Teams
- MCP
- AI-Coding
- '2026'
author: Twodragon
schema_type: Article
toc: true
---

{% include ai-summary-card.html
  title='Claude Code & OpenCode Best Practices: 38가지 실전 가이드'
  categories_html='<span class="category-tag devops">DevOps</span> <span class="category-tag tech">AI Coding</span>'
  tags_html='<span class="tag">Claude-Code</span> <span class="tag">OpenCode</span> <span class="tag">Best-Practices</span> <span class="tag">AI-Agent</span> <span class="tag">Agent-Teams</span> <span class="tag">MCP</span> <span class="tag">Prompt-Engineering</span>'
  highlights_html='<li><strong>환경 설정</strong>: 필수 환경 변수, 권한 관리, MCP 서버 연동, 플러그인 확장 (BP-01~05)</li><li><strong>CLAUDE.md</strong>: 프로젝트별 생성, 배치 위치별 역할 구분, 간결하게 유지하는 원칙 (BP-06~10)</li><li><strong>프롬프팅</strong>: 검증 수단 제공, 구체적 컨텍스트, Opus 4.6 최적 활용법 (BP-11~15)</li><li><strong>워크플로우</strong>: 탐색-계획-구현-커밋 4단계, 실행 모드 선택, 비용 최적화 (BP-16~19)</li><li><strong>세션 관리</strong>: 컨텍스트 공격적 관리, 서브에이전트 위임, 체크포인트 활용 (BP-20~24)</li><li><strong>에이전트 팀</strong>: Subagent vs 팀 선택, 적정 규모 3-5명, 파일 충돌 방지 (BP-25~29)</li><li><strong>Hook & Skills</strong>: 결정적 실행을 위한 Hook, 도메인 지식 Skill 분리 (BP-30~31)</li><li><strong>자동화</strong>: Headless 모드, Writer/Reviewer 패턴, Fan-out 패턴 (BP-35~38)</li>'
  period='2026-02-25'
  audience='AI 코딩 도구 사용자, 개발자, DevOps 엔지니어'
%}

---

## Part 1. 핵심 원칙

### Claude Code는 챗봇이 아니라 에이전트다

> "질문에 답하고 기다리는 챗봇이 아닙니다. 원하는 것을 설명하면 Claude가 탐색하고, 계획하고, 구현합니다."
> — Anthropic 공식 문서

단순히 코드를 물어보는 도구가 아니라, 파일을 읽고, 명령어를 실행하고, 코드를 변경하고, 자율적으로 문제를 해결하는 **에이전트**입니다. 이 관점이 모든 Best Practice의 출발점입니다.

### 가장 중요한 제약: 컨텍스트 윈도우

> "대부분의 베스트 프랙티스는 하나의 제약에 기반합니다: Claude의 컨텍스트 윈도우는 빠르게 채워지고, 채워질수록 성능이 저하됩니다."
> — Anthropic 공식 Best Practices

컨텍스트 윈도우는 전체 대화, 읽은 파일, 명령어 출력을 모두 포함합니다. 디버깅 세션 하나에도 수만 토큰이 소비됩니다. **컨텍스트를 관리하는 것이 곧 성능을 관리하는 것**입니다.

---

## Part 2. 환경 설정 Best Practices

### BP-01. 필수 환경 변수 3가지

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80"
  }
}
```

| 변수 | 왜 설정하는가 |
|------|-------------|
| `AGENT_TEAMS=1` | 여러 Claude 인스턴스가 팀으로 협업 가능. 병렬 리뷰, 디버깅 등에 필수 |
| `MAX_OUTPUT_TOKENS=64000` | 기본값보다 높여서 긴 코드 생성, 상세 분석 시 잘림 방지 |
| `AUTOCOMPACT_PCT=80` | 컨텍스트 80% 차면 자동 압축. 긴 세션에서도 성능 저하 없이 작업 지속 |

### BP-02. 권한은 넓게, 보안이 필요하면 Sandbox로

```json
// 개발 환경 - 빠른 작업에 최적
{
  "permissions": {
    "allow": [
      "Bash(*)", "Edit(*)", "Write(*)", "NotebookEdit(*)",
      "WebFetch(*)", "WebSearch(*)",
      "mcp__playwright__*", "mcp__filesystem__*",
      "mcp__context7__*"
    ]
  }
}
```

**원칙**: 반복적인 승인 요청은 집중을 방해합니다. 개발 환경에서는 넓게 허용하고, 민감한 작업에는 `/sandbox`로 OS 수준 격리를 사용합니다.

```bash
# 보안이 필요한 환경에서는
/sandbox              # OS 수준 격리 활성화
# 또는 특정 도구만 허용
claude --allowedTools "Edit,Bash(npm test *)"
```

### BP-03. 상태라인으로 토큰 실시간 모니터링

Claude Code는 커스텀 상태라인을 지원합니다. 현재 모드, 활성 에이전트 수, 토큰 사용량을 실시간으로 추적할 수 있습니다.

```json
{
  "statusLine": {
    "type": "command",
    "command": "node path/to/your-hud-script.mjs"
  }
}
```

> 공식 문서에서도 "컨텍스트 사용량을 커스텀 상태라인으로 지속적으로 추적하라"고 권장합니다.

### BP-04. MCP 서버로 외부 도구 연동

```json
// ~/.claude/settings.local.json
{
  "enabledMcpjsonServers": ["context7", "filesystem"],
  "enableAllProjectMcpServers": true
}
```

| MCP 서버 | Best Practice |
|----------|--------------|
| **Context7** | 라이브러리 문서를 물어볼 때 자동으로 최신 공식 문서를 조회. 오래된 답변 방지 |
| **Filesystem** | 파일 탐색/읽기/쓰기를 MCP를 통해 안전하게 수행 |
| **Playwright** | UI 변경 후 스크린샷으로 시각적 검증. 공식 가이드에서 강력 권장 |

### BP-05. 플러그인으로 기능 확장

Claude Code는 플러그인 시스템을 지원합니다. 마켓플레이스에서 필요한 플러그인을 검색하여 설치할 수 있습니다.

```bash
# 플러그인 탐색
/plugin    # 마켓플레이스에서 검색
```

주요 플러그인 카테고리:
- **에이전트 오케스트레이션**: 특화 에이전트, 실행 모드, 자동 모델 라우팅
- **HUD/상태라인**: 실시간 상태 디스플레이
- **코드 인텔리전스**: 정적 분석, 코드 품질 도구

---

## Part 3. CLAUDE.md Best Practices

### BP-06. 프로젝트마다 CLAUDE.md 생성

```bash
# 프로젝트 디렉토리에서 실행 → 빌드 시스템, 테스트 프레임워크, 코드 패턴을 분석하여 자동 생성
/init
```

### BP-07. 배치 위치별 역할 구분

| 위치 | 역할 | git 포함 |
|------|------|:--:|
| `~/.claude/CLAUDE.md` | 모든 세션에 적용되는 개인 글로벌 설정 | X |
| `./CLAUDE.md` | 팀 공유 프로젝트 규칙 | O |
| `./CLAUDE.local.md` | 개인 오버라이드 (.gitignore 추가) | X |
| 하위 디렉토리 | 해당 디렉토리 작업 시 자동 로드 | O |

### BP-08. 간결하게 유지 (핵심 규칙만)

**포함해야 할 것**:
- Claude가 코드만 보고는 알 수 없는 Bash 명령어
- 기본값과 다른 코드 스타일 규칙
- 테스트 실행 방법, 선호 테스트 러너
- 브랜치 네이밍, PR 컨벤션
- 프로젝트 고유 아키텍처 결정사항

**제외해야 할 것**:
- 코드를 읽으면 알 수 있는 것 (Claude가 이미 파악 가능)
- 표준 언어 규칙 (Claude가 이미 앎)
- 상세한 API 문서 (링크로 대체)
- "깨끗한 코드를 작성하라" 같은 자명한 것

```markdown
# 좋은 예시
# Code style
- Use ES modules (import/export), not CommonJS (require)
- Destructure imports when possible

# Workflow
- Typecheck after code changes: npm run typecheck
- Run single tests, not the whole suite: npm test -- --testPathPattern=<file>
```

> **핵심**: 각 줄에 대해 "이걸 제거하면 Claude가 실수할까?" 아니면 삭제. **너무 길면 Claude가 중요한 규칙을 무시합니다!**

### BP-09. `@` 구문으로 외부 파일 임포트

```markdown
See @README.md for project overview and @package.json for available npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides: @~/.claude/my-project-instructions.md
```

### BP-10. 강조로 준수율 향상

```markdown
# IMPORTANT: Always run tests before committing
# YOU MUST use the existing error handling pattern in src/utils/errors.ts
```

---

## Part 4. 프롬프팅 Best Practices

### BP-11. 검증 수단을 반드시 제공하라 (최고 효과)

> "Claude가 스스로 작업을 검증할 수 있을 때 극적으로 더 좋은 결과를 냅니다. 이것이 가장 높은 효과를 내는 단일 조치입니다."
> — Anthropic 공식 Best Practices

| 패턴 | Bad | Good |
|------|:--:|:--:|
| **함수 구현** | "이메일 검증 함수 만들어" | "validateEmail 함수 작성해. **구현 후 테스트 실행해**" |
| **UI 변경** | "대시보드 좀 더 보기 좋게" | "[스크린샷 첨부] 이 디자인 구현해. **결과 스크린샷 찍고 원본과 비교해**" |
| **버그 수정** | "빌드가 안 돼" | "빌드가 이 에러로 실패: [에러]. **수정 후 빌드 성공 확인해. 에러 억제 말고 근본 원인 해결해**" |

### BP-12. 구체적 컨텍스트를 프롬프트에 포함

| 전략 | Bad | Good |
|------|:--:|:--:|
| **범위 지정** | "foo.py에 테스트 추가해" | "foo.py에서 **로그아웃 엣지 케이스** 테스트 작성. **mock 사용 안 함**" |
| **출처 지정** | "이 API 왜 이상해?" | "ExecutionFactory의 **git history 살펴보고** API 변천사 요약해" |
| **패턴 참조** | "캘린더 위젯 추가해" | "**HotDogWidget.php 패턴**을 따라서 캘린더 위젯 구현해" |
| **증상 설명** | "로그인 버그 수정" | "세션 타임아웃 후 로그인 실패. src/auth/ **토큰 리프레시** 확인" |

### BP-13. 풍부한 입력 활용

```bash
# 파일 직접 참조 (경로 설명 대신)
@src/auth/handler.ts

# 이미지 붙여넣기 (복사/붙여넣기, 드래그 앤 드롭)

# 에러 로그 파이프
cat error.log | claude

# URL로 문서 제공
> 이 API 문서를 참고해서 구현해: https://docs.example.com/api

# Claude가 직접 조회하게
> gh issue view 123 의 내용을 읽고 해결해
```

### BP-14. 역할 설정 대신 작업을 명확히 (Opus 4.6)

```
# Bad - 불필요한 역할 설정
"너는 시니어 풀스택 개발자야. React와 TypeScript 전문가로서..."

# Good - 바로 작업 내용
"이 함수의 에러 핸들링을 개선하되, 기존 API 계약은 유지해"
```

Opus 4.6은 역할 프롬프트 없이도 맥락을 파악합니다. 범위, 제약, 검증 기준을 명확히 하는 것이 더 효과적입니다.

### BP-15. 큰 기능은 Claude에게 먼저 인터뷰시키기

```
실시간 알림 시스템을 구현하고 싶어. AskUserQuestion 도구로 나를 자세히 인터뷰해줘.

기술 구현, UI/UX, 엣지 케이스, 트레이드오프에 대해 질문해.
뻔한 질문은 하지 말고, 내가 고려하지 못했을 어려운 부분을 파고들어.

모든 것을 다룰 때까지 인터뷰하고, 완료되면 SPEC.md에 전체 스펙을 작성해.
```

스펙 완성 후 **새 세션**에서 구현 시작 → 클린 컨텍스트에서 구현에만 집중.

---

## Part 5. 워크플로우 Best Practices

### BP-16. 탐색 - 계획 - 구현 - 커밋 (공식 4단계)

```
1. 탐색 (Plan Mode: Ctrl+G)
   "src/auth를 읽고 세션과 로그인 처리 방식을 이해해"

2. 계획 (Plan Mode)
   "Google OAuth 추가하려면 어떤 파일 변경? 계획 만들어"
   → Ctrl+G로 계획을 에디터에서 직접 편집 가능

3. 구현 (Normal Mode)
   "계획대로 구현해. 콜백 핸들러 테스트 작성하고 실행해"

4. 커밋
   "설명적 커밋 메시지로 커밋하고 PR 열어"
```

> **Tip**: 범위가 명확하고 작은 수정이면 (오타, 로그 추가, 변수명 변경) 계획을 건너뛰세요. 계획은 **접근법이 불확실하거나, 여러 파일 수정이거나, 코드에 익숙하지 않을 때** 유용합니다.

### BP-17. 실행 모드를 작업 복잡도에 맞게 선택

```
간단한 질문/수정      → 일반 모드 (기본)
새 기능 프로토타입     → autopilot 모드
중규모 기능 개발      → autopilot 또는 ultrawork 모드
대규모 리팩토링       → ultrawork (최대 병렬)
복잡한 버그 (끈질기게) → ralph 모드 (목표 달성까지 반복)
비용 절감 필요        → ecomode (Haiku+Sonnet 조합)
품질 보증/테스트      → ultraqa (테스트→검증→수정 반복)
대규모 마이그레이션    → swarm (N개 에이전트 공유 작업)
순차 파이프라인       → pipeline
```

### BP-18. 계획은 검증까지 포함

```bash
# Bad - 구현만 요청
> OAuth 구현해

# Good - 계획 → 리뷰 → 구현 → 검증
> 1) OAuth 구현 계획 수립
> 2) 계획 리뷰
> 3) 계획대로 구현
> 4) 코드 리뷰
> 5) 보안 리뷰
```

### BP-19. 에이전트 비용 최적화 (모델 라우팅)

```
비용 효율 피라미드:

        ┌────────┐
        │  Opus  │  ← 아키텍처 설계, 보안 리뷰, 복잡한 디버깅만
        │ (고비용) │
       ┌┴────────┴┐
       │  Sonnet  │  ← 코드 구현, 리뷰, 테스트 (표준 작업)
       │ (중비용)  │
      ┌┴──────────┴┐
      │   Haiku    │  ← 파일 탐색, 간단한 조회, 문서 작성
      │  (저비용)   │
      └────────────┘
```

자동 라우팅 원칙:

```json
{
  "quick-lookup": "haiku",
  "standard-work": "sonnet",
  "complex-reasoning": "opus",
  "security-review": "opus",
  "code-review": "sonnet"
}
```

---

## Part 6. 세션 관리 Best Practices

### BP-20. 컨텍스트를 공격적으로 관리하라

| 상황 | 행동 |
|------|------|
| 관련 없는 작업으로 전환할 때 | `/clear` |
| 같은 문제를 두 번 이상 수정 실패 | `/clear` + 더 나은 프롬프트로 재시작 |
| 세션이 길어질 때 | `/compact API 변경에 집중` (수동 압축) |
| 대화 일부만 정리하고 싶을 때 | `Esc+Esc` → 메시지 선택 → **Summarize from here** |

> **핵심 규칙**: 두 번 수정 실패하면 더 이상 수정하지 말고 `/clear` 후 배운 것을 반영한 새 프롬프트로 재시작. **깨끗한 세션 + 좋은 프롬프트가 오염된 세션 + 반복 수정보다 거의 항상 낫습니다.**

### BP-21. 서브에이전트로 탐색을 위임

컨텍스트가 근본적 제약이므로, 탐색은 **서브에이전트에 위임**하여 메인 컨텍스트를 보호합니다:

```bash
# 탐색 위임 → 메인 컨텍스트 깨끗
> 서브에이전트를 사용해서 인증 시스템의 토큰 리프레시 방식과
  재사용 가능한 OAuth 유틸리티가 있는지 조사해줘

# 구현 후 검증도 서브에이전트로
> 서브에이전트로 이 코드의 엣지 케이스를 리뷰해줘
```

### BP-22. 세션을 브랜치처럼 관리

```bash
claude --continue    # 가장 최근 대화 재개
claude --resume      # 세션 목록에서 선택

/rename oauth-migration   # 세션에 설명적 이름 부여
```

다른 작업 흐름은 별도 세션으로 관리하면 지속적인 컨텍스트를 유지할 수 있습니다.

### BP-23. 체크포인트로 부담 없이 실험

Claude는 변경 전 자동으로 체크포인트를 생성합니다:

```
Esc + Esc 또는 /rewind  →  되돌리기 메뉴
  ├── 대화만 복원
  ├── 코드만 복원
  ├── 둘 다 복원
  └── 선택 지점부터 요약
```

> **Tip**: 위험한 시도도 부담 없이 하세요. 안 되면 되돌리고 다른 접근법을 시도하면 됩니다. 체크포인트는 세션 종료 후에도 유지됩니다.

### BP-24. 자동 압축 시 중요 정보 보존

CLAUDE.md에 다음을 추가하면 압축 시 핵심 컨텍스트가 살아남습니다:

```markdown
# Compaction rules
When compacting, always preserve:
- The full list of modified files
- Test commands and their results
- Key architectural decisions made in this session
```

---

## Part 7. 에이전트 팀 Best Practices (공식)

### BP-25. Subagent vs 에이전트 팀 선택 기준

| | Subagents | 에이전트 팀 |
|:--|:--|:--|
| **컨텍스트** | 결과만 메인에 반환 | 완전히 독립적 |
| **통신** | 메인 에이전트에게만 보고 | 팀원끼리 직접 메시지 |
| **조율** | 메인이 관리 | 공유 작업 목록으로 자체 조율 |
| **토큰 비용** | 낮음 | 높음 (각각 별도 인스턴스) |
| **선택 기준** | 결과만 필요한 집중 작업 | 토론/협업이 필요한 복잡한 작업 |

```
결과만 보고받으면 충분      → Subagent
팀원 간 토론/도전이 필요    → 에이전트 팀
구조화된 파이프라인 필요    → 팀 프리셋
```

### BP-26. 에이전트 팀 적정 규모: 3-5명

- 팀원당 5-6개 작업 유지
- 15개 독립 작업이 있으면 3명이 적정
- **세 명의 집중된 팀원이 다섯 명의 산만한 팀원보다 나음**

### BP-27. 파일 충돌 방지

두 팀원이 같은 파일을 편집하면 덮어쓰기 발생. **각 팀원이 다른 파일 집합을 소유**하도록 분할:

```bash
> 에이전트 팀을 만들어줘:
  - 팀원 A: src/api/ 디렉토리 담당
  - 팀원 B: src/components/ 디렉토리 담당
  - 팀원 C: tests/ 디렉토리 담당
```

### BP-28. 팀원에게 충분한 컨텍스트 제공

팀원은 리더의 대화 기록을 상속하지 않습니다. 생성 프롬프트에 작업 세부사항을 포함하세요:

```bash
# Bad
> 보안 리뷰 팀원 추가해

# Good
> 보안 리뷰어 팀원을 생성해. 프롬프트:
  "src/auth/의 인증 모듈 보안 취약점을 리뷰해.
   토큰 핸들링, 세션 관리, 입력 검증에 집중.
   앱은 httpOnly 쿠키에 JWT를 저장. 심각도 등급과 함께 보고해."
```

### BP-29. 연구/리뷰부터 시작

에이전트 팀을 처음 사용할 때는 **코드 작성이 없는 작업**으로 시작:
- PR 검토, 라이브러리 연구, 버그 조사
- 병렬 탐색의 가치를 파악한 후 구현 작업으로 확장

---

## Part 8. Hook & Skills Best Practices

### BP-30. 반드시 실행되어야 하는 것은 Hook으로

> "CLAUDE.md 지시사항은 권고적이지만, Hook은 결정적(deterministic)입니다."

```bash
# Claude가 Hook을 작성해줌
> "파일 편집 후 매번 eslint를 실행하는 Hook을 작성해줘"
> "migrations 폴더에 쓰기를 차단하는 Hook을 작성해줘"

# 대화형 설정
/hooks
```

### Hook 이벤트 종류

| 이벤트 | 사용 예 |
|--------|---------|
| `SessionStart` | 이전 세션 상태 복원 |
| `UserPromptSubmit` | 매직 키워드 감지, 스킬 자동 주입 |
| `PreToolUse` | 특정 디렉토리 쓰기 차단, 규칙 강제 |
| `PostToolUse` | 결과 검증, 린트 자동 실행 |
| `SubagentStart/Stop` | 에이전트 추적 |
| `PreCompact` | 압축 전 중요 상태 보존 |
| `Stop` | 미완료 작업 감지, 영속 모드 유지 |

### BP-31. 도메인 지식은 Skill로

매 세션에 로드되는 CLAUDE.md와 달리, **Skill은 관련 있을 때만 자동 로드**됩니다:

```markdown
# .claude/skills/api-conventions/SKILL.md
---
name: api-conventions
description: REST API design conventions
---
- Use kebab-case for URL paths
- Use camelCase for JSON properties
- Always include pagination for list endpoints
```

반복 가능한 워크플로우도 Skill로 정의:

```markdown
# .claude/skills/fix-issue/SKILL.md
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
1. `gh issue view` → 이슈 상세 확인
2. 코드베이스에서 관련 파일 검색
3. 수정 구현
4. 테스트 작성 및 실행
5. 커밋 후 PR 생성
```

```bash
/fix-issue 1234    # 직접 호출
```

---

## Part 9. OpenCode Best Practices

### BP-32. 작업에 따라 도구 선택

```
┌─────────────────────────────────────────┐
│         작업 유형별 도구 선택               │
├─────────────────────────────────────────┤
│                                         │
│  복잡한 코딩/아키텍처  → Claude Code      │
│    (Opus 4.6 + 에이전트 팀)              │
│                                         │
│  빠른 코드 생성       → OpenCode         │
│    (Gemini Flash / GPT Codex)           │
│                                         │
│  대용량 컨텍스트      → OpenCode         │
│    (1M 토큰 컨텍스트)                    │
│                                         │
│  보안/품질 리뷰       → Claude Code      │
│    (Opus + security-reviewer)           │
│                                         │
│  UI/UX 개발          → 둘 다 활용        │
│    Claude: designer + OpenCode: Gemini  │
│                                         │
└─────────────────────────────────────────┘
```

### BP-33. OpenCode 에이전트 역할 분담

| 에이전트 | 모델 | Best Practice |
|---------|------|--------------|
| **sisyphus** | 기본 | 메인 작업. 복잡한 구현은 이 에이전트로 |
| **explore** | Gemini Flash | 빠른 코드베이스 탐색. 구조 파악에 먼저 사용 |
| **frontend** | Gemini Pro High | UI 작업은 전용 에이전트로. 고품질 모델 활용 |
| **document-writer** | Gemini Flash | 문서 작성은 Flash로 비용 절감 |
| **librarian** | GLM 4.7 | 지식 검색. 무료 모델로 비용 없이 활용 |
| **multimodal** | Gemini Flash | 이미지/스크린샷 분석 |

### BP-34. Claude Code와 OpenCode 비교

| 항목 | Claude Code | OpenCode |
|------|------------|----------|
| **모델** | Claude 전용 (Opus/Sonnet/Haiku) | 멀티 (Gemini, GPT 등) |
| **에이전트** | Agent Teams + 서브에이전트 | 7개 에이전트 |
| **MCP** | 네이티브 지원 | 제한적 |
| **컨텍스트** | 200K 토큰 | 최대 1M 토큰 |
| **Hook/플러그인** | 포괄적 시스템 | 기본적 |
| **강점** | 안정성, 에이전트 오케스트레이션 | 모델 다양성, 대용량 |

---

## Part 10. 자동화 & 스케일링 Best Practices

### BP-35. Headless 모드로 CI/스크립트 통합

```bash
# 일회성 쿼리
claude -p "이 프로젝트가 무엇을 하는지 설명해"

# 구조화된 출력 (스크립트 파싱용)
claude -p "모든 API 엔드포인트를 나열해" --output-format json

# 실시간 스트리밍
claude -p "이 로그 파일을 분석해" --output-format stream-json

# 파이프라인 연결
claude -p "<프롬프트>" --output-format json | your_command
```

### BP-36. Writer/Reviewer 패턴으로 품질 향상

```
세션 A (Writer): "API rate limiter 구현해"
          ↓ 완료
세션 B (Reviewer): "@src/middleware/rateLimiter.ts 리뷰해.
                    엣지 케이스, 레이스 컨디션, 미들웨어 패턴 일관성 확인"
          ↓ 피드백
세션 A (Writer): "리뷰 피드백 반영해: [피드백 내용]"
```

> **왜 효과적인가**: 새 컨텍스트는 Claude가 자신이 작성한 코드에 편향되지 않게 합니다.

### BP-37. 대규모 Fan-out 패턴

```bash
# 1. 작업 목록 생성
claude -p "마이그레이션 필요한 파일 목록을 files.txt에 작성해"

# 2. 병렬 처리
for file in $(cat files.txt); do
  claude -p "Migrate $file to TypeScript. Return OK or FAIL." \
    --allowedTools "Edit,Bash(npx tsc *)"
done

# 3. 2-3개로 먼저 테스트 → 프롬프트 조정 → 전체 실행
```

### BP-38. 팀 프리셋으로 반복 워크플로우 자동화

워크플로우별 에이전트 파이프라인을 프리셋으로 정의하여 재사용할 수 있습니다:

```
코드 리뷰:    explore → architect → critic → executor
기능 구현:    planner → executor → tdd-guide
디버깅:       explore → architect → build-fixer
리서치:       parallel(researcher, explore) → architect → writer
리팩토링:     explore → architect → executor → qa-tester
보안 감사:    explore → security-reviewer → executor → security-reviewer
```

---

## Part 11. 흔한 실패 패턴과 해결법

### 자기 진단 체크리스트

| # | 증상 | 원인 | 해결 |
|:-:|------|------|------|
| 1 | 세션에서 여러 주제를 섞어서 작업 | **Kitchen Sink 세션**: 컨텍스트가 무관한 정보로 가득 | `/clear`로 작업 사이에 초기화 |
| 2 | 같은 실수를 반복 수정 중 | **무한 수정 루프**: 실패한 접근들이 컨텍스트 오염 | 2번 실패하면 `/clear` + 더 나은 프롬프트 |
| 3 | Claude가 CLAUDE.md 규칙을 무시 | **비대한 CLAUDE.md**: 중요한 규칙이 노이즈에 묻힘 | 과감히 정리. Hook으로 변환 |
| 4 | 구현이 그럴듯하지만 엣지 케이스 누락 | **검증 공백**: 테스트 없이 수락 | 항상 검증 제공 (테스트/스크린샷) |
| 5 | Claude가 수백 개 파일을 읽으며 멈춤 | **무한 탐색**: 범위 없는 조사 | 범위 좁히기 또는 서브에이전트 위임 |

### 직감 개발하기 (공식 가이드)

> "이 가이드의 패턴은 시작점이지 절대 규칙이 아닙니다."

- 때로는 컨텍스트를 쌓는 것이 맞음 (하나의 복잡한 문제에 깊이 파고들 때)
- 때로는 계획을 건너뛰는 것이 맞음 (탐색적인 작업일 때)
- 때로는 모호한 프롬프트가 맞음 (Claude의 해석을 먼저 보고 싶을 때)

**좋은 결과가 나왔을 때** 무엇을 했는지 관찰하세요: 프롬프트 구조, 제공한 컨텍스트, 사용한 모드. **실패했을 때** 원인을 분석하세요: 컨텍스트가 너무 시끄러웠는지, 프롬프트가 모호했는지, 작업이 한 번에 하기엔 컸는지.

---

## 부록 A. 빠른 참조 카드

### 키보드 단축키

| 단축키 | 동작 |
|--------|------|
| `Ctrl+G` | Plan Mode 토글 |
| `Esc` | 현재 작업 중단 (컨텍스트 유지) |
| `Esc + Esc` | 되돌리기 메뉴 |
| `Shift+Down` | 에이전트 팀 팀원 순환 |
| `Ctrl+T` | 작업 목록 토글 (에이전트 팀) |

### Claude Code 내장 커맨드

| 명령어 | 설명 | 사용 시점 |
|--------|------|----------|
| `/init` | CLAUDE.md 자동 생성 | 새 프로젝트 시작 |
| `/clear` | 컨텍스트 초기화 | 작업 전환, 실패 누적 시 |
| `/compact <지시>` | 수동 컨텍스트 압축 | 긴 세션에서 핵심만 보존 |
| `/rewind` | 체크포인트 되돌리기 | 코드/대화 복구 |
| `/permissions` | 권한 설정 | 도구 허용/차단 설정 |
| `/hooks` | Hook 대화형 설정 | 자동화 규칙 추가 |
| `/sandbox` | OS 수준 격리 | 보안 민감 작업 |
| `/plugin` | 플러그인 마켓플레이스 | 기능 확장 |
| `/rename` | 세션 이름 변경 | 세션 관리 |

### CLI 실행 옵션

| 명령어 | 용도 |
|--------|------|
| `claude` | 대화형 세션 시작 |
| `claude --continue` | 마지막 세션 재개 |
| `claude --resume` | 세션 선택 재개 |
| `claude -p "prompt"` | Headless 모드 (CI/스크립트) |
| `claude -p "..." --output-format json` | JSON 출력 |
| `claude -p "..." --output-format stream-json` | 스트리밍 JSON |
| `claude --allowedTools "Edit,Bash(...)"` | 도구 제한 (Fan-out 시) |
| `opencode` | OpenCode 실행 |

---

## 부록 B. 설정 파일 위치

| 파일 | 경로 | 역할 |
|------|------|------|
| 전역 설정 | `~/.claude/settings.json` | 환경변수, 권한, 플러그인 |
| 로컬 설정 | `~/.claude/settings.local.json` | MCP 서버 |
| 글로벌 CLAUDE.md | `~/.claude/CLAUDE.md` | 개인 글로벌 지시사항 |
| 프로젝트 CLAUDE.md | `./CLAUDE.md` | 프로젝트별 규칙 |
| OpenCode 설정 | `~/.config/opencode/opencode.json` | 프로바이더, 모델 |
| 커스텀 에이전트 | `.claude/agents/` | 프로젝트별 서브에이전트 |
| Skills | `.claude/skills/` | 프로젝트별 스킬 |

---

## 참조 링크

- [Claude Code 공식 Best Practices](https://code.claude.com/docs/en/best-practices)
- [에이전트 팀 공식 문서 (한국어)](https://code.claude.com/docs/ko/agent-teams)
- [Claude Opus 4.6 활용 가이드](https://news.hada.io/topic?id=26459)
- [Claude Code 작동 원리](https://code.claude.com/docs/en/how-claude-code-works)
- [CLAUDE.md 가이드](https://code.claude.com/docs/en/memory)
- [Hook 가이드](https://code.claude.com/docs/en/hooks-guide)
- [Skills 가이드](https://code.claude.com/docs/en/skills)
- [Subagents 가이드](https://code.claude.com/docs/en/sub-agents)
- [Plugins 가이드](https://code.claude.com/docs/en/plugins)
- [Claude Code 확장하기](https://code.claude.com/docs/en/features-overview)

---

> 이 문서는 Anthropic 공식 Best Practices, 에이전트 팀 문서, Opus 4.6 가이드를 기반으로 실무 경험을 종합하여 작성되었습니다. 번호(BP-01~38)로 특정 항목을 빠르게 참조할 수 있습니다.
