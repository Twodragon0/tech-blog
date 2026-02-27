#!/usr/bin/env python3
"""
Tech Blog - AWS/보안/아키텍처 다이어그램 일괄 생성 스크립트

포스트 내용을 기반으로 고품질 아키텍처 다이어그램을 생성합니다.
영상 제작에 적합한 고해상도 이미지를 생성합니다.

사용법:
    python3 scripts/generate_blog_diagrams.py              # 모든 관련 포스트 처리
    python3 scripts/generate_blog_diagrams.py --video      # 영상용 고해상도 이미지 생성
    python3 scripts/generate_blog_diagrams.py --post FILE  # 특정 포스트만 처리

비용: 무료 (로컬 실행)
필요 패키지: pip install diagrams graphviz pillow
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# diagrams 라이브러리 임포트
try:
    from diagrams import Cluster, Diagram, Edge
    from diagrams.aws.analytics import Athena, Kinesis

    # AWS 서비스
    from diagrams.aws.compute import EC2, ECS, EKS, Fargate, Lambda
    from diagrams.aws.database import (
        RDS,
        Aurora,
        DocumentDB,
        Dynamodb,
        ElastiCache,
        Redshift,
    )
    from diagrams.aws.devtools import Codebuild, Codecommit, Codepipeline, Codestar
    from diagrams.aws.general import Client as AWSClient
    from diagrams.aws.general import Users
    from diagrams.aws.integration import SNS, SQS, Eventbridge, StepFunctions
    from diagrams.aws.management import (
        Cloudtrail,
        Cloudwatch,
        CloudwatchAlarm,
        Config,
        ControlTower,
        Organizations,
    )
    from diagrams.aws.network import (
        ALB,
        ELB,
        NLB,
        VPC,
        APIGateway,
        CloudFront,
        InternetGateway,
        NATGateway,
        PrivateSubnet,
        PublicSubnet,
        Route53,
    )
    from diagrams.aws.security import (
        IAM,
        KMS,
        WAF,
        Cognito,
        Guardduty,
        Inspector,
        SecretsManager,
        SecurityHub,
        Shield,
    )
    from diagrams.aws.storage import EBS, EFS, S3
    from diagrams.generic.blank import Blank
    from diagrams.generic.device import Mobile, Tablet
    from diagrams.k8s.compute import Deployment, Pod
    from diagrams.k8s.controlplane import APIServer
    from diagrams.k8s.network import Ingress, Service
    from diagrams.k8s.rbac import ClusterRole, RoleBinding
    from diagrams.onprem.ci import GithubActions, Jenkins

    # 온프레미스/일반
    from diagrams.onprem.client import Client
    from diagrams.onprem.client import Users as OnpremUsers
    from diagrams.onprem.container import Docker
    from diagrams.onprem.monitoring import Datadog, Grafana
    from diagrams.onprem.vcs import Github
    from diagrams.programming.framework import React
    from diagrams.saas.cdn import Cloudflare

    DIAGRAMS_AVAILABLE = True
except ImportError as e:
    DIAGRAMS_AVAILABLE = False
    print("diagrams 라이브러리 설치 필요: pip install diagrams graphviz")
    print(f"오류: {e}")

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
VIDEO_IMAGES_DIR = PROJECT_ROOT / "assets" / "images" / "video"

# 영상용 고해상도 설정
VIDEO_GRAPH_ATTR = {
    "fontsize": "16",
    "bgcolor": "white",
    "dpi": "300",
    "pad": "1.0",
    "nodesep": "1.0",
    "ranksep": "1.5",
}

# 일반 설정
STANDARD_GRAPH_ATTR = {
    "fontsize": "14",
    "bgcolor": "white",
    "dpi": "150",
}


def log_message(message: str, level: str = "INFO") -> None:
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DIAGRAM": "📊",
    }
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")


# ============================================================================
# 1. AWS VPC 보안 아키텍처 다이어그램
# ============================================================================
def generate_vpc_security_architecture(
    output_path: Path, high_res: bool = False
) -> bool:
    """AWS VPC 보안 아키텍처 - 2주차 포스트 기반"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "AWS VPC Security Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            users = Users("Users")

            with Cluster("AWS Cloud"):
                route53 = Route53("Route 53\nDNS")

                with Cluster("Edge Security"):
                    shield = Shield("AWS Shield\nDDoS Protection")
                    waf = WAF("AWS WAF\nWeb Firewall")
                    cloudfront = CloudFront("CloudFront\nCDN")

                with Cluster("VPC (10.0.0.0/16)"):
                    igw = InternetGateway("Internet\nGateway")

                    with Cluster("Public Subnet (10.0.1.0/24)"):
                        alb = ALB("Application\nLoad Balancer")
                        nat = NATGateway("NAT Gateway")

                    with Cluster("Private Subnet - App (10.0.10.0/24)"):
                        ecs = ECS("ECS Fargate\nApplication")
                        lambda_fn = Lambda("Lambda\nFunctions")

                    with Cluster("Private Subnet - Data (10.0.20.0/24)"):
                        rds = RDS("RDS\nPostgreSQL")
                        elasticache = ElastiCache("ElastiCache\nRedis")

                with Cluster("Security & Monitoring"):
                    guardduty = Guardduty("Guardduty\nThreat Detection")
                    securityhub = SecurityHub("Security Hub")
                    cloudwatch = Cloudwatch("CloudWatch\nMonitoring")

            # 연결
            users >> route53 >> shield >> waf >> cloudfront >> igw >> alb
            alb >> ecs
            ecs >> nat
            ecs >> rds
            ecs >> elasticache
            ecs >> lambda_fn

            guardduty >> securityhub
            ecs >> cloudwatch

        log_message(f"VPC Security Architecture 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"VPC 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 2. AWS WAF + CloudFront 보안 아키텍처
# ============================================================================
def generate_waf_cloudfront_architecture(
    output_path: Path, high_res: bool = False
) -> bool:
    """AWS WAF/CloudFront 보안 아키텍처 - 6주차 포스트 기반"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "AWS WAF & CloudFront Security Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            users = Users("Users")
            attacker = Client("Attacker")

            with Cluster("AWS Edge"):
                shield = Shield("AWS Shield\nAdvanced")

                with Cluster("AWS WAF Rules"):
                    waf = WAF("AWS WAF")
                    waf_rules = Blank("SQL Injection\nXSS\nRate Limiting\nGeo-Block")

                cloudfront = CloudFront("CloudFront\nOAC Enabled")

            with Cluster("Origin"):
                with Cluster("S3 Origin"):
                    s3_static = S3("Static Assets\nBlocked Direct Access")

                with Cluster("ALB Origin"):
                    alb = ALB("Application LB")

                    with Cluster("ECS Cluster"):
                        ecs1 = Fargate("Task 1")
                        ecs2 = Fargate("Task 2")

            with Cluster("Logging & Monitoring"):
                cloudwatch = Cloudwatch("CloudWatch\nLogs")
                s3_logs = S3("WAF Logs")

            # 연결 - 정상 트래픽
            users >> shield >> waf >> cloudfront
            cloudfront >> s3_static
            cloudfront >> alb >> [ecs1, ecs2]

            # 공격자 차단
            attacker >> Edge(color="red", style="dashed", label="Blocked") >> shield

            # 로깅
            waf >> s3_logs
            cloudfront >> cloudwatch

        log_message(f"WAF/CloudFront Architecture 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"WAF 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 3. Database Access Gateway (NLB + Security Group)
# ============================================================================
def generate_db_gateway_architecture(output_path: Path, high_res: bool = False) -> bool:
    """데이터베이스 접근 게이트웨이 아키텍처"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "Database Access Gateway Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            with Cluster("Applications"):
                app1 = ECS("App Service 1")
                app2 = ECS("App Service 2")
                app3 = Lambda("Lambda\nFunctions")

            with Cluster("AWS VPC"):
                with Cluster("Gateway Layer"):
                    nlb = NLB("Network Load Balancer\nStatic IP")

                with Cluster("Security Group - Gateway"):
                    sg_gateway = Blank(
                        "SG: Gateway\nInbound: App IPs\nOutbound: DB Ports"
                    )

                with Cluster("Private Subnet - Databases"):
                    with Cluster("Relational"):
                        rds_mysql = RDS("RDS MySQL\nPort 3306")
                        rds_postgres = RDS("RDS PostgreSQL\nPort 5432")

                    with Cluster("NoSQL"):
                        elasticache = ElastiCache("ElastiCache Redis\nPort 6379")
                        documentdb = DocumentDB("DocumentDB\nPort 27017")

                    with Cluster("Analytics"):
                        redshift = Redshift("Redshift\nPort 5439")

            with Cluster("Security Group - Database"):
                sg_db = Blank("SG: Database\nInbound: Gateway SG Only")

            # 연결
            [app1, app2, app3] >> nlb
            nlb >> sg_gateway
            sg_gateway >> [rds_mysql, rds_postgres, elasticache, documentdb, redshift]

        log_message(f"DB Gateway Architecture 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"DB Gateway 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 4. DevSecOps CI/CD Pipeline
# ============================================================================
def generate_devsecops_pipeline(output_path: Path, high_res: bool = False) -> bool:
    """DevSecOps CI/CD 파이프라인 - 7기 8주차 기반"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "DevSecOps CI/CD Pipeline",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
        ):
            dev = Users("Developer")

            with Cluster("Source Control"):
                github = Github("GitHub")

            with Cluster("CI/CD Pipeline"):
                with Cluster("Build"):
                    gh_actions = GithubActions("GitHub Actions")

                with Cluster("Security Scanning"):
                    sast = Codebuild("SAST\nCodeQL/Semgrep")
                    sca = Codebuild("SCA\nDependabot/Trivy")
                    secrets = Codebuild("Secret Scan\nGitleaks")

                with Cluster("Testing"):
                    unit_test = Codebuild("Unit Tests")
                    dast = Codebuild("DAST\nOWASP ZAP")

            with Cluster("Container Registry"):
                ecr = ECS("ECR\nSigned Images")

            with Cluster("Deployment"):
                with Cluster("Staging"):
                    eks_staging = EKS("EKS Staging")

                with Cluster("Production"):
                    eks_prod = EKS("EKS Production")
                    waf = WAF("WAF")

            with Cluster("Monitoring"):
                cloudwatch = Cloudwatch("CloudWatch")
                guardduty = Guardduty("Guardduty")
                securityhub = SecurityHub("Security Hub")

            # 파이프라인 흐름
            dev >> github >> gh_actions
            gh_actions >> [sast, sca, secrets]
            sast >> unit_test
            unit_test >> dast >> ecr
            ecr >> eks_staging >> eks_prod
            waf >> eks_prod
            eks_prod >> [cloudwatch, guardduty]
            guardduty >> securityhub

        log_message(f"DevSecOps Pipeline 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"DevSecOps 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 5. Kubernetes Security Architecture
# ============================================================================
def generate_k8s_security_architecture(
    output_path: Path, high_res: bool = False
) -> bool:
    """Kubernetes 보안 아키텍처"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "Kubernetes Security Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            with Cluster("External"):
                users = Users("Users")
                devs = Users("Developers")

            with Cluster("Kubernetes Cluster"):
                with Cluster("Control Plane"):
                    api_server = APIServer("API Server\n+ Admission Control")

                with Cluster("RBAC"):
                    rbac = ClusterRole("ClusterRole\nRoleBinding")

                with Cluster("Policy Engine"):
                    kyverno = Blank("Kyverno\nPolicy as Code")

                with Cluster("Workloads"):
                    with Cluster("Namespace: Production"):
                        ingress = Ingress("Ingress\nTLS")
                        svc = Service("Service")

                        with Cluster("Pod Security Standards"):
                            deploy1 = Deployment("App Deployment\nRestricted")
                            pod1 = Pod("Pod\nNon-root")

                    with Cluster("Namespace: Monitoring"):
                        deploy2 = Deployment("Falco\nRuntime Security")

            with Cluster("External Services"):
                vault = Blank("HashiCorp Vault\nSecrets")
                registry = Docker("Container Registry\nSigned Images")

            # 연결
            users >> ingress >> svc >> deploy1 >> pod1
            devs >> api_server >> rbac
            api_server >> kyverno
            pod1 >> vault
            registry >> deploy1
            deploy2 >> Edge(color="orange", label="Alerts") >> Blank("SIEM")

        log_message(f"K8s Security Architecture 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"K8s 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 6. AWS Security Services Overview
# ============================================================================
def generate_aws_security_services(output_path: Path, high_res: bool = False) -> bool:
    """AWS 보안 서비스 전체 개요"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "AWS Security Services Overview",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            with Cluster("Perimeter Protection"):
                shield = Shield("AWS Shield\nDDoS")
                waf = WAF("AWS WAF\nL7 Firewall")
                cloudfront = CloudFront("CloudFront")

            with Cluster("Identity & Access"):
                iam = IAM("IAM\nPolicies & Roles")
                cognito = Cognito("Cognito\nUser Auth")
                sso = Blank("IAM Identity Center\nSSO")

            with Cluster("Detection & Response"):
                guardduty = Guardduty("Guardduty\nThreat Detection")
                securityhub = SecurityHub("Security Hub\nCentral Dashboard")
                inspector = Inspector("Inspector\nVulnerability")

            with Cluster("Data Protection"):
                kms = KMS("KMS\nEncryption Keys")
                secrets = SecretsManager("Secrets Manager")
                s3 = S3("S3\nEncrypted")

            with Cluster("Compliance & Governance"):
                config = Config("AWS Config\nCompliance")
                cloudtrail = Cloudtrail("CloudTrail\nAudit Logs")
                control_tower = ControlTower("Control Tower")

            # 연결
            shield >> waf >> cloudfront
            iam >> cognito
            guardduty >> securityhub
            inspector >> securityhub
            kms >> [secrets, s3]
            config >> securityhub
            cloudtrail >> securityhub

        log_message(f"AWS Security Services 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"AWS Security 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 7. Zero Trust Architecture
# ============================================================================
def generate_zero_trust_architecture(output_path: Path, high_res: bool = False) -> bool:
    """Zero Trust 아키텍처"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "Zero Trust Security Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            with Cluster("Users & Devices"):
                employee = Users("Employees")
                mobile = Mobile("Mobile Devices")
                remote = Tablet("Remote Workers")

            with Cluster("Identity Verification"):
                idp = Cognito("Identity Provider\nMFA Required")
                device_trust = Blank("Device Trust\nVerification")

            with Cluster("Policy Engine"):
                policy = Blank("Zero Trust Policy\nNever Trust, Always Verify")

            with Cluster("Access Proxy"):
                cloudflare = Cloudflare("Cloudflare ZTNA\nor AWS Verified Access")

            with Cluster("Protected Resources"):
                with Cluster("Applications"):
                    app1 = ECS("Internal Apps")
                    app2 = Lambda("APIs")

                with Cluster("Data"):
                    rds = RDS("Databases")
                    s3 = S3("Object Storage")

            with Cluster("Continuous Monitoring"):
                siem = Blank("SIEM\nAnomaly Detection")
                guardduty = Guardduty("Guardduty")

            # 연결
            employee >> idp
            mobile >> idp
            remote >> idp
            idp >> device_trust >> policy
            policy >> cloudflare
            cloudflare >> app1
            cloudflare >> app2
            app1 >> rds
            app2 >> s3
            cloudflare >> siem
            guardduty >> siem

        log_message(f"Zero Trust Architecture 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"Zero Trust 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 8. DevSecOps Learning Roadmap
# ============================================================================
def generate_devsecops_roadmap(output_path: Path, high_res: bool = False) -> bool:
    """DevSecOps 학습 로드맵 - roadmap.sh 기반"""
    try:
        graph_attr = VIDEO_GRAPH_ATTR if high_res else STANDARD_GRAPH_ATTR

        with Diagram(
            "DevSecOps Learning Roadmap 2026",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
        ):
            with Cluster("Stage 1: Foundation (0-6 months)"):
                programming = Blank("Programming\nPython, Bash, Go")
                security_basics = Blank("Security Basics\nOWASP Top 10")
                linux = Blank("Linux/Networking")

            with Cluster("Stage 2: Tools (6-12 months)"):
                sast = Blank("SAST\nCodeQL, Semgrep")
                dast = Blank("DAST\nBurp Suite, ZAP")
                sca = Blank("SCA\nTrivy, Dependabot")

            with Cluster("Stage 3: Platform (12-18 months)"):
                cicd = Blank("CI/CD Security\nGitHub Actions")
                container = Docker("Container Security\nDocker, K8s")
                cloud = Blank("Cloud Security\nAWS, GCP, Azure")

            with Cluster("Stage 4: Advanced (18-24 months)"):
                threat = Blank("Threat Modeling\nSTRIDE, PASTA")
                ir = Blank("Incident Response\nSIEM, SOAR")
                governance = Blank("Governance\nNIST CSF 2.0")

            with Cluster("Stage 5: Expert (24+ months)"):
                architect = Blank("Security Architect\nEnterprise Design")
                leadership = Blank("Security Leadership\nStrategy & Culture")

            # 학습 경로
            programming >> sast
            security_basics >> dast
            linux >> sca

            [sast, dast, sca] >> cicd
            cicd >> container >> cloud

            cloud >> [threat, ir, governance]

            [threat, ir, governance] >> architect >> leadership

        log_message(f"DevSecOps Roadmap 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"DevSecOps Roadmap 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 메인 실행
# ============================================================================
DIAGRAM_FUNCTIONS = {
    "vpc_security": (
        "AWS VPC Security Architecture",
        generate_vpc_security_architecture,
    ),
    "waf_cloudfront": (
        "AWS WAF CloudFront Architecture",
        generate_waf_cloudfront_architecture,
    ),
    "db_gateway": ("Database Access Gateway", generate_db_gateway_architecture),
    "devsecops_pipeline": ("DevSecOps CI/CD Pipeline", generate_devsecops_pipeline),
    "k8s_security": (
        "Kubernetes Security Architecture",
        generate_k8s_security_architecture,
    ),
    "aws_security_services": (
        "AWS Security Services Overview",
        generate_aws_security_services,
    ),
    "zero_trust": ("Zero Trust Architecture", generate_zero_trust_architecture),
    "devsecops_roadmap": ("DevSecOps Learning Roadmap", generate_devsecops_roadmap),
}


def generate_all_diagrams(
    high_res: bool = False, output_dir: Optional[Path] = None
) -> Dict[str, bool]:
    """모든 다이어그램 생성"""
    if not DIAGRAMS_AVAILABLE:
        log_message("diagrams 라이브러리가 설치되지 않았습니다.", "ERROR")
        return {}

    if output_dir is None:
        output_dir = VIDEO_IMAGES_DIR if high_res else ASSETS_IMAGES_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    total = len(DIAGRAM_FUNCTIONS)

    log_message(
        f"{'영상용 고해상도' if high_res else '표준'} 다이어그램 생성 시작 ({total}개)"
    )
    log_message(f"출력 디렉토리: {output_dir}")

    for idx, (key, (title, func)) in enumerate(DIAGRAM_FUNCTIONS.items(), 1):
        log_message(f"[{idx}/{total}] {title} 생성 중...")
        output_path = output_dir / f"diagram_{key}.png"

        try:
            success = func(output_path, high_res=high_res)
            results[key] = success
            if success:
                log_message(f"  생성 완료: {output_path.name}", "SUCCESS")
        except Exception as e:
            log_message(f"  생성 실패: {e}", "ERROR")
            results[key] = False

    # 결과 요약
    success_count = sum(1 for v in results.values() if v)
    log_message(f"\n생성 완료: {success_count}/{total} 다이어그램", "SUCCESS")

    return results


def main():
    parser = argparse.ArgumentParser(description="Tech Blog 아키텍처 다이어그램 생성")
    parser.add_argument(
        "--video", "-v", action="store_true", help="영상 제작용 고해상도 이미지 생성"
    )
    parser.add_argument("--output", "-o", type=str, help="출력 디렉토리 경로")
    parser.add_argument(
        "--diagram",
        "-d",
        type=str,
        choices=list(DIAGRAM_FUNCTIONS.keys()),
        help="특정 다이어그램만 생성",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="생성 가능한 다이어그램 목록"
    )

    args = parser.parse_args()

    if args.list:
        print("\n생성 가능한 다이어그램:")
        for key, (title, _) in DIAGRAM_FUNCTIONS.items():
            print(f"  - {key}: {title}")
        return

    if not DIAGRAMS_AVAILABLE:
        print("\n필요 패키지 설치:")
        print("  pip install diagrams graphviz")
        print("\nMac에서 graphviz 설치:")
        print("  brew install graphviz")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else None

    if args.diagram:
        # 특정 다이어그램만 생성
        if args.diagram in DIAGRAM_FUNCTIONS:
            title, func = DIAGRAM_FUNCTIONS[args.diagram]
            out_dir = output_dir or (
                VIDEO_IMAGES_DIR if args.video else ASSETS_IMAGES_DIR
            )
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = out_dir / f"diagram_{args.diagram}.png"

            log_message(f"{title} 생성 중...")
            success = func(output_path, high_res=args.video)

            if success:
                log_message(f"생성 완료: {output_path}", "SUCCESS")
            sys.exit(0 if success else 1)
    else:
        # 모든 다이어그램 생성
        results = generate_all_diagrams(high_res=args.video, output_dir=output_dir)
        sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
