#!/usr/bin/env python3
"""
블로그 포스팅을 자동으로 영상 강의용 오디오로 변환하는 스크립트

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
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import frontmatter

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_FILE = PROJECT_ROOT / "video_generation_log.txt"

# 출력 디렉토리 생성
OUTPUT_DIR.mkdir(exist_ok=True)

# API 설정 (환경 변수에서 읽기)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# API 엔드포인트
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
ELEVENLABS_VOICES_URL = "https://api.elevenlabs.io/v1/voices"
ELEVENLABS_USER_URL = "https://api.elevenlabs.io/v1/user"

# 설정
MAX_TEXT_LENGTH = 50000  # 최대 텍스트 길이 (비용 관리)
MAX_SCRIPT_LENGTH = 800  # 최대 대본 길이 (약 3분 분량, ElevenLabs 무료 티어 고려)
# ElevenLabs 무료 티어: 월 10,000자 = 약 5,000 크레딧
# 크레딧 = 문자 수이므로 짧은 대본 필요
AUDIO_OUTPUT_FORMAT = "mp3"


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
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ 로그 파일 기록 실패: {e}", file=sys.stderr)
    
    print(log_entry.strip())


def list_voices() -> Optional[Dict[str, Any]]:
    """
    ElevenLabs API를 사용하여 사용 가능한 Voice 목록을 조회합니다.
    
    Returns:
        Voice 목록이 포함된 딕셔너리 또는 None (실패 시)
    """
    if not ELEVENLABS_API_KEY:
        log_message("❌ ELEVENLABS_API_KEY가 설정되지 않았습니다.", "ERROR")
        return None
    
    try:
        log_message("🔍 ElevenLabs Voice 목록 조회 중...")
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        response = requests.get(
            ELEVENLABS_VOICES_URL,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "voices" not in result:
            log_message(f"❌ ElevenLabs API 응답 형식 오류: {json.dumps(result, ensure_ascii=False)}", "ERROR")
            return None
        
        voices = result["voices"]
        log_message(f"✅ {len(voices)}개의 Voice를 찾았습니다.")
        
        return result
        
    except requests.exceptions.RequestException as e:
        log_message(f"❌ ElevenLabs API 요청 실패: {str(e)}", "ERROR")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                log_message(f"   응답 내용: {json.dumps(error_detail, ensure_ascii=False)}", "ERROR")
            except:
                log_message(f"   응답 내용: {e.response.text[:200]}", "ERROR")
        return None
    except Exception as e:
        log_message(f"❌ Voice 목록 조회 중 오류 발생: {str(e)}", "ERROR")
        return None


def check_elevenlabs_credits(required_credits: int = 800) -> Optional[int]:
    """
    ElevenLabs API 크레딧을 확인합니다.
    
    Args:
        required_credits: 필요한 최소 크레딧 (기본값: 800)
        
    Returns:
        남은 크레딧 또는 None (확인 실패 시)
    """
    if not ELEVENLABS_API_KEY:
        return None
    
    try:
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        response = requests.get(
            ELEVENLABS_USER_URL,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            # subscription 정보에서 크레딧 확인
            subscription = user_data.get("subscription", {})
            character_limit = subscription.get("character_limit", 0)
            character_count = subscription.get("character_count", 0)
            remaining = character_limit - character_count
            
            log_message(f"💰 ElevenLabs 크레딧: {remaining:,} / {character_limit:,} (사용: {character_count:,})")
            
            if remaining < required_credits:
                log_message(f"⚠️ 크레딧 부족: {remaining} < {required_credits} (필요)", "WARNING")
                log_message(f"💡 해결 방법:", "WARNING")
                log_message(f"   1. ElevenLabs 대시보드 확인: https://elevenlabs.io/app/usage", "WARNING")
                log_message(f"   2. 다음 달까지 대기 (월간 크레딧 리셋)", "WARNING")
                log_message(f"   3. 유료 플랜 업그레이드 고려", "WARNING")
                return remaining
            
            return remaining
        else:
            log_message(f"⚠️ ElevenLabs 크레딧 확인 실패: HTTP {response.status_code}", "WARNING")
            return None
            
    except Exception as e:
        log_message(f"⚠️ ElevenLabs 크레딧 확인 중 오류: {str(e)}", "WARNING")
        return None


def validate_api_keys() -> bool:
    """
    필수 API 키가 설정되어 있는지 검증합니다.
    
    Returns:
        모든 API 키가 설정되어 있으면 True, 아니면 False
    """
    missing_keys = []
    
    if not ELEVENLABS_API_KEY:
        missing_keys.append("ELEVENLABS_API_KEY")
    if not ELEVENLABS_VOICE_ID:
        missing_keys.append("ELEVENLABS_VOICE_ID")
    if not DEEPSEEK_API_KEY:
        missing_keys.append("DEEPSEEK_API_KEY")
    
    if missing_keys:
        log_message(f"❌ 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_keys)}", "ERROR")
        log_message("환경 변수 설정 방법:", "ERROR")
        log_message("  export ELEVENLABS_API_KEY='your-api-key'", "ERROR")
        log_message("  export ELEVENLABS_VOICE_ID='your-voice-id'", "ERROR")
        log_message("  export DEEPSEEK_API_KEY='your-deepseek-key'", "ERROR")
        return False
    
    # API 키 형식 검증
    if not DEEPSEEK_API_KEY.startswith("sk-"):
        log_message("⚠️ DEEPSEEK_API_KEY 형식이 올바르지 않습니다 (sk-로 시작해야 함)", "WARNING")
    
    return True


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


def generate_script(text: str, post_title: str = "") -> Optional[str]:
    """
    DeepSeek API를 사용하여 강의용 대본을 생성합니다.
    
    Args:
        text: 원본 텍스트
        post_title: 포스트 제목 (선택사항)
        
    Returns:
        생성된 대본 또는 None (실패 시)
    """
    if not text:
        log_message("❌ 텍스트가 비어있습니다.", "ERROR")
        return None
    
    # 텍스트 길이 제한 (비용 관리)
    if len(text) > MAX_TEXT_LENGTH:
        log_message(f"⚠️ 텍스트가 너무 깁니다 ({len(text)}자). 처음 {MAX_TEXT_LENGTH}자만 사용합니다.", "WARNING")
        text = text[:MAX_TEXT_LENGTH]
    
    # 프롬프트 구성
    # ElevenLabs 무료 티어 제한 고려: 월 10,000자 = 약 5,000 크레딧
    # 크레딧 = 문자 수이므로 짧은 대본 생성 필요
    title_context = f"제목: {post_title}\n\n" if post_title else ""
    prompt = f"""다음 보안 기술 블로그 내용을 3분 내외의 간결한 강의 대본으로 요약해줘. 
