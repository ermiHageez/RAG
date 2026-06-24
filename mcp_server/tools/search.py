import urllib.parse
from typing import Any, Dict, List
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup

from app.ml.training_sink import record_training_event


def primary_duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Primary search engine: DuckDuckGo."""
    results = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            })
    return results


def fallback_google_scraper(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Fallback engine: zero-auth Google organic scrape via BeautifulSoup."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}&num={max_results}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=8)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for g in soup.select("div.g")[:max_results]:
        title_el = g.select_one("h3")
        link_el = g.select_one("a")
        snippet_el = g.select_one("div[style*='-webkit-line-clamp'], .VwiC3b")
        if title_el and link_el:
            results.append({
                "title": title_el.get_text(),
                "url": link_el.get("href", ""),
                "snippet": snippet_el.get_text() if snippet_el else "No context available.",
            })
    return results


def resilient_web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Unified search with automatic failover: DDGS → Google scrape."""
    print(f"[SearchRouter] Primary: DuckDuckGo for '{query}'")
    try:
        return primary_duckduckgo_search(query, max_results)
    except Exception as ddg_err:
        print(f"[SearchRouter] DuckDuckGo failed ({ddg_err}), falling back to Google scrape")
        try:
            return fallback_google_scraper(query, max_results)
        except Exception as google_err:
            print(f"[SearchRouter] Google scrape also failed ({google_err})")
            return [
                {
                    "title": "Search unavailable",
                    "url": "",
                    "snippet": f"All search engines exhausted. DDG: {ddg_err}. Google: {google_err}",
                }
            ]


def _guess_sector(title: str, snippet: str) -> str:
    text = (title + " " + snippet).lower()
    if any(w in text for w in ["bank", "finance", "insurance", "microfinance"]):
        return "Finance"
    if any(w in text for w in ["logistics", "transport", "shipping"]):
        return "Logistics"
    if any(w in text for w in ["manufacturing", "factory", "industrial"]):
        return "Manufacturing"
    if any(w in text for w in ["government", "ministry", "authority"]):
        return "Government"
    if any(w in text for w in ["tech", "software", "it ", "digital"]):
        return "Technology"
    if any(w in text for w in ["agriculture", "farm", "agro"]):
        return "Agriculture"
    if any(w in text for w in ["hotel", "tourism", "hospitality"]):
        return "Hospitality"
    return "General"


def discover_ethiopian_enterprises(query: str) -> List[Dict[str, Any]]:
    """Compatibility wrapper used by lead_agent. Returns enriched result format."""
    raw = resilient_web_search(query, max_results=5)
    results = []
    for item in raw:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        results.append({
            "name": title,
            "sector": _guess_sector(title, snippet),
            "location": "Ethiopia",
            "description": snippet,
            "contact": "",
            "link": item.get("url", ""),
        })
    try:
        record_training_event(
            "mcp.search",
            input={"query": query},
            output=results,
            source="mcp",
            metadata={"tool": "discover_ethiopian_enterprises", "result_count": len(results)},
        )
    except Exception:
        pass
    return results
