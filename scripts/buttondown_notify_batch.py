#!/usr/bin/env python3
"""
Buttondown Batch Email Notification Script
Processes multiple blog posts and sends email notifications for each.
Takes post paths as arguments, or the POSTS_JSON list that the workflow's
"Check for new posts" step builds from github.event.before..github.sha. A local
run without either diffs HEAD~1..HEAD itself.
Note: Only new posts trigger email notifications. Updated posts are excluded.

Guards (added 2026-11-21, after one push tried to mail 36 imported WordPress
posts at once):
- A post whose ``original_url`` is on a 2twodragon.com host is imported
  content, not a new post. It is never mailed.
- More than BUTTONDOWN_MAX_POSTS (default 3) mailable posts in one run is
  treated as a bulk import, and nothing is sent.
Either way the run writes a ::warning:: and a GitHub step summary instead.

Exit status: 1 when the API key was rejected (401/403) or Buttondown refused a
request for another reason, because both need a person. 0 otherwise, including
transient failures (429, 5xx, timeout), which are reported as ::warning::.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

# .env 파일에서 환경 변수 로드
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Validate key is a valid identifier before setting
                if key.isidentifier():
                    os.environ[key] = value

sys.path.insert(0, str(SCRIPT_DIR))
from buttondown_notify import (
    AUTH_REJECTED,
    FAILED,
    SENT,
    TRANSIENT,
    find_post_file,
    notify_post,
    parse_frontmatter,
)

DEFAULT_MAX_POSTS = 3
IMPORTED_HOST = "2twodragon.com"


def max_posts_per_run(raw: "str | None") -> int:
    """BUTTONDOWN_MAX_POSTS as a positive int; unset or invalid gives the default."""
    try:
        value = int((raw or "").strip())
    except ValueError:
        return DEFAULT_MAX_POSTS
    return value if value > 0 else DEFAULT_MAX_POSTS


def imported_from(frontmatter: dict) -> str:
    """The post's ``original_url`` if it points at a 2twodragon.com host, else ''."""
    url = str(frontmatter.get("original_url") or "").strip()
    host = (urlsplit(url).hostname or "").lower()
    if host == IMPORTED_HOST or host.endswith("." + IMPORTED_HOST):
        return url
    return ""


def select_posts(posts: list, max_posts: int) -> tuple:
    """Split ``(path, frontmatter)`` pairs into ``(to_send, imported, bulk)``.

    Imported posts are never sent. If more than ``max_posts`` posts are left,
    none of them is sent either: they come back as ``bulk``.
    """
    imported = [(path, fm) for path, fm in posts if imported_from(fm)]
    to_send = [(path, fm) for path, fm in posts if not imported_from(fm)]
    if len(to_send) > max_posts:
        return [], imported, to_send
    return to_send, imported, []


