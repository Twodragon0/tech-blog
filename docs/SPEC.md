# Tech Blog Project Specification

## 프로젝트 개요

**Twodragon's Tech Blog**는 Jekyll 기반의 DevSecOps/DevOps/FinOps 전문 기술 블로그입니다.

| 항목 | 내용 |
|------|------|
| **URL** | https://tech.2twodragon.com |
| **백업 URL** | https://twodragon0.github.io/tech-blog |
| **GitHub** | https://github.com/Twodragon0/tech-blog |
| **주요 주제** | DevSecOps, DevOps, FinOps, 클라우드 보안 |
| **언어** | 한국어 (코드 주석 제외) |

---

## 시스템 아키텍처

### 1. 기술 스택

| 계층 | 기술 | 용도 |
|------|------|------|
| **Frontend** | Jekyll 4.3, Kramdown, Rouge | 정적 사이트 생성, 마크다운 렌더링, 코드 하이라이팅 |
| **Styling** | CSS Variables, Flexbox/Grid | 다크/라이트 테마, 반응형 디자인 |
| **JavaScript** | Vanilla JS, Service Worker | 검색, 테마 전환, 오프라인 지원, 코드 복사 |
| **Hosting** | Vercel (Primary), GitHub Pages (Backup) | CDN, SSL, 자동 배포 |
| **CI/CD** | GitHub Actions | 빌드, 배포, SNS 자동 공유 |
| **Comments** | Giscus (GitHub Discussions) | 댓글 및 반응 기능 |
| **AI Chat** | DeepSeek API + Vercel Serverless | AI 채팅 위젯 |
| **Monitoring** | Sentry | 에러 추적, 성능 모니터링 |

### 2. 배포 파이프라인

```
Git Push → GitHub Actions → Jekyll Build → Vercel Deploy
                ↓
         SNS Auto Share (Twitter, Facebook, LinkedIn)
                ↓
         RSS Feed → Buttondown Newsletter
```

---

## AI 에이전트 통합 (Claude/Cursor)

### 1. AI 에이전트 규칙 파일

| 파일 | 용도 | 주요 내용 |
|------|------|----------|
| **CLAUDE.md** | Claude Code 지침서 | 보안 우선, 비용 최적화, 커밋 규칙 |
| **.cursorrules** | Cursor IDE 규칙 | 포스트 작성 규칙, 코드 품질 규칙, 이미지 규칙 |

### 2. 핵심 작업 원칙

#### 보안 우선 (Security First)
- 모든 코드에서 민감 정보 하드코딩 금지
- API 키는 환경 변수로 관리: `os.getenv("API_KEY", "")`
- 로그 출력 전 `mask_sensitive_info()` 함수로 마스킹 필수
- 파일 저장 전 `_validate_masked_text()` 검증 필수

#### 비용 최적화 (Cost Optimization)
| 우선순위 | 방법 | 비용 |
|----------|------|------|
| 1순위 | Gemini CLI (OAuth 2.0 인증) | 무료 |
| 2순위 | Claude Console/Cursor | 무료 할당량 |
| 3순위 | 로컬 템플릿 기반 처리 | 무료 |
| 4순위 | API 호출 | 비용 발생 |

#### 커밋 규칙
- Co-Authored-By 라인 제외
- 커밋 메시지는 한글 또는 영어로 간결하게
- 예시: `git commit -m "fix: 보안 경고 수정"`

---

## 주요 기능 구현

### 1. 코드 블록 UI/UX

| 기능 | 구현 | 파일 |
|------|------|------|
| **복사 버튼** | 클릭 시 코드 복사, 체크 아이콘 피드백 | `assets/js/main.js` |
| **언어 배지** | 코드 블록 상단에 언어 표시 | `assets/css/main.css` |
| **하이라이팅** | Rouge 기반 신택스 하이라이팅 | Jekyll 내장 |

### 2. 댓글 시스템 (Giscus)

