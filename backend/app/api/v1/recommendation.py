from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.v1.auth import get_current_user
from app.services.recommendation_service import recommendation_service
from app.schemas.recommendation import RecommendationResponse
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await recommendation_service.get_user_recommendations(db, current_user.id)

@router.post("/refresh", response_model=List[RecommendationResponse])
async def refresh_recommendations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await recommendation_service.refresh_user_recommendations(db, current_user.id)
