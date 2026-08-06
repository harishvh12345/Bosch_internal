import numpy as np
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.search import SearchService
from app.repositories.document_repo import doc_chunk_repo
from app.models.document import DocumentChunk

class LocalVectorSearchService(SearchService):
    def __init__(self):
        pass

    async def index_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> bool:
        # Chunks are stored directly in PostgreSQL via document repository/service
        # No extra step needed for local memory-based vector search since it queries PG chunks dynamically
        return True

    async def search_similarity_with_db(
        self, db: AsyncSession, query_vector: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculates cosine similarity in-memory using Numpy.
        Retrieves all chunks from the PostgreSQL database, filters, and ranks them.
        """
        chunks = await doc_chunk_repo.get_all_chunks(db)
        if not chunks:
            return []

        # Filter out chunks without embeddings
        valid_chunks: List[DocumentChunk] = [c for c in chunks if c.embedding is not None]
        if not valid_chunks:
            return []

        # Convert embeddings and query vector to numpy arrays
        embeddings_matrix = np.array([c.embedding for c in valid_chunks])  # Shape: (num_chunks, vector_dim)
        q_vec = np.array(query_vector)

        # Compute cosine similarity: (A . B) / (||A|| * ||B||)
        dot_products = np.dot(embeddings_matrix, q_vec)
        norms_matrix = np.linalg.norm(embeddings_matrix, axis=1)
        norm_query = np.linalg.norm(q_vec)

        # Avoid divide-by-zero
        similarities = dot_products / (norms_matrix * norm_query + 1e-9)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            chunk = valid_chunks[idx]
            results.append({
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": float(similarities[idx])
            })
            
        return results

    async def index_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> bool:
        return True

    async def search_similarity(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        # The search_similarity_with_db should be used in FastAPI routes to pass DB session
        return []

    async def delete_document_index(self, document_id: str) -> bool:
        return True

vector_search = LocalVectorSearchService()
