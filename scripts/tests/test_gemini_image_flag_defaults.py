#!/usr/bin/env python3
"""The Gemini image flags must mean the same thing in every reader.

`USE_GEMINI_PRO_IMAGE` had three different defaults at once (measured 2026-09-18):

    scripts/generate_post_images.py:146       "true"   -> Gemini 3 Pro
    scripts/generate_missing_diagrams.py:42   "false"  -> Gemini 2.5 Flash
    .github/workflows/generate-images.yml     'false'  -> Gemini 2.5 Flash
    docs/setup/MULTI_TOOL_HARNESS_ENV.md      `true`

So "what model does a local run use?" had no single answer, and the docs agreed
with neither CI nor the other script. Unified to Flash; Pro is now an explicit
request. A flag whose default depends on which file you read is not a flag.

The second half of this file guards something sharper. Until 2026-09-18 the only
thing standing between a shell and the Gemini image API was `if GEMINI_API_KEY:`.
Exporting the key was enough to call the API, and a successful call returns True
— which skips the entire `if not image_generated:` branch: the L20/L22/L25/rollup
SVG cover generators, the honesty scorer, and its blocking gate. The post's
`image:` field points at `.svg` while the raster lands at `<stem>.png`, so the
referenced SVG would simply never be built.

Never observed in the corpus (0 posts whose `image:` fails to resolve), because
an existing cover returns early at `has_image and not force` and CI withholds
the key. Latent, not historical — but `generate_post_images.py --force` over the
digests is exactly the run that springs it, and CLAUDE.md already warns against
that command for an unrelated reason.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
POST_IMAGES = REPO_ROOT / "scripts" / "generate_post_images.py"
MISSING_DIAGRAMS = REPO_ROOT / "scripts" / "generate_missing_diagrams.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "generate-images.yml"
HARNESS_DOC = REPO_ROOT / "docs" / "setup" / "MULTI_TOOL_HARNESS_ENV.md"


def _getenv_default(path: Path, var: str) -> str | None:
    """The literal default in `os.getenv("<var>", "<default>")`, via AST.

    Parsed rather than grepped: this repo has read a hardcoded list as 18 when
    it was 32 because a non-greedy regex stopped early.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "getenv"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == var
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
        ):
            return node.args[1].value
    return None


