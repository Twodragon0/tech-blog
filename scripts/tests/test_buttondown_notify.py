"""Newsletter sender: live post URLs, bulk/imported guards, visible failures.

Three defects, all found in buttondown-notify.yml run logs (2026-10-27,
2026-11-06, 2026-11-20):

1. The email link was ``/posts/YYYY/MM/<slug>/``: no day, so every link 404ed.
2. Buttondown answered 401 on every run, and the job stayed green because the
   step had ``continue-on-error`` and ``|| echo "non-critical"``.
3. One push tried to mail 36 imported WordPress posts at once.

No test here touches the network. ``_no_real_buttondown`` makes any unfaked
``requests`` call fail the test; ``buttondown`` installs a scripted fake.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import buttondown_notify
import buttondown_notify_batch as batch
import pytest
import requests

SITE = "https://2twodragon.com"


def _write_post(
    directory: Path, name: str, date: str = "2026-11-19 10:00:00 +0900", **extra: str
) -> Path:
    lines = ["---", 'title: "테스트 포스트"', f"date: {date}", "categories: [security]"]
    lines += [f"{key}: {value}" for key, value in extra.items()]
    lines += ["---", "", "## 개요", "", "본문입니다."]
    path = directory / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# A real requests.Response, so .json() and .text behave as in production.
def _response(
    status: int, body: "str | None" = None, headers: "dict | None" = None
) -> requests.Response:
    if body is None:
        body = '{"id": "em_test"}' if status < 300 else '{"detail": "nope"}'
    response = requests.Response()
    response.status_code = status
    response._content = body.encode("utf-8")
    response.encoding = "utf-8"
    response.headers.update(headers or {})
    return response


class _FakeButtondown:
    """Stands in for requests.post; gives each call the next scripted outcome.

    An outcome is a status code, a prepared response, or an exception (class
    or instance) to raise. A call beyond the script raises IndexError.
    """

    def __init__(self, *outcomes: object) -> None:
        self.outcomes = list(outcomes)
        self.bodies: list = []
        self.headers: list = []

    def __call__(self, url: str, json: dict, headers: dict, timeout: int):
        self.bodies.append(json["body"])
        self.headers.append(headers)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException) or (
            isinstance(outcome, type) and issubclass(outcome, BaseException)
        ):
            raise outcome
        if isinstance(outcome, requests.Response):
            return outcome
        assert isinstance(outcome, int)
        return _response(outcome)


@pytest.fixture(autouse=True)
def _no_real_buttondown(monkeypatch: pytest.MonkeyPatch) -> None:
    """A test that forgets the fake must fail, not mail the real list.

    requests.post/get/request and every Session end in Session.request.
    conftest.py also blocks sockets to other hosts underneath it.
    """

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("test reached requests without the Buttondown fake")

    monkeypatch.setattr(requests.sessions.Session, "request", refuse)


@pytest.fixture(autouse=True)
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list:
    """The waits before a retry, recorded instead of slept through."""
    waits: list = []
    monkeypatch.setattr(buttondown_notify.time, "sleep", waits.append)
    return waits


@pytest.fixture
def buttondown(monkeypatch: pytest.MonkeyPatch):
    def install(*outcomes: object) -> _FakeButtondown:
        fake = _FakeButtondown(*outcomes)
        monkeypatch.setattr(requests, "post", fake)
        return fake

    return install


def test_a_send_without_the_fake_fails_instead_of_mailing() -> None:
    with pytest.raises(AssertionError, match="without the Buttondown fake"):
        buttondown_notify.send_buttondown_email("s", "b", "key")


# ---------------------------------------------------------------------------
# 1. The link in the email is the live URL
# ---------------------------------------------------------------------------


def test_post_url_carries_the_day(tmp_path: Path) -> None:
    post = _write_post(tmp_path, "2026-11-19-Tech_Digest.md")
    assert buttondown_notify.generate_post_url(str(post), SITE) == (
        f"{SITE}/posts/2026/11/19/Tech_Digest/"
    )


def test_post_url_of_a_kst_morning_post_is_the_previous_utc_day(
    tmp_path: Path,
) -> None:
    post = _write_post(
        tmp_path, "2026-11-19-Morning_Digest.md", date="2026-11-19 08:30:00 +0900"
    )
    assert buttondown_notify.generate_post_url(str(post), SITE) == (
        f"{SITE}/posts/2026/11/18/Morning_Digest/"
    )


def test_email_body_links_to_the_live_url(tmp_path: Path, buttondown) -> None:
    fake = buttondown(201)
    post = _write_post(tmp_path, "2026-11-19-Tech_Digest.md")
    status = buttondown_notify.notify_post(str(post), {"title": "T"}, "key", SITE)
    assert status == buttondown_notify.SENT
    assert f"]({SITE}/posts/2026/11/19/Tech_Digest/)" in fake.bodies[0]


# ---------------------------------------------------------------------------
# 2. Every API outcome is classified
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "outcomes, expected",
    [
        ((200,), buttondown_notify.SENT),
        ((201,), buttondown_notify.SENT),
        ((202,), buttondown_notify.SENT),
        ((204,), buttondown_notify.SENT),
        ((401,), buttondown_notify.AUTH_REJECTED),
        ((403,), buttondown_notify.AUTH_REJECTED),
        ((429, 429), buttondown_notify.TRANSIENT),
        ((429, 201), buttondown_notify.SENT),
        ((500,), buttondown_notify.TRANSIENT),
        ((503,), buttondown_notify.TRANSIENT),
        ((requests.exceptions.Timeout,), buttondown_notify.TRANSIENT),
        ((requests.exceptions.ConnectionError,), buttondown_notify.TRANSIENT),
        ((400,), buttondown_notify.FAILED),
        ((422,), buttondown_notify.FAILED),
        ((requests.exceptions.RequestException,), buttondown_notify.FAILED),
    ],
)
def test_send_classifies_the_outcome(buttondown, outcomes, expected: str) -> None:
    fake = buttondown(*outcomes)
    assert buttondown_notify.send_buttondown_email("s", "b", "key") == expected
    assert fake.outcomes == [], "a scripted answer was never asked for"


@pytest.mark.parametrize(
    "outcome",
    [500, 503, requests.exceptions.Timeout, requests.exceptions.ConnectionError],
)
def test_only_a_429_is_retried(buttondown, sleeps: list, outcome) -> None:
    """A 5xx or a timeout can come after Buttondown created the email, so a
    retry could mail every subscriber twice. The fake has one answer only."""
    fake = buttondown(outcome)
    assert buttondown_notify.send_buttondown_email("s", "b", "key") == (
        buttondown_notify.TRANSIENT
    )
    assert (len(fake.bodies), sleeps) == (1, [])


@pytest.mark.parametrize(
    "retry_after, wait",
    [
        ("7", 7),
        ("3600", 60),
        (None, 10),
        ("Wed, 21 Oct 2026 07:28:00 GMT", 10),
        ("²", 10),
    ],
)
def test_a_429_is_retried_once_after_its_retry_after(
    buttondown, sleeps: list, retry_after: "str | None", wait: int
) -> None:
    headers = {"Retry-After": retry_after} if retry_after else {}
    fake = buttondown(_response(429, headers=headers), 201)
    assert buttondown_notify.send_buttondown_email("s", "b", "key") == (
        buttondown_notify.SENT
    )
    assert (len(fake.bodies), sleeps) == (2, [wait])


@pytest.mark.parametrize("status, body", [(201, "not json"), (200, "[]"), (204, "")])
def test_any_2xx_is_sent_whatever_the_body(buttondown, status: int, body: str) -> None:
    """The email exists once Buttondown answers 2xx; an odd body changes nothing.

    requests' JSONDecodeError is a RequestException, so it used to land in the
    FAILED branch after the email had been created.
    """
    buttondown(_response(status, body))
    assert buttondown_notify.send_buttondown_email("s", "b", "key") == (
        buttondown_notify.SENT
    )


KEY = "b7f1c2d4-1111-2222-3333-444455556666"  # Buttondown keys are UUIDs


@pytest.mark.parametrize(
    "status, reason",
    [(401, "key rejected"), (403, "key rejected or missing permission")],
)
def test_auth_failure_prints_the_response_masked_and_truncated(
    buttondown, capsys, monkeypatch: pytest.MonkeyPatch, status: int, reason: str
) -> None:
    monkeypatch.setenv("BUTTONDOWN_API_KEY", KEY)
    buttondown(_response(status, f'{{"detail": "token {KEY} refused"}}' + " pad" * 200))
    assert buttondown_notify.send_buttondown_email("s", "b", KEY) == (
        buttondown_notify.AUTH_REJECTED
    )
    out = capsys.readouterr().out
    assert f"Auth failed ({status}): {reason}." in out
    assert '{"detail": "token ***BUTTONDOWN_API_KEY_MASKED*** refused"}' in out
    assert KEY not in out
    assert 0 < out.count(" pad") < 200


def test_the_api_key_is_stripped_before_use(buttondown) -> None:
    """A trailing newline in the secret made the header invalid."""
    fake = buttondown(201)
    buttondown_notify.send_buttondown_email("s", "b", f"  {KEY}\n")
    assert fake.headers[0]["Authorization"] == f"Token {KEY}"


@pytest.mark.parametrize(
    "error, expected",
    [
        (requests.exceptions.InvalidHeader, buttondown_notify.FAILED),
        (requests.exceptions.ConnectionError, buttondown_notify.TRANSIENT),
    ],
)
def test_request_errors_are_printed_masked(
    buttondown, capsys, monkeypatch: pytest.MonkeyPatch, error, expected: str
) -> None:
    """requests' InvalidHeader message quotes the header value: the token."""
    monkeypatch.setenv("BUTTONDOWN_API_KEY", KEY)
    buttondown(error(f"Invalid header value: 'Token {KEY}\\n'"))
    assert buttondown_notify.send_buttondown_email("s", "b", KEY) == expected
    out = capsys.readouterr().out
    assert "Invalid header value" in out
    assert KEY not in out


