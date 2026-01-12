#!/usr/bin/env python3
"""
AWS 아키텍처 다이어그램 자동 생성 스크립트

포스트 내용을 분석하여 Python diagrams 라이브러리로 아키텍처 다이어그램을 생성합니다.
비용: 무료 (로컬 실행)

사용법:
    python3 scripts/generate_aws_diagram.py [포스트파일명]
    python3 scripts/generate_aws_diagram.py --type vpc _posts/2026-01-12-AWS_Security.md
    python3 scripts/generate_aws_diagram.py --type security _posts/2026-01-12-WAF.md

다이어그램 유형:
    - vpc: VPC 네트워크 아키텍처
    - security: 보안 아키텍처 (WAF, Shield, IAM)
    - compute: EC2/ECS/EKS 컴퓨팅
    - data: 데이터 계층 (S3, RDS, DynamoDB)
    - serverless: Lambda/API Gateway
    - monitoring: CloudWatch/X-Ray
    - devsecops: CI/CD 파이프라인
    - auto: 자동 감지 (기본값)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# diagrams 라이브러리 임포트
try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import EC2, ECS, EKS, Lambda, Fargate
    from diagrams.aws.network import VPC, PrivateSubnet, PublicSubnet, InternetGateway, NATGateway, ELB, ALB, CloudFront, Route53
    from diagrams.aws.security import WAF, Shield, IAM, Cognito, KMS, SecretsManager
    from diagrams.aws.database import RDS, DynamoDB, ElastiCache, Aurora
    from diagrams.aws.storage import S3, EBS, EFS
    from diagrams.aws.integration import SQS, SNS, EventBridge
    from diagrams.aws.management import Cloudwatch, CloudwatchAlarm, Cloudtrail
    from diagrams.aws.devtools import Codepipeline, Codebuild, Codecommit
    from diagrams.aws.general import Users
    from diagrams.onprem.client import Client
    from diagrams.onprem.vcs import Github
    from diagrams.generic.blank import Blank
    DIAGRAMS_AVAILABLE = True
except ImportError:
    DIAGRAMS_AVAILABLE = False
    print("⚠️ diagrams 라이브러리가 설치되지 않았습니다.")
    print("   설치: pip install diagrams graphviz")

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 키워드 → 다이어그램 유형 매핑
KEYWORD_TYPE_MAP = {
    "vpc": ["VPC", "서브넷", "Subnet", "네트워크", "Network", "CIDR", "라우팅"],
    "security": ["WAF", "Shield", "IAM", "보안", "Security", "방화벽", "Firewall", "인증", "ZTNA"],
    "compute": ["EC2", "ECS", "EKS", "Kubernetes", "컨테이너", "Container", "인스턴스"],
    "data": ["RDS", "DynamoDB", "S3", "데이터베이스", "Database", "스토리지", "Storage"],
    "serverless": ["Lambda", "API Gateway", "서버리스", "Serverless", "함수"],
    "monitoring": ["CloudWatch", "모니터링", "Monitoring", "로그", "Log", "X-Ray", "추적"],
    "devsecops": ["CI/CD", "파이프라인", "Pipeline", "DevSecOps", "DevOps", "CodePipeline", "GitHub Actions"],
}


def log_message(message: str, level: str = "INFO") -> None:
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] [{level}] {icon} {message}")


def detect_diagram_type(content: str, tags: List[str]) -> str:
    """포스트 내용과 태그를 분석하여 다이어그램 유형을 감지합니다."""
    content_lower = content.lower()
    tag_str = " ".join(tags).lower()
    combined = content_lower + " " + tag_str

    # 키워드 매칭 점수 계산
    scores = {}
    for diagram_type, keywords in KEYWORD_TYPE_MAP.items():
        score = sum(1 for kw in keywords if kw.lower() in combined)
        if score > 0:
            scores[diagram_type] = score

    if not scores:
        return "vpc"  # 기본값

    # 가장 높은 점수의 유형 반환
    return max(scores, key=scores.get)


def extract_post_info(post_file: Path) -> Dict:
    """포스트 파일에서 정보를 추출합니다."""
    try:
        import frontmatter
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        return {
            "title": post.get("title", ""),
            "tags": post.get("tags", []),
            "categories": post.get("categories", []),
            "content": post.content,
            "date": post.get("date", ""),
        }
    except ImportError:
        # frontmatter 없이 간단 파싱
        with open(post_file, "r", encoding="utf-8") as f:
            content = f.read()

        # YAML front matter 추출
        title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        tags_match = re.search(r'^tags:\s*\[(.+?)\]', content, re.MULTILINE)

        return {
            "title": title_match.group(1) if title_match else "",
            "tags": [t.strip().strip('"\'') for t in tags_match.group(1).split(",")] if tags_match else [],
            "categories": [],
            "content": content,
            "date": "",
        }


def generate_vpc_diagram(title: str, output_path: Path) -> bool:
    """VPC 네트워크 아키텍처 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            users = Users("Users")

            with Cluster("AWS Cloud"):
                route53 = Route53("Route 53")
                cloudfront = CloudFront("CloudFront")

                with Cluster("VPC"):
                    igw = InternetGateway("IGW")

                    with Cluster("Public Subnet"):
                        alb = ALB("ALB")
                        nat = NATGateway("NAT GW")

                    with Cluster("Private Subnet - App"):
                        ecs = ECS("ECS Fargate")
                        ec2 = EC2("EC2")

                    with Cluster("Private Subnet - Data"):
                        rds = RDS("RDS")
                        elasticache = ElastiCache("ElastiCache")

            users >> route53 >> cloudfront >> igw >> alb
            alb >> ecs
            alb >> ec2
            ecs >> nat >> Edge(label="Internet") >> Blank("External API")
            ecs >> rds
            ecs >> elasticache

        log_message(f"VPC 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"VPC 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_security_diagram(title: str, output_path: Path) -> bool:
    """보안 아키텍처 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            users = Users("Users")
            attacker = Client("Attacker")

            with Cluster("AWS Security Layer"):
                shield = Shield("AWS Shield")
                waf = WAF("AWS WAF")
                cloudfront = CloudFront("CloudFront")

                with Cluster("Identity & Access"):
                    cognito = Cognito("Cognito")
                    iam = IAM("IAM")

                with Cluster("Data Protection"):
                    kms = KMS("KMS")
                    secrets = SecretsManager("Secrets Manager")

                with Cluster("VPC"):
                    alb = ALB("ALB")

                    with Cluster("Private Subnet"):
                        ecs = ECS("ECS")
                        rds = RDS("RDS (Encrypted)")

            users >> cognito >> iam
            users >> shield >> waf >> cloudfront >> alb >> ecs >> rds
            attacker >> Edge(color="red", style="dashed") >> shield
            ecs >> secrets
            rds >> kms

        log_message(f"보안 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"보안 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_devsecops_diagram(title: str, output_path: Path) -> bool:
    """DevSecOps CI/CD 파이프라인 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            dev = Users("Developer")

            with Cluster("Source"):
                github = Github("GitHub")

            with Cluster("AWS CodePipeline"):
                with Cluster("Build & Test"):
                    codebuild = Codebuild("CodeBuild")

                with Cluster("Security Scan"):
                    # 보안 스캔 단계
                    sast = Codebuild("SAST")
                    sca = Codebuild("SCA")
                    dast = Codebuild("DAST")

            with Cluster("Deploy"):
                with Cluster("Staging"):
                    ecs_staging = ECS("ECS Staging")

                with Cluster("Production"):
                    ecs_prod = ECS("ECS Production")
                    waf = WAF("WAF")

            with Cluster("Monitoring"):
                cloudwatch = Cloudwatch("CloudWatch")
                cloudtrail = Cloudtrail("CloudTrail")

            dev >> github >> codebuild
            codebuild >> sast >> sca >> dast
            dast >> ecs_staging >> ecs_prod
            waf >> ecs_prod
            ecs_prod >> cloudwatch
            ecs_prod >> cloudtrail

        log_message(f"DevSecOps 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"DevSecOps 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_serverless_diagram(title: str, output_path: Path) -> bool:
    """서버리스 아키텍처 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            users = Users("Users")

            with Cluster("AWS Serverless"):
                cloudfront = CloudFront("CloudFront")

                with Cluster("API Layer"):
                    alb = ALB("API Gateway")
                    waf = WAF("WAF")

                with Cluster("Compute"):
                    lambda1 = Lambda("Auth Lambda")
                    lambda2 = Lambda("API Lambda")
                    lambda3 = Lambda("Worker Lambda")

                with Cluster("Data"):
                    dynamodb = DynamoDB("DynamoDB")
                    s3 = S3("S3")

                with Cluster("Integration"):
                    sqs = SQS("SQS")
                    sns = SNS("SNS")
                    eventbridge = EventBridge("EventBridge")

            users >> cloudfront >> waf >> alb
            alb >> lambda1 >> lambda2
            lambda2 >> dynamodb
            lambda2 >> s3
            lambda2 >> sqs >> lambda3
            lambda3 >> sns
            eventbridge >> lambda3

        log_message(f"서버리스 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"서버리스 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_monitoring_diagram(title: str, output_path: Path) -> bool:
    """모니터링 아키텍처 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            with Cluster("Application Layer"):
                ecs = ECS("ECS")
                lambda_fn = Lambda("Lambda")
                ec2 = EC2("EC2")

            with Cluster("AWS Monitoring"):
                with Cluster("Metrics & Logs"):
                    cloudwatch = Cloudwatch("CloudWatch")
                    cloudwatch_logs = Cloudwatch("CloudWatch Logs")

                with Cluster("Alarms"):
                    alarm = CloudwatchAlarm("Alarms")

                with Cluster("Audit"):
                    cloudtrail = Cloudtrail("CloudTrail")

                sns = SNS("SNS")

            with Cluster("External"):
                users = Users("Ops Team")

            ecs >> cloudwatch
            lambda_fn >> cloudwatch
            ec2 >> cloudwatch
            ecs >> cloudwatch_logs
            cloudwatch >> alarm >> sns >> users
            ecs >> cloudtrail

        log_message(f"모니터링 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"모니터링 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_compute_diagram(title: str, output_path: Path) -> bool:
    """컴퓨팅 아키텍처 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            users = Users("Users")

            with Cluster("AWS Cloud"):
                alb = ALB("ALB")

                with Cluster("EKS Cluster"):
                    with Cluster("Node Group 1"):
                        ec2_1 = EC2("Node 1")
                        ec2_2 = EC2("Node 2")

                    with Cluster("Node Group 2"):
                        ec2_3 = EC2("Node 3")
                        ec2_4 = EC2("Node 4")

                with Cluster("ECS Cluster"):
                    fargate1 = Fargate("Fargate Task 1")
                    fargate2 = Fargate("Fargate Task 2")

                with Cluster("Data Layer"):
                    rds = RDS("RDS")
                    elasticache = ElastiCache("ElastiCache")

            users >> alb
            alb >> ec2_1
            alb >> ec2_2
            alb >> fargate1
            alb >> fargate2
            ec2_1 >> rds
            fargate1 >> elasticache

        log_message(f"컴퓨팅 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"컴퓨팅 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_data_diagram(title: str, output_path: Path) -> bool:
    """데이터 계층 아키텍처 다이어그램 생성"""
    try:
        with Diagram(
            title,
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white"},
        ):
            with Cluster("Application"):
                app = ECS("Application")

            with Cluster("AWS Data Layer"):
                with Cluster("Relational"):
                    aurora = Aurora("Aurora")
                    rds = RDS("RDS MySQL")

                with Cluster("NoSQL"):
                    dynamodb = DynamoDB("DynamoDB")
                    elasticache = ElastiCache("ElastiCache")

                with Cluster("Storage"):
                    s3 = S3("S3")
                    efs = EFS("EFS")

                with Cluster("Security"):
                    kms = KMS("KMS")

            app >> aurora
            app >> dynamodb
            app >> elasticache
            app >> s3
            aurora >> kms
            s3 >> kms

        log_message(f"데이터 다이어그램 생성 완료: {output_path}", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"데이터 다이어그램 생성 실패: {e}", "ERROR")
        return False


# 다이어그램 유형별 생성 함수 매핑
DIAGRAM_GENERATORS = {
    "vpc": generate_vpc_diagram,
    "security": generate_security_diagram,
    "devsecops": generate_devsecops_diagram,
    "serverless": generate_serverless_diagram,
    "monitoring": generate_monitoring_diagram,
    "compute": generate_compute_diagram,
    "data": generate_data_diagram,
}


def generate_diagram(post_file: Path, diagram_type: str = "auto", output_path: Optional[Path] = None) -> bool:
    """포스트에 대한 다이어그램을 생성합니다."""
    if not DIAGRAMS_AVAILABLE:
        log_message("diagrams 라이브러리가 설치되지 않았습니다.", "ERROR")
        return False

    # 포스트 정보 추출
    post_info = extract_post_info(post_file)
    title = post_info["title"] or post_file.stem

    # 다이어그램 유형 결정
    if diagram_type == "auto":
        diagram_type = detect_diagram_type(post_info["content"], post_info["tags"])
        log_message(f"자동 감지된 다이어그램 유형: {diagram_type}")

    # 출력 경로 설정
    if output_path is None:
        output_path = ASSETS_IMAGES_DIR / f"{post_file.stem}_diagram.png"

    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 다이어그램 생성
    generator = DIAGRAM_GENERATORS.get(diagram_type)
    if generator is None:
        log_message(f"지원하지 않는 다이어그램 유형: {diagram_type}", "ERROR")
        log_message(f"지원 유형: {', '.join(DIAGRAM_GENERATORS.keys())}")
        return False

    # 영어 제목으로 변환 (diagrams는 영어 제목 권장)
    english_title = f"AWS {diagram_type.upper()} Architecture"

    log_message(f"다이어그램 생성 시작: {diagram_type}")
    log_message(f"포스트: {post_file.name}")
    log_message(f"출력: {output_path}")

    return generator(english_title, output_path)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="AWS 아키텍처 다이어그램 생성")
    parser.add_argument("post_file", nargs="?", help="포스트 파일 경로")
    parser.add_argument("--type", "-t", choices=list(DIAGRAM_GENERATORS.keys()) + ["auto"],
                        default="auto", help="다이어그램 유형 (기본값: auto)")
    parser.add_argument("--output", "-o", help="출력 파일 경로")
    parser.add_argument("--list-types", action="store_true", help="지원 다이어그램 유형 목록")

    args = parser.parse_args()

    if args.list_types:
        print("지원 다이어그램 유형:")
        for dtype, keywords in KEYWORD_TYPE_MAP.items():
            print(f"  - {dtype}: {', '.join(keywords[:5])}...")
        return

    if not args.post_file:
        # 최신 포스트 찾기
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not posts:
            log_message("포스트 파일을 찾을 수 없습니다.", "ERROR")
            sys.exit(1)
        post_file = posts[0]
        log_message(f"최신 포스트 사용: {post_file.name}")
    else:
        post_file = Path(args.post_file)
        if not post_file.is_absolute():
            # _posts 디렉토리에서 찾기
            if (POSTS_DIR / post_file.name).exists():
                post_file = POSTS_DIR / post_file.name
            elif (POSTS_DIR / post_file).exists():
                post_file = POSTS_DIR / post_file

    if not post_file.exists():
        log_message(f"파일을 찾을 수 없습니다: {post_file}", "ERROR")
        sys.exit(1)

    output_path = Path(args.output) if args.output else None

    success = generate_diagram(post_file, args.type, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
