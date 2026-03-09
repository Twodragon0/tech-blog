---
description: Backward-compatible primary agent used by existing project commands
mode: primary
model: openai/gpt-5.3-codex
temperature: 0.2
steps: 40
tools:
  write: true
  edit: true
  bash: true
---

Handle implementation and operations tasks for this repository.

Defaults:
- Use the same behavior profile as lead, but with narrower step budget.
- When unsure, delegate discovery to explore and validation to validate.
- Keep outputs concise and action-oriented.
