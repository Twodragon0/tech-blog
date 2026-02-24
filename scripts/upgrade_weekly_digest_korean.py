#!/usr/bin/env python3

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"


def collect_sections(lines):
    sections = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            start = i
            j = i + 1
            while (
                j < len(lines)
                and not lines[j].startswith("### ")
                and not lines[j].startswith("## ")
            ):
                j += 1
            sections.append((start, j))
            i = j
            continue
        i += 1
    return sections


def first_text_block(sec_lines):
    buf = []
    for ln in sec_lines:
        s = ln.strip()
        if not s:
            if buf:
                break
            continue
        if (
            s.startswith(">")
            or s.startswith("####")
            or s.startswith("**핵심 포인트")
            or s.startswith("-")
        ):
            if buf:
                break
            continue
        if s.startswith("```"):
            break
        buf.append(s)
    return " ".join(buf)


def summarize_from_title(title, hint):
    t = re.sub(r"\s+", " ", title).strip()

    keywords = {
        "취약점": "취약점 영향 범위와 우선 패치 대상을 신속히 식별해야 합니다",
        "CVE": "CVE 영향도와 완화 조치를 기준으로 대응 우선순위를 정해야 합니다",
        "RCE": "원격 코드 실행 가능성에 대비해 탐지 룰과 차단 정책을 강화해야 합니다",
        "AI": "AI 도입 시 모델 거버넌스와 데이터 보호 기준을 함께 수립해야 합니다",
        "Cloud": "클라우드 운영에서는 권한·네트워크·로그 정책을 함께 점검해야 합니다",
        "Kubernetes": "쿠버네티스 환경에서는 워크로드 격리와 이미지 무결성 검증이 중요합니다",
        "Docker": "컨테이너 운영에서는 베이스 이미지 보안과 런타임 제어를 강화해야 합니다",
        "Supply Chain": "공급망 리스크를 줄이기 위해 의존성 검증과 배포 무결성 점검이 필요합니다",
    }

    action = "실무 적용 전 영향 범위, 운영 리스크, 검증 절차를 동시에 점검해야 합니다"
    for k, v in keywords.items():
        if k.lower() in t.lower():
            action = v
            break

    return f"이번 항목은 최신 기술 동향과 현업 적용 포인트를 간결히 정리한 내용입니다. {action}."


def to_bullets(summary):
    parts = [p.strip(" .") for p in re.split(r"[.!?]\s+", summary) if p.strip()]
    if len(parts) < 2:
        parts = [summary, "실무 적용 시 영향 범위와 우선순위를 함께 점검해야 합니다"]
    return [f"- {parts[0]}", f"- {parts[1]}"]


def rewrite_file(path):
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    sections = collect_sections(lines)
    if not sections:
        return False

    rows = []
    for n, (s, e) in enumerate(sections, start=1):
        title = lines[s].replace("###", "", 1).strip()
        hint = first_text_block(lines[s + 1 : e])
        rows.append((n, title, hint[:240]))

    batch = {idx: summarize_from_title(title, hint) for idx, title, hint in rows}

    new_lines = lines[:]
    offset = 0
    for n, (s, e) in enumerate(sections, start=1):
        s2 = s + offset
        e2 = e + offset
        sec = new_lines[s2:e2]
        summary = batch.get(n)
        if not summary:
            continue

        source_idx = None
        key_idx = None
        for i, ln in enumerate(sec):
            if ln.strip().startswith("> **출처**:") and source_idx is None:
                source_idx = i
            if ln.strip().startswith("**핵심 포인트") and key_idx is None:
                key_idx = i

        if source_idx is None:
            continue

        intro_start = 1
        while intro_start < source_idx and sec[intro_start].strip().startswith("> 🔴"):
            intro_start += 1

        head = sec[:intro_start]
        tail_start = source_idx
        rebuilt = head + ["", summary, ""] + sec[tail_start:]

        if key_idx is not None:
            k = None
            for i, ln in enumerate(rebuilt):
                if ln.strip().startswith("**핵심 포인트"):
                    k = i
                    break
            if k is not None:
                b_start = k + 1
                while b_start < len(rebuilt) and rebuilt[b_start].strip() == "":
                    b_start += 1
                b_end = b_start
                while b_end < len(rebuilt) and rebuilt[b_end].strip().startswith("-"):
                    b_end += 1
                bullets = to_bullets(summary)
                rebuilt = rebuilt[:b_start] + bullets + rebuilt[b_end:]

        delta = len(rebuilt) - len(sec)
        new_lines[s2:e2] = rebuilt
        offset += delta

    updated = "\n".join(new_lines)
    if updated != original:
        path.write_text(
            updated + ("\n" if original.endswith("\n") else ""), encoding="utf-8"
        )
        return True
    return False


def main():
    files = sorted(POSTS_DIR.glob("*Weekly_Digest*.md"))
    changed = 0
    for f in files:
        try:
            if rewrite_file(f):
                changed += 1
        except Exception:
            continue
    print(f"weekly_digest_korean_upgraded={changed} total={len(files)}")


if __name__ == "__main__":
    main()
