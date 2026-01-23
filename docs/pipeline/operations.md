# Pipeline Operations Guide

> tech-blog 프로젝트 운영 가이드

## 일상 운영

### 매일 (Daily)

#### 자동화된 작업
| 시간 (KST) | 작업 | 워크플로우 | 모니터링 |
|-----------|------|----------|---------|
| 06:00 | 뉴스 수집 | daily-news.yml | GitHub Actions 로그 |
| - | Sentry 이벤트 집계 | 자동 | Sentry Dashboard |
| - | Vercel 로그 수집 | 자동 | Vercel Dashboard |

#### 수동 체크리스트
- [ ] GitHub Actions 상태 확인 (실패한 워크플로우 확인)
- [ ] Sentry 에러 확인 (새로운 에러 또는 급증)
- [ ] Vercel Analytics 확인 (트래픽 이상)

### 매주 (Weekly)

#### 월요일 - 리뷰
- [ ] 지난주 에러 분석 및 조치
- [ ] GitHub Actions 사용량 확인 (2,000분/월 제한)
- [ ] Sentry 사용량 확인 (5,000 이벤트/월)

#### 금요일 - 정리
- [ ] `_drafts/` 폴더 정리
- [ ] 미발행 콘텐츠 검토
- [ ] 의존성 보안 알림 확인

### 매월 (Monthly)

#### 첫째 주
- [ ] 의존성 업데이트
  ```bash
  bundle update
  npm update
  pip list --outdated
  ```
- [ ] 보안 감사
  ```bash
  bundle audit --update
  npm audit
  ```

#### 셋째 주
- [ ] 성능 리뷰 (Core Web Vitals)
- [ ] 비용 최적화 검토 (Free Tier 사용량)
- [ ] 백업 검증 (GitHub Pages 접근 테스트)

---

## 일반 운영 작업

### 새 포스트 발행

#### 표준 발행 프로세스
```bash
# 1. 포스트 작성
vi _posts/YYYY-MM-DD-Title.md

# 2. 로컬 미리보기
bundle exec jekyll serve --livereload

# 3. 이미지 검증
python3 scripts/verify_images_unified.py --all

# 4. 링크 검증
python3 scripts/fix_links_unified.py --dry-run

# 5. 포스트 검증
python3 scripts/check_posts.py

# 6. 커밋 및 푸시
git add .
git commit -m "Add: 포스트 제목"
git push
```

#### 자동 후속 작업
1. **Jekyll 빌드** - GitHub Pages 배포
2. **Vercel 배포** - 프로덕션 사이트 업데이트
3. **SNS 공유** - Twitter, Facebook, LinkedIn
4. **이메일 발송** - Buttondown 구독자 알림

### 긴급 롤백

#### Vercel 롤백
```bash
# 이전 배포 목록 확인
vercel ls

# 특정 배포로 롤백
vercel rollback [deployment-url]
```

#### GitHub Pages 롤백
```bash
# 이전 커밋으로 되돌리기
git revert HEAD
git push

# 또는 특정 커밋으로
git revert [commit-hash]
git push
```

### 수동 워크플로우 실행

```bash
# 이미지 생성
gh workflow run generate-images.yml

# 뉴스 수집
gh workflow run daily-news.yml

# SNS 공유 재시도
gh workflow run sns-share.yml

# 특정 입력값과 함께 실행
gh workflow run generate-images.yml -f post_date=2026-01-22
```

---

## 모니터링 대시보드

### GitHub Actions
- **URL**: https://github.com/Twodragon0/tech-blog/actions
- **확인 항목**:
  - 실패한 워크플로우
  - 실행 시간 증가 추세
  - 월간 사용량

### Sentry
- **URL**: https://sentry.io/organizations/[org]/issues/
- **확인 항목**:
  - 신규 에러
  - 에러 빈도 증가
  - 월간 이벤트 사용량

### Vercel
- **URL**: https://vercel.com/dashboard
- **확인 항목**:
  - 배포 상태
  - Analytics (Core Web Vitals)
  - Function 로그

### 사이트 상태
| 항목 | 확인 방법 |
|------|----------|
| 프로덕션 | https://tech.2twodragon.com |
| 백업 | https://twodragon0.github.io/tech-blog |
| RSS | https://tech.2twodragon.com/feed.xml |
| Sitemap | https://tech.2twodragon.com/sitemap.xml |

---

## 문제 해결

### 빌드 실패

