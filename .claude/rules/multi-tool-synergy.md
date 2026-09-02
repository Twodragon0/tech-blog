# Multi-Tool Synergy Rules: Claude Code + Antigravity (AGY) + OpenCode (OMC)

## 1. Tool Tier & Role Hierarchy
- **Claude Code**: Lead author, DevSecOps domain architect, Korean technical tone, Mermaid diagrams, design synthesis.
- **Antigravity (AGY)**: Native execution engine (pytest, ruff, mypy, git), background task & cron manager, 1M+ context search via Gemini.
- **OpenCode (OMC)**: Multi-agent autonomous loop (`sisyphus`, `ralph`), AST code refactoring, safety plugins.
- **CCG Tri-Model Lane**:
  - Gemini/AGY: 1M+ context research, CVE feeds, upstream RFCs.
  - Claude: Architecture & drafting.
  - Codex: Code syntax rigor, YAML configs, regex tests.
  - AGY: Local test and image verification gates.

## 2. Collaboration Protocol
- **Heavy Research / 1M+ Context**: Hand off to AGY Gemini engine (zero cost OAuth) instead of consuming expensive context tokens.
- **Background Tasks & Crons**: Delegate to AGY background workers (`schedule`, `manage_task`).
- **Autonomous Modernization**: Run OpenCode Sisyphus / Ralph loop (`/improve-posts`).
- **Code Changes**: Always run local verification via AGY/bash:
  ```bash
  ruff check scripts/ --fix && ruff format scripts/
  mypy scripts/ --ignore-missing-imports
  pytest scripts/tests/
  python3 scripts/check_posts.py
  python3 scripts/verify_images_unified.py --all
  ```

## 3. Hard Constraints
- **English-Only Images**: Cover images and SVG `<text>` must be strictly English.
- **Timezone Rule**: Post timestamps must use `HH >= 09:00:00 +0900` to match UTC calendar day.
- **NO FAQ Sections**: Never add FAQ (자주 묻는 질문) sections or `schema_type: FAQPage`.
- **Secret Masking**: All stdout/error logs handling external text must use `scripts.lib.security.mask_sensitive_info()`.
- **Commits**: Conventional format, never include `Co-Authored-By: Claude`.
