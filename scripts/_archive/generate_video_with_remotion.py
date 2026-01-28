#!/usr/bin/env python3
"""
Remotion을 활용하여 블로그 포스팅을 영상으로 변환하는 스크립트

주요 기능:
- 포스팅 파일에서 메타데이터와 이미지 경로 추출
- 대본 파일을 파싱하여 시퀀스로 나누기
- 각 시퀀스에 맞는 이미지 매핑
- Remotion을 사용하여 영상 생성

보안 고려사항:
- 입력 검증 수행
- 파일 경로 검증
- 에러 핸들링 강화
"""

import os
import re
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import frontmatter
import mutagen
from mutagen.mp3 import MP3

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
VIDEO_GENERATOR_DIR = PROJECT_ROOT / "video-generator"
ASSETS_DIR = PROJECT_ROOT / "assets" / "images"
LOG_FILE = PROJECT_ROOT / "video_generation_log.txt"

# 출력 디렉토리 생성
OUTPUT_DIR.mkdir(exist_ok=True)
VIDEO_GENERATOR_DIR.mkdir(exist_ok=True)
(VIDEO_GENERATOR_DIR / "public").mkdir(exist_ok=True)


def log_message(message: str, level: str = "INFO") -> None:
    """로그 메시지를 파일과 stdout에 기록합니다."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(log_entry.strip())
    except Exception as e:
        print(f"⚠️ 로그 기록 실패: {str(e)}")


def parse_post_metadata(post_path: Path) -> Optional[Dict[str, Any]]:
    """
    포스팅 파일에서 메타데이터를 추출합니다.
    
    Args:
        post_path: 포스팅 파일 경로
        
    Returns:
        메타데이터 딕셔너리 또는 None
    """
    try:
        with open(post_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        
        metadata = {
            "title": post.metadata.get("title", ""),
            "date": post.metadata.get("date", ""),
            "image": post.metadata.get("image", ""),
            "image_alt": post.metadata.get("image_alt", ""),
            "categories": post.metadata.get("categories", []),
            "tags": post.metadata.get("tags", []),
        }
        
        # 이미지 경로 정규화
        if metadata["image"]:
            # /assets/images/... 형식을 assets/images/...로 변환
            if metadata["image"].startswith("/"):
                metadata["image"] = metadata["image"][1:]
        
        log_message(f"✅ 포스팅 메타데이터 추출 완료: {metadata['title']}")
        return metadata
    
    except Exception as e:
        log_message(f"❌ 포스팅 메타데이터 추출 실패: {str(e)}", "ERROR")
        return None


def parse_script_file(script_path: Path) -> Optional[Dict[str, Any]]:
    """
    대본 파일을 파싱합니다.
    
    Args:
        script_path: 대본 파일 경로
        
    Returns:
        대본 정보 딕셔너리 또는 None
    """
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 대본 섹션 추출
        script_section_match = re.search(
            r'={10,}\s*강의용 대본\s*={10,}\s*\n(.*?)(?=\n={10,}|\Z)',
            content,
            re.DOTALL
        )
        
        if not script_section_match:
            log_message("⚠️ 대본 섹션을 찾을 수 없습니다. 전체 내용을 사용합니다.", "WARNING")
            script_text = content
        else:
            script_text = script_section_match.group(1).strip()
        
        # 메타데이터 추출
        metadata = {}
        metadata_match = re.search(r'생성일:\s*(.+)', content)
        if metadata_match:
            metadata["created_at"] = metadata_match.group(1).strip()
        
        length_match = re.search(r'대본 길이:\s*(\d+)자', content)
        if length_match:
            metadata["length"] = int(length_match.group(1))
        
        log_message(f"✅ 대본 파일 파싱 완료: {len(script_text)}자")
        
        return {
            "script": script_text,
            "metadata": metadata,
        }
    
    except Exception as e:
        log_message(f"❌ 대본 파일 파싱 실패: {str(e)}", "ERROR")
        return None


def split_script_into_segments(
    script_text: str,
    audio_duration: float,
    min_segment_duration: float = 3.0,
    max_segment_duration: float = 10.0,
) -> List[Dict[str, Any]]:
    """
    대본을 시퀀스로 나눕니다.
    
    Args:
        script_text: 대본 텍스트
        audio_duration: 오디오 길이 (초)
        min_segment_duration: 최소 시퀀스 길이 (초)
        max_segment_duration: 최대 시퀀스 길이 (초)
        
    Returns:
        시퀀스 리스트
    """
    # 문장 단위로 분리 (마침표, 느낌표, 물음표 기준)
    sentences = re.split(r'([.!?]\s+)', script_text)
    
    # 문장 재조합
    segments = []
    current_segment = ""
    current_start_time = 0.0
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
        sentence = sentence.strip()
        
        if not sentence:
            continue
        
        # 예상 길이 계산 (한글 기준 약 3자/초, 1.5배속 재생 시 약 4.5자/초)
        estimated_duration = len(sentence) / 4.5
        
        # 최소 길이 보장
        if estimated_duration < 1.0:
            estimated_duration = 1.0
        
        # 현재 시퀀스에 추가할지 결정
        if current_segment and (len(current_segment) + len(sentence)) / 4.5 <= max_segment_duration:
            current_segment += " " + sentence
        else:
            # 이전 시퀀스 저장
            if current_segment:
                segment_duration = len(current_segment) / 4.5
                if segment_duration < min_segment_duration:
                    segment_duration = min_segment_duration
                
                segments.append({
                    "text": current_segment,
                    "startTime": current_start_time,
                    "duration": segment_duration,
                })
                
                current_start_time += segment_duration
            
            # 새 시퀀스 시작
            current_segment = sentence
    
    # 마지막 시퀀스 추가
    if current_segment:
        segment_duration = len(current_segment) / 4.5
        if segment_duration < min_segment_duration:
            segment_duration = min_segment_duration
        
        # 오디오 길이를 초과하지 않도록 조정
        if current_start_time + segment_duration > audio_duration:
            segment_duration = audio_duration - current_start_time
        
        if segment_duration > 0:
            segments.append({
                "text": current_segment,
                "startTime": current_start_time,
                "duration": segment_duration,
            })
    
    log_message(f"✅ 대본을 {len(segments)}개의 시퀀스로 분할 완료")
    return segments


def get_audio_duration(audio_path: Path) -> float:
    """
    오디오 파일의 길이를 가져옵니다.
    
    Args:
        audio_path: 오디오 파일 경로
        
    Returns:
        오디오 길이 (초)
    """
    try:
        audio = MP3(str(audio_path))
        duration = audio.info.length
        log_message(f"✅ 오디오 길이: {duration:.2f}초")
        return duration
    except Exception as e:
        log_message(f"⚠️ 오디오 길이 추출 실패: {str(e)}. 기본값 60초 사용", "WARNING")
        return 60.0


def extract_keywords_from_text(text: str) -> List[str]:
    """
    텍스트에서 주요 키워드를 추출합니다.
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        키워드 리스트
    """
    # 주요 기술 키워드 정의
    keywords = [
        "AWS WAF", "WAF", "웹 ACL", "SQL Injection", "XSS", "크로스 사이트",
        "Cloudflare", "DDoS", "CDN", "SSL/TLS", "TLS", "Bot Management",
        "GitHub", "Dependabot", "Code Scanning", "CodeQL", "Secret Scanning",
        "DVWA", "OWASP", "보안", "DevSecOps", "CI/CD", "CloudFront",
        "S3", "CORS", "DNS", "DNSSEC", "Rate Limiting", "Geo-blocking"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def find_image_by_keywords(
    keywords: List[str],
    assets_dir: Path,
    base_image_name: str,
) -> str:
    """
    키워드를 기반으로 관련 이미지를 찾습니다.
    
    Args:
        keywords: 키워드 리스트
        assets_dir: assets 디렉토리 경로
        base_image_name: 기본 이미지 파일명
        
    Returns:
        이미지 파일명
    """
    if not keywords:
        return base_image_name
    
    # 키워드별 이미지 매핑 (키워드가 파일명에 포함된 이미지 찾기)
    keyword_priority = {
        "cloudflare": ["cloudflare", "Cloudflare"],
        "github": ["github", "GitHub"],
        "aws": ["aws", "AWS", "WAF", "waf"],
        "waf": ["waf", "WAF", "aws"],
        "ddos": ["ddos", "DDoS", "cloudflare"],
        "ssl": ["ssl", "tls", "SSL", "TLS"],
        "cdn": ["cdn", "CDN", "cloudflare"],
        "dependabot": ["dependabot", "Dependabot", "github"],
        "codeql": ["codeql", "CodeQL", "code-scanning", "github"],
        "dvwa": ["dvwa", "DVWA", "waf", "security"],
        "security": ["security", "보안", "Security"],
        "devsecops": ["devsecops", "DevSecOps", "security"],
    }
    
    # 모든 이미지 파일 수집
    all_images = list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.svg"))
    
    # 키워드 우선순위에 따라 이미지 검색
    best_match = None
    best_score = 0
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        for priority_key, search_terms in keyword_priority.items():
            if priority_key in keyword_lower:
                # 관련 이미지 검색
                for image_file in all_images:
                    image_name_lower = image_file.name.lower()
                    score = 0
                    
                    # 정확한 키워드 매칭
                    for term in search_terms:
                        if term.lower() in image_name_lower:
                            score += 10
                        if term.lower() == image_name_lower:
                            score += 20
                    
                    # 부분 매칭
                    if keyword_lower in image_name_lower:
                        score += 5
                    
                    if score > best_score:
                        best_score = score
                        best_match = image_file.name
    
    if best_match and best_score > 0:
        log_message(f"✅ 키워드 {keywords[:3]}에 매칭된 이미지: {best_match} (점수: {best_score})")
        return best_match
    
    # 매칭되는 이미지가 없으면 기본 이미지 사용
    return base_image_name


def find_images_for_segments(
    segments: List[Dict[str, Any]],
    base_image_path: str,
    assets_dir: Path,
) -> List[Dict[str, Any]]:
    """
    각 시퀀스에 맞는 이미지를 찾습니다.
    
    Args:
        segments: 시퀀스 리스트
        base_image_path: 기본 이미지 경로
        assets_dir: assets 디렉토리 경로
        
    Returns:
        이미지가 매핑된 시퀀스 리스트
    """
    # 기본 이미지 경로 정규화
    normalized_path = base_image_path
    if normalized_path.startswith("/"):
        normalized_path = normalized_path[1:]
    if normalized_path.startswith("assets/"):
        normalized_path = normalized_path.replace("assets/", "")
    
    # 기본 이미지 경로 확인
    base_image_full_path = assets_dir / normalized_path
    
    if not base_image_full_path.exists():
        log_message(f"⚠️ 기본 이미지를 찾을 수 없습니다: {base_image_full_path}", "WARNING")
        # 기본 이미지가 없으면 assets 디렉토리에서 첫 번째 이미지 사용
        fallback_images = list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.svg"))
        if fallback_images:
            base_image_name = fallback_images[0].name
            log_message(f"💡 대체 이미지 사용: {base_image_name}")
        else:
            log_message("❌ 사용 가능한 이미지가 없습니다.", "ERROR")
            base_image_name = None
    else:
        # 파일명만 사용 (public 디렉토리에 복사되므로)
        base_image_name = Path(normalized_path).name
    
    if not base_image_name:
        log_message("❌ 기본 이미지를 설정할 수 없습니다.", "ERROR")
        return segments
    
    # 각 시퀀스에 키워드 기반 이미지 매핑
    for i, segment in enumerate(segments):
        if not segment.get("image"):
            # 세그먼트 텍스트에서 키워드 추출
            text = segment.get("text", "")
            keywords = extract_keywords_from_text(text)
            
            # 키워드 기반 이미지 찾기
            matched_image = find_image_by_keywords(keywords, assets_dir, base_image_name)
            segment["image"] = matched_image
            
            if keywords:
                log_message(f"세그먼트 {i+1}: 키워드 {keywords} → 이미지 {matched_image}")
    
    log_message(f"✅ {len(segments)}개 시퀀스에 이미지 매핑 완료")
    return segments


def create_remotion_config(
    title: str,
    thumbnail: str,
    audio_path: str,
    segments: List[Dict[str, Any]],
    duration_in_frames: int,
    output_path: Path,
) -> None:
    """
    Remotion 설정 파일을 생성합니다.
    
    Args:
        title: 영상 제목
        thumbnail: 썸네일 경로
        audio_path: 오디오 파일 경로
        segments: 시퀀스 리스트
        duration_in_frames: 총 프레임 수
        output_path: 출력 파일 경로
    """
    config = {
        "title": title,
        "thumbnail": thumbnail,
        "audioPath": audio_path,
        "segments": segments,
        "durationInFrames": duration_in_frames,
    }
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        log_message(f"✅ Remotion 설정 파일 생성 완료: {output_path}")
    except Exception as e:
        log_message(f"❌ Remotion 설정 파일 생성 실패: {str(e)}", "ERROR")
        raise


def copy_assets_to_remotion(
    segments: List[Dict[str, Any]],
    base_image_path: str,
    audio_path: Path,
    video_generator_dir: Path,
    assets_dir: Path,
) -> Tuple[str, str]:
    """
    에셋을 Remotion public 디렉토리로 복사합니다.
    
    Args:
        segments: 시퀀스 리스트 (이미지 정보 포함)
        base_image_path: 기본 이미지 경로 (상대 경로)
        audio_path: 오디오 파일 경로
        video_generator_dir: video-generator 디렉토리
        assets_dir: assets 디렉토리
        
    Returns:
        (복사된 기본 이미지 경로, 복사된 오디오 경로)
    """
    public_dir = video_generator_dir / "public"
    copied_images = set()
    
    # 기본 이미지 복사
    if base_image_path.startswith("/"):
        base_image_path = base_image_path[1:]
    
    normalized_base = base_image_path.replace("assets/images/", "")
    source_base_image = assets_dir / normalized_base
    if source_base_image.exists():
        base_image_filename = source_base_image.name
        dest_base_image = public_dir / base_image_filename
        try:
            shutil.copy2(source_base_image, dest_base_image)
            copied_images.add(base_image_filename)
            log_message(f"✅ 기본 이미지 복사 완료: {base_image_filename}")
        except Exception as e:
            log_message(f"⚠️ 기본 이미지 복사 실패: {str(e)}", "WARNING")
    
    # 세그먼트별 이미지 복사
    for i, segment in enumerate(segments):
        segment_image = segment.get("image", "")
        if not segment_image:
            continue
        
        # 이미 복사한 이미지는 스킵
        if segment_image in copied_images:
            continue
        
        # 이미지 파일 찾기
        source_image = None
        
        # 정확한 파일명으로 먼저 검색
        potential_path = assets_dir / segment_image
        if potential_path.exists():
            source_image = potential_path
        else:
            # assets 디렉토리에서 직접 검색 (대소문자 무시)
            segment_image_lower = segment_image.lower()
            for ext in ["*.png", "*.svg", "*.jpg", "*.jpeg", "*.webp"]:
                for img_file in assets_dir.glob(ext):
                    if img_file.name.lower() == segment_image_lower:
                        source_image = img_file
                        break
                if source_image:
                    break
        
        if source_image and source_image.exists():
            dest_image = public_dir / source_image.name
            try:
                shutil.copy2(source_image, dest_image)
                copied_images.add(segment_image)
                log_message(f"✅ 세그먼트 {i+1} 이미지 복사 완료: {source_image.name}")
            except Exception as e:
                log_message(f"⚠️ 세그먼트 {i+1} 이미지 복사 실패: {str(e)}", "WARNING")
        else:
            log_message(f"⚠️ 세그먼트 {i+1} 이미지를 찾을 수 없습니다: {segment_image}", "WARNING")
    
    # 오디오 복사
    audio_filename = audio_path.name
    dest_audio = public_dir / audio_filename
    try:
        shutil.copy2(audio_path, dest_audio)
        log_message(f"✅ 오디오 복사 완료: {audio_filename}")
        copied_audio_path = audio_filename
    except Exception as e:
        log_message(f"❌ 오디오 복사 실패: {str(e)}", "ERROR")
        raise
    
    # 기본 이미지 파일명 반환
    base_image_filename = Path(normalized_base).name if source_base_image.exists() else "default-thumbnail.png"
    
    return base_image_filename, copied_audio_path


def update_remotion_root(config_path: Path, video_generator_dir: Path) -> None:
    """
    Remotion Root.tsx 파일은 이미 설정 파일을 읽도록 구성되어 있으므로
    별도 업데이트가 필요 없습니다.
    
    Args:
        config_path: 설정 파일 경로 (참고용)
        video_generator_dir: video-generator 디렉토리 (참고용)
    """
    # Root.tsx는 이미 video-config.json을 읽도록 구성되어 있음
    log_message("✅ Remotion Root.tsx는 이미 설정 파일을 읽도록 구성되어 있습니다")


def render_video_with_remotion(
    video_generator_dir: Path,
    output_video_path: Path,
    composition_id: str = "BlogVideo",
) -> bool:
    """
    Remotion을 사용하여 영상을 렌더링합니다.
    
    Args:
        video_generator_dir: video-generator 디렉토리
        output_video_path: 출력 영상 파일 경로
        composition_id: Composition ID
        
    Returns:
        성공 여부
    """
    try:
        # Remotion 렌더링 명령 실행
        cmd = [
            "npm",
            "run",
            "render",
            "--",
            "--id",
            composition_id,
            "--output",
            str(output_video_path),
        ]
        
        log_message(f"🎬 Remotion 렌더링 시작: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=video_generator_dir,
            capture_output=True,
            text=True,
            timeout=3600,  # 1시간 타임아웃
        )
        
        if result.returncode == 0:
            log_message(f"✅ 영상 렌더링 완료: {output_video_path}")
            return True
        else:
            log_message(f"❌ 영상 렌더링 실패: {result.stderr}", "ERROR")
            return False
    
    except subprocess.TimeoutExpired:
        log_message("❌ 영상 렌더링 타임아웃", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ 영상 렌더링 중 오류: {str(e)}", "ERROR")
        return False


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        log_message("사용법: python generate_video_with_remotion.py <post_filename>", "ERROR")
        log_message("예시: python generate_video_with_remotion.py 2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.md", "ERROR")
        sys.exit(1)
    
    post_filename = sys.argv[1]
    post_path = POSTS_DIR / post_filename
    
    if not post_path.exists():
        log_message(f"❌ 포스팅 파일을 찾을 수 없습니다: {post_path}", "ERROR")
        sys.exit(1)
    
    log_message(f"📝 포스팅 파일 처리 시작: {post_filename}")
    
    # 1. 포스팅 메타데이터 추출
    metadata = parse_post_metadata(post_path)
    if not metadata:
        log_message("❌ 포스팅 메타데이터 추출 실패", "ERROR")
        sys.exit(1)
    
    # 2. 대본 파일 찾기 (improved 버전 우선)
    post_basename = post_path.stem
    script_path = OUTPUT_DIR / f"{post_basename}_script_improved.txt"
    if not script_path.exists():
        script_path = OUTPUT_DIR / f"{post_basename}_script.txt"
    
    if not script_path.exists():
        log_message(f"❌ 대본 파일을 찾을 수 없습니다: {script_path}", "ERROR")
        log_message("먼저 generate_enhanced_audio.py를 실행하여 대본을 생성하세요.", "ERROR")
        sys.exit(1)
    
    # 3. 세그먼트 JSON 파일 확인 (있으면 우선 사용)
    segments_json_path = OUTPUT_DIR / f"{post_basename}_script_segments.json"
    segments = None
    
    if segments_json_path.exists():
        try:
            with open(segments_json_path, "r", encoding="utf-8") as f:
                segments_data = json.load(f)
                if "segments" in segments_data:
                    # JSON 세그먼트를 Remotion 형식으로 변환
                    raw_segments = segments_data["segments"]
                    segments = []
                    for seg in raw_segments:
                        segments.append({
                            "text": seg.get("text", ""),
                            "startTime": seg.get("startTime", 0),
                            "duration": seg.get("duration", 3.0),
                            "image": seg.get("image", ""),  # 이미지가 있으면 사용
                        })
                    log_message(f"✅ 세그먼트 JSON 파일에서 {len(segments)}개 시퀀스 로드 완료")
        except Exception as e:
            log_message(f"⚠️ 세그먼트 JSON 파일 로드 실패: {str(e)}. 대본에서 생성합니다.", "WARNING")
    
    # 4. 오디오 파일 찾기 (improved 버전 우선)
    audio_path = OUTPUT_DIR / f"{post_basename}_audio_improved.mp3"
    if not audio_path.exists():
        audio_path = OUTPUT_DIR / f"{post_basename}_audio.mp3"
    
    if not audio_path.exists():
        log_message(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_path}", "ERROR")
        log_message("먼저 generate_enhanced_audio.py를 실행하여 오디오를 생성하세요.", "ERROR")
        sys.exit(1)
    
    audio_duration = get_audio_duration(audio_path)
    
    # 5. 세그먼트가 없으면 대본에서 생성
    if not segments:
        script_data = parse_script_file(script_path)
        if not script_data:
            log_message("❌ 대본 파싱 실패", "ERROR")
            sys.exit(1)
        
        segments = split_script_into_segments(script_data["script"], audio_duration)
    
    # 6. 이미지 매핑
    image_path = metadata.get("image", "")
    if not image_path:
        log_message("⚠️ 포스팅에 이미지가 없습니다. 기본 이미지를 사용합니다.", "WARNING")
        image_path = "assets/images/default-thumbnail.png"
    
    segments = find_images_for_segments(segments, image_path, ASSETS_DIR)
    
    # 7. 에셋 복사 (세그먼트별 이미지 포함)
    copied_image_path, copied_audio_path = copy_assets_to_remotion(
        segments,
        image_path,
        audio_path,
        VIDEO_GENERATOR_DIR,
        ASSETS_DIR,
    )
    
    # 8. Remotion 설정 파일 생성
    fps = 30
    # 오디오 길이를 기준으로 duration 계산 (세그먼트가 짧아도 오디오 전체 길이 사용)
    duration_in_frames = int(audio_duration * fps)
    
    # 세그먼트가 오디오 길이를 초과하지 않도록 조정
    if segments:
        last_segment_end = segments[-1]["startTime"] + segments[-1]["duration"]
        if last_segment_end < audio_duration:
            # 마지막 세그먼트를 오디오 끝까지 연장
            segments[-1]["duration"] = audio_duration - segments[-1]["startTime"]
            log_message(f"✅ 마지막 세그먼트를 오디오 길이({audio_duration:.2f}초)에 맞춰 조정")
    
    config_path = VIDEO_GENERATOR_DIR / "public" / "video-config.json"
    create_remotion_config(
        metadata["title"],
        copied_image_path,
        copied_audio_path,
        segments,
        duration_in_frames,
        config_path,
    )
    
    # 9. Remotion Root.tsx 업데이트
    update_remotion_root(config_path, VIDEO_GENERATOR_DIR)
    
    # 10. 영상 렌더링
    output_video_path = OUTPUT_DIR / f"{post_basename}_video.mp4"
    
    success = render_video_with_remotion(
        VIDEO_GENERATOR_DIR,
        output_video_path,
    )
    
    if success:
        log_message(f"🎉 영상 생성 완료: {output_video_path}")
        print(f"\n✅ 영상이 생성되었습니다: {output_video_path}")
    else:
        log_message("❌ 영상 생성 실패", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
