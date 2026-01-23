# Pipeline - 프로젝트 단위 전체 흐름

> **Pipeline**: tech-blog 프로젝트의 전체 CI/CD 및 자동화 흐름

## 개요

이 디렉토리는 tech-blog 프로젝트의 **전체 파이프라인 흐름**을 문서화합니다.
개별 기능은 [PDCA 문서](../pdca/README.md)에서 관리됩니다.

## 문서 구조

```
docs/pipeline/
├── README.md                    # 이 파일 (프로젝트 전체 개요)
├── architecture.md              # 전체 아키텍처
├── workflows.md                 # GitHub Actions 워크플로우 상세
└── operations.md                # 운영 가이드
```

## 프로젝트 파이프라인 개요

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TECH-BLOG PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         CONTENT CREATION                             │   │
│   │                                                                      │   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │   │
│   │   │ Manual   │   │  Daily   │   │  AI      │   │  Cursor  │        │   │
│   │   │ Writing  │   │  News    │   │  Image   │   │  Editor  │        │   │
│   │   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘        │   │
│   │        └──────────────┴──────────────┴──────────────┘              │   │
│   │                              │                                      │   │
│   │                              ▼                                      │   │
│   │                    ┌──────────────────┐                            │   │
│   │                    │   Git Commit     │                            │   │
│   │                    │   (main branch)  │                            │   │
│   │                    └────────┬─────────┘                            │   │
│   └─────────────────────────────┼───────────────────────────────────────┘   │
│                                 │                                           │
│   ┌─────────────────────────────┼───────────────────────────────────────┐   │
│   │                             ▼           CI/CD PIPELINE               │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                     GitHub Actions                           │   │   │
│   │   │                                                              │   │   │
│   │   │   ┌──────────┐   ┌──────────┐   ┌──────────┐               │   │   │
│   │   │   │  Check   │──▶│  Build   │──▶│  Deploy  │               │   │   │
│   │   │   │ Changes  │   │  Jekyll  │   │  Pages   │               │   │   │
│   │   │   └──────────┘   └──────────┘   └──────────┘               │   │   │
│   │   │                                                              │   │   │
│   │   │   ┌──────────┐   ┌──────────┐                               │   │   │
│   │   │   │   SNS    │   │  Email   │   (Parallel)                  │   │   │
│   │   │   │  Share   │   │  Notify  │                               │   │   │
│   │   │   └──────────┘   └──────────┘                               │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                      Vercel                                  │   │   │
│   │   │   Auto-deploy on push → Production (tech.2twodragon.com)    │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         USER ENGAGEMENT                              │   │
│   │                                                                      │   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │   │
│   │   │  Giscus  │   │Buttondown│   │   RSS    │   │   SNS    │        │   │
│   │   │ Comments │   │Newsletter│   │   Feed   │   │  Share   │        │   │
│   │   └──────────┘   └──────────┘   └──────────┘   └──────────┘        │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         MONITORING                                   │   │
│   │                                                                      │   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐                        │   │
│   │   │  Sentry  │   │  Vercel  │   │  GitHub  │                        │   │
│   │   │  Errors  │   │ Analytics│   │  Actions │                        │   │
│   │   └──────────┘   └──────────┘   └──────────┘                        │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 워크플로우 요약

### 메인 워크플로우

| 워크플로우 | 파일 | 트리거 | 목적 |
|-----------|------|--------|------|
| **Jekyll CI** | jekyll.yml | push, PR | 빌드 및 GitHub Pages 배포 |
| **SNS Share** | sns-share.yml | push (_posts) | SNS 자동 공유 |
| **Buttondown** | buttondown-notify.yml | push (_posts) | 이메일 뉴스레터 |
| **Daily News** | daily-news.yml | schedule (daily) | 뉴스 수집 및 초안 생성 |
| **Image Gen** | generate-images.yml | workflow_dispatch | AI 이미지 생성 |

### 보조 워크플로우

| 워크플로우 | 파일 | 트리거 | 목적 |
|-----------|------|--------|------|
| **Sentry Release** | sentry-release.yml | deploy | 에러 추적 릴리스 |
| **AI Video** | ai-video-gen.yml | workflow_dispatch | 비디오 생성 |
| **CI Optimization** | ci-optimization.yml | - | CI 최적화 |
| **Vercel Deploy** | vercel-deploy.yml | - | Vercel 배포 보조 |

## 기능별 PDCA 연결

각 기능의 상세 PDCA 문서:

| 기능 | PDCA 문서 | 관련 워크플로우 |
|------|----------|----------------|
| 빌드 | [build.md](../pdca/build.md) | jekyll.yml |
| 배포 | [deploy.md](../pdca/deploy.md) | jekyll.yml, vercel-deploy.yml |
| 콘텐츠 | [content.md](../pdca/content.md) | daily-news.yml, generate-images.yml |
| 알림 | [notification.md](../pdca/notification.md) | sns-share.yml, buttondown-notify.yml |
| 모니터링 | [monitoring.md](../pdca/monitoring.md) | sentry-release.yml |
| 보안 | [security.md](../pdca/security.md) | 전체 |

## 프로젝트 상태

### 현재 상태
- **Production URL**: https://tech.2twodragon.com
- **Backup URL**: https://twodragon0.github.io/tech-blog
- **Repository**: https://github.com/Twodragon0/tech-blog

### 핵심 지표

| 지표 | 상태 |
|------|------|
| 빌드 상태 | Active |
| 배포 상태 | Active |
| 모니터링 | Active |
| 비용 | Free Tier 최적화 |

## 빠른 시작

### 로컬 개발
```bash
# 의존성 설치
bundle install
npm install

# 로컬 서버 실행
bundle exec jekyll serve --livereload
```

### 새 포스트 발행
```bash
# 1. 포스트 작성
vi _posts/YYYY-MM-DD-Title.md

# 2. 이미지 검증
python3 scripts/verify_images_unified.py --all

# 3. 커밋 및 푸시
git add . && git commit -m "Add: 포스트 제목" && git push

# 자동 실행:
# - Jekyll 빌드 및 배포
# - Vercel 배포
# - SNS 공유
# - 이메일 발송
```

### 수동 워크플로우 실행
```bash
# 이미지 생성
gh workflow run generate-images.yml

# 뉴스 수집
gh workflow run daily-news.yml
```

## 관련 문서

- [PDCA 기능 단위 문서](../pdca/README.md)
- [기술 스펙](../SPEC.md)
- [향후 계획](../TECH_BLOG_ENHANCEMENT_PLAN.md)
- [README](../../README.md)
