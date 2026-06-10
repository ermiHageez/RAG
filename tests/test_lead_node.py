from src.agent.nodes.lead_discovery import _deduplicate


def test_deduplicate_removes_duplicates():
    leads = [
        {"name": "Bank A", "sector": "Finance"},
        {"name": "Bank B", "sector": "Insurance"},
        {"name": "Bank A", "sector": "Finance"},
    ]
    result = _deduplicate(leads)
    assert len(result) == 2


def test_deduplicate_empty():
    assert _deduplicate([]) == []


def test_deduplicate_case_insensitive():
    leads = [
        {"name": "Bank A"},
        {"name": "bank a"},
    ]
    result = _deduplicate(leads)
    assert len(result) == 1


def test_deduplicate_no_duplicates():
    leads = [
        {"name": "Bank A"},
        {"name": "Bank B"},
        {"name": "Bank C"},
    ]
    result = _deduplicate(leads)
    assert len(result) == 3
