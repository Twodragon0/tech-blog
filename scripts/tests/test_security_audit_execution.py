"""Exercise security-audit shell gates without network or GitHub API calls."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/security-audit.yml"


@pytest.mark.parametrize("changes", ["failure", "cancelled", "skipped", "success"])
def test_summary_requires_successful_change_detection(
    tmp_path: Path, changes: str
) -> None:
    script = _audit_script("summary", "Evaluate audit results")
    for job, job_result in (
        ("check-changes", changes),
        ("npm-audit", "skipped"),
        ("bundle-audit", "skipped"),
    ):
        script = script.replace("${{ needs." + job + ".result }}", job_result)
    result = subprocess.run(
        ["bash", "-euo", "pipefail", "-c", script],
        cwd=tmp_path,
        env=os.environ
        | {
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
            "NPM_VERDICT": "",
            "BUNDLE_VERDICT": "",
        },
        text=True,
        capture_output=True,
        check=False,
    )
    summary = (tmp_path / "summary").read_text()
    if changes == "success":
        assert result.returncode == 0
        assert "Neither audit ran (no dependency manifest changed)" in summary
    else:
        assert result.returncode != 0
        assert "audit coverage is unknown" in summary
        assert "Neither audit ran (no dependency manifest changed)" not in summary


def _audit_script(job: str, step_name: str) -> str:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps = workflow["jobs"][job]["steps"]
    return next(step["run"] for step in steps if step.get("name") == step_name)


def _run_audit(
    tmp_path: Path, job: str, response: str, exit_code: int
) -> subprocess.CompletedProcess[str]:
    tool = "npm" if job == "npm-audit" else "bundle"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    executable = fake_bin / tool
    executable.write_text(
        "#!/bin/sh\ncat <<'AUDIT_FIXTURE'\n"
        + response
        + "\nAUDIT_FIXTURE\nexit "
        + str(exit_code)
        + "\n",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    output = tmp_path / "output"
    summary = tmp_path / "summary"
    env = os.environ | {
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(summary),
    }
    return subprocess.run(
        [
            "bash",
            "-euo",
            "pipefail",
            "-c",
            _audit_script(
                job, "Run npm audit" if job == "npm-audit" else "Run bundle audit"
            ),
        ],
        env=env,
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )


def _npm_report(high: int = 0, critical: int = 0) -> str:
    return (
        '{"metadata":{"vulnerabilities":{"info":0,"low":0,"moderate":0,'
        f'"high":{high},"critical":{critical}'
        "}}}"
    )


def test_npm_clean_is_clean_verdict(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "npm-audit", _npm_report(), 0)
    assert result.returncode == 0
    assert "vulnerabilities=0" in (tmp_path / "output").read_text()


def test_npm_findings_are_valid_advisory_verdict(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "npm-audit", _npm_report(high=2), 1)
    assert result.returncode == 0
    assert "vulnerabilities=2" in (tmp_path / "output").read_text()


def test_npm_execution_error_has_no_verdict(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "npm-audit", "network unavailable", 7)
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_npm_malformed_json_fails_closed(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "npm-audit", "{not-json", 0)
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_npm_error_payload_fails_closed(tmp_path: Path) -> None:
    report = '{"error":{"code":"ENOAUDIT"},"metadata":{"vulnerabilities":{"high":0,"critical":0}}}'
    result = _run_audit(tmp_path, "npm-audit", report, 0)
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_npm_non_integer_or_negative_counts_fail_closed(tmp_path: Path) -> None:
    for high, critical in ((-1, 1), (0.5, 0)):
        case = tmp_path / f"{high}-{critical}"
        case.mkdir()
        report = (
            '{"metadata":{"vulnerabilities":{"high":'
            + str(high)
            + ',"critical":'
            + str(critical)
            + "}}}"
        )
        result = _run_audit(case, "npm-audit", report, 0)
        assert result.returncode != 0
        assert not (case / "output").exists()


def test_npm_exit_code_must_match_findings(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "npm-audit", _npm_report(high=1), 0)
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_bundle_clean_is_clean_verdict(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "bundle-audit", "No vulnerabilities found", 0)
    assert result.returncode == 0
    assert "vulnerable=false" in (tmp_path / "output").read_text()


def test_bundle_findings_are_valid_advisory_verdict(tmp_path: Path) -> None:
    report = "Name: addressable\nVulnerabilities found!\nSolution: update to >= 2.9.1"
    result = _run_audit(tmp_path, "bundle-audit", report, 1)
    assert result.returncode == 0
    assert "vulnerable=true" in (tmp_path / "output").read_text()


def test_bundle_database_clone_error_has_no_verdict(tmp_path: Path) -> None:
    result = _run_audit(
        tmp_path, "bundle-audit", "fatal: unable to clone advisory db", 1
    )
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_bundle_unknown_output_fails_closed(tmp_path: Path) -> None:
    result = _run_audit(tmp_path, "bundle-audit", "unexpected output", 0)
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_audit_runs_when_workflow_changes() -> None:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    # PyYAML's YAML 1.1 resolver treats the unquoted GitHub Actions key `on` as True.
    events = workflow.get("on", workflow.get(True))
    assert ".github/workflows/security-audit.yml" in events["push"]["paths"]
    # Keep PR runs enabled so skipped summary checks remain visible on all PRs.
    assert events["pull_request"]["branches"] == ["main"]
    assert "paths" not in events["pull_request"]
    for patterns in workflow["jobs"]["check-changes"]["steps"]:
        if patterns.get("id") == "filter":
            filters = yaml.safe_load(patterns["with"]["filters"])
            assert ".github/workflows/security-audit.yml" in filters["should-audit"]
            break
    else:
        raise AssertionError("paths-filter step missing")


def test_issue_reconciliation_is_default_branch_only() -> None:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    expected = (
        "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)"
    )
    for job, step_name in (
        ("npm-audit", "Reconcile npm audit issue"),
        ("bundle-audit", "Reconcile bundle audit issue"),
    ):
        step = next(
            item
            for item in workflow["jobs"][job]["steps"]
            if item.get("name") == step_name
        )
        assert step.get("if") == expected

    default_branch = "main"
    cases = (
        ("refs/heads/main", True),
        ("refs/pull/817/merge", False),
        ("refs/heads/feature/audit", False),
    )
    for ref, may_reconcile in cases:
        actual = ref == f"refs/heads/{default_branch}"
        assert actual is may_reconcile
