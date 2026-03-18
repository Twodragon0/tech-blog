#!/usr/bin/env python3
"""Unit tests for news template generation functions in auto_publish_news.py."""
import sys
from pathlib import Path

# Add scripts directory to path so auto_publish_news can be imported directly
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from auto_publish_news import (
    _generate_ai_analysis_template,
    _generate_contextual_action_point,
    _generate_devops_template,
    _generate_security_analysis_template,
    _generate_security_brief_template,
)

# ---------------------------------------------------------------------------
# Banned phrases - old generic text that must NEVER appear in any branch
# ---------------------------------------------------------------------------
BANNED_PHRASES = [
    "팀 내 기술 동향 공유 및 도입 로드맵 논의",
    "팀 내 기술 공유 및 도입 로드맵 논의",
    "관련 AI/ML 기술의 자사 적용 가능성 및 보안 영향 평가",
]


# ===========================================================================
# Helpers
# ===========================================================================

def _item(title: str = "", summary: str = "") -> dict:
    """Build a minimal news item dict."""
    return {"title": title, "summary": summary}


def _assert_no_banned(text: str, label: str = "") -> None:
    """Fail the test if any banned phrase appears in *text*."""
    for phrase in BANNED_PHRASES:
        assert phrase not in text, (
            f"Banned phrase found{f' in {label}' if label else ''}: {phrase!r}"
        )


# ===========================================================================
# _generate_ai_analysis_template
# ===========================================================================

