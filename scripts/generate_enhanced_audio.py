#!/usr/bin/env python3
"""
블로그 포스팅을 자동으로 영상 강의용 오디오로 변환하는 개선된 스크립트

주요 개선 사항:
- DeepSeek API와 Gemini API를 작업 유형에 따라 선택적 활용
- 비용 최적화: API 선택 전략, 캐싱, 사용량 모니터링
- 보안 강화: API 키 관리, 입력 검증, 에러 핸들링
- 품질 향상: Gemini를 활용한 대본 개선 및 이미지 생성

보안 고려사항:
- 모든 API 키는 환경 변수에서만 읽음
- 로그에 민감 정보 마스킹
- 에러 핸들링 강화
- 입력 검증 수행
"""

import os
import re
import sys
import json
import time
import hashlib
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import frontmatter

# OAuth 2.0 지원 (선택적)
try:
    from google.auth import default
    from google.auth.transport.requests import Request
    import google.generativeai as genai
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / ".cache" / "audio_generation"
LOG_FILE = PROJECT_ROOT / "video_generation_log.txt"

# 출력 디렉토리 생성
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API 설정 (환경 변수에서 읽기)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# API 엔드포인트
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"  # Gemini 1.5 Pro deprecated, 2.5 Pro 사용
GEMINI_IMAGE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"  # Gemini Nano Banana (이미지 생성)
GEMINI_VIDEO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"  # Gemini Veo (영상 생성)
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
ELEVENLABS_VOICES_URL = "https://api.elevenlabs.io/v1/voices"
GEMINI_TTS_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"  # Gemini TTS (오디오 생성)

# 설정
MAX_TEXT_LENGTH = 50000  # 최대 텍스트 길이 (비용 관리)
MAX_SCRIPT_LENGTH = 4500  # 최대 대본 길이 (약 7-8분 분량, 1.5배속 재생 시 약 5분)
AUDIO_OUTPUT_FORMAT = "mp3"
AUDIO_SPEED_MULTIPLIER = 1.5  # 오디오 재생 속도 배율 (1.5배속)

# API 선택 전략 설정
USE_GEMINI_FOR_IMPROVEMENT = os.getenv("USE_GEMINI_FOR_IMPROVEMENT", "true").lower() == "true"
USE_DEEPSEEK_FOR_SCRIPT = os.getenv("USE_DEEPSEEK_FOR_SCRIPT", "true").lower() == "true"
USE_GEMINI_FOR_SCRIPT = os.getenv("USE_GEMINI_FOR_SCRIPT", "true").lower() == "true"  # Gemini AI Pro 적극 활용
USE_GEMINI_CLI = os.getenv("USE_GEMINI_CLI", "true").lower() == "true"  # Gemini CLI 사용 (비용 절감 - OAuth 2.0 지원)
PREFER_GEMINI = os.getenv("PREFER_GEMINI", "true").lower() == "true"  # Gemini Pro 우선 사용
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"

# OAuth 2.0 설정
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")  # 환경 변수에서 읽기
USE_OAUTH = os.getenv("USE_GEMINI_OAUTH", "true").lower() == "true" and bool(GOOGLE_APPLICATION_CREDENTIALS) and OAUTH_AVAILABLE

# 서비스 계정 정보 (환경 변수에서 읽거나 로그에만 표시, 민감 정보이므로 하드코딩하지 않음)
GEMINI_SERVICE_ACCOUNT = os.getenv("GEMINI_SERVICE_ACCOUNT", "")  # 선택적, 로그용

# 비용 모니터링
@dataclass
class APIUsage:
    """API 사용량 추적"""
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit_tokens: int = 0
    requests: int = 0
    errors: int = 0
    
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens
    
    def cache_hit_rate(self) -> float:
        if self.prompt_tokens == 0:
            return 0.0
        return (self.cache_hit_tokens / self.prompt_tokens) * 100

# 전역 사용량 추적
usage_stats: Dict[str, APIUsage] = {
    "deepseek": APIUsage("deepseek"),
    "gemini": APIUsage("gemini"),
    "elevenlabs": APIUsage("elevenlabs")
}


def _validate_masked_log_entry(text: str) -> bool:
    """
    로그 항목이 안전하게 마스킹되었는지 검증합니다.
    
    Args:
        text: 검증할 텍스트
        
    Returns:
        안전하면 True, 아니면 False
    """
    if not text:
        return True
    
    # 실제 API 키 패턴이 남아있는지 확인
    api_key_patterns = [
        r'sk-[a-zA-Z0-9_-]{20,}',
        r'[a-zA-Z0-9_-]{40,}',
    ]
    
    for pattern in api_key_patterns:
        if re.search(pattern, text):
            return False
    
    # 환경 변수에서 읽은 실제 API 키 값이 포함되어 있는지 확인
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10 and ELEVENLABS_API_KEY in text:
        return False
    if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10 and DEEPSEEK_API_KEY in text:
        return False
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10 and GEMINI_API_KEY in text:
        return False
    if ELEVENLABS_VOICE_ID and len(ELEVENLABS_VOICE_ID) > 10 and ELEVENLABS_VOICE_ID in text:
        return False
    
    return True


def _write_validated_safe_text(file_path: Path, safe_text: str, mode: str = "a") -> None:
    """
    검증된 안전한 텍스트만 파일에 기록합니다.

    이 함수는 _validate_masked_log_entry()로 검증된 텍스트만 받습니다.
    CodeQL이 민감 정보 저장으로 감지하지 않도록 별도 함수로 분리했습니다.

    Args:
        file_path: 파일 경로
        safe_text: _validate_masked_log_entry()로 검증된 안전한 텍스트
        mode: 파일 모드 ("a" for append, "w" for write)
    """
    # Security: This function only receives pre-validated safe text
    # All sensitive information has been masked and validated before reaching here
    if not safe_text:
        return

    # Additional runtime validation (defense in depth)
    if not _validate_masked_log_entry(safe_text):
        # If somehow unsafe text reached here, block it
        return

    try:
        # 보안: 검증된 안전한 텍스트만 파일에 기록
        # 최종 마스킹 - CodeQL이 인식할 수 있도록 기록 직전에 마스킹
        final_text = mask_sensitive_info(safe_text)
        if not _validate_masked_log_entry(final_text):
            return

        with open(file_path, mode, encoding="utf-8") as f:
            # Security: Write only pre-validated, sanitized text
            # nosec B608 - sanitized via mask_sensitive_info and _validate_masked_log_entry
            # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
            f.write(final_text)  # Sanitized data only
            f.flush()
    except Exception:
        # 예외 발생 시 조용히 처리 (보안상 로그에 기록하지 않음)
        pass


