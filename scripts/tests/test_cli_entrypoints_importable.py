#!/usr/bin/env python3
"""CLI 로 실행되는 스크립트는 CLI 로 실행해 봐야 한다.

사건 (2026-09-21, #762)
-----------------------
`scripts/lib/digest_headings` 를 도입하면서 두 파일에서
`from scripts.lib.digest_headings import ...` 를 `sys.path.insert` **위에**
넣었다. 결과:

    $ python3 scripts/enrich_digest_references.py --dry-run
    ModuleNotFoundError: No module named 'scripts'

그런데 **전체 스위트 5917건이 통과했다.** 테스트는 저장소 루트를 직접
`sys.path` 에 넣고 모듈로 import 하므로, 임포트 순서가 틀려도 보이지 않는다.
스위트가 검사하지 않는 실행 방식이 정확히 그 파일들의 **유일한 실제 사용
방식**이었다.

교훈은 "임포트 순서를 조심하라"가 아니다 — 그건 사람에게 기억을 요구한다.
**모듈로 import 해서 검사하는 스위트는 CLI 진입점을 검사하지 않는다**는 것이고,
그래서 여기서는 실제로 서브프로세스를 띄운다. `--help` 는 argparse 가 출력하고
exit 0 으로 끝내므로 부작용이 없다 — 하지만 그 지점까지 가려면 **모듈 최상단
import 가 전부 성공해야** 한다. 잡고 싶은 것이 바로 그것이다.

범위: `add_argument` 와 `__main__` 을 둘 다 가진 `scripts/**` 파일.
2026-09-21 실측 137개, 8워커 병렬로 7.4초.
"""

from __future__ import annotations

import concurrent.futures
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: 서드파티 네이티브 라이브러리가 없어 import 단계에서 죽는 것들. 임포트 순서
#: 결함이 아니라 환경 결함이므로 제외하되, 이유를 적어 둔다. 이유 없이 늘리지
#: 말 것 — 면제 목록은 곧 사각지대다.
_ENV_DEPENDENT = {
    # cairosvg -> libcairo. 렌더링 전용이라 CI 이미지에만 있다.
    "scripts/generate_content_summary.py": "libcairo (cairosvg) 로컬 미설치",
}


def _cli_scripts() -> list[Path]:
    out = []
    for p in sorted(REPO_ROOT.joinpath("scripts").rglob("*.py")):
        rel = p.relative_to(REPO_ROOT).as_posix()
        if "/tests/" in rel or "_archive" in rel:
            continue
        src = p.read_text(encoding="utf-8", errors="ignore")
        if "add_argument" in src and "__main__" in src:
            out.append(p)
    return out


_SCRIPTS = _cli_scripts()


def test_the_scan_found_scripts() -> None:
    """탐색이 0건을 내면 아래 전건 검사가 공허해진다."""
    assert len(_SCRIPTS) > 100, (
        f"CLI 스크립트를 {len(_SCRIPTS)}개만 찾았다. 탐색 조건이 깨졌다면 이 "
        "파일의 모든 검사가 조용히 아무것도 안 하게 된다."
    )


def test_every_cli_entrypoint_starts() -> None:
    """`--help` 까지 도달하면 최상단 import 가 전부 성공했다는 뜻이다.

    한 파일씩 parametrize 하지 않고 한 테스트에서 병렬로 돈다. 137개 서브프로세스를
    순차로 띄우면 스위트가 느려지고, 느린 가드는 결국 꺼진다.
    """
    targets = [
        p for p in _SCRIPTS if p.relative_to(REPO_ROOT).as_posix() not in _ENV_DEPENDENT
    ]

    def run(p: Path):
        r = subprocess.run(
            [sys.executable, str(p), "--help"],
            capture_output=True,
            cwd=REPO_ROOT,
            timeout=120,
        )
        return p, r

    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for p, r in ex.map(run, targets):
            if r.returncode != 0:
                tail = r.stderr.decode("utf-8", "replace").strip().splitlines()
                failures.append(
                    f"  {p.relative_to(REPO_ROOT)}: {tail[-1] if tail else r.returncode}"
                )

    assert not failures, (
        "CLI 로 실행하면 죽는 스크립트가 있다. 모듈로 import 하는 테스트는 이걸 보지 "
        "못한다 — #762 에서 `scripts.*` import 를 sys.path.insert 위에 둔 파일 둘이 "
        "스위트 5917건을 전부 통과하고도 CLI 에서 ModuleNotFoundError 로 죽었다.\n"
        + "\n".join(failures)
    )


@pytest.mark.parametrize("rel,reason", sorted(_ENV_DEPENDENT.items()))
def test_exemptions_still_refer_to_real_files(rel: str, reason: str) -> None:
    """면제 대상이 사라지거나 이름이 바뀌면 조용히 무의미해진다."""
    assert (REPO_ROOT / rel).exists(), (
        f"{rel} 가 없다 — _ENV_DEPENDENT 에서 지워라 ({reason})."
    )
