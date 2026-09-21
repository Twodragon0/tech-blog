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
        "한국어 excerpt 를 공백 기준으로 잘라 닫는 서술어를 날린다(200 상한에서도 "
        "4/4 가 그렇다). keywords: 도 지우는데 head.html:79 가 그걸 읽는다. "
        "숫자를 바꿔서 해결되는 문제가 아니다."
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


# --- trim_front_matter: 숫자를 바꿔서 되돌리지 못하도록 사실을 고정한다 -------


def _excerpts() -> list[tuple[str, str]]:
    import re

    out = []
    for p in sorted((REPO_ROOT / "_posts").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        m = re.search(r'^excerpt:\s*"?(.*?)"?\s*$', text.split("---", 2)[1], re.M)
        if m:
            out.append((p.name, m.group(1)))
    return out


def _ends_at_a_sentence(value: str) -> bool:
    """말줄임표를 걷어낸 뒤 문장 종결부호로 끝나는가."""
    return value.rstrip().removesuffix("...").rstrip().endswith((".", "!", "?"))


@pytest.mark.parametrize("limit", [150, 200])
def test_trimming_an_excerpt_cuts_into_its_final_sentence(limit: int) -> None:
    """상한을 올려도 고쳐지지 않는다는 것이 이 검사의 요지다.

    `truncate_at_word` 는 `rfind(" ")` 로 자른다. 한국어는 어절 사이에 공백이
    있으므로 공백이 안전한 절단점이 아니다 — 문장이 서술어로 끝나는데 그 앞의
    공백에서 잘리면 부사어만 남는다. excerpt 는 목록 페이지·RSS·구글 결과가
    보여주는 줄이다.

        before (204):  … 실무 대응 포인트를 주차 단위로 종합 정리합니다.
        after  (197):  … 실무 대응 포인트를 주차 단위로...

    단언은 **출력이 문장 종결부호로 끝나는가** 다. 여기까지 두 번 고쳤다.

    1. 서술어 어미를 접미사로 찾는 초안은 오탐을 냈다 — `남겼습니다. 다음...`
       에서 다음 어절의 `다` 를 서술어 끝으로 읽었다.
    2. "원문의 마지막 문장이 온전히 남는가" 로 바꿨더니 이번엔 **뮤테이션을
       놓쳤다.** 문장 경계 절단기로 교체해도 통과했다 — 마지막 문장을 통째로
       버리는 것과 중간에서 자르는 것을 구별하지 못하기 때문이다. 이 검사의
       존재 이유가 바로 그 신호인데 그걸 못 봤다.

    끝 모양으로 보면 갈린다. 2026-09-21 실측:

        현재 절단기(공백 기준)   150자 0/288,  200자 0/4  가 문장으로 끝남
        문장 경계 절단기         150자 270/288, 200자 4/4  가 문장으로 끝남

    그래서 재검토 조건은 "숫자를 고쳐라"가 아니라 "문장 경계로 자르는 절단기를
    쓰거나 excerpt 처리를 빼라" 다. 그렇게 되면 이 검사가 실패해서 알려 준다.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from trim_front_matter import truncate_at_word

    over = [(n, v) for n, v in _excerpts() if len(v) > limit]
    assert over, f"{limit}자를 넘는 excerpt 가 없다 — 이 검사가 공허해졌다."

    clean = [
        n
        for n, v in over
        if _ends_at_a_sentence(truncate_at_word(v, limit, suffix="..."))
    ]
    assert not clean, (
        f"{limit}자 절단이 {len(clean)}/{len(over)}건에서 문장 경계로 끝났다. "
        "절단기가 문장을 알게 된 것이라면 trim_front_matter 의 재검토 조건이 "
        f"충족됐다는 뜻이다 — docstring 과 이 검사를 함께 갱신하라: {clean[:3]}"
    )


def test_description_is_never_rendered_so_trimming_it_is_moot() -> None:
    """`head.html` 이 excerpt 를 먼저 쓰고 305/305 가 excerpt 를 갖고 있다.

    이 전제가 깨지면(excerpt 없는 포스트가 생기거나 우선순위가 뒤집히면)
    description 절단이 갑자기 의미를 갖게 되므로, 그때 알려야 한다.
    """
    head = (REPO_ROOT / "_includes" / "head.html").read_text(encoding="utf-8")
    assert "page.excerpt | default: page.description" in head, (
        "head.html 의 description 폴백 순서가 바뀌었다. page.description 이 실제로 "
        "렌더링된다면 trim_front_matter 의 description 한계값을 다시 따져야 한다."
    )
    missing = [n for n, v in _excerpts() if not v.strip()]
    assert not missing, (
        f"excerpt 가 빈 포스트 {len(missing)}건 — 그 포스트들은 description 으로 "
        f"폴백한다: {missing[:3]}"
    )
