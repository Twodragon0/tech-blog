# Twodragon's Tech Blog

**DevSecOps, DevOps, FinOps 전문 기술 블로그**

클라우드 보안, 인프라 자동화, 비용 최적화에 대한 실무 경험과 최신 트렌드를 공유합니다.

[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?logo=vercel)](https://tech.2twodragon.com)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Backup-blue?logo=github)](https://twodragon0.github.io/tech-blog)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🏗️ 아키텍처

아래 다이어그램은 콘텐츠 작성부터 배포, 사용자 참여·모니터링까지 전체 시스템 구성을 보여줍니다.

![Tech Blog Architecture](assets/images/readme-architecture.svg)

*그림 1: Tech Blog 아키텍처 (Content Creation → Build & Deploy → User Engagement & Observability)*

**3단계 구성:**
1. **Content Creation** — Markdown, Cursor AI, Gemini(이미지), Claude Code, OpenCode Ralph로 콘텐츠 작성
2. **Build & Deploy** — GitHub Actions(Jekyll, SNS, Buttondown, Sentry), Vercel(프로덕션 + DeepSeek Chat API) 배포
3. **User Engagement & Observability** — Giscus, Buttondown, RSS, DeepSeek 채팅 위젯, Sentry·Vercel Analytics, GitHub Pages 백업

---

## 📈 전체 흐름 (End-to-End)

작성부터 독자 도달까지 한 번에 보는 흐름도입니다.

![End-to-End Flow](assets/images/readme-overall-flow.svg)

*그림 2: 작성 → 버전관리 → 빌드/배포 → 전달 → 독자 (및 푸시 시 병렬 자동화)*

- **상단**: Authoring → Version Control → Build & Deploy → Delivery → Reader
- **중단**: Push 시 GitHub Actions(SNS, 뉴스레터, 백업, Daily News)와 Vercel(프로덕션, DeepSeek API) 병렬 실행
- **하단**: 콘텐츠/데이터, 시크릿·환경변수, 모니터링, 스크립트·자동화 역할 정리

---

## 📊 배포 흐름

Write → Push → Build → Deploy 4단계와 푸시 후 자동 액션을 시각화한 다이어그램입니다.

![Deployment Flow](assets/images/readme-deploy-flow.svg)

*그림 3: 배포 4단계 및 GitHub Actions 연동*

- **Write → Push → Build → Deploy** 4단계 자동 파이프라인
- GitHub Actions: SNS 공유, 뉴스레터 발송, 백업 사이트 배포
- Vercel Edge CDN 글로벌 배포

---

## 🔄 CI/CD 파이프라인

GitHub Actions 워크플로우 트리거와 역할을 정리한 다이어그램입니다.

![CI/CD Pipeline](assets/images/readme-ci-pipeline.svg)

*그림 4: GitHub Actions 트리거(Push / Schedule) 및 워크플로우 요약*

| 트리거 | 워크플로우 | 용도 |
|--------|------------|------|
| **push (main)** | jekyll.yml | Jekyll 빌드, GitHub Pages 백업 |
| **push (_posts/**)** | sns-share.yml | Twitter, Facebook, LinkedIn 자동 공유 |
| **push (_posts/**)** | buttondown-notify.yml | RSS → 이메일(Buttondown) 발송 |
| **push (content paths)** | sentry-release.yml | Sentry 릴리스 생성 |
| **cron (01:00 UTC)** | daily-news.yml | 뉴스 수집·드래프트 생성 |
| **cron (01:00 UTC)** | monitoring.yml | Sentry 할당량·헬스 체크 |
| **workflow_dispatch** | generate-images, ai-video-gen, vercel-deploy | 수동: 이미지/영상 생성, Sentry 알림 |

## 🎯 주요 주제

| 카테고리 | 설명 |
|----------|------|
| **DevSecOps** | CI/CD 보안, SAST/DAST, 컨테이너 보안, 보안 자동화 |
| **DevOps** | 인프라 자동화, Kubernetes, 컨테이너 오케스트레이션, 모니터링 |
| **FinOps** | 클라우드 비용 최적화, 리소스 관리, 비용 거버넌스 |
| **Cloud Security** | AWS/GCP/Azure 보안 아키텍처, 보안 모범 사례 |
| **Incident Response** | 보안 사고 분석, Post-Mortem, 대응 전략 |

## 📁 프로젝트 구조

```
tech-blog/
├── _posts/                 # 블로그 포스트 (~50개, Markdown)
├── _layouts/               # Jekyll 레이아웃 파일
├── _includes/              # 재사용 가능한 컴포넌트
├── _sass/                  # SASS 스타일시트 소스
├── _data/                  # 데이터 파일 (JSON/YAML)
├── assets/
│   ├── css/                # 컴파일된 스타일시트
│   ├── js/                 # JavaScript
│   └── images/             # 이미지 (영어 파일명만!)
├── docs/                   # 프로젝트 문서
│   ├── guides/             # 콘텐츠 작성 가이드
│   ├── optimization/       # 성능 최적화 가이드
│   ├── setup/              # 설정 가이드
│   ├── troubleshooting/    # 문제 해결 가이드
│   ├── pdca/               # 기능별 PDCA 문서
│   ├── pipeline/           # 파이프라인 문서
│   └── scripts/            # 스크립트 문서
├── scripts/                # 유틸리티 스크립트
│   ├── *.py (69개)         # Python 스크립트
│   ├── *.sh (20개)         # Shell 스크립트
│   ├── _archive/           # 보관된 스크립트 (22개)
│   └── README.md           # 스크립트 가이드
├── api/                    # Vercel Serverless Functions
│   ├── chat.js             # DeepSeek 챗봇 API
│   └── lib/                # 공유 라이브러리
├── certifications/         # 자격증 문서 (AWS-SAA, CKA 등)
├── .github/
│   ├── workflows/          # GitHub Actions (CI/CD, SNS 공유)
│   └── ISSUE_TEMPLATE/     # 이슈 템플릿
├── _config.yml             # Jekyll 설정
├── vercel.json             # Vercel 배포 설정 (CSP, 캐싱)
├── package.json            # Node.js 의존성
├── Gemfile                 # Ruby 의존성
├── build.sh                # 빌드 스크립트
├── CLAUDE.md               # Claude Code 지침
├── AGENTS.md               # AI 에이전트 가이드라인
├── SECURITY.md             # 보안 정책
└── README.md               # 이 파일
```

## 🛠️ 기술 스택

### Core
| 기술 | 용도 |
|------|------|
| **Jekyll 4.3** | 정적 사이트 생성기 |
| **Ruby 3.3** | Jekyll 런타임 |
| **Markdown** | 콘텐츠 작성 |

### Hosting & Deploy
| 서비스 | 용도 |
|--------|------|
| **Vercel** | 프로덕션 호스팅 (tech.2twodragon.com) |
| **GitHub Pages** | 백업 호스팅 |
| **GitHub Actions** | CI/CD, SNS 자동 공유 |

### User Engagement
| 서비스 | 용도 |
|--------|------|
| **Giscus** | GitHub Discussions 기반 댓글 |
| **Buttondown** | RSS-to-Email 뉴스레터 |
| **RSS Feed** | 콘텐츠 신디케이션 |

### SNS Auto Share
| 플랫폼 | API |
|--------|-----|
| **Twitter/X** | Tweepy (v2 API) |
| **Facebook** | Graph API |
| **LinkedIn** | UGC Posts API |

## 🚀 로컬 개발

### 요구사항
- Ruby 3.3+
- Bundler
- Git

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/Twodragon0/tech-blog.git
cd tech-blog

# 의존성 설치
bundle install

# 로컬 서버 실행
bundle exec jekyll serve

# 브라우저에서 열기
open http://localhost:4000
```

## 📝 새 글 작성

### 1. 파일 생성
```bash
# 파일명 형식: YYYY-MM-DD-제목.md
touch _posts/2025-01-09-새로운_포스트_제목.md
```

### 2. Front Matter 작성
```yaml
---
layout: post
title: "포스트 제목"
date: 2025-01-09 10:00:00 +0900
categories: devsecops
tags: [AWS, Security, Kubernetes]
excerpt: "포스트 요약 (SEO용)"
image: /assets/images/2025-01-09-포스트_제목.svg
---
```

### 3. 배포
```bash
git add .
git commit -m "Add new post: 포스트 제목"
git push
```

배포 후 자동으로:
- Vercel에 사이트 배포
- SNS에 자동 공유 (설정된 플랫폼)
- RSS 피드 업데이트 → 뉴스레터 발송

## ⚙️ GitHub Secrets 설정

SNS 자동 공유를 위해 다음 시크릿을 설정하세요:

### Twitter/X
| Secret | 설명 |
|--------|------|
| `TWITTER_API_KEY` | API Key |
| `TWITTER_API_SECRET` | API Secret |
| `TWITTER_ACCESS_TOKEN` | Access Token |
| `TWITTER_ACCESS_SECRET` | Access Token Secret |

### Facebook
| Secret | 설명 |
|--------|------|
| `FACEBOOK_PAGE_ID` | Page ID |
| `FACEBOOK_ACCESS_TOKEN` | Page Access Token |

### LinkedIn
| Secret | 설명 |
|--------|------|
| `LINKEDIN_ACCESS_TOKEN` | OAuth Access Token |
| `LINKEDIN_PERSON_ID` | Person URN ID |

## 💬 댓글 시스템

[Giscus](https://giscus.app)를 사용한 GitHub Discussions 기반 댓글:

- **Repository**: [Twodragon0/tech-blog](https://github.com/Twodragon0/tech-blog)
- **Discussions**: [블로그 Discussions](https://github.com/Twodragon0/tech-blog/discussions)
- **Mapping**: pathname (URL 기반 자동 매칭)

## 📧 뉴스레터

[Buttondown](https://buttondown.com/twodragon)을 통한 RSS-to-Email 자동 발송:

- 새 글 작성 시 자동으로 구독자에게 이메일 발송
- 구독 페이지: https://buttondown.com/twodragon
- **개선된 이메일 템플릿**: 시각적으로 매력적인 레이아웃, 카테고리/태그 배지, 요약 섹션 포함

### 이메일 기능

#### 이메일 미리보기
```bash
# 특정 포스트의 이메일 미리보기
python3 scripts/preview_buttondown_email.py _posts/2026-01-15-Example.md

# 미리보기를 파일로 저장
python3 scripts/preview_buttondown_email.py _posts/2026-01-15-Example.md preview.md
```

#### 이메일 발송 테스트
```bash
# Dry run (실제 발송 없이 미리보기)
python3 scripts/test_buttondown_email_send.py _posts/2026-01-15-Example.md --dry-run

# 실제 이메일 발송 (모든 구독자에게 전송)
python3 scripts/test_buttondown_email_send.py _posts/2026-01-15-Example.md
```

#### 이메일 템플릿 특징
- ✨ 시각적으로 매력적인 헤더와 레이아웃
- 📅 발행일 정보 표시
- 🔒 카테고리 배지 (이모지 포함)
- 🏷️ 태그 배지 (최대 6개)
- 📋 요약 섹션 (excerpt 또는 본문에서 자동 추출)
- 🚀 눈에 띄는 CTA 버튼
- 💌 브랜딩된 푸터

#### 자동 발송
GitHub Actions 워크플로우를 통해 새 포스트가 푸시되면 자동으로 이메일이 발송됩니다:
- `.github/workflows/buttondown-notify.yml`에서 처리
- `BUTTONDOWN_API_KEY` GitHub Secret 필요

## 🔗 링크

| 링크 | URL |
|------|-----|
| **프로덕션** | https://tech.2twodragon.com |
| **백업** | https://twodragon0.github.io/tech-blog |
| **RSS** | https://tech.2twodragon.com/feed.xml |
| **뉴스레터** | https://buttondown.com/twodragon |
| **GitHub** | https://github.com/Twodragon0/tech-blog |

## 🤖 AI 어시스턴트 활용

이 프로젝트는 AI 어시스턴트를 활용한 콘텐츠 작성을 지원합니다.

### AI 관련 문서
| 문서 | 용도 |
|------|------|
| `.cursorrules` | Cursor AI 설정 및 프로젝트 규칙 (상세, Opus 4.6 최적화 포함) |
| `CLAUDE.md` | Claude Code 지침 (Opus 4.6 최대한 활용하기 가이드 포함) |
| `AGENTS.md` | AI 에이전트 코딩 가이드라인 (Opus 4.6 활용 전략 포함) |

### Opus 4.6 최적화

이 프로젝트는 Claude Opus 4.6의 향상된 기능을 최대한 활용하기 위한 가이드라인을 포함합니다:

- **정확한 지시 따름**: 반복 지시 불필요, 의도 설명 포함
- **맥락 파악 우선**: 행동하기 전에 전체 그림 파악
- **끈기 있는 작업**: 어려운 작업에 더 오래 매달림
- **적극적 의견 제시**: 대안 탐색, 스트레스 테스트
- **강력한 글쓰기**: 스타일 매칭, 목소리 유지

자세한 내용은 `CLAUDE.md`의 "Opus 4.6 최대한 활용하기" 섹션을 참조하세요.

### 콘텐츠 가이드
| 문서 | 용도 |
|------|------|
| `docs/guides/BEST_PRACTICES.md` | 포스트 작성 모범 사례 |
| `docs/guides/GEMINI_IMAGE_GUIDE.md` | 이미지 생성 가이드 |
| `docs/guides/POST_VISUALIZATION_CHECKLIST.md` | 시각화 체크리스트 |

### 스크립트 사용
| 명령어 | 용도 |
|--------|------|
| `python3 scripts/check_posts.py` | 포스트 검증 |
| `python3 scripts/fix_links_unified.py --fix` | 링크 수정 |
| `python3 scripts/verify_images_unified.py --all` | 이미지 검증 |

## 📊 프로젝트 통계

| 항목 | 수량 |
|------|------|
| 블로그 포스트 | ~50개 |
| Python 스크립트 | 55개 |
| Shell 스크립트 | 20개 |
| 보관된 스크립트 | 36개 |
| 문서 파일 | 50+개 |
| GitHub Actions | 5개 워크플로우 |

### 스크립트 카테고리

| 카테고리 | 스크립트 수 | 용도 |
|----------|------------|------|
| 포스트 검증 | 4개 | Front matter, TOC, 품질 검사 |
| 링크 관리 | 8개 | 링크 수정, Mermaid 호환성 |
| 이미지 관리 | 9개 | 생성, 검증, 변환 |
| 오디오/비디오 | [online-course로 이관](scripts/AUDIO_VIDEO_MOVED.md) | TTS, 비디오 생성 |
| 콘텐츠 개선 | 4개 | AI 기반 개선 |
| 뉴스/뉴스레터 | 10개 | 뉴스 수집, 이메일 발송 |
| Mermaid | 5개 | 다이어그램 관리 |
| SNS 공유 | 3개 | 소셜 미디어 연동 |
| 유틸리티 | 12개 | 정리, 포맷팅, 생성 |
| Shell 스크립트 | 20개 | 설정, 자동화, 모니터링 |

자세한 스크립트 목록은 [scripts/README.md](scripts/README.md)를 참조하세요.

## 📄 라이선스

이 블로그의 모든 콘텐츠는 개인의 학습과 지식 공유를 목적으로 작성되었습니다.

## 🤝 기여

버그 리포트나 개선 제안은 [Issues](https://github.com/Twodragon0/tech-blog/issues)를 통해 제안해주세요.
