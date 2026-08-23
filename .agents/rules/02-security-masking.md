# Security & Secret Masking Rules (Antigravity & Agents)

## 1. Zero Secrets in VCS
- Never hardcode or commit API keys, tokens, passwords, or webhook URLs (`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `BUTTONDOWN_API_KEY`, `SENTRY_DSN`, etc.).
- Always read secrets from environment variables using `os.getenv("VAR_NAME", "")`.
- Ensure `.gitignore` continues to exclude `.env`, `*.env`, `.env.*`, `*.key`.

## 2. Mandatory Output Masking
- All agent logs, stdout, error traces, and diagnostic scripts processing external text or URLs MUST use `scripts.lib.security.mask_sensitive_info()`.
- Example pattern:
```python
from scripts.lib.security import mask_sensitive_info

def log_output(msg: str) -> None:
    safe_msg = mask_sensitive_info(msg)
    print(f"[AGENT] {safe_msg}")
```

## 3. Pre-Commit / Pre-Tool Validation
- Validate that regex patterns for secrets `^(sk-|AIza|gho_|xox[bp]-|eyJ[A-Za-z0-9_-]{20,})` are checked before writing code to repository files.
