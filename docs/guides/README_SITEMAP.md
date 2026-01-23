# Sitemap 설정 가이드

이 문서는 블로그의 sitemap 설정에 대한 가이드를 제공합니다.

## 📍 Sitemap 위치

- **Sitemap URL**: `https://twodragon0.github.io/tech-blog/sitemap.xml`
- **파일 위치**: 프로젝트 루트의 `sitemap.xml`

## 🔧 Sitemap 구성

### 자동 생성 vs 수동 생성

블로그는 **수동으로 작성된 sitemap.xml**을 사용합니다. 이는 다음 이유 때문입니다:

1. **더 세밀한 제어**: priority와 changefreq를 동적으로 설정
2. **최신성 반영**: 포스트의 최근 수정일 반영
3. **커스터마이징**: 특정 페이지 제외 또는 우선순위 조정 가능

### 포함되는 페이지

1. **홈페이지** (`/`)
   - Priority: 1.0
   - Changefreq: daily

2. **정적 페이지** (About, Archive 등)
   - Priority: 0.6-0.8
   - Changefreq: weekly/monthly

3. **블로그 포스트** (`/posts/...`)
   - Priority: 0.6-0.9 (최근 포스트일수록 높음)
   - Changefreq: weekly/monthly/yearly (최근 포스트일수록 자주 업데이트)

4. **카테고리 페이지** (`/categories/...`)
   - Priority: 0.7
   - Changefreq: weekly

5. **태그 페이지** (`/tags/`)
   - Priority: 0.6
   - Changefreq: weekly

### Priority 설정 규칙

- **홈페이지**: 1.0 (최우선)
- **최근 포스트** (30일 이내): 0.9
- **중간 포스트** (180일 이내): 0.8
- **오래된 포스트** (180일 이상): 0.6
- **정적 페이지**: 0.6-0.8

### Changefreq 설정 규칙

- **홈페이지**: daily
- **최근 포스트** (30일 이내): weekly
- **중간 포스트** (180일 이내): monthly
- **오래된 포스트** (180일 이상): yearly
- **정적 페이지**: weekly/monthly

## 🔍 검색 엔진 제출

### Google Search Console

1. https://search.google.com/search-console 접속
2. 속성 선택 또는 추가
3. 좌측 메뉴에서 "Sitemaps" 클릭
4. 다음 URL 입력: `https://twodragon0.github.io/tech-blog/sitemap.xml`
5. "제출" 클릭

### Bing Webmaster Tools

1. https://www.bing.com/webmasters 접속
2. 사이트 추가 또는 선택
3. 좌측 메뉴에서 "Sitemaps" 클릭
4. 다음 URL 입력: `https://twodragon0.github.io/tech-blog/sitemap.xml`
5. "제출" 클릭

### Naver Search Advisor (네이버 웹마스터)

1. https://searchadvisor.naver.com 접속
2. 사이트 등록 또는 선택
3. "요청" > "사이트맵 제출" 클릭
4. 다음 URL 입력: `https://twodragon0.github.io/tech-blog/sitemap.xml`
5. "확인" 클릭

## 🛠️ Sitemap 커스터마이징

### 특정 페이지 제외

포스트나 페이지의 front matter에 다음을 추가:

```yaml
---
sitemap:
  exclude: 'yes'
---
```

### Priority 수정

특정 페이지의 priority를 변경하려면 sitemap.xml 파일을 직접 수정:

```xml
<url>
  <loc>{{ site.url }}{{ site.baseurl }}{{ page.url }}</loc>
  <priority>0.9</priority>  <!-- 원하는 값으로 변경 -->
</url>
```

## 📊 Sitemap 검증

### 온라인 검증 도구

1. **XML Sitemap Validator**
   - https://www.xml-sitemaps.com/validate-xml-sitemap.html
   - XML 형식 및 구조 검증

2. **Google Search Console**
   - Sitemaps 섹션에서 제출 상태 확인
   - 크롤링 오류 확인

3. **Bing Webmaster Tools**
   - Sitemaps 섹션에서 제출 상태 확인
   - 인덱싱 상태 확인

### 로컬 검증

```bash
# Jekyll 빌드 후 sitemap 확인
bundle exec jekyll build
cat _site/sitemap.xml | head -50

# XML 형식 검증
xmllint --noout _site/sitemap.xml
```

## 🔄 Sitemap 업데이트

Sitemap은 Jekyll 빌드 시 자동으로 업데이트됩니다:

1. **로컬 빌드**: `bundle exec jekyll build`
2. **GitHub Pages**: 자동 빌드 및 배포
3. **수동 업데이트**: 필요 시 `sitemap.xml` 파일 직접 수정

## 📝 Sitemap 최적화 팁

1. **정기적인 업데이트**: 새 포스트 발행 시 자동 업데이트
2. **Priority 조정**: 중요한 포스트는 priority를 높게 설정
3. **Changefreq 조정**: 자주 업데이트되는 페이지는 changefreq를 높게 설정
4. **제외 페이지 관리**: 불필요한 페이지는 sitemap에서 제외

## 🚨 주의사항

1. **파일 크기**: Sitemap 파일은 50MB 이하, URL은 50,000개 이하 권장
2. **URL 형식**: 절대 URL 사용 (상대 URL 사용 시 오류 발생 가능)
3. **인코딩**: 한글 URL은 자동으로 URL 인코딩됨
4. **lastmod**: 정확한 날짜 형식 사용 (ISO 8601)

## 📚 참고 자료

- [Sitemaps.org](https://www.sitemaps.org/)
- [Google Sitemap 가이드](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- [Jekyll Sitemap Plugin](https://github.com/jekyll/jekyll-sitemap)
