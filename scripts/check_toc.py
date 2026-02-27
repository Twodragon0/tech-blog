#!/usr/bin/env python3
"""
통합 목차 검증 스크립트
모든 포스팅의 목차 구조를 확인하고 검증합니다.

사용법:
    python3 scripts/check_toc.py              # 기본 검증 (요약)
    python3 scripts/check_toc.py --detailed   # 상세 검증
    python3 scripts/check_toc.py --verify     # ID 매핑 검증
    python3 scripts/check_toc.py --file <파일명>  # 특정 파일 상세 분석
    python3 scripts/check_toc.py --all        # 모든 검증 실행
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# 이모지 패턴
EMOJI_PATTERN = r"[📅🌐🤖📋📝🔧✅🔐💡📊🚀]"
# 굵은 글씨 패턴
BOLD_PATTERN = r"\*\*"


def clean_title(title):
    """헤더 제목에서 이모지와 굵은 글씨 제거"""
    cleaned = re.sub(BOLD_PATTERN, "", title)
    cleaned = re.sub(EMOJI_PATTERN, "", cleaned)
    return cleaned.strip()


def generate_id_from_text(text):
    """헤더 텍스트에서 ID 생성 (Jekyll/kramdown 방식과 유사)"""
    if not text:
        return ""

    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    # 이모지 제거
    text = re.sub(EMOJI_PATTERN, "", text)
    # 굵은 글씨 제거
    text = re.sub(BOLD_PATTERN, "", text)

    # 소문자 변환 및 공백을 하이픈으로
    id_text = text.strip().lower()
    id_text = re.sub(r"[\s_]+", "-", id_text)

    # 특수 문자 제거 (한글은 유지)
    id_text = re.sub(r"[^\w\u3131-\u318E\uAC00-\uD7A3-]", "", id_text)

    # 앞뒤 하이픈 제거
    id_text = re.sub(r"^-+|-+$", "", id_text)

    # 숫자로 시작하면 prefix 추가
    if not id_text or re.match(r"^\d", id_text):
        id_text = "heading-" + id_text

    return id_text


def extract_headers(file_path):
    """포스팅에서 모든 헤더 추출"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        headers = []
        for i, line in enumerate(content.split("\n"), 1):
            # H2
            if line.startswith("## ") and not line.startswith("###"):
                title = line[3:].strip()
                clean_title_text = clean_title(title)
                headers.append(
                    {
                        "level": 2,
                        "line": i,
                        "title": clean_title_text,
                        "original": title,
                        "expected_id": generate_id_from_text(clean_title_text),
                    }
                )
            # H3
            elif line.startswith("### ") and not line.startswith("####"):
                title = line[4:].strip()
                clean_title_text = clean_title(title)
                headers.append(
                    {
                        "level": 3,
                        "line": i,
                        "title": clean_title_text,
                        "original": title,
                        "expected_id": generate_id_from_text(clean_title_text),
                    }
                )
            # H4
            elif line.startswith("#### "):
                title = line[5:].strip()
                headers.append(
                    {
                        "level": 4,
                        "line": i,
                        "title": clean_title(title),
                        "original": title,
                    }
                )

        return headers
    except Exception:
        return []


