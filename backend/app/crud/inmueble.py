from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inmueble import Inmueble, InmuebleCreate, InmuebleUpdate
from app.models.copropiedad import Copropiedad, CopropiedadCreate


async def get_inmueble(db: AsyncSession, inmueble_id: str) -> Optional[Inmueble]:
    """Get an inmueble by ID."""
    return await db.get(Inmueble, inmueble_id)


async def get_inmuebles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    categoria: Optional[str] = None
) -> List[Inmueble]:
    """Get multiple inmuebles with optional filters."""
    statement = select(Inmueble)
    
    if estado is not None:
        statement = statement.where(Inmueble.estado == estado)
    if categoria is not None:
        statement = statement.where(Inmueble.categoria == categoria)
    
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_inmueble(db: AsyncSession, inmueble_in: InmuebleCreate) -> Inmueble:
    """Create a new inmueble."""
    inmueble_id = str(uuid.uuid4())
    
    inmueble = Inmueble(
        id=inmueble_id,
        direccion=inmueble_in.direccion,
        categoria=inmueble_in.categoria,
        superficie=inmueble_in.superficie,
        habitaciones=inmueble_in.habitaciones,
        banos=inmueble_in.banos,
        dormitorios=inmueble_in.dormitorios,
        comodidades=inmueble_in.comodidades,
        descripcion=inmueble_in.descripcion,
        estado=inmueble_in.estado,
        created_at=datetime.utcnow(),
    )
    
    db.add(inmueble)
    await db.commit()
    await db.refresh(inmueble)
    return inmueble


async def update_inmueble(db: AsyncSession, inmueble_id: str, inmueble_in: InmuebleUpdate) -> Optional[Inmueble]:
    """Update an inmueble."""
    inmueble = await db.get(Inmueble, inmueble_id)
    if not inmueble:
        return None
    
    update_data = inmueble_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(inmueble, key, value)
    
    inmueble.updated_at = datetime.utcnow()
    db.add(inmueble)
    await db.commit()
    await db.refresh(inmueble)
    return inmueble


async def delete_inmueble(db: AsyncSession, inmueble_id: str) -> bool:
    """Delete an inmueble."""
    inmueble = await db.get(Inmueble, inmueble_id)
    if not inmueble:
        return False
    
    await db.delete(inmueble)
    await db.commit()
    return True


# Copropiedad functions
async def get_copropiedad_by_inmueble(db: AsyncSession, inmueble_id: str) -> List[Copropiedad]:
    """Get all copropiedad relationships for an inmueble."""
    statement = select(Copropiedad).where(Copropiedad.inmueble_id == inmueble_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def add_propietario_to_inmueble(
    db: AsyncSession,
    propietario_id: str,
    inmueble_id: str,
    porcentaje_participacion: float = 100.00
) -> Copropiedad:
    """Add a propietario to an inmueble (copropiedad)."""
    copropiedad_id = str(uuid.uuid4())
    
    copropiedad = Copropiedad(
        id=copropiedad_id,
        propietario_id=propietario_id,
        inmueble_id=inmueble_id,
        porcentaje_participacion=porcentaje_participacion,
        created_at=datetime.utcnow(),
    )
    
    db.add(copropiedad)
    await db.commit()
    await db.refresh(copropiedad)
    return copropiedad


async def remove_propietario_from_inmueble(
    db: AsyncSession,
    propietario_id: str,
    inmueble_id: str
) -> bool:
    """Remove a propietario from an inmueble."""
    statement = select(Copropiedad).where(
        Copropiedad.propietario_id == propietario_id,
        Copropiedad.inmueble_id == inmueble_id
    )
    result = await db.execute(statement)
    copropiedad = result.scalars().first()
    
    if not copropiedad:
        return False
    
    await db.delete(copropiedad)
    await db.commit()
    return True
