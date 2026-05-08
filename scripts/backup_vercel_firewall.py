#!/usr/bin/env python3
"""Snapshot the Vercel firewall config to a timestamped JSON file.

Why this exists
---------------
On 2026-05-08 we discovered ``managedRules.bot_protection`` was
silently set to ``action: "challenge"`` — every bot (including
Googlebot) got blocked, GSC indexing dropped to 0. The rule had been
edited via the dashboard and there was no audit trail in the repo.
This script captures the live config weekly so any drift is visible
in `git log docs/backups/vercel-firewall/`.

Usage
-----
    # Local (requires VERCEL_TOKEN env var with team-scope read access)
    VERCEL_TOKEN=xxx VERCEL_TEAM_ID=team_... VERCEL_PROJECT_ID=prj_... \
      python3 scripts/backup_vercel_firewall.py

    # Or with the Vercel CLI auth (vercel login already done)
    python3 scripts/backup_vercel_firewall.py --use-cli

The CI workflow (.github/workflows/vercel-firewall-backup.yml) calls
this with `VERCEL_TOKEN` injected from the repo secret.

Output
------
    docs/backups/vercel-firewall/{YYYY-MM-DD}.json
    docs/backups/vercel-firewall/latest.json   (symlink-style copy)

Each JSON file is a pretty-printed snapshot. Diffing two snapshots
shows exactly which managed rules / IP allowlists / custom rules
changed. Compares well with `git diff docs/backups/...`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = REPO_ROOT / "docs" / "backups" / "vercel-firewall"

# Defaults populated from this repo's actual project. Overridable via env.
DEFAULT_PROJECT_ID = "prj_AONcZXgpIpZ8YXjupW9547FdTJEr"
DEFAULT_TEAM_ID = "team_K7Ut1NIGYRvAfP68LYpOLBcA"


def _fetch_via_token(
    token: str, project_id: str, team_id: str
) -> Dict:
    """Fetch firewall config via the Vercel REST API using a bearer token."""
    url = (
        f"https://api.vercel.com/v1/security/firewall/config/active"
        f"?projectId={project_id}&teamId={team_id}"
    )
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:500]
        except Exception:
            pass
        raise SystemExit(f"Vercel API error {e.code}: {body}") from e


def _fetch_via_cli(project_id: str, team_id: str) -> Dict:
    """Fetch via the local `vercel` CLI (relies on `vercel login`)."""
    cmd = [
        "vercel",
        "api",
        f"/v1/security/firewall/config/active?projectId={project_id}&teamId={team_id}",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if out.returncode != 0:
        raise SystemExit(f"vercel CLI failed: {out.stderr.strip()}")
    # vercel CLI prefixes output with a WARNING line; strip non-JSON head.
    raw = out.stdout
    start = raw.find("{")
    if start < 0:
        raise SystemExit(f"unexpected vercel CLI output:\n{raw[:300]}")
    return json.loads(raw[start:])


def _redact(config: Dict) -> Dict:
    """Strip ephemeral / non-meaningful fields so diffs stay focused.

    Vercel includes ``updatedAt`` timestamps on every rule which would
    create noisy diffs even when nothing functionally changed.
    """
    drop_keys = {"updatedAt", "createdAt", "id", "version"}

    def _walk(node):
        if isinstance(node, dict):
            return {
                k: _walk(v)
                for k, v in node.items()
                if k not in drop_keys
            }
        if isinstance(node, list):
            return [_walk(v) for v in node]
        return node

    return _walk(config)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--use-cli",
        action="store_true",
        help="Use the local `vercel` CLI instead of VERCEL_TOKEN env var.",
    )
    parser.add_argument(
        "--project-id",
        default=os.environ.get("VERCEL_PROJECT_ID", DEFAULT_PROJECT_ID),
    )
    parser.add_argument(
        "--team-id",
        default=os.environ.get("VERCEL_TEAM_ID", DEFAULT_TEAM_ID),
    )
    parser.add_argument(
        "--out-dir",
        default=str(BACKUP_DIR),
        help="Where to write the snapshot.",
    )
    args = parser.parse_args(argv)

    if args.use_cli:
        config = _fetch_via_cli(args.project_id, args.team_id)
    else:
        token = os.environ.get("VERCEL_TOKEN", "").strip()
        if not token:
            print(
                "ERROR: VERCEL_TOKEN not set. Pass --use-cli to use vercel CLI auth.",
                file=sys.stderr,
            )
            return 2
        config = _fetch_via_token(token, args.project_id, args.team_id)

    redacted = _redact(config)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().strftime("%Y-%m-%d")
    dated = out_dir / f"{today}.json"
    latest = out_dir / "latest.json"

    serialized = json.dumps(redacted, indent=2, sort_keys=True, ensure_ascii=False)
    serialized += "\n"
    dated.write_text(serialized, encoding="utf-8")
    latest.write_text(serialized, encoding="utf-8")

    print(f"firewall snapshot → {dated}")
    print(f"firewall latest   → {latest}")

    # Quick health summary.
    rules = redacted.get("managedRules", {})
    print()
    print("=== managedRules summary ===")
    for name, body in sorted(rules.items()):
        print(f"  {name:20} active={body.get('active')!s:5} action={body.get('action')}")
    print(f"\nfirewallEnabled : {redacted.get('firewallEnabled')}")
    print(f"attackModeEnabled: {redacted.get('attackModeEnabled')}")
    print(f"custom rules    : {len(redacted.get('rules', []) or [])}")
    print(f"ip rules        : {len(redacted.get('ips', []) or [])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
