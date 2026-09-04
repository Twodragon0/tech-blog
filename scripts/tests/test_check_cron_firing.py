#!/usr/bin/env python3
"""Unit tests for check_cron_firing.py.

The bug these tests exist to prevent is not a crash — the first draft ran fine
and printed a confident, wrong answer. It used a 90-minute delivery grace and
reported 14 dropped cycles for 2026-08-27, a day on which every one of those
workflows eventually ran (350-661 minutes late). Measurement killed that design:
``deploy-pages`` alone starts 87-99 minutes after its nominal 00:30Z on five
consecutive ordinary days, so a 90-minute grace flags the baseline as an outage.

``TestLateIsNotLost`` pins the corrected semantics with those real numbers. If
someone reintroduces a stopwatch-based rule, it fails there.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

from scripts import check_cron_firing as mod


def dt(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, day, hour, minute, tzinfo=timezone.utc)


class TestCronParsing:
    def test_plain_daily(self):
        c = mod.CronExpr.parse("30 0 * * *")
        assert c.minutes == {30}
        assert c.hours == {0}
        assert c.matches(dt(27, 0, 30))
        assert not c.matches(dt(27, 0, 31))

    def test_step_expands_over_full_range(self):
        c = mod.CronExpr.parse("0 */6 * * *")
        assert c.hours == {0, 6, 12, 18}

    def test_range_with_step(self):
        assert mod.CronExpr.parse("0 1-9/4 * * *").hours == {1, 5, 9}

    def test_comma_list(self):
        assert mod.CronExpr.parse("0 1,4,7 * * *").hours == {1, 4, 7}

    def test_sunday_is_both_zero_and_seven(self):
        """POSIX allows 0 and 7 for Sunday; normalising avoids a silent miss."""
        assert (
            mod.CronExpr.parse("0 0 * * 7").dows == mod.CronExpr.parse("0 0 * * 0").dows
        )
        # 2026-08-30 is a Sunday.
        assert mod.CronExpr.parse("0 0 * * 7").matches(dt(30, 0, 0))

    def test_weekday_only_entry(self):
        """The repo's real Monday cron, from vercel-firewall-backup.yml."""
        c = mod.CronExpr.parse("0 0 * * 1")
        assert c.matches(dt(24, 0, 0))  # 2026-08-24 is a Monday
        assert not c.matches(dt(25, 0, 0))

    def test_restricted_dom_and_dow_is_or_not_and(self):
        """POSIX: when both day fields are restricted the entry fires on either.

        Treating this as AND would silently under-count expected fires, and an
        expected fire that is never computed can never be reported as dropped.
        """
        c = mod.CronExpr.parse("0 0 1 * 1")
        assert c.matches(dt(1, 0, 0))  # 2026-08-01: day-of-month hit (a Saturday)
        assert c.matches(dt(24, 0, 0))  # 2026-08-24: day-of-week hit (a Monday)
        assert not c.matches(dt(25, 0, 0))  # neither

    @pytest.mark.parametrize(
        "expr",
        [
            "0 0 * * MON",  # day-of-week names
            "0 0 ? * *",  # Quartz
            "0 0 L * *",  # Quartz last-day
            "0 0 * *",  # four fields
            "0 24 * * *",  # hour out of range
            "0 0 * * */0",  # zero step
        ],
    )
    def test_refuses_to_guess(self, expr):
        with pytest.raises(mod.UnsupportedCron):
            mod.CronExpr.parse(expr)

    def test_fires_between_is_half_open_on_the_left(self):
        c = mod.CronExpr.parse("0 0 * * *")
        fires = c.fires_between(dt(26, 0, 0), dt(28, 0, 0))
        assert fires == [dt(27, 0, 0), dt(28, 0, 0)]


