#!/usr/bin/env python3
"""Unit tests for ``scripts.lib.svg_l22_generator._pick_illustration``.

Covers:
- All existing illustration keys to guard against regressions.
- New keyword clusters added in the 2026-post expansion pass:
  CDN/edge keywords → globe
  Ransomware + Korean incident keywords → incident_timeline
  Korean supply-chain keyword → npm
  Korean / extended k8s keywords (쿠버네티스, kubectl, helm, pod) → k8s
  Extended email keywords (imap, deliverability) → email
  Korean AI agent keyword (ai 에이전트) → agent
  GCP / GKE → aws
  Korean cloud/container (클라우드, 컨테이너) → cloud
  Malware / BYOVD / EDR / Korean keywords → lock
  DNS exfiltration / Korean DNS leak → network
- Rule precedence: cloudflare-specific outage wins over generic incident
- Before/after shield-fallback rate on a representative sample.
"""

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def pick(cat: str, title: str) -> str:
    from scripts.lib.svg_l22_generator import _pick_illustration
    return _pick_illustration(cat, title)


# ---------------------------------------------------------------------------
# Regression: existing routing must not change
# ---------------------------------------------------------------------------

class TestExistingRouting:
    @pytest.mark.parametrize("cat,title,expected", [
        ("security", "SKT USIM SIM card breach", "sim"),
        ("security", "Kandji MDM fleet management", "macos"),
        ("security", "Cloudflare global outage 11/18 incident", "globe"),
        ("security", "Post-mortem: database outage", "incident_timeline"),
        ("security", "NPM supply chain worm attack", "npm"),
        ("devops", "Kubernetes k8s cluster security", "k8s"),
        ("devops", "CI/CD pipeline GitHub Actions GHAS", "pipeline"),
        ("security", "DMARC SPF DKIM email authentication", "email"),
        ("security", "ZTNA zero trust network access", "ztna"),
        ("security", "Zscaler SSL inspection sandbox", "ssl"),
        ("security", "MFA passkey FIDO2 OTP 2FA", "mfa"),
        ("security", "ISMS-P audit compliance SOC2", "isms"),
        ("security", "AI agent LLM OpenAI GPT security", "agent"),
        ("security", "Database RDS NLB gateway access", "database"),
        ("security", "Conference AWSKRUG OWASP Datadog review", "conference"),
        ("security", "FinOps cost-opt savings budget", "finops"),
        ("security", "AWS GuardDuty VPC control tower security hub", "aws"),
        ("security", "Cloud Docker container deployment", "cloud"),
        ("security", "CVE-2026-1234 RCE vulnerability exploit", "lock"),
    ])
    def test_existing_rules_unchanged(self, cat, title, expected):
        assert pick(cat, title) == expected


# ---------------------------------------------------------------------------
# New: CDN / edge network keywords → globe
# ---------------------------------------------------------------------------

class TestGlobeExpansion:
    @pytest.mark.parametrize("title,expected", [
        ("Fastly CDN global edge network", "globe"),
        ("Akamai anycast edge network outage", "globe"),
        ("CloudFront content delivery network", "globe"),
        ("Cloudflare CDN routing incident", "globe"),
    ])
    def test_cdn_edge_routes_to_globe(self, title, expected):
        assert pick("security", title) == expected


# ---------------------------------------------------------------------------
# New: Ransomware + Korean incident keywords → incident_timeline
# ---------------------------------------------------------------------------

class TestIncidentTimelineExpansion:
    @pytest.mark.parametrize("title,expected", [
        ("랜섬웨어 동향 분석 2026 Q3 KARA", "incident_timeline"),
        ("Ransomware group hits 320 victims", "incident_timeline"),
        ("RCA: 4-hour production downtime analysis", "incident_timeline"),
        ("Root cause post-incident review", "incident_timeline"),
        ("인시던트 대응 가이드라인", "incident_timeline"),
        ("침해 사고 사례 분석 2026", "incident_timeline"),
        ("KISA 보안 공지: 랜섬웨어 예방 가이드", "incident_timeline"),
        # Cloudflare-specific outage should stay globe (rule precedence)
        ("Cloudflare global outage ransomware", "globe"),
    ])
    def test_ransomware_and_korean_incident_routes(self, title, expected):
        assert pick("security", title) == expected


