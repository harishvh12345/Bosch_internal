from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class RoleResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    code: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_name: str = "Employee"  # Employee, Manager, Admin

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    role: RoleResponse
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    role: Optional[str] = None
