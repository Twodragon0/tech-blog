#!/usr/bin/env python3
"""`--workers` must not let one thread strip another's socket timeout.

The defect
----------
`socket.setdefaulttimeout` is process-global. `fetch_rss_feed` used to save and
restore it around each feed, which was harmless while collection was sequential.
`--workers 4` landed on 2026-09-19 (in BOTH production callers —
`ai-blogwatcher.yml` and `morning_autopost_cron.sh`) and made that a race.

Reproduced 2026-09-21 by constructing the interleaving — a thread that read
`old=15` finishing last:

    T1 saw 15.0 at fetch time   T1 restored None
    T2 saw None at fetch time   T2 restored 15.0
    process global afterwards:  15.0

Two consequences, both measured:

1. A thread still fetching sees the global reset to `None`, so its
   `feedparser.parse(url)` fallback — the one path with no per-call timeout —
   runs unbounded. That is exactly the hang the 10s timeout was introduced to
   prevent. `ai-blogwatcher.yml` caps the whole step with `timeout 480`;
   `morning_autopost_cron.sh` has no outer bound and `|| true`, so there a hang
   stalls the cron silently.
2. The global leaks after collection finishes.

The first probe of this did NOT reproduce it, because every thread writes the
same value and most interleavings are therefore harmless. It is order-dependent,
not deterministic — with 30+ sources and 4 workers it occurs often, but a test
must construct the order rather than hope for it.

The fix: `fetch_all_news` sets the global once, before any worker starts and
after they all join, and `fetch_rss_feed` never touches it.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

import collect_tech_news as ctn  # noqa: E402

from scripts.lib.source_text import without_comments  # noqa: E402


def _fn_source(name: str) -> str:
    """A function's source with commentary folded away.

    Read through the shared fold, not raw: this module's own explanation quotes
    `socket.setdefaulttimeout` repeatedly, and a substring scan cannot tell a
    call from prose about a call.
    """
    import inspect

    return without_comments(inspect.getsource(getattr(ctn, name)), suffix=".py")


def test_fetch_rss_feed_does_not_touch_the_global_timeout() -> None:
    """The per-feed save/restore is what made `--workers` unsafe."""
    assert "setdefaulttimeout" not in _fn_source("fetch_rss_feed"), (
        "fetch_rss_feed mutates the process-global socket timeout again. Run "
        "under several workers, one thread's restore strips a sibling's timeout "
        "mid-fetch and the feedparser fallback then waits forever."
    )


def test_fetch_all_news_sets_it_once_outside_the_pool() -> None:
    """Someone has to set it — `feedparser.parse(url)` has no timeout argument.

    Doing it in `fetch_all_news` is safe because that runs single-threaded
    before the pool starts and after it joins.
    """
    src = _fn_source("fetch_all_news")
    assert src.count("setdefaulttimeout") == 2, (
        "expected exactly one set and one restore in fetch_all_news; found "
        f"{src.count('setdefaulttimeout')}."
    )
    assert "finally:" in src, (
        "the restore is not in a finally block, so a worker raising out of the "
        "pool would leak the global into whatever runs next."
    )


@pytest.mark.parametrize("workers", [1, 4])
def test_global_timeout_is_restored_after_collection(workers: int) -> None:
    """Whatever it was before, it must be that again afterwards."""
    sentinel = 3.5
    previous = socket.getdefaulttimeout()
    socket.setdefaulttimeout(sentinel)
    try:
        with patch.object(ctn, "_fetch_source_item", return_value=[]):
            ctn.fetch_all_news(sources=None, hours=1, feed_timeout=11, workers=workers)
        assert socket.getdefaulttimeout() == sentinel, (
            f"collection left the process-global socket timeout at "
            f"{socket.getdefaulttimeout()} instead of {sentinel}."
        )
    finally:
        socket.setdefaulttimeout(previous)


def test_workers_see_the_configured_timeout_throughout() -> None:
    """The value must hold for the whole run, not just until the first finisher.

    This is the failure that matters: a slow source entering its feedparser
    fallback late used to find the global already reset to `None`.
    """
    observed: list[float | None] = []

    def slow_then_fast(source_key, source_config, hours, feed_timeout):
        import time

        # Stagger so some workers finish long before others, which is the
        # interleaving that broke the old code.
        time.sleep(0.05 if "slow" in source_key else 0.0)
        observed.append(socket.getdefaulttimeout())
        return []

    sources = {f"s{i}": {"name": f"s{i}"} for i in range(6)}
    sources["slow"] = {"name": "slow"}

    previous = socket.getdefaulttimeout()
    socket.setdefaulttimeout(None)
    try:
        with (
            patch.object(ctn, "NEWS_SOURCES", sources),
            patch.object(ctn, "_fetch_source_item", slow_then_fast),
        ):
            ctn.fetch_all_news(sources=None, hours=1, feed_timeout=11, workers=4)
    finally:
        socket.setdefaulttimeout(previous)

    assert observed, "no worker ran"
    assert all(v == 11 for v in observed), (
        f"workers saw {sorted(set(observed))} rather than 11 throughout. A "
        "sibling restored the previous value while others were still fetching."
    )


def test_both_production_callers_pass_workers() -> None:
    """Pinned so the thread-safety requirement is not theoretical.

    If concurrency is ever removed, this test should be removed with it — not
    left asserting a property nothing exercises.
    """
    workflow = (REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml").read_text(
        encoding="utf-8"
    )
    cron = (REPO_ROOT / "scripts" / "morning_autopost_cron.sh").read_text(
        encoding="utf-8"
    )
    for name, text in (
        ("ai-blogwatcher.yml", workflow),
        ("morning_autopost_cron.sh", cron),
    ):
        assert "--workers" in without_comments(text, suffix=Path(name).suffix), (
            f"{name} no longer passes --workers. If collection went back to "
            "sequential, drop this file's thread-safety guards too."
        )