class TestLateIsNotLost:
    """Real 2026-08-27 numbers. A very late run is delivered, not dropped."""

    SETTLE = timedelta(hours=18)

    def test_eleven_hour_delay_counts_as_delivered(self):
        # svg-lint: nominal 03:45Z, actual 14:46Z -> 661 minutes late.
        dropped, delivered, pending = mod.match_fires(
            expected=[dt(27, 3, 45)],
            actual=[dt(27, 14, 46)],
            settle=self.SETTLE,
            now=dt(28, 1, 0),
        )
        assert dropped == []
        assert pending == []
        assert delivered == [(dt(27, 3, 45), dt(27, 14, 46))]

    def test_baseline_delay_is_not_interesting(self):
        # deploy-pages on an ordinary day: 00:30Z nominal, 02:08Z actual.
        dropped, delivered, _ = mod.match_fires(
            expected=[dt(26, 0, 30)],
            actual=[dt(26, 2, 8)],
            settle=self.SETTLE,
            now=dt(27, 0, 0),
        )
        assert dropped == []
        assert len(delivered) == 1

    def test_undelivered_but_recent_is_pending_not_dropped(self):
        """Today's 00:00Z with nothing yet at 01:20Z: unknown, not lost.

        Calling this a drop is the mistake a human made on 2026-08-28 at 00:58Z
        by eyeballing the run list.
        """
        dropped, _, pending = mod.match_fires(
            expected=[dt(28, 0, 0)],
            actual=[],
            settle=self.SETTLE,
            now=dt(28, 1, 20),
        )
        assert dropped == []
        assert pending == [dt(28, 0, 0)]

    def test_dropped_once_settle_elapses(self):
        dropped, _, pending = mod.match_fires(
            expected=[dt(27, 0, 0)],
            actual=[],
            settle=self.SETTLE,
            now=dt(27, 19, 0),
        )
        assert dropped == [dt(27, 0, 0)]
        assert pending == []

    def test_dropped_when_a_later_cycle_was_already_served(self):
        """The strong signal: the scheduler demonstrably moved past it.

        No waiting required — if 06:00Z ran and 00:00Z never did, 00:00Z is lost
        even though settle has not elapsed. This is what catches the two real
        ops-orchestrator drops on 2026-08-27.
        """
        dropped, delivered, pending = mod.match_fires(
            expected=[dt(27, 0, 0), dt(27, 6, 0)],
            actual=[dt(27, 6, 40)],
            settle=self.SETTLE,
            now=dt(27, 7, 0),
        )
        assert dropped == [dt(27, 0, 0)]
        assert pending == []
        assert delivered == [(dt(27, 6, 0), dt(27, 6, 40))]

    def test_one_run_cannot_satisfy_two_cycles(self):
        """Otherwise a burst of drops hides behind a single late run."""
        dropped, delivered, _ = mod.match_fires(
            expected=[dt(27, 0, 0), dt(27, 6, 0), dt(27, 12, 0)],
            actual=[dt(27, 12, 30)],
            settle=self.SETTLE,
            now=dt(28, 12, 0),
        )
        assert len(delivered) == 1
        assert dropped == [dt(27, 0, 0), dt(27, 6, 0)]


class TestDiscoverSchedules:
    def test_ignores_cron_outside_the_schedule_block(self, tmp_path: Path):
        """A grep for 'cron:' invents fires that were never scheduled.

        Both decoys below appear in real workflow files in this repo — a cron in
        a comment explaining the schedule, and one in a dispatch input default.
        """
        (tmp_path / "w.yml").write_text(
            "name: Decoy\n"
            "on:\n"
            "  # daily at cron: '0 3 * * *' per the runbook\n"
            "  workflow_dispatch:\n"
            "    inputs:\n"
            "      cron:\n"
            "        default: '0 9 * * *'\n"
            "  schedule:\n"
            "    - cron: '15 2 * * *'\n"
            "jobs: {}\n",
            encoding="utf-8",
        )
        found = mod.discover_schedules(tmp_path)
        assert len(found) == 1
        assert [c.raw for c in found[0].crons] == ["15 2 * * *"]

    def test_skips_workflows_without_a_schedule(self, tmp_path: Path):
        (tmp_path / "w.yml").write_text(
            "name: N\non:\n  push:\n    branches: [main]\njobs: {}\n", encoding="utf-8"
        )
        assert mod.discover_schedules(tmp_path) == []

    def test_every_real_workflow_cron_parses(self):
        """Guard: an unparseable cron makes the whole audit exit 2 and go quiet.

        If someone adds `0 0 * * MON`, this fails here rather than turning the
        scheduled audit into a permanently erroring job nobody reads.
        """
        schedules = mod.discover_schedules()
        assert schedules, "no scheduled workflows found; the discovery path broke"
        for wf in schedules:
            for cron in wf.crons:
                assert cron.raw.split(), wf.filename

    def test_discovery_matches_a_raw_yaml_count(self):
        """Cross-check discovery against an independent read of the same files."""
        expected = 0
        for path in sorted(mod.WORKFLOW_DIR.glob("*.yml")):
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(doc, dict):
                continue
            block = doc.get(True) if doc.get(True) is not None else doc.get("on")
            if isinstance(block, dict) and isinstance(block.get("schedule"), list):
                expected += sum(
                    1 for e in block["schedule"] if isinstance(e, dict) and "cron" in e
                )
        assert sum(len(w.crons) for w in mod.discover_schedules()) == expected