class TestGenerateAiAnalysisTemplate:
    """Tests for _generate_ai_analysis_template()."""

    # ------------------------------------------------------------------
    # Branch 1: agent / agentic
    # ------------------------------------------------------------------
    def test_agent_keyword_in_title(self):
        item = _item(title="New AI Agent Framework Released")
        result = _generate_ai_analysis_template(item)
        assert "에이전트" in result or "agent" in result.lower()
        assert "도구 호출 권한" in result
        assert "Human-in-the-Loop" in result

    def test_agentic_keyword_in_summary(self):
        item = _item(summary="This agentic system can autonomously execute tasks")
        result = _generate_ai_analysis_template(item)
        assert "도구 호출 권한" in result

    def test_agent_korean_keyword(self):
        item = _item(title="에이전트 기반 자동화 시스템")
        result = _generate_ai_analysis_template(item)
        assert "도구 호출 권한" in result

    # ------------------------------------------------------------------
    # Branch 2: llm / gpt / claude / model
    # ------------------------------------------------------------------
    def test_llm_keyword(self):
        item = _item(title="LLM Security Best Practices")
        result = _generate_ai_analysis_template(item)
        assert "LLM 입출력" in result
        assert "프롬프트 인젝션" in result

    def test_gpt_keyword(self):
        item = _item(summary="GPT-4 achieves new benchmark results")
        result = _generate_ai_analysis_template(item)
        assert "LLM 입출력" in result

    def test_claude_keyword(self):
        item = _item(title="Claude model capabilities update")
        result = _generate_ai_analysis_template(item)
        assert "프롬프트 인젝션" in result

    def test_model_keyword(self):
        item = _item(summary="Foundation model training improvements")
        result = _generate_ai_analysis_template(item)
        assert "LLM 입출력" in result

    # ------------------------------------------------------------------
    # Branch 3: gpu / nvidia / factory / compute / training
    # ------------------------------------------------------------------
    def test_gpu_keyword(self):
        item = _item(title="GPU cluster security vulnerabilities")
        result = _generate_ai_analysis_template(item)
        assert "GPU 클러스터" in result
        assert "접근 제어" in result

    def test_nvidia_keyword(self):
        item = _item(summary="NVIDIA announces new H100 factory setup")
        result = _generate_ai_analysis_template(item)
        assert "GPU 클러스터" in result

    def test_factory_keyword(self):
        item = _item(title="AI Factory infrastructure deployment")
        result = _generate_ai_analysis_template(item)
        assert "AI 인프라" in result or "GPU 클러스터" in result

    def test_compute_keyword(self):
        item = _item(summary="New compute architecture for AI workloads")
        result = _generate_ai_analysis_template(item)
        assert "GPU 클러스터" in result

    def test_training_keyword(self):
        item = _item(title="Distributed training optimization techniques")
        result = _generate_ai_analysis_template(item)
        assert "GPU 클러스터" in result

    # ------------------------------------------------------------------
    # Branch 4: simulation / optimize
    # ------------------------------------------------------------------
    def test_simulation_keyword(self):
        item = _item(title="AI Simulation for infrastructure testing")
        result = _generate_ai_analysis_template(item)
        assert "시뮬레이션" in result
        assert "최적화" in result or "ROI" in result

    def test_simulation_korean_keyword(self):
        item = _item(title="시뮬레이션 기반 보안 검증 시스템")
        result = _generate_ai_analysis_template(item)
        assert "시뮬레이션" in result

    def test_optimize_keyword(self):
        item = _item(summary="Cost optimize AI inference pipelines")
        result = _generate_ai_analysis_template(item)
        assert "최적화" in result or "ROI" in result

    def test_digital_twin_keyword(self):
        item = _item(title="Digital twin for network simulation")
        result = _generate_ai_analysis_template(item)
        assert "시뮬레이션" in result

    # ------------------------------------------------------------------
    # Branch 5: attack / threat / malware
    # ------------------------------------------------------------------
    def test_attack_keyword(self):
        item = _item(title="New attack vector using AI-generated malware")
        result = _generate_ai_analysis_template(item)
        assert "위협 탐지" in result
        assert "Adversarial Attack" in result

    def test_threat_keyword(self):
        item = _item(summary="Emerging threat landscape in AI systems")
        result = _generate_ai_analysis_template(item)
        assert "위협 탐지" in result

    def test_malware_keyword(self):
        item = _item(title="AI-powered malware detection techniques")
        result = _generate_ai_analysis_template(item)
        assert "위협 탐지" in result or "Adversarial Attack" in result

    def test_attack_korean_keyword(self):
        item = _item(title="공격 그룹 분석 및 대응 방안")
        result = _generate_ai_analysis_template(item)
        assert "위협 탐지" in result

    def test_threat_korean_keyword(self):
        item = _item(summary="AI 기반 위협 인텔리전스 플랫폼 도입")
        result = _generate_ai_analysis_template(item)
        assert "위협 탐지" in result

    # ------------------------------------------------------------------
    # Branch 6: fallback (no matching keywords)
    # ------------------------------------------------------------------
    def test_fallback_no_keywords(self):
        item = _item(title="Quarterly earnings report", summary="Revenue up 10%")
        result = _generate_ai_analysis_template(item)
        assert "데이터 파이프라인" in result
        assert "네트워크 격리" in result

    def test_fallback_empty_item(self):
        item = _item()
        result = _generate_ai_analysis_template(item)
        assert "데이터 파이프라인" in result

    # ------------------------------------------------------------------
    # Common structure checks
    # ------------------------------------------------------------------
    def test_always_contains_header(self):
        for item in [
            _item(title="agent system"),
            _item(title="gpt benchmark"),
            _item(title="gpu cluster"),
            _item(title="simulation"),
            _item(title="attack vector"),
            _item(),
        ]:
            result = _generate_ai_analysis_template(item)
            assert "#### 실무 적용 포인트" in result

    def test_always_has_three_bullets(self):
        items = [
            _item(title="agent system"),
            _item(title="gpt benchmark"),
            _item(title="gpu cluster"),
            _item(title="simulation"),
            _item(title="attack vector"),
            _item(),
        ]
        for item in items:
            result = _generate_ai_analysis_template(item)
            bullet_count = result.count("\n- ")
            assert bullet_count == 3, (
                f"Expected 3 bullets, got {bullet_count} for title={item.get('title')!r}"
            )

    # ------------------------------------------------------------------
    # Anti-regression: no banned phrases in any branch
    # ------------------------------------------------------------------
    def test_no_banned_phrases_agent_branch(self):
        result = _generate_ai_analysis_template(_item(title="AI agent framework"))
        _assert_no_banned(result, "agent branch")

    def test_no_banned_phrases_llm_branch(self):
        result = _generate_ai_analysis_template(_item(title="LLM security"))
        _assert_no_banned(result, "llm branch")

    def test_no_banned_phrases_gpu_branch(self):
        result = _generate_ai_analysis_template(_item(title="GPU infrastructure"))
        _assert_no_banned(result, "gpu branch")

    def test_no_banned_phrases_simulation_branch(self):
        result = _generate_ai_analysis_template(_item(title="simulation optimize"))
        _assert_no_banned(result, "simulation branch")

    def test_no_banned_phrases_attack_branch(self):
        result = _generate_ai_analysis_template(_item(title="attack threat"))
        _assert_no_banned(result, "attack branch")

    def test_no_banned_phrases_fallback_branch(self):
        result = _generate_ai_analysis_template(_item(title="quarterly report"))
        _assert_no_banned(result, "fallback branch")


