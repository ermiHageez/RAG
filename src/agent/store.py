_VECTORSTORE = None


def get_vectorstore():
    global _VECTORSTORE
    if _VECTORSTORE is None:
        from src.vectorstore import FaissVectorStore
        store = FaissVectorStore("faiss_store")
        store.load()
        _VECTORSTORE = store
    return _VECTORSTORE
