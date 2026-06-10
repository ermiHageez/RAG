import os
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    store = FaissVectorStore("faiss_store")
    if store.build_from_documents(docs):
        store.load()
        print(
            store.query("who is the CEO of etech?", top_k=3)
        )
    else:
        print("[WARN] Skipping vector store query because no documents were loaded.")
    rag_search = RAGSearch()
    query = "who is the CEO of etech?"
    result = rag_search.search_and_summarize(query, top_k=3)
    print("\nSummary:", result["summary"])
    if result["sources"]:
        print("\nSources:")
        for i, src in enumerate(result["sources"], 1):
            doc_name = os.path.basename(src["document"])
            print(f"  [{i}] {doc_name} — Page {src['page']}")
