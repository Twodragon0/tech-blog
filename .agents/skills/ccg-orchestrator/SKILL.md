---
name: ccg-orchestrator
description: >-
  Orchestrates the Claude + Codex + Gemini (CCG) tri-model collaboration lane.
  Use this skill when cross-verifying complex technical posts, validating code architecture,
  synthesizing multiple model opinions, or executing rigorous multi-LLM quality gates.
---

# CCG Tri-Model Orchestrator

The **CCG (Claude + Codex + Gemini)** lane coordinates three distinct AI architectures to achieve maximum accuracy, speed, and cost efficiency.

```
                    ┌─────────────────────────────────────────┐
                    │      CCG Orchestration Dispatcher       │
                    └────────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌─────────────────┐             ┌─────────────────┐              ┌─────────────────┐
│     Claude      │             │      Codex      │              │     Gemini      │
│ (Anthropic/OMC) │             │ (OpenAI Engine) │              │  (Google / AGY) │
├─────────────────┤             ├─────────────────┤              ├─────────────────┤
│ • Lead Architect│             │ • Syntax Rigor  │              │ • 1M+ Context   │
│ • Korean Tone   │             │ • Script Safety │              │ • Latest Specs  │
│ • Synthesis     │             │ • Edge UnitTests│              │ • Zero-Cost Run │
└────────┬────────┘             └────────┬────────┘              └────────┬────────┘
         │                               │                                │
         └───────────────────────────────┼────────────────────────────────┘
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │        Consensus & Output Gate          │
                    │ (Validation -> Pytest -> Final Commit)  │
                    └─────────────────────────────────────────┘
```

## Role Specialization Matrix

| Model | Primary Focus | Specific Deliverables | Cost Tier |
|---|---|---|---|
| **Claude** (Opus 4.6 / Sonnet 4.6) | Synthesis, Content Architecture, Tone | Post drafts, Jekyll layouts, overall design decisions, RCA write-ups | Tier 1 (Subscription) |
| **Codex** (GPT-5.4 / Codex Engine) | Code Integrity, AST Correctness, Safety | Python scripts, regex expressions, CI YAML configs, unit tests | Tier 2 (Targeted) |
| **Gemini** (AGY / Gemini 2.5/3.7) | High-Context Search, Fact-Check, Alternatives | 1M+ codebase analysis, alternative approaches, CVE verification | Tier 0 (Free OAuth / CLI) |

## CCG Core Scenario Workflows

### Scenario 1: High-Tech Post Creation & Synthesis
1. **Gemini Phase**: Run deep search across existing `_posts/` and upstream web docs (CNCF, AWS, K8s, RFCs) to gather latest specs and CVE facts.
2. **Claude Phase**: Draft full post in professional Korean DevSecOps tone with Mermaid diagrams and actionable tables.
3. **Codex Phase**: Audit all code blocks (YAML, Python, Bash, Dockerfile) for AST/syntax validity and security hardening.
4. **Synthesis & Gate**: Incorporate reviews, run `python3 scripts/check_posts.py` and `python3 scripts/fix_links_unified.py --fix`.

### Scenario 2: Automation Script & Tool Engineering
1. **Claude (OMC Architect)**: Define spec & architecture in `.omc/plans/`.
2. **Codex**: Generate production-grade Python script with strict type hints, Google docstrings, and robust error handling.
3. **Gemini**: Review edge cases, security masking compliance (`scripts.lib.security.mask_sensitive_info`), and performance bottlenecks.
4. **AGY Local Gate**: Run `.venv/bin/pytest scripts/tests/` and verify coverage >= 40%.

### Scenario 3: Emergency Incident & Vulnerability Advisory
1. **Gemini**: Ingest CVE details, CVSS scores, attack vectors, and vendor mitigation statements.
2. **Codex**: Formulate detection rules (Falco, Sigma, Rego) and verify regex accuracy.
3. **Claude**: Compose post-mortem architecture, timeline, and mitigation checklist.
4. **AGY Local**: Generate English SVG cover and validate post integrity.

### Scenario 4: Tri-Model Quality & Security Audit
1. **Gemini**: Scan repository for outdated dependencies, secrets, and Sentry health status.
2. **Codex**: Audit unit test suite coverage, dead code branches, and lint rules (`ruff check scripts/`).
3. **Claude**: Review SEO meta tags, OpenGraph configs, JSON-LD structured data, and content clarity.