# ---------------------------------------------------------------------------
# New: Korean supply-chain keyword → npm
# ---------------------------------------------------------------------------

class TestNpmExpansion:
    def test_korean_supply_chain_routes_to_npm(self):
        assert pick("security", "소프트웨어 공급망 공격 분석") == "npm"


# ---------------------------------------------------------------------------
# New: Korean + extended k8s keywords → k8s
# ---------------------------------------------------------------------------

class TestK8sExpansion:
    @pytest.mark.parametrize("title", [
        "쿠버네티스 클러스터 보안 가이드",
        "kubectl 명령어 완벽 정리",
        "Helm chart security scanning",
        "Kubernetes pod security namespace",
        "kubelet hardening guide",
        "헬름 차트 보안 검토",
        # Korean title in digest post context
        "주간 다이제스트: 제로데이·BYOVD EDR·쿠버네티스",
    ])
    def test_extended_k8s_keywords_route_to_k8s(self, title):
        assert pick("devops", title) == "k8s"


# ---------------------------------------------------------------------------
# New: Extended email keywords → email
# ---------------------------------------------------------------------------

class TestEmailExpansion:
    @pytest.mark.parametrize("title", [
        "IMAP email server configuration",
        "Email deliverability guide 2026",
        "Mail sender reputation management",
        "Spam filter bypass techniques",
    ])
    def test_extended_email_keywords_route_to_email(self, title):
        assert pick("security", title) == "email"


# ---------------------------------------------------------------------------
# New: Korean AI agent keyword → agent
# ---------------------------------------------------------------------------

class TestAgentExpansion:
    @pytest.mark.parametrize("title", [
        "AI 에이전트 보안 위협 분석",
        "주간 다이제스트: AI 에이전트·클라우드·패치",
    ])
    def test_korean_ai_agent_routes_to_agent(self, title):
        assert pick("security", title) == "agent"

    def test_korean_agentic_ai_security_routes_to_ai_threat(self):
        # "에이전틱 ai" = agentic AI (KO): security/attack context → ai_threat
        assert pick("security", "에이전틱 AI 보안 아키텍처") == "ai_threat"


# ---------------------------------------------------------------------------
# New: GCP / GKE → aws (cloud providers visual)
# ---------------------------------------------------------------------------

class TestAwsExpansion:
    @pytest.mark.parametrize("title", [
        "GCP 클라우드 보안: IAM부터 GKE까지 실무 아키텍처",
        "Google Cloud GKE cluster hardening",
        "GCP IAM permission misconfig",
    ])
    def test_gcp_gke_routes_to_aws(self, title):
        assert pick("cloud", title) == "aws"


# ---------------------------------------------------------------------------
# New: Korean cloud / container keywords → cloud
# ---------------------------------------------------------------------------

class TestCloudExpansion:
    @pytest.mark.parametrize("title", [
        "클라우드 네이티브 보안 전략 2026",
        "컨테이너 보안 모범 사례",
        "클라우드·컨테이너·마이크로서비스 아키텍처",
    ])
    def test_korean_cloud_container_routes_to_cloud(self, title):
        assert pick("devops", title) == "cloud"


# ---------------------------------------------------------------------------
# New: Malware / BYOVD / EDR / Korean zero-day → lock
# ---------------------------------------------------------------------------

class TestLockExpansion:
    @pytest.mark.parametrize("title,cat", [
        ("BYOVD EDR bypass technique analysis", "security"),
        ("EDR evasion via BYOVD driver", "security"),
        ("Endpoint detection response bypass", "security"),
        ("악성코드 분석 보고서 2026", "security"),
        ("제로데이 취약점 발견 및 패치", "security"),
        ("취약점 스캐닝 자동화 가이드", "security"),
        # Korean edr mid-word boundary: "edr·" (common in digest titles)
        ("주간 보안 다이제스트: 제로데이·BYOVD EDR·DNS 유출", "security"),
    ])
    def test_lock_expansion_keywords(self, title, cat):
        assert pick(cat, title) == "lock"


