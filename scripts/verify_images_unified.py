#!/usr/bin/env python3
"""
통합 이미지 검증 스크립트
- 이미지 파일 존재 여부 확인
- 이미지 파일명이 영어로 되어 있는지 확인
- 포스팅 파일의 이미지 경로와 실제 파일 매칭
- 관련 없는 이미지 확인
- Gemini CLI 명령어 생성 (선택사항)
- SVG XML 유효성 검사 및 자동 수정 (--svg-validate / --svg-fix)
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib import image_utils as _image_utils  # noqa: E402
from scripts.lib.image_utils import (  # noqa: E402
    extract_image_paths,
    has_korean,
)

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
GEMINI_GUIDE = PROJECT_ROOT / "GEMINI_IMAGE_GUIDE.md"


def check_image_exists(image_path: str) -> Tuple[bool, Optional[Path]]:
    """이미지 파일 존재 여부 확인 (모듈 전역 PROJECT_ROOT/IMAGES_DIR 사용)."""
    return _image_utils.check_image_exists(
        image_path,
        project_root=PROJECT_ROOT,
        images_dir=IMAGES_DIR,
    )


def check_image_file(filename: str) -> Dict:
    """이미지 파일 검증"""
    result = {
        "filename": filename,
        "exists": False,
        "has_korean": False,
        "file_path": None,
    }

    image_file = IMAGES_DIR / filename
    result["file_path"] = image_file
    result["exists"] = image_file.exists()
    result["has_korean"] = has_korean(filename)

    return result


def extract_post_info(post_file: Path) -> Dict:
    """포스팅 파일에서 정보 추출"""
    content = post_file.read_text(encoding="utf-8")

    # Front matter 추출
    front_matter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    front_matter = {}
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        for line in front_matter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                front_matter[key.strip()] = value.strip().strip('"')

    return {
        "title": front_matter.get("title", ""),
        "category": front_matter.get("categories", front_matter.get("category", "")),
        "tags": front_matter.get("tags", "[]"),
        "image": front_matter.get("image", ""),
        "filename": post_file.name,
        "date": front_matter.get("date", ""),
    }


def generate_gemini_command(post_info: Dict, image_type: str = "architecture") -> str:
    """Gemini CLI 명령어 생성"""
    title = post_info["title"]
    category = post_info["category"]

    # 카테고리에 따른 기본 명령어 템플릿
    templates = {
        "cloud": f"""Create a nano banana style AWS architecture diagram for: {title}
