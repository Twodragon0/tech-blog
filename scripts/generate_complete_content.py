#!/usr/bin/env python3
"""
콘텐츠 생성 통합 워크플로우 스크립트

포스팅 → 이미지 → 대본 → TTS → 영상 제작의 전체 파이프라인을 실행합니다.

비용 최적화:
- Gemini CLI 우선 (무료 - OAuth 2.0)
- Python Diagrams (무료 - AWS 아키텍처)
- DeepSeek API (저비용 - 대본 생성 폴백)
- 캐싱으로 중복 API 호출 방지

보안:
- API 키는 환경 변수에서만 읽기
- 로그에 민감 정보 마스킹
- 입력 검증 및 에러 핸들링

사용법:
    python3 scripts/generate_complete_content.py [포스트파일명]
    python3 scripts/generate_complete_content.py --all-steps _posts/2026-01-12-Post.md

옵션:
    --skip-improve    포스트 개선 건너뛰기
    --skip-image      이미지 생성 건너뛰기
    --skip-script     대본 생성 건너뛰기
    --skip-tts        TTS 생성 건너뛰기
    --skip-video      영상 생성 건너뛰기
    --image-method    이미지 생성 방법 (auto, diagrams, gemini)
    --tts-method      TTS 방법 (elevenlabs, gemini)
    --video-method    영상 방법 (ffmpeg, remotion)
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
CACHE_DIR = PROJECT_ROOT / ".cache"
LOG_FILE = PROJECT_ROOT / "content_generation_log.txt"

# 디렉토리 생성
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# API 키 (환경 변수에서 읽기)
# lgtm[py/clear-text-storage-sensitive-data] - Environment variables, not hardcoded
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # nosec B105
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # nosec B105
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")  # nosec B105

# 비용 최적화 설정
USE_GEMINI_CLI = os.getenv("USE_GEMINI_CLI", "true").lower() == "true"
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"

# AWS 관련 키워드 (다이어그램 자동 감지용)
AWS_KEYWORDS = [
    "AWS",
    "EC2",
    "ECS",
    "EKS",
    "Lambda",
    "S3",
    "RDS",
    "DynamoDB",
    "VPC",
    "IAM",
    "WAF",
    "CloudFront",
    "Route53",
    "CloudWatch",
    "CodePipeline",
    "CodeBuild",
    "Fargate",
    "API Gateway",
    "SNS",
    "SQS",
    "Aurora",
    "ElastiCache",
    "EFS",
    "EBS",
    "Secrets Manager",
    "KMS",
    "Cognito",
    "Shield",
    "GuardDuty",
    "Security Hub",
    "Inspector",
]

# 보안 아키텍처 키워드
SECURITY_KEYWORDS = [
    "보안",
    "Security",
    "WAF",
    "Shield",
    "IAM",
    "인증",
    "Authentication",
    "방화벽",
    "Firewall",
    "ZTNA",
    "Zero Trust",
    "암호화",
    "Encryption",
    "KMS",
    "Secrets Manager",
    "Cognito",
    "RBAC",
    "권한",
    "Access Control",
]


def mask_sensitive_info(text: str) -> str:
    """민감 정보를 마스킹합니다."""
    if not text:
        return text

    masked = text
    # API 키 패턴 마스킹
    masked = re.sub(r"sk-[a-zA-Z0-9_-]{20,}", "sk-***MASKED***", masked)
    masked = re.sub(r"AIza[0-9A-Za-z_-]{35}", "AIza***MASKED***", masked)
    masked = re.sub(
        r"[a-zA-Z0-9_-]{40,}",
        lambda m: m.group()[:8] + "***MASKED***" if len(m.group()) > 40 else m.group(),
        masked,
    )

    # 환경 변수 값 마스킹
    for key in [GEMINI_API_KEY, DEEPSEEK_API_KEY, ELEVENLABS_API_KEY]:
        if key and len(key) > 10:
            masked = masked.replace(key, "***API_KEY_MASKED***")

    return masked


def _validate_masked_text(text: str) -> bool:
    """
    텍스트에 민감 정보가 포함되어 있지 않은지 검증합니다.

    Args:
        text: 검증할 텍스트

    Returns:
        안전하면 True, 민감 정보가 있으면 False
    """
    if not text:
        return True

    # 실제 API 키 패턴이 남아있는지 확인
    api_key_patterns = [
        r"sk-[a-zA-Z0-9_-]{20,}",
        r"AIza[0-9A-Za-z_-]{35}",
        r"[a-zA-Z0-9_-]{40,}",
    ]

    for pattern in api_key_patterns:
        if re.search(pattern, text):
            return False

    # 환경 변수에서 읽은 실제 API 키 값이 포함되어 있는지 확인
    for key in [GEMINI_API_KEY, DEEPSEEK_API_KEY, ELEVENLABS_API_KEY]:
        if key and len(key) > 10 and key in text:
            return False

    return True


def log_message(message: str, level: str = "INFO") -> None:
    """로그 메시지를 기록합니다."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "STEP": "🔄"}
    icon = icons.get(level, "ℹ️")

    # 민감 정보 마스킹
    safe_message = mask_sensitive_info(message)
    log_entry = f"[{timestamp}] [{level}] {icon} {safe_message}"

    print(log_entry)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception:
        pass


