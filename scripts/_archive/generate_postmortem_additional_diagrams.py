#!/usr/bin/env python3
"""
Post-Mortem Next.js SSR Error Incident 추가 다이어그램 생성 스크립트
Mermaid 다이어그램을 대체할 PNG 이미지 생성
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
    from diagrams.aws.network import ALB
    from diagrams.aws.security import WAF
    from diagrams.generic.blank import Blank
    from diagrams.generic.device import Mobile
    from diagrams.k8s.compute import Pod
    from diagrams.k8s.network import Service
    from diagrams.onprem.client import Client
    from diagrams.saas.cdn import Cloudflare
    DIAGRAMS_AVAILABLE = True
except ImportError as e:
    print("❌ diagrams 라이브러리 설치 필요: pip install diagrams graphviz")
    print(f"오류: {e}")
    sys.exit(1)

# 출력 디렉토리 생성
ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def generate_ssr_csr_comparison():
    """SSR vs CSR 환경 비교 다이어그램"""
    print("📊 SSR vs CSR 환경 비교 다이어그램 생성 중...")

    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_ssr_csr_comparison.png"

    with Diagram(
        "SSR vs CSR Environment Comparison",
        filename=str(output_path.with_suffix('')),
        show=False,
        direction="LR",
        graph_attr={"fontsize": "14", "bgcolor": "white"},
        outformat="png",
    ):
        # 클라이언트 사이드
        with Cluster("Client Side (Browser)"):
            browser = Client("Browser")
            location_ok = Blank("location ✅")
            window_ok = Blank("window ✅")
            browser >> location_ok
            browser >> window_ok

        # 서버 사이드
        with Cluster("Server Side (Node.js)"):
            nodejs = Blank("Node.js")
            location_no = Blank("location ❌")
            window_no = Blank("window ❌")
            nodejs >> location_no
            nodejs >> window_no

        # Next.js 렌더링
        with Cluster("Next.js Rendering"):
            ssr = Blank("SSR\nServer Side")
            csr = Blank("CSR\nClient Side")

        # 연결
        ssr >> nodejs
        csr >> browser

    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def generate_mobile_x_flow():
    """모바일 x.com 플로우 다이어그램"""
    print("📊 모바일 x.com 플로우 다이어그램 생성 중...")

    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_mobile_x_flow.png"

    with Diagram(
        "Mobile x.com Link Flow",
        filename=str(output_path.with_suffix('')),
        show=False,
        direction="TB",
        graph_attr={"fontsize": "14", "bgcolor": "white"},
        outformat="png",
    ):
        # 사용자
        user = Mobile("User\n(x.com)")

        # 링크 타입
        with Cluster("Link Types"):
            universal = Blank("Universal Links")
            deeplink = Blank("Deep Links")
            weblink = Blank("Web Links")

        # 앱/브라우저
        with Cluster("App/Browser"):
            xapp = Blank("X App\n(Installed)")
            xbrowser = Blank("X In-App\nBrowser")
            system = Client("System\nBrowser")

        # 서버
        with Cluster("Server"):
            ssr = Blank("Next.js SSR")
            location = Blank("location 접근")
            error = Blank("ReferenceError")

        # 연결
        user >> universal
        user >> deeplink
        user >> weblink

        universal >> xapp
        deeplink >> xapp
        weblink >> system

        xapp >> xbrowser
        xbrowser >> ssr
        system >> ssr

        ssr >> location
        location >> error

    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def generate_cascade_reaction():
    """연쇄 반응 시퀀스 다이어그램"""
    print("📊 연쇄 반응 시퀀스 다이어그램 생성 중...")

    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis_cascade_reaction.png"

    with Diagram(
        "Cascade Reaction Flow",
        filename=str(output_path.with_suffix('')),
        show=False,
        direction="TB",
        graph_attr={"fontsize": "14", "bgcolor": "white"},
        outformat="png",
    ):
        # 사용자
        user = Mobile("User\n(x.com)")

        # Cloudflare
        with Cluster("Cloudflare"):
            cf = Cloudflare("Cloudflare")
            waf = WAF("WAF")
            block = Blank("IP Block\n403")
            pass_through = Blank("Pass Through")

        # ALB
        with Cluster("AWS ALB"):
            alb = ALB("ALB")
            healthcheck = Blank("Health Check\nFailed")
            targetgroup = Blank("Target Group\nUnhealthy")

        # Kubernetes
        with Cluster("Kubernetes"):
            service = Service("Service")
            pod = Pod("Pod\nNext.js SSR")

        # 에러
        with Cluster("Error"):
            ssr = Blank("SSR Rendering")
            location = Blank("location 접근")
            error = Blank("ReferenceError")
            status500 = Blank("500 Error")

        # 연결
        user >> cf
        cf >> waf
        waf >> block
        waf >> pass_through

        block >> status500
        pass_through >> alb

        alb >> healthcheck
        healthcheck >> targetgroup
        targetgroup >> service

        service >> pod
        pod >> ssr
        ssr >> location
        location >> error
        error >> status500

        # 피드백 루프
        status500 >> healthcheck

    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def main():
    """메인 함수"""
    print("🚀 Post-Mortem Next.js SSR Error Incident 추가 다이어그램 생성 시작\n")

    results = []

    # 1. SSR vs CSR 비교
    results.append(generate_ssr_csr_comparison())

    # 2. 모바일 x.com 플로우
    results.append(generate_mobile_x_flow())

    # 3. 연쇄 반응
    results.append(generate_cascade_reaction())

    print("\n" + "="*60)
    if all(results):
        print("✅ 모든 추가 다이어그램 생성 완료!")
        sys.exit(0)
    else:
        print("❌ 일부 다이어그램 생성 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
