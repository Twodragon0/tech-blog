#!/usr/bin/env python3
"""Detect scheduled workflow runs that were due but never fired.

Every other CI check in this repo asks "did a run fail?". None of them can ask
"did a run happen at all?" — and that is the failure mode that has actually hurt
us. ``ops_health_orchestrator.check_github_actions`` filters ``gh run list`` down
to runs whose conclusion is a failure; a dropped schedule produces **no run
object**, so the list is empty and the check reports healthy. The absence is
invisible precisely because it is an absence.

The reason this needs a script rather than a glance is that eyeballing it gets
the answer wrong. On 2026-08-28 at 00:58Z, three cron entries had been due since
00:00-00:30Z with no run in sight, and that looked exactly like an outage. It was
not: measuring ``deploy-pages`` (cron ``30 0 * * *``) across five ordinary days
gives start times of 01:57, 02:09, 02:07, 02:01 and 02:08Z — **this repo's
scheduler is 30-100 minutes late as its normal baseline**, on every workflow
checked. An hour of silence is not a signal here; it is Tuesday.

The genuinely bad day, 2026-08-27, was worse than it first appeared *and* better:
runs arrived 350-661 minutes late, but every one of them did arrive. Nothing was
dropped. That matters because PR #629 was justified on the premise that the
00:30Z ``deploy-pages`` cron "never ran" that day — the schedule run exists, at
10:07Z. The change #629 made is still right (deploying the backup the moment a
digest publishes beats waiting on a trigger that is reliably 90 minutes late, and
was 9.6 hours late that day), but it was argued from a fact that was not checked.
Hence this script: the numbers should come from somewhere other than impression.

What this script does NOT do
---------------------------
It cannot page you *during* a total scheduler outage: anything that observes the
scheduler from inside the scheduler shares its fate. If the audit itself runs on
``schedule:`` and the scheduler is down, the audit does not run either. What it
does is make the gap **retrospectively visible** the moment the scheduler
recovers — a report saying "3 due, 0 delivered, here is the window" instead of
silence. Given the 08-27 outage went unnoticed until a reader hit a 404, that is
the difference that matters. ``workflow_dispatch`` is kept so a human who
suspects a gap can ask immediately without waiting for the next tick.

Stale listings
--------------
``gh run list`` is not a consistent read. Measured 2026-09-04: the same audit,
run ten times inside six minutes over an unchanged run history, returned four
different verdicts (1, 1, 1, 1, 1, 2, 2, 3 drops), and the workflow accused
rotated between ``monitoring``, ``googlebot-access-monitor``,
``slack-category-digest`` and ``ai-blogwatcher``. ``monitoring.yml`` was reported
``0/2 no delivery observed`` while ``gh run list`` showed both of its runs
(09-03T05:15Z, 09-04T05:11Z, both ``success``); re-evaluating that same workflow
seconds later gave ``2/2, lag 251-255m``. Pinning ``--now`` proves the logic is
deterministic — five consecutive runs at a fixed ``now`` agree exactly — so what
changed was the listing, not the arithmetic. The bad pages were not empty and did
not error (40 probe calls, 0 anomalies): they carried a full 100 rows of older
history with the recent runs missing, so nothing downstream could tell them from
the truth.

Hence :func:`audit` never reports a drop from a single read. A drop triggers a
second fetch and the verdict is recomputed over the **union** of both reads: a
run present in either page did happen, while absence from one page is not
evidence of anything.

The union alone is not safe to publish, and the reason is worth stating because
the obvious version of this fix is wrong. Recomputing over the union is monotone
in *deliveries* but **not** in *drops*: :func:`match_fires` calls a fire lost as
soon as a later fire has been served (``moved_past``), so a run supplied by the
second read can raise ``last_served`` and flip a fire from ``pending`` to
``dropped``. Measured with ``ops-orchestrator.yml``'s real crons
(``0 */6 * * *`` + ``0 4 * * *``, 2h minimum gap) at ``now=2026-09-04T06:20Z``,
with the 04:00 cycle's run sitting 130 minutes late and visible only to the
second read: read 1 gives 3 drops, the union gives 4 — and the added one is
**false**, its run mis-credited forward to the 06:00 fire. The 13 daily
workflows here are immune (a 24h gap exceeds the 18h settle, so a pending fire
has no later sibling to serve), which is precisely why this would have shipped
looking correct: the one exposed workflow is the only one that actually drops.

So the second read is a *confirmation*, not a re-decision. It may only withdraw
an accusation, never add one: a fire the union newly accuses is held in
``pending`` and listed under ``withheld_accusations``. Nothing is lost by
waiting — a genuinely lost cycle is permanent and is accused by the *first* read
of the next audit, while a false accusation is transient by construction.
``listing_disagreement`` compares the two reads in both directions, and
``confirmation`` records whether the second read happened at all, so a
once-observed drop is never mistaken for a twice-confirmed one.

This matters because the audit is not a blocking gate: each drop prints an
``::error::`` annotation telling a human to run ``gh workflow run <wf>``. A false
drop therefore asks someone to re-run a workflow that already succeeded, and the
one channel in this repo that can see an absence is the one that must not cry
wolf.

Known residual
--------------
Each workflow's window is clamped to its GitHub ``created_at``, which removes the
false drops a newly added scheduled workflow would otherwise report. It does NOT
cover a workflow whose *cron was edited* inside the lookback window: cycles due
under the old expression but not the new one can still be reported as lost. The
API cannot distinguish this — ``deploy-pages.yml`` reports ``updated_at ==
created_at == 2026-03-25`` although its cron changed on 2026-07-06 — and git
history is unavailable under the shallow clone CI uses. The 48h default lookback
bounds the exposure to two days after any reschedule.

Cron semantics
--------------
Fields are ``minute hour day-of-month month day-of-week`` (POSIX 5-field). We
support ``*``, ``N``, ``a-b``, ``*/N``, ``a-b/N`` and comma lists of those, plus
the POSIX rule that when **both** day-of-month and day-of-week are restricted the
entry fires when *either* matches (not both). Anything else — names like ``MON``,
Quartz extensions like ``L``/``W``/``#``/``?`` — raises ``UnsupportedCron``
rather than being silently approximated. A matcher that quietly mis-parses an
expression would under-report drops, which is the one outcome worse than not
running at all: this repo has twice shipped a gate that reported clean because it
was looking at the wrong thing.

Usage::

    python3 scripts/check_cron_firing.py --lookback-hours 24
    python3 scripts/check_cron_firing.py --json
    python3 scripts/check_cron_firing.py --strict     # exit 1 when drops found
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# How long a due cycle may stay undelivered before we call it lost, when no later
# cycle has been served yet to prove the scheduler moved on. Set from measurement,
# not taste: the worst delay actually observed here is 2026-08-27's svg-lint run,
# 661 minutes (11h01m) after its nominal 03:45Z. 18h leaves headroom above that
# while still flagging a genuinely lost daily cycle before its successor is due.
DEFAULT_SETTLE_HOURS = 18.0


class UnsupportedCron(ValueError):
    """A cron field used syntax this parser refuses to guess at."""


class WorkflowNotMeasurable(RuntimeError):
    """This workflow's run history cannot be read, so it gets no verdict."""


