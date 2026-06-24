from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage


@pytest.fixture
def client():
    from src.api import app
    return TestClient(app)


class TestCallGroq:
    def test_sends_correct_payload(self):
        from src.agents.llm import _call_groq

        with patch("src.agents.llm.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "  Hello from Groq  "}}]
            }
            mock_post.return_value = mock_resp

            result = _call_groq("test prompt")

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["model"] == "llama-3.1-8b-instant"
        assert call_kwargs["json"]["messages"] == [
            {"role": "user", "content": "test prompt"}
        ]
        assert call_kwargs["headers"]["Authorization"].startswith("Bearer ")
        assert call_kwargs["timeout"] == 30
        assert result == "Hello from Groq"

    def test_propagates_http_error(self):
        from src.agents.llm import _call_groq

        with patch("src.agents.llm.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("401 Unauthorized")
            mock_post.return_value = mock_resp

            with pytest.raises(Exception, match="401"):
                _call_groq("test")


class TestFallbackLLM:
    def test_invoke_returns_aimessage_when_ollama_succeeds(self):
        from src.agents.llm import _FallbackLLM

        llm = _FallbackLLM(model="gemma2:2b", base_url="http://localhost:11434", temperature=0.3)

        with patch("src.agents.llm.ChatOllama") as mock_chat:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = AIMessage(content="Ollama response")
            mock_chat.return_value = mock_llm

            with patch("src.agents.llm.requests.post") as mock_groq:
                result = llm.invoke("hello")

        assert isinstance(result, AIMessage)
        assert result.content == "Ollama response"
        mock_groq.assert_not_called()

    def test_invoke_falls_back_to_groq_when_ollama_fails(self):
        from src.agents.llm import _FallbackLLM

        llm = _FallbackLLM(model="gemma2:2b", base_url="http://localhost:11434", temperature=0.3)

        with patch("src.agents.llm.ChatOllama") as mock_chat:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = TimeoutError("ollama timed out")
            mock_chat.return_value = mock_llm

            with patch("src.agents.llm.requests.post") as mock_groq:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {
                    "choices": [{"message": {"content": "Groq fallback"}}]
                }
                mock_groq.return_value = mock_resp

                result = llm.invoke("hello")

        assert isinstance(result, AIMessage)
        assert result.content == "Groq fallback"

    def test_invoke_raises_when_both_fail(self):
        from src.agents.llm import _FallbackLLM

        llm = _FallbackLLM(model="gemma2:2b", base_url="http://localhost:11434", temperature=0.3)

        with patch("src.agents.llm.ChatOllama") as mock_chat:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = RuntimeError("Ollama down")
            mock_chat.return_value = mock_llm

            with patch("src.agents.llm.requests.post") as mock_groq:
                mock_groq.side_effect = RuntimeError("Groq also down")

                with pytest.raises(RuntimeError):
                    llm.invoke("hello")

    def test_passes_temperature_to_groq(self):
        from src.agents.llm import _FallbackLLM

        llm = _FallbackLLM(model="gemma2:2b", base_url="http://localhost:11434", temperature=0.7)

        with patch("src.agents.llm.ChatOllama") as mock_chat:
            mock_chat.return_value.invoke.side_effect = TimeoutError()

            with patch("src.agents.llm.requests.post") as mock_groq:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {
                    "choices": [{"message": {"content": "warm"}}]
                }
                mock_groq.return_value = mock_resp

                llm.invoke("hello")

        assert mock_groq.call_args.kwargs["json"]["temperature"] == 0.7

    def test_factory_returns_fallbackllm_instance(self):
        from src.agents.llm import get_router_llm, get_reasoning_llm, get_content_llm, _FallbackLLM

        assert isinstance(get_router_llm(), _FallbackLLM)
        assert isinstance(get_reasoning_llm(), _FallbackLLM)
        assert isinstance(get_content_llm(), _FallbackLLM)

    def test_normalizes_list_content(self):
        from src.agents.llm import _FallbackLLM

        llm = _FallbackLLM(model="gemma2:2b", base_url="http://localhost:11434", temperature=0.3)

        with patch("src.agents.llm.ChatOllama") as mock_chat:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = AIMessage(content=["Hello", " ", "World"])
            mock_chat.return_value = mock_llm

            with patch("src.agents.llm.requests.post") as mock_groq:
                result = llm.invoke("hello")

        assert result.content == "Hello World"
        mock_groq.assert_not_called()


class TestFallbackOllamaSucceeds:
    def test_returns_ollama_response(self):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.return_value = AIMessage(
            content="  Local Ollama answer  "
        )

        from src.agents.llm import call_content_llm_with_fallback

        with patch("src.agents.llm.requests.post") as mock_groq:
            result = call_content_llm_with_fallback("hello")

        assert result == "Local Ollama answer"
        mock_groq.assert_not_called()

    def test_passes_custom_timeout(self):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.return_value = AIMessage(content="fast")

        from src.agents.llm import call_content_llm_with_fallback

        with patch("src.agents.llm.requests.post") as mock_groq:
            result = call_content_llm_with_fallback("hi", ollama_timeout=5)

        assert result == "fast"
        _, kwargs = ChatOllama.call_args
        assert kwargs["sync_client_kwargs"]["timeout"] == 5


class TestFallbackOllamaFails:
    def test_falls_back_to_groq_on_timeout(self):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.side_effect = TimeoutError("ollama timed out")

        from src.agents.llm import call_content_llm_with_fallback

        with patch("src.agents.llm.requests.post") as mock_groq:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Groq answer"}}]
            }
            mock_groq.return_value = mock_resp

            result = call_content_llm_with_fallback("hello")

        assert result == "Groq answer"
        mock_groq.assert_called_once()

    def test_falls_back_on_connection_error(self):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.side_effect = ConnectionError("refused")

        from src.agents.llm import call_content_llm_with_fallback

        with patch("src.agents.llm.requests.post") as mock_groq:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "fallback OK"}}]
            }
            mock_groq.return_value = mock_resp

            result = call_content_llm_with_fallback("hello")
        assert result == "fallback OK"

    def test_falls_back_on_generic_error(self):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.side_effect = RuntimeError("Ollama crashed")

        from src.agents.llm import call_content_llm_with_fallback

        with patch("src.agents.llm.requests.post") as mock_groq:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Groq rescue"}}]
            }
            mock_groq.return_value = mock_resp

            result = call_content_llm_with_fallback("hello")
        assert result == "Groq rescue"

    def test_raises_when_both_fail(self):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.side_effect = RuntimeError("Ollama down")

        from src.agents.llm import call_content_llm_with_fallback

        with patch("src.agents.llm.requests.post") as mock_groq:
            mock_groq.side_effect = RuntimeError("Groq also down")

            with pytest.raises(RuntimeError):
                call_content_llm_with_fallback("hello")


