# CI/Workflow 보안 하드닝 회고 (2026-06-29 → 2026-07-05)

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

## 보류: GSC 색인 회복률 측정

- 예정일 **2026-07-08** (checkpoint DUE). 오늘(07-05)은 미도래.
- GSC 수치는 서비스계정 크레덴셜 필요 → **사용자/CI 크레덴셜 제공 시점에 측정 가능**.
- 측정 명령: `scripts/gsc_checkpoint.py` (메모리 `checkpoint_gsc_2026_07_08` 참조).
- 07-08 도래 + 크레덴셜 확보 시: 07-01/03 SEO+보안 윈도우의 7일 색인 회복 기록.
