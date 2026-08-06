from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.repositories.base import CRUDBase
from app.models.profile import UserProfile, ProfileSkill, Skill
from app.models.user import User

class UserProfileRepository(CRUDBase[UserProfile]):
    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> Optional[UserProfile]:
        query = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                selectinload(UserProfile.department),
                selectinload(UserProfile.skills_association).selectinload(ProfileSkill.skill),
                selectinload(UserProfile.user).selectinload(User.role)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


    async def update_skills(self, db: AsyncSession, profile_id: str, skills_in: List[dict]) -> None:
        # Delete existing profile skills
        delete_query = delete(ProfileSkill).where(ProfileSkill.profile_id == profile_id)
        await db.execute(delete_query)
        
        # Add new profile skills
        for skill_data in skills_in:
            profile_skill = ProfileSkill(
                profile_id=profile_id,
                skill_id=skill_data["skill_id"],
                level=skill_data["level"]
            )
            db.add(profile_skill)
        await db.flush()

profile_repo = UserProfileRepository(UserProfile)
