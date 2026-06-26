import json
import time
from pathlib import Path

import pytest


def _wait_for_file(path: Path, timeout: float = 2.0) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists() and path.read_text(encoding="utf-8").strip():
            return path.read_text(encoding="utf-8")
        time.sleep(0.05)
    raise AssertionError(f"Timed out waiting for {path}")


class TestTrainingSink:
    def test_append_writes_jsonl(self, tmp_path, monkeypatch):
        import app.ml.training_sink as sink
        output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
        monkeypatch.setattr(sink, "RAW_INTERACTIONS_PATH", output_path)
        monkeypatch.setattr(sink, "MAX_RECORD_INPUT_SIZE", 1024 * 1024)
        monkeypatch.setattr(sink, "MAX_RECORD_OUTPUT_SIZE", 1024 * 1024)

        sink.append_to_training_dataset("session-1", "find inventory shortages", {"answer": "Check low-stock"})

        written = _wait_for_file(output_path)
        line = json.loads(written.strip().splitlines()[0])
        assert line["session_id"] == "session-1"
        assert line["query"] == "find inventory shortages"
        assert line["event_type"] == "interaction"

    def test_record_training_event_validates_schema(self, tmp_path, monkeypatch):
        import app.ml.training_sink as sink
        output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
        monkeypatch.setattr(sink, "RAW_INTERACTIONS_PATH", output_path)
        monkeypatch.setattr(sink, "MAX_RECORD_INPUT_SIZE", 1024 * 1024)
        monkeypatch.setattr(sink, "MAX_RECORD_OUTPUT_SIZE", 1024 * 1024)

        sink.record_training_event(
            "test.event",
            input={"message": "test query"},
            output={"response": "test response"},
            source="test",
        )

        written = _wait_for_file(output_path)
        line = json.loads(written.strip().splitlines()[0])
        assert line["event_type"] == "test.event"
        assert line["source"] == "test"

    def test_duplicate_detection_skips_identical(self, tmp_path, monkeypatch):
        import app.ml.training_sink as sink
        output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
        monkeypatch.setattr(sink, "RAW_INTERACTIONS_PATH", output_path)
        monkeypatch.setattr(sink, "MAX_RECORD_INPUT_SIZE", 1024 * 1024)
        monkeypatch.setattr(sink, "MAX_RECORD_OUTPUT_SIZE", 1024 * 1024)

        sink._rebuild_duplicate_set()
        sink.append_to_training_dataset("session-d", "duplicate query", {"answer": "dup"})
        time.sleep(0.2)
        sink.append_to_training_dataset("session-d", "duplicate query", {"answer": "dup"})
        time.sleep(0.2)

        lines = output_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

    def test_pii_redaction_phone(self, tmp_path, monkeypatch):
        import app.ml.training_sink as sink
        output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
        monkeypatch.setattr(sink, "RAW_INTERACTIONS_PATH", output_path)
        monkeypatch.setattr(sink, "MAX_RECORD_INPUT_SIZE", 1024 * 1024)
        monkeypatch.setattr(sink, "MAX_RECORD_OUTPUT_SIZE", 1024 * 1024)

        sink.record_training_event(
            "test.pii",
            input={"phone": "+251911234567"},
            output={"msg": "Call us"},
            source="test",
        )

        written = _wait_for_file(output_path)
        line = json.loads(written.strip().splitlines()[0])
        assert "[REDACTED-PHONE]" in json.dumps(line["input"])

    def test_pii_redaction_email(self, tmp_path, monkeypatch):
        import app.ml.training_sink as sink
        output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
        monkeypatch.setattr(sink, "RAW_INTERACTIONS_PATH", output_path)
        monkeypatch.setattr(sink, "MAX_RECORD_INPUT_SIZE", 1024 * 1024)
        monkeypatch.setattr(sink, "MAX_RECORD_OUTPUT_SIZE", 1024 * 1024)

        sink.record_training_event(
            "test.pii",
            input={"email": "user@example.com"},
            output={"msg": "sent"},
            source="test",
        )

        written = _wait_for_file(output_path)
        line = json.loads(written.strip().splitlines()[0])
        assert "[REDACTED-EMAIL]" in json.dumps(line["input"])

    def test_metrics_are_tracked(self, tmp_path, monkeypatch):
        import app.ml.training_sink as sink
        output_path = tmp_path / "ml" / "datasets" / "raw_interactions.jsonl"
        monkeypatch.setattr(sink, "RAW_INTERACTIONS_PATH", output_path)
        monkeypatch.setattr(sink, "MAX_RECORD_INPUT_SIZE", 1024 * 1024)
        monkeypatch.setattr(sink, "MAX_RECORD_OUTPUT_SIZE", 1024 * 1024)
        sink.reset_metrics()

        sink.append_to_training_dataset("session-m", "metric test", {"answer": "metrics"})
        time.sleep(0.3)

        metrics = sink.get_metrics()
        assert metrics["records_collected"] >= 1
        assert "queue_depth" in metrics
        assert "errors_by_type" in metrics

    def test_dataset_builder_quality_check(self, tmp_path):
        from app.ml.dataset_builder import DatasetBuilder

        raw_path = tmp_path / "raw.jsonl"
        processed_path = tmp_path / "processed.jsonl"
        raw_path.write_text(
            "\n".join([
                json.dumps({"session_id": "1", "query": "What stock is low?", "response": {"answer": "Review SKU A"}}),
                json.dumps({"session_id": "2", "query": "hi", "response": "ok"}),
                json.dumps({"session_id": "3", "query": "test", "response": "I cannot answer that question"}),
            ]),
            encoding="utf-8",
        )

        builder = DatasetBuilder(raw_path=raw_path, processed_path=processed_path, min_chars=4)
        kept = builder.build()

        assert kept >= 1  # at least the good one
        summary = DatasetBuilder.get_quality_summary()

        # the quality report should exist
        from app.ml.dataset_builder import QUALITY_REPORT_PATH
        assert QUALITY_REPORT_PATH.exists()
        assert summary["total"] > 0
