# 블로그 포스트 검증

블로그 포스트의 형식, 이미지, 보안 요소를 검증합니다.

## 검증 항목

### 1. Front Matter 완전성
- [ ] `layout: post` 존재
- [ ] `title` 존재 (한글 OK)
- [ ] `date` 형식: `YYYY-MM-DD HH:MM:SS +0900`
- [ ] `categories` 배열 존재
- [ ] `tags` 배열 존재 (3개 이상 권장)
- [ ] `excerpt` 존재 (150-200자)
- [ ] `description` 존재 (SEO용, 200자 이내)
- [ ] `keywords` 배열 존재
- [ ] `author: Twodragon` 존재
- [ ] `image` 경로 존재
- [ ] `toc: true` 존재 (목차 활성화)

### 2. 파일명 검증
- [ ] 형식: `YYYY-MM-DD-English_Title.md`
- [ ] 한글 문자 없음 (영문, 숫자, 언더스코어, 하이픈만)
- [ ] `_posts/` 디렉토리에 위치

### 3. 이미지 검증
- [ ] Front matter의 `image` 필드에 지정된 파일이 실제로 존재
- [ ] 이미지 파일명이 영문만 사용
- [ ] SVG 파일인 경우, 텍스트가 영문만 사용 (특수문자 금지)
- [ ] 경로: `/assets/images/YYYY-MM-DD-English_Title.svg`

### 4. 코드 블록 검증
- [ ] 모든 코드 블록에 언어 태그 지정 (```python, ```bash, ```yaml 등)
- [ ] 10줄 이상 코드는 GitHub 링크로 대체 권장
- [ ] 코드 블록에 민감 정보 없음

### 5. 보안 검증
- [ ] API 키, 비밀번호, 토큰 등 하드코딩 없음
- [ ] `YOUR_API_KEY`, `***MASKED***` 등 마스킹 처리 확인
- [ ] 개인정보 노출 없음

### 6. 링크 검증
- [ ] 깨진 링크 없음 (example.com 등 금지)
- [ ] 모든 링크가 실제 리소스를 가리킴

## 실행 방법

1. **수동 검증**: 위 체크리스트를 하나씩 확인
2. **자동 검증**: `python3 scripts/check_posts.py` 실행 (가능한 경우)
3. **이미지 검증**: `python3 scripts/verify_images_unified.py --all` 실행
4. **링크 검증**: `python3 scripts/fix_links_unified.py --check` 실행

## 결과 보고

- 발견된 모든 이슈 나열
- 심각도 표시 (HIGH/MEDIUM/LOW)
- 수정 방법 제안

## 자동 수정 (선택)

사용자가 명시적으로 요청한 경우에만:
- `/validate-post --fix`: 자동으로 수정 가능한 이슈 수정
- 수정 전 백업 생성
- 수정 내용 요약 보고
