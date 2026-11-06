"""T5 preflight and real publisher generation stay offline and fail closed."""

import copy
import json
import socket
import sys
from dataclasses import replace
from datetime import datetime, timezone

import auto_publish_news as publisher
import pytest
import requests

from scripts.news.translation_contract import (
    TranslationContractError,
    TranslationResult,
)
from scripts.news.translation_execution import (
    ExecutionPolicy,
    TranslationCache,
    execute_translation,
)
from scripts.news.translation_provider import ProviderError, ProviderResponse
from scripts.news.translation_publication import (
    PublicationTranslation,
    TranslationPublicationError,
)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("No live network in publication tests")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


@pytest.fixture
def items():
    return [
        {
            "id": f"source-{i}",
            "url": f"https://vendor.test/advisory-{i}",
            "title": "Acme fixes a security flaw",
            "summary": "Acme releases a patch.",
            "source": "Vendor",
            "published_date": "2026-11-06T00:00:00+00:00",
            "category": "security",
            "protected_terms": ["Acme"],
            "score": 100 - i,
        }
        for i in range(3)
    ]


def translated(request):
    return TranslationResult(
        request.article_id,
        request.canonical_url,
        "Acme 취약점 패치 공개",
        "Acme 보안 패치를 공개했다. 적용 전 영향 범위를 검토해야 한다.",
        "",
    )


def test_all_candidates_translated_once_and_source_preserved(items, tmp_path):
    original = copy.deepcopy(items)
    calls = []

    def service(request):
        calls.append(request)
        return translated(request)

    boundary = PublicationTranslation(
        executor=service, max_articles=3, rejection_dir=tmp_path / "rejected"
    )
    out = boundary.prepare({"security": items, "cloud": [copy.deepcopy(items[0])]})
    assert len(calls) == 3
    assert len(out["security"]) == 3 and out["cloud"] == []
    assert items == original
    assert out["security"][0]["published_date"] == items[0]["published_date"]
    assert out["security"][0]["url"] == items[0]["url"]
    assert out["security"][0]["translation_source"]["source_title"] == items[0]["title"]
    assert "취약점" in out["security"][0]["title"]


def test_cap_checked_before_any_translation(items, tmp_path):
    boundary = PublicationTranslation(
        executor=lambda _: pytest.fail("charged beyond cap"),
        max_articles=2,
        rejection_dir=tmp_path,
    )
    with pytest.raises(TranslationPublicationError):
        boundary.prepare({"security": items})
    assert list(tmp_path.glob("*.json"))


def test_conflicting_identity_fails_before_calls(items, tmp_path):
    items[1]["id"] = items[0]["id"]
    boundary = PublicationTranslation(
        executor=lambda _: pytest.fail("ambiguous source"),
        max_articles=3,
        rejection_dir=tmp_path,
    )
    with pytest.raises(TranslationPublicationError):
        boundary.prepare({"security": items})


@pytest.mark.parametrize("failure", ["missing-key", "provider", "id", "url", "facts"])
def test_failures_preserve_safe_rejection_not_partial_results(items, tmp_path, failure):
    def service(request):
        if failure == "missing-key":
            raise TranslationContractError("secret-token do not log")
        if failure == "provider":
            raise ProviderError("authentication")
        result = translated(request)
        if failure == "id":
            return replace(result, article_id="wrong")
        if failure == "url":
            return replace(result, canonical_url="https://wrong.test/")
        return replace(result, korean_summary="추가 피해는 999건이다.")

    boundary = PublicationTranslation(
        executor=service, max_articles=3, rejection_dir=tmp_path / "reject"
    )
    with pytest.raises(TranslationPublicationError) as caught:
        boundary.prepare({"security": items})
    assert "secret-token" not in str(caught.value)
    artifact = list((tmp_path / "reject").glob("*.json"))
    assert len(artifact) == 1
    data = json.loads(artifact[0].read_text())
    assert data["status"] == "failed" and data["inputs"]
    assert not (tmp_path / "_posts").exists()


