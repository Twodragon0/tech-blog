"""Manifest handoff: detect the generated digest, and fail when it cannot."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.blogwatcher_manifest import (
    kst_publish_date,
    main,
    resolve_manifest,
    write_manifest,
)
from scripts.check_kst_midnight import check_file

POST = "_posts/2026-11-05-Tech_Security_Weekly_Digest_Patch_AWS_Data_AI.md"
COVER = "assets/images/2026-11-05-Tech_Security_Weekly_Digest_Patch_AWS_Data_AI.svg"
KST = timezone(timedelta(hours=9))


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "manifest-test@example.com")
    _git(tmp_path, "config", "user.name", "manifest-test")
    _git(tmp_path, "config", "commit.gpgsign", "false")
    (tmp_path / "_posts").mkdir()
    (tmp_path / "assets" / "images").mkdir(parents=True)
    (tmp_path / "_data").mkdir()
    return tmp_path


def _write_pair(repo: Path) -> None:
    (repo / POST).write_text("---\ntitle: t\n---\n", encoding="utf-8")
    (repo / COVER).write_text("<svg></svg>\n", encoding="utf-8")


def test_created_manifest_returns_the_kst_path_without_reading_the_clock(tmp_path):
    repo = _repo(tmp_path)
    _write_pair(repo)
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(
        manifest,
        status="created",
        reason="created",
        date="2026-11-05",
        post_file=POST,
        image_file=COVER,
    )
    result = resolve_manifest(manifest)
    assert result.ok
    assert result.post_created
    assert result.post_file == POST
    assert result.image_file == COVER
    assert result.publish_date == "2026-11-05"


def test_missing_manifest_fails_closed(tmp_path):
    repo = _repo(tmp_path)
    result = resolve_manifest(repo / ".blogwatcher-publish.json")
    assert not result.ok
    assert "no publish manifest" in result.message


def test_created_record_without_the_file_is_generated_but_not_detected(tmp_path):
    repo = _repo(tmp_path)
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(
        manifest,
        status="created",
        reason="created",
        date="2026-11-05",
        post_file=POST,
        image_file=COVER,
    )
    result = resolve_manifest(manifest)
    assert not result.ok
    assert "generated but not detected" in result.message


def test_skip_with_an_untracked_digest_does_not_report_success(tmp_path):
    repo = _repo(tmp_path)
    _write_pair(repo)
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(manifest, status="skipped", reason="not_enough_news")
    result = resolve_manifest(manifest)
    assert not result.ok
    assert "refusing to report success" in result.message


def test_legitimate_skip_stays_green(tmp_path):
    repo = _repo(tmp_path)
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(manifest, status="skipped", reason="not_enough_news")
    result = resolve_manifest(manifest)
    assert result.ok
    assert not result.post_created
    assert result.skip_reason == "not_enough_news"


def test_committed_same_day_post_is_not_a_new_digest(tmp_path):
    repo = _repo(tmp_path)
    _write_pair(repo)
    _git(repo, "add", "--", POST)
    _git(repo, "commit", "-m", "existing digest")
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(
        manifest, status="skipped", reason="same_day_exists", date="2026-11-05"
    )
    result = resolve_manifest(manifest)
    assert result.ok
    assert not result.post_created
    assert result.skip_reason == "same_day_exists"


def test_unexpected_path_is_rejected(tmp_path):
    repo = _repo(tmp_path)
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(
        manifest,
        status="created",
        reason="created",
        date="2026-11-05",
        post_file="_posts/$(id).md",
        image_file=COVER,
    )
    result = resolve_manifest(manifest)
    assert not result.ok
    assert "refusing unexpected publish path" in result.message


def test_hyphenated_topic_slug_is_accepted(tmp_path):
    repo = _repo(tmp_path)
    post = "_posts/2026-11-05-Tech_Security_Weekly_Digest_Zero-Day_Patch.md"
    cover = "assets/images/2026-11-05-Tech_Security_Weekly_Digest_Zero-Day_Patch.svg"
    (repo / post).write_text("---\n---\n", encoding="utf-8")
    (repo / cover).write_text("<svg></svg>\n", encoding="utf-8")
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(
        manifest,
        status="created",
        reason="created",
        date="2026-11-05",
        post_file=post,
        image_file=cover,
    )
    result = resolve_manifest(manifest)
    assert result.ok
    assert result.post_file == post


def test_resolve_cli_writes_github_output(tmp_path):
    repo = _repo(tmp_path)
    _write_pair(repo)
    manifest = repo / ".blogwatcher-publish.json"
    output = repo / "github-output.txt"
    write_manifest(
        manifest,
        status="created",
        reason="created",
        date="2026-11-05",
        post_file=POST,
        image_file=COVER,
    )
    code = main(
        ["resolve", "--manifest", str(manifest), "--github-output", str(output)]
    )
    assert code == 0
    text = output.read_text(encoding="utf-8")
    assert f"post_created=true\npost_file={POST}\n" in text
    assert "publish_date=2026-11-05\n" in text


def test_resolve_cli_fails_when_the_digest_is_missing(tmp_path, capsys):
    repo = _repo(tmp_path)
    manifest = repo / ".blogwatcher-publish.json"
    output = repo / "github-output.txt"
    write_manifest(
        manifest,
        status="created",
        reason="created",
        date="2026-11-05",
        post_file=POST,
        image_file=COVER,
    )
    code = main(
        ["resolve", "--manifest", str(manifest), "--github-output", str(output)]
    )
    assert code == 1
    assert not output.exists()
    assert "generated but not detected" in capsys.readouterr().err


def test_publisher_skip_writes_manifest_and_resolve_accepts_it(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    (repo / "_data" / "collected_news.json").write_text(
        json.dumps({"total_items": 0, "items": []}),
        encoding="utf-8",
    )
    manifest = repo / ".blogwatcher-publish.json"
    monkeypatch.chdir(repo)
    from scripts.news import config as news_config

    monkeypatch.setattr(news_config, "_AI_MODE", news_config._AI_MODE)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "auto_publish_news.py",
            "--use-ai",
            "none",
            "--publish-manifest",
            str(manifest),
        ],
    )
    from auto_publish_news import main as publish_main

    assert publish_main() is None
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "skipped"
    assert payload["reason"] == "not_enough_news"
    assert list(repo.glob("_posts/*.md")) == []
    result = resolve_manifest(manifest)
    assert result.ok
    assert not result.post_created


def test_publisher_same_day_dedup_does_not_claim_a_new_post(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    (repo / "_data" / "collected_news.json").write_text(
        json.dumps({"total_items": 1, "items": []}),
        encoding="utf-8",
    )
    _day = "2026-11-05"
    existing = repo / "_posts" / f"{_day}-Tech_Security_Weekly_Digest_Existing.md"
    existing.write_text("already published\n", encoding="utf-8")
    _git(repo, "add", "--", existing.relative_to(repo).as_posix())
    _git(repo, "commit", "-m", "existing")
    fixed = datetime(2026, 11, 5, 8, 11, tzinfo=KST)
    monkeypatch.chdir(repo)
    from scripts.news import config as news_config

    monkeypatch.setattr(news_config, "_AI_MODE", news_config._AI_MODE)
    monkeypatch.setattr(
        "auto_publish_news.kst_publish_date",
        lambda forced="": (fixed, _day),
    )
    monkeypatch.setattr(
        "auto_publish_news.filter_and_prioritize_news",
        lambda *_args, **_kwargs: [{}] * 5,
    )
    monkeypatch.setattr(
        "auto_publish_news.filter_published_urls",
        lambda items, _urls: items,
    )
    manifest = repo / ".blogwatcher-publish.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "auto_publish_news.py",
            "--use-ai",
            "none",
            "--publish-manifest",
            str(manifest),
        ],
    )
    from auto_publish_news import main as publish_main

    assert publish_main() is None
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "skipped"
    assert payload["reason"] == "same_day_exists"
    assert payload["date"] == _day
    result = resolve_manifest(manifest)
    assert result.ok
    assert not result.post_created


def test_pre_nine_kst_filename_still_satisfies_the_midnight_gate(tmp_path):
    instant, day = kst_publish_date(datetime(2026, 11, 4, 23, 11, tzinfo=timezone.utc))
    assert day == "2026-11-05"
    assert instant.astimezone(KST).hour < 9
    filename = f"{day}-Tech_Security_Weekly_Digest_Patch.md"
    stamp = instant.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S %z")
    content = f'---\ntitle: "t"\ndate: {stamp}\n---\nBody\n'
    from auto_publish_news import _ensure_midnight_redirect

    rewritten = _ensure_midnight_redirect(content, filename, instant.astimezone(KST))
    post = tmp_path / filename
    post.write_text(rewritten, encoding="utf-8")
    assert check_file(post) == []
    assert "/posts/2026/11/05/" in rewritten


def test_nine_kst_does_not_add_a_redirect():
    instant, _day = kst_publish_date(datetime(2026, 11, 5, 0, 0, tzinfo=timezone.utc))
    kst = instant.astimezone(KST)
    assert kst.hour == 9
    content = (
        f'---\ntitle: "t"\ndate: {kst.strftime("%Y-%m-%d %H:%M:%S %z")}\n---\nBody\n'
    )
    from auto_publish_news import _ensure_midnight_redirect

    assert _ensure_midnight_redirect(content, "2026-11-05-Slug.md", kst) == content


def test_invalid_forced_date_exits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "auto_publish_news.py",
            "--date",
            "11-05",
            "--use-ai",
            "none",
            "--publish-manifest",
            str(tmp_path / "manifest.json"),
        ],
    )
    from auto_publish_news import main as publish_main

    with pytest.raises(SystemExit) as caught:
        publish_main()
    assert caught.value.code == 1
    assert not (tmp_path / "manifest.json").exists()


def test_failed_preflight_manifest_roundtrip_cannot_announce_created_post(tmp_path):
    repo = _repo(tmp_path)
    _write_pair(repo)
    manifest = repo / ".blogwatcher-publish.json"
    write_manifest(
        manifest, status="failed", reason="translation_failed", date="2026-11-06"
    )
    assert json.loads(manifest.read_text())["status"] == "failed"
    outcome = resolve_manifest(manifest)
    assert not outcome.ok
    assert not outcome.post_created
    assert "failed preflight" in outcome.message
