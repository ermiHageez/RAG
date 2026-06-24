import logging
import multiprocessing
import os
from dotenv import load_dotenv

import requests

load_dotenv()
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))

OLLAMA_NUM_THREADS = int(
    os.getenv("OLLAMA_NUM_THREADS", str(max(1, multiprocessing.cpu_count() - 1)))
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    "",
)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

_OLLAMA_TIMEOUT = 45
_EMBEDDING_TIMEOUT = 60


def _llm_kwargs() -> dict:
    return {
        "num_ctx": OLLAMA_NUM_CTX,
        "num_thread": OLLAMA_NUM_THREADS,
        "sync_client_kwargs": {"timeout": _OLLAMA_TIMEOUT},
    }


def _embedding_kwargs() -> dict:
    return {
        "num_ctx": OLLAMA_NUM_CTX,
        "sync_client_kwargs": {"timeout": _EMBEDDING_TIMEOUT},
    }


def _normalize_content(content) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "content" in item:
                parts.append(str(item["content"]))
            else:
                parts.append(str(item))
        return "".join(parts).strip()
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


class _FallbackLLM:
    def __init__(self, model: str, base_url: str, temperature: float, **kwargs):
        self._model = model
        self._base_url = base_url
        self._temperature = temperature
        self._ollama_kwargs = kwargs

    def invoke(self, prompt: str) -> AIMessage:
        try:
            llm = ChatOllama(
                model=self._model,
                base_url=self._base_url,
                temperature=self._temperature,
                **self._ollama_kwargs,
            )
            response = llm.invoke(prompt)
            return AIMessage(content=_normalize_content(response.content))
        except Exception:
            logger.warning("Ollama failed, falling back to Groq...")
            text = _call_groq(prompt, temperature=self._temperature)
            return AIMessage(content=text)


EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")


def get_embedding_model():
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
        **_embedding_kwargs(),
    )


def get_router_llm():
    return _FallbackLLM(
        model="gemma2:2b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
        **_llm_kwargs(),
    )


def get_reasoning_llm():
    return _FallbackLLM(
        model="gemma2:2b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
        **_llm_kwargs(),
    )


def get_content_llm():
    return _FallbackLLM(
        model="gemma2:2b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
        **_llm_kwargs(),
    )


def _call_groq(prompt: str, temperature: float = 0.3) -> str:
    if not GROQ_API_KEY.strip():
        raise RuntimeError("GROQ_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=30)
    if not resp.ok:
        logger.error("Groq API error %s — %s", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def call_content_llm_with_fallback(prompt: str, ollama_timeout: int = 15) -> str:
    try:
        llm = ChatOllama(
            model="gemma2:2b",
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
            num_ctx=OLLAMA_NUM_CTX,
            num_thread=OLLAMA_NUM_THREADS,
            sync_client_kwargs={"timeout": ollama_timeout},
        )
        response = llm.invoke(prompt)
        return _normalize_content(response.content)
    except Exception:
        logger.warning("Ollama failed, falling back to Groq...")
        return _call_groq(prompt, temperature=0.3)