def test_single_post_cli_exits_nonzero_unless_sent(
    tmp_path: Path, buttondown, monkeypatch: pytest.MonkeyPatch
) -> None:
    buttondown(503)
    post = _write_post(tmp_path, "2026-11-19-Tech_Digest.md")
    monkeypatch.setenv("BUTTONDOWN_API_KEY", "key")
    monkeypatch.setattr(sys, "argv", ["buttondown_notify.py", str(post)])
    with pytest.raises(SystemExit) as exc:
        buttondown_notify.main()
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# 3. Guards: imported content and bulk runs are not mailed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [(None, 3), ("", 3), ("5", 5), (" 1 ", 1), ("0", 3), ("-2", 3), ("many", 3)],
)
def test_max_posts_per_run(raw: "str | None", expected: int) -> None:
    assert batch.max_posts_per_run(raw) == expected


@pytest.mark.parametrize(
    "original_url, imported",
    [
        ("https://2twodragon.com/pod-restart-temp-auth-iam-role/", True),
        ("https://www.2twodragon.com/some-post/", True),
        ("http://2TwoDragon.com/x/", True),
        ("https://twodragon.tistory.com/700", False),
        ("https://not2twodragon.com/x/", False),
        ("", False),
        (None, False),
    ],
)
def test_imported_from(original_url: "str | None", imported: bool) -> None:
    assert bool(batch.imported_from({"original_url": original_url})) is imported
    assert batch.imported_from({}) == ""


