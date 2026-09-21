#!/usr/bin/env python3
"""배선하면 안 되는 스크립트 2종을, 문서가 아니라 검사로 묶어 둔다.

왜 필요한가
-----------
2026-09-21 의 전수 조사에서 "호출처 0" 인 코퍼스 스크립트 42개를 실측했다. 대부분은
완료된 일회성 도구라 수동인 게 맞았고, `enrich_digest_references` 하나만 배선이
빠진 진짜 결손이어서 #764 에서 발행 경로에 넣었다.

그 과정에서 **배선해서는 안 되는** 2건이 나왔다. 둘 다 "N건이 대상"이라고 보고해
backlog 처럼 읽히지만, 원인을 분류하면 방향이 반대다. 판단 근거를 `notes/` 에만
적으면 다음 사람이 같은 dry-run 숫자를 보고 같은 판단을 반복한다 — 이 저장소가
이미 여러 번 치른 비용이다. 그래서 여기에 건다.

무엇을 거는가
-------------
* `trim_front_matter` — 배선 부재. 측정치는 docstring 에 있다.
* `backfill_digest_commentary --no-llm` — **런타임 거부**. 이쪽은 존재 단언이
  아니라 실제 통제다: `--no-llm` 은 결정론적 가짜 문단을 쓰고(6/6 꼬리 문장 동일),
  `--commit` 과 함께 쓰면 그대로 발행된다. 그리고 **하류 게이트가 잡지 못한다** —
  `check_post_boilerplate` 는 Mermaid 펜스와 체크리스트만 보므로 세 포스트에
  실제로 써 넣고 돌렸을 때 exit 0 을 냈다. 막을 수 있는 지점이 소스뿐이다.

방향: 존재 단언. 배선을 **추가**하면 걸리고, 다른 스크립트를 배선하는 것은 아무것도
건드리지 않는다.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.lib.source_text import without_comments  # noqa: E402

#: 스크립트 -> 배선 금지 사유(한 줄). 사유 없이 늘리지 말 것.
_DO_NOT_WIRE = {
    "trim_front_matter.py": (
        "excerpt 를 150자로 자르는데 CLAUDE.md 규격은 150-200 이고 287건이 그 "
        "범위 안에 있다. 또 keywords: 를 지우는데 head.html:79 가 그걸 읽는다."
    ),
    "backfill_digest_commentary.py": (
        "--no-llm 이 결정론적 가짜 문단을 쓴다(6/6 꼬리 문장 동일). 자동 실행 "
        "경로에 두면 그 플래그가 섞여 들어갈 자리가 생긴다."
    ),
}


def _wiring_surfaces() -> dict[str, str]:
    """워크플로·훅·셸 — 무언가를 자동으로 실행할 수 있는 곳.

    주석을 접고 읽는다. 사유를 적은 주석이 그 자체로 '배선'으로 읽히면, 설명을
    잘 쓸수록 이 검사가 실패하게 된다 — scripts/lib/source_text 가 존재하는 이유다.
    """
    out = {}
    for pat in (
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        ".githooks/*",
        "scripts/*.sh",
        ".claude/hooks/*",
    ):
        for p in REPO_ROOT.glob(pat):
            if p.is_file():
                text = p.read_text(encoding="utf-8", errors="ignore")
                try:
                    out[str(p.relative_to(REPO_ROOT))] = without_comments(
                        text, suffix=p.suffix
                    )
                except SyntaxError:
                    out[str(p.relative_to(REPO_ROOT))] = text
    return out


def test_the_surface_scan_is_not_empty() -> None:
    """탐색이 0건이면 아래 검사가 전부 공허해진다."""
    surfaces = _wiring_surfaces()
    assert len(surfaces) > 10, f"자동 실행 표면을 {len(surfaces)}개만 찾았다."
    assert any("ai-blogwatcher" in k for k in surfaces), (
        "발행 워크플로가 스캔 범위 밖이다 — 정작 배선이 일어나는 곳을 안 보고 있다."
    )


@pytest.mark.parametrize("script,reason", sorted(_DO_NOT_WIRE.items()))
def test_not_wired_into_any_automated_path(script: str, reason: str) -> None:
    found = [k for k, v in _wiring_surfaces().items() if script in v]
    assert not found, (
        f"{script} 가 {found} 에서 자동 실행된다. 배선 금지 사유: {reason} "
        f"측정 근거는 그 파일의 docstring 과 notes/decisions.md(2026-09-21)에 있다. "
        "배선이 필요해졌다면 그 측정을 먼저 반박하고 이 목록에서 지워라."
    )


@pytest.mark.parametrize("script", sorted(_DO_NOT_WIRE))
def test_the_reason_is_recorded_where_the_reader_is(script: str) -> None:
    """사유는 이 테스트가 아니라 스크립트 안에 있어야 한다.

    스크립트를 열어 본 사람이 테스트 파일까지 찾아가지는 않는다.
    """
    src = (REPO_ROOT / "scripts" / script).read_text(encoding="utf-8")
    head = src[: src.find("\n\n\n")] if "\n\n\n" in src else src[:4000]
    assert "notes/decisions.md" in head, (
        f"{script} 의 헤더가 측정 근거를 가리키지 않는다. 사유 없는 금지는 다음 "
        "사람이 같은 dry-run 숫자를 보고 되돌린다."
    )


@pytest.fixture
def sandboxed_digest(tmp_path: Path) -> str:
    """진짜 다이제스트의 사본을 tmp 에 두고, 그것만 가리키는 glob 를 준다.

    `_posts/` 를 직접 가리키면 안 된다. 거부가 회귀하는 순간 **테스트 자신이**
    가짜 문단을 코퍼스에 써 넣는다 — 이 가드를 만들면서 뮤테이션 프로브로 실제로
    그렇게 했고, `git diff` 로 발견해 되돌렸다. 검사가 자기가 막으려는 사고를
    일으켜서는 안 된다.
    """
    src = next(
        p
        for p in sorted((REPO_ROOT / "_posts").glob("2026-09-*Weekly_Digest*.md"))
        if "## 분석가 시점" not in p.read_text(encoding="utf-8")
    )
    dst = tmp_path / src.name
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return str(tmp_path / "*Weekly_Digest*.md")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "backfill_digest_commentary.py"),
            *args,
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_no_llm_refuses_to_commit(sandboxed_digest: str) -> None:
    """실제 통제 — 존재 단언이 아니라 동작을 확인한다.

    `check_post_boilerplate` 는 이 텍스트를 잡지 못한다(세 포스트에 써 넣고 돌려
    exit 0). 하류 방어가 없으므로 이 거부가 유일한 방어선이다.
    """
    r = _run("--no-llm", "--commit", "--posts-glob", sandboxed_digest)
    assert r.returncode != 0, (
        "--no-llm --commit 이 통과했다. 결정론적 가짜 문단이 코퍼스에 쓰인다."
    )
    assert "--no-llm" in (r.stderr + r.stdout), (
        "거부는 했지만 이유를 말하지 않았다 — 무엇을 고쳐야 할지 알 수 없다."
    )
    written = [
        p
        for p in Path(sandboxed_digest).parent.glob("*.md")
        if "## 분석가 시점" in p.read_text(encoding="utf-8")
    ]
    assert not written, (
        "거부 코드는 반환했지만 파일은 이미 쓰인 뒤였다 — 거부가 glob 확장보다 "
        "앞서야 한다."
    )


def test_no_llm_dry_run_still_works(sandboxed_digest: str) -> None:
    """거부가 과하면 테스트 용도 자체가 죽는다. 대조군."""
    r = _run("--no-llm", "--dry-run", "--limit", "1", "--posts-glob", sandboxed_digest)
    assert r.returncode == 0, (
        f"--no-llm --dry-run 까지 막혔다. 거부는 --commit 조합에만 걸려야 한다.\n"
        f"{r.stderr[-400:]}"
    )
