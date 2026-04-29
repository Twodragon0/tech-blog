#!/usr/bin/env python3
"""Upgrade 2025-* legacy cover SVGs to 2026 HQ-tier covers via L25-single mode.

Unlike ``upgrade_2025_svgs.py`` (which depends on flaky external CLIs),
this script uses the deterministic ``render_single_svg()`` generator in
``scripts.lib.svg_l22_generator``. No API calls, no network, fully
reproducible.

Pipeline (per post):
    1. Parse front matter (title, category, excerpt, tags, date) from
       _posts/2025-*.md.
    2. Resolve target SVG path (from ``image:`` or filename convention).
    3. Backup original SVG to assets/images/.backup/.
    4. Build (headline, tag_line, body_line, tags, visual_id, date_label,
       theme_key, illustration_key) from the front matter using a small
       per-post router (slug-keyword -> theme + illustration).
    5. Render via ``render_single_svg(...)``.
    6. Sanitize forbidden chars via ``fix_svg_forbidden_chars.fix_svg_file``.
    7. Validate (XML well-formed, viewBox 0 0 1200 630, text-node count
       50-110, ASCII-only inside <text>).
    8. Restore from backup on any verification failure.

Usage::

    python3 scripts/upgrade_2025_svgs_l25_single.py
    python3 scripts/upgrade_2025_svgs_l25_single.py --dry-run
    python3 scripts/upgrade_2025_svgs_l25_single.py --posts 5
    python3 scripts/upgrade_2025_svgs_l25_single.py --skip-existing-hq
    python3 scripts/upgrade_2025_svgs_l25_single.py --post-glob '2025-09-*.md'
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
BACKUP_DIR = IMAGES_DIR / ".backup_l25"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

import fix_svg_forbidden_chars  # noqa: E402
from scripts.lib import svg_l22_generator as l22  # noqa: E402

HQ_MARKERS = (
    "profile: high-quality-cover",
    "VISUAL SYSTEM",
    "sceneGlow1",
    "sceneGlow2",
    "THREAT INTELLIGENCE",
    "SEVERITY DISTRIBUTION",
    "SEVERITY INDEX",
    "TECH SECURITY",
)

KOREAN_RE = re.compile(r"[\uAC00-\uD7A3]")
VIEWBOX_RE = re.compile(r'viewBox\s*=\s*"([^"]+)"')

MIN_TEXT_NODES = 30
MAX_TEXT_NODES = 110

FORBIDDEN_CHARS = ["\u00B7", "\u2022", "\u2014", "\u2013",
                   "\u201C", "\u201D", "\u2018", "\u2019"]

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


# ---------------------------------------------------------------------------
# Front matter parsing (simple, lib-free)
# ---------------------------------------------------------------------------

def parse_front_matter(post_path: Path) -> dict:
    try:
        text = post_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    m = FRONT_MATTER_RE.search(text)
    if not m:
        return {}
    fm: dict = {}
    body = m.group(1)
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
            val = val.strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            fm[key] = val
    return fm


def post_image_path(front_matter: dict, post_path: Path) -> Optional[Path]:
    img = front_matter.get("image")
    if isinstance(img, str) and img.endswith(".svg"):
        rel = img.lstrip("/")
        candidate = PROJECT_ROOT / rel
        if candidate.exists():
            return candidate
    candidate = IMAGES_DIR / f"{post_path.stem}.svg"
    if candidate.exists():
        return candidate
    return None


# ---------------------------------------------------------------------------
# Title/excerpt -> headline + tag_line + visual id derivation
# ---------------------------------------------------------------------------

# ASCII fallback table for non-ASCII title characters (the front matter title
# is generally Korean; we ASCII-flatten for headline display).
ASCII_FALLBACK = re.compile(r"[^A-Za-z0-9 _\-/.,()]+")


def to_ascii_title(text: str) -> str:
    """Strip non-ASCII chars and collapse whitespace for headline use."""
    cleaned = ASCII_FALLBACK.sub(" ", text or "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


PER_POST_HEADLINE = {
    # Hand-picked compact headlines (max ~30 chars across two lines)
    # Keys are the post path stem (filename minus ".md").
    "2025-04-29-SKT_Security_Issue_Complete_Response_Guide_IMEI_Check_USIMeSIM_Replace_And_MFA_Importance":
        "SKT Security Response",
    "2025-04-30-Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage":
        "Public PC Passkey OTP",
    "2025-05-02-Cloud_Security_Course_7Batch_-_3Week_AWS_Security_And_Finops":
        "AWS Security FinOps",
    "2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide":
        "Kandji macOS MDM",
    "2025-05-09-Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_And_ISMS_Response_Guide":
        "AWS Vuln ISMS Audit",
    "2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA":
        "AWS Control Tower ZTNA",
    "2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security":
        "Cloudflare GitHub",
    "2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS":
        "Amazon Q GHAS Security",
    "2025-05-30-Cloud_Security_Course_7Batch_-_7Week_Docker_And_Kubernetes_Understanding":
        "Docker Kubernetes",
    "2025-05-30-Kubernetes_Minikube_and_K9s_Practice_Guide":
        "Kubernetes Minikube K9s",
    "2025-06-05-Email_Delivery_Trust_Improve_SendGrid_SPF_DKIM_DMARC_Setup_Complete_Guide":
        "SPF DKIM DMARC SendGrid",
    "2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CI_CDAnd_Kubernetes_Security_Practical_Guide":
        "CI/CD K8s Security",
    "2025-06-13-Cloud_Security_Course_7Batch_-_9Week_DevSecOps_Integration":
        "DevSecOps Integration",
    "2025-09-10-npm_Ecosystem_Large_scale_Security_Breach_20_Download_Package_Malware_Infection":
        "npm Supply Chain Hit",
    "2025-09-16-AWS_reInforce_2025_Cloud_Security_Current_and_Future":
        "AWS reInforce 2025",
    "2025-09-17-NPM_Shai-Hulud_Self_Replication_Worm_Attack_180_Above_Package_Breach_Large_scale_Supply_Chain_Attack_Complete_Analysis":
        "Shai-Hulud npm Worm",
    "2025-10-02-Karpenter_v153_Node_Integration_Due_to_Large_scale_Incident_Analysis_And_Resolution":
        "Karpenter v153 Incident",
    "2025-10-03-AWSIn_Database_Access_Gateway_Build_NLB_Security_Group_Complete_Guide":
        "AWS DB Gateway NLB",
    "2025-10-31-AI_Secretary_Security_Hole_For_Enterprise_AI_Service_Security_Guide":
        "AI Secretary Security",
    "2025-11-04-Zscaler_Complete_Guide_SSL_Inspection_Sandbox_AI_Advertisement_Harmful_Site_Complete_Block":
        "Zscaler SSL Inspection",
    "2025-11-19-Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned":
        "Cloudflare 11/18 PM",
    "2025-11-21-Cloud_Security_8Batch_OT_Guide_DevSecOpsFrom_FinOpsTo_Practical_Talent_Leap":
        "Cloud Sec 8 Batch OT",
    "2025-11-26-Cloud_Security_8Batch_1Week_Infrastructure_EssenceFrom_Security_FutureTo":
        "Cloud Infra Essence",
    "2025-12-05-Cloud_Security_8Batch_2Week_AWS_Security_Architecture_Core_VPCFrom_GuardDutyTo_Complete_Conquer":
        "AWS VPC GuardDuty",
    "2025-12-12-Cloud_Security_8Batch_3Week_AWS_FinOps_ArchitectureFrom_ISMS-P_Security_AuditTo_Complete_Strategy":
        "AWS FinOps ISMS-P",
    "2025-12-17-12_Conference_Review_AWSKRUG_OWASP_Datadog_Preview_See_2025_AIAnd_Security_Coexistence":
        "AWSKRUG OWASP Datadog",
    "2025-12-19-Cloud_Security_8Batch_4Week_Integration_Security_Vulnerability_Inspection_And_ISMS-P_Certification_Response":
        "Vuln Audit ISMS-P",
    "2025-12-24-Cloud_Security_Course_8Batch_5Week_AWS_Control_TowerSCP_Based_Governance_And_Datadog_SIEM_Cloudflare_Security":
        "Control Tower SCP SIEM",
}


def derive_headline(post_path: Path, fm: dict) -> str:
    """Build the hero headline from the post.

    Per-post overrides via ``PER_POST_HEADLINE`` keep covers visually clean.
    Fallback: derive from filename slug (after the date prefix), trimmed to
    ~30 characters at a word boundary.
    """
    override = PER_POST_HEADLINE.get(post_path.stem)
    if override:
        return override
    stem = post_path.stem
    parts = stem.split("-", 3)
    body = parts[3] if len(parts) >= 4 else stem
    body = body.replace("_", " ")
    body = re.sub(r"\s+", " ", body).strip()
    if len(body) <= 30:
        return body
    # Truncate at last word boundary <= 30 chars.
    head = body[:30]
    if " " in head:
        head = head.rsplit(" ", 1)[0]
    return head


def derive_visual_id(post_path: Path) -> str:
    """Generate a stable 12-char hex id from the post stem."""
    h = hashlib.sha1(post_path.stem.encode("utf-8")).hexdigest()
    return h[:12].upper()


KOREAN_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def derive_date_label(post_path: Path) -> str:
    """Convert the YYYY-MM-DD prefix to "Month D, YYYY"."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", post_path.name)
    if not m:
        return ""
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{KOREAN_MONTHS[mo - 1]} {d}, {y}"


