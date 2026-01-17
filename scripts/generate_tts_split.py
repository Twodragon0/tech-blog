#!/usr/bin/env python3
"""
대본을 분할하여 Gemini TTS와 Coqui TTS로 생성하는 스크립트

긴 대본을 여러 부분으로 나누어 생성하고 합칩니다.
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
    log_message
)
import subprocess

def split_text(text: str, max_length: int = 2000) -> list:
    """텍스트를 문장 단위로 분할"""
    sentences = []
    current = ""
    
    # 문장 단위로 분할 (마침표, 물음표, 느낌표 기준)
    import re
    parts = re.split(r'([.!?]\s+)', text)
    
    for i in range(0, len(parts), 2):
        sentence = parts[i] + (parts[i+1] if i+1 < len(parts) else "")
        if len(current + sentence) <= max_length:
            current += sentence
        else:
            if current:
                sentences.append(current.strip())
            current = sentence
    
    if current:
        sentences.append(current.strip())
    
    return sentences

def merge_audio_files(audio_files: list, output_path: Path) -> bool:
    """여러 오디오 파일을 하나로 합치기"""
    try:
        # ffmpeg를 사용하여 오디오 파일 합치기
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, "w") as f:
            for audio_file in audio_files:
                if audio_file.exists():
                    f.write(f"file '{audio_file.absolute()}'\n")
        
        result = subprocess.run(
            [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-y",
                str(output_path)
            ],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        # 임시 파일 삭제
        try:
            concat_file.unlink()
        except:
            pass
        
        if result.returncode == 0:
            return True
        else:
            print(f"⚠️ 오디오 합치기 실패: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ 오디오 합치기 오류: {str(e)}")
        return False

def generate_with_gemini_split(script_text: str, output_path: Path) -> bool:
    """Gemini TTS로 분할 생성"""
    print("\n" + "=" * 60)
    print("🎤 Gemini 2.5 TTS로 분할 생성 중...")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return False
    
    # 텍스트 분할
    parts = split_text(script_text, max_length=2000)
    print(f"📝 대본 길이: {len(script_text)}자")
    print(f"📦 분할 개수: {len(parts)}개")
    
    # 각 부분 생성
    temp_files = []
    for i, part in enumerate(parts, 1):
        print(f"\n  [{i}/{len(parts)}] 생성 중... ({len(part)}자)")
        temp_file = output_path.parent / f"{output_path.stem}_part{i}.mp3"
        
        try:
            success = text_to_speech_with_gemini(part, temp_file)
            if success and temp_file.exists():
                file_size = temp_file.stat().st_size
                print(f"    ✅ 완료 ({file_size / 1024:.1f} KB)")
                temp_files.append(temp_file)
            else:
                print(f"    ❌ 실패")
                return False
        except Exception as e:
            print(f"    ❌ 오류: {str(e)}")
            return False
    
    # 오디오 파일 합치기
    print(f"\n🔗 오디오 파일 합치기 중...")
    if merge_audio_files(temp_files, output_path):
        # 임시 파일 삭제
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
        
        file_size = output_path.stat().st_size
        print(f"✅ Gemini TTS 생성 완료!")
        print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print(f"   파일 경로: {output_path}")
        return True
    else:
        return False

def generate_with_coqui_split(script_text: str, output_path: Path) -> bool:
    """Coqui TTS로 분할 생성"""
    print("\n" + "=" * 60)
    print("🎤 Coqui TTS로 분할 생성 중...")
    print("=" * 60)
    
    try:
        from TTS.api import TTS
    except ImportError:
        print("❌ Coqui TTS가 설치되지 않았습니다.")
        print("   설치 방법: pip install TTS[ko]")
        return False
    
    # 텍스트 분할
    parts = split_text(script_text, max_length=2000)
    print(f"📝 대본 길이: {len(script_text)}자")
    print(f"📦 분할 개수: {len(parts)}개")
    
    # 각 부분 생성
    temp_files = []
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    
    for i, part in enumerate(parts, 1):
        print(f"\n  [{i}/{len(parts)}] 생성 중... ({len(part)}자)")
        temp_file = output_path.parent / f"{output_path.stem}_part{i}.wav"
        
        try:
            tts.tts_to_file(text=part, file_path=str(temp_file), language="ko")
            if temp_file.exists():
                file_size = temp_file.stat().st_size
                print(f"    ✅ 완료 ({file_size / 1024:.1f} KB)")
                temp_files.append(temp_file)
            else:
                print(f"    ❌ 실패")
                return False
        except Exception as e:
            print(f"    ❌ 오류: {str(e)}")
            return False
    
    # 오디오 파일 합치기
    print(f"\n🔗 오디오 파일 합치기 중...")
    if merge_audio_files(temp_files, output_path):
        # 임시 파일 삭제
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
        
        file_size = output_path.stat().st_size
        print(f"✅ Coqui TTS 생성 완료!")
        print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print(f"   파일 경로: {output_path}")
        return True
    else:
        return False

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
    """메인 함수"""
    print("=" * 60)
    print("🎵 Gemini TTS vs Coqui TTS 분할 생성")
    print("=" * 60)
    
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
            print(f"📄 자동 선택된 대본: {script_file.name}")
        else:
            print("❌ 대본 파일을 찾을 수 없습니다.")
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
    print("\n[1/2] Gemini TTS 분할 생성")
    results["gemini"] = generate_with_gemini_split(script_text, gemini_output)
    
    # 2. Coqui TTS 생성
    print("\n[2/2] Coqui TTS 분할 생성")
    results["coqui"] = generate_with_coqui_split(script_text, coqui_output)
    
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
            print(f"  {provider.upper()}: {status}")
    
    success_count = sum(1 for s in results.values() if s)
    
    if success_count > 0:
        print("\n🎉 오디오 파일 생성 완료!")
        if results["gemini"]:
            print(f"   - Gemini: {gemini_output}")
        if results["coqui"]:
            print(f"   - Coqui: {coqui_output}")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