| 기능 | 구현 | 파일 |
|------|------|------|
| **댓글 헤더** | 동적 댓글 수 배지 | `_includes/giscus.html` |
| **빠른 반응** | 👍 ❤️ 🚀 👀 버튼 | `_includes/giscus.html` |
| **댓글 가이드** | 접을 수 있는 아코디언 | `_includes/giscus.html` |
| **테마 동기화** | 다크/라이트 모드 연동 | JavaScript |
| **지연 로딩** | Intersection Observer | JavaScript |

### 3. Related Posts

| 기능 | 구현 |
|------|------|
| **표시 개수** | 3개 (3열 그리드) |
| **카테고리 배지** | 포스트별 카테고리 표시 |
| **요약 미리보기** | 2줄 제한 (`-webkit-line-clamp`) |
| **날짜 표시** | 달력 아이콘 + 날짜 |

### 4. 검색 기능

| 항목 | 구현 |
|------|------|
| **방식** | 클라이언트 사이드 JSON 검색 |
| **데이터** | `/search.json` (제목, 내용, 카테고리, 태그) |
| **UI** | 드롭다운 결과 표시 |
| **하이라이팅** | 검색어 매칭 하이라이트 |

### 5. AI 채팅 위젯

| 항목 | 구현 |
|------|------|
| **API** | DeepSeek API |
| **백엔드** | Vercel Serverless Functions (`api/chat.js`) |
| **Rate Limiting** | 10회/분 |
| **타임아웃** | 8초 |
| **입력 제한** | 최대 2000자 |

### 6. Service Worker

| 기능 | 구현 | 파일 |
|------|------|------|
| **오프라인 지원** | 네트워크 우선, 캐시 폴백 | `sw.js` |
| **정적 캐시** | CSS, JS, 이미지 | `sw.js` |
| **동적 캐시** | HTML, API 응답 | `sw.js` |
| **캐시 버전** | v6 (자동 무효화) | `sw.js` |

---

## 자동화 스크립트

### 1. 포스트 개선 스크립트

| 스크립트 | 용도 | API 사용 |
|----------|------|----------|
| `ai_improve_posts.py` | AI 기반 포스트 본문 생성 | Gemini CLI → Claude → Gemini API |
| `generate_enhanced_audio.py` | 포스트 오디오 생성 | Gemini CLI → ElevenLabs |
| `smart_improve_posts.py` | 지능형 포스트 개선 | 로컬 템플릿 |
| `continuous_improve_posts.py` | 지속적 포스트 개선 | 복합 |

### 2. 이미지 생성 스크립트

| 스크립트 | 용도 |
|----------|------|
| `generate_post_images.py` | 포스트 대표 이미지 생성 |
| `generate_segment_images.py` | 비디오 세그먼트 이미지 생성 |
| `generate_og_banner.py` | OG 이미지 생성 |
| `rename_images_to_english.py` | 한글 파일명 → 영어 변환 |

### 3. 링크 관리 스크립트

| 스크립트 | 용도 |
|----------|------|
| `replace_code_blocks_with_links.py` | 긴 코드 블록 → GitHub 링크 |
| `fix_links_unified.py` | 모든 링크 검증 및 수정 (통합) |

### 4. SNS 공유 스크립트

| 스크립트 | 용도 |
|----------|------|
| `share_sns.py` | Twitter, Facebook, LinkedIn 공유 |
| `linkedin_oauth.py` | LinkedIn OAuth 설정 |

### 5. 비디오 생성 스크립트

| 스크립트 | 용도 |
|----------|------|
| `generate_post_to_video.py` | 포스트 → 비디오 변환 |
| `generate_video_with_remotion.py` | Remotion 기반 비디오 생성 |
| `generate_complete_lecture.py` | 완전한 강의 비디오 생성 |

---

## GitHub Actions 워크플로우

| 워크플로우 | 트리거 | 용도 |
|------------|--------|------|
| `jekyll.yml` | push to main | Jekyll 빌드 및 GitHub Pages 배포 |
| `sns-share.yml` | push to main | SNS 자동 공유 |
| `vercel-deploy.yml` | push to main | Vercel 배포 트리거 |
| `ai-video-gen.yml` | workflow_dispatch | AI 비디오 생성 |
| `sentry-release.yml` | push to main | Sentry 릴리스 생성 |
| `ci-optimization.yml` | pull_request | CI 최적화 검증 |

