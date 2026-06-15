from dotenv import load_dotenv
from src import manifest
from src.data_loader import load_all_documents
from src.rag.vectorstore import FaissVectorStore
from src.agents.llm import get_reasoning_llm, get_embedding_model


load_dotenv()


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        data_dir: str = "data",
        get_embedding_model=get_embedding_model,
        llm_model: str = "llama-3.3-70b-versatile",
    ):
        self.vectorstore = FaissVectorStore(persist_dir)
        if manifest.needs_rebuild(persist_dir, data_dir):
            docs = load_all_documents(data_dir)
            if not self.vectorstore.build_from_documents(docs, data_dir=data_dir):
                print(
                    "[WARN] Search initialized without a vector index because no documents were available."
                )
            self.llm = get_reasoning_llm()
            print(f"[INFO] Local LLM initialized")
            return
        else:
            self.vectorstore.load()
        self.llm = get_reasoning_llm()
        print(f"[INFO] Local LLM initialized")

    def search_and_summarize(self, query: str, top_k: int = 5) -> dict:
        if self.vectorstore.index is None:
            return {
                "summary": "No vector index is available. Add documents to data/ and rebuild the store.",
                "sources": [],
            }
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return {"summary": "No relevant documents found.", "sources": []}

        # Extract source references (document path + page)
        sources = []
        seen = set()
        for r in results:
            meta = r.get("metadata", {})
            src = meta.get("source", {})
            if isinstance(src, dict):
                doc = src.get("source", "Unknown")
                page = src.get("page_label", src.get("page", "N/A"))
            else:
                doc = str(src) if src else "Unknown"
                page = "N/A"
            key = (doc, str(page))
            if key not in seen:
                seen.add(key)
                sources.append({"document": doc, "page": page})

        prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""
        response = self.llm.invoke([prompt])
        content = response.content
        if isinstance(content, list):
            summary = " ".join(str(c) for c in content)
        else:
            summary = str(content)

        return {"summary": summary, "sources": sources}


# Example usage
if __name__ == "__main__":
    rag_search = RAGSearch()
    query = "What is attention mechanism?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)
