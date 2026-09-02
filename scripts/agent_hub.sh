#!/usr/bin/env bash
# ==============================================================================
# agent_hub.sh - Unified Multi-Agent CLI Hub (AGY + Claude Code + OMC)
#
# Provides status checks, verification gates, and master scenario runbooks
# across Google Antigravity (AGY), Claude Code, and OpenCode (OMC).
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ -d "$REPO_ROOT/.venv/bin" ]; then
    export PATH="$REPO_ROOT/.venv/bin:$PATH"
fi

COLOR_RESET="\033[0m"
COLOR_BOLD="\033[1m"
COLOR_GREEN="\033[32m"
COLOR_BLUE="\033[34m"
COLOR_YELLOW="\033[33m"
COLOR_RED="\033[31m"
COLOR_CYAN="\033[36m"

print_header() {
    echo -e "\n${COLOR_CYAN}${COLOR_BOLD}================================================================${COLOR_RESET}"
    echo -e "${COLOR_CYAN}${COLOR_BOLD}   $1${COLOR_RESET}"
    echo -e "${COLOR_CYAN}${COLOR_BOLD}================================================================${COLOR_RESET}\n"
}

check_tool() {
    local name="$1"
    local cmd="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
        local version
        version=$("$cmd" --version 2>&1 | head -n 1 || echo "installed")
        echo -e "  [${COLOR_GREEN}✓${COLOR_RESET}] ${COLOR_BOLD}$name${COLOR_RESET}: $(which "$cmd") (${version})"
        return 0
    else
        echo -e "  [${COLOR_RED}✗${COLOR_RESET}] ${COLOR_BOLD}$name${COLOR_RESET}: Not found in PATH"
        return 1
    fi
}

cmd_status() {
    print_header "AI Agent & Development Environment Status"

    echo -e "${COLOR_BOLD}1. Agent CLI Tooling:${COLOR_RESET}"
    check_tool "Google Antigravity (AGY)" "agy" || true
    check_tool "Claude Code CLI" "claude" || true
    check_tool "OpenCode (OMC)" "opencode" || true

    echo -e "\n${COLOR_BOLD}2. Core Runtimes & Compilers:${COLOR_RESET}"
    check_tool "Python 3" "python3" || true
    check_tool "Jekyll" "jekyll" || true
    check_tool "Bun" "bun" || true
    check_tool "Git" "git" || true

    echo -e "\n${COLOR_BOLD}3. Python Virtual Environment (.venv):${COLOR_RESET}"
    if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
        echo -e "  [${COLOR_GREEN}✓${COLOR_RESET}] Virtualenv found at $REPO_ROOT/.venv"
        local pytest_ver
        pytest_ver=$("$REPO_ROOT/.venv/bin/pytest" --version 2>&1 | head -n 1 || echo "unknown")
        echo -e "  [${COLOR_GREEN}✓${COLOR_RESET}] Pytest available: $pytest_ver"
    else
        echo -e "  [${COLOR_YELLOW}!${COLOR_RESET}] .venv not found. Create using: python3 -m venv .venv && pip install -r scripts/requirements.txt"
    fi

    echo -e "\n${COLOR_BOLD}4. Git Repository & Hooks:${COLOR_RESET}"
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    echo -e "  Branch: ${COLOR_BLUE}$branch${COLOR_RESET}"
    if git diff --quiet && git diff --cached --quiet; then
        echo -e "  Working tree: ${COLOR_GREEN}clean${COLOR_RESET}"
    else
        echo -e "  Working tree: ${COLOR_YELLOW}has uncommitted changes${COLOR_RESET}"
    fi

    if [ -f "$REPO_ROOT/.githooks/pre-commit" ] || [ -f "$REPO_ROOT/.git/hooks/pre-commit" ]; then
        echo -e "  [${COLOR_GREEN}✓${COLOR_RESET}] Pre-commit hook installed"
    else
        echo -e "  [${COLOR_YELLOW}!${COLOR_RESET}] Pre-commit hook missing. Install via: bash scripts/install-hooks.sh"
    fi

    echo -e "\n${COLOR_BOLD}5. Key Guidelines & Configurations:${COLOR_RESET}"
    for f in "GEMINI.md" "AGENTS.md" "CLAUDE.md" "OPENCODE.md" ".mcp.json" ".opencode/opencode.json"; do
        if [ -f "$REPO_ROOT/$f" ]; then
            echo -e "  [${COLOR_GREEN}✓${COLOR_RESET}] $f exists"
        else
            echo -e "  [${COLOR_RED}✗${COLOR_RESET}] $f missing"
        fi
    done
}

