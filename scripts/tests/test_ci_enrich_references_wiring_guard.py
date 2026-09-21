#!/usr/bin/env python3
"""배선 가드: 참고자료 보강이 발행 경로에 남아 있어야 한다.

왜 배선 가드인가
----------------
`enrich_digest_references.py` 는 2026-08-06 에 5건 파일럿(#507)으로 들어와,
누군가 2026-01~07 을 백필했다. 그리고 **어디에서도 호출되지 않았다** — 워크플로
0, 훅 0, 파이프라인 0. 스크립트는 내내 정상이었고 테스트도 통과했다. 아무도
돌리지 않았을 뿐이다.

2026-09-21 실측(이 스텝이 생기기 전):

    2026-04..07   30/30 씩 보유   (백필)
    2026-08        6/31 보유      (25건 누락)
    2026-09       14/19 보유      (5건 누락, 그날 아침 발행분 포함)

**생성기는 용도 칼럼을 내보내지 않는다.** 이 스크립트가 유일한 생산자이므로,
배선이 빠지면 그날부터 발행되는 모든 다이제스트가 결손 상태로 태어난다. 게이트가
없어서 아무도 불평하지 않고, 몇 주 뒤 수작업 캠페인이 발견한다 — 실제로 그렇게
30건이 쌓였다.

여기서 코퍼스 전역 검사기를 만들지 않은 이유
--------------------------------------------
위 표의 누락을 검사기로 만들면 태어날 때부터 red 다. 레거시 다이제스트 13건은
참고자료 섹션 자체가 없고(2026-08-06 에 실측으로 기각된 집합), 01~03 월에도
칼럼 없는 포스트가 남아 있다. CLAUDE.md 가 값을 치르고 배운 규칙이 이것이다 —
**휴면 게이트는 배선 전에 돌려서 출력을 읽을 것.** 그래서 사후조건은 그날 발행분
하나에만 건다.

방향: 존재 단언. 범위를 넓히면 아무것도 안 걸리고, 없애면 걸린다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"
STEP_NAME = "Reference-table enrichment (enrich, then verify)"


def _publish_steps() -> list[dict]:
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps: list[dict] = []
    for job in doc["jobs"].values():
        steps.extend(job.get("steps") or [])
    return steps


def _step() -> dict:
    for s in _publish_steps():
        if s.get("name") == STEP_NAME:
            return s
    raise AssertionError(
        f"{WORKFLOW.name} 에 {STEP_NAME!r} 스텝이 없다. 이 스텝이 빠지면 생성기가 "
        "용도 칼럼을 내보내지 않으므로 그날부터 발행되는 다이제스트가 전부 결손 "
        "상태로 태어나고, 대응 게이트가 없어 아무도 불평하지 않는다. 2026-08 에 "
        "25/31 이 그렇게 쌓였다."
    )


def test_the_publish_path_still_enriches() -> None:
    assert "enrich_digest_references.py" in _step()["run"], (
        "스텝은 남아 있는데 enrich 호출이 사라졌다."
    )


def test_the_enrichment_is_not_neutralised() -> None:
    """`|| true` 나 continue-on-error 는 조용한 무력화다.

    이 저장소는 이미 그렇게 죽은 게이트를 겪었다. 실패해야 할 때 실패하지 않으면
    green 은 정보량이 0 이다.
    """
    step = _step()
    assert not step.get("continue-on-error"), (
        "continue-on-error 가 붙었다 — 보강이 실패해도 발행이 진행된다."
    )
    run = step["run"]
    for line in run.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "enrich_digest_references.py" in stripped:
            assert "|| true" not in stripped, (
                f"enrich 호출이 `|| true` 로 무력화됐다: {stripped!r}"
            )


def test_the_post_condition_survives() -> None:
    """보강이 조용히 no-op 해도 통과하면 안 된다.

    30건이 쌓인 방식이 정확히 '아무 일도 일어나지 않았는데 아무도 몰랐다' 이다.
    사후조건이 없으면 이 스텝은 그 상태를 재생산한다.
    """
    run = _step()["run"]
    assert "용도" in run, (
        "사후조건이 사라졌다 — 스텝이 no-op 으로 끝나도 발행이 계속된다."
    )
    assert "REFERENCE_HEADING_RE" in run, (
        "사후조건이 참고자료 섹션 존재를 확인하지 않는다. 생성기가 세 번째 표기를 "
        "쓰기 시작하면 보강이 조용히 건너뛴다 — #762 가 정확히 그 사고였다."
    )


def test_it_runs_before_the_corpus_gate() -> None:
    """보강된 결과가 게이트를 통과하는지 확인돼야 한다.

    뒤에 두면 그날 발행분은 보강 전 상태로 검사받고, 보강이 무언가를 깨도
    다음 날까지 아무도 모른다.
    """
    names = [s.get("name") for s in _publish_steps()]
    assert STEP_NAME in names
    corpus = "Corpus gate pre-flight (block)"
    assert corpus in names, f"{corpus!r} 스텝이 사라졌다 — 이 순서 단언이 공허해졌다."
    assert names.index(STEP_NAME) < names.index(corpus), (
        "보강이 코퍼스 게이트 뒤로 밀렸다. 보강 결과가 검사되지 않는다."
    )


def test_enrich_is_still_the_only_producer_of_the_column() -> None:
    """생성기가 칼럼을 직접 내보내기 시작했다면 이 배선은 불필요해진다.

    그때는 스텝을 지우는 게 맞다 — 다만 그 판단을 근거 없이 하지 않도록,
    전제가 바뀌면 여기서 알린다.
    """
    gen = (REPO_ROOT / "scripts" / "news" / "content_generator.py").read_text(
        encoding="utf-8"
    )
    assert "| 용도 |" not in gen, (
        "content_generator 가 용도 칼럼을 직접 내보낸다. 그렇다면 발행 경로의 "
        "보강 스텝은 중복이다 — 이 테스트와 함께 재검토하라."
    )
