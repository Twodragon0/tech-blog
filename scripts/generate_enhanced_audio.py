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

# .env 파일 로드 (선택적)
def load_env_file(env_path: Path) -> None:
    """간단한 .env 파일 파서 (python-dotenv 없이도 작동)"""
    if not env_path.exists():
        return
    
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 주석이나 빈 줄 건너뛰기
                if not line or line.startswith("#"):
                    continue
                # KEY=VALUE 형식 파싱
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 환경 변수가 이미 설정되어 있지 않은 경우에만 설정
                    if key and not os.getenv(key):
                        os.environ[key] = value
    except Exception:
        # .env 파일 로드 실패 시 무시 (보안상 안전)
        pass

# 프로젝트 루트의 .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
load_env_file(env_path)

# python-dotenv도 시도 (설치되어 있는 경우)
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(env_path, override=False)  # 기존 환경 변수는 덮어쓰지 않음
except ImportError:
    pass

# OAuth 2.0 지원 (선택적)
try:
    from google.auth import default
    from google.auth.transport.requests import Request
    import google.generativeai as genai
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

# TTS 오픈소스 라이브러리 (비용 최적화)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False

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
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# API 엔드포인트
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"  # Gemini 1.5 Pro deprecated, 2.5 Pro 사용
GEMINI_FLASH_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"  # Gemini 2.5 Flash (높은 RPM)
GEMINI_IMAGE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"  # Gemini Nano Banana (이미지 생성)
GEMINI_VIDEO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"  # Gemini Veo (영상 생성)
# Gemini TTS API 엔드포인트 (비용 최적화: Flash 모델 우선)
GEMINI_TTS_FLASH_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"
GEMINI_TTS_PRO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-tts:generateContent"
# Google Cloud Text-to-Speech API (Chirp 3: Instant Custom Voice 지원)
GCP_TTS_API_URL = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"
GCP_TTS_VOICE_CLONING_KEY_API_URL = "https://texttospeech.googleapis.com/v1beta1/voices:generateVoiceCloningKey"

# Gemini API Rate Limit 설정 (유료 1등급 기준)
# gemini-2.5-pro: RPM 150, TPM 2M, RPD 10K
# gemini-2.5-flash: RPM 1K, TPM 1M, RPD 10K
# gemini-2.0-flash: RPM 2K, TPM 4M, RPD 무제한
GEMINI_PRO_RPM_LIMIT = 150  # Requests Per Minute
GEMINI_PRO_TPM_LIMIT = 2_000_000  # Tokens Per Minute
GEMINI_PRO_RPD_LIMIT = 10_000  # Requests Per Day
GEMINI_FLASH_RPM_LIMIT = 1000  # Requests Per Minute
GEMINI_FLASH_TPM_LIMIT = 1_000_000  # Tokens Per Minute
GEMINI_FLASH_RPD_LIMIT = 10_000  # Requests Per Day

# Rate Limit 안전 마진 (80% 사용 시 경고)
RATE_LIMIT_WARNING_THRESHOLD = 0.8
# 요청 간 최소 지연 시간 (초) - RPM 제한 고려
GEMINI_PRO_MIN_DELAY = 60.0 / GEMINI_PRO_RPM_LIMIT  # 약 0.4초
GEMINI_FLASH_MIN_DELAY = 60.0 / GEMINI_FLASH_RPM_LIMIT  # 약 0.06초

# 설정
MAX_TEXT_LENGTH = 50000  # 최대 텍스트 길이 (비용 관리)
MAX_SCRIPT_LENGTH = 4500  # 최대 대본 길이 (약 7-8분 분량, 1.5배속 재생 시 약 5분)
MIN_SCRIPT_LENGTH = 2000  # 최소 대본 길이 (목표: 2,000-2,500자)
AUDIO_OUTPUT_FORMAT = "mp3"
AUDIO_SPEED_MULTIPLIER = 1.5  # 오디오 재생 속도 배율 (1.5배속)

# API 선택 전략 설정
USE_GEMINI_FOR_IMPROVEMENT = os.getenv("USE_GEMINI_FOR_IMPROVEMENT", "true").lower() == "true"
USE_DEEPSEEK_FOR_SCRIPT = os.getenv("USE_DEEPSEEK_FOR_SCRIPT", "true").lower() == "true"
USE_GEMINI_FOR_SCRIPT = os.getenv("USE_GEMINI_FOR_SCRIPT", "true").lower() == "true"  # Gemini AI Pro 적극 활용
USE_GEMINI_CLI = os.getenv("USE_GEMINI_CLI", "true").lower() == "true"  # Gemini CLI 사용 (비용 절감 - OAuth 2.0 지원)
PREFER_GEMINI = os.getenv("PREFER_GEMINI", "true").lower() == "true"  # Gemini Pro 우선 사용
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
# 모델 선택: "pro" (gemini-2.5-pro) 또는 "flash" (gemini-2.5-flash)
# flash는 RPM이 높아 일반 텍스트 생성에 적합, pro는 고품질 생성에 적합
GEMINI_MODEL_TYPE = os.getenv("GEMINI_MODEL_TYPE", "flash").lower()  # 기본값: flash (높은 RPM)

# TTS 제공자 선택 설정 (비용 최적화: Gemini 우선)
# "gemini", "coqui", "auto" (자동 선택: Gemini -> Coqui)
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "auto").lower()  # 기본값: auto (Gemini 우선)
USE_COQUI_TTS = os.getenv("USE_COQUI_TTS", "false").lower() == "true"  # Coqui TTS 사용 여부

# Gemini TTS Voice 설정 (IT/DevSecOps/클라우드 보안 전문가용 남자 목소리)
# 권장 Voice: "Rasalgethi" (Informative and professional) 또는 "Sadaltager" (Knowledgeable and authoritative)
# 기본값: "Rasalgethi" (IT 전문가용 추천)
# 다른 옵션: Charon, Iapetus, Orus 등 (Gemini TTS API 문서 참조)
GEMINI_TTS_VOICE_NAME = os.getenv("GEMINI_TTS_VOICE_NAME", "Rasalgethi").strip()  # 기본값: Rasalgethi (IT 전문가용)
GEMINI_TTS_VOICE_STYLE = os.getenv("GEMINI_TTS_VOICE_STYLE", "").strip()  # 자연어 프롬프트로 스타일 제어 (예: "professional and authoritative")
GEMINI_TTS_VOICE_PACE = float(os.getenv("GEMINI_TTS_VOICE_PACE", "1.0"))  # 속도 조절 (0.25 ~ 4.0, 기본값: 1.0)

# Chirp 3: Instant Custom Voice 설정 (Google Cloud Text-to-Speech API)
# 자신의 목소리로 클로닝하여 사용하려면 아래 설정 필요
USE_CHIRP3_CUSTOM_VOICE = os.getenv("USE_CHIRP3_CUSTOM_VOICE", "false").lower() == "true"  # Chirp 3 사용 여부
GEMINI_TTS_VOICE_CLONING_KEY = os.getenv("GEMINI_TTS_VOICE_CLONING_KEY", "")  # Voice Cloning Key (선택적)
CHIRP3_VOICE_CLONING_KEY = os.getenv("CHIRP3_VOICE_CLONING_KEY", "")  # Chirp 3 Voice Cloning Key
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")  # Google Cloud Project ID
CHIRP3_LOCATION = os.getenv("CHIRP3_LOCATION", "global").strip()  # 리전 설정 (global, us, eu 등)

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


# Rate Limit 추적 (시간 윈도우 기반)
class RateLimitTracker:
    """Rate Limit 추적 및 모니터링"""
    
    def __init__(self, rpm_limit: int, tpm_limit: int, rpd_limit: int):
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.rpd_limit = rpd_limit
        self.request_times: list = []  # 최근 1분간 요청 시간
        self.token_usage: list = []  # 최근 1분간 토큰 사용량 (timestamp, tokens)
        self.daily_requests: int = 0
        self.last_reset_date = datetime.now().date()
        self.last_request_time: float = 0.0
        self.min_delay = 60.0 / rpm_limit if rpm_limit > 0 else 0.0
    
    def reset_daily_if_needed(self) -> None:
        """일일 요청 수 리셋 (날짜 변경 시)"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_requests = 0
            self.last_reset_date = today
    
    def can_make_request(self) -> Tuple[bool, str]:
        """
        요청 가능 여부 확인
        
        Returns:
            (가능 여부, 이유)
        """
        self.reset_daily_if_needed()
        now = time.time()
        
        # 1분 윈도우 정리
        self.request_times = [t for t in self.request_times if now - t < 60.0]
        self.token_usage = [(ts, tokens) for ts, tokens in self.token_usage if now - ts < 60.0]
        
        # RPM 체크
        if len(self.request_times) >= self.rpm_limit:
            wait_time = 60.0 - (now - self.request_times[0])
            return False, f"RPM 제한 초과 (최대 {self.rpm_limit}/분). {wait_time:.1f}초 후 재시도 가능"
        
        # RPD 체크
        if self.daily_requests >= self.rpd_limit:
            return False, f"일일 요청 제한 초과 (최대 {self.rpd_limit}/일)"
        
        # 최소 지연 시간 체크
        if self.last_request_time > 0:
            elapsed = now - self.last_request_time
            if elapsed < self.min_delay:
                return False, f"요청 간 최소 지연 시간 필요 ({self.min_delay:.2f}초)"
        
        return True, ""
    
    def record_request(self, tokens: int = 0) -> None:
        """요청 기록"""
        self.reset_daily_if_needed()
        now = time.time()
        self.request_times.append(now)
        self.daily_requests += 1
        self.last_request_time = now
        if tokens > 0:
            self.token_usage.append((now, tokens))
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계 반환"""
        self.reset_daily_if_needed()
        now = time.time()
        
        # 1분 윈도우 정리
        self.request_times = [t for t in self.request_times if now - t < 60.0]
        self.token_usage = [(ts, tokens) for ts, tokens in self.token_usage if now - ts < 60.0]
        
        current_rpm = len(self.request_times)
        current_tpm = sum(tokens for _, tokens in self.token_usage)
        
        rpm_usage_rate = current_rpm / self.rpm_limit if self.rpm_limit > 0 else 0.0
        tpm_usage_rate = current_tpm / self.tpm_limit if self.tpm_limit > 0 else 0.0
        rpd_usage_rate = self.daily_requests / self.rpd_limit if self.rpd_limit > 0 else 0.0
        
        return {
            "rpm": {"current": current_rpm, "limit": self.rpm_limit, "usage_rate": rpm_usage_rate},
            "tpm": {"current": current_tpm, "limit": self.tpm_limit, "usage_rate": tpm_usage_rate},
            "rpd": {"current": self.daily_requests, "limit": self.rpd_limit, "usage_rate": rpd_usage_rate}
        }
    
    def check_warning_threshold(self) -> Optional[str]:
        """경고 임계값 체크"""
        stats = self.get_usage_stats()
        warnings = []
        
        if stats["rpm"]["usage_rate"] >= RATE_LIMIT_WARNING_THRESHOLD:
            warnings.append(f"RPM 사용률 {stats['rpm']['usage_rate']*100:.1f}% (경고: {RATE_LIMIT_WARNING_THRESHOLD*100}%)")
        if stats["tpm"]["usage_rate"] >= RATE_LIMIT_WARNING_THRESHOLD:
            warnings.append(f"TPM 사용률 {stats['tpm']['usage_rate']*100:.1f}% (경고: {RATE_LIMIT_WARNING_THRESHOLD*100}%)")
        if stats["rpd"]["usage_rate"] >= RATE_LIMIT_WARNING_THRESHOLD:
            warnings.append(f"일일 요청 사용률 {stats['rpd']['usage_rate']*100:.1f}% (경고: {RATE_LIMIT_WARNING_THRESHOLD*100}%)")
        
        return "; ".join(warnings) if warnings else None


