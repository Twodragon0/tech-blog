#!/usr/bin/env python3
"""
Gemini TTS와 Coqui TTS 비교 생성 스크립트

두 가지 TTS 제공자로 동일한 텍스트를 생성하여 비교합니다.
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
    GEMINI_API_KEY,
    OUTPUT_DIR,
    log_message
)

def extract_script_text(script_path: Path) -> str:
    """대본 파일에서 실제 대본 텍스트 추출"""
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # "강의용 대본" 섹션 찾기
        if "강의용 대본" in content:
            parts = content.split("강의용 대본")
            if len(parts) > 1:
                script_text = parts[1].strip()
                # 구분선 제거
                script_text = script_text.replace("=" * 60, "").strip()
                return script_text
        
        # 전체 내용 반환 (구분선이 없는 경우)
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

def generate_with_gemini(script_text: str, output_path: Path) -> bool:
    """Gemini TTS로 오디오 생성"""
    print("\n" + "=" * 60)
    print("🎤 Gemini 2.5 TTS로 오디오 생성 중...")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return False
    
    print(f"📝 대본 길이: {len(script_text)}자")
    print(f"📁 출력 파일: {output_path}")
    
    try:
        success = text_to_speech_with_gemini(script_text, output_path)
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ Gemini TTS 생성 완료!")
            print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            print(f"   파일 경로: {output_path}")
            return True
        else:
            print("❌ Gemini TTS 생성 실패")
            return False
    except Exception as e:
        print(f"❌ Gemini TTS 생성 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_with_coqui(script_text: str, output_path: Path) -> bool:
    """Coqui TTS로 오디오 생성"""
    print("\n" + "=" * 60)
    print("🎤 Coqui TTS로 오디오 생성 중...")
    print("=" * 60)
    
    # Coqui TTS 라이브러리 확인
    try:
        from TTS.api import TTS
    except ImportError:
        print("❌ Coqui TTS가 설치되지 않았습니다.")
        print("   설치 방법: pip install TTS[ko]")
        return False
    
    print(f"📝 대본 길이: {len(script_text)}자")
    print(f"📁 출력 파일: {output_path}")
    
    try:
        success = text_to_speech_with_coqui(script_text, output_path)
        if success:
            # MP3 또는 WAV 파일 확인
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"✅ Coqui TTS 생성 완료!")
                print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                print(f"   파일 경로: {output_path}")
                return True
            else:
                # WAV 파일 확인
                wav_path = output_path.with_suffix(".wav")
                if wav_path.exists():
                    file_size = wav_path.stat().st_size
                    print(f"✅ Coqui TTS 생성 완료 (WAV 형식)!")
                    print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                    print(f"   파일 경로: {wav_path}")
                    return True
        
        print("❌ Coqui TTS 생성 실패")
        return False
    except Exception as e:
        print(f"❌ Coqui TTS 생성 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🎵 Gemini TTS vs Coqui TTS 비교 생성")
    print("=" * 60)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 대본 파일 찾기
    script_file = None
    if len(sys.argv) > 1:
        script_file = Path(sys.argv[1])
        if not script_file.is_absolute():
            script_file = OUTPUT_DIR / script_file
    else:
        # 최신 대본 파일 자동 선택
        script_files = sorted(OUTPUT_DIR.glob("*_script.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        if script_files:
            script_file = script_files[0]
            print(f"📄 자동 선택된 대본: {script_file.name}")
        else:
            print("❌ 대본 파일을 찾을 수 없습니다.")
            print("   사용법: python scripts/generate_tts_comparison.py [대본파일]")
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
    gemini_output = OUTPUT_DIR / f"{base_name}_gemini_tts.mp3"
    coqui_output = OUTPUT_DIR / f"{base_name}_coqui_tts.mp3"
    
    results = {}
    
    # 1. Gemini TTS 생성
    print("\n[1/2] Gemini TTS 생성")
    results["gemini"] = generate_with_gemini(script_text, gemini_output)
    
    # 2. Coqui TTS 생성
    print("\n[2/2] Coqui TTS 생성")
    results["coqui"] = generate_with_coqui(script_text, coqui_output)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 생성 결과 요약")
    print("=" * 60)
    
    for provider, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        output_file = gemini_output if provider == "gemini" else coqui_output
        if success and output_file.exists():
            file_size = output_file.stat().st_size
            print(f"  {provider.upper()}: {status} ({file_size / 1024:.1f} KB)")
        else:
            # WAV 파일 확인 (Coqui의 경우)
            if provider == "coqui":
                wav_file = coqui_output.with_suffix(".wav")
                if wav_file.exists():
                    file_size = wav_file.stat().st_size
                    print(f"  {provider.upper()}: {status} (WAV, {file_size / 1024:.1f} KB)")
                else:
                    print(f"  {provider.upper()}: {status}")
            else:
                print(f"  {provider.upper()}: {status}")
    
    total = len(results)
    success_count = sum(1 for s in results.values() if s)
    
    print(f"\n총 생성 시도: {total}")
    print(f"성공: {success_count}")
    print(f"실패: {total - success_count}")
    
    if success_count > 0:
        print("\n🎉 오디오 파일 생성 완료!")
        print(f"   비교를 위해 두 파일을 재생해보세요:")
        if results["gemini"]:
            print(f"   - Gemini: {gemini_output}")
        if results["coqui"]:
            if coqui_output.exists():
                print(f"   - Coqui: {coqui_output}")
            else:
                wav_file = coqui_output.with_suffix(".wav")
                if wav_file.exists():
                    print(f"   - Coqui: {wav_file}")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
