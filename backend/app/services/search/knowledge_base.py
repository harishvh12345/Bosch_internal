import os
import logging
from uuid import UUID
from typing import List, Dict, Any, BinaryIO
from sqlalchemy.ext.asyncio import AsyncSession
from pypdf import PdfReader
from app.repositories.document_repo import doc_repo, doc_chunk_repo
from app.models.document import Document, DocumentChunk
from app.services.storage.local_storage import local_storage
from app.services.gemini.client import embedding_service
from app.services.search.vector_search import vector_search

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        pass

    async def upload_and_index_pdf(
        self, db: AsyncSession, file_data: BinaryIO, filename: str, user_id: UUID
    ) -> Document:
        """
        Uploads PDF to local storage, extracts text, chunks it, 
        generates embeddings, and saves metadata + chunks in DB.
        """
        # 1. Upload to local storage
        filepath = await local_storage.upload_file(file_data, filename, folder="documents")
        
        # 2. Save Document metadata in DB
        doc_data = {
            "filename": filename,
            "filepath": filepath,
            "file_type": "PDF",
            "uploaded_by": user_id
        }
        document = await doc_repo.create(db, obj_in=doc_data)
        await db.flush()

        # 3. Extract text from PDF
        try:
            reader = PdfReader(filepath)
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text() or ""
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {filename}: {e}")
            raise ValueError(f"Could not parse PDF content: {e}")

        # 4. Chunk text (overlapping sliding window)
        chunks = self._chunk_text(text_content, chunk_size=800, overlap=150)
        
        # 5. Generate embeddings and save chunks
        for idx, chunk_text in enumerate(chunks):
            embedding = await embedding_service.get_embedding(chunk_text)
            
            chunk_obj = DocumentChunk(
                document_id=document.id,
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding
            )
            db.add(chunk_obj)
            
        await db.flush()
        logger.info(f"Indexed document {filename} with {len(chunks)} chunks.")
        return document

    async def get_relevant_context(
        self, db: AsyncSession, query: str, top_k: int = 4
    ) -> str:
        """Generates a text context block of top-k similar chunks for prompt injection."""
        if not query:
            return ""
            
        # Get query embedding
        query_vector = await embedding_service.get_embedding(query)
        
        # Search similarities
        hits = await vector_search.search_similarity_with_db(db, query_vector, top_k=top_k)
        
        if not hits:
            return "No matching internal Bosch training documentation found."
            
        context_blocks = []
        for h in hits:
            context_blocks.append(f"[Ref Chunk {h['chunk_index']}]: {h['content']}")
            
        return "\n\n".join(context_blocks)

    def _chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """Simple text sliding window chunker based on character index."""
        if not text:
            return []
            
        words = text.split()
        chunks = []
        
        # Reconstruct text into character blocks
        current_word_idx = 0
        while current_word_idx < len(words):
            chunk_words = words[current_word_idx : current_word_idx + 120] # approx 700-800 characters
            if not chunk_words:
                break
            chunks.append(" ".join(chunk_words))
            current_word_idx += 90  # overlap of ~30 words (approx 150-200 characters)
            
        return chunks

knowledge_base = KnowledgeBaseService()
