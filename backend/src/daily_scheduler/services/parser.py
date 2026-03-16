"""Parser service — extract structured data from Claude's report output."""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)

REC_PATTERN = re.compile(
    r"<!--\s*REC_START\s*\n(.*?)\nREC_END\s*-->",
    re.DOTALL,
)


def extract_recommendations(raw_output: str) -> list[dict]:
    """Extract recommendation JSON from Claude's HTML output.

    Looks for <!-- REC_START --> ... <!-- REC_END --> markers.
    Returns a list of recommendation dicts.
    """
    match = REC_PATTERN.search(raw_output)
    if not match:
        logger.warning("No REC_START/REC_END markers found in Claude output")
        return []

    json_str = match.group(1).strip()
    try:
        data = json.loads(json_str)
        if isinstance(data, list):
            return data
        logger.warning("Parsed JSON is not a list: %s", type(data))
        return []
    except json.JSONDecodeError as e:
        logger.error("Failed to parse recommendation JSON: %s", e)
        logger.debug("Raw JSON string: %s", json_str[:500])
        return []


def extract_html_report(raw_output: str) -> str:
    """Extract the HTML content from Claude's output.

    If the output contains a full HTML document, extract it.
    Otherwise, return the raw output wrapped in basic HTML.
    """
    # Look for <!DOCTYPE html> or <html>
    html_match = re.search(r"(<!DOCTYPE html>.*</html>)", raw_output, re.DOTALL | re.IGNORECASE)
    if html_match:
        return html_match.group(1)

    # If no full HTML document, check for HTML-like content
    if "<div" in raw_output or "<table" in raw_output:
        return raw_output

    # Wrap plain text in basic HTML
    return f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>Daily Report</title></head>
<body>{raw_output}</body>
</html>"""


def extract_summary(raw_output: str) -> str:
    """Extract a brief summary from the report (first meaningful paragraph)."""
    # Remove HTML tags for summary
    text = re.sub(r"<[^>]+>", "", raw_output)
    text = re.sub(r"\s+", " ", text).strip()
    # Take first 200 chars as summary
    return text[:200] + "..." if len(text) > 200 else text
