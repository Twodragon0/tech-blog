#!/usr/bin/env python3
"""Remove the boilerplate blocks that ``autonomous_post_modernizer.py`` injected.

The modernizer appended three fixed blocks to published posts:

1. ``### 아키텍처 및 워크플로우 다이어그램`` + one of three hardcoded Mermaid
   diagrams, chosen by a title keyword. The diagram does not describe the
   post's architecture, so the heading asserts evidence the post lacks.
2. ``## 실무 적용 및 운영 체크리스트 (Actionable Checklist)`` + four
   byte-identical checkbox items. On digests this duplicated the canonical
   ``## 실무 체크리스트`` section and, because the heading string is not the
   canonical one, it slipped past ``check_digest_checklist_heading.py``.
3. ``### 핵심 구성 및 보안 통제 항목 비교`` + a fabricated control table.

Each block was inserted as an exact literal, so removing that same literal
restores the pre-modernizer body byte-for-byte (trailing whitespace excepted,
which the modernizer itself normalised via ``rstrip()``).

The script refuses to guess: if a post carries one of the headings but the
body underneath is not the known literal, it aborts rather than deleting
hand-authored content.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

DIAGRAM_HEADING = "### 아키텍처 및 워크플로우 다이어그램"
CHECKLIST_HEADING = "## 실무 적용 및 운영 체크리스트 (Actionable Checklist)"
TABLE_HEADING = "### 핵심 구성 및 보안 통제 항목 비교"

# The three Mermaid diagrams the modernizer could emit, verbatim.
_MERMAID_K8S = (
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

_MERMAID_CLOUD = (
    "```mermaid\n"
    "flowchart LR\n"
    "    User([External Client]) --> WAF[AWS WAF / CloudFront]\n"
    "    WAF --> ALB[Application Load Balancer]\n"
    "    ALB --> ECS[Compute: ECS / EKS Cluster]\n"
    "    ECS --> DB[(Encrypted Aurora / DynamoDB)]\n"
    "    ECS -.-> CW[CloudWatch & GuardDuty Alerts]\n"
    "```\n"
)

_MERMAID_GENERIC = (
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

_CHECKLIST_ITEMS = (
    "- [ ] 운영 환경 보안 정책 및 권한 최소화(Least Privilege) 검증\n"
    "- [ ] CI/CD 파이프라인 정적 분석 및 시크릿 유출 차단 룰 적용\n"
    "- [ ] 이상 징후 및 에러 모니터링 경보(Sentry/CloudWatch) 연동 확인\n"
    "- [ ] 장애 발생 시 롤백 및 긴급 복구 런북 최신화\n"
)

_TABLE_BODY = (
    "| 통제 영역 | 주요 기능 | 점검 주기 | 담당 역할 |\n"
    "|---|---|---|---|\n"
    "| **인증/인가** | IAM 역할 및 세션 토큰 제한 | 상시 모니터링 | DevSecOps |\n"
    "| **네트워크** | WAF 규칙 및 보안 그룹 감사 | 주간 | Cloud Ops |\n"
    "| **데이터 보호** | KMS 암호화 및 무결성 검증 | 실시간 | SecOps |\n"
    "\n"
)

# (label, exact literal as it appears on disk)
BOILERPLATE_BLOCKS: List[Tuple[str, str]] = [
    (f"diagram:{name}", f"\n{DIAGRAM_HEADING}\n\n{body}\n")
    for name, body in (
        ("k8s", _MERMAID_K8S),
        ("cloud", _MERMAID_CLOUD),
        ("generic", _MERMAID_GENERIC),
    )
] + [
    ("checklist", f"\n{CHECKLIST_HEADING}\n\n{_CHECKLIST_ITEMS}"),
    ("table", f"\n{TABLE_HEADING}\n\n{_TABLE_BODY}"),
]

# Heading -> the block labels that legitimately explain that heading. Used to
# prove no heading is left behind unexplained.
_HEADING_OWNERS = {
    DIAGRAM_HEADING: ("diagram:k8s", "diagram:cloud", "diagram:generic"),
    CHECKLIST_HEADING: ("checklist",),
    TABLE_HEADING: ("table",),
}


def strip_boilerplate(text: str) -> Tuple[str, Dict[str, int]]:
    """Remove every known boilerplate literal. Returns (new_text, counts)."""
    counts: Dict[str, int] = {}
    for label, block in BOILERPLATE_BLOCKS:
        n = text.count(block)
        if n:
            counts[label] = n
            text = text.replace(block, "")
    return text, counts


def unexplained_headings(text: str, counts: Dict[str, int]) -> List[str]:
    """Headings still present after removal — i.e. bodies we did not recognise."""
    leftovers = []
    for heading, owners in _HEADING_OWNERS.items():
        if heading in text:
            removed = sum(counts.get(o, 0) for o in owners)
            leftovers.append(f"{heading!r} still present (removed {removed} block(s))")
    return leftovers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="write changes (default: dry run)"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="specific posts to process (default: every post)",
    )
    args = parser.parse_args()

    targets = args.paths or sorted(POSTS_DIR.glob("*.md"))
    totals: Dict[str, int] = {}
    changed: List[Tuple[Path, Dict[str, int]]] = []
    aborts: List[str] = []

    for path in targets:
        original = path.read_text(encoding="utf-8")
        stripped, counts = strip_boilerplate(original)
        if not counts:
            continue

        leftovers = unexplained_headings(stripped, counts)
        if leftovers:
            aborts.append(f"{path.name}: " + "; ".join(leftovers))
            continue

        changed.append((path, counts))
        for label, n in counts.items():
            totals[label] = totals.get(label, 0) + n
        if args.apply:
            path.write_text(stripped, encoding="utf-8")

    for path, counts in changed:
        detail = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"{'REMOVED' if args.apply else 'WOULD REMOVE'}  {path.name}  {detail}")

    if aborts:
        print(
            "\nABORTED — a heading survived removal, so its body is not the known "
            "literal and may be hand-authored. Inspect before deleting:",
            file=sys.stderr,
        )
        for line in aborts:
            print(f"  {line}", file=sys.stderr)

    print(
        f"\n[remove-modernizer-boilerplate] {len(changed)} post(s) "
        f"{'changed' if args.apply else 'would change'}; "
        f"blocks: {totals or '{}'}; aborts: {len(aborts)}"
    )
    return 1 if aborts else 0


if __name__ == "__main__":
    sys.exit(main())
