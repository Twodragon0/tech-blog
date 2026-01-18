#!/usr/bin/env python3
"""
포스트에서 누락된 다이어그램 이미지 생성 스크립트

포스트 파일을 분석하여 참조된 다이어그램 이미지가 없는 경우,
Gemini API를 사용하여 이미지를 생성합니다.

사용법:
    python3 scripts/generate_missing_diagrams.py _posts/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.md
"""

import os
import re
import sys
import json
import base64
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
DIAGRAMS_DIR = IMAGES_DIR / "diagrams"

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_IMAGE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
GEMINI_IMAGE_PRO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent"
USE_PRO_MODEL = os.getenv("USE_GEMINI_PRO_IMAGE", "false").lower() == "true"


def log_message(message: str, level: str = "INFO"):
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DIAGRAM": "📊"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")


def extract_diagram_references(content: str) -> List[Tuple[str, str]]:
    """
    마크다운에서 다이어그램 이미지 참조 추출
    
    Returns:
        List of (image_path, alt_text) tuples
    """
    pattern = r'!\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    diagrams = []
    for alt_text, image_path in matches:
        # diagrams 폴더의 이미지만 추출
        if '/diagrams/' in image_path or 'diagrams/' in image_path:
            diagrams.append((image_path, alt_text))
    
    return diagrams


def check_image_exists(image_path: str) -> Tuple[bool, Optional[Path]]:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False, None
    
    # 경로 정규화
    if image_path.startswith("/assets/images/"):
        image_file = PROJECT_ROOT / image_path.lstrip("/")
    elif image_path.startswith("assets/images/"):
        image_file = PROJECT_ROOT / image_path
    else:
        # 상대 경로인 경우
        image_file = DIAGRAMS_DIR / Path(image_path).name
    
    return image_file.exists(), image_file


def generate_diagram_prompt(alt_text: str, image_path: str, content_context: str = "") -> str:
    """다이어그램 이미지 생성 프롬프트 생성"""
    
    # 이미지 경로에서 다이어그램 타입 추출
    diagram_type = Path(image_path).stem
    
    # VM vs Container 비교 특별 처리
    if "vm_vs_container" in diagram_type.lower() or "vm vs container" in alt_text.lower():
        prompt = """Create a professional technical diagram comparing Virtual Machine (VM) and Container architectures side by side.

Requirements:
- Style: Clean, minimalist technical architecture diagram
- Layout: Two columns side by side (VM on left, Container on right)
- Colors: 
  - VM side: Use red/orange tones (#FF6B6B, #FFA07A) for hypervisor layer
  - Container side: Use blue/green tones (#4ECDC4, #95E1D3) for container runtime
  - Host OS: Gray (#95A5A6)
  - Hardware: Dark gray (#34495E)
- Components to show:
  Left (VM Architecture):
    - Top: Multiple applications (App 1, App 2, App 3)
    - Middle: Guest OS layers (Guest OS 1, Guest OS 2, Guest OS 3) - each in different colored boxes
    - Bottom: Hypervisor layer (highlighted in red/orange)
    - Bottom: Host OS
    - Bottom: Hardware
  
  Right (Container Architecture):
    - Top: Multiple applications (App 1, App 2, App 3)
    - Middle: Container Runtime (Docker/containerd) - single layer in blue/green
    - Bottom: Host OS (shared)
    - Bottom: Hardware (shared)
- Show arrows/connections between layers
- Include Korean labels where appropriate: "가상머신", "컨테이너", "하이퍼바이저", "컨테이너 런타임"
- Professional tech blog style
- High resolution (1200x800px minimum, 300 DPI)
- Clear visual distinction between VM (heavier, more layers) and Container (lighter, fewer layers)
"""
    elif "container_isolation" in diagram_type.lower() or "격리" in alt_text:
        prompt = """Create a professional technical diagram showing container isolation mechanisms.

Requirements:
- Style: Clean, minimalist technical architecture diagram
- Show: Namespaces, Cgroups, Union File Systems
- Colors: Blue (#3498DB) for namespaces, Green (#2ECC71) for cgroups, Orange (#E67E22) for union file systems
- Include Korean labels: "네임스페이스", "Cgroups", "유니온 파일시스템"
- Professional tech blog style
- High resolution (1200x800px minimum, 300 DPI)
"""
    elif "kubernetes" in diagram_type.lower():
        prompt = f"""Create a professional Kubernetes architecture diagram.

Title: {alt_text}

Requirements:
- Style: Clean, minimalist Kubernetes architecture diagram
- Colors: Kubernetes blue (#326CE5), Green (#00AA44) for pods, Orange (#FF6600) for services
- Include Korean labels where appropriate
- Professional tech blog style
- High resolution (1200x800px minimum, 300 DPI)
"""
    else:
        # 일반 다이어그램
        prompt = f"""Create a professional technical diagram for a tech blog.

Title: {alt_text}
Diagram Type: {diagram_type}

Requirements:
- Style: Clean, minimalist technical diagram
- Colors: Blue (#0066CC), Green (#00AA44), Orange (#FF6600)
- Include Korean labels where appropriate
- Professional tech blog style
- High resolution (1200x800px minimum, 300 DPI)
- Clear and readable design
"""
    
    return prompt.strip()


