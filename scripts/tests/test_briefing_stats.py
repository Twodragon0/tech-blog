"""Regression tests for executive briefing severity stat consistency.

Catches the class of bug discovered in the 2026-04-10/11/12/13 digest posts
where the briefing claimed e.g. "High 등급 위협 6건" while the actual severity
tagging yielded 5. Any divergence between the "N건" claim and the real
severity count is a regression.
"""

import re
from typing import Dict, List

import pytest

from news.content_generator import _generate_executive_and_risk_sections
from news_utils import determine_severity

_CRITICAL_RE = re.compile(r"Critical 등급 위협\s+(\d+)건")
_HIGH_RE = re.compile(r"High 등급 위협\s+(\d+)건")


def _make_item(title: str, category: str = "security", summary: str = "") -> Dict:
    """Build a minimal news item compatible with the briefing generator."""
    return {
        "title": title,
        "summary": summary or title,
        "content": "",
        "category": category,
        "source": "test",
        "url": "https://example.test/",
    }


def _actual_counts(items: List[Dict]) -> Dict[str, int]:
    """Compute ground-truth severity distribution the same way the generator does."""
    counts = {"Critical": 0, "High": 0, "Medium": 0}
    for item in items:
        text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
        sev = determine_severity(text, item.get("category", "tech"))
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def _parse_briefing(output: str) -> Dict[str, int]:
    """Extract claimed N-counts from the generated briefing string."""
    claimed: Dict[str, int] = {}
    if m := _CRITICAL_RE.search(output):
        claimed["Critical"] = int(m.group(1))
    if m := _HIGH_RE.search(output):
        claimed["High"] = int(m.group(1))
    return claimed


class TestBriefingStatConsistency:
    """Briefing '등 N건' claims must match the actual severity tag count."""

    def test_critical_claim_matches_actual_count(self):
        items = [
            _make_item("Critical RCE zero-day in authentication module"),
            _make_item("Another zero-day exploit actively exploited in the wild"),
            _make_item("Ransomware attack encrypts enterprise backups"),
            _make_item("Routine malware campaign detected"),
        ]
        actual = _actual_counts(items)
        output = _generate_executive_and_risk_sections(items, mode="security")
        claimed = _parse_briefing(output)

        if "Critical" in claimed:
            assert claimed["Critical"] == actual["Critical"], (
                f"Briefing claimed Critical={claimed['Critical']} "
                f"but actual count is {actual['Critical']}. Output:\n{output}"
            )

    def test_high_claim_matches_actual_count(self):
        items = [
            _make_item("Spear phishing campaign using APT tactics"),
            _make_item("Backdoor discovered in supply chain component"),
            _make_item("New malware strain observed in the wild"),
            _make_item("Botnet expands with DDoS capability"),
            _make_item("SSRF vulnerability in web application"),
        ]
        actual = _actual_counts(items)
        output = _generate_executive_and_risk_sections(items, mode="security")
        claimed = _parse_briefing(output)

        assert "High" in claimed, f"Expected High line in briefing, got:\n{output}"
        assert claimed["High"] == actual["High"], (
            f"Briefing claimed High={claimed['High']} "
            f"but actual count is {actual['High']}. Output:\n{output}"
        )

    def test_both_severities_match_simultaneously(self):
        items = [
            _make_item("Zero-day RCE actively exploited"),
            _make_item("Critical flaw in kernel module"),
            _make_item("Phishing campaign targets enterprises"),
            _make_item("Malware distribution via compromised CDN"),
            _make_item("Backdoor in popular SDK"),
            _make_item("Routine advisory about software updates", category="tech"),
        ]
        actual = _actual_counts(items)
        output = _generate_executive_and_risk_sections(items, mode="security")
        claimed = _parse_briefing(output)

        for sev, count in claimed.items():
            assert count == actual[sev], (
                f"Mismatch on {sev}: briefing claims {count}, actual {actual[sev]}. "
                f"Full briefing:\n{output}"
            )

    @pytest.mark.parametrize(
        "critical_n,high_n,medium_n",
        [
            (0, 1, 3),
            (1, 0, 2),
            (2, 3, 4),
            (0, 0, 5),
            (3, 5, 2),
        ],
    )
    def test_parametric_count_alignment(self, critical_n, high_n, medium_n):
        """Random mixtures must keep briefing claims honest."""
        items = []
        for i in range(critical_n):
            items.append(_make_item(f"Zero-day RCE number {i}"))
        for i in range(high_n):
            items.append(_make_item(f"Malware campaign {i}"))
        for i in range(medium_n):
            items.append(_make_item(f"Generic advisory {i}", category="tech"))

        actual = _actual_counts(items)
        output = _generate_executive_and_risk_sections(items, mode="security")
        claimed = _parse_briefing(output)

        for sev, count in claimed.items():
            assert count == actual[sev], (
                f"[{critical_n}C/{high_n}H/{medium_n}M] "
                f"briefing {sev}={count}, actual={actual[sev]}\n{output}"
            )

    def test_empty_news_items_produces_no_false_claims(self):
        output = _generate_executive_and_risk_sections([], mode="security")
        claimed = _parse_briefing(output)
        assert claimed == {}, f"Empty input should not yield severity claims: {output}"


