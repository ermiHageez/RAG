from src.agents.supervisor.supervisor import _parse_route


def test_parse_route_tender():
    result = _parse_route('tender procurement bid')
    assert "tender" in result


def test_parse_route_lead():
    result = _parse_route('find companies and businesses')
    assert "lead" in result


def test_parse_route_knowledge():
    result = _parse_route('what does eTech do')
    assert "knowledge" in result


def test_parse_route_json():
    result = _parse_route('{"route": ["lead", "knowledge"]}')
    assert "lead" in result
    assert "knowledge" in result
    assert "tender" not in result


def test_parse_route_empty():
    result = _parse_route('')
    assert isinstance(result, list)
    assert len(result) > 0


def test_supervisor_call(mock_ollama):
    from src.agents.supervisor import supervisor_agent
    result = supervisor_agent({"query": "find tenders for security systems"})
    assert "route" in result
    assert isinstance(result["route"], list)
