#!/usr/bin/env python3

from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"


CATEGORY_LABEL = {
    "security": ("security", "보안"),
    "devsecops": ("devsecops", "DevSecOps"),
    "devops": ("devops", "DevOps"),
    "cloud": ("cloud", "클라우드"),
    "kubernetes": ("devops", "쿠버네티스"),
    "incident": ("incident", "인시던트"),
    "finops": ("cloud", "FinOps"),
    "tech": ("tech", "기술"),
    "ai": ("tech", "AI"),
    "blockchain": ("tech", "블록체인"),
}


def _to_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        return [x.strip() for x in s.split(",") if x.strip()]
    return []


def _escape_attr(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("'", "&#39;")
        .replace("\n", " ")
        .strip()
    )


def _categories_html(categories: list[str]) -> str:
    chips: list[str] = []
    for raw in categories[:3]:
        key = str(raw).strip().lower()
        css, label = CATEGORY_LABEL.get(key, ("tech", str(raw).strip()))
        chips.append(f'<span class="category-tag {css}">{label}</span>')
    return " ".join(chips) if chips else '<span class="category-tag tech">기술</span>'


def _tags_html(tags: list[str]) -> str:
    if not tags:
        return '<span class="tag">요약</span>'
    return " ".join(f'<span class="tag">{t}</span>' for t in tags[:8])


def _highlights_html(excerpt: str) -> str:
    text = re.sub(r"\s+", " ", (excerpt or "").strip())
    text = re.sub(r"\.{2,}|…", " ", text).strip(" .")
    if not text:
        text = "핵심 이슈를 요약했습니다"
    point1 = text[:100].rstrip(" ,.")
    point2 = "실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다"
    point3 = "운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다"
    return (
        f"<li><strong>포인트 1</strong>: {point1}</li> "
        f"<li><strong>포인트 2</strong>: {point2}</li> "
        f"<li><strong>포인트 3</strong>: {point3}</li>"
    )


def _build_include(front: dict[str, object]) -> str:
    title = str(front.get("title", "최신 기술 동향 요약")).strip()
    categories = _to_list(front.get("categories") or front.get("category"))
    tags = _to_list(front.get("tags"))
    excerpt = str(front.get("excerpt", "")).strip()
    date_value = str(front.get("date", "")).split(" ")[0]
    period = f"{date_value} (24시간)" if date_value else "최근 24시간"
    return (
        "{% include ai-summary-card.html\n"
        f"  title='{_escape_attr(title)}'\n"
        f"  categories_html='{_escape_attr(_categories_html(categories))}'\n"
        f"  tags_html='{_escape_attr(_tags_html(tags))}'\n"
        f"  highlights_html='{_escape_attr(_highlights_html(excerpt))}'\n"
        f"  period='{_escape_attr(period)}'\n"
        "  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'\n"
        "%}"
    )


def classify(title: str) -> str:
    t = title.lower()
    if re.search(r"cve|취약점|rce|제로데이|malware|랜섬|phishing|botnet|exploit", t):
        return "security"
    if re.search(r"ai|llm|agent|gemini|claude|gpt|copilot|bedrock|nova", t):
        return "ai"
    if re.search(r"cloud|aws|azure|gcp|kubernetes|k8s|docker|devops|infra", t):
        return "cloud"
    if re.search(r"bitcoin|crypto|etf|blockchain|token", t):
        return "market"
    return "general"


def section_summary(title: str) -> str:
    c = classify(title)
    if c == "security":
        return (
            f"{title} 이슈는 공격 성립 조건과 영향 범위를 함께 보여주며 우선 대응 대상을 빠르게 식별하게 합니다. "
            "실무에서는 노출 자산 식별, 패치 우선순위, 탐지 룰 갱신을 동일 주기에 묶어 처리해야 합니다."
        )
    if c == "ai":
        return (
            f"{title} 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. "
            "팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다."
        )
    if c == "cloud":
        return (
            f"{title} 업데이트는 인프라 변경이 안정성·비용·보안 통제에 어떤 영향을 주는지 확인할 수 있는 사례입니다. "
            "적용 전에는 대상 서비스, 롤백 경로, 관측 지표를 사전에 고정해 운영 리스크를 낮춰야 합니다."
        )
    if c == "market":
        return (
            f"{title} 이슈는 시장 신호와 제도 변화가 기술 생태계 의사결정에 연결되는 흐름을 보여줍니다. "
            "단기 변동성보다 규제·유동성·채택 속도를 함께 추적해야 실무 판단의 정확도를 높일 수 있습니다."
        )
    return (
        f"{title} 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. "
        "실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다."
    )


