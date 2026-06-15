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

import html as _html
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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
    # This is the GENUINE-specific-CVE route: a real CVE id (cve-2...), CVSS
    # score, RCE, or a dated 0-day/zero-day. It renders the cve_chain motif
    # (PRIOR CVE -> regression -> NEW CVE), which asserts a concrete patched/
    # exploited flaw — honest ONLY when the post carries such specifics.
    (("cve-2", "cvss", "rce", "patch tuesday", "zero-day", "0-day"), "cve_chain"),
    # Generic security topic of UNSPECIFIED severity -> security_advisory
    # (honest "shield + SEVERITY: TBD" motif, no fabricated specifics). This
    # MUST come AFTER the genuine specific-attack routes above (ransomware,
    # container, supply-chain, code-injection, hub-spoke/botnet, data-exfil)
    # AND after the real-CVE route (cve-2/cvss/rce/0-day -> cve_chain) so a
    # post with a concrete CVE id / exploit still renders the specific motif;
    # and it MUST come BEFORE the neutral default so a bare
    # "Vulnerability"/"Malware"/"CVE"/"Threat" band signals a security topic
    # rather than collapsing to the content-neutral digest motif.
    # NOTE: bare "cve" here matches only AFTER "cve-2"/"cvss" failed above, so
    # a real CVE id keeps cve_chain; "security update"/"advisory" are generic
    # roundup phrasings, not a specific exploit.
    (
        (
            "vulnerability",
            "vuln ",
            "malware",
            "threat",
            "cve",
            "security update",
            "advisory",
        ),
        "security_advisory",
    ),
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
    # Generic security advisory of unspecified severity: amber (caution /
    # attention) — a security topic, but NOT a red-alert active incident.
    "security_advisory": "amber",
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
    result = _shorten(candidate, _SUB_MAX_CHARS) or base
    # Redundant-subtitle guard: when no non-redundant context remained, the
    # subheadline collapses to ``base`` alone, which (for single-keyword
    # Korean-fallback posts) equals the headline -- e.g. headline
    # "Vulnerability" / sub "Vulnerability". A duplicate subtitle reads as a
    # rendering bug, so substitute a non-duplicate descriptor: borrow a sibling
    # band's lead keyword, else a neutral phrase. ASCII-only, length-capped.
    if _clean_segment(result).lower() == base.lower():
        descriptor = ""
        for hl in other_headlines or []:
            cand = _clean_segment(hl)
            if cand and cand.lower() != base.lower():
                descriptor = cand
                break
        if descriptor:
            result = _shorten(f"{base} - {descriptor}", _SUB_MAX_CHARS)
        else:
            result = _shorten(f"{base} - security topic overview", _SUB_MAX_CHARS)
    return result


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


# --- Content-post story extraction ---
# Generic tokens that look like post metadata/structure rather than topic
# content. Filtered when picking headline tokens for content covers so we
# don't surface "Latest", "Update", "Complete" etc. as story headlines.
# Keep this set conservative: only drop tokens that are *never* meaningful
# as standalone headlines; real topic words (AI, Security, ...) are allowed.
_CONTENT_FILLER_TOKENS: frozenset = frozenset({
    "latest", "update", "complete", "guide", "analysis", "perspective",
    "view", "viewing", "from", "and", "the", "a", "of", "for", "with",
    "practical", "best", "tools", "tool", "course", "batch", "week",
    "generation", "model", "top", "y", "overview", "intro", "introduction",
    "summary", "notes", "post", "part", "series", "edition", "review",
    "2025", "2026", "2024", "2023",
})

# Minimum character length for a keyword to count as a meaningful headline
# (avoids keeping single-letter fragments like "A" that slip through after
# case-folding).
_CONTENT_KW_MIN_LEN: int = 2


def _meaningful_content_keywords(
    filename: str,
    title: str = "",
) -> List[str]:
    """Return a deduplicated list of meaningful (non-filler) topic keywords.

    Sources (in priority order):
    1. Individual WORD tokens from an English (non-Hangul) title — filtered
       through ``_CONTENT_FILLER_TOKENS``.
    2. Filename slug keywords — also filtered.

    Deduplication is case-insensitive; the first occurrence's original
    casing is preserved.  Digit-only tokens and tokens shorter than
    ``_CONTENT_KW_MIN_LEN`` are always dropped.

    Returns a list of at most 6 keywords; callers use the first 3 as
    headline tokens and the rest as subheadline context.
    """
    seen_lower: set = set()
    result: List[str] = []

    def _push(token: str) -> None:
        t = token.strip()
        if not t or len(t) < _CONTENT_KW_MIN_LEN:
            return
        if t.isdigit():
            return
        # Drop digit-led alphanumeric tokens (e.g. "8Batch", "6Week", "2nd")
        # — these are course/series ordinals, not meaningful topic words.
        if t[0].isdigit():
            return
        tl = t.lower()
        if tl in _CONTENT_FILLER_TOKENS:
            return
        if tl in seen_lower:
            return
        seen_lower.add(tl)
        result.append(t)

    # 1. English title words (skip if Hangul present — Korean titles are
    #    handled by the filename fallback).
    if title and not _has_hangul(title):
        # Pre-scan for known meaningful compound phrases (e.g. "Top 10",
        # "AI Security") BEFORE individual word filtering so they aren't
        # split into individually-filler tokens. Longer phrases first.
        _COMPOUND_PHRASES_RE = re.compile(
            r"\bTop\s+10\b|\bAI\s+Security\b|\bZero\s+Day\b|\bRed\s+Team\b"
            r"|\bBlue\s+Team\b|\bSupply\s+Chain\b",
            re.IGNORECASE,
        )
        remainder = title
        for m in _COMPOUND_PHRASES_RE.finditer(title):
            if len(result) >= 8:
                break
            phrase = re.sub(r"\s+", " ", m.group().strip())
            _push(phrase)
            # Mark matched span so we skip these words during word-level scan.
            remainder = remainder[:m.start()] + " " * (m.end() - m.start()) + remainder[m.end():]
            # Block each component word individually so the filename slug step
            # (step 2) doesn't re-add "AI" and "Security" after "AI Security"
            # was already pushed as a compound.
            for component in re.findall(r"[A-Za-z0-9]+", phrase):
                seen_lower.add(component.lower())
        for word in re.findall(r"[A-Za-z0-9][A-Za-z0-9+#.-]*", remainder):
            if len(result) >= 8:
                break
            _push(word)

    # 2. Filename slug keywords.
    for kw in _english_topics_from_filename(filename):
        if len(result) >= 8:
            break
        _push(kw)

    return result[:6]


