#!/usr/bin/env python3
"""
SVG 텍스트 노드 밀도 최적화 스크립트
목표: text 노드를 10개 이하로 줄이기

변환 전략:
1. footer: "Weekly Digest" text 노드 제거
2. glow2 필터 2줄 타이틀 → 첫 번째 줄에 두 번째 내용 합침 (공백)
3. THREAT SIGNAL MAP + subtitle → tspan 합침
4. g 내부 코드/숫자 장식용 text 노드 제거 (라인번호, 코드 하이라이팅)
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ASSETS_DIR = Path("/Users/yong/Desktop/tech-blog/assets/images")
SVG_NS = "http://www.w3.org/2000/svg"

ET.register_namespace("", SVG_NS)


def count_text_nodes_str(svg_text: str) -> int:
    """SVG 문자열에서 text 노드 수 반환."""
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError:
        return -1
    return len(root.findall(f".//{{{SVG_NS}}}text"))


def has_korean(text: str) -> bool:
    return bool(re.search(r"[\uac00-\ud7a3]", text))


# ---------------------------------------------------------------------------
# 변환 함수들 (regex 기반, SVG 포맷팅 보존)
# ---------------------------------------------------------------------------

def remove_weekly_digest_footer(content: str) -> str:
    """footer의 'Weekly Digest' text 노드 한 줄 제거."""
    # <text ... text-anchor="end">Weekly Digest</text>
    return re.sub(
        r'\n[ \t]*<text[^>]*text-anchor="end"[^>]*>Weekly Digest</text>',
        "",
        content,
    )


def merge_glow2_two_line_title(content: str) -> str:
    """
    glow2 필터가 붙은 연속 2개 <text> 노드를 1개로 합침.
    두 번째 줄 내용을 첫 번째 text 내용에 공백으로 이어붙임.
    예: "Cloud Security Course 7Batch 4Week: AWS" + "Vulnerabi..." → 합침
    """
    pattern = (
        r'(<text(?=[^>]*filter="url\(#glow2\)")[^>]*>)'   # group 1: 첫 번째 여는 태그
        r'([^<]+)'                                          # group 2: 첫 번째 텍스트
        r'(</text>)'                                        # group 3: 닫는 태그
        r'(\s*\n\s*)'                                       # group 4: 공백/줄바꿈
        r'(?:<text(?=[^>]*filter="url\(#glow2\)")[^>]*>)'  # 두 번째 여는 태그 (버림)
        r'([^<]+)'                                          # group 5: 두 번째 텍스트
        r'(?:</text>)'                                      # 두 번째 닫는 태그 (버림)
    )

    def replacer(m):
        open_tag = m.group(1)
        text1 = m.group(2).rstrip()
        text2 = m.group(5).strip()
        # text1 끝의 "-", ":", 공백 처리
        combined = f"{text1} {text2}".strip()
        return f"{open_tag}{combined}</text>"

    return re.sub(pattern, replacer, content)


def merge_threat_signal_subtitle(content: str) -> str:
    """
    THREAT SIGNAL MAP 헤더(y=90) + subtitle(y=120) 두 text 노드를 tspan으로 합침.
    """
    pattern = (
        r'(<text )((?:[^>]*? )?)y="90"([^>]*?)>(THREAT SIGNAL MAP)(</text>)'
        r'(\s*\n\s*)'
        r'<text ((?:[^>]*? )?)x="(\d+)"((?:[^>]*? )?)y="120"([^>]*?)>'
        r'([^<]+)'
        r'</text>'
    )

    def replacer(m):
        pre = m.group(1) + m.group(2)
        post_attrs = m.group(3)
        sub_x = m.group(8)
        subtitle = m.group(11).strip()
        return (
            f"{pre}y=\"90\"{post_attrs}>"
            f"<tspan>THREAT SIGNAL MAP</tspan>"
            f"<tspan x=\"{sub_x}\" dy=\"30\">{subtitle}</tspan>"
            f"</text>"
        )

    return re.sub(pattern, replacer, content)


def remove_decorative_code_texts(content: str) -> str:
    """
    장식용 코드 에디터 내부 text 노드 제거:
    - 라인 번호: fill="#64748b" 이고 내용이 숫자만인 것
    - 코드 내용: x가 음수인 text 노드들 (에디터 내부)
    """
    # 라인 번호 (숫자만, fill="#64748b")
    content = re.sub(
        r'\s*<text [^>]*fill="#64748b"[^>]*>\d+</text>',
        "",
        content,
    )
    # x가 음수인 코드 내용 text들 (장식용 코드 에디터)
    content = re.sub(
        r'\s*<text x="-\d+[^>]*>[^<]*</text>',
        "",
        content,
    )
    return content


def remove_inner_g_texts(content: str) -> str:
    """
    <g font-family="Courier New" ...> ... </g> 블록 전체를 제거.
    코드 에디터 내부의 코드 라인 그룹.
    """
    return re.sub(
        r'\s*<g[^>]*font-family="Courier New"[^>]*>.*?</g>',
        "",
        content,
        flags=re.DOTALL,
    )


def merge_glow_two_line_title(content: str) -> str:
    """
    filter="url(#glow)" (glow2 아님) 연속 2개 <text> 노드를 1개로 합침.
    패턴 B 커스텀 SVG의 30px 2줄 타이틀.
    """
    pattern = (
        r'(<text(?=[^>]*filter="url\(#glow\)")[^>]*>)'   # group 1: 첫 번째 여는 태그
        r'([^<]+)'                                         # group 2: 첫 번째 텍스트
        r'(</text>)'                                       # group 3
        r'(\s*\n\s*)'                                      # group 4: 공백
        r'(?:<text(?=[^>]*filter="url\(#glow\)")[^>]*>)'  # 두 번째 여는 태그 (버림)
        r'([^<]+)'                                         # group 5: 두 번째 텍스트
        r'(?:</text>)'                                     # 두 번째 닫는 태그 (버림)
    )

    def replacer(m):
        open_tag = m.group(1)
        text1 = m.group(2).rstrip()
        text2 = m.group(5).strip()
        combined = f"{text1} {text2}".strip()
        return f"{open_tag}{combined}</text>"

    return re.sub(pattern, replacer, content)


def remove_courier_small_sublabels(content: str) -> str:
    """
    Courier New font-size="8" 또는 font-size="9" 인 서브라벨 text 노드 제거.
    파이프라인 다이어그램의 'git push', 'docker build' 등 소형 설명 텍스트.
    """
    return re.sub(
        r'\s*<text [^>]*font-family="Courier New"[^>]*font-size="[89]"[^>]*>[^<]+</text>',
        "",
        content,
    )


def remove_duplicate_circle_labels(content: str) -> str:
    """
    THREAT SIGNAL MAP 다이어그램에서 원 레이블이 중복된 경우 제거.
    subtitle tspan에 이미 포함된 키워드와 동일한 circle label text 노드 삭제.
    예: tspan에 'K8S  DEVOPS  ZERO DAY' 있으면, 개별 'K8S', 'DEVOPS', 'ZERO DAY' text 제거.

    구체적으로: font-size="15" text-anchor="middle" 인 circle label +
                font-size="14" text-anchor="middle" 인 CVE label +
                font-size="9"  text-anchor="middle" 인 0-DAY label 제거
    (이 속성 조합은 THREAT SIGNAL MAP 다이어그램 특유의 원 레이블)
    """
    # font-size 15 원 레이블 (K8S, DEVOPS, ZERO DAY, AI/ML, PHISH 등)
    content = re.sub(
        r'\s*<text [^>]*font-size="15"[^>]*text-anchor="middle"[^>]*>[^<]+</text>',
        "",
        content,
    )
    # font-size 14 원 레이블 (CVE 등)
    content = re.sub(
        r'\s*<text [^>]*font-size="14"[^>]*text-anchor="middle"[^>]*>[^<]+</text>',
        "",
        content,
    )
    # font-size 9 원 레이블 (0-DAY 등)
    content = re.sub(
        r'\s*<text [^>]*font-size="9"[^>]*text-anchor="middle"[^>]*>[^<]+</text>',
        "",
        content,
    )
    return content


# ---------------------------------------------------------------------------
# 메인 최적화 로직
# ---------------------------------------------------------------------------

def optimize_svg(filepath: Path) -> tuple[int, int, str]:
    """
    SVG 파일 최적화.
    반환: (before_count, after_count, status)
    status: 'optimized' | 'partial:N' | 'skipped_already_ok' |
            'skipped_korean' | 'skipped_no_improvement' | 'error:msg'
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return -1, -1, f"error:{e}"

    before = count_text_nodes_str(content)
    if before < 0:
        return -1, -1, "error:parse_failed"
    if before <= 10:
        return before, before, "skipped_already_ok"
    if has_korean(content):
        return before, before, "skipped_korean"

    modified = content

    # 단계별 변환 적용
    modified = remove_weekly_digest_footer(modified)
    modified = merge_glow2_two_line_title(modified)
    modified = merge_glow_two_line_title(modified)
    modified = merge_threat_signal_subtitle(modified)

    after = count_text_nodes_str(modified)

    # 아직 10개 초과면 Courier New 소형 서브라벨 제거
    if after > 10:
        modified2 = remove_courier_small_sublabels(modified)
        after2 = count_text_nodes_str(modified2)
        if after2 < after:
            modified = modified2
            after = after2

    # 아직 10개 초과면 THREAT SIGNAL MAP 원 중복 레이블 제거
    if after > 10:
        modified2 = remove_duplicate_circle_labels(modified)
        after2 = count_text_nodes_str(modified2)
        if after2 < after:
            modified = modified2
            after = after2

    # 아직 10개 초과면 장식용 코드 텍스트 제거 시도
    if after > 10:
        modified2 = remove_decorative_code_texts(modified)
        after2 = count_text_nodes_str(modified2)
        if after2 < after:
            modified = modified2
            after = after2

    # 여전히 초과면 Courier New g 블록 전체 제거 시도
    if after > 10:
        modified2 = remove_inner_g_texts(modified)
        after2 = count_text_nodes_str(modified2)
        if after2 < after:
            modified = modified2
            after = after2

    # 개선 없으면 원본 유지
    if after >= before:
        return before, before, "skipped_no_improvement"

    # XML 유효성 검증
    try:
        ET.fromstring(modified)
    except ET.ParseError as e:
        return before, before, f"skipped_invalid_xml:{e}"

    filepath.write_text(modified, encoding="utf-8")

    if after <= 10:
        return before, after, "optimized"
    else:
        return before, after, f"partial:{after}"


