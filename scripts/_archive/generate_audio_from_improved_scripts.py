#!/usr/bin/env python3
"""
개선된 대본 파일들을 기반으로 오디오를 생성하는 스크립트

개선된 대본(_improved.txt) 파일들을 찾아서 Gemini TTS로 오디오를 생성합니다.
"""

import os
import sys
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 환경 변수 로드
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
        
        # "개선된 강의용 대본" 섹션 찾기
        if "개선된 강의용 대본" in content:
            parts = content.split("개선된 강의용 대본")
            if len(parts) > 1:
                script_text = parts[1].strip()
                # 구분선 제거
                script_text = re.sub(r'^={10,}\s*$', '', script_text, flags=re.MULTILINE)
                # Remotion 구간 정보 섹션 제거
                if "Remotion 동기화 구간 정보" in script_text:
                    script_text = script_text.split("Remotion 동기화 구간 정보")[0].strip()
                return script_text.strip()
        
        # "강의용 대본" 섹션 찾기 (fallback)
        if "강의용 대본" in content:
            parts = content.split("강의용 대본")
            if len(parts) > 1:
                script_text = parts[1].strip()
                script_text = re.sub(r'^={10,}\s*$', '', script_text, flags=re.MULTILINE)
                if "Remotion 동기화 구간 정보" in script_text:
                    script_text = script_text.split("Remotion 동기화 구간 정보")[0].strip()
                return script_text.strip()
        
        # 전체 내용에서 메타데이터 제거
        lines = content.split("\n")
        script_lines = []
        in_script = False
        
        for line in lines:
            if "개선된 강의용 대본" in line or "강의용 대본" in line or "=" * 10 in line:
                in_script = True
                continue
            if "Remotion 동기화 구간 정보" in line:
                break
            if in_script and line.strip():
                script_lines.append(line.strip())
        
        return "\n".join(script_lines).strip() if script_lines else content.strip()
    except Exception as e:
        print(f"❌ 대본 파일 읽기 오류: {str(e)}")
        return ""

def main():
    """메인 함수"""
    print("=" * 60)
    print("🎤 개선된 대본 기반 오디오 생성")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)
    
    print(f"📢 Voice: {GEMINI_TTS_VOICE_NAME} (IT 전문가용)")
    
    # 개선된 대본 파일 찾기
    improved_scripts = sorted(
        OUTPUT_DIR.glob("*_improved.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not improved_scripts:
        print("❌ 개선된 대본 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 명령줄 인자로 특정 파일 지정 가능
    if len(sys.argv) > 1:
        target_file = Path(sys.argv[1])
        if not target_file.is_absolute():
            target_file = OUTPUT_DIR / target_file
        if target_file.exists() and target_file.name.endswith("_improved.txt"):
            improved_scripts = [target_file]
        else:
            print(f"❌ 파일을 찾을 수 없거나 개선된 대본 파일이 아닙니다: {target_file}")
            sys.exit(1)
    
    print(f"\n📂 발견된 개선된 대본: {len(improved_scripts)}개\n")
    
    results = []
    
    for script_file in improved_scripts:
        print(f"\n{'=' * 60}")
        print(f"처리 중: {script_file.name}")
        print(f"{'=' * 60}")
        
        # 대본 텍스트 추출
        script_text = extract_improved_script_text(script_file)
        
        if not script_text:
            print(f"⚠️ 대본 텍스트를 추출할 수 없습니다. 건너뜁니다.")
            continue
        
        print(f"📝 대본 길이: {len(script_text)}자")
        
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
        
        print(f"🎤 Gemini TTS로 오디오 생성 중...")
        print(f"   출력 파일: {audio_path}")
        
        try:
            success = text_to_speech_with_gemini(script_text, audio_path)
            
            if success and audio_path.exists():
                file_size = audio_path.stat().st_size
                print(f"✅ 오디오 생성 완료!")
                print(f"   파일 크기: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                print(f"   파일 경로: {audio_path}")
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