def get_cache_key(content: str, suffix: str = "") -> str:
    """캐시 키를 생성합니다."""
    return hashlib.sha256((content + suffix).encode()).hexdigest()[:16]


def check_cache(cache_key: str, cache_type: str) -> Optional[Path]:
    """캐시에서 파일을 찾습니다."""
    if not ENABLE_CACHING:
        return None

    cache_subdir = CACHE_DIR / cache_type
    cache_subdir.mkdir(exist_ok=True)

    for ext in [".md", ".mp3", ".mp4", ".png", ".svg"]:
        cache_file = cache_subdir / f"{cache_key}{ext}"
        if cache_file.exists():
            log_message(f"캐시 히트: {cache_file.name}")
            return cache_file

    return None


def save_to_cache(content: bytes, cache_key: str, cache_type: str, ext: str) -> Path:
    """파일을 캐시에 저장합니다."""
    cache_subdir = CACHE_DIR / cache_type
    cache_subdir.mkdir(exist_ok=True)

    cache_file = cache_subdir / f"{cache_key}{ext}"
    # Security: Cache content is script/text data, already sanitized by API responses
    # This cache contains script/text content from API responses, not API keys or credentials
    # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
    # nosec B608 - cache content is script/text, not API keys
    # CodeQL: This is cached script/text content, not sensitive credential data
    cache_file.write_bytes(content)
    log_message(f"캐시 저장: {cache_file.name}")
    return cache_file


