# `main` ruleset — 적용 절차

`main-required-status-checks.json` 은 **선언일 뿐 적용이 아니다.** 저장소에
ruleset 을 만드는 것은 `POST /repos/.../rulesets` 이고, 파일을 머지해도 아무 일도
일어나지 않는다. 2026-09-18 에 #750 으로 머지됐고 2026-09-22 현재까지 미적용이다
(`gh api repos/Twodragon0/tech-blog/rulesets` → `[]`).

## 먼저 evaluate 로

파일은 `"enforcement": "active"` 다. 아래 명령을 그대로 쓰면 **곧바로 강제**되므로,
영향을 무해하게 보려면 값을 덮어써야 한다.

```bash
# 1) evaluate — 아무것도 막지 않고 위반만 기록한다
jq '.enforcement="evaluate"' .github/rulesets/main-required-status-checks.json \
  | gh api --method POST repos/Twodragon0/tech-blog/rulesets --input -

# 2) 하루 지켜본 뒤 active 로
gh api --method POST repos/Twodragon0/tech-blog/rulesets \
  --input .github/rulesets/main-required-status-checks.json
```

이미 만들어 둔 ruleset 의 모드만 바꾸려면 `PUT .../rulesets/{id}` 다.

## 적용 전에 확인한 것 (2026-09-22 실측)

적용을 미루는 동안 가장 큰 위험 둘을 먼저 쟀다. 둘 다 통과했다.

**1. 아무도 만들지 않는 체크 이름이 있는가** — 하나라도 있으면 모든 PR 이 영구히
막힌다. 요구 5개 전부 실제 PR 에서 생성되고, **1파일짜리 문서 전용 PR(#772)에서도
5/5 가 pass** 한다. `skipping` 으로 끝나는 것은 없다.

| 요구 체크 | #772 (1 file) | #771 | #769 |
|---|---|---|---|
| `ruff` | pass | pass | pass |
| `build` | pass | pass | pass |
| `Security Audit Summary` | pass | pass | pass |
| `CodeQL` | pass | pass | pass |
| `GitGuardian Security Checks` | pass | pass | pass |

`npm Security Audit` / `Ruby Gem Security Audit` / `auto-merge` 는 `skipping` 으로
끝나는 일이 있으므로 **요구 목록에 넣지 말 것.**

**2. 일일 크론 push 가 막히는가** — `ai-blogwatcher` 는 main 에 직접 push 한다.
bypass actor 가 틀리면 켜는 즉시 발행이 멈춘다.

```
bypass_actors[0].actor_id = 15368
  gh api /apps/github-actions  →  slug=github-actions  id=15368  ✓
크론 커밋 97976d5b (2026-09-22 발행)
  author = github-actions[bot]  committer = github-actions[bot]  ✓
```

`actor_type: "Integration"` + `bypass_mode: "always"` 이므로 크론 push 는 통과한다.

## 적용 후 확인

```bash
gh api repos/Twodragon0/tech-blog/rulesets              # 생성 확인
gh api repos/Twodragon0/tech-blog/rules/branches/main   # main 에 실제로 걸렸는지
```

그리고 **다음 크론 발행이 실제로 push 되는지** 본다. 스케줄 발화는 선언 시각보다
상시 몇 시간 늦으므로(`scripts/check_cron_firing.py` docstring 참조) 바로 판단하지
말 것.

배경과 왜 classic 보호가 아니라 ruleset 인지: `notes/decisions.md`, 2026-09-18.
