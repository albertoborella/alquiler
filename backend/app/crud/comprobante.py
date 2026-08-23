from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comprobante import Comprobante, ComprobanteCreate, ComprobanteUpdate


async def get_comprobante(db: AsyncSession, comprobante_id: str) -> Optional[Comprobante]:
    """Get a comprobante by ID."""
    return await db.get(Comprobante, comprobante_id)


async def get_comprobantes_by_cobro(db: AsyncSession, cobro_id: str) -> List[Comprobante]:
    """Get all comprobantes for a cobro."""
    statement = select(Comprobante).where(Comprobante.cobro_id == cobro_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_comprobantes_by_propietario(db: AsyncSession, propietario_id: str) -> List[Comprobante]:
    """Get all comprobantes for a propietario."""
    statement = select(Comprobante).where(Comprobante.propietario_id == propietario_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_comprobantes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None
) -> List[Comprobante]:
    """Get multiple comprobantes."""
    statement = select(Comprobante)
    
    if tipo is not None:
        statement = statement.where(Comprobante.tipo == tipo)
    
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_comprobante(db: AsyncSession, comprobante_in: ComprobanteCreate) -> Comprobante:
    """Create a new comprobante."""
    comprobante_id = str(uuid.uuid4())
    
    comprobante = Comprobante(
        id=comprobante_id,
        cobro_id=comprobante_in.cobro_id,
        propietario_id=comprobante_in.propietario_id,
        tipo=comprobante_in.tipo,
        numero=comprobante_in.numero,
        descripcion=comprobante_in.descripcion,
        monto_proporcional=comprobante_in.monto_proporcional,
        porcentaje_participacion=comprobante_in.porcentaje_participacion,
        created_at=datetime.utcnow(),
    )
    
    db.add(comprobante)
    await db.commit()
    await db.refresh(comprobante)
    return comprobante


async def update_comprobante(db: AsyncSession, comprobante_id: str, comprobante_in: ComprobanteUpdate) -> Optional[Comprobante]:
    """Update a comprobante."""
    comprobante = await db.get(Comprobante, comprobante_id)
    if not comprobante:
        return None
    
    update_data = comprobante_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(comprobante, key, value)
    
    db.add(comprobante)
    await db.commit()
    await db.refresh(comprobante)
    return comprobante


async def delete_comprobante(db: AsyncSession, comprobante_id: str) -> bool:
    """Delete a comprobante."""
    comprobante = await db.get(Comprobante, comprobante_id)
    if not comprobante:
        return False
    
    await db.delete(comprobante)
    await db.commit()
    return True