# ===========================================================================
# _generate_devops_template
# ===========================================================================

class TestGenerateDevopsTemplate:
    """Tests for _generate_devops_template()."""

    # ------------------------------------------------------------------
    # Branch: None input (early return)
    # ------------------------------------------------------------------
    def test_none_returns_non_generic_devops(self):
        result = _generate_devops_template(None)
        assert "#### 실무 적용 포인트" in result
        # Must contain operational bullets, not old generic text
        assert "보안 구성 검증 자동화" in result or "IaC" in result or "변경 관리" in result

    def test_none_no_banned_phrases(self):
        result = _generate_devops_template(None)
        _assert_no_banned(result, "None branch")

    # ------------------------------------------------------------------
    # Branch: docker / container
    # ------------------------------------------------------------------
    def test_docker_keyword(self):
        item = _item(title="Docker security best practices 2024")
        result = _generate_devops_template(item)
        assert "컨테이너" in result
        assert "이미지" in result or "런타임" in result

    def test_container_keyword(self):
        item = _item(summary="container runtime security hardening")
        result = _generate_devops_template(item)
        assert "컨테이너" in result

    def test_container_korean_keyword(self):
        item = _item(title="컨테이너 보안 취약점 발견")
        result = _generate_devops_template(item)
        assert "컨테이너" in result

    # ------------------------------------------------------------------
    # Branch: kubernetes / k8s / kcd / cncf
    # ------------------------------------------------------------------
    def test_kubernetes_keyword(self):
        item = _item(title="Kubernetes RBAC hardening guide")
        result = _generate_devops_template(item)
        assert "Kubernetes" in result or "RBAC" in result

    def test_k8s_keyword(self):
        item = _item(summary="k8s cluster security audit findings")
        result = _generate_devops_template(item)
        assert "Kubernetes" in result or "RBAC" in result

    def test_kcd_keyword(self):
        item = _item(title="KCD Seoul 2024 recap")
        result = _generate_devops_template(item)
        assert "Kubernetes" in result or "커뮤니티" in result

    def test_cncf_keyword(self):
        item = _item(summary="CNCF landscape new additions")
        result = _generate_devops_template(item)
        assert "Kubernetes" in result or "RBAC" in result

    # ------------------------------------------------------------------
    # Branch: ci/cd / pipeline / github action / jenkins / 배포
    # ------------------------------------------------------------------
    def test_cicd_keyword(self):
        item = _item(title="ci/cd pipeline security hardening")
        result = _generate_devops_template(item)
        assert "CI/CD" in result
        assert "시크릿" in result or "토큰" in result

    def test_pipeline_keyword(self):
        item = _item(summary="pipeline security scanning integration")
        result = _generate_devops_template(item)
        assert "CI/CD" in result

    def test_github_action_keyword(self):
        item = _item(title="github action supply chain attack")
        result = _generate_devops_template(item)
        assert "CI/CD" in result or "Actions" in result

    def test_jenkins_keyword(self):
        item = _item(summary="jenkins plugin vulnerability discovered")
        result = _generate_devops_template(item)
        assert "CI/CD" in result

    def test_deploy_korean_keyword(self):
        item = _item(title="배포 파이프라인 보안 강화 방안")
        result = _generate_devops_template(item)
        assert "CI/CD" in result

    # ------------------------------------------------------------------
    # Branch: service mesh / istio / envoy / 네트워크
    # ------------------------------------------------------------------
    def test_service_mesh_keyword(self):
        item = _item(title="service mesh mTLS configuration")
        result = _generate_devops_template(item)
        assert "mTLS" in result or "서비스 메시" in result

    def test_service_mesh_korean_keyword(self):
        item = _item(title="서비스 메시 도입 사례")
        result = _generate_devops_template(item)
        assert "mTLS" in result or "서비스 메시" in result

    def test_istio_keyword(self):
        item = _item(summary="istio security policy configuration guide")
        result = _generate_devops_template(item)
        assert "mTLS" in result or "서비스 메시" in result

    def test_envoy_keyword(self):
        item = _item(title="envoy proxy security update")
        result = _generate_devops_template(item)
        assert "mTLS" in result or "서비스 메시" in result

    def test_network_korean_keyword(self):
        item = _item(title="네트워크 보안 아키텍처 설계")
        result = _generate_devops_template(item)
        assert "네트워크" in result

    # ------------------------------------------------------------------
    # Branch: kubecon / conference / summit
    # ------------------------------------------------------------------
    def test_kubecon_keyword(self):
        item = _item(title="KubeCon North America 2024 highlights")
        result = _generate_devops_template(item)
        assert "컨퍼런스" in result or "보안 프레임워크" in result

    def test_conference_keyword(self):
        item = _item(summary="annual security conference keynote speakers")
        result = _generate_devops_template(item)
        assert "컨퍼런스" in result or "보안 프레임워크" in result

    def test_summit_keyword(self):
        item = _item(title="Cloud Security Summit 2024")
        result = _generate_devops_template(item)
        assert "컨퍼런스" in result or "보안 프레임워크" in result

    def test_conference_korean_keyword(self):
        item = _item(title="보안 컨퍼런스 주요 발표 정리")
        result = _generate_devops_template(item)
        assert "컨퍼런스" in result or "보안 프레임워크" in result

    def test_event_korean_keyword(self):
        item = _item(title="행사 참가 후기 및 주요 세션 리뷰")
        result = _generate_devops_template(item)
        assert "컨퍼런스" in result or "보안 프레임워크" in result

    # ------------------------------------------------------------------
    # Branch: fallback (else)
    # ------------------------------------------------------------------
    def test_fallback_drift_detection(self):
        item = _item(title="General infrastructure update notes")
        result = _generate_devops_template(item)
        assert "드리프트" in result or "취약점 데이터베이스" in result

    def test_fallback_empty_item(self):
        item = _item()
        result = _generate_devops_template(item)
        assert "드리프트" in result or "취약점 데이터베이스" in result

    # ------------------------------------------------------------------
    # Common structure checks
    # ------------------------------------------------------------------
    def test_always_contains_header_with_item(self):
        cases = [
            _item(title="docker security"),
            _item(title="kubernetes cluster"),
            _item(title="ci/cd pipeline"),
            _item(title="service mesh"),
            _item(title="kubecon event"),
            _item(title="random topic"),
        ]
        for item in cases:
            result = _generate_devops_template(item)
            assert "#### 실무 적용 포인트" in result, (
                f"Missing header for title={item.get('title')!r}"
            )

    def test_none_input_contains_header(self):
        result = _generate_devops_template(None)
        assert "#### 실무 적용 포인트" in result

    # ------------------------------------------------------------------
    # Anti-regression: no banned phrases in any branch
    # ------------------------------------------------------------------
    def test_no_banned_phrases_none_branch(self):
        _assert_no_banned(_generate_devops_template(None), "None branch")

    def test_no_banned_phrases_docker_branch(self):
        _assert_no_banned(_generate_devops_template(_item(title="docker container")), "docker branch")

    def test_no_banned_phrases_k8s_branch(self):
        _assert_no_banned(_generate_devops_template(_item(title="kubernetes cluster")), "k8s branch")

    def test_no_banned_phrases_cicd_branch(self):
        _assert_no_banned(_generate_devops_template(_item(title="ci/cd pipeline")), "ci/cd branch")

    def test_no_banned_phrases_mesh_branch(self):
        _assert_no_banned(_generate_devops_template(_item(title="service mesh istio")), "mesh branch")

    def test_no_banned_phrases_conference_branch(self):
        _assert_no_banned(_generate_devops_template(_item(title="kubecon summit")), "conference branch")

    def test_no_banned_phrases_fallback_branch(self):
        _assert_no_banned(_generate_devops_template(_item(title="random topic")), "fallback branch")


