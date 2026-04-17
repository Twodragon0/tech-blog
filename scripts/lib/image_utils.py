#!/usr/bin/env python3
"""이미지 경로 추출/검증 공용 유틸리티.

여러 스크립트에서 반복되던 이미지 경로 추출(markdown / HTML / front matter)과
파일 존재 검증 로직을 한 곳에 모았습니다. 기존 호출부와의 하위 호환을 위해
`check_image_exists`는 원본 시그니처(`Tuple[bool, Optional[Path]]`)를 유지합니다.

사용 예시::

    from scripts.lib.image_utils import (
        extract_image_paths,
        check_image_exists,
        has_korean,
    )

    paths = extract_image_paths(content)  # ['2025-01-01-diagram.svg', ...]
    exists, resolved = check_image_exists("/assets/images/diagram.svg")
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# --- 경로 상수 ------------------------------------------------------------
# `scripts/lib/image_utils.py` 기준으로 두 단계 상위가 프로젝트 루트입니다.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR: Path = PROJECT_ROOT / "assets" / "images"

# --- 정규식 ---------------------------------------------------------------
_KOREAN_RE = re.compile(r"[가-힣]")
_FRONT_MATTER_IMAGE_RE = re.compile(r"^image:\s*(.+)$", re.MULTILINE)
_HTML_IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
_MD_IMG_RE = re.compile(r"!\[.*?\]\(([^)]+)\)")


@dataclass(frozen=True)
class ImageIssue:
    """포스트에서 발견된 이미지 문제를 표현하는 컨테이너."""

    post: Path
    image: str
    reason: str  # "missing" | "korean_filename" | "read_error"


def has_korean(text: str) -> bool:
    """한글 문자(가-힣) 포함 여부.

    >>> has_korean("보안.svg")
    True
    >>> has_korean("image.png")
    False
    """
    return bool(_KOREAN_RE.search(text or ""))


def _strip_relative_url(path: str) -> str:
    """Jekyll `{{ '/path' | relative_url }}` 필터 처리."""
    if "| relative_url" in path:
        return path.split("|", 1)[0].strip().strip("'\"")
    return path


def extract_image_paths(content: str) -> List[str]:
    """포스트 본문에서 이미지 파일명(assets/images 기준)을 추출합니다.

    다음을 모두 스캔합니다:
      - Front matter의 ``image:`` 필드
      - HTML ``<img src="...">`` 태그
      - Markdown ``![alt](src)`` 문법
      - Jekyll ``| relative_url`` 필터 사용 경로

    반환값은 `assets/images/` 뒤의 상대 경로만 포함하며 중복이 제거됩니다.

    >>> extract_image_paths("![x](/assets/images/a.svg)")
    ['a.svg']
    """
    raw: List[str] = []

    fm = _FRONT_MATTER_IMAGE_RE.search(content)
    if fm:
        raw.append(fm.group(1).strip())

    raw.extend(_HTML_IMG_RE.findall(content))
    raw.extend(_MD_IMG_RE.findall(content))

    cleaned: List[str] = []
    for item in raw:
        path = _strip_relative_url(item)
        if "/assets/images/" in path:
            cleaned.append(path.split("/assets/images/")[-1])
        elif "assets/images/" in path:
            cleaned.append(path.split("assets/images/")[-1])
        elif path.startswith("/assets/images/"):
            cleaned.append(path.replace("/assets/images/", ""))

    # 중복 제거 (순서는 보장하지 않음 — 기존 verify_images_unified.py와 동일)
    return list(set(cleaned))


def normalize_image_path(
    image_path: str,
    *,
    project_root: Optional[Path] = None,
    images_dir: Optional[Path] = None,
) -> Path:
    """다양한 형태의 이미지 경로를 실제 파일 시스템 경로로 정규화합니다.

    - ``/assets/images/foo.svg`` → ``<project_root>/assets/images/foo.svg``
    - ``assets/images/foo.svg`` → ``<project_root>/assets/images/foo.svg``
    - 그 외 (파일명만)            → ``<images_dir>/foo.svg``

    `project_root` / `images_dir`를 명시하지 않으면 모듈 기본값을 사용합니다.
    """
    root = project_root if project_root is not None else PROJECT_ROOT
    images = images_dir if images_dir is not None else IMAGES_DIR

    if image_path.startswith("/assets/images/"):
        return root / image_path.lstrip("/")
    if image_path.startswith("assets/images/"):
        return root / image_path
    return images / Path(image_path).name


def image_exists(
    image_path: str,
    *,
    project_root: Optional[Path] = None,
    images_dir: Optional[Path] = None,
) -> bool:
    """이미지 파일 존재 여부만 `bool`로 반환합니다."""
    if not image_path:
        return False
    return normalize_image_path(
        image_path, project_root=project_root, images_dir=images_dir
    ).exists()


def check_image_exists(
    image_path: str,
    *,
    project_root: Optional[Path] = None,
    images_dir: Optional[Path] = None,
) -> Tuple[bool, Optional[Path]]:
    """기존 `check_image_exists` 호출부와 호환되는 검증 함수.

    `(존재 여부, 정규화된 Path 혹은 None)` 튜플을 반환합니다.
    `image_path`가 빈 문자열이면 `(False, None)`을 돌려줍니다.
    """
    if not image_path:
        return False, None
    resolved = normalize_image_path(
        image_path, project_root=project_root, images_dir=images_dir
    )
    return resolved.exists(), resolved


def check_image_references(
    post_path: Path,
    *,
    project_root: Optional[Path] = None,
    images_dir: Optional[Path] = None,
) -> List[ImageIssue]:
    """포스트 내 참조된 모든 이미지에 대해 누락/한글 파일명 이슈를 반환합니다."""
    try:
        content = post_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [ImageIssue(post=post_path, image=str(post_path), reason=f"read_error:{exc}")]

    issues: List[ImageIssue] = []
    for rel in extract_image_paths(content):
        if has_korean(rel):
            issues.append(ImageIssue(post=post_path, image=rel, reason="korean_filename"))
        if not image_exists(rel, project_root=project_root, images_dir=images_dir):
            issues.append(ImageIssue(post=post_path, image=rel, reason="missing"))
    return issues


def iter_image_files(
    root: Optional[Path] = None,
    *,
    extensions: Iterable[str] = (".svg", ".png", ".webp", ".jpg", ".jpeg"),
) -> List[Path]:
    """`assets/images/` 하위의 모든 이미지 파일을 리스트로 반환합니다."""
    base = root if root is not None else IMAGES_DIR
    exts = {e.lower() for e in extensions}
    return [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in exts]


__all__ = [
    "ImageIssue",
    "IMAGES_DIR",
    "PROJECT_ROOT",
    "check_image_exists",
    "check_image_references",
    "extract_image_paths",
    "has_korean",
    "image_exists",
    "iter_image_files",
    "normalize_image_path",
]
