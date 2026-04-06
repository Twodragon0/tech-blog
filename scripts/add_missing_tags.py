#!/usr/bin/env python3
"""
add_missing_tags.py - Add missing tags: field to Jekyll blog posts.

Scans all .md files in _posts/ and adds appropriate tags to posts
that are missing the tags: field in their front matter.

Tag placement: after excerpt: and before image: (or at end of front matter
if those fields don't exist).

Usage:
    python3 scripts/add_missing_tags.py [--dry-run]
"""

import argparse
import os
import re
import sys

POSTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts"
)

# Tag generation rules based on keywords
CATEGORY_TAG_MAP = {
    "security": ["security"],
    "devsecops": ["devsecops", "security"],
    "devops": ["devops"],
    "cloud": ["cloud"],
    "kubernetes": ["kubernetes"],
    "finops": ["finops"],
    "incident": ["incident-response"],
    "blockchain": ["blockchain"],
    "ai": ["ai"],
}

FILENAME_TAG_MAP = {
    "aws": "aws",
    "gcp": "gcp",
    "azure": "azure",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "docker": "docker",
    "devsecops": "devsecops",
    "devops": "devops",
    "security": "security",
    "cloud": "cloud",
    "finops": "finops",
    "incident": "incident-response",
    "postmortem": "incident-response",
    "weekly_digest": "weekly-digest",
    "weekly-digest": "weekly-digest",
    "digest": "weekly-digest",
    "ai": "ai",
    "claude": "ai",
    "llm": "ai",
    "blockchain": "blockchain",
    "zero_trust": "zero-trust",
    "ztna": "zero-trust",
    "siem": "siem",
    "soc": "soc",
    "compliance": "compliance",
    "isms": "compliance",
    "cspm": "cloud-security",
    "waf": "security",
    "sast": "devsecops",
    "dast": "devsecops",
    "supply_chain": "supply-chain-security",
    "supplychain": "supply-chain-security",
    "npm": "supply-chain-security",
    "github": "github",
    "cicd": "devops",
    "ci_cd": "devops",
    "terraform": "infrastructure-as-code",
    "iac": "infrastructure-as-code",
    "karpenter": "kubernetes",
    "minikube": "kubernetes",
    "helm": "kubernetes",
    "istio": "kubernetes",
    "mfa": "security",
    "passkey": "security",
    "skt": "security",
    "vercel": "devops",
    "jekyll": "devops",
    "nlb": "cloud",
    "vpc": "cloud",
    "ecs": "cloud",
    "eks": "kubernetes",
    "kandji": "devops",
    "macos": "devops",
    "email": "devops",
    "spf": "security",
    "dkim": "security",
    "dmarc": "security",
    "sendgrid": "devops",
    "zscaler": "security",
    "cloudflare": "security",
}

# Title keyword mappings (lowercase substring match)
TITLE_TAG_MAP = {
    "보안": "security",
    "security": "security",
    "cloud": "cloud",
    "클라우드": "cloud",
    "kubernetes": "kubernetes",
    "쿠버네티스": "kubernetes",
    "docker": "docker",
    "도커": "docker",
    "devops": "devops",
    "devsecops": "devsecops",
    "aws": "aws",
    "finops": "finops",
    "인시던트": "incident-response",
    "incident": "incident-response",
    "postmortem": "incident-response",
    "ai": "ai",
    "weekly digest": "weekly-digest",
    "주간": "weekly-digest",
    "뉴스": "security-news",
    "news": "security-news",
}


def parse_front_matter(content: str):
    """
    Parse Jekyll front matter from content.
    Returns (front_matter_str, body_str, start_offset, end_offset) or None.
    """
    stripped = content.lstrip("\ufeff")
    bom_len = len(content) - len(stripped)

    if not stripped.startswith("---"):
        return None

    first_end = stripped.find("\n", 0)
    if first_end == -1:
        return None

    second_delim = stripped.find("\n---", first_end)
    if second_delim == -1:
        return None

    fm_start = first_end + 1
    fm_end = second_delim
    body_start = second_delim + 4  # skip '\n---'

    fm = stripped[fm_start:fm_end]
    body = stripped[body_start:]

    return fm, body, bom_len, fm_start, fm_end, body_start