# ===========================================================================
# Cross-function anti-regression sweep
# ===========================================================================

class TestAntiRegressionBannedPhrases:
    """Exhaustive check that no branch in either function emits the old generic text."""

    AI_ITEMS = [
        _item(title="AI agent system"),
        _item(title="LLM gpt claude model"),
        _item(title="GPU nvidia factory compute training"),
        _item(title="simulation digital twin optimize"),
        _item(title="attack threat malware"),
        _item(title="no matching keywords at all"),
        _item(),
    ]

    DEVOPS_ITEMS = [
        None,
        _item(title="docker container"),
        _item(title="kubernetes k8s kcd cncf"),
        _item(title="ci/cd pipeline jenkins"),
        _item(title="service mesh istio envoy"),
        _item(title="kubecon conference summit"),
        _item(title="no matching keywords at all"),
        _item(),
    ]

    def test_ai_template_all_branches(self):
        for item in self.AI_ITEMS:
            result = _generate_ai_analysis_template(item)
            for phrase in BANNED_PHRASES:
                assert phrase not in result, (
                    f"Banned phrase {phrase!r} found in ai template for item={item!r}"
                )

    def test_devops_template_all_branches(self):
        for item in self.DEVOPS_ITEMS:
            result = _generate_devops_template(item)
            for phrase in BANNED_PHRASES:
                assert phrase not in result, (
                    f"Banned phrase {phrase!r} found in devops template for item={item!r}"
                )


