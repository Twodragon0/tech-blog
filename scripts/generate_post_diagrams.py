#!/usr/bin/env python3
"""
포스팅별 다이어그램 자동 생성 및 삽입 스크립트

포스팅 내용을 분석하여 Python diagrams, matplotlib, graphviz 등을 활용하여
다양한 다이어그램을 생성하고 포스팅에 자동으로 삽입합니다.

사용법:
    python3 scripts/generate_post_diagrams.py [포스트파일명]
    python3 scripts/generate_post_diagrams.py --all  # 모든 포스트 처리
    python3 scripts/generate_post_diagrams.py --post "Docker_Kubernetes"  # 특정 포스트만

필요 패키지:
    pip install diagrams graphviz matplotlib seaborn networkx pillow
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import yaml

# frontmatter 라이브러리 사용 시도, 없으면 직접 파싱
try:
    import frontmatter
    FRONTMATTER_AVAILABLE = True
except ImportError:
    FRONTMATTER_AVAILABLE = False

# diagrams 라이브러리 임포트
try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import EC2, ECS, EKS, Lambda, Fargate
    from diagrams.aws.network import VPC, PrivateSubnet, PublicSubnet, InternetGateway, NATGateway, ELB, ALB, NLB, CloudFront
    from diagrams.aws.security import WAF, Shield, IAM, Guardduty, SecurityHub
    from diagrams.aws.database import RDS, Dynamodb, ElastiCache
    from diagrams.aws.storage import S3
    from diagrams.aws.general import Users
    from diagrams.onprem.client import Client
    from diagrams.onprem.container import Docker
    from diagrams.onprem.vcs import Github
    from diagrams.onprem.ci import GithubActions
    from diagrams.k8s.compute import Pod, Deployment
    from diagrams.k8s.network import Service, Ingress
    from diagrams.k8s.controlplane import APIServer
    from diagrams.generic.blank import Blank
    DIAGRAMS_AVAILABLE = True
except ImportError:
    DIAGRAMS_AVAILABLE = False
    print("⚠️ diagrams 라이브러리 설치 필요: pip install diagrams graphviz")

# matplotlib 임포트
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ matplotlib 설치 필요: pip install matplotlib")

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def log_message(message: str, level: str = "INFO") -> None:
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DIAGRAM": "📊"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")


# ============================================================================
# Docker/Kubernetes 보안 다이어그램 생성 함수들
# ============================================================================

def generate_docker_vs_vm_comparison(output_path: Path) -> bool:
    """VM vs Container 비교 다이어그램 (diagrams 사용)"""
    if not DIAGRAMS_AVAILABLE:
        return False
    
    try:
        with Diagram(
            "VM vs Container Comparison",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr={"fontsize": "14", "bgcolor": "white", "dpi": "150"},
        ):
            with Cluster("Virtual Machine (VM)"):
                host_os_vm = Blank("Host OS")
                hypervisor = Blank("Hypervisor")
                with Cluster("Guest OS 1"):
                    guest1 = Blank("App")
                with Cluster("Guest OS 2"):
                    guest2 = Blank("App")
            
            with Cluster("Container"):
                host_os_ct = Blank("Host OS")
                docker = Docker("Docker\nRuntime")
                with Cluster("Container 1"):
                    container1 = Blank("App")
                with Cluster("Container 2"):
                    container2 = Blank("App")
            
            host_os_vm >> hypervisor >> [guest1, guest2]
            host_os_ct >> docker >> [container1, container2]
        
        log_message(f"VM vs Container 비교 다이어그램 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"VM vs Container 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_kubernetes_architecture(output_path: Path) -> bool:
    """Kubernetes 아키텍처 다이어그램"""
    if not DIAGRAMS_AVAILABLE:
        return False
    
    try:
        with Diagram(
            "Kubernetes Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white", "dpi": "150"},
        ):
            with Cluster("Control Plane"):
                api_server = APIServer("API Server")
                etcd = Blank("etcd\nState Store")
                scheduler = Blank("Scheduler")
                controller = Blank("Controller\nManager")
            
            with Cluster("Worker Node 1"):
                kubelet1 = Blank("kubelet")
                kube_proxy1 = Blank("kube-proxy")
                with Cluster("Pods"):
                    pod1 = Pod("Pod 1")
                    pod2 = Pod("Pod 2")
            
            with Cluster("Worker Node 2"):
                kubelet2 = Blank("kubelet")
                kube_proxy2 = Blank("kube-proxy")
                with Cluster("Pods"):
                    pod3 = Pod("Pod 3")
                    pod4 = Pod("Pod 4")
            
            api_server >> etcd
            api_server >> scheduler
            api_server >> controller
            api_server >> kubelet1
            api_server >> kubelet2
            kubelet1 >> pod1
            kubelet1 >> pod2
            kubelet2 >> pod3
            kubelet2 >> pod4
        
        log_message(f"Kubernetes 아키텍처 다이어그램 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"Kubernetes 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_container_security_layers(output_path: Path) -> bool:
    """컨테이너 보안 레이어 다이어그램 (diagrams 사용)"""
    if not DIAGRAMS_AVAILABLE:
        return False
    
    try:
        with Diagram(
            "Container Security Layers (Defense in Depth)",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr={"fontsize": "14", "bgcolor": "white", "dpi": "150"},
        ):
            with Cluster("Security Layers"):
                image_scan = Blank("Image Scanning\nTrivy, Snyk")
                secret_mgmt = Blank("Secret Management\nK8s Secrets, Vault")
                non_root = Blank("Non-root User\nrunAsNonRoot")
                read_only = Blank("Read-only Filesystem\nreadOnlyRootFilesystem")
                cap_drop = Blank("Capabilities Drop\ncapabilities.drop: ALL")
                network_policy = Blank("Network Policies\nPod Isolation")
            
            app = Pod("Application\nContainer")
            
            image_scan >> secret_mgmt >> non_root >> read_only >> cap_drop >> network_policy >> app
        
        log_message(f"컨테이너 보안 레이어 다이어그램 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"컨테이너 보안 레이어 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_pod_security_standards(output_path: Path) -> bool:
    """Pod Security Standards 비교 다이어그램 (diagrams 사용)"""
    if not DIAGRAMS_AVAILABLE:
        return False
    
    try:
        with Diagram(
            "Pod Security Standards (PSS) Levels",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr={"fontsize": "14", "bgcolor": "white", "dpi": "150"},
        ):
            privileged = Blank("Privileged\nNo restrictions")
            baseline = Blank("Baseline\nMinimal security\nrequirements")
            restricted = Blank("Restricted\nStrongest security\npolicies")
            
            privileged >> baseline >> restricted
        
        log_message(f"Pod Security Standards 다이어그램 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"Pod Security Standards 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_user_namespaces_security(output_path: Path) -> bool:
    """User Namespaces 보안 효과 다이어그램 (diagrams 사용)"""
    if not DIAGRAMS_AVAILABLE:
        return False
    
    try:
        with Diagram(
            "User Namespaces Security: Before vs After",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr={"fontsize": "14", "bgcolor": "white", "dpi": "150"},
        ):
            with Cluster("Before: Container Escape = Host Root"):
                host_before = Blank("Host OS")
                container_before = Pod("Container\n(root)")
                escape = Blank("Escape = Root\nAccess")
            
            with Cluster("After: User Namespaces Isolation"):
                host_after = Blank("Host OS")
                namespace = Blank("User Namespace\nMapping")
                container_after = Pod("Container\n(root in namespace)")
                blocked = Blank("Escape Blocked\nNon-privileged User")
            
            host_before >> container_before >> escape
            host_after >> namespace >> container_after >> blocked
        
        log_message(f"User Namespaces 보안 다이어그램 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"User Namespaces 다이어그램 생성 실패: {e}", "ERROR")
        return False


def generate_devsecops_workflow(output_path: Path) -> bool:
    """DevSecOps 워크플로우 다이어그램"""
    if not DIAGRAMS_AVAILABLE:
        return False
    
    try:
        with Diagram(
            "DevSecOps Container Security Workflow",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr={"fontsize": "14", "bgcolor": "white", "dpi": "150"},
        ):
            dev = Users("Developer")
            
            with Cluster("Source Control"):
                github = Github("GitHub\nRepository")
            
            with Cluster("CI/CD Pipeline"):
                gh_actions = GithubActions("GitHub Actions")
                
                with Cluster("Security Scanning"):
                    trivy = Blank("Trivy\nImage Scan")
                    snyk = Blank("Snyk\nVulnerability")
                    hadolint = Blank("Hadolint\nDockerfile")
                
                with Cluster("Build"):
                    docker_build = Docker("Docker Build\nSecure Image")
            
            with Cluster("Container Registry"):
                ecr = ECS("ECR\nSigned Images")
            
            with Cluster("Kubernetes"):
                with Cluster("Security Policies"):
                    pss = Blank("Pod Security\nStandards")
                    network_policy = Blank("Network\nPolicies")
                    rbac = Blank("RBAC")
                
                eks = EKS("EKS Cluster")
                pod = Pod("Secure Pod")
            
            with Cluster("Runtime Security"):
                falco = Blank("Falco\nMonitoring")
                guardduty = Guardduty("GuardDuty")
            
            # 워크플로우
            dev >> github >> gh_actions
            gh_actions >> [trivy, snyk, hadolint]
            [trivy, snyk, hadolint] >> docker_build
            docker_build >> ecr
            ecr >> eks
            eks >> [pss, network_policy, rbac] >> pod
            pod >> falco
            falco >> guardduty
        
        log_message(f"DevSecOps 워크플로우 다이어그램 생성: {output_path}", "DIAGRAM")
        return True
    except Exception as e:
        log_message(f"DevSecOps 워크플로우 다이어그램 생성 실패: {e}", "ERROR")
        return False


# ============================================================================
# 포스팅 분석 및 다이어그램 생성
# ============================================================================

def extract_post_info(post_file: Path) -> Dict:
    """포스트 파일에서 정보 추출"""
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # frontmatter 파싱
        if FRONTMATTER_AVAILABLE:
            post = frontmatter.loads(content)
            return {
                'title': post.metadata.get('title', ''),
                'content': post.content,
                'tags': post.metadata.get('tags', []),
                'categories': post.metadata.get('categories', []),
            }
        else:
            # 직접 파싱 (간단한 YAML frontmatter)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    body_content = parts[2]
                    metadata = yaml.safe_load(yaml_content) or {}
                    return {
                        'title': metadata.get('title', ''),
                        'content': body_content,
                        'tags': metadata.get('tags', []),
                        'categories': metadata.get('categories', []),
                    }
            
            # frontmatter가 없으면 전체를 content로
            return {
                'title': '',
                'content': content,
                'tags': [],
                'categories': [],
            }
    except Exception as e:
        log_message(f"포스트 정보 추출 실패: {e}", "ERROR")
        return {}


def detect_required_diagrams(post_info: Dict) -> List[str]:
    """포스트 내용을 분석하여 필요한 다이어그램 목록 반환"""
    content = post_info.get('content', '').lower()
    title = post_info.get('title', '').lower()
    tags = ' '.join(post_info.get('tags', [])).lower()
    
    combined = content + ' ' + title + ' ' + tags
    
    required = []
    
    # Docker/Kubernetes 관련
    if any(kw in combined for kw in ['docker', 'container', 'vm vs container', '가상머신']):
        required.append('docker_vs_vm')
    
    if any(kw in combined for kw in ['kubernetes', 'k8s', 'pod', 'deployment', '클러스터']):
        required.append('kubernetes_architecture')
    
    if any(kw in combined for kw in ['보안', 'security', 'security context', '비루트', 'non-root']):
        required.append('container_security_layers')
    
    if any(kw in combined for kw in ['pod security', 'pss', 'restricted', 'baseline']):
        required.append('pod_security_standards')
    
    if any(kw in combined for kw in ['user namespace', 'hostusers', '격리']):
        required.append('user_namespaces')
    
    if any(kw in combined for kw in ['devsecops', 'ci/cd', '파이프라인', 'workflow']):
        required.append('devsecops_workflow')
    
    return required


def generate_diagrams_for_post(post_file: Path) -> Dict[str, Path]:
    """포스트에 필요한 다이어그램 생성"""
    post_info = extract_post_info(post_file)
    if not post_info:
        return {}
    
    required = detect_required_diagrams(post_info)
    if not required:
        log_message("필요한 다이어그램이 없습니다.", "WARNING")
        return {}
    
    # 출력 디렉토리 설정
    post_stem = post_file.stem
    output_dir = ASSETS_IMAGES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 다이어그램 생성 함수 매핑
    diagram_functions = {
        'docker_vs_vm': generate_docker_vs_vm_comparison,
        'kubernetes_architecture': generate_kubernetes_architecture,
        'container_security_layers': generate_container_security_layers,
        'pod_security_standards': generate_pod_security_standards,
        'user_namespaces': generate_user_namespaces_security,
        'devsecops_workflow': generate_devsecops_workflow,
    }
    
    generated = {}
    
    for diagram_type in required:
        if diagram_type not in diagram_functions:
            continue
        
        output_path = output_dir / f"{post_stem}_{diagram_type}.png"
        
        # 이미 존재하면 스킵
        if output_path.exists():
            log_message(f"이미 존재: {output_path.name}", "INFO")
            generated[diagram_type] = output_path
            continue
        
        log_message(f"다이어그램 생성 중: {diagram_type}", "INFO")
        func = diagram_functions[diagram_type]
        success = func(output_path)
        
        if success and output_path.exists():
            generated[diagram_type] = output_path
            log_message(f"생성 완료: {output_path.name}", "SUCCESS")
        else:
            log_message(f"생성 실패: {diagram_type}", "ERROR")
    
    return generated


def insert_diagrams_into_post(post_file: Path, diagrams: Dict[str, Path]) -> bool:
    """생성된 다이어그램을 포스트에 삽입"""
    if not diagrams:
        return False
    
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 다이어그램 삽입 위치 매핑 (더 유연한 패턴)
        insertion_points = {
            'docker_vs_vm': [
                ('##### **VM vs Container 비교**', '#####.*VM.*Container.*비교'),
                ('### **1.2 Container 이해**', '###.*Container.*이해'),
                ('VM vs Container', 'VM.*Container'),
            ],
            'kubernetes_architecture': [
                ('##### **Kubernetes 아키텍처**', '#####.*Kubernetes.*아키텍처'),
                ('### **1.3 Kubernetes 기본 개념**', '###.*Kubernetes.*기본'),
                ('Kubernetes 아키텍처', 'Kubernetes.*아키텍처'),
            ],
            'container_security_layers': [
                ('#### **2.1 Docker 이미지 보안**', '####.*Docker.*이미지.*보안'),
                ('### **🌐 2. 컨테이너 보안 Best Practices**', '###.*컨테이너.*보안'),
                ('Docker 이미지 보안', 'Docker.*이미지.*보안'),
            ],
            'pod_security_standards': [
                ('##### **PSS 레벨별 정책**', '#####.*PSS.*레벨'),
                ('#### **3.1 Pod Security Standards (PSS)**', '####.*Pod.*Security.*Standards'),
                ('Pod Security Standards', 'Pod.*Security.*Standards'),
            ],
            'user_namespaces': [
                ('##### **컨테이너 격리 강화**', '#####.*컨테이너.*격리'),
                ('#### **3.2 User Namespaces', '####.*User.*Namespaces'),
                ('User Namespaces', 'User.*Namespaces'),
            ],
            'devsecops_workflow': [
                ('#### **💡 멘토의 관점', '####.*멘토'),
                ('### **📝 5. 실전 보안 강화 사례**', '###.*실전.*보안'),
                ('DevSecOps', 'DevSecOps'),
            ],
        }
        
        modified = False
        
        for diagram_type, path in diagrams.items():
            if diagram_type not in insertion_points:
                continue
            
            # 이미지 경로 (상대 경로)
            image_path = f"/assets/images/{path.name}"
            
            # 이미 삽입되어 있는지 확인
            if image_path in content:
                log_message(f"이미 삽입됨: {path.name}", "INFO")
                continue
            
            # 마크다운 이미지 태그
            diagram_title = diagram_type.replace('_', ' ').title()
            image_markdown = f"\n\n![{diagram_title}]({image_path})\n*그림: {diagram_title}*\n\n"
            
            # 삽입 위치 찾기 (여러 패턴 시도)
            markers = insertion_points[diagram_type]
            inserted = False
            
            for exact_marker, pattern_marker in markers:
                # 정확한 마커 먼저 시도
                if exact_marker in content:
                    pattern = f"({re.escape(exact_marker)}[^\n]*\n)"
                    if re.search(pattern, content):
                        # 다음 줄이 비어있지 않으면 한 줄 더 추가
                        replacement = f"\\1{image_markdown}"
                        content = re.sub(pattern, replacement, content, count=1)
                        modified = True
                        inserted = True
                        log_message(f"다이어그램 삽입: {path.name} (위치: {exact_marker})", "SUCCESS")
                        break
                
                # 패턴 매칭 시도
                pattern = f"({pattern_marker}[^\n]*\n)"
                if re.search(pattern, content, re.IGNORECASE):
                    replacement = f"\\1{image_markdown}"
                    content = re.sub(pattern, replacement, content, count=1)
                    modified = True
                    inserted = True
                    log_message(f"다이어그램 삽입: {path.name} (패턴: {pattern_marker})", "SUCCESS")
                    break
            
            if not inserted:
                log_message(f"삽입 위치를 찾을 수 없음: {path.name}", "WARNING")
        
        if modified:
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(content)
            log_message(f"포스트 업데이트 완료: {post_file.name}", "SUCCESS")
            return True
        else:
            log_message("삽입할 위치를 찾을 수 없거나 이미 삽입되어 있습니다.", "WARNING")
            return False
    
    except Exception as e:
        log_message(f"포스트 업데이트 실패: {e}", "ERROR")
        return False


def main():
    parser = argparse.ArgumentParser(description="포스팅별 다이어그램 자동 생성 및 삽입")
    parser.add_argument("post_file", nargs='?', type=str,
                       help="포스트 파일 경로 또는 파일명")
    parser.add_argument("--all", "-a", action="store_true",
                       help="모든 포스트 처리")
    parser.add_argument("--post", "-p", type=str,
                       help="포스트 파일명 패턴 (부분 일치)")
    parser.add_argument("--no-insert", action="store_true",
                       help="다이어그램만 생성하고 포스트에 삽입하지 않음")
    
    args = parser.parse_args()
    
    if not DIAGRAMS_AVAILABLE and not MATPLOTLIB_AVAILABLE:
        print("\n필요 패키지 설치:")
        print("  pip install diagrams graphviz matplotlib")
        print("\nMac에서 graphviz 설치:")
        print("  brew install graphviz")
        sys.exit(1)
    
    # 포스트 파일 찾기
    post_files = []
    
    if args.all:
        post_files = list(POSTS_DIR.glob("*.md"))
    elif args.post:
        pattern = args.post.lower()
        post_files = [f for f in POSTS_DIR.glob("*.md") if pattern in f.name.lower()]
    elif args.post_file:
        post_path = Path(args.post_file)
        if post_path.is_absolute():
            post_files = [post_path]
        else:
            # 상대 경로 또는 파일명만 제공된 경우
            if (POSTS_DIR / post_path).exists():
                post_files = [POSTS_DIR / post_path]
            else:
                # 파일명으로 검색
                matches = list(POSTS_DIR.glob(f"*{post_path.name}*"))
                post_files = matches if matches else [post_path]
    else:
        parser.print_help()
        sys.exit(1)
    
    if not post_files:
        log_message("포스트 파일을 찾을 수 없습니다.", "ERROR")
        sys.exit(1)
    
    # 각 포스트 처리
    total = len(post_files)
    success_count = 0
    
    for idx, post_file in enumerate(post_files, 1):
        log_message(f"\n[{idx}/{total}] 포스트 처리: {post_file.name}", "INFO")
        
        # 다이어그램 생성
        diagrams = generate_diagrams_for_post(post_file)
        
        if diagrams:
            log_message(f"{len(diagrams)}개 다이어그램 생성 완료", "SUCCESS")
            
            # 포스트에 삽입
            if not args.no_insert:
                if insert_diagrams_into_post(post_file, diagrams):
                    success_count += 1
        else:
            log_message("생성된 다이어그램이 없습니다.", "WARNING")
    
    log_message(f"\n처리 완료: {success_count}/{total} 포스트", "SUCCESS")


if __name__ == "__main__":
    main()