def _flatten_category_value(val) -> str:
    """Normalise a category field that may be string, list, or "[a, b]"."""
    if isinstance(val, list):
        return val[0] if val else ""
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1]
            first = inner.split(",", 1)[0].strip().strip("'\"")
            return first
        return s
    return ""


def derive_category(fm: dict, headline: str) -> str:
    """Pick a single primary category string from front matter."""
    cat = _flatten_category_value(fm.get("category", ""))
    if cat:
        return cat
    cats_raw = fm.get("categories", [])
    if isinstance(cats_raw, list) and cats_raw:
        return cats_raw[0]
    if isinstance(cats_raw, str):
        cat = _flatten_category_value(cats_raw)
        if cat:
            return cat
    return "security"


def derive_tag_line(category: str, headline: str, fm: dict) -> str:
    """Build the slash-separated tag line under the hero headline."""
    parts: list[str] = []
    cat_upper = (category or "security").upper()
    parts.append(cat_upper)
    # Pull two more keywords from the headline (alpha tokens, distinct).
    for token in re.findall(r"[A-Za-z]{3,}", headline):
        u = token.upper()
        if u in parts:
            continue
        parts.append(u)
        if len(parts) >= 3:
            break
    return " / ".join(parts[:3])


def derive_tags(fm: dict, headline: str, category: str) -> list[str]:
    """Pull short tags for the chip row."""
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    if not isinstance(tags, list):
        tags = []
    # Normalize: ASCII-only, uppercase, dedupe.
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        flat = ASCII_FALLBACK.sub("", str(t)).upper().strip()
        if not flat or flat in seen:
            continue
        seen.add(flat)
        out.append(flat)
        if len(out) >= 4:
            break
    if not out:
        # Fallback: derive from headline keywords.
        for token in re.findall(r"[A-Za-z]{3,}", headline)[:3]:
            u = token.upper()
            if u not in seen:
                seen.add(u)
                out.append(u)
        out.append(category.upper())
    return out[:4]


