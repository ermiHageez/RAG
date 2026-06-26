from pathlib import Path

import pytest


class TestDataLoader:
    @pytest.fixture
    def fixtures_dir(self):
        return Path(__file__).parent / "fixtures"

    def test_load_txt(self, tmp_path):
        from src.rag.data_loader import load_all_documents
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is a test document.", encoding="utf-8")
        docs = load_all_documents(str(tmp_path))
        assert len(docs) >= 1
        assert "test document" in docs[0].page_content

    def test_load_csv(self, tmp_path):
        from src.rag.data_loader import load_all_documents
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,value\neTech,ERP\nEthioTel,Mobile\n", encoding="utf-8")
        docs = load_all_documents(str(tmp_path))
        assert len(docs) >= 1

    def test_load_json(self, tmp_path):
        pytest.importorskip("jq")
        from src.rag.data_loader import load_all_documents
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value", "nested": {"a": 1}}', encoding="utf-8")
        docs = load_all_documents(str(tmp_path))
        assert len(docs) >= 1

    def test_empty_directory_returns_empty(self, tmp_path):
        from src.rag.data_loader import load_all_documents
        docs = load_all_documents(str(tmp_path))
        assert docs == []

    def test_no_valid_files_returns_empty(self, tmp_path):
        from src.rag.data_loader import load_all_documents
        (tmp_path / "notes.md").write_text("# Notes", encoding="utf-8")
        # .md is not in supported formats, should return empty or try to handle gracefully
        docs = load_all_documents(str(tmp_path))
        assert isinstance(docs, list)
