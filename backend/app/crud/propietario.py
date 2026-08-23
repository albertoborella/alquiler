from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.propietario import Propietario, PropietarioCreate, PropietarioUpdate


async def get_propietario(db: AsyncSession, propietario_id: str) -> Optional[Propietario]:
    """Get a propietario by ID."""
    return await db.get(Propietario, propietario_id)


async def get_propietario_by_dni_cuit(db: AsyncSession, dni_cuit: str) -> Optional[Propietario]:
    """Get a propietario by DNI/CUIT."""
    statement = select(Propietario).where(Propietario.dni_cuit == dni_cuit)
    result = await db.execute(statement)
    return result.scalars().first()


async def get_propietarios(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Propietario]:
    """Get multiple propietarios."""
    statement = select(Propietario).offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_propietario(db: AsyncSession, propietario_in: PropietarioCreate) -> Propietario:
    """Create a new propietario."""
    propietario_id = str(uuid.uuid4())
    
    propietario = Propietario(
        id=propietario_id,
        nombre=propietario_in.nombre,
        dni_cuit=propietario_in.dni_cuit,
        telefono=propietario_in.telefono,
        email=propietario_in.email,
        direccion=propietario_in.direccion,
        created_at=datetime.utcnow(),
    )
    
    db.add(propietario)
    await db.commit()
    await db.refresh(propietario)
    return propietario


async def update_propietario(db: AsyncSession, propietario_id: str, propietario_in: PropietarioUpdate) -> Optional[Propietario]:
    """Update a propietario."""
    propietario = await db.get(Propietario, propietario_id)
    if not propietario:
        return None
    
    update_data = propietario_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(propietario, key, value)
    
    propietario.updated_at = datetime.utcnow()
    db.add(propietario)
    await db.commit()
    await db.refresh(propietario)
    return propietario


async def delete_propietario(db: AsyncSession, propietario_id: str) -> bool:
    """Delete a propietario."""
    propietario = await db.get(Propietario, propietario_id)
    if not propietario:
        return False
    
    await db.delete(propietario)
    await db.commit()
    return True