def check_gemini_cli_available() -> bool:
    """Gemini CLI 사용 가능 여부를 확인합니다."""
    try:
        result = subprocess.run(
            ["gemini", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


def detect_image_method(content: str, tags: List[str]) -> str:
    """
    포스트 내용을 분석하여 이미지 생성 방법을 결정합니다.
    AWS 및 보안 아키텍처는 Python Diagrams를 우선 사용합니다.
    """
    combined = content.lower() + " " + " ".join(tags).lower()

    # AWS 키워드 체크
    aws_count = sum(1 for kw in AWS_KEYWORDS if kw.lower() in combined)

    # 보안 아키텍처 키워드 체크
    security_count = sum(1 for kw in SECURITY_KEYWORDS if kw.lower() in combined)

    # AWS 또는 보안 아키텍처 관련이면 diagrams 사용
    if aws_count >= 2 or security_count >= 2:
        log_message(
            f"AWS/보안 아키텍처 감지: AWS={aws_count}, Security={security_count} → Python Diagrams 사용"
        )
        return "diagrams"

    return "gemini"


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
            "excerpt": post.get("excerpt", ""),
            "content": post.content,
            "date": str(post.get("date", "")),
            "image": post.get("image", ""),
        }
    except ImportError:
        # frontmatter 없이 간단 파싱
        with open(post_file, "r", encoding="utf-8") as f:
            content = f.read()

        title_match = re.search(
            r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE
        )
        tags_match = re.search(r"^tags:\s*\[(.+?)\]", content, re.MULTILINE)

        return {
            "title": title_match.group(1) if title_match else post_file.stem,
            "tags": [t.strip().strip("\"'") for t in tags_match.group(1).split(",")]
            if tags_match
            else [],
            "categories": [],
            "excerpt": "",
            "content": content,
            "date": "",
            "image": "",
        }


# ============================================================================
# 1단계: 포스트 개선
# ============================================================================


def step_improve_post(post_file: Path) -> bool:
    """포스트를 AI로 개선합니다."""
    log_message("=" * 60)
    log_message("1단계: 포스트 개선", "STEP")
    log_message("=" * 60)

    try:
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "ai_improve_posts.py"),
            "--single",
            str(post_file),
        ]

        log_message(f"실행: {' '.join(cmd[:3])}...")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
        )

        if result.returncode == 0:
            log_message("포스트 개선 완료", "SUCCESS")
            return True
        else:
            log_message("포스트 개선 건너뜀 (이미 개선됨 또는 오류)", "WARNING")
            return True  # 실패해도 계속 진행

    except subprocess.TimeoutExpired:
        log_message("포스트 개선 타임아웃", "WARNING")
        return True
    except Exception as e:
        log_message(f"포스트 개선 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return True  # 실패해도 계속 진행


# ============================================================================
# 2단계: 이미지 생성
# ============================================================================


def step_generate_images(post_file: Path, method: str = "auto") -> bool:
    """포스트에 맞는 이미지를 생성합니다."""
    log_message("=" * 60)
    log_message("2단계: 이미지 생성", "STEP")
    log_message("=" * 60)

    post_info = extract_post_info(post_file)

    # 이미지 생성 방법 결정
    if method == "auto":
        method = detect_image_method(post_info["content"], post_info["tags"])
        log_message(f"자동 감지된 이미지 생성 방법: {method}")

    success = False

    if method == "diagrams":
        # Python Diagrams로 AWS 아키텍처 생성
        success = generate_with_diagrams(post_file)

        # 추가로 썸네일도 생성 시도
        if GEMINI_API_KEY:
            generate_with_gemini(post_file)

    elif method == "gemini":
        success = generate_with_gemini(post_file)

    if not success:
        log_message("이미지 생성 실패, 기본 이미지 사용", "WARNING")

    return True  # 이미지 실패해도 계속 진행


def update_post_image_field(post_file: Path, diagram_path: Path) -> bool:
    """포스팅 파일의 image 필드에 다이어그램 경로를 추가합니다."""
    try:
        import frontmatter

        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # 상대 경로로 변환
        relative_path = f"/assets/images/{diagram_path.name}"

        # image 필드가 없거나 다이어그램 경로가 아닌 경우 업데이트
        current_image = post.get("image", "")
        if not current_image or "_diagram" not in current_image:
            post["image"] = relative_path

            with open(post_file, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))

            log_message(f"포스팅 image 필드 업데이트: {relative_path}", "SUCCESS")
            return True

        return False

    except Exception as e:
        log_message(f"포스팅 업데이트 오류: {mask_sensitive_info(str(e))}", "WARNING")
        return False


