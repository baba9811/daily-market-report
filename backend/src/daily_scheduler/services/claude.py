"""Claude Code CLI service — runs claude in headless mode via subprocess."""

from __future__ import annotations

import logging
import subprocess
import time

from daily_scheduler.config import get_settings

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 600  # 10 minutes max per invocation


def call_claude(prompt: str, retry: bool = True) -> str:
    """Call Claude Code CLI with the given prompt and return the response.

    Uses `claude -p` for non-interactive (print) mode.
    Retries once on failure if retry=True.
    """
    settings = get_settings()
    cmd = [
        settings.claude_cli_path,
        "-p",
        prompt,
        "--allowedTools",
        "WebSearch,WebFetch",
    ]

    for attempt in range(2 if retry else 1):
        try:
            start = time.time()
            logger.info("Calling Claude CLI (attempt %d)...", attempt + 1)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=str(get_settings().db_path.parent.parent),
            )

            elapsed = time.time() - start
            logger.info("Claude responded in %.1fs (exit code: %d)", elapsed, result.returncode)

            if result.returncode != 0:
                logger.error("Claude CLI error (stderr): %s", result.stderr[:500])
                if attempt == 0 and retry:
                    logger.info("Retrying in 30s...")
                    time.sleep(30)
                    continue
                return ""

            output = result.stdout.strip()
            if not output:
                logger.warning("Claude returned empty output")
                if attempt == 0 and retry:
                    logger.info("Retrying in 30s...")
                    time.sleep(30)
                    continue
                return ""

            return output

        except subprocess.TimeoutExpired:
            logger.error("Claude CLI timed out after %ds", TIMEOUT_SECONDS)
            if attempt == 0 and retry:
                time.sleep(30)
                continue
            return ""
        except FileNotFoundError:
            logger.error("Claude CLI not found at: %s", settings.claude_cli_path)
            return ""

    return ""


def get_generation_time(prompt: str) -> tuple[str, float]:
    """Call Claude and return (response, elapsed_seconds)."""
    start = time.time()
    response = call_claude(prompt)
    elapsed = time.time() - start
    return response, elapsed