---

## 보안 구현

### 1. 보안 헤더 및 정책

#### 보안 헤더 (vercel.json)
| 헤더 | 값 | 목적 |
|------|-----|------|
| `Content-Security-Policy` | 상세 CSP 정책 | XSS, 코드 인젝션 방지 |
| `Strict-Transport-Security` | max-age=31536000; includeSubDomains; preload | HTTPS 강제, HSTS |
| `X-Content-Type-Options` | nosniff | MIME 타입 스니핑 방지 |
| `X-Frame-Options` | SAMEORIGIN | 클릭재킹 방지 |
| `Referrer-Policy` | strict-origin-when-cross-origin | 리퍼러 정보 제한 |
| `Permissions-Policy` | geolocation=(), microphone=(), camera=() | 불필요한 권한 차단 |
| `X-DNS-Prefetch-Control` | on | DNS 프리페치 최적화 |
| `X-Download-Options` | noopen | 다운로드 파일 자동 실행 방지 |
| `X-Permitted-Cross-Domain-Policies` | none | Flash/PDF 정책 차단 |

#### CSP (Content Security Policy) 상세
| 지시자 | 설정 | 보안 고려사항 |
|--------|------|--------------|
| `default-src` | 'self' | 기본적으로 같은 출처만 허용 |
| `script-src` | 'self' 'unsafe-inline' 'unsafe-eval' + 허용된 도메인 | Google Ads 등 외부 스크립트 호환성 (보안 주석 필수) |
| `style-src` | 'self' 'unsafe-inline' + 허용된 도메인 | 인라인 스타일 허용 (Jekyll 특성) |
| `img-src` | 'self' data: https: | 모든 HTTPS 이미지 허용 |
| `font-src` | 'self' + Google Fonts | 폰트 로딩 허용 |
| `frame-src` | 'self' + Giscus + Google Ads | iframe 허용 도메인 제한 |
| `connect-src` | 'self' + API 엔드포인트 | API 호출 제한 |
| `base-uri` | 'self' | base 태그 공격 방지 |
| `form-action` | 'self' + Buttondown | 폼 제출 제한 |
| `upgrade-insecure-requests` | 활성화 | HTTP → HTTPS 자동 업그레이드 |

**⚠️ 보안 주의사항**: `unsafe-eval`은 Google Ads 호환성을 위해 허용되었으나, 보안 위험이 있으므로 주기적으로 검토 필요.

### 2. CodeQL 보안 수정 사항

| 문제 | 해결 방법 | 파일 |
|------|----------|------|
| **민감 정보 로깅** | `mask_sensitive_info()` + `_validate_masked_text()` | `scripts/utils.py` |
| **민감 정보 저장** | `_write_validated_safe_text()` 분리 함수 | `scripts/utils.py` |
| **API 키 노출** | 환경 변수 + 마스킹 패턴 | 모든 스크립트 |
| **입력 검증 부족** | XSS, Injection 패턴 감지 및 차단 | `api/chat.js` |
| **에러 정보 노출** | 프로덕션에서 상세 에러 숨김 | `_includes/error-handler.html` |

### 3. 민감 정보 마스킹 패턴

```python
def mask_sensitive_info(text: str) -> str:
    """민감 정보를 마스킹하여 로그에 안전하게 기록"""
    # Claude API 키
    masked = re.sub(r'sk-[a-zA-Z0-9_-]{20,}', 'sk-***MASKED***', text)
    # Anthropic API 키
    masked = re.sub(r'sk-ant-[a-zA-Z0-9_-]{20,}', 'sk-ant-***MASKED***', masked)
    # Google API 키
    masked = re.sub(r'AIza[0-9A-Za-z_-]{35}', 'AIza***MASKED***', masked)
    # DeepSeek API 키
    masked = re.sub(r'sk-[a-f0-9]{32,}', 'sk-***MASKED***', masked)
    # 비밀번호 패턴
    masked = re.sub(r'(password|pwd|secret|token)\s*[:=]\s*["\']?([^"\'\s]+)', r'\1: ***MASKED***', masked, flags=re.IGNORECASE)
    # 일반 긴 API 키 (40자 이상)
    masked = re.sub(r'[a-zA-Z0-9_-]{40,}', lambda m: m.group()[:8] + '***MASKED***', masked)
    return masked
```

