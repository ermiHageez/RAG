from unittest.mock import patch, MagicMock
from mcp_server.tools.directory import (
    _guess_sector_from_name,
    discover_companies,
    scrape_2merkato_directory,
    scrape_addisbiz_directory,
    scrape_ethyp_directory,
)


class TestGuessSectorFromName:
    def test_finance(self):
        assert _guess_sector_from_name("Bank of Ethiopia", "financial services") == "Finance"

    def test_technology(self):
        assert _guess_sector_from_name("Tech Solutions PLC", "software development") == "Technology"

    def test_general(self):
        assert _guess_sector_from_name("Unknown Corp", "some random text") == "General"

    def test_agro(self):
        assert _guess_sector_from_name("Green Agro Farm", "Ethiopian farming") == "Agriculture"

    def test_construction(self):
        assert _guess_sector_from_name("BuildWell Construction", "building contractor") == "Construction"

    def test_health(self):
        assert _guess_sector_from_name("St. Mary Hospital", "medical services") == "Health"

    def test_education(self):
        assert _guess_sector_from_name("Addis College", "higher education training") == "Education"

    def test_import_export(self):
        assert _guess_sector_from_name("Global Trade PLC", "import and export") == "Import/Export"

    def test_hospitality(self):
        assert _guess_sector_from_name("Sheraton Hotel", "tourism and travel") == "Hospitality"

    def test_media_telecom(self):
        assert _guess_sector_from_name("Ethio Telecom", "communication services") == "Media & Telecom"


MERKATO_HTML = """<html><body>
<div class="t3-content">
<div id="listings">
<div class="pagination"><ul class="pagination-list"><li class="disabled"><a>1</a></li></ul></div>
<div class="row-fluid">
<div class="span12 listing-summary-featured">
<div class="row-fluid"><div class="span12 heading">
<h4><a href="/directory/123-abc-corp">ABC Corp</a></h4>
</div></div>
<div class="row-fluid"><div class="span12 body">
<div class="span3"><img src="img.jpg"/></div>
<div class="span9">ABC Corp provides IT services in Ethiopia<h5 class="pull-right"><i class="icon-phone"></i> +251 911 123456<a>show all digits</a></h5></div>
</div></div>
<div class="row-fluid"><div class="span12 footer">
<small><i class="icon-map-marker"></i> Addis Ababa, Ethiopia</small>
</div></div>
</div>
</div>
</div>
</body></html>"""


MERKATO_CAT_HTML = """<html><body>
<div class="t3-content">
<div class="row-fluid mtree_category">
<div class="span6"><h4><a href="/directory/1085/">Bank and Insurance</a> <span class="count">(69)</span></h4></div>
</div>
<div class="row-fluid mtree_category">
<div class="span6"><h4><a href="/directory/2/">Ethiopian Importers</a> <span class="count">(9516)</span></h4></div>
</div>
</div>
</body></html>"""


ADDISBIZ_HTML = """<html><body>
<div class="entry-content">
<article>
<h2 class="entry-title"><a href="https://addisbiz.com/tech-company">Tech Company</a></h2>
<div class="entry-content"><p>A technology company in Ethiopia</p></div>
</article>
<article>
<h2 class="entry-title"><a href="https://addisbiz.com/another-firm">Another Firm</a></h2>
<div class="entry-content"><p>Another business in Ethiopia</p></div>
</article>
<ul><li><a href="/business-directory/?category=information-technology">Information Technology (1065)</a></li></ul>
</div>
</body></html>"""


ETHYP_HTML = """<html><body>
<div class="company g_0" data-cmpid="1">
<div class="company_header">
<h3><a href="/company/1/ABC_CORP">ABC Corp</a></h3>
<div class="address"><b>Addis Ababa</b>, Ethiopia</div>
</div>
<div class="tagline">Leading tech company in Ethiopia</div>
<div class="cont"><div class="s"><i class="fa fa-phone"></i><span>+251 911 111111</span></div></div>
</div>
<div class="company with_img g_0" data-cmpid="2">
<div class="company_header">
<h3><a href="/company/2/XYZ_PLC">XYZ PLC</a></h3>
<div class="address"><b>Adama</b>, Ethiopia</div>
</div>
<div class="tagline">Manufacturing and industry</div>
<div class="cont"><div class="s"><i class="fa fa-phone"></i><span>+251 922 222222</span></div></div>
</div>
</body></html>"""


