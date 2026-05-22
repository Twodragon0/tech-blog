# Scheduling the GSC indexing-recovery checkpoint

`scripts/gsc_checkpoint.py` is a single-shot tool: it runs
`gsc_inspect.py` (live GSC URL-Inspection API call) and writes a dated
markdown checkpoint under `.omc/research/`. The intended cadence is
weekly — one run per follow-up date (e.g., 2026-05-29 for the 7-day
recheck after the 2026-05-22 patch stack).

This doc lists three concrete ways to schedule it. **Pick one** —
running the script twice on the same day is idempotent (file is
overwritten), but two schedulers competing on the same hour wastes GSC
quota.

## Prerequisites (all options)

```bash
# 1. Service account JSON for GSC URL Inspection (PR-1 setup; see
#    docs/seo/GSC_RECRAWL_SETUP.md). Either path or raw JSON.
export GSC_SERVICE_ACCOUNT_JSON=/secure/path/sa.json

# 2. Verify a manual run works before automating
cd ~/Desktop/personal/tech-blog
python3 scripts/gsc_checkpoint.py \
    --checkpoint-date 2026-05-29 \
    --baseline-date 2026-05-22 \
    --baseline-crawled 109 \
    --baseline-discovered 162
```

If the manual run fails, fix the auth/network issue before scheduling —
none of the options below will surface errors interactively.

---

## Option A — `.twodragon0` central scheduler (workspace convention)

The `~/Desktop/personal/CLAUDE.md` workspace policy routes recurring
work through `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}`. If that
directory exists on the machine, drop the runner into
`bin/`:

```bash
TWODRAGON0_HOME="${TWODRAGON0_HOME:-$HOME/Desktop/.twodragon0}"

# Idempotent runner — wraps gsc_checkpoint.py with the env loaded.
cat > "$TWODRAGON0_HOME/bin/gsc-weekly-checkpoint.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export GSC_SERVICE_ACCOUNT_JSON="${GSC_SERVICE_ACCOUNT_JSON:-$HOME/.config/twodragon/gsc-sa.json}"
cd "$HOME/Desktop/personal/tech-blog"
python3 scripts/gsc_checkpoint.py \
    --checkpoint-date "$(date -u +%Y-%m-%d)" \
    --baseline-date "${GSC_BASELINE_DATE:-2026-05-22}" \
    --baseline-crawled "${GSC_BASELINE_CRAWLED:-109}" \
    --baseline-discovered "${GSC_BASELINE_DISCOVERED:-162}"
EOF
chmod +x "$TWODRAGON0_HOME/bin/gsc-weekly-checkpoint.sh"
```

Then add the entry to the central cron registration script — see the
workspace's `setup-openclaw-cron.sh` for the existing pattern.

> ⚠️ **As of 2026-05-22 this machine does NOT have `~/Desktop/.twodragon0`
> set up.** Use option B or C until the central scheduler is bootstrapped.

---

## Option B — macOS user LaunchAgent (recommended on this machine)

Persists across reboots and runs even when no terminal is open. Drop
the template at `~/Library/LaunchAgents/com.twodragon.gsc-checkpoint.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.twodragon.gsc-checkpoint</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>cd /Users/yong/Desktop/personal/tech-blog &amp;&amp; /usr/bin/env python3 scripts/gsc_checkpoint.py --checkpoint-date "$(date -u +%Y-%m-%d)" --baseline-date 2026-05-22 --baseline-crawled 109 --baseline-discovered 162 &gt;&gt; /tmp/gsc-checkpoint.log 2&gt;&amp;1</string>
  </array>

  <!-- Run once at 09:00 KST every Friday (=00:00 UTC Friday). 2026-05-29
       is a Friday; subsequent Fridays produce weekly checkpoints. -->
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>5</integer>
    <key>Hour</key><integer>0</integer>
    <key>Minute</key><integer>0</integer>
  </dict>

  <key>EnvironmentVariables</key>
  <dict>
    <key>GSC_SERVICE_ACCOUNT_JSON</key>
    <string>/Users/yong/.config/twodragon/gsc-sa.json</string>
  </dict>

  <key>StandardOutPath</key>
  <string>/tmp/gsc-checkpoint.out</string>
  <key>StandardErrorPath</key>
  <string>/tmp/gsc-checkpoint.err</string>
</dict>
</plist>
```

Load it (one-time):

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.twodragon.gsc-checkpoint.plist
launchctl print gui/$(id -u)/com.twodragon.gsc-checkpoint | head -20   # verify
```

Unload (if you stop using it):

```bash
launchctl bootout gui/$(id -u)/com.twodragon.gsc-checkpoint
```

---

## Option C — One-shot manual run on 2026-05-29

If you don't want any scheduler, just put a reminder for 2026-05-29:

```bash
cd ~/Desktop/personal/tech-blog
GSC_SERVICE_ACCOUNT_JSON=/secure/path/sa.json \
python3 scripts/gsc_checkpoint.py \
    --checkpoint-date 2026-05-29 \
    --baseline-date 2026-05-22 \
    --baseline-crawled 109 \
    --baseline-discovered 162
```

Output lands at `.omc/research/checkpoint_gsc_2026_05_29.md`.

---

## Updating the baseline

When a future SEO patch makes the current `--baseline-*` values stale,
either:

1. Edit the runner script (option A or B) to point at the new baseline date/numbers, or
2. Pass new values to option C on the next run.

Baseline = the `Crawled/Discovered not indexed` totals from GSC at the
**moment the patch was deployed**, not the previous checkpoint.
