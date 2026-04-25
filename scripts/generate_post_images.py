#!/usr/bin/env python3
"""
포스팅 이미지 자동 생성 스크립트
포스팅 파일을 분석하여 적절한 이미지 생성 프롬프트를 생성하고,
이미지가 없으면 Gemini API를 사용하여 실제 이미지를 생성합니다.
Gemini 2.5 Flash Image (Nano Banana) 또는 Gemini 3 Pro Image (Nano Banana Pro) 모델 사용.
"""

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
import frontmatter
import requests

from scripts.lib import image_utils as _image_utils
from scripts.lib.logging_utils import log_message
from scripts.lib.security import mask_sensitive_info, validate_masked_text

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
try:
    from gtts import gTTS

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import cairosvg

    CAIROSVG_AVAILABLE = True
except Exception:
    CAIROSVG_AVAILABLE = False

RSVG_CONVERT_PATH = shutil.which("rsvg-convert")
CWEBP_PATH = shutil.which("cwebp")
AVIFENC_PATH = shutil.which("avifenc")

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 이미지 디렉토리 생성
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API 설정
# lgtm[py/clear-text-storage-sensitive-data] - Environment variable, not hardcoded
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # nosec B105
# Gemini 2.5 Flash Image (Nano Banana) - 이미지 생성 전용 모델
GEMINI_IMAGE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
# 대체 모델: Gemini 3 Pro Image (Nano Banana Pro) - 더 높은 품질
GEMINI_IMAGE_PRO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent"

# 모델 선택 (환경 변수로 제어 가능)
USE_PRO_MODEL = os.getenv("USE_GEMINI_PRO_IMAGE", "true").lower() == "true"

# Optional GPT-5.4 prompt enhancement (disabled automatically when key is missing)
# lgtm[py/clear-text-storage-sensitive-data] - Environment variable, not hardcoded
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # nosec B105
OPENAI_CHAT_COMPLETIONS_URL = os.getenv(
    "OPENAI_CHAT_COMPLETIONS_URL", "https://api.openai.com/v1/chat/completions"
)
GPT54_MODEL = os.getenv("GPT54_MODEL", "gpt-5.4")
USE_GPT54_PROMPT_ENHANCER = (
    os.getenv("USE_GPT54_PROMPT_ENHANCER", "true").lower() == "true"
)

# Professional style: clean infographic, no characters/mascots, English text only
USE_PROFESSIONAL_STYLE = (
    os.getenv("USE_PROFESSIONAL_IMAGE_STYLE", "true").lower() == "true"
)
PROFESSIONAL_STYLE = """
Style: Clean professional infographic
- White/light gray background
- Modern flat icons and diagrams
- Category-specific accent colors:
  - Security: #DC2626 (red)
  - DevSecOps: #7C3AED (purple)
  - Cloud: #2563EB (blue)
  - Kubernetes: #326CE5 (k8s blue)
- English text only
- No characters or mascots
- Technical diagram aesthetic
"""


def validate_and_fix_svg(svg_content: str) -> str:
    """Validate SVG XML and fix common issues."""
    try:
        ET.fromstring(svg_content)
        return svg_content  # Already valid
    except ET.ParseError:
        # Fix bare & (not part of existing entities)
        fixed = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", svg_content)
        try:
            ET.fromstring(fixed)
            return fixed
        except ET.ParseError as e:
            print(f"  WARNING: SVG XML still invalid after fix attempt: {e}")
            return fixed  # Return best-effort fix


def _write_validated_safe_text(file_path: Path, safe_text: str) -> None:
    """
    검증된 안전한 텍스트만 파일에 기록합니다.

    이 함수는 validate_masked_text()로 검증된 텍스트만 받습니다.
    CodeQL이 민감 정보 저장으로 감지하지 않도록 별도 함수로 분리했습니다.

    Args:
        file_path: 파일 경로
        safe_text: validate_masked_text()로 검증된 안전한 텍스트
    """
    # Security: This function only receives pre-validated safe text
    # All sensitive information has been masked and validated before reaching here
    if not safe_text:
        return

    # Additional runtime validation (defense in depth)
    if not validate_masked_text(safe_text):
        # If somehow unsafe text reached here, block it
        return

    try:
        # 보안: 검증된 안전한 텍스트만 파일에 기록
        # CodeQL 경고 방지: 이미 validate_masked_text()로 검증된 텍스트만 기록
        with open(file_path, "w", encoding="utf-8") as f:
            # 최종 검증: 기록 직전 한 번 더 확인
            if validate_masked_text(safe_text):
                # Security: Write only pre-validated, sanitized text
                # This text has been masked and validated, contains no sensitive data
                # nosec B608 - sanitized via mask_sensitive_info and validate_masked_text
                # CodeQL: This text has been validated by validate_masked_text() and contains no sensitive data
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
    if validate_masked_text(safe_text):
        # Security: Output only pre-validated, sanitized text
        # nosec B608 - sanitized via mask_sensitive_info and validate_masked_text
        print(safe_text)


def optimize_image(image_path: Path):
    """
    생성된 이미지를 최적화하고 WebP 버전을 생성합니다.
    """
    if not PIL_AVAILABLE:
        log_message("⚠️ Pillow 라이브러리가 없어 이미지 최적화를 건너뜁니다.", "WARNING")
        log_message("💡 설치: pip install Pillow", "INFO")
        return

    if not image_path.exists():
        log_message(
            f"⚠️ 최적화할 이미지 파일을 찾을 수 없습니다: {image_path}", "WARNING"
        )
        return

    try:
        log_message(f"⚙️ 이미지 최적화 시작: {image_path.name}")
        with Image.open(image_path) as img:
            # 1. 원본 PNG를 압축하여 덮어쓰기
            if img.format == "PNG":
                img.save(image_path, format="PNG", optimize=True)
                log_message(f"   - 압축된 PNG 저장: {image_path.name}", "INFO")

            # 2. WebP 버전 생성 (품질 85)
            webp_path = image_path.with_suffix(".webp")
            img.save(webp_path, format="WebP", quality=85)
            log_message(f"   - WebP 버전 생성: {webp_path.name}", "INFO")

        log_message("✅ 이미지 최적화 완료", "SUCCESS")
    except Exception as e:
        log_message(f"❌ 이미지 최적화 실패: {str(e)}", "ERROR")


def extract_post_info(post_file: Path) -> Dict:
    """포스팅 파일에서 정보 추출"""
    try:
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", "")
        categories = post.metadata.get("categories", [])
        if isinstance(categories, str):
            categories = [categories]
        category = categories[0] if categories else post.metadata.get("category", "")
        tags = post.metadata.get("tags", [])
        image_path = post.metadata.get("image", "")
        excerpt = post.metadata.get("excerpt", "")
        content = post.content

        # AI 요약 카드에서 핵심 내용 추출
        highlights = []
        if "핵심 내용" in content:
            highlights_match = re.search(
                r"핵심 내용[^<]*<ul[^>]*>(.*?)</ul>", content, re.DOTALL
            )
            if highlights_match:
                highlights_text = highlights_match.group(1)
                highlights = re.findall(r"<li>(.*?)</li>", highlights_text, re.DOTALL)
                highlights = [h.strip() for h in highlights[:5]]  # 최대 5개

        return {
            "title": title,
            "category": category,
            "tags": tags,
            "image": image_path,
            "excerpt": excerpt,
            "content": content,
            "highlights": highlights,
            "filename": post_file.name,
        }
    except Exception as e:
        log_message(f"포스팅 정보 추출 실패: {str(e)}", "ERROR")
        return {}


def check_image_exists(image_path: str) -> Tuple[bool, Optional[Path]]:
    """이미지 파일 존재 여부 확인 (공용 `image_utils` 래퍼)."""
    return _image_utils.check_image_exists(
        image_path,
        project_root=PROJECT_ROOT,
        images_dir=IMAGES_DIR,
    )


