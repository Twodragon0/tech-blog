#!/usr/bin/env python3
"""
convert_vercel_redirects_to_jekyll.py

Convert ``vercel.json`` redirects → ``redirect_from:`` front-matter on
the destination posts so jekyll-redirect-from emits equivalent 301s
when the site is served from GitHub Pages.

Mapping rules
-------------

- destination format ``/posts/YYYY/MM/DD/<slug>/`` maps to file
  ``_posts/YYYY-MM-DD-<slug>.md``.
- The ``source`` value (path) is appended to the ``redirect_from:``
  array on the destination post's front matter.
- If a destination is missing on disk, the redirect is reported as a
  ``skipped`` warning. The script exits 0 in that case (warnings only)
  unless ``--strict`` is passed.
- Existing ``redirect_from:`` entries are preserved; new entries are
  merged + de-duplicated, and the array is sorted for deterministic
  diffs.

Usage
-----

    python3 scripts/convert_vercel_redirects_to_jekyll.py            # apply
    python3 scripts/convert_vercel_redirects_to_jekyll.py --dry-run  # preview
    python3 scripts/convert_vercel_redirects_to_jekyll.py --strict   # fail on missing posts

The script prints a JSON summary on stderr suitable for CI logs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VERCEL_JSON = REPO_ROOT / "vercel.json"
DEFAULT_POSTS_DIR = REPO_ROOT / "_posts"

DEST_RE = re.compile(r"^/posts/(\d{4})/(\d{2})/(\d{2})/(.+?)/?$")


# ---------------------------------------------------------------------------
# Pure helpers (covered by unit tests)
# ---------------------------------------------------------------------------


def destination_to_post_path(destination: str, posts_dir: Path) -> Path | None:
    """Map ``/posts/YYYY/MM/DD/<slug>/`` → ``_posts/YYYY-MM-DD-<slug>.md``.

    Returns ``None`` if the destination does not match the canonical
    permalink shape.
    """
    if not destination:
        return None
    m = DEST_RE.match(destination)
    if not m:
        return None
    year, month, day, slug = m.groups()
    slug = slug.rstrip("/")
    if not slug:
        return None
    return posts_dir / f"{year}-{month}-{day}-{slug}.md"


def split_front_matter(text: str) -> tuple[str, str] | None:
    """Split ``---\\n...\\n---\\n<body>`` into (front_matter, body).

    Returns ``None`` if the file does not have a valid YAML front matter
    delimiter pair.
    """
    if not text.startswith("---"):
        return None
    # Find the closing delimiter on its own line. We look at the second
    # occurrence of "---" that appears on a line by itself.
    parts = text.split("\n")
    if not parts or parts[0].strip() != "---":
        return None
    end_idx = None
    for i in range(1, len(parts)):
        if parts[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None
    front_matter = "\n".join(parts[1:end_idx])
    body = "\n".join(parts[end_idx + 1:])
    return front_matter, body


def parse_existing_redirect_from(front_matter: str) -> list[str]:
    """Extract any pre-existing ``redirect_from:`` entries.

    Supports two YAML shapes:
      redirect_from: /a/
      redirect_from:
        - /a/
        - /b/

    The front-matter modifier in this script always emits the list
    (block) form for consistency, so this parser only needs to be good
    enough to detect duplicates.
    """
    lines = front_matter.split("\n")
    entries: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if not in_block:
            m = re.match(r"^redirect_from:\s*(.*)$", line)
            if m:
                rest = m.group(1).strip()
                if rest and not rest.startswith("#"):
                    # Inline scalar form
                    if rest.startswith("[") and rest.endswith("]"):
                        # Inline flow list — split commas
                        inner = rest[1:-1]
                        for item in inner.split(","):
                            item = item.strip().strip('"').strip("'")
                            if item:
                                entries.append(item)
                    else:
                        entries.append(rest.strip('"').strip("'"))
                else:
                    in_block = True
        else:
            # In block list, lines start with "  - ..." indented under the key.
            m = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if m:
                entries.append(m.group(1).strip().strip('"').strip("'"))
            elif stripped == "" or stripped.startswith("#"):
                continue
            else:
                # End of redirect_from block
                break
    return entries


def merge_redirects(existing: Iterable[str], additions: Iterable[str]) -> list[str]:
    """De-duplicate + sort merged redirect paths."""
    seen: set[str] = set()
    out: list[str] = []
    for item in list(existing) + list(additions):
        item = item.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return sorted(out)


def remove_redirect_from_block(front_matter: str) -> str:
    """Strip any pre-existing ``redirect_from:`` key + block list."""
    lines = front_matter.split("\n")
    out: list[str] = []
    skipping = False
    for line in lines:
        if skipping:
            # Block list continuation: lines start with whitespace + "-"
            if re.match(r"^\s+-\s+", line) or line.strip() == "":
                continue
            # Different key reached
            skipping = False
            out.append(line)
            continue
        if re.match(r"^redirect_from:\s*$", line):
            skipping = True
            continue
        if re.match(r"^redirect_from:\s+\S", line):
            # Inline scalar/flow form — drop the single line
            continue
        out.append(line)
    return "\n".join(out)


def insert_redirect_from_block(front_matter: str, redirects: list[str]) -> str:
    """Append a block-list ``redirect_from:`` entry to the front matter."""
    fm = remove_redirect_from_block(front_matter).rstrip("\n")
    block = "redirect_from:\n" + "\n".join(f"  - {r}" for r in redirects)
    if fm:
        return fm + "\n" + block
    return block


# ---------------------------------------------------------------------------
# Conversion driver
# ---------------------------------------------------------------------------


def _safe_relative(path: Path, base: Path = REPO_ROOT) -> str:
    """Return ``path`` relative to ``base`` if possible, else as-is."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def load_vercel_redirects(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("redirects", []) or []