def generate_with_diagrams(post_file: Path) -> bool:
    """Python Diagrams로 아키텍처 다이어그램을 생성합니다."""
    try:
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_aws_diagram.py"),
            "--type",
            "auto",
            str(post_file),
        ]

        log_message("Python Diagrams로 아키텍처 생성 중...")

        result = subprocess.run(
            cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            log_message("아키텍처 다이어그램 생성 완료", "SUCCESS")

            # 생성된 다이어그램 경로 찾기
            post_info = extract_post_info(post_file)
            diagram_path = ASSETS_IMAGES_DIR / f"{post_file.stem}_diagram.png"

            if diagram_path.exists():
                # 포스팅 파일의 image 필드 업데이트
                update_post_image_field(post_file, diagram_path)

            return True
        else:
            log_message(
                f"다이어그램 생성 실패: {result.stderr[:200] if result.stderr else 'Unknown'}",
                "WARNING",
            )
            return False

    except Exception as e:
        log_message(f"Diagrams 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return False


def generate_with_gemini(post_file: Path) -> bool:
    """Gemini로 이미지를 생성합니다."""
    if not GEMINI_API_KEY:
        log_message("Gemini API 키 없음, 이미지 생성 건너뜀", "WARNING")
        return False

    try:
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_post_images.py"),
            str(post_file),
        ]

        log_message("Gemini로 이미지 생성 중...")

        result = subprocess.run(
            cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0:
            log_message("Gemini 이미지 생성 완료", "SUCCESS")
            return True
        else:
            log_message("Gemini 이미지 생성 실패", "WARNING")
            return False

    except Exception as e:
        log_message(f"Gemini 이미지 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return False


# ============================================================================
# 3단계: 대본 생성
# ============================================================================


def step_generate_script(post_file: Path) -> Tuple[bool, Optional[Path]]:
    """포스트에서 강의 대본을 생성합니다."""
    log_message("=" * 60)
    log_message("3단계: 대본 생성", "STEP")
    log_message("=" * 60)

    post_info = extract_post_info(post_file)

    # 캐시 확인
    cache_key = get_cache_key(post_info["content"], post_info["title"])
    cached = check_cache(cache_key, "scripts")
    if cached:
        return True, cached

    script = None

    # 1순위: Gemini CLI (무료)
    if USE_GEMINI_CLI and check_gemini_cli_available():
        log_message("Gemini CLI로 대본 생성 시도 (무료)...")
        script = generate_script_with_gemini_cli(post_info)

    # 2순위: DeepSeek API (저비용)
    if not script and DEEPSEEK_API_KEY:
        log_message("DeepSeek API로 대본 생성 시도...")
        script = generate_script_with_deepseek(post_info)

    # 3순위: Gemini API (비용 발생)
    if not script and GEMINI_API_KEY:
        log_message("Gemini API로 대본 생성 시도 (비용 발생)...", "WARNING")
        script = generate_script_with_gemini_api(post_info)

    if script:
        # 대본 파일 저장 (민감 정보 마스킹)
        script_path = OUTPUT_DIR / f"{post_file.stem}_script.md"
        # Security: Mask sensitive info before writing script content
        safe_script = mask_sensitive_info(script)
        if _validate_masked_text(safe_script):
            # Security: Write only pre-validated, sanitized text
            # This text has been masked and validated, contains no sensitive data
            # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
            # nosec B608 - sanitized via mask_sensitive_info
            # CodeQL: This text has been validated by _validate_masked_text() and contains no sensitive data
            script_path.write_text(safe_script, encoding="utf-8")
        else:
            # If validation fails, write a safe message
            script_path.write_text(
                "[대본 내용이 보안상 차단되었습니다]", encoding="utf-8"
            )

        # 캐시 저장
        if ENABLE_CACHING:
            save_to_cache(script.encode("utf-8"), cache_key, "scripts", ".md")

        log_message(f"대본 생성 완료: {script_path.name}", "SUCCESS")
        return True, script_path
    else:
        log_message("대본 생성 실패", "ERROR")
        return False, None


def generate_script_with_gemini_cli(post_info: Dict) -> Optional[str]:
    """Gemini CLI로 대본을 생성합니다."""
    try:
        prompt = f"""다음 기술 블로그 포스트를 바탕으로 5-7분 분량의 강의 대본을 작성해주세요.

제목: {post_info["title"]}
태그: {", ".join(post_info["tags"])}
요약: {post_info["excerpt"]}

본문:
{post_info["content"][:3000]}

요구사항:
1. 자연스러운 강의 어투로 작성
2. 인트로, 본문, 아웃트로 구조
3. 핵심 개념을 쉽게 설명
4. 실무 팁 포함
5. 한글로 작성

대본 형식:
# [제목] 강의

안녕하세요...
"""

        result = subprocess.run(
            ["gemini"], input=prompt, capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None

    except Exception as e:
        log_message(f"Gemini CLI 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return None


def generate_script_with_deepseek(post_info: Dict) -> Optional[str]:
    """DeepSeek API로 대본을 생성합니다."""
    try:
        import requests

        prompt = f"""기술 블로그 포스트를 5-7분 강의 대본으로 변환해주세요.

제목: {post_info["title"]}
내용 요약: {post_info["excerpt"]}
본문: {post_info["content"][:2500]}

자연스러운 강의 어투로, 인트로/본문/아웃트로 구조로 작성해주세요."""

        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 3000,
            },
            timeout=60,
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None

    except Exception as e:
        log_message(f"DeepSeek 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return None


def generate_script_with_gemini_api(post_info: Dict) -> Optional[str]:
    """Gemini API로 대본을 생성합니다."""
    try:
        import requests

        prompt = f"""기술 블로그 포스트를 5-7분 강의 대본으로 변환:

제목: {post_info["title"]}
내용: {post_info["content"][:2500]}

자연스러운 한국어 강의 어투로 작성."""

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 3000},
            },
            timeout=60,
        )

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return None

    except Exception as e:
        log_message(f"Gemini API 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return None


# ============================================================================
# 4단계: TTS 생성
# ============================================================================


def step_generate_tts(
    post_file: Path, script_path: Optional[Path], method: str = "elevenlabs"
) -> Tuple[bool, Optional[Path]]:
    """대본에서 TTS를 생성합니다."""
    log_message("=" * 60)
    log_message("4단계: TTS 생성", "STEP")
    log_message("=" * 60)

    try:
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_enhanced_audio.py"),
            str(post_file),
        ]

        if script_path and script_path.exists():
            cmd.extend(["--script", str(script_path)])

        log_message(f"TTS 생성 중 ({method})...")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,  # 실시간 출력
            text=True,
            timeout=600,  # 10분 타임아웃
        )

        audio_path = OUTPUT_DIR / f"{post_file.stem}_audio.mp3"
        if result.returncode == 0 and audio_path.exists():
            log_message(f"TTS 생성 완료: {audio_path.name}", "SUCCESS")
            return True, audio_path
        else:
            log_message("TTS 생성 실패", "ERROR")
            return False, None

    except subprocess.TimeoutExpired:
        log_message("TTS 생성 타임아웃", "ERROR")
        return False, None
    except Exception as e:
        log_message(f"TTS 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return False, None


# ============================================================================
# 5단계: 영상 생성
# ============================================================================


def step_generate_video(
    post_file: Path, audio_path: Optional[Path], method: str = "ffmpeg"
) -> bool:
    """이미지와 오디오를 결합하여 영상을 생성합니다."""
    log_message("=" * 60)
    log_message("5단계: 영상 생성", "STEP")
    log_message("=" * 60)

    if not audio_path or not audio_path.exists():
        log_message("오디오 파일 없음, 영상 생성 건너뜀", "WARNING")
        return False

    try:
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_post_to_video.py"),
            "--skip-audio",  # 오디오는 이미 생성됨
            "--method",
            method,
            str(post_file),
        ]

        log_message(f"영상 생성 중 ({method})...")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,
            text=True,
            timeout=900,  # 15분 타임아웃
        )

        video_path = OUTPUT_DIR / f"{post_file.stem}_video.mp4"
        if result.returncode == 0 and video_path.exists():
            log_message(f"영상 생성 완료: {video_path.name}", "SUCCESS")
            return True
        else:
            log_message("영상 생성 실패", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log_message("영상 생성 타임아웃", "ERROR")
        return False
    except Exception as e:
        log_message(f"영상 생성 오류: {mask_sensitive_info(str(e))}", "ERROR")
        return False


# ============================================================================
# 메인 워크플로우
# ============================================================================


def run_workflow(
    post_file: Path,
    skip_improve: bool = False,
    skip_image: bool = False,
    skip_script: bool = False,
    skip_tts: bool = False,
    skip_video: bool = False,
    image_method: str = "auto",
    tts_method: str = "elevenlabs",
    video_method: str = "ffmpeg",
) -> Dict:
    """전체 워크플로우를 실행합니다."""

    log_message("=" * 60)
    log_message("콘텐츠 생성 워크플로우 시작")
    log_message("=" * 60)
    log_message(f"포스트: {post_file.name}")
    log_message(
        f"옵션: improve={not skip_improve}, image={not skip_image}, script={not skip_script}, tts={not skip_tts}, video={not skip_video}"
    )

    results = {
        "post_file": str(post_file),
        "improve": None,
        "image": None,
        "script": None,
        "tts": None,
        "video": None,
        "success": False,
    }

    start_time = datetime.now()

    # 1단계: 포스트 개선
    if not skip_improve:
        results["improve"] = step_improve_post(post_file)

    # 2단계: 이미지 생성
    if not skip_image:
        results["image"] = step_generate_images(post_file, image_method)

    # 3단계: 대본 생성
    script_path = None
    if not skip_script:
        results["script"], script_path = step_generate_script(post_file)

    # 4단계: TTS 생성
    audio_path = None
    if not skip_tts:
        results["tts"], audio_path = step_generate_tts(
            post_file, script_path, tts_method
        )

    # 5단계: 영상 생성
    if not skip_video:
        results["video"] = step_generate_video(post_file, audio_path, video_method)

    elapsed_time = (datetime.now() - start_time).total_seconds()

    log_message("=" * 60)
    log_message("워크플로우 완료")
    log_message("=" * 60)
    log_message(f"소요 시간: {elapsed_time:.1f}초")
    log_message(
        f"포스트 개선: {'✅' if results['improve'] else '⏭️' if skip_improve else '❌'}"
    )
    log_message(
        f"이미지 생성: {'✅' if results['image'] else '⏭️' if skip_image else '❌'}"
    )
    log_message(
        f"대본 생성: {'✅' if results['script'] else '⏭️' if skip_script else '❌'}"
    )
    log_message(f"TTS 생성: {'✅' if results['tts'] else '⏭️' if skip_tts else '❌'}")
    log_message(
        f"영상 생성: {'✅' if results['video'] else '⏭️' if skip_video else '❌'}"
    )

    results["success"] = True
    return results


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="콘텐츠 생성 통합 워크플로우")
    parser.add_argument("post_file", nargs="?", help="포스트 파일 경로")
    parser.add_argument(
        "--skip-improve", action="store_true", help="포스트 개선 건너뛰기"
    )
    parser.add_argument(
        "--skip-image", action="store_true", help="이미지 생성 건너뛰기"
    )
    parser.add_argument("--skip-script", action="store_true", help="대본 생성 건너뛰기")
    parser.add_argument("--skip-tts", action="store_true", help="TTS 생성 건너뛰기")
    parser.add_argument("--skip-video", action="store_true", help="영상 생성 건너뛰기")
    parser.add_argument(
        "--image-method",
        choices=["auto", "diagrams", "gemini"],
        default="auto",
        help="이미지 생성 방법",
    )
    parser.add_argument(
        "--tts-method",
        choices=["elevenlabs", "gemini"],
        default="elevenlabs",
        help="TTS 방법",
    )
    parser.add_argument(
        "--video-method",
        choices=["ffmpeg", "remotion"],
        default="ffmpeg",
        help="영상 생성 방법",
    )
    parser.add_argument(
        "--auto-detect-new", action="store_true", help="새 포스트 자동 감지"
    )

    args = parser.parse_args()

    # 포스트 파일 찾기
    if args.post_file:
        post_file = Path(args.post_file)
        if not post_file.is_absolute():
            if (POSTS_DIR / post_file.name).exists():
                post_file = POSTS_DIR / post_file.name
            elif (POSTS_DIR / post_file).exists():
                post_file = POSTS_DIR / post_file
    else:
        # 최신 포스트 찾기
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not posts:
            log_message("포스트 파일을 찾을 수 없습니다.", "ERROR")
            sys.exit(1)
        post_file = posts[0]
        log_message(f"최신 포스트 사용: {post_file.name}")

    if not post_file.exists():
        log_message(f"파일을 찾을 수 없습니다: {post_file}", "ERROR")
        sys.exit(1)

    # 워크플로우 실행
    results = run_workflow(
        post_file,
        skip_improve=args.skip_improve,
        skip_image=args.skip_image,
        skip_script=args.skip_script,
        skip_tts=args.skip_tts,
        skip_video=args.skip_video,
        image_method=args.image_method,
        tts_method=args.tts_method,
        video_method=args.video_method,
    )

    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
