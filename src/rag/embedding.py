import numpy as np
from typing import Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.agents.llm import get_embedding_model


class EmbeddingPipeline:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = get_embedding_model()

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(documents)
        print(f"[DEBUG] Split {len(chunks)} chunks from {len(documents)} documents")
        return chunks

    def embed_chunks(self, chunks: List[Any]) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks")
        vectors = self.embeddings.embed_documents(texts)
        embeddings = np.array(vectors, dtype=np.float32)
        print(f"[DEBUG] Embeddings shape: {embeddings.shape}")
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        vec = self.embeddings.embed_query(query)
        return np.array([vec], dtype=np.float32)
