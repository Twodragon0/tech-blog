# CI/Workflow 보안 하드닝 회고 (2026-06-29 → 2026-07-06)

`.github/workflows/` CI 파이프라인 보안 감사와 후속 조치의 회고. 발견 → 수정 →
회귀 가드까지의 한 사이클을 기록한다. (GSC 색인 회복률 측정은 별도 — 아래 "보류" 참조.)

## 배경

무인(cron) 자동 발행 파이프라인(blogwatcher / daily-news / generate-images)이
`repository_dispatch` 외부 페이로드를 받고 `contents:write` 토큰으로 main에 커밋하는
구조라, CI 표면이 공급망/PPE(Poisoned Pipeline Execution) 관점에서 가장 민감한 자산.
2026-07-01 security-review로 시작해 severity 클러스터별로 조치했다.

## 발견 및 조치 (severity별)

| ID | 유형 | 파일 | 조치 | 커밋 |
|----|------|------|------|------|
| MEDIUM-1 | blogwatcher 외부 payload SSRF/피드 오염 → main 자동 push | `normalize_blogwatcher_payload.py`, `ai-blogwatcher.yml` | scheme/host allowlist + 사설IP(169.254.169.254 메타데이터)·리다이렉트 차단, 외부 payload는 리뷰 PR 게이트 | `23ce90cb` |
| MEDIUM-2 | `ai-ops-on-demand.yml` job-level 시크릿 과다 노출 | 동 워크플로 | 시크릿을 step-level로 범위화 | `dd0fc74e` |
| MEDIUM-3(클러스터) | sentry 토큰 prefix 로그 + job-level 시크릿 | sentry-release/healthcheck, vercel-firewall-backup | echo 제거 + 최소 노출 | `e0084adc` |
| LOW-5 | GSC 서비스계정 JSON 키 장기 미회전 | (신규) `docs/setup/GSC_SERVICE_ACCOUNT_ROTATION.md` | 90일 회전 런북(무중단, 최소권한 유지) | `d1c399e3` |
| LOW(timeout) | 40개 잡 중 8개 `timeout-minutes` 미선언 → 러너 6h 상한 점유 | 8개 워크플로 | 잡별 timeout 추가(40/40 커버) | `78724989` |

## 회귀 가드 (재발 방지 = 핵심 산출물)

발견을 고치는 것보다 **조용한 재약화(silent weakening)를 pytest에서 loud FAIL로**
만드는 게 더 중요. 브랜치 보호는 이런 회귀를 못 본다. `scripts/tests/test_ci_*.py`:

| 가드 | 불변식 | 커밋 |
|------|--------|------|
| `test_ci_no_run_input_interpolation_guard` | `run:`/`github-script`에 untrusted context 직접 보간 금지(env 경유) | `bb0749f8`/`8c00ac03` |
| `test_ci_workflow_hardening_guard` | G2 top-level `permissions:` 필수 + write-all 금지 / G3 `pull_request_target`+head checkout 금지 / G4 action `with:` 인젝션 / **timeout-minutes 전 잡 선언** | `8c00ac03`, `d1c399e3`, `b44f21d6` |
| `test_ci_dependabot_gate_guard` | dependabot auto-merge는 green CI 게이트 | `06ea3f8a` |
| `test_ci_honesty_gate_guard` / `test_ci_digest_kpi_gate_guard` | 커버 honesty·KPI 게이트 blocking 유지 | — |
| `test_check_workflow_action_pins` | 모든 `uses:` SHA 핀(플로팅 태그 금지) | `b8f49e7a` |

## fresh 스윕 결과 (2026-07-05)

MEDIUM/guard 전부 수정 후, LOW 백로그가 실재하는지 fresh security-reviewer 스윕:
- **정직한 결론: "LOW 3건" 백로그는 실재하지 않음** — 이전 제안의 추정치였다.
  실제 material LOW는 timeout 누락 **1건**뿐이었고 즉시 조치.
- clean 검증: 40개 잡 전부 SHA 핀 / top-level permissions / env-경유 인젝션 가드 /
  SSRF allowlist+리다이렉트 거부 / 시크릿 로그·아티팩트 미노출 / `curl|bash` 없음.

## 배운 것

1. **가드가 진짜 산출물.** 수정은 1회성, 가드는 영속. 각 발견마다 "이걸 조용히
   되돌리면 무엇이 깨지나?"를 물어 test로 고정 (`ci-config-guard` 스킬 패턴).
2. **가드는 non-vacuous 검증 필수.** 실파일 pass + 변형본에서 FAIL 둘 다 증명.
   (timeout 가드: lighthouse.yml temp 복사본에서 timeout 제거 → 정확히 지목하며 FAIL.)
3. **quota 채우려 finding 조작 금지.** "3건" 프레임에 맞춰 억지 LOW를 만들지 않고
   실제 1건만 보고 — 정직성 > 완결성 착시.
