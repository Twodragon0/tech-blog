# PDCA: 콘텐츠 관리 기능

> 뉴스 수집, 이미지 생성, 포스트 관리

## 현황

| 항목 | 값 |
|------|-----|
| **워크플로우** | `daily-news.yml`, `generate-images.yml` |
| **트리거** | schedule (daily), workflow_dispatch |
| **AI 서비스** | Gemini API |
| **상태** | Active |

---

## Plan (계획)

### 목표
- 자동화된 뉴스 수집 및 초안 생성
- AI 기반 이미지 자동 생성
- 콘텐츠 품질 유지

### KPI
| 지표 | 목표 | 현재 |
|------|------|------|
| 일일 뉴스 수집 | 10건+ | - |
| 이미지 생성 성공률 | 95%+ | - |
| API 비용 | 최소화 | - |

### 콘텐츠 파이프라인
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  RSS Feed   │ ──▶ │   Filter    │ ──▶ │  AI Draft   │ ──▶ │   Review    │
│  Collection │     │  & Analyze  │     │  Generation │     │   & Publish │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Image     │
                                        │  Generation │
                                        └─────────────┘
```

---

## Do (실행)

### 1. 일일 뉴스 수집 (daily-news.yml)

**스케줄:**
```yaml
schedule:
  - cron: '0 0 * * *'  # 매일 KST 09:00
```

**수집 소스:**
- 보안 벤더 블로그 (Jamf, Cloudflare, Snyk, HashiCorp 등)
- 기술 뉴스 RSS 피드
- KISA/CISA 보안 공지

**프로세스:**
```bash
# 뉴스 수집
python3 scripts/collect_tech_news.py --hours 24 --filter-processed

# 초안 생성 (AI 사용)
python3 scripts/generate_news_draft.py --use-ai --max-posts 10
```

**결과:**
- `_data/collected_news.json`: 수집된 뉴스 데이터
- `_drafts/*.md`: 생성된 초안
- PR 자동 생성 (검토용)

### 2. 이미지 생성 (generate-images.yml)

**트리거:**
```yaml
workflow_dispatch:  # 수동 실행만 (비용 관리)
```

**생성 타입:**
- `post`: 포스트 대표 이미지
- `segment`: 세그먼트별 이미지
- `both`: 둘 다

**프로세스:**
```bash
# 포스트 이미지 생성
python3 scripts/generate_post_images.py [post_file] [--force]

# 세그먼트 이미지 생성
python3 scripts/generate_segment_images.py [post_basename]
```

### 3. 로컬 스크립트

```bash
# 포스트 검증
python3 scripts/check_posts.py

# 이미지 검증
python3 scripts/verify_images_unified.py --all

# 링크 수정
python3 scripts/fix_links_unified.py --fix
```

---

## Check (점검)

### 모니터링 항목

#### 뉴스 수집 상태
```bash
# 수집된 뉴스 확인
cat _data/collected_news.json | jq '.total_items'

# 생성된 초안 확인
ls -la _drafts/
```

#### API 사용량
- Gemini API: https://makersuite.google.com/app/apikey
- 월간 사용량 및 비용 확인

#### RSS 피드 상태
```bash
# 주간 피드 상태 체크 (월요일 자동 실행)
# daily-news.yml의 check-sources job
```

### 점검 체크리스트
- [ ] 일일 뉴스 수집 정상 동작
- [ ] AI 초안 품질 검토
- [ ] 이미지 생성 성공률
- [ ] API 비용 예산 내 유지

---

## Act (개선)

### 식별된 개선점
1. **소스 다양화**: 더 많은 RSS 피드 추가
2. **필터링 개선**: 중복/저품질 콘텐츠 필터링 강화
3. **AI 프롬프트 최적화**: 초안 품질 향상

### 개선 이력
| 날짜 | 개선 내용 | 결과 |
|------|----------|------|
| - | - | - |

### 다음 사이클 계획
- [ ] 뉴스 소스 추가 (국내 보안 뉴스)
- [ ] AI 초안 템플릿 개선
- [ ] 이미지 스타일 통일화

---

## 비용 관리

### Gemini API 사용
| 항목 | 권장 |
|------|------|
| 일일 호출 수 | 제한 (10건 이하) |
| 수동 실행 | workflow_dispatch만 사용 |
| 캐싱 | 이전 생성 결과 재사용 |

### 비용 절감 팁
1. `--force` 플래그 최소화
2. 이미지 없는 포스트만 타겟
3. 일괄 처리로 API 호출 최소화

---

## 관련 문서

- [Pipeline 전체 흐름](../pipeline/README.md)
- [이미지 가이드](../guides/GEMINI_IMAGE_GUIDE.md)
- [일일 뉴스 스크립트](../../scripts/README.md)