class TestScrape2merkatoDirectory:
    def test_returns_companies_from_html(self):
        with patch("requests.get") as mock_get:
            def side_effect(url, **kw):
                resp = MagicMock()
                resp.raise_for_status.return_value = None
                if "directory/?start" in url or "page:" in url:
                    resp.text = "<html><body></body></html>"
                elif "/directory/1085/" in url:
                    resp.text = MERKATO_HTML
                else:
                    resp.text = MERKATO_CAT_HTML
                return resp
            mock_get.side_effect = side_effect
            results = scrape_2merkato_directory(sector="bank", max_pages=1)

        assert len(results) >= 1
        assert results[0]["name"] == "ABC Corp"
        assert results[0]["phone"].startswith("+251 911")
        assert "Addis Ababa" in results[0]["location"]
        assert results[0]["source"] == "2merkato.com"

    def test_returns_empty_on_http_error(self):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("HTTP error")
            results = scrape_2merkato_directory(sector="bank", max_pages=1)
        assert results == []


class TestScrapeAddisbizDirectory:
    def test_returns_companies_from_html(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.text = ADDISBIZ_HTML
            mock_get.return_value.raise_for_status.return_value = None
            results = scrape_addisbiz_directory(sector="tech", max_pages=1)
        assert len(results) == 2
        assert results[0]["name"] == "Tech Company"
        assert results[0]["source"] == "addisbiz.com"

    def test_returns_empty_on_error(self):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("error")
            results = scrape_addisbiz_directory(sector="tech")
        assert results == []


class TestScrapeEthypDirectory:
    def test_returns_companies_from_html(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.text = ETHYP_HTML
            mock_get.return_value.raise_for_status.return_value = None
            results = scrape_ethyp_directory(sector="tech", max_pages=1)
        assert len(results) == 2
        assert results[0]["name"] == "ABC Corp"
        assert results[0]["phone"] == "+251 911 111111"
        assert "Addis Ababa" in results[0]["location"]
        assert results[0]["source"] == "ethyp.com"
        assert results[1]["name"] == "XYZ PLC"

    def test_skips_ad_items(self):
        html = ETHYP_HTML.replace(
            '<div class="company g_0"',
            '<div class="company g_0 company_ad"',
        )
        with patch("requests.get") as mock_get:
            mock_get.return_value.text = html
            mock_get.return_value.raise_for_status.return_value = None
            results = scrape_ethyp_directory(sector="tech", max_pages=1)
        # should have 1 from "with_img" and skip the ad
        assert len(results) == 1

    def test_returns_empty_on_http_error(self):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("HTTP error")
            results = scrape_ethyp_directory(sector="tech")
        assert results == []


class TestDiscoverCompanies:
    def test_aggregates_across_all_sources(self):
        mock_company = [{"name": "Test Co", "sector": "Tech", "location": "AA", "description": "", "phone": "", "link": "", "source": "ethyp.com"}]
        with patch("mcp_server.tools.directory.scrape_2merkato_directory", return_value=[]):
            with patch("mcp_server.tools.directory.scrape_addisbiz_directory", return_value=[]):
                with patch("mcp_server.tools.directory.scrape_ethyp_directory", return_value=mock_company):
                    results = discover_companies(sector="tech", max_per_source=10)
        assert len(results) == 1
        assert results[0]["name"] == "Test Co"

    def test_deduplicates(self):
        c = {"name": "Dup Co", "sector": "Tech", "location": "AA", "description": "", "phone": "", "link": "", "source": "a"}
        with patch("mcp_server.tools.directory.scrape_2merkato_directory", return_value=[c]):
            with patch("mcp_server.tools.directory.scrape_addisbiz_directory", return_value=[c]):
                with patch("mcp_server.tools.directory.scrape_ethyp_directory", return_value=[]):
                    results = discover_companies(sector="tech", max_per_source=10)
        assert len(results) == 1  # deduplicated

    def test_respects_max_results(self):
        c = {"name": "Co", "sector": "Tech", "location": "AA", "description": "", "phone": "", "link": "", "source": "a"}
        mock_list = [c.copy() for _ in range(5)]
        for i, item in enumerate(mock_list):
            item["name"] = f"Co {i}"
        with patch("mcp_server.tools.directory.scrape_2merkato_directory", return_value=[]):
            with patch("mcp_server.tools.directory.scrape_addisbiz_directory", return_value=[]):
                with patch("mcp_server.tools.directory.scrape_ethyp_directory", return_value=mock_list):
                    results = discover_companies(sector="tech", max_per_source=2)
        assert len(results) <= 2
