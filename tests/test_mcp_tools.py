from mcp_server.tools.search import _mock_search, _guess_sector, discover_ethiopian_enterprises
from mcp_server.tools.tenders import fetch_active_tenders
from mcp_server.tools.n8n_hook import _validate_payload, trigger_n8n_marketing_pipeline


class TestSearchTool:
    def test_mock_search_returns_sector_specific(self):
        results = _mock_search("banking finance Ethiopia")
        assert all(r["sector"] == "Finance" for r in results)

    def test_mock_search_returns_default(self):
        results = _mock_search("unknown sector query")
        assert len(results) == 2
        assert results[0]["sector"] == "General"

    def test_guess_sector_finance(self):
        assert _guess_sector("Bank of Ethiopia", "leading bank") == "Finance"

    def test_guess_sector_technology(self):
        assert _guess_sector("Tech Company PLC", "software solutions") == "Technology"

    def test_guess_sector_general(self):
        assert _guess_sector("Random Company", "doing business") == "General"

    def test_discover_without_api_key_falls_back_to_mock(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_CSE_ID", raising=False)
        results = discover_ethiopian_enterprises("bank")
        assert len(results) > 0


class TestTendersTool:
    def test_fetch_active_tenders_returns_mock_when_no_live(self, monkeypatch):
        monkeypatch.setattr("mcp_server.tools.tenders._scrape_ppa", lambda s: [])
        results = fetch_active_tenders()
        assert len(results) > 0
        assert all(t["source"] == "mock" for t in results)

    def test_fetch_active_tenders_filters_by_sector(self, monkeypatch):
        monkeypatch.setattr("mcp_server.tools.tenders._scrape_ppa", lambda s: [])
        results = fetch_active_tenders(sector="Security")
        assert all("security" in (t["title"] + t["description"]).lower() for t in results)


class TestN8nHookTool:
    def test_validate_payload_missing_field(self):
        error = _validate_payload({"lead_name": "test"})
        assert error is not None
        assert "tender_requirements" in error

    def test_validate_payload_empty_field(self):
        error = _validate_payload({"lead_name": "", "tender_requirements": "req", "validated_email": "a@b.com", "email_body": "body"})
        assert error is not None

    def test_validate_payload_valid(self):
        error = _validate_payload({"lead_name": "Test", "tender_requirements": "req", "validated_email": "a@b.com", "email_body": "body"})
        assert error is None

    def test_trigger_without_url_returns_mock_ack(self, monkeypatch):
        monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
        result = trigger_n8n_marketing_pipeline({"lead_name": "Test", "tender_requirements": "req", "validated_email": "a@b.com", "email_body": "body"})
        assert result["success"] is True
        assert result["response"]["status"] == "mock_acknowledged"
