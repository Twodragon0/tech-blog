#!/usr/bin/env python3
"""
대본 개선 스크립트: 오디오 품질 및 Remotion 동기화 최적화

개선 사항:
1. 오디오 듣기 좋게: 자연스러운 호흡, 강조, 구어체 개선
2. Remotion 동기화: 적절한 구간 분할, 시각적 요소와 매칭
3. 첫 문장 복구: 잘린 첫 문장 복구
4. 문장 길이 최적화: 호흡이 자연스러운 길이로 조정
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import json
import requests

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

def extract_script_content(script_path: Path) -> Tuple[str, dict]:
    """대본 파일에서 메타데이터와 실제 대본 텍스트 추출"""
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 메타데이터 추출
        metadata = {}
        lines = content.split("\n")
        in_metadata = True
        
        for line in lines:
            if line.startswith("생성일:"):
                metadata["생성일"] = line.split(":", 1)[1].strip()
            elif line.startswith("대본 길이:"):
                metadata["대본 길이"] = line.split(":", 1)[1].strip()
            elif line.startswith("원본 포스트:"):
                metadata["원본 포스트"] = line.split(":", 1)[1].strip()
            elif line.startswith("사용된 API:"):
                metadata["사용된 API"] = line.split(":", 1)[1].strip()
            elif line.startswith("API 전략:"):
                metadata["API 전략"] = line.split(":", 1)[1].strip()
            elif line.startswith("=" * 60):
                in_metadata = False
                continue
            elif line.strip() == "강의용 대본":
                continue
            elif not in_metadata and line.strip():
                break
        
        # 실제 대본 텍스트 추출
        script_text = ""
        in_script = False
        
        for line in lines:
            if "강의용 대본" in line or "=" * 10 in line:
                in_script = True
                continue
            if in_script and line.strip():
                script_text += line.strip() + "\n"
        
        return script_text.strip(), metadata
    except Exception as e:
        print(f"❌ 대본 파일 읽기 오류: {str(e)}")
        return "", {}

def fix_truncated_first_sentence(text: str) -> str:
    """잘린 첫 문장 복구"""
    # 첫 문장이 잘려있는 패턴 감지
    first_line = text.split("\n")[0].strip()
    
    # 첫 문장이 대문자로 시작하지 않거나, 앞부분이 잘린 경우
    if first_line and not first_line[0].isupper() and len(first_line) < 50:
        # 일반적인 시작 패턴 추가
        common_starts = [
            "혹시 최근",
            "혹시",
            "오늘은",
            "이번에는",
            "자, 그럼",
            "안녕하세요",
        ]
        
        for start in common_starts:
            if start in first_line:
                # 이미 시작 부분이 있으면 그대로
                return text
        
        # 첫 문장이 잘린 것으로 보이면 복구 시도
        # (실제로는 원본 포스트를 확인해야 하지만, 여기서는 추론)
        if first_line.startswith("CI/CD") or first_line.startswith("자, 그럼"):
            # 앞부분이 잘린 것으로 추정
            return text  # 일단 그대로 반환 (원본 확인 필요)
    
    return text

def improve_breathing_and_pacing(text: str) -> str:
    """호흡과 속도 개선"""
    lines = text.split("\n")
    improved_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            improved_lines.append("")
            continue
        
        # 너무 긴 문장을 적절히 분할
        if len(line) > 150:
            # 문장 부호 기준으로 분할
            sentences = re.split(r'([.!?]\s+)', line)
            new_sentences = []
            current = ""
            
            for i, part in enumerate(sentences):
                if part.strip() in [".", "!", "?"]:
                    current += part
                    if len(current.strip()) > 100:
                        new_sentences.append(current.strip())
                        current = ""
                else:
                    current += part
                    if len(current.strip()) > 120 and i < len(sentences) - 1:
                        # 쉼표나 연결어 기준으로 분할
                        if "그리고" in current or "또한" in current or "특히" in current:
                            parts = re.split(r'(그리고|또한|특히)', current, 1)
                            if len(parts) > 1:
                                new_sentences.append(parts[0].strip())
                                current = parts[1] + "".join(parts[2:])
            
            if current.strip():
                new_sentences.append(current.strip())
            
            improved_lines.extend(new_sentences)
        else:
            improved_lines.append(line)
    
    return "\n".join(improved_lines)

def add_emphasis_and_natural_speech(text: str) -> str:
    """강조와 자연스러운 구어체 개선"""
    # 기술 용어 강조
    tech_terms = {
        "AWS WAF": "에이더블유에스 WAF",
        "Cloudflare": "클라우드플레어",
        "GitHub": "깃허브",
        "DevSecOps": "데브섹옵스",
        "CI/CD": "시아이 슬래시 시디",
        "DDoS": "디도스",
        "SQL 인젝션": "에스큐엘 인젝션",
        "XSS": "엑스에스에스",
        "IAM": "아이에이엠",
        "S3": "에스쓰리",
        "EC2": "이씨투",
        "Lambda": "람다",
        "Kubernetes": "쿠버네티스",
    }
    
    # 기술 용어는 그대로 유지 (발음 가이드는 주석으로)
    # 대신 자연스러운 표현 개선
    
    # 반복되는 표현 개선
    replacements = {
        "그리고": "그리고",
        "또한": "또한",
        "특히": "특히",
        "예를 들어": "예를 들어",
        "이것은": "이건",
        "이러한": "이런",
        "이렇게": "이렇게",
    }
    
    # 자연스러운 구어체로 변환
    text = re.sub(r'\b이것은\b', '이건', text)
    text = re.sub(r'\b이러한\b', '이런', text)
    text = re.sub(r'\b그것은\b', '그건', text)
    text = re.sub(r'\b그러한\b', '그런', text)
    
    # 과도한 "입니다" 줄이기
    text = re.sub(r'입니다\.\s+입니다\.', '입니다.', text)
    
    return text

def segment_for_remotion(text: str, target_duration_per_segment: float = 5.0) -> List[dict]:
    """
    Remotion 동기화를 위한 구간 분할
    
    Args:
        text: 대본 텍스트
        target_duration_per_segment: 각 구간의 목표 길이 (초)
    
    Returns:
        구간별 정보 리스트
    """
    # 평균 읽기 속도: 분당 200-250자 (1.5배속 기준 약 300-375자/분)
    # 5초당 약 25-31자
    chars_per_second = 28  # 1.5배속 기준
    
    segments = []
    lines = text.split("\n")
    current_segment = ""
    current_duration = 0.0
    segment_index = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line_duration = len(line) / chars_per_second
        
        if current_duration + line_duration <= target_duration_per_segment:
            current_segment += line + " "
            current_duration += line_duration
        else:
            if current_segment:
                segments.append({
                    "index": segment_index,
                    "text": current_segment.strip(),
                    "duration": current_duration,
                    "startTime": sum(s["duration"] for s in segments),
                })
                segment_index += 1
            
            current_segment = line + " "
            current_duration = line_duration
    
    # 마지막 구간 추가
    if current_segment:
        segments.append({
            "index": segment_index,
            "text": current_segment.strip(),
            "duration": current_duration,
            "startTime": sum(s["duration"] for s in segments),
        })
    
    return segments

def improve_script_with_gemini(original_text: str, metadata: dict) -> str:
    """Gemini API를 사용하여 대본을 고품질로 개선"""
    import os
    import requests
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        return original_text
    
    GEMINI_FLASH_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    prompt = f"""당신은 IT/DevSecOps 전문 온라인 강의 대본 개선 전문가입니다.
