import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

PPA_URL = os.getenv("PPA_URL", "https://www.ppa.gov.et")
EGP_URL = os.getenv("EGP_URL", "https://www.egp.gov.et")

KEYWORDS = [
    "ጨረታ", "tender", "ERP", "ERP Implementation",
    "System Modernization", "Database Management",
    "Security System", "ICT", "Network Infrastructure",
]

MOCK_TENDERS: List[Dict[str, Any]] = [
    {
        "title": "Supply and Installation of Security Surveillance System",
        "description": "Tender for security cameras and access control for government building",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "url": f"{PPA_URL}/tenders/001",
        "procurement_category": "Security Systems",
        "source": "mock",
    },
    {
        "title": "ERP System Implementation for Public Enterprise",
        "description": "End-to-end ERP solution including finance, HR, and procurement modules",
        "deadline": (datetime.now() + timedelta(days=45)).isoformat(),
        "url": f"{PPA_URL}/tenders/002",
        "procurement_category": "ERP Implementation",
        "source": "mock",
    },
    {
        "title": "Network Infrastructure Upgrade for Ministry Building",
        "description": "Upgrade of existing network infrastructure including switches, routers, and fiber",
        "deadline": (datetime.now() + timedelta(days=21)).isoformat(),
        "url": f"{EGP_URL}/tenders/101",
        "procurement_category": "ICT Infrastructure",
        "source": "mock",
    },
    {
        "title": "Database Management System Maintenance",
        "description": "Annual maintenance contract for enterprise database systems",
        "deadline": (datetime.now() + timedelta(days=60)).isoformat(),
        "url": f"{EGP_URL}/tenders/102",
        "procurement_category": "Database Management",
        "source": "mock",
    },
    {
        "title": "የኮምፒውተር እና የኔትወርክ መሳሪያዎች ግዢ (Computer and Network Equipment Purchase)",
        "description": "Tender for procurement of computers, servers, and networking equipment",
        "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
        "url": f"{PPA_URL}/tenders/003",
        "procurement_category": "ICT Equipment",
        "source": "mock",
    },
]


def _match_keywords(text: str) -> bool:
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def _scrape_ppa(sector: Optional[str]) -> List[Dict[str, Any]]:
    import httpx
    from bs4 import BeautifulSoup

    tenders = []
    try:
        resp = httpx.get(f"{PPA_URL}/tenders", timeout=15.0)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for item in soup.select(".tender-item, .procurement-item, tr"):
            title_el = item.select_one(".tender-title, h3, a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if sector and sector.lower() not in title.lower():
                if not _match_keywords(title):
                    continue
            desc_el = item.select_one(".tender-description, p")
            deadline_el = item.select_one(".tender-deadline, .deadline")
            link_el = item.select_one("a[href]")
            tenders.append({
                "title": title,
                "description": desc_el.get_text(strip=True) if desc_el else "",
                "deadline": deadline_el.get_text(strip=True) if deadline_el else "",
                "url": f"{PPA_URL}{link_el['href']}" if link_el and link_el.get("href") else PPA_URL,
                "procurement_category": "General",
                "source": "ppa.gov.et",
            })
    except Exception as e:
        print(f"[WARN] PPA scrape failed: {e}")
    return tenders


def fetch_active_tenders(sector: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []

    live_results = _scrape_ppa(sector)
    results.extend(live_results)

    if not results:
        print("[INFO] No live tenders fetched, using mock data")
        for tender in MOCK_TENDERS:
            if sector:
                combined = f"{tender['title']} {tender['description']} {tender['procurement_category']}"
                if sector.lower() in combined.lower():
                    results.append(tender)
            else:
                results.append(tender)

    return results
