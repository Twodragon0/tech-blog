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


class _Response:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text

    def json(self) -> dict:
        return {"id": "em_test"}


class _FakeButtondown:
    """Stands in for requests.post; answers with a scripted status per call."""

    def __init__(self, *outcomes: "int | type[Exception]") -> None:
        self.outcomes = list(outcomes)
        self.bodies: list = []

    def __call__(self, url: str, json: dict, headers: dict, timeout: int):
        self.bodies.append(json["body"])
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, type) and issubclass(outcome, Exception):
            raise outcome("simulated")
        return _Response(outcome, "{}" if outcome < 300 else '{"detail": "nope"}')


@pytest.fixture(autouse=True)
def _no_real_buttondown(monkeypatch: pytest.MonkeyPatch) -> None:
    """A test that forgets the fake must fail, not mail the real list.

    requests.post/get/request and every Session end in Session.request.
    conftest.py also blocks sockets to other hosts underneath it.
    """

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("test reached requests without the Buttondown fake")

    monkeypatch.setattr(requests.sessions.Session, "request", refuse)


@pytest.fixture
def buttondown(monkeypatch: pytest.MonkeyPatch):
    def install(*outcomes: "int | type[Exception]") -> _FakeButtondown:
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
    "outcome, expected",
    [
        (200, buttondown_notify.SENT),
        (201, buttondown_notify.SENT),
        (401, buttondown_notify.AUTH_REJECTED),
        (403, buttondown_notify.AUTH_REJECTED),
        (429, buttondown_notify.TRANSIENT),
        (500, buttondown_notify.TRANSIENT),
        (503, buttondown_notify.TRANSIENT),
        (requests.exceptions.Timeout, buttondown_notify.TRANSIENT),
        (requests.exceptions.ConnectionError, buttondown_notify.TRANSIENT),
        (400, buttondown_notify.FAILED),
        (422, buttondown_notify.FAILED),
        (requests.exceptions.RequestException, buttondown_notify.FAILED),
    ],
)
def test_send_classifies_the_outcome(buttondown, outcome, expected: str) -> None:
    buttondown(outcome)
    assert buttondown_notify.send_buttondown_email("s", "b", "key") == expected


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
def run_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
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


def test_batch_sends_new_posts(tmp_path: Path, buttondown, run_batch) -> None:
    fake = buttondown(201, 201)
    posts = [_write_post(tmp_path, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, summary = run_batch(*posts)
    assert code == 0
    assert len(fake.bodies) == 2
    assert "::error::" not in out and "::warning::" not in out
    assert "| `2026-11-18-Post_8.md` | sent |" in summary


def test_batch_rejected_key_fails_the_job_and_stops(
    tmp_path: Path, buttondown, run_batch
) -> None:
    fake = buttondown(401)
    posts = [_write_post(tmp_path, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, summary = run_batch(*posts)
    assert code == 1
    assert "::error::BUTTONDOWN_API_KEY rejected — rotate it in repo secrets" in out
    assert len(fake.bodies) == 1, "kept sending with a key Buttondown rejected"
    assert "stopped after the key was rejected" in summary


def test_batch_transient_failure_warns_without_failing(
    tmp_path: Path, buttondown, run_batch
) -> None:
    buttondown(503)
    code, out, summary = run_batch(_write_post(tmp_path, "2026-11-19-Post.md"))
    assert code == 0
    assert "::warning::Buttondown failed temporarily" in out
    assert "::error::" not in out
    assert "temporary Buttondown failure" in summary


def test_batch_refused_request_fails_the_job(
    tmp_path: Path, buttondown, run_batch
) -> None:
    buttondown(400, 201)
    posts = [_write_post(tmp_path, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, _ = run_batch(*posts)
    assert code == 1
    assert "::error::Buttondown refused the newsletter for 2026-11-18-Post_8.md" in out


def test_batch_bulk_run_sends_nothing(tmp_path: Path, buttondown, run_batch) -> None:
    fake = buttondown()
    posts = [_write_post(tmp_path, f"2026-11-1{i}-Post_{i}.md") for i in range(4)]
    code, out, summary = run_batch(*posts)
    assert code == 0
    assert fake.bodies == []
    assert (
        "::warning::4 new posts in one run is more than BUTTONDOWN_MAX_POSTS=3" in out
    )
    assert summary.count("skipped: bulk run") == 4


def test_batch_limit_is_configurable(
    tmp_path: Path, buttondown, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("BUTTONDOWN_MAX_POSTS", "1")
    fake = buttondown()
    posts = [_write_post(tmp_path, f"2026-11-1{i}-Post_{i}.md") for i in (8, 9)]
    code, out, _ = run_batch(*posts)
    assert (code, fake.bodies) == (0, [])
    assert "BUTTONDOWN_MAX_POSTS=1" in out


def test_batch_skips_imported_posts(tmp_path: Path, buttondown, run_batch) -> None:
    fake = buttondown(201)
    imported = _write_post(
        tmp_path,
        "2024-09-01-EKS_Pod_Restart.md",
        date="2024-09-01 20:36:28 +0900",
        original_url="https://2twodragon.com/pod-restart-temp-auth-iam-role/",
    )
    new = _write_post(tmp_path, "2026-11-19-New_Post.md")
    code, out, summary = run_batch(imported, new)
    assert code == 0
    assert len(fake.bodies) == 1 and "New_Post" in fake.bodies[0]
    assert "::warning::Skipped 1 imported post(s)" in out
    assert "skipped: imported from https://2twodragon.com/pod-restart" in summary


def test_batch_with_only_drafts_is_not_a_failure(
    tmp_path: Path, buttondown, run_batch
) -> None:
    fake = buttondown()
    draft = _write_post(tmp_path, "2026-11-19-Draft.md", draft="true")
    code, _, _ = run_batch(draft)
    assert (code, fake.bodies) == (0, [])


def test_batch_unknown_explicit_post_fails(tmp_path: Path, run_batch) -> None:
    code, out, _ = run_batch(tmp_path / "2026-11-19-Missing.md")
    assert code == 1
    assert "::error::Post file not found" in out


def test_batch_without_api_key_fails(
    tmp_path: Path, run_batch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("BUTTONDOWN_API_KEY")
    code, out, _ = run_batch(_write_post(tmp_path, "2026-11-19-Post.md"))
    assert code == 1
    assert "::error::BUTTONDOWN_API_KEY" in out
