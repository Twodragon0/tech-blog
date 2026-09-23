# `main` ruleset — 현재 계정에서는 이 설계로 적용할 수 없다

`main-required-status-checks.json` 은 2026-09-18 에 #750 으로 머지됐지만 한 번도
적용되지 않았다. 2026-09-22 에 실제로 POST 해 보고 **왜 안 되는지가 확정됐다.**
막은 것은 권한 설정이나 실수가 아니라 **계정 유형·플랜 게이트 둘**이다.

```
$ jq '.enforcement="evaluate"' … | gh api --method POST …/rulesets --input -
422  Actor GitHub Actions integration must be part of the ruleset source
     or owner organization

$ jq '.enforcement="evaluate" | .bypass_actors=[]' … | gh api --method POST …
422  Enforcement evaluate option is not supported on this plan.
     Please upgrade to Enterprise to enable it.
```

| 이 파일이 요구하는 것 | 실제 |
|---|---|
| `bypass_actors` = GitHub Actions(Integration, id 15368) | **조직 소유 저장소 전용.** 이 저장소는 `owner.type = User` |
| `enforcement: evaluate` | **Enterprise 플랜 전용** |

둘 다 돈으로 해결되는 문제가 아니라 계정 유형 문제다 —
메모리 `secret_scanning_toggles_silent_noop`(Secret Protection 이 조직 전용이라
개인 계정은 결제해도 못 켬)과 같은 계열이다.

두 POST 모두 검증 단계에서 거부됐으므로 **아무것도 생성되지 않았다**
(`gh api repos/Twodragon0/tech-blog/rulesets` → `[]`).

JSON 자체에도 같은 경고를 `_comment` 키로 실어 뒀다 — 이 README 를 안 열고
파일만 보는 사람을 위해서다. **GitHub 에 보낼 때는 그 키를 걷어낼 것:**

```bash
jq 'del(._comment)' .github/rulesets/main-required-status-checks.json | gh api …
```

`check_required_checks_contract.py` 는 그 키를 무시하며, 경고가 조용히 사라지지
않도록 `test_the_ruleset_file_says_it_is_not_applied` 가 존재를 단언한다.

## 그래도 적용할 수 있는 유일한 형태와, 그것이 깨뜨리는 것

`enforcement: active` + `bypass_actors: []` 는 검증을 통과할 것이다. 그리고
**일일 발행을 멈춘다.** `ai-blogwatcher` 는 `secrets.GITHUB_TOKEN` 으로 main 에
직접 push 하는데(2026-09-22 발행 커밋 `97976d5b`, actor `github-actions[bot]`),
required status check 가 걸린 브랜치에 직접 push 하면 체크를 만족시킬 방법이 없다.
bypass 가 있던 이유가 정확히 이것이다.

**그러므로 이 형태로 켜지 말 것.**

## 진짜 선택지

1. **봇에게 PAT / GitHub App 토큰을 준다.** 그러면 bypass actor 없이도 push 주체가
   달라진다. 메모리 `branch_protection_bot_token` 이 기록한 경로다. 현재 등록된
   시크릿에 해당 토큰은 **없다**(2026-09-22 확인). 시크릿 신규 발급이므로 사람이
   판단·수행할 일이다.
2. **발행을 PR 경로로 바꾼다.** 크론이 직접 push 대신 PR 을 열고 auto-merge 에
   맡기면 required check 가 자연스럽게 만족된다. 단 발행 지연이 늘고,
   `cron_posts_get_no_notifications` / `ci_gates_blind_to_cron_bot_push` 가 기록한
   봇-push 관련 부작용들의 전제가 바뀌므로 영향 범위가 넓다.
3. **그대로 둔다.** 현재도 PR 은 전부 5개 체크를 통과하고 있고(아래), 강제가 없을
   뿐 실질 위반은 관측되지 않았다.

## 적용 전 실측해 둔 것 (2026-09-22, 여전히 유효)

위 선택지 중 무엇을 고르든 이 두 가지는 먼저 확인된 상태다.

**아무도 만들지 않는 체크 이름은 없다.** 하나라도 있으면 모든 PR 이 영구히 막힌다.

| 요구 체크 | #772 (1 file, 문서 전용) | #771 | #769 |
|---|---|---|---|
| `ruff` | pass | pass | pass |
| `build` | pass | pass | pass |
| `Security Audit Summary` | pass | pass | pass |
| `CodeQL` | pass | pass | pass |
| `GitGuardian Security Checks` | pass | pass | pass |

`npm Security Audit` / `Ruby Gem Security Audit` / `auto-merge` 는 `skipping` 으로
끝나는 일이 있으므로 **요구 목록에 넣지 말 것.**

**bypass actor id 자체는 맞았다.** `gh api /apps/github-actions` →
`slug=github-actions id=15368`. 틀린 것은 id 가 아니라 개인 저장소에서 그 actor 를
선언할 수 없다는 점이다.

배경: `notes/decisions.md` — 2026-09-18(설계), 2026-09-22(적용 불가 확정).
