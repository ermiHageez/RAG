from src.agents.state import AgentState, _merge_lists, _override


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


def test_agent_state_defaults():
    state = AgentState(
        query="",
        route=[],
        qualified_leads=[],
        qualified_tenders=[],
        knowledge_context=[],
        sales_intelligence=None,
        draft_email=None,
        requires_human_approval=None,
        approval_reason=None,
        n8n_payload=None,
    )
    assert state["query"] == ""
    assert state["qualified_leads"] == []
    assert state["sales_intelligence"] is None


def test_agent_state_with_data():
    state = AgentState(
        query="find bank leads",
        route=["lead"],
        qualified_leads=[{"company_name": "Test"}],
        qualified_tenders=[],
        knowledge_context=[],
        sales_intelligence={"summary": "test"},
        draft_email=None,
        requires_human_approval=False,
        approval_reason="OK",
        n8n_payload={"batch": []},
    )
    assert state["query"] == "find bank leads"
    assert state["route"] == ["lead"]
    assert state["sales_intelligence"]["summary"] == "test"
    assert state["requires_human_approval"] is False


def test_merge_lists_reducer():
    state = AgentState(
        query="test",
        route=["lead"],
        qualified_leads=[{"a": 1}],
        qualified_tenders=[],
        knowledge_context=[],
        sales_intelligence=None,
        draft_email=None,
        requires_human_approval=None,
        approval_reason=None,
        n8n_payload=None,
    )
    merged = _merge_lists(state["qualified_leads"], [{"b": 2}])
    assert len(merged) == 2
    assert merged[0] == {"a": 1}
    assert merged[1] == {"b": 2}
