# CI 게이트 감사 회고 (2026-08-10 → 08-11)

"게이트가 존재한다"와 "게이트가 무언가를 막는다"는 다른 주장이라는 것을 실측으로 확인한
사이클. 발견 → 수정 → 회귀 가드까지 PR 10건(#529–#538)을 기록한다.

기존 회고([`ci-security-hardening-2026-07.md`](ci-security-hardening-2026-07.md))가 CI의
**보안 표면**을 다뤘다면, 이번은 **실효성**을 다룬다. 두 질문이 달랐다: "공격자가 이걸
악용할 수 있나" vs **"이게 한 번이라도 무언가를 막은 적이 있나"**.

## 배경 — 감사를 촉발한 관찰

폰트 작업(#528) 중 `font-drift` 게이트가 실제로 돌아 통과하는 것을 보고, 반대 질문이 나왔다:
**돌지 않는 게이트는 몇 개인가?** 최근 30 PR(#494–#528, 49커밋 768 run record)을 실측했다.

| 구분 | 결과 |
|---|---|
| 체크 이름 총수 | 21 |
| **실제 차단 이력 있음** | **5** — `CodeQL`, `build`, `lighthouse`, `lighthouse-perf-gate`, `mermaid-csp-render` |
| 30 PR 중 0회 등장 | `check-svg`, `visual-regression` |
| 100% skipped | `npm/Ruby Security Audit`(설계상 정상), `auto-merge` |
| 실패 이력 0 (유의미) | **`lint`** — 19 PR / 45 record |

그리고 `main`에 `required_status_checks`가 없고 `rulesets`도 `[]`이라 **21개 체크 전부
권고**다. 이는 오설정이 아니라 봇 직push와의 양립 제약([`branch_protection_bot_token`
메모](../CLAUDE.md) 참조 — 2026-06-30 분석)이지만, 그 결정 이후 게이트가 계속 늘어난 만큼
전제를 다시 확인할 가치가 있었다.

## 근본 원인 — 크론 봇 push의 이중 회피

이번 감사에서 가장 값진 한 줄이다.

커버 SVG의 실제 생산자는 사람이 아니다:

```
git log --format='%an' -40 -- 'assets/images/*.svg'
  35  github-actions[bot]      ← main 직접 push
   5  Twodragon
```

봇 push는 두 겹으로 트리거를 빠져나간다 — (1) PR이 없어 `pull_request` 미발동, (2)
`GITHUB_TOKEN` push는 다른 워크플로를 트리거하지 않음(GitHub 재귀 방지). 봇 커버 커밋
`685ca468`에 붙은 실행 12건이 **전부 `schedule`**, push/PR 이벤트 0건으로 실증됐다.

이 레포는 같은 문제를 `deploy-pages.yml`에서 이미 겪고 cron으로 우회했는데(2026-07-06),
그 해법이 다른 곳에는 적용되지 않았다.

## 조치 (PR별)

| PR | 조치 | 근거 |
|----|------|------|
| #529 | `svg-lint.yml`에 schedule 추가, `check-svg` 트리거 `*.svg`→`**.svg` | `--all` 게이트 15개가 봇 산출물을 전혀 못 봄. depth-1 307 / 전체 463 → **156개가 스캔 안·트리거 밖** |
| #530 | silent-pass 5건 fail-closed (D1·D2·D3·D5·D18) | 아래 "기각/재해석" 참조 |
| #531 | 발이 묶인 재번역 2파일 반영 | 3브랜치 중 2개가 같은 제목을 **다르게** 번역(LLM 비결정성) |
| #532 | security-audit 이슈 자가치유 reconcile, backfill `exit 1`→추적 이슈 | 스테일 이슈가 유일한 신호 채널을 침묵시킴 |
| #533 | `svg_visual_baseline.py --verify` 배선 | refresh가 자동 커밋하므로 verify 없이는 generator 변경이 "새 정답"으로 기록됨 |
| #534 | `jekyll.yml` 연성 4곳 (D7–D11) | 60점 하한이 2중 무력화, 1000자 한도는 261/261 위반 |
| #535 | 시크릿 부재를 "실제로 있는 시크릿"에서만 fail-closed | `gh secret list` 대조로 7개 묶음이 둘로 갈림 |
| #536 | 영구 no-op cron 2개 폐기 | 시크릿 미설정으로 매일/매주 green + 무작업 |
| #537 | proper-noun 자가치유에 재검증 추가 | 네 자가치유 중 유일하게 없던 곳 |
| #538 | 베이스라인 표본을 트리거와 일치, 고아 PNG 27개 정리 | #533에서 **내가 들인** trigger⊃scan 불일치 |

## 실측이 전제를 바꾼 사례 — 기각과 재해석

이번 감사에서 가장 재사용 가치가 높은 부분이다. 요청받은 수정 중 **5건이 실측 후 달라졌다.**

### 기각 1 — `visual-regression.yml`에 schedule 추가 (효과 없음)

`run.py`의 `collect_files()`가 `date in ALL_TARGET_DATES`로 필터링하는 **하드코딩 1~3월 날짜
집합**이다. schedule을 붙이면 변하지 않는 파일 30개를 매일 재검사하는 소음일 뿐이다.

이 레포에는 **범위 동결 시스템이 셋** 있었다: `run.py`(하드코딩 날짜),
`svg_visual_baseline.py`(하드코딩 `TARGET_SVGS`), `check-svg` 트리거(depth-1 glob vs rglob).

### 기각 2 — D1을 "교집합 공집합 시 fail"로 (설계 의도 위반)

`lighthouse-ci.yml` 헤더 36-40행이 `"a soft degrade, by design"`이라 명시하고 보안 수정
C-H1(2026-06-30)에 귀속돼 있다. Vercel 차단이 PR을 인질로 잡지 않게 하려는 것이다.

**대신 고친 것:** 빈 비교를 항상 `::warning::`으로 알리고, **양쪽 빌드가 성공했을 때만**
`--require-comparable`로 실패시킨다 — 그때의 공집합은 degrade가 아니라 URL 해석 결함이다.

### 재해석 1 — D5 "skipped를 clean으로 보지 않기" ≠ skipped→fail

두 감사는 `package.json`/`Gemfile` 계열이 바뀔 때만 도는 게 **맞는 설계**다. skipped를
실패시키면 모든 일반 PR이 red가 된다. 커버리지는 월요일 cron이 담당한다(schedule 실행 25회
확인). → skipped는 통과시키되 **표기를 `NOT RUN`**으로, `success`/`skipped` 외 결론은
allow-list로 실패.

### 재해석 2 — D9 "1000자 한도 fail-closed" (100%가 위반)

```
_posts 261개 중 1000자 초과: 261개 (100%) | 최대 2749자
```
**100%가 위반하는 임계값은 게이트가 아니라 소음**이고, 경고 무시를 학습시킨다. →
`check_front_matter_growth.py`(래칫 + 3000자 cap)로 재설계. 레거시는 grandfathered,
새 증가만 실패.

### 재해석 3 — "시크릿 부재 7개 워크플로 일괄 fail-closed" (절반은 영구 red)

`gh secret list` 대조:

| 시크릿 상태 | 워크플로 | 조치 |
|---|---|---|
| 설정됨 (`SLACK_BOT_TOKEN` 등) | slack ×2, googlebot-monitor | **fail-closed** — 부재는 회귀 |
| 한 번도 없음 (`GSC_SERVICE_ACCOUNT_JSON`, `VERCEL_TOKEN`) | gsc-queue-refresh, vercel-firewall-backup | **cron 폐기** — fail-closed면 영구 red |

### 켤 수 있었던 것 — D8 60점 하한

`validate_post_quality.py`의 `--fail-below` **기본값이 60**이라 하한은 원래 있었는데
`continue-on-error` + `|| true`로 2중 무력화돼 pre-commit(=`--no-verify` 우회 가능)에만
살아 있었다. 실측 261개 **최저 80 / 평균 90.6 / 60미만 0** → 20점 여유로 켰다.

## 감사에 없던 추가 발견

에이전트 보고를 검증하는 과정에서 나온 것들.

1. **`vercel-firewall-backup`이 존재 이유를 한 번도 수행하지 않았다.** 무단 Vercel 대시보드
   편집을 커밋된 diff로 남기는 게 목적인데(2026-05-08 사건), 매주 성공을 보고하면서 스냅샷을
   한 번도 만들지 않았다. **그 green이 곧 그 워크플로가 닫으려던 감사 공백이었다.**
2. **quote gate의 `|| true`가 프로세스 치환 안에 있었다.** `mapfile -t CHANGED < <(git diff … || true)`
   — `<(...)` 안의 실패는 `mapfile`이 종료 코드를 **볼 수조차 없다**.
3. **`security-audit`의 스테일 이슈가 신호를 완전히 침묵시켰다.** `|| true`로 잡은 항상 green,
   유일한 신호인 이슈는 dedup이 "열린 이슈 있으면 생성 안 함"인데 close가 없었다. #414·#415가
   2026-06-15부터 열려 있는데 `npm audit`은 현재 0건 → **다음 실제 취약점은 green + 무통보.**
4. **`Number('')는 0`** — 빈 `VULNS`를 "발견 0"으로 읽어 살아있는 이슈를 잘못 닫을 수 있었다.
5. **경로 필터된 체크는 required로 지정할 수 없다** — 미실행 시 PR이 영구 pending. 지금 걸 수
   있는 실질 게이트는 `build` 하나뿐(30/30 실행).
6. **`can_approve_pull_request_reviews`는 PR 생성과 승인을 한 토글로 묶는다** — 향후 리뷰필수
   도입 시 자기승인 우회로가 된다. "설정 토글"과 "GitHub App"은 보안 등가가 아니다.

## 방법론 — 반복해서 통한 것과 걸린 것

### 통한 것: 가드를 뮤테이션으로 자기검증

이 감사의 주제가 "안 돌던 게이트는 검증된 적 없다"였으므로, **새로 만든 가드를 그냥 믿지
않았다.** 각 수정을 되돌려 실제로 잡히는지 확인했다 — 누적 **뮤테이션 60여 종 전부 caught.**

특히 가치 있었던 것은 **양방향 고정**이다. #535의 가드는 "hard로 바꾸는 것"만 요구하지 않고
**hard로 바꾸면 안 되는 곳을 hard로 바꾸는 것도** 실패시킨다.

### 걸린 것: 검사 대상 파일의 주석이 안티패턴을 언급한다

**5개 파일에서 같은 함정**이 나왔고, 한 번은 내 가드가 스스로 걸렸다(`exit 1`을 제거했다고
설명하는 주석에 `exit 1` 검사가 매칭). 해법은 검사 전 주석 제거이고, 그렇게 하면 **주석을
지우고 안티패턴을 되살리는 경우도** 잡힌다.

```python
def _uncommented(shell: str) -> str:
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))
```

### 걸린 것: naive grep 오탐

고아 PNG 삭제 전 참조 확인에서 basename이 포스트 슬러그와 겹쳐 **14건 오탐**이 났다. 경로
기준으로 재확인해 기각했다. 앞서 카드 스캔에서 include 2종 누락으로 과소집계했던 것과 같은
부류다.

### 통한 것: 로컬 검증 불가를 인정하고 CI를 첫 시험대로 쓰기

`--verify`는 macOS에서 30/30 실패하는데 전부 균일한 ~1.5% diff에 `max_block=1134px` 동일 —
플랫폼 렌더링 델타다. 그래서 `pull_request` 트리거를 함께 걸어 그 PR에서 첫 실측을 얻었다.
결과 **30 passed / 0 failed, 전부 0.000% diff** — 가정이 아니라 증명이 됐다.

## 보류 (결정됨, 미실행)

사용자 결정(2026-08-11):

- **`gh pr create` 차단**: 현상유지. #532의 추적 이슈 경로로 운영한다.
- **main required checks**: 보류. 위 발견 5·6이 근거.
- **미설정 시크릿 프로비저닝**: 2026-08-11 결정 — GSC·Vercel은 **프로비저닝**,
  PageSpeed는 현상유지. 아래 "재개 절차" 참조.

### 재개 절차 (시크릿 등록 후)

`test_ci_secret_absence_guard.py`가 "시크릿 미설정 → cron 없음"을 양방향으로 고정하므로,
등록과 cron 복원은 **같은 PR**에서 이뤄져야 한다. 등록 없이 cron만 되살리면 이번엔 영구
green이 아니라 **영구 red**가 된다.

**1. `GSC_SERVICE_ACCOUNT_JSON`** — 얻는 것: sitemap 전수 URL 인스펙션 상태를 일일
아티팩트로. 색인 회복 추이를 자동 기록한다(현재 이 측정이 크레덴셜 부재로 2026-05부터
계속 PENDING이다).

- 키 생성·회전 절차는 [`docs/setup/GSC_SERVICE_ACCOUNT_ROTATION.md`](../docs/setup/GSC_SERVICE_ACCOUNT_ROTATION.md) 참조
  (읽기 전용, 프로젝트 IAM 역할 없음, 90일 회전)
- 등록: `gh secret set GSC_SERVICE_ACCOUNT_JSON < /path/to/key.json`
- 복원 PR: `gsc-queue-refresh.yml`에 `schedule: - cron: '0 6 * * *'` 복원 +
  `test_ci_secret_absence_guard.py`의 `NEVER_CONFIGURED`에서 제거 → `FAIL_CLOSED`로 이동

**2. `VERCEL_TOKEN`** — 얻는 것: 방화벽 설정 변경이 `git diff`로 드러난다.
`docs/backups/vercel-firewall/latest.json`은 **2026-05-08 사건 당일 이후 3개월간 갱신이
0이다** — Googlebot을 며칠간 막았던 그 사건을 다시 못 잡는 상태다.

- 발급: Vercel → Account Settings → Tokens. 팀 스코프 **읽기 전용**으로 충분
  (`PROJECT_ID`/`TEAM_ID`는 기본값이 있어 생략 가능)
- 등록: `gh secret set VERCEL_TOKEN`
- 복원 PR: `vercel-firewall-backup.yml`에 `schedule: - cron: "0 0 * * 1"` 복원 + 위와 동일한
  가드 이동. 부수 효과로 `monitoring.yml`의 Vercel 경로도 함께 살아난다

**3. `PAGESPEED_API_KEY`** — 현상유지. `monitoring.yml`은 이 키 없이도 실제 일을 한다
(프로덕션 HTTP 상태 검사). Core Web Vitals는 `lighthouse-ci` 퍼프 게이트가 PR 단계에서
이미 재고 있어 중복이고, PageSpeed API는 무키 호출도 가능하다(쿼터만 낮다).

## 남은 열화 항목

`jekyll.yml`의 대시보드 코멘트 스텝 내부 `|| true` 3곳(soft 보고 스텝이라 허용),
`monitoring.yml`의 요구 시크릿 3종 미설정 상태(부분 동작 중), `L22`/`L25` generator의
베이스라인 대표 부재(현재 라이브 출력이 없어 보류).

## 참조

- 워크플로 가드: `scripts/tests/test_ci_*.py` (이번에 6개 파일 추가)
- 새 스크립트: `scripts/check_front_matter_growth.py`
- 새 워크플로: `.github/workflows/visual-baseline-verify.yml`
- 관련 회고: [`ci-security-hardening-2026-07.md`](ci-security-hardening-2026-07.md)