def extract_content_stories(
    post_title: str,
    excerpt: str,
    filename: str = "",
    eyebrow: str = "TECH GUIDE",
) -> Tuple[Dict, Dict, Dict]:
    """Split a content-post title/filename into 3 meaningful English story dicts.

    Unlike :func:`extract_three_stories` (digest variant), this helper:

    * Filters generic filler tokens (``_CONTENT_FILLER_TOKENS``) so words
      like "Latest", "Update", "Complete", "Guide" never become story
      headlines.
    * Builds subheadlines from the OTHER selected topic keywords rather
      than from the (often Korean/filler) excerpt.
    * Falls back to the ``eyebrow`` label (e.g. ``"Security Guide"``)
      when fewer than two non-filler topics are available.

    The English-only guarantee and ``_HEADLINE_MAX_CHARS`` / ``_SUB_MAX_CHARS``
    length caps are preserved identical to :func:`extract_three_stories`.
    """
    meaningful = _meaningful_content_keywords(filename, post_title)

    # eyebrow_title used both for subheadline context and fallback labels.
    eyebrow_title = eyebrow.title()  # "SECURITY GUIDE" -> "Security Guide"

    # Fallbacks: category-themed so a thin slug still reads accurately
    # (e.g. "Cloud Guide overview" rather than "Threat Analysis" on a
    # non-security post). Three distinct variants prevent dedup rejection.
    fallbacks = [
        f"{eyebrow_title} overview",
        f"{eyebrow_title} topics",
        f"{eyebrow_title} reference",
    ]
    # Pad to at least 3 using the fallbacks.
    padded = list(meaningful)
    fb_iter = iter(fallbacks)
    while len(padded) < 3:
        fb = next(fb_iter, f"{eyebrow_title} reference")
        if fb.lower() not in {t.lower() for t in padded}:
            padded.append(fb)

    segments = padded[:3]
    headlines = [_shorten(seg, _HEADLINE_MAX_CHARS) for seg in segments]

    # Build subheadlines from the OTHER two selected topic keywords.
    # ``segments`` is always padded to 3, so ``others`` is always length 2.
    stories: List[Dict] = []
    for i, seg in enumerate(segments):
        others = [h for j, h in enumerate(headlines) if j != i]
        sub_raw = f"{others[0]} - {others[1]}"
        sub = _shorten(sub_raw, _SUB_MAX_CHARS)
        # Redundant-subtitle guard: same rule as _pad_subheadline.
        if _clean_segment(sub).lower() == headlines[i].lower():
            sub = _shorten(f"{headlines[i]} - {eyebrow_title}", _SUB_MAX_CHARS)
        stories.append({"headline": headlines[i], "subheadline": sub})

    return stories[0], stories[1], stories[2]



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


# Visual IDs that are honest for a non-incident content guide post.
# Any visual NOT in this set depicts an active attack or breach motif
# (BYPASS AUTHZ, DATA EXFILTRATION, VICTIM/C2, RANSOM NOTE, ...) and
# must not appear on a beginner guide or overview post.
_CONTENT_HONEST_VISUALS: frozenset = frozenset({
    "neutral",
    "security_advisory",
    "market",
})


def _build_story(
    *,
    headline: str,
    subheadline: str,
    index: int,
    severity_label: str,
    action: Optional[str] = None,
    content_mode: bool = False,
) -> Dict:
    """Build a complete story dict ready for ``render_l20_hero``.

    Args:
        content_mode: when True (content covers), any attack/incident visual
            is clamped to ``"neutral"`` so the cover never shows a breach/C2
            motif on a benign guide post. Digest callers leave this False to
            preserve existing routing.
    """
    visual = route_visual_id(headline)
    # Content covers: downgrade attack visuals to neutral so a guide post
    # about "Kubernetes" never renders the container-escape attack motif.
    if content_mode and visual not in _CONTENT_HONEST_VISUALS:
        visual = "neutral"
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


_ACTION_BY_VISUAL: Dict[str, str] = {
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
    # Generic advisory of unspecified severity: a benign call-to-read, NOT
    # "PATCH NOW" — the post carries no specific CVE/exploit to patch.
    "security_advisory": "READ THE ADVISORY",
}


def _action_for_visual(visual: str) -> str:
    """Action tag for an already-resolved visual id (stays congruent with it)."""
    return _ACTION_BY_VISUAL.get(visual, "REVIEW - HARDEN NOW")


def _action_for(headline: str) -> str:
    """Pick a short, all-caps action tag for the hero story from its headline."""
    return _action_for_visual(route_visual_id(headline))


# --- Real-content extraction (digest covers) ------------------------------
#
# The digest headlines/KPIs were previously filename keywords ("AI", "AWS") +
# a hard-coded ``TBD / STATUS / NEW`` KPI placeholder, so every cover looked
# identical. These helpers surface the post's ACTUAL reported content instead:
# the lead entity of each top story (e.g. "Ivanti EPMM", "Mirai"), the real
# source (The Hacker News, ...), and the real collection counts.
#
# Hard ASCII guarantee: the post headlines are Korean, but the SVG <text>
# quality gate forbids Hangul. Every value produced here is ASCII by
# construction — we extract only Latin entity tokens / CVE ids / digits and
# never emit a Korean string. When no usable ASCII content is found the
# caller keeps the existing filename-keyword behavior, so a thin post still
# renders a valid cover.
#
# Honesty note: these helpers change only the DISPLAYED text + KPI counts.
# The visual builder routing (``route_visual_id``) still keys off the
# filename topic, so the honesty class of every band is unchanged.

# HTML-escape artifacts ("x27" from &#x27;) and generic words that never make a
# distinctive story subject. Lead-entity extraction skips these.
_ENTITY_STOP: frozenset = frozenset({
    "the", "a", "an", "of", "for", "and", "with", "via", "to", "in", "on",
    "at", "by", "from", "new", "be", "your", "own", "can", "into", "over",
    "out", "up", "is", "are", "as", "could", "may", "would", "using", "use",
    "used", "now", "how", "why", "what", "when", "this", "that", "it", "its",
    "has", "have", "was", "were", "but", "not", "you", "we", "they", "all",
    "x27", "x2f", "x3d", "x2c", "x3a", "amp", "quot", "nbsp", "gt", "lt", "apos",
    "mdash", "ndash", "hellip", "rsquo", "lsquo", "rdquo", "ldquo",
})

