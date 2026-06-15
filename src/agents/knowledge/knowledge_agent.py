from src.agents.state import AgentState
from src.rag.vectorstore import FaissVectorStore
from src.rag.retriever import Retriever


_STORE: FaissVectorStore | None = None
_RETRIEVER: Retriever | None = None


def _get_retriever() -> Retriever | None:
    global _STORE, _RETRIEVER
    if _RETRIEVER is None:
        _STORE = FaissVectorStore("faiss_store")
        _STORE.load()
        if _STORE.index is not None:
            _RETRIEVER = Retriever(_STORE)
    return _RETRIEVER


def run_knowledge_agent(state: AgentState) -> dict:
    query = state.get("query", "")
    retriever = _get_retriever()

    if retriever is None:
        print("[KnowledgeAgent] No FAISS index available")
        return {
            "knowledge_context": [
                {"text": "[No documents indexed. Add files to data/ and rebuild.]", "source": "", "relevance": 0.0}
            ]
        }

    results = retriever.retrieve(query, top_k=5, rerank_top_k=3)
    context = []
    for r in results:
        meta = r.get("metadata", {})
        text = meta.get("text", "")
        source = meta.get("source", {})
        if isinstance(source, dict):
            source = source.get("source", "")
        context.append({
            "text": text,
            "source": str(source),
            "relevance": 1.0 - min(r.get("distance", 0), 1.0),
        })

    print(f"[KnowledgeAgent] Retrieved {len(context)} chunks for query")
    return {"knowledge_context": context}
