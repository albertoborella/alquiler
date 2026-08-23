from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.models.propietario import PropietarioCreate, PropietarioUpdate, PropietarioPublic
from app.crud.propietario import (
    get_propietario,
    get_propietario_by_dni_cuit,
    get_propietarios,
    create_propietario,
    update_propietario,
    delete_propietario,
)
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[PropietarioPublic])
async def list_propietarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all propietarios."""
    return await get_propietarios(db, skip=skip, limit=limit)


@router.get("/{propietario_id}", response_model=PropietarioPublic)
async def read_propietario(
    propietario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a propietario by ID."""
    propietario = await get_propietario(db, propietario_id)
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    return propietario


@router.post("/", response_model=PropietarioPublic, status_code=status.HTTP_201_CREATED)
async def create_new_propietario(
    propietario_in: PropietarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new propietario."""
    # Check if DNI/CUIT already exists
    existing = await get_propietario_by_dni_cuit(db, propietario_in.dni_cuit)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DNI/CUIT already registered"
        )
    return await create_propietario(db, propietario_in)


@router.put("/{propietario_id}", response_model=PropietarioPublic)
async def update_existing_propietario(
    propietario_id: str,
    propietario_in: PropietarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a propietario."""
    propietario = await get_propietario(db, propietario_id)
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    return await update_propietario(db, propietario_id, propietario_in)


@router.delete("/{propietario_id}")
async def delete_existing_propietario(
    propietario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a propietario."""
    propietario = await get_propietario(db, propietario_id)
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    await delete_propietario(db, propietario_id)
    return {"message": "Propietario deleted successfully"}
