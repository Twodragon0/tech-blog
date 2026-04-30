#!/usr/bin/env python3
"""Tests for the L20 Hero+2-Card keyword router and theme picker.

Mirrors the style of ``scripts/tests/test_news_templates.py`` and
specifically guards the branch-priority rule from CLAUDE.md:
more specific keywords (``container``, ``docker``, ``ai agent``) must be
checked BEFORE more generic ones (``cve-``, ``ai ``).

API disabling and ``sys.path`` setup are handled by ``conftest.py``.
"""

import pytest

from scripts.news.l20_dispatch import (
    extract_three_stories,
    route_theme,
    route_visual_id,
)


# =====================================================================
# route_visual_id - parametrised happy-path coverage of every bucket
# =====================================================================


class TestRouteVisualIdBuckets:
    """One parametrised case per priority bucket plus a default."""

    @pytest.mark.parametrize(
        "topic,expected",
        [
            # 1. Ransomware bucket
            ("LockBit ransomware hits 320 victims", "ransomware_lock"),
            ("LeakNet wiper deployed against fleet", "ransomware_lock"),
            # 2. Container / k8s bucket
            ("Docker container escape via syscall abuse", "container_escape"),
            ("Kubernetes RBAC privilege escalation chain", "container_escape"),
            ("Harbor registry CVE allows pull abuse", "container_escape"),
            # 3. AI agent bucket
            ("AI agent jailbreak across 5 LLMs", "ai_agent_funnel"),
            ("Copilot agentic prompt injection", "ai_agent_funnel"),
            # 4. Supply chain bucket
            ("Supply chain attack on npm registry", "supply_chain_pipe"),
            ("SBOM gap exposes Helm chart pipeline", "supply_chain_pipe"),
            # 5. Code injection / stealer bucket
            ("Snow Loader infostealer hits CI runners", "code_injection"),
            ("BYOVD EDR bypass campaign", "code_injection"),
            # 6. Hub & spoke / botnet bucket
            ("SOHO router botnet rents DDoS", "hub_spoke"),
            ("APT spear-phishing wave hits banks", "hub_spoke"),
            # 7. Data exfiltration bucket
            ("AWS S3 leak exposes credential set", "data_exfil"),
            ("Session hijack via SSO token leak", "data_exfil"),
            # 8. CVE / generic vuln bucket (catch-all)
            ("CVE-2026-1234 RCE in Redis", "cve_chain"),
            ("Patch Tuesday brings 9.8 CVSS fix", "cve_chain"),
            # Default fallback: empty + nonsense
            ("", "cve_chain"),
            ("totally unrelated banana split", "cve_chain"),
        ],
    )
    def test_each_bucket_routes(self, topic, expected):
        assert route_visual_id(topic) == expected


# =====================================================================
# Branch priority: specific > generic (CLAUDE.md guidance)
# =====================================================================


class TestBranchPriorityConflicts:
    """Catch over-matching: stories that also contain CVE / AI / ai
    keywords MUST still route to the more specific bucket first.
    """

    def test_docker_with_cve_routes_container_not_cve(self):
        # "Docker container escape via CVE-2026-X" must NOT fall into
        # the cve_chain bucket because the container bucket is checked
        # before the CVE bucket.
        topic = "Docker container escape via CVE-2026-9999"
        assert route_visual_id(topic) == "container_escape"

    def test_kubernetes_with_cvss_routes_container(self):
        topic = "Kubernetes admission controller CVSS 9.1 bypass"
        assert route_visual_id(topic) == "container_escape"

    def test_ai_agent_with_cve_routes_ai_agent_not_cve(self):
        topic = "AI agent prompt injection bundled with CVE-2026-1111"
        assert route_visual_id(topic) == "ai_agent_funnel"

    def test_ransomware_with_supply_chain_routes_ransomware(self):
        # Ransomware bucket is BEFORE supply-chain bucket on purpose:
        # the dominant story is the ransomware payload.
        topic = "Ransomware delivered via npm supply chain dropper"
        assert route_visual_id(topic) == "ransomware_lock"

    def test_supply_chain_with_cve_routes_supply_chain(self):
        topic = "Supply chain breach exposes CVE-2026-2222 in trivy scan"
        assert route_visual_id(topic) == "supply_chain_pipe"

    def test_botnet_with_phishing_routes_hub_spoke(self):
        topic = "SOHO botnet phishing campaign refreshes C2"
        assert route_visual_id(topic) == "hub_spoke"

    def test_data_exfil_with_cve_routes_data_exfil(self):
        topic = "Token leak triggers data exfil chain CVE-2026-3333"
        assert route_visual_id(topic) == "data_exfil"


# =====================================================================
# route_theme - severity / index / visual hints
# =====================================================================


class TestRouteTheme:
    @pytest.mark.parametrize(
        "hint,expected",
        [
            ("0", "red"),
            ("1", "blue"),
            ("2", "amber"),
            ("critical", "red"),
            ("HIGH", "red"),
            ("medium", "amber"),
            ("low", "blue"),
            ("ransomware_lock", "red"),
            ("supply_chain_pipe", "amber"),
            ("data_exfil", "blue"),
            ("ai_agent_funnel", "amber"),
            ("", "red"),
            (None, "red"),
        ],
    )
    def test_theme_picks(self, hint, expected):
        assert route_theme(hint) == expected


# =====================================================================
# extract_three_stories - splitter + length contract
# =====================================================================


class TestExtractThreeStories:
    def test_returns_three_dicts(self):
        title = (
            "Weekly digest 2026-04-30: Docker container escape, "
            "AI agent jailbreak, Supply chain breach"
        )
        a, b, c = extract_three_stories(title, "Three highlights this week")
        assert all(isinstance(x, dict) for x in (a, b, c))

    def test_segments_are_short(self):
        # Each story headline must be <= 30 chars per L20 layout budget.
        title = (
            "Docker container escape via privileged mount, "
            "AI agent prompt injection in copilot"
        )
        a, b, _ = extract_three_stories(title, "")
        assert len(a["headline"]) <= 30
        assert len(b["headline"]) <= 30

    def test_pads_when_short(self):
        a, b, c = extract_three_stories("Short title", "")
        # Even a 1-segment title still yields 3 stories.
        assert a["headline"]
        assert b["headline"]
        assert c["headline"]

    def test_strips_digest_prefix(self):
        title = "Tech Security Weekly Digest 2026-04-30: Ransomware, AI, Cloud"
        a, _, _ = extract_three_stories(title, "")
        # Hero headline should be the first real topic, not the prefix.
        assert "Weekly Digest" not in a["headline"]
        assert "Ransomware" in a["headline"] or a["headline"].lower().startswith("ranso")

    def test_uses_excerpt_when_title_short(self):
        title = "Weekly digest 2026-04-30: Ransomware"
        excerpt = "Ransomware spree hits banks, AI agent leak, S3 exfil"
        a, b, c = extract_three_stories(title, excerpt)
        # Three distinct stories should emerge from title + excerpt.
        headlines = {a["headline"], b["headline"], c["headline"]}
        assert len(headlines) >= 2
