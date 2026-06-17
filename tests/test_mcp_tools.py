from mcp_server.tools.search import (
    _guess_sector,
    resilient_web_search,
    primary_duckduckgo_search,
    fallback_google_scraper,
    discover_ethiopian_enterprises,
)
from unittest.mock import patch, MagicMock
import pytest


class TestGuessSector:
    def test_finance(self):
        assert _guess_sector("Bank of Ethiopia", "financial services") == "Finance"

    def test_technology(self):
        assert _guess_sector("Tech Solutions PLC", "software development") == "Technology"

    def test_general(self):
        assert _guess_sector("Unknown Corp", "some random text") == "General"


class TestPrimaryDuckDuckGo:
    def test_returns_formatted_results(self):
        mock_items = [
            {"title": "Result A", "href": "https://a.com", "body": "Snippet A"},
            {"title": "Result B", "href": "https://b.com", "body": "Snippet B"},
        ]

        class MockDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                return mock_items

        with patch("mcp_server.tools.search.DDGS", return_value=MockDDGS()):
            results = primary_duckduckgo_search("test", 5)
            assert len(results) == 2
            assert results[0] == {"title": "Result A", "url": "https://a.com", "snippet": "Snippet A"}
            assert results[1] == {"title": "Result B", "url": "https://b.com", "snippet": "Snippet B"}

    def test_returns_empty_when_no_results(self):
        class MockDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                return []

        with patch("mcp_server.tools.search.DDGS", return_value=MockDDGS()):
            results = primary_duckduckgo_search("test", 5)
            assert results == []


class TestFallbackGoogleScraper:
    def test_parses_google_results(self):
        html = """<html><body>
        <div class="g">
            <h3>Result One</h3>
            <a href="https://one.com">Result One</a>
            <div class="VwiC3b">Snippet one</div>
        </div>
        <div class="g">
            <h3>Result Two</h3>
            <a href="https://two.com">Result Two</a>
            <div class="VwiC3b">Snippet two</div>
        </div>
        </body></html>"""

        with patch("mcp_server.tools.search.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = html
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            results = fallback_google_scraper("test", 5)
            assert len(results) == 2
            assert results[0] == {"title": "Result One", "url": "https://one.com", "snippet": "Snippet one"}
            assert results[1] == {"title": "Result Two", "url": "https://two.com", "snippet": "Snippet two"}

    def test_returns_empty_on_no_results(self):
        html = "<html><body></body></html>"
        with patch("mcp_server.tools.search.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = html
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp
            results = fallback_google_scraper("test", 5)
            assert results == []


class TestResilientWebSearch:
    def test_primary_success_returns_ddg_results(self):
        mock_items = [
            {"title": "A", "href": "https://a.com", "body": "A snippet"},
        ]

        class MockDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                return mock_items

        with patch("mcp_server.tools.search.DDGS", return_value=MockDDGS()):
            results = resilient_web_search("test")
        assert len(results) == 1
        assert results[0]["title"] == "A"

    def test_primary_fails_fallback_succeeds(self):
        class FailingDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                raise Exception("429 Too Many Requests")

        html = """<html><body>
        <div class="g"><h3>Fallback Result</h3><a href="https://fb.com">link</a><div class="VwiC3b">fb snippet</div></div>
        </body></html>"""

        with patch("mcp_server.tools.search.DDGS", return_value=FailingDDGS()):
            with patch("mcp_server.tools.search.requests.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.text = html
                mock_resp.raise_for_status.return_value = None
                mock_get.return_value = mock_resp
                results = resilient_web_search("test")

        assert len(results) == 1
        assert results[0]["title"] == "Fallback Result"
        assert results[0]["snippet"] == "fb snippet"

    def test_both_fail_returns_error_dict(self):
        class FailingDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                raise Exception("DDG down")

        with patch("mcp_server.tools.search.DDGS", return_value=FailingDDGS()):
            with patch("mcp_server.tools.search.requests.get") as mock_get:
                mock_get.side_effect = Exception("Google blocked")
                results = resilient_web_search("test")

        assert len(results) == 1
        assert results[0]["title"] == "Search unavailable"
        assert "DDG down" in results[0]["snippet"]
        assert "Google blocked" in results[0]["snippet"]

    def test_returns_identical_contract_regardless_of_engine(self):
        class MockDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                return [{"title": "X", "href": "https://x.com", "body": "X desc"}]

        with patch("mcp_server.tools.search.DDGS", return_value=MockDDGS()):
            results = resilient_web_search("test")

        for r in results:
            assert "title" in r
            assert "url" in r
            assert "snippet" in r
            assert isinstance(r["title"], str)
            assert isinstance(r["url"], str)
            assert isinstance(r["snippet"], str)


class TestDiscoverEthiopianEnterprises:
    def test_returns_enriched_format(self):
        class MockDDGS:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def text(self, query, max_results=5):
                return [{"title": "Tech Corp", "href": "https://tech.et", "body": "A technology company in Ethiopia"}]

        with patch("mcp_server.tools.search.DDGS", return_value=MockDDGS()):
            results = discover_ethiopian_enterprises("tech Ethiopia")

        assert len(results) == 1
        r = results[0]
        assert r["name"] == "Tech Corp"
        assert r["sector"] == "Technology"
        assert r["location"] == "Ethiopia"
        assert "technology company" in r["description"]
        assert r["contact"] == ""
        assert r["link"] == "https://tech.et"


class TestN8nHook:
    def test_validate_payload_missing_field(self):
        from mcp_server.tools.n8n_hook import _validate_payload
        result = _validate_payload({})
        assert result is not None
        assert "Missing required field" in result

    def test_validate_payload_empty_field(self):
        from mcp_server.tools.n8n_hook import _validate_payload
        result = _validate_payload({"lead_name": "", "tender_requirements": "test", "validated_email": "test@test.com", "email_body": "test"})
        assert result is not None
        assert "empty" in result

    def test_validate_payload_valid(self):
        from mcp_server.tools.n8n_hook import _validate_payload
        payload = {"lead_name": "Test", "tender_requirements": "test", "validated_email": "test@test.com", "email_body": "test"}
        result = _validate_payload(payload)
        assert result is None

    def test_trigger_without_url_returns_mock_ack(self, monkeypatch):
        from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline
        monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
        result = trigger_n8n_marketing_pipeline({"lead_name": "Test", "tender_requirements": "test", "validated_email": "test@test.com", "email_body": "test"})
        assert result["response"]["status"] == "mock_acknowledged"
