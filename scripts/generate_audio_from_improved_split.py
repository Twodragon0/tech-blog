#!/usr/bin/env python3
"""
개선된 대본을 분할하여 오디오 생성 (긴 대본 처리용)

긴 대본을 여러 부분으로 나누어 생성하고 합칩니다.
"""

import os
import sys
import re
import subprocess
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
    OUTPUT_DIR,
    AUDIO_OUTPUT_FORMAT,
    GEMINI_API_KEY,
    GEMINI_TTS_VOICE_NAME,
    log_message
)

def extract_improved_script_text(script_path: Path) -> str:
    """개선된 대본 파일에서 실제 대본 텍스트 추출"""
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "개선된 강의용 대본" in content:
            parts = content.split("개선된 강의용 대본")
            if len(parts) > 1:
                script_text = parts[1].strip()
                script_text = re.sub(r'^={10,}\s*$', '', script_text, flags=re.MULTILINE)
                if "Remotion 동기화 구간 정보" in script_text:
                    script_text = script_text.split("Remotion 동기화 구간 정보")[0].strip()
                return script_text.strip()
        
        if "강의용 대본" in content:
            parts = content.split("강의용 대본")
            if len(parts) > 1:
                script_text = parts[1].strip()
                script_text = re.sub(r'^={10,}\s*$', '', script_text, flags=re.MULTILINE)
                if "Remotion 동기화 구간 정보" in script_text:
                    script_text = script_text.split("Remotion 동기화 구간 정보")[0].strip()
                return script_text.strip()
        
        return content.strip()
    except Exception as e:
        print(f"❌ 대본 파일 읽기 오류: {str(e)}")
        return ""

def split_text_for_tts(text: str, max_length: int = 1500) -> list:
    """텍스트를 문장 단위로 분할 (TTS API 제한 고려)"""
    sentences = []
    current = ""
    
    # 문장 단위로 분할
    parts = re.split(r'([.!?]\s+)', text)
    
    for i in range(0, len(parts), 2):
        sentence = parts[i] + (parts[i+1] if i+1 < len(parts) else "")
        sentence = sentence.strip()
        
        if not sentence:
            continue
        
        if len(current + sentence) <= max_length:
            current += sentence + " "
        else:
            if current:
                sentences.append(current.strip())
            current = sentence + " "
    
    if current:
        sentences.append(current.strip())
    
    return sentences

def merge_audio_files(audio_files: list, output_path: Path) -> bool:
    """여러 오디오 파일을 하나로 합치기"""
    try:
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

def generate_audio_split(script_text: str, output_path: Path) -> bool:
    """대본을 분할하여 오디오 생성"""
    print(f"📝 대본 길이: {len(script_text)}자")
    
    # 텍스트 분할
    parts = split_text_for_tts(script_text, max_length=1500)
    print(f"📦 분할 개수: {len(parts)}개")
    
    if len(parts) == 1:
        # 분할이 필요 없는 경우 직접 생성
        print(f"🎤 Gemini TTS로 오디오 생성 중...")
        return text_to_speech_with_gemini(script_text, output_path)
    
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
        print(f"✅ 오디오 생성 완료!")
        print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print(f"   파일 경로: {output_path}")
        return True
    else:
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🎤 개선된 대본 분할 오디오 생성")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)
    
    print(f"📢 Voice: {GEMINI_TTS_VOICE_NAME} (IT 전문가용)\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 개선된 대본 파일 찾기
    if len(sys.argv) > 1:
        target_file = Path(sys.argv[1])
        if not target_file.is_absolute():
            # output/ 접두사가 있으면 제거
            if target_file.parts[0] == "output":
                target_file = OUTPUT_DIR / target_file.relative_to("output")
            else:
                target_file = OUTPUT_DIR / target_file
        if target_file.exists():
            improved_scripts = [target_file]
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {target_file}")
            sys.exit(1)
    else:
        improved_scripts = sorted(
            OUTPUT_DIR.glob("*_improved.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not improved_scripts:
            print("❌ 개선된 대본 파일을 찾을 수 없습니다.")
            sys.exit(1)
        
        print(f"📂 발견된 개선된 대본: {len(improved_scripts)}개\n")
    
    results = []
    
    for script_file in improved_scripts:
        print(f"\n{'=' * 60}")
        print(f"처리 중: {script_file.name}")
        print(f"{'=' * 60}")
        
        # 대본 텍스트 추출
        script_text = extract_improved_script_text(script_file)
        
        if not script_text:
            print(f"⚠️ 대본 텍스트를 추출할 수 없습니다.")
            continue
        
        # 출력 파일 경로
        base_name = script_file.stem.replace("_improved", "").replace("_script", "")
        audio_path = OUTPUT_DIR / f"{base_name}_audio_improved.{AUDIO_OUTPUT_FORMAT}"
        
        # 이미 생성된 오디오가 있는지 확인
        if audio_path.exists():
            file_size = audio_path.stat().st_size
            print(f"⏭️ 이미 생성된 오디오가 있습니다: {audio_path.name} ({file_size / 1024:.1f} KB)")
            results.append({
                "script": script_file.name,
                "audio": audio_path.name,
                "status": "이미 존재",
                "size": file_size
            })
            continue
        
        print(f"📁 출력 파일: {audio_path.name}")
        
        try:
            success = generate_audio_split(script_text, audio_path)
            
            if success and audio_path.exists():
                file_size = audio_path.stat().st_size
                print(f"✅ 오디오 생성 완료!")
                print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                results.append({
                    "script": script_file.name,
                    "audio": audio_path.name,
                    "status": "성공",
                    "size": file_size
                })
            else:
                print(f"❌ 오디오 생성 실패")
                results.append({
                    "script": script_file.name,
                    "audio": None,
                    "status": "실패",
                    "size": 0
                })
        except Exception as e:
            print(f"❌ 오디오 생성 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                "script": script_file.name,
                "audio": None,
                "status": "오류",
                "size": 0
            })
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 오디오 생성 결과 요약")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["status"] == "성공")
    existing_count = sum(1 for r in results if r["status"] == "이미 존재")
    failed_count = sum(1 for r in results if r["status"] in ["실패", "오류"])
    
    for result in results:
        status_icon = "✅" if result["status"] == "성공" else "⏭️" if result["status"] == "이미 존재" else "❌"
        print(f"\n{status_icon} {result['script']}")
        if result["audio"]:
            print(f"   → {result['audio']}")
            if result["size"] > 0:
                print(f"   크기: {result['size'] / 1024:.1f} KB")
        print(f"   상태: {result['status']}")
    
    print(f"\n총 {len(results)}개 처리:")
    print(f"  ✅ 성공: {success_count}개")
    print(f"  ⏭️ 이미 존재: {existing_count}개")
    print(f"  ❌ 실패: {failed_count}개")
    
    if success_count > 0 or existing_count > 0:
        print("\n🎉 오디오 생성 완료!")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
