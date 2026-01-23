# PDCA: 보안 기능

> 코드 보안, 의존성 관리, 시크릿 관리

## 현황

| 항목 | 값 |
|------|-----|
| **워크플로우** | `ci-optimization.yml`, 각 워크플로우 내 보안 설정 |
| **보안 도구** | GitHub Dependabot, AGENTS.md 가이드라인 |
| **시크릿 관리** | GitHub Secrets |
| **상태** | Active |

---

## Plan (계획)

### 목표
- 코드 및 의존성 보안 유지
- 시크릿 안전 관리
- 보안 모범 사례 준수

### KPI
| 지표 | 목표 | 현재 |
|------|------|------|
| 취약점 해결 시간 | < 7일 | - |
| 시크릿 노출 | 0건 | - |
| 보안 감사 통과 | 100% | - |

### 보안 계층
```
┌─────────────────────────────────────────────────────────┐
│                    보안 계층 구조                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Layer 1: 코드 보안                                     │
│   ├── AI 에이전트 가이드라인 (AGENTS.md)                  │
│   ├── 입력 검증                                          │
│   └── 민감 정보 마스킹                                    │
│                                                         │
│   Layer 2: 의존성 보안                                    │
│   ├── Dependabot 자동 업데이트                           │
│   ├── npm audit / bundle audit                          │
│   └── 정기적 의존성 검토                                  │
│                                                         │
│   Layer 3: 인프라 보안                                    │
│   ├── GitHub Secrets                                    │
│   ├── 최소 권한 원칙 (GITHUB_TOKEN)                      │
│   └── CSP, HSTS 헤더                                    │
│                                                         │
│   Layer 4: 모니터링                                       │
│   ├── Sentry 에러 추적                                   │
│   └── 접근 로그 분석                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Do (실행)

### 1. 코드 보안

**AI 에이전트 가이드라인 (AGENTS.md):**
```markdown
# 보안 패턴
- 환경 변수 사용: os.getenv("API_KEY", "")
- 민감 정보 마스킹: safe_log()
- 입력 검증: XSS, Injection 패턴 확인
```

**민감 정보 마스킹:**
```python
# scripts/utils.py
def safe_log(message: str, level: str = "INFO") -> None:
    safe_message = mask_sensitive_info(message)
    if _validate_masked_text(safe_message):
        print(f"[{level}] {safe_message}")
```

### 2. 의존성 보안

**Dependabot 설정:**
```yaml
# .github/dependabot.yml (권장)
version: 2
updates:
  - package-ecosystem: "bundler"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pip"
    directory: "/scripts"
    schedule:
      interval: "weekly"
```

**수동 감사:**
```bash
# Ruby 의존성
bundle audit --update

# Node.js 의존성
npm audit --audit-level=moderate

# Python 의존성
pip-audit
```

### 3. 시크릿 관리

**GitHub Secrets 목록:**
| Secret | 용도 | 갱신 주기 |
|--------|------|----------|
| GEMINI_API_KEY | AI 이미지 생성 | 필요시 |
| SENTRY_AUTH_TOKEN | 에러 추적 | 1년 |
| BUTTONDOWN_API_KEY | 이메일 발송 | 필요시 |
| TWITTER_* | SNS 공유 | 필요시 |
| FACEBOOK_* | SNS 공유 | 필요시 |
| LINKEDIN_* | SNS 공유 | 필요시 |

**시크릿 설정 방법:**
```bash
# GitHub CLI로 시크릿 설정
gh secret set GEMINI_API_KEY --body 'your-api-key'
```

### 4. 워크플로우 보안

**최소 권한 원칙:**
```yaml
permissions:
  contents: read    # 읽기만 필요한 경우
  actions: read
  
# 쓰기 필요한 경우만 명시
permissions:
  contents: write
  pull-requests: write
```

**타임아웃 설정:**
```yaml
jobs:
  build:
    timeout-minutes: 10  # 무한 실행 방지
```

### 5. HTTP 보안 헤더

**Vercel 설정 (vercel.json):**
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000" }
      ]
    }
  ]
}
```

---

## Check (점검)

### 모니터링 항목

#### 의존성 취약점
```bash
# 정기 감사
npm audit
bundle audit
pip-audit
```

#### 시크릿 노출 확인
- [ ] 코드 리뷰 시 시크릿 확인
- [ ] git history에 시크릿 없음 확인

#### 보안 헤더 검증
```bash
# 보안 헤더 확인
curl -I https://tech.2twodragon.com
```

### 점검 체크리스트
- [ ] 고위험 취약점 0건
- [ ] 시크릿 노출 0건
- [ ] 보안 헤더 적용 확인
- [ ] 워크플로우 권한 최소화 확인

### 장애 대응
| 상황 | 대응 |
|------|------|
| 취약점 발견 | 즉시 패치/업데이트 |
| 시크릿 노출 | 즉시 갱신, git history 정리 |
| 보안 사고 | 인시던트 대응 절차 실행 |

---

## Act (개선)

### 식별된 개선점
1. **SAST 도구 추가**: CodeQL, Semgrep
2. **의존성 자동 업데이트**: Dependabot PR 자동 머지
3. **보안 테스트 자동화**: 보안 스캔 CI 통합

### 개선 이력
| 날짜 | 개선 내용 | 결과 |
|------|----------|------|
| - | - | - |

### 다음 사이클 계획
- [ ] SAST 도구 도입 검토
- [ ] 보안 감사 자동화
- [ ] 시크릿 로테이션 정책

---

## 보안 참고 자료

### 내부 문서
- [SECURITY.md](../../SECURITY.md)
- [AGENTS.md](../../AGENTS.md)

### 외부 자료
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/actions/security-guides)
- [Dependabot 문서](https://docs.github.com/en/code-security/dependabot)

---

## 관련 문서

- [Pipeline 전체 흐름](../pipeline/README.md)
- [모니터링 PDCA](monitoring.md)