def generate_image_with_gemini(prompt: str, output_path: Path, max_retries: int = 3) -> bool:
    """Gemini API를 사용하여 이미지 생성"""
    if not GEMINI_API_KEY:
        log_message("Gemini API 키가 없어 이미지 생성을 건너뜁니다.", "WARNING")
        return False
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = 2 ** (attempt - 1)
                log_message(f"🔄 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            
            api_url = GEMINI_IMAGE_PRO_API_URL if USE_PRO_MODEL else GEMINI_IMAGE_API_URL
            url = f"{api_url}?key={GEMINI_API_KEY}"
            
            log_message("🎨 Gemini API로 이미지 생성 시도 중...")
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                }
            }
            
            response = requests.post(url, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                image_data = part["inlineData"]["data"]
                                image_mime_type = part["inlineData"]["mimeType"]
                                
                                try:
                                    image_bytes = base64.b64decode(image_data)
                                    
                                    if "png" in image_mime_type:
                                        output_path = output_path.with_suffix(".png")
                                    elif "jpeg" in image_mime_type or "jpg" in image_mime_type:
                                        output_path = output_path.with_suffix(".jpg")
                                    
                                    output_path.parent.mkdir(parents=True, exist_ok=True)
                                    with open(output_path, "wb") as f:
                                        f.write(image_bytes)
                                    
                                    log_message(f"✅ 이미지 생성 완료: {output_path.name} ({len(image_bytes)} bytes)", "SUCCESS")
                                    return True
                                except Exception as e:
                                    log_message(f"❌ 이미지 디코딩 실패: {str(e)}", "ERROR")
                                    if attempt < max_retries:
                                        continue
                                    return False
                            
                            if "url" in part:
                                image_url = part["url"]
                                log_message(f"📥 이미지 URL 받음, 다운로드 중: {image_url}")
                                
                                img_response = requests.get(image_url, timeout=60)
                                if img_response.status_code == 200:
                                    output_path.parent.mkdir(parents=True, exist_ok=True)
                                    with open(output_path, "wb") as f:
                                        f.write(img_response.content)
                                    log_message(f"✅ 이미지 다운로드 완료: {output_path.name}", "SUCCESS")
                                    return True
                                else:
                                    log_message(f"❌ 이미지 다운로드 실패: {img_response.status_code}", "ERROR")
                                    if attempt < max_retries:
                                        continue
                                    return False
                    
                    log_message("⚠️ Gemini API 응답에 이미지 데이터가 없습니다.", "WARNING")
                    if attempt < max_retries:
                        continue
                    return False
            else:
                error_text = response.text[:500] if response.text else "No error message"
                log_message(f"⚠️ Gemini API 호출 실패: HTTP {response.status_code}", "WARNING")
                log_message(f"   오류: {error_text}", "WARNING")
                
                if attempt < max_retries:
                    continue
                return False
                
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                log_message(f"⏱️ 타임아웃 발생, 재시도 예정...", "WARNING")
                continue
            log_message(f"❌ 이미지 생성 타임아웃 (120초 초과, {max_retries}회 시도)", "ERROR")
            return False
        except Exception as e:
            if attempt < max_retries:
                log_message(f"🔄 오류 발생, 재시도 예정: {str(e)[:100]}", "WARNING")
                continue
            log_message(f"⚠️ 이미지 생성 중 오류: {str(e)}", "WARNING")
            return False
    
    return False


def process_post(post_file: Path, force: bool = False) -> bool:
    """포스팅 파일 처리"""
    log_message(f"📄 포스팅 처리 시작: {post_file.name}")
    
    # 파일 읽기
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_message(f"❌ 파일 읽기 실패: {str(e)}", "ERROR")
        return False
    
    # 다이어그램 참조 추출
    diagram_refs = extract_diagram_references(content)
    log_message(f"📊 {len(diagram_refs)}개의 다이어그램 참조 발견")
    
    if not diagram_refs:
        log_message("💡 다이어그램 참조가 없습니다.", "INFO")
        return True
    
    # 누락된 이미지 찾기
    missing_diagrams = []
    for image_path, alt_text in diagram_refs:
        exists, image_file = check_image_exists(image_path)
        if not exists:
            missing_diagrams.append((image_path, alt_text, image_file))
            log_message(f"  ❌ 누락: {Path(image_path).name} - {alt_text}", "WARNING")
        elif force:
            missing_diagrams.append((image_path, alt_text, image_file))
            log_message(f"  🔄 강제 재생성: {Path(image_path).name}", "INFO")
        else:
            log_message(f"  ✅ 존재: {Path(image_path).name}", "SUCCESS")
    
    if not missing_diagrams:
        log_message("✅ 모든 다이어그램 이미지가 존재합니다.", "SUCCESS")
        return True
    
    log_message(f"📊 {len(missing_diagrams)}개의 누락된 다이어그램 이미지를 생성합니다.")
    
    # Gemini API 키 확인
    if not GEMINI_API_KEY:
        log_message("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.", "ERROR")
        log_message("💡 설정 방법: export GEMINI_API_KEY='your-key'", "INFO")
        return False
    
    # 각 다이어그램 이미지 생성
    success_count = 0
    for image_path, alt_text, image_file in missing_diagrams:
        log_message(f"\n📊 다이어그램 생성 중: {Path(image_path).name}")
        log_message(f"   설명: {alt_text}")
        
        # 프롬프트 생성
        prompt = generate_diagram_prompt(alt_text, image_path, content)
        
        # 이미지 생성
        if generate_image_with_gemini(prompt, image_file):
            success_count += 1
        else:
            log_message(f"⚠️ 이미지 생성 실패: {Path(image_path).name}", "WARNING")
    
    log_message(f"\n📊 처리 완료: {success_count}/{len(missing_diagrams)}개 다이어그램 생성 성공", "SUCCESS")
    return success_count == len(missing_diagrams)


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="누락된 다이어그램 이미지 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 특정 포스팅 처리
  python3 scripts/generate_missing_diagrams.py _posts/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.md
  
  # 강제 재생성
  python3 scripts/generate_missing_diagrams.py _posts/2026-01-15-...md --force
        """
    )
    
    parser.add_argument(
        "post_file",
        help="처리할 포스팅 파일"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="이미지가 있어도 강제로 재생성"
    )
    
    args = parser.parse_args()
    
    # 파일 경로 처리
    post_path = Path(args.post_file)
    if not post_path.is_absolute():
        post_path = PROJECT_ROOT / post_path
    
    if not post_path.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
        sys.exit(1)
    
    # 처리
    success = process_post(post_path, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