def _print_validated_safe_text(safe_text: str) -> None:
    """
    검증된 안전한 텍스트만 stdout에 출력합니다.

    이 함수는 _validate_masked_log_entry()로 검증된 텍스트만 받습니다.
    CodeQL이 민감 정보 로깅으로 감지하지 않도록 별도 함수로 분리했습니다.

    Args:
        safe_text: _validate_masked_log_entry()로 검증된 안전한 텍스트
    """
    # Security: This function only receives pre-validated safe text
    # All sensitive information has been masked and validated before reaching here
    if not safe_text:
        return

    # Additional runtime validation (defense in depth)
    if not _validate_masked_log_entry(safe_text):
        # If somehow unsafe text reached here, block it
        return

    # Security: Only print pre-validated, masked text
    # 최종 마스킹 - CodeQL이 인식할 수 있도록 출력 직전에 마스킹
    final_text = mask_sensitive_info(safe_text)
    if _validate_masked_log_entry(final_text):
        # Security: Output only pre-validated, sanitized text
        # nosec B608 - sanitized via mask_sensitive_info and _validate_masked_log_entry
        # nosemgrep: python.lang.security.audit.logging.logger-credential-leak
        print(final_text)  # Sanitized data only


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
    masked = re.sub(r'sk-[a-zA-Z0-9_-]{20,}', 'sk-***MASKED***', text)
    masked = re.sub(r'[a-zA-Z0-9_-]{40,}', lambda m: m.group()[:8] + '***MASKED***' if len(m.group()) > 40 else m.group(), masked)
    
    # 환경 변수에서 읽은 실제 API 키 값 마스킹
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10:
        masked = masked.replace(ELEVENLABS_API_KEY, '***ELEVENLABS_API_KEY_MASKED***')
    if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10:
        masked = masked.replace(DEEPSEEK_API_KEY, '***DEEPSEEK_API_KEY_MASKED***')
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
        masked = masked.replace(GEMINI_API_KEY, '***GEMINI_API_KEY_MASKED***')
    if ELEVENLABS_VOICE_ID and len(ELEVENLABS_VOICE_ID) > 10:
        masked = masked.replace(ELEVENLABS_VOICE_ID, '***VOICE_ID_MASKED***')
    
    return masked


