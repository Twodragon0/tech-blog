#!/usr/bin/env python3
"""
모든 블로그 포스트에 대해 비디오 강의용 대본을 생성하는 스크립트

Gemini API를 활용하여 모든 포스트의 대본을 자동으로 생성합니다.
이미 대본이 있는 포스트는 건너뛰고, 없는 포스트만 처리합니다.

보안 고려사항:
- API 키는 환경 변수에서만 읽음
- 로그에 민감 정보 마스킹
- Rate Limit 관리
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import frontmatter

# 프로젝트 루트 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
OUTPUT_DIR = PROJECT_ROOT / "output"

# generate_enhanced_audio.py의 함수들을 import
sys.path.insert(0, str(SCRIPT_DIR))


# .env 파일 로드
def load_env_file(env_path: Path) -> None:
    """간단한 .env 파일 파서"""
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


def mask_sensitive_info(text: str) -> str:
    """Mask sensitive data (API keys, tokens) in text before writing to files."""
    if not text:
        return text
    import re
    masked = re.sub(r"sk-[a-zA-Z0-9_-]{20,}", "sk-***MASKED***", text)
    masked = re.sub(r"AIza[0-9A-Za-z_-]{35}", "AIza***MASKED***", masked)
    for env_var in ["GEMINI_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"]:
        val = os.getenv(env_var, "")
        if val and len(val) > 10:
            masked = masked.replace(val, f"***{env_var}_MASKED***")
    return masked
env_path = PROJECT_ROOT / ".env"
load_env_file(env_path)

try:
    from dotenv import load_dotenv

    if env_path.exists():
        load_dotenv(env_path, override=False)
except ImportError:
    pass

# generate_enhanced_audio.py에서 필요한 함수들 import
try:
    from generate_enhanced_audio import (
        DEEPSEEK_API_KEY,
        GEMINI_API_KEY,
        PREFER_GEMINI,
        USE_DEEPSEEK_FOR_SCRIPT,
        USE_GEMINI_FOR_SCRIPT,
        clean_markdown,
        generate_script,
        log_message,
    )
except ImportError as e:
    print(f"❌ generate_enhanced_audio.py를 import할 수 없습니다: {e}")
    sys.exit(1)


def get_existing_scripts() -> Dict[str, Path]:
    """
    이미 생성된 대본 파일 목록을 반환합니다.

    Returns:
        {post_stem: script_path} 딕셔너리
    """
    existing = {}
    if not OUTPUT_DIR.exists():
        return existing

    for script_file in OUTPUT_DIR.glob("*_script.txt"):
        # 파일명에서 포스트 stem 추출
        # 예: "2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective_script.txt"
        # -> "2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective"
        stem = script_file.stem.replace("_script", "")
        existing[stem] = script_file

    return existing


def get_all_posts() -> List[Path]:
    """
    모든 포스트 파일 목록을 반환합니다.

    Returns:
        포스트 파일 경로 리스트
    """
    if not POSTS_DIR.exists():
        log_message(f"❌ 포스트 디렉토리를 찾을 수 없습니다: {POSTS_DIR}", "ERROR")
        return []

    posts = sorted(POSTS_DIR.glob("*.md"))
    return posts


def process_post_for_script(post_path: Path, existing_scripts: Dict[str, Path]) -> bool:
    """
    단일 포스트에 대해 대본을 생성합니다.

    Args:
        post_path: 포스트 파일 경로
        existing_scripts: 이미 생성된 대본 딕셔너리

    Returns:
        성공 시 True, 실패 시 False
    """
    post_stem = post_path.stem

    # 이미 대본이 있는지 확인
    if post_stem in existing_scripts:
        log_message(f"⏭️  대본이 이미 존재합니다: {post_path.name} (건너뜀)")
        return True

    try:
        log_message(f"📄 포스트 처리 시작: {post_path.name}")

        # Front matter와 콘텐츠 읽기
        with open(post_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", "")
        content = post.content

        if not content:
            log_message(f"❌ 포스트 콘텐츠가 비어있습니다: {post_path.name}", "ERROR")
            return False

        # 마크다운 정제
        cleaned_text = clean_markdown(content)

        if not cleaned_text:
            log_message(f"❌ 정제된 텍스트가 비어있습니다: {post_path.name}", "ERROR")
            return False

        log_message(f"📝 정제된 텍스트 길이: {len(cleaned_text)}자")

        # 대본 생성
        log_message("🤖 Gemini API로 대본 생성 중...")
        script = generate_script(cleaned_text, title)

        if not script:
            log_message(f"❌ 대본 생성 실패: {post_path.name}", "ERROR")
            return False

        # 출력 파일 경로 생성
        script_filename = f"{post_stem}_script.txt"
        script_path = OUTPUT_DIR / script_filename

        # 대본 파일 저장
        try:
            # 사용된 API 정보 추적
            api_info = []
            if GEMINI_API_KEY:
                api_info.append("Gemini API Key")
            if DEEPSEEK_API_KEY:
                api_info.append("DeepSeek API")

            used_api = " → ".join(api_info) if api_info else "알 수 없음"

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"대본 길이: {len(script)}자\n")
                f.write(f"원본 포스트: {post_path.name}\n")
                f.write(f"사용된 API: {used_api}\n")
                f.write("API 전략: ")
                if PREFER_GEMINI:
                    f.write("Gemini 우선")
                else:
                    f.write("DeepSeek 우선")
                f.write("\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("강의용 대본\n")
                f.write("=" * 60 + "\n\n")
                f.write(mask_sensitive_info(script))
                f.write("\n")

            log_message(f"✅ 대본 생성 완료: {script_path.name} ({len(script)}자)")
            return True

        except Exception as e:
            log_message(f"❌ 대본 파일 저장 실패: {str(e)}", "ERROR")
            return False

    except Exception as e:
        log_message(f"❌ 포스트 처리 중 오류: {str(e)}", "ERROR")
        return False


def main():
    """메인 함수"""
    print("=" * 60)
    print("📝 모든 포스트 대본 생성 스크립트")
    print("=" * 60)
    print()

    # API 키 확인
    if not GEMINI_API_KEY and not DEEPSEEK_API_KEY:
        print("❌ GEMINI_API_KEY 또는 DEEPSEEK_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 API 키를 설정해주세요.")
        return 1

    if GEMINI_API_KEY:
        print("✅ Gemini API 키 확인됨")
    if DEEPSEEK_API_KEY:
        print("✅ DeepSeek API 키 확인됨")
    print()

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 모든 포스트 가져오기
    all_posts = get_all_posts()
    if not all_posts:
        log_message("❌ 포스트를 찾을 수 없습니다.", "ERROR")
        return 1

    log_message(f"📚 총 {len(all_posts)}개의 포스트를 찾았습니다.")

    # 이미 생성된 대본 확인
    existing_scripts = get_existing_scripts()
    log_message(f"📋 이미 생성된 대본: {len(existing_scripts)}개")

    # 처리할 포스트 필터링
    posts_to_process = [p for p in all_posts if p.stem not in existing_scripts]

    if not posts_to_process:
        log_message("✅ 모든 포스트의 대본이 이미 생성되어 있습니다!")
        return 0

    log_message(f"🔄 처리할 포스트: {len(posts_to_process)}개")
    print()

    # 각 포스트 처리
    success_count = 0
    fail_count = 0

    for i, post_path in enumerate(posts_to_process, 1):
        log_message(f"\n[{i}/{len(posts_to_process)}] {post_path.name}")
        log_message("-" * 60)

        success = process_post_for_script(post_path, existing_scripts)

        if success:
            success_count += 1
        else:
            fail_count += 1

        # Rate Limit을 고려한 대기 시간
        if i < len(posts_to_process):
            wait_time = 3  # Gemini API Rate Limit을 고려한 3초 대기
            log_message(f"⏳ 다음 요청까지 {wait_time}초 대기 중...")
            time.sleep(wait_time)

        print()

    # 결과 요약
    print("=" * 60)
    print("📊 처리 결과 요약")
    print("=" * 60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"⏭️  건너뜀: {len(existing_scripts)}개")
    print(f"📚 전체: {len(all_posts)}개")
    print()

    if fail_count > 0:
        log_message(
            f"⚠️ {fail_count}개의 포스트 처리에 실패했습니다. 로그를 확인해주세요.",
            "WARNING",
        )
        return 1

    log_message("🎉 모든 포스트의 대본 생성이 완료되었습니다!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
