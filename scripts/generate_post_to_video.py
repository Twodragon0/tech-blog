#!/usr/bin/env python3
"""
블로그 포스트를 오디오로 변환한 후 영상까지 자동 생성하는 통합 스크립트

사용법:
    python3 scripts/generate_post_to_video.py [포스트파일명]
    python3 scripts/generate_post_to_video.py  # 최신 포스트 사용

옵션:
    --method: 영상 생성 방법 (ffmpeg, remotion, gemini-veo, 기본값: ffmpeg)
    --skip-audio: 오디오 생성 건너뛰기 (이미 생성된 경우)
    --skip-video: 영상 생성 건너뛰기 (오디오만 생성)
    --skip-image: 이미지 생성 건너뛰기 (기존 썸네일 사용)
    --generate-image: 이미지 생성 활성화 (Gemini Nano Banana 사용)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
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


def generate_audio(post_file: Path) -> bool:
    """
    오디오를 생성합니다.

    Args:
        post_file: 포스트 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("=" * 60)
    log_message("1단계: 오디오 생성 시작")
    log_message("=" * 60)

    try:
        # generate_enhanced_audio.py 실행
        post_filename = post_file.name if post_file.parent == POSTS_DIR else post_file
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_enhanced_audio.py"),
            str(post_filename),
        ]

        log_message(f"📝 오디오 생성 스크립트 실행: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,  # 실시간 출력
            text=True,
        )

        if result.returncode == 0:
            log_message("✅ 오디오 생성 완료")
            return True
        else:
            log_message(
                f"❌ 오디오 생성 실패 (종료 코드: {result.returncode})", "ERROR"
            )
            return False

    except Exception as e:
        log_message(f"❌ 오디오 생성 중 오류: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def find_audio_file(post_stem: str) -> Path:
    """생성된 오디오 파일을 찾습니다."""
    audio_filename = f"{post_stem}_audio.mp3"
    audio_path = OUTPUT_DIR / audio_filename

    if audio_path.exists():
        return audio_path

    # 파일명 패턴이 다른 경우 찾기
    audio_files = list(OUTPUT_DIR.glob(f"{post_stem}*audio*.mp3"))
    if audio_files:
        return audio_files[0]

    raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_filename}")


def generate_image_with_gemini_nano_banana(
    post_title: str, script: str, output_path: Path
) -> bool:
    """
    Gemini Nano Banana를 사용하여 강의용 썸네일 이미지를 생성합니다.

    Args:
        post_title: 포스트 제목
        script: 대본 텍스트 (이미지 생성 프롬프트에 활용)
        output_path: 출력 이미지 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    import os
    import requests

    # lgtm[py/clear-text-storage-sensitive-data] - Environment variable
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # nosec B105
    if not GEMINI_API_KEY:
        log_message("⚠️ Gemini API 키가 없어 이미지 생성을 건너뜁니다.", "WARNING")
        return False

    try:
        log_message("🎨 Gemini Nano Banana로 이미지 생성 중...")

        # 이미지 생성 프롬프트 (대본의 핵심 내용 기반)
        script_summary = script[:500] if len(script) > 500 else script
        prompt = f"""다음 기술 강의를 위한 전문적이고 현대적인 썸네일 이미지를 생성해주세요.

강의 제목: {post_title}
강의 요약: {script_summary}

