from src.rag.data_loader import load_all_documents
from src.rag.vectorstore import FaissVectorStore

if __name__ == "__main__":
    docs = load_all_documents("data")
    print(f"Loaded {len(docs)} documents from data/")
    if docs:
        store = FaissVectorStore("faiss_store")
        store.build_from_documents(docs)
        print(f"FAISS index built at faiss_store/ ({len(store.metadata)} chunks)")
    else:
        print("No documents found — place files in data/ and retry")
