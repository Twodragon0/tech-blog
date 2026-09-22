# 이 저장소에서 켤 수 없는 GitHub 기능 (계정 유형 게이트)

`Twodragon0/tech-blog` 는 **개인 계정 소유 공개 저장소**다.

```bash
$ gh api repos/Twodragon0/tech-blog --jq '.owner.type'
User
```

GitHub 의 저장소 거버넌스 기능 상당수는 **결제가 아니라 소유 주체**로 갈린다.
같은 벽에 두 번 부딪히고 나서 이 문서를 만들었다 — 제안하기 전에 여기를 볼 것.

## 켤 수 없는 것

| 기능 | 게이트 | 증상 | 확정일 |
|---|---|---|---|
| ruleset `bypass_actors` (GitHub Actions Integration) | **조직 소유 전용** | `422 Actor GitHub Actions integration must be part of the ruleset source or owner organization` | 2026-09-22 |
| ruleset `enforcement: evaluate` | **Enterprise 플랜 전용** | `422 Enforcement evaluate option is not supported on this plan.` | 2026-09-22 |
| Secret scanning **validity checks** | 조직 소유 전용 | `PATCH` 가 **200 을 반환하고 조용히 무시** — 재조회하면 `disabled` 그대로 | 2026-08-07 |
| Secret scanning **AI detection** | 조직 소유 전용 | 같음. 재조회하면 키 자체가 `absent` | 2026-08-07 |

2026-09-22 현재 상태:

```json
{"owner_type":"User","secret_scanning":"enabled","push_protection":"enabled",
 "validity_checks":"disabled","ai_detection":"absent"}
```

`secret_scanning` 과 `push_protection` 은 **켜져 있다.** 공개 저장소에는 무료로
제공되는 것들이고, 위 표의 두 토글만 조직 전용이다.

## 두 가지 실패 모양을 구별할 것

이 게이트들은 **서로 다른 방식으로** 실패한다.

- **422 로 거부** (ruleset) — 시끄럽다. 시도하면 즉시 안다.
- **200 후 조용한 무시** (secret scanning 토글) — 위험하다. `PATCH` 가 성공을
  돌려주므로 켰다고 착각하기 쉽다. **반드시 재조회해서 값을 확인할 것.**

## 제안하기 전에 할 것

1. 이 문서와 메모리(`ruleset_bypass_and_evaluate_are_org_only`,
   `secret_scanning_toggles_silent_noop`)를 먼저 읽는다.
2. 목록에 없으면 **한 번은 끝까지 밀어 본다.** 실패 메시지 하나가 추측보다
   훨씬 많은 것을 알려 준다. ruleset 은 나흘 동안 "권한이 없어서 못 한다" 로만
   보고되다가, 실제로 POST 한 날 진짜 이유가 드러났다.
3. 상태를 바꾸는 API 를 쓴 뒤에는 **재조회한다.** 응답 코드는 반영의 증거가
   아니다.

## 관련

- `.github/rulesets/README.md` — ruleset 이 적용 불가인 이유와 남은 선택지
- `notes/decisions.md` — 2026-09-18(ruleset 설계), 2026-09-22(적용 불가 확정)
- `scripts/check_required_checks_contract.py` — ruleset 이 적용되지 않아도
  요구 체크 이름이 실제로 생성 가능한지는 계속 검사한다(pytest 에서 실행)
