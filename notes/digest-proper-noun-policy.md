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
| 안드로이드 | Android |
| 텔레그램 | Telegram |
| 메타 | Meta |
| 시스코 | Cisco |

> allow-list는 **deny-by-default**: 목록에 없는 한글 토큰은 절대 자동 치환/플래그하지 않는다 (`l20_topic_tag_entity_guard`의 entity 오매칭 교훈). 신규 엔티티는 데이터로 혼용 ≥ 임계치 확인 + **substring 트랩 검증** 후 목록에 추가.

### allow-list 확장 조사 (2026-07-29, post-researcher 실측)

corpus 실측 결과 안드로이드(6건 혼용)·텔레그램(2건)만 안전 추가. **substring 트랩이 raw
count를 부풀리므로 반드시 word-boundary 실측 필요** (naive grep 금지):

| 후보 | 판정 | 근거 |
|------|------|------|
| 안드로이드→Android, 텔레그램→Telegram | **ADD** | 진짜 혼용 + 독립 토큰(충돌 없음) |
| 애플→Apple | **REJECT** | raw 최다지만 ~0 genuine — 애플리케이션(application)이 94/96 파일 지배 |
| 리플→Ripple | **REJECT** | 100% 리플래시(reflash)/리플리카(replica) 노이즈, genuine 0 |
| 네이버, 카카오 | **REJECT** | 국내 브랜드, 영문 표기 자체가 corpus에 없음(혼용 없음) |
| OpenAI·Nvidia·TensorFlow·Ubuntu·RedHat·Discord | **REJECT** | 이미 100% 영문 canonical, 고칠 결함 없음 |
| 메타→Meta | ~~DEFER~~ → **ADD (2026-07-30)** | 아래 재측정 참조 — 예외 불요 |
| 윈도우→Windows | **DEFER (확정)** | "컨텍스트/안정화 윈도우"(window) **동음이의어** — 아래 재측정 참조 |
| 시스코→Cisco | ~~DEFER~~ → **ADD (2026-07-30)** | 아래 재측정 참조 — 예외 불요 |
| 솔라나·크롬·삼성·파이어폭스 | **DEFER** | 혼용 0~1, 신호 부족 |

### DEFER 재측정 (2026-07-30, 실제 가드 매처로 검증) — 메타·시스코 ADD, 윈도우 확정 DEFER

**결정적 발견:** 위 DEFER 근거는 **naive substring count** 기반이었으나, 가드의 실제
매처 `_ENTITY_RE` = `(?<![가-힣A-Za-z0-9]){ko}(?=$|[^가-힣]|josa)` 는 word-boundary +
josa 룩어헤드라 **접미 복합어·임베디드 substring을 이미 제외**한다. 디제스트 코퍼스에서
매처를 시뮬레이션한 결과:

| 후보 | 매처 hits | genuine | 노이즈 누출 | 결정 |
|------|----------:|--------:|-----------:|------|
| 메타→Meta | 21 | 21 (메타의 광고·메타가 크리에이터·메타의 파이썬) | 0 (메타데이터/버스/분석/문자 = 메타+Hangul-non-josa → 룩어헤드가 이미 제외) | **ADD, 예외 불요** |
| 시스코→Cisco | 2 | 2 (시스코가 분기·Unified) | 0 (샌프란시스코 = 임베디드 → 룩비하인드가 이미 제외) | **ADD, 예외 불요** |
| 윈도우→Windows | 29 | ~10 (Parallels/Defender/사내) | ~19 (컨텍스트 윈도우 등) | **DEFER 확정** |

**윈도우 확정 DEFER 근거:** window 어의(뜻)는 **선행 수식어**(컨텍스트/안정화/슬라이딩/
익스플로잇/유지보수 기간/블록 N)에 실리므로 룩어헤드로 못 잡는다. deny-prefix
negative-lookbehind를 설계·실측했으나 개재 토큰(숫자·괄호: "블록 961632 윈도우",
"유지보수 기간(윈도우)")이 prefix 앵커를 무력화해 **KEPT 12건 중 3건(~25%) FP** 잔존.
deny-by-default·no-FP 원칙상 자동 canonical화 불가 → genuine Windows 혼용은 per-post 수동.

