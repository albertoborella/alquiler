from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inquilino import Inquilino, InquilinoCreate, InquilinoUpdate


async def get_inquilino(db: AsyncSession, inquilino_id: str) -> Optional[Inquilino]:
    """Get an inquilino by ID."""
    return await db.get(Inquilino, inquilino_id)


async def get_inquilino_by_cuit(db: AsyncSession, cuit: str) -> Optional[Inquilino]:
    """Get an inquilino by CUIT."""
    statement = select(Inquilino).where(Inquilino.cuit == cuit)
    result = await db.execute(statement)
    return result.scalars().first()


async def get_inquilinos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Inquilino]:
    """Get multiple inquilinos."""
    statement = select(Inquilino).offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_inquilino(db: AsyncSession, inquilino_in: InquilinoCreate) -> Inquilino:
    """Create a new inquilino."""
    inquilino_id = str(uuid.uuid4())
    
    inquilino = Inquilino(
        id=inquilino_id,
        nombre=inquilino_in.nombre,
        cuit=inquilino_in.cuit,
        iva=inquilino_in.iva,
        telefono=inquilino_in.telefono,
        email=inquilino_in.email,
        direccion=inquilino_in.direccion,
        created_at=datetime.utcnow(),
    )
    
    db.add(inquilino)
    await db.commit()
    await db.refresh(inquilino)
    return inquilino


async def update_inquilino(db: AsyncSession, inquilino_id: str, inquilino_in: InquilinoUpdate) -> Optional[Inquilino]:
    """Update an inquilino."""
    inquilino = await db.get(Inquilino, inquilino_id)
    if not inquilino:
        return None
    
    update_data = inquilino_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(inquilino, key, value)
    
    inquilino.updated_at = datetime.utcnow()
    db.add(inquilino)
    await db.commit()
    await db.refresh(inquilino)
    return inquilino


async def delete_inquilino(db: AsyncSession, inquilino_id: str) -> bool:
    """Delete an inquilino."""
    inquilino = await db.get(Inquilino, inquilino_id)
    if not inquilino:
        return False
    
    await db.delete(inquilino)
    await db.commit()
    return True
