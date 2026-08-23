from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.models.comprobante import ComprobanteCreate, ComprobanteUpdate, ComprobantePublic
from app.crud.comprobante import (
    get_comprobante,
    get_comprobantes_by_cobro,
    get_comprobantes_by_propietario,
    get_comprobantes,
    create_comprobante,
    update_comprobante,
    delete_comprobante,
)
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[ComprobantePublic])
async def list_comprobantes(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = Query(None, description="Filter by tipo: expensas, honorarios, comprobante"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all comprobantes with optional filters."""
    return await get_comprobantes(db, skip=skip, limit=limit, tipo=tipo)


@router.get("/{comprobante_id}", response_model=ComprobantePublic)
async def read_comprobante(
    comprobante_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a comprobante by ID."""
    comprobante = await get_comprobante(db, comprobante_id)
    if not comprobante:
        raise HTTPException(status_code=404, detail="Comprobante not found")
    return comprobante


@router.get("/cobro/{cobro_id}", response_model=List[ComprobantePublic])
async def list_comprobantes_by_cobro(
    cobro_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all comprobantes for a cobro."""
    return await get_comprobantes_by_cobro(db, cobro_id)


@router.get("/propietario/{propietario_id}", response_model=List[ComprobantePublic])
async def list_comprobantes_by_propietario(
    propietario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all comprobantes for a propietario."""
    return await get_comprobantes_by_propietario(db, propietario_id)


@router.post("/", response_model=ComprobantePublic, status_code=status.HTTP_201_CREATED)
async def create_new_comprobante(
    comprobante_in: ComprobanteCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new comprobante."""
    return await create_comprobante(db, comprobante_in)


@router.put("/{comprobante_id}", response_model=ComprobantePublic)
async def update_existing_comprobante(
    comprobante_id: str,
    comprobante_in: ComprobanteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a comprobante."""
    comprobante = await get_comprobante(db, comprobante_id)
    if not comprobante:
        raise HTTPException(status_code=404, detail="Comprobante not found")
    return await update_comprobante(db, comprobante_id, comprobante_in)


@router.delete("/{comprobante_id}")
async def delete_existing_comprobante(
    comprobante_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a comprobante."""
    comprobante = await get_comprobante(db, comprobante_id)
    if not comprobante:
        raise HTTPException(status_code=404, detail="Comprobante not found")
    await delete_comprobante(db, comprobante_id)
    return {"message": "Comprobante deleted successfully"}
