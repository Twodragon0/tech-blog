from scripts.lib.svg_utils import escape_xml_text, escape_xml_attr


def test_escape_basic():
    assert escape_xml_text("A & B") == "A &amp; B"
    assert escape_xml_text("<1s") == "&lt;1s"
    assert escape_xml_text("a < b > c & d") == "a &lt; b &gt; c &amp; d"


def test_escape_idempotent_for_entities():
    assert escape_xml_text("R&amp;D") == "R&amp;D"
    assert escape_xml_text("&lt;ok&gt;") == "&lt;ok&gt;"
    assert escape_xml_text("&#123;") == "&#123;"


def test_escape_mixed():
    assert escape_xml_text("MITRE ATT&CK") == "MITRE ATT&amp;CK"
    assert escape_xml_text("R&amp;D & ML") == "R&amp;D &amp; ML"


def test_escape_attr():
    assert escape_xml_attr('say "hi"') == "say &quot;hi&quot;"


def test_empty():
    assert escape_xml_text("") == ""
    assert escape_xml_text(None) is None  # type: ignore[arg-type]
