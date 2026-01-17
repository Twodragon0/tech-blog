#!/usr/bin/env python3
"""
Gemini Pro를 사용하여 강의용 대본을 확장하는 스크립트

요구사항:
- 1.5배속으로 최소 5분 분량 (일반 속도로는 약 7.5분)
- 약 1500-2000자 분량 필요
- Gemini Pro 모델 적극 활용
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Tuple, List
import requests
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
POSTS_DIR = PROJECT_ROOT / "_posts"

# .env 파일에서 환경 변수 로드
def load_env_file():
    """프로젝트 루트의 .env 파일에서 환경 변수 로드"""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # 따옴표 제거
                        value = value.strip().strip('"').strip("'")
                        os.environ[key.strip()] = value
        except Exception as e:
            print(f"⚠️ .env 파일 읽기 오류: {str(e)}")

# .env 파일 로드
load_env_file()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_PRO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

# 목표 분량 설정
TARGET_MINUTES = 5.0  # 1.5배속 기준 5분
NORMAL_SPEED_MINUTES = TARGET_MINUTES * 1.5  # 일반 속도로는 7.5분
CHARS_PER_MINUTE = 200  # 분당 약 200자 (자연스러운 말하기 속도)
TARGET_CHARS = int(NORMAL_SPEED_MINUTES * CHARS_PER_MINUTE)  # 약 1500자

def read_post_content(post_filename: str) -> str:
    """원본 포스트 파일 읽기"""
    post_path = POSTS_DIR / post_filename
    if not post_path.exists():
        print(f"❌ 원본 포스트를 찾을 수 없습니다: {post_path}")
        return ""
    
    try:
        with open(post_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ 포스트 읽기 오류: {str(e)}")
        return ""

def extract_script_content(script_path: Path) -> Tuple[str, dict]:
    """대본 파일에서 메타데이터와 실제 대본 텍스트 추출"""
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 메타데이터 추출
        metadata = {}
        lines = content.split("\n")
        
        for line in lines:
            if line.startswith("원본 포스트:"):
                metadata["원본 포스트"] = line.split(":", 1)[1].strip()
            elif line.startswith("개선 후 대본 길이:"):
                metadata["대본 길이"] = line.split(":", 1)[1].strip()
            elif "=" * 60 in line:
                break
        
        # 실제 대본 텍스트 추출
        script_text = ""
        in_script = False
        
        for line in lines:
            if "개선된 강의용 대본" in line or "=" * 10 in line:
                in_script = True
                continue
            if in_script and line.strip() and not line.startswith("="):
                if "Remotion 동기화 구간 정보" in line:
                    break
                script_text += line.strip() + "\n"
        
        return script_text.strip(), metadata
    except Exception as e:
        print(f"❌ 대본 파일 읽기 오류: {str(e)}")
        return "", {}

def expand_script_with_gemini_pro(original_script: str, post_content: str, target_length: int) -> str:
    """Gemini Pro를 사용하여 대본을 확장"""
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   export GEMINI_API_KEY='your-key'")
        return original_script
    
    # 원본 포스트에서 핵심 내용 추출 (요약 부분 활용)
    post_summary = ""
    if "핵심 내용" in post_content:
        # AI 요약 카드에서 핵심 내용 추출
        summary_match = re.search(r'<li><strong>([^<]+)</strong>([^<]+)</li>', post_content)
        if summary_match:
            post_summary = summary_match.group(0)
    
    # 본문 내용 추출 (마크다운 제거)
    body_content = re.sub(r'^---.*?---', '', post_content, flags=re.DOTALL)
    body_content = re.sub(r'<[^>]+>', '', body_content)  # HTML 태그 제거
    body_content = re.sub(r'```[\s\S]*?```', '', body_content)  # 코드 블록 제거
    body_content = re.sub(r'#{1,6}\s+', '', body_content)  # 헤더 제거
    body_content = body_content[:3000]  # 처음 3000자만 사용
    
    prompt = f"""당신은 IT/DevSecOps 전문 온라인 강의 대본 작성 전문가입니다.
다음 짧은 대본을 원본 블로그 포스트 내용을 바탕으로 확장하여, 1.5배속으로 최소 5분 분량(일반 속도로는 약 7.5분, 약 {target_length}자)이 되도록 작성해주세요.

**원본 대본 (현재 {len(original_script)}자):**
{original_script}

**원본 포스트 핵심 내용:**
{body_content[:2000]}

