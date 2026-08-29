from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contrato import Contrato, ContratoCreate, ContratoUpdate


async def get_contrato(db: AsyncSession, contrato_id: str) -> Optional[Contrato]:
    """Get a contrato by ID."""
    return await db.get(Contrato, contrato_id)


async def get_contratos_by_inmueble(db: AsyncSession, inmueble_id: str) -> List[Contrato]:
    """Get all contratos for an inmueble."""
    statement = select(Contrato).where(Contrato.inmueble_id == inmueble_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_contratos_by_inquilino(db: AsyncSession, inquilino_id: str) -> List[Contrato]:
    """Get all contratos for an inquilino."""
    statement = select(Contrato).where(Contrato.inquilino_id == inquilino_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_contratos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
) -> List[Contrato]:
    """Get multiple contratos."""
    statement = select(Contrato)
    
    if activo is not None:
        statement = statement.where(Contrato.activo == activo)
    
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_contrato(db: AsyncSession, contrato_in: ContratoCreate) -> Contrato:
    """Create a new contrato."""
    contrato_id = str(uuid.uuid4())
    
    contrato = Contrato(
        id=contrato_id,
        inmueble_id=contrato_in.inmueble_id,
        inquilino_id=contrato_in.inquilino_id,
        fecha_inicio=contrato_in.fecha_inicio,
        fecha_fin=contrato_in.fecha_fin,
        fecha_maxima_pago=contrato_in.fecha_maxima_pago,
        modalidad_pago=contrato_in.modalidad_pago,
        frecuencia=contrato_in.frecuencia,
        monto_base=contrato_in.monto_base,
        moneda=contrato_in.moneda,
        indice=contrato_in.indice,
        periodo_indexacion=contrato_in.periodo_indexacion,
        tipo_producto=contrato_in.tipo_producto,
        kilos=contrato_in.kilos,
        precio_kilo=contrato_in.precio_kilo,
        fuente_precio_agro=contrato_in.fuente_precio_agro,
        activo=contrato_in.activo,
        created_at=datetime.utcnow(),
    )
    
    db.add(contrato)
    await db.commit()
    await db.refresh(contrato)
    return contrato


async def update_contrato(db: AsyncSession, contrato_id: str, contrato_in: ContratoUpdate) -> Optional[Contrato]:
    """Update a contrato."""
    contrato = await db.get(Contrato, contrato_id)
    if not contrato:
        return None
    
    update_data = contrato_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(contrato, key, value)
    
    contrato.updated_at = datetime.utcnow()
    db.add(contrato)
    await db.commit()
    await db.refresh(contrato)
    return contrato


async def delete_contrato(db: AsyncSession, contrato_id: str) -> bool:
    """Delete a contrato."""
    contrato = await db.get(Contrato, contrato_id)
    if not contrato:
        return False
    
    await db.delete(contrato)
    await db.commit()
    return True
