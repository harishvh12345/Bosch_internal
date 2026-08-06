from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import CRUDBase
from app.models.recommendation import Recommendation

class RecommendationRepository(CRUDBase[Recommendation]):
    async def get_active_by_user(self, db: AsyncSession, user_id: str) -> List[Recommendation]:
        query = (
            select(Recommendation)
            .where(Recommendation.user_id == user_id, Recommendation.is_active == True)
            .order_by(Recommendation.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

rec_repo = RecommendationRepository(Recommendation)
