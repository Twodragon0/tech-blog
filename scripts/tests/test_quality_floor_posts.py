"""quality_floor_posts.py: which posts the 60-point quality floor applies to."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quality_floor_posts import is_imported_wp_post, main  # noqa: E402

IMPORTED = '---\ntitle: "x"\noriginal_url: https://2twodragon.com/zscaler-guide/\n---\nbody\n'


def test_imported_wordpress_post_is_exempt():
    assert is_imported_wp_post(IMPORTED)


def test_quoted_values_are_recognised():
    assert is_imported_wp_post("---\noriginal_url: 'https://2twodragon.com/a/'\n---\n")
    assert is_imported_wp_post('---\noriginal_url: "https://www.2twodragon.com/a/"\n---\n')


def test_other_hosts_are_gated():
    assert not is_imported_wp_post("---\noriginal_url: https://twodragon.tistory.com/1\n---\n")
    assert not is_imported_wp_post("---\noriginal_url: https://tech.2twodragon.com/a/\n---\n")


def test_body_line_does_not_exempt_an_authored_post():
    text = '---\ntitle: "x"\n---\noriginal_url: https://2twodragon.com/a/\n'
    assert not is_imported_wp_post(text)


def test_no_front_matter_is_gated():
    assert not is_imported_wp_post("original_url: https://2twodragon.com/a/\n")


def test_cli_prints_gated_drops_exempt_and_missing(tmp_path, capsys):
    imported = tmp_path / "imported.md"
    imported.write_text(IMPORTED, encoding="utf-8")
    authored = tmp_path / "authored.md"
    authored.write_text('---\ntitle: "y"\n---\nbody\n', encoding="utf-8")
    missing = tmp_path / "deleted.md"

    assert main([str(imported), str(authored), str(missing)]) == 0
    out, err = capsys.readouterr()
    assert out.splitlines() == [str(authored)]
    assert str(imported) in err