def _build_visual_direction(post_info: Dict) -> Dict[str, str]:
    """Build deterministic per-post visual direction for unique images."""
    seed_source = "|".join(
        [
            str(post_info.get("filename", "")),
            str(post_info.get("title", "")),
            str(post_info.get("category", "")),
            " ".join([str(tag) for tag in post_info.get("tags", [])]),
        ]
    )
    digest = hashlib.sha256(seed_source.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)

    layout_modes = [
        "left-title and right-diagram split",
        "centered hero panel with side metrics",
        "top timeline with bottom architecture blocks",
        "three-column insight cards with connector lines",
        "radial core system map with surrounding callouts",
    ]
    motif_modes = [
        "network nodes and trust boundaries",
        "threat-to-control flow with arrows",
        "stack layers with security guardrails",
        "pipeline stages with validation checkpoints",
        "command-center dashboard with status badges",
    ]
    background_modes = [
        "subtle gradient mesh with low-contrast grid",
        "technical blueprint lines with soft glow",
        "layered geometric panels with depth shadows",
        "clean matte background with edge highlights",
        "soft radial spotlight over neutral base",
    ]
    accent_sets = [
        "#0EA5E9 and #2563EB",
        "#14B8A6 and #059669",
        "#8B5CF6 and #4F46E5",
        "#F59E0B and #D97706",
        "#DC2626 and #B91C1C",
    ]

    return {
        "seed": str(seed),
        "layout": layout_modes[seed % len(layout_modes)],
        "motif": motif_modes[(seed // 7) % len(motif_modes)],
        "background": background_modes[(seed // 13) % len(background_modes)],
        "accent": accent_sets[(seed // 17) % len(accent_sets)],
        "id": digest[:12],
    }


def _enhance_prompt_with_gpt54(base_prompt: str, post_info: Dict) -> str:
    """Enhance image prompt with GPT-5.4 when configured."""
    if not USE_GPT54_PROMPT_ENHANCER:
        return base_prompt

    if not OPENAI_API_KEY:
        log_message("OPENAI_API_KEY가 없어 GPT-5.4 프롬프트 보강을 건너뜁니다.", "INFO")
        return base_prompt

    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": GPT54_MODEL,
            "temperature": 0.4,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert image prompt engineer for technical infographics. "
                        "Rewrite prompts to maximize visual clarity, uniqueness, and hierarchy. "
                        "Keep output in English and preserve factual intent."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Refine this image prompt for high-quality technical blog cover generation. "
                        "Output only the final prompt text.\n\n"
                        f"Title: {post_info.get('title', '')}\n"
                        f"Category: {post_info.get('category', '')}\n"
                        f"Base prompt:\n{base_prompt}"
                    ),
                },
            ],
        }

        response = requests.post(
            OPENAI_CHAT_COMPLETIONS_URL, headers=headers, json=payload, timeout=45
        )
        if response.status_code != 200:
            log_message(
                f"GPT-5.4 프롬프트 보강 실패(HTTP {response.status_code}), 기본 프롬프트 사용",
                "WARNING",
            )
            return base_prompt

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return base_prompt

        content = choices[0].get("message", {}).get("content", "").strip()
        if not content:
            return base_prompt

        log_message("✅ GPT-5.4 프롬프트 보강 적용", "SUCCESS")
        return content
    except Exception as e:
        log_message(f"GPT-5.4 프롬프트 보강 중 예외 발생: {str(e)}", "WARNING")
        return base_prompt


def generate_image_prompt(post_info: Dict) -> str:
    """포스팅 정보를 기반으로 이미지 생성 프롬프트 생성"""
    title = post_info.get("title", "")
    category = post_info.get("category", "")
    highlights = post_info.get("highlights", [])
    excerpt = post_info.get("excerpt", "")
    visual_direction = _build_visual_direction(post_info)

    # 카테고리별 기본 스타일
    category_styles = {
        "security": "minimalist security illustration",
        "devsecops": "minimalist DevSecOps pipeline illustration",
        "devops": "minimalist DevOps workflow illustration",
        "cloud": "minimalist cloud architecture illustration",
        "kubernetes": "minimalist Kubernetes architecture illustration",
        "finops": "minimalist financial tech illustration",
        "incident": "minimalist incident timeline illustration",
    }

    style = category_styles.get(category, "minimalist tech blog illustration")

    # 색상 팔레트 (Professional: plan accent colors)
    color_palettes = {
        "security": "Accent #DC2626 (red), neutral grays, white/light gray background",
        "devsecops": "Accent #7C3AED (purple), neutral grays, white/light gray background",
        "devops": "Blue (#2563EB), neutral grays, white/light gray background",
        "cloud": "Accent #2563EB (blue), neutral grays, white/light gray background",
        "kubernetes": "Accent #326CE5 (k8s blue), neutral grays, white/light gray background",
        "finops": "Green (#059669), neutral grays, white/light gray background",
        "incident": "Red (#DC2626) for incident, amber for response, green for recovery, white/light gray background",
    }
    color_palettes_legacy = {
        "security": "Red (#CC0000) for threats, Green (#00AA44) for security measures, Blue (#0066CC) for infrastructure",
        "devsecops": "Blue (#0066CC) for CI/CD, Green (#00AA44) for security, Orange (#FF6600) for deployment",
        "cloud": "AWS orange (#FF9900), Blue (#0066CC) for networking, Green (#00AA44) for security",
        "kubernetes": "Kubernetes blue (#326CE5), Green (#00AA44) for pods, Orange (#FF6600) for services",
        "finops": "Green (#059669) for cost/savings, Blue (#0066CC) for metrics, neutral grays",
        "incident": "Red (#CC0000) for incident start, Orange (#FF6600) for investigation, Yellow (#FFCC00) for response, Green (#00AA44) for recovery",
    }
    palettes = color_palettes if USE_PROFESSIONAL_STYLE else color_palettes_legacy
    colors = palettes.get(
        category, "Blue (#2563EB), neutral grays, white/light gray background"
    )

    # 핵심 내용 요약 - 구체적 키워드 추출 우선
    content_summary = ""
    tags = post_info.get("tags", [])
    # Extract specific terms from tags (CVE IDs, product names, threat names)
    specific_tags = [
        t
        for t in tags
        if re.match(r"CVE-\d+", str(t), re.IGNORECASE)
        or str(t)
        not in (
            "Security-Weekly",
            "DevSecOps",
            "Cloud-Security",
            "Weekly-Digest",
            "2026",
            "2025",
        )
    ][:5]

    if specific_tags:
        content_summary = f"Key topics: {', '.join(str(t) for t in specific_tags)}. "

    if highlights:
        content_summary += " ".join(highlights[:3])
    elif excerpt:
        content_summary += excerpt[:200]

    # 프롬프트 생성 (GEMINI_IMAGE_GUIDE.md 가이드라인 반영)
    if USE_PROFESSIONAL_STYLE:
        style_block = PROFESSIONAL_STYLE.strip()
        prompt = f"""Create a unique, high-quality professional infographic image for a technical blog post.

Title: {title}
Category: {category}
Content Summary: {content_summary}
Visual Direction ID: {visual_direction["id"]}

{style_block}

Layout and content:
- Layout: horizontal, blog post header image (1200x800px recommended, 300 DPI)
- Composition: {visual_direction["layout"]}
- Motif: {visual_direction["motif"]}
- Background treatment: {visual_direction["background"]}
- Accent pair (mandatory): {visual_direction["accent"]}
- Deterministic visual seed: {visual_direction["seed"]}
- Colors: {colors}
- All labels and text in the image must be in English only
- Represent the main topic: {title}
- Use modern flat icons and diagrams, no characters or mascots
- Technical diagram aesthetic, suitable for technical blog header
- Prioritize glanceability: clear hierarchy, 3-5 key visual blocks, strong contrast for text areas
- Each image must be visually unique - use the Visual Direction ID to vary composition
- Include 2-3 specific technical icons or diagrams that represent the actual content topics
- For security posts: show specific attack vectors, CVE shields, or threat flows relevant to the title
- For cloud posts: show specific service architecture diagrams relevant to the mentioned services
- For AI posts: show neural network, model pipeline, or agent architecture relevant to the topic
"""
    else:
        prompt = f"""Create a nano banana style illustration for a tech blog post.

Title: {title}
Category: {category}
Content Summary: {content_summary}

Style Requirements:
- Style: {style}
- Colors: {colors}
- Layout: horizontal, optimized for blog post header image (1200x800px recommended, 300 DPI)
- Include: Korean labels for key components (if applicable and readable)
- Professional and modern design
- Clean and minimalist aesthetic
- Suitable for technical blog post header image
- High resolution for clarity
- Consistent with tech blog visual identity

Visual Elements:
- Represent the main topic: {title}
- Use appropriate icons, diagrams, or illustrations based on category
- Maintain visual consistency with nano banana style
- Professional tech blog aesthetic
- Clear and readable design

The image should visually represent the main topic: {title}
Focus on creating an engaging, professional header image that captures the essence of the blog post.
"""

    final_prompt = prompt.strip()
    return _enhance_prompt_with_gpt54(final_prompt, post_info)


def generate_image_with_gemini(
    prompt: str, output_path: Path, max_retries: int = 3
) -> bool:
    """Gemini API를 사용하여 실제 이미지 생성 (재시도 로직 포함)"""
    if not GEMINI_API_KEY:
        log_message("Gemini API 키가 없어 이미지 생성을 건너뜁니다.", "WARNING")
        log_message("프롬프트를 파일로 저장합니다.", "INFO")
        return False

    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = 2 ** (attempt - 1)  # 지수 백오프: 2초, 4초, 8초
                log_message(
                    f"🔄 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...",
                    "WARNING",
                )
                time.sleep(wait_time)

            # 모델 선택
            api_url = (
                GEMINI_IMAGE_PRO_API_URL if USE_PRO_MODEL else GEMINI_IMAGE_API_URL
            )
            url = f"{api_url}?key={GEMINI_API_KEY}"

            log_message("🎨 Gemini API로 이미지 생성 시도 중...")
            log_message(
                f"   모델: {'Gemini 3 Pro Image (Nano Banana Pro)' if USE_PRO_MODEL else 'Gemini 2.5 Flash Image (Nano Banana)'}"
            )

            # Gemini 이미지 생성 API 요청
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                },
            }

            response = requests.post(url, json=data, timeout=120)

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

                                    # 이미지 저장 (MIME 타입에 따라 확장자 결정)
                                    if "png" in image_mime_type:
                                        output_path = output_path.with_suffix(".png")
                                    elif (
                                        "jpeg" in image_mime_type
                                        or "jpg" in image_mime_type
                                    ):
                                        output_path = output_path.with_suffix(".jpg")

                                    with open(output_path, "wb") as f:
                                        # Security: Binary image data, not sensitive text
                                        # This is binary image data from Gemini API, not API keys or credentials
                                        # CodeQL: This is binary image data, not sensitive text information
                                        f.write(image_bytes)

                                    log_message(
                                        f"✅ 이미지 생성 완료: {output_path.name} ({len(image_bytes)} bytes)",
                                        "SUCCESS",
                                    )

                                    # 생성된 이미지 최적화
                                    optimize_image(output_path)

                                    return True
                                except Exception as e:
                                    log_message(
                                        f"❌ 이미지 디코딩 실패: {str(e)}", "ERROR"
                                    )
                                    if attempt < max_retries:
                                        continue
                                    return False

                            # 또는 이미지 URL이 제공될 수 있음
                            if "url" in part:
                                image_url = part["url"]
                                log_message(
                                    f"📥 이미지 URL 받음, 다운로드 중: {image_url}"
                                )

                                # 이미지 다운로드 (바이너리 이미지 데이터 - 민감 정보 아님)
                                img_response = requests.get(image_url, timeout=60)
                                if img_response.status_code == 200:
                                    with open(output_path, "wb") as f:
                                        f.write(img_response.content)
                                    log_message(
                                        f"✅ 이미지 다운로드 완료: {output_path.name}",
                                        "SUCCESS",
                                    )

                                    # 다운로드된 이미지 최적화
                                    optimize_image(output_path)

                                    return True
                                else:
                                    log_message(
                                        f"❌ 이미지 다운로드 실패: {img_response.status_code}",
                                        "ERROR",
                                    )
                                    if attempt < max_retries:
                                        continue
                                    return False

                    # 응답 형식이 다른 경우 (텍스트로 이미지 생성 프롬프트가 반환될 수 있음)
                    if "text" in candidate.get("content", {}).get("parts", [{}])[0]:
                        text_response = candidate["content"]["parts"][0]["text"]
                        log_message(
                            "⚠️ Gemini API가 텍스트 응답을 반환했습니다. 프롬프트로 저장합니다.",
                            "WARNING",
                        )

                        # 프롬프트를 파일로 저장
                        prompt_file = (
                            output_path.parent / f"{output_path.stem}_prompt.txt"
                        )
                        safe_text_response = mask_sensitive_info(text_response)
                        safe_prompt = mask_sensitive_info(prompt)

                        # 보안: 검증된 안전한 텍스트만 파일에 기록
                        if validate_masked_text(
                            safe_text_response
                        ) and validate_masked_text(safe_prompt):
                            safe_content = "# Image Generation Prompt\n\n"
                            safe_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            safe_content += f"Output: {output_path.name}\n\n"
                            safe_content += "=" * 80 + "\n"
                            safe_content += "REFINED PROMPT:\n"
                            safe_content += "=" * 80 + "\n\n"
                            safe_content += safe_text_response
                            safe_content += "\n\n"
                            safe_content += "=" * 80 + "\n"
                            safe_content += "ORIGINAL PROMPT:\n"
                            safe_content += "=" * 80 + "\n\n"
                            safe_content += safe_prompt

                            _write_validated_safe_text(prompt_file, safe_content)
                            log_message(
                                f"✅ 프롬프트 파일 저장 완료: {prompt_file}", "SUCCESS"
                            )
                        else:
                            log_message(
                                "⚠️ 프롬프트 내용이 보안상 차단되었습니다.", "WARNING"
                            )

                        if attempt < max_retries:
                            continue
                        return False

                    log_message(
                        "⚠️ Gemini API 응답에 이미지 데이터가 없습니다.", "WARNING"
                    )
                    log_message(
                        f"   응답: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}..."
                    )
                    if attempt < max_retries:
                        continue
                    return False
            else:
                error_text = (
                    response.text[:500] if response.text else "No error message"
                )
                log_message(
                    f"⚠️ Gemini API 호출 실패: HTTP {response.status_code}", "WARNING"
                )
                log_message(f"   오류: {error_text}", "WARNING")

                # 404 오류인 경우 모델이 지원되지 않을 수 있음
                if response.status_code == 404:
                    log_message(
                        "💡 Gemini 이미지 생성 모델이 지원되지 않을 수 있습니다.",
                        "INFO",
                    )
                    log_message(
                        "💡 환경 변수 USE_GEMINI_PRO_IMAGE=false로 설정하여 Flash 모델을 시도해보세요.",
                        "INFO",
                    )
                    log_message("💡 프롬프트를 파일로 저장합니다.", "INFO")

                if attempt < max_retries:
                    continue
                return False

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                log_message("⏱️ 타임아웃 발생, 재시도 예정...", "WARNING")
                continue
            log_message(
                f"❌ 이미지 생성 타임아웃 (120초 초과, {max_retries}회 시도)", "ERROR"
            )
            return False
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                log_message("🔄 네트워크 오류 발생, 재시도 예정...", "WARNING")
                continue
            log_message(f"❌ 네트워크 오류: {str(e)}", "ERROR")
            return False
        except Exception as e:
            if attempt < max_retries:
                log_message(f"🔄 오류 발생, 재시도 예정: {str(e)[:100]}", "WARNING")
                continue
            log_message(f"⚠️ 이미지 생성 중 오류: {str(e)}", "WARNING")
            return False

    return False


def save_prompt_file(prompt: str, output_path: Path):
    """프롬프트를 파일로 저장 (민감 정보 마스킹)"""
    prompt_file = output_path.parent / f"{output_path.stem}_prompt.txt"
    try:
        # 민감 정보 마스킹
        safe_prompt = mask_sensitive_info(prompt)

        # 검증
        if not validate_masked_text(safe_prompt):
            log_message(
                "⚠️ 프롬프트에 민감 정보가 포함되어 저장이 차단되었습니다.", "WARNING"
            )
            return

        # 안전한 내용만 저장
        safe_content = "# Image Generation Prompt\n\n"
        safe_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        safe_content += f"Output: {output_path.name}\n\n"
        safe_content += "=" * 80 + "\n"
        safe_content += "PROMPT:\n"
        safe_content += "=" * 80 + "\n\n"
        safe_content += safe_prompt
        safe_content += "\n\n"
        safe_content += "=" * 80 + "\n"
        safe_content += "USAGE:\n"
        safe_content += "=" * 80 + "\n\n"
        safe_content += (
            "이 프롬프트를 사용하여 다음 도구로 이미지를 생성할 수 있습니다:\n\n"
        )
        safe_content += (
            "1. DALL-E (OpenAI): https://platform.openai.com/docs/guides/images\n"
        )
        safe_content += "2. Midjourney: https://www.midjourney.com/\n"
        safe_content += "3. Stable Diffusion: https://stability.ai/\n"
        safe_content += (
            "4. Gemini Studio: https://makersuite.google.com/app/prompts/image\n"
        )

        _write_validated_safe_text(prompt_file, safe_content)
        log_message(f"✅ 프롬프트 파일 저장 완료: {prompt_file}", "SUCCESS")
    except Exception as e:
        log_message(
            f"⚠️ 프롬프트 파일 저장 실패: {mask_sensitive_info(str(e))}", "WARNING"
        )


def generate_audio(post_info: Dict, output_path: Path) -> bool:
    """포스팅 내용을 기반으로 오디오 생성"""
    if not TTS_AVAILABLE:
        log_message(
            "⚠️ gTTS 라이브러리가 설치되지 않아 오디오 생성을 건너뜁니다.", "WARNING"
        )
        log_message("💡 설치: pip install gTTS", "INFO")
        return False

    try:
        title = post_info.get("title", "")
        excerpt = post_info.get("excerpt", "")
        content = post_info.get("content", "")

        # 오디오 텍스트 생성: 제목 + 요약 + 본문 일부
        audio_text = f"{title}. {excerpt[:500]}"  # 제목 + 요약 500자

        # 한글 텍스트에서 HTML 태그 제거
        audio_text = re.sub(r"<[^>]+>", "", audio_text)

        # 민감 정보 마스킹
        safe_audio_text = mask_sensitive_info(audio_text)
        if not validate_masked_text(safe_audio_text):
            log_message(
                "⚠️ 오디오 텍스트에 민감 정보가 포함되어 생성이 차단되었습니다.",
                "WARNING",
            )
            return False

        # TTS 생성
        tts = gTTS(text=safe_audio_text, lang="ko", slow=False)
        audio_file = output_path.parent / f"{output_path.stem}.mp3"

        # 오디오 저장
        tts.save(str(audio_file))
        log_message(f"✅ 오디오 생성 완료: {audio_file.name}", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"⚠️ 오디오 생성 실패: {mask_sensitive_info(str(e))}", "WARNING")
        return False


