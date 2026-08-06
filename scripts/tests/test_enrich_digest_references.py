"""Tests for scripts/enrich_digest_references.py.

The 참고 자료 table is identical across 151 digests (CISA KEV / MITRE ATT&CK /
FIRST EPSS), carrying zero per-post context, and it has no description column
even though 4 posts already show a 3-column precedent. This transformer adds a
용도 column with canonical descriptions and appends the sources the post
ACTUALLY cited, taken from its own news cards — no LLM, no invented facts.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import enrich_digest_references as enr  # noqa: E402

_FM = '---\nlayout: post\ntitle: "x"\n---\n\n'

_TABLE_2COL = (
    "## 참고 자료\n\n"
    "| 리소스 | 링크 |\n"
    "|--------|------|\n"
    "| CISA KEV | [cisa.gov](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |\n"
    "| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |\n"
    "| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |\n"
)


def _card(source, url):
    return (
        "{% include news-card.html\n"
        '  title="t"\n'
        f'  url="{url}"\n'
        '  summary="s"\n'
        f'  source="{source}"\n'
        '  severity="High"\n'
        "%}\n\n"
    )


def _post(cards="", table=_TABLE_2COL, head="## 1. 보안\n\n### 1.1 기사\n\n"):
    return _FM + head + cards + table


# --- column upgrade ----------------------------------------------------------


def test_mapped_table_gains_the_용도_column():
    out = enr.transform(_post())
    assert "| 리소스 | 링크 | 용도 |" in out
    assert "|--------|------|------|" in out
    assert "실제 악용 확인된 취약점 목록" in out
    assert "공격 전술·기법 매핑" in out


def test_unmapped_label_keeps_the_table_two_column():
    table = _TABLE_2COL + "| Docker 3Cs Framework | [docs.docker.com](https://docs.docker.com/) |\n"
    out = enr.transform(_post(cards=_card("The Hacker News", "https://thehackernews.com/a"), table=table))
    assert "| 리소스 | 링크 | 용도 |" not in out
    # source rows are still appended, in the 2-column shape
    assert "| The Hacker News | [thehackernews.com](https://thehackernews.com) |\n" in out


# --- source rows -------------------------------------------------------------


def test_cited_sources_are_appended_with_citation_counts():
    cards = (
        _card("Google Cloud Blog", "https://cloud.google.com/blog/a")
        + _card("The Hacker News", "https://thehackernews.com/x")
        + _card("Google Cloud Blog", "https://cloud.google.com/blog/b")
    )
    out = enr.transform(_post(cards=cards))
    assert "| Google Cloud Blog | [cloud.google.com](https://cloud.google.com) | 본문 2건 인용 |" in out
    assert "| The Hacker News | [thehackernews.com](https://thehackernews.com) | 본문 1건 인용 |" in out


def test_source_order_follows_first_appearance():
    cards = _card("B Source", "https://b.example/1") + _card("A Source", "https://a.example/1")
    out = enr.transform(_post(cards=cards))
    assert out.index("| B Source |") < out.index("| A Source |")


def test_source_already_present_is_not_duplicated():
    table = _TABLE_2COL + "| The Hacker News | [thehackernews.com](https://thehackernews.com) |\n"
    out = enr.transform(_post(cards=_card("The Hacker News", "https://thehackernews.com/a"), table=table))
    # count inside the reference section only — the news card also names the source
    section = out.split("## 참고 자료")[1]
    assert section.count("The Hacker News") == 1


def test_post_without_cards_is_unchanged_except_the_column():
    out = enr.transform(_post())
    assert "본문" not in out


# --- safety ------------------------------------------------------------------


def test_transform_is_idempotent():
    once = enr.transform(_post(cards=_card("The Hacker News", "https://thehackernews.com/a")))
    assert enr.transform(once) == once


def test_only_the_reference_section_is_rewritten():
    src = _post(cards=_card("The Hacker News", "https://thehackernews.com/a"))
    out = enr.transform(src)
    assert out.split("## 참고 자료")[0] == src.split("## 참고 자료")[0]


def test_post_without_a_reference_section_is_untouched():
    src = _FM + "## 1. 보안\n\n본문.\n"
    assert enr.transform(src) == src


def test_reference_section_without_a_table_is_untouched():
    src = _FM + "## 참고 자료\n\n- [링크](https://example.com)\n"
    assert enr.transform(src) == src


def test_trailing_section_after_references_survives():
    src = _post() + "\n## 🔗 관련 포스트\n\n- 다른 글\n"
    out = enr.transform(src)
    assert out.endswith("## 🔗 관련 포스트\n\n- 다른 글\n")
    assert "| 리소스 | 링크 | 용도 |" in out


def test_non_digest_post_is_skipped_by_the_cli(tmp_path, capsys):
    p = tmp_path / "2026-08-06-Some_Guide.md"
    p.write_text(_post(), encoding="utf-8")
    assert enr.main([str(p)]) == 0
    assert p.read_text(encoding="utf-8") == _post()


def test_cli_dry_run_does_not_write(tmp_path):
    p = tmp_path / "2026-08-06-Tech_Blog_Weekly_Digest_x.md"
    src = _post(cards=_card("The Hacker News", "https://thehackernews.com/a"))
    p.write_text(src, encoding="utf-8")
    assert enr.main([str(p), "--dry-run"]) == 0
    assert p.read_text(encoding="utf-8") == src


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.microsoft.com/en-us/security/blog/x/", "https://www.microsoft.com"),
        ("https://thehackernews.com/2026/08/a.html", "https://thehackernews.com"),
        ("http://blogs.nvidia.com/blog/x", "http://blogs.nvidia.com"),
    ],
)
def test_origin_is_derived_from_the_cited_url(url, expected):
    assert enr.origin_of(url) == expected


def test_www_prefix_is_dropped_from_the_display_label_only():
    out = enr.transform(_post(cards=_card("Docker Blog", "https://www.docker.com/blog/x")))
    assert "| Docker Blog | [docker.com](https://www.docker.com) | 본문 1건 인용 |" in out
