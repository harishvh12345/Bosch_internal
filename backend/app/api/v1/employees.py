from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.v1.auth import get_current_user, allow_manager, allow_all
from app.services.employee_service import employee_service
from app.schemas.profile import UserProfileUpdate, UserProfileResponse, SkillResponse
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await employee_service.get_profile(db, current_user.id)

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await employee_service.update_profile(db, current_user.id, profile_in)

@router.get("/skills", response_model=List[SkillResponse])
async def list_skills(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(allow_all)
):
    return await employee_service.get_all_skills(db)

@router.post("/skills/seed", status_code=status.HTTP_200_OK)
async def seed_skills(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(allow_manager)
):
    await employee_service.seed_default_skills(db)
    return {"message": "Default automotive skills seeded successfully."}