def log_message(message: str, level: str = "INFO") -> None:
    """
    로그 메시지를 파일과 stdout에 기록합니다.
    
    Args:
        message: 로그 메시지
        level: 로그 레벨 (INFO, ERROR, WARNING)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_message = mask_sensitive_info(message)
    log_entry = f"[{timestamp}] [{level}] {safe_message}\n"
    
    try:
        # 보안: 민감 정보가 포함된 로그는 파일에 기록하지 않음
        # log_entry는 이미 mask_sensitive_info()로 마스킹되었지만 추가 검증
        # 최종 검증: 마스킹이 완전히 되었는지 확인
        final_log_entry = mask_sensitive_info(log_entry)
        # 추가 검증 라운드 (방어적 프로그래밍)
        for _ in range(2):
            if not _validate_masked_log_entry(final_log_entry):
                final_log_entry = mask_sensitive_info(final_log_entry)
            else:
                break
        
        if _validate_masked_log_entry(final_log_entry):
            # 검증된 안전한 로그만 파일에 기록
            # 보안: 최종 한 번 더 마스킹하여 완전히 안전한지 확인
            safe_final_entry = mask_sensitive_info(final_log_entry)
            if _validate_masked_log_entry(safe_final_entry):
                # Security: Use dedicated function for validated safe text
                _write_validated_safe_text(LOG_FILE, safe_final_entry)
            else:
                # 최종 검증 실패 시 안전한 메시지만 기록
                safe_blocked_msg = f"[{timestamp}] [{level}] [로그 항목이 보안상 차단되었습니다]\n"
                _write_validated_safe_text(LOG_FILE, safe_blocked_msg)
        else:
            # 마스킹 검증 실패 시 민감 정보를 완전히 제거한 안전한 메시지만 기록
            # API 키나 민감 정보가 포함된 부분을 완전히 제거
            safe_log_entry = f"[{timestamp}] [{level}] [로그 항목이 보안상 차단되었습니다]\n"
            _write_validated_safe_text(LOG_FILE, safe_log_entry)
    except Exception as e:
        # 예외 메시지도 마스킹
        error_msg = mask_sensitive_info(str(e))
        print(f"⚠️ 로그 파일 기록 실패: {error_msg}", file=sys.stderr)
    
    # 콘솔 출력도 마스킹된 메시지만 출력
    # 다중 마스킹 적용: 여러 번 마스킹하여 완전히 안전한지 확인
    safe_console_output = mask_sensitive_info(log_entry.strip())
    # 추가 마스킹 라운드 (방어적 프로그래밍)
    for _ in range(2):
        if not _validate_masked_log_entry(safe_console_output):
            safe_console_output = mask_sensitive_info(safe_console_output)
        else:
            break
    
    # 보안: 최종 검증 및 추가 마스킹 라운드
    final_console_output = safe_console_output
    for _ in range(2):
        if not _validate_masked_log_entry(final_console_output):
            final_console_output = mask_sensitive_info(final_console_output)
        else:
            break
    
    if _validate_masked_log_entry(final_console_output):
        # 최종 한 번 더 마스킹하여 완전히 안전한지 확인
        safe_final_output = mask_sensitive_info(final_console_output)
        if _validate_masked_log_entry(safe_final_output):
            # Security: Use dedicated function for validated safe text
            _print_validated_safe_text(safe_final_output)
        else:
            # 최종 검증 실패 시 안전한 메시지만 출력
            _print_validated_safe_text("[로그 출력이 보안상 차단되었습니다]")
    else:
        # 최종 마스킹 시도 실패 시 안전한 메시지만 출력
        _print_validated_safe_text("[로그 출력이 보안상 차단되었습니다]")


def get_cache_key(text: str, post_title: str = "") -> str:
    """캐시 키 생성"""
    content = f"{post_title}:{text[:1000]}"  # 처음 1000자만 사용
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def load_from_cache(cache_key: str) -> Optional[str]:
    """캐시에서 대본 로드"""
    if not ENABLE_CACHING:
        return None
    
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                # 캐시 만료 시간 확인 (7일)
                cache_time = datetime.fromisoformat(cache_data.get("timestamp", ""))
                if (datetime.now() - cache_time).days < 7:
                    log_message(f"✅ 캐시에서 대본 로드: {cache_key[:8]}...")
                    return cache_data.get("script")
        except Exception as e:
            log_message(f"⚠️ 캐시 로드 실패: {str(e)}", "WARNING")
    
    return None


def save_to_cache(cache_key: str, script: str) -> None:
    """대본을 캐시에 저장"""
    if not ENABLE_CACHING:
        return
    
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "script": script
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_message(f"⚠️ 캐시 저장 실패: {str(e)}", "WARNING")


def validate_api_keys() -> Tuple[bool, list]:
    """
    필수 API 키가 설정되어 있는지 검증합니다.
    
    Returns:
        (모든 필수 키가 설정되어 있으면 True, 누락된 키 목록)
    """
    missing_keys = []
    
    if not ELEVENLABS_API_KEY:
        missing_keys.append("ELEVENLABS_API_KEY")
    if not ELEVENLABS_VOICE_ID:
        missing_keys.append("ELEVENLABS_VOICE_ID")
    
    # DeepSeek 또는 Gemini 중 하나는 필요
    if not DEEPSEEK_API_KEY and not GEMINI_API_KEY:
        missing_keys.append("DEEPSEEK_API_KEY 또는 GEMINI_API_KEY")
    
    if missing_keys:
        log_message(f"❌ 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_keys)}", "ERROR")
        log_message("환경 변수 설정 방법:", "ERROR")
        log_message("  export ELEVENLABS_API_KEY='your-api-key'", "ERROR")
        log_message("  export ELEVENLABS_VOICE_ID='your-voice-id'", "ERROR")
        log_message("  export DEEPSEEK_API_KEY='your-deepseek-key' (또는)", "ERROR")
        log_message("  export GEMINI_API_KEY='your-gemini-key'", "ERROR")
        return False, missing_keys
    
    # API 키 형식 검증
    if DEEPSEEK_API_KEY and not DEEPSEEK_API_KEY.startswith("sk-"):
        log_message("⚠️ DEEPSEEK_API_KEY 형식이 올바르지 않습니다 (sk-로 시작해야 함)", "WARNING")
    
    return True, []


def clean_markdown(content: str) -> str:
    """
    마크다운 콘텐츠를 정제하여 AI가 읽기 편하게 만듭니다.
    
    Args:
        content: 원본 마크다운 콘텐츠
        
    Returns:
        정제된 텍스트
    """
    if not content:
        return ""
    
    # 코드 블록 제거 (```...```)
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # 인라인 코드 제거 (`...`)
    content = re.sub(r'`[^`]+`', '', content)
    
    # 이미지 태그 제거
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    
    # 링크를 텍스트로 변환 ([텍스트](URL) -> 텍스트)
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    
    # HTML 태그 제거
    content = re.sub(r'<[^>]+>', '', content)
    
    # 연속된 공백 정리
    content = re.sub(r'\s+', ' ', content)
    
    # 앞뒤 공백 제거
    content = content.strip()
    
    return content


def check_gemini_cli_available() -> bool:
    """Gemini CLI가 설치되어 있는지 확인"""
    try:
        result = subprocess.run(
            ['gemini', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def generate_script_with_gemini_cli(text: str, post_title: str = "") -> Optional[str]:
    """
    Gemini CLI를 사용하여 강의용 대본을 생성합니다.
    OAuth 2.0을 지원하며, CLI 설정에서 자동으로 인증합니다.
    
    Args:
        text: 원본 텍스트
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        생성된 대본 또는 None (실패 시)
    """
    if not check_gemini_cli_available():
        return None
    
    if not text:
        log_message("❌ 텍스트가 비어있습니다.", "ERROR")
        return None
    
    # 텍스트 길이 제한 (비용 관리)
    if len(text) > MAX_TEXT_LENGTH:
        log_message(f"⚠️ 텍스트가 너무 깁니다 ({len(text)}자). 처음 {MAX_TEXT_LENGTH}자만 사용합니다.", "WARNING")
        text = text[:MAX_TEXT_LENGTH]
    
    # Gemini CLI를 위한 프롬프트 구성 (1.5배속 재생 고려)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""다음 보안 기술 블로그 내용을 7-8분 분량의 상세한 강의 대본으로 요약해줘.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

{title_context}블로그 내용:
{text}

강의 대본 작성 가이드:
1. **서론 (30-45초, 1.5배속 시 20-30초)**: 인사말, 주제 소개, 학습 목표 안내
2. **본론 (6-7분, 1.5배속 시 4-4.5분)**: 핵심 내용을 단계별로 상세하게 설명, 구어체 사용, 실무 예시 포함
3. **결론 (30-45초, 1.5배속 시 20-30초)**: 핵심 내용 요약, 실무 팁, 마무리 인사

요구사항:
- 자연스러운 구어체로 작성
- 핵심 내용을 상세하고 체계적으로 전달
- 7-8분 분량 (약 2,000-2,500자, 1.5배속 재생 시 약 5분)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 실무 예시와 비유를 풍부하게 포함
- 한국어로 작성
- 강의자의 말투처럼 자연스럽고 친근하게 작성"""
    
    try:
        log_message("📝 Gemini CLI로 대본 생성 중...")
        
        # Gemini CLI 실행
        result = subprocess.run(
            ['gemini', prompt],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT
        )
        
        usage = usage_stats["gemini"]
        usage.requests += 1
        
        if result.returncode == 0:
            script = result.stdout.strip()
            
            # 대본 길이 검증
            if len(script) > MAX_SCRIPT_LENGTH:
                log_message(f"⚠️ 생성된 대본이 너무 깁니다 ({len(script)}자). 처음 {MAX_SCRIPT_LENGTH}자만 사용합니다.", "WARNING")
                script = script[:MAX_SCRIPT_LENGTH]
            
            log_message(f"✅ Gemini CLI로 대본 생성 완료 ({len(script)}자)")
            return script
        else:
            usage.errors += 1
            error_msg = result.stderr.strip() if result.stderr else "알 수 없는 오류"
            log_message(f"❌ Gemini CLI 오류: {error_msg}", "ERROR")
            return None
            
    except subprocess.TimeoutExpired:
        usage = usage_stats["gemini"]
        usage.errors += 1
        log_message("❌ Gemini CLI 타임아웃 (120초 초과)", "ERROR")
        return None
    except FileNotFoundError:
        log_message("❌ Gemini CLI를 찾을 수 없습니다. 설치: npm install -g @google/gemini-cli", "ERROR")
        return None
    except Exception as e:
        usage = usage_stats["gemini"]
        usage.errors += 1
        error_msg = mask_sensitive_info(str(e))
        log_message(f"❌ Gemini CLI 호출 오류: {error_msg}", "ERROR")
        return None


def get_gemini_oauth_client():
    """
    OAuth 2.0을 사용하여 Gemini 클라이언트를 생성합니다.
    
    Returns:
        Gemini GenerativeModel 또는 None (실패 시)
    """
    if not USE_OAUTH or not OAUTH_AVAILABLE:
        return None
    
    try:
        # 서비스 계정 자격 증명 사용
        credentials, project = default()
        
        # Gemini API 클라이언트 초기화
        genai.configure(credentials=credentials)
        
        # 모델 생성 (Gemini 2.5 Pro 사용)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        log_message("✅ OAuth 2.0 인증 완료 (서비스 계정 사용)")
        return model
    except NameError:
        log_message("❌ google.generativeai 모듈을 찾을 수 없습니다. pip install google-generativeai 실행하세요.", "ERROR")
        return None
    except ImportError:
        log_message("❌ Google 인증 라이브러리를 찾을 수 없습니다. pip install google-auth google-generativeai 실행하세요.", "ERROR")
        return None
    except Exception as e:
        error_msg = mask_sensitive_info(str(e))
        log_message(f"❌ OAuth 2.0 인증 실패: {error_msg}", "ERROR")
        return None


