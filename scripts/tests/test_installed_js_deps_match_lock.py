#!/usr/bin/env python3
"""설치된 JS 의존성이 lock 과 다르면 `npm test` 결과는 근거가 아니다.

사건 (2026-09-23)
-----------------
`53e9e922`(vitest 4 → 5 메이저 범프)를 사후 리뷰하면서 `npm test` 를 돌려
**738 passed** 를 받고 "범프는 안전하다" 고 적을 뻔했다. 그 검증은 공허했다 —
`node_modules` 가 낡아 실제로는 **vitest 4.1.10** 으로 돌고 있었다. 선언은
`^5.0.0`, lock 도 5.0.0 이었는데 설치본만 4 였다.

`npm ci` 로 lock 대로 설치하고 다시 돌려서야 vitest 5.0.0 에서의 결과(30 files /
738 tests)를 얻었다. 숫자는 같았지만, 같은 숫자가 나온다는 것을 **몰랐던 상태에서
그 숫자를 근거로 쓰려 했던 것**이 문제다.

CI 는 `npm ci` 를 쓰므로 이 함정에 빠지지 않는다. 빠지는 것은 로컬에서 확인하는
사람이고, 그 사람이 PR 설명에 "로컬에서 전건 통과" 라고 적는다.

왜 테스트인가
-------------
"`npm test` 전에 `npm ci` 를 하라" 는 규칙은 사람 기억에 의존한다. 이 저장소가
반복해서 배운 대로, 기억을 요구하는 규칙은 다음에도 실패한다. 파이썬 스위트는
로컬에서 늘 돌므로 여기 걸어 두면 불일치가 있을 때 **조용히 통과하지 않는다.**

범위는 lock 이 직접 고정한 최상위 개발 의존성으로 한정한다. 전이 의존성까지
비교하면 `npm ci` 를 안 한 트리에서 소음이 커지고, 그러면 가드가 꺼진다.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"
LOCK = REPO_ROOT / "package-lock.json"
NODE_MODULES = REPO_ROOT / "node_modules"


def _declared() -> dict[str, str]:
    data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for key in ("dependencies", "devDependencies"):
        out.update(data.get(key) or {})
    return out


def _locked(name: str) -> str | None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    entry = (lock.get("packages") or {}).get(f"node_modules/{name}")
    return (entry or {}).get("version")


def _installed(name: str) -> str | None:
    pkg = NODE_MODULES / name / "package.json"
    if not pkg.is_file():
        return None
    return json.loads(pkg.read_text(encoding="utf-8")).get("version")


def test_lock_covers_every_declared_dependency() -> None:
    """lock 에 없는 선언이 있으면 아래 비교가 그 패키지를 조용히 건너뛴다."""
    missing = [n for n in _declared() if _locked(n) is None]
    assert not missing, (
        f"package.json 에 선언됐지만 package-lock.json 이 고정하지 않은 패키지: "
        f"{missing}. `npm install` 로 lock 을 갱신하라."
    )


@pytest.mark.skipif(
    not NODE_MODULES.is_dir(),
    # 이 문구는 test_skip_path_policy.ALLOWED_REASON_PATTERNS 의 "not installed"
    # 에 걸린다. node_modules 는 gitignore 대상이고 `npm ci` 로만 생기므로
    # 저장소 산출물이 아니라 환경 사실이다 — 파이썬만 도는 CI 잡에는 없다.
    reason="node_modules is not installed (npm ci has not run in this environment)",
)
@pytest.mark.parametrize("name", sorted(_declared()))
def test_installed_version_matches_lock(name: str) -> None:
    """설치본이 lock 과 다르면 `npm test` 결과를 근거로 쓸 수 없다.

    이 검사가 실패하면 테스트가 틀린 게 아니라 **트리가 낡은 것**이다.
    `npm ci` 를 돌리고 다시 확인하라.

    node_modules 가 있는데 특정 패키지만 없는 경우는 **skip 하지 않는다.** 그것이
    바로 잡으려는 드리프트이고, skip 하면 green 으로 보고된다 —
    `test_skip_path_policy` 가 그 점을 지적해서 고쳤다.
    """
    locked = _locked(name)
    installed = _installed(name)
    assert installed is not None, (
        f"{name} 이 lock 에는 있는데 node_modules 에 없다. 트리가 lock 과 어긋나 "
        "있으므로 `npm test` 결과를 근거로 쓸 수 없다. `npm ci` 로 맞출 것."
    )
    assert installed == locked, (
        f"{name}: 설치본 {installed} != lock {locked}. 이 상태에서 `npm test` 가 "
        "내는 결과는 lock 이 고정한 버전의 결과가 아니다 — 2026-09-23 에 vitest "
        "4.1.10 으로 돌린 738 passed 를 5.0.0 의 근거로 쓸 뻔했다. `npm ci` 후 "
        "다시 돌릴 것."
    )
