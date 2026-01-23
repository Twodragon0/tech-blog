# 소셜 공유 및 RSS 피드 설정 가이드

이 문서는 블로그의 소셜 공유 기능과 RSS 피드 설정에 대한 가이드를 제공합니다.

## 📱 카카오톡 공유 설정

### Open Graph 이미지 생성

카카오톡 공유 시 표시될 이미지를 생성하려면 다음 단계를 따르세요:

1. **SVG 이미지 확인**
   - 기본 SVG 이미지: `assets/images/og-default.svg`
   - 이미 생성되어 있습니다.

2. **PNG 이미지 생성**
   ```bash
   # 방법 1: Python 스크립트 사용 (cairosvg 필요)
   pip install cairosvg
   python scripts/generate_og_image.py

   # 방법 2: Inkscape 사용
   brew install inkscape  # macOS
   inkscape --export-type=png --export-width=1200 --export-height=630 \
     --export-filename=assets/images/og-default.png \
     assets/images/og-default.svg

   # 방법 3: librsvg 사용
   brew install librsvg  # macOS
   rsvg-convert --width=1200 --height=630 --format=png \
     --output=assets/images/og-default.png \
     assets/images/og-default.svg
   ```

3. **이미지 확인**
   - 생성된 파일: `assets/images/og-default.png`
   - 크기: 1200x630 (Open Graph 표준)

### 포스트별 이미지 설정

각 포스트의 front matter에 `image` 필드를 추가하면 해당 이미지가 공유 시 사용됩니다:

```yaml
---
layout: post
title: "포스트 제목"
date: 2025-01-08 16:00:00 +0900
image: /assets/images/2025-01-08-포스트_이미지.png
---
```

이미지가 없는 경우 기본 이미지(`og-default.png`)가 사용됩니다.

## 📡 RSS 피드

### RSS 피드 URL

- **피드 URL**: `https://twodragon0.github.io/tech-blog/feed.xml`
- **Atom 형식**: RSS 2.0 및 Atom 1.0 모두 지원

### RSS 피드 설정

`_config.yml`에 다음 설정이 포함되어 있습니다:

```yaml
feed:
  path: feed.xml
  excerpt_only: false
  categories: true
  tags: true
```

### RSS 리더에 추가하기

다음 RSS 리더에서 피드를 구독할 수 있습니다:

- **Feedly**: https://feedly.com
- **Inoreader**: https://www.inoreader.com
- **RSSOwl**: https://www.rssowl.org
- **기타 RSS 리더**: 피드 URL을 직접 입력

## 🗺️ Sitemap

### Sitemap URL

- **Sitemap URL**: `https://twodragon0.github.io/tech-blog/sitemap.xml`
- 자동으로 생성되며 모든 포스트와 페이지를 포함합니다.

### 검색 엔진 제출

다음 검색 엔진에 sitemap을 제출하세요:

1. **Google Search Console**
   - https://search.google.com/search-console
   - Sitemaps 섹션에서 URL 제출

2. **Bing Webmaster Tools**
   - https://www.bing.com/webmasters
   - Sitemaps 섹션에서 URL 제출

## 🤖 Robots.txt

### Robots.txt 위치

- **URL**: `https://twodragon0.github.io/tech-blog/robots.txt`
- 파일 위치: 프로젝트 루트의 `robots.txt`

### 설정 내용

- 모든 검색 엔진 크롤러 허용
- 내부 디렉토리(`_site`, `_posts` 등) 차단
- `feed.xml`, `sitemap.xml` 허용
- Sitemap 위치 명시

## 🔍 Open Graph 메타 태그

### 자동 생성되는 메타 태그

각 페이지에 다음 Open Graph 메타 태그가 자동으로 추가됩니다:

- `og:title`: 페이지 제목
- `og:description`: 페이지 설명
- `og:url`: 페이지 URL
- `og:type`: 페이지 유형 (article/website)
- `og:image`: 공유 이미지
- `og:image:width`: 이미지 너비 (1200)
- `og:image:height`: 이미지 높이 (630)
- `og:locale`: 언어 설정 (ko_KR)

### 포스트별 추가 메타 태그

포스트의 경우 다음 메타 태그도 추가됩니다:

- `article:author`: 작성자
- `article:published_time`: 발행 시간
- `article:modified_time`: 수정 시간 (있는 경우)
- `article:section`: 카테고리
- `article:tag`: 태그들

## 🐦 Twitter Card

Twitter Card도 자동으로 설정됩니다:

- `twitter:card`: summary_large_image
- `twitter:title`: 페이지 제목
- `twitter:description`: 페이지 설명
- `twitter:image`: 공유 이미지

## 📝 검증 도구

다음 도구로 Open Graph 설정을 검증할 수 있습니다:

1. **Facebook Sharing Debugger**
   - https://developers.facebook.com/tools/debug/
   - URL 입력 후 "Scrape Again" 클릭

2. **Twitter Card Validator**
   - https://cards-dev.twitter.com/validator
   - Twitter 계정 필요

3. **LinkedIn Post Inspector**
   - https://www.linkedin.com/post-inspector/
   - LinkedIn 계정 필요

4. **카카오톡 공유 미리보기**
   - 카카오톡 앱에서 링크 공유 시 자동으로 미리보기 표시
   - Open Graph 메타 태그를 읽어서 표시

## 🔒 보안 고려사항

1. **이미지 최적화**
   - 공유 이미지는 1200x630 크기로 최적화
   - 파일 크기는 1MB 이하 권장

2. **메타 태그 검증**
   - 프로덕션 배포 전 Open Graph 메타 태그 검증
   - 이미지 URL이 절대 경로인지 확인

3. **CSP 정책**
   - Content Security Policy가 소셜 공유 기능에 영향을 주지 않는지 확인

## 🚀 배포 후 확인사항

1. ✅ Open Graph 이미지가 올바르게 표시되는지 확인
2. ✅ RSS 피드가 정상적으로 작동하는지 확인
3. ✅ Sitemap이 모든 페이지를 포함하는지 확인
4. ✅ Robots.txt가 올바르게 설정되었는지 확인
5. ✅ 카카오톡 공유 시 미리보기가 올바르게 표시되는지 확인

## 📚 참고 자료

- [Open Graph Protocol](https://ogp.me/)
- [Twitter Cards](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [Jekyll Feed Plugin](https://github.com/jekyll/jekyll-feed)
- [Jekyll Sitemap Plugin](https://github.com/jekyll/jekyll-sitemap)
