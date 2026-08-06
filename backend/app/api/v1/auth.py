from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.auth_service import auth_service
from app.repositories.user_repo import user_repo
from app.core.security import security_service
from app.schemas.user import UserCreate, Token, UserLogin, UserResponse
from app.models.user import User
from app.core.exceptions import CredentialsException, PermissionException

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Dependency to retrieve the logged in user via JWT validation."""
    payload = security_service.decode_access_token(token)
    if not payload:
        raise CredentialsException()
        
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise CredentialsException()
        
    import uuid
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise CredentialsException()
        
    user = await user_repo.get_with_profile(db, user_uuid)
    if not user:
        raise CredentialsException()
        
    return user


class RoleChecker:
    """Role-based access control dependency filter."""
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in self.allowed_roles:
            raise PermissionException(detail="Access denied: Insufficient privileges")
        return current_user

# Pre-defined checkers
allow_admin = RoleChecker(["Admin"])
allow_manager = RoleChecker(["Admin", "Manager"])
allow_all = RoleChecker(["Admin", "Manager", "Employee"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_user(db, user_in)

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.authenticate_user(db, login_in)

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