def has_tags_field(fm: str) -> bool:
    """Check if front matter has a tags: field (even if empty)."""
    return bool(re.search(r"^tags\s*:", fm, re.MULTILINE))


def get_fm_field(fm: str, field: str):
    """Extract value of a front matter field (inline or block list)."""
    # Try inline: field: value or field: [v1, v2]
    inline = re.search(rf"^{field}\s*:\s*(.+)$", fm, re.MULTILINE)
    if inline:
        val = inline.group(1).strip()
        if val.startswith("["):
            # Parse inline array
            items = re.findall(r"[\w\-\.]+", val)
            return [i.lower() for i in items]
        return [val.lower()]

    # Try block list:
    # field:
    # - item1
    # - item2
    block = re.search(rf"^{field}\s*:\s*\n((?:\s*-\s*.+\n?)+)", fm, re.MULTILINE)
    if block:
        items = re.findall(r"-\s*(.+)", block.group(1))
        return [i.strip().lower() for i in items]

    return []


def generate_tags(fname: str, fm: str) -> list:
    """Generate appropriate tags based on filename, categories, and title."""
    tags = set()

    # From categories field
    categories = get_fm_field(fm, "categories") or get_fm_field(fm, "category")
    for cat in categories:
        cat_lower = cat.lower()
        for key, tag_list in CATEGORY_TAG_MAP.items():
            if key in cat_lower:
                for t in tag_list:
                    tags.add(t)

    # From filename (lowercase, split by separators)
    fname_lower = fname.lower().replace("-", "_")
    for keyword, tag in FILENAME_TAG_MAP.items():
        kw_normalized = keyword.replace("-", "_")
        if kw_normalized in fname_lower:
            tags.add(tag)

    # From title field
    title_match = re.search(r"^title\s*:\s*['\"]?(.*?)['\"]?\s*$", fm, re.MULTILINE)
    if title_match:
        title_lower = title_match.group(1).lower()
        for keyword, tag in TITLE_TAG_MAP.items():
            if keyword in title_lower:
                tags.add(tag)

    # Weekly digest posts: ensure both weekly-digest and security-news
    if "weekly_digest" in fname_lower or "weekly-digest" in fname_lower:
        tags.add("weekly-digest")
        tags.add("security-news")

    # Ensure at least one tag exists
    if not tags:
        # Fall back to generic tags from categories
        if categories:
            tags.add(categories[0].lower().replace(" ", "-"))
        else:
            tags.add("tech")

    # Limit to 5 tags, sorted for determinism
    tag_list = sorted(tags)[:5]
    return tag_list


def insert_tags_into_fm(fm: str, tags: list) -> str:
    """Insert tags: field after excerpt: and before image:, or at end of fm."""
    tags_line = "tags: [" + ", ".join(tags) + "]"

    # Try to insert after excerpt:
    excerpt_match = re.search(r"^(excerpt\s*:.*(?:\n(?!\w).*)*)$", fm, re.MULTILINE)
    if excerpt_match:
        insert_pos = excerpt_match.end()
        return fm[:insert_pos] + "\n" + tags_line + fm[insert_pos:]

    # Try to insert before image:
    image_match = re.search(r"^image\s*:", fm, re.MULTILINE)
    if image_match:
        insert_pos = image_match.start()
        return fm[:insert_pos] + tags_line + "\n" + fm[insert_pos:]

    # Append at end of front matter
    return fm.rstrip("\n") + "\n" + tags_line + "\n"


