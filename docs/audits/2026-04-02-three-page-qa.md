# 2026-04-02 Three-Page QA Audit

Date: 2026-04-02
Scope:
- `https://tech.2twodragon.com/tags/`
- `https://tech.2twodragon.com/archive/`
- `https://tech.2twodragon.com/discussion/`

## Summary

This audit covered visual QA for dark mode on the three public pages above, Lighthouse checks for performance and accessibility, and a lightweight repository-level validation pass.

No repository code was changed during the audit itself. This document records the findings and recommended follow-up work.

## Visual QA

Observed on dark-mode captures:
- All three pages render without catastrophic layout breakage.
- `/tags/` has poor tag-cloud readability in dark mode because multiple tags and counts fall below comfortable contrast.
- `/archive/` is structurally stable, but category badges and linked post titles are low-contrast in dark mode.
- `/discussion/` is structurally stable, but category cards, CTA text, and some footer toolbar text have contrast issues.
- The bottom floating toolbar overlays content near the viewport bottom on mobile-sized captures.

Limitation:
- Automated light-mode visual capture hit a Vercel security checkpoint in headless mode, so visual evidence was strongest for dark mode. Theme toggle logic still exists in the client runtime.

## Lighthouse Scores

### `/tags/`
- Performance: 59
- Accessibility: 92
- Best Practices: 92
- SEO: 100
- FCP: 4.8s
- LCP: 6.6s
- TBT: 270ms
- CLS: 0

Key findings:
- Console error from CSP blocking an inline script on the page.
- Low contrast in the tag cloud.
- Label-content-name mismatch on header logo and repeated "Top" links.
- Tag search input has insufficient touch target size.
- Unused CSS and JS are materially inflating payload size.

### `/archive/`
- Performance: 66
- Accessibility: 96
- Best Practices: 96
- SEO: 100
- FCP: 4.7s
- LCP: 6.3s
- TBT: 0ms
- CLS: 0.014

Key findings:
- Low contrast on category badges and archive item links.
- Label-content-name mismatch on the header logo.
- Console noise from a 403 on the AdSense script request.
- Unused CSS and JS remain a notable performance cost.

### `/discussion/`
- Performance: 67
- Accessibility: 88
- Best Practices: 96
- SEO: 100
- FCP: 4.6s
- LCP: 6.0s
- TBT: 50ms
- CLS: 0

Key findings:
- Invalid ARIA structure: `role="listitem"` is used without a required list parent.
- Heading order issue in the guidelines section.
- Low contrast on category cards, CTA, and footer-adjacent controls.
- Label-content-name mismatch on the header logo, category cards, and CTA.
- Console noise from a 403 on the AdSense script request.

## Code-Level Findings

### 1. CSP blocks the tag page inline script

The tag filtering script is inline in `tags.html:94`, but the deployed CSP in `vercel.json:33` does not include its current hash. Lighthouse reported the missing hash as:

- `sha256-pLGGqf6DwwoYaV/szjoTzBxwbkMNQbefVp0UoU1xYdc=`

Impact:
- Tag filtering can be broken in production even though the UI control is visible.

Recommended fix:
- Move the script into a static asset, or update CSP hashes as part of the deployment path.

### 2. Accessible names do not match visible labels

Examples:
- Header logo in `_includes/header.html:5`
- Tag section back-to-top links in `tags.html:83`
- Discussion category cards in `discussion.html:48`
- Discussion CTA in `discussion.html:211`

Impact:
- Screen reader and voice-control users get names that do not reflect visible text.

Recommended fix:
- Align `aria-label` values with visible copy, or rely on visible text where no override is needed.

### 3. Discussion ARIA and heading semantics need repair

Relevant locations:
- `discussion.html:95`
- `discussion.html:96`
- `discussion.html:127`

Impact:
- Lighthouse accessibility score drops and assistive-technology navigation becomes less reliable.

Recommended fix:
- Add a list container role or switch to semantic list markup.
- Change guideline headings so the section does not jump from `h2` to `h4`.

### 4. Dark-mode contrast is still below target in several components

Relevant style locations:
- `_sass/_tags.scss:127`
- `_sass/_tags.scss:366`
- `_sass/_archive.scss:439`
- `_sass/_discussion.scss:126`
- `_sass/_discussion.scss:373`

Impact:
- Readability regresses most noticeably on `/tags/` and `/discussion/`.

Recommended fix:
- Raise contrast for dark-mode text and badge/link combinations before further visual polish.

## Repository Validation

Verification commands run:

```bash
bundle exec jekyll build --destination /tmp/tech-blog-audit-site
python3 scripts/check_posts.py
```

Results:
- Jekyll build completed successfully.
- `check_posts.py` completed successfully but reported many asset-quality warnings.
- 66 post files emitted issue summaries.
- 65 SVG assets were flagged as "text too dense".
- 1 SVG was flagged for truncated text.
- 1 SVG was flagged for repeated label text instead of a single concept.

These findings are asset-quality issues rather than build blockers, but they are substantial enough to warrant a dedicated cleanup pass.

## Follow-Up Priority

1. Fix the `/tags/` CSP breakage first.
2. Repair Discussion page semantics and accessible names.
3. Raise dark-mode contrast on tags, archive badges/links, and discussion cards/CTA.
4. Triage the SVG quality backlog separately from page-level accessibility fixes.
