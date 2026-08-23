from typing import Optional, List
from datetime import datetime, date
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cobro import Cobro, CobroCreate, CobroUpdate


async def get_cobro(db: AsyncSession, cobro_id: str) -> Optional[Cobro]:
    """Get a cobro by ID."""
    return await db.get(Cobro, cobro_id)


async def get_cobros_by_contrato(db: AsyncSession, contrato_id: str) -> List[Cobro]:
    """Get all cobros for a contrato."""
    statement = select(Cobro).where(Cobro.contrato_id == contrato_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_cobros(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> List[Cobro]:
    """Get multiple cobros with optional date range filter."""
    statement = select(Cobro)
    
    if fecha_inicio is not None:
        statement = statement.where(Cobro.fecha_cobro >= fecha_inicio)
    if fecha_fin is not None:
        statement = statement.where(Cobro.fecha_cobro <= fecha_fin)
    
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_cobro(db: AsyncSession, cobro_in: CobroCreate) -> Cobro:
    """Create a new cobro."""
    cobro_id = str(uuid.uuid4())
    
    cobro = Cobro(
        id=cobro_id,
        contrato_id=cobro_in.contrato_id,
        fecha_cobro=cobro_in.fecha_cobro,
        monto=cobro_in.monto,
        moneda_original=cobro_in.moneda_original,
        monto_original=cobro_in.monto_original,
        cotizacion=cobro_in.cotizacion,
        fuente_precio=cobro_in.fuente_precio,
        precio_producto=cobro_in.precio_producto,
        observaciones=cobro_in.observaciones,
        created_at=datetime.utcnow(),
    )
    
    db.add(cobro)
    await db.commit()
    await db.refresh(cobro)
    return cobro


async def update_cobro(db: AsyncSession, cobro_id: str, cobro_in: CobroUpdate) -> Optional[Cobro]:
    """Update a cobro."""
    cobro = await db.get(Cobro, cobro_id)
    if not cobro:
        return None
    
    update_data = cobro_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(cobro, key, value)
    
    cobro.updated_at = datetime.utcnow()
    db.add(cobro)
    await db.commit()
    await db.refresh(cobro)
    return cobro


async def delete_cobro(db: AsyncSession, cobro_id: str) -> bool:
    """Delete a cobro."""
    cobro = await db.get(Cobro, cobro_id)
    if not cobro:
        return False
    
    await db.delete(cobro)
    await db.commit()
    return True