Style: minimalist, clean lines, professional tech illustration
Colors: AWS orange (#FF9900), Blue for networking, Green for security
Layout: horizontal, optimized for blog post
Include: Korean labels for key components""",
        "security": f"""Create a nano banana style security architecture diagram for: {title}
Style: minimalist security illustration
Colors: Red (#CC0000) for threats, Green (#00AA44) for security measures
Layout: horizontal flow showing security layers
Include: Korean labels (보안 레이어, 위협, 보호)""",
        "incident": f"""Create a nano banana style incident timeline for: {title}
Style: minimalist timeline illustration
Colors: Red for incident start, Orange for investigation, Yellow for response, Green for recovery
Layout: horizontal timeline
Include: Korean labels (인지, 조사, 대응, 복구)""",
        "devsecops": f"""Create a nano banana style DevSecOps pipeline diagram for: {title}
Style: minimalist CI/CD security illustration
Colors: Blue for CI/CD, Green for security, Orange for deployment
Layout: horizontal pipeline flow
Include: Korean labels (개발, 보안, 배포)""",
    }

    template = templates.get(category, templates["cloud"])

    return f"""gemini "{template}\""""


def process_post_file(file_path: Path, generate_commands: bool = False) -> Dict:
    """포스팅 파일 처리"""
    result = {
        "file": str(file_path),
        "images": [],
        "issues": [],
        "post_info": None,
    }

    try:
        content = file_path.read_text(encoding="utf-8")
        post_info = extract_post_info(file_path)
        result["post_info"] = post_info

        # 메인 이미지 확인 (frontmatter image: 필드를 권위 있는 소스로 사용)
        if post_info["image"]:
            has_image, image_path = check_image_exists(post_info["image"])
            if not has_image:
                result["issues"].append(
                    f"Front matter의 메인 이미지를 찾을 수 없습니다: {post_info['image']}"
                )
                if generate_commands:
                    result["gemini_command"] = generate_gemini_command(post_info)
            else:
                img_result = check_image_file(Path(post_info["image"]).name)
                result["images"].append(img_result)
                if img_result["has_korean"]:
                    result["issues"].append(
                        f"이미지 파일명에 한글이 포함되어 있습니다: {post_info['image']}"
                    )

        return result

    except Exception as e:
        result["issues"].append(f"처리 중 오류 발생: {str(e)}")
        return result


def collect_all_referenced_images() -> set:
    """전체 프로젝트에서 참조되는 이미지 경로 수집 (assets/images 기준 상대경로)."""
    refs = set()
    # _posts
    for f in (PROJECT_ROOT / "_posts").glob("*.md"):
        refs.update(extract_image_paths(f.read_text(encoding="utf-8")))
    # _includes, _layouts
    for d in ("_includes", "_layouts"):
        dir_path = PROJECT_ROOT / d
        if dir_path.exists():
            for f in dir_path.rglob("*.html"):
                refs.update(extract_image_paths(f.read_text(encoding="utf-8")))
    # README, _config
    for name in ("README.md", "_config.yml"):
        p = PROJECT_ROOT / name
        if p.exists():
            refs.update(extract_image_paths(p.read_text(encoding="utf-8")))
    # sw.js, JS, HTML에서 /assets/images/xxx 또는 assets/images/xxx 패턴
    extra_files = [
        PROJECT_ROOT / "sw.js",
        PROJECT_ROOT / "assets" / "js" / "main-post.js",
        PROJECT_ROOT / "_includes" / "head.html",
        PROJECT_ROOT / "_config.yml",
    ]
    for p in extra_files:
        if p.exists():
            content = p.read_text(encoding="utf-8")
            for m in re.findall(r"/assets/images/([^\"')\s}\|]+)", content):
                refs.add(m.strip("'\""))
            for m in re.findall(r"assets/images/([^\"')\s}\|]+)", content):
                refs.add(m.strip("'\""))
    normalized = set()
    for r in refs:
        r = r.strip().split("|")[0].strip("'\"")
        if not r or r.startswith("["):
            continue
        normalized.add(r)
        if "/" in r:
            normalized.add(Path(r).name)
    return normalized


def list_all_image_files() -> set:
    """assets/images 하위 모든 이미지 파일 (assets/images 기준 상대경로)."""
    exts = {".svg", ".png", ".webp", ".jpg", ".jpeg"}
    out = set()
    for f in IMAGES_DIR.rglob("*"):
        if f.is_file() and f.suffix.lower() in exts:
            out.add(str(f.relative_to(IMAGES_DIR)))
    return out


def run_unused_report() -> List[str]:
    """미사용 이미지 목록 반환."""
    refs = collect_all_referenced_images()
    all_files = list_all_image_files()
    unused = []
    for rel in sorted(all_files):
        name = Path(rel).name
        if rel in refs or name in refs:
            continue
        unused.append(rel)
    return unused


def _xmllint_check(path: Path) -> Optional[str]:
    """xmllint --noout 실행 후 stderr 반환 (유효하면 None)."""
    result = subprocess.run(
        ["xmllint", "--noout", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        return None
    return result.stderr.strip()


# Regex: & NOT already part of a valid XML/HTML entity reference
_BARE_AMP_RE = re.compile(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9A-Fa-f]+);)")

# Regex: text content between > and < where < is immediately followed by digit or space
# Capture group 1 = content before the stray <, group 2 = the char after <
_STRAY_LT_RE = re.compile(r">([^<]*)<([0-9 ])")


def _fix_svg_text(content: str) -> str:
    """Apply conservative auto-fixes to SVG text content.

    Pass 1: replace bare & with &amp;
    Pass 2: replace stray < (followed by digit or space) inside text nodes with &lt;
            Iterates until no more matches to handle adjacent occurrences.
    """
    # Pass 1: bare ampersands
    content = _BARE_AMP_RE.sub("&amp;", content)

    # Pass 2: stray < before digit/space inside text runs, iterate until stable
    while True:
        new_content = _STRAY_LT_RE.sub(lambda m: ">" + m.group(1) + "&lt;" + m.group(2), content)
        if new_content == content:
            break
        content = new_content

    return content


def run_svg_validate(fix: bool = False) -> Dict:
    """Validate all SVGs under assets/images/ with xmllint.

    Returns a dict with keys:
      scanned, invalid_before, fixed, still_broken, details
    where details is a list of dicts per invalid file.
    """
    svg_files = sorted(IMAGES_DIR.rglob("*.svg"))
    total = len(svg_files)
    invalid_before = []
    fixed = []
    still_broken = []

    for svg_path in svg_files:
        err = _xmllint_check(svg_path)
        if err is None:
            continue
        invalid_before.append(svg_path)

        if not fix:
            continue

        # Attempt auto-fix
        original = svg_path.read_text(encoding="utf-8")
        patched = _fix_svg_text(original)

        if patched == original:
            still_broken.append((svg_path, err))
            continue

        # Write patched content to a temp check
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".svg", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(patched)
            tmp_path = Path(tmp.name)

        recheck_err = _xmllint_check(tmp_path)
        tmp_path.unlink(missing_ok=True)

        if recheck_err is None:
            svg_path.write_text(patched, encoding="utf-8")
            fixed.append(svg_path)
        else:
            still_broken.append((svg_path, recheck_err))

    return {
        "scanned": total,
        "invalid_before": len(invalid_before),
        "fixed": fixed,
        "still_broken": still_broken,
    }


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="통합 이미지 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 모든 포스팅 확인
  python3 scripts/verify_images_unified.py --all

  # 이미지가 없는 포스팅만 표시
  python3 scripts/verify_images_unified.py --missing

  # 미사용 이미지 목록 (참조 없는 파일)
  python3 scripts/verify_images_unified.py --unused

  # Gemini CLI 명령어 생성
  python3 scripts/verify_images_unified.py --all --generate-commands
        """,
    )

    parser.add_argument("--all", action="store_true", help="모든 포스팅 확인")
    parser.add_argument(
        "--missing", action="store_true", help="이미지가 없는 포스팅만 표시"
    )
    parser.add_argument(
        "--unused", action="store_true", help="참조되지 않는 이미지 파일 목록"
    )
    parser.add_argument(
        "--svg-validate",
        action="store_true",
        help="assets/images/ 내 모든 SVG의 XML 유효성 검사 (xmllint 필요)",
    )
    parser.add_argument(
        "--svg-fix",
        action="store_true",
        help="--svg-validate와 함께 사용: 유효하지 않은 SVG를 자동 수정 시도 (& → &amp;, stray < → &lt;)",
    )
    parser.add_argument(
        "--move-unused-to-archive",
        action="store_true",
        help="미사용 이미지를 assets/images/_unused_archive/ 로 이동 (--unused와 함께 사용)",
    )
    parser.add_argument("--recent", type=int, default=10, help="최근 N개 포스팅만 확인")
    parser.add_argument(
        "--generate-commands", action="store_true", help="Gemini CLI 명령어 생성"
    )

    args = parser.parse_args()

    if not POSTS_DIR.exists():
        print(f"❌ 포스팅 디렉토리를 찾을 수 없습니다: {POSTS_DIR}")
        sys.exit(1)

    if not IMAGES_DIR.exists():
        print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {IMAGES_DIR}")
        sys.exit(1)

    if args.svg_validate:
        print("SVG XML 유효성 검사 중...\n")
        report = run_svg_validate(fix=args.svg_fix)
        print("=" * 80)
        print("SVG 유효성 검사 결과")
        print("=" * 80)
        print(f"스캔한 SVG 파일: {report['scanned']}")
        print(f"유효하지 않은 파일 (수정 전): {report['invalid_before']}")
        if args.svg_fix:
            print(f"자동 수정 완료: {len(report['fixed'])}")
            print(f"수동 수정 필요: {len(report['still_broken'])}")
        print()
        if report["fixed"]:
            print("자동 수정된 파일:")
            for p in report["fixed"]:
                print(f"  [fixed] {p.name}")
        if report["still_broken"]:
            print("수동 수정 필요한 파일:")
            for p, err in report["still_broken"]:
                first_line = err.splitlines()[0] if err else "unknown error"
                print(f"  [broken] {p.name}")
                print(f"           {first_line}")
        if not report["fixed"] and not report["still_broken"]:
            if report["invalid_before"] == 0:
                print("모든 SVG 파일이 유효합니다.")
            else:
                print("유효하지 않은 파일이 있습니다. --svg-fix 플래그로 자동 수정을 시도하세요.")
        print("=" * 80)
        sys.exit(0 if report["still_broken"] == [] else 1)

    if args.unused:
        unused = run_unused_report()
        print(f"📊 미사용 이미지 (참조 없음): {len(unused)}개\n")
        for u in unused:
            print(u)
        if args.move_unused_to_archive and unused:
            archive_dir = IMAGES_DIR / "_unused_archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = archive_dir / "manifest.txt"
            moved = []
            for rel in unused:
                src = IMAGES_DIR / rel
                if not src.exists():
                    continue
                dest = archive_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    import shutil

                    shutil.move(str(src), str(dest))
                    moved.append(rel)
                except OSError as e:
                    print(f"  ⚠️ 이동 실패: {rel} - {e}")
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(
                    "# Moved by verify_images_unified.py --unused --move-unused-to-archive\n"
                )
                for m in moved:
                    f.write(m + "\n")
            print("=" * 80)
            print(
                f"✅ {len(moved)}개 파일을 {archive_dir} 로 이동했습니다. 목록: {manifest_path}"
            )
        print("=" * 80)
        return

    # 포스팅 파일 목록 (AGENTS.md는 deepinit 가이드, 포스트 아님)
    if args.all:
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
    else:
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )[: args.recent]
    posts = [p for p in posts if p.name != "AGENTS.md"]

    print(f"📊 {len(posts)}개 포스팅 이미지 확인 중...\n")

    results = []
    total_issues = 0
    missing_images = []
    korean_filenames = []

    for post_file in posts:
        result = process_post_file(post_file, generate_commands=args.generate_commands)

        if args.missing and not result["issues"]:
            continue

        if result["issues"]:
            results.append(result)
            total_issues += len(result["issues"])

            # 결과 출력
            print(f"📄 {post_file.name}")
            print(
                f"   제목: {result['post_info']['title'][:60] if result['post_info'] else 'N/A'}..."
            )

            for issue in result["issues"]:
                print(f"  ⚠️  {issue}")

                if "찾을 수 없습니다" in issue:
                    missing_images.append(
                        {
                            "file": post_file.name,
                            "image": issue.split(": ")[-1] if ": " in issue else "",
                        }
                    )
                elif "한글이 포함" in issue:
                    korean_filenames.append(
                        {
                            "file": post_file.name,
                            "image": issue.split(": ")[-1] if ": " in issue else "",
                        }
                    )

            if args.generate_commands and "gemini_command" in result:
                print("   💡 생성 명령어:")
                print(f"   {result['gemini_command']}")

            print()

    # 요약 통계
    print("=" * 80)
    print("📊 이미지 파일 통계")
    print("=" * 80)
    print(f"전체 포스팅: {len(posts)}")
    print(f"문제 발견: {len(results)}")
    print(f"총 문제 수: {total_issues}")

    if missing_images:
        print(f"\n❌ 이미지 파일을 찾을 수 없는 포스팅 ({len(missing_images)}개):")
        for item in missing_images:
            print(f"  - {item['file']}: {item['image']}")

    if korean_filenames:
        print(f"\n⚠️  이미지 파일명에 한글이 포함된 포스팅 ({len(korean_filenames)}개):")
        for item in korean_filenames:
            print(f"  - {item['file']}: {item['image']}")

    if not results:
        print("\n✅ 모든 이미지 파일이 정상적으로 검증되었습니다!")

    print("=" * 80)


if __name__ == "__main__":
    main()
