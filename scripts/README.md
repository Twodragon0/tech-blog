# Scripts 디렉토리 가이드

이 디렉토리에는 기술 블로그 관리를 위한 다양한 스크립트가 포함되어 있습니다.

## 📋 목차

- [주요 스크립트](#주요-스크립트)
- [카테고리별 스크립트](#카테고리별-스크립트)
- [사용 가이드](#사용-가이드)
- [통합 스크립트](#통합-스크립트)

## 주요 스크립트

### 포스트 검증 및 수정

#### `check_posts.py` - 통합 포스팅 검증
모든 포스팅의 일관성과 규칙 준수를 확인합니다.

```bash
# 모든 포스팅 검증
python3 scripts/check_posts.py

# 특정 파일만 검증
python3 scripts/check_posts.py _posts/2025-01-01-example.md
```

**검증 항목:**
- Front matter 필수 필드
- 이미지 파일명 (한글 확인)
- 이미지 파일 존재 여부
- 더미 링크
- 긴 코드 블록
- AI 요약 카드

#### `fix_links_unified.py` - 통합 링크 수정
부적절한 링크를 검증하고 수정합니다.

```bash
# 링크 확인만 (dry-run)
python3 scripts/fix_links_unified.py --check

# 링크 수정
python3 scripts/fix_links_unified.py --fix

# 특정 파일만 수정
python3 scripts/fix_links_unified.py --fix _posts/2025-01-01-example.md
```

**기능:**
- 부적절한 GitHub 링크 수정
- 더미 링크 제거
- 참고자료 링크 검증 및 수정
- 코드 블록 링크 개선

#### `verify_images_unified.py` - 통합 이미지 검증
이미지 파일을 검증하고 누락된 이미지를 확인합니다.

```bash
# 모든 포스팅 확인
python3 scripts/verify_images_unified.py --all

# 이미지가 없는 포스팅만 표시
python3 scripts/verify_images_unified.py --missing

# Gemini CLI 명령어 생성
python3 scripts/verify_images_unified.py --all --generate-commands
```

**기능:**
- 이미지 파일 존재 여부 확인
- 이미지 파일명 한글 확인
- 포스팅 파일의 이미지 경로와 실제 파일 매칭
- Gemini CLI 명령어 생성 (선택사항)

### 이미지 생성

#### `generate_missing_diagrams.py` - 누락된 다이어그램 생성
포스트에서 참조된 다이어그램 이미지가 없는 경우 Gemini API를 사용하여 생성합니다.

```bash
# 특정 포스팅 처리
python3 scripts/generate_missing_diagrams.py _posts/2025-01-01-example.md

# 강제 재생성
python3 scripts/generate_missing_diagrams.py _posts/2025-01-01-example.md --force
```

**필수 환경 변수:**
- `GEMINI_API_KEY`: Gemini API 키

#### `generate_og_banner.py` - OG 이미지 생성
포스팅용 Open Graph 이미지를 생성합니다.

```bash
python3 scripts/generate_og_banner.py
```

### 포스트 개선

#### `ai_improve_posts.py` - AI 기반 포스팅 개선
Claude API 또는 Gemini API를 사용하여 포스팅을 개선합니다.

```bash
python3 scripts/ai_improve_posts.py
```

**필수 환경 변수:**
- `CLAUDE_API_KEY` 또는 `GEMINI_API_KEY`

#### `smart_improve_posts.py` - 지능형 포스팅 개선
API 키 없이도 작동하는 기본 템플릿 기반 개선 스크립트입니다.

```bash
python3 scripts/smart_improve_posts.py
```

## 카테고리별 스크립트

### 포스트 검증
- `check_posts.py` - 통합 포스팅 검증
- `check_post_structure.py` - 포스트 구조 검증
- `check_toc.py` - 목차(TOC) 검증

### 링크 관리
- `fix_links_unified.py` - 통합 링크 수정 ⭐ (권장)
- `fix_all_links.py` - 모든 링크 수정 (구버전)
- `fix_github_links.py` - GitHub 링크 수정 (구버전)
- `fix_reference_links.py` - 참고자료 링크 수정 (구버전)
- `verify_post_links.py` - 포스트 링크 검증
- `validate_all_reference_links.py` - 모든 참고 링크 검증

### 이미지 관리
- `verify_images_unified.py` - 통합 이미지 검증 ⭐ (권장)
- `check_images.py` - 이미지 확인 (구버전)
- `verify_images.py` - 이미지 검증 (구버전)
- `check_unrelated_images.py` - 관련 없는 이미지 확인
- `rename_images_to_english.py` - 이미지 파일명 영어 변환
- `cleanup_empty_images.py` - 빈 이미지 정리

### 이미지 생성
- `generate_missing_diagrams.py` - 누락된 다이어그램 생성
- `generate_blog_diagrams.py` - 블로그 다이어그램 생성
- `generate_aws_diagram.py` - AWS 다이어그램 생성
- `generate_postmortem_diagrams.py` - 포스트모템 다이어그램 생성
- `generate_og_banner.py` - OG 이미지 생성
- `generate_favicon.py` - 파비콘 생성

### 오디오/비디오 생성
- `generate_audio_batch.py` - 배치 오디오 생성
- `generate_audio_from_script.py` - 스크립트에서 오디오 생성
- `generate_video_with_remotion.py` - Remotion으로 비디오 생성
- `generate_post_to_video.py` - 포스트를 비디오로 변환

### 포스트 개선
- `ai_improve_posts.py` - AI 기반 포스팅 개선
- `smart_improve_posts.py` - 지능형 포스팅 개선
- `enhance_all_posts.py` - 모든 포스팅 요약 섹션 보강
- `continuous_improve_posts.py` - 지속적인 포스팅 개선

### 설정 및 유틸리티
- `setup_gemini_api_key.sh` - Gemini API 키 설정
- `setup_gemini_oauth.sh` - Gemini OAuth 설정
- `setup_linkedin_keys.sh` - LinkedIn API 키 설정
- `install_dependencies.sh` - 의존성 설치

### 모니터링
- `monitor_sentry_quota.sh` - Sentry 할당량 모니터링
- `monitor_vercel_builds.sh` - Vercel 빌드 모니터링
- `check-vercel-logs.sh` - Vercel 로그 확인

## 통합 스크립트

### ⭐ 권장 사용 스크립트

다음 스크립트들은 여러 기능을 통합하여 사용하기 편리합니다:

1. **`check_posts.py`** - 포스팅 검증 (모든 검증 기능 통합)
2. **`fix_links_unified.py`** - 링크 수정 (모든 링크 수정 기능 통합)
3. **`verify_images_unified.py`** - 이미지 검증 (모든 이미지 검증 기능 통합)

### 구버전 스크립트

다음 스크립트들은 통합 스크립트로 대체되었습니다:

- `fix_all_links.py` → `fix_links_unified.py` 사용
- `fix_github_links.py` → `fix_links_unified.py` 사용
- `fix_reference_links.py` → `fix_links_unified.py` 사용
- `check_images.py` → `verify_images_unified.py` 사용
- `verify_images.py` → `verify_images_unified.py` 사용

## 사용 가이드

### 빠른 시작

#### 포스팅 검증
```bash
# 모든 포스팅 검증
python3 scripts/check_posts.py

# 특정 파일만 검증
python3 scripts/check_posts.py _posts/2025-01-01-example.md
```

#### 링크 수정
```bash
# 링크 확인만 (dry-run)
python3 scripts/fix_links_unified.py --check

# 링크 수정
python3 scripts/fix_links_unified.py --fix
```

#### 이미지 검증
```bash
# 모든 포스팅 확인
python3 scripts/verify_images_unified.py --all

# 이미지가 없는 포스팅만 표시
python3 scripts/verify_images_unified.py --missing
```

### 1. 포스팅 작성 후 검증 워크플로우

```bash
# 1. 포스팅 검증
python3 scripts/check_posts.py _posts/2025-01-01-example.md

# 2. 이미지 검증
python3 scripts/verify_images_unified.py --missing

# 3. 링크 검증
python3 scripts/fix_links_unified.py --check
```

### 2. 포스팅 개선

```bash
# AI 기반 개선 (API 키 필요)
python3 scripts/ai_improve_posts.py

# 기본 템플릿 기반 개선 (API 키 불필요)
python3 scripts/smart_improve_posts.py
```

### 3. 이미지 생성

```bash
# 누락된 다이어그램 생성
export GEMINI_API_KEY="your-key"
python3 scripts/generate_missing_diagrams.py _posts/2025-01-01-example.md
```

### 4. 일괄 처리

```bash
# 모든 포스팅 검증
python3 scripts/check_posts.py

# 모든 링크 수정
python3 scripts/fix_links_unified.py --fix

# 모든 이미지 검증
python3 scripts/verify_images_unified.py --all
```

## 환경 변수

주요 스크립트에서 사용하는 환경 변수:

- `GEMINI_API_KEY`: Gemini API 키 (이미지 생성, AI 개선)
- `CLAUDE_API_KEY`: Claude API 키 (AI 개선)
- `DEEPSEEK_API_KEY`: DeepSeek API 키 (채팅 위젯)
- `LINKEDIN_CLIENT_ID`: LinkedIn 클라이언트 ID
- `LINKEDIN_CLIENT_SECRET`: LinkedIn 클라이언트 시크릿

## 의존성

필수 Python 패키지는 `requirements.txt`에 정의되어 있습니다:

```bash
pip install -r scripts/requirements.txt
```

## 보안 고려사항

- 모든 API 키는 환경 변수로 관리합니다
- 민감한 정보는 절대 하드코딩하지 않습니다
- 로그에 민감 정보가 포함되지 않도록 주의합니다
- 스크립트 실행 전 백업을 권장합니다

## 문제 해결

### 스크립트 실행 오류

1. **Python 버전 확인**: Python 3.8 이상 필요
2. **의존성 설치**: `pip install -r scripts/requirements.txt`
3. **경로 확인**: 프로젝트 루트에서 실행

### API 키 오류

1. 환경 변수 확인: `echo $GEMINI_API_KEY`
2. `.env` 파일 확인 (있는 경우)
3. 스크립트 내 환경 변수 로딩 확인

### 이미지 생성 실패

1. Gemini API 키 확인
2. API 할당량 확인
3. 네트워크 연결 확인
4. 재시도: `--force` 옵션 사용

## 추가 문서

- [AI 개선 가이드](README_AI_IMPROVEMENT.md)
- [이미지 생성 가이드](../../GEMINI_IMAGE_GUIDE.md)
- [오디오 생성 가이드](README_AUDIO_GENERATION.md)
- [비디오 생성 가이드](README_POST_TO_VIDEO.md)

## 기여

새로운 스크립트를 추가하거나 기존 스크립트를 개선할 때:

1. 보안 우선 원칙 준수
2. 에러 핸들링 포함
3. 로그에 민감 정보 마스킹
4. 문서 업데이트
