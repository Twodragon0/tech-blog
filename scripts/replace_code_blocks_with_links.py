#!/usr/bin/env python3
"""
포스트 파일에서 코드 블록을 GitHub 링크나 관련 링크로 대체하는 스크립트
"""

import re
import os
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

# GitHub 링크 매핑 (코드 타입별) - 예제 저장소 우선
GITHUB_LINKS = {
    "terraform": "https://github.com/terraform-aws-modules",
    "hcl": "https://github.com/terraform-aws-modules",
    "yaml": "https://github.com/kubernetes/examples",
    "kubernetes": "https://github.com/kubernetes/examples",
    "python": "https://github.com/python/cpython/tree/main/Doc",
    "bash": None,  # Bash는 공식 문서 링크 사용
    "shell": None,  # Shell은 공식 문서 링크 사용
    "json": None,  # JSON은 공식 문서 링크 사용
    "dockerfile": "https://github.com/docker-library",
    "docker": "https://github.com/docker-library",
    "javascript": "https://github.com/nodejs/node/tree/main/doc",
    "typescript": "https://github.com/microsoft/TypeScript/tree/main/doc",
    "go": "https://github.com/golang/go/tree/master/doc",
    "rust": "https://github.com/rust-lang/rust/tree/master/src/doc",
    "java": "https://github.com/openjdk/jdk/tree/master/doc",
    "c": "https://github.com/torvalds/linux/tree/master/Documentation",
    "cpp": "https://github.com/microsoft/STL/tree/main/docs",
    "solidity": "https://github.com/ethereum/solidity/tree/develop/docs",
    "aws": "https://github.com/aws-samples",
}

# 관련 링크 매핑 (GitHub 링크가 없는 경우)
RELATED_LINKS = {
    "terraform": "https://registry.terraform.io/browse/modules?provider=aws",
    "hcl": "https://www.terraform.io/docs/language",
    "yaml": "https://yaml.org/spec/",
    "kubernetes": "https://kubernetes.io/docs/home/",
    "python": "https://docs.python.org/3/",
    "bash": "https://www.gnu.org/software/bash/manual/bash.html",
    "shell": "https://www.gnu.org/software/bash/manual/bash.html",
    "json": "https://www.json.org/json-en.html",
    "dockerfile": "https://docs.docker.com/engine/reference/builder/",
    "docker": "https://docs.docker.com/",
    "aws": "https://docs.aws.amazon.com/",
    "cloudformation": "https://docs.aws.amazon.com/cloudformation/",
}


def detect_code_type(code_block: str) -> Optional[str]:
    """코드 블록의 타입을 감지"""
    code_lower = code_block.lower()

    # Terraform/HCL
    if 'resource "aws_' in code_block or 'provider "aws"' in code_block:
        return "terraform"

    # Kubernetes YAML
    if "apiVersion:" in code_block and (
        "kind:" in code_block or "metadata:" in code_block
    ):
        return "kubernetes"

    # Docker
    if "FROM " in code_block and ("RUN " in code_block or "COPY " in code_block):
        return "dockerfile"

    # Python
    if "import " in code_block or "def " in code_block or "class " in code_block:
        return "python"

    # Bash/Shell
    if (
        code_block.startswith("#!")
        or "#!/bin/bash" in code_block
        or "#!/bin/sh" in code_block
    ):
        return "bash"

    # AWS CLI
    if "aws " in code_block and ("--region" in code_block or "--profile" in code_block):
        return "aws"

    # JSON
    if code_block.strip().startswith("{") and code_block.strip().endswith("}"):
        return "json"

    return None


def validate_url(url: str) -> bool:
    """
    URL이 안전한지 검증합니다.

    Args:
        url: 검증할 URL

    Returns:
        안전하면 True, 아니면 False
    """
    if not url or not isinstance(url, str):
        return False

    url_lower = url.lower().strip()

    # 보안: 위험한 스킴 차단 (완전한 스킴 검사)
    dangerous_schemes = ["javascript:", "data:", "vbscript:", "file:", "about:", "jar:"]
    for scheme in dangerous_schemes:
        # URL 시작 부분 또는 공백/줄바꿈 후에 오는 경우도 차단
        if (
            url_lower.startswith(scheme)
            or " " + scheme in url_lower
            or "\n" + scheme in url_lower
            or "\t" + scheme in url_lower
        ):
            return False

    # 보안: 허용된 스킴만 허용 (정확한 비교)
    if not url_lower.startswith("http://") and not url_lower.startswith("https://"):
        return False

    # 보안: URL 전체에서 위험한 패턴 검사 (부분 문자열 포함)
    dangerous_patterns = [
        "javascript:",
        "data:text/html",
        "data:text/javascript",
        "vbscript:",
        "onerror=",
        "onclick=",
        "<script",
        "<iframe",
        "expression(",
    ]

    for pattern in dangerous_patterns:
        if pattern in url_lower:
            return False

    # 보안: URL 파싱을 통한 추가 검증
    try:
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(url)

        # 파싱된 URL의 각 구성 요소 검증
        url_parts = [
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ]
        url_string = " ".join(str(part) for part in url_parts if part)

        # 각 구성 요소에서 위험한 패턴 검사
        for pattern in dangerous_patterns:
            if pattern in url_string.lower():
                return False

        # 스킴 재검증
        if parsed.scheme not in ["http", "https"]:
            return False

    except Exception:
        # URL 파싱 실패 시 안전하지 않은 것으로 간주
        return False

    return True


