"""Deterministic cache and retry tests; all provider exchanges are injected."""

import json
from dataclasses import replace
from datetime import datetime, timezone

import pytest
import requests

from scripts.news.translation_contract import (
    TranslationContractError,
    TranslationRequest,
)
from scripts.news.translation_execution import (
    ExecutionLimitError,
    ExecutionPolicy,
    TranslationCache,
    execute_translation,
)
from scripts.news.translation_provider import ProviderError, ProviderResponse

KEYS = {"CLAUDE_API_KEY": "secret-claude", "OPENAI_API_KEY": "secret-openai"}


class Clock:
    def __init__(self):
        self.now = 0.0
        self.delays = []

    def __call__(self):
        return self.now

    def sleep(self, delay):
        self.delays.append(delay)
        self.now += delay


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def block(*args, **kwargs):
        raise AssertionError("No live network")

    monkeypatch.setattr(requests.sessions.Session, "request", block)


@pytest.fixture
def article():
    return TranslationRequest(
        "news:1",
        "https://vendor.test/news",
        "Acme v2.4 CVE-2026-12345",
        "Cost $30.",
        "Acme",
        datetime(2026, 11, 6, tzinfo=timezone.utc),
        ("Acme", "v2.4", "$30"),
    )


def good(article, provider="openai"):
    output = {
        "article_id": article.article_id,
        "canonical_url": article.canonical_url,
        "korean_title": "Acme v2.4 CVE-2026-12345 수정",
        "korean_summary": "비용은 $30이다.",
        "editorial_note": "",
    }
    text = json.dumps(output)
    envelope = (
        {"choices": [{"finish_reason": "stop", "message": {"content": text}}]}
        if provider == "openai"
        else {"stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}
    )
    return ProviderResponse(200, json.dumps(envelope))


def run(article, transport, timer, cache, **kwargs):
    options = dict(
        provider="openai",
        model="test-model",
        credentials=KEYS,
        rules_version="rules-1",
        transport=transport,
        clock=timer,
        sleeper=timer.sleep,
        jitter=lambda: 1.0,
        cache=cache,
        policy=ExecutionPolicy(),
    )
    options.update(kwargs)
    return execute_translation(article, **options)


def test_cache_hit_no_second_transport_and_no_secret_key(article):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        return good(article)

    assert run(article, transport, clock, cache).status == "validated"
    assert run(article, transport, clock, cache).status == "validated"
    assert len(calls) == 1
    assert "secret-" not in repr(cache)
    assert all("secret-" not in key for key in cache.keys())


@pytest.mark.parametrize(
    "change",
    [
        "source",
        "url",
        "id",
        "terms",
        "time",
        "source-name",
        "rules",
        "model",
        "provider",
    ],
)
def test_key_invalidates_all_source_and_execution_identity(article, change):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def first(request):
        calls.append(request)
        return good(article)

    run(article, first, clock, cache)
    new, extra = article, {}
    if change == "source":
        new = replace(article, source_summary=article.source_summary + " New facts.")
    elif change == "url":
        new = replace(article, canonical_url="https://vendor.test/new")
    elif change == "id":
        new = replace(article, article_id="news:2")
    elif change == "terms":
        new = replace(article, protected_terms=("Acme",))
    elif change == "time":
        new = replace(article, published_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
    elif change == "source-name":
        new = replace(article, source_name="Other source")
    elif change == "rules":
        extra = {"rules_version": "rules-2"}
    elif change == "model":
        extra = {"model": "other-model"}
    else:
        extra = {"provider": "claude"}

    def second(request):
        calls.append(request)
        return good(new, extra.get("provider", "openai"))

    run(new, second, clock, cache, **extra)
    assert len(calls) == 2


def test_expiry_uses_injected_clock(article):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        return good(article)

    run(article, transport, clock, cache)
    clock.now = 10
    run(article, transport, clock, cache)
    assert len(calls) == 2


@pytest.mark.parametrize(
    "failure", [429, 500, 503, TimeoutError, requests.exceptions.Timeout]
)
def test_retryable_only_and_success_cached(article, failure):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        if len(calls) == 1:
            if isinstance(failure, int):
                return ProviderResponse(failure, "secret body")
            raise failure("secret source")
        return good(article)

    run(article, transport, clock, cache)
    assert len(calls) == 2
    assert clock.delays == [1.0]
    run(article, transport, clock, cache)
    assert len(calls) == 2


@pytest.mark.parametrize("failure", [401, 403, 400, 200])
def test_nonretryable_or_bad_output_never_cached(article, failure):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        return ProviderResponse(failure, "invalid JSON secret")

    with pytest.raises(ProviderError):
        run(article, transport, clock, cache)
    assert len(calls) == 1
    assert clock.delays == []
    assert list(cache.keys()) == []


def test_bounded_attempts_and_capped_jitter_backoff(article):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        return ProviderResponse(429, "")

    with pytest.raises(ProviderError):
        run(
            article,
            transport,
            clock,
            cache,
            policy=ExecutionPolicy(max_attempts=4, base_delay=2, max_delay=3),
            jitter=lambda: 0.0,
        )
    assert len(calls) == 4
    assert clock.delays == [1.0, 1.5, 1.5]


def test_elapsed_budget_prevents_sleep_or_extra_call(article):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        clock.now += 1
        return ProviderResponse(503, "")

    with pytest.raises(ExecutionLimitError):
        run(
            article,
            transport,
            clock,
            cache,
            policy=ExecutionPolicy(max_elapsed=1.5, base_delay=1),
        )
    assert len(calls) == 1
    assert clock.delays == []


def test_per_attempt_timeout_capped_to_remaining_budget_and_late_success_rejected(
    article,
):
    clock, cache = Clock(), TranslationCache(ttl_seconds=10)

    def transport(request):
        assert request.timeout_seconds == 2
        clock.now = 3
        return good(article)

    with pytest.raises(ExecutionLimitError):
        run(article, transport, clock, cache, policy=ExecutionPolicy(max_elapsed=2))
    assert list(cache.keys()) == []


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"max_attempts": True},
        {"max_attempts": 6},
        {"max_elapsed": 0},
        {"max_elapsed": float("inf")},
        {"base_delay": -1},
        {"max_delay": 0},
        {"timeout_seconds": "30"},
    ],
)
def test_invalid_policy(kwargs):
    with pytest.raises(TranslationContractError):
        ExecutionPolicy(**kwargs)