# ---------------------------------------------------------------------------
# 실행 진입점
# ---------------------------------------------------------------------------

def main():
    print("SVG 텍스트 노드 밀도 최적화")
    print("=" * 65)

    svg_files = sorted(ASSETS_DIR.glob("*.svg"))

    counts = {
        "optimized": 0,
        "partial": 0,
        "no_improvement": 0,
        "korean": 0,
        "already_ok": 0,
        "error": 0,
    }
    detail_lines = []

    for svg_file in svg_files:
        before, after, status = optimize_svg(svg_file)

        if status == "skipped_already_ok":
            counts["already_ok"] += 1
            continue
        if status == "skipped_korean":
            counts["korean"] += 1
            continue

        name = svg_file.name[:68]

        if status == "optimized":
            counts["optimized"] += 1
            detail_lines.append(f"  OK  {before:2d}→{after:2d}  {name}")
        elif status.startswith("partial:"):
            counts["partial"] += 1
            detail_lines.append(f"  ~   {before:2d}→{after:2d}  {name}  [목표 미달]")
        elif status == "skipped_no_improvement":
            counts["no_improvement"] += 1
            detail_lines.append(f"  --  {before:2d}    {name}  [변환 불가]")
        elif status.startswith("error") or status.startswith("skipped_invalid"):
            counts["error"] += 1
            detail_lines.append(f"  !!  {before:2d}    {name}  [{status}]")

    for line in detail_lines:
        print(line)

    print()
    print("=" * 65)
    print(f"최적화 완료 (10 이하)  : {counts['optimized']:3d}개")
    print(f"부분 개선 (10 초과)    : {counts['partial']:3d}개")
    print(f"변환 불가              : {counts['no_improvement']:3d}개")
    print(f"한글 포함 (건너뜀)     : {counts['korean']:3d}개")
    print(f"이미 OK (10 이하)      : {counts['already_ok']:3d}개")
    print(f"오류                   : {counts['error']:3d}개")


if __name__ == "__main__":
    main()
