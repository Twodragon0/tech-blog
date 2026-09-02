# OPENCODE.md - OpenCode & Oh-My-Claude (OMC) Guidelines

> **Project**: [tech.2twodragon.com](https://tech.2twodragon.com)  
> **Framework**: OpenCode Sisyphus Mode + Ralph Loop + CCG Tri-Model Lane  
> **Agent Runtime**: OpenCode (OMC) + Google Antigravity (AGY) + Claude Code

---

## 1. OpenCode Architecture & Lead Agent Pattern

This repository implements OpenCode with a specialized **lead-orchestrator pattern** and multi-agent specialist subagents configured in `.opencode/opencode.json`:

```
                           ┌────────────────────────┐
                           │      lead (Primary)    │
                           │   (Lead Orchestrator)  │
                           └───────────┬────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ explore (Subagent│          │  code (Subagent) │          │validate (Subagent│
│  Gemini 3 Flash  │          │   GPT-5 Codex    │          │ Claude Sonnet 4.5│
├──────────────────┤          ├──────────────────┤          ├──────────────────┤
│ • Read-Only      │          │ • Implementation │          │ • Read-Only      │
│ • Codebase Recon │          │ • AST Refactor   │          │ • Quality Gates  │
│ • Fast Discovery │          │ • Regex Hardening│          │ • Security Check │
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

### Specialist Subagent Roster

| Agent Name | Mode | Default Model | Primary Responsibility | Permissions |
|---|---|---|---|---|
| `lead` | `primary` | `openai/gpt-5.4` | Repository-wide orchestration, task delegation, verification | Full (bash, edit, task) |
| `primary` | `primary` | `openai/gpt-5.4` | Compatibility runner for command templates | Full (bash, edit, write) |
| `explore` | `subagent` | `google/antigravity-gemini-3-flash` | Read-only codebase exploration, pattern indexing | Read-only (no edit/bash) |
| `validate` | `subagent` | `anthropic/claude-sonnet-4.5` | Quality, security, and compliance validation | Read-only (no edit/bash) |
| `code` | `subagent` | `openai/gpt-5.3-codex` | Production implementation, refactoring, bug fixes | Full (bash, edit, write) |

---

## 2. Sisyphus Mode & Ralph Loop Automation

OpenCode runs in **Sisyphus mode** with continuous **Ralph Loops**, guaranteeing that tasks continue until explicit completion promises are fulfilled:

```bash
# Start OpenCode in Sisyphus mode
opencode sisyphus

# Execute Ralph Loop commands
/improve-posts               # Continuous blog post quality enhancement
/validate-posts              # Validate post structure, front matter, and images
/collect-news                # Aggregation & classification of RSS feeds
/generate-images             # SVG cover generation and compliance audit
/security-audit              # Dependency, CSP, and secret masking audit
/write-code                  # Implementation of new features or scripts
/refactor                    # Behavior-preserving refactoring
/fix-bugs                    # Bug and test regression fixes
/cost-optimize               # Token and API cost analysis
```

### Quality Score Criteria (Promise: `POSTS_IMPROVED`)

| Metric | Weight | Threshold | Description |
|---|---|---|---|
| **Content Length** | 20% | >= 3,000 chars | Comprehensive technical depth and analysis |
| **Tables** | 15% | >= 2 tables | Comparison, configuration, or checklist tables |
| **Code Blocks** | 15% | >= 1 block | Correct syntax with explicit language tags |
| **Checklist** | 10% | >= 1 item | Actionable production verification steps |
| **Front Matter** | 20% | Valid | UTC timezone rule (`HH >= 09:00 +0900`), category, tags |
| **English Images** | 10% | Valid | English filenames and SVG text only |
| **Valid Links** | 10% | 100% | Zero broken links, zero placeholder domains |

---

## 3. Tri-Agent Synergy: OMC + AGY + Claude Code

OpenCode seamlessly collaborates with Google Antigravity (AGY) and Claude Code:

1. **AGY as Execution Engine & High-Context Researcher**:
   - OMC delegates heavy shell tasks (`pytest`, `mypy`, `ruff`, Jekyll builds) and long-running background tasks to AGY.
   - AGY's Gemini engine (1M+ context, free OAuth quota) performs zero-cost CVE ingestion and broad repo-wide searches.
2. **Claude Code as Lead DevSecOps Author**:
   - OMC routes technical writing and architecture diagrams (Mermaid) to Claude for natural Korean technical voice.
3. **CCG Consensus**:
   - Claude drafts -> Codex ensures AST syntax correctness -> Gemini cross-verifies against upstream specs -> AGY enforces local gates.

---

## 4. Safety Guardrails & Plugins

OpenCode enforces policy at execution time via `.opencode/plugins/safety-hooks.js`:
- **Blocked Shell Commands**: `rm *`, `sudo *`, `git reset --hard*`, `git clean -fd*`, `git push --force*`, direct pushes to `main`/`master`.
- **Protected Files**: `.env`, `*.env`, `.env.*` read access is strictly denied (only `.env.example` allowed).
- **Injected Environment**: `CI=1`, `TECH_BLOG_AUTO_YES=1`, `GIT_TERMINAL_PROMPT=0` to ensure non-blocking script execution.

---

## 5. Centralized Hourly Automation (Runtime)

This repository integrates with centralized hourly automation under a configurable Desktop root:

- **Pull runner**: `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}/bin/hourly-opencode-git-pull.sh`
- **Cron installer**: `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}/bin/install-system-cron.sh`
- **Repo inventory**: `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}/repos.list`

Set `TWODRAGON0_HOME` per operator machine if the manager root differs from default.

### Operational Safety
- Fast-forward pull only (`git pull --ff-only`).
- Dirty working trees are skipped safely.
- File-lock based overlap prevention (`flock`).

---

## 6. Verification & Health Commands

```bash
# Run test suite
.venv/bin/pytest scripts/tests/

# Verify blog posts & images
python3 scripts/check_posts.py
python3 scripts/verify_images_unified.py --all
python3 scripts/fix_links_unified.py --fix

# Linting
ruff check scripts/ --fix && ruff format scripts/
mypy scripts/ --ignore-missing-imports
```