def _posts(count: int, **frontmatter: str) -> list:
    return [
        (f"_posts/2026-11-{10 + i:02d}-Post_{i}.md", dict(frontmatter))
        for i in range(count)
    ]


def test_select_posts_sends_up_to_the_limit() -> None:
    to_send, imported, bulk = batch.select_posts(_posts(3), max_posts=3)
    assert (len(to_send), imported, bulk) == (3, [], [])


def test_select_posts_holds_back_a_bulk_run_entirely() -> None:
    to_send, imported, bulk = batch.select_posts(_posts(4), max_posts=3)
    assert (to_send, imported, len(bulk)) == ([], [], 4)


def test_select_posts_drops_imported_posts_before_counting() -> None:
    wordpress = _posts(36, original_url="https://2twodragon.com/old-slug/")
    to_send, imported, bulk = batch.select_posts(wordpress + _posts(1), max_posts=3)
    assert (len(to_send), len(imported), bulk) == (1, 36, [])


# ---------------------------------------------------------------------------
# 4. The batch run: exit status, annotations, step summary
# ---------------------------------------------------------------------------


@pytest.fixture
def repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A stand-in repository root, with an empty _posts/."""
    root = tmp_path / "repo"
    (root / "_posts").mkdir(parents=True)
    monkeypatch.setattr(batch, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def posts_dir(repo_root: Path) -> Path:
    return repo_root / "_posts"


@pytest.fixture
def run_batch(tmp_path: Path, repo_root: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    summary = tmp_path / "step_summary.md"
    monkeypatch.setenv("BUTTONDOWN_API_KEY", "key")
    monkeypatch.setenv("SITE_URL", SITE)
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.delenv("BUTTONDOWN_MAX_POSTS", raising=False)
    monkeypatch.delenv("POSTS_JSON", raising=False)

    def run(*posts: Path) -> tuple:
        code = 0
        try:
            batch.main([str(p) for p in posts])
        except SystemExit as exc:
            code = exc.code
        text = summary.read_text(encoding="utf-8") if summary.exists() else ""
        return code, capsys.readouterr().out, text

    return run


def test_batch_sends_new_posts(posts_dir: Path, buttondown, run_batch) -> None:
    fake = buttondown(201, 201)
    posts = [_write_post(posts_dir, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, summary = run_batch(*posts)
    assert code == 0
    assert len(fake.bodies) == 2
    assert "::error::" not in out and "::warning::" not in out
    assert "| `2026-11-18-Post_8.md` | sent |" in summary


def test_batch_rejected_key_fails_the_job_and_stops(
    posts_dir: Path, buttondown, run_batch
) -> None:
    fake = buttondown(401)
    posts = [_write_post(posts_dir, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, summary = run_batch(*posts)
    assert code == 1
    assert "::error::BUTTONDOWN_API_KEY rejected — rotate it in repo secrets" in out
    assert "Don't use Re-run jobs" in out
    assert len(fake.bodies) == 1, "kept sending with a key Buttondown rejected"
    assert "stopped after the key was rejected" in summary


def test_batch_transient_failure_fails_the_job_and_names_the_post_to_resend(
    posts_dir: Path, buttondown, run_batch
) -> None:
    """The workflow is isolated: a red run is the only notice anyone gets."""
    fake = buttondown(201, 503)
    posts = [_write_post(posts_dir, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, summary = run_batch(*posts)
    assert code == 1
    assert len(fake.bodies) == 2
    assert (
        "::error::Buttondown did not confirm the newsletter for 2026-11-19-Post_9.md"
        in out
    )
    assert "post_path=_posts/2026-11-19-Post_9.md" in out
    assert "post_path=_posts/2026-11-18-Post_8.md" not in out
    assert "Don't use Re-run jobs" in out
    assert "| `2026-11-18-Post_8.md` | sent |" in summary
    assert "| `2026-11-19-Post_9.md` | not confirmed: temporary Buttondown" in summary
    assert "Don't use Re-run jobs" in summary


def test_batch_rate_limited_once_then_sent_passes(
    posts_dir: Path, buttondown, run_batch, sleeps: list
) -> None:
    buttondown(429, 201)
    code, out, summary = run_batch(_write_post(posts_dir, "2026-11-19-Post.md"))
    assert (code, sleeps) == (0, [10])
    assert "::error::" not in out
    assert "| `2026-11-19-Post.md` | sent |" in summary


def test_batch_refused_request_fails_the_job(
    posts_dir: Path, buttondown, run_batch
) -> None:
    buttondown(400, 201)
    posts = [_write_post(posts_dir, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, _ = run_batch(*posts)
    assert code == 1
    assert "::error::Buttondown refused the newsletter for 2026-11-18-Post_8.md" in out
    assert "post_path=_posts/2026-11-18-Post_8.md" in out


def test_batch_bulk_run_sends_nothing(posts_dir: Path, buttondown, run_batch) -> None:
    fake = buttondown()
    posts = [_write_post(posts_dir, f"2026-11-1{i}-Post_{i}.md") for i in range(4)]
    code, out, summary = run_batch(*posts)
    assert code == 0
    assert fake.bodies == []
    assert (
        "::warning::4 new posts in one run is more than BUTTONDOWN_MAX_POSTS=3" in out
    )
    assert summary.count("skipped: bulk run") == 4


def test_batch_limit_is_configurable(
    posts_dir: Path, buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("BUTTONDOWN_MAX_POSTS", "1")
    fake = buttondown()
    posts = [_write_post(posts_dir, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, _ = run_batch(*posts)
    assert (code, fake.bodies) == (0, [])
    assert "BUTTONDOWN_MAX_POSTS=1" in out


def test_batch_skips_imported_posts(posts_dir: Path, buttondown, run_batch) -> None:
    fake = buttondown(201)
    imported = _write_post(
        posts_dir,
        "2024-09-01-EKS_Pod_Restart.md",
        date="2024-09-01 20:36:28 +0900",
        original_url="https://2twodragon.com/pod-restart-temp-auth-iam-role/",
    )
    new = _write_post(posts_dir, "2026-11-19-New_Post.md")
    code, out, summary = run_batch(imported, new)
    assert code == 0
    assert len(fake.bodies) == 1 and "New_Post" in fake.bodies[0]
    assert "::warning::Skipped 1 imported post(s)" in out
    assert "skipped: imported from https://2twodragon.com/pod-restart" in summary


def test_batch_with_only_drafts_is_not_a_failure(
    posts_dir: Path, buttondown, run_batch
) -> None:
    fake = buttondown()
    draft = _write_post(posts_dir, "2026-11-19-Draft.md", draft="true")
    code, _, _ = run_batch(draft)
    assert (code, fake.bodies) == (0, [])


def test_batch_unknown_explicit_post_fails(posts_dir: Path, run_batch) -> None:
    code, out, _ = run_batch(posts_dir / "2026-11-19-Missing.md")
    assert code == 1
    assert "::error::Post file not found" in out


def test_batch_without_api_key_fails(
    posts_dir: Path, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("BUTTONDOWN_API_KEY")
    code, out, _ = run_batch(_write_post(posts_dir, "2026-11-19-Post.md"))
    assert code == 1
    assert "::error::BUTTONDOWN_API_KEY" in out


# ---------------------------------------------------------------------------
# 5. A push run mails exactly the posts the workflow's check step found
# ---------------------------------------------------------------------------


def _posts_json(*paths: str) -> str:
    """POSTS_JSON as the check step writes it: base64 paths in a JSON array."""
    return json.dumps([base64.b64encode(p.encode()).decode() for p in paths])


def test_batch_mails_every_post_the_check_step_found(
    repo_root: Path, buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    names = ["2026-11-19-First.md", "2026-11-20-보안_점검.md"]
    for name in names:
        _write_post(repo_root / "_posts", name)
    monkeypatch.setenv("POSTS_JSON", _posts_json(*(f"_posts/{n}" for n in names)))
    fake = buttondown(201, 201)
    code, _, summary = run_batch()
    assert code == 0
    assert len(fake.bodies) == 2
    assert "| `2026-11-20-보안_점검.md` | sent |" in summary


def test_batch_does_not_diff_again_when_the_check_step_found_nothing(
    buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POSTS_JSON", "[]")
    monkeypatch.setattr(
        batch, "detect_posts_via_git_diff", lambda: pytest.fail("diffed again")
    )
    fake = buttondown()
    code, _, _ = run_batch()
    assert (code, fake.bodies) == (0, [])


@pytest.mark.parametrize(
    "posts_json", ["", "not json", '{"a": 1}', "[1]", '["not base64!"]']
)
def test_batch_malformed_posts_json_fails_without_sending(
    posts_json: str, buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POSTS_JSON", posts_json)
    monkeypatch.setattr(
        batch, "detect_posts_via_git_diff", lambda: pytest.fail("diffed again")
    )
    fake = buttondown()
    code, out, _ = run_batch()
    assert code == 1
    assert "::error::POSTS_JSON from the check step is malformed" in out
    assert fake.bodies == []


def test_local_git_diff_fallback_reads_non_ascii_names_verbatim(
    repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Default git config: core.quotePath would quote the name without -z.
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")

    def commit(message: str) -> None:
        for args in (["add", "-A"], ["commit", "-q", "-m", message]):
            subprocess.run(
                ["git", "-c", "user.name=fixture", "-c", "user.email=f@invalid.local"]
                + ["-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]
                + args,
                cwd=repo_root,
                check=True,
                capture_output=True,
            )

    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)
    (repo_root / "README.md").write_text("x\n", encoding="utf-8")
    commit("base")
    _write_post(repo_root / "_posts", "2026-11-19-보안_점검.md")
    commit("post")
    assert batch.detect_posts_via_git_diff() == ["_posts/2026-11-19-보안_점검.md"]


# ---------------------------------------------------------------------------
# 6. A post_path names one real post; drafts and missing posts are reported
# ---------------------------------------------------------------------------


def _outside_the_repo(repo: Path) -> str:
    return str(_write_post(repo.parent, "2026-11-19-Outside.md"))


def _dot_dot_out_of_posts(repo: Path) -> str:
    _write_post(repo, "2026-11-19-Root.md")
    return "_posts/../2026-11-19-Root.md"


def _symlink_out_of_posts(repo: Path) -> str:
    target = _write_post(repo.parent, "2026-11-19-Target.md")
    (repo / "_posts" / "2026-11-19-Link.md").symlink_to(target)
    return "_posts/2026-11-19-Link.md"


def _not_named_like_a_post(repo: Path) -> str:
    _write_post(repo / "_posts", "README.md")
    return "_posts/README.md"


def _not_markdown(repo: Path) -> str:
    _write_post(repo / "_posts", "2026-11-19-Post.txt")
    return "_posts/2026-11-19-Post.txt"


@pytest.mark.parametrize(
    "make_path",
    [
        _outside_the_repo,
        _dot_dot_out_of_posts,
        _symlink_out_of_posts,
        _not_named_like_a_post,
        _not_markdown,
    ],
)
def test_batch_refuses_a_post_path_that_is_not_a_post(
    repo_root: Path, buttondown, run_batch, make_path
) -> None:
    fake = buttondown()
    code, out, _ = run_batch(make_path(repo_root))
    assert code == 1
    assert "::error::Post file not found" in out
    assert fake.bodies == []


def test_batch_mails_a_post_named_twice_once(
    posts_dir: Path, buttondown, run_batch
) -> None:
    post = _write_post(posts_dir, "2026-11-19-Post.md")
    fake = buttondown(201)
    code, _, summary = run_batch(post, "_posts/2026-11-19-Post.md", post.name)
    assert code == 0
    assert len(fake.bodies) == 1
    assert summary.count("2026-11-19-Post.md") == 1


def test_batch_warns_when_the_dispatched_post_is_a_draft(
    posts_dir: Path, buttondown, run_batch
) -> None:
    fake = buttondown()
    draft = _write_post(posts_dir, "2026-11-19-Draft.md", draft="true")
    code, out, summary = run_batch(draft)
    assert (code, fake.bodies) == (0, [])
    assert "::warning::2026-11-19-Draft.md is a draft (draft: true)" in out
    assert "| `2026-11-19-Draft.md` | skipped: draft |" in summary


def test_batch_lists_a_pushed_draft_without_a_warning(
    posts_dir: Path, buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_post(posts_dir, "2026-11-19-Draft.md", draft="true")
    monkeypatch.setenv("POSTS_JSON", _posts_json("_posts/2026-11-19-Draft.md"))
    fake = buttondown()
    code, out, summary = run_batch()
    assert (code, fake.bodies) == (0, [])
    assert "::warning::" not in out
    assert "| `2026-11-19-Draft.md` | skipped: draft |" in summary


def test_batch_warns_about_a_new_post_it_cannot_find(
    posts_dir: Path, buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_post(posts_dir, "2026-11-19-Here.md")
    monkeypatch.setenv(
        "POSTS_JSON",
        _posts_json("_posts/2026-11-19-Here.md", "_posts/2026-11-20-Gone.md"),
    )
    fake = buttondown(201)
    code, out, summary = run_batch()
    assert code == 0
    assert len(fake.bodies) == 1
    assert "::warning::New post _posts/2026-11-20-Gone.md is not a" in out
    assert "| `_posts/2026-11-20-Gone.md` | not sent: file not found |" in summary
    assert "| `2026-11-19-Here.md` | sent |" in summary
