#!/usr/bin/env python3
"""
통합 링크 수정 스크립트
- 부적절한 GitHub 링크 수정
- 더미 링크 제거
- 참고자료 링크 검증 및 수정
- 코드 블록 링크 개선
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"

# GitHub 도메인 패턴
GITHUB_PATTERN = r"https?://(?:www\.)?github\.com/"

# 부적절한 링크 매핑
INVALID_LINKS = {
    "https://www.gnu.org/software/bash/manual/bash.html": {
        "text": "Bash 공식 문서",
        "link": "https://www.gnu.org/software/bash/manual/bash.html",
    },
    "https://www.json.org/json-en.html": {
        "text": "JSON 공식 문서",
        "link": "https://www.json.org/json-en.html",
    },
}

# 링크 교체 규칙
LINK_REPLACEMENTS = [
    # GitHub Actions/Dependabot 관련
    (
        r"github\.com/kubernetes/examples.*dependabot|dependabot.*github\.com/kubernetes/examples",
        r"[GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot)",
    ),
    # GitHub Actions 워크플로우
    (
        r"github\.com/kubernetes/examples.*workflows|\.github/workflows.*github\.com/kubernetes/examples",
        r"[GitHub Actions 문서](https://docs.github.com/en/actions)",
    ),
    # CodeQL 관련
    (
        r"github\.com/kubernetes/examples.*codeql|codeql.*github\.com/kubernetes/examples",
        r"[GitHub CodeQL 문서](https://docs.github.com/en/code-security/code-scanning/using-codeql-code-scanning-with-your-ci)",
    ),
    # AWS WAF/CloudFront
    (
        r"github\.com/aws-samples.*waf|waf.*github\.com/aws-samples|cloudfront.*github\.com/aws-samples",
        r"[AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)",
    ),
    # 자동차 보안 GitHub Actions
    (
        r"github\.com/kubernetes/examples.*automotive|automotive.*github\.com/kubernetes/examples",
        r"[GitHub Actions 보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)",
    ),
    # Falco 관련
    (
        r"github\.com/kubernetes/examples.*falco|falco.*github\.com/kubernetes/examples",
        r"[Falco 공식 저장소](https://github.com/falcosecurity/falco)",
    ),
    # SBOM 관련
    (
        r"github\.com/kubernetes/examples.*sbom|sbom.*github\.com/kubernetes/examples",
        r"[CycloneDX](https://github.com/CycloneDX/cyclonedx-cli) 및 [SPDX](https://github.com/spdx/tools)",
    ),
]

# 링크 수정 규칙
LINK_FIXES = [
    # Kubernetes 보안 Best Practices (404 오류)
    (
        r"https://kubernetes\.io/docs/concepts/security/best-practices/",
        "https://kubernetes.io/docs/concepts/security/security-checklist/",
    ),
    # Trivy 구버전 다운로드 링크
    (
        r"https://github\.com/aquasecurity/trivy/releases/latest/download/trivy_\d+\.\d+\.\d+_Linux-64bit\.tar\.gz",
        "https://github.com/aquasecurity/trivy/releases",
    ),
]

# 링크 텍스트 교체 규칙
TEXT_FIXES = [
    # docker-library 링크를 컨텍스트에 맞게 교체
    (
        r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/docker-library\)를 참조하세요\.",
        "> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.",
    ),
]

# 더미 링크 패턴
DUMMY_PATTERNS = [
    r"https?://(?:www\.)?github\.com/example",
    r"https?://(?:www\.)?github\.com/.*/example",
    r"더미",
    r"dummy",
    r"placeholder",
]


def is_github_link(url: str) -> bool:
    """URL이 GitHub 링크인지 확인.

    Args:
        url: 확인할 URL 문자열.

    Returns:
        GitHub 링크이면 True, 아니면 False.
    """
    return bool(re.search(GITHUB_PATTERN, url))


def fix_link_text(match) -> str:
    """링크 텍스트를 컨텍스트에 맞게 수정.

    'GitHub 예제 저장소'와 같은 일반적인 링크 텍스트를
    URL의 컨텍스트에 따라 '공식 문서' 등으로 변경합니다.

    Args:
        match: re.sub에서 전달된 re.Match 객체.

    Returns:
        수정된 마크다운 링크 문자열.
    """
    full_match = match.group(0)
    url = match.group(2)

    # GitHub 링크인지 확인
    if is_github_link(url):
        return full_match  # GitHub 링크는 그대로 유지

    # GitHub가 아닌 링크 처리
    if url in INVALID_LINKS:
        info = INVALID_LINKS[url]
        # "GitHub 예제 저장소"를 적절한 텍스트로 변경
        new_text = match.group(1).replace("GitHub 예제 저장소", info["text"])
        new_text = new_text.replace("GitHub 예제", info["text"])
        return f"[{new_text}]({url})"

    # 기타 GitHub가 아닌 링크
    new_text = match.group(1).replace("GitHub 예제 저장소", "공식 문서")
    new_text = new_text.replace("GitHub 예제", "공식 문서")
    return f"[{new_text}]({url})"


def fix_code_blocks(content: str) -> str:
    """코드 블록 관련 문제를 수정.

    - 주석 처리된 짧은 코드 블록(예: 설정, DNS 레코드)을 복원합니다.
    - 주석 내의 링크 참조 텍스트를 수정합니다.
    - 링크 텍스트를 컨텍스트에 맞게 수정합니다.
    - JSON 코드 블록의 GitHub 링크를 공식 문서 링크로 교체합니다.

    Args:
        content: 수정할 포스트의 전체 내용.

    Returns:
        수정된 포스트 내용.
    """
    # 1. 주석 처리된 짧은 코드 블록 복원 (DNS 레코드, 설정 예시 등)
    comment_pattern = (
        r"<!-- (?:긴 코드 블록 제거됨|코드 블록 제거됨).*?```(\w+)?\n(.*?)```\n-->"
    )

    def restore_short_code(match):
        language = match.group(1) or ""
        code_block = match.group(2)

        # 코드 블록 길이 확인
        lines = code_block.strip().split("\n")
        code_length = len(code_block.strip())

        # 짧은 코드 블록 (5줄 이하, 200자 이하)은 복원
        if len(lines) <= 5 and code_length <= 200:
            # DNS 레코드, 설정 예시, DMARC 설정 등은 복원
            keywords = [
                "dns",
                "txt",
                "record",
                "레코드",
                "설정",
                "config",
                "dmarc",
                "spf",
                "dkim",
                "v=dmarc",
                "v=spf",
            ]
            if any(keyword in code_block.lower() for keyword in keywords):
                return f"```{language}\n{code_block}\n```"

        return match.group(0)  # 긴 코드는 주석 유지

    content = re.sub(comment_pattern, restore_short_code, content, flags=re.DOTALL)

    # 2. 주석 내 "위 GitHub 링크 참조" 텍스트 수정
    comment_link_pattern = r"<!-- 전체 코드는 위 (GitHub )?링크 참조"

    def fix_comment_text(match):
        # 앞뒤 맥락 확인하여 GitHub 링크인지 확인
        start_pos = match.start()
        context = content[max(0, start_pos - 500) : start_pos + 100]
        if "github.com" not in context.lower():
            return "<!-- 전체 코드는 위 링크 참조"
        return match.group(0)

    content = re.sub(comment_link_pattern, fix_comment_text, content)

    # 3. 링크 텍스트 수정
    link_pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"
    content = re.sub(link_pattern, fix_link_text, content)

    # 4. JSON 코드 블록의 경우 GitHub 링크 대신 공식 문서 링크 사용
    json_pattern = r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/[^\)]+\)를 참조하세요\.\n> \n> ```json\n"
    json_replacement = r"> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.\n> \n> ```json\n"
    content = re.sub(json_pattern, json_replacement, content)

    return content


def fix_contextual_links(content: str) -> str:
    """포스트의 컨텍스트에 따라 일반적인 GitHub 링크를 더 구체적인 공식 문서 링크로 수정.

    예: 'kubernetes/examples'와 'dependabot' 키워드가 함께 나오면
    일반 GitHub 링크를 GitHub Dependabot 공식 문서 링크로 교체합니다.

    Args:
        content: 수정할 포스트의 전체 내용.

    Returns:
        수정된 포스트 내용.
    """
    # 패턴 1: GitHub Actions/Dependabot 워크플로우
    if ".github/workflows" in content or "dependabot" in content.lower():
        # Dependabot 설정
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?dependabot",
            r"> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # GitHub Actions 워크플로우
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?\.github/workflows",
            r"> **참고**: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # CodeQL
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?codeql",
            r"> **참고**: CodeQL 분석 설정 관련 내용은 [GitHub CodeQL 문서](https://docs.github.com/en/code-security/code-scanning/using-codeql-code-scanning-with-your-ci) 및 [CodeQL Action](https://github.com/github/codeql-action)을 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # 패턴 2: AWS WAF/CloudFront
    if "waf" in content.lower() or "cloudfront" in content.lower():
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/aws-samples\).*?(?:waf|cloudfront)",
            r"> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # 패턴 3: 자동차 보안
    if "automotive" in content.lower() or "자동차" in content:
        # SAST/보안 스캔
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?(?:sast|보안|security)",
            r"> **참고**: 자동차 보안 스캔 관련 내용은 [GitHub Actions 보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) 및 [SonarQube](https://github.com/SonarSource/sonarqube)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Falco
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?falco",
            r"> **참고**: Falco 런타임 보안 모니터링 관련 내용은 [Falco 공식 저장소](https://github.com/falcosecurity/falco)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # SBOM
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?sbom",
            r"> **참고**: SBOM 생성 관련 내용은 [CycloneDX](https://github.com/CycloneDX/cyclonedx-cli) 및 [SPDX](https://github.com/spdx/tools)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # 패턴 4: 블록체인 보안
    if (
        "blockchain" in content.lower()
        or "블록체인" in content
        or "solidity" in content.lower()
    ):
        content = re.sub(
            r"> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?(?:security-audit|securify)",
            r"> **참고**: 블록체인 보안 감사 관련 내용은 [Slither](https://github.com/crytic/slither), [Mythril](https://github.com/ConsenSys/mythril) 및 [Securify](https://github.com/eth-sri/securify2)를 참조하세요.",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

    return content


def fix_reference_links(content: str) -> str:
    """오래되거나 잘못된 참고자료 링크를 올바른 URL로 수정.

    Args:
        content: 수정할 포스트의 전체 내용.

    Returns:
        수정된 포스트 내용.
    """
    # URL 교체
    for pattern, replacement in LINK_FIXES:
        content = re.sub(pattern, replacement, content)

    # 텍스트 교체
    for pattern, replacement in TEXT_FIXES:
        content = re.sub(pattern, replacement, content)

    return content


def check_dummy_links(content: str) -> List[Tuple[int, str]]:
    """'dummy', 'placeholder' 등 더미 링크 패턴이 있는지 확인.

    Args:
        content: 검사할 포스트의 전체 내용.

    Returns:
        (줄 번호, 매치된 텍스트) 튜플의 리스트.
    """
    issues = []

    for pattern in DUMMY_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            issues.append((line_num, match.group()))

    return issues


def process_post_file(
    file_path: Path, fix_mode: bool = False, dry_run: bool = False
) -> Dict:
    """단일 포스트 파일을 처리하여 링크를 검사하고 선택적으로 수정.

    Args:
        file_path: 처리할 포스트 파일의 경로.
        fix_mode: True이면 링크를 실제로 수정.
        dry_run: True이고 fix_mode가 True이면, 변경사항을 파일에 쓰지 않음.

    Returns:
        처리 결과를 담은 딕셔너리.
    """
    result = {"file": str(file_path), "fixed": False, "issues": [], "fixed_links": []}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 더미 링크 확인
        dummy_issues = check_dummy_links(content)
        if dummy_issues:
            for line_num, match_text in dummy_issues:
                result["issues"].append(
                    f"Line {line_num}: Possible dummy link - {match_text}"
                )

        if fix_mode:
            # 코드 블록 및 링크 수정
            content = fix_code_blocks(content)

            # 컨텍스트 기반 링크 수정
            content = fix_contextual_links(content)

            # 참고자료 링크 수정
            content = fix_reference_links(content)

            # 변경사항이 있는지 확인
            if content != original_content:
                result["fixed"] = True
                if not dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

        return result

    except Exception as e:
        result["issues"].append(f"Error: {str(e)}")
        return result


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="통합 링크 수정 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 링크 확인만 (dry-run)
  python3 scripts/fix_links_unified.py --check
  
  # 링크 수정
  python3 scripts/fix_links_unified.py --fix
  
  # 특정 파일만 수정
  python3 scripts/fix_links_unified.py --fix _posts/2025-01-01-example.md
        """,
    )

    parser.add_argument(
        "--check", action="store_true", help="링크 확인만 수행 (수정하지 않음)"
    )
    parser.add_argument("--fix", action="store_true", help="링크 수정 수행")
    parser.add_argument(
        "--dry-run", action="store_true", help="수정 사항 미리보기 (실제 수정하지 않음)"
    )
    parser.add_argument("file", nargs="?", help="처리할 특정 파일 (선택사항)")

    args = parser.parse_args()

    if not args.check and not args.fix:
        parser.print_help()
        return

    if not POSTS_DIR.exists():
        print(f"❌ Posts directory not found: {POSTS_DIR}")
        return

    # 파일 목록
    if args.file:
        post_files = [Path(args.file)]
        if not post_files[0].is_absolute():
            post_files[0] = PROJECT_ROOT / post_files[0]
    else:
        post_files = sorted(POSTS_DIR.glob("*.md"))

    print("=" * 80)
    print("통합 링크 수정 스크립트")
    print("=" * 80)
    print()

    processed = 0
    updated = 0
    total_issues = 0

    for post_file in post_files:
        if not post_file.exists():
            print(f"⚠️  File not found: {post_file}")
            continue

        processed += 1
        result = process_post_file(post_file, fix_mode=args.fix, dry_run=args.dry_run)

        if result["issues"]:
            print(f"📄 {post_file.name}")
            for issue in result["issues"]:
                print(f"  ⚠️  {issue}")
                total_issues += 1

        if result["fixed"]:
            updated += 1
            status = "[DRY-RUN] " if args.dry_run else ""
            print(f"{status}✅ 수정: {post_file.name}")

    print()
    print("=" * 80)
    print(f"처리 완료: {processed}개 파일")
    if args.fix:
        print(f"수정됨: {updated}개 파일")
    if args.check:
        print(f"발견된 문제: {total_issues}개")
    print("=" * 80)


if __name__ == "__main__":
    main()
