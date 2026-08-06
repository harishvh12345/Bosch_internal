from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.repositories.base import CRUDBase
from app.models.document import Document, DocumentChunk

class DocumentRepository(CRUDBase[Document]):
    async def get_all_with_chunks(self, db: AsyncSession) -> List[Document]:
        query = select(Document).options(selectinload(Document.chunks))
        result = await db.execute(query)
        return list(result.scalars().all())

class DocumentChunkRepository(CRUDBase[DocumentChunk]):
    async def get_by_document(self, db: AsyncSession, document_id: str) -> List[DocumentChunk]:
        query = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_all_chunks(self, db: AsyncSession) -> List[DocumentChunk]:
        query = select(DocumentChunk)
        result = await db.execute(query)
        return list(result.scalars().all())

doc_repo = DocumentRepository(Document)
doc_chunk_repo = DocumentChunkRepository(DocumentChunk)
