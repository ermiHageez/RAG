import numpy as np
from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from src.data_loader import load_all_documents


class EmbeddingPipeline:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = load_all_documents("data")
        print(
            f"[DEBUG] Loaded {len(self.documents)} documents. model :{model_name} chunk_size:{chunk_size} chunk_overlap:{chunk_overlap}"
        )
        self.model = SentenceTransformer(model_name)

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
        text = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(text)} chunks")
        embeddings = self.model.encode(text, show_progress_bar=True)
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings)
        print(f"[DEBUG] Embeddings shape: {embeddings.shape}")
        return embeddings


# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    emb_pipe = EmbeddingPipeline()
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print(f"[DEBUG] Embeddings shape: {embeddings.shape}")
