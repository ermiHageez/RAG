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


def test_append_to_training_dataset_writes_jsonl(tmp_path, monkeypatch):
    import app.ml.training_sink as training_sink

    output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
    monkeypatch.setattr(training_sink, "RAW_INTERACTIONS_PATH", output_path)

    training_sink.append_to_training_dataset(
        "session-1",
        "find inventory shortages",
        {"answer": "Check low-stock items first"},
    )

    written = _wait_for_file(output_path)
    line = written.strip().splitlines()[0]
    record = json.loads(line)

    assert record["session_id"] == "session-1"
    assert record["query"] == "find inventory shortages"
    assert record["response"] == {"answer": "Check low-stock items first"}
    assert record["event_type"] == "interaction"
    assert record["source"] == "memory"
    assert record["input"] == "find inventory shortages"
    assert record["output"] == {"answer": "Check low-stock items first"}
    assert "timestamp" in record
    assert "\n" not in line


def test_dataset_builder_filters_and_formats_records(tmp_path):
    from app.ml.dataset_builder import DatasetBuilder

    raw_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
    processed_path = tmp_path / "ml" / "datasets" / "processed_training.jsonl"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        "\n".join(
            [
                json.dumps({"session_id": "1", "query": "hi", "response": "ok"}),
                json.dumps({"session_id": "2", "query": "What stock is low?", "response": {"answer": "Review SKU A and SKU B"}}),
                json.dumps({"session_id": "3", "query": "plan", "response": "yes"}),
            ]
        ),
        encoding="utf-8",
    )

    builder = DatasetBuilder(raw_path=raw_path, processed_path=processed_path)
    kept = builder.build()

    assert kept == 1
    lines = processed_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    processed = json.loads(lines[0])
    assert processed == {
        "messages": [
            {"role": "user", "content": "What stock is low?"},
            {"role": "assistant", "content": "Review SKU A and SKU B"},
        ]
    }


def test_dataset_builder_supports_input_output_schema(tmp_path):
    from app.ml.dataset_builder import DatasetBuilder

    raw_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
    processed_path = tmp_path / "ml" / "datasets" / "processed_training.jsonl"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        json.dumps(
            {
                "event_type": "rag.chat",
                "session_id": "s-1",
                "input": {"message": "What does eTech do?"},
                "output": {"response": "eTech provides ERP solutions."},
            }
        ),
        encoding="utf-8",
    )

    builder = DatasetBuilder(raw_path=raw_path, processed_path=processed_path)
    kept = builder.build()

    assert kept == 1
    processed = json.loads(processed_path.read_text(encoding="utf-8").strip())
    assert processed["messages"][0]["content"] == "What does eTech do?"
    assert processed["messages"][1]["content"] == "eTech provides ERP solutions."


def test_memory_route_writes_training_sink_for_custom_memory(monkeypatch):
    import src.api as api_module

    class FakeStore:
        def __init__(self, path: str = "memory_store"):
            self.path = Path(path)
            self.path.mkdir(parents=True, exist_ok=True)
            self._data = {}

        def save(self, key, value):
            self._data[key] = value

        def load(self, key):
            return self._data.get(key)

    calls: list[tuple[str, str, dict]] = []

    monkeypatch.setattr("src.memory.base.JSONMemoryStore", FakeStore)
    monkeypatch.setattr(api_module, "append_to_training_dataset", lambda session_id, query, response: calls.append((session_id, query, response)))

    req = api_module.MemoryRequest(session_id="session-x", query="find stock", response={"answer": "low stock"})
    resp = api_module.save_memory("custom", req)

    assert resp.count == 1
    assert calls == [("session-x", "find stock", {"answer": "low stock"})]


def test_conversation_memory_writes_training_sink(monkeypatch, tmp_path):
    import src.memory.conversation_memory as conversation_memory
    from src.memory.base import JSONMemoryStore
    from src.memory.conversation_memory import ConversationMemory

    calls: list[tuple[str, str, dict]] = []
    monkeypatch.setattr(conversation_memory, "append_to_training_dataset", lambda session_id, query, response: calls.append((session_id, query, response)))

    store = JSONMemoryStore(str(tmp_path / "memory_store"))
    memory = ConversationMemory(store)
    memory.add_interaction("session-y", "reorder items", {"answer": "ordered"})

    assert calls == [("session-y", "reorder items", {"answer": "ordered"})]
