"""Tests for the parser service."""

from daily_scheduler.services.parser import (
    extract_html_report,
    extract_recommendations,
    extract_summary,
)


class TestExtractRecommendations:
    def test_extracts_valid_json(self):
        raw = """
        <html><body>Report content</body></html>
        <!-- REC_START
        [
          {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "market": "NASDAQ",
            "direction": "LONG",
            "timeframe": "SWING",
            "entry_price": 185.0,
            "target_price": 195.0,
            "stop_loss": 180.0,
            "sector": "Technology",
            "rationale": "Strong earnings"
          }
        ]
        REC_END -->
        """
        recs = extract_recommendations(raw)
        assert len(recs) == 1
        assert recs[0]["ticker"] == "AAPL"
        assert recs[0]["entry_price"] == 185.0

    def test_returns_empty_on_no_markers(self):
        recs = extract_recommendations("<html>no markers here</html>")
        assert recs == []

    def test_returns_empty_on_invalid_json(self):
        raw = "<!-- REC_START\n{invalid json}\nREC_END -->"
        recs = extract_recommendations(raw)
        assert recs == []

    def test_multiple_recommendations(self):
        raw = """<!-- REC_START
        [
          {"ticker": "AAPL", "name": "Apple", "market": "NASDAQ", "direction": "LONG",
           "timeframe": "DAY", "entry_price": 185, "target_price": 190, "stop_loss": 182,
           "sector": "Tech", "rationale": "test"},
          {"ticker": "TSLA", "name": "Tesla", "market": "NASDAQ", "direction": "SHORT",
           "timeframe": "SWING", "entry_price": 250, "target_price": 230, "stop_loss": 260,
           "sector": "Auto", "rationale": "test2"}
        ]
        REC_END -->"""
        recs = extract_recommendations(raw)
        assert len(recs) == 2
        assert recs[1]["ticker"] == "TSLA"
        assert recs[1]["direction"] == "SHORT"


class TestExtractHtmlReport:
    def test_extracts_full_html_document(self):
        raw = "some preamble\n<!DOCTYPE html><html><body>content</body></html>\nmore text"
        html = extract_html_report(raw)
        assert html.startswith("<!DOCTYPE html>")
        assert html.endswith("</html>")

    def test_returns_raw_if_html_tags_present(self):
        raw = "<div>some content</div><table>data</table>"
        html = extract_html_report(raw)
        assert "<div>" in html

    def test_wraps_plain_text(self):
        raw = "just plain text with no html"
        html = extract_html_report(raw)
        assert "<!DOCTYPE html>" in html
        assert "just plain text" in html


class TestExtractSummary:
    def test_strips_html_and_truncates(self):
        raw = "<h1>Title</h1><p>" + "a" * 300 + "</p>"
        summary = extract_summary(raw)
        assert len(summary) <= 203  # 200 + "..."
        assert "<h1>" not in summary

    def test_short_text_no_ellipsis(self):
        summary = extract_summary("<p>Short text</p>")
        assert summary == "Short text"
        assert "..." not in summary