# ===========================================================================
# _generate_contextual_action_point
# ===========================================================================

class TestGenerateContextualActionPoint:
    """Tests for inline '실무 포인트' generation."""

    def _item(self, title="", summary="", category="tech"):
        return {"title": title, "summary": summary, "category": category}

    # --- Blockchain branches ---
    def test_blockchain_hack_keyword(self):
        result = _generate_contextual_action_point(
            self._item("Bitcoin exchange hack", category="blockchain")
        )
        assert "IoC" in result or "방어" in result

    def test_blockchain_regulation_keyword(self):
        result = _generate_contextual_action_point(
            self._item("SEC 규제 변화", category="blockchain")
        )
        assert "컴플라이언스" in result or "법무" in result

    def test_blockchain_defi_keyword(self):
        result = _generate_contextual_action_point(
            self._item("DeFi protocol exploit", category="blockchain")
        )
        # hack keyword should match first (higher priority)
        assert "IoC" in result or "스마트 컨트랙트" in result

    def test_blockchain_defi_swap(self):
        result = _generate_contextual_action_point(
            self._item("Uniswap 스왑 기능 업데이트", category="blockchain")
        )
        assert "스마트 컨트랙트" in result

    def test_blockchain_conference(self):
        result = _generate_contextual_action_point(
            self._item("Bitcoin 2026 컨퍼런스 연사", category="blockchain")
        )
        assert "공식 채널" in result or "피싱" in result

    def test_blockchain_bitcoin(self):
        result = _generate_contextual_action_point(
            self._item("Bitcoin price DCA analysis", category="blockchain")
        )
        assert "피싱 도메인" in result or "출금" in result

    def test_blockchain_ethereum_stablecoin(self):
        result = _generate_contextual_action_point(
            self._item("스테이블코인 시장 동향", category="blockchain")
        )
        assert "트랜잭션 모니터링" in result or "접근 제어" in result

    def test_blockchain_fallback(self):
        result = _generate_contextual_action_point(
            self._item("NFT marketplace trends", category="blockchain")
        )
        assert "프로토콜" in result or "스마트 컨트랙트" in result

    # --- Security branches ---
    def test_security_ransomware(self):
        result = _generate_contextual_action_point(
            self._item("New ransomware variant", category="security")
        )
        assert "백업" in result or "격리" in result

    def test_security_cve(self):
        result = _generate_contextual_action_point(
            self._item("CVE-2026-12345 critical vuln", category="security")
        )
        assert "CVE" in result or "패치" in result

    # --- AI branches ---
    def test_ai_agent(self):
        result = _generate_contextual_action_point(
            self._item("AI 에이전트 보안", category="ai")
        )
        assert "Agent" in result or "권한" in result

    def test_ai_model(self):
        result = _generate_contextual_action_point(
            self._item("New LLM model release", category="ai")
        )
        assert "적용" in result or "트레이드오프" in result

    # --- Cloud/DevOps branches ---
    def test_cloud_k8s(self):
        result = _generate_contextual_action_point(
            self._item("Kubernetes security update", category="kubernetes")
        )
        assert "클러스터" in result

    def test_cloud_aws(self):
        result = _generate_contextual_action_point(
            self._item("AWS new service", category="cloud")
        )
        assert "클라우드" in result or "인프라" in result

    # --- Anti-regression: no old generic phrases ---
    def test_no_generic_blockchain_phrase(self):
        """Blockchain items should never return the old generic phrase."""
        test_items = [
            self._item("Bitcoin price analysis", category="blockchain"),
            self._item("Ethereum DeFi update", category="blockchain"),
            self._item("Crypto regulation news", category="blockchain"),
            self._item("NFT marketplace", category="blockchain"),
        ]
        banned = "가격 변동에 따른 보안 위협(피싱/스캠) 증가에 대비하세요."
        for item in test_items:
            result = _generate_contextual_action_point(item)
            assert result != banned, f"Got banned phrase for: {item['title']}"


