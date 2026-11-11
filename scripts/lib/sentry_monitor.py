"""Read-only Sentry access shared by the monitoring entry points."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

API_ROOT = "https://sentry.io/api/0"
MODE_ENV = "SENTRY_MONITOR_MODE"
TOTAL_TIMEOUT = 25
PAGE_LIMIT = 100
MAX_PAGES = 3


class SentryMonitorError(ValueError):
    """An access, configuration, or response error safe to report publicly."""

    def __init__(self, message: str, *, http_status: int | None = None) -> None:
        super().__init__(message)
        self.http_status = http_status


@dataclass(frozen=True)
class SentryConfig:
    org: str
    project: str
    token: str = field(repr=False)


@dataclass(frozen=True)
class IssuePages:
    issues: list[dict[str, Any]]
    complete: bool


def monitor_mode() -> str:
    mode = os.getenv(MODE_ENV) or "shared"
    if mode not in {"shared", "dedicated"}:
        raise SentryMonitorError("Invalid SENTRY_MONITOR_MODE")
    return mode


def load_config() -> SentryConfig:
    token_name = (
        "SENTRY_MONITOR_AUTH_TOKEN"
        if monitor_mode() == "dedicated"
        else "SENTRY_AUTH_TOKEN"
    )
    token = os.getenv(token_name)
    if not token or not token.strip() or "\r" in token or "\n" in token:
        raise SentryMonitorError(f"Missing or invalid {token_name}")
    org = os.getenv("SENTRY_ORG", "")
    project = os.getenv("SENTRY_PROJECT", "")
    for name, value in (("SENTRY_ORG", org), ("SENTRY_PROJECT", project)):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value):
            raise SentryMonitorError(f"Missing or invalid {name}")
    return SentryConfig(org, project, token)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        # The Authorization header is valid only for the configured Sentry host.
        return None


_open = urllib.request.build_opener(NoRedirect()).open


def _read_json(
    url: str, config: SentryConfig, deadline: float, endpoint: str
) -> tuple[Any, str]:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise SentryMonitorError(f"Sentry {endpoint} API deadline exceeded")
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {config.token}",
            "Accept": "application/json",
        },
    )
    try:
        with _open(request, timeout=remaining) as response:
            if response.status != 200:
                raise SentryMonitorError(
                    f"Sentry {endpoint} API returned HTTP {response.status}",
                    http_status=response.status,
                )
            return json.loads(response.read()), response.headers.get("Link", "")
    except urllib.error.HTTPError as error:
        raise SentryMonitorError(
            f"Sentry {endpoint} API returned HTTP {error.code}", http_status=error.code
        ) from None
    except SentryMonitorError:
        raise
    except (http.client.HTTPException, OSError, ValueError):
        raise SentryMonitorError(
            f"Sentry {endpoint} API request or JSON decoding failed"
        ) from None


def _next_cursor(link: str) -> str | None:
    if not link:
        return None
    next_links = [
        part for part in link.split(",") if re.search(r';\s*rel="next"', part)
    ]
    if len(next_links) != 1:
        raise SentryMonitorError(
            "Sentry issues API returned invalid pagination metadata"
        )
    part = next_links[0]
    result = re.findall(r';\s*results="(true|false)"', part)
    if result == ["false"]:
        return None
    cursor_attr = re.findall(r';\s*cursor="([^"]*)"', part)
    if not cursor_attr:
        href = re.search(r"<([^>]+)>", part)
        if href:
            try:
                cursor_attr = urllib.parse.parse_qs(
                    urllib.parse.urlsplit(href.group(1)).query
                ).get("cursor", [])
            except ValueError:
                cursor_attr = []
    if (
        result != ["true"]
        or len(cursor_attr) != 1
        or not re.fullmatch(r"[A-Za-z0-9:_-]{1,256}", cursor_attr[0])
    ):
        raise SentryMonitorError(
            "Sentry issues API returned invalid pagination metadata"
        )
    return cursor_attr[0]


def read_issues(
    config: SentryConfig,
    *,
    query: str = "is:unresolved",
    period: str | None = None,
    limit: int = PAGE_LIMIT,
    max_pages: int = MAX_PAGES,
) -> IssuePages:
    """Return rows and coverage after a bounded sequence of same-target requests."""
    deadline = time.monotonic() + TOTAL_TIMEOUT
    endpoint = f"{API_ROOT}/organizations/{config.org}/issues/"
    params: dict[str, str | int] = {
        "project": config.project,
        "query": query,
        "limit": limit,
    }
    if period:
        params["statsPeriod"] = period
    issues: list[dict[str, Any]] = []
    cursors: set[str] = set()
    for _ in range(max_pages):
        url = f"{endpoint}?{urllib.parse.urlencode(params)}"
        payload, link = _read_json(url, config, deadline, "issues")
        if not isinstance(payload, list) or not all(
            isinstance(row, dict) for row in payload
        ):
            raise SentryMonitorError("Sentry issues API returned an invalid issue list")
        issues.extend(payload)
        cursor = _next_cursor(link)
        if cursor is None:
            return IssuePages(issues, bool(link) or len(payload) < limit)
        if cursor in cursors:
            raise SentryMonitorError("Sentry issues API repeated a pagination cursor")
        cursors.add(cursor)
        params["cursor"] = cursor
    return IssuePages(issues, False)


def _healthcheck(config: SentryConfig) -> None:
    deadline = time.monotonic() + TOTAL_TIMEOUT
    url = f"{API_ROOT}/projects/{config.org}/{config.project}/"
    project, _ = _read_json(url, config, deadline, "project")
    if not isinstance(project, dict):
        raise SentryMonitorError("Sentry project API returned an invalid object")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("token_ok=true\n")
        try:
            page = read_issues(config, limit=1, max_pages=1)
        except SentryMonitorError:
            output.write("issues_ok=false\nunresolved_count=unknown\n")
            raise
        output.write(f"issues_ok=true\nunresolved_count={len(page.issues)}\n")
    print("Sentry project and issues APIs are accessible")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=("health", "issues"))
    check = parser.parse_args().check
    try:
        config = load_config()
        if check == "health":
            _healthcheck(config)
        else:
            page = read_issues(config)
            if not page.complete:
                raise SentryMonitorError(
                    f"Sentry issues observation is partial ({len(page.issues)} issues observed)"
                )
            print(f"Unresolved Sentry issues: {len(page.issues)}")
    except SentryMonitorError as error:
        print(f"::error::{error}; no complete Sentry measurement")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
