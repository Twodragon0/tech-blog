---
description: Ultrawork loop for investing post reliability, quality, and image checks
agent: lead
---

Run an ultrawork loop dedicated to investing post improvement.

Target selection:
1. If `INVESTING_POST` is set, use that exact post path.
2. Otherwise, select the latest `_posts/*.md` matching `invest|investing|투자` in filename or content.

For each cycle:
1. Validate target quality with `python3 scripts/check_posts.py <TARGET_POST>` and `python3 scripts/validate_post_quality.py <TARGET_POST>`.
2. Fix post issues only in `<TARGET_POST>`.
3. Force-refresh target image via `python3 scripts/generate_post_images.py <TARGET_POST> --force`.
4. Run `python3 scripts/verify_images_unified.py --missing` and resolve missing-image findings that affect the target.
5. Continue until no P0/P1 issue remains for the target post.

Output `<promise>ULTRAWORK_INVESTING_LOOP_COMPLETE</promise>` when complete.
