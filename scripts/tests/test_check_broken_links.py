"""Tests for the internal /posts/ link gate.

The interesting part is not that the corpus is clean — it is *why* the old
version said it wasn't. It reported 370 broken links, all 370 of them
``redirect_from`` YAML items in front matter, because its regex allowed a
leading whitespace and front matter was in scope. Adding an exit code without
fixing that would have produced a permanently red job.

These tests pin both halves: front matter is not scanned, and a declared
``redirect_from`` target counts as a valid destination.
"""

from __future__ import annotations

from pathlib import Path

from scripts import check_broken_links as gate

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = REPO_ROOT / "_posts"

_FM = """---
layout: post
title: "T"
redirect_from:
  - /posts/2026/01/Old_Shape/
  - /posts/2026-01-02-Filename_Shape/
---
"""


def _post(tmp_path: Path, name: str, body: str, front_matter: str = _FM) -> Path:
    p = tmp_path / name
    p.write_text(front_matter + "\n" + body, encoding="utf-8")
    return p


def test_front_matter_is_not_scanned(tmp_path):
    """The whole 370-false-positive bug in one assertion."""
    p = _post(tmp_path, "2026-01-02-Filename_Shape.md", "no links here\n")
    assert gate.broken_links(p, {"/posts/2026/01/02/Filename_Shape/"}) == []


def test_parsing_goes_through_python_frontmatter_not_a_local_splitter():
    """scripts/tests/test_lib_seam_drift_guard.py forbids hand-rolled parsers.

    Using the library also means redirect_from arrives as real YAML, so the
    block-list, inline-list and bare-string forms all work without three
    separate regexes.
    """
    src = (REPO_ROOT / "scripts" / "check_broken_links.py").read_text(encoding="utf-8")
    assert "import frontmatter" in src
    assert "split_front_matter" not in src


def test_bare_string_redirect_from_is_accepted(tmp_path):
    fm = "---\nlayout: post\nredirect_from: /posts/2026/01/Solo/\n---\n"
    p = _post(tmp_path, "2026-01-02-Solo.md", "", front_matter=fm)
    assert "/posts/2026/01/Solo/" in gate.valid_targets([p])


def test_declared_redirect_targets_are_valid_destinations(tmp_path):
    p = _post(tmp_path, "2026-01-02-Filename_Shape.md", "")
    targets = gate.valid_targets([p])
    assert "/posts/2026/01/02/Filename_Shape/" in targets  # from the filename
    assert "/posts/2026/01/Old_Shape/" in targets  # from redirect_from
    assert "/posts/2026-01-02-Filename_Shape/" in targets


def test_a_body_link_to_a_redirect_target_is_not_broken(tmp_path):
    """jekyll-redirect-from serves these, so flagging them would be wrong.

    This is the KST/UTC case from CLAUDE.md: the filename-date URL lives in
    redirect_from because the live URL can be one day earlier.
    """
    p = _post(
        tmp_path,
        "2026-01-02-Filename_Shape.md",
        "see [old](/posts/2026/01/Old_Shape/)\n",
    )
    assert gate.broken_links(p, gate.valid_targets([p])) == []


def test_a_genuinely_missing_target_is_flagged(tmp_path):
    """Proof the gate is not vacuously green."""
    p = _post(
        tmp_path,
        "2026-01-02-Filename_Shape.md",
        "see [gone](/posts/2026/01/02/No_Such_Post/)\n",
    )
    assert gate.broken_links(p, gate.valid_targets([p])) == [
        "/posts/2026/01/02/No_Such_Post/"
    ]


def test_html_href_and_bare_path_are_both_detected(tmp_path):
    body = (
        '<a href="/posts/2026/01/02/Gone_A/">a</a>\n'
        "bare /posts/2026/01/02/Gone_B/ here\n"
    )
    p = _post(tmp_path, "2026-01-02-Filename_Shape.md", body)
    found = gate.broken_links(p, gate.valid_targets([p]))
    assert "/posts/2026/01/02/Gone_A/" in found
    assert "/posts/2026/01/02/Gone_B/" in found


def test_fenced_link_is_illustrative_not_a_link(tmp_path):
    body = "```markdown\n[x](/posts/2026/01/02/Gone_In_Fence/)\n```\n"
    p = _post(tmp_path, "2026-01-02-Filename_Shape.md", body)
    assert gate.broken_links(p, gate.valid_targets([p])) == []


def test_inline_redirect_from_list_form_is_accepted(tmp_path):
    fm = "---\nlayout: post\nredirect_from: [/posts/2026/01/Inline_One/, /posts/x/]\n---\n"
    p = _post(tmp_path, "2026-01-02-Inline.md", "", front_matter=fm)
    targets = gate.valid_targets([p])
    assert "/posts/2026/01/Inline_One/" in targets
    assert "/posts/x/" in targets


def test_live_corpus_has_no_broken_body_links():
    posts = sorted(POSTS_DIR.glob("*.md"))
    targets = gate.valid_targets(posts)
    offenders = {
        p.name: links for p in posts if (links := gate.broken_links(p, targets))
    }
    assert offenders == {}, offenders


def test_the_corpus_scan_is_actually_looking_at_something():
    """Guards against the whole check silently reducing to an empty scan."""
    posts = sorted(POSTS_DIR.glob("*.md"))
    assert len(posts) > 200
    targets = gate.valid_targets(posts)
    # permalinks plus redirect_from declarations — measured 645 on 2026-08-24
    assert len(targets) > len(posts), (
        "valid targets should exceed post count because redirect_from adds more"
    )
