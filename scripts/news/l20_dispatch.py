"""L20 Hero+2-Card weekly digest dispatch helpers.

This module wires the new ``scripts.lib.svg_l20_hero`` cover style into the
weekly-digest publishing pipeline used by ``scripts/auto_publish_news.py``.

Public entrypoints:

- :data:`L20_HERO_ENABLED` -- module-level boolean flag, evaluated at import
  time from the ``USE_L20_HERO`` env var. Defaults to ``True`` (L20 ON).
- :func:`route_visual_id` -- keyword router mapping a topic phrase to one of
  the 8 visual builders shipped by :mod:`scripts.lib.svg_l20_hero`.
- :func:`route_theme` -- pick a theme palette (red / blue / amber / green /
  purple) from a severity / index hint.
- :func:`extract_three_stories` -- split a post title + excerpt into 3
  short, English-friendly story dicts.
- :func:`_infer_kpi` -- regex-driven KPI heuristic (CVE id, USD amounts,
  CVSS score) used to populate the L20 KPI cards.
- :func:`generate_l20_digest_svg` -- top-level writer that mirrors
  ``generate_l22_digest_svg`` and renders an L20 cover for a digest post.

Branch order in :func:`route_visual_id` is intentional: more specific
keywords (``container``, ``docker``, ``ai agent``) precede broader ones
(``cve-``, ``ai ``) so that a story about "Docker container escape via
CVE-2026-X" routes to ``container_escape`` instead of ``cve_chain``.
This mirrors the priority guidance in ``CLAUDE.md``.

The module never makes network calls, never reads/writes secrets, and uses
stdlib + existing repo modules only.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Module-level feature flag. Evaluated once at import time so callers may
# override it for tests via ``monkeypatch.setattr(...)`` or by mutating the
# module attribute directly.
L20_HERO_ENABLED: bool = os.getenv("USE_L20_HERO", "1").strip().lower() not in {
    "0",
    "false",
    "",
}


# Ordered keyword routes. ORDER MATTERS: specific keywords first.
# Each tuple is (tuple_of_keywords, visual_id).
_VISUAL_ROUTES: List[Tuple[Tuple[str, ...], str]] = [
    # 1. CVE / vuln (catch-all for CVSS / RCE / patch tuesday). Only matches
    #    after the more-specific routes below failed, because container/AI
    #    stories may also contain "CVE-...". Kept here as the *first* visible
    #    route only because it is the natural fallback for raw vuln stories;
    #    the dispatcher iterates routes in order, but specific buckets
    #    (container, ai-agent, ransomware, supply chain) come *before* this
    #    block for over-match safety. -- See ordering below.
    # NOTE: do NOT reorder without updating tests/test_l20_hero_routing.py.
    (("ransomware", "wiper", "encryptor", "leaknet", "gentlemen"), "ransomware_lock"),
    (("container", "docker", "kubernetes", "ecs", "k8s", "harbor"), "container_escape"),
    (
        ("ai agent", "agentic", "llm jailbreak", "prompt injection", "copilot"),
        "ai_agent_funnel",
    ),
    (
        (
            "supply chain",
            "slsa",
            "sbom",
            "npm",
            "git push",
            "trivy",
            "helm chart",
        ),
        "supply_chain_pipe",
    ),
    (
        (
            "infostealer",
            "stealer",
            "rmm",
            "rms",
            "edr bypass",
            "byovd",
            "code injection",
            "snow loader",
            "fast16",
        ),
        "code_injection",
    ),
    (
        (
            "botnet",
            "router",
            "soho",
            "apt",
            "dns hijack",
            "phishing",
            "spear-phishing",
            "c2",
        ),
        "hub_spoke",
    ),
    (
        (
            "data leak",
            "exfil",
            "credential",
            "token leak",
            "session hijack",
            "sso",
            "aws s3 leak",
        ),
        "data_exfil",
    ),
    # Brand / topic aliases (ASCII-only). Korean source tokens never reach
    # this router: ``extract_three_stories`` replaces Hangul segments with
    # ASCII filename-slug keywords BEFORE routing (see L321-333), so only the
    # ASCII brand names below can match. HONESTY-DRIVEN mapping (Option B):
    # non-attack content routes to the content-neutral ``neutral`` builder,
    # genuine market/price stories to ``market``; only genuine attack/vuln
    # content reaches an attack builder. The prior Option A stopgap mapped
    # these to attack builders (data_exfil/container_escape/hub_spoke), which
    # the designer re-audit flagged: those assert breaches / container
    # escapes / C2 the posts do not contain. See
    # ``.omc/plans/l20-digest-cover-audit-fix.md`` (Step 7 / Option B):
    #   bithumb/upbit  -> neutral   (exchange OPERATIONAL incident, not an
    #                                intrusion; data_exfil falsely asserted a
    #                                breach the post lacks)
    #   cncf/cluster api/cloud native -> neutral (ecosystem velocity /
    #                                lifecycle, NOT a container escape)
    #   bitcoin/ethereum -> market  (price / market story; no attack topology)
    #   chainalysis/hexagate -> neutral (security-integration product story,
    #                                not an attack; also dead for the 2
    #                                flagged covers but kept honest)
    # MUST precede the generic cve_chain catch-all (specific-first ordering).
    # NOTE: chainalysis/hexagate are effectively dead for the two flagged
    # CNCF/Bithumb covers (those titles yield 3 ASCII segments, so the
    # excerpt where these tokens live never backfills into a routed
    # headline); they are added for OTHER posts that may surface them.
    (("bithumb", "upbit"), "neutral"),
    (("cncf", "cluster api", "cloud native"), "neutral"),
    (("bitcoin", "ethereum"), "market"),
    (("chainalysis", "hexagate"), "neutral"),
    # CVE / generic vuln route MUST come after the specific buckets above so
    # that "Docker container escape via CVE-2026-X" stays in container_escape.
    (("cve-2", "cvss", "rce", "patch tuesday", "zero-day", "0-day"), "cve_chain"),
]

# Theme rotation defaults: hero=red, second=blue, third=amber.
_THEME_BY_INDEX: Dict[int, str] = {0: "red", 1: "blue", 2: "amber"}

# Content-driven theme overrides (visual_id -> theme).
_THEME_BY_VISUAL: Dict[str, str] = {
    "ransomware_lock": "red",
    "supply_chain_pipe": "amber",
    "data_exfil": "blue",
    "ai_agent_funnel": "amber",
    # Non-incident visuals: cool/calm palettes (blue digest, amber market)
    # so the cover does not read as a red-alert security incident.
    "neutral": "blue",
    "market": "amber",
}

# Severity-keyword overrides (case-insensitive substring match).
_SEVERITY_OVERRIDES: List[Tuple[str, str]] = [
    ("critical", "red"),
    ("high", "red"),
    ("ransomware", "red"),
    ("medium", "amber"),
    ("supply chain", "amber"),
    ("low", "blue"),
    ("info", "blue"),
]


def route_visual_id(topic: str) -> str:
    """Return the L20 visual_id that best matches ``topic``.

    Uses an ordered list of keyword tuples; the FIRST tuple whose keyword
    appears (case-insensitive substring) in ``topic`` wins.

    No-match / empty-topic default is ``"neutral"`` — a genuinely
    content-neutral digest/ecosystem visual (``svg_l20_hero.vb_neutral``,
    Option B / the honest corpus-wide fix). It asserts NO incident (no CVE,
    breach, C2, or exfiltration) on any unrouted topic. History: the default
    was ``"cve_chain"`` (fabricated a CVE-exploitation narrative on every
    unrouted crypto/market/cloud-native topic) -> ``"hub_spoke"`` (Option A
    stopgap; relocated the false claim to a C2/relay narrative) -> ``"neutral"``
    (honest). This default and the matching ``_render_visual`` unknown-key
    fallback (``svg_l20_hero.py``) MUST stay in lockstep. See
    ``.omc/plans/l20-digest-cover-audit-fix.md`` (Step 7 / Option B).

    Order is deliberately specific-first: e.g. "Docker container escape via
    CVE-2026-1234" routes to ``container_escape`` rather than ``cve_chain``
    because the container bucket is checked before the CVE bucket. The
    explicit CVE keyword route (``cve-2``/``cvss``/``rce``/...) is preserved
    so real-CVE posts still render ``cve_chain``.
    """
    if not topic:
        return "neutral"
    lower = topic.lower()
    for keywords, visual_id in _VISUAL_ROUTES:
        for kw in keywords:
            if kw in lower:
                return visual_id
    return "neutral"


def route_theme(severity_or_index: str) -> str:
    """Pick one of the 5 L20 theme palettes.

    Accepts either a severity/keyword string ("critical", "ransomware",
    "supply chain") or a 0-based index ("0" / "1" / "2"). Falls back to
    ``"red"`` so the hero panel always renders.
    """
    if severity_or_index is None:
        return "red"
    s = str(severity_or_index).strip().lower()
    if not s:
        return "red"

    # Index path: "0" -> red, "1" -> blue, "2" -> amber.
    if s.isdigit():
        return _THEME_BY_INDEX.get(int(s), "red")

    # Visual-id path.
    if s in _THEME_BY_VISUAL:
        return _THEME_BY_VISUAL[s]

    # Severity / keyword path.
    for needle, theme in _SEVERITY_OVERRIDES:
        if needle in s:
            return theme
    return "red"


# --- Story extraction ---
# Tunable via constants kept at module-scope so tests can monkeypatch them.
_HEADLINE_MAX_CHARS: int = 30
_SUB_MIN_CHARS: int = 40
_SUB_MAX_CHARS: int = 60

# Splitter regex: comma, hyphen-with-spaces, the unicode middle-dot,
# ASCII bullet, and pipe. Hyphens INSIDE words ("Zero-Day") are preserved
# because we require surrounding whitespace.
_STORY_SPLIT_RE = re.compile(r"\s*(?:,|;|\s-\s|\s\u00b7\s|\u2022|\|)\s*")

# Boilerplate prefixes to strip from titles before splitting.
_TITLE_PREFIX_RE = re.compile(
    r"^(?:weekly\s+digest|tech\s+security\s+weekly\s+digest|daily\s+tech\s+digest)"
    r"\s*[:\-]?\s*\d{0,4}[\-./]?\d{0,2}[\-./]?\d{0,2}\s*[:\-]?\s*",
    re.IGNORECASE,
)

# Hangul syllable + jamo block detector. Triggers the English-fallback path
# in extract_three_stories so SVG <text> elements stay ASCII-only (the
# check-svg quality gate forbids Hangul in <text>).
_HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")

# Strip the date prefix (YYYY-MM-DD-) and the digest stem from a post
# filename so the trailing ``slug_part_with_topics`` can be split into
# English keywords.
_FILENAME_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_FILENAME_DIGEST_STEM_RE = re.compile(
    r"^(?:Tech_Security_Weekly_Digest|Tech_Blog_Weekly_Digest|"
    r"Weekly[_-]Security_Digest|Weekly_Tech_AI_Blockchain_Digest|"
    r"Weekly_Security_DevOps_Digest|Daily_Tech_Digest|"
    r"Security_Cloud_Digest|AI_Cloud_Digest|DevOps_Blockchain_Digest|"
    r"Security_Digest|Blockchain_Tech_Digest)_+",
    re.IGNORECASE,
)


def _english_topics_from_filename(filename: str) -> List[str]:
    """Extract English topic keywords from a digest filename's slug.

    Example::

        2026-05-01-Tech_Security_Weekly_Digest_AI_AWS_Threat_Cloud.md
        → ["AI", "AWS", "Threat", "Cloud"]

    Returns an empty list when no slug-style keywords can be derived.
    """
    if not filename:
        return []
    name = Path(filename).stem
    name = _FILENAME_DATE_PREFIX_RE.sub("", name)
    name = _FILENAME_DIGEST_STEM_RE.sub("", name)
    parts = [p for p in re.split(r"[_-]+", name) if p]
    # Filter out anything containing non-ASCII or pure digits.
    keywords: List[str] = []
    for p in parts:
        if any(ord(ch) > 127 for ch in p):
            continue
        if p.isdigit():
            continue
        keywords.append(p)
    return keywords


def _has_hangul(text: str) -> bool:
    return bool(_HANGUL_RE.search(text or ""))


def _clean_segment(seg: str) -> str:
    """Trim and collapse whitespace in a single split segment."""
    return re.sub(r"\s+", " ", (seg or "").strip())


def _shorten(text: str, limit: int) -> str:
    """Trim ``text`` to <= ``limit`` chars without inserting ellipses."""
    text = _clean_segment(text)
    if len(text) <= limit:
        return text
    # Prefer breaking on whitespace to keep words intact.
    cut = text[:limit].rsplit(" ", 1)[0].rstrip()
    return cut or text[:limit].rstrip()


_SUBHEADLINE_EXTRA_MAX_TOKENS: int = 2


def _dedupe_subheadline_extra(
    base: str,
    extra: str,
    other_headlines: Optional[List[str]] = None,
) -> str:
    """Drop the redundant slug echo from a subheadline ``extra`` context.

    Bug fix (designer re-audit): for Korean-excerpt digests the only ASCII
    ``extra`` available is the filename-keyword join (e.g. ``"Bithumb
    Bitcoin"``), which echoes the headline token. The old ``base + " - " +
    extra`` then rendered ``"Bithumb - Bithumb Bitcoin"`` /
    ``"CNCF - CNCF Chainalysis Bitcoin"``. Here we remove every word of
    ``extra`` that already appears in ``base`` (case-insensitive).

    Trailing-token tightening (polish nit 2): the kept remainder could still
    duplicate *another* band's topic — e.g. for band 1 "Cluster API" the
    extra ``"CNCF Chainalysis Bitcoin"`` kept a trailing "Bitcoin" that is
    band 3's headline. So we additionally:

    1. de-duplicate repeated tokens within ``extra`` (keep first occurrence);
    2. when ``other_headlines`` is supplied, drop any token equal to another
       band's headline lead-token (the cross-band echo);
    3. cap the remainder to ``_SUBHEADLINE_EXTRA_MAX_TOKENS`` tokens.

    Returns the trimmed remainder (possibly empty). The cap keeps the result
    honest/meaningful — it shortens, it does not blank a genuine context.
    """
    base_words = {w.lower() for w in re.findall(r"\w+", base)}
    drop_words = set(base_words)
    for hl in other_headlines or []:
        for w in re.findall(r"\w+", hl or ""):
            drop_words.add(w.lower())

    kept: List[str] = []
    seen: set = set()
    for w in extra.split():
        wl = w.lower()
        if wl in base_words:
            continue  # always drop the headline's own echo
        if wl in seen:
            continue  # de-dup repeated tokens
        if wl in drop_words:
            continue  # cross-band headline echo
        seen.add(wl)
        kept.append(w)
        if len(kept) >= _SUBHEADLINE_EXTRA_MAX_TOKENS:
            break
    return _clean_segment(" ".join(kept))


def _pad_subheadline(
    seg: str,
    excerpt: str,
    other_headlines: Optional[List[str]] = None,
) -> str:
    """Build a 40-60 char subheadline from a segment + excerpt context.

    The ``extra`` context is de-duplicated against the headline so the
    subheadline never echoes the headline back (see
    ``_dedupe_subheadline_extra``). ``other_headlines`` (the sibling bands'
    headlines) lets the de-dupe also drop a trailing token that duplicates
    another band's topic. When no non-redundant context remains, fall back
    to the headline segment alone rather than ``"X - X ..."``.
    """
    base = _clean_segment(seg)
    if len(base) >= _SUB_MIN_CHARS:
        return _shorten(base, _SUB_MAX_CHARS)
    extra = _dedupe_subheadline_extra(
        base, _clean_segment(excerpt), other_headlines=other_headlines
    )
    candidate = (base + " - " + extra).strip(" -") if extra else base
    return _shorten(candidate, _SUB_MAX_CHARS) or base


def extract_three_stories(
    post_title: str,
    excerpt: str,
    filename: str = "",
) -> Tuple[Dict, Dict, Dict]:
    """Split title + excerpt into 3 succinct English story dicts.

    Returned dicts contain ``headline`` (<= 30 chars) and ``subheadline``
    (40-60 chars when material is available). They are intended to be
    merged with routing/KPI keys before being handed to ``render_l20_hero``.

    English-only guarantee: when any candidate segment contains Hangul,
    that slot is replaced with a keyword derived from ``filename``'s
    English topic slug (e.g., ``..._AI_AWS_Threat_Cloud.md`` →
    ``["AI", "AWS", "Threat", "Cloud"]``). The check-svg quality gate
    forbids non-ASCII text inside SVG ``<text>`` elements, so this is a
    hard correctness requirement, not a cosmetic concern.
    """
    title = (post_title or "").strip()
    title = _TITLE_PREFIX_RE.sub("", title)

    # Primary split source: the title (it carries 3 topic phrases in the
    # current digest naming convention).
    raw_segments = [s for s in _STORY_SPLIT_RE.split(title) if s.strip()]

    # Backfill from excerpt if the title yielded fewer than 3 segments.
    if len(raw_segments) < 3:
        excerpt_segments = [
            s for s in _STORY_SPLIT_RE.split(excerpt or "") if s.strip()
        ]
        for seg in excerpt_segments:
            if len(raw_segments) >= 3:
                break
            raw_segments.append(seg)

    # Replace any Hangul-containing segment with an English keyword pulled
    # from the filename slug. We pad the keyword pool with neutral fallbacks
    # so a Korean-only post still produces 3 deterministic English stories.
    en_keywords = _english_topics_from_filename(filename)
    en_pool = list(en_keywords) + ["Security Update", "Threat Analysis", "Patch Advisory"]
    en_iter = iter(en_pool)
    cleaned: List[str] = []
    for seg in raw_segments:
        if _has_hangul(seg):
            cleaned.append(next(en_iter, "Security Update"))
        else:
            cleaned.append(seg)
    raw_segments = cleaned

    # Final padding: stable placeholders that still render legibly. Prefer
    # remaining filename keywords before falling back to a generic phrase.
    while len(raw_segments) < 3:
        raw_segments.append(next(en_iter, "Security Update"))

    segments = [_clean_segment(s) for s in raw_segments[:3]]
    stories: List[Dict] = []
    # Subheadline padding context: also stripped of Hangul to avoid leaking
    # Korean into the secondary text element.
    safe_excerpt = excerpt or ""
    if _has_hangul(safe_excerpt):
        safe_excerpt = " ".join(en_keywords) if en_keywords else ""
    headlines = [_shorten(seg, _HEADLINE_MAX_CHARS) for seg in segments]
    for i, seg in enumerate(segments):
        others = [h for j, h in enumerate(headlines) if j != i]
        stories.append(
            {
                "headline": headlines[i],
                "subheadline": _pad_subheadline(
                    seg, safe_excerpt, other_headlines=others
                ),
            }
        )
    return stories[0], stories[1], stories[2]


# --- KPI inference ---
_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
_CVSS_RE = re.compile(r"CVSS\s*([0-9]+(?:\.[0-9])?)", re.IGNORECASE)
_USD_RE = re.compile(r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*([KMB])\b", re.IGNORECASE)
_PERCENT_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*%")
_COUNT_RE = re.compile(r"\b([0-9]{2,})(?:\s*\+)?\b")


def _infer_kpi(headline: str) -> Tuple[str, str, str]:
    """Infer a (kpi_value, kpi_label, kpi_sub) triple from a story headline.

    Heuristics, in priority order:

    1. Embedded CVE id           -> ("CVE", "ID", "<cve-id>")
    2. CVSS score                -> ("<score>", "CVSS", "severity")
    3. USD amounts ($87M, $3.2B) -> ("$87M", "IMPACT", "estimated")
    4. Percentages (63%)         -> ("63%", "RATIO", "share")
    5. Standalone counts (12k+, 320, 85k) -> ("320", "COUNT", "items")

    Defaults to ("TBD", "STATUS", "NEW") when nothing matches so the L20
    KPI card always renders.
    """
    text = headline or ""
    cve = _CVE_RE.search(text)
    if cve:
        return ("CVE", "ID", cve.group(0).upper()[:18])
    cvss = _CVSS_RE.search(text)
    if cvss:
        return (cvss.group(1), "CVSS", "severity")
    usd = _USD_RE.search(text)
    if usd:
        amount = f"${usd.group(1)}{usd.group(2).upper()}"
        return (amount[:6], "IMPACT", "estimated")
    pct = _PERCENT_RE.search(text)
    if pct:
        return (f"{pct.group(1)}%"[:6], "RATIO", "share")
    cnt = _COUNT_RE.search(text)
    if cnt:
        return (cnt.group(1)[:6], "COUNT", "items")
    return ("TBD", "STATUS", "NEW")


# --- Generator wiring ---
_FILENAME_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})-(.+?)(?:\.svg|\.md)?$")


def _post_url_from_filename(filename: str) -> str:
    """Reconstruct the canonical post URL from a YYYY-MM-DD-Slug.* filename.

    The Jekyll permalink config (`_config.yml`) is
    ``/posts/:year/:month/:day/:title/`` and the ``:title`` placeholder is
    Jekyll's slug derived directly from the filename — i.e. underscores
    are preserved, not converted to hyphens. A previous version of this
    function did ``slug.replace("_", "-")`` which produced a 404 URL in
    every QR code on every weekly digest cover. That bug is fixed here.
    """
    if not filename:
        return "https://tech.2twodragon.com/"
    name = Path(filename).name
    m = _FILENAME_RE.match(name)
    if not m:
        return "https://tech.2twodragon.com/"
    yyyy, mm, dd, slug = m.groups()
    return f"https://tech.2twodragon.com/posts/{yyyy}/{mm}/{dd}/{slug}/"


def _date_str_from_filename(filename: str, fallback: str = "") -> str:
    """Extract the dotted date (YYYY.MM.DD) used in the L20 header bar."""
    name = Path(filename or "").name
    m = _FILENAME_RE.match(name)
    if not m:
        return fallback
    yyyy, mm, dd, _ = m.groups()
    return f"{yyyy}.{mm}.{dd}"


def _build_story(
    *,
    headline: str,
    subheadline: str,
    index: int,
    severity_label: str,
    action: Optional[str] = None,
) -> Dict:
    """Build a complete story dict ready for ``render_l20_hero``."""
    visual = route_visual_id(headline)
    # Theme: prefer visual-driven theme when content suggests it,
    # otherwise fall back to the index rotation.
    theme = _THEME_BY_VISUAL.get(visual, route_theme(str(index)))
    kpi_value, kpi_label, kpi_sub = _infer_kpi(headline)
    # Market-routed bands: a USD figure is a PRICE, not an attack IMPACT.
    # ``_infer_kpi`` is generic and labels any "$71K" as IMPACT/estimated
    # (correct for a breach-cost figure on an attack visual). When the band
    # is routed to the market visual the same figure is a spot price, so
    # relabel here — where both the routed visual_id and the kpi are known —
    # rather than weakening the generic heuristic. Non-market USD KPIs keep
    # their existing IMPACT label.
    if visual == "market" and kpi_label == "IMPACT":
        kpi_label, kpi_sub = "PRICE", "spot"
    story: Dict = {
        "tag": severity_label.upper(),
        "index": f"{index + 1:02d}",
        "theme": theme,
        "visual": visual,
        "headline": headline,
        "subheadline": subheadline,
        "kpi_value": kpi_value,
        "kpi_label": kpi_label,
        "kpi_sub": kpi_sub,
    }
    if action is not None:
        story["action"] = action
    return story


def _action_for(headline: str) -> str:
    """Pick a short, all-caps action tag for the hero story."""
    visual = route_visual_id(headline)
    return {
        "cve_chain": "PATCH UPSTREAM NOW",
        "ransomware_lock": "ISOLATE - RESTORE FROM BACKUP",
        "container_escape": "PIN RUNTIME - REVOKE PRIVS",
        "ai_agent_funnel": "GATE TOOL CALLS - REVIEW LOGS",
        "supply_chain_pipe": "VERIFY SLSA - SIGN ARTIFACTS",
        "code_injection": "ROTATE TOKENS - AUDIT CI",
        "hub_spoke": "BLOCK C2 - SEGMENT NETWORK",
        "data_exfil": "REVOKE TOKENS - ROTATE KEYS",
        # Non-incident visuals: benign, non-alarmist call-to-read tags so the
        # action bar does not assert a security response on neutral content.
        "neutral": "READ THE FULL DIGEST",
        "market": "TRACK THE MARKET TREND",
    }.get(visual, "REVIEW - HARDEN NOW")


def generate_l20_digest_svg(post_info: Dict, output_path: Path) -> bool:
    """Render an L20 Hero+2-Card SVG cover for a Weekly Digest post.

    Mirrors the contract of ``scripts.generate_post_images.generate_l22_digest_svg``:
    accepts a ``post_info`` dict (title / excerpt / filename / content) plus
    an output path, and writes a sanitized SVG. Returns True on success.

    All side-effecting helpers (``validate_and_fix_svg``,
    ``_sanitize_svg_forbidden_chars``) are imported lazily so the module
    can be imported in environments where the heavier
    ``scripts/generate_post_images.py`` module is unavailable (e.g. unit
    tests that monkey-patch the writer).
    """
    try:
        from scripts.lib.svg_l20_hero import render_l20_hero
    except Exception as exc:  # pragma: no cover - defensive import guard
        logging.error(f"L20 hero generator import failed: {exc}")
        return False

    try:
        title = str(post_info.get("title", "") or "")
        excerpt = str(post_info.get("excerpt", "") or "")
        filename = str(post_info.get("filename", "") or output_path.name)

        hero_dict, tr_dict, br_dict = extract_three_stories(title, excerpt, filename)

        hero_story = _build_story(
            headline=hero_dict["headline"],
            subheadline=hero_dict["subheadline"],
            index=0,
            severity_label="HIGH",
            action=_action_for(hero_dict["headline"]),
        )
        tr_story = _build_story(
            headline=tr_dict["headline"],
            subheadline=tr_dict["subheadline"],
            index=1,
            severity_label="HIGH",
        )
        br_story = _build_story(
            headline=br_dict["headline"],
            subheadline=br_dict["subheadline"],
            index=2,
            severity_label="MEDIUM",
        )

        date_str = _date_str_from_filename(
            filename, fallback=str(post_info.get("date", "") or "")
        )
        url = _post_url_from_filename(filename)

        svg = render_l20_hero(
            date_str=date_str or "",
            hero=hero_story,
            top_right=tr_story,
            bottom_right=br_story,
            url=url,
            post_title=title or "Weekly Digest",
        )

        # Optional sanitizers: only used when the heavier module is on the
        # path. Keeps unit tests fast.
        try:
            from scripts.generate_post_images import (  # type: ignore
                _sanitize_svg_forbidden_chars,
                validate_and_fix_svg,
            )

            svg = validate_and_fix_svg(svg)
        except Exception:  # pragma: no cover - sanitizer optional
            _sanitize_svg_forbidden_chars = None  # type: ignore

        output_svg = output_path.with_suffix(".svg")
        output_svg.parent.mkdir(parents=True, exist_ok=True)
        with open(output_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        if _sanitize_svg_forbidden_chars is not None:
            try:
                _sanitize_svg_forbidden_chars(output_svg)
            except Exception:  # pragma: no cover
                pass

        logging.info(f"L20 digest SVG written: {output_svg.name}")
        return True
    except Exception as exc:
        logging.error(f"L20 digest SVG generation failed: {exc}")
        return False