# Short tokens that ARE meaningful entities despite being <= 3 chars / not
# strictly Capitalized (acronyms that read as proper subjects on a cover).
_ENTITY_ACRONYMS: frozenset = frozenset({
    "ai", "ml", "rce", "rat", "ddos", "iot", "cli", "api", "sap", "aws",
    "gcp", "llm", "mfa", "vpn", "sql", "xss", "csrf", "ssrf", "c2", "k8s",
    "npm", "pip", "ssh", "tls", "dns", "gpt", "ios", "vm", "vms", "ot",
})

# Generic platform / region words that read as a noise *trailing* token on a
# cover ("Showboat Linux" -> "Showboat", "Foo Cloud" -> "Foo"). They are NOT
# distinctive story subjects on their own, so they are dropped from the 2-token
# headline join and rejected as a lone headline.
_GENERIC_TRAILING: frozenset = frozenset({
    "linux", "windows", "android", "ios", "macos", "cloud", "ai", "ml", "api",
    "web", "app", "mena", "apac", "emea",
})

# Weak lead words that pass the acronym/Capitalized filter but make a useless
# headline on their own ("Sorry", a bare "New"/"Report"). Rejected as a lone
# headline; a stronger following entity is preferred.
_WEAK_HEADLINE_WORDS: frozenset = frozenset({
    "sorry", "new", "first", "report", "update", "alert", "week", "summary",
})

# Severity words (the digest body-table impact column). A headline made ENTIRELY
# of these (e.g. "Critical Medium") is a cross-table leak from a risk-summary
# table, never a real story — rejected by _is_good_headline (W4).
_SEVERITY_WORDS: frozenset = frozenset({"critical", "high", "medium", "low"})

# Provably-generic English common nouns / severity words that pass the
# Capitalized/length filter but read as filler on a cover. Consulted ONLY in the
# single-token reject path of _is_good_headline (W3) — NEVER in the two-token
# join-lead path, which would wrongly kill real product names. Place/surname
# detection is intentionally NOT attempted (false-positive risk on real actors).
_WEAK_TRAILING: frozenset = frozenset({"factories"}) | _SEVERITY_WORDS

# Generic capitalized English common words that read as filler bigrams on a
# cover ("Show Option") and as useless lone headlines ("Show"). Consulted ONLY
# in the single-token reject path of _is_good_headline (W3) and in the bigram
# both-generic reject — NEVER for real story subjects. Deliberately EXCLUDES
# real subjects like "strategy" (the MSTR-rebrand entity, a legit lone lead).
#
# Each member is per-word vetted against the live digest corpus
# (scripts/tests/test_l20_realcontent.py::TestGenericHeadlineWordVetting): a word
# is admitted only when it appears as a *lone* filler headline backed by a
# generic source (no real story subject) and never collides with a real-entity
# lone lead. "show"/"option"/"command" all come from the same GeekNews macOS
# keyboard-key line ("Show GN: 오른쪽 Option / Command 키...").
#
# NOT admitted (deferred): adjective-of-"AI" words like "agentic" ("Agentic AI",
# real vendor sources HashiCorp/AWS/NVIDIA) and "vertical" ("Vertical AI"). These
# are NOT clean filler — rejecting the lone adjective yields an empty/degraded
# fallthrough, not a better cover. The adjective+"AI" case needs the dedicated
# stripping rule tracked separately (FM2), not a generic-word reject here.
_GENERIC_HEADLINE_WORDS: frozenset = frozenset({"show", "option", "command"})


def _common_prefix_len(a: str, b: str) -> int:
    """Length of the case-insensitive common leading run of ``a`` and ``b``."""
    n = 0
    for x, y in zip(a.lower(), b.lower()):
        if x != y:
            break
        n += 1
    return n


def _is_good_headline(h: str) -> bool:
    """True iff ``h`` is a presentable, distinctive headline token/phrase.

    A good headline is ASCII-only AND (>= 4 chars OR a CVE id OR a multi-word
    phrase). A SINGLE token additionally must not be a bare acronym
    (``AI``/``VPN``/``npm``), a generic platform/region word (``Linux``,
    ``MENA``), or a weak lead word (``Sorry``, ``New``) — those overclaim
    nothing but read as garbage on a cover.
    """
    h = (h or "").strip()
    if not h or not h.isascii():
        return False
    has_space = " " in h
    if not (len(h) >= 4 or _CVE_RE.match(h) or has_space):
        return False
    if not has_space:
        tl = h.lower()
        if tl in (
            _ENTITY_ACRONYMS
            | _GENERIC_TRAILING
            | _WEAK_HEADLINE_WORDS
            | _WEAK_TRAILING
            | _GENERIC_HEADLINE_WORDS
        ):
            return False
    elif all(t.lower() in _SEVERITY_WORDS for t in h.split()):
        # W4: a multi-word headline made entirely of severity words
        # ("Critical Medium") is a cross-table leak, not a real story.
        return False
    return True


def _entity_tokens(title: str) -> List[str]:
    """Distinctive ASCII entity tokens from a (possibly Korean) headline.

    HTML-unescapes first so ``&#x27;`` does not leak a bogus ``x27`` token.
    Keeps Capitalized words (``Ivanti``, ``Mirai``, ``WhatsApp``), all-caps
    acronyms (``TCLBANKER``, ``RCE``), known short acronyms, and CVE ids — in
    document order. Generic stopwords are dropped. Returns ``[]`` when the
    title carries no usable ASCII entity (e.g. an all-Korean headline).
    """
    text = _html.unescape(title or "")
    out: List[str] = []
    for tok in re.findall(r"[A-Za-z][A-Za-z0-9.+#/-]{1,}", text):
        core = tok.strip(".+#/-")
        tl = core.lower()
        if not core or tl in _ENTITY_STOP:
            continue
        if _CVE_RE.match(tok):
            out.append(tok)
            continue
        # Proper noun / product / all-caps name of >= 3 chars (drops 2-letter
        # fragments like "FA"), OR a known meaningful short acronym ("AI", "C2").
        if (len(core) >= 3 and (tok[0].isupper() or tok.isupper())) or tl in _ENTITY_ACRONYMS:
            out.append(tok)
    return out


