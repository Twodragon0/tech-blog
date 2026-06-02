#!/usr/bin/env python3
"""L20 cover visual-honesty scorer (deterministic, NO LLM).

Resolves OQ-6: produces a versioned, reproducible 0-100 honesty score for any
committed L20 Hero+2-Card digest cover, so a PR can prove "score went from X
to N" byte-for-byte instead of relying on an ad-hoc agent audit.

What it checks (per band: hero / top-right / bottom-right):
  1. CLAIM CLASS — each L20 visual builder (``vb_*`` in
     ``scripts/lib/svg_l20_hero.py``) hardcodes a fixed ``<text>`` vocabulary
     that asserts a specific claim class (vuln/CVE, ransomware, breach, ...).
     This module maps every builder -> claim class -> the set of post evidence
     tokens that must be present for that assertion to be HONEST.
  2. HONESTY — an attack-class band requires >=1 matching evidence token in the
     owning post's title/excerpt/body; zero matches => HONESTY_VIOLATION. The
     content-neutral classes (``neutral`` / ``market`` / ``security_advisory``)
     assert no fabricated incident and are honest on a security/market digest.
  3. BAND IDENTITY (dual path) — band identity is resolved two independent,
     deterministic ways and the two must agree:
       (a) REPLAY the generator's routing intent
           (``l20_dispatch.extract_three_stories`` + ``route_visual_id``);
       (b) FINGERPRINT the on-disk SVG by its builder's discriminating anchor.
     Disagreement => STALE_RENDER flag (the committed bytes predate the current
     generator). STALE_RENDER is a QUALITY deduction, not an honesty violation.
  4. QUALITY PROXIES (no aesthetics) — ASCII <title>/<desc> (reuses
     ``check_svg_title_ascii``), size band (reuses
     ``check_svg_size_gate.classify``), label legibility, motif diversity,
     fresh render.

Honesty is the GATING dimension: >=1 honesty violation hard-caps the total at
49 (below the PASS threshold of 70) regardless of quality points.

Determinism: same (SVG, post) bytes -> same score, every run. No network, no
LLM, no clock/random. Stdlib only.

CLI::

    python3 scripts/score_cover_honesty.py path/to/cover.svg     # single cover
    python3 scripts/score_cover_honesty.py --all                 # every L20 cover
    python3 scripts/score_cover_honesty.py --files a.svg b.svg   # explicit list
    python3 scripts/score_cover_honesty.py --all --json          # machine-readable
    python3 scripts/score_cover_honesty.py --all --strict        # exit 1 on any FAIL
    python3 scripts/score_cover_honesty.py --all --baseline scripts/cover_honesty_baseline.txt --strict
    python3 scripts/score_cover_honesty.py --update-baseline scripts/cover_honesty_baseline.txt

Exit codes:
  0  no FAIL among scored files (or all FAILs baselined), OR warn-only (default)
  1  --strict and >=1 non-baselined FAIL
  2  usage / IO error

Importable gate:
  ``score_file(svg_path) -> dict``  full scored result (JSON-serializable)
  ``check_file(svg_path) -> list[str]``  human-readable issue strings (empty = clean)

CI ROLLOUT NOTE (warn-only -> strict):
  This gate is wired into ``.github/workflows/svg-lint.yml`` as a NON-BLOCKING
  (``continue-on-error: true``) step for now, so it reports but never fails the
  build while the 60/40 weighting + 70 threshold are calibrated against the
  live corpus. To FLIP IT TO BLOCKING after calibration:
    1. Run ``--update-baseline scripts/cover_honesty_baseline.txt`` to
       grandfather the current legacy FAILs.
    2. In ``svg-lint.yml`` remove ``continue-on-error: true`` from the
       ``cover_honesty`` step and switch its command to
       ``--changed "$BASE" --baseline scripts/cover_honesty_baseline.txt --strict``
       (the same pattern the size-gate step uses).
  No pre-commit hook is wired yet (intentional — warn-only rollout first).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"
POSTS = REPO / "_posts"

# Make sibling modules importable both as ``scripts.x`` (test / package context)
# and as bare ``x`` (direct CLI run from any cwd).
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Reuse-only imports (read-only): claim-class anchors + routing + quality proxies.
from scripts.lib.svg_l20_hero import VISUAL_BUILDERS  # noqa: E402
from scripts.news.l20_dispatch import (  # noqa: E402
    extract_three_stories,
    route_visual_id,
)
from scripts.check_svg_title_ascii import _violations as _ascii_violations  # noqa: E402
from scripts.check_svg_size_gate import (  # noqa: E402
    BANDS,
    classify,
)

# Rubric identity. A score is only comparable within the same version. Bump
# this whenever the taxonomy, weighting, or thresholds change.
RUBRIC_VERSION = "1.0"

# L20 profile marker emitted by render_l20_hero (svg_l20_hero.py).
_L20_MARKER = "profile: high-quality-cover (L20 Hero+2-Card)"

# Verdict thresholds.
_PASS_MIN = 70
_WARN_MIN = 50
_HONESTY_CAP = 49  # >=1 honesty violation hard-caps the total here

# Legibility budgets (mirror svg_l20_hero._fit_panel_headline / _fit_subheadline).
_HEADLINE_MAX = 27
_SUBHEADLINE_MAX = 54

# ---------------------------------------------------------------------------
# Claim-class taxonomy (anchored to each builder's hardcoded <text> vocab).
#
# Each entry maps a visual_id ->
#   (claim_class, [evidence_regex...], [discriminating_anchor...], always_pass)
#
#   * claim_class            human-readable label used in JSON output.
#   * evidence_regex         post-evidence token family; >=1 match => honest.
#   * discriminating_anchor  literal string(s) present in the RENDERED svg only
#                            when this builder drew the band (fingerprint path).
#                            Anchors must be present verbatim after _escape();
#                            none contain '&', so XML-escaping is a no-op here.
#   * always_pass            True => asserts no fabricated incident; honest on
#                            any digest (neutral / market / security_advisory).
#                            ``market`` additionally requires a price/crypto
#                            token to be a *supported* market claim, but its
#                            absence is NOT a fabrication (still always_pass).
#
# R3 lockstep guard: CLAIM_CLASSES keys MUST equal VISUAL_BUILDERS keys. An
# unknown builder -> UNKNOWN_BUILDER hard FAIL, never a silent pass.
# ---------------------------------------------------------------------------
CLAIM_CLASSES: Dict[str, Tuple[str, List[str], List[str], bool]] = {
    "cve_chain": (
        "vuln/CVE",
        [
            r"cve-\d", r"cvss", r"\brce\b", r"zero-day", r"0-day",
            r"patch tuesday", r"exploit",
        ],
        ["CVE REGRESSION CHAIN"],
        False,
    ),
    "ransomware_lock": (
        "ransomware",
        [r"ransomware", r"wiper", r"encryptor", r"extortion", r"lockbit"],
        ["RANSOM NOTE"],
        False,
    ),
    "container_escape": (
        "container-escape/breach",
        [
            r"container escape", r"\bdocker\b", r"kubernetes", r"\bk8s\b",
            r"\brunc\b", r"privilege escalation", r"breakout",
        ],
        ["HOST KERNEL"],
        False,
    ),
    "code_injection": (
        "code-injection/RCE",
        [
            r"\brce\b", r"injection", r"payload", r"infostealer", r"stealer",
            r"byovd", r"code injection",
        ],
        ["payload.py"],
        False,
    ),
    "data_exfil": (
        "breach/exfil",
        [
            r"data leak", r"exfil", r"breach", r"credential", r"token leak",
            r"session hijack", r"s3 leak",
        ],
        ["DATA EXFILTRATION"],
        False,
    ),
    "hub_spoke": (
        "C2/botnet",
        [
            r"botnet", r"\bc2\b", r"router", r"soho", r"\bapt\b",
            r"dns hijack", r"phishing",
        ],
        [">HUB<"],
        False,
    ),
    "ai_agent_funnel": (
        "ai-agent-abuse",
        [
            r"ai agent", r"agentic", r"llm jailbreak", r"prompt injection",
            r"copilot", r"shadow ai",
        ],
        ["EXPOSED FLEET"],
        False,
    ),
    "supply_chain_pipe": (
        "supply-chain",
        [
            r"supply chain", r"slsa", r"sbom", r"\bnpm\b", r"trivy",
            r"helm chart", r"poisoned", r"tainted",
        ],
        ["SUPPLY-CHAIN POISON"],
        False,
    ),
    "neutral": (
        "neutral",
        [],  # asserts no incident — always honest
        [">UPDATE<"],
        True,
    ),
    "market": (
        "market",
        [r"\$\s*\d", r"bitcoin", r"ethereum", r"crypto", r"price", r"\d+\s*%",
         r"market cap"],
        [">MARKET<"],
        True,
    ),
    "security_advisory": (
        "generic security (advisory)",
        [
            r"vulnerability", r"\bcve\b", r"malware", r"threat", r"advisory",
            r"security", r"patch",
        ],
        ["SECURITY ADVISORY"],
        True,
    ),
}

# Precompile evidence + anchor regexes once (determinism + speed).
_EVIDENCE_RE: Dict[str, List[re.Pattern]] = {
    vid: [re.compile(p, re.IGNORECASE) for p in patterns]
    for vid, (_, patterns, _, _) in CLAIM_CLASSES.items()
}


# ---------------------------------------------------------------------------
# Cover -> post mapping (reverse-resolve the post whose image: points here)
# ---------------------------------------------------------------------------
_IMAGE_FIELD_RE = re.compile(r"^image:\s*(.+?)\s*$", re.MULTILINE)
_FRONTMATTER_FIELD = re.compile(
    r"^(title|excerpt|description):\s*(.+?)\s*$", re.MULTILINE
)


def _read_front_matter(text: str) -> str:
    """Return the YAML front-matter block (between the first two '---')."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    return text[3:end]