def get_replacement_link(
    code_type: Optional[str], code_block: str, context: str = ""
) -> Optional[str]:
    """코드 블록을 대체할 링크 반환"""
    code_lower = code_block.lower()

    # AWS 관련 코드는 AWS 예제 저장소 우선
    if "aws" in code_lower or "boto3" in code_lower or "amazon" in code_lower:
        if code_type in ["terraform", "hcl"]:
            link = "https://github.com/terraform-aws-modules"
        elif code_type == "python":
            link = "https://github.com/aws-samples"
        elif code_type == "yaml" and "kubernetes" in code_lower:
            link = "https://github.com/aws-samples/aws-k8s-examples"
        else:
            link = "https://github.com/aws-samples"

        # 보안: URL 검증
        if validate_url(link):
            return link
        return None

    # Kubernetes 관련
    if "kubernetes" in code_lower or "k8s" in code_lower or "kubectl" in code_lower:
        if code_type in ["yaml", "kubernetes"]:
            link = "https://github.com/kubernetes/examples"
        else:
            link = "https://github.com/kubernetes/examples"

        # 보안: URL 검증
        if validate_url(link):
            return link
        return None

    # Docker 관련
    if "docker" in code_lower or "container" in code_lower:
        link = "https://github.com/docker-library"
        # 보안: URL 검증
        if validate_url(link):
            return link
        return None

    # GitHub 링크 우선
    if code_type in GITHUB_LINKS and GITHUB_LINKS[code_type]:
        link = GITHUB_LINKS[code_type]
        # 보안: URL 검증
        if validate_url(link):
            return link
        return None

    # 관련 링크
    if code_type in RELATED_LINKS:
        link = RELATED_LINKS[code_type]
        # 보안: URL 검증
        if validate_url(link):
            return link
        return None

    return None


def should_replace_code_block(code_block: str, code_type: str) -> bool:
    """코드 블록을 대체해야 하는지 판단"""
    # 너무 짧은 코드 블록은 유지 (설명용)
    if len(code_block.strip()) < 20:
        return False

    # 주석만 있는 코드 블록은 유지
    lines = code_block.strip().split("\n")
    non_comment_lines = [
        line for line in lines if line.strip() and not line.strip().startswith("#")
    ]
    if len(non_comment_lines) < 2:
        return False

    return True


