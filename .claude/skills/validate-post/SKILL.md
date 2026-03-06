---
name: validate-post
description: 포스트 품질을 검증합니다
argument-hint: "[파일명 또는 빈칸=최근 포스트]"
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

포스트 "$ARGUMENTS" (또는 최근 수정 포스트)를 검증합니다.

1. Front matter 검증:
   - 필수 필드: layout, title, date, category, tags, excerpt
   - 날짜 형식: YYYY-MM-DD HH:MM:SS +0900
   - 파일명: YYYY-MM-DD-English_Title.md (한국어 금지)
2. 이미지 검증:
   - `python3 scripts/verify_images_unified.py --all`
   - SVG 텍스트에 한국어 없는지 확인
   - 참조된 이미지 파일 존재 확인
3. 링크 검증:
   - `python3 scripts/fix_links_unified.py --check`
   - example.com 링크 없는지 확인
4. 코드 블록 검증:
   - 모든 코드 블록에 언어 태그 있는지 확인
5. 콘텐츠 검증:
   - FAQ 섹션 없는지 확인
   - 하드코딩된 비밀 없는지 확인
6. Jekyll 빌드 테스트: `bundle exec jekyll build`