class TestWorkflowBirth:
    """A cron means nothing before its workflow exists.

    Regression from the audit's own first CI run: ``cron-firing-audit.yml`` was
    merged at 2026-08-28T02:32Z and the report immediately called its
    2026-08-26T20:00Z and 2026-08-27T20:00Z cycles DROPPED — cycles for which no
    schedule had been registered. Left alone, every newly added scheduled
    workflow would announce itself with a false drop, and a report that cries
    wolf on each addition is one people learn to skip.
    """

    def test_parse_births_normalises_path_and_offset(self):
        births = mod.parse_births(
            ".github/workflows/a.yml\t2026-08-28T11:32:44.000+09:00\n"
            ".github/workflows/b.yml\t2026-03-25T14:08:50.000+09:00\n"
            "dynamic/github-code-scanning/codeql\t\n"  # no timestamp -> skipped
        )
        assert set(births) == {"a.yml", "b.yml"}
        assert births["a.yml"] == dt(28, 2, 32).replace(second=44)

    def test_cycles_before_birth_are_not_due(self):
        schedules = [
            mod.WorkflowSchedule(
                filename="new.yml", name="N", crons=[mod.CronExpr.parse("0 20 * * *")]
            )
        ]
        common = dict(
            now=dt(28, 4, 0),
            lookback=timedelta(hours=54),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: [],
        )
        # Without the clamp both pre-birth cycles are treated as due: 08-26T20:00
        # is already past settle and reported DROPPED, 08-27T20:00 is still
        # inside it and reported pending. Neither was ever scheduled.
        unclamped = mod.audit(**common)
        assert unclamped["expected"] == 2
        assert unclamped["dropped"] == 1
        assert unclamped["pending"] == 1

        # With it: the workflow did not exist for either, so neither was due.
        clamped = mod.audit(**common, births={"new.yml": dt(28, 2, 32)})
        assert clamped["dropped"] == 0
        assert clamped["expected"] == 0

    def test_cycles_after_birth_are_still_judged(self):
        """The clamp must not become a blanket amnesty for young workflows."""
        schedules = [
            mod.WorkflowSchedule(
                filename="new.yml", name="N", crons=[mod.CronExpr.parse("0 */6 * * *")]
            )
        ]
        report = mod.audit(
            now=dt(28, 23, 0),
            lookback=timedelta(hours=54),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: [dt(28, 18, 30)],
            births={"new.yml": dt(28, 2, 32)},
        )
        # Post-birth cycles: 06:00, 12:00, 18:00. The 18:00 one was served, and
        # that delivery proves the scheduler moved past 06:00 and 12:00.
        assert report["expected"] == 3
        assert report["dropped"] == 2
        assert report["delivered"] == 1

    def test_clamp_is_reported_not_just_applied(self):
        schedules = [
            mod.WorkflowSchedule(
                filename="new.yml", name="N", crons=[mod.CronExpr.parse("0 */6 * * *")]
            )
        ]
        report = mod.audit(
            now=dt(28, 23, 0),
            lookback=timedelta(hours=54),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: [],
            births={"new.yml": dt(28, 2, 32)},
        )
        assert report["workflows"][0]["window_clamped_to_birth"] == "2026-08-28T02:32Z"
        assert "workflow created then" in mod.format_report(report)

    def test_old_workflow_is_not_clamped(self):
        schedules = [
            mod.WorkflowSchedule(
                filename="old.yml", name="O", crons=[mod.CronExpr.parse("0 0 * * *")]
            )
        ]
        report = mod.audit(
            now=dt(28, 6, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: [dt(27, 1, 0), dt(28, 1, 0)],
            births={"old.yml": datetime(2026, 3, 25, tzinfo=timezone.utc)},
        )
        assert report["workflows"][0]["window_clamped_to_birth"] is None
        assert report["expected"] == 2


class TestAudit:
    def test_counts_roll_up_across_workflows(self):
        schedules = [
            mod.WorkflowSchedule(
                filename="a.yml", name="A", crons=[mod.CronExpr.parse("0 0 * * *")]
            ),
            mod.WorkflowSchedule(
                filename="b.yml", name="B", crons=[mod.CronExpr.parse("0 12 * * *")]
            ),
        ]
        runs = {"a.yml": [dt(27, 1, 30)], "b.yml": []}
        # 32h back from 28T07:00 starts the window at 26T23:00. fires_between is
        # half-open on the left, so a 30h window starting exactly at 27T00:00
        # would silently drop that fire from the expected set.
        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: runs[f],
        )
        assert report["expected"] == 3  # a: 27+28 00:00, b: 27 12:00
        assert report["delivered"] == 1  # a's 27T00:00 -> 01:30 run
        assert report["dropped"] == 1  # b's 27T12:00, 19h old > 18h settle
        assert report["pending"] == 1  # a's 28T00:00, 7h old, still in flight

    def test_unreadable_workflow_is_reported_not_counted(self):
        """A 404 from `gh run list` must not become a drop, and must not vanish.

        Found empirically: running this script on the branch that adds it made
        `gh run list --workflow cron-firing-audit.yml` return "not found on the
        default branch", which aborted the whole audit. Both obvious repairs are
        wrong — crashing loses the report over one unrelated file, and treating
        404 as "zero runs" marks every due cycle of that workflow as dropped.
        """

        def runs_for(filename):
            if filename == "new.yml":
                raise mod.WorkflowNotMeasurable(
                    "HTTP 404: not found on the default branch"
                )
            return [dt(27, 1, 0)]

        schedules = [
            mod.WorkflowSchedule(
                filename="new.yml", name="N", crons=[mod.CronExpr.parse("0 0 * * *")]
            ),
            mod.WorkflowSchedule(
                filename="old.yml", name="O", crons=[mod.CronExpr.parse("0 0 * * *")]
            ),
        ]
        report = mod.audit(
            now=dt(27, 12, 0),
            lookback=timedelta(hours=13),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=runs_for,
        )
        assert report["dropped"] == 0
        assert report["expected"] == 1  # only old.yml's cycle is measurable
        assert [u["workflow"] for u in report["unmeasurable"]] == ["new.yml"]
        assert "new.yml" in mod.format_report(report)

    def test_no_second_read_when_nothing_dropped(self):
        """The confirming read is spent only on drops.

        This is the cost guard for the re-read. On an ordinary day exactly one
        workflow here reports a drop, so confirmation costs one extra `gh` call
        for the whole repo; confirming every workflow unconditionally would
        double the API traffic to re-prove 30 deliveries that were never in
        doubt.
        """
        calls: list[str] = []

        def runs_for(filename):
            calls.append(filename)
            return [dt(27, 1, 30)]

        schedules = [
            mod.WorkflowSchedule(
                filename="a.yml", name="A", crons=[mod.CronExpr.parse("0 0 * * *")]
            )
        ]
        report = mod.audit(
            now=dt(27, 12, 0),
            lookback=timedelta(hours=13),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=runs_for,
        )
        assert report["dropped"] == 0
        assert calls == ["a.yml"]

    def test_workflow_with_no_due_fires_is_omitted(self):
        schedules = [
            mod.WorkflowSchedule(
                filename="m.yml", name="M", crons=[mod.CronExpr.parse("0 0 1 1 *")]
            )
        ]
        report = mod.audit(
            now=dt(28, 6, 0),
            lookback=timedelta(hours=24),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: [],
        )
        assert report["workflows"] == []
        assert report["expected"] == 0


