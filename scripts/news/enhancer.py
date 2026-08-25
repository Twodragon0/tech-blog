"""AI enhancement functions (Gemini, DeepSeek, Claude, OpenAI)."""

import logging
import os
import subprocess
import time
from typing import Dict, Optional

import scripts.news.config as _cfg

# A transport fault on the runner -> DeepSeek path costs the item its Korean
# text: the call returns "" and the caller falls through to the English
# template. Run 32794655444 hit ConnectionResetError(104) three times inside a
# single digest, which is how two English summaries reached main on 2026-08-25.
# One immediate retry plus one backed-off retry covers a reset without turning
# a genuine outage into a long stall.
_TRANSIENT_RETRIES: int = max(0, int(os.getenv("AUTO_PUBLISH_HTTP_RETRIES", "2")))
_TRANSIENT_BACKOFF_S: float = 1.5


def post_with_retry(
    url: str,
    *,
    headers: Optional[Dict] = None,
    json: Optional[Dict] = None,
    timeout: int = 20,
    label: str = "AI API",
):
    """POST that retries transport faults and 429/5xx. ``None`` when exhausted.

    A 4xx other than 429 is a real answer — bad key, retired model, malformed
    request — so it is returned to the caller rather than retried. Retrying it
    would only burn the job's wall clock and bury the reason.
    """
    try:
        import requests
    except ImportError:
        logging.debug("requests library not available for %s", label)
        return None

    last_error = None
    for attempt in range(_TRANSIENT_RETRIES + 1):
        try:
            response = requests.post(
                url, headers=headers, json=json, timeout=timeout
            )
            if response.status_code == 429 or response.status_code >= 500:
                last_error = f"status {response.status_code}"
            else:
                return response
        except Exception as e:  # connection reset, read timeout, DNS, ...
            last_error = e
        if attempt < _TRANSIENT_RETRIES:
            time.sleep(_TRANSIENT_BACKOFF_S * (attempt + 1))
            logging.info(
                "%s transient failure (%s) - retry %d/%d",
                label,
                last_error,
                attempt + 1,
                _TRANSIENT_RETRIES,
            )
    logging.warning("%s failed after %d attempts: %s", label, _TRANSIENT_RETRIES + 1, last_error)
    return None


def _allow_gemini() -> bool:
    return _cfg._AI_MODE in {"auto", "gemini"}


def _allow_deepseek() -> bool:
    return _cfg._AI_MODE in {"auto", "deepseek"}


def check_gemini_available() -> bool:
    """Check if Gemini is available (API key or CLI)."""
    if not _allow_gemini():
        return False
    if _cfg._GEMINI_CIRCUIT_OPEN:
        return False
    if _cfg._GEMINI_API_KEY:
        return True
    if _cfg._GEMINI_AVAILABLE is not None:
        return _cfg._GEMINI_AVAILABLE
    try:
        result = subprocess.run(["gemini", "--version"], capture_output=True, timeout=5)
        _cfg._GEMINI_AVAILABLE = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        _cfg._GEMINI_AVAILABLE = False
    return _cfg._GEMINI_AVAILABLE


def _gemini_api_call(prompt: str, timeout: int = 20) -> str:
    """Direct Gemini REST API call."""
    if not _cfg._GEMINI_API_KEY:
        return ""

    try:
        import requests

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{_cfg._GEMINI_MODEL}:generateContent?key={_cfg._GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=timeout,
        )
        if response.status_code == 200:
            data = response.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            return text.strip()
        elif response.status_code == 404:
            # A retired model ID, not a transient fault. This was a plain
            # WARNING while gemini-2.0-flash 404'd on every single call for
            # weeks, so the primary translator's death never surfaced. Name the
            # override so the fix is obvious from the log alone.
            logging.error(
                "Gemini model '%s' returned 404 (retired or not enabled for this "
                "key) - the Gemini path is dead for this whole run. Set "
                "AUTO_PUBLISH_GEMINI_MODEL to a live model ID. Response: %s",
                _cfg._GEMINI_MODEL,
                response.text[:100],
            )
        else:
            logging.warning(
                f"Gemini API status {response.status_code}: {response.text[:100]}"
            )
    except ImportError:
        logging.debug("requests library not available for Gemini API")
    except Exception as e:
        logging.warning(f"Gemini API error: {e}")

    return ""


