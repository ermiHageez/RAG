from langchain_ollama import ChatOllama, OllamaEmbeddings

OLLAMA_BASE_URL = "http://localhost:11434"


def get_embedding_model():
    return OllamaEmbeddings(
        model="qwen3-embedding:4b",
        base_url=OLLAMA_BASE_URL
    )


def get_router_llm():
    return ChatOllama(
        model="gemma3:4b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.1
    )


def get_reasoning_llm():
    return ChatOllama(
        model="qwen3:8b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.2
    )


def get_content_llm():
    return ChatOllama(
        model="llama3.1:8b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.3
    )