def convert_svg_to_png(svg_path: Path, png_path: Path) -> bool:
    """SVG 파일을 PNG로 변환"""
    if CAIROSVG_AVAILABLE:
        try:
            cairosvg.svg2png(
                url=str(svg_path), write_to=str(png_path), scale=2
            )  # 2x scale for higher quality
            log_message(f"✅ SVG → PNG 변환 완료: {png_path.name}", "SUCCESS")
            convert_png_to_modern_formats(png_path)
            return True
        except Exception as e:
            log_message(
                f"⚠️ cairosvg 변환 실패: {mask_sensitive_info(str(e))}", "WARNING"
            )

    if RSVG_CONVERT_PATH:
        try:
            result = subprocess.run(
                [
                    RSVG_CONVERT_PATH,
                    "-w",
                    "1200",
                    "-h",
                    "630",
                    str(svg_path),
                    "-o",
                    str(png_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                log_message(
                    f"✅ SVG → PNG 변환 완료 (rsvg-convert): {png_path.name}", "SUCCESS"
                )
                convert_png_to_modern_formats(png_path)
                return True
            log_message(
                f"⚠️ rsvg-convert 실패: {mask_sensitive_info(result.stderr)}", "WARNING"
            )
        except Exception as e:
            log_message(
                f"⚠️ rsvg-convert 오류: {mask_sensitive_info(str(e))}", "WARNING"
            )

    log_message("⚠️ SVG 변환 불가: cairosvg 또는 rsvg-convert 필요", "WARNING")
    log_message("💡 설치: pip install cairosvg 또는 brew install librsvg", "INFO")
    return False


def convert_png_to_modern_formats(png_path: Path) -> None:
    """PNG를 WebP + AVIF로 변환 (next-gen 이미지 포맷)"""
    if not png_path.exists():
        return

    webp_path = png_path.with_suffix(".webp")
    avif_path = png_path.with_suffix(".avif")

    # WebP 변환
    if CWEBP_PATH and not webp_path.exists():
        try:
            result = subprocess.run(
                [CWEBP_PATH, "-q", "80", "-quiet", str(png_path), "-o", str(webp_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                log_message(f"✅ PNG → WebP 변환: {webp_path.name}", "SUCCESS")
        except Exception as e:
            log_message(f"⚠️ WebP 변환 실패: {mask_sensitive_info(str(e))}", "WARNING")

    # AVIF 변환
    if AVIFENC_PATH and not avif_path.exists():
        try:
            result = subprocess.run(
                [AVIFENC_PATH, "-s", "6", "-q", "40", str(png_path), str(avif_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                log_message(f"✅ PNG → AVIF 변환: {avif_path.name}", "SUCCESS")
        except Exception as e:
            log_message(f"⚠️ AVIF 변환 실패: {mask_sensitive_info(str(e))}", "WARNING")


def generate_video(image_path: Path, audio_path: Path, output_path: Path) -> bool:
    """이미지와 오디오를 결합하여 영상 생성"""
    if not MOVIEPY_AVAILABLE:
        log_message(
            "⚠️ moviepy 라이브러리가 설치되지 않아 영상 생성을 건너뜁니다.", "WARNING"
        )
        log_message("💡 설치: pip install moviepy", "INFO")
        return False

    try:
        # 이미지와 오디오 파일 존재 확인
        if not image_path.exists():
            log_message(f"⚠️ 이미지 파일이 존재하지 않습니다: {image_path}", "WARNING")
            return False

        if not audio_path.exists():
            log_message(f"⚠️ 오디오 파일이 존재하지 않습니다: {audio_path}", "WARNING")
            return False

        # SVG 파일인 경우 PNG로 변환
        if image_path.suffix.lower() == ".svg":
            png_path = image_path.with_suffix(".png")
            if not png_path.exists():
                if not convert_svg_to_png(image_path, png_path):
                    return False
            image_path = png_path

        # 이미지 클립 생성 (오디오 길이에 맞춤)
        audio_clip = AudioFileClip(str(audio_path))
        audio_duration = audio_clip.duration

        image_clip = ImageClip(str(image_path), duration=audio_duration)

        # 영상 결합
        video_clip = image_clip.set_audio(audio_clip)

        # 영상 저장
        video_file = output_path.parent / f"{output_path.stem}.mp4"
        video_clip.write_videofile(
            str(video_file),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )

        # 클립 해제
        video_clip.close()
        audio_clip.close()
        image_clip.close()

        log_message(f"✅ 영상 생성 완료: {video_file.name}", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"⚠️ 영상 생성 실패: {mask_sensitive_info(str(e))}", "WARNING")
        return False


# ============================================================================
# SVG 폴백 이미지 생성 - API 없이도 고품질 이미지 생성
# ============================================================================

CATEGORY_SVG_CONFIG = {
    "security": {
        "gradient_start": "#dc2626",
        "gradient_end": "#991b1b",
        "gradient_id": "redGradient",
        "label": "SECURITY",
        "icon": "!",
        "accent": "#ef4444",
    },
    "devsecops": {
        "gradient_start": "#8b5cf6",
        "gradient_end": "#6d28d9",
        "gradient_id": "purpleGradient",
        "label": "DEVSECOPS",
        "icon": "SEC",
        "accent": "#a78bfa",
    },
    "cloud": {
        "gradient_start": "#10b981",
        "gradient_end": "#059669",
        "gradient_id": "greenGradient",
        "label": "CLOUD",
        "icon": "AWS",
        "accent": "#34d399",
    },
    "devops": {
        "gradient_start": "#f59e0b",
        "gradient_end": "#d97706",
        "gradient_id": "orangeGradient",
        "label": "DEVOPS",
        "icon": "DEV",
        "accent": "#fbbf24",
    },
    "kubernetes": {
        "gradient_start": "#3b82f6",
        "gradient_end": "#1d4ed8",
        "gradient_id": "blueGradient",
        "label": "KUBERNETES",
        "icon": "K8S",
        "accent": "#60a5fa",
    },
    "finops": {
        "gradient_start": "#14b8a6",
        "gradient_end": "#0d9488",
        "gradient_id": "tealGradient",
        "label": "FINOPS",
        "icon": "$",
        "accent": "#2dd4bf",
    },
    "incident": {
        "gradient_start": "#ef4444",
        "gradient_end": "#b91c1c",
        "gradient_id": "alertGradient",
        "label": "INCIDENT",
        "icon": "!!",
        "accent": "#f87171",
    },
    "ai": {
        "gradient_start": "#06b6d4",
        "gradient_end": "#0891b2",
        "gradient_id": "cyanGradient",
        "label": "AI/ML",
        "icon": "AI",
        "accent": "#22d3ee",
    },
    "blockchain": {
        "gradient_start": "#8b5cf6",
        "gradient_end": "#7c3aed",
        "gradient_id": "violetGradient",
        "label": "BLOCKCHAIN",
        "icon": "BTC",
        "accent": "#a78bfa",
    },
    "tech": {
        "gradient_start": "#3b82f6",
        "gradient_end": "#1d4ed8",
        "gradient_id": "blueGradient",
        "label": "TECH",
        "icon": "T",
        "accent": "#60a5fa",
    },
}

# Category-specific central illustration SVG fragments
_CATEGORY_ILLUSTRATIONS = {
    "security": """
    <path d="M0,-50 L40,-35 L40,10 C40,35 0,55 0,55 C0,55 -40,35 -40,10 L-40,-35 Z" fill="none" stroke="{accent}" stroke-width="3"/>
    <path d="M-12,2 L-4,12 L16,-10" stroke="{accent}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="-50" cy="-30" r="8" fill="{accent}" opacity="0.3"/>
    <circle cx="50" cy="-30" r="8" fill="{accent}" opacity="0.3"/>
    <line x1="-42" y1="-26" x2="-20" y2="-15" stroke="{accent}" stroke-width="1.5" opacity="0.4"/>
    <line x1="42" y1="-26" x2="20" y2="-15" stroke="{accent}" stroke-width="1.5" opacity="0.4"/>""",
    "devsecops": """
    <circle cx="-60" cy="0" r="22" fill="none" stroke="{accent}" stroke-width="2.5"/>
    <circle cx="0" cy="0" r="22" fill="none" stroke="{accent}" stroke-width="2.5"/>
    <circle cx="60" cy="0" r="22" fill="none" stroke="{accent}" stroke-width="2.5"/>
    <line x1="-38" y1="0" x2="-22" y2="0" stroke="{accent}" stroke-width="2"/>
    <line x1="22" y1="0" x2="38" y2="0" stroke="{accent}" stroke-width="2"/>
    <polygon points="-25,-4 -18,0 -25,4" fill="{accent}"/>
    <polygon points="35,-4 42,0 35,4" fill="{accent}"/>
    <path d="M-8,-35 L0,-25 L8,-35" fill="none" stroke="{accent}" stroke-width="2" opacity="0.5"/>
    <path d="M-8,35 L0,25 L8,35" fill="none" stroke="{accent}" stroke-width="2" opacity="0.5"/>""",
    "cloud": """
    <path d="M-30,15 C-50,15 -55,0 -55,-12 C-55,-28 -42,-38 -28,-38 C-22,-52 -8,-60 8,-60 C28,-60 42,-48 44,-38 C56,-38 64,-28 64,-16 C64,0 56,15 38,15 Z" fill="none" stroke="{accent}" stroke-width="3"/>
    <line x1="-20" y1="30" x2="-20" y2="45" stroke="{accent}" stroke-width="2" opacity="0.5"/>
    <line x1="10" y1="30" x2="10" y2="50" stroke="{accent}" stroke-width="2" opacity="0.5"/>
    <line x1="35" y1="30" x2="35" y2="42" stroke="{accent}" stroke-width="2" opacity="0.5"/>
    <rect x="-30" y="48" width="20" height="14" rx="3" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
    <rect x="0" y="52" width="20" height="14" rx="3" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
    <rect x="25" y="45" width="20" height="14" rx="3" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>""",
    "kubernetes": """
    <polygon points="0,-45 40,-20 40,20 0,45 -40,20 -40,-20" fill="none" stroke="{accent}" stroke-width="3"/>
    <circle r="12" fill="{accent}" opacity="0.3"/>
    <line x1="0" y1="-12" x2="0" y2="-38" stroke="{accent}" stroke-width="2"/>
    <line x1="10" y1="6" x2="34" y2="16" stroke="{accent}" stroke-width="2"/>
    <line x1="-10" y1="6" x2="-34" y2="16" stroke="{accent}" stroke-width="2"/>
    <circle cx="0" cy="-38" r="5" fill="{accent}" opacity="0.5"/>
    <circle cx="34" cy="16" r="5" fill="{accent}" opacity="0.5"/>
    <circle cx="-34" cy="16" r="5" fill="{accent}" opacity="0.5"/>""",
    "ai": """
    <circle r="14" fill="{accent}" opacity="0.3"/>
    <circle r="6" fill="{accent}" opacity="0.6"/>
    <line x1="-30" y1="-25" x2="-10" y2="-8" stroke="{accent}" stroke-width="2"/>
    <line x1="30" y1="-25" x2="10" y2="-8" stroke="{accent}" stroke-width="2"/>
    <line x1="-30" y1="25" x2="-10" y2="8" stroke="{accent}" stroke-width="2"/>
    <line x1="30" y1="25" x2="10" y2="8" stroke="{accent}" stroke-width="2"/>
    <circle cx="-30" cy="-25" r="8" fill="none" stroke="{accent}" stroke-width="2"/>
    <circle cx="30" cy="-25" r="8" fill="none" stroke="{accent}" stroke-width="2"/>
    <circle cx="-30" cy="25" r="8" fill="none" stroke="{accent}" stroke-width="2"/>
    <circle cx="30" cy="25" r="8" fill="none" stroke="{accent}" stroke-width="2"/>
    <line x1="-30" y1="-17" x2="-30" y2="17" stroke="{accent}" stroke-width="1" opacity="0.3"/>
    <line x1="30" y1="-17" x2="30" y2="17" stroke="{accent}" stroke-width="1" opacity="0.3"/>""",
    "devops": """
    <path d="M-20,0 A20 20 0 0 1 20,0" fill="none" stroke="{accent}" stroke-width="3"/>
    <path d="M20,0 A20 20 0 0 1 -20,0" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="5 3"/>
    <polygon points="20,-5 28,0 20,5" fill="{accent}"/>
    <polygon points="-20,5 -28,0 -20,-5" fill="{accent}"/>
    <rect x="-55" y="-8" width="20" height="16" rx="3" fill="none" stroke="{accent}" stroke-width="2" opacity="0.5"/>
    <rect x="35" y="-8" width="20" height="16" rx="3" fill="none" stroke="{accent}" stroke-width="2" opacity="0.5"/>
    <line x1="-35" y1="0" x2="-28" y2="0" stroke="{accent}" stroke-width="1.5" opacity="0.4"/>
    <line x1="28" y1="0" x2="35" y2="0" stroke="{accent}" stroke-width="1.5" opacity="0.4"/>""",
    "blockchain": """
    <rect x="-20" y="-30" width="40" height="20" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <rect x="-20" y="-5" width="40" height="20" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <rect x="-20" y="20" width="40" height="20" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <line x1="0" y1="-10" x2="0" y2="-5" stroke="{accent}" stroke-width="2"/>
    <line x1="0" y1="15" x2="0" y2="20" stroke="{accent}" stroke-width="2"/>
    <line x1="-30" y1="-20" x2="-20" y2="-20" stroke="{accent}" stroke-width="1.5" opacity="0.4" stroke-dasharray="3 2"/>
    <line x1="20" y1="5" x2="30" y2="5" stroke="{accent}" stroke-width="1.5" opacity="0.4" stroke-dasharray="3 2"/>""",
    "finops": """
    <circle r="35" fill="none" stroke="{accent}" stroke-width="2.5" stroke-dasharray="8 4"/>
    <text x="0" y="8" font-family="Arial,sans-serif" font-size="32" font-weight="bold" fill="{accent}" text-anchor="middle" opacity="0.8">$</text>
    <line x1="-50" y1="20" x2="-35" y2="-10" stroke="{accent}" stroke-width="2" opacity="0.4"/>
    <line x1="-35" y1="-10" x2="-15" y2="5" stroke="{accent}" stroke-width="2" opacity="0.4"/>
    <line x1="15" y1="-5" x2="35" y2="-20" stroke="{accent}" stroke-width="2" opacity="0.4"/>
    <line x1="35" y1="-20" x2="50" y2="-15" stroke="{accent}" stroke-width="2" opacity="0.4"/>""",
}


def _strip_korean(text: str) -> str:
    """SVG 텍스트에서 한글 제거 - SVG는 영문만 허용"""
    if not text:
        return ""
    result = []
    for char in text:
        if (
            "\uac00" <= char <= "\ud7a3"
            or "\u3131" <= char <= "\u3163"
            or "\u3165" <= char <= "\u318e"
        ):
            result.append(" ")
        else:
            result.append(char)
    cleaned = " ".join("".join(result).split())
    return cleaned.strip(" ,;:-") or "Tech Blog"


def _escape_svg_text(text: str) -> str:
    """SVG 텍스트 이스케이프 (한글 자동 제거 포함)"""
    if not text:
        return ""
    text = _strip_korean(text)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _truncate_title(title: str, max_len: int = 50) -> str:
    """제목 길이 제한 - 핵심 키워드만 추출하여 축약 (잘림 방지)"""
    if not title:
        return "Tech Blog Post"
    if len(title) <= max_len:
        return title

    # Strategy 1: Split by common delimiters and take first meaningful part
    for delim in [" - ", ": ", ", ", " | "]:
        parts = [p.strip() for p in title.split(delim) if p.strip()]
        if len(parts) >= 2:
            result = parts[0]
            for part in parts[1:]:
                candidate = result + " + " + part
                if len(candidate) <= max_len:
                    result = candidate
                else:
                    break
            if len(result) <= max_len:
                return result

    # Strategy 2: Extract key technical words (skip filler words)
    skip_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "in",
        "on",
        "to",
        "for",
        "with",
        "from",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "complete",
        "guide",
        "practical",
        "comprehensive",
        "understanding",
        "overview",
        "introduction",
        "analysis",
        "perspective",
        "strategy",
    }
    words = [w for w in title.split() if w.lower() not in skip_words]
    result = ""
    for word in words:
        candidate = (result + " " + word).strip() if result else word
        if len(candidate) <= max_len:
            result = candidate
        else:
            break

    return result.rstrip(" ,;:-") if result else title.split()[0]


def _extract_keywords_from_title(title: str) -> list:
    """제목에서 키워드 추출"""
    keywords = []
    tech_terms = [
        "AI",
        "ML",
        "Security",
        "Cloud",
        "AWS",
        "Azure",
        "GCP",
        "Kubernetes",
        "K8s",
        "Docker",
        "DevOps",
        "DevSecOps",
        "API",
        "Terraform",
        "CI/CD",
        "Zero-Day",
        "CVE",
        "Vulnerability",
        "Patch",
        "Update",
        "Release",
    ]
    for term in tech_terms:
        if term.lower() in title.lower():
            keywords.append(term)
        if len(keywords) >= 4:
            break
    return keywords if keywords else ["Tech", "Blog", "Update"]


_VISUAL_TOKEN_PATTERNS = [
    (r"ai agent|agentic", "AI AGENT"),
    (r"prompt injection", "PROMPT INJECTION"),
    (r"\brag\b", "RAG"),
    (r"\bmcp\b", "MCP"),
    (r"llm|gpt|model", "LLM"),
    (r"zero[\s-]?day|0-day|cve-\d{4}-\d+", "ZERO DAY"),
    (r"ransomware", "RANSOMWARE"),
    (r"malware|trojan|botnet|rootkit", "MALWARE"),
    (r"phishing|vishing|aitm", "PHISHING"),
    (r"identity|iam|mfa|passkey|auth", "IDENTITY"),
    (r"zero trust|ztna", "ZERO TRUST"),
    (r"incident|outage|postmortem|breach", "INCIDENT"),
    (r"architecture|design", "ARCHITECTURE"),
    (r"pipeline|ci/cd|deployment", "PIPELINE"),
    (r"devsecops", "DEVSECOPS"),
    (r"devops", "DEVOPS"),
    (r"kubernetes|\bk8s\b|container|docker|helm|eks|gke", "KUBERNETES"),
    (r"cloud|aws|azure|gcp|serverless", "CLOUD"),
    (r"finops|cost|billing", "FINOPS"),
    (r"blockchain|bitcoin|crypto|defi|wallet", "BLOCKCHAIN"),
    (r"tesla|vehicle|automotive", "AUTOMATION"),
    (r"owasp", "OWASP"),
    (r"api", "API"),
    (r"security|threat|exploit|patch", "SECURITY"),
]


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _normalize_cover_label(text: str, max_len: int = 22) -> str:
    cleaned = _strip_korean(text or "")
    cleaned = cleaned.upper()
    cleaned = re.sub(r"[^A-Z0-9/+ ]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" /+-")
    if not cleaned:
        return ""
    if len(cleaned) <= max_len:
        return cleaned
    truncated = cleaned[:max_len]
    split = truncated.rfind(" ")
    if split > max_len * 0.55:
        truncated = truncated[:split]
    return truncated.rstrip(" /+-")


def _extract_visual_tokens(post_info: Dict, limit: int = 5) -> list[str]:
    title = str(post_info.get("title", ""))
    excerpt = str(post_info.get("excerpt", ""))
    category = str(post_info.get("category", "tech")).lower()
    tags = [str(tag) for tag in post_info.get("tags", [])]
    haystack = " ".join([title, excerpt, " ".join(tags), category]).lower()

    tokens: list[str] = []
    for pattern, label in _VISUAL_TOKEN_PATTERNS:
        if re.search(pattern, haystack):
            tokens.append(label)

    for raw_tag in tags:
        normalized = _normalize_cover_label(raw_tag, max_len=18)
        if normalized and len(normalized) >= 3:
            tokens.append(normalized)

    category_label = CATEGORY_SVG_CONFIG.get(category, CATEGORY_SVG_CONFIG["tech"])[
        "label"
    ]
    tokens.append(category_label)
    tokens.append("TECH BLOG")

    return _dedupe_preserve_order(tokens)[:limit]


def _wrap_cover_phrase(text: str, max_chars: int = 22, max_lines: int = 2) -> list[str]:
    normalized = _normalize_cover_label(text, max_len=max_chars * max_lines)
    if not normalized:
        return []

    words = normalized.split()
    if not words:
        return []

    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines - 1:
            break

    if current and len(lines) < max_lines:
        lines.append(current[:max_chars].rstrip())

    return lines[:max_lines]


def _compose_cover_headline(post_info: Dict, tokens: list[str]) -> list[str]:
    title = str(post_info.get("title", ""))
    english_title = _strip_korean(title)
    english_title = re.sub(r"[_|]+", " ", english_title)
    english_title = re.sub(r"\s+", " ", english_title).strip()

    if len(english_title) >= 10:
        lines = _wrap_cover_phrase(english_title, max_chars=22, max_lines=2)
        if lines:
            if len(lines) == 1:
                fallback_line = next(
                    (
                        _normalize_cover_label(token, max_len=22)
                        for token in tokens
                        if _normalize_cover_label(token, max_len=22) != lines[0]
                    ),
                    "UPDATE",
                )
                lines.append(fallback_line or "UPDATE")
            return lines[:2]

    headline_lines: list[str] = []
    for token in tokens[:2]:
        normalized = _normalize_cover_label(token, max_len=22)
        if normalized:
            headline_lines.append(normalized)

    if not headline_lines:
        headline_lines = ["TECH BLOG", "UPDATE"]
    elif len(headline_lines) == 1:
        headline_lines.append("UPDATE")

    return headline_lines[:2]


def _render_cover_token_chips(tokens: list[str], accent: str) -> str:
    chip_parts = []
    x = 84
    for token in tokens[:3]:
        width = max(110, min(220, 34 + len(token) * 10))
        chip_parts.append(
            f'''  <g transform="translate({x} 474)">
    <rect width="{width}" height="38" rx="19" fill="{accent}" opacity="0.16" stroke="{accent}" stroke-width="1.2"/>
    <text x="{width / 2:.1f}" y="24" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#e2e8f0" text-anchor="middle">{_escape_svg_text(token)}</text>
  </g>'''
        )
        x += width + 14
    return "\n".join(chip_parts)


def _render_cover_metric_cards(
    category_label: str, accent: str, tokens: list[str], tag_count: int
) -> str:
    metrics = [
        ("CATEGORY", category_label),
        ("SIGNALS", f"{max(2, len(tokens)):02d}"),
        ("TAGS", f"{tag_count:02d}"),
    ]
    x_positions = [84, 246, 408]
    cards = []
    for x, (label, value) in zip(x_positions, metrics):
        cards.append(
            f'''  <g transform="translate({x} 536)">
    <rect width="144" height="58" rx="16" fill="#111827" fill-opacity="0.78" stroke="{accent}" stroke-opacity="0.35" stroke-width="1.2"/>
    <text x="18" y="24" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="#94a3b8">{label}</text>
    <text x="18" y="43" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">{_escape_svg_text(value)}</text>
  </g>'''
        )
    return "\n".join(cards)


def generate_fallback_svg(post_info: Dict, output_path: Path) -> bool:
    """API 없이 고품질 SVG 이미지 생성"""
    try:
        category = post_info.get("category", "tech").lower()
        tags = post_info.get("tags", [])
        config = CATEGORY_SVG_CONFIG.get(category, CATEGORY_SVG_CONFIG["tech"])
        category_label = config["label"]
        tokens = _extract_visual_tokens(post_info, limit=5)
        headline_lines = _compose_cover_headline(post_info, tokens)
        subtitle = " / ".join(tokens[:3])
        date_str = datetime.now().strftime("%B %d, %Y")
        visual_direction = _build_visual_direction(post_info)
        layout_variant = int(visual_direction["seed"]) % 3

        illustration = _CATEGORY_ILLUSTRATIONS.get(
            category, _CATEGORY_ILLUSTRATIONS.get("tech", "")
        )
        if not illustration:
            illustration = _CATEGORY_ILLUSTRATIONS.get("security", "")
        illustration = illustration.replace("{accent}", config["accent"])

        hero_group = {
            0: {"x": 760, "y": 116, "w": 352, "h": 312, "cx": 936, "cy": 270},
            1: {"x": 720, "y": 132, "w": 388, "h": 292, "cx": 914, "cy": 278},
            2: {"x": 736, "y": 104, "w": 362, "h": 326, "cx": 917, "cy": 270},
        }[layout_variant]

        orbit_lines = {
            0: """
  <path d="M712 178 C780 150 850 150 936 190" fill="none" stroke="#60a5fa" stroke-width="1.3" opacity="0.26"/>
  <path d="M724 414 C796 438 870 438 948 398" fill="none" stroke="#c084fc" stroke-width="1.2" opacity="0.22"/>
""",
            1: """
  <path d="M704 148 C792 118 892 122 980 176" fill="none" stroke="#67e8f9" stroke-width="1.3" opacity="0.24"/>
  <path d="M716 430 C804 462 914 458 1010 390" fill="none" stroke="#f59e0b" stroke-width="1.2" opacity="0.22"/>
""",
            2: """
  <path d="M724 152 C822 126 922 136 1020 202" fill="none" stroke="#f59e0b" stroke-width="1.3" opacity="0.24"/>
  <path d="M706 420 C782 454 878 462 968 410" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.22"/>
""",
        }[layout_variant]

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{_escape_svg_text(" ".join(headline_lines))}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120"/>
      <stop offset="52%" stop-color="#121a2f"/>
      <stop offset="100%" stop-color="#170f25"/>
    </linearGradient>
    <linearGradient id="panel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="#111827" stop-opacity="0.86"/>
    </linearGradient>
    <pattern id="microGrid" x="0" y="0" width="36" height="36" patternUnits="userSpaceOnUse">
      <path d="M36 0H0V36" fill="none" stroke="#334155" stroke-width="1" opacity="0.25"/>
      <circle cx="18" cy="18" r="1.2" fill="{config["accent"]}" opacity="0.15"/>
    </pattern>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="sg" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="36"/>
    </filter>
    <filter id="shadow" x="-30%" y="-30%" width="180%" height="180%">
      <feDropShadow dx="0" dy="14" stdDeviation="22" flood-color="#020617" flood-opacity="0.42"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#microGrid)"/>
  <circle cx="202" cy="150" r="190" fill="{config["accent"]}" opacity="0.08" filter="url(#sg)"/>
  <circle cx="1020" cy="486" r="220" fill="{config["gradient_end"]}" opacity="0.08" filter="url(#sg)"/>
  <circle cx="920" cy="160" r="140" fill="#38bdf8" opacity="0.04" filter="url(#sg)"/>
  <path d="M0 96 C224 46 426 44 654 118 L654 630 L0 630 Z" fill="#020617" opacity="0.24"/>
  <path d="M0 526 C248 490 426 486 654 548" fill="none" stroke="#475569" stroke-width="1.2" opacity="0.22"/>
  <rect x="{hero_group["x"]}" y="{hero_group["y"]}" width="{hero_group["w"]}" height="{hero_group["h"]}" rx="28" fill="url(#panel)" stroke="{config["accent"]}" stroke-opacity="0.28" stroke-width="1.4" filter="url(#shadow)"/>
  <rect x="{hero_group["x"] + 18}" y="{hero_group["y"] + 18}" width="{hero_group["w"] - 36}" height="{hero_group["h"] - 36}" rx="22" fill="none" stroke="#334155" stroke-opacity="0.7" stroke-width="1"/>
  <rect x="{hero_group["x"] + 22}" y="{hero_group["y"] + 20}" width="108" height="12" rx="6" fill="{config["accent"]}" opacity="0.28"/>
  <rect x="{hero_group["x"] + 144}" y="{hero_group["y"] + 20}" width="72" height="12" rx="6" fill="#334155" opacity="0.55"/>
  <rect x="{hero_group["x"] + 228}" y="{hero_group["y"] + 20}" width="48" height="12" rx="6" fill="#334155" opacity="0.35"/>
  {orbit_lines}
  <g transform="translate({hero_group["cx"]},{hero_group["cy"]})" filter="url(#shadow)">
    <circle r="96" fill="#0f172a" stroke="{config["accent"]}" stroke-width="2.6" opacity="0.94"/>
    <circle r="124" fill="none" stroke="{config["accent"]}" stroke-opacity="0.15" stroke-width="1.2" stroke-dasharray="8 8"/>
    <circle r="54" fill="none" stroke="#e2e8f0" stroke-opacity="0.15" stroke-width="1"/>
{illustration}
  </g>
  <g transform="translate(84 66)">
    <rect width="164" height="36" rx="18" fill="{config["accent"]}" opacity="0.2" stroke="{config["accent"]}" stroke-width="1.2"/>
    <text x="82" y="23" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{config["accent"]}" text-anchor="middle">{category_label}</text>
  </g>
  <text x="84" y="170" font-family="Arial,sans-serif" font-size="54" font-weight="700" fill="#f8fafc" letter-spacing="0.5">{_escape_svg_text(headline_lines[0])}</text>
  <text x="84" y="232" font-family="Arial,sans-serif" font-size="52" font-weight="700" fill="#dbeafe" letter-spacing="0.5">{_escape_svg_text(headline_lines[1])}</text>
  <text x="84" y="288" font-family="Arial,sans-serif" font-size="18" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>
  <rect x="84" y="314" width="520" height="1.5" fill="#334155" opacity="0.9"/>
  <text x="84" y="344" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#94a3b8">VISUAL SYSTEM {visual_direction["id"].upper()}</text>
  <text x="84" y="372" font-family="Arial,sans-serif" font-size="14" fill="#94a3b8">Clean technical cover with stronger depth, hierarchy, and category-specific structure.</text>
{_render_cover_token_chips(tokens, config["accent"])}
{_render_cover_metric_cards(category_label, config["accent"], tokens, len(tags))}
  <g transform="translate(1030 74)">
    <rect width="130" height="34" rx="17" fill="#1d4ed8" opacity="0.18" stroke="#3b82f6" stroke-width="1.2"/>
    <text x="65" y="22" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#bfdbfe" text-anchor="middle">{date_str}</text>
  </g>
  <line x1="50" y1="588" x2="1150" y2="588" stroke="#334155" stroke-width="1" opacity="0.5"/>
  <text x="1150" y="612" font-family="Arial,sans-serif" font-size="13" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>'''

        output_svg = output_path.with_suffix(".svg")
        svg_content = validate_and_fix_svg(svg_content)
        with open(output_svg, "w", encoding="utf-8") as f:
            f.write(svg_content)

        log_message(f"✅ SVG 폴백 이미지 생성 완료: {output_svg.name}", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"❌ SVG 폴백 이미지 생성 실패: {str(e)}", "ERROR")
        return False


_SECTION_BANNER_CONFIG = {
    "section-security.svg": {
        "label": "SECURITY",
        "subtitle": "Threat defense and response",
        "accent": "#ef4444",
        "secondary": "#f59e0b",
        "motif": """
  <path d="M0,-120 C70,-120 118,-82 118,-12 C118,70 62,126 0,156 C-62,126 -118,70 -118,-12 C-118,-82 -70,-120 0,-120Z" fill="#0f172a" stroke="{accent}" stroke-width="2.8"/>
  <path d="M-4,-92 L10,-50 L-10,-8 L16,38 L-12,84" fill="none" stroke="#fca5a5" stroke-width="3" stroke-linecap="round"/>
  <rect x="-24" y="-8" width="48" height="36" rx="7" fill="none" stroke="{accent}" stroke-width="2.2"/>
  <path d="M-14,-8 L-14,-24 C-14,-42 14,-42 14,-24 L14,-8" fill="none" stroke="{accent}" stroke-width="2.4"/>
  <circle cx="0" cy="12" r="5" fill="{accent}" opacity="0.7"/>
  <path d="M-240,-44 C-174,-20 -122,6 -74,40" fill="none" stroke="{secondary}" stroke-width="2" stroke-dasharray="8 6" opacity="0.42"/>
  <path d="M240,-44 C174,-20 122,6 74,40" fill="none" stroke="#60a5fa" stroke-width="2" stroke-dasharray="8 6" opacity="0.42"/>
""",
    },
    "section-ai-ml.svg": {
        "label": "AI ML",
        "subtitle": "Models agents and inference systems",
        "accent": "#6366f1",
        "secondary": "#22d3ee",
        "motif": """
  <circle r="22" fill="{accent}" opacity="0.18"/>
  <circle r="8" fill="{accent}" opacity="0.55"/>
  <circle cx="-108" cy="-72" r="18" fill="#0f172a" stroke="{secondary}" stroke-width="1.8"/>
  <circle cx="108" cy="-72" r="18" fill="#0f172a" stroke="{secondary}" stroke-width="1.8"/>
  <circle cx="-138" cy="54" r="16" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <circle cx="138" cy="54" r="16" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <circle cx="0" cy="-126" r="16" fill="#0f172a" stroke="{secondary}" stroke-width="1.8"/>
  <g stroke="{secondary}" stroke-width="1.8" opacity="0.46">
    <line x1="0" y1="0" x2="-108" y2="-72"/><line x1="0" y1="0" x2="108" y2="-72"/>
    <line x1="0" y1="0" x2="-138" y2="54"/><line x1="0" y1="0" x2="138" y2="54"/>
    <line x1="0" y1="0" x2="0" y2="-126"/>
  </g>
""",
    },
    "section-ai.svg": {
        "label": "AI",
        "subtitle": "Applied AI and agent engineering",
        "accent": "#06b6d4",
        "secondary": "#3b82f6",
        "motif": """
  <rect x="-76" y="-64" width="152" height="128" rx="24" fill="#0f172a" stroke="{accent}" stroke-width="2.6"/>
  <circle cx="0" cy="-6" r="36" fill="none" stroke="{secondary}" stroke-width="2"/>
  <path d="M-18 -6 h36 M0 -24 v36" stroke="{secondary}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="-128" cy="0" r="18" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <circle cx="128" cy="0" r="18" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <path d="M-110 0 C-82 0 -62 -6 -44 -18" fill="none" stroke="{accent}" stroke-width="1.8" opacity="0.4"/>
  <path d="M110 0 C82 0 62 -6 44 -18" fill="none" stroke="{accent}" stroke-width="1.8" opacity="0.4"/>
""",
    },
    "section-cloud.svg": {
        "label": "CLOUD",
        "subtitle": "Platform architecture and operations",
        "accent": "#3b82f6",
        "secondary": "#22c55e",
        "motif": """
  <path d="M-82,34 C-130,34 -156,6 -156,-28 C-156,-62 -126,-92 -90,-92 C-84,-126 -48,-150 -8,-150 C34,-150 72,-122 78,-88 C118,-88 146,-58 146,-24 C146,10 120,34 82,34 Z" fill="#0f172a" stroke="{accent}" stroke-width="2.5"/>
  <rect x="-96" y="76" width="58" height="38" rx="8" fill="#0f172a" stroke="{secondary}" stroke-width="1.6"/>
  <rect x="-28" y="66" width="58" height="48" rx="8" fill="#0f172a" stroke="{accent}" stroke-width="1.6"/>
  <rect x="40" y="76" width="58" height="38" rx="8" fill="#0f172a" stroke="{secondary}" stroke-width="1.6"/>
  <g stroke="#475569" stroke-width="1.4" opacity="0.45">
    <line x1="-67" y1="76" x2="-67" y2="44"/><line x1="1" y1="66" x2="1" y2="36"/><line x1="69" y1="76" x2="69" y2="44"/>
    <line x1="-67" y1="44" x2="1" y2="28"/><line x1="69" y1="44" x2="1" y2="28"/>
  </g>
""",
    },
    "section-devops.svg": {
        "label": "DEVOPS",
        "subtitle": "Delivery reliability and automation",
        "accent": "#f59e0b",
        "secondary": "#3b82f6",
        "motif": """
  <rect x="-190" y="-44" width="96" height="88" rx="18" fill="#0f172a" stroke="{accent}" stroke-width="2"/>
  <rect x="-48" y="-58" width="96" height="116" rx="18" fill="#0f172a" stroke="{secondary}" stroke-width="2"/>
  <rect x="94" y="-44" width="96" height="88" rx="18" fill="#0f172a" stroke="{accent}" stroke-width="2"/>
  <path d="M-94 0 H-48" fill="none" stroke="#475569" stroke-width="2" stroke-dasharray="8 6"/>
  <path d="M48 0 H94" fill="none" stroke="#475569" stroke-width="2" stroke-dasharray="8 6"/>
  <text x="-142" y="8" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="{accent}" text-anchor="middle">BUILD</text>
  <text x="0" y="8" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="{secondary}" text-anchor="middle">TEST</text>
  <text x="142" y="8" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="{accent}" text-anchor="middle">RUN</text>
""",
    },
    "section-devsecops.svg": {
        "label": "DEVSECOPS",
        "subtitle": "Pipelines guardrails and controls",
        "accent": "#8b5cf6",
        "secondary": "#22c55e",
        "motif": """
  <rect x="-196" y="-44" width="96" height="88" rx="18" fill="#0f172a" stroke="{accent}" stroke-width="2"/>
  <rect x="-48" y="-58" width="96" height="116" rx="18" fill="#0f172a" stroke="{secondary}" stroke-width="2"/>
  <rect x="100" y="-44" width="96" height="88" rx="18" fill="#0f172a" stroke="{accent}" stroke-width="2"/>
  <path d="M-100 0 H-48" fill="none" stroke="#475569" stroke-width="2" stroke-dasharray="8 6"/>
  <path d="M48 0 H100" fill="none" stroke="#475569" stroke-width="2" stroke-dasharray="8 6"/>
  <path d="M-18 -10 L-4 8 L18 -18" fill="none" stroke="{secondary}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="-148" y="8" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="{accent}" text-anchor="middle">CODE</text>
  <text x="148" y="8" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="{accent}" text-anchor="middle">SHIP</text>
""",
    },
    "section-blockchain.svg": {
        "label": "BLOCKCHAIN",
        "subtitle": "Ledger protocols and ecosystem risk",
        "accent": "#8b5cf6",
        "secondary": "#f59e0b",
        "motif": """
  <rect x="-110" y="-96" width="220" height="54" rx="10" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <rect x="-110" y="-22" width="220" height="54" rx="10" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <rect x="-110" y="52" width="220" height="54" rx="10" fill="#0f172a" stroke="{accent}" stroke-width="1.8"/>
  <g stroke="{secondary}" stroke-width="1.5" opacity="0.36">
    <line x1="-126" y1="-70" x2="-164" y2="-70"/><line x1="126" y1="-70" x2="164" y2="-70"/>
    <line x1="-126" y1="4" x2="-164" y2="4"/><line x1="126" y1="4" x2="164" y2="4"/>
    <line x1="-126" y1="78" x2="-164" y2="78"/><line x1="126" y1="78" x2="164" y2="78"/>
  </g>
""",
    },
    "section-tech.svg": {
        "label": "TECH",
        "subtitle": "Signals across platforms cloud and tools",
        "accent": "#3b82f6",
        "secondary": "#ef4444",
        "motif": """
  <circle cx="0" cy="0" r="146" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.24"/>
  <circle cx="0" cy="0" r="106" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.28"/>
  <circle cx="0" cy="0" r="66" fill="none" stroke="{accent}" stroke-width="1.4" opacity="0.36"/>
  <line x1="-164" y1="0" x2="164" y2="0" stroke="#475569" stroke-width="1" opacity="0.32"/>
  <line x1="0" y1="-164" x2="0" y2="164" stroke="#475569" stroke-width="1" opacity="0.32"/>
  <path d="M0 0 L88 -94" fill="none" stroke="{secondary}" stroke-width="2.2" opacity="0.52"/>
  <circle cx="88" cy="-94" r="8" fill="{secondary}" opacity="0.7"/>
  <circle cx="-48" cy="62" r="7" fill="{accent}" opacity="0.65"/>
  <circle cx="112" cy="36" r="5" fill="{secondary}" opacity="0.52"/>
""",
    },
}


def generate_section_banner_svg(filename: str) -> str:
    config = _SECTION_BANNER_CONFIG[filename]
    accent = config["accent"]
    secondary = config["secondary"]
    motif = (
        config["motif"]
        .replace("{accent}", accent)
        .replace("{secondary}", secondary)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{filename[:-4]}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#08101f"/>
      <stop offset="58%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#170f25"/>
    </linearGradient>
    <pattern id="microGrid" x="0" y="0" width="34" height="34" patternUnits="userSpaceOnUse">
      <path d="M34 0H0V34" fill="none" stroke="#334155" stroke-width="1" opacity="0.24"/>
      <circle cx="17" cy="17" r="1.1" fill="{accent}" opacity="0.14"/>
    </pattern>
    <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <filter id="shadow" x="-30%" y="-30%" width="180%" height="180%">
      <feDropShadow dx="0" dy="14" stdDeviation="20" flood-color="#020617" flood-opacity="0.42"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#microGrid)"/>
  <circle cx="180" cy="118" r="190" fill="{accent}" opacity="0.08" filter="url(#softGlow)"/>
  <circle cx="1010" cy="500" r="220" fill="{secondary}" opacity="0.06" filter="url(#softGlow)"/>
  <path d="M0 520 C228 476 426 476 640 544" fill="none" stroke="#475569" stroke-width="1.2" opacity="0.24"/>
  <g transform="translate(84 70)">
    <rect width="170" height="36" rx="18" fill="{accent}" opacity="0.18" stroke="{accent}" stroke-width="1.2"/>
    <text x="85" y="23" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{accent}" text-anchor="middle">{config["label"]}</text>
  </g>
  <text x="84" y="174" font-family="Arial,sans-serif" font-size="56" font-weight="700" fill="#f8fafc">{config["label"]}</text>
  <text x="84" y="226" font-family="Arial,sans-serif" font-size="20" fill="#cbd5e1">{config["subtitle"]}</text>
  <rect x="84" y="260" width="510" height="1.5" fill="#334155" opacity="0.9"/>
  <g transform="translate(860 318)" filter="url(#shadow)">
    <rect x="-204" y="-170" width="408" height="340" rx="30" fill="#0f172a" fill-opacity="0.82" stroke="{accent}" stroke-opacity="0.28" stroke-width="1.4"/>
    <rect x="-182" y="-148" width="364" height="296" rx="24" fill="none" stroke="#334155" stroke-opacity="0.7" stroke-width="1"/>
    {motif}
  </g>
  <g transform="translate(84 470)">
    <rect width="176" height="40" rx="20" fill="{accent}" opacity="0.14" stroke="{accent}" stroke-width="1.2"/>
    <text x="88" y="25" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#e2e8f0" text-anchor="middle">SECTION BANNER</text>
  </g>
  <g transform="translate(274 470)">
    <rect width="220" height="40" rx="20" fill="{secondary}" opacity="0.14" stroke="{secondary}" stroke-width="1.2"/>
    <text x="110" y="25" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#e2e8f0" text-anchor="middle">POST NAVIGATION</text>
  </g>
  <line x1="50" y1="588" x2="1150" y2="588" stroke="#334155" stroke-width="1" opacity="0.5"/>
  <text x="1150" y="612" font-family="Arial,sans-serif" font-size="13" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>'''


def regenerate_section_banners() -> int:
    generated = 0
    for filename in sorted(_SECTION_BANNER_CONFIG):
        output_path = IMAGES_DIR / filename
        svg_content = validate_and_fix_svg(generate_section_banner_svg(filename))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        generated += 1
    log_message(f"✅ 섹션 배너 재생성 완료: {generated}개", "SUCCESS")
    return generated


# Node definitions for THREAT SIGNAL MAP SVG (Digest posts)
_DIGEST_NODE_DEFS = {
    "ransomware": {
        "label": "RANSOMWARE",
        "color": "#dc2626",
        "icon": '<rect x="-22" y="-4" width="44" height="36" rx="8" fill="#221617" stroke="{color}" stroke-width="2"/>'
        '<path d="M-12 -4 v-16 c0-18 24-18 24 0 v16" stroke="{color}" stroke-width="4" fill="none" stroke-linecap="round"/>'
        '<circle cx="0" cy="16" r="6" fill="{color}"/><rect x="-2" y="20" width="4" height="10" rx="2" fill="{color}"/>',
    },
    "zero-day": {
        "label": "ZERO DAY",
        "color": "#dc2626",
        "icon": '<rect x="-20" y="-16" width="40" height="32" rx="6" fill="#1a1020" stroke="{color}" stroke-width="2"/>'
        '<text x="0" font-family="Courier New" fill="{color}" text-anchor="middle"><tspan y="-2" font-size="11" font-weight="700">CVE</tspan><tspan x="0" y="12" font-size="8" opacity="0.7">0-DAY</tspan></text>',
    },
    "malware": {
        "label": "MALWARE",
        "color": "#f59e0b",
        "icon": '<circle r="16" fill="{color}" opacity="0.2"/>'
        '<circle cx="-12" cy="-8" r="6" fill="{color}" opacity="0.5"/>'
        '<circle cx="12" cy="8" r="6" fill="{color}" opacity="0.5"/>'
        '<circle cx="8" cy="-12" r="4" fill="{color}" opacity="0.4"/>',
    },
    "blockchain": {
        "label": "BLOCKCHAIN",
        "color": "#8b5cf6",
        "icon": '<ellipse cx="-10" cy="-6" rx="14" ry="10" fill="none" stroke="{color}" stroke-width="2.5" transform="rotate(-30 -10 -6)"/>'
        '<ellipse cx="10" cy="6" rx="14" ry="10" fill="none" stroke="{color}" stroke-width="2.5" transform="rotate(-30 10 6)"/>'
        '<circle cx="-18" cy="18" r="3" fill="{color}" opacity="0.6"/>'
        '<circle cx="18" cy="-18" r="3" fill="{color}" opacity="0.6"/>',
    },
    "ai": {
        "label": "AI/ML",
        "color": "#22d3ee",
        "icon": '<circle r="14" fill="none" stroke="{color}" stroke-width="2"/>'
        '<circle r="6" fill="{color}" opacity="0.4"/>'
        '<line x1="-20" y1="-14" x2="-8" y2="-6" stroke="{color}" stroke-width="1.5"/>'
        '<line x1="20" y1="-14" x2="8" y2="-6" stroke="{color}" stroke-width="1.5"/>'
        '<line x1="-20" y1="14" x2="-8" y2="6" stroke="{color}" stroke-width="1.5"/>'
        '<line x1="20" y1="14" x2="8" y2="6" stroke="{color}" stroke-width="1.5"/>'
        '<circle cx="-20" cy="-14" r="4" fill="{color}" opacity="0.5"/>'
        '<circle cx="20" cy="-14" r="4" fill="{color}" opacity="0.5"/>'
        '<circle cx="-20" cy="14" r="4" fill="{color}" opacity="0.5"/>'
        '<circle cx="20" cy="14" r="4" fill="{color}" opacity="0.5"/>',
    },
    "cloud": {
        "label": "CLOUD",
        "color": "#3b82f6",
        "icon": '<ellipse cx="0" cy="4" rx="22" ry="14" fill="none" stroke="{color}" stroke-width="2"/>'
        '<circle cx="-8" cy="-4" r="10" fill="none" stroke="{color}" stroke-width="2"/>'
        '<circle cx="8" cy="-6" r="12" fill="none" stroke="{color}" stroke-width="2"/>',
    },
    "patch": {
        "label": "PATCH",
        "color": "#22c55e",
        "icon": '<path d="M0 -24 L20 -12 L20 8 C20 22 0 32 0 32 C0 32 -20 22 -20 8 L-20 -12 Z" fill="none" stroke="{color}" stroke-width="2.5"/>'
        '<path d="M-8 2 L-2 8 L10 -6" stroke="{color}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    },
    "supply-chain": {
        "label": "SUPPLY CHAIN",
        "color": "#f97316",
        "icon": '<rect x="-18" y="-12" width="14" height="14" rx="3" fill="none" stroke="{color}" stroke-width="2"/>'
        '<rect x="4" y="-12" width="14" height="14" rx="3" fill="none" stroke="{color}" stroke-width="2"/>'
        '<rect x="-7" y="6" width="14" height="14" rx="3" fill="none" stroke="{color}" stroke-width="2"/>'
        '<line x1="-4" y1="2" x2="-1" y2="6" stroke="{color}" stroke-width="1.5"/>'
        '<line x1="11" y1="2" x2="4" y2="6" stroke="{color}" stroke-width="1.5"/>',
    },
    "auth": {
        "label": "AUTH",
        "color": "#eab308",
        "icon": '<rect x="-16" y="-4" width="32" height="24" rx="4" fill="none" stroke="{color}" stroke-width="2"/>'
        '<path d="M-8 -4 v-10 c0-12 16-12 16 0 v10" stroke="{color}" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        '<circle cx="0" cy="8" r="4" fill="{color}"/>',
    },
    "kubernetes": {
        "label": "K8S",
        "color": "#326ce5",
        "icon": '<polygon points="0,-22 20,-8 12,18 -12,18 -20,-8" fill="none" stroke="{color}" stroke-width="2.5"/>'
        '<circle r="6" fill="{color}" opacity="0.4"/>'
        '<line x1="0" y1="-6" x2="0" y2="-18" stroke="{color}" stroke-width="1.5"/>'
        '<line x1="5" y1="3" x2="16" y2="12" stroke="{color}" stroke-width="1.5"/>'
        '<line x1="-5" y1="3" x2="-16" y2="12" stroke="{color}" stroke-width="1.5"/>',
    },
    "devops": {
        "label": "DEVOPS",
        "color": "#f97316",
        "icon": '<path d="M-16 0 A16 16 0 0 1 16 0" fill="none" stroke="{color}" stroke-width="2.5"/>'
        '<path d="M16 0 A16 16 0 0 1 -16 0" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="4 3"/>'
        '<polygon points="16,-4 22,0 16,4" fill="{color}"/>'
        '<polygon points="-16,4 -22,0 -16,-4" fill="{color}"/>',
    },
    "finops": {
        "label": "FINOPS",
        "color": "#14b8a6",
        "icon": '<circle r="22" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="6 4"/>'
        '<path d="M2,-16 v4 c-7,1 -12,5 -12,10 c0,6 5,9 12,10 v7 c-4,-1 -8,-3 -11,-5 l-2,3 c3,3 8,5 13,6 v4 h3 v-4 c8,-1 13,-5 13,-11 c0,-6 -5,-9 -13,-10 v-7 c3,1 7,2 10,4 l2,-3 c-3,-3 -7,-5 -12,-5 v-4 z" fill="{color}"/>',
    },
}

# Keyword-to-node mapping for automatic detection
_DIGEST_KEYWORD_MAP = {
    "ransomware": "ransomware",
    "랜섬웨어": "ransomware",
    "zero-day": "zero-day",
    "제로데이": "zero-day",
    "0-day": "zero-day",
    "malware": "malware",
    "악성코드": "malware",
    "trojan": "malware",
    "트로이목마": "malware",
    "blockchain": "blockchain",
    "블록체인": "blockchain",
    "defi": "blockchain",
    "crypto": "blockchain",
    "bitcoin": "blockchain",
    "비트코인": "blockchain",
    "ai": "ai",
    "llm": "ai",
    "gpt": "ai",
    "ml": "ai",
    "cloud": "cloud",
    "aws": "cloud",
    "azure": "cloud",
    "gcp": "cloud",
    "클라우드": "cloud",
    "patch": "patch",
    "패치": "patch",
    "supply chain": "supply-chain",
    "공급망": "supply-chain",
    "authentication": "auth",
    "인증": "auth",
    "credential": "auth",
    "identity": "auth",
    "zero trust": "auth",
    "제로트러스트": "auth",
    "botnet": "malware",
    "봇넷": "malware",
    "spyware": "malware",
    "cve": "zero-day",
    "exploit": "zero-day",
    "익스플로잇": "zero-day",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "컨테이너": "kubernetes",
    "container": "kubernetes",
    "docker": "kubernetes",
    "helm": "kubernetes",
    "devops": "devops",
    "devsecops": "devops",
    "ci/cd": "devops",
    "pipeline": "devops",
    "finops": "finops",
    "cost": "finops",
    "billing": "finops",
    "비용": "finops",
}


def _detect_digest_nodes(post_info: Dict) -> list:
    """Detect up to 3 unique threat signal nodes from post content."""
    title = post_info.get("title", "").lower()
    tags = [str(t).lower() for t in post_info.get("tags", [])]
    text = f"{title} {' '.join(tags)}"

    seen = []
    # Check multi-word phrases first, use word boundary for short keywords
    for keyword in sorted(_DIGEST_KEYWORD_MAP.keys(), key=len, reverse=True):
        if len(keyword) <= 3:
            matched = bool(re.search(r"\b" + re.escape(keyword) + r"\b", text))
        else:
            matched = keyword in text
        if matched and _DIGEST_KEYWORD_MAP[keyword] not in seen:
            seen.append(_DIGEST_KEYWORD_MAP[keyword])
            if len(seen) >= 3:
                break

    # Ensure at least 2 nodes
    if len(seen) < 2:
        for fallback in ["ai", "patch", "malware"]:
            if fallback not in seen:
                seen.append(fallback)
                if len(seen) >= 2:
                    break

    return seen[:3]


def generate_digest_svg(post_info: Dict, output_path: Path) -> bool:
    """Generate THREAT SIGNAL MAP style SVG for Digest posts based on content."""
    try:
        nodes = _detect_digest_nodes(post_info)
        node_configs = [_DIGEST_NODE_DEFS[n] for n in nodes]

        # Extract date from filename or post_info
        date_str = post_info.get("date", "")
        if date_str:
            try:
                from datetime import datetime as dt

                parsed = dt.strptime(str(date_str)[:10], "%Y-%m-%d")
                date_display = parsed.strftime("%B %d, %Y")
            except (ValueError, TypeError):
                date_display = datetime.now().strftime("%B %d, %Y")
        else:
            date_display = datetime.now().strftime("%B %d, %Y")

        subtitle = "  ".join(nc["label"] for nc in node_configs)

        # Calculate node positions based on count
        if len(node_configs) == 2:
            positions = [350, 850]
        else:
            positions = [250, 600, 950]

        # Build node SVG elements
        nodes_svg = ""
        for i, (nc, x_pos) in enumerate(zip(node_configs, positions)):
            color = nc["color"]
            icon_svg = nc["icon"].replace("{color}", color)
            nodes_svg += f"""
  <g transform="translate({x_pos} 340)" filter="url(#shadow)">
    <circle r="56" fill="#0f172a" stroke="{color}" stroke-width="2.5"/>
    {icon_svg}
  </g>

"""

        # Node labels as single text element with tspans
        labels_svg = (
            '  <text font-family="Arial, sans-serif" font-size="16" font-weight="700">'
        )
        for nc, x_pos in zip(node_configs, positions):
            labels_svg += f'<tspan x="{x_pos}" y="448" fill="{nc["color"]}" text-anchor="middle">{nc["label"]}</tspan>'
        labels_svg += "</text>\n"

        # Connection dots between nodes
        dots_svg = ""
        for i in range(len(positions) - 1):
            mid_x = (positions[i] + positions[i + 1]) // 2
            dots_svg += f'  <circle cx="{mid_x}" cy="340" r="4" fill="#475569"/>\n'

        # Glow circles - position relative to nodes
        glows = ""
        glow_offsets = [(0, -170, 180), (0, -200, 160), (0, -120, 170)]
        for i, nc in enumerate(node_configs):
            dx, dy, r = glow_offsets[i]
            cx = positions[i] + dx
            cy = 340 + dy
            glows += f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{nc["color"]}" opacity="0.12" filter="url(#glow)"/>\n'

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>Tech Security Weekly Digest</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120"/>
      <stop offset="55%" stop-color="#151b32"/>
      <stop offset="100%" stop-color="#181024"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="18" flood-color="#020617" flood-opacity="0.5"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
{glows}  <text x="90" y="164" font-family="Arial, sans-serif" font-weight="700" fill="#f8fafc"><tspan font-size="52">THREAT SIGNAL MAP</tspan><tspan x="92" dy="40" font-size="20" fill="#cbd5e1">{subtitle}</tspan></text>
  <line x1="180" y1="340" x2="1020" y2="340" stroke="#475569" stroke-width="4" stroke-dasharray="14 10" opacity="0.8"/>
{nodes_svg}{labels_svg}{dots_svg}
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text font-family="Arial, sans-serif" font-size="14" fill="#94a3b8"><tspan x="90" y="574">{date_display}</tspan><tspan x="1110" y="574" text-anchor="end">tech.2twodragon.com</tspan></text>
</svg>"""

        output_svg = output_path.with_suffix(".svg")
        svg = validate_and_fix_svg(svg)
        with open(output_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        log_message(f"✅ Digest SVG 이미지 생성 완료: {output_svg.name}", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"❌ Digest SVG 생성 실패: {str(e)}", "ERROR")
        return False


# --- L22 stacked-bands cover for Weekly Digest posts ---
_DIGEST_TITLE_PATTERN = re.compile(
    r"Weekly\s+Digest|주간\s*다이제스트|Tech_Security_Weekly_Digest|Daily_Tech_Digest",
    re.IGNORECASE,
)

# Boilerplate H2 sections that appear in every digest and are not topics.
_DIGEST_BOILERPLATE_HEADINGS = {
    "서론",
    "📊 빠른 참조",
    "빠른 참조",
    "경영진 브리핑",
    "위험 스코어카드",
    "트렌드 분석",
    "실무 체크리스트",
    "이번 주 다이제스트",
    "참고 자료",
    "기타 주목할 뉴스",
}

# Keyword -> (theme, visual_factory_name, label) routing for L22 bands.
# Order matters: more specific keywords first.
_L22_KEYWORD_ROUTES = [
    ("ransomware", "red", "v_network_nodes", "RANSOMWARE", "RaaS"),
    ("랜섬웨어", "red", "v_network_nodes", "RANSOMWARE", "RaaS"),
    ("supply chain", "amber", "v_network_nodes", "SUPPLY CHAIN", "CHAIN"),
    ("공급망", "amber", "v_network_nodes", "SUPPLY CHAIN", "CHAIN"),
    ("zero-day", "amber", "v_lock_cve", "ZERO-DAY", "0-DAY"),
    ("zero day", "amber", "v_lock_cve", "ZERO-DAY", "0-DAY"),
    ("제로데이", "amber", "v_lock_cve", "ZERO-DAY", "0-DAY"),
    ("cve-", "amber", "v_lock_cve", "VULNERABILITY", "CVE"),
    ("cvss", "amber", "v_lock_cve", "VULNERABILITY", "CVE"),
    ("kubernetes", "green", "v_cloud_k8s", "KUBERNETES", "K8s"),
    ("k8s", "green", "v_cloud_k8s", "KUBERNETES", "K8s"),
    ("helm", "green", "v_cloud_k8s", "KUBERNETES", "HELM"),
    ("container", "green", "v_cloud_k8s", "CONTAINER", "CTR"),
    ("컨테이너", "green", "v_cloud_k8s", "CONTAINER", "CTR"),
    ("aws", "blue", "v_cloud_k8s", "AWS CLOUD", "AWS"),
    ("azure", "blue", "v_cloud_k8s", "AZURE CLOUD", "AZ"),
    ("gcp", "blue", "v_cloud_k8s", "GCP CLOUD", "GCP"),
    ("cloud", "blue", "v_cloud_k8s", "CLOUD", "CLD"),
    ("클라우드", "blue", "v_cloud_k8s", "CLOUD", "CLD"),
    ("prompt injection", "purple", "v_code_bars", "AI SECURITY", "LLM"),
    ("llm", "purple", "v_code_bars", "LLM", "LLM"),
    ("ai agent", "purple", "v_code_bars", "AI AGENT", "AGENT"),
    ("ai/ml", "purple", "v_code_bars", "AI ML", "AI"),
    ("ai ", "purple", "v_code_bars", "AI", "AI"),
    ("blockchain", "purple", "v_wallet_forensic", "BLOCKCHAIN", "CHAIN"),
    ("블록체인", "purple", "v_wallet_forensic", "BLOCKCHAIN", "CHAIN"),
    ("bitcoin", "amber", "v_price_chart", "CRYPTO MARKET", "BTC"),
    ("btc", "amber", "v_price_chart", "CRYPTO MARKET", "BTC"),
    ("ethereum", "amber", "v_price_chart", "CRYPTO MARKET", "ETH"),
    ("wallet", "green", "v_wallet_forensic", "WALLET", "WLT"),
    ("stablecoin", "amber", "v_senate_columns", "STABLECOIN", "REG"),
    ("regulation", "amber", "v_senate_columns", "REGULATION", "REG"),
    ("규제", "amber", "v_senate_columns", "REGULATION", "REG"),
    ("phishing", "red", "v_browser_cve", "PHISHING", "PSH"),
    ("피싱", "red", "v_browser_cve", "PHISHING", "PSH"),
    ("browser", "amber", "v_browser_cve", "BROWSER", "BRW"),
    ("router", "green", "v_router_mesh", "NETWORK", "NET"),
    ("botnet", "red", "v_router_mesh", "BOTNET", "BOT"),
    ("malware", "red", "v_network_nodes", "MALWARE", "MAL"),
    ("멀웨어", "red", "v_network_nodes", "MALWARE", "MAL"),
    ("trojan", "red", "v_network_nodes", "MALWARE", "TRJ"),
    ("breach", "red", "v_bar_graph", "DATA BREACH", "BRC"),
    ("유출", "red", "v_bar_graph", "DATA BREACH", "BRC"),
    ("zero trust", "green", "v_shield", "ZERO TRUST", "ZT"),
    ("제로트러스트", "green", "v_shield", "ZERO TRUST", "ZT"),
    ("iam", "amber", "v_lock_cve", "IAM", "IAM"),
    ("identity", "amber", "v_lock_cve", "IDENTITY", "ID"),
    ("patch", "green", "v_shield", "PATCH", "PT"),
    ("패치", "green", "v_shield", "PATCH", "PT"),
    ("devsecops", "green", "v_shield", "DEVSECOPS", "DSO"),
    ("devops", "blue", "v_code_bars", "DEVOPS", "DEV"),
    ("ci/cd", "amber", "v_code_bars", "CI/CD", "CICD"),
    ("finops", "amber", "v_bar_graph", "FINOPS", "FIN"),
    ("compliance", "blue", "v_shield", "COMPLIANCE", "CMP"),
]

# Default theme rotation when keyword routing returns fewer than 3 hits.
_L22_FALLBACK_ROTATION = [
    ("red", "v_network_nodes", "SECURITY", "SEC"),
    ("amber", "v_lock_cve", "VULNERABILITY", "VLN"),
    ("green", "v_shield", "DEFENSE", "DEF"),
]


def _is_digest_post(post_info: Dict) -> bool:
    """Return True when the post matches the weekly digest pattern."""
    title = str(post_info.get("title", ""))
    filename = str(post_info.get("filename", ""))
    if _DIGEST_TITLE_PATTERN.search(title) or _DIGEST_TITLE_PATTERN.search(filename):
        return True
    # Fallback: security/devsecops category with date-named digest pattern.
    category = str(post_info.get("category", "")).lower()
    if category in {"security", "devsecops"} and re.search(
        r"\d{4}-\d{2}-\d{2}-(?:Tech_Security_)?(?:Weekly|Daily).*Digest",
        filename,
        re.IGNORECASE,
    ):
        return True
    return False


def _extract_digest_topics(content: str, max_topics: int = 3) -> List[str]:
    """Extract up to ``max_topics`` topic strings from digest body H2/H3 sections.

    Skips boilerplate sections (e.g. 서론, 빠른 참조). Prefers numbered
    section subheadings (e.g. ``### 1.1 ...``) when present, falling back
    to the section title itself.
    """
    if not content:
        return []

    topics: List[str] = []
    seen: set = set()

    # Walk sections starting at "## " headings. For each non-boilerplate
    # section, collect either its first ### subheading or the H2 itself.
    section_pattern = re.compile(
        r"^##\s+([^\n]+)\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL
    )
    for match in section_pattern.finditer(content):
        h2_title = match.group(1).strip()
        h2_clean = re.sub(r"^\d+\.\s*", "", h2_title).strip()
        if any(bp in h2_clean for bp in _DIGEST_BOILERPLATE_HEADINGS):
            continue
        body = match.group(2)
        h3_match = re.search(r"^###\s+([^\n]+)", body, re.MULTILINE)
        if h3_match:
            topic = h3_match.group(1).strip()
            # Strip leading numbering like "1.1 " or "1.2 ".
            topic = re.sub(r"^\d+(?:\.\d+)?\s+", "", topic).strip()
        else:
            topic = h2_clean
        if topic and topic not in seen:
            seen.add(topic)
            topics.append(topic)
        if len(topics) >= max_topics:
            break

    return topics


def _route_l22_band(topic: str, used_themes: set) -> dict:
    """Pick a theme + visual + label from a topic string via keyword match."""
    lower = topic.lower()
    for keyword, theme, visual_name, label, badge_label in _L22_KEYWORD_ROUTES:
        if keyword in lower:
            return {
                "theme": theme,
                "visual_name": visual_name,
                "label": label,
                "badge_label": badge_label,
            }
    # Fallback: pick the first rotation entry whose theme is not yet used.
    for theme, visual_name, label, badge_label in _L22_FALLBACK_ROTATION:
        if theme not in used_themes:
            return {
                "theme": theme,
                "visual_name": visual_name,
                "label": label,
                "badge_label": badge_label,
            }
    # Absolute fallback.
    return {
        "theme": "blue",
        "visual_name": "v_code_bars",
        "label": "TECH",
        "badge_label": "INFO",
    }


def _trim_l22_text(text: str, limit: int) -> str:
    """Trim text to ``limit`` chars without breaking a trailing word too hard."""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _build_l22_band_cfg(topic: str, route: dict) -> dict:
    """Compose a single render_bands_svg band dict from a topic + route."""
    from scripts.lib import svg_l22_generator as _l22

    visual_fn = getattr(_l22, route["visual_name"])
    accent = _l22.THEMES[route["theme"]]["accent"]
    soft = _l22.THEMES[route["theme"]]["soft"]
    # All visuals share the same (cx=500, yc=105) origin; band() shifts the
    # group vertically per index, so the same yc works for every band.
    try:
        visual_svg = visual_fn(500, 105, accent, soft)
    except TypeError:
        # v_senate_columns has a different signature (no soft).
        visual_svg = visual_fn(500, 105, accent)

    headline = _trim_l22_text(topic, 36)
    metric = _trim_l22_text(topic, 48)
    return {
        "theme": route["theme"],
        "label": route["label"],
        "headline": headline,
        "metric": metric,
        "detail": _trim_l22_text(topic, 96),
        "badge_value": route["badge_label"][:4] or "INFO",
        "badge_label": route["badge_label"],
        "badge_sub": "highlighted",
        "visual": visual_svg,
    }


def generate_l22_digest_svg(post_info: Dict, output_path: Path) -> bool:
    """Generate an L22 stacked-bands SVG cover for a Weekly Digest post.

    Extracts up to three topic headings from the post body, routes each
    to a themed band via keyword heuristics, and writes the rendered
    SVG to ``output_path`` (with ``.svg`` suffix).
    """
    try:
        from scripts.lib import svg_l22_generator as _l22
    except Exception as exc:  # pragma: no cover - import guard
        log_message(f"❌ L22 generator import 실패: {exc}", "ERROR")
        return False

    try:
        content = post_info.get("content", "") or ""
        title = post_info.get("title", "") or ""
        filename = post_info.get("filename", "") or ""

        topics = _extract_digest_topics(content, max_topics=3)
        # Backfill from title tokens / tags if too few topics found.
        if len(topics) < 3:
            extra = _extract_visual_tokens(post_info, limit=6)
            for tok in extra:
                if tok and tok not in topics:
                    topics.append(tok)
                if len(topics) >= 3:
                    break
        # Final guard: pad with generic placeholders.
        while len(topics) < 3:
            topics.append("Security Update")

        bands_cfg = []
        used_themes: set = set()
        for topic in topics[:3]:
            route = _route_l22_band(topic, used_themes)
            used_themes.add(route["theme"])
            bands_cfg.append(_build_l22_band_cfg(topic, route))

        # Build URL from filename (YYYY-MM-DD-Slug.md -> /posts/YYYY/MM/DD/Slug/).
        url = "https://tech.2twodragon.com/"
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md", filename)
        if m:
            yyyy, mm, dd, slug = m.groups()
            slug_url = slug.replace("_", "-")
            url = f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug_url}/"

        sfx = "L22"
        aria = _trim_l22_text(title, 200) or "Weekly digest cover"
        svg_title = _trim_l22_text(title, 240) or "Weekly digest"

        svg = _l22.render_bands_svg(
            sfx=sfx,
            aria=_escape_svg_text(aria),
            title=_escape_svg_text(svg_title),
            url=url,
            bands_cfg=bands_cfg,
        )
        svg = validate_and_fix_svg(svg)

        output_svg = output_path.with_suffix(".svg")
        with open(output_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        log_message(f"✅ L22 Digest SVG 생성 완료: {output_svg.name}", "SUCCESS")
        return True

    except Exception as exc:
        log_message(f"❌ L22 Digest SVG 생성 실패: {exc}", "ERROR")
        return False


def process_post(
    post_file: Path,
    force: bool = False,
    optimize_only: bool = False,
    svg_only: bool = False,
) -> bool:
    """단일 포스팅 처리"""
    log_message(f"📄 포스팅 처리 시작: {post_file.name}")

    post_info = extract_post_info(post_file)
    if not post_info:
        log_message(f"❌ 포스팅 정보 추출 실패: {post_file.name}", "ERROR")
        return False

    image_path = post_info.get("image", "")
    has_image, image_file = check_image_exists(image_path)

    # --svg-only: regenerate ONLY the SVG cover. For weekly digest posts
    # this routes through the L22 generator; otherwise it falls back to
    # the standard SVG cover. PNG/WebP/AVIF steps are skipped entirely.
    if svg_only:
        if not image_path:
            post_stem = post_file.stem
            image_path = f"/assets/images/{post_stem}.svg"
        output_path = IMAGES_DIR / Path(image_path).name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if _is_digest_post(post_info):
            log_message("🎨 L22 Digest SVG (--svg-only) 생성 시도...", "INFO")
            ok = generate_l22_digest_svg(post_info, output_path)
        else:
            log_message("🎨 SVG 폴백 (--svg-only) 생성 시도...", "INFO")
            ok = generate_fallback_svg(post_info, output_path)
        return ok

    if optimize_only:
        if has_image and image_file:
            log_message(
                f"✨ 최적화 모드: 기존 이미지 최적화 중... {image_file.name}", "INFO"
            )
            optimize_image(image_file)
            return True
        else:
            log_message(
                f"⚠️ 최적화 모드: 이미지를 찾을 수 없어 건너뜁니다. {image_path}",
                "WARNING",
            )
            return False

    if has_image and not force:
        if image_file:
            log_message(f"✅ 이미지가 이미 존재합니다: {image_file.name}", "SUCCESS")
        return True

    if not image_path:
        post_stem = post_file.stem
        image_filename = f"{post_stem}.svg"
        image_path = f"/assets/images/{image_filename}"
        log_message(f"💡 이미지 경로 생성: {image_path}", "INFO")

    output_path = IMAGES_DIR / Path(image_path).name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = generate_image_prompt(post_info)
    log_message("📝 이미지 생성 프롬프트 생성 완료", "SUCCESS")

    image_generated = False
    if GEMINI_API_KEY:
        image_generated = generate_image_with_gemini(prompt, output_path)

    if not image_generated:
        # Weekly digest posts route through the L22 stacked-bands generator
        # first (content-driven covers), then fall through to the legacy
        # threat-signal-map digest SVG, then to the generic fallback.
        if _is_digest_post(post_info):
            log_message("🎨 L22 Digest SVG 이미지 생성 시도...", "INFO")
            image_generated = generate_l22_digest_svg(post_info, output_path)
            if not image_generated:
                log_message("🎨 Digest SVG 이미지 생성 시도...", "INFO")
                image_generated = generate_digest_svg(post_info, output_path)
        if not image_generated:
            log_message("🎨 SVG 폴백 이미지 생성 시도...", "INFO")
            image_generated = generate_fallback_svg(post_info, output_path)
        if not image_generated:
            save_prompt_file(prompt, output_path)

    png_path = output_path.with_suffix(".png")
    if output_path.suffix == ".svg":
        log_message("💡 SVG를 PNG로 변환하려면 다음 명령어를 사용하세요:", "INFO")
        log_message("   python3 scripts/generate_og_image.py", "INFO")

    log_message(f"✅ 포스팅 처리 완료: {post_file.name}", "SUCCESS")
    return True


def main():
    """메인 함수"""
    if not GEMINI_API_KEY:
        log_message("GEMINI_API_KEY not set - API features disabled", "WARNING")

    import argparse

    parser = argparse.ArgumentParser(
        description="포스팅 이미지 자동 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 최근 포스팅 이미지 생성
  python3 scripts/generate_post_images.py --recent 1
  
  # 특정 포스팅 이미지 생성
  python3 scripts/generate_post_images.py _posts/2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.md
  
  # 모든 포스팅 이미지 생성
  python3 scripts/generate_post_images.py --all
  
  # 이미지가 있어도 강제로 재생성
  python3 scripts/generate_post_images.py --recent 1 --force
        """,
    )

    parser.add_argument("post_file", nargs="?", help="처리할 포스팅 파일 (선택사항)")
    parser.add_argument("--all", action="store_true", help="모든 포스팅 처리")
    parser.add_argument(
        "--recent", type=int, default=1, help="최근 N개 포스팅만 처리 (기본값: 1)"
    )
    parser.add_argument(
        "--force", action="store_true", help="이미지가 있어도 강제로 재생성"
    )
    parser.add_argument(
        "--missing", action="store_true", help="이미지가 없는 포스팅만 처리"
    )
    parser.add_argument(
        "--optimize-only",
        action="store_true",
        help="이미지 재생성 없이 기존 이미지를 최적화",
    )
    parser.add_argument(
        "--webp-only",
        action="store_true",
        help="기존 PNG에서 WebP만 생성 (SVG/PNG 재생성 없음)",
    )
    parser.add_argument(
        "--avif-only",
        action="store_true",
        help="기존 PNG에서 AVIF만 생성 (SVG/PNG 재생성 없음)",
    )
    parser.add_argument(
        "--use-pro-image",
        action="store_true",
        help="Gemini 3 Pro Image 모델 사용 강제",
    )
    parser.add_argument(
        "--use-gpt54-prompt",
        action="store_true",
        help="GPT-5.4 기반 프롬프트 보강 활성화",
    )
    parser.add_argument(
        "--no-gpt54-prompt",
        action="store_true",
        help="GPT-5.4 프롬프트 보강 비활성화",
    )
    parser.add_argument(
        "--regenerate-section-banners",
        action="store_true",
        help="공통 섹션 배너 SVG를 재생성",
    )
    parser.add_argument(
        "--svg-only",
        action="store_true",
        help="SVG 커버만 재생성 (PNG/WebP/AVIF 변환 등 비-SVG 단계는 건너뜀)",
    )

    args = parser.parse_args()

    global USE_PRO_MODEL, USE_GPT54_PROMPT_ENHANCER
    if args.use_pro_image:
        USE_PRO_MODEL = True
    if args.use_gpt54_prompt:
        USE_GPT54_PROMPT_ENHANCER = True
    if args.no_gpt54_prompt:
        USE_GPT54_PROMPT_ENHANCER = False

    log_message(
        f"🧠 Prompt enhancer: {'GPT-5.4 ON' if USE_GPT54_PROMPT_ENHANCER else 'OFF'}",
        "INFO",
    )
    log_message(
        f"🎨 Image model: {'Gemini 3 Pro Image' if USE_PRO_MODEL else 'Gemini 2.5 Flash Image'}",
        "INFO",
    )

    if args.regenerate_section_banners:
        regenerate_section_banners()
        sys.exit(0)

    # Gemini API 키 확인
    if not GEMINI_API_KEY:
        log_message("⚠️ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.", "WARNING")
        log_message(
            "💡 프롬프트만 생성합니다. 이미지 생성은 수동으로 진행해야 합니다.", "INFO"
        )
        log_message("💡 Gemini API 키 설정: export GEMINI_API_KEY='your-key'", "INFO")

    # 포스팅 파일 목록
    posts = []

    if args.post_file:
        # 특정 파일 처리
        post_path = Path(args.post_file)
        if not post_path.is_absolute():
            post_path = PROJECT_ROOT / post_path

        if not post_path.exists():
            log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
            sys.exit(1)

        posts = [post_path]
    elif args.all:
        # 모든 포스팅 처리
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
    else:
        # 최근 N개 포스팅 처리
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )[: args.recent]

    # --webp-only / --avif-only: 기존 PNG에서 변환만 수행
    if getattr(args, "webp_only", False) or getattr(args, "avif_only", False):
        from pathlib import Path as P

        pngs = sorted(IMAGES_DIR.glob("*_og.png"))
        converted = 0
        for png in pngs:
            if args.webp_only:
                webp = png.with_suffix(".webp")
                if not webp.exists() and CWEBP_PATH:
                    try:
                        subprocess.run(
                            [
                                CWEBP_PATH,
                                "-q",
                                "80",
                                "-quiet",
                                str(png),
                                "-o",
                                str(webp),
                            ],
                            capture_output=True,
                            timeout=30,
                        )
                        if webp.exists():
                            converted += 1
                    except Exception:
                        pass
            if args.avif_only:
                avif = png.with_suffix(".avif")
                if not avif.exists() and AVIFENC_PATH:
                    try:
                        subprocess.run(
                            [AVIFENC_PATH, "-s", "6", "-q", "40", str(png), str(avif)],
                            capture_output=True,
                            timeout=60,
                        )
                        if avif.exists():
                            converted += 1
                    except Exception:
                        pass
        log_message(f"✅ {converted}개 파일 변환 완료", "SUCCESS")
        sys.exit(0)

    if not posts:
        log_message("❌ 처리할 포스팅이 없습니다.", "ERROR")
        sys.exit(1)

    log_message(f"📊 {len(posts)}개 포스팅 처리 시작\n")

    # 각 포스팅 처리
    success_count = 0
    for post_file in posts:
        try:
            # 이미지가 없는 포스팅만 처리하는 경우
            if args.missing and not args.optimize_only:
                post_info = extract_post_info(post_file)
                has_image, _ = check_image_exists(post_info.get("image", ""))
                if has_image:
                    continue

            if process_post(
                post_file,
                force=args.force,
                optimize_only=args.optimize_only,
                svg_only=args.svg_only,
            ):
                success_count += 1
        except Exception as e:
            log_message(f"❌ 포스팅 처리 실패: {post_file.name} - {str(e)}", "ERROR")

        print()  # 빈 줄 추가

    # 요약
    log_message("=" * 80)
    log_message(f"📊 처리 완료: {success_count}/{len(posts)}개 성공", "SUCCESS")
    log_message("=" * 80)

    if not GEMINI_API_KEY:
        log_message("\n💡 다음 단계:", "INFO")
        log_message("1. 생성된 프롬프트 파일 확인", "INFO")
        log_message(
            "2. DALL-E, Midjourney, 또는 Stable Diffusion으로 이미지 생성", "INFO"
        )
        log_message("3. 생성된 이미지를 assets/images/ 디렉토리에 저장", "INFO")


if __name__ == "__main__":
    main()