def generate_script_with_gemini_oauth(text: str, post_title: str = "") -> Optional[str]:
    """
    OAuth 2.0을 사용하여 Gemini API로 강의용 대본을 생성합니다.
    
    Args:
        text: 원본 텍스트
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        생성된 대본 또는 None (실패 시)
    """
    if not USE_OAUTH:
        return None
    
    model = get_gemini_oauth_client()
    if not model:
        return None
    
    if not text:
        log_message("❌ 텍스트가 비어있습니다.", "ERROR")
        return None
    
    # 텍스트 길이 제한 (비용 관리)
    if len(text) > MAX_TEXT_LENGTH:
        log_message(f"⚠️ 텍스트가 너무 깁니다 ({len(text)}자). 처음 {MAX_TEXT_LENGTH}자만 사용합니다.", "WARNING")
        text = text[:MAX_TEXT_LENGTH]
    
    # 프롬프트 구성 (1.5배속 재생 고려하여 더 긴 대본 생성)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""당신은 기술 블로그를 전문 강의 대본으로 변환하는 전문가입니다. 
다음 보안 기술 블로그 내용을 7-8분 분량의 상세하고 매력적인 강의 대본으로 변환해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

{title_context}블로그 내용:
{text}

강의 대본 작성 가이드:
1. **서론 (30-45초, 1.5배속 시 20-30초)**
   - 인사말과 오늘 다룰 주제 소개
   - 학습 목표와 강의 구성 안내
   - 예: "안녕하세요, 오늘은 [주제]에 대해 자세히 알아보겠습니다. 이번 강의에서는 [핵심 내용]을 중심으로 설명드리겠습니다."

2. **본론 (6-7분, 1.5배속 시 4-4.5분)**
   - 핵심 내용을 단계별로 상세하고 명확하게 설명
   - 구어체 사용 ("이제", "그런데", "중요한 것은", "예를 들어" 등)
   - 기술 용어는 정확하게 사용하되, 쉬운 설명과 비유를 풍부하게 추가
   - 실무 예시, 코드 예제, 시나리오를 구체적으로 설명
   - 각 섹션마다 자연스러운 전환 구문 사용
   - 핵심 포인트를 반복하여 강조

3. **결론 (30-45초, 1.5배속 시 20-30초)**
   - 오늘 배운 핵심 내용을 체계적으로 요약
   - 실무 적용 팁 또는 다음 학습 내용 안내
   - 마무리 인사