cmd_verify() {
    print_header "Running Multi-Agent Zero-Regression Verification Gate"

    local PYTHON_CMD="python3"
    if [ -f "$REPO_ROOT/.venv/bin/python3" ]; then
        PYTHON_CMD="$REPO_ROOT/.venv/bin/python3"
    fi

    echo -e "${COLOR_BOLD}Step 1/5: Python Syntax & Linter (ruff)...${COLOR_RESET}"
    if command -v ruff >/dev/null 2>&1; then
        ruff check scripts/ --fix
        echo -e "  [${COLOR_GREEN}PASS${COLOR_RESET}] ruff check passed"
    else
        echo -e "  [${COLOR_YELLOW}SKIP${COLOR_RESET}] ruff not installed"
    fi

    echo -e "\n${COLOR_BOLD}Step 2/5: Type Checking (mypy - advisory)...${COLOR_RESET}"
    if command -v mypy >/dev/null 2>&1; then
        if mypy scripts/ --ignore-missing-imports; then
            echo -e "  [${COLOR_GREEN}PASS${COLOR_RESET}] mypy passed cleanly"
        else
            echo -e "  [${COLOR_YELLOW}WARN${COLOR_RESET}] mypy found advisory legacy warnings (non-blocking)"
        fi
    else
        echo -e "  [${COLOR_YELLOW}SKIP${COLOR_RESET}] mypy not installed"
    fi

    echo -e "\n${COLOR_BOLD}Step 3/5: Automated Test Suite (pytest)...${COLOR_RESET}"
    if [ -f "$REPO_ROOT/.venv/bin/pytest" ]; then
        "$REPO_ROOT/.venv/bin/pytest" scripts/tests/ -q
        echo -e "  [${COLOR_GREEN}PASS${COLOR_RESET}] pytest passed"
    else
        echo -e "  [${COLOR_YELLOW}SKIP${COLOR_RESET}] .venv/bin/pytest not found"
    fi

    echo -e "\n${COLOR_BOLD}Step 4/5: Blog Post & Image Structure Check...${COLOR_RESET}"
    $PYTHON_CMD scripts/check_posts.py
    $PYTHON_CMD scripts/verify_images_unified.py --all
    echo -e "  [${COLOR_GREEN}PASS${COLOR_RESET}] Blog posts & images verified"

    echo -e "\n${COLOR_BOLD}Step 5/5: Timezone Rule Check (UTC vs KST)...${COLOR_RESET}"
    $PYTHON_CMD scripts/check_kst_midnight.py
    echo -e "  [${COLOR_GREEN}PASS${COLOR_RESET}] Timezone rule verified"

    print_header "All Verification Gates Passed Successfully!"
}

cmd_scenario() {
    local num="${1:-}"
    case "$num" in
        1)
            print_header "Master Scenario 1: New DevSecOps Post Creation (CCG Tri-Lane)"
            cat << 'EOF'
Workflow:
  1. AGY/Gemini Recon: Check _posts/ for duplicates; search RFCs & CVE feeds.
  2. Claude Drafting: Author _posts/YYYY-MM-DD-English_Title.md (3000+ chars, 2+ tables, Mermaid diagram).
  3. Codex Audit: Review YAML/Bash/Python snippets for AST syntax correctness.
  4. AGY Local Gate:
       python3 scripts/generate_post_images.py --post _posts/YYYY-MM-DD-English_Title.md
       python3 scripts/check_posts.py
       python3 scripts/fix_links_unified.py --fix
       python3 scripts/check_kst_midnight.py
