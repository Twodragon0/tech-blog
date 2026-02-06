# Documentation Index

This directory contains all technical documentation for the tech-blog project.

## Directory Structure

```
docs/
├── pdca/              # Feature-level PDCA documents (Plan-Do-Check-Act)
├── pipeline/          # Project-level pipeline & architecture
├── scripts/           # Script-specific documentation (moved from scripts/docs/)
├── guides/            # Content creation and feature guides
├── optimization/      # Performance and cost optimization guides
├── setup/             # Setup and configuration guides
└── troubleshooting/   # Troubleshooting and fixes
```

## Quick Navigation

### PDCA Documents (`pdca/`) - Feature-Level
PDCA (Plan-Do-Check-Act) documents for each feature:

- [README.md](pdca/README.md) - PDCA overview and index
- [build.md](pdca/build.md) - Jekyll build process
- [deploy.md](pdca/deploy.md) - GitHub Pages & Vercel deployment
- [content.md](pdca/content.md) - News collection & image generation
- [notification.md](pdca/notification.md) - SNS sharing & email newsletter
- [monitoring.md](pdca/monitoring.md) - Sentry error tracking & analytics
- [security.md](pdca/security.md) - Code security & dependency management

### Pipeline Documents (`pipeline/`) - Project-Level
Project-wide pipeline and architecture documentation:

- [README.md](pipeline/README.md) - Pipeline overview
- [architecture.md](pipeline/architecture.md) - System architecture
- [workflows.md](pipeline/workflows.md) - GitHub Actions workflows
- [operations.md](pipeline/operations.md) - Operations guide

### Script Documentation (`scripts/`)
Script-specific guides and references:

- [QUICK_START.md](scripts/QUICK_START.md) - Quick start guide
- [README_DAILY_NEWS.md](scripts/README_DAILY_NEWS.md) - Daily news collection
- [README_AI_IMPROVEMENT.md](scripts/README_AI_IMPROVEMENT.md) - AI-based post improvement
- [README_AUDIO_GENERATION.md](scripts/README_AUDIO_GENERATION.md) - Audio generation
- [README_POST_IMAGES.md](scripts/README_POST_IMAGES.md) - Post image generation
- [README_VIDEO_GENERATION.md](scripts/README_VIDEO_GENERATION.md) - Video generation
- [README_AUTO_SHARE.md](scripts/README_AUTO_SHARE.md) - SNS auto-share
- [README_LINKEDIN.md](scripts/README_LINKEDIN.md) - LinkedIn integration
- [COST_OPTIMIZATION_GUIDE.md](scripts/COST_OPTIMIZATION_GUIDE.md) - API cost optimization
- [GEMINI_OAUTH_SETUP.md](scripts/GEMINI_OAUTH_SETUP.md) - Gemini OAuth setup

### Content Guides (`guides/`)
- [BEST_PRACTICES.md](guides/BEST_PRACTICES.md) - Post writing best practices
- [GEMINI_IMAGE_GUIDE.md](guides/GEMINI_IMAGE_GUIDE.md) - Image generation with Gemini
- [POST_VISUALIZATION_CHECKLIST.md](guides/POST_VISUALIZATION_CHECKLIST.md) - Visualization checklist
- [POSTING_WRITING_RULES.md](guides/POSTING_WRITING_RULES.md) - Post writing rules
- [README_CHAT_WIDGET.md](guides/README_CHAT_WIDGET.md) - DeepSeek chat widget
- [README_GEMINI.md](guides/README_GEMINI.md) - Gemini API integration
- [README_SENTRY_LOGS.md](guides/README_SENTRY_LOGS.md) - Sentry logging guide
- [README_SITEMAP.md](guides/README_SITEMAP.md) - Sitemap configuration
- [README_SOCIAL_SHARING.md](guides/README_SOCIAL_SHARING.md) - SNS auto-share setup

### Optimization Guides (`optimization/`)
- [AD_OPTIMIZATION_GUIDE.md](optimization/AD_OPTIMIZATION_GUIDE.md) - Ad optimization
- [BLOG_OPTIMIZATION_GUIDE.md](optimization/BLOG_OPTIMIZATION_GUIDE.md) - Blog performance
- [DEEPSEEK_API_OPTIMIZATION.md](optimization/DEEPSEEK_API_OPTIMIZATION.md) - DeepSeek API
- [SENTRY_FREE_TIER_OPTIMIZATION.md](optimization/SENTRY_FREE_TIER_OPTIMIZATION.md) - Sentry free tier
- [TTFB_OPTIMIZATION_GUIDE.md](optimization/TTFB_OPTIMIZATION_GUIDE.md) - Time to First Byte
- [VERCEL_FREE_TIER_OPTIMIZATION.md](optimization/VERCEL_FREE_TIER_OPTIMIZATION.md) - Vercel free tier
- [VERCEL_PERFORMANCE_OPTIMIZATION.md](optimization/VERCEL_PERFORMANCE_OPTIMIZATION.md) - Vercel performance

