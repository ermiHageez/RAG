import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

MERKATO_URL = os.getenv("MERKATO_URL", "https://www.2merkato.com")
ADDISBIZ_URL = os.getenv("ADDISBIZ_URL", "https://addisbiz.com")
ETHYP_URL = os.getenv("ETHYP_URL", "https://www.ethyp.com")

SECTOR_CATEGORY_MAP: Dict[str, List[str]] = {
    "bank": ["Bank and Insurance", "Banking", "Finance"],
    "insurance": ["Bank and Insurance", "Insurance", "Insurance Brokerage"],
    "finance": ["Bank and Insurance", "Banking", "Finance"],
    "logistics": ["Transport, Storage and Communication", "Transport", "Logistics"],
    "transport": ["Transport, Storage and Communication", "Transport"],
    "manufacturing": ["Manufacturing", "Ethiopian Manufacturers"],
    "tech": ["ICT", "Technology", "Information Technology"],
    "technology": ["ICT", "Technology", "Information Technology"],
    "ict": ["ICT", "Technology", "Information Technology"],
    "it": ["ICT", "Technology", "Information Technology"],
    "software": ["ICT", "Technology", "Information Technology"],
    "agriculture": ["Agriculture", "Agriculture"],
    "farm": ["Agriculture"],
    "construction": ["Construction and Engineering", "Construction"],
    "engineering": ["Construction and Engineering"],
    "hotel": ["Hotels and Restaurants, Tour and Travel", "Hospitality"],
    "hospitality": ["Hotels and Restaurants, Tour and Travel", "Hospitality"],
    "tourism": ["Hotels and Restaurants, Tour and Travel", "Tour / Travel / Car Rental"],
    "government": ["Government and Other Organizations", "Government"],
    "import": ["Ethiopian Importers", "Importers"],
    "export": ["Ethiopian Exporters", "Exporters"],
    "health": ["Health"],
    "education": ["Education / University, School & Training", "Education"],
    "shopping": ["Shopping"],
    "automotive": ["Automotive"],
}


def _guess_sector_from_name(name: str, description: str) -> str:
    text = (name + " " + description).lower()
    if any(w in text for w in ["bank", "finance", "insurance", "microfinance"]):
        return "Finance"
    if any(w in text for w in ["logistics", "transport", "shipping", "freight"]):
        return "Logistics"
    if any(w in text for w in ["manufacturing", "factory", "industrial", "production"]):
        return "Manufacturing"
    if any(w in text for w in ["government", "ministry", "authority", "public"]):
        return "Government"
    if any(w in text for w in ["tech", "software", "it ", "digital", "computer", "ict"]):
        return "Technology"
    if any(w in text for w in ["agriculture", "farm", "agro", "farming"]):
        return "Agriculture"
    if any(w in text for w in ["hotel", "tourism", "hospitality", "lodge", "resort"]):
        return "Hospitality"
    if any(w in text for w in ["construction", "engineering", "building", "contractor"]):
        return "Construction"
    if any(w in text for w in ["import", "export", "trading", "trade", "distributor"]):
        return "Import/Export"
    if any(w in text for w in ["education", "school", "college", "university", "training"]):
        return "Education"
    if any(w in text for w in ["health", "medical", "hospital", "clinic", "pharma"]):
        return "Health"
    if any(w in text for w in ["hotel", "tourism", "travel", "tour", "car rental"]):
        return "Hospitality"
    if any(w in text for w in ["communication", "telecom", "media", "advertising"]):
        return "Media & Telecom"
    return "General"


def _guess_sector_from_name_only(name: str) -> str:
    return _guess_sector_from_name(name, "")


def _sector_to_merkato_keywords(sector: Optional[str]) -> List[str]:
    if not sector:
        return []
    key = sector.lower().strip()
    for kw, cats in SECTOR_CATEGORY_MAP.items():
        if kw in key or key in kw:
            return cats
    return [sector]


def _sector_to_addisbiz_keywords(sector: Optional[str]) -> List[str]:
    if not sector:
        return []
    key = sector.lower().strip()
    for kw, cats in SECTOR_CATEGORY_MAP.items():
        if kw in key or key in kw:
            return cats
    return [sector]


# ── 2merkato.com directory scraper ──────────────────────────────────

