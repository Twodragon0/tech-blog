---
description: Ralph loop for continuous investing post quality and image improvement
agent: lead
---

Run a focused Ralph loop for one investing post.

Target selection:
1. If `INVESTING_POST` is set, use that exact post path.
2. Otherwise, pick the most recently modified `_posts/*.md` file that matches `invest|investing|투자` in filename or content.

Loop rules:
1. Improve only the selected post file.
2. Run `python3 scripts/check_posts.py <TARGET_POST>`.
3. Run `python3 scripts/validate_post_quality.py <TARGET_POST>` and keep iterating until score is >= 80.
4. Regenerate the post image with `python3 scripts/generate_post_images.py <TARGET_POST> --force`.
5. Verify image consistency with `python3 scripts/verify_images_unified.py --missing`.
6. Keep iteration focused on quality + image issues for this target post only.

Output `<promise>INVESTING_POSTS_IMPROVED</promise>` when complete.
