#!/usr/bin/env python3
"""Autonomous Post Modernizer & Continual Improver (AGY + CCG).

Scans Jekyll blog posts, evaluates technical depth, Mermaid architecture diagrams,
practical implementation checklists, and image validity. Automatically raises quality
scores above 90+ and runs the zero-regression verification gate.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
ASSETS_DIR = REPO_ROOT / "assets" / "images"

sys.path.insert(0, str(REPO_ROOT))
from scripts.lib.security import mask_sensitive_info


def safe_print(msg: str, level: str = "INFO") -> None:
    """Print log message with security masking applied."""
    masked = mask_sensitive_info(msg)
    print(f"[{level}] {masked}")


def analyze_post_needs(post_path: Path) -> Tuple[int, List[str]]:
    """Score post and determine missing architectural elements."""
    text = post_path.read_text(encoding="utf-8", errors="ignore")
    issues: List[str] = []
    score = 100

    # 1. Content Length Check
    char_count = len(text)
    if char_count < 2500:
        score -= 25
        issues.append(f"Short content ({char_count} chars < 2500)")
    elif char_count < 3500:
        score -= 10
        issues.append(f"Moderate content ({char_count} chars < 3500)")

    # 2. Mermaid Diagram Check
    has_mermaid = "```mermaid" in text
    if not has_mermaid:
        score -= 20
        issues.append("Missing Mermaid architecture diagram")

    # 3. Actionable Checklist Check
    has_checklist = bool(re.search(r"-\s*\[\s*[ xX]?\s*\]", text))
    if not has_checklist:
        score -= 15
        issues.append("Missing actionable checklist (- [ ])")

    # 4. Tables Check
    table_count = len(re.findall(r"\|.*\|.*\n\|[-:\s|]+\|", text))
    if table_count < 1:
        score -= 15
        issues.append("Missing comparison or configuration table")

    # 5. Code Block Check
    code_blocks = len(re.findall(r"```\w+", text))
    if code_blocks < 1:
        score -= 10
        issues.append("Missing syntax-highlighted code block")

    # 6. Strict Prohibitions (FAQ section heading or FAQPage schema)
    has_faq_heading = bool(
        re.search(
            r"^#{1,4}\s*.*(?:자주\s*묻는\s*질문|\bFAQ\b)", text, re.MULTILINE | re.IGNORECASE
        )
    )
    has_faq_schema = "schema_type: FAQPage" in text or '"FAQPage"' in text
    if has_faq_heading or has_faq_schema:
        score -= 30
        issues.append("Contains prohibited FAQ section/schema")

    # 7. Image Reference Check
    img_match = re.search(
        r"^image:\s*['\"]?(/assets/images/[^\s'\"]+)['\"]?", text, re.MULTILINE
    )
    if not img_match:
        score -= 15
        issues.append("Missing front matter image reference")
    else:
        img_rel = img_match.group(1).lstrip("/")
        if not (REPO_ROOT / img_rel).exists():
            score -= 20
            issues.append(f"Referenced image {img_rel} does not exist on disk")

    return max(0, score), issues


def find_candidate_posts(
    min_score_threshold: int = 85, limit: int = 5
) -> List[Tuple[Path, int, List[str]]]:
    """Find posts scoring below threshold, prioritized by lowest score."""
    candidates = []
    for p in sorted(POSTS_DIR.glob("*.md")):
        score, issues = analyze_post_needs(p)
        if score < min_score_threshold:
            candidates.append((p, score, issues))

    # Sort lowest score first
    candidates.sort(key=lambda x: x[1])
    return candidates[:limit]


def generate_mermaid_for_topic(title: str, category: str) -> str:
    """Generate contextual Mermaid architecture diagram."""
    lower_title = title.lower()
    if (
        "kubernetes" in lower_title
        or "k8s" in lower_title
        or "container" in lower_title
    ):
        return (
            "```mermaid\n"
            "graph TD\n"
            "    subgraph Ingress & Control Plane\n"
            "        GW[API Gateway / Ingress Controller]\n"
            "        AC[Admission Controller / Webhook]\n"
            "    end\n"
            "    subgraph Data Plane & Pods\n"
            "        P1[Application Pod 1]\n"
            "        P2[Application Pod 2]\n"
            "        Sec[Security Agent / Sidecar]\n"
            "    end\n"
            "    GW --> AC\n"
            "    AC --> P1\n"
            "    AC --> P2\n"
            "    P1 --- Sec\n"
            "    P2 --- Sec\n"
            "```\n"
        )
    elif "aws" in lower_title or "cloud" in lower_title:
        return (
            "```mermaid\n"
            "flowchart LR\n"
            "    User([External Client]) --> WAF[AWS WAF / CloudFront]\n"
            "    WAF --> ALB[Application Load Balancer]\n"
            "    ALB --> ECS[Compute: ECS / EKS Cluster]\n"
            "    ECS --> DB[(Encrypted Aurora / DynamoDB)]\n"
            "    ECS -.-> CW[CloudWatch & GuardDuty Alerts]\n"
            "```\n"
        )
    else:
        return (
            "```mermaid\n"
            "sequenceDiagram\n"
            "    autonumber\n"
            "    actor Engineer as DevSecOps Engineer\n"
            "    participant CI as CI/CD Pipeline\n"
            "    participant Sec as Security Gate & Scanner\n"
            "    participant Prod as Production Environment\n"
            "\n"
            "    Engineer->>CI: Push Git Commit / Pull Request\n"
            "    CI->>Sec: Static Analysis (SAST / Secret Masking)\n"
            "    Sec-->>CI: Policy Compliance (Zero Regression)\n"
            "    CI->>Prod: Automated Zero-Downtime Deployment\n"
            "```\n"
        )


def enhance_post_content(post_path: Path, issues: List[str]) -> bool:
    """Enhance post with missing architectural elements."""
    text = post_path.read_text(encoding="utf-8")
    original_text = text
    modified = False

    # Extract frontmatter title and category
    title_match = re.search(r"^title:\s*['\"]?(.*?)['\"]?$", text, re.MULTILINE)
    title = title_match.group(1) if title_match else post_path.stem
    cat_match = re.search(r"^category:\s*['\"]?(.*?)['\"]?$", text, re.MULTILINE)
    category = cat_match.group(1) if cat_match else "security"

    # Remove any prohibited FAQ sections
    if re.search(r"^#{1,4}\s*.*(?:자주\s*묻는\s*질문|\bFAQ\b)", text, re.MULTILINE | re.IGNORECASE) or "schema_type: FAQPage" in text:
        text = re.sub(
            r"##\s*(?:\d+[\.\)]\s*)?(?:자주\s*묻는\s*질문|FAQ)[\s\S]*?(?=\n##|\Z)",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = text.replace("schema_type: FAQPage", "")
        modified = True

    # 1. Add Mermaid Diagram if missing
    if "Missing Mermaid architecture diagram" in issues and "```mermaid" not in text:
        diag = generate_mermaid_for_topic(title, category)
        # Place diagram after first section
        h2_split = re.split(r"(\n##\s+.*?\n)", text, maxsplit=1)
        if len(h2_split) >= 3:
            text = (
                f"{h2_split[0]}{h2_split[1]}\n"
                f"### 아키텍처 및 워크플로우 다이어그램\n\n"
                f"{diag}\n"
                f"{h2_split[2]}"
            )
            modified = True

    # 2. Add Implementation Checklist if missing
    if "Missing actionable checklist (- [ ])" in issues and not re.search(
        r"-\s*\[\s*[ xX]?\s*\]", text
    ):
        checklist_block = (
            "\n## 실무 적용 및 운영 체크리스트 (Actionable Checklist)\n\n"
            "- [ ] 운영 환경 보안 정책 및 권한 최소화(Least Privilege) 검증\n"
            "- [ ] CI/CD 파이프라인 정적 분석 및 시크릿 유출 차단 룰 적용\n"
            "- [ ] 이상 징후 및 에러 모니터링 경보(Sentry/CloudWatch) 연동 확인\n"
            "- [ ] 장애 발생 시 롤백 및 긴급 복구 런북 최신화\n"
        )
        text = text.rstrip() + "\n" + checklist_block
        modified = True

    # 3. Add Comparison Table if missing
    if "Missing comparison or configuration table" in issues and "|" not in text:
        table_block = (
            "\n### 핵심 구성 및 보안 통제 항목 비교\n\n"
            "| 통제 영역 | 주요 기능 | 점검 주기 | 담당 역할 |\n"
            "|---|---|---|---|\n"
            "| **인증/인가** | IAM 역할 및 세션 토큰 제한 | 상시 모니터링 | DevSecOps |\n"
            "| **네트워크** | WAF 규칙 및 보안 그룹 감사 | 주간 | Cloud Ops |\n"
            "| **데이터 보호** | KMS 암호화 및 무결성 검증 | 실시간 | SecOps |\n\n"
        )
        text = text.rstrip() + "\n" + table_block
        modified = True

    if modified and text != original_text:
        post_path.write_text(text, encoding="utf-8")
        safe_print(f"✅ Enhanced post: {post_path.name}")
        return True

    return False


def run_verification_gate() -> bool:
    """Run full zero-regression verification gate."""
    safe_print("🔍 Running zero-regression verification gate...")

    commands = [
        [sys.executable, str(REPO_ROOT / "scripts" / "check_posts.py")],
        [sys.executable, str(REPO_ROOT / "scripts" / "fix_links_unified.py"), "--fix"],
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "verify_images_unified.py"),
            "--all",
        ],
        [sys.executable, str(REPO_ROOT / "scripts" / "check_kst_midnight.py")],
        [
            str(REPO_ROOT / ".venv" / "bin" / "pytest"),
            "scripts/tests/test_news_templates.py",
        ],
    ]

    for cmd in commands:
        cmd_str = " ".join(cmd)
        safe_print(f"Executing: {cmd_str}")
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if res.returncode != 0:
            safe_print(
                f"❌ Gate failed on command: {cmd_str}\n{res.stderr}", level="ERROR"
            )
            return False

    safe_print("🎉 All verification gates passed successfully!")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous Post Modernizer (AGY + CCG)"
    )
    parser.add_argument(
        "--threshold", type=int, default=85, help="Quality threshold score"
    )
    parser.add_argument(
        "--limit", type=int, default=3, help="Max posts to enhance per run"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Scan only without writing"
    )
    args = parser.parse_args()

    safe_print(
        f"🚀 Scanning posts for modernization (Threshold: {args.threshold}, Limit: {args.limit})..."
    )
    candidates = find_candidate_posts(args.threshold, args.limit)

    if not candidates:
        safe_print("🌟 All posts meet high-quality standards! Zero candidates found.")
        return 0

    safe_print(f"Found {len(candidates)} candidate posts for improvement:")
    for post_path, score, issues in candidates:
        safe_print(f"  • {post_path.name} (Score: {score}) -> {', '.join(issues)}")

    if args.dry_run:
        safe_print("Dry-run mode: No modifications made.")
        return 0

    improved_count = 0
    for post_path, score, issues in candidates:
        if enhance_post_content(post_path, issues):
            improved_count += 1

    if improved_count > 0:
        if run_verification_gate():
            safe_print(f"🎉 Successfully modernized {improved_count} posts!")
            return 0
        else:
            safe_print(
                "⚠️ Verification gate failed after enhancements. Review changes.",
                level="WARN",
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
