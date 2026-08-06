from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.v1.auth import get_current_user, allow_manager, allow_all
from app.services.search.knowledge_base import knowledge_base
from app.repositories.document_repo import doc_repo
from app.schemas.document import DocumentResponse
from app.models.user import User
from typing import List

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_manager)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for RAG indexing currently."
        )
        
    try:
        # Pass file stream to knowledge base service
        return await knowledge_base.upload_and_index_pdf(
            db, file.file, file.filename, current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and index PDF: {e}"
        )

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(allow_all)
):
    return await doc_repo.get_multi(db, limit=100)
