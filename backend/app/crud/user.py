from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid

from app.models.user import users_table
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


async def get_user(db: AsyncSession, user_id: str) -> Optional[dict]:
    """Get a user by ID."""
    result = await db.execute(select(users_table).where(users_table.c.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[dict]:
    """Get a user by email."""
    result = await db.execute(select(users_table).where(users_table.c.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[dict]:
    """Get multiple users."""
    query = select(users_table)
    if is_active is not None:
        query = query.where(users_table.c.is_active == is_active)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_user(db: AsyncSession, user_in: UserCreate) -> dict:
    """Create a new user."""
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_in.password)
    
    user_data = {
        "id": user_id,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "full_name": user_in.full_name,
        "role": user_in.role,
        "is_active": True,
    }
    
    await db.execute(users_table.insert().values(**user_data))
    await db.commit()
    
    return await get_user(db, user_id)


async def update_user(
    db: AsyncSession,
    user_id: str,
    user_in: UserUpdate
) -> Optional[dict]:
    """Update a user."""
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    if update_data:
        await db.execute(
            users_table.update()
            .where(users_table.c.id == user_id)
            .values(**update_data)
        )
        await db.commit()
    
    return await get_user(db, user_id)


async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """Delete a user."""
    result = await db.execute(
        users_table.delete().where(users_table.c.id == user_id)
    )
    await db.commit()
    return result.rowcount > 0


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> Optional[dict]:
    """Authenticate a user."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    from app.core.security import verify_password
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