#### Jekyll 빌드 에러
```bash
# 로컬에서 재현
bundle exec jekyll build --trace

# 일반적인 원인
# - Front matter YAML 문법 오류
# - Liquid 템플릿 오류
# - 누락된 플러그인
```

#### Node.js 관련 에러
```bash
# 의존성 재설치
rm -rf node_modules
npm install

# 캐시 정리
npm cache clean --force
```

### 배포 실패

#### Vercel 배포 실패
1. Vercel 대시보드에서 빌드 로그 확인
2. `vercel.json` 설정 검토
3. 환경 변수 확인

```bash
# 로컬에서 Vercel 빌드 테스트
vercel build
```

#### GitHub Pages 배포 실패
1. Actions 로그 확인
2. `_config.yml` 검토
3. 브랜치 설정 확인 (Settings > Pages)

### SNS 공유 실패

#### Twitter API 에러
```bash
# API 키 유효성 확인
# GitHub Secrets 확인:
# - TWITTER_API_KEY
# - TWITTER_API_SECRET
# - TWITTER_ACCESS_TOKEN
# - TWITTER_ACCESS_SECRET
```

#### Facebook/LinkedIn 에러
- Access Token 만료 여부 확인
- API 권한 확인
- Rate Limit 확인

### 이미지 문제

#### 이미지 누락
```bash
# 이미지 검증
python3 scripts/verify_images_unified.py --all

# 누락된 이미지 생성
python3 scripts/generate_post_images.py --all
```

#### 이미지 파일명 문제
```bash
# 한글 파일명을 영어로 변환
python3 scripts/rename_images_to_english.py --yes
```

---

## 유지보수 스크립트

### 포스트 관리
```bash
# 전체 포스트 검증
python3 scripts/check_posts.py

# 링크 수정
python3 scripts/fix_links_unified.py --fix

# 이미지 검증
python3 scripts/verify_images_unified.py --all
```

### 이미지 관리
```bash
# 이미지 생성
python3 scripts/generate_post_images.py --all

# 이미지 파일명 변환 (한글→영어)
python3 scripts/rename_images_to_english.py --yes
```

### 뉴스 수집
```bash
# 최근 24시간 뉴스 수집
python3 scripts/collect_tech_news.py --hours 24

# 초안 생성
python3 scripts/generate_news_draft.py --use-ai --max-posts 10
```

### 모니터링
```bash
# Sentry 사용량 확인
./scripts/monitor_sentry_quota.sh

# Vercel 로그 확인
./scripts/check-vercel-logs.sh

# API 사용량 확인
python3 scripts/monitor_api_usage.py
```

### 코드 품질
```bash
# Python 린트 및 포맷
ruff check scripts/ --fix && ruff format scripts/

# 타입 검사
mypy scripts/ --ignore-missing-imports
```

---

## 비상 연락처

### 서비스 상태 페이지
| 서비스 | 상태 페이지 |
|--------|-----------|
| GitHub | https://www.githubstatus.com |
| Vercel | https://www.vercel-status.com |
| Sentry | https://status.sentry.io |
| Buttondown | https://status.buttondown.com |

### 지원 채널
| 서비스 | 지원 |
|--------|------|
| GitHub | https://support.github.com |
| Vercel | https://vercel.com/help |
| Sentry | https://help.sentry.io |

---

## Free Tier 제한 관리

### 월간 제한
| 서비스 | 제한 | 모니터링 |
|--------|------|---------|
| GitHub Actions | 2,000분 | Settings > Billing |
| Sentry | 5,000 이벤트 | Usage Stats |
| Vercel | 100GB 대역폭 | Dashboard |
| Buttondown | 100 구독자 | Dashboard |

### 최적화 전략
1. **GitHub Actions**: 캐시 활용, 불필요한 빌드 스킵
2. **Sentry**: 샘플링 적용, 에러 필터링
3. **Vercel**: Edge 캐싱 최적화
4. **API 호출**: 캐싱, Rate Limiting

### 비용 알림 설정
- GitHub: Billing > Spending limits
- Vercel: Project Settings > Alerts
- Sentry: Organization Settings > Quotas

---

## 관련 문서

- [아키텍처 상세](./architecture.md)
- [워크플로우 상세](./workflows.md)
- [PDCA 문서](../pdca/README.md)
- [Free Tier 최적화](../setup/FREE_TIER_OPTIMIZATION.md)
- [문제 해결 가이드](../troubleshooting/)