def find_owning_post(svg_path: Path) -> Optional[Path]:
    """Return the _posts/*.md whose ``image:`` front-matter points at ``svg_path``.

    Deterministic: scans posts in sorted order and matches by basename, so the
    result is stable regardless of filesystem iteration order.
    """
    target = svg_path.name
    for post in sorted(POSTS.glob("*.md")):
        try:
            fm = _read_front_matter(post.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        m = _IMAGE_FIELD_RE.search(fm)
        if m and Path(m.group(1).strip().strip("\"'")).name == target:
            return post
    return None


def _post_signals(post: Path) -> Tuple[str, str, str]:
    """Return (title, excerpt, lowercased full body+frontmatter) for evidence."""
    try:
        text = post.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ("", "", "")
    fm = _read_front_matter(text)
    title = ""
    excerpt = ""
    for m in _FRONTMATTER_FIELD.finditer(fm):
        key, val = m.group(1), m.group(2).strip().strip("\"'")
        if key == "title" and not title:
            title = val
        elif key in ("excerpt", "description") and not excerpt:
            excerpt = val
    return (title, excerpt, text.lower())


# ---------------------------------------------------------------------------
# Band identity (dual path)
# ---------------------------------------------------------------------------
_BAND_NAMES = ("hero", "top_right", "bottom_right")


def _routed_visual_ids(title: str, excerpt: str, filename: str) -> List[str]:
    """Replay the generator routing intent for the 3 bands (path a)."""
    stories = extract_three_stories(title, excerpt, filename)
    return [route_visual_id(s.get("headline", "")) for s in stories]


def _fingerprint_visual_ids(svg_text: str) -> List[Optional[str]]:
    """Identify the builder per band by its discriminating anchor (path b).

    The L20 layout draws exactly 3 visual builders, in document order:
    hero (first), top-right (second), bottom-right (third). We scan the SVG for
    every builder's discriminating anchor, record (offset, visual_id) hits, and
    sort by offset to recover the per-band ordering. Returns a 3-list aligned
    to (hero, top_right, bottom_right); None when fewer than 3 builders are
    detected (a malformed/partial cover).
    """
    hits: List[Tuple[int, str]] = []
    for vid, (_, _, anchors, _) in CLAIM_CLASSES.items():
        for anchor in anchors:
            idx = svg_text.find(anchor)
            if idx != -1:
                hits.append((idx, vid))
                break  # first anchor occurrence is enough to confirm the builder
    hits.sort(key=lambda h: h[0])
    ordered = [vid for _, vid in hits]
    out: List[Optional[str]] = [None, None, None]
    for i in range(min(3, len(ordered))):
        out[i] = ordered[i]
    return out


# ---------------------------------------------------------------------------
# Honesty detector
# ---------------------------------------------------------------------------
def _band_supported(visual_id: str, body_lower: str) -> bool:
    """True if the post carries >=1 evidence token for this band's claim class."""
    return any(rx.search(body_lower) for rx in _EVIDENCE_RE.get(visual_id, []))


def _score_honesty(
    band_ids: List[Optional[str]],
    body_lower: str,
) -> Tuple[int, List[Dict], List[str]]:
    """Return (honesty_score, violations, flags).

    honesty_score starts at 60; -25 per HONESTY_VIOLATION (floor 0). An
    UNKNOWN_BUILDER (visual_id not in the taxonomy) is treated as a violation
    (R3: never a silent pass).
    """
    score = 60
    violations: List[Dict] = []
    flags: List[str] = []
    for band_name, vid in zip(_BAND_NAMES, band_ids):
        if vid is None:
            continue  # unresolved band (counted under fresh/stale, not honesty)
        if vid not in CLAIM_CLASSES:
            score -= 25
            violations.append({
                "band": band_name,
                "visual_id": vid,
                "claim_class": "unknown",
                "reason": "UNKNOWN_BUILDER: visual_id not in taxonomy",
            })
            flags.append(f"UNKNOWN_BUILDER:{band_name}")
            continue
        claim_class, _, _, always_pass = CLAIM_CLASSES[vid]
        if always_pass:
            continue  # neutral / market / security_advisory assert no fabrication
        if not _band_supported(vid, body_lower):
            score -= 25
            violations.append({
                "band": band_name,
                "visual_id": vid,
                "claim_class": claim_class,
                "reason": (
                    f"no {claim_class} evidence token in post; "
                    f"band asserts a claim the post lacks"
                ),
            })
    return (max(0, score), violations, flags)


# ---------------------------------------------------------------------------
# Quality proxies (deterministic, no aesthetics)
# ---------------------------------------------------------------------------
def _quality_ascii(svg_path: Path) -> int:
    """8 pts when <title>/<desc> are ASCII-clean (reuse check_svg_title_ascii)."""
    return 0 if _ascii_violations(svg_path) else 8


def _quality_size_band(svg_path: Path) -> int:
    """8 pts when the cover sits inside its classified size band (reuse gate)."""
    try:
        profile = classify(svg_path)
        mn, mx = BANDS[profile]
        size = svg_path.stat().st_size
    except (OSError, KeyError):
        return 0
    return 8 if mn <= size <= mx else 0


# Side-panel headline text in the rendered SVG sits at x=670 font-size=24.
_PANEL_HEADLINE_RE = re.compile(
    r'<text x="670" y="(?:140|404)"[^>]*font-size="24"[^>]*>([^<]*)</text>'
)
# Hero headline sits at x=54 y=146 font-size="31".
_HERO_HEADLINE_RE = re.compile(
    r'<text x="54" y="146"[^>]*font-size="31"[^>]*>([^<]*)</text>'
)
_SUBHEADLINE_RE = re.compile(
    r'<text x="(?:54|670)" y="(?:174|163|428)"[^>]*font-weight="500"[^>]*>([^<]*)</text>'
)


def _quality_legibility(svg_text: str) -> int:
    """8 pts when no band headline/subheadline overflows its legible budget.

    Mirrors the generator's _fit_panel_headline (27) / _fit_subheadline (54)
    truncation budgets: a headline ending in '...' (truncated mid-token) or a
    side-panel headline > 27 chars indicates overflow. Hero headline is wider
    (uses 62-char fit) so it is exempt from the 27 cap but still penalized for
    a trailing ellipsis.
    """
    panel_headlines = _PANEL_HEADLINE_RE.findall(svg_text)
    hero_headlines = _HERO_HEADLINE_RE.findall(svg_text)
    subheadlines = _SUBHEADLINE_RE.findall(svg_text)
    for h in panel_headlines:
        if h.endswith("...") or len(h) > _HEADLINE_MAX:
            return 0
    for h in hero_headlines:
        if h.endswith("..."):
            return 0
    for s in subheadlines:
        if len(s) > _SUBHEADLINE_MAX + 3:  # +3 allows the '...' suffix itself
            return 0
    return 8


def _quality_motif_diversity(band_ids: List[Optional[str]]) -> int:
    """8 pts for 3 distinct claim classes, 5 for 2, 0 for 1 (all-identical)."""
    classes = set()
    for vid in band_ids:
        if vid and vid in CLAIM_CLASSES:
            classes.add(CLAIM_CLASSES[vid][0])
        elif vid:
            classes.add(vid)
    distinct = len(classes)
    if distinct >= 3:
        return 8
    if distinct == 2:
        return 5
    return 0


def _quality_fresh_render(stale_bands: int) -> int:
    """8 pts when no band is stale; -4 per stale band (floor 0)."""
    return max(0, 8 - 4 * stale_bands)


# ---------------------------------------------------------------------------
# Top-level scorer
# ---------------------------------------------------------------------------
def is_l20_cover(svg_path: Path) -> bool:
    """True when the SVG carries the L20 Hero+2-Card profile marker."""
    try:
        return _L20_MARKER in svg_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def score_file(svg_path: Path) -> Dict:
    """Score a single L20 cover. Returns a JSON-serializable result dict.

    Result keys: rubric_version, file, post, score, verdict, honesty{}, quality{},
    flags[]. Non-L20 covers return verdict ``SKIP``; covers with no owning post
    return verdict ``NO_POST`` (honesty unverifiable, not a false pass/fail).
    """
    svg_path = Path(svg_path)
    rel = _repo_rel(svg_path)
    base = {
        "rubric_version": RUBRIC_VERSION,
        "file": rel,
        "post": None,
        "score": None,
        "verdict": None,
        "honesty": {"score": None, "violations": []},
        "quality": {},
        "flags": [],
    }

    if not svg_path.exists():
        base["verdict"] = "IO_ERROR"
        base["flags"] = ["FILE_NOT_FOUND"]
        return base

    svg_text = svg_path.read_text(encoding="utf-8", errors="replace")
    if _L20_MARKER not in svg_text:
        base["verdict"] = "SKIP"
        base["flags"] = ["NOT_L20"]
        return base

    post = find_owning_post(svg_path)
    if post is None:
        base["verdict"] = "NO_POST"
        base["flags"] = ["NO_POST"]
        return base
    base["post"] = _repo_rel(post)

    title, excerpt, body_lower = _post_signals(post)

    # Band identity — dual path.
    routed = _routed_visual_ids(title, excerpt, svg_path.name)
    fingerprinted = _fingerprint_visual_ids(svg_text)

    flags: List[str] = []
    stale_bands = 0
    # The fingerprint is the source of truth for *what is on disk* (honesty must
    # score the committed bytes). Disagreement with the routing intent => stale.
    resolved: List[Optional[str]] = []
    for band_name, r_id, f_id in zip(_BAND_NAMES, routed, fingerprinted):
        if f_id is None:
            # Builder not detectable on disk for this band — fall back to the
            # routed intent so honesty can still be assessed, and flag stale.
            resolved.append(r_id)
            stale_bands += 1
            flags.append(f"STALE_RENDER:{band_name}")
        else:
            resolved.append(f_id)
            if f_id != r_id:
                stale_bands += 1
                flags.append(f"STALE_RENDER:{band_name}")

    honesty_score, violations, honesty_flags = _score_honesty(resolved, body_lower)
    flags.extend(honesty_flags)

    q_ascii = _quality_ascii(svg_path)
    q_size = _quality_size_band(svg_path)
    q_leg = _quality_legibility(svg_text)
    q_div = _quality_motif_diversity(resolved)
    q_fresh = _quality_fresh_render(stale_bands)
    quality_score = q_ascii + q_size + q_leg + q_div + q_fresh

    if q_div == 0:
        flags.append("LOW_DIVERSITY")

    has_violation = bool(violations)
    total = honesty_score + quality_score
    if has_violation:
        total = min(total, _HONESTY_CAP)

    if has_violation or total < _WARN_MIN:
        verdict = "FAIL" if has_violation else "WARN"
    elif total < _PASS_MIN:
        verdict = "WARN"
    else:
        verdict = "PASS"

    base["score"] = total
    base["verdict"] = verdict
    base["honesty"] = {"score": honesty_score, "violations": violations}
    base["quality"] = {
        "score": quality_score,
        "ascii": q_ascii,
        "size_band": q_size,
        "legibility": q_leg,
        "motif_diversity": q_div,
        "fresh_render": q_fresh,
    }
    base["bands"] = dict(zip(_BAND_NAMES, resolved))
    base["flags"] = flags
    return base


def check_file(svg_path: Path) -> List[str]:
    """Human-readable issue strings for ``svg_path`` (empty list = clean PASS).

    Mirrors ``digest_quality_report.check_file`` so a generator post-hook or
    ``auto_publish_news.py`` can gate immediately after writing a cover.
    """
    result = score_file(svg_path)
    verdict = result.get("verdict")
    if verdict in ("PASS", "SKIP"):
        return []
    messages: List[str] = []
    if verdict == "NO_POST":
        messages.append("NO_POST: no owning post found for cover (image: mismatch)")
        return messages
    if verdict == "IO_ERROR":
        messages.append("IO_ERROR: cover file unreadable")
        return messages
    for v in result["honesty"]["violations"]:
        messages.append(
            f"HONESTY_VIOLATION[{v['band']}]: {v['visual_id']} "
            f"({v['claim_class']}) - {v['reason']}"
        )
    for flag in result["flags"]:
        if flag.startswith(("STALE_RENDER", "LOW_DIVERSITY", "UNKNOWN_BUILDER")):
            messages.append(flag)
    if verdict == "WARN" and not messages:
        messages.append(
            f"WARN: score {result['score']} below PASS threshold {_PASS_MIN}"
        )
    return messages


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def _repo_rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return p.as_posix()


def collect_all() -> List[Path]:
    """Every L20 cover under assets/images/ (deterministic sorted order)."""
    return [p for p in sorted(ASSETS.glob("*.svg")) if is_l20_cover(p)]


def load_baseline(path: Path) -> set:
    """Newline-delimited grandfathered FAIL paths (mirror size-gate baseline)."""
    if not path.exists():
        return set()
    out = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            out.add(line.replace("\\", "/"))
    return out


def _resolve_paths(args_paths: List[str]) -> List[Path]:
    out: List[Path] = []
    for a in args_paths:
        p = Path(a)
        if not p.is_absolute():
            cand = Path.cwd() / a
            p = cand if cand.exists() else REPO / a
        out.append(p)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="L20 cover visual-honesty scorer (deterministic).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Score every L20 cover.")
    group.add_argument("--files", nargs="+", metavar="SVG", help="Explicit cover paths.")
    parser.add_argument("paths", nargs="*", help="Cover path(s) to score.")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any non-baselined FAIL.")
    parser.add_argument("--baseline", metavar="FILE", help="Grandfather FAILs listed here.")
    parser.add_argument(
        "--update-baseline", metavar="FILE",
        help="Write the current FAIL set to FILE then exit 0.",
    )
    args = parser.parse_args(argv)

    if args.update_baseline:
        targets = collect_all()
    elif args.all:
        targets = collect_all()
    elif args.files:
        targets = _resolve_paths(args.files)
    elif args.paths:
        targets = _resolve_paths(args.paths)
    else:
        parser.print_usage(sys.stderr)
        print("[cover-honesty] ERROR: no input (use --all, --files, or a path).", file=sys.stderr)
        return 2

    if not targets:
        if args.update_baseline:
            Path(args.update_baseline).write_text("", encoding="utf-8")
        print("[cover-honesty] No L20 covers to score.")
        return 0

    results = [score_file(p) for p in targets]

    baseline = load_baseline(Path(args.baseline)) if args.baseline else set()

    if args.update_baseline:
        fails = sorted(r["file"] for r in results if r["verdict"] == "FAIL")
        out_lines = [
            "# scripts/cover_honesty_baseline.txt",
            "# Grandfathered L20 cover-honesty FAILs.",
            "# Auto-generated by: python3 scripts/score_cover_honesty.py "
            "--update-baseline scripts/cover_honesty_baseline.txt",
            "# Each line is a repo-relative POSIX path of an L20 cover currently",
            "# scoring FAIL (>=1 honesty violation) that is intentionally allowed",
            "# during the warn-only rollout. Re-run --update-baseline after a",
            "# legacy cover is regenerated/fixed or a new legacy-class cover lands.",
            "",
        ]
        out_lines.extend(fails)
        Path(args.update_baseline).write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        print(f"[cover-honesty] wrote baseline with {len(fails)} FAIL entries -> {args.update_baseline}")
        return 0

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        _print_text(results, baseline)

    new_fails = [
        r for r in results
        if r["verdict"] == "FAIL" and r["file"] not in baseline
    ]
    if args.strict and new_fails:
        return 1
    return 0


