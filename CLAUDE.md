# Claude Code Instructions for Tech Blog

이 파일은 Claude Code가 이 프로젝트에서 작업할 때 참조하는 지침서입니다.

## 프로젝트 개요

Jekyll 기반의 DevSecOps 기술 블로그입니다.
- **URL**: https://tech.2twodragon.com
- **주제**: DevSecOps, DevOps, FinOps, 클라우드 보안
- **언어**: 한국어 (코드 주석 제외)

## 핵심 작업 규칙

### 1. 보안 우선 (Security First)
- 모든 코드에서 민감 정보(API 키, 비밀번호, 토큰)는 절대 하드코딩 금지
- API 키는 반드시 환경 변수로 관리: `os.getenv("API_KEY", "")`
- 로그 출력 전 `mask_sensitive_info()` 함수로 마스킹 필수
- 파일 저장 전 `_validate_masked_text()` 검증 필수

### 2. 비용 최적화 (Cost Optimization)
- **Gemini API 직접 호출 최소화**: 비용 발생
- **우선순위**:
  1. Gemini CLI (`gemini` 명령어) - OAuth 2.0 인증, 무료
  2. Claude Console/Cursor - 무료 할당량 활용
  3. 로컬 템플릿 기반 처리
  4. API 호출은 마지막 수단

### 3. 커밋 규칙
- **Co-Authored-By 라인 제외**: 커밋 메시지에 `Co-Authored-By: Claude` 포함하지 않음
- 커밋 메시지는 한글 또는 영어로 간결하게 작성
- 예시:
  ```bash
  git commit -m "fix: 보안 경고 수정"
  git commit -m "feat: Add new feature"
  ```

## 파일 구조

```
tech-blog/
├── _posts/              # 블로그 포스트 (Markdown)
├── _layouts/            # Jekyll 레이아웃
├── _includes/           # 재사용 컴포넌트
├── assets/
│   ├── css/            # 스타일시트
│   ├── js/             # JavaScript
│   └── images/         # 이미지 (영어 파일명만)
├── scripts/            # Python/Bash 스크립트
├── api/                # Vercel Serverless Functions
└── CLAUDE.md           # 이 파일
```

## 포스트 작성 규칙

### 파일명
- 형식: `YYYY-MM-DD-영문_제목.md`
- 한글 파일명 금지
- 예: `2026-01-12-DevSecOps_Security_Guide.md`

### Front Matter
```yaml
---
layout: post
title: "제목 (한글 가능)"
date: YYYY-MM-DD HH:MM:SS +0900
category: [카테고리]
categories: [카테고리1, 카테고리2]
tags: [태그1, 태그2]
excerpt: "요약 (150-200자)"
image: /assets/images/영문파일명.svg
---
```

### 코드 블록
- 언어 태그 필수: ```python, ```bash, ```yaml
- 10줄 이상: GitHub 링크로 대체 + HTML 주석으로 원본 보존
- 3-10줄: 그대로 유지하되 참조 링크 추가
- 민감 정보는 `YOUR_API_KEY`, `***MASKED***` 등으로 대체

## 이미지 규칙

### 파일명
- **영어만 사용**: 한글 파일명 절대 금지
- 형식: `YYYY-MM-DD-English_Title.svg`
- 변환 스크립트: `python3 scripts/rename_images_to_english.py`

### SVG 텍스트
- **영어만 사용**: SVG 내부 텍스트도 영어로 작성
- 특수문자 금지: `·`, `•`, `—`, `"`, `'` 등
- UTF-8 인코딩 필수

## 스크립트 수정 시 주의사항

### 보안 패턴
```python
# 로그 출력
def log_message(message: str, level: str = "INFO"):
    safe_message = mask_sensitive_info(message)
    if _validate_masked_text(safe_message):
        print(safe_message)

# 파일 저장
def save_file(path: Path, content: str):
    safe_content = mask_sensitive_info(content)
    if _validate_masked_text(safe_content):
        with open(path, 'w') as f:
            f.write(safe_content)
```

### API 우선순위
```python
# 비용 최적화: CLI 우선, API는 마지막
def generate_content(text: str) -> str:
    # 1. Gemini CLI (무료)
    if check_gemini_cli_available():
        result = generate_with_gemini_cli(text)
        if result:
            return result

    # 2. 로컬 템플릿 (무료)
    result = generate_from_template(text)
    if result:
        return result

    # 3. API 호출 (비용 발생 - 마지막 수단)
    if GEMINI_API_KEY:
        return generate_with_gemini_api(text)

    return None
```

## 자주 사용하는 명령어

### 로컬 개발
```bash
# Jekyll 서버 시작
bundle exec jekyll serve

# 이미지 파일명 영어로 변환
python3 scripts/rename_images_to_english.py

# 포스트 이미지 생성
python3 scripts/generate_post_images.py
```

### Git 작업
```bash
# 변경 사항 확인
git status
git diff

# 커밋 (Co-Authored-By 없이)
git add .
git commit -m "fix: 설명"
git push origin main
```

## 참고 문서
- `.cursorrules`: Cursor IDE 규칙 (상세)
- `GEMINI_IMAGE_GUIDE.md`: 이미지 생성 가이드
- `POST_VISUALIZATION_CHECKLIST.md`: 시각화 체크리스트
- `README.md`: 프로젝트 개요
- `SECURITY.md`: 보안 정책

## 요약

1. **보안**: 민감 정보 마스킹 필수
2. **비용**: API 대신 CLI/로컬 처리 우선
3. **커밋**: Co-Authored-By 라인 제외
4. **이미지**: 영어 파일명만 사용
5. **코드 블록**: 언어 태그 필수
