"""Opt-in publisher preflight using an injected offline-testable T4 executor.

No provider, transport, credentials, model, or CLI activation is selected here.
"""

from __future__ import annotations

import copy
import hashlib
import html
import json
import re
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from scripts.lib.security import mask_sensitive_info
from scripts.news.translation_contract import (
    TranslationContractError,
    TranslationRequest,
    TranslationResult,
    validate_result,
)


class TranslatedArticle(dict[str, Any]):
    """Trusted in-process renderer item; a decoded feed dict cannot forge it."""

    __slots__ = ("_translation",)

    def __init__(self, source: dict, result: TranslationResult) -> None:
        super().__init__(source)
        self._translation = result

    @property
    def translation(self) -> TranslationResult:
        return self._translation


class TranslationPublicationError(ValueError):
    """Safe preflight failure; no partial translated batch may be published."""


@dataclass(frozen=True)
class PublicationTranslation:
    executor: Callable[[TranslationRequest], TranslationResult]
    max_articles: int
    rejection_dir: Path

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_articles, bool)
            or not isinstance(self.max_articles, int)
            or not 1 <= self.max_articles <= 50
        ):
            raise TranslationContractError("Publication article cap must be 1..50")
        if not isinstance(self.rejection_dir, Path):
            raise TranslationContractError("Explicit rejection directory required")

    def _request(self, item: Mapping[str, Any]) -> TranslationRequest:
        url = item.get("canonical_url") or item.get("url", "")
        if item.get("url") != url:
            raise TranslationContractError("Canonical URL and rendered URL differ")
        identity = item.get("id") or url
        if not isinstance(identity, str):
            raise TranslationContractError("Source identity must be text")
        published = item.get("published_date")
        if isinstance(published, str):
            published = datetime.fromisoformat(published.replace("Z", "+00:00"))
        if not isinstance(published, datetime):
            raise TranslationContractError("Source publication timestamp required")
        return TranslationRequest(
            article_id=hashlib.sha256(identity.encode()).hexdigest(),
            canonical_url=url,
            source_title=item.get("title", ""),
            source_summary=item.get("summary", ""),
            source_name=item.get("source", ""),
            published_at=published,
            protected_terms=tuple(item.get("protected_terms", ())),
        )

    def _preserve(self, categorized: Mapping[str, list[dict]], reason: str) -> None:
        # Whitelist and bound diagnostic input. Never dump arbitrary metadata,
        # provider exceptions, credentials, headers, or unbounded source bodies.
        inputs: list[dict[str, object]] = []
        for category, items in categorized.items():
            for item in items:
                if len(inputs) >= self.max_articles:
                    break
                if not isinstance(item, Mapping):
                    inputs.append(
                        {"category": str(category)[:200], "invalid_item": True}
                    )
                    continue
                safe = {
                    key: mask_sensitive_info(str(item.get(key, ""))[:20_000])
                    for key in (
                        "id",
                        "url",
                        "title",
                        "summary",
                        "source",
                        "published_date",
                    )
                }
                if isinstance(item, TranslatedArticle):
                    original = item.get("translation_source", {})
                    for field, source_field in (
                        ("title", "source_title"),
                        ("summary", "source_summary"),
                        ("source", "source_name"),
                    ):
                        safe[field] = mask_sensitive_info(
                            str(original.get(source_field, ""))[:20_000]
                        )
                try:
                    parsed = urlsplit(safe["url"])
                    safe["url"] = urlunsplit(
                        (parsed.scheme, parsed.hostname or "", parsed.path, "", "")
                    )
                except ValueError:
                    safe["url"] = "[invalid-url]"
                inputs.append({"category": str(category)[:200], "source": safe})
        artifact = {
            "status": "failed",
            "reason": reason,
            "inputs": inputs,
            "input_limit": self.max_articles,
        }
        text = json.dumps(artifact, ensure_ascii=False, indent=2)
        self.rejection_dir.mkdir(parents=True, exist_ok=True)
        self.rejection_dir.chmod(0o700)
        target = self.rejection_dir / f"translation-rejected-{uuid.uuid4().hex}.json"
        with target.open("x", encoding="utf-8") as file:
            target.chmod(0o600)
            file.write(text)

    def prepare(
        self, categorized: Mapping[str, list[dict]], *, legacy_ai_disabled: bool = True
    ) -> dict[str, list[dict]]:
        """Translate every unique render candidate or fail before publication.

        Duplicate source IDs/URLs must agree on all T1 source facts. Non-source
        metadata stays on cloned items and never mutates the caller's feed.
        """
        reason = "input_contract"
        try:
            if not legacy_ai_disabled:
                raise TranslationContractError(
                    "Opt-in translation requires legacy AI disabled"
                )
            planned: list[tuple[str, dict, TranslationRequest]] = []
            by_url: dict[str, TranslationRequest] = {}
            by_id: dict[str, TranslationRequest] = {}
            for category, items in categorized.items():
                for item in items:
                    request = self._request(item)
                    prior = by_url.get(request.canonical_url) or by_id.get(
                        request.article_id
                    )
                    if prior is not None:
                        if prior != request:
                            raise TranslationContractError(
                                "Conflicting source identity"
                            )
                        continue
                    by_url[request.canonical_url] = request
                    by_id[request.article_id] = request
                    planned.append((category, item, request))
                    if len(planned) > self.max_articles:
                        raise TranslationContractError(
                            "Render candidates exceed article cap"
                        )
            prepared: dict[str, list[dict]] = {category: [] for category in categorized}
            reason = "translation_failed"
            for category, item, request in planned:
                result = self.executor(request)
                if not isinstance(result, TranslationResult):
                    raise TranslationContractError(
                        "Executor did not return a translation result"
                    )
                checked = validate_result(
                    request,
                    {
                        field: getattr(result, field)
                        for field in (
                            "article_id",
                            "canonical_url",
                            "korean_title",
                            "korean_summary",
                            "editorial_note",
                        )
                    },
                )
                if len(checked.korean_summary) > 200:
                    raise TranslationContractError(
                        "Validated summary exceeds renderer's lossless card limit"
                    )
                clone = TranslatedArticle(copy.deepcopy(item), checked)
                clone["translation_source"] = request.source_data()
                clone["translation_editorial_note"] = checked.editorial_note
                clone["title"] = checked.korean_title
                clone["summary"] = checked.korean_summary
                prepared[category].append(clone)
            return prepared
        except Exception:
            try:
                self._preserve(categorized, reason)
            except OSError:
                raise TranslationPublicationError(
                    "Translation failed; rejection artifact could not be saved"
                ) from None
            raise TranslationPublicationError(
                "Translation preflight failed; input preserved for review"
            ) from None

    def rendered_items(
        self, content: str, categorized: Mapping[str, list[dict]]
    ) -> list[dict]:
        """Track only validated source cards that the generated body contains.

        Source-card absence/unknown URLs require review; reference links and
        unrendered category candidates are not evidence of published articles.
        """
        from scripts.check_duplicate_card_summary import CARD_RE

        try:
            known = {}
            for items in categorized.values():
                for item in items:
                    if (
                        not isinstance(item, TranslatedArticle)
                        or item.get("url") != item.translation.canonical_url
                    ):
                        raise TranslationContractError(
                            "Rendered source candidates must be validated"
                        )
                    known[item["url"]] = item
            rendered: dict[str, dict] = {}
            for card in CARD_RE.finditer(content):
                attributes = re.findall(
                    r"\burl\s*=\s*([\"'])(.*?)\1", card.group(), re.DOTALL
                )
                if len(attributes) != 1:
                    raise TranslationContractError(
                        "Source card requires exactly one URL"
                    )
                url = html.unescape(attributes[0][1])
                if url not in known:
                    raise TranslationContractError(
                        "Source card URL not in validated inputs"
                    )
                rendered[url] = known[url]
            if not rendered:
                raise TranslationContractError(
                    "No validated source cards were rendered"
                )
            return list(rendered.values())
        except Exception:
            try:
                self._preserve(categorized, "rendered_sources")
            except OSError:
                raise TranslationPublicationError(
                    "Source rendering failed; rejection artifact could not be saved"
                ) from None
            raise TranslationPublicationError(
                "Source card preflight failed; input preserved for review"
            ) from None
