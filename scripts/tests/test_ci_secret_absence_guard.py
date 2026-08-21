#!/usr/bin/env python3
"""CI regression guard: a missing secret must fail where the secret actually exists.

The 2026-08-10 audit flagged seven workflows as "missing secret -> green, zero work".
Measuring `gh secret list` against what each workflow requires splits that group in
two, and the two halves need opposite treatment:

**Secrets that ARE configured** (`SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`) — their absence
at runtime is not an optional-integration case. It means the secret was removed,
rotated without updating, or the job lost access to it. Skipping green there silences
the one regression worth knowing about: notifications quietly stopping. These three
workflows now exit 1, following `sentry-healthcheck.yml`, which already does.

**Secrets that were NEVER configured** — `GSC_SERVICE_ACCOUNT_JSON` for
`gsc-queue-refresh.yml`, and `VERCEL_TOKEN` / `VERCEL_PROJECT_ID` / `VERCEL_TEAM_ID`
for `vercel-firewall-backup.yml`. Verified from live run logs on 2026-08-10:

    gsc-queue-refresh      ::warning::GSC_SERVICE_ACCOUNT_JSON secret is NOT set.
    vercel-firewall-backup ##[warning]VERCEL_TOKEN secret not set; skipping snapshot.

Both report success on every scheduled run while doing nothing — `vercel-firewall-backup`
is the one whose purpose is recording firewall drift. They are deliberately NOT made
fail-closed here: with the secret permanently absent that would produce a permanently
red cron, which is the muted-noise failure mode `digest-translate-backfill.yml` was
just repaired for. Provisioning the secrets or retiring the workflows is a decision for
the repo owner, so this guard pins the current asymmetry and the reason for it instead
of quietly picking one.

Direction: if a secret listed in NEVER_CONFIGURED gets provisioned, that workflow
should move to the fail-closed set and this guard should be updated in the same PR.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# Secrets confirmed present in the repo -> absence is a regression -> fail.
FAIL_CLOSED = (
    "slack-post-notify.yml",
    "slack-category-digest.yml",
    "googlebot-access-monitor.yml",
    # Added 2026-08-21. Until then this workflow alerted through
    # `secrets.SLACK_WEBHOOK`, which has never been configured, behind an
    # `env.HAS_SLACK_WEBHOOK == 'true'` gate — so the channel had never fired
    # once while the job reported success. Switched to the SLACK_BOT_TOKEN /
    # SLACK_CHANNEL_ID pair the three workflows above already use, which makes
    # it eligible for the same fail-closed rule: the step only runs after
    # monitoring has already failed, so a missing secret means an alert about a
    # real outage is being dropped.
    "monitoring.yml",
)

# Secrets never configured -> fail-closed would be a permanently red cron.
NEVER_CONFIGURED = {
    "gsc-queue-refresh.yml": "GSC_SERVICE_ACCOUNT_JSON",
}

# Fail-closed on a NON-Slack secret. Same rule as FAIL_CLOSED above (an absent
# secret is a regression, not an optional integration), but the assertions
# differ: these workflows have no SLACK_BOT_TOKEN / SLACK_CHANNEL_ID pair to
# match, so the guard block is keyed on the workflow's own secret name.
#
# vercel-firewall-backup moved here from NEVER_CONFIGURED when VERCEL_TOKEN was
# provisioned. Its cron came back in the same change, which is what the
# docstring's "Direction" paragraph asks for: the secret and the schedule are
# only correct together.
FAIL_CLOSED_NON_SLACK = {
    "vercel-firewall-backup.yml": "VERCEL_TOKEN",
}


def _uncommented(text: str) -> str:
    """Workflow text minus comment-only lines.

    Each repaired file explains the `exit 0` it replaced and names the never-configured
    counter-examples, so matching raw text would hit the explanation rather than code.
    """
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _body(name: str) -> str:
    return _uncommented((WORKFLOWS / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", FAIL_CLOSED)
def test_missing_slack_secret_fails(name: str):
    body = _body(name)
    assert "SLACK_BOT_TOKEN" in body, f"{name} no longer references SLACK_BOT_TOKEN"
    # Find the guard block and confirm it exits non-zero.
    blocks = re.findall(
        r'if \[ -z "\$\{SLACK_(?:BOT_TOKEN|CHANNEL_ID):-\}" \][^\n]*\n(.*?)\n\s*fi',
        body,
        re.DOTALL,
    )
    assert blocks, f"{name}: no SLACK secret guard block found"
    for block in blocks:
        assert "exit 1" in block, (
            f"{name}: a missing Slack secret still exits 0. Both secrets are configured "
            "in this repo, so a green skip hides notifications silently stopping."
        )
        assert "exit 0" not in block, f"{name}: guard block still contains exit 0"


@pytest.mark.parametrize("name", FAIL_CLOSED)
def test_missing_secret_is_an_error_annotation_not_a_warning(name: str):
    """`::warning::` reads as expected-and-fine; this state is neither."""
    body = _body(name)
    guard_region = body[body.find("SLACK_BOT_TOKEN:-") :][:1200]
    assert "::error::" in guard_region, (
        f"{name}: the missing-secret branch should emit ::error::, not ::warning::"
    )


@pytest.mark.parametrize(("name", "secret"), sorted(FAIL_CLOSED_NON_SLACK.items()))
def test_non_slack_fail_closed_workflows_exit_nonzero(name: str, secret: str):
    """A provisioned secret's absence must fail, whatever the integration is."""
    body = _body(name)
    assert secret in body, f"{name} no longer references {secret}"
    blocks = re.findall(
        rf'if \[ -z "\$\{{?{secret}}}?" \][^\n]*\n(.*?)\n\s*fi',
        body,
        re.DOTALL,
    )
    assert blocks, f"{name}: no {secret} guard block found"
    for block in blocks:
        assert "exit 1" in block, (
            f"{name}: a missing {secret} still exits 0. The secret is configured, "
            f"so a green skip hides the job silently doing nothing — which is the "
            f"state this workflow was retired from cron for."
        )
        assert "exit 0" not in block, f"{name}: guard block still contains exit 0"
        assert "::error::" in block, (
            f"{name}: the missing-secret branch emits no ::error::. A ::warning:: "
            f"reads as expected-and-fine; this state is neither."
        )


