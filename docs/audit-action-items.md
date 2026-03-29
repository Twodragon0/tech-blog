# Quick Action Items - Blog Audit 2026-03-29

## Priority 1: CRITICAL (This Week)

### Task 1A: Add Missing Tags (81 posts) - HIGH
- [ ] Posts missing `tags:` field: 81 (65% of total)
- [ ] Estimated effort: 1-2 hours (with script)
- [ ] Impact: Navigation, SEO, discoverability
- [ ] Script template: See `audit-2026-03-29.md`

### Task 1B: Fix Unclosed Code Blocks (24 posts) - HIGH
- [ ] Posts with unclosed code blocks: 24
- [ ] Estimated effort: 1-2 hours (manual review)
- [ ] Impact: Markdown rendering broken
- [ ] Critical files:
  - `2026-01-14-GCP_Cloud_Security_Complete_Guide_IAMFrom_GKETo_Security_Architecture.md`
  - `2026-01-28-Claude_MD_Security_Guide.md`
  - `2026-02-25-Claude_Code_OpenCode_Best_Practices.md`
  - And 21 others (see audit report)

## Priority 2: HIGH (Next 2 Weeks)

### Task 2A: Add Language Tags to Code Blocks (61 posts) - MEDIUM
- [ ] Posts with bare code blocks: 61
- [ ] Estimated effort: 2-3 hours
- [ ] Impact: No syntax highlighting, reduced readability
- [ ] Includes:
  - `2026-02-05-AI_Content_Creator_Workflow_2026_Blog_Video_Music_Animation.md` (16 bare blocks)
  - `2026-02-25-Claude_Code_OpenCode_Best_Practices.md` (27 bare blocks)
  - And 59 others

### Task 2B: Fix Localhost Links (2 posts) - HIGH
- [ ] Posts with localhost links: 2
- [ ] Estimated effort: 30 minutes
- [ ] Impact: Non-functional links in published posts
- [ ] Files to fix:
  - `2025-05-30-Kubernetes_Minikube_ampamp_K9s_Practice_Guide_Problem_From_Resolution_Practical_TestTo.md` (2 links)
  - `2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.md` (1 link)

## Priority 3: MEDIUM (Optional)

### Task 3: Shorten SEO Titles (17 posts) - LOW
- [ ] Titles exceeding 60 chars: 17
- [ ] Estimated effort: 1-2 hours
- [ ] Impact: Better Google CTR, improved search visibility

## Quality Checks Passed

- [x] Content length adequate (no posts <500 chars)
- [x] Section headings present in all posts
- [x] Alt text on images (good coverage)
- [x] No FAQ sections (project rules observed)
- [x] No `example.com` links in published content
- [x] No empty href/src attributes
- [x] Excellent excerpt metadata (80-200 char range)
- [x] No duplicate excerpts
- [x] Strong OG image integration

## Next Steps

1. Run `/validate-post` on all modified posts
2. Test blog build locally: `bundle exec jekyll serve`
3. Verify deployment to https://tech.2twodragon.com
4. Add pre-commit hook to prevent future issues

## Report Reference
See `/Users/yong/Desktop/personal/tech-blog/docs/audit-2026-03-29.md` for full details.

---
**Report Date:** 2026-03-29  
**Total Issues:** 233 (HIGH: 129, MEDIUM: 76, LOW: 28)  
**Posts Affected:** 233 issues across 124 posts