def test_missing_key_even_on_cache_hit(article):
    clock, cache = Clock(), TranslationCache(ttl_seconds=10)
    run(article, lambda _: good(article), clock, cache)
    with pytest.raises(TranslationContractError):
        run(article, lambda _: pytest.fail("called"), clock, cache, credentials={})


def test_credential_rotation_not_part_of_cache_identity(article):
    clock, cache = Clock(), TranslationCache(ttl_seconds=10)
    run(article, lambda _: good(article), clock, cache)
    result = run(
        article,
        lambda _: pytest.fail("cache miss"),
        clock,
        cache,
        credentials={"OPENAI_API_KEY": "rotated-secret"},
    )
    assert result.status == "validated"
    assert "rotated-secret" not in repr(cache)


@pytest.mark.parametrize("ttl", [0, -1, True, "10", float("nan")])
def test_invalid_cache_ttl(ttl):
    with pytest.raises(TranslationContractError):
        TranslationCache(ttl_seconds=ttl)


@pytest.mark.parametrize("fraction", [-1, 2, float("nan"), True])
def test_invalid_jitter_does_not_retry(article, fraction):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        return ProviderResponse(429, "")

    with pytest.raises(TranslationContractError):
        run(article, transport, clock, cache, jitter=lambda: fraction)
    assert len(calls) == 1
    assert clock.delays == []


def test_sleep_overrun_cannot_start_another_attempt(article):
    clock, cache, calls = Clock(), TranslationCache(ttl_seconds=10), []

    def transport(request):
        calls.append(request)
        return ProviderResponse(503, "")

    def oversleep(delay):
        clock.now += 100

    with pytest.raises(ExecutionLimitError):
        run(
            article,
            transport,
            clock,
            cache,
            sleeper=oversleep,
            policy=ExecutionPolicy(max_elapsed=2),
        )
    assert len(calls) == 1


def test_invalid_rules_before_transport(article):
    with pytest.raises(TranslationContractError):
        run(
            article,
            lambda _: pytest.fail("called"),
            Clock(),
            TranslationCache(ttl_seconds=10),
            rules_version="",
        )


def test_backward_clock_rejected_before_transport(article):
    ticks = iter([2.0, 1.0])
    with pytest.raises(TranslationContractError, match="backwards"):
        run(
            article,
            lambda _: pytest.fail("called"),
            Clock(),
            TranslationCache(ttl_seconds=10),
            clock=lambda: next(ticks),
        )
