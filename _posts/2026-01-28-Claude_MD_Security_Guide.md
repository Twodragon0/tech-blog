---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-01-28 18:30:00 +0900
description: AI 에이전트(Claude Code, Cursor, Copilot)와 협업하는 프로젝트의 보안 가이드라인. CLAUDE.md
  작성법, Never Hardcode Secrets, 로그 마스킹, 입력 검증, Pre-commit 자동화
excerpt: CLAUDE.md와 AGENTS.md로 AI 에이전트 보안 가이드라인 구축. Security-First 원칙과 실무 구현
image: /assets/images/2026-01-28-Claude_MD_Security_Guide.svg
image_alt: CLAUDE.md Security Guide - AI Agent Security Guidelines Never Hardcode
  Secrets Log Masking Input Validation
keywords:
- CLAUDE.md
- AGENTS.md
- AI Security
- Claude Code
- DevSecOps
- Security Guidelines
- AI Agent
- 보안 가이드라인
layout: post
schema_type: Article
tags:
- CLAUDE.md
- AI-Security
- Claude-Code
- DevSecOps
- Security-Guidelines
- AI-Agent
- Prompt-Engineering
- '2026'
title: 'CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계'
toc: true
---

## 요약

- **핵심 요약**: CLAUDE.md와 AGENTS.md로 AI 에이전트 보안 가이드라인 구축. Security-First 원칙과 실무 구현
- **주요 주제**: CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계
- **키워드**: CLAUDE.md, AI-Security, Claude-Code, DevSecOps, Security-Guidelines

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">CLAUDE.md</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Claude-Code</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Pre-commit</span>
      <span class="tag">Log-Masking</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>CLAUDE.md</strong>: Claude Code CLI가 참조하는 프로젝트 지시 파일 - 보안 정책, 비용 최적화, 운영 효율성 통합</li>
      <li><strong>Never Hardcode Secrets</strong>: os.getenv() 사용, 환경 변수로 민감 정보 관리</li>
      <li><strong>Log Masking</strong>: mask_sensitive_info() 함수로 API 키, 토큰, 비밀번호 마스킹</li>
      <li><strong>Input Validation</strong>: XSS, SQL Injection 패턴 검증, HTML sanitization</li>
      <li><strong>Pre-commit 자동화</strong>: Gitleaks, Bandit, npm audit, 커스텀 보안 스크립트</li>
      <li><strong>GitHub Actions</strong>: 자동화된 보안 스캔 워크플로우 (Semgrep, Gitleaks, pip-audit)</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">CLAUDE.md, AGENTS.md, Gitleaks, Bandit, Semgrep, Pre-commit, GitHub Actions</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">AI 에이전트 활용 개발자, DevSecOps 엔지니어, 보안 담당자, 플랫폼 엔지니어</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

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

**CLAUDE.md에 명시할 내용:**

```markdown
## Security First
- **Never hardcode** API keys, passwords, tokens
- Use `os.getenv("API_KEY", "")` for sensitive data
- Raise explicit error if required key is missing
```

### 2.2 로그 마스킹 (Log Masking)

AI가 생성한 로깅 코드는 종종 민감 정보를 그대로 출력합니다.

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

### 2.3 파일 쓰기 전 검증

AI가 생성한 설정 파일에 민감 정보가 포함되지 않도록 검증합니다.

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

### 2.4 입력 검증 (Input Validation)

AI가 생성한 웹 엔드포인트에는 반드시 입력 검증을 추가해야 합니다.

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

---

## 3. CLAUDE.md 실무 템플릿

### 3.1 기본 템플릿

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
1. **Free tier first** - Gemini CLI, local processing
2. **Cache results** - 7-day TTL for API responses
3. **API calls last** - Only when necessary

### 3. Code Quality
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
\```bash
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

```yaml
# .pre-commit-config.yaml
repos:
  # 시크릿 탐지
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  # Python 보안 검사
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: ["-r", "scripts/", "-ll"]

  # 의존성 취약점 검사
  - repo: local
    hooks:
      - id: npm-audit
        name: npm audit
        entry: npm audit --audit-level=high
        language: system
        pass_filenames: false
        files: package\.json$

  # 커스텀 보안 검증
  - repo: local
    hooks:
      - id: security-check
        name: Custom Security Check
        entry: python3 scripts/security_check.py
        language: python
        types: [python]
```

### 5.2 보안 검증 스크립트

```python
#!/usr/bin/env python3
"""
Pre-commit 보안 검증 스크립트
"""
import re
import sys
from pathlib import Path

# 금지된 패턴
FORBIDDEN_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key detected"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token detected"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth Token detected"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID detected"),
    (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
    (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
]

def check_file(file_path: Path) -> list[str]:
    """파일에서 보안 문제 검사"""
    issues = []
    try:
        content = file_path.read_text(encoding="utf-8")
        for pattern, message in FORBIDDEN_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"{file_path}: {message}")
    except Exception as e:
        issues.append(f"{file_path}: Error reading file - {e}")
    return issues

def main() -> int:
    """메인 함수"""
    files_to_check = [Path(f) for f in sys.argv[1:]]
    all_issues = []

    for file_path in files_to_check:
        if file_path.suffix in [".py", ".js", ".ts", ".yaml", ".yml", ".json", ".env"]:
            issues = check_file(file_path)
            all_issues.extend(issues)

    if all_issues:
        print("🚨 Security issues detected:")
        for issue in all_issues:
            print(f"  - {issue}")
        return 1

    print("✅ No security issues found")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 5.3 GitHub Actions 보안 워크플로우

