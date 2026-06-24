import re
import numpy as np
from typing import Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.agents.llm import get_embedding_model


class EmbeddingPipeline:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.embeddings = get_embedding_model()
        except Exception as e:
            raise RuntimeError(
                f"Failed to load embedding model. Check that Ollama is running "
                f"and the model is pulled (`ollama pull <model>`). Error: {e}"
            )

    @staticmethod
    def _clean_documents(documents: List[Any]) -> List[Any]:
        for doc in documents:
            lines = doc.page_content.split("\n")
            cleaned = [l for l in lines if not re.match(r"^[\s]*[-=]{3,}[\s]*$", l)]
            doc.page_content = "\n".join(cleaned)
        return documents

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        documents = self._clean_documents(documents)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(documents)
        print(f"[DEBUG] Split {len(chunks)} chunks from {len(documents)} documents")
        return chunks

    def embed_chunks(self, chunks: List[Any], batch_size: int = 50) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks (batch_size={batch_size})")
        all_vectors = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            print(f"[DEBUG] Embedding batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size} ({len(batch)} chunks)")
            vectors = self.embeddings.embed_documents(batch)
            all_vectors.extend(vectors)
        embeddings = np.array(all_vectors, dtype=np.float32)
        print(f"[DEBUG] Embeddings shape: {embeddings.shape}")
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        vec = self.embeddings.embed_query(query)
        return np.array([vec], dtype=np.float32)
