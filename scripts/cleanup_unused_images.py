#!/usr/bin/env python3
"""
미사용 이미지 정리 스크립트

_posts/*.md 및 레이아웃/인클루드 파일에서 이미지 참조를 추출하고
assets/images/ 디렉토리의 미사용 이미지와 누락된 이미지를 분석합니다.

사용법:
    python3 scripts/cleanup_unused_images.py              # 기본 분석 (dry-run)
    python3 scripts/cleanup_unused_images.py --verbose    # 상세 목록 출력
    python3 scripts/cleanup_unused_images.py --missing    # 누락 이미지만 표시
    python3 scripts/cleanup_unused_images.py --delete     # 미사용 이미지 삭제 (확인 필요)
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
IMAGES_DIR = REPO_ROOT / "assets" / "images"
LAYOUTS_DIR = REPO_ROOT / "_layouts"
INCLUDES_DIR = REPO_ROOT / "_includes"
ARCHIVE_DIR = IMAGES_DIR / "_unused_archive"

# 미사용 이미지 집계에서 제외할 디렉토리 (빌드 결과물, 아카이브 등)
# _unused_archive는 별도로 처리하므로 여기서는 제외하지 않음
SKIP_DIRS = {"_site", ".git"}

# 항상 유지할 정적 이미지 (레이아웃/인클루드에서 참조)
STATIC_IMAGES = {
    "og-default.png",
    "og-default.webp",
    "og-default.avif",
    "favicon.png",
    "apple-touch-icon.png",
    "news-fallback.svg",
}


def extract_image_refs_from_file(filepath: Path) -> set[str]:
    """파일에서 이미지 참조 경로를 추출합니다."""
    refs = set()
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return refs

    # front matter image: /assets/images/...
    for match in re.finditer(r"^image\s*:\s*['\"]?(/assets/images/[^\s'\"]+)['\"]?", content, re.MULTILINE):
        refs.add(match.group(1))

    # Markdown image syntax: ![alt](path)
    for match in re.finditer(r"!\[[^\]]*\]\((/assets/images/[^\s)]+)\)", content):
        refs.add(match.group(1))

    # HTML img src: <img src="/assets/images/...">
    for match in re.finditer(r'<img[^>]+src=["\']([^"\']*assets/images/[^"\']+)["\']', content):
        refs.add(match.group(1))

    # HTML picture source srcset: <source srcset="...">
    for match in re.finditer(r'<source[^>]+srcset=["\']([^"\']*assets/images/[^"\']+)["\']', content):
        path = match.group(1).split()[0]  # srcset에서 첫 URL만
        refs.add(path)

    # src= 또는 href= 패턴 (레이아웃/인클루드용)
    for match in re.finditer(r'(?:src|href)=["\']([^"\']*assets/images/[^"\']+)["\']', content):
        refs.add(match.group(1))

    # Liquid {{ ... }} 내부 assets/images 참조
    for match in re.finditer(r"\{%[^%]*%\}|{{[^}]*}}", content):
        inner = match.group(0)
        for m2 in re.finditer(r"['\"]([^'\"]*assets/images/[^'\"]+)['\"]", inner):
            refs.add(m2.group(1))

    # {% raw %}{{ '/assets/images/...' | filter }}{% endraw %} 패턴
    for match in re.finditer(r"\{%-?\s*raw\s*-?%\}(.*?)\{%-?\s*endraw\s*-?%\}", content, re.DOTALL):
        inner = match.group(1)
        for m2 in re.finditer(r"['\"]([^'\"]*assets/images/[^'\"]+)['\"]", inner):
            refs.add(m2.group(1))

    return refs


def normalize_ref(ref: str) -> str:
    """참조 경로를 정규화합니다 (앞의 /assets/images/ 제거)."""
    ref = ref.strip()
    # /assets/images/ 또는 assets/images/ 제거
    if ref.startswith("/assets/images/"):
        return ref[len("/assets/images/"):]
    if ref.startswith("assets/images/"):
        return ref[len("assets/images/"):]
    return ref


def get_base_stem(filename: str) -> str:
    """파일명에서 확장자 및 _og, .webp, .avif 등 변형 접미사를 제거한 기본 이름을 반환합니다."""
    stem = Path(filename).stem
    # _og 접미사 제거
    if stem.endswith("_og"):
        stem = stem[:-3]
    # _image 접미사 제거
    if stem.endswith("_image"):
        stem = stem[:-6]
    return stem


def collect_all_refs() -> tuple[dict[str, set[Path]], set[str]]:
    """
    모든 소스 파일에서 이미지 참조를 수집합니다.

    Returns:
        (refs_map, static_refs)
        refs_map: {정규화된 이미지 경로 -> {참조한 파일들}}
        static_refs: 레이아웃/인클루드에서 참조된 정적 이미지 이름 집합
    """
    refs_map: dict[str, set[Path]] = defaultdict(set)
    static_refs: set[str] = set()

    # _posts/ 수집
    for post_file in POSTS_DIR.glob("*.md"):
        for ref in extract_image_refs_from_file(post_file):
            norm = normalize_ref(ref)
            if norm:
                refs_map[norm].add(post_file)

    # _layouts/ 수집
    for layout_file in LAYOUTS_DIR.rglob("*.html"):
        for ref in extract_image_refs_from_file(layout_file):
            norm = normalize_ref(ref)
            if norm:
                refs_map[norm].add(layout_file)
                static_refs.add(norm)

    # _includes/ 수집
    for inc_file in INCLUDES_DIR.rglob("*.html"):
        for ref in extract_image_refs_from_file(inc_file):
            norm = normalize_ref(ref)
            if norm:
                refs_map[norm].add(inc_file)
                static_refs.add(norm)

    return refs_map, static_refs


def collect_all_images() -> tuple[list[Path], list[Path]]:
    """
    assets/images/ 디렉토리의 모든 이미지 파일을 수집합니다.

    Returns:
        (active_images, archive_images)
        active_images: _unused_archive 제외한 활성 이미지
        archive_images: _unused_archive 내 이미지
    """
    active_images = []
    archive_images = []
    for f in IMAGES_DIR.rglob("*"):
        if not f.is_file():
            continue
        rel_parts = f.relative_to(IMAGES_DIR).parts
        # 빌드 결과물 디렉토리 스킵
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        # _unused_archive 분리
        if rel_parts[0] == "_unused_archive":
            archive_images.append(f)
        else:
            active_images.append(f)
    return active_images, archive_images


def is_referenced(image_path: Path, refs_map: dict[str, set[Path]]) -> bool:
    """
    이미지가 참조되는지 확인합니다.
    WebP/AVIF/PNG 변형은 원본 SVG가 참조되면 참조된 것으로 간주합니다.
    _og 변형은 원본 이미지가 참조되면 참조된 것으로 간주합니다.
    """
    rel = str(image_path.relative_to(IMAGES_DIR))

    # 직접 참조 확인
    if rel in refs_map:
        return True

    # 하위 디렉토리 내 파일은 서브경로 포함해서도 확인
    # (예: og/filename.png -> 참조는 og/filename.png 형태)
    for ref_key in refs_map:
        if ref_key == rel:
            return True

    # 변형 이미지 처리: 원본 stem을 확인
    # 예: foo.webp -> foo.svg / foo.png 가 참조되면 OK
    # 예: foo_og.png -> foo.svg / foo.png 가 참조되면 OK
    stem = image_path.stem
    ext = image_path.suffix.lower()
    parent_rel = str(image_path.parent.relative_to(IMAGES_DIR)) if image_path.parent != IMAGES_DIR else ""

    def make_rel(name: str) -> str:
        if parent_rel and parent_rel != ".":
            return f"{parent_rel}/{name}"
        return name

    # WebP/AVIF 변형: 같은 stem의 원본이 참조되면 OK
    if ext in {".webp", ".avif"}:
        for orig_ext in [".svg", ".png", ".jpg", ".jpeg", ".gif"]:
            orig_rel = make_rel(stem + orig_ext)
            if orig_rel in refs_map:
                return True

    # _og 변형 처리: foo_og.* -> foo.* 가 참조되면 OK
    if stem.endswith("_og"):
        base_stem = stem[:-3]
        for check_ext in [".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif"]:
            base_rel = make_rel(base_stem + check_ext)
            if base_rel in refs_map:
                return True
        # WebP/AVIF _og 변형: foo_og.webp -> foo_og.png 가 참조되면 OK
        if ext in {".webp", ".avif"}:
            for orig_ext in [".svg", ".png", ".jpg"]:
                orig_rel = make_rel(stem + orig_ext)
                if orig_rel in refs_map:
                    return True

    # _image 접미사 변형: foo_image.png -> foo.svg 가 참조되면 OK
    if stem.endswith("_image"):
        base_stem = stem[:-6]
        for check_ext in [".svg", ".png", ".jpg", ".jpeg"]:
            base_rel = make_rel(base_stem + check_ext)
            if base_rel in refs_map:
                return True

    # 정적 이미지 (favicon, og-default 등)
    filename = image_path.name
    if filename in STATIC_IMAGES:
        return True

    return False


def format_size(size_bytes: int) -> str:
    """바이트 크기를 읽기 쉬운 형식으로 변환합니다."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes //= 1024
    return f"{size_bytes:.1f} TB"