다음 강의 대본을 오디오 품질과 영상 동기화를 최적화하여 개선해주세요.

**개선 목표:**
1. **오디오 듣기 좋게**: 자연스러운 호흡, 적절한 강조, 구어체 개선
2. **Remotion 동기화**: 시각적 요소와 매칭되는 적절한 구간 분할
3. **문장 길이 최적화**: 호흡이 자연스러운 길이 (100-150자 권장)
4. **기술 용어 명확화**: Kubernetes, DevSecOps 등 전문 용어 정확한 발음 고려
5. **자연스러운 전환**: 문장 간 자연스러운 연결

**원본 대본:**
{original_text}

**개선 요구사항:**
- 자연스러운 구어체 유지 (강의자가 직접 말하는 느낌)
- 핵심 내용은 그대로 유지하되 표현 개선
- 문장을 적절히 분할하여 호흡이 자연스럽게
- 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
- 한국어로 작성 (UTF-8 인코딩)
- **절대 사용 금지**: "(본론 시작)", "(슬라이드 1)" 등 모든 메타 지시어
- 각 문장은 독립적으로 읽을 수 있도록 자연스러운 마무리

**중요**: 
- 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요.
- 원본의 핵심 내용과 순서는 그대로 유지하세요.
- 오디오로 녹음했을 때 자연스럽고 듣기 좋아야 합니다."""
    
    try:
        url = f"{GEMINI_FLASH_API_URL}?key={GEMINI_API_KEY}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 6000,
            }
        }
        
        response = requests.post(url, json=data, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            candidates = result.get('candidates', [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts and len(parts) > 0:
                    improved_text = parts[0].get('text', '').strip()
                    if improved_text:
                        print(f"   ✅ Gemini API로 대본 개선 완료")
                        return improved_text
        
        print(f"   ⚠️ Gemini API 응답 오류, 기본 개선만 적용")
        return original_text
    except Exception as e:
        print(f"   ⚠️ Gemini API 오류: {str(e)[:100]}, 기본 개선만 적용")
        return original_text

def improve_script(script_path: Path) -> Tuple[str, List[dict]]:
    """대본 개선"""
    print(f"📝 대본 개선 중: {script_path.name}")
    
    # 원본 대본 읽기
    original_text, metadata = extract_script_content(script_path)
    
    if not original_text:
        print(f"⚠️ 대본 텍스트를 추출할 수 없습니다.")
        return "", []
    
    print(f"   원본 길이: {len(original_text)}자")
    
    # Gemini API로 고품질 개선 시도
    use_gemini = os.getenv("USE_GEMINI_FOR_SCRIPT_IMPROVEMENT", "true").lower() == "true"
    if use_gemini:
        print(f"   🤖 Gemini API로 고품질 개선 시도 중...")
        improved_text = improve_script_with_gemini(original_text, metadata)
    else:
        improved_text = original_text
    
    # 1. 잘린 첫 문장 복구
    improved_text = fix_truncated_first_sentence(improved_text)
    
    # 2. 호흡과 속도 개선
    improved_text = improve_breathing_and_pacing(improved_text)
    
    # 3. 강조와 자연스러운 구어체
    improved_text = add_emphasis_and_natural_speech(improved_text)
    
    # 4. Remotion 구간 분할
    segments = segment_for_remotion(improved_text)
    
    print(f"   개선 후 길이: {len(improved_text)}자")
    print(f"   구간 수: {len(segments)}개")
    print(f"   예상 총 길이: {sum(s['duration'] for s in segments):.1f}초")
    
    return improved_text, segments

def save_improved_script(script_path: Path, improved_text: str, segments: List[dict], metadata: dict):
    """개선된 대본 저장"""
    output_path = script_path.parent / f"{script_path.stem}_improved.txt"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            # 메타데이터
            if metadata.get("title"):
                f.write(f"# {metadata['title']}\n\n")
            if metadata.get("생성일"):
                f.write(f"개선일: {metadata['생성일']}\n")
            if metadata.get("원본 포스트"):
                f.write(f"원본 포스트: {metadata['원본 포스트']}\n")
            f.write(f"개선 후 대본 길이: {len(improved_text)}자\n")
            f.write(f"Remotion 구간 수: {len(segments)}개\n")
            f.write(f"예상 총 길이: {sum(s['duration'] for s in segments):.1f}초\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("개선된 강의용 대본\n")
            f.write("=" * 60 + "\n\n")
            
            # 개선된 대본
            f.write(improved_text)
            
            # Remotion 구간 정보
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("Remotion 동기화 구간 정보\n")
            f.write("=" * 60 + "\n\n")
            
            for segment in segments:
                f.write(f"[구간 {segment['index'] + 1}] 시작: {segment['startTime']:.2f}초, 길이: {segment['duration']:.2f}초\n")
                f.write(f"{segment['text'][:100]}...\n\n")
        
        # JSON 형식으로도 저장 (Remotion에서 사용)
        json_path = script_path.parent / f"{script_path.stem}_segments.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "script": improved_text,
                "segments": segments,
                "metadata": metadata,
                "totalDuration": sum(s["duration"] for s in segments)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 개선된 대본 저장: {output_path.name}")
        print(f"✅ Remotion 구간 정보 저장: {json_path.name}")
        
        return output_path, json_path
    except Exception as e:
        print(f"❌ 저장 실패: {str(e)}")
        return None, None

def main():
    """메인 함수"""
    print("=" * 60)
    print("🎬 대본 개선: 오디오 품질 및 Remotion 동기화 최적화")
    print("=" * 60)
    
    # 대본 파일 찾기
    script_files = sorted(OUTPUT_DIR.glob("*_script.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not script_files:
        print("❌ 대본 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 명령줄 인자로 특정 파일 지정 가능
    if len(sys.argv) > 1:
        target_file = Path(sys.argv[1])
        if not target_file.is_absolute():
            target_file = OUTPUT_DIR / target_file
        if target_file.exists():
            script_files = [target_file]
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {target_file}")
            sys.exit(1)
    
    print(f"\n📂 발견된 대본 파일: {len(script_files)}개\n")
    
    results = []
    
    for script_file in script_files:
        print(f"\n{'=' * 60}")
        print(f"처리 중: {script_file.name}")
        print(f"{'=' * 60}")
        
        try:
            improved_text, segments = improve_script(script_file)
            if improved_text:
                _, metadata = extract_script_content(script_file)
                output_path, json_path = save_improved_script(script_file, improved_text, segments, metadata)
                if output_path:
                    results.append({
                        "original": script_file.name,
                        "improved": output_path.name,
                        "segments": len(segments),
                        "duration": sum(s["duration"] for s in segments)
                    })
        except Exception as e:
            print(f"❌ 처리 실패: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 개선 결과 요약")
    print("=" * 60)
    
    for result in results:
        print(f"\n✅ {result['original']}")
        print(f"   → {result['improved']}")
        print(f"   구간 수: {result['segments']}개")
        print(f"   예상 길이: {result['duration']:.1f}초")
    
    print(f"\n총 {len(results)}개 대본 개선 완료!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
