# Google Search Console Indexing Fixes

**작성일**: 2026-04-30
**대상**: 129 URLs not indexed (GSC coverage report)
**목표**: 카테고리별 indexing 실패 원인 진단 및 수정

## GSC Coverage Report 요약

| 카테고리 | URL 수 | 영향도 | 비고 |
|----------|-------|--------|------|
| Not found (404) | 16 | High | 잘못된 내부 링크 / 구 URL 패턴 |
| Page with redirect | 4 | Low | 정상 동작 (Google 안내) |
| Alternate page with proper canonical tag | 3 | None | 정상 동작 (canonical 작동) |
| Blocked by robots.txt | 2 | Low | 의도된 차단 (vendor / node_modules) |
| Excluded by 'noindex' tag | 1 | None | 의도된 차단 (`/llms.txt`, `/llms-full.txt`) |
| Crawled — currently not indexed | 103 | High | 콘텐츠 품질/내부 링크 신호 |
| **합계** | **129** | | |

## 카테고리별 점검 및 수정

### 1. Not found (404) — 16건

**원인 분석**:
- 일부 포스트의 내부 링크가 옛 permalink 패턴 (`/posts/YYYY/MM/<slug>/`, day 누락) 또는 슬러그에 날짜 prefix가 들어간 잘못된 형식 (`/posts/YYYY-MM-DD-<slug>/`) 으로 작성되어 있었음.
- `_config.yml permalink: /posts/:year/:month/:day/:title/` 형식이 정식.

**수정**:
- `_posts/2026-01-22-Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide.md`
  - `/posts/2026-01-17-AI_Coding_Assistants_Comparison_...` → `/posts/2026/01/17/AI_Coding_Assistants_Comparison_...`
- `_posts/2026-02-25-Claude_Code_OpenCode_Best_Practices.md`
  - `/posts/2026/01/Claude_MD_Security_Guide/` → `/posts/2026/01/28/Claude_MD_Security_Guide/`
  - `/posts/2026/02/AI_vs_Claude_Code_AI_Coding_Assistant_Comparison/` → `/posts/2026/02/04/AI_vs_Claude_Code_AI_Coding_Assistant_Comparison/`
- `vercel.json` 301 redirect 추가:
  - `/posts/2026-01-17-AI_Coding_Assistants_Comparison_...` → `/posts/2026/01/17/...` (외부에서 캐시된 잘못된 URL 보호망)
  - `/posts/2026/01/Claude_MD_Security_Guide/` 와 `/posts/2026/02/AI_vs_Claude_Code_AI_Coding_Assistant_Comparison/` 는 이미 vercel.json line 650, 715에 존재.

**Sitemap 검증**:
```
Total URLs in sitemap: 170
Missing files: 0
```
빌드된 `_site/sitemap.xml`의 모든 URL이 실제 파일에 매핑됨.

### 2. Page with redirect — 4건

**원인 분석**:
- `vercel.json`에 정의된 ~150건의 301 리다이렉트가 정상 동작.
- Google이 이를 인지하고 색인 대상에서 제외하는 것은 정상 동작.

**조치**: 별도 조치 불필요. 단, 리다이렉트 체인이 길지 않은지 주기적으로 확인할 것.

### 3. Alternate page with proper canonical tag — 3건

**원인 분석**:
- `_includes/head.html` line 70 `<link rel="canonical" href="...">` 가 모든 페이지에 정상 출력됨.
- 카테고리/태그 페이지나 페이지네이션이 캐노니컬을 통해 중복 제거되는 것을 Google이 정상 인지.

**조치**: 별도 조치 불필요. canonical 누락 의심 시 production HTML 직접 확인.

### 4. Blocked by robots.txt — 2건

**원인 분석**:
- `robots.txt` line 12-13:
  ```
  Disallow: /vendor/
  Disallow: /node_modules/
  ```
- `bundle install` 시 생성되는 `vendor/` 또는 `node_modules/` 잔재가 노출되어 Google이 시도했을 가능성.

**조치**: 의도된 차단. 별도 조치 불필요.

### 5. Excluded by 'noindex' tag — 1건

**원인 분석**:
- `vercel.json`이 `/llms.txt`, `/llms-full.txt`에 `X-Robots-Tag: noindex` 헤더 설정 (line 311, 328).
- LLM 학습 전용 텍스트 자료이므로 Google 색인 제외는 의도된 동작.

**조치**: 별도 조치 불필요.

### 6. Crawled — currently not indexed — 103건 (가장 큰 비중)

**원인 분석**:
- Google이 페이지를 크롤링했으나 색인할 가치가 부족하다고 판단.
- 일반적 원인:
  1. 콘텐츠가 비슷한 주제의 다른 포스트와 유사 (얇은 차별화)
  2. 내부 링크 신호 부족 (orphan-like)
  3. 외부 링크/도메인 권위 부족 (신생 도메인의 경우)
  4. 페이지 내 unique value가 부족 (자동 생성된 weekly digest는 위험군)
  5. 색인 우선순위 큐의 후순위 (시간 경과로 자동 색인 가능성)

