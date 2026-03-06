---
name: new-post
description: 새 블로그 포스트를 생성합니다
argument-hint: "[주제/제목]"
user-invocable: true
disable-model-invocation: true
---

새 블로그 포스트 "$ARGUMENTS"를 생성합니다.

1. 기존 포스트 패턴 분석 (최근 _posts/ 파일 참고)
2. 파일 생성: `_posts/YYYY-MM-DD-English_Title.md`
   - 한국어 제목, 영문 파일명
   - Front matter: layout, title, date, category, categories, tags, excerpt, image
3. SVG 대표 이미지 생성: `assets/images/YYYY-MM-DD-English_Title.svg`
   - SVG 텍스트는 영문만 사용
   - 주제에 맞는 아이콘/다이어그램 포함
4. 콘텐츠 구조:
   - ai-summary-card 포함
   - 실무 중심 기술 내용
   - 코드 예제와 설정 파일
   - 트러블슈팅 섹션
   - FAQ 절대 금지
5. `python3 scripts/check_posts.py`로 포스트 검증
