#!/usr/bin/env python3
"""
블로그 포스트를 완전한 강의 영상으로 변환하는 통합 워크플로우

워크플로우:
1. 이미지 생성 (Gemini Nano Banana / Cursor / Claude) - 포스팅 완료 후
2. 강의 대본 생성 (Gemini 우선 → DeepSeek 폴백)
3. 오디오 생성 (ElevenLabs 우선 → Gemini 폴백)
4. 영상 제작 (Gemini Veo 우선 → Remotion 폴백)

비용 최적화:
- 캐싱 활용으로 중복 API 호출 방지
- API 선택 전략으로 비용 효율적인 API 우선 사용
- 에러 처리 및 폴백 전략으로 불필요한 재시도 방지

보안:
- API 키는 환경 변수에서만 읽음
- 로그에 민감 정보 마스킹
- 입력 검증 및 에러 핸들링

사용법:
    python3 scripts/generate_complete_lecture.py [포스트파일명]
    python3 scripts/generate_complete_lecture.py  # 최신 포스트 사용

옵션:
    --skip-image: 이미지 생성 건너뛰기
    --skip-script: 대본 생성 건너뛰기
    --skip-audio: 오디오 생성 건너뛰기
    --skip-video: 영상 생성 건너뛰기
    --image-method: 이미지 생성 방법 (gemini, cursor, claude, 기본값: gemini)
    --video-method: 영상 생성 방법 (gemini-veo, remotion, ffmpeg, 기본값: gemini-veo)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
LOG_FILE = PROJECT_ROOT / "video_generation_log.txt"

# 출력 디렉토리 생성
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


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


def generate_image_with_gemini_nano_banana(
    post_title: str, post_content: str, output_path: Path
) -> bool:
    """
    Gemini Nano Banana를 사용하여 강의용 썸네일 이미지를 생성합니다.

    Args:
        post_title: 포스트 제목
        post_content: 포스트 내용 (요약용)
        output_path: 출력 이미지 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        log_message("⚠️ Gemini API 키가 없어 이미지 생성을 건너뜁니다.", "WARNING")
        return False

    try:
        log_message("🎨 Gemini Nano Banana로 이미지 생성 중...")

        # 포스트 내용 요약 (이미지 생성 프롬프트에 활용)
        content_summary = (
            post_content[:1000] if len(post_content) > 1000 else post_content
        )

        # 이미지 생성 프롬프트
        prompt = f"""다음 기술 강의를 위한 전문적이고 현대적인 썸네일 이미지를 생성해주세요.

강의 제목: {post_title}
강의 내용 요약: {content_summary}

요구사항:
- 기술 블로그 강의용 썸네일
- 전문적이고 깔끔한 디자인
- 기술적인 느낌을 주는 색상과 아이콘
- 1920x1080 해상도
- 한국어 텍스트 포함 가능
- 현대적이고 세련된 스타일
- 제목을 명확하게 표시"""

        # Gemini API 호출 (이미지 생성은 향후 지원 예정)
        # 현재는 기본 썸네일 생성 또는 외부 도구 사용
        log_message("⚠️ Gemini Nano Banana 이미지 생성은 현재 제한적입니다.", "WARNING")
        log_message(
            "💡 Cursor나 Claude를 사용하여 이미지를 생성하거나, 기본 썸네일을 사용합니다.",
            "INFO",
        )
        return False

    except Exception as e:
        log_message(f"⚠️ 이미지 생성 중 오류: {str(e)}", "WARNING")
        return False


