#!/usr/bin/env python3
"""Cover visual-honesty scorer (deterministic, NO LLM) for L20 / L22 / L25.

Resolves OQ-6: produces a versioned, reproducible 0-100 honesty score for any
committed L20 Hero+2-Card digest cover, so a PR can prove "score went from X
to N" byte-for-byte instead of relying on an ad-hoc agent audit.

Resolves OQ-5: extends the same deterministic rubric to the L22 fallback
3-band digest renderer (``scripts.lib.svg_l22_generator.render_bands_svg``,
fired only when L20 fails) and the L25 single-topic cover family
(``profile: high-quality-cover (2025 upgraded L25-single)``), so an L22/L25
cover can be audited reproducibly instead of by hand.

System detection (``detect_system``) reads the on-disk SVG and classifies it:
  * L20 — carries the ``profile: high-quality-cover (L20 Hero+2-Card)`` marker.
  * L25 — carries the ``profile: high-quality-cover (2025 upgraded L25-single)``
          marker (single-topic, one illustrative visual; both
          ``svg_l25_single.render_l25_single`` and the single-mode
          ``svg_l22_generator.render_single_svg`` emit this exact marker).
  * L22 — no profile marker, but has the 3-band stacked structure (``bandA``
          gradient ids + the three ``translate(500,{105,315,525})`` visual
          groups) produced by ``render_bands_svg``.
  * unknown — none of the above => current SKIP behavior (never false-flag).

Each system carries its OWN claim-class taxonomy anchored to THAT builder's
hardcoded ``<text>`` vocabulary. The honesty rule is identical across all
three: an attack-class band/visual requires >=1 matching evidence token in the
owning post, else a HONESTY_VIOLATION; neutral / market / advisory /
single-illustrative classes that assert no fabricated incident always pass.

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
    python3 scripts/score_cover_honesty.py --all                 # every L20/L22/L25 cover
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
  live corpus. As of 2026-06-02 the svg-lint ``cover_honesty`` step IS blocking,
  run conservatively as:
    ``--all --baseline scripts/cover_honesty_baseline.txt --strict``
  which scores the whole corpus but only fails on a FAIL that is NOT
  grandfathered in the baseline — i.e. only NEW honesty regressions break the
  build. (Note: there is no ``--changed`` flag; use ``--all`` + ``--baseline``.)
  After an intentional cover change, re-grandfather with
  ``--update-baseline scripts/cover_honesty_baseline.txt``.
  No pre-commit hook is wired (CI gate only).
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
    resolve_digest_band_visuals,
    route_visual_id,
)

try:  # Optional: lets the L20 routing-replay mirror the generator exactly.
    import frontmatter as _frontmatter  # type: ignore
except Exception:  # pragma: no cover - frontmatter optional in minimal envs
    _frontmatter = None
from scripts.check_svg_title_ascii import _violations as _ascii_violations  # noqa: E402
from scripts.check_svg_size_gate import (  # noqa: E402
    BANDS,
    classify,
)

# Rubric identity. A score is only comparable within the same version. Bump
# this whenever the taxonomy, weighting, or thresholds change. 1.1 widens the
# taxonomy from L20-only to L20 + L22 + L25 (OQ-5); the L20 sub-rubric and its
# scores are byte-identical to 1.0, so existing L20 PASS/FAIL verdicts are
# unchanged.
RUBRIC_VERSION = "1.1"

# Profile markers emitted by each generator family.
#   L20 — render_l20_hero (svg_l20_hero.py)
#   L25 — render_l25_single (svg_l25_single.py) AND the single-mode
#         render_single_svg (svg_l22_generator.py); both emit this exact string.
_L20_MARKER = "profile: high-quality-cover (L20 Hero+2-Card)"
_L25_MARKER = "profile: high-quality-cover (2025 upgraded L25-single)"

# Structural markers that identify an L22 3-band digest cover on disk. L22's
# render_bands_svg emits NO profile comment, so detection is structural: every
# L22 cover carries a ``bandA`` linear-gradient id and the three fixed visual
# groups at translate(500,{105,315,525}).
_L22_BAND_ANCHORS = ('id="bandA', "translate(500,105)")

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

# ---------------------------------------------------------------------------
# L22 claim-class taxonomy (anchored to svg_l22_generator's ``v_*`` visual
# captions — the hardcoded <text> vocab each visual primitive emits). L22 is
# the FALLBACK 3-band digest renderer (fires only when L20 fails). On disk a
# band's builder is identified by its discriminating caption (e.g. ``C2 HUB``
# for v_network_nodes). The routing replay path uses
# ``l22_dispatch._route_visual_kind``.
#
# Keys are the L22 visual-kind names (v_<key>). Same 4-tuple shape as
# CLAIM_CLASSES: (claim_class, [evidence...], [anchor...], always_pass).
# Attack-class kinds require a matching evidence token; the architectural /
# advisory / market kinds assert no fabricated incident and always pass.
# ---------------------------------------------------------------------------
CLAIM_CLASSES_L22: Dict[str, Tuple[str, List[str], List[str], bool]] = {
    "lock_cve": (
        "vuln/CVE",
        [r"cve-\d", r"cvss", r"\brce\b", r"zero-day", r"0-day", r"exploit",
         r"vulnerab", r"patch"],
        ["CVSS : critical scope"],
        False,
    ),
    "browser_cve": (
        "browser-vuln/CVE",
        [r"cve-\d", r"cvss", r"browser", r"chrome", r"firefox", r"safari",
         r"\bedge\b", r"exploit"],
        ["scan ack : 1 alert"],
        False,
    ),
    "network_nodes": (
        "C2/botnet",
        [r"botnet", r"\bc2\b", r"\bddos\b", r"lateral", r"\bworm\b",
         r"\bapt\b", r"infra"],
        ["C2 HUB"],
        False,
    ),
    "botnet_p2p": (
        "C2/botnet",
        [r"botnet", r"\bp2p\b", r"peer-to-peer", r"\bc2\b", r"\bddos\b",
         r"mirai", r"\bworm\b"],
        ["no central C2"],
        False,
    ),
    "wallet_forensic": (
        "crypto-breach/exfil",
        [r"bitcoin", r"\bbtc\b", r"crypto", r"wallet", r"mixer", r"on-chain",
         r"laund", r"defi", r"blockchain", r"exfil", r"breach"],
        ["on-chain trace : 3 hops"],
        False,
    ),
    "kernel_lpe": (
        "privilege-escalation",
        [r"privilege escalation", r"\blpe\b", r"\brce\b", r"kernel", r"\bring 0\b",
         r"\bring0\b", r"root", r"breakout", r"escape"],
        ["RING 3"],
        False,
    ),
    "ad_fraud": (
        "ad-fraud",
        [r"\bfraud\b", r"\bbid\b", r"ad fraud", r"click fraud", r"\bsdk\b",
         r"malvertis"],
        ["BID FRAUD"],
        False,
    ),
    "supply_chain": (
        "supply-chain",
        [r"supply chain", r"slsa", r"sbom", r"\bnpm\b", r"\bpypi\b", r"poisoned",
         r"tampered", r"package", r"registry", r"cosign"],
        ["4 stages : 1 tampered"],
        False,
    ),
    # --- Architectural / advisory / market kinds: assert no fabricated
    # incident, honest on any security/market digest band. always_pass=True.
    "shield": (
        "security (advisory/posture)",
        [],  # signed/verified posture — asserts no incident
        ["verified"],
        True,
    ),
    "code_bars": (
        "neutral (code/technical)",
        [],
        ["cursor : line 5 col 14"],
        True,
    ),
    "bar_graph": (
        "market/growth",
        [r"\$\s*\d", r"\d+\s*%", r"growth", r"trend", r"revenue", r"market",
         r"qoq", r"yoy"],
        ["6 buckets : qoq trend"],
        True,
    ),
    "price_chart": (
        "market",
        [r"\$\s*\d", r"price", r"bitcoin", r"crypto", r"\d+\s*%", r"rsi",
         r"market", r"ohlc"],
        ["7d ohlc : RSI 29"],
        True,
    ),
    "senate_columns": (
        "regulation/policy",
        [r"regulation", r"senate", r"policy", r"compliance", r"law", r"\bact\b",
         r"governance"],
        ["5 columns : 1 gavel"],
        True,
    ),
    "router_mesh": (
        "network-topology (neutral)",
        [],
        ["4 nodes : 1 hub : 8 links"],
        True,
    ),
    "cloud_k8s": (
        "kubernetes (neutral)",
        [],
        ["K8s CLOUD"],
        True,
    ),
    "compliance_grid": (
        "compliance (advisory)",
        [],
        ["9 controls : 6 pass : 1 audit"],
        True,
    ),
    "identity_handshake": (
        "zero-trust (advisory)",
        [],
        ["mTLS verify : 3 step"],
        True,
    ),
    "siem_panels": (
        "observability (advisory)",
        [],
        ["5 signals : 1 open : MTTR -60%"],
        True,
    ),
    "attestation_chain": (
        "supply-chain (advisory)",
        [],
        ["signed : cosign + SLSA L3"],
        True,
    ),
    "ai_threat": (
        "ai-security (advisory)",
        [],
        ["3 layers : 1 poison : injection"],
        True,
    ),
}

# ---------------------------------------------------------------------------
# L25 claim-class taxonomy (single-topic cover, ONE illustrative visual).
# Anchored to svg_l22_generator.SINGLE_ILLUSTRATIONS captions (the on-disk
# L25-marker covers are emitted by render_single_svg) and the L20-builder
# reuse path in svg_l25_single.render_l25_single.
#
# An L25 cover carries exactly one visual that DESCRIBES the post's own
# single topic, so almost every illustration is single-illustrative and
# asserts no fabricated incident (always_pass). The few hard attack-claim
# illustrations (a CVE padlock, a C2 network, a ransomware/incident timeline)
# still require a matching evidence token in the post.
# Keys are SINGLE_ILLUSTRATIONS keys.
# ---------------------------------------------------------------------------
CLAIM_CLASSES_L25: Dict[str, Tuple[str, List[str], List[str], bool]] = {
    "lock": (
        "vuln/CVE",
        [r"cve-\d", r"cvss", r"\brce\b", r"zero-day", r"0-day", r"exploit",
         r"vulnerab", r"malware", r"byovd", r"patch", r"breach"],
        ["SECURE PERIMETER"],
        False,
    ),
    "network": (
        "C2/network-attack",
        [r"botnet", r"\bc2\b", r"\bddos\b", r"\bdns\b", r"lateral", r"\bworm\b",
         r"infra", r"network", r"propagat", r"fanout"],
        ["PROPAGATION GRAPH"],
        False,
    ),
    "incident_timeline": (
        "incident/ransomware",
        [r"ransomware", r"incident", r"outage", r"post-?mortem", r"\brca\b",
         r"downtime", r"breach", r"spike", r"랜섬웨어", r"인시던트"],
        ["INCIDENT TIMELINE"],
        False,
    ),
    # --- single-illustrative / architectural / advisory: always_pass. These
    # describe the post's own topic and assert no fabricated incident. Each
    # anchor is the verbatim caption emitted by the matching _illust_* builder.
    "shield": ("security (illustrative)", [], ["SHIELDED PERIMETER"], True),
    "cloud": ("cloud (illustrative)", [], ["CLOUD WORKLOADS"], True),
    "chart": ("market/metrics (illustrative)", [], ["QUARTERLY TREND"], True),
    "chip": ("hardware/ai (illustrative)", [], ["AI INFERENCE"], True),
    "npm": ("supply-chain (illustrative)", [], ["PACKAGE GRAPH"], True),
    "k8s": ("kubernetes (illustrative)", [], ["K8S CLUSTER"], True),
    "pipeline": ("ci/cd (illustrative)", [], ["CI/CD PIPELINE"], True),
    "globe": ("edge/cdn (illustrative)", [], ["GLOBAL EDGE NET"], True),
    "aws": ("aws (illustrative)", [], ["AWS SERVICE STACK"], True),
    "finops": ("finops (illustrative)", [], ["FINOPS COST"], True),
    "mfa": ("mfa (illustrative)", [], ["MFA STACK"], True),
    "ztna": ("zero-trust (illustrative)", [], ["ZERO TRUST"], True),
    "isms": ("compliance (illustrative)", [], ["AUDIT CHECKLIST"], True),
    "agent": ("ai-agent (illustrative)", [], ["AGENT NETWORK"], True),
    "database": ("database (illustrative)", [], ["DB ACCESS GATEWAY"], True),
    "email": ("email-auth (illustrative)", [], ["EMAIL TRUST"], True),
    "sim": ("telco (illustrative)", [], ["TELCO IDENTITY"], True),
    "ssl": ("ssl-inspect (illustrative)", [], ["SSL INSPECT + SANDBOX"], True),
    "macos": ("macos (illustrative)", [], ["macOS DEVICE"], True),
    "conference": ("event (illustrative)", [], ["CONFERENCE STAGE"], True),
    "ai_threat": ("ai-threat (illustrative)", [], ["3 layers : 1 poison : injection"], True),
    "rollup_index": ("rollup-index (illustrative)", [], ["ROLLUP INDEX"], True),
}

# Map a system id -> its claim-class taxonomy.
_TAXONOMY_BY_SYSTEM: Dict[str, Dict[str, Tuple[str, List[str], List[str], bool]]] = {
    "L20": CLAIM_CLASSES,
    "L22": CLAIM_CLASSES_L22,
    "L25": CLAIM_CLASSES_L25,
}

# Precompile evidence + anchor regexes once per system (determinism + speed).
_EVIDENCE_RE_BY_SYSTEM: Dict[str, Dict[str, List[re.Pattern]]] = {
    system: {
        vid: [re.compile(p, re.IGNORECASE) for p in patterns]
        for vid, (_, patterns, _, _) in taxonomy.items()
    }
    for system, taxonomy in _TAXONOMY_BY_SYSTEM.items()
}

# Back-compat: the L20 evidence map keeps its original module name so the
# unchanged L20 helpers below (and any external importer) still resolve it.
_EVIDENCE_RE: Dict[str, List[re.Pattern]] = _EVIDENCE_RE_BY_SYSTEM["L20"]


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


def _routed_visual_ids(
    title: str,
    excerpt: str,
    filename: str,
    post: Optional[Path] = None,
) -> List[str]:
    """Replay the generator routing intent for the 3 bands (path a).

    When the owning ``post`` is available, mirror the generator's CONTENT-AWARE
    routing (``resolve_digest_band_visuals``): a band displaying a real story is
    routed from that story's entity, so the scored intent matches the on-disk
    visual and no spurious STALE_RENDER is raised. Falls back to filename-keyword
    routing when the post / front matter can't be loaded (older covers predating
    the content-aware generator legitimately read as stale).
    """
    if post is not None and _frontmatter is not None:
        try:
            fm = _frontmatter.load(str(post))
            return resolve_digest_band_visuals(
                title,
                excerpt,
                filename,
                content=fm.content,
                summary_card=fm.metadata.get("summary_card"),
            )
        except Exception:  # pragma: no cover - defensive: fall back to keywords
            pass
    stories = extract_three_stories(title, excerpt, filename)
    return [route_visual_id(s.get("headline", "")) for s in stories]


def _fingerprint_visual_ids(
    svg_text: str,
    taxonomy: Optional[Dict[str, Tuple[str, List[str], List[str], bool]]] = None,
    n_bands: int = 3,
) -> List[Optional[str]]:
    """Identify the builder per band by its discriminating anchor (path b).

    A 3-band digest (L20 / L22) draws exactly 3 visual builders, in document
    order: hero/first band (first), second band, third band. We scan the SVG
    for every builder's discriminating anchor, record (offset, visual_id)
    hits, and sort by offset to recover the per-band ordering. Returns an
    ``n_bands``-list aligned to band order; None entries when fewer than
    ``n_bands`` builders are detected (a malformed/partial cover).

    ``taxonomy`` defaults to the L20 ``CLAIM_CLASSES`` so existing callers are
    byte-identical; pass the L22/L25 map to fingerprint those systems. For a
    single-visual cover (L25) pass ``n_bands=1``.
    """
    tax = taxonomy if taxonomy is not None else CLAIM_CLASSES
    hits: List[Tuple[int, str]] = []
    for vid, (_, _, anchors, _) in tax.items():
        for anchor in anchors:
            idx = svg_text.find(anchor)
            if idx != -1:
                hits.append((idx, vid))
                break  # first anchor occurrence is enough to confirm the builder
    hits.sort(key=lambda h: h[0])
    ordered = [vid for _, vid in hits]
    out: List[Optional[str]] = [None] * n_bands
    for i in range(min(n_bands, len(ordered))):
        out[i] = ordered[i]
    return out


# ---------------------------------------------------------------------------
# Honesty detector
# ---------------------------------------------------------------------------
def _band_supported(
    visual_id: str,
    body_lower: str,
    evidence: Optional[Dict[str, List[re.Pattern]]] = None,
) -> bool:
    """True if the post carries >=1 evidence token for this band's claim class.

    ``evidence`` defaults to the L20 ``_EVIDENCE_RE`` map (regression-safe);
    pass the L22/L25 precompiled map to score those systems.
    """
    ev = evidence if evidence is not None else _EVIDENCE_RE
    return any(rx.search(body_lower) for rx in ev.get(visual_id, []))


def _score_honesty(
    band_ids: List[Optional[str]],
    body_lower: str,
    taxonomy: Optional[Dict[str, Tuple[str, List[str], List[str], bool]]] = None,
    evidence: Optional[Dict[str, List[re.Pattern]]] = None,
    band_names: Optional[Tuple[str, ...]] = None,
) -> Tuple[int, List[Dict], List[str]]:
    """Return (honesty_score, violations, flags).

    honesty_score starts at 60; -25 per HONESTY_VIOLATION (floor 0). An
    UNKNOWN_BUILDER (visual_id not in the taxonomy) is treated as a violation
    (R3: never a silent pass).

    ``taxonomy`` / ``evidence`` / ``band_names`` default to the L20 maps so
    existing callers are byte-identical; pass the L22/L25 maps to score those
    systems. ``band_names`` is the per-band label tuple (L25 uses a single
    ``("visual",)`` band).
    """
    tax = taxonomy if taxonomy is not None else CLAIM_CLASSES
    ev = evidence if evidence is not None else _EVIDENCE_RE
    names = band_names if band_names is not None else _BAND_NAMES
    score = 60
    violations: List[Dict] = []
    flags: List[str] = []
    for band_name, vid in zip(names, band_ids):
        if vid is None:
            continue  # unresolved band (counted under fresh/stale, not honesty)
        if vid not in tax:
            score -= 25
            violations.append({
                "band": band_name,
                "visual_id": vid,
                "claim_class": "unknown",
                "reason": "UNKNOWN_BUILDER: visual_id not in taxonomy",
            })
            flags.append(f"UNKNOWN_BUILDER:{band_name}")
            continue
        claim_class, _, _, always_pass = tax[vid]
        if always_pass:
            continue  # neutral / market / advisory / illustrative: no fabrication
        if not _band_supported(vid, body_lower, ev):
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


def _quality_motif_diversity(
    band_ids: List[Optional[str]],
    taxonomy: Optional[Dict[str, Tuple[str, List[str], List[str], bool]]] = None,
) -> int:
    """8 pts for 3 distinct claim classes, 5 for 2, 0 for 1 (all-identical).

    ``taxonomy`` defaults to the L20 map (regression-safe). A single-visual
    cover (L25) has 1 band -> distinct==1 by construction, so diversity is not
    a meaningful penalty for L25 and the caller exempts it.
    """
    tax = taxonomy if taxonomy is not None else CLAIM_CLASSES
    classes = set()
    for vid in band_ids:
        if vid and vid in tax:
            classes.add(tax[vid][0])
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
# System detection + per-system routing replay
# ---------------------------------------------------------------------------
def is_l20_cover(svg_path: Path) -> bool:
    """True when the SVG carries the L20 Hero+2-Card profile marker."""
    try:
        return _L20_MARKER in svg_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def detect_system(svg_text: str) -> Optional[str]:
    """Classify a cover by system from its on-disk bytes.

    Returns ``"L20"`` / ``"L22"`` / ``"L25"`` / ``None`` (unknown).

    * L20 — ``profile: high-quality-cover (L20 Hero+2-Card)`` marker.
    * L25 — ``profile: high-quality-cover (2025 upgraded L25-single)`` marker.
    * L22 — no profile marker, but the 3-band stacked structure (``bandA``
            gradient id + the first ``translate(500,105)`` visual group).
    * None — none of the above (keep current SKIP behavior; never false-flag).

    Order matters: profile markers win over the structural L22 check so a
    future marker-bearing L22 cover (if ever added) would not mis-detect.
    """
    if _L20_MARKER in svg_text:
        return "L20"
    if _L25_MARKER in svg_text:
        return "L25"
    if all(anchor in svg_text for anchor in _L22_BAND_ANCHORS):
        return "L22"
    return None


def is_cover_in_scope(svg_path: Path) -> bool:
    """True when the SVG is an L20/L22/L25 cover this scorer can audit."""
    try:
        return detect_system(
            svg_path.read_text(encoding="utf-8", errors="replace")
        ) is not None
    except OSError:
        return False


def _routed_visual_kinds_l22(title: str, excerpt: str, filename: str) -> List[str]:
    """Replay the L22 dispatch routing intent for the 3 bands (path a).

    Mirrors ``l22_dispatch.generate_l22_digest_svg``: resolve the 3 anchor
    stories, route each headline to a visual kind, then apply the same
    deterministic variety-enforcement pass keyed by the post-date seed so the
    routed intent matches what the generator would emit today.
    """
    from scripts.news import l22_dispatch as l22d

    h, tr, br = l22d._resolve_three_stories(title, excerpt, filename)
    date_str = l22d._date_str_from_filename(filename) or ""
    seed = date_str.replace(".", "") or filename or "L22"
    initial = [
        l22d._route_visual_kind(h.get("headline", ""), 0),
        l22d._route_visual_kind(tr.get("headline", ""), 1),
        l22d._route_visual_kind(br.get("headline", ""), 2),
    ]
    return l22d._force_variety(initial, seed)


def _picked_illustration_l25(title: str, excerpt: str, category: str) -> Optional[str]:
    """Replay the L25 single-mode illustration choice (path a).

    ``render_single_svg`` picks its illustration via
    ``svg_l22_generator._pick_illustration(category, title)``. We replay that
    here so the routed intent can be compared against the on-disk fingerprint.
    Returns the SINGLE_ILLUSTRATIONS key, or None when the module is
    unavailable.
    """
    try:
        from scripts.lib import svg_l22_generator as l22
    except Exception:
        return None
    return l22._pick_illustration(category or "", title or "")


# ---------------------------------------------------------------------------
# Top-level scorer
# ---------------------------------------------------------------------------
def score_file(svg_path: Path) -> Dict:
    """Score a single L20/L22/L25 cover. Returns a JSON-serializable dict.

    Result keys: rubric_version, system, file, post, score, verdict, honesty{},
    quality{}, bands{}, flags[]. Covers of an unknown system return verdict
    ``SKIP``; in-scope covers with no owning post return ``NO_POST`` (honesty
    unverifiable, not a false pass/fail).
    """
    svg_path = Path(svg_path)
    rel = _repo_rel(svg_path)
    base = {
        "rubric_version": RUBRIC_VERSION,
        "system": None,
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
    system = detect_system(svg_text)
    if system is None:
        base["verdict"] = "SKIP"
        base["flags"] = ["UNKNOWN_SYSTEM"]
        return base
    base["system"] = system

    post = find_owning_post(svg_path)
    if post is None:
        base["verdict"] = "NO_POST"
        base["flags"] = ["NO_POST"]
        return base
    base["post"] = _repo_rel(post)

    title, excerpt, body_lower = _post_signals(post)

    if system == "L25":
        return _finish_l25(base, svg_path, svg_text, title, excerpt, body_lower)
    # L20 + L22 share the 3-band scoring shape (different taxonomy + routing).
    return _finish_three_band(
        base, system, svg_path, svg_text, title, excerpt, body_lower, post
    )


def _finish_three_band(
    base: Dict,
    system: str,
    svg_path: Path,
    svg_text: str,
    title: str,
    excerpt: str,
    body_lower: str,
    post: Optional[Path] = None,
) -> Dict:
    """Score an L20 or L22 3-band digest cover (dual-path band identity)."""
    taxonomy = _TAXONOMY_BY_SYSTEM[system]
    evidence = _EVIDENCE_RE_BY_SYSTEM[system]

    # Band identity — dual path.
    if system == "L20":
        routed = _routed_visual_ids(title, excerpt, svg_path.name, post)
    else:  # L22
        try:
            routed = _routed_visual_kinds_l22(title, excerpt, svg_path.name)
        except Exception:
            routed = [None, None, None]
    fingerprinted = _fingerprint_visual_ids(svg_text, taxonomy, n_bands=3)

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

    honesty_score, violations, honesty_flags = _score_honesty(
        resolved, body_lower, taxonomy, evidence
    )
    flags.extend(honesty_flags)

    q_ascii = _quality_ascii(svg_path)
    q_size = _quality_size_band(svg_path)
    q_leg = _quality_legibility(svg_text)
    q_div = _quality_motif_diversity(resolved, taxonomy)
    q_fresh = _quality_fresh_render(stale_bands)
    quality_score = q_ascii + q_size + q_leg + q_div + q_fresh

    if q_div == 0:
        flags.append("LOW_DIVERSITY")

    return _finalize(
        base, honesty_score, violations, flags, quality_score,
        {
            "ascii": q_ascii, "size_band": q_size, "legibility": q_leg,
            "motif_diversity": q_div, "fresh_render": q_fresh,
        },
        dict(zip(_BAND_NAMES, resolved)),
    )


_L25_BAND_NAMES = ("visual",)


def _finish_l25(
    base: Dict,
    svg_path: Path,
    svg_text: str,
    title: str,
    excerpt: str,
    body_lower: str,
) -> Dict:
    """Score an L25 single-topic cover (one illustrative visual).

    L25 has a single claim-bearing visual rather than 3 bands, so motif
    diversity is not a meaningful signal (always 1 class) — it is excluded
    from the quality budget and replaced by an equal-weight rebalance so an
    honest single cover can still reach the PASS threshold. Honesty is scored
    identically: an attack-class illustration requires a matching evidence
    token; the single-illustrative classes always pass.
    """
    taxonomy = CLAIM_CLASSES_L25
    evidence = _EVIDENCE_RE_BY_SYSTEM["L25"]

    fingerprinted = _fingerprint_visual_ids(svg_text, taxonomy, n_bands=1)
    category = _category_from_post(base.get("post"))
    routed = _picked_illustration_l25(title, excerpt, category)

    flags: List[str] = []
    stale = 0
    f_id = fingerprinted[0]
    if f_id is None:
        resolved = [routed]
        stale = 1
        flags.append("STALE_RENDER:visual")
    else:
        resolved = [f_id]
        if routed is not None and f_id != routed:
            stale = 1
            flags.append("STALE_RENDER:visual")

    honesty_score, violations, honesty_flags = _score_honesty(
        resolved, body_lower, taxonomy, evidence, band_names=_L25_BAND_NAMES
    )
    flags.extend(honesty_flags)

    # Quality (no motif-diversity term — single visual). Redistribute the 8
    # diversity points across the 4 remaining proxies so the max stays 40.
    q_ascii = _quality_ascii(svg_path)
    q_size = _quality_size_band(svg_path)
    q_leg = _quality_legibility_l25(svg_text)
    q_fresh = _quality_fresh_render(stale)
    # Each of the 4 proxies is worth 10 (was 8). Scale 8-point results to 10.
    quality_score = round((q_ascii + q_size + q_leg + q_fresh) * 10 / 8)

    return _finalize(
        base, honesty_score, violations, flags, quality_score,
        {
            "ascii": q_ascii, "size_band": q_size, "legibility": q_leg,
            "fresh_render": q_fresh,
        },
        {"visual": resolved[0]},
    )


def _finalize(
    base: Dict,
    honesty_score: int,
    violations: List[Dict],
    flags: List[str],
    quality_score: int,
    quality_detail: Dict,
    bands: Dict,
) -> Dict:
    """Shared verdict computation for all systems (identical to L20 1.0)."""
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
    base["quality"] = dict(quality_detail, score=quality_score)
    base["bands"] = bands
    base["flags"] = flags
    return base


def _category_from_post(post_rel: Optional[str]) -> str:
    """Read the post's ``category`` front-matter field (for L25 replay)."""
    if not post_rel:
        return ""
    p = REPO / post_rel
    try:
        fm = _read_front_matter(p.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ""
    m = re.search(r"^category:\s*(.+?)\s*$", fm, re.MULTILINE)
    if m:
        return m.group(1).strip().strip("[]\"'")
    return ""


# L25 hero headline sits at x=54 y=172 font-size="34"; subheadline x=54 y=208
# font-size="18". The single-mode render_single_svg uses a different layout
# (Arial hero at x=84), so the L25 legibility proxy only penalizes a trailing
# ellipsis on any hero/sub text rather than re-deriving per-layout budgets.
_L25_ELLIPSIS_RE = re.compile(r'<text[^>]*font-size="(?:18|34|40|48|54|60)"[^>]*>([^<]*)</text>')


def _quality_legibility_l25(svg_text: str) -> int:
    """8 pts when no L25 hero/subheadline text is truncated with an ellipsis."""
    for t in _L25_ELLIPSIS_RE.findall(svg_text):
        if t.endswith("..."):
            return 0
    return 8


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
    """Every in-scope L20/L22/L25 cover under assets/images/ (sorted)."""
    return [p for p in sorted(ASSETS.glob("*.svg")) if is_cover_in_scope(p)]


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
        print("[cover-honesty] No in-scope covers to score.")
        return 0

    results = [score_file(p) for p in targets]

    baseline = load_baseline(Path(args.baseline)) if args.baseline else set()

    if args.update_baseline:
        fails = sorted(r["file"] for r in results if r["verdict"] == "FAIL")
        out_lines = [
            "# scripts/cover_honesty_baseline.txt",
            "# Grandfathered cover-honesty FAILs (L20 / L22 / L25).",
            "# Auto-generated by: python3 scripts/score_cover_honesty.py "
            "--update-baseline scripts/cover_honesty_baseline.txt",
            "# Each line is a repo-relative POSIX path of a cover currently",
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

    # Per-system breakdown (only scored verdicts count toward a system).
    sys_counts: Dict[str, Dict[str, int]] = {}
    for r in results:
        sysid = r.get("system") or "unknown"
        bucket = sys_counts.setdefault(
            sysid, {"PASS": 0, "WARN": 0, "FAIL": 0, "NO_POST": 0}
        )
        if r["verdict"] in bucket:
            bucket[r["verdict"]] += 1

    print("=" * 64)
    print(f"  Cover Honesty Report (rubric {RUBRIC_VERSION})  L20 / L22 / L25")
    print("=" * 64)
    scored = counts["PASS"] + counts["WARN"] + counts["FAIL"]
    print(f"  Covers scored: {scored}  (skipped unknown-system: {counts['SKIP']})")
    print(f"  PASS: {counts['PASS']}   WARN: {counts['WARN']}   FAIL: {counts['FAIL']}"
          f"   NO_POST: {counts['NO_POST']}")
    print()
    print("  By system:")
    for sysid in ("L20", "L22", "L25", "unknown"):
        b = sys_counts.get(sysid)
        if not b:
            continue
        n = b["PASS"] + b["WARN"] + b["FAIL"]
        print(f"    {sysid:8s} scored={n:3d}  PASS={b['PASS']:3d}  "
              f"WARN={b['WARN']:3d}  FAIL={b['FAIL']:3d}  NO_POST={b['NO_POST']:3d}")
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
