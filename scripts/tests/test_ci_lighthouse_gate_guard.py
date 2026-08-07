#!/usr/bin/env python3
"""CI regression guard: the Lighthouse gate must stay metric-based and scoped.

Why this guard exists
---------------------
``.github/workflows/lighthouse.yml`` used to gate on the composite
``performance`` category score with a 0.5 floor. That score is ~30% weighted on
total-blocking-time, and TBT on a GitHub runner is decided by the CPU the VM
lottery hands out. Measured over 60 real runs of this workflow (artifacts
downloaded from ``lighthouse-results``): benchmarkIndex 1966-3439, TBT
0-2452 ms, performance 0.55-0.86 -- on unchanged content. One run scored 30 and
went red (run 29005388708, 2026-07-09). Meanwhile accessibility / best-practices
/ seo did not move at all, and CLS never exceeded 0.014.

So the gate was rebuilt around things that actually mean something:

* the composite ``performance`` floor is GONE (it was measuring the runner),
* ``accessibility`` / ``best-practices`` / ``seo`` stay blocking,
* absolute metric budgets (LCP, CLS) are read from the LHR at ``jsonPath``
  -- NOT from ``manifest.summary``, which only carries category scores,
* the ``pull_request`` trigger got the same ``paths`` filter the ``push``
  trigger already had, so content-only PRs stop running Lighthouse at all.

Each of those can be undone silently: raise a budget "just a little", drop a
category threshold, delete the paths filter, or refactor the check step so the
budget constants are still there but nothing reads ``jsonPath`` any more (a
vacuous gate). This guard makes any of that fail loudly and reviewably.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control) / NIST SSDF PW.4.

Direction
---------
* Category thresholds are FLOORS -> asserted ``>=`` (raising them stays green).
* Metric budgets are CEILINGS -> asserted ``<=`` (tightening stays green,
  loosening trips).
* The paths filter and the jsonPath wiring are PRESENCE assertions.

If a change here is intentional, update this guard in the same PR and say why.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "lighthouse.yml"

# Direction: ceilings. Loosening (raising) must fail.
MAX_LCP_MS = 4600
MAX_CLS = 0.05
# Direction: floors. Weakening (lowering) must fail.
MIN_CATEGORY_SCORES = {
    "accessibility": 0.8,
    "best-practices": 0.75,
    "seo": 0.9,
}


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _triggers(wf: dict) -> dict:
    """The ``on:`` mapping.

    PyYAML resolves the bare key ``on`` to the boolean ``True`` (YAML 1.1
    truthiness), so ``wf["on"]`` is not reliable -- look both up.
    """
    return wf.get("on") or wf.get(True) or {}


def _check_step(wf: dict) -> dict:
    steps = wf["jobs"]["lighthouse"]["steps"]
    for step in steps:
        if step.get("name") == "Check Lighthouse scores":
            return step
    return {}


def _check_script(wf: dict) -> str:
    """The JS between ``node - <<'EOF'`` and its terminator.

    Returned verbatim as the shell would feed it to node's stdin, so the tests
    below execute the code that actually ships rather than a copy of it.
    """
    run = _check_step(wf).get("run", "")
    lines = run.splitlines()
    start = next(
        (i for i, ln in enumerate(lines) if re.match(r"\s*node\s+-\s+<<'EOF'\s*$", ln)),
        None,
    )
    if start is None:
        return ""
    body = []
    for ln in lines[start + 1:]:
        if ln.strip() == "EOF":
            return "\n".join(body)
        body.append(ln)
    return ""


def _uncommented(script: str) -> str:
    """Script with ``//`` comment-only lines dropped.

    The check step's comments legitimately MENTION ``performance``, ``jsonPath``
    and the budget numbers; asserting on the raw text would let the executable
    code be gutted while stale prose kept this guard green.
    """
    return "\n".join(
        ln for ln in script.splitlines() if not ln.lstrip().startswith("//")
    )


# --------------------------------------------------------------------------
# Static invariants
# --------------------------------------------------------------------------


class TestLighthouseGateConfig:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_pull_request_has_paths_filter(self):
        pr = _triggers(_workflow()).get("pull_request") or {}
        paths = pr.get("paths")
        assert paths, (
            "the pull_request trigger lost its 'paths' filter — every PR, "
            "including content-only _posts/** PRs that cannot move any measured "
            "metric, would run Lighthouse again. If intentional, update this guard."
        )

    def test_pull_request_paths_match_push_paths(self):
        on = _triggers(_workflow())
        push_paths = (on.get("push") or {}).get("paths") or []
        pr_paths = (on.get("pull_request") or {}).get("paths") or []
        assert push_paths, "the push trigger lost its 'paths' filter"
        assert sorted(pr_paths) == sorted(push_paths), (
            "pull_request and push 'paths' filters diverged "
            f"(push={sorted(push_paths)}, pull_request={sorted(pr_paths)}). "
            "They must stay identical so a PR is gated on exactly what a push "
            "to main is gated on. If intentional, update this guard."
        )

    def test_check_step_present(self):
        assert _check_script(_workflow()), (
            "the 'Check Lighthouse scores' step (or its node heredoc) "
            "disappeared — nothing enforces any Lighthouse result any more."
        )

    def test_composite_performance_is_not_a_gate(self):
        code = _uncommented(_check_script(_workflow()))
        assert not re.search(r"^\s*performance:\s*0?\.\d", code, re.M), (
            "a numeric 'performance:' threshold came back. The composite "
            "performance score is ~30% TBT and swings 0.55-0.86 on unchanged "
            "content across GitHub runners; gating on it is what caused the "
            "random red this workflow was fixed for."
        )

    def test_category_floors_not_weakened(self):
        code = _uncommented(_check_script(_workflow()))
        for category, floor in MIN_CATEGORY_SCORES.items():
            key = f"'{category}'" if "-" in category else category
            m = re.search(rf"^\s*{re.escape(key)}:\s*([\d.]+),", code, re.M)
            assert m, (
                f"the '{category}' category threshold was removed from "
                "CATEGORY_THRESHOLDS; it is stable across runners and costs "
                "nothing to keep blocking."
            )
            assert float(m.group(1)) >= floor, (
                f"the '{category}' threshold was lowered to {m.group(1)} "
                f"(floor: {floor}). Raising is fine; lowering silently weakens "
                "the gate. If intentional, update this guard."
            )

    def test_metric_budgets_not_loosened(self):
        code = _uncommented(_check_script(_workflow()))
        lcp = re.search(
            r"'largest-contentful-paint':\s*\{\s*max:\s*([\d.]+)", code
        )
        cls = re.search(
            r"'cumulative-layout-shift':\s*\{\s*max:\s*([\d.]+)", code
        )
        assert lcp, "the largest-contentful-paint budget was removed"
        assert cls, "the cumulative-layout-shift budget was removed"
        assert float(lcp.group(1)) <= MAX_LCP_MS, (
            f"the LCP budget was raised to {lcp.group(1)}ms (ceiling: "
            f"{MAX_LCP_MS}ms). Raising it is how this gate stops catching a real "
            "regression. If intentional, update this guard and say why."
        )
        assert float(cls.group(1)) <= MAX_CLS, (
            f"the CLS budget was raised to {cls.group(1)} (ceiling: {MAX_CLS}). "
            "Measured CLS never exceeded 0.014 over 60 runs, so a raise means "
            "something regressed. If intentional, update this guard."
        )

    def test_budgets_are_read_from_the_lhr(self):
        """Budgets must be evaluated, not merely declared.

        ``manifest.summary`` carries CATEGORY scores only (see @lhci/cli
        ``runFilesystemTarget``); metric values exist only in the LHR written to
        ``jsonPath``. A refactor that keeps METRIC_BUDGETS but stops reading the
        LHR would leave the constants in place and enforce nothing.
        """
        code = _uncommented(_check_script(_workflow()))
        # Assert on the READ expression, not the bare identifier: 'jsonPath'
        # also appears in the failure message, so a substring check would still
        # pass after the readFileSync call was removed.
        assert re.search(r"readFileSync\(\s*result\.jsonPath", code), (
            "the check step no longer reads result.jsonPath — metric budgets "
            "cannot be evaluated from manifest.summary (category scores only), "
            "so the LCP/CLS budgets would be dead constants."
        )
        assert "numericValue" in code, (
            "the check step no longer reads audit numericValue; the metric "
            "budgets are not actually compared against anything."
        )

    def test_observability_fields_logged(self):
        code = _uncommented(_check_script(_workflow()))
        for field in ("total-blocking-time", "benchmarkIndex"):
            assert field in code, (
                f"'{field}' is no longer logged. It is not a gate, but without "
                "it a red build cannot be triaged as slow-runner vs real "
                "regression from the job log alone."
            )

    def test_step_not_neutralized(self):
        step = _check_step(_workflow())
        assert step.get("continue-on-error") is not True, (
            "the check step is marked continue-on-error; a FAIL would no longer "
            "block the job."
        )
        assert "|| true" not in step.get("run", ""), (
            "the check step is neutralised with '|| true'; a FAIL would be "
            "swallowed."
        )


# --------------------------------------------------------------------------
# Behavioural verification: run the shipped script against LHR-shaped fixtures
# --------------------------------------------------------------------------

# Shaped after a real LHR downloaded from this workflow's own
# `lighthouse-results` artifact (run 31068899103): mobile preset, simulate
# throttling, lighthouse 12.6.1.
_GOOD_LHR = {
    "requestedUrl": "http://localhost:4000/",
    "environment": {"benchmarkIndex": 2180},
    "categories": {"performance": {"score": 0.64}},
    "audits": {
        "largest-contentful-paint": {"numericValue": 4298.2, "numericUnit": "millisecond"},
        "cumulative-layout-shift": {"numericValue": 0.0, "numericUnit": "unitless"},
        "total-blocking-time": {"numericValue": 671.7, "numericUnit": "millisecond"},
    },
}
_GOOD_SUMMARY = {
    "performance": 0.64,
    "accessibility": 0.97,
    "best-practices": 1,
    "seo": 1,
}


def _run_gate(lhr: dict, summary: dict) -> subprocess.CompletedProcess:
    """Execute the workflow's own check script over one manifest entry."""
    script = _check_script(_workflow())
    assert script, "could not extract the check script from the workflow"
    with tempfile.TemporaryDirectory() as tmp:
        lhr_path = Path(tmp) / "lhr-1.json"
        lhr_path.write_text(json.dumps(lhr), encoding="utf-8")
        manifest = [{
            "url": lhr["requestedUrl"],
            "isRepresentativeRun": True,
            "htmlPath": str(Path(tmp) / "lhr-1.html"),
            "jsonPath": str(lhr_path),
            "summary": summary,
        }]
        return subprocess.run(
            ["node", "-"],
            input=script,
            capture_output=True,
            text=True,
            env={"PATH": __import__("os").environ["PATH"],
                 "LIGHTHOUSE_MANIFEST": json.dumps(manifest)},
        )


