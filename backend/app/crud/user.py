from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalars().first()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get multiple users."""
    statement = select(User)
    if is_active is not None:
        statement = statement.where(User.is_active == is_active)
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user."""
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_in.password)
    
    user = User(
        id=user_id,
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: str, user_in: UserUpdate) -> Optional[User]:
    """Update a user."""
    user = await db.get(User, user_id)
    if not user:
        return None
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """Delete a user."""
    user = await db.get(User, user_id)
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    return True


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    from app.core.security import verify_password
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
