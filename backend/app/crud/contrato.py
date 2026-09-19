from typing import Optional, List
from datetime import datetime, date
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contrato import Contrato, ContratoCreate, ContratoUpdate
from app.models.inmueble import Inmueble


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
    """Create a new contrato and update inmueble state to alquilado."""
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
    
    # Update inmueble state to alquilado
    inmueble = await db.get(Inmueble, contrato_in.inmueble_id)
    if inmueble and inmueble.estado == "disponible":
        inmueble.estado = "alquilado"
        inmueble.updated_at = datetime.utcnow()
        db.add(inmueble)
    
    await db.commit()
    await db.refresh(contrato)
    return contrato


async def update_contrato(db: AsyncSession, contrato_id: str, contrato_in: ContratoUpdate) -> Optional[Contrato]:
    """Update a contrato and manage inmueble state if active status changes."""
    contrato = await db.get(Contrato, contrato_id)
    if not contrato:
        return None
    
    update_data = contrato_in.model_dump(exclude_unset=True)
    was_active = contrato.activo
    
    for key, value in update_data.items():
        setattr(contrato, key, value)
    
    contrato.updated_at = datetime.utcnow()
    db.add(contrato)
    await db.commit()
    await db.refresh(contrato)
    
    # If contract was deactivated, check if inmueble should be disponible
    if was_active and not contrato.activo:
        # Check if there are any other active contracts for this inmueble
        stmt = select(Contrato).where(
            Contrato.inmueble_id == contrato.inmueble_id,
            Contrato.activo == True
        )
        result = await db.execute(stmt)
        active_contracts = list(result.scalars().all())
        
        # If no active contracts, set inmueble to disponible
        if len(active_contracts) == 0:
            inmueble = await db.get(Inmueble, contrato.inmueble_id)
            if inmueble and inmueble.estado == "alquilado":
                inmueble.estado = "disponible"
                inmueble.updated_at = datetime.utcnow()
                db.add(inmueble)
                await db.commit()
    
    return contrato


async def delete_contrato(db: AsyncSession, contrato_id: str) -> bool:
    """Delete a contrato and update inmueble state if no active contracts remain."""
    contrato = await db.get(Contrato, contrato_id)
    if not contrato:
        return False
    
    inmueble_id = contrato.inmueble_id
    
    await db.delete(contrato)
    await db.commit()
    
    # Check if there are any other active contracts for this inmueble
    stmt = select(Contrato).where(
        Contrato.inmueble_id == inmueble_id,
        Contrato.activo == True
    )
    result = await db.execute(stmt)
    active_contracts = list(result.scalars().all())
    
    # If no active contracts, set inmueble to disponible
    if len(active_contracts) == 0:
        inmueble = await db.get(Inmueble, inmueble_id)
        if inmueble and inmueble.estado == "alquilado":
            inmueble.estado = "disponible"
            inmueble.updated_at = datetime.utcnow()
            db.add(inmueble)
            await db.commit()
    
    return True


async def update_inmueble_states_for_expired_contracts(db: AsyncSession) -> int:
    """
    Sync inmueble states with their active contracts:
    - If inmueble is 'disponible' but has an active contract → set to 'alquilado'
    - If inmueble is 'alquilado' but no active (non-expired) contract → set to 'disponible'
    
    Returns the number of inmuebles updated.
    """
    today = date.today()
    updated_count = 0
    
    # 1. Find inmuebles marked as 'disponible' that might have active contracts
    stmt_disp = select(Inmueble).where(Inmueble.estado == "disponible")
    result_disp = await db.execute(stmt_disp)
    disponibles = list(result_disp.scalars().all())
    
    for inmueble in disponibles:
        # Check for any active contract that hasn't expired
        contrato_stmt = select(Contrato).where(
            Contrato.inmueble_id == inmueble.id,
            Contrato.activo == True,
            Contrato.fecha_fin >= today,
        )
        contrato_result = await db.execute(contrato_stmt)
        contrato_activo = contrato_result.first()
        
        if contrato_activo:
            # Has an active, non-expired contract → set to alquilado
            inmueble.estado = "alquilado"
            inmueble.updated_at = datetime.utcnow()
            db.add(inmueble)
            updated_count += 1
    
    # 2. Find inmuebles marked as 'alquilado' and verify they still have active contracts
    stmt_alq = select(Inmueble).where(Inmueble.estado == "alquilado")
    result_alq = await db.execute(stmt_alq)
    alquilados = list(result_alq.scalars().all())
    
    for inmueble in alquilados:
        # Check for any active contract that hasn't expired
        contrato_stmt = select(Contrato).where(
            Contrato.inmueble_id == inmueble.id,
            Contrato.activo == True,
            Contrato.fecha_fin >= today,
        )
        contrato_result = await db.execute(contrato_stmt)
        contrato_activo = contrato_result.first()
        
        if not contrato_activo:
            # No active non-expired contract → set to disponible
            inmueble.estado = "disponible"
            inmueble.updated_at = datetime.utcnow()
            db.add(inmueble)
            updated_count += 1
    
    if updated_count > 0:
        await db.commit()
    
    return updated_count