def _parse_field(spec: str, lo: int, hi: int) -> set[int]:
    """Expand one cron field into the set of values it matches.

    Raises UnsupportedCron for anything outside the documented subset.
    """
    if not spec:
        raise UnsupportedCron("empty cron field")
    values: set[int] = set()
    for part in spec.split(","):
        step = 1
        if "/" in part:
            part, _, step_s = part.partition("/")
            if not step_s.isdigit() or int(step_s) < 1:
                raise UnsupportedCron(f"bad step in {spec!r}")
            step = int(step_s)
        if part == "*":
            start, end = lo, hi
        elif "-" in part.lstrip("-"):
            a, _, b = part.partition("-")
            if not (a.isdigit() and b.isdigit()):
                raise UnsupportedCron(f"non-numeric range in {spec!r}")
            start, end = int(a), int(b)
        elif part.isdigit():
            start = end = int(part)
        else:
            raise UnsupportedCron(f"unsupported cron field {spec!r}")
        if start < lo or end > hi or start > end:
            raise UnsupportedCron(f"cron field {spec!r} out of range [{lo},{hi}]")
        values.update(range(start, end + 1, step))
    return values


@dataclass(frozen=True)
class CronExpr:
    """A parsed 5-field cron expression."""

    raw: str
    minutes: frozenset[int]
    hours: frozenset[int]
    doms: frozenset[int]
    months: frozenset[int]
    dows: frozenset[int]
    dom_restricted: bool
    dow_restricted: bool

    @classmethod
    def parse(cls, expr: str) -> CronExpr:
        fields = expr.split()
        if len(fields) != 5:
            raise UnsupportedCron(
                f"expected 5 cron fields, got {len(fields)} in {expr!r}"
            )
        mi, ho, dom, mon, dow = fields
        dows = _parse_field(dow, 0, 7)
        # Both 0 and 7 mean Sunday in POSIX cron.
        if 7 in dows:
            dows = (dows - {7}) | {0}
        return cls(
            raw=expr,
            minutes=frozenset(_parse_field(mi, 0, 59)),
            hours=frozenset(_parse_field(ho, 0, 23)),
            doms=frozenset(_parse_field(dom, 1, 31)),
            months=frozenset(_parse_field(mon, 1, 12)),
            dows=frozenset(dows),
            dom_restricted=dom != "*",
            dow_restricted=dow != "*",
        )

    def matches(self, when: datetime) -> bool:
        if when.minute not in self.minutes or when.hour not in self.hours:
            return False
        if when.month not in self.months:
            return False
        dom_hit = when.day in self.doms
        dow_hit = (when.isoweekday() % 7) in self.dows
        if self.dom_restricted and self.dow_restricted:
            # POSIX: restricted day-of-month OR restricted day-of-week.
            return dom_hit or dow_hit
        return dom_hit and dow_hit

    def fires_between(self, start: datetime, end: datetime) -> list[datetime]:
        """Fire times in the half-open interval (start, end]."""
        out: list[datetime] = []
        t = start.replace(second=0, microsecond=0) + timedelta(minutes=1)
        while t <= end:
            if self.matches(t):
                out.append(t)
            t += timedelta(minutes=1)
        return out


