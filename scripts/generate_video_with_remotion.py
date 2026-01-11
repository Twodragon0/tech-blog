#!/usr/bin/env python3
"""
Remotion을 사용하여 블로그 포스팅 영상을 생성하는 스크립트

사전 요구사항:
1. generate_audio.py로 오디오 생성 완료
2. Node.js 및 npm 설치
3. video-generator 디렉토리에 npm install 완료
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
VIDEO_GENERATOR_DIR = PROJECT_ROOT / "video-generator"
LOG_FILE = PROJECT_ROOT / "video_generation_log.txt"


def log_message(message: str, level: str = "INFO") -> None:
    """로그 메시지를 파일과 stdout에 기록합니다."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ 로그 파일 기록 실패: {e}", file=sys.stderr)
    
    print(log_entry.strip())


def check_dependencies() -> bool:
    """필수 의존성이 설치되어 있는지 확인합니다."""
    # Node.js 확인
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            log_message("❌ Node.js가 설치되어 있지 않습니다.", "ERROR")
            return False
        log_message(f"✅ Node.js 버전: {result.stdout.strip()}")
    except FileNotFoundError:
        log_message("❌ Node.js가 설치되어 있지 않습니다.", "ERROR")
        log_message("   설치 방법: https://nodejs.org/", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ Node.js 확인 중 오류: {str(e)}", "ERROR")
        return False
    
    # npm 확인
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            log_message("❌ npm이 설치되어 있지 않습니다.", "ERROR")
            return False
        log_message(f"✅ npm 버전: {result.stdout.strip()}")
    except FileNotFoundError:
        log_message("❌ npm이 설치되어 있지 않습니다.", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ npm 확인 중 오류: {str(e)}", "ERROR")
        return False
    
    # video-generator 디렉토리 확인
    if not VIDEO_GENERATOR_DIR.exists():
        log_message("❌ video-generator 디렉토리가 없습니다.", "ERROR")
        log_message("   video-generator 디렉토리를 생성하고 npm install을 실행하세요.", "ERROR")
        return False
    
    # node_modules 확인
    node_modules = VIDEO_GENERATOR_DIR / "node_modules"
    if not node_modules.exists():
        log_message("⚠️ node_modules가 없습니다. npm install을 실행합니다...", "WARNING")
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=VIDEO_GENERATOR_DIR,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                log_message(f"❌ npm install 실패: {result.stderr}", "ERROR")
                return False
            log_message("✅ npm install 완료")
        except Exception as e:
            log_message(f"❌ npm install 중 오류: {str(e)}", "ERROR")
            return False
    
    return True


def get_audio_duration(audio_path: Path) -> Optional[float]:
    """FFprobe를 사용하여 오디오 길이를 초 단위로 반환합니다."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            return duration
        else:
            log_message(f"⚠️ 오디오 길이 확인 실패: {result.stderr}", "WARNING")
            return None
    except FileNotFoundError:
        log_message("⚠️ ffprobe가 설치되어 있지 않습니다. 기본 길이를 사용합니다.", "WARNING")
        return None
    except Exception as e:
        log_message(f"⚠️ 오디오 길이 확인 중 오류: {str(e)}", "WARNING")
        return None


def find_thumbnail(post_metadata: Dict[str, Any]) -> Path:
    """포스트의 썸네일 이미지를 찾습니다."""
    # Front matter의 image 필드 확인
    image_path = post_metadata.get("image", "")
    
    if image_path:
        # /assets/images/... 형식인 경우
        if image_path.startswith("/assets/images/"):
            image_file = PROJECT_ROOT / "assets" / "images" / Path(image_path).name
            if image_file.exists():
                return image_file
    
    # 기본 썸네일 찾기
    default_images = list((PROJECT_ROOT / "assets" / "images").glob("*.png"))
    default_images.extend(list((PROJECT_ROOT / "assets" / "images").glob("*.jpg")))
    
    if default_images:
        return default_images[0]
    
    # 썸네일이 없으면 에러
    raise FileNotFoundError("썸네일 이미지를 찾을 수 없습니다.")


def generate_video_with_remotion(
    post_title: str,
    audio_path: Path,
    thumbnail_path: Path,
    output_path: Path
) -> bool:
    """
    Remotion을 사용하여 영상을 생성합니다.
    
    Args:
        post_title: 포스트 제목
        audio_path: 오디오 파일 경로
        thumbnail_path: 썸네일 이미지 경로
        output_path: 출력 영상 파일 경로
        
    Returns:
        성공 시 True, 실패 시 False
    """
    if not audio_path.exists():
        log_message(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_path}", "ERROR")
        return False
    
    if not thumbnail_path.exists():
        log_message(f"❌ 썸네일 이미지를 찾을 수 없습니다: {thumbnail_path}", "ERROR")
        return False
    
    # 오디오 길이 확인
    audio_duration = get_audio_duration(audio_path)
    if audio_duration is None:
        audio_duration = 10.0  # 기본값: 10초
        log_message("⚠️ 오디오 길이를 확인할 수 없어 기본값(10초)을 사용합니다.", "WARNING")
    
    # 프레임 수 계산 (30fps 기준)
    duration_in_frames = int(audio_duration * 30)
    
    log_message(f"📹 Remotion으로 영상 생성 중...")
    log_message(f"   제목: {post_title}")
    log_message(f"   오디오 길이: {audio_duration:.2f}초 ({duration_in_frames} 프레임)")
    log_message(f"   썸네일: {thumbnail_path.name}")
    
    # 오디오 파일을 video-generator/public으로 복사
    public_dir = VIDEO_GENERATOR_DIR / "public"
    public_dir.mkdir(exist_ok=True)
    
    audio_filename = audio_path.name
    public_audio_path = public_dir / audio_filename
    
    try:
        import shutil
        shutil.copy2(audio_path, public_audio_path)
        log_message(f"✅ 오디오 파일 복사 완료: {public_audio_path}")
    except Exception as e:
        log_message(f"❌ 오디오 파일 복사 실패: {str(e)}", "ERROR")
        return False
    
    # 썸네일 이미지를 video-generator/public으로 복사
    thumbnail_filename = thumbnail_path.name
    public_thumbnail_path = public_dir / thumbnail_filename
    
    try:
        import shutil
        shutil.copy2(thumbnail_path, public_thumbnail_path)
        log_message(f"✅ 썸네일 이미지 복사 완료: {public_thumbnail_path}")
    except Exception as e:
        log_message(f"❌ 썸네일 이미지 복사 실패: {str(e)}", "ERROR")
        return False
    
    # Remotion render 실행
    try:
        log_message("📝 Remotion 렌더링 시작...")
        
        # Remotion render 명령 실행
        # props는 JSON 문자열로 전달
        props_json = json.dumps({
            "title": post_title,
            "thumbnail": thumbnail_filename,
            "audioPath": audio_filename,
        }, ensure_ascii=False)
        
        cmd = [
            "npx", "remotion", "render",
            "BlogVideo",
            str(output_path),
            "--props", props_json,
            "--frames", "0", str(duration_in_frames - 1),
        ]
        
        result = subprocess.run(
            cmd,
            cwd=VIDEO_GENERATOR_DIR,
            capture_output=True,
            text=True,
            timeout=600  # 10분 타임아웃
        )
        
        if result.returncode != 0:
            log_message(f"❌ Remotion 렌더링 실패: {result.stderr}", "ERROR")
            if result.stdout:
                log_message(f"   stdout: {result.stdout[:500]}", "ERROR")
            return False
        
        if output_path.exists():
            file_size = output_path.stat().st_size
            log_message(f"✅ 영상 생성 완료: {output_path} ({file_size:,} bytes)")
            return True
        else:
            log_message("❌ 영상 파일이 생성되지 않았습니다.", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("❌ Remotion 렌더링 타임아웃 (10분 초과)", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ Remotion 렌더링 중 오류: {str(e)}", "ERROR")
        import traceback
        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def process_post_with_remotion(post_path: Path) -> bool:
    """포스트를 처리하여 Remotion으로 영상을 생성합니다."""
    if not post_path.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
        return False
    
    try:
        import frontmatter
        
        log_message(f"📄 포스트 처리 시작: {post_path.name}")
        
        # Front matter와 콘텐츠 읽기
        with open(post_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        
        title = post.metadata.get("title", "")
        if not title:
            log_message(f"❌ 포스트 제목이 없습니다: {post_path.name}", "ERROR")
            return False
        
        # 오디오 파일 찾기
        post_stem = post_path.stem
        audio_filename = f"{post_stem}_audio.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        
        if not audio_path.exists():
            log_message(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_path}", "ERROR")
            log_message("   먼저 generate_audio.py를 실행하여 오디오를 생성하세요.", "ERROR")
            return False
        
        # 썸네일 이미지 찾기
        try:
            thumbnail_path = find_thumbnail(post.metadata)
        except FileNotFoundError as e:
            log_message(f"❌ {str(e)}", "ERROR")
            return False
        
        # 출력 영상 파일 경로
        video_filename = f"{post_stem}_video.mp4"
        video_path = OUTPUT_DIR / video_filename
        
        # Remotion으로 영상 생성
        success = generate_video_with_remotion(
            title,
            audio_path,
            thumbnail_path,
            video_path
        )
        
        if success:
            log_message(f"✅ 포스트 처리 완료: {post_path.name}")
            log_message(f"   영상 파일: {video_path}")
            return True
        else:
            log_message(f"❌ 영상 생성 실패: {post_path.name}", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"❌ 포스트 처리 중 오류 발생: {str(e)}", "ERROR")
        import traceback
        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def main():
    """메인 실행 함수"""
    log_message("=" * 60)
    log_message("Remotion 영상 생성 시작")
    log_message("=" * 60)
    
    # 의존성 확인
    if not check_dependencies():
        log_message("❌ 의존성 확인 실패. 스크립트를 종료합니다.", "ERROR")
        sys.exit(1)
    
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        # 특정 포스트 파일 지정
        post_file = Path(sys.argv[1])
        if not post_file.is_absolute():
            post_file = POSTS_DIR / post_file
        
        if not post_file.exists():
            log_message(f"❌ 파일을 찾을 수 없습니다: {post_file}", "ERROR")
            sys.exit(1)
        
        post_paths = [post_file]
    else:
        # 최신 포스트 자동 선택
        log_message("📂 최신 포스트 검색 중...")
        post_files = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not post_files:
            log_message("❌ 포스트 파일을 찾을 수 없습니다.", "ERROR")
            sys.exit(1)
        
        latest_post = post_files[0]
        log_message(f"📄 최신 포스트 선택: {latest_post.name}")
        post_paths = [latest_post]
    
    # 포스트 처리
    success_count = 0
    for post_path in post_paths:
        if process_post_with_remotion(post_path):
            success_count += 1
    
    # 결과 요약
    log_message("=" * 60)
    log_message(f"처리 완료: {success_count}/{len(post_paths)} 성공")
    log_message("=" * 60)
    
    if success_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