def _ascii_word_tokens(s: str) -> set:
    """Lowercased ASCII alphanumeric word tokens of ``s`` (for whole-word
    source-name-echo comparison — not substring)."""
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


# Map a severity cell's emoji marker to an ASCII all-caps severity word. The
# digest highlights table tags each row's impact with a colored dot
# (🔴 critical / 🟠 high / 🟡 medium); anything else is unknown -> "" (the
# cover then OMITS the severity line rather than asserting a fabricated level).
_SEVERITY_BY_EMOJI: Dict[str, str] = {
    "🔴": "CRITICAL",
    "🟠": "HIGH",
    "🟡": "MEDIUM",
}


def _severity_from_marker(cell: str) -> str:
    """ASCII severity word for a table/highlight severity cell, else ``""``."""
    for emoji, word in _SEVERITY_BY_EMOJI.items():
        if emoji in (cell or ""):
            return word
    return ""


def build_lead_headline(title: str) -> str:
    """Lead 1-2 entity-token headline for a (possibly Korean) ``title``.

    Encapsulates the shared headline-resolution logic used by both the L20
    digest panel builder and ``draft_rollup_spec.lead_entity``. Operates on the
    NON-CVE entity tokens of ``title`` and returns ``""`` when nothing resolves
    (the caller then applies its own CVE / source fallback). Carries every
    existing guard verbatim: generic-trailing block, near-dup prefix, length
    cap, the load-bearing ``acronym_product_join`` exception (keeps "AWS KY3P" /
    "npm Worm"), and the ``_is_good_headline`` single-token fallthrough — PLUS a
    both-generic bigram reject so two filler words never form a headline
    ("Show Option"). Combined with the generic-word reject in ``_is_good_headline``
    this keeps lone/paired filler words ("Show", "Option") off the cover.

    Known limitation (deferred): a possessive lead like "Strategy의 Michael
    Saylor" still yields "Strategy Michael" — recovering the person bigram
    "Michael Saylor" would need surname detection, which this module
    deliberately avoids (false-positive risk on real actors; see the wordlist
    comments above).
    """
    toks = _entity_tokens(title)
    non_cve = [t for t in toks if not _CVE_RE.match(t)]
    if not non_cve:
        return ""
    # Lead candidate: first entity, optionally joined with the second token
    # — but never glue a generic platform/region trailing word ("Showboat
    # Linux" -> "Showboat", "Foo MENA" -> "Foo").
    candidate = non_cve[0]
    if (
        len(non_cve) > 1
        and non_cve[1].lower() not in _GENERIC_TRAILING
        # Skip a near-duplicate brand restatement ("ChatGPhish ChatGPT"):
        # a long shared prefix means token 2 just echoes token 1.
        and _common_prefix_len(non_cve[0], non_cve[1]) < 4
        and len(f"{non_cve[0]} {non_cve[1]}") <= _HEADLINE_MAX_CHARS
        # Never join two generic filler words into a useless bigram
        # ("Show Option") — see _GENERIC_HEADLINE_WORDS.
        and not (
            non_cve[0].lower() in _GENERIC_HEADLINE_WORDS
            and non_cve[1].lower() in _GENERIC_HEADLINE_WORDS
        )
    ):
        candidate = f"{non_cve[0]} {non_cve[1]}"
    # Trust the lead candidate only when it is good AND the LEAD token is
    # not itself a generic/weak/acronym word — otherwise a phrase like
    # "Linux Defender" would slip through on the strength of its space.
    #
    # Exception: a known cloud/product ACRONYM (aws, gcp, npm, …) IS a
    # meaningful lead when the second token is a real entity — e.g.
    # "AWS KY3P" is a recognisable vendor+product phrase. In that case
    # keep the joined candidate even though the lead token alone would be
    # flagged as "bad". Only reject the join when the lead is a *generic
    # trailing* or *weak* word (linux, cloud, sorry, etc.).
    lead_token_lower = non_cve[0].lower()
    lead_is_acronym = lead_token_lower in _ENTITY_ACRONYMS
    lead_is_generic = lead_token_lower in (_GENERIC_TRAILING | _WEAK_HEADLINE_WORDS)
    lead_bad = lead_token_lower in (
        _ENTITY_ACRONYMS | _GENERIC_TRAILING | _WEAK_HEADLINE_WORDS
    )
    # Allow "ACRONYM Product" joins (e.g. "AWS KY3P", "npm worm", "GCP
    # IAM") when the second token itself passes _is_good_headline.
    two_token_candidate = " " in candidate
    acronym_product_join = (
        two_token_candidate
        and lead_is_acronym
        and not lead_is_generic  # ios, ai, ml are in BOTH sets → still bad
        and len(non_cve) > 1
        and _is_good_headline(non_cve[1])
    )
    if _is_good_headline(candidate) and (not lead_bad or acronym_product_join):
        return candidate
    # The lead entity is a bare acronym / generic / weak word (e.g.
    # "AI", "Sorry", "Linux"). Scan for the first token that passes,
    # preferring a Capitalized non-acronym over a lone acronym.
    cap = next(
        (t for t in non_cve
         if _is_good_headline(t) and t.lower() not in _ENTITY_ACRONYMS),
        "",
    )
    acro = next((t for t in non_cve if _is_good_headline(t)), "")
    return cap or acro


