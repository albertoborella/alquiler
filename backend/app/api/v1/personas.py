from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.models.persona import PersonaCreate, PersonaUpdate, PersonaPublic
from app.crud.persona import (
    get_persona,
    get_persona_by_cuit,
    get_personas,
    get_propietarios,
    get_inquilinos,
    create_persona,
    update_persona,
    delete_persona,
)
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[PersonaPublic])
async def list_personas(
    skip: int = 0,
    limit: int = 100,
    rol: Optional[str] = Query(None, description="Filter by rol: propietario, inquilino, ambos"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all personas with optional rol filter."""
    return await get_personas(db, skip=skip, limit=limit, rol=rol)


@router.get("/propietarios", response_model=List[PersonaPublic])
async def list_propietarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all propietarios (rol propietario or ambos)."""
    return await get_propietarios(db, skip=skip, limit=limit)


@router.get("/inquilinos", response_model=List[PersonaPublic])
async def list_inquilinos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all inquilinos (rol inquilino or ambos)."""
    return await get_inquilinos(db, skip=skip, limit=limit)


@router.get("/{persona_id}", response_model=PersonaPublic)
async def read_persona(
    persona_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a persona by ID."""
    persona = await get_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.post("/", response_model=PersonaPublic, status_code=status.HTTP_201_CREATED)
async def create_new_persona(
    persona_in: PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new persona."""
    # Check if CUIT already exists
    existing = await get_persona_by_cuit(db, persona_in.cuit)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CUIT already registered"
        )
    return await create_persona(db, persona_in)


@router.put("/{persona_id}", response_model=PersonaPublic)
async def update_existing_persona(
    persona_id: str,
    persona_in: PersonaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a persona."""
    persona = await get_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return await update_persona(db, persona_id, persona_in)


@router.delete("/{persona_id}")
async def delete_existing_persona(
    persona_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a persona."""
    persona = await get_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    await delete_persona(db, persona_id)
    return {"message": "Persona deleted successfully"}