**현 상태 점검**:
- 모든 155개 포스트가 front-matter 항목 (excerpt, image, tags, categories, title) 충실.
- `_layouts/post.html`이 related-posts (3개), category-link, tag-links, breadcrumb JSON-LD, BlogPosting JSON-LD를 모두 출력.
- `_includes/head.html`이 canonical, OG, Twitter Card, JSON-LD를 모두 출력.
- `sitemap.xml`이 `<lastmod>`, `<changefreq>`, `<priority>`, `<image:image>`까지 포함.

**구조적 개선 (이번 PR 범위)**:
1. `_config.yml exclude:`에 repo metadata 폴더/파일 추가 (`docs/`, `notes/`, `tests/`, `reports/`, `prisma/`, `AGENTS.md`, `CLAUDE.md` 등). 이로써 Jekyll이 `_site/`에 발행하지 않음 → 크롤러가 무가치 URL 시도 횟수 감소.
2. 깨진 내부 링크 3건 수정 (Not found 카테고리와 중복).
3. 안전망 redirect 1건 추가.

**장기 개선 (PR 범위 외, 콘텐츠 작업)**:
1. **유사 weekly digest 통합/축약**: 주 단위로 동일한 형식의 digest 포스트가 반복되어 Google이 "near-duplicate"로 분류할 가능성. 월간 통합 인덱스 페이지 강화 (`/posts/YYYY/MM/30/<Month>_YYYY_Security_Digest_Monthly_Index/`) 또는 weekly 포스트의 unique commentary 비중 확대 권장.
2. **외부 백링크 확보**: GitHub README, Tistory, 미디어 사이트, LinkedIn 글에서 본 블로그로 inbound 링크 추가.
3. **GSC 수동 색인 요청**: GSC > URL 검사 > "색인 요청" 으로 high-priority 포스트 (시리즈 가이드, 자격증 가이드 등)부터 처리.
4. **Last_modified_at 추가**: 155개 포스트 모두에 `last_modified_at` front-matter 부재. 실제 업데이트 시점을 명확히 하여 Google 재크롤 유도. 자동 스크립트는 git history 기반으로 일괄 추가 가능.

## 사용자 수동 작업 체크리스트

이 PR이 머지된 후 다음 GSC 작업을 권장:

| 단계 | 작업 | 위치 | 예상 시간 |
|------|------|------|-----------|
| 1 | 도메인 소유권 검증 확인 | GSC > Settings > Ownership verification | 즉시 |
| 2 | Sitemap 재제출 | GSC > Sitemaps > `https://tech.2twodragon.com/sitemap.xml` | 즉시 |
| 3 | Robots.txt 검증 | GSC > robots.txt Tester | 즉시 |
| 4 | 깨진 URL 수동 색인 요청 | GSC > URL Inspection (개별 URL) | 16건 × 1분 |
| 5 | "Crawled - currently not indexed" 우선순위 URL 5-10건 수동 색인 요청 | GSC > URL Inspection | 5-10분 |
| 6 | 1개월 후 coverage 재확인 | GSC > Coverage | 5분 |

## 검증 명령어

```bash
# Jekyll 빌드
eval "$(rbenv init -)" && rbenv exec bundle exec jekyll build --quiet --destination _site

# Sitemap 일관성 확인
python3 -c "
import re
from pathlib import Path
content = (Path('_site/sitemap.xml')).read_text()
urls = re.findall(r'<loc>https://tech\.2twodragon\.com(.*?)</loc>', content)
missing = [u for u in urls if not (Path('_site') / u.strip('/') / 'index.html').exists() and not (Path('_site') / u.strip('/')).exists() and u != '/']
print(f'Total: {len(urls)}, Missing: {len(missing)}')
"

# 발행 누수 확인 (예상: 21 항목, 데브 메타파일 없음)
ls _site/ | wc -l

# pytest 회귀 테스트
python3 -m pytest scripts/tests/ -q
```

## 모니터링 권장 주기

- **주간**: GSC Coverage 보고서 확인 (Indexed vs Not indexed 추이)
- **월간**: Sitemap 제출 상태, robots.txt 캐시 갱신 확인
- **분기별**: 핵심 키워드 검색 노출 (Performance > Queries) 분석, content gap 식별

## 관련 파일

- `_config.yml` (line 217+): `exclude:` 항목
- `_includes/head.html` (line 69, 70): GSC 검증 + canonical
- `robots.txt`: 검색엔진 크롤 정책
- `sitemap.xml`: 사이트맵 템플릿 (jekyll-sitemap 보완)
- `vercel.json` redirects: 약 ~150건의 301 redirect
- `_layouts/post.html`: 포스트 SEO 구조 (related-posts, breadcrumb, JSON-LD)