def analyze(verbose: bool = False, show_missing: bool = False) -> dict:
    """이미지 참조 분석을 실행하고 결과를 반환합니다."""
    print("이미지 참조 분석 중...")

    refs_map, static_refs = collect_all_refs()
    active_images, archive_images = collect_all_images()

    missing_images: dict[str, set[Path]] = {}  # 참조는 있지만 파일 없음
    # _unused_archive 내 파일을 빠른 검색용 이름 맵으로 구성
    archive_by_name: dict[str, Path] = {}  # filename -> path
    archive_by_rel: dict[str, Path] = {}   # rel path from _unused_archive -> path
    for f in archive_images:
        archive_by_name[f.name] = f
        rel = str(f.relative_to(ARCHIVE_DIR))
        archive_by_rel[rel] = f

    # 참조된 이미지 중 실제 파일 존재 여부 확인
    for ref_norm, source_files in refs_map.items():
        image_path = IMAGES_DIR / ref_norm
        if not image_path.exists():
            # _unused_archive에도 없는 경우만 진짜 누락
            archive_path = ARCHIVE_DIR / ref_norm
            filename = Path(ref_norm).name
            if not archive_path.exists() and filename not in archive_by_name:
                missing_images[ref_norm] = source_files

    unused_images = []
    used_images = []

    for img_path in active_images:
        if is_referenced(img_path, refs_map):
            used_images.append(img_path)
        else:
            unused_images.append(img_path)

    # 아카이브 디렉토리 파일 중 참조된 것 (복원 가능한 누락 이미지)
    restorable_images: dict[str, Path] = {}  # ref_norm -> archive path
    for ref_norm, source_files in refs_map.items():
        image_path = IMAGES_DIR / ref_norm
        if not image_path.exists():
            archive_path = ARCHIVE_DIR / ref_norm
            filename = Path(ref_norm).name
            if archive_path.exists():
                restorable_images[ref_norm] = archive_path
            elif filename in archive_by_name:
                restorable_images[ref_norm] = archive_by_name[filename]

    # 미사용 이미지 총 크기 계산
    total_unused_size = sum(f.stat().st_size for f in unused_images)

    return {
        "active_images": active_images,
        "archive_images": archive_images,
        "used_images": used_images,
        "unused_images": unused_images,
        "missing_images": missing_images,
        "restorable_images": restorable_images,
        "refs_map": refs_map,
        "total_unused_size": total_unused_size,
    }