class TestBriefingStructureSnapshot:
    """Structural snapshot guard for the executive briefing layout.

    Locks in the shape of `_generate_executive_and_risk_sections` output so
    that intentional structure changes surface as explicit test updates
    rather than silent drift. Validates section headers, line prefixes,
    scorecard row count, and header ordering.
    """

    _EXPECTED_SECTION_HEADERS = ("## 경영진 브리핑", "## 위험 스코어카드")

    _EXPECTED_SCORECARD_AREAS = (
        "| 위협 대응 |",
        "| 탐지/모니터링 |",
        "| 취약점 관리 |",
        "| 클라우드 보안 |",
    )

    @staticmethod
    def _security_fixture() -> List[Dict]:
        return [
            _make_item("Zero-day RCE actively exploited in wild"),
            _make_item("Ransomware attack on healthcare network"),
            _make_item("Phishing campaign impersonates finance team"),
            _make_item("Malware distribution via compromised CDN"),
            _make_item("Cloud misconfiguration exposes S3 bucket", category="cloud"),
            _make_item("CVE-2026-99999 patched upstream", category="security"),
        ]

    def _generate(self) -> str:
        return _generate_executive_and_risk_sections(
            self._security_fixture(), mode="security"
        )

    def test_contains_both_section_headers_in_order(self):
        output = self._generate()
        positions = []
        for header in self._EXPECTED_SECTION_HEADERS:
            idx = output.find(header)
            assert idx >= 0, f"Missing section header: {header}\nOutput:\n{output}"
            positions.append(idx)
        assert positions == sorted(positions), (
            f"Section headers out of order: {self._EXPECTED_SECTION_HEADERS}"
        )

    def test_briefing_lines_use_expected_prefixes(self):
        """Every briefing bullet must start with '- ' — no orphaned prose."""
        output = self._generate()
        briefing_block = output.split("## 경영진 브리핑", 1)[1].split(
            "## 위험 스코어카드", 1
        )[0]
        bullets = [
            ln for ln in briefing_block.splitlines() if ln.strip() and not ln.startswith("#")
        ]
        assert bullets, f"Briefing block was empty:\n{briefing_block}"
        for ln in bullets:
            assert ln.startswith("- "), (
                f"Briefing line missing bullet prefix: {ln!r}\nFull block:\n{briefing_block}"
            )

    def test_scorecard_has_all_four_areas(self):
        output = self._generate()
        for area in self._EXPECTED_SCORECARD_AREAS:
            assert area in output, (
                f"Scorecard missing area row: {area}\nOutput:\n{output}"
            )

    def test_scorecard_row_count_stable(self):
        output = self._generate()
        scorecard = output.split("## 위험 스코어카드", 1)[1]
        data_rows = [
            ln
            for ln in scorecard.splitlines()
            if ln.startswith("|") and "---" not in ln and "영역" not in ln
        ]
        assert len(data_rows) == 4, (
            f"Expected 4 scorecard data rows, got {len(data_rows)}:\n{scorecard}"
        )

    def test_empty_input_still_emits_both_headers(self):
        output = _generate_executive_and_risk_sections([], mode="security")
        for header in self._EXPECTED_SECTION_HEADERS:
            assert header in output, (
                f"Empty input dropped header {header!r}:\n{output}"
            )

    def test_output_ends_with_double_newline(self):
        """Callers concatenate directly — trailing whitespace contract must hold."""
        output = self._generate()
        assert output.endswith("\n\n"), f"Output missing trailing \\n\\n: {output[-10:]!r}"

    def test_tech_blog_mode_does_not_emit_severity_claims(self):
        """tech-blog mode uses action-point style briefing, not severity counts."""
        output = _generate_executive_and_risk_sections(
            self._security_fixture(), mode="tech-blog"
        )
        assert "Critical 등급 위협" not in output, (
            f"tech-blog mode should not claim Critical counts:\n{output}"
        )
        assert "High 등급 위협" not in output, (
            f"tech-blog mode should not claim High counts:\n{output}"
        )


class TestPublishedDigestConsistency:
    """Scan real digest posts to ensure briefing '등 N건' == rendered card severity count.

    Catches the 2026-04-10/11/12/13 class of bug where the briefing counted
    pre-filter items but only a subset of items became rendered news cards.

    Uses a ratchet cutoff: posts published on/after CUTOFF_ISO must match.
    Historical posts before the cutoff are known to have inconsistencies and
    are documented as accepted debt — fix them opportunistically and move the
    cutoff earlier when safe. Never raise the cutoff (that would hide regressions).
    """

    CUTOFF_ISO = "2026-03-21"  # ratchet: only posts on/after this date are enforced

    _POSTS_DIR = None  # lazily resolved

    @classmethod
    def _posts_dir(cls):
        if cls._POSTS_DIR is None:
            from pathlib import Path

            cls._POSTS_DIR = Path(__file__).resolve().parents[2] / "_posts"
        return cls._POSTS_DIR

    @staticmethod
    def _count_severity_tags(markdown: str) -> Dict[str, int]:
        """Count severity="..." occurrences in news-card includes."""
        tags = re.findall(r'severity="(Critical|High|Medium|Low)"', markdown)
        out = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for t in tags:
            out[t] += 1
        return out

    @classmethod
    def _digest_posts_after_cutoff(cls):
        posts = sorted(cls._posts_dir().glob("*Tech_Security_Weekly_Digest*.md"))
        return [p for p in posts if p.name[:10] >= cls.CUTOFF_ISO]

    def test_recent_weekly_digest_briefing_matches_rendered_cards(self):
        """Posts on/after CUTOFF_ISO: briefing claims must match rendered card severity tags."""
        mismatches = []
        for post in self._digest_posts_after_cutoff():
            text = post.read_text(encoding="utf-8")
            claimed = _parse_briefing(text)
            actual = self._count_severity_tags(text)
            for sev, count in claimed.items():
                if count != actual.get(sev, 0):
                    mismatches.append(
                        f"{post.name}: briefing {sev}={count} vs "
                        f"rendered severity tags {sev}={actual.get(sev, 0)}"
                    )
        assert not mismatches, (
            f"Briefing/card severity mismatch in posts on/after {self.CUTOFF_ISO}:\n  - "
            + "\n  - ".join(mismatches)
        )