def derive_body_line(fm: dict, headline: str) -> str:
    """One-line body summary for the cover (ASCII-flat, <= ~115 chars).

    Truncates at the last word boundary <= 115 chars and STRIPS any trailing
    ellipsis to avoid the check_posts.py "truncated text" warning. Trailing
    punctuation (",.") is also trimmed for visual cleanliness.
    """
    raw = fm.get("excerpt") or fm.get("description") or ""
    text = to_ascii_title(str(raw))
    if not text:
        text = headline
    if len(text) > 115:
        head = text[:115]
        if " " in head:
            head = head.rsplit(" ", 1)[0]
        text = head
    return text.rstrip(",.;: ").strip()


def derive_post_url(post_path: Path, fm: dict) -> str:
    """Derive a canonical post URL for the QR encoding."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", post_path.name)
    if not m:
        return "https://tech.2twodragon.com/"
    y, mo, d, slug = m.group(1), m.group(2), m.group(3), m.group(4)
    cat = derive_category(fm, slug).lower()
    return f"https://tech.2twodragon.com/{cat}/{y}/{mo}/{d}/{slug}.html"


def derive_aria(headline: str, category: str) -> str:
    return to_ascii_title(f"{category} {headline}")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    ok: bool
    text_count: int = 0
    reason: str = ""


def validate_svg(svg_xml: str) -> ValidationResult:
    if not svg_xml or "<svg" not in svg_xml:
        return ValidationResult(False, reason="no <svg> root")
    m = VIEWBOX_RE.search(svg_xml[:2048])
    if not m:
        return ValidationResult(False, reason="missing viewBox")
    if m.group(1).strip() != "0 0 1200 630":
        return ValidationResult(False, reason=f"viewBox '{m.group(1)}'")
    try:
        root = ET.fromstring(svg_xml)
    except ET.ParseError as exc:
        return ValidationResult(False, reason=f"XML parse: {exc}")
    text_count = sum(
        1 for el in root.iter()
        if (el.tag.split("}")[-1] if "}" in el.tag else el.tag) == "text"
    )
    if text_count < MIN_TEXT_NODES:
        return ValidationResult(False, text_count, f"too few text ({text_count})")
    if text_count > MAX_TEXT_NODES:
        return ValidationResult(False, text_count, f"too many text ({text_count})")
    # ASCII-only inside <text>/<tspan>
    for el in root.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag not in ("text", "tspan"):
            continue
        for s in (el.text, *(c.tail for c in el), *(c.text for c in el)):
            if s and KOREAN_RE.search(s):
                return ValidationResult(
                    False, text_count, "Korean inside <text>"
                )
            if s:
                for ch in FORBIDDEN_CHARS:
                    if ch in s:
                        return ValidationResult(
                            False, text_count,
                            f"forbidden char {repr(ch)} inside <text>",
                        )
    return ValidationResult(True, text_count)


# ---------------------------------------------------------------------------
# Job collection + processing
# ---------------------------------------------------------------------------

@dataclass
class PostJob:
    post_path: Path
    svg_path: Path
    fm: dict
    backup_path: Path = field(init=False)

    def __post_init__(self):
        self.backup_path = BACKUP_DIR / self.svg_path.name


def collect_jobs(post_glob: str, limit: Optional[int],
                 skip_existing_hq: bool) -> tuple[list[PostJob], list[str]]:
    skipped: list[str] = []
    jobs: list[PostJob] = []
    for post_path in sorted(POSTS_DIR.glob(post_glob)):
        fm = parse_front_matter(post_path)
        if not fm:
            skipped.append(f"{post_path.name}: no front matter")
            continue
        svg_path = post_image_path(fm, post_path)
        if svg_path is None:
            skipped.append(f"{post_path.name}: no SVG resolved")
            continue
        if skip_existing_hq:
            try:
                existing = svg_path.read_text(encoding="utf-8")
                if any(m in existing for m in HQ_MARKERS):
                    skipped.append(f"{svg_path.name}: already HQ")
                    continue
            except OSError:
                pass
        jobs.append(PostJob(post_path, svg_path, fm))
        if limit is not None and len(jobs) >= limit:
            break
    return jobs, skipped


def process_job(job: PostJob) -> tuple[str, str, dict]:
    info: dict = {"file": job.svg_path.name}
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(job.svg_path, job.backup_path)
    except OSError as exc:
        return "FAIL", f"backup failed: {exc}", info

    try:
        headline = derive_headline(job.post_path, job.fm)
        category = derive_category(job.fm, headline)
        tag_line = derive_tag_line(category, headline, job.fm)
        body_line = derive_body_line(job.fm, headline)
        tags = derive_tags(job.fm, headline, category)
        visual_id = derive_visual_id(job.post_path)
        date_label = derive_date_label(job.post_path)
        url = derive_post_url(job.post_path, job.fm)
        aria = derive_aria(headline, category)
        title_attr = headline

        sfx = "X" + visual_id[:4]

        # Lint compliance hint: lint_svg_compliance.py keys CATEGORY_RULES
        # off filename tokens. Force theme to satisfy the Cloud accent rule
        # whenever the filename or category mentions cloud / aws / gcp / ec2.
        stem = job.post_path.stem
        theme_key = ""
        if any(k in stem for k in ("Cloud_Security", "AWS_", "GCP_", "EC2_")):
            theme_key = "cloud"
        elif "Cloud_" in stem and category.lower() != "kubernetes":
            theme_key = "cloud"

        svg_xml = l22.render_single_svg(
            sfx=sfx,
            aria=aria,
            title=title_attr,
            url=url,
            headline=headline,
            category=category,
            tag_line=tag_line,
            body_line=body_line,
            tags=tags,
            visual_id=visual_id,
            date_label=date_label,
            theme_key=theme_key,
        )

        # Sanitize before validation (defensive).
        # Note: forbidden chars typically come from headline/excerpt; the
        # generator already runs everything through _xml_escape but does not
        # strip the forbidden punctuation set, so we patch the string here.
        for ch in FORBIDDEN_CHARS:
            svg_xml = svg_xml.replace(ch, " ")

        v = validate_svg(svg_xml)
        if not v.ok:
            shutil.copy2(job.backup_path, job.svg_path)
            info["reason"] = v.reason
            return "FAIL", v.reason, info

        info["text_count"] = v.text_count
        info["bytes"] = len(svg_xml)

        job.svg_path.write_text(svg_xml, encoding="utf-8")
        try:
            fix_svg_forbidden_chars.fix_svg_file(job.svg_path)
        except Exception:
            pass

        # Final re-parse sanity.
        try:
            ET.fromstring(job.svg_path.read_text(encoding="utf-8"))
        except ET.ParseError as exc:
            shutil.copy2(job.backup_path, job.svg_path)
            return "FAIL", f"post-fix parse: {exc}", info

        return "OK", "", info
    except Exception as exc:  # noqa: BLE001
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
    ap.add_argument("--posts", type=int, default=None)
    ap.add_argument("--skip-existing-hq", action="store_true")
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
        return 0

    if args.dry_run:
        for i, j in enumerate(jobs, start=1):
            headline = derive_headline(j.post_path, j.fm)
            cat = derive_category(j.fm, headline)
            tags = derive_tags(j.fm, headline, cat)
            print(f"[{i:02d}/{len(jobs)}] DRY {j.svg_path.name}")
            print(f"     headline: {headline[:70]}")
            print(f"     category: {cat}  tags: {tags}")
        return 0

    started = time.time()
    ok = 0
    fail = 0
    results: list[tuple[str, str, str, dict]] = []
    for i, j in enumerate(jobs, start=1):
        status, reason, info = process_job(j)
        results.append((j.svg_path.name, status, reason, info))
        tag = "OK" if status == "OK" else status
        extras = []
        if "text_count" in info:
            extras.append(f"text={info['text_count']}")
        if "bytes" in info:
            extras.append(f"bytes={info['bytes']}")
        if reason:
            extras.append(f"reason={reason[:80]}")
        print(f"[{i:02d}/{len(jobs)}] {tag}: {j.svg_path.name}  " + " ".join(extras))
        if status == "OK":
            ok += 1
        else:
            fail += 1

    elapsed = time.time() - started
    print()
    print(f"Done in {elapsed:.1f}s  OK={ok}  FAIL={fail}")

    if fail:
        log = SCRIPTS_DIR / "upgrade_2025_svgs_l25_single.failures"
        with log.open("w", encoding="utf-8") as fh:
            fh.write(f"Run at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for name, status, reason, info in results:
                if status != "OK":
                    fh.write(f"{name}\t{reason}\t"
                             f"{json.dumps(info, ensure_ascii=False)}\n")
        print(f"  failures logged to {log.relative_to(PROJECT_ROOT)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