def _print_text(results: List[Dict], baseline: set) -> None:
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0, "NO_POST": 0, "IO_ERROR": 0}
    flagged: List[Dict] = []
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
        if r["verdict"] in ("FAIL", "WARN", "NO_POST"):
            flagged.append(r)

    print("=" * 64)
    print(f"  L20 Cover Honesty Report (rubric {RUBRIC_VERSION})")
    print("=" * 64)
    scored = counts["PASS"] + counts["WARN"] + counts["FAIL"]
    print(f"  Covers scored: {scored}  (skipped non-L20: {counts['SKIP']})")
    print(f"  PASS: {counts['PASS']}   WARN: {counts['WARN']}   FAIL: {counts['FAIL']}"
          f"   NO_POST: {counts['NO_POST']}")
    print()
    if flagged:
        print("-" * 64)
        for r in flagged:
            baselined = " [baselined]" if r["file"] in baseline else ""
            print(f"  [{r['verdict']}] score={r['score']} {r['file']}{baselined}")
            for v in r["honesty"]["violations"]:
                print(f"      HONESTY[{v['band']}] {v['visual_id']} "
                      f"({v['claim_class']}): {v['reason']}")
            for flag in r["flags"]:
                if not flag.startswith("STALE_RENDER") and flag != "LOW_DIVERSITY":
                    continue
                print(f"      flag: {flag}")
        print()
    print("=" * 64)


if __name__ == "__main__":
    sys.exit(main())