class TestStaleListingIsNotADrop:
    """`gh run list` is not a consistent read, and the audit accused the innocent.

    Measured 2026-09-04 against an unchanged run history: ten runs of this audit
    inside six minutes produced four different verdicts (1, 1, 1, 1, 1, 2, 2, 3
    drops) with the accused workflow rotating between `monitoring`,
    `googlebot-access-monitor`, `slack-category-digest` and `ai-blogwatcher`.
    `monitoring.yml` was reported `0/2 no delivery observed` while `gh run list`
    showed both of its runs succeeding; re-evaluating it seconds later returned
    `2/2, lag 251-255m`. Pinning `--now` gave five identical verdicts, which is
    what rules out the arithmetic and leaves the listing.

    The bad pages were the hard part: not empty and not an error (40 probe calls,
    0 anomalies), just 100 rows of older history with the recent runs missing. So
    the shape being pinned here is a *plausible* page, not a broken one.
    """

    @staticmethod
    def _daily(filename: str = "a.yml"):
        return [
            mod.WorkflowSchedule(
                filename=filename, name="A", crons=[mod.CronExpr.parse("0 0 * * *")]
            )
        ]

    def test_stale_first_read_does_not_become_a_drop(self):
        """The monitoring.yml case: first page misses the run, second has it.

        Read 1 carries an old row rather than being empty, because that is the
        shape actually measured — a plausible page, not a broken one. It also
        makes `newest_run_observed` load-bearing: reported off the stale read it
        says 08-20, which is the misleading value the field exists to expose.
        """
        pages = [[dt(20, 1, 30)], [dt(20, 1, 30), dt(27, 1, 30)]]

        def runs_for(filename):
            return pages.pop(0)

        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        assert report["dropped"] == 0, "a stale page must not accuse a workflow"
        assert report["delivered"] == 1
        wf = report["workflows"][0]
        assert wf["listing_disagreement"] is True
        assert wf["confirmation"] == "confirmed"
        assert wf["newest_run_observed"] == "2026-08-27T01:30Z"

    def test_a_late_run_in_the_second_read_cannot_manufacture_a_drop(self):
        """The counterexample that killed the union-as-verdict design.

        `ops-orchestrator.yml`'s real crons, 2h minimum gap. The 04:00 cycle ran
        130 minutes late and only read 2 sees it. Recomputing over the union
        raises `last_served` past 09-04T04:00, whose run is then mis-credited
        forward to the 06:00 fire — so the union reports 4 drops where read 1
        reported 3, and the extra one is false.

        Measured before the downgrade-only rule:
            read1 -> dropped 09-02T12:00, 09-02T18:00, 09-03T04:00
            union -> the same three PLUS 09-04T04:00

        The 13 daily workflows in this repo cannot reach this (24h gap > 18h
        settle leaves a pending fire with no later sibling to serve), which is
        why it would have shipped looking right: the only exposed workflow is
        the only one that genuinely drops.
        """
        crons = [mod.CronExpr.parse("0 */6 * * *"), mod.CronExpr.parse("0 4 * * *")]
        schedules = [mod.WorkflowSchedule(filename="ops.yml", name="O", crons=crons)]
        first = [
            datetime(2026, 9, 3, 1, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 3, 7, 30, tzinfo=timezone.utc),
            datetime(2026, 9, 3, 13, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 3, 19, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 4, 2, 43, tzinfo=timezone.utc),
        ]
        late = datetime(2026, 9, 4, 6, 10, tzinfo=timezone.utc)
        pages = [list(first), first + [late]]

        report = mod.audit(
            now=datetime(2026, 9, 4, 6, 20, tzinfo=timezone.utc),
            lookback=timedelta(hours=48),
            settle=timedelta(hours=18),
            schedules=schedules,
            runs_for=lambda f: pages.pop(0),
        )
        wf = report["workflows"][0]
        assert "2026-09-04T04:00Z" not in wf["dropped"]
        assert wf["withheld_accusations"] == ["2026-09-04T04:00Z"]
        assert "2026-09-04T04:00Z" in wf["pending"]
        assert wf["dropped"] == [
            "2026-09-02T12:00Z",
            "2026-09-02T18:00Z",
            "2026-09-03T04:00Z",
        ]
        assert "withheld: 2026-09-04T04:00Z" in mod.format_report(report)

    def test_confirmation_never_raises_the_accusation_count(self):
        """The invariant the whole design rests on, over the staleness model.

        Read 1 is a subset of read 2 — rows missing from the top, never invented
        — which is the shape measured on 2026-09-04. Asserted as a property
        because the counterexample above was found by fuzzing, not by reading:
        a single hand-picked case cannot stand in for a monotonicity claim.
        """
        crons = [mod.CronExpr.parse("0 */6 * * *"), mod.CronExpr.parse("0 4 * * *")]
        schedules = [mod.WorkflowSchedule(filename="ops.yml", name="O", crons=crons)]
        now = datetime(2026, 9, 4, 6, 20, tzinfo=timezone.utc)
        base = [
            datetime(2026, 9, 2, 13, 0, tzinfo=timezone.utc) + timedelta(hours=6 * i)
            for i in range(8)
        ]
        for hidden in range(len(base) + 1):
            visible = base[: len(base) - hidden] if hidden else list(base)
            pages = [list(visible), list(base)]
            single = mod.audit(
                now=now,
                lookback=timedelta(hours=48),
                settle=timedelta(hours=18),
                schedules=schedules,
                runs_for=lambda f, v=visible: list(v),
            )
            merged = mod.audit(
                now=now,
                lookback=timedelta(hours=48),
                settle=timedelta(hours=18),
                schedules=schedules,
                runs_for=lambda f: pages.pop(0),
            )
            assert set(merged["workflows"][0]["dropped"]) <= set(
                single["workflows"][0]["dropped"]
            ), f"confirmation added an accusation when {hidden} row(s) were hidden"

    def test_union_credits_a_run_seen_in_either_read(self):
        """Neither read alone is complete, and the merge is not "trust read 2".

        Read 1 sees the 27th's run and misses the 28th's; read 2 the reverse.
        Taking either page wholesale reports one drop. The union reports none,
        which is the truth: both runs happened.
        """
        pages = [[dt(27, 1, 0)], [dt(28, 2, 0)]]

        def runs_for(filename):
            return pages.pop(0)

        report = mod.audit(
            now=dt(28, 20, 0),
            lookback=timedelta(hours=45),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        assert report["dropped"] == 0
        assert report["delivered"] == 2

    def test_a_genuinely_lost_cycle_survives_both_reads(self):
        """The guard must not have bought quiet by going blind.

        A lost cycle is permanent — GitHub never backfills it — so it is absent
        from every read, and the union of two absences is still an absence. This
        is `ops-orchestrator.yml`'s 2026-09-03T04:00Z drop, which reproduced in
        10 of 10 runs while the false ones rotated.
        """
        calls: list[str] = []

        def runs_for(filename):
            calls.append(filename)
            return []

        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        assert report["dropped"] == 1
        assert calls == ["a.yml", "a.yml"], "the drop must have been re-read"
        assert report["workflows"][0]["listing_disagreement"] is False

    def test_confirming_read_failure_leaves_the_first_verdict_standing(self):
        """One observation and no grounds to overrule it is not a third outcome.

        Discarding the drop would let an unreadable re-read silence a real one;
        promoting it to `unmeasurable` would throw away the only measurement we
        actually have.
        """

        def runs_for(filename):
            if len(calls) == 0:
                calls.append(filename)
                return []
            raise mod.WorkflowNotMeasurable("HTTP 404: not found on the default branch")

        calls: list[str] = []
        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        assert report["dropped"] == 1
        assert report["unmeasurable"] == []

    def test_drop_carries_the_evidence_it_rests_on(self):
        """`0/2 no delivery observed` alone cannot be triaged.

        A reader needs to know whether the listing showed recent activity for
        this workflow at all: "newest run seen: none" is the stale-page
        signature, and a fresh timestamp next to a missing slot is a real skip.
        """
        report = mod.audit(
            now=dt(28, 20, 0),
            lookback=timedelta(hours=45),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=lambda f: [dt(27, 1, 0)],
        )
        wf = report["workflows"][0]
        assert wf["dropped"] == ["2026-08-28T00:00Z"]
        assert wf["newest_run_observed"] == "2026-08-27T01:00Z"
        assert "newest run seen: 2026-08-27T01:00Z" in mod.format_report(report)

    def test_disagreement_is_surfaced_in_the_report_text(self):
        """A silent correction is how a flaky source passes for a reliable one."""
        pages = [[], [dt(27, 1, 30)]]
        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=lambda f: pages.pop(0),
        )
        assert "listings disagreed" in mod.format_report(report)

    def test_duplicate_rows_in_the_first_read_do_not_suppress_the_correction(self):
        """`len(union) != len(actual)` compared a set size against a list size.

        With a duplicate timestamp in read 1, `len(set(actual)) < len(actual)`
        made the lengths match even though read 2 supplied a genuine run — so
        the recompute was skipped, the false drop survived, and
        `listing_disagreement` reported clean. Two runs of one workflow can
        share a `createdAt` second whenever two cron entries coincide; none of
        this repo's 14 collide today, which makes this one cron edit away rather
        than impossible.
        """
        pages = [
            [dt(20, 1, 30), dt(20, 1, 30)],
            [dt(20, 1, 30), dt(27, 1, 30)],
        ]
        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=lambda f: pages.pop(0),
        )
        assert report["dropped"] == 0
        assert report["workflows"][0]["listing_disagreement"] is True

    def test_a_stale_page_served_twice_is_marked_confirmed_not_corrected(self):
        """The fix is a no-op when both reads are the same stale page.

        Nothing can be done about that from here, but the report must not imply
        two independent observations agreed on fresh data. `newest_run_observed`
        predating the window is the only signature available, so it has to be
        present and truthful.
        """
        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=lambda f: [dt(20, 1, 30)],
        )
        wf = report["workflows"][0]
        assert wf["dropped"] == ["2026-08-27T00:00Z"]
        assert wf["confirmation"] == "confirmed"
        assert wf["listing_disagreement"] is False
        assert wf["newest_run_observed"] == "2026-08-20T01:30Z"

    def test_a_failed_confirming_read_is_labelled_not_silently_equated(self):
        """One observation and two must not produce identical reports.

        Before `confirmation`, a drop whose re-read raised and a drop confirmed
        by two agreeing reads were byte-identical in the report dict — which is
        the opposite of carrying the evidence the verdict rests on.
        """
        calls: list[str] = []

        def runs_for(filename):
            if not calls:
                calls.append(filename)
                return [dt(20, 1, 30)]
            raise mod.WorkflowNotMeasurable("HTTP 404: not found on the default branch")

        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        wf = report["workflows"][0]
        assert wf["dropped"] == ["2026-08-27T00:00Z"]
        assert wf["confirmation"] == "unconfirmed"
        assert report["unmeasurable"] == []
        assert "rests on a single listing" in mod.format_report(report)

    def test_a_transport_error_on_the_re_read_does_not_abort_the_audit(self):
        """This job's contract is that it never goes red, and `main()` returns 2.

        `fetch_schedule_runs` raises a plain `RuntimeError` for a 502 or a rate
        limit — not `WorkflowNotMeasurable`. Letting it escape empties
        `report.json`, the workflow's `json.load` then fails, and
        `ops-orchestrator`'s `AUTO_RECOVER_GHA=true` re-runs the job forever
        over a cycle lost hours ago. The re-read is a new call on exactly the
        days something is already wrong, so it widens that exposure.
        """
        calls: list[str] = []

        def runs_for(filename):
            if not calls:
                calls.append(filename)
                return []
            raise RuntimeError("gh run list failed for a.yml: HTTP 502")

        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        assert report["dropped"] == 1
        assert report["workflows"][0]["confirmation"] == "unconfirmed"

    def test_pending_alone_does_not_buy_a_second_read(self):
        """The cost guard, exercised against the realistic over-fetch.

        A fully-delivered workflow is the easy case. Pending is the common one
        here — 18h settle over a 30-100 minute baseline lag means something is
        usually in flight — so `if dropped or pending:` is the mutation that
        would actually double this audit's API traffic, and it has to fail.
        """
        calls: list[str] = []

        def runs_for(filename):
            calls.append(filename)
            return [dt(27, 1, 30)]

        report = mod.audit(
            now=dt(28, 7, 0),
            lookback=timedelta(hours=32),
            settle=timedelta(hours=18),
            schedules=self._daily(),
            runs_for=runs_for,
        )
        assert report["pending"] == 1
        assert report["dropped"] == 0
        assert calls == ["a.yml"]
