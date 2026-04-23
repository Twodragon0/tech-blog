"""Tests that '실무 포인트' variants diversify across articles.

The reviewer flagged that many weekly digests shared the same boilerplate
action point for common branches (e.g., every Bitcoin article returning the
same '시장 변동성' sentence). `_pick_variant` selects deterministically from
a list of phrasings keyed on the article identity, so different articles in
the same keyword branch yield different tips — but the same article always
yields the same tip across regenerations.
"""

from typing import Dict, List

import pytest

from news.content_generator import (
    _generate_ai_analysis_template,
    _generate_contextual_action_point,
    _generate_devops_template,
    _pick_variant,
)


def _item(title: str, category: str = "security", url: str = "") -> Dict:
    return {
        "title": title,
        "summary": title,
        "content": "",
        "category": category,
        "url": url or f"https://example.test/{title.replace(' ', '-')}",
    }


class TestPickVariantDeterminism:
    def test_same_item_yields_same_variant(self):
        variants = ["A", "B", "C", "D", "E"]
        item = _item("stable article")
        first = _pick_variant(item, variants)
        for _ in range(10):
            assert _pick_variant(item, variants) == first

    def test_empty_variants_returns_empty_string(self):
        assert _pick_variant(_item("x"), []) == ""

    def test_single_variant_always_returned(self):
        assert _pick_variant(_item("x"), ["only"]) == "only"