@dataclass
class WorkflowSchedule:
    """One workflow file and the cron entries declared under its ``on:``."""

    filename: str
    name: str
    crons: list[CronExpr] = field(default_factory=list)


def _on_block(doc: dict[str, Any]) -> dict[str, Any]:
    # YAML 1.1 parses a bare `on:` key as the boolean True.
    block = doc.get(True)
    if block is None:
        block = doc.get("on")
    return block if isinstance(block, dict) else {}


def discover_schedules(workflow_dir: Path = WORKFLOW_DIR) -> list[WorkflowSchedule]:
    """Read cron entries from the ``on.schedule`` block of every workflow.

    Deliberately parses YAML instead of grepping for ``cron:``: a grep also picks
    up cron strings in comments and in ``inputs`` defaults, which would invent
    expected fires that were never scheduled and report them as drops.
    """
    found: list[WorkflowSchedule] = []
    for path in sorted(workflow_dir.glob("*.yml")) + sorted(
        workflow_dir.glob("*.yaml")
    ):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            continue
        schedule = _on_block(doc).get("schedule")
        if not isinstance(schedule, list):
            continue
        crons: list[CronExpr] = []
        for entry in schedule:
            if not isinstance(entry, dict) or "cron" not in entry:
                continue
            crons.append(CronExpr.parse(str(entry["cron"])))
        if crons:
            found.append(
                WorkflowSchedule(
                    filename=path.name,
                    name=str(doc.get("name") or path.stem),
                    crons=crons,
                )
            )
    return found


