#!/usr/bin/env python3
"""Explicit handoff from digest generation to the publish workflow.

The generator chooses the filename from the KST calendar. The workflow used to
look for that file again with its own clock. Those clocks disagree across
00:00-09:00 KST (15:00-24:00 UTC): run 41770313270 wrote
``2026-11-05-...Digest....md`` at 23:11 UTC and the UTC ``date`` scan reported
``No post created for today``, then the job exited 0.

The manifest is the only candidate list. A skip with no new digest stays a
success. A digest that was written but is not the recorded file fails closed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

# Slugs include keyword hyphens such as Zero-Day and Open-Source. Dots stay
# forbidden so the path cannot be ``..`` or a hidden extra extension.
_POST_RE = re.compile(r"^_posts/\d{4}-\d{2}-\d{2}-[A-Za-z0-9_-]+\.md$")
_SVG_RE = re.compile(r"^assets/images/\d{4}-\d{2}-\d{2}-[A-Za-z0-9_-]+\.svg$")


def default_manifest_path() -> Path:
    """Repo-root manifest. Stable so the workflow does not search by date."""
    return Path(__file__).resolve().parent.parent / ".blogwatcher-publish.json"


def kst_publish_date(
    now: datetime | None = None,
    forced: str = "",
) -> tuple[datetime, str]:
    """Return the KST instant and the ``YYYY-MM-DD`` filename date.

    Naive datetimes are read as KST. Aware datetimes are converted to KST, so
    23:11 UTC is the next KST morning. ``forced`` replaces the calendar day and
    keeps the clock, including the hour that decides the midnight redirect.
    """
    current = now if now is not None else datetime.now(KST)
    if current.tzinfo is None:
        current = current.replace(tzinfo=KST)
    else:
        current = current.astimezone(KST)
    if forced:
        forced_day = datetime.strptime(forced, "%Y-%m-%d")
        current = current.replace(
            year=forced_day.year,
            month=forced_day.month,
            day=forced_day.day,
        )
    return current, current.strftime("%Y-%m-%d")


def write_manifest(
    path: Path,
    *,
    status: str,
    reason: str,
    date: str = "",
    post_file: str = "",
    image_file: str = "",
) -> None:
    """Atomically record one publisher outcome. ``status`` is a closed set."""
    if status not in {"created", "skipped", "dry_run"}:
        raise ValueError(f"unknown publish status: {status}")
    payload: dict[str, str] = {
        "calendar": "Asia/Seoul",
        "date": date,
        "image_file": image_file,
        "post_file": post_file,
        "reason": reason,
        "status": status,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


@dataclass(frozen=True)
class ResolveResult:
    """Workflow-facing view of a manifest. ``ok`` is false when detection fails."""

    ok: bool
    post_created: bool = False
    post_file: str = ""
    image_file: str = ""
    publish_date: str = ""
    skip_reason: str = ""
    message: str = ""


def _safe_rel(root: Path, rel: str, pattern: re.Pattern[str]) -> Path:
    if not pattern.fullmatch(rel):
        raise ValueError(f"refusing unexpected publish path: {rel}")
    path = root / rel
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"publish path escapes the repository: {rel}")
    return path


def _dirty_digests(root: Path) -> list[str]:
    """Digest/weekly markdown that git does not already have at HEAD.

    A same-day post that is already committed is clean. A file the publisher
    just wrote is untracked. Guessing from ``date`` is what dropped 2026-11-05.
    """
    proc = subprocess.run(
        # `all` lists files inside a not-yet-tracked _posts directory. The default
        # porcelain collapses that directory to `?? _posts/` and hides the digest.
        [
            "git",
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            "_posts",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(detail or "git status failed; refusing to guess a digest")
    found: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        rel = raw.replace("\\", "/").strip()
        name = Path(rel).name
        if name.endswith(".md") and ("Digest" in name or "Weekly" in name):
            found.append(rel)
    return found


def resolve_manifest(manifest: Path) -> ResolveResult:
    """Accept a recorded skip, or the exact created paths. Never scan a clock."""
    if not manifest.is_file():
        return ResolveResult(
            ok=False,
            message=("no publish manifest; refusing to scan the clock for a digest"),
        )
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ResolveResult(ok=False, message=f"unreadable publish manifest: {exc}")
    if not isinstance(payload, Mapping):
        return ResolveResult(ok=False, message="publish manifest is not an object")

    status = str(payload.get("status") or "")
    reason = str(payload.get("reason") or "")
    date = str(payload.get("date") or "")
    post_file = str(payload.get("post_file") or "")
    image_file = str(payload.get("image_file") or "")
    root = manifest.resolve().parent
    try:
        dirty = _dirty_digests(root)
    except RuntimeError as exc:
        return ResolveResult(ok=False, message=str(exc))

    if status in {"skipped", "dry_run"}:
        if dirty:
            return ResolveResult(
                ok=False,
                message=(
                    "a digest was generated but the manifest says "
                    f"{status}; refusing to report success"
                ),
            )
        return ResolveResult(
            ok=True,
            post_created=False,
            publish_date=date,
            skip_reason=reason or status,
        )
    if status != "created":
        return ResolveResult(
            ok=False,
            message=f"unknown publish manifest status: {status}",
        )

    try:
        post_path = _safe_rel(root, post_file, _POST_RE)
        image_path = _safe_rel(root, image_file, _SVG_RE)
    except ValueError as exc:
        return ResolveResult(ok=False, message=str(exc))
    if date and not post_file.startswith(f"_posts/{date}-"):
        return ResolveResult(
            ok=False,
            message="post filename date does not match the declared KST date",
        )
    if date and not image_file.startswith(f"assets/images/{date}-"):
        return ResolveResult(
            ok=False,
            message="cover filename date does not match the declared KST date",
        )
    if Path(post_file).stem != Path(image_file).stem:
        return ResolveResult(ok=False, message="post and cover stems differ")
    if not post_path.is_file() or not image_path.is_file():
        missing = post_file if not post_path.is_file() else image_file
        return ResolveResult(
            ok=False,
            message=f"generated but not detected: {missing}",
        )
    extras = [item for item in dirty if item != post_file]
    if extras:
        return ResolveResult(
            ok=False,
            message="unrecorded digest changes: " + ", ".join(extras),
        )
    return ResolveResult(
        ok=True,
        post_created=True,
        post_file=post_file,
        image_file=image_file,
        publish_date=date,
        skip_reason="",
    )


def preserve_on_failure(manifest: Path, dest: Path) -> None:
    """Copy a generated-but-uncommitted digest next to the gate-failure draft.

    Best-effort. A missing manifest is the not-written case and is not an error.
    """
    if not manifest.is_file():
        return
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"could not read publish manifest: {exc}", file=sys.stderr)
        return
    if not isinstance(payload, Mapping) or payload.get("status") != "created":
        return
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "blogwatcher-publish.json").write_text(
        manifest.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    root = manifest.resolve().parent
    for key in ("post_file", "image_file"):
        rel = str(payload.get(key) or "")
        parts = rel.split("/")
        if not rel or rel.startswith("/") or ".." in parts:
            continue
        src = root / rel
        if src.is_file():
            target = dest / src.name
            target.write_bytes(src.read_bytes())
            print(f"preserved {rel} -> {target}")


def _write_github_output(path: Path, result: ResolveResult) -> None:
    fields = {
        "post_created": "true" if result.post_created else "false",
        "post_file": result.post_file,
        "image_file": result.image_file,
        "publish_date": result.publish_date,
        "skip_reason": result.skip_reason,
    }
    text = "".join(f"{key}={value}\n" for key, value in fields.items())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI used by ai-blogwatcher.yml. Prints ``::error::`` and exits 1 on a miss."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve", help="emit GitHub outputs or fail closed")
    resolve.add_argument("--manifest", type=Path, required=True)
    resolve.add_argument("--github-output", type=Path, required=True)

    keep = sub.add_parser(
        "preserve-on-failure",
        help="copy a created digest into the diagnostic directory",
    )
    keep.add_argument("--manifest", type=Path, required=True)
    keep.add_argument("--dest", type=Path, required=True)

    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "preserve-on-failure":
        preserve_on_failure(args.manifest, args.dest)
        return 0

    result = resolve_manifest(args.manifest)
    if not result.ok:
        print(f"::error::{result.message}", file=sys.stderr)
        return 1
    _write_github_output(args.github_output, result)
    if result.post_created:
        print(f"Post created: {result.post_file}")
    else:
        print(f"No post created ({result.skip_reason})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
