"""Offline translation contracts; no provider invocation or publication side effects.

This validates structural and lexical preservation, not semantic faithfulness.
Source strings remain untrusted data, including strings that resemble instructions.
"""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from urllib.parse import urlsplit

Provider = Literal["claude", "openai"]
MAX_SOURCE_CHARS = 20_000
MAX_OUTPUT_CHARS = 10_000
_KOREAN = re.compile(r"[가-힣]")
_NUMBERS = re.compile(r"\d+(?:[.,:/-]\d+)*(?:%)?")
_CVES = re.compile(r"CVE-\d{4}-\d{4,}", re.IGNORECASE)


class TranslationContractError(ValueError):
    """Input, configuration, or translated output violates the contract."""


def select_provider(provider: str, credentials: Mapping[str, str]) -> Provider:
    """Require explicit selection and its key; never choose a fallback or call it."""
    keys = {"claude": "CLAUDE_API_KEY", "openai": "OPENAI_API_KEY"}
    if provider not in keys:
        raise TranslationContractError("Select claude or openai explicitly")
    if not credentials.get(keys[provider], "").strip():
        raise TranslationContractError("Selected provider credential is missing")
    return cast(Provider, provider)


def _text(value: object, field: str, limit: int, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise TranslationContractError(f"Invalid text field: {field}")
    if len(value) > limit or "\x00" in value:
        raise TranslationContractError(f"Text limit or encoding violation: {field}")
    return value


def _canonical_url(value: str) -> None:
    """Validate URL shape offline; DNS/redirect safety belongs to fetch validation."""
    try:
        parts = urlsplit(value)
        host = parts.hostname
        port = parts.port
        if (
            parts.scheme != "https"
            or not host
            or parts.username is not None
            or parts.password is not None
            or parts.fragment
            or port not in (None, 443)
            or any(c.isspace() for c in value)
            or "\\" in value
            or host.lower() == "localhost"
            or host.lower().endswith((".localhost", ".local"))
        ):
            raise ValueError
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is not None and not address.is_global:
            raise ValueError
    except ValueError:
        raise TranslationContractError("Invalid canonical source URL") from None


@dataclass(frozen=True)
class TranslationRequest:
    article_id: str
    canonical_url: str
    source_title: str
    source_summary: str
    source_name: str
    published_at: datetime
    protected_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field in (
            "article_id",
            "canonical_url",
            "source_title",
            "source_summary",
            "source_name",
        ):
            _text(getattr(self, field), field, MAX_SOURCE_CHARS)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", self.article_id):
            raise TranslationContractError("Invalid article ID")
        _canonical_url(self.canonical_url)
        if (
            not isinstance(self.published_at, datetime)
            or self.published_at.utcoffset() is None
        ):
            raise TranslationContractError(
                "Source publication timestamp needs timezone"
            )
        if len(self.source_title) + len(self.source_summary) > MAX_SOURCE_CHARS:
            raise TranslationContractError("Combined source exceeds input limit")
        if not isinstance(self.protected_terms, tuple):
            raise TranslationContractError("Protected terms must be an immutable tuple")
        source = self.source_title + "\n" + self.source_summary
        for term in self.protected_terms:
            _text(term, "protected_term", 200)
            if term not in source:
                raise TranslationContractError("Protected term absent from source")

    def source_data(self) -> dict[str, str]:
        """Return inert source facts, not a model prompt or executable instruction."""
        return {
            "article_id": self.article_id,
            "canonical_url": self.canonical_url,
            "source_title": self.source_title,
            "source_summary": self.source_summary,
            "source_name": self.source_name,
            "published_at": self.published_at.isoformat(),
        }


@dataclass(frozen=True)
class TranslationResult:
    article_id: str
    canonical_url: str
    korean_title: str
    korean_summary: str
    editorial_note: str
    status: Literal["validated"] = "validated"


def validate_result(
    request: TranslationRequest, output: Mapping[str, object]
) -> TranslationResult:
    """Fail closed on structure, identity, Korean, or protected-fact drift.

    Accepted status is a lexical validation outcome, not approval to publish.
    Editorial notes remain separate and are never used to satisfy source facts.
    """
    fields = {
        "article_id",
        "canonical_url",
        "korean_title",
        "korean_summary",
        "editorial_note",
    }
    if not isinstance(output, Mapping) or set(output) != fields:
        raise TranslationContractError("Translation output fields do not match schema")
    values = {
        field: _text(
            output[field], field, MAX_OUTPUT_CHARS, empty=field == "editorial_note"
        )
        for field in fields
    }
    if sum(map(len, values.values())) > MAX_OUTPUT_CHARS:
        raise TranslationContractError("Combined output exceeds limit")
    if values["article_id"] != request.article_id:
        raise TranslationContractError("Article ID mismatch")
    if values["canonical_url"] != request.canonical_url:
        raise TranslationContractError("Canonical source URL mismatch")
    for field in ("korean_title", "korean_summary"):
        if not _KOREAN.search(values[field]):
            raise TranslationContractError(f"Korean text required: {field}")
    source = request.source_title + "\n" + request.source_summary
    translated = values["korean_title"] + "\n" + values["korean_summary"]
    if set(_NUMBERS.findall(source)) != set(_NUMBERS.findall(translated)):
        raise TranslationContractError("Numeric facts changed")
    if set(_CVES.findall(source)) != set(_CVES.findall(translated)):
        raise TranslationContractError("CVE identifiers changed")
    if any(term not in translated for term in request.protected_terms):
        raise TranslationContractError("Protected source term changed")
    return TranslationResult(
        article_id=values["article_id"],
        canonical_url=values["canonical_url"],
        korean_title=values["korean_title"],
        korean_summary=values["korean_summary"],
        editorial_note=values["editorial_note"],
    )