def collect_redirects_by_post(
    redirects: list[dict],
    posts_dir: Path,
) -> tuple[dict[Path, list[str]], list[dict]]:
    """Group sources under each destination post path.

    Returns ``(grouped, skipped)`` where ``skipped`` is a list of
    ``{"reason": ..., "redirect": ...}`` records for entries that did
    not map to an on-disk post.
    """
    grouped: dict[Path, list[str]] = defaultdict(list)
    skipped: list[dict] = []
    for r in redirects:
        dest = r.get("destination", "")
        src = r.get("source", "")
        post_path = destination_to_post_path(dest, posts_dir)
        if post_path is None:
            skipped.append({"reason": "unparsed-destination", "redirect": r})
            continue
        if not post_path.is_file():
            skipped.append({"reason": "post-not-found", "redirect": r,
                            "expected_path": str(post_path)})
            continue
        if src and src not in grouped[post_path]:
            grouped[post_path].append(src)
    return grouped, skipped


def apply_to_post(post_path: Path, new_redirects: list[str]) -> tuple[bool, list[str]]:
    """Inject ``redirect_from:`` entries into a post file.

    Returns ``(changed, merged_redirects)``.
    """
    text = post_path.read_text(encoding="utf-8")
    parsed = split_front_matter(text)
    if parsed is None:
        raise ValueError(f"{post_path}: no YAML front matter")
    front_matter, body = parsed
    existing = parse_existing_redirect_from(front_matter)
    merged = merge_redirects(existing, new_redirects)
    if merged == existing:
        return False, merged
    new_fm = insert_redirect_from_block(front_matter, merged)
    new_text = "---\n" + new_fm + "\n---\n" + body
    if new_text == text:
        return False, merged
    post_path.write_text(new_text, encoding="utf-8")
    return True, merged


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vercel-json", type=Path, default=DEFAULT_VERCEL_JSON)
    p.add_argument("--posts-dir", type=Path, default=DEFAULT_POSTS_DIR)
    p.add_argument("--dry-run", action="store_true",
                   help="Print summary without modifying files.")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 if any redirect destination is missing on disk.")
    args = p.parse_args(argv)

    redirects = load_vercel_redirects(args.vercel_json)
    grouped, skipped = collect_redirects_by_post(redirects, args.posts_dir)

    changed_posts = 0
    posts_modified: list[str] = []
    for post_path, new_srcs in sorted(grouped.items()):
        if args.dry_run:
            text = post_path.read_text(encoding="utf-8")
            parsed = split_front_matter(text)
            existing = parse_existing_redirect_from(parsed[0]) if parsed else []
            merged = merge_redirects(existing, new_srcs)
            if merged != existing:
                changed_posts += 1
                posts_modified.append(_safe_relative(post_path))
        else:
            changed, _ = apply_to_post(post_path, new_srcs)
            if changed:
                changed_posts += 1
                posts_modified.append(_safe_relative(post_path))

    summary = {
        "total_redirects": len(redirects),
        "destinations_grouped": len(grouped),
        "posts_modified": changed_posts,
        "skipped": len(skipped),
        "dry_run": args.dry_run,
    }
    print(json.dumps(summary, indent=2))
    if skipped:
        print(f"\n{len(skipped)} redirect(s) skipped:", file=sys.stderr)
        for s in skipped[:20]:
            r = s["redirect"]
            print(f"  [{s['reason']}] {r.get('source','')} -> {r.get('destination','')}",
                  file=sys.stderr)
        if len(skipped) > 20:
            print(f"  ... +{len(skipped) - 20} more", file=sys.stderr)
    if posts_modified:
        print(f"\nModified posts ({len(posts_modified)}):")
        for p in posts_modified[:20]:
            print(f"  {p}")
        if len(posts_modified) > 20:
            print(f"  ... +{len(posts_modified) - 20} more")

    if args.strict and skipped:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