def write_step_summary(lines: list) -> None:
    """Append Markdown to the GitHub step summary; no-op outside Actions."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def decode_posts_json(raw: str) -> list:
    """The paths in POSTS_JSON: a JSON array of base64-encoded UTF-8 paths.

    The workflow's check step writes it. Raises ValueError if it is malformed.
    """
    items = json.loads(raw)
    if not isinstance(items, list) or not all(isinstance(i, str) for i in items):
        raise ValueError("expected a JSON array of strings")
    return [base64.b64decode(item, validate=True).decode("utf-8") for item in items]


def detect_posts_via_git_diff():
    """Detect only new posts via git diff (excludes modified posts)."""
    posts = []

    try:
        # Get only added posts (new posts)
        # Modified posts are excluded to prevent email notifications for updates
        # -z: NUL-separated and unquoted, so non-ASCII names come out verbatim
        result = subprocess.run(
            [
                "git",
                "diff",
                "-z",
                "--name-only",
                "--diff-filter=A",
                "HEAD~1",
                "HEAD",
                "--",
                "_posts/*.md",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
        if result.returncode == 0:
            posts = [name for name in result.stdout.split("\0") if name]
        else:
            print(f"⚠️ git diff failed: {result.stderr.strip()}")

        if posts:
            print(f"📝 Detected {len(posts)} new post(s) (modified posts excluded)")

    except subprocess.TimeoutExpired:
        print("⚠️ Git diff command timed out")
    except Exception as e:
        print(f"⚠️ Error detecting posts via git diff: {e}")

    return posts


def main(argv: "list | None" = None) -> None:
    """Process posts given as arguments, from a JSON array, or from git diff."""
    parser = argparse.ArgumentParser(
        description="Send the Buttondown newsletter for new posts."
    )
    parser.add_argument(
        "posts",
        nargs="*",
        help="post files to send (default: POSTS_JSON, else git diff HEAD~1 HEAD)",
    )
    args = parser.parse_args(argv)

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    site_url = os.environ.get("SITE_URL", "https://2twodragon.com")
    max_posts = max_posts_per_run(os.environ.get("BUTTONDOWN_MAX_POSTS"))

    # Debug logging
    print("🔍 Debug: Environment variables")
    print(f"   BUTTONDOWN_API_KEY: {'set' if api_key else 'not set'}")
    print(f"   SITE_URL: {site_url}")
    print(f"   BUTTONDOWN_MAX_POSTS: {max_posts}")
    print("")

    if not api_key:
        print("::error::BUTTONDOWN_API_KEY environment variable not set")
        sys.exit(1)

    posts = []
    for raw_path in args.posts:
        post_file = find_post_file(raw_path)
        # find_post_file() falls back to any post sharing the date prefix, so a
        # mistyped post_path would mail a different post to every subscriber.
        # Accept only the file that was named.
        requested = Path(raw_path.strip().strip("'\"")).name
        if post_file.name != requested or not post_file.exists():
            print(f"::error::Post file not found: {raw_path}")
            sys.exit(1)
        posts.append(str(post_file))

    # In the workflow the check step hands over the posts it found, even an
    # empty list, so this script never works out a different range. Only a
    # local run without POSTS_JSON diffs for itself.
    posts_json = os.environ.get("POSTS_JSON")
    if not args.posts and posts_json is not None:
        print("📋 Using the posts the check step found (POSTS_JSON)")
        try:
            posts = decode_posts_json(posts_json)
        except ValueError as e:
            print(f"::error::POSTS_JSON from the check step is malformed: {e}")
            sys.exit(1)
    elif not args.posts:
        print("📋 Detecting posts via git diff HEAD~1 HEAD...")
        posts = detect_posts_via_git_diff()

    # Filter out draft posts and validate
    valid_posts = []
    for post_file in posts:
        post_path = Path(post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_file

        if not post_path.exists():
            print(f"⚠️ Post file not found: {post_path}")
            continue

        # Check if draft (quick check without full parsing)
        try:
            with open(post_path, "r", encoding="utf-8") as f:
                content = f.read(1000)  # Read first 1000 chars
                if "draft: true" in content or "draft: True" in content:
                    print(f"⏭️ Skipping draft post: {post_file}")
                    continue
        except Exception as e:
            print(f"⚠️ Error checking draft status for {post_file}: {e}")

        valid_posts.append(str(post_path))

    if not valid_posts:
        print("No valid post files found, nothing to send")
        print("   This might happen if:")
        print("   1. No new posts were detected (updated posts are excluded)")
        print("   2. All posts are marked as draft")
        print("   3. The post files don't exist")
        sys.exit(0)

    candidates = []
    for path in valid_posts:
        frontmatter = parse_frontmatter(path)
        if not isinstance(frontmatter, dict) or not frontmatter:
            frontmatter = {"title": Path(path).stem}
        candidates.append((path, frontmatter))

    to_send, imported, bulk = select_posts(candidates, max_posts)

    notes = []
    if imported:
        notes.append(
            f"Skipped {len(imported)} imported post(s) whose original_url is on "
            f"{IMPORTED_HOST}. They are not new posts, so no newsletter was sent "
            "for them."
        )
    if bulk:
        notes.append(
            f"{len(bulk)} new posts in one run is more than "
            f"BUTTONDOWN_MAX_POSTS={max_posts} and looks like a bulk import, so no "
            "newsletter was sent. To mail one of them, run this workflow manually "
            "with post_path."
        )
    summary = ["## Buttondown newsletter", ""]
    for note in notes:
        print(f"::warning::{note}")
        summary += [note, ""]
    summary += ["| Post | Result |", "| --- | --- |"]
    for path, frontmatter in imported:
        print(f"⏭️ Skipping imported post: {Path(path).name}")
        summary.append(
            f"| `{Path(path).name}` | skipped: imported from "
            f"{imported_from(frontmatter)} |"
        )
    for path, _ in bulk:
        print(f"⏭️ Skipping (bulk run): {Path(path).name}")
        summary.append(f"| `{Path(path).name}` | skipped: bulk run |")

    print(f"📧 Processing {len(to_send)} post(s)...")
    print("")

    results = []
    for path, frontmatter in to_send:
        name = Path(path).name
        print(f"📄 Processing: {name}")

        # 이메일 발송
        result = notify_post(path, frontmatter, api_key, site_url)
        results.append((path, result))

        if result == SENT:
            print(f"✅ Email sent successfully for: {name}")
        elif result == AUTH_REJECTED:
            print(
                "::error::BUTTONDOWN_API_KEY rejected — rotate it in repo secrets "
                "(Settings > Secrets and variables > Actions), then re-run this job."
            )
            # Every later post would be rejected with the same key.
            break
        elif result == TRANSIENT:
            print(
                f"::warning::Buttondown failed temporarily; no newsletter was sent "
                f"for {name}. Run this workflow manually with post_path once it "
                "recovers."
            )
        else:
            print(
                f"::error::Buttondown refused the newsletter for {name}; "
                "see the response above."
            )

        print("")

    labels = {
        SENT: "sent",
        AUTH_REJECTED: "not sent: API key rejected",
        TRANSIENT: "not sent: temporary Buttondown failure",
        FAILED: "not sent: refused by Buttondown",
    }
    for path, result in results:
        summary.append(f"| `{Path(path).name}` | {labels[result]} |")
    for path, _ in to_send[len(results) :]:
        summary.append(
            f"| `{Path(path).name}` | not sent: stopped after the key was rejected |"
        )
    write_step_summary(summary)

    sent = sum(1 for _, result in results if result == SENT)
    transient = sum(1 for _, result in results if result == TRANSIENT)
    failed = len(to_send) - sent - transient

    # 결과 요약
    print("=" * 42)
    print("📊 Email Notification Summary")
    print("=" * 42)
    print(f"✅ Sent: {sent}")
    print(f"⏭️ Skipped: {len(imported) + len(bulk)}")
    print(f"⚠️ Temporary failures: {transient}")
    print(f"❌ Failed: {failed}")
    print(f"📝 Total: {len(valid_posts)}")
    print("=" * 42)

    # A rejected key or a refused request needs a person, so the job goes red.
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