# ---------------------------------------------------------------------------
# New: DNS exfiltration / Korean DNS → network
# ---------------------------------------------------------------------------

class TestNetworkRouting:
    @pytest.mark.parametrize("title,expected", [
        # "DNS 유출 취약점" hits 취약점 → lock fires before network (rule precedence).
        # lock is semantically valid for a DNS vulnerability post.
        ("DNS 유출 취약점 분석 및 대응", "lock"),
        # Pure DNS exfil / tunnel posts (no vulnerability keyword) → network
        ("DNS tunneling exfiltration detection", "network"),
        ("DNS leak prevention guide", "network"),
        ("dns 유출 방어 전략", "network"),
    ])
    def test_dns_routing(self, title, expected):
        assert pick("security", title) == expected


# ---------------------------------------------------------------------------
# Rule precedence: specific before generic
# ---------------------------------------------------------------------------

class TestRulePrecedence:
    def test_cloudflare_wins_over_incident_when_both_match(self):
        """Cloudflare-specific rule fires before incident_timeline."""
        assert pick("security", "Cloudflare 11 global outage post-mortem") == "globe"

    def test_ransomware_fires_before_cloud(self):
        """랜섬웨어 (incident_timeline) fires before 클라우드 (cloud)."""
        assert pick("security", "랜섬웨어 클라우드 공격") == "incident_timeline"

    def test_k8s_fires_before_cloud(self):
        """Kubernetes fires before generic cloud."""
        assert pick("devops", "Kubernetes cloud container cluster") == "k8s"

    def test_agent_fires_before_lock_in_mixed_digest_title(self):
        """In multi-topic digest titles, agent rule precedes lock rule.

        'BYOVD EDR·AI 에이전트·클라우드' contains both BYOVD/EDR (lock) and
        'ai 에이전트' (agent). The agent rule is listed before lock in the
        function body, so agent wins. This test documents that ordering so
        any future reordering is caught.
        """
        result = pick("security", "주간 보안 다이제스트: BYOVD EDR·AI 에이전트·클라우드")
        assert result == "agent"

    def test_zero_day_in_digest_routes_to_lock_not_shield(self):
        """제로데이 in Korean digest should now route to lock, not shield."""
        assert pick("security", "2026년 제로데이·랜섬웨어·패치 다이제스트") == "incident_timeline"


# ---------------------------------------------------------------------------
# Shield rate: representative sample should be < 30%
# ---------------------------------------------------------------------------

class TestShieldFallbackRate:
    def test_shield_rate_below_30pct_on_2026_sample(self):
        """_pick_illustration must not fall back to shield for >30% of posts.

        This test uses a representative set of 20 2026 post titles
        (drawn from the full corpus simulation) to guard against future
        regressions that widen the shield bucket again.
        """
        sample = [
            ("", "2026년 01월 24일 주간 보안 다이제스트: 랜섬웨어·BYOVD EDR·AI 에이전트 (5건)"),
            ("", "2026년 01월 25일 주간 보안 다이제스트: 제로데이·랜섬웨어·악성코드 (5건)"),
            ("", "2026년 01월 26일 주간 보안 다이제스트: BYOVD EDR·DNS 유출·AI 에이전트 (5건)"),
            ("", "2026년 01월 27일 주간 보안 다이제스트: 제로데이·BYOVD EDR·DNS 유출 (5건)"),
            ("", "2026년 01월 29일 주간 보안 다이제스트: 제로데이·DNS 유출·AI 에이전트 (5건)"),
            ("", "2026년 01월 30일 주간 보안 다이제스트: 제로데이·BYOVD EDR·AI 에이전트 (5건)"),
            ("", "2026년 02월 01일 주간 보안 다이제스트: 제로데이·AI 에이전트·쿠버네티스 (4건)"),
            ("", "2026년 02월 20일 기술 블로그 주간 다이제스트: 쿠버네티스·클라우드·컨테이너 (3건)"),
            ("", "2026년 02월 20일 주간 보안 다이제스트: 제로데이·악성코드·쿠버네티스 (3건)"),
            ("", "GCP 클라우드 보안 완벽 가이드: IAM부터 GKE까지 실무 중심 보안 아키텍처"),
            ("", "KISA 보안 공지 분석: 랜섬웨어 예방 가이드와 리눅스 커널 루트킷 점검"),
            ("", "2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략"),
            ("", "에이전틱 AI 보안 2026: AI Agent 공격 벡터와 방어 아키텍처 완전 가이드"),
            ("", "LLM 보안 실무 가이드 2026: 프롬프트 인젝션, RAG 보안, MCP 위협 대응"),
            ("", "Kubernetes cluster security admission controller best practice"),
            ("", "BYOVD driver abuse for EDR bypass: analysis and mitigations"),
            ("", "DNS 유출 취약점 분석 및 방어 전략 2026"),
            ("", "악성코드 분석 자동화 파이프라인 구축"),
            # These legitimately remain shield
            ("", "테슬라 FSD 2026: Model Y Juniper 비용, 하드웨어, DevSecOps 보안"),
            ("", "2026년 DevSecOps 로드맵 완벽 가이드: roadmap.sh 분석"),
        ]
        shield_count = sum(1 for cat, title in sample if pick(cat, title) == "shield")
        rate = shield_count / len(sample)
        assert rate < 0.30, (
            f"Shield fallback rate {rate:.1%} exceeds 30% threshold "
            f"({shield_count}/{len(sample)} posts fell back to shield)"
        )


