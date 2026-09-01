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
* one absolute metric budget -- CLS -- is read from the LHR at ``jsonPath``
  rather than from ``manifest.summary``, which only carries category scores,
* LCP is measured and LOGGED but deliberately NOT gated, because it is bimodal
  on this runner for reasons CI does not control (see
  :meth:`TestLighthouseGateConfig.test_lcp_stays_observable_but_ungated`),
* the ``pull_request`` trigger got the same ``paths`` filter the ``push``
  trigger already had, so content-only PRs stop running Lighthouse at all.

Each of those can be undone silently: raise the CLS budget "just a little", drop
a category threshold, delete the paths filter, drop the LCP log line that is the
evidence trail for re-deriving a budget, or refactor the check step so the budget
constants are still there but nothing reads ``jsonPath`` any more (a vacuous
gate). This guard makes any of that fail loudly and reviewably.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control) / NIST SSDF PW.4.

Direction
---------
* Category thresholds are FLOORS -> asserted ``>=`` (raising them stays green).
* The CLS budget is a CEILING -> asserted ``<=`` (tightening stays green,
  loosening trips).
* The paths filter, the jsonPath wiring and the LCP log line are PRESENCE
  assertions. The LCP *budget* is an ABSENCE assertion.

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

# Direction: ceiling. Loosening (raising) must fail.
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
    body: list[str] = []
    for ln in lines[start + 1 :]:
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

    def test_cls_budget_not_loosened(self):
        code = _uncommented(_check_script(_workflow()))
        cls = re.search(r"'cumulative-layout-shift':\s*\{\s*max:\s*([\d.]+)", code)
        assert cls, (
            "the cumulative-layout-shift budget was removed. CLS is the one "
            "metric that is stable on this runner (0.000-0.014 across 60 runs), "
            "so it is the only absolute budget the gate can carry."
        )
        assert float(cls.group(1)) <= MAX_CLS, (
            f"the CLS budget was raised to {cls.group(1)} (ceiling: {MAX_CLS}). "
            "Measured CLS never exceeded 0.014 over 60 runs, so a raise means "
            "something regressed. If intentional, update this guard."
        )

    def test_lcp_stays_observable_but_ungated(self):
        """LCP must be LOGGED, and must NOT be a budget.

        Why LCP is not gated: it is bimodal on this runner and the split is not
        caused by anything CI controls. Over 60 real runs of this workflow, 55
        measured 4218-4373ms and 5 measured 6921-9695ms. Runs `31150603094` and
        `31151236111` have the same observed FCP (147ms) and effectively the same
        benchmarkIndex (3294 vs 3293), yet simulate 4297ms vs 9693ms — a 5396ms
        gap produced entirely inside Lighthouse's Lantern simulation of a ~1.66MB
        page over the mobile preset. A warm-cache prerun does not address it:
        outliers skew toward the FASTEST runners (median benchmarkIndex 3293 vs
        2250) and the fastest observed loads (median observed FCP 176ms vs
        1335ms), which is the opposite of a cold-start signature. Any budget
        placed between the two modes reds ~8.3% of runs while catching nothing.

        Why it must still be logged: these job-log values are the only running
        record of LCP once the gate stops asserting it. Reducing the page's
        transfer weight is the real fix, and re-deriving a budget afterwards
        needs this data. If the log line goes, the evidence trail goes with it.

        Direction: presence assertions on BOTH sides — the log must exist, and
        LCP must not reappear in METRIC_BUDGETS without a fresh measurement.
        """
        code = _uncommented(_check_script(_workflow()))
        assert re.search(r"audits\['largest-contentful-paint'\]", code), (
            "largest-contentful-paint is no longer read from the LHR, so it can "
            "no longer be logged. That log is the only record from which an LCP "
            "budget can be recomputed after transfer weight comes down."
        )
        assert re.search(
            r"\[observed, not gated\][^\n]*largest-contentful-paint"
            r"|largest-contentful-paint:\s*\$\{typeof lcp",
            code,
        ), (
            "largest-contentful-paint dropped out of the '[observed, not gated]' "
            "log line. Keep it: it is the evidence trail for re-deriving the "
            "budget later."
        )
        assert not re.search(r"'largest-contentful-paint':\s*\{\s*max:", code), (
            "an LCP budget was re-added to METRIC_BUDGETS. LCP is bimodal on "
            "this runner (55/60 runs 4218-4373ms, 5/60 runs 6921-9695ms with "
            "identical observed inputs), so a budget between the modes reds "
            "~8.3% of runs for no signal. Re-add one only with a fresh "
            "measurement showing the bimodality is gone — and update this guard "
            "in the same PR."
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

    def test_empty_manifest_fails_closed(self):
        """An empty manifest must not report success.

        The gates all live inside ``for (const result of manifest)``. With an
        empty manifest that loop body never runs, so without an explicit
        length check the step prints "All Lighthouse thresholds met." and exits
        0 on a run that measured nothing at all.
        """
        code = _uncommented(_check_script(_workflow()))
        assert re.search(r"manifest\.length\s*===?\s*0", code), (
            "the empty-manifest fail-closed check was removed; a Lighthouse run "
            "that produced no manifest would pass the gate green while asserting "
            "nothing. If intentional, update this guard."
        )

    def test_step_not_neutralized(self):
        step = _check_step(_workflow())
        assert step.get("continue-on-error") is not True, (
            "the check step is marked continue-on-error; a FAIL would no longer "
            "block the job."
        )
        assert "|| true" not in step.get("run", ""), (
            "the check step is neutralised with '|| true'; a FAIL would be swallowed."
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
        "largest-contentful-paint": {
            "numericValue": 4298.2,
            "numericUnit": "millisecond",
        },
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
        manifest = [
            {
                "url": lhr["requestedUrl"],
                "isRepresentativeRun": True,
                "htmlPath": str(Path(tmp) / "lhr-1.html"),
                "jsonPath": str(lhr_path),
                "summary": summary,
            }
        ]
        return subprocess.run(
            ["node", "-"],
            input=script,
            capture_output=True,
            text=True,
            env={
                "PATH": __import__("os").environ["PATH"],
                "LIGHTHOUSE_MANIFEST": json.dumps(manifest),
            },
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
        assert "largest-contentful-paint: 4298ms" in r.stdout, (
            "LCP must appear in the observability log even though it is not "
            f"gated:\n{r.stdout}"
        )

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

    def test_lcp_outlier_is_logged_but_does_not_fail(self):
        """LCP is observability, not a gate.

        9693ms is the real value measured on run 31151236111, whose observed
        inputs were indistinguishable from the passing run 31150603094. It must
        be visible in the log and must NOT red the build.
        """
        r = _run_gate(_mutate(largest_contentful_paint=9693.3), _GOOD_SUMMARY)
        assert r.returncode == 0, (
            "the LCP outlier failed the gate — LCP is bimodal on this runner and "
            f"is intentionally ungated:\n{r.stdout}\n{r.stderr}"
        )
        assert "largest-contentful-paint: 9693ms" in r.stdout, (
            f"the outlier value was not logged:\n{r.stdout}"
        )
        assert "[FAIL]" not in r.stdout, r.stdout

    def test_cls_over_budget_fails(self):
        r = _run_gate(_mutate(cumulative_layout_shift=0.21), _GOOD_SUMMARY)
        assert r.returncode == 1, f"CLS 0.21 was not caught:\n{r.stdout}"
        assert "cumulative-layout-shift: 0.210" in r.stdout

    def test_category_regression_fails(self):
        r = _run_gate(_GOOD_LHR, dict(_GOOD_SUMMARY, accessibility=0.5))
        assert r.returncode == 1, f"accessibility 0.50 was not caught:\n{r.stdout}"

    def test_empty_manifest_exits_nonzero(self):
        script = _check_script(_workflow())
        r = subprocess.run(
            ["node", "-"],
            input=script,
            capture_output=True,
            text=True,
            env={"PATH": __import__("os").environ["PATH"], "LIGHTHOUSE_MANIFEST": "[]"},
        )
        assert r.returncode == 1, (
            "an empty manifest passed the gate — the step would report success "
            f"having asserted nothing:\n{r.stdout}\n{r.stderr}"
        )
        assert "All Lighthouse thresholds met." not in r.stdout

    def test_absent_manifest_env_exits_nonzero(self):
        """The action sets `manifest` to '' when it produced no manifest.json."""
        script = _check_script(_workflow())
        r = subprocess.run(
            ["node", "-"],
            input=script,
            capture_output=True,
            text=True,
            env={"PATH": __import__("os").environ["PATH"], "LIGHTHOUSE_MANIFEST": ""},
        )
        assert r.returncode == 1, (
            f"an empty LIGHTHOUSE_MANIFEST passed the gate:\n{r.stdout}\n{r.stderr}"
        )

    def test_unreadable_lhr_fails_closed(self):
        """A missing LHR must not silently pass the metric budgets."""
        script = _check_script(_workflow())
        manifest = [
            {
                "url": "http://localhost:4000/",
                "isRepresentativeRun": True,
                "htmlPath": "/nonexistent/lhr-1.html",
                "jsonPath": "/nonexistent/lhr-1.json",
                "summary": _GOOD_SUMMARY,
            }
        ]
        r = subprocess.run(
            ["node", "-"],
            input=script,
            capture_output=True,
            text=True,
            env={
                "PATH": __import__("os").environ["PATH"],
                "LIGHTHOUSE_MANIFEST": json.dumps(manifest),
            },
        )
        assert r.returncode == 1, (
            "an unreadable LHR passed the gate — the metric budgets would be "
            f"silently skipped:\n{r.stdout}\n{r.stderr}"
        )
