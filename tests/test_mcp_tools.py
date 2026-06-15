import os
from mcp_server.tools.search import _guess_sector, _mock_search, discover_ethiopian_enterprises
from mcp_server.tools.tenders import fetch_active_tenders
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline, _validate_payload
import pytest


class TestSearchTool:
    def test_mock_search_returns_sector_specific(self):
        results = _mock_search("bank")
        assert len(results) > 0
        assert results[0]["sector"] == "Finance"

    def test_mock_search_returns_default(self):
        results = _mock_search("unknown sector query")
        assert len(results) == 2

    def test_guess_sector_finance(self):
        assert _guess_sector("Bank of Ethiopia", "financial services") == "Finance"

    def test_guess_sector_technology(self):
        assert _guess_sector("Tech Solutions PLC", "software development") == "Technology"

    def test_guess_sector_general(self):
        assert _guess_sector("Unknown Corp", "some random text") == "General"

    def test_discover_without_api_key_falls_back_to_mock(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_CSE_ID", raising=False)
        results = discover_ethiopian_enterprises("bank")
        assert len(results) > 0


class TestTendersTool:
    def test_fetch_active_tenders_returns_mock_when_no_live(self):
        tenders = fetch_active_tenders()
        assert len(tenders) > 0
        assert all(t.get("source") == "mock" for t in tenders)

    def test_fetch_active_tenders_filters_by_sector(self):
        tenders = fetch_active_tenders("Security")
        assert all("Security" in t.get("procurement_category", "") for t in tenders)


class TestN8nHookTool:
    def test_validate_payload_missing_field(self):
        result = _validate_payload({})
        assert result is not None
        assert "Missing required field" in result

    def test_validate_payload_empty_field(self):
        result = _validate_payload({"lead_name": "", "tender_requirements": "test", "validated_email": "test@test.com", "email_body": "test"})
        assert result is not None
        assert "empty" in result

    def test_validate_payload_valid(self):
        payload = {"lead_name": "Test", "tender_requirements": "test", "validated_email": "test@test.com", "email_body": "test"}
        result = _validate_payload(payload)
        assert result is None

    def test_trigger_without_url_returns_mock_ack(self, monkeypatch):
        monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
        result = trigger_n8n_marketing_pipeline({"lead_name": "Test", "tender_requirements": "test", "validated_email": "test@test.com", "email_body": "test"})
        assert result["response"]["status"] == "mock_acknowledged"
