#!/usr/bin/env python3
"""
Post-Mortem Next.js SSR Error Incident 다이어그램 생성 스크립트
포스트에 포함된 Python diagrams 코드를 실행하여 이미지를 생성합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# diagrams 라이브러리 임포트
try:
    from diagrams import Cluster, Diagram, Edge
    from diagrams.aws.compute import ECR
    from diagrams.aws.network import ALB, CloudFront
    from diagrams.aws.security import WAF
    from diagrams.generic.blank import Blank
    from diagrams.generic.device import Mobile, Tablet
    from diagrams.k8s.compute import Deployment, Pod
    from diagrams.k8s.controlplane import APIServer
    from diagrams.k8s.network import Ingress, Service
    from diagrams.onprem.ci import GithubActions
    from diagrams.onprem.client import Client, Users
    from diagrams.onprem.container import Docker
    from diagrams.onprem.vcs import Github
    from diagrams.programming.framework import React
    from diagrams.saas.cdn import Cloudflare
    DIAGRAMS_AVAILABLE = True
except ImportError as e:
    print("❌ diagrams 라이브러리 설치 필요: pip install diagrams graphviz")
    print(f"오류: {e}")
    sys.exit(1)

# 출력 디렉토리 생성
ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def generate_architecture_diagram():
    """전체 아키텍처 다이어그램 생성"""
    print("📊 전체 아키텍처 다이어그램 생성 중...")

    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_architecture_diagram.png"

    with Diagram(
        "Next.js SSR Error Incident Architecture",
        filename=str(output_path.with_suffix('')),  # 확장자 제거 (diagrams가 자동 추가)
        show=False,
        direction="TB",
        graph_attr={"fontsize": "14", "bgcolor": "white"},
        outformat="png",
    ):
        # 클라이언트 환경
        with Cluster("Client Environment"):
            mobile = Mobile("Mobile x.com")
            desktop = Client("Desktop Browser")
            inapp = Tablet("In-App Browser")

        # CDN & 보안
        with Cluster("CDN & Security"):
            cloudflare = Cloudflare("Cloudflare")
            waf = WAF("WAF Rules")
            ratelimit = Blank("Rate Limiting")

        # AWS 인프라
        with Cluster("AWS Infrastructure"):
            alb = ALB("Application Load Balancer")
            targetgroup = Blank("Target Group")
            healthcheck = Blank("Health Check")

        # Kubernetes 클러스터
        with Cluster("Kubernetes Cluster"):
            ingress = Ingress("Ingress Controller")
            service = Service("Service")

            with Cluster("Pods"):
                pod1 = Pod("Pod 1\nNext.js SSR")
                pod2 = Pod("Pod 2\nNext.js SSR")
                pod3 = Pod("Pod 3\nNext.js SSR")

        # 에러 발생 지점
        with Cluster("Error Point"):
            ssr = Blank("SSR Rendering")
            location = Blank("location 접근")
            referror = Blank("ReferenceError")

        # 연결
        mobile >> cloudflare
        desktop >> cloudflare
        inapp >> cloudflare

        cloudflare >> waf
        waf >> ratelimit
        ratelimit >> alb

        alb >> targetgroup
        targetgroup >> healthcheck
        healthcheck >> ingress

        ingress >> service
        service >> pod1
        service >> pod2
        service >> pod3

        pod1 >> ssr
        pod2 >> ssr
        pod3 >> ssr

        ssr >> location
        location >> referror

    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def generate_deployment_diagram():
    """배포 프로세스 다이어그램 생성"""
    print("📊 배포 프로세스 다이어그램 생성 중...")

    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_deployment_diagram.png"

    with Diagram(
        "Deployment Process Flow",
        filename=str(output_path.with_suffix('')),  # 확장자 제거
        show=False,
        direction="LR",
        graph_attr={"fontsize": "14", "bgcolor": "white"},
        outformat="png",
    ):
        # 개발자
        developer = Blank("Developer")

        # 소스 코드 관리
        with Cluster("Source Code"):
            github = Github("GitHub\nexample-frontend")
            main_branch = Blank("main branch")

        # CI/CD 파이프라인
        with Cluster("CI/CD Pipeline"):
            actions = GithubActions("GitHub Actions\nbuild-and-deploy.yml")
            build = Blank("Build\nnpm run build")
            docker_build = Docker("Docker Build\nImage: v1.0.1")

        # 컨테이너 레지스트리
        with Cluster("Container Registry"):
            ecr = ECR("ECR\nImage Storage")

        # Kubernetes 배포
        with Cluster("Kubernetes"):
            api = APIServer("Kubernetes\nAPI Server")
            deployment = Deployment("Deployment\nweb-app")
            pod = Pod("Pod\nNext.js SSR")

        # 연결
        developer >> github
        github >> main_branch
        main_branch >> actions
        actions >> build
        build >> docker_build
        docker_build >> ecr
        ecr >> api
        api >> deployment
        deployment >> pod

    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def generate_error_path_diagram():
    """5XX 에러 발생 경로 다이어그램 생성"""
    print("📊 5XX 에러 발생 경로 다이어그램 생성 중...")

    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_error_path_diagram.png"

    with Diagram(
        "5XX Error Path",
        filename=str(output_path.with_suffix('')),  # 확장자 제거
        show=False,
        direction="TB",
        graph_attr={"fontsize": "14", "bgcolor": "white"},
        outformat="png",
    ):
        # 클라이언트
        mobile = Mobile("Mobile x.com")
        desktop = Client("Desktop Browser")

        # Cloudflare
        with Cluster("Cloudflare"):
            cloudflare = Cloudflare("Cloudflare")
            waf = WAF("WAF")
            block = Blank("IP 차단")
            pass_through = Blank("요청 통과")

        # ALB
        with Cluster("AWS ALB"):
            alb = ALB("Application Load Balancer")
            ingress = Ingress("Ingress")
            healthcheck = Blank("Health Check\n실패")
            targetgroup = Blank("Target Group\nUnhealthy")

        # Kubernetes
        with Cluster("Kubernetes"):
            service = Service("Service")
            pod1 = Pod("Pod 1")
            pod2 = Pod("Pod 2")
            pod3 = Pod("Pod 3")

        # 에러
        with Cluster("Error"):
            ssr = Blank("SSR 렌더링")
            location = Blank("location 접근")
            referror = Blank("ReferenceError")
            status500 = Blank("500 에러")

        # 연결
        mobile >> cloudflare
        desktop >> cloudflare

        cloudflare >> waf
        waf >> block
        waf >> pass_through

        block >> status500
        pass_through >> alb

        alb >> ingress
        ingress >> healthcheck
        healthcheck >> targetgroup
        targetgroup >> service

        service >> pod1
        service >> pod2
        service >> pod3

        pod1 >> ssr
        pod2 >> ssr
        pod3 >> ssr

        ssr >> location
        location >> referror
        referror >> status500

    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def main():
    """메인 함수"""
    print("🚀 Post-Mortem Next.js SSR Error Incident 다이어그램 생성 시작\n")

    results = []

    # 1. 전체 아키텍처 다이어그램
    results.append(generate_architecture_diagram())

    # 2. 배포 프로세스 다이어그램
    results.append(generate_deployment_diagram())

    # 3. 5XX 에러 발생 경로 다이어그램
    results.append(generate_error_path_diagram())

    print("\n" + "="*60)
    if all(results):
        print("✅ 모든 다이어그램 생성 완료!")
        sys.exit(0)
    else:
        print("❌ 일부 다이어그램 생성 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
