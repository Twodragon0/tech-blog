# Twodragon0's Tech Blog

IT, DevSecOps, 코딩 관련 기술 블로그입니다.

## 구조

- `_posts/`: 블로그 포스트
- `_layouts/`: Jekyll 레이아웃 파일
- `_includes/`: 재사용 가능한 컴포넌트
- `assets/`: CSS, JS, 이미지 등 정적 파일

## 로컬 실행

```bash
bundle install
bundle exec jekyll serve
```

## Giscus 설정

1. [Giscus](https://giscus.app)에서 저장소 연결
2. `_config.yml`의 `giscus` 섹션에 `repo_id`와 `category_id` 입력
3. Discussions 활성화 확인

## 자동 배포

GitHub Actions를 통해 자동으로 배포됩니다.