def setup_main(monkeypatch, tmp_path, items, *, dry_run=False):
    posts, images = tmp_path / "_posts", tmp_path / "images"
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(publisher, "POSTS_DIR", posts)
    monkeypatch.setattr(publisher, "IMAGES_DIR", images)
    monkeypatch.setattr(publisher, "MIN_NEWS_COUNT", 1)
    monkeypatch.setattr(
        publisher,
        "load_collected_news",
        lambda: {"total_items": len(items), "items": items},
    )
    monkeypatch.setattr(publisher, "filter_and_prioritize_news", lambda *a, **k: items)
    monkeypatch.setattr(publisher, "load_published_urls", lambda: {})
    monkeypatch.setattr(publisher, "filter_published_urls", lambda rows, _: rows)
    monkeypatch.setattr(publisher, "categorize_news", lambda rows: {"security": rows})
    monkeypatch.setattr(publisher, "_convert_svg_to_og_png", lambda *_: None)
    monkeypatch.setattr(
        publisher, "_generate_and_commit_raster_variants", lambda **_: None
    )
    tracker = []
    monkeypatch.setattr(
        publisher, "save_published_urls", lambda rows, date: tracker.extend(rows)
    )
    argv = [
        "publisher",
        "--use-ai",
        "none",
        "--no-commit",
        "--date",
        "2026-11-06",
        "--publish-manifest",
        str(manifest),
    ]
    if dry_run:
        argv.append("--dry-run")
    monkeypatch.setattr(sys, "argv", argv)
    return posts, images, manifest, tracker


def test_actual_publisher_generates_korean_post_through_t4_fake_transport(
    items, tmp_path, monkeypatch
):
    for i in (3, 4):
        extra = copy.deepcopy(items[0])
        extra.update(id=f"source-{i}", url=f"https://vendor.test/advisory-{i}")
        items.append(extra)
    posts, images, manifest, tracker = setup_main(monkeypatch, tmp_path, items)
    original = copy.deepcopy(items)
    monkeypatch.setattr(sys, "argv", sys.argv + ["--max-news", "1"])
    extract_topics = publisher._extract_key_topics

    def original_source_topics(rows):
        assert all("fixes" in row["title"] for row in rows)
        return extract_topics(rows)

    monkeypatch.setattr(publisher, "_extract_key_topics", original_source_topics)
    calls = []

    def transport(request):
        calls.append(request)
        source = json.loads(request.body["messages"][-1]["content"])["source_data"]
        result = translated(type("Article", (), source)())
        output = {
            key: getattr(result, key)
            for key in (
                "article_id",
                "canonical_url",
                "korean_title",
                "korean_summary",
                "editorial_note",
            )
        }
        return ProviderResponse(
            200,
            json.dumps(
                {
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {"content": json.dumps(output)},
                        }
                    ]
                }
            ),
        )

    cache = TranslationCache(ttl_seconds=10)

    def service(request):
        return execute_translation(
            request,
            provider="openai",
            model="test-model",
            credentials={"OPENAI_API_KEY": "fake-key"},
            rules_version="t5",
            transport=transport,
            cache=cache,
            policy=ExecutionPolicy(),
            clock=lambda: 0.0,
            sleeper=lambda _: pytest.fail("sleep"),
            jitter=lambda: 1.0,
        )

    boundary = PublicationTranslation(
        executor=service, max_articles=5, rejection_dir=tmp_path / "rejected"
    )
    publisher.main(translation=boundary)
    generated = list(posts.glob("*.md"))
    assert len(generated) == 1
    content = generated[0].read_text()
    assert "Acme 취약점 패치 공개" in content
    assert all(item["url"] in content for item in items[:3])
    assert all(item["url"] not in content for item in items[3:])
    from scripts.news.qa_gate import validate_stats_consistency

    assert validate_stats_consistency(content) == []
    assert json.loads(manifest.read_text())["status"] == "created"
    assert len(tracker) == 3 and len(calls) == 5
    assert {item["url"] for item in tracker} == {item["url"] for item in items[:3]}
    assert items == original


