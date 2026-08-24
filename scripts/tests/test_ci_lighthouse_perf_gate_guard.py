#!/usr/bin/env python3
"""CI regression guard: the Lighthouse *perf gate* must keep measuring the diff.

Sibling of ``test_ci_lighthouse_gate_guard.py``, which guards the absolute
budgets in ``lighthouse.yml``. This one guards the head-vs-base LCP regression
gate in ``lighthouse-ci.yml``.

What can be undone silently here
--------------------------------
1. **Drop ``_posts/**`` from the trigger.** The gate goes back to never firing
   on the PRs this repo actually produces — 16 of the last 30 merged PRs touched
   ``_posts/**`` and 0 touched any other trigger path.
2. **Re-hard-code the measured post URL.** Before 2026-08-08 the gate always
   measured a fixed 2026-04-29 post. On a ``_posts/**`` PR that post is
   byte-identical on both sides, so the gate reports +0 ms and blocks nothing —
   green, and vacuous. The URL list must come from the resolver.
3. **Stop requiring the URL to exist in both builds.** The runs are served with
   ``serve … --single``, which answers an unknown path with the homepage at
   HTTP 200 and no redirect. Measure a head-only URL and the comparison pits a
   post page against the homepage; the delta is noise with a plausible sign.
   The existence check needs ``--site-dir`` for *both* builds and the local
   measurement steps need both builds to have succeeded.
4. **Raise the 200 ms threshold** or neutralise the compare step.
5. **Remove the post-URL cap**, turning a 100-post corpus PR into a 101-URL
   sweep — 100× the run time, on a 30-minute job timeout.

Direction
---------
* ``--threshold-lcp-ms`` and ``--max-post-urls`` are CEILINGS -> asserted ``<=``
  (tightening stays green, loosening trips).
* Trigger paths, the resolver call, the both-builds conditions and the
  ``--site-dir`` pair are PRESENCE assertions.
* The hard-coded post URL inside the measurement loops is an ABSENCE assertion.

If a change here is intentional, update this guard in the same PR and say why.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "lighthouse-ci.yml"
RESOLVER = REPO_ROOT / "scripts" / "dev" / "resolve_lighthouse_urls.py"

# Direction: ceiling. Loosening (raising) must fail.
MAX_THRESHOLD_LCP_MS = 200
MAX_POST_URL_CAP = 3

REQUIRED_TRIGGER_PATHS = {
    "_posts/**",
    "_includes/**",
    "_layouts/**",
    "assets/**",
    "scripts/dev/compare_lighthouse_runs.py",
    "scripts/dev/resolve_lighthouse_urls.py",
}


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _triggers(wf: dict) -> dict:
    """The ``on:`` mapping.

    PyYAML resolves the bare key ``on`` to the boolean ``True`` (YAML 1.1
    truthiness), so ``wf["on"]`` is not reliable -- look both up.
    """
    return wf.get("on") or wf.get(True) or {}


def _steps(wf: dict) -> list[dict]:
    return wf["jobs"]["lighthouse-perf-gate"]["steps"]


def _step(wf: dict, name: str) -> dict:
    for step in _steps(wf):
        if step.get("name") == name:
            return step
    return {}


def _measurement_steps(wf: dict) -> list[dict]:
    """Steps that record Lighthouse reports.

    Keyed on ``--output-path=`` rather than the bare ``lighthouse`` command so
    the install step (``lighthouse --version``) is not swept in.
    """
    return [s for s in _steps(wf) if "--output-path=" in s.get("run", "")]


class TestPerfGateConfig:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_resolver_exists(self):
        assert RESOLVER.is_file(), (
            f"{RESOLVER} not found — the workflow's 'Resolve measurement URLs' "
            "step would fail and the gate would measure nothing."
        )

    def test_trigger_paths_present(self):
        paths = set(
            (_triggers(_workflow()).get("pull_request") or {}).get("paths") or []
        )
        missing = REQUIRED_TRIGGER_PATHS - paths
        assert not missing, (
            f"the pull_request 'paths' filter lost {sorted(missing)}. "
            "Without '_posts/**' the gate never fires on this repo's PRs "
            "(16 of the last 30 merged PRs were content-only); without the "
            "script paths, a change to the gate's own logic is not self-tested. "
            "If intentional, update this guard."
        )

    def test_threshold_not_loosened(self):
        run = _step(_workflow(), "Compare LCP head vs base").get("run", "")
        m = re.search(r"--threshold-lcp-ms\s+(\d+)", run)
        assert m, "the --threshold-lcp-ms argument disappeared from the compare step."
        assert int(m.group(1)) <= MAX_THRESHOLD_LCP_MS, (
            f"the LCP regression threshold was raised to {m.group(1)} ms "
            f"(ceiling: {MAX_THRESHOLD_LCP_MS} ms). Tightening is fine; raising "
            "silently weakens the gate. If intentional, update this guard."
        )

    def test_compare_step_not_neutralized(self):
        step = _step(_workflow(), "Compare LCP head vs base")
        assert step, "the 'Compare LCP head vs base' step is gone — nothing gates."
        assert step.get("continue-on-error") is not True, (
            "the compare step is marked continue-on-error; a regression would no "
            "longer block the PR. It is already fail-safe by design (an "
            "incomparable base yields 'skip' and exit 0), so this flag only "
            "disables real failures."
        )
        assert "|| true" not in step.get("run", ""), (
            "the compare step is neutralised with '|| true'; a FAIL would be swallowed."
        )

    def test_urls_come_from_the_resolver(self):
        step = _step(_workflow(), "Resolve measurement URLs")
        run = step.get("run", "")
        assert "resolve_lighthouse_urls.py" in run, (
            "the 'Resolve measurement URLs' step no longer calls the resolver. "
            "A fixed URL list makes the gate vacuous on _posts/** PRs: the "
            "measured post is identical on both sides, so the delta is always "
            "+0 ms."
        )
        assert "--output lh-urls.txt" in run, (
            "the resolver no longer writes lh-urls.txt, which is what the "
            "measurement steps read."
        )

    def test_existence_is_checked_against_both_builds(self):
        run = _step(_workflow(), "Resolve measurement URLs").get("run", "")
        for site in ("_site_head", "_site_base"):
            assert f"--site-dir {site}" in run, (
                f"the resolver is no longer given --site-dir {site}. Both are "
                "required: a URL present in only one build gets served the "
                "homepage by 'serve --single' at HTTP 200, so the comparison "
                "would silently pit a post page against the homepage."
            )

    def test_post_url_cap_bounds_runtime(self):
        wf = _workflow()
        cap = wf.get("env", {}).get("MAX_POST_URLS")
        assert cap is not None, (
            "MAX_POST_URLS was removed. Without a cap, a corpus-wide PR (the "
            "last one touched 100 posts) sweeps one URL per post at ~3 min each "
            "and blows the 30-minute job timeout."
        )
        assert int(cap) <= MAX_POST_URL_CAP, (
            f"MAX_POST_URLS was raised to {cap} (ceiling: {MAX_POST_URL_CAP}). "
            "Each extra URL adds 12 Lighthouse runs (2 sides x [1 warm + 5 "
            "measured]). If intentional, update this guard."
        )
        assert "--max-post-urls" in _step(wf, "Resolve measurement URLs").get(
            "run", ""
        ), (
            "the cap is declared in env but no longer passed to the resolver — "
            "a dead constant."
        )

    def test_local_measurement_requires_both_builds(self):
        wf = _workflow()
        for name in (
            "Run Lighthouse on head (local build)",
            "Run Lighthouse on base (local build)",
        ):
            step = _step(wf, name)
            assert step, f"the '{name}' step is gone."
            condition = str(step.get("if", ""))
            for outcome in ("build-head", "build-base"):
                assert f"steps.{outcome}.outcome == 'success'" in condition, (
                    f"'{name}' no longer requires {outcome} to have succeeded "
                    f"(if: {condition!r}). With only one build present the URL "
                    "list is resolved without an existence check on the other "
                    "side, re-opening the 'serve --single' homepage-substitution "
                    "hazard."
                )

    def test_no_hardcoded_post_url_in_measurement_loops(self):
        """The resolver must be the only source of measured post URLs."""
        for step in _measurement_steps(_workflow()):
            run = step.get("run", "")
            assert "lh-urls.txt" in run, (
                f"the '{step.get('name')}' step measures URLs without reading "
                "lh-urls.txt, so it is not measuring what the PR changed."
            )
            hardcoded = re.findall(r"(?:localhost:4000|tech-blog)/posts/\S+", run)
            assert not hardcoded, (
                f"a post URL was hard-coded back into '{step.get('name')}': "
                f"{hardcoded}. On a _posts/** PR that page is identical on both "
                "sides, so the gate reports +0 ms and blocks nothing. The "
                "fallback URL belongs in the DEFAULT_POST_URL env var, which the "
                "resolver drops automatically once the post stops existing."
            )

    def test_server_cannot_drift_to_another_port(self):
        """The bug that made this gate vacuous for months.

        Head and base are served on :4000 in turn. ``npx serve`` answers a busy
        port by silently binding a RANDOM free one, while Lighthouse keeps
        requesting :4000 — so the second side measures the first side's build.
        Runs 31150717334 / 30882267998 / 30332794243 all logged ``Accepting
        connections at http://localhost:<random>`` for the base server: from
        PR #326 until 2026-08-08 this gate compared head against head, which is
        why every post-page row came back at ±2 ms.

        Two independent defences, because the failure is silent: refuse the
        fallback, and verify over HTTP which tree is actually being served.
        """
        wf = _workflow()
        ports = {}
        for side, name in (
            ("head", "Run Lighthouse on head (local build)"),
            ("base", "Run Lighthouse on base (local build)"),
        ):
            run = _step(wf, name).get("run", "")
            m = re.search(rf"npx serve _site_{side} -l (\d+)", run)
            assert m, f"'{name}' no longer starts a server for _site_{side}."
            ports[side] = m.group(1)
            measured = re.search(r'url="http://localhost:(\d+)\$\{path\}"', run)
            assert measured, (
                f"'{name}' no longer builds its measurement URL from a "
                "localhost port, so what it measures cannot be checked."
            )
            assert measured.group(1) == m.group(1), (
                f"'{name}' serves _site_{side} on :{m.group(1)} but measures "
                f":{measured.group(1)}. Lighthouse would hit whatever else is "
                "listening there — which is exactly how the base sweep came to "
                "re-measure the head build."
            )
        assert ports["head"] != ports["base"], (
            f"head and base are both served on :{ports['head']}. Sharing a port "
            "is the exact defect this gate shipped with: serve binds a random "
            "free port when the requested one is still held, Lighthouse keeps "
            "requesting the original, and the second side re-measures the first. "
            "Run 31244446805 showed a teardown-and-wait does not close it."
        )
        for name in (
            "Run Lighthouse on head (local build)",
            "Run Lighthouse on base (local build)",
        ):
            run = _step(wf, name).get("run", "")
            assert "--no-port-switching" in run, (
                f"'{name}' starts the server without --no-port-switching. On a "
                "busy port serve picks a random one instead of failing, and "
                "Lighthouse then measures whatever is still listening."
            )
            assert "build-id.txt" in run, (
                f"'{name}' no longer probes build-id.txt before measuring, so "
                "'the server on :4000 is serving the tree I think it is' is "
                "assumed rather than verified."
            )
            assert "pkill -P" in run, (
                f"'{name}' tears the server down by the npx wrapper PID alone; "
                "the listening child survives and holds :4000 for the next side."
            )

        stamp = _step(wf, "Stamp build identity into each site").get("run", "")
        for site, expected in (("_site_head", "head"), ("_site_base", "base")):
            assert f"echo {expected} > {site}/build-id.txt" in stamp, (
                f"{site} is no longer stamped with its build id, so the probe "
                "above cannot tell the two builds apart."
            )

    def test_default_post_url_is_a_single_source(self):
        wf = _workflow()
        default = wf.get("env", {}).get("DEFAULT_POST_URL")
        assert default and default.startswith("/posts/"), (
            "DEFAULT_POST_URL is missing or is not a site-root path. It is what "
            "an assets/** or _includes/** PR measures alongside the homepage; "
            "without it those PRs only ever measure '/'."
        )
        assert "--default-post-url" in _step(wf, "Resolve measurement URLs").get(
            "run", ""
        ), "DEFAULT_POST_URL is declared but no longer passed to the resolver."