@pytest.mark.parametrize("name", sorted(FAIL_CLOSED_NON_SLACK))
def test_non_slack_fail_closed_workflows_are_scheduled(name: str):
    """The inverse of the NEVER_CONFIGURED rule below.

    Fail-closed without a cron is a workflow that can only fail when someone
    remembers to click it. The pairing runs both ways: no secret -> no cron, and
    secret -> cron.
    """
    import yaml

    parsed = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    on = parsed[True] if True in parsed else parsed["on"]
    assert "schedule" in on, (
        f"{name} is fail-closed on a provisioned secret but has no schedule, so "
        f"the snapshot only happens on a manual dispatch. Restore the cron."
    )


@pytest.mark.parametrize(("name", "secret"), sorted(NEVER_CONFIGURED.items()))
def test_never_configured_workflows_stay_soft(name: str, secret: str):
    """Deliberate asymmetry — read the module docstring before "fixing" this.

    These secrets have never existed in the repo. Making the workflow fail would create
    a cron that is red every single run, which trains people to ignore it. The state is
    a provisioning decision, not a code defect.
    """
    body = _body(name)
    assert secret in body, f"{name} no longer references {secret}"
    assert "exit 0" in body, (
        f"{name} now fails when {secret} is absent. That secret has never been "
        "configured, so this would be red on every scheduled run. If it HAS now been "
        "provisioned, move this workflow into FAIL_CLOSED and say so in the PR."
    )


