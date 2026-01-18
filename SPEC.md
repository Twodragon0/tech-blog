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

### 1. CodeQL 보안 수정 사항

| 문제 | 해결 방법 |
|------|----------|
| **민감 정보 로깅** | `mask_sensitive_info()` + `_validate_masked_text()` |
| **민감 정보 저장** | `_write_validated_safe_text()` 분리 함수 |
| **API 키 노출** | 환경 변수 + 마스킹 패턴 |

### 2. 민감 정보 마스킹 패턴

```python
def mask_sensitive_info(text: str) -> str:
    # Claude API 키
    masked = re.sub(r'sk-[a-zA-Z0-9_-]{20,}', 'sk-***MASKED***', text)
    # Anthropic API 키
    masked = re.sub(r'sk-ant-[a-zA-Z0-9_-]{20,}', 'sk-ant-***MASKED***', masked)
    # Google API 키
    masked = re.sub(r'AIza[0-9A-Za-z_-]{35}', 'AIza***MASKED***', masked)
    # 일반 긴 API 키
    masked = re.sub(r'[a-zA-Z0-9_-]{40,}', lambda m: m.group()[:8] + '***MASKED***', masked)
    return masked
```

### 3. CSP (Content Security Policy)

| 지시자 | 설정 |
|--------|------|
| `default-src` | 'self' |
| `script-src` | 'self' + Giscus + Google Ads |
| `style-src` | 'self' 'unsafe-inline' |
| `img-src` | 'self' data: https: |
| `connect-src` | 'self' + API 엔드포인트 |

---

## 성능 최적화

### 1. Vercel 프리티어 최적화

| 항목 | 설정 |
|------|------|
| **Serverless 타임아웃** | 8초 (안전 마진) |
| **메모리** | 1024MB |
| **응답 크기** | 최대 1500 토큰 |
| **Rate Limiting** | 10회/분/세션 |

### 2. Sentry 프리티어 최적화

| 항목 | 설정 |
|------|------|
| **로그 레벨** | warn, error만 |
| **환경** | 프로덕션만 수집 |
| **샘플링** | 10% (Vercel Log Drains) |
| **월 제한** | 5,000 이벤트 |

### 3. 프론트엔드 최적화

| 항목 | 구현 |
|------|------|
| **이미지 지연 로딩** | `loading="lazy"` |
| **코드 스플리팅** | 필요 시 동적 로드 |
| **Service Worker** | 오프라인 캐싱 |
| **CSS 변수** | 테마 전환 최적화 |

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

## 버전 히스토리

| 버전 | 날짜 | 주요 변경 사항 |
|------|------|---------------|
| v6 | 2026-01-12 | Giscus 댓글 UI/UX 개선, 빠른 반응 추가 |
| v5 | 2026-01-12 | Related Posts 3열 그리드, 카테고리 배지 |
| v4 | 2026-01-12 | 코드 블록 복사 버튼 추가 |
| v3 | 2026-01-11 | CodeQL 보안 수정 |
| v2 | 2026-01-10 | Gemini CLI 비용 최적화 |
| v1 | 2026-01-09 | 초기 릴리스 |

---

*이 문서는 Claude Code와 Cursor AI 에이전트가 프로젝트 작업 시 참조하는 종합 스펙 문서입니다.*
