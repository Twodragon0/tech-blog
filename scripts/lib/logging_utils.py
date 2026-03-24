"""Centralized logging utility for tech-blog scripts.

Consolidates log_message() previously duplicated across 13+ scripts.
All scripts should import from here.
"""

import logging
import sys
from datetime import datetime

from scripts.lib.security import mask_sensitive_info

# Configure root logger once
_logger = logging.getLogger("tech-blog")
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
    )
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def log_message(message: str, level: str = "INFO") -> None:
    """Log a message with automatic sensitive data masking.

    Args:
        message: Message to log (will be masked automatically)
        level: Log level - INFO, WARNING, ERROR, SUCCESS, DEBUG
    """
    safe_message = mask_sensitive_info(message)

    level_map = {
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "DEBUG": logging.DEBUG,
        "SUCCESS": logging.INFO,
    }

    log_level = level_map.get(level.upper(), logging.INFO)
    _logger.log(log_level, safe_message)
