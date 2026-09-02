---
name: agent-triad
description: Multi-agent coordination guide across AGY, Claude Code, and OpenCode (OMC)
compatibility: opencode
license: MIT
metadata:
  audience: agents
  domain: orchestration
---

# Agent Triad Orchestration Skill (OMC + AGY + Claude)

Use this skill when orchestrating tasks across OpenCode, Google Antigravity (AGY), and Claude Code.

## Workflow Routing
1. **Research & Long-Context (1M+)**:
   - Utilize AGY / Gemini CLI for zero-cost ingestion of large RFCs, vendor documentation, and whole-codebase indexing.
2. **Technical Drafting & Architecture**:
   - Route DevSecOps blog content, Mermaid diagrams, and Korean technical style to Claude Code.
3. **AST Code Refactoring & Logic**:
   - Route strict Python/YAML implementation and test creation to OpenCode `code` agent.
4. **Local Verification Gate**:
   - Always run local tests via AGY/bash:
     - `.venv/bin/pytest scripts/tests/ --cov-fail-under=40`
     - `python3 scripts/check_posts.py`
     - `python3 scripts/verify_images_unified.py --all`

## Safety Directives
- Never commit unmasked secrets. Use `scripts.lib.security.mask_sensitive_info()`.
- Never include `Co-Authored-By: Claude` in git commits.
- Enforce UTC timezone rule (`HH >= 09:00:00 +0900`) on all blog posts.
- Maintain English-only filenames and SVG `<text>` elements.
