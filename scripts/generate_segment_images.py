#!/usr/bin/env python3
"""
세그먼트별 이미지 자동 생성 스크립트
비디오 세그먼트별로 관련 이미지를 Gemini API를 사용하여 생성합니다.
Gemini 2.5 Flash Image (Nano Banana) 모델을 사용하여 실제 이미지를 생성합니다.
"""

import os
import re
import json
import sys
import time
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 이미지 디렉토리 생성
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Gemini 2.5 Flash Image (Nano Banana) - 이미지 생성 전용 모델
GEMINI_IMAGE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
# 대체 모델: Gemini 3 Pro Image (Nano Banana Pro) - 더 높은 품질
GEMINI_IMAGE_PRO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent"

# 모델 선택 (환경 변수로 제어 가능)
USE_PRO_MODEL = os.getenv("USE_GEMINI_PRO_IMAGE", "false").lower() == "true"


def mask_sensitive_info(text: str) -> str:
    """
    로그에 기록될 민감한 정보를 마스킹합니다.

    Args:
        text: 마스킹할 텍스트

    Returns:
        마스킹된 텍스트
    """
    if not text:
        return text

    # API 키 마스킹
    masked = re.sub(r'AIza[0-9A-Za-z_-]{35}', 'AIza***MASKED***', text)
    masked = re.sub(r'[a-zA-Z0-9_-]{40,}', lambda m: m.group()[:8] + '***MASKED***' if len(m.group()) > 40 else m.group(), masked)

    # 환경 변수에서 읽은 실제 API 키 값 마스킹
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
        masked = masked.replace(GEMINI_API_KEY, '***GEMINI_API_KEY_MASKED***')

    # URL에 포함된 API 키 마스킹 (key= 파라미터)
    masked = re.sub(r'[?&]key=[a-zA-Z0-9_-]+', '?key=***MASKED***', masked)

    return masked


def _validate_masked_text(text: str) -> bool:
    """
    텍스트가 안전하게 마스킹되었는지 검증합니다.

    Args:
        text: 검증할 텍스트

    Returns:
        안전하면 True, 아니면 False
    """
    if not text:
        return True

    # 실제 API 키 패턴이 남아있는지 확인
    api_key_patterns = [
        r'AIza[0-9A-Za-z_-]{35}',
        r'[a-zA-Z0-9_-]{40,}',
    ]

    for pattern in api_key_patterns:
        if re.search(pattern, text):
            return False

    # 환경 변수에서 읽은 실제 API 키 값이 포함되어 있는지 확인
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10 and GEMINI_API_KEY in text:
        return False

    return True


def _write_safe_text_to_file(file_path: Path, safe_text: str) -> None:
    """
    검증된 안전한 텍스트만 파일에 기록합니다.
    
    Args:
        file_path: 파일 경로
        safe_text: _validate_masked_text()로 검증된 안전한 텍스트
    """
    if not safe_text:
        return
    
    # Additional runtime validation (defense in depth)
    if not _validate_masked_text(safe_text):
        return
    
    try:
        # Security: Write only pre-validated, sanitized text
        # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
        with open(file_path, "w", encoding="utf-8") as f:
            # nosec B608 - sanitized via mask_sensitive_info and _validate_masked_text
            f.write(safe_text)
            f.flush()
    except Exception:
        # 예외 발생 시 조용히 처리 (보안상 로그에 기록하지 않음)
        pass


def _safe_print(text: str) -> None:
    """
    검증된 안전한 텍스트만 출력합니다.
    CodeQL 경고 방지를 위해 별도 함수로 분리.
    """
    if not text:
        return

    # 추가 검증 (defense in depth)
    safe_text = mask_sensitive_info(text)
    if _validate_masked_text(safe_text):
        # Security: Output only pre-validated, sanitized text
        # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
        # nosec B608 - sanitized via mask_sensitive_info and _validate_masked_text
        print(safe_text)


