# PDCA - 기능 단위 지속적 개선 문서

> **PDCA**: Plan-Do-Check-Act 사이클을 기능 단위로 관리

## 개요

이 디렉토리는 tech-blog 프로젝트의 각 **기능 단위**별 PDCA 사이클을 관리합니다.
각 기능은 독립적으로 계획, 실행, 점검, 개선됩니다.

## 문서 구조

```
docs/pdca/
├── README.md                    # 이 파일
├── build.md                     # 빌드 기능 PDCA
├── deploy.md                    # 배포 기능 PDCA
├── content.md                   # 콘텐츠 관리 기능 PDCA
├── notification.md              # 알림/공유 기능 PDCA
├── monitoring.md                # 모니터링 기능 PDCA
└── security.md                  # 보안 기능 PDCA
```

## 기능별 PDCA 요약

| 기능 | 워크플로우 | 현재 상태 | 마지막 점검 |
|------|-----------|----------|------------|
| [빌드](build.md) | jekyll.yml | Active | - |
| [배포](deploy.md) | vercel-deploy.yml, jekyll.yml | Active | - |
| [콘텐츠](content.md) | daily-news.yml, generate-images.yml | Active | - |
| [알림/공유](notification.md) | sns-share.yml, buttondown-notify.yml | Active | - |
| [모니터링](monitoring.md) | sentry-release.yml | Active | - |
| [보안](security.md) | ci-optimization.yml | Active | - |

## PDCA 사이클 가이드

### Plan (계획)
- 기능 목표 정의
- 성공 지표(KPI) 설정
- 리소스/비용 계획

### Do (실행)
- 워크플로우 구현
- 자동화 적용
- 문서화

### Check (점검)
- 지표 모니터링
- 문제점 식별
- 비용 분석

### Act (개선)
- 문제 해결
- 최적화 적용
- 다음 사이클 계획

## 관련 문서

- [Pipeline 프로젝트 전체 흐름](../pipeline/README.md)
- [기술 스펙](../SPEC.md)
- [향후 계획](../TECH_BLOG_ENHANCEMENT_PLAN.md)
