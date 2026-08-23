# Multi-Tool Synergy: AGY + OMC + CCG Rules

## 1. Tool Stack & Tier Hierarchy
| Tier | Tool / Engine | Primary Role | Cost Basis |
|---|---|---|---|
| **Tier 0** | **AGY Native / Local Python** | Local validations, test suite, file I/O, regex gates | Free |
| **Tier 0** | **Gemini CLI (OAuth) / AGY** | 1M+ codebase search, broad research, feed analysis | Free OAuth quota |
| **Tier 1** | **Claude Code & OMC** | Multi-agent orchestration, architectural design, drafting | Anthropic Plan |
| **Tier 1** | **CCG (Claude + Codex + Gemini)** | Tri-model synthesis, peer-review & fact verification | Subagent orchestration |
| **Tier 2** | **DeepSeek API (Context Cache)** | High-throughput blog post content generation | Low cost tokens |
| **Tier 2/3**| **OpenAI / Direct APIs** | Specific image enhancement & fallback paths | Pay per call |

## 2. Multi-Agent Protocol & Handoffs
- **AGY**: Acts as the local system orchestrator, executes shell commands, manages background tasks, verifies tests (`scripts/tests/`), and enforces safety hooks.
- **OMC (Oh-My-ClaudeCode)**: Manages multi-agent specialized roles (`writer`, `designer`, `executor`, `code-reviewer`) and modes (`ultrawork`, `autopilot`, `ralph`).
- **CCG Lane**: Dispatches tasks to Codex for strict code/script syntax and Gemini for 1M context search/alternatives, synthesized by Claude into the final deliverable.

## 3. Worktree & Concurrency Isolation
- Multi-agent long running tasks should utilize git worktree isolation (`bash scripts/setup-worktrees.sh`) to prevent git working tree collisions.
- Use atomic commits following conventional commit rules (`feat:`, `fix:`, `refactor:`, `perf:`, `docs:`).
- Never include `Co-Authored-By: Claude` in git commits.

## 4. Skills & Scenarios Execution Catalog
- **Master Scenarios**: Refer to `.agents/rules/04-best-scenarios.md` and `docs/pipeline/AGY_OMC_CCG_BEST_SCENARIOS.md`.
- **Available Skills**:
  - `ccg-orchestrator`: Tri-model multi-agent collaboration lane.
  - `techblog-post-create`: End-to-end technical post authoring with quality gates.
  - `autonomous-improvement`: Autonomous long-running post modernization (`/goal` + Ralph loop).
  - `daily-news-pipeline`: Automated RSS aggregation, AI scoring, and news publishing.
  - `emergency-incident-post`: Fast-track zero-day CVE & post-mortem analysis.
  - `techblog-qa-audit`: Comprehensive test suite, security, link, and image audit.

