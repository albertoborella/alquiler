from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.models.contrato import ContratoCreate, ContratoUpdate, ContratoPublic
from app.crud.contrato import (
    get_contrato,
    get_contratos_by_inmueble,
    get_contratos_by_inquilino,
    get_contratos,
    create_contrato,
    update_contrato,
    delete_contrato,
)
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[ContratoPublic])
async def list_contratos(
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all contratos with optional filters."""
    return await get_contratos(db, skip=skip, limit=limit, activo=activo)


@router.get("/{contrato_id}", response_model=ContratoPublic)
async def read_contrato(
    contrato_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a contrato by ID."""
    contrato = await get_contrato(db, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato not found")
    return contrato


@router.get("/inmueble/{inmueble_id}", response_model=List[ContratoPublic])
async def list_contratos_by_inmueble(
    inmueble_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all contratos for an inmueble."""
    return await get_contratos_by_inmueble(db, inmueble_id)


@router.get("/inquilino/{inquilino_id}", response_model=List[ContratoPublic])
async def list_contratos_by_inquilino(
    inquilino_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all contratos for an inquilino."""
    return await get_contratos_by_inquilino(db, inquilino_id)


@router.post("/", response_model=ContratoPublic, status_code=status.HTTP_201_CREATED)
async def create_new_contrato(
    contrato_in: ContratoCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new contrato."""
    return await create_contrato(db, contrato_in)


@router.put("/{contrato_id}", response_model=ContratoPublic)
async def update_existing_contrato(
    contrato_id: str,
    contrato_in: ContratoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a contrato."""
    contrato = await get_contrato(db, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato not found")
    return await update_contrato(db, contrato_id, contrato_in)


@router.delete("/{contrato_id}")
async def delete_existing_contrato(
    contrato_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a contrato."""
    contrato = await get_contrato(db, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato not found")
    await delete_contrato(db, contrato_id)
    return {"message": "Contrato deleted successfully"}
