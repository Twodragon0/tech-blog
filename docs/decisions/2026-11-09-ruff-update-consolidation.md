# Ruff 업데이트 통합안 (2026-11-09)

## 변경과 검증

기준 main `786e1ad8`에서 Ruff 선언 두 곳과 workflow 핀 네 곳을 0.16.9로
동시에 갱신한다. requirement 파일의 기존 하한 선언(`>=`)은 유지하고,
차단 린트·운영 검사의 실행 버전은 `==0.16.9`로 고정한다.
새 패키지나 workflow를 추가하지 않는다.

| 위치 | 결과 |
|---|---|
| `requirements-blogwatcher.txt` | `ruff>=0.16.9` |
| `scripts/requirements-ci.txt` | `ruff>=0.16.9` |
| `python-lint.yml` 한 곳 | `ruff==0.16.9` |
| `ops-orchestrator.yml` 세 곳 | `ruff==0.16.9` |

임시 도구 디렉터리에 설치한 Ruff 0.16.9로 scripts 전체 린트와 483개 파일의
포맷 검사가 통과했다. 소스 재포맷은 필요하지 않았다.
기존 `test_ci_python_lint_gate.py`와 `test_ci_python_syntax_floor_guard.py`는
합계 23개 통과했다. 변경된 두 workflow의 Actionlint와 diff 공백 검사도 통과했다.
하한 선언은 의존성 lockfile이 아니므로 미래의 설치가 반드시 0.16.9를 사용한다는
보장은 하지 않는다. 기존 정합성 가드는 workflow 핀이 선언 범위를 만족하는지 검사한다.

## 기존 PR 대체 순서

1. 통합 변경의 PR을 생성하고 최종 HEAD에서 린트·Jekyll 등 CI를 확인한다.
2. [#778](https://github.com/Twodragon0/tech-blog/pull/778)은 0.16.8의 네 핀·두 선언 변경,
   [#759](https://github.com/Twodragon0/tech-blog/pull/759)는 0.16.8의 두 선언 변경,
   [#783](https://github.com/Twodragon0/tech-blog/pull/783)은 CI 선언만 0.16.9로 올린 변경이다.
   통합안은 세 변경의 Ruff 버전 범위를 함께 대체한다.
3. 리뷰·CI가 통과하고 통합 PR의 반영 경로가 확정된 후 기존 세 PR을 대체됨으로 정리한다.
   세 PR을 순서대로 병합해 0.16.8로 다시 내리지 않는다.
4. [#798](https://github.com/Twodragon0/tech-blog/pull/798)의 Actions 업데이트는 별도 범위다.
   workflow가 겹치므로 병합 순서에 따라 충돌을 해소하고 핀·선언 정합성을 다시 검사한다.

이 로컬 작업에서는 원격 전송·PR 종료·병합을 하지 않았다.
되돌릴 때에는 네 파일의 버전을 함께 되돌려 정합성을 유지한다.
