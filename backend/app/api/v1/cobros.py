from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.models.cobro import CobroCreate, CobroUpdate, CobroPublic
from app.models.contrato import Contrato
from app.models.persona import Persona
from app.models.user import User
from app.crud.cobro import (
    get_cobro,
    get_cobros_by_contrato,
    get_cobros,
    create_cobro,
    update_cobro,
    delete_cobro,
)
from app.core.deps import get_current_active_user
from app.api.v1.notifications import emit_cobro_notification

router = APIRouter()


@router.get("/", response_model=List[CobroPublic])
async def list_cobros(
    skip: int = 0,
    limit: int = 100,
    fecha_inicio: Optional[date] = Query(None, description="Filter from date"),
    fecha_fin: Optional[date] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all cobros with optional date range filter."""
    return await get_cobros(db, skip=skip, limit=limit, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/{cobro_id}", response_model=CobroPublic)
async def read_cobro(
    cobro_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a cobro by ID."""
    cobro = await get_cobro(db, cobro_id)
    if not cobro:
        raise HTTPException(status_code=404, detail="Cobro not found")
    return cobro


@router.get("/contrato/{contrato_id}", response_model=List[CobroPublic])
async def list_cobros_by_contrato(
    contrato_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all cobros for a contrato."""
    return await get_cobros_by_contrato(db, contrato_id)


@router.post("/", response_model=CobroPublic, status_code=status.HTTP_201_CREATED)
async def create_new_cobro(
    cobro_in: CobroCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new cobro."""
    cobro = await create_cobro(db, cobro_in)

    # Emit notification to admin users
    try:
        result = await db.execute(select(Contrato).where(Contrato.id == cobro_in.contrato_id))
        contrato = result.scalar_one_or_none()
        inquilino_nombre = ""
        inmueble_direccion = ""
        if contrato:
            # Get inquilino name
            inq_result = await db.execute(select(Persona).where(Persona.id == contrato.inquilino_id))
            inquilino = inq_result.scalar_one_or_none()
            if inquilino:
                inquilino_nombre = inquilino.nombre
            # Get inmueble address
            from app.models.inmueble import Inmueble
            inm_result = await db.execute(select(Inmueble).where(Inmueble.id == contrato.inmueble_id))
            inmueble = inm_result.scalar_one_or_none()
            if inmueble:
                inmueble_direccion = inmueble.direccion

        await emit_cobro_notification(
            usuario_nombre=current_user.full_name or current_user.email,
            usuario_email=current_user.email,
            monto=cobro.monto,
            inquilino_nombre=inquilino_nombre,
            inmueble_direccion=inmueble_direccion,
        )
    except Exception:
        pass  # Notification failure should not block cobro creation

    return cobro


@router.put("/{cobro_id}", response_model=CobroPublic)
async def update_existing_cobro(
    cobro_id: str,
    cobro_in: CobroUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a cobro."""
    cobro = await get_cobro(db, cobro_id)
    if not cobro:
        raise HTTPException(status_code=404, detail="Cobro not found")
    return await update_cobro(db, cobro_id, cobro_in)


@router.delete("/{cobro_id}")
async def delete_existing_cobro(
    cobro_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a cobro."""
    cobro = await get_cobro(db, cobro_id)
    if not cobro:
        raise HTTPException(status_code=404, detail="Cobro not found")
    await delete_cobro(db, cobro_id)
    return {"message": "Cobro deleted successfully"}
