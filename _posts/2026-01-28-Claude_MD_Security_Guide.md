---
layout: post
title: "CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계"
date: 2026-01-28 18:30:00 +0900
categories: [security, devsecops]
tags: [CLAUDE.md, AI-Security, Claude-Code, DevSecOps, Security-Guidelines, AI-Agent, Prompt-Engineering, "2026"]
excerpt: "CLAUDE.md와 AGENTS.md로 AI 에이전트 보안 가이드라인 구축. Security-First 원칙과 실무 구현"
description: "AI 에이전트(Claude Code, Cursor, Copilot)와 협업하는 프로젝트의 보안 가이드라인. CLAUDE.md 작성법, Never Hardcode Secrets, 로그 마스킹, 입력 검증, Pre-commit 자동화"
keywords: [CLAUDE.md, AGENTS.md, AI Security, Claude Code, DevSecOps, Security Guidelines, AI Agent, 보안 가이드라인]
author: Twodragon
comments: true
image: /assets/images/2026-01-28-Claude_MD_Security_Guide.svg
image_alt: "CLAUDE.md Security Guide - AI Agent Security Guidelines Never Hardcode Secrets Log Masking Input Validation"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">CLAUDE.md</span> <span class="tag">AI-Security</span> <span class="tag">Claude-Code</span> <span class="tag">DevSecOps</span> <span class="tag">Security-Guidelines</span> <span class="tag">AI-Agent</span> <span class="tag">Prompt-Engineering</span> <span class="tag">2026</span>'
  highlights_html='<li><strong>CLAUDE.md / AGENTS.md 보안 가이드라인 설계</strong>: AI 에이전트가 API 키 하드코딩, 로그 민감정보 노출, 검증 없는 외부 라이브러리 도입 등의 보안 실수를 반복하지 않도록 지시 파일에 Security-First 원칙을 명시하는 구체적 작성법 제시</li>
      <li><strong>Never Hardcode &amp; 로그 마스킹 패턴</strong>: os.getenv() 기반 환경 변수 관리, mask_sensitive_info()로 로그 마스킹, _validate_masked_text()로 파일 저장 전 검증하는 Python/JavaScript 실무 코드 패턴 수록</li>
      <li><strong>Pre-commit 보안 자동화 체크리스트</strong>: 비밀 키 탐지(git-secrets), 이미지 파일명 영문 확인, SVG 한글 텍스트 금지, 코드 블록 언어 태그 필수, CSP 헤더 검토 등 커밋 전 자동 검증 파이프라인 구축 방법</li>'
  period='2026-01-28 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## 서론

안녕하세요, **Twodragon**입니다.

2025년부터 **Claude Code**, **Cursor**, **GitHub Copilot** 등 AI 코딩 에이전트가 개발 현장에 빠르게 확산되고 있습니다. 이러한 AI 에이전트들은 코드 생성, 리팩토링, 버그 수정에서 놀라운 생산성을 보여주지만, 동시에 새로운 보안 위협을 야기합니다.

**핵심 문제:**
- AI가 민감한 API 키를 코드에 하드코딩
- 로그에 비밀번호나 토큰 노출
- 검증 없이 외부 라이브러리 도입
- 보안 취약점이 있는 코드 패턴 생성

이 문제를 해결하기 위해 **CLAUDE.md**와 **AGENTS.md** 파일을 활용한 **AI 에이전트 보안 가이드라인**을 소개합니다.

### 이 가이드에서 다루는 내용

| 섹션 | 내용 |
|------|------|
| **CLAUDE.md 개요** | AI 에이전트 지시 파일의 역할과 구조 |
| **Security First 원칙** | 하드코딩 방지, 마스킹, 입력 검증 |
| **실무 구현** | Python/JavaScript 보안 코드 패턴 |
| **체크리스트** | Pre-commit 보안 검증 자동화 |
| **Best Practices** | AI 협업 시 보안 모범 사례 |

---

## 1. CLAUDE.md란 무엇인가?

### 1.1 AI 에이전트 지시 파일의 진화