def _mutate(**audits) -> dict:
    lhr = json.loads(json.dumps(_GOOD_LHR))
    for audit_id, value in audits.items():
        lhr["audits"][audit_id.replace("_", "-")]["numericValue"] = value
    return lhr


pytestmark = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node is not on PATH; the check script cannot be executed here",
)


class TestLighthouseGateBehaviour:
    def test_passes_on_a_healthy_run(self):
        r = _run_gate(_GOOD_LHR, _GOOD_SUMMARY)
        assert r.returncode == 0, f"gate failed a healthy run:\n{r.stdout}\n{r.stderr}"
        assert "All Lighthouse thresholds met." in r.stdout

    def test_logs_observability_fields(self):
        r = _run_gate(_GOOD_LHR, _GOOD_SUMMARY)
        assert "benchmarkIndex: 2180" in r.stdout, r.stdout
        assert "total-blocking-time: 672ms" in r.stdout, r.stdout
        assert "performance: 64" in r.stdout, r.stdout

    def test_high_tbt_alone_does_not_fail(self):
        """The exact regression this rework targets.

        Run 31150566340 measured TBT 1825ms / performance 0.57 on unchanged
        content. Under the old composite gate that trended toward red; it must
        now pass, because LCP and CLS were both fine.
        """
        lhr = _mutate(total_blocking_time=1824.5)
        summary = dict(_GOOD_SUMMARY, performance=0.30)
        r = _run_gate(lhr, summary)
        assert r.returncode == 0, (
            "a slow-CPU run (high TBT, low composite performance) still fails "
            f"the gate:\n{r.stdout}\n{r.stderr}"
        )

    def test_lcp_over_budget_fails(self):
        # 9693ms — the real outlier measured on run 31151236111.
        r = _run_gate(_mutate(largest_contentful_paint=9693.3), _GOOD_SUMMARY)
        assert r.returncode == 1, f"LCP 9693ms was not caught:\n{r.stdout}"
        assert "largest-contentful-paint: 9693ms" in r.stdout
        assert "[FAIL]" in r.stdout

    def test_cls_over_budget_fails(self):
        r = _run_gate(_mutate(cumulative_layout_shift=0.21), _GOOD_SUMMARY)
        assert r.returncode == 1, f"CLS 0.21 was not caught:\n{r.stdout}"
        assert "cumulative-layout-shift: 0.210" in r.stdout

    def test_category_regression_fails(self):
        r = _run_gate(_GOOD_LHR, dict(_GOOD_SUMMARY, accessibility=0.5))
        assert r.returncode == 1, f"accessibility 0.50 was not caught:\n{r.stdout}"

    def test_unreadable_lhr_fails_closed(self):
        """A missing LHR must not silently pass the metric budgets."""
        script = _check_script(_workflow())
        manifest = [{
            "url": "http://localhost:4000/",
            "isRepresentativeRun": True,
            "htmlPath": "/nonexistent/lhr-1.html",
            "jsonPath": "/nonexistent/lhr-1.json",
            "summary": _GOOD_SUMMARY,
        }]
        r = subprocess.run(
            ["node", "-"],
            input=script,
            capture_output=True,
            text=True,
            env={"PATH": __import__("os").environ["PATH"],
                 "LIGHTHOUSE_MANIFEST": json.dumps(manifest)},
        )
        assert r.returncode == 1, (
            "an unreadable LHR passed the gate — the metric budgets would be "
            f"silently skipped:\n{r.stdout}\n{r.stderr}"
        )
