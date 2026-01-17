#!/usr/bin/env python3
"""
개선된 대본 배치 오디오 생성 스크립트

아직 생성되지 않은 개선된 대본 파일들을 순차적으로 처리합니다.
진행 상황을 저장하여 중단 후 재개 가능합니다.
"""

import os
import sys
import json
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
import re
import subprocess

PROGRESS_FILE = OUTPUT_DIR / ".audio_generation_progress.json"

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
    """텍스트를 문장 단위로 분할"""
    sentences = []
    current = ""
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
            ["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-y", str(output_path)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        try:
            concat_file.unlink()
        except:
            pass
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 오디오 합치기 오류: {str(e)}")
        return False

def generate_audio_split(script_text: str, output_path: Path) -> bool:
    """대본을 분할하여 오디오 생성"""
    parts = split_text_for_tts(script_text, max_length=1500)
    
    if len(parts) == 1:
        return text_to_speech_with_gemini(script_text, output_path)
    
    temp_files = []
    for i, part in enumerate(parts, 1):
        temp_file = output_path.parent / f"{output_path.stem}_part{i}.mp3"
        try:
            success = text_to_speech_with_gemini(part, temp_file)
            if success and temp_file.exists():
                temp_files.append(temp_file)
            else:
                return False
        except Exception as e:
            print(f"    ❌ 오류: {str(e)}")
            return False
    
    if merge_audio_files(temp_files, output_path):
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
        return True
    return False

def load_progress() -> dict:
    """진행 상황 로드"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"completed": [], "failed": []}
    return {"completed": [], "failed": []}

def save_progress(progress: dict):
    """진행 상황 저장"""
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except:
        pass

def main():
    """메인 함수"""
    print("=" * 60)
    print("🎤 개선된 대본 배치 오디오 생성")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)
    
    print(f"📢 Voice: {GEMINI_TTS_VOICE_NAME} (IT 전문가용)\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 개선된 대본 파일 찾기
    improved_scripts = sorted(
        OUTPUT_DIR.glob("*_improved.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not improved_scripts:
        print("❌ 개선된 대본 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 진행 상황 로드
    progress = load_progress()
    completed = set(progress.get("completed", []))
    
    # 아직 생성되지 않은 파일 필터링
    pending_scripts = []
    for script_file in improved_scripts:
        base_name = script_file.stem.replace("_improved", "").replace("_script", "")
        audio_path = OUTPUT_DIR / f"{base_name}_audio_improved.{AUDIO_OUTPUT_FORMAT}"
        
        if not audio_path.exists() and script_file.name not in completed:
            pending_scripts.append(script_file)
    
    if not pending_scripts:
        print("✅ 모든 개선된 대본의 오디오가 이미 생성되었습니다!")
        return 0
    
    print(f"📂 총 개선된 대본: {len(improved_scripts)}개")
    print(f"📂 생성 완료: {len(improved_scripts) - len(pending_scripts)}개")
    print(f"📂 생성 필요: {len(pending_scripts)}개\n")
    
    results = []
    success_count = 0
    
    for idx, script_file in enumerate(pending_scripts, 1):
        print(f"\n{'=' * 60}")
        print(f"[{idx}/{len(pending_scripts)}] 처리 중: {script_file.name}")
        print(f"{'=' * 60}")
        
        # 대본 텍스트 추출
        script_text = extract_improved_script_text(script_file)
        
        if not script_text:
            print(f"⚠️ 대본 텍스트를 추출할 수 없습니다.")
            progress["failed"].append(script_file.name)
            save_progress(progress)
            continue
        
        print(f"📝 대본 길이: {len(script_text)}자")
        
        # 출력 파일 경로
        base_name = script_file.stem.replace("_improved", "").replace("_script", "")
        audio_path = OUTPUT_DIR / f"{base_name}_audio_improved.{AUDIO_OUTPUT_FORMAT}"
        
        print(f"📁 출력 파일: {audio_path.name}")
        
        try:
            # 분할 개수 확인
            parts = split_text_for_tts(script_text, max_length=1500)
            if len(parts) > 1:
                print(f"📦 분할 생성: {len(parts)}개 부분")
            
            success = generate_audio_split(script_text, audio_path)
            
            if success and audio_path.exists():
                file_size = audio_path.stat().st_size
                print(f"✅ 오디오 생성 완료! ({file_size / 1024:.1f} KB)")
                results.append({
                    "script": script_file.name,
                    "audio": audio_path.name,
                    "status": "성공",
                    "size": file_size
                })
                progress["completed"].append(script_file.name)
                save_progress(progress)
                success_count += 1
            else:
                print(f"❌ 오디오 생성 실패")
                results.append({
                    "script": script_file.name,
                    "audio": None,
                    "status": "실패",
                    "size": 0
                })
                progress["failed"].append(script_file.name)
                save_progress(progress)
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
            progress["failed"].append(script_file.name)
            save_progress(progress)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 배치 생성 결과 요약")
    print("=" * 60)
    
    failed_count = len(results) - success_count
    
    print(f"\n총 처리: {len(results)}개")
    print(f"  ✅ 성공: {success_count}개")
    print(f"  ❌ 실패: {failed_count}개")
    
    if success_count > 0:
        print(f"\n✅ 성공한 파일:")
        for result in results:
            if result["status"] == "성공":
                print(f"   - {result['audio']} ({result['size'] / 1024:.1f} KB)")
    
    if failed_count > 0:
        print(f"\n❌ 실패한 파일:")
        for result in results:
            if result["status"] != "성공":
                print(f"   - {result['script']}")
        print(f"\n💡 실패한 파일은 나중에 다시 시도할 수 있습니다.")
        print(f"   진행 상황은 {PROGRESS_FILE}에 저장되었습니다.")
    
    print(f"\n🎉 배치 생성 완료!")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