4. **reusable-workflow(`uses:`) 잡은 timeout 예외** — 호출된 워크플로 잡에 timeout이
   있으므로 가드에서 제외.

## 2026-07-06 추가 감사 (blogwatcher untrusted 경로 심화)

07-01 감사의 MEDIUM-1(SSRF allowlist + PR 격리)은 **트러스트 경계**를 세웠지만,
그 경계 안에서 두 가지 잔여 노출이 남아 있었다. fresh blogwatcher 보안 감사로 발견.
(주의: 아래 "MED-1/MED-2"는 07-06 감사의 자체 넘버링이며, 위 표의 MEDIUM-1
[07-01 SSRF allowlist, `23ce90cb`]과는 별개 항목이다.)

| ID (07-06) | 유형 | 근본원인 | 조치 | 커밋 |
|----|------|----------|------|------|
| MED-1 | untrusted 경로에 LLM 시크릿 라이브 | `repository_dispatch`는 PR로 격리되나 **시크릿은 미격리**. job-level env(무조건) + step-level(USE_AI 기본 `auto`가 전부 un-gate)로 GEMINI/CLAUDE/OPENAI/DEEPSEEK 4키가 untrusted 경로에 노출 → 피드 포이즈닝이 라이브 키 도달 가능 | 8개 키 표현식(job+step) 전부에 `github.event_name != 'repository_dispatch'` 게이트 → untrusted 경로는 항상 `''`. trusted 경로 무영향(enrichment는 human review/merge 시) | `25b84541` |
| MED-2 | untrusted URL fetch fail-**open** | `BLOGWATCHER_ALLOWED_HOSTS` 미설정 시 `validate_fetch_url`(env 경로)이 host allowlist를 건너뛰어 **모든 public 호스트 허용**. payload URL은 untrusted client_payload에서만 유래하는데 미구성이 조용히 any-host 허용 = allowlist inert | env 경로(`allowed_hosts=None`) + allowlist 비어 있으면 **거부(fail-closed)**. 명시적 리스트 호출자(신뢰/테스트)는 기존 permissive 의미 유지 | `d0e6ad6a` |

### 회귀 가드 (07-06)

| 가드 | 불변식 | 커밋 |
|------|--------|------|
| `test_ci_blogwatcher_secret_partition_guard` | 모든 `*_API_KEY: secrets.*` 표현식이 `event_name != 'repository_dispatch'` 게이트 포함. 주석-스트립으로 prose 오매칭 방지, non-vacuous(게이트 1개 제거 시 FAIL) | `25b84541` |
| `TestFailClosedAllowlist` (`test_blogwatcher_ssrf.py`) | env 미설정/공백 → 거부, env 설정 시 매칭 허용·타호스트 거부, **명시적 `[]`는 permissive 계약 유지**(회귀 가드) | `d0e6ad6a` |

### Non-breaking 근거 (MED-2)

- 실제 워크플로 배선은 `--payload-json`(항상 `toJson(client_payload)`로 truthy)이
  `--payload-url`보다 `_load_payload`에서 우선 → **URL fetch 경로 도달 불가**.
  fail-closed는 잠재 가드(defense-in-depth)이며 프로덕션 발행 경로에 영향 없음.
- 경험적 확인: payload_json+payload_url 동시 설정 시 payload_json 분기 반환 /
  URL-only + allowlist 미설정 시에만 신규 거부 발동. 18 tests pass(SSRF 15 + 파티션 3).
- `BLOGWATCHER_ALLOWED_HOSTS`는 **미설정을 안전 기본값**으로 유지(URL fetch 비활성).
  향후 URL fetch 필요 시 워크플로 env에 신뢰 호스트만 추가.

### 배운 것 (07-06)

5. **트러스트 경계 ≠ 시크릿 경계.** PR 격리(MED-1의 07-01 조치)는 `main`을 보호하지만
   러너 안의 시크릿·네트워크 표면은 별개로 격리해야 한다. "격리했다"에서 멈추지 말고
   *무엇을* 격리했는지 물을 것.
6. **미구성 = fail-open은 조용한 취약점.** allowlist가 "선택적"이면 미설정 배포에서
   inert가 된다. 신뢰 경계 밖 입력을 다루는 게이트는 미구성 시 fail-closed가 기본.

## 보류: GSC 색인 회복률 측정

- 예정일 **2026-07-08** (checkpoint DUE). 오늘(07-05)은 미도래.
- GSC 수치는 서비스계정 크레덴셜 필요 → **사용자/CI 크레덴셜 제공 시점에 측정 가능**.
- 측정 명령: `scripts/gsc_checkpoint.py` (메모리 `checkpoint_gsc_2026_07_08` 참조).
- 07-08 도래 + 크레덴셜 확보 시: 07-01/03 SEO+보안 윈도우의 7일 색인 회복 기록.