def _gemini_call(prompt: str, timeout: int = 35) -> str:
    """Gemini call with CLI-first strategy and circuit breaker."""
    if _cfg._GEMINI_CIRCUIT_OPEN:
        return ""

    if _cfg._GEMINI_AVAILABLE is not False:
        try:
            proc = subprocess.run(
                ["gemini", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode == 0 and len(proc.stdout.strip()) > 20:
                _cfg._GEMINI_CONSECUTIVE_FAILURES = 0
                return proc.stdout.strip()
            _cfg._GEMINI_CONSECUTIVE_FAILURES += 1
        except subprocess.TimeoutExpired:
            _cfg._GEMINI_CONSECUTIVE_FAILURES += 1
            logging.warning(f"Gemini CLI timeout ({timeout}s)")
        except (subprocess.SubprocessError, OSError) as e:
            _cfg._GEMINI_CONSECUTIVE_FAILURES += 1
            logging.warning(f"Gemini CLI error: {e}")

    if _cfg._GEMINI_API_KEY and _cfg._GEMINI_CONSECUTIVE_FAILURES > 0:
        api_timeout = min(timeout, 20)
        result = _gemini_api_call(prompt, timeout=api_timeout)
        if result and len(result) > 20:
            _cfg._GEMINI_CONSECUTIVE_FAILURES = 0
            return result
        _cfg._GEMINI_CONSECUTIVE_FAILURES += 1

    if not _cfg._GEMINI_AVAILABLE and not _cfg._GEMINI_API_KEY:
        _cfg._GEMINI_CONSECUTIVE_FAILURES += 1

    if _cfg._GEMINI_CONSECUTIVE_FAILURES >= 3:
        _cfg._GEMINI_CIRCUIT_OPEN = True
        logging.warning(
            f"Gemini circuit breaker OPEN after {_cfg._GEMINI_CONSECUTIVE_FAILURES} "
            "consecutive failures - switching to DeepSeek/template for remaining items"
        )
    return ""


def enhance_with_gemini(item: Dict, max_retries: Optional[int] = None) -> str:
    """Enhance news with Gemini CLI (free)."""
    title = item.get("title", "")
    summary = item.get("summary", "")[:300]
    url = item.get("url", "")

    if not title:
        return ""

    prompt = (
        f"DevSecOps \uad00\uc810\uc5d0\uc11c \ub2e4\uc74c \ub274\uc2a4\ub97c \ud55c\uad6d\uc5b4 \ubd84\uc11d (500\uc790 \uc774\ub0b4, \ub9c8\ud06c\ub2e4\uc6b4):\n"
        f"\uc81c\ubaa9: {title}\n\uc694\uc57d: {summary}\n\ucd9c\ucc98: {url}\n\n"
        f"\ud615\uc2dd: ### \uc81c\ubaa9\n1. **\uae30\uc220 \ubc30\uacbd** (2-3\ubb38\uc7a5)\n"
        f"2. **\uc2e4\ubb34 \uc601\ud5a5** (\uad6c\uccb4\uc801 \uc2dc\uc2a4\ud15c/\ub3c4\uad6c)\n"
        f"3. **\uccb4\ud06c\ub9ac\uc2a4\ud2b8** (- [ ] 3-4\uac1c)\n"
        f"4. **MITRE ATT&CK** (\ud574\ub2f9 \uc2dc)"
    )

    retries = max_retries if max_retries is not None else _cfg._GEMINI_MAX_RETRIES

    for attempt in range(retries):
        content = _gemini_call(prompt, timeout=_cfg._GEMINI_CALL_TIMEOUT)
        if content and len(content) > 100:
            logging.info(f"Gemini enhanced: {title[:50]}...")
            return content

        if _cfg._GEMINI_CIRCUIT_OPEN:
            break

        if attempt < retries - 1:
            import time

            time.sleep(2)

    logging.info(f"Gemini enhancement failed, falling back: {title[:50]}")
    return ""


def enhance_with_deepseek(item: Dict) -> str:
    """DeepSeek API fallback."""
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        logging.debug("DeepSeek API key not found, skipping")
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")
    url = item.get("url", "")

    if not title:
        return ""

    try:
        prompt = f"""\ub2e4\uc74c \ubcf4\uc548/\uae30\uc220 \ub274\uc2a4\ub97c DevSecOps \uc2e4\ubb34\uc790 \uad00\uc810\uc5d0\uc11c \ubd84\uc11d:
\uc81c\ubaa9: {title}
\uc694\uc57d: {summary}
\ucd9c\ucc98: {url}

\ub2e4\uc74c \ud615\uc2dd\uc73c\ub85c \ud55c\uad6d\uc5b4\ub85c \uc791\uc131 (500-800\uc790):
1. \uae30\uc220\uc801 \ubc30\uacbd \ubc0f \uc704\ud611 \ubd84\uc11d
2. \uc2e4\ubb34 \uc601\ud5a5 \ubd84\uc11d
3. \ub300\uc751 \uccb4\ud06c\ub9ac\uc2a4\ud2b8 (- [ ] \ud615\uc2dd, 3-5\uac1c)

\ub9c8\ud06c\ub2e4\uc6b4 \ud615\uc2dd\uc73c\ub85c \uc791\uc131."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        response = post_with_retry(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
            label="DeepSeek enhance",
        )

        if response is None:
            return ""
        if response.status_code == 200:
            result = response.json()
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            if len(content) > 100:
                logging.info(f"DeepSeek API enhanced: {title[:50]}...")
                return content.strip()
        else:
            logging.warning(f"DeepSeek API returned status {response.status_code}")

    except Exception as e:
        # Transport faults are handled (and retried) inside post_with_retry;
        # anything reaching here is a response-shaping bug, not a flaky network.
        logging.warning(f"DeepSeek API error: {e}")

    return ""


def enhance_with_claude(item: Dict) -> str:
    """Claude API enhancement."""
    api_key = _cfg._CLAUDE_API_KEY
    if not api_key:
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")[:500]
    url = item.get("url", "")
    if not title:
        return ""

    prompt = f"""\ub2e4\uc74c \ubcf4\uc548/\uae30\uc220 \ub274\uc2a4\ub97c DevSecOps \uc2e4\ubb34\uc790 \uad00\uc810\uc5d0\uc11c \ubd84\uc11d:
\uc81c\ubaa9: {title}
\uc694\uc57d: {summary}
\ucd9c\ucc98: {url}

\ub2e4\uc74c \ud615\uc2dd\uc73c\ub85c \ud55c\uad6d\uc5b4\ub85c \uc791\uc131 (500-800\uc790):
1. \uae30\uc220\uc801 \ubc30\uacbd \ubc0f \uc704\ud611 \ubd84\uc11d
2. \uc2e4\ubb34 \uc601\ud5a5 \ubd84\uc11d
3. \ub300\uc751 \uccb4\ud06c\ub9ac\uc2a4\ud2b8 (- [ ] \ud615\uc2dd, 3-5\uac1c)
4. \uc6b0\uc120\uc21c\uc704(P0/P1/P2) \uc81c\uc548

\ub9c8\ud06c\ub2e4\uc6b4 \ud615\uc2dd\uc73c\ub85c \uc791\uc131."""

    try:
        import requests

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": _cfg._CLAUDE_MODEL,
                "max_tokens": 1200,
                "temperature": 0.4,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            parts = data.get("content", [])
            text_parts = [
                part.get("text", "") for part in parts if part.get("type") == "text"
            ]
            content = "\n".join(text_parts).strip()
            if len(content) > 100:
                logging.info(f"Claude enhanced: {title[:50]}...")
                return content
        else:
            logging.warning(f"Claude API returned status {response.status_code}")
    except ImportError:
        logging.warning("requests library not available for Claude API")
    except Exception as e:
        logging.warning(f"Claude API error: {e}")

    return ""


def enhance_with_openai_codex_medium(item: Dict) -> str:
    """OpenAI Codex Medium enhancement."""
    api_key = _cfg._OPENAI_API_KEY
    if not api_key:
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")[:500]
    url = item.get("url", "")
    if not title:
        return ""

    prompt = f"""\ub2e4\uc74c \ubcf4\uc548/\uae30\uc220 \ub274\uc2a4\ub97c DevSecOps \uc2e4\ubb34\uc790 \uad00\uc810\uc5d0\uc11c \ubd84\uc11d:
\uc81c\ubaa9: {title}
\uc694\uc57d: {summary}
\ucd9c\ucc98: {url}

\ub2e4\uc74c \ud615\uc2dd\uc73c\ub85c \ud55c\uad6d\uc5b4\ub85c \uc791\uc131 (500-800\uc790):
1. \uae30\uc220\uc801 \ubc30\uacbd \ubc0f \uc704\ud611 \ubd84\uc11d
2. \uc2e4\ubb34 \uc601\ud5a5 \ubd84\uc11d
3. \ub300\uc751 \uccb4\ud06c\ub9ac\uc2a4\ud2b8 (- [ ] \ud615\uc2dd, 3-5\uac1c)
4. \uc6b0\uc120\uc21c\uc704(P0/P1/P2) \uc81c\uc548

\ub9c8\ud06c\ub2e4\uc6b4 \ud615\uc2dd\uc73c\ub85c \uc791\uc131."""

    try:
        import requests

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _cfg._OPENAI_Codex_MODEL,
                "temperature": 0.4,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if len(content) > 100:
                logging.info(f"OpenAI Codex enhanced: {title[:50]}...")
                return content
        else:
            logging.warning(f"OpenAI API returned status {response.status_code}")
    except ImportError:
        logging.warning("requests library not available for OpenAI API")
    except Exception as e:
        logging.warning(f"OpenAI API error: {e}")

    return ""


def enhance_with_openai_gpt54(item: Dict) -> str:
    """OpenAI GPT-5.4 enhancement."""
    api_key = _cfg._OPENAI_API_KEY
    if not api_key:
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")[:500]
    url = item.get("url", "")
    if not title:
        return ""

    prompt = f"""\ub2e4\uc74c \ubcf4\uc548/\uae30\uc220 \ub274\uc2a4\ub97c DevSecOps \uc2e4\ubb34\uc790 \uad00\uc810\uc5d0\uc11c \ubd84\uc11d:
\uc81c\ubaa9: {title}
\uc694\uc57d: {summary}
\ucd9c\ucc98: {url}

\ub2e4\uc74c \ud615\uc2dd\uc73c\ub85c \ud55c\uad6d\uc5b4\ub85c \uc791\uc131 (500-800\uc790):
1. \uae30\uc220\uc801 \ubc30\uacbd \ubc0f \uc704\ud611 \ubd84\uc11d
2. \uc2e4\ubb34 \uc601\ud5a5 \ubd84\uc11d
3. \ub300\uc751 \uccb4\ud06c\ub9ac\uc2a4\ud2b8 (- [ ] \ud615\uc2dd, 3-5\uac1c)
4. \uc6b0\uc120\uc21c\uc704(P0/P1/P2) \uc81c\uc548

\ub9c8\ud06c\ub2e4\uc6b4 \ud615\uc2dd\uc73c\ub85c \uc791\uc131."""

    try:
        import requests

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _cfg._OPENAI_GPT54_MODEL,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if len(content) > 100:
                logging.info(f"OpenAI GPT-5.4 enhanced: {title[:50]}...")
                return content
        else:
            logging.warning(
                f"OpenAI GPT-5.4 API returned status {response.status_code}"
            )
    except ImportError:
        logging.warning("requests library not available for OpenAI API")
    except Exception as e:
        logging.warning(f"OpenAI GPT-5.4 API error: {e}")

    return ""


def enhance_content_with_fallback(item: Dict) -> str:
    """3-stage fallback chain: Claude -> Gemini CLI -> DeepSeek API -> Template."""
    title_short = item.get("title", "")[:50]

    if _cfg._AI_MODE == "none":
        title_short = item.get("title", "")[:50]
        logging.info(f"Template fallback (AI disabled): {title_short}")
        return ""

    if _cfg._AI_MODE in {"auto", "claude"}:
        content = enhance_with_claude(item)
        if content:
            logging.info(f"Claude: {title_short}")
            return content

    if _cfg._AI_MODE in {"auto", "gemini"} and check_gemini_available():
        content = enhance_with_gemini(item)
        if content:
            logging.info(f"Gemini CLI: {title_short}")
            return content

    if _cfg._AI_MODE in {"auto", "gpt-5.4"}:
        content = enhance_with_openai_gpt54(item)
        if content:
            logging.info(f"OpenAI GPT-5.4: {title_short}")
            return content

    if _cfg._AI_MODE in {"auto", "codex-medium"}:
        content = enhance_with_openai_codex_medium(item)
        if content:
            logging.info(f"OpenAI Codex: {title_short}")
            return content

    content = ""
    if _cfg._AI_MODE in {"auto", "gemini", "deepseek"}:
        content = enhance_with_deepseek(item)
    if content:
        logging.info(f"DeepSeek API: {title_short}")
        return content

    logging.info(f"Template fallback: {title_short}")
    return ""