**확장 요구사항:**
1. **분량**: 최소 {target_length}자 이상 (1.5배속으로 5분 분량)
2. **내용**: 원본 포스트의 핵심 내용을 모두 포함
   - SKT USIM 정보 유출 사태 배경 및 위험성
   - SIM 스와핑/복제 공격 메커니즘과 피해 사례
   - IMEI 확인 방법 (아이폰, 안드로이드)
   - USIM/eSIM 교체 절차 및 주의사항
   - MFA/OTP의 중요성 및 권장 방법
   - 2025년 업데이트된 통신사 보안 강화 조치
   - 기업 보안 시사점 (공급망 보안, Zero Trust 등)
3. **스타일**: 
   - 자연스러운 구어체 (강의자가 직접 말하는 느낌)
   - 기술 용어는 정확하게 사용하되 이해하기 쉽게 설명
   - 문장 길이는 100-150자 권장 (자연스러운 호흡)
   - 핵심 내용을 강조하되 과하지 않게
4. **구조**:
   - 서론: 문제 제기 및 중요성 강조
   - 본론: 각 주제별 상세 설명
   - 결론: 핵심 요약 및 실천 방안
5. **금지 사항**:
   - "(본론 시작)", "(슬라이드 1)" 등 모든 메타 지시어 사용 금지
   - 원본 포스트에 없는 내용 추가 금지
   - 과도한 반복 지양

