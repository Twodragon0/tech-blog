# PDCA: 배포 기능

> GitHub Pages 및 Vercel 배포 관리

## 현황

| 항목 | 값 |
|------|-----|
| **워크플로우** | `jekyll.yml` (deploy job), `vercel-deploy.yml` |
| **배포 대상** | GitHub Pages (백업), Vercel (프로덕션) |
| **도메인** | tech.2twodragon.com (Vercel), twodragon0.github.io/tech-blog (GH Pages) |
| **상태** | Active |

---

## Plan (계획)

### 목표
- 무중단 배포 보장
- 멀티 플랫폼 배포 (Vercel + GitHub Pages)
- 롤백 가능한 배포 체계

### KPI
| 지표 | 목표 | 현재 |
|------|------|------|
| 배포 성공률 | 99.9%+ | - |
| 배포 시간 | < 5분 | - |
| 다운타임 | 0 | - |

### 배포 전략
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Commit    │ ──▶ │    Build    │ ──▶ │   Deploy    │
│   (main)    │     │  (Jekyll)   │     │  (Parallel) │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                         ┌─────────────────────┼─────────────────────┐
                         ▼                     ▼                     ▼
                  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                  │   Vercel    │      │   GitHub    │      │    SNS      │
                  │ (Primary)   │      │   Pages     │      │   Share     │
                  │             │      │  (Backup)   │      │             │
                  └─────────────┘      └─────────────┘      └─────────────┘
```

---

## Do (실행)

### 1. GitHub Pages 배포 (백업)

```yaml
# jekyll.yml - deploy job
deploy:
  if: |
    github.event_name == 'push' && 
    github.ref == 'refs/heads/main' &&
    needs.build.result == 'success'
  
  concurrency:
    group: pages-deploy-${{ github.ref }}
    cancel-in-progress: false
```

**특징:**
- 빌드 성공 후에만 배포
- 동시 배포 방지 (concurrency)
- 15분 타임아웃

### 2. Vercel 배포 (프로덕션)

```yaml
# vercel-deploy.yml
# Vercel GitHub Integration으로 자동 배포
# 별도 워크플로우 불필요 (Vercel이 직접 감지)
```

**특징:**
- Push 시 자동 감지
- Preview 배포 (PR)
- Production 배포 (main)
- Edge CDN 자동 배포

### 3. 배포 검증

```yaml
- name: Deployment Info
  if: success()
  run: |
    echo "✅ Deployed to GitHub Pages"
    echo "URL: ${{ steps.deployment.outputs.page_url }}"
```

---

## Check (점검)

### 모니터링 항목

#### 배포 상태 확인
```bash
# GitHub Pages 배포 상태
gh api repos/Twodragon0/tech-blog/pages

# 최근 배포 이력
gh run list --workflow=jekyll.yml --limit=5
```

#### 사이트 가용성
- Vercel: https://tech.2twodragon.com
- GitHub Pages: https://twodragon0.github.io/tech-blog

### 점검 체크리스트
- [ ] 배포 후 사이트 접근 가능
- [ ] SSL 인증서 유효
- [ ] CDN 캐시 정상 동작
- [ ] 이미지/리소스 로드 정상

### 장애 대응
| 상황 | 대응 |
|------|------|
| Vercel 장애 | GitHub Pages로 DNS 전환 |
| 빌드 실패 | 이전 커밋으로 롤백 |
| 배포 지연 | GitHub Actions 재실행 |

---

## Act (개선)

### 식별된 개선점
1. **배포 알림**: Slack/Discord 알림 추가
2. **헬스체크**: 배포 후 자동 헬스체크 추가
3. **롤백 자동화**: 실패 시 자동 롤백

### 개선 이력
| 날짜 | 개선 내용 | 결과 |
|------|----------|------|
| - | - | - |

### 다음 사이클 계획
- [ ] 배포 후 헬스체크 자동화
- [ ] 배포 알림 시스템 구축
- [ ] 블루-그린 배포 검토

---

## 관련 문서

- [빌드 PDCA](build.md)
- [Pipeline 전체 흐름](../pipeline/README.md)
- [Vercel 설정](../setup/vercel.md)