### Setup Guides (`setup/`)
- [BUILD_IMPROVEMENTS.md](setup/BUILD_IMPROVEMENTS.md) - Build improvements
- [daum_search_registration.md](setup/daum_search_registration.md) - Daum search registration
- [LINKEDIN_APP_CREATION_GUIDE.md](setup/LINKEDIN_APP_CREATION_GUIDE.md) - LinkedIn app setup
- [SECURITY_AUDIT_REPORT.md](setup/SECURITY_AUDIT_REPORT.md) - Security audit
- [SECURITY_MONITORING_GUIDE.md](setup/SECURITY_MONITORING_GUIDE.md) - Security monitoring
- [SENTRY_GITHUB_FREE_TIER_OPTIMIZATION.md](setup/SENTRY_GITHUB_FREE_TIER_OPTIMIZATION.md) - Sentry + GitHub
- [SENTRY_VERCEL_GITHUB_INTEGRATION.md](setup/SENTRY_VERCEL_GITHUB_INTEGRATION.md) - Sentry + Vercel
- [VERCEL_DEPLOYMENT_OPTIMIZATION.md](setup/VERCEL_DEPLOYMENT_OPTIMIZATION.md) - Vercel deployment
- [VERCEL_ENV_SETUP.md](setup/VERCEL_ENV_SETUP.md) - Vercel environment setup
- [VERCEL_FIREWALL_SECURITY.md](setup/VERCEL_FIREWALL_SECURITY.md) - Vercel firewall

### Troubleshooting (`troubleshooting/`)
- [CHAT_API_TROUBLESHOOTING.md](troubleshooting/CHAT_API_TROUBLESHOOTING.md) - Chat API issues
- [ERROR_ANALYSIS_AND_FIXES.md](troubleshooting/ERROR_ANALYSIS_AND_FIXES.md) - Error analysis
- [MISSING_IMAGES_ISSUE.md](troubleshooting/MISSING_IMAGES_ISSUE.md) - Missing images
- [VERCEL_SECURITY_CHECKPOINT_FIX.md](troubleshooting/VERCEL_SECURITY_CHECKPOINT_FIX.md) - Security checkpoint

### Project Overview
- [SPEC.md](SPEC.md) - Project specification
- [TECH_BLOG_ENHANCEMENT_PLAN.md](TECH_BLOG_ENHANCEMENT_PLAN.md) - Enhancement plan

## Root Documentation

These files remain in the project root for quick access and convention compliance:

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `CLAUDE.md` | Claude Code instructions (includes Opus 4.6 optimization guide) |
| `AGENTS.md` | AI agent coding guidelines (includes Opus 4.6 best practices) |
| `.cursorrules` | Cursor AI rules (includes Opus 4.6 optimization principles) |
| `SECURITY.md` | Security policy |

## AI Assistant Optimization

### Opus 4.6 최대한 활용하기

Claude Opus 4.6는 의미 있는 업그레이드입니다. 프로젝트의 주요 AI 관련 문서에 Opus 4.6 활용 가이드가 포함되어 있습니다:

- **CLAUDE.md**: Opus 4.6 최대한 활용하기 섹션 (5가지 핵심 원칙)
- **AGENTS.md**: Opus 4.6 최대한 활용하기 섹션 (표 형식 요약)
- **.cursorrules**: Opus 4.6 최적화 원칙 (프롬프트 작성 가이드)

**핵심 원칙**:
1. **지시사항을 더 정확하게 따름**: 반복 지시 불필요, 의도 설명 포함
2. **행동하기 전에 맥락을 파악**: 관련 파일 공유, 간단한 작업은 범위 좁히기
3. **어려운 작업에서 끈기 있게 작업**: 확인 지점 설정, 협업 요청
4. **더 적극적으로 의견을 제시**: 대안 탐색, 스트레스 테스트
5. **더 강력한 글쓰기**: 스타일 매칭, 목소리 유지

자세한 내용은 각 문서의 해당 섹션을 참조하세요.

## See Also

- `scripts/README.md` - Scripts documentation
- `.github/` - GitHub Actions workflows and guides
