import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from langchain_groq import ChatGroq

load_dotenv()


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "llama-3.3-70b-versatile",
    ):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from src.data_loader import load_all_documents

            docs = load_all_documents("data")
            if not self.vectorstore.build_from_documents(docs):
                print(
                    "[WARN] Search initialized without a vector index because no documents were available."
                )
                self.llm = ChatGroq(model=llm_model)
                print(f"[INFO] Groq LLM initialized: {llm_model}")
                return
        else:
            self.vectorstore.load()
        self.llm = ChatGroq(model=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

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
