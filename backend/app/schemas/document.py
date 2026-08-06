from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    filepath: str
    file_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str

    class Config:
        from_attributes = True