def replace_code_blocks(content: str) -> str:
    """마크다운 파일의 코드 블록에 GitHub 링크 추가 또는 대체"""
    # 코드 블록 패턴: ```language\n...\n```
    pattern = r"```(\w+)?\n(.*?)```"

    def replace_match(match):
        language = match.group(1) or ""
        code_block = match.group(2)
        full_match = match.group(0)

        context_start = max(0, match.start() - 200)
        context = content[context_start : match.start()]
        import re

        existing_marker_pattern = r"(\*\*코드 예시\*\*|전체 코드는 위 GitHub 링크 참조)"
        if re.search(existing_marker_pattern, context, re.IGNORECASE):
            return full_match

        # 코드 타입 감지
        code_type = (
            language.lower() if language else detect_code_type(code_block)
        ) or ""

        # 링크 가져오기
        link = get_replacement_link(code_type, code_block)

        # 코드 블록 길이 확인
        code_lines = len(code_block.strip().split("\n"))
        code_length = len(code_block.strip())

        # 보안: 링크 검증
        if link and not validate_url(link):
            link = None  # 검증 실패 시 링크 제거

        # 긴 코드 블록 (10줄 이상 또는 500자 이상)은 링크로 대체
        if code_lines >= 10 or code_length >= 500:
            if link:
                # 보안: 링크 이스케이프 (마크다운 링크 형식에서 안전하게 처리)
                code_preview = code_block.split("\n")[0][:80].strip()
                # 보안: URL에 위험한 문자가 포함되지 않도록 검증된 링크만 사용
                safe_link = link.replace("]", "%5D").replace(
                    "[", "%5B"
                )  # 마크다운 링크 구문자 이스케이프
                return f"> **코드 예시**: 전체 코드는 [GitHub 예제 저장소]({safe_link})를 참조하세요.\n> \n> ```{language}\n> {code_preview}...\n> ```\n\n<!-- 전체 코드는 위 GitHub 링크 참조 -->"
            else:
                # 링크가 없으면 주석 처리
                return "<!-- 긴 코드 블록 제거됨 (가독성 향상) -->"
        else:
            # 짧은 코드 블록은 유지하되 링크 추가 (너무 짧으면 링크 추가 안 함)
            if link and code_lines >= 3:  # 3줄 이상인 경우만 링크 추가
                # 보안: 링크 재검증 (방어적 프로그래밍)
                if not validate_url(link):
                    return full_match  # 검증 실패 시 링크 추가하지 않음

                # 보안: 링크 이스케이프 (마크다운 링크 형식에서 안전하게 처리)
                # 보안: URL 파싱을 통해 netloc을 안전하게 확인 (부분 문자열 매칭 방지)
                from urllib.parse import quote, urlparse, urlunparse

                # URL 파싱을 통해 각 구성 요소를 안전하게 인코딩
                parsed = urlparse(link)
                # 보안: 정확한 도메인 매칭 (부분 문자열 매칭 방지)
                # evil.github.com 같은 도메인을 차단하기 위해 정확히 github.com 또는 www.github.com만 허용
                netloc_lower = parsed.netloc.lower() if parsed.netloc else ""
                is_github = (
                    netloc_lower == "github.com"
                    or netloc_lower == "www.github.com"
                    or netloc_lower.endswith(".github.com")
                    and netloc_lower.count(".") == 2
                )
                link_text = "GitHub 예제 저장소" if is_github else "공식 문서"
                # 보안: URL에 위험한 문자가 포함되지 않도록 검증된 링크만 사용
                # 각 구성 요소를 개별적으로 인코딩하여 부분 문자열 우회 방지
                safe_scheme = parsed.scheme
                safe_netloc = parsed.netloc
                safe_path = quote(parsed.path, safe="/")
                safe_params = quote(parsed.params, safe=";")
                safe_query = quote(parsed.query, safe="=&?")
                safe_fragment = quote(parsed.fragment, safe="#")
                # 안전하게 재구성된 URL
                safe_link = urlunparse(
                    (
                        safe_scheme,
                        safe_netloc,
                        safe_path,
                        safe_params,
                        safe_query,
                        safe_fragment,
                    )
                )
                # 마크다운 링크 구문자 추가 이스케이프 (URL 인코딩)
                safe_link = safe_link.replace("]", "%5D").replace("[", "%5B")
                # 최종 URL 검증 (재구성 후에도 안전한지 확인)
                if not validate_url(safe_link):
                    return full_match  # 검증 실패 시 링크 추가하지 않음
                return f"> **참고**: 관련 예제는 [{link_text}]({safe_link})를 참조하세요.\n\n{full_match}"
            else:
                return full_match  # 링크가 없거나 너무 짧으면 원본 유지

    return re.sub(pattern, replace_match, content, flags=re.DOTALL)


def process_post_file(file_path: Path) -> bool:
    """포스트 파일 처리"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 코드 블록이 있는지 확인
        if "```" not in content:
            return False

        # 코드 블록 대체
        new_content = replace_code_blocks(content)

        # 변경사항이 있는지 확인
        if content != new_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    posts_dir = Path(__file__).parent.parent / "_posts"

    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return

    parser = argparse.ArgumentParser(
        description="Replace long code blocks with reference links"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific post files to process (default: all posts)",
    )
    args = parser.parse_args()

    if args.files:
        target_files = [Path(file_path) for file_path in args.files]
        resolved_files = []
        for file_path in target_files:
            if not file_path.is_absolute():
                file_path = posts_dir / file_path
            if file_path.exists():
                resolved_files.append(file_path)
            else:
                print(f"File not found: {file_path}")
        post_files = resolved_files
    else:
        post_files = list(posts_dir.glob("*.md"))

    processed = 0
    updated = 0

    for post_file in post_files:
        processed += 1
        if process_post_file(post_file):
            updated += 1
            print(f"Updated: {post_file.name}")

    print(f"\nProcessed: {processed} files")
    print(f"Updated: {updated} files")


if __name__ == "__main__":
    main()
