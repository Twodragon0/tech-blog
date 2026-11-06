"""Bounded offline-testable T1/T2 execution, with an explicit in-memory cache.

No persistence, default network transport, environment credentials, or publisher.
All clock, sleep, and jitter behavior is supplied by the caller.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from scripts.news.translation_contract import (
    TranslationContractError,
    TranslationRequest,
    TranslationResult,
)
from scripts.news.translation_provider import (
    ProviderError,
    Transport,
    build_request,
    translate,
)


class ExecutionLimitError(ValueError):
    """Elapsed-time budget exhausted; no more calls or sleeps are permitted."""


def _finite_number(
    value: object, name: str, *, minimum: float, maximum: float
) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not minimum <= value <= maximum
    ):
        raise TranslationContractError(f"Invalid execution configuration: {name}")
    return float(value)


@dataclass(frozen=True)
class ExecutionPolicy:
    max_attempts: int = 3
    max_elapsed: float = 60
    timeout_seconds: float = 30
    base_delay: float = 1
    max_delay: float = 8

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_attempts, bool)
            or not isinstance(self.max_attempts, int)
            or not 1 <= self.max_attempts <= 5
        ):
            raise TranslationContractError("Attempts must be an integer from 1 to 5")
        _finite_number(self.max_elapsed, "max_elapsed", minimum=0.001, maximum=600)
        _finite_number(
            self.timeout_seconds, "timeout_seconds", minimum=0.001, maximum=120
        )
        _finite_number(self.base_delay, "base_delay", minimum=0, maximum=120)
        _finite_number(self.max_delay, "max_delay", minimum=0.001, maximum=120)


class TranslationCache:
    """Process-local validated results only; caller must use a shared clock basis."""

    def __init__(self, *, ttl_seconds: float) -> None:
        self.ttl_seconds = _finite_number(
            ttl_seconds, "ttl_seconds", minimum=0.001, maximum=86_400
        )
        self._entries: dict[str, tuple[float, TranslationResult]] = {}

    def __repr__(self) -> str:
        return f"TranslationCache(entries={len(self._entries)})"

    def keys(self) -> tuple[str, ...]:
        """Return hashed identities only, for inspection without source or credentials."""
        return tuple(self._entries)

    def _get(self, key: str, now: float) -> TranslationResult | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        stored_at, result = entry
        if now < stored_at or now >= stored_at + self.ttl_seconds:
            del self._entries[key]
            return None
        return result

    def _put(self, key: str, now: float, result: TranslationResult) -> None:
        # Called only after translate() has passed T1 validation and the deadline.
        self._entries[key] = (now, result)


def _cache_key(
    article: TranslationRequest, provider: str, model: str, rules_version: str
) -> str:
    if (
        not isinstance(rules_version, str)
        or not rules_version.strip()
        or len(rules_version) > 128
    ):
        raise TranslationContractError("Explicit bounded rules version required")
    source = {**article.source_data(), "protected_terms": article.protected_terms}
    source_hash = hashlib.sha256(
        json.dumps(source, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    identity = [article.canonical_url, source_hash, rules_version, provider, model]
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()


def execute_translation(
    article: TranslationRequest,
    *,
    provider: str,
    model: str,
    credentials: Mapping[str, str],
    rules_version: str,
    transport: Transport,
    cache: TranslationCache,
    policy: ExecutionPolicy,
    clock: Callable[[], float],
    sleeper: Callable[[float], None],
    jitter: Callable[[], float],
) -> TranslationResult:
    """Use a validated cache hit or bounded attempts against the SAME provider.

    A transport must honor the supplied timeout. Synchronous Python cannot abort
    an arbitrary injected callable; late success is rejected rather than cached.
    """
    selected, _ = build_request(
        article,
        provider=provider,
        model=model,
        credentials=credentials,
        timeout_seconds=policy.timeout_seconds,
    )
    key = _cache_key(article, selected, model, rules_version)
    start = _finite_number(clock(), "clock", minimum=0, maximum=1e15)
    last_tick = start

    def tick() -> float:
        nonlocal last_tick
        current = _finite_number(clock(), "clock", minimum=0, maximum=1e15)
        if current < last_tick:
            raise TranslationContractError("Execution clock moved backwards")
        last_tick = current
        return current

    hit = cache._get(key, start)
    if hit is not None:
        return hit
    for attempt in range(1, policy.max_attempts + 1):
        remaining = policy.max_elapsed - (tick() - start)
        if remaining <= 0:
            raise ExecutionLimitError("Translation elapsed budget exhausted")
        try:
            result = translate(
                article,
                provider=selected,
                model=model,
                credentials=credentials,
                transport=transport,
                timeout_seconds=min(policy.timeout_seconds, remaining),
            )
        except ProviderError as error:
            if not error.retryable or attempt == policy.max_attempts:
                raise
            elapsed = tick() - start
            fraction = _finite_number(jitter(), "jitter", minimum=0, maximum=1)
            delay = min(policy.max_delay, policy.base_delay * 2 ** (attempt - 1)) * (
                0.5 + 0.5 * fraction
            )
            if elapsed + delay >= policy.max_elapsed:
                raise ExecutionLimitError(
                    "Translation retry exceeds elapsed budget"
                ) from None
            sleeper(delay)
            continue
        finished = tick()
        if finished - start >= policy.max_elapsed:
            raise ExecutionLimitError("Translation result arrived after elapsed budget")
        cache._put(key, finished, result)
        return result
    raise AssertionError("Validated attempt count guarantees an attempt")
