#!/usr/bin/env python3
"""
여러 대본 파일을 일괄로 확장하는 스크립트

1.5배속 기준 최소 5분 분량이 되도록 모든 대본을 확장
"""

import os
import sys
from pathlib import Path

# expand_script_with_gemini 모듈 import
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from expand_script_with_gemini import (
    extract_script_content,
    read_post_content,
    expand_script_with_gemini_pro,
    segment_for_remotion,
    save_expanded_script,
    TARGET_CHARS,
    TARGET_MINUTES,
    OUTPUT_DIR
)

def check_script_length(script_path: Path) -> tuple:
    """대본 길이 확인"""
    try:
        text, metadata = extract_script_content(script_path)
        if not text:
            return None, None, None
        
        # Remotion 구간 분할로 실제 길이 계산
        segments = segment_for_remotion(text)
        total_duration = sum(s["duration"] for s in segments)
        speed_15x_duration = total_duration / 90  # 1.5배속 기준
        
        return len(text), total_duration, speed_15x_duration
    except Exception as e:
        print(f"   ⚠️ 확인 오류: {str(e)}")
        return None, None, None

def main():
    """메인 함수"""
    print("=" * 60)
    print("📝 모든 대본 파일 확인 및 확장")
    print("=" * 60)
    
    # 모든 script_improved.txt 파일 찾기
    script_files = sorted(OUTPUT_DIR.glob("*_script_improved.txt"))
    
    if not script_files:
        print("❌ 대본 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    print(f"\n📂 발견된 대본 파일: {len(script_files)}개\n")
    
    # 각 파일 확인
    needs_expansion = []
    
    for script_file in script_files:
        print(f"확인 중: {script_file.name}")
        length, duration, speed_15x = check_script_length(script_file)
        
        if length is None:
            print(f"   ⚠️ 확인 불가\n")
            continue
        
        print(f"   길이: {length}자, 1.5배속 기준: {speed_15x:.1f}분")
        
        if speed_15x < TARGET_MINUTES:
            needs_expansion.append((script_file, length, speed_15x))
            print(f"   ❌ 목표 미달 (목표: {TARGET_MINUTES}분)")
        else:
            print(f"   ✅ 목표 달성")
        print()
    
    if not needs_expansion:
        print("✅ 모든 대본이 목표 분량을 충족합니다!")
        return 0
    
    print(f"\n📊 확장이 필요한 파일: {len(needs_expansion)}개\n")
    
    # 사용자 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        auto_expand = True
    else:
        response = input("확장을 진행하시겠습니까? (y/n): ")
        auto_expand = response.lower() == 'y'
    
    if not auto_expand:
        print("취소되었습니다.")
        return 0
    
    # 확장 진행
    print("\n" + "=" * 60)
    print("🚀 대본 확장 시작")
    print("=" * 60 + "\n")
    
    results = []
    
    for i, (script_file, current_length, current_duration) in enumerate(needs_expansion, 1):
        print(f"\n[{i}/{len(needs_expansion)}] {script_file.name}")
        print(f"   현재: {current_length}자 ({current_duration:.1f}분)")
        print(f"   목표: {TARGET_CHARS}자 이상 ({TARGET_MINUTES}분)")
        
        try:
            # 대본 읽기
            original_text, metadata = extract_script_content(script_file)
            if not original_text:
                print("   ❌ 대본 텍스트를 추출할 수 없습니다.")
                continue
            
            # 원본 포스트 읽기
            post_filename = metadata.get("원본 포스트", "")
            post_content = ""
            if post_filename:
                post_content = read_post_content(post_filename)
                if not post_content:
                    print("   ⚠️ 원본 포스트를 읽을 수 없습니다. 대본만으로 확장합니다.")
            
            # Gemini Pro로 확장
            expanded_text = expand_script_with_gemini_pro(original_text, post_content, TARGET_CHARS)
            
            if len(expanded_text) < TARGET_CHARS * 0.8:
                print(f"   ⚠️ 확장된 대본이 목표 길이에 미치지 못합니다: {len(expanded_text)}자")
            
            # Remotion 구간 분할
            segments = segment_for_remotion(expanded_text)
            total_duration = sum(s["duration"] for s in segments)
            speed_15x_duration = total_duration / 90
            
            print(f"   확장 후: {len(expanded_text)}자 ({speed_15x_duration:.1f}분)")
            
            if speed_15x_duration < TARGET_MINUTES:
                print(f"   ⚠️ 여전히 목표 미달")
            else:
                print(f"   ✅ 목표 달성!")
            
            # 저장
            output_path, json_path = save_expanded_script(script_file, expanded_text, segments, metadata)
            
            if output_path:
                results.append({
                    "file": script_file.name,
                    "before": current_length,
                    "after": len(expanded_text),
                    "duration": speed_15x_duration,
                    "success": speed_15x_duration >= TARGET_MINUTES
                })
                print(f"   ✅ 저장 완료")
            else:
                print(f"   ❌ 저장 실패")
                
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 확장 결과 요약")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["success"])
    
    for result in results:
        status = "✅" if result["success"] else "⚠️"
        print(f"\n{status} {result['file']}")
        print(f"   {result['before']}자 → {result['after']}자")
        print(f"   1.5배속 기준: {result['duration']:.1f}분")
    
    print(f"\n총 {len(results)}개 파일 처리 완료")
    print(f"목표 달성: {success_count}개 / {len(results)}개")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
