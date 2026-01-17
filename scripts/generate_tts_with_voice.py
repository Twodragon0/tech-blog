#!/usr/bin/env python3
"""
IT 전문가용 남자 목소리로 대본 TTS 생성

Gemini TTS의 전문가용 남자 목소리로 대본을 생성합니다.
권장 Voice: Rasalgethi (Informative and professional) 또는 Sadaltager (Knowledgeable and authoritative)
"""

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):
                        os.environ[key] = value
    except Exception:
        pass

env_path = PROJECT_ROOT / ".env"
load_env_file(env_path)

try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(env_path, override=False)
except ImportError:
    pass

from generate_enhanced_audio import (
    text_to_speech_with_gemini,
    text_to_speech_with_coqui,
    GEMINI_API_KEY,
    GEMINI_TTS_VOICE_NAME,
    OUTPUT_DIR,
    log_message
)

# IT 전문가용 남자 목소리 (권장)
# Rasalgethi: Informative and professional (정보 전달 전문가용)
# Sadaltager: Knowledgeable and authoritative (권위적이고 지식이 풍부한)
# Charon: Informative and clear (명확한 정보 전달)
# Iapetus: Clear and articulate (명확하고 표현력 있는)
# Orus: Firm and decisive (단호하고 결단력 있는)
RECOMMENDED_VOICES = {
    "Rasalgethi": "Informative and professional - IT/DevSecOps 전문가용 추천",
    "Sadaltager": "Knowledgeable and authoritative - 기술 강의용 추천",
    "Charon": "Informative and clear - 명확한 정보 전달",
    "Iapetus": "Clear and articulate - 명확하고 표현력 있는",
    "Orus": "Firm and decisive - 단호하고 결단력 있는"
}

def extract_script_text(script_path: Path) -> str:
    """대본 파일에서 실제 대본 텍스트 추출"""
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "강의용 대본" in content:
            parts = content.split("강의용 대본")
            if len(parts) > 1:
                script_text = parts[1].strip()
                script_text = script_text.replace("=" * 60, "").strip()
                return script_text
        
        lines = content.split("\n")
        script_lines = []
        in_script = False
        
        for line in lines:
            if "강의용 대본" in line or "=" * 10 in line:
                in_script = True
                continue
            if in_script and line.strip():
                script_lines.append(line.strip())
        
        return "\n".join(script_lines) if script_lines else content
    except Exception as e:
        print(f"⚠️ 대본 파일 읽기 오류: {str(e)}")
        return ""

def main():
    print("=" * 60)
    print("🎤 IT 전문가용 남자 목소리로 TTS 생성")
    print("=" * 60)
    
    # Voice 설정 확인
    current_voice = os.getenv("GEMINI_TTS_VOICE_NAME", "Kore")
    print(f"\n📢 현재 Voice 설정: {current_voice}")
    
    if current_voice in RECOMMENDED_VOICES:
        print(f"   특징: {RECOMMENDED_VOICES[current_voice]}")
    else:
        print(f"   ⚠️ 권장 Voice가 아닙니다.")
        print(f"\n💡 IT 전문가용 권장 Voice:")
        for voice, desc in RECOMMENDED_VOICES.items():
            print(f"   - {voice}: {desc}")
        print(f"\n   .env 파일에 다음을 추가하세요:")
        print(f"   GEMINI_TTS_VOICE_NAME=Rasalgethi  # 또는 Sadaltager")
    
    # Voice를 전문가용으로 설정 (환경 변수에 없으면)
    if current_voice == "Kore" or current_voice not in RECOMMENDED_VOICES:
        recommended_voice = "Rasalgethi"  # IT 전문가용 추천
        print(f"\n🔧 Voice를 '{recommended_voice}'로 임시 설정합니다.")
        os.environ["GEMINI_TTS_VOICE_NAME"] = recommended_voice
        # 모듈 재로드를 위해 import 다시
        import importlib
        import generate_enhanced_audio
        importlib.reload(generate_enhanced_audio)
        from generate_enhanced_audio import GEMINI_TTS_VOICE_NAME
        print(f"   설정 완료: {GEMINI_TTS_VOICE_NAME}")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 대본 파일 찾기
    script_file = None
    if len(sys.argv) > 1:
        script_file = Path(sys.argv[1])
        if not script_file.is_absolute():
            script_file = OUTPUT_DIR / script_file
    else:
        script_files = sorted(OUTPUT_DIR.glob("*_script.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        if script_files:
            script_file = script_files[0]
            print(f"\n📄 자동 선택된 대본: {script_file.name}")
        else:
            print("\n❌ 대본 파일을 찾을 수 없습니다.")
            print("   사용법: python scripts/generate_tts_with_voice.py [대본파일]")
            sys.exit(1)
    
    if not script_file.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {script_file}")
        sys.exit(1)
    
    # 대본 텍스트 추출
    print(f"\n📖 대본 파일 읽기: {script_file.name}")
    script_text = extract_script_text(script_file)
    
    if not script_text:
        print("❌ 대본 텍스트를 추출할 수 없습니다.")
        sys.exit(1)
    
    print(f"✅ 대본 추출 완료: {len(script_text)}자")
    
    # 출력 파일 경로
    base_name = script_file.stem.replace("_script", "")
    output_path = OUTPUT_DIR / f"{base_name}_audio_professional.mp3"
    
    # Gemini TTS로 생성
    print(f"\n🎤 Gemini TTS로 생성 중...")
    print(f"   Voice: {GEMINI_TTS_VOICE_NAME}")
    print(f"   출력 파일: {output_path}")
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)
    
    try:
        # 환경 변수 직접 설정 (모듈이 이미 로드된 경우)
        os.environ["GEMINI_TTS_VOICE_NAME"] = GEMINI_TTS_VOICE_NAME
        
        success = text_to_speech_with_gemini(script_text, output_path)
        
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"\n✅ TTS 생성 완료!")
            print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            print(f"   파일 경로: {output_path}")
            print(f"   Voice: {GEMINI_TTS_VOICE_NAME}")
            print(f"\n🎉 IT 전문가용 남자 목소리로 생성되었습니다!")
            return 0
        else:
            print("\n❌ TTS 생성 실패")
            return 1
    except Exception as e:
        print(f"\n❌ TTS 생성 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