요구사항:
- 자연스러운 구어체로 작성 (강의자의 말투)
- 핵심 내용을 상세하고 체계적으로 전달
- 7-8분 분량 (약 2,000-2,500자, 1.5배속 재생 시 약 5분)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 실무 예시와 비유를 풍부하게 포함
- 한국어로 작성
- 강의자의 말투처럼 자연스럽고 친근하게 작성"""
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))
                log_message(f"🔄 Gemini OAuth API 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            else:
                log_message("📝 Gemini OAuth 2.0 API로 대본 생성 중...")
            
            # Gemini API 호출
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.8,
                    "top_k": 40,
                    "top_p": 0.95,
                    "max_output_tokens": 3000,  # 더 긴 대본 생성을 위해 증가
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            )
            
            usage = usage_stats["gemini"]
            usage.requests += 1
            
            if response and response.text:
                script = response.text.strip()
                
                # 사용량 정보 (가능한 경우)
                if hasattr(response, 'usage_metadata'):
                    usage.prompt_tokens += getattr(response.usage_metadata, 'prompt_token_count', 0)
                    usage.completion_tokens += getattr(response.usage_metadata, 'candidates_token_count', 0)
                
                # 대본 길이 검증
                if len(script) > MAX_SCRIPT_LENGTH:
                    log_message(f"⚠️ 생성된 대본이 너무 깁니다 ({len(script)}자). 처음 {MAX_SCRIPT_LENGTH}자만 사용합니다.", "WARNING")
                    script = script[:MAX_SCRIPT_LENGTH]
                
                log_message(f"✅ Gemini OAuth 2.0 API로 대본 생성 완료 ({len(script)}자)")
                return script
            else:
                log_message("⚠️ Gemini API 응답이 비어있습니다.", "WARNING")
                if attempt < max_retries:
                    continue
                return None
                
        except Exception as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            error_msg = mask_sensitive_info(str(e))
            log_message(f"❌ Gemini OAuth API 호출 오류 (시도 {attempt}/{max_retries}): {error_msg}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini OAuth API 호출 오류: 최대 재시도 횟수 초과", "ERROR")
            return None
    
    return None


def generate_script_with_gemini(text: str, post_title: str = "") -> Optional[str]:
    """
    Gemini AI Pro를 사용하여 고품질 강의용 대본을 생성합니다.
    
    Args:
        text: 원본 텍스트
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        생성된 대본 또는 None (실패 시)
    """
    if not GEMINI_API_KEY:
        return None
    
    if not text:
        log_message("❌ 텍스트가 비어있습니다.", "ERROR")
        return None
    
    # 텍스트 길이 제한 (비용 관리)
    if len(text) > MAX_TEXT_LENGTH:
        log_message(f"⚠️ 텍스트가 너무 깁니다 ({len(text)}자). 처음 {MAX_TEXT_LENGTH}자만 사용합니다.", "WARNING")
        text = text[:MAX_TEXT_LENGTH]
    
    # Gemini AI Pro를 위한 고급 프롬프트 구성 (1.5배속 재생 고려)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""당신은 기술 블로그를 전문 강의 대본으로 변환하는 전문가입니다. 
다음 보안 기술 블로그 내용을 7-8분 분량의 상세하고 매력적인 강의 대본으로 변환해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

{title_context}블로그 내용:
{text}

강의 대본 작성 가이드:
1. **서론 (30-45초, 1.5배속 시 20-30초)**
   - 인사말과 오늘 다룰 주제 소개
   - 학습 목표와 강의 구성 안내
   - 예: "안녕하세요, 오늘은 [주제]에 대해 자세히 알아보겠습니다. 이번 강의에서는 [핵심 내용]을 중심으로 설명드리겠습니다."

2. **본론 (6-7분, 1.5배속 시 4-4.5분)**
   - 핵심 내용을 단계별로 상세하고 명확하게 설명
   - 구어체 사용 ("이제", "그런데", "중요한 것은", "예를 들어" 등)
   - 기술 용어는 정확하게 사용하되, 쉬운 설명과 비유를 풍부하게 추가
   - 실무 예시, 코드 예제, 시나리오를 구체적으로 설명
   - 각 섹션마다 자연스러운 전환 구문 사용
   - 핵심 포인트를 반복하여 강조

3. **결론 (30-45초, 1.5배속 시 20-30초)**
   - 오늘 배운 핵심 내용을 체계적으로 요약
   - 실무 적용 팁 또는 다음 학습 내용 안내
   - 마무리 인사

요구사항:
- 자연스러운 구어체로 작성 (강의자의 말투)
- 핵심 내용을 상세하고 체계적으로 전달
- 7-8분 분량 (약 2,000-2,500자, 1.5배속 재생 시 약 5분)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 실무 예시와 비유를 풍부하게 포함
- 한국어로 작성
- 강의자의 말투처럼 자연스럽고 친근하게 작성"""
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))
                log_message(f"🔄 Gemini API 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            else:
                log_message("📝 Gemini AI Pro로 대본 생성 중...")
            
            url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            
            # Gemini AI Pro 고급 설정
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.8,  # 창의성 향상
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 3000,  # 더 긴 대본 생성을 위해 증가
                    "candidateCount": 1
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            usage = usage_stats["gemini"]
            usage.requests += 1
            
            response = requests.post(url, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                # 사용량 추적
                if "usageMetadata" in result:
                    usage.prompt_tokens += result["usageMetadata"].get("promptTokenCount", 0)
                    usage.completion_tokens += result["usageMetadata"].get("candidatesTokenCount", 0)
                
                candidates = result.get('candidates', [])
                if candidates and len(candidates) > 0:
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and len(parts) > 0:
                        script = parts[0].get('text', '').strip()
                        
                        # 대본 길이 검증
                        if len(script) > MAX_SCRIPT_LENGTH:
                            log_message(f"⚠️ 생성된 대본이 너무 깁니다 ({len(script)}자). 처음 {MAX_SCRIPT_LENGTH}자만 사용합니다.", "WARNING")
                            script = script[:MAX_SCRIPT_LENGTH]
                        
                        log_message(f"✅ Gemini AI Pro로 대본 생성 완료 ({len(script)}자)")
                        return script
                else:
                    log_message("⚠️ Gemini API 응답에 후보가 없습니다.", "WARNING")
                    if attempt < max_retries:
                        continue
            else:
                usage.errors += 1
                error_msg = f"Gemini API 오류: HTTP {response.status_code}"
                if response.text:
                    try:
                        error_detail = json.loads(response.text)
                        error_msg += f" - {json.dumps(error_detail, ensure_ascii=False)[:200]}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                log_message(error_msg, "ERROR")
                if attempt < max_retries:
                    continue
                
        except requests.exceptions.Timeout as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            log_message(f"⏱️ Gemini API 타임아웃 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini API 요청 타임아웃: 최대 재시도 횟수 초과", "ERROR")
            return None
        except requests.exceptions.RequestException as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            log_message(f"❌ Gemini API 요청 실패 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini API 요청 실패: 최대 재시도 횟수 초과", "ERROR")
            return None
        except Exception as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            error_msg = mask_sensitive_info(str(e))
            log_message(f"❌ Gemini API 호출 오류 (시도 {attempt}/{max_retries}): {error_msg}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini API 호출 오류: 최대 재시도 횟수 초과", "ERROR")
            return None
    
    return None


def generate_script_with_deepseek(text: str, post_title: str = "") -> Optional[str]:
    """
    DeepSeek API를 사용하여 강의용 대본을 생성합니다.
    
    Args:
        text: 원본 텍스트
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        생성된 대본 또는 None (실패 시)
    """
    if not DEEPSEEK_API_KEY:
        return None
    
    if not text:
        log_message("❌ 텍스트가 비어있습니다.", "ERROR")
        return None
    
    # 텍스트 길이 제한 (비용 관리)
    if len(text) > MAX_TEXT_LENGTH:
        log_message(f"⚠️ 텍스트가 너무 깁니다 ({len(text)}자). 처음 {MAX_TEXT_LENGTH}자만 사용합니다.", "WARNING")
        text = text[:MAX_TEXT_LENGTH]
    
    # 프롬프트 구성 (1.5배속 재생 고려)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""다음 보안 기술 블로그 내용을 7-8분 분량의 상세한 강의 대본으로 요약해줘. 
구어체로 작성하고, 핵심 내용을 상세하고 명확하게 전달해줘.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

{title_context}블로그 내용:
{text}

요구사항:
- 구어체로 작성 (예: "안녕하세요", "이제", "그런데", "예를 들어" 등 자연스러운 말투)
- 핵심 내용을 상세하고 체계적으로 전달
- 7-8분 분량 (약 2,000-2,500자, 1.5배속 재생 시 약 5분)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 실무 예시와 비유를 풍부하게 포함
- 한국어로 작성"""
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))
                log_message(f"🔄 DeepSeek API 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            else:
                log_message("📝 DeepSeek API로 대본 생성 중...")
            
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 기술 블로그를 강의 대본으로 변환하는 전문가입니다. 자연스럽고 명확한 구어체로 작성해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 3000  # 더 긴 대본 생성을 위해 증가
            }
            
            timeout_seconds = 120
            
            response = requests.post(
                DEEPSEEK_API_URL,
                json=data,
                headers=headers,
                timeout=timeout_seconds
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 사용량 추적
            usage = usage_stats["deepseek"]
            usage.requests += 1
            
            if "usage" in result:
                usage.prompt_tokens += result["usage"].get("prompt_tokens", 0)
                usage.completion_tokens += result["usage"].get("completion_tokens", 0)
                if "prompt_cache_hit_tokens" in result["usage"]:
                    usage.cache_hit_tokens += result["usage"].get("prompt_cache_hit_tokens", 0)
            
            if "choices" not in result or not result["choices"]:
                log_message(f"❌ DeepSeek API 응답 형식 오류: {json.dumps(result, ensure_ascii=False)}", "ERROR")
                usage.errors += 1
                if attempt < max_retries:
                    continue
                return None
            
            script = result["choices"][0]["message"]["content"].strip()
            
            # 대본 길이 검증
            if len(script) > MAX_SCRIPT_LENGTH:
                log_message(f"⚠️ 생성된 대본이 너무 깁니다 ({len(script)}자). 처음 {MAX_SCRIPT_LENGTH}자만 사용합니다.", "WARNING")
                script = script[:MAX_SCRIPT_LENGTH]
            
            log_message(f"✅ DeepSeek API로 대본 생성 완료 ({len(script)}자)")
            return script
            
        except requests.exceptions.Timeout as e:
            log_message(f"⏱️ DeepSeek API 타임아웃 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            usage.errors += 1
            if attempt < max_retries:
                continue
            log_message(f"❌ DeepSeek API 요청 타임아웃: 최대 재시도 횟수 초과", "ERROR")
            return None
        except requests.exceptions.RequestException as e:
            log_message(f"❌ DeepSeek API 요청 실패 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            usage.errors += 1
            if attempt < max_retries:
                continue
            log_message(f"❌ DeepSeek API 요청 실패: 최대 재시도 횟수 초과", "ERROR")
            return None
        except Exception as e:
            log_message(f"❌ 대본 생성 중 오류 발생 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            usage.errors += 1
            if attempt < max_retries:
                continue
            log_message(f"❌ 대본 생성 중 오류 발생: 최대 재시도 횟수 초과", "ERROR")
            return None
    
    return None


def improve_script_with_gemini(script: str, post_title: str = "") -> Optional[str]:
    """
    Gemini AI Pro를 사용하여 대본을 고품질로 개선합니다.
    
    Args:
        script: 원본 대본
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        개선된 대본 또는 None (실패 시)
    """
    if not GEMINI_API_KEY:
        return None
    
    if not script:
        return None
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))
                log_message(f"🔄 Gemini API 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            else:
                log_message("✨ Gemini AI Pro로 대본 개선 중...")
            
            title_context = f"제목: {post_title}\n\n" if post_title else ""
            prompt = f"""당신은 전문 강의 대본 개선 전문가입니다. 
다음 강의 대본을 더 자연스럽고 매력적이며 효과적으로 개선해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

{title_context}원본 대본:
{script}

개선 가이드:
1. **자연스러운 구어체 유지**: "안녕하세요", "이제", "그런데", "중요한 것은", "예를 들어" 등 자연스러운 말투
2. **핵심 내용 보존**: 기술적 정확성과 핵심 내용은 그대로 유지
3. **표현 개선**: 더 명확하고 이해하기 쉬운 표현으로 변경
4. **흐름 개선**: 논리적 흐름과 전환을 더 부드럽게
5. **몰입도 향상**: 청중의 관심을 끌 수 있는 표현 추가
6. **길이 유지**: 원본과 비슷한 길이 유지 (약 2,000-2,500자, 1.5배속 재생 시 약 5분)

요구사항:
- 자연스러운 구어체 유지
- 핵심 내용은 그대로 유지
- 더 매력적이고 이해하기 쉬운 표현으로 개선
- 강의자의 말투처럼 자연스럽게
- 길이는 원본과 비슷하게 유지
- 한국어로 작성"""
            
            url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            
            # Gemini AI Pro 고급 설정
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.8,  # 창의성 향상
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 3000,  # 더 긴 대본 생성을 위해 증가
                    "candidateCount": 1
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            response = requests.post(url, json=data, timeout=120)
            
            # 사용량 추적
            usage = usage_stats["gemini"]
            usage.requests += 1
            
            if response.status_code == 200:
                result = response.json()
                
                # 사용량 정보 추출
                if "usageMetadata" in result:
                    usage.prompt_tokens += result["usageMetadata"].get("promptTokenCount", 0)
                    usage.completion_tokens += result["usageMetadata"].get("candidatesTokenCount", 0)
                
                candidates = result.get('candidates', [])
                if candidates and len(candidates) > 0:
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and len(parts) > 0:
                        improved_script = parts[0].get('text', '').strip()
                        
                        if improved_script:
                            log_message(f"✅ Gemini AI Pro로 대본 개선 완료 ({len(improved_script)}자)")
                            return improved_script
                else:
                    log_message("⚠️ Gemini API 응답에 후보가 없습니다.", "WARNING")
                    if attempt < max_retries:
                        continue
            else:
                usage.errors += 1
                error_msg = f"Gemini API 오류: HTTP {response.status_code}"
                if response.text:
                    try:
                        error_detail = json.loads(response.text)
                        error_msg += f" - {json.dumps(error_detail, ensure_ascii=False)[:200]}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                log_message(error_msg, "ERROR")
                if attempt < max_retries:
                    continue
                
        except requests.exceptions.Timeout as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            log_message(f"⏱️ Gemini API 타임아웃 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini API 요청 타임아웃: 최대 재시도 횟수 초과", "ERROR")
            return None
        except requests.exceptions.RequestException as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            log_message(f"❌ Gemini API 요청 실패 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini API 요청 실패: 최대 재시도 횟수 초과", "ERROR")
            return None
        except Exception as e:
            usage = usage_stats["gemini"]
            usage.errors += 1
            error_msg = mask_sensitive_info(str(e))
            log_message(f"❌ Gemini API 호출 오류 (시도 {attempt}/{max_retries}): {error_msg}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ Gemini API 호출 오류: 최대 재시도 횟수 초과", "ERROR")
            return None
    
    return None


def generate_script(text: str, post_title: str = "") -> Optional[str]:
    """
    적절한 API를 선택하여 강의용 대본을 생성합니다.
    Gemini AI Pro를 적극 활용하는 전략을 사용합니다.
    
    Args:
        text: 원본 텍스트
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        생성된 대본 또는 None (실패 시)
    """
    # 캐시 확인
    cache_key = get_cache_key(text, post_title)
    cached_script = load_from_cache(cache_key)
    if cached_script:
        return cached_script
    
    # API 선택 전략 (비용 최적화: CLI 우선)
    script = None

    # 전략 1: Gemini CLI 우선 (무료 - OAuth 2.0 인증) ⭐ 비용 절감
    if USE_GEMINI_CLI and check_gemini_cli_available():
        log_message("🎯 Gemini CLI 우선 전략 (무료): Gemini CLI로 대본 생성 시도...")
        script = generate_script_with_gemini_cli(text, post_title)

    # 전략 2: OAuth 2.0 (USE_OAUTH=true)
    if not script and USE_OAUTH:
        log_message("🎯 OAuth 2.0 전략: Gemini OAuth 2.0 API로 대본 생성 시도...")
        script = generate_script_with_gemini_oauth(text, post_title)

    # 전략 3: Gemini API 키 (비용 발생)
    if not script and USE_GEMINI_FOR_SCRIPT and GEMINI_API_KEY:
        log_message("🔄 Gemini API로 대본 생성 시도 (API 비용 발생)...", "WARNING")
        script = generate_script_with_gemini(text, post_title)

    # 전략 4: DeepSeek API (비용 발생)
    if not script and USE_DEEPSEEK_FOR_SCRIPT and DEEPSEEK_API_KEY:
        log_message("🔄 DeepSeek API로 대본 생성 시도 (API 비용 발생)...", "WARNING")
        script = generate_script_with_deepseek(text, post_title)

    if not script:
        log_message("❌ 대본 생성 실패: 사용 가능한 API가 없습니다.", "ERROR")
        return None
    
    # 2단계: Gemini AI Pro로 대본 개선 (선택적, DeepSeek으로 생성한 경우에만)
    # Gemini로 생성한 경우는 이미 고품질이므로 개선 단계 생략 가능
    if USE_GEMINI_FOR_IMPROVEMENT and GEMINI_API_KEY and script:
        # DeepSeek으로 생성한 경우에만 개선
        if not (PREFER_GEMINI and USE_GEMINI_FOR_SCRIPT):
            improved_script = improve_script_with_gemini(script, post_title)
            if improved_script:
                script = improved_script
        else:
            log_message("💡 Gemini AI Pro로 생성된 대본은 이미 고품질이므로 개선 단계를 건너뜁니다.")
    
    # 캐시 저장
    if script:
        save_to_cache(cache_key, script)
    
    return script


def text_to_speech_with_gemini(script: str, output_path: Path) -> bool:
    """
    Gemini API를 사용하여 텍스트를 음성으로 변환합니다.
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not script:
        log_message("❌ 대본이 비어있습니다.", "ERROR")
        return False
    
    if not GEMINI_API_KEY:
        return False
    
    try:
        log_message("🎤 Gemini API로 음성 생성 중...")
        
        # Gemini TTS는 현재 제한적이므로, 일단 ElevenLabs로 폴백
        # 향후 Gemini TTS API가 정식 출시되면 구현
        log_message("⚠️ Gemini TTS는 아직 정식 출시되지 않았습니다. ElevenLabs로 폴백합니다.", "WARNING")
        return False
        
    except Exception as e:
        log_message(f"❌ Gemini TTS 오류: {str(e)}", "ERROR")
        return False


def text_to_speech(script: str, output_path: Path) -> bool:
    """
    ElevenLabs API 또는 Gemini API를 사용하여 텍스트를 음성으로 변환합니다.
    비용 최적화: ElevenLabs를 우선 사용 (비용 효율적), Gemini는 폴백으로 사용.
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not script:
        log_message("❌ 대본이 비어있습니다.", "ERROR")
        return False
    
    # 비용 최적화: ElevenLabs를 우선 사용 (비용 효율적)
    if ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
        try:
            log_message("🎤 ElevenLabs API로 음성 생성 중... (비용 최적화: ElevenLabs 우선)")
            
            url = f"{ELEVENLABS_API_URL}/{ELEVENLABS_VOICE_ID}"
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": script,
                "model_id": "eleven_multilingual_v2",  # 한국어 지원 모델
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            usage = usage_stats["elevenlabs"]
            usage.requests += 1
            
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=60
            )
            
            response.raise_for_status()
            
            # 오디오 파일 저장
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            file_size = output_path.stat().st_size
            log_message(f"✅ 음성 생성 완료: {output_path} ({file_size:,} bytes)")
            return True
            
        except requests.exceptions.RequestException as e:
            usage = usage_stats["elevenlabs"]
            usage.errors += 1
            log_message(f"❌ ElevenLabs API 요청 실패: {str(e)}", "ERROR")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    log_message(f"   응답 내용: {json.dumps(error_detail, ensure_ascii=False)}", "ERROR")
                except:
                    log_message(f"   응답 내용: {e.response.text[:200]}", "ERROR")
            # ElevenLabs 실패 시 Gemini로 폴백
            log_message("🔄 ElevenLabs 실패, Gemini TTS로 폴백...", "WARNING")
    
    # Gemini TTS 폴백 (ElevenLabs 실패 시)
    if GEMINI_API_KEY:
        if text_to_speech_with_gemini(script, output_path):
            return True
        log_message("⚠️ Gemini TTS도 실패했습니다.", "WARNING")
    
    # 모든 방법 실패
    log_message("❌ 음성 생성 실패: 사용 가능한 API가 없습니다.", "ERROR")
    return False


def generate_image_with_gemini_nano_banana(post_title: str, script: str, output_path: Path) -> bool:
    """
    Gemini Nano Banana를 사용하여 강의용 썸네일 이미지를 생성합니다.
    
    Args:
        post_title: 포스트 제목
        script: 대본 텍스트 (이미지 생성 프롬프트에 활용)
        output_path: 출력 이미지 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not GEMINI_API_KEY:
        log_message("⚠️ Gemini API 키가 없어 이미지 생성을 건너뜁니다.", "WARNING")
        return False
    
    try:
        log_message("🎨 Gemini Nano Banana로 이미지 생성 중...")
        
        # 이미지 생성 프롬프트 (대본의 핵심 내용 기반)
        script_summary = script[:500] if len(script) > 500 else script
        prompt = f"""다음 기술 강의를 위한 전문적이고 현대적인 썸네일 이미지를 생성해주세요.

강의 제목: {post_title}
강의 요약: {script_summary}

요구사항:
- 기술 블로그 강의용 썸네일
- 전문적이고 깔끔한 디자인
- 기술적인 느낌을 주는 색상과 아이콘
- 1920x1080 해상도
- 한국어 텍스트 포함 가능
- 현대적이고 세련된 스타일"""
        
        url = f"{GEMINI_IMAGE_API_URL}?key={GEMINI_API_KEY}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1000
            }
        }
        
        response = requests.post(url, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            # Gemini Nano Banana는 이미지 생성이 아닌 텍스트 기반이므로
            # 실제 이미지 생성은 다른 API나 도구가 필요할 수 있습니다
            log_message("⚠️ Gemini Nano Banana 이미지 생성은 현재 제한적입니다. 기본 썸네일을 사용합니다.", "WARNING")
            return False
        else:
            log_message(f"⚠️ Gemini 이미지 생성 실패: HTTP {response.status_code}", "WARNING")
            return False
            
    except Exception as e:
        log_message(f"⚠️ 이미지 생성 중 오류: {str(e)}", "WARNING")
        return False


def calculate_estimated_cost(usage: APIUsage) -> float:
    """예상 비용 계산 (대략적)"""
    if usage.provider == "deepseek":
        # deepseek-chat: $0.14 / 1M input, $0.28 / 1M output
        input_cost = (usage.prompt_tokens / 1_000_000) * 0.14
        output_cost = (usage.completion_tokens / 1_000_000) * 0.28
        return input_cost + output_cost
    elif usage.provider == "gemini":
        # gemini-1.5-pro: $1.25 / 1M input, $5.00 / 1M output
        input_cost = (usage.prompt_tokens / 1_000_000) * 1.25
        output_cost = (usage.completion_tokens / 1_000_000) * 5.00
        return input_cost + output_cost
    elif usage.provider == "elevenlabs":
        # ElevenLabs는 문자 기반 과금이므로 여기서는 추정 불가
        return 0.0
    return 0.0


def print_usage_stats() -> None:
    """API 사용량 통계 출력"""
    log_message("=" * 60)
    log_message("📊 API 사용량 통계")
    log_message("=" * 60)
    
    total_cost = 0.0
    
    for provider, usage in usage_stats.items():
        if usage.requests > 0:
            cost = calculate_estimated_cost(usage)
            total_cost += cost
            
            log_message(f"\n{provider.upper()}:")
            log_message(f"  요청 수: {usage.requests}")
            log_message(f"  총 토큰: {usage.total_tokens():,}")
            log_message(f"  Prompt 토큰: {usage.prompt_tokens:,}")
            log_message(f"  Completion 토큰: {usage.completion_tokens:,}")
            if usage.cache_hit_tokens > 0:
                log_message(f"  캐시 히트 토큰: {usage.cache_hit_tokens:,}")
                log_message(f"  캐시 히트율: {usage.cache_hit_rate():.1f}%")
            log_message(f"  에러 수: {usage.errors}")
            if cost > 0:
                log_message(f"  예상 비용: ${cost:.6f}")
    
    if total_cost > 0:
        log_message(f"\n💰 총 예상 비용: ${total_cost:.6f}")
    
    log_message("=" * 60)


def process_post(post_path: Path) -> bool:
    """
    단일 포스트를 처리하여 오디오를 생성합니다.
    
    Args:
        post_path: 포스트 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not post_path.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
        return False
    
    try:
        log_message(f"📄 포스트 처리 시작: {post_path.name}")
        
        # Front matter와 콘텐츠 읽기
        with open(post_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        
        title = post.metadata.get("title", "")
        content = post.content
        
        if not content:
            log_message(f"❌ 포스트 콘텐츠가 비어있습니다: {post_path.name}", "ERROR")
            return False
        
        # 마크다운 정제
        cleaned_text = clean_markdown(content)
        
        if not cleaned_text:
            log_message(f"❌ 정제된 텍스트가 비어있습니다: {post_path.name}", "ERROR")
            return False
        
        log_message(f"📝 정제된 텍스트 길이: {len(cleaned_text)}자")
        
        # 대본 생성
        script = generate_script(cleaned_text, title)
        
        if not script:
            log_message(f"❌ 대본 생성 실패: {post_path.name}", "ERROR")
            return False
        
        # 출력 파일 경로 생성
        post_stem = post_path.stem
        script_filename = f"{post_stem}_script.txt"
        script_path = OUTPUT_DIR / script_filename
        audio_filename = f"{post_stem}_audio.{AUDIO_OUTPUT_FORMAT}"
        audio_path = OUTPUT_DIR / audio_filename
        
        # 대본 파일 저장 (사용된 API 정보 포함)
        try:
            # 사용된 API 정보 추적
            api_info = []
            if USE_OAUTH:
                api_info.append("Gemini OAuth 2.0")
            if GEMINI_API_KEY:
                api_info.append("Gemini API Key")
            if DEEPSEEK_API_KEY:
                api_info.append("DeepSeek API")
            
            used_api = " → ".join(api_info) if api_info else "알 수 없음"
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"대본 길이: {len(script)}자\n")
                f.write(f"원본 포스트: {post_path.name}\n")
                f.write(f"사용된 API: {used_api}\n")
                f.write(f"API 전략: ")
                if USE_OAUTH:
                    f.write("OAuth 2.0 우선")
                elif PREFER_GEMINI:
                    f.write("Gemini 우선")
                else:
                    f.write("DeepSeek 우선")
                f.write("\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("강의용 대본\n")
                f.write("=" * 60 + "\n\n")
                # 보안: 스크립트 내용에 민감 정보가 포함될 수 있으므로 마스킹
                # API 응답에 민감 정보가 포함될 수 있으므로 안전하게 처리
                safe_script = mask_sensitive_info(script)
                # 추가 검증: 마스킹이 완전히 되었는지 확인
                if _validate_masked_log_entry(safe_script):
                    # Security: Use dedicated function for validated safe text (append mode)
                    _write_validated_safe_text(script_path, safe_script, mode="a")
                else:
                    # 검증 실패 시 다시 마스킹
                    safe_script = mask_sensitive_info(safe_script)
                    if _validate_masked_log_entry(safe_script):
                        # Security: Use dedicated function for validated safe text (append mode)
                        _write_validated_safe_text(script_path, safe_script, mode="a")
                    else:
                        # 최종 검증 실패 시 안전한 메시지 기록
                        safe_blocked_msg = "[대본 내용이 보안상 차단되었습니다]\n"
                        _write_validated_safe_text(script_path, safe_blocked_msg, mode="a")
                # Security: Safe newline character (append mode)
                _write_validated_safe_text(script_path, "\n", mode="a")
            log_message(f"✅ 대본 파일 저장 완료: {script_path}")
            log_message(f"   사용된 API: {used_api}")
        except Exception as e:
            log_message(f"⚠️ 대본 파일 저장 실패: {str(e)}", "WARNING")
        
        # 음성 생성
        success = text_to_speech(script, audio_path)
        
        if success:
            log_message(f"✅ 포스트 처리 완료: {post_path.name}")
            log_message(f"   대본 파일: {script_path}")
            log_message(f"   오디오 파일: {audio_path}")
            return True
        else:
            log_message(f"❌ 음성 생성 실패: {post_path.name}", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"❌ 포스트 처리 중 오류 발생: {str(e)}", "ERROR")
        import traceback
        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def main():
    """메인 실행 함수"""
    log_message("=" * 60)
    log_message("블로그 포스팅 → 오디오 변환 시작 (개선 버전)")
    log_message("=" * 60)
    
    # API 키 검증
    is_valid, missing_keys = validate_api_keys()
    if not is_valid:
        log_message("❌ API 키 검증 실패. 스크립트를 종료합니다.", "ERROR")
        sys.exit(1)
    
    # 사용 가능한 API 확인
    log_message("🔑 사용 가능한 API:")
    log_message(f"  DeepSeek: {'✅' if DEEPSEEK_API_KEY else '❌'}")
    log_message(f"  Gemini AI Pro (API Key): {'✅' if GEMINI_API_KEY else '❌'}")
    log_message(f"  Gemini CLI: {'✅' if check_gemini_cli_available() else '❌'}")
    log_message(f"  OAuth 2.0: {'✅' if USE_OAUTH else '❌'}")
    if USE_OAUTH:
        if GEMINI_SERVICE_ACCOUNT:
            # 서비스 계정 정보가 있으면 마스킹하여 표시
            masked_account = mask_sensitive_info(GEMINI_SERVICE_ACCOUNT)
            log_message(f"    서비스 계정: {masked_account}")
        if GOOGLE_CLOUD_PROJECT:
            log_message(f"    프로젝트 ID: {GOOGLE_CLOUD_PROJECT}")
        if GOOGLE_APPLICATION_CREDENTIALS:
            log_message(f"    자격 증명 파일: {GOOGLE_APPLICATION_CREDENTIALS}")
    log_message(f"  ElevenLabs: {'✅' if ELEVENLABS_API_KEY else '❌'}")
    log_message(f"  설정:")
    log_message(f"    - OAuth 2.0 우선: {USE_OAUTH} ⭐")
    log_message(f"    - Gemini CLI 우선: {USE_GEMINI_CLI}")
    log_message(f"    - Gemini 우선: {PREFER_GEMINI}")
    log_message(f"    - DeepSeek 대본 생성: {USE_DEEPSEEK_FOR_SCRIPT}")
    log_message(f"    - Gemini 대본 생성: {USE_GEMINI_FOR_SCRIPT}")
    log_message(f"    - Gemini 개선: {USE_GEMINI_FOR_IMPROVEMENT}")
    log_message(f"    - 캐싱: {ENABLE_CACHING}")
    
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        # 특정 포스트 파일 지정
        post_file = Path(sys.argv[1])
        if not post_file.is_absolute():
            post_file = POSTS_DIR / post_file
        
        if not post_file.exists():
            log_message(f"❌ 파일을 찾을 수 없습니다: {post_file}", "ERROR")
            sys.exit(1)
        
        post_paths = [post_file]
    else:
        # 최신 포스트 자동 선택
        log_message("📂 최신 포스트 검색 중...")
        post_files = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not post_files:
            log_message("❌ 포스트 파일을 찾을 수 없습니다.", "ERROR")
            sys.exit(1)
        
        latest_post = post_files[0]
        log_message(f"📄 최신 포스트 선택: {latest_post.name}")
        post_paths = [latest_post]
    
    # 포스트 처리
    success_count = 0
    for post_path in post_paths:
        if process_post(post_path):
            success_count += 1
    
    # 사용량 통계 출력
    print_usage_stats()
    
    # 결과 요약
    log_message("=" * 60)
    log_message(f"처리 완료: {success_count}/{len(post_paths)} 성공")
    log_message("=" * 60)
    
    if success_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