def print_report(result: dict, verbose: bool = False, show_missing: bool = False) -> None:
    """분석 결과를 출력합니다."""
    active_images = result["active_images"]
    archive_images = result["archive_images"]
    used_images = result["used_images"]
    unused_images = result["unused_images"]
    missing_images = result["missing_images"]
    restorable_images = result["restorable_images"]
    total_unused_size = result["total_unused_size"]

    total_active = len(active_images)
    total_with_archive = total_active + len(archive_images)

    print("\n" + "=" * 65)
    print("이미지 분석 결과")
    print("=" * 65)
    print(f"  활성 이미지 (assets/images/):      {total_active:>5}개")
    print(f"  아카이브 이미지 (_unused_archive/): {len(archive_images):>5}개")
    print(f"  총 이미지 (활성+아카이브):         {total_with_archive:>5}개")
    print("-" * 65)
    print(f"  참조된 이미지 (사용 중):           {len(used_images):>5}개")
    print(f"  미사용 이미지 (활성 디렉토리):     {len(unused_images):>5}개")
    print(f"  미사용 총 크기:                    {format_size(total_unused_size):>8}")
    print("-" * 65)
    print(f"  참조O/파일X (진짜 누락):           {len(missing_images):>5}개")
    print(f"  아카이브에서 복원 가능:            {len(restorable_images):>5}개")
    print("=" * 65)

    if restorable_images and (verbose or show_missing):
        print(f"\n[복원 가능한 이미지] (_unused_archive에 존재, {len(restorable_images)}개)")
        print("-" * 65)
        for ref_norm in sorted(restorable_images.keys()):
            archive_path = restorable_images[ref_norm]
            source_files = result["refs_map"].get(ref_norm, set())
            post_sources = sorted(
                {f.name for f in source_files if str(f).endswith(".md")}
            )
            print(f"  RESTORABLE: assets/images/{ref_norm}")
            print(f"              (아카이브: {archive_path.relative_to(IMAGES_DIR)})")
            for post in post_sources:
                print(f"              <- {post}")

    if verbose or show_missing:
        if missing_images:
            print(f"\n[진짜 누락된 이미지 목록] (참조O/파일X, 아카이브에도 없음, {len(missing_images)}개)")
            print("-" * 65)
            for ref_norm in sorted(missing_images.keys()):
                source_files = missing_images[ref_norm]
                post_sources = sorted(
                    {f.name for f in source_files if str(f).endswith(".md")}
                )
                print(f"  MISSING: assets/images/{ref_norm}")
                for post in post_sources:
                    print(f"           <- {post}")
        else:
            print("\n누락된 이미지가 없습니다. (모든 참조 이미지가 존재하거나 아카이브에 있음)")

    if verbose:
        print(f"\n[미사용 이미지 목록] (활성 디렉토리, {len(unused_images)}개)")
        print("-" * 65)
        # 확장자별 그룹핑
        by_ext: dict[str, list[Path]] = defaultdict(list)
        for img in sorted(unused_images, key=lambda x: str(x.relative_to(IMAGES_DIR))):
            by_ext[img.suffix.lower()].append(img)

        ext_summary = ", ".join(
            f"{ext}:{len(files)}개" for ext, files in sorted(by_ext.items())
        )
        print(f"  확장자별: {ext_summary}")
        print()

        for img in sorted(unused_images, key=lambda x: str(x.relative_to(IMAGES_DIR))):
            rel = img.relative_to(IMAGES_DIR)
            size = img.stat().st_size
            print(f"  {rel}  ({format_size(size)})")

    print()