def _panel_from_source_title(
    src: str, ttl: str, severity: str = ""
) -> Optional[Dict]:
    """Build one ``{headline, subheadline, severity}`` panel from a pair.

    * headline = the lead 1-2 entity tokens (joins multi-word product names
      like ``"Hugging Face"`` when they fit), capped at ``_HEADLINE_MAX_CHARS``.
      CVE ids belong in the subheadline, not the headline, so a leading CVE is
      only used as the headline when the title has no other ASCII entity.
    * subheadline = a CVE id (when present) + the real source attribution,
      e.g. ``"CVE-2026-6973 - The Hacker News"``, capped at ``_SUB_MAX_CHARS``.

    Returns ``None`` when the title carries no usable ASCII entity, so callers
    skip the slot (leaving it on the keyword path) rather than padding it.
    """
    toks = _entity_tokens(ttl)
    if not toks:
        return None
    cve = _CVE_RE.search(_html.unescape(ttl))
    cve_str = cve.group(0).upper() if cve else ""

    headline: str = build_lead_headline(ttl)

    if not headline:
        # No non-CVE entity passed. Prefer a CVE id, then an ASCII source as a
        # last-resort headline (with a neutral descriptor), else give up so the
        # caller keeps the filename-keyword fallback. NEVER emit a lone
        # acronym / generic / weak word as the headline.
        if cve_str:
            headline = cve_str
        elif src and not _has_hangul(src) and src.isascii():
            return {
                "headline": _shorten(src, _HEADLINE_MAX_CHARS),
                "subheadline": "Security advisory",
                "severity": severity,
                # Mark as source-name fallback so _digest_panels can demote
                # this to a side card when a real-entity story is available.
                "_src_fallback": True,
            }
        else:
            return None
    headline = _shorten(headline, _HEADLINE_MAX_CHARS)

    # Don't echo the CVE in the subheadline when it is already the headline
    # (CVE-only highlight) — avoids "CVE-X / CVE-X - source".
    if cve_str and cve_str == headline.upper():
        cve_str = ""
    src_ascii = src if (src and not _has_hangul(src)) else ""
    if cve_str and src_ascii:
        sub = f"{cve_str} - {src_ascii}"
    elif cve_str:
        sub = cve_str
    elif src_ascii:
        sub = src_ascii
    else:
        # No ASCII source / CVE: use a neutral descriptor rather than echoing
        # the headline back (avoids a redundant "APT / APT" band).
        sub = "Security advisory"
    panel = {
        "headline": headline,
        "subheadline": _shorten(sub, _SUB_MAX_CHARS),
        "severity": severity,
    }
    # Source-name echo: a MULTI-word headline whose tokens are WHOLLY contained
    # in the row's source name carries no story information — it just echoes the
    # publication (body-table source "Cloudflare Blog" -> headline "Cloudflare
    # Blog"; "AWS Security Blog" -> "AWS Security"; "Tech World Monitor" ->
    # "World Monitor"). Flag it _src_fallback so the side-card rescue demotes it
    # below real stories. Constraints that protect real subjects:
    #   - require >= 2 tokens: a lone vendor name ("Google", "Meta") may BE the
    #     story subject reported on its own blog, so it is NOT demoted;
    #   - whole-word containment (not substring → "Meta" vs "Metaverse Daily" is
    #     kept); never for a CVE-id headline;
    #   - any headline token NOT in the source (a real co-entity, "CISA Ivanti")
    #     keeps the panel.
    h_tokens = _ascii_word_tokens(headline)
    if (
        len(h_tokens) >= 2
        and h_tokens <= _ascii_word_tokens(src)
        and not _CVE_RE.match(headline)
    ):
        panel["_src_fallback"] = True
    return panel


def _digest_highlight_panels(highlights) -> List[Dict]:
    """Build up to 3 panels from the front-matter ``summary_card.highlights``.

    ``highlights`` is a list of ``{source, title}`` dicts. Highlights with no
    ASCII entity are skipped (not padded). Returns ``[]`` when nothing usable.
    """
    panels: List[Dict] = []
    for h in (highlights or []):
        if len(panels) >= 3:
            break
        if isinstance(h, dict):
            src = str(h.get("source", "") or "")
            ttl = str(h.get("title", "") or "")
            sev = _severity_from_marker(str(h.get("severity", "") or ""))
        else:
            src, ttl, sev = "", str(h or ""), ""
        panel = _panel_from_source_title(src, ttl, sev)
        if panel is not None:
            panels.append(panel)
    return panels


# A digest body carries a markdown highlights table whose rows are
# ``| <category> | <source> | <title> | <severity> |``. This is a SUPERSET of
# summary_card.highlights (one row per collected item), so it backfills panels
# for thin posts whose summary_card yields < 3 ASCII-usable highlights, and is
# the real-content source on the cron path (which has the full body but no
# parsed summary_card dict). The header/separator rows are skipped.
_DIGEST_TABLE_ROW_RE = re.compile(r"^\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|\s*$", re.MULTILINE)
_DIGEST_TABLE_SKIP_RE = re.compile(r"분야|소스|핵심\s*내용|^[\s:\-]+$")

# W1 anchor: the digest highlights table opens with a (category, source) header
# — current "분야 | 소스 | 핵심 내용 | 영향도" or the legacy "카테고리 | 출처 |
# 주요 발견 | 영향도". Parsing is scoped to the contiguous rows AFTER this header,
# so secondary body tables (risk summary, component, "대응 긴급도", reference /
# regulation tables whose col1 is 이슈/출처/제목/기관) are excluded structurally —
# regardless of their columns. This keeps cross-table garbage like "Critical
# Medium" out of the candidate pool WITHOUT a category allowlist (the highlights
# table legitimately uses 8+ categories incl. Korean labels: Security/AI/Cloud/
# DevOps/Blockchain/Tech/FinOps/보안/클라우드/…, which an allowlist would drop).
_DIGEST_TABLE_HEADER_RE = re.compile(r"^\|\s*(?:분야|카테고리)\s*\|\s*(?:소스|출처)\s*\|")

# W2: Blockchain / Tech rows are off-topic FILLER for a security digest; rank
# them below on-topic (Security/AI/Cloud/DevOps/…) backfill. The English stems
# are letter-boundary anchored so on-topic labels that merely CONTAIN them
# ("FinTech", "Biotech") are NOT demoted. (1 = filler / lower priority, 0 = on-topic.)
_FILLER_CATEGORY_RE = re.compile(
    r"(?<![a-z])(?:blockchain|tech)(?![a-z])|블록체인|기술", re.IGNORECASE
)


def _category_rank(col1: str) -> int:
    """0 for an on-topic security category, 1 for Blockchain/Tech filler (W2)."""
    return 1 if _FILLER_CATEGORY_RE.search(col1 or "") else 0


