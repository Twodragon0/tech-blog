#!/usr/bin/env python3
"""Bulk regenerate legacy digest SVGs for pre-2026-04-02 blog posts.

Classification + manifest pipeline that routes each post into one of six
lanes (digest, tutorial, postmortem, roadmap, news-roundup, manual-review)
and regenerates only the lanes currently supported by safe generators.

Safety rules (default-deny overwrite):
- Never touch files under assets/images/diagrams/** or _unused_archive/**
- Never touch filenames matching bespoke patterns (learning-path, flow,
  timeline, architecture, attack-chain, ecosystem, roadmap, mermaid)
- manual-review lane is ALWAYS skipped regardless of --execute
- Only the `digest` and `news-roundup` lanes are wired to a working
  generator right now — other lanes emit manifest entries for follow-up

Usage:
    # Dry-run (always start here):
    python3 scripts/bulk_regenerate_old_svgs.py --dry-run

    # Execute digest lane only (safest):
    python3 scripts/bulk_regenerate_old_svgs.py --execute --lane digest

    # Execute digest + news-roundup lanes:
    python3 scripts/bulk_regenerate_old_svgs.py --execute \
        --lane digest --lane news-roundup

    # Output the classification manifest without touching files:
    python3 scripts/bulk_regenerate_old_svgs.py --dry-run \
        --manifest-out bulk_regen_manifest.json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "_posts"
IMAGES_DIR = BASE_DIR / "assets" / "images"

if str(BASE_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "scripts"))

# Only import generators on demand to keep --dry-run fast and offline.
_LANE_GENERATORS: dict[str, object] = {}  # type: ignore
_CONVERT_OG = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("bulk-regen")


# ---------------------------------------------------------------------------
# Cutoff — only backfill posts dated BEFORE this boundary
# ---------------------------------------------------------------------------

CUTOFF = datetime(2026, 4, 2)

# Lanes that currently have a working, safe generator wired up.
# Each lane is routed via auto_publish_news.generate_svg_image →
# scripts/news/svg_generator layout functions:
#   digest/news-roundup → generate_card_signal_svg
#   tutorial            → generate_tutorial_stack_svg  (3-pillar stack)
#   postmortem          → generate_timeline_pulse_svg  (ECG timeline)
#   roadmap             → generate_milestone_curve_svg (S-curve)
#   comparison          → generate_versus_split_svg    (left/right split)
EXECUTABLE_LANES = frozenset(
    {
        "digest",
        "news-roundup",
        "tutorial",
        "postmortem",
        "roadmap",
        "comparison",
    }
)


# ---------------------------------------------------------------------------
# Safety rules — default-deny overwrite
# ---------------------------------------------------------------------------

# Directories that are never touched, regardless of lane.
PROTECTED_DIRS = (
    "assets/images/diagrams",
    "assets/images/mermaid",
    "assets/images/_unused_archive",
)

# Filename markers that indicate a bespoke hand-crafted asset.
#
# The tokens must appear in a structural position (separated by '-' or at the
# tail of the stem, ending in .svg) rather than as a substring match — because
# words like "architecture" and "timeline" commonly appear inside legitimate
# tutorial/guide post titles (e.g. "AWS Security Architecture Week 2"),
# and we were incorrectly skipping those from regeneration.
#
# Format: bare filename stem ends with one of these tokens, optionally
# followed by a short suffix like "-diagram" or "-v2". Example matches:
#   learning-path.svg, learning_path.svg, roadmap-structure.svg,
#   tools-stack.svg, incident-timeline.svg, devsecops-architecture.svg,
#   attack-chain-v2.svg, mermaid.svg, flow-diagram.svg, flowchart-1.svg
BESPOKE_FILENAME_TOKENS = (
    "learning-path",
    "learning_path",
    "roadmap-structure",
    "tools-stack",
    "attack-chain",
    "attack_chain",
    "mermaid",
    "before-after",
    "flow-diagram",
    "flowchart",
    "ecosystem-diagram",
)

# Tokens that only qualify as bespoke when they appear as a standalone
# trailing segment (e.g. "-architecture.svg" but NOT "_Security_Architecture_Week2").
_BESPOKE_SUFFIX_PATTERN = re.compile(
    r"-(?:architecture|timeline|dashboard|topology|flow|diagram)"
    r"(?:-[a-z0-9]+)?\.svg$",
    re.IGNORECASE,
)


def is_bespoke_asset(image_path: str) -> bool:
    """Return True if the image is a hand-crafted asset that must not be
    overwritten automatically.

    Matching strategy:
      1. Protected directories (diagrams/, mermaid/, _unused_archive/) are
         unconditionally skipped.
      2. Filename stems containing a bespoke token are skipped.
      3. Filenames whose trailing segment matches the suffix pattern
         (``-architecture.svg``, ``-timeline-v2.svg``, …) are skipped.
    """
    lower = image_path.lower()
    if any(lower.startswith("/" + d) or d in lower for d in PROTECTED_DIRS):
        return True
    fname = Path(image_path).name.lower()
    if any(token in fname for token in BESPOKE_FILENAME_TOKENS):
        return True
    return bool(_BESPOKE_SUFFIX_PATTERN.search(fname))


# ---------------------------------------------------------------------------
# Classification — rule-based, conservative
# ---------------------------------------------------------------------------

DIGEST_PATTERNS = (
    r"weekly.?digest",
    r"daily.?digest",
    r"tech.?security.?weekly",
    r"security.?weekly",
    r"weekly.?tech",
    r"security.?threat.?intelligence",
    r"rss.?roundup",
    r"news.?roundup",
    r"tech.?blog.?weekly",
    r"daily.?tech.?digest",
    r"monthly.?index",
    # Generic _Digest_ catch-all — matches Security_Cloud_Digest, Blockchain_Tech_Digest,
    # AI_Cloud_Digest, DevOps_Blockchain_Digest, Krebs_Security_Digest, etc.
    r"(?:^|_)digest(?:_|\.|$)",
    r"digest.*\.md$",
    r"patch.?tuesday",
    r"vendor.?blog.?(?:weekly|review)",
)

POSTMORTEM_PATTERNS = (
    r"postmortem",
    r"post.?mortem",
    r"incident.?(report|analysis)",
    r"outage",
)

ROADMAP_PATTERNS = (
    r"roadmap",
    r"learning.?path",
    r"career.?path",
    r"maturity.?model",
)

TUTORIAL_PATTERNS = (
    r"complete.?guide",
    r"설치",
    r"course",
    r"practical",
    r"how.?to",
    r"step.?by.?step",
    r"tutorial",
    r"hands.?on",
)

NEWS_ROUNDUP_PATTERNS = (
    r"cloud.?updates",
    r"monthly.?recap",
    r"quarterly.?review",
    r"vendor.?review",
    r"trend.?review",
)

COMPARISON_PATTERNS = (
    r"comparison",
    r"vs\.?",
    r"versus",
    r"비교",
)


def classify_post(front_matter: dict, post_name: str) -> str:
    """Return a lane label for the given post.

    Rules, evaluated in order:
        1. postmortem / roadmap / comparison (rare but distinct)
        2. digest (most common)
        3. news-roundup (monthly recaps etc.)
        4. tutorial (guides, courses, how-tos)
        5. manual-review (default, safe)
    """
    title = str(front_matter.get("title", "")).lower()
    filename = post_name.lower()
    blob = f"{title} {filename}"

    def _match(patterns: tuple[str, ...]) -> bool:
        return any(re.search(p, blob) for p in patterns)

    if _match(POSTMORTEM_PATTERNS):
        return "postmortem"
    if _match(ROADMAP_PATTERNS):
        return "roadmap"
    if _match(COMPARISON_PATTERNS):
        return "comparison"
    if _match(DIGEST_PATTERNS):
        return "digest"
    if _match(NEWS_ROUNDUP_PATTERNS):
        return "news-roundup"
    if _match(TUTORIAL_PATTERNS):
        return "tutorial"
    return "manual-review"


# ---------------------------------------------------------------------------
# Manifest entry
# ---------------------------------------------------------------------------


@dataclass
class ManifestEntry:
    post_name: str
    post_date: str
    title: str
    image_path: str
    lane: str
    action: str  # "regenerate" | "skip-bespoke" | "skip-protected" | "skip-lane"
    reason: str
    current_svg_bytes: Optional[int] = None
    new_svg_bytes: Optional[int] = None
    tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Post loader
# ---------------------------------------------------------------------------


def load_front_matter(post_path: Path) -> dict:
    text = post_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def parse_post_date(post_name: str) -> Optional[datetime]:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", post_name)
    if not match:
        return None
    try:
        return datetime.fromisoformat(f"{match.group(1)}T00:00:00")
    except ValueError:
        return None


def collect_candidates() -> list[tuple[Path, dict, datetime]]:
    """Return [(post_path, front_matter, post_date)] for posts before CUTOFF."""
    candidates: list[tuple[Path, dict, datetime]] = []
    for post_path in sorted(POSTS_DIR.glob("*.md")):
        post_date = parse_post_date(post_path.name)
        if post_date is None or post_date >= CUTOFF:
            continue
        front_matter = load_front_matter(post_path)
        if not front_matter:
            continue
        candidates.append((post_path, front_matter, post_date))
    return candidates


# ---------------------------------------------------------------------------
# Build a manifest entry per post
# ---------------------------------------------------------------------------


def build_entry(
    post_path: Path, front_matter: dict, post_date: datetime
) -> ManifestEntry:
    image_path = str(front_matter.get("image", "")).strip()
    title = str(front_matter.get("title", "")).strip()
    tags = [str(t).strip() for t in front_matter.get("tags", []) or []]
    lane = classify_post(front_matter, post_path.name)

    svg_file: Optional[Path] = None
    current_bytes: Optional[int] = None
    if image_path:
        svg_file = (BASE_DIR / image_path.lstrip("/")).resolve()
        if svg_file.exists():
            current_bytes = svg_file.stat().st_size

    if not image_path:
        return ManifestEntry(
            post_name=post_path.name,
            post_date=post_date.strftime("%Y-%m-%d"),
            title=title,
            image_path="",
            lane=lane,
            action="skip-no-image",
            reason="front matter has no image field",
            tags=tags,
        )

    if is_bespoke_asset(image_path):
        return ManifestEntry(
            post_name=post_path.name,
            post_date=post_date.strftime("%Y-%m-%d"),
            title=title,
            image_path=image_path,
            lane=lane,
            action="skip-bespoke",
            reason="bespoke filename or protected directory",
            current_svg_bytes=current_bytes,
            tags=tags,
        )

    if svg_file is None or not svg_file.exists():
        return ManifestEntry(
            post_name=post_path.name,
            post_date=post_date.strftime("%Y-%m-%d"),
            title=title,
            image_path=image_path,
            lane=lane,
            action="skip-missing",
            reason="image file not found on disk",
            tags=tags,
        )

    if lane not in EXECUTABLE_LANES:
        return ManifestEntry(
            post_name=post_path.name,
            post_date=post_date.strftime("%Y-%m-%d"),
            title=title,
            image_path=image_path,
            lane=lane,
            action="skip-lane",
            reason=f"lane '{lane}' does not have a working bulk generator yet",
            current_svg_bytes=current_bytes,
            tags=tags,
        )

    return ManifestEntry(
        post_name=post_path.name,
        post_date=post_date.strftime("%Y-%m-%d"),
        title=title,
        image_path=image_path,
        lane=lane,
        action="regenerate",
        reason=f"lane '{lane}' — safe to regenerate via card-signal-map",
        current_svg_bytes=current_bytes,
        tags=tags,
    )


# ---------------------------------------------------------------------------
# Regeneration for a single entry (digest / news-roundup lane only)
# ---------------------------------------------------------------------------


def _lazy_import_generator() -> None:
    """Populate _LANE_GENERATORS with one generator per executable lane.

    Importing up-front would slow down --dry-run (no files touched) and
    pull in heavy dependencies, so generators are only loaded on the
    first --execute call.
    """
    global _CONVERT_OG
    if _LANE_GENERATORS:
        return
    from auto_publish_news import _convert_svg_to_og_png  # type: ignore
    from news.svg_generator import (  # type: ignore
        generate_card_signal_svg,
        generate_milestone_curve_svg,
        generate_timeline_pulse_svg,
        generate_tutorial_stack_svg,
        generate_versus_split_svg,
    )

    _LANE_GENERATORS.update(
        {
            "digest": generate_card_signal_svg,
            "news-roundup": generate_card_signal_svg,
            "tutorial": generate_tutorial_stack_svg,
            "postmortem": generate_timeline_pulse_svg,
            "roadmap": generate_milestone_curve_svg,
            "comparison": generate_versus_split_svg,
        }
    )
    _CONVERT_OG = _convert_svg_to_og_png


def _build_news_items_from_post(front_matter: dict, post_name: str) -> list[dict]:
    """Synthesize news items from frontmatter for the generator."""
    title = str(front_matter.get("title", "")).strip()
    excerpt = str(front_matter.get("excerpt", "")).strip()
    tags = [str(t).strip() for t in front_matter.get("tags", []) or []]

    seeds = [title] + tags[:4]
    items: list[dict] = []
    for i, seed in enumerate(seeds):
        if not seed:
            continue
        items.append(
            {
                "title": seed if i == 0 else f"{seed} briefing",
                "summary": excerpt,
            }
        )
    if not items:
        items.append({"title": post_name, "summary": excerpt})
    return items


def _build_categorized(
    front_matter: dict, news_items: list[dict]
) -> dict[str, list[dict]]:
    categorized: defaultdict[str, list[dict]] = defaultdict(list)
    primary = str(front_matter.get("category", "")).strip().lower()
    secondary = [
        str(c).strip().lower()
        for c in front_matter.get("categories", []) or []
        if str(c).strip()
    ]
    keys = [k for k in [primary] + secondary if k]
    if not keys:
        keys = ["security"]  # Default so the generator picks card-signal-map
    for key in keys:
        categorized[key].append(news_items[0])
    return dict(categorized)


def regenerate_entry(entry: ManifestEntry) -> None:
    """Run the safe generator for a single manifest entry.

    Critically, this dispatches directly by ``entry.lane`` rather than
    relying on ``auto_publish_news.generate_svg_image`` to re-classify.
    The manifest's classification is authoritative — the generator's
    internal heuristic can disagree (e.g. on non-English titles that
    don't match filename-based tutorial markers), which would cause a
    postmortem post to render as a legacy TECH SIGNAL MAP.

    Raises KeyError on an unknown lane — the caller should ensure lanes
    are validated via :data:`EXECUTABLE_LANES` first.
    """
    _lazy_import_generator()
    generator = _LANE_GENERATORS.get(entry.lane)
    if generator is None:
        raise KeyError(f"No generator wired up for lane '{entry.lane}'")
    assert _CONVERT_OG is not None

    post_path = POSTS_DIR / entry.post_name
    front_matter = load_front_matter(post_path)
    news_items = _build_news_items_from_post(front_matter, entry.post_name)
    categorized = _build_categorized(front_matter, news_items)
    post_date = datetime.fromisoformat(f"{entry.post_date}T00:00:00")

    svg_content = generator(post_date, categorized, news_items)  # type: ignore[operator]
    svg_path = (BASE_DIR / entry.image_path.lstrip("/")).resolve()
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_content, encoding="utf-8")
    entry.new_svg_bytes = svg_path.stat().st_size

    # OG PNG via existing helper (writes the .png alongside the .svg).
    _CONVERT_OG(svg_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify and print the manifest but do not write files.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually regenerate SVGs for lanes that are safe to process.",
    )
    parser.add_argument(
        "--lane",
        action="append",
        choices=["digest", "news-roundup", "tutorial", "postmortem", "roadmap",
                 "comparison", "manual-review"],
        help="Restrict processing to these lanes. Repeatable.",
    )
    parser.add_argument(
        "--manifest-out",
        help="Write the classification manifest to this JSON file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process at most N entries (0 = no limit). Useful for sampling.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.dry_run and not args.execute:
        log.warning(
            "Neither --dry-run nor --execute given; defaulting to --dry-run."
        )
        args.dry_run = True

    log.info("[bulk-regen] Collecting candidates from %s", POSTS_DIR)
    candidates = collect_candidates()
    log.info("[bulk-regen] Found %d posts dated before %s",
             len(candidates), CUTOFF.strftime("%Y-%m-%d"))

    entries: list[ManifestEntry] = []
    for post_path, front_matter, post_date in candidates:
        entries.append(build_entry(post_path, front_matter, post_date))

    # Lane filtering (for --execute phased rollout)
    allowed_lanes: Optional[set[str]] = set(args.lane) if args.lane else None

    lane_counts = Counter(e.lane for e in entries)
    action_counts = Counter(e.action for e in entries)
    log.info("[bulk-regen] Lane distribution: %s", dict(lane_counts))
    log.info("[bulk-regen] Action distribution: %s", dict(action_counts))

    # Write manifest
    if args.manifest_out:
        out_path = Path(args.manifest_out)
        out_path.write_text(
            json.dumps(
                [asdict(e) for e in entries],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        log.info("[bulk-regen] Manifest written: %s", out_path)

    # Dry-run summary
    if args.dry_run:
        log.info("[bulk-regen] DRY-RUN: listing entries that would regenerate")
        count = 0
        for e in entries:
            if e.action != "regenerate":
                continue
            if allowed_lanes and e.lane not in allowed_lanes:
                continue
            size_kb = (e.current_svg_bytes or 0) / 1024
            log.info("  REGEN [%s] %s (%.1f KB) — %s",
                     e.lane, e.post_name, size_kb, e.title[:60])
            count += 1
            if args.limit and count >= args.limit:
                break
        log.info("[bulk-regen] DRY-RUN would regenerate %d entries", count)
        return 0

    # Execute
    if not args.execute:
        return 0

    to_process = [
        e for e in entries
        if e.action == "regenerate"
        and (not allowed_lanes or e.lane in allowed_lanes)
    ]
    if args.limit:
        to_process = to_process[: args.limit]

    log.info("[bulk-regen] EXECUTE: regenerating %d entries", len(to_process))
    success = 0
    failures: list[tuple[str, str]] = []
    for entry in to_process:
        try:
            regenerate_entry(entry)
            delta = (entry.new_svg_bytes or 0) - (entry.current_svg_bytes or 0)
            log.info(
                "  ✓ [%s] %s  %d → %d bytes (%+d)",
                entry.lane,
                entry.post_name,
                entry.current_svg_bytes or 0,
                entry.new_svg_bytes or 0,
                delta,
            )
            success += 1
        except Exception as exc:  # noqa: BLE001 - bulk pass must keep going
            failures.append((entry.post_name, str(exc)))
            log.error("  ✗ [%s] %s failed: %s",
                      entry.lane, entry.post_name, exc)

    log.info(
        "[bulk-regen] Done. Success: %d  Failures: %d",
        success,
        len(failures),
    )
    if failures:
        for name, err in failures:
            log.error("  FAIL: %s — %s", name, err)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