def test_main_translation_failure_writes_failed_manifest_without_post_or_tracker(
    items, tmp_path, monkeypatch
):
    posts, images, manifest, tracker = setup_main(monkeypatch, tmp_path, items)

    def fail(_):
        raise TranslationContractError("secret-token")

    boundary = PublicationTranslation(
        executor=fail, max_articles=3, rejection_dir=tmp_path / "rejected"
    )
    with pytest.raises(SystemExit) as caught:
        publisher.main(translation=boundary)
    assert caught.value.code == 1
    assert not posts.exists() and not images.exists() and not tracker
    assert json.loads(manifest.read_text())["status"] == "failed"
    assert list((tmp_path / "rejected").glob("*.json"))


def test_dry_run_has_no_post_or_tracker_write(items, tmp_path, monkeypatch):
    posts, images, manifest, tracker = setup_main(
        monkeypatch, tmp_path, items, dry_run=True
    )
    boundary = PublicationTranslation(
        executor=translated, max_articles=3, rejection_dir=tmp_path / "rejected"
    )
    publisher.main(translation=boundary)
    assert not posts.exists() and not images.exists() and not tracker
    assert json.loads(manifest.read_text())["status"] == "dry_run"


def test_legacy_main_without_dependency_still_dry_runs(items, tmp_path, monkeypatch):
    for item in items:
        item["title"] = "Acme 보안 패치 공개"
        item["summary"] = "Acme 보안 업데이트를 공개했다. 영향 범위를 확인해야 한다."
    posts, images, manifest, tracker = setup_main(
        monkeypatch, tmp_path, items, dry_run=True
    )
    publisher.main()
    assert json.loads(manifest.read_text())["status"] == "dry_run"
    assert not posts.exists() and not tracker


def test_duplicate_url_with_changed_facts_is_rejected_before_executor(items, tmp_path):
    changed = copy.deepcopy(items[0])
    changed["summary"] = "Changed source facts."
    boundary = PublicationTranslation(
        executor=lambda _: pytest.fail("conflicting batch called executor"),
        max_articles=3,
        rejection_dir=tmp_path,
    )
    with pytest.raises(TranslationPublicationError):
        boundary.prepare({"security": [items[0], changed]})


def test_diagnostic_artifact_redacts_input_secrets_and_is_private(items, tmp_path):
    secret = "sk-" + "a" * 48
    items[0]["url"] = "https://user:short-secret@vendor.test/news?token=short-secret"
    items[0]["summary"] = "Original source contains " + secret
    boundary = PublicationTranslation(
        executor=lambda _: pytest.fail("invalid input called executor"),
        max_articles=3,
        rejection_dir=tmp_path / "private",
    )
    with pytest.raises(TranslationPublicationError):
        boundary.prepare({"security": items})
    artifact = next((tmp_path / "private").glob("*.json"))
    raw = artifact.read_text()
    assert "short-secret" not in raw and secret not in raw
    assert json.loads(raw)["inputs"]
    assert artifact.stat().st_mode & 0o777 == 0o600


def test_main_failure_keeps_existing_post_untouched(items, tmp_path, monkeypatch):
    posts, _, manifest, tracker = setup_main(monkeypatch, tmp_path, items)
    posts.mkdir()
    existing = posts / "existing.md"
    existing.write_text("Existing manual content")

    def failure(_):
        raise ProviderError("authentication")

    boundary = PublicationTranslation(
        executor=failure, max_articles=3, rejection_dir=tmp_path / "rejected"
    )
    with pytest.raises(SystemExit):
        publisher.main(translation=boundary)
    assert existing.read_text() == "Existing manual content"
    assert list(posts.iterdir()) == [existing] and not tracker
    assert json.loads(manifest.read_text())["status"] == "failed"


