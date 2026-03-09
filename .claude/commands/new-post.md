# 새 블로그 포스트 생성

새로운 Jekyll 블로그 포스트를 생성합니다.

## 실행 순서

1. **사용자에게 필수 정보 질문**
   - 제목 (Korean)
   - 카테고리 (security, devsecops, devops, cloud, kubernetes, finops, incident 중 선택)
   - 추가 카테고리 (선택)
   - 태그 (콤마로 구분)

2. **파일명 생성**
   - 형식: `YYYY-MM-DD-English_Title.md`
   - 한글 제목을 영문으로 변환 (단어는 언더스코어로 연결)
   - 오늘 날짜 사용
   - 예시: `2026-02-03-OpenClaw_Security_Vulnerability_Analysis.md`

3. **Front Matter 생성**
   ```yaml
   ---
   layout: post
   title: "제목 (사용자가 입력한 한글 제목)"
   date: YYYY-MM-DD HH:MM:SS +0900
   categories: [category1, category2]
   tags: [tag1, tag2, tag3]
   excerpt: "요약 (150-200자, 사용자에게 작성 요청)"
   description: "SEO description (200자 이내)"
   keywords: [keyword1, keyword2, keyword3]
   schema_type: Article
   author: Twodragon
   comments: true
   image: /assets/images/YYYY-MM-DD-English_Title.svg
   toc: true
   ---
   ```

4. **이미지 파일 경로 준비**
   - 경로: `/assets/images/YYYY-MM-DD-English_Title.svg`
   - 이미지는 나중에 `python3 scripts/generate_post_images.py` 명령으로 생성 가능

5. **파일 생성 및 열기**
   - `_posts/` 디렉토리에 파일 생성
   - 기본 템플릿 내용 작성

6. **사용자에게 안내**
   - 생성된 파일 경로 알려주기
   - 다음 단계:
     * 포스트 내용 작성
     * `python3 scripts/generate_post_images.py --post YYYY-MM-DD-English_Title.md` 명령으로 이미지 생성
     * `/validate-post` 명령으로 검증

## 참고사항

- 파일명은 반드시 영문만 사용 (한글 금지)
- 이미지 파일명도 영문만 사용
- SVG 텍스트는 영문만 (특수문자 금지: ·, •, —, ", ')
- 코드 블록은 언어 태그 필수 (```python, ```bash, ```yaml 등)
- 10줄 이상 코드는 GitHub 링크로 대체 권장
- 민감 정보 절대 하드코딩 금지