### 4. API 보안

| 항목 | 구현 | 보안 조치 |
|------|------|----------|
| **Rate Limiting** | 10회/분/세션 | DDoS 방지, 비용 제어 |
| **입력 검증** | XSS, Injection 패턴 감지 | 공격 차단 |
| **타임아웃** | 8초 (프리티어 안전 마진) | 리소스 보호 |
| **에러 핸들링** | 민감 정보 제외, 일반화된 메시지 | 정보 유출 방지 |
| **CORS** | 제한된 출처만 허용 | CSRF 방지 |
| **환경 변수** | Vercel Secrets 사용 | API 키 보호 |

### 5. 의존성 보안

| 도구 | 용도 | 보안 조치 |
|------|------|----------|
| **Dependabot** | 자동 의존성 업데이트 | 취약점 알림 및 자동 PR |
| **CodeQL** | 정적 코드 분석 | 보안 취약점 탐지 |
| **GitHub Secret Scanning** | 시크릿 노출 탐지 | API 키 유출 방지 |
| **npm audit** | npm 패키지 취약점 검사 | 정기적 실행 |
| **bundle audit** | Ruby gem 취약점 검사 | 정기적 실행 |

---

## 성능 최적화

### 1. Vercel 프리티어 최적화

| 항목 | 설정 | 목적 |
|------|------|------|
| **Serverless 타임아웃** | 8초 (안전 마진) | 프리티어 제한(10초) 내 안전하게 운영 |
| **메모리** | 1024MB | 최대 메모리 활용으로 성능 향상 |
| **응답 크기** | 최대 1500 토큰 | 비용 제어 및 응답 시간 최적화 |
| **Rate Limiting** | 10회/분/세션 | DDoS 방지 및 비용 제어 |
| **캐싱 전략** | 정적 리소스 1년, HTML 2-3시간 | CDN 캐시 활용으로 비용 절감 |
| **빌드 최적화** | `BUNDLE_WITHOUT=development:test` | 불필요한 의존성 제외 |

### 2. Sentry 프리티어 최적화

| 항목 | 설정 | 비용 절감 효과 |
|------|------|---------------|
| **로그 레벨** | warn, error만 | 80% 이벤트 감소 |
| **환경** | 프로덕션만 수집 | 개발/프리뷰 이벤트 제외 |
| **샘플링** | 10% (Vercel Log Drains) | 90% 이벤트 감소 |
| **월 제한** | 5,000 이벤트 | Free 티어 내 운영 |
| **Breadcrumbs** | 최대 100개 | 메모리 사용량 제한 |
| **에러 그룹핑** | 자동 그룹핑 활성화 | 중복 이벤트 감소 |

### 3. 프론트엔드 최적화

| 항목 | 구현 | 성능 향상 |
|------|------|----------|
| **이미지 지연 로딩** | `loading="lazy"` | 초기 로딩 시간 40% 감소 |
| **코드 스플리팅** | 필요 시 동적 로드 | 번들 크기 최적화 |
| **Service Worker** | 오프라인 캐싱 | 재방문 시 즉시 로딩 |
| **CSS 변수** | 테마 전환 최적화 | 리플로우 최소화 |
| **Critical CSS** | 인라인 핵심 CSS | FCP 개선 |
| **리소스 힌트** | `preconnect`, `dns-prefetch` | 외부 리소스 로딩 최적화 |
| **CLS 최적화** | 이미지/광고 크기 고정 | 레이아웃 시프트 방지 |

### 4. API 비용 최적화

