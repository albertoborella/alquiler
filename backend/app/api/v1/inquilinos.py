from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.models.inquilino import InquilinoCreate, InquilinoUpdate, InquilinoPublic
from app.crud.inquilino import (
    get_inquilino,
    get_inquilino_by_cuit,
    get_inquilinos,
    create_inquilino,
    update_inquilino,
    delete_inquilino,
)
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[InquilinoPublic])
async def list_inquilinos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all inquilinos."""
    return await get_inquilinos(db, skip=skip, limit=limit)


@router.get("/{inquilino_id}", response_model=InquilinoPublic)
async def read_inquilino(
    inquilino_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get an inquilino by ID."""
    inquilino = await get_inquilino(db, inquilino_id)
    if not inquilino:
        raise HTTPException(status_code=404, detail="Inquilino not found")
    return inquilino


@router.post("/", response_model=InquilinoPublic, status_code=status.HTTP_201_CREATED)
async def create_new_inquilino(
    inquilino_in: InquilinoCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new inquilino."""
    # Check if CUIT already exists
    existing = await get_inquilino_by_cuit(db, inquilino_in.cuit)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CUIT already registered"
        )
    return await create_inquilino(db, inquilino_in)


@router.put("/{inquilino_id}", response_model=InquilinoPublic)
async def update_existing_inquilino(
    inquilino_id: str,
    inquilino_in: InquilinoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update an inquilino."""
    inquilino = await get_inquilino(db, inquilino_id)
    if not inquilino:
        raise HTTPException(status_code=404, detail="Inquilino not found")
    return await update_inquilino(db, inquilino_id, inquilino_in)


@router.delete("/{inquilino_id}")
async def delete_existing_inquilino(
    inquilino_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete an inquilino."""
    inquilino = await get_inquilino(db, inquilino_id)
    if not inquilino:
        raise HTTPException(status_code=404, detail="Inquilino not found")
    await delete_inquilino(db, inquilino_id)
    return {"message": "Inquilino deleted successfully"}