구현: `ENTITIES`에 `메타/시스코` 추가 + 회귀 테스트 4건(josa canonical·복합어 불변·
샌프란시스코 불변·윈도우 미포함). 예외 코드는 추가하지 않음(기존 매처로 충분).

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

## 4. 롤아웃 (레거시 194개 분리) — 진행 현황

1. **Phase 1 — 코드 + 가드 (신규 강제):** ✅ **완료 (PR #472)**. `check_digest_proper_nouns.py`
   + 테스트 29 + pre-commit(9c)/svg-lint CI/blogwatcher `--fix` wiring. 신규 digest canonical 보장.
2. **Phase 2a — 구조-clean 레거시 37개:** ✅ **완료 (PR #473)**, 742→해당분 치환, 오변환 0, 게이트 전부 green.
3. **Phase 2b — 구조-defective 98개: ⏸ deferred (전용 캠페인 권장).**
   - **발견(empirical):** `--fix --all`은 135개를 바꾸지만 그 중 **98개는 pre-existing 구조 결함**
     (넘버링/H1/체크리스트, 레거시 176개 미백필)이 있어, staging 시 digest **구조 게이트**(pre-commit
     step 9 + svg-lint `--changed`)가 red가 된다. proper-noun 스왑 자체는 구조와 무관(증명: 실패
     파일 diff는 `비트코인→Bitcoin` 단일 스왑)이지만 게이트가 함께 스캔.
   - **순서 의존:** 98개는 **구조 백필 먼저 → proper-noun 백필** 순서 필요.
   - **실현성 파일럿(2026-07-29):** 구조 백필은 단순 정규화가 아니다.
     (a) 위반 대부분이 "실무 체크리스트 found 0"(누락) → `backfill_digest_native_sections.py`로
     본문 근거 기반 **섹션 생성** 필요(결정적이나 콘텐츠 생성). (b) `backfill_digest_structure.py`
     dry-run이 레거시 뉴스 헤딩(`## 1. AISLE AI…`, `## 2. CVE…`)을 "whitelist에 없는 헤딩"으로
     경고 → 98개가 **이질적 구조**라 정규화기가 clean 처리 못 함.
   - **권장:** 이질적 98개 공개 포스트의 구조 백필+콘텐츠 생성은 슬롭/파손 위험이 커 **단일 세션
     blast 금지**. 소스 파티션(발행 연월/구조 유형별) 전용 캠페인으로 per-post 검증하며 스테이지드
     진행(ultragoal/autopilot). Bitcoin 혼용 상당수가 이 98개에 잔존.
4. **측정:** Phase 2b 완료 후 §1 표 재측정 → 혼용 0 목표.

### Phase 2 부수 발견 (2026-07-29)
- 마스킹 정교화: 뉴스카드 `title=`/`summary=` 속성값은 인용 제목이 **아님** → canonical 대상
  (`(?<!=)` 규칙). 안 그러면 산문은 Bitcoin, 카드는 비트코인으로 **문서 내 불일치**.
- 마크다운 링크/표의 인용 기사 제목(9건)도 canonical화됨 — owner "전부 영문" 정책에 부합해 as-is 수용.
- 크론 발행 digest가 main 코퍼스 테스트를 깨는 패턴 재확인(07-29 "Claude AI" lone-adjective 커버
  가드 → `_DEFERRED_AI_ADJECTIVES`에 claude vet, PR #474). baseline stale(#471)과 동류.

---

## 5. 리스크 / 미해결

- **인용 제목 오탐**: 한글 기사 제목에 "구글" 등이 있으면 canonical 치환하면 안 됨 → 인용 마스킹이 방어선. 테스트로 강제.
- **Amazon vs AWS**: "아마존"이 서비스(AWS)인지 회사인지 문맥 의존 → 초기엔 회사=Amazon, 인프라 문맥은 수동 리뷰(allow-list에서 아마존→Amazon만, AWS 승격은 --fix 대상 외).
- **부분 로안워드**: "쿠버네티스 클러스터" → "Kubernetes 클러스터"(혼합)가 자연스러운지 vs 전체 영문. 정책상 고유명사 토큰만 치환, 뒤 일반명사는 보존.
- Phase 2 백필은 owner 승인 후 별도 진행 (이 문서는 Phase 1 설계까지 확정).
