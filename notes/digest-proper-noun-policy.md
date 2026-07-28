# Digest 고유명사 표기 정책 + 자동 가드 설계

**Status:** 설계 확정 (2026-07-28) · 구현 대기
**Decision owner:** 블로그 owner (편집 보이스 결정: **전부 영문 통일**)
**관련:** 재발 방지 A(#469 탐지 게이트) / B(#470 재번역 워크플로), memory `l20_topic_tag_entity_guard`, `digest_native_sections_backfill`, `digest_structural_normalization`, `feedback_cover_empirical_first`

---

## 1. 문제 (empirical)

194개 digest 포스트에서 동일 엔티티가 한글/영문 양쪽으로 표기되는 실태 계량 (2026-07-28 측정):

| 엔티티 | 한글 파일 | 영문 파일 | **같은 파일 내 혼용** |
|--------|----------:|----------:|----------------------:|
| Bitcoin (비트코인) | 129 | 133 | **112** ← 최대 결함 |
| Kubernetes (쿠버네티스) | 22 | 95 | 15 |
| Microsoft (마이크로소프트) | 10 | 116 | 8 |
| Google (구글) | 9 | 150 | 8 |
| Linux (리눅스) | 13 | 46 | 8 |
| Ethereum (이더리움) | 8 | 9 | 4 |
| GitHub, Docker, Amazon/AWS, Cloudflare | ≤3 | 74~136 | ≤3 |

**핵심 defect = intra-document 혼용** (특히 Bitcoin 112건). 회사/제품/기술명은 이미 영문 압도적이라 사실상 표준이 존재하고, 실제 혼란은 암호화폐·OS 로안워드(비트코인·이더리움·리눅스·쿠버네티스)에 집중.

---

## 2. 정책 (canonical = 영문)

**규칙:** digest 본문의 고유명사(회사·제품·프로토콜·기술·암호화폐)는 **영문 정식 표기**를 canonical로 한다.

**예외 (한글/원문 보존 — 가드 대상 아님):**
1. **인용된 기사 제목** (`"..."`, `「...」`, `『...』` 안) — 원문 그대로.
2. **CVE ID·식별자** (`CVE-YYYY-NNNNN`), 버전 문자열, 코드블록/인라인 코드(`` ` ``), URL·경로.
3. **일반명사화된 한글어** (예: "블록체인", "클라우드", "컨테이너") — 고유명사가 아니므로 대상 외.
4. **front matter의 `title`/`excerpt`** 중 이미 한국어 카피로 확정된 것은 별도 정책(재번역 워크플로 B 소관). 이 가드는 **본문 고유명사**만 다룬다.

**canonical 매핑 (초기 allow-list, deny-by-default):**

| 한글 형태 | canonical 영문 |
|-----------|----------------|
| 비트코인 | Bitcoin |
| 이더리움 | Ethereum |
| 쿠버네티스 | Kubernetes |
| 리눅스 | Linux |
| 도커 | Docker |
| 구글 | Google |
| 마이크로소프트 | Microsoft |
| 아마존(웹서비스) | Amazon (AWS) |
| 깃허브 | GitHub |
| 클라우드플레어 | Cloudflare |

> allow-list는 **deny-by-default**: 목록에 없는 한글 토큰은 절대 자동 치환/플래그하지 않는다 (`l20_topic_tag_entity_guard`의 entity 오매칭 교훈). 신규 엔티티는 데이터로 혼용 ≥ 임계치 확인 후 목록에 추가.

---

## 3. 자동 가드 설계 (`scripts/check_digest_proper_nouns.py`)

**목적:** 신규 digest가 canonical(영문)에서 벗어나거나 한/영 혼용을 재도입하면 pre-commit + CI에서 실패.

**동작:**
1. 입력 파일마다 본문에서 §2 예외 영역(인용 제목·CVE·코드·URL·front matter)을 **먼저 마스킹**.
2. 남은 본문에서 allow-list의 **한글 형태 등장**을 검출.
   - `--check` (기본): 한글 형태 1건이라도 있으면 `MISSING`/`VIOLATION` 리포트 + exit 1.
   - `--fix`: 한글 형태 → canonical 영문 치환 (마스킹 영역은 불변).
3. **혼용 리포트**: 같은 파일에 canonical 영문과 한글 형태가 공존하면 최우선 플래그.

**스코프 (critical — `digest_structural_normalization`·`digest_native_sections_backfill` 교훈):**
- 가드는 **`--staged` / `--changed` 만** 대상. **NEVER `--all`** — 194개 레거시를 크론/pre-commit이 일괄 건드리면 안 됨.
- digest 판별은 `_is_digest_post` 필터 재사용 (파일명 `*Digest*`/`*Weekly*` + front matter 확인). 비-digest 포스트는 대상 외.

**Wiring:**
- pre-commit: 스테이징된 digest만 (기존 hook 체인에 step 추가, `githooks_hookspath_gotcha` 준수 — `.githooks/` 소스, `install-hooks.sh` 경유).
- CI (svg-lint 또는 신규 gate job): PR의 changed digest만.
- **blogwatcher 발행 경로**(`ai-blogwatcher.yml`): 발행 직전 `--fix`를 자동 적용해 신규 digest가 항상 canonical로 커밋되게 (재발 방지 A/B와 동일 계층).

**회귀 가드:** `scripts/tests/test_check_digest_proper_nouns.py` — 마스킹 정확성(인용 제목 오탐 금지), deny-by-default(목록 외 토큰 무시), --check/--fix 멱등성, digest-only 스코프.

---

## 4. 롤아웃 (레거시 194개 분리)

1. **Phase 1 — 코드 + 가드 (신규 강제):** 스크립트·테스트·wiring 머지. 이 시점부터 신규 digest는 canonical 보장. **레거시 미변경.**
2. **Phase 2 — 레거시 백필 (opt-in, 별도 PR):** `--fix`를 194개에 배치 적용하되 **소스 파티션**으로 리뷰 (Bitcoin 112건 혼용부터). 인용 제목 마스킹을 실제 포스트로 RUN 검증 후 (`feedback_cover_empirical_first`). honesty/커버에 영향 없음(본문 텍스트만).
3. **측정:** 백필 후 §1 표 재측정 → 혼용 0 확인.

---

## 5. 리스크 / 미해결

- **인용 제목 오탐**: 한글 기사 제목에 "구글" 등이 있으면 canonical 치환하면 안 됨 → 인용 마스킹이 방어선. 테스트로 강제.
- **Amazon vs AWS**: "아마존"이 서비스(AWS)인지 회사인지 문맥 의존 → 초기엔 회사=Amazon, 인프라 문맥은 수동 리뷰(allow-list에서 아마존→Amazon만, AWS 승격은 --fix 대상 외).
- **부분 로안워드**: "쿠버네티스 클러스터" → "Kubernetes 클러스터"(혼합)가 자연스러운지 vs 전체 영문. 정책상 고유명사 토큰만 치환, 뒤 일반명사는 보존.
- Phase 2 백필은 owner 승인 후 별도 진행 (이 문서는 Phase 1 설계까지 확정).