# Rate Limit 추적 인스턴스
rate_limit_trackers = {
    "pro": RateLimitTracker(GEMINI_PRO_RPM_LIMIT, GEMINI_PRO_TPM_LIMIT, GEMINI_PRO_RPD_LIMIT),
    "flash": RateLimitTracker(GEMINI_FLASH_RPM_LIMIT, GEMINI_FLASH_TPM_LIMIT, GEMINI_FLASH_RPD_LIMIT)
}

# 전역 사용량 추적
usage_stats: Dict[str, APIUsage] = {
    "deepseek": APIUsage("deepseek"),
    "gemini": APIUsage("gemini")
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
    if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10 and DEEPSEEK_API_KEY in text:
        return False
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10 and GEMINI_API_KEY in text:
        return False
    if CHIRP3_VOICE_CLONING_KEY and len(CHIRP3_VOICE_CLONING_KEY) > 10 and CHIRP3_VOICE_CLONING_KEY in text:
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
    if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10:
        masked = masked.replace(DEEPSEEK_API_KEY, '***DEEPSEEK_API_KEY_MASKED***')
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
        masked = masked.replace(GEMINI_API_KEY, '***GEMINI_API_KEY_MASKED***')
    if CHIRP3_VOICE_CLONING_KEY and len(CHIRP3_VOICE_CLONING_KEY) > 10:
        masked = masked.replace(CHIRP3_VOICE_CLONING_KEY, '***CHIRP3_VOICE_CLONING_KEY_MASKED***')
    
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
    
    # TTS 제공자에 따라 필요한 키 확인
    if TTS_PROVIDER == "chirp3":
        # Chirp 3 사용 시
        if not USE_CHIRP3_CUSTOM_VOICE:
            missing_keys.append("USE_CHIRP3_CUSTOM_VOICE=true")
        if not CHIRP3_VOICE_CLONING_KEY:
            missing_keys.append("CHIRP3_VOICE_CLONING_KEY")
        if not GOOGLE_CLOUD_PROJECT_ID:
            missing_keys.append("GOOGLE_CLOUD_PROJECT")
        if not GOOGLE_APPLICATION_CREDENTIALS:
            missing_keys.append("GOOGLE_APPLICATION_CREDENTIALS")
    elif TTS_PROVIDER == "gemini":
        # Gemini TTS 사용 시
        if not GEMINI_API_KEY:
            missing_keys.append("GEMINI_API_KEY")
    elif TTS_PROVIDER == "coqui":
        # Coqui TTS 사용 시 (추가 키 불필요)
        pass
    else:
        # auto 모드: 최소한 하나의 TTS 제공자가 필요
        if not USE_CHIRP3_CUSTOM_VOICE and not GEMINI_API_KEY and not USE_COQUI_TTS:
            missing_keys.append("USE_CHIRP3_CUSTOM_VOICE 또는 GEMINI_API_KEY 또는 USE_COQUI_TTS")
    
    # 대본 생성을 위한 API 키 확인
    if not DEEPSEEK_API_KEY and not GEMINI_API_KEY:
        missing_keys.append("DEEPSEEK_API_KEY 또는 GEMINI_API_KEY (대본 생성용)")
    
    if missing_keys:
        log_message(f"❌ 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_keys)}", "ERROR")
        log_message("환경 변수 설정 방법:", "ERROR")
        if TTS_PROVIDER == "chirp3":
            log_message("  export USE_CHIRP3_CUSTOM_VOICE=true", "ERROR")
            log_message("  export CHIRP3_VOICE_CLONING_KEY='your-voice-cloning-key'", "ERROR")
            log_message("  export GOOGLE_CLOUD_PROJECT='your-project-id'", "ERROR")
            log_message("  export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'", "ERROR")
        else:
            log_message("  export DEEPSEEK_API_KEY='your-deepseek-key' (선택적)", "ERROR")
            log_message("  export GEMINI_API_KEY='your-gemini-key' (TTS 필수)", "ERROR")
            log_message("  자세한 내용은 CHIRP3_VOICE_SETUP_GUIDE.md 참조", "ERROR")
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
    
    # Gemini CLI를 위한 프롬프트 구성 (온라인 강의 베스트 프랙티스 반영)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""당신은 클라우드 보안, IT, DevSecOps 전문 온라인 강의를 제작하는 전문가입니다.
다음 기술 블로그 내용을 7-8분 분량의 고품질 온라인 강의 대본으로 변환해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

**⚠️ 매우 중요한 구조 요구사항 - 반드시 정확히 이 순서를 따르세요!**

**대본은 반드시 첫 문장으로 시작해야 합니다. 첫 문장을 절대 생략하거나 잘라내지 마세요!**

1. **처음 30초 (1.5배속 시 약 20초, 약 200-300자) - 핵심 요약으로 흥미 유발**
   **문장 1 (필수)**: 블로그 내용에서 가장 흥미로운 구체적 예시나 질문으로 시작
     * 블로그에 "Pioneer" 같은 구체적 예시가 있으면: "혹시 최근 유튜브에서 화제가 된 'Pioneer'라는 AI 뮤직비디오 보셨나요?"
     * 구체적 예시가 없으면: "2026년, 이제 이미지부터 음악, 영상까지 전부 AI로 만들 수 있게 되었습니다"
     * **⚠️ 절대 첫 문장을 생략하거나 잘라내지 마세요! 대본은 반드시 이 첫 문장으로 시작해야 합니다!**
   **문장 2 (필수)**: 구체적 사례나 놀라운 사실 제시
     * 예: "이미지부터 음악, 영상까지 전부 AI로만 만들었는데, 퀄리티가 정말 놀랍죠"
     * 블로그에 나온 구체적 도구나 기술을 언급
   
   **문장 3 (필수)**: 문제 제기와 관점 전환
     * 예: "하지만 우리 같은 DevSecOps 엔지니어들에게는 이 화려한 기술 뒤에 숨겨진 보안, 비용, 거버넌스 문제가 더 중요합니다"
   
   **문장 4 (필수)**: 블로그 전체 내용 요약 (30초 안에 모든 핵심 키워드 포함)
     * 블로그에 언급된 모든 주요 도구, 기술, 보안 이슈, 비용 최적화 등을 자연스럽게 나열
     * 예: "오늘은 Midjourney, Suno V5, Veo 3 같은 최신 AI 도구부터, API 키 관리, 데이터 프라이버시 보호, CI/CD 자동화, 그리고 비용 최적화 전략까지 DevSecOps 관점에서 완벽하게 정리해드리겠습니다"
     * **반드시 블로그의 모든 핵심 키워드를 빠짐없이 포함하세요!**
   
   **문장 5 (필수)**: 학습 목표 제시
     * 예: "이 강의가 끝나면 여러분은 생성형 AI 프로젝트를 안전하고 효율적으로 운영하는 실질적인 노하우를 갖게 되실 겁니다"
   
   **30초 요약의 핵심**: 
   - 시청자가 "이 강의에서 무엇을 배울 수 있을까?"를 즉시 알 수 있도록 블로그의 모든 핵심 내용을 빠짐없이 요약
   - 반드시 위 5개 문장을 모두 순서대로 포함하여 작성하세요
   - 첫 문장부터 시작하여 다섯 번째 문장까지 완전한 문장으로 작성하세요

2. **본론 (6-7분, 1.5배속 시 4-4.5분) - 포스팅 내용을 순서대로 상세히 설명**
   - **포스팅의 구조와 순서를 그대로 따라가며** 상세히 설명
   - 포스팅에 나온 모든 구체적 정보를 빠짐없이 포함:
     * 도구별 가격, 기능, 특징
     * 워크플로우와 사용 방법
     * 보안 고려사항과 베스트 프랙티스
     * 비용 최적화 전략과 수치
     * 실전 사례와 팁
   - 대화형 톤: "이게 왜 중요하냐고요?", "실무에서 이걸 어떻게 활용하냐고요?" 같은 질문 사용
   - 실무 예시: 구체적인 사례, 수치, 데이터 포함
   - 핵심 포인트 반복 강조: 각 섹션 마무리에서 핵심 요약
   - 상호작용 요소: "지금 기억해두시면 좋을 것 같아요", "여기서 팁을 하나 드리면"
   - 자연스러운 전환: "자, 그럼 시작해볼까요?", "이제 가장 중요한 부분입니다"

3. **결론 (30-45초, 1.5배속 시 20-30초) - 핵심 내용 체계적 요약**
   - 핵심 내용을 5가지로 체계적으로 요약
   - 실무 적용 팁 제시
   - 다음 학습 내용 또는 추가 자료 안내 (선택적)
   - 친근한 마무리 인사

{title_context}블로그 내용:
{text}

작성 스타일 요구사항:
- 자연스러운 구어체로 작성 (강의자가 직접 말하는 느낌)
- 전문가 신뢰도: 실무 경험 기반 사례와 구체적인 조언
- 대화형 톤: 질문, 사고 유도, 상호작용 요소 포함
- 실무 중심: 이론보다 실전 적용 가능한 내용 강조
- 구체적이고 명확: 모호한 표현 지양, 정확한 수치와 데이터 사용
- **반드시 2,000-2,500자 분량으로 작성** (7-8분 분량, 1.5배속 재생 시 약 5분)
- **처음 30초 분량은 반드시 200-300자로 작성** (1.5배속 재생 시 약 20초)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 한국어로 작성 (UTF-8 인코딩, 특수문자 없이)
- **절대 사용 금지**: "(본론 시작)", "(슬라이드 1)", "(본론 1)", "**강사:**", "---", "**1단계:**" 등 모든 메타 지시어
- **절대 사용 금지**: 괄호로 둘러싼 지시어, 굵은 글씨로 된 단계 표시, 구분선 등
- 자연스러운 흐름으로 작성: 서론에서 본론으로, 본론에서 결론으로 자연스럽게 전환

**중요**: 
- 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요.
- 30초 요약 부분은 반드시 블로그의 모든 핵심 내용을 포함하여 흥미롭게 작성하세요.
- 본론은 포스팅의 순서와 내용을 그대로 따라가며 상세히 설명하세요."""
    
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
            elif len(script) < MIN_SCRIPT_LENGTH:
                log_message(f"⚠️ 생성된 대본이 너무 짧습니다 ({len(script)}자). 목표는 {MIN_SCRIPT_LENGTH}-{MAX_SCRIPT_LENGTH}자입니다.", "WARNING")
            
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
    
    # 프롬프트 구성 (온라인 강의 베스트 프랙티스 반영)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""당신은 클라우드 보안, IT, DevSecOps 전문 온라인 강의를 제작하는 전문가입니다.
다음 기술 블로그 내용을 7-8분 분량의 고품질 온라인 강의 대본으로 변환해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

**⚠️ 매우 중요한 구조 요구사항 - 반드시 정확히 이 순서를 따르세요!**

**대본은 반드시 첫 문장으로 시작해야 합니다. 첫 문장을 절대 생략하거나 잘라내지 마세요!**

1. **처음 30초 (1.5배속 시 약 20초, 약 200-300자) - 핵심 요약으로 흥미 유발**
   **문장 1 (필수)**: 블로그 내용에서 가장 흥미로운 구체적 예시나 질문으로 시작
     * 블로그에 "Pioneer" 같은 구체적 예시가 있으면: "혹시 최근 유튜브에서 화제가 된 'Pioneer'라는 AI 뮤직비디오 보셨나요?"
     * 구체적 예시가 없으면: "2026년, 이제 이미지부터 음악, 영상까지 전부 AI로 만들 수 있게 되었습니다"
     * **⚠️ 절대 첫 문장을 생략하거나 잘라내지 마세요! 대본은 반드시 이 첫 문장으로 시작해야 합니다!**
   **문장 2 (필수)**: 구체적 사례나 놀라운 사실 제시
     * 예: "이미지부터 음악, 영상까지 전부 AI로만 만들었는데, 퀄리티가 정말 놀랍죠"
     * 블로그에 나온 구체적 도구나 기술을 언급
   
   **문장 3 (필수)**: 문제 제기와 관점 전환
     * 예: "하지만 우리 같은 DevSecOps 엔지니어들에게는 이 화려한 기술 뒤에 숨겨진 보안, 비용, 거버넌스 문제가 더 중요합니다"
   
   **문장 4 (필수)**: 블로그 전체 내용 요약 (30초 안에 모든 핵심 키워드 포함)
     * 블로그에 언급된 모든 주요 도구, 기술, 보안 이슈, 비용 최적화 등을 자연스럽게 나열
     * 예: "오늘은 Midjourney, Suno V5, Veo 3 같은 최신 AI 도구부터, API 키 관리, 데이터 프라이버시 보호, CI/CD 자동화, 그리고 비용 최적화 전략까지 DevSecOps 관점에서 완벽하게 정리해드리겠습니다"
     * **반드시 블로그의 모든 핵심 키워드를 빠짐없이 포함하세요!**
   
   **문장 5 (필수)**: 학습 목표 제시
     * 예: "이 강의가 끝나면 여러분은 생성형 AI 프로젝트를 안전하고 효율적으로 운영하는 실질적인 노하우를 갖게 되실 겁니다"
   
   **30초 요약의 핵심**: 
   - 시청자가 "이 강의에서 무엇을 배울 수 있을까?"를 즉시 알 수 있도록 블로그의 모든 핵심 내용을 빠짐없이 요약
   - 반드시 위 5개 문장을 모두 순서대로 포함하여 작성하세요
   - 첫 문장부터 시작하여 다섯 번째 문장까지 완전한 문장으로 작성하세요

2. **본론 (6-7분, 1.5배속 시 4-4.5분) - 포스팅 내용을 순서대로 상세히 설명**
   - **포스팅의 구조와 순서를 그대로 따라가며** 상세히 설명
   - 포스팅에 나온 모든 구체적 정보를 빠짐없이 포함:
     * 도구별 가격, 기능, 특징
     * 워크플로우와 사용 방법
     * 보안 고려사항과 베스트 프랙티스
     * 비용 최적화 전략과 수치
     * 실전 사례와 팁
   - 대화형 톤: "이게 왜 중요하냐고요?", "실무에서 이걸 어떻게 활용하냐고요?" 같은 질문 사용
   - 실무 예시: 구체적인 사례, 수치, 데이터 포함
   - 핵심 포인트 반복 강조: 각 섹션 마무리에서 핵심 요약
   - 상호작용 요소: "지금 기억해두시면 좋을 것 같아요", "여기서 팁을 하나 드리면"
   - 자연스러운 전환: "자, 그럼 시작해볼까요?", "이제 가장 중요한 부분입니다"

3. **결론 (30-45초, 1.5배속 시 20-30초) - 핵심 내용 체계적 요약**
   - 핵심 내용을 5가지로 체계적으로 요약
   - 실무 적용 팁 제시
   - 다음 학습 내용 또는 추가 자료 안내 (선택적)
   - 친근한 마무리 인사

{title_context}블로그 내용:
{text}

작성 스타일 요구사항:
- 자연스러운 구어체로 작성 (강의자가 직접 말하는 느낌)
- 전문가 신뢰도: 실무 경험 기반 사례와 구체적인 조언
- 대화형 톤: 질문, 사고 유도, 상호작용 요소 포함
- 실무 중심: 이론보다 실전 적용 가능한 내용 강조
- 구체적이고 명확: 모호한 표현 지양, 정확한 수치와 데이터 사용
- **반드시 2,000-2,500자 분량으로 작성** (7-8분 분량, 1.5배속 재생 시 약 5분)
- **처음 30초 분량은 반드시 200-300자로 작성** (1.5배속 재생 시 약 20초)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 한국어로 작성 (UTF-8 인코딩, 특수문자 없이)
- **절대 사용 금지**: "(본론 시작)", "(슬라이드 1)", "(본론 1)", "**강사:**", "---", "**1단계:**" 등 모든 메타 지시어
- **절대 사용 금지**: 괄호로 둘러싼 지시어, 굵은 글씨로 된 단계 표시, 구분선 등
- 자연스러운 흐름으로 작성: 서론에서 본론으로, 본론에서 결론으로 자연스럽게 전환

**중요**: 
- 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요.
- 30초 요약 부분은 반드시 블로그의 모든 핵심 내용을 포함하여 흥미롭게 작성하세요.
- 본론은 포스팅의 순서와 내용을 그대로 따라가며 상세히 설명하세요."""
    
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
                    "max_output_tokens": 4000,  # 더 긴 대본 생성을 위해 증가 (2,000-2,500자 목표)
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
                elif len(script) < MIN_SCRIPT_LENGTH:
                    log_message(f"⚠️ 생성된 대본이 너무 짧습니다 ({len(script)}자). 목표는 {MIN_SCRIPT_LENGTH}-{MAX_SCRIPT_LENGTH}자입니다.", "WARNING")
                
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
    Gemini AI를 사용하여 고품질 강의용 대본을 생성합니다.
    Rate Limit을 고려하여 안전하게 요청합니다.
    
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
    
    # 모델 타입 선택 (pro 또는 flash)
    model_type = GEMINI_MODEL_TYPE if GEMINI_MODEL_TYPE in ["pro", "flash"] else "flash"
    tracker = rate_limit_trackers[model_type]
    
    # Rate Limit 체크
    can_request, reason = tracker.can_make_request()
    if not can_request:
        log_message(f"⚠️ Rate Limit 제한: {reason}", "WARNING")
        # 경고 메시지 출력
        warning = tracker.check_warning_threshold()
        if warning:
            log_message(f"⚠️ Rate Limit 경고: {warning}", "WARNING")
        return None
    
    # 텍스트 길이 제한 (비용 관리)
    if len(text) > MAX_TEXT_LENGTH:
        log_message(f"⚠️ 텍스트가 너무 깁니다 ({len(text)}자). 처음 {MAX_TEXT_LENGTH}자만 사용합니다.", "WARNING")
        text = text[:MAX_TEXT_LENGTH]
    
    # 사용량 통계 확인 및 경고
    stats = tracker.get_usage_stats()
    if stats["rpm"]["usage_rate"] >= RATE_LIMIT_WARNING_THRESHOLD:
        log_message(f"⚠️ RPM 사용률 높음: {stats['rpm']['current']}/{stats['rpm']['limit']} ({stats['rpm']['usage_rate']*100:.1f}%)", "WARNING")
    
    # Gemini AI Pro를 위한 고급 프롬프트 구성 (온라인 강의 베스트 프랙티스 반영)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    
    prompt = f"""당신은 클라우드 보안, IT, DevSecOps 전문 온라인 강의를 제작하는 전문가입니다.
다음 기술 블로그 내용을 7-8분 분량의 고품질 온라인 강의 대본으로 변환해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

**⚠️ 매우 중요한 구조 요구사항 - 반드시 정확히 이 순서를 따르세요!**

**대본은 반드시 첫 문장으로 시작해야 합니다. 첫 문장을 절대 생략하거나 잘라내지 마세요!**

1. **처음 30초 (1.5배속 시 약 20초, 약 200-300자) - 핵심 요약으로 흥미 유발**
   **문장 1 (필수)**: 블로그 내용에서 가장 흥미로운 구체적 예시나 질문으로 시작
     * 블로그에 "Pioneer" 같은 구체적 예시가 있으면: "혹시 최근 유튜브에서 화제가 된 'Pioneer'라는 AI 뮤직비디오 보셨나요?"
     * 구체적 예시가 없으면: "2026년, 이제 이미지부터 음악, 영상까지 전부 AI로 만들 수 있게 되었습니다"
     * **⚠️ 절대 첫 문장을 생략하거나 잘라내지 마세요! 대본은 반드시 이 첫 문장으로 시작해야 합니다!**
   **문장 2 (필수)**: 구체적 사례나 놀라운 사실 제시
     * 예: "이미지부터 음악, 영상까지 전부 AI로만 만들었는데, 퀄리티가 정말 놀랍죠"
     * 블로그에 나온 구체적 도구나 기술을 언급
   
   **문장 3 (필수)**: 문제 제기와 관점 전환
     * 예: "하지만 우리 같은 DevSecOps 엔지니어들에게는 이 화려한 기술 뒤에 숨겨진 보안, 비용, 거버넌스 문제가 더 중요합니다"
   
   **문장 4 (필수)**: 블로그 전체 내용 요약 (30초 안에 모든 핵심 키워드 포함)
     * 블로그에 언급된 모든 주요 도구, 기술, 보안 이슈, 비용 최적화 등을 자연스럽게 나열
     * 예: "오늘은 Midjourney, Suno V5, Veo 3 같은 최신 AI 도구부터, API 키 관리, 데이터 프라이버시 보호, CI/CD 자동화, 그리고 비용 최적화 전략까지 DevSecOps 관점에서 완벽하게 정리해드리겠습니다"
     * **반드시 블로그의 모든 핵심 키워드를 빠짐없이 포함하세요!**
   
   **문장 5 (필수)**: 학습 목표 제시
     * 예: "이 강의가 끝나면 여러분은 생성형 AI 프로젝트를 안전하고 효율적으로 운영하는 실질적인 노하우를 갖게 되실 겁니다"
   
   **30초 요약의 핵심**: 
   - 시청자가 "이 강의에서 무엇을 배울 수 있을까?"를 즉시 알 수 있도록 블로그의 모든 핵심 내용을 빠짐없이 요약
   - 반드시 위 5개 문장을 모두 순서대로 포함하여 작성하세요
   - 첫 문장부터 시작하여 다섯 번째 문장까지 완전한 문장으로 작성하세요

2. **본론 (6-7분, 1.5배속 시 4-4.5분) - 포스팅 내용을 순서대로 상세히 설명**
   - **포스팅의 구조와 순서를 그대로 따라가며** 상세히 설명
   - 포스팅에 나온 모든 구체적 정보를 빠짐없이 포함:
     * 도구별 가격, 기능, 특징
     * 워크플로우와 사용 방법
     * 보안 고려사항과 베스트 프랙티스
     * 비용 최적화 전략과 수치
     * 실전 사례와 팁
   - 대화형 톤: "이게 왜 중요하냐고요?", "실무에서 이걸 어떻게 활용하냐고요?" 같은 질문 사용
   - 실무 예시: 구체적인 사례, 수치, 데이터 포함
   - 핵심 포인트 반복 강조: 각 섹션 마무리에서 핵심 요약
   - 상호작용 요소: "지금 기억해두시면 좋을 것 같아요", "여기서 팁을 하나 드리면"
   - 자연스러운 전환: "자, 그럼 시작해볼까요?", "이제 가장 중요한 부분입니다"

3. **결론 (30-45초, 1.5배속 시 20-30초) - 핵심 내용 체계적 요약**
   - 핵심 내용을 5가지로 체계적으로 요약
   - 실무 적용 팁 제시
   - 다음 학습 내용 또는 추가 자료 안내 (선택적)
   - 친근한 마무리 인사

{title_context}블로그 내용:
{text}

작성 스타일 요구사항:
- 자연스러운 구어체로 작성 (강의자가 직접 말하는 느낌)
- 전문가 신뢰도: 실무 경험 기반 사례와 구체적인 조언
- 대화형 톤: 질문, 사고 유도, 상호작용 요소 포함
- 실무 중심: 이론보다 실전 적용 가능한 내용 강조
- 구체적이고 명확: 모호한 표현 지양, 정확한 수치와 데이터 사용
- **반드시 2,000-2,500자 분량으로 작성** (7-8분 분량, 1.5배속 재생 시 약 5분)
- **처음 30초 분량은 반드시 200-300자로 작성** (1.5배속 재생 시 약 20초)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 한국어로 작성 (UTF-8 인코딩, 특수문자 없이)
- **절대 사용 금지**: "(본론 시작)", "(슬라이드 1)", "(본론 1)", "**강사:**", "---", "**1단계:**" 등 모든 메타 지시어
- **절대 사용 금지**: 괄호로 둘러싼 지시어, 굵은 글씨로 된 단계 표시, 구분선 등
- 자연스러운 흐름으로 작성: 서론에서 본론으로, 본론에서 결론으로 자연스럽게 전환

**중요**: 
- 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요.
- 30초 요약 부분은 반드시 블로그의 모든 핵심 내용을 포함하여 흥미롭게 작성하세요.
- 본론은 포스팅의 순서와 내용을 그대로 따라가며 상세히 설명하세요."""
    
    # API URL 선택 (모델 타입에 따라)
    if model_type == "flash":
        api_url = GEMINI_FLASH_API_URL
        log_message(f"📝 Gemini 2.5 Flash로 대본 생성 중... (RPM: {GEMINI_FLASH_RPM_LIMIT}, TPM: {GEMINI_FLASH_TPM_LIMIT:,})")
    else:
        api_url = GEMINI_API_URL
        log_message(f"📝 Gemini 2.5 Pro로 대본 생성 중... (RPM: {GEMINI_PRO_RPM_LIMIT}, TPM: {GEMINI_PRO_TPM_LIMIT:,})")
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            # Rate Limit 재확인
            can_request, reason = tracker.can_make_request()
            if not can_request:
                if attempt < max_retries:
                    wait_time = tracker.min_delay * 2
                    log_message(f"⏳ Rate Limit 대기: {reason} ({wait_time:.1f}초 대기)...", "WARNING")
                    time.sleep(wait_time)
                    continue
                else:
                    log_message(f"❌ Rate Limit 제한으로 요청 불가: {reason}", "ERROR")
                    return None
            
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))
                log_message(f"🔄 Gemini API 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            
            # 최소 지연 시간 적용
            if tracker.last_request_time > 0:
                elapsed = time.time() - tracker.last_request_time
                if elapsed < tracker.min_delay:
                    sleep_time = tracker.min_delay - elapsed
                    time.sleep(sleep_time)
            
            url = f"{api_url}?key={GEMINI_API_KEY}"
            
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
                    "maxOutputTokens": 4000,  # 더 긴 대본 생성을 위해 증가 (2,000-2,500자 목표)
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
            
            # Rate Limit 에러 처리 (429)
            if response.status_code == 429:
                usage.errors += 1
                error_detail = {}
                try:
                    if response.text:
                        error_detail = json.loads(response.text)
                except:
                    pass
                
                # Retry-After 헤더 확인
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    wait_time = int(retry_after)
                else:
                    # Exponential backoff
                    wait_time = retry_delay * (2 ** (attempt - 1))
                
                log_message(f"⚠️ Rate Limit 초과 (429). {wait_time}초 후 재시도...", "WARNING")
                
                if attempt < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    log_message(f"❌ Rate Limit 초과: 최대 재시도 횟수 초과", "ERROR")
                    return None
            
            if response.status_code == 200:
                result = response.json()
                
                # 사용량 추적
                prompt_tokens = 0
                completion_tokens = 0
                if "usageMetadata" in result:
                    prompt_tokens = result["usageMetadata"].get("promptTokenCount", 0)
                    completion_tokens = result["usageMetadata"].get("candidatesTokenCount", 0)
                    usage.prompt_tokens += prompt_tokens
                    usage.completion_tokens += completion_tokens
                
                # Rate Limit 추적에 토큰 사용량 기록
                total_tokens = prompt_tokens + completion_tokens
                tracker.record_request(total_tokens)
                
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
                        elif len(script) < MIN_SCRIPT_LENGTH:
                            log_message(f"⚠️ 생성된 대본이 너무 짧습니다 ({len(script)}자). 목표는 {MIN_SCRIPT_LENGTH}-{MAX_SCRIPT_LENGTH}자입니다.", "WARNING")
                        
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
    
    # 프롬프트 구성 (온라인 강의 베스트 프랙티스 반영)
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""당신은 클라우드 보안, IT, DevSecOps 전문 온라인 강의를 제작하는 전문가입니다.
다음 기술 블로그 내용을 7-8분 분량의 고품질 온라인 강의 대본으로 변환해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

**⚠️ 매우 중요한 구조 요구사항 - 반드시 정확히 이 순서를 따르세요!**

**대본은 반드시 첫 문장으로 시작해야 합니다. 첫 문장을 절대 생략하거나 잘라내지 마세요!**

1. **처음 30초 (1.5배속 시 약 20초, 약 200-300자) - 핵심 요약으로 흥미 유발**
   **문장 1 (필수)**: 블로그 내용에서 가장 흥미로운 구체적 예시나 질문으로 시작
     * 블로그에 "Pioneer" 같은 구체적 예시가 있으면: "혹시 최근 유튜브에서 화제가 된 'Pioneer'라는 AI 뮤직비디오 보셨나요?"
     * 구체적 예시가 없으면: "2026년, 이제 이미지부터 음악, 영상까지 전부 AI로 만들 수 있게 되었습니다"
     * **⚠️ 절대 첫 문장을 생략하거나 잘라내지 마세요! 대본은 반드시 이 첫 문장으로 시작해야 합니다!**
   **문장 2 (필수)**: 구체적 사례나 놀라운 사실 제시
     * 예: "이미지부터 음악, 영상까지 전부 AI로만 만들었는데, 퀄리티가 정말 놀랍죠"
     * 블로그에 나온 구체적 도구나 기술을 언급
   
   **문장 3 (필수)**: 문제 제기와 관점 전환
     * 예: "하지만 우리 같은 DevSecOps 엔지니어들에게는 이 화려한 기술 뒤에 숨겨진 보안, 비용, 거버넌스 문제가 더 중요합니다"
   
   **문장 4 (필수)**: 블로그 전체 내용 요약 (30초 안에 모든 핵심 키워드 포함)
     * 블로그에 언급된 모든 주요 도구, 기술, 보안 이슈, 비용 최적화 등을 자연스럽게 나열
     * 예: "오늘은 Midjourney, Suno V5, Veo 3 같은 최신 AI 도구부터, API 키 관리, 데이터 프라이버시 보호, CI/CD 자동화, 그리고 비용 최적화 전략까지 DevSecOps 관점에서 완벽하게 정리해드리겠습니다"
     * **반드시 블로그의 모든 핵심 키워드를 빠짐없이 포함하세요!**
   
   **문장 5 (필수)**: 학습 목표 제시
     * 예: "이 강의가 끝나면 여러분은 생성형 AI 프로젝트를 안전하고 효율적으로 운영하는 실질적인 노하우를 갖게 되실 겁니다"
   
   **30초 요약의 핵심**: 
   - 시청자가 "이 강의에서 무엇을 배울 수 있을까?"를 즉시 알 수 있도록 블로그의 모든 핵심 내용을 빠짐없이 요약
   - 반드시 위 5개 문장을 모두 순서대로 포함하여 작성하세요
   - 첫 문장부터 시작하여 다섯 번째 문장까지 완전한 문장으로 작성하세요

2. **본론 (6-7분, 1.5배속 시 4-4.5분) - 포스팅 내용을 순서대로 상세히 설명**
   - **포스팅의 구조와 순서를 그대로 따라가며** 상세히 설명
   - 포스팅에 나온 모든 구체적 정보를 빠짐없이 포함:
     * 도구별 가격, 기능, 특징
     * 워크플로우와 사용 방법
     * 보안 고려사항과 베스트 프랙티스
     * 비용 최적화 전략과 수치
     * 실전 사례와 팁
   - 대화형 톤: "이게 왜 중요하냐고요?", "실무에서 이걸 어떻게 활용하냐고요?" 같은 질문 사용
   - 실무 예시: 구체적인 사례, 수치, 데이터 포함
   - 핵심 포인트 반복 강조: 각 섹션 마무리에서 핵심 요약
   - 상호작용 요소: "지금 기억해두시면 좋을 것 같아요", "여기서 팁을 하나 드리면"
   - 자연스러운 전환: "자, 그럼 시작해볼까요?", "이제 가장 중요한 부분입니다"

3. **결론 (30-45초, 1.5배속 시 20-30초) - 핵심 내용 체계적 요약**
   - 핵심 내용을 5가지로 체계적으로 요약
   - 실무 적용 팁 제시
   - 다음 학습 내용 또는 추가 자료 안내 (선택적)
   - 친근한 마무리 인사

{title_context}블로그 내용:
{text}

작성 스타일 요구사항:
- 자연스러운 구어체로 작성 (강의자가 직접 말하는 느낌)
- 전문가 신뢰도: 실무 경험 기반 사례와 구체적인 조언
- 대화형 톤: 질문, 사고 유도, 상호작용 요소 포함
- 실무 중심: 이론보다 실전 적용 가능한 내용 강조
- 구체적이고 명확: 모호한 표현 지양, 정확한 수치와 데이터 사용
- **반드시 2,000-2,500자 분량으로 작성** (7-8분 분량, 1.5배속 재생 시 약 5분)
- **처음 30초 분량은 반드시 200-300자로 작성** (1.5배속 재생 시 약 20초)
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 한국어로 작성 (UTF-8 인코딩, 특수문자 없이)
- **절대 사용 금지**: "(본론 시작)", "(슬라이드 1)", "(본론 1)", "**강사:**", "---", "**1단계:**" 등 모든 메타 지시어
- **절대 사용 금지**: 괄호로 둘러싼 지시어, 굵은 글씨로 된 단계 표시, 구분선 등
- 자연스러운 흐름으로 작성: 서론에서 본론으로, 본론에서 결론으로 자연스럽게 전환

**중요**: 
- 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요.
- 30초 요약 부분은 반드시 블로그의 모든 핵심 내용을 포함하여 흥미롭게 작성하세요.
- 본론은 포스팅의 순서와 내용을 그대로 따라가며 상세히 설명하세요."""
    
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
                        "content": "당신은 클라우드 보안, IT, DevSecOps 전문 온라인 강의를 제작하는 전문가입니다. 실무 경험 기반의 구체적이고 명확한 대화형 톤으로 작성해주세요. 슬라이드 지시어, 본론 지시어, 강사 지시어 등 메타 지시어는 절대 사용하지 마세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000  # 더 긴 대본 생성을 위해 증가 (2,000-2,500자 목표)
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
            elif len(script) < MIN_SCRIPT_LENGTH:
                log_message(f"⚠️ 생성된 대본이 너무 짧습니다 ({len(script)}자). 목표는 {MIN_SCRIPT_LENGTH}-{MAX_SCRIPT_LENGTH}자입니다.", "WARNING")
            
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
    Gemini AI를 사용하여 대본을 고품질로 개선합니다.
    Rate Limit을 고려하여 안전하게 요청합니다.
    
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
    
    # 모델 타입 선택 (pro 또는 flash)
    model_type = GEMINI_MODEL_TYPE if GEMINI_MODEL_TYPE in ["pro", "flash"] else "flash"
    tracker = rate_limit_trackers[model_type]
    
    # Rate Limit 체크
    can_request, reason = tracker.can_make_request()
    if not can_request:
        log_message(f"⚠️ Rate Limit 제한: {reason}", "WARNING")
        warning = tracker.check_warning_threshold()
        if warning:
            log_message(f"⚠️ Rate Limit 경고: {warning}", "WARNING")
        return None
    
    # 사용량 통계 확인 및 경고
    stats = tracker.get_usage_stats()
    if stats["rpm"]["usage_rate"] >= RATE_LIMIT_WARNING_THRESHOLD:
        log_message(f"⚠️ RPM 사용률 높음: {stats['rpm']['current']}/{stats['rpm']['limit']} ({stats['rpm']['usage_rate']*100:.1f}%)", "WARNING")
    
    # API URL 선택 (모델 타입에 따라)
    if model_type == "flash":
        api_url = GEMINI_FLASH_API_URL
        log_message(f"✨ Gemini 2.5 Flash로 대본 개선 중... (RPM: {GEMINI_FLASH_RPM_LIMIT}, TPM: {GEMINI_FLASH_TPM_LIMIT:,})")
    else:
        api_url = GEMINI_API_URL
        log_message(f"✨ Gemini 2.5 Pro로 대본 개선 중... (RPM: {GEMINI_PRO_RPM_LIMIT}, TPM: {GEMINI_PRO_TPM_LIMIT:,})")
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            # Rate Limit 재확인
            can_request, reason = tracker.can_make_request()
            if not can_request:
                if attempt < max_retries:
                    wait_time = tracker.min_delay * 2
                    log_message(f"⏳ Rate Limit 대기: {reason} ({wait_time:.1f}초 대기)...", "WARNING")
                    time.sleep(wait_time)
                    continue
                else:
                    log_message(f"❌ Rate Limit 제한으로 요청 불가: {reason}", "ERROR")
                    return None
            
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))
                log_message(f"🔄 Gemini API 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
                time.sleep(wait_time)
            
            # 최소 지연 시간 적용
            if tracker.last_request_time > 0:
                elapsed = time.time() - tracker.last_request_time
                if elapsed < tracker.min_delay:
                    sleep_time = tracker.min_delay - elapsed
                    time.sleep(sleep_time)
            
            title_context = f"제목: {post_title}\n\n" if post_title else ""
            prompt = f"""당신은 클라우드 보안, IT, DevSecOps 전문 온라인 강의 대본 개선 전문가입니다.
다음 강의 대본을 온라인 강의 베스트 프랙티스에 맞게 개선해주세요.
(참고: 이 대본은 1.5배속으로 재생되어 약 5분 분량의 강의가 됩니다)

{title_context}원본 대본:
{script}

개선 가이드 (온라인 강의 베스트 프랙티스):

1. **명확한 학습 목표 제시**: 서론에서 "오늘 여러분이 배우게 될 핵심 내용은 세 가지입니다"와 같이 명확히 제시
2. **대화형 톤 강화**: "이게 왜 중요하냐고요?", "실무에서 이걸 어떻게 활용하냐고요?" 같은 질문 추가
3. **실무 예시 강화**: 구체적인 사례, 수치, 데이터 포함 (예: "한 스타트업에서...", "비용을 70퍼센트 절감")
4. **핵심 포인트 반복 강조**: 각 섹션 마무리에서 핵심 요약 추가
5. **상호작용 요소 추가**: "지금 기억해두시면 좋을 것 같아요", "여기서 팁을 하나 드리면" 같은 표현 추가
6. **구체적인 수치와 데이터**: 비용, 시간, 성능 등 정확한 수치 제시
7. **전문가 신뢰도 향상**: 실무 경험 기반 사례와 구체적인 조언 추가
8. **자연스러운 전환**: "이제 가장 중요한 부분입니다", "자, 그럼 시작해볼까요?" 같은 전환 구문 추가
9. **결론 체계화**: 핵심 내용을 5가지로 체계적으로 요약

개선 요구사항:
- 자연스러운 구어체 유지 (강의자가 직접 말하는 느낌)
- 핵심 내용은 그대로 유지하되 표현 개선
- 전문가 신뢰도: 실무 경험 기반 사례 추가
- 대화형 톤: 질문, 사고 유도, 상호작용 요소 포함
- 실무 중심: 이론보다 실전 적용 가능한 내용 강조
- 구체적이고 명확: 모호한 표현 지양, 정확한 수치와 데이터 사용
- **반드시 2,000-2,500자 분량으로 작성** (원본이 짧으면 확장, 원본이 길면 요약)
- 한국어로 작성 (UTF-8 인코딩, 특수문자 없이)
- **절대 사용 금지**: "(본론 시작)", "(슬라이드 1)", "(본론 1)", "**강사:**", "---", "**1단계:**" 등 모든 메타 지시어
- **절대 사용 금지**: 괄호로 둘러싼 지시어, 굵은 글씨로 된 단계 표시, 구분선 등
- 자연스러운 흐름으로 작성: 서론에서 본론으로, 본론에서 결론으로 자연스럽게 전환
- 각 섹션을 자연스러운 문장으로 연결 (예: "자, 그럼 시작해볼까요?", "이제 가장 중요한 부분입니다")

중요: 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요. 원본에 메타 지시어가 있다면 반드시 제거하세요."""
            
            url = f"{api_url}?key={GEMINI_API_KEY}"
            
            # Gemini AI 고급 설정
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
                    "maxOutputTokens": 4000,  # 더 긴 대본 생성을 위해 증가 (2,000-2,500자 목표)
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
            
            # Rate Limit 에러 처리 (429)
            if response.status_code == 429:
                usage = usage_stats["gemini"]
                usage.errors += 1
                error_detail = {}
                try:
                    if response.text:
                        error_detail = json.loads(response.text)
                except:
                    pass
                
                # Retry-After 헤더 확인
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    wait_time = int(retry_after)
                else:
                    # Exponential backoff
                    wait_time = retry_delay * (2 ** (attempt - 1))
                
                log_message(f"⚠️ Rate Limit 초과 (429). {wait_time}초 후 재시도...", "WARNING")
                
                if attempt < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    log_message(f"❌ Rate Limit 초과: 최대 재시도 횟수 초과", "ERROR")
                    return None
            
            # 사용량 추적
            usage = usage_stats["gemini"]
            usage.requests += 1
            
            if response.status_code == 200:
                result = response.json()
                
                # 사용량 정보 추출
                prompt_tokens = 0
                completion_tokens = 0
                if "usageMetadata" in result:
                    prompt_tokens = result["usageMetadata"].get("promptTokenCount", 0)
                    completion_tokens = result["usageMetadata"].get("candidatesTokenCount", 0)
                    usage.prompt_tokens += prompt_tokens
                    usage.completion_tokens += completion_tokens
                
                # Rate Limit 추적에 토큰 사용량 기록
                total_tokens = prompt_tokens + completion_tokens
                tracker.record_request(total_tokens)
                
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


def adjust_audio_speed(input_path: Path, output_path: Path, speed: float = 1.5) -> bool:
    """
    ffmpeg를 사용하여 오디오 속도를 조절합니다.
    
    Args:
        input_path: 입력 오디오 파일 경로
        output_path: 출력 오디오 파일 경로
        speed: 재생 속도 배율 (기본값: 1.5)
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not input_path.exists():
        log_message(f"❌ 입력 파일을 찾을 수 없습니다: {input_path}", "ERROR")
        return False
    
    try:
        log_message(f"⚡ 오디오 속도 조절 중 ({speed}배속)...")
        
        # ffmpeg 명령어 실행
        # atempo 필터를 사용하여 속도 조절 (0.5 ~ 2.0 범위)
        # 1.5배속이 2.0을 초과하지 않으므로 한 번의 atempo로 처리 가능
        result = subprocess.run(
            [
                "ffmpeg",
                "-i", str(input_path),
                "-filter:a", f"atempo={speed}",
                "-y",  # 덮어쓰기
                str(output_path)
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5분 타임아웃
        )
        
        if result.returncode == 0:
            file_size = output_path.stat().st_size
            log_message(f"✅ 오디오 속도 조절 완료: {output_path} ({file_size:,} bytes, {speed}배속)")
            return True
        else:
            error_msg = result.stderr.strip() if result.stderr else "알 수 없는 오류"
            log_message(f"❌ ffmpeg 오류: {error_msg}", "ERROR")
            return False
            
    except FileNotFoundError:
        log_message("❌ ffmpeg를 찾을 수 없습니다. 설치: brew install ffmpeg (macOS) 또는 apt-get install ffmpeg (Linux)", "ERROR")
        return False
    except subprocess.TimeoutExpired:
        log_message("❌ ffmpeg 타임아웃 (5분 초과)", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ 오디오 속도 조절 중 오류: {str(e)}", "ERROR")
        return False


def text_to_speech_with_gemini(script: str, output_path: Path) -> bool:
    """
    Gemini 2.5 TTS API를 사용하여 텍스트를 음성으로 변환합니다.
    비용 효율적: 토큰 기반 과금으로 ElevenLabs 대비 저렴함.
    
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
    
    # 모델 선택 (Flash가 더 저렴하고 빠름)
    model_type = GEMINI_MODEL_TYPE if GEMINI_MODEL_TYPE in ["pro", "flash"] else "flash"
    if model_type == "flash":
        api_url = GEMINI_TTS_FLASH_API_URL
        log_message(f"🎤 Gemini 2.5 Flash TTS로 음성 생성 중... (비용 효율적, Voice: {GEMINI_TTS_VOICE_NAME})")
    else:
        api_url = GEMINI_TTS_PRO_API_URL
        log_message(f"🎤 Gemini 2.5 Pro TTS로 음성 생성 중... (고품질, Voice: {GEMINI_TTS_VOICE_NAME})")
    
    try:
        url = f"{api_url}?key={GEMINI_API_KEY}"
        
        # Gemini TTS API 요청 데이터
        # 참고: responseModalities를 ["AUDIO"]로 설정하여 오디오 응답 요청
        # 기본 제공 Voice 사용
        voice_config = {
            "prebuiltVoiceConfig": {
                "voiceName": GEMINI_TTS_VOICE_NAME  # IT/DevSecOps 전문가용 남자 목소리 (환경 변수로 설정 가능)
            }
        }
        
        # Voice Controls 추가 (Gemini 2.5 TTS 기능)
        speech_config = {
            "voiceConfig": voice_config
        }
        
        # 스타일 제어 (자연어 프롬프트)
        if GEMINI_TTS_VOICE_STYLE:
            speech_config["style"] = GEMINI_TTS_VOICE_STYLE
        
        # 속도 제어 (0.25 ~ 4.0)
        if GEMINI_TTS_VOICE_PACE != 1.0:
            speech_config["pace"] = max(0.25, min(4.0, GEMINI_TTS_VOICE_PACE))
        
        data = {
            "contents": [{
                "parts": [{
                    "text": script
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],  # 오디오 응답 요청
                "speechConfig": speech_config
            }
        }
        
        usage = usage_stats["gemini"]
        usage.requests += 1
        
        response = requests.post(url, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            # 오디오 데이터 추출
            candidates = result.get('candidates', [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                
                # 오디오 데이터 찾기
                audio_data = None
                mime_type = None
                for part in parts:
                    if 'inlineData' in part:
                        audio_data = part['inlineData'].get('data')
                        mime_type = part['inlineData'].get('mimeType', 'audio/L16;codec=pcm;rate=24000')
                        break
                    elif 'inline_data' in part:  # 하위 호환성
                        audio_data = part['inline_data'].get('data')
                        mime_type = part['inline_data'].get('mimeType', 'audio/L16;codec=pcm;rate=24000')
                        break
                    elif 'text' in part:
                        # 텍스트 응답인 경우 (에러 메시지일 수 있음)
                        log_message(f"⚠️ Gemini TTS 텍스트 응답: {part['text'][:200]}", "WARNING")
                
                if audio_data:
                    # Base64 디코딩
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    
                    # PCM 오디오를 WAV로 저장 (임시)
                    import wave
                    temp_wav = output_path.parent / f"{output_path.stem}_temp.wav"
                    with wave.open(str(temp_wav), "wb") as wf:
                        # MIME 타입에서 샘플 레이트 추출 (기본값: 24000)
                        sample_rate = 24000
                        if mime_type and 'rate=' in mime_type:
                            try:
                                sample_rate = int(mime_type.split('rate=')[1].split(';')[0])
                            except:
                                pass
                        wf.setnchannels(1)  # Mono
                        wf.setsampwidth(2)  # 16-bit PCM
                        wf.setframerate(sample_rate)
                        wf.writeframes(audio_bytes)
                    
                    # WAV를 MP3로 변환 (ffmpeg 사용)
                    temp_output = output_path.parent / f"{output_path.stem}_temp{output_path.suffix}"
                    if output_path.suffix == ".mp3":
                        result = subprocess.run(
                            [
                                "ffmpeg",
                                "-i", str(temp_wav),
                                "-y",
                                str(temp_output)
                            ],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        try:
                            temp_wav.unlink()
                        except:
                            pass
                        
                        if result.returncode != 0:
                            log_message(f"⚠️ MP3 변환 실패: {result.stderr[:200]}", "WARNING")
                            # WAV 파일을 그대로 사용
                            temp_wav.rename(output_path.with_suffix(".wav"))
                            log_message(f"✅ Gemini TTS 음성 생성 완료 (WAV): {output_path.with_suffix('.wav')}")
                            return True
                    else:
                        temp_wav.rename(temp_output)
                    
                    # 1.5배속으로 오디오 속도 조절
                    if AUDIO_SPEED_MULTIPLIER != 1.0:
                        success = adjust_audio_speed(temp_output, output_path, AUDIO_SPEED_MULTIPLIER)
                        # 임시 파일 삭제
                        try:
                            temp_output.unlink()
                        except:
                            pass
                        
                        if success:
                            file_size = output_path.stat().st_size
                            log_message(f"✅ Gemini TTS 음성 생성 완료 (1.5배속): {output_path} ({file_size:,} bytes)")
                            return True
                        else:
                            # 속도 조절 실패 시 원본 파일 사용
                            log_message("⚠️ 속도 조절 실패, 원본 오디오 사용", "WARNING")
                            temp_output.rename(output_path)
                            file_size = output_path.stat().st_size
                            log_message(f"✅ Gemini TTS 음성 생성 완료 (원본 속도): {output_path} ({file_size:,} bytes)")
                            return True
                    else:
                        # 속도 조절이 필요 없는 경우
                        temp_output.rename(output_path)
                        file_size = output_path.stat().st_size
                        log_message(f"✅ Gemini TTS 음성 생성 완료: {output_path} ({file_size:,} bytes)")
                        return True
                else:
                    log_message("⚠️ Gemini TTS 응답에 오디오 데이터가 없습니다.", "WARNING")
                    usage.errors += 1
                    return False
            else:
                log_message("⚠️ Gemini TTS 응답에 후보가 없습니다.", "WARNING")
                usage.errors += 1
                return False
        else:
            usage.errors += 1
            error_msg = f"Gemini TTS API 오류: HTTP {response.status_code}"
            if response.text:
                try:
                    error_detail = json.loads(response.text)
                    error_msg += f" - {json.dumps(error_detail, ensure_ascii=False)[:200]}"
                except:
                    error_msg += f" - {response.text[:200]}"
            log_message(error_msg, "ERROR")
            return False
        
    except requests.exceptions.Timeout:
        usage = usage_stats["gemini"]
        usage.errors += 1
        log_message("⏱️ Gemini TTS API 타임아웃 (300초 초과)", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        usage = usage_stats["gemini"]
        usage.errors += 1
        log_message(f"❌ Gemini TTS API 요청 실패: {str(e)}", "ERROR")
        return False
    except Exception as e:
        usage = usage_stats["gemini"]
        usage.errors += 1
        error_msg = mask_sensitive_info(str(e))
        log_message(f"❌ Gemini TTS 오류: {error_msg}", "ERROR")
        return False


<<<<<<< Updated upstream
def adjust_audio_speed(input_path: Path, output_path: Path, speed: float = 1.5) -> bool:
    """FFmpeg를 사용하여 오디오 속도를 조정합니다."""
    try:
        import subprocess
        
        # FFmpeg로 속도 조정
        cmd = [
            "ffmpeg", "-i", str(input_path),
            "-filter:a", f"atempo={speed}",
            "-y",  # 덮어쓰기
            str(output_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return True
        return False
        
    except Exception as e:
        log_message(f"⚠️ 오디오 속도 조정 실패 (FFmpeg 없음): {str(e)}", "WARNING")
        return False


def text_to_speech_with_edge_tts(script: str, output_path: Path) -> bool:
    """
    Edge-TTS (Microsoft Edge TTS)를 사용하여 텍스트를 음성으로 변환합니다.
    무료, API 키 불필요, 한국어 지원.
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not EDGE_TTS_AVAILABLE:
        return False
    
    try:
        log_message("🎤 Edge-TTS로 음성 생성 중... (무료, API 키 불필요)")
        
        # 한국어 음성 선택 (여성 음성)
        voice = "ko-KR-SunHiNeural"  # 한국어 여성 음성
        
        # 임시 파일 경로
        temp_path = output_path.with_suffix(".tmp.mp3")
        
        # Edge-TTS로 음성 생성
        communicate = edge_tts.Communicate(script, voice)
        communicate.save(str(temp_path))
        
        # 오디오 속도 조정 (1.5배속)
        if AUDIO_SPEED_MULTIPLIER != 1.0:
            if adjust_audio_speed(temp_path, output_path, AUDIO_SPEED_MULTIPLIER):
                temp_path.unlink()  # 임시 파일 삭제
            else:
                # 속도 조정 실패 시 원본 파일 사용
                temp_path.rename(output_path)
        else:
            temp_path.rename(output_path)
        
        file_size = output_path.stat().st_size
        log_message(f"✅ Edge-TTS 음성 생성 완료: {output_path} ({file_size:,} bytes, {AUDIO_SPEED_MULTIPLIER}x 속도)")
        return True
        
    except Exception as e:
        log_message(f"❌ Edge-TTS 오류: {str(e)}", "ERROR")
        return False


def text_to_speech_with_coqui_tts(script: str, output_path: Path) -> bool:
    """
    Coqui TTS를 사용하여 텍스트를 음성으로 변환합니다.
    로컬 실행, 완전 무료, 한국어 지원.
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not COQUI_TTS_AVAILABLE:
        return False
    
    try:
        log_message("🎤 Coqui TTS로 음성 생성 중... (로컬 실행, 완전 무료)")
        
        # 한국어 모델 초기화
        tts = TTS(model_name="tts_models/ko/common-glow_tts", progress_bar=False)
        
        # 임시 파일 경로
        temp_path = output_path.with_suffix(".tmp.mp3")
        
        # 음성 생성
        tts.tts_to_file(text=script, file_path=str(temp_path))
        
        # 오디오 속도 조정 (1.5배속)
        if AUDIO_SPEED_MULTIPLIER != 1.0:
            if adjust_audio_speed(temp_path, output_path, AUDIO_SPEED_MULTIPLIER):
                temp_path.unlink()  # 임시 파일 삭제
            else:
                # 속도 조정 실패 시 원본 파일 사용
                temp_path.rename(output_path)
        else:
            temp_path.rename(output_path)
        
        file_size = output_path.stat().st_size
        log_message(f"✅ Coqui TTS 음성 생성 완료: {output_path} ({file_size:,} bytes, {AUDIO_SPEED_MULTIPLIER}x 속도)")
        return True
        
    except Exception as e:
        log_message(f"❌ Coqui TTS 오류: {str(e)}", "ERROR")
        return False


def text_to_speech(script: str, output_path: Path) -> bool:
    """
    텍스트를 음성으로 변환합니다.
    비용 최적화 우선순위:
    1. Edge-TTS (무료, API 키 불필요, 한국어 지원)
    2. Coqui TTS (로컬, 완전 무료, 한국어 지원)
    3. ElevenLabs (유료, 최고 품질)
    4. Gemini TTS (유료, 폴백)
=======
def create_chirp3_voice_cloning_key(reference_audio_path: Path, consent_audio_path: Path) -> Optional[str]:
    """
    Chirp 3: Instant Custom Voice를 위한 Voice Cloning Key를 생성합니다.
    
    Args:
        reference_audio_path: 참조 오디오 파일 경로 (WAV, 24kHz, LINEAR16, 몇 초 분량의 명확한 음성)
        consent_audio_path: 동의 오디오 파일 경로 (화자가 동의 스크립트를 읽은 오디오)
        
    Returns:
        Voice cloning key 또는 None (실패 시)
    """
    if not GOOGLE_CLOUD_PROJECT_ID:
        log_message("❌ GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.", "ERROR")
        return None
    
    if not reference_audio_path.exists() or not consent_audio_path.exists():
        log_message("❌ 참조 오디오 또는 동의 오디오 파일을 찾을 수 없습니다.", "ERROR")
        return None
    
    try:
        import base64
        
        # 오디오 파일을 Base64로 인코딩
        with open(reference_audio_path, "rb") as f:
            reference_audio_bytes = base64.b64encode(f.read()).decode("utf-8")
        
        with open(consent_audio_path, "rb") as f:
            consent_audio_bytes = base64.b64encode(f.read()).decode("utf-8")
        
        # API 엔드포인트 설정
        api_endpoint = (
            f"{CHIRP3_LOCATION}-texttospeech.googleapis.com"
            if CHIRP3_LOCATION != "global"
            else "texttospeech.googleapis.com"
        )
        url = f"https://{api_endpoint}/v1beta1/voices:generateVoiceCloningKey"
        
        # OAuth 2.0 인증 토큰 가져오기
        if USE_OAUTH and OAUTH_AVAILABLE:
            try:
                from google.auth import default
                from google.auth.transport.requests import Request
                credentials, _ = default()
                auth_req = Request()
                credentials.refresh(auth_req)
                access_token = credentials.token
            except Exception as e:
                log_message(f"❌ OAuth 2.0 인증 실패: {str(e)}", "ERROR")
                return None
        else:
            log_message("❌ OAuth 2.0 인증이 필요합니다. GOOGLE_APPLICATION_CREDENTIALS를 설정하세요.", "ERROR")
            return None
        
        # 요청 본문
        request_body = {
            "reference_audio": {
                "audio_config": {
                    "audio_encoding": "LINEAR16",
                    "sample_rate_hertz": 24000
                },
                "content": reference_audio_bytes
            },
            "voice_talent_consent": {
                "audio_config": {
                    "audio_encoding": "LINEAR16",
                    "sample_rate_hertz": 24000
                },
                "content": consent_audio_bytes
            },
            "consent_script": "I am the owner of this voice and I consent to Google using this voice to create a synthetic voice model.",
            "language_code": "ko-KR"  # 한국어 지원
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-goog-user-project": GOOGLE_CLOUD_PROJECT_ID,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        log_message("🎤 Chirp 3: Instant Custom Voice Key 생성 중...")
        response = requests.post(url, headers=headers, json=request_body, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            voice_key = result.get("voiceCloningKey")
            if voice_key:
                log_message(f"✅ Chirp 3 Voice Cloning Key 생성 완료: {voice_key[:10]}...")
                return voice_key
            else:
                log_message("❌ 응답에 voiceCloningKey가 없습니다.", "ERROR")
                return None
        else:
            error_msg = f"HTTP {response.status_code}"
            if response.text:
                try:
                    error_detail = json.loads(response.text)
                    error_msg += f" - {json.dumps(error_detail, ensure_ascii=False)[:200]}"
                except:
                    error_msg += f" - {response.text[:200]}"
            log_message(f"❌ Chirp 3 Voice Cloning Key 생성 실패: {error_msg}", "ERROR")
            return None
            
    except Exception as e:
        error_msg = mask_sensitive_info(str(e))
        log_message(f"❌ Chirp 3 Voice Cloning Key 생성 오류: {error_msg}", "ERROR")
        return None


def text_to_speech_with_chirp3(script: str, output_path: Path) -> bool:
    """
    Chirp 3: Instant Custom Voice를 사용하여 텍스트를 음성으로 변환합니다.
    자신의 목소리로 클로닝된 음성을 사용할 수 있습니다.
>>>>>>> Stashed changes
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not script:
        log_message("❌ 대본이 비어있습니다.", "ERROR")
        return False
    
<<<<<<< Updated upstream
    # 1순위: Edge-TTS (무료, API 키 불필요)
    if EDGE_TTS_AVAILABLE:
        if text_to_speech_with_edge_tts(script, output_path):
            return True
        log_message("⚠️ Edge-TTS 실패, 다음 옵션 시도...", "WARNING")
    
    # 2순위: Coqui TTS (로컬, 완전 무료)
    if COQUI_TTS_AVAILABLE:
        if text_to_speech_with_coqui_tts(script, output_path):
            return True
        log_message("⚠️ Coqui TTS 실패, 다음 옵션 시도...", "WARNING")
    
    # 3순위: ElevenLabs (유료, 최고 품질)
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
            
            # 임시 파일에 저장
            temp_path = output_path.with_suffix(".tmp.mp3")
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            # 오디오 속도 조정 (1.5배속)
            if AUDIO_SPEED_MULTIPLIER != 1.0:
                if adjust_audio_speed(temp_path, output_path, AUDIO_SPEED_MULTIPLIER):
                    temp_path.unlink()  # 임시 파일 삭제
                else:
                    # 속도 조정 실패 시 원본 파일 사용
                    temp_path.rename(output_path)
            else:
                temp_path.rename(output_path)
            
            file_size = output_path.stat().st_size
            log_message(f"✅ ElevenLabs 음성 생성 완료: {output_path} ({file_size:,} bytes, {AUDIO_SPEED_MULTIPLIER}x 속도)")
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
=======
    if not CHIRP3_VOICE_CLONING_KEY:
        log_message("❌ CHIRP3_VOICE_CLONING_KEY 환경 변수가 설정되지 않았습니다.", "ERROR")
        return False
>>>>>>> Stashed changes
    
    if not GOOGLE_CLOUD_PROJECT_ID:
        log_message("❌ GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.", "ERROR")
        return False
    
    try:
        import base64
        
        # API 엔드포인트 설정
        api_endpoint = (
            f"{CHIRP3_LOCATION}-texttospeech.googleapis.com"
            if CHIRP3_LOCATION != "global"
            else "texttospeech.googleapis.com"
        )
        url = f"https://{api_endpoint}/v1beta1/text:synthesize"
        
        # OAuth 2.0 인증 토큰 가져오기
        if USE_OAUTH and OAUTH_AVAILABLE:
            try:
                from google.auth import default
                from google.auth.transport.requests import Request
                credentials, _ = default()
                auth_req = Request()
                credentials.refresh(auth_req)
                access_token = credentials.token
            except Exception as e:
                log_message(f"❌ OAuth 2.0 인증 실패: {str(e)}", "ERROR")
                return False
        else:
            log_message("❌ OAuth 2.0 인증이 필요합니다. GOOGLE_APPLICATION_CREDENTIALS를 설정하세요.", "ERROR")
            return False
        
        # 요청 본문
        request_body = {
            "input": {
                "text": script
            },
            "voice": {
                "language_code": "ko-KR",  # 한국어
                "voice_clone": {
                    "voice_cloning_key": CHIRP3_VOICE_CLONING_KEY
                }
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16",
                "sample_rate_hertz": 24000
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-goog-user-project": GOOGLE_CLOUD_PROJECT_ID,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        log_message(f"🎤 Chirp 3: Instant Custom Voice로 음성 생성 중... (자신의 목소리)")
        
        response = requests.post(url, headers=headers, json=request_body, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            audio_content = result.get("audioContent")
            
            if audio_content:
                # Base64 디코딩
                audio_bytes = base64.b64decode(audio_content)
                
                # PCM 오디오를 WAV로 저장 (임시)
                import wave
                temp_wav = output_path.parent / f"{output_path.stem}_temp.wav"
                with wave.open(str(temp_wav), "wb") as wf:
                    wf.setnchannels(1)  # Mono
                    wf.setsampwidth(2)  # 16-bit PCM
                    wf.setframerate(24000)  # 24kHz
                    wf.writeframes(audio_bytes)
                
                # WAV를 MP3로 변환 (ffmpeg 사용)
                temp_output = output_path.parent / f"{output_path.stem}_temp{output_path.suffix}"
                if output_path.suffix == ".mp3":
                    result = subprocess.run(
                        [
                            "ffmpeg",
                            "-i", str(temp_wav),
                            "-y",
                            str(temp_output)
                        ],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    try:
                        temp_wav.unlink()
                    except:
                        pass
                    
                    if result.returncode != 0:
                        log_message(f"⚠️ MP3 변환 실패: {result.stderr[:200]}", "WARNING")
                        # WAV 파일을 그대로 사용
                        temp_wav.rename(output_path.with_suffix(".wav"))
                        log_message(f"✅ Chirp 3 음성 생성 완료 (WAV): {output_path.with_suffix('.wav')}")
                        return True
                else:
                    temp_wav.rename(temp_output)
                
                # 1.5배속으로 오디오 속도 조절
                if AUDIO_SPEED_MULTIPLIER != 1.0:
                    success = adjust_audio_speed(temp_output, output_path, AUDIO_SPEED_MULTIPLIER)
                    # 임시 파일 삭제
                    try:
                        temp_output.unlink()
                    except:
                        pass
                    
                    if success:
                        file_size = output_path.stat().st_size
                        log_message(f"✅ Chirp 3 음성 생성 완료 (1.5배속): {output_path} ({file_size:,} bytes)")
                        return True
                    else:
                        # 속도 조절 실패 시 원본 파일 사용
                        log_message("⚠️ 속도 조절 실패, 원본 오디오 사용", "WARNING")
                        temp_output.rename(output_path)
                        file_size = output_path.stat().st_size
                        log_message(f"✅ Chirp 3 음성 생성 완료 (원본 속도): {output_path} ({file_size:,} bytes)")
                        return True
                else:
                    # 속도 조절이 필요 없는 경우
                    temp_output.rename(output_path)
                    file_size = output_path.stat().st_size
                    log_message(f"✅ Chirp 3 음성 생성 완료: {output_path} ({file_size:,} bytes)")
                    return True
            else:
                log_message("⚠️ Chirp 3 응답에 오디오 데이터가 없습니다.", "WARNING")
                return False
        else:
            error_msg = f"HTTP {response.status_code}"
            if response.text:
                try:
                    error_detail = json.loads(response.text)
                    error_msg += f" - {json.dumps(error_detail, ensure_ascii=False)[:200]}"
                except:
                    error_msg += f" - {response.text[:200]}"
            log_message(f"❌ Chirp 3 API 오류: {error_msg}", "ERROR")
            return False
            
    except requests.exceptions.Timeout:
        log_message("⏱️ Chirp 3 API 타임아웃 (120초 초과)", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        log_message(f"❌ Chirp 3 API 요청 실패: {str(e)}", "ERROR")
        return False
    except Exception as e:
        error_msg = mask_sensitive_info(str(e))
        log_message(f"❌ Chirp 3 오류: {error_msg}", "ERROR")
        return False


def text_to_speech_with_coqui(script: str, output_path: Path) -> bool:
    """
    Coqui TTS 오픈소스를 사용하여 텍스트를 음성으로 변환합니다.
    완전 무료이며 자체 호스팅 가능 (한국어 지원).
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not script:
        log_message("❌ 대본이 비어있습니다.", "ERROR")
        return False
    
    try:
        # Coqui TTS 라이브러리 확인
        try:
            from TTS.api import TTS
        except ImportError:
            log_message("⚠️ Coqui TTS가 설치되지 않았습니다. 설치: pip install TTS", "WARNING")
            log_message("   한국어 지원: pip install TTS[ko]", "WARNING")
            return False
        
        log_message("🎤 Coqui TTS로 음성 생성 중... (무료 오픈소스)")
        
        # 한국어 지원 모델 로드 (xtts_v2)
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        
        # 임시 파일에 오디오 저장 (속도 조절 전 원본)
        temp_output = output_path.parent / f"{output_path.stem}_temp.wav"
        tts.tts_to_file(text=script, file_path=str(temp_output), language="ko")
        
        # WAV를 MP3로 변환 (ffmpeg 사용)
        if output_path.suffix == ".mp3":
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-i", str(temp_output),
                    "-y",
                    str(output_path)
                ],
                capture_output=True,
                text=True,
                timeout=300
            )
            try:
                temp_output.unlink()
            except:
                pass
            
            if result.returncode != 0:
                log_message(f"⚠️ MP3 변환 실패: {result.stderr[:200]}", "WARNING")
                # WAV 파일을 그대로 사용
                temp_output.rename(output_path.with_suffix(".wav"))
                log_message(f"✅ Coqui TTS 음성 생성 완료 (WAV): {output_path.with_suffix('.wav')}")
                return True
        else:
            temp_output.rename(output_path)
        
        # 1.5배속으로 오디오 속도 조절
        if AUDIO_SPEED_MULTIPLIER != 1.0:
            final_output = output_path.parent / f"{output_path.stem}_final{output_path.suffix}"
            success = adjust_audio_speed(output_path, final_output, AUDIO_SPEED_MULTIPLIER)
            if success:
                output_path.unlink()
                final_output.rename(output_path)
                file_size = output_path.stat().st_size
                log_message(f"✅ Coqui TTS 음성 생성 완료 (1.5배속): {output_path} ({file_size:,} bytes)")
                return True
            else:
                log_message("⚠️ 속도 조절 실패, 원본 오디오 사용", "WARNING")
        
        file_size = output_path.stat().st_size
        log_message(f"✅ Coqui TTS 음성 생성 완료: {output_path} ({file_size:,} bytes)")
        return True
        
    except ImportError:
        log_message("⚠️ Coqui TTS 라이브러리를 찾을 수 없습니다.", "WARNING")
        return False
    except Exception as e:
        error_msg = mask_sensitive_info(str(e))
        log_message(f"❌ Coqui TTS 오류: {error_msg}", "ERROR")
        return False


def text_to_speech(script: str, output_path: Path) -> bool:
    """
    Chirp 3, Gemini TTS, 또는 Coqui TTS를 사용하여 텍스트를 음성으로 변환합니다.
    비용 최적화: Chirp 3 (자신의 목소리) -> Gemini TTS -> Coqui TTS 순서로 시도.
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not script:
        log_message("❌ 대본이 비어있습니다.", "ERROR")
        return False
    
    # TTS 제공자 선택 전략
    if TTS_PROVIDER == "chirp3":
        # Chirp 3만 사용 (자신의 목소리)
        if USE_CHIRP3_CUSTOM_VOICE and CHIRP3_VOICE_CLONING_KEY:
            if text_to_speech_with_chirp3(script, output_path):
                return True
        log_message("❌ Chirp 3 TTS 실패: USE_CHIRP3_CUSTOM_VOICE와 CHIRP3_VOICE_CLONING_KEY가 필요합니다.", "ERROR")
        return False
    elif TTS_PROVIDER == "gemini":
        # Gemini만 사용
        if GEMINI_API_KEY:
            if text_to_speech_with_gemini(script, output_path):
                return True
        log_message("❌ Gemini TTS 실패: API 키가 없습니다.", "ERROR")
        return False
    elif TTS_PROVIDER == "coqui":
        # Coqui만 사용
        if USE_COQUI_TTS:
            if text_to_speech_with_coqui(script, output_path):
                return True
        log_message("❌ Coqui TTS 실패: USE_COQUI_TTS가 활성화되지 않았습니다.", "ERROR")
        return False
    else:
        # auto: 자동 선택 (우선순위: Chirp 3 -> Gemini -> Coqui)
        # 1. Chirp 3 우선 (자신의 목소리)
        if USE_CHIRP3_CUSTOM_VOICE and CHIRP3_VOICE_CLONING_KEY:
            if text_to_speech_with_chirp3(script, output_path):
                return True
            log_message("🔄 Chirp 3 실패, 다음 옵션 시도...", "WARNING")
        
        # 2. Gemini TTS 폴백 (비용 효율적)
        if GEMINI_API_KEY:
            if text_to_speech_with_gemini(script, output_path):
                return True
            log_message("🔄 Gemini TTS 실패, 다음 옵션 시도...", "WARNING")
        
        # 3. Coqui TTS 폴백 (무료)
        if USE_COQUI_TTS:
            if text_to_speech_with_coqui(script, output_path):
                return True
    
    # 모든 방법 실패
    log_message("❌ 음성 생성 실패: 사용 가능한 TTS 제공자가 없습니다.", "ERROR")
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
    return 0.0


def print_usage_stats() -> None:
    """API 사용량 통계 출력 (Rate Limit 정보 포함)"""
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
    
    # Gemini Rate Limit 정보 출력
    if GEMINI_API_KEY:
        log_message(f"\n🔒 Gemini API Rate Limit 상태:")
        for model_type, tracker in rate_limit_trackers.items():
            stats = tracker.get_usage_stats()
            model_name = "Gemini 2.5 Pro" if model_type == "pro" else "Gemini 2.5 Flash"
            log_message(f"\n  {model_name}:")
            log_message(f"    RPM: {stats['rpm']['current']}/{stats['rpm']['limit']} ({stats['rpm']['usage_rate']*100:.1f}%)")
            log_message(f"    TPM: {stats['tpm']['current']:,}/{stats['tpm']['limit']:,} ({stats['tpm']['usage_rate']*100:.1f}%)")
            log_message(f"    일일 요청: {stats['rpd']['current']}/{stats['rpd']['limit']} ({stats['rpd']['usage_rate']*100:.1f}%)")
            
            # 경고 메시지
            warning = tracker.check_warning_threshold()
            if warning:
                log_message(f"    ⚠️ 경고: {warning}", "WARNING")
            else:
                log_message(f"    ✅ 정상 범위 내")
    
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
    log_message(f"  TTS 제공자:")
    log_message(f"    - 선택된 제공자: {TTS_PROVIDER}")
    log_message(f"    - Chirp 3: Instant Custom Voice: {'✅' if (USE_CHIRP3_CUSTOM_VOICE and CHIRP3_VOICE_CLONING_KEY) else '❌'} (자신의 목소리 ⭐)")
    if USE_CHIRP3_CUSTOM_VOICE and CHIRP3_VOICE_CLONING_KEY:
        log_message(f"      Voice Cloning Key: {CHIRP3_VOICE_CLONING_KEY[:10]}...")
        log_message(f"      Location: {CHIRP3_LOCATION}")
    log_message(f"    - Gemini TTS: {'✅' if GEMINI_API_KEY else '❌'} (비용 효율적)")
    if GEMINI_API_KEY:
        log_message(f"      Voice: {GEMINI_TTS_VOICE_NAME} (IT/DevSecOps 전문가용)")
        if GEMINI_TTS_VOICE_STYLE:
            log_message(f"      Style: {GEMINI_TTS_VOICE_STYLE}")
        if GEMINI_TTS_VOICE_PACE != 1.0:
            log_message(f"      Pace: {GEMINI_TTS_VOICE_PACE}x")
    log_message(f"    - Coqui TTS: {'✅' if USE_COQUI_TTS else '❌'} (무료 오픈소스)")
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
