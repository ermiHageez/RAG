from src.agent.state import AgentState, _merge_lists, _override


def test_merge_lists_both_empty():
    assert _merge_lists(None, None) == []


def test_merge_lists_left_empty():
    assert _merge_lists(None, [1, 2]) == [1, 2]


def test_merge_lists_right_empty():
    assert _merge_lists([1, 2], None) == [1, 2]


def test_merge_lists_both_populated():
    assert _merge_lists([1], [2, 3]) == [1, 2, 3]


def test_override_new_value():
    assert _override("old", "new") == "new"


def test_override_none_new():
    assert _override("old", None) == "old"


def test_override_none_both():
    assert _override(None, None) is None


def test_agent_state_defaults(empty_state):
    assert empty_state["query"] == ""
    assert empty_state["found_leads"] == []
    assert empty_state["sales_report"] is None


def test_agent_state_with_data():
    state = AgentState(
        query="find bank leads",
        rag_context=["context1"],
        found_leads=[{"name": "Test"}],
        active_tender_listings=[],
        sales_intel=[],
        sales_report="report",
        email_drafts=[],
        n8n_payload={"batch": []},
    )
    assert state["query"] == "find bank leads"
    assert state["sales_report"] == "report"