**중요**: 
- 대본은 순수한 강의 내용만 포함해야 하며, 지시어나 메타 정보는 전혀 포함하지 마세요.
- 원본 포스트의 핵심 내용을 모두 포함하되, 자연스럽고 듣기 좋게 작성하세요.
- 오디오로 녹음했을 때 자연스럽고 전문가다운 느낌이 나야 합니다.
- DevSecOps 전문가 관점에서 실무적이고 실용적인 내용으로 작성하세요."""

    try:
        url = f"{GEMINI_PRO_API_URL}?key={GEMINI_API_KEY}"
        
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
                "maxOutputTokens": 8000,  # 충분한 토큰 할당
            }
        }
        
        print(f"   🤖 Gemini Pro로 대본 확장 중... (목표: {target_length}자 이상)")
        response = requests.post(url, json=data, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            candidates = result.get('candidates', [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts and len(parts) > 0:
                    expanded_text = parts[0].get('text', '').strip()
                    if expanded_text:
                        # 코드 블록이나 마크다운 제거
                        expanded_text = re.sub(r'```[\s\S]*?```', '', expanded_text)
                        expanded_text = re.sub(r'^\*\*.*?\*\*', '', expanded_text, flags=re.MULTILINE)
                        expanded_text = re.sub(r'^#+\s+', '', expanded_text, flags=re.MULTILINE)
                        expanded_text = expanded_text.strip()
                        
                        print(f"   ✅ Gemini Pro로 대본 확장 완료: {len(expanded_text)}자")
                        return expanded_text
            else:
                print(f"   ⚠️ Gemini Pro API 응답에 candidates가 없습니다.")
                print(f"   응답: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
        else:
            print(f"   ⚠️ Gemini Pro API HTTP 오류: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   오류 상세: {json.dumps(error_detail, ensure_ascii=False, indent=2)[:500]}")
            except:
                print(f"   응답 본문: {response.text[:500]}")
        
        return original_script
    except Exception as e:
        print(f"   ⚠️ Gemini Pro API 오류: {str(e)[:100]}")
        return original_script

def segment_for_remotion(text: str, target_duration_per_segment: float = 5.0) -> List[dict]:
    """Remotion 동기화를 위한 구간 분할"""
    # 1.5배속 기준: 분당 약 300자
    chars_per_second = 5.0  # 초당 약 5자 (1.5배속 기준)
    
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

def save_expanded_script(script_path: Path, expanded_text: str, segments: List[dict], metadata: dict):
    """확장된 대본 저장"""
    output_path = script_path.parent / f"{script_path.stem}_improved.txt"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            # 메타데이터
            f.write(f"개선일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if metadata.get("원본 포스트"):
                f.write(f"원본 포스트: {metadata['원본 포스트']}\n")
            f.write(f"개선 후 대본 길이: {len(expanded_text)}자\n")
            f.write(f"Remotion 구간 수: {len(segments)}개\n")
            total_duration = sum(s["duration"] for s in segments)
            f.write(f"예상 총 길이: {total_duration:.1f}초 ({total_duration/60:.1f}분, 1.5배속 기준 {total_duration/90:.1f}분)\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("개선된 강의용 대본\n")
            f.write("=" * 60 + "\n\n")
            
            # 확장된 대본
            f.write(expanded_text)
            
            # Remotion 구간 정보
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("Remotion 동기화 구간 정보\n")
            f.write("=" * 60 + "\n\n")
            
            for segment in segments:
                f.write(f"[구간 {segment['index'] + 1}] 시작: {segment['startTime']:.2f}초, 길이: {segment['duration']:.2f}초\n")
                preview = segment['text'][:100] + "..." if len(segment['text']) > 100 else segment['text']
                f.write(f"{preview}\n\n")
        
        # JSON 형식으로도 저장
        json_path = script_path.parent / f"{script_path.stem}_segments.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "script": expanded_text,
                "segments": segments,
                "metadata": metadata,
                "totalDuration": sum(s["duration"] for s in segments),
                "targetMinutes": TARGET_MINUTES,
                "normalSpeedMinutes": NORMAL_SPEED_MINUTES
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 확장된 대본 저장: {output_path.name}")
        print(f"✅ Remotion 구간 정보 저장: {json_path.name}")
        
        return output_path, json_path
    except Exception as e:
        print(f"❌ 저장 실패: {str(e)}")
        return None, None

def main():
    """메인 함수"""
    print("=" * 60)
    print("📝 Gemini Pro를 사용한 강의용 대본 확장")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   export GEMINI_API_KEY='your-key'")
        sys.exit(1)
    
    # 명령줄 인자로 파일 지정
    if len(sys.argv) < 2:
        print("사용법: python expand_script_with_gemini.py <script_file>")
        print("예시: python expand_script_with_gemini.py output/2025-04-29-SKT_보안_이슈_완벽_대응_가이드_IMEI_확인_USIMeSIM_교체_그리고_MFA의_중요성_script_improved.txt")
        sys.exit(1)
    
    script_file = Path(sys.argv[1])
    if not script_file.is_absolute():
        script_file = OUTPUT_DIR / script_file.name if script_file.name.startswith("2025") else OUTPUT_DIR / script_file
    
    if not script_file.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {script_file}")
        sys.exit(1)
    
    print(f"\n📂 처리할 파일: {script_file.name}\n")
    
    # 대본 읽기
    original_text, metadata = extract_script_content(script_file)
    if not original_text:
        print("❌ 대본 텍스트를 추출할 수 없습니다.")
        sys.exit(1)
    
    print(f"   원본 길이: {len(original_text)}자")
    print(f"   목표 길이: {TARGET_CHARS}자 이상 (1.5배속 기준 {TARGET_MINUTES}분)")
    
    # 원본 포스트 읽기
    post_filename = metadata.get("원본 포스트", "")
    if not post_filename:
        print("⚠️ 원본 포스트 정보를 찾을 수 없습니다.")
        post_content = ""
    else:
        post_content = read_post_content(post_filename)
        if not post_content:
            print("⚠️ 원본 포스트를 읽을 수 없습니다. 대본만으로 확장합니다.")
    
    # Gemini Pro로 대본 확장
    expanded_text = expand_script_with_gemini_pro(original_text, post_content, TARGET_CHARS)
    
    if len(expanded_text) < TARGET_CHARS * 0.8:  # 목표의 80% 미만이면 경고
        print(f"⚠️ 확장된 대본이 목표 길이({TARGET_CHARS}자)에 미치지 못합니다: {len(expanded_text)}자")
    
    # Remotion 구간 분할
    segments = segment_for_remotion(expanded_text)
    total_duration = sum(s["duration"] for s in segments)
    
    print(f"\n   확장 후 길이: {len(expanded_text)}자")
    print(f"   구간 수: {len(segments)}개")
    print(f"   예상 총 길이: {total_duration:.1f}초 ({total_duration/60:.1f}분)")
    print(f"   1.5배속 기준: {total_duration/90:.1f}분")
    
    if total_duration/90 < TARGET_MINUTES:
        print(f"⚠️ 목표 분량({TARGET_MINUTES}분)에 미치지 못합니다.")
    
    # 저장
    output_path, json_path = save_expanded_script(script_file, expanded_text, segments, metadata)
    
    if output_path:
        print(f"\n✅ 대본 확장 완료!")
        print(f"   저장 위치: {output_path}")
        return 0
    else:
        print("\n❌ 저장 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