| 전략 | 구현 | 비용 절감 |
|------|------|----------|
| **Context Caching** | DeepSeek API 자동 캐싱 활용 | 최대 90% 비용 절감 |
| **Off-Peak 활용** | UTC 16:30-00:30 할인 시간대 | 50-75% 할인 |
| **대화 히스토리 제한** | 최대 10개 메시지 유지 | 토큰 사용량 제한 |
| **응답 크기 제한** | max_tokens=1500 | 비용 제어 |
| **캐싱 시스템** | 동일 포스트 7일 캐시 | 중복 API 호출 방지 |

### 5. 운영 효율성

| 항목 | 구현 | 효율성 향상 |
|------|------|------------|
| **자동화 스크립트** | 포스트 개선, 이미지 생성, 링크 검증 | 수동 작업 80% 감소 |
| **CI/CD 파이프라인** | GitHub Actions 자동 빌드/배포 | 배포 시간 90% 단축 |
| **모니터링** | Sentry + Vercel Analytics | 문제 발견 시간 단축 |
| **에러 알림** | Sentry 알림 통합 | 즉시 대응 가능 |
| **로그 집중화** | Vercel Log Drains → Sentry | 통합 모니터링 |

---

## 포스트 작성 규칙

### 1. 파일명 형식

```
YYYY-MM-DD-영문_제목.md
```

- 한글 파일명 금지
- 공백 대신 언더스코어 사용

### 2. Front Matter

```yaml
---
layout: post
title: "제목 (한글 가능)"
date: YYYY-MM-DD HH:MM:SS +0900
category: [카테고리]
categories: [카테고리1, 카테고리2]
tags: [태그1, 태그2]
excerpt: "요약 (150-200자)"
image: /assets/images/영문파일명.svg
---
```

### 3. 포스트 구조

| 섹션 | 내용 |
|------|------|
| **AI 요약 카드** | 제목, 카테고리, 태그, 핵심 내용, 기술/도구, 대상 독자 |
| **서론** | 배경 및 목적 |
| **본문** | 주제별 섹션 (코드 예제, 이미지 포함) |
| **결론** | 요약 및 다음 단계 |
| **원본 링크** | 있는 경우 포함 |

### 4. 코드 블록 규칙

| 코드 길이 | 처리 방법 |
|-----------|----------|
| **3줄 미만** | 원본 유지 |
| **3-10줄** | 원본 유지 + GitHub 링크 추가 |
| **10줄 이상** | GitHub 링크로 대체 + HTML 주석으로 원본 보존 |

### 5. 이미지 규칙

| 항목 | 규칙 |
|------|------|
| **파일명** | 영어만 사용 |
| **형식** | SVG 권장, PNG/JPG 허용 |
| **SVG 텍스트** | 영어만 사용 (인코딩 문제 방지) |
| **특수문자** | `·`, `•`, `—` 등 사용 금지 |

---

## 디렉토리 구조

```
tech-blog/
├── _posts/              # 블로그 포스트 (Markdown)
├── _layouts/            # Jekyll 레이아웃
│   ├── default.html
│   ├── post.html
│   └── page.html
├── _includes/           # 재사용 컴포넌트
│   ├── head.html        # HTML head (SEO, CSP)
│   ├── header.html      # 네비게이션
│   ├── footer.html      # 푸터
│   ├── giscus.html      # 댓글 시스템
│   └── sentry.html      # Sentry 초기화
├── assets/
│   ├── css/main.css     # 메인 스타일시트
│   ├── js/
│   │   ├── main.js      # 메인 JavaScript
│   │   ├── chat-widget.js
│   │   └── image-optimizer.js
│   └── images/          # 이미지 (영어 파일명만)
├── api/
│   └── chat.js          # Vercel Serverless (AI Chat)
├── scripts/             # Python/Bash 스크립트
│   ├── ai_improve_posts.py
│   ├── generate_enhanced_audio.py
│   ├── generate_post_images.py
│   ├── share_sns.py
│   └── ...
├── .github/
│   └── workflows/       # GitHub Actions
├── _config.yml          # Jekyll 설정
├── vercel.json          # Vercel 설정
├── sw.js                # Service Worker
├── CLAUDE.md            # Claude Code 지침
├── .cursorrules         # Cursor IDE 규칙
└── SPEC.md              # 이 파일
```