class TestContextualActionDiversity:
    """Different articles in the same keyword branch should not all share one tip."""

    @staticmethod
    def _collect_variants(items: List[Dict]) -> set:
        return {_generate_contextual_action_point(it) for it in items}

    def test_bitcoin_branch_diversifies(self):
        items = [
            _item("Bitcoin surges past 80k mark", category="blockchain"),
            _item("Bitcoin Magazine keynote recap", category="blockchain"),
            _item("비트코인 시세 업데이트 요약", category="blockchain"),
            _item("BTC on-chain analytics roundup", category="blockchain"),
            _item("Bitcoin ETF inflow trend", category="blockchain"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2, (
            f"Bitcoin branch collapsed to single variant across 5 articles: {variants}"
        )

    def test_ransomware_branch_diversifies(self):
        items = [
            _item("Ransomware attack on hospital"),
            _item("LockBit ransomware resurgence in 2026"),
            _item("랜섬웨어 방어 모범 사례"),
            _item("New ransomware variant observed"),
            _item("Ransomware-as-a-Service operator profile"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2, (
            f"Ransomware branch collapsed to one variant: {variants}"
        )

    def test_phishing_branch_diversifies(self):
        items = [
            _item("Phishing campaign targets SaaS users"),
            _item("피싱 공격 탐지 기법"),
            _item("Credential phishing via cloned portals"),
            _item("자격증명 탈취 피싱 증가"),
            _item("Spear phishing against finance teams"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2

    def test_llm_branch_diversifies(self):
        items = [
            _item("GPT-5 architecture preview", category="ai"),
            _item("Claude Haiku 4.5 released", category="ai"),
            _item("Gemini 3 multimodal benchmarks", category="ai"),
            _item("LLM prompt injection survey", category="ai"),
            _item("GPT-4o performance update", category="ai"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2

    def test_supply_chain_branch_diversifies(self):
        items = [
            _item("Supply chain attack via npm package"),
            _item("공급망 공격 SBOM 대응"),
            _item("Dependency confusion campaign"),
            _item("Trivy supply chain breach response"),
            _item("Sonatype supply chain malware report"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2

    @pytest.mark.parametrize(
        "title,category,required_substrings",
        [
            ("Bitcoin keynote", "blockchain", ["피싱", "지갑", "화이트리스트"]),
            ("Ransomware on MSP", "security", ["백업", "복구", "SMB"]),
            ("Phishing surge report", "security", ["MFA", "FIDO2", "조건부"]),
            ("LLM update from vendor", "ai", ["LLM", "모델", "프롬프트", "리덕션"]),
        ],
    )
    def test_branch_variants_contain_relevant_terminology(
        self, title, category, required_substrings
    ):
        """Every variant in a branch must include at least one expected keyword."""
        # Generate tips for 10 slightly different titles — must cover >=2 unique variants
        items = [_item(f"{title} {i}", category=category) for i in range(10)]
        unique = {_generate_contextual_action_point(it) for it in items}
        assert len(unique) >= 2, f"Branch produced single variant for {title}"
        for tip in unique:
            assert any(
                sub in tip for sub in required_substrings
            ), f"Variant missing expected terminology ({required_substrings}): {tip}"


def _ai_item(title: str, url: str = "") -> Dict:
    return {
        "title": title,
        "summary": title,
        "url": url or f"https://example.test/{title.replace(' ', '-')}",
    }


def _devops_item(title: str, url: str = "") -> Dict:
    return {
        "title": title,
        "summary": title,
        "url": url or f"https://example.test/{title.replace(' ', '-')}",
    }


class TestAiTemplateDiversity:
    """5 different articles in the same AI branch must produce >=2 unique variants."""

    @staticmethod
    def _collect(items):
        return {_generate_ai_analysis_template(it) for it in items}

    def test_agent_branch_diversifies(self):
        items = [
            _ai_item("New AI Agent Framework Released alpha"),
            _ai_item("Agentic system security review beta"),
            _ai_item("에이전트 기반 자동화 플랫폼 gamma"),
            _ai_item("Multi-agent orchestration security delta"),
            _ai_item("Agent tool-use permission hardening epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"agent branch collapsed to single variant: {len(unique)} unique"
        )

    def test_llm_branch_diversifies(self):
        items = [
            _ai_item("LLM Security Best Practices alpha"),
            _ai_item("GPT model deployment security beta"),
            _ai_item("Claude prompt injection research gamma"),
            _ai_item("Gemini API key rotation delta"),
            _ai_item("Foundation model serving security epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"llm branch collapsed to single variant: {len(unique)} unique"
        )

    def test_gpu_branch_diversifies(self):
        items = [
            _ai_item("GPU cluster security vulnerabilities alpha"),
            _ai_item("NVIDIA H100 infrastructure hardening beta"),
            _ai_item("AI factory compute security gamma"),
            _ai_item("Training cluster access control delta"),
            _ai_item("Large-scale AI infra deployment epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"gpu branch collapsed to single variant: {len(unique)} unique"
        )

    def test_simulation_branch_diversifies(self):
        items = [
            _ai_item("AI Simulation for infrastructure testing alpha"),
            _ai_item("Digital twin network simulation beta"),
            _ai_item("시뮬레이션 기반 보안 검증 gamma"),
            _ai_item("Cost optimize AI inference pipelines delta"),
            _ai_item("AI workload optimization security epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"simulation branch collapsed to single variant: {len(unique)} unique"
        )

    def test_attack_branch_diversifies(self):
        items = [
            _ai_item("New attack vector using AI systems alpha"),
            _ai_item("AI threat detection platform beta"),
            _ai_item("공격 그룹 분석 및 AI 대응 gamma"),
            _ai_item("Adversarial malware detection delta"),
            _ai_item("AI-powered threat intelligence epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"attack branch collapsed to single variant: {len(unique)} unique"
        )


class TestDevopsTemplateDiversity:
    """5 different articles in the same DevOps branch must produce >=2 unique variants."""

    @staticmethod
    def _collect(items):
        return {_generate_devops_template(it) for it in items}

    def test_container_branch_diversifies(self):
        items = [
            _devops_item("Docker security best practices alpha"),
            _devops_item("Container runtime hardening guide beta"),
            _devops_item("컨테이너 보안 취약점 분석 gamma"),
            _devops_item("Docker image scanning automation delta"),
            _devops_item("Container network isolation epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"container branch collapsed to single variant: {len(unique)} unique"
        )

    def test_rbac_branch_diversifies(self):
        items = [
            _devops_item("Kubernetes RBAC hardening guide alpha"),
            _devops_item("OPA gatekeeper policy enforcement beta"),
            _devops_item("Pod Security Admission restricted gamma"),
            _devops_item("Admission controller webhook TLS delta"),
            _devops_item("PSA restricted profile migration epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"rbac branch collapsed to single variant: {len(unique)} unique"
        )

    def test_image_branch_diversifies(self):
        items = [
            _devops_item("OCI image signing with cosign alpha"),
            _devops_item("Container registry access control beta"),
            _devops_item("sigstore supply chain verification gamma"),
            _devops_item("SBOM image vulnerability tracking delta"),
            _devops_item("Private registry scan policy epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"image branch collapsed to single variant: {len(unique)} unique"
        )

    def test_cicd_branch_diversifies(self):
        items = [
            _devops_item("CI/CD pipeline security hardening alpha"),
            _devops_item("GitHub Actions supply chain attack beta"),
            _devops_item("Jenkins plugin vulnerability gamma"),
            _devops_item("배포 파이프라인 시크릿 관리 delta"),
            _devops_item("Pipeline secret rotation automation epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"cicd branch collapsed to single variant: {len(unique)} unique"
        )

    def test_kubernetes_branch_diversifies(self):
        items = [
            _devops_item("k8s cluster security audit alpha"),
            _devops_item("Kubernetes CIS benchmark compliance beta"),
            _devops_item("CNCF landscape new additions gamma"),
            _devops_item("KCD Seoul 2024 k8s security delta"),
            _devops_item("Kubernetes API server hardening epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"kubernetes branch collapsed to single variant: {len(unique)} unique"
        )

    def test_database_branch_diversifies(self):
        items = [
            _devops_item("Redis security hardening guide alpha"),
            _devops_item("PostgreSQL database access control beta"),
            _devops_item("SQL injection prevention in production gamma"),
            _devops_item("Valkey cache encryption setup delta"),
            _devops_item("데이터베이스 감사 로그 설정 epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"database branch collapsed to single variant: {len(unique)} unique"
        )

    def test_mobile_branch_diversifies(self):
        items = [
            _devops_item("Flutter mobile security best practices alpha"),
            _devops_item("iOS certificate pinning implementation beta"),
            _devops_item("React Native API key exposure gamma"),
            _devops_item("Android app data protection delta"),
            _devops_item("모바일 앱 개인정보 처리 정책 epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"mobile branch collapsed to single variant: {len(unique)} unique"
        )

    def test_network_branch_diversifies(self):
        items = [
            _devops_item("Network segmentation zero trust alpha"),
            _devops_item("Firewall rule optimization guide beta"),
            _devops_item("네트워크 모니터링 강화 방안 gamma"),
            _devops_item("DNS tunneling detection network delta"),
            _devops_item("VPN firmware patch network security epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"network branch collapsed to single variant: {len(unique)} unique"
        )

    def test_serverless_branch_diversifies(self):
        items = [
            _devops_item("Lambda function IAM role hardening alpha"),
            _devops_item("Cloud Run serverless security review beta"),
            _devops_item("Cloud Functions secret injection gamma"),
            _devops_item("Serverless VPC connector security delta"),
            _devops_item("Function cold start secret delay epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"serverless branch collapsed to single variant: {len(unique)} unique"
        )

    def test_bigquery_branch_diversifies(self):
        items = [
            _devops_item("BigQuery row-level security setup alpha"),
            _devops_item("Data warehouse ETL pipeline security beta"),
            _devops_item("Analytics lakehouse PII masking gamma"),
            _devops_item("데이터 큐레이션 감사 정책 delta"),
            _devops_item("Iceberg table access control epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"bigquery branch collapsed to single variant: {len(unique)} unique"
        )


class TestAiTemplateDiversityExtra:
    """Additional diversity tests for newly-variant-ized AI branches."""

    @staticmethod
    def _collect(items):
        return {_generate_ai_analysis_template(it) for it in items}

    def test_coding_branch_diversifies(self):
        items = [
            _ai_item("Copilot code generation security review alpha"),
            _ai_item("VS Code AI coding assistant vulnerabilities beta"),
            _ai_item("AI 코딩 도구 보안 가이드라인 gamma"),
            _ai_item("Cursor IDE secret detection delta"),
            _ai_item("Code generation SAST gate enforcement epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"coding branch collapsed to single variant: {len(unique)} unique"
        )

    def test_open_source_branch_diversifies(self):
        items = [
            _ai_item("HuggingFace model CVE security alert alpha"),
            _ai_item("Ollama open source model license review beta"),
            _ai_item("오픈소스 AI 모델 공급망 보안 gamma"),
            _ai_item("HuggingFace model integrity verification delta"),
            _ai_item("Community AI model security audit epsilon"),
        ]
        unique = self._collect(items)
        assert len(unique) >= 2, (
            f"open_source branch collapsed to single variant: {len(unique)} unique"
        )
