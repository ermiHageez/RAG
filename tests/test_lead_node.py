from src.agents.lead.lead_agent import _deduplicate


def test_deduplicate_removes_duplicates():
    leads = [
        {"name": "Test Corp", "sector": "Finance"},
        {"name": "Test Corp", "sector": "Finance"},
        {"name": "Other Corp", "sector": "Tech"},
    ]
    result = _deduplicate(leads)
    assert len(result) == 2


def test_deduplicate_empty():
    assert _deduplicate([]) == []


def test_deduplicate_case_insensitive():
    leads = [
        {"name": "Test Corp", "sector": "Finance"},
        {"name": "test corp", "sector": "Finance"},
    ]
    result = _deduplicate(leads)
    assert len(result) == 1


def test_deduplicate_no_duplicates():
    leads = [
        {"name": "Corp A", "sector": "Finance"},
        {"name": "Corp B", "sector": "Tech"},
    ]
    result = _deduplicate(leads)
    assert len(result) == 2