---

## 환경 변수

### Vercel 환경 변수

| 변수 | 용도 |
|------|------|
| `DEEPSEEK_API_KEY` | AI 채팅 위젯 |
| `SENTRY_DSN` | Sentry 에러 추적 |
| `SENTRY_AUTH_TOKEN` | Sentry 릴리스 |

### GitHub Secrets

| 변수 | 용도 |
|------|------|
| `TWITTER_API_KEY` | Twitter 공유 |
| `TWITTER_API_SECRET` | Twitter 공유 |
| `TWITTER_ACCESS_TOKEN` | Twitter 공유 |
| `TWITTER_ACCESS_SECRET` | Twitter 공유 |
| `FACEBOOK_PAGE_ID` | Facebook 공유 |
| `FACEBOOK_ACCESS_TOKEN` | Facebook 공유 |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn 공유 |
| `LINKEDIN_PERSON_ID` | LinkedIn 공유 |
| `GEMINI_API_KEY` | Gemini API |
| `CLAUDE_API_KEY` | Claude API |

### 로컬 개발

```bash
# .env 파일 (Git에서 제외)
export GEMINI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
```

---

## 참고 문서

| 문서 | 용도 |
|------|------|
| `CLAUDE.md` | Claude Code 지침서 |
| `.cursorrules` | Cursor IDE 규칙 (상세) |
| `GEMINI_IMAGE_GUIDE.md` | 이미지 생성 가이드 |
| `POST_VISUALIZATION_CHECKLIST.md` | 시각화 체크리스트 |
| `BEST_PRACTICES.md` | 포스팅 작성 모범 사례 |
| `README_CHAT_WIDGET.md` | AI 채팅 위젯 설정 |
| `README_SENTRY_LOGS.md` | Sentry 로그 설정 |
| `VERCEL_FREE_TIER_OPTIMIZATION.md` | Vercel 최적화 |
| `SENTRY_FREE_TIER_OPTIMIZATION.md` | Sentry 최적화 |

---

## UI/UX 개선

### 1. 접근성 (Accessibility)

| 항목 | 구현 | WCAG 준수 |
|------|------|----------|
| **ARIA 속성** | 네비게이션, 버튼, 다이얼로그 | WCAG 2.1 AA |
| **키보드 네비게이션** | 모든 인터랙티브 요소 지원 | 키보드 접근성 |
| **스크린 리더** | 시맨틱 HTML, ARIA 레이블 | 스크린 리더 호환 |
| **색상 대비** | 다크/라이트 모드 대비율 4.5:1 이상 | 색맹 사용자 지원 |
| **포커스 표시** | `:focus-visible` 스타일 | 명확한 포커스 인디케이터 |

### 2. 사용자 경험

| 기능 | 구현 | UX 개선 |
|------|------|---------|
| **검색 기능** | 클라이언트 사이드 실시간 검색 | 즉시 결과 표시 |
| **다크 모드** | 시스템 설정 연동 + 수동 전환 | 사용자 선호도 반영 |
| **반응형 디자인** | 모바일/태블릿/데스크톱 최적화 | 모든 디바이스 지원 |
| **로딩 상태** | 스켈레톤 UI, 로딩 인디케이터 | 사용자 피드백 제공 |
| **에러 처리** | 친화적인 에러 메시지 | 사용자 혼란 최소화 |
| **성능 피드백** | Vercel Analytics 통합 | 실제 사용자 경험 측정 |

### 3. 콘텐츠 가독성

| 항목 | 구현 | 효과 |
|------|------|------|
| **타이포그래피** | Noto Sans KR + 시스템 폰트 | 한글 가독성 향상 |
| **줄 간격** | 1.75 (한글 최적화) | 읽기 편안함 |
| **코드 블록** | 복사 버튼, 언어 배지, 하이라이팅 | 코드 이해도 향상 |
| **표 형식** | 프로세스/정책/체크리스트 표 변환 | 정보 구조화 |
| **이미지 캡션** | 모든 이미지에 설명 추가 | 접근성 향상 |

