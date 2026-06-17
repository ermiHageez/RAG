import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

PPA_URL = os.getenv("PPA_URL", "https://www.2merkato.com").rstrip("/")
EGP_URL = os.getenv("EGP_URL", "https://addisbiz.com").rstrip("/")


def _keyword_filter(items: List[Dict[str, Any]], keyword: Optional[str]) -> List[Dict[str, Any]]:
    if not keyword:
        return items
    kw = keyword.lower()
    matched = [i for i in items if kw in i["title"].lower() or kw in i["description"].lower()]
    return matched if matched else items


def _scrape_2merkato_news(keyword: Optional[str]) -> List[Dict[str, Any]]:
    import requests
    from bs4 import BeautifulSoup

    seen_urls = set()
    items = []
    try:
        resp = requests.get(f"{PPA_URL}/news", timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article")
        for art in articles[:10]:
            title_el = art.select_one("h2 a, h3 a, .article-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            if link and not link.startswith("http"):
                link = f"{PPA_URL}{link}"
            if link in seen_urls:
                continue
            seen_urls.add(link)
            desc_el = art.select_one(".article-intro, .nspText, .itemText, .catItemIntroText")
            items.append({
                "title": title,
                "description": desc_el.get_text(strip=True) if desc_el else "",
                "deadline": "",
                "url": link,
                "procurement_category": "General",
                "source": "2merkato.com",
            })
    except Exception as e:
        print(f"[WARN] 2merkato news scrape failed: {e}")
    return _keyword_filter(items, keyword)


def _scrape_addisbiz_opportunities(keyword: Optional[str]) -> List[Dict[str, Any]]:
    import requests
    from bs4 import BeautifulSoup

    items = []
    try:
        resp = requests.get(f"{EGP_URL}/business-news", timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article")
        for art in articles[:10]:
            title_el = art.select_one(".entry-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            desc_el = art.select_one(".entry-content p, .post-content p")
            items.append({
                "title": title,
                "description": desc_el.get_text(strip=True) if desc_el else "",
                "deadline": "",
                "url": link,
                "procurement_category": "General",
                "source": "addisbiz.com",
            })
    except Exception as e:
        print(f"[WARN] AddisBiz scrape failed: {e}")
    return _keyword_filter(items, keyword)


def fetch_active_tenders(sector: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []
    results.extend(_scrape_2merkato_news(sector))
    results.extend(_scrape_addisbiz_opportunities(sector))
    return results
