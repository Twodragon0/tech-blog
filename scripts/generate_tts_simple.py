#!/usr/bin/env python3
"""
간단한 텍스트로 Gemini TTS와 Coqui TTS 테스트 생성

짧은 텍스트로 두 TTS 제공자를 빠르게 테스트합니다.
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
    OUTPUT_DIR,
)

# 실제 대본에서 추출한 텍스트 (처음 부분)
TEST_TEXT = """혹시 최근 유튜브에서 화제가 된 'Pioneer'라는 AI 뮤직비디오 보셨나요? 
이미지부터 음악, 영상까지 전부 AI로만 만들었는데, 퀄리티가 정말 놀랍죠. 
하지만 우리 같은 DevSecOps 엔지니어들에게는 이 화려한 기술 뒤에 숨겨진 보안, 비용, 거버넌스 문제가 더 중요합니다. 
오늘은 Midjourney, Suno V5, Veo 3 같은 최신 AI 도구부터, API 키 관리, 데이터 프라이버시 보호, CI/CD 자동화, 그리고 비용 최적화 전략까지 DevSecOps 관점에서 완벽하게 정리해드리겠습니다."""

def main():
    print("=" * 60)
    print("🎵 Gemini TTS vs Coqui TTS 간단 테스트")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    gemini_output = OUTPUT_DIR / "test_gemini_simple.mp3"
    coqui_output = OUTPUT_DIR / "test_coqui_simple.mp3"
    
    results = {}
    
    # 1. Gemini TTS
    print("\n[1/2] Gemini TTS 생성 중...")
    if GEMINI_API_KEY:
        try:
            success = text_to_speech_with_gemini(TEST_TEXT, gemini_output)
            if success and gemini_output.exists():
                file_size = gemini_output.stat().st_size
                print(f"✅ Gemini TTS 성공! ({file_size / 1024:.1f} KB)")
                print(f"   파일: {gemini_output}")
                results["gemini"] = True
            else:
                print("❌ Gemini TTS 실패")
                results["gemini"] = False
        except Exception as e:
            print(f"❌ Gemini TTS 오류: {str(e)}")
            results["gemini"] = False
    else:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        results["gemini"] = False
    
    # 2. Coqui TTS
    print("\n[2/2] Coqui TTS 생성 중...")
    try:
        from TTS.api import TTS
        try:
            success = text_to_speech_with_coqui(TEST_TEXT, coqui_output)
            if success:
                if coqui_output.exists():
                    file_size = coqui_output.stat().st_size
                    print(f"✅ Coqui TTS 성공! ({file_size / 1024:.1f} KB)")
                    print(f"   파일: {coqui_output}")
                    results["coqui"] = True
                else:
                    wav_file = coqui_output.with_suffix(".wav")
                    if wav_file.exists():
                        file_size = wav_file.stat().st_size
                        print(f"✅ Coqui TTS 성공! (WAV, {file_size / 1024:.1f} KB)")
                        print(f"   파일: {wav_file}")
                        results["coqui"] = True
                    else:
                        print("❌ Coqui TTS 실패")
                        results["coqui"] = False
            else:
                print("❌ Coqui TTS 실패")
                results["coqui"] = False
        except Exception as e:
            print(f"❌ Coqui TTS 오류: {str(e)}")
            results["coqui"] = False
    except ImportError:
        print("❌ Coqui TTS가 설치되지 않았습니다.")
        print("   설치: pip install TTS[ko]")
        results["coqui"] = False
    
    # 결과
    print("\n" + "=" * 60)
    print("📊 결과 요약")
    print("=" * 60)
    for provider, success in results.items():
        print(f"  {provider.upper()}: {'✅ 성공' if success else '❌ 실패'}")
    
    success_count = sum(1 for s in results.values() if s)
    print(f"\n성공: {success_count}/{len(results)}")
    
    if success_count > 0:
        print("\n🎉 테스트 완료! 생성된 파일을 재생해보세요.")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