def _digest_table_panels(content: str, limit: int = 3) -> List[Dict]:
    """Build up to ``limit`` panels from the digest body **highlights table**.

    W1: parsing is anchored to the highlights table — the contiguous
    ``| category | source | title | severity |`` rows following the
    ``| 분야 | 소스 | … |`` header, stopping at the first non-table line. This
    excludes every secondary body table (risk summary, component, "대응 긴급도")
    so their rows can never leak a garbage panel (e.g. "Critical Medium").

    Reuses :func:`_panel_from_source_title`, so rows with no ASCII entity in the
    title are skipped. Each panel is tagged with ``_category_rank`` (W2) so the
    caller can demote Blockchain/Tech filler below on-topic security stories.
    Returns ``[]`` when the highlights table is absent or carries no usable row.

    The default ``limit=3`` matches the visible slot count; :func:`_digest_panels`
    passes a larger ``limit`` so the candidate pool is deep enough to backfill a
    source-name fallback with a *real-entity* story (side-card rescue).
    """
    panels: List[Dict] = []
    in_table = False
    for line in (content or "").splitlines():
        if not in_table:
            if _DIGEST_TABLE_HEADER_RE.match(line):
                in_table = True
            continue
        m = re.match(r"^\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|\s*$", line)
        if not m:
            break  # blank / non-table line ends the highlights table
        if len(panels) >= limit:
            break
        col1, source, title, col4 = (c.strip() for c in m.groups())
        if set(col1) <= set("-: "):  # |---|---| separator row
            continue
        if not source or set(col4) <= set("-: "):
            continue
        panel = _panel_from_source_title(source, title, _severity_from_marker(col4))
        if panel is not None:
            panel["_category_rank"] = _category_rank(col1)  # W2 backfill rank
            panels.append(panel)
    return panels


# Body markers for the digest collection-stats block. Korean anchors are used
# only to LOCATE the digit — the rendered value is the ASCII number itself.
_DIGEST_TOTAL_RE = re.compile(r"총\s*뉴스\s*수\*{0,2}\s*[:：]\s*(\d{1,4})")
_DIGEST_SECURITY_RE = re.compile(r"보안\s*뉴스\*{0,2}\s*[:：]\s*(\d{1,4})")


def _digest_stats(content: str) -> Dict[str, Optional[int]]:
    """Extract real collection counts (total / security) from a digest body.

    Returns ``{"total": int|None, "security": int|None}``. ``None`` when the
    marker is absent so the caller keeps the inferred KPI.
    """
    text = content or ""

    def _grab(rx: re.Pattern) -> Optional[int]:
        m = rx.search(text)
        return int(m.group(1)) if m else None

    return {"total": _grab(_DIGEST_TOTAL_RE), "security": _grab(_DIGEST_SECURITY_RE)}


def _rescue_hero(panels: List[Dict]) -> List[Dict]:
    """Promote the best real-entity story to the hero slot when the natural hero
    is a source-name fallback (e.g. "The Hacker News") and a more informative
    story is available in the side cards.

    Trigger condition (all must be true):
    - panels[0] has ``_src_fallback=True`` (headline == ASCII source name)
    - At least one of panels[1:] does NOT have ``_src_fallback=True``

    Promotion is targeted: we pick the side-card story with the best real entity
    (prefer stories with a known severity; among equals, prefer the longer
    headline as a proxy for specificity) and swap it into slot 0. The demoted
    source-name story fills the vacated side-card slot.

    If ALL panels are source-name fallbacks, or panels[0] already has a real
    entity, return the list unchanged — no blind reshuffling.

    This is honesty-neutral: visual routing follows the headline (unchanged by
    this swap), all digest stories route only to always-honest classes, and the
    scorer's :func:`resolve_digest_band_visuals` calls :func:`_digest_panels`
    which calls this same function, so path-a stays byte-identical to path-b.
    """
    if not panels or not panels[0].get("_src_fallback"):
        return panels

    # Find the best non-source-fallback candidate from the side cards.
    # Primary tiebreaker: severity (CRITICAL > HIGH > MEDIUM > unknown).
    # Secondary tiebreaker: editorial rank (lower index wins, i.e. the story
    # that appeared first in the highlights is considered more newsworthy).
    _SEV_RANK = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "": 0}

    best_idx: Optional[int] = None
    best_sev: int = -1
    for i, p in enumerate(panels[1:], start=1):
        if p.get("_src_fallback"):
            continue
        sev_score = _SEV_RANK.get((p.get("severity") or "").upper(), 0)
        # Prefer higher severity; among equal severity, the first real-entity
        # story wins (lower index = earlier editorial rank). Since we iterate
        # left-to-right and only update on strict improvement, the first
        # equal-severity story is kept automatically.
        if sev_score > best_sev:
            best_sev = sev_score
            best_idx = i

    if best_idx is None:
        # All side cards are also source fallbacks; keep original order.
        return panels

    # Swap: bring the best real-entity story to slot 0, demote the
    # source-name story to the vacated position.
    result = list(panels)
    result[0], result[best_idx] = result[best_idx], result[0]
    return result


# Candidate-pool depth for body-table backfill. 2x the 3 visible slots so the
# pool survives dedup (rows that re-state a highlight) and source-name-fallback
# skips and can still yield 3 real-entity stories for the side-card rescue.
_BACKFILL_POOL = 6


def _digest_panels(summary_card, content: str) -> List[Dict]:
    """The ordered real-content panels for a digest, lead story first.

    summary_card.highlights (editorially ranked) first, then body-table backfill
    (a superset, for thin posts / the cron path), deduped by headline. A
    source-name fallback (``_src_fallback`` — headline == bare source name) is
    kept OUT of the 3 visible slots whenever a real-entity story is available:
    real-entity panels fill the slots first (in editorial order), and a fallback
    occupies a slot only once the reals are exhausted (so the cover never goes
    blank). The hero is therefore the editorial-lead real story.

    Single source of truth shared by the generator override and the honesty
    scorer's routing replay, so both agree on the band visuals. The rescue is
    honesty-neutral: digest stories route only to always-honest classes, so
    surfacing a different (real) story cannot introduce an overclaim.
    """
    highlights = summary_card.get("highlights") if isinstance(summary_card, dict) else None
    hl_panels = _digest_highlight_panels(highlights)
    table_panels = _digest_table_panels(content or "", limit=_BACKFILL_POOL)
    # W2: rank the body-table BACKFILL by category (Security ahead of
    # Blockchain/Tech filler), stable by document order. Editorial highlights
    # are NOT reordered — they are curated/ranked already and always precede the
    # backfill, so category ranking never demotes a lead story.
    table_panels = [
        p for _, p in sorted(
            enumerate(table_panels),
            key=lambda ip: (ip[1].get("_category_rank", 0), ip[0]),
        )
    ]
    # Dedupe candidates by headline, keeping the first (highest-ranked) one.
    seen: Set[str] = set()
    candidates: List[Dict] = []
    for p in hl_panels + table_panels:
        key = p["headline"].lower()
        if key in seen:
            continue
        seen.add(key)
        candidates.append(p)
    # Real-entity stories first (editorial order preserved), source-name
    # fallbacks last — generalises hero rescue to EVERY visible slot.
    real = [p for p in candidates if not p.get("_src_fallback")]
    fallback = [p for p in candidates if p.get("_src_fallback")]
    panels = (real + fallback)[:3]
    # Defence-in-depth: the partition already places any real story ahead of a
    # fallback, so panels[0] is a fallback only when NO real story exists — in
    # which case _rescue_hero is a no-op. Retained for symmetry / safety should
    # the partition ever be relaxed.
    panels = _rescue_hero(panels)
    return panels