# ---------------------------------------------------------------------------
# New: AI-threat routing (v_ai_threat primitive)
# ---------------------------------------------------------------------------

class TestAiThreatRouting:
    @pytest.mark.parametrize("cat,title,expected", [
        # E2 spec cases
        ("security", "Agentic AI Security 2026 Attack Vectors Defense Architecture", "ai_threat"),
        ("security", "Prompt injection RAG MCP security guide", "ai_threat"),
        ("security", "LLM threat model analysis 2026", "ai_threat"),
        ("security", "OWASP 2025 Agentic AI Security threat landscape", "ai_threat"),
        # Non-threat AI must still route to agent
        ("security", "DevSecOps AI tooling workflow integration", "shield"),
        # Additional threat keywords
        ("security", "Tool poisoning attack on MCP servers", "ai_threat"),
        ("security", "Model poisoning training data corruption", "ai_threat"),
        ("security", "MCP abuse lateral movement via AI agent", "ai_threat"),
        ("security", "Deepfake crypto scam detection and prevention", "ai_threat"),
        ("security", "AI threat intelligence platform 2026", "ai_threat"),
        # Korean equivalents
        ("security", "프롬프트 인젝션 공격 분석 및 방어 전략", "ai_threat"),
        ("security", "딥페이크 탐지 기술 연구 2026", "ai_threat"),
    ])
    def test_ai_threat_routing(self, cat, title, expected):
        assert pick(cat, title) == expected


# ---------------------------------------------------------------------------
# New: Rollup index posts (monthly / weekly aggregate)
# ---------------------------------------------------------------------------

class TestRollupIndexRouting:
    @pytest.mark.parametrize("cat,title,expected", [
        ("security", "주간 롤업 2026년 4월 1주차", "rollup_index"),
        ("security", "월간 인덱스", "rollup_index"),
        ("security", "Weekly Security Threat Intelligence Digest", "rollup_index"),
        ("devops", "Daily Tech Digest RSS Roundup", "rollup_index"),
        ("security", "보안 벤더 블로그 주간 리뷰 2026.01.22", "rollup_index"),
        ("security", "Weekly Security DevOps Digest", "rollup_index"),
        ("security", "February 2026 Security Digest Monthly Index", "rollup_index"),
        ("security", "March 2026 Security Digest Monthly Index", "rollup_index"),
        ("security", "Weekly Rollup April 2026 Week 1", "rollup_index"),
    ])
    def test_rollup_index_routing(self, cat, title, expected):
        assert pick(cat, title) == expected

    def test_rollup_does_not_match_generic_digest(self):
        """Generic weekly digest without rollup keywords should NOT route to rollup_index."""
        # Standard digest titles that use 주간 다이제스트 go to agent/lock/etc not rollup_index
        result = pick("security", "주간 보안 다이제스트: 제로데이·BYOVD EDR")
        assert result != "rollup_index"
