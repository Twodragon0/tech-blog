# 부분문자열 가드 공허성 감사 (2026-09-18)

> **결과: 공허한 가드 0건 / 프로브 대상 20건.** 같은 날 세 번 재발한 결함은 전부
> **그날 새로 작성된 가드**에서 나왔다. 기존 가드는 건강하다.

## 계기 — 하루에 세 번

"부분문자열 스캔은 읽기와 읽기에 대한 산문을 구분하지 못한다" 가 2026-09-18 하루에
세 번 발생했다.

| # | 어디 | 증상 |
|---|---|---|
| #742 | `check_secret_contract.code_consumers` | `PAGESPEED_API_KEY` **제거 사유 주석 3개**를 소비자로 세어 "0 violations" 를 냈다 |
| #746 | `test_ci_ops_failure_issue_inlines_report` 초안 | 자기 설명 주석이 옛 버그를 인용해서 **옳은 워크플로에서 실패**했다 |
| #751 | `test_gemini_image_flag_defaults` 초안 | 찾는 문자열이 **로그 줄에도** 있어 버그를 되돌려도 **통과**했다 |

셋 다 "통과"나 "실패"로 위장하고, 특히 1번은 **정리를 잘 할수록** 더 확실히 눈이 먼다.

## 방법 — 분류가 아니라 프로브

정적 분류는 세 번 틀렸다. 매번 **내 추출기**가 원인이었다.

| 시도 | 보고 | 실제 |
|---|---|---|
| 1차: 리터럴이 "문자열 리터럴 위치" 면 비-코드로 셈 | 공허 65건 | `add_argument("--staged")` 처럼 **함수적 문자열이 곧 코드**인 경우를 오분류 |
| 2차: 주석·독스트링만 비-코드, 줄 단위 | 22건 | `DEFAULT_THRESHOLD_PCT = 0.5  # max % …` 처럼 **끝주석이 붙은 코드 줄**을 통째로 주석 취급 |
| 3차: 컬럼 단위 | 20건 | 여기까지가 후보. 판정은 여전히 불가 — 가드가 파일 전체가 아니라 **슬라이스**에 단언할 수 있다 |

그래서 판정은 **뮤테이션 프로브**로만 했다. 대상 파일에서 **주석·독스트링 안의
occurrence 만** 같은 길이로 치환하고 테스트를 다시 돌린다. 깨지면 그 단언은 산문을
읽고 있었던 것이다. 대조군(치환 전 통과)을 매번 먼저 확인한다 —
[`mutation_probe_needs_control`](../CLAUDE.md).

## 결과

**20건 전부 "코드를 본다".** VACUOUS 로 나온 3건(테스트 2개)은 전부 **문서가 대상인
것이 의도**였고, 테스트 이름이 그렇게 말한다:

- `test_inline_gate_registry.test_the_workflow_points_at_the_registry`
  — 독스트링: *"The whole problem was that the workflow gave no hint these exist."*
  `ai-blogwatcher.yml` 의 **주석**이 `INLINE_PUBLISH_GATES` 를 가리키는지 검사하는 것이
  목적이다. 주석이 대상인 게 맞다.
- `test_sentry_csp_volume.test_docstring_records_why_401_403_is_not_fail_closed`
  — `mod.__doc__` 를 직접 읽는다. 이름이 이미 그렇게 말한다.

즉 **오탐이 아니라 정상 설계**다. 이것이 이 검사를 CI 게이트로 만들지 않은 이유다 —
게이트로 만들면 이 둘을 면제 목록에 넣어야 하고, 면제 목록이 바로 썩는 그것이다.

## 실제로 나온 것 — 같은 방어가 6벌, 강도가 다르다

| 구현 | 방식 | 끝주석 | 문자열 안 `#` |
|---|---|---|---|
| `test_trend_single_source._code_only` | `tokenize` | 처리 | 안전 |
| `test_inline_gate_registry._code_only` | `tokenize` (오프셋 보존) | 처리 | 안전 |
| `test_ci_python_lint_gate._code` | `_code_lines` 위임 | — | — |
| `test_ci_soft_spot_triage_guard._code` | 줄 접두사 `#` | **놓침** | 해당없음 |
| `test_ci_ops_failure_issue_inlines_report._code` | 줄 접두사 `#`/`//`/`*` | **놓침** | 해당없음 |
| `test_font_tier_split._strip_comments` | HTML 주석 | — | — |

줄-접두사 방식은 끝주석을 놓친다. **이 감사의 2차 시도가 정확히 그 함정에 빠졌다** —
`DEFAULT_THRESHOLD_PCT = 0.5  # …` 를 주석으로 읽어 오탐 4건을 냈다. 현재 그 약점 때문에
공허해진 가드는 없지만(위 프로브 결과), 일곱 번째 작성자는 또 처음부터 짓게 된다.

통합은 통과 중인 가드 6개를 건드리는 일이라 이 감사에서는 하지 않았다. 기록만 남긴다.

## 다시 쓸 때

```bash
# 전수
python3 scripts/dev/probe_guard_vacuity.py --scan

# 단건 (새 가드를 쓰면서)
python3 scripts/dev/probe_guard_vacuity.py \
  --test scripts/tests/test_x.py --target scripts/y.py --literal "--flag"
```

새 가드를 쓸 때의 규칙 두 가지:

1. 소스 텍스트에 리터럴을 단언하기 전에 **주석·독스트링을 먼저 제거**하거나, 아예
   `ast` 로 호출 지점·조건을 직접 읽는다. #751 은 후자로 고쳤다 — 부분문자열로는
   호출 지점과 로그 줄을 구분할 수 없었다.
2. **문서가 대상이면 테스트 이름에 그렇게 쓴다.** 위 두 건이 그렇게 해서, 이 감사에서
   즉시 정상으로 판정됐다.
