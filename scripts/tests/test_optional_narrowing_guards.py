#!/usr/bin/env python3
"""Pin the Optional-narrowing guards added to clear mypy's [arg-type] errors.

Each guard replaced a site where a ``None`` could flow into a callee that was
annotated non-Optional. They fall into two kinds and this file covers both:

  - **Unreachable None, clearer failure.** The five ``spec_from_file_location``
    call sites in scripts/tests/ and the ``check_image_exists`` call site in
    generate_missing_diagrams.py. The None was not reachable in practice, but
    when it *was* reached the resulting error named the wrong thing.
  - **Reachable None, already handled.** ``new_violations(base=None)``, whose
    body documented and implemented the None case while the signature denied
    it. Annotation-only; the test pins the behaviour the annotation now admits.

Also pins the CATEGORY_SVG_CONFIG value-type invariant that the annotation in
scripts/news/config.py asserts.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

TESTS_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# importlib spec guard (5 loader sites)
# ---------------------------------------------------------------------------

# Every scripts/tests/ file that side-loads a module by path. Keep in sync:
# a new side-loader without the guard fails test_every_spec_loader_is_guarded.
_SPEC_LOADER_FILES = (
    "test_svg_size_gate.py",
    "test_visual_regression_gate.py",
    "test_compare_lighthouse_runs.py",
    "test_ci_actionlint_ratchet_guard.py",
    "test_blogwatcher_ssrf.py",
)


def test_spec_from_file_location_can_return_none(tmp_path) -> None:
    """The premise: the guard is not guarding against nothing.

    spec_from_file_location returns None when no loader claims the suffix.
    Passing that None to module_from_spec raises an AttributeError that names
    'NoneType' and 'loader' — it does not say which file failed to load.
    """
    not_python = tmp_path / "gate.txt"
    not_python.write_text("BANDS = {}\n", encoding="utf-8")

    assert importlib.util.spec_from_file_location("_probe", not_python) is None

    # Re-derived into a deliberately Any-typed name: this test *wants* to hand
    # the None to module_from_spec to show what the un-narrowed call does,
    # which is exactly the call mypy flags at the five real loader sites.
    spec: Any = importlib.util.spec_from_file_location("_probe", not_python)
    with pytest.raises(AttributeError) as exc:
        importlib.util.module_from_spec(spec)
    assert "loader" in str(exc.value)
    assert str(not_python) not in str(exc.value)


def test_spec_guard_names_the_file(tmp_path) -> None:
    """The guard idiom fails with the path instead, before module_from_spec."""
    not_python = tmp_path / "gate.txt"
    not_python.write_text("BANDS = {}\n", encoding="utf-8")

    with pytest.raises(AssertionError) as exc:
        spec = importlib.util.spec_from_file_location("_probe", not_python)
        assert spec is not None and spec.loader is not None, f"cannot load {not_python}"
        importlib.util.module_from_spec(spec)
    assert str(not_python) in str(exc.value)


def test_spec_guard_leaves_the_happy_path_alone(tmp_path) -> None:
    """A real .py file still loads and executes through the guarded idiom."""
    module_file = tmp_path / "gate.py"
    module_file.write_text("BANDS = {'std': 1}\n", encoding="utf-8")

    spec = importlib.util.spec_from_file_location("_probe_ok", module_file)
    assert spec is not None and spec.loader is not None, f"cannot load {module_file}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.BANDS == {"std": 1}


@pytest.mark.parametrize("name", _SPEC_LOADER_FILES)
def test_every_spec_loader_is_guarded(name) -> None:
    """Each side-loader narrows the spec before module_from_spec sees it."""
    src = (TESTS_DIR / name).read_text(encoding="utf-8")
    assert "spec_from_file_location" in src, f"{name} no longer side-loads a module"
    assert "is not None and " in src and ".loader is not None" in src, (
        f"{name} calls module_from_spec on an un-narrowed spec; a bad suffix "
        f"would fail with a NoneType AttributeError naming no file"
    )


# ---------------------------------------------------------------------------
# generate_missing_diagrams: unresolvable image path
# ---------------------------------------------------------------------------


def _post_with_diagram_ref(tmp_path: Path) -> Path:
    post = tmp_path / "2026-01-01-Probe.md"
    post.write_text(
        "---\ntitle: probe\n---\n\n"
        "![Architecture overview](/assets/images/diagrams/probe.svg)\n",
        encoding="utf-8",
    )
    return post


def test_unresolvable_image_path_is_skipped_not_crashed(tmp_path, monkeypatch) -> None:
    """check_image_exists -> (False, None) must skip, not reach the generator.

    Before the guard the None was appended to missing_diagrams and handed to
    generate_image_with_gemini, which does output_path.parent — an
    AttributeError on NoneType, several frames from the real cause.
    """
    import scripts.generate_missing_diagrams as mod

    monkeypatch.setattr(mod, "check_image_exists", lambda _p: (False, None))

    def must_not_run(*_a, **_k):
        raise AssertionError("generate_image_with_gemini reached with a None path")

    monkeypatch.setattr(mod, "generate_image_with_gemini", must_not_run)

    assert mod.process_post(_post_with_diagram_ref(tmp_path)) is True


def test_resolvable_image_path_still_reaches_the_generator(
    tmp_path, monkeypatch
) -> None:
    """Control: with a real Path the reference is still processed."""
    import scripts.generate_missing_diagrams as mod

    target = tmp_path / "probe.svg"
    monkeypatch.setattr(mod, "check_image_exists", lambda _p: (False, target))

    seen: list[Path] = []

    def record(_prompt, output_path, *_a, **_k):
        seen.append(output_path)
        return True

    monkeypatch.setattr(mod, "generate_image_with_gemini", record)
    monkeypatch.setattr(mod, "GEMINI_API_KEY", "dummy-not-a-real-key")

    assert mod.process_post(_post_with_diagram_ref(tmp_path)) is True
    assert seen == [target]


# ---------------------------------------------------------------------------
# check_digest_structure.new_violations: base=None
# ---------------------------------------------------------------------------


def test_new_violations_treats_missing_base_as_all_new() -> None:
    """base=None means "file did not exist at the base revision"."""
    from scripts.check_digest_structure import new_violations

    current = ["missing checklist", "missing checklist", "missing sources"]
    out = new_violations(current, None)
    assert out == current
    assert out is not current  # a copy, so the caller cannot mutate the input


def test_new_violations_with_a_base_still_grandfathers_by_kind() -> None:
    """Control: a real base list is still a multiset difference over kind."""
    from scripts.check_digest_structure import new_violations

    current = ["missing checklist", "missing checklist", "missing sources"]
    base = ["missing checklist"]
    assert len(new_violations(current, base)) == 2


# ---------------------------------------------------------------------------
# CATEGORY_SVG_CONFIG value-type invariant
# ---------------------------------------------------------------------------


def test_category_svg_config_icon_color_is_always_a_string() -> None:
    """svg_generator passes config["icon_color"] as the `accent: str` argument.

    The dict's values are heterogeneous (gradient is a tuple), so an unannotated
    literal infers Sequence[str] for every key and makes this read look wrong.
    It is not wrong — but only while every icon_color really is a str.
    """
    from scripts.news.config import CATEGORY_SVG_CONFIG

    assert CATEGORY_SVG_CONFIG, "config is empty; the invariant would be vacuous"
    for category, config in CATEGORY_SVG_CONFIG.items():
        assert isinstance(config["icon_color"], str), category
        assert isinstance(config["label"], str), category
        assert isinstance(config["icon"], str), category
        assert isinstance(config["gradient"], tuple), category
