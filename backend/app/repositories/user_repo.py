from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.repositories.base import CRUDBase
from app.models.user import User, Role, Department
from app.models.profile import UserProfile, Skill, ProfileSkill

class UserRepository(CRUDBase[User]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        query = (
            select(User)
            .where(User.email == email)
            .options(selectinload(User.role))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_profile(self, db: AsyncSession, user_id: str) -> Optional[User]:
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.role),
                selectinload(User.profile).selectinload(UserProfile.department),
                selectinload(User.profile)
                .selectinload(UserProfile.skills_association)
                .selectinload(ProfileSkill.skill)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

class RoleRepository(CRUDBase[Role]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        query = select(Role).where(Role.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class DepartmentRepository(CRUDBase[Department]):
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Department]:
        query = select(Department).where(Department.code == code)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class SkillRepository(CRUDBase[Skill]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Skill]:
        query = select(Skill).where(Skill.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

user_repo = UserRepository(User)
role_repo = RoleRepository(Role)
dept_repo = DepartmentRepository(Department)
skill_repo = SkillRepository(Skill)