# ===========================================================================
# _generate_security_brief_template
# ===========================================================================

class TestGenerateSecurityBriefTemplate:
    """Tests for security brief '권장 조치' generation."""

    def _item(self, title="", summary="", content=""):
        return {"title": title, "summary": summary, "content": content}

    # --- None input ---
    def test_none_returns_default(self):
        result = _generate_security_brief_template(None)
        assert "권장 조치" in result
        assert "관련 시스템 목록 확인" in result

    # --- Ransomware branch ---
    def test_ransomware_keyword(self):
        result = _generate_security_brief_template(self._item("New ransomware variant detected"))
        assert "백업" in result
        assert "인시던트 대응" in result

    def test_ransomware_korean(self):
        result = _generate_security_brief_template(self._item("신규 랜섬웨어 공격 캠페인"))
        assert "백업" in result

    def test_encrypt_keyword(self):
        result = _generate_security_brief_template(self._item("File encryption malware spreads"))
        assert "백업" in result

    # --- Authentication branch ---
    def test_authentication_keyword(self):
        result = _generate_security_brief_template(self._item("Authentication bypass vulnerability"))
        assert "인증" in result or "Credential" in result

    def test_mfa_keyword(self):
        result = _generate_security_brief_template(self._item("MFA fatigue attack campaign"))
        assert "MFA" in result or "인증" in result

    def test_auth_bypass_korean(self):
        result = _generate_security_brief_template(self._item("인증 우회 취약점 발견"))
        assert "인증" in result

    def test_credential_keyword(self):
        result = _generate_security_brief_template(self._item("Credential stuffing attack"))
        assert "인증 정보" in result or "Credential" in result

    def test_sso_keyword(self):
        result = _generate_security_brief_template(self._item("SSO provider compromise"))
        assert "SSO" in result or "인증" in result

    # --- Supply chain branch ---
    def test_supply_chain_keyword(self):
        result = _generate_security_brief_template(self._item("Supply chain attack on npm"))
        assert "의존성" in result or "SBOM" in result

    def test_dependency_keyword(self):
        result = _generate_security_brief_template(self._item("Malicious dependency found"))
        assert "의존성" in result

    def test_npm_keyword(self):
        result = _generate_security_brief_template(self._item("npm package backdoor"))
        assert "의존성" in result or "npm" in result

    def test_pypi_keyword(self):
        result = _generate_security_brief_template(self._item("PyPI package malware"))
        assert "의존성" in result or "pip" in result

    def test_sbom_keyword(self):
        result = _generate_security_brief_template(self._item("SBOM requirements update"))
        assert "SBOM" in result

    def test_supply_chain_korean(self):
        result = _generate_security_brief_template(self._item("공급망 공격 증가"))
        assert "의존성" in result

    # --- Default/fallback ---
    def test_fallback_generic(self):
        result = _generate_security_brief_template(self._item("Some generic security news"))
        assert "권장 조치" in result
        assert "관련 시스템 목록 확인" in result

    # --- All branches return '권장 조치' header ---
    def test_all_branches_have_header(self):
        items = [
            None,
            self._item("ransomware attack"),
            self._item("authentication bypass"),
            self._item("supply chain attack"),
            self._item("generic news"),
        ]
        for item in items:
            result = _generate_security_brief_template(item)
            assert "권장 조치" in result, f"Missing header for: {item}"

    # --- All branches return 4 bullet points ---
    def test_all_branches_have_four_bullets(self):
        items = [
            None,
            self._item("ransomware attack"),
            self._item("authentication bypass"),
            self._item("supply chain attack"),
            self._item("generic news"),
        ]
        for item in items:
            result = _generate_security_brief_template(item)
            bullets = [line for line in result.strip().split("\n") if line.strip().startswith("- ")]
            assert len(bullets) == 4, f"Expected 4 bullets, got {len(bullets)} for: {item}"

    # --- Missing keyword edge cases ---
    def test_password_keyword(self):
        result = _generate_security_brief_template(
            self._item("Password spray attack targeting enterprises")
        )
        assert "인증" in result or "Credential" in result

    def test_login_keyword(self):
        result = _generate_security_brief_template(
            self._item("Brute force login attempts detected")
        )
        assert "인증" in result or "Credential" in result

    def test_package_keyword(self):
        result = _generate_security_brief_template(
            self._item("Malicious package published to registry")
        )
        assert "의존성" in result or "SBOM" in result

    def test_maven_keyword(self):
        result = _generate_security_brief_template(
            self._item("Maven repository compromise alert")
        )
        assert "의존성" in result or "SBOM" in result


