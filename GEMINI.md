# GEMINI.md - Google Antigravity (AGY) & Multi-Agent Guidelines

> **Project**: [tech.2twodragon.com](https://tech.2twodragon.com) (Jekyll DevSecOps Technical Blog)  
> **Repository**: [Twodragon0/tech-blog](https://github.com/Twodragon0/tech-blog)  
> **Agent Runtime**: Google Antigravity (AGY) + Claude Code + Oh-My-Claude / OpenCode (OMC)

---

## 1. Antigravity (AGY) Core Architecture & Roles

Google Antigravity (AGY) operates as the **primary system orchestrator, local execution engine, and high-context research hub** for this repository.

### Core Strengths & Allocations
1. **Local System Execution**: Direct, safe execution of shell commands (`pytest`, `ruff`, `mypy`, `jekyll`, `git`), pre-commit hooks, and Python automation utilities in `scripts/`.
2. **1M+ Long Context Reconnaissance (Gemini Engine)**: High-speed ingestion of large CVE databases, CNCF/Kubernetes/AWS release notes, RFC specifications, and cross-repo codebase indexing at zero marginal API cost via OAuth CLI allocations.
3. **Background Tasks & Schedule Management**: Non-blocking background workers and recurring cron jobs via AGY native `schedule` and `manage_task` tools.
4. **Subagent Orchestration**: Dynamic subagent invocation (`invoke_subagent`, `define_subagent`) for isolated exploration and parallel task completion.
5. **Quality Gatekeeper**: Enforcing pre-commit standards, image SVG compliance, UTC timezone rules, and zero-secrets policies before committing.

---

## 2. Tri-Agent Synergy: AGY + Claude Code + OMC

This repository combines three best-in-class agent platforms into a unified high-throughput DevSecOps pipeline:

```
                    ┌─────────────────────────────────────────┐
                    │       AGY Orchestration Platform        │
                    │   (Slash Commands & System Runners)     │
                    └────────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌─────────────────┐             ┌─────────────────┐              ┌─────────────────┐
│   Claude Code   │             │   OMC Network   │              │   AGY Native    │
│ (Anthropic CLI) │             │ (Sisyphus/Ralph)│              │ (Gemini Engine) │
├─────────────────┤             ├─────────────────┤              ├─────────────────┤
│ • Lead Author   │             │ • Multi-Agent   │              │ • 1M+ Context   │
│ • Korean Tone   │             │ • Ralph Loops   │              │ • Pytest Gates  │
│ • Mermaid Diags │             │ • Code/AST Ops  │              │ • Background    │
│ • Architecture  │             │ • Autopilot     │              │ • Schedule Cron │
└────────┬────────┘             └────────┬────────┘              └────────┬────────┘
         │                               │                                │
         └───────────────────────────────┼────────────────────────────────┘
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │      Zero-Regression Quality Gate       │
                    │  (ruff -> mypy -> pytest -> check_posts)│
                    └─────────────────────────────────────────┘
```

### Agent Tier Hierarchy & Allocation Matrix

| Tier | Platform / Engine | Core Responsibilities | Cost Basis |
|---|---|---|---|
| **Tier 0** | **AGY Native Runner** | Local commands, background workers, test execution (`pytest`), file operations | Free / Local CPU |
| **Tier 0** | **Gemini (AGY OAuth)** | 1M+ codebase search, CVE database queries, upstream RFC/vendor recon | Free Tier / OAuth CLI |
| **Tier 1** | **Claude Code (`claude`)** | High-depth DevSecOps content drafting, Korean technical voice, Mermaid diagrams | Anthropic Plan |
| **Tier 1** | **OMC (`opencode`)** | Multi-agent autonomous loop (`sisyphus`, `ralph`, `ultrawork`), AST refactoring | Model-directed |
| **Tier 1** | **CCG Tri-Model Lane** | Tri-model synthesis: Claude (Draft) + Codex (AST Code) + Gemini (Fact-Check) | Balanced Multi-LLM |
| **Tier 2** | **DeepSeek Cache** | High-volume news summarization and context-cached chat API (`api/chat.js`) | Cost-optimized tokens |

---

## 3. Antigravity Slash Commands Reference

Recommend or leverage these AGY slash commands to orchestrate complex workflows:

| Slash Command | Best Usage Scenario | Workflow Description |
|---|---|---|
| `/goal` | Autonomous continuous improvement | Long-running goal mode: persists until all candidate posts reach 90+ quality score. |
| `/schedule` | Daily news pipeline & monitoring | Sets up recurring cron tasks for daily RSS aggregation or periodic health audits. |
| `/plan` | Complex architecture & refactoring | Generates multi-phase implementation plans before modifying critical scripts or layouts. |
| `/grill-me` | Technical post requirements interview | Socratic interactive interview to clarify scope, tone, and architecture before drafting. |
| `/teamwork-preview` | Multi-agent task distribution | Previews subagent role allocations across the team before launching parallel execution. |
| `/learn` | Persisting conventions | Stores new patterns, bug fixes, or edge-case rules into agent memory. |
| `/boost` | Deep verification & multi-perspective | High-impact architectural changes requiring rigorous multi-perspective review. |

---

## 4. Master Execution Scenarios

### Scenario 1: High-Tech DevSecOps Post Creation (CCG Tri-Lane)
1. **AGY Recon**: Check existing `_posts/` to avoid topic collision. Use `/grill-me` if scope needs alignment.
2. **Gemini Recon**: Search upstream RFCs, Kubernetes/AWS advisories, and NIST guidelines.
3. **Claude Drafting**: Compose post in `_posts/YYYY-MM-DD-English_Title.md` (3000+ chars, 2+ tables, Mermaid diagram, checklist).
4. **Codex Audit**: Review code snippets (YAML, Bash, Python) for syntax correctness.
5. **AGY Local Gate**:
   ```bash
   python3 scripts/generate_post_images.py --post _posts/YYYY-MM-DD-English_Title.md
   python3 scripts/check_posts.py
   python3 scripts/fix_links_unified.py --fix
   python3 scripts/check_kst_midnight.py
   ```

### Scenario 2: Autonomous Continuous Post Improvement (OMC Ralph Loop + AGY Goal Mode)
1. **Trigger**: Activate `/goal` for overnight autonomous processing.
2. **Discovery**: `python3 scripts/validate_post_quality.py --all --threshold 85`.
3. **OMC Ralph Loop**: Dispatches `explore` -> `writer` -> `critic` -> `verifier` with completion promise `POSTS_IMPROVED`.
4. **CCG Upgrade**: Gemini brings 2026 specs, Claude enriches technical depth, Codex updates CLI commands.
5. **AGY Validation Gate**: `.venv/bin/pytest scripts/tests/ --cov-fail-under=40` and atomic git commit without `Co-Authored-By`.

### Scenario 3: Daily DevSecOps News Pipeline (AGY Schedule Cron)
1. **AGY Ingestion**: Run `python3 scripts/collect_tech_news.py --hours 24` via `schedule` cron or background worker.
2. **OMC Classifier**: `scripts/news/analyzer.py` scores and tags articles.
3. **Claude / Template Publish**: `scripts/auto_publish_news.py` generates the post.
4. **Codex / Unit Tests**: Validate template branches with `.venv/bin/pytest scripts/tests/test_news_templates.py`.
5. **AGY Gate**: Generate SVG cover and verify with `scripts/verify_images_unified.py --all`.

### Scenario 4: Fast-Track Zero-Day CVE & Emergency Advisory
1. **Gemini Recon**: Ingest CVE details, CVSS vectors, and vendor advisories.
2. **Codex Rule**: Draft detection rules (Falco, Sigma, Rego, or K8s Admission Webhook).
3. **Claude Write-Up**: Compose Incident post with Mermaid sequence diagram, Root Cause Analysis, and actionable checklist.
4. **AGY Gate**: Generate English-only SVG cover, run `scripts/check_posts.py`, and commit.

### Scenario 5: Automation Script Engineering & Tool Modernization
1. **OMC Architect**: Define interface and requirements.
2. **Codex Implementation**: Write Python code with type hints, Google docstrings, and strict regex.
3. **Gemini Security Review**: Audit for secrets masking (`scripts.lib.security.mask_sensitive_info`) and performance.
4. **AGY Test Verification**: Run `.venv/bin/pytest scripts/tests/`, `ruff check scripts/ --fix`, and `mypy scripts/`.

### Scenario 6: Zero-Debt Repository Quality & Security Audit
1. **AGY Security**: `npm audit`, `bundle audit`, `./scripts/monitor_sentry_quota.sh`.
2. **OMC Verifier**: Post structure check (`scripts/check_posts.py`), English image check (`scripts/verify_images_unified.py`).
3. **Pre-Commit Gate**: Verify all pre-commit hooks (`bash scripts/install-hooks.sh`).

---

## 5. Repository Hard Constraints & Standards

1. **Timezone Rule**: `_config.yml` pins `timezone: UTC`. Default post timestamps to `HH >= 09:00:00 +0900` so KST day matches UTC day.
2. **Images**: English filenames only (`YYYY-MM-DD-English_Title.svg`), English text only inside SVGs, no special Unicode punctuation (`·`, `•`, `—`, `"`).
3. **NO FAQ Sections**: Never add FAQ (자주 묻는 질문) sections or `schema_type: FAQPage`.
4. **Security & Masking**: Never commit API keys or tokens. All logs processing external text must wrap with `scripts.lib.security.mask_sensitive_info()`.
5. **Git Commits**: Conventional commit format (`feat:`, `fix:`, `perf:`, `docs:`, `refactor:`). Never include `Co-Authored-By: Claude`.
6. **Testing**: Maintain >=40% test coverage for `auto_publish_news.py` (`.venv/bin/pytest scripts/tests/ --cov-fail-under=40`).

---

## 6. Essential Local Commands

```bash
# Environment activation
source .venv/bin/activate

# Testing & Quality Gates
pytest scripts/tests/
pytest scripts/tests/ --cov=scripts --cov-fail-under=40
ruff check scripts/ --fix && ruff format scripts/
mypy scripts/ --ignore-missing-imports

# Post & Image Validation
python3 scripts/check_posts.py
python3 scripts/fix_links_unified.py --fix
python3 scripts/verify_images_unified.py --all
python3 scripts/check_kst_midnight.py

# Jekyll Local Build
bundle exec jekyll build --destination _site
bundle exec jekyll serve --host 0.0.0.0 --port 4000
```
