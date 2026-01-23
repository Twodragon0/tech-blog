#!/usr/bin/env python3
"""
TTS 제공자 테스트 스크립트

Gemini 2.5 TTS API와 Coqui TTS를 테스트합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 환경 변수 로드
def load_env_file(env_path: Path) -> None:
    """간단한 .env 파일 파서"""
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

# .env 파일 로드
env_path = PROJECT_ROOT / ".env"
load_env_file(env_path)

# python-dotenv도 시도
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(env_path, override=False)
except ImportError:
    pass

# generate_enhanced_audio 모듈 임포트
from generate_enhanced_audio import (
    text_to_speech_with_gemini,
    text_to_speech_with_coqui,
    text_to_speech,
    GEMINI_API_KEY,
    USE_COQUI_TTS,
    OUTPUT_DIR,
    log_message
)

def test_gemini_tts():
    """Gemini TTS 테스트"""
    print("\n" + "=" * 60)
    print("🧪 Gemini 2.5 TTS API 테스트")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 GEMINI_API_KEY를 추가하세요.")
        return False
    
    test_text = "안녕하세요. 이것은 Gemini TTS API 테스트입니다. 한국어 음성 생성이 정상적으로 작동하는지 확인합니다."
    output_path = OUTPUT_DIR / "test_gemini_tts.mp3"
    
    print(f"📝 테스트 텍스트: {test_text}")
    print(f"📁 출력 파일: {output_path}")
    
    try:
        success = text_to_speech_with_gemini(test_text, output_path)
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ Gemini TTS 테스트 성공!")
            print(f"   파일 크기: {file_size:,} bytes")
            print(f"   파일 경로: {output_path}")
            return True
        else:
            print("❌ Gemini TTS 테스트 실패: 파일이 생성되지 않았습니다.")
            return False
    except Exception as e:
        print(f"❌ Gemini TTS 테스트 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_coqui_tts():
    """Coqui TTS 테스트"""
    print("\n" + "=" * 60)
    print("🧪 Coqui TTS 오픈소스 테스트")
    print("=" * 60)
    
    # Coqui TTS 라이브러리 확인
    try:
        from TTS.api import TTS
    except ImportError:
        print("❌ Coqui TTS가 설치되지 않았습니다.")
        print("   설치 방법: pip install TTS[ko]")
        print("   또는: pip install TTS")
        return False
    
    test_text = "안녕하세요. 이것은 Coqui TTS 테스트입니다. 무료 오픈소스 음성 생성이 정상적으로 작동하는지 확인합니다."
    output_path = OUTPUT_DIR / "test_coqui_tts.mp3"
    
    print(f"📝 테스트 텍스트: {test_text}")
    print(f"📁 출력 파일: {output_path}")
    
    try:
        success = text_to_speech_with_coqui(test_text, output_path)
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ Coqui TTS 테스트 성공!")
            print(f"   파일 크기: {file_size:,} bytes")
            print(f"   파일 경로: {output_path}")
            return True
        else:
            # WAV 파일도 확인
            wav_path = OUTPUT_DIR / "test_coqui_tts.wav"
            if wav_path.exists():
                file_size = wav_path.stat().st_size
                print(f"✅ Coqui TTS 테스트 성공 (WAV 형식)!")
                print(f"   파일 크기: {file_size:,} bytes")
                print(f"   파일 경로: {wav_path}")
                return True
            print("❌ Coqui TTS 테스트 실패: 파일이 생성되지 않았습니다.")
            return False
    except Exception as e:
        print(f"❌ Coqui TTS 테스트 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_selection():
    """자동 선택 테스트 (auto 모드)"""
    print("\n" + "=" * 60)
    print("🧪 자동 TTS 제공자 선택 테스트 (auto 모드)")
    print("=" * 60)
    
    # TTS_PROVIDER를 auto로 설정
    original_provider = os.getenv("TTS_PROVIDER", "auto")
    os.environ["TTS_PROVIDER"] = "auto"
    
    test_text = "안녕하세요. 이것은 자동 선택 모드 테스트입니다. 시스템이 가장 적합한 TTS 제공자를 자동으로 선택합니다."
    output_path = OUTPUT_DIR / "test_auto_tts.mp3"
    
    print(f"📝 테스트 텍스트: {test_text}")
    print(f"📁 출력 파일: {output_path}")
    print(f"🔧 TTS_PROVIDER: auto (자동 선택)")
    
    try:
        success = text_to_speech(test_text, output_path)
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ 자동 선택 테스트 성공!")
            print(f"   파일 크기: {file_size:,} bytes")
            print(f"   파일 경로: {output_path}")
            
            # 어떤 제공자가 사용되었는지 확인
            if GEMINI_API_KEY:
                print(f"   사용된 제공자: Gemini TTS (우선순위 1)")
            elif USE_COQUI_TTS:
                print(f"   사용된 제공자: Coqui TTS (폴백)")
            else:
                print(f"   사용된 제공자: 알 수 없음")
            
            return True
        else:
            print("❌ 자동 선택 테스트 실패: 파일이 생성되지 않았습니다.")
            return False
    except Exception as e:
        print(f"❌ 자동 선택 테스트 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 원래 설정 복원
        if original_provider:
            os.environ["TTS_PROVIDER"] = original_provider


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🎤 TTS 제공자 테스트 시작")
    print("=" * 60)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    results = {}
    
    # 1. Gemini TTS 테스트
    print("\n[1/3] Gemini TTS 테스트")
    results["gemini"] = test_gemini_tts()
    
    # 2. Coqui TTS 테스트
    print("\n[2/3] Coqui TTS 테스트")
    results["coqui"] = test_coqui_tts()
    
    # 3. 자동 선택 테스트
    print("\n[3/3] 자동 선택 테스트")
    results["auto"] = test_auto_selection()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {test_name.upper()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"\n총 테스트: {total_tests}")
    print(f"성공: {passed_tests}")
    print(f"실패: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 모든 테스트가 성공했습니다!")
        return 0
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다. 위의 오류 메시지를 확인하세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