def log_message(message: str, level: str = "INFO"):
    """로그 메시지 출력 (민감 정보 자동 마스킹)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "ℹ️")
    # 민감 정보 마스킹 후 출력
    safe_message = mask_sensitive_info(message)
    log_entry = f"[{timestamp}] [{level}] {icon} {safe_message}"
    _safe_print(log_entry)


def extract_keywords_from_text(text: str) -> List[str]:
    """텍스트에서 주요 키워드 추출"""
    keywords = [
        "AWS WAF", "WAF", "웹 ACL", "SQL Injection", "XSS", "크로스 사이트",
        "Cloudflare", "DDoS", "CDN", "SSL/TLS", "TLS", "Bot Management",
        "GitHub", "Dependabot", "Code Scanning", "CodeQL", "Secret Scanning",
        "DVWA", "OWASP", "보안", "DevSecOps", "CI/CD", "CloudFront",
        "S3", "CORS", "DNS", "DNSSEC", "Rate Limiting", "Geo-blocking"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def generate_image_prompt_for_segment(segment_text: str, keywords: List[str], post_title: str = "") -> str:
    """세그먼트 텍스트를 기반으로 이미지 생성 프롬프트 생성 (Gemini 가이드라인 반영)"""
    
    # 키워드 기반 주제 파악
    main_topic = "클라우드 보안"
    color_palette = "Blue (#0066CC) for cloud/infrastructure, Green (#00AA44) for security, Orange (#FF6600) for AWS services"
    
    if any(kw in keywords for kw in ["AWS WAF", "WAF"]):
        main_topic = "AWS WAF 웹 애플리케이션 방화벽"
        color_palette = "AWS orange (#FF9900), Blue (#0066CC) for networking, Green (#00AA44) for security"
    elif any(kw in keywords for kw in ["Cloudflare", "DDoS"]):
        main_topic = "Cloudflare 보안 및 DDoS 방어"
        color_palette = "Cloudflare orange (#F38020), Blue (#0066CC) for CDN, Green (#00AA44) for security"
    elif any(kw in keywords for kw in ["GitHub", "Dependabot", "Code Scanning"]):
        main_topic = "GitHub 보안 자동화"
        color_palette = "GitHub dark (#24292e), Blue (#0066CC) for automation, Green (#00AA44) for security"
    elif any(kw in keywords for kw in ["DVWA", "SQL Injection", "XSS"]):
        main_topic = "웹 애플리케이션 보안 테스트"
        color_palette = "Red (#CC0000) for vulnerabilities, Orange (#FF6600) for testing, Green (#00AA44) for security"
    elif any(kw in keywords for kw in ["Kubernetes", "K8s", "Pod"]):
        main_topic = "Kubernetes 보안"
        color_palette = "Kubernetes blue (#326CE5), Green (#00AA44) for pods, Orange (#FF6600) for services"
    elif any(kw in keywords for kw in ["Docker", "Container"]):
        main_topic = "Docker 컨테이너 보안"
        color_palette = "Docker blue (#0db7ed), Green (#00AA44) for security, Gray (#666666) for containers"
    
    # 세그먼트 내용 요약 (최대 200자)
    segment_summary = segment_text[:200].strip()
    
    # 프롬프트 생성 (GEMINI_IMAGE_GUIDE.md 가이드라인 반영)
    prompt = f"""Create a nano banana style minimalist illustration for a video segment.

Topic: {main_topic}
Segment Content: {segment_summary}
Keywords: {', '.join(keywords[:5]) if keywords else 'tech security'}
Post Title: {post_title[:100] if post_title else 'Tech Blog'}

Style Requirements:
- Style: minimalist, clean, professional tech illustration (nano banana style)
- Colors: {color_palette}
- Layout: horizontal, optimized for video background (16:9 aspect ratio, 1920x1080px recommended)
- No text overlays (image only, no Korean labels or text)
- Focus on visual representation of the concept
- Modern and professional design
- Suitable for video background overlay
- Clean lines and simple shapes
- Professional tech blog aesthetic

Visual Elements:
- Represent the main concept: {main_topic}
- Use icons, diagrams, or abstract representations
- Maintain visual consistency with tech blog style
- Avoid cluttered or complex designs