def process_file(fpath: str, dry_run: bool = False) -> dict:
    """
    Process a single post file.
    Returns a dict with status info.
    """
    fname = os.path.basename(fpath)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    parsed = parse_front_matter(content)
    if parsed is None:
        return {"file": fname, "status": "no_front_matter"}

    fm, body, bom_len, fm_start, fm_end, body_start = parsed

    if has_tags_field(fm):
        # Check if tags has actual values
        tags_match = re.search(r"^tags\s*:\s*(.*)$", fm, re.MULTILINE)
        if tags_match:
            val = tags_match.group(1).strip()
            if val:  # inline value present
                return {"file": fname, "status": "has_tags", "tags": val}
            else:
                # Check for block list on next lines
                block_match = re.search(
                    r"^tags\s*:\s*\n((?:[ \t]*-[ \t]*.+\n?)+)", fm, re.MULTILINE
                )
                if block_match:
                    return {"file": fname, "status": "has_tags", "tags": "block_list"}
                else:
                    # Empty tags field - treat as missing
                    return {"file": fname, "status": "empty_tags_needs_fill"}
        return {"file": fname, "status": "has_tags"}

    # Missing tags - generate and insert
    tags = generate_tags(fname, fm)
    new_fm = insert_tags_into_fm(fm, tags)

    # Reconstruct the full content
    bom = content[:bom_len] if bom_len > 0 else ""
    stripped = content[bom_len:]
    new_content = bom + "---" + new_fm + "---" + stripped[fm_end + 3 :]

    if not dry_run:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return {"file": fname, "status": "added_tags", "tags": tags}


def main():
    parser = argparse.ArgumentParser(
        description="Add missing tags: field to Jekyll posts"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing"
    )
    parser.add_argument(
        "--posts-dir",
        default=POSTS_DIR,
        help=f"Path to _posts directory (default: {POSTS_DIR})",
    )
    args = parser.parse_args()

    posts_dir = args.posts_dir
    if not os.path.isdir(posts_dir):
        print(f"ERROR: Posts directory not found: {posts_dir}")
        sys.exit(1)

    md_files = sorted(f for f in os.listdir(posts_dir) if f.endswith(".md"))
    print(f"Scanning {len(md_files)} posts in {posts_dir}")
    if args.dry_run:
        print("DRY RUN - no files will be modified\n")

    results = {
        "has_tags": [],
        "added_tags": [],
        "empty_tags_needs_fill": [],
        "no_front_matter": [],
        "errors": [],
    }

    for fname in md_files:
        fpath = os.path.join(posts_dir, fname)
        try:
            result = process_file(fpath, dry_run=args.dry_run)
            status = result["status"]
            if status not in results:
                results[status] = []
            results[status].append(result)
        except Exception as e:
            results["errors"].append({"file": fname, "error": str(e)})

    # Report
    print(f"\n{'=' * 60}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Posts with existing tags:    {len(results['has_tags'])}")
    print(f"  Posts with tags added:       {len(results['added_tags'])}")
    print(f"  Posts with empty tags field: {len(results['empty_tags_needs_fill'])}")
    print(f"  Posts with no front matter:  {len(results['no_front_matter'])}")
    print(f"  Errors:                      {len(results['errors'])}")

    if results["added_tags"]:
        print(f"\n{'=' * 60}")
        action = "Would add" if args.dry_run else "Added"
        print(f"{action} tags to {len(results['added_tags'])} posts:")
        print(f"{'=' * 60}")
        for r in results["added_tags"]:
            print(f"  {r['file']}")
            print(f"    tags: {r['tags']}")

    if results["empty_tags_needs_fill"]:
        print(f"\n{'=' * 60}")
        print(
            f"WARNING: {len(results['empty_tags_needs_fill'])} posts have empty tags field:"
        )
        print(f"{'=' * 60}")
        for r in results["empty_tags_needs_fill"]:
            print(f"  {r['file']}")

    if results["no_front_matter"]:
        print(
            f"\nWARNING: {len(results['no_front_matter'])} posts have no front matter:"
        )
        for r in results["no_front_matter"]:
            print(f"  {r['file']}")

    if results["errors"]:
        print(f"\nERRORS ({len(results['errors'])}):")
        for r in results["errors"]:
            print(f"  {r['file']}: {r['error']}")

    print(f"\n{'=' * 60}")
    if results["added_tags"]:
        if args.dry_run:
            print("DRY RUN complete. Run without --dry-run to apply changes.")
        else:
            print(f"Successfully added tags to {len(results['added_tags'])} posts.")
    else:
        print("All posts already have tags: field. No changes needed.")
    print(f"{'=' * 60}")

    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