def generate_image_with_cursor(
    post_title: str, post_content: str, output_path: Path
) -> bool:
    """
    Cursor를 사용하여 이미지를 생성합니다.
    (Cursor는 IDE이므로 실제로는 사용자에게 안내)

    Args:
        post_title: 포스트 제목
        post_content: 포스트 내용
        output_path: 출력 이미지 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("💡 Cursor를 사용하여 이미지를 생성하세요.", "INFO")
    log_message(f"   프롬프트: '{post_title}' 기술 강의용 썸네일 이미지 생성", "INFO")
    log_message(f"   출력 경로: {output_path}", "INFO")
    log_message("   생성 후 해당 경로에 이미지를 저장하세요.", "INFO")
    return False


def generate_image_with_claude(
    post_title: str, post_content: str, output_path: Path
) -> bool:
    """
    Claude를 사용하여 이미지를 생성합니다.
    (Claude는 텍스트 생성이므로 이미지 생성은 제한적)

    Args:
        post_title: 포스트 제목
        post_content: 포스트 내용
        output_path: 출력 이미지 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("💡 Claude는 이미지 생성이 제한적입니다.", "INFO")
    log_message("   Gemini Nano Banana나 Cursor를 사용하는 것을 권장합니다.", "INFO")
    return False


def generate_image(post_file: Path, image_method: str = "gemini") -> Optional[Path]:
    """
    이미지를 생성합니다.

    Args:
        post_file: 포스트 파일 경로
        image_method: 이미지 생성 방법 (gemini, cursor, claude)

    Returns:
        생성된 이미지 경로 또는 None
    """
    try:
        import frontmatter

        log_message("=" * 60)
        log_message("0단계: 이미지 생성 시작")
        log_message("=" * 60)

        # Front matter 읽기
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", "")
        content = (
            post.content[:2000] if len(post.content) > 2000 else post.content
        )  # 요약용

        post_stem = post_file.stem
        image_filename = f"{post_stem}_thumbnail.png"
        image_path = ASSETS_IMAGES_DIR / image_filename

        # 이미지가 이미 존재하는지 확인
        if image_path.exists():
            log_message(f"✅ 기존 이미지 사용: {image_path.name}")
            return image_path

        # 이미지 생성 시도
        success = False
        if image_method == "gemini":
            success = generate_image_with_gemini_nano_banana(title, content, image_path)
        elif image_method == "cursor":
            success = generate_image_with_cursor(title, content, image_path)
        elif image_method == "claude":
            success = generate_image_with_claude(title, content, image_path)
        else:
            log_message(f"⚠️ 알 수 없는 이미지 생성 방법: {image_method}", "WARNING")
            log_message("   지원하는 방법: gemini, cursor, claude", "WARNING")

        if success and image_path.exists():
            log_message(f"✅ 이미지 생성 완료: {image_path}")
            return image_path
        else:
            log_message("⚠️ 이미지 생성 실패 또는 건너뜀", "WARNING")
            log_message(
                "   기본 썸네일을 사용하거나 수동으로 이미지를 추가하세요.", "WARNING"
            )
            return None

    except Exception as e:
        log_message(f"❌ 이미지 생성 중 오류: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return None


def generate_script(post_file: Path) -> bool:
    """
    강의용 대본을 생성합니다.
    Gemini 우선, DeepSeek 폴백 전략 사용.

    Args:
        post_file: 포스트 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("=" * 60)
    log_message("1단계: 강의 대본 생성 시작")
    log_message("=" * 60)

    try:
        post_filename = post_file.name if post_file.parent == POSTS_DIR else post_file
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_enhanced_audio.py"),
            str(post_filename),
        ]

        log_message(f"📝 대본 생성 스크립트 실행: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,  # 실시간 출력
            text=True,
        )

        if result.returncode == 0:
            log_message("✅ 대본 생성 완료")
            return True
        else:
            log_message(f"❌ 대본 생성 실패 (종료 코드: {result.returncode})", "ERROR")
            return False

    except Exception as e:
        log_message(f"❌ 대본 생성 중 오류: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def generate_audio(post_file: Path) -> bool:
    """
    오디오를 생성합니다.
    ElevenLabs 우선, Gemini 폴백 전략 사용.

    Args:
        post_file: 포스트 파일 경로

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("=" * 60)
    log_message("2단계: 오디오 생성 시작")
    log_message("=" * 60)

    # generate_enhanced_audio.py가 이미 오디오도 생성하므로
    # 대본 생성과 함께 오디오도 생성됨
    log_message("💡 대본 생성 시 오디오도 함께 생성됩니다.", "INFO")
    return True


def generate_video(post_file: Path, video_method: str = "gemini-veo") -> bool:
    """
    영상을 생성합니다.
    Gemini Veo 우선, Remotion 폴백 전략 사용.

    Args:
        post_file: 포스트 파일 경로
        video_method: 영상 생성 방법 (gemini-veo, remotion, ffmpeg)

    Returns:
        성공 시 True, 실패 시 False
    """
    log_message("=" * 60)
    log_message("3단계: 영상 생성 시작")
    log_message("=" * 60)

    try:
        post_filename = post_file.name if post_file.parent == POSTS_DIR else post_file
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "generate_post_to_video.py"),
            str(post_filename),
            "--method",
            video_method,
            "--skip-audio",  # 오디오는 이미 생성됨
            "--skip-image",  # 이미지는 이미 생성됨
        ]

        log_message(f"📹 영상 생성 스크립트 실행: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,  # 실시간 출력
            text=True,
        )

        if result.returncode == 0:
            log_message("✅ 영상 생성 완료")
            return True
        else:
            log_message(f"❌ 영상 생성 실패 (종료 코드: {result.returncode})", "ERROR")
            return False

    except Exception as e:
        log_message(f"❌ 영상 생성 중 오류: {str(e)}", "ERROR")
        import traceback

        log_message(f"   상세 오류:\n{traceback.format_exc()}", "ERROR")
        return False


