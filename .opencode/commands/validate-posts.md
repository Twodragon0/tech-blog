---
description: Validate posts for quality and security compliance
agent: validate
---

SECURITY AND VALIDATION:
1. Run `python3 scripts/check_posts.py`.
2. Run `python3 scripts/fix_links_unified.py --check`.
3. Run `python3 scripts/verify_images_unified.py --all`.

Then check for:
- Hardcoded secrets
- File permission issues
- XSS or injection patterns
- English-only image filenames

Never expose sensitive information in output.
Output `<promise>POSTS_VALIDATED</promise>` when complete.
