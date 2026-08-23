from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.models.cobro import CobroCreate, CobroUpdate, CobroPublic
from app.crud.cobro import (
    get_cobro,
    get_cobros_by_contrato,
    get_cobros,
    create_cobro,
    update_cobro,
    delete_cobro,
)
from app.core.deps import get_current_active_user

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
    current_user = Depends(get_current_active_user)
):
    """Create a new cobro."""
    return await create_cobro(db, cobro_in)


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
