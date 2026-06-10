import os
import json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

MOCK_RESPONSES: Dict[str, List[Dict[str, str]]] = {
    "bank": [
        {"name": "Mock Bank of Ethiopia", "sector": "Finance", "location": "Addis Ababa", "description": "Leading commercial bank", "contact": "info@mockbank.et"},
        {"name": "Mock Credit & Savings", "sector": "Finance", "location": "Addis Ababa", "description": "Microfinance institution", "contact": "contact@mocksavings.et"},
    ],
    "insurance": [
        {"name": "Mock Insurance SC", "sector": "Insurance", "location": "Addis Ababa", "description": "Full-service insurance provider", "contact": "info@mockinsurance.et"},
    ],
    "logistics": [
        {"name": "Mock Logistics PLC", "sector": "Logistics", "location": "Addis Ababa", "description": "Freight and supply chain management", "contact": "ops@mocklogistics.et"},
    ],
    "manufacturing": [
        {"name": "Mock Manufacturing PLC", "sector": "Manufacturing", "location": "Addis Ababa", "description": "Industrial goods manufacturer", "contact": "sales@mockmfg.et"},
    ],
    "government": [
        {"name": "Mock Ministry of Tech", "sector": "Government", "location": "Addis Ababa", "description": "Government technology authority", "contact": "info@mockministry.gov.et"},
    ],
    "default": [
        {"name": "Mock Enterprise 1", "sector": "General", "location": "Addis Ababa", "description": "Ethiopian enterprise", "contact": "info@mock1.et"},
        {"name": "Mock Enterprise 2", "sector": "General", "location": "Addis Ababa", "description": "Ethiopian enterprise", "contact": "info@mock2.et"},
    ],
}


def _mock_search(query: str) -> List[Dict[str, str]]:
    query_lower = query.lower()
    for sector_key, results in MOCK_RESPONSES.items():
        if sector_key in query_lower:
            return results
    return MOCK_RESPONSES["default"]


def _google_search(query: str) -> List[Dict[str, str]]:
    import httpx

    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        print("[WARN] GOOGLE_API_KEY or GOOGLE_CSE_ID not set, falling back to mock")
        return _mock_search(query)

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cse_id, "q": query, "num": 5}
    try:
        resp = httpx.get(url, params=params, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "name": item.get("title", ""),
                "sector": _guess_sector(item.get("title", ""), item.get("snippet", "")),
                "location": "Addis Ababa",
                "description": item.get("snippet", ""),
                "contact": "",
            })
        return results
    except Exception as e:
        print(f"[WARN] Google search failed ({e}), falling back to mock")
        return _mock_search(query)


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
    return "General"


def discover_ethiopian_enterprises(query: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("GOOGLE_API_KEY")
    api_key_set = bool(api_key and os.getenv("GOOGLE_CSE_ID"))

    if api_key_set:
        return _google_search(query)
    return _mock_search(query)