# Visuals a band may assert when routed FROM REAL STORY CONTENT (a one-line
# headline). ONLY the always-honest classes are allowed: a content headline
# routes by KEYWORD, but an attack-class builder asserts a specific incident
# whose honesty the gate verifies against an EVIDENCE TOKEN in the post body —
# and a headline entity is NOT the same thing as that body token. Routing
# "APT36/SideCopy RAT" to hub_spoke (C2/botnet) when the body lacks a c2/botnet
# token, or "Ivanti CVE-…" to cve_chain ("CVE REGRESSION CHAIN") from a single
# CVE, both OVERCLAIM and FAIL the honesty gate. Since digests auto-publish via
# cron (unattended), any attack-class content route is DOWNGRADED to the honest
# weaker ``security_advisory`` ("advisory, severity unassessed", always_pass) —
# congruent with a security headline, guaranteed to never overclaim or FAIL.
# Mirrors the ``content_mode`` clamp in ``_build_story`` + the 2026-06-02
# cve_chain default removal. See .omc/plans/l20-panel-visual-desync.md.
_DIGEST_CONTENT_HONEST: frozenset = frozenset({"neutral", "market", "security_advisory"})


def _honest_content_visual(visual_id: str) -> str:
    """Clamp a content-routed visual to an always-honest class.

    Always-honest classes (``neutral`` / ``market`` / ``security_advisory``)
    pass through; every attack-class route is downgraded to ``security_advisory``
    so a one-line headline never asserts an incident the post body does not
    establish (no overclaim, and the honesty gate can never FAIL on it).
    """
    return visual_id if visual_id in _DIGEST_CONTENT_HONEST else "security_advisory"


def resolve_digest_band_visuals(
    title: str,
    excerpt: str,
    filename: str,
    content: str,
    summary_card,
) -> List[str]:
    """Return the FINAL 3 band visuals for a digest cover (content-aware).

    A band whose displayed headline comes from a real story is routed from THAT
    story's entity (so the icon matches the headline — e.g. a 'Mirai' botnet
    headline gets the hub_spoke/C2 motif, not the filename keyword's
    ransomware_lock). A band with no real panel keeps its filename-keyword
    routing.

    This is the lockstep source of truth: the generator (``_apply_real_content``)
    sets ``story['visual']`` from it, and the honesty scorer's routing-replay
    (``_routed_visual_ids``) calls it too, so on-disk visuals and scored intent
    never diverge (no spurious STALE_RENDER).
    """
    h, tr, br = extract_three_stories(title, excerpt, filename)
    visuals = [
        route_visual_id(h["headline"]),
        route_visual_id(tr["headline"]),
        route_visual_id(br["headline"]),
    ]
    panels = _digest_panels(summary_card, content)
    for i in range(min(3, len(visuals))):
        if i < len(panels) and panels[i] is not None:
            p = panels[i]
            visuals[i] = _honest_content_visual(
                route_visual_id(f"{p['headline']} {p['subheadline']}")
            )
    return visuals


