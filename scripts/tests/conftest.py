"""Shared pytest configuration for scripts/tests/.

Disables all external API calls (Gemini, DeepSeek, OpenAI) and patches
module-level globals to prevent network access during testing.
"""

import os
import sys
from pathlib import Path

# --- Environment: disable all API keys before any module import ---
os.environ["GEMINI_API_KEY"] = ""
os.environ["DEEPSEEK_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["NEWS_NO_TRANSLATE"] = "1"

# --- Path setup ---
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Patch module globals to block CLI/network calls ---
import auto_publish_news  # noqa: E402

auto_publish_news._GEMINI_AVAILABLE = False
auto_publish_news._GEMINI_CIRCUIT_OPEN = True
