from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.profile_repo import profile_repo
from app.repositories.user_repo import user_repo, skill_repo, dept_repo
from app.schemas.profile import UserProfileUpdate, UserProfileResponse
from app.models.profile import UserProfile, Skill
from app.core.exceptions import NotFoundException

class EmployeeService:
    async def get_profile(self, db: AsyncSession, user_id: UUID) -> UserProfile:
        profile = await profile_repo.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundException(detail="Profile not found for this user")
        return profile

    async def update_profile(
        self, db: AsyncSession, user_id: UUID, profile_in: UserProfileUpdate
    ) -> UserProfile:
        profile = await profile_repo.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundException(detail="Profile not found")
            
        update_dict = profile_in.model_dump(exclude_unset=True, exclude={"skills"})
        
        # Update scalar fields
        profile = await profile_repo.update(db, db_obj=profile, obj_in=update_dict)
        
        # Update skills association if provided
        if profile_in.skills is not None:
            skills_data = []
            for item in profile_in.skills:
                # Verify skill exists
                skill = await skill_repo.get(db, item.skill_id)
                if not skill:
                    raise NotFoundException(detail=f"Skill with ID {item.skill_id} not found")
                skills_data.append({
                    "skill_id": item.skill_id,
                    "level": item.level
                })
            await profile_repo.update_skills(db, profile.id, skills_data)
            
        # Refresh and return
        await db.refresh(profile)
        return profile

    async def get_all_skills(self, db: AsyncSession) -> List[Skill]:
        return await skill_repo.get_multi(db, limit=200)

    async def seed_default_skills(self, db: AsyncSession) -> None:
        """Seeds standard skills for engineering teams."""
        defaults = [
            ("C Programming", "Embedded Systems"),
            ("MATLAB Simulink", "Control Systems"),
            ("CAN Bus Diagnostics", "Automotive Communication"),
            ("ECU Flash Programming", "Automotive Communication"),
            ("PID Control Damping", "Control Systems"),
            ("Python FastAPI", "Backend Development"),
            ("PostgreSQL Administration", "Databases"),
            ("Docker Orchestration", "DevOps")
        ]
        for name, cat in defaults:
            exists = await skill_repo.get_by_name(db, name)
            if not exists:
                await skill_repo.create(db, obj_in={"name": name, "category": cat})

employee_service = EmployeeService()
