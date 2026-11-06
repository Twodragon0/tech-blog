"""Only the explicit Vercel site build may regenerate the shared _site tree.

The Node API builder also discovers reserved package build scripts; those hooks
must not rerun a destructive site build while static packaging reads its files.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_node_function_builder_has_no_implicit_site_build_hook():
    package = json.loads((ROOT / "package.json").read_text())
    assert not {"vercel-build", "now-build"} & set(package["scripts"])


def test_static_site_has_one_explicit_build_owner():
    config = json.loads((ROOT / "vercel.json").read_text())
    assert config["buildCommand"] == "chmod +x build.sh && ./build.sh"
    assert config["outputDirectory"] == "_site"
    assert config["functions"]
    assert all((ROOT / name).is_file() for name in config["functions"])
