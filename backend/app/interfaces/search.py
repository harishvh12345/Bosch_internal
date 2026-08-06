from abc import ABC, abstractmethod
from typing import List, Dict, Any

class EmbeddingService(ABC):
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for a single text string."""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        pass

class SearchService(ABC):
    @abstractmethod
    async def index_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Index list of chunks in vector store.
        Each chunk contains: { "id": str, "content": str, "embedding": List[float], "chunk_index": int }
        """
        pass

    @abstractmethod
    async def search_similarity(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for top_k similar document chunks based on query vector.
        Returns list of chunks with metadata and score.
        """
        pass

    @abstractmethod
    async def delete_document_index(self, document_id: str) -> bool:
        """Remove indexed document chunks from vector store."""
        pass
