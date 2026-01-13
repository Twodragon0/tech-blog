# 포스팅 이미지 자동 생성 가이드

포스팅 작성 후 자동으로 이미지 생성 프롬프트를 생성하고, 이미지가 없으면 안내하는 스크립트입니다.

## 📋 목차

1. [기능 개요](#기능-개요)
2. [설치 및 설정](#설치-및-설정)
3. [사용 방법](#사용-방법)
4. [워크플로우](#워크플로우)
5. [문제 해결](#문제-해결)

---

## 기능 개요

### 주요 기능

- **자동 프롬프트 생성**: 포스팅 내용을 분석하여 적절한 이미지 생성 프롬프트 자동 생성
- **이미지 존재 확인**: 포스팅의 이미지 파일 존재 여부 확인
- **카테고리별 스타일**: 보안, DevSecOps, 클라우드 등 카테고리별 최적화된 스타일 적용
- **프롬프트 파일 저장**: 생성된 프롬프트를 파일로 저장하여 재사용 가능

### 지원하는 이미지 형식

- **SVG**: 벡터 이미지 (권장)
- **PNG**: 래스터 이미지 (OG 이미지용)

---

## 설치 및 설정

### 필수 요구사항

```bash
# Python 패키지 설치
pip install frontmatter requests
```

### 환경 변수 설정

#### 로컬 환경

Gemini API 키를 설정하면 실제 이미지를 생성할 수 있습니다:

```bash
export GEMINI_API_KEY='your-gemini-api-key'
```

#### GitHub Actions (권장) ⭐

GitHub Secrets에 `GEMINI_API_KEY`를 설정하면 GitHub Actions에서 자동으로 이미지를 생성할 수 있습니다:

1. **GitHub Secrets 설정**:
   ```bash
   # GitHub CLI 사용 (권장)
   gh secret set GEMINI_API_KEY --body 'your-gemini-api-key'
   
   # 또는 GitHub 웹 인터페이스 사용
   # Settings → Secrets and variables → Actions → New repository secret
   ```

2. **워크플로우 실행**:
   - GitHub 저장소 → **Actions** 탭
   - **Generate Post Images** 워크플로우 선택
   - **Run workflow** 클릭
   - 옵션 설정:
     - `post_file`: 특정 포스트 파일명 (선택사항)
     - `image_type`: `post` (포스트 이미지), `segment` (세그먼트 이미지), `both` (둘 다)
     - `force`: 이미지가 있어도 강제 재생성 (선택사항)

> **참고**: 
> - 로컬에서는 API 키가 없어도 프롬프트만 생성됩니다.
> - GitHub Actions에서는 `GEMINI_API_KEY`가 필수입니다 (실제 이미지 생성).
> - 자세한 내용: [.github/SECRETS_MANAGEMENT.md](../.github/SECRETS_MANAGEMENT.md)

---

## 사용 방법

### 기본 사용법

```bash
# 최근 포스팅 이미지 생성
python3 scripts/generate_post_images.py --recent 1

# 특정 포스팅 이미지 생성
python3 scripts/generate_post_images.py _posts/2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.md

# 모든 포스팅 이미지 생성
python3 scripts/generate_post_images.py --all

# 이미지가 없는 포스팅만 처리
python3 scripts/generate_post_images.py --missing

# 이미지가 있어도 강제로 재생성
python3 scripts/generate_post_images.py --recent 1 --force
```

### 옵션 설명

| 옵션 | 설명 |
|------|------|
| `post_file` | 처리할 포스팅 파일 (선택사항) |
| `--all` | 모든 포스팅 처리 |
| `--recent N` | 최근 N개 포스팅만 처리 (기본값: 1) |
| `--force` | 이미지가 있어도 강제로 재생성 |
| `--missing` | 이미지가 없는 포스팅만 처리 |

---

## 워크플로우

### GitHub Actions 사용 (권장) ⭐

GitHub Actions를 사용하면 자동으로 이미지를 생성할 수 있습니다:

1. **GitHub Secrets 설정** (최초 1회):
   ```bash
   gh secret set GEMINI_API_KEY --body 'your-gemini-api-key'
   ```

2. **워크플로우 실행**:
   - GitHub 저장소 → **Actions** 탭
   - **Generate Post Images** 선택
   - **Run workflow** 클릭
   - 옵션 설정 후 실행

3. **생성된 이미지 확인**:
   - 워크플로우 완료 후 **Artifacts**에서 다운로드
   - 또는 저장소의 `assets/images/` 디렉토리 확인

**장점**:
- 로컬 환경 설정 불필요
- GitHub Secrets로 안전한 API 키 관리
- 자동화된 이미지 생성
- 생성된 이미지 자동 다운로드

### 로컬 워크플로우

### 1. 새 포스팅 작성 후

```bash
# 1. 포스팅 작성 완료
# 2. 이미지 생성 프롬프트 생성
python3 scripts/generate_post_images.py _posts/새포스팅.md

# 3. 생성된 프롬프트 파일 확인
cat assets/images/새포스팅_prompt.txt

# 4. 프롬프트를 사용하여 이미지 생성
# - DALL-E: https://platform.openai.com/docs/guides/images
# - Midjourney: https://www.midjourney.com/
# - Stable Diffusion: https://stability.ai/
# - Gemini Studio: https://makersuite.google.com/app/prompts/image

# 5. 생성된 이미지를 assets/images/ 디렉토리에 저장
# 6. 포스팅의 front matter에서 image 경로 확인
```

### 2. 이미지가 없는 포스팅 찾기

```bash
# 이미지가 없는 포스팅 확인
python3 scripts/generate_post_images.py --missing

# 이미지가 없는 포스팅에 대해 프롬프트 생성
python3 scripts/generate_post_images.py --missing --recent 10
```

### 3. 일괄 처리

```bash
# 최근 5개 포스팅 이미지 생성
python3 scripts/generate_post_images.py --recent 5

# 모든 포스팅 이미지 생성
python3 scripts/generate_post_images.py --all
```

---

## 프롬프트 파일 형식

생성된 프롬프트 파일은 다음 형식을 따릅니다:

```
# Image Generation Prompt

Generated: 2026-01-11 19:29:48
Output: 2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.svg

================================================================================
PROMPT:
================================================================================

Create a nano banana style illustration for a tech blog post.

Title: AI 기반 음악 비디오 생성 완벽 가이드: DevSecOps 관점에서 본 생성형 AI 활용법
Category: devsecops
Content Summary: [핵심 내용 요약]

Requirements:
- Style: minimalist DevSecOps pipeline illustration
- Colors: Blue (#0066CC) for CI/CD, Green (#00AA44) for security, Orange (#FF6600) for deployment
- Layout: horizontal, optimized for blog post (1200x800px recommended)
- Include: Korean labels for key components (if applicable)
- Professional and modern design
- Clean and minimalist aesthetic
- Suitable for technical blog post header image

================================================================================
USAGE:
================================================================================

이 프롬프트를 사용하여 다음 도구로 이미지를 생성할 수 있습니다:

1. DALL-E (OpenAI): https://platform.openai.com/docs/guides/images
2. Midjourney: https://www.midjourney.com/
3. Stable Diffusion: https://stability.ai/
4. Gemini Studio: https://makersuite.google.com/app/prompts/image
```

---

## 카테고리별 스타일

스크립트는 포스팅의 카테고리에 따라 자동으로 적절한 스타일을 적용합니다:

| 카테고리 | 스타일 | 색상 팔레트 |
|---------|--------|------------|
| `security` | minimalist security illustration | Red (#CC0000) for threats, Green (#00AA44) for security measures |
| `devsecops` | minimalist DevSecOps pipeline illustration | Blue (#0066CC) for CI/CD, Green (#00AA44) for security |
| `cloud` | minimalist cloud architecture illustration | AWS orange (#FF9900), Blue (#0066CC) for networking |
| `kubernetes` | minimalist Kubernetes architecture illustration | Kubernetes blue (#326CE5), Green (#00AA44) for pods |
| `incident` | minimalist incident timeline illustration | Red, Orange, Yellow, Green for different phases |

---

## 이미지 생성 도구 사용법

### DALL-E (OpenAI)

```bash
# OpenAI API 사용
curl https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "dall-e-3",
    "prompt": "[프롬프트 내용]",
    "size": "1024x1024",
    "quality": "standard",
    "n": 1
  }'
```

### Midjourney

1. Discord에서 Midjourney 봇 사용
2. `/imagine` 명령어 사용
3. 프롬프트 입력

### Stable Diffusion

```python
# Python 예제
from diffusers import StableDiffusionPipeline
import torch

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "[프롬프트 내용]"
image = pipe(prompt).images[0]
image.save("output.png")
```

---

## 문제 해결

### 프롬프트가 생성되지 않음

```bash
# 포스팅 파일 확인
cat _posts/포스팅명.md

# front matter 확인
# title, category, image 필드가 올바르게 설정되어 있는지 확인
```

### 이미지 경로 오류

```bash
# 이미지 경로 형식 확인
# 올바른 형식: /assets/images/파일명.svg
# 또는: assets/images/파일명.svg
```

### Gemini API 오류

#### 로컬 환경

```bash
# API 키 확인
echo $GEMINI_API_KEY

# API 키 재설정
export GEMINI_API_KEY='your-new-key'
```

#### GitHub Actions

```bash
# GitHub Secrets 확인
gh secret list | grep GEMINI_API_KEY

# GitHub Secrets 재설정
gh secret set GEMINI_API_KEY --body 'your-new-key'

# 워크플로우 재실행
# GitHub 저장소 → Actions → Generate Post Images → Run workflow
```

### 워크플로우 실행 실패

1. **GitHub Secrets 확인**:
   ```bash
   gh secret list
   ```

2. **워크플로우 로그 확인**:
   - GitHub 저장소 → Actions → 실패한 워크플로우 → 로그 확인

3. **API 키 형식 확인**:
   - Gemini API 키는 최소 20자 이상이어야 합니다
   - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급 확인

---

## 참고 자료

- [GEMINI_IMAGE_GUIDE.md](../GEMINI_IMAGE_GUIDE.md) - 이미지 생성 가이드
- [POST_VISUALIZATION_CHECKLIST.md](../POST_VISUALIZATION_CHECKLIST.md) - 포스팅별 시각화 체크리스트
- [POSTING_WRITING_RULES.md](../POSTING_WRITING_RULES.md) - 포스팅 작성 규칙

---

**마지막 업데이트**: 2026-01-11
