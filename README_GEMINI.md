# Gemini CLI 활용 가이드

이 문서는 Gemini CLI를 사용하여 포스팅 요약 개선 및 이미지 생성을 위한 가이드입니다.

## 📋 목차

1. [설치 및 설정](#설치-및-설정)
2. [포스팅 요약 개선](#포스팅-요약-개선)
3. [이미지 확인 및 생성](#이미지-확인-및-생성)
4. [스크립트 사용법](#스크립트-사용법)

---

## 설치 및 설정

### Gemini CLI 설치

```bash
npm install -g @google/gemini-cli
```

### API 키 설정

Gemini CLI는 Google AI Studio API 키가 필요합니다. 환경 변수로 설정하거나 CLI 설정에서 구성할 수 있습니다.

```bash
export GEMINI_API_KEY="your-api-key-here"
```

또는 `~/.gemini/config.json` 파일에 설정:

```json
{
  "apiKey": "your-api-key-here"
}
```

---

## 포스팅 요약 개선

### 자동 요약 개선 스크립트

포스팅의 요약 섹션을 Gemini CLI를 사용하여 자동으로 개선할 수 있습니다.

```bash
# 최근 5개 포스팅 분석
python3 scripts/improve_post_summary.py --recent 5

# 특정 포스팅 분석 및 요약 개선
python3 scripts/improve_post_summary.py "2025-12-24-클라우드_시큐리티_과정_8기_5주차_AWS_Control_TowerSCP_기반_거버넌스_및_Datadog_SIEM_Cloudflare_보안.md" --gemini

# 모든 포스팅 분석
python3 scripts/improve_post_summary.py --all --gemini
```

### 수동 요약 개선

Gemini CLI를 직접 사용하여 요약을 개선할 수도 있습니다:

```bash
gemini "다음 기술 블로그 포스팅의 요약을 개선해주세요:

**제목**: 클라우드 시큐리티 과정 8기 5주차
**카테고리**: cloud
**태그**: AWS, Control-Tower, SCP

**현재 요약**:
[현재 요약 내용]

**개선 요청사항**:
1. 핵심 내용을 더 명확하고 구조화된 형식으로 정리
2. 기술적 키워드와 주요 개념을 강조
3. AI가 이해하기 쉬운 구조화된 형식 유지
4. 한글로 작성하되, 기술 용어는 영어 병기"
```

---

## 이미지 확인 및 생성

### 이미지 파일 확인

포스팅별 이미지 파일 존재 여부를 확인합니다:

```bash
# 최근 10개 포스팅 확인
python3 scripts/verify_images_unified.py --recent 10

# 이미지가 없는 포스팅만 표시
python3 scripts/verify_images_unified.py --missing

# 모든 포스팅 확인
python3 scripts/verify_images_unified.py --all

# Gemini CLI 명령어 생성
python3 scripts/verify_images_unified.py --recent 5 --generate-commands
```

### 이미지 생성 가이드

각 포스팅에 맞는 이미지를 생성하기 위한 Gemini CLI 명령어는 `GEMINI_IMAGE_GUIDE.md` 파일을 참조하세요.

#### 기본 이미지 생성 명령어 형식

```bash
gemini "Create a nano banana style [이미지 타입] for: [포스팅 제목]
Style: minimalist, clean lines, professional tech illustration
Colors: [색상 팔레트]
Layout: [레이아웃 타입]
Include: Korean labels ([한글 라벨])"
```

#### 예시: AWS 아키텍처 다이어그램

```bash
gemini "Create a nano banana style AWS Control Tower governance architecture showing: Management Account at the top (crown icon), Multiple Organizational Units (OU) branching down, Service Control Policies (SCP) as policy documents attached to OUs, Member accounts with different compliance levels, Guardrails and compliance checks as protective shields. Style: minimalist organizational chart style. Colors: AWS orange (#FF9900), Blue for accounts, Green for compliance. Layout: hierarchical tree structure from top to bottom. Include: Korean labels (관리 계정, 조직 단위, SCP 정책, 멤버 계정)."
```

#### 예시: 인시던트 타임라인

```bash
gemini "Create a nano banana style incident timeline showing: Timeline from left to right, Key events marked with icons (alert, investigation, response, recovery), Color coding: Red for incident start, Orange for investigation, Yellow for response, Green for recovery, Duration indicators showing time spent in each phase. Style: minimalist timeline illustration. Colors: Red (#CC0000), Orange (#FF6600), Yellow (#FFCC00), Green (#00AA44). Layout: horizontal timeline. Include: Korean labels (인지, 조사, 대응, 복구)."
```

---

## 스크립트 사용법

### 1. `improve_post_summary.py`

포스팅 요약 개선 및 이미지 확인 스크립트

**옵션:**
- `post`: 분석할 포스팅 파일명 (선택사항)
- `--all`: 모든 포스팅 분석
- `--gemini`: Gemini CLI를 사용하여 요약 개선
- `--recent N`: 최근 N개 포스팅만 분석 (기본값: 5)

**예시:**
```bash
# 최근 5개 포스팅 분석
python3 scripts/improve_post_summary.py --recent 5

# 특정 포스팅 요약 개선
python3 scripts/improve_post_summary.py "2025-12-24-포스팅명.md" --gemini

# 모든 포스팅 분석 및 요약 개선
python3 scripts/improve_post_summary.py --all --gemini
```

### 2. `verify_images_unified.py`

통합 이미지 파일 확인 및 Gemini CLI 명령어 생성 스크립트

**옵션:**
- `--all`: 모든 포스팅 확인
- `--missing`: 이미지가 없는 포스팅만 표시
- `--recent N`: 최근 N개 포스팅만 확인 (기본값: 10)
- `--generate-commands`: Gemini CLI 명령어 생성

**예시:**
```bash
# 최근 10개 포스팅 이미지 확인
python3 scripts/verify_images_unified.py --recent 10

# 이미지가 없는 포스팅 확인 및 명령어 생성
python3 scripts/verify_images_unified.py --missing --generate-commands
```

---

## 워크플로우

### 1. 새 포스팅 작성 후

```bash
# 1. 최신 포스팅 이미지 확인
python3 scripts/verify_images_unified.py --recent 1

# 2. 이미지가 없으면 생성
# GEMINI_IMAGE_GUIDE.md의 가이드를 참조하여 Gemini CLI로 이미지 생성

# 3. 요약 개선
python3 scripts/improve_post_summary.py "새포스팅.md" --gemini
```

### 2. 기존 포스팅 개선

```bash
# 1. 모든 포스팅 분석
python3 scripts/improve_post_summary.py --all

# 2. 이미지가 없는 포스팅 확인
python3 scripts/verify_images_unified.py --missing --generate-commands

# 3. 요약이 부족한 포스팅 개선
python3 scripts/improve_post_summary.py --all --gemini
```

### 3. 정기적인 점검

```bash
# 주간 점검 스크립트
python3 scripts/verify_images_unified.py --all > image_report.txt
python3 scripts/improve_post_summary.py --all > summary_report.txt
```

---

## 참고 자료

- [Gemini CLI 공식 문서](https://github.com/google-gemini/gemini-cli)
- [GEMINI_IMAGE_GUIDE.md](./GEMINI_IMAGE_GUIDE.md) - 이미지 생성 가이드
- [POST_VISUALIZATION_CHECKLIST.md](./POST_VISUALIZATION_CHECKLIST.md) - 포스팅별 시각화 체크리스트

---

## 문제 해결

### Gemini CLI를 찾을 수 없음

```bash
# 설치 확인
which gemini

# 재설치
npm install -g @google/gemini-cli
```

### API 키 오류

```bash
# 환경 변수 확인
echo $GEMINI_API_KEY

# 설정 파일 확인
cat ~/.gemini/config.json
```

### 타임아웃 오류

Gemini CLI 요청이 타임아웃되는 경우, 네트워크 연결을 확인하거나 요청 내용을 간소화하세요.

---

**마지막 업데이트**: 2025-12-24
