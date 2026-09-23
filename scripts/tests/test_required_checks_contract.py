#!/usr/bin/env python3
"""Runs the credentials-free half of scripts/check_required_checks_contract.py.

`--gh` is deliberately NOT here: it needs an authenticated `gh`, and a suite
that fails without credentials is a suite people learn to ignore. Same split as
check_secret_contract.py and check_runtime_env_contract.py.

What this protects
------------------
A required status check is a NAME. If nothing produces that name, GitHub never
receives the status and **every pull request blocks forever**. That is the same
defect as A-H3 (a four-name exclusion list that matched nothing after the
workflows were consolidated) with a much larger blast radius, so the required
set is declared in `.github/rulesets/main-required-status-checks.json` and
checked here rather than living only in the UI.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_required_checks_contract as rc  # noqa: E402


def test_ruleset_file_exists() -> None:
    assert rc.RULESET.is_file(), (
        f"{rc.RULESET} is missing. The required-check set must stay declared in "
        "the repo — a set that lives only in the GitHub UI cannot be reviewed, "
        "diffed, or guarded."
    )
    json.loads(rc.RULESET.read_text(encoding="utf-8"))  # must parse


def test_contract_holds() -> None:
    problems = rc.check_contract()
    assert problems == [], "\n".join(problems)


def test_every_required_check_resolves() -> None:
    """Either a workflow job produces it, or it is a documented external app."""
    unresolved = [
        c
        for c in rc.required_contexts()
        if not rc.producers(c) and c not in rc.EXTERNAL_CHECKS
    ]
    assert unresolved == [], (
        f"{unresolved} are required but nothing produces them. Every PR would "
        "block. This is the A-H3 failure mode aimed at the merge queue."
    )


def test_no_required_check_is_paths_filtered() -> None:
    """The permanent-pending trap, measured rather than assumed.

    A job skipped by an `if:` still reports (`auto-merge`, `npm Security Audit`
    and `Ruby Gem Security Audit` all reported `skipped` on 8/8 sampled PRs, and
    GitHub accepts that). A workflow whose `pull_request` trigger has a `paths:`
    filter does not run at all on an unrelated PR, so the status never arrives.
    `Validate action pin consistency` was absent from 4 of those 8 PRs for
    exactly that reason.
    """
    offenders = [
        f"{c} <- {f}:{j}"
        for c in rc.required_contexts()
        for f, j, filtered in rc.producers(c)
        if filtered
    ]
    assert offenders == [], (
        "\n".join(offenders) + "\n\nThese would leave unrelated PRs pending "
        "forever. Require a check that always reports, or remove the paths filter."
    )


def test_no_required_check_name_is_ambiguous() -> None:
    """Two jobs may not share a required name.

    Live example this rules out: `check-changes` is the job id in BOTH
    `jekyll.yml` and `security-audit.yml`, and both report under that one name.
    It is otherwise a good candidate — always runs, no paths filter — but
    nothing can say which one satisfied the requirement, so it is excluded.
    """
    ambiguous = {
        c: [f"{f}:{j}" for f, j, _ in rc.producers(c)]
        for c in rc.required_contexts()
        if len(rc.producers(c)) > 1
    }
    assert ambiguous == {}, (
        f"{ambiguous} — name matching cannot disambiguate. Rename one job."
    )


def test_actions_bot_keeps_its_bypass() -> None:
    """Without it the daily digest stops publishing.

    Four workflows push straight to main with `secrets.GITHUB_TOKEN` —
    ai-blogwatcher, generate-images, vercel-firewall-backup,
    visual-baseline-refresh — and a required status check rejects a direct push.
    The bypass is the only reason enforcement and the publishing pipeline
    coexist. Removing it is a valid decision ONLY together with converting those
    crons to pull requests.
    """
    actors = rc.declared().get("bypass_actors") or []
    assert any(
        a.get("actor_id") == rc.ACTIONS_APP_ID and a.get("actor_type") == "Integration"
        for a in actors
    ), (
        f"the GitHub Actions app (id {rc.ACTIONS_APP_ID}) lost its bypass. "
        "Check whether the four direct-push crons still exist before merging this."
    )


def test_strict_policy_stays_off() -> None:
    """`strict` forces every branch up to date, which #735 has history with.

    Auto-merge false-reds were traced partly to rebases leaving sibling runs
    deadlocked. Turning this on re-introduces mandatory rebases.
    """
    params = next(
        r["parameters"]
        for r in rc.declared()["rules"]
        if r["type"] == "required_status_checks"
    )
    assert not params.get("strict_required_status_checks_policy"), (
        "strict_required_status_checks_policy is on. Re-measure the #735 "
        "auto-merge deadlock before keeping it."
    )


def test_external_exceptions_state_their_removal_condition() -> None:
    """An exception without an exit condition is a permanent hole.

    These two are riskier than workflow-backed checks: if the app is
    uninstalled, the context stops being produced and all PRs block. The reason
    string has to say that.
    """
    vague = sorted(n for n, why in rc.EXTERNAL_CHECKS.items() if len(why) < 60)
    assert vague == [], (
        f"{vague} are exempted as external with a reason too short to act on. "
        "Say which app produces it and what to do when the app goes away."
    )


def test_per_language_codeql_checks_are_not_required() -> None:
    """Require the `CodeQL` aggregate, never `Analyze (<language>)`.

    The per-language names track the detected language list. Dropping Ruby from
    the repo would stop producing `Analyze (ruby)` and block every PR — A-H3
    again, pointed at the merge queue. Measured 2026-09-18: `CodeQL` comes from
    the `github-advanced-security` app and carries the real verdict ("No new
    alerts in code changed by this pull request"), so the aggregate loses
    nothing.
    """
    per_language = [c for c in rc.required_contexts() if c.startswith("Analyze (")]
    assert per_language == [], (
        f"{per_language} are required. Use the `CodeQL` aggregate instead — these "
        "names disappear when a language does."
    )
    assert "CodeQL" in rc.required_contexts(), (
        "The CodeQL aggregate is no longer required. If Advanced Security default "
        "setup was turned off, remove it from the ruleset in the same change."
    )


@pytest.mark.parametrize(
    "weird", ["x" * 200, "ctx\nwith-newline", "$(whoami)", "a;rm -rf /"]
)
def test_context_names_are_sanitized_before_printing(weird: str) -> None:
    """Contexts reach stdout, and this runs on a public repo's CI."""
    assert rc._safe(weird) == "<redacted>"


@pytest.mark.parametrize(
    "real", ["ruff", "build", "Security Audit Summary", "CodeQL", "Analyze (python)"]
)
def test_real_context_names_survive_the_sanitizer(real: str) -> None:
    """Not vacuous — a redact-everything version would make messages useless."""
    assert rc._safe(real) == real


def test_the_ruleset_file_says_it_is_not_applied() -> None:
    """JSON 만 읽는 사람이 그대로 POST 하지 않도록.

    이 파일은 선언이지 설정이다 — 2026-09-18 에 머지되고 나흘 동안 "적용 대기" 로
    오해된 채 남아 있었고, 실제로는 적용이 **불가능**했다(bypass_actors 가 조직 소유
    저장소 전용). JSON 은 주석을 지원하지 않으므로 `_comment` 키로 싣는다.

    GitHub 에 보낼 때는 `jq 'del(._comment)'` 로 걷어낸다 — README 의 명령이 그렇게
    되어 있다. 계약 검사기는 이 키를 무시한다(추가해도 18건 그대로 통과).

    이 단언이 깨진다면 누군가 경고를 지운 것이다. 지우기 전에
    `.github/rulesets/README.md` 와 `docs/troubleshooting/GITHUB_ACCOUNT_TYPE_GATES.md`
    를 먼저 반박하라.
    """
    data = json.loads(rc.RULESET.read_text(encoding="utf-8"))
    comment = data.get("_comment", "")
    assert comment, (
        "ruleset JSON 에서 `_comment` 가 사라졌다. 이 파일은 적용할 수 없는데도 "
        "적용 가능한 설정처럼 읽힌다 — 그 오해로 나흘을 썼다."
    )
    for token in ("README.md", "owner.type=User", "del(._comment)"):
        assert token in comment, (
            f"`_comment` 가 {token!r} 를 더 이상 가리키지 않는다. 사유·근거·적용 "
            "방법 중 하나가 빠지면 다음 사람이 다시 추측하게 된다."
        )