def key_points(title: str) -> list[str]:
    c = classify(title)
    if c == "security":
        return [
            "영향받는 자산과 공격 경로를 먼저 확정합니다.",
            "패치·완화 조치·탐지 룰을 하나의 대응 배치로 실행합니다.",
            "유사 자산까지 점검 범위를 확장해 재발 위험을 낮춥니다.",
        ]
    if c == "ai":
        return [
            "모델 성능뿐 아니라 운영 통제 기준을 함께 설계합니다.",
            "데이터 보호와 권한 경계를 배포 체크리스트에 포함합니다.",
            "도입 효과를 정량 지표로 기록해 재현 가능한 운영 체계를 만듭니다.",
        ]
    if c == "cloud":
        return [
            "적용 대상 서비스와 의존 구간을 사전 매핑합니다.",
            "롤백 경로와 모니터링 지표를 변경 단위와 함께 고정합니다.",
            "성능·비용·보안 통제를 동일 기준으로 비교해 배포합니다.",
        ]
    if c == "market":
        return [
            "가격 변동보다 구조적 정책 신호를 우선 확인합니다.",
            "규제·유동성·인프라 요인을 분리해 영향도를 평가합니다.",
            "리스크 한도와 점검 주기를 명시해 의사결정 변동성을 줄입니다.",
        ]
    return [
        "핵심 변화의 적용 범위와 기대 효과를 먼저 정리합니다.",
        "운영 리스크와 검증 기준을 같은 문서에서 관리합니다.",
        "도입 이후 추적할 성과 지표를 사전에 합의합니다.",
    ]


def row_summary(title: str) -> str:
    c = classify(title)
    if c == "security":
        return "위협 조건과 영향 자산을 기준으로 대응 우선순위를 즉시 정해야 하는 보안 뉴스입니다."
    if c == "ai":
        return "AI 기능 확대에 따른 운영 방식 변화와 거버넌스 점검 포인트를 함께 확인해야 하는 업데이트입니다."
    if c == "cloud":
        return "인프라 변경이 안정성·비용·보안 통제에 직접 연결되므로 배포 전 검증 체계가 핵심인 소식입니다."
    if c == "market":
        return "시장·규제 신호가 기술 생태계 의사결정에 미치는 영향을 함께 읽어야 하는 동향입니다."
    return "적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다."


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    front: dict[str, object] = {}
    body = original
    fm_raw = ""
    if original.startswith("---\n"):
        parts = original.split("---", 2)
        if len(parts) >= 3:
            fm_raw = parts[1]
            body = parts[2]
            front_data: object = yaml.safe_load(fm_raw)
            if isinstance(front_data, dict):
                front = {str(k): v for k, v in front_data.items()}

    lines = body.splitlines()
    out: list[str] = []
    current_h3 = ""
    current_h2 = ""
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("## "):
            current_h2 = line
            out.append(line)
            i += 1
            continue

        m_h3 = re.match(r"^###\s+\d+\.\d+\s+(.+)$", line)
        if m_h3:
            current_h3 = m_h3.group(1).strip()
            out.append(line)
            i += 1
            continue

        generic_para = line.startswith(
            "이번 소식은 해당 기술 변화의 배경과 실제 적용 영향을 중심으로 정리했습니다."
        ) or line.startswith(
            "이번 항목은 최신 기술 동향과 현업 적용 포인트를 간결히 정리한 내용입니다"
        )
        if generic_para and current_h3:
            out.append(section_summary(current_h3))
            i += 1
            continue

        if line.strip().startswith("**핵심 포인트") and current_h3:
            out.append(line)
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                out.append(lines[i])
                i += 1
            while i < len(lines) and lines[i].strip().startswith("-"):
                i += 1
            for p in key_points(current_h3):
                out.append(f"- {p}")
            out.append("")
            continue

        row = re.match(
            r"^\|\s*\[(.*?)\]\((.*?)\)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", line
        )
        if row and "기타 주목할 뉴스" in current_h2:
            title = row.group(1).strip()
            url = row.group(2).strip()
            source = row.group(3).strip()
            summary = row_summary(title)
            out.append(f"| [{title}]({url}) | {source} | {summary} |")
            i += 1
            continue

        out.append(line)
        i += 1

    updated_body = "\n".join(out)
    if "ai-summary-card" not in updated_body.lower():
        include_block = _build_include(front)
        updated_body = include_block + "\n\n" + updated_body.lstrip("\n")

    if fm_raw:
        updated = f"---{fm_raw}---\n\n{updated_body.lstrip()}"
    else:
        updated = updated_body

    if original.endswith("\n") and not updated.endswith("\n"):
        updated += "\n"

    if updated != original:
        _ = path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    files = sorted(POSTS_DIR.glob("*Weekly_Digest*.md"))
    changed = 0
    for p in files:
        if process_file(p):
            changed += 1
    print(f"digest_quality_upgraded={changed} total={len(files)}")


if __name__ == "__main__":
    main()