def restore_from_archive(restorable_images: dict[str, Path], skip_confirm: bool = False) -> None:
    """아카이브에서 복원 가능한 이미지를 활성 디렉토리로 복사합니다."""
    import shutil

    if not restorable_images:
        print("복원할 이미지가 없습니다.")
        return

    print(f"\n복원 대상: {len(restorable_images)}개 파일")
    for ref_norm, archive_path in sorted(restorable_images.items()):
        print(f"  {archive_path.name} → assets/images/{ref_norm}")

    if not skip_confirm:
        confirm = input(f"\n{len(restorable_images)}개 파일을 복원하시겠습니까? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("복원 취소됨.")
            return

    restored = 0
    for ref_norm, archive_path in restorable_images.items():
        dest = IMAGES_DIR / ref_norm
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(archive_path, dest)
            restored += 1
        except OSError as e:
            print(f"  오류: {archive_path} → {dest} - {e}")

    print(f"복원 완료: {restored}개")


def delete_unused(unused_images: list[Path], dry_run: bool = True, skip_confirm: bool = False) -> None:
    """미사용 이미지를 삭제합니다."""
    if not unused_images:
        print("삭제할 미사용 이미지가 없습니다.")
        return

    total_size = sum(f.stat().st_size for f in unused_images)
    print(f"\n삭제 대상: {len(unused_images)}개 파일 ({format_size(total_size)})")

    if dry_run:
        print("[DRY-RUN] 실제 삭제하지 않음. --delete 옵션으로 실제 삭제하세요.")
        return

    if not skip_confirm:
        confirm = input(f"\n정말로 {len(unused_images)}개 파일을 삭제하시겠습니까? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("삭제 취소됨.")
            return

    deleted = 0
    errors = 0
    for img in unused_images:
        try:
            img.unlink()
            deleted += 1
        except OSError as e:
            print(f"  오류: {img} - {e}")
            errors += 1

    print(f"삭제 완료: {deleted}개 / 오류: {errors}개")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="블로그 미사용 이미지 분석 및 정리 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python3 scripts/cleanup_unused_images.py              # 기본 요약 분석
  python3 scripts/cleanup_unused_images.py --verbose    # 전체 목록 출력
  python3 scripts/cleanup_unused_images.py --missing    # 누락 이미지만 표시
  python3 scripts/cleanup_unused_images.py --delete     # 미사용 이미지 삭제 (확인 필요)
""",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="미사용 이미지 전체 목록 출력")
    parser.add_argument("--missing", "-m", action="store_true", help="누락 이미지 목록만 출력")
    parser.add_argument("--delete", "-d", action="store_true", help="미사용 이미지 실제 삭제 (확인 프롬프트)")
    parser.add_argument("--restore", "-r", action="store_true", help="아카이브에서 누락 이미지 복원")
    parser.add_argument("--yes", "-y", action="store_true", help="확인 프롬프트 없이 실행")
    args = parser.parse_args()

    result = analyze()
    print_report(result, verbose=args.verbose, show_missing=args.missing or args.verbose)

    if args.restore:
        restore_from_archive(result["restorable_images"], skip_confirm=args.yes)

    if args.delete:
        delete_unused(result["unused_images"], dry_run=False, skip_confirm=args.yes)
    else:
        if not args.verbose and not args.missing:
            print("사용 가능한 옵션:")
            print("  --verbose 옵션: 미사용 이미지 전체 목록 + 누락 이미지 목록 출력")
            print("  --missing 옵션: 누락/복원 가능 이미지 목록 출력")
            print("  --delete  옵션: 미사용 이미지 삭제 실행 (확인 필요)")
        # 복원 가능한 이미지가 있으면 안내
        if result["restorable_images"] and not args.missing and not args.verbose:
            print(f"\n[안내] {len(result['restorable_images'])}개 이미지가 _unused_archive에 있어 복원 가능합니다.")
            print("  --missing 옵션으로 상세 내용을 확인하세요.")


if __name__ == "__main__":
    main()
