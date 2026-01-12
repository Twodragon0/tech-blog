#!/usr/bin/env python3
"""
Assets 디렉토리 정리 스크립트
- 한국어 파일명을 영어로 변환
- 디렉토리 구조 정리
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
POSTS_DIR = PROJECT_ROOT / "_posts"

# 한국어 → 영어 매핑
KOREAN_TO_ENGLISH = {
    # 일반 단어
    "년": "_year_",
    "월": "_month_",
    "일": "_day_",
    "완벽": "complete",
    "가이드": "guide",
    "보안": "security",
    "클라우드": "cloud",
    "분석": "analysis",
    "실습": "practical",
    "시큐리티": "security",
    "과정": "course",
    "주차": "week",
    "기": "batch",
    "부터": "from",
    "까지": "to",
    "및": "and",
    "의": "_",
    "와": "_and_",
    "를": "",
    "을": "",
    "이": "",
    "가": "",
    "에": "_in_",
    "에서": "_in_",
    "로": "_to_",
    "으로": "_to_",
    "위한": "_for_",
    "통한": "_through_",
    "기반": "based",
    "활용": "using",
    "방법": "method",
    "설정": "setup",
    "구축": "build",
    "접근": "access",
    "관리": "management",
    "서비스": "service",
    "아키텍처": "architecture",
    "네트워크": "network",
    "취약점": "vulnerability",
    "점검": "inspection",
    "대응": "response",
    "인증": "authentication",
    "암호": "encryption",
    "화폐": "currency",
    "블록체인": "blockchain",
    "자동차": "automotive",
    "자동": "auto",
    "테스트": "test",
    "문제": "problem",
    "해결": "solution",
    "장애": "incident",
    "노드": "node",
    "통합": "integration",
    "생태계": "ecosystem",
    "대규모": "large_scale",
    "패키지": "package",
    "악성": "malicious",
    "코드": "code",
    "감염": "infection",
    "침해": "breach",
    "공급망": "supply_chain",
    "공격": "attack",
    "복제": "replication",
    "웜": "worm",
    "긴급": "urgent",
    "새": "new",
    "글": "post",
    "알림": "notification",
    "구독": "subscription",
    "컨퍼런스": "conference",
    "회고": "review",
    "미리": "preview",
    "공존": "coexistence",
    "시대": "era",
    "당신": "your",
    "비서": "assistant",
    "구멍": "hole",
    "되지": "",
    "않도록": "",
    "기업": "enterprise",
    "셋업": "setup",
    "규정": "regulation",
    "준수": "compliance",
    "올인원": "all_in_one",
    "마스터": "master",
    "데이터베이스": "database",
    "게이트웨이": "gateway",
    "강화": "enhance",
    "최적화": "optimization",
    "로드맵": "roadmap",
    "학습": "learning",
    "경로": "path",
    "에이전틱": "agentic",
    "업데이트": "update",
    "최신": "latest",
    "현재": "current",
    "미래": "future",
    "검사": "inspection",
    "샌드박스": "sandbox",
    "광고": "ad",
    "유해": "harmful",
    "사이트": "site",
    "차단": "blocking",
    "안전": "safe",
    "하게": "ly",
    "패스키": "passkey",
    "강력한": "strong",
    "확인": "check",
    "교체": "replace",
    "그리고": "and",
    "중요성": "importance",
    "이슈": "issue",
    "핵심": "core",
    "정복": "conquer",
    "본질": "essence",
    "인프라": "infrastructure",
    "하드웨어": "hardware",
    "비용": "cost",
    "관점": "perspective",
    "도구": "tools",
    "모범": "best",
    "사례": "practice",
    "다운로드": "download",
    "억": "billion",
    "개": "",
    "이상": "over",
    "자가": "self",
    "완전": "complete",
}

# 특수 파일명 매핑 (전체 파일명)
SPECIAL_MAPPINGS = {
    "12월_컨퍼런스_회고_AWSKRUG_OWASP_Datadog으로_미리_보는_2025년_AI와_보안의_공존_og.png":
        "december_conference_review_awskrug_owasp_datadog_2025_ai_security_coexistence_og.png",
    "2026-01-10-2026년_DevSecOps_로드맵_완벽_가이드_roadmap.sh_분석_og.png":
        "2026-01-10-2026_devsecops_roadmap_complete_guide_roadmap_sh_analysis_og.png",
    "AI_시대_당신의_amplsquo비서amprsquo가_amplsquo보안_구멍amprsquo이_되지_않도록_기업을_위한_AI_서비스_보안_가이드_og.png":
        "ai_era_assistant_security_enterprise_ai_service_security_guide_og.png",
    "AWS_reInforce_2025_클라우드_보안의_현재와_미래__og.png":
        "aws_reinforce_2025_cloud_security_current_future_og.png",
    "AWS에서_안전한_데이터베이스_접근_게이트웨이_구축하기_NLB__Security_Group_완벽_가이드_og.png":
        "aws_secure_database_access_gateway_nlb_security_group_complete_guide_og.png",
    "Amazon_Q_Developer와_GitHub_Advanced_Security를_활용한_코드_보안_강화_및_AWS_최적화_og.png":
        "amazon_q_developer_github_advanced_security_code_security_aws_optimization_og.png",
    "DevSecOps가_바라보는_자동차_보안_완벽_가이드_og.png":
        "devsecops_automotive_security_complete_guide_og.png",
    "Kandji로_macOS_완벽_마스터_셋업부터_보안_규정_준수까지_올인원_가이드_og.png":
        "kandji_macos_complete_master_setup_security_compliance_all_in_one_guide_og.png",
    "Karpenter_v153_노드_통합으로_인한_대규모_장애_분석_및_해결기_og.png":
        "karpenter_v153_node_consolidation_large_scale_incident_analysis_resolution_og.png",
    "Kubernetes_Minikube_ampamp_K9s_실습_가이드_문제_해결부터_실전_테스트까지_og.png":
        "kubernetes_minikube_k9s_practical_guide_problem_solving_testing_og.png",
    "NPM_ampquotShai-Huludampquot_자가_복제_웜_공격_180개_이상_패키지_침해된_대규모_공급망_공격_완전_분석_og.png":
        "npm_shai_hulud_self_replicating_worm_attack_180_packages_supply_chain_analysis_og.png",
    "OWASP_2025_최신_업데이트_완벽_가이드_Top_10_에이전틱_AI_보안_og.png":
        "owasp_2025_latest_update_complete_guide_top10_agentic_ai_security_og.png",
    "Post-Mortem_2025년_11월_18일_Cloudflare_글로벌_장애_대응_일지_우리는_무엇을_배웠나_og.png":
        "postmortem_2025_nov_18_cloudflare_global_incident_response_lessons_learned_og.png",
    "SKT_보안_이슈_완벽_대응_가이드_IMEI_확인_USIMeSIM_교체_그리고_MFA의_중요성_og.png":
        "skt_security_issue_complete_response_guide_imei_usim_esim_mfa_importance_og.png",
    "Tesla_FSD_2026_완벽_가이드_Model_Y_Juniper_비용_하드웨어_보안_DevSecOps_관점_og.png":
        "tesla_fsd_2026_complete_guide_model_y_juniper_cost_hardware_security_devsecops_og.png",
    "Zscaler_완벽_가이드_SSL_검사_샌드박스_AI_광고_유해_사이트_완벽_차단_og.png":
        "zscaler_complete_guide_ssl_inspection_sandbox_ai_ad_harmful_site_blocking_og.png",
    "공용_PC에서도_안전하게_패스키_OTP_강력한_암호_관리_활용법_og.png":
        "public_pc_safely_passkey_otp_strong_password_management_og.png",
    "긴급_npm_생태계_대규모_보안_침해_20억_다운로드_패키지_악성코드_감염_og.png":
        "urgent_npm_ecosystem_large_scale_security_breach_2billion_download_malware_infection_og.png",
    "블록체인_암호화폐_보안_완벽_가이드_DevSecOps_관점에서_본_GitHub_보안_도구_및_모범_사례_og.png":
        "blockchain_cryptocurrency_security_complete_guide_devsecops_github_security_tools_best_practices_og.png",
    "이메일_발송_신뢰도_높이기_SendGrid_SPF_DKIM_DMARC_설정_완벽_가이드_og.png":
        "email_delivery_trust_sendgrid_spf_dkim_dmarc_setup_complete_guide_og.png",
    "클라우드_보안_과정_7기_-_4주차_AWS_취약점_점검_및_ISMS_대응_가이드_og.png":
        "cloud_security_course_7batch_4week_aws_vulnerability_inspection_isms_response_guide_og.png",
    "클라우드_보안_과정_8기_6주차_AWS_WAF_CloudFront_보안_아키텍처_및_GitHub_DevSecOps_실전_og.png":
        "cloud_security_course_8batch_6week_aws_waf_cloudfront_security_architecture_github_devsecops_og.png",
    "클라우드_시큐리티_8기_1주차_인프라의_본질부터_보안의_미래까지_og.png":
        "cloud_security_8batch_1week_infrastructure_essence_security_future_og.png",
    "클라우드_시큐리티_8기_2주차_AWS_보안_아키텍처의_핵심_VPC부터_GuardDuty까지_완벽_정복_og.png":
        "cloud_security_8batch_2week_aws_security_architecture_vpc_guardduty_complete_guide_og.png",
    "클라우드_시큐리티_8기_3주차_AWS_FinOps_아키텍처부터_ISMS-P_보안_감사까지_완벽_공략_og.png":
        "cloud_security_8batch_3week_aws_finops_architecture_ismsp_security_audit_complete_guide_og.png",
    "클라우드_시큐리티_8기_4주차_통합_보안_취약점_점검_및_ISMS-P_인증_대응_실무_og.png":
        "cloud_security_8batch_4week_integrated_security_vulnerability_inspection_ismsp_certification_og.png",
    "클라우드_시큐리티_8기_OT_안내_DevSecOps부터_FinOps까지_실무형_인재로_도약하라_og.png":
        "cloud_security_8batch_ot_guide_devsecops_finops_practical_talent_og.png",
    "클라우드_시큐리티_과정_7기_-_3주차_AWS_보안_및_Finops_og.png":
        "cloud_security_course_7batch_3week_aws_security_finops_og.png",
    "클라우드_시큐리티_과정_7기_-_5주차_AWS_Control_Tower_및_ZTNA_og.png":
        "cloud_security_course_7batch_5week_aws_control_tower_ztna_og.png",
    "클라우드_시큐리티_과정_7기_-_6주차_Cloudflare_및_github_보안_og.png":
        "cloud_security_course_7batch_6week_cloudflare_github_security_og.png",
    "클라우드_시큐리티_과정_7기_-_7주차_Docker_및_Kubernetes_이해_og.png":
        "cloud_security_course_7batch_7week_docker_kubernetes_understanding_og.png",
    "클라우드_시큐리티_과정_7기_-_8주차_CICD와_Kubernetes_보안_실전_가이드_og.png":
        "cloud_security_course_7batch_8week_cicd_kubernetes_security_practical_guide_og.png",
    "클라우드_시큐리티_과정_7기_-_9주차_DevSecOps_통합_정리_og.png":
        "cloud_security_course_7batch_9week_devsecops_integration_og.png",
    "클라우드_시큐리티_과정_8기_5주차_AWS_Control_TowerSCP_기반_거버넌스_및_Datadog_SIEM_Cloudflare_보안_og.png":
        "cloud_security_course_8batch_5week_aws_control_tower_scp_governance_datadog_siem_cloudflare_og.png",
    # SVG 파일
    "2025-10-31-AI_시대_당신의_amplsquo비서amprsquo가_amplsquo보안_구멍amprsquo이_되지_않도록_기업을_위한_AI_서비스_보안_가이드.svg":
        "2025-10-31-AI_Era_Enterprise_AI_Service_Security_Guide.svg",
}


def convert_korean_to_english(filename: str) -> str:
    """한국어 파일명을 영어로 변환"""
    # 특수 매핑 확인
    if filename in SPECIAL_MAPPINGS:
        return SPECIAL_MAPPINGS[filename]

    # 한국어가 없으면 그대로 반환
    if not re.search(r'[가-힣]', filename):
        return filename

    result = filename

    # 한국어 단어를 영어로 변환
    for korean, english in sorted(KOREAN_TO_ENGLISH.items(), key=lambda x: -len(x[0])):
        result = result.replace(korean, english)

    # 정리
    result = re.sub(r'_+', '_', result)  # 여러 언더스코어를 하나로
    result = re.sub(r'^_|_$', '', result)  # 시작/끝 언더스코어 제거
    result = result.lower()

    return result


def get_files_to_rename() -> Dict[Path, Path]:
    """변경할 파일 목록 생성"""
    files_to_rename = {}

    for file_path in IMAGES_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        filename = file_path.name
        new_filename = convert_korean_to_english(filename)

        if filename != new_filename:
            new_path = file_path.parent / new_filename
            files_to_rename[file_path] = new_path

    return files_to_rename


def update_post_references(old_name: str, new_name: str) -> int:
    """포스트 파일에서 이미지 참조 업데이트"""
    count = 0

    for post_file in POSTS_DIR.glob("*.md"):
        try:
            content = post_file.read_text(encoding="utf-8")
            if old_name in content:
                new_content = content.replace(old_name, new_name)
                post_file.write_text(new_content, encoding="utf-8")
                count += 1
                print(f"  Updated: {post_file.name}")
        except Exception as e:
            print(f"  Error updating {post_file.name}: {e}")

    return count


def organize_assets(dry_run: bool = True) -> None:
    """assets 디렉토리 정리"""
    files_to_rename = get_files_to_rename()

    if not files_to_rename:
        print("No files need to be renamed.")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Files to rename: {len(files_to_rename)}")
    print("-" * 60)

    for old_path, new_path in sorted(files_to_rename.items()):
        old_name = old_path.name
        new_name = new_path.name

        print(f"\n{old_name}")
        print(f"  -> {new_name}")

        if not dry_run:
            # 파일 이름 변경
            if new_path.exists():
                print(f"  WARNING: Target file already exists, skipping")
                continue

            old_path.rename(new_path)

            # 포스트 참조 업데이트
            updated = update_post_references(old_name, new_name)
            if updated:
                print(f"  Updated {updated} post(s)")

    print("\n" + "-" * 60)
    print(f"{'[DRY RUN] Would rename' if dry_run else 'Renamed'} {len(files_to_rename)} files")


if __name__ == "__main__":
    import sys

    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("Running in DRY RUN mode. Use --apply to actually rename files.")

    organize_assets(dry_run=dry_run)
