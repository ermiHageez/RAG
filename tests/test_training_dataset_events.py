import json
import time
from pathlib import Path


def _wait_for_file(path: Path, timeout: float = 2.0) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists() and path.read_text(encoding="utf-8").strip():
            return path.read_text(encoding="utf-8")
        time.sleep(0.05)
    raise AssertionError(f"Timed out waiting for {path}")


def test_record_training_event_writes_schema(tmp_path, monkeypatch):
    import app.ml.training_sink as training_sink

    output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
    monkeypatch.setattr(training_sink, "RAW_INTERACTIONS_PATH", output_path)

    training_sink.record_training_event(
        "mcp.search",
        session_id="session-1",
        input={"query": "bank"},
        output=[{"title": "Example Bank"}],
        source="mcp",
        metadata={"tool": "discover_ethiopian_enterprises"},
    )

    written = _wait_for_file(output_path)
    record = json.loads(written.strip().splitlines()[0])

    assert record["event_type"] == "mcp.search"
    assert record["source"] == "mcp"
    assert record["origin"] == "discover_ethiopian_enterprises"
    assert record["session_id"] == "session-1"
    assert record["query"] == "bank"
    assert record["input"] == {"query": "bank"}
    assert record["output"] == [{"title": "Example Bank"}]
    assert record["metadata"] == {"tool": "discover_ethiopian_enterprises"}
    assert "timestamp" in record


def test_mcp_search_tool_logs_event(monkeypatch):
    import mcp_server.tools.search as search_mod

    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(search_mod, "resilient_web_search", lambda query, max_results=5: [
        {"title": "Alpha Bank", "url": "https://example.com", "snippet": "Bank in Ethiopia"}
    ])
    monkeypatch.setattr(
        search_mod,
        "record_training_event",
        lambda *args, **kwargs: calls.append((args[0], kwargs)),
    )

    results = search_mod.discover_ethiopian_enterprises("bank")

    assert results[0]["name"] == "Alpha Bank"
    assert calls and calls[0][0] == "mcp.search"
    assert calls[0][1]["source"] == "mcp"


def test_mcp_tenders_tool_logs_event(monkeypatch):
    import mcp_server.tools.tenders as tenders_mod

    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(tenders_mod, "_scrape_2merkato_news", lambda keyword: [{"title": "Tender A", "description": "Security"}])
    monkeypatch.setattr(tenders_mod, "_scrape_addisbiz_opportunities", lambda keyword: [])
    monkeypatch.setattr(
        tenders_mod,
        "record_training_event",
        lambda *args, **kwargs: calls.append((args[0], kwargs)),
    )

    results = tenders_mod.fetch_active_tenders("security")

    assert results[0]["title"] == "Tender A"
    assert calls and calls[0][0] == "mcp.tenders"


def test_mcp_directory_tool_logs_event(monkeypatch):
    import mcp_server.tools.directory as directory_mod

    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(directory_mod, "scrape_2merkato_directory", lambda sector, max_pages=2: [{"name": "Alpha Tech", "sector": "Technology", "description": "ICT company"}])
    monkeypatch.setattr(directory_mod, "scrape_addisbiz_directory", lambda sector, max_pages=2: [])
    monkeypatch.setattr(directory_mod, "scrape_ethyp_directory", lambda sector, max_pages=2: [])
    monkeypatch.setattr(
        directory_mod,
        "record_training_event",
        lambda *args, **kwargs: calls.append((args[0], kwargs)),
    )

    results = directory_mod.discover_companies("technology", max_per_source=5)

    assert results[0]["name"] == "Alpha Tech"
    assert calls and calls[0][0] == "mcp.directory"


def test_rag_chat_logs_event(monkeypatch):
    import src.api as api

    class Store:
        def query(self, query, top_k=10):
            return [{
                "metadata": {
                    "text": "eTech provides ERP solutions.",
                    "source": {"title": "Doc", "url": "https://example.com"},
                },
                "distance": 0.1,
            }]

    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr("src.rag.vectorstore.get_vectorstore", lambda: Store())
    monkeypatch.setattr(api, "call_content_llm_with_fallback", lambda prompt, ollama_timeout=15: "answer")
    monkeypatch.setattr(
        api,
        "record_training_event",
        lambda *args, **kwargs: calls.append((args[0], kwargs)),
    )

    result = api.rag_chat(api.RagChatRequest(session_id="s1", message="What does eTech do?", history=[]))

    assert result.response == "answer"
    assert calls and calls[0][0] == "rag.chat"
    assert calls[0][1]["session_id"] == "s1"
