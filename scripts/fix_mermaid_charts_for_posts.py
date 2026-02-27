#!/usr/bin/env python3
"""
2025년 포스팅들의 머메이드 차트를 포스팅 내용에 맞게 재생성하는 스크립트

각 포스팅의 내용을 분석하여 적절한 머메이드 차트를 생성하고,
이미지로 변환하여 올바른 위치에 배치합니다.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
DIAGRAMS_DIR = IMAGES_DIR / "diagrams"


def log_message(message: str, level: str = "INFO"):
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


def analyze_post_content(post_file: Path) -> Dict:
    """포스팅 내용을 분석하여 필요한 차트 정보 추출"""
    try:
        with open(post_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        log_message(f"❌ 파일 읽기 실패: {str(e)}", "ERROR")
        return {}

    # 이미지 태그에서 차트 정보 추출
    image_pattern = r'<img src="\{\{ \'([^\']+mermaid_chart_\d+\.png)\' \| relative_url \}\}" alt="([^"]+)"'
    images = re.findall(image_pattern, content)

    # 각 이미지 주변 텍스트 분석
    chart_info = []
    for img_path, alt_text in images:
        # 이미지 경로에서 차트 번호 추출
        chart_match = re.search(r"mermaid_chart_(\d+)", img_path)
        if not chart_match:
            continue

        chart_num = int(chart_match.group(1))

        # 이미지 주변 텍스트 찾기 (이미지 앞 10줄, 뒤 5줄)
        img_pattern = re.escape(
            f'<img src="{{{{ \'{img_path}\' | relative_url }}}}" alt="{alt_text}"'
        )
        img_match = re.search(img_pattern, content)
        if img_match:
            start_pos = max(0, img_match.start() - 2000)  # 앞 2000자
            end_pos = min(len(content), img_match.end() + 1000)  # 뒤 1000자
            context = content[start_pos:end_pos]

            # 이미지 앞 텍스트에서 설명 추출
            before_text = content[max(0, img_match.start() - 500) : img_match.start()]
            after_text = content[
                img_match.end() : min(len(content), img_match.end() + 500)
            ]

            # 제목이나 설명 찾기
            title_match = re.search(r"###?\s+(.+?)(?:\n|$)", before_text[-300:])
            title = title_match.group(1).strip() if title_match else ""

            # 설명 문장 찾기
            desc_match = re.search(
                r"([^。\n]+(?:보안|차트|다이어그램|프로세스|워크플로우|아키텍처|구조|전략|사이클|레이어)[^。\n]*)",
                before_text[-200:],
            )
            description = desc_match.group(1).strip() if desc_match else ""

            chart_info.append(
                {
                    "chart_num": chart_num,
                    "img_path": img_path,
                    "alt_text": alt_text,
                    "title": title,
                    "description": description,
                    "context": context,
                }
            )

    return {"post_file": post_file, "charts": chart_info, "content": content}


def generate_mermaid_chart(chart_info: Dict, post_title: str) -> Optional[str]:
    """포스팅 내용에 맞는 머메이드 차트 생성"""
    title = chart_info.get("title", "")
    description = chart_info.get("description", "")
    context = chart_info.get("context", "")

    # 포스팅 제목과 차트 정보를 기반으로 적절한 차트 생성
    chart_type = determine_chart_type(title, description, context, post_title)

    if not chart_type:
        return None

    return create_mermaid_code(chart_type, title, description, context)


def determine_chart_type(
    title: str, description: str, context: str, post_title: str
) -> Optional[str]:
    """차트 타입 결정"""
    text = (title + " " + description + " " + context).lower()

    # DevSecOps 사이클
    if any(
        keyword in text
        for keyword in ["devsecops", "devops", "cicd", "파이프라인", "사이클"]
    ):
        return "devsecops_cycle"

    # Defense in Depth
    if any(
        keyword in text for keyword in ["defense in depth", "다층", "레이어", "방어"]
    ):
        return "defense_in_depth"

    # User Namespaces
    if any(keyword in text for keyword in ["user namespace", "네임스페이스", "격리"]):
        return "user_namespaces"

    # 인프라 구조
    if any(
        keyword in text
        for keyword in ["인프라", "infrastructure", "네트워크", "컴퓨팅", "스토리지"]
    ):
        return "infrastructure"

    # 보안 아키텍처
    if any(
        keyword in text for keyword in ["아키텍처", "architecture", "보안", "security"]
    ):
        return "security_architecture"

    # 워크플로우
    if any(
        keyword in text for keyword in ["워크플로우", "workflow", "프로세스", "process"]
    ):
        return "workflow"

    return None


def create_mermaid_code(
    chart_type: str, title: str, description: str, context: str
) -> str:
    """머메이드 차트 코드 생성"""

    if chart_type == "devsecops_cycle":
        return """```mermaid
graph LR
    A[Plan<br/>계획] --> B[Code<br/>코딩]
    B --> C[Build<br/>빌드]
    C --> D[Test<br/>테스트]
    D --> E[Release<br/>릴리스]
    E --> F[Deploy<br/>배포]
    F --> G[Operate<br/>운영]
    G --> H[Monitor<br/>모니터링]
    H --> A
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#00BCD4,color:#fff
    style F fill:#F44336,color:#fff
    style G fill:#795548,color:#fff
    style H fill:#607D8B,color:#fff
```"""

    elif chart_type == "defense_in_depth":
        return """```mermaid
graph TB
    subgraph Network["네트워크 레이어<br/>Network Layer"]
        N1[VPC]
        N2[Security Group]
        N3[NACL]
    end
    
    subgraph Application["애플리케이션 레이어<br/>Application Layer"]
        A1[WAF]
        A2[API Gateway]
        A3[Load Balancer]
    end
    
    subgraph Data["데이터 레이어<br/>Data Layer"]
        D1[암호화<br/>Encryption]
        D2[접근 제어<br/>Access Control]
        D3[백업<br/>Backup]
    end
    
    subgraph Monitoring["모니터링 레이어<br/>Monitoring Layer"]
        M1[CloudTrail]
        M2[CloudWatch]
        M3[GuardDuty]
    end
    
    Network --> Application
    Application --> Data
    Data --> Monitoring
    
    style Network fill:#4CAF50,color:#fff
    style Application fill:#2196F3,color:#fff
    style Data fill:#FF9800,color:#fff
    style Monitoring fill:#9C27B0,color:#fff
```"""

    elif chart_type == "user_namespaces":
        return """```mermaid
graph TB
    subgraph Container["컨테이너 내부"]
        C1[Root User<br/>UID 0]
    end
    
    subgraph Host["호스트 시스템"]
        H1[Non-privileged User<br/>UID 1000]
    end
    
    C1 -->|매핑| H1
    
    style Container fill:#F44336,color:#fff
    style Host fill:#4CAF50,color:#fff
```"""

    elif chart_type == "infrastructure":
        return """```mermaid
graph TB
    subgraph Network["네트워크"]
        N1[VPC]
        N2[서브넷]
        N3[라우팅]
    end
    
    subgraph Compute["컴퓨팅"]
        C1[EC2]
        C2[Lambda]
        C3[컨테이너]
    end
    
    subgraph Storage["스토리지"]
        S1[S3]
        S2[EBS]
        S3[EFS]
    end
    
    Network --> Compute
    Compute --> Storage
    
    style Network fill:#4CAF50,color:#fff
    style Compute fill:#2196F3,color:#fff
    style Storage fill:#FF9800,color:#fff
```"""

    elif chart_type == "security_architecture":
        return """```mermaid
graph TB
    subgraph IAM["IAM"]
        I1[사용자]
        I2[역할]
        I3[정책]
    end
    
    subgraph Network["네트워크 보안"]
        N1[VPC]
        N2[방화벽]
        N3[VPN]
    end
    
    subgraph Data["데이터 보안"]
        D1[암호화]
        D2[접근 제어]
        D3[백업]
    end
    
    IAM --> Network
    Network --> Data
    
    style IAM fill:#4CAF50,color:#fff
    style Network fill:#2196F3,color:#fff
    style Data fill:#FF9800,color:#fff
```"""

    elif chart_type == "workflow":
        return """```mermaid
graph LR
    A[시작] --> B[단계 1]
    B --> C[단계 2]
    C --> D[단계 3]
    D --> E[완료]
    
    style A fill:#4CAF50,color:#fff
    style E fill:#4CAF50,color:#fff
```"""

    return None


def process_post(post_file: Path) -> bool:
    """포스팅 처리"""
    log_message(f"📄 포스팅 분석: {post_file.name}")

    # 포스팅 내용 분석
    post_info = analyze_post_content(post_file)
    if not post_info or not post_info.get("charts"):
        log_message("💡 차트 정보가 없습니다.", "INFO")
        return True

    charts = post_info["charts"]
    log_message(f"📊 {len(charts)}개의 차트 발견")

    # 포스팅 제목 추출
    with open(post_file, "r", encoding="utf-8") as f:
        frontmatter_match = re.search(r'^title:\s*"([^"]+)"', f.read(), re.MULTILINE)
        post_title = frontmatter_match.group(1) if frontmatter_match else ""

    # 각 차트에 대해 적절한 머메이드 코드 생성
    post_stem = post_file.stem
    post_diagrams_dir = DIAGRAMS_DIR / post_stem
    post_diagrams_dir.mkdir(parents=True, exist_ok=True)

    for chart_info in charts:
        chart_num = chart_info["chart_num"]
        log_message(f"  📊 차트 {chart_num} 분석 중...", "DIAGRAM")

        # 적절한 머메이드 차트 생성
        mermaid_code = generate_mermaid_chart(chart_info, post_title)

        if mermaid_code:
            # 이미지 파일 경로
            image_filename = f"{post_stem}_mermaid_chart_{chart_num}.png"
            image_path = post_diagrams_dir / image_filename

            # 머메이드 차트를 이미지로 변환
            import sys

            sys.path.insert(0, str(Path(__file__).parent))
            from convert_mermaid_to_image import convert_mermaid_to_image

            # 머메이드 코드에서 ```mermaid 제거
            chart_content = (
                mermaid_code.replace("```mermaid\n", "").replace("```", "").strip()
            )

            if convert_mermaid_to_image(chart_content, image_path):
                log_message(f"  ✅ 차트 {chart_num} 이미지 생성 완료", "SUCCESS")
            else:
                log_message(f"  ⚠️ 차트 {chart_num} 이미지 생성 실패", "WARNING")
        else:
            log_message(f"  ⚠️ 차트 {chart_num} 타입을 결정할 수 없습니다", "WARNING")

    return True


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="2025년 포스팅들의 머메이드 차트를 포스팅 내용에 맞게 재생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--all-2025", action="store_true", help="모든 2025년 포스팅 처리"
    )
    parser.add_argument("post_file", nargs="?", help="처리할 포스팅 파일")

    args = parser.parse_args()

    if args.all_2025:
        # 2025년 포스팅 모두 처리
        post_files = sorted(POSTS_DIR.glob("2025-*.md"))
        log_message(f"📊 {len(post_files)}개 2025년 포스팅 처리 시작", "INFO")

        for post_file in post_files:
            try:
                process_post(post_file)
                print()  # 빈 줄
            except Exception as e:
                log_message(f"❌ 처리 실패: {post_file.name} - {str(e)}", "ERROR")
    elif args.post_file:
        # 특정 파일 처리
        post_path = Path(args.post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_path

        if not post_path.exists():
            log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
            sys.exit(1)

        process_post(post_path)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
