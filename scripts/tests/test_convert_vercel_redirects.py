"""Tests for ``scripts/convert_vercel_redirects_to_jekyll.py``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from convert_vercel_redirects_to_jekyll import (  # noqa: E402
    collect_redirects_by_post,
    destination_to_post_path,
    insert_redirect_from_block,
    main,
    merge_redirects,
    parse_existing_redirect_from,
    remove_redirect_from_block,
    split_front_matter,
)


# ---------------------------------------------------------------------------
# destination_to_post_path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "destination,expected_filename",
    [
        ("/posts/2025/04/29/SKT_Security/", "2025-04-29-SKT_Security.md"),
        ("/posts/2026/05/01/Foo_Bar_Baz/", "2026-05-01-Foo_Bar_Baz.md"),
        # No trailing slash
        ("/posts/2024/12/31/Year_End", "2024-12-31-Year_End.md"),
    ],
)
def test_destination_maps_to_post_file(tmp_path, destination, expected_filename):
    posts_dir = tmp_path / "_posts"
    result = destination_to_post_path(destination, posts_dir)
    assert result == posts_dir / expected_filename


@pytest.mark.parametrize(
    "destination",
    [
        "",
        "/about/",
        "/posts/2025/04/no_day/",
        "/posts/2025/04//empty_slug/",
        "/category/security/",
    ],
)
def test_destination_rejects_invalid(tmp_path, destination):
    assert destination_to_post_path(destination, tmp_path / "_posts") is None


# ---------------------------------------------------------------------------
# split_front_matter
# ---------------------------------------------------------------------------


def test_split_front_matter_happy_path():
    text = "---\ntitle: Foo\ntags: [a, b]\n---\nBody here\n"
    fm, body = split_front_matter(text)
    assert "title: Foo" in fm
    assert body.startswith("Body here")


def test_split_front_matter_missing_returns_none():
    assert split_front_matter("no front matter\n") is None
    assert split_front_matter("---\nunterminated\n") is None


# ---------------------------------------------------------------------------
# parse / remove / insert
# ---------------------------------------------------------------------------


def test_parse_existing_block_list():
    fm = "title: Foo\nredirect_from:\n  - /a/\n  - /b/\n"
    assert parse_existing_redirect_from(fm) == ["/a/", "/b/"]


def test_parse_existing_inline_scalar():
    fm = "redirect_from: /old/path/\n"
    assert parse_existing_redirect_from(fm) == ["/old/path/"]


def test_parse_existing_none():
    fm = "title: Foo\ndate: 2025-01-01\n"
    assert parse_existing_redirect_from(fm) == []


def test_merge_redirects_dedup_and_sort():
    assert merge_redirects(["/b/", "/a/"], ["/b/", "/c/"]) == ["/a/", "/b/", "/c/"]


def test_remove_redirect_from_block_strips_block_list():
    fm = "title: Foo\nredirect_from:\n  - /a/\n  - /b/\ntags: [x]\n"
    cleaned = remove_redirect_from_block(fm)
    assert "redirect_from" not in cleaned
    assert "title: Foo" in cleaned
    assert "tags: [x]" in cleaned


def test_remove_redirect_from_inline_scalar():
    fm = "title: Foo\nredirect_from: /old/\ntags: [x]\n"
    cleaned = remove_redirect_from_block(fm)
    assert "redirect_from" not in cleaned
    assert "title: Foo" in cleaned
    assert "tags: [x]" in cleaned


def test_insert_redirect_from_block_appends_in_block_form():
    fm = "title: Foo\ndate: 2025-01-01"
    out = insert_redirect_from_block(fm, ["/a/", "/b/"])
    assert "redirect_from:\n  - /a/\n  - /b/" in out
    assert "title: Foo" in out


def test_insert_redirect_from_block_replaces_existing():
    fm = "title: Foo\nredirect_from:\n  - /old/\n"
    out = insert_redirect_from_block(fm, ["/a/", "/old/"])
    # Old key removed, new key added with merged set
    assert out.count("redirect_from:") == 1
    assert "  - /a/" in out
    assert "  - /old/" in out


# ---------------------------------------------------------------------------
# collect_redirects_by_post
# ---------------------------------------------------------------------------


def _make_post(posts_dir: Path, name: str) -> Path:
    posts_dir.mkdir(parents=True, exist_ok=True)
    p = posts_dir / name
    p.write_text("---\ntitle: T\n---\nBody\n", encoding="utf-8")
    return p


def test_collect_groups_multiple_sources_by_destination(tmp_path):
    posts_dir = tmp_path / "_posts"
    _make_post(posts_dir, "2025-04-29-Foo.md")
    redirects = [
        {"source": "/posts/2025/04/Foo/", "destination": "/posts/2025/04/29/Foo/", "statusCode": 301},
        {"source": "/posts/2025/04/Foo_legacy/", "destination": "/posts/2025/04/29/Foo/", "statusCode": 301},
    ]
    grouped, skipped = collect_redirects_by_post(redirects, posts_dir)
    assert len(grouped) == 1
    assert skipped == []
    [(post, srcs)] = grouped.items()
    assert post.name == "2025-04-29-Foo.md"
    assert sorted(srcs) == ["/posts/2025/04/Foo/", "/posts/2025/04/Foo_legacy/"]


def test_collect_skips_missing_post(tmp_path):
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    redirects = [
        {"source": "/posts/2099/01/Phantom/", "destination": "/posts/2099/01/01/Phantom/"},
    ]
    grouped, skipped = collect_redirects_by_post(redirects, posts_dir)
    assert grouped == {}
    assert len(skipped) == 1
    assert skipped[0]["reason"] == "post-not-found"


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


def test_main_dry_run_does_not_modify(tmp_path, capsys):
    posts_dir = tmp_path / "_posts"
    p = _make_post(posts_dir, "2025-04-29-Foo.md")
    before = p.read_text(encoding="utf-8")
    vercel = tmp_path / "vercel.json"
    vercel.write_text(json.dumps({
        "redirects": [
            {"source": "/posts/2025/04/Foo/",
             "destination": "/posts/2025/04/29/Foo/",
             "statusCode": 301}
        ],
    }), encoding="utf-8")
    rc = main([
        "--vercel-json", str(vercel),
        "--posts-dir", str(posts_dir),
        "--dry-run",
    ])
    assert rc == 0
    assert p.read_text(encoding="utf-8") == before
    captured = capsys.readouterr()
    assert "posts_modified" in captured.out


def test_main_apply_writes_redirect_from(tmp_path):
    posts_dir = tmp_path / "_posts"
    p = _make_post(posts_dir, "2025-04-29-Foo.md")
    vercel = tmp_path / "vercel.json"
    vercel.write_text(json.dumps({
        "redirects": [
            {"source": "/posts/2025/04/Foo/",
             "destination": "/posts/2025/04/29/Foo/",
             "statusCode": 301},
            {"source": "/posts/2025/04/Foo_alt/",
             "destination": "/posts/2025/04/29/Foo/",
             "statusCode": 301},
        ],
    }), encoding="utf-8")
    rc = main([
        "--vercel-json", str(vercel),
        "--posts-dir", str(posts_dir),
    ])
    assert rc == 0
    text = p.read_text(encoding="utf-8")
    assert "redirect_from:" in text
    assert "  - /posts/2025/04/Foo/" in text
    assert "  - /posts/2025/04/Foo_alt/" in text


def test_main_strict_returns_one_on_missing_post(tmp_path):
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    vercel = tmp_path / "vercel.json"
    vercel.write_text(json.dumps({
        "redirects": [
            {"source": "/posts/2099/01/Phantom/",
             "destination": "/posts/2099/01/01/Phantom/",
             "statusCode": 301}
        ],
    }), encoding="utf-8")
    rc = main([
        "--vercel-json", str(vercel),
        "--posts-dir", str(posts_dir),
        "--strict",
    ])
    assert rc == 1
