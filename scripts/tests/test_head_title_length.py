"""Keep <title> short enough that mobile results still show the brand.

Long Korean post titles plus " | Twodragon's Tech Blog" were cut off on mobile
SERPs, and the home page rendered as "Home | Twodragon's Tech Blog".
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HEAD = (ROOT / "_includes" / "head.html").read_text()
CONFIG = yaml.safe_load((ROOT / "_config.yml").read_text())


def _title_tag():
    start = HEAD.index("<title>")
    return HEAD[start:HEAD.index("</title>", start)]


def test_page_titles_use_short_brand_suffix():
    assert CONFIG["title_short"] == "Twodragon"
    tag = _title_tag()
    assert "| {{ site.title_short }}" in tag
    assert "| {{ site.title }}" not in tag


def test_home_title_is_descriptive_not_home():
    home_title = CONFIG["home_title"]
    assert home_title.startswith(CONFIG["title"])
    # Google cuts titles around 600px (~50 Latin characters); Hangul is wider.
    assert len(home_title) <= 45
    assert "page.url == '/'" in _title_tag()
