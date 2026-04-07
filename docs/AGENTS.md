<!-- Parent: ../AGENTS.md -->
# docs/ — AI Agent Guidelines

**Last updated**: 2026-04-08

Project documentation organized by concern. All files are Markdown.

## Directory Layout

```
docs/
├── guides/          # Content creation guides (best practices, image gen, visualization)
├── optimization/    # Performance optimization notes
├── setup/           # Environment and tool setup instructions
├── troubleshooting/ # Known issues and workarounds
├── audits/          # Security and performance audit records
├── pdca/            # PDCA cycle records per feature
├── pipeline/        # CI/CD and deployment pipeline documentation
├── scripts/         # Script usage documentation
├── README.md        # Documentation index
└── SPEC.md          # Full technical specification
```

## Key Files

| File | Purpose |
|------|---------|
| `README.md` | Index of all docs — update when adding new files |
| `SPEC.md` | Authoritative technical specification |
| `guides/BEST_PRACTICES.md` | Post writing best practices |
| `guides/GEMINI_IMAGE_GUIDE.md` | SVG/image generation guide |
| `audits/audit-2026-03-29.md` | Latest security/perf audit |

## Writing Guidelines

- Use English headings; body text may be Korean or English
- No FAQ sections in documentation (mirrors the blog post rule)
- Keep files focused — one topic per file
- Update `README.md` when adding a new file to any subdirectory
- Audit records in `audits/` are append-only — create new files, do not edit past records

## PDCA Records (`pdca/`)

Each feature or significant change gets a PDCA document:
- Plan: goals and approach
- Do: what was implemented
- Check: metrics or test results
- Act: next steps or follow-up

File naming: `pdca/YYYY-MM-DD-feature-name.md`

## When to Update Docs

- New script added → update `scripts/README.md` and `docs/README.md`
- New GitHub Actions workflow → update root `AGENTS.md` section 9
- Security audit completed → add file to `audits/`, update `audit-action-items.md`
- Architecture change → update `SPEC.md` and relevant `setup/` files
