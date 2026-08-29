from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.config import settings
from app.core.security import verify_token
from app.models.user import User
from app.db.session import get_db

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-Access-Token", auto_error=False)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_access_token: Optional[str] = Depends(api_key_header),
) -> User:
    """Get current user from access token.
    
    Checks in order:
    1. X-Access-Token header (for Swagger UI / API clients)
    2. access_token cookie (for browser/frontend)
    3. Authorization: Bearer header
    """
    access_token = x_access_token

    # If not in header, try cookie
    if not access_token:
        access_token = request.cookies.get("access_token")

    # If not in cookie, try Authorization Bearer header
    if not access_token:
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
            if credentials:
                access_token = credentials.credentials
        except HTTPException:
            pass

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Login via POST /api/login and use the access_token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(access_token, settings.JWT_SECRET_KEY)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
