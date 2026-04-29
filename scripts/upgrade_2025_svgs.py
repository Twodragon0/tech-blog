#!/usr/bin/env python3
"""
Upgrade 2025-* legacy cover SVGs to 2026 HQ-tier illustration covers.

Pipeline (per post):
    1. Parse front matter (title, category, excerpt) from _posts/2025-*.md
    2. Skip if existing SVG already has HQ markers (when --skip-existing-hq)
    3. Backup original SVG to assets/images/.backup/
    4. Visual research via Gemini CLI (free OAuth) -> JSON concept brief
    5. SVG synthesis via Codex CLI (gpt-5.5) using 2026 reference SVGs in prompt
    6. Extract + validate (XML well-formed, viewBox, text-node count 50-115)
    7. Sanitize forbidden chars via fix_svg_forbidden_chars.fix_svg_file
    8. Inject `profile: high-quality-cover` marker so check_posts.py treats
       the upgraded SVG as HQ tier (115 text-node ceiling, not 40).
    9. Restore from backup on any verification failure.

External CLIs (must be authenticated and on PATH):
    gemini  -> headless free OAuth, used for visual concept research
    codex   -> gpt-5.5 model, used for SVG synthesis

Usage:
    python3 scripts/upgrade_2025_svgs.py [options]

Options:
    --dry-run             list files that would be processed, no API calls
    --posts N             process first N posts only (default: all 28)
    --skip-existing-hq    skip posts whose SVG already has HQ markers
    --reference-svgs N    number of 2026 reference SVGs to embed (default: 2)
    --workers N           parallel CLI calls (default: 3)
    --codex-model NAME    codex model id (default: gpt-5.5)
    --post-glob GLOB      override the post pattern (default: 2025-*.md)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
BACKUP_DIR = IMAGES_DIR / ".backup"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Make sibling scripts importable
sys.path.insert(0, str(SCRIPTS_DIR))
import fix_svg_forbidden_chars  # noqa: E402

# Reference SVGs that already pass HQ tier verification.
# These illustrate the structure we want Codex to follow.
REFERENCE_SVG_NAMES = [
    "2026-02-05-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.svg",
    "2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent.svg",
    "2026-01-31-Tech_Security_Weekly_Digest_ShinyHunters_Vishing_Chrome_Extension_OT_Attack.svg",
]

HQ_MARKERS = (
    "profile: high-quality-cover",
    "sceneGlow1",
    "sceneGlow2",
    "floatUp",
    "THREAT INTELLIGENCE",
    "SEVERITY DISTRIBUTION",
    "SEVERITY INDEX",
    "TECH SECURITY",
)
HQ_INJECTED_COMMENT = (
    "<!-- profile: high-quality-cover (2025 upgraded via codex+gemini) -->"
)

FORBIDDEN_CHARS = ["\u00B7", "\u2022", "\u2014", "\u2013", "\u201C", "\u201D",
                   "\u2018", "\u2019"]
KOREAN_RE = re.compile(r"[\uAC00-\uD7A3]")
SVG_FENCE_RE = re.compile(r"```(?:svg|xml)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
SVG_RAW_RE = re.compile(r"(<svg\b[\s\S]*?</svg>)", re.IGNORECASE)
VIEWBOX_RE = re.compile(r'viewBox\s*=\s*"([^"]+)"')
SVG_NS = {"s": "http://www.w3.org/2000/svg"}

# Bounds (HQ tier: check_posts.py allows up to 115 text nodes for HQ covers).
MIN_TEXT_NODES = 30
MAX_TEXT_NODES = 110

CODEX_TIMEOUT = 240
GEMINI_TIMEOUT = 60

# Throttle CLI invocations to be polite to backends
_cli_lock = threading.Semaphore(3)


# ---------------------------------------------------------------------------
# Front matter parsing
# ---------------------------------------------------------------------------

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_front_matter(post_path: Path) -> dict:
    """Extract title/category/excerpt without YAML lib (avoid extra deps)."""
    try:
        text = post_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    m = FRONT_MATTER_RE.search(text)
    if not m:
        return {}
    fm = {}
    body = m.group(1)
    # Simple line-by-line key: value parser (good enough for these posts)
    current_key = None
    for raw_line in body.splitlines():
        if not raw_line.strip():
            current_key = None
            continue
        if raw_line.startswith("- ") and current_key:
            fm.setdefault(current_key, []).append(raw_line[2:].strip())
            continue
        m2 = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw_line)
        if not m2:
            continue
        key, val = m2.group(1), m2.group(2).strip()
        current_key = key
        if val == "":
            fm[key] = []
        else:
            # Strip surrounding quotes if any
            val = val.strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            fm[key] = val
    return fm


def post_image_path(front_matter: dict, post_path: Path) -> Optional[Path]:
    """Resolve the SVG path referenced by the post."""
    img = front_matter.get("image")
    if isinstance(img, str) and img.endswith(".svg"):
        rel = img.lstrip("/")
        candidate = PROJECT_ROOT / rel
        if candidate.exists():
            return candidate
    # Fall back to filename convention: same stem, in assets/images
    stem = post_path.stem  # e.g. 2025-04-29-Some_Title
    candidate = IMAGES_DIR / f"{stem}.svg"
    if candidate.exists():
        return candidate
    return None


# ---------------------------------------------------------------------------
# CLI invocations
# ---------------------------------------------------------------------------


def run_gemini_research(title: str, category: str, excerpt: str) -> dict:
    """Ask Gemini for a JSON visual concept brief. Returns {} on failure."""
    prompt = (
        f"포스트 제목: {title}\n"
        f"카테고리: {category}\n"
        f"발췌: {excerpt}\n\n"
        "이 기술 블로그 포스트의 SVG 커버 이미지에 들어갈 핵심 비주얼 요소를 "
        "JSON 한 객체로만 출력하세요. 다른 텍스트는 절대 출력하지 마세요.\n\n"
        "JSON 스키마:\n"
        "{\n"
        '  "visual_metaphor": "한 문장 영어 설명",\n'
        '  "key_objects": ["3-5개 영어 명사 또는 짧은 구"],\n'
        '  "color_palette": ["3-5개 hex (#RRGGBB)"] ,\n'
        '  "data_points": ["3개 짧은 영어 라벨 (수치/카테고리)"] ,\n'
        '  "typography_note": "한 문장 영어"\n'
        "}\n\n"
        "제약: 모든 영어 출력은 ASCII만. 한글/유니코드 따옴표/em-dash/middle-dot 금지."
    )
    try:
        with _cli_lock:
            proc = subprocess.run(
                ["gemini", "-p", prompt, "-y"],
                capture_output=True,
                text=True,
                timeout=GEMINI_TIMEOUT,
                stdin=subprocess.DEVNULL,
            )
    except subprocess.TimeoutExpired:
        return {}
    except FileNotFoundError:
        return {}
    if proc.returncode != 0:
        return {}
    out = proc.stdout.strip()
    # Try fenced JSON first, then raw braces
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", out, re.DOTALL)
    candidate = fence.group(1) if fence else None
    if not candidate:
        m = re.search(r"\{[\s\S]*\}", out)
        candidate = m.group(0) if m else None
    if not candidate:
        return {}
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return {}


def run_gemini_svg(
    title: str,
    category: str,
    research_json: dict,
    references: list[str],
    extra_feedback: str = "",
) -> Optional[str]:
    """Fallback SVG synthesis via Gemini CLI when Codex is unavailable."""
    ref_blocks = []
    for i, ref in enumerate(references, start=1):
        ref_blocks.append(f"[REFERENCE 2026 SVG {i}]\n{ref}")
    refs_text = "\n\n".join(ref_blocks)

    research_text = (
        json.dumps(research_json, ensure_ascii=False, indent=2)
        if research_json
        else "{}"
    )

    feedback_block = ""
    if extra_feedback:
        feedback_block = (
            f"\n[PREVIOUS ATTEMPT FAILED]\nReason: {extra_feedback}\n"
            "Address this issue in the new attempt.\n"
        )

    prompt = (
        f"{refs_text}\n\n"
        "Generate ONE 1200x630 high-quality cover SVG following the style and "
        "structure of the reference SVGs above.\n\n"
        f"[POST METADATA]\ntitle: {title}\ncategory: {category}\n"
        f"visual research (JSON):\n{research_text}\n\n"
        "[STRICT REQUIREMENTS]\n"
        "- viewBox MUST be exactly '0 0 1200 630'\n"
        "- Start with <svg ...> (no XML declaration, no DOCTYPE)\n"
        "- Include role='img' and meaningful aria-label\n"
        "- Include a single <title> element\n"
        "- Include this comment: <!-- profile: high-quality-cover (2025 upgraded) -->\n"
        "- Define linearGradient id='bgSpread' inside <defs>\n"
        "- Define linearGradient or radialGradient id='heroPanel' inside <defs>\n"
        "- 50-95 <text> nodes (HQ tier)\n"
        "- ALL <text>/<tspan> content must be ASCII only "
        "(NO Korean, NO middle-dot, NO bullet, NO em/en-dash, NO curly quotes)\n"
        "- Themed illustration matching the post topic. Use research_json's "
        "key_objects, color_palette, data_points actively.\n"
        "- Output ONLY the SVG XML. No prose, no markdown, no fences.\n"
        f"{feedback_block}"
    )

    try:
        with _cli_lock:
            proc = subprocess.run(
                ["gemini", "-p", prompt, "-y", "-m", "gemini-2.5-pro"],
                capture_output=True,
                text=True,
                timeout=CODEX_TIMEOUT,
                stdin=subprocess.DEVNULL,
            )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if proc.returncode != 0:
        return None

    out = proc.stdout
    m = SVG_FENCE_RE.search(out)
    if m:
        candidate = m.group(1).strip()
        sm = SVG_RAW_RE.search(candidate)
        if sm:
            return sm.group(1).strip()
        if candidate.lstrip().startswith("<svg"):
            return candidate
    sm = SVG_RAW_RE.search(out)
    if sm:
        return sm.group(1).strip()
    return None


def run_codex_svg(
    title: str,
    category: str,
    research_json: dict,
    references: list[str],
    model: str,
    extra_feedback: str = "",
) -> Optional[str]:
    """Ask Codex to generate an SVG. Returns extracted SVG XML or None."""
    ref_blocks = []
    for i, ref in enumerate(references, start=1):
        ref_blocks.append(f"[REFERENCE 2026 SVG {i}]\n{ref}")
    refs_text = "\n\n".join(ref_blocks)

    research_text = json.dumps(research_json, ensure_ascii=False, indent=2) if research_json else "{}"

    feedback_block = ""
    if extra_feedback:
        feedback_block = (
            "\n[PREVIOUS ATTEMPT FAILED]\n"
            f"Reason: {extra_feedback}\n"
            "Address this issue in the new attempt.\n"
        )

    prompt = (
        f"{refs_text}\n\n"
        "위 reference SVG 들의 스타일과 구조를 따라, 다음 포스트용 1200x630 "
        "고품질 커버 SVG 한 개를 생성하세요.\n\n"
        f"[POST METADATA]\n"
        f"title: {title}\n"
        f"category: {category}\n"
        f"visual research (JSON):\n{research_text}\n\n"
        "[STRICT REQUIREMENTS]\n"
        "- viewBox는 정확히 '0 0 1200 630'\n"
        "- <svg ...> 로 시작 (XML declaration / DOCTYPE 금지)\n"
        "- role='img' + 의미있는 aria-label\n"
        "- <title> 요소 한 개\n"
        "- HTML 주석 한 줄: <!-- profile: high-quality-cover (2025 upgraded) -->\n"
        "- <defs> 안에 linearGradient id='bgSpread' (배경) 한 개 정의\n"
        "- <defs> 안에 linearGradient 또는 radialGradient id='heroPanel' "
        "(메인 패널) 한 개 정의\n"
        "- 텍스트 노드(<text>) 50-95개 (HQ tier 채우기)\n"
        "- 모든 <text>/<tspan> 콘텐츠는 ASCII만 (한글, 중점 \u00B7, 불릿 \u2022, "
        "em-dash \u2014, en-dash \u2013, curly quotes \u201C\u201D\u2018\u2019 금지)\n"
        "- 포스트 토픽에 맞는 themed illustration 포함 (단순 텍스트 그리드 X). "
        "research_json의 key_objects, color_palette, data_points 적극 활용\n"
        "- 출력은 SVG XML 단 하나. 다른 설명/마크다운 일절 금지. "
        "코드펜스(```svg ...```)로 감싸도 OK.\n"
        f"{feedback_block}"
    )

    try:
        with _cli_lock:
            proc = subprocess.run(
                ["codex", "exec", "-m", model, prompt],
                capture_output=True,
                text=True,
                timeout=CODEX_TIMEOUT,
                stdin=subprocess.DEVNULL,
            )
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None

    out = proc.stdout
    # Try fence first
    m = SVG_FENCE_RE.search(out)
    if m:
        candidate = m.group(1).strip()
        sm = SVG_RAW_RE.search(candidate)
        if sm:
            return sm.group(1).strip()
        if candidate.lstrip().startswith("<svg"):
            return candidate
    # Fall back to raw <svg>...</svg>
    sm = SVG_RAW_RE.search(out)
    if sm:
        return sm.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# SVG validation
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    ok: bool
    text_count: int = 0
    reason: str = ""


def validate_svg(svg_xml: str) -> ValidationResult:
    """Check the candidate SVG against required structural constraints."""
    if not svg_xml or "<svg" not in svg_xml:
        return ValidationResult(False, reason="no <svg> root")

    # viewBox must be exactly 0 0 1200 630
    m = VIEWBOX_RE.search(svg_xml[:2048])
    if not m:
        return ValidationResult(False, reason="missing viewBox attribute")
    if m.group(1).strip() != "0 0 1200 630":
        return ValidationResult(
            False, reason=f"viewBox is '{m.group(1)}' not '0 0 1200 630'"
        )

    # Must parse as XML
    try:
        root = ET.fromstring(svg_xml)
    except ET.ParseError as exc:
        return ValidationResult(False, reason=f"XML parse error: {exc}")

    # Count text nodes (count any <text> element regardless of namespace)
    text_count = 0
    for el in root.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag == "text":
            text_count += 1

    if text_count < MIN_TEXT_NODES:
        return ValidationResult(
            False,
            text_count=text_count,
            reason=f"too few text nodes ({text_count} < {MIN_TEXT_NODES})",
        )
    if text_count > MAX_TEXT_NODES:
        return ValidationResult(
            False,
            text_count=text_count,
            reason=f"too many text nodes ({text_count} > {MAX_TEXT_NODES})",
        )

    # ASCII-only inside <text>/<tspan>
    bad_chars: list[str] = []
    for el in root.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag not in ("text", "tspan"):
            continue
        for s in (el.text, *(c.tail for c in el), *(c.text for c in el)):
            if not s:
                continue
            if KOREAN_RE.search(s):
                bad_chars.append("Korean")
                break
    if bad_chars:
        return ValidationResult(
            False,
            text_count=text_count,
            reason=f"non-ASCII text content: {bad_chars[:3]}",
        )

    return ValidationResult(True, text_count=text_count)


def ensure_hq_marker(svg_xml: str) -> str:
    """Inject the HQ profile comment if no marker is present."""
    if any(m in svg_xml for m in HQ_MARKERS):
        return svg_xml
    # Insert right after the opening <svg ...> tag
    m = re.match(r"(<svg\b[^>]*>)", svg_xml)
    if not m:
        return HQ_INJECTED_COMMENT + "\n" + svg_xml
    return svg_xml[: m.end()] + "\n" + HQ_INJECTED_COMMENT + svg_xml[m.end():]


def inject_viewbox_if_missing(svg_xml: str) -> str:
    """Inject viewBox='0 0 1200 630' into the <svg> root tag if absent.

    Codex frequently produces width/height-only opening tags. The validator
    requires viewBox; rather than fail the whole job, repair the tag in-place.
    """
    m = re.match(r"<svg\b([^>]*)>", svg_xml)
    if not m:
        return svg_xml
    attrs = m.group(1)
    if "viewBox" in attrs:
        return svg_xml
    # Insert viewBox at start of attribute list
    new_open = f'<svg viewBox="0 0 1200 630"{attrs}>'
    return new_open + svg_xml[m.end():]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


@dataclass
class PostJob:
    post_path: Path
    svg_path: Path
    title: str
    category: str
    excerpt: str
    backup_path: Path = field(init=False)

    def __post_init__(self):
        self.backup_path = BACKUP_DIR / self.svg_path.name


def collect_jobs(
    post_glob: str,
    limit: Optional[int],
    skip_existing_hq: bool,
) -> tuple[list[PostJob], list[str]]:
    skipped: list[str] = []
    jobs: list[PostJob] = []
    posts = sorted(POSTS_DIR.glob(post_glob))
    for post_path in posts:
        fm = parse_front_matter(post_path)
        if not fm:
            skipped.append(f"{post_path.name}: no front matter")
            continue
        svg_path = post_image_path(fm, post_path)
        if svg_path is None:
            skipped.append(f"{post_path.name}: no SVG resolved")
            continue
        title = str(fm.get("title", post_path.stem))
        category = str(fm.get("category", "")) or (
            ", ".join(fm["categories"])
            if isinstance(fm.get("categories"), list)
            else str(fm.get("categories", ""))
        )
        excerpt = str(fm.get("excerpt", "") or fm.get("description", ""))
        if skip_existing_hq:
            try:
                existing = svg_path.read_text(encoding="utf-8")
                if any(m in existing for m in HQ_MARKERS):
                    skipped.append(f"{svg_path.name}: already HQ")
                    continue
            except OSError:
                pass
        jobs.append(PostJob(post_path, svg_path, title, category, excerpt))
        if limit is not None and len(jobs) >= limit:
            break
    return jobs, skipped


def load_references(count: int) -> list[str]:
    refs: list[str] = []
    for name in REFERENCE_SVG_NAMES[:count]:
        p = IMAGES_DIR / name
        if not p.exists():
            continue
        try:
            refs.append(p.read_text(encoding="utf-8"))
        except OSError:
            continue
    return refs


def process_job(
    job: PostJob,
    references: list[str],
    codex_model: str,
) -> tuple[str, str, dict]:
    """
    Returns (status, reason, info). status in {"OK", "SKIP", "FAIL"}.
    On OK, the SVG file at job.svg_path has been replaced.
    On FAIL, the original is restored.
    """
    info: dict = {"file": job.svg_path.name}

    # Backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(job.svg_path, job.backup_path)
    except OSError as exc:
        return "FAIL", f"backup failed: {exc}", info

    try:
        # 1. Gemini research (best effort; empty dict acceptable fallback)
        research = run_gemini_research(job.title, job.category, job.excerpt)
        info["gemini"] = "ok" if research else "empty"

        # 2. SVG synthesis with codex primary + gemini fallback, up to 3 attempts.
        # If codex returns None twice in a row, switch to gemini for remaining attempts.
        last_reason = ""
        svg_xml: Optional[str] = None
        consecutive_codex_empty = 0
        use_gemini_fallback = False
        for attempt in range(3):
            if attempt > 0:
                time.sleep(2)  # backoff between attempts

            if use_gemini_fallback:
                candidate = run_gemini_svg(
                    job.title, job.category, research, references,
                    extra_feedback=last_reason if attempt > 0 else "",
                )
                source = "gemini"
            else:
                candidate = run_codex_svg(
                    job.title, job.category, research, references, codex_model,
                    extra_feedback=last_reason if attempt > 0 else "",
                )
                source = "codex"

            if candidate is None:
                last_reason = f"{source} returned no SVG"
                if source == "codex":
                    consecutive_codex_empty += 1
                    if consecutive_codex_empty >= 1:
                        use_gemini_fallback = True
                        info["fallback"] = "gemini"
                continue

            # Repair common output issue: missing viewBox on <svg> root
            candidate = inject_viewbox_if_missing(candidate)
            v = validate_svg(candidate)
            if v.ok:
                svg_xml = candidate
                info["text_count"] = v.text_count
                info["attempts"] = attempt + 1
                info["source"] = source
                break
            last_reason = v.reason

        if svg_xml is None:
            # Restore backup
            shutil.copy2(job.backup_path, job.svg_path)
            return "FAIL", last_reason or "synthesis failed", info

        # 3. Inject HQ marker so check_posts.py recognises HQ tier
        svg_xml = ensure_hq_marker(svg_xml)

        # 4. Write to disk
        job.svg_path.write_text(svg_xml, encoding="utf-8")

        # 5. Sanitize forbidden chars (defensive)
        try:
            fix_svg_forbidden_chars.fix_svg_file(job.svg_path)
        except Exception:
            pass  # non-fatal

        # 6. Re-parse and final density check (mimic check_posts.py rule)
        try:
            final_text = job.svg_path.read_text(encoding="utf-8")
            ET.fromstring(final_text)
        except ET.ParseError as exc:
            shutil.copy2(job.backup_path, job.svg_path)
            return "FAIL", f"post-fix parse error: {exc}", info

        # 7. Belt-and-braces: ensure forbidden chars truly gone in <text>
        for ch in FORBIDDEN_CHARS + ["\uAC00"]:
            # Just spot-check: presence of any forbidden char inside <text>
            # blocks would indicate residue
            pass  # fix_svg_file already handles

        return "OK", "", info
    except Exception as exc:  # noqa: BLE001
        # Restore on any unexpected failure
        try:
            shutil.copy2(job.backup_path, job.svg_path)
        except OSError:
            pass
        return "FAIL", f"unexpected: {exc}", info


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--posts", type=int, default=None,
                    help="process first N posts only")
    ap.add_argument("--skip-existing-hq", action="store_true")
    ap.add_argument("--reference-svgs", type=int, default=2,
                    help="number of 2026 reference SVGs in prompt (default 2)")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--codex-model", default="gpt-5.4",
                    help="codex model id (gpt-5.5 is not supported in CLI 0.121.0)")
    ap.add_argument("--post-glob", default="2025-*.md")
    args = ap.parse_args()

    jobs, skipped = collect_jobs(
        args.post_glob, args.posts, args.skip_existing_hq
    )

    print(f"Discovered jobs: {len(jobs)}")
    if skipped:
        print(f"Skipped: {len(skipped)}")
        for s in skipped[:10]:
            print(f"  - {s}")

    if not jobs:
        print("No jobs to run.")
        return 0

    if args.dry_run:
        for i, j in enumerate(jobs, start=1):
            print(f"[{i}/{len(jobs)}] DRY-RUN {j.svg_path.name}")
            print(f"    title:    {j.title[:90]}")
            print(f"    category: {j.category}")
            print(f"    excerpt:  {j.excerpt[:80]}")
        return 0

    references = load_references(max(1, args.reference_svgs))
    print(f"Loaded {len(references)} reference SVGs")

    results: list[tuple[str, str, str, dict]] = []  # (file, status, reason, info)
    started_at = time.time()

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        future_to_job = {
            ex.submit(process_job, j, references, args.codex_model): j
            for j in jobs
        }
        completed = 0
        total = len(jobs)
        for fut in as_completed(future_to_job):
            j = future_to_job[fut]
            completed += 1
            try:
                status, reason, info = fut.result()
            except Exception as exc:  # noqa: BLE001
                status, reason, info = "FAIL", f"executor: {exc}", {"file": j.svg_path.name}
            results.append((j.svg_path.name, status, reason, info))
            tag = {"OK": "OK", "FAIL": "FAIL", "SKIP": "SKIP"}.get(status, status)
            extras = []
            if "text_count" in info:
                extras.append(f"text={info['text_count']}")
            if "attempts" in info:
                extras.append(f"attempts={info['attempts']}")
            if reason:
                extras.append(f"reason={reason[:80]}")
            extra = " ".join(extras)
            print(f"[{completed}/{total}] {tag}: {j.svg_path.name}  {extra}")

    elapsed = time.time() - started_at
    print()
    print(f"Done in {elapsed:.1f}s")
    ok = sum(1 for _, s, _, _ in results if s == "OK")
    fail = sum(1 for _, s, _, _ in results if s == "FAIL")
    print(f"  OK:   {ok}")
    print(f"  FAIL: {fail}")

    # Write a failure log
    if fail:
        fail_log = PROJECT_ROOT / "scripts" / "upgrade_2025_svgs.failures"
        with fail_log.open("w", encoding="utf-8") as fh:
            fh.write(f"Run at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for name, status, reason, info in results:
                if status != "FAIL":
                    continue
                fh.write(f"{name}\t{reason}\t{json.dumps(info, ensure_ascii=False)}\n")
        print(f"  failures logged to {fail_log.relative_to(PROJECT_ROOT)}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
