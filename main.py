import os
from src.rag.data_loader import load_all_documents
from src.rag.vectorstore import FaissVectorStore
from src.rag.retriever import Retriever

if __name__ == "__main__":
    docs = load_all_documents("data")
    store = FaissVectorStore("faiss_store")
    if store.build_from_documents(docs):
        store.load()
        if store.index is not None:
            print(f"FAISS index rebuilt: {store.index.ntotal} entries, dimension {store.index.d}")
        else:
            print("FAISS index rebuilt, but index metadata is unavailable.")

        retriever = Retriever(store)
        results = retriever.retrieve("who is the CEO of etech?", top_k=5, rerank_top_k=3)
        print(f"\nQuery results: {len(results)}")
        for r in results:
            meta = r.get("metadata", {})
            text = meta.get("text", "")[:120]
            print(f"  [{r['distance']:.3f}] {text}...")
    else:
        print("[WARN] No documents loaded, skipping.")
