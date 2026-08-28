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
