"""Tests for the L20 spec-slug case-sensitive consistency gate."""
from __future__ import annotations

from pathlib import Path

from scripts import check_l20_spec_slug_consistency as gate


def _post(posts: Path, name: str, slug: str) -> None:
    (posts / f"{name}.md").write_text(
        f'---\nimage: /assets/images/{slug}.svg\n---\nbody\n', encoding="utf-8"
    )


def _spec(specs: Path, fname: str, date: str, slug: str) -> None:
    (specs / f"{fname}.yml").write_text(f"date: '{date}'\nslug: {slug}\n", encoding="utf-8")


def test_exact_match_passes(tmp_path, monkeypatch):
    posts = tmp_path / "_posts"; specs = tmp_path / "_data/l20_covers"
    posts.mkdir(parents=True); specs.mkdir(parents=True)
    _post(posts, "2026-01-08-Foo_and_Bar", "2026-01-08-Foo_and_Bar")
    _spec(specs, "2026-01-08-Foo_and_Bar", "2026-01-08", "Foo_and_Bar")
    monkeypatch.setattr(gate, "POSTS", posts)
    monkeypatch.setattr(gate, "SPECS_DIR", specs)
    assert gate.main() == 0


def test_case_only_mismatch_fails(tmp_path, monkeypatch):
    posts = tmp_path / "_posts"; specs = tmp_path / "_data/l20_covers"
    posts.mkdir(parents=True); specs.mkdir(parents=True)
    # post uses lowercase 'and', spec uses 'And' -> Linux 404 risk
    _post(posts, "2026-01-08-Foo_and_Bar", "2026-01-08-Foo_and_Bar")
    _spec(specs, "2026-01-08-Foo_And_Bar", "2026-01-08", "Foo_And_Bar")
    monkeypatch.setattr(gate, "POSTS", posts)
    monkeypatch.setattr(gate, "SPECS_DIR", specs)
    assert gate.main() == 1


def test_orphan_spec_warns_not_fails(tmp_path, monkeypatch):
    posts = tmp_path / "_posts"; specs = tmp_path / "_data/l20_covers"
    posts.mkdir(parents=True); specs.mkdir(parents=True)
    _spec(specs, "2026-01-08-No_Post", "2026-01-08", "No_Post")  # no matching post
    monkeypatch.setattr(gate, "POSTS", posts)
    monkeypatch.setattr(gate, "SPECS_DIR", specs)
    assert gate.main() == 0  # orphan is a WARN, not a hard fail


def test_live_corpus_passes():
    """Backstop: the live l20_covers specs case-match their posts (2 fixed 2026-06-22)."""
    assert gate.main() == 0