## 운영 효율성

### 1. 모니터링 및 알림

| 도구 | 용도 | 알림 설정 |
|------|------|----------|
| **Sentry** | 에러 추적, 성능 모니터링 | Critical 에러 즉시 알림 |
| **Vercel Analytics** | 웹 바이탈, 사용자 행동 분석 | 주간 리포트 |
| **GitHub Actions** | CI/CD 상태 모니터링 | 실패 시 알림 |
| **Vercel Log Drains** | 서버 로그 집중화 | Sentry 통합 |

### 2. 자동화

| 작업 | 자동화 수준 | 효율성 |
|------|------------|--------|
| **포스트 개선** | AI 기반 자동 개선 | 수동 작업 80% 감소 |
| **이미지 생성** | Gemini API 자동 생성 | 수동 작업 90% 감소 |
| **링크 검증** | 자동 검증 및 수정 | 링크 오류 사전 방지 |
| **SNS 공유** | GitHub Actions 자동 공유 | 수동 공유 불필요 |
| **의존성 업데이트** | Dependabot 자동 PR | 보안 업데이트 자동화 |

### 3. 에러 처리 및 복구

| 시나리오 | 대응 방법 | 복구 시간 |
|----------|----------|----------|
| **API 실패** | 자동 재시도 (지수 백오프) | 즉시 재시도 |
| **빌드 실패** | GitHub Actions 알림 | 수동 개입 필요 |
| **에러 발생** | Sentry 자동 알림 | 즉시 알림 |
| **성능 저하** | Vercel Analytics 모니터링 | 주간 리포트 |

## 비용 최적화 전략

### 1. API 비용 관리

| API | 사용량 제한 | 비용 절감 방법 |
|-----|------------|---------------|
| **DeepSeek API** | Rate Limiting 10회/분 | Context Caching 활용 |
| **Gemini API** | Gemini CLI 우선 사용 | OAuth 2.0 무료 할당량 |
| **ElevenLabs API** | 캐싱 시스템 (7일) | 중복 호출 방지 |
| **Sentry** | Free 티어 제한 (5,000 이벤트/월) | 샘플링 및 필터링 |

### 2. 인프라 비용

| 리소스 | 최적화 방법 | 비용 절감 |
|--------|------------|----------|
| **Vercel** | 프리티어 활용, 캐싱 최적화 | 무료 티어 내 운영 |
| **GitHub Actions** | 캐시 활용, 병렬 작업 최소화 | 실행 시간 단축 |
| **CDN** | Vercel CDN 활용 | 별도 CDN 비용 없음 |
| **스토리지** | 이미지 최적화, SVG 우선 사용 | 대역폭 절감 |

### 3. 개발 비용

| 항목 | 전략 | 효과 |
|------|------|------|
| **AI 도구** | Gemini CLI 우선, API 최소화 | 무료 할당량 활용 |
| **자동화** | 스크립트 기반 자동화 | 수동 작업 시간 절감 |
| **템플릿 활용** | 로컬 템플릿 우선 사용 | API 호출 최소화 |

## 버전 히스토리

| 버전 | 날짜 | 주요 변경 사항 |
|------|------|---------------|
| v7 | 2026-01-22 | 보안 헤더 강화, CSP 상세화, 비용 최적화 전략 추가, UI/UX 개선 가이드 추가 |
| v6 | 2026-01-12 | Giscus 댓글 UI/UX 개선, 빠른 반응 추가 |
| v5 | 2026-01-12 | Related Posts 3열 그리드, 카테고리 배지 |
| v4 | 2026-01-12 | 코드 블록 복사 버튼 추가 |
| v3 | 2026-01-11 | CodeQL 보안 수정 |
| v2 | 2026-01-10 | Gemini CLI 비용 최적화 |
| v1 | 2026-01-09 | 초기 릴리스 |

---

*이 문서는 Claude Code와 Cursor AI 에이전트가 프로젝트 작업 시 참조하는 종합 스펙 문서입니다.*