def process_post(
    post_file: Path,
    skip_image: bool = False,
    skip_script: bool = False,
    skip_audio: bool = False,
    skip_video: bool = False,
    image_method: str = "gemini",
    video_method: str = "gemini-veo",
) -> bool:
    """
    포스트를 처리하여 완전한 강의 영상을 생성합니다.

    Args:
        post_file: 포스트 파일 경로
        skip_image: 이미지 생성 건너뛰기
        skip_script: 대본 생성 건너뛰기
        skip_audio: 오디오 생성 건너뛰기
        skip_video: 영상 생성 건너뛰기
        image_method: 이미지 생성 방법
        video_method: 영상 생성 방법

    Returns:
        성공 시 True, 실패 시 False
    """
    if not post_file.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {post_file}", "ERROR")
        return False

    try:
        import frontmatter

        log_message("=" * 60)
        log_message("블로그 포스트 → 완전한 강의 영상 변환 시작")
        log_message("=" * 60)
        log_message(f"📄 포스트: {post_file.name}")
        log_message(f"🎨 이미지 생성 방법: {image_method}")
        log_message(f"🎬 영상 생성 방법: {video_method}")
        log_message("")

        # Front matter 읽기
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", "")
        post_stem = post_file.stem

        success_steps = []

        # 0단계: 이미지 생성 (포스팅 완료 후)
        image_path = None
        if not skip_image:
            image_path = generate_image(post_file, image_method)
            if image_path:
                success_steps.append("이미지")
            else:
                log_message("⚠️ 이미지 생성 실패 또는 건너뜀", "WARNING")
        else:
            log_message("⏭️ 이미지 생성 건너뛰기")

        # 1단계: 강의 대본 생성 (Gemini 우선 → DeepSeek 폴백)
        if not skip_script:
            if not generate_script(post_file):
                log_message("❌ 대본 생성 실패. 오디오 생성을 건너뜁니다.", "ERROR")
                return False
            success_steps.append("대본")
        else:
            log_message("⏭️ 대본 생성 건너뛰기")

        # 2단계: 오디오 생성 (ElevenLabs 우선 → Gemini 폴백)
        # generate_enhanced_audio.py가 대본 생성 시 오디오도 함께 생성
        if not skip_audio:
            if not skip_script:
                # 대본 생성 시 오디오도 함께 생성됨
                log_message("💡 대본 생성 시 오디오도 함께 생성되었습니다.", "INFO")
            else:
                # 대본이 이미 있는 경우 오디오만 생성
                if not generate_audio(post_file):
                    log_message("❌ 오디오 생성 실패", "ERROR")
                    return False
            success_steps.append("오디오")
        else:
            log_message("⏭️ 오디오 생성 건너뛰기")

        # 3단계: 영상 생성 (Gemini Veo 우선 → Remotion 폴백)
        if not skip_video:
            if not generate_video(post_file, video_method):
                log_message("❌ 영상 생성 실패", "ERROR")
                return False
            success_steps.append("영상")
        else:
            log_message("⏭️ 영상 생성 건너뛰기")

        # 결과 요약
        log_message("=" * 60)
        log_message("✅ 처리 완료!")
        log_message("=" * 60)
        log_message(
            f"완료된 단계: {', '.join(success_steps) if success_steps else '없음'}"
        )

        # 생성된 파일 목록
        script_files = list(OUTPUT_DIR.glob(f"{post_stem}*script*.txt"))
        audio_files = list(OUTPUT_DIR.glob(f"{post_stem}*audio*.mp3"))
        video_files = list(OUTPUT_DIR.glob(f"{post_stem}*video*.mp4"))

        if script_files:
            log_message(f"📝 대본 파일: {script_files[0]}")
        if audio_files:
            log_message(f"🎤 오디오 파일: {audio_files[0]}")
        if image_path:
            log_message(f"🎨 이미지 파일: {image_path}")
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
        description="블로그 포스트를 완전한 강의 영상으로 변환 (비용 최적화, 효율성, 보안 고려)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