구어체로 작성하고, 핵심 내용만 명확하게 전달해줘.

{title_context}블로그 내용:
{text}

요구사항:
- 구어체로 작성 (예: "안녕하세요", "이제", "그런데" 등 자연스러운 말투)
- 핵심 내용만 간결하게 전달 (불필요한 설명 생략)
- 3분 내외 분량 (약 500-700자, 최대 800자)
- 기술 용어는 정확하게 사용
- 한국어로 작성
- 크레딧 절약을 위해 가능한 한 짧게 작성"""
    
    # 재시도 로직 (최대 3회)
    max_retries = 3
    retry_delay = 2  # 초기 재시도 대기 시간 (초)
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = retry_delay * (2 ** (attempt - 2))  # 지수 백오프
                log_message(f"🔄 재시도 {attempt}/{max_retries} (대기: {wait_time}초)...", "WARNING")
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
                "max_tokens": 2000
            }
            
            # 타임아웃 증가: 긴 포스트 처리 시 시간이 더 필요함
            timeout_seconds = 120  # 30초 → 120초로 증가
            
            response = requests.post(
                DEEPSEEK_API_URL,
                json=data,
                headers=headers,
                timeout=timeout_seconds
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                log_message(f"❌ DeepSeek API 응답 형식 오류: {json.dumps(result, ensure_ascii=False)}", "ERROR")
                if attempt < max_retries:
                    continue
                return None
            
            script = result["choices"][0]["message"]["content"].strip()
            
            # 대본 길이 검증
            if len(script) > MAX_SCRIPT_LENGTH:
                log_message(f"⚠️ 생성된 대본이 너무 깁니다 ({len(script)}자). 처음 {MAX_SCRIPT_LENGTH}자만 사용합니다.", "WARNING")
                script = script[:MAX_SCRIPT_LENGTH]
            
            log_message(f"✅ 대본 생성 완료 ({len(script)}자)")
            return script
            
        except requests.exceptions.Timeout as e:
            log_message(f"⏱️ DeepSeek API 타임아웃 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ DeepSeek API 요청 타임아웃: 최대 재시도 횟수 초과", "ERROR")
            return None
        except requests.exceptions.RequestException as e:
            log_message(f"❌ DeepSeek API 요청 실패 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ DeepSeek API 요청 실패: 최대 재시도 횟수 초과", "ERROR")
            return None
        except Exception as e:
            log_message(f"❌ 대본 생성 중 오류 발생 (시도 {attempt}/{max_retries}): {str(e)}", "WARNING")
            if attempt < max_retries:
                continue
            log_message(f"❌ 대본 생성 중 오류 발생: 최대 재시도 횟수 초과", "ERROR")
            return None
    
    return None


def text_to_speech(script: str, output_path: Path) -> bool:
    """
    ElevenLabs API를 사용하여 텍스트를 음성으로 변환합니다.
    
    Args:
        script: 대본 텍스트
        output_path: 출력 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not script:
        log_message("❌ 대본이 비어있습니다.", "ERROR")
        return False
    
    if not ELEVENLABS_VOICE_ID:
        log_message("❌ ELEVENLABS_VOICE_ID가 설정되지 않았습니다.", "ERROR")
        return False
    
    # 크레딧 사전 확인 (대본 길이만큼 필요)
    required_credits = len(script)
    remaining_credits = check_elevenlabs_credits(required_credits)
    
    if remaining_credits is not None and remaining_credits < required_credits:
        log_message(f"❌ 크레딧 부족: {remaining_credits} < {required_credits} (필요)", "ERROR")
        log_message(f"💡 대본 길이: {len(script)}자 → 필요 크레딧: {required_credits}", "ERROR")
        log_message(f"💡 해결 방법:", "ERROR")
        log_message(f"   1. 대본을 더 짧게 생성 (현재 제한: {MAX_SCRIPT_LENGTH}자)", "ERROR")
        log_message(f"   2. ElevenLabs 크레딧 확인: https://elevenlabs.io/app/usage", "ERROR")
        log_message(f"   3. 다음 달까지 대기 또는 유료 플랜 업그레이드", "ERROR")
        return False
    
    try:
        log_message("🎤 ElevenLabs API로 음성 생성 중...")
        
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
        
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=60  # 음성 생성은 시간이 걸릴 수 있음
        )
        
        response.raise_for_status()
        
        # 오디오 파일 저장
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        file_size = output_path.stat().st_size
        log_message(f"✅ 음성 생성 완료: {output_path} ({file_size:,} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        log_message(f"❌ ElevenLabs API 요청 실패: {str(e)}", "ERROR")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                log_message(f"   응답 내용: {json.dumps(error_detail, ensure_ascii=False)}", "ERROR")
                
                # 크레딧 부족 오류 처리
                if "detail" in error_detail:
                    detail = error_detail["detail"]
                    if isinstance(detail, dict) and detail.get("status") == "quota_exceeded":
                        message = detail.get("message", "")
                        log_message(f"⚠️ ElevenLabs 크레딧 부족: {message}", "ERROR")
                        log_message(f"💡 해결 방법:", "ERROR")
                        log_message(f"   1. ElevenLabs 대시보드에서 크레딧 확인: https://elevenlabs.io/app/usage", "ERROR")
                        log_message(f"   2. 대본 길이를 줄이거나 다음 달까지 대기", "ERROR")
                        log_message(f"   3. 유료 플랜으로 업그레이드 고려", "ERROR")
            except:
                log_message(f"   응답 내용: {e.response.text[:200]}", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ 음성 생성 중 오류 발생: {str(e)}", "ERROR")
        return False


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
    
    # 작업 시작 전 크레딧 확인 (예상 최대 크레딧: MAX_SCRIPT_LENGTH)
    log_message("💰 ElevenLabs 크레딧 사전 확인 중...")
    remaining_credits = check_elevenlabs_credits(MAX_SCRIPT_LENGTH)
    if remaining_credits is not None and remaining_credits < MAX_SCRIPT_LENGTH:
        log_message(f"⚠️ 크레딧이 부족할 수 있습니다: {remaining_credits} < {MAX_SCRIPT_LENGTH} (예상 필요)", "WARNING")
        log_message(f"💡 짧은 대본으로 생성 시도하겠습니다...", "WARNING")
    
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
        audio_filename = f"{post_stem}_audio.{AUDIO_OUTPUT_FORMAT}"
        audio_path = OUTPUT_DIR / audio_filename
        
        # 음성 생성
        success = text_to_speech(script, audio_path)
        
        if success:
            log_message(f"✅ 포스트 처리 완료: {post_path.name}")
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
    log_message("블로그 포스팅 → 오디오 변환 시작")
    log_message("=" * 60)
    
    # Voice 목록 조회 옵션 처리
    if len(sys.argv) > 1 and sys.argv[1] == "--list-voices":
        if not ELEVENLABS_API_KEY:
            log_message("❌ ELEVENLABS_API_KEY가 설정되지 않았습니다.", "ERROR")
            sys.exit(1)
        
        result = list_voices()
        if result and "voices" in result:
            log_message("\n📋 사용 가능한 Voice 목록:")
            log_message("=" * 60)
            for voice in result["voices"]:
                voice_id = voice.get("voice_id", "N/A")
                name = voice.get("name", "N/A")
                category = voice.get("category", "N/A")
                description = voice.get("description", "")
                
                log_message(f"\n🎤 Voice: {name}")
                log_message(f"   ID: {voice_id}")
                log_message(f"   카테고리: {category}")
                if description:
                    log_message(f"   설명: {description}")
            
            log_message("\n" + "=" * 60)
            log_message("💡 Voice ID를 환경 변수에 설정하세요:")
            log_message("   export ELEVENLABS_VOICE_ID='your-voice-id'")
        else:
            log_message("❌ Voice 목록을 가져올 수 없습니다.", "ERROR")
            sys.exit(1)
        
        sys.exit(0)
    
    # API 키 검증
    if not validate_api_keys():
        log_message("❌ API 키 검증 실패. 스크립트를 종료합니다.", "ERROR")
        sys.exit(1)
    
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
    
    # 결과 요약
    log_message("=" * 60)
    log_message(f"처리 완료: {success_count}/{len(post_paths)} 성공")
    log_message("=" * 60)
    
    if success_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
