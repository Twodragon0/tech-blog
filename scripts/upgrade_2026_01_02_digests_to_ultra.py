#!/usr/bin/env python3
"""Bulk-upgrade Jan/Feb 2026 weekly-digest SVGs to L22 ultra tier.

Targets every ``2026-01-*`` and ``2026-02-*`` ``Tech_Security_Weekly_Digest``
SVG in ``assets/images/`` whose current file size is below 30 KB.
For each target the matching ``_posts/*.md`` file is parsed via the
existing ``_extract_digest_topics`` / ``_route_l22_band`` helpers from
``generate_post_images.py`` so band content stays consistent with the
auto-generator. The SVG is then re-emitted with ``tier="ultra"`` to
match the late-April family (typically 60-70 KB).

Each band gets enriched with secondary ``metric_b`` / ``detail_b`` /
``mini2_*`` fields derived from the same topic text so the ultra tier
has visible additional rows and a second mini-card.

Usage::

    python3 scripts/upgrade_2026_01_02_digests_to_ultra.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_post_images import (  # noqa: E402
    _escape_svg_text,
    _extract_digest_topics,
    _extract_visual_tokens,
    _route_l22_band,
    _trim_l22_text,
    _sanitize_svg_forbidden_chars,
    validate_and_fix_svg,
)
from scripts.lib import svg_l22_generator as l22  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "assets" / "images"
POSTS = REPO_ROOT / "_posts"
SIZE_THRESHOLD_BYTES = 30 * 1024


def _load_post_for_svg(svg_path: Path) -> dict:
    """Find the ``_posts/*.md`` file matching ``svg_path`` and return parts.

    Returns a dict with ``filename``, ``title``, ``content``, and ``tags``.
    """
    md_path = POSTS / svg_path.name.replace(".svg", ".md")
    if not md_path.exists():
        raise FileNotFoundError(f"matching post not found: {md_path}")
    raw = md_path.read_text(encoding="utf-8")
    title_match = re.search(r'^title:\s*"([^"]+)"', raw, re.MULTILINE)
    tags_match = re.search(r"^tags:\s*\[([^\]]+)\]", raw, re.MULTILINE)
    body_match = re.split(r"^---\s*$", raw, maxsplit=2, flags=re.MULTILINE)
    body = body_match[2] if len(body_match) >= 3 else raw
    tags: list[str] = []
    if tags_match:
        tags = [t.strip().strip('"').strip("'") for t in tags_match.group(1).split(",") if t.strip()]
    return {
        "filename": md_path.name,
        "title": title_match.group(1) if title_match else md_path.stem,
        "content": body,
        "tags": tags,
    }


def _build_band_cfg(topic: str, used_themes: set) -> dict:
    """Build a single ultra-tier band cfg from ``topic`` text."""
    route = _route_l22_band(topic, used_themes)
    used_themes.add(route["theme"])
    theme_palette = l22.THEMES[route["theme"]]
    visual_fn = getattr(l22, route["visual_name"])
    try:
        visual_svg = visual_fn(500, 105, theme_palette["accent"], theme_palette["soft"])
    except TypeError:
        visual_svg = visual_fn(500, 105, theme_palette["accent"])

    headline = _trim_l22_text(topic, 36)
    metric = _trim_l22_text(topic, 48)
    detail = _trim_l22_text(topic, 96)

    badge_value = (route["badge_label"][:4] or "INFO").upper()
    label_short = route["label"]

    metric_b = _trim_l22_text(f"DevSecOps : {label_short.lower()} response", 60)
    detail_b = _trim_l22_text(
        f"Detection rules + IoC pre-load + secret rotation + SBOM verify : {label_short.lower()}",
        110,
    )
    mini2_value = badge_value[:4]
    mini2_label = "BADGE"
    mini2_sub = "context"

    return {
        "theme": route["theme"],
        "label": label_short,
        "headline": headline,
        "metric": metric,
        "detail": detail,
        "metric_b": metric_b,
        "detail_b": detail_b,
        "badge_value": badge_value,
        "badge_label": route["badge_label"],
        "badge_sub": "highlighted",
        "mini_value": label_short[:4],
        "mini_label": "FOCUS",
        "mini_sub": "weekly",
        "mini2_value": mini2_value,
        "mini2_label": mini2_label,
        "mini2_sub": mini2_sub,
        "visual": visual_svg,
    }


def _upgrade_svg(svg_path: Path) -> tuple[float, int]:
    """Regenerate ``svg_path`` at tier='ultra'. Returns (kb_size, lines)."""
    post_info = _load_post_for_svg(svg_path)
    topics = _extract_digest_topics(post_info["content"], max_topics=3)
    if len(topics) < 3:
        for token in _extract_visual_tokens(post_info, limit=8):
            if token and token not in topics:
                topics.append(token)
            if len(topics) >= 3:
                break
    while len(topics) < 3:
        topics.append("Security Update")

    used_themes: set = set()
    bands_cfg = [_build_band_cfg(t, used_themes) for t in topics[:3]]

    title = post_info["title"]
    aria = _trim_l22_text(title, 200) or "Weekly digest cover"
    svg_title = _trim_l22_text(title, 240) or "Weekly digest"

    m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md", post_info["filename"])
    if m:
        yyyy, mm, dd, slug = m.groups()
        slug_url = slug.replace("_", "-")
        url = f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug_url}/"
    else:
        url = "https://tech.2twodragon.com/"

    svg = l22.render_bands_svg(
        sfx="L22U",
        aria=_escape_svg_text(aria),
        title=_escape_svg_text(svg_title),
        url=url,
        bands_cfg=bands_cfg,
        tier="ultra",
    )
    svg = validate_and_fix_svg(svg)
    svg_path.write_text(svg, encoding="utf-8")
    _sanitize_svg_forbidden_chars(svg_path)

    size_kb = svg_path.stat().st_size / 1024
    line_count = svg.count("\n") + 1
    return size_kb, line_count


def _collect_targets() -> list[Path]:
    """Return weekly-digest SVGs for 2026-01 and 2026-02 below the threshold."""
    candidates = sorted(
        list(ASSETS.glob("2026-01-*Tech_Security_Weekly_Digest*.svg"))
        + list(ASSETS.glob("2026-02-*Tech_Security_Weekly_Digest*.svg"))
    )
    return [p for p in candidates if p.stat().st_size < SIZE_THRESHOLD_BYTES]


def main() -> None:
    targets = _collect_targets()
    if not targets:
        print("No 2026-01/02 weekly digests under 30 KB. Nothing to do.")
        return

    print(f"Upgrading {len(targets)} digest SVG(s) to L22 ultra tier...")
    upgraded = 0
    failed: list[str] = []
    for svg in targets:
        before_kb = svg.stat().st_size / 1024
        try:
            after_kb, lines = _upgrade_svg(svg)
        except Exception as exc:  # pragma: no cover - reported per-file
            failed.append(f"{svg.name}: {exc}")
            print(f"  FAIL {svg.name}: {exc}")
            continue
        upgraded += 1
        delta = after_kb - before_kb
        print(
            f"  ok   {svg.name}: {before_kb:.1f}KB -> {after_kb:.1f}KB "
            f"({delta:+.1f}KB, {lines} lines)"
        )

    print(f"\nDone: {upgraded}/{len(targets)} upgraded.")
    if failed:
        print("Failures:")
        for entry in failed:
            print(f"  {entry}")
        sys.exit(1)


if __name__ == "__main__":
    main()
