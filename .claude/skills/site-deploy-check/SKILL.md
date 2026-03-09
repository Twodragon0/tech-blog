---
name: site-deploy-check
description: Verify tech blog build and Vercel deployment readiness
---

# Site Deploy Check

## Steps
1. Build site: `bundle exec jekyll build`
2. Check for build warnings or errors
3. Verify recent posts have correct frontmatter
4. Check broken links in generated HTML
5. Verify Vercel configuration (vercel.json if present)
6. Check GitHub Actions status: `gh run list --limit 5`
7. Test responsive layout if applicable
