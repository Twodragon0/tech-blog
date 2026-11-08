"""Secret-free T6 fixture validation. No live transport or publish operation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.news import config
from scripts.news.content_generator import (
    _run_post_quality_gate,
    generate_tech_blog_content,
)
from scripts.news.qa_gate import validate_stats_consistency
from scripts.news.translation_budget import BudgetLedger
from scripts.news.translation_execution import (
    ExecutionPolicy,
    TranslationCache,
    execute_translation,
)
from scripts.news.translation_production import ProductionBudgetLedger
from scripts.news.translation_provider import ProviderRequest, ProviderResponse
from scripts.news.translation_publication import PublicationTranslation


class ValidationError(ValueError):
    """Safe offline validation failure; no arbitrary source/provider exception."""


def _private_write(path: Path, text: str) -> None:
    with path.open("x", encoding="utf-8") as file:
        path.chmod(0o600)
        file.write(text)


def _load_fixture(path: Path) -> tuple[list[dict], dict[str, dict]]:
    if path.stat().st_size > 100_000:
        raise ValidationError("Fixture exceeds validation size limit")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"articles"}:
        raise ValidationError("Invalid fixture schema")
    rows = data["articles"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 10:
        raise ValidationError("Fixture requires 1..10 articles")
    allowed = {
        "id",
        "url",
        "title",
        "summary",
        "source",
        "published_date",
        "category",
        "protected_terms",
        "translation",
    }
    sources, translations = [], {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != allowed:
            raise ValidationError("Invalid fixture article schema")
        translation = row["translation"]
        if not isinstance(translation, dict) or set(translation) != {
            "korean_title",
            "korean_summary",
            "editorial_note",
        }:
            raise ValidationError("Invalid fixture translation schema")
        if row["category"] not in {"ai", "cloud", "devops", "tech"}:
            raise ValidationError("Validation requires tech-blog categories")
        if not isinstance(row["url"], str) or row["url"] in translations:
            raise ValidationError("Fixture URLs must be unique")
        sources.append({k: v for k, v in row.items() if k != "translation"})
        translations[row["url"]] = translation
    return sources, translations


def validate_fixture(
    fixture: Path,
    output: Path,
    ledger_path: Path,
    run_id: str,
    *,
    daily_limit_microusd: int = 1_000_000,
    batch_limit_microusd: int = 250_000,
    require_existing_ledger: bool = False,
) -> dict[str, Any]:
    """Exercise T2/T4/T5 and budget accounting with synthetic fixture charges.

    Outputs are private, isolated validation artifacts; never a publish manifest,
    published-URL tracker, commit, image generation, or production deployment.
    """
    if not isinstance(require_existing_ledger, bool):
        raise ValidationError("Existing-ledger policy must be boolean")
    output, ledger_path = output.resolve(), ledger_path.resolve()
    for target in (output, ledger_path):
        if target == ROOT or ROOT in target.parents:
            raise ValidationError("Validation state must be outside the checkout")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", run_id):
        raise ValidationError("Explicit safe run ID required")
    if output.exists():
        raise ValidationError("Validation output must not exist")
    output.mkdir(parents=True, mode=0o700)
    report: dict[str, Any] = {
        "mode": "offline_fixture",
        "ledger_policy": "existing_only"
        if require_existing_ledger
        else "fixture_bootstrap",
        "status": "failed",
        "live_calls": 0,
        "fixture_requests": 0,
        "rendered_articles": 0,
    }
    prior_mode = config._AI_MODE
    candidate = output / "candidate.md"
    try:
        rows, translations = _load_fixture(fixture)
        categorized: dict[str, list[dict]] = {}
        for row in rows:
            categorized.setdefault(row["category"], []).append(row)
        ledger_type = (
            ProductionBudgetLedger if require_existing_ledger else BudgetLedger
        )
        ledger = ledger_type(
            ledger_path,
            daily_limit_microusd=daily_limit_microusd,
            batch_limit_microusd=batch_limit_microusd,
        )
        # Never pass environment credentials to the provider. A new local cache
        # and this fixed transport are the only execution path in this command.
        with ledger.batch(run_id) as batch:

            def fixture_transport(request: ProviderRequest) -> ProviderResponse:
                index = report["fixture_requests"]
                reservation = batch.reserve(
                    f"fixture-{index}", 1_000, at=datetime.now(timezone.utc)
                )
                report["fixture_requests"] += 1
                messages = request.body["messages"]
                source = json.loads(messages[-1]["content"])["source_data"]  # type: ignore[index]
                payload = {
                    "article_id": source["article_id"],
                    "canonical_url": source["canonical_url"],
                    **translations[source["canonical_url"]],
                }
                # These are synthetic test amounts, not a model price estimate.
                batch.settle(reservation, actual_microusd=500)
                return ProviderResponse(
                    200,
                    json.dumps(
                        {
                            "choices": [
                                {
                                    "finish_reason": "stop",
                                    "message": {"content": json.dumps(payload)},
                                }
                            ]
                        }
                    ),
                )

            cache = TranslationCache(ttl_seconds=60)

            def executor(article):
                import random
                import time

                return execute_translation(
                    article,
                    provider="openai",
                    model="offline-fixture",
                    credentials={"OPENAI_API_KEY": "offline-fixture-only"},
                    rules_version="t6-offline-v1",
                    transport=fixture_transport,
                    cache=cache,
                    policy=ExecutionPolicy(max_attempts=1),
                    clock=time.monotonic,
                    sleeper=time.sleep,
                    jitter=random.random,
                )

            boundary = PublicationTranslation(
                executor=executor, max_articles=10, rejection_dir=output / "rejected"
            )
            config._AI_MODE = "none"
            prepared = boundary.prepare(categorized, legacy_ai_disabled=True)
            selected = [item for items in prepared.values() for item in items]
            content = generate_tech_blog_content(
                selected,
                prepared,
                datetime(2026, 11, 8, 9, tzinfo=timezone.utc),
                "Offline_Validation",
            )
            if validate_stats_consistency(content):
                raise ValidationError("Fixture statistics gate failed")
            rendered = boundary.rendered_items(content, prepared)
            _private_write(candidate, content)
            score = _run_post_quality_gate(candidate, target=80)
            if score is None or score < 80:
                raise ValidationError("Fixture quality gate failed")
            # Offline fixtures are already reviewed. Any repair needs review;
            # URL-only checks cannot prove translated facts stayed unchanged.
            if candidate.read_text() != content:
                raise ValidationError("Fixture quality repair requires review")
            # Re-check source identity after the existing quality self-heal.
            boundary.rendered_items(candidate.read_text(), prepared)
            if validate_stats_consistency(candidate.read_text()):
                raise ValidationError("Fixture post-quality statistics failed")
            report.update(
                status="validated", rendered_articles=len(rendered), quality_score=score
            )
    except Exception:
        candidate.unlink(missing_ok=True)
        _private_write(output / "report.json", json.dumps(report, indent=2))
        raise ValidationError(
            "Offline fixture validation failed; inspect safe report"
        ) from None
    finally:
        config._AI_MODE = prior_mode
    _private_write(output / "report.json", json.dumps(report, indent=2))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--require-existing-ledger",
        action="store_true",
        help="Use production admission against an existing fixture DB and lock; never bootstrap",
    )
    args = parser.parse_args(argv)
    try:
        report = validate_fixture(
            args.fixture,
            args.output,
            args.ledger,
            args.run_id,
            require_existing_ledger=args.require_existing_ledger,
        )
    except (ValidationError, OSError):
        print(
            "Offline validation failed; no production files or live calls.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