EOF
            ;;
        2)
            print_header "Master Scenario 2: Autonomous Post Improvement (OMC Ralph Loop + AGY Goal Mode)"
            cat << 'EOF'
Workflow:
  1. AGY Goal Mode: Trigger /goal in Antigravity chat for autonomous execution.
  2. Discovery: python3 scripts/validate_post_quality.py --all --threshold 85
  3. OMC Ralph Loop: Dispatch subagents (explore -> writer -> critic -> verifier).
  4. CCG Upgrade: Gemini brings 2026 specs, Claude crafts depth, Codex fixes code.
  5. AGY Gate:
       .venv/bin/pytest scripts/tests/ --cov-fail-under=40
       git commit -m "perf(posts): improve technical depth and diagrams"
EOF
            ;;
        3)
            print_header "Master Scenario 3: Daily DevSecOps News Pipeline (AGY Schedule Cron)"
            cat << 'EOF'
Workflow:
  1. AGY Ingestion: python3 scripts/collect_tech_news.py --hours 24 via /schedule cron.
  2. OMC Classifier: scripts/news/analyzer.py tags articles.
  3. Auto-Publish: python3 scripts/auto_publish_news.py
  4. Test Gate: .venv/bin/pytest scripts/tests/test_news_templates.py
  5. Image Verification: python3 scripts/verify_images_unified.py --all
EOF
            ;;
        4)
            print_header "Master Scenario 4: Fast-Track Zero-Day CVE & Emergency Advisory"
            cat << 'EOF'
Workflow:
  1. Gemini Recon: Ingest CVE CVSS score, affected versions, attack vectors.
  2. Codex Rule: Formulate detection rule (Falco/Sigma/Rego).
  3. Claude Write-Up: Incident post with attack sequence Mermaid diagram & RCA.
  4. AGY Gate: Generate SVG cover, validate structure, and commit.
EOF
            ;;
        5)
            print_header "Master Scenario 5: Automation Script Engineering & Tool Modernization"
            cat << 'EOF'
Workflow:
  1. OMC Architect: Design interface & requirements in .omc/plans/.
  2. Codex Implementation: Write Python code with type hints & Google docstrings.
  3. Gemini Review: Check secret masking & performance bottlenecks.
  4. AGY Test Verification:
       .venv/bin/pytest scripts/tests/
       ruff check scripts/ --fix
       mypy scripts/
EOF
            ;;
        6)
            print_header "Master Scenario 6: Zero-Debt Repository Quality & Security Audit"
            cat << 'EOF'
Workflow:
  1. AGY Security: npm audit && bundle audit && ./scripts/monitor_sentry_quota.sh
  2. OMC Verifier: python3 scripts/check_posts.py && python3 scripts/verify_images_unified.py --all
  3. Gate: bash scripts/install-hooks.sh
EOF
            ;;
        *)
            echo "Usage: $0 scenario <1-6>"
            echo "  1: New Post Creation (CCG Tri-Lane)"
            echo "  2: Autonomous Continuous Post Improvement"
            echo "  3: Daily News Pipeline"
            echo "  4: Emergency CVE Advisory"
            echo "  5: Automation Script Engineering"
            echo "  6: Zero-Debt Repository Audit"
            ;;
    esac
}

usage() {
    cat << EOF
Multi-Agent Hub (AGY + Claude Code + OMC)

Usage:
  bash scripts/agent_hub.sh [command]

Commands:
  status         Check installed agent CLIs, runtimes, git hooks, and guidelines
  verify         Run full zero-regression verification gate (ruff, mypy, pytest, check_posts)
  scenario <N>   Display master scenario playbook (1 through 6)
  help           Show this help message

Examples:
  bash scripts/agent_hub.sh status
  bash scripts/agent_hub.sh verify
  bash scripts/agent_hub.sh scenario 1
EOF
}

case "${1:-status}" in
    status)
        cmd_status
        ;;
    verify)
        cmd_verify
        ;;
    scenario)
        cmd_scenario "${2:-}"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${COLOR_RED}Unknown command: $1${COLOR_RESET}"
        usage
        exit 1
        ;;
esac