def _get_merkato_category_ids(sector_hint: Optional[str] = None) -> List[tuple]:
    import requests
    from bs4 import BeautifulSoup

    cat_keywords = _sector_to_merkato_keywords(sector_hint)
    matches = []
    try:
        resp = requests.get(f"{MERKATO_URL}/directory/", timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for cat_div in soup.select(".mtree_category"):
            link = cat_div.select_one("h4 a")
            if not link:
                continue
            name = link.get_text(strip=True)
            href = link.get("href", "")
            cat_id = href.strip("/").split("/")[-1] if "/" in href else ""
            if not sector_hint:
                matches.append((name, cat_id, href))
            else:
                for kw in cat_keywords:
                    if kw.lower() in name.lower():
                        matches.append((name, cat_id, href))
                        break
    except Exception as e:
        print(f"[WARN] Failed to get 2merkato categories: {e}")
    return matches


def scrape_2merkato_directory(sector: Optional[str] = None, max_pages: int = 2) -> List[Dict[str, Any]]:
    import requests
    from bs4 import BeautifulSoup

    companies = []
    cat_matches = _get_merkato_category_ids(sector)
    for cat_name, cat_id, cat_path in cat_matches:
        for page in range(1, max_pages + 1):
            page_url = f"{MERKATO_URL}{cat_path}"
            if page > 1:
                page_url = f"{MERKATO_URL}/directory/{cat_id}/page:{page}"
            try:
                resp = requests.get(page_url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for listing in soup.select(".listing-summary-featured"):
                    title_el = listing.select_one(".heading h4 a")
                    if not title_el:
                        continue
                    name = title_el.get_text(strip=True)
                    link = title_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = f"{MERKATO_URL}{link}"

                    desc_el = listing.select_one(".body .span9")
                    description = desc_el.get_text(" ", strip=True) if desc_el else ""
                    cleaned_desc = " ".join(description.split()[:50])

                    phone_el = listing.select_one(".body h5.pull-right")
                    phone = phone_el.get_text(" ", strip=True) if phone_el else ""
                    phone = phone.replace("show all digits", "").replace("Popular", "").strip()

                    loc_el = listing.select_one(".footer small")
                    location = loc_el.get_text(" ", strip=True) if loc_el else ""
                    location = location.replace("Ethiopia", "").strip() or "Ethiopia"

                    companies.append({
                        "name": name,
                        "sector": cat_name if sector else _guess_sector_from_name(name, cleaned_desc),
                        "location": location,
                        "description": cleaned_desc,
                        "phone": phone,
                        "link": link,
                        "source": "2merkato.com",
                    })
            except Exception as e:
                print(f"[WARN] 2merkato page {page_url} failed: {e}")
                continue
    return companies


# ── addisbiz.com directory scraper ──────────────────────────────────

def _get_addisbiz_categories(sector_hint: Optional[str] = None) -> List[str]:
    import requests
    from bs4 import BeautifulSoup

    cat_keywords = _sector_to_addisbiz_keywords(sector_hint)
    matches = []
    try:
        resp = requests.get(f"{ADDISBIZ_URL}/business-directory/", timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for link in soup.select("ul li a[href*='category=']"):
            name = link.get_text(strip=True).split("(")[0].strip()
            cat_slug = link.get("href", "").split("=")[-1] if "=" in link.get("href", "") else ""
            if not name or not cat_slug:
                continue
            if not sector_hint:
                matches.append(cat_slug)
            else:
                for kw in cat_keywords:
                    if kw.lower() in name.lower():
                        matches.append(cat_slug)
                        break
    except Exception as e:
        print(f"[WARN] Failed to get addisbiz categories: {e}")
    return matches if matches else ["information-technology"]


def scrape_addisbiz_directory(sector: Optional[str] = None, max_pages: int = 2) -> List[Dict[str, Any]]:
    import requests
    from bs4 import BeautifulSoup

    companies = []
    cat_slugs = _get_addisbiz_categories(sector)
    for cat_slug in cat_slugs:
        for page in range(1, max_pages + 1):
            page_url = f"{ADDISBIZ_URL}/business-directory/?category={cat_slug}"
            if page > 1:
                page_url = f"{ADDISBIZ_URL}/page/{page}/?category={cat_slug}"
            try:
                resp = requests.get(page_url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for item in soup.select("article"):
                    title_el = item.select_one(".entry-title a")
                    if not title_el:
                        continue
                    name = title_el.get_text(strip=True)
                    link = title_el.get("href", "")
                    desc_el = item.select_one(".entry-content p, .post-content p")
                    description = desc_el.get_text(strip=True) if desc_el else ""
                    companies.append({
                        "name": name,
                        "sector": _guess_sector_from_name(name, description),
                        "location": "Ethiopia",
                        "description": description,
                        "phone": "",
                        "link": link,
                        "source": "addisbiz.com",
                    })
            except Exception as e:
                print(f"[WARN] addisbiz page {page_url} failed: {e}")
                continue
    return companies


# ── ethyp.com directory scraper ─────────────────────────────────────

ETHYP_CATEGORIES = [
    "Restaurants", "Vehicle_services", "Doctors_and_Clinics", "Shopping_centres",
    "Lawyers", "Real_estate_agents", "Contractors", "Employment_Agencies",
    "Banks", "Insurance_Brokers", "Hotels", "Schools",
    "Information_Technology", "Transport", "Agriculture",
    "Manufacturing", "Construction", "Health_and_Medical",
    "Tour_Operators", "Accountants",
]

ETHYP_SECTOR_MAP = {
    "Banks": "Finance", "Insurance_Brokers": "Insurance",
    "Information_Technology": "Technology", "Transport": "Logistics",
    "Manufacturing": "Manufacturing", "Construction": "Construction",
    "Agriculture": "Agriculture", "Hotels": "Hospitality",
    "Tour_Operators": "Hospitality", "Restaurants": "Hospitality",
    "Health_and_Medical": "Health", "Schools": "Education",
    "Lawyers": "Legal", "Accountants": "Finance",
    "Shopping_centres": "Retail", "Real_estate_agents": "Real Estate",
    "Contractors": "Construction", "Employment_Agencies": "HR",
    "Vehicle_services": "Automotive", "Doctors_and_Clinics": "Health",
}


def _get_ethyp_target_categories(sector_hint: Optional[str] = None) -> List[str]:
    if not sector_hint:
        return ETHYP_CATEGORIES[:5]
    key = sector_hint.lower()
    matches = []
    for cat, sector_name in ETHYP_SECTOR_MAP.items():
        if key in cat.lower() or key in sector_name.lower():
            matches.append(cat)
    for cat in ETHYP_CATEGORIES:
        if key in cat.lower():
            if cat not in matches:
                matches.append(cat)
    return matches[:5] if matches else ["Information_Technology"]


def scrape_ethyp_directory(sector: Optional[str] = None, max_pages: int = 2) -> List[Dict[str, Any]]:
    import requests
    from bs4 import BeautifulSoup

    companies = []
    cats = _get_ethyp_target_categories(sector)
    for cat in cats:
        for page in range(1, max_pages + 1):
            page_url = f"{ETHYP_URL}/category/{cat}"
            if page > 1:
                page_url = f"{ETHYP_URL}/category/{cat}/{page}"
            try:
                resp = requests.get(page_url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for item in soup.select("div.company.g_0, div.company.with_img"):
                    if "company_ad" in item.get("class", []):
                        continue
                    title_el = item.select_one(".company_header h3 a")
                    if not title_el:
                        continue
                    name = title_el.get_text(strip=True)
                    link = title_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = f"{ETHYP_URL}{link}"

                    addr_el = item.select_one(".company_header .address")
                    location = addr_el.get_text(" ", strip=True) if addr_el else "Ethiopia"

                    tagline_el = item.select_one(".tagline")
                    description = tagline_el.get_text(strip=True) if tagline_el else ""

                    phone_el = item.select_one(".cont div.s span")
                    phone = phone_el.get_text(strip=True) if phone_el else ""

                    companies.append({
                        "name": name,
                        "sector": ETHYP_SECTOR_MAP.get(cat, "General"),
                        "location": location if "Ethiopia" in location else f"{location}, Ethiopia",
                        "description": description,
                        "phone": phone,
                        "link": link,
                        "source": "ethyp.com",
                    })
            except Exception as e:
                print(f"[WARN] ethyp page {page_url} failed: {e}")
                continue
    return companies


# ── Unified Aggregator ──────────────────────────────────────────────

def discover_companies(sector: Optional[str] = None, max_per_source: int = 20) -> List[Dict[str, Any]]:
    from mcp_server.tools.search import _guess_sector
    all_companies = []
    all_companies.extend(scrape_2merkato_directory(sector, max_pages=2))
    all_companies.extend(scrape_addisbiz_directory(sector, max_pages=2))
    all_companies.extend(scrape_ethyp_directory(sector, max_pages=2))

    seen = set()
    unique = []
    for c in all_companies:
        key = c["name"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            if c["sector"] == "General":
                c["sector"] = _guess_sector(c["name"], c["description"])
            unique.append(c)
    return unique[:max_per_source]