def test_opt_in_rejects_legacy_ai_activation_before_executor(
    items, tmp_path, monkeypatch
):
    posts, _, manifest, tracker = setup_main(monkeypatch, tmp_path, items)
    argv = list(sys.argv)
    argv[argv.index("none")] = "auto"
    monkeypatch.setattr(sys, "argv", argv)
    boundary = PublicationTranslation(
        executor=lambda _: pytest.fail("legacy mode called executor"),
        max_articles=3,
        rejection_dir=tmp_path / "rejected",
    )
    with pytest.raises(SystemExit):
        publisher.main(translation=boundary)
    assert not posts.exists() and not tracker
    assert json.loads(manifest.read_text())["status"] == "failed"


def test_validated_item_bypasses_stale_summary_cache_but_raw_json_cannot(
    items, tmp_path, monkeypatch
):
    from scripts.news.content_generator import (
        KOREAN_SUMMARY_CACHE,
        _korean_brief_summary,
    )

    boundary = PublicationTranslation(
        executor=translated, max_articles=3, rejection_dir=tmp_path
    )
    wrapped = boundary.prepare({"security": items})["security"][0]
    monkeypatch.setitem(KOREAN_SUMMARY_CACHE, items[0]["id"], "Stale English summary")
    assert _korean_brief_summary(wrapped) == wrapped.translation.korean_summary
    plain = json.loads(json.dumps(wrapped))
    plain["translation_validated"] = True
    plain["translation"] = {"korean_summary": "위조된 검증 값"}
    assert _korean_brief_summary(plain) == "Stale English summary"


@pytest.mark.parametrize(
    "content",
    [
        "No cards",
        '{% include news-card.html url="https://unknown.test/" %}',
        '{% include news-card.html title="No URL" %}',
    ],
)
def test_rendered_source_boundary_rejects_empty_unknown_or_malformed_cards(
    items, tmp_path, content
):
    boundary = PublicationTranslation(
        executor=translated, max_articles=3, rejection_dir=tmp_path / "rejected"
    )
    prepared = boundary.prepare({"security": items})
    with pytest.raises(TranslationPublicationError):
        boundary.rendered_items(content, prepared)
    assert list((tmp_path / "rejected").glob("*.json"))


def test_rendered_source_matching_unescapes_url_and_deduplicates(items, tmp_path):
    items[0]["url"] += "?view=full&format=html"
    boundary = PublicationTranslation(
        executor=translated, max_articles=3, rejection_dir=tmp_path
    )
    prepared = boundary.prepare({"security": items})
    card = '{% include news-card.html url="https://vendor.test/advisory-0?view=full&amp;format=html" %}'
    tracked = boundary.rendered_items(card + card, prepared)
    assert len(tracked) == 1
    assert tracked[0]["url"] == items[0]["url"]


def test_long_summary_is_rejected_before_renderer_can_drop_protected_facts(
    items, tmp_path
):
    def long_summary(request):
        return replace(translated(request), korean_summary="한" * 201)

    boundary = PublicationTranslation(
        executor=long_summary, max_articles=3, rejection_dir=tmp_path
    )
    with pytest.raises(TranslationPublicationError):
        boundary.prepare({"security": items})


def test_tech_mode_missing_source_cards_fails_closed(items, tmp_path, monkeypatch):
    posts, _, manifest, tracker = setup_main(monkeypatch, tmp_path, items)
    monkeypatch.setattr(sys, "argv", sys.argv + ["--mode", "tech-blog"])
    monkeypatch.setattr(publisher, "categorize_news", lambda rows: {"cloud": rows})
    boundary = PublicationTranslation(
        executor=translated, max_articles=3, rejection_dir=tmp_path / "rejected"
    )
    with pytest.raises(SystemExit):
        publisher.main(translation=boundary)
    assert not posts.exists() and not tracker
    assert json.loads(manifest.read_text())["reason"] == "translation_source_rendering"