The image should visually represent the concept of: {main_topic}
"""
    
    return prompt.strip()


def generate_image_with_gemini(prompt: str, output_path: Path, max_retries: int = 3) -> bool:
    """Gemini API를 사용하여 이미지 생성 (재시도 로직 포함)"""
    if not GEMINI_API_KEY:
        log_message("GEMINI_API_KEY가 설정되지 않았습니다.", "ERROR")
        return False
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = 2 ** (attempt - 1)  # 지수 백오프: 2초, 4초, 8초
                log_message(f"🔄 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            
            # 모델 선택
            api_url = GEMINI_IMAGE_PRO_API_URL if USE_PRO_MODEL else GEMINI_IMAGE_API_URL
            url = f"{api_url}?key={GEMINI_API_KEY}"
            
            # Gemini 이미지 생성 API 요청 형식
            payload = {
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
            
            log_message(f"🖼️ Gemini API로 이미지 생성 중: {output_path.name}")
            log_message(f"   모델: {'Gemini 3 Pro Image (Nano Banana Pro)' if USE_PRO_MODEL else 'Gemini 2.5 Flash Image (Nano Banana)'}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=120,  # 이미지 생성은 시간이 걸릴 수 있음
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Gemini API 응답에서 이미지 데이터 추출
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    
                    # 이미지 데이터가 parts에 포함되어 있을 수 있음
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            # 이미지 데이터가 base64로 인코딩되어 있을 수 있음
                            if "inlineData" in part:
                                image_data = part["inlineData"]["data"]
                                image_mime_type = part["inlineData"]["mimeType"]
                                
                                # base64 디코딩
                                try:
                                    image_bytes = base64.b64decode(image_data)
                                    
                                    # 이미지 저장 (바이너리 이미지 데이터 - 민감 정보 아님)
                                    with open(output_path, "wb") as f:
                                        # Security: Binary image data, not sensitive text
                                        # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
                                        # nosec B608 - binary image data, not sensitive text
                                        f.write(image_bytes)
                                    
                                    log_message(f"✅ 이미지 생성 완료: {output_path.name} ({len(image_bytes)} bytes)", "SUCCESS")
                                    return True
                                except Exception as e:
                                    log_message(f"❌ 이미지 디코딩 실패: {str(e)}", "ERROR")
                                    if attempt < max_retries:
                                        continue
                                    return False
                            
                            # 또는 이미지 URL이 제공될 수 있음
                            if "url" in part:
                                image_url = part["url"]
                                log_message(f"📥 이미지 URL 받음, 다운로드 중: {image_url}")
                                
                                # 이미지 다운로드 (바이너리 이미지 데이터 - 민감 정보 아님)
                                img_response = requests.get(image_url, timeout=60)
                                if img_response.status_code == 200:
                                    with open(output_path, "wb") as f:
                                        # Security: Binary image data, not sensitive text
                                        # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
                                        # nosec B608 - binary image data, not sensitive text
                                        f.write(img_response.content)
                                    log_message(f"✅ 이미지 다운로드 완료: {output_path.name}", "SUCCESS")
                                    return True
                                else:
                                    log_message(f"❌ 이미지 다운로드 실패: {img_response.status_code}", "ERROR")
                                    if attempt < max_retries:
                                        continue
                                    return False
                    
                    # 응답 형식이 다른 경우 (텍스트로 이미지 생성 프롬프트가 반환될 수 있음)
                    if "text" in candidate.get("content", {}).get("parts", [{}])[0]:
                        text_response = candidate["content"]["parts"][0]["text"]
                        log_message(f"⚠️ Gemini API가 텍스트 응답을 반환했습니다. 이미지 생성 프롬프트로 사용할 수 있습니다.", "WARNING")
                        # Security: Mask sensitive info before logging
                        safe_text_preview = mask_sensitive_info(text_response[:200])
                        log_message(f"   응답: {safe_text_preview}...")
                        
                        # 프롬프트 파일로 저장 (민감 정보 마스킹)
                        prompt_file = output_path.parent / f"{output_path.stem}_prompt.txt"
                        safe_prompt = mask_sensitive_info(prompt)
                        safe_text_response = mask_sensitive_info(text_response)
                        if _validate_masked_text(safe_prompt) and _validate_masked_text(safe_text_response):
                            safe_content = f"# Image Generation Prompt\n\n"
                            safe_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            safe_content += f"Original Prompt:\n{safe_prompt}\n\n"
                            safe_content += f"Refined Prompt:\n{safe_text_response}\n"
                            # Security: Use dedicated function for validated safe text
                            _write_safe_text_to_file(prompt_file, safe_content)
                        
                        log_message(f"💡 프롬프트 파일 저장: {prompt_file}", "INFO")
                        if attempt < max_retries:
                            continue
                        return False
                
                    log_message(f"⚠️ Gemini API 응답에 이미지 데이터가 없습니다.", "WARNING")
                    log_message(f"   응답: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                    if attempt < max_retries:
                        continue
                    return False
                
            else:
                error_text = response.text[:500] if response.text else "No error message"
                log_message(f"❌ 이미지 생성 실패: HTTP {response.status_code}", "ERROR")
                log_message(f"   오류: {error_text}", "ERROR")
                
                # 404 오류인 경우 모델이 지원되지 않을 수 있음
                if response.status_code == 404:
                    log_message("💡 Gemini 이미지 생성 모델이 지원되지 않을 수 있습니다.", "INFO")
                    log_message("💡 환경 변수 USE_GEMINI_PRO_IMAGE=false로 설정하여 Flash 모델을 시도해보세요.", "INFO")
                
                if attempt < max_retries:
                    continue
                return False
                
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                log_message(f"⏱️ 타임아웃 발생, 재시도 예정...", "WARNING")
                continue
            log_message(f"❌ 이미지 생성 타임아웃 (120초 초과, {max_retries}회 시도)", "ERROR")
            return False
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                log_message(f"🔄 네트워크 오류 발생, 재시도 예정...", "WARNING")
                continue
            log_message(f"❌ 네트워크 오류: {str(e)}", "ERROR")
            return False
        except Exception as e:
            if attempt < max_retries:
                log_message(f"🔄 오류 발생, 재시도 예정: {str(e)[:100]}", "WARNING")
                continue
            log_message(f"❌ 이미지 생성 중 오류: {str(e)}", "ERROR")
            return False
    
    return False


def generate_segment_images(segments_json_path: Path, post_title: str = "") -> Dict[str, str]:
    """세그먼트별 이미지 생성"""
    if not segments_json_path.exists():
        log_message(f"❌ 세그먼트 JSON 파일을 찾을 수 없습니다: {segments_json_path}", "ERROR")
        return {}
    
    try:
        with open(segments_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        segments = data.get("segments", [])
        if not segments:
            log_message("❌ 세그먼트가 없습니다.", "ERROR")
            return {}
        
        log_message(f"📝 {len(segments)}개 세그먼트에 대한 이미지 생성 시작")
        
        image_mapping = {}
        
        for i, segment in enumerate(segments):
            segment_text = segment.get("text", "")
            if not segment_text:
                continue
            
            # 키워드 추출
            keywords = extract_keywords_from_text(segment_text)
            
            # 이미지 파일명 생성
            segment_index = segment.get("index", i)
            safe_title = post_title.replace(" ", "_").replace("/", "_")[:50] if post_title else "segment"
            image_filename = f"{safe_title}_segment_{segment_index:02d}.png"
            image_path = IMAGES_DIR / image_filename
            
            # 이미지가 이미 존재하면 스킵
            if image_path.exists():
                log_message(f"⏭️ 세그먼트 {segment_index} 이미지 이미 존재: {image_filename}")
                image_mapping[f"segment_{segment_index}"] = image_filename
                continue
            
            # 이미지 생성 프롬프트 생성
            prompt = generate_image_prompt_for_segment(segment_text, keywords, post_title)
            
            # Gemini API로 실제 이미지 생성
            if generate_image_with_gemini(prompt, image_path):
                image_mapping[f"segment_{segment_index}"] = image_filename
                log_message(f"✅ 세그먼트 {segment_index} 이미지 생성 완료: {image_filename}", "SUCCESS")
            else:
                log_message(f"⚠️ 세그먼트 {segment_index} 이미지 생성 실패", "WARNING")
                image_mapping[f"segment_{segment_index}"] = None
            
            # Rate limit 방지를 위한 지연
            time.sleep(0.5)  # Flash 모델의 경우 RPM이 높지만 안전을 위해 지연
        
        log_message(f"✅ 이미지 매핑 완료: {len(image_mapping)}개")
        return image_mapping
        
    except Exception as e:
        log_message(f"❌ 세그먼트 이미지 생성 실패: {str(e)}", "ERROR")
        return {}


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        log_message("사용법: python generate_segment_images.py <post_basename>", "ERROR")
        log_message("예시: python generate_segment_images.py 2025-05-23-클라우드_시큐리티_과정_7기_-_6주차_Cloudflare_및_github_보안", "ERROR")
        sys.exit(1)
    
    post_basename = sys.argv[1]
    segments_json_path = OUTPUT_DIR / f"{post_basename}_script_segments.json"
    
    # 포스팅 제목 추출 (선택적)
    post_title = ""
    if len(sys.argv) >= 3:
        post_title = sys.argv[2]
    
    log_message(f"📝 세그먼트 이미지 생성 시작: {post_basename}")
    
    image_mapping = generate_segment_images(segments_json_path, post_title)
    
    if image_mapping:
        log_message(f"✅ 세그먼트 이미지 생성 완료: {len(image_mapping)}개")
    else:
        log_message("⚠️ 생성된 이미지가 없습니다.", "WARNING")


if __name__ == "__main__":
    main()
