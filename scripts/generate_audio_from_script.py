#!/usr/bin/env python3
"""
생성된 대본 파일을 기반으로 오디오를 생성하는 스크립트

사용법:
    python scripts/generate_audio_from_script.py output/2025-04-30-공용_PC에서도_안전하게_패스키_OTP_강력한_암호_관리_활용법_script.txt
"""

import sys
import re
from pathlib import Path

# generate_enhanced_audio.py의 함수들을 import
sys.path.insert(0, str(Path(__file__).parent))
from generate_enhanced_audio import (
    text_to_speech,
    log_message,
    OUTPUT_DIR,
    AUDIO_OUTPUT_FORMAT
)


def extract_script_text(script_file_path: Path) -> str:
    """
    대본 파일에서 실제 대본 텍스트를 추출합니다.
    
    Args:
        script_file_path: 대본 파일 경로
        
    Returns:
        추출된 대본 텍스트
    """
    if not script_file_path.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {script_file_path}", "ERROR")
        return ""
    
    try:
        with open(script_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # "강의용 대본" 섹션 찾기
        # "============================================================" 다음에 오는 텍스트가 실제 대본
        pattern = r'강의용 대본\s*\n={10,}\s*\n(.*?)(?:\n\n|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            script_text = match.group(1).strip()
            # 마크다운 강조 제거 (**텍스트** -> 텍스트)
            script_text = re.sub(r'\*\*(.+?)\*\*', r'\1', script_text)
            return script_text
        else:
            # 패턴을 찾지 못한 경우, "강의용 대본" 이후의 모든 텍스트를 사용
            if "강의용 대본" in content:
                parts = content.split("강의용 대본")
                if len(parts) > 1:
                    script_text = parts[-1].strip()
                    # 구분선 제거
                    script_text = re.sub(r'^={10,}\s*$', '', script_text, flags=re.MULTILINE)
                    # 마크다운 강조 제거
                    script_text = re.sub(r'\*\*(.+?)\*\*', r'\1', script_text)
                    return script_text.strip()
            
            # 여전히 찾지 못한 경우, 전체 내용을 사용 (헤더 제거)
            lines = content.split('\n')
            script_started = False
            script_lines = []
            
            for line in lines:
                if "강의용 대본" in line or "=" * 20 in line:
                    script_started = True
                    continue
                if script_started and line.strip():
                    script_lines.append(line)
            
            if script_lines:
                script_text = '\n'.join(script_lines).strip()
                # 마크다운 강조 제거
                script_text = re.sub(r'\*\*(.+?)\*\*', r'\1', script_text)
                return script_text
        
        # 모든 방법 실패 시 전체 내용 반환 (헤더 제외)
        log_message("⚠️ 대본 텍스트를 자동으로 추출하지 못했습니다. 전체 내용을 사용합니다.", "WARNING")
        return content.strip()
        
    except Exception as e:
        log_message(f"❌ 파일 읽기 오류: {str(e)}", "ERROR")
        return ""


def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        log_message("사용법: python scripts/generate_audio_from_script.py <대본_파일_경로>", "ERROR")
        sys.exit(1)
    
    script_file_path = Path(sys.argv[1])
    
    if not script_file_path.is_absolute():
        # 상대 경로인 경우 프로젝트 루트 기준으로 처리
        project_root = Path(__file__).parent.parent
        script_file_path = project_root / script_file_path
    
    log_message("=" * 60)
    log_message("대본 파일 기반 오디오 생성 시작")
    log_message("=" * 60)
    log_message(f"📄 대본 파일: {script_file_path}")
    
    # 대본 텍스트 추출
    script_text = extract_script_text(script_file_path)
    
    if not script_text:
        log_message("❌ 대본 텍스트를 추출할 수 없습니다.", "ERROR")
        sys.exit(1)
    
    log_message(f"✅ 대본 텍스트 추출 완료 ({len(script_text)}자)")
    
    # 출력 파일 경로 생성
    script_stem = script_file_path.stem.replace("_script", "")
    audio_filename = f"{script_stem}_audio.{AUDIO_OUTPUT_FORMAT}"
    audio_path = OUTPUT_DIR / audio_filename
    
    log_message(f"🎤 오디오 생성 시작: {audio_path}")
    
    # 오디오 생성
    success = text_to_speech(script_text, audio_path)
    
    if success:
        log_message("=" * 60)
        log_message("✅ 오디오 생성 완료!")
        log_message(f"📁 출력 파일: {audio_path}")
        log_message("=" * 60)
    else:
        log_message("=" * 60)
        log_message("❌ 오디오 생성 실패")
        log_message("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