def _apply_real_content(
    stories: List[Dict],
    post_info: Dict,
) -> None:
    """Override displayed headline/subheadline/visual/KPI from real post content.

    Mutates ``stories`` (hero, top_right, bottom_right) in place:
    - headline/subheadline ← the real story (lead story stays on the hero);
    - ``visual`` ← re-routed from the real headline so the icon matches the
      story (Approach B — fixes the filename-keyword icon/headline desync);
      ``theme`` follows the new visual and the hero ``action`` is recomputed;
    - KPI ← real collection counts.

    Honesty stays intact: the new visual is routed from an entity that comes
    FROM the post, so its claim class still has matching post evidence. The
    scorer replays the identical routing via :func:`resolve_digest_band_visuals`.
    Bands with no real panel keep their filename-keyword visual untouched.
    """
    content = str(post_info.get("content", "") or "")
    panels = _digest_panels(post_info.get("summary_card"), content)
    for i, story in enumerate(stories):
        if i < len(panels) and panels[i] is not None:
            panel = panels[i]
            story["headline"] = panel["headline"]
            story["subheadline"] = panel["subheadline"]
            # Real per-story severity (ASCII word) for the advisory gauge; ""
            # when unknown so the renderer OMITS the severity line (no "TBD").
            story["severity"] = panel.get("severity", "")
            # Re-route the visual (+ theme, + hero action) to the real story,
            # clamped to an honest, non-overclaiming class.
            new_visual = _honest_content_visual(
                route_visual_id(f"{panel['headline']} {panel['subheadline']}")
            )
            story["visual"] = new_visual
            story["theme"] = _THEME_BY_VISUAL.get(new_visual, story.get("theme", "blue"))
            if "action" in story:
                # Follow the RESOLVED visual (not the raw headline) so a
                # downgraded band shows "READ THE ADVISORY", not "PATCH NOW".
                story["action"] = _action_for_visual(new_visual)

    stats = _digest_stats(content)
    # KPI cards live on the two right panels (index 1, 2). Replace the
    # placeholder ``TBD / STATUS / NEW`` with real counts when available.
    if len(stories) > 1 and stats.get("total"):
        stories[1]["kpi_value"] = str(stats["total"])
        stories[1]["kpi_label"] = "ITEMS"
        stories[1]["kpi_sub"] = "24h feed"
    if len(stories) > 2 and stats.get("security") is not None:
        stories[2]["kpi_value"] = str(stats["security"])
        stories[2]["kpi_label"] = "SECURITY"
        stories[2]["kpi_sub"] = "flagged"


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
        from scripts.lib.svg_l20_hero import build_cover_title, render_l20_hero
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

        # Surface the post's REAL reported content (lead story entities, real
        # source attribution, real collection counts) over the generic
        # filename-keyword text + ``TBD`` KPI placeholders. Visual routing /
        # theme / action are left untouched, so the honesty class is unchanged.
        _apply_real_content([hero_story, tr_story, br_story], post_info)

        date_str = _date_str_from_filename(
            filename, fallback=str(post_info.get("date", "") or "")
        )
        url = _post_url_from_filename(filename)

        # Build a clean, ASCII, a11y-friendly cover <title> instead of feeding
        # the raw Korean post title through the Hangul stripper (which left
        # malformed boilerplate like "2026 05 29 AI (29 )" — orphaned slug
        # fragments + a dangling "(N )" count). Derives cadence + topic from
        # the title / category / filename; date from the dotted header date.
        cover_title = build_cover_title(
            post_title=title,
            date_str=date_str or "",
            category=str(post_info.get("category", "") or ""),
            filename=filename,
        )

        svg = render_l20_hero(
            date_str=date_str or "",
            hero=hero_story,
            top_right=tr_story,
            bottom_right=br_story,
            url=url,
            post_title=cover_title or "Weekly Tech Digest",
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


# --- Content-post (non-digest) L20 cover ----------------------------------

# Category -> honest eyebrow label (ASCII, all-caps). Default "TECH GUIDE".
_CONTENT_EYEBROW_BY_CATEGORY: Dict[str, str] = {
    "security": "SECURITY GUIDE",
    "devsecops": "DEVSECOPS GUIDE",
    "devops": "DEVOPS GUIDE",
    "cloud": "CLOUD GUIDE",
    "kubernetes": "KUBERNETES GUIDE",
    "finops": "FINOPS GUIDE",
    "blockchain": "BLOCKCHAIN GUIDE",
    "incident": "INCIDENT REPORT",
}

# Title-cased footer label per eyebrow (deterministic, ASCII).
_CONTENT_FOOTER_BY_EYEBROW: Dict[str, str] = {
    "SECURITY GUIDE": "Security Guide",
    "DEVSECOPS GUIDE": "DevSecOps Guide",
    "DEVOPS GUIDE": "DevOps Guide",
    "CLOUD GUIDE": "Cloud Guide",
    "KUBERNETES GUIDE": "Kubernetes Guide",
    "FINOPS GUIDE": "FinOps Guide",
    "BLOCKCHAIN GUIDE": "Blockchain Guide",
    "INCIDENT REPORT": "Incident Report",
    "TECH GUIDE": "Tech Guide",
}


def _content_eyebrow_from_category(category) -> str:
    """Map a post ``category`` (str / list / comma string) to an eyebrow label.

    Uses the first token when ``category`` is a list or comma-separated string.
    Returns ``"TECH GUIDE"`` for unknown / empty categories.
    """
    token = ""
    if isinstance(category, (list, tuple)):
        token = str(category[0]) if category else ""
    else:
        token = str(category or "")
        if "," in token:
            token = token.split(",", 1)[0]
    token = token.strip().lower()
    return _CONTENT_EYEBROW_BY_CATEGORY.get(token, "TECH GUIDE")


def generate_l20_content_svg(post_info: Dict, output_path: Path) -> bool:
    """Render an L20 Hero+2-Card SVG cover for a NON-digest content post.

    Mirrors :func:`generate_l20_digest_svg` but renders an honest, category-
    appropriate cover for Korean technical guides instead of the hardcoded
    "WEEKLY DIGEST" branding. The eyebrow / footer / hero CTA are derived from
    the post ``category``; story text reuses the same English-only
    ``extract_three_stories`` + ``_build_story`` pipeline (filename-keyword
    fallback) so the ``check_svg_quality`` Hangul gate stays satisfied.

    Returns True on success, False on failure (identical contract to the
    digest variant).
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

        eyebrow = _content_eyebrow_from_category(post_info.get("category", ""))
        footer_label = _CONTENT_FOOTER_BY_EYEBROW.get(eyebrow, "Tech Guide")
        hero_action = (
            "READ THE FULL REPORT"
            if eyebrow == "INCIDENT REPORT"
            else "READ THE FULL GUIDE"
        )

        # Use the content-specific extractor (filler-filtered, topic-aware
        # subheadlines) instead of the digest extractor so generic tokens
        # like "Latest", "Update", "Complete" never become story headlines.
        hero_dict, tr_dict, br_dict = extract_content_stories(
            title, excerpt, filename, eyebrow=eyebrow
        )

        hero_story = _build_story(
            headline=hero_dict["headline"],
            subheadline=hero_dict["subheadline"],
            index=0,
            severity_label="HIGH",
            action=hero_action,
            content_mode=True,
        )
        tr_story = _build_story(
            headline=tr_dict["headline"],
            subheadline=tr_dict["subheadline"],
            index=1,
            severity_label="HIGH",
            content_mode=True,
        )
        br_story = _build_story(
            headline=br_dict["headline"],
            subheadline=br_dict["subheadline"],
            index=2,
            severity_label="MEDIUM",
            content_mode=True,
        )

        date_str = _date_str_from_filename(
            filename, fallback=str(post_info.get("date", "") or "")
        )
        url = _post_url_from_filename(filename)

        # Honest, ASCII-only cover <title>: "<Footer Label> - <date>" instead of
        # the digest "...Digest" wording so the a11y/<title> text is accurate
        # for a content guide. Falls back to the footer label when no date.
        cover_title = f"{footer_label} - {date_str}" if date_str else footer_label

        svg = render_l20_hero(
            date_str=date_str or "",
            hero=hero_story,
            top_right=tr_story,
            bottom_right=br_story,
            url=url,
            post_title=cover_title,
            eyebrow=eyebrow,
            footer_label=footer_label,
        )

        # Optional sanitizers: only used when the heavier module is on the
        # path. Keeps unit tests fast.
        _sanitize_svg_forbidden_chars = None
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

        logging.info(f"L20 content SVG written: {output_svg.name}")
        return True
    except Exception as exc:
        logging.error(f"L20 content SVG generation failed: {exc}")
        return False
