#!/usr/bin/env python3
"""``check_posts.py`` must report its verdict through its exit code.

Until 2026-09-10 line 1116 was a bare ``main()`` instead of ``sys.exit(main())``,
and ``main()`` had no failing return path. The script therefore exited 0 no
matter what it found:

    $ python3 scripts/check_posts.py; echo $?
    Summary: 5 total issues found in 4 files
    0
    $ python3 scripts/check_posts.py _posts/DOES_NOT_EXIST.md; echo $?
    ⚠️  File not found: .../_posts/DOES_NOT_EXIST.md
    0

That matters because three callers read the exit code and one of them is on the
publish path — ``ai-blogwatcher.yml``'s "Validate new post" step, run against
the bot's digest of the day. Hard errors in its issue set (``❌ Main image file
not found``, ``❌ Missing required field``) therefore gated nothing: a digest
pointing at a missing cover passed every gate in the repo.
``check-svg.yml:118-135`` already distrusted the number and grepped stdout, but
only for 2 of ~22 issue classes.

Scope is deliberate and these tests pin both halves of it
---------------------------------------------------------
Only ``❌`` blocks. ``⚠️`` and ``💡`` do not.

``❌`` is objective — a file is absent, a required field is missing. The ``⚠️``
set is ~22 heuristics including "Generic title should be more specific" and
"Title looks like keyword soup". Making those blocking on the cron path would
let a title heuristic delete a day's digest, and this repo has just lost two
publish days (2026-09-05, 09-06) to gates that blocked more than they could
repair. If a warning class is worth blocking, promote that class to ``❌``
deliberately rather than widening the threshold here.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_posts.py"

# A post whose every required field is present and whose image resolves. Body
# kept minimal so no warning heuristic fires; each test perturbs one thing.
_GOOD_IMAGE = (
    "/assets/images/2026-09-09-Tech_Security_Weekly_Digest_API_Bitcoin_AI_GPT.svg"
)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_post(
    tmp_path: Path, *, image: str = _GOOD_IMAGE, body: str = "본문입니다.\n"
) -> Path:
    post = tmp_path / "2026-09-09-Fixture_Post.md"
    post.write_text(
        "---\n"
        "layout: post\n"
        'title: "픽스처 포스트"\n'
        "date: 2026-09-09 09:00:00 +0900\n"
        "categories: [security]\n"
        "tags: [security]\n"
        'excerpt: "테스트용 픽스처 포스트입니다."\n'
        f"image: {image}\n"
        "---\n\n" + body,
        encoding="utf-8",
    )
    return post


class TestExitCodeIsWired:
    def test_clean_post_exits_zero(self, tmp_path):
        """Control. Without this the rest could pass by failing on everything."""
        r = _run(str(_write_post(tmp_path)))
        assert r.returncode == 0, f"clean fixture should pass:\n{r.stdout}\n{r.stderr}"

    def test_missing_main_image_exits_nonzero(self, tmp_path):
        """`❌ Main image file not found` — the defect that reached production."""
        post = _write_post(tmp_path, image="/assets/images/NO_SUCH_COVER_9f3a.svg")
        r = _run(str(post))
        assert "❌" in r.stdout, f"expected a hard error in output:\n{r.stdout}"
        assert r.returncode != 0, (
            "a post whose cover image does not exist still exits 0. This is the "
            "publish path's 'Validate new post' gate — it must fail."
        )

    def test_missing_required_field_exits_nonzero(self, tmp_path):
        post = _write_post(tmp_path)
        post.write_text(
            post.read_text(encoding="utf-8").replace("tags: [security]\n", ""),
            encoding="utf-8",
        )
        r = _run(str(post))
        assert "❌ Missing required field" in r.stdout
        assert r.returncode != 0

    def test_explicitly_named_missing_file_exits_nonzero(self):
        """A path that does not resolve must not read as 'nothing wrong'.

        The workflow passes `$POST_FILE`. If that ever resolves to nothing —
        a rename, a wrong glob, an empty variable — the old code printed a
        warning and exited 0, i.e. the gate checked zero files and passed.
        """
        r = _run("_posts/DOES_NOT_EXIST_8c21.md")
        assert r.returncode != 0, (
            "a named-but-absent post exits 0, so the gate can pass having "
            "inspected nothing at all."
        )


class TestThresholdIsErrorsOnly:
    """Warnings and advisories must NOT block — see the module docstring."""

    def test_advisory_only_post_exits_zero(self, tmp_path):
        """`💡 Long code block` is advice, not a defect."""
        long_block = "```python\n" + "x = 1\n" * 40 + "```\n"
        r = _run(str(_write_post(tmp_path, body=long_block)))
        assert "💡" in r.stdout, f"fixture did not produce an advisory:\n{r.stdout}"
        assert "❌" not in r.stdout
        assert r.returncode == 0, (
            "a 💡 advisory blocked the run. On the cron path that deletes a day "
            "of content over a code-block length suggestion."
        )

    def test_warning_only_post_exits_zero(self, tmp_path):
        """`⚠️ Possible dummy link` is a heuristic; heuristics do not block."""
        r = _run(str(_write_post(tmp_path, body="[예시](https://example.com/foo)\n")))
        assert "⚠️" in r.stdout, f"fixture did not produce a warning:\n{r.stdout}"
        assert "❌" not in r.stdout
        assert r.returncode == 0, (
            "a ⚠️ warning blocked the run. The ⚠️ set includes title heuristics; "
            "blocking them on the publish path trades a lost digest for a "
            "style opinion. Promote a class to ❌ instead of widening this."
        )


class TestCorpusStaysGreen:
    def test_real_corpus_exits_zero(self):
        """The gate must land green on the corpus it is about to start gating.

        Measured 2026-09-10: 5 issues in 4 files, all `💡 Long code block`, zero
        ❌. A gate wired while red is a gate that gets muted.
        """
        r = _run()
        assert r.returncode == 0, (
            "check_posts.py now fails on the live corpus. Wiring it that way "
            f"would make every publish red. Output tail:\n{r.stdout[-3000:]}"
        )