class TestRagChatEndpoint:
    ENDPOINT = "/rag/chat"
    PAYLOAD = {
        "session_id": "test-session",
        "message": "What does eTech do?",
        "history": [],
    }

    def test_returns_200_when_ollama_succeeds(self, client, mock_vectorstore):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.return_value = AIMessage(
            content="eTech provides ERP solutions."
        )

        resp = client.post(self.ENDPOINT, json=self.PAYLOAD)
        assert resp.status_code == 200
        body = resp.json()
        assert "eTech" in body["response"]
        assert len(body["sources"]) > 0
        assert body["session_id"] == "test-session"

    def test_returns_200_with_groq_when_ollama_times_out(
        self, client, mock_vectorstore
    ):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.side_effect = TimeoutError("timeout")

        with patch("src.agents.llm.requests.post") as mock_groq:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Groq fallback response"}}]
            }
            mock_groq.return_value = mock_resp

            resp = client.post(self.ENDPOINT, json=self.PAYLOAD)

        assert resp.status_code == 200
        assert resp.json()["response"] == "Groq fallback response"

    def test_returns_503_when_both_fail(self, client, mock_vectorstore):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.side_effect = RuntimeError("Ollama crashed")

        with patch("src.agents.llm.requests.post") as mock_groq:
            mock_groq.side_effect = RuntimeError("Groq API error")

            resp = client.post(self.ENDPOINT, json=self.PAYLOAD)

        assert resp.status_code == 503
        assert "LLM unavailable" in resp.json()["detail"]

    def test_propagates_rag_sources(self, client, mock_vectorstore):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.return_value = AIMessage(
            content="Answer with sources."
        )

        resp = client.post(self.ENDPOINT, json=self.PAYLOAD)
        assert resp.status_code == 200
        sources = resp.json()["sources"]
        assert len(sources) > 0
        for s in sources:
            assert "title" in s
            assert "snippet" in s
            assert "url" in s

    def test_works_with_history(self, client, mock_vectorstore):
        from src.agents.llm import ChatOllama
        ChatOllama.return_value.invoke.return_value = AIMessage(
            content="History-aware answer."
        )

        payload = {
            "session_id": "s1",
            "message": "Tell me more",
            "history": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello"},
            ],
        }
        resp = client.post(self.ENDPOINT, json=payload)
        assert resp.status_code == 200
        assert resp.json()["session_id"] == "s1"

    def test_rejects_missing_session_id(self, client):
        resp = client.post(self.ENDPOINT, json={"message": "hi"})
        assert resp.status_code == 422

    def test_rejects_missing_message(self, client):
        resp = client.post(self.ENDPOINT, json={"session_id": "s1"})
        assert resp.status_code == 422
