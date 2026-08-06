from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import CredentialsException, PermissionException
from app.core.security import security_service
from app.repositories.user_repo import user_repo, role_repo, dept_repo
from app.schemas.user import UserCreate, Token, UserLogin, UserResponse
from app.models.user import User
from app.models.profile import UserProfile

class AuthService:
    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        # Check if user exists
        existing_user = await user_repo.get_by_email(db, user_in.email)
        if existing_user:
            raise CredentialsException(detail="Email already registered")
            
        # Get target role
        role = await role_repo.get_by_name(db, user_in.role_name)
        if not role:
            # Create default role if missing
            role = await role_repo.create(db, obj_in={"name": user_in.role_name})
            
        hashed_password = security_service.hash_password(user_in.password)
        
        user_data = {
            "email": user_in.email,
            "password_hash": hashed_password,
            "role_id": role.id,
            "is_active": True
        }
        
        user = await user_repo.create(db, obj_in=user_data)
        
        # Create empty profile for user
        profile_data = {
            "user_id": user.id,
            "first_name": user_in.email.split("@")[0].capitalize(),
            "last_name": "Employee",
            "experience_years": 0,
            "learning_history": {}
        }
        profile_obj = UserProfile(**profile_data)
        db.add(profile_obj)
        await db.flush()
        
        return user

    async def authenticate_user(self, db: AsyncSession, login_in: UserLogin) -> Token:
        user = await user_repo.get_by_email(db, login_in.email)
        if not user:
            raise CredentialsException(detail="Invalid email or password")
            
        if not security_service.verify_password(login_in.password, user.password_hash):
            raise CredentialsException(detail="Invalid email or password")
            
        if not user.is_active:
            raise CredentialsException(detail="User account is inactive")
            
        # Generate token
        token_data = {
            "sub": str(user.id),
            "role": user.role.name
        }
        access_token = security_service.create_access_token(token_data)
        
        # Format response
        user_res = UserResponse.model_validate(user)
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_res
        )

auth_service = AuthService()
