#!/usr/bin/env python3
"""CI regression guard: five gates that used to pass without checking anything.

Found by the 2026-08-10 CI gate audit. Each of these reported a green tick while
verifying nothing, which is worse than a missing gate — a missing gate is visible.

D1  lighthouse-ci.yml — when either Jekyll build fails the run falls back to GH Pages,
    which writes head-side LHRs only. The intersection in compare() is then empty,
    no row is judged, and the script exits 0. That soft degrade is deliberate
    (security fix C-H1: a Vercel block must not hold a PR hostage) and stays. What
    was not deliberate is that it looked identical to a clean pass. The empty case is
    now always announced, and --require-comparable (passed only when BOTH builds
    succeeded) turns it into a failure, because then emptiness means URL resolution
    broke rather than the run degraded.

D2  check-svg.yml — ran `check_svg_quality.py --fix --ci`, repairing missing
    width/height in the CI workspace and only then asserting. Nothing commits the
    repair, so the regression class could never surface.

D3  check-svg.yml — `check_posts.py 2>&1 || true` then grepped two literal strings. A
    traceback or a renamed message yielded TOTAL=0 under a step named "zero SVG
    warnings".

D5  security-audit.yml — the summary compared needs.*.result to "failure" only and
    printed "clean (or skipped)". Measured: both audits `skipped` on 100% of the last
    30 PRs while this job reported success on all 30. Skipped still passes (the Monday
    cron audits unconditionally), but it must not read as clean.

D18 font-drift-gate.yml — the override label was matched with an unanchored
    `grep -q`, so any label containing the text bypassed the gate, and because the
    bypass gated steps rather than the job, an overridden run reported SUCCESS.

Direction: these assert the ABSENCE of the old shapes and the PRESENCE of the new
ones. Reintroducing `--fix` in CI, `|| true` around the script, the substring label
match, or the failure-only comparison trips this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CHECK_SVG = WORKFLOWS / "check-svg.yml"
SECURITY_AUDIT = WORKFLOWS / "security-audit.yml"
FONT_DRIFT = WORKFLOWS / "font-drift-gate.yml"
LIGHTHOUSE_CI = WORKFLOWS / "lighthouse-ci.yml"
COMPARE_SCRIPT = REPO_ROOT / "scripts" / "dev" / "compare_lighthouse_runs.py"


def _body(path: Path) -> str:
    """File text with comment-only lines dropped.

    Every file below documents the anti-pattern it removed, naming `--fix`,
    `|| true` and `grep -q 'font-drift-allowed'` in prose. Matching that commentary
    would keep this guard green after the real YAML came back.
    """
    return "\n".join(
        ln for ln in path.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#")
    )


# ---------------------------------------------------------------------------
# D1 — the perf gate must not render "measured nothing" as a plain pass
# ---------------------------------------------------------------------------


def test_compare_script_supports_require_comparable():
    src = COMPARE_SCRIPT.read_text(encoding="utf-8")
    assert "--require-comparable" in src, "compare_lighthouse_runs.py lost the --require-comparable flag"
    assert "require_comparable" in src


def test_empty_comparison_is_always_announced():
    """Silent green was the defect; the annotation is the fix."""
    src = COMPARE_SCRIPT.read_text(encoding="utf-8")
    assert "::warning::" in src, (
        "the degraded (no comparable URLs) path no longer emits a ::warning::, so a run "
        "that measured nothing is again indistinguishable from a clean pass"
    )
    assert "::error::" in src, "the --require-comparable failure path lost its ::error:: annotation"


def test_workflow_passes_require_comparable_only_when_both_builds_succeeded():
    body = _body(LIGHTHOUSE_CI)
    assert "--require-comparable" in body or "$REQUIRE" in body, (
        "lighthouse-ci.yml no longer wires --require-comparable; an empty comparison "
        "with two healthy builds would pass again"
    )
    assert "steps.build-head.outcome" in body and "steps.build-base.outcome" in body, (
        "the flag must be conditioned on both build outcomes — passing it "
        "unconditionally would fail every legitimate GH Pages fallback run"
    )


def test_compare_exit_codes_for_empty_input(tmp_path):
    """Behavioural check, not a text match: run the script on empty dirs both ways."""
    import subprocess
    import sys

    base = tmp_path / "base"
    head = tmp_path / "head"
    base.mkdir()
    head.mkdir()

    lenient = subprocess.run(
        [sys.executable, str(COMPARE_SCRIPT), "--base-dir", str(base), "--head-dir", str(head), "--quiet"],
        capture_output=True,
        text=True,
    )
    assert lenient.returncode == 0, "the soft-degrade path must stay exit 0 (security fix C-H1)"
    assert "::warning::" in lenient.stderr, "soft degrade must still be announced"

    strict = subprocess.run(
        [
            sys.executable, str(COMPARE_SCRIPT),
            "--base-dir", str(base), "--head-dir", str(head),
            "--quiet", "--require-comparable",
        ],
        capture_output=True,
        text=True,
    )
    assert strict.returncode == 1, "--require-comparable must fail when nothing is comparable"
    assert "::error::" in strict.stderr


# ---------------------------------------------------------------------------
# D2 / D3 — check-svg must not repair its own input, nor swallow a crash
# ---------------------------------------------------------------------------


def test_svg_quality_gate_does_not_self_repair_in_ci():
    body = _body(CHECK_SVG)
    assert not re.search(r"check_svg_quality\.py\s+--fix", body), (
        "check-svg.yml runs check_svg_quality.py with --fix again. In CI that rewrites "
        "the files before asserting on them, so the missing-dimensions regression class "
        "can never fail. Repair locally instead."
    )
    assert re.search(r"check_svg_quality\.py\s+--ci\s+assets/images/", body), (
        "the read-only corpus check is gone from check-svg.yml"
    )


def test_check_posts_exit_code_is_not_swallowed():
    body = _body(CHECK_SVG)
    assert not re.search(r"check_posts\.py[^\n]*\|\|\s*true", body), (
        "check_posts.py is wrapped in '|| true' again — a traceback would then yield "
        "TOTAL=0 and pass under the step name 'zero SVG warnings'"
    )
    assert "check_posts.py" in body, "the check_posts.py step disappeared entirely"


def test_check_posts_step_fails_on_nonzero_exit():
    body = _body(CHECK_SVG)
    step = body[body.index("Check posts quality") :]
    step = step[: step.find("\n      - name:") if "\n      - name:" in step else len(step)]
    assert "if ! OUTPUT=$(python3 scripts/check_posts.py 2>&1); then" in step, (
        "the step must branch on check_posts.py's own exit code before trusting its stdout"
    )
    assert "exit 1" in step


# ---------------------------------------------------------------------------
# D5 — "skipped" must not print as "clean"
# ---------------------------------------------------------------------------


def test_security_summary_does_not_call_skipped_clean():
    body = _body(SECURITY_AUDIT)
    assert "Security audit clean (or skipped" not in body, (
        "the summary again prints 'clean (or skipped)'. Both audits are skipped on "
        "every PR that does not touch a dependency manifest (30/30 measured), so this "
        "wording made a never-executed audit read as a clean bill of health."
    )
    assert "NOT RUN" in body, "the skipped case must be labelled as not-run"


def test_security_summary_rejects_unexpected_conclusions():
    """A failure-only equality test lets cancelled/timed_out fall through as success."""
    body = _body(SECURITY_AUDIT)
    assert not re.search(r'if\s+\[\s+"\$NPM"\s+=\s+"failure"\s+\]\s+\|\|\s+\[\s+"\$BUNDLE"\s+=\s+"failure"\s+\]', body), (
        "the summary is back to comparing only against 'failure'; cancelled and "
        "timed_out would pass"
    )
    assert "success|skipped)" in body, (
        "expected an allow-list of acceptable conclusions rather than a deny-list of one"
    )


@pytest.mark.parametrize("manifest", ["package.json", "package-lock.json", "Gemfile", "Gemfile.lock"])
def test_audit_trigger_manifests_still_filtered(manifest: str):
    """Canary on the premise of D5: the audits really are manifest-gated."""
    assert f"'{manifest}'" in _body(SECURITY_AUDIT), (
        f"{manifest} is no longer in the should-audit filter; if the audits now run on "
        "every PR, the skipped-vs-clean distinction this guard protects is moot and the "
        "guard should be revisited."
    )


# ---------------------------------------------------------------------------
# D18 — the font-drift bypass must be exact and must render as a skip
# ---------------------------------------------------------------------------


def test_font_drift_override_is_not_a_substring_match():
    body = _body(FONT_DRIFT)
    assert "grep -q 'font-drift-allowed'" not in body, (
        "the override is matched with an unanchored grep again: any label containing "
        "'font-drift-allowed' (e.g. 'not-font-drift-allowed') would disable the gate"
    )
    assert "contains(github.event.pull_request.labels.*.name, 'font-drift-allowed')" in body, (
        "expected an exact element match over the label array"
    )


def test_font_drift_override_skips_the_job_not_the_steps():
    """A step-gated bypass reports SUCCESS; a job-level `if` renders grey."""
    import yaml

    parsed = yaml.safe_load(FONT_DRIFT.read_text(encoding="utf-8"))
    job = parsed["jobs"]["font-drift"]
    assert "if" in job, (
        "font-drift has no job-level 'if'. With the bypass at step level an overridden "
        "run reports SUCCESS having checked nothing — a green tick that looks like a pass."
    )
    assert "font-drift-allowed" in job["if"]

    body = _body(FONT_DRIFT)
    assert "label-check" not in body, (
        "the old in-job label-check step is back; the bypass belongs in the job's 'if'"
    )
    assert "steps.label-check.outputs.skip" not in body


def test_font_drift_still_runs_the_gate_script():
    body = _body(FONT_DRIFT)
    assert "scripts/dev/check_font_drift.py" in body, "the gate no longer invokes its own script"
    assert "CHANGED_FILES" in body, "the env-passing hardening (security fix M-01) was dropped"
