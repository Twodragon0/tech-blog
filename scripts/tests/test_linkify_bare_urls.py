"""Tests for scripts/linkify_bare_urls.py.

Corpus audit 2026-08-06: 123 bare `https://…` occurrences across 19 posts render
as PLAIN TEXT, not links — verified on built output
(`_site/posts/2025/05/30/…Docker…/index.html` contains the URL with no `href`).
kramdown is configured without GFM input, so it does not auto-link bare URLs.

The fix uses the corpus' own anchor convention — `[cisa.gov/known-exploited-…]`,
`[first.org/epss]`, `[attack.mitre.org]` — i.e. host (minus `www.`) plus path,
never an invented description.

NOT in scope, and deliberately so: the 250 `[바로가기]`/`[링크]` anchors are all
inside a table's link column whose neighbouring cell already carries the title.
Rewriting them would duplicate that cell, so they are correct as they stand.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import linkify_bare_urls as lb  # noqa: E402

_FM = '---\nlayout: post\noriginal_url: https://twodragon.tistory.com/704\n---\n\n'


def t(body):
    return lb.transform(_FM + body)


# --- the fix -----------------------------------------------------------------


def test_bare_url_becomes_a_link():
    assert "[kubernetes.io/docs/tasks/debug](https://kubernetes.io/docs/tasks/debug/)" in t(
        "참고: https://kubernetes.io/docs/tasks/debug/\n"
    )


def test_www_is_dropped_from_the_label_only():
    out = t("- https://www.sans.org/white-papers/bypassing-mfa/\n")
    assert "[sans.org/white-papers/bypassing-mfa](https://www.sans.org/white-papers/bypassing-mfa/)" in out


def test_host_only_label_when_path_is_long():
    url = "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/"
    out = t(f"- {url}\n")
    assert f"[docs.aws.amazon.com]({url})" in out


def test_root_url_labels_with_the_host():
    assert "[slack.k8s.io](https://slack.k8s.io/)" in t("- **Kubernetes Slack**: https://slack.k8s.io/\n")


def test_existing_line_label_is_preserved():
    out = t("- **Kubernetes Slack**: https://slack.k8s.io/\n")
    assert "- **Kubernetes Slack**: [" in out


def test_trailing_sentence_punctuation_stays_outside_the_link():
    out = t("자세한 내용은 https://example.com/guide 를 참고하세요.\n")
    assert "[example.com/guide](https://example.com/guide)" in out
    out2 = t("참고: https://example.com/guide.\n")
    assert "[example.com/guide](https://example.com/guide)." in out2


# --- what must NOT be touched ------------------------------------------------


def test_front_matter_is_untouched():
    out = t("본문.\n")
    assert "original_url: https://twodragon.tistory.com/704" in out


def test_existing_markdown_link_is_untouched():
    src = "[FIDO](https://fidoalliance.org/) 참고.\n"
    assert t(src) == _FM + src


def test_code_fence_is_untouched():
    src = "```bash\ncurl https://example.com/api\n```\n"
    assert t(src) == _FM + src


def test_inline_code_is_untouched():
    src = "`curl https://example.com/api` 를 실행합니다.\n"
    assert t(src) == _FM + src


def test_liquid_include_url_is_untouched():
    src = '{% include news-card.html\n  url="https://example.com/a"\n%}\n'
    assert t(src) == _FM + src


def test_html_attribute_url_is_untouched():
    src = '<a href="https://example.com/a">x</a>\n'
    assert t(src) == _FM + src


def test_table_link_column_anchor_is_untouched():
    src = "| 출처 | [링크](https://example.com/a) |\n"
    assert t(src) == _FM + src


# --- safety ------------------------------------------------------------------


def test_transform_is_idempotent():
    once = t("참고: https://kubernetes.io/docs/tasks/debug/\n")
    assert lb.transform(once) == once


def test_url_text_survives_verbatim_inside_the_link_target():
    url = "https://csrc.nist.gov/publications/detail/sp/800-161/rev-1/final"
    out = t(f"- {url}\n")
    assert f"]({url})" in out


@pytest.mark.parametrize(
    "url,label",
    [
        ("https://attack.mitre.org/", "attack.mitre.org"),
        ("https://www.first.org/epss/", "first.org/epss"),
        ("http://example.com/a/b", "example.com/a/b"),
    ],
)
def test_label_matches_the_corpus_convention(url, label):
    assert lb.label_for(url) == label


def test_cli_dry_run_does_not_write(tmp_path):
    p = tmp_path / "2026-08-06-X.md"
    src = _FM + "참고: https://kubernetes.io/docs/tasks/debug/\n"
    p.write_text(src, encoding="utf-8")
    assert lb.main([str(p), "--dry-run"]) == 0
    assert p.read_text(encoding="utf-8") == src


# --- multi-line Liquid regions (the 2026-03-01 corruption) -------------------


_MULTILINE_CARD = (
    "{% include news-card.html\n"
    '  title="t"\n'
    '  url="https://example.com/a"\n'
    '  image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,w=1200/'
    'https://s3.cointelegraph.com/uploads/2026-03/x.jpg"\n'
    '  source="Cointelegraph"\n'
    "%}\n"
)


def test_multiline_liquid_include_is_untouched():
    """`{%` and the attribute lines are on DIFFERENT lines.

    A per-line `{%` guard misses the attribute lines, and the nested URL inside
    `image="…/https://s3…"` is not preceded by `="`, so it slipped past the
    lookbehind and the image URL was corrupted on 3 digests.
    """
    assert t(_MULTILINE_CARD) == _FM + _MULTILINE_CARD


def test_prose_after_a_liquid_block_is_still_linkified():
    out = t(_MULTILINE_CARD + "\n참고: https://kubernetes.io/docs/tasks/debug/\n")
    assert _MULTILINE_CARD in out
    assert "[kubernetes.io/docs/tasks/debug](https://kubernetes.io/docs/tasks/debug/)" in out


def test_nested_url_inside_a_query_string_is_not_split():
    src = "- https://r.example.com/redirect?to=https://target.example/page\n"
    out = t(src)
    assert out.count("](") == 1, out


# --- --check gate mode -------------------------------------------------------


def test_check_reports_offender_and_exits_1(tmp_path, capsys):
    url = "https://kubernetes.io/docs/tasks/debug/"
    p = tmp_path / "2026-08-06-X.md"
    p.write_text(_FM + f"참고: {url}\n", encoding="utf-8")
    assert lb.main([str(p), "--check"]) == 1
    out = capsys.readouterr().out
    # Assert the whole reported line, not a host substring: a bare
    # `"kubernetes.io" in out` reads as URL-substring validation (CodeQL
    # py/incomplete-url-substring-sanitization) and is a weaker assertion.
    assert "FAIL" in out
    assert f"  - bare URL: {url}" in out


def test_check_exits_0_when_clean(tmp_path, capsys):
    p = tmp_path / "2026-08-06-X.md"
    p.write_text(_FM + "참고: [k8s](https://kubernetes.io/docs/)\n", encoding="utf-8")
    assert lb.main([str(p), "--check"]) == 0


def test_check_does_not_write(tmp_path):
    p = tmp_path / "2026-08-06-X.md"
    src = _FM + "참고: https://kubernetes.io/docs/tasks/debug/\n"
    p.write_text(src, encoding="utf-8")
    lb.main([str(p), "--check"])
    assert p.read_text(encoding="utf-8") == src


def test_corpus_is_clean_under_the_gate():
    """Measured 2026-08-06 after PR #509: 0 bare URLs corpus-wide."""
    offenders = [
        p.name
        for p in sorted((REPO / "_posts").glob("*.md"))
        if lb.transform(p.read_text(encoding="utf-8")) != p.read_text(encoding="utf-8")
    ]
    assert offenders == [], offenders


def _noncomment(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("#"))


@pytest.mark.parametrize("rel", [".githooks/pre-commit", "scripts/install-hooks.sh"])
def test_wired_into_precommit(rel):
    import re as _re

    text = (REPO / rel).read_text(encoding="utf-8")
    assert _re.search(r'linkify_bare_urls\.py"?\s+--check', _noncomment(text)), rel


def test_wired_into_ci():
    wf = (REPO / ".github/workflows/svg-lint.yml").read_text(encoding="utf-8")
    assert "linkify_bare_urls.py --check" in _noncomment(wf)
