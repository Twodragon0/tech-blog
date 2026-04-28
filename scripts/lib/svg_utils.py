"""SVG utility helpers — XML text escape & validation."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path


_XML_TEXT_ESCAPES = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
}


def escape_xml_text(text: str) -> str:
    """Escape XML special chars for use inside SVG text element bodies.

    Replaces & with &amp;, < with &lt;, > with &gt;.
    Idempotent for already-escaped entities (e.g. &amp; stays &amp;).
    """
    if not text:
        return text
    # First, protect existing entity references like &amp; &lt; &#123; &nbsp;
    # by tokenizing them, escape raw chars, then restore.
    placeholder = "\x00ENT\x00"
    pattern = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9A-Fa-f]+);")
    entities: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        entities.append(match.group(0))
        return placeholder

    stashed = pattern.sub(_stash, text)
    escaped = (
        stashed.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    for ent in entities:
        escaped = escaped.replace(placeholder, ent, 1)
    return escaped


def escape_xml_attr(text: str) -> str:
    """Escape XML special chars for attribute values (adds quote escaping)."""
    return escape_xml_text(text).replace('"', "&quot;").replace("'", "&apos;")


def is_valid_svg(path: Path | str) -> tuple[bool, str]:
    """Return (ok, error_message). Uses xmllint when available, falls back to ElementTree."""
    p = Path(path)
    if not p.exists():
        return False, f"missing: {p}"
    try:
        result = subprocess.run(
            ["xmllint", "--noout", str(p)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip()
    except FileNotFoundError:
        # xmllint not installed — fall back to xml.etree
        import xml.etree.ElementTree as ET
        try:
            ET.parse(p)
            return True, ""
        except ET.ParseError as e:
            return False, str(e)
    except subprocess.TimeoutExpired:
        return False, "xmllint timeout"


__all__ = ["escape_xml_text", "escape_xml_attr", "is_valid_svg"]
