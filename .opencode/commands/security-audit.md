---
description: Comprehensive security audit for secrets, validation, and exposure
agent: validate
---

Run a comprehensive security audit:
1. Scan for hardcoded secrets (API keys, passwords, tokens).
2. Validate file permissions for sensitive config files.
3. Review API usage patterns (auth, rate limiting).
4. Check for XSS/injection patterns.
5. Validate input sanitization.
6. Check logs/output for sensitive data exposure.

Use `scripts/check_security.py` if available.
Never expose raw sensitive values; mask them.

Output `<promise>SECURITY_AUDIT_COMPLETE</promise>` when complete.