def fetch_workflow_births() -> dict[str, datetime]:
    """When GitHub first registered each workflow, keyed by file basename.

    A cron only means anything from the moment the workflow exists. Without this
    bound the audit computes due cycles for a period when the schedule was not in
    effect and reports them as lost — which is what it did on its own first CI
    run: ``cron-firing-audit.yml`` merged at 2026-08-28T02:32Z and the report
    immediately called its 08-26T20:00Z and 08-27T20:00Z cycles DROPPED. Every
    newly added scheduled workflow would produce that, and a report that cries
    wolf on each addition is one people learn to skip.

    One paginated call for the whole repo rather than one per workflow. The API's
    ``created_at`` is used, not ``updated_at``: measured on 2026-08-28,
    ``deploy-pages.yml`` reports both as 2026-03-25 despite its cron having been
    edited on 2026-07-06, so ``updated_at`` does not track content edits and
    would give a false sense of precision.
    """
    proc = subprocess.run(
        [
            "gh",
            "api",
            "repos/{owner}/{repo}/actions/workflows",
            "--paginate",
            "--jq",
            ".workflows[] | [.path, .created_at] | @tsv",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"gh api workflows failed: {(proc.stderr or proc.stdout).strip()}"
        )
    return parse_births(proc.stdout)


def parse_births(stdout: str) -> dict[str, datetime]:
    """Parse ``path\\tcreated_at`` lines into basename -> UTC datetime.

    Split out from the subprocess call so the parsing has tests. The API returns
    repo-relative paths and offset-aware timestamps (``+09:00`` for this repo's
    account), both of which have to be normalised before they can be compared
    against the audit window.
    """
    births: dict[str, datetime] = {}
    for line in stdout.splitlines():
        path, _, created = line.partition("\t")
        if not created.strip():
            continue
        births[Path(path).name] = datetime.fromisoformat(created.strip()).astimezone(
            timezone.utc
        )
    return births


def fetch_schedule_runs(filename: str, limit: int = 100) -> list[datetime]:
    """Start times of this workflow's ``schedule``-triggered runs, newest first.

    A run that exists but was skipped by a job-level ``if:`` still counts: the
    scheduler delivered the event, which is the only thing this audit measures.
    """
    proc = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--workflow",
            filename,
            "--event",
            "schedule",
            "--limit",
            str(limit),
            "--json",
            "createdAt",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        # A workflow file present in the checkout but not on the default branch
        # — a newly added one on a feature branch, or one just renamed — makes
        # `gh run list --workflow` return 404. Found by running this script
        # against its own PR branch, where it aborted the entire audit on the
        # first such file. Two wrong ways to handle it: crashing takes the whole
        # report down for one unrelated file, and treating 404 as "zero runs"
        # marks every due cycle of that workflow as dropped. It is neither
        # delivered nor lost; it is not measurable, and says so.
        if "404" in detail or "not found on the default branch" in detail:
            raise WorkflowNotMeasurable(detail)
        raise RuntimeError(f"gh run list failed for {filename}: {detail}")
    rows = json.loads(proc.stdout or "[]")
    return sorted(
        (datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00")) for r in rows),
        reverse=True,
    )


def match_fires(
    expected: Iterable[datetime],
    actual: Iterable[datetime],
    settle: timedelta,
    now: datetime,
) -> tuple[list[datetime], list[tuple[datetime, datetime]], list[datetime]]:
    """Classify each due fire as delivered, dropped, or still pending.

    A fixed "delivered within N minutes" grace does not work here, and the
    measurement that killed that design is worth recording. Actual start times
    for ``deploy-pages`` (cron ``30 0 * * *``) on five consecutive ordinary days:
    01:57, 02:09, 02:07, 02:01, 02:08 — i.e. this repo's scheduler is **routinely
    87-99 minutes late**, and ``ai-blogwatcher`` / ``svg-lint`` / ``monitoring``
    show the same 30-100 minute baseline. Any grace tight enough to be
    interesting would fire every single day; any grace loose enough to be quiet
    (12h+) would not distinguish a drop from a delay at all. The first draft of
    this function used a 90-minute grace and reported 14 drops for 2026-08-27,
    a day on which **every one of those workflows eventually ran**.

    So delivery is decided by ordering, not by a stopwatch. Each run is credited
    to the most recent due fire at or before it. A fire with no run is only
    called *dropped* once the scheduler has demonstrably moved past it — either a
    later fire has already been served, or ``settle`` has elapsed. Until then it
    is *pending*, because on 2026-08-27 runs arrived up to 11 hours late and
    calling those drops would have been wrong.
    """
    runs = sorted(actual)
    fires = sorted(expected)
    assigned: dict[datetime, datetime] = {}
    for run in runs:
        owner = None
        for fire in fires:
            if fire <= run:
                owner = fire
            else:
                break
        if owner is not None and owner not in assigned:
            assigned[owner] = run

    delivered = [(f, assigned[f]) for f in fires if f in assigned]
    last_served = max((f for f in assigned), default=None)
    dropped: list[datetime] = []
    pending: list[datetime] = []
    for fire in fires:
        if fire in assigned:
            continue
        moved_past = last_served is not None and last_served > fire
        if moved_past or (now - fire) > settle:
            dropped.append(fire)
        else:
            pending.append(fire)
    return dropped, delivered, pending


def audit(
    now: datetime,
    lookback: timedelta,
    settle: timedelta,
    schedules: list[WorkflowSchedule],
    runs_for: Any,
    births: dict[str, datetime] | None = None,
) -> dict[str, Any]:
    """Compare due fires against delivered runs for every scheduled workflow."""
    window_start = now - lookback
    births = births or {}
    results: list[dict[str, Any]] = []
    unmeasurable: list[dict[str, str]] = []
    for wf in schedules:
        # A cron is only in effect once the workflow exists. Clamping here rather
        # than filtering afterwards keeps the pre-birth cycles out of `expected`
        # entirely, so they cannot be counted as due-but-undelivered.
        born = births.get(wf.filename)
        start = max(window_start, born) if born else window_start
        expected: list[datetime] = []
        for cron in wf.crons:
            expected.extend(cron.fires_between(start, now))
        if not expected:
            continue
        try:
            actual = runs_for(wf.filename)
        except WorkflowNotMeasurable as exc:
            unmeasurable.append({"workflow": wf.filename, "reason": str(exc)})
            continue
        dropped, delivered, pending = match_fires(expected, actual, settle, now)
        # A drop is the only verdict here that accuses anyone, and it is the one
        # `gh run list` gets wrong intermittently (see "Stale listings" above).
        # So it costs a second read before it is believed. Only drops pay this —
        # on an ordinary day that is one extra call for the whole repo — because
        # a stale page can only ever manufacture a drop, never erase one.
        disagreement = False
        confirmation = "not_attempted"
        withheld: list[datetime] = []
        if dropped:
            try:
                second = runs_for(wf.filename)
            except (WorkflowNotMeasurable, RuntimeError):
                # Any failed re-read, not only a 404. `fetch_schedule_runs`
                # raises a plain RuntimeError for a 502 or a rate limit, and
                # letting that escape leaves `report.json` empty — which makes
                # cron-firing-audit.yml red, the one thing its header says it
                # must never be, and `AUTO_RECOVER_GHA` would then re-run it
                # forever over a cycle that was lost hours ago.
                #
                # The first read's verdict stands rather than being upgraded or
                # discarded: we have one observation and no grounds to overrule
                # it. `confirmation` says it was only one.
                confirmation = "unconfirmed"
            else:
                confirmation = "confirmed"
                # Merging inside `else:` rather than behind a `second is not
                # None` sentinel. A sentinel makes an absent re-read and a
                # `runs_for` that returned nothing the same value, so a caller
                # returning None would be labelled "confirmed" while no merge
                # ever ran — the exact conflation `confirmation` was added to
                # remove.
                #
                # Judged in both directions, and deliberately not derived from
                # "did the union grow". Which of the two reads is the stale one
                # is a coin flip, so a one-directional test reports about half
                # of the disagreements — in a field whose whole purpose is to
                # keep a flaky source from passing for a reliable one. Set
                # comparison also avoids reading `len(list)` against
                # `len(set)`, where a single duplicate row hides a real
                # correction.
                disagreement = set(second) != set(actual)
                union = sorted(set(actual) | set(second))
                accused_by_first = set(dropped)
                u_dropped, delivered, u_pending = match_fires(
                    expected, union, settle, now
                )
                # Downgrade-only. See "Stale listings": the union can invent a
                # drop out of a late run, so an accusation needs both reads.
                withheld = [d for d in u_dropped if d not in accused_by_first]
                dropped = [d for d in u_dropped if d in accused_by_first]
                pending = sorted(set(u_pending) | set(withheld))
                actual = union
        lags = [int((got - due).total_seconds() // 60) for due, got in delivered]
        results.append(
            {
                "workflow": wf.filename,
                "name": wf.name,
                "crons": [c.raw for c in wf.crons],
                # Surfaced, not just applied: a shortened window changes what
                # "0 dropped" means, and a reader who cannot see the clamp has
                # no way to tell a quiet workflow from a young one.
                "window_clamped_to_birth": (
                    born.strftime("%Y-%m-%dT%H:%MZ")
                    if born and born > window_start
                    else None
                ),
                "expected": len(expected),
                "delivered": len(delivered),
                "dropped": [d.strftime("%Y-%m-%dT%H:%MZ") for d in dropped],
                "pending": [p.strftime("%Y-%m-%dT%H:%MZ") for p in pending],
                # The evidence the verdict rests on, not just the verdict. A
                # reader who sees `0/2 no delivery observed` cannot tell "the
                # scheduler skipped this slot" from "this listing showed us
                # nothing recent at all" — the second is the stale-page
                # signature, and it was indistinguishable until this line.
                "newest_run_observed": (
                    max(actual).strftime("%Y-%m-%dT%H:%MZ") if actual else None
                ),
                # True when the confirming read disagreed with the first one.
                # Surfaced because a silent correction is how a known-flaky
                # data source gets mistaken for a reliable one.
                "listing_disagreement": disagreement,
                # How many observations this verdict rests on:
                # "not_attempted" (nothing was accused, so no re-read was owed),
                # "confirmed" (two reads), "unconfirmed" (the re-read failed, so
                # one). Without this a single-sourced drop and a twice-confirmed
                # one are byte-identical.
                "confirmation": confirmation,
                # Fires the union accused but the first read did not. Held in
                # `pending`, and listed rather than silently absorbed: this is
                # the audit refusing to escalate on one read, and a reader who
                # cannot see it has no way to know a judgement was deferred.
                "withheld_accusations": [
                    w.strftime("%Y-%m-%dT%H:%MZ") for w in withheld
                ],
                # min and max, not a median: over a 48h window most workflows
                # have two deliveries, and a two-sample median is just the
                # larger one wearing a statistical hat. The spread is the
                # interesting part — 45m on an ordinary day next to 653m on
                # 2026-08-27 is the whole story, and an average hides it.
                "min_lag_minutes": min(lags, default=None),
                "max_lag_minutes": max(lags, default=None),
            }
        )
    return {
        "window_start": window_start.strftime("%Y-%m-%dT%H:%MZ"),
        "now": now.strftime("%Y-%m-%dT%H:%MZ"),
        "settle_hours": round(settle.total_seconds() / 3600, 1),
        "expected": sum(r["expected"] for r in results),
        "delivered": sum(r["delivered"] for r in results),
        "dropped": sum(len(r["dropped"]) for r in results),
        "pending": sum(len(r["pending"]) for r in results),
        "workflows": results,
        # Reported, never silently omitted: a workflow this audit could not read
        # looks identical to a workflow with nothing wrong if you only print the
        # ones that passed.
        "unmeasurable": unmeasurable,
    }


def format_report(report: dict[str, Any]) -> str:
    lines = [
        f"[cron-firing] window {report['window_start']} -> {report['now']} "
        f"(settle {report['settle_hours']}h)",
        f"[cron-firing] due {report['expected']} / delivered "
        f"{report['delivered']} / DROPPED {report['dropped']} / "
        f"pending {report['pending']}",
        "",
    ]
    for r in sorted(
        report["workflows"], key=lambda x: (-len(x["dropped"]), x["workflow"])
    ):
        mark = "DROP" if r["dropped"] else ("wait" if r["pending"] else "ok  ")
        lag = (
            f"lag {r['min_lag_minutes']}-{r['max_lag_minutes']}m"
            if r["delivered"]
            else "no delivery observed"
        )
        lines.append(
            f"  {mark} {r['workflow']:<38} {r['delivered']}/{r['expected']}  {lag}"
        )
        if r.get("window_clamped_to_birth"):
            lines.append(
                f"         window starts {r['window_clamped_to_birth']} "
                f"(workflow created then; earlier cycles were never scheduled)"
            )
        if r.get("listing_disagreement"):
            lines.append(
                "         note: the two run listings disagreed; verdict computed "
                "over the union of both reads"
            )
        if r.get("confirmation") == "unconfirmed":
            lines.append(
                "         note: the confirming read failed — this verdict rests "
                "on a single listing, which is the one known to go stale"
            )
        for w in r.get("withheld_accusations", []):
            lines.append(
                f"         withheld: {w} looked dropped only after the second "
                f"read; held as pending rather than accused on one read"
            )
        for d in r["dropped"]:
            lines.append(
                f"         DROPPED: {d}  [{', '.join(r['crons'])}]  "
                f"(newest run seen: {r.get('newest_run_observed') or 'none'})"
            )
        for p in r["pending"]:
            lines.append(f"         not yet delivered: {p}  (still within settle)")
    for u in report.get("unmeasurable", []):
        lines.append(
            f"  n/a  {u['workflow']:<38} run history unreadable — NOT counted "
            f"as delivered or dropped"
        )
        lines.append(f"         {u['reason']}")
    lines += [
        "",
        "Lag is expected: this repo's scheduler baseline is 30-100 minutes late "
        "on ordinary days. Only DROPPED means a cycle was lost — GitHub does not "
        "backfill it, so whatever that workflow was the sole trigger for did not "
        "happen and will not happen on its own.",
    ]
    return "\n".join(lines)


def _iso_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lookback-hours", type=float, default=48.0)
    p.add_argument("--settle-hours", type=float, default=DEFAULT_SETTLE_HOURS)
    p.add_argument("--now", type=_iso_utc, default=None, help="override 'now' (UTC)")
    p.add_argument("--json", action="store_true", help="emit the raw report as JSON")
    p.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when any due schedule was never delivered",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    now = args.now or datetime.now(timezone.utc)
    try:
        schedules = discover_schedules()
    except UnsupportedCron as exc:
        print(f"[cron-firing] ERROR: {exc}", file=sys.stderr)
        print(
            "[cron-firing] refusing to guess at the expression; extend "
            "_parse_field() rather than loosening it.",
            file=sys.stderr,
        )
        return 2
    try:
        report = audit(
            now=now,
            lookback=timedelta(hours=args.lookback_hours),
            settle=timedelta(hours=args.settle_hours),
            schedules=schedules,
            runs_for=fetch_schedule_runs,
            births=fetch_workflow_births(),
        )
    except RuntimeError as exc:
        print(f"[cron-firing] ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else format_report(report))
    return 1 if (args.strict and report["dropped"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
