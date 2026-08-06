from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional, Dict, Any

class SkillBase(BaseModel):
    name: str
    category: str

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: UUID

    class Config:
        from_attributes = True

class ProfileSkillResponse(BaseModel):
    skill: SkillResponse
    level: int  # 1 to 5 scale

    class Config:
        from_attributes = True

class ProfileSkillUpdate(BaseModel):
    skill_id: UUID
    level: int

class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    experience_years: int = 0
    learning_history: Dict[str, Any] = {}

class UserProfileCreate(UserProfileBase):
    department_id: Optional[UUID] = None
    skills: List[ProfileSkillUpdate] = []

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    experience_years: Optional[int] = None
    department_id: Optional[UUID] = None
    learning_history: Optional[Dict[str, Any]] = None
    skills: Optional[List[ProfileSkillUpdate]] = None

from app.schemas.user import DepartmentResponse

class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    department: Optional[DepartmentResponse] = None
    skills_association: List[ProfileSkillResponse] = []

    class Config:
        from_attributes = True

