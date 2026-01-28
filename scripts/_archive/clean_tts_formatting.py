#!/usr/bin/env python3
"""
대본 파일에서 TTS에 방해되는 마크다운 형식을 제거하는 스크립트
- ** (볼드 마크다운) 제거
- `코드` (인라인 코드) 제거
- [서론], [본론], [결론] 같은 라벨 제거
"""

import os
import re
import glob
from pathlib import Path

def clean_tts_formatting(text):
    """TTS에 방해되는 마크다운 형식을 제거"""
    # **텍스트** 패턴 제거 (볼드 마크다운)
    # 반복적으로 처리하여 모든 ** 패턴 제거
    while True:
        new_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        if new_text == text:
            break
        text = new_text
    
    # 짝이 맞지 않는 ** 패턴도 제거 (예: "text**" 또는 "**text")
    text = re.sub(r'\*\*([^*\n]+)', r'\1', text)  # **로 시작하지만 끝나지 않은 경우
    text = re.sub(r'([^*\n]+)\*\*', r'\1', text)  # **로 끝나지만 시작하지 않은 경우
    
    # `코드` 패턴 제거 (인라인 코드)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # [서론], [본론], [결론], [30초 요약] 같은 라벨 제거
    text = re.sub(r'\[30초 요약[^\]]*\]', '', text)
    text = re.sub(r'\[서론\]', '', text)
    text = re.sub(r'\[본론\]', '', text)
    text = re.sub(r'\[결론\]', '', text)
    
    return text

def process_file(file_path):
    """단일 파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remotion 구간 정보 섹션 시작 위치 찾기
        remotion_marker = 'Remotion 동기화 구간 정보'
        remotion_start = content.find(remotion_marker)
        
        if remotion_start != -1:
            # Remotion 구간 정보가 있으면 그 이전까지만 처리
            main_content = content[:remotion_start]
            remotion_content = content[remotion_start:]
            
            # 메인 대본 부분과 Remotion 구간 정보 모두 정리
            cleaned_main = clean_tts_formatting(main_content)
            cleaned_remotion = clean_tts_formatting(remotion_content)
            
            # 다시 합치기
            cleaned_content = cleaned_main + cleaned_remotion
        else:
            # Remotion 구간 정보가 없으면 전체 처리
            cleaned_content = clean_tts_formatting(content)
        
        # 변경사항이 있으면 파일 저장
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    # output 디렉토리의 모든 script 파일 찾기
    output_dir = Path(__file__).parent.parent / 'output'
    script_files = list(output_dir.glob('*_script*.txt'))
    
    print(f"Found {len(script_files)} script files")
    
    processed_count = 0
    for script_file in script_files:
        if process_file(script_file):
            processed_count += 1
            print(f"Processed: {script_file.name}")
    
    print(f"\nTotal processed: {processed_count} files")

if __name__ == '__main__':
    main()