요구사항:
- 기술 블로그 강의용 썸네일
- 전문적이고 깔끔한 디자인
- 기술적인 느낌을 주는 색상과 아이콘
- 1920x1080 해상도
- 한국어 텍스트 포함 가능
- 현대적이고 세련된 스타일"""

        # Gemini API 호출 (이미지 생성은 향후 지원 예정)
        # 현재는 기본 썸네일 사용
        log_message(
            "⚠️ Gemini Nano Banana 이미지 생성은 현재 제한적입니다. 기본 썸네일을 사용합니다.",
            "WARNING",
        )
        return False

    except Exception as e:
        log_message(f"⚠️ 이미지 생성 중 오류: {str(e)}", "WARNING")
        return False


def find_thumbnail_image(
    post_metadata: dict,
    post_title: str = "",
    script: str = "",
    generate_if_missing: bool = False,
) -> Path:
    """
    썸네일 이미지를 찾거나 생성합니다.

    Args:
        post_metadata: 포스트 메타데이터
        post_title: 포스트 제목 (이미지 생성 시 사용)
        script: 대본 텍스트 (이미지 생성 시 사용)
        generate_if_missing: 이미지가 없을 때 생성 시도 여부

    Returns:
        썸네일 이미지 경로
    """
    import frontmatter

    # Front matter의 image 필드 확인
    image_path = post_metadata.get("image", "")

    if image_path:
        # /assets/images/... 형식인 경우
        if image_path.startswith("/assets/images/"):
            image_file = PROJECT_ROOT / "assets" / "images" / Path(image_path).name
            if image_file.exists():
                return image_file

    # 기본 썸네일 찾기
    assets_images = PROJECT_ROOT / "assets" / "images"
    if assets_images.exists():
        default_images = list(assets_images.glob("*.png"))
        default_images.extend(list(assets_images.glob("*.jpg")))

        if default_images:
            return default_images[0]

    # 이미지 생성 시도 (generate_if_missing이 True인 경우)
    if generate_if_missing and post_title and script:
        generated_image = (
            OUTPUT_DIR
            / f"{Path(post_metadata.get('title', 'default')).stem}_thumbnail.png"
        )
        if generate_image_with_gemini_nano_banana(post_title, script, generated_image):
            if generated_image.exists():
                return generated_image

    # 썸네일이 없으면 에러
    raise FileNotFoundError(
        "썸네일 이미지를 찾을 수 없습니다. assets/images 디렉토리에 이미지를 추가하거나 --generate-image 옵션을 사용하세요."
    )


def generate_video_with_ffmpeg(
    audio_path: Path, thumbnail_path: Path, output_path: Path
) -> bool:
    """
    FFmpeg를 사용하여 영상을 생성합니다.

    Args:
        audio_path: 오디오 파일 경로
        thumbnail_path: 썸네일 이미지 경로
        output_path: 출력 영상 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("=" * 60)
    log_message("2단계: FFmpeg로 영상 생성 시작")
    log_message("=" * 60)

    # FFmpeg 설치 확인
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            log_message("❌ FFmpeg가 설치되어 있지 않습니다.", "ERROR")
            log_message(
                "   설치 방법: brew install ffmpeg (macOS) 또는 apt-get install ffmpeg (Linux)",
                "ERROR",
            )
            return False
    except FileNotFoundError:
        log_message("❌ FFmpeg가 설치되어 있지 않습니다.", "ERROR")
        log_message(
            "   설치 방법: brew install ffmpeg (macOS) 또는 apt-get install ffmpeg (Linux)",
            "ERROR",
        )
        return False

    log_message(f"📹 영상 생성 중...")
    log_message(f"   오디오: {audio_path.name}")
    log_message(f"   썸네일: {thumbnail_path.name}")
    log_message(f"   출력: {output_path.name}")

    try:
        # FFmpeg로 영상 생성
        # -loop 1: 이미지를 반복하여 오디오 길이에 맞춤
        # -tune stillimage: 정적 이미지 최적화
        # -shortest: 오디오 길이에 맞춤
        cmd = [
            "ffmpeg",
            "-loop",
            "1",
            "-i",
            str(thumbnail_path),
            "-i",
            str(audio_path),
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            "-y",
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
        )

        if result.returncode == 0 and output_path.exists():
            file_size = output_path.stat().st_size
            log_message(f"✅ 영상 생성 완료: {output_path} ({file_size:,} bytes)")
            return True
        else:
            log_message(f"❌ FFmpeg 영상 생성 실패", "ERROR")
            if result.stderr:
                log_message(f"   오류: {result.stderr[:500]}", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log_message("❌ FFmpeg 영상 생성 타임아웃 (5분 초과)", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ FFmpeg 영상 생성 중 오류: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def generate_video_with_gemini_veo(
    audio_path: Path, thumbnail_path: Path, script: str, output_path: Path
) -> bool:
    """
    Gemini Veo를 사용하여 영상을 생성합니다.

    Args:
        audio_path: 오디오 파일 경로
        thumbnail_path: 썸네일 이미지 경로
        script: 대본 텍스트 (영상 생성 프롬프트에 활용)
        output_path: 출력 영상 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    import os
    import requests

    # lgtm[py/clear-text-storage-sensitive-data] - Environment variable
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # nosec B105
    if not GEMINI_API_KEY:
        log_message(
            "⚠️ Gemini API 키가 없어 Gemini Veo 영상 생성을 건너뜁니다.", "WARNING"
        )
        return False

    log_message("=" * 60)
    log_message("2단계: Gemini Veo로 영상 생성 시작")
    log_message("=" * 60)

    try:
        log_message("📹 Gemini Veo로 영상 생성 중...")
        log_message(f"   오디오: {audio_path.name}")
        log_message(f"   썸네일: {thumbnail_path.name}")

        # Gemini Veo는 현재 제한적이므로, 향후 정식 출시 시 구현
        # 현재는 FFmpeg나 Remotion으로 폴백
        log_message("⚠️ Gemini Veo는 현재 제한적입니다. FFmpeg로 폴백합니다.", "WARNING")
        return generate_video_with_ffmpeg(audio_path, thumbnail_path, output_path)

    except Exception as e:
        log_message(f"❌ Gemini Veo 영상 생성 중 오류: {str(e)}", "ERROR")
        return False


def generate_video_with_remotion(post_file: Path, audio_path: Path) -> bool:
    """
    Remotion을 사용하여 영상을 생성합니다.

    Args:
        post_file: 포스트 파일 경로
        audio_path: 오디오 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("=" * 60)
    log_message("2단계: Remotion으로 영상 생성 시작")
    log_message("=" * 60)

    try:
        # generate_video_with_remotion.py 실행
        post_filename = post_file.name if post_file.parent == POSTS_DIR else post_file
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_video_with_remotion.py"),
            str(post_filename),
        ]

        log_message(f"📝 Remotion 영상 생성 스크립트 실행: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,  # 실시간 출력
            text=True,
        )

        if result.returncode == 0:
            log_message("✅ Remotion 영상 생성 완료")
            return True
        else:
            log_message(
                f"❌ Remotion 영상 생성 실패 (종료 코드: {result.returncode})", "ERROR"
            )
            return False

    except Exception as e:
        log_message(f"❌ Remotion 영상 생성 중 오류: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def process_post(
    post_file: Path,
    method: str = "ffmpeg",
    skip_audio: bool = False,
    skip_video: bool = False,
    skip_image: bool = True,
    generate_image: bool = False,
) -> bool:
    """
    포스트를 처리하여 오디오와 영상을 생성합니다.

    Args:
        post_file: 포스트 파일 경로
        method: 영상 생성 방법 (ffmpeg 또는 remotion)
        skip_audio: 오디오 생성 건너뛰기
        skip_video: 영상 생성 건너뛰기

    Returns:
        성공 시 True, 실패 시 False
    """
    if not post_file.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {post_file}", "ERROR")
        return False

    try:
        import frontmatter

        log_message("=" * 60)
        log_message("블로그 포스트 → 오디오 → 영상 변환 시작")
        log_message("=" * 60)
        log_message(f"📄 포스트: {post_file.name}")
        log_message(f"🎬 영상 생성 방법: {method}")
        log_message("")

        # Front matter 읽기
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", "")
        post_stem = post_file.stem

        # 0단계: 대본 파일 읽기 (이미지/영상 생성 시 사용)
        script = ""
        script_file = OUTPUT_DIR / f"{post_stem}_script.txt"
        if script_file.exists():
            try:
                with open(script_file, "r", encoding="utf-8") as f:
                    script_content = f.read()
                    # 대본 본문만 추출 (헤더 제외)
                    if "강의용 대본" in script_content:
                        script = script_content.split("강의용 대본")[-1].strip()
                    else:
                        script = script_content
                log_message(f"✅ 대본 파일 로드: {len(script)}자")
            except Exception as e:
                log_message(f"⚠️ 대본 파일 읽기 실패: {str(e)}", "WARNING")

        # 1단계: 오디오 생성
        audio_path = None
        if not skip_audio:
            if not generate_audio(post_file):
                log_message("❌ 오디오 생성 실패. 영상 생성을 건너뜁니다.", "ERROR")
                return False

            # 생성된 오디오 파일 찾기
            try:
                audio_path = find_audio_file(post_stem)
                log_message(f"✅ 오디오 파일 확인: {audio_path.name}")
            except FileNotFoundError as e:
                log_message(f"❌ {str(e)}", "ERROR")
                return False

            # 대본 파일 다시 읽기 (오디오 생성 후 업데이트되었을 수 있음)
            if script_file.exists() and not script:
                try:
                    with open(script_file, "r", encoding="utf-8") as f:
                        script_content = f.read()
                        if "강의용 대본" in script_content:
                            script = script_content.split("강의용 대본")[-1].strip()
                        else:
                            script = script_content
                except Exception as e:
                    log_message(f"⚠️ 대본 파일 읽기 실패: {str(e)}", "WARNING")
        else:
            log_message("⏭️ 오디오 생성 건너뜀 (--skip-audio 옵션)")
            try:
                audio_path = find_audio_file(post_stem)
                log_message(f"✅ 기존 오디오 파일 사용: {audio_path.name}")
            except FileNotFoundError as e:
                log_message(f"❌ {str(e)}", "ERROR")
                return False

        # 1.5단계: 이미지 생성 (옵션)
        thumbnail_path = None
        if not skip_image and generate_image:
            if script:
                generated_image = OUTPUT_DIR / f"{post_stem}_thumbnail.png"
                if generate_image_with_gemini_nano_banana(
                    title, script, generated_image
                ):
                    if generated_image.exists():
                        thumbnail_path = generated_image
                        log_message(f"✅ 생성된 썸네일 이미지: {thumbnail_path.name}")
            else:
                log_message("⚠️ 대본이 없어 이미지 생성을 건너뜁니다.", "WARNING")

        # 2단계: 영상 생성
        if not skip_video:
            # 썸네일 이미지 찾기 또는 생성
            if not thumbnail_path:
                try:
                    thumbnail_path = find_thumbnail_image(
                        post.metadata, title, script, generate_image
                    )
                    log_message(f"✅ 썸네일 이미지 확인: {thumbnail_path.name}")
                except FileNotFoundError as e:
                    log_message(f"❌ {str(e)}", "ERROR")
                    return False

            # 영상 파일 경로
            video_filename = f"{post_stem}_video.mp4"
            video_path = OUTPUT_DIR / video_filename

            if method == "ffmpeg":
                if not generate_video_with_ffmpeg(
                    audio_path, thumbnail_path, video_path
                ):
                    return False
            elif method == "remotion":
                if not generate_video_with_remotion(post_file, audio_path):
                    return False
            elif method == "gemini-veo":
                if not script:
                    log_message(
                        "⚠️ Gemini Veo는 대본이 필요합니다. 대본 파일을 확인하세요.",
                        "WARNING",
                    )
                if not generate_video_with_gemini_veo(
                    audio_path, thumbnail_path, script, video_path
                ):
                    return False
            else:
                log_message(f"❌ 알 수 없는 영상 생성 방법: {method}", "ERROR")
                log_message("   지원하는 방법: ffmpeg, remotion, gemini-veo", "ERROR")
                return False
        else:
            log_message("⏭️ 영상 생성 건너뜀 (--skip-video 옵션)")

        # 결과 요약
        log_message("=" * 60)
        log_message("✅ 처리 완료!")
        log_message("=" * 60)

        # 생성된 파일 목록
        script_files = list(OUTPUT_DIR.glob(f"{post_stem}*script*.txt"))
        if script_files:
            log_message(f"📝 대본 파일: {script_files[0]}")

        if audio_path:
            log_message(f"🎤 오디오 파일: {audio_path}")

        if not skip_video:
            video_files = list(OUTPUT_DIR.glob(f"{post_stem}*video*.mp4"))
            if video_files:
                log_message(f"📹 영상 파일: {video_files[0]}")

        return True

    except Exception as e:
        log_message(f"❌ 포스트 처리 중 오류 발생: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="블로그 포스트를 오디오로 변환한 후 영상까지 자동 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 최신 포스트로 오디오 + 영상 생성 (FFmpeg)
  python3 scripts/generate_post_to_video.py
  
  # 특정 포스트로 오디오 + 영상 생성
  python3 scripts/generate_post_to_video.py _posts/2025-01-10-example.md
  
  # Remotion으로 영상 생성
  python3 scripts/generate_post_to_video.py --method remotion
  
  # Gemini Veo로 영상 생성
  python3 scripts/generate_post_to_video.py --method gemini-veo
  
  # 이미지 생성 활성화 (Gemini Nano Banana)
  python3 scripts/generate_post_to_video.py --generate-image
  
  # 오디오만 생성 (영상 생성 건너뛰기)
  python3 scripts/generate_post_to_video.py --skip-video
  
  # 영상만 생성 (오디오 생성 건너뛰기)
  python3 scripts/generate_post_to_video.py --skip-audio
        """,
    )

    parser.add_argument(
        "post_file", nargs="?", help="포스트 파일명 (선택사항, 없으면 최신 포스트 사용)"
    )
    parser.add_argument(
        "--method",
        choices=["ffmpeg", "remotion", "gemini-veo"],
        default="ffmpeg",
        help="영상 생성 방법 (기본값: ffmpeg)",
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="오디오 생성 건너뛰기 (이미 생성된 경우)",
    )
    parser.add_argument(
        "--skip-video", action="store_true", help="영상 생성 건너뛰기 (오디오만 생성)"
    )
    parser.add_argument(
        "--skip-image",
        action="store_true",
        default=True,
        help="이미지 생성 건너뛰기 (기존 썸네일 사용, 기본값: True)",
    )
    parser.add_argument(
        "--generate-image",
        action="store_true",
        help="이미지 생성 활성화 (Gemini Nano Banana 사용)",
    )

    args = parser.parse_args()

    # 포스트 파일 경로 결정
    if args.post_file:
        post_file = Path(args.post_file)
        if not post_file.is_absolute():
            post_file = POSTS_DIR / post_file
    else:
        # 최신 포스트 자동 선택
        log_message("📂 최신 포스트 검색 중...")
        post_files = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )

        if not post_files:
            log_message("❌ 포스트 파일을 찾을 수 없습니다.", "ERROR")
            sys.exit(1)

        post_file = post_files[0]
        log_message(f"📄 최신 포스트 선택: {post_file.name}")

    # 포스트 처리
    success = process_post(
        post_file,
        method=args.method,
        skip_audio=args.skip_audio,
        skip_video=args.skip_video,
        skip_image=args.skip_image and not args.generate_image,
        generate_image=args.generate_image,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
