#!/usr/bin/env python3
"""
이미지 최적화 스크립트 (WebP, AVIF)
모든 이미지를 WebP 및 AVIF 형식으로 변환하여 성능 향상

사용법:
    python3 scripts/optimize_images.py [--format webp|avif|both] [--quality 80-100] [--dir assets/images]
"""

import argparse
import sys
from pathlib import Path
from typing import List

# Pillow import (이미지 처리)
try:
    from PIL import Image, ImageOps

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow 라이브러리가 없습니다. 설치: pip install Pillow")
    sys.exit(1)

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 지원되는 이미지 형식
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"}


def log_message(message: str, level: str = "INFO"):
    """로그 메시지 출력"""
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
    }
    icon = icons.get(level, "ℹ️")
    print(f"{icon} {message}")


def optimize_image(
    image_path: Path,
    output_format: str = "webp",
    quality: int = 85,
    create_avif: bool = False,
) -> List[Path]:
    """
    이미지를 최적화하고 WebP/AVIF 버전 생성

    Args:
        image_path: 원본 이미지 경로
        output_format: 출력 형식 ('webp', 'avif', 'both')
        quality: 품질 (80-100)
        create_avif: AVIF 생성 여부

    Returns:
        생성된 파일 경로 리스트
    """
    created_files = []

    if not image_path.exists():
        log_message(f"이미지 파일을 찾을 수 없습니다: {image_path}", "ERROR")
        return created_files

    try:
        with Image.open(image_path) as img:
            # 이미지 최적화 (EXIF 데이터 제거, 회전 정규화)
            img = ImageOps.exif_transpose(img)

            # RGB 모드로 변환 (WebP/AVIF는 RGB만 지원)
            if img.mode in ("RGBA", "LA", "P"):
                # 투명도가 있는 경우
                if img.mode == "P" and "transparency" in img.info:
                    img = img.convert("RGBA")
                elif img.mode in ("RGBA", "LA"):
                    pass  # 이미 RGBA/LA
                else:
                    img = img.convert("RGB")
            elif img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # WebP 생성
            if output_format in ("webp", "both"):
                webp_path = image_path.with_suffix(".webp")
                save_options = {
                    "format": "WebP",
                    "quality": quality,
                    "method": 6,  # 최고 압축 (느리지만 작은 파일)
                }

                # 투명도 지원
                if img.mode == "RGBA":
                    save_options["lossless"] = False
                    save_options["quality"] = quality

                img.save(webp_path, **save_options)
                created_files.append(webp_path)
                original_size = image_path.stat().st_size
                webp_size = webp_path.stat().st_size
                reduction = ((original_size - webp_size) / original_size) * 100
                log_message(
                    f"WebP 생성: {webp_path.name} "
                    f"({original_size // 1024}KB → {webp_size // 1024}KB, "
                    f"-{reduction:.1f}%)",
                    "SUCCESS",
                )

            # AVIF 생성 (Pillow 8.0+ 필요)
            if create_avif or output_format in ("avif", "both"):
                try:
                    avif_path = image_path.with_suffix(".avif")
                    save_options = {
                        "format": "AVIF",
                        "quality": quality,
                    }

                    # 투명도 지원
                    if img.mode == "RGBA":
                        save_options["lossless"] = False

                    img.save(avif_path, **save_options)
                    created_files.append(avif_path)
                    original_size = image_path.stat().st_size
                    avif_size = avif_path.stat().st_size
                    reduction = ((original_size - avif_size) / original_size) * 100
                    log_message(
                        f"AVIF 생성: {avif_path.name} "
                        f"({original_size // 1024}KB → {avif_size // 1024}KB, "
                        f"-{reduction:.1f}%)",
                        "SUCCESS",
                    )
                except Exception as e:
                    log_message(
                        f"AVIF 생성 실패 (Pillow 8.0+ 필요): {str(e)}", "WARNING"
                    )

            # 원본 PNG 최적화 (PNG인 경우)
            if image_path.suffix.lower() == ".png":
                try:
                    # PNG 최적화 (덮어쓰기)
                    img.save(image_path, format="PNG", optimize=True)
                    log_message(f"PNG 최적화 완료: {image_path.name}", "SUCCESS")
                except Exception as e:
                    log_message(f"PNG 최적화 실패: {str(e)}", "WARNING")

    except Exception as e:
        log_message(f"이미지 처리 실패: {image_path.name} - {str(e)}", "ERROR")

    return created_files


def find_images(directory: Path, recursive: bool = True) -> List[Path]:
    """디렉토리에서 이미지 파일 찾기"""
    images = []

    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    for ext in SUPPORTED_FORMATS:
        images.extend(directory.glob(f"{pattern}{ext}"))
        images.extend(directory.glob(f"{pattern}{ext.upper()}"))

    return sorted(set(images))


def main():
    parser = argparse.ArgumentParser(description="이미지 최적화 스크립트 (WebP, AVIF)")
    parser.add_argument(
        "--format",
        choices=["webp", "avif", "both"],
        default="both",
        help="생성할 형식 (기본값: both)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        choices=range(80, 101),
        metavar="80-100",
        help="이미지 품질 (기본값: 85)",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=IMAGES_DIR,
        help=f"이미지 디렉토리 (기본값: {IMAGES_DIR})",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="하위 디렉토리 포함 (기본값: True)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 변환 없이 미리보기만",
    )

    args = parser.parse_args()

    if not PIL_AVAILABLE:
        log_message("Pillow 라이브러리가 필요합니다.", "ERROR")
        sys.exit(1)

    if not args.dir.exists():
        log_message(f"이미지 디렉토리를 찾을 수 없습니다: {args.dir}", "ERROR")
        sys.exit(1)

    log_message(f"이미지 최적화 시작: {args.dir}")
    log_message(f"형식: {args.format}, 품질: {args.quality}")

    if args.dry_run:
        log_message("🔍 DRY RUN 모드 (실제 변환 없음)", "WARNING")

    images = find_images(args.dir, recursive=args.recursive)

    if not images:
        log_message("처리할 이미지를 찾을 수 없습니다.", "WARNING")
        return

    log_message(f"총 {len(images)}개 이미지 발견", "INFO")

    created_files = []
    skipped_files = []
    failed_files = []

    for image_path in images:
        # 이미 최적화된 파일은 건너뛰기 (선택사항)
        if args.format in ("webp", "both") and image_path.with_suffix(".webp").exists():
            if not args.dry_run:
                skipped_files.append(image_path)
                continue

        if args.format in ("avif", "both"):
            avif_path = image_path.with_suffix(".avif")
            if avif_path.exists() and not args.dry_run:
                skipped_files.append(image_path)
                continue

        if args.dry_run:
            log_message(f"[DRY RUN] 변환 예정: {image_path.name}", "INFO")
            continue

        try:
            created = optimize_image(
                image_path,
                output_format=args.format,
                quality=args.quality,
                create_avif=args.format in ("avif", "both"),
            )
            created_files.extend(created)
        except Exception as e:
            log_message(f"처리 실패: {image_path.name} - {str(e)}", "ERROR")
            failed_files.append(image_path)

    # 결과 요약
    print("\n" + "=" * 50)
    log_message("최적화 완료", "SUCCESS")
    print(f"  - 처리된 이미지: {len(images)}개")
    print(f"  - 생성된 파일: {len(created_files)}개")
    if skipped_files:
        print(f"  - 건너뛴 파일: {len(skipped_files)}개 (이미 최적화됨)")
    if failed_files:
        print(f"  - 실패한 파일: {len(failed_files)}개")
    print("=" * 50)


if __name__ == "__main__":
    main()