```yaml
{% raw %}
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # Gitleaks - 시크릿 탐지
      - name: Gitleaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # Semgrep - SAST
      - name: Semgrep Scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten

      # npm audit
      - name: npm Security Audit
        run: npm audit --audit-level=high
        continue-on-error: true

      # Python 의존성 검사
      - name: pip-audit
        run: |
          pip install pip-audit
          pip-audit || true

      # 결과 요약
      - name: Security Summary
        if: always()
        run: |
          echo "## Security Scan Summary" >> $GITHUB_STEP_SUMMARY
          echo "- Gitleaks: ${{ steps.gitleaks.outcome }}" >> $GITHUB_STEP_SUMMARY
          echo "- Semgrep: ${{ steps.semgrep.outcome }}" >> $GITHUB_STEP_SUMMARY
{% endraw %}
```

---

## 6. AI 협업 시 보안 모범 사례

### 6.1 프롬프트 보안 지침

AI에게 요청할 때 보안을 명시적으로 지시합니다.

```markdown
## 보안 요청 프롬프트 예시

### API 엔드포인트 생성 요청
"Create a REST API endpoint for user authentication.
Requirements:
- Use environment variables for secrets (os.getenv)
- Implement rate limiting (10 req/min)
- Validate all inputs (XSS, SQL injection check)
- Return user-friendly error messages (no stack traces)
- Log errors with masking (mask_sensitive_info)"

### 설정 파일 생성 요청
"Generate a configuration file for the database connection.
Requirements:
- Use placeholder values: YOUR_DB_HOST, YOUR_DB_PASSWORD
- Add comments explaining each environment variable
- Never include actual credentials"
```

### 6.2 코드 리뷰 체크리스트

AI가 생성한 코드를 리뷰할 때 확인할 사항:

| 카테고리 | 확인 사항 | 우선순위 |
|----------|-----------|----------|
| **시크릿** | 하드코딩된 API 키, 비밀번호 없음 | **P0** |
| **입력 검증** | 사용자 입력 sanitization 적용 | **P0** |
| **에러 처리** | 스택 트레이스 노출 없음 | **P1** |
| **로깅** | 민감 정보 마스킹 적용 | **P1** |
| **의존성** | 알려진 취약점 없는 버전 사용 | **P1** |
| **권한** | 최소 권한 원칙 적용 | **P2** |

### 6.3 AI 생성 코드 검증 플로우

![AI-Generated Code Validation Flow - From generation through automated scans and human review to merge](/assets/images/diagrams/2026-01-28-ai-code-validation-flow.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```
AI-Generated Code Validation Flow:
1. AI Generates Code
2. Automated Scans (Gitleaks, Semgrep, npm audit, Bandit)
3. Human Review (Security checklist, OWASP Top 10, Business logic)
4. Merge to Main
```

</details>

---

## 7. 비용 최적화와 보안의 균형

### 7.1 Free Tier 우선 원칙

보안을 유지하면서도 비용을 최적화하는 전략:

```markdown
## Cost Optimization (Security Maintained)

Priority order for AI operations:
1. **Gemini CLI** (OAuth 2.0) - Free ⭐
   - 보안: OAuth 토큰 자동 갱신
   - 비용: 완전 무료

2. **Local templates** - No cost
   - 보안: 네트워크 요청 없음
   - 비용: 제로

3. **Cached responses** - 7-day TTL
   - 보안: 로컬 캐시, 민감 정보 제외
   - 비용: API 호출 최소화

4. **API calls** - Last resort
   - 보안: 환경 변수로 키 관리
   - 비용: 필요시에만 사용
```

### 7.2 API 키 안전 관리

```python
# config/settings.py
import os
from typing import Optional
from functools import lru_cache

class APISettings:
    """API 설정 관리 (싱글톤)"""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_openai_key() -> Optional[str]:
        """OpenAI API 키 (캐시됨)"""
        return os.getenv("OPENAI_API_KEY")

    @staticmethod
    @lru_cache(maxsize=1)
    def get_gemini_key() -> Optional[str]:
        """Gemini API 키 (캐시됨)"""
        return os.getenv("GEMINI_API_KEY")

    @classmethod
    def validate_keys(cls) -> dict[str, bool]:
        """모든 API 키 유효성 검사"""
        return {
            "openai": bool(cls.get_openai_key()),
            "gemini": bool(cls.get_gemini_key()),
        }

# 사용 예시
settings = APISettings()
if not settings.get_openai_key():
    print("Warning: OPENAI_API_KEY not set, using Gemini as fallback")
```

---

## 8. 실무 체크리스트

### P0 - 필수 (프로젝트 시작 전)

- [ ] CLAUDE.md 파일 생성 및 보안 원칙 명시
- [ ] AGENTS.md 파일 생성 (범용 AI 가이드)
- [ ] .gitignore에 민감 파일 추가 (.env, secrets.*)
- [ ] Pre-commit hook 설정 (gitleaks, bandit)
- [ ] 환경 변수 템플릿 생성 (.env.example)

### P1 - 권장 (개발 중)

- [ ] 보안 유틸리티 함수 구현 (mask_sensitive_info, validate_input)
- [ ] GitHub Actions 보안 스캔 워크플로우 설정
- [ ] 의존성 보안 감사 자동화 (Dependabot)
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