@pytest.mark.parametrize("name", sorted(NEVER_CONFIGURED))
def test_never_configured_workflows_are_not_scheduled(name: str):
    """Retired from cron on 2026-08-10 — restoring it needs the secret, not just a cron.

    Both ran on a schedule and reported success on every run while doing nothing. A
    recurring green tick over zero work is worse than no workflow at all: on the Actions
    tab, and in any audit of "what protects this repo", it reads as a job that runs.
    `vercel-firewall-backup` is the sharp case — it exists so an unauthorized Vercel
    dashboard edit shows up as a committed diff, and its weekly success had never
    produced one.

    `workflow_dispatch` is kept, so provisioning the secret makes the first real run one
    click away. Re-adding the cron is only correct in the same change that provisions
    the secret; this assertion is what forces that pairing to be deliberate.
    """
    import yaml

    parsed = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    triggers = parsed[True] if True in parsed else parsed["on"]
    assert "schedule" not in triggers, (
        f"{name} is on a schedule again. Its secret "
        f"({NEVER_CONFIGURED[name]}) must be provisioned in the SAME change, otherwise "
        "every run is a green tick over zero work. If it was provisioned, move this "
        "workflow to FAIL_CLOSED and drop it from NEVER_CONFIGURED here."
    )
    assert "workflow_dispatch" in triggers, (
        f"{name} lost workflow_dispatch; there would be no way to run it once the "
        "secret exists."
    )


def test_sentry_healthcheck_remains_the_reference_implementation():
    """The audit cited this as the counter-example done right; keep it that way."""
    body = _body("sentry-healthcheck.yml")
    assert "exit 1" in body, (
        "sentry-healthcheck.yml no longer fails on missing secrets. It is the pattern "
        "the three Slack workflows were aligned to; if it changed, revisit them too."
    )


def test_the_two_groups_do_not_overlap():
    """Canary against a copy-paste that puts a workflow in both lists."""
    assert not set(FAIL_CLOSED) & set(NEVER_CONFIGURED)


# Social secrets for sns-share.yml, retired 2026-08-11. All eight were unconfigured,
# so every push spent ~3 minutes installing scripts/requirements.txt (TTS -> torch/CUDA)
# and then reported success having shared to nothing. X/Twitter API v2 posting needs a
# paid tier and Facebook/LinkedIn need app review, which conflicts with the free-tier-
# first rule in CLAUDE.md. scripts/share_sns.py stays for manual use.
RETIRED_SOCIAL_SECRETS = (
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_SECRET",
    "FACEBOOK_PAGE_ID",
    "FACEBOOK_ACCESS_TOKEN",
    "LINKEDIN_ACCESS_TOKEN",
    "LINKEDIN_PERSON_ID",
)


@pytest.mark.parametrize("secret", RETIRED_SOCIAL_SECRETS)
def test_retired_social_secrets_are_not_referenced_by_any_workflow(secret: str):
    """Re-adding SNS automation must come with the credentials, not before them.

    The same pairing this file enforces for the retired crons: a workflow that reads a
    secret nobody has produces a green tick over zero work. If these are provisioned,
    re-add the workflow and drop the secret from RETIRED_SOCIAL_SECRETS in that PR.
    """
    referencing = sorted(
        path.name
        for path in WORKFLOWS.glob("*.yml")
        if secret in path.read_text(encoding="utf-8")
    )
    assert not referencing, (
        f"{referencing} reference {secret}, which is not configured in this repo. Either "
        "provision it in the same change, or drop the reference — otherwise the workflow "
        "runs, costs runner time, and reports success while doing nothing."
    )


def test_share_sns_script_is_kept_for_manual_use():
    """Retiring the workflow should not delete the capability."""
    script = REPO_ROOT / "scripts" / "share_sns.py"
    assert script.is_file(), (
        "scripts/share_sns.py is gone. The sns-share workflow was retired, not the "
        "ability to share manually — deleting the script makes the retirement "
        "irreversible without rewriting it."
    )