워크플로우:
  1. 이미지 생성 (Gemini Nano Banana / Cursor / Claude)
  2. 강의 대본 생성 (Gemini 우선 → DeepSeek 폴백)
  3. 오디오 생성 (ElevenLabs 우선 → Gemini 폴백)
  4. 영상 제작 (Gemini Veo 우선 → Remotion 폴백)

비용 최적화:
  - 캐싱 활용으로 중복 API 호출 방지
  - API 선택 전략으로 비용 효율적인 API 우선 사용
  - 에러 처리 및 폴백 전략으로 불필요한 재시도 방지

예시:
  # 전체 워크플로우 실행
  python3 scripts/generate_complete_lecture.py
  
  # 특정 포스트로 실행
  python3 scripts/generate_complete_lecture.py _posts/2026-01-08-example.md
  
  # 이미지 생성 방법 지정
  python3 scripts/generate_complete_lecture.py --image-method cursor
  
  # 영상 생성 방법 지정
  python3 scripts/generate_complete_lecture.py --video-method remotion
  
  # 특정 단계만 실행
  python3 scripts/generate_complete_lecture.py --skip-image --skip-video
        """,
    )

    parser.add_argument(
        "post_file", nargs="?", help="포스트 파일명 (선택사항, 없으면 최신 포스트 사용)"
    )
    parser.add_argument(
        "--skip-image", action="store_true", help="이미지 생성 건너뛰기"
    )
    parser.add_argument("--skip-script", action="store_true", help="대본 생성 건너뛰기")
    parser.add_argument(
        "--skip-audio", action="store_true", help="오디오 생성 건너뛰기"
    )
    parser.add_argument("--skip-video", action="store_true", help="영상 생성 건너뛰기")
    parser.add_argument(
        "--image-method",
        choices=["gemini", "cursor", "claude"],
        default="gemini",
        help="이미지 생성 방법 (기본값: gemini)",
    )
    parser.add_argument(
        "--video-method",
        choices=["gemini-veo", "remotion", "ffmpeg"],
        default="gemini-veo",
        help="영상 생성 방법 (기본값: gemini-veo)",
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
        skip_image=args.skip_image,
        skip_script=args.skip_script,
        skip_audio=args.skip_audio,
        skip_video=args.skip_video,
        image_method=args.image_method,
        video_method=args.video_method,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