# ===========================================================================
# _generate_security_analysis_template
# ===========================================================================

class TestGenerateSecurityAnalysisTemplate:
    """Tests for Critical security news '위협 분석' generation."""

    def _item(self, title="", summary="", content="", category="security"):
        return {"title": title, "summary": summary, "content": content, "category": category}

    # --- Structure tests ---
    def test_always_has_threat_analysis_header(self):
        result = _generate_security_analysis_template(self._item("Generic vuln"))
        assert "위협 분석" in result

    def test_always_has_action_items(self):
        result = _generate_security_analysis_template(self._item("Generic vuln"))
        assert "권장 조치" in result

    def test_always_has_five_checkboxes(self):
        result = _generate_security_analysis_template(self._item("Generic vuln"))
        checkboxes = [l for l in result.split("\n") if l.strip().startswith("- [ ]")]
        assert len(checkboxes) == 5

    def test_has_severity_field(self):
        result = _generate_security_analysis_template(self._item("Critical vuln"))
        assert "심각도" in result

    def test_has_priority_field(self):
        result = _generate_security_analysis_template(self._item("Critical vuln"))
        assert "대응 우선순위" in result

    # --- CVE extraction ---
    def test_cve_id_extracted(self):
        result = _generate_security_analysis_template(
            self._item("Patch CVE-2026-12345 immediately")
        )
        assert "CVE-2026-12345" in result

    def test_multiple_cves(self):
        result = _generate_security_analysis_template(
            self._item("CVE-2026-11111 and CVE-2026-22222 found")
        )
        assert "CVE-2026-11111" in result
        assert "CVE-2026-22222" in result

    def test_no_cve_shows_unknown(self):
        result = _generate_security_analysis_template(self._item("Generic security issue"))
        assert "미공개" in result or "해당 없음" in result

    # --- SIEM query generation ---
    def test_rce_generates_siem_query(self):
        result = _generate_security_analysis_template(
            self._item("Remote code execution vulnerability")
        )
        assert "SIEM 탐지 쿼리" in result
        assert "splunk" in result.lower() or "exploit" in result

    def test_auth_generates_siem_query(self):
        result = _generate_security_analysis_template(
            self._item("Authentication bypass found")
        )
        assert "SIEM 탐지 쿼리" in result

    def test_injection_generates_siem_query(self):
        result = _generate_security_analysis_template(
            self._item("SQL injection vulnerability in API")
        )
        assert "SIEM 탐지 쿼리" in result

    def test_no_siem_for_generic(self):
        result = _generate_security_analysis_template(
            self._item("New security best practice guide")
        )
        assert "SIEM 탐지 쿼리" not in result

    # --- MITRE ATT&CK ---
    def test_rce_mitre_mapping(self):
        result = _generate_security_analysis_template(
            self._item("Remote code execution exploit")
        )
        assert "MITRE ATT&CK" in result
        assert "T1203" in result

    def test_auth_mitre_mapping(self):
        result = _generate_security_analysis_template(
            self._item("Authentication bypass attack")
        )
        assert "T1078" in result

    def test_injection_mitre_mapping(self):
        result = _generate_security_analysis_template(
            self._item("SQL injection attack")
        )
        assert "T1190" in result

    def test_supply_chain_mitre_mapping(self):
        result = _generate_security_analysis_template(
            self._item("Supply chain compromise detected")
        )
        assert "T1195" in result

    def test_zero_day_mitre_mapping(self):
        result = _generate_security_analysis_template(
            self._item("Zero-day exploit in wild")
        )
        assert "T1068" in result

    def test_privilege_mitre_mapping(self):
        result = _generate_security_analysis_template(
            self._item(summary="권한 상승 취약점 발견")
        )
        assert "T1068" in result
