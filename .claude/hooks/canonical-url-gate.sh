#!/bin/bash
# canonical-url-gate.sh — warn when a Liquid template emits the canonical
# anti-pattern that broke GSC indexing (commit 312faeb5, 2026-05-06).
#
# `{{ ... | absolute_url }}` and `{{ site.url }}{{ site.baseurl }}{{ ... }}`
# both prepend site.baseurl. On the GH Pages backup the build runs with
# `--baseurl "/tech-blog"` so they emit https://tech.2twodragon.com/tech-blog/...
# which 404s on Vercel — Google then drops the page from the index.
#
# Files that emit canonical / share / sitemap URLs MUST use
# `{{ site.url }}{{ page.url }}` (or equivalent without site.baseurl).
# Asset paths (favicon, RSS link, same-origin <img>) keep `relative_url`.
#
# This hook is advisory: it prints a warning and returns 0, so it doesn't
# block legitimate work — but every PR review and CI gate should treat
# the warning as a blocker.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only inspect templates that produce SEO/share metadata or sitemap entries.
case "$FILE_PATH" in
  */head.html|*/sitemap.xml|*/feed.xml|*/llms.txt|*/llms-full.txt) ;;
  *) exit 0 ;;
esac

[ -f "$FILE_PATH" ] || exit 0

# Match lines that BOTH (a) emit a SEO/share URL, AND (b) use the
# baseurl-leaking patterns. Skip Liquid comments {%- comment -%} blocks
# and HTML comments <!-- ... --> since those are documentation, not code.
PATTERNS_FOUND=$(awk '
  /\{%-? *comment/,/\{%-? *endcomment/ { next }
  /<!--/,/-->/ { next }
  /(canonical|og:url|og:image|<loc>|share_url|<image:loc>)/ && (/\| *absolute_url/ || /site\.baseurl/) {
    print NR ": " $0
  }
' "$FILE_PATH" 2>/dev/null || true)

if [ -n "$PATTERNS_FOUND" ]; then
  cat >&2 <<MSG
[canonical-url-gate] WARNING: $FILE_PATH may emit baseurl-prefixed canonical URLs.

Lines using \`absolute_url\` or \`site.baseurl\` near canonical/og/sitemap fields:
$PATTERNS_FOUND

These prepend site.baseurl (= /tech-blog/ on the GH Pages backup), producing
URLs like https://tech.2twodragon.com/tech-blog/... that 404 on Vercel and
caused GSC to drop pages from the index in the past.

Use \`{{ site.url }}{{ page.url }}\` (no site.baseurl) for canonical/share/
sitemap URLs. Keep \`relative_url\` for same-origin asset paths.

See notes/seo-canonical-fix.md for the regression history.
MSG
fi
exit 0
