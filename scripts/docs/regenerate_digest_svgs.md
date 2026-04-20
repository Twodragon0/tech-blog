# regenerate_digest_svgs.py 사용 가이드

Weekly Digest 커버 SVG 및 파생 이미지(og.webp, og.avif, card.webp, card.avif)를 재생성하는 스크립트입니다.
외부 API 호출 없이 오프라인으로 동작하며, Phase A(2026-04-09..2026-04-19)와 Phase B(2026-03-08..2026-04-05) 두 웨이브를 모두 지원합니다.

관련 PR: [PR #262 (Phase A)](https://github.com/Twodragon0/tech-blog/pull/262) | [PR #263 (Phase B)](https://github.com/Twodragon0/tech-blog/pull/263)

---

## 빠른 시작

```bash
# 1. Cairo 라이브러리 경로 설정 (macOS Homebrew 필수)
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/cairo/lib

# 2. 전체 Phase 재생성 (기본값)
python3 scripts/regenerate_digest_svgs.py

# 3. Phase A만 재생성
python3 scripts/regenerate_digest_svgs.py --phase a

# 4. Phase B만 재생성
python3 scripts/regenerate_digest_svgs.py --phase b
```

---

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--phase {a,b,all}` | 재생성할 웨이브 선택 | `all` |
| `--skip-derivatives` | SVG만 출력, 래스터 파생물 생략 | `False` |

---

## 산출물 구조

스크립트 실행 후 각 포스트 basename에 대해 다음 파일이 생성됩니다:

```
assets/images/
  {basename}.svg          # 1200x630 소스 SVG (navy-indigo 3-카드 레이아웃)
  {basename}_og.webp      # Open Graph 이미지 (1200x630, quality 88)
  {basename}_og.avif      # Open Graph 이미지 (1200x630, quality 72)
  {basename}_card.webp    # Twitter 카드 이미지 (525x275, quality 88)
  {basename}_card.avif    # Twitter 카드 이미지 (525x275, quality 72)
```

임시 파일(`_og.png`, `_card.png`)은 변환 후 자동 삭제됩니다.

---

## 사용 예시

### 예시 1: Phase A 전체 재실행 (PR #262 산출물 복원)

```bash
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/cairo/lib
python3 scripts/regenerate_digest_svgs.py --phase a
```

2026-04-09부터 2026-04-18까지 10개 포스트의 SVG 및 파생 이미지를 재생성합니다.
레퍼런스 파일(`2026-04-19-..._Botnet.svg`)의 SVG 소스는 덮어쓰지 않으며, 파생물만 재생성합니다.

### 예시 2: Phase B 전체 재실행 (PR #263 산출물 복원)

```bash
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/cairo/lib
python3 scripts/regenerate_digest_svgs.py --phase b
```

2026-03-08부터 2026-04-05까지 29개 포스트(월간 인덱스 포함)를 처리합니다.

### 예시 3: SVG만 빠르게 확인 (래스터 변환 생략)

```bash
python3 scripts/regenerate_digest_svgs.py --phase a --skip-derivatives
```

cairosvg/Pillow 없이도 SVG 텍스트 유효성 검사와 파일 출력이 가능합니다.
CI 환경이나 텍스트 수정 확인 시 유용합니다.

---

## 주의 사항

### SVG 텍스트 규칙 (프로젝트 정책)

스크립트 내부 검증기가 다음을 거부합니다:

- **한국어 문자** (가-힣 범위): 카드 필드(label, headline, tag, desc)에 한글 입력 불가
- **특수 문자**: `·` `•` `—` `"` `"` `'` `'` 사용 불가

위반 시 `ValueError`가 발생하며 파일이 기록되지 않습니다.

### 파일 덮어쓰기

`assets/images/` 내 기존 SVG 및 파생 이미지는 **경고 없이 덮어씁니다**.
실수로 실행한 경우 `git checkout -- assets/images/` 로 복원하세요.

### 레퍼런스 파일 보존

`2026-04-19-Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet.svg`는 시각적 스타일 앵커입니다.
이 파일의 SVG 소스는 Phase A/B 어느 실행에서도 덮어쓰지 않습니다. 파생물(og/card)만 재생성됩니다.

### Pre-commit 훅

`scripts/regenerate_digest_svgs.py` 또는 `scripts/tests/` 변경 시 pre-commit 훅이 자동으로 `pytest scripts/tests/`를 실행합니다.
커밋 전 테스트 통과를 확인하세요.

### API 키 불필요

이 스크립트는 외부 API를 호출하지 않습니다. 모든 카드 데이터는 소스 코드 내 상수로 정의되어 있습니다.

---

## 의존성

| 라이브러리 | 용도 | 설치 |
|-----------|------|------|
| `cairosvg` | SVG → PNG 변환 | `pip install cairosvg` |
| `Pillow` | PNG → WebP/AVIF 변환 | `pip install Pillow` |
| Cairo (시스템) | cairosvg 백엔드 | `brew install cairo` |

`--skip-derivatives` 사용 시 cairosvg/Pillow 없이도 SVG 출력만 가능합니다.

---

## Deprecated 파일

`scripts/regenerate_phase_a_svgs.py`는 Phase A 전용 원본 스크립트로, 현재 2-line shim으로 교체되었습니다.
git blame/history 보존을 위해 파일은 유지되지만, 실제 로직은 모두 이 파일로 이전되었습니다.

```python
# regenerate_phase_a_svgs.py 현재 내용 (shim)
from scripts.regenerate_digest_svgs import *  # noqa: F401,F403
```

Phase A 재생성이 필요하면 항상 `regenerate_digest_svgs.py --phase a`를 사용하세요.
