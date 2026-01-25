# /validate-posts - Post Validation Command

## Description
Comprehensive validation of all blog posts for quality, security, and compliance.

## Usage
```
/validate-posts [--threshold=80] [--fix=false]
```

## Arguments
- `--threshold`: Minimum quality score (default: 80)
- `--fix`: Automatically fix issues when possible (default: false)

## Validation Checks

### Quality Checks
- Content length >= 3000 chars
- Has at least 2 tables
- Has at least 1 code block
- Has at least 1 checklist
- Front matter complete (title, date, category, tags, excerpt)

### Security Checks
- No hardcoded secrets
- No sensitive data exposure
- Valid file permissions
- No XSS/injection patterns

### Compliance Checks
- Image filenames are English only
- No Korean characters in SVG files
- All links are valid
- No broken internal links

## Workflow
1. Run `python3 scripts/check_posts.py`
2. Run `python3 scripts/fix_links_unified.py --check`
3. Run `python3 scripts/verify_images_unified.py --all`
4. Calculate quality scores
5. Generate validation report
6. Fix issues if `--fix=true`

## Completion Promise
Output `<promise>POSTS_VALIDATED</promise>` when complete.

## Error Handling
- Continue validation even if individual posts fail
- Log all issues for review
- Mark posts for manual review if score < threshold