def _call_site_guards(path: Path, func: str) -> list[str]:
    """Source of each `if` that encloses a call to `func`.

    Substring scans cannot tell a call from prose about a call — this repo hit
    that three times on 2026-09-18 alone. So walk the tree and read the actual
    enclosing conditions.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent  # type: ignore[attr-defined]

    guards: list[str] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == func
        ):
            continue
        cur = getattr(node, "parent", None)
        conditions = []
        while cur is not None:
            if isinstance(cur, ast.If):
                conditions.append(ast.get_source_segment(source, cur.test) or "")
            cur = getattr(cur, "parent", None)
        guards.append(" AND ".join(conditions) or "<unconditional>")
    return guards


def _workflow_defaults(var: str) -> list[str]:
    """`${{ vars.X || 'default' }}` occurrences in the workflow."""
    text = WORKFLOW.read_text(encoding="utf-8")
    return re.findall(
        rf"\$\{{\{{\s*vars\.{re.escape(var)}\s*\|\|\s*'([^']*)'\s*\}}\}}", text
    )


@pytest.mark.parametrize("path", [POST_IMAGES, MISSING_DIAGRAMS])
def test_pro_flag_defaults_to_flash_in_every_script(path: Path) -> None:
    """Both readers must agree, and agree with CI."""
    default = _getenv_default(path, "USE_GEMINI_PRO_IMAGE")
    assert default is not None, (
        f"{path.name} no longer reads USE_GEMINI_PRO_IMAGE with a literal "
        "default. If the flag moved, update this guard in the same change."
    )
    assert default.lower() == "false", (
        f"{path.name} defaults USE_GEMINI_PRO_IMAGE to {default!r}. The other "
        "reader, the workflow and the docs all say 'false'; a flag whose default "
        "depends on which file you read is not a flag. Pro stays available via "
        "--use-pro-image or the repo variable."
    )


def test_workflow_default_matches_the_scripts() -> None:
    defaults = _workflow_defaults("USE_GEMINI_PRO_IMAGE")
    assert defaults, (
        "generate-images.yml no longer supplies a default for "
        "USE_GEMINI_PRO_IMAGE. An unset repo variable would render as '' and the "
        "scripts would take their own default — the drift this file exists to stop."
    )
    assert set(d.lower() for d in defaults) == {"false"}, (
        f"workflow defaults are {defaults}; expected every one to be 'false'."
    )


def test_docs_do_not_contradict_the_code() -> None:
    """The docs said `true` while nothing else did.

    Documentation that disagrees with the code is worse than none: it is the
    thing people act on.
    """
    text = HARNESS_DOC.read_text(encoding="utf-8")
    assert "USE_GEMINI_PRO_IMAGE=true" not in text, (
        "MULTI_TOOL_HARNESS_ENV.md still shows USE_GEMINI_PRO_IMAGE=true in the "
        "sample env. The default is false."
    )
    assert re.search(r"`USE_GEMINI_PRO_IMAGE`\s*\|\s*`false`", text), (
        "The variable table no longer documents `false` as the default."
    )


def test_raster_path_is_opt_in_not_key_presence() -> None:
    """`if GEMINI_API_KEY:` alone must not reach the image API.

    The gate has to include the explicit opt-in, or merely having the key
    exported bypasses the SVG cover system — see this module's docstring.
    """
    guards = _call_site_guards(POST_IMAGES, "generate_image_with_gemini")
    assert guards, (
        "No `if ...: generate_image_with_gemini(...)` found. If the call moved, "
        "update this guard in the same change."
    )
    assert all("USE_IMAGE_API" in g for g in guards), (
        f"the Gemini call is reachable under {guards} — at least one path does "
        "not require USE_IMAGE_API. A shell with GEMINI_API_KEY exported would "
        "silently take the raster path and skip the L20/L22/L25 cover "
        "generators, leaving the .svg that the post's `image:` field references "
        "unbuilt.\n\nChecked on the AST, not as a substring: the same text also "
        "appears in a log line, so a substring scan passes while the real call "
        "site is ungated (measured — the first draft of this test did exactly "
        "that and a mutation probe caught it)."
    )
    default = _getenv_default(POST_IMAGES, "USE_GEMINI_IMAGE_API")
    assert default is not None and default.lower() == "false", (
        f"USE_GEMINI_IMAGE_API defaults to {default!r}. It must be off by default "
        "— on is the destructive direction."
    )


def test_cli_can_still_turn_the_api_on() -> None:
    """Not vacuous: gating it off entirely would remove a working feature."""
    source = POST_IMAGES.read_text(encoding="utf-8")
    assert '"--use-api"' in source, (
        "The --use-api flag is gone, so the Gemini raster path can only be "
        "reached through the environment. Keep an explicit way in."
    )
    assert '"--use-pro-image"' in source, "The Pro override was removed."


def test_workflow_passes_the_opt_in_so_ci_behaviour_is_unchanged() -> None:
    """CI was already opt-in via its `use_api` input (default false).

    The script-side gate must be fed from that same decision, or dispatching the
    workflow with `use_api: true` would silently stop calling the API.
    """
    spec = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    on = spec.get(True) or spec.get("on") or {}
    use_api = ((on.get("workflow_dispatch") or {}).get("inputs") or {}).get("use_api")
    assert use_api is not None, "the `use_api` input disappeared"
    assert use_api.get("default") in (False, "false"), (
        f"`use_api` now defaults to {use_api.get('default')!r}. On by default "
        "means every push spends on the image API and bypasses the SVG covers."
    )

    steps = [
        s
        for job in spec["jobs"].values()
        for s in (job.get("steps") or [])
        if "USE_GEMINI_IMAGE_API" in (s.get("env") or {})
    ]
    assert steps, (
        "No step passes USE_GEMINI_IMAGE_API. The script now defaults it off, so "
        "a workflow_dispatch with use_api=true would no longer call the API."
    )
    for step in steps:
        value = str(step["env"]["USE_GEMINI_IMAGE_API"])
        assert "api_check" in value, (
            f"USE_GEMINI_IMAGE_API is set to {value!r} rather than derived from "
            "the api_check step. It must follow the same `use_api` + key-length "
            "decision that already gates the key itself."
        )


def test_dead_segment_step_does_not_carry_the_flag() -> None:
    """`scripts/generate_segment_images.py` is archived.

    The step warns and exits 0 without reading anything, so a flag there is
    decoration that reads as configuration.
    """
    assert not (REPO_ROOT / "scripts" / "generate_segment_images.py").exists(), (
        "generate_segment_images.py is back. Re-add its flags and drop this test."
    )
    spec = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    for job in spec["jobs"].values():
        for step in job.get("steps") or []:
            if "segment" in str(step.get("name", "")).lower():
                assert "USE_GEMINI_PRO_IMAGE" not in (step.get("env") or {}), (
                    "The archived segment step carries USE_GEMINI_PRO_IMAGE again."
                )
