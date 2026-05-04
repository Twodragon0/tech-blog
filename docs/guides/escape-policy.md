# Escape policy: which sink, which encoding

**Last updated:** 2026-05-04

The auto-publish pipeline (`scripts/news/content_generator.py`) injects
upstream news headlines and AI-generated text into three different parsers
in the same generated post. Each parser has its own grammar; mixing the
encodings up has produced silent build failures (Jekyll skipping a post)
and broken image renders in the past.

This page is the canonical reference for which encoding to use where.
**One rule:** values get encoded once, *at the boundary between the
generator and the sink* — never inside the data pipeline itself.

## The three sinks

| # | Sink | Helper | Maps |
|---|---|---|---|
| 1 | **YAML scalar** (post frontmatter) | `_yaml_escape_dq` | `\` → `\\`, then `"` → `\"` |
| 2 | **HTML attribute** (Liquid `{% include %}` arg) | `_html_escape_quotes` | `&` → `&amp;`, `"` → `&quot;`, `'` → `&#x27;` |
| 3 | **SVG `<text>` element** | `_escape_svg_text` | `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#39;` |

The helpers all live in `scripts/news/content_generator.py` (or
`scripts/news/svg_generator.py` for #3), keep them imported from there
rather than reinventing per file.

## When to use which

### 1) YAML scalar — frontmatter

```yaml
---
title: "{{ value }}"
excerpt: "{{ value }}"
---
```

The Jekyll YAML parser terminates a double-quoted scalar at the first
unescaped `"`. **Korean post-quoted phrases like `"Sorry"` and `"퇴행적"`
flow straight through translation and break the scalar.** When that
happens Jekyll silently skips the entire post:

```
YAML Exception ... did not find expected key while parsing a block
mapping at line 2 column 1
```

The fix is `_yaml_escape_dq`: `\` first (so we don't double-escape
backslashes added later for `"`), then `"`.

**Apply to**: `title`, `excerpt`, `description`, `image_alt`, and any
other free-text frontmatter field.

### 2) HTML attribute — Liquid include args

```liquid
{% include ai-summary-card.html
  title="{{ value }}"
  ...
%}
```

The Liquid parser terminates a double-quoted attribute on the first
unescaped `"`. Single quotes break the same way in `'…'` form. The
blast radius is smaller than YAML because Jekyll only fails the
include, not the post — but the rendered card breaks visually.

The fix is `_html_escape_quotes`: HTML entity encode all four risky
characters at once. Order matters: `&` first so existing entities don't
get double-escaped into `&amp;quot;` etc.

**Apply to**: every value injected into a Liquid `include` attribute,
HTML attribute, or anywhere else where HTML entities are decoded for
you by the consumer (i.e. browsers and Liquid).

### 3) SVG `<text>` — banner / cover graphics

```xml
<text x="60" y="120">{{ value }}</text>
```

SVG is XML, so the parser cares about `<` and `>` as well as the quote
characters. An unescaped `<` cuts the `<text>` content short and the
SVG either renders garbled or fails to parse altogether. CI's SVG XML
well-formedness gate catches this before commit, but only if the
generator escapes correctly.

The fix is `_escape_svg_text`: full XML entity set. **In addition**,
`_to_english_svg_text` strips non-ASCII letters because the SVG cover
templates only embed Latin-script fonts — Korean text inside `<text>`
nodes would render as tofu boxes.

**Apply to**: every dynamic value emitted inside an SVG element body,
including `<title>`, `<text>`, `<desc>`, and any attribute that contains
text content (`aria-label="..."`, `data-*="..."`).

## Anti-patterns

- **HTML entities into YAML.** A `&quot;` in a YAML title shows up as
  the literal six characters in the rendered page — readers see
  "&quot;Sorry&quot;" instead of "\"Sorry\"". HTML entity encoding
  belongs only in the HTML / Liquid / SVG sinks, never in YAML.
- **Single-pass escape across multiple sinks.** Don't try to construct
  an escape that satisfies all three at once — there's no single
  encoding that's safe for both YAML scalars (which want backslashes)
  and HTML/SVG (which want entities). Keep the value untouched in the
  builder, encode at the sink.
- **Hand-coding `.replace('"', '\\"')`.** Use the helpers; they centralize
  the escape order (backslash before quote, ampersand before
  quote-as-entity) so a future contributor can't get the order wrong
  in copy-paste.

## Real failure modes (history)

| Date | Sink | Symptom | Fix |
|---|---|---|---|
| 2026-05-03 | YAML | Whole post skipped: "did not find expected key while parsing block mapping" | PR #349 — `_yaml_escape_dq` |
| (ongoing) | HTML | Liquid include rendered with truncated arg when title contains `'` | `_html_escape_quotes` |
| (CI gate) | SVG | Pre-commit hook fails: "not well-formed XML" | `_escape_svg_text` + `_to_english_svg_text` |

## When adding a new field

1. Identify the **destination sink** of the rendered output:
   - `_posts/*.md` frontmatter → YAML
   - `<picture>` / `<source>` / Liquid `include` arg → HTML attribute
   - `assets/images/*.svg` `<text>` → SVG/XML
2. Pick the matching helper from the table above.
3. Wrap the value at the single point where it crosses into the sink:
   `f'title: "{_yaml_escape_dq(value)}"'`, not deeper in the builder.
4. Add a regression test that round-trips an adversarial input through
   the relevant parser (`yaml.safe_load`, `xml.etree.ElementTree.fromstring`,
   etc.). See `scripts/tests/test_blogwatcher_yaml_escape.py` for the
   shape that's worked well in this repo.