![AI Agent Instruction File Evolution - From .editorconfig to CLAUDE.md/AGENTS.md](/assets/images/diagrams/2026-01-28-ai-agent-instruction-evolution.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```
AI Agent Instruction File Evolution:
2023: .editorconfig → Simple formatting rules
2024: .cursorrules → Basic AI instructions
2025-2026: CLAUDE.md / AGENTS.md → Security + Cost + Operations integrated
```

</details>

**CLAUDE.md**는 Claude Code CLI가 프로젝트에서 작업할 때 참조하는 **지시 파일**입니다. 단순한 코딩 스타일 가이드를 넘어, **보안 정책**, **비용 최적화**, **운영 효율성**을 모두 포함하는 종합 가이드라인입니다.

### 1.2 CLAUDE.md vs AGENTS.md

| 파일 | 대상 | 목적 | 상세도 |
|------|------|------|--------|
| **CLAUDE.md** | Claude Code CLI | 프로젝트 전반 지시 | 핵심 원칙 중심 |
| **AGENTS.md** | 모든 AI 에이전트 | 기술적 구현 가이드 | 상세 구현 포함 |
| **.cursorrules** | Cursor IDE | Cursor 전용 설정 | IDE 최적화 |

### 1.3 파일 위치와 우선순위

```
project-root/
├── CLAUDE.md              # 프로젝트 루트 (최우선)
├── .claude/
│   └── CLAUDE.md          # .claude 디렉토리 (2순위)
├── AGENTS.md              # 범용 AI 에이전트 가이드
└── .cursorrules           # Cursor 전용
```

**우선순위**: 프로젝트 루트 > .claude 디렉토리 > 전역 설정

---

## 2. Security First 핵심 원칙

### 2.1 절대 규칙: Never Hardcode Secrets

AI 에이전트가 가장 많이 실수하는 부분이 **민감 정보 하드코딩**입니다.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # ❌ 절대 금지 - AI가 종종 이렇게 생성함...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # ❌ 절대 금지 - AI가 종종 이렇게 생성함...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # ❌ 절대 금지 - AI가 종종 이렇게 생성함 [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# ❌ 절대 금지 - AI가 종종 이렇게 생성함
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# ✅ 올바른 방법 - 환경 변수 사용
import os

API_KEY = os.getenv("API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 키가 없으면 명시적 에러
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")


```
-->
-->
-->

**CLAUDE.md에 명시할 내용:**

```markdown
## Security First
- **Never hardcode** API keys, passwords, tokens
- Use `os.getenv("API_KEY", "")` for sensitive data
- Raise explicit error if required key is missing
```

### 2.2 로그 마스킹 (Log Masking)

AI가 생성한 로깅 코드는 종종 민감 정보를 그대로 출력합니다.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> import re...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> import re...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> import re [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
import re
from typing import Optional

# 마스킹 패턴 정의
SENSITIVE_PATTERNS = [
    (r'(api[_-]?key["\s:=]+)["\']?[\w-]{20,}["\']?', r'\1***MASKED***'),
    (r'(password["\s:=]+)["\']?[^\s"\']+["\']?', r'\1***MASKED***'),
    (r'(token["\s:=]+)["\']?[\w-]{20,}["\']?', r'\1***MASKED***'),
    (r'(bearer\s+)[\w-]{20,}', r'\1***MASKED***', re.IGNORECASE),
    (r'(sk-)[a-zA-Z0-9]{20,}', r'\1***MASKED***'),  # OpenAI API Key
    (r'(ghp_)[a-zA-Z0-9]{36}', r'\1***MASKED***'),  # GitHub Token
    (r'(gho_)[a-zA-Z0-9]{36}', r'\1***MASKED***'),  # GitHub OAuth
]

def mask_sensitive_info(text: str) -> str:
    """민감 정보를 마스킹하여 반환"""
    masked = text
    for pattern in SENSITIVE_PATTERNS:
        if len(pattern) == 3:
            masked = re.sub(pattern[0], pattern[1], masked, flags=pattern[2])
        else:
            masked = re.sub(pattern[0], pattern[1], masked)
    return masked

def _validate_masked_text(text: str) -> bool:
    """마스킹이 제대로 되었는지 검증"""
    dangerous_patterns = [
        r'sk-[a-zA-Z0-9]{20,}',  # OpenAI
        r'ghp_[a-zA-Z0-9]{36}',  # GitHub
        r'password\s*[=:]\s*["\'][^"\']+["\']',
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True

def safe_log(message: str, level: str = "INFO") -> None:
    """안전한 로깅 함수"""
    safe_message = mask_sensitive_info(message)
    if _validate_masked_text(safe_message):
        print(f"[{level}] {safe_message}")
    else:
        print(f"[{level}] [REDACTED - Sensitive info detected]")


```
-->
-->
-->

### 2.3 파일 쓰기 전 검증

AI가 생성한 설정 파일에 민감 정보가 포함되지 않도록 검증합니다.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> from pathlib import Path...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> from pathlib import Path...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> from pathlib import Path [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
from pathlib import Path

def write_safe_file(file_path: Path, content: str) -> bool:
    """민감 정보 검증 후 파일 작성"""
    # 1단계: 마스킹 시도
    safe_content = mask_sensitive_info(content)

    # 2단계: 검증
    if not _validate_masked_text(safe_content):
        raise SecurityError(
            f"Cannot write to {file_path}: "
            "Content contains unmasked sensitive information"
        )

    # 3단계: 안전한 내용만 작성
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(safe_content)

    return True

class SecurityError(Exception):
    """보안 관련 예외"""
    pass


```
-->
-->
-->

### 2.4 입력 검증 (Input Validation)

AI가 생성한 웹 엔드포인트에는 반드시 입력 검증을 추가해야 합니다.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> import re...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> import re...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> import re [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
import re
from typing import Optional

# XSS 방지 패턴
XSS_PATTERNS = [
    r'<script[^>]*>',
    r'javascript:',
    r'on\w+\s*=',
    r'<iframe',
    r'<object',
    r'<embed',
]

# SQL Injection 방지 패턴
SQL_INJECTION_PATTERNS = [
    r"('\s*(OR|AND)\s*'?\d*\s*[=<>])",
    r'(;\s*(DROP|DELETE|UPDATE|INSERT))',
    r'(UNION\s+SELECT)',
    r'(--)|(#)|(\/\*)',
]

def validate_input(user_input: str, max_length: int = 1000) -> tuple[bool, Optional[str]]:
    """
    사용자 입력 검증

    Returns:
        tuple: (is_valid, error_message)
    """
    # 길이 검증
    if len(user_input) > max_length:
        return False, f"Input exceeds maximum length of {max_length}"

    # XSS 검증
    for pattern in XSS_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Potentially malicious content detected (XSS)"

    # SQL Injection 검증
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Potentially malicious content detected (SQL Injection)"

    return True, None

def sanitize_html(html_content: str) -> str:
    """HTML 콘텐츠 sanitize"""
    import html
    # 기본 HTML 이스케이프
    sanitized = html.escape(html_content)
    return sanitized


```
-->
-->
-->

---

## 3. CLAUDE.md 실무 템플릿

### 3.1 기본 템플릿

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```markdown
# Claude Code Instructions

Instructions for Claude Code when working on this project.

**Last updated**: YYYY-MM-DD

## Project Overview

[프로젝트 설명]

- **Tech Stack**: [기술 스택]
- **Language**: [언어]
- **Hosting**: [호스팅]

## Core Principles

### 1. 보안 우선
- **Never hardcode** API keys, passwords, tokens
- Use `os.getenv("API_KEY", "")` for sensitive data
- Mask logs with `mask_sensitive_info()` before output
- Validate with `_validate_masked_text()` before file writes
- **CSP Compliance**: Review CSP headers when adding external scripts
- **Input Validation**: Always validate and sanitize user inputs
- **Error Handling**: Never expose sensitive information in error messages
- **Dependency Security**: Run `npm audit` and `bundle audit` regularly

### 2. 비용 최적화
Priority order for AI operations:
1. **Free tier first** - Gemini CLI, local processing
2. **Cache results** - 7-day TTL for API responses
3. **API calls last** - Only when necessary

### 3. 코드 품질
- Always include type hints
- Use language tags in code blocks
- Follow project naming conventions

## Security Checklist

### Pre-Commit
- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] Logs are masked
- [ ] Dependencies audited

### API Security
- [ ] Rate limiting implemented
- [ ] CORS configured correctly
- [ ] Authentication required
- [ ] Input sanitization applied


```
-->
-->
-->

### 3.2 보안 강화 섹션

```markdown
## Security Patterns

### Environment Variable Loading
\```python
import os
from typing import Optional

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

def get_optional_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)
\```

### Safe Logging
\```python
from utils.security import mask_sensitive_info, safe_log

# ❌ 절대 금지
print(f"API Key: {api_key}")
logger.info(f"Password: {password}")

# ✅ 올바른 방법
safe_log(f"Processing request with key: {api_key}")
logger.info(mask_sensitive_info(f"Auth: {token}"))
\```

### Error Handling
\```python
# ❌ 절대 금지 - 내부 정보 노출
except Exception as e:
    return {"error": str(e)}  # 스택 트레이스 노출 가능

# ✅ 올바른 방법 - 사용자 친화적 메시지
except ValueError as e:
    logger.error(f"Validation error: {mask_sensitive_info(str(e))}")
    return {"error": "Invalid input provided"}
except Exception as e:
    logger.error(f"Unexpected error: {mask_sensitive_info(str(e))}")
    return {"error": "An unexpected error occurred. Please try again."}
\```
```

---

## 4. AGENTS.md 통합 가이드

### 4.1 AGENTS.md 역할

**AGENTS.md**는 Claude뿐만 아니라 **모든 AI 에이전트**가 참조할 수 있는 범용 가이드라인입니다.

![AI Agent File Hierarchy - AGENTS.md as universal guide with tool-specific children](/assets/images/diagrams/2026-01-28-ai-agent-hierarchy.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```
AI Agent File Hierarchy:
AGENTS.md (Universal Guide)
├── CLAUDE.md (Claude-specific)
├── .cursorrules (Cursor-specific)
└── copilot.yml (Copilot-specific)
```

</details>

### 4.2 보안 섹션 예시

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```markdown
## Security Best Practices

### Input Validation
- Always validate user inputs (XSS, Injection patterns)
- Sanitize HTML content before rendering
- Validate URLs and file uploads
- Use parameterized queries for databases

### Error Handling
- Never expose sensitive info in error messages
- Log detailed errors server-side only
- Provide user-friendly error messages
- Implement automatic retry with exponential backoff

### API Security
- Rate limiting: 10 requests/minute per session
- Input validation: Check for XSS, Injection patterns
- CORS: Restrict allowed origins
- Timeout: 8 seconds (free tier safe margin)

### Dependency Security
\


```
-->
-->
-->bash
# Regular security audits
npm audit --audit-level=moderate
bundle audit --update
pip-audit

# Dependabot enabled for auto-updates
\```
```

---

## 5. 실무 체크리스트 자동화

### 5.1 Pre-commit Hook 설정

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.)
- [ ] 에러 핸들링 가이드라인 문서화

### P2 - 개선 (운영 중)

- [ ] 정기 보안 감사 스케줄 설정
- [ ] 침투 테스트 수행
- [ ] 보안 인시던트 대응 절차 문서화
- [ ] AI 생성 코드 리뷰 프로세스 정립

---

## 참고 자료

| 리소스 | 설명 | 링크 |
|--------|------|------|
| **Claude Code Docs** | 공식 Claude Code 문서 | [docs.anthropic.com](https://docs.anthropic.com/claude/docs/claude-code) |
| **OWASP Top 10** | 웹 애플리케이션 보안 위협 | [owasp.org/Top10](https://owasp.org/Top10/) |
| **Gitleaks** | 시크릿 탐지 도구 | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| **Semgrep** | 정적 분석 도구 | [semgrep.dev](https://semgrep.dev/) |
| **Pre-commit** | Git 훅 프레임워크 | [pre-commit.com](https://pre-commit.com/) |

---

## 마무리

AI 에이전트 시대에 **CLAUDE.md**와 **AGENTS.md**는 단순한 설정 파일이 아니라, 프로젝트의 **보안 정책을 AI에게 전달하는 핵심 인터페이스**입니다.

### 핵심 요약

1. 🔐 **Security First**: 하드코딩 금지, 마스킹 필수, 입력 검증
2. 📋 **명시적 지시**: AI에게 보안 요구사항을 명확히 전달
3. 🔄 **자동화**: Pre-commit, CI/CD로 보안 검증 자동화
4. 💰 **비용 균형**: Free tier 우선, 보안 유지

AI와 협업하는 개발 환경에서 보안은 선택이 아닌 필수입니다. CLAUDE.md를 통해 AI 에이전트가 처음부터 보안을 고려한 코드를 생성하도록 가이드하세요.

---

**작성자**: Twodragon
**작성일**: 2026-01-28
**카테고리**: Security, DevSecOps