"""Shared pytest configuration for scripts/tests/.

Disables all external API calls (Gemini, DeepSeek, OpenAI) and patches
module-level globals to prevent network access during testing. Also keeps
every test's git commands out of the repository that launched pytest.
"""

import os
import sys
from pathlib import Path

import pytest

# --- Environment: disable all API keys before any module import ---
os.environ["GEMINI_API_KEY"] = ""
os.environ["DEEPSEEK_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["NEWS_NO_TRANSLATE"] = "1"

# --- Path setup ---
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Patch module globals to block CLI/network calls ---
import auto_publish_news  # noqa: E402

auto_publish_news._GEMINI_AVAILABLE = False
auto_publish_news._GEMINI_CIRCUIT_OPEN = True

# Saved original state for reset
_ORIG_GEMINI_AVAILABLE = False
_ORIG_CIRCUIT_OPEN = True
_ORIG_TITLE_CACHE: dict[str, str] = {}


@pytest.fixture(autouse=True)
def _reset_module_state():
    """Reset mutable module state after each test to prevent cross-contamination."""
    yield
    auto_publish_news._GEMINI_AVAILABLE = _ORIG_GEMINI_AVAILABLE
    auto_publish_news._GEMINI_CIRCUIT_OPEN = _ORIG_CIRCUIT_OPEN
    auto_publish_news.KOREAN_TITLE_CACHE.clear()
    auto_publish_news.KOREAN_TITLE_CACHE.update(_ORIG_TITLE_CACHE)


# --- Git repository isolation ---
# Git exports repository-local variables to the hooks it runs: GIT_INDEX_FILE,
# and GIT_DIR, which in a linked worktree is an absolute path into the shared
# .git. When the pre-commit hook runs this suite there, every `git` a test
# spawns in its own tmp repo inherits them and acts on the developer's checkout
# instead. That has happened: fixture posts were staged and committed there,
# and the shared .git/config got core.bare=true (`git init` guesses "bare" when
# GIT_DIR does not end in /.git) plus a fixture's user.name, user.email and
# commit.gpgsign.
#
# The list is `git rev-parse --local-env-vars` minus GIT_CONFIG_PARAMETERS and
# GIT_CONFIG_COUNT, the same set git clears itself before running a command in
# another repository, such as a submodule. Those two carry `git -c` settings,
# not a location, so they stay, as do GIT_AUTHOR_* / GIT_COMMITTER_*: identity
# selects no repository, and commits in tmp repos may rely on it.
_REPO_LOCAL_GIT_ENV = (
    # Which repository, work tree and index git acts on, and where in it.
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_IMPLICIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_INDEX_FILE",
    "GIT_PREFIX",
    # Where objects are read from and written to.
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    # Per-repository state otherwise taken from the caller: the config file
    # `git config` writes, grafts, shallow boundary and replace refs.
    "GIT_CONFIG",
    "GIT_GRAFT_FILE",
    "GIT_SHALLOW_FILE",
    "GIT_REPLACE_REF_BASE",
    "GIT_NO_REPLACE_OBJECTS",
)


# Removed once when this file is imported, too: module- and session-scoped
# fixtures, class-level setup and import-time code all run before the
# function-scoped fixture below would.
for _name in _REPO_LOCAL_GIT_ENV:
    os.environ.pop(_name, None)


@pytest.fixture(autouse=True)
def _isolate_git_repo_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make each test's git find its repository from its own cwd.

    The import-time removal above already covers the whole process; this
    re-applies it per test in case something set the variables again.
    """
    for name in _REPO_LOCAL_GIT_ENV:
        monkeypatch.delenv(name, raising=False)