def analyze_post(file_path):
    """포스팅의 목차 구조 분석"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Front matter 확인
        has_toc = "toc: true" in content or "toc: True" in content

        # 헤더 추출
        headers = extract_headers(file_path)
        h2_headers = [h for h in headers if h["level"] == 2]
        h3_headers = [h for h in headers if h["level"] == 3]
        h4_headers = [h for h in headers if h["level"] == 4]

        # 주요 섹션 패턴 (숫자로 시작하거나 주요 키워드 포함)
        main_section_patterns = [
            r"^\d+\.",  # "1. ", "2. " 등
            r"서론|결론|개요|소개|시작",
        ]

        # H3로 시작하는 주요 섹션 찾기
        main_sections_as_h3 = []
        for h3 in h3_headers:
            for pattern in main_section_patterns:
                if re.search(pattern, h3["title"]):
                    main_sections_as_h3.append(h3)
                    break

        return {
            "file": file_path.name,
            "has_toc": has_toc,
            "h2_count": len(h2_headers),
            "h3_count": len(h3_headers),
            "h4_count": len(h4_headers),
            "h2_headers": h2_headers,
            "h3_headers": h3_headers,
            "main_sections_as_h3": main_sections_as_h3,
            "needs_attention": len(main_sections_as_h3) > 0 and len(h2_headers) < 5,
            "toc_will_show": len(h2_headers) > 0,
            "is_good": len(h2_headers) >= 3 and len(main_sections_as_h3) == 0,
        }
    except Exception as e:
        return {"error": str(e)}


def print_summary(results):
    """요약 정보 출력"""
    stats = defaultdict(int)
    for result in results:
        if "error" in result:
            continue
        stats["total"] += 1
        if result["has_toc"]:
            stats["with_toc"] += 1
            if result["is_good"]:
                stats["good"] += 1
            elif result["needs_attention"]:
                stats["needs_attention"] += 1
            elif result["h2_count"] < 3:
                stats["low_h2"] += 1
            elif result["h2_count"] == 0:
                stats["no_h2"] += 1

    print("=" * 80)
    print("목차 구조 검증 요약")
    print("=" * 80)
    print(f"\n전체 포스팅 수: {stats['total']}")
    print(f"목차 활성화된 포스팅: {stats['with_toc']}")
    print(f"✅ 구조가 좋은 포스팅: {stats['good']}개")
    print(f"⚠️  주의가 필요한 포스팅: {stats['needs_attention']}개")
    print(f"⚠️  H2가 적은 포스팅 (1-2개): {stats['low_h2']}개")
    print(f"❌ H2가 없는 포스팅: {stats['no_h2']}개")
    print("=" * 80)


def print_detailed(results):
    """상세 정보 출력"""
    needs_attention = [r for r in results if r.get("needs_attention")]
    low_h2 = [
        r
        for r in results
        if r.get("has_toc") and r["h2_count"] < 3 and r["h2_count"] > 0
    ]
    no_h2 = [r for r in results if r.get("has_toc") and r["h2_count"] == 0]

    if needs_attention:
        print("\n" + "=" * 80)
        print("주의가 필요한 포스팅:")
        print("=" * 80)
        for result in needs_attention:
            print(f"\n📄 {result['file']}")
            print(f"   H2 헤더: {result['h2_count']}개")
            print(f"   H3 헤더: {result['h3_count']}개")
            if result["main_sections_as_h3"]:
                print(
                    f"   ⚠️  주요 섹션이 H3로 되어 있음: {len(result['main_sections_as_h3'])}개"
                )
                for section in result["main_sections_as_h3"][:3]:
                    print(f"      - {section['title']}")

    if low_h2:
        print("\n" + "=" * 80)
        print("H2가 적은 포스팅 (목차에 표시될 항목이 적음):")
        print("=" * 80)
        for result in low_h2[:10]:
            print(
                f"  - {result['file']}: H2 {result['h2_count']}개, H3 {result['h3_count']}개"
            )

    if no_h2:
        print("\n" + "=" * 80)
        print("⚠️  H2가 없는 포스팅 (목차에 아무것도 표시되지 않음):")
        print("=" * 80)
        for result in no_h2:
            print(f"  - {result['file']}")


def print_verify(results):
    """ID 매핑 검증 출력"""
    good_toc = [r for r in results if r.get("toc_will_show") and r["h2_count"] >= 3]
    low_h2 = [
        r
        for r in results
        if r.get("toc_will_show") and r["h2_count"] < 3 and r["h2_count"] > 0
    ]
    no_h2 = [r for r in results if r.get("toc_will_show") and r["h2_count"] == 0]

    print("=" * 80)
    print("목차 매핑 검증 결과")
    print("=" * 80)
    print(f"\n목차 활성화된 포스팅: {len([r for r in results if r.get('has_toc')])}개")
    print(f"✅ 목차가 잘 구성된 포스팅 (H2 3개 이상): {len(good_toc)}개")
    print(f"⚠️  H2가 적은 포스팅 (H2 1-2개): {len(low_h2)}개")
    print(f"❌ H2가 없는 포스팅: {len(no_h2)}개")

    if low_h2:
        print("\n" + "=" * 80)
        print("H2가 적은 포스팅:")
        print("=" * 80)
        for result in low_h2[:5]:
            print(f"  - {result['file']}: H2 {result['h2_count']}개")
            for h2 in result["h2_headers"]:
                print(f"    • {h2['title']}")

    if no_h2:
        print("\n" + "=" * 80)
        print("⚠️  H2가 없는 포스팅:")
        print("=" * 80)
        for result in no_h2:
            print(f"  - {result['file']}")

    print("\n" + "=" * 80)
    print("✅ 목차 시스템 동작 방식:")
    print("=" * 80)
    print("1. Jekyll이 마크다운을 HTML로 변환할 때 헤더에 자동으로 ID를 생성합니다")
    print(
        "2. 목차 시스템은 렌더링된 HTML에서 <h2 id='...'> 태그를 찾아 목차를 생성합니다"
    )
    print("3. H2 (##)는 메인 목차로, H3 (###)는 하위 목차로 표시됩니다")
    print("4. 헤더에 ID가 있어야 목차 링크가 작동합니다")
    print("=" * 80)


def print_file_detail(results, filename):
    """특정 파일 상세 분석 출력"""
    target_result = next((r for r in results if r["file"] == filename), None)

    if not target_result:
        print(f"❌ 파일을 찾을 수 없습니다: {filename}")
        return

    if "error" in target_result:
        print(f"❌ 오류: {target_result['error']}")
        return

    print("=" * 80)
    print(f"📄 {filename} 상세 분석")
    print("=" * 80)
    print(f"\n목차 활성화: {'✅' if target_result['has_toc'] else '❌'}")
    print(f"H2 헤더: {target_result['h2_count']}개")
    print(f"H3 헤더: {target_result['h3_count']}개")
    print(f"H4 헤더: {target_result['h4_count']}개")

    if target_result["h2_headers"]:
        print(f"\n목차에 표시될 H2 섹션 ({len(target_result['h2_headers'])}개):")
        for i, h2 in enumerate(target_result["h2_headers"], 1):
            print(f"  {i}. {h2['title']}")
            print(f"     예상 ID: {h2['expected_id']}")
            print(f"     라인: {h2['line']}")

    if target_result["main_sections_as_h3"]:
        print(
            f"\n⚠️  주요 섹션이 H3로 되어 있음 ({len(target_result['main_sections_as_h3'])}개):"
        )
        for section in target_result["main_sections_as_h3"]:
            print(f"  - {section['title']} (라인 {section['line']})")

    if target_result["h3_headers"]:
        print(f"\n하위 목차로 표시될 H3 섹션 ({len(target_result['h3_headers'])}개):")
        for h3 in target_result["h3_headers"][:10]:  # 최대 10개만
            print(f"  - {h3['title']} (라인 {h3['line']})")

    print("\n" + "=" * 80)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="포스팅 목차 구조 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python3 scripts/check_toc.py                    # 기본 검증
  python3 scripts/check_toc.py --detailed          # 상세 검증
  python3 scripts/check_toc.py --verify            # ID 매핑 검증
  python3 scripts/check_toc.py --file <파일명>      # 특정 파일 분석
  python3 scripts/check_toc.py --all                # 모든 검증 실행
        """,
    )
    parser.add_argument("--detailed", action="store_true", help="상세 검증 실행")
    parser.add_argument("--verify", action="store_true", help="ID 매핑 검증 실행")
    parser.add_argument("--file", type=str, help="특정 파일 상세 분석")
    parser.add_argument("--all", action="store_true", help="모든 검증 실행")

    args = parser.parse_args()

    posts_dir = Path(__file__).parent.parent / "_posts"

    if not posts_dir.exists():
        print(f"❌ Posts directory not found: {posts_dir}")
        return 1

    # 모든 포스팅 분석
    results = []
    for md_file in sorted(posts_dir.glob("*.md")):
        result = analyze_post(md_file)
        if result:
            results.append(result)

    # 특정 파일 분석
    if args.file:
        print_file_detail(results, args.file)
        return 0

    # 모든 검증 실행
    if args.all:
        print_summary(results)
        print_detailed(results)
        print_verify(results)
        return 0

    # 기본 검증
    if not args.detailed and not args.verify:
        print_summary(results)
        return 0

    # 상세 검증
    if args.detailed:
        print_summary(results)
        print_detailed(results)

    # ID 매핑 검증
    if args.verify:
        print_verify(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
