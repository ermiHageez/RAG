import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    from src.api import app
    return TestClient(app)


class TestMcpTendersEndpoint:
    ENDPOINT = "/mcp/tenders"

    def test_returns_empty_when_scrapers_find_nothing(self, client):
        with patch("mcp_server.tools.tenders._scrape_2merkato_news", return_value=[]):
            with patch("mcp_server.tools.tenders._scrape_addisbiz_opportunities", return_value=[]):
                resp = client.post(self.ENDPOINT, json={"query": "ERP", "max_results": 5})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["results"] == []
        assert body["total"] == 0

    def test_returns_results_when_scraper_succeeds(self, client):
        mock_results = [
            {
                "title": "ERP System Tender",
                "description": "Implementation of ERP system",
                "deadline": "",
                "url": "https://www.2merkato.com/tender/1",
                "procurement_category": "ICT",
                "source": "2merkato.com",
            }
        ]
        with patch("mcp_server.tools.tenders._scrape_2merkato_news", return_value=mock_results):
            with patch("mcp_server.tools.tenders._scrape_addisbiz_opportunities", return_value=[]):
                resp = client.post(self.ENDPOINT, json={"query": "ERP", "max_results": 5})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert len(body["results"]) == 1
        assert body["total"] == 1
        assert body["results"][0]["title"] == "ERP System Tender"

    def test_works_with_empty_query(self, client):
        with patch("mcp_server.tools.tenders._scrape_2merkato_news", return_value=[]):
            with patch("mcp_server.tools.tenders._scrape_addisbiz_opportunities", return_value=[]):
                resp = client.post(self.ENDPOINT, json={"query": "", "max_results": 5})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["total"] == 0

    def test_missing_query_returns_422(self, client):
        resp = client.post(self.ENDPOINT, json={})
        assert resp.status_code == 422

    def test_returns_500_on_scraper_exception(self, client):
        with patch("mcp_server.tools.tenders._scrape_2merkato_news", side_effect=Exception("site down")):
            resp = client.post(self.ENDPOINT, json={"query": "ERP", "max_results": 5})
        assert resp.status_code == 500


class TestTendersTool:
    def test_fetch_active_tenders_calls_both_scrapers(self):
        from mcp_server.tools.tenders import fetch_active_tenders
        with patch("mcp_server.tools.tenders._scrape_2merkato_news", return_value=[{"title": "a"}]):
            with patch("mcp_server.tools.tenders._scrape_addisbiz_opportunities", return_value=[{"title": "b"}]):
                results = fetch_active_tenders(sector="ICT")
        assert len(results) == 2

    def test_fetch_active_tenders_aggregates_empty(self):
        from mcp_server.tools.tenders import fetch_active_tenders
        with patch("mcp_server.tools.tenders._scrape_2merkato_news", return_value=[]):
            with patch("mcp_server.tools.tenders._scrape_addisbiz_opportunities", return_value=[]):
                results = fetch_active_tenders(sector=None)
        assert results == []


class TestMcpDirectoryEndpoint:
    ENDPOINT = "/mcp/directory"

    def test_returns_empty_when_no_companies_found(self, client):
        with patch("mcp_server.tools.directory.scrape_2merkato_directory", return_value=[]):
            with patch("mcp_server.tools.directory.scrape_addisbiz_directory", return_value=[]):
                with patch("mcp_server.tools.directory.scrape_ethyp_directory", return_value=[]):
                    resp = client.post(self.ENDPOINT, json={"query": "tech", "max_results": 5})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["results"] == []
        assert body["total"] == 0

    def test_returns_company_results(self, client):
        mock = [{
            "name": "Tech Corp",
            "sector": "Technology",
            "location": "Addis Ababa, Ethiopia",
            "description": "A tech company",
            "phone": "+251 911 123456",
            "link": "https://example.com",
            "source": "ethyp.com",
        }]
        with patch("mcp_server.tools.directory.scrape_2merkato_directory", return_value=[]):
            with patch("mcp_server.tools.directory.scrape_addisbiz_directory", return_value=[]):
                with patch("mcp_server.tools.directory.scrape_ethyp_directory", return_value=mock):
                    resp = client.post(self.ENDPOINT, json={"query": "tech", "max_results": 5})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert len(body["results"]) == 1
        assert body["total"] == 1
        assert body["results"][0]["name"] == "Tech Corp"

    def test_deduplicates_duplicate_names(self, client):
        mock = [
            {"name": "Tech Corp", "sector": "Technology", "location": "AA", "description": "", "phone": "", "link": "", "source": "a"},
            {"name": "Tech Corp", "sector": "Technology", "location": "AA", "description": "", "phone": "", "link": "", "source": "b"},
        ]
        with patch("mcp_server.tools.directory.scrape_2merkato_directory", return_value=[]):
            with patch("mcp_server.tools.directory.scrape_addisbiz_directory", return_value=mock):
                with patch("mcp_server.tools.directory.scrape_ethyp_directory", return_value=[]):
                    resp = client.post(self.ENDPOINT, json={"query": "tech", "max_results": 10})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1  # deduplicated
